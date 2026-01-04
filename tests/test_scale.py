# tests/test_scale_ops.py
import tempfile
from pathlib import Path
from typing import Any, Tuple
from unittest.mock import patch

import pytest
from PIL import Image

from microscale.config import SCALE_HEIGHT
from microscale.ops.jpegtran import JpegtranError
from microscale.ops.scale import add_scale, calculate_scale_length, lens_label, make_temp_scale

STEM = "2555v1_vi_s_N4_25112210990_39_"


def test_calculate_scale_length() -> None:
    cases: list[Tuple[int, float, str]] = [
        (4656, 3345, "200 µm"),  # small image
        (4656, 1376, "500 µm"),  # medium image
        (4656, 6924, "100 µm"),  # large image
    ]

    for width, ppm, expected_label in cases:
        length_px, label = calculate_scale_length(width, ppm)
        assert isinstance(length_px, int)
        assert length_px > 0
        assert label == expected_label


def test_make_temp_scale_creates_file() -> None:
    width, height = 800, 50
    label = STEM

    scale_file: Path = make_temp_scale((width, height), 3345, label)
    assert scale_file.exists()

    # Validate image size and mode
    with Image.open(scale_file) as im:
        assert im.size == (width, height)
        assert im.mode == "RGB"

    # Clean up
    scale_file.unlink(missing_ok=True)


def test_lens_label_valid() -> None:
    label = lens_label(STEM)
    assert label == "n4"


def test_lens_label_invalid() -> None:
    stem = "invalid_file_name"
    with pytest.raises(ValueError):
        lens_label(stem)


def test_add_scale_creates_file() -> None:
    """add_scale creates output image with increased height."""
    width, height = 4656, 4000

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        fp_in = tmp / f"{STEM}.jpg"
        fp_out = tmp / f"{STEM}_.jpg"

        Image.new("RGB", (width, height), (128, 100, 128)).save(fp_in, subsampling=1)

        result = add_scale(fp_in, fp_out)

        assert result.exists()
        with Image.open(result) as im:
            assert im.size == (width, height + SCALE_HEIGHT)


@patch("microscale.ops.concatenate.run_jpegtran")
def test_add_scale_fails_on_subsampling(mock_run: Any) -> None:
    """add_scale propagates jpegtran subsampling failure."""
    width, height = 4656, 4000

    mock_run.side_effect = JpegtranError("mismatching sampling ratio 1:1, 1:2")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        fp_in = tmp / f"{STEM}.jpg"
        fp_out = tmp / f"{STEM}_.jpg"

        Image.new("RGB", (width, height), (0, 0, 0)).save(fp_in, subsampling=2)

        with pytest.raises(JpegtranError):
            add_scale(fp_in, fp_out)

        assert not fp_out.exists()
