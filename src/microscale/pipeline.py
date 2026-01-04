from __future__ import annotations

import os
from pathlib import Path

from .model import Ops
from .ops import exif, jpegtran
from .ops import scale as scale_op


def process_image(fp: Path, ops: Ops) -> Path:
    stat = fp.stat()

    if ops.crop:
        fp = jpegtran.crop(fp)

    if ops.rotate:
        jpegtran.rotate(fp)

    if ops.scale:
        scale_op.add_scale(fp)

    if ops.iptc:
        exif.apply_from_filename(fp)

    os.utime(fp, (stat.st_atime, stat.st_mtime))
    return fp
