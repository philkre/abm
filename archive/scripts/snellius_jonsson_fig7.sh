#!/bin/bash
# Snellius job: Jonsson & Jonsson (2025) Fig 7 replication.
#
# Sweeps UC fraction 0→1 (step 0.05, 21 points), 1000 seeds per point,
# L=5 (25-agent well-mixed group), frozen strategies.
#
# Wall-time estimate: 21 000 runs × ~0.2 s each / 32 cores ≈ 130 s.
# Requesting 15 min to be safe.
#
# Usage (from philkre-abm root):
#   mkdir -p logs
#   sbatch scripts/snellius_jonsson_fig7.sh
#
# Output: results/figures/jonsson_fig7_replication.png
#
#SBATCH --job-name=jonsson_fig7
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --time=00:15:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j_jonsson_fig7.out
#SBATCH --error=logs/%j_jonsson_fig7.err

set -euo pipefail

mkdir -p logs results/figures

module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

uv run python scripts/jonsson_fig7_validation.py \
    --L 5 \
    --seeds 1000 \
    --workers 32 \
    --step 0.05
