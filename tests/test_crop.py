# tests/test_jpegtran_ops.py
from __future__ import annotations

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
    Path(tmp_path).unlink()  # Remove empty file; Pillow will write it
    path = Path(tmp_path)
    img = Image.new("RGB", (width, height), (0, 0, 0))
    img.save(path, "JPEG")
    return path


@patch("microscale.ops.jpegtran.run_jpegtran")
def test_crop_wide(mock_run: Any) -> None:
    """Test cropping a wide image calls jpegtran with correct arguments."""
    w, h = 2000, 1000
    fp = make_image(w, h)
    fp_out = fp.with_stem(fp.stem + CROPPED_SUFFIX)

    out = jpegtran.crop(fp, fp_out)

    # Output path correctness
    assert out == fp_out
    assert out.stem.endswith(CROPPED_SUFFIX)

    # run_jpegtran was called
    mock_run.assert_called_once()
    crop_args: list[str] = mock_run.call_args[0][0]
    assert "-crop" in crop_args
    assert str(fp_out) in crop_args

    fp.unlink()


@patch("microscale.ops.jpegtran.run_jpegtran")
def test_crop_too_narrow(mock_run: Any) -> None:
    """Test crop raises ValueError if image aspect ratio is too narrow."""
    w, h = 800, 1000  # ratio < TARGET_RATIO
    fp = make_image(w, h)
    fp_out = fp.with_stem(fp.stem + CROPPED_SUFFIX)

    with pytest.raises(ValueError):
        jpegtran.crop(fp, fp_out)

    # run_jpegtran should not have been called
    mock_run.assert_not_called()
    fp.unlink()


@patch("microscale.ops.jpegtran.run_jpegtran")
def test_descale(mock_run: Any) -> None:
    """Test descale calls jpegtran to reduce height by SCALE_HEIGHT (rounded to block)."""
    w, h = 500, 200
    fp = make_image(w, h)
    fp_out = fp.with_stem(fp.stem + SCALED_SUFFIX)

    out = jpegtran.descale(fp, fp_out)

    assert out == fp_out
    assert out.stem.endswith(SCALED_SUFFIX)

    mock_run.assert_called_once()
    args: list[str] = mock_run.call_args[0][0]
    assert "-crop" in args
    assert str(fp_out) in args

    fp.unlink()


@patch("microscale.ops.jpegtran.run_jpegtran")
def test_rotate(mock_run: Any) -> None:
    """Test rotate calls jpegtran correctly for 180° in-place rotation."""
    fp = make_image(100, 100)

    out = jpegtran.rotate(fp)

    mock_run.assert_called_once()
    args: list[str] = mock_run.call_args[0][0]
    assert "-rotate" in args
    assert str(fp) in args
    assert out == fp

    fp.unlink()
