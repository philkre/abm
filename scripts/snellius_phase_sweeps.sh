#!/bin/bash
# Three-phase SA follow-up sweeps (from SA results showing T_over_E and beta dominate).
#
# Phase 1: T_over_E ∈ [0.3, 0.8] — find where threshold becomes clearable.
# Phase 2: eta ∈ [0.0, 0.2] at T_over_E=t_star — check erosion dynamics.
# Phase 3: lambda_mean ∈ [1.0, 3.0] with cc_d mix — can loss-averse CC bootstrap?
#
# After phase 1 completes, check op_vs_T_over_E.pdf and update --t-star if needed,
# then re-run phases 2 & 3 only via:
#   uv run spatcoop param-sweep --only eta      (at desired T)
#   uv run spatcoop param-sweep --only lambda_mean --initial-mix cc_d  (at desired T)
#
# Usage:
#   sbatch scripts/snellius_phase_sweeps.sh
#
#SBATCH --job-name=phase_sweeps
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=24
#SBATCH --time=03:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

set -euo pipefail

cd /gpfs/home6/pkreiter/abm
mkdir -p logs results/figures

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[phase-sweep] Starting — $(date)"

uv run spatcoop phase-sweep \
    --L 200 \
    --n-gens 1500 \
    --n-seeds 10 \
    --n-points 21 \
    --eta 0.03 \
    --sigma 0.1 \
    --t-star 0.55 \
    --n-jobs "$SLURM_CPUS_PER_TASK"

echo "[phase-sweep] Done — $(date). Figures in results/figures/."
