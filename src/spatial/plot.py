"""Sanity-check plots for the spatial threshold PGG.

Run after `uv run spatial-run` has produced data/spatial_tpgg.pkl.
"""

import shutil
from pathlib import Path

import matplotlib.pyplot as plt
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


def main() -> None:
    df = load(DATA_DIR / "spatial_tpgg.pkl")

    fig, axes = plt.subplots(3, 1, figsize=(6, 7), sharex=True)

    axes[0].plot(df.index, df["cooperation_rate"])
    axes[0].set_ylabel("Cooperation rate")
    axes[0].set_ylim(0, 1)

    axes[1].plot(df.index, df["mean_wealth"])
    axes[1].set_ylabel("Mean wealth")

    axes[2].plot(df.index, df["disaster_rate"])
    axes[2].set_ylabel("Disaster rate")
    axes[2].set_ylim(0, 1)
    axes[2].set_xlabel("Step")

    fig.suptitle("Spatial threshold PGG — sanity check")
    plt.tight_layout()

    out = PLOT_DIR / "spatial_tpgg_sanity.png"
    plt.savefig(out, dpi=150)
    print(f"Saved plot to {out}")


if __name__ == "__main__":
    main()
