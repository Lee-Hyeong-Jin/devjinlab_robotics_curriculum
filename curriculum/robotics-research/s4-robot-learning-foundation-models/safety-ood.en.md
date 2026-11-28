---
id: s4-safety-ood
lang: en
title: Safety, OOD and failure modes
summary: >-
  Separate **what the uncertainty estimates of a learned policy guarantee from what they do not**.
  Prove the marginal coverage guarantee of split conformal prediction from exchangeability alone,
  and derive that the guarantee is an average over calibration sets, so the realized coverage
  scatters as a beta distribution, and that it collapses in closed form under distribution shift.
  Show that the variance of an ensemble over- or under-estimates the error depending on a single
  quantity, the correlation of the members' errors, and so carries no guarantee; and derive that
  the optimal threshold of an abstention (ask-for-help) policy is the cost ratio $c_h/c_f$, which
  prices safety in human intervention load.
objectives:
  - Prove the marginal coverage guarantee of split conformal prediction from exchangeability and write its lower and upper bounds.
  - Derive that the realized coverage given a calibration set follows a beta distribution and compute the calibration sample size required.
  - Derive how much coverage is lost under distribution shift and explain what weighted conformal prediction requires.
  - Derive, from the correlation of the members, the conditions under which the ensemble variance over- or under-estimates the prediction error.
  - Derive the optimal threshold of an abstention policy from the costs and compute the trade between intervention load and selective risk.
tags: [safety, out-of-distribution, conformal-prediction, ensembles, abstention, research]
---

# Safety, OOD and failure modes

## Setup and notation

`s4-evaluation-science` covered the statistics of evaluating a policy **before deployment**. This
lesson covers the devices that let a policy say, **during deployment**, "do not trust me now", and
the exact scope of the guarantees those devices give. We use the notion of distribution shift of
`c8-generalization-sim2real` as it stands. The recommended prerequisites are those two lessons.

| Symbol | Meaning |
|---|---|
| $(x_i, y_i)$ | Input (observation, instruction) and ground truth (expert action, success or failure, …) |
| $\hat{\mu}(x)$ | The learned predictor. Assumed trained **independently of the data used for calibration** |
| $s_i = s(x_i, y_i)$ | Nonconformity score. For example $\lvert y_i - \hat{\mu}(x_i)\rvert$ |
| $n$ | Number of calibration samples |
| $\alpha$ | Allowed error rate. $0.1$ in this lesson (target coverage 90%) |
| $\hat{q}$ | The $\lceil(n+1)(1-\alpha)\rceil$-th smallest calibration score |
| $C(x) = \{y : s(x,y) \le \hat{q}\}$ | The prediction set (interval) |
| Exchangeable | The joint distribution is invariant to reordering. Holds for i.i.d. data |
| $M$, $c$ | Number of ensemble members, pairwise correlation of the members' errors |
| $u$, $\tau$ | Uncertainty score and abstention threshold (if $u > \tau$, do not act and ask for help) |
| $c_f$, $c_h$ | Cost of one failure and of one request for help |

**Three layers of defence** are the map of this lesson (the system-level view of
`sinha2022-system-level-ood`).

| Layer | Question | Tool | Condition for a guarantee |
|---|---|---|---|
| Uncertainty quantification | How far can this prediction be trusted? | Conformal prediction (R1–R3), ensembles (R4) | Exchangeability / none |
| Runtime monitoring | Is the current input outside the training distribution? | An OOD score and a threshold | Only on the distribution where the threshold was calibrated |
| Fallback | What to do when it cannot be trusted? | Abstain and ask for help (R5), safe stop | When the cost model is right |

## Key results

The bracket gives the derivation depth (D0 cited / D1 skeleton / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (marginal coverage of split conformal prediction) [D3]** — if the calibration scores
  $s_1,\dots,s_n$ and the test score $s_{n+1}$ are exchangeable then, **whatever the predictor and
  whatever the distribution**,
  $$
  1 - \alpha \;\le\; \Pr\big[y_{n+1} \in C(x_{n+1})\big] \;\le\; 1 - \alpha + \frac{1}{n+1} \tag{1}
  $$
  (the upper bound when the scores have no ties). The proof is the single sentence "among $n+1$
  exchangeable values the rank of the last one is uniform". Measured in the reproduction task: a
  mean coverage of $0.9008$ at $n = 200$ (theory $181/201 = 0.9005$).
- **R2 (that guarantee is an average — the distribution of the realized coverage) [D2]** — the
  probability in (1) is an average that includes the calibration set. With **one calibration set
  fixed** the coverage is a random variable and
  $$
  \Pr\big[y \in C(x) \mid \text{calibration set}\big] \;\sim\; \mathrm{Beta}(k,\; n+1-k),
  \qquad k = \lceil(n+1)(1-\alpha)\rceil. \tag{2}
  $$
  At $n = 100$ its standard deviation is $0.030$ and **5.5% of calibration sets give a coverage
  below 85%**. Reducing the standard deviation to $0.007$ takes $n = 2000$. Moreover (1) is a
  **marginal** guarantee and does not hold region by region in the input — measured, $0.993$ in
  the easy region and $0.781$ in the hard one.
- **R3 (collapse under distribution shift) [D2]** — when exchangeability breaks, (1) is gone. If
  the residuals are Gaussian and the residual scale at test time is multiplied by $\kappa$, the
  coverage falls to
  $$
  2\Phi\!\left(\frac{z_{1-\alpha/2}}{\kappa}\right) - 1 \tag{3}
  $$
  that is $0.727$ at $\kappa = 1.5$ and $0.589$ at $\kappa = 2$. If a covariate shift has a
  **known** likelihood ratio $w(x) = p_{\text{test}}(x)/p_{\text{cal}}(x)$, a weighted quantile
  restores the guarantee **[D1]**, but for the shifts a robot meets that ratio is usually
  unknown.
- **R4 (the ensemble variance carries no guarantee) [D2]** — if the members' errors have variance
  $\sigma^2$ and pairwise correlation $c$, then
  $$
  \mathbb{E}[\text{ensemble variance}] = \sigma^2(1-c), \qquad
  \operatorname{Var}(\text{error of the ensemble mean}) = \sigma^2\Big(c + \frac{1-c}{M}\Big). \tag{4}
  $$
  **The variance measures only how much the members differ from one another, not how much they
  are wrong together.** At $M = 5$ the two quantities coincide at the single point $c = 0.444$,
  and at $c = 0.8$ the actual error is $4.2$ times the variance, so the measured coverage of the
  nominal 90% interval is $0.534$. **Calibrating** the same score with conformal prediction
  restores $0.90$ regardless of $c$.
- **R5 (the optimal abstention threshold and its price) [D2]** — if the failure probability at
  uncertainty score $u$ is $\pi(u)$, the rule that minimizes the expected cost is
  $$
  \text{act} \iff \pi(u) < \frac{c_h}{c_f} \tag{5}
  $$
  (Chow's rule). For $\pi(u) = 0.02 + 0.6u^2$, $u \sim U(0,1)$, $c_f = 10$, $c_h = 1$ the optimal
  threshold is $\tau^\star = 0.365$ and the expected cost drops from $2.20$ (always act) to
  $0.805$, but **the price is calling a human in 63.5% of trials**. Safety is not free; it is
  paid for in intervention load.

## Derivation

### R2 — the distribution of the realized coverage

Fixing the calibration set fixes $\hat{q}$, and the probability that a new score falls below it is
$F(\hat{q})$ ($F$ the cumulative distribution of the scores, taken continuous). $\hat{q}$ is the
$k$-th order statistic $s_{(k)}$ of $n$ samples, so

$$
\text{coverage} = F\big(s_{(k)}\big) = U_{(k)},
$$

where $U_i = F(s_i)$ is uniform on $(0,1)$ (the probability integral transform) and $U_{(k)}$ is
its $k$-th order statistic. **The $k$-th order statistic of $n$ uniforms follows
$\mathrm{Beta}(k, n+1-k)$** (its density is $\propto u^{k-1}(1-u)^{n-k}$: $k-1$ below, $n-k$
above, one in place). This is (2). Its mean is $k/(n+1) \ge 1-\alpha$ — the same expression as the
lower bound of (1) — and its variance is

$$
\operatorname{Var} = \frac{k(n+1-k)}{(n+1)^2(n+2)} \;\approx\; \frac{\alpha(1-\alpha)}{n}. \tag{6}
$$

| $n$ | $k$ | Mean | Standard deviation | 5% quantile | $\Pr[\text{coverage} < 0.85]$ |
|---|---|---|---|---|---|
| 20 | 19 | $0.905$ | $0.063$ | $0.784$ | $0.176$ |
| 100 | 91 | $0.901$ | $0.030$ | $0.848$ | $0.055$ |
| 500 | 451 | $0.900$ | $0.013$ | $0.877$ | $0.0004$ |
| 2000 | 1801 | $0.900$ | $0.007$ | $0.889$ | $0.0000$ |

**How to read it.** A calibration sample of $n = 20$ is common with robot data (20 real-world
demonstrations). One then writes "90% guarantee" while **17.6% of calibration sets actually give
less than 85%**. The guarantee is not false — averaged over redrawing the calibration set it is
90%. But a deployed robot lives with **one** calibration set. The honest statement is therefore
"with probability $1-\delta$ the coverage is at least $1-\alpha$", and for that one takes $k$
larger, so that the $\delta$ quantile of (2) is $1-\alpha$ (problem P2).

**Marginal versus conditional.** (1) is an average over $x$ as well. The setting of the
reproduction task is a heteroscedastic regression whose noise grows in proportion to
$\lvert x\rvert$, and the measurement for the absolute-residual score is

| Region | Coverage |
|---|---|
| Overall | $0.901$ |
| Easy region ($\lvert x\rvert < 0.2$) | $0.993$ |
| Hard region ($\lvert x\rvert > 0.8$) | $0.781$ |

**The 90% average is made of 78% where it is hard and 99% where it is easy** — and the hard
places are the ones that matter for safety. Dividing the score by the noise scale
($s = \lvert y - \hat{\mu}\rvert/\hat{\sigma}(x)$) brings the two regions to $0.899$ and $0.902$.
But only **when that $\hat{\sigma}(x)$ is estimated correctly**.

**Where the assumptions break**: (2) is the exact distribution for a continuous score
distribution and i.i.d. calibration and test data. Using several steps of the same episode as
calibration samples makes the samples correlated, so **the effective $n$ drops** and the realized
coverage scatters more widely than (2) — the same violation as the overdispersion of
`s4-evaluation-science` R1. The unit of calibration must be the episode, not the step. And it is
known that "guaranteeing conditional coverage at every $x$" is **impossible** without
distributional assumptions — what is possible is only a guarantee for each of finitely many
groups fixed in advance.

### R3 — collapse under distribution shift

**Setting.** At calibration time let the residual be $y - \hat{\mu}(x) \sim \mathcal{N}(0, \sigma^2)$
with plenty of calibration samples. Then $\hat{q} \to \sigma z_{1-\alpha/2}$ ($1.645\sigma$ at
$\alpha = 0.1$).

**Scale shift.** If at test time the residual is $\mathcal{N}(0, \kappa^2\sigma^2)$ (the system
has entered a region where the model fits worse),

$$
\Pr\big[\lvert y - \hat{\mu}\rvert \le \hat{q}\big]
 = \Pr\Big[\lvert Z\rvert \le \frac{z_{1-\alpha/2}}{\kappa}\Big]
 = 2\Phi\Big(\frac{z_{1-\alpha/2}}{\kappa}\Big) - 1,
$$

which is (3). **Mean shift.** If the residual acquires a bias $\delta\sigma$ the coverage is
$\Phi(z_{1-\alpha/2} - \delta) - \Phi(-z_{1-\alpha/2} - \delta)$.

| Scale $\kappa$ | 1 | 1.25 | 1.5 | 2 | 3 |
|---|---|---|---|---|---|
| Coverage | $0.900$ | $0.812$ | $0.727$ | $0.589$ | $0.417$ |

| Bias $\delta$ | 0 | 0.5 | 1 | 2 |
|---|---|---|---|---|
| Coverage | $0.900$ | $0.858$ | $0.736$ | $0.361$ |

**The interval does not widen.** That is the point — $\hat{q}$ is a constant fixed at calibration
time, so the width of the prediction interval stays the same when the input leaves the
distribution. Conformal prediction **does not detect OOD.** It only gives "an interval that is
right on average inside the distribution". Detection has to be done by a separate device (a
runtime monitor).

**Weighted conformal prediction (skeleton).** If only the covariates shift ($p(y\mid x)$ is the
same) and the likelihood ratio $w(x)$ is known, then using the quantile of the **weighted
empirical distribution** that gives the calibration scores weights proportional to $w(x_i)$ and
the test point a weight $w(x_{n+1})$ restores (1). The proof replaces the exchangeability of R1 by
"weighted exchangeability". **[D1]** The limitation is $w$: the shifts a robot meets (new
lighting, new objects, new users) usually have an unknown $w$, and if the support of the test
distribution leaves that of the calibration distribution $w = \infty$ and no weighting can fix it.

**Where the assumptions break**: (3) is the formula for Gaussian residuals and infinitely many
calibration samples. With heavier tails the coverage drops less at the same $\kappa$ (the
quantile is already wide), and with finite calibration the scatter of R2 is added. And **in closed
loop the shift creates itself** — the actions of the policy determine the next observation, so
small errors accumulate and the test distribution drifts away from the calibration distribution
(the covariate shift of `c8-imitation-learning`). The moment an interval calibrated on
demonstration data is used on **rollouts** of the policy, exchangeability is broken.

### R4 — what the ensemble variance measures and what it cannot

**The model.** Put the truth at 0 and write the prediction error of member $m$ as

$$
e_m = \sigma\big(\sqrt{c}\,z_0 + \sqrt{1-c}\,z_m\big), \qquad z_0, z_1, \dots, z_M \overset{\text{iid}}{\sim} \mathcal{N}(0,1). \tag{7}
$$

$z_0$ is the error **shared by all members** (the bias that comes from the same data, the same
architecture, the same pretrained weights) and $z_m$ the error that differs from member to member
(initialization, minibatch order). $\operatorname{Var}(e_m) = \sigma^2$ and
$\operatorname{Corr}(e_m, e_{m'}) = c$.

**The error of the ensemble mean.** $\bar{e} = \sigma(\sqrt{c}\,z_0 + \sqrt{1-c}\,\bar{z})$ with
$\bar{z} \sim \mathcal{N}(0, 1/M)$, so

$$
\operatorname{Var}(\bar{e}) = \sigma^2\Big(c + \frac{1-c}{M}\Big).
$$

**The ensemble variance.** In the sample variance $S^2 = \frac{1}{M-1}\sum_m(e_m - \bar{e})^2$,
$e_m - \bar{e} = \sigma\sqrt{1-c}\,(z_m - \bar{z})$ — **the shared error $z_0$ cancels in the
subtraction.** Hence $\mathbb{E}[S^2] = \sigma^2(1-c)$. This is (4).

**The ratio.** Dividing the actual error variance by the ensemble variance,

$$
\frac{\operatorname{Var}(\bar{e})}{\mathbb{E}[S^2]} = \frac{c + (1-c)/M}{1-c}. \tag{8}
$$

| $c$ ($M = 5$) | Ratio (8) | Measured coverage of the nominal 90% interval $\bar{e} \pm 1.645S$ | After conformal calibration |
|---|---|---|---|
| $0$ | $0.20$ | $0.979$ (too wide) | $0.893$ |
| $0.444$ | $1.00$ | $0.825$ | $0.906$ |
| $0.5$ | $1.20$ | $0.793$ | $0.909$ |
| $0.8$ | $4.20$ | $0.534$ | $0.902$ |
| $0.95$ | $19.2$ | $0.273$ | $0.907$ |

(Even at $c = 0.444$, where the ratio is 1, the measurement is $0.825$ rather than $0.90$ because
$S$ is estimated from 5 members — the right quantile is that of a $t$ distribution with 4 degrees
of freedom, not the normal one.)

**How to read it.** (a) If the members are **completely independent** ($c = 0$), the variance is
5 times the actual error and the interval is too wide. (b) Real deep ensembles share the data and
the architecture, so $c$ is large, and then the variance **severely underestimates** the actual
error. $c$ is not observable (observing it requires the ground truth), so from the ensemble
variance alone one cannot tell which case one is in — that is the precise meaning of **no
guarantee**. (c) The ensemble variance can still be **a good score**: if the variance is large on
inputs where the error is large (the ranking is right), it can be used as the score
$s = \lvert y - \bar{\mu}\rvert/S$ of conformal prediction and calibrated. That is the last
column of the table — the threshold $\hat{q}$ moves from $0.93$ ($c = 0$) to $9.63$ ($c = 0.95$),
absorbing $c$ **from the data**.

**Where the assumptions break**: (7) assumes the correlation $c$ does not depend on the input. In
reality **$c$ changes outside the distribution** — members that err differently inside the
training distribution (small $c$) can extrapolate in the same direction outside it and be wrong
together (large $c$). A $\hat{q}$ calibrated inside the distribution is then insufficient
outside: the collapse of R3 happens to ensembles as well. The empirical observation that the
ensemble variance grows on OOD inputs is not a guarantee, and depending on the architecture it
does not hold.

### R5 — the cost of abstention

**Setting.** On every trial the policy outputs an uncertainty score $u$. If $u \le \tau$ it acts
(failure probability $\pi(u)$, failure cost $c_f$); if $u > \tau$ it abstains and asks a human
(cost $c_h$, no failure). Let $\pi$ be increasing in $u$ (the assumption that the score is
**useful**).

**Pointwise optimization.** At a given $u$ the expected cost of acting is $c_f\pi(u)$ and the cost
of abstaining is $c_h$. Choosing the smaller gives (5): act when $c_f\pi(u) < c_h$. Since $\pi$ is
increasing this is the threshold rule $u < \tau^\star$ with $\pi(\tau^\star) = c_h/c_f$.

**The expected cost.** For $u \sim U(0,1)$,

$$
J(\tau) = c_f\int_0^\tau\pi(u)\,du + c_h(1-\tau), \qquad
J'(\tau) = c_f\pi(\tau) - c_h = 0 \iff \pi(\tau^\star) = \frac{c_h}{c_f}. \tag{9}
$$

**Numbers.** With $\pi(u) = 0.02 + 0.6u^2$, $c_f = 10$, $c_h = 1$:
$\tau^\star = \sqrt{(0.1 - 0.02)/0.6} = 0.3651$ and

| Policy | Expected cost | Abstention rate | Selective risk (failure rate among the trials acted on) |
|---|---|---|---|
| Always act ($\tau = 1$) | $2.200$ | $0\%$ | $0.220$ |
| Optimal ($\tau^\star = 0.365$) | $0.805$ | $63.5\%$ | $0.047$ |
| Conservative ($\tau = 0.2$) | $0.856$ | $80.0\%$ | $0.028$ |
| Always abstain ($\tau = 0$) | $1.000$ | $100\%$ | — |

**Three things to read.** (a) The optimal policy cuts the cost from $2.20$ to $0.805$ but **calls
a human in 63.5% of trials**. From the standpoint of autonomy this is a "36.5% autonomous"
system. (b) The cost is flat near the optimum (the cost at $\tau = 0.2$ is $0.856$) — setting the
threshold a little conservatively is cheap. The other side ($\tau = 0.6$, cost $0.950$) is
similar, so **whether $\pi(u)$ is correctly calibrated** matters far more than the precise value
of the threshold. (c) If the cost of help changes, the whole answer changes:

| $c_h$ | $0.2$ | $0.5$ | $1$ | $2$ | $5$ |
|---|---|---|---|---|---|
| $\tau^\star$ | $0$ | $0.224$ | $0.365$ | $0.548$ | $0.894$ |
| Minimum cost | $0.200$ | $0.455$ | $0.805$ | $1.343$ | $2.138$ |

For $c_h \le 0.2$ ($c_h/c_f \le \pi(0) = 0.02$) **always asking the human is optimal** — even the
policy's most confident trial costs more than help. That policy is not worth deploying.

**Connecting the threshold to a guarantee.** (5) assumes $\pi(u)$ is **known**. In practice
$\tau$ has to be chosen from calibration data, and the logic of R1 applies as it stands: take
"failure when acting" as the loss on the calibration trials and choose, with a finite-sample
correction, the largest $\tau$ whose selective risk is below the target (conformal risk control).
Applying this to a language planner to calibrate "ask when ambiguous" is `ren2023-knowno`.

**Where the assumptions break**: (a) the assumption that $\pi(u)$ is increasing **breaks outside
the distribution** — a neural network can output high confidence (low $u$) on OOD inputs. The
most dangerous trials then pass the threshold. The safety of an abstention policy rests entirely
on the **rank validity** of the uncertainty score, and R3 and R4 say that it is not guaranteed
outside the distribution. (b) The costs were assumed constant. If the human's response time
grows, $c_h$ increases with the call frequency (a queue), and if the human becomes desensitized
to alarms the "no failure" bought with $c_h$ disappears. (c) Abstaining was assumed **always
safe**. In a dynamic task (a moving robot, an arm holding an object) stopping can itself be
dangerous, and what is needed then is not abstention but a safe fallback controller.

## Proof sketch

### R1 — coverage of split conformal prediction [D3]

**Hypotheses**
H1: the scores $s_1, \dots, s_n, s_{n+1}$ are **exchangeable**.
H2: the score function $s(\cdot,\cdot)$ and the predictor $\hat{\mu}$ were fixed independently of
these $n+1$ samples (the split: training data and calibration data do not overlap).
H3 (for the upper bound only): the scores are almost surely distinct (no ties).

**Conclusion** C: with $\hat{q}$ the $k = \lceil(n+1)(1-\alpha)\rceil$-th smallest of
$s_1,\dots,s_n$ ($\hat{q} = \infty$ if $k > n$), (1) holds.

**Strategy**: turn the coverage event into an event about a **rank**, and use that exchangeability
makes the rank uniform.

1. **Translating the event.** $y_{n+1} \in C(x_{n+1}) \iff s_{n+1} \le \hat{q} = s_{(k)}$. And
   "$s_{n+1}$ is at most the $k$-th of the $n$ calibration scores" is the same as "the rank of
   $s_{n+1}$ among all $n+1$ is at most $k$" (if $s_{n+1}$ is the $r$-th smallest overall there
   are $r-1$ calibration scores below it, and $s_{(k)} \ge s_{n+1}$ exactly when $r \le k$).
2. **Uniformity of the rank.** By H1 the joint distribution of $(s_1,\dots,s_{n+1})$ is invariant
   under permutations, so $s_{n+1}$ is equally likely to occupy any of the $n+1$ ranks. Under H3
   the rank is uniform on $\{1,\dots,n+1\}$.
3. **The probability.** $\Pr[\text{rank} \le k] = k/(n+1) = \lceil(n+1)(1-\alpha)\rceil/(n+1)$.
4. **The two bounds.** From $\lceil a\rceil \ge a$, $\ge 1-\alpha$; from $\lceil a\rceil < a + 1$,
   $< 1 - \alpha + 1/(n+1)$. **C**.
   (Without H3 ties act only in the direction of lowering the rank, so the lower bound still holds
   and only the upper bound is lost.)

**What the proof did not use.** That $\hat{\mu}$ is a good predictor, that the distribution is
Gaussian, that $n$ is large — none of these. A bad predictor merely produces a **wide** interval;
it does not lose coverage. The guarantee is about **honesty**, not accuracy.

**Where it collapses if a hypothesis is removed**

- **Remove H1** (the test distribution differs from the calibration distribution): step 2
  collapses. If test scores are systematically larger the rank is pushed upward and the coverage
  falls as in (3). This is OOD.
- **Remove H2** (the predictor was also trained on the calibration data): because the predictor
  has "seen" the calibration points, the calibration scores are systematically smaller than the
  test scores — like the training residuals of an overfitted model. Exchangeability breaks and
  the interval comes out **too narrow**. This is the most common mistake in practice, and it
  comes from the temptation, when data is scarce, that "setting aside a calibration split is a
  waste".
- **Replace the $(n+1)$ of $k$ by $n$** (use the empirical $(1-\alpha)$ quantile as it is): step 3
  becomes $\lceil n(1-\alpha)\rceil/(n+1)$, which can fall below $1-\alpha$. At $n = 20$,
  $\alpha = 0.1$ it is $18/21 = 0.857$. The finite-sample correction $+1$ is not decoration.

## Problem set

The answer policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★, R1)** Write the four steps of the proof sketch with no line missing, and
(a) prove the rank translation of step 1 rigorously, (b) state why the lower bound survives ties,
(c) show that $\hat{q} = \infty$ when $n < 1/\alpha - 1$ and say in one sentence what that means.
*Strategy + key inequality*: (c) is $\lceil(n+1)(1-\alpha)\rceil > n \iff (n+1)\alpha < 1$.
Meaning: with fewer than 9 calibration samples there is **no** finite interval that gives a 90%
guarantee — the interval is the whole space.

**P2 (derivation, ★★, R2)** Derive (2) from order statistics and write the rule that fixes the
$k$ for which "with probability $1-\delta$ the coverage is at least $1-\alpha$". Find that $k$
for $\alpha = 0.1$, $\delta = 0.05$, $n = 100$, and the mean coverage that results.
*Answer sketch*: the smallest $k$ such that the $\delta$ quantile of $\mathrm{Beta}(k, n+1-k)$ is
at least $1-\alpha$. At $n = 100$, $k = 96$ (instead of the default $91$) and the mean coverage
rises to $96/101 = 0.950$ — **the price of a probabilistic guarantee is a wider interval**. Find
$k$ with `scipy.stats.beta.ppf`.

**P3 (derivation, ★★, R4)** Derive (4) and (8), and (a) find the $c$ at which the ratio is 1 as a
function of $M$, (b) find the limit of (8) as $M \to \infty$ and answer "is it fixed by adding
members".
*Answer sketch*: (a) from $c + (1-c)/M = 1 - c$, $c^\star = (M-1)/(2M-1)$ — $0.444$ at $M = 5$
and $1/2$ as $M \to \infty$. (b) The limit is $c/(1-c)$: **increasing $M$ does not reduce the
shared error**. The size of the ensemble only averages the $z_m$ and never touches $z_0$.

**P4 (numerical, ★, R2, R3, R5)** (a) For $n = 50$, $\alpha = 0.1$ find $k$, the mean coverage
and its standard deviation. (b) What is the coverage if the residual scale grows to
$\kappa = 1.25$ and at the same time a bias $\delta = 0.5$ appears? (c) For
$\pi(u) = 0.05 + 0.5u$, $c_f = 20$, $c_h = 3$ find $\tau^\star$, the minimum cost and the
abstention rate.
*Answer*: (a) $k = 46$, mean $46/51 = 0.9020$, standard deviation $0.0413$.
(b) $\Phi((1.645 - 0.5)/1.25) - \Phi((-1.645 - 0.5)/1.25) = \Phi(0.916) - \Phi(-1.716) = 0.777$.
(c) From $\pi(\tau^\star) = 0.15$, $\tau^\star = 0.2$,
$J = 20(0.05\cdot0.2 + 0.25\cdot0.04) + 3\cdot0.8 = 2.80$, abstention rate 80%. (Tolerance
$\pm0.002$.)
*Check*: in (c) compare with the cost of always acting, $20(0.05 + 0.25) = 6.0$, and of always
abstaining, $3.0$, and confirm that $2.80$ is below both.

**P5 (implementation, ★★★, R1, R2, R3)** Measure the effect of the calibration unit on data with
episode structure. Generate data with $E$ episodes of $T$ steps each whose step residual is "an
episode-wide component + a step component" (variance ratio $\rho$), and compare the distribution
of the realized coverage (a) when steps are the calibration unit and (b) when episodes are (with
the maximum residual of the episode as the score).
*Rubric*: (a) show that with steps as the unit the mean coverage is still about 0.9 but its
variance is larger than the prediction of (6) for $n = ET$ and close to that for $n = E$
(b) explain that the episode unit guarantees the stronger event "the **whole** episode is inside
the interval" (c) vary $\rho$ from 0 to 0.9 and estimate the effective sample size (d) repeat at
least 1000 times.

**P6 (counterexample, ★★, R3, R4, R5)** Construct a counterexample to each of (a) "a wide
prediction interval means out of distribution" and (b) "a small ensemble variance means an
accurate prediction". (c) Construct a case in which the uncertainty score is inverted outside the
distribution ($\pi$ decreasing in $u$) and the abstention policy is **worse than always acting**.
*Property checklist*: (a) uses the heteroscedastic region **inside** the distribution (the hard
region of R2) — a wide interval means the noise is large, not that the input is OOD. (b) uses
$c \to 1$ in (7) — if all members are wrong in the same direction the variance is 0 and the error
is $\sigma$. (c) shows by cost that for a decreasing function such as $\pi(u) = 0.6 - 0.5u$ the
threshold rule **abstains on the safe trials and acts on the dangerous ones**.

**P7 (paper, ★★, R1, R5)** Read sections 1–3 of `angelopoulos2021-conformal` and
`sinha2022-system-level-ood` and (a) check whether the coverage theorem of Angelopoulos and Bates
uses the same quantile level $\lceil(n+1)(1-\alpha)\rceil/n$ as (1) in this lesson, (b) check
whether the distribution the authors use to explain the effect of the calibration sample size is
the same as (2), (c) write with respect to what, rather than as "a property of the model", Sinha
et al. argue OOD should be defined, (d) classify the research challenges the authors present into
the rows of the "three layers of defence" table of this lesson.
*Rubric*: (a) and (b) pass by citing equation numbers. (c) is the core — stating in your own
words the gist "relative to task performance and system-level outcomes" passes, and giving an
example in which the same input is OOD for one task and not for another is excellent. (d) submits
the classification table and, if some challenge fits no row, says so explicitly.

## Paper reading

**Two must-read papers.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read in three passes, and in the third pass concentrate on questions 1,
4 and 8 — "a guarantee under which assumptions" is all there is to this lesson.

1. **Angelopoulos & Bates, "A gentle introduction to conformal prediction and distribution-free
   uncertainty quantification" (2021, arXiv 2107.07511)** — role: `standard`.
   <https://arxiv.org/abs/2107.07511> (§1-3)
   The primary source for R1 and R2 of this lesson. It is a tutorial, so read it while running
   the code examples.
   Additional questions: (a) in the authors' examples of score functions (classification,
   quantile regression), what is the criterion for "a good score" — coverage or the size of the
   interval? (b) what do they recommend as a way of checking conditional coverage? (c) what extra
   information does the extension to distribution shift require (compare with the $w$ of R3)?
2. **Sinha, Sharma, Banerjee, Lew, Luo, Richards, Sun, Schmerling & Pavone, "A system-level view
   on out-of-distribution data in robotics" (2022, arXiv 2212.14020)** — role: `survey`.
   <https://arxiv.org/abs/2212.14020>
   The source of the "three layers of defence" framing of this lesson. A paper to be read for its
   **problem formulation** rather than its mathematics.
   Additional questions: (a) on what grounds do the authors argue that the OOD problem should be
   seen at the system level rather than the model level? (b) what requirements do the authors
   stress for designing runtime monitors and fallback behaviour? (c) which of the open problems
   the authors leave overlap with the "where the assumptions break" of R3 and R4?

**Three recommended papers.** `ren2023-knowno` (calibrating the "request for help" of a language
planner with conformal prediction — an application of R5, <https://arxiv.org/abs/2307.01928>),
`lakshminarayanan2017-deep-ensembles` (the original deep ensembles paper — the object of R4,
<https://arxiv.org/abs/1612.01474>) and `chow1970-reject-tradeoff` (the original reject rule —
(5), <https://doi.org/10.1109/TIT.1970.1054406>).

**The ten fixed questions**: (1) what problem is solved under what assumptions (2) what exactly
could earlier work not do (3) the key idea in one line of mathematics (4) what is the theoretical
guarantee and **what is not guaranteed** (5) the independent and dependent variables and baselines
of the experiments, and were they tuned fairly (6) do the metrics match the claims, and are
variance and seeds reported (7) what information needed for reproduction is missing (8) if it is
wrong, which assumption to suspect first (9) computational and memory complexity and real-time
capability (10) what would you change to surpass it a year from now.

## Reproduction task

**Tier R2 (algorithm reimplementation).** Compute budget: one laptop CPU core, under 3 minutes in
total, at most 1 GB of memory. numpy + scipy only. No GPU, simulator or robot is needed.

**The input data** is produced by the generator below. Create `np.random.default_rng(SEED)` afresh
for every setting. The "action" is a one-dimensional continuous value (for example the target
position of a gripper), and the problem is a heteroscedastic regression whose noise grows with the
size of the input.

```python
"""Reproduction task of s4-safety-ood: data generator and split-conformal quantile."""

import numpy as np

SEED = 20261117
ALPHA = 0.1


def draw(rng, n):
    """Input x ~ U(-1, 1), action y = sin(3x) + (0.1 + 0.2|x|) * noise."""
    x = rng.uniform(-1.0, 1.0, n)
    y = np.sin(3.0 * x) + (0.1 + 0.2 * np.abs(x)) * rng.normal(size=n)
    return x, y


def conformal_quantile(scores, alpha=ALPHA):
    """The ceil((n + 1)(1 - alpha))-th smallest calibration score; inf if that rank exceeds n."""
    n = len(scores)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    return np.inf if k > n else float(np.sort(scores)[k - 1])
```

**Part A — the 90% target coverage.** In each repetition fit a cubic polynomial to 500 training
points (`np.polyfit`), obtain $\hat{q}$ from 200 calibration points, and measure the coverage on
2000 test points. Repeat 2000 times. For (a) the absolute-residual score and (b) the score divided
by the true noise scale $0.1 + 0.2\lvert x\rvert$, report the mean coverage, the standard
deviation across repetitions, and the coverage in the regions $\lvert x\rvert < 0.2$ and
$\lvert x\rvert > 0.8$.

**Part B — the distribution of the realized coverage.** From the beta distribution of (2) compute
the mean, the standard deviation, the 5% quantile and $\Pr[\text{coverage} < 0.85]$ for
$n \in \{20, 100, 500, 2000\}$ (no random numbers; `scipy.stats.beta`).

**Part C — distribution shift.** Calibrate on $10^5$ standard-normal residuals to obtain
$\hat{q}$, measure the coverage on $4\times10^5$ test residuals with scale
$\kappa \in \{1, 1.5, 2\}$ and with bias $\delta \in \{0.5, 1, 2\}$, and compare with (3).

**Part D — ensembles.** In the model (7) ($\sigma = 1$, $M = 5$), for
$c \in \{0, 0.5, 0.8, 0.95\}$ draw $2\times10^5$ times and measure (a) the coverage of the nominal
interval $\bar{e} \pm 1.645S$ and (b) the coverage on the remainder after conformally calibrating
the score $\lvert\bar{e}\rvert/S$ on the first 500 draws.

**Part E — abstention.** For $\pi(u) = 0.02 + 0.6u^2$, $c_f = 10$, $c_h = 1$ compute $J(\tau)$ on
a 10001-point grid over $\tau \in [0, 1]$, find the minimizer and compare with the analytic
solution of (5). Then simulate $10^6$ trials and measure the cost, the abstention rate and the
selective risk at $\tau \in \{\tau^\star, 0.2, 0.6, 1\}$.

**Acceptance criteria — all five conditions must hold to pass.**

1. **Part A** — (a) the mean coverage of the absolute-residual score is $0.9005 \pm 0.003$
   (theory $181/201$) with a standard deviation across repetitions of $0.022 \pm 0.003$. **The 90%
   target is met.** (b) For the same score the easy region gives $0.993 \pm 0.005$ and the hard
   region $0.781 \pm 0.015$ — print explicitly that **the marginal guarantee is not a conditional
   guarantee**. (c) With the normalized score the two regions come to $0.899$ and $0.902$
   ($\pm0.01$) and the mean coverage is still $0.9005 \pm 0.003$.
2. **Part B** — the standard deviations are $0.0626, 0.0296, 0.0134, 0.0067$, the 5% quantiles
   $0.7839, 0.8482, 0.8773, 0.8888$, and $\Pr[\text{coverage} < 0.85]$ is
   $0.1756, 0.0551, 0.0004, 0.0000$ (tolerance $10^{-3}$). Check that the standard deviation
   across repetitions of Part A matches $0.0221$, the root sum of squares of the $0.0211$ of
   $\mathrm{Beta}(181, 20)$ and the test-sample noise $\sqrt{0.09/2000} = 0.0067$.
3. **Part C** — the coverage under scale shift is $0.900, 0.727, 0.589$ and under bias shift
   $0.858, 0.736, 0.361$ (tolerance $\pm0.01$), in agreement with (3). Print alongside that
   **$\hat{q}$ is the same value regardless of the shift** ($1.645 \pm 0.02$).
4. **Part D** — (a) the coverage of the nominal interval at $c = 0, 0.5, 0.8, 0.95$ is
   $0.979, 0.793, 0.534, 0.273$ (tolerance $\pm0.01$). (b) After conformal calibration all four
   cases are $0.90 \pm 0.04$ (the scatter of the realized coverage for 500 calibration samples —
   three times the $n = 500$ standard deviation $0.013$ of Part B). (c) The threshold $\hat{q}$
   **increases monotonically** with $c$ (measured $0.93 \to 9.63$).
5. **Part E** — the grid minimizer is $\tau^\star = 0.3651 \pm 0.0002$ with minimum cost
   $0.8053 \pm 0.0002$, in agreement with the analytic solution. The simulation gives, at
   $\tau^\star$, cost $0.805$, abstention rate $0.635$ and selective risk $0.047$; at $\tau = 1$,
   cost $2.20$ and selective risk $0.220$ (tolerance $\pm0.01$).

**Comparison**: (a) the baseline of Parts A, C and D is the target coverage $0.90$. (b) For the
scatter across repetitions of Part A the beta distribution of Part B is the baseline. (c) The
baseline of Part D is the uncalibrated nominal interval. (d) The baselines of Part E are always
acting and always abstaining.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The mean coverage of Part A is near 0.895 | The $(n+1)$ correction was left out of the empirical quantile | Check that $k = 181$ (with $180$ it is $180/201 = 0.8955$) |
| The mean coverage of Part A is visibly above 0.90 | Training points were reused for calibration, or the polynomial was fitted on the calibration points | Check that training, calibration and test are distinct samples |
| The coverage is 0.90 in both regions | The noise of the generator is homoscedastic | Check that the noise scale is $0.1 + 0.2\lvert x\rvert$ |
| In Part C the interval widens with the shift | It was recalibrated on the test residuals | $\hat{q}$ is computed **once**, on the calibration distribution |
| The nominal coverage of Part D does not depend on $c$ | The shared component $z_0$ was drawn separately for each member | Check that $z_0$ has shape $(N, 1)$ |
| The $c = 0$ coverage of Part D is 0.90 | The interval was centred on a single member (not on the ensemble mean) | Check that the centre is $\bar{e}$ and the width $S$ (with $M-1$ degrees of freedom) |
| The optimal cost of Part E exceeds 1 | The abstention term $c_h(1-\tau)$ was left out of the cost or has the wrong sign | Check that $J(0) = 1$ and $J(1) = 2.2$ |

## Open problems

- **(Open problem) Calibration in closed loop** — R1 requires exchangeability, but the rollout of
  a policy is a distribution the policy itself creates, with correlated steps and different from
  the demonstration distribution. Current approaches: taking episodes as the calibration unit,
  and adaptive conformal inference, which adjusts the threshold online over time to guarantee the
  **long-run average** coverage. What is missing: online adjustment guarantees only the average
  coverage and says nothing about **this step, now** — and the latter is what safety needs.
- **(Open problem) Distribution shift without a likelihood ratio** — the weighted conformal
  prediction of R3 requires $w(x)$, but estimating it for high-dimensional observations (images)
  is itself a hard problem, and how the estimation error propagates into the guarantee is only
  partly known. Current approach: robust conformal prediction, which bounds the size of the shift
  by an $f$-divergence ball and calibrates for the worst case. What is missing: a way to set the
  radius of that ball from data — at present a human in effect picks it.
- **(Open problem) Defining and detecting task-relevant OOD** — the gist of
  `sinha2022-system-level-ood` is that an input differing from the training distribution and
  **the task failing** are different things. If the policy is fine when the background changes,
  an OOD alarm is a false alarm. Current approaches: monitors that measure changes in the
  policy's internal representations or action distribution, and training a separate failure
  predictor. What is missing: a monitor with **guaranteed recall** on task failures — the
  fundamental obstacle is that failure data is rare and calibration samples are scarce.
- **(Open problem) Safety metrics that include intervention load** — R5 shows that lowering the
  selective risk raises the abstention rate. Papers report "a success rate of Y% at a help-request
  rate of X%", but there are no metrics for the **closed-loop human-robot system** that include
  the degradation of the human's response quality with call frequency (alarm fatigue). Current
  approach: comparing success rates under a fixed help-request budget. What is missing: the
  optimal abstention policy when $c_h$ is not constant, and a protocol for evaluating it.

## Concept check

Take it with `rc quiz s4-safety-ood`. This quiz is a **concept check only**; the real work is the
problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

## How to study this stage

1. **Read the table of the three layers first (10 min)** — the table in "Setup and notation". See
   that uncertainty quantification, runtime monitoring and fallback answer different questions,
   and look at the "condition for a guarantee" column of each layer. Every result of this lesson
   fills in that column.
2. **The proof of R1 from a blank page (40 min)** — it has four steps. The single sentence "the
   rank is uniform" is all of it; confirm that the proof **does not use** the accuracy of the
   predictor. Then remove the three hypotheses one at a time.
3. **Run Part A and see the 90% (50 min)** — right after confirming the mean coverage $0.9005$,
   print the coverage by region ($0.993$ and $0.781$). This contrast is what "marginal guarantee"
   means.
4. **Derive (2), then Part B (40 min)** — from order statistics to the beta distribution. Explain
   the $n = 20$ row of the table in your own words: how can "90% guarantee" and "below 85% with
   probability 17.6%" both be true?
5. **Break the guarantee with Part C (30 min)** — doubling the scale gives a coverage of $0.589$.
   See in numbers that **$\hat{q}$ does not change**. This is where it becomes clear that
   conformal prediction is not an OOD detector.
6. **Derive (4), then Part D (50 min)** — the one line in which the shared error cancels in the
   subtraction is the core. Then conformally calibrate the same score and see $0.90$ come out
   regardless of $c$ — "a score without guarantee + calibration = an interval with guarantee" is
   the standard combination in practice.
7. **(9) and Part E (40 min)** — derive the optimal threshold and fill in the table. Look at the
   63.5% abstention rate and ask yourself "what percent autonomous is this policy?". With the
   table for varying $c_h$, see how sensitive the answer is.
8. **The two papers (120 min)** — read Angelopoulos and Bates together with the code, and Sinha et
   al. with the problem formulation in focus. While reading the latter, check whether each of the
   "three layers" exists in one robot system you know. The one-page note per paper is
   **mandatory**.
9. **Close the module (30 min)** — this is the last lesson of S4. Collect and read the "Open
   problems" of the six lessons and write a paragraph on how the open problems of
   `s4-evaluation-science` (violation of independence, adaptive overfitting) and those of this
   lesson (calibration in closed loop, task-relevant OOD) share one root — **the process that
   produced the data differs from the process that uses it**.

**Pass criterion**: from a blank page you can derive the four steps of R1, (2), (3), (4) and (9);
you can tell apart marginal and conditional guarantees, and average guarantees and realized
coverage; you can explain **what conformal prediction does not do** under OOD; you have code that
satisfies all five conditions of the reproduction task; and you have notes on the two papers.
