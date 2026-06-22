"""Configuration for the experiment ABM.

Replicates the five treatments from Jonsson & Jonsson (2025):
  Control  — no disaster risk
  10P      — 10% disaster check probability
  40P      — 40% disaster check probability  (main treatment)
  Level    — 40% check, integer threshold drawn from [50, 70] each check
  Impact   — 40% check; on a failed check the individual accounts, the group
             account, or both are wiped (probability 1/3 each), instead of
             always both as in 10P/40P/Level
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
        multiplier: Public-good multiplier applied to the pot.
        random_impact: If True (Impact treatment), a failed check wipes the
            individual accounts, the group account, or both with probability
            1/3 each; otherwise a failed check always wipes both.
    """

    name: str
    disaster_prob: float
    threshold: float = 60.0
    threshold_lo: float = 60.0  # used only when threshold_lo != threshold_hi
    threshold_hi: float = 60.0
    n_rounds: int = 20
    group_size: int = 4
    endowment: float = 20.0
    multiplier: float = 1.6  # public-good multiplier (paper: pot ×1.6, split 4 ways)
    random_impact: bool = False  # Impact: wipe individual/group/both w.p. 1/3 each

    def sample_threshold(self, rng) -> float:
        """Return the active threshold for one disaster check.

        Level draws an integer uniformly from [threshold_lo, threshold_hi]
        (inclusive), as in the paper ("any integer value in 50 to 70 units").
        """
        if self.threshold_lo == self.threshold_hi:
            return self.threshold
        return float(rng.randint(int(self.threshold_lo), int(self.threshold_hi)))


@dataclass(frozen=True)
class AgentConfig:
    """Blend-rule parameters (see specs/2026-06-10-blend-rule-design.md).

    Each round every agent blends three anchors into its next contribution:

        c ← clip( w·share + (1-w)·(m·others_mean + (1-m)·g − bias), 0, E )

    where share = threshold_hi / group_size (worst case under Level
    uncertainty), and w = s·θ is the threat weight: per-agent sensitivity s
    times session-level threat salience θ.

    Heterogeneous traits, drawn once per agent:
      g ~ U(g_lo, g_hi)  — intrinsic generosity (warm glow; also round-1 basis)
      m ~ U(m_lo, m_hi)  — conformity (weight on matching others)
      s ~ U(0, 1)        — threat sensitivity

    Threat salience θ (session level, lives on the model):
      θ_0 = theta_init if disaster_prob > 0 else 0   (existence of risk, not
            its magnitude — the paper's coarse probability heuristic)
      failed check → θ += theta_bump, landing one round late (gambler's
            fallacy; reproduces Fig 5's flat-then-rise)
      θ decays by (1 - theta_decay) per round (habituation), clipped to [0,1].

    The joint (g, m, s) draw produces the emergent UC/CC/FR mix: high s →
    flat high LCP line (UC); high m → matching line (CC); low s, m, g →
    flat low line (FR).

    Args:
        g_lo: Lower bound of the generosity draw (MU).
        g_hi: Upper bound of the generosity draw (MU).
        m_lo: Lower bound of the conformity draw.
        m_hi: Upper bound of the conformity draw.
        bias: Self-serving downward bias applied to the social anchor (MU).
        anchor_margin: Safety factor on the fair share (>1 = overshoot the
            threshold as insurance against others' shortfall; the paper's
            groups plateau at pot 62-65, above the 60 threshold).
        theta_init: Initial threat salience when any disaster risk exists.
        theta_bump: Salience increment after a failed check.
        theta_decay: Per-round salience decay rate (habituation).
        noise_sd: SD of idiosyncratic per-round noise (MU). Contributions are
            rounded to whole units, as in the paper's design ("allocation is
            in whole units (0, 1, ..., 20)").
    """

    g_lo: float = 4.0
    g_hi: float = 20.0
    m_lo: float = 0.1
    m_hi: float = 1.0
    bias: float = 0.5
    anchor_margin: float = 1.15
    theta_init: float = 0.9
    theta_bump: float = 0.15
    theta_decay: float = 0.01
    noise_sd: float = 2.0


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
        random_impact=True,
    ),
}

DEFAULT_AGENT_CONFIG = AgentConfig()
