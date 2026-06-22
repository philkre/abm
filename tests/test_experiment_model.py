"""Tests for ExperimentModel phases, the blend rule, and CLI defaults."""

from __future__ import annotations

import random

import numpy as np
import pytest

from experiment.config import (
    DEFAULT_AGENT_CONFIG,
    AgentConfig,
    TREATMENTS,
)
from experiment.model import ExperimentModel
from experiment.run import _build_parser

CONTROL = TREATMENTS["Control"]
P40 = TREATMENTS["40P"]


# Deterministic agent config: no noise, degenerate trait draws.
def _fixed_cfg(g=12.0, m=0.6, **kw) -> AgentConfig:
    return AgentConfig(
        g_lo=g,
        g_hi=g,
        m_lo=m,
        m_hi=m,
        noise_sd=0.0,
        **kw,
    )


# ── CLI defaults must match DEFAULT_AGENT_CONFIG ────────────────────────────


def test_cli_defaults_match_default_agent_config():
    args = _build_parser().parse_args([])
    d = DEFAULT_AGENT_CONFIG
    assert args.g_lo == d.g_lo
    assert args.g_hi == d.g_hi
    assert args.m_lo == d.m_lo
    assert args.m_hi == d.m_hi
    assert args.bias == d.bias
    assert args.anchor_margin == d.anchor_margin
    assert args.theta_init == d.theta_init
    assert args.theta_bump == d.theta_bump
    assert args.theta_decay == d.theta_decay
    assert args.noise_sd == d.noise_sd


# ── DataCollector aligned with rounds as played ─────────────────────────────


def test_datacollector_matches_contrib_record():
    m = ExperimentModel(P40, DEFAULT_AGENT_CONFIG, seed=7)
    m.run()
    df = m.datacollector.get_model_vars_dataframe()
    assert len(df) == P40.n_rounds
    for i in range(P40.n_rounds):
        assert df["mean_contribution"].iloc[i] == pytest.approx(
            float(np.mean(m.contrib_record[i]))
        )


# ── Blend rule ───────────────────────────────────────────────────────────────


def test_control_round1_is_generosity():
    # Control: theta = 0 → round-1 contribution = g (no noise).
    m = ExperimentModel(CONTROL, _fixed_cfg(g=11.0), seed=0)
    assert all(a.contribution == 11.0 for a in m.agents)
    assert m.theta == 0.0


def test_update_blends_three_anchors():
    cfg = _fixed_cfg(g=12.0, m=0.5, bias=0.5, anchor_margin=1.0)
    m = ExperimentModel(P40, cfg, seed=0)
    a = list(m.agents)[0]
    a.s = 0.5
    a.update(others_mean=10.0, theta=0.8)
    # w = 0.4; share = 60/4 = 15; social = 0.5·10 + 0.5·12 − 0.5 = 10.5
    # c = 0.4·15 + 0.6·10.5 = 12.3 → rounded to 12
    assert a.contribution == 12.0


def test_update_zero_theta_is_pure_social():
    cfg = _fixed_cfg(g=8.0, m=1.0, bias=1.0)
    m = ExperimentModel(CONTROL, cfg, seed=0)
    a = list(m.agents)[0]
    a.update(others_mean=10.0, theta=0.0)
    # pure matching minus bias: 10 − 1 = 9
    assert a.contribution == 9.0


def test_update_full_threat_anchors_at_share():
    cfg = _fixed_cfg(g=0.0, m=1.0, bias=0.0, anchor_margin=1.0)
    m = ExperimentModel(P40, cfg, seed=0)
    a = list(m.agents)[0]
    a.s = 1.0
    a.update(others_mean=0.0, theta=1.0)
    assert a.contribution == 15.0  # w=1 → share = 60/4


def test_update_clips_to_endowment_range():
    cfg = _fixed_cfg(g=25.0, m=0.0, bias=0.0)  # g above endowment
    m = ExperimentModel(CONTROL, cfg, seed=0)
    a = list(m.agents)[0]
    a.update(others_mean=0.0, theta=0.0)
    assert a.contribution == CONTROL.endowment
    a2 = list(m.agents)[1]
    a2.g = -10.0
    a2.update(others_mean=0.0, theta=0.0)
    assert a2.contribution == 0.0


def test_contributions_are_whole_units():
    m = ExperimentModel(P40, DEFAULT_AGENT_CONFIG, seed=3)
    m.run()
    for row in m.contrib_record:
        for c in row:
            assert c == int(c)
            assert 0.0 <= c <= P40.endowment


def test_level_share_uses_worst_case_threshold():
    cfg = _fixed_cfg(anchor_margin=1.0)
    m = ExperimentModel(TREATMENTS["Level"], cfg, seed=0)
    a = list(m.agents)[0]
    assert a._share == pytest.approx(70.0 / 4.0)


# ── Theta dynamics (Fig 5: one-round lag) ────────────────────────────────────


def test_theta_zero_without_risk():
    m = ExperimentModel(CONTROL, DEFAULT_AGENT_CONFIG, seed=0)
    m.run()
    assert m.theta == 0.0


def test_theta_bump_lands_one_round_late():
    cfg = _fixed_cfg(theta_init=0.5, theta_bump=0.2, theta_decay=0.0)
    m = ExperimentModel(P40, cfg, seed=0)
    theta0 = m.theta
    m._learning_phase(pool=10.0, disaster=True)
    # Bump is only queued: theta unchanged this round.
    assert m.theta == pytest.approx(theta0)
    m._learning_phase(pool=10.0, disaster=False)
    # Now it lands.
    assert m.theta == pytest.approx(theta0 + 0.2)


def test_theta_capped_at_one():
    cfg = _fixed_cfg(theta_init=0.95, theta_bump=0.5, theta_decay=0.0)
    m = ExperimentModel(P40, cfg, seed=0)
    m._learning_phase(pool=10.0, disaster=True)
    m._learning_phase(pool=10.0, disaster=False)
    assert m.theta == 1.0


# ── Payoff phase / accounts ──────────────────────────────────────────────────


def test_payoff_phase_safe_round_accounting():
    m = ExperimentModel(CONTROL, _fixed_cfg(), seed=0)
    agents = list(m.agents)
    for a, c in zip(agents, [5.0, 10.0, 15.0, 20.0]):
        a.contribution = c
    pool = 50.0
    m._payoff_phase(pool, disaster=False)

    share = CONTROL.multiplier * pool / CONTROL.group_size  # 1.6*50/4 = 20
    assert m.group_account == pytest.approx(CONTROL.multiplier * pool)
    for a, c in zip(agents, [5.0, 10.0, 15.0, 20.0]):
        assert a.payoff == pytest.approx((CONTROL.endowment - c) + share)
        assert a.indiv_account == pytest.approx(CONTROL.endowment - c)


def test_payoff_phase_disaster_wipes_both():
    m = ExperimentModel(P40, _fixed_cfg(), seed=0)
    for a in m.agents:
        a.indiv_account = 50.0
    m.group_account = 100.0
    m._payoff_phase(40.0, disaster=True)

    assert m.group_account == 0.0
    for a in m.agents:
        assert a.indiv_account == 0.0
        assert a.wealth == 0.0
        assert a.disaster is True
        assert a.payoff == 0.0


def test_impact_individual_scope_spares_group_account(monkeypatch):
    m = ExperimentModel(TREATMENTS["Impact"], _fixed_cfg(), seed=0)
    monkeypatch.setattr(m, "_disaster_scope", lambda: "individual")
    for a in m.agents:
        a.indiv_account = 50.0
    m.group_account = 100.0
    m._payoff_phase(40.0, disaster=True)
    assert m.group_account == pytest.approx(100.0 + 1.6 * 40.0)
    assert all(a.indiv_account == 0.0 for a in m.agents)


def test_impact_group_scope_spares_individual_accounts(monkeypatch):
    m = ExperimentModel(TREATMENTS["Impact"], _fixed_cfg(), seed=0)
    monkeypatch.setattr(m, "_disaster_scope", lambda: "group")
    agents = list(m.agents)
    for a in agents:
        a.indiv_account = 50.0
        a.contribution = 10.0
    m.group_account = 100.0
    m._payoff_phase(40.0, disaster=True)
    assert m.group_account == 0.0
    assert all(a.indiv_account == pytest.approx(60.0) for a in agents)


def test_impact_scope_distribution():
    m = ExperimentModel(TREATMENTS["Impact"], _fixed_cfg(), seed=0)
    scopes = {m._disaster_scope() for _ in range(300)}
    assert scopes == {"individual", "group", "both"}


def test_non_impact_scope_always_both():
    m = ExperimentModel(P40, _fixed_cfg(), seed=0)
    assert all(m._disaster_scope() == "both" for _ in range(50))


# ── Level threshold is an integer in [50, 70] ───────────────────────────────


def test_level_threshold_integer_inclusive_range():
    level = TREATMENTS["Level"]
    rng = random.Random(0)
    draws = [level.sample_threshold(rng) for _ in range(2000)]
    assert all(float(v).is_integer() for v in draws)
    assert min(draws) == 50.0
    assert max(draws) == 70.0


def test_fixed_threshold_unchanged():
    rng = random.Random(0)
    assert P40.sample_threshold(rng) == 60.0


# ── End-to-end: disaster risk sustains cooperation ──────────────────────────


def test_40p_final_contribution_exceeds_control():
    def final_mean(treatment) -> float:
        finals = []
        for i in range(30):
            m = ExperimentModel(treatment, DEFAULT_AGENT_CONFIG, seed=100 + i)
            m.run()
            finals.append(float(np.mean(m.contrib_record[-1])))
        return float(np.mean(finals))

    assert final_mean(P40) > final_mean(CONTROL) + 2.0


def test_control_contributions_decline():
    r1s, rNs = [], []
    for i in range(50):
        m = ExperimentModel(CONTROL, DEFAULT_AGENT_CONFIG, seed=i)
        m.run()
        r1s.append(float(np.mean(m.contrib_record[0])))
        rNs.append(float(np.mean(m.contrib_record[-1])))
    assert np.mean(rNs) < np.mean(r1s) - 0.5
