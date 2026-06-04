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
