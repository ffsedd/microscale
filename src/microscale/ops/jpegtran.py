from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from PIL import Image

from ..config import CROPPED_SUFFIX, SCALE_HEIGHT, TARGET_RATIO

logger = logging.getLogger(__name__)


def _run(args: list[str]) -> None:
    """Run jpegtran command."""
    subprocess.run(["jpegtran", *args], check=True)


def crop(fp: Path) -> Path:
    """
    Crop JPEG to TARGET_RATIO.
    - Too wide → crop left/right evenly.
    - Too tall → remove SCALE_HEIGHT pixels from bottom if it fixes the ratio.
    Returns new Path with CROPPED_SUFFIX.
    """
    out = fp.with_stem(fp.stem + CROPPED_SUFFIX)

    with Image.open(fp) as im:
        w, h = im.size

    current_ratio = w / h
    logger.debug(
        "%s: %dx%d (ratio %.3f) -> target %.3f", fp.name, w, h, current_ratio, TARGET_RATIO
    )

    if abs(current_ratio - TARGET_RATIO) < 1e-6:
        logger.info("%s: Already correct ratio, skipping crop", fp.name)
        out.write_bytes(fp.read_bytes())
        return out

    if current_ratio > TARGET_RATIO:
        # Crop left/right
        new_w = int(h * TARGET_RATIO)
        left = (w - new_w) // 2
        top = 0
        crop_w = new_w - (new_w % 8)
        crop_h = h - (h % 8)
    else:
        # Too tall → remove SCALE_HEIGHT if it fixes ratio
        new_h = h - SCALE_HEIGHT
        if abs((w / new_h) - TARGET_RATIO) < 1e-3:
            top = 0
            left = 0
            crop_w = w - (w % 8)
            crop_h = new_h - (new_h % 8)
            logger.info("%s: Removing %d rows from bottom to fix ratio", fp.name, SCALE_HEIGHT)
        else:
            logger.info(
                "%s: Too tall but removing %d rows won't fix ratio, skipping crop",
                fp.name,
                SCALE_HEIGHT,
            )
            out.write_bytes(fp.read_bytes())
            return out

    crop_str = f"{crop_w}x{crop_h}+{left}+{top}"
    logger.info("%s: Cropping geometry: %s", fp.name, crop_str)

    _run(["-crop", crop_str, "-outfile", str(out), str(fp)])
    logger.info("%s: Crop done -> %s", fp.name, out.name)
    return out


def rotate(fp: Path) -> None:
    """Lossless rotate 180° in place."""
    logger.info("%s: Rotating 180°", fp.name)
    _run(["-rotate", "180", "-outfile", str(fp), str(fp)])
    logger.info("%s: Rotation done", fp.name)
