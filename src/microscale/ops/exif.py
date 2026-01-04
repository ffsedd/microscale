from __future__ import annotations

import subprocess
from pathlib import Path


def apply_from_filename(fp: Path) -> None:
    subprocess.run(
        ["exiftool", "-overwrite_original", str(fp)],
        check=True,
    )
