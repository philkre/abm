#!/bin/bash
# Single-node PAWN sensitivity analysis — linear risk phase.
#
# Parameters varied: beta [0.1, 10], p_max [0, 1], T_over_E [0.4, 0.9], ell [0, 1]
# Fixed (non-default): L=200, sigma=0.1, eta=0.03 (headline A+ run).
#   For ablation (no flood-env feedback): change --fix eta:0.03 to --fix eta:0.0
#   For compute-heavy sweeps: change --fix L:200 to --fix L:150
# Method: PAWN (Latin Hypercube, N=500 total samples).
#   Total episodes = N * n_seeds = 500 * 20 = 10,000.
#   At L=200, 1500 gens, 16 CPUs: estimated ~35–55 min wall time.
#
# Why single-node (not array) for PAWN:
#   PAWN uses Latin Hypercube sampling, which is NOT deterministic without a
#   fixed seed. Array tasks would each generate a different X and simulate
#   incompatible slices; the saved sample_X.npy would then mismatch the
#   simulated params during reanalysis. Sobol (Saltelli sequence) is
#   deterministic and is safe to split across array tasks.
#
# Usage:
#   sbatch scripts/snellius_pawn_linear.sh
#
# After completion, print results:
#   spatcoop sensitivity analyse --out-dir results/sa/linear_pawn
#
#SBATCH --job-name=spatcoop_pawn_linear
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=02:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

set -euo pipefail

mkdir -p logs results/sa/linear_pawn

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[pawn_linear] Starting PAWN SA — linear risk phase"
echo "  Host:       $(hostname)"
echo "  CPUs:       $SLURM_CPUS_PER_TASK"
echo "  Started:    $(date)"

uv run spatcoop sensitivity run \
    --vary beta:0.1:10.0 \
    --vary p_max:0.0:1.0 \
    --vary T_over_E:0.4:0.9 \
    --vary ell:0.0:1.0 \
    --method pawn \
    --N 500 \
    --n-seeds 20 \
    --n-jobs "$SLURM_CPUS_PER_TASK" \
    --fix L:200 \
    --fix sigma:0.1 \
    --fix eta:0.03 \
    --output-key resilience \
    --output-key flood_rate \
    --output-key mean_env \
    --out-dir results/sa/linear_pawn

echo "[pawn_linear] Done: $(date)"
echo ""
echo "Results saved to results/sa/linear_pawn/"
echo "To print indices:"
echo "  spatcoop sensitivity analyse --out-dir results/sa/linear_pawn"
