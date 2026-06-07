"""CLI entry point: Fig 7 sweep and spatial Fermi lattice simulation."""

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
    p.add_argument(
        "--lattice",
        action="store_true",
        help="run the spatial Fermi lattice model instead of the Fig 7 sweep",
    )

    # Lattice-specific options (ignored unless --lattice is set)
    p.add_argument("--grid-size", type=int, default=50, metavar="L",
                   help="lattice side length (L×L torus) [lattice only]")
    p.add_argument("--n-gen", type=int, default=500, metavar="N",
                   help="evolutionary generations [lattice only]")
    p.add_argument("--kappa", type=float, default=0.1, metavar="K",
                   help="Fermi noise temperature [lattice only]")
    p.add_argument("--init-uc", type=float, default=0.56, metavar="F",
                   help="initial UC proportion [lattice only]")
    p.add_argument("--init-cc", type=float, default=0.358, metavar="F",
                   help="initial CC proportion (FR fills remainder) [lattice only]")
    p.add_argument("--seed", type=int, default=None, metavar="N",
                   help="RNG seed for reproducibility [lattice only]")
    p.add_argument("--snapshots", action="store_true",
                   help="save grid snapshot mosaic PNG [lattice only]")
    return p


def _run_lattice(args: argparse.Namespace) -> None:
    from coop_disaster.lattice import run_evolution
    from coop_disaster.plot import plot_lattice_evolution, plot_grid_mosaic
    from coop_disaster.types import SimConfig, LatticeConfig

    sim_cfg = SimConfig(n_rounds=args.n_rounds)
    lat_cfg = LatticeConfig(
        grid_size=args.grid_size,
        n_gen=args.n_gen,
        kappa=args.kappa,
        init_uc=args.init_uc,
        init_cc=args.init_cc,
    )

    print("Running spatial Fermi lattice simulation...")
    print(f"  Grid: {lat_cfg.grid_size}×{lat_cfg.grid_size}  |  "
          f"Generations: {lat_cfg.n_gen}  |  κ={lat_cfg.kappa}")
    print(f"  Init: UC={lat_cfg.init_uc:.2f}  CC={lat_cfg.init_cc:.2f}  "
          f"FR={1 - lat_cfg.init_uc - lat_cfg.init_cc:.3f}")

    t0 = time.perf_counter()
    result = run_evolution(sim_cfg, lat_cfg, seed=args.seed)
    elapsed = time.perf_counter() - t0
    print(f"  Done in {elapsed:.1f}s\n")

    final_uc = result["uc_freq"][-1]
    final_cc = result["cc_freq"][-1]
    final_fr = result["fr_freq"][-1]
    final_sr = result["success_rate"][-1]
    print(f"Final state (gen {lat_cfg.n_gen}):")
    print(f"  UC={final_uc:.3f}  CC={final_cc:.3f}  FR={final_fr:.3f}  "
          f"success={final_sr:.3f}")

    out = args.output if args.output != Path("fig7.png") else Path("lattice_evolution.png")
    if not args.no_plot:
        plot_lattice_evolution(result, out)
        print(f"\nEvolution plot saved to {out}")

        if args.snapshots:
            mosaic_out = out.with_name(out.stem + "_snapshots.png")
            plot_grid_mosaic(result["snapshots"], mosaic_out)
            print(f"Snapshot mosaic saved to {mosaic_out}")


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)

    if args.lattice:
        _run_lattice(args)
        return


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
