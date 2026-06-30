#!/usr/bin/env bash
# Recompute SA indices for EVERY order parameter, then plot them all.
#
# The SA run scripts only request a curated set of output keys, but every summary
# statistic is stored in the per-run checkpoints. This script recomputes the SA
# indices for all OBS_KEYS straight from those checkpoints (no re-simulation),
# then plots a bar chart per order parameter — so you can inspect sensitivity for
# OPs that were not in the curated headline set.
#
# Cost: NO simulation, but it loads every checkpoint (I/O-heavy for the full
# sample) and runs the analyser per key. Fine on a login node for moderate
# samples; for very large samples consider submitting as a short SLURM job.
#
# Requires: fresh checkpoints that include the new OPs. Stale pre-existing
# results/raw/*.npz (created before the new OPs were added) will KeyError — those
# runs must be re-simulated first.
#
# Usage:
#   bash scripts/make_sa_plots_all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

export PATH="$HOME/.local/bin:$PATH"

PAIRS=(
    "/scratch-shared/lschoonheid/results/sa/linear_sobol sobol"
    "/scratch-shared/lschoonheid/results/sa/linear_pawn  pawn"
)

for pair in "${PAIRS[@]}"; do
    read -r dir method <<<"$pair"
    if [[ ! -d "$dir" ]]; then
        echo "[make_sa_plots_all] Skipping missing dir: $dir"
        continue
    fi
    echo "[make_sa_plots_all] Recomputing ALL order parameters for $method in $dir"
    uv run spatcoop sensitivity analyse --out-dir "$dir" --method "$method" --recompute --all-keys \
        --raw-dir /scratch-shared/lschoonheid/results/raw
    echo "[make_sa_plots_all] Plotting all $method bars from $dir"
    uv run spatcoop plot-sa --out-dir "$dir" --method "$method" --all
done

echo "[make_sa_plots_all] Done. All-OP SA figures in results/figures/."
