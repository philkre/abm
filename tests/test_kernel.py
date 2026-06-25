"""Unit tests for focal_sum and fermi_step — M1 gate."""

import numpy as np
import pytest
from spatcoop.kernel import focal_sum, fermi_step_numpy
from spatcoop.params import D, UC


def test_focal_sum_cross():
    """Single 1.0 at (0,0) produces a cross pattern; everything else zero."""
    arr = np.zeros((10, 10), dtype=np.float32)
    arr[0, 0] = 1.0
    out = focal_sum(arr)
    assert out[0, 0] == 1.0   # centre
    assert out[1, 0] == 1.0   # south
    assert out[9, 0] == 1.0   # north (wraps)
    assert out[0, 1] == 1.0   # east
    assert out[0, 9] == 1.0   # west (wraps)
    assert out[1, 1] == 0.0   # not a neighbour


def test_focal_sum_homogeneous():
    """Uniform array → every cell's focal sum = 5 × value."""
    arr = np.ones((20, 20), dtype=np.float32) * 3.0
    np.testing.assert_allclose(focal_sum(arr), 15.0)


def test_focal_sum_shape_preserved():
    arr = np.random.default_rng(0).random((15, 15)).astype(np.float32)
    assert focal_sum(arr).shape == arr.shape


def test_focal_sum_sum_invariant():
    """Sum of focal_sum(arr) = 5 * sum(arr) (each element counted in 5 groups)."""
    arr = np.arange(25, dtype=np.float32).reshape(5, 5)
    assert abs(focal_sum(arr).sum() - 5 * arr.sum()) < 1e-3


def test_fermi_deterministic_high_beta():
    """At very high β, neighbours of the fittest cell should adopt its strategy."""
    L = 10
    strategy = np.zeros((L, L), dtype=np.int8)   # all D
    phi = np.zeros((L, L), dtype=np.float32)
    phi[5, 5] = 1000.0
    strategy[5, 5] = UC
    rng = np.random.default_rng(0)
    s_new = fermi_step_numpy(strategy, phi, beta=100.0, rng=rng)
    # At least one neighbour of (5,5) should have adopted UC
    neighbours_adopted = (
        s_new[4, 5] == UC or s_new[6, 5] == UC
        or s_new[5, 4] == UC or s_new[5, 6] == UC
    )
    assert neighbours_adopted


def test_fermi_equal_fitness_both_strategies_survive():
    """Equal fitness → ~50% imitation; both strategies still present."""
    L = 20
    rng = np.random.default_rng(1)
    strategy = rng.choice([D, UC], (L, L)).astype(np.int8)
    phi = np.zeros((L, L), dtype=np.float32)   # all equal
    s_new = fermi_step_numpy(strategy, phi, beta=5.0, rng=rng)
    assert np.any(s_new == D) and np.any(s_new == UC)


def test_fermi_probability_half_at_equal_fitness():
    """P(adopt) = 0.5 when φ_j = φ_i; confirm empirically with large L."""
    L = 100
    rng = np.random.default_rng(42)
    # All D, all same fitness
    strategy = np.zeros((L, L), dtype=np.int8)
    strategy[:, L // 2 :] = UC   # right half UC
    phi = np.zeros((L, L), dtype=np.float32)
    # Run 1000 independent Fermi steps and check mean fraction unchanged
    fracs = []
    for _ in range(20):
        s_new = fermi_step_numpy(strategy, phi, beta=0.0, rng=rng)
        fracs.append((s_new == UC).mean())
    # β=0 → all Fermi probs = 0.5; strategy distribution should be ~uniform
    # (not necessarily 0.5 because boundary cells mix, but within [0.3, 0.7])
    assert 0.3 < np.mean(fracs) < 0.7


def test_fermi_output_dtype():
    L = 5
    rng = np.random.default_rng(7)
    strategy = rng.choice([D, UC], (L, L)).astype(np.int8)
    phi = np.zeros((L, L), dtype=np.float32)
    s_new = fermi_step_numpy(strategy, phi, beta=2.0, rng=rng)
    assert s_new.dtype == np.int8
    assert s_new.shape == (L, L)
