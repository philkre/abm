# Cooperation in the Face of Disaster — Simulation Design

**Date:** 2026-06-04  
**Paper:** Jonsson & Jonsson (2025), PLoS ONE 20(4): e0318891  
**Goal:** Reproduce Fig 7 — proportion of successful groups vs proportion of unconditional cooperators (UC), using Julia.

---

## Scope

Base model only: replicating the simulation in the paper's "Simulation results" section (p. 13).

- 1000 groups of 4 players
- 200 rounds per group
- Treatment conditions: 40% check probability, threshold = 60
- Sweep UC proportion 0→1 (CC:FR ratio fixed at 215/21 ≈ 10.2)
- Output: Plots.jl figure matching Fig 7 shape, saved as `sim/fig7.png`

Extensions (wealth distribution, spatial topology) are explicitly out of scope and will be addressed in a future spec.

---

## Architecture

```
sim/
  Project.toml
  Manifest.toml
  src/
    CoopDisaster.jl   # module entry, re-exports public API
    types.jl          # PlayerType, LcpParams, SimConfig
    lcp.jl            # contribution(type, others_mean, cfg) → Float64
    group.jl          # simulate_group(types, cfg, rng) → Bool
    sweep.jl          # run_sweep(uc_props, cfg) → Vector{Float64}
  scripts/
    fig7.jl           # entry point: load module, run sweep, save plot
```

No globals. `SimConfig` is threaded through all functions so parameters can be changed without touching internals.

---

## Types (`src/types.jl`)

```julia
@enum PlayerType UC CC FR

struct LcpParams
    init :: Float64   # first-round contribution
    α    :: Float64   # LCP intercept
    β    :: Float64   # LCP slope
end

struct SimConfig
    n_groups    :: Int
    n_rounds    :: Int
    group_size  :: Int
    endowment   :: Float64
    threshold   :: Float64
    cc_fr_ratio :: Float64
    lcp         :: Dict{PlayerType, LcpParams}
end
```

---

## LCP Calibration (`src/lcp.jl`)

Each agent's contribution is a linear function of the mean contribution of the other group members in the previous round (Linear Contribution Profile, from Kurzban & Houser 2005).

`contribution(type, others_mean) = clamp(α + β × others_mean, 0, endowment)`

**Calibration constraint:** For a group of 4 identical agents at convergence, fixed point is `x = α/(1−β)`. Group total = `4x`. Need `4x ≥ 60` for all-UC groups to succeed, so `x ≥ 15`.

**Parameters** (estimated from Fig 6; exact empirical values in [condcoop GitHub](https://github.com/markusrobertjonsson/condcoop)):

| Type | init | α   | β     | Fixed point | Group (4×) |
|------|------|-----|-------|-------------|------------|
| UC   | 17   | 18  | −0.15 | 15.65       | 62.6 ✓     |
| CC   | 12   |  5  |  0.50 | 10.00       | 40.0       |
| FR   |  5   |  5  |  0.05 |  5.26       | 21.1       |

UC: always above 50% endowment (10 units) — unconditional.  
CC: positive slope, crosses 10 at others_mean = 10 — conditional reciprocator.  
FR: always below 10 — free-rider.

---

## Group Simulation (`src/group.jl`)

```
simulate_group(types, cfg, rng) → Bool
```

1. Init contributions: `contribs[i] = cfg.lcp[types[i]].init`
2. For each round 1..n_rounds:
   - Copy `prev = contribs`
   - For each agent `i`: `contribs[i] = contribution(types[i], mean(prev[-i]), cfg)`
3. Return `sum(contribs) >= cfg.threshold`

Note: disaster check mechanics (40% probability, zeroing accounts) affect earnings but not LCP-based contribution decisions. The simulation tracks contribution convergence only, matching the paper's approach for Fig 7.

---

## Parameter Sweep (`src/sweep.jl`)

```
run_sweep(uc_props, cfg) → Vector{Float64}
```

- For each `uc_prop` in `uc_props`:
  - `cc_prop = (1 − uc_prop) × ratio/(ratio + 1)`
  - `fr_prop = (1 − uc_prop)/(ratio + 1)`
  - Run `cfg.n_groups` independent groups; each randomly assigns 4 types from this distribution
  - Record `n_success / n_groups`
- Parallelised with `Threads.@threads` over UC proportion values
- Each thread uses `Random.default_rng()` (thread-local in Julia 1.7+)

---

## Entry Point (`scripts/fig7.jl`)

1. `include("../src/CoopDisaster.jl")` (or `using CoopDisaster`)
2. Define default `SimConfig`
3. Call `run_sweep(0.0:0.01:1.0, cfg)`
4. Plot with Plots.jl: success rate (y) vs UC proportion (x), vertical line at UC = 0.56 (empirical value from paper)
5. Save `sim/fig7.png`

---

## Success Criteria

- Fig 7 shape reproduced: success rate ≈ 0 below UC ≈ 0.4, nonlinear rise, ≈ 1.0 at UC = 1.0
- Empirical UC proportion (0.56) falls on the rising portion of the curve
- Runs in < 5 seconds on 4+ threads
- No globals; `SimConfig` controls all parameters

---

## Out of Scope

- Wealth/endowment heterogeneity
- Spatial/network topology
- Sensitivity analysis
- Pluto/Jupyter notebook interface
- Nash equilibrium analysis
