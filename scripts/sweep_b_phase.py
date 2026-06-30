"""
Phase diagram: multiple order parameters vs income b.
Starts from degraded environment (initial_e=-1) to show the resilience-erosion trap.

Usage:
    uv run python scripts/sweep_b_phase.py
    uv run python scripts/sweep_b_phase.py --b-values 5 10 15 21 30 45 60 --n-seeds 5
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import argparse
import numpy as np
import matplotlib.pyplot as plt
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

ORDER_PARAMS = [
    ("resilience",  "Resilience\n(frac immune groups)", "#2ecc71"),
    ("mean_env",    "Mean EHI\n(−1…1)",                 "#3498db"),
    ("flood_rate",  "Flood rate",                        "#e74c3c"),
    ("n_UC",        "UC fraction",                       "#f39c12"),
    ("n_CC",        "CC fraction",                       "#1abc9c"),
    ("osc_period",  "Dominant period\n(gens/cycle)",     "#9b59b6"),
    ("osc_power",   "Oscillation power\n(frac. variance)",      "#e67e22"),
]


def _run_one(b: float, seed: int) -> dict:
    p = ModelParams(**{**BASE_PARAMS, "b": b})
    r = run_episode(p, seed=seed)
    s = r.summary
    L2 = p.L ** 2
    return {
        "b": b,
        "seed": seed,
        "resilience":     s["resilience"],
        "mean_env":       s["mean_env"],
        "flood_rate":     s["flood_rate"],
        "resilience_std": s["resilience_std"],
        "n_UC":           s["n_UC"] / L2,
        "n_CC":           s["n_CC"] / L2,
        "osc_period":     s["osc_period"],
        "osc_power":      s["osc_power"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--b-values", type=float, nargs="+",
                    default=[5, 8, 11, 14, 17, 21, 26, 32, 40, 55, 70])
    ap.add_argument("--n-seeds", type=int, default=5)
    ap.add_argument("--n-jobs", type=int, default=-1)
    ap.add_argument("--out", type=str, default="results/b_phase.png")
    args = ap.parse_args()

    jobs = [(b, s) for b in args.b_values for s in range(args.n_seeds)]
    print(f"Running {len(jobs)} episodes  ({len(args.b_values)} b-values × {args.n_seeds} seeds)")
    print(f"  L={BASE_PARAMS['L']}, n_gens={BASE_PARAMS['n_gens']}, initial_e={BASE_PARAMS['initial_e']}")

    raw = Parallel(n_jobs=args.n_jobs, verbose=5)(
        delayed(_run_one)(b, s) for b, s in jobs
    )

    # Aggregate: mean ± std over seeds per b value
    b_arr = np.array(args.b_values)
    agg = {k: {"mean": [], "std": []} for k, *_ in ORDER_PARAMS}

    for b in b_arr:
        rows = [r for r in raw if r["b"] == b]
        for k, *_ in ORDER_PARAMS:
            vals = [r[k] for r in rows]
            # Replace inf with nan so nanmean/nanstd ignore non-oscillating seeds
            vals_arr = np.where(np.isfinite(vals), vals, np.nan)
            agg[k]["mean"].append(float(np.nanmean(vals_arr)))
            agg[k]["std"].append(float(np.nanstd(vals_arr)))

    for k in agg:
        agg[k]["mean"] = np.array(agg[k]["mean"])
        agg[k]["std"]  = np.array(agg[k]["std"])

    # ── Plot ──────────────────────────────────────────────────────────────────
    n_panels = len(ORDER_PARAMS)
    fig, axes = plt.subplots(n_panels, 1, figsize=(8, 2.2 * n_panels),
                             sharex=True)
    fig.subplots_adjust(hspace=0.08)

    for ax, (key, ylabel, color) in zip(axes, ORDER_PARAMS):
        m = agg[key]["mean"]
        s = agg[key]["std"]
        ax.plot(b_arr, m, color=color, lw=2, marker="o", ms=4)
        ax.fill_between(b_arr, m - s, m + s, color=color, alpha=0.2)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.axvline(21, color="gray", lw=0.8, ls="--", label="NetLogo b=21")
        ax.grid(axis="y", lw=0.4, alpha=0.5)

    axes[-1].set_xlabel("Income b (NetLogo units)", fontsize=9)
    axes[0].legend(fontsize=7)
    axes[0].set_title(
        f"Phase diagram: order parameters vs income  "
        f"(initial_e=−1, L={BASE_PARAMS['L']}, {args.n_seeds} seeds)",
        fontsize=9
    )

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    fig.savefig(args.out, dpi=150, bbox_inches="tight")
    print(f"\nSaved → {args.out}")


if __name__ == "__main__":
    main()
