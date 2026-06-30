"""local_money_sa_plot.py — Plots from the money-parameter exploratory SA.

Reads:  results/local_money_sa/  (produced by local_money_sa_run.py)
Writes: results/local_money_sa/sobol_heatmap.pdf
          — Three panels:
            1. S1 (first-order Sobol) for the 5 direct parameters
            2. ST (total-order Sobol) for the 5 direct parameters
            3. Spearman r² for derived ratios c̄/T, c̄/b, T/b
               (proxy for first-order sensitivity of dimensionless groups)
        results/local_money_sa/timeseries.pdf
          — Timeseries per base sample point

Derived-ratio sensitivity note:
  Sobol S1/ST for derived quantities (c̄/T, c̄/b, T/b) cannot be read off
  directly from a Saltelli design built for the primary parameters, because
  neither A_B^i matrix isolates a ratio.  We instead report Spearman rank
  correlation squared ρ_s² as an approximation to S1 — it captures monotonic
  relationships correctly and does not assume linearity.

Usage (run from philkre-abm root):
    uv run python scripts/local_money_sa_plot.py

Note: with the default N=16 all indices have wide CIs; treat rankings as ordinal.
"""

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spatcoop.params import ModelParams
from spatcoop.sa import build_problem, _apply_row
from spatcoop.runner import load_result, result_path

OUT_DIR = Path("results/local_money_sa")
RAW_DIR = OUT_DIR / "raw"

# Must match VARY_SPECS in local_money_sa_run.py
VARY_SPECS = [
    ("T_over_E", 0.2,  0.9),
    ("b",        1.0,  21.0),
    ("c_bar",    0.1,  1.5),
    ("ell",      0.05, 1.0),
    ("sigma",    0.0,  0.5),
]

PARAM_LABELS = {
    "T_over_E": "T/E (threshold)",
    "b":        "b (drift/income)",
    "c_bar":    "c̄ (cooperation)",
    "ell":      "ℓ (loss frac)",
    "sigma":    "σ (diffusion)",
}

DERIVED_LABELS = {
    "c̄/T":  "c̄/T",
    "c̄/b":  "c̄/b",
    "T/b":   "T/b",
}

# Output metrics for Sobol heatmap
SA_OUTPUTS = {
    "mean_env":        "Env (mean)",
    "mean_env_std":    "Env variance (time)",
    "flood_rate":      "Flood rate",
    "coop_frac":       "Coop fraction",
    "coop_frac_std":   "Strategy ratio variance",
    "mean_wealth":     "Avg wealth",
    "mean_wealth_std": "Wealth variance (time)",
    "gini_wealth":     "Wealth inequality",
    "resilience":      "Resilience",
}


# ── helpers ───────────────────────────────────────────────────────────────────


def _load_config():
    return json.loads((OUT_DIR / "config.json").read_text())


def _make_base(cfg) -> ModelParams:
    return ModelParams(**cfg["base_params"])


def _rebuild_params(cfg):
    """Load saved sample_X.npy and reconstruct params_list from it."""
    base = _make_base(cfg)
    problem = build_problem(VARY_SPECS)
    X = np.load(OUT_DIR / "sample_X.npy")
    if X.shape[1] != len(VARY_SPECS):
        raise RuntimeError(
            f"sample_X.npy has {X.shape[1]} columns but VARY_SPECS has {len(VARY_SPECS)} "
            "parameters. Run local_money_sa_run.py first to regenerate the sample."
        )
    params_list = [_apply_row(problem["names"], row, base) for row in X]
    return params_list, X, problem


def _load_Y(params_list, seeds, key):
    Y = []
    for p in params_list:
        vals = []
        for s in seeds:
            path = result_path(p, s, RAW_DIR)
            if path.exists():
                r = load_result(path)
                v = r.summary.get(key, float("nan"))
                if not np.isnan(v):
                    vals.append(v)
        Y.append(float(np.nanmean(vals)) if vals else float("nan"))
    return np.array(Y, dtype=np.float64)


# ── Derived ratio sensitivity (Spearman r²) ───────────────────────────────────


def _spearman_r2(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation squared as proxy for first-order sensitivity."""
    mask = ~(np.isnan(x) | np.isnan(y))
    if mask.sum() < 6 or np.nanstd(y[mask]) < 1e-10 or np.nanstd(x[mask]) < 1e-10:
        return float("nan")
    r, _ = spearmanr(x[mask], y[mask])
    return float(r ** 2)


def _compute_derived_sensitivity(X: np.ndarray, names: list, params_list, seeds):
    """Compute Spearman r² for derived ratios c̄/T, c̄/b, T/b over the full sample."""
    col = {n: X[:, i] for i, n in enumerate(names)}
    T_abs = col["T_over_E"] * 5.0
    b_vals = col["b"]
    cbar   = col["c_bar"]

    derived = {
        "c̄/T": cbar / T_abs,
        "c̄/b": cbar / b_vals,
        "T/b":  T_abs / b_vals,
    }

    ratio_mat = np.full((len(SA_OUTPUTS), len(derived)), np.nan)
    for i, key in enumerate(SA_OUTPUTS):
        Y = _load_Y(params_list, seeds, key)
        for j, ratio_vals in enumerate(derived.values()):
            ratio_mat[i, j] = _spearman_r2(ratio_vals, Y)

    return list(derived.keys()), ratio_mat


# ── Sobol heatmap ─────────────────────────────────────────────────────────────


def plot_sobol_heatmap(params_list, X, problem, seeds):
    from SALib.analyze import sobol as sobol_analyze

    names = problem["names"]
    n_out = len(SA_OUTPUTS)
    n_par = len(names)

    S1_mat = np.full((n_out, n_par), np.nan)
    ST_mat = np.full((n_out, n_par), np.nan)

    for i, key in enumerate(SA_OUTPUTS):
        Y = _load_Y(params_list, seeds, key)
        if np.all(np.isnan(Y)):
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                Si = sobol_analyze.analyze(problem, Y, calc_second_order=False,
                                           print_to_console=False)
                S1_mat[i] = np.clip(Si["S1"], 0, 1)
                ST_mat[i] = np.clip(Si["ST"], 0, 1)
            except Exception:
                pass

    # Derived-ratio sensitivity
    ratio_names, ratio_mat = _compute_derived_sensitivity(X, names, params_list, seeds)

    row_labels = list(SA_OUTPUTS.values())
    col_labels  = [PARAM_LABELS.get(n, n) for n in names]

    fig, axes = plt.subplots(1, 3, figsize=(max(14, n_par * 1.8 + 6), max(5, n_out * 0.75 + 1.5)))

    # Panels 1 & 2 — S1 and ST for the 5 primary parameters
    for ax, mat, title in zip(axes[:2], [S1_mat, ST_mat],
                               ["S1 (first-order)", "ST (total-order)"]):
        im = ax.imshow(mat, vmin=0, vmax=1, cmap="YlOrRd", aspect="auto")
        ax.set_xticks(range(n_par))
        ax.set_xticklabels(col_labels, rotation=30, ha="right", fontsize=8.5)
        ax.set_yticks(range(n_out))
        ax.set_yticklabels(row_labels, fontsize=8.5)
        ax.set_title(title, fontsize=10)
        for r in range(n_out):
            for c in range(n_par):
                v = mat[r, c]
                if not np.isnan(v):
                    ax.text(c, r, f"{v:.2f}", ha="center", va="center", fontsize=7,
                            color="white" if v > 0.55 else "black")
        plt.colorbar(im, ax=ax, shrink=0.8)

    # Panel 3 — Spearman r² for derived ratios
    ax3 = axes[2]
    im3 = ax3.imshow(ratio_mat, vmin=0, vmax=1, cmap="Blues", aspect="auto")
    ax3.set_xticks(range(len(ratio_names)))
    ax3.set_xticklabels(ratio_names, rotation=30, ha="right", fontsize=8.5)
    ax3.set_yticks(range(n_out))
    ax3.set_yticklabels(row_labels, fontsize=8.5)
    ax3.set_title("Spearman r²\n(derived ratios, approx. S1)", fontsize=10)
    for r in range(n_out):
        for c in range(len(ratio_names)):
            v = ratio_mat[r, c]
            if not np.isnan(v):
                ax3.text(c, r, f"{v:.2f}", ha="center", va="center", fontsize=7,
                         color="white" if v > 0.55 else "black")
    plt.colorbar(im3, ax=ax3, shrink=0.8)

    fig.suptitle(
        "Sobol sensitivity — money + diffusion params  (exploratory, small N)\n"
        "Fixed: delta=0.042, gamma=0.018, eta=0.005, kappa=0.1, beta=1.8, p_max=1.0  "
        "| wealth_mode=ou (Wiener-with-drift: b=drift, σ=diffusion)",
        fontsize=8.5,
    )
    fig.tight_layout()
    out = OUT_DIR / "sobol_heatmap.pdf"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved → {out}")


# ── Timeseries PDF ────────────────────────────────────────────────────────────


def plot_timeseries_pdf(params_list, X, names, seeds, N_base):
    SEED = seeds[0]
    base_params = params_list[:N_base]
    base_X = X[:N_base]

    with PdfPages(OUT_DIR / "timeseries.pdf") as pdf:
        combos_per_page = 2
        for page_start in range(0, N_base, combos_per_page):
            chunk_p = base_params[page_start: page_start + combos_per_page]
            chunk_X = base_X[page_start: page_start + combos_per_page]
            n_c = len(chunk_p)

            fig, axes = plt.subplots(n_c, 2, figsize=(13, 4 * n_c), squeeze=False)

            for row_i, (p, x_row) in enumerate(zip(chunk_p, chunk_X)):
                path = result_path(p, SEED, RAW_DIR)
                if not path.exists():
                    for ax in axes[row_i]:
                        ax.text(0.5, 0.5, "missing", transform=ax.transAxes,
                                ha="center", va="center", color="gray")
                    continue

                r = load_result(path)
                ts = r.timeseries
                N_cells = p.L ** 2
                gens = np.arange(p.n_gens)

                title = "   ".join(
                    f"{PARAM_LABELS.get(n, n).split('(')[0].strip()}={v:.2f}"
                    for n, v in zip(names, x_row)
                )
                # Append key derived ratios to title
                T_abs = x_row[names.index("T_over_E")] * 5.0
                b_val = x_row[names.index("b")]
                cb_val = x_row[names.index("c_bar")]
                title += f"   c̄/b={cb_val/b_val:.3f}  c̄/T={cb_val/T_abs:.3f}"

                # Panel 1 — strategy shares
                ax1 = axes[row_i, 0]
                ax1.stackplot(
                    gens,
                    ts["n_D"]  / N_cells,
                    ts["n_CC"] / N_cells,
                    ts["n_UC"] / N_cells,
                    labels=["D", "CC", "UC"],
                    colors=["#e74c3c", "#e67e22", "#27ae60"],
                    alpha=0.75,
                )
                ax1.set_ylim(0, 1)
                ax1.set_ylabel("Strategy share", fontsize=8)
                ax1.set_xlabel("Generation", fontsize=8)
                ax1.set_title(f"Strategy shares\n{title}", fontsize=6.5)
                ax1.legend(fontsize=7, loc="lower right", ncol=3)
                ax1.tick_params(labelsize=7)

                # Panel 2 — env / flood / wealth
                ax2 = axes[row_i, 1]
                ax2_r = ax2.twinx()
                ax2.plot(gens, ts["mean_env"],   color="lightblue", lw=1.4, label="env")
                ax2.plot(gens, ts["flood_rate"], color="steelblue", lw=1.0, ls="--",
                         label="flood rate")
                ax2_r.plot(gens, ts["mean_wealth"], color="black", lw=1.2, label="avg wealth")
                ax2.axhline(0, color="gray", lw=0.5, ls=":")
                ax2.set_ylim(-1.1, 1.1)
                ax2.set_ylabel("env  /  flood rate", fontsize=8, color="steelblue")
                ax2.set_xlabel("Generation", fontsize=8)
                ax2_r.set_ylabel("avg wealth", fontsize=8)
                ax2.set_title(f"Env / flood / wealth\n{title}", fontsize=6.5)
                lines1 = ax2.get_lines()
                lines2 = ax2_r.get_lines()
                ax2.legend(lines1 + lines2, [l.get_label() for l in lines1 + lines2],
                           fontsize=7, loc="upper right")
                ax2.tick_params(labelsize=7)
                ax2_r.tick_params(labelsize=7)

            combo_range = f"{page_start + 1}–{page_start + n_c}"
            fig.suptitle(
                f"Money-SA timeseries  (seed={SEED}, sample {combo_range} of {N_base})",
                fontsize=9, y=1.01,
            )
            fig.tight_layout()
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    out = OUT_DIR / "timeseries.pdf"
    print(f"Saved → {out}")


# ── entry point ───────────────────────────────────────────────────────────────


def main():
    cfg = _load_config()
    params_list, X, problem = _rebuild_params(cfg)
    seeds = cfg["seeds"]
    N = cfg["N"]
    names = problem["names"]

    print(f"Plotting {len(SA_OUTPUTS)} Sobol outputs × {problem['num_vars']} params "
          f"+ 3 derived-ratio Spearman columns ...")
    plot_sobol_heatmap(params_list, X, problem, seeds)

    print(f"Plotting timeseries for {N} base sample points ...")
    plot_timeseries_pdf(params_list, X, names, seeds, N_base=N)

    print("All figures saved.")


if __name__ == "__main__":
    main()
