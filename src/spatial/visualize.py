"""Spatial visualisation of the threshold PGG lattice.

Produces two outputs in plots/:
  spatial_snapshots.png   — 6-panel grid at key time steps
  spatial_evolution.gif   — animated lattice (requires pillow, which is bundled
                            with matplotlib on most installs)

Run with:
    uv run python src/spatial/visualize.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import numpy as np

from spatial.config import ModelConfig
from spatial.model import SpatialCollectiveRiskModel

PLOT_DIR = Path(__file__).parent.parent.parent / "plots"
PLOT_DIR.mkdir(exist_ok=True)

# -------------------------------------------------------------------
# Colour scheme: Defector=warm red, UC=steel blue
# -------------------------------------------------------------------
CMAP = mcolors.ListedColormap(["#d62728", "#1f77b4"])  # D, UC

# -------------------------------------------------------------------
# Run configuration (lighter than the default for faster rendering)
# -------------------------------------------------------------------
VIZ_CONFIG = ModelConfig(
    grid_size=40,
    initial_uc_fraction=0.5,
    n_steps=300,
    seed=42,
)
SNAPSHOT_STEPS = [0, 30, 60, 120, 200, 300]
CAPTURE_EVERY = 3  # save a frame every N steps for the animation


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _grid_array(model: SpatialCollectiveRiskModel) -> np.ndarray:
    """Return a (grid_size, grid_size) array: 1 = UC, 0 = D."""
    n = model.config.grid_size
    arr = np.zeros((n, n), dtype=np.uint8)
    for agent in model.agents:
        x, y = agent.cell.coordinate
        arr[y, x] = 1 if agent.strategy == "UC" else 0
    return arr


def _coop_rate(arr: np.ndarray) -> float:
    return arr.mean()


# -------------------------------------------------------------------
# Simulate and collect frames
# -------------------------------------------------------------------

def run_and_collect(cfg: ModelConfig) -> tuple[list[np.ndarray], list[int]]:
    """Run the model and return (frames, step_indices) for every CAPTURE_EVERY step."""
    model = SpatialCollectiveRiskModel(cfg)
    frames: list[np.ndarray] = []
    steps: list[int] = []

    # Step 0
    frames.append(_grid_array(model))
    steps.append(0)

    for t in range(1, cfg.n_steps + 1):
        model.step()
        if t % CAPTURE_EVERY == 0:
            frames.append(_grid_array(model))
            steps.append(t)

    return frames, steps


# -------------------------------------------------------------------
# Snapshot figure
# -------------------------------------------------------------------

def save_snapshots(
    frames: list[np.ndarray],
    steps: list[int],
    snapshot_steps: list[int],
) -> None:
    step_to_frame = dict(zip(steps, frames))
    # Pick the closest available step for each requested snapshot
    available = np.array(steps)
    chosen = [available[np.argmin(np.abs(available - s))] for s in snapshot_steps]

    fig, axes = plt.subplots(2, 3, figsize=(9, 6.5))
    for ax, s in zip(axes.flat, chosen):
        arr = step_to_frame[s]
        ax.imshow(arr, cmap=CMAP, vmin=0, vmax=1, origin="lower", interpolation="nearest")
        ax.set_title(f"t = {s}  (coop = {_coop_rate(arr):.2f})", fontsize=9)
        ax.axis("off")

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#1f77b4", label="UC"),
        Patch(facecolor="#d62728", label="D"),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=2, fontsize=9,
               bbox_to_anchor=(0.5, 0.01))

    fig.suptitle("Spatial threshold PGG — lattice evolution", fontsize=11)
    plt.tight_layout(rect=[0, 0.05, 1, 1])

    out = PLOT_DIR / "spatial_snapshots.png"
    plt.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved {out}")


# -------------------------------------------------------------------
# Animation
# -------------------------------------------------------------------

def save_animation(frames: list[np.ndarray], steps: list[int]) -> None:
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.axis("off")
    img = ax.imshow(
        frames[0], cmap=CMAP, vmin=0, vmax=1,
        origin="lower", interpolation="nearest",
    )
    title = ax.set_title(f"t = {steps[0]}  (coop = {_coop_rate(frames[0]):.2f})", fontsize=10)

    def update(i: int):
        img.set_data(frames[i])
        title.set_text(f"t = {steps[i]}  (coop = {_coop_rate(frames[i]):.2f})")
        return img, title

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=80, blit=True
    )

    out = PLOT_DIR / "spatial_evolution.gif"
    ani.save(out, writer="pillow", fps=12)
    plt.close(fig)
    print(f"Saved {out}")


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main() -> None:
    print(f"Running {VIZ_CONFIG.n_steps} steps on {VIZ_CONFIG.grid_size}x{VIZ_CONFIG.grid_size} grid…")
    frames, steps = run_and_collect(VIZ_CONFIG)
    print(f"  Collected {len(frames)} frames.")

    save_snapshots(frames, steps, SNAPSHOT_STEPS)
    save_animation(frames, steps)


if __name__ == "__main__":
    main()
