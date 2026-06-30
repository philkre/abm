#!/bin/bash
# 2-parameter Sobol SA over (ell × b) for wealth and strategy diagnostic plots.
#
# Purpose: generate data for plot_wealth_diagnostics.py — the three diagnostic
#   figures that cannot be derived from the 5-param headline SA because ell is
#   fixed there (ell=0.64).  By varying ell and b jointly we can show:
#     1. How ell drives wealth inequality WITHIN each phase (b=collapse / oscillatory)
#     2. How b determines the dominant wealth-oscillation period (FFT)
#     3. How strategy shares distribute in (b, ell) space
#
# Parameters varied:
#   ell  [0.1, 0.9]  — flood loss fraction (main driver of wealth inequality)
#   b    [1,  25]    — Wiener drift (income); phase boundary at b≈4
#
# Fixed at NetLogo-verified cooperative-regime values so that the full phase
#   range [collapse → oscillatory] is captured as b is swept:
#   L=200, n_gens=1500, T=1.7 (= T/E≈0.34), p_max=1.0, eta=0.005,
#   sigma=0.1, c_bar=0.75, delta=0.042, gamma=0.018, kappa=0.1,
#   initial_mix=thirds, lambda_mode=lognormal, lambda_mean=2.25
#
# Compute (N=512, D=2):
#   Saltelli samples = N * (D+2) = 512 * 4 = 2,048
#   Total episodes   = 2,048 * 20 seeds = 40,960
#   At L=200, 1500 gens, 96 CPUs: estimated ~2–3 h wall time.
#
# Usage:
#   sbatch scripts/snellius_ell_b_sa.sh
#
# After completion, generate diagnostic plots locally or on the login node:
#   uv run python scripts/plot_wealth_diagnostics.py
#
#SBATCH --job-name=ell_b_sa_spatcoop
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=96
#SBATCH --time=04:00:00
#SBATCH --partition=genoa
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err

set -euo pipefail

OUTDIR=/scratch-shared/lschoonheid/results/ell_b_sa
RAWDIR=/scratch-shared/lschoonheid/results/ell_b_sa/raw

mkdir -p logs "$OUTDIR" "$RAWDIR"

module load 2024
module load Python/3.13.1-GCCcore-13.3.0 2>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"

echo "[ell_b_sa] Starting ell×b diagnostic SA"
echo "  Host:    $(hostname)"
echo "  CPUs:    $SLURM_CPUS_PER_TASK"
echo "  Started: $(date)"
echo "  Varying: ell [0.1, 0.9], b [1, 25]"
echo "  Fixed:   T=1.7 (T/E≈0.34), delta=0.042, gamma=0.018, eta=0.005, kappa=0.1"

uv run spatcoop sensitivity run \
    --vary ell:0.1:0.9 \
    --vary b:1.0:25.0 \
    --method sobol \
    --N 512 \
    --n-seeds 20 \
    --n-jobs "$SLURM_CPUS_PER_TASK" \
    --fix L:200 \
    --fix T:1.7 \
    --fix p_max:1.0 \
    --fix eta:0.005 \
    --fix sigma:0.1 \
    --fix c_bar:0.75 \
    --fix delta:0.042 \
    --fix gamma:0.018 \
    --fix kappa:0.1 \
    --fix initial_mix:thirds \
    --fix lambda_mode:lognormal \
    --fix lambda_mean:2.25 \
    --output-key gini_wealth \
    --output-key mean_wealth \
    --output-key mean_wealth_std \
    --output-key coop_frac \
    --output-key resilience \
    --output-key mean_env \
    --output-key flood_rate \
    --out-dir "$OUTDIR" \
    --raw-dir "$RAWDIR"

echo "[ell_b_sa] Done: $(date)"
echo ""
echo "Results saved to $OUTDIR"
echo "Generate diagnostic plots:"
echo "  uv run python scripts/plot_wealth_diagnostics.py"
