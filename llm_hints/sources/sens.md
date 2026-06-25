Sensitivity Analysis
How to perform comprehensive, efficient, and robust Sensitivity
Analysis?
Dr. Debraj Roy
June 9, 2026
ComputationalScienceLab

Table of contents
1. Introduction
2. Local Sensitivity analysis
3. The elementary effect method
4. Regression Based
1

Introduction

| Modelling     | & Simulation  |            |                       |
| ------------- | ------------- | ---------- | --------------------- |
| ”Essentially, | all models    | are wrong, | but some are useful.” |
| — Box, George | E. P.; Norman | R. Draper  | (1987). Empirical     |
Model-BuildingandResponseSurfaces, p. 424, Wiley. ISBN0471810339.
2

Case study of Covid
3

| Impact | of Uncertainty     | on CovidSim      | Predictions    |          | (1/3) |
| ------ | ------------------ | ---------------- | -------------- | -------- | ----- |
| •      | CovidSim           | Model:           |                |          |       |
|        | • Agent-based      | epidemiological  | model for      | COVID-19 | (UK)  |
|        | • 940 input        | parameters, many | with uncertain | values   |       |
| •      | Global Sensitivity | Analysis:        |                |          |       |
• Identified 19 critical parameters driving output uncertainty
|     | • Parametric | uncertainty increased | predictions | by up | to 300% |
| --- | ------------ | --------------------- | ----------- | ----- | ------- |
4

Role of Sensitivity Analysis (2/3)
5

| Role of Sensitivity | Analysis | (3/3)        |     |     |
| ------------------- | -------- | ------------ | --- | --- |
| • Sensitivity       | Analysis | in CovidSim: |     |     |
• Screened influential parameters, reducing computational burden
| • Highlighted  | model       | weaknesses | and areas needing | improvement |
| -------------- | ----------- | ---------- | ----------------- | ----------- |
| • Implications | for Policy: |            |                   |             |
• Overreliance on unvalidated parameters or scenarios can mislead
| • Need | for transparent | communication | of uncertainty |     |
| ------ | --------------- | ------------- | -------------- | --- |
• Conclusion:
| • Sensitivity | analysis | is vital |     |     |
| ------------- | -------- | -------- | --- | --- |
• Robust modeling requires addressing both parametric and structural
uncertainty
6

| Modelling | & Simulation |     |
| --------- | ------------ | --- |
Uncertainty analysis: Focuses on just quantifying the uncertainty in
model output.
Sensitivity analysis: The study of the relative importance of different
| input factors | on the model | output. |
| ------------- | ------------ | ------- |
7

Modelling & Simulation
The framework [2]
8

| Applications  | of sensitivity   | analysis       |
| ------------- | ---------------- | -------------- |
| Parameter     | prioritization   |                |
| which factors | determine output | the most       |
| Parameter     | fixing           |                |
| which factors | can be removed   | from the model |
| Parameter     | mapping          |                |
which factors are most important for causing good/bad outputs
9

Applications of GSA
10

| Applications | of GSA |     |     |
| ------------ | ------ | --- | --- |
• To quantify the variability in ABM outcomes resulting from model
parameters.
• To gain insight in how patterns and emergent properties are
| generated    | in the ABM;    |             |             |
| ------------ | -------------- | ----------- | ----------- |
| • To examine | the robustness | of emergent | properties; |
11

Types of sensitivity analysis
• Sensitivity analysis (SA) : quantification of the effects of changes or
uncertainties in a model’s input parameters on the model output
• Local SA: Consider only the effect of changes in individual
parameters
• Global SA: Consider the effects of changes in multiple parameters
simultaneously
12

| Types    | of sensitivity | analysis                      |     |         |
| -------- | -------------- | ----------------------------- | --- | ------- |
| Broadly, | these are      |                               |     |         |
| •        | Sensitivities  | based on one-factor-at-a-time |     | (OFAT); |
• Sensitivities based on model-based output variance decomposition.
• Sensitivities based on model-free output variance decomposition;
| •   | Sensitivities | based on density | functions. |     |
| --- | ------------- | ---------------- | ---------- | --- |
13

Local Sensitivity analysis

| Local sensitivity | analysis   |      |        |
| ----------------- | ---------- | ---- | ------ |
| Which             | parameters | when | nudged |
| will change       | the output |      | most?  |
(cid:12)
@f (cid:12)
(cid:12)
@(cid:18) (cid:18)0
i
14

Local sensitivity analysis
Two notable deficiencies of this definition of sensitivity are:
1. First, if f is nonlinear with respect to, then its partial derivative @f
@(cid:18)i
will change depending on where in the range of you choose to
measure.
2. Second, if there are interactions between model inputs, then @f will
@(cid:18)i
change depending on the values of the remaining input factors as
well.
In short, first partial derivatives are only a valid measure of sensitivity
when the model is linear, in which case @f will remain constant for any (cid:18)
@(cid:18)i i
15

| Local sensitivity | analysis:      | Ricker Model |
| ----------------- | -------------- | ------------ |
| The Ricker        | model is given | by:          |
N =N eq(1(cid:0)N t)
t+1 t c
where:
| • N is | the population | size at time t. |
| ------ | -------------- | --------------- |
t
| • q is the | intrinsic growth   | rate. |
| ---------- | ------------------ | ----- |
| • c is the | carrying capacity. |       |
16

| Local sensitivity | analysis: | Ricker Model |
| ----------------- | --------- | ------------ |
17

Local sensitivity analysis: Ricker Model
• The elasticities show that on long timescales, c is the only influential
parameter. On shorter time scales q and n are more influential.
0
• q does not influence the steady state,but influences strongly the
transient dynamics,especially at intermediat epopulation sizes
18

| Test Case Description |                  |        |
| --------------------- | ---------------- | ------ |
| • All decisions       | are stochastic   | [3]    |
| • Agents tend         | to harvest       | if :   |
| • internal            | energy is        | low    |
| • resource            | is abundant      |        |
| • other               | agents are close |        |
| • Agents move         | to sites         | with : |
| • abundant            | resource         |        |
| • few                 | agents           |        |
19

Input Parameters
• recommended to include all
input parameters
• parameters may have different
dimensions
20

Output Parameters
| • As main | output, we consider | the number | of agents n |
| --------- | ------------------- | ---------- | ----------- |
• ABMs produce large amounts of outputs on different levels (e.g.,
| system | level, agent level) |     |     |
| ------ | ------------------- | --- | --- |
• Multiple outputs may be considered separately during sensitivity
analysis
21

Default parameter setting
• First step in most SA methods is to choose a default parameter
setting
• This setting acts as a reference point to assess the effects of
parameter changes
• First, we run the model a number of times in the default setting
22

Model Output
23

| Histogram model     | runs          |     |
| ------------------- | ------------- | --- |
| • The distribution  | resembles     | a   |
| normal distribution |               |     |
| • A large number    | of replicates | is  |
| needed to estimate  | this          |     |
distribution
24

| OAT results | of r (resource | growth rate) |
| ----------- | -------------- | ------------ |
25

| OAT results | of r (resource | growth rate) |
| ----------- | -------------- | ------------ |
• The spread within replicates is small compared to the spread
between replicates (i.e. stochasticity has little influence).
• The effect of the parameter on the output is approximately linear
26

| OAT results | of D (Diffusion | coefficient) |
| ----------- | --------------- | ------------ |
27

OAT in 2D: Analyse This?
28

OAT in 3D: Analyse This?
29

Analyse This?
30

OAT is inefficient
| Can we analyse | influence         | of many |
| -------------- | ----------------- | ------- |
| parameters     | using few points? | [1]     |
3 points for each of 2 parameters.
Parameter effects are mixed (but
maybe we can un-mix them)
31

| Conclusions on | OFAT |     |
| -------------- | ---- | --- |
• OFAT is a good method for analysing the qualitative behaviour of
your ABM
| • It can detect | tipping points, | and other non-linearities |
| --------------- | --------------- | ------------------------- |
• OFAT presents a good trade-off between costs (time) and gains
| (model insight) | for ABM | goals |
| --------------- | ------- | ----- |
• Parameter effects are not readily comparable due to differences in
| dimensions       | and units |         |
| ---------------- | --------- | ------- |
| • No interaction | effects   | covered |
32

The elementary effect method

The elementary effect method
33

| The elementary effect | method      |                       |          |
| --------------------- | ----------- | --------------------- | -------- |
| Y(x ;:::;x            | ;x +∆       | ;x ;:::;x )(cid:0)Y(x | ;:::;x ) |
| EE = 1                | i(cid:0)1 i | i i+1 k               | 1 k :    |
i
∆
i
∑
r EEj
|     | (cid:22) = | j=1 i : |     |
| --- | ---------- | ------- | --- |
i
r
∑
r jEEjj
|     | (cid:22) (cid:3) = | j=1 i : |     |
| --- | ------------------ | ------- | --- |
i
r
∑
|     | r          | (EEj(cid:0)(cid:22))2 |     |
| --- | ---------- | --------------------- | --- |
|     | j=1        | i i                   |     |
|     | (cid:27) = | :                     |     |
|     | i          | r                     |     |
34

| The elementary | effect method |     |     |
| -------------- | ------------- | --- | --- |
1. if EE is non null, then X has an influence on the output [1],
| j   | j   |     |     |
| --- | --- | --- | --- |
2. if EE is non null and does not vary as X varies, therefore, X has a
| j   |     | j   | j   |
| --- | --- | --- | --- |
linear influence on the output and has no interactions with other
input factors,
3. if EE varies as X varies, then X affects non linearly the output with
| j   | j   | j   |     |
| --- | --- | --- | --- |
or without interactions.
35

| Morris Method:     | Steps (1/3)        |                  |                   |
| ------------------ | ------------------ | ---------------- | ----------------- |
| 1. Discretize      | the Input Space    |                  |                   |
| • Define           | the range for each | input parameter. |                   |
| • Discretize       | each parameter     | into a finite    | number of levels. |
| 2. Sample Starting | Points             |                  |                   |
• Randomly select several starting points in the input space.
| • Each | starting point is | a set of parameter | values. |
| ------ | ----------------- | ------------------ | ------- |
36

| Morris Method: | Steps        | (2/3) |     |     |
| -------------- | ------------ | ----- | --- | --- |
| 3. Generate    | Trajectories |       |     |     |
• For each starting point, create a trajectory by sequentially changing
| one        | parameter at     | a time (OAT). |                  |         |
| ---------- | ---------------- | ------------- | ---------------- | ------- |
| • Keep     | other parameters | fixed         | at their current | values. |
| 4. Compute | Elementary       | Effects       |                  |         |
• For each parameter change, calculate the elementary effect (EE):
|     |     |     | Change in | output |
| --- | --- | --- | --------- | ------ |
EE =
i
|          |          | Change         | in parameter | value       |
| -------- | -------- | -------------- | ------------ | ----------- |
| • Repeat | this for | each parameter | along the    | trajectory. |
37

| Morris Method: | Steps        | (3/3)        |       |                   |
| -------------- | ------------ | ------------ | ----- | ----------------- |
| 5. Repeat      | for Multiple | Trajectories |       |                   |
| • Repeat       | steps        | 2–4 several  | times | (typically 5–15). |
• This results in multiple EEs for each parameter, exploring different
| regions      | of the          | input    | space.   |     |
| ------------ | --------------- | -------- | -------- | --- |
| 6. Calculate | Sensitivity     | Measures |          |     |
| • For        | each parameter, |          | compute: |     |
• MeanoftheabsolutevaluesoftheEEs((cid:22)(cid:3)),indicatingoverall
influence.
• Standarddeviation((cid:27)),indicatingnonlinearityorinteraction.
| 7. Interpret | Results |     |     |     |
| ------------ | ------- | --- | --- | --- |
(cid:22)(cid:3)
| • Parameters |                   | with high | are     | influential.     |
| ------------ | ----------------- | --------- | ------- | ---------------- |
| • High       | (cid:27) suggests | nonlinear | effects | or interactions. |
This method is computationally efficient and well-suited for screening
| important factors | in  | models | with many | parameters[5][6][2]. |
| ----------------- | --- | ------ | --------- | -------------------- |
38

| Computational |             | Complexity     | of Morris  | Method                  |
| ------------- | ----------- | -------------- | ---------- | ----------------------- |
| •             | Complexity  | is linear in   | the number | of input parameters (k) |
| •             | Total model | runs required: |            |                         |
runs=r(cid:2)(k+1)
Total
where:
|     | • r = | number of trajectories | (typically | 5-15) |
| --- | ----- | ---------------------- | ---------- | ----- |
|     | • k = | number of input        | parameters |       |
• Runs grow proportionally with both parameters and trajectories
• Key advantage: More efficient than variance-based methods (e.g.,
|     |        | O(k2)     | O(k3)   |     |
| --- | ------ | --------- | ------- | --- |
|     | Sobol) | requiring | to runs |     |
39

| Objective: | Maximise | Trajectory | Spread |     |
| ---------- | -------- | ---------- | ------ | --- |
Goal: choosertrajectoriesfromapoolofMcandidatessotheyareasspreadapartas
possibleinthed-dimensionalinputspace.
| Objective | function |     |     |     |
| --------- | -------- | --- | --- | --- |
∑
|     |     | D(S) | = dj1j2 |     |
| --- | --- | ---- | ------- | --- |
2S
j1;j2
j1 ̸=j2
| whereS | istheselectedsubsetofsizer. |     |     |     |
| ------ | --------------------------- | --- | --- | --- |
Inter-trajectorydistance—eachtrajectoryjhas(d+1)pointsx(j);:::;x(j)
2Rd:
1 d+1
v
u
|     |     | u∑d+1∑d+1∑d | [                  | ]        |
| --- | --- | ----------- | ------------------ | -------- |
|     |     | t           | x( j1)(i)(cid:0)x( | j2)(i) 2 |
|     |     | dj1j2 =     | a                  |          |
b
|      |                | a=1b=1    | i=1        |                         |
| ---- | -------------- | --------- | ---------- | ----------------------- |
| • a: | pointindexinj1 | (1:::d+1) | Keyinsight |                         |
| • b: | pointindexinj2 | (1:::d+1) | dj1j2      | measuresdistancebetween |
entiretrajectories,notjust
| • i: parameterdimension |                          | (1:::d) |                 |     |
| ----------------------- | ------------------------ | ------- | --------------- | --- |
| • Innersum:             | squaredEuclideandistance |         | startingpoints. |     |
betweenapairofpoints
accumulatesoverall(d+1)2 40
• Doublesum:

Example
| Concrete example     | (d=2, each | trajectory       | has 3 points): |
| -------------------- | ---------- | ---------------- | -------------- |
| j1: f(0;0); (0:5;0); | (0:5;0:5)g |                  |                |
| f(1;1);              | (0:5;0:5)g | O u tersumforr=4 |                |
| j2: (0:5;1);         |            | ( )              |                |
|                      |            | 4                | =6pairs:       |
| Paira=1;b=1:         |            | 2                |                |
D(S)=d12+d13+d14+d23+d24+d34
(0(cid:0)1)2+(0(cid:0)1)2=2
|     |     | Forcesevery | pairtobefarapart |
| --- | --- | ----------- | ---------------- |
Repeatforall3(cid:2)3=9pairs,sum,take
| p   |     | simultaneously—greedysearchcannot |     |
| --- | --- | --------------------------------- | --- |
.
guaranteethis.
| Twoclusteredtrajectories)smalldj1j2 |     | .   |     |
| ----------------------------------- | --- | --- | --- |
Originvs.corner(1;1;:::;1))large
dj1j2 .
41

| The elementary | effect method |     |
| -------------- | ------------- | --- |
It is not possible with Morris method to distinguish between non linearity
| and the interactions | with other input | factors. |
| -------------------- | ---------------- | -------- |
42

The elementary effect method
43

Regression Based

| Regression-Based |                  | Sensitivity | Analysis | for ABMs | (1/3) |
| ---------------- | ---------------- | ----------- | -------- | -------- | ----- |
| 1.               | Design Parameter | Sampling    |          |          |       |
• Perform global sampling (e.g., Latin Hypercube, Sobol sequences)
|     | across  | the parameter        | space.      |              |        |
| --- | ------- | -------------------- | ----------- | ------------ | ------ |
|     | • For k | parameters, generate | N parameter | combinations | (e.g., |
N=1000).
| 2.  | Run Simulations | and Collect | Outputs        |              |     |
| --- | --------------- | ----------- | -------------- | ------------ | --- |
|     | • Execute       | the ABM for | each parameter | combination. |     |
• Record summary statistics (e.g., agent population size, resource
|     | utilization) | as model | outputs. |     |     |
| --- | ------------ | -------- | -------- | --- | --- |
• Repeat simulations to account for stochasticity (e.g., 10 runs per
|     | parameter | set). |     |     |     |
| --- | --------- | ----- | --- | --- | --- |
44

| Regression-Based |                | Sensitivity |     | Analysis | for | ABMs (2/3) |
| ---------------- | -------------- | ----------- | --- | -------- | --- | ---------- |
| 3.               | Fit Regression | Models      |     |          |     |            |
• Use linear or nonlinear regression to relate parameters (X) to outputs
(Y):
|     |                | Y=(cid:12) | +(cid:12) | X +(cid:12)  | X +(cid:1)(cid:1)(cid:1)+(cid:12) | X +ϵ |
| --- | -------------- | ---------- | --------- | ------------ | --------------------------------- | ---- |
|     |                |            | 0         | 1 1          | 2 2                               | k k  |
|     | • Standardized | Regression |           | Coefficients | (SRCs):                           |      |
(cid:27)
|     |     |     |     | SRC | =(cid:12) (cid:1) Xi |     |
| --- | --- | --- | --- | --- | -------------------- | --- |
i i (cid:27)
Y
|     | Higher | absolute | SRCs indicate | greater | sensitivity. |     |
| --- | ------ | -------- | ------------- | ------- | ------------ | --- |
(R2):
|     | • Coefficient | of Determination |           |     | Measures | how well the model |
| --- | ------------- | ---------------- | --------- | --- | -------- | ------------------ |
|     | explains      | output           | variance. |     |          |                    |
45

| Regression-Based |     |         | Sensitivity     |         | Analysis      | for ABMs (3/3)    |
| ---------------- | --- | ------- | --------------- | ------- | ------------- | ----------------- |
|                  | 4.  | Compute | Sensitivity     | Indices |               |                   |
|                  |     | • Main  | Effect Indices: | Use     | SRCs directly | to rank parameter |
importance.
• Variance-Based Indices: For nonlinear models, apply Sobol’ indices
|     |     | via regression |            | metamodels | to decompose      | output variance into |
| --- | --- | -------------- | ---------- | ---------- | ----------------- | -------------------- |
|     |     | individual     | parameters |            | and interactions. |                      |
|     | 5.  | Validate and   | Interpret  |            | Results           |                      |
• Check regression assumptions (linearity, homoscedasticity) and refine
|     |     | models | if needed. |     |     |     |
| --- | --- | ------ | ---------- | --- | --- | --- |
• Use visualization tools (e.g., scatterplots, interaction plots) to
|     |     | identify | nonlinear | relationships | or parameter | thresholds. |
| --- | --- | -------- | --------- | ------------- | ------------ | ----------- |
46

| Regression     | based  |                            |
| -------------- | ------ | -------------------------- |
| The regression | method | has three main advantages: |
1. it explores the entire interval of definition of each factor;
2. each ’factor effect’ is averaged over that of the other factors;
3. standardized regression coefficients give also the sign of the effect of
| a input | factor on the | output. |
| ------- | ------------- | ------- |
47

References I
Andrea Saltelli and Paola Annoni. “How to avoid a perfunctory
sensitivity analysis”. In: Environmental Modelling & Software 25.12
| (2010), pp. | 1508–1517. |     |     |     |
| ----------- | ---------- | --- | --- | --- |
Andrea Saltelli et al. “Why so many published sensitivity analyses
are false: A systematic review of sensitivity analysis practices”. In:
| Environmental | modelling      | & software | 114 (2019), | pp. 29–39.  |
| ------------- | -------------- | ---------- | ----------- | ----------- |
| Guus Ten      | Broeke, George | Van Voorn, | and Arend   | Ligtenberg. |
“Which sensitivity analysis method should I use for my agent-based
model?” In: Journal of Artificial Societies and Social Simulation
| 19.1 (2016), | p. 5. |     |     |     |
| ------------ | ----- | --- | --- | --- |
48
