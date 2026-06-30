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
