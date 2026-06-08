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

    def sample_threshold(self, rng) -> float:
        """Return the active threshold for one disaster check."""
        if self.threshold_lo == self.threshold_hi:
            return self.threshold
        return rng.uniform(self.threshold_lo, self.threshold_hi)


@dataclass(frozen=True)
class AgentConfig:
    """Aspiration-based learning parameters.

    Each agent maintains a contribution level and an aspiration (target payoff).
    After each round:
      - If payoff < aspiration  → increase contribution by delta (cooperate more)
      - If payoff >= aspiration → decrease contribution by delta (defect a little)
    Aspiration tracks a moving average of received payoffs.

    Args:
        contrib_init: Starting contribution (MU). Paper average ≈ 12.
        aspiration_init: Starting aspiration level (MU).
        aspiration_alpha: Aspiration update learning rate ∈ (0, 1].
        contrib_delta: Step size for contribution adjustment (MU).
    """

    contrib_init: float = 12.0
    aspiration_init: float = 8.0    # slightly below endowment - contrib_init
    aspiration_alpha: float = 0.2
    contrib_delta: float = 1.0


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
