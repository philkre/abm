"""Spatial threshold public goods game — Mesa model."""

from __future__ import annotations

from math import exp

import mesa
from mesa import DataCollector
from mesa.discrete_space import OrthogonalVonNeumannGrid

from spatial.agents import HouseholdAgent
from spatial.config import DEFAULT_CONFIG, ModelConfig


class SpatialCollectiveRiskModel(mesa.Model):
    """Spatial threshold public goods game on a square Von Neumann lattice.

    Agents are Unconditional Cooperators (UC) or Defectors (D).  Each step
    they pool contributions within their focal group (agent + 4 neighbours),
    face an independent disaster draw if the pool falls below a threshold,
    and update strategies by synchronous Fermi imitation.

    Parameters
    ----------
    config:
        All model parameters.  Defaults to DEFAULT_CONFIG.

    Attributes
    ----------
    config: ModelConfig
    grid: OrthogonalVonNeumannGrid
    datacollector: mesa.DataCollector
    """

    def __init__(self, config: ModelConfig = DEFAULT_CONFIG) -> None:
        super().__init__(rng=config.seed)
        self.config = config

        self.grid = OrthogonalVonNeumannGrid(
            (config.grid_size, config.grid_size),
            torus=True,
            capacity=1,
            random=self.random,
        )

        for cell in self.grid.all_cells:
            strategy = (
                "UC" if self.random.random() < config.initial_uc_fraction else "D"
            )
            agent = HouseholdAgent(self, strategy, config.initial_wealth)
            agent.cell = cell

        self._pools: dict[int, float] = {}

        self.datacollector = DataCollector(
            model_reporters={
                "cooperation_rate": self._cooperation_rate,
                "mean_wealth": self._mean_wealth,
                "disaster_rate": self._disaster_rate,
            }
        )
        self.datacollector.collect(self)

    # ------------------------------------------------------------------
    # Mesa interface
    # ------------------------------------------------------------------

    def step(self) -> None:
        self._contribution_phase()
        self._pool_phase()
        self._disaster_phase()
        self._payoff_phase()
        self._strategy_update_phase()
        self._mutation_phase()
        self.datacollector.collect(self)

    # ------------------------------------------------------------------
    # Neighbourhood helpers
    # ------------------------------------------------------------------

    def _neighbours(self, agent: HouseholdAgent) -> list[HouseholdAgent]:
        """Return the 4 Von Neumann neighbours (excludes the agent itself)."""
        return [next(iter(c.agents)) for c in agent.cell.connections.values()]

    def _focal_group(self, agent: HouseholdAgent) -> list[HouseholdAgent]:
        """Return [agent] + its Von Neumann neighbours."""
        return [agent] + self._neighbours(agent)

    # ------------------------------------------------------------------
    # Phase methods
    # ------------------------------------------------------------------

    def _contribution_phase(self) -> None:
        for agent in self.agents:
            agent.contribution = (
                self.config.contribution if agent.strategy == "UC" else 0.0
            )

    def _pool_phase(self) -> None:
        for agent in self.agents:
            self._pools[agent.unique_id] = sum(
                m.contribution for m in self._focal_group(agent)
            )

    def _disaster_phase(self) -> None:
        cfg = self.config
        for agent in self.agents:
            if self._pools[agent.unique_id] >= cfg.threshold:
                agent.disaster = False
            else:
                agent.disaster = self.random.random() < cfg.disaster_prob

    def _payoff_phase(self) -> None:
        for agent in self.agents:
            wealth_before = agent.wealth
            agent.wealth -= agent.contribution
            if agent.disaster:
                loss = self.config.loss_fraction * agent.wealth
                agent.wealth -= loss
            agent.payoff = agent.wealth - wealth_before

    def _strategy_update_phase(self) -> None:
        """Synchronous Fermi imitation using accumulated wealth as fitness proxy.

        Wealth integrates performance over all past rounds, giving a more
        robust signal than single-round payoff.
        """
        cfg = self.config
        new_strategies: dict[int, str] = {}
        for agent in self.agents:
            neighbour = self.random.choice(self._neighbours(agent))
            delta = neighbour.wealth - agent.wealth
            prob = 1.0 / (1.0 + exp(-cfg.beta * delta))
            new_strategies[agent.unique_id] = (
                neighbour.strategy if self.random.random() < prob else agent.strategy
            )
        for agent in self.agents:
            agent.strategy = new_strategies[agent.unique_id]

    def _mutation_phase(self) -> None:
        for agent in self.agents:
            if self.random.random() < self.config.mu:
                agent.strategy = "D" if agent.strategy == "UC" else "UC"

    # ------------------------------------------------------------------
    # DataCollector reporters
    # ------------------------------------------------------------------

    def _cooperation_rate(self) -> float:
        agents = list(self.agents)
        return sum(a.strategy == "UC" for a in agents) / len(agents)

    def _mean_wealth(self) -> float:
        agents = list(self.agents)
        return sum(a.wealth for a in agents) / len(agents)

    def _disaster_rate(self) -> float:
        agents = list(self.agents)
        return sum(a.disaster for a in agents) / len(agents)
