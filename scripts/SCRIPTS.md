# Scripts reference

All scripts run from the **`philkre-abm/` root** via `uv run`.

---

## Exploratory money-parameter SA (local, fast)

Sweeps T/E, income `b`, initial wealth `w0`, and loss fraction `ell` while holding
NetLogo environmental params fixed (`delta=0.042, gamma=0.018, eta=0.005, kappa=0.1`).
Goal: identify which two money params to include in the big Snellius SA alongside β and p_max.

```bash
# 1. Generate data (L=60, 200 gens, N=16 Sobol base → 96 samples × 3 seeds ≈ 2 min)
uv run python scripts/local_money_sa_run.py

# Optional: larger run for better statistics
uv run python scripts/local_money_sa_run.py --N 32 --L 100 --n-gens 500

# 2. Plot Sobol heatmap + timeseries PDF
uv run python scripts/local_money_sa_plot.py
```

Outputs: `results/local_money_sa/sobol_heatmap.pdf`, `results/local_money_sa/timeseries.pdf`

---

## Snellius — main Sobol SA (linear risk phase)

4-parameter Sobol SA: β, p_max, T/E, ell. Fixed: L=200, eta=0.03, sigma=0.1.

```bash
sbatch scripts/snellius_sobol_linear.sh
```

After completion, analyse results:
```bash
spatcoop sensitivity analyse --out-dir /scratch-shared/lschoonheid/results/sa/linear_sobol
bash scripts/make_sa_plots.sh
```

---

## Snellius — PAWN SA (linear risk phase)

Same parameters as Sobol but uses Latin Hypercube + KS statistic. Run separately
(LHS is not deterministic — do not split across array tasks).

```bash
sbatch scripts/snellius_pawn_linear.sh
```

---

## Snellius — targeted 1-D sweeps

Sweeps delta, gamma, eta, lambda_mean, b, w0 one at a time over the headline config.
Produces `op_vs_<param>.pdf` grid figures (all order parameters vs the swept value).

```bash
sbatch scripts/snellius_sweeps.sh
```

---

## Snellius — diagnostics & snapshots

Long baseline runs at L=200 for timeseries and spatial snapshot figures.

```bash
sbatch scripts/snellius_diagnostics.sh
```

---

## Snellius — β × p_max visualisation sweep

10×10 grid in (β, p_max) space with snapshot frames.

```bash
sbatch scripts/snellius_viz_sweep.sh
```

---

## Post-processing (laptop / Snellius login node)

```bash
# Sobol + PAWN bar charts for the curated output set
bash scripts/make_sa_plots.sh

# All order parameters (runs from cached NPZ without re-simulation)
bash scripts/make_sa_plots_all.sh

# PAWN-specific figure
uv run python scripts/plot_sa_pawn.py
```

---

## General CLI

```bash
# Single run (view timeseries in results/figures/)
uv run spatcoop run --n-gens 500 --L 60

# Sensitivity run (dynamic params, any method)
uv run spatcoop sensitivity run \
    --vary beta:0.1:10 --vary p_max:0.0:1.0 \
    --fix L:60 --fix eta:0.005 \
    --method sobol --N 32 --n-seeds 3

# Analyse saved results
uv run spatcoop sensitivity analyse --out-dir results/sa/my_run
```

Windows note: prefix commands with `PYTHONUTF8=1` or set it in the environment if you
see codec errors on the console.
