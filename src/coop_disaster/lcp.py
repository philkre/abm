"""Linear Contribution Profile: single-agent contribution update rule."""

from coop_disaster.types import PlayerType, SimConfig


def contribution(player_type: PlayerType, others_mean: float, cfg: SimConfig) -> float:
    """Compute one agent's contribution given the mean contribution of others.

    LCP rule: alpha + beta * others_mean, clamped to [0, endowment].

    Args:
        player_type: UC, CC, or FR.
        others_mean: Mean contribution of the other group members last round.
        cfg: Simulation config supplying LCP params and endowment cap.

    Returns:
        Contribution in [0, cfg.endowment].
    """
    p = cfg.lcp[player_type]
    return max(0.0, min(cfg.endowment, p.alpha + p.beta * others_mean))
