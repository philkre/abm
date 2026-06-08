"""Agent definition for the spatial threshold public goods game."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mesa.discrete_space import CellAgent

if TYPE_CHECKING:
    from spatial.model import SpatialCollectiveRiskModel


class HouseholdAgent(CellAgent):
    """A household on the Von Neumann lattice.

    Pure data container — all simulation logic lives in the model.

    Attributes:
        strategy: "UC" (unconditional cooperator) or "D" (defector).
        wealth: Accumulated wealth; updated each round.
        contribution: Amount contributed this round (set by model).
        payoff: Signed wealth change this round (set by model; always <= 0).
        disaster: Whether this agent suffered a disaster loss this round.
    """

    def __init__(
        self,
        model: SpatialCollectiveRiskModel,
        strategy: str,
        wealth: float,
    ) -> None:
        super().__init__(model)
        self.strategy = strategy
        self.wealth = wealth
        self.contribution: float = 0.0
        self.payoff: float = 0.0
        self.disaster: bool = False
