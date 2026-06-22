# Flood-Faithfulness and Validation Recommendations

*Companion to `from_ding_to_our_model.md` (decisions and equations) and the two reading guides. This document covers four things: (1) data sources that make the flood interpretation more truthful, with the Jonsson experiment locations mapped onto real flood risk; (2) which backbone formulas are most natural under the flood reading; (3) a validation plan using the Klügl (2008) process, made specific to flooding and covering structural, replicative, and predictive validity; (4) how to represent the flood defences more concretely. Section references like "§7.7" point into the model file.*

---

## 1. Making the flood interpretation more truthful: data

### 1.1 Can the Jonsson experiment locations be tied to real flood risk?

The Jonsson & Jonsson lab experiment ran with 884 participants in **Sweden and the Philippines**. Those sites were chosen for a behavioural reason (a cross-cultural check on whether disaster risk lifts cooperation in both a high-trust European setting and a lower-trust, higher-exposure one), not because the authors modelled either country's flood hazard. So the locations do not come with a flood model attached. But they sit at opposite ends of a real risk gradient, and that is usable.

- **Philippines.** Lower-middle-income, South-East Asian, among the most flood- and typhoon-exposed countries on earth. High baseline disaster probability, weak and uneven defences, a steep loss-aversion gradient (poor households cannot absorb a loss). This is the high-`p_max`, low-baseline-protection corner of our parameter space, and the one you are most interested in.
- **Sweden.** High-income, strong institutions, low river-flood exposure outside specific catchments. Low baseline probability, well-maintained defences, shallow loss-aversion gradient. The low-risk anchor.
- **Netherlands (via Kolen).** The engineered extreme: a 1/3000-per-year defended standard, the strongest flood protection in the world. The contrast Kolen lets us calibrate directly.

The point: the two experiment countries already give a low-risk / high-risk pair, and the Netherlands extends it to a third, engineered extreme. That maps cleanly onto our risk knob (`p_max` in the linear phase, the sigmoid midpoint `e_0` in the sigmoid phase) and onto the loss-aversion distribution. It turns "Sweden vs the Philippines" from a footnote in Jonsson into a designed cross-country experiment for our model (§1.4).

### 1.2 Concrete data sources

Grouped by role. None of these is an ABM to reproduce; they supply calibration, initial fields, and validation targets.

**Cross-country, comparable (the backbone for any contrast).**

- **WRI Aqueduct Floods** (Global Flood Analyzer, hazard maps, country rankings). Open, free, global. River and coastal flood inundation at nine return periods from the 2-year to the 1000-year flood, plus urban damage, affected GDP, and affected population by country, basin, and state. Crucially for us, Aqueduct assigns a country-wide protection level by income: roughly 10-year protection for low-income, 25-year for lower-middle, 50-year for upper-middle, 100-year for high-income, and 1000-year specifically for the Netherlands. That single table gives us a defensible baseline-probability and a protection-standard contrast across exactly our three settings. It also offers 2030/2050/2080 projections under RCP4.5 and RCP8.5, which feed the predictive test in §3.3. The country ranking (about 21 million people affected by river floods per year, with the most-exposed list dominated by South and South-East Asia) is good framing for the SE-Asia focus.
- **Fathom Global Flood Hazard** (e.g. the Manila packages on OasisHub). Return periods from 5 to 1000 years, fluvial and pluvial, at ~90 m. Notable: Fathom simulates flood **defences dynamically** from economic indicators, so it distinguishes defended from undefended hazard. That defended/undefended gap is a direct empirical handle on what our environment scalar `e_i` is supposed to encode.

**Philippines, national (for the SE-Asia case study).**

- **Project NOAH** (UP NIGS / DOST), open under ODbL. Flood inundation maps at 5-, 25-, and 100-year rainfall return periods for all 81 provinces, simulated with Flo-2D over LiDAR terrain for the 18 major river basins. This is the best open national hazard layer, and a real raster we could seed `e_i(0)` from (§4f).
- **Phil-LiDAR / LiPAD portal.** LiDAR DEMs, DTMs, and flood hazard maps, GIS-ready and open. The terrain layer behind NOAH.
- **HazardHunterPH / GeoRisk PH** and **DOST-ASTI** Sentinel-1 SAR flood-impact maps. Operational, near-real-time observed flooding, useful as a reality check on simulated flood footprints.
- **PAGASA** for the meteorological/return-period side.

**Historical event record (for replicative validation of frequency and loss).**

- **EM-DAT** (CRED, Louvain): the international disaster database, dates, deaths, and economic losses per flood event per country. The standard source for "how often, how bad."
- **DesInventar / Sendai Framework Monitor** for sub-national, municipality-level loss records (the Philippines has good DesInventar coverage). This is the layer that matches our cell-level disaster frequency.
- **HDX / UN-OCHA** Philippines flood datasets for humanitarian-grade event and exposure data.

**Netherlands and Sweden (the two European anchors).**

- **Netherlands:** Kolen (2025), already our calibration source; plus Deltares / LIWO (Landelijk Informatiesysteem Water en Overstromingen) and PBL for hazard and the 1/3000 standard, and the EU Floods Directive risk maps.
- **Sweden:** MSB (Myndigheten för samhällsskydd och beredskap) flood-hazard mapping under the EU Floods Directive, and SMHI for hydrology. The low-river-flood-exposure anchor.

### 1.3 How the data maps onto our parameters

| Model quantity | Source |
|---|---|
| Baseline defended probability (the `p_min` floor, or sigmoid healthy tail) | Aqueduct income-protection table (25-yr PH, 1000-yr NL); Kolen 1/3000; NOAH return periods |
| `p_max` (undefended, degraded `e_i`) | Fathom / Aqueduct **undefended** return-period probability; NOAH 5-year layer |
| Loss fraction `ℓ` and any depth-dependence (`f_3`) | Kolen depth-damage (`ℓ ≈ 0.34` for ~2 m); Aqueduct urban-damage / GDP-affected curves |
| Sigmoid shape `k`, `e_0` | Kolen decimation-height (×10 per 0.5 m); the defended-vs-undefended hazard gap |
| Initial environment field `e_i(0)` (geographic heterogeneity) | NOAH / Fathom / Aqueduct hazard raster, resampled to the lattice |
| Disaster frequency and damage distribution (validation targets) | EM-DAT, DesInventar, Aqueduct country/basin estimates |
| Climate-scenario stress test | Aqueduct 2030/2050/2080, RCP4.5/8.5 |

### 1.4 The cross-country contrast as a designed experiment

Run the same model at three calibrated parameter points and compare emergent resilience:

- **"Philippines" point:** high `p_max`, weak baseline protection (~25-year), frequent shocks, strong loss-aversion gradient (poorer households more loss-averse).
- **"Netherlands" point:** very low baseline probability (1/3000), rare but severe shocks, strong institutions (high maintenance rate `δ`), shallow loss-aversion gradient.
- **"Sweden" point:** low river-flood exposure, moderate everything, the European low-risk control.

This is not predictive forecasting. It is an illustrative, replicative contrast: does UC dominance survive locally in a high-frequency regime the way it does in a rare-disaster one? It also gives Debraj's conference a clean narrative line (the same mechanism, three real risk regimes, one of them his own SE-Asia / informal-settlement focus), and it uses real, citable calibration rather than invented numbers.

---

## 2. Which backbone formulas are most natural under the flood reading

Going through the model file's choices and rating each for flood faithfulness. The recommendation column is what to use in the headline ("flood-truthful") runs; the placeholder column is the simpler MVP form.

**Environment `e_i` as flood-defence integrity (§6).** The cleanest mapping in the model. `e_i` is the slow protective stock: drainage condition, embankment and dyke upkeep, wetland and mangrove health, soil absorption. High `e_i` is well-maintained defence and low baseline risk; low `e_i` is clogged drains and eroded banks. Keep as is. The two-timescale split (acute per-round contribution = sandbagging this storm; chronic `e_i` = year-round maintenance) is what stops cooperation being double-counted, and it is physically true of real flood defence.

**Disaster probability from the environment (§5, §7.8).** The **sigmoid** is the natural flood form. Real defences hold risk near zero until they degrade past a design point, then risk climbs sharply: a tipping point, not a gentle slope. Kolen's decimation-height rule (each 0.5 m of lost defence multiplies flood probability by about 10, a geometric rise that has to saturate at 1) is exactly a sigmoid, and it calibrates the steepness `k`. Use linear as the MVP placeholder only; move to sigmoid for the truthful runs.

**Full immunity at the threshold vs smooth risk (§7.4).** This is the one place where Jonsson-faithfulness and flood-faithfulness pull apart. Full immunity (clearing `T` gives `d_i = 0`) matches Jonsson and Santos and is needed for validation. But it is *less* flood-truthful: a defended area still carries residual risk, and Kolen's risk function `R = C·P·(1 + f_3 Z/H_D)` has no hard cutoff. So use **full immunity for the Jonsson validation runs, and keep the smooth-risk variant as the flood-faithful robustness check**, where meeting the threshold lowers but does not zero the probability. Be explicit in the report that the smooth version is the more truthful one and the hard threshold is the price of comparability.

**Pure cost vs multiplied public good (§7.3).** **Pure cost** is the faithful flood reading: money spent on a levee is gone, and the only return is avoiding the flood. Switch the multiplier on only for (a) the well-mixed Jonsson validation run, where the productive return is needed for a quantitative match, and (b) the nature-based-solutions variant, where defences also create amenity value (Mutlu–Roy–Filatova's ~15% price premium is the magnitude). Recommended as in the file.

**Income (§7.5).** **Multiplicative growth** `w_i ← w_i(1+g)`, `g ≈ 0.015`/yr. In the flood frame wealth is property value, which compounds (Kolen `V_t = V_0(1+g)^t`), and a flood loss is a fraction of a growing asset, which is what makes loss aversion bite. Keep flat income only for the Jonsson validation.

**What a flood does (§7.9).** **Fractional wealth loss** (`ℓ ≈ 0.34` for a ~2 m flood) **plus the A+ defence-damage term** (`−η d_i` on `e_i`). The fractional loss is calibrated and scales with the asset; the defence-damage term is the literal "a flood erodes the defences" mechanism that creates the resilience-erosion spiral. Depth-dependent `ℓ` (Kolen `f_3 = 0.2` per 0.5 m) is the most truthful refinement and a documented extension, not v1.

**Environment wiring (§6, §7.7).** **A+ (composition plus flood damage)** is the most flood-natural: cooperators maintain defences, defectors let them decay, and a flood itself damages them. The `−η d_i` term is the headline mechanism and aligns with the real "floods faster than recovery means no recovery" dynamic Kolen describes (and the decade-long post-tsunami rebuild he cites). Keep plain Ding (A, `η = 0`) as the validated starting point and an ablation. Keep the literal Weitz logistic (C) on the shelf as the direct bridge to the oscillation prediction if a reviewer asks.

**Loss aversion (§7.10).** Option (a), overweighting the expected loss in a conditional cooperator's contribution target, is the most flood-natural: it reads directly as willingness to pay for defence, and it ties to Kolen's risk term `R = p_i ℓ w_i`. It belongs in the decision layer, never the physical wealth update, because the flood removes the same `ℓ w_i` regardless of attitude.

**Summary.**

| Formula / choice | Flood-faithful (headline) | Placeholder (MVP) |
|---|---|---|
| Risk from environment | Sigmoid (Kolen decimation height) | Linear in `p_max` |
| Threshold protection | Smooth residual risk | Full immunity (matches Jonsson) |
| Contribution return | Pure cost | + multiplier for validation / NbS |
| Income | Multiplicative `(1+g)` | Flat `E` (validation) |
| Flood event | `ℓ`-loss + `−η d_i` (A+) | `ℓ`-loss only (A) |
| Loss aversion | Overweight expected loss in CC target | Homogeneous `λ`, then off |

---

## 3. Validation plan, using the Klügl process

Klügl (2008) frames validity along two dimensions. **Method:** *face (facial) validity* (human judgement of output and design: structured walkthrough, expert assessment, animation, plausibility checking) versus *empirical validity* (direct statistical comparison against the real system or another model). **Element:** *structural validity* (the internal causal mechanism) versus *behaviour validity* (input-output as a grey box), where behaviour splits into *replicative* (can we distinguish model from system under the experimental frame?) and *predictive* (replicative, plus predicting as-yet-unseen input-output). The three validity types the brief asks for sit inside this grid: structural is the element dimension, replicative and predictive are the behaviour sub-types. Below, each is made concrete for flooding.

### 3.1 Structural validity

Does the model's inner workings reflect the real flood system step by step? This is where the flood interpretation earns its keep over an abstract TPGG: every component has a named real-world referent, so we can actually ask whether the causal chain is right.

- **Causal-loop walkthrough** of the ODD+D: contributions maintain defences (`δ`), neglect degrades them (`γ`), a flood erodes them (`−η d_i`), degraded defences raise next season's probability (sigmoid), which makes the next flood more likely. Check each arrow against flood reality.
- **Expert assessment** by Debraj, whose research is flood resilience in informal settlements. The single most efficient structural check available to us.
- **Animation / face validity:** render the lattice over time. Do degraded zones cluster? Do floods cluster spatially even though disaster draws are independent (they should, through shared focal-group pools)? Does a flooded patch visibly slide toward the trap unless maintenance recovers it?
- **Plausibility checks:** monotonicity (more maintenance lowers risk; higher `p_max` lowers resilience), and conservation (a contribution enters five pools but is paid once; wealth bookkeeping closes).

### 3.2 Replicative validity

Under a fixed experimental frame, can we tell the model apart from a reference? We have **three published-model references plus one real-data reference**, in roughly this order.

1. **The Jonsson well-mixed limit (the blocking dependency).** With the `well_mixed` and `frozen` flags and the multiplier switched on, reproduce **Jonsson & Jonsson Figure 7**. This is replicative validity against a published model-plus-experiment, and it must pass before any spatial claim is credible. Compare the cooperation-vs-round trajectories and the UC/CC/D composition, not single points.
2. **The Ding phase diagram.** In the no-threshold, no-flood limit (`η = 0`, environment back in Ding's payoff-scaling role), recover Ding's discontinuous transitions in the (δ, γ) plane. Philipp's `src/epgg` baseline already passes Ding's Figures 2 and 3, so this check is largely in hand; the task is to confirm it still holds once our threshold-and-flood machinery is switched off cleanly. This guards the claim that we built *on* Ding rather than *near* it.
3. **The Weitz oscillation.** In the mean-field / fast-feedback limit with the literal logistic wiring (option C, §6 of the model file), recover the oscillating tragedy of the commons that Weitz predicts analytically. This is the reference for the secondary question of whether spatial structure stabilises or destabilises those cycles.
4. **Real flood statistics for one locale (e.g. Metro Manila).** Calibrate to that locale (NOAH return periods, Aqueduct protection level, Kolen-style depth-damage) and compare emergent output to data as *distributions*, since the model is stochastic:
   - long-run per-cell flood frequency vs the locale's return-period probability (NOAH / Aqueduct),
   - damage-per-event distribution vs depth-damage and EM-DAT / DesInventar loss records,
   - spatial clustering of flooded and degraded cells (Moran's I) vs the clustering in the real hazard raster.

The experimental frame is the calibrated parameter point; replicative validity is the claim that, within that frame, our output is statistically indistinguishable from the reference on these measures. The first three checks validate the *machinery* against the papers we built from; the fourth validates the *flood instantiation* against the world.

**A finite-size caveat that is really a validity threat.** Philipp's Ding reproduction found that the cooperative phase does not exist at L ≤ 150: cooperator clusters die in the early defector bottleneck on small lattices, and a naive stationarity stop fires during the roughly 150-generation low before recovery and misclassifies a C regime as D. The consequence for validation is sharp. If we run the replicative checks or the sensitivity sweeps at the model file's convenience size of L = 50, we risk reporting a structural artifact (a phase the lattice is too small to support) as a result. So the finite-size check is not optional polish, it is part of establishing structural and replicative validity. Recommendation: run the phase-sensitive validation at **L = 200**, confirm any headline regime is stable across at least two lattice sizes (e.g. L = 100 and L = 200) before trusting it, and gate the phase detector behind a minimum-generation count so it cannot fire in the early defector low. The L = 50 vs L = 200 compute tension this creates (Snellius vs laptop) is for the parameter-list deliverable to resolve, but the validity point stands on its own.

### 3.3 Predictive validity

Predictive validity is replicative validity plus predicting unseen input-output. Be honest in the report: like most ABMs of this kind (El-Farol, civil violence), we do **not** claim strong predictive validity, and Klügl's own caveat applies, a new experimental frame (crisis vs stable conditions) can invalidate a model that replicated fine. Our resilience-erosion regime is exactly such a frame, so over-claiming would be wrong.

What we *can* do is a bounded out-of-sample test:

- Calibrate in one regime (the historical defended baseline), then **predict the direction and qualitative shape** of the response to an unseen change: raise `p_max` or lower the protection level (a climate-stress scenario) and check whether the model predicts the same direction of rising risk and falling resilience as Aqueduct's 2030/2050/2080 RCP4.5/8.5 projections.
- Test the **policy lever**: inject external aid after a failed season and see whether recovery matches the "aid prevents collapse" expectation.
- Test one behavioural prediction directly: Mutlu–Roy–Filatova find flood-risk perception fades within 9–12 years of the last flood. A decaying environmental signal should reproduce that fade as an emergent property, which is an out-of-sample behavioural check rather than a fitted one.

### 3.4 The process, in order

Klügl is a workflow, not just a taxonomy. Run it in this sequence (cheapest and most diagnostic first):

1. **Face validation first:** structured walkthrough, animation, plausibility. Catches gross errors before any expensive run.
2. **Calibration** to the locale (Kolen plus Aqueduct / NOAH). The course's empirical-calibration framings (Windrum's indirect calibration and the Werker–Brenner approach) are the reference here: use known data to pin what you can, leave wide ranges where you cannot, and discard parameter settings that produce implausible output.
3. **Sensitivity analysis** (already planned: Sobol on the four-parameter sets, `β` always in). Klügl treats robustness as part of establishing validity, so the SA is not a separate exercise from validation, it is a stage of it.
4. **Empirical validation:** replicative first (the machinery checks against Jonsson, Ding, and Weitz, then the locale statistics), then the bounded predictive test. Run the phase-sensitive checks at L = 200, not L = 50, and confirm regime stability across lattice sizes.
5. **Iterate** where a stage fails.

Mapping the plan onto Klügl's grid:

| Step | Method | Element |
|---|---|---|
| ODD+D walkthrough, expert review, animation | Face | Structural |
| Plausibility / monotonicity / conservation | Face | Structural + behaviour |
| Jonsson Figure 7 reproduction (well-mixed limit) | Empirical (vs model + experiment) | Replicative |
| Ding phase diagram + Weitz oscillation (machinery limits) | Empirical (vs another model) | Replicative |
| Finite-size stability across L | Empirical | Structural (artifact guard) |
| Locale statistics (frequency, damage, clustering) | Empirical (vs real system) | Replicative |
| Climate / aid / risk-memory tests | Empirical | Predictive (bounded) |

---

## 4. Representing the flood defences more concretely

Right now `e_i` is one abstract scalar. Options to make the defences concrete, ordered from cheap to ambitious.

- **(a) Name the referent, keep the scalar.** Document `e_i` as a composite of drainage condition, embankment height, and wetland health, even if it stays one number. Costs nothing, buys structural credibility in the ODD+D. Do this regardless.
- **(b) Map `e_i` to a protection return period (recommended for the report).** Define a monotone map `e_i → T_p(e_i)` from environment to defence design standard, so the baseline probability is `1/T_p`. This plugs straight into Aqueduct's income-to-protection table (25-year for the Philippines, 1000-year for the Netherlands) and Kolen's 1/3000, and it makes the sigmoid midpoint `e_0` interpretable as "the design standard starts to fail." Every probability in the model becomes a real, citable number. Cheap and high payoff.
- **(c) Split fast and slow stocks explicitly.** Separate the acute per-round contribution (sandbagging) from the slow capital stock (`e_i`). The two-timescale reading already implies this; making it a second state variable would sharpen it, at the cost of one more stock to track.
- **(d) Decimation-height degradation.** Tie the degradation and flood-damage rates (`γ`, `η`) to Kolen's ×10-per-0.5 m rule, so neglect maps to a concrete probability multiplier rather than a free parameter. This is calibration, not new structure.
- **(e) Nature-based vs grey defences.** Use the multiplied-public-good variant for defences that also create amenity value (mangroves, wetlands), calibrated to the ~15% NbS premium in Mutlu–Roy–Filatova. This becomes a policy lever: NbS yields co-benefits and a different feedback signature.
- **(f) Seed a real defence field (the spatial-realism extension).** Initialise `e_i(0)` from a real hazard raster (NOAH, Fathom, or Aqueduct) resampled to the lattice, so defences start heterogeneous and map-grounded rather than uniform. This is the geographic-risk-heterogeneity extension already on the horizon, and it is what turns the "Philippines vs Netherlands" contrast (§1.4) into a spatially explicit one.

**Recommendation:** do (a) and (b) for the headline report (cheap, and they make every probability interpretable and tied to data), calibrate with (d), flag (f) as the spatial-realism extension and (e) as the policy extension.

---

## 5. Recommendations at a glance

- Treat **Sweden / Philippines / Netherlands** as a designed three-point risk contrast, calibrated from Aqueduct, NOAH, and Kolen, not as incidental experiment sites. The Philippines is the SE-Asia case; the Netherlands is the engineered extreme.
- Core data stack: **Aqueduct** (comparable cross-country, income-protection table, climate scenarios), **Project NOAH / Phil-LiDAR** (Philippines hazard rasters, and a real `e_i(0)` field), **EM-DAT / DesInventar** (frequency and loss for validation), **Kolen / Deltares / MSB** (the two European anchors).
- Most flood-natural backbone: **sigmoid risk, pure cost, multiplicative income, A+ feedback, fractional loss plus defence damage, loss aversion as overweighted expected loss.** Keep the Jonsson-matching forms (full immunity, multiplier, flat income) only for the well-mixed validation run.
- Validation in Klügl order: **face first** (walkthrough, animation, Debraj's expert review), **calibrate**, **SA**, then **empirical**. Replicative validity has four targets, not one: the machinery against **Jonsson Figure 7, the Ding phase diagram, and the Weitz oscillation**, then the flood instantiation against **Manila statistics**. Then a **bounded predictive** test against Aqueduct climate scenarios and the Mutlu–Roy–Filatova risk-memory fade. Do not over-claim predictive validity.
- **Run phase-sensitive validation and sweeps at L = 200, not L = 50.** The cooperative phase dies on small lattices, so a too-small grid can misclassify a C regime as defection and report a finite-size artifact as a result. This is a validity threat, not just a compute choice.
- Make defences concrete cheaply by **mapping `e_i` to a protection return period**, and seed a **real hazard raster** as the spatial-realism extension.

---

---

## 6. Geopolitical case study: treaty participation and the conflict trap

The model's core dynamics — threshold collective action, an environment that records the accumulated state of cooperation, and a disaster that damages the very conditions for future cooperation — map cleanly onto international security politics. This section describes that interpretation as a second case study, using the same equations with a different semantic layer. Networked (non-lattice) topology is flagged as future work throughout; the lattice is used here as a first approximation.

### 6.1 Semantic mapping

Every state variable and parameter acquires a geopolitical referent with minimal reinterpretation.

| Model quantity | Geopolitical referent |
|---|---|
| Agent `i` | Nation-state (or regional actor) |
| Lattice adjacency | Geographic neighbourhood / shared border region (lattice as MVP; alliance network for future work) |
| Strategy UC | Unconditional treaty adherent — always fulfills obligations regardless of what neighbours do |
| Strategy D | Free-rider / norm violator — enjoys collective security without contributing |
| Strategy CC | Conditional participant — tit-for-tat diplomat, contributes in proportion to what neighbours contribute |
| Contribution `c_i` | Defense spending, diplomatic effort, compliance with treaty obligations (e.g. 2% GDP NATO target) |
| Pool `P_i`, threshold `T` | Collective security quorum — enough combined commitment to deter conflict or sustain a security regime |
| Environment `e_i ∈ [−1,1]` | Regional security environment: institutional trust, norm robustness, alliance cohesion. High `e_i` = stable, low tension; low `e_i` = eroded norms, high hostility |
| Flood probability `p_i` | Conflict outbreak probability — driven by how degraded the security environment is |
| Flood event `d_i` | War or armed conflict occurring — the discrete disaster |
| Wealth `w_i` | Economic and political capital of the state |
| Wealth growth `(1+g)` | Peacetime economic growth compounding on stability |
| Flood loss `ℓ w_i` | War costs: GDP destruction, political instability, refugee flows, reconstruction burden |
| Maintenance rate `δ` | Diplomatic effort, institution-building, treaty compliance raising `e_i` |
| Neglect rate `γ` | Norm erosion from free-riding, arms build-up, or treaty withdrawal |
| Flood damage to defences `η` | Conflict damages the institutions that prevent the next conflict — war destroys trust, collapses agreements, creates grievances |
| Loss aversion `λ_i` | War-memory effect: states that recently experienced conflict are more willing to invest in security arrangements |
| Imitation (Fermi) | States copy the foreign policy posture of more successful neighbours |

### 6.2 The resilience-erosion trap, geopolitically

The trap reads: defection from treaty obligations (D strategies) degrades the security environment (`e_i` falls via `γ`). A degraded environment raises conflict probability (`p_i` rises). When conflict occurs, it further damages the institutional infrastructure that made cooperation possible (`−η d_i` on `e_i`), raising risk again. The cycle is the security spiral in formal form: arms races, norm collapse, and repeated conflict are not independent events but a coupled positive feedback. The threshold mechanism adds a discontinuity: if enough states defect and the collective pool falls below `T`, the security umbrella collapses entirely and even cooperative states face elevated risk they cannot individually offset.

### 6.3 Real-world analogues

- **NATO collective defense (Article 5).** The threshold `T` is the minimum credible deterrence contribution. Member states that do not meet the 2% GDP target are D-strategists in this frame. If too many defect, deterrence fails and conflict probability rises sharply — the threshold maps onto the deterrence-sufficiency condition.
- **Nuclear non-proliferation (NPT).** Each signatory's compliance is a contribution to the shared non-proliferation norm. Free-riders (states pursuing covert programs) degrade the norm environment. A proliferation event (conflict, first use, or demonstrated capability) damages the treaty architecture for all remaining members.
- **ASEAN regional security.** Looser norm structure, more CC-like conditional participation, geographic lattice topology close to the model's assumption. Relevant for the SE Asia focus already present in the flood case study (§1.1).
- **EU security cooperation / OSCE.** High-`e_i`, high-`δ` regime — the engineered extreme in the security domain, analogous to the Netherlands in the flood domain.

### 6.4 Parameter calibration anchors

Unlike the flood case, direct quantitative calibration is harder (war is rarer and less measured than flooding), but several data sources provide anchors.

| Model quantity | Geopolitical source |
|---|---|
| Baseline conflict probability `p_min` | UCDP/PRIO Armed Conflict Dataset — annual conflict onset probability by region |
| `p_max` (fully degraded security environment) | Historical conflict-prone dyads (Correlates of War MIDs), regions with collapsed institutions |
| Loss fraction `ℓ` | World Bank / IMF estimates of GDP loss per conflict year (~5–15% per year of active conflict) |
| Environment degradation `γ` | Quantitative indices: SIPRI arms transfers, treaty withdrawal events, alliance cohesion indices |
| Recovery rate `δ` | Time to treaty re-accession, post-conflict institution rebuild timelines (e.g. Bonn Agreement → Afghan elections) |
| Conflict damage to institutions `η` | Post-conflict norm collapse literature; UCDP recurrence rates (roughly 40% of conflicts recur within 5 years, implying high `η`) |
| Loss aversion `λ_i` | Conflict-memory studies; states bordering recent wars show higher defense spending and treaty participation |

### 6.5 What changes for the networked extension (future work)

The lattice is a geographic approximation. International relations are not governed by proximity alone; the interaction topology is an alliance and trade network with small-world or scale-free properties. Moving to a dynamic network changes several spatial predictions:

- **Clustering** will follow alliance structure, not grid adjacency. Hub states (large alliances) will exert outsized imitation pressure on their treaty partners.
- **The threshold mechanism** interacts with degree heterogeneity: a high-degree state's defection removes disproportionate pool mass and can single-handedly collapse a regional security arrangement.
- **CC dynamics** become path-dependent on network structure: a CC surrounded by D-adjacent hubs will converge to near-zero contribution even if geographically distant UCs are cooperating.
- **Spatial contagion (A+ feedback)** spreads along network edges, not grid adjacency — conflict in a hub state degrades the security environment of all treaty partners simultaneously, not just geographic neighbors.

The lattice model is the correct MVP. Network topology is the natural extension once the core dynamics are established, and it is the step that makes the geopolitical case study more realistic than the flood one rather than less.

### 6.6 Validity notes for the geopolitical case study

The same Klügl structure applies (§3), but the empirical targets shift:

- **Structural validity:** causal loop matches the conflict-trap and security-spiral literature (Jervis 1978; Fearon 1995 on war as bargaining failure under information problems).
- **Replicative validity:** in the well-mixed limit, recover cooperation levels consistent with Axelrod's tournament results and iterated-PD predictions; in the spatial limit, recover alliance clustering patterns qualitatively consistent with known alliance data (COW).
- **Predictive validity:** same caveat as §3.3 — do not over-claim. A bounded test: calibrate to a post-Cold War baseline and check whether the model's predicted direction of cooperation change under rising `p_max` (rising baseline conflict risk) matches the observed trend in treaty participation or burden-sharing disputes.

---

*Sources for the data section: WRI Aqueduct Floods (wri.org/data/aqueduct-floods-hazard-maps; country rankings and income-based protection assumptions); Fathom Global Flood Hazard (Manila packages, OasisHub); Project NOAH / UP NIGS (data.bettergov.ph; Hugging Face bettergovph/project-noah-hazard-maps); Phil-LiDAR / LiPAD (lipad.dream.upd.edu.ph); HazardHunterPH / GeoRisk PH; EM-DAT (CRED); DesInventar / Sendai Monitor; HDX (data.humdata.org); Kolen (2025); MSB and SMHI (Sweden). Calibration numbers and provenance: `from_ding_to_our_model.md` §A. Validation framework: Klügl (2008), via Lecture 8.*

*Authorship note (resolving the handoff action item): the lineage paper is confirmed as Mutlu, A., Roy, D. & Filatova, T. (2023), "Capitalized value of evolving flood risks discount and nature-based solution premiums on property prices," Ecological Economics 205: 107682 (open access, CC BY 4.0; doi 10.1016/j.ecolecon.2022.107682). Debraj Roy is listed with a University of Amsterdam affiliation, so the tie to the instructor is safe to state in the report.*
