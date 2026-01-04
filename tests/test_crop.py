# tests/test_jpegtran_ops.py
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from PIL import Image

from microscale.config import CROPPED_SUFFIX, SCALED_SUFFIX
from microscale.ops import jpegtran


def make_image(width: int, height: int) -> Path:
    """Create a temporary JPEG image of given size."""
    fd, tmp_path = tempfile.mkstemp(suffix=".jpg")
    Path(tmp_path).unlink()  # remove empty file, Pillow will write it
    path = Path(tmp_path)
    img = Image.new("RGB", (width, height), (0, 0, 0))
    img.save(path, "JPEG")
    return path


@patch("microscale.ops.jpegtran._run")
def test_crop_wide(mock_run: Any) -> None:
    """Test cropping a wide image."""
    w: int = 2000
    h: int = 1000
    fp: Path = make_image(w, h)
    fp_out: Path = fp.with_stem(fp.stem + CROPPED_SUFFIX)

    out: Path = jpegtran.crop(fp, fp_out)

    # Output filename
    assert out == fp_out
    assert out.stem.endswith(CROPPED_SUFFIX)

    # _run called once
    mock_run.assert_called_once()
    crop_args: list[str] = mock_run.call_args[0][0]
    assert "-crop" in crop_args
    assert str(fp_out) in crop_args

    fp.unlink()


@patch("microscale.ops.jpegtran._run")
def test_crop_too_narrow(mock_run: Any) -> None:
    """Test crop raises ValueError if image is too narrow."""
    w: int = 800
    h: int = 1000  # ratio < TARGET_RATIO
    fp: Path = make_image(w, h)
    fp_out: Path = fp.with_stem(fp.stem + CROPPED_SUFFIX)

    with pytest.raises(ValueError):
        jpegtran.crop(fp, fp_out)

    mock_run.assert_not_called()
    fp.unlink()


@patch("microscale.ops.jpegtran._run")
def test_descale(mock_run: Any) -> None:
    """Test descale reduces height by SCALE_HEIGHT (rounded)."""
    w: int = 500
    h: int = 200
    fp: Path = make_image(w, h)
    fp_out: Path = fp.with_stem(fp.stem + SCALED_SUFFIX)

    out: Path = jpegtran.descale(fp, fp_out)

    assert out == fp_out
    assert out.stem.endswith(SCALED_SUFFIX)
    mock_run.assert_called_once()
    args: list[str] = mock_run.call_args[0][0]
    assert "-crop" in args
    assert str(fp_out) in args

    fp.unlink()


@patch("microscale.ops.jpegtran._run")
def test_rotate(mock_run: Any) -> None:
    """Test rotate calls jpegtran correctly."""
    fp: Path = make_image(100, 100)

    out: Path = jpegtran.rotate(fp)

    mock_run.assert_called_once()
    args: list[str] = mock_run.call_args[0][0]
    assert "-rotate" in args
    assert str(fp) in args
    assert out == fp

    fp.unlink()
