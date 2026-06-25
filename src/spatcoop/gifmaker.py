"""Generate animated GIFs from visualization sweep frame files.

Two modes:
- Per-run GIFs: animate one (params, seed) file across snap_gens, showing
  strategy + env + wealth side by side.
- Grid GIF: for each snap_gen, show the full (beta, p_max) grid of spatial
  patterns for a single field, animated across time.
"""

from __future__ import annotations

import io
import json
from pathlib import Path

import matplotlib
from matplotlib.figure import Figure

matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from tqdm import tqdm

# ── Colour maps ───────────────────────────────────────────────────────────────

STRAT_CMAP = mcolors.ListedColormap(["#e74c3c", "#2ecc71", "#3498db"])
STRAT_NORM = mcolors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5], STRAT_CMAP.N)
_STRAT_PATCHES = [
    mpatches.Patch(color="#e74c3c", label="D"),
    mpatches.Patch(color="#2ecc71", label="UC"),
    mpatches.Patch(color="#3498db", label="CC"),
]
ENV_CMAP = "RdYlGn"
WEALTH_CMAP = "plasma"


# ── Internal helpers ──────────────────────────────────────────────────────────


def _fig_to_pil(fig: Figure) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=90, bbox_inches="tight")
    buf.seek(0)
    img = Image.open(buf).convert("RGB")
    img.load()
    buf.close()
    plt.close(fig)
    return img


def _save_gif(imgs: list[Image.Image], path: Path, ms_per_frame: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    imgs[0].save(
        path,
        save_all=True,
        append_images=imgs[1:],
        duration=ms_per_frame,
        loop=0,
    )


def _snap_gens_in(d) -> list[int]:
    """Sorted list of generation indices present in an npz data object."""
    return sorted(set(int(k.split("_")[1]) for k in d.files if k.startswith("frame_")))


def _majority_vote(stack: np.ndarray) -> np.ndarray:
    """Pixel-wise mode of an int8 (N, H, W) stack along axis 0."""
    from scipy import stats

    return stats.mode(stack, axis=0, keepdims=False).mode.astype(np.int8)


# ── Per-run temporal GIFs ─────────────────────────────────────────────────────


def make_run_gifs(
    in_dir: Path,
    out_dir: Path,
    ms_per_frame: int = 800,
) -> None:
    """One animated GIF per *_frames.npz in in_dir.

    Each GIF animates across snap_gens, showing a 3-panel figure
    (strategy | environment | wealth).
    """
    files = sorted(in_dir.glob("*_frames.npz"))
    out_dir.mkdir(parents=True, exist_ok=True)

    n_new = 0
    for npz_path in tqdm(files, desc="run GIFs", unit="file"):
        gif_path = out_dir / (npz_path.stem.replace("_frames", "") + ".gif")
        if gif_path.exists():
            continue

        d = np.load(npz_path, allow_pickle=True)
        params = json.loads(str(d["params_json"]))
        seed = int(d["seed"])
        gens = _snap_gens_in(d)

        # Global wealth max for consistent colour scale across frames
        w_max = max(float(d[f"frame_{g:04d}_wealth"].max()) for g in gens) or 1.0

        imgs: list[Image.Image] = []
        for gen in gens:
            strat = d[f"frame_{gen:04d}_strategy"]
            env = d[f"frame_{gen:04d}_env"]
            wealth = d[f"frame_{gen:04d}_wealth"]

            fig, axes = plt.subplots(1, 3, figsize=(9, 3.4))

            axes[0].imshow(strat, cmap=STRAT_CMAP, norm=STRAT_NORM, interpolation="nearest")
            axes[0].set_title("Strategy", fontsize=9)
            axes[0].axis("off")

            im1 = axes[1].imshow(env, cmap=ENV_CMAP, vmin=-1, vmax=1, interpolation="nearest")
            plt.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)
            axes[1].set_title("Environment", fontsize=9)
            axes[1].axis("off")

            im2 = axes[2].imshow(wealth, cmap=WEALTH_CMAP, vmin=0, vmax=w_max, interpolation="nearest")
            plt.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04)
            axes[2].set_title("Wealth", fontsize=9)
            axes[2].axis("off")

            fig.suptitle(
                f"β={params['beta']:.3g}  p_max={params['p_max']:.2f}  " f"seed={seed}  gen={gen}",
                fontsize=9,
            )
            fig.legend(
                handles=_STRAT_PATCHES,
                loc="lower left",
                fontsize=7,
                bbox_to_anchor=(0.01, 0.0),
                ncol=3,
                framealpha=0.7,
            )
            fig.tight_layout(rect=(0, 0.05, 1, 1))
            imgs.append(_fig_to_pil(fig))

        if imgs:
            _save_gif(imgs, gif_path, ms_per_frame)
            n_new += 1

    print(f"  {n_new} new per-run GIFs → {out_dir}/")


# ── Grid GIF (phase portrait across parameter space) ─────────────────────────


def make_grid_gif(
    in_dir: Path,
    out_dir: Path,
    field: str = "strategy",
    ms_per_frame: int = 900,
) -> None:
    """Animated GIF of the (beta, p_max) grid for a single field.

    Each animation frame is one snap_gen; each subplot is one parameter
    combination aggregated across seeds (majority vote for strategy; mean for
    continuous fields).  Rows = p_max (high at top), columns = β (log-spaced).
    """
    files = sorted(in_dir.glob("*_frames.npz"))
    if not files:
        print(f"  No *_frames.npz files found in {in_dir}")
        return

    # ── Load all arrays ───────────────────────────────────────────────────────
    # data[(beta, pmax)][seed][gen] = ndarray
    data: dict[tuple[float, float], dict[int, dict[int, np.ndarray]]] = {}
    all_gens: set[int] = set()

    for npz_path in files:
        d = np.load(npz_path, allow_pickle=True)
        params = json.loads(str(d["params_json"]))
        seed = int(d["seed"])
        beta = float(params["beta"])
        pmax = float(params["p_max"])
        gens = _snap_gens_in(d)
        all_gens.update(gens)
        key = (beta, pmax)
        if key not in data:
            data[key] = {}
        data[key][seed] = {g: d[f"frame_{g:04d}_{field}"] for g in gens}

    betas = sorted(set(b for b, _ in data))
    pmaxes = sorted(set(p for _, p in data))
    snap_gens = sorted(all_gens)
    nrow, ncol = len(pmaxes), len(betas)

    # ── Colour scale ──────────────────────────────────────────────────────────
    if field == "env":
        vmin, vmax, cmap = -1.0, 1.0, ENV_CMAP
    elif field == "wealth":
        all_arrs = [arr for cell in data.values() for seed_d in cell.values() for arr in seed_d.values()]
        vmin, vmax, cmap = 0.0, float(max(a.max() for a in all_arrs)), WEALTH_CMAP
    else:
        vmin, vmax, cmap = None, None, None  # strategy: per-pixel colourmap

    # ── Render one image per snap_gen ─────────────────────────────────────────
    imgs: list[Image.Image] = []
    for gen in tqdm(snap_gens, desc=f"grid/{field}"):
        fig, axes = plt.subplots(
            nrow,
            ncol,
            figsize=(ncol * 1.5 + 0.6, nrow * 1.5 + 1.0),
            squeeze=False,
            gridspec_kw={"hspace": 0.05, "wspace": 0.05},
        )

        for r, pmax in enumerate(reversed(pmaxes)):  # high p_max at top
            for c, beta in enumerate(betas):
                ax = axes[r][c]
                ax.set_xticks([])
                ax.set_yticks([])

                # Collect seed arrays for this cell and generation
                seed_arrs: list[np.ndarray] = []
                cell = data.get((beta, pmax), {})
                for seed_d in cell.values():
                    if gen in seed_d:
                        seed_arrs.append(seed_d[gen])

                if not seed_arrs:
                    ax.set_facecolor("#cccccc")
                    continue

                # Aggregate across seeds
                if field == "strategy":
                    if len(seed_arrs) == 1:
                        agg = seed_arrs[0]
                    else:
                        agg = _majority_vote(np.stack(seed_arrs, axis=0))
                    ax.imshow(agg, cmap=STRAT_CMAP, norm=STRAT_NORM, interpolation="nearest")
                else:
                    agg = np.mean(seed_arrs, axis=0)
                    ax.imshow(agg, cmap=cmap, vmin=vmin, vmax=vmax, interpolation="nearest")

                # Edge labels
                if r == nrow - 1:
                    ax.set_xlabel(f"β={beta:.2g}", fontsize=6, labelpad=1)
                    ax.xaxis.set_label_position("bottom")
                if c == 0:
                    ax.set_ylabel(f"p={pmax:.2f}", fontsize=6, labelpad=1)

        fig.suptitle(f"Spatial {field} — gen {gen}", fontsize=11)

        if field == "strategy":
            fig.legend(
                handles=_STRAT_PATCHES,
                loc="lower center",
                ncol=3,
                fontsize=8,
                bbox_to_anchor=(0.5, -0.01),
                framealpha=0.8,
            )
        else:
            norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            fig.colorbar(
                sm,
                ax=axes.ravel().tolist(),
                shrink=0.6,
                pad=0.02,
                aspect=25,
                label=field,
            )

        fig.tight_layout()
        imgs.append(_fig_to_pil(fig))

    if imgs:
        out_path = out_dir / f"grid_{field}.gif"
        _save_gif(imgs, out_path, ms_per_frame)
        print(f"  saved → {out_path}")
