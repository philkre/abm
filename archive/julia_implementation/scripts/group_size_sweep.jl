include("../src/CoopDisaster.jl")
using .CoopDisaster
using Plots, Printf

# Threshold scales with group_size: 75% of max (60/80 from paper's 4-player game)
THRESHOLD_PER_PLAYER = 60.0 / 4.0 * 0.75 * 4  # = 15 per player
make_config(gs) = SimConfig(
    500,           # n_groups (fewer to keep runtime reasonable for large groups)
    200,
    gs,
    20.0,
    15.0 * gs,     # scaled threshold: 75% of max group contribution
    10.2,
    DEFAULT_CONFIG.lcp,
)

GROUP_SIZES = [4, 25, 100, 500]
uc_props = collect(0.0:0.01:1.0)

plt = plot(
    xlabel = "Proportion unconditional cooperators",
    ylabel = "Proportion successful groups",
    title  = "Effect of group size on cooperation",
    legend = :topleft,
    ylims  = (0.0, 1.05),
    xlims  = (0.0, 1.0),
    size   = (700, 500),
)

for gs in GROUP_SIZES
    cfg = make_config(gs)
    println("Running group_size=$gs (threshold=$(Int(cfg.threshold)))...")
    elapsed = @elapsed rates = run_sweep(uc_props, cfg)
    @printf("  Done in %.2f seconds\n", elapsed)
    plot!(plt, uc_props, rates; label="n=$gs", lw=2)
end

vline!(plt, [0.56]; label="Empirical UC (0.56)", color=:black, lw=1.5, ls=:dash)

outpath = joinpath(@__DIR__, "..", "group_size_sweep.png")
savefig(plt, outpath)
println("\nPlot saved to sim/group_size_sweep.png")
