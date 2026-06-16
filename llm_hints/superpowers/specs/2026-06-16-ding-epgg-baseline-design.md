# Spatial EPGG Baseline — Ding et al. (2024)

Reproduce the baseline lattice public-goods game with environmental feedback
(Ding, Wang, Zhao, Gu, Chen, *Chaos* **34**, 123138, 2024;
doi:10.1063/5.0242366) as the foundation for a later spatial extension.

**Decisions (this session):**
- New package `src/epgg/`; the Mesa-based `experiment/` (Jonsson blend rule) is
  left untouched. Clean break — Mesa's per-agent object model cannot handle
  L²=40 000 nodes × up to 6×10⁸ steps. Baseline is pure numpy + numba.
- Validation gate = **Fig 2 δ-sweep only** (D→C→C+D at γ=0.04). Build the
  baseline, pass the gate, *then* extend. Do not build baseline + extension
  together — you won't know which part is buggy.

## Model

Square lattice L=200, periodic (toroidal). Each node = one residence with:
- `strategy[L,L] ∈ {0=D, 1=C}`, init random ~50/50.
- `ehi[L,L] ∈ [-1,1]` (environmental health index), init all 0.

**Two distinct neighborhoods — never conflate:**
- `open(i)`  = 4 von Neumann neighbors. Used ONLY to pick the imitation target.
- `closed(i)` = self + 4 neighbors (5 nodes). The paper's "first-order
  neighborhood." Used for the payoff sum AND the EHI feedback. `n_C+n_D=5`.

### Payoff — Eq. (1)

    π_i = r · Σ_{j∈closed(i)} e_j − 5c·[s_i = C]

- `r=4`, `c=1` baseline. `r` is a **linear scaling on environmental benefit,
  not** a classic PGG synergy/pooling factor. There is no pool-and-redistribute
  step.
- The "5" in `5c` = the five games an agent plays (one centered on self, four on
  neighbors); cost is flat `5c` for any cooperator regardless of realized EHI
  gain (even if Δ is wasted against the +1 ceiling).
- **Structural defector advantage:** at any *single* node, D earns exactly `5c`
  more than C would (identical benefit, no cost). Cooperation survives only
  because δ raises local EHI → cooperator-rich neighborhoods have higher `e_j` →
  higher benefit for everyone there (network reciprocity *via the environment*).

### EHI update — Eq. (2), once per generation

    ehi ← clip( ehi + δ·n_C − γ·n_D ,  −1, +1 )

- `n_C`, `n_D` = cooperator / defector counts in each node's **closed**
  neighborhood (single neighborhood — see Decision 1).
- `δ` = cooperator repair rate, `γ` = defector destruction rate.
- Clip ONCE, after the full per-generation increment.

### Strategy update — Fermi, L² steps per generation

Generation = L² elementary updates (random sequential, with replacement):
1. pick random node `x`;
2. pick random `y ∈ open(x)`;
3. `x` copies `y`'s strategy w.p. `W = 1/(1+exp((π_x − π_y)/K))`, `K=0.5`.

Payoffs use the CURRENT strategies and the FROZEN ehi field (EHI does not change
mid-generation). EHI is updated only at generation end, from the post-generation
strategy field.

## Resolved decision points

1. **EHI increment scope → single closed-neighborhood.** Eq. (2) prints a double
   sum `Σ_{j∈Ω_i}` but the prose is explicit: "the presence of a cooperator in
   this neighborhood increases e_i by δ" → `e_i += n_C^i·δ − n_D^i·γ`, counts in
   i's own 5-node neighborhood. The double sum is a typo. Magnitude check
   confirms: single-sum gives max +5δ/gen (≈+0.16 at δ=0.032), matching the
   *gradual* EHI spread over ~1000+ generations in Figs 3–4; the double sum
   (~25 counts) saturates the clip in one generation — incompatible.
2. **Clip once** per generation, after the full increment.
3. **Generation boundary is the load-bearing invariant.** EHI updates ONLY at
   generation end, never per step. Getting this wrong collapses the fast-strategy
   / slow-environment timescale separation — the mechanism behind every
   counterintuitive result.

## Implementation notes (amendments to the original plan)

- **Precompute the benefit term once per generation.** Within a generation EHI
  and the neighborhood are fixed, so `benefit[i] = r·Σ_{closed} e_j` is constant;
  only the cost term flips with `s_i`. Compute `benefit = r·conv(ehi, closed)`
  once, then in the loop `π_x = benefit[x] − 5c·s_x`. Correctness clarification +
  the biggest speedup (no per-step neighborhood resum).
- **End-of-generation counts use post-generation strategies** — convolve the
  strategy field as it stands after all L² Fermi updates.
- **Convolutions** (benefit sum, n_C/n_D counts) vectorized with periodic wrap
  (`scipy.signal.convolve2d(boundary='wrap')` or roll-and-add). The Fermi sweep
  is inherently sequential (each update sees prior within-generation updates) →
  `@njit`. Numba `np.random` with explicit per-repeat seeds.

## Stationarity & measurement

- **Mean-stabilization, not variance.** C+D is cyclic dominance (Figs 4a5, 8c) —
  the cooperator fraction oscillates forever, variance never decays. Declare
  stationary when the *windowed mean* fraction changes < ε between consecutive
  windows. Works for all three phases.
- **`min_gen` gate is mandatory (validated).** The C phase sits at frac≈0 for
  *hundreds* of generations before cooperators recover — Fig 3 reproduced
  exactly: defectors peak at gen ~20, frac stays ≈0.00–0.01 through gen ~150,
  then slow recovery to full C by ~gen 2600 (δ=0.021, γ=0.04, L=200). A naive
  mean-stabilization stop fires on that early plateau and **misclassifies C as
  D**. Only allow a convergence stop after `min_gen` comfortably past the
  recovery window (≥1500 default; raise near the D→C transition).
- **Homogeneity exit is safe** *only* on exact frac 0 or 1 (absorbing). The
  recoverable near-extinction plateau keeps a few survivors (frac > 0 exactly),
  so it is never cut short.
- **Measurement = two averages:** on a homogeneity exit report the final
  fraction; otherwise time-average over the final window — never the declining
  transient. Then ensemble-average over 20 fresh-init repeats.
- **Fresh random init per parameter point** — never warm-start from a neighboring
  δ. Discontinuous transitions (Fig 2) would otherwise show spurious hysteresis.

## Validation gate — Fig 2 (DO BEFORE EXTENDING)

Sweep δ at `r=4, c=1, γ=0.04`. Confirm D→C→C+D: two discontinuous jumps;
cooperator fraction rises from 0, then *declines* within C+D as δ increases
further. Use **L=200 throughout** — the C phase **does not exist at L≤150**
(validated: clusters cannot survive the gen-20 bottleneck on a small lattice, so
the system settles into C+D coexistence ~0.4 instead of full C). Debugging at
L=100 would mislead. ~20–30 δ-points.

**Model already validated against Fig 3** (the C-phase trajectory): at δ=0.021,
γ=0.04, L=200 the run reproduces defector peak → slow recovery → full C (→1.00
by ~gen 2600), and the counterintuitive δ-trend holds (δ=0.021→1.0,
δ=0.05→~0.40).

**GATE PASSED** (L=200, γ=0.04, r=4, c=1, 5 repeats, 16 δ-points): D phase
(δ≤0.01 → C=0) → discontinuous jump → C phase (δ=0.02–0.025 → C=1.0) →
discontinuous drop → C+D phase declining (δ=0.03→0.52, …, δ=1.0→0.15). Both
discontinuous transitions and the counterintuitive in-phase decline reproduced.
Reproduce with `uv run epgg-fig2` (→ epgg_fig2.png, epgg_fig2.npz).

**Cheap sanity checks first** (seconds, before the expensive sweep):
- δ=0, γ=0 → EHI stays 0 → C earns −5c, D earns 0 → pure D.
- high δ, low γ → C phase.
- `n_C+n_D == 5` everywhere; periodic wrap correct at edges.

## Performance budget

Workload `L² × generations × repeats`. Worst case ~6×10⁸ Fermi steps (slow
C-phase invasion) × ~20 δ-points × 20 repeats. Mean-stabilization + homogeneity
exit cut most runs far below worst case. Keep njit kernels free of Python objects
(nopython mode). Hard cap ~10⁸ steps per run, sized up for C-phase points.

## Extension scaffolding (after the gate passes — separate module, swap ONE part)

- Topology change → replace neighborhood construction.
- EHI spatial diffusion → augment the EHI update, e.g. `ehi += D·laplacian(ehi)`.
  Decide whether diffusion runs BEFORE or AFTER the clip — diffusion can move a
  node back below the ceiling and "free up" room the discarded Δ would otherwise
  have wasted.
