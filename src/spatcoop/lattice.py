"""Precomputed Von Neumann neighbour indices for a toroidal L×L lattice."""

import numpy as np


def make_neighbour_indices(L: int) -> np.ndarray:
    """
    Return shape (L, L, 4) int32 array of flat neighbour indices.

    Axis-2 order: [North, South, East, West] where
      North = (row-1) % L,  South = (row+1) % L,
      East  = (col+1) % L,  West  = (col-1) % L.
    Flat index = row * L + col.
    """
    rows = np.arange(L, dtype=np.int32)
    cols = np.arange(L, dtype=np.int32)
    r, c = np.meshgrid(rows, cols, indexing="ij")  # (L, L)
    N = ((r - 1) % L) * L + c
    S = ((r + 1) % L) * L + c
    E = r * L + (c + 1) % L
    W = r * L + (c - 1) % L
    return np.stack([N, S, E, W], axis=-1)  # (L, L, 4)
