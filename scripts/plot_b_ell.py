"""plot_b_ell.py — Re-plot the b × ell sweep from saved .npz.

Reads results/raw/b_ell_sweep.npz and produces:
  results/figures/b_ell_mean_env.png
  results/figures/b_ell_resilience.png
  results/figures/b_ell_combined.png  (side-by-side)

Usage:
    uv run python scripts/plot_b_ell.py
    uv run python scripts/plot_b_ell.py --data results/raw/b_ell_sweep.npz
    uv run python scripts/plot_b_ell.py --contour --no-combined
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Calibrated b=21 is outside the sweep range [0.1, 2.0], so no marker shown.
FIXED_ELL = 0.64


def _heatmap_ax(
    ax: plt.Axes,
    grid: np.ndarray,
    ell_vals: np.ndarray,
    b_vals: np.ndarray,
    vmin: float,
    vmax: float,
    cmap: str,
    contour: bool,
) -> plt.cm.ScalarMappable:
    im = ax.imshow(
        grid,
        origin="lower",
        aspect="auto",
        extent=[ell_vals[0], ell_vals[-1], b_vals[0], b_vals[-1]],
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        interpolation="nearest",
    )

    if contour:
        levels = np.linspace(vmin, vmax, 9)
        cs = ax.contour(
            np.linspace(ell_vals[0], ell_vals[-1], grid.shape[1]),
            np.linspace(b_vals[0], b_vals[-1], grid.shape[0]),
            grid,
            levels=levels,
            colors="black",
            linewidths=0.5,
            alpha=0.4,
        )
        ax.clabel(cs, fmt="%.2f", fontsize=7)

    ax.set_xlabel("ell  (flood-loss fraction)", fontsize=11)
    ax.set_ylabel("b  (OU income rate)", fontsize=11)
    return im


def plot_combined(
    env_grid: np.ndarray,
    res_grid: np.ndarray,
    ell_vals: np.ndarray,
    b_vals: np.ndarray,
    eta: float,
    out_path: Path,
    contour: bool,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    im0 = _heatmap_ax(axes[0], env_grid, ell_vals, b_vals, -1.0, 1.0, "RdYlGn", contour)
    plt.colorbar(im0, ax=axes[0], label="mean_env (final 200 gens)")
    axes[0].set_title("Environment recovery", fontsize=12)

    im1 = _heatmap_ax(axes[1], res_grid, ell_vals, b_vals, 0.0, 1.0, "RdYlGn", contour)
    plt.colorbar(im1, ax=axes[1], label="resilience (frac pools ≥ T)")
    axes[1].set_title("Group resilience", fontsize=12)

    fig.suptitle(
        f"b × ell operating window  (initial_e=−1, η={eta:.3f} fixed)\n"
        f"ell ∈ [{ell_vals[0]:.2f}, {ell_vals[-1]:.2f}]  "
        f"b ∈ [{b_vals[0]:.2f}, {b_vals[-1]:.2f}]  "
        f"grid {len(ell_vals)}×{len(b_vals)}",
        fontsize=11,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


def plot_single(
    grid: np.ndarray,
    ell_vals: np.ndarray,
    b_vals: np.ndarray,
    title: str,
    label: str,
    out_path: Path,
    vmin: float,
    vmax: float,
    cmap: str,
    contour: bool,
    eta: float,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    im = _heatmap_ax(ax, grid, ell_vals, b_vals, vmin, vmax, cmap, contour)
    plt.colorbar(im, ax=ax, label=label)
    ax.set_title(f"{title}  (η={eta:.3f} fixed)", fontsize=11)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", default="results/raw/b_ell_sweep.npz",
                   help="Path to the .npz file from b_ell_sweep.py")
    p.add_argument("--contour", action="store_true",
                   help="Overlay contour lines on heatmaps")
    p.add_argument("--no-combined", action="store_true",
                   help="Skip the side-by-side combined figure")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    data_path = Path(args.data)
    if not data_path.exists():
        sys.exit(f"Data file not found: {data_path}\nRun b_ell_sweep.py first.")

    d = np.load(data_path)
    ell_vals = d["ell_vals"]
    b_vals = d["b_vals"]
    env_grid = d["env_grid"]
    res_grid = d["res_grid"]

    # Recover eta from npz if stored, else fall back to default
    eta = float(d["eta"]) if "eta" in d else 0.03

    print(f"Loaded {data_path}")
    print(f"  ell: {ell_vals[0]:.3f} → {ell_vals[-1]:.3f} ({len(ell_vals)} points)")
    print(f"  b:   {b_vals[0]:.3f} → {b_vals[-1]:.3f} ({len(b_vals)} points)")
    print(f"  env_grid: min={env_grid.min():.3f}  max={env_grid.max():.3f}")
    print(f"  res_grid: min={res_grid.min():.3f}  max={res_grid.max():.3f}")
    print()

    plot_single(
        env_grid, ell_vals, b_vals,
        title="mean_env (final 200 gens)  —  b × ell operating window",
        label="mean_env",
        out_path=Path("results/figures/b_ell_mean_env.png"),
        vmin=-1.0, vmax=1.0, cmap="RdYlGn",
        contour=args.contour, eta=eta,
    )

    plot_single(
        res_grid, ell_vals, b_vals,
        title="resilience (frac pools ≥ T)  —  b × ell operating window",
        label="resilience",
        out_path=Path("results/figures/b_ell_resilience.png"),
        vmin=0.0, vmax=1.0, cmap="RdYlGn",
        contour=args.contour, eta=eta,
    )

    if not args.no_combined:
        plot_combined(
            env_grid, res_grid, ell_vals, b_vals, eta,
            out_path=Path("results/figures/b_ell_combined.png"),
            contour=args.contour,
        )


if __name__ == "__main__":
    main()
