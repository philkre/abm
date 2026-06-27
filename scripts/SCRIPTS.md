# Scripts reference

All scripts run from the **`philkre-abm/` root** via `uv run`.

---

## Exploratory money-parameter SA (local, fast)

Sweeps 5 money/process parameters while holding NetLogo env params fixed:
  **T/E [0.2,0.9], b [1,21], c̄ [0.1,1.5], ℓ [0.05,1.0], σ [0,0.5]**
  Fixed: delta=0.042, gamma=0.018, eta=0.005, kappa=0.1, beta=1.8, p_max=1.0

Includes Sobol S1/ST heatmap for the 5 direct params plus Spearman r² for derived
ratios c̄/T, c̄/b, T/b. Confirmed: w0 is uninformative (dropped); b is the primary
phase-transition lever; c̄ and T/E dominate cooperative dynamics.

```bash
# 1. Generate data (L=60, 200 gens, N=16 → 112 samples × 3 seeds ≈ 5 min)
.venv/Scripts/python.exe scripts/local_money_sa_run.py

# Optional: larger run for better statistics
.venv/Scripts/python.exe scripts/local_money_sa_run.py --N 32 --L 100 --n-gens 500

# 2. Plot Sobol heatmap + timeseries PDF
.venv/Scripts/python.exe scripts/local_money_sa_plot.py
```

Outputs: `results/local_money_sa/sobol_heatmap.pdf`, `results/local_money_sa/timeseries.pdf`

---

## Snellius — main Sobol SA (linear risk phase, v2)

5-parameter Sobol SA (updated 2026-06-27):
  **β [0.1,10], p_max [0,1], T/E [0.2,0.9], b [1,30], η [0,0.020]**
  Fixed: delta=0.042, gamma=0.018, kappa=0.1, c_bar=0.75, ell=0.64, sigma=0.1,
         lambda_mode=lognormal, lambda_mean=2.25, lambda_sigma=0.5 (heterogeneous λ)

N=5120 → 35,840 Saltelli samples × 20 seeds = 716,800 episodes (~7–9 h on Genoa).
14 output keys: resilience, flood_rate, mean_env, mean_env_std, coop_frac,
  coop_frac_std, p_span_UC, p_span_CC, interface_density, mean_wealth,
  mean_wealth_std, gini_wealth, mean_fitness, mean_payoff.

```bash
sbatch scripts/snellius_sobol_linear.sh
```

After completion, analyse results:
```bash
spatcoop sensitivity analyse --out-dir /scratch-shared/lschoonheid/results/sa/linear_sobol
bash scripts/make_sa_plots.sh
```

---

## Snellius — PAWN SA (linear risk phase, v2)

Same 5 parameters as Sobol, Latin Hypercube + KS statistic. Run separately
(LHS is not deterministic — do not split across array tasks).
N=3584 = 512*(5+2) LHS samples × 20 seeds = 71,680 episodes (~8–10 h on Genoa).

```bash
sbatch scripts/snellius_pawn_linear.sh
```

---

## Snellius — targeted λ SA (loss-aversion heterogeneity axis)

1-parameter PAWN SA varying `lambda_mean` [1.0, 3.0] under lognormal λ (sigma=0.5).
Documents the effect of loss-aversion spread on cooperation and resilience (ODD+
second heterogeneity axis beyond wealth). All other parameters at headline values.

```bash
sbatch scripts/snellius_lambda_sa.sh
```

After completion:
```bash
spatcoop sensitivity analyse --out-dir /scratch-shared/lschoonheid/results/sa/lambda_pawn
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

## Snellius — ell × b diagnostic SA

2-parameter Sobol SA over (ell [0.1,0.9]) × (b [1,25]) at NetLogo-verified fixed params.
Generates the data for `plot_wealth_diagnostics.py`.  Cannot use the 5-param headline SA
because ell is fixed there (ell=0.64).

N=512 → 512*(2+2)=2048 Saltelli samples × 20 seeds = 40,960 episodes
Fixed: T=1.7, p_max=1.0, eta=0.005, sigma=0.1, c_bar=0.75, delta=0.042, gamma=0.018,
       kappa=0.1, initial_mix=thirds, lambda_mode=lognormal, lambda_mean=2.25
Estimated ~2–3 h on 96 CPUs.

```bash
sbatch scripts/snellius_ell_b_sa.sh
```

Results: `/scratch-shared/lschoonheid/results/ell_b_sa/`

---

## Snellius — wealth and strategy diagnostic plots

Three-page PDF from the ell×b SA (`results/figures/wealth_diagnostics.pdf`).
Run on the Snellius login node or locally after syncing results.

1. **ell vs gini_wealth, stratified by b-regime** — shows how ℓ drives wealth inequality
   *within* the collapse / transition / cooperative phases separately (bin-mean lines per
   regime), not averaged across them.  Background scatter coloured by b.
2. **b vs dominant wealth-oscillation period (FFT)** — mean_wealth timeseries FFT-ed per
   sample (first 25 % discarded as warm-up).  Log y-axis separates oscillatory runs
   (period ≈ 10–200 gens) from flat/collapse.  Coloured by cooperation fraction.
3. **Strategy shares in (b, ell) space** — three scatter panels (D, CC, UC) coloured by
   equilibrium fraction.  D=Reds, CC=Oranges, UC=Greens (same scheme as timeseries plots).

```bash
# On Snellius login node
uv run python scripts/plot_wealth_diagnostics.py

# Locally (after rsync of ell_b_sa/ from scratch)
.venv/Scripts/python.exe scripts/plot_wealth_diagnostics.py \
    --data-dir /synced/ell_b_sa \
    --raw-dir  /synced/ell_b_sa/raw

# Quick local smoke-test (N=4, L=30, 150 gens → 32 episodes, ~2 min)
.venv/Scripts/python.exe -m spatcoop.cli sensitivity run \
    --vary ell:0.1:0.9 --vary b:1.0:25.0 \
    --method sobol --N 4 --n-seeds 2 \
    --fix L:30 --fix n_gens:150 --fix T:1.7 --fix p_max:1.0 \
    --fix eta:0.005 --fix sigma:0.1 --fix c_bar:0.75 \
    --fix delta:0.042 --fix gamma:0.018 --fix kappa:0.1 \
    --fix initial_mix:thirds --fix lambda_mode:lognormal --fix lambda_mean:2.25 \
    --output-key gini_wealth --output-key mean_wealth --output-key coop_frac \
    --out-dir results/test_ell_b --raw-dir results/test_ell_b/raw
.venv/Scripts/python.exe scripts/plot_wealth_diagnostics.py \
    --data-dir results/test_ell_b --raw-dir results/test_ell_b/raw \
    --out results/test_ell_b/wealth_diagnostics_test.pdf
```

Requires: `snellius_ell_b_sa.sh` to have been run first (or the smoke-test above).

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
