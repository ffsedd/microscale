from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from PIL import Image

from ..config import SCALE_HEIGHT, TARGET_RATIO

logger = logging.getLogger(__name__)


def _run(args: list[str]) -> None:
    """
    Run a jpegtran command safely.

    Args:
        args: List of arguments for jpegtran (excluding the executable itself).

    Raises:
        subprocess.CalledProcessError: If jpegtran fails.
    """
    subprocess.run(["jpegtran", *args], check=True)


def _crop_geometry(fp: Path, w: int, h: int) -> str:
    """
    Compute the crop geometry string for a wide JPEG to match TARGET_RATIO.

    The width is adjusted to fit the target ratio; height remains unchanged.
    Both width and height are rounded down to multiples of 8, as required by jpegtran.

    Args:
        fp: Path to the image file (used for logging purposes).
        w: Original image width in pixels.
        h: Original image height in pixels.

    Returns:
        A string suitable for the "-crop" argument of jpegtran, e.g., "1160x1000+20+0".
    """
    new_w = int(h * TARGET_RATIO)
    crop_w = new_w - (new_w % 8)
    crop_h = h - (h % 8)
    left = (w - crop_w) // 2
    top = 0
    return f"{crop_w}x{crop_h}+{left}+{top}"


def descale(fp: Path, fp_out: Path) -> Path:
    """
    Lossless removal of SCALE_HEIGHT pixels from the bottom of a JPEG.

    Args:
        fp: Path to the input JPEG file.
        fp_out: Path to save the descaled output file.

    Returns:
        Path to the descaled JPEG.
    """
    with Image.open(fp) as im:
        w, h = im.size

    crop_h = h - SCALE_HEIGHT - ((h - SCALE_HEIGHT) % 8)
    crop_str = f"{w}x{crop_h}+0+0"

    _run(["-crop", crop_str, "-outfile", str(fp_out), str(fp)])
    logger.info("%s: Descale done -> %s", fp.name, fp_out.name)
    return fp_out


def crop(fp: Path, fp_out: Path) -> Path:
    """
    Crop a JPEG to TARGET_RATIO (lossless) by trimming left and right sides if too wide.

    Raises a ValueError if the image is not wide enough to crop.

    Args:
        fp: Path to the input JPEG file.
        fp_out: Path to save the cropped output file.

    Returns:
        Path to the cropped JPEG.
    """
    with Image.open(fp) as im:
        w, h = im.size
    current_ratio = w / h

    if current_ratio > TARGET_RATIO:
        crop_str = _crop_geometry(fp, w, h)
    else:
        raise ValueError(
            f"{fp.name}: Cannot crop - image ratio {current_ratio:.3f} < target {TARGET_RATIO}"
        )

    _run(["-crop", crop_str, "-outfile", str(fp_out), str(fp)])
    logger.info("%s: Crop done -> %s", fp.name, fp_out.name)
    return fp_out


def rotate(fp: Path) -> Path:
    """
    Lossless rotate a JPEG image 180° in place.

    Args:
        fp: Path to the input JPEG file.

    Returns:
        The same Path as input (rotated in place).
    """
    _run(["-rotate", "180", "-outfile", str(fp), str(fp)])
    logger.info("%s: Rotation done", fp.name)
    return fp
