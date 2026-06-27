#!/bin/bash
# Single-node Sobol sensitivity analysis — linear risk phase (v2, 2026-06-27).
#
# Parameters varied (5):
#   beta     [0.1, 10]    — Fermi selection strength
#   p_max    [0,   1]     — maximum disaster probability
#   T_over_E [0.2, 0.9]  — threshold/group-income; covers NetLogo≈0.34; T=T_over_E*5
#   b        [1,  30]     — Wiener drift (income); collapse regime at b≈1, oscillatory at b≥4
#   eta      [0,  0.020]  — flood→env damage; NetLogo=0.005; [0,0.020] = 4× headroom
#
# Fixed (NetLogo-verified oscillatory-regime defaults):
#   L=200, sigma=0.1, c_bar=0.75, ell=0.64, initial_mix=thirds
#   delta=0.042, gamma=0.018, kappa=0.1  (asymmetric env; NetLogo values)
#   lambda_mode=lognormal, lambda_mean=2.25, lambda_sigma=0.5  (Kahneman–Tversky
#     heterogeneous loss aversion — the second heterogeneity axis beyond wealth)
#
# Rationale for param changes vs v1:
#   - Replaced ell with b: local SA (2026-06-27) showed ell only affects Wealth inequality;
#     b is the primary phase-transition lever (c_bar/b ratio).
#   - Replaced ell with eta: flood→env coupling is an independent mechanism axis.
#   - Extended T_over_E from [0.4, 0.9] to [0.2, 0.9] to include NetLogo's T/E≈0.34.
#   - Fixed env params at NetLogo values (delta=0.042, gamma=0.018, kappa=0.1) so that
#     the oscillatory cooperative phase is accessible at b≥4 (verified 2026-06-27).
#   - Kept heterogeneous λ: lambda_mode=lognormal, lambda_mean=2.25, lambda_sigma=0.5.
#
# Compute budget (5 params, N=5120):
#   Total Saltelli samples = N * (D+2) = 5120 * 7 = 35,840
#   Total episodes         = 35,840 * 20 seeds = 716,800
#   At L=200, 1500 gens, 192 CPUs: estimated ~7 h wall time.
#
# Output keys (14 total — superset of local_money_sa outputs):
#   Ecological:  resilience, flood_rate, mean_env, mean_env_std
#   Cooperation: coop_frac, coop_frac_std, p_span_UC, p_span_CC, interface_density
#   Wealth:      mean_wealth, mean_wealth_std, gini_wealth
#   Fitness:     mean_fitness, mean_payoff
#   All summary stats are saved in checkpoints → more keys via `sensitivity analyse --recompute`
#   without re-simulating (see make_sa_plots_all.sh).
#
# Usage:
#   sbatch scripts/snellius_sobol_linear.sh
#
# After completion:
#   spatcoop sensitivity analyse --out-dir /scratch-shared/lschoonheid/results/sa/linear_sobol
#
#SBATCH --job-name=sobol_linear_v2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=192
#SBATCH --time=09:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

set -euo pipefail

mkdir -p logs /scratch-shared/lschoonheid/results/sa/linear_sobol /scratch-shared/lschoonheid/results/raw

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true

export PATH="$HOME/.local/bin:$PATH"

echo "[sobol_linear] Starting Sobol SA v2 — linear risk phase (5 params)"
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
    --method sobol \
    --N 5120 \
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
    --out-dir /scratch-shared/lschoonheid/results/sa/linear_sobol \
    --raw-dir /scratch-shared/lschoonheid/results/raw

echo "[sobol_linear] Done: $(date)"
echo ""
echo "Results saved to /scratch-shared/lschoonheid/results/sa/linear_sobol/"
echo "To print indices:"
echo "  spatcoop sensitivity analyse --out-dir /scratch-shared/lschoonheid/results/sa/linear_sobol"
