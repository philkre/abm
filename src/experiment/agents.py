"""Household agent with aspiration-based contribution learning.

Decision rule (aspiration learning):
  Each round the agent receives a payoff π = endowment - contribution,
  minus any wealth lost to disaster.
  - If π < aspiration  → increase contribution by delta (seek to avert disaster)
  - If π >= aspiration → decrease contribution by delta (exploit safety)
  Aspiration updates as a moving average: A ← (1-α)A + α·π
"""

from __future__ import annotations

import mesa

from experiment.config import AgentConfig, TreatmentConfig


class HouseholdAgent(mesa.Agent):
    """A participant in one experimental session.

    Pure data container between rounds. All phase logic lives in the model.

    Attributes:
        contribution: Amount contributed to the group pot this round.
        wealth: Accumulated private earnings across rounds.
        aspiration: Current aspiration level (moving avg of payoffs).
        payoff: Net payoff received this round (set by model).
        disaster: Whether this agent suffered a disaster loss this round.
    """

    def __init__(
        self,
        model: mesa.Model,
        treatment: TreatmentConfig,
        agent_cfg: AgentConfig,
    ) -> None:
        super().__init__(model)
        self._treatment = treatment
        self._alpha = agent_cfg.aspiration_alpha
        self._delta = agent_cfg.contrib_delta

        self.contribution: float = agent_cfg.contrib_init
        self.aspiration: float = agent_cfg.aspiration_init
        self.wealth: float = 0.0
        self.payoff: float = 0.0
        self.disaster: bool = False

    # ── called by model after payoff_phase ────────────────────────────────

    def update(self) -> None:
        """Aspiration-based contribution adjustment + aspiration update."""
        if self.payoff < self.aspiration:
            self.contribution = min(
                self._treatment.endowment,
                self.contribution + self._delta,
            )
        else:
            self.contribution = max(0.0, self.contribution - self._delta)

        self.aspiration = (
            (1.0 - self._alpha) * self.aspiration + self._alpha * self.payoff
        )
