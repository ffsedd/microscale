from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Ops:
    crop: bool = False
    descale: bool = False
    rotate: bool = False
    scale: bool = True
    iptc: bool = True


@dataclass(frozen=True)
class Job:
    path: Path
    ops: Ops
