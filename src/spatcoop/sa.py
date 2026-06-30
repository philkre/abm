"""SALib wrapper: sample → batch → analyse (Sobol, Morris, PAWN, Delta).

Provides two interfaces:
- Legacy functions (sample_params, analyse_sa, run_sa) for the fixed LINEAR/SIGMOID problems.
- Dynamic functions (build_problem, sample_params_from_problem, run_sa_custom) that accept
  arbitrary parameter ranges from the CLI, running a separate analysis file per output metric.

Recommended three-tier workflow for this model
-----------------------------------------------
1. morris  — cheap screen (O(N*(k+1)) runs). Identifies which parameters are non-influential
             so they can be fixed before the expensive Sobol/PAWN sweep.
2. sobol   — variance decomposition (S1, ST). Quantifies interactions (S1 vs ST gap).
             Misleading as a *ranking* when output is bimodal, but the S1/ST split is the
             cleanest way to separate direct effects from interactions.
3. pawn    — headline ranking for `resilience` and other bounded, bimodal outputs.
             Compares unconditional vs conditional CDFs (KS statistic); correctly sees
             "fixing this parameter collapses the bimodality" even when variance barely moves.
             PAWN analysis can be run on any existing (X, Y) — including a Sobol sample —
             without resampling, via `sensitivity analyse --method pawn`.

Why `resilience` is a worst case for pure Sobol
  • resilience ∈ [0,1] piles at 0 and 1 near phase boundaries — bimodal, not Gaussian.
  • Discontinuous C/D/C+D phase transitions (à la Ding) make the sweep bimodal by design.
  • Stochastic fixation under near-neutral drift adds bimodality across seeds too.
  Sobol ranks parameters by their share of total variance; PAWN ranks by distributional shift.
  Both are informative — neither alone is sufficient.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed
from SALib.sample import saltelli
from SALib.analyze import sobol
from tqdm import tqdm

from spatcoop.params import ModelParams, LINEAR, SIGMOID
from spatcoop.runner import run_batch, load_result, result_path
from spatcoop.model import OBS_KEYS

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
    name for name, field in ModelParams.__dataclass_fields__.items() if field.type in (float, int)
)

# Alias → (real param name, conversion fn)
# T_over_E is more interpretable than T; converted via T = value * 5.0 (5 cells × E=1)
_SA_PARAM_ALIASES: dict[str, tuple[str, Callable[[float], float]]] = {
    "T_over_E": ("T", lambda v: float(v) * 5.0),
}

# Every summary statistic produced by run_episode is a valid SA target: each
# observable (OBS_KEYS), its final-window std (`*_std`), and the post-processed
# scalars added at the end of run_episode.
VALID_OUTPUT_KEYS: frozenset[str] = (
    frozenset(OBS_KEYS)
    | frozenset(f"{k}_std" for k in OBS_KEYS)
    | frozenset({"moran_i", "uc_oscillation", "uc_flip_rate"})
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

    phase = SIGMOID if base_params.risk_mode == SIGMOID else LINEAR
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
            raise ValueError(f"Cannot vary {name!r}. Valid numeric parameters:\n" f"  {sorted(valid)}")
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
    Generate a ModelParams sample for the given SA method.

    Returns (params_list, X) where X is the raw sample matrix needed for analysis.
    Total sample sizes:
      - sobol:  N * (num_vars + 2)  — Saltelli quasi-random design
      - morris: N * (num_vars + 1)  — N trajectories (N = 5–15 typical)
      - pawn:   N                   — Latin Hypercube; handles bimodal/non-normal outputs
      - delta:  N                   — Latin Hypercube; moment-independent, handles bimodal outputs
    """
    if method == "sobol":
        X = saltelli.sample(problem, N, calc_second_order=False)
    elif method == "morris":
        from SALib.sample import morris as morris_sample  # noqa: PLC0415

        X = morris_sample.sample(problem, N)
    elif method in ("pawn", "delta"):
        # Distribution-based methods use LHS; total samples = N (no multiplier)
        from SALib.sample import latin  # noqa: PLC0415

        X = latin.sample(problem, N)
    else:
        raise ValueError(f"method must be 'sobol', 'morris', 'pawn', or 'delta', got {method!r}")

    params_list = [_apply_row(problem["names"], row, base_params) for row in X]
    return params_list, X


def collect_Y_vectors(
    params_list: list[ModelParams],
    seeds: list[int],
    output_keys: list[str],
    n_jobs: int = -1,
    raw_dir: Path = Path("results/raw"),
) -> dict[str, np.ndarray]:
    """Load saved results, average over seeds, return {output_key: Y_array}.

    Uses parallel I/O (joblib threads) over parameter points — each worker loads
    all seeds for one point and returns a dict of per-key means.
    """

    def _load_one(p: ModelParams) -> dict[str, float]:
        return {
            key: float(np.mean([load_result(result_path(p, s, raw_dir)).summary[key] for s in seeds]))
            for key in output_keys
        }

    rows: list[dict[str, float]] = Parallel(n_jobs=n_jobs, prefer="threads")(  # type: ignore[assignment]
        delayed(_load_one)(p) for p in tqdm(params_list, desc="loading results", unit="param")
    )
    return {key: np.array([r[key] for r in rows], dtype=np.float64) for key in output_keys}


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


def _compute_pawn(problem: dict, X: np.ndarray, Y: np.ndarray) -> dict:
    """
    PAWN sensitivity index (Pianosi & Wagener 2015).

    Compares unconditional vs conditional CDFs via KS statistic.
    KS ∈ [0, 1]: higher = more influential. Correct for bimodal outputs because
    it operates on the full distribution rather than just its variance.
    """
    from SALib.analyze import pawn as pawn_analyze  # noqa: PLC0415

    Si = pawn_analyze.analyze(problem, X, Y, S=10, print_to_console=False)
    return {
        "KS": Si["median"].tolist(),  # median KS across conditioning intervals
        "KS_min": Si["minimum"].tolist(),
        "KS_mean": Si["mean"].tolist(),
        "KS_max": Si["maximum"].tolist(),
        "KS_conf": Si["CV"].tolist(),  # coefficient of variation across intervals
    }


def _compute_delta(problem: dict, X: np.ndarray, Y: np.ndarray) -> dict:
    """
    Borgonovo δ moment-independent sensitivity index (2007).

    Measures the expected shift in the full output distribution when an input
    is fixed. Correct for bimodal outputs; includes first-order Sobol S1 as a
    by-product (for comparison).
    """
    from SALib.analyze import delta as delta_analyze  # noqa: PLC0415

    Si = delta_analyze.analyze(problem, X, Y, print_to_console=False)
    return {
        "delta": Si["delta"].tolist(),
        "delta_conf": Si["delta_conf"].tolist(),
        "S1": Si["S1"].tolist(),
        "S1_conf": Si["S1_conf"].tolist(),
    }


_COMPUTE_FN = {
    "sobol": _compute_sobol,
    "morris": _compute_morris,
    "pawn": _compute_pawn,
    "delta": _compute_delta,
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


def _task_slice(n_total: int, task_id: int, n_tasks: int) -> tuple[int, int]:
    """Return (lo, hi) slice indices for one SLURM array task."""
    chunk = n_total // n_tasks
    lo = task_id * chunk
    hi = lo + chunk if task_id < n_tasks - 1 else n_total
    return lo, hi


def run_sa_custom(
    vary_specs: list[tuple[str, float, float]],
    N: int,
    base_params: ModelParams,
    seeds: list[int],
    output_keys: list[str],
    method: str = "pawn",
    n_jobs: int = -1,
    out_dir: Path = Path("results/sa/custom"),
    raw_dir: Path = Path("results/raw"),
    task_id: int | None = None,
    n_tasks: int | None = None,
) -> None:
    """
    Full SA pipeline: build problem → sample → run sims → collect outputs → analyse.

    Saves one result file per output key: {out_dir}/{method}_{output_key}.json
    Also saves run_config.json and sample_X.npy for later re-analysis.

    SLURM array mode: when task_id and n_tasks are both set, only the corresponding
    slice of the sample is simulated and the analysis step is skipped.  Run
    `spatcoop sensitivity analyse --out-dir <out_dir>` once all array tasks finish.
    """
    if method not in _COMPUTE_FN:
        raise ValueError(f"method must be one of {list(_COMPUTE_FN)}, got {method!r}")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    problem = build_problem(vary_specs)
    params_list, X = sample_params_from_problem(problem, N, base_params, method)
    n_samples = len(params_list)

    # ── Persist config + sample (idempotent; all array tasks write the same content) ──
    config = {
        "method": method,
        "N": N,
        "problem": problem,
        "seeds": seeds,
        "output_keys": output_keys,
        "base_params": asdict(base_params),
    }
    config_path = out_dir / "run_config.json"
    if not config_path.exists():
        config_path.write_text(json.dumps(config, indent=2))
    sample_path = out_dir / "sample_X.npy"
    if not sample_path.exists():
        np.save(sample_path, X)

    # ── Determine which param points this task is responsible for ──────────────
    if task_id is not None and n_tasks is not None:
        lo, hi = _task_slice(n_samples, task_id, n_tasks)
        run_slice = params_list[lo:hi]
        print(
            f"SA array task {task_id + 1}/{n_tasks}: "
            f"simulating param points [{lo}:{hi}] ({len(run_slice)} of {n_samples})"
        )
        run_batch(run_slice, seeds, n_jobs=n_jobs, raw_dir=raw_dir)
        print(f"  Done. When all {n_tasks} tasks finish, run:")
        print(f"    spatcoop sensitivity analyse --out-dir {out_dir} --recompute")
        return

    run_slice = params_list
    print(f"SA: method={method}, N={N}, {n_samples} model runs × {len(seeds)} seeds")
    print(f"  Varying: {list(zip(problem['names'], problem['bounds']))}")
    print(f"  Output keys: {output_keys}")

    # ── Simulate (idempotent checkpoints) ─────────────────────────────────────
    run_batch(run_slice, seeds, n_jobs=n_jobs, raw_dir=raw_dir)

    # ── Collect Y vectors (parallel I/O) ──────────────────────────────────────
    Y_dict = collect_Y_vectors(params_list, seeds, output_keys, n_jobs=n_jobs, raw_dir=raw_dir)

    # ── Compute SA indices in parallel across output keys ─────────────────────
    _compute = _COMPUTE_FN[method]

    def _analyse_key(key: str, Y: np.ndarray) -> Path:
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
        return out_path

    saved = Parallel(
        n_jobs=min(len(output_keys), n_jobs if n_jobs > 0 else len(output_keys)),
        prefer="threads",
    )(delayed(_analyse_key)(key, Y) for key, Y in Y_dict.items())
    for path in saved:
        print(f"  Saved: {path}")


def reanalyse_from_dir(
    out_dir: Path,
    output_keys: list[str] | None = None,
    method_override: str | None = None,
    raw_dir: Path = Path("results/raw"),
) -> None:
    """
    Re-collect outputs and recompute SA indices from a saved run_config.json.

    Useful after additional simulation results are checkpointed, or to apply a
    different analysis method to an existing sample.  For example, a Sobol run
    can be reanalysed with PAWN (no resampling needed — PAWN's KS statistic
    works on any (X, Y) pair):

        spatcoop sensitivity analyse --out-dir results/sa/custom --method pawn --recompute

    Args:
        out_dir:         Directory containing run_config.json and sample_X.npy.
        output_keys:     Restrict to these keys (default: all keys in run_config).
        method_override: Apply this analysis method instead of the one stored in
                         run_config.json.  The sample X is reused unchanged.
    """
    out_dir = Path(out_dir)
    config_path = out_dir / "run_config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"No run_config.json found in {out_dir}")

    config = json.loads(config_path.read_text())
    sample_method = config["method"]  # method used for sampling
    method = method_override or sample_method  # method used for analysis
    if method not in _COMPUTE_FN:
        raise ValueError(f"method must be one of {list(_COMPUTE_FN)}, got {method!r}")

    N = config["N"]
    problem = config["problem"]
    seeds = config["seeds"]
    keys = output_keys or config["output_keys"]
    base_params = ModelParams(**config["base_params"])
    X = np.load(out_dir / "sample_X.npy")

    params_list = [_apply_row(problem["names"], X[i], base_params) for i in range(len(X))]

    label = method if method == sample_method else f"{method} (sample: {sample_method})"
    print(f"Re-analysing {out_dir} ({label}, {len(params_list)} samples, keys={keys})")
    Y_dict = collect_Y_vectors(params_list, seeds, keys, raw_dir=raw_dir)
    _compute = _COMPUTE_FN[method]

    for key, Y in Y_dict.items():
        indices = _compute(problem, X, Y)
        out_path = out_dir / f"{method}_{key}.json"
        _save_sa_result(out_path, method, key, problem, N, len(X), len(seeds), base_params, indices)
        print(f"  Saved: {out_path}")
