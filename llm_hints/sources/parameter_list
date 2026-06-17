# Full Parameter List

*Every parameter in the spatial collective-risk flood model. For each: symbol, role, recommended value or range with source, and whether to fix it or include it in the sensitivity analysis (SA), with the reason. Calibration provenance is in `from_ding_to_our_model.md` §A; the model uses these symbols as defined in `Final Model Specification.md`. Citations use the handoff reference list. The lattice-size question (Q9) is resolved in the last section.*

*Symbol note: `g` is the wealth growth rate (Kolen); the per-cooperator contribution level is `c̄` (the source file's §4 reused `g` for both, which is the clash this resolves).*

---

## 1. Structural parameters (fixed by design)

| Symbol | Role | Value | Fix / SA | Reason and source |
|---|---|---|---|---|
| `L` | Lattice side | dev 50, headline ≥150, finite-size 200 | special — see §6 | The cooperative phase dies at `L ≤ 150` (Philipp's Ding PR), so a too-small lattice is a validity threat, not just a speed choice. Ding uses 200. |
| — | Neighbourhood | von Neumann (4) | fixed | Matches Ding; defines `|G_i| = 5`. |
| `|G_i|` | Focal-group size | 5 | fixed (derived) | Self + 4 neighbours. Jonsson groups are 4; ours is 5 by the lattice geometry. |
| — | Boundary | torus (periodic) | fixed | Removes edge effects; Ding, Santos. |
| — | Update scheme | synchronous | fixed (Q1) | The threshold/flood snapshot must be well-defined; vectorises for SALib. |
| `μ` | Mutation rate | 0.01 | fixed | Keeps strategies from absorbing; standard (Santos & Pacheco 2011). |

---

## 2. Game and economic parameters

| Symbol | Role | Value / range | Fix / SA | Reason and source |
|---|---|---|---|---|
| `c̄` | Cooperator contribution (UC's effort, CC cap) | `0.75 E` | fixed (derived from `T`) | Calibrated so a full-cooperator group of 5 exactly clears `T`; ties to Jonsson's 75% rule. |
| `T` | Threshold (pool needed for safety) | `0.75 × (5E) = 3.75 E` | via `T/E` in SA | Jonsson's 75%-of-endowment rule; Santos shows stringency drives cooperation. |
| `T / E` | Threshold ratio (the dimensionless knob) | sweep `[0.4, 0.9]` | **SA (linear phase; sigmoid-phase candidate)** | The most game-defining structural knob: how hard it is to be safe (Santos & Pacheco 2011). |
| `E` | Flat per-round income | Jonsson endowment scale (set `E = 1` as the unit) | fixed | Validation income; also the unit that `c̄, T, w₀` are expressed in. |
| `g` | Wealth growth rate (multiplicative) | `0.015` /round | fixed | Regional ≈ national property appreciation (Kolen 2025, `V_t = V_0(1+g)^t`). |
| `w₀` | Initial wealth | `≈ E` (one round's income) | fixed | Avoids a degenerate start; sensitivity is weak once `κ` discounts history. |
| `R` | Public-good multiplier | `0` (main); `> 0` for Jonsson validation only | fixed (mode switch) | Pure cost in the flood model (Q2); the multiplier exists in code, off by default, on for the well-mixed match. |

---

## 3. Risk parameters

| Symbol | Role | Value / range | Fix / SA | Reason and source |
|---|---|---|---|---|
| `p_max` | Maximum flood probability | sweep `[0, 1]` (linear); fixed `1.0` (sigmoid) | **SA (linear phase)**; fixed (sigmoid) | The core stochastic-risk knob; Jonsson shows cooperation responds to it, Santos shows risk rescues cooperation. In the sigmoid phase the shape parameters replace it. |
| `k` | Sigmoid steepness | sweep, anchored by the ×10-per-0.5 m decimation rule | **SA (sigmoid phase)** | How sharp the defence tipping point is. Calibrated by Kolen's decimation height (2025). |
| `e_0` | Sigmoid midpoint | sweep across `[−1, 1]` | **SA (sigmoid phase)** | Where defences start to fail. No fixed empirical value; the knob of interest. |
| `ℓ` | Loss fraction per flood | `0.34` (fixed in sigmoid phase); sweep `(0, 1]` in linear phase | **SA (linear phase)**; fixed `0.34` (sigmoid) | Disaster severity (Jonsson's impact dimension). `0.34 = f₁ f₂ = 0.9 × 0.38` for a ~2 m flood (Kolen 2025, SSM2023). |
| `p_min` | Baseline probability floor (optional) | `0`, or `1/3000` for calibrated Dutch runs | fixed | Realistic residual risk even with good defences; the Dutch safety standard (Kolen 2025). Off by default. |

---

## 4. Environment and feedback parameters

These set the slow dynamics. Per the brief and Debraj's guidance, study them in **targeted sweeps** rather than spending Sobol axes on them (the four-parameter SA budget is reserved for the knobs in §3 plus `β`).

| Symbol | Role | Value / range | Fix / SA | Reason and source |
|---|---|---|---|---|
| `δ` | Environment improvement rate (per maintainer) | `≈ 0.03` (range `0.02–0.04`) | targeted sweep | Ding's phase-diagram range; `epgg` recovers full cooperation at `δ ≈ 0.02–0.025`. |
| `γ` | Environment degradation rate (per defector) | `≈ 0.03` (`epgg` Fig 3 uses `0.04`) | targeted sweep | Ding (2024) range; sets the cooperator/defector tension. |
| `η` | Flood-damage rate on defences (A+ term) | tune; `0` for MVP, `> 0` for headline | targeted sweep | New, the resilience-erosion channel. Anchor by the decimation-height logic (Kolen 2025). |
| `τ` | Feedback update interval | `1` generation | targeted sweep | Ding/Weitz timescale; sets any oscillation period. Weitz (2016) shows the qualitative outcome is robust to it, but the period is not. |
| `κ` | Fitness discount | `0.1–0.3` | fix `≈ 0.2`, sweep if needed | New; balances recency against lifetime wealth and damps heavy-tailed-wealth imitation artefacts. |
| `α`, `θ` | Weitz logistic feedback speed, enhancement ratio | only for wiring C | fixed per oscillation run | Used only for the literal-Weitz oscillation-bridge runs, not the A+ headline model (Weitz 2016). |

---

## 5. Imitation, loss aversion, and run control

| Symbol | Role | Value / range | Fix / SA | Reason and source |
|---|---|---|---|---|
| `β` | Fermi selection strength (`= 1/K`) | sweep `[0.1, 10]` | **SA — always in (priority)** | Flagged by both Luka and Debraj; controls determinism of imitation and interacts with finite size to cause spurious fixation (Szolnoki 2009). Brackets Ding's `β = 2` and Santos's `β = 5`. |
| `λ_i` | Loss aversion (per household) | `1` (risk-neutral baseline) → `λ̄ ≈ 2.25` homogeneous → heterogeneous draw, log-normal or uniform `[1, λ_max]`, mean `2.25` | staged, not in Sobol | Decision-layer only (Q7a); enters CC's contribution, never the physical wealth update. Mean from Kahneman & Tversky (1979). Sanity-check homogeneous before heterogeneous. |
| — | Initial strategy mix | MVP: 50/50 UC/D; headline: equal thirds UC/CC/D | fixed (robustness check) | Confirm results are not initial-condition artefacts by testing a second mix. |
| — | Replications (seeds) | `≈ 50` per parameter point | fixed | Stochastic model; report distributions. Record every seed. |
| — | Generations | `≈ 1500`, measure over the final `~200` | fixed | Burn-in then a stationary measurement window (reading guide §8.6). Gate the phase detector behind a minimum-generation count so it does not fire in the early defector low. |

---

## 6. Lattice size — resolving the L = 50 vs L = 200 tension (Q9)

The compute cost scales with the cell count `L²`: `L = 50 → 2500` cells, `L = 150 → 22 500`, `L = 200 → 40 000`. So `L = 200` is roughly 16× the work of `L = 50` per generation, and a full Sobol sample times 50 replications multiplies that again.

Against that sits the hard finding from Philipp's Ding reproduction: **the cooperative phase does not exist at `L ≤ 150`** — cooperator clusters die in the early defector bottleneck on small lattices. Running headline results or the SA at `L = 50` would therefore suppress the very phenomena the project is about, and could report a finite-size artefact (a phase the lattice is too small to support) as a result.

**Resolution (per the Q9 answer):**

- **Develop and debug at `L = 50`.** Fast iteration, cheap on a laptop, fine for checking that the pipeline runs and the bookkeeping closes.
- **Run headline results at `L ≥ 150`**, where Ding's cooperative phase and transitions actually exist. This is the size for the figures that go in the report.
- **Finite-size check at `L = 200`** on a reduced parameter set, to confirm the headline regime is stable and not an artefact of the chosen size.
- **Sensitivity analysis:** run the full Sobol sample at the smallest size that still supports the cooperative phase (target `L = 150`), and repeat a reduced sample at `L = 200` to confirm the index rankings are size-stable. If `β` does not rank highly, re-check at `L = 200` first, since finite-size and `β` interact (Szolnoki 2009).
- **Compute split:** the `L ≥ 150` sweeps will likely need SURF Snellius; keep an `L = 50` laptop path for development and for when Snellius credits run low. The coding deliverable should make this split explicit.

---

## 7. Sensitivity-analysis sets (max 4 parameters)

Method: Sobol first-order and total-effect indices (Saltelli 2008), via SALib. Primary output: resilience (fraction of focal groups clearing the threshold over the final window). Secondary: long-run cooperation rate, mean wealth, clustering (Moran's I).

- **Linear phase (start here):** `{ β, p_max, T/E, ℓ }`.
- **Sigmoid phase:** `{ β, k, e_0, ? }`, with `p_max` and `ℓ` fixed. The fourth axis (Q8) is **deferred**; the candidates are `T/E` (how often risk is triggered, the operating-regime knob) or `ℓ` (disaster severity). Recommendation when you decide: `T/E`, fixing `ℓ = 0.34`, because the threshold ratio governs the regime while `ℓ` only scales the consequence. Swap to `ℓ` if severity proves the more interesting axis.

`β` is in both sets and is the priority parameter. The feedback parameters (`δ, γ, η, τ, κ`) are studied in separate targeted sweeps rather than spending Sobol axes on them.
