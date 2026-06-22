"""Tests for the EPGG generation loop, stationarity detection, and sweep.

Machinery correctness only — the scientific phase reproduction (Fig 2) is the
separate validation gate at full L.
"""

from __future__ import annotations

import numpy as np

from epgg.model import RunResult, mean_converged, run_to_stationarity
from epgg.sweep import coop_fraction_at, delta_sweep

# ── mean-stabilization detector ─────────────────────────────────────────────


def test_mean_converged_true_for_flat_series():
    series = [0.5] * 100
    assert mean_converged(series, window=20, tol=1e-3)


def test_mean_converged_false_while_drifting():
    series = list(np.linspace(0.0, 1.0, 100))  # steadily rising
    assert not mean_converged(series, window=20, tol=1e-3)


def test_mean_converged_false_when_too_short():
    series = [0.5] * 10
    assert not mean_converged(series, window=20, tol=1e-3)


def test_mean_converged_tolerates_cyclic_fluctuation():
    # Oscillating around a stable mean => converged under mean-stabilization,
    # even though the variance never decays (the C+D phase).
    t = np.arange(200)
    series = list(0.4 + 0.1 * np.sin(t))
    assert mean_converged(series, window=50, tol=1e-2)


# ── generation loop ─────────────────────────────────────────────────────────


def test_run_degenerate_environment_collapses_to_defection():
    # delta = gamma = 0 => EHI stays 0 => defectors strictly dominate.
    res = run_to_stationarity(L=40, delta=0.0, gamma=0.0, seed=0)
    assert isinstance(res, RunResult)
    assert res.coop_fraction < 0.05
    assert res.converged


def test_run_sustains_cooperation_above_dead_baseline():
    # EHI feedback keeps cooperation alive when delta > gamma, unlike the dead
    # environment (frac=0). Full C-phase magnitude needs L=200 — that is the
    # separate validation gate; here we only assert survival of the machinery.
    res = run_to_stationarity(
        L=60, delta=0.05, gamma=0.04, seed=1, window=120, min_gen=400, max_gen=800
    )
    assert res.coop_fraction > 0.2


def test_run_history_length_matches_generations():
    res = run_to_stationarity(L=30, delta=0.0, gamma=0.0, seed=0)
    assert len(res.history) == res.generations


# ── sweep / ensemble averaging ──────────────────────────────────────────────


def test_coop_fraction_at_returns_unit_interval_mean():
    frac = coop_fraction_at(
        delta=0.0, gamma=0.0, L=30, n_repeats=3, base_seed=0, min_gen=100
    )
    assert 0.0 <= frac <= 1.0
    assert frac < 0.05  # degenerate => defection


def test_delta_sweep_returns_one_fraction_per_delta():
    deltas = [0.0, 0.05]
    fracs = delta_sweep(
        deltas,
        gamma=0.04,
        L=60,
        n_repeats=2,
        base_seed=0,
        window=120,
        min_gen=400,
        max_gen=800,
    )
    assert fracs.shape == (2,)
    assert fracs[0] < fracs[1]  # D phase below coexistence
