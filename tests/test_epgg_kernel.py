"""Sanity tests for the Ding (2024) EPGG kernel.

Pins the load-bearing invariants before the expensive sweep:
  - closed neighborhood = self + 4 von Neumann (5 nodes), periodic
  - n_C + n_D == 5 everywhere
  - EHI update clips to [-1, 1] and is signed by delta/gamma
  - degenerate environment (EHI=0) => defectors strictly dominate
"""

from __future__ import annotations

import numpy as np

from epgg.kernel import (
    benefit_field,
    cooperator_counts,
    closed_sum,
    fermi_sweep,
    update_ehi,
)
from epgg.lattice import neighbor_indices

# ── closed_sum: 5-node closed neighborhood, periodic ────────────────────────


def test_closed_sum_uniform_field_is_five():
    field = np.ones((6, 6))
    assert np.all(closed_sum(field) == 5.0)


def test_closed_sum_single_spike_hits_self_and_four_neighbors():
    field = np.zeros((5, 5))
    field[2, 2] = 1.0
    out = closed_sum(field)
    # self + N/S/E/W each receive the spike, nothing else.
    assert out[2, 2] == 1.0
    assert out[1, 2] == out[3, 2] == out[2, 1] == out[2, 3] == 1.0
    assert out.sum() == 5.0


def test_closed_sum_wraps_at_corner():
    field = np.zeros((4, 4))
    field[0, 0] = 1.0
    out = closed_sum(field)
    # neighbors of (0,0) wrap to (3,0),(1,0),(0,3),(0,1)
    assert out[0, 0] == 1.0
    assert out[3, 0] == out[1, 0] == out[0, 3] == out[0, 1] == 1.0


# ── cooperator/defector counts sum to 5 ─────────────────────────────────────


def test_counts_sum_to_five_everywhere():
    rng = np.random.default_rng(0)
    strategy = rng.integers(0, 2, size=(10, 10)).astype(np.int8)
    n_C, n_D = cooperator_counts(strategy)
    assert np.all(n_C + n_D == 5)


def test_all_cooperators_count_is_five():
    strategy = np.ones((5, 5), dtype=np.int8)
    n_C, n_D = cooperator_counts(strategy)
    assert np.all(n_C == 5)
    assert np.all(n_D == 0)


# ── EHI update: clip + sign ─────────────────────────────────────────────────


def test_ehi_unchanged_when_delta_and_gamma_zero():
    ehi = np.full((5, 5), 0.3)
    strategy = np.ones((5, 5), dtype=np.int8)
    out = update_ehi(ehi, strategy, delta=0.0, gamma=0.0)
    assert np.allclose(out, 0.3)


def test_ehi_rises_with_cooperators_and_clips_at_one():
    ehi = np.zeros((5, 5))
    strategy = np.ones((5, 5), dtype=np.int8)  # n_C = 5 everywhere
    out = update_ehi(ehi, strategy, delta=0.1, gamma=0.04)
    assert np.allclose(out, 0.5)  # 0 + 5*0.1 - 0
    out2 = update_ehi(np.full((5, 5), 0.9), strategy, delta=0.1, gamma=0.04)
    assert np.all(out2 == 1.0)  # clipped


def test_ehi_falls_with_defectors_and_clips_at_minus_one():
    ehi = np.zeros((5, 5))
    strategy = np.zeros((5, 5), dtype=np.int8)  # n_D = 5 everywhere
    out = update_ehi(ehi, strategy, delta=0.1, gamma=0.04)
    assert np.allclose(out, -0.2)  # 0 - 5*0.04
    out2 = update_ehi(np.full((5, 5), -0.9), strategy, delta=0.1, gamma=0.5)
    assert np.all(out2 == -1.0)  # clipped


# ── benefit_field = r * closed EHI sum ──────────────────────────────────────


def test_benefit_field_scales_closed_sum_by_r():
    ehi = np.full((5, 5), 0.5)
    out = benefit_field(ehi, r=4.0)
    assert np.allclose(out, 4.0 * 2.5)  # 5 nodes * 0.5 * r


# ── neighbor index array ────────────────────────────────────────────────────


def test_neighbor_indices_shape_and_wrap():
    nbr = neighbor_indices(4)
    assert nbr.shape == (16, 4)
    # node 0 = (0,0): up/down/left/right flattened, periodic
    assert set(nbr[0].tolist()) == {12, 4, 3, 1}


# ── Fermi sweep: degenerate environment => defectors dominate ───────────────


def test_fermi_sweep_defectors_dominate_when_environment_dead():
    # EHI = 0 everywhere => benefit = 0; cooperators pay 5c, defectors pay 0.
    L = 20
    rng = np.random.default_rng(1)
    strategy = rng.integers(0, 2, size=L * L).astype(np.int8)
    benefit = np.zeros(L * L)
    nbr = neighbor_indices(L)
    frac0 = strategy.mean()
    for g in range(50):
        fermi_sweep(strategy, benefit, nbr, c=1.0, K=0.5, seed=g)
    assert strategy.mean() < frac0
    assert strategy.mean() < 0.05  # cooperators wiped out


def test_fermi_sweep_leaves_homogeneous_state_frozen():
    L = 10
    strategy = np.ones(L * L, dtype=np.int8)  # all cooperators
    benefit = np.zeros(L * L)
    nbr = neighbor_indices(L)
    fermi_sweep(strategy, benefit, nbr, c=1.0, K=0.5, seed=0)
    assert np.all(strategy == 1)  # no disagreement => no flips
