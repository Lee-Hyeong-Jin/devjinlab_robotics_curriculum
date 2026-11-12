---
id: c7-robust-fitting-ransac
lang: en
title: Robust fitting and the theory of RANSAC
summary: >-
  Derive the RANSAC iteration-count formula exactly, from the hypergeometric distribution, and
  then separate numerically what the formula does **not** guarantee — that an all-inlier sample
  yields a good model. Establishes how the minimal sample size enters the cost exponentially and
  what the real limit on contamination is, and solves maximum consensus to global optimality by
  branch and bound, checked against exhaustive enumeration.
objectives:
  - Derive the RANSAC iteration-count formula from the hypergeometric distribution and show numerically when the $w^m$ approximation is optimistic.
  - Distinguish what the iteration-count formula guarantees from what it does not, and explain from measurements why the refit step is mandatory.
  - Derive the inlier threshold $\epsilon$ as a $\chi^2$ quantile of the noise model and compute it for each degree of freedom.
  - Show that the minimal sample size $m$ enters the cost exponentially, and compare the iteration counts of the five-, seven- and eight-point solvers.
  - Derive the branch-and-bound upper bound for maximum consensus by a Lipschitz argument and confirm global optimality against exhaustive enumeration.
tags: [perception, ransac, robust-estimation, consensus-maximization, branch-and-bound, research]
---

# Robust fitting and the theory of RANSAC

## Setup and notation

The recommended prerequisites are `c7-two-view-geometry` in this module (minimal solvers and
degenerate configurations), `r0-estimation-theory` (bias and consistency of estimators) and
`r0-convex-optimization` (relaxations and duality). None of them is locked. The lesson assumes:

- Probability: the binomial, hypergeometric and geometric distributions, quantiles, the $\chi^2$
  distribution and its quantiles, independent trials.
- Optimisation: what combinatorial optimisation means, and the basic structure of branch and bound
  (upper bound, lower bound, pruning).
- Complexity: what NP-hardness means, and the difference between "exponential in the input size
  $n$" and "exponential in the parameter dimension $d$".

Notation (continuing the C7 conventions):

| Symbol | Meaning |
|---|---|
| $n$ | number of data points; $I$ the number of true inliers; $w = I/n$ the inlier ratio |
| $m$ | minimal sample size (line 2, homography 4, essential 5, fundamental 7) |
| $N$ | number of RANSAC iterations |
| $\eta$ | tolerated failure probability (this lesson uses $\eta = 0.01$) |
| $p$ | probability that one draw is all-inlier |
| $\epsilon$ | inlier threshold, in residual units |
| $r_i(\theta)$ | residual of point $i$; $C(\theta) = \{i : r_i(\theta) \le \epsilon\}$ the consensus set |
| $\sigma$ | standard deviation of the inlier noise |
| $\mathcal{B}$, $\rho_\mathcal{B}$ | a box in parameter space and its radius |

**A warning about the word "success"**: it is used here in **three different senses**, and telling
them apart is the core of R1 — (1) drawing an all-inlier sample at least once; (2) that sample
yielding an **accurate** model; (3) the final output of RANSAC being accurate. The iteration-count
formula speaks only about (1).

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (iteration count and failure probability) [D3]** — when $I$ of $n$ points are inliers, the
  probability that a size-$m$ sample drawn without replacement is all-inlier is
  $$p = \frac{\binom{I}{m}}{\binom{n}{m}} = \prod_{k=0}^{m-1}\frac{I-k}{n-k} \;\le\; w^m \tag{1}$$
  with equality as $n \to \infty$, and the probability that none of $N$ independent draws is
  all-inlier is $(1-p)^N$. The smallest number of iterations that pushes this below $\eta$ is
  $$N_\eta = \left\lceil \frac{\log\eta}{\log(1-p)} \right\rceil
    \;\approx\; \frac{\ln(1/\eta)}{p} \quad (p \ll 1). \tag{2}$$
  The number of draws until the first success is $\mathrm{Geom}(p)$, with mean $1/p$ and standard
  deviation $\sqrt{1-p}/p \approx 1/p$ — so **(2) is not a mean but a $1-\eta$ quantile**, about
  4.6 times the mean at $\eta = 0.01$.
- **R2 (what the formula does not guarantee) [D2]** — (2) guarantees only that an all-inlier sample
  is drawn. (1) An all-inlier but **nearly degenerate** sample amplifies noise into a bad model.
  (2) The consensus score can rate the wrong model higher. (3) Adaptive termination estimates
  $\hat{w}$ from the **maximum** support so far, which is biased upward, so $N$ is underestimated
  and the real failure probability exceeds $\eta$. The **refit** after the minimal model is not
  optional.
- **R3 (the threshold comes from the noise model) [D2]** — if the squared residual of an inlier is
  $\sigma^2\chi^2_d$ (isotropic Gaussian, $d$ = number of independent residual components), the
  threshold at significance $\alpha$ is
  $$\epsilon = \sigma\sqrt{\chi^2_{d,\,1-\alpha}}. \tag{3}$$
  At $\alpha = 0.05$: $d=1$ (point-line distance) gives $\epsilon = 1.960\sigma$, $d=2$
  (reprojection error) gives $2.448\sigma$, $d=3$ gives $2.796\sigma$ and $d=4$ gives $3.080\sigma$.
- **R4 (the minimal sample size enters exponentially) [D2]** — from (2) with $p \approx w^m$,
  $$\ln N_\eta \approx \ln\ln(1/\eta) + m\ln(1/w), \tag{4}$$
  so **every extra element of the minimal sample multiplies the cost by $1/w$**. The real limit on
  contamination is not "50%" but two things: the cost blowing up, and the unidentifiability that
  appears once the outliers form a **larger consensus set** than the true structure, in which case
  maximum consensus picks that one.
- **R5 (branch and bound for maximum consensus) [D2]** — maximum consensus
  $\max_\theta \lvert C(\theta)\rvert$ is NP-hard in general. If $r_i$ has Lipschitz constant $L$
  on a box $\mathcal{B}$, then
  $$\max_{\theta\in\mathcal{B}} \lvert C(\theta)\rvert
    \;\le\; U(\mathcal{B}) := \big\lvert\{i : r_i(\theta_c) \le \epsilon + L\rho_\mathcal{B}\}\big\rvert \tag{5}$$
  is a valid upper bound, and best-first search pruned by it returns the **global optimum**.

## Derivation

### R1 — the iteration-count formula

**(1) The hypergeometric probability.** There are $\binom{n}{m}$ ways to draw $m$ of $n$ points
without replacement, of which $\binom{I}{m}$ are all-inlier. The draw is uniform, so

$$p = \frac{\binom{I}{m}}{\binom{n}{m}}
    = \frac{I!/(m!(I-m)!)}{n!/(m!(n-m)!)}
    = \prod_{k=0}^{m-1}\frac{I-k}{n-k}.$$

Each factor satisfies $\frac{I-k}{n-k} \le \frac{I}{n} = w$ (for $k \ge 0$ and $I \le n$,
subtracting from the numerator cuts the ratio more than subtracting from the denominator). So
$p \le w^m$, and as $n \to \infty$ with $I/n \to w$ fixed each factor tends to $w$, giving equality
in the limit. **In other words the textbook formula $p = w^m$ is always optimistic** — it is the
value for sampling with replacement.

Measured ($\eta = 0.01$):

| $n$ | $I$ | $m$ | $w^m$ | exact $p$ | $N$($w^m$) | $N$(exact) | difference |
|---|---|---|---|---|---|---|---|
| 1000 | 500 | 5 | $3.125\times10^{-2}$ | $3.094\times10^{-2}$ | 146 | 147 | $+0.7\%$ |
| 100 | 50 | 5 | $3.125\times10^{-2}$ | $2.814\times10^{-2}$ | 146 | 162 | $+11.0\%$ |
| 100 | 50 | 7 | $7.812\times10^{-3}$ | $6.240\times10^{-3}$ | 588 | 736 | $+25.2\%$ |
| 50 | 25 | 5 | $3.125\times10^{-2}$ | $2.508\times10^{-2}$ | 146 | 182 | $+24.7\%$ |
| 20 | 10 | 5 | $3.125\times10^{-2}$ | $1.625\times10^{-2}$ | 146 | 282 | $+93.2\%$ |

Above $n \approx 1000$ this is negligible, but at $n = 20$ — fitting a homography to a handful of
planar correspondences, say — the required number of iterations **doubles**. Half of the practical
observation that "RANSAC fails unusually often on small data" is this.

**(2) The iteration count.** If draws are independent, the probability that all $N$ fail is
$(1-p)^N$, and

$$(1-p)^N \le \eta \iff N\log(1-p) \le \log\eta \iff N \ge \frac{\log\eta}{\log(1-p)}$$

where the last step flips the inequality because $\log(1-p) < 0$ — losing that sign is the classic
mistake here. For $p \ll 1$, $\log(1-p) \approx -p$, so $N_\eta \approx \ln(1/\eta)/p$, and at
$\eta = 0.01$, $\ln(100) = 4.605$.

**(3) Looking at the whole distribution.** The number of draws $T$ until the first success has
$P(T = k) = (1-p)^{k-1}p$, that is, $\mathrm{Geom}(p)$, with $\mathbb{E}[T] = 1/p$ and
$\mathrm{sd}(T) = \sqrt{1-p}/p$. The coefficient of variation is $\sqrt{1-p} \approx 1$, so **the
mean and the standard deviation are the same size** — budgeting the mean number of iterations
succeeds only about 63% of the time ($1 - e^{-1}$). Measured:

| $w$ | $m$ | mean $1/p$ | sd | $N_{0.99}$ |
|---|---|---|---|---|
| 0.5 | 5 | 32 | 31 | 146 |
| 0.3 | 7 | 4,572 | 4,572 | 21,055 |
| 0.2 | 7 | 78,125 | 78,124 | 359,777 |
| 0.1 | 7 | $10^7$ | $10^7$ | 46,051,700 |

**Where the assumptions break**: (1) independence of draws — PROSAC-style samplers draw
non-uniformly by quality, so (2) does not apply as written. (2) Knowing $w$ — in practice one does
not (R2 (3)). (3) The implicit assumption that the points are independent — tracked features are
correlated, so "$I$ inliers" is effectively fewer.

### R2 — what the formula does not guarantee

(2) is about the probability of event (1) ("an all-inlier sample is drawn at least once"). An
experiment separates (1), (2) and (3).

Measured (2D line fitting, $n = 200$, inlier noise $\sigma = 0.5$, $\epsilon = 1.5$, $m = 2$, 400
trials per setting, $N$ from (2)):

| $w$ | $N_{0.99}$ | (1) at least one all-inlier sample | slope error of the minimal model (median / p90) | after refit (median / p90) | Jaccard of the inlier set |
|---|---|---|---|---|---|
| 0.8 | 5 | 0.993 | 0.0477 / 0.1485 | **0.0057 / 0.0159** | 0.976 |
| 0.5 | 17 | 0.995 | 0.0508 / 0.1308 | **0.0095 / 0.0257** | 0.917 |
| 0.3 | 49 | 0.995 | 0.0586 / 0.1577 | **0.0164 / 0.0431** | 0.822 |

How to read it. The (1) column matches the theoretical $1-\eta = 0.99$ — **the formula is accurate
about what it claims**. And yet the median slope error of the minimal model (a line through two
points) is **5 to 8 times** larger than after the refit. The reason is simple: if the two inlier
points are $\Delta x$ apart in $x$, the slope error grows like $\sqrt{2}\sigma/\Delta x$, and
uniform sampling draws close pairs just as often as far ones. **A minimal sample is a hypothesis
generator, not an estimator.** Refitting by least squares on the consensus set (the local
refinement, the L of LO-RANSAC) is where nearly all of the accuracy comes from.

(3) **The bias of adaptive termination**: not knowing $w$, implementations estimate
$\hat{w} = \max_t \lvert C(\theta_t)\rvert / n$ from the best support so far and update $N$ with
(2). As a maximum statistic, $\hat{w}$ easily has $\mathbb{E}[\hat w] > w$, and $N$ depends on $w$
exponentially ($m\ln(1/w)$, see (4)), so a small upward bias cuts the iteration count a lot. The
consequence is that **the reported $\eta$ is not achieved**. Mitigations are to use a downward
(confidence-bound) correction on $\hat w$ or to floor $N$. This is the motivation behind MAGSAC++
redesigning the score together with the threshold.

### R3 — the threshold $\epsilon$

If the residual vector of an inlier has $d$ independent components, each $N(0,\sigma^2)$, then
$\lVert r\rVert^2/\sigma^2 \sim \chi^2_d$. Requiring "accept an inlier with probability
$1-\alpha$" means $P(\lVert r\rVert^2 \le \epsilon^2) = 1-\alpha$, which is (3). The common values:

| Residual | $d$ | $\sqrt{\chi^2_{d,0.95}}$ | $\epsilon$ |
|---|---|---|---|
| point-line distance, one-sided epipolar distance | 1 | 1.9600 | $1.960\sigma$ |
| reprojection error (2D point) | 2 | 2.4477 | $2.448\sigma$ |
| symmetric transfer error (both images) | 4 | 3.0802 | $3.080\sigma$ |

Measured: in a $10^6$-sample Monte Carlo, $P(\lvert r\rvert < 1.960\sigma) = 0.9499$ and
$P(\lVert r_2\rVert < 2.4477\sigma) = 0.9500$ — (3) confirmed as written.

**Where the assumptions break**: $\sigma$ is unknown. Too large an $\epsilon$ lets outliers into
the consensus and drags the model (and loosens the bound (5), slowing branch and bound); too small
an $\epsilon$ discards true inliers, lowering $w$ and raising the cost exponentially through (4).
$\sigma$ usually differs between scenes and is not even uniform within an image. MAGSAC++ answers
this by not fixing $\sigma$ at all but using a score **marginalised** over a range of $\sigma$ —
§3 of must-read 2.

### R4 — minimal sample size and contamination

Substituting $p \approx w^m$ into (2) and taking logarithms gives (4). In numbers:

$N_{0.99} = \lceil \log 0.01 / \log(1 - w^m)\rceil$

| $w$ | $m=2$ | $m=3$ | $m=4$ | $m=5$ | $m=7$ | $m=8$ |
|---|---|---|---|---|---|---|
| 0.9 | 3 | 4 | 5 | 6 | 8 | 9 |
| 0.7 | 7 | 11 | 17 | 26 | 54 | 78 |
| 0.5 | 17 | 35 | 72 | 146 | 588 | 1,177 |
| 0.3 | 49 | 169 | 567 | 1,893 | 21,055 | 70,188 |
| 0.2 | 113 | 574 | 2,876 | 14,389 | 359,777 | 1,798,893 |
| 0.1 | 459 | 4,603 | 46,050 | 460,515 | 46,051,700 | 460,517,014 |

This table connects directly to the conclusion of `c7-two-view-geometry`: at $w = 0.5$ the
five-point solver needs 146 iterations, the seven-point 588 and the eight-point 1,177 — a factor
of **4 to 8**. At $w = 0.3$ the gap widens to 1,893 against 21,055 against 70,188, more than an
order of magnitude. This table is why a minimal solver is worth a paper.

**The limit on contamination** (failure mode): "RANSAC cannot handle more than 50% outliers" is not
accurate — it needs only one clean sample, so in principle $w$ can be arbitrarily small. The real
limits are two.

1. **Cost**: at $w = 0.1$, $m = 7$, that is $4.6\times10^7$ iterations. At $100\,\mu s$ per
   hypothesis, 1.3 hours.
2. **Unidentifiability**: maximum consensus picks "the largest consensus set". If the outliers
   happen to form — or structurally do form, through repeated patterns, two planes, a moving object
   — a larger consensus set than the true inliers, then RANSAC will pick that one however many
   samples it draws. This limit is a function of $\epsilon$ and the scene structure and **is not
   fixed by more iterations**. Degenerate configurations (R3 and R4 of `c7-two-view-geometry`)
   belong in this category too: coplanar correspondences give a large consensus and a wrong pose.

### R5 — global maximum consensus by branch and bound

The maximum consensus problem

$$\theta^\star \in \arg\max_\theta \lvert C(\theta)\rvert, \qquad
  C(\theta) = \{i : r_i(\theta) \le \epsilon\}$$

is NP-hard for a general design, and more precisely it is known to be **exponential in the
parameter dimension $d$** (Chin et al. 2018 **[D0]**). Still, for small $d$ branch and bound
returns the global optimum.

**Deriving the bound.** Let the box $\mathcal{B}$ have centre $\theta_c$ and radius
$\rho_\mathcal{B}$, and let $r_i$ be Lipschitz on $\mathcal{B}$:
$\lvert r_i(\theta) - r_i(\theta_c)\rvert \le L\rho_\mathcal{B}$ for all
$\theta \in \mathcal{B}$. Then

$$r_i(\theta) \le \epsilon \;\Longrightarrow\; r_i(\theta_c) \le \epsilon + L\rho_\mathcal{B}$$

so $C(\theta) \subseteq \{i : r_i(\theta_c) \le \epsilon + L\rho_\mathcal{B}\}$, which is (5). The
bound $U(\mathcal{B})$ is obtained by evaluating **at a single point** of the box, so it costs
$O(n)$. If $U(\mathcal{B}) \le$ the best value so far, the box is discarded. Halving a box halves
$\rho$, tightening the bound; stopping at a finite resolution leaves the global optimum within that
resolution.

**The concrete form for line fitting.** With the points inside a disc of radius $R$ and the line
parameterised by $(\theta, \rho)$ — $n(\theta) = (\cos\theta, \sin\theta)$ and the residual
$r_i = \lvert x_i^\top n(\theta) - \rho\rvert$ —

$$\left\lvert \frac{\partial r_i}{\partial \theta}\right\rvert
  = \lvert x_i^\top n'(\theta)\rvert \le \lVert x_i\rVert \le R, \qquad
  \left\lvert \frac{\partial r_i}{\partial \rho}\right\rvert = 1$$

so the bound for the box $[\theta_c \pm \Delta\theta] \times [\rho_c \pm \Delta\rho]$ is

$$U = \big\lvert\{i : r_i(\theta_c, \rho_c) \le \epsilon + R\,\Delta\theta + \Delta\rho\}\big\rvert. \tag{6}$$

**Confirming global optimality.** Maximum consensus for a line can also be solved by exhaustive
enumeration: the optimal band can always be translated and rotated until it touches two points, so
it suffices to consider the lines through all pairs of points and their $\pm\epsilon$ translates
($O(n^2)$). Measured ($\epsilon = 0.3$, inlier noise 0.1):

| $n$ | $w$ | branch-and-bound maximum consensus | exhaustive | equal | nodes |
|---|---|---|---|---|---|
| 40 | 0.6 | 24 | 24 | yes | 250 |
| 60 | 0.5 | 34 | 34 | yes | 394 |
| 80 | 0.4 | 36 | 36 | yes | 448 |

**What the measurements say (honestly)**: branch and bound is **cheap** on this problem. The node
count barely grows with $n$ (250 to 450 from $n = 40$ to 320), grows somewhat with the outlier
ratio (250 to 778 from $w = 0.6$ to 0.25), and grows only logarithmically with the box resolution
(387 to 658 as the tolerance goes from $10^{-1}$ to $10^{-6}$). The worst case $(1/\delta)^d$ **is
not realised on this easy instance**. The point is that $d = 2$. That is why branch and bound is
practical for rotation search ($d = 3$, Go-ICP) and for 1D problems, and is not used for an 8-DOF
homography or a 6-DOF pose. **"NP-hard" is a statement about $d$, not about $n$.**

## Proof sketch

### R1 — the rigorous form of the iteration-count formula

**Hypotheses** H1: each iteration draws a size-$m$ sample **uniformly and without replacement**
from $n$ points, and iterations are independent. H2: there are $I = wn$ inliers. H3: "success"
means drawing an all-inlier sample at least once.
**Conclusions** C1: $p$ is (1) and $p \le w^m$. C2: the failure probability after $N$ iterations is
$(1-p)^N$ and the minimal iteration count is (2). C3: the time of the first success is
$\mathrm{Geom}(p)$ with $\mathbb{E}[T] = 1/p$.

**Strategy**: counting for a uniform draw, then the product over independent trials, then the
geometric distribution.

1. **C1**: the sample space is all size-$m$ subsets ($\binom{n}{m}$ of them) under the uniform
   distribution (H1), of which $\binom{I}{m}$ are all-inlier. Computing the ratio gives the product
   form. The inequality $\frac{I-k}{n-k} \le \frac{I}{n}$ follows by cross-multiplying:
   $n(I-k) \le I(n-k) \iff -nk \le -Ik \iff Ik \le nk$, which holds because $I \le n$ and
   $k \ge 0$. $\square$
2. **C2**: by the independence in H1, failing all $N$ times is the product of the per-iteration
   failures, $(1-p)^N$. Applying the monotone $\log$ and dividing by $\log(1-p) < 0$ flips the
   inequality and gives (2). $\square$
3. **C3**: $P(T = k)$ is the product of $k-1$ failures and one success, which is the geometric
   distribution; the mean and variance are standard. $\square$
4. **What H3 does not say**: nowhere in C1-C3 is there any statement that the model is accurate.
   The measurements of R2 size that gap: at $w = 0.8$ event (1) has probability 0.993 while the p90
   slope error of the minimal model, 0.1485, is nine times the value after refit (0.0159). **A
   textbook case of a theorem that is true and of limited use.**
5. **Remove a hypothesis**: drop the independence of H1 (as PROSAC and NAPSAC do, sampling by
   quality or proximity) and (2) is void; those methods have to derive their own stopping rules.
   Drop "we know $I$" from H2 and the bias of $\hat w$ (R2 (3)) enters, breaking the $\eta$
   guarantee. Replacing uniform-without-replacement by sampling **with** replacement makes
   $p = w^m$ exact, but then samples can contain a repeated point and the model computation becomes
   singular — the case implementations usually filter out silently.

Step left out: the mean and variance of the geometric distribution. Standard; see
`r0-estimation-theory`.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R1·R4)** Derive (2) and (4) from (1), and say how many times larger $N_\eta$
is than the mean iteration count $1/p$ at $\eta = 0.01$. Then answer: if you run exactly the mean
number of iterations, what is the success probability?
*Solution sketch*: with $\log(1-p) \approx -p$, $N_\eta \approx \ln(1/\eta)/p = 4.605/p$, that is,
4.605 times the mean. Running the mean gives $1-(1-p)^{1/p} \to 1 - e^{-1} = 0.632$.

**P2 (proof, ★★★, R5)** Prove that (5) is a valid upper bound, and that best-first branch and bound
pruned by it is **globally optimal** within a finite resolution $\delta$. Then say why the bound
must be **monotone** (tightening when a box is split), and give a counterexample showing what
breaks with a non-monotone bound.
*Strategy and key inequality*: everything follows from
$C(\theta) \subseteq \{i : r_i(\theta_c) \le \epsilon + L\rho\}$. For global optimality, show by
induction that a box containing the optimum is never pruned
($U \ge \lvert C(\theta^\star)\rvert \ge$ the incumbent). Without monotonicity a child's bound may
exceed its parent's, so the pruning order can discard the optimum.

**P3 (numerical, ★, R3)** For isotropic Gaussian noise with $\sigma = 0.8$ px, compute the
$\alpha = 0.05$ threshold $\epsilon$ for (a) the point-line distance, (b) the 2D reprojection
error, (c) the symmetric transfer error (both images). (d) What does (b) become at $\alpha = 0.01$?
*Answer*: (a) $1.960 \times 0.8 = 1.568$; (b) $2.4477 \times 0.8 = 1.958$;
(c) $3.0802 \times 0.8 = 2.464$; (d) $\sqrt{\chi^2_{2,0.99}} = \sqrt{9.2103} = 3.0349$, so
$2.428$. Tolerance $10^{-3}$. Check: a $10^6$-sample Monte Carlo acceptance rate within $\pm0.002$
of $1-\alpha$.

**P4 (numerical, ★★, R1·R4)** For $n = 30$, $I = 15$, $m = 7$ (the fundamental matrix), compute
(a) the $w^m$ approximation, (b) the exact hypergeometric $p$, (c) $N_{0.99}$ for each, (d) the
difference in percent. (e) What is the difference at $n = 3000$ with the same $w$?
*Answer*: (a) $0.5^7 = 7.8125\times10^{-3}$; (b)
$p = \prod_{k=0}^{6}\frac{15-k}{30-k} = 2.4105\times10^{-3}$; (c) 588 against 1910; (d) $+225\%$,
more than three times; (e) at $n = 3000$, $p = 7.7016\times10^{-3}$ and $N = 597$, a difference of
$+1.5\%$. Tolerance 2%. Check: $\binom{15}{7}/\binom{30}{7} = 6435/2035800$.

**P5 (implementation, ★★, R1·R2)** Write a line-fitting RANSAC and measure (a) whether the
empirical probability of event (1) matches $1-\eta$, and (b) the accuracy difference between the
minimal model and the refit. Refit by least squares on the consensus set.
*Rubric*: (a) the empirical probability of (1) is within $\pm0.02$ of $1-\eta$; (b) the refit cuts
the median slope error by at least a factor of 3; (c) you show that with adaptive termination the
actual failure rate **exceeds** $\eta$; (d) the threshold is computed from (3) with the reasoning
written down.

**P6 (counterexample, ★★, R4)** Construct a dataset on which RANSAC returns a wrong model however
many iterations it is given: the outliers must form a **larger consensus set** than the true
inliers. Then say what happens when $\epsilon$ is reduced, and what new problem that creates.
*Property checklist*: (a) add a second structure (line or plane) with more points than the true
one; (b) raising the iteration count to $10\times N_{0.99}$ does not change the result; (c) confirm
that the answer is correct **by the definition** of maximum consensus (it is not a bug); (d)
reducing $\epsilon$ drops true inliers too, lowering $w$ and raising the cost exponentially via
(4); (e) one line on why multi-model fitting is a different problem.

**P7 (numerical, ★★, R5)** Implement the bound (6), run branch and bound, and confirm on at least
three instances that the maximum consensus is **exactly** the same as exhaustive enumeration over
the $O(n^2)$ point pairs. Then measure the node count against (a) $n$, (b) the outlier ratio, (c)
the box resolution, and tabulate it.
*Answer (reference measurements)*: $n=40, w=0.6$ gives consensus 24 with 250 nodes;
$n=60, w=0.5$ gives 34 with 394; $n=80, w=0.4$ gives 36 with 448. The node count goes from 250 to
450 as $n$ goes from 40 to 320, from 250 to 778 as $w$ goes from 0.6 to 0.25, and from 387 to 658
as the resolution tightens from $10^{-1}$ to $10^{-6}$. Tolerance: the consensus counts must match
**exactly**; node counts are implementation-dependent, so matching the trend is enough.

**P8 (paper, ★★, R3)** Read MAGSAC++ and write in one equation how the score the authors obtain by
marginalising $\sigma$ differs from (3) of this lesson. Then write (a) what the method does and does
not guarantee, (b) whether the iteration-count formula (2) is still used in MAGSAC++, and (c)
whether the baselines in the comparison are fairly tuned — in particular each baseline's $\epsilon$.
*Rubric*: going beyond "the threshold goes away" and naming the integral form of the
marginalisation and the point where it turns into a weighted score. For (c), checking whether the
paper says how each baseline's $\epsilon$ was chosen is an excellent answer.

## Paper reading

**Two must-reads.** Write a one-page note on each, using the ten fixed questions
(`lesson-standard.md` §5). Read in three passes, and attack questions 4, 5, 6 and 7 in the third.
For the full bibliography, including the recommended papers, run
`rc papers c7-robust-fitting-ransac`.

1. **Fischler & Bolles, "Random sample consensus" (1981, Communications of the ACM)** — role:
   `seminal`. <https://doi.org/10.1145/358669.358692>
   Extra questions: (a) what claim did the 1981 paper make against "smoothing" (least-squares-based
   robustification), and which part of that claim still holds today? (b) Is the termination rule
   the authors give the same as (2) of this lesson? (c) How does the paper's discussion of
   threshold selection differ from (3)?
2. **Barath, Noskova, Ivashechkin & Matas, "MAGSAC++, a fast, reliable and accurate robust
   estimator" (2020, CVPR)** — role: `frontier`. <https://arxiv.org/abs/1912.05909> (§3 is the core.)
   Extra questions: (a) what assumption does the $\sigma$-marginalised score use in place of the
   fixed threshold of (3)? (b) Does the reported speed-up come from the score function or from the
   implementation (sampler, preprocessing) — does the paper separate the two? (c) Does the method
   solve degenerate configurations (failure mode 2 of R4 here)?

**The ten fixed questions**: (1) which problem under which assumptions; (2) what exactly earlier
work could not do; (3) the core idea in one equation; (4) what is guaranteed and **what is not**;
(5) the independent and dependent variables and the baselines, fairly tuned or not; (6) whether the
metric matches the claim, and whether variance and seeds are reported; (7) what is missing for
reproduction; (8) the first assumption to doubt if the result were wrong; (9) time and memory
complexity and real-time behaviour; (10) what you would change to go beyond it in a year.

**Recommended**: Chin et al. 2018 (where the hardness lives), Go-ICP (branch and bound over
rotation space), MVG ch.4.7.

## Reproduction task

**Tier R1 (numerical check).** Budget: one laptop CPU core, under 5 minutes in total, numpy and
scipy only. The input is a generator this lesson specifies; no external data is needed.

**Generator (fixed)**: $\lfloor wn \rfloor$ inliers on the line $y = 1.3x - 2$
($x \sim U(-10,10)$, with $N(0, 0.5^2)$ noise added to $y$) and $n - \lfloor wn\rfloor$ outliers
($x \sim U(-10,10)$, $y \sim U(-30,30)$), with $n = 200$ and $\epsilon = 1.5$. Report with a fixed
seed.

All **five conditions** must hold to pass. Every reference value was measured for this lesson.

1. **Empirical confirmation of the iteration-count formula (the main point)**: for
   $(w, m, n) \in \{(0.8,2,200), (0.5,2,200), (0.3,2,200), (0.6,4,500), (0.5,5,1000),
   (0.4,7,2000)\}$, collect the number of draws until the first all-inlier sample over at least
   1,500 independent trials, take the **99th percentile**, and match
   $N_{0.99} = \lceil\log 0.01/\log(1-w^m)\rceil$ to within **10%**.
   (Reference ratios: 1.000, 1.000, 0.959, 1.059, 1.055, 1.009.)
2. **The hypergeometric correction**: at $(n,I,m) = (100,50,7)$ the exact $p$ is smaller than $w^m$
   and $N(\text{exact})/N(w^m) \ge 1.2$ (reference 1.252), while at $(1000,500,5)$ that ratio is
   $\le 1.02$ (reference 1.007).
3. **What the formula does and does not guarantee**: at $w = 0.5$, $m = 2$, $N = 17$, over at least
   400 trials, (a) the empirical probability of event (1) is $0.99 \pm 0.02$ (reference 0.995) and
   (b) the median slope error of the minimal model is at least **3 times** the value after
   refitting on the consensus set (reference 0.0508 against 0.0095, a factor of 5.3).
4. **Threshold calibration**: with $\epsilon = 1.960\sigma$ ($d=1$) and $2.4477\sigma$ ($d=2$) from
   (3), the acceptance rate over $10^6$ samples is $0.95 \pm 0.002$ (reference 0.9499, 0.9500).
5. **Global maximum consensus**: implement branch and bound with the bound (6) and, on **at least
   three** instances with $n \le 100$, match the maximum consensus of exhaustive enumeration
   ($O(n^2)$ point pairs plus the $\pm\epsilon$ translates) **exactly**. (Reference: 24/24, 34/34,
   36/36.)

**State this in the report**: the table of node counts from condition 5 against $n$, the outlier
ratio and the box resolution, and how that table shows that "branch and bound is cheap only when
$d$ is small". In the reference measurements the node count grew by 1.8x for an 8x increase in $n$
and by 1.7x for a $10^5$-fold tightening of the resolution — the worst case $(1/\delta)^d$ does not
appear at $d = 2$.

**Baselines**: (1) the theoretical formula (2) (condition 1); (2) exhaustive enumeration
(condition 5); (3) `skimage.measure.ransac` or OpenCV's `USAC_MAGSAC` on the same generator, to
compare iteration counts and accuracy (if installed).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| the empirical 99th percentile is half the theoretical value | success was defined as "the support is high" (event (3)) | redefine success as "the sample indices are all inliers" and recount |
| the empirical value is more than twice the theoretical one | you sampled with replacement (a repeated point) or $m$ is wrong | check one sample's indices for duplicates |
| the refit does not improve accuracy | you refitted on the minimal sample rather than the consensus set | print how many points went into the refit |
| branch and bound returns a larger value than exhaustive enumeration | the bound was used as a lower bound, or $L$ is underestimated | check $R = \max\lVert x_i\rVert$ and that $U$ is at least each child's $U$ |
| branch and bound returns a smaller value | the pruning test is $U \le \text{best}$ instead of $U < \text{best}$ | stop discarding on equality |
| branch and bound never terminates | there is no stopping resolution, or the bound does not tighten | log the box radius and confirm it halves |

## Open problems

- **(open problem) a principled way to set the threshold and noise scale from the data** — (3)
  assumes $\sigma$ is known, but in a real scene it is not, and it is not even uniform.
  [MAGSAC++](https://arxiv.org/abs/1912.05909), which marginalises $\sigma$ away, is the practical
  answer, but there is no theory for how the $\sigma$ prior used in that marginalisation should
  change with the scene. What is missing: a bound on how the estimation error of the noise scale
  propagates into the final pose error.
- **(open problem) an honest confidence guarantee for adaptive termination** — as R2 (3) showed,
  the standard stopping rule that estimates $\hat w$ from the maximum support does not achieve
  $\eta$. There is no stopping rule that corrects the selection bias and stays practical (not
  absurdly conservative). Current approaches: the complexity viewpoint of
  [Chin et al. 2018](https://arxiv.org/abs/1802.06464) and the score redesign of MAGSAC++. What is
  missing: a stopping rule that actually delivers the $\eta$ it reports.
- **(open problem) global maximum consensus in higher parameter dimensions** — branch and bound is
  practical for $d \le 3$ (measured: a few hundred nodes at $d = 2$) and is not used for a
  homography (8) or a pose (6). Raising $d$ without giving up global optimality has only partial
  results from mixed-integer programming and relaxations. Current approaches:
  [Go-ICP](https://arxiv.org/abs/1605.03344) (rotation search at $d = 3$) and
  [TEASER](https://arxiv.org/abs/2001.07715) (decoupling plus certification). What is missing:
  real-time global maximum consensus for an 8-DOF model.
- **(open problem) handling multiple structures and degeneracy at once** — maximum consensus assumes
  there is **one** structure. With a moving object, two planes or a repeated pattern, the largest
  consensus need not be the true structure (failure mode 2 of R4), and a degenerate configuration
  gives a large consensus together with a wrong pose. There is no framework that treats multi-model
  fitting and degeneracy detection together. Current approaches: model-selection heuristics and the
  weighted scoring of [MAGSAC++](https://arxiv.org/abs/1912.05909). What is missing: a principled
  criterion that infers the number of structures and the degeneracy jointly. The question continues
  in `c7-learned-correspondence-slam`.

## Concept check

Run `rc quiz c7-robust-fitting-ransac`. The quiz is for **concept checking only**; the real work is
the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: what the iteration-count formula actually guarantees; in which direction the
$w^m$ approximation errs; the $\alpha = 0.05$ inlier threshold for a 2D reprojection error; the
factor by which the cost grows per extra element of the minimal sample; and why branch and bound is
used for rotation search but not for a homography.

## How to study this stage

1. **Do the counting first (40 min)** — turn (1) from $\binom{I}{m}/\binom{n}{m}$ into the product
   form by hand, and verify $\frac{I-k}{n-k} \le w$ by cross-multiplying. Then find the place in (2)
   where the inequality flips. Use P4 to feel the size of the correction at small $n$.
2. **See it as a geometric distribution (30 min)** — write down the difference between the mean
   $1/p$ and $N_{0.99} = 4.605/p$, and compute "running the mean succeeds 63% of the time" yourself
   (P1). That intuition is the whole of budgeting in practice.
3. **Separate the formula from the accuracy (90 min)** — implement line RANSAC and count only event
   (1), matching the theory (conditions 1 and 3(a)). **Then** compare the error of the minimal model
   with the error after refit (condition 3(b)). Seeing those two numbers differ is the central
   experience of this lesson.
4. **Break adaptive termination on purpose (60 min)** — use the standard implementation that
   estimates $\hat w$ from the maximum support and measure whether the actual failure rate exceeds
   $\eta$ (P5(c)). If it does not, raise the number of trials.
5. **Derive the threshold before using it (30 min)** — compute (3) from the $\chi^2$ quantile and
   confirm the acceptance rate by Monte Carlo (condition 4). After that you will never again leave
   $\epsilon$ at "3 pixels, from experience" in any code.
6. **Find the global optimum yourself (120 min)** — implement the bound (6), run branch and bound
   and match exhaustive enumeration **exactly** (condition 5). Then measure the node count against
   $n$, the outlier ratio and the resolution, and tabulate where the difficulty actually lives (P7).
7. **Two papers and the notes (120 min)** — read Fischler & Bolles first and write down what
   survives from the 1981 framing. Then read MAGSAC++ §3 against (3). Write the one-page note per
   paper **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the open problems and write a paragraph on
   why it is still open. An honest confidence guarantee for adaptive termination is one you could
   start on today.

**Passing bar**: you can derive (1) and (2) on a blank page, you can state in one sentence each
what the iteration-count formula guarantees and what it does not, you have code that passes all five
conditions of the reproduction task, you have matched branch and bound to exhaustive enumeration, and
you have notes on both papers.
