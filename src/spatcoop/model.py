"""run_episode — one complete model run returning a RunResult."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import label
from tqdm import tqdm

from spatcoop.params import ModelParams, D, UC, CC, LINEAR
from spatcoop.kernel import focal_sum, fermi_step

# Per-generation observables, in a single canonical order. run_episode builds its
# timeseries dict from this list; _observe must return exactly these keys.
OBS_KEYS: tuple[str, ...] = (
    "n_D",
    "n_UC",
    "n_CC",
    "mean_wealth",
    "flood_rate",
    "mean_env",
    "resilience",
    "env_std",
    "mean_pool_gap",
    "near_miss_frac",
    "gini_wealth",
    "cc_contrib_frac",
    # Extended (fitness/payoff, cooperation, clustering, heterogeneity)
    "mean_fitness",
    "mean_payoff",
    "coop_frac",
    "mean_contrib",
    "wealth_D",
    "wealth_UC",
    "wealth_CC",
    "p_span_D",
    "p_span_UC",
    "p_span_CC",
    "max_cluster_D",
    "max_cluster_UC",
    "max_cluster_CC",
    "interface_density",
)

# ── Output types ──────────────────────────────────────────────────────────────


@dataclass
class RunResult:
    params: ModelParams
    seed: int
    timeseries: dict  # keys from _observe; values: (n_gens,) float32 arrays
    summary: dict  # final-window means + std + moran_i
    completed: bool = True
    # Optional per-cell lattice snapshots over the measure window (dedicated
    # plotting runs only). Keys: gens (int), strategy/wealth/env/phi → (n,L,L).
    snapshots: dict | None = None


# ── Initialisation ────────────────────────────────────────────────────────────


def _draw_lambda(p: ModelParams, L: int, rng: np.random.Generator) -> np.ndarray:
    """Draw the loss-aversion field λ_i for all cells."""
    if p.lambda_mode == "homogeneous":
        return np.full((L, L), p.lambda_mean, dtype=np.float32)
    elif p.lambda_mode == "lognormal":
        # Match mean = lambda_mean via log-normal parameterisation
        mu = np.log(p.lambda_mean) - 0.5 * p.lambda_sigma**2
        return rng.lognormal(mu, p.lambda_sigma, (L, L)).astype(np.float32)
    elif p.lambda_mode == "uniform":
        return rng.uniform(1.0, p.lambda_max, (L, L)).astype(np.float32)
    else:
        raise ValueError(f"Unknown lambda_mode: {p.lambda_mode!r}")


def _init_state(p: ModelParams, rng: np.random.Generator) -> dict:
    L = p.L
    if p.initial_mix == "equal":
        strategy = rng.choice([D, UC], size=(L, L)).astype(np.int8)
    elif p.initial_mix == "thirds":
        strategy = rng.choice([D, UC, CC], size=(L, L)).astype(np.int8)
    else:
        raise ValueError(f"Unknown initial_mix: {p.initial_mix!r}")

    return dict(
        strategy=strategy,
        env=np.zeros((L, L), dtype=np.float32),
        wealth=np.full((L, L), p.w0, dtype=np.float32),
        phi=np.zeros((L, L), dtype=np.float32),
        prev_c=np.zeros((L, L), dtype=np.float32),  # CC lagged contributions
        contrib=np.zeros((L, L), dtype=np.float32),
        lam=_draw_lambda(p, L, rng),
    )


# ── Per-generation step ───────────────────────────────────────────────────────


def _flood_prob(env: np.ndarray, p: ModelParams) -> np.ndarray:
    if p.risk_mode == LINEAR:
        prob = p.p_max * (1.0 - env) / 2.0
    else:  # SIGMOID
        prob = p.p_max / (1.0 + np.exp(p.k * (env - p.e0)))
    return np.clip(prob + p.p_min, p.p_min, 1.0).astype(np.float32)


def _step(state: dict, p: ModelParams, rng: np.random.Generator, gen: int) -> tuple[dict, dict]:
    """Advance state by one generation. Mutates state in-place; also returns it."""
    s = state["strategy"]
    e = state["env"]
    w = state["wealth"]
    phi = state["phi"]
    lam = state["lam"]
    L = p.L

    # ── Step 1: Contributions ─────────────────────────────────────────────────
    p_i = _flood_prob(e, p)

    # Latch previous round's contributions for CC before overwriting
    state["prev_c"] = state["contrib"].copy()
    prev_c = state["prev_c"]

    contrib = np.zeros((L, L), dtype=np.float32)
    contrib[s == UC] = p.c_bar

    if np.any(s == CC):
        nbr_mean = (
            np.roll(prev_c, 1, axis=0)
            + np.roll(prev_c, -1, axis=0)
            + np.roll(prev_c, 1, axis=1)
            + np.roll(prev_c, -1, axis=1)
        ) / 4.0
        # Loss-averse premium; zero when λ_i = 1
        premium = (lam - 1.0) * p_i * p.ell * w / 5.0
        cc_contrib = np.clip(nbr_mean + premium, 0.0, p.c_bar)
        contrib[s == CC] = cc_contrib[s == CC]

    state["contrib"] = contrib

    # ── Step 2: Pool ──────────────────────────────────────────────────────────
    if p.well_mixed:
        # Every cell sees the same total contribution scaled to group size 5
        total = contrib.sum()
        pool_val = total * 5.0 / (L * L)
        pool = np.full((L, L), pool_val, dtype=np.float32)
    else:
        pool = focal_sum(contrib)

    # ── Step 4: Flood check ───────────────────────────────────────────────────
    exposed = pool < p.T
    flood_draw = rng.random((L, L), dtype=np.float32) < p_i
    disaster = (exposed & flood_draw).astype(np.float32)

    # ── Step 5: Wealth and fitness ────────────────────────────────────────────
    pg_return = p.R * pool / 5.0
    w_before = w.copy()
    loss = disaster * p.ell * w

    if p.wealth_mode == "ou":
        # Wiener-process-with-drift wealth: additive income b minus contribution
        # minus fractional flood loss (mean-reverting → Ornstein–Uhlenbeck),
        # plus an optional idiosyncratic Gaussian shock.
        w_new = w + p.b - contrib - loss + pg_return
        if p.sigma > 0.0:
            w_new = w_new + rng.normal(0.0, p.sigma, (L, L)).astype(np.float32)
        pi = p.b - contrib - disaster * p.ell * w_before + pg_return
    elif p.wealth_mode == "multiplicative":
        w_new = (1.0 + p.g) * w - contrib - loss + pg_return
        pi = p.g * w_before - contrib - disaster * p.ell * w_before + pg_return
    else:
        raise ValueError(f"Unknown wealth_mode: {p.wealth_mode!r}")

    w_new = np.maximum(w_new, 0.0)
    phi_new = (1.0 - p.kappa) * phi + pi

    state["wealth"] = w_new
    state["phi"] = phi_new

    # ── Step 6: Environment update (every τ generations) ─────────────────────
    if gen % p.env_update_every == 0:
        maint = focal_sum(contrib) / p.c_bar  # m_j^+: in [0, 5]
        neglect = 5.0 - maint  # m_j^-
        flood_group = focal_sum(disaster)  # Σ_{k ∈ G_j} d_k (A+ damage)

        delta_e = p.delta * maint - p.gamma * neglect - p.eta * flood_group
        state["env"] = np.clip(e + delta_e, -1.0, 1.0)

    # ── Step 7: Fermi strategy update ─────────────────────────────────────────
    if not p.frozen_strategies:
        s_new = fermi_step(s, phi_new, p.beta, rng)

        # ── Step 8: Mutation ──────────────────────────────────────────────────
        n_strategies = 2 if p.initial_mix == "equal" else 3
        mutate_mask = rng.random((L, L), dtype=np.float32) < p.mu
        random_strats = rng.integers(0, n_strategies, (L, L), dtype=np.int8)
        s_new[mutate_mask] = random_strats[mutate_mask]

        state["strategy"] = s_new

    obs = _observe(state, pool, disaster, pi, p)
    return state, obs


def _observe(state: dict, pool: np.ndarray, disaster: np.ndarray, pi: np.ndarray, p: ModelParams) -> dict:
    s = state["strategy"]
    w = state["wealth"]
    e = state["env"]
    phi = state["phi"]  # discounted fitness φ (post-update)
    contrib = state["contrib"]

    d_mask, uc_mask, cc_mask = s == D, s == UC, s == CC

    def _masked_mean(arr: np.ndarray, mask: np.ndarray) -> float:
        return float(arr[mask].mean()) if mask.any() else float("nan")

    cc_contrib_frac = float(contrib[cc_mask].mean() / p.c_bar) if cc_mask.any() else float("nan")

    span_d, max_d = _cluster_stats(d_mask)
    span_uc, max_uc = _cluster_stats(uc_mask)
    span_cc, max_cc = _cluster_stats(cc_mask)

    return {
        "n_D": int(d_mask.sum()),
        "n_UC": int(uc_mask.sum()),
        "n_CC": int(cc_mask.sum()),
        "mean_wealth": float(w.mean()),
        "flood_rate": float(disaster.mean()),
        "mean_env": float(e.mean()),
        "resilience": float((pool >= p.T).mean()),
        # Extended order parameters
        "env_std": float(e.std()),
        "mean_pool_gap": float(np.maximum(p.T - pool, 0.0).mean() / p.T),
        "near_miss_frac": float(((pool >= 0.9 * p.T) & (pool < p.T)).mean()),
        "gini_wealth": _gini(w),
        "cc_contrib_frac": cc_contrib_frac,
        # Fitness / payoff (previously computed but discarded)
        "mean_fitness": float(phi.mean()),
        "mean_payoff": float(pi.mean()),
        # Cooperation / contribution
        "coop_frac": float((uc_mask.sum() + cc_mask.sum()) / s.size),
        "mean_contrib": float(contrib.mean() / p.c_bar),
        # Mean wealth by strategy
        "wealth_D": _masked_mean(w, d_mask),
        "wealth_UC": _masked_mean(w, uc_mask),
        "wealth_CC": _masked_mean(w, cc_mask),
        # Per-strategy spanning-cluster probability (fraction of cells in a
        # spanning same-strategy cluster) and largest-cluster fraction
        "p_span_D": span_d,
        "p_span_UC": span_uc,
        "p_span_CC": span_cc,
        "max_cluster_D": max_d,
        "max_cluster_UC": max_uc,
        "max_cluster_CC": max_cc,
        # Spatial disorder: fraction of neighbour pairs with differing strategy
        "interface_density": _interface_density(s),
    }


# ── Cluster / spatial-pattern statistics ──────────────────────────────────────


def _cluster_stats(mask: np.ndarray) -> tuple[float, float]:
    """Spanning-cluster cell fraction and largest-cluster fraction for one strategy.

    Connected components are 4-connected (Von Neumann). A component "spans" if it
    touches both opposite borders (top/bottom or left/right) — an edge proxy for
    percolation on the torus. Both outputs are normalised by L².
    Returns (span_fraction, largest_fraction); (0, 0) when the strategy is absent.
    """
    if not mask.any():
        return 0.0, 0.0
    lab, n = label(mask)
    if n == 0:
        return 0.0, 0.0
    sizes = np.bincount(lab.ravel())[1:]  # drop background label 0
    largest = float(sizes.max()) / mask.size

    spanning = ((set(lab[0]) & set(lab[-1])) | (set(lab[:, 0]) & set(lab[:, -1]))) - {0}
    span_cells = float(np.isin(lab, list(spanning)).sum()) / mask.size if spanning else 0.0
    return span_cells, largest


def _interface_density(s: np.ndarray) -> float:
    """Fraction of Von Neumann neighbour pairs (right + down on the torus) that
    differ in strategy. 0 = single domain, →1 = fully mixed."""
    diff = (s != np.roll(s, -1, axis=1)).sum() + (s != np.roll(s, -1, axis=0)).sum()
    return float(diff) / (2 * s.size)


# ── Gini coefficient ──────────────────────────────────────────────────────────


def _gini(w: np.ndarray) -> float:
    """Gini coefficient of the wealth distribution (0 = equal, 1 = maximal inequality)."""
    flat = w.ravel().astype(np.float64)
    total = flat.sum()
    if total == 0.0:
        return 0.0
    flat = np.sort(flat)
    n = len(flat)
    idx = np.arange(1, n + 1, dtype=np.float64)
    return float((2.0 * (idx * flat).sum()) / (n * total) - (n + 1.0) / n)


# ── Moran's I ─────────────────────────────────────────────────────────────────


def _moran_i(strategy: np.ndarray) -> float:
    """Spatial autocorrelation of UC indicator. O(L²) via rolling sums."""
    x = (strategy == UC).astype(np.float32)
    x_mean = float(x.mean())
    x_dev = x - x_mean
    x_lag = (
        np.roll(x, 1, axis=0) + np.roll(x, -1, axis=0) + np.roll(x, 1, axis=1) + np.roll(x, -1, axis=1)
    ) / 4.0
    num = float((x_dev * (x_lag - x_mean)).sum())
    denom = float((x_dev**2).sum())
    return float(num / denom) if denom > 0 else 0.0


# ── Top-level entry point ─────────────────────────────────────────────────────


def run_episode(
    p: ModelParams,
    seed: int,
    progress: bool = False,
    snapshot_every: int | None = None,
) -> RunResult:
    """Run one complete model episode and return a RunResult.

    snapshot_every: if set, save per-cell lattice snapshots every this many gens
    within the final measure_window (dedicated plotting runs only; default off).
    """
    rng = np.random.default_rng(seed)
    state = _init_state(p, rng)
    ts: dict = {k: [] for k in OBS_KEYS}

    mw = p.measure_window
    snap_start = p.n_gens - mw  # first gen of the measure window
    snaps: dict[str, list] = {"gens": [], "strategy": [], "wealth": [], "env": [], "phi": []}

    for gen in tqdm(range(p.n_gens), desc=f"seed={seed}", unit="gen", disable=not progress):
        state, obs = _step(state, p, rng, gen)
        for k, v in obs.items():
            ts[k].append(v)
        if snapshot_every and gen >= snap_start and (gen - snap_start) % snapshot_every == 0:
            snaps["gens"].append(gen)
            snaps["strategy"].append(state["strategy"].copy())
            snaps["wealth"].append(state["wealth"].copy())
            snaps["env"].append(state["env"].copy())
            snaps["phi"].append(state["phi"].copy())

    ts = {k: np.array(v, dtype=np.float32) for k, v in ts.items()}

    summary: dict = {}
    for k in ts:
        arr = ts[k][-mw:]
        all_nan = np.all(np.isnan(arr))
        summary[k] = float("nan") if all_nan else float(np.nanmean(arr))
        summary[f"{k}_std"] = float("nan") if all_nan else float(np.nanstd(arr))

    summary["moran_i"] = _moran_i(state["strategy"])

    # Post-processed from full timeseries (no re-run needed)
    uc_arr = ts["n_UC"].astype(np.float32)
    diff = np.diff(uc_arr[len(uc_arr) // 2 :])
    signs = np.sign(diff[diff != 0])
    summary["uc_oscillation"] = float(np.sum(signs[1:] != signs[:-1])) if len(signs) > 1 else 0.0
    summary["uc_flip_rate"] = float(np.abs(np.diff(uc_arr[-mw:])).mean()) / float(p.L**2)
    # resilience_std is already provided by the per-key *_std loop above.

    snapshots = None
    if snapshot_every and snaps["gens"]:
        snapshots = {
            "gens": np.array(snaps["gens"], dtype=np.int32),
            "strategy": np.stack(snaps["strategy"]).astype(np.int8),
            "wealth": np.stack(snaps["wealth"]).astype(np.float32),
            "env": np.stack(snaps["env"]).astype(np.float32),
            "phi": np.stack(snaps["phi"]).astype(np.float32),
        }

    return RunResult(params=p, seed=seed, timeseries=ts, summary=summary, snapshots=snapshots)
