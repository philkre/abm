"""Group-level simulation: type assignment and LCP dynamics via Mesa.

Corresponds to condcoop's Distribution, Group, and Simulation classes.
"""

import random

import mesa

from coop_disaster.lcp import contribution
from coop_disaster.types import PlayerType, SimConfig


class PlayerAgent(mesa.Agent):
    """One participant in the threshold public goods game.

    Corresponds to condcoop's Player subclasses (UnconditionalCooperator, etc.).

    Attributes:
        player_type: UC, CC, or FR archetype.
        contribution: Current contribution value, updated each step.
    """

    def __init__(self, model: "DisasterGroupModel", player_type: PlayerType) -> None:
        super().__init__(model)
        self.player_type = player_type
        self.contribution: float = model.cfg.lcp[player_type].init


class DisasterGroupModel(mesa.Model):
    """ABM for one group's LCP dynamics over n_rounds steps.

    Corresponds to condcoop's Group. Uses simultaneous activation so every agent
    reads last round's contributions before any agent updates — fixing the bug in
    condcoop's _get_others_contributions, which accidentally used self.last_contribution
    instead of other_player.last_contribution.

    Args:
        types: One PlayerType per group member.
        cfg: Simulation configuration.
    """

    def __init__(self, types: list[PlayerType], cfg: SimConfig) -> None:
        super().__init__()
        self.cfg = cfg
        for t in types:
            PlayerAgent(self, t)

    def step(self) -> None:
        """One round: snapshot contributions, then update all agents simultaneously."""
        agents = list(self.agents)
        prev = [a.contribution for a in agents]
        for i, agent in enumerate(agents):
            others_mean = sum(prev[:i] + prev[i + 1 :]) / (len(prev) - 1)
            agent.contribution = contribution(agent.player_type, others_mean, self.cfg)

    def run(self) -> bool:
        """Run n_rounds and return True if the final group total meets the threshold.

        Returns:
            True if sum of final contributions >= cfg.threshold.
        """
        for _ in range(self.cfg.n_rounds):
            self.step()
        return sum(a.contribution for a in self.agents) >= self.cfg.threshold


def assign_types(uc_prop: float, cfg: SimConfig, rng: random.Random) -> list[PlayerType]:
    """Randomly draw player types for one group given UC proportion.

    Corresponds to condcoop's Distribution.sample_group().

    Args:
        uc_prop: Fraction of players assigned as UC (0–1).
        cfg: Config supplying group_size and cc_fr_ratio.
        rng: RNG instance (allows seeding for reproducibility).

    Returns:
        List of length cfg.group_size with PlayerType values.
    """
    cc_prop = (1.0 - uc_prop) * cfg.cc_fr_ratio / (cfg.cc_fr_ratio + 1.0)
    types: list[PlayerType] = []
    for _ in range(cfg.group_size):
        r = rng.random()
        if r < uc_prop:
            types.append(PlayerType.UC)
        elif r < uc_prop + cc_prop:
            types.append(PlayerType.CC)
        else:
            types.append(PlayerType.FR)
    return types


def simulate_group(types: list[PlayerType], cfg: SimConfig) -> bool:
    """Run one group via Mesa and return whether the threshold was met.

    Args:
        types: Player types for each group member.
        cfg: Config supplying n_rounds, threshold, endowment, and LCP params.

    Returns:
        True if sum of final contributions >= cfg.threshold.
    """
    return DisasterGroupModel(types, cfg).run()
