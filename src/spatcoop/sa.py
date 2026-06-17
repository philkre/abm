"""SALib wrapper: sample → batch → analyse (Sobol sensitivity analysis)."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
from SALib.sample import saltelli
from SALib.analyze import sobol
from tqdm import tqdm

from spatcoop.params import ModelParams, LINEAR, SIGMOID
from spatcoop.runner import run_batch, load_result, result_path

LINEAR_PROBLEM = {
    "num_vars": 4,
    "names": ["beta", "p_max", "T_over_E", "ell"],
    "bounds": [[0.1, 10.0], [0.0, 1.0], [0.4, 0.9], [0.0, 1.0]],
}

SIGMOID_PROBLEM = {
    "num_vars": 4,
    "names": ["beta", "k", "e0", "T_over_E"],
    "bounds": [[0.1, 10.0], [1.0, 20.0], [-1.0, 1.0], [0.4, 0.9]],
}


def sample_params(
    problem: dict,
    N: int,
    base_params: ModelParams,
) -> tuple[list[ModelParams], np.ndarray]:
    """
    Generate Saltelli sample of ModelParams objects.

    N: base sample size; total samples = N * (num_vars + 2).
    Returns (params_list, X) where X is the raw sample matrix for SALib.analyse.
    """
    X = saltelli.sample(problem, N, calc_second_order=False)
    params_list = []
    for row in X:
        overrides = dict(zip(problem["names"], row))
        if "T_over_E" in overrides:
            overrides["T"] = overrides.pop("T_over_E") * 5.0  # 5 cells × E=1
        kw = asdict(base_params)
        kw.update(overrides)
        params_list.append(ModelParams(**kw))
    return params_list, X


def analyse_sa(
    problem: dict,
    X: np.ndarray,
    Y: np.ndarray,
    out_path: Path,
) -> dict:
    """
    Compute Sobol indices from Y (n_samples,) and save to JSON.
    Returns the indices dict.
    """
    Si = sobol.analyze(problem, Y, calc_second_order=False, print_to_console=False)
    result = {k: Si[k].tolist() for k in ["S1", "ST", "S1_conf", "ST_conf"]}
    result["names"] = problem["names"]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    return result


def run_sa(
    problem: dict,
    N: int,
    base_params: ModelParams,
    seeds: list[int],
    n_jobs: int = -1,
    output_key: str = "resilience",
) -> dict:
    """End-to-end: sample → run (with checkpointing) → analyse."""
    params_list, X = sample_params(problem, N, base_params)
    run_batch(params_list, seeds, n_jobs=n_jobs)

    Y = np.array(
        [
            np.mean([load_result(result_path(p, s)).summary[output_key] for s in seeds])
            for p in tqdm(params_list, desc="loading results", unit="param")
        ],
        dtype=np.float64,
    )

    phase = "sigmoid" if base_params.risk_mode == SIGMOID else "linear"
    out = Path(f"results/sa/sobol_{phase}_N{N}.json")
    return analyse_sa(problem, X, Y, out)
