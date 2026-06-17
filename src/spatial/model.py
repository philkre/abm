"""Spatial threshold public goods game — Mesa model."""

from __future__ import annotations
import math
from math import exp

import mesa
from mesa import DataCollector
from mesa.discrete_space import OrthogonalVonNeumannGrid

from spatial.agents import HouseholdAgent
from spatial.config import DEFAULT_CONFIG, ModelConfig


class SpatialCollectiveRiskModel(mesa.Model):
    """Spatial threshold public goods game on a square Von Neumann lattice.

    Agents are Unconditional Cooperators (UC), Conditional Cooperators (CC),
    or Defectors (D).  Each step they pool contributions within their focal
    group (agent + 4 neighbours), face an independent disaster draw if the
    pool falls below a threshold, and update strategies by synchronous Fermi
    imitation.

    CC agents match the mean of their neighbours' contributions from the
    *previous* round.  This down-matching under defector pressure is the
    mechanism by which UC out-competes CC under stochastic disaster risk.

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

        # local EHI at each side using agent.unique_id, e_i
        self.ehi: dict[int, float] = {}

        self.grid = OrthogonalVonNeumannGrid(
            (config.grid_size, config.grid_size),
            torus=True,
            capacity=1,
            random=self.random,
        )

        uc_thresh = config.initial_uc_fraction
        cc_thresh = config.initial_uc_fraction + config.initial_cc_fraction

        for cell in self.grid.all_cells:
            r = self.random.random()
            if r < uc_thresh:
                strategy = "UC"
            elif r < cc_thresh:
                strategy = "CC"
            else:
                strategy = "D"
            # CC agents start as full cooperators (prev_contribution = max contribution)
            agent = HouseholdAgent(
                self,
                strategy,
                config.initial_wealth,
                initial_contribution=config.contribution,
            )
            agent.cell = cell

            # initial EHI: e_i(0)
            self.ehi[agent.unique_id] = config.env_initial

        self._pools: dict[int, float] = {}

        self.datacollector = DataCollector(
            model_reporters={
                "uc_rate": self._uc_rate,
                "cc_rate": self._cc_rate,
                "cooperation_rate": self._cooperation_rate,
                "mean_wealth": self._mean_wealth,
                "disaster_rate": self._disaster_rate,
                "mean_ehi": self._mean_ehi,
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
        self._strategy_update_phase_payoff()
        self._mutation_phase()
        self._update_prev_contributions_phase()
        self._environmental_update_phase()
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
        cfg = self.config
        for agent in self.agents:
            if agent.strategy == "UC":
                agent.contribution = cfg.contribution
            elif agent.strategy == "D":
                agent.contribution = 0.0
            else:  # CC: match mean of neighbours' contributions from the previous round
                mean_prev = (
                    sum(n.prev_contribution for n in self._neighbours(agent)) / 4
                )
                agent.contribution = min(mean_prev, cfg.contribution)

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
        cfg = self.config
        for agent in self.agents:
            wealth_before = agent.wealth
            
            # enviromental benefit
            env_sum = sum(self.ehi[m.unique_id] for m in self._focal_group(agent))
            env_benefit = cfg.env_r * env_sum
            agent.wealth += env_benefit

            agent.wealth += cfg.income           # receive round endowment
            agent.wealth -= agent.contribution
            if agent.disaster:
                loss = cfg.loss_fraction * agent.wealth
                agent.wealth -= loss
            agent.payoff = agent.wealth - wealth_before


    def _strategy_update_phase_payoff(self) -> None:
        """ Synchronous Fermi imitation using per-round payoff as fitness proxy. """
        cfg = self.config
        new_strategies: dict[int, str] = {}

        for agent in self.agents:
            neighbour = self.random.choice(self._neighbours(agent))

            # Use current-round payoff difference
            delta = neighbour.payoff - agent.payoff

            # Argument of the exponential
            x = cfg.beta * delta

            # Clamp x to avoid overflow in exp(x)
            if x > 50:
                prob = 1.0          # neighbour much better: almost sure imitation
            elif x < -50:
                prob = 0.0          # neighbour much worse: almost never imitate
            else:
                prob = 1.0 / (1.0 + math.exp(-x))

            new_strategies[agent.unique_id] = (
                neighbour.strategy if self.random.random() < prob else agent.strategy)

        # Synchronous update
        for agent in self.agents:
            agent.strategy = new_strategies[agent.unique_id]


    def _strategy_update_phase(self) -> None:
        """Synchronous Fermi imitation using accumulated wealth as fitness proxy.

        Wealth integrates performance over all past rounds, giving a more
        robust signal than single-round payoff.
        """
        cfg = self.config
        new_strategies: dict[int, str] = {}
        for agent in self.agents:
            neighbour = self.random.choice(self._neighbours(agent))
            delta = neighbour.payoff - agent.payoff
            print(delta)
            prob = 1.0 / (1.0 + exp(-cfg.beta * delta))
            new_strategies[agent.unique_id] = (
                neighbour.strategy if self.random.random() < prob else agent.strategy
            )
        for agent in self.agents:
            agent.strategy = new_strategies[agent.unique_id]

    def _mutation_phase(self) -> None:
        strategies = ("UC", "CC", "D")
        for agent in self.agents:
            if self.random.random() < self.config.mu:
                agent.strategy = self.random.choice(
                    [s for s in strategies if s != agent.strategy]
                )

    def _update_prev_contributions_phase(self) -> None:
        """Store each agent's contribution so CC can read it next round."""
        for agent in self.agents:
            agent.prev_contribution = agent.contribution

    def _environmental_update_phase(self) -> None:
        """Update EHI based on number of cooperators and defectors in the neighborhood."""
        cfg = self.config
        
        new_ehi: dict[int, float] = {}
        for agent in self.agents:
            neighborhood = self._focal_group(agent)

            # environment update eq
            n_C = sum(m.strategy != "D" for m in neighborhood)
            n_D = sum(m.strategy == "D" for m in neighborhood)
            e_old = self.ehi[agent.unique_id]
            e_new = e_old + n_C * cfg.env_delta - n_D * cfg.env_gamma

            # bound [-1, 1]
            e_new = max(cfg.env_min, min(cfg.env_max, e_new))
            new_ehi[agent.unique_id] = e_new

        self.ehi = new_ehi


    # ------------------------------------------------------------------
    # DataCollector reporters
    # ------------------------------------------------------------------

    def _uc_rate(self) -> float:
        agents = list(self.agents)
        return sum(a.strategy == "UC" for a in agents) / len(agents)

    def _cc_rate(self) -> float:
        agents = list(self.agents)
        return sum(a.strategy == "CC" for a in agents) / len(agents)

    def _cooperation_rate(self) -> float:
        """Fraction of non-defectors (UC + CC)."""
        agents = list(self.agents)
        return sum(a.strategy != "D" for a in agents) / len(agents)

    def _mean_wealth(self) -> float:
        agents = list(self.agents)
        return sum(a.wealth for a in agents) / len(agents)

    def _disaster_rate(self) -> float:
        agents = list(self.agents)
        return sum(a.disaster for a in agents) / len(agents)
    
    def _mean_ehi(self) -> float:
        return sum(self.ehi.values()) / len(self.ehi)
