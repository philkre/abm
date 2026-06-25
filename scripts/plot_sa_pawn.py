"""Plot PAWN sensitivity analysis results from a results directory.

Usage:
    uv run python scripts/plot_sa_pawn.py [results_dir]

Defaults to results/sa/linear_pawn/ if no argument given.
Saves pawn_sensitivity.png in the results directory.
"""

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── display config ────────────────────────────────────────────────────────────

PARAM_LABELS = {
    "beta": r"$\beta$ (Fermi strength)",
    "p_max": r"$p_{\max}$ (max flood prob.)",
    "T_over_E": r"$T/E$ (threshold ratio)",
    "ell": r"$\ell$ (loss fraction)",
}

OUTPUT_LABELS = {
    "resilience": "Resilience",
    "flood_rate": "Flood rate",
    "mean_env": "Mean env.",
}

# Colour per output metric
OUTPUT_COLORS = {
    "resilience": "#2c7bb6",
    "flood_rate": "#d7191c",
    "mean_env": "#1a9641",
}

SIGNIFICANCE_THRESHOLD = 0.1  # conventional PAWN cut-off


# ── data loading ──────────────────────────────────────────────────────────────


def load_pawn_results(results_dir: Path) -> dict[str, dict]:
    """Load all pawn_*.json files from results_dir, keyed by output_key."""
    results = {}
    for path in sorted(results_dir.glob("pawn_*.json")):
        with open(path) as f:
            data = json.load(f)
        key = data["output_key"]
        results[key] = data
    return results


# ── figure: grouped bar chart + heatmap ──────────────────────────────────────


def plot_pawn(results: dict[str, dict], out_path: Path) -> None:
    param_names = results[next(iter(results))]["problem"]["names"]
    n_params = len(param_names)
    output_keys = list(results.keys())
    n_outputs = len(output_keys)

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(13, 5),
        gridspec_kw={"width_ratios": [3, 1.5]},
    )
    fig.subplots_adjust(wspace=0.35)

    # ── left: grouped bar chart ───────────────────────────────────────────────
    ax = axes[0]

    bar_width = 0.22
    x = np.arange(n_params)
    offsets = np.linspace(
        -(n_outputs - 1) * bar_width / 2,
        (n_outputs - 1) * bar_width / 2,
        n_outputs,
    )

    for i, key in enumerate(output_keys):
        d = results[key]
        ks_mean = np.array(d["KS_mean"])
        ks_min = np.array(d["KS_min"])
        ks_max = np.array(d["KS_max"])

        err_low = ks_mean - ks_min
        err_high = ks_max - ks_mean

        color = OUTPUT_COLORS.get(key, f"C{i}")
        bars = ax.bar(
            x + offsets[i],
            ks_mean,
            width=bar_width,
            color=color,
            alpha=0.85,
            label=OUTPUT_LABELS.get(key, key),
            zorder=3,
        )
        ax.errorbar(
            x + offsets[i],
            ks_mean,
            yerr=[err_low, err_high],
            fmt="none",
            color="black",
            capsize=3,
            linewidth=0.9,
            zorder=4,
        )

    # significance threshold line
    ax.axhline(
        SIGNIFICANCE_THRESHOLD,
        color="grey",
        linestyle="--",
        linewidth=1.1,
        zorder=2,
        label=f"Significance threshold ({SIGNIFICANCE_THRESHOLD})",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(
        [PARAM_LABELS.get(p, p) for p in param_names],
        fontsize=10,
    )
    ax.set_ylabel("PAWN KS statistic (mean across seeds)", fontsize=10)
    ax.set_title(
        "PAWN sensitivity — linear risk phase",
        fontsize=11,
        fontweight="bold",
    )
    ax.set_ylim(0, 1.0)
    ax.legend(fontsize=9, framealpha=0.9)
    ax.grid(axis="y", alpha=0.35, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)

    # ── right: heatmap ────────────────────────────────────────────────────────
    ax2 = axes[1]

    matrix = np.array([results[key]["KS_mean"] for key in output_keys])  # shape: (n_outputs, n_params)

    im = ax2.imshow(
        matrix,
        aspect="auto",
        cmap="YlOrRd",
        vmin=0,
        vmax=1,
    )

    # annotate cells
    for row in range(n_outputs):
        for col in range(n_params):
            val = matrix[row, col]
            text_color = "black" if val < 0.55 else "white"
            ax2.text(
                col,
                row,
                f"{val:.2f}",
                ha="center",
                va="center",
                fontsize=9,
                color=text_color,
                fontweight="bold",
            )

    ax2.set_xticks(range(n_params))
    ax2.set_xticklabels(
        [PARAM_LABELS.get(p, p) for p in param_names],
        rotation=30,
        ha="right",
        fontsize=9,
    )
    ax2.set_yticks(range(n_outputs))
    ax2.set_yticklabels(
        [OUTPUT_LABELS.get(k, k) for k in output_keys],
        fontsize=9,
    )
    ax2.set_title("KS mean (heatmap)", fontsize=11, fontweight="bold")
    fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.04, label="KS statistic")

    # ── save ─────────────────────────────────────────────────────────────────
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved → {out_path}")


# ── ranking summary ───────────────────────────────────────────────────────────


def print_ranking(results: dict[str, dict]) -> None:
    param_names = results[next(iter(results))]["problem"]["names"]
    print("\nPAWN sensitivity ranking (KS_mean, highest first)")
    print("=" * 55)
    for key, label in OUTPUT_LABELS.items():
        if key not in results:
            continue
        d = results[key]
        ks = d["KS_mean"]
        ranked = sorted(zip(param_names, ks), key=lambda x: -x[1])
        print(f"\n  {label}:")
        for param, val in ranked:
            marker = " ◄ dominant" if val == max(ks) else ""
            print(f"    {PARAM_LABELS.get(param, param):35s}  {val:.3f}{marker}")


# ── main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    results_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/sa/linear_pawn")
    results_dir = Path(results_dir)

    if not results_dir.exists():
        sys.exit(f"Directory not found: {results_dir}")

    results = load_pawn_results(results_dir)
    if not results:
        sys.exit(f"No pawn_*.json files found in {results_dir}")

    print_ranking(results)

    out_path = results_dir / "pawn_sensitivity.png"
    plot_pawn(results, out_path)


if __name__ == "__main__":
    main()
