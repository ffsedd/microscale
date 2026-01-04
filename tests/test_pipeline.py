from pathlib import Path

from microscale.model import Ops
from microscale.pipeline import process_image


def test_pipeline_smoke(tmp_path: Path) -> None:
    fp = tmp_path / "a.jpg"
    fp.write_bytes(b"fake")

    ops = Ops(scale=False, iptc=False)
    out = process_image(fp, ops)

    assert out.exists()
