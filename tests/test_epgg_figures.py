"""Smoke tests for the Fig 2 reproduction wiring (no heavy compute)."""

from __future__ import annotations

import numpy as np

from epgg.figures import plot_delta_sweep, run_fig2


def test_plot_delta_sweep_writes_file(tmp_path):
    deltas = np.array([0.0, 0.05, 0.1])
    fracs = np.array([0.0, 0.8, 0.5])
    out = tmp_path / "fig2.png"
    plot_delta_sweep(deltas, fracs, out, gamma=0.04)
    assert out.exists() and out.stat().st_size > 0


def test_run_fig2_returns_aligned_arrays(tmp_path):
    # Tiny scale: only checks wiring/shape, not the phase diagram.
    deltas = [0.0, 0.05]
    out = tmp_path / "fig2.png"
    d, fracs = run_fig2(
        L=30,
        gamma=0.04,
        deltas=deltas,
        n_repeats=1,
        output=out,
        min_gen=100,
        window=50,
        max_gen=300,
    )
    assert np.allclose(d, deltas)
    assert fracs.shape == (2,)
    assert np.all((fracs >= 0.0) & (fracs <= 1.0))
    assert out.exists()
