include("../src/CoopDisaster.jl")
using .CoopDisaster
using Test
using Random

@testset "CoopDisaster" begin
    @test DEFAULT_CONFIG.n_groups == 1_000
    @test DEFAULT_CONFIG.group_size == 4
    @test DEFAULT_CONFIG.threshold == 60.0
    @test haskey(DEFAULT_CONFIG.lcp, UC)
    @test haskey(DEFAULT_CONFIG.lcp, CC)
    @test haskey(DEFAULT_CONFIG.lcp, FR)
end

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
    @test contribution(CC, 1000.0, cfg) == cfg.endowment   # upper clamp (CC has positive β)
    @test contribution(FR, -1000.0, cfg) == 0.0            # lower clamp
end

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

    # Monotonically non-decreasing endpoint check
    @test results[1] < results[end]
end
