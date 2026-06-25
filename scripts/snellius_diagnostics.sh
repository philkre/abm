#!/bin/bash
# Sim-backed diagnostic plots at the headline config (L=200).
#
# Runs a single dedicated ensemble (NOT part of the SA sweep — the SA samples are
# all different parameter points) and produces:
#   - op_timeseries.pdf : every order parameter over time, mean ± across-seed σ
#   - spectrum_<key>.pdf : oscillation power spectra (n_UC, coop_frac, mean_env)
#   - snapshot_fields.pdf : strategy/wealth/env lattices over the measure window
#
# plot-ops and spectrum share the same param-hash, so run_batch simulates the
# ensemble once and the spectrum calls reuse the cached checkpoints.
#
# Usage:
#   sbatch scripts/snellius_diagnostics.sh
#
#SBATCH --job-name=spatcoop_diagnostics
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=01:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

set -euo pipefail

mkdir -p logs results/figures

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

# Headline ensemble config (matches the SA fixed params).
COMMON=(--L 200 --n-gens 1500 --eta 0.03 --sigma 0.1 --initial-mix thirds)
N_SEEDS=10

echo "[diagnostics] Starting — $(date)"

# 1. Timeseries of all order parameters (mean ± σ). Simulates the ensemble.
uv run spatcoop plot-ops "${COMMON[@]}" --n-seeds "$N_SEEDS" --n-jobs "$SLURM_CPUS_PER_TASK"

# 2. Power spectra for the oscillation-prone OPs (reuses cached sims).
for key in n_UC coop_frac mean_env; do
    uv run spatcoop spectrum "${COMMON[@]}" --n-seeds "$N_SEEDS" \
        --n-jobs "$SLURM_CPUS_PER_TASK" --key "$key"
done

# 3. Saved snapshot fields (single representative seed).
uv run spatcoop snapshot-fields --L 200 --n-gens 1500 --eta 0.03 --sigma 0.1 \
    --initial-mix thirds --snapshot-every 50 --seed 0

echo "[diagnostics] Done — $(date). Figures in results/figures/."
