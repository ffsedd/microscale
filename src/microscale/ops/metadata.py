from __future__ import annotations

import io
import logging
from pathlib import Path

import pyexiv2  # type: ignore
from PIL import Image

logger = logging.getLogger(__name__)

THUMB_SIZE = (256, 256)
THUMB_TAGS = {
    "Exif.Thumbnail.JPEGInterchangeFormat",
    "Exif.Thumbnail.JPEGInterchangeFormatLength",
}


def _rebuild_exif_thumbnail(fp: Path, img: pyexiv2.Image) -> None:
    img.exif_thumbnail = None  # remove any residue

    with Image.open(fp) as im:
        # im = im.copy()
        im.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=70, subsampling=1)
        img.exif_thumbnail = buf.getvalue()


def copy(fp_src: Path, fp_dst: Path) -> Path:
    """
    Copy EXIF/IPTC/XMP metadata from fp_src to fp_dst,
    stripping broken thumbnails and rebuilding a clean one.
    """
    try:
        with pyexiv2.Image(str(fp_src)) as src, pyexiv2.Image(str(fp_dst)) as dst:
            exif = src.read_exif()

            # Strip thumbnail tags BEFORE writing
            for tag in THUMB_TAGS:
                exif.pop(tag, None)

            dst.modify_exif(exif)
            dst.modify_iptc(src.read_iptc())
            dst.modify_xmp(src.read_xmp())

            _rebuild_exif_thumbnail(fp_dst, dst)

        logger.info(
            "Metadata + thumbnail copied %s → %s",
            fp_src.name,
            fp_dst.name,
        )

    except Exception as e:
        logger.warning("Failed to copy metadata: %s", e)

    return fp_dst
