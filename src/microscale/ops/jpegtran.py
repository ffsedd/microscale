from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from PIL import Image

from ..config import CROPPED_SUFFIX, SCALE_HEIGHT, SCALED_SUFFIX, TARGET_RATIO

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


def descale(fp: Path) -> Path:
    """
    Remove a bottom SCALE_HEIGHT strip from a JPEG image (lossless).

    Useful for removing a scale bar from microscope images.
    The output filename receives the SCALED_SUFFIX.

    Args:
        fp: Path to the input JPEG file.

    Returns:
        Path to the descaled output JPEG.
    """
    with Image.open(fp) as im:
        w, h = im.size

    crop_h = h - SCALE_HEIGHT - ((h - SCALE_HEIGHT) % 8)
    crop_str = f"{w}x{crop_h}+0+0"
    out = fp.with_stem(fp.stem + SCALED_SUFFIX)
    _run(["-crop", crop_str, "-outfile", str(out), str(fp)])
    logger.info("%s: Descale done -> %s", fp.name, out.name)
    return out


def crop(fp: Path) -> Path:
    """
    Crop a JPEG to TARGET_RATIO (lossless) by trimming left and right sides if too wide.

    Raises a ValueError if the image is not wide enough to crop.

    Args:
        fp: Path to the input JPEG file.

    Returns:
        Path to the cropped JPEG with CROPPED_SUFFIX added to the stem.
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

    out = fp.with_stem(fp.stem + CROPPED_SUFFIX)
    _run(["-crop", crop_str, "-outfile", str(out), str(fp)])
    logger.info("%s: Crop done -> %s", fp.name, out.name)
    return out


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
