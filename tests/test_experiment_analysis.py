"""Tests for the LCP classifier (experiment.analysis)."""

from __future__ import annotations

import numpy as np
import pytest

from experiment.analysis import (
    classify_lcp,
    classify_session,
    fit_lcp,
    type_distribution,
)

E = 20.0  # endowment → 50% line at 10


# ── fit_lcp ──────────────────────────────────────────────────────────────────


def test_fit_recovers_known_line():
    x = np.array([0.0, 5.0, 10.0, 15.0, 20.0])
    y = 3.0 + 0.5 * x
    alpha, beta = fit_lcp(y, x)
    assert alpha == pytest.approx(3.0, abs=1e-9)
    assert beta == pytest.approx(0.5, abs=1e-9)


def test_fit_zero_variance_regressor():
    x = np.array([7.0, 7.0, 7.0])
    y = np.array([4.0, 6.0, 8.0])
    alpha, beta = fit_lcp(y, x)
    assert beta == 0.0
    assert alpha == pytest.approx(6.0)  # mean(y)


def test_fit_empty():
    assert fit_lcp(np.array([]), np.array([])) == (0.0, 0.0)


# ── classify_lcp (Fig 6 rules) ───────────────────────────────────────────────


def test_classify_uc_line_above_half():
    # Paper empirical UC: alpha≈17.6, beta≈-0.027 → stays above 10 over [0,20]
    assert classify_lcp(17.6, -0.027, E) == "UC"


def test_classify_fr_line_below_half():
    # Paper empirical FR: alpha≈4.1, beta≈0.134 → 4.1..6.8, entirely below 10
    assert classify_lcp(4.1, 0.134, E) == "FR"


def test_classify_cc_positive_slope_crossing():
    # Paper empirical CC: alpha≈0.82, beta≈0.865 → 0.82..18.1, crosses 10
    assert classify_lcp(0.82, 0.865, E) == "CC"


def test_classify_uncategorized_negative_slope_crossing():
    # Crosses 10 but with negative slope → not CC
    assert classify_lcp(18.0, -0.6, E) == "Uncategorized"


def test_classify_boundary_flat_at_half_is_fr():
    # Flat line exactly on the 10 line counts as below (hi <= half)
    assert classify_lcp(10.0, 0.0, E) == "FR"


# ── classify_session / type_distribution ─────────────────────────────────────


def test_classify_session_short_record_uncategorized():
    # Single round → no regression possible
    labels = classify_session([[5.0, 5.0, 5.0, 5.0]], E)
    assert labels == ["Uncategorized"] * 4


def test_classify_session_constant_high_is_uc():
    # An agent always at 20 while others vary → flat line at 20 → UC
    rng = np.random.default_rng(0)
    rounds = 30
    record = []
    for _ in range(rounds):
        others = rng.uniform(0, 20, size=3).tolist()
        record.append([20.0, *others])
    labels = classify_session(record, E)
    assert labels[0] == "UC"


def test_type_distribution_sums_to_one():
    rng = np.random.default_rng(1)
    sessions = [
        [[rng.uniform(0, 20) for _ in range(4)] for _ in range(20)] for _ in range(5)
    ]
    dist = type_distribution(sessions, E)
    assert set(dist) == {"UC", "CC", "FR", "Uncategorized"}
    assert sum(dist.values()) == pytest.approx(1.0)


def test_type_distribution_empty():
    dist = type_distribution([], E)
    assert dist == {"UC": 0.0, "CC": 0.0, "FR": 0.0, "Uncategorized": 0.0}
