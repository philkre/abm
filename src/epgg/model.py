"""EPGG generation loop with fast-strategy / slow-environment timescales.

One generation (Ding 2024):
  1. freeze EHI; precompute benefit = r·Σ_closed e once.
  2. L² random sequential Fermi updates (fermi_sweep).
  3. update EHI once, from the post-generation strategy field (Eq. 2).

Stationarity is judged by mean-stabilization (not variance): the C+D phase is
cyclic dominance whose fraction oscillates forever, so a variance threshold
never fires. Homogeneous all-C / all-D states are absorbing and exit early.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from epgg.kernel import benefit_field, fermi_sweep, update_ehi
from epgg.lattice import neighbor_indices


@dataclass
class RunResult:
    """Outcome of one session.

    Attributes:
        coop_fraction: cooperator fraction time-averaged over the final window.
        generations: generations actually run (<= max_gen).
        converged: True if stationary (or homogeneous) before the cap.
        history: cooperator fraction per generation.
    """

    coop_fraction: float
    generations: int
    converged: bool
    history: np.ndarray


def mean_converged(series, window: int, tol: float) -> bool:
    """True when the windowed mean has stabilized between consecutive windows.

    Compares the mean of the last `window` samples to the mean of the `window`
    before it; converged when they differ by less than `tol`. Robust to the
    cyclic fluctuation of the C+D phase (the mean is flat even if variance is
    not). Returns False until at least 2·window samples exist.
    """
    n = len(series)
    if n < 2 * window:
        return False
    arr = np.asarray(series)
    recent = arr[-window:].mean()
    prior = arr[-2 * window : -window].mean()
    return abs(recent - prior) < tol


def _gen_seed(seed: int, gen: int) -> int:
    """Spread per-generation seeds so sequential generations decorrelate."""
    return int((seed * 1_000_003 + gen * 2_654_435_761) % (2**31))


def run_to_stationarity(
    L: int,
    delta: float,
    gamma: float,
    r: float = 4.0,
    c: float = 1.0,
    K: float = 0.5,
    seed: int = 0,
    window: int = 200,
    tol: float = 1e-3,
    min_gen: int = 1500,
    max_gen: int = 12_000,
) -> RunResult:
    """Run one session to stationarity from a fresh ~50/50 random init.

    Args:
        L: lattice side; nodes = L². The C phase only exists near L=200 — on
            smaller lattices cooperator clusters cannot survive the early
            defector bottleneck, so use L=200 for paper-comparable results.
        delta: cooperator EHI repair rate.
        gamma: defector EHI destruction rate.
        r: environmental benefit scaling (paper baseline 4).
        c: per-game cooperation cost (paper baseline 1; flat 5c per cooperator).
        K: Fermi noise (paper 0.5).
        seed: RNG seed (init + per-generation Fermi stream).
        window: samples per stabilization window.
        tol: mean-change tolerance for convergence.
        min_gen: generations that MUST elapse before a mean-stabilization stop is
            allowed. The C phase can sit at frac≈0 for hundreds of generations
            before cooperators recover (cf. Fig 3: defectors peak ~gen 20, full C
            by ~gen 2600); stopping during that plateau would misclassify C as D.
            Set comfortably past the recovery window.
        max_gen: hard cap on generations.

    Returns a RunResult with the final-window time-averaged cooperator fraction.
    A run still ends immediately if it reaches an absorbing homogeneous state
    (frac exactly 0 or 1), which the recoverable near-extinction plateau never
    does (a few survivors keep frac > 0).
    """
    rng = np.random.default_rng(seed)
    strategy = (rng.random((L, L)) < 0.5).astype(np.int8)
    ehi = np.zeros((L, L))
    neighbors = neighbor_indices(L)

    history: list[float] = []
    converged = False
    homogeneous = False
    for gen in range(max_gen):
        benefit = np.ascontiguousarray(benefit_field(ehi, r).ravel())
        fermi_sweep(
            strategy.reshape(-1), benefit, neighbors, c, K, _gen_seed(seed, gen)
        )
        ehi = update_ehi(ehi, strategy, delta, gamma)

        frac = float(strategy.mean())
        history.append(frac)

        if frac == 0.0 or frac == 1.0:  # absorbing homogeneous state
            converged = True
            homogeneous = True
            break
        if gen + 1 >= min_gen and mean_converged(history, window, tol):
            converged = True
            break

    hist = np.asarray(history)
    # On a homogeneity exit the stationary value is the final fraction; otherwise
    # time-average the post-convergence window (never the declining transient).
    if homogeneous:
        coop = hist[-1]
    else:
        tail = hist[-window:] if hist.size >= window else hist
        coop = float(tail.mean())
    return RunResult(
        coop_fraction=coop,
        generations=hist.size,
        converged=converged,
        history=hist,
    )
