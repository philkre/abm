"""epgg — spatial public goods game with environmental feedback (Ding 2024).

Baseline reproduction of Ding, Wang, Zhao, Gu & Chen (2024), *Chaos* 34,
123138 (doi:10.1063/5.0242366): an L×L lattice where each residence carries an
environmental health index (EHI) that cooperators repair and defectors degrade.
Payoffs scale with the local EHI; strategies evolve by the Fermi rule on a fast
timescale while the EHI updates once per generation (slow timescale).

Design: llm_hints/superpowers/specs/2026-06-16-ding-epgg-baseline-design.md

Pure numpy + numba (not Mesa): the hot loop is L²=40 000 nodes × up to ~6×10⁸
Fermi steps, far beyond a per-agent object model.
"""

from epgg.kernel import (
    benefit_field,
    closed_sum,
    cooperator_counts,
    fermi_sweep,
    update_ehi,
)
from epgg.lattice import neighbor_indices
from epgg.model import RunResult, mean_converged, run_to_stationarity
from epgg.sweep import coop_fraction_at, delta_sweep
from epgg.figures import plot_delta_sweep, run_fig2

__all__ = [
    "neighbor_indices",
    "closed_sum",
    "cooperator_counts",
    "update_ehi",
    "benefit_field",
    "fermi_sweep",
    "RunResult",
    "mean_converged",
    "run_to_stationarity",
    "coop_fraction_at",
    "delta_sweep",
    "plot_delta_sweep",
    "run_fig2",
]
