ID: pone.0318891 — 2025/4/3 — page 1 — #1

RESEARCH ARTICLE

Cooperation in the face of disaster

Marijane Luistro Jonsson

1,2☯∗, Markus Jonsson3,4☯

1 Center for Sustainability Research, Stockholm School of Economics, Stockholm, Sweden, 2 Department
of Neurobiology, Care Sciences and Society, Karolinska Institute, Stockholm, Sweden, 3 Center for
Cultural Evolution, Stockholm University, Stockholm, Sweden, 4 Department of Oncology-Pathology,
Karolinska Institute, Stockholm, Sweden

☯ These authors contributed equally to this work.
∗ marijane.luistro.jonsson@ki.se

Abstract

As calamities and health crises are expected to recur and become more frequent, we rely
more on cooperation to prevent similar situations and to cope with their aftermaths. How-
ever, it is not clear if, how and why people cooperate in uncertain situations where losses
can result from inadequate cooperation. Through theoretical modelling, experiments and
simulations, we show the behavioural patterns driving cooperation in a stochastic envi-
ronment. Specifically, by introducing stochastic shocks to a threshold public goods game
where one can randomly incur losses when group contributions are below a specific
level, we investigate what happens to cooperation when disasters strike repeatedly. The
findings show that compared to a control setting, cooperation is higher and persists when
there is a risk for disasters to strike, and that this is sustained by unconditional coopera-
tion. People give more and do not match the contributions of others, contrasting the con-
ditionality observed in deterministic environments. In other words, we observe a contribu-
tion divergence in uncertain environments wherein some give unconditionally while oth-
ers free-ride. We study three different types of uncertainty about the disaster: the proba-
bility of a disaster, additionally if it is uncertain how much cooperation is required to avoid
them (threshold level), and how much losses will be incurred (impact). The results are
similar in countries having different natural disaster risks, the Philippines and Sweden.
Simulating for a longer time period suggests the importance of promoting unconditionality
to foster sustained cooperation in facing an uncertain world.

Introduction

Cooperation is a fundamental mechanism in the biological and cultural evolution of human-
ity, and people often conditionally cooperate with others [1,2]. A common definition of coop-
eration is when one individual pays a cost for another to receive a benefit [2], and this has
been studied game-theoretically and experimentally through the standard public goods game
(e.g. [3,4]). In this deterministic environment, participants face a prisoner’s dilemma in decid-
ing how much of their given endowments will be contributed to the common good [5]. This
situation is often connected to but not limited to impacts of human activities to the natural
environment, such as overgrazing [6,7]. Forest lands, for example, are often privately cleared
for logging and farming, leading to a tragedy of the commons marked by erosion, flooding

OPEN ACCESS

Citation: Jonsson M L, Jonsson M (2025)
Cooperation in the face of disaster. PLoS ONE
20(4): e0318891. https://doi.org/10.1371/
journal.pone.0318891

Editor: The Anh Han, Teesside University,
UNITED KINGDOM OF GREAT BRITAIN AND
NORTHERN IRELAND

Received: October 6, 2024

Accepted: January 23, 2025

Published: April 3, 2025

Copyright: © 2025 Jonsson, Jonsson. This is
an open access article distributed under the
terms of the Creative Commons Attribution
License, which permits unrestricted use,
distribution, and reproduction in any medium,
provided the original author and source are
credited.

Data availability statement: All experiment
data and the simulation source code are
available at github.com/markusrobertjonsson/
condcoop. Below is our Data Sharing Plan: 1.
Data Description This study uses empirical data
collected during the experiments described in
the paper, as well as simulation data generated
through custom code. The shared dataset
includes: • Raw experimental data in XLSX
format. • Source code for simulations and data

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

1/ 18

PLOS ONE

ID: pone.0318891 — 2025/4/3 — page 2 — #2

PLOS ONE

Cooperation in the face of disaster

processing scripts. • Accompanying README
files describing the structure and contents of
the data. 2. Data Availability The full dataset and
code are publicly available in the following
GitHub repository: https://github.com/\protect\
penalty-\@M{}markusrobertjonsson/condcoop/
3. Licensing and Reuse Conditions • Source
Code: Licensed under the MIT License. Users
are free to use, modify, and distribute the code
with attribution. • Data: Licensed under Creative
Commons Attribution 4.0 International (CC BY
4.0). The data may be freely shared and adapted
with proper credit to the authors.

Funding: M.L.J.’s PhD studies were funded by
the Jan Wallanders och Tom Hedelius Stiftelse
samt Tore Browaldhs Stiftelse foundation,
including the experiments in this study. The
foundation did not play any role in the study
design, data collection and analysis, decision to
publish, or preparation of the manuscript.

Competing interests: The authors have
declared that no competing interests exist.

and desertification. Theoretically, the dominant individual optimal strategy is to not con-
tribute, because regardless of the actions of others, one will always be better off keeping one’s
endowments. However, if everyone resorts to this free-riding, the group suffers since every-
one would have been better-off contributing, displaying that the favorable behavior for the
individual is not best or efficient for the group. In time, with repeated interactions, contri-
butions are expected to converge to non-cooperation [8]. This is supported by experimental
studies, empirically revealing that a majority of the participants cooperate conditionally, as
they adjust or match their low and decreasing contributions to those of others (e.g. [9,10]).
Conditional cooperation is prevalent in different societies, both in stable, affluent countries
[10–12] as well as in the developing world [13,14].

Cooperative behavior is however not as straightforward to predict in a stochastic environ-

ment, where disasters that can lead to losses may occur repeatedly. Human judgements are
not always predictable in times of uncertainty [15], but it is nonetheless crucial to understand
human cooperation in this context. As we live in the Anthropocene age, the natural environ-
ment becomes more vulnerable and uncertain, depicted by human activities crossing over
planetary boundaries [16]. The environmental alterations, such as climate change and biodi-
versity loss, result to erratic changes in the natural systems, and eventually lead to catastrophic
consequences to human systems. We already witness the direct and indirect effects of recur-
ring hazards and disasters with the increasing cases of flash floods, forest fires, catastrophic
storms, disease outbreaks, and extreme weathers, causing not only economic losses but loss
of lives as well. In making these social ecological systems more robust, it has been argued
that the link and cooperation between resource users and public infrastructure providers
should not be ignored [17]. There are complex and nonlinear linkages between the environ-
mental and human systems [18], but oftentimes policies addressing these systems assume
deterministic settings.

This study investigates cooperation in a stochastic environment through a multi-modal
approach consisting of theoretical modelling, empirical experiments and simulations that
build on each other. We initially identified the equilibria predictions, and experimentally
tested the models to find out what the contribution levels converge to. The empirical find-
ings were subsequently used as a basis for a simulation of interactions for a longer period of
time to analyze identified mechanisms driving the results. The interplay between theoreti-
cal modelling, experimental work, and simulations allows this study to address the limita-
tions of each of the methods involved. For instance, the empirical data can shed evidence on
equilibrium selection to theoretical analyses with multiple equilibria, while the simulations
replicated empirical conditions to study the effects of specific combinations of agent strategies
for a longer time period, which is not possible to manipulate in experimental settings. The
next section provides a review of the previous studies that have provided a foundation for the
theoretical modelling.

Cooperation in a stochastic environment

One way in which cooperation has been studied in a stochastic environment is through
threshold public goods games (TPGG), also called provisional point mechanisms [19,20], step
level public goods [21,22], discrete public goods game [23], collective risk social dilemma [24,25],
or climate public goods games [26]. In its standard form, there is a collective target or thresh-
old that must be reached for the provision of the public good or the avoidance of a public bad
(i.e. collective loss). Here, there is an incentive for everyone in the group to contribute enough
to reach the threshold to avoid the risk of a collective loss, but at the same time, there is temp-
tation to defect or free-ride on the contributions of others, as in the standard public goods

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

2/ 18

ID: pone.0318891 — 2025/4/3 — page 3 — #3

PLOS ONE

Cooperation in the face of disaster

game. The best outcome for everyone is any contribution combination that exactly meets
the threshold (even if contributions are not fairly distributed among the participants). The
presence of multiple equilibria in a single interaction, including zero contributions, makes
it unclear if cooperation, with repeated interactions, will arise and persist or converge to the
non-cooperating behavior.

Theoretical studies using the TPGG framework, both taking game theoretic and evolu-
tionary dynamics perspectives, have attempted to model under which conditions the coop-
eration equilibrium emerges when there is a risk for loss in repeated interactions. Some of
the identified factors leading to successful group cooperation are reciprocity [27], high value
of the public good [23], high threshold uncertainty [28], high risk for a catastrophic event
[29], small group size under high risk [30], intermediate feedback of performance and risk
for loss [31], big initial endowments [32], and when participants care for the future [33].
Although these theoretical studies reveal valuable insights, they are based on predictions on
how hypothetical agents will behave to meet the cooperative equilibrium, prompting the need
for complementary empirical studies to provide evidence (e.g. [33]).

Empirical TPGG studies provide rich empirical evidence but are quite fragmented, having

multiple experimental design variants. They have identified different conditions and inter-
ventions making cooperation successful, such as lower threshold [21], homogeneous groups
[22], and the presence of refund guarantees [20,34] and communication [35]. More recent
studies, framed in the context of global cooperation, climate change or environmental conser-
vation, similarly use the collective risk dilemma setting to investigate the avoidance of envi-
ronmental disasters under different uncertainties. In general, cooperation is more success-
ful with higher risk on the occurrence of a loss [24], lower uncertainty on the threshold level
[36] and remains the same when the consequences or impact are known [37]. Conditions that
enhance cooperation include the provision of intermediate targets [25], expert information
and non-anonymity of contributions [26], as well as communication of commitments [37].
Conversely, cooperation decreases with inequality [22,38], when the benefits of avoiding the
catastrophe are low [37], and if the rewards of cooperation is delayed into future [39]. In the
same manner, variants of common pool resource and appropriation game settings similarly
study uncertainties surrounding cooperation by refraining from overharvesting resource or
moving funds to prevent drastic collapse. The studies likewise find that factors such as com-
munication [40], voting [41], slow thought processes [42], low opportunity costs [43], as well
as individual optimism [43] enhance cooperation when there is a chance for resource collapse
or losses. Although the extant experimental studies can shed some light on factors affecting
cooperation, the studies often entail a single decision interaction (e.g. [35–37]), or if there are
repeated interactions, there is only a single risk of disaster at the end of the game (e.g. [26,38])
or only one of the rounds is randomly chosen to be compensated (e.g. [44]). The variation in
the experimental designs makes it difficult to compare results of various types of uncertainties
and complement existing theoretical studies.

To provide more suitable empirical evidence that can inform related theoretical models,
and relevantly address the increased frequency of a wide range of disaster events, this study
makes a series of theoretical analyses, experiments, and simulations to study the effects of
uncertainties to cooperation. It seeks to investigate if cooperation persists under different
types of uncertainties, and identify possible underlying mechanisms driving it. In contrast to
other studies, this study does not intend to model the dynamics of a specific environmental
resource system with risk for a total system collapse (i.e. the game ends) but presents a gen-
eral stochastic environment to study how human cooperate with a constant risk for repeated
losses, and the interaction remains. We focus on the distinct effects of three common types
of uncertainties surrounding a possible disaster: when we do not know when it will happen

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

3/ 18

ID: pone.0318891 — 2025/4/3 — page 4 — #4

PLOS ONE

Cooperation in the face of disaster

(timing), how much loss will be incurred (timing+impact) and which cooperation level will
avoid it (timing+threshold).

Experiment design and theoretical predictions

To investigate how people cooperate in a stochastic environment, we compare a control group
(Control) in a deterministic setting (standard public goods game), and different treatments
depicting cooperation in stochastic settings (threshold public goods games). We initially
assign participants randomly into groups of four that interact with each other throughout
the experiment that lasts for 20 rounds, but the number of rounds is undisclosed to the par-
ticipants. In each round, each participant is given 20 monetary units to allocate between the
public pot and their individual account (i.e. what they keep for themselves). The allocation is
in whole units (0, 1, … , 20). The total contribution to the public pot is multiplied by 1.6 and
added to the group account.

After making the contribution decision in each round, participants get a summary infor-

mation of how others contributed (presented in random order), what they earned in that
round, and the current balance in their individual and group accounts. At the end of the
experiment, the balance in the group account is divided evenly among the four participants,
and the total earnings for each participant (the private account and their share of the group
account) are converted to real money.

In Control, there is no risk for losses and everyone gets their full income from the individ-
ual and group accounts at the end of their interactions. A single-interaction equilibrium anal-
ysis of the experiment groups shows that contributions in Control, with four participants and
21 strategies, are expected to converge to the single, dominant zero-contribution equilibrium.
In the treatment groups, there is a probability of a random check in each round, and if the

group contribution does not meet a certain level, losses in earnings are incurred. Different
treatments focus on different parameters, such as the probability of a check, the impact of a
failed check, and the threshold level. If there is a check, the participants get a red/green screen
informing them if the group failed/passed before they get the updated results and summary
information about the account balances. We specifically have these treatment groups:

• 10P: There is a 10% probability of a check in each round, and if the group contribution is
below a threshold level of 75% of total endowments in the group (i.e. 60 monetary units),
the cumulative earnings in both the individual and the group account will be reduced to
zero;

• 40P: The same conditions as 10P but there is a 40% probability of a check;
• Impact: The same conditions as 40P but if the threshold is not met, there is equal probabil-
ity (i.e. 1/3) that the individual account, the group account, or both accounts are reduced to
zero;

• Level: The same conditions as 40P but the threshold level in each round can be any inte-

ger value in a certain range (i.e. 50 to 70 units), randomly chosen with equal probability. In
each round, the threshold level for that round is revealed after contributing.

Fig 1 shows an overview of the different experiment groups, and details of the experiment

design and implementation can be found in S1 Appendix in the supporting information.
Additional information regarding the ethical, cultural, and scientific considerations specific
to inclusivity in global research is included in S4 Checklist.

In these treatments, the equilibria consist of the zero-contribution profile (0, 0, 0, 0) and
the group contribution combinations that add up to 60 units (70 units for Level). Details of

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

4/ 18

ID: pone.0318891 — 2025/4/3 — page 5 — #5

PLOS ONE

Cooperation in the face of disaster

Fig 1. Overview of the experiments.

https://doi.org/10.1371/journal.pone.0318891.g001

the equilibrium analyses for these different treatment groups are given in S2 Appendix in the
supporting information. This means that we cannot a priori predict what contributions will
converge to – either to a cooperative or to a free-riding regime. Various theoretical models
have made predictions but they build on assumptions such as how people may discount the
future (e.g. [32]), which might change alongside how people experience the disasters. There-
fore, we look into and rely on empirical evidence to study which equilibrium will be most
likely taken in the various experimental groups. The experiments were conducted to a total
of 884 participants in Sweden and the Philippines, countries having diverging disaster risk
exposures [45], to add to the external validity of the results.

Experimental results

In statistically analyzing if there are differences among the treatments, we used OLS regres-
sions, with standard errors adjusted for clustering on groups and participants.

Contributions

Effect of uncertainty. Our results show that contributions are 27% higher in the face
of disasters than in the absence of it (Fig 2A). In 58% of the threshold checks, the groups
succeeded in having adequate cooperation and avoided the disaster. The contributions in
the treatment groups also increased throughout the rounds, while it decreased in Control
(Fig 2B).

This pattern of not only higher but also increasing contributions is significant and consis-
tent for both countries and for the different types of uncertainty treatments (Figs 3A and 3B),
giving evidence that the interactions end up in a cooperative regime in the face of disaster.
That contributions are higher when there is a risk of losing earnings (unless a contribu-
tion threshold is met) is both intuitive and consistent with the Nash equilibrium analysis in

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

5/ 18

ID: pone.0318891 — 2025/4/3 — page 6 — #6

PLOS ONE

Cooperation in the face of disaster

Fig 2. Contributions: (A) Mean of individual contributions to the public good, with 95% confidence interval and
(B) mean contribution over time for each country.

https://doi.org/10.1371/journal.pone.0318891.g002

S2 Appendix. However, the extent to which contributions increase in the presence of a disas-
ter risk naturally depends on the participant’s risk-willingness. We see evidence of this in the
Contextual differences section below.

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

6/ 18

ID: pone.0318891 — 2025/4/3 — page 7 — #7

PLOS ONE

Cooperation in the face of disaster

Fig 3. Contributions of different experiment groups: (A) Mean of individual contribution to the public good,
with 95% confidence interval, and (B) mean contribution over time.

https://doi.org/10.1371/journal.pone.0318891.g003

Effect of different uncertainty types. Focusing on the specific results for the different
types of uncertainties, the ensuing patterns were exposed. There was no significant differ-
ence between contributions in 10P and 40P in either of the countries, showing that the exis-
tence of a possible loss, regardless of the probability level, may induce cooperation. To fur-

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

7/ 18

ID: pone.0318891 — 2025/4/3 — page 8 — #8

PLOS ONE

Cooperation in the face of disaster

Fig 4. Contribution given different disaster probabilities: (A) Mean of individual contribution to the public good
at different probability levels for a check to happen in each round, with 95% confidence interval and (B) mean
contribution over time.

https://doi.org/10.1371/journal.pone.0318891.g004

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

8/ 18

ID: pone.0318891 — 2025/4/3 — page 9 — #9

PLOS ONE

Cooperation in the face of disaster

ther explore the effects of this probability, additional experiments for 70% and 100% prob-
ability were conducted in Sweden. The findings in Fig 4 show that contributions generally
increase in a stepwise manner, with a significant increase between 40% and 70%, but not
between 70% and 100%. The non-difference of contributions in the range of 10% to 40%, and
70% to 100%, most likely reveal the heuristics people make in their probability estimation
[15]. The additional uncertainty in Impact did not lead to a significant difference in contribu-
tion levels compared to 40P while the additional uncertainty in Level resulted in significantly
higher contributions than in 40P and Impact, supporting the theoretical predictions. Partici-
pants level up their contributions to the upper limit of the uncertain threshold level interval,
converging to contribution combinations of 70 units.

Contextual differences

For contextual difference, those with less exposure to real-world disasters (Swedish partici-
pants) are faster to cooperate with others in the laboratory, contributing more when the loss
is not only real but also when looming. In isolating rounds wherein the threshold checks have
not yet occurred (i.e. rounds before the first check), the findings show that the Swedish par-
ticipants gave significantly higher contributions in all the treatment groups than Control (p <
0.001, SE = 0.964). This was not the case for the Filipino participants (p = 0.120, SE = 0.941).
Moreover, contributions in the first round in the treatment groups were significantly higher in
Sweden, see Fig 2B. These results suggest that those who are more exposed to higher disaster
risks initially take more risks, procrastinating higher contributions until the checks become
a reality. In the questionnaire given at the end of the experiment, the Swedes reported lower
risk-willingness compared to Filipinos (p < 0.001).

Responses to checks

In investigating how people behave behind the big picture of sustained cooperation, the fol-
lowing results prevail.

After experiencing a check where the group failed to meet the threshold, the total group
contribution in the immediate round after the check does not significantly change (Sweden
p = 0.469; Philippines p = 0.397). However, it then increases in the succeeding rounds, and
eventually plateaus around the threshold (Fig 5A). In particular, it drastically increases in the
second round after the check (Sweden p < 0.001; Philippines p < 0.001), and from the second
to the third round (Sweden p = 0.006; Philippines p < 0.001). The succeeding changes between
consecutive rounds tapered and were not significant any longer.

Moreover, group contributions in “almost-made-it” cases (i.e. 10% or less below the thresh-

old level) drastically decreased in the immediate round after the check, then eventually
increases, see Fig 5B. This depicts that close-call events can result in riskier decisions [46].
Both of the abovementioned results (where contributions are not increased after a failed
check) is consistent with erroneous heuristics used when assessing the risk of an uncertain
event, in particular the “Gambler’s fallacy” – the belief that the probability of a check in the
current round is lower if there was a check in the previous round [47,48].

Conditionality

We analyzed if individuals reciprocate the contributions of others, as what previous studies
have empirically found in a deterministic setting (e.g. [10,13,49]). Intuitive reciprocation, as
opposed to deliberative strategies, is argued to be the driving force behind cooperation [27].

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

9/ 18

ID: pone.0318891 — 2025/4/3 — page 10 — #10

PLOS ONE

Cooperation in the face of disaster

Fig 5. Contributions after a check: (A) Mean group contribution by rounds after a check, with 95% confidence
interval in groups which passed and failed the checks, and (B) for near-miss and almost made-it cases.

https://doi.org/10.1371/journal.pone.0318891.g005

We investigated if this is still the case in a repeated interaction and stochastic setting. Condi-
tional cooperation, and its corollary unconditional cooperation, is empirically measured in
this study in two ways.

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

10/ 18

ID: pone.0318891 — 2025/4/3 — page 11 — #11

PLOS ONE

Cooperation in the face of disaster

Firstly, we analysed the data using a statistical-type classification algorithm that calculates
each subject’s linear conditional-contribution profile (LCP) as a basis of classifying the partici-
pants [50]. The LCP is the ordinary least-squares regression line of a participant’s contribution
on the mean contribution that he/she observed immediately before making the contribution
(in our case, the average contribution of the other three participants in the previous round).
The intercept of the LCP gives a measure of the subject’s willingness to cooperate even if other
members do not, while the slope measures the subject’s responsiveness in the direction and
magnitude of others’ contribution. If the subject’s LCP lies only in the area below 50% of the
endowment level (10 units in our case), one is considered a “Free-Rider” (FR); if the LCP lies
only in the area above 10 units, one is considered an “Unconditional Cooperator” (UC); and
if the LCP has a positive slope and lies both above and below 10 units, one is considered a
“Conditional Cooperator” (CC) (or Reciprocator in other studies’ terminology). Subjects with
LCP lines not fitting into any of these criteria are classified as “Uncategorized”. Fig 6 shows a
typical LCP line for each category.

Fig 6. Typical Linear Contribution Profiles (LCP) for the different player types: LCPs of Unconditional Cooper-
ators are always above 10, Free riders are always below 10, Conditional Cooperators crosses 10 and has a positive
slope.

https://doi.org/10.1371/journal.pone.0318891.g006

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

11/ 18

ID: pone.0318891 — 2025/4/3 — page 12 — #12

PLOS ONE

Cooperation in the face of disaster

We find there were fewer CC in the treatments compared to Control. The distribution of
player types in Control is similar to what earlier studies have found, where a majority behaved
as CC (60%), followed by UC (24%), FR (11%), and Uncategorized (5%). On the other hand,
in the treatments, the distribution shifts to more UC (56%), and fewer CC (36%), FR (4%) and
Uncategorized (4%).

Secondly, we analyzed the extent of conformity, and the direction to which the participants

conform. Similar to previous studies, we investigated whether people increased, decreased
or did not change their contribution, depending on if they were above, below or equal to
the group average [50–52]. We find that the contributions in the treatment groups did not
decrease/increase as much as in Control, confirming that the tendency to conform is lower in
the treatments.

In looking into how participants contributions ranked compared to others, we additionally
find similar evidence that conditional cooperation weakens in a stochastic environment, com-
pared to a deterministic one. In this method, people’s contribution decisions are shaped based
on their perception on how they deviate from the group, thus, one can conform towards
the direction of the group. See S3 Appendix in the supporting information for conformity
analyses.

Equlibrium selection

The Nash equilibrium analysis in S2 Appendix in the supporting information for the treat-
ment groups 10P, 40P, and Impact with threshold level 60 predicts convergence to a number
of contribution combinations where the total group contribution is 60. Empirically, isolat-
ing these three treatments and consolidating both countries, the average contributions indeed
show an approximate convergence to a level slightly above 60 units, as seen in Table 1.

To investigate which of the Nash equilibria with group contribution 60 was selected, in
particular whether the symmetric Pareto-optimal equilibrium (15-15-15-15) was selected,
we computed the distances between this and the group contribution combinations. This was
done using a four-dimensional Manhattan metric. The results show that group contribu-
tions were far from the symmetric equilibrium. This is however expected as we have estab-
lished the presence of unconditional cooperation in these treatments in the section Condi-
tionality. In other words, there is a divergence characterized by the presence of both free-
riders and high-contributors in the uncertainty treatments. In the presence of free-riders, the
high-contributors are categorized as unconditional cooperators.

Simulation results

Given the experimental findings, simulations were made to investigate how groups with dif-
ferent constellations of player types would fare in the long run, given the identified contribu-
tion patterns found in the experiments (See [53] for the source code.). For each player type,
we used the average of the observed LCP lines to compute the contribution in each round
based on the other participants’ contributions in the previous round. We also used the aver-
age initial contributions for each player type to determine the contribution in the first round.

Table 1. Group contributions in 10P, 40P, and Impact over round number.

Round
Contribution
Round
Contribution

1
53.0
11
59.1

2
52.4
12
59.3

3
58.8
13
61.0

4
59.9
14
60.6

5
58.9
15
60.3

6
59.7
16
62.0

7
58.2
17
63.0

8
57.2
18
64.0

9
59.7
19
63.4

10
59.5
20
62.7

https://doi.org/10.1371/journal.pone.0318891.t001

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

12/ 18

ID: pone.0318891 — 2025/4/3 — page 13 — #13

PLOS ONE

Cooperation in the face of disaster

Fig 7 shows varying proportions of UC (x-axis), where the CC/FR ratio is fixed to the empir-
ically found value 215/21 = 10.2. With the resulting distribution of player types, a popula-
tion of 4000 individuals was divided into 1000 groups of four where each group member was
assigned a player type at random with probabilities from this distribution. After 200 rounds
the simulation was terminated and the converged group contribution g was compared to the
threshold level 60. If g < 60, the group is considered unsuccessful, otherwise successful. The
proportion of successful groups in the population is then used as a measure of the popula-
tion’s success (y-axis). The empirical value (proportion 0.56 unconditional cooperators) is
marked in Fig 7.

We find a nonlinear increase of population success with respect to proportion UC. In

other words, a population gains more (in terms of number of successful groups) by increasing
the proportion of UC, compared to what the population loses by decreasing the proportion
of UC.

Discussion and conclusion

The various experimental and simulation findings of this study jointly show that in the long
term, cooperation can persist in the face of disasters, It also exposes the role that uncondi-
tional cooperation plays in this process. People generally chose to cooperate and avoid a dis-
aster given a small probability of the disaster, and where the required threshold to avoid the
disaster is unknown (level), as well as when the consequences of the disaster is unknown
(impact). These findings give supporting evidence to earlier studies postulating how the col-
lective dilemmas do not necessarily have to end in a tragedy [33].

Fig 7. Proportion of successful groups against the proportion of unconditional cooperators: Results of simulated
interactions under treatments conditions for 200 rounds, based on the average empirical LCP lines per player
type. The vertical black line depicts the empirical proportion of UC in the experiments.

https://doi.org/10.1371/journal.pone.0318891.g007

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

13/ 18

ID: pone.0318891 — 2025/4/3 — page 14 — #14

PLOS ONE

Cooperation in the face of disaster

This study also finds that unconditional cooperation increases in these uncertain environ-
ments compared to a certain one. With the definition of unconditionality used in this paper,
this increase is explained by the fact that there is both low-contributing individuals and high-
contributing individuals present in these environents, giving rise to the unconditional coop-
eration found in this study. If all individuals matched one another’s sufficiently high contribu-
tions to avoid the tragedy of the commons in the face of disasters, there would be no uncon-
ditional cooperation to measure. However, the reality of free-riding behavior gives rise to a
contribution divergence and calls attention to the importance of unconditional cooperation.

Uncovering unconditional cooperation behavior is merely scratching the surface of human

behavior in uncertain times, as other related mechanisms or deep-seated factors might be
involved. In this study unconditional cooperation is conceptualized as the high contributions
of people do not match the low contributions of others, which can stem from various reasons
not necessarily limited or equated to altruism or pro-sociality. For instance, given the experi-
mental set-up involving multiple rounds, one can interpret the behaviour as a form of learned
generosity, or can alternatively result from loss avoidance. Future studies can probe more into
the concept of unconditional cooperation. Nonetheless, as this study uncovers the importance
of unconditional cooperation, it leaves implications not only for science to explore, but for
management and policy to promote unconditional behavior. With the increasing uncertainty
in the real world, it is difficult to assume that people will cooperate unconditionally, especially
since humans have been used to conditionally cooperate. In the stable Holocene age, we have
developed a tit-for-tat behavior to survive, and we need to be aware that others will continue
to reactively cooperate conditionally or free-ride in the face of disaster.

Given that there will always be people who will free-ride, how do we then go forward pro-
moting unconditional cooperation? The experimental settings in this study can provide some
insights for conditions. In the experiments, the participants were informed and reminded of
the probabilities of a disaster when they made their decisions, giving an insight how infor-
mation dissemination can be important to people’s capacity and psychology to cooperate.
Humanity cannot rely on the looming risk for disasters alone to push cooperation, but the
awareness and reminder of it can aid people in making unconditional cooperative decisions.
The findings also reveal that being informed of an even low probability of a disaster can make
people cooperate in the same way as a moderate one. The information nudge can help us pre-
pare and act according to what is best for us, rather than become unnecessary victims due
to ignorance, overconfidence, knowledge resistance or denial of disasters. It should be noted
that people perceive information on disasters differently, and their experience of disasters and
emotions play an important role. In the study, some people instantly cooperate with the pres-
ence of a threat of a loss, while others only cooperate after “getting burned”. Thus, exposure
to disasters can give variations to how people immediately respond to the call to cooperate,
indicating the importance of spreading information effectively.

Moreover, the findings imply the importance for various institutions to structurally pro-
mote unconditional cooperation, and not just to rely on individual responsibility to encourage
altruistic acts. There are social factors beyond the scope of this study, which future studies can
investigate, that can have the reverse effect to cooperation in the face of disasters (e.g. inequal-
ity). Thus, considering the vulnerable state of the world with increasing polarization, there
is an urgent need to establish a structural change in mindset among governing systems and
institutions for bottom-up unconditional cooperation to arise in its various forms (e.g. follow-
ing health restrictions, using less fossil fuels or compensating for its use). Currently, institu-
tional structures are still designed to function in a stable environment and based on norms
of reciprocity and conditional cooperation, reflected for instance by repeated failed global

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

14/ 18

ID: pone.0318891 — 2025/4/3 — page 15 — #15

PLOS ONE

Cooperation in the face of disaster

cooperation agreements, which warrants transformation. Although studies on unstable envi-
ronments such as this one shows the positive effects of uncertainty, the real world have other
factors that can outweigh such effects. This presents an urgency for policy and management,
in various levels, to create and cultivate conditions conducive for unconditional cooperation
as we face more disasters.

To conclude, cooperation has been and still is a keystone of humanity’s survival in times
of disasters. The key lesson is that we are indeed capable of cooperating, but it is important
for an unconditional cooperation mindset to dominate in order to successfully hurdle over
thresholds in unstable environments. This study shows how some conditions, such as pro-
viding information about the possibilities, impact and prevention level of disasters, no mat-
ter how uncertain they are, can provide provisions for unconditional cooperation to prevail.
This demonstrates the importance of transparency, effective communication, education, and
transforming institutional structures that can give way to forming collective ethos encourag-
ing unconditional cooperation. We eventually realize that we need to think of and cooperate
with others to overcome disasters, regardless of the past, to save ourselves in the future. Dis-
asters are continuously happening – remotely for some and immediate for others, and in this
uncertain world where disaster can strike, there is a need for unconditionality to flourish for
human cooperation to thrive.

Supporting information

S1 Appendix. Materials and methods. This file contains the details of the experiment design
and implementation.
(PDF)

S2 Appendix. Nash equilibrium analyses. This file contains the Nash equilibrium analyses of
the different experiment groups.
(PDF)

S3 Appendix. Conformity tests. This file contains an analysis of how the participants con-
form to the rest of the group.
(PDF)

S4 Checklist. Inclusivity in global research. This file contains information regarding the
ethical, cultural, and scientific considerations specific to inclusivity in global research.
(PDF)

Acknowledgments

We acknowledge the staff of the computer laboratory at the Computational Science Research
Center (CSRC), University of the Philippines Diliman, for their administrative and tech-
nical support during the experiments conducted at their facility. We also thank Alexander
Funcke from the Centre for Cultural Evolution (CEK), Stockholm University, for his technical
assistance in the CEK lab.

Author contributions

Conceptualization: Marijane Luistro Jonsson.

Data curation: Marijane Luistro Jonsson.

Formal analysis: Marijane Luistro Jonsson, Markus Jonsson.

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

15/ 18

ID: pone.0318891 — 2025/4/3 — page 16 — #16

PLOS ONE

Cooperation in the face of disaster

Investigation: Marijane Luistro Jonsson.

Methodology: Marijane Luistro Jonsson.

Project administration: Marijane Luistro Jonsson.

Software: Markus Jonsson.

Visualization: Marijane Luistro Jonsson, Markus Jonsson.

Writing – original draft: Marijane Luistro Jonsson.

Writing – review & editing: Marijane Luistro Jonsson, Markus Jonsson.

References
1. Axelrod R, Hamilton WD. The evolution of cooperation. Science. 1981;211(4489):1390–1396.

https://doi.org/10.1126/science.7466396 PMID: 7466396

2. Nowak MA. Five rules for the evolution of cooperation. Science. 2006;314(5805):1560–1563.

https://doi.org/10.1126/science.1133755 PMID: 17158317
Ledyard JO, et al. Public goods: a survey of experimental research. Div Hum Soc Sci. 1994.

3.

4. Chaudhuri A. Sustaining cooperation in laboratory public goods experiments: a selective survey of

the literature. Exp Econ. 2010;14(1):47–83. https://doi.org/10.1007/s10683-010-9257-1

5. Dawes RM. Social dilemmas. Ann Rev Psychol. 1980;31(1):123–45.

https://doi.org/10.1146/annurev.ps.31.1980.001123

6. Hardin G. The tragedy of the commons. the population problem has no technical solution; it requires

a fundamental extension in morality. Science. 1968;162(3859):1243–8.
https://doi.org/10.1126/science.162.3859.1243 PMID: 5699198

7. Ostrom E. Governing the commons: the evolution of institutions for collective action. 1990.

8.

9.

Fudenberg D, Maskin E. The Folk theorem in repeated games with discounting or with incomplete
information. Econometrica. 1986;54(3):533-554. https://doi.org/10.2307/1911307

Fischbacher U, Gächter S, Fehr E. Are people conditionally cooperative? Evidence from a public
goods experiment. Econom Lett. 2001;71(3):397–404.
https://doi.org/10.1016/s0165-1765(01)00394-9

10.

Fischbacher U, Gächter S. Social preferences, beliefs, and the dynamics of free riding in public
goods experiments. Am Econ Rev. 2010;100(1):541–56. https://doi.org/10.1257/aer.100.1.541

11. Brandts J, Saijo T, Schram A. How universal is behavior? A four country comparison of spite and
cooperation in voluntary contribution mechanisms. Public Choice. 2004;119(3/4):381–424.
https://doi.org/10.1023/b:puch.0000033329.53595.1b

12. Herrmann B, Thöni C. Measuring conditional cooperation: a replication study in Russia. Exp Econ.

2008;12(1):87–92. https://doi.org/10.1007/s10683-008-9197-1

13. Hofmeyr A, Burns J, Visser M. Income inequality, reciprocity and public good provision: an

experimental analysis. South Afr J Econ. 2007;75(3):508–520.
https://doi.org/10.1111/j.1813-6982.2007.00127.x

14. Martinsson P, Pham-Khanh N, Villegas-Palacio C. Conditional cooperation and disclosure in

developing countries. J Econ Psychol. 2013;34:148–155. https://doi.org/10.1016/j.joep.2012.09.005

15. Slovic P, Tversky A. Judgment under uncertainty: heuristics and biases. Cambridge University

Press 1982

16. Rockström J, Steffen W, Noone K, Persson Å, Chapin FSI, Lambin E, et al. Planetary boundaries:

exploring the safe operating space for humanity. E&S. 2009;14(2).
https://doi.org/10.5751/es-03180-140232

17. Anderies JM, Janssen MA, Ostrom E. A framework to analyze the robustness of social-ecological

systems from an institutional perspective. E&S. 2004;9(1). https://doi.org/10.5751/es-00610-090118

18.

19.

Liu J, Dietz T, Carpenter SR, Alberti M, Folke C, Moran E, et al. Complexity of coupled human and
natural systems. Science. 2007;317(5844):1513–1516. https://doi.org/10.1126/science.1144004
PMID: 17872436

Isaac RM, Schmidtz D, Walker JM. The assurance problem in a laboratory market. Public Choice.
1989;62(3):217–236. https://doi.org/10.1007/bf02337743

20. Rondeau D, D. Schulze W, Poe GL. Voluntary revelation of the demand for public goods using a

provision point mechanism. J Publ Econ. 1999;72(3):455–470.
https://doi.org/10.1016/s0047-2727(98)00104-2

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

16/ 18

ID: pone.0318891 — 2025/4/3 — page 17 — #17

PLOS ONE

Cooperation in the face of disaster

21. Suleiman R, Budescu D, Rapoport A. Provision of step-level public goods with uncertain provision

threshold and continuous contribution. Group Decis Negotiation. 2001;10:253–274

22. Rapoport A, Suleiman R. Incremental contribution in step-level public goods games with asymmetric

players. Organ Behav Hum Decis Process. 1993;55(2):171–194.
https://doi.org/10.1006/obhd.1993.1029

23. McBride M. Discrete public goods under threshold uncertainty. J Publ Econ.
2006;90(6–7):1181–1199. https://doi.org/10.1016/j.jpubeco.2005.09.012

24. Milinski M, Sommerfeld RD, Krambeck H-J, Reed FA, Marotzke J. The collective-risk social dilemma

and the prevention of simulated dangerous climate change. Proc Natl Acad Sci USA.
2008;105(7):2291–2294. https://doi.org/10.1073/pnas.0709546105 PMID: 1828708

25. Milinski M, Röhl T, Marotzke J. Cooperative interaction of rich and poor can be catalyzed by

intermediate climate targets. Clim Change. 2011;109(3–4):807–814.
https://doi.org/10.1007/s10584-011-0319-y

26. Milinski M, Semmann D, Krambeck H-J, Marotzke J. Stabilizing the earth’s climate is not a losing

game: supporting evidence from public goods experiments. Proc Natl Acad Sci U S A.
2006;103(11):3994–3998. https://doi.org/10.1073/pnas.0504902103 PMID: 16537474

27. Rand DG, Nowak MA. Human cooperation. Trends Cogn Sci. 2013;17(8):413–425.

https://doi.org/10.1016/j.tics.2013.06.003 PMID: 23856025

28. Suleiman R. Provision of step-level public goods under uncertainty. Ration Soc. 1997;9(2):163–187.

https://doi.org/10.1177/104346397009002002

29. Hilbe C, Abou Chakra M, Altrock PM, Traulsen A. The evolution of strategic timing in collective-risk
dilemmas. PLoS One. 2013;8(6):e66490. https://doi.org/10.1371/journal.pone.0066490 PMID:
23799109

30. Santos FC, Pacheco JM. Risk of collective failure provides an escape from the tragedy of the

commons. Proc Natl Acad Sci USA. 2011;108(26):10421–10425.
https://doi.org/10.1073/pnas.1015648108 PMID: 21659631

31. Chen X, Szolnoki A, Perc M. Averting group failures in collective-risk social dilemmas. EPL.

2012;99(6):68003. https://doi.org/10.1209/0295-5075/99/68003

32. Wang J, Fu F, Wu T, Wang L. Emergence of social cooperation in threshold public goods games

with collective risk. Phys Rev E Stat Nonlin Soft Matter Phys. 2009;80(1 Pt 2):016101.
https://doi.org/10.1103/PhysRevE.80.016101 PMID: 19658768

33. Barfuss W, Donges JF, Vasconcelos VV, Kurths J, Levin SA. Caring for the future can turn tragedy
into comedy for long-term collective action under risk of collapse. Proc Natl Acad Sci U S A.
2020;117(23):12915–12922. https://doi.org/10.1073/pnas.1916545117 PMID: 32434908

34. Rose SK, Clark J, Poe GL, Rondeau D, Schulze WD. The private provision of public goods: tests of

a provision point mechanism for funding green power programs. Resour Energy Econom.
2002;24(1–2):131–155. https://doi.org/10.1016/s0928-7655(01)00048-3

35. Palfrey T, Rosenthal H, Roy N. How cheap talk enhances efficiency in threshold public goods
games. Games Econom Behav. 2017;101:234–259. https://doi.org/10.1016/j.geb.2015.10.004

36.

37.

38.

39.

40.

arrett S, Dannenberg A. Sensitivity of collective action to uncertainty about climate tipping points.
Nat Clim Change. 2013;4(1):36–39. https://doi.org/10.1038/nclimate2059

arrett S, Dannenberg A. Climate negotiations under scientific uncertainty. Proc Natl Acad Sci U S A.
2012;109(43):17372–17376. https://doi.org/10.1073/pnas.1208417109 PMID: 23045685

Tavoni A, Dannenberg A, Kallis G, Löschel A. Inequality, communication, and the avoidance of
disastrous climate change in a public goods game. Proc Natl Acad Sci USA.
2011;108(29):11825–11829. https://doi.org/10.1073/pnas.1102493108 PMID: 21730154

Jacquet J, Hagel K, Hauert C, Marotzke J, Röhl T, Milinski M. Intra- and intergenerational
discounting in the climate game. Nat Clim Change. 2013;3(12):1025–1028.
https://doi.org/10.1038/nclimate2024

Lindahl T, Crépin A-S, Schill C. Potential Disasters can turn the tragedy into success. Environ
Resource Econ. 2016;65(3):657–676. https://doi.org/10.1007/s10640-016-0043-1

41. Hauser OP, Rand DG, Peysakhovich A, Nowak MA. Cooperating with the future. Nature.

2014;511(7508):220–223. https://doi.org/10.1038/nature13530 PMID: 25008530

42. Brozyna C, Guilfoos T, Atlas S. Slow and deliberate cooperation in the commons. Nat Sustain.

2018;1(4):184–189. https://doi.org/10.1038/s41893-018-0050-z

43. Blanco E, Haller T, Walker JM. Externalities in appropriation: responses to probabilistic losses. Exp

Econ. 2017;20(4):793–808. https://doi.org/10.1007/s10683-017-9511-x PMID: 29151806

44. Blanco E, Lopez MC, Walker JM. The opportunity costs of conservation with deterministic and

probabilistic degradation externalities. Environ Resource Econ. 2015;64(2):255–273.
https://doi.org/10.1007/s10640-014-9868-7

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

17/ 18

ID: pone.0318891 — 2025/4/3 — page 18 — #18

PLOS ONE

Cooperation in the face of disaster

45. Bündnis Entwicklung Hilft, . WeltRisikoBericht. 2023

46. Dillon RL, Tinsley CH. How near-misses influence decision making under risk: a missed opportunity

for learning. Manag Sci. 2008;54(8):1425–1440. https://doi.org/10.1287/mnsc.1080.0869

47. Clotfelter CT, Cook PJ. Notes: the “Gambler’s Fallacy” in lottery play. Manag Sci.

1993;39(12):1521–1525. https://doi.org/10.1287/mnsc.39.12.1521

48.

49.

Tversky A, Kahneman D. Belief in the law of small numbers.. Psychol Bull. 1971;76(2):105–110.
https://doi.org/10.1037/h0031322

Fehr E, Gintis H. Human motivation and social cooperation: experimental and analytical
foundations. Ann Rev Sociol. 2007;33(1):43–64.

50. Kurzban R, Houser D. Experiments investigating cooperative types in humans: a complement to

evolutionary theory and simulations. Proc Natl Acad Sci USA. 2005;102(5):1803–1807.
https://doi.org/10.1073/pnas.0408759102 PMID: 15665099

51. Croson R, Fatas E, Neugebauer T. Reciprocity, matching and conditional cooperation in two public

goods games. Econom Lett. 2005;87(1):95–101. https://doi.org/10.1016/j.econlet.2004.10.007.

52. Keser C, Van Winden F. Conditional cooperation and voluntary contributions to public goods. Scand

J Econom. 2000;102(1):23–39. https://doi.org/10.1111/1467-9442.00182

53.

Jonsson M. Unconditional cooperation: Code for simulations; 2023.
https://github.com/markusrobertjonsson/condcoop.

PLOS ONE https://doi.org/10.1371/journal.pone.0318891 April 3, 2025

18/ 18


