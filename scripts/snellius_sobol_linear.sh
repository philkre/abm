#!/bin/bash
# Single-node Sobol sensitivity analysis — linear risk phase.
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
# Method: Sobol (Saltelli sequence, N=512 base).
#   Total samples = N * (D+2) = 512 * 6 = 3,072 per Debraj's formula.
#   Total episodes = 3,072 * 20 = 61,440.
#   At L=200, 1500 gens, 16 CPUs: estimated ~4–6 h wall time.
#
# Why single-node is safe for Sobol:
#   Saltelli sampling is deterministic, so the full X matrix is generated once
#   and each task sees a consistent slice. Array splitting is possible but not
#   needed at this sample size.
#
# Usage:
#   sbatch scripts/snellius_sobol_linear.sh
#
# After completion, print results:
#   spatcoop sensitivity analyse --out-dir results/sa/linear_sobol
#
#SBATCH --job-name=spatcoop_sobol_linear
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=192
#SBATCH --time=06:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

set -euo pipefail

mkdir -p logs results/sa/linear_sobol

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[sobol_linear] Starting Sobol SA — linear risk phase"
echo "  Host:       $(hostname)"
echo "  CPUs:       $SLURM_CPUS_PER_TASK"
echo "  Started:    $(date)"

uv run spatcoop sensitivity run \
    --vary beta:0.1:10.0 \
    --vary p_max:0.0:1.0 \
    --vary T_over_E:0.4:0.9 \
    --vary ell:0.0:1.0 \
    --method sobol \
    --N 5120 \
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
    --out-dir results/sa/linear_sobol

echo "[sobol_linear] Done: $(date)"
echo ""
echo "Results saved to results/sa/linear_sobol/"
echo "To print indices:"
echo "  spatcoop sensitivity analyse --out-dir results/sa/linear_sobol"
