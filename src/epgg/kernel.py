"""Core EPGG kernels (Ding 2024): closed-neighborhood ops + Fermi sweep.

Two neighborhoods, never conflated:
  - closed = self + 4 von Neumann (5 nodes): payoff sum and EHI feedback.
  - open   = 4 von Neumann: Fermi imitation target only (see lattice.py).

The per-generation vectorized ops (closed_sum, counts, EHI update, benefit) run
in numpy; the inherently sequential Fermi sweep runs under @njit. EHI is frozen
during a generation, so the benefit term r·Σ_closed e is precomputed once and
reused across the L² Fermi steps — only the cost term flips with the strategy.
"""

from __future__ import annotations

import numpy as np
from numba import njit


def closed_sum(field: np.ndarray) -> np.ndarray:
    """Sum of `field` over each node's closed neighborhood (self + 4), periodic."""
    return (
        field
        + np.roll(field, 1, axis=0)
        + np.roll(field, -1, axis=0)
        + np.roll(field, 1, axis=1)
        + np.roll(field, -1, axis=1)
    )


def cooperator_counts(strategy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(n_C, n_D) per node over the closed neighborhood; n_C + n_D == 5."""
    n_C = closed_sum(strategy.astype(np.int64))
    n_D = 5 - n_C
    return n_C, n_D


def update_ehi(
    ehi: np.ndarray, strategy: np.ndarray, delta: float, gamma: float
) -> np.ndarray:
    """One per-generation EHI step (Eq. 2), clipped once to [-1, 1].

    e ← clip(e + δ·n_C − γ·n_D, −1, 1), counts over the closed neighborhood.
    """
    n_C, n_D = cooperator_counts(strategy)
    return np.clip(ehi + delta * n_C - gamma * n_D, -1.0, 1.0)


def benefit_field(ehi: np.ndarray, r: float) -> np.ndarray:
    """Environmental benefit r·Σ_closed e per node (the cost-free payoff part)."""
    return r * closed_sum(ehi)


@njit(cache=True)
def fermi_sweep(
    strategy: np.ndarray,
    benefit: np.ndarray,
    neighbors: np.ndarray,
    c: float,
    K: float,
    seed: int,
) -> None:
    """One generation = L² random sequential Fermi updates, in place.

    Args (all flattened, row-major):
        strategy: int8[N] in {0=D, 1=C}; mutated in place.
        benefit:  float64[N] = r·Σ_closed e, frozen for the generation.
        neighbors: int32[N, 4] open-neighborhood indices.
        c: per-game cooperation cost (flat cost 5c per cooperator).
        K: Fermi noise.
        seed: seeds numba's RNG for reproducibility.

    Payoff π = benefit − 5c·[s=C]. Node x copies a random open neighbor y with
    probability 1/(1+exp((π_x − π_y)/K)). Reads see prior within-generation
    updates (sequential), as in the paper.
    """
    np.random.seed(seed)
    N = strategy.shape[0]
    cost = 5.0 * c
    for _ in range(N):
        x = np.random.randint(0, N)
        y = neighbors[x, np.random.randint(0, 4)]
        pi_x = benefit[x] - cost * strategy[x]
        pi_y = benefit[y] - cost * strategy[y]
        w = 1.0 / (1.0 + np.exp((pi_x - pi_y) / K))
        if np.random.random() < w:
            strategy[x] = strategy[y]
