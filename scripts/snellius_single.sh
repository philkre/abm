#!/bin/bash
# Single-node batch job for the linear-risk SA.
# Wall time: ~2h at L=150, N=512, 50 seeds, 32 CPUs.
#SBATCH --job-name=spatcoop_sa
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --partition=thin
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

module load Python/3.11.3-GCCcore-12.3.0

uv run spatcoop run-batch --phase linear --N 64 --L 150 --n-gens 1500 --n-seeds 50
