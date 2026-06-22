# Final Model Specification

*The spatial collective-risk flood model, eventual target form (A+ feedback, sigmoid risk, loss aversion), with the simpler MVP placeholder noted at each step. Decisions are those recorded in the open-decisions questionnaire (Q1–Q9). Calibration and parameter ranges live in the companion `Full Parameter List.md`; the reasoning behind each choice is in `from_ding_to_our_model.md`. A symbol note: $g$ is the wealth growth rate (Kolen), and the per-cooperator contribution is written $\bar c$ to avoid the $g$ clash in the source file.*

---

## 1. The model in one paragraph

Households sit on a lattice and each season decide how much defence effort to pool with their immediate neighbours. If a neighbourhood pools enough to clear a threshold, it is safe that season. If not, it faces a flood whose probability is set by the local **defence environment**: a well-maintained neighbourhood is safe, a degraded one is exposed. A flood removes a fraction of a household's wealth and damages the defences across the flooded area, which raises next season's risk. This is the resilience-erosion trap. Cooperators (who maintain defences) and defectors (who free-ride) imitate whichever neighbours are doing better, so strategies evolve. The question is whether the unconditional cooperator, who maintains regardless of what neighbours do, still dominates once interaction is local rather than global, and whether the coupled system shows the phase transitions of Ding and the oscillations of Weitz.

---

## 2. Space, agents, state

- **Lattice.** $L \times L$ torus, von Neumann neighbourhood (4 neighbours). One household per cell. The focal group of household $i$ is $G_i = \{i\} \cup \{\text{4 neighbours}\}$, so $|G_i| = 5$. Neighbour lists are precomputed once.
- **Strategy** $s_i \in \{\mathrm{UC}, \mathrm{CC}, \mathrm{D}\}$. UC = unconditional cooperator (always maintains), D = defector (never), CC = conditional cooperator (responds to the local neighbourhood; this local response is the novelty, since Santos showed a lattice equals well-mixed for binary C/D).
- **Environment** $e_i \in [-1, 1]$: the integrity of the local flood defences (drainage, embankments, wetland, soil absorption). High $e_i$ is well-maintained and low-risk; low $e_i$ is degraded and exposed. Initialised to $0$ (Ding).
- **Wealth** $w_i \ge 0$: property value. Initialised to $w_0$.

---

## 3. The round, step by step

One **synchronous** sweep per round (Q1): compute everything from a frozen snapshot, then apply. Notation is collected in the parameter list.

**Step 1 — Contribute.** Defence effort by strategy:

$$
c_i =
\begin{cases}
\bar c & s_i = \mathrm{UC} \\
0 & s_i = \mathrm{D} \\
\text{(rule below)} & s_i = \mathrm{CC}
\end{cases}
$$

The CC responds to the local neighbourhood. Base rule (the MVP placeholder for CC, and the novelty-critical behaviour): the mean of neighbours' previous-round contributions, capped at $\bar c$,

$$
m_i(t) = \frac{1}{4} \sum_{j \in \mathrm{nbr}(i)} c_j(t-1).
$$

Loss-averse rule (eventual, Q7 option a): add a risk premium so a more loss-averse CC pays more to cover perceived expected loss,

$$
c_i(t) = \mathrm{clip}\!\left( m_i(t) + (\lambda_i - 1)\,\frac{p_i\,\ell\,w_i}{|G_i|},\ 0,\ \bar c \right).
$$

At $\lambda_i = 1$ this is the pure matcher; $\lambda_i > 1$ overweights the loss. *(Modelling note: this composition of reciprocity and a loss-aversion premium is one clean way to honour both the "responds to the local average" novelty and Q7(a); confirm with the team before committing. Store `prev_contribution` so CC reads the correct lagged value under synchronous update.)*

**Step 2 — Pool the focal group.** A contribution enters five overlapping pools but is paid once:

$$
P_i = \sum_{j \in G_i} c_j.
$$

**Step 3 — Flood probability from the environment.** Eventual (sigmoid, the target form):

$$
p_i = \frac{p_{\max}}{1 + \exp[\,k\,(e_i - e_0)\,]},
$$

so risk stays low while defences hold and climbs sharply once $e_i$ falls past the midpoint $e_0$; $k$ sets the steepness. MVP placeholder (linear): $p_i = p_{\max}\,(1 - e_i)/2$. Probability is read from the focal cell's own $e_i$.

**Step 4 — Flood check (full immunity, Q3).** Clearing the threshold buys complete safety this round; otherwise the environment-set probability applies:

$$
d_i =
\begin{cases}
0 & P_i \ge T \\
\mathrm{Bernoulli}(p_i) & P_i < T
\end{cases}
$$

Draws are independent per household; spatial correlation of floods is emergent (shared pool membership), not hand-coded.

**Step 5 — Wealth and fitness.** Wealth grows multiplicatively (Q4), pays the contribution, and loses a fraction $\ell$ to a flood (Q5):

$$
w_i \leftarrow (1 + g)\,w_i - c_i - d_i\,\ell\,w_i \;\Big[\, +\, R\,\tfrac{P_i}{|G_i|} \,\Big].
$$

The bracketed term is the public-good multiplier, with $R = 0$ in the main model (pure cost, Q2) and $R > 0$ only for the Jonsson validation run. The per-round payoff is the net flow,

$$
\pi_i = g\,w_i - c_i - d_i\,\ell\,w_i \;\Big[\, +\, R\,\tfrac{P_i}{|G_i|} \,\Big],
$$

which a flood makes sharply negative (it loses $\ell\,w_i$), so disasters dominate fitness. The fitness used for imitation is discounted accumulated wealth:

$$
\phi_i \leftarrow (1 - \kappa)\,\phi_i + \pi_i.
$$

**Step 6 — Environment update (A+, whole-group damage, Q6).** Once per generation, on a slower clock than strategies. Maintenance heals, neglect degrades, and a flood damages the defences across the whole inundated area:

$$
e_j \leftarrow \mathrm{clip}\!\left( e_j + \delta\,m_j^{+} - \gamma\,m_j^{-} - \eta \sum_{k \in G_j} d_k,\ -1,\ 1 \right).
$$

Here $m_j^{+}$ is the maintenance effort in $G_j$ and $m_j^{-}$ the neglect. For the binary MVP (UC/D only) these are the cooperator and defector counts $n_j^{C}, n_j^{D}$, recovering Ding exactly. With CC's continuous contribution, use the effort-weighted form $m_j^{+} = \sum_{i \in G_j} c_i / \bar c$ and $m_j^{-} = |G_j| - m_j^{+}$, which reduces to the counts when contributions are binary. The damage term $-\eta \sum_{k \in G_j} d_k$ is the whole-focal-group scope: because the neighbourhood is symmetric on the torus ($j \in G_k \iff k \in G_j$), a flood at any $k$ whose group contains $j$ lands on $j$, which is exactly the floods inside $G_j$. So $j$'s defences are degraded by $\eta$ times the number of floods in its own focal group. *(MVP placeholder: plain Ding feedback, $\eta = 0$, focal-cell only; switch on $\eta > 0$ and whole-group scope for the headline runs.)*

**Step 7 — Strategy update (synchronous Fermi).** Each household picks a random neighbour $j$ and adopts its strategy with probability

$$
W(s_i \leftarrow s_j) = \frac{1}{1 + \exp[\,-\beta\,(\phi_j - \phi_i)\,]}.
$$

Stage all new strategies in a buffer, then apply at once.

**Step 8 — Mutation.** With probability $\mu$, set $s_i$ to a random strategy.

---

## 4. Build order and the two regimes

1. **MVP.** UC + D only, linear risk, plain Ding feedback ($\eta = 0$), flat income, $R = 0$. Validate the well-mixed limit against Jonsson Figure 7 (with $R > 0$, a single fully connected group, frozen strategies).
2. **Headline.** Switch on the flood-damage term ($\eta > 0$, whole-group), the conditional cooperator, the sigmoid risk, multiplicative growth, and heterogeneous loss aversion.

The **linear phase** uses $p_{\max}$ as the risk knob; the **sigmoid phase** fixes $p_{\max}$ and treats the risk *shape* ($k, e_0$) as the parameters of interest. The two phases carry different sensitivity-analysis sets (parameter list, §7).

---

## 5. Outputs

Per generation: cooperation fraction (UC + CC, or fraction contributing), strategy counts, mean wealth, flood rate, mean environment $\bar e$. Periodically (it is expensive): Moran's I for spatial clustering. The headline resilience measure is the fraction of focal groups clearing the threshold, averaged over the final measurement window. For sensitivity-analysis runs, collect only final-window aggregates.

---

## 6. Case studies

The model is instantiated in two parallel case studies sharing identical mechanics. Parameters are tuned per case; the equations do not change.

### 6.1 Flood defence (primary)

The flood reading is the default semantic layer throughout this document. `e_i` is drainage and embankment integrity, `c_i` is maintenance effort, a flood event is a literal inundation, and wealth is property value. Calibration anchors: Aqueduct income-based protection standards (25-year for Philippines, 1000-year for Netherlands), Kolen depth-damage (`ℓ ≈ 0.34` for ~2 m), Project NOAH hazard rasters for initial `e_i(0)`. The three-point contrast (Philippines / Sweden / Netherlands) gives a designed cross-country experiment over the risk parameter `p_max`.

### 6.2 Geopolitical: treaty participation and the conflict trap

Every state variable and parameter reinterprets cleanly without changing the equations.

| Model quantity | Geopolitical referent |
|---|---|
| Agent $i$ | Nation-state or regional actor |
| Strategy UC | Unconditional treaty adherent — fulfils obligations regardless of neighbours |
| Strategy D | Free-rider / norm violator |
| Strategy CC | Conditional participant — contributes in proportion to what neighbours contribute |
| Contribution $c_i$ | Defence spending, diplomatic effort, treaty compliance (e.g. 2% GDP NATO target) |
| Pool $P_i$, threshold $T$ | Collective security quorum — minimum combined commitment to deter conflict |
| Environment $e_i \in [-1,1]$ | Regional security environment: institutional trust, norm robustness, alliance cohesion |
| Flood probability $p_i$ | Conflict outbreak probability, driven by how degraded the security environment is |
| Flood event $d_i$ | War or armed conflict |
| Wealth $w_i$ | Economic and political capital |
| Flood loss $\ell\,w_i$ | War costs: GDP destruction, political instability, reconstruction burden |
| Maintenance rate $\delta$ | Diplomatic effort and institution-building raising $e_i$ |
| Neglect rate $\gamma$ | Norm erosion from free-riding, arms build-up, or treaty withdrawal |
| Flood damage $\eta$ | Conflict damages the institutions that prevent the next conflict — war destroys trust, collapses agreements, creates grievances |
| Loss aversion $\lambda_i$ | War-memory effect: states that recently experienced conflict invest more in security arrangements |

**The conflict trap.** Defection from treaty obligations degrades the security environment ($e_i$ falls via $\gamma$). A degraded environment raises conflict probability ($p_i$ rises). When conflict occurs it further damages institutional infrastructure ($-\eta\,d_i$ on $e_i$), raising risk again. This is the security spiral in formal terms: arms races, norm collapse, and repeated conflict as a coupled positive feedback, not independent events. The threshold adds a discontinuity: if collective pool falls below $T$, the security umbrella collapses and even cooperative states face elevated risk they cannot individually offset.

**Real-world analogues.** NATO Article 5 (threshold $T$ = minimum credible deterrence; member states below 2% GDP are D-strategists); NPT non-proliferation norm (compliance as contribution, proliferation event as the A+ damage term); ASEAN regional security (loose CC-like conditional participation, geographic lattice topology); EU/OSCE (high-$e_i$, high-$\delta$ regime — the engineered extreme, analogous to the Netherlands in the flood case).

**Calibration anchors.** Baseline conflict probability from UCDP/PRIO Armed Conflict Dataset; loss fraction $\ell$ from World Bank GDP-loss-per-conflict-year estimates (~5–15%); degradation $\gamma$ from SIPRI arms-transfer indices and treaty withdrawal events; flood-damage rate $\eta$ informed by UCDP conflict recurrence rate (~40% within 5 years).

**Networked topology (future work).** The lattice is a geographic approximation. International relations follow alliance and trade networks with small-world or scale-free properties. A hub state's defection removes disproportionate pool mass; CC dynamics become path-dependent on network degree. Spatial contagion spreads along network edges rather than grid adjacency. The lattice MVP is the correct starting point; network topology is the natural extension once core dynamics are established.

---

## 7. What this model satisfies

Discrete agents with internal state ($s_i, e_i, w_i$); spatial localisation (lattice, local pools); bounded rationality (Fermi imitation, loss-averse perception); risk and loss aversion (stochastic flood, $\lambda_i$); strategy learning (imitation + mutation); game-theoretically formalised interaction (threshold public-goods game); no central supervisor; nontrivial emergent behaviour (clustering, phase transitions, possible oscillations); and a sensitivity analysis with $\beta$ always included. These are the course's mandatory ingredients.
