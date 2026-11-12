---
id: c5-robust-global-estimation
lang: en
title: Robust estimation and global optimality
summary: >-
  Prove that the stationarity condition of an M-estimator is the normal equations of iteratively
  reweighted least squares, and use the influence function to separate bounded from redescending
  kernels. Prove in four lines that for SO(2) rotation synchronization a positive semidefinite dual
  certificate matrix S = Lambda - C makes the solution globally optimal (SE-Sync in miniature), and
  confirm numerically that its tightness breaks once outliers appear. Measure both the 26-fold ATE
  improvement robust estimation gives on a pose graph with 20% outliers and its limits.
objectives:
  - Derive the IRLS weight w = psi(r)/r from the stationarity condition of an M-estimator.
  - Separate bounded from redescending kernels by their influence function and explain how each fails.
  - Prove the global optimality certificate for SO(2) rotation synchronization with no missing steps.
  - Characterize numerically the conditions (outliers, noise) under which the certificate breaks.
  - Show with numbers why GNC is not a guarantee and what a redescending kernel costs.
  - Explain why TEASER's invariant-measurement decomposition splits the problem.
tags: [state-estimation, robust-estimation, m-estimator, irls, se-sync, teaser, certification, research]
---

# Robust estimation and global optimality

## Setup and notation

The MAP and least-squares notation of `c5-factor-graphs-map` and the consistency discussion of
`c5-observability-consistency` carry over. R1 of `c5-factor-graphs-map` — "least squares is another
name for the Gaussian assumption" — is the starting point here, because an outlier is precisely
something that is not Gaussian. Additional symbols:

| Symbol | Meaning |
|---|---|
| $\rho : [0,\infty) \to [0,\infty)$ | the **loss function (kernel)**, with $\rho(0)=0$ and increasing. The squared loss is $\rho(r) = \tfrac12 r^2$ |
| $\psi := \rho'$ | the **influence function** — how much one measurement moves the solution |
| $w(r) := \psi(r)/r$ | the **IRLS weight** |
| $c$ | the kernel parameter (threshold), measured in whitened residual units |
| $\epsilon^\ast$ | the **breakdown point** — the outlier fraction at which the estimator starts to fail |
| $\mu$ | the convexity parameter of GNC. $\mu\to\infty$ is convex, $\mu\to 0$ is the original kernel |
| $x \in \mathbb{C}^n$, $\lvert x_k\rvert = 1$ | the complex representation of an $SO(2)$ rotation, $x_k = e^{i\theta_k}$ |
| $C$ | the synchronization data matrix, $C_{ij} = e^{-i\bar\theta_{ij}}$ (Hermitian) |
| $\Lambda$, $S := \Lambda - C$ | the dual variable (real diagonal) and the **certificate matrix** |

**The main kernels** (in terms of the whitened residual norm $r = \lVert r_k\rVert$):

| Kernel | $\rho(r)$ | $\psi(r)$ | $w(r)$ | Influence |
|---|---|---|---|---|
| squared (L2) | $\tfrac12 r^2$ | $r$ | $1$ | **unbounded** — one outlier drags the solution |
| Huber | $r\le c$: $\tfrac12 r^2$ / $r>c$: $c r - \tfrac12 c^2$ | $\min(r, c)$ | $\min(1, c/r)$ | **bounded**, but not zero |
| Cauchy | $\tfrac{c^2}{2}\log(1 + r^2/c^2)$ | $\dfrac{r}{1+r^2/c^2}$ | $\dfrac{1}{1+r^2/c^2}$ | **redescending** ($\psi\to0$ as $r\to\infty$) |
| TLS (truncated) | $r\le c$: $\tfrac12 r^2$ / $r>c$: $\tfrac12 c^2$ | $r\le c$: $r$ / $r>c$: $0$ | $\mathbb{1}[r\le c]$ | **redescending**, fully truncated |

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the stationarity condition of an M-estimator = the normal equations of IRLS) [D3]** — the
  stationary points of $F(x) = \sum_k \rho(\lVert r_k(x)\rVert)$ satisfy
  $$
  \sum_k w\big(\lVert r_k\rVert\big)\,J_k^\top r_k = 0,
    \qquad w(r) = \frac{\psi(r)}{r} \tag{1}
  $$
  which are the normal equations of the least-squares problem
  $\min_\delta\sum_k w_k\lVert r_k + J_k\delta\rVert^2$ with the weights **held fixed**. So the
  fixed point of the "update the weights, solve weighted least squares" iteration (IRLS) is a
  stationary point of $F$. As measured in the reproduction task, at the converged point of Huber
  IRLS, $\lVert\nabla F\rVert_\infty = 3.651\times10^{-7}$.
- **R2 (a robust kernel does not give global optimality; what GNC costs) [D2]** — if $\rho$ is
  non-convex (redescending) then $F$ has several local minima and IRLS depends on the
  initialization. GNC starts from a convex surrogate and anneals $\mu$, but **there is no global
  optimality guarantee**. As measured in the reproduction task (20% outliers): squared loss gives
  ATE $5.4638$, Huber $0.2045$ (**a 26.7-fold improvement**) and GNC-TLS $0.1214$. GNC-TLS,
  however, also cuts 17 inliers, and even with **no** outliers its ATE is $0.1218$ rather than
  $0.1151$ — the price of a redescending kernel.
- **R3 (the global optimality certificate for $SO(2)$ rotation synchronization) [D3]** — if
  $\hat x$ is a stationary point of $\max_{\lvert x_k\rvert=1} x^*Cx$ and
  $$
  \Lambda := \mathrm{diag}\Big(\mathrm{Re}\big(\overline{\hat x}\odot(C\hat x)\big)\Big),
  \qquad S := \Lambda - C \tag{2}
  $$
  satisfies $S \succeq 0$, then $\hat x$ is the **global** optimum. The proof is four lines (see
  the proof sketch), so checking $\lambda_{\min}(S) \ge -\mathrm{tol}$ alone **certifies**
  globality. This is a miniature of what `rosen2019-se-sync` does on $SO(3)$ and $SE(3)$.
- **R3' (the tightness of the certificate breaks under outliers) [D2]** — $S\succeq0$ holds only
  when the relaxation is **tight**. As measured in the reproduction task ($n=40$, a chain plus
  extra edges): with no outliers, $\sigma = 0.02, 0.10$ and $0.30$ all give
  $\lambda_{\min}(S) = O(10^{-16})$ and the certificate **succeeds**, while a mere 10% of outliers
  makes $\lambda_{\min}(S) < 0$ and the certificate **fails** (globality cannot be claimed). In
  other words, **certifiability and robustness do not yet go together.**
- **R4 (TEASER's invariant-measurement decomposition) [D2]** — for point cloud registration
  $y_i = s\,R\,p_i + t + \epsilon_i$, taking the difference of two measurements cancels $t$ (a
  TIM), and taking the norm of that cancels $R$ as well (a TRIM). So scale, then rotation, then
  translation can be solved **one at a time**, each subproblem becoming one-dimensional or a small
  problem on $SO(3)$, so that inliers can be selected by a maximum clique and each piece solved
  certifiably. The point is that the decomposition does not create robustness — it **makes the
  problem small enough to certify.**
- **R5 (breakdown is measured on the metric, not on the kernel) [D1]** — the sweep in the
  reproduction task: as the outlier fraction goes $0 \to 11 \to 20 \to 29 \to 40\%$, Huber's ATE
  goes $0.1151 \to 0.2179 \to 0.2045 \to 0.2980 \to 0.8815$ while GNC-TLS goes
  $0.1218 \to 0.1654 \to 0.1214 \to 0.0961 \to 0.1642$. **Huber degrades 4.3-fold from $0.2045$ at
  20% to $0.8815$ at 40% while the redescending kernel stays around $0.16$** — the difference
  between the influence functions showing up as numbers. In exchange, the redescending kernel is
  slightly worse when there are no outliers.

## Derivation

### R1 — where reweighted least squares comes from

Differentiate $F(x) = \sum_k \rho(\lVert r_k(x)\rVert)$. Writing $n_k := \lVert r_k\rVert$, the
chain rule gives $\partial n_k/\partial x = J_k^\top r_k / n_k$, hence

$$
\nabla F(x) = \sum_k \rho'(n_k)\,\frac{J_k^\top r_k}{n_k}
  = \sum_k \frac{\psi(n_k)}{n_k}\,J_k^\top r_k
  = \sum_k w(n_k)\,J_k^\top r_k. \tag{3}
$$

Setting $\nabla F = 0$ gives (1). On the other hand, the gradient of the weighted least-squares
objective with the weights **held constant**, $G(x) = \tfrac12\sum_k w_k\lVert r_k(x)\rVert^2$, is
$\nabla G = \sum_k w_k J_k^\top r_k$. The two expressions are **literally the same** at
$w_k = w(n_k)$. Therefore the fixed point of the following iteration (IRLS) satisfies (1):

$$
w_k^{(t)} = w\big(\lVert r_k(x^{(t)})\rVert\big), \qquad
x^{(t+1)} = \arg\min_x \tfrac12\sum_k w_k^{(t)}\lVert r_k(x)\rVert^2. \tag{4}
$$

**What the influence function says.** By (3), the size of measurement $k$'s contribution to the
gradient is $\lVert w(n_k)J_k^\top r_k\rVert \approx \psi(n_k)\lVert J_k\rVert$. So **$\psi$ is
that measurement's "force".**

- The squared loss has $\psi(r) = r$, unbounded — one outlier with residual $10^3$ matches $10^6$
  inliers. That is why six outliers take the ATE from $0.115$ to $5.46$ in the reproduction task.
- Huber has $\psi = \min(r,c)$, bounded but not zero — an outlier **keeps pulling with a constant
  force**. As outliers accumulate their sum grows and the estimator collapses (the 40% row of R5).
- Cauchy and TLS have $\psi \to 0$ (redescending) — a sufficiently distant measurement is
  **ignored entirely**. The price is non-convexity and the loss of inliers (GNC-TLS cuts 17
  inliers in the reproduction task and is slightly worse with no outliers at all).

**Where the assumption breaks**: (3) is valid only for $n_k > 0$. As $n_k \to 0$,
$w(n_k) = \psi(n_k)/n_k$ is $0/0$ and the limit differs by kernel (1 for Huber, TLS and Cauchy
alike). Implementations branch on $n_k < 10^{-12}$. The more important assumption is that **the
residuals are independent across measurements** — if perceptual aliasing makes outliers arrive in
**clusters**, they agree with one another and a robust kernel accepts the cluster as inliers
(problem P6).

### R2 — non-convex kernels and GNC's annealing

A redescending kernel has non-convex $\rho$, so $F$ acquires several local minima. GNC replaces
$\rho$ by a family of surrogates $\rho_\mu$ parameterized by $\mu$ such that (a) as
$\mu \to \infty$, $\rho_\mu$ is convex (close to the squared loss) and (b) as $\mu \to 0$,
$\rho_\mu \to \rho$. One then starts at a large $\mu$ and decreases it gradually, running IRLS at
each step — a strategy of **chaining** the solution of a convex problem into the initialization of
a non-convex one.

The GNC weights for TLS come out in closed form (`yang2021-teaser` §6):

$$
w_k = \begin{cases}
1 & n_k^2 \le \dfrac{\mu}{\mu+1}c^2,\\[4pt]
\dfrac{c}{n_k}\sqrt{\mu(\mu+1)} - \mu & \dfrac{\mu}{\mu+1}c^2 < n_k^2 < \dfrac{\mu+1}{\mu}c^2,\\[4pt]
0 & n_k^2 \ge \dfrac{\mu+1}{\mu}c^2.
\end{cases} \tag{5}
$$

For large $\mu$ the middle band is wide and almost every measurement receives a partial weight
(close to convex); as $\mu$ shrinks the 0 and 1 regions widen and it approaches truncation.

**Where the assumption breaks**: GNC is a **heuristic**. (a) There is no theory for the initial
$\mu$ or the decay rate, (b) nor any guarantee that each $\mu$ is solved to global optimality, (c)
nor that the annealing path leads to the right basin. It works in practice because of the problem
structure "outliers are a minority and do not agree with each other", and when that structure
fails so does GNC. That GNC-TLS still reaches ATE $0.1642$ at 40% outliers in the reproduction task
is **a property of this problem instance, not a guarantee**.

### R3 — building the certificate matrix for $SO(2)$ synchronization

Consider rotation-only synchronization. Each node carries $\theta_k$ and each edge $(i,j)$ a
measurement $\bar\theta_{ij} \approx \theta_j - \theta_i$. Setting $x_k := e^{i\theta_k}$ makes
$e^{-i\bar\theta_{ij}}\,\bar x_i x_j \approx 1$, so the objective to maximize is

$$
\max_{x\in\mathbb{C}^n,\ \lvert x_k\rvert = 1}\ x^*Cx, \qquad
C_{ij} = e^{-i\bar\theta_{ij}},\ C_{ji} = e^{+i\bar\theta_{ij}},\ C_{ii} = 0. \tag{6}
$$

Since $x^*Cx = 2\sum_{(i,j)}\mathrm{Re}\big(\bar x_i x_j e^{-i\bar\theta_{ij}}\big)$, this is the
sum of per-edge agreements, and with perfect measurements the maximum is twice the edge count.
**This is a non-convex problem** — the constraint $\lvert x_k\rvert = 1$ is non-convex.

Write the Lagrangian. Treating the constraint as $\lvert x_k\rvert^2 = 1$ with real multipliers
$\Lambda_{kk}$, the stationarity condition of the minimization form $\min -x^*Cx$ is

$$
-C\hat x + \Lambda\hat x = 0
  \quad\Longleftrightarrow\quad
  C\hat x = \Lambda\hat x, \qquad \Lambda \text{ real diagonal.} \tag{7}
$$

Multiplying the $k$-th component of (7) by $\bar{\hat x}_k$ and taking the real part gives
$\Lambda_{kk} = \mathrm{Re}\big(\bar{\hat x}_k (C\hat x)_k\big)$ (using
$\lvert\hat x_k\rvert = 1$), which is (2). And (7) says exactly that
$S\hat x = (\Lambda - C)\hat x = 0$ — **$\hat x$ always lies in the null space of $S$.** The only
remaining question is whether $S$ is positive semidefinite, and that is the four lines of the proof
sketch.

**How to compute the certificate in practice.** (a) Find $\hat x$ with any local method (a spectral
initialization plus coordinate ascent $x_k \leftarrow (C x)_k / \lvert (Cx)_k\rvert$, which
increases the objective monotonically). (b) Form $\Lambda$ and $S$ from (2). (c) Compute
$\lambda_{\min}(S)$. If it is not negative you are **done** — $\hat x$ is the global optimum. If it
is negative, globality cannot be claimed (which does not mean the solution is wrong).

**Where the assumption breaks**: $S \succeq 0$ is a **sufficient** condition. $\hat x$ may be
globally optimal even when $\lambda_{\min}(S) < 0$ — it is the certificate that failed, not the
solution. Also (2) and (7) are for the **rotation-only** problem. Moving to the full pose graph
($SE(d)$) requires eliminating the translations first, and that elimination is the first step of
`rosen2019-se-sync` (a generalized Schur complement) — the same operation as R3 of
`c5-factor-graphs-map`.

### R4 — why TEASER splits the problem

The point cloud registration model is $y_i = s\,R\,p_i + t + \epsilon_i$ ($s>0$ a scale,
$R\in SO(3)$, $t\in\mathbb{R}^3$), and a substantial share of the correspondences $i$ are outliers.
The key is **invariants that eliminate the unknowns one at a time.**

1. **TIM (translation-invariant measurement).** Taking the difference of two correspondences,
   $$
   y_j - y_i = s\,R\,(p_j - p_i) + (\epsilon_j - \epsilon_i) \tag{8}
   $$
   makes $t$ **disappear**. The remaining unknowns are $s$ and $R$.
2. **TRIM (translation- and rotation-invariant measurement).** Taking the norm of (8), and using
   that $R$ preserves norms,
   $$
   \lVert y_j - y_i\rVert \approx s\,\lVert p_j - p_i\rVert \tag{9}
   $$
   makes $R$ **disappear** too. The only unknown left is **the single scalar $s$**.
3. **The payoff of splitting.** Equation (9) is a one-dimensional robust estimation problem and so
   is certifiably solvable (by interval voting or adaptive voting). Knowing $s$ turns (8) into
   robust rotation estimation on $SO(3)$, and knowing $R$ turns $t$ into a component-wise
   one-dimensional robust estimation.
4. **Maximum clique.** Keeping only the TIM pairs that satisfy (9) as edges and finding the
   **maximum clique** of that graph yields a set of mutually consistent correspondences — the step
   that filters outliers **combinatorially**.

**The key reading**: the decomposition itself does not confer robustness. What it does is **reduce
each subproblem to a certifiable size**, which is what lets TEASER call itself "fast and
certifiable". Just as the elimination of R3 in `c5-factor-graphs-map` reduced cost, the elimination
here creates **certifiability**.

**Where the assumption breaks**: step 2 assumes the noise enters the norm independently of $R$. For
large noise, the discrepancy between the two sides of (9) biases the scale estimate. The maximum
clique of step 4 is NP-hard (practice uses approximations), and the whole procedure depends on the
assumption that **outliers do not agree with each other** — a cluster of outliers can form a large
clique among themselves.

## Proof sketch

### R1 — IRLS fixed point = M-estimator stationary point

**Hypotheses** H1: $\rho$ is differentiable on $(0,\infty)$ with $\psi = \rho'$. H2:
$\lVert r_k(x)\rVert > 0$ for every $k$. H3: $r_k$ is differentiable with
$J_k = \partial r_k/\partial x$.
**Conclusions** C1: (3) holds, so $\nabla F = 0 \iff$ (1). C2: a fixed point $x^\ast$ of (4)
satisfies (1). C3: **the converse fails** — a solution of (1) need not be a minimum of $F$.

**Strategy**: one chain rule, plus the observation that "holding the weights fixed gives a
different function".

1. **Gradient.** Since $n_k = \lVert r_k\rVert = \sqrt{r_k^\top r_k}$, we have
   $\partial n_k/\partial x = J_k^\top r_k/n_k$ (the denominator is nonzero by H2). The chain rule
   gives (3).
2. **Fixed point.** If $x^{(t+1)} = x^{(t)} = x^\ast$ in (4), then $x^\ast$ is a stationary point of
   the weighted least-squares problem with weights $w_k = w(\lVert r_k(x^\ast)\rVert)$ held fixed,
   so $\sum_k w_k J_k^\top r_k = 0$ — and those $w_k$ are exactly $w(n_k)$. C2.
3. **Why the converse fails.** (1) is a first-order condition and therefore includes local minima,
   local maxima and saddle points alike. If $\rho$ is non-convex there are several solutions of (1)
   and IRLS reaches the one in whose basin it started. C3.
4. **Monotonicity is not guaranteed either.** That each IRLS iteration decreases $F$ is **not true
   in general**. When $\rho$ can be written as a concave increasing function of $r^2$ (Huber,
   Cauchy and TLS all can), a majorization-minimization argument gives monotone decrease — but it
   requires solving the weighted least-squares problem **exactly**, and running only a few
   Gauss-Newton steps forfeits the guarantee.

**Delete a hypothesis**: dropping H2 leaves $J_k^\top r_k/n_k$ in step 1 undefined — the $0/0$
branch in an implementation is what fills this hypothesis in. Dropping the differentiability of
$\rho$ in H1 (for instance differentiating a hard truncation at its breakpoint) makes $\psi$
discontinuous, and IRLS can oscillate between two weights.

(Omitted: the convergence analysis of IRLS as majorization-minimization. Barfoot SER ch.5.3 and
`yang2021-teaser` §6.)

### R3 — $S \succeq 0$ implies global optimality

**Hypotheses** H1: $C$ is Hermitian. H2: $\hat x$ is feasible ($\lvert\hat x_k\rvert = 1$) and
satisfies (7), with $\Lambda$ as defined in (2). H3: $S := \Lambda - C \succeq 0$.
**Conclusion** C: $x^*Cx \le \hat x^*C\hat x$ for every feasible $x$. That is, $\hat x$ is the
**global** optimum.

**Strategy**: use the constraint to rewrite the objective **exactly** as a quadratic form in $S$,
then read off a bound from $S\succeq0$. No relaxation needs solving and no dual problem needs
forming.

1. **The identity the constraint gives.** For any feasible $x$,
   $$
   x^*\Lambda x = \sum_k \Lambda_{kk}\lvert x_k\rvert^2 = \sum_k\Lambda_{kk} = \operatorname{tr}\Lambda,
   $$
   so $x^*\Lambda x$ is **a constant, independent of $x$**. This is the heart of the proof.
2. **Rewriting the objective.** Therefore
   $$
   -x^*Cx = -x^*Cx + x^*\Lambda x - \operatorname{tr}\Lambda = x^*Sx - \operatorname{tr}\Lambda .
   $$
3. **The bound.** By H3, $x^*Sx \ge 0$, so $-x^*Cx \ge -\operatorname{tr}\Lambda$, i.e.
   $x^*Cx \le \operatorname{tr}\Lambda$ for **every** feasible $x$.
4. **The bound is attained.** By (7) in H2, $S\hat x = \Lambda\hat x - C\hat x = 0$, so
   $\hat x^*S\hat x = 0$, and applying step 2 at $\hat x$ gives
   $\hat x^*C\hat x = \operatorname{tr}\Lambda$. The upper bound of step 3 is attained exactly,
   which is C. $\square$

5. **Relation to the SDP relaxation.** The SDP relaxation of (6) is
   $\max\{\operatorname{tr}(CX) : X\succeq0,\ X_{kk}=1\}$, and the argument above is the same as
   showing that the dual optimum of that relaxation is $\operatorname{tr}\Lambda$. So $S\succeq0$ is
   equivalent to **the relaxation being tight and the SDP solution having rank one**. The
   "Riemannian staircase" of `rosen2019-se-sync` is the procedure that checks this rank condition
   progressively on $SO(3)$.

**Delete a hypothesis**: dropping H3 removes the bound of step 3 and nothing can be said — which is
why the certificate is a **sufficient** condition. Dropping stationarity from H2 makes
$S\hat x \ne 0$ in step 4 so the bound is not attained (but $\operatorname{tr}\Lambda$ is still an
**upper** bound, so one can compute the **optimality gap**
$\operatorname{tr}\Lambda - \hat x^*C\hat x$ and say how close to optimal $\hat x$ is — a useful
number even when the certificate fails).

(Omitted: the generalized Schur complement that eliminates the translations in the extension to
$SE(d)$, and the convergence of the Riemannian staircase. `rosen2019-se-sync` §3-5 and
`carlone2015-lagrangian-duality`.)

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** For the four kernels of the notation table, (a) derive $\psi$ and $w$,
(b) find their limits as $r\to0$ and $r\to\infty$, (c) decide which are redescending, and (d) add
Geman-McClure, $\rho(r) = \dfrac{c^2 r^2}{2(c^2 + r^2)}$, to the table.
*Solution sketch*: for (d), $\psi(r) = \dfrac{c^4 r}{(c^2+r^2)^2}$ and
$w(r) = \dfrac{c^4}{(c^2+r^2)^2}$, and since $\psi$ peaks at $r = c/\sqrt3$ and then falls to zero
it is **redescending**. The crucial observation in (b) is that every kernel has $w\to1$ as
$r\to0$ (agreeing with the squared loss) — kernels differ **only at large residuals**.

**P2 (proof, ★★★, R3)** Write the proof of R3 with no missing steps, and show: (a) that
$S\hat x = 0$ is automatic when $\Lambda$ is defined by (2); (b) that $\operatorname{tr}\Lambda$ is
always an **upper** bound regardless of whether $S\succeq0$; (c) and hence that an optimality gap
can be computed even when the certificate fails. (d) Argue by duality that the rank-one condition
on the SDP relaxation is equivalent to $S\succeq0$.
*Strategy and key inequality*: (b) is the crux — steps 1 and 2 never use H3, so
$x^*Cx = \operatorname{tr}\Lambda - x^*Sx$ always holds, and if the smallest eigenvalue of $S$ is
negative then $x^*Sx \ge n\lambda_{\min}(S)$ gives a relaxed upper bound. (d) uses weak duality and
complementary slackness. The expansion is hidden.

**P3 (numerical, ★, R2·R5)** Run the outlier sweep of the reproduction task and report (a) the ATE
table for the three kernels, (b) the improvement factor of the squared loss over Huber at 20%
outliers, and (c) the outlier fraction at which Huber starts to fail.
*Answer*: (a) the table of acceptance criterion 2 of the reproduction task. (b)
$5.4638 / 0.2045 = 26.7$. (c) 40% (Huber's ATE jumps about threefold from $0.2980$ to $0.8815$,
while over the same interval GNC-TLS moves from $0.0961$ to $0.1642$, staying more than five times
better than Huber). Tolerance $\pm0.02$ on ATE.
Check it: confirm that at 0% outliers **the L2 and Huber** ATEs agree ($0.1151$) — if they do not,
your bounded kernel is touching the inliers. GNC-TLS is slightly worse even at 0%, at $0.1218$.

**P4 (numerical, ★★, R3·R3')** On the $n = 40$ synchronization problem, find (a) at 0% outliers,
$\lambda_{\min}(S)$ and $\lVert S\hat x\rVert$ for $\sigma \in \{0.02, 0.10, 0.30\}$;
(b) $\lambda_{\min}(S)$ at $\{10, 20, 40\}\%$ outliers; (c) the angular RMSE in each case. (d)
Compute the **optimality gap** in the cases where the certificate fails (P2(c)).
*Answer*: (a) $\lvert\lambda_{\min}(S)\rvert < 10^{-14}$ in all three cases (reference
$7.8\times10^{-16}$, $-4.4\times10^{-16}$, $-3.7\times10^{-16}$),
$\lVert S\hat x\rVert \approx 3.3\times10^{-14}$, and angular RMSE $0.0298 / 0.1492 / 0.4473$ rad.
(b) all negative — at $\sigma = 0.02$, $-6.8\times10^{-3} / -7.4\times10^{-2} / -8.9\times10^{-2}$
(averaged over 10 runs). (c) the angular RMSE degrades to $0.72 / 1.15 / 1.75$ rad. Tolerances:
order of magnitude for (a), 30% relative error for (b) and (c) (they are random averages).
*Grading point for (d)*: it passes if it notes that the gap comes not from
$\operatorname{tr}\Lambda - \hat x^*C\hat x$ but from the **relaxed** upper bound of order
$-n\lambda_{\min}(S)$.

**P5 (implementation, ★★★, R1·R2)** On the pose graph of the reproduction task, implement (a) Huber
IRLS and (b) GNC-TLS.
*Rubric*: (a) report $\lVert\nabla F\rVert_\infty < 10^{-6}$ at the IRLS fixed point (the numerical
verification of R1); (b) report the outlier detection as a confusion matrix (reference: Huber
detects 6/6 with 0 false positives, GNC-TLS detects 6/6 while cutting 17 inliers); (c) sweep $c$
over $1$ to $10$ and plot the trade-off between ATE and the false-positive count; (d) show
numerically that changing GNC's $\mu$ annealing schedule changes the result (R2's "not a
guarantee").

**P6 (counterexample, ★★, R1·R2·R4)** Show that "robust estimation works as long as the outlier
fraction is below the breakdown point" is false. (a) Construct a cluster of **mutually consistent**
outliers (for instance by inserting the same wrong loop closure several times) and show numerically
that a robust kernel accepts the cluster as inliers even at a 10% outlier fraction; (b) explain why
TEASER's maximum clique step also fails in that case; (c) state what additional information would
distinguish them.
*Property checklist*: in (a) the outliers must **agree with one another** — random outliers will not
reproduce it. (b) is that a consistent cluster of outliers forms a large clique. (c) passes if it
uses external information (an absolute measurement, temporal ordering, appearance-based
verification) or a combinatorial argument counting hypotheses. "Use a more robust kernel" does not
pass.

**P7 (paper, ★★, R3·R4)** Read §3-5 of `rosen2019-se-sync` and §4-6 of `yang2021-teaser`, then
(a) state in one sentence each **what each paper certifies**; (b) say what SE-Sync's certificate
tells you in the presence of outliers (contrast with R3' here); (c) discuss whether "certifiable"
means the same thing in the two papers.
*Rubric*: (a) passes if it distinguishes SE-Sync's "global optimality of the given (outlier-free)
least-squares problem" from TEASER's "global optimality of the decomposed subproblems plus a
combinatorial selection of the inlier set". (c) is the crux — it is excellent if it points out
that the former is global optimality of an objective and the latter is not a guarantee that **the
right model was chosen**. Citing the R3' numbers of the reproduction task is better still.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read with 3-pass and attack questions 4, 5, 6 and 7 on the third pass.

1. **Rosen, Carlone, Bandeira & Leonard, "SE-Sync: a certifiably correct algorithm for
   synchronization over the special Euclidean group" (2019, IJRR)** — role: `seminal`.
   <https://arxiv.org/abs/1612.07386> (§3-5)
   Extra questions: (a) is the step that eliminates the translations the same operation as the
   Schur complement of R3 in `c5-factor-graphs-map`? (b) state in one sentence each what
   "certifiably correct" does and does not guarantee. (c) can the Riemannian staircase fail to
   terminate?
2. **Yang, Shi & Carlone, "TEASER: fast and certifiable point cloud registration" (2021,
   IEEE T-RO)** — role: `standard`. <https://arxiv.org/abs/2001.07715> (§4-6)
   Extra questions: (a) how does the TIM/TRIM decomposition propagate noise, and how does that
   bias the scale estimate? (b) the maximum clique is NP-hard, so what do the authors actually
   compute? (c) what does the GNC section (§6) guarantee?
3. **Sunderhauf & Protzel, "Switchable constraints for robust pose graph SLAM" (2012, IROS)** —
   role: `standard`. <https://doi.org/10.1109/IROS.2012.6385590>
   Extra questions: (a) how does putting a switch variable in the state differ mathematically from
   an M-estimator (hint: what kernel do you get if you marginalize it)? (b) what role does the
   prior on the switch variable play? (c) how would this method behave on clustered outliers?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) the independent and dependent variables and the baselines — were they tuned fairly?
(6) does the metric match the claim, and are variance and seeds reported? (7) what is missing for
reproduction? (8) if the result were wrong, which assumption would you doubt first?
(9) computational and memory complexity, and real-time feasibility. (10) what would you change to
surpass it in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one laptop CPU core, Part A under 30 seconds and
Part B under a minute, in under 200 MB. Only numpy and scipy.sparse.

**The input data** is produced by the two generators below (deterministic, fixed seed). No external
dataset is needed.

**Part A — a pose graph with 20% outliers.** Mix outlier loop closures into the SE(2) pose graph of
`c5-factor-graphs-map` and compare squared-loss GN, Huber IRLS and GNC-TLS.

```python
"""c5-robust-global-estimation Part A: an SE(2) pose graph generator with outliers."""

import numpy as np

SEED = 20261112
SIGMA_ODOM = np.array([0.02, 0.02, 0.01])
SIGMA_LOOP = np.array([0.05, 0.05, 0.02])
SIGMA_ANCHOR = np.array([1e-3, 1e-3, 1e-3])


def wrap(a):
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def rot(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])


def between(xi, xj):
    return np.array([*(rot(xi[2]).T @ (xj[:2] - xi[:2])), wrap(xj[2] - xi[2])])


def make_graph(outlier_frac=0.2, laps=2, per_lap=50, radius=5.0, every=2, seed=SEED):
    """Ground truth, edges, measurements and the outlier mask. An outlier is an extra edge with a random relative measurement."""
    rng = np.random.default_rng(seed)
    n = laps * per_lap
    ang = 2.0 * np.pi * np.arange(n) / per_lap
    gt = np.column_stack([radius * np.cos(ang), radius * np.sin(ang), wrap(ang + np.pi / 2)])
    edges = [(i, i + 1, SIGMA_ODOM) for i in range(n - 1)]
    loops = [(i, i + per_lap, SIGMA_LOOP) for i in range(0, per_lap - 2, every)]
    n_out = int(round(outlier_frac * len(loops) / (1.0 - outlier_frac)))
    out_pairs = []
    for _ in range(n_out):
        i, j = rng.choice(n, 2, replace=False)
        out_pairs.append((int(min(i, j)), int(max(i, j)), SIGMA_LOOP))
    edges = edges + loops + out_pairs
    meas, is_out = [], []
    for k, (i, j, s) in enumerate(edges):
        if k >= len(edges) - n_out:
            meas.append(
                np.array([rng.uniform(-6, 6), rng.uniform(-6, 6), rng.uniform(-np.pi, np.pi)])
            )
            is_out.append(True)
        else:
            meas.append(between(gt[i], gt[j]) + s * rng.standard_normal(3))
            is_out.append(False)
    return gt, edges, np.array(meas), np.array(is_out)
```

Use the residual and Jacobians of (15) and (16) of the `c5-factor-graphs-map` reproduction task
unchanged, and the same anchor factor. Apply the weights to the whitened residual norm
$n_k = \lVert r_k\rVert$, **treating the $3\times3$ block as one unit** — weighting component by
component would separate rotation from translation and change what the kernel means. The initial
guess is dead reckoning without the loop closures. Use the kernel parameter $c = 3$ (the 97th
percentile of $\chi^2_3$ for a residual norm with three degrees of freedom).

**Part B — the global optimality certificate for $SO(2)$ synchronization.** Use the generator
below.

```python
"""c5-robust-global-estimation Part B: SO(2) rotation synchronization and the certificate matrix."""

import numpy as np


def make_sync(n=40, sigma=0.02, outlier_frac=0.0, seed=100, extra_edges=3):
    """True angles, edges, relative measurements and the outlier mask."""
    rng = np.random.default_rng(seed)
    th = rng.uniform(-np.pi, np.pi, n)
    th[0] = 0.0
    edges = [(k, (k + 1) % n) for k in range(n)]
    for _ in range(extra_edges * n // 10):
        i, j = rng.choice(n, 2, replace=False)
        if i != j:
            edges.append((int(i), int(j)))
    meas, is_out = [], []
    for i, j in edges:
        if rng.random() < outlier_frac:
            meas.append(rng.uniform(-np.pi, np.pi))
            is_out.append(True)
        else:
            meas.append(th[j] - th[i] + rng.normal(scale=sigma))
            is_out.append(False)
    return th, edges, np.array(meas), np.array(is_out)


def build_C(n, edges, meas):
    """The Hermitian data matrix: C_ij = exp(-i * meas_ij) and C_ji = conj(C_ij)."""
    C = np.zeros((n, n), dtype=complex)
    for (i, j), m in zip(edges, meas, strict=True):
        C[i, j] += np.exp(-1j * m)
        C[j, i] += np.exp(1j * m)
    return C


def certificate(C, x):
    """Lambda = diag(Re(conj(x) * (C x))) and S = Lambda - C. S >= 0 certifies x as the global optimum."""
    lam = np.real(np.conj(x) * (C @ x))
    S = np.diag(lam).astype(complex) - C
    ev = np.linalg.eigvalsh(S)
    return float(ev[0]), float(np.linalg.norm(S @ x)), float(np.sum(lam))
```

For the local solver use **coordinate ascent** — project the leading eigenvector of $C$ onto unit
modulus as the initialization, then update one coordinate at a time by
$x_k \leftarrow (Cx)_k/\lvert(Cx)_k\rvert$ (this update increases the objective monotonically and
therefore converges). Fix the gauge by normalizing $x_0$ to be a positive real.

**Acceptance criteria — all four conditions must hold.**

1. **Part A (20% outliers)** — 100 poses and 129 edges (99 odometry + 24 loop closures + 6
   outliers, i.e. **20%** of the loop-closure edges), dead-reckoning ATE $0.2874$, and the three
   kernels give

   | Kernel | ATE (m) |
   |---|---|
   | squared loss (L2) | $5.4638$ |
   | Huber ($c=3$) | $0.2045$ |
   | GNC-TLS ($c=3$) | $0.1214$ |

   with a tolerance of $\pm0.01$. The improvement factor is $5.4638/0.2045 = 26.7$ (far beyond the
   blueprint's "at least twofold"). And at the Huber IRLS fixed point
   $\lVert\nabla F\rVert_\infty < 10^{-6}$ (reference $3.651\times10^{-7}$) — the numerical
   verification of R1.
2. **Part A (sweep)** — varying the outlier fraction, reproduce the table below (ATE, tolerance
   $\pm0.02$).

   | Outliers | edges | L2 | Huber | GNC-TLS |
   |---|---|---|---|---|
   | 0% | 0 | $0.1151$ | $0.1151$ | $0.1218$ |
   | 11% | 3 | $3.8666$ | $0.2179$ | $0.1654$ |
   | 20% | 6 | $5.4638$ | $0.2045$ | $0.1214$ |
   | 29% | 10 | $4.6225$ | $0.2980$ | $0.0961$ |
   | 40% | 16 | $5.7145$ | $0.8815$ | $0.1642$ |

   **In the 0% row, L2 and Huber must agree** ($0.1151$) — the check that a bounded kernel does not
   touch the inliers. GNC-TLS does not agree ($0.1218$), and that is what a redescending kernel
   costs. Also report that Huber degrades 4.3-fold from $0.2045$ at 20% to $0.8815$ at 40% while
   the redescending kernel stays around $0.16$.
3. **Part B (the certificate succeeds)** — with no outliers and $n = 40$, all of
   $\sigma \in \{0.02, 0.10, 0.30\}$ give $\lvert\lambda_{\min}(S)\rvert < 10^{-14}$ (reference
   $7.8\times10^{-16}$, $-4.4\times10^{-16}$, $-3.7\times10^{-16}$) and
   $\lVert S\hat x\rVert < 10^{-12}$ (reference $3.3\times10^{-14}$). The angular RMSE is
   $0.0298 / 0.1492 / 0.4473$ rad (averaged over 10 runs, within 20% relative error).
   **The certificate still holds at a noise level of $\sigma = 0.3$** — the tightness of the
   relaxation is fairly robust to noise.
4. **Part B (the certificate fails)** — at $\{10, 20, 40\}\%$ outliers,
   $\lambda_{\min}(S) < -10^{-4}$ (reference at $\sigma=0.02$: $-6.8\times10^{-3}$,
   $-7.4\times10^{-2}$, $-8.9\times10^{-2}$; averaged over 10 runs, within 30% relative error),
   while $\lVert S\hat x\rVert$ is still of order $10^{-13}$ (it is a stationary point, just not a
   global one). The angular RMSE degrades to $0.72 / 1.15 / 1.75$ rad. The conclusion of this part
   is that **once outliers appear, global optimality cannot be certified.**

**Baselines**: (a) the baseline for Part A is squared-loss GN (the solver of
`c5-factor-graphs-map`). (b) The second baseline is the L2 solution on the graph with the outliers
**removed by hand**, which gives the ceiling for robust estimation (reference: the $0.1151$ of the
0% row). (c) The baseline for Part B is the spectral solution (the projected leading eigenvector);
report how much coordinate ascent improves on it. Optional: solve the same objective with
`scipy.optimize` and check that it reaches the same value as coordinate ascent.

**Numbers to report**: every value of the four criteria, the outlier detection confusion matrix of
Part A (reference: Huber detects 6/6 with 0 false positives, GNC-TLS detects 6/6 while cutting 17
inliers), and the upper bound on the optimality gap in the cases where Part B's certificate fails
(P2(c)).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The three kernels differ in the 0% row of Part A | $c$ is so small that inliers are being cut too | look at the distribution of the inlier residual norms and check that $c$ exceeds the 99th percentile |
| Huber gives the same ATE as L2 | the weights were applied component by component, or the residuals were not whitened | check that $n_k$ is the norm of the $3\times3$ block and that the weight is $\min(1,c/n_k)$ |
| IRLS oscillates | only one GN step was taken per weight update, or $c$ sits on the boundary of the residual distribution | raise the inner GN iterations to three and print $F$ at every iteration |
| $\lVert\nabla F\rVert$ is of order $10^{-2}$ | the gradient was computed from the squared loss rather than from (3) | check that the weight $w(n_k)$ appears in the gradient expression |
| GNC-TLS cuts every edge to zero | the initial $\mu$ is so small that it starts near truncation | start $\mu$ at around $\max_k n_k^2/c^2$ and **decrease** it |
| The Part B angular error is of order $\pi$ | the sign in the exponent of $C_{ij}$ is flipped | check that $C_{ij} = e^{-i\bar\theta_{ij}}$ and that $\sigma=0$ recovers the truth |
| $\lVert S\hat x\rVert$ in Part B is of order $10^{-1}$ | the local solver did not converge (a simultaneous update can oscillate) | check that the update is coordinate-wise (Gauss-Seidel) and raise the iteration count |
| $\lambda_{\min}(S)$ is negative even at 0% outliers | the gauge was not fixed, or the real part of $\Lambda$ was not taken | check that $\Lambda$ is a real diagonal and that $x_0$ was normalized |

## Open problems

- **(Open problem) A method that is both certifiable and robust** — the certificate of R3 proves
  global optimality of the **outlier-free** least-squares problem. As R3' shows, a mere 10% of
  outliers breaks the tightness and the certificate fails. TEASER splits the problem and certifies
  the pieces, but that certificate is not a guarantee that **the inlier set was chosen correctly**.
  Current approaches: the dual certificate of
  [SE-Sync](https://arxiv.org/abs/1612.07386), the decomposition plus maximum clique of
  [TEASER](https://arxiv.org/abs/2001.07715), and
  [Lagrangian duality in 3D SLAM](https://arxiv.org/abs/1506.00746). What is missing: a
  characterization of the region of outlier fraction $\epsilon$ and noise $\sigma$ in which the
  global optimality of a **robust** objective can be certified.
- **(Open problem) A theory of GNC annealing** — the initial $\mu$, its decay rate and the stopping
  criterion are all heuristic, and there is no guarantee that the annealing path reaches the right
  basin (R2). That GNC-TLS works well at 40% outliers in the reproduction task is a property of the
  instance, not a guarantee. Current approach: the GNC of
  [TEASER §6](https://arxiv.org/abs/2001.07715) and its experimental evaluation. What is missing:
  conditions mapping a schedule to global optimality (or to its probability).
- **(Open problem) Clustered outliers (perceptual aliasing)** — every robust kernel and every
  RANSAC-style method assumes outliers do not agree with each other. In repetitive environments
  (corridors, car parks, orchards) false loop closures **agree** and arrive as a group, and once
  that group is large enough no kernel will reject it (problem P6). Current approaches:
  [switchable constraints](https://doi.org/10.1109/IROS.2012.6385590), appearance-based
  verification, and the discussion in §IV of the
  [long-term SLAM survey](https://arxiv.org/abs/1606.05830). What is missing: a theory that puts
  the **correlation structure** of outliers into the model and states a breakdown point under it.

## Concept check

Run `rc quiz c5-robust-global-estimation`. The quiz is for **concept checking only**; the real work
is the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: the IRLS weight in terms of $\rho$ and $\psi$; why Huber collapses as
outliers accumulate; the step that makes the $S \succeq 0$ certificate work; whether an SE-Sync
style certificate guarantees anything in the presence of outliers; and what TEASER's TIM/TRIM
decomposition is for.

## How to study this stage

1. **Do $\psi$ and $w$ for the four kernels by hand (45 min)** — differentiate each of the four
   kernels in the notation table to get $\psi$ and $w$, and write down the limits as $r\to0$ and
   $r\to\infty$. That is P1. The important moment is confirming that every kernel agrees with the
   squared loss at small residuals.
2. **Write (3) from a blank page (30 min)** — it is one chain rule, and that one line is the entire
   reason IRLS exists. You should be able to state the observation "holding the weights fixed gives
   a different function" in your own words.
3. **Run Part A first (90 min)** — watch L2 break to $5.46$ and Huber recover to $0.20$. Then print
   $\lVert\nabla F\rVert$ to confirm that the IRLS fixed point really is a stationary point (the
   numerical verification of R1). The first check is whether L2 and Huber give the same value at 0%
   outliers.
4. **See the breakdown in the sweep (45 min)** — plot Huber jumping at 40% while TLS holds. This is
   where the difference between the influence functions appears as numbers. Read Barfoot SER ch.5.3
   alongside.
5. **Memorize the four lines of R3's proof (60 min)** — remember only step 1 ($x^*\Lambda x$ is
   constant) and the rest follows. Then use P2(b) to confirm that "the upper bound survives even
   when the certificate fails" — that observation is the most useful one in practice.
6. **Run Part B (60 min)** — see $\lambda_{\min}(S)$ at $10^{-16}$ with no outliers, then add 10%
   outliers and watch it go negative. **"Robust to noise, fragile to outliers"** is the character
   of relaxation tightness, and the conclusion of this lesson.
7. **Read the papers asking "what is certified" (150 min)** — go through §3-5 of SE-Sync and §4-6 of
   TEASER writing one sentence each on exactly what their "certifiable" claims. Then translate
   Sunderhauf & Protzel's switch variables into an M-estimator. Write the one-page note per paper
   **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the three open problems and write a
   paragraph. Clustered outliers become a research topic the moment you solve P6.

**Passing bar**: you can write (3) and the four lines of R3's proof from a blank page, you can
derive $\psi$ and $w$ for the four kernels, you have code that satisfies all four conditions of the
reproduction task, and you have notes on all three papers.
