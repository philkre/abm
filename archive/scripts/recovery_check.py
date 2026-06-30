"""recovery_check.py — Phase 1: can a fully-degraded environment self-rescue?

Single run with initial_e = -1 and the calibrated parameter set.
Plots mean_env and resilience over 1500 generations, marks stabilisation.

Usage (from abm root):
    uv run python scripts/recovery_check.py
    uv run python scripts/recovery_check.py --seeds 5 --L 100
"""

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spatcoop.model import run_episode
from spatcoop.params import ModelParams

# ── Calibrated fixed parameters ───────────────────────────────────────────────
BASE_KWARGS = dict(
    n_gens=1500,
    measure_window=200,
    # Structural
    L=200,
    # Game
    c_bar=0.83,
    T=1.7,
    w0=312.0,
    mu=0.0104,
    # Wealth
    wealth_mode="ou",
    b=21.0,
    sigma=0.0,
    # Risk
    risk_mode="linear",
    p_max=1.0,
    ell=0.64,
    p_min=0.0,
    # Environment
    delta=0.042,
    gamma=0.018,
    eta=0.005,
    kappa=0.1,
    # Imitation
    beta=1.8,
    # Loss aversion — lognormal CC
    lambda_mode="lognormal",
    lambda_mean=2.25,
    lambda_sigma=0.5,
    # Start with all three strategies present
    initial_mix="thirds",
    # Phase 1: fully degraded
    initial_e=-1.0,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seeds", type=int, default=3, help="Number of seeds to overlay")
    p.add_argument("--L", type=int, default=None, help="Override lattice size")
    p.add_argument("--workers", type=int, default=None, help="Parallel workers")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    kwargs = dict(BASE_KWARGS)
    if args.L is not None:
        kwargs["L"] = args.L

    p = ModelParams(**kwargs)
    n_gens = p.n_gens

    print(f"Recovery check  L={p.L}  seeds={args.seeds}  n_gens={n_gens}")
    print(f"  ell={p.ell}  eta={p.eta}  initial_e={p.initial_e}")
    print()

    all_env = []
    all_res = []
    all_coop = []

    for seed in range(args.seeds):
        print(f"  Running seed {seed}...", flush=True)
        result = run_episode(p, seed=seed, progress=True)
        all_env.append(result.timeseries["mean_env"])
        all_res.append(result.timeseries["resilience"])
        all_coop.append(result.timeseries["coop_frac"])
        final_e = float(result.timeseries["mean_env"][-1])
        final_r = float(result.timeseries["resilience"][-1])
        print(f"    → final mean_env={final_e:.3f}  resilience={final_r:.3f}")

    gens = np.arange(n_gens)
    env_arr = np.array(all_env)
    res_arr = np.array(all_res)
    coop_arr = np.array(all_coop)

    # Detect approximate stabilisation: where mean_env first crosses 0
    crosses_zero = []
    for trace in env_arr:
        idx = np.where(trace >= 0.0)[0]
        crosses_zero.append(idx[0] if len(idx) else None)

    # ── Plot ─────────────────────────────────────────────────────────────────
    fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    colors = plt.cm.tab10(np.linspace(0, 0.5, args.seeds))

    for i, (env_ts, res_ts, coop_ts) in enumerate(zip(env_arr, res_arr, coop_arr)):
        c = colors[i]
        axes[0].plot(gens, env_ts, color=c, alpha=0.8, lw=1.2, label=f"seed {i}")
        axes[1].plot(gens, res_ts, color=c, alpha=0.8, lw=1.2)
        axes[2].plot(gens, coop_ts, color=c, alpha=0.8, lw=1.2)

    if args.seeds > 1:
        env_mean = env_arr.mean(axis=0)
        axes[0].plot(gens, env_mean, color="black", lw=2.0, label="mean")

    axes[0].axhline(0.0, color="red", ls="--", lw=1.0, label="neutral (e=0)")
    axes[0].axhline(-1.0, color="gray", ls=":", lw=1.0, label="full degradation")
    axes[0].set_ylabel("mean_env")
    axes[0].set_ylim(-1.1, 1.1)
    axes[0].legend(fontsize=9, loc="lower right")

    # Annotate crossing points
    for gen_cross in crosses_zero:
        if gen_cross is not None:
            axes[0].axvline(gen_cross, color="orange", ls="--", lw=0.8, alpha=0.5)

    axes[1].axhline(1.0, color="gray", ls=":", lw=1.0)
    axes[1].set_ylabel("resilience (frac pools ≥ T)")
    axes[1].set_ylim(-0.05, 1.1)

    axes[2].axhline(1.0, color="gray", ls=":", lw=1.0)
    axes[2].set_ylabel("coop_frac (UC + CC)")
    axes[2].set_ylim(-0.05, 1.1)
    axes[2].set_xlabel("Generation")

    fig.suptitle(
        f"Phase 1 — Recovery check  (initial_e=−1, ell={p.ell}, eta={p.eta})\n"
        f"L={p.L}, c_bar={p.c_bar}, T={p.T}, b={p.b}, w0={p.w0}, "
        f"λ∼LN({p.lambda_mean},{p.lambda_sigma})",
        fontsize=11,
    )
    fig.tight_layout()

    out = Path("results/figures/recovery_check.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"\nFigure saved to {out}")

    # Summary
    print()
    recovered = sum(1 for g in crosses_zero if g is not None)
    print(f"Recovered (crossed e=0): {recovered}/{args.seeds} seeds")
    for i, g in enumerate(crosses_zero):
        if g is not None:
            final_e = float(env_arr[i, -1])
            print(f"  seed {i}: crossed at gen {g}, stabilised at mean_env={final_e:.3f}")
        else:
            print(f"  seed {i}: NEVER crossed 0 — full-degradation trap")


if __name__ == "__main__":
    main()
