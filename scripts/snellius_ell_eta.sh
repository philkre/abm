#!/bin/bash
# Operating-window sweep: ell × eta (2D heatmap), starting from initial_e = -1.
#
# 15×15 grid × 5 seeds = 1125 runs, L=200, 1500 gens.
# Wall-time estimate: 1125 runs × ~20 s each / 32 cores ≈ 12 min.
# Requesting 1 h to be safe.
#
# Usage:
#   mkdir -p logs
#   sbatch scripts/snellius_ell_eta.sh
#
# Outputs:
#   results/figures/ell_eta_mean_env.png
#   results/figures/ell_eta_resilience.png
#   results/raw/ell_eta_sweep.npz
#
#SBATCH --job-name=ell_eta_sweep
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=01:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j_ell_eta.out
#SBATCH --error=logs/%j_ell_eta.err

set -euo pipefail

cd /gpfs/home6/pkreiter/abm
mkdir -p logs results/figures results/raw

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[ell-eta] Starting — $(date)"
echo "[ell-eta] 15×15 grid × 5 seeds = 1125 runs, L=200, 1500 gens"

uv run python scripts/ell_eta_sweep.py \
    --n-points 15 \
    --seeds 5 \
    --L 200 \
    --workers 32 \
    --ell-lo 0.1 \
    --ell-hi 0.9 \
    --eta-lo 0.0 \
    --eta-hi 0.3

echo "[ell-eta] Done — $(date)"
echo "[ell-eta] Figures in results/figures/, raw data in results/raw/ell_eta_sweep.npz"
