"""Parallel parameter sweep for the spatial TPGG.

Runs a grid of (config, seed) combinations and saves a tidy DataFrame to
data/analysis_{experiment}.pkl for downstream plotting.

Usage:
    uv run spatial-analysis --experiment uc_dominance --jobs 4 --seeds 5
    uv run spatial-analysis --experiment threshold --jobs 4
    uv run spatial-analysis --experiment beta --jobs 4
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from itertools import product
from pathlib import Path
from typing import Any

import pandas as pd
from joblib import dump

from spatial.config import PAPER_CONFIG, ModelConfig
from spatial.model import SpatialCollectiveRiskModel

DATA_DIR = Path(__file__).parent.parent.parent / "data"

# Discard the first BURN_IN steps; average over the remainder for steady-state estimates.
BURN_IN = 200

# ──────────────────────────────────────────────────────────────────────────────
# Experiment grids
# ──────────────────────────────────────────────────────────────────────────────

# Key experiment: does UC dominate as disaster_prob increases?
# Varies initial conditions to test convergence to the same attractor.
UC_DOMINANCE_GRID: dict[str, list] = {
    "disaster_prob": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    "initial_uc_fraction": [0.2, 0.33, 0.5],
}

# How sensitive is UC dominance to the threshold tightness?
# Max pool = 5 (agent + 4 neighbours × 1.0 contribution).
THRESHOLD_GRID: dict[str, list] = {
    "threshold": [1.0, 2.0, 2.5, 3.0, 3.75, 4.5, 5.0],
    "disaster_prob": [0.1, 0.4, 0.7],
}

# How does Fermi selection strength interact with disaster pressure?
BETA_GRID: dict[str, list] = {
    "beta": [0.1, 0.5, 1.0, 2.0, 5.0],
    "disaster_prob": [0.1, 0.4, 0.7],
}

EXPERIMENT_GRIDS: dict[str, dict[str, list]] = {
    "uc_dominance": UC_DOMINANCE_GRID,
    "threshold": THRESHOLD_GRID,
    "beta": BETA_GRID,
}


# ──────────────────────────────────────────────────────────────────────────────
# Worker (must be module-level for ProcessPoolExecutor pickling)
# ──────────────────────────────────────────────────────────────────────────────

def _run_single(args: tuple[dict[str, Any], int, int]) -> dict[str, Any]:
    params, seed, n_steps = args
    cfg = ModelConfig(**{**asdict(PAPER_CONFIG), **params, "seed": seed, "n_steps": n_steps})
    model = SpatialCollectiveRiskModel(cfg)
    for _ in range(n_steps):
        model.step()
    df = model.datacollector.get_model_vars_dataframe()
    burn = min(BURN_IN, n_steps // 2)
    tail = df.iloc[burn:]
    return {
        **params,
        "seed": seed,
        "uc_rate": tail["uc_rate"].mean(),
        "cc_rate": tail["cc_rate"].mean(),
        "cooperation_rate": tail["cooperation_rate"].mean(),
        "disaster_rate": tail["disaster_rate"].mean(),
        "mean_wealth": tail["mean_wealth"].mean(),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def run_grid(
    param_grid: dict[str, list],
    n_seeds: int = 5,
    n_steps: int = 500,
    n_jobs: int = 1,
) -> pd.DataFrame:
    """Run all (param_combo × seed) pairs and return a tidy DataFrame."""
    keys = list(param_grid.keys())
    combos = [dict(zip(keys, vals)) for vals in product(*param_grid.values())]
    tasks = [(combo, seed, n_steps) for combo in combos for seed in range(n_seeds)]

    if n_jobs == 1:
        results = [_run_single(t) for t in tasks]
    else:
        with ProcessPoolExecutor(max_workers=n_jobs) as pool:
            results = list(pool.map(_run_single, tasks))

    return pd.DataFrame(results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Spatial TPGG parameter sweep")
    parser.add_argument(
        "--experiment",
        choices=list(EXPERIMENT_GRIDS),
        default="uc_dominance",
        help="Which experiment grid to run (default: uc_dominance)",
    )
    parser.add_argument("--jobs", type=int, default=1, metavar="N",
                        help="Parallel worker processes (default: 1)")
    parser.add_argument("--seeds", type=int, default=5, metavar="N",
                        help="RNG seeds per configuration (default: 5)")
    parser.add_argument("--steps", type=int, default=500, metavar="N",
                        help="Simulation steps per run (default: 500)")
    args = parser.parse_args()

    grid = EXPERIMENT_GRIDS[args.experiment]
    n_combos = 1
    for v in grid.values():
        n_combos *= len(v)
    total = n_combos * args.seeds
    print(
        f"Running '{args.experiment}': {n_combos} configs x {args.seeds} seeds "
        f"= {total} runs  (jobs={args.jobs})"
    )

    df = run_grid(grid, n_seeds=args.seeds, n_steps=args.steps, n_jobs=args.jobs)

    DATA_DIR.mkdir(exist_ok=True)
    out = DATA_DIR / f"analysis_{args.experiment}.pkl"
    dump(df, out)
    print(f"Saved {len(df)} rows to {out}")
    print(df.groupby(list(grid.keys()))["uc_rate"].mean().round(3).to_string())


if __name__ == "__main__":
    main()
