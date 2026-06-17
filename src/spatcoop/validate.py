"""Validation targets: Jonsson well-mixed, Ding phase diagram, Weitz oscillation."""

from __future__ import annotations
from dataclasses import replace
import numpy as np
from spatcoop.params import ModelParams, LINEAR
from spatcoop.model import run_episode

# ── M3: Jonsson well-mixed qualitative check ──────────────────────────────────


def validate_jonsson(tol_coop: float = 0.5, seed: int = 0) -> bool:
    """
    Two runs — risk (p_max=0.5) vs no-risk (p_max=0.0) — in the well-mixed
    limit with frozen strategies and a productive multiplier (R=1.0).

    Returns True when:
      - risk run resilience  > tol_coop
      - no-risk run resilience < 0.3
    """
    base = ModelParams(
        L=50,
        n_gens=20,
        measure_window=5,
        well_mixed=True,
        frozen_strategies=True,
        initial_mix="thirds",
        R=1.0,
        g=0.0,  # flat income
        kappa=0.0,  # no fitness discounting
        mu=0.0,
        T=3.75,
    )
    risk = run_episode(replace(base, p_max=0.5), seed=seed)
    norisk = run_episode(replace(base, p_max=0.0), seed=seed)
    return risk.summary["resilience"] > tol_coop and norisk.summary["resilience"] < 0.3


# ── M4: Ding phase diagram parameters ────────────────────────────────────────

# At δ ≈ 0.021, γ = 0.04, L = 200, cooperation should dominate after ~2600 gens.
DING_BASE = dict(
    L=200,
    n_gens=3000,
    measure_window=200,
    eta=0.0,
    p_max=0.0,
    T=0.0,
    R=0.0,
    g=0.0,
    gamma=0.04,
    beta=2.0,
    mu=0.01,
    initial_mix="equal",  # UC/D only
    risk_mode=LINEAR,
)

DING_DELTA_SWEEP = np.linspace(0.005, 0.05, 20)


def validate_ding_c_phase(delta: float = 0.021, seed: int = 0, coop_threshold: float = 0.7) -> bool:
    """
    At the given δ in the pure Ding regime (no floods, no threshold),
    confirm that the UC fraction in the final window exceeds coop_threshold.
    Must run at L=200 — the C phase does not exist at smaller lattices.
    """
    p = ModelParams(**DING_BASE, delta=delta)
    r = run_episode(p, seed=seed)
    uc_frac = r.summary["n_UC"] / (p.L**2)
    return uc_frac > coop_threshold


# ── M7: Weitz oscillation (soft target) ──────────────────────────────────────


def check_weitz_oscillation(seed: int = 0) -> bool:
    """
    In the mean-field limit with η>0 and moderate β, cooperation should show
    non-monotone dynamics (oscillations). Returns True if the UC time-series
    has at least 2 local maxima in the final half of the run.
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
