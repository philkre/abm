"""local_money_sa_run.py — Data generation for the money-parameter exploratory SA.

Sweeps five parameters while holding the NetLogo environmental params fixed:
  T/E (threshold), b (Wiener drift / income), c_bar (cooperation contribution),
  ell (flood loss fraction), sigma (Wiener diffusion / idiosyncratic shock).

wealth_mode="ou" (the default) IS the Wiener-with-drift process:
  w_{t+1} = w + b  -  contrib  -  loss  +  N(0, sigma)
where b is the additive drift (income) and sigma is the diffusion coefficient.
No separate Wiener script is needed — this script already uses that mode.

w0 (initial wealth) was swept in the first pass and confirmed uninformative
(S1 ≈ 0 across all outputs; consistent with theory: SS wealth = b/ell regardless
of w0). It has been dropped from the sweep.

Usage (run from philkre-abm root):
    uv run python scripts/local_money_sa_run.py                   # defaults
    uv run python scripts/local_money_sa_run.py --N 32 --L 100   # bigger

After completion, run:
    uv run python scripts/local_money_sa_plot.py

Outputs: results/local_money_sa/raw/*.npz  +  config.json  +  sample_X.npy
"""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spatcoop.params import ModelParams
from spatcoop.sa import build_problem, sample_params_from_problem
from spatcoop.runner import run_batch

OUT_DIR = Path("results/local_money_sa")
RAW_DIR = OUT_DIR / "raw"

# Five money/process parameters spanning both cooperative and collapse phases.
# Ranges chosen so that (b, c_bar) jointly cover c_bar/b ∈ [0.005, 1.5]:
#   - c_bar/b ≈ 0.04 at NetLogo scale (b=21, c_bar≈0.84)  → oscillatory
#   - c_bar/b ≈ 0.75 at SA scale (b=1, c_bar=0.75)        → collapse
# sigma = Wiener diffusion; at 0 → deterministic income; at 0.5 → noisy (50% of b=1).
# w0 dropped: uninformative (S1≈0 everywhere; SS wealth = b/ell regardless of w0).
VARY_SPECS = [
    ("T_over_E", 0.2,  0.9),   # threshold ratio; NetLogo≈0.34; old SA [0.4,0.9]
    ("b",        1.0,  21.0),  # Wiener drift (income); collapse at b=1, oscillatory at b≥4
    ("c_bar",    0.1,  1.5),   # cooperation contribution; c_bar/b spans [0.005, 1.5]
    ("ell",      0.05, 1.0),   # flood loss fraction; NetLogo=0.64
    ("sigma",    0.0,  0.5),   # Wiener diffusion (per-round idiosyncratic wealth shock)
]


def make_base(L: int = 60, n_gens: int = 200) -> ModelParams:
    """Fixed params: NetLogo env values + beta=1.8, p_max=1.0, wealth_mode=ou."""
    mw = min(100, n_gens // 2)
    return ModelParams(
        L=L, n_gens=n_gens, measure_window=mw,
        # NetLogo environmental params (required for oscillatory phase)
        delta=0.042, gamma=0.018, eta=0.005, kappa=0.1,
        # Fermi / mutation (not swept here; enter big Snellius SA)
        beta=1.8, p_max=1.0, mu=0.0104,
        # Wealth mode: "ou" = Wiener-with-drift (b=drift, sigma=diffusion)
        wealth_mode="ou",
        # Spatial / strategy initialisation
        sigma=0.1, initial_mix="thirds", risk_mode="linear",
        # Placeholder values overridden by sweep
        T=2.0, b=5.0, c_bar=0.75, w0=1.0, ell=0.5,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Money-SA data generation.")
    parser.add_argument("--N",      type=int, default=16,
                        help="Sobol base sample size; total = N*(D+2). Default: 16 → 112 samples.")
    parser.add_argument("--seeds",  type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--L",      type=int, default=60,
                        help="Grid side length. 60 = fast local; 200 = headline quality.")
    parser.add_argument("--n-gens", type=int, default=200)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    base = make_base(args.L, args.n_gens)
    problem = build_problem(VARY_SPECS)
    params_list, X = sample_params_from_problem(problem, args.N, base, method="sobol")

    np.save(OUT_DIR / "sample_X.npy", X)
    config = {
        "N": args.N, "seeds": args.seeds, "L": args.L, "n_gens": args.n_gens,
        "vary_specs": VARY_SPECS, "base_params": asdict(base),
    }
    (OUT_DIR / "config.json").write_text(json.dumps(config, indent=2))

    total = len(params_list) * len(args.seeds)
    print(f"Sobol  D={problem['num_vars']}  N={args.N} → {len(params_list)} samples")
    print(f"Seeds: {args.seeds}  →  {total} episodes  |  L={args.L}  n_gens={args.n_gens}")
    print(f"Parameters: {problem['names']}")
    print("(wealth_mode=ou → Wiener-with-drift; b=drift, sigma=diffusion)")
    run_batch(params_list, args.seeds, n_jobs=args.n_jobs, raw_dir=RAW_DIR)
    print(f"Done.  Results in {RAW_DIR}/")


if __name__ == "__main__":
    main()
