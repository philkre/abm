| Global Sensitivity    | Analysis       |                |               |
| --------------------- | -------------- | -------------- | ------------- |
| How to perform        | comprehensive, | efficient, and | robust Global |
| Sensitivity Analysis? |                |                |               |
Debraj Roy
ComputationalScienceLab,UniversityofAmsterdam

Table of contents
1. Monte Carlo Integration
2. Low discrepancy sequences
3. Quasi Monte-carlo sequence
1

| Estimating | First-order | Sensitivity |     |     |
| ---------- | ----------- | ----------- | --- | --- |
∫
∑n
1
|     | E2(yjx | =x~)p(x~)dx~ | =     | f(A)f(Bj ) |
| --- | ------ | ------------ | ----- | ---------- |
|     |        | j j j        | j j n | i A i      |
i=1
∑n
1
E2(y)=
f(A)f(B)
|     |     |     | n i | i   |
| --- | --- | --- | --- | --- |
i=1
2

| Estimating | Total-order | Sensitivity |     |     |     |
| ---------- | ----------- | ----------- | --- | --- | --- |
∫
∑n
|     |        |                                      | ~   | 1           |       |
| --- | ------ | ------------------------------------ | --- | ----------- | ----- |
|     | E2(yjx | =(cid:24)x~)p((cid:24)x~)d((cid:24)x |     | )= f(B)f(Bj | )     |
|     |        | j j j                                | j j | n           | i A i |
i=1
∑n
1
E2(y)=
f(A)f(B)
|     |     |     | n   | i i |     |
| --- | --- | --- | --- | --- | --- |
i=1
3

Monte Carlo Integration

| Integration | in one dimension |                  |
| ----------- | ---------------- | ---------------- |
| What is     | the area under   | the green curve? |
4

| Integration    | in one dimension       |                  |                     |
| -------------- | ---------------------- | ---------------- | ------------------- |
| What is        | the area under         | the green curve? |                     |
| Approximation: | Area t                 | sum of the areas | of the 8 rectangles |
| We get         | a better approximation | with more        | rectangles          |
5

| Integration    | in two dimension       |                      |               |
| -------------- | ---------------------- | -------------------- | ------------- |
| What is        | the volume under       | the blue surface?    |               |
| Approximation: | Volume                 | t sum of the volumes | of the 8x8=64 |
| rectangular    | prisms                 |                      |               |
| We get         | a better approximation | with more prisms     |               |
6

| Integration in  | two dimension |                    |               |
| --------------- | ------------- | ------------------ | ------------- |
| Approximation:  | Volume t      | sum of the volumes | of the 8x8=64 |
| rectangular     | prisms        |                    |               |
| We get a better | approximation | with finer grids   |               |
| 82 dots ! k2    | dots          |                    |               |
7

| Integration | in s dimension |     |     |
| ----------- | -------------- | --- | --- |
!
| Integral      | in high dimensions | “hyper | volume” |
| ------------- | ------------------ | ------ | ------- |
| Approximation | by product         | grids: |         |
k2
•
• k3
• ...
• ...
| • ks points | in hyper cube |     |     |
| ----------- | ------------- | --- | --- |
Approximation: s=360;k=2;2360 is astronomical (220 one million)
| We need | to stay away from | product grids | in high dimensions |
| ------- | ----------------- | ------------- | ------------------ |
8

| Monte carlo | methods |     |
| ----------- | ------- | --- |
Integral t average of function values at random points in the hyper cube.
| drawbacks: | big gaps, clusters, | slow convergence |
| ---------- | ------------------- | ---------------- |
9

Low discrepancy sequences

Equidistributed Sequence
A sequence fx g in the interval [0;1] is called equidistributed (or
n
uniformly distributed) if for any subinterval [a;b](cid:26)[0;1],
∑N
1
lim (cid:31) (x )=b(cid:0)a;
N!1N [a;b] n
n=1
where (cid:31) is the characteristic function of the interval [a;b], defined by
[a;b]
{
1 if x2[a;b];
(cid:31) (x)=
[a;b] 0 if x2= [a;b]:
In simpler terms, a sequence is equidistributed if the proportion of its
terms falling within any subinterval [a;b] approaches the length of the
interval, b(cid:0)a, as the number of terms goes to infinity.
10

Discrepancy
fx g
The discrepancy D N of a sequence n in the interval [0;1] is a measure
of how far the sequence is from being equidistributed. It is defined as:
|         | (cid:12)          |                                 | (cid:12) |
| ------- | ----------------- | ------------------------------- | -------- |
|         | (cid:12)          |                                 | (cid:12) |
|         | (cid:12)1 ∑N      |                                 | (cid:12) |
| D = sup | (cid:12) (cid:31) | (x )(cid:0)(b(cid:0)a)(cid:12); |          |
| N       | (cid:12)N         | [a;b) n                         | (cid:12) |
0(cid:20)a<b(cid:20)1
n=1
where (cid:31) is the characteristic function of the interval [a;b), given by
[a;b)
{
|          | 1    | if x2[a;b); |     |
| -------- | ---- | ----------- | --- |
| (cid:31) | (x)= |             |     |
[a;b)
|     | 0   | if x2= [a;b): |     |
| --- | --- | ------------- | --- |
11

Discrepancy
[0;1)s,
| Given a sequence | P=x 1 ;:::;x | N in     | its discrepancy | is: |
| ---------------- | ------------ | -------- | --------------- | --- |
|                  |              | (cid:12) | (cid:12)        |     |
|                  |              | (cid:12) | (cid:12)        |     |
A(B ;P)
|     |           | (cid:12)     | (cid:0)(cid:21) (cid:12) |     |
| --- | --------- | ------------ | ------------------------ | --- |
|     | D N (P)=s | u p (cid:12) | s (B) (cid:12)           |     |
2 N
B J
where (cid:21) is the s-dimensional Lebesgue measure, A(B;P) is the number
s
of points in P that fall into B, and J is the set of s-dimensional intervals
| or boxes of the | form |     |     |     |
| --------------- | ---- | --- | --- | --- |
∏s
|     | [a;b)=fx2Rs |     | (cid:20)x (cid:20)bg |     |
| --- | ----------- | --- | -------------------- | --- |
:a
|     | i i |     | i i i |     |
| --- | --- | --- | ----- | --- |
i=1
| where 0(cid:20)a | (cid:20)b (cid:20)1 |     |     |     |
| ---------------- | ------------------- | --- | --- | --- |
i i
12

Star Discrepancy
The star-discrepancy D(cid:3)(P) is defined similarly, except that the
N
supremum is taken over the set J(cid:3) of rectangular boxes of the form:
∏s
[0;u)
i
i=1
where u is in the half-open interval [0;1)
i
13

| Low Discrepancy | Sequences       |           |                  |
| --------------- | --------------- | --------- | ---------------- |
| Why are         | these sequences | important | in applications? |
Theorem
| A sequence | x ;:::;x | in Is is u.d. | mod 1 iff |
| ---------- | -------- | ------------- | --------- |
1 N
|     |     | ∑N  | ∫   |
| --- | --- | --- | --- |
1
|     |     | f(x)= | i f(u)du |
| --- | --- | ----- | -------- |
N
(cid:22)Is
i=1
| for all Riemann | integrable | functions | f on Is |
| --------------- | ---------- | --------- | ------- |
14

| Low Discrepancy | Sequences       |           |                  |
| --------------- | --------------- | --------- | ---------------- |
| Why are         | these sequences | important | in applications? |
Theorem
| A sequence | x ;:::;x | in Is is u.d. | mod 1 iff |
| ---------- | -------- | ------------- | --------- |
1 N
|     |     | ∑N  | ∫   |
| --- | --- | --- | --- |
1
|     |     | f(x)= | i f(u)du |
| --- | --- | ----- | -------- |
N
(cid:22)Is
i=1
| for all Riemann | integrable | functions | f on Is |
| --------------- | ---------- | --------- | ------- |
15

| Low Discrepancy | Sequences |                            |
| --------------- | --------- | -------------------------- |
| Why are these   | sequences | important in applications? |
Theorem
)!0
| D N (x n | iff x n is a u.d. | mod 1 sequence. |
| -------- | ----------------- | --------------- |
Remark
Sequences with best known bounds for star-discrepancy satisfy
O((logN)s=N). (The term low-discrepancy sequence is used for these
sequences.). This is important because of the Koksma-Hlawka inequality.
16

Koksma-Hlawka inequality
| (cid:12) ∫  | (cid:12) |     |
| ----------- | -------- | --- |
| (cid:12) ∑N | (cid:12) |     |
| (cid:12)1   | (cid:12) |     |
(cid:12) f(x)(cid:0) f(u)du(cid:12)(cid:20)V(f)D (cid:3) (x ;:::;x ):
| (cid:12)N i | (cid:12) | N 1 N |
| ----------- | -------- | ----- |
(cid:22)Is
i=1
It tells us about the asymptotic behaviour of the error O((logN)s=N).
17

Quasi Monte-carlo sequence

(t,m,s) nets
Definition
| 0(cid:20)t(cid:20)m, |                    | bm        | [0;1)s  |
| -------------------- | ------------------ | --------- | ------- |
| For                  | a  finite sequence | of points | in is a |
(t;m;s)(cid:0)net in base b if every elementary interval in base b of volume
| bt(cid:0)m contains | exactly bt points | of the sequence. |     |
| ------------------- | ----------------- | ---------------- | --- |
18

(t,m,s) nets
It is all about having the right number of points in various subdivisions.
2D Example:
we want to place 4 points in the unit square so that there is exactly one
point in each of the 4 rectangles of the same shape and size,given by the
three possible subdivisions:
19

(t,m,s) nets
2D Example:
we want to place 4 points in the unit square so that there is exactly one
point in each of the 4 rectangles of the same shape and size,given by the
three possible subdivisions:
20

(t,m,s) nets
2D Example:
we want to place 4 points in the unit square so that there is exactly one
point in each of the 4 rectangles of the same shape and size,given by the
three possible subdivisions:
21

(t,m,s) nets
2D Exercise:
draw a “(1;4;2)(cid:0)net in base 2”, that is, we want to place 16 points in
the unit square so that there are exactly 2 points in each of the 8
rectangles of the same shape and size, given by the fourpossible
subdivisions:
22

(t,m,s) nets
2D Exercise:
draw a “(1;4;2)(cid:0)net in base 2”, that is, we want to place 16 points in
the unit square so that there are exactly 2 points in each of the 8
rectangles of the same shape and size, given by the fourpossible
subdivisions:
23

(t,m,s) nets
2D Exercise:
draw a “(1;4;2)(cid:0)net in base 2”, that is, we want to place 16 points in
the unit square so that there are exactly 2 points in each of the 8
rectangles of the same shape and size, given by the fourpossible
subdivisions:
24

(t,m,s) nets
2D Exercise:
draw a “(1;4;2)(cid:0)net in base 2”, that is, we want to place 16 points in
the unit square so that there are exactly 2 points in each of the 8
rectangles of the same shape and size, given by the fourpossible
subdivisions:
25

(t,s) nets
Definition: An infinite sequence of points q ;q ;::: is called a
1 2
(t;s)-sequence in base b if the finite sequence q ;:::;q is a
kbm+1 (k+1)bm
(t;m;s)(cid:0)net in base b for all k(cid:21)0 and m(cid:21)t.
26

Sobol sequences
The most popular QMC approach uses Sobol sequences(xi) which have
| the property | that for small | dimensions d<40 | the subsequence: |
| ------------ | -------------- | --------------- | ---------------- |
2m (cid:20)i<2m+1
of length 2m has precisely 2m(cid:0)d points in each of the little cubes of
2(cid:0)d
volume formed by bisecting the unit hypercubein each dimension,
| and similar | properties hold | with other pieces. |     |
| ----------- | --------------- | ------------------ | --- |
27

Sobol sequences
| We can reuse | points compared | to Monte Carlo |
| ------------ | --------------- | -------------- |
28

Sobol sequences
QMC
can give a much lower error than standard MC; O(N1) in best cases,
instead of O(N1=2)
29

Questions?
29
