#!/bin/bash
# Recover and compute PAWN indices from the v2 simulation checkpoints.
#
# The v2 PAWN job completed all 71,680 episodes but the stale v1 run_config.json
# blocked sample_X.npy from being saved, so the LHS sample was lost.
# scripts/recover_pawn_and_analyse.py rebuilds params_list directly from the
# stored params_json in each .npz, runs collect_Y_vectors, computes PAWN
# indices, and writes pawn_{key}.json + corrected run_config.json/sample_X.npy.
#
# Estimated wall time: ~2 h (loading 3584 × 20 checkpoints is the bottleneck).
#
# Usage:
#   sbatch --account=gisr129479 scripts/snellius_pawn_analyse.sh
#
#SBATCH --job-name=pawn_analyse
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=192
#SBATCH --time=02:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err
# Note: pass --account=<your-account> to sbatch if your cluster requires it.

set -euo pipefail

mkdir -p logs

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[pawn_analyse] Computing PAWN indices from checkpoints"
echo "  Host:    $(hostname)"
echo "  CPUs:    $SLURM_CPUS_PER_TASK"
echo "  Started: $(date)"

uv run python scripts/recover_pawn_and_analyse.py

echo "[pawn_analyse] Done: $(date)"
echo ""
echo "Results saved to /scratch-shared/lschoonheid/results/sa/linear_pawn/"
echo "Fetch with: rsync -av snellius:/scratch-shared/lschoonheid/results/sa/linear_pawn/ results/sa/linear_pawn/"
