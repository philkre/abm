"""Oscillation-frequency analysis of order-parameter timeseries (low priority).

Works on the scalar timeseries already saved in results/raw/ — no re-run needed.
Sampling interval is one generation, so frequency is in cycles/generation and
period in generations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
from scipy import signal
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from spatcoop.params import ModelParams
from spatcoop.runner import load_result, result_path

FIGURES_DIR = Path("results/figures")


def dominant_frequencies(ts: np.ndarray, top_k: int = 3) -> list[dict]:
    """Top-k oscillation peaks of a 1-D timeseries.

    Linearly detrends and drops the DC component, then returns the `top_k`
    highest-power peaks as dicts {frequency, period, power}, strongest first.
    """
    ts = np.asarray(ts, dtype=np.float64)
    ts = ts[np.isfinite(ts)]
    if ts.size < 4 or np.allclose(ts, ts[0]):
        return []
    freqs, power = signal.periodogram(ts, fs=1.0, detrend="linear")
    freqs, power = freqs[1:], power[1:]  # drop DC (freq 0)
    order = np.argsort(power)[::-1][:top_k]
    return [
        {
            "frequency": float(freqs[i]),
            "period": float(1.0 / freqs[i]) if freqs[i] > 0 else float("inf"),
            "power": float(power[i]),
        }
        for i in order
    ]


def _mean_spectrum(results, key: str) -> tuple[np.ndarray, np.ndarray]:
    """Periodogram averaged over seeds for one order parameter."""
    spectra = []
    freqs = None
    for r in results:
        ts = np.asarray(r.timeseries[key], dtype=np.float64)
        ts = ts[np.isfinite(ts)]
        if ts.size < 4:
            continue
        freqs, p = signal.periodogram(ts, fs=1.0, detrend="linear")
        spectra.append(p)
    if not spectra:
        return np.array([]), np.array([])
    return freqs, np.mean(spectra, axis=0)


def plot_spectrum(
    p: ModelParams,
    seeds: Sequence[int],
    key: str = "n_UC",
    top_k: int = 3,
) -> Path:
    """Save the seed-averaged power spectrum of `key`, annotating top-k peaks."""
    results = [load_result(result_path(p, s)) for s in seeds]
    freqs, power = _mean_spectrum(results, key)

    fig, ax = plt.subplots(figsize=(7, 4))
    if freqs.size > 1:
        ax.plot(freqs[1:], power[1:], color="purple", lw=1.2)
        mean_ts = np.mean([r.timeseries[key] for r in results], axis=0)
        for peak in dominant_frequencies(mean_ts, top_k=top_k):
            f = peak["frequency"]
            ax.axvline(f, color="grey", ls="--", lw=0.8)
            ax.annotate(
                f"T≈{peak['period']:.0f}",
                xy=(f, peak["power"]),
                fontsize=8,
                ha="left",
                va="bottom",
            )
    ax.set_xlabel("Frequency (cycles / generation)")
    ax.set_ylabel("Power")
    ax.set_title(f"Power spectrum — {key}")
    fig.tight_layout()

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"spectrum_{key}.pdf"
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  saved → {path}")
    return path
