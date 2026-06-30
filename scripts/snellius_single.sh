#!/bin/bash
# Single-node batch job for the linear-risk SA.
# Wall time: ~2h at L=150, N=512, 50 seeds, 32 CPUs.
#SBATCH --job-name=sa_spatcoop
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --time=04:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

mkdir -p logs  # for any in-script writes; logs/ must exist before sbatch is called

module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

uv run spatcoop run-batch --phase linear --N 64 --L 150 --n-gens 1500 --n-seeds 50
