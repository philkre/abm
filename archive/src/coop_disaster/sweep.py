"""Parameter sweep: success rate vs UC proportion."""

import random
from concurrent.futures import ProcessPoolExecutor

from tqdm import tqdm

from coop_disaster.group import assign_types, simulate_group
from coop_disaster.types import SimConfig


def _worker(args: tuple[float, SimConfig, int]) -> float:
    """Simulate cfg.n_groups groups at one UC proportion; return success fraction."""
    uc_prop, cfg, seed = args
    rng = random.Random(seed)
    n_success = sum(simulate_group(assign_types(uc_prop, cfg, rng), cfg) for _ in range(cfg.n_groups))
    return n_success / cfg.n_groups


def run_sweep(
    uc_props: list[float],
    cfg: SimConfig,
    *,
    n_jobs: int = 1,
) -> list[float]:
    """Sweep UC proportions and return the success rate at each point.

    Corresponds to condcoop's vary_only_uc(). Parallelises over UC proportion
    values using ProcessPoolExecutor when n_jobs > 1.

    Args:
        uc_props: Sequence of UC proportion values to evaluate (e.g. 0.0..1.0).
        cfg: Simulation config.
        n_jobs: Worker processes for parallelism (1 = serial).

    Returns:
        List of success rates, one per entry in uc_props.
    """
    task_args = [(uc, cfg, seed) for seed, uc in enumerate(uc_props)]
    pbar = tqdm(total=len(task_args), unit="pt")
    if n_jobs == 1:
        results = []
        for a in task_args:
            results.append(_worker(a))
            pbar.update()
        pbar.close()
        return results
    with ProcessPoolExecutor(max_workers=n_jobs) as pool:
        results = []
        for r in pool.map(_worker, task_args):
            results.append(r)
            pbar.update()
        pbar.close()
        return results
