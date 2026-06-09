"""Experiment model: one fixed group of 4 agents for n_rounds.

Replicates the structure of a single experimental session from
Jonsson & Jonsson (2025). Phase order each round:

  1. Contribution — agents play the contribution set last round (or init)
  2. Pool         — sum contributions into the group pot
  3. Check        — with prob `disaster_prob` a threshold check fires
  4. Payoff       — round earnings = (endowment - contribution) + public-good
                    share (multiplier · pot / group_size). On a failed check
                    (disaster) cumulative wealth is wiped to zero and the
                    learning signal is a bounded negative penalty.
  5. Learning     — agents update contributions via the aspiration rule

Payoff model (paper): the pot is multiplied by `multiplier` (1.6) and split
evenly across the group, so each agent receives `multiplier · pot / n`.
A disaster (failed check) zeroes cumulative individual + group earnings.
"""

from __future__ import annotations

import mesa
from mesa import DataCollector

from experiment.agents import HouseholdAgent
from experiment.config import DEFAULT_AGENT_CONFIG, AgentConfig, TreatmentConfig


class ExperimentModel(mesa.Model):
    """One experimental session: fixed group, n_rounds steps.

    Args:
        treatment: Treatment configuration (disaster prob, threshold, etc.).
        agent_cfg: Aspiration learning parameters shared across agents.
        seed: RNG seed for reproducibility.

    Recorded across the session (for paper-comparable metrics):
        contrib_record: list[list[float]] — contributions played each round.
        check_fired:    list[bool] — whether a threshold check fired each round.
        check_passed:   list[bool] — whether pot >= threshold given a check.
    """

    def __init__(
        self,
        treatment: TreatmentConfig,
        agent_cfg: AgentConfig = DEFAULT_AGENT_CONFIG,
        seed: int | None = None,
    ) -> None:
        super().__init__(rng=seed)
        self.treatment = treatment
        self._disaster_penalty = agent_cfg.disaster_penalty

        for _ in range(treatment.group_size):
            HouseholdAgent(self, treatment, agent_cfg)

        # Per-round records (paper-comparable metrics)
        self.contrib_record: list[list[float]] = []
        self.check_fired: list[bool] = []
        self.check_passed: list[bool] = []

        self.datacollector = DataCollector(
            model_reporters={
                "mean_contribution": self._mean_contribution,
                "group_pot": self._group_pot,
                "disaster_rate": self._disaster_rate,
                "mean_wealth": self._mean_wealth,
                "mean_aspiration": self._mean_aspiration,
            }
        )
        self.datacollector.collect(self)

    # ── Mesa interface ─────────────────────────────────────────────────────

    def step(self) -> None:
        pool = self._pool_phase()
        fired, passed = self._check_phase(pool)
        disaster = fired and not passed

        # Record the contributions actually played this round, before learning.
        self.contrib_record.append([a.contribution for a in self.agents])
        self.check_fired.append(fired)
        self.check_passed.append(passed)

        self._payoff_phase(pool, disaster)
        self._learning_phase()
        self.datacollector.collect(self)

    def run(self) -> None:
        """Run the full session (n_rounds steps)."""
        for _ in range(self.treatment.n_rounds):
            self.step()

    # ── Phase methods ──────────────────────────────────────────────────────

    def _pool_phase(self) -> float:
        """Sum all contributions into the group pot."""
        return sum(a.contribution for a in self.agents)

    def _check_phase(self, pool: float) -> tuple[bool, bool]:
        """Decide whether a check fires and whether the group passed it.

        Returns (fired, passed). `passed` is meaningful only when `fired`.
        """
        cfg = self.treatment
        if cfg.disaster_prob <= 0.0 or self.random.random() >= cfg.disaster_prob:
            return False, True
        threshold = cfg.sample_threshold(self.random)
        return True, pool >= threshold

    def _payoff_phase(self, pool: float, disaster: bool) -> None:
        """Round earnings incl. public-good share; wipe wealth on disaster.

        Non-disaster: payoff = (endowment - contribution) + multiplier·pot/n,
        added to cumulative wealth.
        Disaster:     cumulative wealth wiped to 0; learning signal = bounded
        negative penalty (decoupled from the unbounded wealth loss so a single
        wipeout doesn't crater the aspiration moving average for many rounds).
        """
        cfg = self.treatment
        share = cfg.multiplier * pool / cfg.group_size
        for agent in self.agents:
            agent.disaster = disaster
            if disaster:
                agent.wealth = 0.0
                agent.payoff = -self._disaster_penalty
            else:
                round_earnings = (cfg.endowment - agent.contribution) + share
                agent.wealth += round_earnings
                agent.payoff = round_earnings

    def _learning_phase(self) -> None:
        """All agents update contributions simultaneously (synchronous)."""
        for agent in self.agents:
            agent.update()

    # ── DataCollector reporters ────────────────────────────────────────────

    def _mean_contribution(self) -> float:
        agents = list(self.agents)
        return sum(a.contribution for a in agents) / len(agents)

    def _group_pot(self) -> float:
        return sum(a.contribution for a in self.agents)

    def _disaster_rate(self) -> float:
        return float(any(a.disaster for a in self.agents))

    def _mean_wealth(self) -> float:
        agents = list(self.agents)
        return sum(a.wealth for a in agents) / len(agents)

    def _mean_aspiration(self) -> float:
        agents = list(self.agents)
        return sum(a.aspiration for a in agents) / len(agents)
