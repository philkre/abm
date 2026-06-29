#!/bin/bash
# Operating-window sweep: b × ell (2D heatmap), starting from initial_e = -1.
# η is fixed at 0.03 (= δ = γ, symmetric).
#
# 15×15 grid × 5 seeds = 1125 runs, L=200, 1500 gens.
# Wall-time estimate: 1125 runs × ~20 s each / 32 cores ≈ 12 min.
# Requesting 1 h to be safe.
#
# Usage:
#   mkdir -p logs
#   sbatch scripts/snellius_b_ell.sh
#
# Outputs:
#   results/figures/b_ell_combined.png
#   results/figures/b_ell_mean_env.png
#   results/figures/b_ell_resilience.png
#   results/raw/b_ell_sweep.npz
#
#SBATCH --job-name=b_ell_sweep
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=01:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j_b_ell.out
#SBATCH --error=logs/%j_b_ell.err

set -euo pipefail

cd /gpfs/home6/pkreiter/abm
mkdir -p logs results/figures results/raw

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[b-ell] Starting — $(date)"
echo "[b-ell] 15×15 grid × 5 seeds = 1125 runs, L=200, 1500 gens, η=0.03 fixed"

uv run python scripts/b_ell_sweep.py \
    --n-points 15 \
    --seeds 5 \
    --L 200 \
    --workers 32 \
    --ell-lo 0.1 \
    --ell-hi 0.9 \
    --b-lo 0.1 \
    --b-hi 2.0

echo "[b-ell] Done — $(date)"
echo "[b-ell] Figures in results/figures/, raw data in results/raw/b_ell_sweep.npz"
