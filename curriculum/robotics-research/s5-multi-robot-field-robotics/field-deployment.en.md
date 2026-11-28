---
id: s5-field-deployment
lang: en
title: Field deployment and long-term autonomy
summary: >-
  Derive, at the scale of a robot field trial, the reliability engineering that turns "it worked
  in the field" into numbers. Obtain the MTBF and its confidence interval from a failure count,
  compute the mission reliability of a series system and of a multi-robot team, and show that
  when the failure rate is not constant (early failures) the extrapolation of the exponential
  model is wrong in both directions. Analyse failure modes as competing risks so that "which one
  to fix first" is decided by the change in mission reliability, and derive the number of
  failure-free trials needed to demonstrate a target reliability. The final deliverable is a
  classification of the failures of real field reports in the same framework.
objectives:
  - Derive and compute the point estimate and the chi-square confidence interval of the MTBF from a failure count and the cumulative operating time.
  - Derive the mission reliability of a series system and of a k-out-of-n team and compute the effect of common-cause failures.
  - Derive, with the Weibull model, the extrapolation error of the exponential model when the failure rate is not constant, and check for it in data.
  - Analyse failure modes as competing risks and justify an improvement priority by the change in mission reliability.
  - Derive the number of failure-free trials required at a target reliability and confidence level and design a field trial.
tags: [field-robotics, reliability, mtbf, failure-modes, long-term-autonomy, research]
---

# Field deployment and long-term autonomy

## Setup and notation

The first five lessons of S5 covered the **algorithms** of multi-robot systems. This lesson
covers the questions that arise once such a system is put in the field — **how long and how
often does it run without failing, and what should be fixed first**. The statistics are those of
`r1-experiment-design` and `s4-evaluation-science` (binomial intervals, power). The recommended
prerequisites are `s5-comms-constrained-estimation` and `r1-experiment-design`.

| Symbol | Meaning |
|---|---|
| $T$ | Cumulative operating time (the sum over all missions) |
| $r$ | Number of failures observed |
| $\lambda$, MTBF | Failure rate and mean time between failures. For a constant failure rate $\mathrm{MTBF} = 1/\lambda$ |
| $R(t)$ | Mission reliability — the probability of completing a mission of length $t$ without failure |
| $h(t)$, $H(t)$ | Hazard function (instantaneous failure rate) and cumulative hazard $\int_0^th$. $R(t) = e^{-H(t)}$ |
| $\beta$, $\eta$ | Weibull shape and scale parameters. $H(t) = (t/\eta)^\beta$. $\beta < 1$ early failures, $\beta = 1$ constant, $\beta > 1$ wear-out |
| Failure mode $k$ | Cause category of a failure (communication, mobility, perception, power, computation, …). A mission ends at its **first** failure (competing risks) |
| $C$ | Confidence level |

**The three ways a field trial differs from a laboratory evaluation** are the map of this lesson.

| Difference | Consequence | Treated in |
|---|---|---|
| Failures are rare and time is expensive | Intervals are wide — one has to speak about the MTBF from 3 failures | R1, R5 |
| The system is in series and there are several robots | The weakest link and the common causes dominate | R2 |
| The failure rate is not constant and there are several causes | Extrapolating from one average is wrong, and what to fix has to be seen cause by cause | R3, R4 |

## Key results

The bracket gives the derivation depth (D0 cited / D1 skeleton / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (the confidence interval of the MTBF) [D3]** — if failures form a Poisson process of
  constant rate $\lambda$ and $r$ failures are observed in a cumulative operating time $T$, then
  $$
  \widehat{\mathrm{MTBF}} = \frac{T}{r}, \qquad
  \frac{2T}{\chi^2_{1-\alpha/2,\,2r+2}} \;\le\; \mathrm{MTBF} \;\le\; \frac{2T}{\chi^2_{\alpha/2,\,2r}} \tag{1}
  $$
  is an interval of confidence level at least $1-\alpha$. **3 failures in 40 hours** give a point
  estimate of $13.3$ h with a 95% interval of $[4.6, 64.7]$ h — a factor of 14. Even with **0**
  failures there is a lower bound: $\mathrm{MTBF} \ge T/(-\ln\alpha)$, that is $T/3.0$ at 95%
  (the time version of the rule of three).
- **R2 (series systems and teams) [D2]** — if the subsystems are independent and the failure of
  any one fails the mission, failure rates **add**: $\lambda_{\mathrm{sys}} = \sum_k\lambda_k$.
  Four subsystems of MTBF 50 hours give a system MTBF of $12.5$ h. The reliability of a team in
  which at least $k$ of $n$ robots must survive is
  $$
  R_{\mathrm{team}} = R_{\mathrm{cc}}\sum_{j=k}^{n}\binom{n}{j}R_{\mathrm{ind}}^{\,j}(1 - R_{\mathrm{ind}})^{n-j} \tag{2}
  $$
  ($R_{\mathrm{cc}}$: the probability of no common-cause failure). With a single-robot two-hour
  reliability of $0.884$, a mission that needs only one of three robots to survive has
  $0.9984$, but if **30% of the failures are common cause** it falls to $0.963$ — redundancy
  does not fix common causes.
- **R3 (if the constant-rate assumption is wrong, extrapolation is wrong in both directions)
  [D2]** — with the Weibull hazard $H(t) = (t/\eta)^\beta$ and $\beta < 1$ (early failures), an
  exponential model fitted on two-hour missions is **optimistic for short missions** and
  **pessimistic for long ones**. On the field log of the reproduction task (80 missions) the
  prediction of the exponential model against the truth is $0.933$ vs $0.889$ for a 0.5-hour
  mission and $0.329$ vs $0.421$ for an 8-hour mission. And "one 8-hour mission" and "eight
  1-hour missions" have different reliabilities for the same cumulative time — $0.636$ vs
  $0.354$ at $\beta = 0.6$.
- **R4 (what to fix first: competing risks and the change in mission reliability) [D2]** — the
  mission reliability with failure mode $k$ removed is
  $$
  R_{-k}(t) = \exp\Big(-\sum_{j\ne k}H_j(t)\Big) = \frac{R(t)}{R_k(t)} \tag{3}
  $$
  and this is the **value** of the improvement. In the field log, mobility failures are 14 of 19
  (74%, 95% interval $[49\%, 91\%]$) and removing them raises the two-hour reliability from
  $0.764$ to $0.932$. No other mode gets past $0.80$. And **the modes never observed** (power,
  computation: 0 failures) have a 95% upper bound of $17.6\%$ on their share — unobserved is not
  absent.
- **R5 (failure-free trials needed to demonstrate a target reliability) [D2]** — demonstrating a
  reliability $R$ at confidence level $C$ takes
  $$
  n = \left\lceil\frac{\ln(1-C)}{\ln R}\right\rceil \tag{4}
  $$
  consecutive failure-free missions: 22 for $R = 0.9$, $C = 0.9$; 45 for $R = 0.95$; 230 for
  $R = 0.99$. Allowing one failure raises these to 38, 77 and 388. **A 99% reliability is hard to
  demonstrate by field trial** — which is why high-reliability systems are argued through
  subsystem tests and models.

## Derivation

### R2 — series systems, teams, common causes

**Series.** Let the lifetimes $X_k$ of the subsystems be independent and let the system fail at
$\min_kX_k$.

$$
R_{\mathrm{sys}}(t) = \Pr[\min_kX_k > t] = \prod_k\Pr[X_k > t] = \prod_ke^{-H_k(t)} = e^{-\sum_kH_k(t)}. \tag{5}
$$

**Cumulative hazards add.** For constant rates $\lambda_{\mathrm{sys}} = \sum\lambda_k$ and
$\mathrm{MTBF}_{\mathrm{sys}} = (\sum 1/\mathrm{MTBF}_k)^{-1}$ — the same form as resistors in
parallel.

**Numbers.** The subsystems of the single robot used in this lesson (approximated by constant
rates):

| Subsystem | MTBF (h) | Share | System MTBF if removed | $R(2\,\mathrm{h})$ if removed |
|---|---|---|---|---|
| Communication | 40 | $40.5\%$ | $27.3$ | $0.929$ |
| Mobility | 60 | $27.0\%$ | $22.2$ | $0.914$ |
| Perception | 120 | $13.5\%$ | $18.8$ | $0.899$ |
| Power | 150 | $10.8\%$ | $18.2$ | $0.896$ |
| Computation | 200 | $8.1\%$ | $17.6$ | $0.893$ |
| **Whole** | $16.2$ | | | $0.884$ |

Each part has an MTBF of 40 to 200 hours, yet the system has $16.2$ hours. **Five parts that are
each "fairly reliable" do not make a reliable system.** And removing the weakest link
(communication) **entirely** raises the MTBF only to $27.3$ hours — the next weakest link is
waiting.

**Teams.** If $n$ robots are independent with mission reliability $R$ each, the number of
survivors is $\mathrm{Bin}(n, R)$, and needing at least $k$ gives the sum in (2). At $R = 0.884$:

| Team | Needed | Reliability |
|---|---|---|
| 1 robot | 1 | $0.884$ |
| 3 robots | at least 1 | $0.9984$ |
| 3 robots | at least 2 | $0.963$ |
| 4 robots | at least 2 | $0.994$ |
| 4 robots | at least 3 | $0.931$ |

**Common causes.** The table above rests on the assumption that the robots fail
**independently**. Suppose a fraction $\beta_{\mathrm{cc}}$ of the failure rate comes from causes
that strike the whole team at once (communication infrastructure, corruption of a shared map,
the same software bug, weather). Then each robot has an independent failure rate
$(1-\beta_{\mathrm{cc}})\lambda$, the common failure rate is $\beta_{\mathrm{cc}}\lambda$, and

$$
R_{\mathrm{cc}} = e^{-\beta_{\mathrm{cc}}\lambda t}, \qquad R_{\mathrm{ind}} = e^{-(1-\beta_{\mathrm{cc}})\lambda t}
$$

go into (2). The reliability of "at least 1 of 3":

| $\beta_{\mathrm{cc}}$ | 0 | 0.1 | 0.3 |
|---|---|---|---|
| Team reliability | $0.9984$ | $0.9866$ | $0.9631$ |
| Failure probability | $0.0016$ | $0.0134$ | $0.0369$ |

**10% common cause multiplies the failure probability by 8.** Redundancy works only on
independent failures, and however large the team, $R_{\mathrm{team}} \le R_{\mathrm{cc}}$. The
reliability of a multi-robot system is set not by the number of robots but by **what they
share**.

**Where the assumptions break**: (a) (5) used the **independence** of the subsystems. In reality
one failure calls another — a voltage drop restarts the computer, which loses localization. The
log tends to record the last symptom (loss of localization) as the cause. (b) "Failure = mission
failure" was assumed. A well-designed system moves into **degraded operation** on many failures
(return autonomously when communication drops), and then the mission reliability is set not by
the failure rate but by **the rate of failed recovery**. (c) The robots of the team were taken to
be identical. In a heterogeneous team the roles (relay, explorer) differ in how replaceable they
are, and instead of the binomial of (2) a structure function per role is needed.

### R3 — a non-constant failure rate

**Three regimes.** The hazard function is usually bathtub shaped: early failures (assembly
defects, configuration errors, failed initialization: $h$ **decreasing**), random failures ($h$
constant), wear-out ($h$ increasing). The Weibull $H(t) = (t/\eta)^\beta$ expresses all three with
the single parameter $\beta$.

**A robot mission starts from scratch every time.** That is the point. Factory equipment is
switched on once and runs for long, but a field robot is powered up, initialized and sent off for
every mission. Early failures come back **on every mission**. So for the same cumulative time the
reliability depends on how the missions are divided ($\eta = 30$ h):

| $\beta$ | One 8-hour mission, $e^{-(8/\eta)^\beta}$ | Eight consecutive 1-hour missions all succeed, $e^{-8(1/\eta)^\beta}$ |
|---|---|---|
| $0.6$ (early failures) | $0.636$ | $0.354$ |
| $1.0$ (constant) | $0.766$ | $0.766$ |
| $2.0$ (wear-out) | $0.931$ | $0.991$ |

The two agree only at $\beta = 1$ — **the very notion of "cumulative operating time" is the
constant-rate assumption.** For a system dominated by early failures, time accumulated over many
short tests says nothing about the reliability of a long mission (it looks worse than it is), and
conversely a few long tests hide the failure rate of short missions.

**The extrapolation error of the exponential model.** An exponential model fitted on missions of
length $t_0$ is fitted so that roughly $\hat\lambda t_0 \approx H(t_0)$ (it matches the cumulative
hazard at that length). Extrapolating to another length $t$, the predicted cumulative hazard is
$H(t_0)\,t/t_0$ while the truth is $H(t_0)(t/t_0)^\beta$, so

$$
\frac{\text{predicted cumulative hazard}}{\text{true cumulative hazard}} = \Big(\frac{t}{t_0}\Big)^{1-\beta}. \tag{6}
$$

For $\beta < 1$ the ratio is below 1 at $t < t_0$ — the hazard is **under**-predicted (optimism)
— and above 1 at $t > t_0$ (pessimism). On the field log of the reproduction task (80 two-hour
missions):

| Mission length | $R$ predicted by the exponential model | True $R$ |
|---|---|---|
| 0.5 h | $0.933$ | $0.889$ |
| 2 h (test condition) | $0.758$ | $0.734$ |
| 8 h | $0.329$ | $0.421$ |

**How to notice it in the data.** Look at where within the mission the failure times cluster. In
the field log **5 of the 14** mobility failures occurred **in the first 15 minutes**. The first
15 minutes are $14.6\%$ of the total operating time, so a constant rate would predict $2.0$.
Fitting a Weibull gives $\hat\beta = 0.66$ ($\hat\eta = 23.4$ h), and the likelihood-ratio test
against the exponential model gives $p = 0.080$ — **14 failures do not establish early failures
at the usual 5% level.** The honest report is "suggestive of early failures but not conclusive",
and the practical conclusion is the same anyway: instrument the first 15 minutes after departure
separately.

**Where the assumptions break**: (a) the Weibull takes the hazard to be **monotone**. A real
bathtub curve can decrease and then increase within one mission (failed initialization + battery
depletion), and fitting a single $\beta$ lets the two cancel into $\hat\beta \approx 1$ — it
looks like a constant rate but is not. (b) Conditions differ from mission to mission (terrain,
weather, operator). The hazard of data pooled over conditions decreases in appearance "because
the hard missions fail first and drop out" — the **heterogeneity effect**, which gives
$\hat\beta < 1$ without any early failures. Early failures and heterogeneity call for different
remedies (check-out procedures versus mission screening), so they must be told apart (problem
P7).

### R4 — competing risks and the priority of improvements

**Competing risks.** A mission ends at its **first** failure, so the failure time of mode $k$ is
not observed if another mode fails first — it is **censored** by the other modes. The cumulative
hazard per mode is obtained with the Nelson–Aalen estimator: sort the failure (or termination)
times and, at each failure of mode $k$, add the reciprocal of the number $Y$ of **missions still
in progress** at that moment:

$$
\hat{H}_k(t) = \sum_{i:\ t_i \le t,\ \text{mode } k}\frac{1}{Y(t_i)}. \tag{7}
$$

By (5), $\hat{R}(t) = \exp(-\sum_k\hat{H}_k(t))$, and the hypothetical reliability with mode $k$
removed is (3).

**Analysis of the field log** (80 two-hour missions, $136.8$ h cumulative, 19 failures, 61
completions):

| Mode | Failures | Share (95% interval) | $\hat{H}_k(2\,\mathrm{h})$ | $\hat{R}(2\,\mathrm{h})$ if removed | Truth |
|---|---|---|---|---|---|
| Mobility | 14 | $73.7\%$ $[48.8, 90.9]$ | $0.199$ | $0.932$ | $0.914$ |
| Communication | 3 | $15.8\%$ $[3.4, 39.6]$ | $0.042$ | $0.797$ | $0.771$ |
| Perception | 2 | $10.5\%$ $[1.3, 33.1]$ | $0.028$ | $0.786$ | $0.746$ |
| Power | 0 | $0\%$ $[0, 17.6]$ | $0$ | $0.764$ | $0.744$ |
| Computation | 0 | $0\%$ $[0, 17.6]$ | $0$ | $0.764$ | $0.741$ |
| **Current** | 19 | | $0.269$ | $0.764$ | $0.734$ |

(The point estimate of the overall MTBF is $136.8/19 = 7.2$ h, with the 95% interval
$[4.6, 12.0]$ h of (1).)

**Three things to read.** (a) **The priority is clear.** Removing mobility failures gives
$0.764 \to 0.932$, and nothing else gets past $0.80$. Over 5000 bootstrap resamples the
probability that mobility is the most frequent mode is $0.998$ — even 19 failures **settle the
first place**. (b) **Second place and below cannot be settled.** The intervals of communication
(3 failures) and perception (2) almost coincide. Writing "communication is more of a problem
than perception" from this data is over-interpretation. (c) **Zero failures is not zero.** Power
and computation never failed, yet the 95% upper bound on their share is $17.6\%$, and in the true
model both are real. The observation time is $136.8$ h and the MTBFs of those modes are 150 and
200 hours, so **it is only to be expected that they do not show**.

**The rule for prioritizing.** What (3) gives is the value of removing a mode **completely**. A
real improvement is partial and costs differ, so the value of a candidate improvement $a$ is
compared as

$$
\Delta_a = R(t)\Big[\exp\big(\epsilon_a\hat{H}_{k(a)}(t)\big) - 1\Big] \Big/ \text{cost}_a \tag{8}
$$

($\epsilon_a$: the fraction by which the improvement reduces the cumulative hazard of the mode).
This is why one does not choose by share (the Pareto chart) alone — if the second-ranked mode can
be reduced by 90% cheaply, that can beat reducing the first-ranked mode by 30% expensively.

**Where the assumptions break**: (a) (3) assumes the modes are **independent** — removing mode
$k$ leaves the hazards of the others unchanged. In reality fixing one mode lets the mission go on
longer and farther, so that other modes show up **under conditions never reached before** (fix
mobility and the robot enters the communication dead zone). A competing-risks analysis speaks
only of "the priority among what has shown up". (b) **The classification itself** of failure
modes is a judgment. Is "loss of localization" a failure of perception or of the vibration
(mobility) that caused it? The classification rules have to be fixed in advance and two people
have to classify independently, with their agreement reported (`r1-experiment-design`). (c) All
failures were counted with equal weight. Without distinguishing failures that lose the mission
from failures recovered by a restart, the priority follows **frequency** and not
**consequence**.

### R5 — designing a field trial

**Failure-free trials.** With mission reliability $R$ the probability of $n$ consecutive
successes is $R^n$. The probability of observing $n$ consecutive successes although the true
reliability is **below** the target $R_0$ is at most $R_0^n$, so making that at most $1 - C$
gives

$$
R_0^n \le 1 - C \iff n \ge \frac{\ln(1-C)}{\ln R_0},
$$

which is (4). This is the one-sided Clopper–Pearson lower limit $(1-C)^{1/n}$ of
`s4-evaluation-science` solved for $n$.

| Target $R_0$ | Failure-free ($C = 0.9$) | One failure allowed | Two failures allowed |
|---|---|---|---|
| $0.90$ | 22 | 38 | 52 |
| $0.95$ | 45 | 77 | 105 |
| $0.99$ | 230 | 388 | — |

**How to read it.** (a) 22 consecutive successes correspond to "90% reliability at 90%
confidence". Given that field trials usually number around 10, most claims of "validated in the
field" amount to about $R \ge 0.79$ (10 failure-free trials, $0.1^{1/10}$). (b) Allowing one
failure takes 1.7 times the trials — the practice of **restarting the count from zero whenever a
failure occurs** uses the "failure-free" column of this table while in fact making several
attempts, and so overstates the confidence level (the selection bias of `s4-evaluation-science`
R3). (c) $R = 0.99$ takes 230 trials. At 2 hours per mission that is 460 hours of failure-free
field testing. High-reliability requirements are therefore argued not by system-level tests but
by **decomposing** through (5) into subsystems (accelerated tests, simulation, component data).

**A checklist for the trial design.** What a field trial plan has to answer: (a) the length of
the missions and **the range of conditions** (terrain, weather, communication) — the intervals
of (1) and (4) speak only about the conditions tested. (b) The **operational definition** of a
failure (is one operator intervention a failure?). (c) The stopping rule — decide **in advance**
after how many trials to stop and what to report. (d) The minimum log fields: mission start and
end time, reason for termination, time and kind of each intervention, software version.
(e) Whether the system **was changed** between trials — if it was, failures before and after
cannot be pooled into one population.

**Where the assumptions break**: (4) assumes the missions are independent and concern **the same
system under the same conditions**. In a field trial the system is fixed every time it fails, so
it keeps changing — a good thing in itself (reliability growth), but successes after a fix must
not be counted together with successes before it. Reliability-growth models (Duane, Crow–AMSAA)
take the cumulative number of failures to grow as $T^{b}$ ($b < 1$) and estimate the "current"
MTBF. **[D1]** And most fundamentally, if the test conditions do not cover the deployment
conditions no statistics bridge the gap — in field robotics a large share of failures comes from
"conditions that were not tested".

## Proof sketch

### R1 — the chi-square interval of the MTBF [D3]

**Hypotheses**
H1: failures form a (homogeneous) Poisson process of constant rate $\lambda$ — times between
failures are independent exponentials.
H2: the test ends at a fixed cumulative time $T$ (time truncation). The number of failures $r$
is the random variable.

**Conclusion** C: the interval of (1) has coverage at least $1-\alpha$ for every $\lambda$.

**Strategy**: invert the tail probabilities of $r \sim \mathrm{Poisson}(\lambda T)$ (the same
construction as `s4-evaluation-science` R1). The identity between Poisson tails and the
chi-square (gamma) distribution gives the closed form.

1. **The distribution.** By H1 and H2, $r \sim \mathrm{Poisson}(\mu)$ with
   $\mu = \lambda T = T/\mathrm{MTBF}$.
2. **The tail identity.** In a Poisson process "at most $r$ events by time $\mu$" is the same as
   "the $(r+1)$-th event comes after $\mu$", and the time of the $(r+1)$-th event is
   $\mathrm{Gamma}(r+1, 1)$. Hence
   $$
   \Pr[\mathrm{Poisson}(\mu) \le r] = \Pr[\mathrm{Gamma}(r+1, 1) > \mu] = \Pr\big[\chi^2_{2r+2} > 2\mu\big],
   $$
   the last step being $2\,\mathrm{Gamma}(m, 1) \sim \chi^2_{2m}$.
3. **The upper limit on $\mu$.** Tail inversion: $\mu_U$ solves
   $\Pr[\mathrm{Poisson}(\mu_U) \le r] = \alpha/2$, and by step 2
   $2\mu_U = \chi^2_{1-\alpha/2,\,2r+2}$. Since $\mathrm{MTBF} = T/\mu$, this is the **lower**
   limit $2T/\chi^2_{1-\alpha/2,\,2r+2}$ of the MTBF.
4. **The lower limit on $\mu$.** In the same way, from
   $\Pr[\mathrm{Poisson}(\mu_L) \ge r] = \alpha/2$, $2\mu_L = \chi^2_{\alpha/2,\,2r}$ (for
   $r = 0$, $\mu_L = 0$ and the upper limit of the MTBF is $\infty$).
5. **Coverage.** The tail probabilities are monotone in $\mu$, so by the same argument as for
   Clopper–Pearson each side fails with probability at most $\alpha/2$. **C**. Because of
   discreteness it is conservative: measured coverage $0.979$ ($\mu = 5$, 20,000 draws).

**The case $r = 0$.** In step 3, $2\mu_U = \chi^2_{1-\alpha/2,\,2}$, and a chi-square with 2
degrees of freedom is an exponential, so $\mu_U = -\ln(\alpha/2)$. For a one-sided interval
$\mu_U = -\ln\alpha$, that is $\mathrm{MTBF} \ge T/(-\ln\alpha) = T/3.0$ ($\alpha = 0.05$).

**Where it collapses if a hypothesis is removed**

- **Remove the constant rate in H1**: $r$ is not Poisson. With early failures and a restart for
  every mission the number of failures is more nearly proportional to the **number** of missions
  and its relation to cumulative **time** breaks — this is R3. The interval of (1) must then be
  read only as "the mean time between failures at this mission length" and must not be carried
  over to another length.
- **Remove the independence in H1** (failures come in clusters — a robot that failed is repaired
  in haste and fails again): the variance of $r$ exceeds the Poisson one (overdispersion) and the
  interval comes out **too narrow**. Look first at whether the gaps between failures are
  exponential (whether short gaps are over-represented).
- **Replace H2 by "the test ends at $r$ failures"** (failure truncation): the degrees of freedom
  of the lower limit are $2r$, not $2r+2$. Without knowing how the test ended one cannot know
  which formula applies. **"The test was ended because the third failure occurred" and "it was
  ended at 40 hours and there had been three" are different data.**

## Problem set

The answer policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★, R1)** Write the five steps of the proof sketch with no line missing, and
(a) prove the Poisson–gamma identity of step 2 by integration by parts or by a Poisson-process
argument, (b) show that in a failure-truncated test (ending at a fixed $r$ failures)
$2\lambda T \sim \chi^2_{2r}$ and state how the interval changes.
*Strategy + key inequality*: (b) follows from $T$ being a sum of $r$ independent exponentials (a
gamma), and in this case the interval is **exact** (there is no discreteness). The expansion is
withheld.

**P2 (derivation, ★, R2)** Derive (5) and show that when all $m$ subsystems have the same MTBF
$M$ the system MTBF is $M/m$. Then, for a requirement of "system MTBF 100 hours", find the MTBF
required of each of 20 subsystems, and find through (1) the failure-free time needed to
demonstrate it by field trial.
*Answer sketch*: 2000 hours each. Demonstrating it with a 95% one-sided lower limit needs
$T/3.0 \ge 2000$, that is 6000 failure-free hours per subsystem. **Decomposing a requirement
makes the requirement on the parts untestable** — this is why component data and accelerated
tests are needed.

**P3 (derivation, ★★, R3)** Derive (6), and show that in the Weibull model the probability of
consecutive successes when the mission is divided into $m$ equal parts with a restart each time
is $\exp(-m^{1-\beta}(t/\eta)^\beta)$. Explain whether "restarting often" helps or hurts for
$\beta < 1$ and for $\beta > 1$, and give one example of each in robot operation.
*Answer sketch*: each segment has cumulative hazard $(t/(m\eta))^\beta$ and there are $m$ of
them. For $\beta < 1$ restarting repeats the early failures and hurts (for example, sensor
initialization and calibration on every mission); for $\beta > 1$ restarting undoes the wear and
helps (for example, periodic resetting of a memory leak or of a drifting estimator).

**P4 (numerical, ★, R1, R5)** (a) 8 failures in 250 hours: find the point estimate and the 95%
interval of the MTBF. (b) 0 failures in 60 hours: find the 90% one-sided lower limit. (c) Find
the number of failure-free missions needed to demonstrate a mission reliability of $0.97$ at
confidence level $0.9$. (d) There have been 15 consecutive successes. What lower limit on the
reliability can be stated at 90% confidence?
*Answer*: (a) $31.25$ h,
$[2\cdot250/\chi^2_{0.975,18},\ 2\cdot250/\chi^2_{0.025,16}] = [15.9, 72.4]$ h.
(b) $60/(-\ln 0.1) = 26.1$ h. (c) $\lceil\ln 0.1/\ln 0.97\rceil = 76$. (d) $0.1^{1/15} = 0.858$.
(Tolerance 1%.)
*Check*: confirm that the interval of (a) contains the point estimate and is asymmetric (longer
on the upper side). See that (d) is far below "15/15 = 100%".

**P5 (numerical, ★★, R2)** A team of 4 robots succeeds if at least 3 survive. The mission
reliability of one robot is $0.9$ and 20% of the failures are common cause. Find (a) the team
reliability assuming independence and (b) the team reliability with the common cause, and
(c) answer which is better: increasing the team to 5 robots (at least 3 needed) or reducing the
common-cause fraction to 10%.
*Answer*: $\lambda t = -\ln 0.9 = 0.10536$. (a) $4\cdot0.9^3\cdot0.1 + 0.9^4 = 0.9477$.
(b) $R_{\mathrm{cc}} = e^{-0.02107} = 0.9791$, $R_{\mathrm{ind}} = e^{-0.08429} = 0.9192$,
$0.9791\times(4\cdot0.9192^3\cdot0.0808 + 0.9192^4) = 0.9791\times0.9649 = 0.9448$.
(c) 5 robots: $0.9791\times0.9953 = 0.9746$. Common cause 10%: $R_{\mathrm{cc}} = 0.9895$,
$R_{\mathrm{ind}} = 0.9095$, $0.9895\times0.9566 = 0.9466$. **In this setting adding robots is
better** — the requirement of at least 3 is tight, so independent failures still dominate.
(Tolerance $\pm0.002$.)
*Check*: confirm that the conclusion reverses when the requirement is changed to "at least 1"
(then the common cause dominates).

**P6 (implementation, ★★★, R3, R4)** Extend the field-log generator of the reproduction task to
imitate reliability growth, in which a **repair** follows each failure and lowers the hazard of
that mode (each failure increases the scale parameter $\eta$ of its mode by 15%). (a) Plot the
cumulative number of failures against cumulative time on log-log axes and estimate the slope,
(b) compare the MTBF from the whole data treated as one population with the MTBF estimated
**from the last 20 missions only**.
*Rubric*: (a) show that the slope is below 1 and report its value (b) show in numbers that the
MTBF of the whole data **under**-estimates the "current" system (c) compute through (1) how much
wider the interval gets when only the last 20 are used and describe the bias-variance trade in a
paragraph (d) repeat at least 500 times.

**P7 (counterexample, ★★, R3, R4)** (a) Construct a case in which every mission has a
**constant failure rate** and yet fitting a Weibull to the data gives $\hat\beta < 1$ — half the
missions under easy conditions (MTBF 100 h) and half under hard ones (MTBF 5 h) will do.
(b) Construct through (8) a case in which fixing the first-ranked mode of the Pareto chart is
**not** the best choice.
*Property checklist*: (a) reports the $\hat\beta$ of the pooled data together with the
$\hat\beta$ fitted per condition (both about 1). Property to confirm: an apparent decreasing
hazard can be not early failures but **heterogeneity**, and the remedies differ. (b) builds in
numbers a case where the $\epsilon$ of the first-ranked mode is small and its cost large.

**P8 (paper, ★★, R4, R5)** Read `ebadi2022-darpa-subt` and `roucek2019-darpa-subt-system` and
(a) make a table classifying the failures and limitations each paper reports into **failure
modes** (mode, symptom, the cause the authors give, location in the paper — section or page),
(b) separate those reported **quantitatively** (counts, times, rates) from those described only
anecdotally, (c) estimate, from the standpoint of (4), what level of reliability the authors'
field trials were large enough to demonstrate, (d) find whether there were failures that qualify
as the **common cause** of R2 in this lesson.
*Rubric*: (a) passes with at least 5 entries per paper, each with its source location. (b) is
the core — discovering that most are anecdotes and **writing exactly that** passes (inventing
numbers that are not there fails). (c) finds the number of trials in the paper and computes; if
you cannot find it, say so. (d) passes by naming at least one of communication, map sharing and
common software.

## Paper reading

**Two must-read papers.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read in three passes, and in the third pass concentrate on questions 5,
6 and 8. These two are long and descriptive, so find and read **the parts that describe
failures** first.

1. **Ebadi, Bernreiter, Biggie et al., "Present and future of SLAM in extreme underground
   environments" (2022, arXiv 2208.01787)** — role: `survey`.
   <https://arxiv.org/abs/2208.01787> (the parts describing each team's system and the parts on
   lessons learned and open problems)
   A paper that collects the SLAM systems of several teams of the DARPA Subterranean Challenge
   and the lessons they learned in the field. In this lesson it is read as material on **what
   broke in the field**.
   Additional questions: (a) which causes of failure do several teams report **in common**?
   (b) which problems did not show on laboratory benchmarks but did in the field, and how do the
   authors explain why? (c) how often do multi-robot map merging and communication appear as the
   cause of a failure?
2. **Rouček, Pecka, Čížek et al., "DARPA Subterranean Challenge: multi-robotic exploration of
   underground environments" (2020, MESAS 2019, LNCS)** — role: `standard`.
   <https://doi.org/10.1007/978-3-030-43890-6_22> (the parts on the system composition and on
   the competition results and lessons)
   A paper that reports one team's whole system (vehicles, sensors, communication, autonomy) and
   its experience in the competition. Material for reading system-level failure modes.
   Additional questions: (a) drawing the authors' system as the series structure of R2, how many
   subsystems are there and which was the weakest link? (b) how do the failure patterns of
   heterogeneous robots (wheeled, tracked, legged, flying) differ? (c) how many operator
   interventions were there, and were they counted as "failures"?

**Two recommended papers.** `carlson2005-ugv-failures` (the classic that tallies field failures
of ground robots by type — it reports the MTBF and the distribution of failure modes in actual
numbers, <https://doi.org/10.1109/TRO.2004.838027>) and `tranzatto2022-cerberus` (the winning
team's system and field experience, <https://doi.org/10.1126/scirobotics.abp9742>). Use them as
the comparison when building the table of problem P8.

**The ten fixed questions**: (1) what problem is solved under what assumptions (2) what exactly
could earlier work not do (3) the key idea in one line of mathematics (4) what is the theoretical
guarantee and **what is not guaranteed** (5) the independent and dependent variables and baselines
of the experiments, and were they tuned fairly (6) do the metrics match the claims, and are
variance and seeds reported (7) what information needed for reproduction is missing (8) if it is
wrong, which assumption to suspect first (9) computational and memory complexity and real-time
capability (10) what would you change to surpass it a year from now.

## Reproduction task

**Tier R2 (algorithm reimplementation).** Compute budget: one laptop CPU core, under 2 minutes in
total, at most 500 MB of memory. numpy + scipy only.

The task has two halves. **Parts A–E** build and validate the analysis tools on a field log
produced by a generator (data whose true model is known). **Part F** applies the same tools and
framework to **published field reports** — that is the actual deliverable of this lesson.

```python
"""Reproduction task of s5-field-deployment: generator of a field log with competing risks."""

import numpy as np

SEED = 20261117
MODES = ["comms", "mobility", "perception", "power", "compute"]
ETA = np.array([40.0, 25.0, 120.0, 150.0, 200.0])  # Weibull scale (hours)
BETA = np.array([1.0, 0.6, 1.0, 1.0, 1.0])  # Weibull shape - early failures in mobility only


def field_log(rng, n_missions=80, mission_h=2.0):
    """Operating time and reason for termination per mission. mode = -1: completed, no failure."""
    t = ETA * rng.weibull(BETA, size=(n_missions, len(MODES)))
    first, t_fail = t.argmin(1), t.min(1)
    duration = np.minimum(t_fail, mission_h)
    mode = np.where(t_fail <= mission_h, first, -1)
    return duration, mode
```

**Conventions.** "The field log" is **one** call of `field_log` on a generator created with
`np.random.default_rng(SEED)`. The bootstrap uses a generator **newly** created with `SEED`.

**Part A — MTBF and its interval.** Report the cumulative time $T$, the number of failures $r$,
the point estimate of the MTBF and the 95% interval of (1). Confirm the coverage of (1) at
Poisson $\mu = 5$ by 20,000 simulations.

**Part B — the distribution of failure modes.** Report the number of failures per mode, the
shares with their 95% Clopper–Pearson intervals, and, with 5000 bootstrap resamples of the
missions, the distribution of which mode is "the most frequent".

**Part C — checking the constant rate.** (a) For the mobility mode (failures of other modes and
mission completion are censoring) fit a Weibull by maximum likelihood and run the
likelihood-ratio test against the exponential model. (b) Compare the number of mobility failures
within the first 15 minutes of a mission with the fraction of the total operating time that the
first 15 minutes represent.

**Part D — improvement priority.** With the Nelson–Aalen estimate (7) find
$\hat{H}_k(2\,\mathrm{h})$ per mode, the current $\hat{R}(2\,\mathrm{h})$ and
$\hat{R}_{-k}(2\,\mathrm{h})$ with each mode removed, and compare with the truth (computed from
the parameters of the generator).

**Part E — extrapolation and trial design.** (a) Compare the $R(0.5\,\mathrm{h})$ and
$R(8\,\mathrm{h})$ predicted by the exponential model with the truth. (b) Reproduce with (4) the
failure-free trial counts of the table in the text, and find the counts with one failure allowed
from the binomial cumulative distribution.

**Part F — classifying the failure modes of published field reports.** From the two must-read
papers (the recommended ones may be added) (a) build the classification table of problem P8(a),
(b) count the **occurrences** per mode in the format of Part B, marking modes whose occurrences
cannot be counted (anecdotes only) as "reported, not quantified", (c) present the top three
improvement priorities in the framework of (8) **with their grounds**.

**Acceptance criteria — all six conditions must hold to pass.**

1. **Part A** — $T = 136.82$ h and $r = 19$ (61 completions), with MTBF $7.20$ h and 95%
   interval $[4.61, 11.96]$ h (tolerance $\pm0.02$; when the conventions are followed). The
   simulated coverage is $0.979 \pm 0.005$, **at least the nominal $0.95$**.
2. **Part B** — the failure counts are communication 3, mobility 14, perception 2, power 0,
   computation 0, and the share of mobility is $0.737$ with interval $[0.488, 0.909]$. In the
   bootstrap the probability that mobility is the most frequent is at least $0.99$. **Print
   explicitly the upper bound $0.176$ on the share of the two modes with 0 failures.**
3. **Part C** — (a) for the mobility mode $\hat\beta = 0.657 \pm 0.01$,
   $\hat\eta = 23.4 \pm 0.5$ h, likelihood-ratio statistic $3.06 \pm 0.05$ and
   $p = 0.080 \pm 0.005$ — report that it **is not rejected at the 5% level**. (b) Mobility
   failures in the first 15 minutes are 5 of 14 and the fraction of operating time in that window
   is $0.146$.
4. **Part D** — $\hat{R}(2\,\mathrm{h}) = 0.764$, and the reliabilities with a mode removed are
   mobility $0.932$, communication $0.797$, perception $0.786$, power and computation $0.764$
   (tolerance $\pm0.002$). Print them next to the truth
   ($0.734$; $0.914, 0.771, 0.746, 0.744, 0.741$) and confirm that **the first-ranked mode is the
   same in the estimate and in the truth**.
5. **Part E** — (a) the predictions of the exponential model are $0.933$ and $0.329$ and the
   truth is $0.889$ and $0.421$ (tolerance $\pm0.002$) — state explicitly that it is **optimistic
   on the short side and pessimistic on the long side**. (b) The failure-free counts are
   $22, 45, 230$ and with one failure allowed $38, 77, 388$ (exact agreement).
6. **Part F** — the classification table has at least 5 entries per paper and **every entry has
   a source location (section or page)**. Quantitative and anecdotal reports are separated. Each
   of the three priorities has at least one sentence of grounds for each of the three elements of
   (8) (size of the mode, effect of the improvement, cost). **No number absent from the papers
   has been filled in by guesswork** — where an estimate is needed, mark it as an estimate.

**Comparison**: (a) the baseline of Parts A–E is the value computed from the true parameters of
the generator. (b) The baseline of Part C is the constant-rate (exponential) model. (c) For Part
F the distribution of failure modes reported by `carlson2005-ugv-failures` is the comparison —
write a paragraph on how the mode categories of your table correspond to those of that paper.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| $T$ is 160 | Failed missions were also counted as 2 hours | Operating time runs up to the failure time. Use the sum of `duration` |
| The lower limit of the MTBF interval exceeds the upper | The tails of the chi-square quantiles were swapped | $\chi^2_{0.975,\,2r+2}$ for the lower limit, $\chi^2_{0.025,\,2r}$ for the upper |
| The $\hat\beta$ of the mobility mode is near 1 | Failures of other modes were **excluded** rather than censored | Check that the survival term $-(t/\eta)^\beta$ of every mission enters the likelihood |
| The likelihood ratio is negative | The Weibull optimization did not converge | First check that a Weibull with $\beta$ fixed at 1 gives the same likelihood as the exponential model |
| The Nelson–Aalen $\hat{R}$ differs greatly from the completion fraction | The risk set $Y$ was not decreased | After sorting check that $Y$ goes $80, 79, \dots$. $\hat{R}(2\,\mathrm{h}) = 0.764$ is close to the completion fraction $0.7625$ |
| The reliability with a mode removed is below the current one | The sign in (3) is wrong | $R_{-k} = R/R_k \ge R$ |
| Every count in the table of Part F is filled in | Anecdotes were turned into numbers | Find again where in the paper that number is written. If it is not there, change it to "not quantified" |

## Open problems

- **(Open problem) Reliability models for learned components** — the models of R1–R3 treat a
  failure as an event that happens in time. The "failure" of learned perception or of a learned
  policy is a function not of time but of **the input** — it happens on out-of-distribution
  scenes and happens again on the same scene. The MTBF is the wrong measure for such failures.
  Current approaches: failure rates per operational design domain (ODD), interventions per
  distance travelled. What is missing: a model that **predicts** the failure rate when the
  distribution of conditions changes during deployment — the same gap as the open problem of
  `s4-safety-ood`.
- **(Open problem) Identifying common-cause failures of multiple robots in advance** — R2 shows
  that the common cause sets the ceiling of team reliability, but what the common causes are is
  usually learned **after the failure** (corruption of a shared map, a wrong loop closure of one
  robot spreading through the team — the rumor propagation of
  `s5-comms-constrained-estimation`). Current approaches: fault-injection tests, isolating and
  validating the state shared between robots. What is missing: a way to estimate at design time,
  from the system structure (what is shared), an **upper bound** on the common-cause fraction.
- **(Open problem) Test methods for long-term autonomy** — R5 shows that even a 99% reliability
  is hard to demonstrate by field trial. For a system aiming at months of unattended operation
  the test period is shorter than the mission period. Current approaches: accelerated testing
  (shorter, under harsher conditions), combining simulation with real logs, reliability-growth
  models. What is missing: acceleration factors for failures dominated by software — autonomy
  software has no counterpart of the temperature and vibration acceleration of hardware.
- **(Open problem) A reporting standard for field failures** — as problem P8 makes plain, field
  papers describe failures anecdotally and leave out the denominator (number of attempts,
  operating time). Comparison between papers and between systems is therefore impossible.
  Current approaches: the official scores and published logs of competitions, and failure-case
  datasets of some laboratories. What is missing: a consensus of the field on the operational
  definition of a failure, on a classification scheme and on the minimum reported fields
  (operating time, number of interventions, reasons for termination) — the field version of the
  artifact criteria treated in `r1-reproducibility-artifacts`.

## Concept check

Take it with `rc quiz s5-field-deployment`. This quiz is a **concept check only**; the real work
is the problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

## How to study this stage

1. **Read the table of the three differences first (10 min)** — the table in "Setup and
   notation". Apply the three ways a field trial differs from a laboratory evaluation to one
   robot system you know.
2. **The proof of R1 from a blank page (40 min)** — the Poisson–gamma identity is the key. Put it
   next to the Clopper–Pearson proof of `s4-evaluation-science` and see that it has the same
   structure (tail inversion). Then compute the interval for 3 failures in 40 hours yourself.
3. **(5) and team reliability (40 min)** — rebuild the table of parts, then vary the common-cause
   fraction from 0 to 0.5 and plot the team reliability. See the ceiling that adding robots
   cannot pass.
4. **Run Parts A and B (40 min)** — read from the intervals **what can and what cannot be said**
   from 19 failures: first place is settled, second and below are not, and zero failures is not
   zero.
5. **Doubt the constant rate with Part C (40 min)** — see the failures clustered in the first 15
   minutes, and see that the test nonetheless gives $p = 0.08$. How to write "suggestive but not
   conclusive" is the most practical exercise of this lesson.
6. **Parts D and E (50 min)** — implement Nelson–Aalen, build the table of reliabilities with a
   mode removed, and confirm that the extrapolation of the exponential model is wrong in both
   directions. Build the table of (4) and compute, for your own research, "what did our field
   trial demonstrate".
7. **The two papers (150 min)** — start from the parts that describe failures. As you read, look
   for **the denominator** (how many attempts, how many hours). Usually it is not there — that
   is the finding. The one-page note per paper is **mandatory**.
8. **Part F: build the classification table (60 min)** — the final deliverable of this lesson.
   Do not invent numbers. Record anecdotes as anecdotes and write three priorities with their
   grounds in the framework of (8).
9. **Close the module (30 min)** — this is the last lesson of S5. For each algorithm of the
   previous five lessons write down one "failure mode that breaks it in the field" (consensus ↔
   loss of communication, distributed SLAM ↔ propagation of a wrong loop closure, MAPF ↔
   localization error, active perception ↔ correlated sensor noise, distributed estimation ↔
   double counting). That table ties the algorithms of S5 to this lesson.

**Pass criterion**: from a blank page you can derive the five steps of R1 and (2), (3), (4), (5)
and (6); you can compute the interval of the MTBF from a failure count and an operating time; you
can say what goes wrong in which direction when the constant-rate assumption fails; you have code
that satisfies all six conditions of the reproduction task and **a failure-mode classification
table with sources**; and you have notes on the two papers.
