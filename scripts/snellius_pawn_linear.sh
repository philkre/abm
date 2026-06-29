#!/bin/bash
# Single-node PAWN sensitivity analysis — linear risk phase (v2, 2026-06-27).
#
# Parameters varied (5, matching snellius_sobol_linear.sh):
#   beta     [0.1, 10]    — Fermi selection strength
#   p_max    [0,   1]     — maximum disaster probability
#   T_over_E [0.2, 0.9]  — threshold/group-income; T=T_over_E*5; covers NetLogo≈0.34
#   b        [1,  30]     — Wiener drift (income); collapse at b≈1, oscillatory at b≥4
#   eta      [0,  0.020]  — flood→env damage; NetLogo=0.005
#
# Fixed (NetLogo-verified oscillatory-regime defaults):
#   L=200, sigma=0.1, c_bar=0.75, ell=0.64, initial_mix=thirds
#   delta=0.042, gamma=0.018, kappa=0.1  (asymmetric env; NetLogo values)
#   lambda_mode=lognormal, lambda_mean=2.25, lambda_sigma=0.5  (Kahneman–Tversky
#     heterogeneous loss aversion — the second heterogeneity axis beyond wealth)
#
# Method: PAWN (Latin Hypercube, N=3584 total samples).
#   N=3584 = 512 * (5+2), preserving per-dimension coverage vs old N=3072 for 4 params.
#   Total episodes = N * n_seeds = 3584 * 20 = 71,680.
#   At L=200, 1500 gens, 192 CPUs: estimated ~6–8 h wall time.
#
# Why single-node (not array) for PAWN:
#   LHS is not deterministic; array tasks would each generate a different X,
#   producing incompatible slices. Saltelli (Sobol) is deterministic → safe for arrays.
#
# Usage:
#   sbatch scripts/snellius_pawn_linear.sh
#
# After completion:
#   spatcoop sensitivity analyse --out-dir /scratch-shared/lschoonheid/results/sa/linear_pawn
#
#SBATCH --job-name=pawn_linear_v2
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

mkdir -p logs /scratch-shared/lschoonheid/results/sa/linear_pawn /scratch-shared/lschoonheid/results/raw

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[pawn_linear] Starting PAWN SA v2 — linear risk phase (5 params)"
echo "  Host:       $(hostname)"
echo "  CPUs:       $SLURM_CPUS_PER_TASK"
echo "  Started:    $(date)"
echo "  Params:     beta p_max T_over_E b eta"
echo "  Fixed env:  delta=0.042 gamma=0.018 kappa=0.1 (NetLogo oscillatory regime)"

uv run spatcoop sensitivity run \
    --vary beta:0.1:10.0 \
    --vary p_max:0.0:1.0 \
    --vary T_over_E:0.2:0.9 \
    --vary b:1.0:30.0 \
    --vary eta:0.0:0.020 \
    --method pawn \
    --N 3584 \
    --n-seeds 20 \
    --n-jobs "$SLURM_CPUS_PER_TASK" \
    --fix L:200 \
    --fix sigma:0.1 \
    --fix c_bar:0.75 \
    --fix ell:0.64 \
    --fix delta:0.042 \
    --fix gamma:0.018 \
    --fix kappa:0.1 \
    --fix initial_mix:thirds \
    --fix lambda_mode:lognormal \
    --fix lambda_mean:2.25 \
    --fix lambda_sigma:0.5 \
    --output-key resilience \
    --output-key flood_rate \
    --output-key mean_env \
    --output-key mean_env_std \
    --output-key coop_frac \
    --output-key coop_frac_std \
    --output-key p_span_UC \
    --output-key p_span_CC \
    --output-key interface_density \
    --output-key mean_wealth \
    --output-key mean_wealth_std \
    --output-key gini_wealth \
    --output-key mean_fitness \
    --output-key mean_payoff \
    --out-dir /scratch-shared/lschoonheid/results/sa/linear_pawn \
    --raw-dir /scratch-shared/lschoonheid/results/raw

echo "[pawn_linear] Done: $(date)"
echo ""
echo "Results saved to /scratch-shared/lschoonheid/results/sa/linear_pawn/"
echo "To print indices:"
echo "  spatcoop sensitivity analyse --out-dir /scratch-shared/lschoonheid/results/sa/linear_pawn"
