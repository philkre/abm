#!/bin/bash
# Submit the full SA pipeline as a chain of 2-hour jobs.
#
# Sobol requires ~7-9 h of compute; PAWN ~2 h.  Both scripts checkpoint each
# simulation run individually, so a chain of jobs naturally continues from
# where the previous one stopped — no manual restart needed.
#
# Usage:
#   bash scripts/submit_sa_jobs.sh                        # uses default account
#   bash scripts/submit_sa_jobs.sh --account=gisr129479   # explicit account
#
# All extra arguments are forwarded to every sbatch call.

set -euo pipefail

EXTRA_ARGS=("$@")          # e.g. --account=gisr129479
N_SOBOL_JOBS=5             # 5 × 2 h = 10 h budget; adjust if runs complete faster

cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "=== Sobol chain (${N_SOBOL_JOBS} × 2 h) ==="
J=$(sbatch --parsable "${EXTRA_ARGS[@]}" scripts/snellius_sobol_linear.sh)
echo "  job 1: $J"
for i in $(seq 2 $N_SOBOL_JOBS); do
    J=$(sbatch --parsable --dependency=afterany:"$J" "${EXTRA_ARGS[@]}" scripts/snellius_sobol_linear.sh)
    echo "  job $i: $J"
done
echo "  Sobol chain: last job $J"

echo ""
echo "=== PAWN (1 × 2 h) ==="
JP=$(sbatch --parsable "${EXTRA_ARGS[@]}" scripts/snellius_pawn_linear.sh)
echo "  job: $JP"

echo ""
echo "All jobs submitted. Monitor with:"
echo "  squeue --me"
echo ""
echo "After all jobs finish, fetch results and generate plots:"
echo "  spatcoop sensitivity analyse --out-dir /scratch-shared/.../results/sa/linear_sobol"
echo "  spatcoop sensitivity analyse --out-dir /scratch-shared/.../results/sa/linear_pawn"
