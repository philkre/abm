"""
Parameter sweeps for delta, gamma, and eta.

uv run spatcoop param-sweep
"""

import numpy as np
from typing import Sequence
from dataclasses import replace
import matplotlib.pyplot as plt
from pathlib import Path

from spatcoop.params import ModelParams
from spatcoop.runner import run_batch
from spatcoop.analysis import load_all_results, summary_table

METRICS = ["resilience", "mean_env", "flood_rate"]
FIGURES_DIR = Path("results/figures")

def save(fig, name: str) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / name
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return path

def sweep(
        base: ModelParams,
        param_name: str,
        values: np.ndarray,
        seeds: Sequence[int],
        n_jobs: int = -1,
) -> None:
    """
    Sweep one parameter over values and save plot.

    base: ModelParams where all stay fixed except for "param_name"
    param_name: sweeped parameter
    values: 1D array of parameter values.
    seeds: list of seeds
    n_jobs: number of parallel jobs
    """

    param_list = [replace(base, **{param_name: float(v)}) for v in values]

    run_batch(param_list, list(seeds), n_jobs=n_jobs)

    results = load_all_results(param_list, seeds)
    tbl = summary_table(results, keys=METRICS)      #shape = (n, 3)

    # plots: metric vs parameter value
    for idx, metric in enumerate(METRICS):
        y = tbl[:, idx]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(values, y, marker="o", lw=1.5)
        ax.set_xlabel(param_name)
        ax.set_ylabel(metric)
        ax.set_title(f"Effect of {param_name} on {metric}")
        ax.grid(True, alpha=0.3)
        fname = f"sweep_{param_name}_{metric}.png"
        save(fig, fname)

def run_param_sweeps(
        base: ModelParams,
        seeds: Sequence[int],
        n_jobs: int = -1,
        n_points: int = 21,
) -> None:
    """
    Run sweep for detla, gamma, and eta on [0,1].
    For each parameter:
    - run model at n_points in [0,1]
    - compute mean resilience, mean_env, and flood_rate
    - save plots

    base: ModelParams where all stay fixed except for selected parameters
    seeds: list of seeds
    n_jobs: number of parallel jobs
    n_points: number of gridpoints in [0,1]
    """
    values = np.linspace(0.0, 1.0, n_points)
    for param_name in ["delta", "gamma", "eta"]:
        sweep(base, param_name, values, seeds, n_jobs=n_jobs)

if __name__ == "__main__":
    base = ModelParams()
    seeds = list(range(8))
    run_param_sweeps(base, seeds, n_jobs=-1, n_points=21)