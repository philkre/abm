"""
Phase portrait: recovery from degraded environment across b × eta grid.

Two panels:
  Left  — mean EHI in measurement window (did it recover?)
  Right — recovery time: first generation where 50-gen rolling-mean EHI crosses 0
           (NaN = never recovered within n_gens)

Both start from initial_e = -1.

Usage:
    uv run python scripts/phase_recovery.py
    uv run python scripts/phase_recovery.py --n-seeds 10 --out results/phase_recovery.png
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from joblib import Parallel, delayed

from spatcoop.params import ModelParams
from spatcoop.model import run_episode

BASE_PARAMS = dict(
    L=150,
    n_gens=1500,
    measure_window=400,
    p_max=1.0,
    ell=0.64,
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
    R=0.0,
)

ROLL_WIN   = 50   # rolling window for recovery detection
BURN_IN    = 100  # ignore first N gens (initial condition artifact)
EHI_THRESH = 0.3  # EHI level that counts as "recovered"


def _recovery_time(ehi_ts: np.ndarray) -> float:
    """First generation (after burn-in) where 50-gen rolling mean EHI > threshold."""
    n = len(ehi_ts)
    if n < ROLL_WIN + BURN_IN:
        return float("nan")
    # Rolling mean via cumsum
    cs = np.cumsum(ehi_ts, dtype=np.float64)
    roll = (cs[ROLL_WIN:] - cs[:-ROLL_WIN]) / ROLL_WIN
    # roll[i] corresponds to gen i + ROLL_WIN
    for i, val in enumerate(roll):
        gen = i + ROLL_WIN
        if gen < BURN_IN:
            continue
        if val > EHI_THRESH:
            return float(gen)
    return float("nan")


def _run_one(b: float, eta: float, seed: int) -> dict:
    p = ModelParams(**{**BASE_PARAMS, "b": b, "eta": eta})
    r = run_episode(p, seed=seed)
    ehi_ts = r.timeseries["mean_env"]
    return {
        "b":            b,
        "eta":          eta,
        "seed":         seed,
        "mean_env":     r.summary["mean_env"],
        "recovery_gen": _recovery_time(ehi_ts),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--b-values", type=float, nargs="+",
                    default=[1, 3, 5, 8, 12, 17, 21, 28, 38, 50, 65, 80])
    ap.add_argument("--eta-values", type=float, nargs="+",
                    default=[0.0, 0.001, 0.003, 0.005, 0.01, 0.02, 0.04, 0.08, 0.12, 0.16])
    ap.add_argument("--n-seeds", type=int, default=10)
    ap.add_argument("--n-jobs", type=int, default=-1)
    ap.add_argument("--out", type=str, default="results/phase_recovery.png")
    args = ap.parse_args()

    b_vals   = np.array(args.b_values)
    eta_vals = np.array(args.eta_values)
    jobs = [(b, eta, s)
            for b in b_vals for eta in eta_vals for s in range(args.n_seeds)]

    print(f"Running {len(jobs)} episodes  "
          f"({len(b_vals)} b × {len(eta_vals)} η × {args.n_seeds} seeds)")

    raw = Parallel(n_jobs=args.n_jobs, verbose=5)(
        delayed(_run_one)(b, eta, s) for b, eta, s in jobs
    )

    # ── Aggregate over seeds ──────────────────────────────────────────────────
    nb, ne = len(b_vals), len(eta_vals)
    ehi_grid      = np.full((ne, nb), np.nan)
    recov_grid    = np.full((ne, nb), np.nan)
    recov_frac    = np.full((ne, nb), np.nan)  # fraction of seeds that recovered

    for ib, b in enumerate(b_vals):
        for ie, eta in enumerate(eta_vals):
            rows = [r for r in raw if r["b"] == b and r["eta"] == eta]
            ehi_vals_arr = np.array([r["mean_env"] for r in rows])
            rec_arr      = np.array([r["recovery_gen"] for r in rows])

            ehi_grid[ie, ib]   = float(np.nanmean(ehi_vals_arr))
            recov_grid[ie, ib] = float(np.nanmean(rec_arr[np.isfinite(rec_arr)])) \
                                  if np.any(np.isfinite(rec_arr)) else np.nan
            recov_frac[ie, ib] = float(np.isfinite(rec_arr).mean())

    # ── Plot ──────────────────────────────────────────────────────────────────
    fig, (ax_ehi, ax_rt) = plt.subplots(1, 2, figsize=(13, 5))
    fig.subplots_adjust(wspace=0.35)

    # Tick labels
    b_labels   = [str(int(v)) for v in b_vals]
    eta_labels = [f"{v:.3f}" for v in eta_vals]

    # — Left: mean EHI —
    vmin, vmax = -1.0, 1.0
    im1 = ax_ehi.imshow(ehi_grid, aspect="auto", origin="lower",
                         cmap="RdYlGn", vmin=vmin, vmax=vmax,
                         extent=[-0.5, nb - 0.5, -0.5, ne - 0.5])
    ax_ehi.set_xticks(range(nb)); ax_ehi.set_xticklabels(b_labels, fontsize=8)
    ax_ehi.set_yticks(range(ne)); ax_ehi.set_yticklabels(eta_labels, fontsize=8)
    ax_ehi.set_xlabel("Income b", fontsize=10)
    ax_ehi.set_ylabel("Flood–defense damage rate η", fontsize=10)
    ax_ehi.set_title("Mean EHI (measurement window)\ninitial_e = −1", fontsize=10)
    cb1 = fig.colorbar(im1, ax=ax_ehi, fraction=0.046, pad=0.04)
    cb1.set_label("Mean EHI (−1…1)", fontsize=9)
    # Contour at recovery threshold
    ax_ehi.contour(ehi_grid, levels=[EHI_THRESH], colors="black", linewidths=1.2,
                   extent=[-0.5, nb - 0.5, -0.5, ne - 0.5])

    # — Right: recovery time —
    cmap_rt = plt.cm.viridis_r.copy()
    cmap_rt.set_bad("0.85")  # gray for never-recovered
    im2 = ax_rt.imshow(recov_grid, aspect="auto", origin="lower",
                        cmap=cmap_rt,
                        extent=[-0.5, nb - 0.5, -0.5, ne - 0.5])
    ax_rt.set_xticks(range(nb)); ax_rt.set_xticklabels(b_labels, fontsize=8)
    ax_rt.set_yticks(range(ne)); ax_rt.set_yticklabels(eta_labels, fontsize=8)
    ax_rt.set_xlabel("Income b", fontsize=10)
    ax_rt.set_ylabel("Flood–defense damage rate η", fontsize=10)
    ax_rt.set_title(f"Mean recovery time (gens until rolling EHI > {EHI_THRESH})\n"
                    f"gray = never recovered  [{args.n_seeds} seeds]",
                    fontsize=10)
    cb2 = fig.colorbar(im2, ax=ax_rt, fraction=0.046, pad=0.04)
    cb2.set_label("Generation", fontsize=9)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    fig.savefig(args.out, dpi=300, bbox_inches="tight")
    print(f"\nSaved → {args.out}")


if __name__ == "__main__":
    main()
