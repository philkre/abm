#!/bin/bash
# Compute PAWN indices from already-completed simulation checkpoints.
#
# Run this after snellius_pawn_linear.sh has finished all simulation runs.
# The "sensitivity run" command checkpoints each episode as a .npz file in
# --raw-dir; "sensitivity analyse" reads those and computes the PAWN KS
# statistics without re-running any simulations.
#
# Estimated wall time: ~2 h (385/3584 params in 13 min observed on tcn668).
#
# Usage:
#   sbatch --account=gisr129479 scripts/snellius_pawn_analyse.sh
#
#SBATCH --job-name=pawn_analyse
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=192
#SBATCH --exclusive
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

uv run spatcoop sensitivity analyse \
    --out-dir /scratch-shared/lschoonheid/results/sa/linear_pawn \
    --raw-dir /scratch-shared/lschoonheid/results/raw \
    --recompute

echo "[pawn_analyse] Done: $(date)"
echo ""
echo "Results saved to /scratch-shared/lschoonheid/results/sa/linear_pawn/"
