---
id: s5-distributed-optimization
lang: en
title: Distributed optimization and distributed SLAM
summary: >-
  How several robots solve one optimization together without handing their data to anyone else.
  Prove the convergence of two-block ADMM, and derive that on a quadratic problem ADMM becomes an
  affine iteration whose rate is an explicit spectral radius. Prove that the convergence rate of
  block Gauss-Seidel on a distributed pose graph is exactly 1 - lambda_min(Lambda_22^-1 S) with S
  the Schur complement, so it always converges when Lambda is positive definite, then match the
  centralized solution to within 1e-4 on a two-robot pose graph while measuring the trade-off
  between communication volume and convergence rate.
objectives:
  - Derive the two-block ADMM iteration from the augmented Lagrangian and state its convergence theorem with the hypotheses separated.
  - Show that ADMM is an affine iteration on a quadratic objective and write its rate as a spectral radius.
  - Derive the error recursion of block Gauss-Seidel and its rate through the Schur complement.
  - Prove that block Gauss-Seidel always converges when Lambda is positive definite.
  - Measure how the separator size sets the communication volume while the coupling strength sets the rate.
  - Explain why convergence of a distributed solver and certification of global optimality are different guarantees.
tags: [multi-robot, distributed-optimization, admm, gauss-seidel, distributed-slam, research]
---

# Distributed optimization and distributed SLAM

## Setup and notation

The normal equations and the Schur complement of `c5-factor-graphs-map` and the distributed-rate
viewpoint of `s5-graph-consensus` carry over. **The problem of this lesson is the linearized least
squares of R2 in `c5-factor-graphs-map`, split between two robots.** Additional symbols:

| Symbol | Meaning |
|---|---|
| $f_i$ | the piece of the objective robot $i$ can build **from its own data alone** |
| $\Lambda, \eta$ | the information matrix and vector of the linearized problem ($\Lambda\delta = \eta$, (3) of `c5-factor-graphs-map`) |
| $\Lambda_{11}, \Lambda_{12}, \Lambda_{22}$ | $\Lambda$ partitioned into robot A and B blocks, with $\Lambda_{21} = \Lambda_{12}^\top$ |
| $S := \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ | the **Schur complement** of $\Lambda_{11}$ (R3 of `c5-factor-graphs-map`) |
| $\mathcal{S}$ | the **separator** — the poses appearing in inter-robot measurements. These are the only things communicated |
| $\rho > 0$ | the penalty (augmentation) parameter of ADMM |
| $u, v, w$ | ADMM's two block variables and the (scaled) dual variable |
| $M$ | the error iteration matrix of block Gauss-Seidel, $M = \Lambda_{22}^{-1}\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ |
| $T(\rho)$ | the affine matrix of the ADMM iteration on a quadratic problem; the rate is $\rho(T)$ |

**Why distributed.** Obtaining the centralized solution $\delta^\ast = \Lambda^{-1}\eta$ requires
someone to hold all of $\Lambda$. There are three reasons that is impossible or undesirable:
(a) communication bandwidth (every measurement cannot be shipped to one place), (b) privacy (a
robot does not hand over its own trajectory and observations), and (c) a single point of failure
(if the central node dies, everything stops). This lesson analyses two methods — ADMM and block
Gauss-Seidel — by which **each robot solves only its own block and exchanges only the separator**
yet arrives at the same answer.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (the two-block ADMM iteration and its convergence) [D3]** — for
  $\min_{u,v} f_1(u) + f_2(v)$ subject to $u = v$, the augmented Lagrangian yields
  $$
  u^{k+1} = \arg\min_u f_1(u) + \tfrac{\rho}{2}\lVert u - v^k + w^k\rVert^2, \quad
  v^{k+1} = \arg\min_v f_2(v) + \tfrac{\rho}{2}\lVert u^{k+1} - v + w^k\rVert^2, \quad
  w^{k+1} = w^k + u^{k+1} - v^{k+1}. \tag{1}
  $$
  If $f_1, f_2$ are closed proper convex and the augmented Lagrangian has a saddle point, then
  **the residual $u^k - v^k \to 0$ and the objective converges to the optimum**
  (`boyd2011-admm` §3.2). Strong convexity and smoothness are **not required** — and the price is
  that **no rate is guaranteed.**
- **R2 (on a quadratic problem ADMM is an affine iteration) [D2]** — if
  $f_i(x) = \tfrac12 x^\top\Lambda_i x - \eta_i^\top x$ then both $\arg\min$ in (1) are closed
  form, $(\Lambda_i + \rho I)^{-1}(\cdots)$, and the whole iteration is affine. The iteration
  matrix $T(\rho)$ on the state $(v, w)$ can be written explicitly and **the rate is
  $\rho(T(\rho))$**. A small $\rho$ makes the dual update slow and a large one ties the primal
  variables together, so **the optimal $\rho$ is interior.** As measured: the minimum
  $\rho(T) = 0.979669$ occurs at $\rho = 56.23$.
- **R3 (the error recursion and rate of block Gauss-Seidel) [D2]** — if robots A and B take turns
  minimizing their own block exactly,
  $$
  \delta_1^{k+1} = \Lambda_{11}^{-1}(\eta_1 - \Lambda_{12}\delta_2^{k}), \qquad
  \delta_2^{k+1} = \Lambda_{22}^{-1}(\eta_2 - \Lambda_{21}\delta_1^{k+1}) \tag{2}
  $$
  and the error $e_2^k := \delta_2^k - \delta_2^\ast$ satisfies $e_2^{k+1} = M\,e_2^k$ with
  $M = \Lambda_{22}^{-1}\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$. The rate is $\rho(M)$. As
  measured: predicted $0.96860653$ against an empirical $0.96860641$ (relative error
  $1.2\times10^{-7}$).
- **R3' (it always converges when $\Lambda \succ 0$; the rate in closed form) [D3]** —
  $$
  M = I - \Lambda_{22}^{-1}S \quad\Longrightarrow\quad
  \mathrm{spec}(M) = \{1 - \mu : \mu \in \mathrm{spec}(\Lambda_{22}^{-1}S)\} \subset [0, 1),
  \qquad \rho(M) = 1 - \lambda_{\min}\big(\Lambda_{22}^{-1}S\big). \tag{3}
  $$
  If $\Lambda\succ0$ then $S \succ 0$ (problem P2 of `c5-factor-graphs-map`) and
  $S \preceq \Lambda_{22}$, so $\mu \in (0, 1]$ and therefore $\rho(M) < 1$ — **block Gauss-Seidel
  converges with no further assumptions.** As measured:
  $\lambda_{\min}(\Lambda_{22}^{-1}S) = 0.0313934719$ and $1 - \lambda_{\min}$ agrees with
  $\rho(M)$ to $2.0\times10^{-15}$.
- **R4 (communication volume and convergence rate are different axes, and they move in opposite
  directions) [D2]** — only the **separator poses** are exchanged per round, so the per-round
  volume is $O(\lvert\mathcal{S}\rvert)$ and the total is (rounds) $\times$
  $O(\lvert\mathcal{S}\rvert)$. But adding inter-robot measurements improves accuracy while
  strengthening the coupling in (3), pushing $\rho(M)$ **towards 1**. As measured: inter-robot
  edges $13 \to 5 \to 3 \to 1$ give $\rho(M)$ of
  $0.98968 \to 0.96861 \to 0.95421 \to 0.00466$, **monotonically decreasing**. With a single edge
  it is essentially done in one round.
- **R5 (distributed convergence $\ne$ certified global optimality) [D1]** — (2) and (3) are
  statements about converging to the solution of the **linearized** quadratic problem. Global
  optimality of the original problem on $SE(d)$ needs the certification machinery of R3 in
  `c5-robust-global-estimation`, and doing that certification in a distributed way is yet another
  problem (`tian2021-distributed-certifiable`). **"It converged in a distributed fashion" and "it
  is globally optimal" are different guarantees.**

## Derivation

### R1 — how ADMM comes out of the augmented Lagrangian

Attaching a multiplier $y$ to the constraint $u = v$, the **augmented** Lagrangian is

$$
L_\rho(u, v, y) = f_1(u) + f_2(v) + y^\top(u - v) + \tfrac{\rho}{2}\lVert u - v\rVert^2 \tag{4}
$$

the ordinary Lagrangian plus a quadratic penalty, which (a) makes each subproblem strongly convex
even when $f_i$ is not, and (b) makes the dual function differentiable.

Setting $w := y/\rho$ (the scaled dual variable), completing the square gives
$y^\top(u-v) + \tfrac\rho2\lVert u-v\rVert^2
= \tfrac\rho2\lVert u - v + w\rVert^2 - \tfrac\rho2\lVert w\rVert^2$, so minimizing over $u$ with
$v, w$ fixed gives the first line of (1) and over $v$ the second. The dual ascent step is
$y^{k+1} = y^k + \rho(u^{k+1}-v^{k+1})$, which divided by $\rho$ is the third line. **ADMM is
"minimize the two blocks in turn, then take one dual ascent step"**; with one block it degenerates
to the augmented Lagrangian method, and without the penalty to dual decomposition.

**What is guaranteed.** The theorem of `boyd2011-admm` §3.2 uses only two assumptions — (A1)
$f_1, f_2$ closed proper convex, and (A2) the unaugmented Lagrangian of (4) has a saddle point.
Then $\lVert u^k - v^k\rVert \to 0$ (primal residual), $y^k \to y^\ast$ (dual convergence) and
$f_1(u^k)+f_2(v^k) \to p^\ast$. **Strong convexity, smoothness and finiteness of $f_i$ are never
used** — which is why ADMM applies to $\ell_1$ penalties and to indicator functions
(projections).

**Where the assumption breaks**: the theorem **gives no rate.** For general convex problems ADMM
is on the order of $O(1/k)$, and strong convexity plus smoothness must be added before linear
convergence can be claimed. The theorem also says nothing about choosing $\rho$, while practical
performance responds to it by **orders of magnitude** (reproduction task Part C: after 3000
iterations the error is $4.4\times10^{-3}$ at $\rho = 1$ against $3.1\times10^{-14}$ at
$\rho = 56$). Extending to three or more blocks can **break convergence outright** — counterexamples
are known, so the two-block hypothesis is essential.

### R2 — writing the iteration matrix explicitly on a quadratic problem

Let $f_i(x) = \tfrac12 x^\top\Lambda_i x - \eta_i^\top x$ with $\Lambda = \Lambda_1 + \Lambda_2$
and $\eta = \eta_1 + \eta_2$ (each robot stacks **only its own edges**; the individual
$\Lambda_i$ may be singular). Both $\arg\min$ of (1) come out in closed form from the first-order
conditions:

$$
u^{k+1} = A_1\big(\eta_1 + \rho(v^k - w^k)\big), \qquad
v^{k+1} = A_2\big(\eta_2 + \rho(u^{k+1} + w^k)\big), \tag{5}
$$

$$
A_i := (\Lambda_i + \rho I)^{-1} \quad (\rho > 0 \text{ makes this invertible with only } \Lambda_i \succeq 0).
$$

Combining (5) with $w^{k+1} = w^k + u^{k+1} - v^{k+1}$ gives an **affine** iteration on the state
$(v^k, w^k)$. Eliminating $u^{k+1}$ and collecting coefficients,

$$
\begin{bmatrix}v^{k+1}\\ w^{k+1}\end{bmatrix}
= T(\rho)\begin{bmatrix}v^{k}\\ w^{k}\end{bmatrix} + c(\rho),
\qquad
T(\rho) = \begin{bmatrix}
\rho A_2 B_v & \rho A_2(B_w + I)\\
B_v - \rho A_2 B_v & I + B_w - \rho A_2(B_w + I)
\end{bmatrix}, \tag{6}
$$

where $B_v := \rho A_1$ and $B_w := -\rho A_1$ (the coefficients of $v^k$ and $w^k$ in
$u^{k+1}$). The convergence condition and rate of an affine iteration follow from fixed-point
theory:

$$
\text{convergence} \iff \rho(T) < 1, \qquad \lVert \text{error}^k\rVert \sim \rho(T)^k. \tag{7}
$$

**Why both extremes of $\rho$ are bad.** As $\rho \to 0$ we get $A_i \to \Lambda_i^{-1}$, so each
subproblem is solved well but the dual update $w^{k+1} - w^k = u-v$ enters scaled by $\rho$, making
**agreement slow**. As $\rho \to \infty$ we get $A_i \to \rho^{-1}I$, so the two variables are
tied so tightly to each other that **the original problem is barely solved**. So
$\rho(T(\rho))$ has an interior minimum. As measured: $0.999552$ at $\rho = 1$, $0.999991$ at
$\rho = 10^5$, and the minimum $0.979669$ at $\rho = 56.23$.

**Where the assumption breaks**: (6) assumes the **splitting is fixed** and that each robot solves
its subproblem **exactly**. Approximating the subproblem iteratively makes this an inexact ADMM and
weakens the guarantee. Also (6) has $u, v$ as **copies of the whole state** — which is why a round
exchanges the entire state (a cost that surfaces in R4). Reducing the copied part to the separator
changes the matrices and $T$ must be re-derived.

### R3 — the error recursion of block Gauss-Seidel

Unlike ADMM, **each robot treating the other's current estimate as a constant and minimizing its
own block exactly** is block Gauss-Seidel (the distributed Gauss-Seidel of Choudhary et al.).
Solving the first block row of the full first-order condition

$$
\begin{bmatrix}\Lambda_{11} & \Lambda_{12}\\ \Lambda_{21} & \Lambda_{22}\end{bmatrix}
\begin{bmatrix}\delta_1\\ \delta_2\end{bmatrix}
= \begin{bmatrix}\eta_1\\ \eta_2\end{bmatrix} \tag{8}
$$

for $\delta_1$ and the second for $\delta_2$ gives (2). The optimum
$(\delta_1^\ast, \delta_2^\ast)$ satisfies (8), so subtracting it from (2) leaves the error:

$$
e_1^{k+1} = -\Lambda_{11}^{-1}\Lambda_{12}\,e_2^{k}, \qquad
e_2^{k+1} = -\Lambda_{22}^{-1}\Lambda_{21}\,e_1^{k+1}
= \underbrace{\Lambda_{22}^{-1}\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}}_{=: M}\,e_2^{k}. \tag{9}
$$

The error follows a **linear recursion** with iteration matrix $M$, so the rate is $\rho(M)$, and
robot A's error $e_1^k = -\Lambda_{11}^{-1}\Lambda_{12}e_2^{k-1}$ follows the same rate.

**The relation to the centralized solution.** When (9) goes to zero both robots' estimates go to
$\Lambda^{-1}\eta$ — **the same point as the centralized solution**. Being distributed costs no
accuracy. What it costs is **rounds**. As measured: 44 rounds to $10^{-2}$, 186 to $10^{-4}$, 475
to $10^{-8}$, and an error of $1.5\times10^{-15}$ after 4000.

**Where the assumption breaks**: (2) assumes each robot solves its block **exactly** — which is
itself expensive when $\Lambda_{11}$ is large, and approximating it breaks the clean recursion of
(9). More importantly, (8) is the **linearized** problem: on a nonlinear pose graph $\Lambda$
changes with every outer Gauss-Newton iteration, and cutting the inner Gauss-Seidel rounds means
more outer iterations (problem P5). And with $m$ blocks rather than two, $M$ comes from a block
triangular splitting and depends on the robot ordering — **the ordering changes the rate** (the
same kind of problem as the elimination ordering of `c5-sparsity-isam`).

### R4 — communication volume against convergence rate

**What travels in one round.** In (2) all robot A needs is $\Lambda_{12}\delta_2^k$, and
$\Lambda_{12}$ is nonzero **only at poses carrying inter-robot measurements**. So all B has to send
are the increments of its own poses in the separator $\mathcal{S}$:

$$
\text{volume per round} = O\big(d\,\lvert\mathcal{S}\rvert\big), \qquad
\text{total} = (\text{rounds}) \times O\big(d\,\lvert\mathcal{S}\rvert\big) \tag{10}
$$

($d = 3$ being the dimension of an $SE(2)$ pose). The full-copy ADMM of R2, by contrast, sends
$O(d\,N)$ per round. As measured ($N = 50$, $\lvert\mathcal{S}\rvert = 10$): Gauss-Seidel sends 30
doubles per round and full-copy ADMM 150 — a factor of **five**. And the rounds to reach $10^{-4}$
are 186 against 377, again fewer for Gauss-Seidel. **On this problem full-copy ADMM loses on both
axes** — which is why the distributed-SLAM literature uses Gauss-Seidel-type methods.

**Where the trade-off lives.** Adding inter-robot measurements raises the estimation accuracy (more
constraints). But in (3), a larger $\Lambda_{12}$ makes
$S = \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ smaller, so
$\lambda_{\min}(\Lambda_{22}^{-1}S)$ shrinks and $\rho(M) = 1 - \lambda_{\min}$ approaches 1. As
measured:

| inter-robot edges | separator | $\rho(M)$ |
|---|---|---|
| 13 | 26 | $0.98968495$ |
| 5 | 10 | $0.96860653$ |
| 3 | 6 | $0.95420678$ |
| 1 | 2 | $0.00466476$ |

**Share more and you are more accurate but must iterate more.** With a single edge
$\rho(M) \approx 0.005$ finishes in effectively one round, but the relative placement of the two
trajectories then hangs on that one edge. This is the design trade-off of distributed SLAM, and what
makes it particularly awkward is that **the per-round volume (separator size) and the number of
rounds (coupling strength) worsen together.**

**Where the assumption breaks**: (10) treats communication as **lossless and instantaneous**. With
packet loss the recursion of (9) becomes an asynchronous iteration and the convergence condition
changes (the subject of `s5-comms-constrained-estimation`). And (10) counts only the increments —
in practice pose ids, covariance blocks and data-association hypotheses travel too, so the constant
factor is large.

### R5 — convergence and certification are different guarantees

What (2) and (3) give is "it converges to the unique solution of the **linearized** quadratic
problem". The original problem is non-convex on $SE(d)^N$, and claiming global optimality there
requires the dual certificate ($S \succeq 0$) of R3 in `c5-robust-global-estimation`. Computing
that certificate in a distributed way — each robot contributing to a global certificate while
seeing only its own block — is a separate problem, which
`tian2021-distributed-certifiable` solves: it solves the rank-relaxed problem distributedly by
Riemannian block coordinate descent and performs the certification distributedly as well. **[D1]**

When reporting, keep three things apart: (a) how close the distributed iteration is to the
centralized solution (Part A of the reproduction task), (b) whether that centralized solution is
the solution of the linearized problem or a local minimum of the original, and (c) whether that
local minimum is global (certification). The habit of checking which one a paper claims when it
writes both "distributed" and "certifiably correct" is a necessary one.

## Proof sketch

### R3' — block Gauss-Seidel converges whenever $\Lambda \succ 0$

**Hypotheses** H1: $\Lambda = \begin{bmatrix}\Lambda_{11} & \Lambda_{12}\\ \Lambda_{21} & \Lambda_{22}\end{bmatrix}$
is symmetric positive definite (with $\Lambda_{21} = \Lambda_{12}^\top$). H2: the iteration is (2).
**Conclusions** C1: $M = I - \Lambda_{22}^{-1}S$ and $\mathrm{spec}(M) \subset [0,1)$.
C2: $\rho(M) = 1 - \lambda_{\min}(\Lambda_{22}^{-1}S) < 1$, so (2) **always** converges.

**Strategy**: rewrite $M$ through the Schur complement and use only the two inequalities
$S \succ 0$ and $S \preceq \Lambda_{22}$. The Schur complement of `c5-factor-graphs-map` is reused
directly.

1. **Rewriting $M$.** From the definition
   $S = \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ we get
   $\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12} = \Lambda_{22} - S$, hence
   $$
   M = \Lambda_{22}^{-1}\big(\Lambda_{22} - S\big) = I - \Lambda_{22}^{-1}S .
   $$
   So the eigenvalues of $M$ are $1 - \mu$ for $\mu \in \mathrm{spec}(\Lambda_{22}^{-1}S)$.
2. **$\mu > 0$.** By H1 the principal submatrices satisfy $\Lambda_{11} \succ 0$ and
   $\Lambda_{22} \succ 0$, and the Schur complement is $S \succ 0$ too (problem P2 of
   `c5-factor-graphs-map` — substitute $x = (-\Lambda_{11}^{-1}\Lambda_{12}v,\ v)$ into
   $x^\top\Lambda x > 0$ for $v\ne0$). The product $\Lambda_{22}^{-1}S$ of two positive definite
   matrices has all **positive real** eigenvalues (it is similar to
   $\Lambda_{22}^{-1/2}S\Lambda_{22}^{-1/2} \succ 0$).
3. **$\mu \le 1$.** Since $\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12} \succeq 0$, we have
   $S = \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12} \preceq \Lambda_{22}$, hence
   $\Lambda_{22}^{-1/2}S\Lambda_{22}^{-1/2} \preceq I$ and $\mu \le 1$.
4. **Conclusion.** From 2 and 3, $\mu \in (0, 1]$, so $1 - \mu \in [0, 1)$, which is C1. The
   largest $\lvert 1-\mu\rvert$ comes from the smallest $\mu$, which is C2. $\square$
5. **Where equality occurs.** $\mu = 1$ $\iff$ $\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ vanishes
   in that direction $\iff$ that degree of freedom of robot B **is touched by no inter-robot
   measurement at all**. The error in that direction disappears in exactly one round
   ($1-\mu = 0$). This is why the measured $\mathrm{spec}(\Lambda_{22}^{-1}S)$ has a maximum of
   exactly $1.0000000000$ and $\mathrm{spec}(M)$ a minimum of $0$.

**Delete a hypothesis**: dropping positive definiteness from H1 (a surviving gauge, with only
relative measurements) makes $\Lambda_{11}$ singular so the first line of (2) is not even defined —
**without an anchor the distributed solver does not run either** (the same story as the "delete a
hypothesis" of R3 in `c5-factor-graphs-map`). Dropping symmetry breaks the similarity argument of
step 2 and $\mu$ can become complex, so $\rho(M) < 1$ is no longer guaranteed. With three or more
blocks, (9) takes a block triangular form that depends on the ordering — it still converges when
$\Lambda\succ0$ (Ostrowski-Reich) but the closed form (3) for the rate is lost.

### R1' — the structure of the ADMM convergence theorem

**Hypotheses** H1: $f_1, f_2$ are closed proper convex. H2: the unaugmented Lagrangian
$f_1(u)+f_2(v)+y^\top(u-v)$ has a saddle point $(u^\ast, v^\ast, y^\ast)$.
**Conclusions** C1: $u^k - v^k \to 0$. C2: $f_1(u^k)+f_2(v^k) \to p^\ast$. C3: $y^k \to y^\ast$.

**Strategy**: show that the Lyapunov function
$V^k = \tfrac1\rho\lVert y^k - y^\ast\rVert^2 + \rho\lVert v^k - v^\ast\rVert^2$ decreases at every
iteration and that the decrease bounds the squared residual.

1. **Optimality conditions.** At the saddle point of H2, $u^\ast = v^\ast$,
   $-y^\ast \in \partial f_1(u^\ast)$ and $y^\ast \in \partial f_2(v^\ast)$.
2. **First-order conditions of the iteration.** Read
   $-\rho(u^{k+1}-v^k+w^k) \in \partial f_1(u^{k+1})$ and its counterpart off each $\arg\min$ of
   (1), then substitute the $w$ update to express them through $y^{k+1}$.
3. **The convexity inequality.** Applying monotonicity of the subdifferential
   ($\langle \partial f(a)-\partial f(b), a-b\rangle \ge 0$) to the expressions of steps 1 and 2
   yields $V^k - V^{k+1} \ge \rho\lVert u^{k+1}-v^{k+1}\rVert^2
   + \rho\lVert v^{k+1}-v^k\rVert^2$.
4. **Summability gives convergence.** $V^k \ge 0$ and decreasing, so the series on the right
   converges and each term goes to zero — which is C1 and $v^{k+1}-v^k \to 0$. C2 and C3 follow.
5. **Why there is no rate.** Step 3 gives only a **lower bound on the decrease**, not a decrease
   proportional to $V^k$. Obtaining a form $V^{k+1} \le (1-c)V^k$ requires strong convexity of
   $f_i$ (or metric subregularity) — which is why the rate can be written **exactly** for the
   quadratic problem of R2 but not for general convex problems.

**Delete a hypothesis**: dropping the saddle point of H2 (an infeasible constraint, or an optimum
of $-\infty$) breaks step 1 and $y^k$ can diverge. Dropping closedness from H1 can make the
$\arg\min$ unattained. And **raising the block count to three** invalidates the inequality of step 3,
with known divergent counterexamples — the refutation of the common belief that "ADMM does not care
how many blocks there are".

(Omitted: the expansion of the inequality in step 3. `boyd2011-admm` Appendix A.)

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★, R3')** Write the four steps of R3' with no missing steps, then (a) show that the
product of two positive definite matrices has positive real eigenvalues via a similarity
transformation, (b) characterize exactly the "where equality occurs" of step 5, and (c) bound
$\rho(M)$ using only the **eigenvalues** of $\Lambda_{22}$ and $S$.
*Strategy and key inequality*: (a) uses
$\Lambda_{22}^{-1}S \sim \Lambda_{22}^{-1/2}S\Lambda_{22}^{-1/2}$, similar to a symmetric positive
definite matrix. For (c),
$\lambda_{\min}(\Lambda_{22}^{-1}S) \ge \lambda_{\min}(S)/\lambda_{\max}(\Lambda_{22})$ gives
$\rho(M) \le 1 - \lambda_{\min}(S)/\lambda_{\max}(\Lambda_{22})$ — a loose bound, but what matters
is that **each robot can compute it from its own block** (a distributable bound). The expansion is
hidden.

**P2 (proof, ★★★, R1')** Derive the step-3 inequality
$V^k - V^{k+1} \ge \rho\lVert u^{k+1}-v^{k+1}\rVert^2 + \rho\lVert v^{k+1}-v^k\rVert^2$ of R1'.
(b) Then argue that if $f_1, f_2$ are $m$-strongly convex one obtains a form
$V^{k+1} \le (1-c)V^k$, and write $c$ in terms of $m$ and $\rho$ (the exact constant is not
required). (c) Describe in a paragraph the **structure** of a known divergent three-block ADMM
counterexample.
*Strategy*: (a) applies subdifferential monotonicity twice and collects terms using the $w$ update.
(c) passes if it notes that a cycle appears when the three constraint matrices are not linearly
independent (citing a concrete $3\times3$ counterexample is excellent). The expansion is hidden.

**P3 (derivation, ★★, R2)** Derive the $T(\rho)$ of (6) from (5) with no missing steps, then show
(a) $\rho(T) \to 1$ as $\rho\to0$ and (b) as $\rho\to\infty$, and (c) argue from that for the
existence of an interior minimum. (d) For the symmetric split
$\Lambda_1 = \Lambda_2 = \tfrac12\Lambda$, find $\rho(T)$ in closed form through the eigenvalues of
$\Lambda$.
*Solution sketch*: (d) is the crux — under the symmetric split
$A_1 = A_2 = (\tfrac12\Lambda+\rho I)^{-1}$ and $T$ decomposes into $2\times2$ blocks in the
eigenbasis of $\Lambda$, so one computes the spectral radius of a $2\times2$ matrix per eigenvalue
$\lambda$ and takes the maximum. Minimizing that over $\rho$ puts the optimal $\rho$ on the order of
the **geometric mean of the extreme eigenvalues** of $\Lambda$ — the same kind of result as the
$2/(\lambda_2+\lambda_n)$ of R2 in `s5-graph-consensus`.

**P4 (numerical, ★, R3·R3'·R4)** On the two-robot pose graph of the reproduction task, find (a) the
predicted and measured $\rho(M)$, (b) whether $\lambda_{\min}(\Lambda_{22}^{-1}S)$ and
$1-\lambda_{\min}$ agree with $\rho(M)$, (c) the rounds needed to reach
$10^{-2}, 10^{-4}, 10^{-6}, 10^{-8}$, and (d) the table of $\rho(M)$ against the inter-robot edge
count.
*Answer*: (a) predicted $0.96860653$, measured $0.96860641$ (relative error $1.2\times10^{-7}$).
(b) $\lambda_{\min} = 0.0313934719$ and $1-\lambda_{\min} = 0.9686065281 = \rho(M)$ (difference
$2.0\times10^{-15}$); further, the maximum of $\mathrm{spec}(\Lambda_{22}^{-1}S)$ is exactly $1.0$
and the minimum of $\mathrm{spec}(M)$ is $0$. (c) $44, 186, 330, 475$ rounds. (d) the table of R4
($0.98968495 / 0.96860653 / 0.95420678 / 0.00466476$). Tolerance $10^{-6}$.
Check it: confirm first that both $\Lambda$ and $S$ are positive definite (smallest eigenvalue
> 0) — if not, the anchor is missing and (2) is not even defined.

**P5 (implementation, ★★★, R3·R4)** Implement (a) block Gauss-Seidel and (b) full-copy two-block
ADMM and compare them on the same problem. (c) Then attach a **nonlinear** outer loop (Gauss-Newton
outside, Gauss-Seidel inside) and compare the total cost (outer iterations $\times$ inner rounds)
for inner round counts of $1, 3, 10, \infty$.
*Rubric*: (a) and (b) satisfy acceptance criteria 1 and 3 and report the per-round communication
volume (number of doubles); (c) presents the trade-off as a numerical table — cutting inner rounds
raises outer iterations — and must show that **the minimum total communication is not at inner
$= \infty$**; (d) sweeps ADMM's $\rho$ on a grid to find the optimum and matches the prediction of
(6) to within 1%.

**P6 (counterexample, ★★, R4·R5)** (a) Show with the reproduction task's table that "sharing more
inter-robot measurements makes distributed optimization better" is false. (b) Convert accuracy and
round count into the **same unit** (for instance the total communication needed to reach a target
ATE) and show numerically that the optimal amount of sharing is interior. (c) Explain why "it
converged distributedly, therefore it is globally optimal" is false, using the certificate of R3 in
`c5-robust-global-estimation`.
*Property checklist*: (a) just uses the monotone increase of $\rho(M)$. (b) is the crux — the two
axes must be folded into one cost before "the optimum is interior" can be said, and the conversion
(bytes per round × rounds) must be stated. (c) must point out that "the unique solution of the
linearized problem" is not "the global minimum of the original non-convex problem".

**P7 (paper, ★★, R3·R5)** Read §IV-V of `choudhary2017-distributed-slam` and §III-V of
`tian2021-distributed-certifiable`, then (a) state in one sentence each **what each computes
distributedly and what it guarantees**, (b) say what exactly Choudhary et al.'s "privacy" claim
hides (and what it does not), and (c) say how Tian et al.'s certificate corresponds to the
$S \succeq 0$ of R3 in `c5-robust-global-estimation`.
*Rubric*: (a) passes if it separates Choudhary's "distributed solution of the linearized (or
two-stage) pose graph" from Tian's "distributed solution of the rank-relaxed problem plus a
distributed certificate of global optimality". (b) is excellent if it points out that the separator
pose increments are still exposed. (c) is excellent if it says what doing the positive
semidefiniteness check distributedly requires (a distributed computation of the smallest
eigenvalue).

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read with 3-pass and attack questions 4, 5, 6 and 7 on the third pass.

1. **Boyd, Parikh, Chu, Peleato & Eckstein, "Distributed optimization and statistical learning
   via the alternating direction method of multipliers" (2011, Foundations and Trends in ML)** —
   role: `standard`. <https://doi.org/10.1561/9781601984616> (§3, §7)
   Extra questions: (a) list separately the assumptions the §3.2 convergence theorem uses and the
   ones it **does not**. (b) is the consensus ADMM form of §7 the same as the full-copy form of R2
   here, or different? (c) what do the authors say, and not say, about choosing $\rho$?
2. **Choudhary, Carlone, Nieto, Rogers, Christensen & Dellaert, "Distributed mapping with privacy
   and communication constraints" (2017, IJRR)** — role: `standard`.
   <https://arxiv.org/abs/1702.03435> (§IV-V)
   Extra questions: (a) is the authors' distributed Gauss-Seidel the same as (2) here, or does the
   separator handling differ? (b) in what units do they report communication, and can it be
   compared against (10) here? (c) how does the two-stage decomposition (rotations first, then
   poses) affect the rate?
3. **Tian, Khosoussi, Rosen & How, "Distributed certifiably correct pose-graph optimization"
   (2021, IEEE T-RO)** — role: `seminal`.
   <https://doi.org/10.1109/TRO.2021.3072346> (§III-V)
   Extra questions: (a) what exactly is the **certificate** the authors compute distributedly?
   (b) is the convergence guarantee of Riemannian block coordinate descent the same kind as R3'
   here? (c) how does the number of communication rounds scale with the number of robots?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) the independent and dependent variables and the baselines — were they tuned fairly?
(6) does the metric match the claim, and are variance and seeds reported? (7) what is missing for
reproduction? (8) if the result were wrong, which assumption would you doubt first?
(9) computational and memory complexity, and real-time feasibility. (10) what would you change to
surpass it in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one laptop CPU core, under two minutes in total,
under 300 MB. Only numpy (the largest matrix is $300\times300$).

**The input data** is produced by the generator below (fixed seed, deterministic). No external
dataset is needed. Use the residual and Jacobians of (15) and (16) of the
`c5-factor-graphs-map` reproduction task unchanged.

```python
"""s5-distributed-optimization reproduction task: a two-robot pose graph generator."""

import numpy as np

SEED = 20261112
SIG_ODOM = np.array([0.02, 0.02, 0.01])
SIG_INTER = np.array([0.05, 0.05, 0.02])
SIG_ANCHOR = np.array([1e-3, 1e-3, 1e-3])


def wrap(a):
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def rot(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])


def between(xi, xj):
    return np.array([*(rot(xi[2]).T @ (xj[:2] - xi[:2])), wrap(xj[2] - xi[2])])


def make_two_robot(n=25, radius=5.0, inter_every=5, seed=SEED):
    """Two robots on offset circular tracks, with odometry and inter-robot measurements.

    Pose indices 0..n-1 are robot A and n..2n-1 are robot B. The only anchor is on A's pose 0.
    """
    rng = np.random.default_rng(seed)
    ang = np.linspace(0.0, 1.6 * np.pi, n)
    gt_a = np.column_stack([radius * np.cos(ang), radius * np.sin(ang), wrap(ang + np.pi / 2)])
    gt_b = np.column_stack(
        [radius * np.cos(ang) + 2.0, radius * np.sin(ang) + 1.0, wrap(ang + np.pi / 2 + 0.3)]
    )
    gt = np.vstack([gt_a, gt_b])
    edges = [(i, i + 1, SIG_ODOM) for i in range(n - 1)]
    edges += [(n + i, n + i + 1, SIG_ODOM) for i in range(n - 1)]
    inter = [(i, n + i, SIG_INTER) for i in range(0, n, inter_every)]
    edges += inter
    meas = [between(gt[i], gt[j]) + s * rng.standard_normal(3) for i, j, s in edges]
    return gt, edges, np.array(meas), n, len(inter)
```

**What to do.** (a) Linearize with the Jacobians of `c5-factor-graphs-map` to build $\Lambda$ and
$\eta$ (the anchor on A's pose 0, weights $1/\sigma$). The linearization point is **per-robot dead
reckoning** — each robot accumulates only its own odometry from its own anchor (A from true pose 0,
B from true pose $n$). (b) Compute the centralized solution
$\delta^\ast = \Lambda^{-1}\eta$. (c) Split the blocks by pose index as $I_1 = \{0..3n-1\}$ and
$I_2 = \{3n..6n-1\}$ (state dimension $3\cdot2n = 150$).

**Part A — block Gauss-Seidel.** Run (2) for 4000 rounds and record the
$\lVert\cdot\rVert_\infty$ error against $\delta^\ast$. Measure the asymptotic rate from a
**two-point slope in a late window** ($k_1 = 200$, $k_2 = 400$) as the exponential of
$\big(\log e_{k_2} - \log e_{k_1}\big)/(k_2-k_1)$ (too late and it drowns in machine precision — see
the diagnosis table). Compare against the prediction $\rho(M)$.

**Part B — the Schur complement identity.** Build
$S = \Lambda_{22}-\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$, compute
$\mathrm{spec}(\Lambda_{22}^{-1}S)$ and verify (3).

**Part C — ADMM.** Split the edges by owner to build $\Lambda_1, \eta_1$ (A's odometry plus the
anchor) and $\Lambda_2, \eta_2$ (B's odometry plus the inter-robot measurements), asserting
$\Lambda_1+\Lambda_2 = \Lambda$, then implement the ADMM of (5) and (6). Sweep $\rho$ over
`np.geomspace(1.0, 1e5, 41)` to find the minimizer of $\rho(T)$ from (6), and run 3000 iterations
at that $\rho$ and at $\rho=1$ and $\rho=10^5$.

**Part D — coupling strength against rate.** Vary `inter_every` over $2, 5, 10, 25$ and find
$\rho(M)$, the inter-robot edge count and the separator size for each.

**Acceptance criteria — all four conditions must hold.**

1. **Part A** — 50 poses (25+25), 53 edges (48 odometry + 5 inter-robot), state dimension 150, and
   $\kappa(\Lambda) = 1.105\times10^{6}$. The prediction $\rho(M) = 0.96860653$ and the measurement
   agree to a **relative error $< 10^{-5}$** (reference measurement $0.96860641$,
   $1.2\times10^{-7}$). The round counts are $10^{-2}$:44, $10^{-4}$:186, $10^{-6}$:330,
   $10^{-8}$:475, with an error of $1.5\times10^{-15}$ after 4000. **Agreeing with the centralized
   solution to within $10^{-4}$ takes 186 rounds** — the point at which the blueprint's requirement
   is met. Tolerances: round counts $\pm3$, error to an order of magnitude.
2. **Part B** — confirm $\Lambda \succ 0$ and $S \succ 0$, that
   $\mathrm{spec}(\Lambda_{22}^{-1}S) \subset (0, 1]$ with $\lambda_{\min} = 0.0313934719$ and
   $\lambda_{\max} = 1.0000000000$ (tolerance $10^{-8}$), and that
   $\lvert\rho(M) - (1-\lambda_{\min})\rvert < 10^{-12}$ (reference $2.0\times10^{-15}$) with
   $\min\mathrm{spec}(M) = 0$ (tolerance $10^{-12}$).
3. **Part C** — $\Lambda_1+\Lambda_2 = \Lambda$ and $\eta_1+\eta_2 = \eta$ hold, and on the grid
   the minimum of $\rho(T)$ is $0.979669$ at $\rho = 56.23$ (tolerance $10^{-5}$ / 1%). At that
   $\rho$ the error after 3000 iterations is $3.1\times10^{-14}$ and $10^{-4}$ is reached in 377
   rounds. At $\rho = 1$ and $\rho = 10^5$ the predictions are $0.999552$ and $0.999991$ and the
   errors after 3000 iterations are $4.4\times10^{-3}$ and $1.1\times10^{-1}$, so $10^{-4}$ is
   **never reached**. The measured rate **brackets** the prediction $0.979669$ depending on the
   window, from $0.9745$ (iterations 300-600) to $0.9814$ (900-1500) — within 1% of the prediction
   passes. And report that **Gauss-Seidel wins on both the round count (186 against 377) and the
   per-round volume (30 against 150 doubles).**
4. **Part D** — reproduce the table below (tolerance $10^{-6}$).

   | `inter_every` | inter-robot edges | separator | $\rho(M)$ |
   |---|---|---|---|
   | 2 | 13 | 26 | $0.98968495$ |
   | 5 | 5 | 10 | $0.96860653$ |
   | 10 | 3 | 6 | $0.95420678$ |
   | 25 | 1 | 2 | $0.00466476$ |

   State that it is **monotonically increasing**, and report that $\rho(M)$ drops to $0.005$ with a
   single edge.

**Baselines**: (a) the baseline for Part A is the centralized solution $\Lambda^{-1}\eta$. (b) The
baseline for Part C is the Gauss-Seidel of Part A — **that ADMM loses is the measurement**. (c) The
baseline for Part D is the `inter_every=5` row. Optional: linearize at the ground truth instead of
per-robot dead reckoning and confirm that $\rho(M)$ barely changes (the coupling is set by
**structure**, not by values), which makes the meaning of R3' clear.

**Numbers to report**: every value of the four criteria, plus the total communication at the moment
Part A reaches $10^{-4}$ (reference $186 \times 30 = 5580$ doubles) and at $10^{-6}$ (reference
$330 \times 30 = 9900$).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The measured Part A rate is exactly $1.0$ | the window is so late that the error is already at machine precision | print the error sequence and check it exceeds $10^{-8}$ at $k_1$, pulling $k_1$ back to 200 |
| The measured Part A rate is smaller than predicted | the window is too early — the slow mode does not yet dominate | sweep $k_1$ from 100 to 400 and check the value converges to the prediction |
| `solve` fails because $\Lambda_{11}$ is singular | no anchor was added, so a gauge survives | print $\lambda_{\min}(\Lambda)$; zero means the anchor is missing |
| $\mathrm{spec}(\Lambda_{22}^{-1}S)$ is complex in Part B | $\Lambda$ was assembled asymmetrically | print $\lVert\Lambda-\Lambda^\top\rVert_\infty$ |
| The Part B $\lambda_{\max}$ exceeds 1 | $S$ was formed against $\Lambda_{22}$ instead of $\Lambda_{11}$ | verify $S \preceq \Lambda_{22}$ through the eigenvalues |
| The Part C assertion fails | an inter-robot edge went into both sides, or the anchor was added twice | check that the edges were **partitioned** by owner with no duplication |
| Part C improves as $\rho$ grows | $T(\rho)$ was assembled wrongly (the dual update sign) | check that $\rho(T) \to 1$ at $\rho = 10^5$ |
| Part D is not monotone | the seed was changed along with `inter_every` | fix the generator's `seed` and vary only `inter_every` |

## Open problems

- **(Open problem) A partition that reduces communication volume and round count together** — the
  measurements of R4 show the two axes worsening **in the same direction** (sharing more raises both
  the per-round volume and the number of rounds). Graph partitioning theory addresses only the
  separator side and does not put the convergence rate in the objective. Current approach: the
  two-stage decomposition and block-ordering heuristics of
  [distributed SLAM](https://arxiv.org/abs/1702.03435). What is missing: a formulation of the
  robot-pose partitioning problem with **both $\rho(M)$ and $\lvert\mathcal{S}\rvert$ in the
  objective**, with an approximation ratio.
- **(Open problem) Distributed pose graphs under asynchronous and lossy communication** — (2) and
  (9) assume synchronous rounds and lossless links. Convergence theory exists for asynchronous
  block coordinate descent, but the rate is unknown for the case of **large blocks with structural
  coupling** such as a pose graph. Current approach: convergence proofs under conservative delay
  bounds, plus engineering retries. What is missing: a bound from the delay and loss distribution to
  an effective rate playing the role of $\rho(M)$ (this continues into
  `s5-comms-constrained-estimation`).
- **(Open problem) Quantifying privacy** — the claim "being distributed means the raw data is never
  handed over" coexists with the fact that separator increments are exposed. There is no
  quantitative analysis of how much of a peer's trajectory and observations can be reconstructed
  from many rounds of separator increments. Current approaches: the qualitative discussion of
  [the privacy and communication constraints paper](https://arxiv.org/abs/1702.03435), and
  differential privacy from other fields. What is missing: an **attack model and a leakage bound**
  for what distributed SLAM actually transmits.

## Concept check

Run `rc quiz s5-distributed-optimization`. The quiz is for **concept checking only**; the real work
is the problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

The five items cover: which assumption the ADMM convergence theorem does not use; the error
iteration matrix of block Gauss-Seidel; why it always converges when $\Lambda \succ 0$; whether
sharing more inter-robot measurements speeds convergence; and what distributed convergence to the
centralized solution actually guarantees.

## How to study this stage

1. **Derive (1) from (4) by hand (45 min)** — confirm directly that completing the square produces
   the $w = y/\rho$ form. The point is to see the structure "alternate minimization plus dual
   ascent".
2. **(9) from a blank page (30 min)** — three lines, subtracting the optimality condition from (8).
   It is the shortest and most-used derivation in this lesson.
3. **Memorize the four lines of R3' (45 min)** — the single line $M = I - \Lambda_{22}^{-1}S$ plus
   the two inequalities ($S\succ0$, $S\preceq\Lambda_{22}$) are all of it. Re-solving problem P2 of
   `c5-factor-graphs-map` to own $S\succ0$ makes this lesson easy.
4. **Run Parts A and B first (60 min)** — see the measured rate match the prediction to $10^{-7}$,
   then see Part B's $1-\lambda_{\min}$ give the same number. The moment the two routes agree is
   the evidence you understood R3'.
5. **See the trade-off in Part D (30 min)** — print the table yourself, from $\rho(M) = 0.005$ at
   one edge to $0.990$ at thirteen. The conclusion "share more and it is slower" is
   counter-intuitive, so pin it down with numbers.
6. **Do Part C last (60 min)** — assemble $T(\rho)$ and sweep $\rho$ for the optimum. See that both
   $\rho=1$ and $\rho=10^5$ are slow, confirming the interior minimum. Then write into the report
   that ADMM loses to Gauss-Seidel **on both axes**.
7. **Read the papers asking "what is being done distributedly" (150 min)** — check the assumptions
   precisely in Boyd et al. §3.2 and the consensus form in §7, see the actual decomposition of
   distributed SLAM in Choudhary et al. §IV-V, and see what **distributing the certificate** means
   in Tian et al. §III-V. Write the one-page note per paper **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the three open problems and write a
   paragraph. The partitioning problem that puts volume and rounds in one objective is directly
   motivated by Part D's table.

**Passing bar**: you can derive (1), (9) and the four lines of R3' from a blank page, you can say
why $\rho(M)$ equals $1-\lambda_{\min}(\Lambda_{22}^{-1}S)$, you have code that satisfies all four
conditions of the reproduction task, and you have notes on all three papers.
