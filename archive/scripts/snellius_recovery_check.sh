#!/bin/bash
# Phase 1 — recovery check: single run (10 seeds) from initial_e = -1.
# Plots mean_env timeseries to see if/where it stabilises.
#
# Wall-time estimate: 10 seeds × L=200 × 1500 gens ≈ 10 min on 10 cores.
# Requesting 30 min.
#
# Usage:
#   mkdir -p logs
#   sbatch scripts/snellius_recovery_check.sh
#
# Output: results/figures/recovery_check.png
#
#SBATCH --job-name=recovery_check
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=00:30:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j_recovery_check.out
#SBATCH --error=logs/%j_recovery_check.err

set -euo pipefail

cd /gpfs/home6/pkreiter/abm
mkdir -p logs results/figures

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[recovery-check] Starting — $(date)"

uv run python scripts/recovery_check.py \
    --seeds 10 \
    --L 200 \
    --workers 10

echo "[recovery-check] Done — $(date). Figure: results/figures/recovery_check.png"
