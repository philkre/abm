"""Smoke tests for the Fig 4 disaster-probability sweep."""

from __future__ import annotations

import numpy as np

from experiment.config import TreatmentConfig
from experiment.figures import disaster_prob_sweep


def test_sweep_returns_all_probs_with_trend_length():
    probs = (0.0, 0.4, 1.0)
    res = disaster_prob_sweep(probs=probs, n_sessions=20, base_seed=0)
    assert set(res) == set(probs)
    n_rounds = TreatmentConfig("x", disaster_prob=0.0).n_rounds
    for p in probs:
        assert res[p].trend.shape == (n_rounds,)
        assert 0.0 <= res[p].grand_mean <= 20.0
        assert res[p].ci95 >= 0.0


def test_contribution_increases_with_disaster_prob():
    res = disaster_prob_sweep(probs=(0.0, 0.4, 1.0), n_sessions=40, base_seed=0)
    # Disaster risk should not lower mean contribution: 0% < 40% <= 100%.
    assert res[0.0].grand_mean < res[0.4].grand_mean
    assert res[0.4].grand_mean <= res[1.0].grand_mean + 1e-6


def test_control_has_no_checks():
    res = disaster_prob_sweep(probs=(0.0,), n_sessions=10, base_seed=0)
    assert np.isnan(res[0.0].pass_rate)
