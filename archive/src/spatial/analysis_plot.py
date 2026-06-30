"""Plot spatial TPGG sweep results from data/analysis_{experiment}.pkl.

Run after spatial-analysis has produced the data file.

Usage:
    uv run python src/spatial/analysis_plot.py --experiment uc_dominance
    uv run python src/spatial/analysis_plot.py --experiment threshold
    uv run python src/spatial/analysis_plot.py --experiment beta
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from joblib import load

import scienceplots  # noqa: F401

DATA_DIR = Path(__file__).parent.parent.parent / "data"
PLOT_DIR = Path(__file__).parent.parent.parent / "plots"
PLOT_DIR.mkdir(exist_ok=True)

styles = (
    ["science"]
    if (shutil.which("latex") and shutil.which("dvipng"))
    else ["science", "no-latex"]
)
plt.style.use(styles)


# ──────────────────────────────────────────────────────────────────────────────
# Plot functions
# ──────────────────────────────────────────────────────────────────────────────

def plot_uc_dominance(df) -> None:
    """Two-panel line plot: UC and CC rates vs disaster_prob at steady state."""
    grouped = (
        df.groupby(["disaster_prob", "initial_uc_fraction"])
        .mean(numeric_only=True)
        .reset_index()
    )
    fractions = sorted(grouped["initial_uc_fraction"].unique())

    fig, axes = plt.subplots(1, 2, figsize=(9, 4))

    for frac in fractions:
        sub = grouped[grouped["initial_uc_fraction"] == frac]
        axes[0].plot(sub["disaster_prob"], sub["uc_rate"],
                     marker="o", ms=4, label=f"init={frac:.0%}")
        axes[1].plot(sub["disaster_prob"], sub["cc_rate"],
                     marker="s", ms=4, linestyle="--", label=f"init={frac:.0%}")

    for ax, title, ylabel in zip(
        axes,
        ["UC rate at steady state", "CC rate at steady state"],
        ["UC fraction", "CC fraction"],
    ):
        ax.set_xlabel("Disaster probability")
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=10)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.legend(fontsize=8, title="Initial UC fraction")

    fig.suptitle("Spatial TPGG: UC dominance under stochastic disaster risk", fontsize=11)
    plt.tight_layout()
    out = PLOT_DIR / "analysis_uc_dominance.png"
    plt.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved {out}")


def _heatmap(df, x_col: str, y_col: str, z_col: str, title: str, out_name: str) -> None:
    grouped = df.groupby([x_col, y_col])[z_col].mean().reset_index()
    x_vals = sorted(grouped[x_col].unique())
    y_vals = sorted(grouped[y_col].unique())

    mat = np.full((len(y_vals), len(x_vals)), np.nan)
    for i, y in enumerate(y_vals):
        for j, x in enumerate(x_vals):
            row = grouped[(grouped[x_col] == x) & (grouped[y_col] == y)]
            if not row.empty:
                mat[i, j] = row[z_col].values[0]

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    im = ax.imshow(mat, origin="lower", aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(x_vals)))
    ax.set_xticklabels([f"{v:.2g}" for v in x_vals], fontsize=8)
    ax.set_yticks(range(len(y_vals)))
    ax.set_yticklabels([f"{v:.2g}" for v in y_vals], fontsize=8)
    ax.set_xlabel(x_col.replace("_", " "))
    ax.set_ylabel(y_col.replace("_", " "))
    ax.set_title(title, fontsize=10)
    plt.colorbar(im, ax=ax, label=z_col.replace("_", " "))
    plt.tight_layout()
    out = PLOT_DIR / out_name
    plt.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved {out}")


def plot_threshold(df) -> None:
    _heatmap(
        df, "threshold", "disaster_prob", "uc_rate",
        "UC rate: threshold tightness vs disaster probability",
        "analysis_threshold.png",
    )


def plot_beta(df) -> None:
    _heatmap(
        df, "beta", "disaster_prob", "uc_rate",
        "UC rate: Fermi selection strength vs disaster probability",
        "analysis_beta.png",
    )


PLOT_DISPATCH = {
    "uc_dominance": plot_uc_dominance,
    "threshold": plot_threshold,
    "beta": plot_beta,
}


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Plot spatial TPGG sweep results")
    parser.add_argument(
        "--experiment",
        choices=list(PLOT_DISPATCH),
        default="uc_dominance",
    )
    args = parser.parse_args()

    pkl = DATA_DIR / f"analysis_{args.experiment}.pkl"
    if not pkl.exists():
        print(f"Data file not found: {pkl}")
        print(f"Run first: uv run spatial-analysis --experiment {args.experiment}")
        return

    df = load(pkl)
    PLOT_DISPATCH[args.experiment](df)


if __name__ == "__main__":
    main()
