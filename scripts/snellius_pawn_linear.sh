#!/bin/bash
# Single-node PAWN sensitivity analysis — linear risk phase.
#
# Parameters varied: beta [0.1, 10], p_max [0, 1], T_over_E [0.4, 0.9], ell [0, 1]
# Fixed (non-default): L=200, sigma=0.1, eta=0.03, initial_mix=thirds (headline A+ run).
#   For ablation (no flood-env feedback): change --fix eta:0.03 to --fix eta:0.0
#   For compute-heavy sweeps: change --fix L:200 to --fix L:150
#
# Output keys (curated headline set): resilience, flood_rate, mean_env,
#   mean_fitness, mean_payoff, coop_frac, p_span_UC, p_span_CC, gini_wealth,
#   interface_density. All summary stats are saved in the checkpoints regardless,
#   so further OPs can be added later with `sensitivity analyse --recompute`
#   (or `--all-keys`) without re-simulating — see make_sa_plots_all.sh.
# Method: PAWN (Latin Hypercube, N=3072 total samples).
#   N=3072 = 512 * (4+2), matching Saltelli-equivalent coverage per Debraj's formula.
#   Total episodes = N * n_seeds = 3072 * 20 = 61,440.
#   At L=200, 1500 gens, 16 CPUs: estimated ~4–6 h wall time.
#   Prefer snellius_sobol_linear.sh for Sobol indices; use this for PAWN-specific diagnostics.
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
#   spatcoop sensitivity analyse --out-dir /scatch-shared/lschoonheid/results/sa/linear_pawn
#
#SBATCH --job-name=spatcoop_pawn_linear
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=08:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

set -euo pipefail

mkdir -p logs /scatch-shared/lschoonheid/results/sa/linear_pawn

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
    --N 3072 \
    --n-seeds 20 \
    --n-jobs "$SLURM_CPUS_PER_TASK" \
    --fix L:200 \
    --fix sigma:0.1 \
    --fix eta:0.03 \
    --fix initial_mix:thirds \
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
    --out-dir /scatch-shared/lschoonheid/results/sa/linear_pawn

echo "[pawn_linear] Done: $(date)"
echo ""
echo "Results saved to /scatch-shared/lschoonheid/results/sa/linear_pawn/"
echo "To print indices:"
echo "  spatcoop sensitivity analyse --out-dir /scatch-shared/lschoonheid/results/sa/linear_pawn"
