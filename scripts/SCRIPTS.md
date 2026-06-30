# Scripts reference

All scripts run from the **`philkre-abm/` root** via `uv run`.

---

## Reproducing the report's sensitivity analysis

The report's §Sensitivity Analysis (PAWN + Sobol' over 4 parameters: β, p_max, T/E, ℓ) is the
analysis actually published, backed by the committed results in `results/sa/linear_pawn/` and
`results/sa/linear_sobol/`. Two ways to reproduce it, cheapest first.

**1. Replot from committed results (seconds, no simulation):**
```bash
bash scripts/make_sa_plots.sh
```
Regenerates every SA figure in the report (main text + appendix) from the already-committed
indices — no re-simulation needed.

**2. Re-run from scratch** (6,140 PAWN + 61,440 Sobol episodes total; the Sobol run is
HPC-scale — it's what originally ran on a single Snellius `genoa` node):
```bash
# PAWN: N=307 LHS samples × 20 seeds
uv run spatcoop sensitivity run \
    --vary beta:0.1:10.0 --vary p_max:0.0:1.0 --vary T_over_E:0.4:0.9 --vary ell:0.0:1.0 \
    --fix L:200 --fix n_gens:1500 --fix eta:0.03 --fix b:1.0 --fix sigma:0.1 \
    --fix kappa:0.2 --fix mu:0.01 --fix delta:0.03 --fix gamma:0.03 \
    --fix lambda_mode:homogeneous --fix lambda_mean:1.0 --fix initial_mix:thirds \
    --output-key resilience --output-key flood_rate --output-key mean_env \
    --output-key coop_frac --output-key gini_wealth --output-key interface_density \
    --output-key mean_fitness --output-key mean_payoff \
    --method pawn --N 307 --n-seeds 20 --out-dir results/sa/linear_pawn

# Sobol: N=512 base → 3,072 Saltelli points × 20 seeds (same --vary/--fix/--output-key as above)
uv run spatcoop sensitivity run \
    --vary beta:0.1:10.0 --vary p_max:0.0:1.0 --vary T_over_E:0.4:0.9 --vary ell:0.0:1.0 \
    --fix L:200 --fix n_gens:1500 --fix eta:0.03 --fix b:1.0 --fix sigma:0.1 \
    --fix kappa:0.2 --fix mu:0.01 --fix delta:0.03 --fix gamma:0.03 \
    --fix lambda_mode:homogeneous --fix lambda_mean:1.0 --fix initial_mix:thirds \
    --output-key resilience --output-key flood_rate --output-key mean_env \
    --output-key coop_frac --output-key gini_wealth --output-key interface_density \
    --output-key mean_fitness --output-key mean_payoff \
    --method sobol --N 512 --n-seeds 20 --out-dir results/sa/linear_sobol
```
Then `bash scripts/make_sa_plots.sh` to regenerate the figures from the new results.

---

## Extended sensitivity analysis (proposed, not completed)

The Discussion proposes extending the design above to directly vary income `b` and the
resilience-erosion rate `η` — the two parameters the Results identify as the primary drivers of
recovery, but which the published SA holds fixed — together with heterogeneous loss aversion
(`lambda_mode=lognormal, lambda_mean=2.25`) instead of the risk-neutral default.

**Design:** β [0.1,10], p_max [0,1], T/E [0.2,0.9], b [1,30], η [0,0.020].
Fixed: δ=0.042, γ=0.018, κ=0.1, c̄=0.75, ℓ=0.64, σ=0.1.

**Status: attempted, not completed.** The PAWN run simulated all 71,680 episodes, but the analysis
step (computing the indices from the checkpoints) was repeatedly killed by Snellius's 2-hour
wall-time limit. The Sobol run never started — every submission was cancelled by the scheduler due
to an unresolved CPU-allocation issue on this account. The project's Snellius compute budget is
now exhausted; re-running needs a fresh allocation.

```bash
sbatch scripts/snellius_pawn_linear.sh    # N=3584 LHS × 20 seeds = 71,680 episodes, ~8-10h
sbatch scripts/snellius_sobol_linear.sh   # N=5120 → 35,840 points × 20 seeds = 716,800 episodes, ~7-9h
```

If the PAWN checkpoints are still on scratch, recover the indices without re-simulating:
```bash
sbatch scripts/snellius_pawn_analyse.sh   # runs scripts/recover_pawn_and_analyse.py
```

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
.venv/Scripts/python.exe archive/scripts/local_money_sa_run.py

# Optional: larger run for better statistics
.venv/Scripts/python.exe archive/scripts/local_money_sa_run.py --N 32 --L 100 --n-gens 500

# 2. Plot Sobol heatmap + timeseries PDF
.venv/Scripts/python.exe archive/scripts/local_money_sa_plot.py
```

Outputs: `results/local_money_sa/sobol_heatmap.pdf`, `results/local_money_sa/timeseries.pdf`
(N=16, L=60 — exploratory only, not statistically significant; not used in the report).

---

## Snellius — targeted λ SA (loss-aversion heterogeneity axis)

1-parameter PAWN SA varying `lambda_mean` [1.0, 3.0] under lognormal λ (sigma=0.5).
Documents the effect of loss-aversion spread on cooperation and resilience (ODD+
second heterogeneity axis beyond wealth). All other parameters at headline values.

```bash
sbatch archive/scripts/snellius_lambda_sa.sh
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
sbatch archive/scripts/snellius_diagnostics.sh
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
sbatch archive/scripts/snellius_ell_b_sa.sh
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
uv run python archive/scripts/plot_wealth_diagnostics.py

# Locally (after rsync of ell_b_sa/ from scratch)
.venv/Scripts/python.exe archive/scripts/plot_wealth_diagnostics.py \
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
.venv/Scripts/python.exe archive/scripts/plot_wealth_diagnostics.py \
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
