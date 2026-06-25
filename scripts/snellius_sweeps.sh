#!/bin/bash
# 1-D parameter sweeps at the headline config (L=200), over all order parameters.
#
# Sweeps delta, gamma, eta, lambda_mean, b, w0 and saves one grid figure per
# swept parameter (op_vs_<param>.pdf) showing every order parameter vs the value.
#
# Compute: 6 parameters * n_points * n_seeds episodes at L=200, 1500 gens.
#   With n_points=15, n_seeds=10 → 6*15*10 = 900 episodes.
#   Shrink via --n-points / --n-seeds if wall time is tight.
#
# Usage:
#   sbatch scripts/snellius_sweeps.sh
#
#SBATCH --job-name=sweeps_spatcoop
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --time=02:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

set -euo pipefail

mkdir -p logs results/figures

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[sweeps] Starting — $(date)"

uv run spatcoop param-sweep \
    --L 200 \
    --n-gens 1500 \
    --eta 0.03 \
    --sigma 0.1 \
    --initial-mix thirds \
    --n-seeds 10 \
    --n-points 15 \
    --n-jobs "$SLURM_CPUS_PER_TASK"

echo "[sweeps] Done — $(date). Figures (op_vs_*.pdf) in results/figures/."
