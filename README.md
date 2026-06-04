# Cooperation in the Face of Disaster — ABM

Implementation of Jonsson & Jonsson (2025), *PLoS ONE* 20(4): e0318891.

**Paper:** [doi.org/10.1371/journal.pone.0318891](https://doi.org/10.1371/journal.pone.0318891)  
**Paper's simulation code:** [github.com/markusrobertjonsson/condcoop](https://github.com/markusrobertjonsson/condcoop)

## Structure

```
notebooks/          # Python/Mesa exercises (course material)
  1/1-mesa/         # Mesa basics
  2-3/2-axelrod/    # Axelrod tournament
  2-3/3-discrete-choice/
  4/                # Wolf-sheep predator-prey + sensitivity analysis
sim/                # Julia simulation replicating Fig 7 from paper
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

## Python notebooks

**Setup** ([uv](https://docs.astral.sh/uv/) required):

```bash
uv sync
uv run jupyter notebook
```

Navigate to `notebooks/` in Jupyter.
