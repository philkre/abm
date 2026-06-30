"""
Time-series diagnostic plot — 6-panel layout matching the NetLogo reference figure.
Runs 3 seeds and overlays them; strategy shares and wealth are seed-averaged.

Usage:
    uv run python scripts/plot_timeseries.py
    uv run python scripts/plot_timeseries.py --n-gens 500 --beta 1.5 --eta 0.05
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from spatcoop.params import ModelParams
from spatcoop.model import run_episode


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--n-gens", type=int, default=400)
    p.add_argument("--L", type=int, default=150)
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    p.add_argument("--beta", type=float, default=2.0)
    p.add_argument("--p-max", type=float, default=0.5)
    p.add_argument("--eta", type=float, default=0.03)
    p.add_argument("--delta", type=float, default=0.04)
    p.add_argument("--gamma", type=float, default=0.02)
    p.add_argument("--b", type=float, default=21.0)
    p.add_argument("--sigma", type=float, default=3.0)
    p.add_argument("--ell", type=float, default=0.64)
    p.add_argument("--kappa", type=float, default=0.1)
    p.add_argument("--w0", type=float, default=312.0)
    p.add_argument("--c-bar", type=float, default=0.83, dest="c_bar")
    p.add_argument("--T", type=float, default=1.7)
    p.add_argument("--mu", type=float, default=0.0104)
    p.add_argument("--out", type=str, default="results/timeseries.png")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    params = ModelParams(
        L=args.L,
        n_gens=args.n_gens,
        measure_window=args.n_gens,  # track full run
        beta=args.beta,
        p_max=args.p_max,
        eta=args.eta,
        delta=args.delta,
        gamma=args.gamma,
        b=args.b,
        sigma=args.sigma,
        ell=args.ell,
        kappa=args.kappa,
        w0=args.w0,
        c_bar=args.c_bar,
        T=args.T,
        mu=args.mu,
        initial_mix="thirds",
        lambda_mode="lognormal",
        lambda_mean=2.25,
    )

    print(f"Running {len(args.seeds)} seeds | L={args.L} | {args.n_gens} gens")
    print(f"  T={params.T:.3f}  c_bar={params.c_bar}  beta={params.beta}")
    print(f"  eta={params.eta}  delta={params.delta}  gamma={params.gamma}")

    results = []
    for seed in args.seeds:
        print(f"  seed {seed}...", end=" ", flush=True)
        r = run_episode(params, seed=seed)
        results.append(r)
        print("done")

    gens = np.arange(args.n_gens)
    N = params.L ** 2

    # ── Build figure ─────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(15, 8))
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.38, wspace=0.32)
    ax = [[fig.add_subplot(gs[r, c]) for c in range(3)] for r in range(2)]

    colors_seed = ["#f7a35c", "#7cb5ec", "#90ed7d"]
    colors_strat = {"D": "#e84118", "UC": "#44bd32", "CC": "#0097e6"}

    def _ts(r, key):
        return r.timeseries[key]

    # ── Top-left: mean_env ────────────────────────────────────────────────────
    for i, r in enumerate(results):
        ax[0][0].plot(gens, _ts(r, "mean_env"), color=colors_seed[i],
                      lw=1.2, label=f"seed {args.seeds[i]}")
    ax[0][0].set_title("mean_env")
    ax[0][0].set_ylabel("mean_env (−1…1)")
    ax[0][0].legend(fontsize=7)

    # ── Top-mid: flood_rate ───────────────────────────────────────────────────
    for i, r in enumerate(results):
        ax[0][1].plot(gens, _ts(r, "flood_rate"), color=colors_seed[i], lw=1.2,
                      label=f"seed {args.seeds[i]}")
    ax[0][1].set_title("flood_rate")
    ax[0][1].set_ylabel("flood rate")
    ax[0][1].legend(fontsize=7)

    # ── Top-right: strategy shares (seed-averaged) ────────────────────────────
    n_D  = np.mean([_ts(r, "n_D")  / N for r in results], axis=0)
    n_UC = np.mean([_ts(r, "n_UC") / N for r in results], axis=0)
    n_CC = np.mean([_ts(r, "n_CC") / N for r in results], axis=0)
    ax[0][2].plot(gens, n_D,  color=colors_strat["D"],  lw=1.5, label="D")
    ax[0][2].plot(gens, n_UC, color=colors_strat["UC"], lw=1.5, label="UC")
    ax[0][2].plot(gens, n_CC, color=colors_strat["CC"], lw=1.5, label="CC")
    ax[0][2].set_title("Strategy shares (mean over seeds)")
    ax[0][2].set_ylabel("Fraction")
    ax[0][2].legend(fontsize=7)

    # ── Bottom-left: mean wealth by strategy (seed-averaged) ─────────────────
    # Approximate: mean_wealth tracked globally; per-strategy from strategy counts
    # Use mean_wealth proxy (per-strategy breakdown not stored separately)
    w_all = np.mean([_ts(r, "mean_wealth") for r in results], axis=0)
    ax[1][0].plot(gens, w_all, color="gray", lw=1.5, label="all")
    ax[1][0].set_title("Mean wealth (all agents)")
    ax[1][0].set_ylabel("Wealth")
    ax[1][0].legend(fontsize=7)

    # ── Bottom-mid: resilience ────────────────────────────────────────────────
    for i, r in enumerate(results):
        ax[1][1].plot(gens, _ts(r, "resilience"), color=colors_seed[i], lw=1.2,
                      label=f"seed {args.seeds[i]}")
    ax[1][1].set_title("resilience")
    ax[1][1].set_ylabel("resilience (frac immune groups)")
    ax[1][1].legend(fontsize=7)

    # ── Bottom-right: coop_frac ───────────────────────────────────────────────
    for i, r in enumerate(results):
        coop = (_ts(r, "n_UC") + _ts(r, "n_CC")) / N
        ax[1][2].plot(gens, coop, color=colors_seed[i], lw=1.2,
                      label=f"seed {args.seeds[i]}")
    ax[1][2].set_title("coop_frac")
    ax[1][2].set_ylabel("coop frac (UC+CC)")
    ax[1][2].legend(fontsize=7)

    for row in ax:
        for a in row:
            a.set_xlabel("Generation")

    param_str = (
        f"spatcoop  L={args.L}, {args.n_gens} gens, {len(args.seeds)} seeds\n"
        f"T={params.T:.2f}, c_bar={params.c_bar}, b={args.b}, w0={args.w0}, "
        f"sigma={args.sigma}, ell={args.ell}, "
        f"delta={args.delta}, gamma={args.gamma}, eta={args.eta}, "
        f"kappa={args.kappa}, beta={args.beta}, lam-lognormal({params.lambda_mean})"
    )
    fig.suptitle(param_str, fontsize=8, y=1.01)

    import os
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    fig.savefig(args.out, dpi=150, bbox_inches="tight")
    print(f"\nSaved → {args.out}")


if __name__ == "__main__":
    main()
