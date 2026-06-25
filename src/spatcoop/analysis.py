"""Load and aggregate results from the results/raw/ directory.

All functions read from saved .npz files — no model code here.
"""

from __future__ import annotations
from typing import Sequence

import numpy as np

from spatcoop.params import ModelParams, UC
from spatcoop.runner import load_result, result_path
from spatcoop.model import RunResult


def load_all_results(
    params_list: Sequence[ModelParams],
    seeds: Sequence[int],
) -> list[list[RunResult]]:
    """
    Load results for all (params, seed) combinations.

    Returns results[param_idx][seed_idx].
    Raises FileNotFoundError if any expected file is missing.
    """
    return [[load_result(result_path(p, s)) for s in seeds] for p in params_list]


def summary_table(
    results: list[list[RunResult]],
    keys: list[str] | None = None,
) -> np.ndarray:
    """
    Mean over seeds for each parameter point.

    Returns (n_params, n_keys) float64 array, in the same order as results.
    """
    if keys is None:
        keys = [
            "resilience",
            "n_UC",
            "n_CC",
            "n_D",
            "mean_wealth",
            "flood_rate",
            "mean_env",
            "moran_i",
        ]
    rows = []
    for seed_runs in results:
        row = [np.mean([r.summary[k] for r in seed_runs]) for k in keys]
        rows.append(row)
    return np.array(rows, dtype=np.float64)


def moran_i_strategy(strategy: np.ndarray) -> float:
    """
    Spatial autocorrelation of the UC indicator on the torus.

    UC is coded as 1, all others as 0. Uses a focal rolling-sum spatial lag
    (4 neighbours, row-standardised weight matrix). O(L²), no distance matrix.

    Returns 0.0 when the variance is zero (all-same strategy).
    """
    x = (strategy == UC).astype(np.float32)
    x_mean = x.mean()
    x_dev = x - x_mean

    # Spatial lag: mean of 4 Von Neumann neighbours
    x_lag = (np.roll(x, 1, axis=0) + np.roll(x, -1, axis=0) + np.roll(x, 1, axis=1) + np.roll(x, -1, axis=1)) / 4.0

    num = float((x_dev * (x_lag - x_mean)).sum())
    denom = float((x_dev**2).sum())

    if denom == 0.0:
        return 0.0

    # Row-standardised weight: each cell sums to 1 → W = L²
    n = float(strategy.size)
    W = n  # sum of all weights
    return (n / (W * denom)) * num


def mean_over_seeds(results: list[RunResult], key: str) -> float:
    """Mean of a summary statistic over multiple seeds."""
    return float(np.mean([r.summary[key] for r in results]))


def coop_fraction_timeseries(
    results: list[RunResult],
    L: int,
) -> np.ndarray:
    """
    (UC + CC) / L² averaged over seeds, shape (n_gens,).
    """
    n = L * L
    arrays = [(r.timeseries["n_UC"] + r.timeseries["n_CC"]) / n for r in results]
    return np.mean(arrays, axis=0)
