"""Figures from saved data only — no model code in this module.

All plot functions read from results/ via analysis.py and save PDFs to
results/figures/. Call `uv run spatcoop analyse` before plotting.
"""

from __future__ import annotations
import json
import math
import warnings
from dataclasses import replace
from pathlib import Path
from typing import Sequence

from matplotlib.figure import Figure
import numpy as np
import matplotlib

matplotlib.use("Agg")  # headless-safe backend
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from spatcoop.params import ModelParams
from spatcoop.model import OBS_KEYS, RunResult
from spatcoop.runner import load_result, result_path
from spatcoop.analysis import (
    load_all_results,
    summary_table,
    coop_fraction_timeseries,
)

FIGURES_DIR = Path("results/figures")

# Canonical order-parameter list for the grid plots (every per-gen observable).
ALL_OPS: tuple[str, ...] = OBS_KEYS


def _save(fig: Figure, name: str) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / name
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  saved → {path}")
    return path


def _grid_axes(n: int, ncols: int = 4) -> tuple[Figure, np.ndarray]:
    """Create a grid of subplots sized for n panels; hide any unused axes."""
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.4 * ncols, 2.6 * nrows), squeeze=False)
    flat = axes.ravel()
    for ax in flat[n:]:
        ax.axis("off")
    return fig, flat


# ─────────────────────────────────────────────────────────────────────────────
# ts_coop.pdf — cooperation fraction over time
# ─────────────────────────────────────────────────────────────────────────────


def plot_ts_coop(
    params_list: Sequence[ModelParams],
    seeds: Sequence[int],
    labels: Sequence[str] | None = None,
) -> Path:
    """Mean (UC+CC)/L² over time for each parameter set."""
    fig, ax = plt.subplots(figsize=(7, 4))
    colors = cm.tab10(np.linspace(0, 0.7, len(params_list)))

    for idx, p in enumerate(params_list):
        results = [load_result(result_path(p, s)) for s in seeds]
        ts = coop_fraction_timeseries(results, p.L)
        label = labels[idx] if labels else f"run {idx}"
        ax.plot(ts, color=colors[idx], label=label, lw=1.5)

    ax.set_xlabel("Generation")
    ax.set_ylabel("Cooperation fraction (UC+CC)")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=8)
    ax.set_title("Cooperation over time")
    fig.tight_layout()
    return _save(fig, "ts_coop.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# ts_wealth.pdf — mean wealth over time
# ─────────────────────────────────────────────────────────────────────────────


def plot_ts_wealth(
    p: ModelParams,
    seeds: Sequence[int],
) -> Path:
    """Mean wealth averaged over seeds, with flood-rate shade."""
    results = [load_result(result_path(p, s)) for s in seeds]
    w = np.mean([r.timeseries["mean_wealth"] for r in results], axis=0)
    fr = np.mean([r.timeseries["flood_rate"] for r in results], axis=0)

    fig, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(w, color="steelblue", lw=1.5, label="mean wealth")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Mean wealth", color="steelblue")

    ax2 = ax1.twinx()
    ax2.fill_between(range(len(fr)), fr, alpha=0.25, color="tomato", label="flood rate")
    ax2.set_ylabel("Flood rate", color="tomato")
    ax2.set_ylim(0, 1)

    fig.legend(loc="upper right", bbox_to_anchor=(0.9, 0.88), fontsize=8)
    ax1.set_title("Wealth dynamics")
    fig.tight_layout()
    return _save(fig, "ts_wealth.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# phase_linear.pdf — resilience in (β, p_max) plane
# ─────────────────────────────────────────────────────────────────────────────


def plot_phase_linear(
    params_list: Sequence[ModelParams],
    seeds: Sequence[int],
) -> Path:
    """Heat-map of resilience (fraction groups above threshold) in β-p_max space."""
    results = load_all_results(params_list, seeds)
    tbl = summary_table(results, keys=["resilience"])
    resil = tbl[:, 0]

    betas = sorted(set(p.beta for p in params_list))
    pmaxes = sorted(set(p.p_max for p in params_list))

    Z = np.full((len(pmaxes), len(betas)), np.nan)
    beta_idx = {b: i for i, b in enumerate(betas)}
    pmax_idx = {m: i for i, m in enumerate(pmaxes)}

    for p, r in zip(params_list, resil):
        Z[pmax_idx[p.p_max], beta_idx[p.beta]] = r

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(
        Z,
        origin="lower",
        aspect="auto",
        vmin=0,
        vmax=1,
        extent=[min(betas), max(betas), min(pmaxes), max(pmaxes)],
        cmap="RdYlGn",
    )
    plt.colorbar(im, ax=ax, label="Resilience")
    ax.set_xlabel("β (selection strength)")
    ax.set_ylabel("p_max (max flood probability)")
    ax.set_title("Resilience phase diagram (linear risk)")
    fig.tight_layout()
    return _save(fig, "phase_linear.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# sa_bar_linear.pdf / sa_bar_sigmoid.pdf — Sobol indices bar chart
# ─────────────────────────────────────────────────────────────────────────────


def plot_sobol_bar(phase: str = "linear", N: int = 512) -> Path:
    """S1 and ST bar chart for the given phase and sample size."""
    path = Path(f"results/sa/sobol_{phase}_N{N}.json")
    Si = json.loads(path.read_text())

    names = Si["names"]
    S1 = np.array(Si["S1"])
    ST = np.array(Si["ST"])
    S1_ci = np.array(Si["S1_conf"])
    ST_ci = np.array(Si["ST_conf"])

    x = np.arange(len(names))
    w = 0.35
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(x - w / 2, S1, w, yerr=S1_ci, label="S1", color="steelblue", capsize=4, error_kw={"lw": 1})
    ax.bar(x + w / 2, ST, w, yerr=ST_ci, label="ST", color="coral", capsize=4, error_kw={"lw": 1})
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Sobol index")
    ax.set_ylim(0, min(1.0, max(ST) * 1.3 + 0.05))
    ax.legend()
    ax.set_title(f"Sobol sensitivity — {phase} risk (N={N})")
    fig.tight_layout()
    fname = f"sa_bar_{phase}.pdf"
    return _save(fig, fname)


# ─────────────────────────────────────────────────────────────────────────────
# spatial_snapshot.pdf — strategy lattice at multiple time points
# ─────────────────────────────────────────────────────────────────────────────


def plot_spatial_snapshot(
    p: ModelParams,
    seed: int = 0,
    snap_gens: Sequence[int] = (500, 1000, 1500),
) -> Path:
    """
    Re-run a single episode collecting strategy snapshots at specified
    generations, then save a multi-panel figure.
    Snapshots are collected inside run_episode via a patched observer.
    """
    from spatcoop.model import _init_state, _step
    import numpy as np

    rng = np.random.default_rng(seed)
    state = _init_state(p, rng)
    snaps = []
    snap_set = set(snap_gens)

    for gen in range(p.n_gens):
        state, _ = _step(state, p, rng, gen)
        if gen + 1 in snap_set:
            snaps.append((gen + 1, state["strategy"].copy()))

    n = len(snaps)
    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]

    cmap = matplotlib.colors.ListedColormap(["#e74c3c", "#2ecc71", "#3498db"])
    bounds = [-0.5, 0.5, 1.5, 2.5]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    for ax, (gen, strat) in zip(axes, snaps):
        ax.imshow(strat, cmap=cmap, norm=norm, interpolation="nearest")
        ax.set_title(f"Gen {gen}")
        ax.axis("off")

    # Legend patches
    import matplotlib.patches as mpatches

    labels = ["D (defector)", "UC (unconditional)", "CC (conditional)"]
    colors = ["#e74c3c", "#2ecc71", "#3498db"]
    patches = [mpatches.Patch(color=c, label=lb) for c, lb in zip(colors, labels)]
    fig.legend(handles=patches, loc="lower center", ncol=3, fontsize=8, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Strategy spatial distribution", y=1.02)
    fig.tight_layout()
    return _save(fig, "spatial_snapshot.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# op_timeseries.pdf — every order parameter over time, mean ± across-seed σ
# ─────────────────────────────────────────────────────────────────────────────


def plot_op_timeseries(
    p: ModelParams,
    seeds: Sequence[int],
    keys: Sequence[str] = ALL_OPS,
    name: str = "op_timeseries.pdf",
) -> Path:
    """Grid of OP timeseries: per key, mean over seeds with a ±1σ shaded band."""
    results = [load_result(result_path(p, s)) for s in seeds]
    fig, axes = _grid_axes(len(keys))

    for ax, key in zip(axes, keys):
        stack = np.array([r.timeseries[key] for r in results], dtype=np.float64)  # (n_seeds, n_gens)
        with np.errstate(invalid="ignore"), warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)  # all-NaN slices (absent strategy)
            mean = np.nanmean(stack, axis=0)
            std = np.nanstd(stack, axis=0)
        gens = np.arange(mean.shape[0])
        ax.plot(gens, mean, color="steelblue", lw=1.2)
        ax.fill_between(gens, mean - std, mean + std, color="steelblue", alpha=0.25, lw=0)
        ax.set_title(key, fontsize=9)
        ax.tick_params(labelsize=7)

    fig.suptitle(f"Order parameters over time (mean ± σ, {len(seeds)} seeds)", y=1.005)
    fig.tight_layout()
    return _save(fig, name)


# ─────────────────────────────────────────────────────────────────────────────
# op_vs_<param>.pdf — average order parameter vs a swept parameter
# ─────────────────────────────────────────────────────────────────────────────


def plot_op_vs_param(
    param_name: str,
    values: Sequence[float],
    base: ModelParams,
    seeds: Sequence[int],
    keys: Sequence[str] = ALL_OPS,
    name: str | None = None,
) -> Path:
    """Grid of avg-OP (y) vs swept parameter value (x). Results must be on disk.

    One panel per OP; the y value is the final-window summary mean averaged over
    seeds (uses summary_table). Drives the λ and wealth/income sweep figures.
    """
    params_list = [replace(base, **{param_name: float(v)}) for v in values]
    results = load_all_results(params_list, seeds)
    tbl = summary_table(results, keys=list(keys))  # (n_values, n_keys)

    fig, axes = _grid_axes(len(keys))
    for j, (ax, key) in enumerate(zip(axes, keys)):
        ax.plot(values, tbl[:, j], marker="o", ms=3, lw=1.2, color="darkorange")
        ax.set_title(key, fontsize=9)
        ax.set_xlabel(param_name, fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(True, alpha=0.3)

    fig.suptitle(f"Order parameters vs {param_name}", y=1.005)
    fig.tight_layout()
    return _save(fig, name or f"op_vs_{param_name}.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# sa_<method>_<key>.pdf — sensitivity indices for the custom SA workflow
# ─────────────────────────────────────────────────────────────────────────────


def plot_sa_indices(out_dir: Path | str, method: str, key: str) -> Path:
    """Bar chart of SA indices from results/sa/<...>/{method}_{key}.json.

    sobol → grouped first-order S1 and total-order ST bars (with conf bars).
    pawn  → median KS bars with [min, max] whiskers.
    morris/delta → mu* / δ bars with conf bars.
    """
    out_dir = Path(out_dir)
    result = json.loads((out_dir / f"{method}_{key}.json").read_text())
    names = result["problem"]["names"]
    x = np.arange(len(names))

    fig, ax = plt.subplots(figsize=(max(5, 1.1 * len(names)), 4))

    if method == "sobol":
        w = 0.38
        ax.bar(
            x - w / 2,
            result["S1"],
            w,
            yerr=result["S1_conf"],
            capsize=3,
            label="S1 (first-order)",
            color="steelblue",
            error_kw={"lw": 1},
        )
        ax.bar(
            x + w / 2,
            result["ST"],
            w,
            yerr=result["ST_conf"],
            capsize=3,
            label="ST (total-order)",
            color="coral",
            error_kw={"lw": 1},
        )
        ax.set_ylabel("Sobol index")
        ax.legend()
    elif method == "pawn":
        lo = np.array(result["KS"]) - np.array(result["KS_min"])
        hi = np.array(result["KS_max"]) - np.array(result["KS"])
        ax.bar(x, result["KS"], 0.6, yerr=[lo, hi], capsize=3, color="mediumseagreen", error_kw={"lw": 1})
        ax.set_ylabel("PAWN KS (median; whiskers = min/max)")
    elif method == "morris":
        ax.bar(
            x,
            result["mu_star"],
            0.6,
            yerr=result["mu_star_conf"],
            capsize=3,
            color="slateblue",
            error_kw={"lw": 1},
        )
        ax.set_ylabel("Morris μ*")
    elif method == "delta":
        ax.bar(
            x,
            result["delta"],
            0.6,
            yerr=result["delta_conf"],
            capsize=3,
            color="indianred",
            error_kw={"lw": 1},
        )
        ax.set_ylabel("Borgonovo δ")
    else:
        raise ValueError(f"Unknown method {method!r}")

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=30, ha="right")
    ax.set_title(f"{method.upper()} sensitivity — {key}")
    fig.tight_layout()
    return _save(fig, f"sa_{method}_{key}.pdf")


# ─────────────────────────────────────────────────────────────────────────────
# snapshot_fields.pdf — saved per-cell lattices (strategy / wealth / env)
# ─────────────────────────────────────────────────────────────────────────────


def plot_snapshot_fields(r: RunResult, name: str = "snapshot_fields.pdf") -> Path:
    """Render saved snapshot lattices: rows = {strategy, wealth, env},
    cols = the snapshot generations. Requires a RunResult with .snapshots."""
    if not r.snapshots:
        raise ValueError("RunResult has no snapshots (run with snapshot_every set).")

    snaps = r.snapshots
    gens = [int(g) for g in snaps["gens"]]
    n = len(gens)

    strat_cmap = matplotlib.colors.ListedColormap(["#e74c3c", "#2ecc71", "#3498db"])
    strat_norm = matplotlib.colors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5], strat_cmap.N)

    rows = [
        ("strategy", snaps["strategy"], strat_cmap, strat_norm, None),
        ("wealth", snaps["wealth"], "viridis", None, "Wealth"),
        ("env", snaps["env"], "BrBG", None, "Env (−1…1)"),
    ]

    fig, axes = plt.subplots(len(rows), n, figsize=(3 * n, 3 * len(rows)), squeeze=False)
    for i, (label, stack, cmap, norm, cbar_label) in enumerate(rows):
        vmin = -1.0 if label == "env" else None
        vmax = 1.0 if label == "env" else None
        for j, gen in enumerate(gens):
            ax = axes[i][j]
            im = ax.imshow(stack[j], cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, interpolation="nearest")
            ax.axis("off")
            if i == 0:
                ax.set_title(f"gen {gen}", fontsize=9)
            if j == 0:
                ax.text(
                    -0.08,
                    0.5,
                    label,
                    transform=ax.transAxes,
                    rotation=90,
                    va="center",
                    ha="right",
                    fontsize=10,
                )
        if cbar_label is not None:
            fig.colorbar(im, ax=axes[i].tolist(), fraction=0.046, pad=0.02, label=cbar_label)

    fig.suptitle("Snapshot fields over the measure window", y=1.0)
    return _save(fig, name)
