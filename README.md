# Cooperation in the Face of Disaster — Julia Simulation

Replicates Fig 7 from Jonsson & Jonsson (2025), *PLoS ONE* 20(4): e0318891.

**Paper:** "Cooperation in the face of disaster"  
**Source code for paper's simulation:** [github.com/markusrobertjonsson/condcoop](https://github.com/markusrobertjonsson/condcoop)

## What this does

Simulates a Threshold Public Goods Game with stochastic disasters. 1000 groups of 4 players run 200 rounds each. Sweeps the proportion of Unconditional Cooperators (UC) from 0 to 1 (CC:FR ratio fixed at 10.2) and plots the fraction of groups that reach the cooperation threshold.

## Player types

Each player has a Linear Contribution Profile (LCP): `contribution = clamp(α + β × own_last_contribution, 0, 20)`.

| Type | Description | α | β | Fixed point |
|------|-------------|-----|-----|-------------|
| UC | Unconditional Cooperator — always gives >10 | 17.60 | −0.027 | 17.13 |
| CC | Conditional Cooperator — matches others | 0.816 | 0.865 | 6.06 |
| FR | Free-Rider — always gives <10 | 4.10 | 0.134 | 4.74 |

Parameters are averages across 4 treatments (10P, 40P, Level, Impact) from the paper's empirical LCP analysis.

**Note on dynamics:** Each agent updates based on its *own* last contribution (matching the paper's `fig6.py` exactly). This makes mixed groups converge independently — only all-UC groups (4 × 17.13 = 68.5 ≥ 60) reach the threshold, producing the convex curve in Fig 7.

## Setup

Requires Julia 1.7+. Install dependencies once:

```bash
cd sim
julia --project=. -e 'using Pkg; Pkg.instantiate()'
```

## Run

```bash
julia --project=. --threads=auto scripts/fig7.jl
```

Outputs `sim/fig7.png`.

## Test

```bash
julia --project=. --threads=auto test/runtests.jl
```

## Structure

```
sim/
  src/
    CoopDisaster.jl   # module entry
    types.jl          # PlayerType, LcpParams, SimConfig, DEFAULT_CONFIG
    lcp.jl            # contribution(type, others_mean, cfg)
    group.jl          # assign_types, simulate_group
    sweep.jl          # run_sweep — threaded sweep over UC proportions
  scripts/
    fig7.jl           # entry point: runs sweep, saves fig7.png
  test/
    runtests.jl       # 30 tests
```
