"""Verification suite for spatcoop — does the code match the spec/math?

Distinct from validation (does it match reality, see validate.py). These tests
exercise internal invariants and analytic limits:

  A. mean-field oracle — well-mixed collapses to the (x≈0, e≈−1) tragedy
  B. conditional cooperator — local matching, one-round lag, clipping
  C. resilience-erosion — a flood degrades the defence stock (η term)
  D. threshold immunity + linear risk function
  E. run-wide invariants (counts, contribution/env/probability bounds)
  F. reproducibility (seed determinism) + numba kernel correctness
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from spatcoop.params import ModelParams, D, UC, CC, LINEAR
from spatcoop.model import _init_state, _step, _flood_prob, run_episode
from spatcoop._numba_kernels import _fermi_jit


def _state_with(
    p: ModelParams, strat, *, seed: int = 0, contrib=None, env=None, wealth=None
):
    """Build a model state with a forced strategy grid (and optional fields)."""
    rng = np.random.default_rng(seed)
    state = _init_state(p, rng)
    state["strategy"] = np.asarray(strat, dtype=np.int8)
    if contrib is not None:
        state["contrib"] = np.asarray(contrib, dtype=np.float32)
    if env is not None:
        state["env"] = np.asarray(env, dtype=np.float32)
    if wealth is not None:
        state["wealth"] = np.asarray(wealth, dtype=np.float32)
    return state, rng


# ── A. Mean-field oracle: well-mixed → tragedy (x≈0, e≈−1) ───────────────────


def test_wellmixed_collapses_to_tragedy():
    # Analytic prediction (multiplicative growth, shared benefit): the only
    # stable mean-field fixed point is all-defect in a depleted environment.
    p = ModelParams(
        L=50,
        n_gens=400,
        measure_window=100,
        well_mixed=True,
        initial_mix="equal",
        eta=0.0,
        mu=0.0,
        delta=0.03,
        gamma=0.03,
        p_max=0.5,
        risk_mode=LINEAR,
        wealth_mode="multiplicative",  # tragedy is the multiplicative prediction
    )
    r = run_episode(p, seed=0)
    uc_frac = r.summary["n_UC"] / (p.L**2)
    assert uc_frac < 0.1, f"well-mixed UC fraction {uc_frac:.3f} (expected ~0)"
    assert (
        r.summary["mean_env"] < -0.8
    ), f"mean_env {r.summary['mean_env']:.3f} (expected ~-1)"


# ── B. Conditional cooperator behaviour ──────────────────────────────────────


def _cc_params(L=5, **kw):
    kw.setdefault("lambda_mean", 1.0)  # default: no loss-aversion premium
    return ModelParams(
        L=L,
        frozen_strategies=True,
        mu=0.0,
        lambda_mode="homogeneous",
        **kw,
    )


def test_cc_matches_full_cooperation():
    p = _cc_params()
    strat = np.full((p.L, p.L), UC, dtype=np.int8)
    strat[2, 2] = CC
    state, rng = _state_with(p, strat, contrib=np.full((p.L, p.L), p.c_bar))
    _step(state, p, rng, 0)
    assert state["contrib"][2, 2] == pytest.approx(p.c_bar, abs=1e-6)


def test_cc_matches_full_defection():
    p = _cc_params()
    strat = np.full((p.L, p.L), D, dtype=np.int8)
    strat[2, 2] = CC
    state, rng = _state_with(p, strat, contrib=np.zeros((p.L, p.L)))
    _step(state, p, rng, 0)
    assert state["contrib"][2, 2] == pytest.approx(0.0, abs=1e-6)


def test_cc_matches_partial_neighbourhood_mean():
    p = _cc_params()
    strat = np.full((p.L, p.L), UC, dtype=np.int8)
    strat[2, 2] = CC
    prev = np.zeros((p.L, p.L), dtype=np.float32)
    prev[1, 2] = prev[3, 2] = p.c_bar  # N, S contributed c̄ last round
    # E (2,3), W (2,1) contributed 0  → local mean = c̄/2
    state, rng = _state_with(p, strat, contrib=prev)
    _step(state, p, rng, 0)
    assert state["contrib"][2, 2] == pytest.approx(p.c_bar / 2, abs=1e-6)


def test_cc_reads_lagged_contribution():
    # CC reacts to neighbours' PREVIOUS round, not the current one. prev_c starts
    # at 0, so round 1 a CC among UCs still contributes 0; round 2 it catches up.
    p = _cc_params()
    strat = np.full((p.L, p.L), UC, dtype=np.int8)
    strat[2, 2] = CC
    state, rng = _state_with(p, strat)  # contrib initialised to zeros
    _step(state, p, rng, 0)
    assert state["contrib"][2, 2] == pytest.approx(0.0, abs=1e-6)  # saw lagged zeros
    _step(state, p, rng, 1)
    assert state["contrib"][2, 2] == pytest.approx(p.c_bar, abs=1e-6)  # now saw c̄


def test_cc_contribution_clipped_to_cbar():
    # Large loss-aversion premium must not push CC above c̄.
    p = _cc_params(lambda_mean=10.0, p_max=1.0, ell=0.34)
    strat = np.full((p.L, p.L), UC, dtype=np.int8)
    strat[2, 2] = CC
    state, rng = _state_with(
        p,
        strat,
        contrib=np.full((p.L, p.L), p.c_bar),
        wealth=np.full((p.L, p.L), 100.0),  # inflate the premium
    )
    _step(state, p, rng, 0)
    assert state["contrib"][2, 2] == pytest.approx(p.c_bar, abs=1e-6)


# ── C. Resilience-erosion: a flood damages the defence stock (η) ──────────────


def test_flood_damages_environment():
    L = 20
    p0 = ModelParams(
        L=L,
        frozen_strategies=True,
        mu=0.0,
        delta=0.0,
        gamma=0.0,
        eta=0.0,
        p_max=1.0,
        risk_mode=LINEAR,
    )
    p_eta = replace(p0, eta=0.2)

    def env_after_one_gen(p, seed):
        strat = np.full((L, L), D, dtype=np.int8)  # all exposed (pool 0 < T)
        state, rng = _state_with(p, strat, seed=seed)
        _step(state, p, rng, 0)
        return state["env"]

    e_no_eta = env_after_one_gen(p0, seed=7)
    e_eta = env_after_one_gen(p_eta, seed=7)  # same seed → same flood pattern
    assert e_no_eta.mean() == pytest.approx(0.0, abs=1e-6)  # δ=γ=η=0 ⇒ env frozen
    assert e_eta.mean() < e_no_eta.mean()  # η>0 ⇒ floods erode defences


# ── D. Threshold immunity + linear risk ──────────────────────────────────────


def test_threshold_immunity():
    L = 10
    p = ModelParams(L=L, frozen_strategies=True, mu=0.0, p_max=1.0, risk_mode=LINEAR)
    strat = np.full((L, L), UC, dtype=np.int8)  # pool = 5·c̄ = T everywhere
    state, rng = _state_with(p, strat, env=np.full((L, L), -1.0))  # p_i = p_max = 1
    _, obs = _step(state, p, rng, 0)
    assert obs["flood_rate"] == 0.0  # meeting T ⇒ immune despite max risk
    assert obs["resilience"] == 1.0


def test_flood_prob_linear_endpoints():
    p = ModelParams(p_max=0.6, p_min=0.0, risk_mode=LINEAR)
    f = lambda e: float(_flood_prob(np.array([[e]], dtype=np.float32), p)[0, 0])
    assert f(-1.0) == pytest.approx(0.6)  # degraded ⇒ p_max
    assert f(1.0) == pytest.approx(0.0)  # pristine ⇒ 0
    assert f(0.0) == pytest.approx(0.3)  # midpoint ⇒ p_max/2


def test_flood_prob_clipped_to_unit_interval():
    p = ModelParams(p_max=2.0, p_min=0.0, risk_mode=LINEAR)  # p_max>1 forces clip
    val = float(_flood_prob(np.array([[-1.0]], dtype=np.float32), p)[0, 0])
    assert val == pytest.approx(1.0)


# ── E. Run-wide invariants ───────────────────────────────────────────────────


def test_three_strategy_counts_sum_to_area():
    p = ModelParams(L=30, n_gens=10, initial_mix="thirds")
    r = run_episode(p, seed=0)
    area = p.L**2
    for nD, nUC, nCC in zip(
        r.timeseries["n_D"], r.timeseries["n_UC"], r.timeseries["n_CC"]
    ):
        assert nD + nUC + nCC == area


def test_bounds_hold_every_generation():
    p = ModelParams(
        L=20,
        n_gens=30,
        initial_mix="thirds",
        eta=0.2,
        p_max=0.8,
        lambda_mode="uniform",
        lambda_max=4.0,
    )
    rng = np.random.default_rng(1)
    state = _init_state(p, rng)
    for gen in range(p.n_gens):
        _step(state, p, rng, gen)
        c, e = state["contrib"], state["env"]
        assert c.min() >= 0.0 and c.max() <= p.c_bar + 1e-6
        assert e.min() >= -1.0 - 1e-6 and e.max() <= 1.0 + 1e-6
        pi = _flood_prob(e, p)
        assert pi.min() >= 0.0 and pi.max() <= 1.0


# ── F. Reproducibility + numba kernel correctness ────────────────────────────


def test_seed_determinism():
    p = ModelParams(L=20, n_gens=30, initial_mix="thirds", eta=0.1)
    r1 = run_episode(p, seed=123)
    r2 = run_episode(p, seed=123)
    for k in r1.timeseries:
        assert np.array_equal(r1.timeseries[k], r2.timeseries[k])


def test_numba_kernel_matches_numpy_oracle():
    # _fermi_jit's own direction convention: d=0 N, 1 S, 2 E(j+1), 3 W(j-1).
    L = 15
    rng = np.random.default_rng(2)
    strategy = rng.integers(0, 2, (L, L)).astype(np.int8)
    phi = rng.standard_normal((L, L)).astype(np.float32)
    beta = 2.0
    rand_dir = rng.integers(0, 4, size=(L, L), dtype=np.uint8)
    rand_acc = rng.random((L, L), dtype=np.float32)

    out_numba = _fermi_jit(strategy, phi, beta, rand_dir, rand_acc)

    rolls_s = [
        np.roll(strategy, 1, 0),  # d=0 N
        np.roll(strategy, -1, 0),  # d=1 S
        np.roll(strategy, -1, 1),  # d=2 E (j+1)
        np.roll(strategy, 1, 1),  # d=3 W (j-1)
    ]
    rolls_p = [
        np.roll(phi, 1, 0),
        np.roll(phi, -1, 0),
        np.roll(phi, -1, 1),
        np.roll(phi, 1, 1),
    ]
    d = rand_dir.astype(np.intp)
    s_j = np.choose(d, rolls_s)
    phi_j = np.choose(d, rolls_p)
    fermi = 1.0 / (1.0 + np.exp(-beta * (phi_j - phi)))
    out_numpy = np.where(rand_acc < fermi, s_j, strategy).astype(np.int8)

    assert np.array_equal(out_numba, out_numpy)


# ── G. OU wealth model ───────────────────────────────────────────────────────


def test_ou_additive_income_drift():
    # OU: additive income b, no multiplicative growth. All-UC is immune (pool=T),
    # so no flood: w' = w0 + b − c̄.
    L = 6
    p = ModelParams(
        L=L,
        wealth_mode="ou",
        b=1.0,
        sigma=0.0,
        R=0.0,
        frozen_strategies=True,
        mu=0.0,
        w0=1.0,
    )
    strat = np.full((L, L), UC, dtype=np.int8)
    state, rng = _state_with(p, strat)
    _step(state, p, rng, 0)
    assert np.allclose(state["wealth"], p.w0 + p.b - p.c_bar)


def test_multiplicative_mode_preserved():
    # The legacy multiplicative update remains available behind the flag.
    L = 6
    p = ModelParams(
        L=L,
        wealth_mode="multiplicative",
        g=0.015,
        R=0.0,
        frozen_strategies=True,
        mu=0.0,
        w0=1.0,
    )
    strat = np.full((L, L), UC, dtype=np.int8)
    state, rng = _state_with(p, strat)
    _step(state, p, rng, 0)
    assert np.allclose(state["wealth"], (1.0 + p.g) * p.w0 - p.c_bar)


def test_ou_wealth_mean_reverts():
    # All-defector, frozen environment (δ=γ=η=0 ⇒ e≡0 ⇒ d=p_max/2): OU wealth
    # mean-reverts to b/(dℓ), the stationary mean of the process.
    L = 30
    p = ModelParams(
        L=L,
        wealth_mode="ou",
        b=1.0,
        sigma=0.0,
        delta=0.0,
        gamma=0.0,
        eta=0.0,
        p_max=0.5,
        ell=0.34,
        R=0.0,
        frozen_strategies=True,
        mu=0.0,
        w0=1.0,
    )
    rng = np.random.default_rng(3)
    state = _init_state(p, rng)
    state["strategy"] = np.full((L, L), D, dtype=np.int8)
    means = []
    for gen in range(400):
        _step(state, p, rng, gen)
        means.append(float(state["wealth"].mean()))
    d = p.p_max / 2.0
    target = p.b / (d * p.ell)  # ≈ 11.8
    final = float(np.mean(means[-200:]))
    assert 0.6 * target < final < 1.4 * target


def test_ou_wellmixed_collapses_but_slower_at_low_beta():
    # IMPORTANT: the OU wealth gap that would cancel the cooperation cost builds
    # too slowly (rate ~dℓ) to beat imitation (rate ~β·c̄), and fitness is a
    # discounted accumulation that locks in the early defector advantage. So the
    # neutral fixed point is dynamically unreachable: well-mixed OU still
    # collapses to tragedy at the default β. Slower imitation (low β) retains
    # more cooperation but does not rescue it — the timescale-race signature.
    base = dict(
        L=40,
        n_gens=400,
        measure_window=100,
        well_mixed=True,
        initial_mix="equal",
        mu=0.01,
        delta=0.03,
        gamma=0.03,
        p_max=0.5,
        eta=0.0,
        wealth_mode="ou",
        b=1.0,
    )
    hi = run_episode(ModelParams(**base, beta=2.0), seed=0)
    lo = run_episode(ModelParams(**base, beta=0.1), seed=0)
    uc_hi = hi.summary["n_UC"] / (40**2)
    uc_lo = lo.summary["n_UC"] / (40**2)
    assert uc_hi < 0.1  # default-β OU collapses (no neutral rescue)
    assert uc_lo > uc_hi  # slower imitation retains more (timescale race)
