"""Plotting helpers for simulation output."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


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


# UC=steelblue  CC=orange  FR=crimson
_LATTICE_CMAP = mcolors.ListedColormap(["steelblue", "orange", "crimson"])
_LATTICE_NORM = mcolors.BoundaryNorm([0, 1, 2, 3], 3)


def plot_lattice_evolution(
    result: dict,
    output: Path,
) -> None:
    """Plot type frequencies and group success rate over evolutionary time.

    Args:
        result: Dict returned by ``run_evolution`` (keys: uc_freq, cc_freq,
                fr_freq, success_rate).
        output: Path to save the PNG.
    """
    gens = np.arange(len(result["uc_freq"]))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

    ax1.plot(gens, result["uc_freq"], color="steelblue", lw=2, label="UC")
    ax1.plot(gens, result["cc_freq"], color="orange",    lw=2, label="CC")
    ax1.plot(gens, result["fr_freq"], color="crimson",   lw=2, label="FR")
    ax1.set_ylabel("Type frequency")
    ax1.set_ylim(0, 1.05)
    ax1.legend(loc="upper right")
    ax1.set_title("Spatial Fermi evolution — Von Neumann lattice")

    ax2.plot(gens, result["success_rate"], color="black", lw=1.5)
    ax2.set_ylabel("Fraction successful groups")
    ax2.set_xlabel("Generation")
    ax2.set_ylim(0, 1.05)

    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def plot_grid_snapshot(
    type_grid: np.ndarray,
    gen: int,
    output: Path,
) -> None:
    """Render a single lattice state as a colour grid.

    UC = blue, CC = orange, FR = red.

    Args:
        type_grid: (L, L) int array of type codes (0=UC, 1=CC, 2=FR).
        gen: Generation number shown in the title.
        output: Path to save the PNG.
    """
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.imshow(type_grid, cmap=_LATTICE_CMAP, norm=_LATTICE_NORM,
              interpolation="nearest")
    ax.set_title(f"Lattice — generation {gen}")
    ax.axis("off")
    # Legend patches
    patches = [
        plt.Rectangle((0, 0), 1, 1, fc="steelblue", label="UC"),
        plt.Rectangle((0, 0), 1, 1, fc="orange",    label="CC"),
        plt.Rectangle((0, 0), 1, 1, fc="crimson",   label="FR"),
    ]
    ax.legend(handles=patches, loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def plot_grid_mosaic(
    snapshots: list[tuple[int, np.ndarray]],
    output: Path,
    max_panels: int = 9,
) -> None:
    """Grid of lattice snapshots at different generations.

    Args:
        snapshots: List of (generation, type_grid) tuples from run_evolution.
        output: Path to save the PNG.
        max_panels: Maximum number of panels to show (evenly spaced).
    """
    idxs = np.round(np.linspace(0, len(snapshots) - 1, min(max_panels, len(snapshots)))).astype(int)
    chosen = [snapshots[i] for i in idxs]
    ncols = min(3, len(chosen))
    nrows = (len(chosen) + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4 * nrows))
    axes = np.array(axes).flatten()

    for ax, (gen, grid) in zip(axes, chosen):
        ax.imshow(grid, cmap=_LATTICE_CMAP, norm=_LATTICE_NORM, interpolation="nearest")
        ax.set_title(f"gen {gen}", fontsize=9)
        ax.axis("off")
    for ax in axes[len(chosen):]:
        ax.axis("off")

    fig.suptitle("Lattice evolution snapshots (UC=blue, CC=orange, FR=red)")
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
