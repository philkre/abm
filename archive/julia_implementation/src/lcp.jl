function contribution(type::PlayerType, others_mean::Float64, cfg::SimConfig)::Float64
    p = cfg.lcp[type]
    clamp(p.α + p.β * others_mean, 0.0, cfg.endowment)
end
