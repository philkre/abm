"""Spatial evolutionary extension: Von Neumann lattice + Fermi update rule.

Grid:
  L×L torus (periodic boundaries via np.roll).
  Each agent's group = self + 4 VN neighbours (group size 5).
  Threshold default 75 = 75% of max group contribution (5 × 20 × 0.75).

Each generation:
  1. Interact — run n_rounds of vectorised LCP dynamics across the full grid.
     Each agent updates based on the mean of its 4 VN neighbours' contributions.
  2. Payoff  — group success (1.0) or failure (0.0) per agent.
  3. Update  — each agent picks one random VN neighbour; copies their type
               with Fermi probability 1 / (1 + exp(-(π_j − π_i) / κ)).
               Update is synchronous (all agents decide simultaneously).
"""

from __future__ import annotations

import numpy as np

from coop_disaster.types import LatticeConfig, LcpParams, PlayerType, SimConfig

# Integer codes used in the numpy grid arrays
_UC = 0
_CC = 1
_FR = 2
_TYPE_CODE: dict[PlayerType, int] = {
    PlayerType.UC: _UC,
    PlayerType.CC: _CC,
    PlayerType.FR: _FR,
}
CODE_TO_TYPE: dict[int, PlayerType] = {v: k for k, v in _TYPE_CODE.items()}


# ── helpers ────────────────────────────────────────────────────────────────


def _param_arrays(
    type_grid: np.ndarray,
    lcp: dict[PlayerType, LcpParams],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build (init, alpha, beta) float arrays from a type-code grid."""
    init = np.empty_like(type_grid, dtype=float)
    alpha = np.empty_like(type_grid, dtype=float)
    beta = np.empty_like(type_grid, dtype=float)
    for ptype, code in _TYPE_CODE.items():
        m = type_grid == code
        p = lcp[ptype]
        init[m] = p.init
        alpha[m] = p.alpha
        beta[m] = p.beta
    return init, alpha, beta


def _vn_sum(grid: np.ndarray) -> np.ndarray:
    """Sum the 4 Von Neumann neighbours of every cell (torus)."""
    return (
        np.roll(grid, -1, axis=0)
        + np.roll(grid, 1, axis=0)
        + np.roll(grid, -1, axis=1)
        + np.roll(grid, 1, axis=1)
    )


def _vn_stack(grid: np.ndarray) -> np.ndarray:
    """Stack 4 VN-neighbour grids into shape (L, L, 4) [up,down,left,right]."""
    return np.stack(
        [
            np.roll(grid, -1, axis=0),
            np.roll(grid, 1, axis=0),
            np.roll(grid, -1, axis=1),
            np.roll(grid, 1, axis=1),
        ],
        axis=2,
    )


# ── core simulation steps ──────────────────────────────────────────────────


def run_generation(
    type_grid: np.ndarray,
    sim_cfg: SimConfig,
    lat_cfg: LatticeConfig,
) -> np.ndarray:
    """Run one generation of LCP dynamics and return the payoff grid.

    Each agent's contribution each round = clamp(α + β × mean_of_4_vn_neighbours, 0, endowment).
    Group total = self + sum of 4 neighbours. Payoff = 1.0 if ≥ threshold, else 0.0.

    Args:
        type_grid: (L, L) int array of player-type codes.
        sim_cfg: Core config — lcp params, endowment, n_rounds.
        lat_cfg: Lattice config — group_threshold.

    Returns:
        (L, L) float array: 1.0 for successful groups, 0.0 for failed ones.
    """
    init, alpha, beta = _param_arrays(type_grid, sim_cfg.lcp)
    contribs = init.copy()

    for _ in range(sim_cfg.n_rounds):
        neighbor_mean = _vn_sum(contribs) / 4.0
        contribs = np.clip(alpha + beta * neighbor_mean, 0.0, sim_cfg.endowment)

    group_total = contribs + _vn_sum(contribs)  # self + 4 neighbours
    return (group_total >= lat_cfg.group_threshold).astype(float)


def fermi_update(
    type_grid: np.ndarray,
    payoffs: np.ndarray,
    lat_cfg: LatticeConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    """One synchronous Fermi update step.

    Each agent selects a random VN neighbour and copies their type with
    probability 1 / (1 + exp(-(π_neighbour − π_self) / κ)).

    Args:
        type_grid: (L, L) current type-code grid.
        payoffs: (L, L) payoffs from the current generation.
        lat_cfg: Supplies kappa.
        rng: NumPy Generator.

    Returns:
        Updated (L, L) type-code grid (new array; input unchanged).
    """
    L = lat_cfg.grid_size
    nbr_payoffs = _vn_stack(payoffs)   # (L, L, 4)
    nbr_types = _vn_stack(type_grid)   # (L, L, 4)

    # Random neighbour direction for each agent: 0=up 1=down 2=left 3=right
    dirs = rng.integers(0, 4, (L, L))
    rows = np.arange(L)[:, None]
    cols = np.arange(L)[None, :]

    sel_payoff = nbr_payoffs[rows, cols, dirs]  # (L, L)
    sel_type = nbr_types[rows, cols, dirs]      # (L, L)

    delta = sel_payoff - payoffs
    fermi_p = 1.0 / (1.0 + np.exp(-delta / lat_cfg.kappa))
    copy = rng.random((L, L)) < fermi_p

    return np.where(copy, sel_type, type_grid)


# ── full evolutionary run ──────────────────────────────────────────────────


def run_evolution(
    sim_cfg: SimConfig,
    lat_cfg: LatticeConfig,
    seed: int | None = None,
) -> dict:
    """Run the full spatial evolutionary simulation.

    Args:
        sim_cfg: Core simulation config (lcp, endowment, n_rounds).
        lat_cfg: Lattice config (grid_size, n_gen, kappa, init proportions,
                 group_threshold, snapshot_every).
        seed: RNG seed for reproducibility.

    Returns:
        dict with keys:
          ``uc_freq``      — (n_gen,) UC proportion each generation
          ``cc_freq``      — (n_gen,) CC proportion each generation
          ``fr_freq``      — (n_gen,) FR proportion each generation
          ``success_rate`` — (n_gen,) fraction of successful groups
          ``snapshots``    — list of (generation, type_grid) pairs
    """
    rng = np.random.default_rng(seed)
    L = lat_cfg.grid_size
    N = L * L

    # Initialise type grid from proportions
    r = rng.random((L, L))
    uc_cut = lat_cfg.init_uc
    cc_cut = lat_cfg.init_uc + lat_cfg.init_cc
    type_grid = np.where(r < uc_cut, _UC, np.where(r < cc_cut, _CC, _FR))

    uc_freq, cc_freq, fr_freq, success_rate = [], [], [], []
    snapshots: list[tuple[int, np.ndarray]] = []

    for gen in range(lat_cfg.n_gen):
        payoffs = run_generation(type_grid, sim_cfg, lat_cfg)
        type_grid = fermi_update(type_grid, payoffs, lat_cfg, rng)

        uc_freq.append((type_grid == _UC).sum() / N)
        cc_freq.append((type_grid == _CC).sum() / N)
        fr_freq.append((type_grid == _FR).sum() / N)
        success_rate.append(float(payoffs.mean()))

        if gen % lat_cfg.snapshot_every == 0 or gen == lat_cfg.n_gen - 1:
            snapshots.append((gen, type_grid.copy()))

    return {
        "uc_freq": np.array(uc_freq),
        "cc_freq": np.array(cc_freq),
        "fr_freq": np.array(fr_freq),
        "success_rate": np.array(success_rate),
        "snapshots": snapshots,
    }


def init_type_grid(lat_cfg: LatticeConfig, seed: int | None = None) -> np.ndarray:
    """Create an (L, L) type-code grid from LatticeConfig proportions.

    Convenience function for notebooks / interactive use.
    """
    rng = np.random.default_rng(seed)
    L = lat_cfg.grid_size
    r = rng.random((L, L))
    uc_cut = lat_cfg.init_uc
    cc_cut = lat_cfg.init_uc + lat_cfg.init_cc
    return np.where(r < uc_cut, _UC, np.where(r < cc_cut, _CC, _FR))
