"""Core array kernels: focal_sum and Fermi imitation step."""

import os
import numpy as np


def focal_sum(arr: np.ndarray) -> np.ndarray:
    """
    For each cell (i,j), sum arr over its Von Neumann focal group
    G_{ij} = {(i,j), N, S, E, W} on the torus.

    Uses np.roll — no explicit index array needed.
    Input/output shape: (L, L), same dtype.
    """
    return (
        arr
        + np.roll(arr, 1, axis=0)  # North
        + np.roll(arr, -1, axis=0)  # South
        + np.roll(arr, 1, axis=1)  # East
        + np.roll(arr, -1, axis=1)
    )  # West


def fermi_step_numpy(
    strategy: np.ndarray,  # (L, L) int8
    phi: np.ndarray,  # (L, L) float32
    beta: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    Synchronous Fermi imitation. Each cell picks one random neighbour,
    adopts its strategy with probability 1/(1+exp(-β*(φ_j - φ_i))).

    Returns new strategy array (L, L) int8. Input arrays are unchanged.
    """
    L = strategy.shape[0]
    # Random direction per cell: 0=N 1=S 2=E 3=W
    dirs = rng.integers(0, 4, size=(L, L)).astype(np.intp)

    phi_N = np.roll(phi, 1, axis=0)
    phi_S = np.roll(phi, -1, axis=0)
    phi_E = np.roll(phi, 1, axis=1)
    phi_W = np.roll(phi, -1, axis=1)

    s_N = np.roll(strategy, 1, axis=0)
    s_S = np.roll(strategy, -1, axis=0)
    s_E = np.roll(strategy, 1, axis=1)
    s_W = np.roll(strategy, -1, axis=1)

    phi_j = np.choose(dirs, [phi_N, phi_S, phi_E, phi_W])
    s_j = np.choose(dirs, [s_N, s_S, s_E, s_W])

    # Clip the exponent to guard overflow at large beta (the numba kernel
    # short-circuits the same ±30 range). exp(±30) saturates fermi to 0/1.
    z = np.clip(-beta * (phi_j - phi), -30.0, 30.0)
    fermi = 1.0 / (1.0 + np.exp(z))
    accept = rng.random((L, L), dtype=np.float32) < fermi

    return np.where(accept, s_j, strategy).astype(np.int8)


# Select implementation at import time
if os.environ.get("USE_NUMBA", "0") == "1":
    try:
        from spatcoop._numba_kernels import fermi_step_numba as fermi_step
    except ImportError:
        fermi_step = fermi_step_numpy
else:
    fermi_step = fermi_step_numpy
