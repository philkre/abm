"""CLI entry point: run the Fig 7 sweep from the command line."""

import argparse
import time
from pathlib import Path


def _build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser for the simulation."""
    p = argparse.ArgumentParser(
        prog="coop-disaster",
        description=(
            "Reproduce Fig 7 from Jonsson & Jonsson (2025): "
            "fraction of successful groups vs proportion of unconditional cooperators."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--n-groups",
        type=int,
        default=1_000,
        metavar="N",
        help="groups simulated per UC proportion value",
    )
    p.add_argument(
        "--n-rounds",
        type=int,
        default=200,
        metavar="N",
        help="LCP update rounds per group",
    )
    p.add_argument(
        "--uc-steps",
        type=int,
        default=101,
        metavar="N",
        help="number of UC proportion points swept from 0 to 1",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("fig7.png"),
        metavar="FILE",
        help="output plot path",
    )
    p.add_argument(
        "--jobs",
        type=int,
        default=1,
        metavar="N",
        help="parallel worker processes (1 = serial)",
    )
    p.add_argument(
        "--no-plot",
        action="store_true",
        help="skip plot generation, only print results to stdout",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    ...


if __name__ == "__main__":
    main()
