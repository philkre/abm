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

    from coop_disaster.sweep import run_sweep
    from coop_disaster.types import SimConfig

    cfg = SimConfig(n_groups=args.n_groups, n_rounds=args.n_rounds)
    uc_props = [i / (args.uc_steps - 1) for i in range(args.uc_steps)]

    print("Running Fig 7 simulation...")
    print(f"  Groups: {cfg.n_groups}  |  Rounds: {cfg.n_rounds}  |  Workers: {args.jobs}")

    t0 = time.perf_counter()
    success_rates = run_sweep(uc_props, cfg, n_jobs=args.jobs)
    elapsed = time.perf_counter() - t0
    print(f"  Done in {elapsed:.2f}s\n")

    step = max(1, len(uc_props) // 10)
    print(f"{'UC prop':>8}  {'Success rate':>12}")
    print("-" * 23)
    for i in range(0, len(uc_props), step):
        print(f"  {uc_props[i]:.2f}    {success_rates[i]:.3f}")

    if not args.no_plot:
        from coop_disaster.plot import plot_fig7

        plot_fig7(uc_props, success_rates, args.output)
        print(f"\nPlot saved to {args.output}")


if __name__ == "__main__":
    main()
