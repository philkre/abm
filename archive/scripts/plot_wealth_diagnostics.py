"""plot_wealth_diagnostics.py — Wealth and strategy diagnostics from the ell×b Snellius SA.

Data source: snellius_ell_b_sa.sh (2-parameter Sobol SA over ell×b at L=200, 1500 gens,
20 seeds).  NOT the local_money_sa data (too small / wrong L).

Three PDF pages saved to results/figures/wealth_diagnostics.pdf:

  Page 1 — Effect of ℓ on wealth inequality, stratified by b-regime
    Scatter of ell vs Gini wealth (seed-averaged).  Background points coloured by b.
    Three overlaid bin-mean lines for the collapse (b<4), transition (4≤b<10), and
    cooperative (b≥10) regimes, so the effect of ℓ on inequality can be compared
    within each phase rather than averaged across them.

  Page 2 — Income drift b vs dominant wealth-oscillation period (FFT)
    For each sample, the mean_wealth timeseries is FFT-ed after discarding the first
    WARMUP_FRAC of generations.  Dominant non-DC frequency → period (gens), log y-axis.
    Scatter coloured by equilibrium cooperation fraction.

  Page 3 — Strategy shares in (b, ell) space
    Three scatter panels (D, CC, UC) in (b, ell) space, coloured by window-mean
    equilibrium fraction.  Colour maps: Reds / Oranges / Greens — same as the
    local_money_sa timeseries plots (D=red, CC=orange, UC=green).

Usage:
    # On Snellius login node (defaults point to scratch)
    uv run python scripts/plot_wealth_diagnostics.py

    # Locally after syncing results from Snellius
    .venv/Scripts/python.exe scripts/plot_wealth_diagnostics.py \\
        --data-dir /path/to/ell_b_sa \\
        --raw-dir  /path/to/ell_b_sa/raw

Reads:  {data_dir}/run_config.json, {data_dir}/sample_X.npy, {raw_dir}/*.npz
Writes: results/figures/wealth_diagnostics.pdf
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spatcoop.params import ModelParams
from spatcoop.sa import _apply_row
from spatcoop.runner import result_path

WARMUP_FRAC = 0.25  # discard first 25 % of generations before FFT

# Colour scheme matching local_money_sa timeseries panels
STRAT_COLORS = {"D": "#e74c3c", "CC": "#e67e22", "UC": "#27ae60"}
STRAT_CMAPS  = {"D": "Reds",    "CC": "Oranges", "UC": "Greens"}

# b-range strata for Page 1 stratified lines
B_STRATA = [
    (1.0,  4.0,  "collapse  (b < 4)",       "#d62728"),
    (4.0,  10.0, "transition  (4 ≤ b < 10)", "#ff7f0e"),
    (10.0, 25.0, "cooperative  (b ≥ 10)",   "#2ca02c"),
]


# ── data helpers ──────────────────────────────────────────────────────────────

def _load_npz_key(path: Path, key: str):
    """Load a single array from an npz without reading the whole file."""
    try:
        with np.load(path, allow_pickle=True) as d:
            return d[key].copy() if key in d.files else None
    except Exception:
        return None


def _scalar(params_list: list, seeds: list[int], key: str, raw_dir: Path) -> np.ndarray:
    """Seed-averaged summary scalar (sum_{key}) for each sample. Missing → nan."""
    out = []
    for p in params_list:
        vals = []
        for s in seeds:
            path = result_path(p, s, raw_dir)
            if path.exists():
                raw = _load_npz_key(path, f"sum_{key}")
                if raw is not None:
                    v = float(raw)
                    if not np.isnan(v):
                        vals.append(v)
        out.append(float(np.nanmean(vals)) if vals else np.nan)
    return np.array(out, dtype=float)


def _mean_wealth_ts(params_list: list, seeds: list[int], raw_dir: Path) -> list:
    """Seed-averaged mean_wealth timeseries for each sample. Missing → None."""
    result = []
    for p in params_list:
        arrays = [
            arr for s in seeds
            if (path := result_path(p, s, raw_dir)).exists()
            and (arr := _load_npz_key(path, "ts_mean_wealth")) is not None
        ]
        if arrays:
            L = min(a.shape[0] for a in arrays)
            result.append(np.stack([a[:L] for a in arrays]).mean(axis=0))
        else:
            result.append(None)
    return result


def _dominant_period(ts: np.ndarray) -> float:
    """Dominant oscillation period (gens) from FFT after warm-up discard."""
    warmup = max(10, int(len(ts) * WARMUP_FRAC))
    sig = ts[warmup:].astype(float)
    if len(sig) < 8 or sig.std() < 1e-10:
        return np.nan
    sig -= sig.mean()
    freq  = np.fft.rfftfreq(len(sig))
    power = np.abs(np.fft.rfft(sig)) ** 2
    peak  = 1 + int(np.argmax(power[1:]))   # skip DC
    f = float(freq[peak])
    return 1.0 / f if f > 1e-12 else np.nan


# ── Page 1: ell vs gini_wealth stratified by b ────────────────────────────────

def page_ell_gini(
    pdf: PdfPages,
    X: np.ndarray, names: list[str],
    params_list: list, seeds: list[int], raw_dir: Path,
    cfg: dict,
) -> None:
    ell_vals = X[:, names.index("ell")]
    b_vals   = X[:, names.index("b")]
    gini     = _scalar(params_list, seeds, "gini_wealth", raw_dir)

    mask_all = ~np.isnan(gini)
    fig, ax = plt.subplots(figsize=(8, 5))

    # Background scatter coloured by b
    sc = ax.scatter(
        ell_vals[mask_all], gini[mask_all],
        c=b_vals[mask_all], cmap="viridis",
        s=16, alpha=0.35, edgecolors="none", zorder=2,
    )
    plt.colorbar(sc, ax=ax, label="b  (income drift)")

    # Per-stratum bin-mean lines (collapse / transition / cooperative)
    bins = np.linspace(ell_vals.min(), ell_vals.max(), 9)
    bx   = 0.5 * (bins[:-1] + bins[1:])
    for lo_b, hi_b, label, color in B_STRATA:
        in_stratum = mask_all & (b_vals >= lo_b) & (b_vals < hi_b)
        by = np.array([
            np.nanmean(gini[sel]) if (sel := in_stratum & (ell_vals >= lo) & (ell_vals < hi)).any()
            else np.nan
            for lo, hi in zip(bins[:-1], bins[1:])
        ])
        valid = ~np.isnan(by)
        if valid.sum() >= 2:
            ax.plot(bx[valid], by[valid], "-o", ms=5, lw=2.2,
                    color=color, label=label, zorder=5)

    ax.set_xlabel("ℓ  (flood loss fraction)", fontsize=10)
    ax.set_ylabel("Gini wealth  (window mean, avg over seeds)", fontsize=10)
    ax.set_title(
        "Effect of loss fraction ℓ on wealth inequality — stratified by income-drift regime\n"
        f"L=200  n_gens=1500  N={cfg['N']} Saltelli samples × {len(seeds)} seeds",
        fontsize=9,
    )
    ax.legend(title="b regime", fontsize=8, title_fontsize=8)
    fig.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ── Page 2: b vs dominant wealth-oscillation period (FFT) ────────────────────

def page_b_freq(
    pdf: PdfPages,
    X: np.ndarray, names: list[str],
    params_list: list, seeds: list[int], raw_dir: Path,
    cfg: dict,
) -> None:
    b_vals   = X[:, names.index("b")]
    coop     = _scalar(params_list, seeds, "coop_frac", raw_dir)
    ts_lists = _mean_wealth_ts(params_list, seeds, raw_dir)

    periods = np.array([
        _dominant_period(ts) if ts is not None else np.nan
        for ts in ts_lists
    ])

    mask = ~(np.isnan(periods) | np.isnan(coop))
    fig, ax = plt.subplots(figsize=(8, 5))

    sc = ax.scatter(
        b_vals[mask], periods[mask],
        c=coop[mask], cmap="RdYlGn", vmin=0, vmax=1,
        s=22, alpha=0.82, edgecolors="none", zorder=3,
    )
    plt.colorbar(sc, ax=ax, label="Cooperation fraction")

    ax.set_xlabel("b  (income drift)", fontsize=10)
    ax.set_ylabel("Dominant wealth-oscillation period  (generations)", fontsize=10)
    ax.set_yscale("log")
    ax.set_title(
        "Income drift b vs dominant wealth-oscillation period (FFT of mean_wealth)\n"
        f"Warm-up discarded (first {int(WARMUP_FRAC * 100)} %)  |  coloured by cooperation fraction",
        fontsize=9,
    )
    fig.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ── Page 3: strategy shares in (b, ell) space ────────────────────────────────

def page_strategy_phase(
    pdf: PdfPages,
    X: np.ndarray, names: list[str],
    params_list: list, seeds: list[int], raw_dir: Path,
    cfg: dict,
) -> None:
    b_vals   = X[:, names.index("b")]
    ell_vals = X[:, names.index("ell")]

    n_D  = _scalar(params_list, seeds, "n_D",  raw_dir)
    n_UC = _scalar(params_list, seeds, "n_UC", raw_dir)
    n_CC = _scalar(params_list, seeds, "n_CC", raw_dir)
    total = n_D + n_UC + n_CC      # always == L^2

    with np.errstate(invalid="ignore"):
        fracs = {
            "D":  n_D  / total,
            "CC": n_CC / total,
            "UC": n_UC / total,
        }

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)
    fig.suptitle(
        "Strategy shares in (b, ℓ) space — window-mean equilibrium fractions, avg over seeds\n"
        f"L=200  n_gens=1500  N={cfg['N']} Saltelli samples × {len(seeds)} seeds",
        fontsize=9,
    )

    for ax, (strat, frac) in zip(axes, fracs.items()):
        mask = ~np.isnan(frac)
        sc = ax.scatter(
            b_vals[mask], ell_vals[mask],
            c=frac[mask],
            cmap=STRAT_CMAPS[strat],
            vmin=0, vmax=1,
            s=40, alpha=0.88,
            edgecolors="0.35", linewidths=0.4,
            zorder=3,
        )
        plt.colorbar(sc, ax=ax, label=f"{strat} fraction")
        ax.set_xlabel("b  (income drift)", fontsize=9)
        if ax is axes[0]:
            ax.set_ylabel("ℓ  (flood loss fraction)", fontsize=9)
        ax.set_title(
            f"Strategy {strat}",
            color=STRAT_COLORS[strat],
            fontsize=11, fontweight="bold",
        )
        ax.tick_params(labelsize=8)

    fig.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Wealth and strategy diagnostic plots (ell×b SA).")
    parser.add_argument(
        "--data-dir",
        default="/scratch-shared/lschoonheid/results/ell_b_sa",
        help="Directory containing run_config.json and sample_X.npy.",
    )
    parser.add_argument(
        "--raw-dir",
        default=None,
        help="Raw .npz checkpoint directory. Defaults to {data_dir}/raw.",
    )
    parser.add_argument(
        "--out",
        default="results/figures/wealth_diagnostics.pdf",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    raw_dir  = Path(args.raw_dir) if args.raw_dir else data_dir / "raw"
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cfg     = json.loads((data_dir / "run_config.json").read_text())
    base    = ModelParams(**cfg["base_params"])
    problem = cfg["problem"]
    names   = problem["names"]
    X       = np.load(data_dir / "sample_X.npy")
    seeds   = cfg["seeds"]

    params_list = [_apply_row(names, row, base) for row in X]
    print(f"Loaded {len(params_list)} samples × {len(seeds)} seeds")
    print(f"  data_dir : {data_dir}")
    print(f"  raw_dir  : {raw_dir}")

    with PdfPages(out_path) as pdf:
        print("Page 1: ell vs gini_wealth (stratified by b-regime) ...")
        page_ell_gini(pdf, X, names, params_list, seeds, raw_dir, cfg)

        print("Page 2: b vs dominant wealth-oscillation period (FFT) ...")
        page_b_freq(pdf, X, names, params_list, seeds, raw_dir, cfg)

        print("Page 3: strategy shares in (b, ell) space ...")
        page_strategy_phase(pdf, X, names, params_list, seeds, raw_dir, cfg)

    print(f"Saved → {out_path}")


if __name__ == "__main__":
    main()
