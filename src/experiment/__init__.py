"""experiment — ABM replication of Jonsson & Jonsson (2025) experiments.

Agents use aspiration-based learning to adjust contributions across five
treatments (Control, 10P, 40P, Level, Impact). Types emerge from dynamics
rather than being pre-classified.
"""

from experiment.config import (
    AgentConfig,
    TreatmentConfig,
    TREATMENTS,
    DEFAULT_AGENT_CONFIG,
)
from experiment.agents import HouseholdAgent
from experiment.model import ExperimentModel
from experiment.run import run_sessions, run_all_treatments

__all__ = [
    "AgentConfig",
    "TreatmentConfig",
    "TREATMENTS",
    "DEFAULT_AGENT_CONFIG",
    "HouseholdAgent",
    "ExperimentModel",
    "run_sessions",
    "run_all_treatments",
]
