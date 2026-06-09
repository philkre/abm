"""Household agent with aspiration-based contribution learning.

Decision rule (aspiration learning), evaluated each round after payoffs:
  - If payoff <  aspiration → increase contribution by delta (avert disaster)
  - If payoff >= aspiration → decrease contribution by delta (exploit safety)
  Aspiration updates as a moving average:  A ← (1-α)·A + α·payoff

Heterogeneity: each agent draws its initial aspiration from
[aspiration_lo, aspiration_hi]. This spread is what makes a mix of
Unconditional Cooperators / Conditional Cooperators / Free-Riders emerge,
which the LCP classifier (analysis.py) then recovers — matching the paper's
type distributions.
"""

from __future__ import annotations

import mesa

from experiment.config import AgentConfig, TreatmentConfig


class HouseholdAgent(mesa.Agent):
    """A participant in one experimental session.

    Pure data container between rounds. All phase logic lives in the model.

    Attributes:
        contribution: Amount contributed to the group pot this round.
        wealth: Accumulated private earnings across rounds (zeroed on disaster).
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
        self._delta_up = agent_cfg.delta_up

        self.contribution: float = agent_cfg.contrib_init
        self.aspiration: float = model.random.uniform(
            agent_cfg.aspiration_lo, agent_cfg.aspiration_hi
        )
        self.wealth: float = 0.0
        self.payoff: float = 0.0
        self.disaster: bool = False

    # ── called by model after payoff_phase ────────────────────────────────

    def update(self) -> None:
        """Asymmetric aspiration update (matches the empirical Fig-5 response).

        - Disaster this round → jump contribution up by delta_up ("got burned":
          after a failed check, groups ratchet contributions up over the next
          rounds, Jonsson & Jonsson 2025 Fig 5).
        - Safe round, payoff >= aspiration → satisfied, free-ride a little down.
        - Safe round, payoff <  aspiration → nudge contribution up.

        Without disasters (Control) the rule has only the free-ride pull, so
        contributions decline; disaster risk is what sustains cooperation.
        Aspiration tracks a moving average of payoffs.
        """
        E = self._treatment.endowment
        if self.disaster:
            self.contribution = min(E, self.contribution + self._delta_up)
        elif self.payoff >= self.aspiration:
            self.contribution = max(0.0, self.contribution - self._delta)
        else:
            self.contribution = min(E, self.contribution + self._delta)

        self.aspiration = (
            (1.0 - self._alpha) * self.aspiration + self._alpha * self.payoff
        )
