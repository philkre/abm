"""Standalone PAWN heatmap for slide 2 left column.

Styled to match presentation palette (navyblue/goldaccent).
Usage:
    uv run python scripts/plot_sa_heatmap_slide.py [results_dir]
Saves slides/pawn_heatmap.pdf
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

PARAM_LABELS = [
    r"$\beta$",
    r"$p_{\max}$",
    r"$T/E$",
    r"$\ell$",
]
OUTPUT_LABELS = ["Flood rate", "Mean env.", "Resilience"]
OUTPUT_KEYS   = ["flood_rate", "mean_env", "resilience"]

# Presentation palette
NAVYBLUE  = "#1a3a5c"
TEXTGRAY  = "#555555"
FOOTGRAY  = "#888888"


def main() -> None:
    results_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/sa/linear_pawn")
    out_path = Path("slides/pawn_heatmap.pdf")

    results = {}
    for key in OUTPUT_KEYS:
        p = results_dir / f"pawn_{key}.json"
        with open(p) as f:
            results[key] = json.load(f)

    matrix = np.array([results[k]["KS_mean"] for k in OUTPUT_KEYS])  # (3, 4)

    fig, ax = plt.subplots(figsize=(3.6, 2.2))
    fig.patch.set_facecolor("white")

    # YlOrRd but start from very pale yellow
    cmap = plt.get_cmap("YlOrRd")
    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1,
                   interpolation="nearest")

    # Annotate cells
    for r in range(matrix.shape[0]):
        for c in range(matrix.shape[1]):
            val = matrix[r, c]
            color = "white" if val > 0.55 else NAVYBLUE
            ax.text(c, r, f"{val:.2f}", ha="center", va="center",
                    fontsize=8.5, color=color, fontweight="bold",
                    fontfamily="serif")

    ax.set_xticks(range(4))
    ax.set_xticklabels(PARAM_LABELS, fontsize=9, color=NAVYBLUE,
                       fontfamily="serif")
    ax.set_yticks(range(3))
    ax.set_yticklabels(OUTPUT_LABELS, fontsize=8.5, color=TEXTGRAY,
                       fontfamily="serif")
    ax.tick_params(length=0)

    # Thin navy border around each cell
    for spine in ax.spines.values():
        spine.set_edgecolor(NAVYBLUE)
        spine.set_linewidth(0.8)

    # Colorbar
    cb = fig.colorbar(im, ax=ax, fraction=0.038, pad=0.03)
    cb.ax.tick_params(labelsize=7, color=TEXTGRAY)
    cb.set_label("KS statistic", fontsize=7.5, color=TEXTGRAY,
                 fontfamily="serif")
    cb.outline.set_edgecolor(NAVYBLUE)
    cb.outline.set_linewidth(0.6)

    fig.tight_layout(pad=0.4)
    plt.savefig(out_path, dpi=200, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    print(f"Saved → {out_path}")


if __name__ == "__main__":
    main()
