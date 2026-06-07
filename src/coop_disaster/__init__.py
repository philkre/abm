"""
Cooperation in the Face of Disaster — Python ABM.

Replicates Fig 7 from Jonsson & Jonsson (2025), PLoS ONE 20(4): e0318891.
"""

from coop_disaster.types import DEFAULT_CONFIG, LcpParams, PlayerType, SimConfig, LatticeConfig, DEFAULT_LATTICE_CONFIG
from coop_disaster.lcp import contribution
from coop_disaster.group import PlayerAgent, DisasterGroupModel, assign_types, simulate_group
from coop_disaster.sweep import run_sweep
from coop_disaster.lattice import run_evolution, run_generation, fermi_update

__all__ = [
    "PlayerType",
    "LcpParams",
    "SimConfig",
    "DEFAULT_CONFIG",
    "LatticeConfig",
    "DEFAULT_LATTICE_CONFIG",
    "contribution",
    "PlayerAgent",
    "DisasterGroupModel",
    "assign_types",
    "simulate_group",
    "run_sweep",
    "run_evolution",
    "run_generation",
    "fermi_update",
]
