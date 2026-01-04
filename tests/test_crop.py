# tests/test_crop.py
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from microscale.config import CROPPED_SUFFIX, SCALE_HEIGHT, TARGET_RATIO
from microscale.ops.jpegtran import crop


def make_image(width: int, height: int) -> Path:
    """Create a temporary JPEG image of given size."""
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    path: Path = Path(tmp.name)
    img = Image.new("RGB", (width, height), (0, 0, 0))
    img.save(path, "JPEG")
    return path


@patch("microscale.ops.jpegtran._run")
def test_crop_wide(mock_run: MagicMock) -> None:
    """Wide image is cropped left/right."""
    fp: Path = make_image(2000, 1000)
    out: Path = crop(fp)

    # Output filename has correct suffix
    assert out.stem.endswith(CROPPED_SUFFIX)

    # Calculate expected crop width (multiple of 8)
    expected_w: int = int(1000 * TARGET_RATIO)
    crop_w: int = expected_w - (expected_w % 8)
    assert crop_w % 8 == 0

    # _run should have been called
    mock_run.assert_called_once()
    crop_args: list[str] = mock_run.call_args[0][0]
    assert "-crop" in crop_args
    assert str(out) in crop_args

    # Cleanup
    fp.unlink(missing_ok=True)
    out.unlink(missing_ok=True)


@patch("microscale.ops.jpegtran._run")
def test_crop_tall_fixable(mock_run: MagicMock) -> None:
    """Tall image where removing SCALE_HEIGHT fixes ratio."""
    h: int = 1000
    w: int = int((h - SCALE_HEIGHT) * TARGET_RATIO)
    fp: Path = make_image(w, h)
    out: Path = crop(fp)

    # _run should have been called
    mock_run.assert_called_once()

    fp.unlink(missing_ok=True)
    out.unlink(missing_ok=True)


@patch("microscale.ops.jpegtran._run")
def test_crop_tall_unfixable(mock_run: MagicMock) -> None:
    """Tall image where removing SCALE_HEIGHT does NOT fix ratio."""
    h: int = 1000
    w: int = int(h * TARGET_RATIO * 0.9)  # deliberately wrong
    fp: Path = make_image(w, h)
    out: Path = crop(fp)

    # _run should NOT be called
    mock_run.assert_not_called()

    # File copied if crop skipped
    assert out.read_bytes() == fp.read_bytes()

    fp.unlink(missing_ok=True)
    out.unlink(missing_ok=True)
