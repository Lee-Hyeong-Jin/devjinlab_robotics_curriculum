---
id: r0-convex-optimization
lang: en
title: Convexity, duality and KKT
summary: >-
  Start from the definitions of convex sets and functions, construct the Lagrange dual, and treat
  weak and strong duality and the KKT conditions at the level of proof. Builds the instinct for
  reducing robotics problems to SOCP or SDP.
objectives:
  - State the definitions of convex sets and functions and apply the first- and second-order tests.
  - Construct the Lagrange dual function and prove weak duality.
  - Explain that strong duality holds under Slater's condition and say what the duality gap means.
  - Write the KKT conditions and show that for a convex problem they are necessary and sufficient for optimality.
  - Decide whether a robotics problem reduces to an LP, QP, SOCP or SDP.
tags: [optimization, convexity, duality, kkt, research]
---

# Convexity, duality and KKT

## Setup and notation

| Symbol | Meaning |
|---|---|
| $f_0, f_i, h_j$ | objective, inequality constraints, equality constraints |
| $\mathcal{D}$ | the problem domain; $p^\star$ the optimal value |
| $\lambda \ge 0$, $\nu$ | dual variables of the inequality and equality constraints |
| $L(x,\lambda,\nu)$ | the Lagrangian |
| $g(\lambda,\nu) = \inf_x L$ | the dual function; $d^\star$ the dual optimal value |
| $p^\star - d^\star$ | the duality gap |

Standard form: $\min f_0(x)$ subject to $f_i(x)\le 0$ and $h_j(x)=0$. Assumed:
`f0-calculus-multivariable` (gradients, Lagrange multipliers) and `r0-linear-algebra-decompositions`.

## Key results

- **R1 (tests for convexity) [D2]** — if $f$ is twice differentiable then $f$ is convex
  $\iff \nabla^2 f(x) \succeq 0$ throughout the domain. The first-order test is
  $f(y) \ge f(x) + \nabla f(x)^\top(y-x)$.
- **R2 (weak duality) [D3]** — for any $\lambda \ge 0$ and $\nu$,

$$
g(\lambda,\nu) \le p^\star, \qquad \text{hence}\quad d^\star \le p^\star. \tag{1}
$$

  **It holds even when the problem is not convex** — which is why the dual always gives a lower
  bound, and the basis of branch and bound.
- **R3 (strong duality and Slater's condition) [D1]** — for a convex problem satisfying
  **Slater's condition** (a strictly feasible point exists: some $x$ with $f_i(x) < 0$ and
  $h_j(x)=0$), $d^\star = p^\star$. The proof uses a separating hyperplane theorem and is cited
  here **[D0]** (Boyd-Vandenberghe §5.3.2).
- **R4 (the KKT conditions) [D3]** — for a differentiable problem, if
  $(x^\star,\lambda^\star,\nu^\star)$ is optimal and strong duality holds then

$$
\begin{aligned}
&f_i(x^\star)\le 0,\quad h_j(x^\star)=0 &&\text{(primal feasibility)}\\
&\lambda_i^\star \ge 0 &&\text{(dual feasibility)}\\
&\lambda_i^\star f_i(x^\star) = 0 &&\text{(complementary slackness)}\\
&\nabla f_0 + \textstyle\sum_i \lambda_i^\star\nabla f_i + \sum_j \nu_j^\star\nabla h_j = 0 &&\text{(stationarity)}
\end{aligned} \tag{2}
$$

  and **for a convex problem (2) is necessary and sufficient** for optimality.
- **R5 (the reduction hierarchy) [D1]** — LP ⊂ QP ⊂ SOCP ⊂ SDP. Reductions common in robotics:
  least squares and MPC → QP; friction cone constraints → SOCP; rotation relaxations and SOS → SDP.
  **Which level a problem fits decides the solver and the achievable scale.**

## Derivation

### R2 — weak duality

If $x$ is feasible for the primal and $\lambda \ge 0$, then from $f_i(x) \le 0$ and $h_j(x) = 0$,

$$
L(x,\lambda,\nu) = f_0(x) + \sum_i \lambda_i f_i(x) + \sum_j \nu_j h_j(x) \le f_0(x) .
$$

(The second sum is $\le 0$ since $\lambda_i \ge 0$ and $f_i \le 0$; the third is zero.) Hence for
**every** feasible $x$,

$$
g(\lambda,\nu) = \inf_{x'} L(x',\lambda,\nu) \le L(x,\lambda,\nu) \le f_0(x),
$$

where the first inequality holds because the infimum is over the **whole domain**, not only the
feasible points. Minimising over $x$ gives $g(\lambda,\nu) \le p^\star$, and maximising over
$\lambda,\nu$ gives (1).

**Why convexity is not needed**: the argument above **never used** convexity of $f_0$ or $f_i$ —
only the sign conditions and the definition of an infimum. That is why the dual bounds non-convex
problems from below, and it is the structure behind SE-Sync in `c5-robust-global-estimation`, which
obtains a **lower bound from a dual relaxation and then asks when it is tight**.

**Where the assumption breaks**: if $\inf_x L$ is $-\infty$ then $g$ gives no useful bound; the
domain of the dual function (the set of finite $(\lambda,\nu)$) has to be treated as well.

### R4 — deriving the KKT conditions (necessity)

Under strong duality, $f_0(x^\star) = g(\lambda^\star,\nu^\star)$. From the definition of $g$,

$$
f_0(x^\star) = \inf_x \Big(f_0(x) + \sum_i\lambda_i^\star f_i(x) + \sum_j \nu_j^\star h_j(x)\Big)
\le f_0(x^\star) + \sum_i \lambda_i^\star f_i(x^\star) + 0 \le f_0(x^\star),
$$

the last inequality from $\lambda^\star \ge 0$ and $f_i(x^\star)\le0$. The two ends agree, so
**both inequalities are equalities**, which yields two conclusions:

1. $\sum_i \lambda_i^\star f_i(x^\star) = 0$ with every term $\le 0$, hence **each term is zero** —
   complementary slackness.
2. $x^\star$ minimises $L(\cdot,\lambda^\star,\nu^\star)$, so if differentiable its gradient
   vanishes — stationarity.

**Sufficiency (in the convex case)**: given $(x,\lambda,\nu)$ satisfying (2), convexity makes
$L(\cdot,\lambda,\nu)$ convex, so stationarity means a global minimum and
$g(\lambda,\nu) = L(x,\lambda,\nu) = f_0(x)$ (the constraint terms vanish by complementary
slackness). Combined with weak duality, $x$ is optimal.

**How to read it**: complementary slackness says **only active constraints carry multipliers**. The
multiplier of an inactive constraint ($f_i<0$) must be zero. The CBF safety filter (C3) and contact
complementarity (C2) both have this structure.

## Proof sketch

### R1 — the second-order test

**Hypotheses** H1: $f$ is twice differentiable on an open convex set.
**Conclusion** C: $f$ is convex $\iff \nabla^2 f \succeq 0$.

**Strategy**: reduce to one dimension; convexity is equivalent to convexity along every line.

1. Setting $g(t) := f(x+tv)$, $f$ is convex $\iff g$ is convex for all $x, v$ (directly from the definition).
2. In one dimension $g$ is convex $\iff g'' \ge 0$ (the standard calculus result).
3. $g''(t) = v^\top\nabla^2 f(x+tv)v$, so this must be $\ge 0$ for all $v$, i.e.
   $\nabla^2 f \succeq 0$. C.
4. **Why the set must be open**: on a boundary, perturbing $t$ in both directions may leave the
   domain, which breaks step 2.

**Delete a hypothesis**: without twice differentiability (for example $\lVert x\rVert_1$) the
second-order test is unavailable and one must use the first-order test or the definition. Robust
costs in robotics (Huber) are differentiable but have a discontinuous second derivative, which
requires care.

## Problem set

★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** For the equality-constrained least squares $\min \lVert Ax-b\rVert^2$
subject to $Cx=d$, find the Lagrange dual function explicitly and show that the dual problem is
another least-squares problem.
*Solution sketch*: minimising $L$ over $x$ gives $x = (A^\top A)^{-1}(A^\top b - C^\top\nu/2)$, and
substituting back leaves a quadratic in $\nu$.

**P2 (derivation, ★★, R5)** Show that the friction cone constraint
$\lVert f_t\rVert_2 \le \mu f_n$ is a **second-order cone**, and write a contact-force
optimization with that constraint in SOCP standard form.
*Solution sketch*: an SOC is $\{(z,t): \lVert z\rVert_2 \le t\}$; taking $z = f_t$ and
$t = \mu f_n$ matches exactly. The contact dynamics of C2 use this reduction.

**P3 (proof, ★★★, R4)** Prove the **sufficiency** of KKT for a convex problem in full (the sketch
above, with no gaps). Give one example where sufficiency fails for a non-convex problem.
*Solution sketch*: sufficiency closes with weak duality plus stationarity plus complementary
slackness. For the non-convex counterexample, construct a saddle point satisfying KKT without being optimal.

**P4 (proof, ★★, R2)** Identify exactly where convexity is *not* used in the weak-duality argument,
and explain why the dual can therefore serve as a **lower bound** for a non-convex problem. What
decides whether a dual relaxation such as SE-Sync is "tight"?
*Rubric*: a pass notes checking numerically whether $p^\star - d^\star = 0$ (the duality gap), or
inspecting a rank condition on the relaxed solution.

**P5 (numerical, ★, R4)** Find the KKT solution of $\min x^2 + y^2$ subject to $x + y \ge 2$.
*Answer*: writing the constraint as $2 - x - y \le 0$, stationarity gives $2x = \lambda$ and
$2y = \lambda$ so $x=y$; the active constraint $x+y=2$ gives $x=y=1$ and $\lambda = 2$, with
optimal value 2. Tolerance $10^{-9}$. Check both $\lambda \ge 0$ and complementary slackness.

**P6 (implementation, ★★, R2·R4)** Generate a random convex QP and (a) solve the primal directly,
(b) solve the dual, (c) confirm the duality gap is numerically zero, and (d) check each of the four
KKT conditions numerically.
*Rubric*: (a) includes both equality and inequality constraints; (b) the dual function is obtained
analytically, not by a numerical infimum; (c) the gap is at most $10^{-8}$; (d) complementary
slackness is checked term by term, printing the active/inactive classification.

## Paper reading

**The textbook exception applies** (lesson standard §5). Read Boyd and Vandenberghe as the primary
source and write two one-page notes (fixed questions 1, 3, 4 and 8).

1. **Boyd & Vandenberghe, ch.2-3 (convex sets and functions)** — questions: (a) summarise what the
   authors offer as the way to **recognise** convexity (the operations that preserve it). (b) what
   principle lets disciplined convex programming (DCP) decide convexity mechanically?
2. **Boyd & Vandenberghe, ch.5 (duality)** — questions: (a) separate the assumptions needed for
   weak and for strong duality. (b) explain, with a robotics example, the interpretation the authors
   give dual variables (sensitivity, shadow price). (c) does the book give an example where strong
   duality fails?

**One methodological source**: the DCP rules in the [CVXPY documentation](https://www.cvxpy.org/) —
a tool for deciding mechanically whether something can be written convexly.

## Reproduction task

**Tier R1 (numerical check).** Budget: under one minute on a laptop CPU, numpy/scipy (optionally
cvxpy). All four conditions must pass.

1. **Zero duality gap**: generate a random convex QP ($n=20$, 3 equalities, 10 inequalities) so
   that Slater's condition holds, compute the primal and dual optimal values, and confirm
   $|p^\star - d^\star| < 10^{-8}$.
2. **The four KKT conditions**: for the solution of 1, check primal feasibility, dual feasibility,
   complementary slackness and stationarity numerically, classify active and inactive constraints,
   and show that **the multipliers of inactive constraints are at most $10^{-8}$**.
3. **Weak duality even when non-convex**: build the same shape of problem with a non-convex
   objective (e.g. $x^\top Qx$ with indefinite $Q$) and confirm $g(\lambda) \le p^\star$ for 100
   random $\lambda\ge0$, where $p^\star$ is the global minimum found by grid search.
4. **Violating Slater's condition**: deliberately construct a problem with no strictly feasible
   point and exhibit a **non-zero duality gap** (or confirm numerically that a gap appears).

**Baseline**: solving the same QP with `cvxpy` must agree on the optimal value to within $10^{-8}$
(if installable); also compare with SLSQP in `scipy.optimize.minimize`.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| the duality gap is non-zero | Slater's condition is violated, or the dual function is computed wrongly | find and print a strictly feasible point; if none exists you are in case 4 |
| multipliers of inactive constraints are large | the active/inactive threshold is wrong | print $f_i(x^\star)$ alongside $\lambda_i$ and inspect the pairs |
| the stationarity residual is large | the constraint sign convention ($f_i \le 0$) was mixed | check that all constraints were normalised to the $\le 0$ form |
| condition 3 fails | $p^\star$ was taken as a local minimum | widen the grid-search range or use multiple starts to confirm the global minimum |

## Open problems

- **(Open) Tight relaxations of non-convex robotics problems** — the dual always gives a lower
  bound (R2), but the classification of **which problem structures admit a tight relaxation** is
  partial. It is known for pose graphs (SE-Sync) and point-cloud registration (TEASER) but does not
  extend to trajectory optimization with contact (C4) or to IK (C1).
- **(Open) Convex solvers under real-time constraints** — kHz-rate QP solvers for MPC are mature,
  but ways to achieve real-time performance at SOCP or SDP scale are limited. Handling friction
  cones (SOCP) in real time requires approximations, and how much guarantee those approximations
  cost is not quantified.
- **(Open) Convex structure over learned models** — neural dynamics are non-convex, so control
  cannot be written as a convex problem. How much expressive power is sacrificed by
  convexity-preserving model structures (such as input-convex neural networks) is unsettled.

## Concept check

Run `rc quiz r0-convex-optimization` (add `--lang en` for the English text). It is for concept
checking only.

The four items cover: whether weak duality needs convexity; what complementary slackness means;
the reduction level of a friction cone; and the status of KKT for a convex problem.

## How to study this stage

1. **Prove weak duality on a blank page (40 min)** — it is three lines. Then confirm that
   **convexity is used nowhere**. That observation leads to certifiable estimation in C5.
2. **Remember KKT as "two inequalities becoming equalities" (60 min)** — rewriting the derivation
   shows complementary slackness and stationarity emerging from **the same line**. Do not memorise
   the four conditions separately.
3. **Practise reductions (60 min)** — classify five robotics constraints (joint limits, friction
   cones, torque limits, collision avoidance, rotation constraints) into LP/QP/SOCP/SDP. P2 is that exercise.
4. **See the duality gap numerically (90 min)** — do conditions 1 and 4 of the reproduction task
   together. Watching a gap appear when Slater's condition fails imprints that strong duality is
   not free.
5. **Build judgement with CVXPY's DCP (40 min)** — tweak expressions to pass and fail DCP. It
   trains the mechanical decision of "can this be written convexly", used directly in MPC design in C4.
6. **Read the textbook for the interpretation of dual variables (120 min)** — the sensitivity
   (shadow price) reading in ch.5 translates in control into "which constraint dominates the cost".
   That view recurs in C4 and S2.

**Passing bar**: you can prove weak duality and the necessity of KKT on a blank page, can classify
robotics constraints by reduction level, and have code meeting all four acceptance conditions plus
notes on both textbook readings.
