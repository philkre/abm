#!/bin/bash
# 2D phase diagram: T_over_E [0.3, 0.8] × eta [0.0, 0.2].
# 15×15 grid × 10 seeds = 2250 runs at L=200, 1500 gens.
# Output: results/figures/phase_T_x_eta.pdf
#
# Usage:
#   sbatch scripts/snellius_phase_diagram.sh
#
#SBATCH --job-name=phase_diagram
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --time=02:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

set -euo pipefail

cd /gpfs/home6/pkreiter/abm
mkdir -p logs results/figures

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[phase-diagram] Starting — $(date)"
echo "[phase-diagram] 15×15 grid × 10 seeds = 2250 runs, L=200"

uv run spatcoop phase-diagram \
    --L 200 \
    --n-gens 1500 \
    --n-seeds 10 \
    --n-points 15 \
    --sigma 0.1 \
    --n-jobs "$SLURM_CPUS_PER_TASK"

echo "[phase-diagram] Done — $(date). Figure: results/figures/phase_T_x_eta.pdf"
