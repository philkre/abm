"""
Cooperation in the Face of Disaster — Python ABM.

Replicates Fig 7 from Jonsson & Jonsson (2025), PLoS ONE 20(4): e0318891.
"""

from coop_disaster.types import DEFAULT_CONFIG, LcpParams, PlayerType, SimConfig
from coop_disaster.sweep import run_sweep

__all__ = [
    "PlayerType",
    "LcpParams",
    "SimConfig",
    "DEFAULT_CONFIG",
    "run_sweep",
]
