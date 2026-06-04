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
