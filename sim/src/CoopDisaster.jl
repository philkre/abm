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
