"""Experiment model: one fixed group of 4 agents for n_rounds.

Replicates the structure of a single experimental session from
Jonsson & Jonsson (2025). Phase order each round:

  1. Contribution — agents play the contribution set last round (or init)
  2. Pool         — sum contributions into the group pot
  3. Check        — with prob `disaster_prob` a threshold check fires
  4. Payoff       — credit accounts; on a failed check wipe accounts per scope
  5. Collect      — record the round as actually played
  6. Learning     — agents blend anchors into next round's contribution
                    (see agents.py); threat salience θ then updates

Accounting (paper): each round the kept endowment (endowment - contribution)
accrues to the agent's individual account, and the pot × multiplier (1.6)
accrues to a shared group account that is divided evenly at the end of the
session. A failed check wipes the individual accounts and the group account
(10P/40P/Level), or — in Impact — the individual accounts, the group account,
or both with probability 1/3 each.

Threat salience θ (session level): starts at theta_init when any disaster
risk exists; a failed check adds theta_bump with a one-round lag (gambler's
fallacy — Fig 5 shows no response in the round immediately after a failed
check, then a rise); decays by (1 - theta_decay) per round. Agents weight
the threshold anchor by w = s·θ.
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
        agent_cfg: Blend-rule parameters shared across agents.
        seed: RNG seed for reproducibility.

    Recorded across the session (for paper-comparable metrics):
        contrib_record: list[list[float]] — contributions played each round.
        check_fired:    list[bool] — whether a threshold check fired each round.
        check_passed:   list[bool] — whether pot >= threshold given a check.

    The DataCollector collects once per round *after* payoffs but *before*
    learning, so row i (0-based) is round i+1 exactly as played.
    """

    def __init__(
        self,
        treatment: TreatmentConfig,
        agent_cfg: AgentConfig = DEFAULT_AGENT_CONFIG,
        seed: int | None = None,
    ) -> None:
        super().__init__(rng=seed)
        self.treatment = treatment
        self._cfg = agent_cfg
        self.group_account: float = 0.0

        # Threat salience: existence of risk switches it on (before agents,
        # who read it for their round-1 contribution).
        self.theta: float = agent_cfg.theta_init if treatment.disaster_prob > 0 else 0.0
        self._pending_bump: float = 0.0  # failed-check bump, lands next round

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
                "theta": lambda m: m.theta,
            }
        )

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
        self.datacollector.collect(self)
        self._learning_phase(pool, disaster)

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

    def _disaster_scope(self) -> str:
        """Which accounts a failed check wipes: 'individual'/'group'/'both'."""
        if not self.treatment.random_impact:
            return "both"
        return self.random.choice(("individual", "group", "both"))

    def _payoff_phase(self, pool: float, disaster: bool) -> None:
        """Credit accounts, apply disaster wipes, record round earnings.

        Accounts are credited first so that Impact's partial wipes leave this
        round's earnings in the surviving account. `payoff` is a recorded
        metric only (the blend rule does not consume it); 0 on a disaster.
        """
        cfg = self.treatment
        share = cfg.multiplier * pool / cfg.group_size

        self.group_account += cfg.multiplier * pool
        for agent in self.agents:
            agent.indiv_account += cfg.endowment - agent.contribution

        if disaster:
            scope = self._disaster_scope()
            if scope in ("individual", "both"):
                for agent in self.agents:
                    agent.indiv_account = 0.0
            if scope in ("group", "both"):
                self.group_account = 0.0
            for agent in self.agents:
                agent.disaster = True
                agent.payoff = 0.0
        else:
            for agent in self.agents:
                agent.disaster = False
                agent.payoff = (cfg.endowment - agent.contribution) + share

    def _learning_phase(self, pool: float, disaster: bool) -> None:
        """Agents blend anchors (synchronous), then θ updates.

        The failed-check bump is queued and applied only *after* next round's
        contribution is set, so the response lands two rounds after the check
        (Fig 5: flat at +1, rise at +2).
        """
        n = self.treatment.group_size
        for agent in self.agents:
            others_mean = (pool - agent.contribution) / (n - 1)
            agent.update(others_mean, self.theta)

        self.theta = min(
            1.0, self.theta * (1.0 - self._cfg.theta_decay) + self._pending_bump
        )
        self._pending_bump = self._cfg.theta_bump if disaster else 0.0

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
