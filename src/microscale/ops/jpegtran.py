from __future__ import annotations

import subprocess
from pathlib import Path


def _run(args: list[str]) -> None:
    subprocess.run(
        ["jpegtran", *args],
        check=True,
    )


def crop(fp: Path) -> Path:
    out = fp.with_stem(fp.stem + "_")
    _run(["-crop", "TODOxTODO+0+0", "-outfile", str(out), str(fp)])
    return out


def descale(fp: Path) -> None:
    _run(["-crop", "TODOxTODO+0+0", "-outfile", str(fp), str(fp)])


def rotate(fp: Path) -> None:
    _run(["-rotate", "180", "-outfile", str(fp), str(fp)])
