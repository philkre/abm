"""Configuration for the experiment ABM.

Replicates the five treatments from Jonsson & Jonsson (2025):
  Control  — no disaster risk
  10P      — 10% disaster check probability
  40P      — 40% disaster check probability  (main treatment)
  Level    — 40% check, threshold drawn uniformly from [50, 70] each check
  Impact   — 40% check, same mechanics as 40P (different framing in paper)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TreatmentConfig:
    """Parameters for one experimental treatment.

    Args:
        name: Treatment label.
        disaster_prob: Per-round probability of a disaster check.
        threshold: Group contribution required to avert disaster.
        threshold_lo: Lower bound for random threshold (Level treatment only).
        threshold_hi: Upper bound for random threshold (Level treatment only).
        n_rounds: Rounds per session (20 in the paper's experiment).
        group_size: Players per group (4 in the paper).
        endowment: Per-player per-round endowment in MU.
    """

    name: str
    disaster_prob: float
    threshold: float = 60.0
    threshold_lo: float = 60.0   # used only when threshold_lo != threshold_hi
    threshold_hi: float = 60.0
    n_rounds: int = 20
    group_size: int = 4
    endowment: float = 20.0
    multiplier: float = 1.6      # public-good multiplier (paper: pot ×1.6, split 4 ways)

    def sample_threshold(self, rng) -> float:
        """Return the active threshold for one disaster check."""
        if self.threshold_lo == self.threshold_hi:
            return self.threshold
        return rng.uniform(self.threshold_lo, self.threshold_hi)


@dataclass(frozen=True)
class AgentConfig:
    """Asymmetric aspiration-learning parameters.

    Each agent keeps a contribution level and an aspiration (target payoff).
    After each round (see HouseholdAgent.update):
      - Disaster this round       → jump contribution up by delta_up
                                    (the empirical "got burned" response, Fig 5)
      - Safe & payoff >= aspiration → free-ride a little down by contrib_delta
      - Safe & payoff <  aspiration → nudge up by contrib_delta
    Aspiration tracks a moving average of received payoffs.

    The disaster bump is what differentiates treatments from Control: with no
    disasters the rule has only the free-ride pull, so Control contributions
    decline, while disaster risk sustains cooperation near the threshold.

    Per-agent heterogeneity (the source of the emergent UC/CC/FR type mix):
    each agent draws its initial aspiration uniformly from
    [aspiration_lo, aspiration_hi]. A higher aspiration is rarely satisfied →
    higher sustained contribution → classified UC; a lower aspiration is easily
    satisfied → free-rides → classified FR.

    Args:
        contrib_init: Starting contribution (MU). Paper round-1 average ≈ 12.
        aspiration_lo: Lower bound of the per-agent initial aspiration draw.
        aspiration_hi: Upper bound of the per-agent initial aspiration draw.
        aspiration_alpha: Aspiration update learning rate ∈ (0, 1].
        contrib_delta: Safe-round step size for contribution adjustment (MU).
        delta_up: Upward step taken on a disaster round (MU); larger than
            contrib_delta to reproduce the post-failed-check ratchet (Fig 5).
        disaster_penalty: Bounded negative learning signal on a disaster round,
            fed to the aspiration moving average. Decoupled from the (unbounded)
            cumulative wealth wipeout so one wipeout doesn't crater aspiration.
    """

    contrib_init: float = 12.0          # paper round-1 mean ≈ 12
    aspiration_lo: float = 20.0
    aspiration_hi: float = 36.0
    aspiration_alpha: float = 0.3
    contrib_delta: float = 1.0          # step on a safe round (aspiration rule)
    delta_up: float = 6.0               # step up after a disaster (got-burned response)
    disaster_penalty: float = 20.0


# ── Treatment definitions ──────────────────────────────────────────────────

TREATMENTS: dict[str, TreatmentConfig] = {
    "Control": TreatmentConfig(
        name="Control",
        disaster_prob=0.0,
    ),
    "10P": TreatmentConfig(
        name="10P",
        disaster_prob=0.1,
    ),
    "40P": TreatmentConfig(
        name="40P",
        disaster_prob=0.4,
    ),
    "Level": TreatmentConfig(
        name="Level",
        disaster_prob=0.4,
        threshold=60.0,
        threshold_lo=50.0,
        threshold_hi=70.0,
    ),
    "Impact": TreatmentConfig(
        name="Impact",
        disaster_prob=0.4,
    ),
}

DEFAULT_AGENT_CONFIG = AgentConfig()
