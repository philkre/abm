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
