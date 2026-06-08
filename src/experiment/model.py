"""Experiment model: one fixed group of 4 agents for n_rounds.

Replicates the structure of a single experimental session from
Jonsson & Jonsson (2025). Phase order each round:

  1. Contribution — agents submit contributions (already set from prior round)
  2. Pool         — sum contributions into group pot
  3. Disaster     — stochastic check; zero wealth if pool < threshold
  4. Payoff       — compute round earnings, update wealth
  5. Learning     — agents update contributions via aspiration rule
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
    """

    def __init__(
        self,
        treatment: TreatmentConfig,
        agent_cfg: AgentConfig = DEFAULT_AGENT_CONFIG,
        seed: int | None = None,
    ) -> None:
        super().__init__(rng=seed)
        self.treatment = treatment

        for _ in range(treatment.group_size):
            HouseholdAgent(self, treatment, agent_cfg)

        self._pools: dict[int, float] = {}

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
        self._disaster_phase(pool)
        self._payoff_phase()
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

    def _disaster_phase(self, pool: float) -> None:
        """Stochastic disaster check. Zero wealth if pool < threshold."""
        cfg = self.treatment
        disaster_fires = (
            cfg.disaster_prob > 0.0
            and self.random.random() < cfg.disaster_prob
            and pool < cfg.sample_threshold(self.random)
        )
        for agent in self.agents:
            agent.disaster = disaster_fires
            if disaster_fires:
                agent.wealth = 0.0

    def _payoff_phase(self) -> None:
        """Round earnings = endowment - contribution (zeroed on disaster)."""
        endowment = self.treatment.endowment
        for agent in self.agents:
            round_earnings = endowment - agent.contribution
            if agent.disaster:
                agent.payoff = -agent.wealth   # wealth already zeroed; signal the loss
            else:
                agent.payoff = round_earnings
                agent.wealth += round_earnings

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
        agents = list(self.agents)
        return float(any(a.disaster for a in agents))

    def _mean_wealth(self) -> float:
        agents = list(self.agents)
        return sum(a.wealth for a in agents) / len(agents)

    def _mean_aspiration(self) -> float:
        agents = list(self.agents)
        return sum(a.aspiration for a in agents) / len(agents)
