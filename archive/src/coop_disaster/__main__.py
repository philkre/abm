"""CLI entry point: run the Fig 7 sweep from the command line."""

import argparse
import logging
import time
from pathlib import Path
from coop_disaster.sweep import run_sweep
from coop_disaster.types import SimConfig
from coop_disaster.plot import plot_fig7

log = logging.getLogger(__name__)


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
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable DEBUG logging",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )
    if not args.verbose:
        logging.getLogger("MESA").setLevel(logging.WARNING)

    cfg = SimConfig(n_groups=args.n_groups, n_rounds=args.n_rounds)
    # UC (unconditional cooperators) proportions to sweep from 0 to 1
    uc_props = [i / (args.uc_steps - 1) for i in range(args.uc_steps)]

    log.info("Running Fig 7 simulation...")
    log.info("  Groups: %d  |  Rounds: %d  |  Workers: %d", cfg.n_groups, cfg.n_rounds, args.jobs)

    t0 = time.perf_counter()
    success_rates = run_sweep(uc_props, cfg, n_jobs=args.jobs)
    elapsed = time.perf_counter() - t0
    log.info("  Done in %.2fs", elapsed)

    step = max(1, len(uc_props) // 10)
    log.info("%8s  %12s", "UC prop", "Success rate")
    log.info("-" * 23)
    for i in range(0, len(uc_props), step):
        log.info("  %.2f    %.3f", uc_props[i], success_rates[i])

    if not args.no_plot:
        plot_fig7(uc_props, success_rates, args.output)
        log.info("Plot saved to %s", args.output)


if __name__ == "__main__":
    main()
