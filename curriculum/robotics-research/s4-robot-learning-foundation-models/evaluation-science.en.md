---
id: s4-evaluation-science
lang: en
title: The science of evaluation
summary: >-
  What does the number say, and what does it not say, when the success rate of a robot policy is
  reported as "18 out of 20"? Prove the coverage guarantee of the Clopper–Pearson interval and
  show by exact computation how badly the Wald interval collapses at robot-scale sample sizes.
  Derive the number of trials needed to detect a difference between the success rates of two
  policies, and derive and confirm numerically that at low power a significant result inflates
  the effect, that picking the best on the same evaluation set produces 13 points out of no
  difference in skill, and that the noise of real-world evaluation sets an upper bound on the
  sim-to-real correlation.
objectives:
  - Prove that the Clopper–Pearson interval has at least nominal coverage for every $p$ and $n$.
  - Derive the number of trials needed to detect a difference between two success rates and compute the gain of a paired design.
  - Show by exact computation that at low power significant estimates exaggerate the effect (the winner's curse).
  - Derive the selection bias of picking the best of $K$ on the same evaluation set and remove it with a holdout.
  - Derive how much real-evaluation noise attenuates the sim-to-real correlation and compute its upper bound.
tags: [evaluation, statistics, confidence-interval, power-analysis, benchmark-overfitting, research]
---

# The science of evaluation

## Setup and notation

Where `r1-robotics-evaluation-statistics` covered **the procedure for designing** an evaluation
protocol (choice of metric, seeds, multiple comparisons), this lesson works the **mathematics**
underneath that procedure all the way through at the actual scale of robot learning — 10 to 50
real-world trials per policy. The recommended prerequisites are that lesson and
`s4-vla-architectures` (to know what the policies being evaluated are).

| Symbol | Meaning |
|---|---|
| $p$ | The true success rate of a policy. Trials are assumed independent Bernoulli (where this breaks: R1) |
| $n$, $k$ | Number of trials and of successes. $\hat{p} = k/n$ |
| $1-\alpha$ | Confidence level. $0.95$ in this lesson ($z_{\alpha/2} = 1.960$) |
| $1-\beta$ | Power. The standard is $0.8$ ($z_\beta = 0.842$) |
| $\Delta = p_2 - p_1$ | The true difference in success rate between two policies |
| $K$ | Number of variants (checkpoints, hyperparameters) compared on the same evaluation set |
| $R_i$, $S_i$ | Real-world and simulated success rate of policy $i$ |
| Coverage | The probability that the interval contains the truth, $\Pr_p[L(k) \le p \le U(k)]$ |

**The four questions this lesson answers.**

| Question | Answer | Result |
|---|---|---|
| What does "18/20 successes" say? | $p \in [0.683, 0.988]$ — 30 points wide | R1 |
| How many runs to claim A beats B by 20 points? | 82 per arm ($0.6$ vs $0.8$) | R2 |
| What if you report the best of 20 checkpoints? | +13 points with no difference in skill ($n = 50$) | R3 |
| Is a 0.9 correlation between simulated and real evaluation good? | With 20 real trials the expected correlation of a **perfect** simulator is 0.88 | R4 |

## Key results

The bracket gives the derivation depth (D0 cited / D1 skeleton / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (the coverage guarantee of the Clopper–Pearson interval) [D3]** — the interval obtained by
  inverting the binomial tail probabilities,
  $$
  L(k) = \inf\{p : \Pr_p[X \ge k] > \alpha/2\}, \qquad
  U(k) = \sup\{p : \Pr_p[X \le k] > \alpha/2\} \tag{1}
  $$
  has coverage at least $1-\alpha$ for **every** $p \in [0,1]$ and **every** $n$. It is a
  guarantee without approximation. By contrast the textbook Wald interval
  $\hat{p} \pm z\sqrt{\hat{p}(1-\hat{p})/n}$ has, at $n = 20$, a coverage of $0.876$ at $p = 0.9$
  and $0.639$ at $p = 0.05$. With 0 or $n$ successes the Wald interval has **zero width**. For
  $k = n$ the lower limit of (1) is $(\alpha/2)^{1/n}$, and used one-sided the 95% upper bound on
  the failure rate is $1 - 0.05^{1/n} \approx 3/n$ (the "rule of three").
- **R2 (trials needed to compare two success rates) [D2]** — to distinguish $p_1$ from $p_2$ at
  two-sided level $\alpha$ with power $1-\beta$ one needs, per arm,
  $$
  n \;\approx\; \frac{\big(z_{\alpha/2}\sqrt{2\bar{p}\bar{q}} + z_\beta\sqrt{p_1q_1 + p_2q_2}\big)^2}{\Delta^2},
  \qquad \bar{p} = \tfrac12(p_1+p_2),\; q = 1-p \tag{2}
  $$
  trials. For $0.6$ vs $0.8$, $n = 81.2$ (exact power: $0.807$ at $n = 82$); for $0.5$ vs $0.6$,
  $n = 387$. The $n = 20$ typical of robot papers has a power of **$0.291$** against a 20-point
  difference. A **paired design**, which uses the same initial conditions for both policies,
  reduces the variance by the correlation $\rho$ of the outcomes and multiplies the required
  number of trials by $1 - \rho\,\frac{2\sqrt{p_1q_1p_2q_2}}{p_1q_1+p_2q_2}$.
- **R3 (the winner's curse and selection bias) [D2]** — (a) at low power the estimates that
  **come out significant** exaggerate the effect. With a true difference of $0.10$ ($0.5$ vs
  $0.6$) and $n = 20$, the mean estimated difference among significant results is $0.384$ —
  **3.8 times** the truth. (b) Picking the best of $K$ variants of **equal** skill on the same
  evaluation set inflates the reported success rate by
  $$
  \mathbb{E}\big[\max_{i\le K}\hat{p}_i\big] - p \;\le\; \sqrt{\frac{pq}{n}}\,\sqrt{2\ln K} \tag{3}
  $$
  (in the Gaussian approximation), and the exact value at $p = 0.5$, $n = 50$, $K = 20$ is
  $+0.131$. **Re-evaluating with new trials** after the selection makes the bias exactly 0.
- **R4 (real-world noise bounds the sim-to-real correlation) [D2]** — if the true success rates
  of $N$ policies have variance $\sigma_p^2$ and the real-world evaluation uses $n$ trials per
  policy, then even a simulator that matches the true success rates **perfectly** cannot have an
  observed Pearson correlation above
  $$
  r_{\mathrm{obs}} \;\approx\; \sqrt{\frac{\sigma_p^2}{\sigma_p^2 + \overline{pq}/n}}. \tag{4}
  $$
  For 10 policies with success rates spread evenly over $0.2$–$0.8$ and $n = 20$ this is $0.880$
  (measured $0.896$), and **45% of perfect simulators produce $r < 0.9$**. The validity of a
  simulated evaluation must therefore be reported together with the number of real-world trials.
- **R5 (aggregating over tasks: neither mean nor median but IQM, with a stratified bootstrap)
  [D1]** — when the results of $M$ tasks × $n$ trials are reduced to one number, the mean is
  pulled by the outlier of a single task and the median discards half the tasks and has a large
  variance. The interquartile mean (IQM), the mean of the middle 50%, is the compromise between
  them, and the interval is built by a bootstrap stratified by task
  (`agarwal2021-deep-rl-at-the-edge` §4).

## Derivation

### R2 — the required number of trials

**The test.** The two-sample $z$ test of the null hypothesis $H_0: p_1 = p_2$ rejects when the
statistic

$$
Z = \frac{\hat{p}_2 - \hat{p}_1}{\sqrt{2\hat{\bar{p}}(1-\hat{\bar{p}})/n}}, \qquad
\hat{\bar{p}} = \tfrac12(\hat{p}_1 + \hat{p}_2) \tag{5}
$$

satisfies $\lvert Z\rvert > z_{\alpha/2}$. The denominator is the standard error **under the null**
(the two arms are taken to share one success rate, estimated by pooling).

**The distribution under the alternative.** If the truth is $p_1 \ne p_2$, then
$\hat{p}_2 - \hat{p}_1$ is approximately normal with mean $\Delta$ and variance
$(p_1q_1 + p_2q_2)/n$. The denominator of the rejection condition converges to
$\sqrt{2\bar{p}\bar{q}/n}$. Taking $\Delta > 0$, the rejection probability (dominated by the upper
tail) is

$$
\Pr\Big[\hat{p}_2 - \hat{p}_1 > z_{\alpha/2}\sqrt{2\bar{p}\bar{q}/n}\Big]
 = \Pr\left[\mathcal{N}(0,1) > \frac{z_{\alpha/2}\sqrt{2\bar{p}\bar{q}/n} - \Delta}{\sqrt{(p_1q_1+p_2q_2)/n}}\right].
$$

**The power condition.** For this probability to be $1 - \beta$ the threshold on the right must
be $-z_\beta$:

$$
z_{\alpha/2}\sqrt{2\bar{p}\bar{q}/n} - \Delta = -z_\beta\sqrt{(p_1q_1+p_2q_2)/n}
\;\Longrightarrow\;
\sqrt{n}\,\Delta = z_{\alpha/2}\sqrt{2\bar{p}\bar{q}} + z_\beta\sqrt{p_1q_1+p_2q_2},
$$

and squaring both sides and dividing by $\Delta^2$ gives (2).

**Read it in numbers.** $z_{\alpha/2} = 1.960$, $z_\beta = 0.842$.

| Comparison | $n$ of (2) (per arm) | Total trials |
|---|---|---|
| $0.5$ vs $0.7$ | $93.0$ | 186 |
| $0.6$ vs $0.8$ | $81.2$ | 164 |
| $0.7$ vs $0.9$ | $61.6$ | 124 |
| $0.5$ vs $0.6$ | $387.3$ | 776 |

Since $n \propto 1/\Delta^2$, halving the difference quadruples the trials. **Verifying a
10-point difference on real hardware takes about 780 trials in total** — more than ten times what
most robot papers report.

The power obtained by summing the test (5) **exactly** over all combinations $(k_1, k_2)$ ($0.6$
vs $0.8$):

| $n$ per arm | 10 | 20 | 50 | 82 | 100 | 200 |
|---|---|---|---|---|---|---|
| Power | $0.131$ | $0.291$ | $0.595$ | $0.807$ | $0.880$ | $0.993$ |

The approximation $81.2$ of (2) is confirmed by the exact power $0.807$ at $n = 82$.

**The paired design.** Running both policies on the same initial condition $i$ (object placement,
lighting, starting pose) makes the outcomes $(X_{1i}, X_{2i})$ **positively correlated** — on a
hard initial condition both tend to fail. The variance of the difference $D_i = X_{2i} - X_{1i}$
is

$$
\operatorname{Var}(D_i) = p_1q_1 + p_2q_2 - 2\rho\sqrt{p_1q_1p_2q_2}, \tag{6}
$$

so the required number of trials is $1 - \rho\cdot 2\sqrt{p_1q_1p_2q_2}/(p_1q_1+p_2q_2)$ times
that of the independent design. For $0.6$ vs $0.8$ and $\rho = 0.5$ the factor is
$1 - 0.5\times0.392/0.40 = 0.51$ — **half the trials**. The paired design is the largest gain
available at no cost in real-world evaluation.

**Where the assumptions break**: (a) (2) is a normal approximation. It is off when $p$ is near 0
or 1 or $n$ is small — which is why it is checked by exact computation as in the table above.
(b) Trials were assumed **independent**. If the robot heats up, the objects wear, or the operator
resets slightly differently each time, trials become correlated and **the effective sample size
is below $n$**. Running the two policies **interleaved** (A, B, A, B, …) is the minimal defence
that spreads temporal drift evenly over both. (c) The $\rho$ of (6) is not known in advance.
Estimate it from 20 pilot pairs, or plan with $\rho = 0$ and treat the gain as a bonus.

### R3 — the winner's curse and selection bias

**(a) Estimates filtered by significance are biased.** At low power, rejection happens only when
the sample difference is **large by chance**. The rejection region is $\hat{\Delta} > c$,
$c = z_{\alpha/2}\sqrt{2\hat{\bar{p}}(1-\hat{\bar{p}})/n}$, so a significant estimate cannot be
smaller than $c$:

$$
\mathbb{E}\big[\hat{\Delta} \mid \text{reject},\ \hat{\Delta} > 0\big] \;>\; \min c.
$$

At $n = 20$, $c$ is $0.308$ when the pooled sample success rate is near $0.55$, and over all
possible $(k_1, k_2)$ the smallest significant difference is $0.20$. **Even when the true
difference is $0.10$, every significant result reports at least twice that.** Exact computation
($0.5$ vs $0.6$):

| $n$ per arm | Power | Mean $\hat{\Delta}$ when significant | Exaggeration ratio | Probability of the wrong sign |
|---|---|---|---|---|
| 20 | $0.087$ | $0.384$ | $3.8\times$ | $0.0041$ |
| 50 | $0.184$ | $0.244$ | $2.4\times$ | $0.0017$ |
| 100 | $0.310$ | $0.180$ | $1.8\times$ | $0.0004$ |
| 400 | $0.814$ | $0.112$ | $1.1\times$ | $0.0000$ |

**How to read it.** If an experiment with power $0.087$ produced a significant result, its effect
size is **inflated 3.8 times on average**. And since such results are the ones that become
papers, the mean effect size reported in the literature exceeds the truth. The exaggeration ratio
(the type M error) comes down to $1.1$ only when the power reaches $0.8$ (`gelman2014-type-s-m`).

**(b) Picking the best inflates.** Evaluate $K$ variants of equal skill ($p$) with the same $n$
trials each and report the best. Writing $\hat{p}_i \approx p + \sigma Z_i$
($\sigma = \sqrt{pq/n}$, $Z_i$ standard normal),
$\mathbb{E}[\max_i\hat{p}_i] - p = \sigma\,\mathbb{E}[\max_iZ_i]$. The expectation of the maximum
is bounded as follows. For any $t > 0$, by Jensen,

$$
\exp\big(t\,\mathbb{E}[\max_iZ_i]\big) \le \mathbb{E}\big[\exp(t\max_iZ_i)\big]
 = \mathbb{E}\big[\max_ie^{tZ_i}\big] \le \sum_{i=1}^{K}\mathbb{E}\big[e^{tZ_i}\big] = K e^{t^2/2},
$$

and taking logarithms $\mathbb{E}[\max_iZ_i] \le \ln K/t + t/2$, whose right side is minimized at
$t = \sqrt{2\ln K}$ with value $\sqrt{2\ln K}$. This is (3).

Exact values for the binomial distribution ($p = 0.5$; the bound (3) in brackets):

| $n$ \ $K$ | 5 | 20 | 100 |
|---|---|---|---|
| 20 | $+0.129$ ($0.201$) | $+0.206$ ($0.274$) | $+0.273$ ($0.339$) |
| 50 | $+0.082$ ($0.127$) | $+0.131$ ($0.173$) | $+0.176$ ($0.215$) |
| 100 | $+0.058$ ($0.090$) | $+0.093$ ($0.122$) | $+0.125$ ($0.152$) |

**Evaluating 20 checkpoints with $n = 50$ and reporting the best produces 13 points even when
all of them have the same skill.** The bias grows only as $\sqrt{\ln K}$, so the excuse "we only
looked at 20" does not hold — looking at just 5 already gives 8 points.

**A holdout fixes it.** If the selected variant $i^\star$ is re-evaluated with $n'$ **new**
trials, the new trials are independent of those used for the selection, so
$\mathbb{E}[\hat{p}'_{i^\star} \mid i^\star] = p_{i^\star}$ — the bias is exactly 0. This is why
"evaluation for checkpoint selection" and "evaluation for reporting" are kept apart, and why
benchmark overfitting is dangerous: a public benchmark is a structure in which **the whole
field** grows $K$ on the same evaluation set.

**Where the assumptions break**: (a) (3) is an upper bound for **independent** variants.
Checkpoints are strongly correlated with one another (adjacent checkpoints are almost the same
policy), so the effective $K$ is much smaller and so is the bias. Conversely, if the variants
**differ** in skill, picking the best also brings a real gain, and a holdout is needed to
separate the inflation from the real gain. (b) The unbiasedness of the holdout holds when the new
trials come from **the same distribution**. If the reporting evaluation is run on a different day
with different objects, distribution shift is mixed in — which may be not a bias but part of the
generalization one wants to measure, and one has to say which.

### R4 — attenuation of the correlation

**Setting.** Policies $i = 1,\dots,N$ have true real-world success rates $p_i$, and the
real-world evaluation is $R_i = k_i/n$, $k_i \sim \mathrm{Bin}(n, p_i)$. Suppose the simulator is
**perfect**: $S_i = p_i$. What is observed is still $\operatorname{corr}(S, R)$, not
$\operatorname{corr}(S, p) = 1$.

**Derivation.** $R_i = p_i + \varepsilon_i$, with $\mathbb{E}[\varepsilon_i \mid p_i] = 0$ and
$\operatorname{Var}(\varepsilon_i \mid p_i) = p_iq_i/n$. At the level of the population of
policies,

$$
\operatorname{Cov}(S, R) = \operatorname{Cov}(p, p + \varepsilon) = \sigma_p^2, \qquad
\operatorname{Var}(R) = \sigma_p^2 + \overline{pq}/n,
$$

($\overline{pq}$ being the mean of the $p_iq_i$), so

$$
r_{\mathrm{obs}} = \frac{\sigma_p^2}{\sigma_p\sqrt{\sigma_p^2 + \overline{pq}/n}}
 = \sqrt{\frac{\sigma_p^2}{\sigma_p^2 + \overline{pq}/n}},
$$

which is (4). The ratio under the square root is the **reliability** of the real-world
measurement, and (4) is the attenuation formula of psychometrics. If the simulated side also uses
finitely many trials, the square root of its reliability multiplies in once more.

**Numbers.** Ten $p_i$ evenly placed on $0.2, \dots, 0.8$ ($\sigma_p^2 = 0.0367$,
$\overline{pq} = 0.2133$), measured over 20,000 draws:

| Real $n$ | Prediction of (4) | Measured mean $r$ | $\Pr[r < 0.9]$ | Mean MMRV |
|---|---|---|---|---|
| 10 | $0.795$ | $0.816$ | $0.804$ | $0.128$ |
| 20 | $0.880$ | $0.896$ | $0.450$ | $0.069$ |
| 50 | $0.946$ | $0.955$ | $0.027$ | $0.026$ |
| 200 | $0.986$ | $0.988$ | $0.000$ | $0.003$ |

(The measurement is slightly above the prediction because (4) is a population formula and the
sample correlation is computed from 10 policies.) MMRV is the rank-violation metric used by
`li2024-simpler`:
$\mathrm{MMRV} = \frac1N\sum_i\max_j\lvert R_i - R_j\rvert\cdot\mathbb{1}[(S_i < S_j) \ne (R_i < R_j)]$ —
for each policy it takes, among the pairs whose simulated ranking disagrees with the real one,
the largest real performance gap, and averages (check the definition in the paper yourself —
problem P8(a)).

**How to read it.** (a) **Even a perfect simulator** has an expected correlation of $0.88$ with
20 real trials, and nearly half fall short of $0.9$. So "our simulator has $r = 0.9$ with the real
world" cannot be interpreted without the number of real trials. (b) If the policies are **close**
in skill (small $\sigma_p^2$) the bound is lower — validity is hardest to verify in exactly the
situation where one wants to use the proxy, to separate similar policies. (c) MMRV is not zero
either: at $n = 20$ the mean MMRV of a perfect simulator is $0.069$. This is the **noise floor**
of that metric, and a reported MMRV has to be compared against it.

**Where the assumptions break**: (4) is the **upper bound** for zero simulator error. A real
simulator has a bias that differs from policy to policy (policies with a larger visual gap drop
more in simulation), and if that bias correlates with the skill of the policy the ranking is
flipped systematically — that is not attenuation but **bias**, and more real trials do not make
it go away. And the Pearson correlation measures a linear relation, so if the simulated success
rate is a monotone but nonlinear function of the real one (simulation is uniformly harder), the
ranking is right while $r$ is low. That is the reason for reporting a rank metric alongside.

### R5 — aggregating over tasks (skeleton)

Each task $m = 1,\dots,M$ has a success rate $\hat{p}_m$ and one number is wanted.

- **The mean** uses every task but is pulled by the extreme value of a single task (especially
  when task scores are on different scales).
- **The median** is robust to extremes but discards half the tasks, so its statistical efficiency
  is low — the interval is wider for the same number of trials.
- **The IQM** sorts the scores, drops the bottom 25% and the top 25%, and averages the middle
  50%. It is more efficient than the median and more robust than the mean.

The interval is built with a **stratified bootstrap**: with tasks as strata, resample trials (or
seeds) with replacement **within** each task and recompute the aggregate, repeatedly. Tasks are
not mixed because the tasks are a fixed part of the evaluation design, not a random sample
(`agarwal2021-deep-rl-at-the-edge` §4). **[D1]**

**Where the assumptions break**: with a very small $n$ (3 to 5 seeds per task) the bootstrap errs
on the side of intervals that are **too narrow**. And for a task whose success rate is 0 or 1
resampling never changes the value, so the uncertainty that task contributes to the interval is
computed as 0 — a failure of the same kind as the Wald interval of R1.

## Proof sketch

### R1 — coverage of the Clopper–Pearson interval [D3]

**Hypotheses**
H1: $X \sim \mathrm{Bin}(n, p)$ — the trials are independent with a common success rate.
H2: the interval is defined by (1).

**Conclusion** C: for every $p \in [0,1]$, $\Pr_p[L(X) \le p \le U(X)] \ge 1 - \alpha$.

**Strategy**: turn the event "the truth is outside the interval" into the event "the observation
is in a tail". The bridge is that tail probabilities are monotone in $p$.

1. **Monotonicity.** For fixed $k$, $p \mapsto \Pr_p[X \ge k]$ is continuous and **increasing**
   (a higher success rate makes large values more likely — a coupling argument: build
   $\mathbb{1}[U_i \le p]$ from the same uniform random numbers, and raising $p$ only ever turns
   trials into successes). Likewise $p \mapsto \Pr_p[X \le k]$ is decreasing.
2. **Translating the lower-limit failure event.** Let $p < L(k)$. By the definition of $L(k)$ and
   the monotonicity of step 1, $\Pr_p[X \ge k] \le \alpha/2$. That is, "$p$ is below the lower
   limit of the observation $k$" is the same as "$k$ is a value whose upper tail probability
   under $p$ is at most $\alpha/2$".
3. **The probability of that event.** Put $k^\star(p) := \min\{k : \Pr_p[X \ge k] \le \alpha/2\}$.
   The event of step 2 is $\{X \ge k^\star(p)\}$ (tail probabilities decrease in $k$), and its
   probability is $\Pr_p[X \ge k^\star] \le \alpha/2$ by definition.
4. **The upper limit likewise.** By the symmetric argument $\Pr_p[p > U(X)] \le \alpha/2$.
5. **Combine.** $\Pr_p[p \notin [L, U]] \le \alpha/2 + \alpha/2 = \alpha$. **C**.

**Why the inequality is not an equality.** In step 3, $\Pr_p[X \ge k^\star] \le \alpha/2$ is
usually a **strict** inequality — $X$ is discrete, so no $k$ makes the tail probability exactly
$\alpha/2$. The interval is conservative by that difference: at $n = 20$ the actual coverage is at
least $0.959$ and $0.975$ on average. That is the price of the guarantee.

**Where it collapses if a hypothesis is removed**

- **Remove the independence in H1**: $X$ is not binomial and its variance exceeds $npq$
  (overdispersion). (1) is computed from binomial tails, so the interval comes out **too narrow**
  and the coverage falls below nominal. This is the most common violation in robot evaluation —
  repeating the same initial condition, or a day's trials sharing the lighting. The defence is to
  aggregate by cluster (initial condition, date) and use the number of clusters as $n$.
- **Remove "a common success rate" in H1** (the $p_i$ differ from trial to trial but the trials
  are independent): $X$ is Poisson-binomial and its variance is **smaller** than that of the
  binomial with the mean success rate. (1) is then still conservative for the mean success rate —
  this violation is on the safe side. The problem is when the paper does not say **over which
  distribution of initial conditions** that "mean" is taken.
- **Replace (1) by Wald**: the interval comes from a normal approximation rather than from tail
  probabilities, and that approximation is wrong when $p$ is near 0 or 1 or $n$ is small. In
  particular at $k \in \{0, n\}$ the estimated standard error is 0 and the interval has zero
  width: "20/20 successes" is reported as "$p = 1$ for certain". The actual 95% lower limit is
  $0.832$.

## Problem set

The answer policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★, R1)** Write the five steps of the proof sketch with no line missing, and
(a) prove the monotonicity of step 1 by a coupling argument, (b) derive directly from (1) that
$L(n) = (\alpha/2)^{1/n}$ when $k = n$, (c) explain why the endpoints of (1) are computed as
quantiles of a beta distribution ($L = B^{-1}(\alpha/2;\,k,\,n-k+1)$).
*Strategy + key inequality*: (b) is $\Pr_p[X \ge n] = p^n$. (c) uses the identity between the
binomial tail and the incomplete beta function, $\Pr_p[X \ge k] = I_p(k, n-k+1)$ (integrate by
parts $k$ times). The expansion is withheld.

**P2 (derivation, ★, R2)** Derive (2), and compute for $0.6$ vs $0.8$ how the required number of
trials changes for a one-sided test (asking only whether A is **better** than B). Then write a
paragraph on the condition under which a one-sided test may be used.
*Answer sketch*: replace $z_{\alpha/2} = 1.960$ by $z_\alpha = 1.645$. It drops to about $64$. A
one-sided test is justified only when it was decided **in advance** that a result in the opposite
direction will be treated exactly like "no difference" — choosing after seeing the result doubles
the level.

**P3 (derivation, ★★, R4)** Extend (4) to the case in which the simulated side is also evaluated
with $n_s$ trials per policy. Then write the attenuation-correction formula that "recovers the
true correlation from the observed $r_{\mathrm{obs}}$" and give one case in which that correction
is dangerous.
*Answer sketch*: $r_{\mathrm{obs}} = r_{\mathrm{true}}\sqrt{\mathrm{rel}_R\,\mathrm{rel}_S}$,
$\mathrm{rel} = \sigma^2/(\sigma^2 + \overline{pq}/n)$. The correction is a division. Danger:
when the reliability is estimated from the sample its estimation error is amplified and the
corrected correlation can exceed 1 — especially when the number of policies $N$ is small.

**P4 (numerical, ★, R1)** (a) Find the 95% Clopper–Pearson intervals of $18/20$, $20/20$, $9/10$
and $45/50$, and (b) find how many trials are needed for a half-width of $\pm0.10$ and $\pm0.05$
(near $p = 0.5$).
*Answer*: (a) $[0.683, 0.988]$, $[0.832, 1.000]$, $[0.555, 0.997]$, $[0.782, 0.967]$ (tolerance
$\pm0.002$). (b) For the exact interval, half-width $0.102$ at $n = 100$ and $0.050$ at $n = 400$;
by the Wald approximation, $97$ and $385$.
*Check*: compute with `scipy.stats.beta.ppf`, and confirm that the lower limit of $20/20$ equals
$0.025^{1/20} = 0.8316$. See that **for the same 90% the intervals of $9/10$ and $45/50$ differ
in width by more than a factor of two**.

**P5 (numerical, ★★, R2, R3)** A paper reports "proposed method $17/20$, baseline $12/20$".
(a) Find the $z$ statistic of (5) and the two-sided $p$ value, (b) find what the power of this
experiment was if the true success rates really are $0.85$ and $0.60$, (c) write in two sentences
how this result is honestly described.
*Answer*: (a) $\hat{\bar{p}} = 0.725$, $\mathrm{SE} = 0.1412$, $z = 1.771$, $p = 0.077$ — not
significant. (b) $0.441$ by exact computation (tolerance $\pm0.01$). (c) "The difference is 25
points but 20 trials do not separate the two (the 95% interval includes 0)" and "confirming this
difference with power 0.8 takes about 50 trials per arm".

**P6 (implementation, ★★★, R3)** Simulate checkpoint selection. Evaluate with $n$ trials each 20
checkpoints whose true success rate rises with the training step as
$p(t) = 0.4 + 0.3(1 - e^{-t/5})$, pick the best, and (a) measure the difference between the
**reported** and the **true** success rate of the selected checkpoint (the selection bias) at
$n = 10, 20, 50, 100$, (b) compare the reporting bias and the **quality of the selection** (the
true success rate of the chosen checkpoint) when the same total budget is split into "selection
$n/2$ + holdout $n/2$".
*Rubric*: (a) show that the bias is positive and shrinks as $n$ grows (b) show that the reporting
bias of the holdout is 0 within statistical error (c) show in numbers that the holdout slightly
**lowers** the quality of the selection (only half the trials are used to select) and describe
the trade in a paragraph (d) repeat at least 10,000 times.

**P7 (counterexample, ★★, R1, R3)** (a) Give, as a probability at $n = 20$, a counterexample to
"with the same number of trials the higher success rate is the better policy" — it suffices to
find the probability that a policy with true success rate $0.7$ has a sample success rate at
least that of a policy with $0.8$. (b) Show with a numerical example that "if the confidence
intervals overlap the difference is not significant" is false.
*Property checklist*: (a) sums the joint probability of the two binomials exactly (about $0.29$,
ties included). (b) finds one $(k_1, k_2, n)$ whose two intervals overlap while the test (5)
rejects — the widths of the individual intervals add as $\mathrm{SE}_1 + \mathrm{SE}_2$ whereas
the standard error of the difference, $\sqrt{\mathrm{SE}_1^2 + \mathrm{SE}_2^2}$, is smaller.
Adding that the converse (no overlap implies significance) is true is excellent.

**P8 (paper, ★★, R4, R5)** Read the section of `li2024-simpler` that defines the metrics and the
section on the real-world correspondence experiments, and §4 of
`agarwal2021-deep-rl-at-the-edge`, and (a) transcribe SIMPLER's definition of MMRV as a formula
and check whether it matches the one in this lesson, (b) find how many trials per policy and per
task the authors' real-world evaluation uses and roughly compute the bound (4), (c) give one case
that grounds the demand of Agarwal et al. for intervals instead of point estimates, (d) decide
whether the argument that the IQM is better than the median rests on statistical efficiency or
on robustness.
*Rubric*: (a) passes if the formula is right (if it differs from this lesson, treat **this
lesson as the one in error** and write down the difference). (b) is the core — you must find the
number of trials and compute the bound with your own hands. If the correlation the paper reports
is above that bound, the skills of the policies are widely spread, and writing that
interpretation is excellent. (c) and (d) pass by quoting the paper.

## Paper reading

**Two must-read papers.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read in three passes, and in the third pass concentrate on questions 5,
6 and 7 — those three questions are the very subject of this lesson.

1. **Li, Hsu, Gu et al., "Evaluating real-world robot manipulation policies in simulation"
   (2024, arXiv 2405.05941)** — role: `frontier`.
   <https://arxiv.org/abs/2405.05941> (the section defining the metrics and the section on the
   real-world correspondence experiments)
   The object of R4 of this lesson. It is an attempt to use simulated evaluation as a **proxy
   metric** for real-world evaluation, and the purpose of reading is "how is the validity of a
   proxy metric verified".
   Additional questions: (a) into which two kinds (control, visual) do the authors divide the
   sim-to-real gap, and how do they reduce each? (b) which metric serves as the evidence of
   validity, and is its **noise floor** reported? (c) how many trials are on the real-world side,
   and what is the bound (4) at that number?
2. **Agarwal, Schwarzer, Castro, Courville & Bellemare, "Deep reinforcement learning at the edge
   of the statistical precipice" (2021, NeurIPS)** — role: `critique`.
   <https://arxiv.org/abs/2108.13264> (§4)
   The primary source for R5 of this lesson, and a paper that demonstrates the concern of R3
   (point estimates from few runs overturn conclusions) empirically on reinforcement learning
   benchmarks.
   Additional questions: (a) which case do the authors show in which the re-analysis **changes
   the ranking**? (b) what is a "stratum" in the stratified bootstrap and why are tasks not
   mixed? (c) in what is a performance profile better, and in what worse, than a one-number
   aggregate?

**Two recommended papers.** `brown2001-binomial-intervals` (a coverage comparison of binomial
intervals — it shows the collapse of Wald in R1 systematically,
<https://doi.org/10.1214/ss/1009213286>) and `gelman2014-type-s-m` (sign and magnitude errors of
significant results — the primary source for R3(a),
<https://doi.org/10.1177/1745691614551642>).

**The ten fixed questions**: (1) what problem is solved under what assumptions (2) what exactly
could earlier work not do (3) the key idea in one line of mathematics (4) what is the theoretical
guarantee and **what is not guaranteed** (5) the independent and dependent variables and baselines
of the experiments, and were they tuned fairly (6) do the metrics match the claims, and are
variance and seeds reported (7) what information needed for reproduction is missing (8) if it is
wrong, which assumption to suspect first (9) computational and memory complexity and real-time
capability (10) what would you change to surpass it a year from now.

## Reproduction task

**Tier R2 (algorithm reimplementation).** Compute budget: one laptop CPU core, under 3 minutes in
total, at most 500 MB of memory. numpy + scipy only. No GPU, simulator or robot is needed.

**Input data**: none. Parts A–D **sum binomial probabilities exactly** and use no random numbers
(the results are deterministic); only Part E uses `np.random.default_rng(20261117)`, created
afresh for each $n$.

```python
"""Reproduction task of s4-evaluation-science: three intervals and exact coverage."""

import numpy as np
from scipy import stats

Z = stats.norm.ppf(0.975)


def wald(k, n):
    p = k / n
    half = Z * np.sqrt(p * (1 - p) / n)
    return p - half, p + half


def wilson(k, n):
    p = k / n
    den = 1 + Z**2 / n
    centre = (p + Z**2 / (2 * n)) / den
    half = Z * np.sqrt(p * (1 - p) / n + Z**2 / (4 * n**2)) / den
    return centre - half, centre + half


def clopper_pearson(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else stats.beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else stats.beta.ppf(1 - alpha / 2, k + 1, n - k)
    return lo, hi


def coverage(interval, n, p):
    """Probability that the interval contains the truth p, summed exactly over the binomial pmf."""
    ks = np.arange(n + 1)
    pmf = stats.binom.pmf(ks, n, p)
    return float(sum(pmf[k] for k in ks if interval(k, n)[0] <= p <= interval(k, n)[1]))
```

**Part A — coverage.** For $n \in \{10, 20, 50, 100\}$ and $p \in \{0.05, 0.06, \dots, 0.95\}$
compute the coverage of the three intervals and report, for each $n$, the minimum over the grid
and the value at $p = 0.9$.

**Part B — power.** Sum the test (5) over all combinations $(k_1, k_2)$ to obtain the power of
$0.6$ vs $0.8$ at $n \in \{10, 20, 50, 82, 100, 200\}$ and compare with the approximation (2) (do
not reject when $\hat{\bar{p}} \in \{0, 1\}$).

**Part C — the winner's curse.** For $0.5$ vs $0.6$ and $n \in \{20, 50, 100, 400\}$ find the
power, the mean $\hat{\Delta}$ given "reject and $\hat{\Delta} > 0$", and the probability of
"reject and $\hat{\Delta} < 0$".

**Part D — selection bias.** Compute the expectation of the maximum of $K$ variants with
$p = 0.5$ exactly as $\mathbb{E}[\max] = \sum_k\frac{k}{n}\big(F(k)^K - F(k-1)^K\big)$ ($F$ the
binomial cumulative distribution) to obtain the bias for $n \in \{20, 50, 100\}$,
$K \in \{5, 20, 100\}$, and compare with the bound (3).

**Part E — attenuation of the correlation.** With $p_i$ = `np.linspace(0.2, 0.8, 10)`,
$S_i = p_i$ (a perfect simulator) and $R_i = \mathrm{Bin}(n, p_i)/n$ drawn 20,000 times, find the
mean Pearson $r$, $\Pr[r < 0.9]$ and the mean MMRV at $n \in \{10, 20, 50, 200\}$ and compare
with (4).

**Acceptance criteria — all five conditions must hold to pass.** Parts A–D are deterministic, so
the tolerances are small.

1. **Part A** — (a) the minimum coverage of Clopper–Pearson at $n = 10, 20, 50, 100$ is
   $0.9623, 0.9586, 0.9534, 0.9543$ (tolerance $10^{-3}$), **all at least $0.95$**. (b) The
   minimum coverage of Wald is $0.4002, 0.6389, 0.8073, 0.8775$, and $0.8760$ at $p = 0.9$,
   $n = 20$. (c) The minimum coverage of Wilson is $0.9139, 0.9245, 0.9315, 0.9332$ — slightly
   below nominal but far better than Wald; report alongside that its mean is near $0.95$.
2. **Part B** — the power is $0.1312, 0.2911, 0.5953, 0.8074, 0.8797, 0.9933$ (tolerance
   $10^{-3}$) and (2) gives $81.2$. Confirm that the rejection rate under the null ($0.7$ vs
   $0.7$) is $0.0533, 0.0498, 0.0510$ at $n = 20, 50, 100$ — a check that the level of the test
   is right.
3. **Part C** — the mean $\hat{\Delta}$ when significant is $0.3842, 0.2436, 0.1798, 0.1115$
   (tolerance $10^{-3}$) and the exaggeration ratios are $3.8, 2.4, 1.8, 1.1$. The power is
   $0.0873, 0.1836, 0.3096, 0.8141$.
4. **Part D** — the bias is within $10^{-3}$ of the nine values of the table in the text
   ($0.1313$ at $n = 50$, $K = 20$) and **all are below the bound (3)**. Confirm that the bias is
   exactly 0 at $K = 1$.
5. **Part E** — the mean $r$ is $0.816, 0.896, 0.955, 0.988$ (tolerance $\pm0.005$),
   $\Pr[r < 0.9]$ is $0.80, 0.45, 0.03, 0.00$ (tolerance $\pm0.02$), and the mean MMRV is
   $0.128, 0.069, 0.026, 0.003$ (tolerance $\pm0.005$). Print them next to the predictions
   $0.795, 0.880, 0.946, 0.986$ of (4).

**Comparison**: (a) for Part A the nominal level $0.95$ is the baseline. (b) For Part B the
approximation (2) is the baseline. (c) For Parts C and D "no bias" (exaggeration ratio 1, bias 0)
is the baseline. (d) For Part E the analytic value of (4) is the baseline.

**Optional task (apply it to published results).** Pick one table of real-world success rates
from `li2024-simpler` or from one of the must-read papers of `s4-vla-architectures` and
(a) compute the Clopper–Pearson interval of every cell, (b) among the comparisons the paper
describes in its text as "A is better than B", separate those that are significant by the test
(5) from those that are not, (c) for one non-significant comparison compute with (2) the number
of trials needed for power 0.8. Acceptance: state the source of the table (paper, table number)
and the number of trials, and submit the three computations as a table. **Copy the numbers
directly from the paper** — do not use a summary from a secondary source.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The Clopper–Pearson coverage drops below 0.95 | The parameters of the beta quantile are wrong ($k+1$ and $k$ swapped) | Check that the lower limit of $20/20$ is $0.025^{1/20} = 0.8316$ |
| The coverage is smooth in $p$ | It was computed by a normal approximation, not an exact sum | The coverage must be sawtooth shaped — plot it with $p$ in steps of $0.001$ |
| The Wald coverage comes out high | Zero-width intervals at $k = 0, n$ were counted as "containing" | A zero-width interval does not contain $p \in (0,1)$ |
| The power of Part B is far below (2) | An unpooled standard error was mixed in, or only one tail was counted | First check that the rejection rate under the null is near $0.05$ |
| The mean $\hat{\Delta}$ of Part C is close to the truth $0.10$ | No conditioning on rejection | Check that only the rejected $(k_1, k_2)$ enter the weighted mean |
| The bias of Part D exceeds the bound (3) | $F(k)$ was used for $F(k-1)$ (the pmf of the maximum is wrong) | Check that the bias is 0 at $K = 1$ and that the pmf sums to 1 |
| The MMRV of Part E is 0 | The inequalities in the rank-violation indicator were written the same way | Check that feeding $R$ in the reverse order of $S$ maximizes MMRV |

## Open problems

- **(Open problem) A standard procedure for measuring the violation of independence in
  real-world evaluation** — the guarantee of R1 leans on the independence of trials, which on
  real hardware is broken by hardware drift, the operator and repeated resets. A procedure that
  **tests for overdispersion and reports the effective sample size** has not taken hold in the
  robot learning literature. Current approaches: hierarchical models with initial conditions as
  clusters, and randomizing or interleaving the order of trials. What is missing: a way to
  estimate overdispersion reliably from few trials (around 10 clusters) and a standard reporting
  format that carries that estimate into the interval.
- **(Open problem) The limits of validity of proxy evaluation** — R4 says only that real-world
  noise sets an upper bound on the sim-to-real correlation. The opposite direction — the number
  of policies and trials needed, on a given real-world budget, to **certify** that "this
  simulator ranks two policies correctly with probability $1-\delta$" — has not been established.
  Current approaches: empirical reports of MMRV and Pearson correlation (`li2024-simpler`), and
  prediction-powered inference from paired real and simulated samples. What is missing:
  finite-sample guarantees under simulator bias that depends on the policy.
- **(Open problem) Adaptive overfitting at the level of a benchmark** — the holdout of R3 works
  inside one laboratory, but a public benchmark has the whole field reusing the same evaluation
  set for years. Nobody knows that cumulative $K$. Current approaches: private evaluation sets
  and evaluation servers, and studies that re-evaluate on new tasks and environments to check
  whether rankings are preserved. What is missing: a way to bound adaptive overfitting when, as
  in real-world evaluation, the evaluation set **cannot be hidden** (a physical environment is
  bound to be public).
- **(Open problem) Metrics beyond the success rate** — binary success throws information away (a
  trial that almost succeeded equals one that failed from the start). Progress and
  partial-success metrics raise the power but bring in **subjectivity of scoring**. Current
  approaches: stage-wise success rubrics and survival analysis of completion time. What is
  missing: design principles for metrics that, under the total measurement error including
  inter-rater reliability, actually have higher power than binary success.

## Concept check

Take it with `rc quiz s4-evaluation-science`. This quiz is a **concept check only**; the real work
is the problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

## How to study this stage

1. **Read the table of the four questions first (10 min)** — the table in "Setup and notation".
   Memorize the four numbers ($0.683$–$0.988$, 82 trials, +13 points, $0.88$). By the end of this
   lesson you must be able to compute those four numbers yourself.
2. **Run Part A first (40 min)** — plot the coverage against $p$ and see the sawtooth. Reading the
   proof of R1 after seeing with your own eyes where Wald collapses makes "why invert tail
   probabilities" obvious.
3. **The five steps of R1 from a blank page (50 min)** — the core is the translation of step 2
   ("the truth is outside the interval" ↔ "the observation is in a tail"). If you can explain why
   the inequality of step 3 is not an equality (discreteness), you have understood where the
   conservatism comes from.
4. **Derive (2), then Part B (50 min)** — the derivation is six lines. Then put the number of
   trials of a robot paper you read recently into (2). This one computation changes how you read
   papers.
5. **See the two biases with Parts C and D (60 min)** — the winner's curse and selection bias are
   different phenomena: the former is a result filtered by **significance**, the latter a result
   of picking the **maximum**. Write in one sentence what they have in common: both are instances
   of "an unbiased estimator, seen conditionally, is biased".
6. **Derive (4), then Part E (40 min)** — the attenuation formula is four lines. The point is to
   see for yourself the fraction (45%) of perfect simulators that produce $r < 0.9$. Look at the
   noise floor of MMRV as well.
7. **The two papers (120 min)** — read SIMPLER tracking only "how was the validity of the proxy
   metric verified". For Agarwal et al., summarize each of the three recommendations of §4
   (intervals, performance profiles, IQM) in one sentence. The one-page note per paper is
   **mandatory**.
8. **Apply it to published results (60 min, optional but recommended)** — the optional task of
   the reproduction task. Attaching intervals to the table of a real paper is the true output of
   this lesson. End by writing a one-page plan for the next real-world evaluation of your own
   research (number of trials, paired design or not, separating selection from reporting).

**Pass criterion**: from a blank page you can derive the five steps of R1, (2), the bound (3) and
(4); you can attach an interval to any "$k/n$ successes"; you can compute the number of trials
needed to compare two success rates; you can explain why evaluation for selection and evaluation
for reporting are kept apart; you have code that satisfies all five conditions of the
reproduction task; and you have notes on the two papers.
