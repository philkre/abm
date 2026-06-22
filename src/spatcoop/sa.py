"""SALib wrapper: sample → batch → analyse (Sobol and Morris sensitivity analysis).

Provides two interfaces:
- Legacy functions (sample_params, analyse_sa, run_sa) for the fixed LINEAR/SIGMOID problems.
- Dynamic functions (build_problem, sample_params_from_problem, run_sa_custom) that accept
  arbitrary parameter ranges from the CLI, running a separate analysis file per output metric.
"""

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

# ── Pre-defined SA problems (legacy, used by run-batch command) ────────────────

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

# ── Parameter metadata ────────────────────────────────────────────────────────

# Numeric (float/int) ModelParams fields that can be varied in SA
_NUMERIC_FIELDS: frozenset[str] = frozenset(
    name
    for name, field in ModelParams.__dataclass_fields__.items()
    if field.type in (float, int)
)

# Alias → (real param name, conversion fn)
# T_over_E is more interpretable than T; converted via T = value * 5.0 (5 cells × E=1)
_SA_PARAM_ALIASES: dict[str, tuple[str, object]] = {
    "T_over_E": ("T", lambda v: float(v) * 5.0),
}

VALID_OUTPUT_KEYS: frozenset[str] = frozenset(
    {
        "n_D",
        "n_UC",
        "n_CC",
        "mean_wealth",
        "flood_rate",
        "mean_env",
        "resilience",
        "moran_i",
    }
)

# ── Legacy functions ──────────────────────────────────────────────────────────


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


# ── Dynamic SA functions ──────────────────────────────────────────────────────


def build_problem(vary_specs: list[tuple[str, float, float]]) -> dict:
    """
    Build a SALib problem dict from vary_specs = [(name, lo, hi), ...].

    Accepts both real ModelParams field names and the T_over_E alias.
    """
    valid = _NUMERIC_FIELDS | set(_SA_PARAM_ALIASES)
    for name, lo, hi in vary_specs:
        if name not in valid:
            raise ValueError(
                f"Cannot vary {name!r}. Valid numeric parameters:\n"
                f"  {sorted(valid)}"
            )
        if lo >= hi:
            raise ValueError(f"Range for {name!r} requires lo < hi, got [{lo}, {hi}]")
    return {
        "num_vars": len(vary_specs),
        "names": [name for name, _, _ in vary_specs],
        "bounds": [[lo, hi] for _, lo, hi in vary_specs],
    }


def _apply_row(names: list[str], row: np.ndarray, base: ModelParams) -> ModelParams:
    """Apply one sample row to base params, handling aliases and type casting."""
    kw = asdict(base)
    for name, val in zip(names, row):
        if name in _SA_PARAM_ALIASES:
            real_name, convert = _SA_PARAM_ALIASES[name]
            kw[real_name] = convert(val)
        else:
            field = ModelParams.__dataclass_fields__[name]
            kw[name] = int(round(val)) if field.type is int else float(val)
    return ModelParams(**kw)


def sample_params_from_problem(
    problem: dict,
    N: int,
    base_params: ModelParams,
    method: str,
) -> tuple[list[ModelParams], np.ndarray]:
    """
    Generate a ModelParams sample using Saltelli (Sobol) or Morris design.

    Returns (params_list, X) where X is the raw sample matrix needed for analysis.
    Total sample sizes:
      - sobol:  N * (num_vars + 2)
      - morris: N * (num_vars + 1)  (N = number of trajectories, typically 5–15)
    """
    if method == "sobol":
        X = saltelli.sample(problem, N, calc_second_order=False)
    elif method == "morris":
        from SALib.sample import morris as morris_sample  # noqa: PLC0415

        X = morris_sample.sample(problem, N)
    else:
        raise ValueError(f"method must be 'sobol' or 'morris', got {method!r}")

    params_list = [_apply_row(problem["names"], row, base_params) for row in X]
    return params_list, X


def collect_Y_vectors(
    params_list: list[ModelParams],
    seeds: list[int],
    output_keys: list[str],
) -> dict[str, np.ndarray]:
    """Load saved results, average over seeds, return {output_key: Y_array}."""
    Y: dict[str, list[float]] = {key: [] for key in output_keys}
    for p in tqdm(params_list, desc="loading results", unit="param"):
        for key in output_keys:
            vals = [load_result(result_path(p, s)).summary[key] for s in seeds]
            Y[key].append(float(np.mean(vals)))
    return {key: np.array(v, dtype=np.float64) for key, v in Y.items()}


def _compute_sobol(problem: dict, X: np.ndarray, Y: np.ndarray) -> dict:
    Si = sobol.analyze(problem, Y, calc_second_order=False, print_to_console=False)
    return {
        "S1": Si["S1"].tolist(),
        "ST": Si["ST"].tolist(),
        "S1_conf": Si["S1_conf"].tolist(),
        "ST_conf": Si["ST_conf"].tolist(),
    }


def _compute_morris(problem: dict, X: np.ndarray, Y: np.ndarray) -> dict:
    from SALib.analyze import morris as morris_analyze  # noqa: PLC0415

    Si = morris_analyze.analyze(problem, X, Y, print_to_console=False)
    return {
        "mu": Si["mu"].tolist(),
        "mu_star": Si["mu_star"].tolist(),
        "sigma": Si["sigma"].tolist(),
        "mu_star_conf": Si["mu_star_conf"].tolist(),
    }


def _save_sa_result(
    out_path: Path,
    method: str,
    output_key: str,
    problem: dict,
    N: int,
    n_samples: int,
    n_seeds: int,
    base_params: ModelParams,
    indices: dict,
) -> None:
    result = {
        "method": method,
        "output_key": output_key,
        "problem": problem,
        "N": N,
        "n_samples": n_samples,
        "n_seeds": n_seeds,
        "base_params": asdict(base_params),
        **indices,
    }
    out_path.write_text(json.dumps(result, indent=2))


def run_sa_custom(
    vary_specs: list[tuple[str, float, float]],
    N: int,
    base_params: ModelParams,
    seeds: list[int],
    output_keys: list[str],
    method: str = "sobol",
    n_jobs: int = -1,
    out_dir: Path = Path("results/sa/custom"),
) -> None:
    """
    Full SA pipeline: build problem → sample → run sims → collect outputs → analyse.

    Saves one result file per output key: {out_dir}/{method}_{output_key}.json
    Also saves run_config.json and sample_X.npy for later re-analysis.
    """
    out_dir = Path(out_dir)
    problem = build_problem(vary_specs)
    params_list, X = sample_params_from_problem(problem, N, base_params, method)

    n_samples = len(params_list)
    print(f"SA: method={method}, N={N}, {n_samples} model runs × {len(seeds)} seeds")
    print(f"  Varying: {list(zip(problem['names'], problem['bounds']))}")
    print(f"  Output keys: {output_keys}")

    # Run simulations (idempotent: skips already-computed checkpoints)
    run_batch(params_list, seeds, n_jobs=n_jobs)

    # Persist config and sample matrix so analysis can be repeated without re-running
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "method": method,
        "N": N,
        "problem": problem,
        "seeds": seeds,
        "output_keys": output_keys,
        "base_params": asdict(base_params),
    }
    (out_dir / "run_config.json").write_text(json.dumps(config, indent=2))
    np.save(out_dir / "sample_X.npy", X)

    # Compute SA indices per output key and save to separate files
    Y_dict = collect_Y_vectors(params_list, seeds, output_keys)
    _compute = _compute_sobol if method == "sobol" else _compute_morris

    for key, Y in Y_dict.items():
        indices = _compute(problem, X, Y)
        out_path = out_dir / f"{method}_{key}.json"
        _save_sa_result(
            out_path,
            method,
            key,
            problem,
            N,
            n_samples,
            len(seeds),
            base_params,
            indices,
        )
        print(f"  Saved: {out_path}")


def reanalyse_from_dir(
    out_dir: Path,
    output_keys: list[str] | None = None,
) -> None:
    """
    Re-collect outputs and recompute SA indices from a saved run_config.json.

    Useful when additional simulation results have been checkpointed since the
    original run_sa_custom call, or to compute indices for new output keys.
    """
    out_dir = Path(out_dir)
    config_path = out_dir / "run_config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"No run_config.json found in {out_dir}")

    config = json.loads(config_path.read_text())
    method = config["method"]
    N = config["N"]
    problem = config["problem"]
    seeds = config["seeds"]
    keys = output_keys or config["output_keys"]
    base_params = ModelParams(**config["base_params"])
    X = np.load(out_dir / "sample_X.npy")

    params_list = [
        _apply_row(problem["names"], X[i], base_params) for i in range(len(X))
    ]

    print(f"Re-analysing {out_dir} ({method}, {len(params_list)} samples, keys={keys})")
    Y_dict = collect_Y_vectors(params_list, seeds, keys)
    _compute = _compute_sobol if method == "sobol" else _compute_morris

    for key, Y in Y_dict.items():
        indices = _compute(problem, X, Y)
        out_path = out_dir / f"{method}_{key}.json"
        _save_sa_result(
            out_path, method, key, problem, N, len(X), len(seeds), base_params, indices
        )
        print(f"  Saved: {out_path}")
