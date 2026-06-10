"""Household agent with the three-anchor blend rule.

NOTE: the decision rule is an *original modelling addition* of this project,
not part of Jonsson & Jonsson (2025) — the paper reports human experiments
and contains no behavioural agent model. The rule is built from documented
behaviour (design: llm_hints/superpowers/specs/2026-06-10-blend-rule-design.md):

  - conditional cooperation: match others' previous-round mean (shown to
    subjects on the summary screen), minus a self-serving bias
  - intrinsic generosity g: warm-glow anchor that keeps Control from
    collapsing to zero (and sets the round-1 contribution)
  - threshold anchoring: under disaster risk, agents pull toward their fair
    share of the (worst-case) threshold with threat weight w = s·θ

Honesty note: the rule is linear in others' mean — the same functional form
the LCP classifier (analysis.py) fits — so the type *form* is built in and
the treatment type mix is a calibration target. Dynamics and the
Control→treatment type shift remain emergent.
"""

from __future__ import annotations

import mesa

from experiment.config import AgentConfig, TreatmentConfig


class HouseholdAgent(mesa.Agent):
    """A participant in one experimental session.

    Pure data container between rounds. All phase logic lives in the model;
    the model calls `update()` with the information a subject saw on the
    summary screen (others' mean) and the current threat salience θ.

    Attributes:
        contribution: Amount contributed to the group pot this round.
        indiv_account: Accumulated private earnings (endowment - contribution).
        payoff: Round earnings as experienced (0 on a disaster round).
        disaster: Whether this agent suffered a disaster loss this round.
        g: Intrinsic generosity draw (MU).
        m: Conformity draw (weight on matching others).
        s: Threat sensitivity draw.
    """

    def __init__(
        self,
        model: mesa.Model,
        treatment: TreatmentConfig,
        agent_cfg: AgentConfig,
    ) -> None:
        super().__init__(model)
        self._treatment = treatment
        self._bias = agent_cfg.bias
        self._noise_sd = agent_cfg.noise_sd

        rng = model.random
        self.g: float = rng.uniform(agent_cfg.g_lo, agent_cfg.g_hi)
        self.m: float = rng.uniform(agent_cfg.m_lo, agent_cfg.m_hi)
        self.s: float = rng.uniform(0.0, 1.0)

        # Fair share of the worst-case threshold (Level: 70/4 = 17.5), with a
        # safety margin (insurance against others' shortfall; paper groups
        # plateau above the threshold).
        self._share = (
            treatment.threshold_hi / treatment.group_size * agent_cfg.anchor_margin
        )

        # Round 1: no information about others yet — blend share with own
        # generosity. In Control θ=0, so this reduces to g.
        w0 = self.s * model.theta
        self.contribution: float = self._quantize(
            w0 * self._share + (1.0 - w0) * self.g
        )

        self.indiv_account: float = 0.0
        self.payoff: float = 0.0
        self.disaster: bool = False

    @property
    def wealth(self) -> float:
        """Total earnings as if the group account were split now (paper:
        the group account is divided evenly at the end of the session)."""
        return (
            self.indiv_account + self.model.group_account / self._treatment.group_size
        )

    def _quantize(self, c: float) -> float:
        """Add idiosyncratic noise, round to whole units, clip to [0, E]
        (paper: allocations are whole units 0..20)."""
        c += self.model.random.gauss(0.0, self._noise_sd)
        return min(self._treatment.endowment, max(0.0, float(round(c))))

    # ── called by model in the learning phase ─────────────────────────────

    def update(self, others_mean: float, theta: float) -> None:
        """Blend the three anchors into next round's contribution.

        Args:
            others_mean: Mean contribution of the other group members this
                round (the summary-screen information).
            theta: Current session-level threat salience ∈ [0, 1].
        """
        w = self.s * theta
        social = self.m * others_mean + (1.0 - self.m) * self.g - self._bias
        self.contribution = self._quantize(w * self._share + (1.0 - w) * social)
