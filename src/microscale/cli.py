from __future__ import annotations

import argparse
import logging
from multiprocessing import Pool
from pathlib import Path

from .model import Ops
from .pipeline import process_image


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="microscale")
    p.add_argument("files", nargs="+", type=Path)

    p.add_argument("--crop", action="store_true")
    p.add_argument("--descale", action="store_true")
    p.add_argument("--rotate", action="store_true")
    p.add_argument("--no-scale", dest="scale", action="store_false")
    p.add_argument("--no-iptc", dest="iptc", action="store_false")

    p.add_argument("-j", "--jobs", type=int, default=0)
    p.add_argument("-v", "--verbose", action="count", default=0)

    return p.parse_args()


def main() -> None:
    args = parse_args()

    logging.basicConfig(
        level=logging.WARNING - 10 * args.verbose,
        format="%(levelname)s %(message)s",
    )

    ops = Ops(
        crop=args.crop,
        descale=args.descale,
        rotate=args.rotate,
        scale=args.scale,
        iptc=args.iptc,
    )

    jobs = [(fp, ops) for fp in args.files]

    if args.jobs > 1:
        with Pool(args.jobs) as pool:
            pool.starmap(process_image, jobs)
    else:
        for fp, ops in jobs:
            process_image(fp, ops)
