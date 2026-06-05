"""Parameter sweep: success rate vs UC proportion."""

import random
from concurrent.futures import ProcessPoolExecutor

from coop_disaster.types import SimConfig


def _worker(args: tuple[float, SimConfig, int]) -> float:
    """Simulate cfg.n_groups groups at one UC proportion; return success fraction."""
    ...


def run_sweep(
    uc_props: list[float],
    cfg: SimConfig,
    *,
    n_jobs: int = 1,
) -> list[float]:
    """Sweep UC proportions and return the success rate at each point.

    Args:
        uc_props: Sequence of UC proportion values to evaluate (e.g. 0.0..1.0).
        cfg: Simulation config.
        n_jobs: Worker processes for parallelism (1 = serial).

    Returns:
        List of success rates, one per entry in uc_props.
    """
    ...
