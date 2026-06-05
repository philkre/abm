"""Core types: player taxonomy, LCP parameters, and simulation config."""

from dataclasses import dataclass, field
from enum import Enum, auto


class PlayerType(Enum):
    """Three player archetypes from Jonsson & Jonsson (2025)."""

    UC = auto()  # Unconditional Cooperator
    CC = auto()  # Conditional Cooperator
    FR = auto()  # Free-Rider


@dataclass(frozen=True)
class LcpParams:
    """Linear Contribution Profile parameters for one player type.

    Args:
        init: First-round contribution (before any social information).
        alpha: LCP intercept.
        beta: LCP slope (response to others' mean contribution).
    """

    init: float
    alpha: float
    beta: float


# Empirical parameters averaged across 4 treatments from condcoop
# (github.com/markusrobertjonsson/condcoop, ref [53] in paper).
# Fixed point: x = alpha / (1 - beta) for a homogeneous group.
# UC: x ≈ 17.13, group total ≈ 68.5 > threshold 60 ✓
# CC: x ≈  6.06, group total ≈ 24.3
# FR: x ≈  4.74, group total ≈ 19.0
_DEFAULT_LCP: dict[PlayerType, LcpParams] = {
    PlayerType.UC: LcpParams(init=14.839736, alpha=17.599818, beta=-0.027274),
    PlayerType.CC: LcpParams(init=11.947847, alpha=0.815997, beta=0.865409),
    PlayerType.FR: LcpParams(init=9.678571, alpha=4.099742, beta=0.134343),
}


@dataclass(frozen=True)
class SimConfig:
    """Immutable simulation configuration threaded through all functions.

    Args:
        n_groups: Independent groups simulated per UC proportion value.
        n_rounds: LCP update rounds per group.
        group_size: Players per group.
        endowment: Per-player per-round endowment.
        threshold: Group contribution required to avoid disaster.
        cc_fr_ratio: CC:FR split among non-UC players (CC/FR ≈ 0.358/0.035 ≈ 10.2).
        lcp: Per-type LCP parameters.
    """

    n_groups: int = 1_000
    n_rounds: int = 200
    group_size: int = 4
    endowment: float = 20.0
    threshold: float = 60.0
    cc_fr_ratio: float = 10.2
    lcp: dict[PlayerType, LcpParams] = field(default_factory=lambda: _DEFAULT_LCP)


DEFAULT_CONFIG = SimConfig()
