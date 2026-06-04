module CoopDisaster
    using Random, Statistics

    include("types.jl")
    include("lcp.jl")

    # Remaining files added in later tasks
    export PlayerType, UC, CC, FR
    export LcpParams, SimConfig, DEFAULT_CONFIG
    export contribution
end
