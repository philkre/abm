# Cooperation in the Face of Disaster — Simulation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Fig 7 simulation from Jonsson & Jonsson (2025) in Julia — sweep UC proportion 0→1, measure group success rate, reproduce the nonlinear cooperation curve.

**Architecture:** Pure Julia module (`CoopDisaster`) with four focused files (types, lcp, group, sweep) wired together via `src/CoopDisaster.jl`. Entry point in `scripts/fig7.jl` loads the module, runs the sweep, saves `sim/fig7.png`. No globals — all parameters flow through `SimConfig`.

**Tech Stack:** Julia 1.12, Plots.jl (already installed), stdlib `Test`, `Random`, `Statistics`. No external ABM framework.

---

## File Map

| File | Responsibility |
|------|---------------|
| `sim/src/types.jl` | `PlayerType` enum, `LcpParams` struct, `SimConfig` struct, `DEFAULT_CONFIG` |
| `sim/src/lcp.jl` | `contribution(type, others_mean, cfg)` — single-agent LCP update |
| `sim/src/group.jl` | `assign_types(uc_prop, cfg, rng)`, `simulate_group(types, cfg, rng)` |
| `sim/src/sweep.jl` | `run_sweep(uc_props, cfg)` — threaded sweep over UC proportions |
| `sim/src/CoopDisaster.jl` | Module entry, includes all above, exports public API |
| `sim/scripts/fig7.jl` | Entry point: load module, run sweep, plot, save `fig7.png` |
| `sim/test/runtests.jl` | All tests |

**Delete:** `sim/fig7.jl` (buggy prototype — LCP params miscalibrated, all outputs zero)

---

## Task 1: Clean up and scaffold structure

**Files:**
- Delete: `sim/fig7.jl`
- Create: `sim/src/CoopDisaster.jl`
- Create: `sim/src/types.jl`
- Create: `sim/scripts/fig7.jl` (stub)
- Create: `sim/test/runtests.jl` (stub)

- [ ] **Step 1: Delete the buggy prototype**

```bash
rm /path/to/sim/fig7.jl sim/fig7.png
```

Replace `/path/to/sim` with the actual path. From the repo root:
```bash
rm sim/fig7.jl sim/fig7.png
```

- [ ] **Step 2: Create directory structure**

```bash
mkdir -p sim/src sim/scripts sim/test
```

- [ ] **Step 3: Write `sim/src/types.jl`**

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

# Parameters estimated from Fig 6. Fixed-point constraint: 4 × α/(1−β) ≥ 60.
# UC: α/(1−β) = 18/1.15 ≈ 15.65, group total ≈ 62.6 ✓
# CC: α/(1−β) = 5/0.5  = 10.00, group total = 40.0
# FR: α/(1−β) = 5/0.95 ≈  5.26, group total ≈ 21.1
const DEFAULT_CONFIG = SimConfig(
    1_000,
    200,
    4,
    20.0,
    60.0,
    215.0 / 21.0,
    Dict(
        UC => LcpParams(17.0, 18.0, -0.15),
        CC => LcpParams(12.0,  5.0,  0.50),
        FR => LcpParams( 5.0,  5.0,  0.05),
    )
)
```

- [ ] **Step 4: Write `sim/src/CoopDisaster.jl` (module entry — include stubs)**

```julia
module CoopDisaster
    using Random, Statistics

    include("types.jl")

    # Remaining files added in later tasks
    export PlayerType, UC, CC, FR
    export LcpParams, SimConfig, DEFAULT_CONFIG
end
```

- [ ] **Step 5: Write `sim/test/runtests.jl` (stub)**

```julia
include("../src/CoopDisaster.jl")
using .CoopDisaster
using Test

@testset "CoopDisaster" begin
    @test DEFAULT_CONFIG.n_groups == 1_000
    @test DEFAULT_CONFIG.group_size == 4
    @test DEFAULT_CONFIG.threshold == 60.0
    @test haskey(DEFAULT_CONFIG.lcp, UC)
    @test haskey(DEFAULT_CONFIG.lcp, CC)
    @test haskey(DEFAULT_CONFIG.lcp, FR)
end
```

- [ ] **Step 6: Run the stub test**

```bash
cd sim && julia --project=. test/runtests.jl
```

Expected output:
```
Test Summary: | Pass  Total  Time
CoopDisaster  |    5      5
```

- [ ] **Step 7: Write stub `sim/scripts/fig7.jl`**

```julia
include("../src/CoopDisaster.jl")
using .CoopDisaster
println("Module loaded. n_groups = $(DEFAULT_CONFIG.n_groups)")
```

- [ ] **Step 8: Verify stub script runs**

```bash
cd sim && julia --project=. scripts/fig7.jl
```

Expected: `Module loaded. n_groups = 1000`

- [ ] **Step 9: Commit**

```bash
git add sim/src/ sim/scripts/ sim/test/ && git rm sim/fig7.jl sim/fig7.png
git commit -m "feat: scaffold CoopDisaster Julia module structure"
```

---

## Task 2: LCP contribution function

**Files:**
- Create: `sim/src/lcp.jl`
- Modify: `sim/src/CoopDisaster.jl` (add include + exports)
- Modify: `sim/test/runtests.jl` (add LCP tests)

- [ ] **Step 1: Write the failing tests**

Add to `sim/test/runtests.jl` after the existing `@testset` block:

```julia
@testset "LCP contribution" begin
    cfg = DEFAULT_CONFIG

    # UC always above 50% endowment (10 units) regardless of others
    @test contribution(UC, 0.0, cfg)  > 10.0
    @test contribution(UC, 10.0, cfg) > 10.0
    @test contribution(UC, 20.0, cfg) > 10.0

    # FR always below 10 units
    @test contribution(FR, 0.0, cfg)  < 10.0
    @test contribution(FR, 10.0, cfg) < 10.0
    @test contribution(FR, 20.0, cfg) < 10.0

    # CC crosses 10 with positive slope
    @test contribution(CC, 0.0, cfg)  < 10.0
    @test contribution(CC, 20.0, cfg) > 10.0

    # Contributions clipped to [0, endowment]
    @test contribution(UC, 1000.0, cfg) <= cfg.endowment
    @test contribution(FR, -1000.0, cfg) >= 0.0
end
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd sim && julia --project=. test/runtests.jl
```

Expected: `UndefVarError: contribution not defined`

- [ ] **Step 3: Write `sim/src/lcp.jl`**

```julia
function contribution(type::PlayerType, others_mean::Float64, cfg::SimConfig)::Float64
    p = cfg.lcp[type]
    clamp(p.α + p.β * others_mean, 0.0, cfg.endowment)
end
```

- [ ] **Step 4: Add include + export to `sim/src/CoopDisaster.jl`**

```julia
module CoopDisaster
    using Random, Statistics

    include("types.jl")
    include("lcp.jl")

    export PlayerType, UC, CC, FR
    export LcpParams, SimConfig, DEFAULT_CONFIG
    export contribution
end
```

- [ ] **Step 5: Run tests — expect pass**

```bash
cd sim && julia --project=. test/runtests.jl
```

Expected:
```
Test Summary:    | Pass  Total  Time
CoopDisaster     |    5      5
LCP contribution |   10     10
```

- [ ] **Step 6: Commit**

```bash
git add sim/src/lcp.jl sim/src/CoopDisaster.jl sim/test/runtests.jl
git commit -m "feat: add LCP contribution function with tests"
```

---

## Task 3: Group simulation

**Files:**
- Create: `sim/src/group.jl`
- Modify: `sim/src/CoopDisaster.jl` (add include + exports)
- Modify: `sim/test/runtests.jl` (add group tests)

- [ ] **Step 1: Write the failing tests**

Add to `sim/test/runtests.jl`:

```julia
@testset "assign_types" begin
    cfg = DEFAULT_CONFIG
    rng = MersenneTwister(42)

    # All UC
    types = assign_types(1.0, cfg, rng)
    @test length(types) == cfg.group_size
    @test all(t == UC for t in types)

    # All FR (uc_prop=0, cc_fr_ratio very small → all FR)
    cfg_all_fr = SimConfig(
        cfg.n_groups, cfg.n_rounds, cfg.group_size,
        cfg.endowment, cfg.threshold,
        0.0,   # cc_fr_ratio = 0 → no CC, all remaining are FR
        cfg.lcp
    )
    types_fr = assign_types(0.0, cfg_all_fr, MersenneTwister(1))
    @test all(t == FR for t in types_fr)

    # Mixed: each type possible
    rng2 = MersenneTwister(0)
    seen = Set{PlayerType}()
    for _ in 1:500
        push!(seen, assign_types(0.5, cfg, rng2)...)
    end
    @test UC in seen
    @test CC in seen
    @test FR in seen
end

@testset "simulate_group convergence" begin
    cfg = DEFAULT_CONFIG
    rng = MersenneTwister(42)

    # All-UC group must succeed (fixed point ≈ 15.65 each, total ≈ 62.6 > 60)
    all_uc = fill(UC, cfg.group_size)
    @test simulate_group(all_uc, cfg, rng) == true

    # All-FR group must fail (fixed point ≈ 5.26 each, total ≈ 21.1 < 60)
    all_fr = fill(FR, cfg.group_size)
    @test simulate_group(all_fr, cfg, rng) == false
end
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd sim && julia --project=. test/runtests.jl
```

Expected: `UndefVarError: assign_types not defined`

- [ ] **Step 3: Write `sim/src/group.jl`**

```julia
function assign_types(uc_prop::Float64, cfg::SimConfig, rng::AbstractRNG)::Vector{PlayerType}
    cc_prop = (1.0 - uc_prop) * cfg.cc_fr_ratio / (cfg.cc_fr_ratio + 1.0)
    map(1:cfg.group_size) do _
        r = rand(rng)
        if r < uc_prop
            UC
        elseif r < uc_prop + cc_prop
            CC
        else
            FR
        end
    end
end

function simulate_group(types::Vector{PlayerType}, cfg::SimConfig, rng::AbstractRNG)::Bool
    contribs = [cfg.lcp[t].init for t in types]
    for _ in 1:cfg.n_rounds
        prev = copy(contribs)
        for i in 1:cfg.group_size
            others_mean = mean(prev[j] for j in 1:cfg.group_size if j != i)
            contribs[i] = contribution(types[i], others_mean, cfg)
        end
    end
    sum(contribs) >= cfg.threshold
end
```

- [ ] **Step 4: Add include + exports to `sim/src/CoopDisaster.jl`**

```julia
module CoopDisaster
    using Random, Statistics

    include("types.jl")
    include("lcp.jl")
    include("group.jl")

    export PlayerType, UC, CC, FR
    export LcpParams, SimConfig, DEFAULT_CONFIG
    export contribution
    export assign_types, simulate_group
end
```

- [ ] **Step 5: Run tests — expect pass**

```bash
cd sim && julia --project=. test/runtests.jl
```

Expected:
```
Test Summary:                | Pass  Total  Time
CoopDisaster                 |    5      5
LCP contribution             |   10     10
assign_types                 |    4      4
simulate_group convergence   |    2      2
```

- [ ] **Step 6: Commit**

```bash
git add sim/src/group.jl sim/src/CoopDisaster.jl sim/test/runtests.jl
git commit -m "feat: add group simulation with type assignment"
```

---

## Task 4: Parameter sweep

**Files:**
- Create: `sim/src/sweep.jl`
- Modify: `sim/src/CoopDisaster.jl` (add include + export)
- Modify: `sim/test/runtests.jl` (add sweep tests)

- [ ] **Step 1: Write the failing tests**

Add to `sim/test/runtests.jl`:

```julia
@testset "run_sweep" begin
    # Small config for speed: 100 groups, 200 rounds
    test_cfg = SimConfig(
        100, 200, 4, 20.0, 60.0, 215.0 / 21.0, DEFAULT_CONFIG.lcp
    )

    # All free-riders → no group should succeed
    results_zero = run_sweep([0.0], test_cfg)
    @test length(results_zero) == 1
    @test results_zero[1] == 0.0

    # All unconditional cooperators → nearly all groups succeed
    results_one = run_sweep([1.0], test_cfg)
    @test length(results_one) == 1
    @test results_one[1] > 0.9

    # Sweep returns one value per input proportion
    props = collect(0.0:0.1:1.0)
    results = run_sweep(props, test_cfg)
    @test length(results) == length(props)

    # Monotonically non-decreasing (more UC → more success, in expectation)
    # Use wide tolerances due to stochasticity; just check endpoints
    @test results[1] < results[end]
end
```

- [ ] **Step 2: Run tests — expect failure**

```bash
cd sim && julia --project=. test/runtests.jl
```

Expected: `UndefVarError: run_sweep not defined`

- [ ] **Step 3: Write `sim/src/sweep.jl`**

```julia
function run_sweep(uc_props, cfg::SimConfig)::Vector{Float64}
    success_rates = zeros(length(uc_props))
    Threads.@threads for idx in eachindex(uc_props)
        rng = Random.default_rng()   # thread-local in Julia 1.7+
        uc  = uc_props[idx]
        n_success = 0
        for _ in 1:cfg.n_groups
            types = assign_types(uc, cfg, rng)
            n_success += simulate_group(types, cfg, rng)
        end
        success_rates[idx] = n_success / cfg.n_groups
    end
    success_rates
end
```

- [ ] **Step 4: Add include + export to `sim/src/CoopDisaster.jl`**

```julia
module CoopDisaster
    using Random, Statistics

    include("types.jl")
    include("lcp.jl")
    include("group.jl")
    include("sweep.jl")

    export PlayerType, UC, CC, FR
    export LcpParams, SimConfig, DEFAULT_CONFIG
    export contribution
    export assign_types, simulate_group
    export run_sweep
end
```

- [ ] **Step 5: Run all tests — expect pass**

```bash
cd sim && julia --project=. --threads=auto test/runtests.jl
```

Expected:
```
Test Summary:                | Pass  Total  Time
CoopDisaster                 |    5      5
LCP contribution             |   10     10
assign_types                 |    4      4
simulate_group convergence   |    2      2
run_sweep                    |    4      4
```

- [ ] **Step 6: Commit**

```bash
git add sim/src/sweep.jl sim/src/CoopDisaster.jl sim/test/runtests.jl
git commit -m "feat: add threaded parameter sweep"
```

---

## Task 5: Entry point script + output figure

**Files:**
- Modify: `sim/scripts/fig7.jl` (full implementation, replacing stub)

- [ ] **Step 1: Write `sim/scripts/fig7.jl`**

```julia
include("../src/CoopDisaster.jl")
using .CoopDisaster
using Plots, Printf

cfg = DEFAULT_CONFIG
uc_props = collect(0.0:0.01:1.0)

println("Running Fig 7 simulation...")
println("  Groups: $(cfg.n_groups)  |  Rounds: $(cfg.n_rounds)  |  Threads: $(Threads.nthreads())")

elapsed = @elapsed success_rates = run_sweep(uc_props, cfg)
@printf("  Done in %.2f seconds\n\n", elapsed)

println("UC prop | Success rate")
println("--------|-------------")
for idx in 1:10:length(uc_props)
    @printf("  %.2f  |   %.3f\n", uc_props[idx], success_rates[idx])
end

plt = plot(
    uc_props, success_rates;
    xlabel = "Proportion unconditional cooperators",
    ylabel = "Proportion successful groups",
    title  = "Fig 7 — Cooperation in the face of disaster",
    label  = "Simulation",
    lw     = 2,
    color  = :steelblue,
    ylims  = (0.0, 1.05),
    xlims  = (0.0, 1.0),
    size   = (700, 500),
    legend = :topleft,
)
vline!(plt, [0.56];
    label  = "Empirical UC proportion (0.56)",
    color  = :black,
    lw     = 1.5,
    ls     = :dash,
)

outpath = joinpath(@__DIR__, "..", "fig7.png")
savefig(plt, outpath)
println("\nPlot saved to sim/fig7.png")
```

- [ ] **Step 2: Run the script**

```bash
cd sim && julia --project=. --threads=auto scripts/fig7.jl
```

Expected output (values approximate — stochastic):
```
Running Fig 7 simulation...
  Groups: 1000  |  Rounds: 200  |  Threads: 8
  Done in X.XX seconds

UC prop | Success rate
--------|-------------
  0.00  |   0.000
  0.10  |   0.000
  0.20  |   0.000
  0.30  |   0.000
  0.40  |   0.000
  0.50  |   0.005   ← starts rising near empirical UC=0.56
  0.60  |   0.100
  0.70  |   0.400
  0.80  |   0.800
  0.90  |   0.980
  1.00  |   1.000

Plot saved to sim/fig7.png
```

- [ ] **Step 3: Verify the plot**

Open `sim/fig7.png`. Check:
- x-axis: 0 to 1 (UC proportion)
- y-axis: 0 to 1 (success rate)
- Curve is near-zero below UC ≈ 0.5, then rises nonlinearly to 1.0
- Vertical dashed line at x = 0.56

If the curve is flat zero everywhere, the LCP parameters are still off — revisit `DEFAULT_CONFIG` in `types.jl` and ensure `α/(1−β) > 15` for UC.

- [ ] **Step 4: Commit**

```bash
git add sim/scripts/fig7.jl sim/fig7.png
git commit -m "feat: add Fig 7 entry point script, reproduce cooperation curve"
```

---

## Self-Review

**Spec coverage:**
- ✅ 1000 groups × 200 rounds × sweep 0→1 → Task 4 + 5
- ✅ CC:FR ratio 10.2 → `DEFAULT_CONFIG.cc_fr_ratio`
- ✅ Threshold 60, group size 4 → `DEFAULT_CONFIG`
- ✅ LCP calibration fix (fixed-point constraint) → Task 1 `types.jl` comment + Task 3 test
- ✅ No globals → `SimConfig` passed everywhere
- ✅ Threaded sweep → Task 4 `Threads.@threads`
- ✅ Plots.jl output with empirical vertical line → Task 5
- ✅ Old buggy file deleted → Task 1

**Placeholder scan:** Clean — all steps have exact code, commands, and expected output.

**Type consistency:**
- `contribution(type, others_mean, cfg)` used in Task 2 (defined), Task 3 (used in `simulate_group`) ✅
- `assign_types(uc_prop, cfg, rng)` defined Task 3, used in Task 4 (`run_sweep`) ✅
- `simulate_group(types, cfg, rng)` defined Task 3, used in Task 4 ✅
- `DEFAULT_CONFIG` defined Task 1, used in Tasks 2–5 ✅
