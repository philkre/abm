"""Tests for ExperimentModel phases, HouseholdAgent.update, and CLI defaults."""

from __future__ import annotations

import random

import numpy as np
import pytest

from experiment.config import (
    DEFAULT_AGENT_CONFIG,
    AgentConfig,
    TreatmentConfig,
    TREATMENTS,
)
from experiment.model import ExperimentModel
from experiment.run import _build_parser

CONTROL = TREATMENTS["Control"]
P40 = TREATMENTS["40P"]

# Deterministic agent config: fixed aspiration (lo == hi), no penalty surprises.
FIXED_CFG = AgentConfig(
    contrib_init=12.0,
    aspiration_lo=25.0,
    aspiration_hi=25.0,
    aspiration_alpha=0.0,
    contrib_delta=1.0,
    delta_up=6.0,
    disaster_penalty=20.0,
)


# ── BUG 1: CLI defaults must match DEFAULT_AGENT_CONFIG ─────────────────────


def test_cli_defaults_match_default_agent_config():
    args = _build_parser().parse_args([])
    d = DEFAULT_AGENT_CONFIG
    assert args.contrib_init == d.contrib_init
    assert args.aspiration_lo == d.aspiration_lo
    assert args.aspiration_hi == d.aspiration_hi
    assert args.aspiration_alpha == d.aspiration_alpha
    assert args.contrib_delta == d.contrib_delta
    assert args.delta_up == d.delta_up
    assert args.disaster_penalty == d.disaster_penalty


# ── BUG 2: DataCollector aligned with rounds as played ──────────────────────


def test_datacollector_matches_contrib_record():
    m = ExperimentModel(P40, FIXED_CFG, seed=7)
    m.run()
    df = m.datacollector.get_model_vars_dataframe()
    assert len(df) == P40.n_rounds
    # Every collected row must equal the contribution actually played.
    for i in range(P40.n_rounds):
        assert df["mean_contribution"].iloc[i] == pytest.approx(
            float(np.mean(m.contrib_record[i]))
        )


# ── HouseholdAgent.update branches ───────────────────────────────────────────


def _lone_agent(cfg: AgentConfig = FIXED_CFG):
    model = ExperimentModel(CONTROL, cfg, seed=0)
    return list(model.agents)[0]


def test_update_disaster_jumps_by_delta_up():
    a = _lone_agent()
    a.contribution, a.disaster = 10.0, True
    a.update()
    assert a.contribution == 16.0


def test_update_disaster_clamps_at_endowment():
    a = _lone_agent()
    a.contribution, a.disaster = 18.0, True
    a.update()
    assert a.contribution == CONTROL.endowment


def test_update_satisfied_decreases():
    a = _lone_agent()
    a.contribution, a.disaster = 10.0, False
    a.payoff, a.aspiration = 30.0, 25.0  # payoff >= aspiration
    a.update()
    assert a.contribution == 9.0


def test_update_unsatisfied_increases():
    a = _lone_agent()
    a.contribution, a.disaster = 10.0, False
    a.payoff, a.aspiration = 10.0, 25.0  # payoff < aspiration
    a.update()
    assert a.contribution == 11.0


def test_update_decrease_clamps_at_zero():
    a = _lone_agent()
    a.contribution, a.disaster = 0.5, False
    a.payoff, a.aspiration = 30.0, 25.0
    a.update()
    assert a.contribution == 0.0


def test_update_aspiration_moving_average():
    cfg = AgentConfig(aspiration_lo=25.0, aspiration_hi=25.0, aspiration_alpha=0.5)
    a = _lone_agent(cfg)
    a.payoff, a.disaster = 15.0, False
    a.update()
    assert a.aspiration == pytest.approx(0.5 * 25.0 + 0.5 * 15.0)


# ── Payoff phase ─────────────────────────────────────────────────────────────


def test_payoff_phase_safe_round_accounting():
    m = ExperimentModel(CONTROL, FIXED_CFG, seed=0)
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
        assert a.wealth == pytest.approx(
            (CONTROL.endowment - c) + CONTROL.multiplier * pool / 4
        )


def test_payoff_phase_disaster_wipes_both_and_sets_penalty():
    m = ExperimentModel(P40, FIXED_CFG, seed=0)
    for a in m.agents:
        a.indiv_account = 50.0
    m.group_account = 100.0
    m._payoff_phase(40.0, disaster=True)

    assert m.group_account == 0.0
    for a in m.agents:
        assert a.indiv_account == 0.0
        assert a.wealth == 0.0
        assert a.disaster is True
        assert a.payoff == -FIXED_CFG.disaster_penalty


# ── BUG 4: Impact wipes individual/group/both with prob 1/3 each ────────────


def _impact_model() -> ExperimentModel:
    return ExperimentModel(TREATMENTS["Impact"], FIXED_CFG, seed=0)


def test_impact_individual_scope_spares_group_account(monkeypatch):
    m = _impact_model()
    monkeypatch.setattr(m, "_disaster_scope", lambda: "individual")
    for a in m.agents:
        a.indiv_account = 50.0
    m.group_account = 100.0
    m._payoff_phase(40.0, disaster=True)
    # This round's pot still credited, group account survives.
    assert m.group_account == pytest.approx(100.0 + 1.6 * 40.0)
    assert all(a.indiv_account == 0.0 for a in m.agents)


def test_impact_group_scope_spares_individual_accounts(monkeypatch):
    m = _impact_model()
    monkeypatch.setattr(m, "_disaster_scope", lambda: "group")
    agents = list(m.agents)
    for a in agents:
        a.indiv_account = 50.0
        a.contribution = 10.0
    m.group_account = 100.0
    m._payoff_phase(40.0, disaster=True)
    assert m.group_account == 0.0
    # Individual accounts keep prior balance + this round's kept endowment.
    assert all(a.indiv_account == pytest.approx(60.0) for a in agents)


def test_impact_scope_distribution():
    m = _impact_model()
    scopes = {m._disaster_scope() for _ in range(300)}
    assert scopes == {"individual", "group", "both"}


def test_non_impact_scope_always_both():
    m = ExperimentModel(P40, FIXED_CFG, seed=0)
    assert all(m._disaster_scope() == "both" for _ in range(50))


# ── BUG 5: Level threshold is an integer in [50, 70] ────────────────────────


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
