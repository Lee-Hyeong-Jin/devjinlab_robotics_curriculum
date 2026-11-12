---
id: r0-estimation-theory
lang: en
title: Probability and estimation theory
summary: >-
  Derive that MAP estimation in a linear-Gaussian model is weighted least squares, prove the
  Cramer-Rao bound, and organise the relation between consistency, efficiency and Fisher
  information.
objectives:
  - Derive that the MAP estimate of a linear-Gaussian model is weighted least squares.
  - Define Fisher information and show it equals the information matrix in the linear-Gaussian case.
  - Prove the Cramer-Rao bound and state its assumptions (unbiasedness, regularity).
  - Distinguish consistency, efficiency and asymptotic normality and evaluate an estimator against them.
  - Decide with NEES whether an estimator reporting a covariance is overconfident.
tags: [estimation, probability, cramer-rao, fisher-information, research]
---

# Probability and estimation theory

## Setup and notation

| Symbol | Meaning |
|---|---|
| $x \in \mathbb{R}^n$ | the state (or parameter) to be estimated |
| $z = Hx + w$, $w \sim \mathcal{N}(0,R)$ | linear-Gaussian observation model |
| $\hat{x}$ | the estimate; $\Sigma = \mathrm{Cov}(\hat{x})$ |
| $\Lambda = H^\top R^{-1}H$ | the information matrix |
| $\mathcal{I}(x)$ | the Fisher information matrix |
| $\mathrm{NEES}$ | normalised estimation error squared, $e^\top\Sigma^{-1}e$ |

Assumed: `f0-probability-statistics` (Bayes, the three Gaussian properties) and
`r0-numerical-optimization` (least-squares solvers).

## Key results

- **R1 (MAP = weighted least squares) [D2]** — with prior $x \sim \mathcal{N}(\mu_0, \Sigma_0)$ and
  observation $z = Hx+w$, $w\sim\mathcal{N}(0,R)$, the MAP estimate is

$$
\hat{x} = \arg\min_x \tfrac12\lVert z - Hx\rVert^2_{R^{-1}} + \tfrac12\lVert x-\mu_0\rVert^2_{\Sigma_0^{-1}}, \tag{1}
$$

  i.e. **weighted least squares**, with solution
  $(\Sigma_0^{-1} + H^\top R^{-1}H)\hat{x} = \Sigma_0^{-1}\mu_0 + H^\top R^{-1}z$.
- **R2 (posterior covariance = inverse information) [D2]** — in that model the posterior is
  Gaussian with

$$
\Sigma_{\text{post}} = \big(\Sigma_0^{-1} + H^\top R^{-1}H\big)^{-1} . \tag{2}
$$

  The way to read it is that **observations add information** (inverse covariances add).
- **R3 (Fisher information and the CRLB) [D3]** — under regularity conditions, the covariance of an
  **unbiased** estimator $\hat{x}$ satisfies

$$
\mathrm{Cov}(\hat{x}) \succeq \mathcal{I}(x)^{-1}, \qquad
\mathcal{I}(x) = \mathbb{E}\big[\nabla_x\log p(z|x)\,\nabla_x\log p(z|x)^\top\big] . \tag{3}
$$

  In the linear-Gaussian case $\mathcal{I} = H^\top R^{-1}H = \Lambda$ and the MLE **attains** the bound.
- **R4 (consistency, efficiency, asymptotic normality) [D2]** — the three differ:
  **consistency** (convergence to the truth as samples grow), **efficiency** (attaining the CRLB)
  and **asymptotic normality** (the error distribution converging to a Gaussian). Under regularity
  the MLE is consistent, asymptotically normal and asymptotically efficient, but **can be biased in
  finite samples**.
- **R5 (detecting overconfidence with NEES) [D2]** — if the reported $\Sigma$ is correct then
  $\mathrm{NEES} = e^\top\Sigma^{-1}e \sim \chi^2_n$, so $\mathbb{E}[\mathrm{NEES}] = n$.
  **$\mathrm{NEES} \gg n$ means overconfidence** (the covariance is reported too small) and
  $\ll n$ means over-conservatism.

## Derivation

### R1 — why MAP becomes weighted least squares

Bayes' theorem gives $p(x|z) \propto p(z|x)p(x)$, and a Gaussian density carries a quadratic form
in its exponent:

$$
-\log p(x|z) = \tfrac12(z-Hx)^\top R^{-1}(z-Hx) + \tfrac12(x-\mu_0)^\top\Sigma_0^{-1}(x-\mu_0) + \text{const} .
$$

Taking logarithms makes **the quadratic form in the exponent the cost function itself** — which is
(1). Maximisation becomes minimisation because of the sign, and the constant is dropped as it does
not depend on $x$.

Differentiating in $x$ and setting to zero,

$$
-H^\top R^{-1}(z-Hx) + \Sigma_0^{-1}(x-\mu_0) = 0
\;\Longrightarrow\; (\Sigma_0^{-1}+H^\top R^{-1}H)x = \Sigma_0^{-1}\mu_0 + H^\top R^{-1}z .
$$

**Three ways to read it**: (a) the weights are **inverse covariances** — uncertain observations
enter lightly; (b) the prior enters with the same standing as "one more observation"; (c) the
matrix on the left is exactly the posterior information matrix, which gives (2). The whole of
factor graphs in C5 is (1) with many more terms.

**Where the assumption breaks**: for a nonlinear observation $z = h(x)+w$, $-\log p$ is not a
quadratic form and (1) is not exact. Linearising makes it weighted least squares, but then **the
Jacobian depends on the current estimate**, so it must be iterated — Gauss-Newton in
`c1-manifold-optimization` is that iteration.

### R5 — NEES and its distribution

If the error $e = \hat{x}-x$ is $\mathcal{N}(0,\Sigma)$ and the reported covariance equals the
true one, then $\Sigma^{-1/2}e \sim \mathcal{N}(0,I_n)$ and

$$
\mathrm{NEES} = e^\top\Sigma^{-1}e = \lVert\Sigma^{-1/2}e\rVert^2 \sim \chi^2_n ,
$$

so $\mathbb{E}[\mathrm{NEES}] = n$ and $\mathrm{Var} = 2n$. Averaging over $M$ Monte Carlo runs,
the 95% interval for $\overline{\mathrm{NEES}}$ comes from quantiles of $\chi^2_{nM}/M$, and
falling outside it means **the reported covariance is wrong**.

**Why it matters**: judging an estimator only by "the error is small" cannot catch overconfidence,
which is fatal in fusion — wrong information is trusted too much and suppresses other
observations. The EKF inconsistency discussion of C5 and the evaluation procedures of S1 use this metric.

## Proof sketch

### R3 — the Cramer-Rao bound

**Hypotheses** H1: $p(z|x)$ is differentiable in $x$ and integration and differentiation may be
exchanged (regularity). H2: $\hat{x}(z)$ is **unbiased** ($\mathbb{E}[\hat{x}] = x$).
**Conclusion** C: (3).

**Strategy**: apply Cauchy-Schwarz to the covariance of the score function and the estimation error.

1. The score $s(z,x) := \nabla_x\log p(z|x)$ has zero mean:
   $\mathbb{E}[s] = \int \nabla_x p\,dz = \nabla_x\int p\,dz = \nabla_x 1 = 0$
   (H1 is used here — exchanging integration and differentiation).
2. Differentiate unbiasedness: $\nabla_x\mathbb{E}[\hat{x}] = I$, and expanding the left side,
   $\int \hat{x}\,\nabla_x p\,dz = \int \hat{x}\,s\,p\,dz = \mathbb{E}[\hat{x}s^\top] = I$. Since
   $\mathbb{E}[s]=0$ from step 1, $\mathrm{Cov}(\hat{x}, s) = \mathbb{E}[(\hat{x}-x)s^\top] = I$.
3. The joint covariance matrix
   $\begin{bmatrix}\mathrm{Cov}(\hat{x}) & I\\ I & \mathcal{I}\end{bmatrix} \succeq 0$
   (the joint covariance of any two random vectors is positive semidefinite).
4. By the Schur complement condition (`r0-sparse-linear-algebra` R3), if $\mathcal{I} \succ 0$ then
   $\mathrm{Cov}(\hat{x}) - I\mathcal{I}^{-1}I \succeq 0$, which is C.
5. **Equality condition**: attained when $\hat{x}-x$ and $s$ are linearly dependent, i.e.
   $\hat{x}-x = \mathcal{I}^{-1}s$. In the linear-Gaussian case the MLE has exactly this form.

**Delete a hypothesis**: without H2 (unbiasedness), **a biased estimator can have smaller variance
than the CRLB** (in the extreme, $\hat{x} \equiv 0$ has zero variance). So the CRLB must not be
mistaken for an unreachable wall — it is a limit among unbiased estimators. An example where
regularity (H1) fails is a distribution whose support depends on $x$ (estimating the bound of a
uniform distribution).

**Practical consequence**: in robotics the CRLB is used to **evaluate the ceiling for sensor
placement and trajectory design** (the information-gathering planning of
`s5-active-information-gathering`). And since $\mathcal{I} = \Lambda$, the reading "the inverse of
the information matrix is the smallest achievable covariance" is used throughout C5.

## Problem set

★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1·R2)** Show that without a prior ($\Sigma_0^{-1} \to 0$) the solution of
(1) reduces to ordinary least squares, and confirm the posterior covariance is then
$(H^\top R^{-1}H)^{-1}$. What happens if $H$ is rank deficient?
*Solution sketch*: with the prior gone the information matrix is only $H^\top R^{-1}H$, which under
rank deficiency has no inverse — leaving **directions not determined by the observations**. Those
directions are the gauge of `c1-manifold-optimization`.

**P2 (derivation, ★★, R3)** Compute directly that $\mathcal{I} = H^\top R^{-1}H$ in the
linear-Gaussian case.
*Solution sketch*: $\log p(z|x) = -\tfrac12(z-Hx)^\top R^{-1}(z-Hx)+c$ gives
$s = H^\top R^{-1}(z-Hx)$, and $\mathbb{E}[ss^\top] = H^\top R^{-1}\mathbb{E}[ww^\top]R^{-1}H
= H^\top R^{-1}H$.

**P3 (proof, ★★★, R3)** Write the CRLB proof with no gaps and state explicitly why exchanging
integration and differentiation is needed in step 2. Give an example of a distribution where that
exchange fails.
*Solution sketch*: if the support depends on $x$ (e.g. $\mathrm{Unif}(0,x)$) differentiation moves
the limits of integration and the exchange fails. The CRLB then does not hold, and unbiased
estimators of smaller variance genuinely exist.

**P4 (numerical, ★, R2·R5)** With $H = [1]$ (scalar), $R = 4$ and $N$ independent observations,
find (a) the posterior covariance, (b) the CRLB, (c) the expected NEES at $N=100$.
*Answer*: (a) $(N/4)^{-1} = 4/N$; (b) the same ($4/N$) — the MLE is efficient; (c) $n=1$ so
$\mathbb{E}[\mathrm{NEES}]=1$, independent of the sample size. Tolerance $10^{-9}$.

**P5 (implementation, ★★, R3·R5)** For a linear-Gaussian model, (a) estimate the sample covariance
of the MLE over $M=10^4$ Monte Carlo runs and compare with the CRLB, and (b) compare the mean NEES
with the 95% interval of $\chi^2_n$.
*Rubric*: (a) the CRLB is shown to be attained to within 5% relative error; (b) the mean NEES lies
inside the interval; (c) an estimator that **deliberately reports $R$ two times too small** is
built and its NEES is shown to leave the interval from above; (d) the covariance is confirmed to
shrink like $1/N$ as the sample size varies.

**P6 (counterexample, ★★, R3·R4)** Construct an estimator with variance **smaller** than the CRLB
(hint: allow bias) and decide whether it is consistent. Explain why "breaking the CRLB" is not a violation.
*Property checklist*: $\hat{x} = \alpha\bar{z}$ with $0<\alpha<1$ has smaller variance but is
biased, and is not consistent unless $\alpha \to 1$. Since the CRLB assumes **unbiasedness**, this
is no violation.

## Paper reading

**The textbook exception applies** (lesson standard §5). Read the following and write two one-page
notes (fixed questions 1, 3, 4 and 8).

1. **Barfoot, *State Estimation for Robotics*, ch.2-3** — questions: (a) write how the author
   distinguishes MAP from maximum likelihood (with and without a prior). (b) find where the author
   says that "if everything is Gaussian, estimation reduces to linear algebra" and organise the
   conditions for it.
2. **Thrun, Burgard & Fox, *Probabilistic Robotics*, ch.2-3** — questions: (a) state the two
   assumptions used in deriving the recursive Bayes filter (Markov, observation independence) and
   when they fail. (b) does this book address the **consistency** of the covariance? If not, write
   why that is a problem.

**One methodological source**: procedures for NEES and covariance-consistency evaluation — read
them alongside the evaluation tooling of `s1-slam-benchmarking`.

## Reproduction task

**Tier R1 (numerical check).** Budget: under one minute on a laptop CPU, numpy only. All four
conditions must pass.

1. **Attaining the CRLB**: for a linear-Gaussian model ($n=3$, $m=10$ observations), repeat the MLE
   $M=10^4$ times, compute the sample covariance, and confirm it matches the CRLB
   $(H^\top R^{-1}H)^{-1}$ **entrywise to within 5% relative error**.
2. **The NEES interval**: in the same experiment, confirm the mean NEES lies inside the 95%
   interval of $\chi^2_{nM}/M$ (compute and print the interval in code).
3. **Detecting overconfidence**: build an estimator reporting **half** the true covariance and show
   its mean NEES leaves the interval **from above**, and one reporting **twice** it leaving from below.
4. **$1/N$ convergence**: varying the number of observations over $N \in \{10, 100, 1000\}$,
   confirm the diagonal of the posterior covariance shrinks like $1/N$ with a log-log slope of
   $-1\pm0.1$.

**Baseline**: the weighted least-squares solution from `numpy.linalg.lstsq` and the analytic
solution of (1) must agree to within $10^{-10}$.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| the sample covariance is below the CRLB | the same random numbers were reused (correlation), or the estimator is biased | change the seed every run and print $\mathbb{E}[\hat{x}]-x$ |
| NEES is far outside the interval | the reported and true covariances differ (a bug, unless deliberate) | print $R$ and $\Sigma$ and check that the model matches the generating process |
| the slope in condition 4 is not $-1$ | the observations were not generated independently | check the correlation of the noise samples |
| the CRLB computation is singular | $H$ is rank deficient (P1) | print the numerical rank of $H$ together with the threshold |

## Open problems

- **(Open) Achievable limits in the nonlinear, non-Gaussian case** — the CRLB is a limit under
  unbiasedness and regularity. **What the achievable lower bound is** on manifolds (C1) and for
  multi-modal posteriors is not settled in general. Manifold variants of the CRLB have been
  proposed but none is standard in robotics practice.
- **(Open) Finite-sample guarantees** — the efficiency of the MLE is **asymptotic**. Robotics must
  estimate with few observations (initialisation, short trajectories), where bias and covariance
  guarantees are lacking.
- **(Open) Standardising consistency evaluation** — NEES requires ground truth, which makes it hard
  to use in real-robot experiments. Ways to **evaluate covariance consistency without ground
  truth** are limited (the same item as the open problems of `s1-slam-benchmarking` and
  `s4-evaluation-science`).

## Concept check

Run `rc quiz r0-estimation-theory` (add `--lang en` for the English text). It is for concept
checking only.

The four items cover: what MAP equals in a linear-Gaussian model; the Fisher information of that
model; whether a variance below the CRLB implies an error; and how to read a mean NEES of $3n$.

## How to study this stage

1. **Derive (1) on a blank page (40 min)** — three lines: Bayes, logarithm, quadratic form. If you
   can answer "why are the weights inverse covariances", every derivation in C5 becomes easier.
2. **See the CRLB through the Schur complement (70 min)** — steps 3 and 4 of the proof use the same
   tool as R3 of `r0-sparse-linear-algebra`. Noticing the same mathematics recurring in a different
   context makes it stick.
3. **Imprint the unbiasedness assumption with a counterexample (40 min)** — solve P6. You will see
   why "I broke the CRLB" is usually not a bug but an **assumption violation**.
4. **Run NEES yourself (80 min)** — do conditions 2 and 3 of the reproduction task together.
   Watching the metric respond when you deliberately misreport the covariance is the central
   experience of this lesson; the evaluations of C5 and S1 use it.
5. **Revisit rank deficiency from the estimation view (40 min)** — P1 produces "directions not
   determined by the observations". Confirm this is the same thing as the gauge of
   `c1-manifold-optimization`: linear algebra, optimization and estimation all point at one phenomenon.
6. **Read the textbooks hunting for the list of assumptions (110 min)** — in Thrun ch.2, find the
   **exact points** where the Markov and observation-independence assumptions are used in deriving
   the recursive filter. Those points are where things break in C5.

**Passing bar**: you can derive (1) and (2) on a blank page, can prove the CRLB and state its
assumptions, have code judging overconfidence by NEES that meets all four acceptance conditions,
and have notes on both textbook readings.
