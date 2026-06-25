#!/usr/bin/env bash
# Plot the curated SA index bars from finished sensitivity runs.
#
# Cheap: reads the {method}_{key}.json files already written by the SA jobs — no
# simulation. Safe to run on a login node or locally. For the full all-OP
# analysis (recomputes indices for every order parameter) use make_sa_plots_all.sh.
#
# Usage:
#   bash scripts/make_sa_plots.sh
#
# Figures are written to results/figures/ (sa_{method}_{key}.pdf), plus the rich
# combined PAWN figure (pawn_sensitivity.png) in the results dir.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

export PATH="$HOME/.local/bin:$PATH"

# (results dir, method) pairs to plot.
PAIRS=(
    "results/sa/linear_sobol sobol"
    "results/sa/linear_pawn  pawn"
)

for pair in "${PAIRS[@]}"; do
    read -r dir method <<<"$pair"
    if [[ ! -d "$dir" ]]; then
        echo "[make_sa_plots] Skipping missing dir: $dir"
        continue
    fi
    echo "[make_sa_plots] Plotting curated $method bars from $dir"
    uv run spatcoop plot-sa --out-dir "$dir" --method "$method"
done

# Rich combined PAWN figure (grouped bars + KS heatmap).
if [[ -d results/sa/linear_pawn ]]; then
    echo "[make_sa_plots] Rendering combined PAWN figure"
    uv run python scripts/plot_sa_pawn.py results/sa/linear_pawn
fi

echo "[make_sa_plots] Done. Figures in results/figures/ and results/sa/linear_pawn/."
