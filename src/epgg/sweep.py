"""Parameter sweeps: ensemble-averaged stationary cooperator fractions.

Each parameter point runs `n_repeats` independent sessions from fresh random
inits (no warm-start across points — discontinuous transitions would otherwise
show spurious hysteresis) and averages their final-window fractions.
"""

from __future__ import annotations

import numpy as np

from epgg.model import run_to_stationarity


def coop_fraction_at(
    delta: float,
    gamma: float,
    L: int = 200,
    r: float = 4.0,
    c: float = 1.0,
    n_repeats: int = 20,
    base_seed: int = 42,
    **run_kwargs,
) -> float:
    """Mean stationary cooperator fraction over `n_repeats` fresh-init sessions."""
    fracs = [
        run_to_stationarity(
            L, delta, gamma, r=r, c=c, seed=base_seed + i, **run_kwargs
        ).coop_fraction
        for i in range(n_repeats)
    ]
    return float(np.mean(fracs))


def delta_sweep(
    deltas,
    gamma: float,
    L: int = 200,
    r: float = 4.0,
    c: float = 1.0,
    n_repeats: int = 20,
    base_seed: int = 42,
    **run_kwargs,
) -> np.ndarray:
    """Cooperator fraction vs delta at fixed gamma (Fig 2 cross section)."""
    return np.array(
        [
            coop_fraction_at(
                d,
                gamma,
                L=L,
                r=r,
                c=c,
                n_repeats=n_repeats,
                base_seed=base_seed,
                **run_kwargs,
            )
            for d in deltas
        ]
    )
