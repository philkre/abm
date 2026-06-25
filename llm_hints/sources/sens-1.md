| Global Sensitivity    | Analysis       |                |               |
| --------------------- | -------------- | -------------- | ------------- |
| How to perform        | comprehensive, | efficient, and | robust Global |
| Sensitivity Analysis? |                |                |               |
Debraj Roy
June 10, 2026
ComputationalScienceLab,UniversityofAmsterdam

Table of contents
1. Introduction
2. Variance-based Sensitivity Indices
3. Estimating Sensitivity Indicies
4. High Dimensional Model decomposition
5. Density based methods
6. Looking Forward
1

Introduction

| Basic local | sensitivity |     |     |
| ----------- | ----------- | --- | --- |
Idea: quantify how a model output changes near a reference parameter
setting.
| For a model | output |     |     |
| ----------- | ------ | --- | --- |
Y=f((cid:2));
(cid:2)(cid:3)
and a focal parameter (cid:2), i the local sensitivity at a reference setting is
| often written | as  | (cid:12) |     |
| ------------- | --- | -------- | --- |
(cid:12)
@f((cid:2))(cid:12)
|     | Slocal | =   | :   |
| --- | ------ | --- | --- |
i (cid:12)
@(cid:2)
i (cid:2)=(cid:2)(cid:3)
Pros
| • Simple | and easy to interpret. |     |     |
| -------- | ---------------------- | --- | --- |
Cons
| • Cannot | handle strong non-linearity | well.           |             |
| -------- | --------------------------- | --------------- | ----------- |
| • Does   | not capture interaction     | effects between | parameters. |
2

| OAT / OFAT | design |     |     |     |
| ---------- | ------ | --- | --- | --- |
Idea: vary one parameter at a time around a baseline while holding all
others fixed.
| A typical design | is      |                            |                     |      |
| ---------------- | ------- | -------------------------- | ------------------- | ---- |
|                  |         | 2f(cid:2) (cid:3)(cid:0)∆; | (cid:3) (cid:3)     | +∆g; |
|                  | (cid:2) | i                          | i (cid:2) ; (cid:2) | i    |
|                  |         | i                          | i i                 |      |
| =(cid:2)(cid:3)  | j̸=i.   |                            |                     |      |
| while (cid:2)    | for all |                            |                     |      |
| j                | j       |                            |                     |      |
Pros
| • Can detect | tipping | points | and other non-linearities. |     |
| ------------ | ------- | ------ | -------------------------- | --- |
• Good trade-off between computational cost and model insight.
Cons
| • Still local,   | so it misses | most | of the parameter | space. |
| ---------------- | ------------ | ---- | ---------------- | ------ |
| • No interaction | effects      | are  | covered.         |        |
3

Elementary effects (Morris)
Idea: estimate the effect of changing one factor over many points in the
input space.
For step size ∆, an elementary effect for parameter (cid:2) is
i
f((cid:2) ;:::;(cid:2) +∆;:::;(cid:2) )(cid:0)f((cid:2))
EE((cid:2))= 1 i k :
i ∆
Across many trajectories, one often summarizes with (cid:22)(cid:3) and (cid:27).
i i
Pros
• Can help separate a strong main effect from evidence of interaction
or non-linearity.
Cons
• Morris cannot distinguish non-linearity from interactions with other
input factors.
4

| Regression-based | sensitivity |     |
| ---------------- | ----------- | --- |
Idea: sample the parameter space and regress output on inputs.
| A common formulation | is  |     |
| -------------------- | --- | --- |
∑k
|     |     | Y=(cid:12) + (cid:12)(cid:2) +"; |
| --- | --- | -------------------------------- |
0 i i
i=1
with standardized regression coefficients used for comparison across
factors.
Pros
• Each factor effect is averaged over the effects of the other factors.
• Standardized regression coefficients also provide the sign of the
| effect of | an input factor | on the output. |
| --------- | --------------- | -------------- |
Cons
| • Assumes | a model. |     |
| --------- | -------- | --- |
5

| Global Sensitivity | Analysis    | (GSA)             |                |
| ------------------ | ----------- | ----------------- | -------------- |
| To understand      | GSA we need | to be clear about | the following: |
| • The shortcomings | of          | OFAT              |                |
| • The objective    | of GSA      |                   |                |
| • Formulation      | of GSA      |                   |                |
Note: For this lecture I will use the term parameters/factors/input
interchangebly.
6

| Global sensitivity | analysis   |          |       |
| ------------------ | ---------- | -------- | ----- |
| Which              | parameters | are most |       |
| significant        | over the   | entire   | input |
range?
7

Applications of GSA
8

| “Good” global | sensitivity | index | should satisfy |
| ------------- | ----------- | ----- | -------------- |
• To be global, i.e. to consider parameter variations in the entire
| feasible     | space.        |                 |                      |
| ------------ | ------------- | --------------- | -------------------- |
| • To be      | quantitative, | i.e. computable | through a numerical, |
| reproducible | procedure.    |                 |                      |
• To be model independent, i.e. applicable independently of the form
of the input–output relationship , e.g. linear or non-linear, additive
| or non-additive, | etc.                |                |              |
| ---------------- | ------------------- | -------------- | ------------ |
| • To be          | unconditional       | on any assumed | input value. |
| • To be          | easy to interpret,  | compute        | and stable.  |
| • To be          | moment-independent. |                |              |
9

Variance-based Sensitivity
Indices

| Conditional | Variance       |     |     |
| ----------- | -------------- | --- | --- |
| Consider    | a model:       |     |     |
| Y=f(X       | ;X ;X ;:::::;X | )   |     |
| 1           | 2 3            | k   |     |
What would happen to the uncertainty of Y if we could fix a factor.
x(cid:3)
| Imagine that | we fix factor | X at a particular | value . |
| ------------ | ------------- | ----------------- | ------- |
|              |               | i                 | i       |
10

Conditional Variance
Y=f(X ;X ;X ;:::::;X )
1 2 3 k
Let V
X(cid:24)i
(YjX
i
=x(cid:3)
i
) be the resulting variance of Y, taken over X(cid:24)i (all
factors but X). We call this a conditional variance, as it is conditional on
i
X being fixed to x(cid:3).
i i
11

| Conditional | Variance    |     |     |     |
| ----------- | ----------- | --- | --- | --- |
| Y=f(X ;X    | ;X ;:::::;X | )   |     |     |
| 1           | 2 3 k       |     |     |     |
We would imagine that, having frozen one potential source of variation
(YjX =x(cid:3))
| (X), the resulting | variance               | V            | will be less than | the |
| ------------------ | ---------------------- | ------------ | ----------------- | --- |
| i                  |                        | X(cid:24)i i | i                 |     |
| corresponding      | total or unconditional | variance     | V(Y)              |     |
12

| Conditional | Variance       |     |     |     |     |
| ----------- | -------------- | --- | --- | --- | --- |
| Y=f(X       | ;X ;X ;:::::;X | )   |     |     |     |
| 1           | 2 3            | k   |     |     |     |
V (YjX =x(cid:3)) could be a potential indicator of sensitivity of parameter
| X(cid:24)i | i i |     |     |     |     |
| ---------- | --- | --- | --- | --- | --- |
(YjX =x(cid:3)),
| X, reasoning | that the smaller | the remaining | variance | - V          |     |
| ------------ | ---------------- | ------------- | -------- | ------------ | --- |
| i            |                  |               |          | X(cid:24)i i | i   |
| the greater  | the influence    | of X. i       |          |              |     |
13

Conditional Variance
| Y=f(X ;X | ;X ;:::::;X ) |     |
| -------- | ------------- | --- |
| 1 2      | 3 k           |     |
There are few problem though in using V (YjX =x(cid:3))  as a measure
X(cid:24)i i i
for sensitivity:
• First, it makes the sensitivity measure dependent on the position of
| point x(cid:3) | for each input factor, | which is impractical |
| -------------- | ---------------------- | -------------------- |
i
• one can design a model that for particular factors X i and fixed point
| x(cid:3) yields | V (YjX =x(cid:3))>V(Y)  |     |
| --------------- | ----------------------- | --- |
| i               | X(cid:24)i i i          |     |
14

| Conditional | Variance |     |     |     |
| ----------- | -------- | --- | --- | --- |
Solution:
• If we take instead the average of this measure over all possible
|        | x(cid:3)         | x(cid:3)will |            |     |
| ------ | ---------------- | ------------ | ---------- | --- |
| points | , the dependence | on           | disappear. |     |
|        | i                | i            |            |     |
=x(cid:3)))
| • We write | this as E (V | (YjX         | This is always | lower or equal |
| ---------- | ------------ | ------------ | -------------- | -------------- |
|            | Xi           | X(cid:24)i i | i              |                |
to V(Y)
15

| Conditional Variance |     |     |     |
| -------------------- | --- | --- | --- |
Solution:
• If we take instead the average of this measure over all possible
| x(cid:3) |                  | x(cid:3)will |            |
| -------- | ---------------- | ------------ | ---------- |
| points   | , the dependence | on           | disappear. |
|          | i                | i            |            |
• We write this as E (V (YjX))  . This is always lower or equal to
|     | Xi  | X(cid:24)i i |     |
| --- | --- | ------------ | --- |
V(Y)
|                   | (YjX))+V  | (YjX))=V(Y)     |          |
| ----------------- | --------- | --------------- | -------- |
| E (V              |           | (E              |          |
| Xi X(cid:24)i     | i Xi      | X(cid:24)i i    |          |
| See lecture notes | for proof | of Law of Total | Variance |
16

| First-order | Sensitivity | Index |
| ----------- | ----------- | ----- |
V (E (YjX))
| S   | = Xi X(cid:24)i | i ;0(cid:20)S (cid:20)1 |
| --- | --------------- | ----------------------- |
| i   |                 | i                       |
V(Y)
A high value signals an important variable. And vice versa? Does a small
| value | of S i flag a non-important | variable? |
| ----- | --------------------------- | --------- |
17

| Higher-order | Sensitivity | Indices |
| ------------ | ----------- | ------- |
We continue our game with conditioned variances by playing with two
| factors instead | of one. |     |
| --------------- | ------- | --- |
(YjX;X))
| V Xi;Xj | (E X(cid:24)ij i | j   |
| ------- | ---------------- | --- |
V(Y)
18

| Higher-order | Sensitivity | Indices |
| ------------ | ----------- | ------- |
We continue our game with conditioned variances by playing with two
| factors instead | of one. |        |
| --------------- | ------- | ------ |
| V(E(YjX;X))=V   |         | +V +V  |
|                 | i j     | i j ij |
The term V is the interaction term between factors X;X . It captures
ij i j
that part of the response of Y to X;X that cannot be written as a
i j
| superposition | of effects | separately due to X;X |
| ------------- | ---------- | --------------------- |
i j
19

| Total-order | Sensitivity | Indices |
| ----------- | ----------- | ------- |
What is a total effect term? Let us again use our model, and ask what
| we would   | obtain if we        | were to compute: |
| ---------- | ------------------- | ---------------- |
| E(cid:24)i | (V (YjX(cid:24)i )) |                  |
Xi
V(Y)

20

| Total-order | Sensitivity | Indices |
| ----------- | ----------- | ------- |
What is a total effect term? Let us again use our model, and ask what
| we would | obtain if we | were to compute: |
| -------- | ------------ | ---------------- |
(YjX(cid:24)i
| E(cid:24)i | (V Xi )) |     |
| ---------- | -------- | --- |
V(Y)

We are conditioning now on all factors but  X. In other words, we ask
i
the question what variance would remain if we fix everything but X.
i
21

| Total-order | Sensitivity | Indices |
| ----------- | ----------- | ------- |
What is a total effect term? Let us again use our model, and ask what
| we would | obtain if we | were to compute: |
| -------- | ------------ | ---------------- |
(YjX(cid:24)i
|     | V X(cid:24)i (E | Xi )) |
| --- | --------------- | ----- |
| S   | =1(cid:0)       |       |
| Ti  | V(Y)            |       |

We are conditioning now on all factors but  X. In other words, we ask
i
the question what variance would remain if we fix everything but X.
i
22

| Total-order | Sensitivity |     | Indices |     |     |
| ----------- | ----------- | --- | ------- | --- | --- |
To consider a different example, for a generic three-factor model, one
| would | have: |     |     |     |     |
| ----- | ----- | --- | --- | --- | --- |
(YjX(cid:24)1
|     |             | V (E       | ))  |          |        |
| --- | ----------- | ---------- | --- | -------- | ------ |
|     | S =1(cid:0) | X(cid:24)1 | X1  | =S +S +S | +S     |
|     | T1          |            |     | 1 12     | 13 123 |
V(Y)

23

| First-Order | Sensitivity                    | Index  |
| ----------- | ------------------------------ | ------ |
| ∑           | ∑                              |        |
| d S         | + d S +(cid:1)(cid:1)(cid:1)+S | =1     |
| i=1         | i i<j ij                       | 12:::d |
24

| Total-order | Sensitivity | Index |
| ----------- | ----------- | ----- |
∑
| d S | (cid:21)1 |     |
| --- | --------- | --- |
| i=1 | Ti        |     |
25

| Estimating | Sensitivity | Indicies |
| ---------- | ----------- | -------- |

| Estimating Sensitivity |             |           |     |
| ---------------------- | ----------- | --------- | --- |
| Consider a model       | with random | inputs:   |     |
|                        | y=f(X       | ;X ;:::;X | ):  |
|                        |             | 1 2 k     |     |
Assume the factors X ;:::;X are independent random variables. Then
|     | 1   | k   |     |
| --- | --- | --- | --- |
the joint probability density function of the factors factorizes as:
∏k
|     | p X1;:::;Xk | (x 1 ;:::;x k )= | p(x): i i |
| --- | ----------- | ---------------- | --------- |
i=1
Interpretation: the probability of seeing a particular combination
(x ;:::;x ) is the product of the individual densities, because the inputs
1 k
are independent.
26

| Expectation | and | Variance |     |     |     |     |
| ----------- | --- | -------- | --- | --- | --- | --- |
Mean and variance of y can be written as multidimensional integrals.
| Expectation | (mean | output): |     |     |     |     |
| ----------- | ----- | -------- | --- | --- | --- | --- |
∫ ∫
∏k
|     | E(y)= |     | (cid:1)(cid:1)(cid:1) |               |     |     |
| --- | ----- | --- | --------------------- | ------------- | --- | --- |
|     |       |     | f(x 1 ;:::;x          | k ) p(x)dx: i | i i |     |
i=1
| Variance | (spread | of the                | output):   |                |        |     |
| -------- | ------- | --------------------- | ---------- | -------------- | ------ | --- |
|          |         | ∫ ∫                   |            |                | ∏k     |     |
|          |         |                       | (          | )              |        |     |
|          |         | (cid:1)(cid:1)(cid:1) |            | )(cid:0)E(y) 2 |        |     |
|          | Var(y)= |                       | f(x ;:::;x |                | p(x)dx |     |
|          |         |                       | 1          | k              | i i i  |     |
i=1
∫ ∫
∏k
|     |     | (cid:1)(cid:1)(cid:1) |              | )2           | (cid:0) E(y)2: |     |
| --- | --- | --------------------- | ------------ | ------------ | -------------- | --- |
|     | =   |                       | f(x 1 ;:::;x | k p(x)dx i i | i              |     |
i=1
This uses the identity Var(Y)=E[Y2](cid:0)(E[Y])2, where both
∏
| expectations | are computed |     | with the same | joint pdf | p (x ). | 27  |
| ------------ | ------------ | --- | ------------- | --------- | ------- | --- |
i i i

| Conditional | Variance |     |     |     |     |     |
| ----------- | -------- | --- | --- | --- | --- | --- |
If one of the input factors x j is fixed to a generic value x~ j , the resulting
| variance | of y will be | equal to: |     |     |     |     |
| -------- | ------------ | --------- | --- | --- | --- | --- |
∫ ∫
∏k
| V(yjx | (cid:1)(cid:1)(cid:1) |         |             | )(cid:0)E(yjx |               |     |
| ----- | --------------------- | ------- | ----------- | ------------- | ------------- | --- |
| =x~)= |                       | (f(X ;X | ;X ;:::::;X |               | =x~))2 p(x)dx |     |
| j     | j                     | 1       | 2 3         | k             | j j i         | i i |
k
i=1
i̸=j
∫ ∫
∏k
= (cid:1)(cid:1)(cid:1) f2(X ;X ;X ;:::::;X ) p(x)dx (cid:0)E2(yjx =x~)
|     |     | 1   | 2 3 | k   | i i i j | j   |
| --- | --- | --- | --- | --- | ------- | --- |
|     |     | k   |     | i=1 |         |     |
i̸=j
28

| Estimating | First-order | Sensitivity |     |     |
| ---------- | ----------- | ----------- | --- | --- |
For the purpose of sensitivity analysis one is interested in eliminating the
V(yjx
dependence upon the value x~ j by integrating j =x~) j over the
| probability | density function | of x , obtaining: |     |     |
| ----------- | ---------------- | ----------------- | --- | --- |
j
∫ ∫
∏k
E(V(yjx))= (cid:1)(cid:1)(cid:1) f2(X ;X ;X ;:::::;X ) p(x)dx(cid:0)
|     | j   | 1 2 3 | k i | i i |
| --- | --- | ----- | --- | --- |
|     | ∫   | k     | i=1 |     |
E2(yjx =x~)p(x)dx
|     |     | j j j j j |     |     |
| --- | --- | --------- | --- | --- |
29

| Estimating | First-order |                       | Sensitivity |         |                |          |              |
| ---------- | ----------- | --------------------- | ----------- | ------- | -------------- | -------- | ------------ |
|            |             | ∫                     | ∫           |         |                | ∏k       |              |
|            |             | (cid:1)(cid:1)(cid:1) | f2(X        |         |                |          | (cid:0)E2(y) |
|            | V(y)=       |                       | 1           | ;X 2 ;X | 3 ;:::::;X k ) | p(x)dx i | i i          |
|            |             |                       | k           |         |                | i=1      |              |
|            |             |                       | ∫ ∫         |         |                |          |              |
∏k
E(V(yjx))= (cid:1)(cid:1)(cid:1) f2(X ;X ;X ;:::::;X ) p(x)dx(cid:0)
|     |     | j   |     | 1   | 2 3 | k   | i i i |
| --- | --- | --- | --- | --- | --- | --- | ----- |
k
|     |     | ∫   |                   |     |     | i=1 |     |
| --- | --- | --- | ----------------- | --- | --- | --- | --- |
|     |     |     | E2(yjx =x~)p(x)dx |     |     |     |     |
|     |     |     | j                 | j j | j j |     |     |
We have dropped the dependence x~ j due to the integration, therefore:
∫
|     | V(y)(cid:0)E(V(yjx))= |     |     | E2(yjx | =x~)p(x)dx |       | (cid:0)E2(y) |
| --- | --------------------- | --- | --- | ------ | ---------- | ----- | ------------ |
|     |                       |     | j   |        | j          | j j j | j            |
30

| Estimating | First-order | Sensitivity |     |     |
| ---------- | ----------- | ----------- | --- | --- |
We have dropped the dependence x~ due to the integration, therefore:
j
∫
|     | V(y)(cid:0)E(V(yjx))= | E2(yjx | =x~)p(x)dx | (cid:0)E2(y) |
| --- | --------------------- | ------ | ---------- | ------------ |
|     |                       | j      | j j j      | j j          |
(YjX))
The left-hand side of the above equation is also equal to V Xi (E X(cid:24)i i
and is a good measure of the sensitivity of y with respect to factor x . If
j
one divides it by the unconditional variance V(y), one obtains the
| so-called | first-order sensitivity | index: |     |     |
| --------- | ----------------------- | ------ | --- | --- |
V (E (YjX))
| S   | = Xi X(cid:24)i | i ;0(cid:20)S (cid:20)1 |     |     |
| --- | --------------- | ----------------------- | --- | --- |
| i   |                 | i                       |     |     |
V(Y)
31

| Estimating | First-order | Sensitivity |     |     |
| ---------- | ----------- | ----------- | --- | --- |
∫
|     | V(y)(cid:0)E(V(yjx))= | E2(yjx | =x~)p(x)dx | (cid:0)E2(y) |
| --- | --------------------- | ------ | ---------- | ------------ |
|     |                       | j      | j j j      | j j          |
The ∫ the computational question reduces to estimating the integral
| E2(yjx | =x~)p(x)dx |     |     |     |
| ------ | ---------- | --- | --- | --- |
|        | j j j j    | j   |     |     |
32

| Estimating | First-order | Sensitivity |     |     |     |
| ---------- | ----------- | ----------- | --- | --- | --- |
∫
| E2(yjx | =x~)p(x)dx |       | =   |     |     |
| ------ | ---------- | ----- | --- | --- | --- |
|        | j j        | j j j |     |     |     |
|        | 8          |       |     |     | 9   |
2
|     | ∫ ><∫ | ∫   |     |     | >=  |
| --- | ----- | --- | --- | --- | --- |
∏k
|     |     | (cid:1)(cid:1)(cid:1) | f(x ;x ;x ;:::::;x | ) p(x)dx | p(x)dx      |
| --- | --- | --------------------- | ------------------ | -------- | ----------- |
|     | >:  |                       | 1 2 3              | k i      | i i>; j j j |
i=1
i̸=j
See Lecture notes Monte Carlo Basics: Estimating the Square of the
| Mean | via Monte Carlo |     |     |     |     |
| ---- | --------------- | --- | --- | --- | --- |
33

| Estimating | First-order |     | Sensitivity |     |     |     |     |     |
| ---------- | ----------- | --- | ----------- | --- | --- | --- | --- | --- |
∫
E2(yjx =x~)p(x)dx
|     |     | j j | j j | j   |     |     |      |     |
| --- | --- | --- | --- | --- | --- | --- | ---- | --- |
|     |     | 8   |     |     |     |     | 9    |     |
|     |     | ><∫ |     |     |     |     | >= 2 |     |
|     | ∫   |     | ∫   |     | ∏k  |     |      |     |
(cid:1)(cid:1)(cid:1)
|     | =   |     | f(x | 1 ;x 2 ;x 3 ;:::::;x | k ) | p(x)dx i i | i>; p(x)dx | j j j |
| --- | --- | --- | --- | -------------------- | --- | ---------- | ---------- | ----- |
>:
i=1
i̸=j
∫ ∫
∏k
|     |     | =   | (cid:1)(cid:1)(cid:1) | f(x ;x ;x | ;:::::;x | ) p(x)dx |     |     |
| --- | --- | --- | --------------------- | --------- | -------- | -------- | --- | --- |
|     |     |     |                       | 1 2       | 3        | k i      | i i |     |
i=1
i̸=j
∏k
|     |     |     |     | ′      | ′ ′         | ′   | ′              | ′     |
| --- | --- | --- | --- | ------ | ----------- | --- | -------------- | ----- |
|     |     |     |     | f(x ;x | ;x ;:::::;x | )   | p(x)dxp(x)dx i | j j j |
|     |     |     |     | 1      | 2 3         | k   | i              | i     |
i=1
i̸=j
See Lecture notes Monte Carlo Basics: Estimating the Square of the
| Mean | via Monte | Carlo |     |     |     |     |     |     |
| ---- | --------- | ----- | --- | --- | --- | --- | --- | --- |
34

| Estimating | First-order | Sensitivity |     |     |     |
| ---------- | ----------- | ----------- | --- | --- | --- |
∫
E2(yjx =x~)p(x)dx
|     | j j | j j j |     |     |     |
| --- | --- | ----- | --- | --- | --- |
|     | 8   |       |     | 9   |     |
2
|     | ∫ ><∫ | ∫   |     | >=  |     |
| --- | ----- | --- | --- | --- | --- |
∏k
(cid:1)(cid:1)(cid:1)
|     | =   | f(x ;x ;x ;:::::;x | ) p(x)dx | p(x)dx    |     |
| --- | --- | ------------------ | -------- | --------- | --- |
|     | >:  | 1 2 3              | k i      | i i>; j j | j   |
i=1
i̸=j
|     | ∫ ∫ |     |     |     |     |
| --- | --- | --- | --- | --- | --- |
|     |     |     |     | ∏k  | ∏k  |
= (cid:1)(cid:1)(cid:1) f(x ;x ;::;x~;::;x )f(x ′ ;x ′ ;:::;x~;::;x ′ ) p(x)dx p(x ′ )dx ′
|     | 1 2 | j k 1 | 2 j k | i i i | i i i |
| --- | --- | ----- | ----- | ----- | ----- |
i=1 i=1
i̸=j
35

| Estimating | First-order | Sensitivity |     |     |
| ---------- | ----------- | ----------- | --- | --- |
The integral can be computed using a single Monte Carlo loop. The
Monte Carlo procedure that follows was proposed by Saltelli et al. Two
| input | sample matrices | A and B are generated: |         |     |
| ----- | --------------- | ---------------------- | ------- | --- |
|       | 2               | 3                      | 2       | 3   |
|       |                 |                        | x′      | x′  |
|       | x               | ::: x                  | :::     |     |
|       | 11              | 1k                     | 11      | 1k  |
|       | 6 .             | ... 7                  | 6 . ... | . 7 |
|       | A= 4 .          | 5 B=                   | 4 .     | . 5 |
|       | .               |                        | .       | .   |
|       | x               | x                      | x′ :::  | x′  |
|       | n1              | nK                     | n1      |     |
nk
36

| Estimating | First-order  | Sensitivity       |     |     |
| ---------- | ------------ | ----------------- | --- | --- |
| Then       | a new matrix | Bj can be defined | as: |     |
A
|     |     | 2       |              | 3   |
| --- | --- | ------- | ------------ | --- |
|     |     | x′ x′   | ::: x :::    | x′  |
|     |     | 11      | 12 1j        | 1k  |
|     |     | 6 .     | ...          | 7   |
|     | Bj  | = 4 .   |              | 5   |
|     |     | A . ::: |              |     |
|     |     | x′ x′   |              | x′  |
|     |     |         | ::: x nj ::: |     |
|     |     | n1      | n2           | nk  |
If one thinks of matrix A as the “sample” matrix, and of B as the
“re-sample” matrix, then Bj a matrix where all factors except x are
|     |     | A   |     | j   |
| --- | --- | --- | --- | --- |
re-sampled.
37

| Estimating | First-order | Sensitivity |     |     |
| ---------- | ----------- | ----------- | --- | --- |
|            | ∫           |             | ∑n  |     |
1
|     | E2(yjx |                  |       | f(A)f(Bj |
| --- | ------ | ---------------- | ----- | -------- |
|     |        | j =x~)p(x)dx j j | j j = | i ) i    |
|     |        |                  | n     | A        |
i=1
∑n
1
|     |     | E2(y)= | f(A)f(B) |     |
| --- | --- | ------ | -------- | --- |
|     |     |        | i        | i   |
n
i=1
In this way the computational cost associated with a full set of first order
| indices | S i is n(k+2). |     |     |     |
| ------- | -------------- | --- | --- | --- |
38

| Estimating | Total-order             | Sensitivity      |
| ---------- | ----------------------- | ---------------- |
|            | V (E                    | (YjX(cid:24)i )) |
|            | =1(cid:0) X(cid:24)i Xi |                  |
S Ti
V(Y)
|   We | need to estimate | V (E (YjX(cid:24)i )) |
| ---- | ---------------- | --------------------- |
X(cid:24)i Xi
39

Estimating Total-order Sensitivity
∫
∑n
1
E2(yjx =(cid:24)x~)p((cid:24)x~)d((cid:24)x ~ )= f(B)f(Bj )
j j j j j n i A i
i=1
∑n
1
E2(y)= f(A)f(B)
n i i
i=1
Homework: Work it out yourself. What is the computational cost?
40

| Estimating | Sensitivity | - Example |     |
| ---------- | ----------- | --------- | --- |
Generate an N x 2d sample matrix, i.e. each row is a sample point in the
| hyperspace | of 2d dimensions. | Sample from | pdf Sobol 2001. |
| ---------- | ----------------- | ----------- | --------------- |
41

| Estimating | Sensitivity | - Example |
| ---------- | ----------- | --------- |
Use the first d columns of the matrix as matrix A, and the remaining d
| columns | as matrix B. |     |
| ------- | ------------ | --- |
42

Estimating Sensitivity - Example
Build d further N x d matrices Ai , for i = 1,2,...,d, such that the ith
B
column of Ai = the ith column of B, and the remaining columns arefrom
B
43
A.

| Estimating | Sensitivity | - Example |
| ---------- | ----------- | --------- |
N(d+2) points in the input space (one for each row).corresponding f(A),
| f(B) and | f(Ai ) values. |     |
| -------- | -------------- | --- |
B
44

| Estimating        | Sensitivity    | - Example      |                  |     |
| ----------------- | -------------- | -------------- | ---------------- | --- |
|                   |                | ∑              | ( ( )            | )   |
| Var (E            | (YjX))(cid:25) | 1 N f(B)       | f Ai (cid:0)f(A) |     |
| Xi                | X(cid:24)i i   | j=1            | (j B             | ))j |
|                   |                | N              | j                |     |
|                   |                | ∑              | (                | 2   |
|                   | (YjX(cid:24)i  | ))(cid:25) 1 N | (cid:0)f Ai      |     |
| E X(cid:24)i (Var | Xi             |                | f(A)             |     |
|                   |                | 2 N j=1        | j                | B j |
45

| Estimating | Sensitivity | - Example |
| ---------- | ----------- | --------- |
46

High Dimensional Model
decomposition

| High dimensional | model       | representation |     |     |
| ---------------- | ----------- | -------------- | --- | --- |
| Y=f(X ;X         | ;X ;:::::;X | )              |     |     |
| 1                | 2 3         | k              |     |     |
∑ ∑
| Y=f 0 + | f(X)+ i i | f ij (X;X)+::: i | j   |     |
| ------- | --------- | ---------------- | --- | --- |
|         | i         | i;j              |     |     |
where f is a constant and f is a function of X, f a function of X and
| 0                     |     | i              | i ij        | i   |
| --------------------- | --- | -------------- | ----------- | --- |
| X; etc. Specifically, | for | each non-empty | S, we have: |     |
j
E[f (x )]=0
S S
where the expectation is taken over the distribution of the variables in S.
Only the constant term f captures the global mean response, while all
0
other components represent deviations from this mean due to single
| variables, pairs, | or higher-order | interactions. |     |     |
| ----------------- | --------------- | ------------- | --- | --- |
47

| High dimensional | model         | representation |     |
| ---------------- | ------------- | -------------- | --- |
| Y=f(X ;X         | ;X ;:::::;X ) |                |     |
| 1 2              | 3 k           |                |     |
|                  | ∑ ∑           |                |     |
| Y=f +            | f(X)+         | f (X;X)+:::    |     |
| 0                | i i i         | i;j ij i j     |     |
where f 0 is a constant and f i is a function of X, i f ij a function of X i and
X; etc.
j
|     | Component | Mean           | Constraint   |
| --- | --------- | -------------- | ------------ |
|     | f         | None (captures | global mean) |
0
E[f(x)]=0
f(x)
|     | i i |     | i i |
| --- | --- | --- | --- |
E[f
|     | f ij (x;x) i j     | ij (x;x)]=0     | i j |
| --- | ------------------ | --------------- | --- |
|     | ... (higher-order) | ... (analogous) |     |
48

| High dimensional | model         | representation |     |
| ---------------- | ------------- | -------------- | --- |
| Y=f(X ;X         | ;X ;:::::;X ) |                |     |
| 1 2              | 3 k           |                |     |
∑ ∑
| Y=f + | f(X)+ | f (X;X)+::: |     |
| ----- | ----- | ----------- | --- |
| 0     | i i i | i;j ij i j  |     |
where f 0 is a constant and f i is a function of X, i f ij a function of X i and
X; etc.
j
where:
| • f = global | mean response | (constant | term), |
| ------------ | ------------- | --------- | ------ |
0
| • f(x) = | individual variable | contributions, |     |
| -------- | ------------------- | -------------- | --- |
i i
| • f ij (x;x) i j | = pairwise          | interactions, |          |
| ---------------- | ------------------- | ------------- | -------- |
| • Higher         | terms = diminishing | cooperative   | effects. |
49

| High dimensional |                    | model       | representation |          |     |     |
| ---------------- | ------------------ | ----------- | -------------- | -------- | --- | --- |
| For              | f(x 1 ;x 2 ;x 3 ), | a 2nd-order | HDMR           | becomes: |     |     |
~f=f
|     | +f (x | )+f (x )+f | (x  | )+f (x ;x | )+f (x ;x | )+f (x ;x ) |
| --- | ----- | ---------- | --- | --------- | --------- | ----------- |
|     | 0 1 1 | 2 2        | 3 3 | 12 1 2    | 13 1 3    | 23 2 3      |
50

| High dimensional     |       | model       | representation |     |
| -------------------- | ----- | ----------- | -------------- | --- |
|                      | ∑     | ∑           |                |     |
| Y=f +                | f(X)+ | f           | (X;X)+:::      |     |
| 0                    | i i i | i;j ij      | i j            |     |
| Taking unconditional |       | expectation | on both sides: |     |
f 0 =E(Y)
| Taking conditional |     | expectation | X =x |     |
| ------------------ | --- | ----------- | ---- | --- |
i i
| f(x)=E(YjX | =x)(cid:0)f |     |     |     |
| ---------- | ----------- | --- | --- | --- |
| i i        | i           | i 0 |     |     |
f is the effect of varying X alone (known as the main effect of X )
| i   |     |     | i   | i   |
| --- | --- | --- | --- | --- |
51

| High dimensional   |       | model       | representation                    |            |        |
| ------------------ | ----- | ----------- | --------------------------------- | ---------- | ------ |
|                    | ∑     | ∑           |                                   |            |        |
| Y=f +              | f(X)+ |             | f (X;X)+:::                       |            |        |
| 0                  | i i   | i           | i;j ij                            | i j        |        |
| Taking conditional |       | expectation |                                   | X i =x;X i | j =x j |
| f (x;x)=E(YjX      |       | =x;X        | =x)(cid:0)f(x)(cid:0)f(x)(cid:0)f |            |        |
| ij i j             |       | i           | i j                               | j i i      | j j 0  |
f is the effect of varying X and X simultaneously, additional to the
| ij  |     |     | i   | j   |     |
| --- | --- | --- | --- | --- | --- |
effect of their individual variations. This is known as a second-order
| interaction. | Higher-order |     | terms       | have analogous | definitions. |
| ------------ | ------------ | --- | ----------- | -------------- | ------------ |
| Can you      | derive       | the | third-order | interaction?   |              |
52

Variance decomposition
| If inputs | are independent, | V distributes | over this! |
| --------- | ---------------- | ------------- | ---------- |
∑ ∑
|           | d                 | d +(cid:1)(cid:1)(cid:1)+V |          |
| --------- | ----------------- | -------------------------- | -------- |
| Var(Y)=   | V i +             | V ij                       | 12:::d   |
|           | i=1               | i<j                        |          |
| V =Var    | (E (YjX))         |                            |          |
| i         | Xi X(cid:24)i     | i                          |          |
|           | (                 | )                          |          |
|           | (YjX;X)           | (cid:0)V                   | (cid:0)V |
| V ij =Var | Xij E X(cid:24)ij | i j i                      | j        |
53

| Sensitivity | Index |     |
| ----------- | ----- | --- |
First-order sensitivity index”, or ”main effect index” S = V i . it
i V (Y )
measures the effect of varying X alone, but averaged over variations in
i
| other input | parameters. |                            |
| ----------- | ----------- | -------------------------- |
| ∑           | ∑           |                            |
|             | d           | d +(cid:1)(cid:1)(cid:1)+V |
| V(Y)=       | V i +       | V ij 12:::d                |
i=1 i<j
| Dividing both | sides by                     | Var(Y): |
| ------------- | ---------------------------- | ------- |
| ∑             | ∑                            |         |
| d S +         | d S +(cid:1)(cid:1)(cid:1)+S | =1      |
| i=1 i         | i<j ij                       | 12:::d  |
54

Density based methods

| Variance-based | drawback           |                     |
| -------------- | ------------------ | ------------------- |
| Which has      | the most variance? | and most uncertain? |
55

Density based methods
56

Density based methods
√
N +N
K^S>c((cid:11)) u c
N N
u c
57

Density based methods
58

Looking Forward

| What | are we             | missing? (Bazyleva,  | Garibay, and   | Roy 2023, | 2024) |
| ---- | ------------------ | -------------------- | -------------- | --------- | ----- |
|      | Traditional global | sensitivity analysis | (GSA) of ABMs: |           |       |
• Collapses a whole trajectory into a single scalar (e.g. mean at time
|     | T) and | computes Sobol’ indices | on that. |     |     |
| --- | ------ | ----------------------- | -------- | --- | --- |
• Time-varying GSA (Sobol’ at each t) is better, but still treats each
|     | time step | independently. |     |     |     |
| --- | --------- | -------------- | --- | --- | --- |
• For path-dependent, multi-level ABMs, what matters is the entire
|     | trajectory,        | not isolated slices. |     |     |     |
| --- | ------------------ | -------------------- | --- | --- | --- |
|     | Proposed solution: | trajectory-based     | GSA |     |     |
(cid:2) (cid:2)
• Treat the full output trajectory (time series agents levels) as
|     | the object | of analysis. |     |     |     |
| --- | ---------- | ------------ | --- | --- | --- |
• Compute sensitivity indices that reflect variation in trajectory shape
|     | and timing, | not just a terminal | scalar. |     |     |
| --- | ----------- | ------------------- | ------- | --- | --- |
59

| Time-varying | GSA (Bazyleva, | Garibay, and | Roy 2023, | 2024) |
| ------------ | -------------- | ------------ | --------- | ----- |
60

| GDMaps |     | +   | sparse | PCE | (Bazyleva, | Garibay, | and Roy | 2023, |
| ------ | --- | --- | ------ | --- | ---------- | -------- | ------- | ----- |
2024)
|     | Method | in  | a sentence |     |     |     |     |     |
| --- | ------ | --- | ---------- | --- | --- | --- | --- | --- |
|     |        |     | !          |     |     |     | !   |     |
Trajectories dimensionality reduction (GDMaps) surrogate (sparse
|     | PCE) | ! Sobol’       | indices          | on trajectory   | space.         |      |                   |     |
| --- | ---- | -------------- | ---------------- | --------------- | -------------- | ---- | ----------------- | --- |
|     | Two  | key components |                  |                 |                |      |                   |     |
|     | •    | Grassmannian   |                  | Diffusion       | Maps (GDMaps): |      |                   |     |
|     |      | • Embed        | high-dimensional |                 | trajectories   | into | a low-dimensional |     |
|     |      | geometric      |                  | representation. |                |      |                   |     |
• No need to pre-choose scalar summary statistics; GDMaps discovers
|     |     | the       | main       | modes of variation | in           | trajectories. |                   |     |
| --- | --- | --------- | ---------- | ------------------ | ------------ | ------------- | ----------------- | --- |
|     | •   | Sparse    | Polynomial | Chaos              | Expansion    | (PCE):        |                   |     |
|     |     | • Fit     | a cheap    | surrogate          | from inputs  | to GDMaps     | coordinates.      |     |
|     |     | • Compute |            | Sobol’ indices     | analytically | from          | PCE coefficients. |     |
61

| Trajectory | Based GSA | (Bazyleva, | Garibay, and | Roy 2023, | 2024) |
| ---------- | --------- | ---------- | ------------ | --------- | ----- |
62

| Trajectory Based  | GSA |     |     |     |
| ----------------- | --- | --- | --- | --- |
| What this enables |     |     |     |     |
• Multi-level sensitivity: micro (agent), meso, and macro trajectories
| in one framework.  |                   |                |                       |               |
| ------------------ | ----------------- | -------------- | --------------------- | ------------- |
| • Path dependence: | parameters        | that           | matter early          | or change     |
| distributional     | spread remain     | visible        | in the GSA.           |               |
| • Applications:    | Lotka–Volterra,   | DeepABM–COVID, |                       | and a poverty |
| trap ABM           | (micro/meso/macro |                | inequality dynamics). |               |
63

| Trajectory | Based GSA | (Bazyleva, | Garibay, and | Roy 2023, | 2024) |
| ---------- | --------- | ---------- | ------------ | --------- | ----- |
64

References I
Bazyleva, Valentina, Victoria M Garibay, and Debraj Roy (2023). “Global
sensitivity analysis using polynomial chaos expansion on the grassmann
manifold”. In: International Conference on Computational Science.
| Springer, | pp. 583–597. |     |     |     |
| --------- | ------------ | --- | --- | --- |
– (2024). “Trajectory-based global sensitivity analysis in multiscale
| models”. | In: Scientific | Reports 14.1, | p. 13902. |     |
| -------- | -------------- | ------------- | --------- | --- |
Sobol, Ilya M (2001). “Global sensitivity indices for nonlinear
| mathematical | models        | and their Monte | Carlo estimates”. | In:      |
| ------------ | ------------- | --------------- | ----------------- | -------- |
| Mathematics  | and computers | in simulation   | 55.1-3, pp.       | 271–280. |
65
