"""Plotting helpers for simulation output."""

from pathlib import Path

import matplotlib.pyplot as plt


def plot_fig7(
    uc_props: list[float],
    success_rates: list[float],
    output: Path,
) -> None:
    """Reproduce Fig 7: fraction of successful groups vs UC proportion.

    Args:
        uc_props: UC proportion values (x-axis).
        success_rates: Corresponding success fractions (y-axis).
        output: Path to save the PNG.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(uc_props, success_rates, color="steelblue", lw=2, label="Simulation")
    ax.axvline(0.56, color="black", lw=1.5, ls="--", label="Empirical UC proportion (0.56)")
    ax.set_xlabel("Proportion unconditional cooperators")
    ax.set_ylabel("Proportion successful groups")
    ax.set_title("Fig 7 — Cooperation in the face of disaster")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
