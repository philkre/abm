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

# Empirical LCP parameters: averages across 4 treatments (10P, 40P, Level, Impact)
# from fig6.py in github.com/markusrobertjonsson/condcoop (ref [53] in paper).
# Fixed-point x = α/(1−β) for homogeneous group; success if 4x ≥ threshold 60.
# UC: x ≈ 17.13, group ≈ 68.5 ✓ | CC: x ≈ 6.06, group ≈ 24.3 | FR: x ≈ 4.74, group ≈ 19.0
# cc_fr_ratio = 10.2 per paper (CC:0.358, FR:0.035 → 0.358/0.035 ≈ 10.2)
const DEFAULT_CONFIG = SimConfig(
    1_000,
    200,
    4,
    20.0,
    60.0,
    10.2,
    Dict(
        UC => LcpParams(14.839736, 17.599818, -0.027274),
        CC => LcpParams(11.947847,  0.815997,  0.865409),
        FR => LcpParams( 9.678571,  4.099742,  0.134343),
    )
)
