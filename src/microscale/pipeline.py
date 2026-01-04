from __future__ import annotations

import os
from pathlib import Path

from .config import CROPPED_SUFFIX, SCALED_SUFFIX
from .model import Ops
from .ops import jpegtran
from .ops import scale as scale_op


def process_image(fp: Path, ops: Ops) -> Path:
    """
    Apply a sequence of image operations (descale, crop, rotate, scale) to a JPEG file.

    Args:
        fp: Path to the input JPEG file.
        ops: Ops object containing boolean flags for each operation.

    Returns:
        Path to the processed file (last operation output).
    """
    # Preserve original access/modification times
    orig_stat = fp.stat()

    # Descale: remove bottom SCALE_HEIGHT pixels if requested
    if ops.descale:
        fp_out = fp.with_stem(fp.stem[:-1] + CROPPED_SUFFIX)
        fp = jpegtran.descale(fp, fp_out)

    # Crop to TARGET_RATIO if requested
    if ops.crop:
        fp_out = fp.with_stem(fp.stem + CROPPED_SUFFIX)
        fp = jpegtran.crop(fp, fp_out)

    # Rotate 180° if requested
    if ops.rotate:
        fp = jpegtran.rotate(fp)

    # Add scale bar if requested
    if ops.scale:
        print("NOT IMPLEMENTED: scale operation")
        fp_out = fp.with_stem(fp.stem[:-1] + SCALED_SUFFIX)
        fp = scale_op.add_scale(fp, fp_out)

    # Restore original timestamps
    os.utime(fp, (orig_stat.st_atime, orig_stat.st_mtime))
    return fp
