"""plot_ell_eta.py — Re-plot the ell × eta sweep from saved .npz.

Reads results/raw/ell_eta_sweep.npz and produces:
  results/figures/ell_eta_mean_env.png
  results/figures/ell_eta_resilience.png
  results/figures/ell_eta_combined.png  (side-by-side)

All plot settings live here — re-run this freely without touching the sweep.

Usage:
    uv run python scripts/plot_ell_eta.py
    uv run python scripts/plot_ell_eta.py --data results/raw/ell_eta_sweep.npz
    uv run python scripts/plot_ell_eta.py --contour --no-combined
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Fixed-parameter marker (the calibrated point) ────────────────────────────
FIXED_ELL = 0.64
FIXED_ETA = 0.005


def _heatmap_ax(
    ax: plt.Axes,
    grid: np.ndarray,
    ell_vals: np.ndarray,
    eta_vals: np.ndarray,
    label: str,
    vmin: float,
    vmax: float,
    cmap: str,
    contour: bool,
) -> plt.cm.ScalarMappable:
    im = ax.imshow(
        grid,
        origin="lower",
        aspect="auto",
        extent=[ell_vals[0], ell_vals[-1], eta_vals[0], eta_vals[-1]],
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        interpolation="nearest",
    )

    if contour:
        levels = np.linspace(vmin, vmax, 9)
        cs = ax.contour(
            np.linspace(ell_vals[0], ell_vals[-1], grid.shape[1]),
            np.linspace(eta_vals[0], eta_vals[-1], grid.shape[0]),
            grid,
            levels=levels,
            colors="black",
            linewidths=0.5,
            alpha=0.4,
        )
        ax.clabel(cs, fmt="%.2f", fontsize=7)

    ax.scatter(
        [FIXED_ELL], [FIXED_ETA],
        color="blue", marker="x", s=100, linewidths=2.5, zorder=5,
        label=f"calibrated (ell={FIXED_ELL}, η={FIXED_ETA})",
    )
    ax.legend(fontsize=8, loc="upper left")
    ax.set_xlabel("ell  (flood-loss fraction)", fontsize=11)
    ax.set_ylabel("η  (flood-damage rate)", fontsize=11)
    return im


def plot_single(
    grid: np.ndarray,
    ell_vals: np.ndarray,
    eta_vals: np.ndarray,
    title: str,
    label: str,
    out_path: Path,
    vmin: float,
    vmax: float,
    cmap: str,
    contour: bool,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    im = _heatmap_ax(ax, grid, ell_vals, eta_vals, label, vmin, vmax, cmap, contour)
    plt.colorbar(im, ax=ax, label=label)
    ax.set_title(title, fontsize=11)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


def plot_combined(
    env_grid: np.ndarray,
    res_grid: np.ndarray,
    ell_vals: np.ndarray,
    eta_vals: np.ndarray,
    out_path: Path,
    contour: bool,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    im0 = _heatmap_ax(axes[0], env_grid, ell_vals, eta_vals,
                      "mean_env", -1.0, 1.0, "RdYlGn", contour)
    plt.colorbar(im0, ax=axes[0], label="mean_env (final 200 gens)")
    axes[0].set_title("Environment recovery", fontsize=12)

    im1 = _heatmap_ax(axes[1], res_grid, ell_vals, eta_vals,
                      "resilience", 0.0, 1.0, "RdYlGn", contour)
    plt.colorbar(im1, ax=axes[1], label="resilience (frac pools ≥ T)")
    axes[1].set_title("Group resilience", fontsize=12)

    fig.suptitle(
        f"ell × η operating window  (initial_e=−1, calibrated params)\n"
        f"ell ∈ [{ell_vals[0]:.2f}, {ell_vals[-1]:.2f}]  "
        f"η ∈ [{eta_vals[0]:.3f}, {eta_vals[-1]:.3f}]  "
        f"grid {len(ell_vals)}×{len(eta_vals)}",
        fontsize=11,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", default="results/raw/ell_eta_sweep.npz",
                   help="Path to the .npz file from ell_eta_sweep.py")
    p.add_argument("--contour", action="store_true",
                   help="Overlay contour lines on heatmaps")
    p.add_argument("--no-combined", action="store_true",
                   help="Skip the side-by-side combined figure")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    data_path = Path(args.data)
    if not data_path.exists():
        sys.exit(f"Data file not found: {data_path}\nRun ell_eta_sweep.py first.")

    d = np.load(data_path)
    ell_vals = d["ell_vals"]
    eta_vals = d["eta_vals"]
    env_grid = d["env_grid"]
    res_grid = d["res_grid"]

    print(f"Loaded {data_path}")
    print(f"  ell: {ell_vals[0]:.3f} → {ell_vals[-1]:.3f} ({len(ell_vals)} points)")
    print(f"  eta: {eta_vals[0]:.4f} → {eta_vals[-1]:.4f} ({len(eta_vals)} points)")
    print(f"  env_grid: min={env_grid.min():.3f}  max={env_grid.max():.3f}")
    print(f"  res_grid: min={res_grid.min():.3f}  max={res_grid.max():.3f}")
    print()

    plot_single(
        env_grid, ell_vals, eta_vals,
        title="mean_env (final 200 gens)  —  ell × η operating window",
        label="mean_env",
        out_path=Path("results/figures/ell_eta_mean_env.png"),
        vmin=-1.0, vmax=1.0, cmap="RdYlGn",
        contour=args.contour,
    )

    plot_single(
        res_grid, ell_vals, eta_vals,
        title="resilience (frac pools ≥ T)  —  ell × η operating window",
        label="resilience",
        out_path=Path("results/figures/ell_eta_resilience.png"),
        vmin=0.0, vmax=1.0, cmap="RdYlGn",
        contour=args.contour,
    )

    if not args.no_combined:
        plot_combined(
            env_grid, res_grid, ell_vals, eta_vals,
            out_path=Path("results/figures/ell_eta_combined.png"),
            contour=args.contour,
        )


if __name__ == "__main__":
    main()
