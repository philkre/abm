"""Configuration for the spatial threshold public goods game."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelConfig:
    """Immutable configuration for SpatialCollectiveRiskModel.

    Args:
        grid_size: Side length of the square lattice (N = grid_size²).
        initial_uc_fraction: Probability each agent starts as UC.
        initial_wealth: Starting wealth for every agent.
        contribution: Amount UC agents pay into the pool each round.
        threshold: Pool sum required to avert disaster for a focal group.
        disaster_prob: Probability of loss when pool < threshold.
        loss_fraction: Fraction of post-contribution wealth lost in a disaster.
        beta: Fermi selection strength (higher → more deterministic imitation).
        mu: Per-agent mutation probability each step.
        n_steps: Default number of simulation steps for run.py.
        seed: RNG seed (passed to Mesa's Model for full reproducibility).
    """

    grid_size: int = 20
    initial_uc_fraction: float = 0.5
    initial_wealth: float = 10.0
    contribution: float = 1.0
    threshold: float = 3.0
    disaster_prob: float = 0.5
    loss_fraction: float = 0.5
    beta: float = 1.0
    mu: float = 0.001
    n_steps: int = 500
    seed: int = 42


DEFAULT_CONFIG = ModelConfig()
