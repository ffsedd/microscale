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
    tmp: tempfile._TemporaryFileWrapper = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)  # type: ignore
    path: Path = Path(tmp.name)
    img: Image.Image = Image.new("RGB", (width, height), (0, 0, 0))
    img.save(path, "JPEG")
    return path


@patch("microscale.ops.jpegtran._run")
def test_crop_wide(mock_run: Any) -> None:
    """Test cropping a wide image."""
    w: int = 2000
    h: int = 1000
    fp: Path = make_image(w, h)

    out: Path = jpegtran.crop(fp)

    # Output filename
    assert out.stem.endswith(CROPPED_SUFFIX)

    # _run called once
    mock_run.assert_called_once()
    crop_args: list[str] = mock_run.call_args[0][0]
    assert "-crop" in crop_args
    assert str(out) in crop_args

    fp.unlink()


@patch("microscale.ops.jpegtran._run")
def test_crop_too_narrow(mock_run: Any) -> None:
    """Test crop raises ValueError if image is too narrow."""
    w: int = 800
    h: int = 1000  # ratio < TARGET_RATIO
    fp: Path = make_image(w, h)

    with pytest.raises(ValueError):
        jpegtran.crop(fp)

    mock_run.assert_not_called()
    fp.unlink()


@patch("microscale.ops.jpegtran._run")
def test_descale(mock_run: Any) -> None:
    """Test descale reduces height by SCALE_HEIGHT (rounded)."""
    w: int = 500
    h: int = 200
    fp: Path = make_image(w, h)

    out: Path = jpegtran.descale(fp)

    assert out.stem.endswith(SCALED_SUFFIX)
    mock_run.assert_called_once()
    args: list[str] = mock_run.call_args[0][0]
    assert "-crop" in args
    assert str(out) in args

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
