#!/usr/bin/env python3
"""
Recover v2 PAWN SA results from existing checkpoints and compute indices.

Background
----------
The v2 PAWN job (snellius_pawn_linear.sh) completed all 71,680 simulation
episodes but was killed before writing the SA indices.  The stale v1
run_config.json blocked the job from saving sample_X.npy, so the LHS sample
is not on disk.

This script:
1. Scans raw_dir for v2 checkpoints (identified by delta=0.042 + lognormal λ).
2. Rebuilds params_list directly from the stored params_json — exact hashes,
   no floating-point round-trip through T_over_E.
3. Builds an X matrix (beta, p_max, T_over_E, b, eta) for the SALib analysis.
4. Calls collect_Y_vectors with the exact params_list → finds the checkpoints.
5. Runs PAWN and saves pawn_{key}.json plus a new run_config.json / sample_X.npy.

Usage (on Snellius, submit via sbatch or run interactively on a fat node):
    uv run python scripts/recover_pawn_and_analyse.py

Or submit as a batch job (see snellius_pawn_analyse.sh for the SBATCH header).
"""

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

RAW_DIR = Path("/scratch-shared/lschoonheid/results/raw")
OUT_DIR = Path("/scratch-shared/lschoonheid/results/sa/linear_pawn")

NAMES = ["beta", "p_max", "T_over_E", "b", "eta"]
BOUNDS = [[0.1, 10.0], [0.0, 1.0], [0.2, 0.9], [1.0, 30.0], [0.0, 0.020]]
SEEDS = list(range(20))
OUTPUT_KEYS = [
    "resilience", "flood_rate", "mean_env", "mean_env_std",
    "coop_frac", "coop_frac_std", "p_span_UC", "p_span_CC",
    "interface_density", "mean_wealth", "mean_wealth_std",
    "gini_wealth", "mean_fitness", "mean_payoff",
]
N_EXPECTED = 3584

# V2 fixed-param fingerprint (differ from v1)
V2_DELTA = 0.042
V2_LAMBDA_MODE = "lognormal"


def main() -> None:
    from spatcoop.params import ModelParams
    from spatcoop.sa import collect_Y_vectors
    from spatcoop.sa import _compute_pawn, _save_sa_result

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Collect unique v2 param sets from raw checkpoints ──────────────────
    print(f"Scanning {RAW_DIR} ...")
    all_files = sorted(RAW_DIR.glob("*.npz"))
    print(f"  Total .npz files: {len(all_files)}")

    by_hash: dict[str, Path] = {}
    for f in all_files:
        prefix = f.stem.rsplit("_", 1)[0]
        if prefix not in by_hash:
            by_hash[prefix] = f

    print(f"  Unique param hashes: {len(by_hash)}")

    v2_params_raw: list[dict] = []
    for prefix, f in by_hash.items():
        d = np.load(f, allow_pickle=True)
        p = json.loads(str(d["params_json"]))
        if (
            abs(p.get("delta", 0.0) - V2_DELTA) < 1e-9
            and p.get("lambda_mode") == V2_LAMBDA_MODE
        ):
            v2_params_raw.append(p)

    print(f"  V2 param points found: {len(v2_params_raw)}")
    if len(v2_params_raw) != N_EXPECTED:
        print(f"  WARNING: expected {N_EXPECTED}, got {len(v2_params_raw)}. "
              "Some checkpoints may be missing — proceeding anyway.")

    # ── 2. Build params_list from exact stored dicts (no round-trip via X) ───
    # This guarantees ModelParams.hash() matches the filename prefix.
    params_list = [ModelParams(**p) for p in v2_params_raw]

    # ── 3. Build X for the SALib PAWN analysis (statistics only, not lookups) ─
    # T_over_E = T / 5.0 (5 cells × E=1). Small float errors are fine here.
    X = np.array([
        [p["beta"], p["p_max"], p["T"] / 5.0, p["b"], p["eta"]]
        for p in v2_params_raw
    ])
    print(f"\nX shape: {X.shape}")
    for i, name in enumerate(NAMES):
        print(f"  {name}: [{X[:, i].min():.4f}, {X[:, i].max():.4f}]")

    # ── 4. Load Y vectors by looking up checkpoints via exact params_list ──────
    print(f"\nLoading Y vectors ({len(params_list)} params × {len(SEEDS)} seeds) ...")
    problem = {
        "num_vars": len(NAMES),
        "names": NAMES,
        "bounds": BOUNDS,
        "sample_scaled": True,
    }
    Y_dict = collect_Y_vectors(params_list, SEEDS, OUTPUT_KEYS, raw_dir=RAW_DIR)

    # ── 5. Compute PAWN indices and save results ───────────────────────────────
    print("\nComputing PAWN indices ...")
    for key, Y in Y_dict.items():
        indices = _compute_pawn(problem, X, Y)
        out_path = OUT_DIR / f"pawn_{key}.json"
        _save_sa_result(out_path, "pawn", key, problem, N_EXPECTED,
                        len(X), len(SEEDS), params_list[0], indices)
        print(f"  Saved: {out_path.name}")

    # ── 6. Write corrected run_config.json and sample_X.npy ───────────────────
    config_path = OUT_DIR / "run_config.json"
    sample_path = OUT_DIR / "sample_X.npy"

    # Back up stale v1 files if still present
    for path, suffix in [(config_path, "_v1_backup.json"), (sample_path, "_v1_backup.npy")]:
        if path.exists():
            backup = path.with_suffix("").with_name(path.stem + suffix)
            path.rename(backup)
            print(f"Backed up stale {path.name} → {backup.name}")

    config = {
        "method": "pawn",
        "N": N_EXPECTED,
        "problem": problem,
        "seeds": SEEDS,
        "output_keys": OUTPUT_KEYS,
        "base_params": asdict(params_list[0]),
    }
    config_path.write_text(json.dumps(config, indent=2))
    np.save(sample_path, X)
    print(f"\nWrote {config_path}")
    print(f"Wrote {sample_path}")
    print("\nDone. Run `spatcoop sensitivity analyse` to print the indices.")


if __name__ == "__main__":
    main()
