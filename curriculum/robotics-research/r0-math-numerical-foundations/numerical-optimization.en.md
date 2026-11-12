---
id: r0-numerical-optimization
lang: en
title: Numerical optimization - Newton, quasi-Newton, SQP
summary: >-
  Prove the quadratic convergence of Newton's method, derive the secant condition behind BFGS, and
  see how line search and trust regions deliver global convergence. Connects through to the SQP and
  interior-point structure for constrained problems.
objectives:
  - Prove the local quadratic convergence of Newton's method together with its assumptions.
  - Derive the BFGS update from the secant condition and a least-change principle.
  - Explain the structure by which line search (Armijo, Wolfe) and trust regions give global convergence.
  - Write the relation between Gauss-Newton and Levenberg-Marquardt from a trust-region viewpoint.
  - Say how SQP and interior-point methods solve the KKT conditions numerically.
tags: [optimization, newton, quasi-newton, sqp, research]
---

# Numerical optimization - Newton, quasi-Newton, SQP

## Setup and notation

| Symbol | Meaning |
|---|---|
| $f: \mathbb{R}^n \to \mathbb{R}$ | the objective, of class $C^2$ |
| $g_k = \nabla f(x_k)$, $H_k = \nabla^2 f(x_k)$ | gradient and Hessian |
| $p_k$ | search direction; $\alpha_k$ the step length |
| $B_k$ | the quasi-Newton Hessian approximation, $B_k \approx H_k$ |
| $s_k = x_{k+1}-x_k$, $y_k = g_{k+1}-g_k$ | step and gradient change |
| $\Delta_k$ | trust-region radius |

Assumed: `r0-convex-optimization` (KKT, duality) and `r0-linear-algebra-decompositions` (conditioning).

## Key results

- **R1 (quadratic convergence of Newton's method) [D3]** — if $x^\star$ is a local minimum with
  $\nabla f(x^\star)=0$, $H(x^\star) \succ 0$ and $H$ Lipschitz (constant $L$), then for $x_0$
  close enough,

$$
\lVert x_{k+1}-x^\star\rVert \le \frac{L}{2\sigma_{\min}(H^\star)}\lVert x_k-x^\star\rVert^2 . \tag{1}
$$

- **R2 (BFGS and the secant condition) [D2]** — a quasi-Newton approximation must satisfy the
  **secant condition** $B_{k+1}s_k = y_k$, and among those the update that is symmetric positive
  definite while **changing least** from the previous approximation is BFGS:

$$
B_{k+1} = B_k - \frac{B_ks_ks_k^\top B_k}{s_k^\top B_k s_k} + \frac{y_ky_k^\top}{y_k^\top s_k}. \tag{2}
$$

  Positive definiteness is preserved when $y_k^\top s_k > 0$ (the curvature condition).
- **R3 (global convergence of line search) [D1]** — choosing steps satisfying Armijo (sufficient
  decrease) and the curvature (Wolfe) condition, with directions satisfying an angle condition
  against the gradient, gives $\lVert g_k\rVert \to 0$ (Zoutendijk's theorem). The proof is cited
  **[D0]** (Nocedal-Wright Theorem 3.2).
- **R4 (LM = trust-region Gauss-Newton) [D2]** — in least squares the Gauss-Newton direction solves
  $(J^\top J)p = -J^\top r$, and the Levenberg-Marquardt system
  $(J^\top J+\lambda I)p = -J^\top r$ is the solution of the subproblem constrained to a trust
  region, with **$\lambda$ corresponding to the radius $\Delta$**. Damping is therefore not
  arbitrary regularisation but **step-length control**.
- **R5 (SQP and interior point solve KKT) [D1]** — SQP linearises the KKT conditions at each
  iteration and solves a QP subproblem; interior-point methods relax complementary slackness to
  $\lambda_i f_i = -\mu$ and drive $\mu \to 0$. **Both are ways of numerically tracking the KKT
  conditions** of R4.

## Derivation

### R1 — quadratic convergence (sketch in the proof section)

The Newton step is $p_k = -H_k^{-1}g_k$. Where it comes from: expanding $f$ to second order,

$$
f(x_k+p) \approx f(x_k) + g_k^\top p + \tfrac12 p^\top H_k p ,
$$

and differentiating the right-hand side in $p$ and setting it to zero gives $H_kp = -g_k$. So
**Newton's method goes to the minimiser of the quadratic model**, and converges as fast as that
model is accurate. The quadratic rate (1) follows from the Taylor remainder being
$O(\lVert x_k-x^\star\rVert^2)$.

**Where the assumption breaks**: without $H_k \succ 0$ the step $p_k$ need not be a descent
direction (near a saddle point). Practice therefore does one of: (a) modify $H_k$ (modified
Cholesky); (b) use a trust region; (c) use $J^\top J$ instead of $H$ (Gauss-Newton, always positive
semidefinite). Also, forming and factorising $H_k$ costs $O(n^3)$, so at scale one uses
quasi-Newton or CG.

### R2 — the secant condition and BFGS

$B_{k+1}$ must be **consistent with what has already been seen**. From the mean value theorem for
gradients,

$$
y_k = g_{k+1}-g_k = \left(\int_0^1 H(x_k+ts_k)\,dt\right)s_k \approx H_{k+1}s_k ,
$$

so the approximation should satisfy $B_{k+1}s_k = y_k$ — the secant condition. With
$n(n+1)/2$ unknowns and only $n$ equations there are **infinitely many solutions**. BFGS takes

$$
B_{k+1} = \arg\min_B \lVert B - B_k\rVert_W \quad \text{s.t. } B = B^\top,\ Bs_k = y_k
$$

(a weighted Frobenius norm), and computing it yields (2) (omitted: the choice of weighting norm and
the algebra — Nocedal-Wright §6.1).

**What the curvature condition means**: $y_k^\top s_k > 0$ says "the gradient increased along the
step", i.e. **the curvature in that direction is positive**. When it fails (a non-convex region)
positive definiteness is not preserved and the update must be skipped or damped. A line search
satisfying the Wolfe curvature condition guarantees it **automatically** — which is why the two
components come as a pair.

### R4 — why LM is a trust region

The trust-region subproblem is $\min_p \tfrac12\lVert r + Jp\rVert^2$ subject to
$\lVert p\rVert \le \Delta$. Applying the Lagrange conditions (KKT, from the previous lesson),

$$
(J^\top J + \lambda I)p = -J^\top r, \qquad \lambda \ge 0,\quad \lambda(\lVert p\rVert-\Delta) = 0 ,
$$

so **the $\lambda$ of LM is the dual variable of the trust-region constraint**. By complementary
slackness: if the constraint is inactive ($\lVert p\rVert<\Delta$) then $\lambda=0$ and the step is
pure Gauss-Newton; if active then $\lambda>0$ and the step shortens.

**Practical consequence**: "it only works if I raise $\lambda$" means **one of two things** —
(a) you are in a region where the quadratic model is poor (normal; the trust region should be
small), or (b) $J^\top J$ is structurally singular (over-parameterisation or gauge deficiency —
`c1-manifold-optimization` R4 and R5). Without distinguishing them you will raise the damping forever.

## Proof sketch

### R1 — local quadratic convergence of Newton's method

**Hypotheses** H1: $f \in C^2$ with $H$ Lipschitz (constant $L$) near $x^\star$.
H2: $H^\star \succ 0$. H3: $x_k$ is close enough. **Conclusion** C: (1).

**Strategy**: turn the error of the Newton step into a Taylor remainder and bound it with the norm
of $H^{-1}$.

1. With $e_k := x_k - x^\star$,
   $e_{k+1} = e_k - H_k^{-1}g_k = H_k^{-1}\big(H_ke_k - g_k\big)$.
2. $g_k = g_k - g^\star = \int_0^1 H(x^\star+te_k)e_k\,dt$ (mean value theorem, $g^\star=0$).
3. Combining 1 and 2,
   $e_{k+1} = H_k^{-1}\int_0^1\big(H_k - H(x^\star+te_k)\big)e_k\,dt$.
4. The Lipschitz condition gives
   $\lVert H_k - H(x^\star+te_k)\rVert \le L(1-t)\lVert e_k\rVert$, so the integral is bounded by
   $\tfrac{L}{2}\lVert e_k\rVert^2$.
5. For $x_k$ close enough, continuity gives $\lVert H_k^{-1}\rVert \lesssim 1/\sigma_{\min}(H^\star)$,
   which yields (1). C.

**Delete a hypothesis**: without H2 the $\lVert H_k^{-1}\rVert$ of step 5 blows up and convergence
is not guaranteed — which is why Newton's method **diverges or converges to a saddle** near a
saddle point. Without H3 there is no global convergence: Newton is a local method and globality
comes from line search or trust regions (R3).

**Comparison with Gauss-Newton**: in least squares $H = J^\top J + \sum_i r_i\nabla^2 r_i$, and
Gauss-Newton discards the second term. Near zero residual that term is small, so convergence is
**close to quadratic**; with large residuals it drops to linear — the same structure as (3) in R3
of `c1-manifold-optimization`.

## Problem set

★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Derive the secant condition from the mean value theorem and count, for
$n=2$, how many degrees of freedom remain among symmetric $B$ satisfying it.
*Solution sketch*: a symmetric $2\times2$ has 3 degrees of freedom and the secant condition imposes
2 equations, leaving 1. Choosing that 1 by a "least change" criterion is BFGS.

**P2 (derivation, ★★, R4)** Derive the LM equation from the KKT conditions of the trust-region
subproblem and show that $\lambda$ is a monotone decreasing function of $\Delta$.
*Solution sketch*: increasing $\lambda$ decreases $\lVert p(\lambda)\rVert$ (the eigenvalues of
$(J^\top J+\lambda I)^{-1}$ shrink), so each $\Delta$ corresponds to a unique $\lambda$.

**P3 (proof, ★★★, R1)** Write the proof of R1 with no gaps, and quantify "close enough" in step 5
(within what radius does it hold?).
*Solution sketch*: use the Lipschitz condition to find the radius on which
$\lVert H_k^{-1}\rVert \le 2/\sigma_{\min}(H^\star)$, then state the condition making the
coefficient of (1) less than one there.

**P4 (numerical, ★, R1)** Apply Newton's method to $f(x)=x^4$ from $x_0=1$: compute $x_1, x_2, x_3$
and determine the order of convergence.
*Answer*: $x_{k+1} = x_k - \frac{4x_k^3}{12x_k^2} = \tfrac23 x_k$, so $x_1 = 0.666\ldots$,
$x_2 = 0.444\ldots$, $x_3 = 0.296\ldots$ — **linear** convergence with ratio 2/3. Tolerance
$10^{-9}$. **Why not quadratic**: at $x^\star=0$, $H^\star = 12x^{\star2} = 0$, so H2 fails.

**P5 (implementation, ★★, R1·R2·R3)** Implement (a) gradient descent, (b) BFGS and (c) Newton on
the Rosenbrock function and compare iteration counts and convergence orders, using Armijo line
search throughout.
*Rubric*: (a) all three use the same stopping test and the same line search; (b) the convergence
order is **estimated** from the slope of $\log\lVert e_{k+1}\rVert$ against
$\log\lVert e_k\rVert$ and reported (near 1, ~1.6, 2); (c) Newton is shown to fail where $H$ is
indefinite, and a modification is applied.

**P6 (counterexample, ★★, R1·R4)** Construct one example where Newton's method (a) converges to a
saddle point and one where it (b) diverges. Then show that LM damping fixes (a) but **does not fix
gauge deficiency**.
*Property checklist*: (a) is $f(x,y)=x^2-y^2$ from an arbitrary start; (b) is something like
$f(x)=\sqrt{1+x^2}$ from a far start. Gauge deficiency leaves a **structural** null space in
$J^\top J$, so raising $\lambda$ leaves the solution in that direction arbitrary.

## Paper reading

**The textbook exception applies** (lesson standard §5). Read the following and write two one-page
notes (fixed questions 1, 3, 4 and 8).

1. **Nocedal & Wright, ch.3 and ch.6** — line search and quasi-Newton. Questions: (a) write what
   each half of the Wolfe conditions prevents (too long a step? too short?). (b) how do the authors
   characterise BFGS as the "least-change" update, and what justifies the weighting norm?
2. **Nocedal & Wright, ch.18 or 19** — SQP or interior point. Questions: (a) write one paragraph on
   how your chosen method tracks the KKT conditions numerically. (b) what does the way feasibility
   is handled (interior point stays interior, SQP does not) mean for safety constraints in robotics?

**One methodological source**: Boyd & Vandenberghe ch.9-11 — the same algorithms from the convex viewpoint.

## Reproduction task

**Tier R2 (re-implementation).** Budget: under two minutes on a laptop CPU, numpy only. All four
conditions must pass.

1. **Separating the convergence orders**: record the error sequences $\lVert e_k\rVert$ of gradient
   descent, BFGS and Newton on Rosenbrock and estimate the order from the slope of
   $\log\lVert e_{k+1}\rVert$ against $\log\lVert e_k\rVert$. The result should be **about 1 for
   gradient descent, 1.2-1.8 (superlinear) for BFGS and about 2 for Newton** (each ±0.3).
2. **Preserving the secant condition**: confirm your BFGS satisfies
   $\lVert B_{k+1}s_k - y_k\rVert < 10^{-10}$ at every iteration, and that it skips the update on
   iterations where the curvature condition $y_k^\top s_k > 0$ fails.
3. **LM = trust region**: on a least-squares problem, (a) vary $\lambda$ directly and confirm
   $\lVert p(\lambda)\rVert$ decreases monotonically, and (b) bisect for the $\lambda$
   corresponding to a given $\Delta$, matching $\lVert p\rVert = \Delta$ to within $10^{-8}$.
4. **When H2 fails**: confirm numerically that Newton converges **linearly** on $f(x)=x^4$ (P4) and
   that the estimated order is near 1 (confirming that quadratic convergence depends on
   $H^\star \succ 0$).

**Baseline**: compare iteration counts with `BFGS` and `trust-ncg` in
`scipy.optimize.minimize`, and confirm your LM solution agrees with
`least_squares(method='lm')` to within $10^{-8}$.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| Newton's order is not 2 | $H^\star$ is singular (as in P4) or the line search is cutting steps | print the smallest eigenvalue of $H$ and the $\alpha_k$ |
| BFGS diverges | the update was not skipped when the curvature condition failed | print $y_k^\top s_k$ every iteration |
| LM does not match the trust region | $\lambda$ and $\Delta$ were paired arbitrarily, without complementary slackness | pair them by the bisection of condition 3(b) |
| the order estimate is unstable | errors near machine precision were included in the regression | regress only over the range $\lVert e_k\rVert > 10^{-12}$ |

## Open problems

- **(Open) Second-order information for large non-convex problems** — Newton-rate convergence is
  attractive but forming and factorising $H$ is prohibitive at robotics scale. The convergence
  guarantees of **cheap second-order information** exploiting sparsity and low rank (Hessian-free,
  L-BFGS variants) are only partially known.
- **(Open) Quasi-Newton for non-smooth objectives** — robust costs (Huber, truncated) and contact
  weaken the justification of the curvature and secant conditions. The IRLS and damping heuristics
  robotics uses are largely empirical (the same item as the open problem of `c1-manifold-optimization`).
- **(Open) Stopping criteria under real-time constraints** — MPC must use the iterate it has when
  time runs out. Ways of quantifying the **guarantees of an early-stopped solution**
  (sub-optimality, stability) are limited (connecting to the real-time iteration of C4).

## Concept check

Run `rc quiz r0-numerical-optimization` (add `--lang en` for the English text). It is for concept
checking only.

The four items cover: which assumption is **not** needed for Newton's quadratic convergence; the
name of the quasi-Newton condition; the precise interpretation of the LM damping parameter; and
whether damping can cure gauge deficiency.

## How to study this stage

1. **See Newton as "the minimiser of the quadratic model" (30 min)** — derive it by differentiating
   the second-order expansion rather than memorising the formula. That view carries into
   Gauss-Newton, LM and SQP alike.
2. **Separate the convergence orders on a plot (90 min)** — do condition 1 of the reproduction task
   first. Once slopes 1, 1.6 and 2 separate visually, the theory reads as explanation.
3. **See an example where H2 fails (40 min)** — P4 and condition 4. Confirming numerically "what
   breaks when an assumption breaks" is the working method of the whole research track.
4. **Rewrite LM as KKT (60 min)** — the previous R0 lesson (KKT) is used directly here. If you
   thought of damping as arbitrary regularisation, this hour is the biggest gain of the lesson.
5. **Distinguish the two situations that "need damping" (50 min)** — solve P6. (a) a region where
   the quadratic model is poor (normal) and (b) a structural null space (gauge,
   over-parameterisation). Failing to distinguish them lands you in the same trap in
   `c1-manifold-optimization` and `c5-sparsity-isam`.
6. **Read the textbook as algorithm-design logic (120 min)** — Nocedal and Wright explain *why*
   each condition is demanded. If you can write what each half of the Wolfe conditions prevents,
   you have read it properly.

**Passing bar**: you can prove R1 on a blank page, can derive the secant condition, can explain LM
as trust-region KKT, and have code meeting all four acceptance conditions plus notes on both
textbook readings.
