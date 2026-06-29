"""ell_eta_sweep.py — Phase 2: operating-window sweep over ell × eta.

2D heatmap: x-axis = ell (flood-loss fraction), y-axis = eta (flood-damage rate).
All runs start from initial_e = -1 (fully degraded) with the calibrated parameter set.

Saves raw results to results/raw/ell_eta_sweep.npz, then calls plot_ell_eta.py.
To re-plot without re-running the simulation:
    uv run python scripts/plot_ell_eta.py [--contour] [--no-combined]

Usage (from abm root):
    uv run python scripts/ell_eta_sweep.py
    uv run python scripts/ell_eta_sweep.py --n-points 10 --seeds 3 --L 50 --workers 8
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spatcoop.model import run_episode
from spatcoop.params import ModelParams

# ── Calibrated fixed parameters (non-swept) ───────────────────────────────────
BASE_KWARGS = dict(
    n_gens=1500,
    measure_window=200,
    L=200,
    # Game
    c_bar=0.83,
    T=1.7,
    w0=312.0,
    mu=0.0104,
    # Wealth
    wealth_mode="ou",
    b=1.5,
    sigma=0.1,
    # Risk
    risk_mode="linear",
    p_max=1.0,
    p_min=0.0,
    # ell and eta are swept — defaults used only when the other is swept
    ell=0.64,
    eta=0.005,
    # Environment
    delta=0.042,
    gamma=0.018,
    kappa=0.1,
    # Imitation
    beta=1.8,
    # Loss aversion
    lambda_mode="lognormal",
    lambda_mean=2.25,
    lambda_sigma=0.5,
    # Start with all three strategies
    initial_mix="thirds",
    # Fully degraded start
    initial_e=-1.0,
)


def _run_one(args: tuple) -> tuple[float, float]:
    """Run one (ell, eta, seed) point; return (mean_env_final, resilience_final)."""
    ell_val, eta_val, seed, base_kwargs = args
    kwargs = {k: v for k, v in base_kwargs.items() if k not in ("ell", "eta")}
    p = ModelParams(**kwargs, ell=ell_val, eta=eta_val)
    result = run_episode(p, seed=seed)
    mean_env = float(result.summary["mean_env"])
    resilience = float(result.summary["resilience"])
    return mean_env, resilience


def run_sweep(
    ell_vals: np.ndarray,
    eta_vals: np.ndarray,
    n_seeds: int,
    base_kwargs: dict,
    max_workers: int | None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (mean_env_grid, resilience_grid) averaged over seeds.

    Grid shape: (len(eta_vals), len(ell_vals)) — y-axis first (imshow convention).
    """
    n_ell, n_eta = len(ell_vals), len(eta_vals)
    tasks = [
        (ell, eta, seed, base_kwargs)
        for eta in eta_vals
        for ell in ell_vals
        for seed in range(n_seeds)
    ]
    n_total = len(tasks)

    env_raw = np.zeros(n_total, dtype=np.float32)
    res_raw = np.zeros(n_total, dtype=np.float32)

    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_run_one, task): idx for idx, task in enumerate(tasks)}
        done = 0
        for fut in as_completed(futures):
            idx = futures[fut]
            env_raw[idx], res_raw[idx] = fut.result()
            done += 1
            if done % max(1, n_total // 20) == 0:
                print(f"  {done}/{n_total} ({100*done/n_total:.0f}%)", flush=True)

    # Reshape: (n_eta, n_ell, n_seeds) → average over seeds
    env_grid = env_raw.reshape(n_eta, n_ell, n_seeds).mean(axis=2)
    res_grid = res_raw.reshape(n_eta, n_ell, n_seeds).mean(axis=2)
    return env_grid, res_grid


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--n-points", type=int, default=15, help="Grid points per axis")
    p.add_argument("--seeds", type=int, default=5, help="Seeds per grid point")
    p.add_argument("--L", type=int, default=None, help="Override lattice size")
    p.add_argument("--workers", type=int, default=None, help="Parallel workers")
    p.add_argument("--ell-lo", type=float, default=0.1, help="ell sweep lower bound")
    p.add_argument("--ell-hi", type=float, default=0.9, help="ell sweep upper bound")
    p.add_argument("--eta-lo", type=float, default=0.0, help="eta sweep lower bound")
    p.add_argument("--eta-hi", type=float, default=0.3, help="eta sweep upper bound")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    base_kwargs = dict(BASE_KWARGS)
    if args.L is not None:
        base_kwargs["L"] = args.L

    ell_vals = np.linspace(args.ell_lo, args.ell_hi, args.n_points)
    eta_vals = np.linspace(args.eta_lo, args.eta_hi, args.n_points)

    n_total = args.n_points ** 2 * args.seeds
    L = base_kwargs["L"]
    print(f"ell × eta sweep  ({args.n_points}×{args.n_points} grid, {args.seeds} seeds)")
    print(f"  ell ∈ [{args.ell_lo}, {args.ell_hi}]  "
          f"eta ∈ [{args.eta_lo}, {args.eta_hi}]")
    print(f"  L={L}, n_gens={base_kwargs['n_gens']}, total runs={n_total}")
    print()

    env_grid, res_grid = run_sweep(ell_vals, eta_vals, args.seeds, base_kwargs, args.workers)

    np_out = Path("results/raw/ell_eta_sweep.npz")
    np_out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(np_out, ell_vals=ell_vals, eta_vals=eta_vals,
             env_grid=env_grid, res_grid=res_grid)
    print(f"\nRaw data saved to {np_out}")

    # Delegate all plotting to the standalone script
    import subprocess
    subprocess.run(
        [sys.executable, str(Path(__file__).parent / "plot_ell_eta.py"),
         "--data", str(np_out)],
        check=True,
    )

    print("\nDone.")


if __name__ == "__main__":
    main()
