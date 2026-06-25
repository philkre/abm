#!/bin/bash
# Visualization sweep — captures spatial frames (strategy, env, wealth) for a
# targeted grid of parameter points.
#
# Design: 10×10 (beta, p_max) grid × 3 seeds = 300 runs.
# Frames at gens 149, 499, 999, 1499 (early / mid / late / final).
# Fixed: T_over_E=0.65, ell=0.34 (Kolen), eta=0.03 (A+), sigma=0.1, L=200.
#
# Storage estimate (strategy+env+wealth, 4 frames, 300 runs):
#   300 × 4 × ~150 KB ≈ 180 MB — well under budget.
#
# Wall-time estimate: ~300 runs × ~25 s/run / 16 CPUs ≈ 8 min.
#
# Output: /scatch-shared/lschoonheid/results/viz/beta_pmax/{hash}_{seed:06d}_frames.npz
#
# To add other 2D slices (e.g. T_over_E × ell), copy this script and
# swap the --grid lines and --out-dir accordingly.
#
# Usage:
#   sbatch scripts/snellius_viz_sweep.sh
#
#SBATCH --job-name=spatcoop_viz
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=01:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

set -euo pipefail

mkdir -p logs /scatch-shared/lschoonheid/results/viz/beta_pmax

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[viz_sweep] Starting visualization sweep"
echo "  Host:    $(hostname)"
echo "  CPUs:    $SLURM_CPUS_PER_TASK"
echo "  Started: $(date)"

uv run spatcoop viz-sweep \
    --grid beta:0.1:10.0:10:log \
    --grid p_max:0.0:1.0:10 \
    --fix L:200 \
    --fix eta:0.03 \
    --fix sigma:0.1 \
    --fix T_over_E:0.65 \
    --fix ell:0.34 \
    --fix initial_mix:thirds \
    --snap-gens 1,149,249,499,749,999,1249,1499 \
    --n-seeds 3 \
    --n-jobs "$SLURM_CPUS_PER_TASK" \
    --out-dir /scatch-shared/lschoonheid/results/viz/beta_pmax

echo "[viz_sweep] Done: $(date)"
echo ""
echo "Frames in /scatch-shared/lschoonheid/results/viz/beta_pmax/"
echo "Grid: beta (10, log) × p_max (10, linear) × 3 seeds = 300 runs"
echo "Snap generations: 1, 149, 249, 499, 749, 999, 1249, 1499"
