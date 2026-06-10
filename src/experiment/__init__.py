"""experiment — ABM replication of Jonsson & Jonsson (2025) experiments.

Agents use aspiration-based learning to adjust contributions across five
treatments (Control, 10P, 40P, Level, Impact). Types emerge from dynamics
rather than being pre-classified.

NOTE: the paper reports human experiments and a deterministic LCP projection;
it contains no behavioural agent model. The asymmetric aspiration learning
rule here is an original modelling addition of this project, tuned to
reproduce the paper's aggregate findings (see agents.py).
"""

from experiment.config import (
    AgentConfig,
    TreatmentConfig,
    TREATMENTS,
    DEFAULT_AGENT_CONFIG,
)
from experiment.agents import HouseholdAgent
from experiment.model import ExperimentModel
from experiment.run import TreatmentResults, run_sessions, run_all_treatments
from experiment.analysis import (
    TYPES,
    classify_lcp,
    classify_session,
    fit_lcp,
    type_distribution,
)
from experiment.figures import ProbResult, disaster_prob_sweep, plot_fig4

__all__ = [
    "AgentConfig",
    "TreatmentConfig",
    "TREATMENTS",
    "DEFAULT_AGENT_CONFIG",
    "HouseholdAgent",
    "ExperimentModel",
    "TreatmentResults",
    "run_sessions",
    "run_all_treatments",
    "TYPES",
    "fit_lcp",
    "classify_lcp",
    "classify_session",
    "type_distribution",
    "ProbResult",
    "disaster_prob_sweep",
    "plot_fig4",
]
