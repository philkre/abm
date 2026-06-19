# Cooperation in the Face of Disaster — ABM

Implementation of Jonsson & Jonsson (2025), *PLoS ONE* 20(4): e0318891.

**Paper:** [doi.org/10.1371/journal.pone.0318891](https://doi.org/10.1371/journal.pone.0318891)  
**Paper's simulation code:** [github.com/markusrobertjonsson/condcoop](https://github.com/markusrobertjonsson/condcoop)

## Structure

```
src/coop_disaster/  # Python ABM package (Fig 7 sweep)
  types.py          # PlayerType, LcpParams, SimConfig, DEFAULT_CONFIG
  lcp.py            # contribution() — single-agent LCP update
  group.py          # assign_types(), simulate_group()
  sweep.py          # run_sweep() — parallel UC proportion sweep
  plot.py           # plot_fig7()
  __main__.py       # CLI entry point (argparse)
src/spatial/        # Spatial threshold PGG on a Von Neumann lattice (Mesa 3.x)
  config.py         # ModelConfig dataclass + DEFAULT_CONFIG
  agents.py         # HouseholdAgent (UC / D strategies, CellAgent)
  model.py          # SpatialCollectiveRiskModel — full phase-based step loop
  run.py            # Entry point: run 500 steps, save results.png
julia_implementation/  # Julia simulation (reference implementation)
notebooks/          # Python/Mesa exercises (course material)
  1/1-mesa/         # Mesa basics
  2-3/2-axelrod/    # Axelrod tournament
  2-3/3-discrete-choice/
  4/                # Wolf-sheep predator-prey + sensitivity analysis
```

## Paper summary

Threshold Public Goods Game with stochastic disasters. Groups of 4 players each contribute from a 20-unit endowment per round. If group contribution ≥ 60 when a disaster check occurs (40% probability per round), the group is safe. Otherwise earnings are zeroed.

Three player types defined by Linear Contribution Profiles (LCP):

| Type | Behaviour | Fixed point |
|------|-----------|-------------|
| UC — Unconditional Cooperator | Always contributes ~17 regardless of others | 17.13 |
| CC — Conditional Cooperator | Matches others; low in isolation | 6.06 |
| FR — Free-Rider | Always contributes ~5 | 4.74 |

Key finding: cooperation is higher and increases over time when disaster risk is present, driven by unconditional cooperators.

## Julia simulation (Fig 7)

Sweeps UC proportion 0→1 (CC:FR ratio fixed at 10.2), runs 1000 groups × 200 rounds, plots fraction of successful groups. Only all-UC groups reach the threshold — producing the convex curve in Fig 7.

**Setup** (Julia 1.7+ required):

```bash
cd sim
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

**Run:**

```bash
julia --project=. --threads=auto scripts/fig7.jl
# → saves sim/fig7.png
```

**Test:**

```bash
julia --project=. --threads=auto test/runtests.jl
```

## Python simulation

**Setup** ([uv](https://docs.astral.sh/uv/) required):

```bash
uv sync
```

**Run (Fig 7 sweep):**

```bash
uv run coop-disaster                   # 1 000 groups, serial
uv run coop-disaster --jobs 4          # parallel with 4 workers
uv run coop-disaster --help            # all options
```

Key options:

| Flag | Default | Description |
|------|---------|-------------|
| `--n-groups N` | 1000 | Groups per UC proportion value |
| `--n-rounds N` | 200 | LCP update rounds per group |
| `--uc-steps N` | 101 | Points swept from 0 → 1 |
| `--output FILE` | fig7.png | Output plot path |
| `--jobs N` | 1 | Parallel worker processes |
| `--no-plot` | — | Skip plot, print table only |

**Use as a library:**

```python
from coop_disaster import SimConfig, run_sweep

cfg = SimConfig(n_groups=500, n_rounds=200)
uc_props = [i / 100 for i in range(101)]
rates = run_sweep(uc_props, cfg, n_jobs=4)
```

## Spatial threshold PGG (src/spatial/)

A minimal spatial collective-risk game on a 20×20 torus with Von Neumann
neighbourhoods.  Agents are Unconditional Cooperators (UC) or Defectors (D).
They pool contributions within focal groups (agent + 4 neighbours), face
independent disaster draws when the pool is below the threshold, and update
strategies by synchronous Fermi imitation.

**Run (500 steps, saves `results.png`):**

```bash
uv run spatial-run
uv run python src/spatial/plot.py
```

**Use as a library:**

```python
from spatial import SpatialCollectiveRiskModel, ModelConfig

cfg = ModelConfig(grid_size=20, n_steps=500, seed=42)
model = SpatialCollectiveRiskModel(cfg)
for _ in range(cfg.n_steps):
    model.step()
df = model.datacollector.get_model_vars_dataframe()
```

**Key parameters** (all in `ModelConfig`):

| Field | Default | Description |
|-------|---------|-------------|
| `grid_size` | 20 | Side length of the square lattice |
| `initial_uc_fraction` | 0.5 | Starting UC fraction |
| `initial_wealth` | 10.0 | Initial wealth per agent |
| `contribution` | 1.0 | UC contribution per round |
| `threshold` | 3.0 | Pool sum needed to avert disaster |
| `disaster_prob` | 0.5 | Prob of loss if pool < threshold |
| `loss_fraction` | 0.5 | Fraction of wealth lost in disaster |
| `beta` | 1.0 | Fermi selection strength |
| `mu` | 0.001 | Mutation probability per agent per step |
| `n_steps` | 500 | Steps run by `spatial-run` |
| `seed` | 42 | RNG seed |

---

## Python notebooks

**Setup** ([uv](https://docs.astral.sh/uv/) required):

```bash
cd notebooks
uv sync
uv run jupyter notebook
```

Navigate to `notebooks/` in Jupyter.
