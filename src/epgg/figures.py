"""Fig 2 reproduction: cooperator fraction vs delta at fixed gamma (Ding 2024).

Validation gate for the baseline. Sweeps delta at r=4, c=1, gamma=0.04 on the
L=200 lattice and plots the stationary cooperator fraction, expecting the
D → C → C+D sequence (two discontinuous jumps; cooperation rises from 0, then
declines within C+D as delta grows further).

Usage:
    uv run epgg-fig2                       # full gate (L=200)
    uv run epgg-fig2 --n-repeats 5 --output fig2.png
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from epgg.sweep import coop_fraction_at

# Default delta grid: dense near the D→C→C+D transitions, sparse in the tail.
DEFAULT_DELTAS = [
    0.005,
    0.01,
    0.015,
    0.02,
    0.025,
    0.03,
    0.04,
    0.05,
    0.07,
    0.1,
    0.15,
    0.2,
    0.3,
    0.5,
    0.7,
    1.0,
]


def run_fig2(
    L: int = 200,
    gamma: float = 0.04,
    deltas=DEFAULT_DELTAS,
    r: float = 4.0,
    c: float = 1.0,
    n_repeats: int = 5,
    base_seed: int = 42,
    output: Path = Path("epgg_fig2.png"),
    save_data: bool = True,
    **run_kwargs,
) -> tuple[np.ndarray, np.ndarray]:
    """Run the delta-sweep gate, plot, and (optionally) cache raw data to .npz.

    Returns (deltas, coop_fractions). Extra run_kwargs (window, min_gen, max_gen)
    pass through to each session.
    """
    deltas = np.asarray(deltas, dtype=float)
    t0 = time.perf_counter()
    # Loop per-δ (rather than delta_sweep) to print incremental progress on the
    # long L=200 gate run.
    fracs = np.empty(len(deltas))
    for i, d in enumerate(deltas):
        td = time.perf_counter()
        fracs[i] = coop_fraction_at(
            d,
            gamma,
            L=L,
            r=r,
            c=c,
            n_repeats=n_repeats,
            base_seed=base_seed,
            **run_kwargs,
        )
        print(
            f"  [{i + 1:2d}/{len(deltas)}] δ={d:.3f}  C={fracs[i]:.3f}  "
            f"({time.perf_counter() - td:.0f}s)",
            flush=True,
        )
    elapsed = time.perf_counter() - t0
    print(f"  swept {len(deltas)} δ × {n_repeats} repeats at L={L} ({elapsed:.0f}s)")

    plot_delta_sweep(deltas, fracs, output, gamma=gamma)
    if save_data:
        npz = Path(output).with_suffix(".npz")
        np.savez(npz, deltas=deltas, fracs=fracs, gamma=gamma, L=L, n_repeats=n_repeats)
        print(f"  data saved to {npz}")
    return deltas, fracs


def plot_delta_sweep(
    deltas: np.ndarray, fracs: np.ndarray, output: Path, gamma: float
) -> None:
    """Plot cooperator (and defector) fraction vs delta — cf. paper Fig 2."""
    deltas = np.asarray(deltas)
    fracs = np.asarray(fracs)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(deltas, fracs, "s-", color="steelblue", lw=1.5, ms=5, label="C")
    ax.plot(deltas, 1.0 - fracs, "o-", color="crimson", lw=1.5, ms=4, label="D")
    ax.set_xlabel("δ (cooperator repair rate)")
    ax.set_ylabel("Stationary fraction")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title(f"EPGG Fig 2 reproduction (r=4, c=1, γ={gamma})")
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    print(f"  plot saved to {output}")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="epgg-fig2",
        description="Reproduce Ding (2024) Fig 2: cooperation vs delta.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--L", type=int, default=200, help="lattice side")
    p.add_argument(
        "--gamma", type=float, default=0.04, help="defector destruction rate"
    )
    p.add_argument("--n-repeats", type=int, default=5, help="sessions per δ")
    p.add_argument("--seed", type=int, default=42, help="base RNG seed")
    p.add_argument("--window", type=int, default=200, help="stabilization window")
    p.add_argument(
        "--min-gen", type=int, default=1500, help="min generations before stop"
    )
    p.add_argument("--max-gen", type=int, default=6000, help="hard generation cap")
    p.add_argument(
        "--output", type=Path, default=Path("epgg_fig2.png"), help="output plot path"
    )
    return p


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)
    print(f"Running Fig 2 gate sweep at L={args.L}, γ={args.gamma}...")
    run_fig2(
        L=args.L,
        gamma=args.gamma,
        n_repeats=args.n_repeats,
        base_seed=args.seed,
        output=args.output,
        window=args.window,
        min_gen=args.min_gen,
        max_gen=args.max_gen,
    )


if __name__ == "__main__":
    main()
