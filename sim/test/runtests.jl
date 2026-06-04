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
