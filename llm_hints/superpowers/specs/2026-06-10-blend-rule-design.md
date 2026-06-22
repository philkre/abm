# Blend update rule — design

**Date:** 2026-06-10
**Status:** approved (replaces the asymmetric aspiration rule in `src/experiment/`)

## Motivation

The aspiration rule was ad hoc and missed three empirical patterns from
Jonsson & Jonsson (2025): the post-failed-check shape (Fig 5: flat one round,
then rise to a plateau at the threshold), the existence-of-risk effect
(10P ≈ 40P, Fig 4), and a persistent free-rider share (~4%). Redesign from
first principles: what does a subject in the experiment actually do?

- Round 1: give ~60% of endowment (standard PGG opening).
- No risk (Control): conditional cooperation — match others' previous-round
  mean (shown on the summary screen), minus a self-serving bias; intrinsic
  generosity (warm glow) keeps contributions from collapsing to zero.
- Risk present: a second anchor appears — the fair share of the threshold
  (60/4 = 15). Paper: subjects "give more and do not match the contributions
  of others"; conditionality weakens, pot converges just above 60.
- The threat weight differs per person ("some instantly cooperate with the
  presence of a threat, others only after getting burned") and grows after a
  failed check — with a one-round lag (gambler's fallacy, Fig 5).

## Rule

Synchronous, end of each round, per agent i:

```
c_{i,t+1} = clip( w_it·share + (1 − w_it)·(m_i·x̄_t + (1 − m_i)·g_i − b), 0, E )

share  = (threshold_hi / n)·anchor_margin   # worst case under Level
                                   # uncertainty (70/4); margin > 1 = insurance
                                   # against others' shortfall (pot plateaus
                                   # above 60 in the paper, Fig 5/Table 1)
x̄_t    = others' mean contribution in round t (info subjects actually see)
w_it   = s_i · θ_t                 # threat weight
c_{i,0} = w_i0·share + (1 − w_i0)·g_i
```

Three anchors: threshold share (weight w), others' mean (conformity m),
intrinsic generosity g. Heterogeneous traits per agent, all uniform draws:

| trait | draw | meaning |
|---|---|---|
| g_i | U(g_lo, g_hi) | intrinsic generosity / warm glow |
| m_i | U(m_lo, m_hi) | conformity (match others) |
| s_i | U(0, 1)       | threat sensitivity |

Session-level threat salience θ:

- θ_0 = θ_init if disaster_prob > 0 else 0  — switched on by the *existence*
  of announced risk, not its magnitude (paper's coarse probability heuristic)
- failed check at round t → θ += θ_bump, landing at round t+2 (one-round lag)
- θ decays by factor (1 − θ_decay) per round (habituation), clipped to [0, 1]

## Why each empirical pattern falls out

| pattern | mechanism |
|---|---|
| Control declines 12→~10, stable | w=0; fixed point x̄* = ḡ − b/(1−m̄) |
| Treatments rise to pot ≈ 60+ | w>0 mass pulls toward share; burns raise θ |
| 10P ≈ 40P (existence effect) | probability does not appear in the rule; θ_init is the same for any p>0 |
| 70/100% slightly higher | more failed checks early → more θ bumps |
| Fig 5 flat at +1, rise at +2 | θ bump lands with one-round lag |
| Level highest (16.5) | share = 70/4 = 17.5 (worst-case threshold) |
| UC/CC/FR divergence | joint (g, m, s) draw: high s → flat high line (UC); high m → matching line (CC); low s, m, g → flat low line (FR) |
| Conformity lower in treatments (S3) | effective matching weight is (1−w)·m_i |

## Honesty note (calibrated replication)

The rule is linear in others' mean — the same functional form the LCP
classifier fits. Type *form* is therefore built in, and the treatment type
mix is a calibration target, not a prediction (the paper's own Fig 7
simulation makes the same move). What remains emergent/predicted: all
dynamics (levels, trends, pass rates, post-check response), the
Control-vs-treatment type *shift* from a single population draw, and the
Control mix itself.

## Out of scope

- Almost-made-it risky shift (Fig 5B dip) — possible later θ tweak.
- Country differences (Sweden vs Philippines risk-willingness).

## Implementation notes

- `AgentConfig` fields: g_lo, g_hi, m_lo, m_hi, bias, theta_init, theta_bump,
  theta_decay. Aspiration fields, contrib deltas, and disaster_penalty are
  removed; `agent.payoff` stays as a recorded metric (0 on disaster rounds).
- θ lives on the model (shared session-level salience) with a one-slot
  pending buffer for the lag; w_i = s_i·θ computed in the learning phase.
- DataCollector: replace mean_aspiration with theta.
- Parameters tuned by sweep against: Control 12→~10 (CC-dominant mix);
  40P ≈ 15.1, pass ≈ 0.58, mix ≈ 56/36/4; 10P ≈ 14.9; Level ≈ 16.5;
  Impact ≈ 40P; Fig 4 curve; Fig 5 shape.
