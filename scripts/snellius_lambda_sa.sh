#!/bin/bash
# Targeted PAWN sensitivity analysis — loss-aversion heterogeneity axis.
#
# Varies lambda_mean [1.0, 3.0] with lambda_mode=lognormal, lambda_sigma=0.5.
# All other parameters held at headline A+ values.
# Purpose: document how the spread of the loss-aversion distribution
#   affects cooperation and resilience, satisfying the ODD+ heterogeneity axis
#   requirement (second axis beyond wealth).
#
# Design note: with Fermi imitation ON, higher lambda_mean accelerates defection
#   dominance (CC premium is discounted by imitation speed); see project-todos.md P1.
#   This script intentionally runs the imitation-on case to document the collapse.
#   For frozen-strategies contrast, add --fix frozen_strategies:true.
#
# Method: PAWN (Latin Hypercube, N=512 samples — sufficient for 1 varied parameter).
#   Total episodes = 512 * 20 = 10,240.
#   At L=200, 1500 gens, 24 CPUs: estimated ~1–2 h wall time.
#
# Usage:
#   sbatch scripts/snellius_lambda_sa.sh
#
# After completion, print results:
#   spatcoop sensitivity analyse --out-dir /scratch-shared/lschoonheid/results/sa/lambda_pawn
#
#SBATCH --job-name=lambda_pawn_spatcoop
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --time=03:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

set -euo pipefail

mkdir -p logs /scratch-shared/lschoonheid/results/sa/lambda_pawn /scratch-shared/lschoonheid/results/raw

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[lambda_pawn] Starting targeted PAWN SA — loss-aversion axis"
echo "  Host:       $(hostname)"
echo "  CPUs:       $SLURM_CPUS_PER_TASK"
echo "  Started:    $(date)"

uv run spatcoop sensitivity run \
    --vary lambda_mean:1.0:3.0 \
    --method pawn \
    --N 512 \
    --n-seeds 20 \
    --n-jobs "$SLURM_CPUS_PER_TASK" \
    --fix L:200 \
    --fix sigma:0.1 \
    --fix eta:0.03 \
    --fix initial_mix:thirds \
    --fix lambda_mode:lognormal \
    --fix lambda_sigma:0.5 \
    --output-key resilience \
    --output-key flood_rate \
    --output-key mean_env \
    --output-key mean_fitness \
    --output-key mean_payoff \
    --output-key coop_frac \
    --output-key p_span_UC \
    --output-key p_span_CC \
    --output-key gini_wealth \
    --output-key interface_density \
    --out-dir /scratch-shared/lschoonheid/results/sa/lambda_pawn \
    --raw-dir /scratch-shared/lschoonheid/results/raw

echo "[lambda_pawn] Done: $(date)"
echo ""
echo "Results saved to /scratch-shared/lschoonheid/results/sa/lambda_pawn/"
echo "To print indices:"
echo "  spatcoop sensitivity analyse --out-dir /scratch-shared/lschoonheid/results/sa/lambda_pawn"
