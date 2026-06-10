"""experiment — ABM replication of Jonsson & Jonsson (2025) experiments.

Agents use a three-anchor blend rule — threshold share (threat-weighted),
others' previous-round mean (conformity), intrinsic generosity — across five
treatments (Control, 10P, 40P, Level, Impact). The UC/CC/FR mix arises from
the joint heterogeneous trait draw (design:
llm_hints/superpowers/specs/2026-06-10-blend-rule-design.md).

NOTE: the paper reports human experiments and a deterministic LCP projection;
it contains no behavioural agent model. The blend rule is an original
modelling addition built from documented behaviour (conditional cooperation,
threshold anchoring, threat salience), calibrated to the paper's aggregate
findings (see agents.py for the honesty note on LCP circularity).
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
