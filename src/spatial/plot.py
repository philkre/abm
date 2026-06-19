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

    fig, axes = plt.subplots(4, 1, figsize=(6, 9), sharex=True)

    # ---- Panel 1: UC, CC, cooperation + mean EHI (second y-axis) ----
    ax0 = axes[0]
    ax0.plot(df.index, df["uc_rate"], label="UC", color="tab:blue")
    ax0.plot(df.index, df["cc_rate"], label="CC", color="tab:orange", linestyle="--")
    ax0.plot(
        df.index,
        df["cooperation_rate"],
        label="Coop (UC+CC)",
        color="tab:green",
        linestyle=":",
    )
    ax0.set_ylabel("Strategy fraction")
    ax0.set_ylim(0, 1)

    ax0_ehi = ax0.twinx()
    ax0_ehi.plot(
        df.index,
        df["mean_ehi"],
        label="Mean EHI",
        color="black",
        linestyle="-.",
    )
    ax0_ehi.set_ylabel("Mean EHI")

    # combine legends from both axes
    lines1, labels1 = ax0.get_legend_handles_labels()
    lines2, labels2 = ax0_ehi.get_legend_handles_labels()
    ax0.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper right")

    # ---- Panel 2: mean wealth ----
    axes[1].plot(df.index, df["mean_wealth"])
    axes[1].set_ylabel("Mean wealth")

    # ---- Panel 3: disaster rate ----
    axes[2].plot(df.index, df["disaster_rate"])
    axes[2].set_ylabel("Disaster rate")
    axes[2].set_ylim(0, 1)

    # (You can reuse panel 4 for anything else, or drop to 3 panels.)

    axes[3].axis("off")  # optional: if you don’t need a 4th panel
    axes[3].set_xlabel("Step")

    fig.suptitle("Spatial TPGG with environmental feedback — sanity check")
    plt.tight_layout()

    out = PLOT_DIR / "spatial_tpgg_sanity.png"
    plt.savefig(out, dpi=150)
    print(f"Saved plot to {out}")

if __name__ == "__main__":
    main()
