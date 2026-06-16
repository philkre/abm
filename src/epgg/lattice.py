"""Lattice topology: precomputed neighbor indices for the hot loop."""

from __future__ import annotations

import numpy as np


def neighbor_indices(L: int) -> np.ndarray:
    """Open (von Neumann) neighbors of every node on a periodic L×L lattice.

    Returns an int32 array of shape (L*L, 4): row x holds the flattened indices
    of x's up/down/left/right neighbors (row-major, toroidal wrap). Used ONLY to
    pick the Fermi imitation target — distinct from the closed neighborhood used
    for payoffs and the EHI feedback.
    """
    idx = np.arange(L * L).reshape(L, L)
    up = np.roll(idx, 1, axis=0)
    down = np.roll(idx, -1, axis=0)
    left = np.roll(idx, 1, axis=1)
    right = np.roll(idx, -1, axis=1)
    nbr = np.stack([up.ravel(), down.ravel(), left.ravel(), right.ravel()], axis=1)
    return nbr.astype(np.int32)
