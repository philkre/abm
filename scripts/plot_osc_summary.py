"""
Three-panel summary figure (gridspec layout):
  Top-left    — resilience time series at b=21 (3 seeds), showing oscillation
  Bottom-left — strategy shares (UC/CC/D) at b=21, seed-averaged
  Right       — dominant period (left y-axis) and mean EHI (right y-axis) vs income b

Usage:
    uv run python scripts/plot_osc_summary.py
    uv run python scripts/plot_osc_summary.py --n-seeds 15 --out results/osc_summary.png
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from joblib import Parallel, delayed

from spatcoop.params import ModelParams
from spatcoop.model import run_episode

BASE_PARAMS = dict(
    L=150,
    n_gens=1000,
    measure_window=400,
    p_max=1.0,
    ell=0.64,
    eta=0.005,
    delta=0.042,
    gamma=0.018,
    beta=1.8,
    kappa=0.1,
    mu=0.0104,
    w0=312.0,
    c_bar=0.83,
    T=1.7,
    sigma=3.0,
    initial_e=-1.0,
    initial_mix="thirds",
    lambda_mode="lognormal",
    lambda_mean=2.25,
)

B_REF = 21.0  # NetLogo reference


def _run_one(b: float, seed: int) -> dict:
    p = ModelParams(**{**BASE_PARAMS, "b": b})
    r = run_episode(p, seed=seed)
    s = r.summary
    L2 = p.L ** 2
    result = {
        "b": b,
        "seed": seed,
        "osc_period": s["osc_period"],
        "mean_env":   s["mean_env"],
        "timeseries_resilience": None,
        "timeseries_n_UC": None,
        "timeseries_n_CC": None,
        "timeseries_n_D":  None,
    }
    if b == B_REF:
        result["timeseries_resilience"] = r.timeseries["resilience"]
        result["timeseries_n_UC"] = r.timeseries["n_UC"] / L2
        result["timeseries_n_CC"] = r.timeseries["n_CC"] / L2
        result["timeseries_n_D"]  = r.timeseries["n_D"]  / L2
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--b-values", type=float, nargs="+",
                    default=[8, 11, 14, 17, 21, 26, 32, 40, 50])
    ap.add_argument("--n-seeds", type=int, default=15)
    ap.add_argument("--ts-seeds", type=int, nargs="+", default=[0, 1, 2],
                    help="seeds for left-panel time series (b=21 only)")
    ap.add_argument("--initial-e", type=float, default=-1.0)
    ap.add_argument("--out", type=str, default="results/osc_summary.png")
    args = ap.parse_args()

    BASE_PARAMS["initial_e"] = args.initial_e
    b_values = args.b_values
    if B_REF not in b_values:
        b_values = sorted(set(list(b_values) + [B_REF]))

    sweep_jobs = [(b, s) for b in b_values for s in range(args.n_seeds)]
    ts_extra_seeds = [s for s in args.ts_seeds if s >= args.n_seeds]
    ts_jobs = [(B_REF, s) for s in ts_extra_seeds]

    all_jobs = sweep_jobs + ts_jobs
    print(f"Running {len(all_jobs)} episodes total")

    raw = Parallel(n_jobs=-1, verbose=5)(
        delayed(_run_one)(b, s) for b, s in all_jobs
    )

    # ── Aggregate sweep ───────────────────────────────────────────────────────
    b_arr = np.array(sorted(set(b_values)))
    period_mean, period_std = [], []
    ehi_mean, ehi_std = [], []

    for b in b_arr:
        rows = [r for r in raw if r["b"] == b]
        periods = np.array([r["osc_period"] for r in rows])
        periods = np.where(np.isfinite(periods), periods, np.nan)
        period_mean.append(float(np.nanmean(periods)))
        period_std.append(float(np.nanstd(periods)))
        ehi_vals = np.array([r["mean_env"] for r in rows])
        ehi_mean.append(float(np.nanmean(ehi_vals)))
        ehi_std.append(float(np.nanstd(ehi_vals)))

    period_mean = np.array(period_mean)
    period_std  = np.array(period_std)
    ehi_mean    = np.array(ehi_mean)
    ehi_std     = np.array(ehi_std)

    # ── Collect time series at b=21 ───────────────────────────────────────────
    ts_rows = [r for r in raw if r["b"] == B_REF and r["timeseries_resilience"] is not None]
    ts_seeds_used = sorted({r["seed"] for r in ts_rows})[:3]
    ts_resilience = {r["seed"]: r["timeseries_resilience"] for r in ts_rows
                     if r["seed"] in ts_seeds_used}

    # Strategy shares: average over all B_REF seeds
    strat_rows = [r for r in raw if r["b"] == B_REF and r["timeseries_n_UC"] is not None]
    uc_mean = np.mean([r["timeseries_n_UC"] for r in strat_rows], axis=0)
    cc_mean = np.mean([r["timeseries_n_CC"] for r in strat_rows], axis=0)
    d_mean  = np.mean([r["timeseries_n_D"]  for r in strat_rows], axis=0)

    n_gens = BASE_PARAMS["n_gens"]
    gens = np.arange(n_gens)

    # ── Plot ──────────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(14, 7))
    gs = gridspec.GridSpec(2, 2, figure=fig,
                           width_ratios=[1, 1],
                           hspace=0.05,
                           wspace=0.38)

    ax_res   = fig.add_subplot(gs[0, 0])
    ax_strat = fig.add_subplot(gs[1, 0], sharex=ax_res)
    ax_sw    = fig.add_subplot(gs[:, 1])

    colors_seed = ["#f7a35c", "#7cb5ec", "#90ed7d"]
    mw = BASE_PARAMS["measure_window"]

    # — Top-left: resilience time series —
    for i, seed in enumerate(ts_seeds_used):
        ax_res.plot(gens, ts_resilience[seed], color=colors_seed[i % 3],
                    lw=1.2, alpha=0.85, label=f"seed {seed}")
    ax_res.axvspan(n_gens - mw, n_gens, color="gray", alpha=0.10,
                   label="measure window")
    ax_res.set_ylabel("Resilience\n(frac. groups ≥ T)", fontsize=9)
    ax_res.set_title(
        f"Time series at b = {B_REF:.0f}  (initial_e = {args.initial_e})", fontsize=10)
    ax_res.legend(fontsize=8, loc="lower right")
    ax_res.grid(axis="y", lw=0.4, alpha=0.5)
    plt.setp(ax_res.get_xticklabels(), visible=False)

    # — Bottom-left: strategy shares —
    ax_strat.plot(gens, uc_mean, color="#27ae60", lw=1.5, label="UC")
    ax_strat.plot(gens, cc_mean, color="#2980b9", lw=1.5, label="CC")
    ax_strat.plot(gens, d_mean,  color="#c0392b", lw=1.5, label="D")
    ax_strat.axvspan(n_gens - mw, n_gens, color="gray", alpha=0.10)
    ax_strat.set_xlabel("Generation", fontsize=10)
    ax_strat.set_ylabel("Strategy share", fontsize=9)
    ax_strat.set_ylim(0, 1)
    ax_strat.legend(fontsize=8, loc="lower right")
    ax_strat.grid(axis="y", lw=0.4, alpha=0.5)

    # — Right: dominant period + mean EHI vs b —
    color_period = "#9b59b6"
    color_ehi    = "#3498db"

    ax_sw.plot(b_arr, period_mean, color=color_period, lw=2, marker="o", ms=4,
               label="Dominant period (gens)")
    ax_sw.fill_between(b_arr, period_mean - period_std, period_mean + period_std,
                        color=color_period, alpha=0.18)
    ax_sw.set_xlabel("Income b", fontsize=10)
    ax_sw.set_ylabel("Dominant oscillation period (gens)", color=color_period, fontsize=9)
    ax_sw.tick_params(axis="y", labelcolor=color_period)

    ax2 = ax_sw.twinx()
    ax2.plot(b_arr, ehi_mean, color=color_ehi, lw=2, marker="s", ms=4,
             linestyle="--", label="Mean EHI")
    ax2.fill_between(b_arr, ehi_mean - ehi_std, ehi_mean + ehi_std,
                     color=color_ehi, alpha=0.18)
    ax2.set_ylabel("Mean environment EHI (−1…1)", color=color_ehi, fontsize=9)
    ax2.tick_params(axis="y", labelcolor=color_ehi)

    ax_sw.axvline(B_REF, color="gray", lw=0.8, ls="--")
    ax_sw.set_title(
        f"Oscillation period & mean EHI vs income b\n"
        f"(initial_e={args.initial_e}, L={BASE_PARAMS['L']}, {args.n_seeds} seeds)",
        fontsize=10)

    lines1, labels1 = ax_sw.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax_sw.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper left")
    ax_sw.grid(axis="y", lw=0.4, alpha=0.5)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    fig.savefig(args.out, dpi=300, bbox_inches="tight")
    print(f"\nSaved → {args.out}")


if __name__ == "__main__":
    main()
