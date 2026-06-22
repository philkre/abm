"""Configuration for the spatial threshold public goods game."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    """Immutable configuration for SpatialCollectiveRiskModel.

    Args:
        grid_size: Side length of the square lattice (N = grid_size²).
        initial_uc_fraction: Fraction of agents starting as UC.
        initial_cc_fraction: Fraction of agents starting as CC. D fraction = 1 - uc - cc.
        initial_wealth: Starting wealth for every agent.
        income: Endowment received at the start of every payoff phase (mirrors the
            paper's 20-unit round endowment). Keeps wealth dynamics meaningful over
            many rounds; without it, all wealth decays to zero.
        contribution: Max contribution; UC always pays this, CC is capped at this.
        threshold: Pool sum required to avert disaster for a focal group.
        disaster_prob: Probability of loss when pool < threshold.
        loss_fraction: Fraction of post-contribution wealth lost in a disaster.
        beta: Fermi selection strength (higher → more deterministic imitation).
        mu: Per-agent mutation probability each step.
        n_steps: Default number of simulation steps for run.py.
        seed: RNG seed (passed to Mesa's Model for full reproducibility).
        env_initial: environmental health index (EHI) at t=0.
        env_min: lower bound of EHI.
        env_max: upper bound of EHI.
        env_delta: increase in EHI per cooperator in neighborhood.
        env_gamma: decrease in EHI per defector in neighborhood.
        env_r: scales payoff.
    """

    grid_size: int = 20
    initial_uc_fraction: float = 0.5
    initial_cc_fraction: float = 0.0
    initial_wealth: float = 10.0
    income: float = 0.0
    contribution: float = 1.0
    threshold: float = 3.0
    disaster_prob: float = 0.5
    loss_fraction: float = 0.5
    beta: float = 1.0
    mu: float = 0.001
    n_steps: int = 500
    seed: int = 42
    
    # environmental feedback
    env_initial: float = 0.0
    env_min: float = -1.0
    env_max: float = 1.0
    env_delta: float = 0.04
    env_gamma: float = 0.02
    env_r: float = 4.0

    def __post_init__(self) -> None:
        if self.initial_uc_fraction + self.initial_cc_fraction > 1.0:
            raise ValueError(
                f"initial_uc_fraction + initial_cc_fraction = "
                f"{self.initial_uc_fraction + self.initial_cc_fraction:.3f} > 1.0"
            )


DEFAULT_CONFIG = ModelConfig()

# Paper-calibrated preset: threshold = 75% of max pool (5 agents × 1.0 contribution),
# disaster_prob = 40% (main stochastic treatment from Jonsson & Jonsson 2025), full wealth loss.
PAPER_CONFIG = ModelConfig(
    threshold=3.75,
    disaster_prob=0.4,
    loss_fraction=1.0,
    income=2.0,
    initial_uc_fraction=0.33,
    initial_cc_fraction=0.33,
)
