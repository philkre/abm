function assign_types(uc_prop::Float64, cfg::SimConfig, rng::AbstractRNG)::Vector{PlayerType}
    cc_prop = (1.0 - uc_prop) * cfg.cc_fr_ratio / (cfg.cc_fr_ratio + 1.0)
    map(1:cfg.group_size) do _
        r = rand(rng)
        if r < uc_prop
            UC
        elseif r < uc_prop + cc_prop
            CC
        else
            FR
        end
    end
end

function simulate_group(types::Vector{PlayerType}, cfg::SimConfig, ::AbstractRNG)::Bool
    # rng unused: LCP dynamics are deterministic; kept for uniform API with run_sweep
    contribs = [cfg.lcp[t].init for t in types]
    for _ in 1:cfg.n_rounds
        prev = copy(contribs)
        for i in 1:cfg.group_size
            others_mean = mean(prev[j] for j in 1:cfg.group_size if j != i)
            contribs[i] = contribution(types[i], others_mean, cfg)
        end
    end
    sum(contribs) >= cfg.threshold
end
