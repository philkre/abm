"""
1-D parameter sweeps. For each swept parameter, runs the model over a grid of
values (× seeds) and saves one grid figure (every order parameter vs the value)
via plots.plot_op_vs_param.

Swept parameters: delta, gamma, eta (environment feedback), lambda_mean (loss
aversion — needs CC present, so initial_mix="thirds"), and b / w0 (wealth/income).

    uv run spatcoop param-sweep
    rm results/raw/*.npz
"""

from __future__ import annotations

from dataclasses import replace
from typing import Sequence

import numpy as np

from spatcoop.params import ModelParams
from spatcoop.runner import run_batch
from spatcoop.plots import plot_op_vs_param, ALL_OPS


def sweep(
    base: ModelParams,
    param_name: str,
    values: np.ndarray,
    seeds: Sequence[int],
    metrics: Sequence[str] = ALL_OPS,
    n_jobs: int = -1,
) -> None:
    """Sweep one parameter over `values`, run all seeds, and save a grid figure.

    base:       ModelParams; all fields fixed except `param_name`.
    param_name: the swept field.
    values:     1-D array of parameter values.
    metrics:    order parameters to plot (default: all).
    """
    param_list = [replace(base, **{param_name: float(v)}) for v in values]
    run_batch(param_list, list(seeds), n_jobs=n_jobs)
    plot_op_vs_param(param_name, list(values), base, seeds, keys=list(metrics))


def run_param_sweeps(
    base: ModelParams,
    seeds: Sequence[int],
    n_jobs: int = -1,
    n_points: int = 21,
    only: Sequence[str] | None = None,
) -> None:
    """Run 1-D sweeps of delta, gamma, eta, lambda_mean, b, and w0.

    base:     ModelParams; the swept field is overwritten inside `sweep`.
    n_points: number of grid points per sweep.
    only:     if given, restrict to these parameter names (for quick/micro runs).
    """
    lin = lambda lo, hi: np.linspace(lo, hi, n_points)  # noqa: E731

    # (param, value grid, base used for this sweep). lambda_mean needs CC agents.
    specs: dict[str, tuple[np.ndarray, ModelParams]] = {
        "delta": (lin(0.0, 1.0), base),
        "gamma": (lin(0.0, 0.1), base),
        "eta": (lin(0.0, 0.1), base),
        "lambda_mean": (lin(1.0, 3.0), replace(base, initial_mix="thirds")),
        "b": (lin(0.0, 3.0), base),
        "w0": (lin(0.5, 3.0), base),
    }
    if only:
        specs = {k: v for k, v in specs.items() if k in only}

    for name, (values, sweep_base) in specs.items():
        sweep(sweep_base, name, values, seeds, n_jobs=n_jobs)
