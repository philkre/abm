"""Validation target: Weitz oscillation (mean-field, soft check).

The Ding and Jonsson replicative targets were removed — neither is achievable
for this model as written:

  - Ding: spatcoop couples environment → flood *risk*, not environment →
    *payoff* (there is no `r·Σe` benefit term). At `p_max=0` (the Ding
    isolation point) the environment no longer affects payoff, leaving pure
    cost, so the cooperative C phase cannot exist. spatcoop is not
    Ding-reducible; the epgg package holds the Ding reproduction instead.
  - Jonsson: the threshold-resilience metric `(pool ≥ T)` needs near-universal
    contribution and reads ~0 with any defectors present, so it does not match
    Jonsson's contribution-level measure.

Code-vs-math checks now live in tests/test_spatcoop_verification.py (including
the mean-field `well_mixed → (x≈0, e≈−1)` oracle).
"""

from __future__ import annotations

import numpy as np

from spatcoop.params import ModelParams, LINEAR
from spatcoop.model import run_episode


def check_weitz_oscillation(seed: int = 0) -> bool:
    """
    In the mean-field limit with η>0 and moderate β, cooperation should show
    non-monotone dynamics (oscillations). Returns True if the UC time-series
    reverses direction at least twice in the final half of the run.

    NOTE: this reversal count is a weak proxy — a noisy series clears it easily.
    Treat as a soft, illustrative check, not a quantitative target.
    """
    p = ModelParams(
        L=50,
        n_gens=500,
        measure_window=100,
        well_mixed=True,
        eta=0.3,
        p_max=0.4,
        beta=1.5,
        delta=0.04,
        gamma=0.04,
        g=0.0,
        kappa=0.0,
        mu=0.005,
        initial_mix="equal",
        risk_mode=LINEAR,
    )
    r = run_episode(p, seed=seed)
    ts = r.timeseries["n_UC"]
    half = len(ts) // 2
    ts_late = ts[half:]
    # Count direction changes as a proxy for oscillation
    diff = np.diff(ts_late.astype(np.float32))
    signs = np.sign(diff[diff != 0])
    n_reversals = int(np.sum(signs[1:] != signs[:-1]))
    return n_reversals >= 2
