;; spatcoop_v2.nlogo
;; Faithful NetLogo replica of philkre-abm/src/spatcoop/model.py (state: 2026-06-27)
;; Strategies: UC (unconditional), CC (conditional), D (defector)
;; Risk: linear only | Wealth: OU / Wiener-with-drift | Neighbourhood: von Neumann (4)
;;
;; INTERFACE CONVENTION
;;   - SLIDERS on top      = the 5 sensitivity-analysis control parameters
;;                           (beta, p-max, T-over-E, b, eta) + grid-size (its own slider).
;;   - NUMBER INPUTS below = the parameters held FIXED during the SA
;;                           (c-bar, loss-fraction, sigma, delta, gamma, kappa,
;;                            mutation-rate, lambda-mean, lambda-sigma).
;;   - Two phase presets expose the model's two regimes:
;;       "Cooperative phase" (oscillatory, mean-env cycles 0.3–0.9)  [DEFAULT]
;;       "Collapse phase"    (defection wins, mean-env → −1)
;;
;; THRESHOLD CONVENTION (matches sa.py):  T = T-over-E * 5    (5 cells, income unit E = 1)

globals [
  T                     ;; derived threshold = T-over-E * 5  (SA convention, no c-bar factor)

  ;; Order parameters (updated each tick in update-globals)
  frac-uc frac-cc frac-d
  flood-rate
  mean-env env-std
  mean-wealth wealth-uc wealth-cc wealth-d
  wealth-var
  gini-wealth
  resilience
  coop-frac
  mean-contrib cc-contrib-frac
  mean-fitness mean-payoff
  mean-pool-gap near-miss-frac
  p-span-uc p-span-cc p-span-d
  max-cluster-uc max-cluster-cc max-cluster-d
  interface-density
  cluster-sizes         ;; list of every cooperator (UC|CC) cluster's raw cell count this round
]

patches-own [
  strategy            ;; "UC" | "CC" | "D"
  env                 ;; e_i in [-1, 1]
  wealth              ;; w_i >= 0
  fitness             ;; phi_i discounted accumulated payoff
  lambda-val          ;; lambda_i loss-aversion coefficient
  contribution        ;; c_i this round
  prev-contribution   ;; c_i last round (CC lagged-mean rule)
  pool                ;; P_i = focal-group contribution sum
  p-flood             ;; flood probability (linear: p-max*(1-e)/2)
  flooded?            ;; d_i boolean
  payoff              ;; pi_i net payoff this round
  ticks-since-flood   ;; recency counter (reset to 0 when flooded)
  new-strategy        ;; synchronous update buffer
  cluster-id          ;; scratch for BFS cluster analysis
]

;; ============================================================
;; SETUP
;; ============================================================

to setup
  clear-all
  resize-world 0 (grid-size - 1) 0 (grid-size - 1)
  set-patch-size (floor (400 / grid-size))
  set T (T-over-E * 5)                 ;; SA convention: T = T-over-E * 5 (NOT * c-bar)
  ask patches [
    ;; Equal thirds initial mix (matches initial_mix = "thirds" in Python)
    let r random 3
    set strategy (ifelse-value (r = 0) ["D"] (r = 1) ["UC"] ["CC"])
    set env 0.0
    set wealth w0
    set fitness 0.0
    set contribution 0.0
    set prev-contribution 0.0
    set flooded? false
    set payoff 0.0
    set ticks-since-flood 999
    set cluster-id -1
    set lambda-val draw-lambda
  ]
  set cluster-sizes (list)
  update-globals
  recolor
  reset-ticks
end

to-report draw-lambda
  if lambda-mode = "homogeneous" [ report lambda-mean ]
  if lambda-mode = "lognormal" [
    ;; Log-normal with specified mean: mu_ln = ln(mean) - sigma^2/2 (sigma = lambda-sigma)
    let s lambda-sigma
    let m (ln lambda-mean) - (s * s) / 2
    report max (list 1.0 (exp (random-normal m s)))
  ]
  ;; Uniform on [1, 4] matching Python code's lambda_max = 4.0 default
  if lambda-mode = "uniform" [ report 1 + random-float 3 ]
  report lambda-mean
end

;; ============================================================
;; MAIN LOOP
;; ============================================================

to go
  play-round
  update-environment
  imitate
  mutate
  update-globals
  recolor
  tick
end

;; ============================================================
;; STEPS 1-5: PLAY ROUND
;; ============================================================

to play-round
  ;; Latch previous contributions (CC reads these for the lagged mean)
  ask patches [ set prev-contribution contribution ]

  ;; Step 1: Contributions
  ask patches [
    set p-flood clamp (p-max * (1.0 - env) / 2.0) 0 1
    if strategy = "UC" [ set contribution c-bar ]
    if strategy = "D"  [ set contribution 0 ]
    if strategy = "CC" [
      let nbr-mean mean [prev-contribution] of neighbors4
      let premium (lambda-val - 1) * p-flood * loss-fraction * wealth / 5
      set contribution clamp (nbr-mean + premium) 0 c-bar
    ]
  ]

  ;; Step 2: Pool over focal group (self + 4 VN neighbours)
  ask patches [
    set pool sum [contribution] of (patch-set self neighbors4)
  ]

  ;; Step 4: Flood check — full immunity if pool >= T
  ask patches [
    ifelse pool >= T [
      set flooded? false
    ] [
      set flooded? (random-float 1 < p-flood)
    ]
    ifelse flooded?
      [ set ticks-since-flood 0 ]
      [ set ticks-since-flood (ticks-since-flood + 1) ]
  ]

  ;; Step 5: Wealth (OU additive / Wiener-with-drift) and fitness
  ask patches [
    let w-before wealth
    let flood-loss 0
    if flooded? [ set flood-loss loss-fraction * w-before ]
    let noise 0
    if sigma > 0 [ set noise random-normal 0 sigma ]
    set wealth max (list 0 (w-before + b - contribution - flood-loss + noise))
    ;; Payoff uses w-before for flood-loss (matches model.py line 169)
    set payoff (b - contribution - flood-loss)
    set fitness ((1 - kappa) * fitness + payoff)
  ]
end

;; ============================================================
;; STEP 6: ENVIRONMENT UPDATE (A+ form, effort-weighted)
;; ============================================================

to update-environment
  ask patches [
    let focal (patch-set self neighbors4)
    ;; m_j^+ = effort-weighted maintenance in [0,5]
    let maint (ifelse-value (c-bar > 0) [(sum [contribution] of focal) / c-bar] [0])
    let neglect (5 - maint)
    let flood-group (count focal with [flooded?])
    set env clamp (env + delta * maint - gamma * neglect - eta * flood-group) -1 1
  ]
end

;; ============================================================
;; STEP 7: FERMI IMITATION (synchronous)
;; ============================================================

to imitate
  ask patches [
    let mate one-of neighbors4
    let prob fermi-prob ([fitness] of mate - fitness)
    set new-strategy (ifelse-value (random-float 1 < prob) [[strategy] of mate] [strategy])
  ]
  ask patches [ set strategy new-strategy ]
end

to-report fermi-prob [diff]
  ;; Clip exponent to avoid overflow (matches Python kernel's +-30 clip)
  let z clamp (- beta * diff) -30 30
  report 1.0 / (1.0 + exp z)
end

;; ============================================================
;; STEP 8: MUTATION
;; ============================================================

to mutate
  ask patches [
    if random-float 1 < mutation-rate [
      let r random 3
      set strategy (ifelse-value (r = 0) ["D"] (r = 1) ["UC"] ["CC"])
    ]
  ]
end

;; ============================================================
;; GLOBAL STATISTICS
;; ============================================================

to update-globals
  let n count patches

  ;; Strategy shares
  set frac-uc  count patches with [strategy = "UC"] / n
  set frac-cc  count patches with [strategy = "CC"] / n
  set frac-d   count patches with [strategy = "D"]  / n

  ;; Flood and environment
  set flood-rate count patches with [flooded?] / n
  set mean-env   mean [env] of patches
  set env-std    standard-deviation [env] of patches

  ;; Resilience: fraction of focal groups clearing the threshold
  set resilience count patches with [pool >= T] / n

  ;; Wealth
  set mean-wealth mean [wealth] of patches
  set wealth-var  (ifelse-value (n > 1) [variance [wealth] of patches] [0])
  let uc-p patches with [strategy = "UC"]
  let cc-p patches with [strategy = "CC"]
  let d-p  patches with [strategy = "D"]
  set wealth-uc (ifelse-value any? uc-p [mean [wealth] of uc-p] [0])
  set wealth-cc (ifelse-value any? cc-p [mean [wealth] of cc-p] [0])
  set wealth-d  (ifelse-value any? d-p  [mean [wealth] of d-p]  [0])
  set gini-wealth compute-gini

  ;; Cooperation and contribution
  set coop-frac (frac-uc + frac-cc)
  set mean-contrib (ifelse-value (c-bar > 0)
    [mean [contribution] of patches / c-bar] [0])
  set cc-contrib-frac (ifelse-value (any? cc-p and c-bar > 0)
    [mean [contribution] of cc-p / c-bar] [0])

  ;; Fitness and payoff
  set mean-fitness mean [fitness] of patches
  set mean-payoff  mean [payoff]  of patches

  ;; Pool gap metrics
  let exposed patches with [pool < T]
  set mean-pool-gap (ifelse-value (any? exposed and T > 0)
    [mean [(T - pool) / T] of exposed] [0])
  set near-miss-frac count patches with [pool >= 0.9 * T and pool < T] / n

  ;; Interface density: fraction of VN neighbour pairs differing in strategy
  let diff-h count patches with [strategy != [strategy] of patch-at 1 0]
  let diff-v count patches with [strategy != [strategy] of patch-at 0 1]
  set interface-density (diff-h + diff-v) / (2 * n)

  ;; Cluster statistics (BFS over all strategies)
  analyze-clusters
end

;; ============================================================
;; CLUSTER ANALYSIS (4-connected BFS, torus-spanning detection)
;; Also collects raw cooperator-cluster sizes for the log-log distribution.
;; ============================================================

to analyze-clusters
  ask patches [ set cluster-id -1 ]
  let n count patches
  set max-cluster-uc 0  set max-cluster-cc 0  set max-cluster-d 0
  set p-span-uc 0        set p-span-cc 0        set p-span-d 0
  set cluster-sizes (list)
  let cid 0

  foreach ["UC" "CC" "D"] [ strat ->
    ask patches with [strategy = strat] [
      if cluster-id = -1 [
        ;; BFS using agentset expansion (fast C-level operations)
        set cluster-id cid
        let component (patch-set self)
        let frontier  (patch-set self)

        while [any? frontier] [
          let new-f (patch-set [neighbors4 with [strategy = strat and cluster-id = -1]] of frontier)
          ask new-f [ set cluster-id cid ]
          set component (patch-set component new-f)
          set frontier new-f
        ]

        let csize count component
        let frac csize / n
        ;; Spanning: touches both x=0 and x=max-pxcor, or both y=0 and y=max-pycor
        let spans? (
          (any? component with [pxcor = min-pxcor] and any? component with [pxcor = max-pxcor])
          or
          (any? component with [pycor = min-pycor] and any? component with [pycor = max-pycor])
        )

        if strat = "UC" [
          if frac > max-cluster-uc [ set max-cluster-uc frac ]
          if spans? [ set p-span-uc p-span-uc + frac ]
          set cluster-sizes lput csize cluster-sizes
        ]
        if strat = "CC" [
          if frac > max-cluster-cc [ set max-cluster-cc frac ]
          if spans? [ set p-span-cc p-span-cc + frac ]
          set cluster-sizes lput csize cluster-sizes
        ]
        if strat = "D" [
          if frac > max-cluster-d [ set max-cluster-d frac ]
          if spans? [ set p-span-d p-span-d + frac ]
        ]
        set cid cid + 1
      ]
    ]
  ]
end

;; Log-log cooperator-cluster-size distribution (pen update command).
;; A straight line ⇒ power-law n(s) ~ s^(−tau).
to plot-cluster-dist
  set-current-plot "Cluster sizes (log-log)"
  set-current-plot-pen "n(s)"
  plot-pen-reset
  if empty? cluster-sizes [ stop ]
  foreach (sort remove-duplicates cluster-sizes) [ s ->
    let cnt length (filter [x -> x = s] cluster-sizes)
    plotxy (log s 10) (log cnt 10)
  ]
end

;; ============================================================
;; GINI COEFFICIENT
;; ============================================================

to-report compute-gini
  let sorted-w sort [wealth] of patches
  let n length sorted-w
  if n = 0 [ report 0 ]
  let total sum sorted-w
  if total = 0 [ report 0 ]
  let i 1
  let weighted 0
  foreach sorted-w [ v ->
    set weighted weighted + i * v
    set i i + 1
  ]
  report (2 * weighted / (n * total)) - ((n + 1) / n)
end

;; ============================================================
;; DISPLAY
;; ============================================================

to recolor
  if display-mode = "strategy"      [ ask patches [ color-strategy ] ]
  if display-mode = "environment"   [ ask patches [ color-environment ] ]
  if display-mode = "wealth"        [ ask patches [ color-wealth ] ]
  if display-mode = "payoff"        [ ask patches [ color-payoff ] ]
  if display-mode = "fitness"       [ ask patches [ color-fitness ] ]
  if display-mode = "flood-recency" [ ask patches [ color-recency ] ]
  if display-mode = "loss-aversion" [ ask patches [ color-lambda ] ]
end

to color-strategy
  set pcolor (ifelse-value
    (strategy = "UC") [green]
    (strategy = "CC") [orange]
    [red + 1])
end

to color-environment
  ;; Dark = healthy (e=+1), light = degraded (e=-1)
  set pcolor scale-color blue env -1.4 1.4
end

to color-wealth
  let max-w max [wealth] of patches
  set pcolor (ifelse-value (max-w > 0) [scale-color green wealth 0 (max-w * 1.1)] [grey])
end

to color-payoff
  if payoff >= 0 [ set pcolor scale-color lime (payoff + 0.001) 0 (b * 2 + 0.001) ]
  if payoff < 0  [ set pcolor scale-color red  (- payoff)       0 (b * 3 + 0.001) ]
end

to color-fitness
  let f-max max (list 0.001 (max [abs fitness] of patches))
  if fitness >= 0 [ set pcolor scale-color lime fitness 0 f-max ]
  if fitness < 0  [ set pcolor scale-color red  (- fitness) 0 f-max ]
end

to color-recency
  set pcolor (ifelse-value
    (ticks-since-flood = 0) [red]
    [scale-color grey (min (list ticks-since-flood 30)) -5 35])
end

to color-lambda
  set pcolor scale-color violet lambda-val 0.5 5.5
end

;; ============================================================
;; PHASE PRESETS
;; ============================================================

to preset-cooperative
  ;; Oscillatory cooperative regime — NetLogo effective params verified in spatcoop
  ;; (2026-06-27): mean-env cycles 0.3–0.9, coop-frac ~0.5–0.7. Cheap cooperation
  ;; (c-bar/b ≈ 0.036) + catastrophic floods (ell·w ≫ b) sustain contributions.
  set grid-size       50
  set beta            1.8
  set p-max           1.0
  set T-over-E        0.35
  set b               21
  set eta             0.005
  set c-bar           0.75
  set loss-fraction   0.64
  set w0              1.0
  set sigma           0.1
  set delta           0.042
  set gamma           0.018
  set kappa           0.1
  set mutation-rate   0.0104
  set lambda-mean     2.25
  set lambda-sigma    0.5
  set lambda-mode     "lognormal"
  set display-mode    "strategy"
  setup
end

to preset-collapse
  ;; Collapse regime — defection wins, mean-env → −1. Expensive cooperation
  ;; (c-bar/b = 0.75) means Fermi imitation drives UC/CC extinct (the SA's headline
  ;; regime at low income). Same fixed env params as the cooperative preset.
  set grid-size       50
  set beta            2.0
  set p-max           0.5
  set T-over-E        0.65
  set b               1
  set eta             0.005
  set c-bar           0.75
  set loss-fraction   0.64
  set w0              1.0
  set sigma           0.1
  set delta           0.042
  set gamma           0.018
  set kappa           0.1
  set mutation-rate   0.0104
  set lambda-mean     2.25
  set lambda-sigma    0.5
  set lambda-mode     "lognormal"
  set display-mode    "strategy"
  setup
end

;; ============================================================
;; UTILITY
;; ============================================================

to-report clamp [x lo hi]
  report max (list lo (min (list hi x)))
end
@#$#@#$#@
GRAPHICS-WINDOW
425
10
841
427
-1
-1
8.0
1
10
1
1
1
0
1
1
1
0
49
0
49
0
0
1
ticks
30.0

BUTTON
10
10
100
48
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
104
10
195
48
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
199
10
305
48
Cooperative phase
preset-cooperative
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
309
10
418
48
Collapse phase
preset-collapse
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

TEXTBOX
10
51
418
69
─── SENSITIVITY-ANALYSIS PARAMETERS  (sliders) ───
11
105.0
1

SLIDER
10
70
418
103
grid-size
grid-size
20
200
50.0
10
1
NIL
HORIZONTAL

SLIDER
10
105
418
138
beta
beta
0.1
10.0
1.8
0.1
1
NIL
HORIZONTAL

SLIDER
10
140
418
173
p-max
p-max
0.0
1.0
1.0
0.05
1
NIL
HORIZONTAL

SLIDER
10
175
418
208
T-over-E
T-over-E
0.1
1.0
0.35
0.05
1
NIL
HORIZONTAL

SLIDER
10
210
418
243
b
b
1
30
21.0
1
1
NIL
HORIZONTAL

SLIDER
10
245
418
278
eta
eta
0.0
0.02
0.005
0.001
1
NIL
HORIZONTAL

TEXTBOX
10
281
418
299
─── FIXED PARAMETERS  (number inputs — held constant in the SA) ───
11
15.0
1

INPUTBOX
10
301
108
361
c-bar
0.75
1
0
Number

INPUTBOX
113
301
211
361
loss-fraction
0.64
1
0
Number

INPUTBOX
216
301
314
361
sigma
0.1
1
0
Number

INPUTBOX
319
301
417
361
delta
0.042
1
0
Number

INPUTBOX
10
363
108
423
gamma
0.018
1
0
Number

INPUTBOX
113
363
211
423
kappa
0.1
1
0
Number

INPUTBOX
216
363
314
423
mutation-rate
0.0104
1
0
Number

INPUTBOX
319
363
417
423
lambda-mean
2.25
1
0
Number

INPUTBOX
10
425
108
485
lambda-sigma
0.5
1
0
Number

INPUTBOX
113
425
211
485
w0
1.0
1
0
Number

CHOOSER
216
425
314
470
lambda-mode
lambda-mode
"homogeneous" "lognormal" "uniform"
1

CHOOSER
319
425
417
470
display-mode
display-mode
"strategy" "environment" "wealth" "payoff" "fitness" "flood-recency" "loss-aversion"
0

MONITOR
10
492
105
537
% UC
frac-uc * 100
1
1
11

MONITOR
108
492
205
537
% CC
frac-cc * 100
1
1
11

MONITOR
208
492
305
537
% D
frac-d * 100
1
1
11

MONITOR
320
492
417
537
flood rate %
flood-rate * 100
2
1
11

MONITOR
10
539
140
584
mean env
mean-env
3
1
11

MONITOR
143
539
278
584
resilience
resilience
3
1
11

MONITOR
281
539
417
584
mean wealth
mean-wealth
3
1
11

TEXTBOX
425
435
841
545
Display (strategy mode):  green = UC (unconditional cooperator),  orange = CC (conditional cooperator),  red = D (defector).\nTwo phase buttons set every parameter for the regime:\n• Cooperative phase → oscillatory, mean-env cycles 0.3–0.9 (NetLogo headline).\n• Collapse phase → defection wins, mean-env → −1 (SA low-income regime).
11
0.0
1

PLOT
850
10
1190
195
Strategy shares
generation
%
0.0
10.0
0.0
100.0
true
true
"" ""
PENS
"UC" 1.0 0 -10899396 true "" "plot frac-uc * 100"
"CC" 1.0 0 -955883 true "" "plot frac-cc * 100"
"D" 1.0 0 -2674135 true "" "plot frac-d * 100"

PLOT
850
200
1190
385
Cooperation
generation
fraction
0.0
10.0
0.0
1.0
true
true
"" ""
PENS
"coop frac" 1.0 0 -13345367 true "" "plot coop-frac"
"mean contrib" 1.0 0 -10899396 true "" "plot mean-contrib"
"CC contrib" 1.0 0 -955883 true "" "plot cc-contrib-frac"

PLOT
850
390
1190
575
Resilience
generation
fraction at threshold
0.0
10.0
0.0
1.0
true
false
"" ""
PENS
"resilience" 1.0 0 -13345367 true "" "plot resilience"

PLOT
850
580
1190
765
Flood rate
generation
fraction flooded
0.0
10.0
0.0
1.0
true
false
"" ""
PENS
"flood" 1.0 0 -7500403 true "" "plot flood-rate"

PLOT
850
770
1190
955
Mean environment
generation
e
0.0
10.0
-1.0
1.0
true
true
"" ""
PENS
"mean env" 1.0 0 -13791810 true "" "plot mean-env"
"env std" 1.0 0 -14835848 true "" "plot env-std"

PLOT
1195
10
1535
195
Mean wealth
generation
w
0.0
10.0
0.0
2.0
true
true
"" ""
PENS
"overall" 1.0 0 -16777216 true "" "plot mean-wealth"
"UC" 1.0 0 -10899396 true "" "plot wealth-uc"
"CC" 1.0 0 -955883 true "" "plot wealth-cc"
"D" 1.0 0 -2674135 true "" "plot wealth-d"

PLOT
1195
200
1535
385
Wealth variance
generation
var(w)
0.0
10.0
0.0
1.0
true
false
"" ""
PENS
"var" 1.0 0 -5825686 true "" "plot wealth-var"

PLOT
1195
390
1535
575
Wealth inequality (Gini)
generation
Gini
0.0
10.0
0.0
1.0
true
false
"" ""
PENS
"Gini" 1.0 0 -8630108 true "" "plot gini-wealth"

PLOT
1195
580
1535
765
Fitness and Payoff
generation
value
0.0
10.0
-1.0
1.0
true
true
"" ""
PENS
"mean fitness" 1.0 0 -13345367 true "" "plot mean-fitness"
"mean payoff" 1.0 0 -2674135 true "" "plot mean-payoff"

PLOT
1195
770
1535
955
Pool gap
generation
fraction
0.0
10.0
0.0
1.0
true
true
"" ""
PENS
"pool gap" 1.0 0 -2674135 true "" "plot mean-pool-gap"
"near miss" 1.0 0 -955883 true "" "plot near-miss-frac"

PLOT
1540
10
1880
195
Spanning cluster fraction
generation
fraction of cells
0.0
10.0
0.0
1.0
true
true
"" ""
PENS
"UC span" 1.0 0 -10899396 true "" "plot p-span-uc"
"CC span" 1.0 0 -955883 true "" "plot p-span-cc"
"D span" 1.0 0 -2674135 true "" "plot p-span-d"

PLOT
1540
200
1880
385
Max cluster fraction
generation
fraction of cells
0.0
10.0
0.0
1.0
true
true
"" ""
PENS
"UC max" 1.0 0 -10899396 true "" "plot max-cluster-uc"
"CC max" 1.0 0 -955883 true "" "plot max-cluster-cc"
"D max" 1.0 0 -2674135 true "" "plot max-cluster-d"

PLOT
1540
390
1880
575
Interface density
generation
fraction diff. pairs
0.0
10.0
0.0
1.0
true
false
"" ""
PENS
"interface" 1.0 0 -7500403 true "" "plot interface-density"

PLOT
1540
580
1880
765
Cluster sizes (log-log)
log10 size
log10 n(s)
0.0
1.0
0.0
1.0
true
false
"" ""
PENS
"n(s)" 1.0 0 -16777216 true "" "plot-cluster-dist"

PLOT
1540
770
1880
955
Environment std
generation
std(e)
0.0
10.0
0.0
1.0
true
false
"" ""
PENS
"env std" 1.0 0 -14835848 true "" "plot env-std"

@#$#@#$#@
## WHAT IS IT?

A faithful NetLogo replica of the **spatcoop** Python model
(`philkre-abm/src/spatcoop/model.py`, state of 2026-06-27).

Households sit on a torus lattice and pool contributions to maintain shared
flood defences. If a focal group of 5 (self + 4 von Neumann neighbours) pools
enough to clear a threshold **T = T-over-E × 5**, it is immune that season.
Otherwise it faces a linear flood probability `p = p-max*(1-e)/2` set by the
local defence environment **e**. Floods erode wealth and degrade defences,
feeding back into next season's risk — the **resilience-erosion trap**.

Three strategies compete:
- **UC** (green) — unconditional cooperator, always contributes `c-bar`.
- **CC** (orange) — conditional cooperator, matches neighbours' previous-round
  mean plus a loss-aversion premium.
- **D** (red) — defector, contributes nothing.

Strategies evolve via synchronous Fermi imitation of a random neighbour, with
mutation rate `mutation-rate`. Wealth follows a Wiener-with-drift (OU) process
`w ← w + b − contribution − flood-loss + N(0, sigma)`.

## INTERFACE LAYOUT

- **Top sliders** = the five parameters swept in the Snellius sensitivity
  analysis: `beta, p-max, T-over-E, b, eta` (plus `grid-size`, on its own slider
  and defaulted to 50 to keep it light).
- **Number inputs below** = the parameters held FIXED in the SA:
  `c-bar, loss-fraction, sigma, delta, gamma, kappa, mutation-rate,
  lambda-mean, lambda-sigma`, plus the `lambda-mode` and `display-mode` choosers.

## PHASE PRESETS

- **Cooperative phase** (default) — oscillatory regime, `mean-env` cycles
  0.3–0.9 and cooperation persists. NetLogo headline params: `b=21`,
  `c-bar/b ≈ 0.036`, `T-over-E=0.35`, `eta=0.005`, lognormal λ.
- **Collapse phase** — defection wins and `mean-env → −1`. The SA's low-income
  regime: `b=1`, `c-bar/b = 0.75`, so Fermi imitation drives cooperators extinct.

The single lever distinguishing the two is the cost-of-cooperation ratio
`c-bar / b`: cheap cooperation (low ratio) sustains the cooperative phase;
expensive cooperation (high ratio) collapses it.

## OUTPUT GRAPHS

All 14 SA order parameters are plotted live: strategy shares, cooperation,
resilience, flood rate, mean environment (+std), mean wealth (overall + per
strategy), wealth variance, Gini inequality, fitness/payoff, pool gap, spanning
and maximum cluster fractions, interface density, and the log-log
cooperator-cluster-size distribution (a straight line ⇒ power-law domains).

## CREDITS

Based on Ding (2024), Weitz et al. (2016), Jonsson & Jonsson (2025), and
Santos & Pacheco (2011). Agent-Based Modelling course, UvA/VU Amsterdam.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

circle
false
0
Circle -7500403 true true 0 0 300

square
false
0
Rectangle -7500403 true true 30 30 270 270
@#$#@#$#@
NetLogo 6.4.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="coop_phase" repetitions="1" runMetricsEveryStep="true">
    <setup>preset-cooperative</setup>
    <go>go</go>
    <timeLimit steps="200"/>
    <metric>mean-env</metric>
    <metric>coop-frac</metric>
    <metric>resilience</metric>
    <metric>flood-rate</metric>
    <metric>mean-wealth</metric>
    <metric>gini-wealth</metric>
  </experiment>
  <experiment name="collapse_phase" repetitions="1" runMetricsEveryStep="true">
    <setup>preset-collapse</setup>
    <go>go</go>
    <timeLimit steps="200"/>
    <metric>mean-env</metric>
    <metric>coop-frac</metric>
    <metric>resilience</metric>
    <metric>flood-rate</metric>
    <metric>mean-wealth</metric>
    <metric>gini-wealth</metric>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
