"""jonsson_fig7_validation.py — Reproduce Jonsson & Jonsson (2025) Fig 7.

Well-mixed Jonsson limit: frozen strategies, no spatial structure, no
environmental feedback (eta=0). Sweeps the fraction of unconditional
cooperators (UC) from 0→1 while keeping the empirical CC:D ratio from
Jonsson fixed at 215/21 ≈ 10.2.

At each UC proportion:
  - initial_cc_fraction = (1 - uc) * 10.2 / 11.2
  - initial_d_fraction  = (1 - uc) / 11.2
  - 1000 independent single-group simulations (seeds)
  - Success: pool >= T at the final generation

Key parameters matching Jonsson:
  T = 3.75, c_bar = 0.75, R = 1.6 (Jonsson's 1.6 multiplier on group total),
  eta = 0.0, n_gens = 200, lambda_mean = 1.0 (risk-neutral CC),
  well_mixed = True, frozen_strategies = True.

Usage (from philkre-abm root):
    uv run python scripts/jonsson_fig7_validation.py
    uv run python scripts/jonsson_fig7_validation.py --L 5 --seeds 500

Saves: results/figures/jonsson_fig7_replication.png
"""

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spatcoop.model import run_episode
from spatcoop.params import ModelParams

# CC:D ratio from Jonsson's empirical distribution (215/21)
CC_FR_RATIO = 215.0 / 21.0  # ≈ 10.238
RATIO_SUM = CC_FR_RATIO + 1.0  # 11.2...


def _run_one(args: tuple) -> float:
    """Run a single group simulation; return 1.0 if pool >= T at final gen, 0.0 otherwise."""
    uc_frac, seed, L, base_kwargs = args
    cc_frac = (1.0 - uc_frac) * CC_FR_RATIO / RATIO_SUM
    # d_frac = (1 - uc_frac) / RATIO_SUM  (implied)

    p = ModelParams(
        L=L,
        **base_kwargs,
        initial_mix="fractions",
        initial_uc_frac=uc_frac,
        initial_cc_frac=cc_frac,
    )
    result = run_episode(p, seed=seed)
    # Well-mixed pool = 5 * mean_contribution. Use a small tolerance (1e-4) because
    # float32 accumulation in CC rolling-average updates gives pool = 3.749999... instead
    # of exactly 3.75 when all agents converge to c_bar — a numerical artefact, not a
    # true shortfall. Jonsson's criterion is "converged contribution >= threshold".
    mean_c = float(result.timeseries["mean_contrib"][-1]) * p.c_bar
    pool = mean_c * 5.0
    return float(pool >= p.T - 1e-4)


def run_sweep(
    uc_props: np.ndarray,
    n_seeds: int,
    L: int,
    base_kwargs: dict,
    max_workers: int | None = None,
) -> np.ndarray:
    """Sweep UC fraction, returning success rates (fraction of seeds with pool >= T)."""
    tasks = [
        (uc, seed, L, base_kwargs)
        for uc in uc_props
        for seed in range(n_seeds)
    ]

    outcomes = np.zeros(len(tasks), dtype=np.float32)
    n_total = len(tasks)

    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_run_one, task): idx for idx, task in enumerate(tasks)}
        done = 0
        for fut in as_completed(futures):
            idx = futures[fut]
            outcomes[idx] = fut.result()
            done += 1
            if done % max(1, n_total // 20) == 0:
                print(f"  {done}/{n_total} ({100*done/n_total:.0f}%)", flush=True)

    # Average across seeds for each UC fraction
    success_rates = outcomes.reshape(len(uc_props), n_seeds).mean(axis=1)
    return success_rates


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--L", type=int, default=5, help="Lattice side (default: 5 → 25 agents per group)")
    p.add_argument("--seeds", type=int, default=1000, help="Seeds per UC fraction point")
    p.add_argument("--workers", type=int, default=None, help="Parallel workers (default: CPU count)")
    p.add_argument("--step", type=float, default=0.05, help="UC fraction step size")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # Base ModelParams shared across all runs (no initial_mix / uc_frac / cc_frac yet)
    base_kwargs = dict(
        n_gens=200,
        measure_window=200,
        # Game
        c_bar=0.75,
        T=3.75,
        R=1.6,  # Jonsson 1.6 multiplier; in well-mixed: pg_return = R * mean_c
        w0=1.0,
        mu=0.0,  # no mutation with frozen strategies
        # Wealth: OU with flat-ish income (b=c_bar keeps wealth near w0 for full-coop groups)
        wealth_mode="ou",
        b=0.75,
        sigma=0.0,
        # Risk
        p_max=0.5,
        ell=0.34,
        p_min=0.0,
        # Environment — no feedback for this validation
        delta=0.03,
        gamma=0.03,
        eta=0.0,
        kappa=0.2,
        # Imitation (irrelevant with frozen strategies)
        beta=2.0,
        # Loss aversion: risk-neutral (premium = 0, CC just matches neighbours)
        lambda_mode="homogeneous",
        lambda_mean=1.0,
        # Flags
        well_mixed=True,
        frozen_strategies=True,
    )

    uc_props = np.arange(0.0, 1.0 + args.step / 2, args.step)
    uc_props = np.clip(uc_props, 0.0, 1.0)

    print(f"Jonsson Fig 7 validation")
    print(f"  L={args.L} ({args.L**2} agents/group), seeds={args.seeds}, step={args.step}")
    print(f"  UC fraction points: {len(uc_props)}")
    print(f"  Total simulations: {len(uc_props) * args.seeds}")
    print()

    success_rates = run_sweep(uc_props, args.seeds, args.L, base_kwargs, max_workers=args.workers)

    # ── Report ───────────────────────────────────────────────────────────────
    print()
    print("Results:")
    print(f"{'UC fraction':>12}  {'CC fraction':>12}  {'D fraction':>12}  {'Success rate':>13}")
    print("-" * 56)
    for uc, sr in zip(uc_props, success_rates):
        cc = (1.0 - uc) * CC_FR_RATIO / RATIO_SUM
        d = (1.0 - uc) / RATIO_SUM
        print(f"{uc:12.2f}  {cc:12.3f}  {d:12.3f}  {sr:13.3f}")

    # Key points summary
    print()
    targets = {0.0: None, 0.56: None, 1.0: None}
    for uc, sr in zip(uc_props, success_rates):
        for t in targets:
            if abs(uc - t) < args.step / 2:
                targets[t] = sr

    print("Key points:")
    for uc_val, sr in targets.items():
        label = f"UC={uc_val:.2f}"
        if sr is None:
            print(f"  {label}: not sampled")
        else:
            print(f"  {label}: success_rate = {sr:.3f}")

    nonlinear = (
        success_rates[-1] > 0.9
        and np.any(np.diff(success_rates) > 0.05)
        and success_rates[0] < 0.5
    )
    print(f"\n  Curve nonlinear: {nonlinear}")
    if success_rates.max() < 0.05:
        print("  WARNING: flat near-zero everywhere — T or CC dynamics may be miscalibrated")

    # ── Plot ─────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 5))

    ax.plot(uc_props, success_rates, color="#2166ac", lw=2.0, label="Simulation")
    ax.axvline(0.56, color="black", lw=1.5, ls="--", label="Empirical UC = 0.56")

    ax.set_xlabel("Proportion of unconditional cooperators (UC)", fontsize=12)
    ax.set_ylabel("Proportion of successful groups (pool ≥ T)", fontsize=12)
    ax.set_title(
        "Jonsson & Jonsson (2025) Fig 7 — Replication\n"
        f"well-mixed, frozen strategies, L={args.L}, {args.seeds} seeds",
        fontsize=11,
    )
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    out_path = Path("results/figures/jonsson_fig7_replication.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"\nFigure saved to {out_path}")


if __name__ == "__main__":
    main()
