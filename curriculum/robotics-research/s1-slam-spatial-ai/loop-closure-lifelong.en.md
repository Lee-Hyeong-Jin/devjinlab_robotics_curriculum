---
id: s1-loop-closure-lifelong
lang: en
title: Loop closure and lifelong operation
summary: >-
  Model the precision-recall trade-off of place recognition from the score distributions and derive
  that **recall collapses at fixed precision as the map grows**, confirming numerically that the
  threshold grows linearly in $\ln N$ (and that the commonly quoted $\sqrt{2\ln N}$ answers a
  different question). Measures that a single false loop inflates the ATE of a least-squares pose
  graph by a factor of 22, and sweeps the contamination rate to find where Huber and graduated
  non-convexity (GNC) give out. Ends with the fill-in that marginalisation creates in map
  sparsification, and why a sparse approximation is naturally **overconfident**, measured in KLD.
objectives:
  - Model the precision of place recognition from the score distributions and the database size, and derive the collapse of recall at fixed precision.
  - Derive and measure that the threshold holding precision fixed grows linearly in $\ln N$, and explain how that differs from $\sqrt{2\ln N}$.
  - Measure the destructive effect of a single false loop on a least-squares pose graph and explain it from the cost function.
  - Write the weight functions of Huber and GNC and locate numerically the contamination rate at which each gives out.
  - Measure the fill-in of marginalisation and quantify the KLD-versus-conservativeness trade-off of a sparse approximation.
tags: [slam, loop-closure, place-recognition, robust-estimation, sparsification, research]
---

# Loop closure and lifelong operation

## Setup and notation

The recommended prerequisites are `s1-vio-systems` in this module (marginalisation and
consistency), `c7-robust-fitting-ransac` (contamination and robust estimation) and
`c7-bundle-adjustment` (normal equations and the Schur complement). None of them is locked. The
lesson assumes:

- Probability: Gaussian tails, quantiles, precision and recall, the binomial distribution, KL
  divergence.
- Linear algebra: information matrices, the Schur complement, the positive-definite order
  ($A \preceq B$), the generalised eigenvalue problem.
- Optimisation: weighted least squares, M-estimators and influence functions, local minima of
  non-convex problems.
- Graphs: spanning trees and the sparsity of an adjacency matrix.

Notation:

| Symbol | Meaning |
|---|---|
| $N$ | size of the place database (the number of keyframes in the map) |
| $s$ | query-candidate similarity score; $s_t$ for a true match, $s_n$ for a non-match |
| $\tau$ | the loop acceptance threshold |
| $P$, $R$ | precision and recall |
| $\rho$ | false loop rate = (false loops)/(all loops) |
| $e_{ij}$ | the residual of a pose-graph edge; $\lVert e\rVert_\Sigma$ is the Mahalanobis norm |
| $w(e)$ | the weight of a robust kernel |
| $\delta$ | the transition point of the kernel (Huber); $\mu$ the non-convexity control of GNC |
| $\Lambda$ | the information matrix; $\Lambda_{\text{marg}}$ after marginalisation |
| $\Lambda_s$ | a sparse approximation; $\mathrm{KLD}$ is measured against $\Lambda_{\text{marg}}$ |

**Conventions**: the ATE is reported as a position RMSE in metres and the pose graph is planar,
$(x,y,\theta)$. Every "rate" is the **fraction of loops that are false**, not a fraction of all
edges — definitions differ between papers, so that is the first thing to check when comparing
numbers.

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (precision depends on the database size) [D2]** — with one true match per query and
  $N-1 \approx N$ non-matches whose scores are independent, at threshold $\tau$
  $$P(\tau) = \frac{R(\tau)}{R(\tau) + N\,\bar{F}_n(\tau)},
    \qquad R(\tau) = \bar{F}_t(\tau),\;\; \bar{F}(\tau) = 1 - F(\tau) \tag{1}$$
  so **precision falls in inverse proportion to the size of the database**.
- **R2 (collapse of recall at fixed precision) [D2]** — with $s_n \sim \mathcal{N}(0,1)$ and
  $s_t \sim \mathcal{N}(\mu_t,1)$, the threshold that holds a target precision $P^\star$ is
  $$\tau(N) \approx \frac{\ln N}{\mu_t} + \frac{\mu_t}{2} \tag{2}$$
  that is, **linear in $\ln N$** with slope $1/\mu_t$, while the recall
  $R = \bar\Phi(\tau - \mu_t)$ **collapses exponentially**. Growing the map from $10^2$ to $10^6$
  takes the recall at 99% precision from 0.55 to 0.0086. The commonly quoted $\sqrt{2\ln N}$ is the
  threshold that **bounds the number of false accepts at $O(1)$ without regard to recall**; for
  $\mu_t = 4$ and $N \le 10^6$ the two happen to be numerically close, which is why they get
  conflated.
- **R3 (the destructive power of one false loop) [D2]** — the cost of a least-squares pose graph is
  a sum of squared residuals, so the large residual of a single false loop **drags every pose**.
  Measured: adding **one** false loop to a graph with 12 true loops takes the ATE from
  $0.098$ to $2.18$ m (**a factor of 22**).
- **R4 (robust kernels and their limits) [D2]** — the Huber weight
  $w = \min(1, \delta/\lVert e\rVert)$ bounds the influence function, but the weight **never
  reaches zero**, so at a high contamination rate the estimate is still dragged (measured: ATE
  6.79 m at $\rho = 0.625$). GNC instead uses
  $$w = \left(\frac{\mu\delta^2}{\lVert e\rVert^2 + \mu\delta^2}\right)^{2} \tag{3}$$
  starting from a large $\mu$ and shrinking it, approaching the non-convex problem by **continuous
  deformation** from a convex one — measured: ATE 0.098 m even at $\rho = 0.625$, the same as with
  no contamination.
- **R5 (why sparsification becomes overconfident) [D2]** — marginalising old nodes makes the Schur
  complement create **fill-in**, densifying the graph (measured: block density
  $0.056 \to 0.139$). When that dense marginal information is replaced by a sparse approximation,
  the naive approach of **keeping selected entries** almost always gives
  $\Lambda_{\text{marg}} - \Lambda_s \not\succeq 0$, so it **overstates the information** in some
  directions. Making it conservative means shaving information off, and the price is measured in
  KLD (measured: the tree approximation goes from KLD 0.267 to 9.88, about 37 times).

## Derivation

### R1 and R2 — why loop closure gets harder as the map grows

Place recognition compares a query image against the $N$ places of a database, produces a similarity
score, and proposes a loop when the score exceeds a threshold $\tau$. Take one true match per query
and $N-1$ non-matches (in reality several consecutive frames are correct, but one is the
conservative choice).

**Precision.** The probability of accepting the true match is $R(\tau) = \Pr[s_t > \tau]$, and the
probability of wrongly accepting one non-match is $\bar{F}_n(\tau) = \Pr[s_n > \tau]$. If the
non-matches are independent the expected number of false accepts is $N\bar{F}_n(\tau)$, which gives
(1). The point is the $N$ in the denominator — **at a fixed threshold, false loops grow linearly
with the size of the map.**

**Growth of the threshold.** With non-match scores $\mathcal{N}(0,1)$, Mills' ratio gives
$\bar\Phi(\tau) \approx \phi(\tau)/\tau$, and holding a target precision $P^\star$ requires
$N\bar\Phi(\tau) \le c\,\bar\Phi(\tau-\mu_t)$ with $c = (1-P^\star)/P^\star$. Taking logarithms and
using Mills' ratio,

$$\ln N - \frac{\tau^2}{2} - \ln\tau
  \;\le\; -\frac{(\tau-\mu_t)^2}{2} - \ln(\tau-\mu_t) + \ln c$$

and since $(\tau-\mu_t)^2/2 = \tau^2/2 - \mu_t\tau + \mu_t^2/2$, **the $\tau^2/2$ cancels on both
sides**. What remains is

$$\ln N \;\lesssim\; \mu_t\tau - \frac{\mu_t^2}{2} + O(\ln\tau)
  \;\Longrightarrow\;
  \tau(N) \approx \frac{\ln N}{\mu_t} + \frac{\mu_t}{2} \tag{2}$$

which is (2) — **the threshold is linear in $\ln N$** with slope $1/\mu_t$, so **the better the
separation between true-match and non-match scores, the less sensitive the system is to map
growth**. The recall is $R = \bar\Phi(\tau-\mu_t)$, so the linear growth of the threshold
translates into a **Gaussian-tail decay** of recall.

That one cancellation of $\tau^2/2$ matters. Miss it, look only at the left-hand side, and you get
$\tau \approx \sqrt{2\ln N}$ — which is the answer to the condition
$N\bar\Phi(\tau) = O(1)$, bounding the expected number of false accepts **without any regard for
recall**. The two expressions answer different questions, and as the table below shows they are
numerically close for $\mu_t = 4$ and $N \le 10^6$, which is why the literature and the folklore mix
them up.

Measured ($s_t \sim \mathcal{N}(4,1)$, $s_n \sim \mathcal{N}(0,1)$, solving (1) by bisection for the
threshold at each target precision):

| $N$ | $\tau(P{=}0.99)$ | recall | $\tau(P{=}0.90)$ | recall | prediction (2) $\frac{\ln N}{\mu_t}+\frac{\mu_t}{2}$ | $\sqrt{2\ln N}$ |
|---|---|---|---|---|---|---|
| $10^2$ | 3.863 | 0.5545 | 3.121 | 0.8102 | 3.151 | 3.035 |
| $10^3$ | 4.524 | 0.3001 | 3.835 | 0.5656 | 3.727 | 3.717 |
| $10^4$ | 5.158 | 0.1234 | 4.497 | 0.3094 | 4.303 | 4.292 |
| $10^5$ | 5.776 | 0.0379 | 5.132 | 0.1287 | 4.878 | 4.799 |
| $10^6$ | 6.383 | 0.0086 | 5.751 | 0.0400 | 5.454 | 5.257 |

How to read it. (1) **The threshold grows linearly in $\ln N$.** The increment per decade is
$0.661, 0.634, 0.618, 0.607$ in the measurements against a predicted slope of
$\ln 10/\mu_t = 0.576$ — the slope matches and the intercept is about 0.9 higher (from the
$O(\ln\tau)$ correction and the $c$ term). The $\sqrt{2\ln N}$ column looks similar, but it is a
function whose increment per decade **shrinks**; push $N$ to $10^9$ and the two predictions part
company (linear $7.2$ against square-root $6.4$). (2) **At 99% precision the recall falls from 0.55
to 0.0086, a factor of 64.** (3) Lowering the precision target to 90% recovers four to five times
the recall, but as R3 will show **lowering precision is the most expensive choice available**. Monte
Carlo check ($N = 10^4$, $\tau = 6.1$, 20,000 queries): precision 1.0000 (model 0.9997), recall
0.0174 (model 0.0179).

**Where the assumptions break**: (1) the **independence** of non-match scores. Real places resemble
each other (corridors, trees, repeated structure) and the scores are correlated, so false accepts
arrive in clusters — (1) is optimistic. (2) The assumption of a single true match: consecutive
frames give several, so the recall is underestimated. (3) The score distribution **differs between
scenes**, so the same $\tau$ gives different precision indoors and outdoors. That is why DBoW2-style
systems normalise the score by the previous frame's score (a relative score) and chain a temporal
consistency check and a geometric verification **in series** — each stage multiplies $\bar{F}_n$
down and so offsets the $N$ term of (1).

### R3 — what one false loop does

Pose graph optimisation solves

$$\min_{x} \sum_{(i,j)\in\mathcal{E}} \big\lVert e_{ij}(x) \big\rVert^2_{\Sigma_{ij}},
  \qquad e_{ij} = \log\big(T_{ij}^{-1}\,T_i^{-1}T_j\big)$$

Because the cost is **quadratic**, the influence of an edge grows linearly with its residual (the
influence function $\psi(e) = e$ is unbounded). A false loop asserts that two completely different
poses are the same, so its residual is metres in size, and the optimum **folds the whole trajectory**
to reduce it.

Measured (a planar circular trajectory of 60 poses, odometry
$\sigma = (0.02, 0.02, 0.005)$, 12 true loops with $\sigma = (0.05, 0.05, 0.01)$, false loops whose
relative pose is drawn uniformly from $[-6,6]^2 \times [-\pi,\pi]$, median over three seeds):

| false loops | $\rho$ | ATE least squares | ATE Huber ($\delta=2$) | ATE GNC ($\delta=2$) |
|---|---|---|---|---|
| 0 | 0.000 | 0.0976 | 0.0963 | 0.0975 |
| 1 | 0.077 | **2.1837** | 0.1012 | 0.0975 |
| 2 | 0.143 | 3.2399 | 0.0965 | 0.0975 |
| 5 | 0.294 | 5.2646 | 0.1513 | 0.0976 |
| 10 | 0.455 | 6.8092 | 0.3775 | 0.0976 |
| 20 | 0.625 | 9.9040 | **6.7916** | 0.0982 |

**One false loop takes the ATE from 0.098 m to 2.18 m, a factor of 22.** That is the basis for R2's
"lowering precision is the most expensive choice" — buying a few percent of recall by dropping
precision from 99% to 90% produces a hundred false loops in a thousand queries, and a least-squares
back end is finished.

### R4 — robust kernels: how far do they hold?

**Huber.** For a residual norm $u = \lVert e\rVert_\Sigma$, with cost
$\rho_\delta(u) = \tfrac12u^2$ for $u \le \delta$ and $\delta(u - \tfrac12\delta)$ for $u > \delta$,
the iteratively reweighted least squares weight is

$$w_{\text{Huber}}(u) = \min\!\left(1, \frac{\delta}{u}\right) \tag{4}$$

The influence function is bounded by $\delta$, so there is **a cap on how hard one edge can pull**.
But the weight **never becomes zero** — an edge with a 100 m residual keeps pulling with force
$w = \delta/100 > 0$. As false loops accumulate, those small forces add up and eventually win.
Measured: it holds at ATE 0.38 m up to $\rho = 0.455$ and collapses to 6.79 m at $0.625$.

**GNC (graduated non-convexity).** The goal is a **redescending** kernel of the Geman–McClure type —
the weight goes to zero for large residuals — but that cost is non-convex and traps local minima.
GNC introduces a control $\mu$ to build a family that is **convex** as $\mu \to \infty$ (identical to
least squares) and equals the target kernel as $\mu \to 1$, then starts with a large $\mu$ and
shrinks it, converging at each step. The weight is (3): for large $\mu$, $w \to 1$ (all edges
equal), and as $\mu$ shrinks the weight of a large residual goes to **zero** as
$\mathcal{O}(\mu^2/u^4)$.

That continuous deformation is the key. Starting from the solution of a convex problem and dragging
it gradually into the non-convex one avoids the local minima you fall into by starting with the
redescending kernel directly. Measured: at $\rho = 0.625$ the ATE is 0.0982 m — **indistinguishable
from the uncontaminated 0.0976**.

**Where the assumptions break**: (1) GNC breaks too as $\rho \to 1$. Once the false loops are a
**majority**, the "consistent majority" is the false one and any robust estimator picks it (the same
wall as the unidentifiability of `c7-robust-fitting-ransac` R4). (2) When the false loops are
**structurally consistent** — those arising from repeated structure, such as two identical corridors
— they do not contradict each other and a robust kernel cannot filter them out. That is the real
failure mode of lifelong operation. (3) $\delta$ has to come from the noise scale (the $\chi^2$
quantile of `c7-robust-fitting-ransac` R3). A wrong $\delta$ either discards true loops or accepts
false ones. (4) Switch variables (Sünderhauf–Protzel) do the same job with an extra variable per
edge, where the strength of the prior plays the role of $\delta$.

### R5 — map sparsification: fill-in and overconfidence

Lifelong operation cannot grow the graph forever. **Marginalising** old nodes
(`s1-vio-systems` R1) makes the Schur complement create **new edges** among the remaining nodes —
every node that observed the marginalised node together becomes connected (fill-in).

Measured (a 60-pose graph with odometry plus 12 loops, marginalising the first 20 poses):

| | non-zero blocks | block density |
|---|---|---|
| before marginalisation (60 nodes) | 202 / 3600 | 0.0561 |
| after marginalisation (40 nodes) | 222 / 1600 | **0.1388** |

A third of the nodes are gone and the **density is 2.5 times higher**. Left alone, the graph becomes
dense and the benefit of sparsity disappears, so the dense $\Lambda_{\text{marg}}$ is **approximated
by a sparse $\Lambda_s$**. The quality of the approximation is measured by the KL divergence, which
between two zero-mean Gaussians is

$$\mathrm{KLD}\big(\mathcal{N}(0,\Lambda_{\text{marg}}^{-1}) \,\big\|\,
  \mathcal{N}(0,\Lambda_s^{-1})\big)
  = \tfrac12\Big(\operatorname{tr}\big(\Lambda_s\Lambda_{\text{marg}}^{-1}\big) - n
  + \ln\det\Lambda_{\text{marg}} - \ln\det\Lambda_s\Big) \tag{5}$$

Three naive sparsifications were compared, all of them **keeping selected entries** of
$\Lambda_{\text{marg}}$:

| Approximation | blocks (density) | KLD | $\lambda_{\min}(\Lambda_{\text{marg}} - \Lambda_s)$ | Verdict |
|---|---|---|---|---|
| dense marginal (reference) | 222 (0.139) | 0 | 0 | — |
| maximum spanning tree | 118 (0.074) | 0.267 | $-5.0\times10^{2}$ | **overconfident** |
| chain only | 118 (0.074) | 0.267 | $-5.0\times10^{2}$ | **overconfident** |
| block diagonal | 40 (0.025) | 623.5 | $-8.8\times10^{3}$ | **overconfident** |

**All three are overconfident.** That $\Lambda_{\text{marg}} - \Lambda_s$ is not positive
semi-definite means that in some direction **the approximation claims more information than the
original**, and a downstream module then believes a map whose uncertainty is understated there. It
feels as though dropping entries should remove information, but dropping off-diagonal entries of an
information matrix is **erasing a correlation**, and that *reduces* the conditional variance.

Making it conservative requires shaving information off. Scaling by the largest $\alpha$ with
$\alpha\Lambda_s \preceq \Lambda_{\text{marg}}$ (from the generalised eigenvalue problem
$\Lambda_s v = \lambda\Lambda_{\text{marg}}v$, so $\alpha = 1/\lambda_{\max}$):

| Approximation | $\alpha$ | KLD after | Verdict |
|---|---|---|---|
| maximum spanning tree | 0.5300 | 9.88 (**37 times** the original 0.267) | conservative |
| block diagonal | 0.0020 | 279.6 | conservative |

**The price of conservativeness is stated explicitly in KLD.** This is the problem the literature on
*consistent sparsification* solves — minimise the KLD subject to
$\Lambda_s \preceq \Lambda_{\text{marg}}$ as a **constraint**, with the sparsity pattern fixed, which
makes it convex. Naive entry selection simply ignores that constraint.

**Where the assumptions break**: (1) (5) compares two distributions **at the same linearisation
point**. If the state moves substantially after sparsification the comparison loses meaning.
(2) Fixing the sparsity pattern to a tree is arbitrary — which pattern minimises the KLD is a
combinatorial problem. (3) Repeating a conservative approximation makes the information decrease
**monotonically**, so after thousands of sparsifications the map can become uselessly loose. There is
no theory for "how often and how much" in lifelong operation (open problem 3).

## Proof sketch

### R2 — the fixed-precision threshold grows linearly in $\ln N$

**Hypotheses** H1: one true match and $N$ non-matches per query, with mutually independent scores.
H2: $s_n \sim \mathcal{N}(0,1)$ and $s_t \sim \mathcal{N}(\mu_t, 1)$ with $\mu_t > 0$ fixed.
H3: a fixed target precision $P^\star \in (0,1)$.
**Conclusions** C1: (1) holds. C2: the smallest $\tau$ with $P(\tau) \ge P^\star$ satisfies
$\tau(N) \approx \ln N/\mu_t + \mu_t/2$. C3: the recall is then
$R = \bar\Phi(\tau - \mu_t) \to 0$, decaying like
$(\ln N)^{-1/2}$ times a Gaussian tail.

**Strategy**: Mills' ratio $\bar\Phi(\tau) \sim \phi(\tau)/\tau$ plus a comparison of logarithms.

1. **C1**: precision is the fraction of accepted items that are true. The expected number of true
   accepts is $R(\tau)$ and, by linearity, the expected number of false accepts is
   $N\bar{F}_n(\tau)$ (the independence of H1 is **not needed for the expectation** but is needed for
   the variance and the clustering behaviour). The ratio is (1). $\square$
2. **C2**: $P(\tau) \ge P^\star \iff N\bar\Phi(\tau) \le c\,\bar\Phi(\tau-\mu_t)$ with
   $c = (1-P^\star)/P^\star$. Taking logarithms and using Mills' ratio
   $\bar\Phi(x) \approx \phi(x)/x$,
   $\ln N - \tfrac{\tau^2}{2} - \ln\tau \le -\tfrac{(\tau-\mu_t)^2}{2} - \ln(\tau-\mu_t) + \ln c$,
   and the $\tau^2/2$ **cancels**, leaving
   $\ln N \le \mu_t\tau - \tfrac{\mu_t^2}{2} + O(\ln\tau)$ — that is,
   $\tau(N) \approx \ln N/\mu_t + \mu_t/2$, **linear in $\ln N$**. The measured increments per
   decade, $0.607$ to $0.661$, match the predicted slope $\ln10/\mu_t = 0.576$. $\square$
   (By contrast, missing the cancellation of $\tau^2/2$ and solving only
   $N\bar\Phi(\tau) = O(1)$ gives $\tau \approx \sqrt{2\ln N}$ — the answer to a different
   question, one that **ignores recall** and only bounds the number of false accepts.)
3. **C3**: substitute the $\tau$ of C2 into $R = \bar\Phi(\tau-\mu_t)$ and use Mills' ratio.
   $\square$
4. **What prevents this collapse**: only reducing the denominator of (1). (1) Chain a geometric
   verification in series to multiply $\bar{F}_n$ down (DBoW2's temporal consistency plus a RANSAC
   verification). (2) Restrict the candidates spatially to **reduce the effective $N$** (only
   candidates inside the current position uncertainty). (3) Make the back end robust so that lower
   precision is survivable (R4). Modern systems use all three.
5. **Remove a hypothesis**: if the independence of H1 fails (repeated structure), false accepts
   arrive in clusters; the expectation is unchanged but **several are accepted at once in one
   query**, so the shock to the back end is larger. Replacing the Gaussian of H2 with a heavier tail
   makes $\tau$ grow faster than (2) and the recall collapse sooner — real score distributions have
   heavier tails than a Gaussian.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R1·R2)** Derive (1) and write the number of false accepts allowed at a target
precision $P^\star$ in terms of $R$ and $P^\star$. Then derive (2), compute how much $\tau$ must rise
when $N$ grows by a factor of ten, and say why the $\sqrt{2\ln N}$ approximation underestimates it.
*Solution sketch*: the allowed number of false accepts is $R(1-P^\star)/P^\star$. From (2), a factor
of ten in $N$ gives $\Delta\tau \approx \ln10/\mu_t = 0.576$, and in the measured table $10^4 \to
10^5$ gives $5.158 \to 5.776$, about $+0.62$. Predicting with $\sqrt{2\ln N}$ gives $+0.51$, an
underestimate.

**P2 (proof, ★★★, R5)** Derive (5), and show why **zeroing one off-diagonal block** of an
information matrix *reduces* the variance in that direction (that is, is overconfident). Build a
counterexample with $2\times2$ blocks, and argue that minimising the KLD subject to
$\Lambda_s \preceq \Lambda$ is a convex problem.
*Strategy and key inequality*: from $\Sigma = \Lambda^{-1}$,
$\Sigma_{11} = (\Lambda_{11} - \Lambda_{12}\Lambda_{22}^{-1}\Lambda_{21})^{-1}$, so
$\Lambda_{12} \to 0$ **increases** the bracket and therefore shrinks $\Sigma_{11}$. The KLD is of the
form $-\ln\det\Lambda_s + \operatorname{tr}(\Lambda_s\Sigma)$ in $\Lambda_s$, and both terms are
convex (the first is minus a log determinant), so with the linear constraint
$\Lambda_s \preceq \Lambda$ and a fixed sparsity pattern the problem is convex.

**P3 (numerical, ★, R2)** With $s_t \sim \mathcal{N}(4,1)$ and $s_n \sim \mathcal{N}(0,1)$, compute
for $N = 10^3$ and $10^5$ (a) the $\tau$ and recall at $P = 0.99$, (b) the same at $P = 0.90$, and
(c) the ratio of recalls between $10^3$ and $10^5$.
*Answer*: (a) $N{=}10^3$: $\tau = 4.524$, $R = 0.3001$; $N{=}10^5$: $\tau = 5.776$, $R = 0.0379$;
(b) $3.835, 0.5656$ and $5.132, 0.1287$; (c) $0.3001/0.0379 = 7.9$ (at 99%) and $4.4$ (at 90%).
Tolerance $10^{-3}$. Check: put $\tau$ back into (1) and confirm the precision matches the target to
within $10^{-4}$.

**P4 (derivation, ★★, R4)** Derive (4) and (3) from their cost functions (the IRLS weight is
$w(u) = \rho'(u)/u$). Show that the GNC weight tends to 1 as $\mu \to \infty$ and to 0 as
$\mu \to 0$, and find the order of its decay at large residuals.
*Solution sketch*: for Huber, $\rho'(u) = \min(u, \delta)$ gives (4). For GNC (the Geman–McClure
family), differentiating $\rho_\mu(u) = \frac{\mu\delta^2u^2}{\mu\delta^2+u^2}$ gives (3). At large
$u$, $w \sim (\mu\delta^2)^2/u^4$ — decaying with the **fourth** power.

**P5 (numerical, ★★, R5)** Build a 60-pose pose graph and compute (a) the block density before and
after marginalisation, (b) the KLD and
$\lambda_{\min}(\Lambda_{\text{marg}}-\Lambda_s)$ of the spanning-tree approximation, and (c) the
conservativeness factor $\alpha$ and the KLD it produces.
*Answer (reference measurements)*: (a) $0.0561 \to 0.1388$; (b) KLD 0.267 with
$\lambda_{\min} = -5.0\times10^2$ (overconfident); (c) $\alpha = 0.5300$ with KLD 9.88. Tolerance:
the density within ±20%, the KLD to the right order of magnitude, and the **sign** of
$\lambda_{\min}$ must be negative (that is the point). Check: having obtained $\alpha$ from the
generalised eigenvalue problem, confirm that
$\lambda_{\min}(\Lambda_{\text{marg}}-\alpha\Lambda_s)$ is $+0$.

**P6 (implementation, ★★★, R3·R4)** Implement planar pose graph optimisation and measure the ATE
against the false loop rate for three back ends: least squares, Huber and GNC.
*Rubric*: (a) all three use the **same graph and the same initial guess**; (b) the first pose is
fixed to remove the gauge; (c) angle wrapping is handled; (d) you show the least-squares ATE growing
by at least a factor of 20 from a single false loop; (e) you report GNC's $\mu$ schedule and
iteration count.

**P7 (counterexample, ★★, R4)** Construct false loop configurations on which GNC also fails: (a) one
where the false loops are a majority and (b) one where the false loops are **mutually consistent** (a
model of repeated structure). Report the ATE and the final weight distribution GNC settles on in each
case.
*Property checklist*: (a) GNC's ATE grows at $\rho > 0.7$; (b) with a consistent set of false loops
GNC selects them as "true" even at small $\rho$; (c) check whether the surviving weights polarise to
0 and 1; (d) a paragraph arguing that this failure is **unidentifiability**, not an algorithmic
defect (connecting to `c7-robust-fitting-ransac` R4).

**P8 (paper, ★★, R1·R2)** Read §III–V of Gálvez-López & Tardós 2012 and §IV and §VI of Cadena et al.
2016, and (a) list every device DBoW2 uses to reduce the denominator of (1), saying how each reduces
$\bar{F}_n$; (b) check whether the precision-recall curves the paper reports are given against
**database size** (or only at a fixed $N$); and (c) find the item in the survey's open problems that
connects directly to the sparsification of R5.
*Rubric*: for (a), naming three or more of relative score normalisation, temporal consistency,
geometric verification and the direct index passes. For (b), establishing that they are reported only
at a fixed $N$ is excellent — it is why R2's collapse is invisible in the paper.

## Paper reading

**Two must-reads.** Write a one-page note on each, using the ten fixed questions
(`lesson-standard.md` §5). Read in three passes, and attack questions 4, 5, 6 and 7 in the third.
For the full bibliography, including the recommended papers, run
`rc papers s1-loop-closure-lifelong`.

1. **Gálvez-López & Tardós, "Bags of binary words for fast place recognition in image sequences"
   (2012, IEEE T-RO)** — role: `seminal`.
   <https://doi.org/10.1109/TRO.2012.2197158> (§III–V is the core.)
   Extra questions: (a) which term of (1) do the branching factor and depth of the vocabulary tree
   affect? (b) How much recall does the temporal consistency check cost — does the paper report that
   separately? (c) How does the direct index reduce the cost of geometric verification?
2. **Cadena, Carlone, Carrillo et al., "Past, present, and future of SLAM: towards the
   robust-perception age" (2016, IEEE T-RO)** — role: `survey`.
   <https://arxiv.org/abs/1606.05830> (§IV on robustness, §VI on lifelong operation.)
   Extra questions: (a) map the four requirements the survey gives for the "robust perception age"
   onto R3, R4 and R5 of this lesson. (b) Which of the open problems listed in 2016 are settled as of
   2026? (c) Does the section on sparsification mention the **conservativeness** problem?

**The ten fixed questions**: (1) which problem under which assumptions; (2) what exactly earlier
work could not do; (3) the core idea in one equation; (4) what is guaranteed and **what is not**;
(5) the independent and dependent variables and the baselines, fairly tuned or not; (6) whether the
metric matches the claim, and whether variance and seeds are reported; (7) what is missing for
reproduction; (8) the first assumption to doubt if the result were wrong; (9) time and memory
complexity and real-time behaviour; (10) what you would change to go beyond it in a year.

**Recommended**: Sünderhauf & Protzel 2012 (switch variables), Yang et al. 2020 §III (the
formulation of GNC), Barfoot ch.5.

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 10 minutes in total, numpy and
scipy only. The input is a generator this lesson specifies; no external data is needed.

> **Relation to the blueprint**: the reproduction task in the design is "inject a rate of false
> loops, find the point at which the ATE collapses, and show that a robust kernel mitigates it"
> (tier R3). This task does **exactly** that, with the input taken from a pose graph this lesson
> specifies rather than a public dataset, so that it finishes inside ten CPU minutes — and since the
> contamination rate must be **controlled** to find the collapse point, a synthetic graph actually
> serves the purpose better. Reproducing it on a public pose graph (sphere, city10000) is the
> optional extension below.

**Generators (fixed)**: (a) the score model — $s_t \sim \mathcal{N}(4,1)$,
$s_n \sim \mathcal{N}(0,1)$, $N \in \{10^2,\dots,10^6\}$. (b) The pose graph — a circular trajectory
of radius 8 m with 60 poses, odometry noise $\sigma = (0.02, 0.02, 0.005)$, 12 true loops
($\sigma = (0.05,0.05,0.01)$, first third against last third), false loops with relative poses drawn
uniformly from $[-6,6]^2\times[-\pi,\pi]$, a false loop count in $\{0,1,2,5,10,20\}$, and three
seeds. (c) Sparsification — marginalising the first 20 poses of the same graph's information matrix.
Report with a fixed seed.

All **four conditions** must hold to pass. Every reference value was measured for this lesson.

1. **The precision-recall law**: with generator (a), solve (1) by bisection and tabulate the
   threshold and recall at $P = 0.99$ and $0.90$ against $N$, showing that (a) the recall
   **decreases monotonically** with $N$; (b) the recall at 99% precision falls by **a factor of at
   least 50** from $N = 10^2$ to $10^6$; and (c) the increment of the threshold per decade is of the
   same order as the slope $\ln10/\mu_t$ of (2) (reference: recall
   $0.5545 \to 0.0086$, a factor of 64; $\tau$ $3.863 \to 6.383$ with per-decade increments
   $0.661/0.634/0.618/0.607$ against a prediction of $0.576$). Confirm the precision and recall of
   (1) by Monte Carlo to within $\pm0.005$.
2. **The destructive power of one false loop**: with generator (b), adding **one** false loop makes
   the least-squares back end's ATE at least **20 times** the uncontaminated value (reference:
   $0.0976 \to 2.1837$, a factor of 22).
3. **Where the robust back ends give out**: on the same generator, measure the ATE of
   Huber ($\delta = 2$) and GNC ($\delta = 2$) against the false loop count, showing that (a) Huber
   stays below 0.5 m up to $\rho \le 0.455$ and **collapses above 1 m** at $\rho = 0.625$, and
   (b) GNC stays within **1.1 times** the uncontaminated ATE even at $\rho = 0.625$ (reference:
   Huber $0.3775 \to 6.7916$, GNC $0.0976 \to 0.0982$).
4. **The overconfidence of sparsification**: with generator (c), (a) marginalisation at least
   **doubles** the block density; (b) the spanning-tree and block-diagonal approximations have a
   **negative** $\lambda_{\min}(\Lambda_{\text{marg}} - \Lambda_s)$; and (c) scaling by a
   conservativeness factor $\alpha < 1$ makes the KLD at least **ten times** larger (reference:
   density $0.0561 \to 0.1388$, $\lambda_{\min} = -5.0\times10^2$ and $-8.8\times10^3$, tree KLD
   $0.267 \to 9.88$ at a factor of 37 with $\alpha = 0.53$).

**Optional extension (R3, public data)**: download `sphere` or `city10000` from Carlone's public
pose graph collection and repeat the same experiment. Inject false loops at a rate and compare the
ATE of the three back ends; since a public graph may have no ground-truth trajectory, take **the
uncontaminated optimum as the reference** and say so in the report.

**State this in the report**: (1) the conclusion from reading conditions 1 and 2 together — "buying
recall by lowering precision is the most expensive choice available to a least-squares back end";
(2) what the sign of $\lambda_{\min}$ in condition 4 means (overconfidence); (3) GNC's $\mu$
schedule and iteration count (without them it does not reproduce).

**Baselines**: (1) the analytic expression (1) (condition 1); (2) the three back ends against each
other (conditions 2 and 3); (3) the dense marginal information (condition 4); (4) optionally GTSAM's
`noiseModel::Robust` and its GNC implementation.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| one false loop does not raise the ATE | the false loop's relative pose happens to be close to the true one | print the residual norm of the false loop (it should be metres) |
| Huber raises the ATE even without contamination | $\delta$ is below the noise scale and is shaving true edges | reset $\delta$ from the $\chi^2$ quantile |
| GNC gives the same answer as least squares | $\mu$ was never shrunk (still in the convex regime) | log the trajectory of $\mu$ |
| GNC diverges | $\mu$ was shrunk too fast | use a reduction ratio of 2 to 4 and converge at each $\mu$ |
| the optimisation drifts along the gauge | the first pose was not fixed | check the weight of the anchor term |
| the KLD comes out negative | a sign or the order of the $\log\det$ terms in (5) is wrong | check that KLD = 0 at $\Lambda_s = \Lambda_{\text{marg}}$ |
| $\lambda_{\min}$ comes out positive (no overconfidence) | the whole matrix was scaled instead of zeroing off-diagonals | confirm that the blocks outside the tree were set to **zero** |

## Open problems

- **(open problem) structurally consistent false loops** — the measurements of R4 show GNC is
  almost perfect when the false loops **contradict each other**. But false loops arising from
  repeated structure (identical corridors, car parks, orchards) are mutually consistent and no robust
  kernel can filter them. Current approaches:
  [switchable constraints](https://doi.org/10.1109/IROS.2012.6385590),
  [GNC](https://arxiv.org/abs/1909.08605), and multi-hypothesis tracking. What is missing: a
  principled criterion that separates a "consistent minority hypothesis". It is the same wall as the
  unidentifiability of `c7-robust-fitting-ransac`.
- **(open problem) preserving recall as the database grows** — R2 shows recall collapsing with $N$
  at fixed precision. Reducing the effective $N$ by geometric verification and spatial restriction
  is the present answer, but there is no method that keeps recall constant at **decade scale**
  (millions of places). Current approaches: hierarchical vocabularies
  ([DBoW2](https://doi.org/10.1109/TRO.2012.2197158)), learned global descriptors, and restricting
  candidates with a position prior. What is missing: retrieval whose cost grows only
  logarithmically in $N$ while holding recall.
- **(open problem) consistent and repeatable sparsification** — R5 shows naive sparsification is
  overconfident and that conservativeness is expensive in KLD. Choosing the sparsity pattern is a
  combinatorial problem, and there is no bound on how much information drains away after thousands of
  conservative sparsifications. Current approaches: the convex formulation of KLD minimisation under
  a positive-definite constraint, and Chow–Liu-style tree approximations. What is missing: a bound on
  the information loss of repeated sparsification and a schedule matched to it.
- **(open problem) co-designing loop-closure acceptance and the back end** — today the front end
  picks a threshold targeting precision and the back end copes with whatever contamination is left.
  There is no model predicting the **joint optimum** of the two stages (at which precision, with
  which robust kernel, is the overall ATE minimal). Current approach: empirical tuning. What is
  missing: a framework that ties R2's PR curve and the ATE curves of R3 and R4 into one design
  problem.

## Concept check

Run `rc quiz s1-loop-closure-lifelong`. The quiz is for **concept checking only**; the real work is
the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: what happens at a fixed threshold as the place database grows; the factor by
which a single false loop inflates the least-squares ATE; why Huber is eventually dragged at high
contamination; whether zeroing off-diagonal blocks of an information matrix is conservative; and what
marginalisation does to the structure of the graph.

## How to study this stage

1. **Write the precision expression first (40 min)** — derive (1) and note that $N$ sits in the
   denominator. Then do the logarithmic comparison of (2) by hand. Working out, in step 2 of the
   proof sketch, *which* condition the commonly quoted $\sqrt{2\ln N}$ actually answers is the heart
   of this section.
2. **Build the PR table yourself (40 min)** — solve (1) by bisection and sweep $N$ (condition 1).
   Only after seeing the recall drop by a factor of 64 in numbers does the next section's "do not
   lower precision" carry weight.
3. **Insert a single false loop (60 min)** — implement the pose graph and reproduce the factor of 22
   from one false loop (condition 2). Plotting the trajectory makes the folding visible.
4. **Derive the kernels before using them (60 min)** — derive (4) and (3) from their cost functions
   (P4) and implement them with IRLS. Compare, in one table, the point where Huber gives out with
   GNC holding (condition 3).
5. **Break GNC on purpose (40 min)** — never shrink $\mu$, or shrink it too fast, and watch it become
   least squares or diverge respectively. Why the continuous deformation is needed becomes clear here.
6. **Measure the overconfidence of sparsification (80 min)** — measure the marginalisation fill-in
   (condition 4(a)), then the KLD and the sign of $\lambda_{\min}$ of the tree approximation (4(b)).
   Obtain the conservativeness $\alpha$ from the generalised eigenvalue problem and confirm the KLD
   growing by a factor of 37 (4(c)). The point is to verify by hand that the intuition "dropping
   information is conservative" is wrong (P2).
7. **Two papers and the notes (130 min)** — read DBoW2 §III–V as a list of devices for reducing the
   denominator of (1), and map the survey's §IV and §VI onto R3, R4 and R5. Write the one-page note
   per paper **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the open problems and write a paragraph on
   why it is still open. Structurally consistent false loops are a question you can design an
   experiment for immediately.

**Passing bar**: you can derive (1) and (2) on a blank page, you have reproduced the factor-of-22
effect of one false loop, you can write the weight functions of Huber and GNC and state where each
gives out, you can explain through the $\Sigma_{11}$ expression why sparsification becomes
overconfident, and you have notes on both papers.
