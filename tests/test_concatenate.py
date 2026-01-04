# tests/test_concatenate.py
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from PIL import Image

from microscale.ops.concatenate import (
    concatenate,
    enlarge_with_jpegtran,
)


def make_image(width: int, height: int) -> Path:
    """Create a temporary JPEG image."""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        path = Path(tmp.name)
    img = Image.new("RGB", (width, height), (0, 0, 0))
    img.save(path, "JPEG")
    return path


@patch("microscale.ops.concatenate.run_jpegtran")
def test_enlarge_with_jpegtran_no_change(mock_run: Any) -> None:
    """If new size equals old, jpegtran is not called."""
    fp = make_image(100, 50)
    out = enlarge_with_jpegtran(fp, (100, 50), (100, 50))
    assert out == fp
    mock_run.assert_not_called()
    fp.unlink()


@patch("microscale.ops.concatenate.run_jpegtran")
def test_enlarge_with_jpegtran_calls_jpegtran(mock_run: Any) -> None:
    """Check jpegtran is called when enlarging."""
    fp = make_image(80, 40)
    out = enlarge_with_jpegtran(fp, (80, 40), (80, 80))
    mock_run.assert_called_once()
    assert out == fp
    fp.unlink()


@patch("microscale.ops.concatenate.run_jpegtran")
def test_concatenate_success(mock_run: Any) -> None:
    """Concatenate two images with the same width."""
    fp1 = make_image(100, 50)
    fp2 = make_image(100, 70)
    fp_out = Path(tempfile.mktemp(suffix=".jpg"))

    result = concatenate(fp1, fp2, fp_out, metadata="none")
    assert result == fp_out
    mock_run.assert_called()  # jpegtran commands executed
    assert fp_out.exists()
    # Clean up
    fp1.unlink()
    fp2.unlink()
    fp_out.unlink()


def test_concatenate_width_mismatch() -> None:
    """Concatenate raises ValueError for width mismatch."""
    fp1 = make_image(100, 50)
    fp2 = make_image(120, 50)
    fp_out = Path(tempfile.mktemp(suffix=".jpg"))

    with pytest.raises(ValueError):
        concatenate(fp1, fp2, fp_out)

    fp1.unlink()
    fp2.unlink()
