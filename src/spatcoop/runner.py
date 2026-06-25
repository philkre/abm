"""Checkpoint system and batch execution via joblib."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from contextlib import contextmanager

import joblib
import numpy as np
from joblib import Parallel, delayed
from tqdm import tqdm

from spatcoop.params import ModelParams
from spatcoop.model import run_episode, run_episode_with_frames, RunResult


@contextmanager
def _tqdm_joblib(bar: tqdm):
    """Patch joblib's batch callback to tick a tqdm bar on each completed task."""
    class _Callback(joblib.parallel.BatchCompletionCallBack):
        def __call__(self, *args, **kwargs):
            bar.update(n=self.batch_size)
            return super().__call__(*args, **kwargs)

    old = joblib.parallel.BatchCompletionCallBack
    joblib.parallel.BatchCompletionCallBack = _Callback
    try:
        yield bar
    finally:
        joblib.parallel.BatchCompletionCallBack = old
        bar.close()

RESULTS_DIR = Path("results/raw")


def result_path(p: ModelParams, seed: int) -> Path:
    return RESULTS_DIR / f"{p.hash()}_{seed:06d}.npz"


def already_done(p: ModelParams, seed: int) -> bool:
    return result_path(p, seed).exists()


def save_result(r: RunResult) -> None:
    path = result_path(r.params, r.seed)
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays: dict = {f"ts_{k}": v for k, v in r.timeseries.items()}
    arrays.update({f"sum_{k}": np.array(v) for k, v in r.summary.items()})
    arrays["params_json"] = np.array(json.dumps(asdict(r.params)), dtype=object)
    arrays["seed"] = np.array(r.seed)
    np.savez_compressed(path, **arrays)


def load_result(path: Path) -> RunResult:
    d = np.load(path, allow_pickle=True)
    p = ModelParams(**json.loads(str(d["params_json"])))
    ts = {k[3:]: d[k] for k in d if k.startswith("ts_")}
    summary = {k[4:]: float(d[k]) for k in d if k.startswith("sum_")}
    return RunResult(params=p, seed=int(d["seed"]), timeseries=ts, summary=summary)


def _run_one(p: ModelParams, seed: int) -> None:
    """Run one episode and save; skip if already on disk."""
    if already_done(p, seed):
        return
    r = run_episode(p, seed)
    save_result(r)


def run_batch(
    params_list: list[ModelParams],
    seeds: list[int],
    n_jobs: int = -1,
) -> None:
    """Run all (params, seed) combinations not already on disk. Idempotent."""
    tasks = [(p, s) for p in params_list for s in seeds if not already_done(p, s)]
    n_cached = len(params_list) * len(seeds) - len(tasks)
    print(f"Running {len(tasks)} new combinations ({n_cached} already cached).")
    bar = tqdm(total=len(tasks), desc="batch", unit="run")
    with _tqdm_joblib(bar):
        Parallel(n_jobs=n_jobs, verbose=0)(delayed(_run_one)(p, s) for p, s in tasks)


# ── Visualization sweep ───────────────────────────────────────────────────────

VIZ_DIR = Path("results/viz")


def viz_result_path(p: ModelParams, seed: int, out_dir: Path = VIZ_DIR) -> Path:
    return out_dir / f"{p.hash()}_{seed:06d}_frames.npz"


def viz_already_done(p: ModelParams, seed: int, out_dir: Path = VIZ_DIR) -> bool:
    return viz_result_path(p, seed, out_dir).exists()


def save_viz_result(
    r: RunResult,
    frames: dict[int, dict[str, np.ndarray]],
    out_dir: Path = VIZ_DIR,
) -> Path:
    """Save summary scalars + spatial frames to a single compressed .npz.

    Frame arrays are stored as ``frame_{gen:04d}_{field}`` (e.g.
    ``frame_0499_strategy``).  Fields: strategy (int8), env (float32),
    wealth (float32).
    """
    path = viz_result_path(r.params, r.seed, out_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays: dict = {}
    arrays["params_json"] = np.array(json.dumps(asdict(r.params)), dtype=object)
    arrays["seed"] = np.array(r.seed)
    for k, v in r.summary.items():
        arrays[f"sum_{k}"] = np.array(v)
    for gen, fields in frames.items():
        for field, arr in fields.items():
            arrays[f"frame_{gen:04d}_{field}"] = arr
    np.savez_compressed(path, **arrays)
    return path


def _run_viz_one(p: ModelParams, seed: int, snap_gens: list[int], out_dir: Path) -> None:
    """Run one viz episode and save frames; skip if already on disk."""
    if viz_already_done(p, seed, out_dir):
        return
    r, frames = run_episode_with_frames(p, seed, snap_gens)
    save_viz_result(r, frames, out_dir)


def run_viz_batch(
    params_list: list[ModelParams],
    seeds: list[int],
    snap_gens: list[int],
    out_dir: Path = VIZ_DIR,
    n_jobs: int = -1,
) -> None:
    """Run all (params, seed) viz combinations not already on disk. Idempotent."""
    tasks = [(p, s) for p in params_list for s in seeds if not viz_already_done(p, s, out_dir)]
    n_cached = len(params_list) * len(seeds) - len(tasks)
    print(
        f"Viz sweep: {len(tasks)} new runs ({n_cached} cached) | "
        f"snap_gens={snap_gens} | out={out_dir}"
    )
    bar = tqdm(total=len(tasks), desc="viz", unit="run")
    with _tqdm_joblib(bar):
        Parallel(n_jobs=n_jobs, verbose=0)(
            delayed(_run_viz_one)(p, s, snap_gens, out_dir) for p, s in tasks
        )
