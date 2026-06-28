"""ModelParams dataclass and strategy/risk-mode constants."""

from dataclasses import dataclass, asdict
import hashlib
import json

# Strategy integer codes — used throughout as int8 arrays
D = 0
UC = 1
CC = 2

# Risk function modes
LINEAR = "linear"
SIGMOID = "sigmoid"


@dataclass(frozen=True)
class ModelParams:
    # Structural
    L: int = 150
    n_gens: int = 1500
    measure_window: int = 200  # final window for summary statistics
    env_update_every: int = 1  # τ: environment clock (1 = every generation)

    # Game
    c_bar: float = 0.75  # cooperator contribution (E = 1.0 as unit)
    T: float = 3.75  # threshold = 0.75 * 5 * E
    R: float = 0.0  # public-good multiplier; 0 = pure cost
    w0: float = 1.0  # initial wealth
    mu: float = 0.01  # mutation rate

    # Wealth process
    # "ou": Wiener-with-drift — additive income b, fractional flood loss
    #       (mean-reverting → Ornstein–Uhlenbeck), optional Gaussian shock sigma.
    # "multiplicative": legacy (1+g)·w growth.
    wealth_mode: str = "ou"
    b: float = 1.0  # OU additive income drift (E units)
    sigma: float = 0.0  # OU idiosyncratic volatility (per-round Gaussian shock)
    g: float = 0.015  # multiplicative wealth growth rate (Kolen); mult mode only

    # Risk
    risk_mode: str = LINEAR
    p_max: float = 0.5  # maximum disaster probability
    k: float = 5.0  # sigmoid steepness
    e0: float = 0.0  # sigmoid midpoint
    ell: float = 0.34  # loss fraction (Kolen)
    p_min: float = 0.0  # optional baseline probability floor

    # Environment / feedback
    delta: float = 0.03  # improvement rate per cooperator
    gamma: float = 0.03  # degradation rate per defector
    eta: float = 0.0  # flood-damage rate (0 = MVP / plain Ding)
    kappa: float = 0.2  # fitness discount rate

    # Imitation
    beta: float = 2.0  # Fermi selection strength

    # Loss aversion (CC only; λ_i distribution)
    lambda_mode: str = "homogeneous"  # "homogeneous" | "lognormal" | "uniform"
    lambda_mean: float = 1.0  # 1.0 = risk-neutral; 2.25 = K-T mean
    lambda_sigma: float = 0.5  # log-normal σ (shape); headline value from K-T literature
    lambda_max: float = 4.0  # upper bound for uniform draw

    # Flags
    well_mixed: bool = False  # True → every agent's group is the whole population
    frozen_strategies: bool = False  # True → no Fermi, no mutation (Jonsson validation)
    initial_mix: str = "equal"  # "equal" (UC/D 50-50) | "thirds" (UC/CC/D equal)

    # Explicit initial strategy fractions (used when initial_mix == "fractions").
    # initial_d_frac is implied as 1 - initial_uc_frac - initial_cc_frac.
    initial_uc_frac: float = 0.0
    initial_cc_frac: float = 0.0

    def hash(self) -> str:
        """12-char hex digest; stable across Python runs."""
        d = json.dumps(asdict(self), sort_keys=True)
        return hashlib.md5(d.encode()).hexdigest()[:12]
