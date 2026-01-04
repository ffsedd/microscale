from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from PIL import Image

from ..config import SCALE_HEIGHT, TARGET_RATIO

logger = logging.getLogger(__name__)

JPEGTRAN = "jpegtran"
JPEG_BLOCK = 8  # jpegtran requires multiples of 8


def _run(args: list[str]) -> None:
    """
    Run a jpegtran command safely.
    """
    subprocess.run([JPEGTRAN, *args], check=True)


def _round_down_block(x: int, block: int = JPEG_BLOCK) -> int:
    return x - (x % block)


def _crop_geometry(w: int, h: int, target_ratio: float) -> str:
    """
    Compute jpegtran crop geometry for a wide image.

    Width is reduced to match target_ratio, height unchanged.
    Geometry is centered horizontally and block-aligned.
    """
    new_w = int(h * target_ratio)
    crop_w = _round_down_block(new_w)
    crop_h = _round_down_block(h)
    left = (w - crop_w) // 2
    return f"{crop_w}x{crop_h}+{left}+0"


def descale(
    fp: Path,
    fp_out: Path,
    scale_height: int = SCALE_HEIGHT,
) -> Path:
    """
    Lossless removal of scale bar from the bottom of a JPEG.
    """
    with Image.open(fp) as im:
        w, h = im.size

    new_h = h - scale_height
    if new_h <= 0:
        raise ValueError(f"{fp.name}: scale height larger than image")

    crop_h = _round_down_block(new_h)
    crop_str = f"{w}x{crop_h}+0+0"

    _run(["-crop", crop_str, "-outfile", str(fp_out), str(fp)])
    logger.info("%s: Descale done -> %s", fp.name, fp_out.name)
    return fp_out


def crop(
    fp: Path,
    fp_out: Path,
    target_ratio: float = TARGET_RATIO,
) -> Path:
    """
    Lossless crop to target aspect ratio by trimming left/right sides.
    """
    with Image.open(fp) as im:
        w, h = im.size

    current_ratio = w / h
    if current_ratio <= target_ratio:
        raise ValueError(
            f"{fp.name}: Cannot crop - image ratio {current_ratio:.3f} < target {target_ratio}"
        )

    crop_str = _crop_geometry(w, h, target_ratio)
    _run(["-crop", crop_str, "-outfile", str(fp_out), str(fp)])
    logger.info("%s: Crop done -> %s", fp.name, fp_out.name)
    return fp_out


def rotate(fp: Path) -> Path:
    """
    Lossless rotate a JPEG image 180° in place.
    """
    _run(["-rotate", "180", "-outfile", str(fp), str(fp)])
    logger.info("%s: Rotation done", fp.name)
    return fp
