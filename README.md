# Spatial Flood Cooperation — ABM

Agent-based model of households maintaining shared flood defences on a spatial lattice. Three strategies compete — unconditional cooperators (UC), conditional cooperators (CC), and defectors (D) — in a threshold public-goods game coupled to an environmental feedback loop that links collective effort to local flood risk.

**Research question:** Can locally organised communities sustain flood defences against free-riding, and which strategy mix is most resilient?

**Model lineage:** Builds on the evolutionary spatial PGG of Ding et al. (2024) and the environmental feedback model of Weitz et al. (2016), with three novelties: a threshold flood-immunity rule, a resilience-erosion term (floods damage defences), and conditional cooperation as a third strategy type following Jonsson & Jonsson (2025).

---

## Structure

```
src/spatcoop/       # Main model — NumPy/Numba ABM + full SA pipeline
src/spatial/        # Precursor — Mesa 3.x model with Weitz-style feedback
src/coop_disaster/  # Jonsson validation (well-mixed, used for mean-field baseline)
src/condcoop/       # Additional Jonsson figures
tests/              # Verification test suite
scripts/            # Snellius HPC batch jobs
notebooks/          # Course practicals
```

---

## Model

Agents occupy an L × L torus; each belongs to a focal group of 5 (itself + 4 von Neumann neighbours). Each generation:

1. **Contribute.** UC pays c̄; D pays 0; CC matches the mean of neighbours' previous contributions, with an optional loss-aversion premium.
2. **Pool.** Contributions are summed per focal group.
3. **Flood check.** Groups clearing threshold T are immune; others face flood probability p\_i = f(e\_i), where e\_i ∈ [−1, 1] is the local defence environment.
4. **Wealth update.** Ornstein–Uhlenbeck process: additive income, minus contribution, minus fractional loss on a flood.
5. **Environment update.** Cooperation repairs defences, neglect degrades them, and floods cause additional damage η (the resilience-erosion trap).
6. **Imitation.** Fermi rule — agents copy better-performing neighbours stochastically.

The mean-field well-mixed reduction admits only the all-defector equilibrium; spatial structure is the necessary condition for cooperation to survive.

---

## Main package: `spatcoop`

High-performance NumPy/Numba ABM with Sobol and PAWN sensitivity analysis via SALib.

**Setup** ([uv](https://docs.astral.sh/uv/) and Python ≥ 3.13 required):

```bash
uv sync
```

**Single run:**

```bash
uv run spatcoop run-single --L 50 --n-gens 500 --seed 0
```

**Sensitivity analysis (Snellius HPC):**

```bash
sbatch scripts/snellius_sobol_linear.sh   # Sobol S1/ST, linear risk phase
sbatch scripts/snellius_pawn_linear.sh    # PAWN KS, single-node
```

**Diagnostic plots:**

```bash
bash scripts/make_sa_plots.sh             # curated SA bar charts
bash scripts/make_sa_plots_all.sh         # all 26 order-parameter bars
sbatch scripts/snellius_diagnostics.sh   # timeseries, spectra, lattice snapshots
sbatch scripts/snellius_sweeps.sh        # 1-D parameter sweeps
```

**Key parameters** (all in `src/spatcoop/params.py`):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `L` | 150 | Lattice side length |
| `c_bar` | 0.75 | UC/CC max contribution |
| `T` | 3.75 | Threshold pool for immunity (= 0.75 × 5) |
| `p_max` | 0.5 | Maximum flood probability |
| `ell` | 0.34 | Flood loss fraction |
| `delta` | 0.03 | Environment repair rate per cooperator |
| `gamma` | 0.03 | Environment degradation rate per defector |
| `eta` | 0.0 | Flood damage to defences (0 = no erosion) |
| `beta` | 2.0 | Fermi selection strength |
| `mu` | 0.01 | Mutation rate |
| `risk_mode` | `linear` | `linear` or `sigmoid` flood–environment link |

---

## Precursor: `spatial`

Mesa 3.x model with Weitz-style continuous environmental feedback (no threshold immunity, no resilience erosion). Useful for isolating the feedback mechanism.

```bash
uv run spatial-run
```

---

## Jonsson validation: `coop_disaster`

Well-mixed threshold PGG used to reproduce the Jonsson & Jonsson (2025) mean-field baseline and verify the model against their Fig 7.

```bash
uv run coop-disaster          # 1 000 groups, serial
uv run coop-disaster --jobs 4 # parallel
uv run coop-disaster --help
```

---

## Notebooks

Course practicals (Mesa intro, Axelrod, Wolf–Sheep, sensitivity analysis):

```bash
cd notebooks && uv sync && uv run jupyter notebook
```
