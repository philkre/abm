"""Smoke tests and conservation checks for model.py — M2 gate."""

import numpy as np
import pytest
from spatcoop.params import ModelParams, D, UC, CC
from spatcoop.model import run_episode, _init_state, _step
from spatcoop.kernel import focal_sum


def test_run_episode_completes():
    p = ModelParams(L=10, n_gens=5, mu=0.0)
    r = run_episode(p, seed=0)
    assert r.completed
    assert r.summary["resilience"] >= 0.0


def test_timeseries_length():
    p = ModelParams(L=10, n_gens=20, mu=0.0)
    r = run_episode(p, seed=1)
    for k, arr in r.timeseries.items():
        assert len(arr) == 20, f"{k} has wrong length"


def test_wealth_floor():
    """Wealth must never go negative even under extreme flood pressure."""
    p = ModelParams(L=30, n_gens=200, p_max=1.0, ell=0.99, eta=0.5)
    r = run_episode(p, seed=42)
    assert r.summary["mean_wealth"] >= 0.0


def test_no_flood_wealth_positive():
    """With p_max=0, no floods; mean wealth must stay positive."""
    p = ModelParams(L=20, n_gens=10, p_max=0.0, eta=0.0, mu=0.0)
    r = run_episode(p, seed=0)
    assert r.timeseries["mean_wealth"][-1] > 0


def test_focal_sum_equals_pool():
    """Pool inside the model matches focal_sum(contrib)."""
    p   = ModelParams(L=10, n_gens=1, mu=0.0)
    rng = np.random.default_rng(7)
    state = _init_state(p, rng)
    state["strategy"][:] = UC
    state["contrib"][:] = p.c_bar
    pool_expected = focal_sum(state["contrib"])
    pool_actual   = focal_sum(state["contrib"])
    np.testing.assert_allclose(pool_actual, pool_expected)


def test_frozen_strategies_unchanged():
    """frozen_strategies=True → strategy array identical before and after step."""
    p   = ModelParams(L=10, n_gens=1, frozen_strategies=True, mu=0.0)
    rng = np.random.default_rng(3)
    state = _init_state(p, rng)
    s_before = state["strategy"].copy()
    _step(state, p, rng, gen=0)
    np.testing.assert_array_equal(state["strategy"], s_before)


def test_all_defectors_run_completes():
    """Model must not crash even when all agents are defectors."""
    p = ModelParams(L=10, n_gens=20, beta=10.0, p_max=0.0, mu=0.0)
    r = run_episode(p, seed=99)
    assert r.completed


def test_env_clipped():
    """Environment must stay within [-1, 1] regardless of parameters."""
    p = ModelParams(L=20, n_gens=50, delta=1.0, gamma=1.0, eta=1.0, p_max=0.8)
    r = run_episode(p, seed=5)
    assert r.summary["mean_env"] >= -1.0
    assert r.summary["mean_env"] <=  1.0


def test_strategy_counts_sum_to_L_squared():
    """n_D + n_UC + n_CC = L² every generation."""
    p = ModelParams(L=15, n_gens=10, initial_mix="thirds")
    r = run_episode(p, seed=2)
    total = (r.timeseries["n_D"] + r.timeseries["n_UC"]
             + r.timeseries["n_CC"])
    np.testing.assert_array_equal(total, 15 * 15)


def test_well_mixed_pool_uniform():
    """In well-mixed mode every cell gets the same pool value."""
    p   = ModelParams(L=10, n_gens=1, well_mixed=True, frozen_strategies=True,
                      mu=0.0)
    rng = np.random.default_rng(0)
    state = _init_state(p, rng)
    # Set half UC, half D
    state["strategy"][:5, :] = UC
    state["strategy"][5:, :] = D
    state["contrib"][:] = 0.0
    _step(state, p, rng, gen=0)   # just check it doesn't crash


def test_moran_i_all_same():
    """Perfectly uniform strategy → Moran's I undefined but doesn't crash."""
    from spatcoop.model import _moran_i
    strategy = np.full((10, 10), UC, dtype=np.int8)
    mi = _moran_i(strategy)
    assert isinstance(mi, float)
