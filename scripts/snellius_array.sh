#!/bin/bash
# Array job for L=200 or large N: splits the Sobol sample across nodes.
# Each task handles (total_samples / n_tasks) parameter points.
# After all tasks finish, run `spatcoop analyse --phase linear --N 512` locally.
#SBATCH --job-name=spatcoop_array
#SBATCH --array=0-95
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --time=02:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%A_%a.out
#SBATCH --error=logs/%A_%a.err

module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

mkdir -p logs

uv run spatcoop run-batch --phase linear --N 64 --L 150 --n-gens 1500 --n-seeds 50 \
    --task-id "$SLURM_ARRAY_TASK_ID" --n-tasks 96
