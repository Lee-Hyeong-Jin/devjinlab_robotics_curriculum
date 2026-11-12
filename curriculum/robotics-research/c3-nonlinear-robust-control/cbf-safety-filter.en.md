---
id: c3-cbf-safety-filter
lang: en
title: CBF and CLF safety filters
summary: >-
  How a control barrier function guarantees forward invariance of a safe set, proved with the
  comparison lemma, and the closed form of the minimum-intervention QP filter derived from the KKT
  conditions. Higher-order (exponential) CBFs handle constraints of relative degree two or more,
  and where the guarantee **collapses** once input limits enter is measured numerically. It ends
  with the undesired equilibria a CBF-QP creates.
objectives:
  - Give a proof sketch, via the comparison lemma, that the CBF condition makes the safe set forward invariant.
  - Derive the closed-form solution of the single-constraint minimum-intervention QP from the KKT conditions and show it passes the nominal control through when inactive.
  - Build the exponential CBF chain for a relative-degree-two constraint and write the explicit input bound for a double integrator.
  - Measure numerically the region where the QP becomes infeasible under input limits and write that condition as a formula.
  - Explain the mechanism by which a CBF-QP creates equilibria that are not the goal.
tags: [nonlinear-control, control-barrier-function, safety, quadratic-program, research]
---

# CBF and CLF safety filters

## Setup and notation

Every earlier lesson of this module was about **converging to a goal**. This one is about a
different demand: **there are regions you must never enter.** Convergence and safety are different
properties (safety is invariance, not stability), and in practice one separates "the controller
that performs" from "the filter that keeps you safe". What makes that separation possible is the
control barrier function (CBF) and its QP filter.

Assumed: the comparison lemma and invariant sets from `c3-lyapunov-stability`, the KKT conditions
of convex optimisation (`r0-convex-optimization`), and Lie derivatives and relative degree (R2 of
`c3-feedback-linearization`).

| Symbol | Meaning |
|---|---|
| $\dot x = f(x) + g(x)u$ | affine in the input, $f, g$ locally Lipschitz |
| $h : \mathbb{R}^n\to\mathbb{R}$ | the safety function; the safe set is $\mathcal{C} = \{x : h(x)\ge0\}$ |
| $\alpha$ | an extended class-$\mathcal{K}$ function ($\alpha(0)=0$, strictly increasing, defined on $\mathbb{R}$) |
| $L_fh, L_gh$ | $\nabla h^\top f$ and $\nabla h^\top g$ (the latter a row vector) |
| $u_{\text{nom}}(x,t)$ | the nominal (performance) control |
| $u^\star$ | the control after filtering |
| $\psi_0, \psi_1,\dots$ | the higher-order CBF chain, $\psi_0 = h$, $\psi_{i+1} = \dot\psi_i + \alpha_{i+1}(\psi_i)$ |
| $u_{\max}$ | the input magnitude limit |

The running example is the double integrator $\ddot x = u$ with the wall constraint
$x \le x_{\max} = 1$. It matters because $h = x_{\max} - x$ has **relative degree two**
($L_gh = 0$), so the first-order CBF theory does not apply as written — and every joint-limit and
collision constraint on a robot has that shape.

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (CBF and forward invariance) [D3]** — if $\nabla h \ne 0$ on the boundary of
  $\mathcal{C}$ and a locally Lipschitz control $u(x)$ satisfies, with an extended class-
  $\mathcal{K}$ function $\alpha$,
  $$
  \dot h(x) = L_fh(x) + L_gh(x)u(x) \;\ge\; -\alpha\big(h(x)\big), \tag{1}
  $$
  then $\mathcal{C}$ is **forward invariant**: $x(0)\in\mathcal{C} \Rightarrow x(t)\in\mathcal{C}$
  as long as the solution exists. The proof is one line of the comparison lemma.
- **R2 (the minimum-intervention QP filter and its closed form) [D2]** — with one constraint and
  no input limits, the solution of
  $$
  u^\star = \arg\min_u \tfrac12\lVert u - u_{\text{nom}}\rVert^2
    \;\;\text{s.t.}\;\; L_fh + L_ghu + \alpha(h) \ge 0 \tag{2}
  $$
  is **closed form**:
  $$
  u^\star = u_{\text{nom}} + \frac{\big[-\lambda\big]_+}{\lVert L_gh\rVert^2}\,L_gh^\top,
    \qquad \lambda := L_fh + L_ghu_{\text{nom}} + \alpha(h), \tag{3}
  $$
  so when the constraint is **inactive ($\lambda \ge 0$) the nominal control passes through
  exactly**, and when active the filter pushes minimally along $L_gh$. Numerically: over 1500
  random instances (3) differs from a QP solver by $6.1\cdot10^{-7}$ (solver tolerance), and in the
  inactive cases $\lVert u^\star - u_{\text{nom}}\rVert = 0$.
- **R3 (higher-order, exponential CBFs) [D2]** — when $L_gh \equiv 0$, (1) is unusable. With the
  chain $\psi_0 = h$, $\psi_1 = \dot\psi_0 + \alpha_1(\psi_0)$ and the constraint
  $\dot\psi_1 + \alpha_2(\psi_1)\ge0$, the intersection $\mathcal{C}_0\cap\mathcal{C}_1$
  (with $\mathcal{C}_i = \{\psi_i\ge0\}$) is forward invariant. For the double integrator with
  linear $\alpha_i$ the constraint becomes an **explicit input bound**:
  $$
  u \;\le\; -(\alpha_1+\alpha_2)\,\dot x + \alpha_1\alpha_2\,(x_{\max}-x). \tag{4}
  $$
- **R4 (feasibility and input limits) [D2]** — (2) is always feasible when $L_gh \ne 0$. But
  ⓐ with $L_gh = 0$ and $L_fh + \alpha(h) < 0$ it is **infeasible**, and ⓑ adding
  $\lVert u\rVert\le u_{\max}$ makes the constraint unsatisfiable wherever the bound in (4) drops
  below $-u_{\max}$. Numerically ($\alpha_1=\alpha_2=3$, $x_{\max}=1$, nominal $u\equiv10$): at
  $u_{\max}=2$, 95 of 189 runs saturate and **safety is violated** (worst
  $\min_t h = -0.138$); at $u_{\max}=5$, 2 of 183 saturate with no violation; at $u_{\max}=20$
  there is no saturation.
- **R5 (undesired equilibria created by a CBF-QP) [D1]** — filtering a CLF-based controller through
  a CBF-QP can create **asymptotically stable equilibria that are not the goal**, on the boundary
  where the barrier constraint is active (Reis, Aguiar & Tabuada 2021). Safety holds but the task
  never finishes — the price of separating safety from performance.

## Derivation

### R2 — the closed form of the minimum-intervention QP

(2) is a convex QP in $u \in \mathbb{R}^m$ with one constraint. Writing the Lagrangian

$$
\mathcal{L}(u,\mu) = \tfrac12\lVert u - u_{\text{nom}}\rVert^2
  - \mu\big(L_fh + L_ghu + \alpha(h)\big), \qquad \mu \ge 0,
$$

the KKT conditions are ⓐ stationarity
$\nabla_u\mathcal{L} = u - u_{\text{nom}} - \mu L_gh^\top = 0$, ⓑ complementarity
$\mu\big(L_fh+L_ghu+\alpha(h)\big) = 0$, ⓒ feasibility, and ⓓ $\mu\ge0$.

**Step 1.** From ⓐ, $u = u_{\text{nom}} + \mu L_gh^\top$ — the solution can only move along
$L_gh$, because the objective is the Euclidean distance.

**Step 2.** Substituting into the constraint,

$$
L_fh + L_gh\big(u_{\text{nom}} + \mu L_gh^\top\big) + \alpha(h)
  = \lambda + \mu\lVert L_gh\rVert^2,
$$

where $\lambda := L_fh + L_ghu_{\text{nom}} + \alpha(h)$ is the **margin of the nominal control**.

**Step 3 (two cases).** If $\lambda \ge 0$ then $\mu = 0$ satisfies ⓑ, ⓒ and ⓓ, so
$u^\star = u_{\text{nom}}$ — the nominal control **passes through unchanged**. If $\lambda < 0$
then $\mu = 0$ violates the constraint, so by ⓑ the constraint must be active with equality and
$\mu = -\lambda/\lVert L_gh\rVert^2 > 0$. Together these give (3).

**Step 4 (continuity).** $\lambda$ is a continuous function of $x$ and $[\cdot]_+$ is Lipschitz, so
on any region where $L_gh$ is bounded away from zero, $u^\star(x)$ is Lipschitz — which is how the
"locally Lipschitz control" required by R1 is obtained. **As $\lVert L_gh\rVert \to 0$ the
denominator of (3) vanishes and that property fails** (case ⓐ of R4).

**Numerical check**: over 1500 random $(u_{\text{nom}}, L_gh, L_fh, \alpha(h))$ with input
dimension 1-3, the largest componentwise difference between (3) and the CLARABEL QP solution is
$6.1\cdot10^{-7}$, and in the cases with $\lambda>0$ the quantity
$\lVert u^\star - u_{\text{nom}}\rVert_\infty$ is **exactly zero**.

### R3 — a relative-degree-two constraint: the exponential CBF

Take the double integrator $\dot x_1 = x_2$, $\dot x_2 = u$ with $h = x_{\max}-x_1$. Since
$\nabla h = (-1, 0)$, we have $L_gh = 0$ — $u$ **does not appear** on the left of (1). With a
first-order CBF, no control can affect the constraint at all.

**Step 1 (build the chain).** With $\psi_0 := h = x_{\max}-x_1$ we get $\dot\psi_0 = -x_2$, and we
promote what the first-order condition would require, $\dot\psi_0 + \alpha_1(\psi_0) \ge 0$, into a
**new safety function**:

$$
\psi_1 := \dot\psi_0 + \alpha_1(\psi_0) = -x_2 + \alpha_1(x_{\max}-x_1). \tag{5}
$$

**Step 2 (where $u$ appears).** Now $\dot\psi_1$ contains $u$:

$$
\dot\psi_1 = -u - \alpha_1'(\psi_0)\,x_2 \;\xrightarrow{\ \alpha_i(s)=\alpha_is\ }\; -u - \alpha_1 x_2.
$$

So the second-order condition $\dot\psi_1 + \alpha_2(\psi_1) \ge 0$ reads

$$
-u - \alpha_1x_2 + \alpha_2\big(-x_2 + \alpha_1(x_{\max}-x_1)\big) \ge 0
  \iff u \le -(\alpha_1+\alpha_2)x_2 + \alpha_1\alpha_2(x_{\max}-x_1),
$$

which is (4). The constraint **reduces to a single upper bound on the input**, so the filter is one
line: $u^\star = \min\{u_{\text{nom}},\ \text{bound}\}$ (equivalent to (3) for a scalar input).

**Step 3 (the scope of the invariance).** The second-order condition keeps $\psi_1 \ge 0$, and
$\psi_1\ge0$ in turn gives $\dot\psi_0 \ge -\alpha_1(\psi_0)$ through (5), which by R1 keeps
$\psi_0 \ge 0$. So what is invariant is $\mathcal{C}_0\cap\mathcal{C}_1$, and **the initial state
must lie in both**. Even far from the wall, **too large a velocity** means $\psi_1 < 0$ and you are
outside the guarantee — that is the practical restriction of higher-order CBFs, and
$\alpha_1\alpha_2$ is the number that sets the "braking distance".

**Numerical check**: with $\alpha_1 = \alpha_2 = 3$, $x_{\max}=1$ and a nominal control
$u_{\text{nom}}(t) = c + A\sin\omega t$ (random $c\in[-2,4]$, $A\in[0.5,5]$, $\omega\in[0.5,4]$),
integrating 295 random initial conditions inside $\mathcal{C}_0\cap\mathcal{C}_1$ for $T=12$ with
$\Delta t = 10^{-4}$ gives a **worst $\min_t h$ of $+1.4\cdot10^{-13}$** (no violation), and at
times when the constraint is inactive the maximum of
$\lvert u^\star - u_{\text{nom}}\rvert$ is **exactly zero**.

**Where the assumptions break**: raising $\alpha_i$ loosens the bound and so touches the nominal
control less, but it shrinks $\mathcal{C}_1$ (the admissible velocity range), making it **easier to
start outside the guarantee**. Lowering them widens the guaranteed region but makes the filter
conservative. There is no automatic answer to that trade, and input limits make it worse (R4).

### R4 — feasibility: it breaks in two different ways

**ⓐ A direction control cannot reach.** The constraint in (2) is
$L_gh u \ge -L_fh - \alpha(h)$. If $L_gh = 0$ the left side does not depend on $u$, so in any state
with $L_fh + \alpha(h) < 0$ **no $u$ whatsoever** satisfies it. Higher-order CBFs (R3) defer the
problem down a chain, and if $u$ still fails to appear at the last step (lack of controllability)
the constraint was impossible from the start.

**ⓑ Input limits.** Adding $\lvert u\rvert \le u_{\max}$ to (2) narrows the feasible set to
$\{u : L_ghu \ge -L_fh-\alpha(h)\} \cap \{\lVert u\rVert_\infty \le u_{\max}\}$, and on the double
integrator the intersection empties the moment the bound in (4) falls below $-u_{\max}$:

$$
-(\alpha_1+\alpha_2)x_2 + \alpha_1\alpha_2(x_{\max}-x_1) < -u_{\max}. \tag{6}
$$

Where (6) holds, even **maximum braking** cannot satisfy the constraint. **Numerical check**
(nominal $u\equiv10$, starting inside $\mathcal{C}_0\cap\mathcal{C}_1$ with $x_2(0)\in[0,2]$):

| $u_{\max}$ | saturation (infeasible) | worst $\min_t h$ |
|---|---|---|
| 2 | **95** of 189 | $-0.138$ (**safety violated**) |
| 5 | 2 of 183 | $0.0000$ |
| 20 | 0 of 188 | $0.0000$ |

As $u_{\max}=2$ shows, **once saturation occurs the guarantee is gone**. There are three
prescriptions: ⓘ shrink the safe set **in advance** to account for the input limits
(input-constrained CBFs), ⓘⓘ construct an invariant set numerically from the trajectories of a
backup controller (backup CBFs), or ⓘⓘⓘ lower $\alpha_i$ to match the input limit (at the price of
a conservative filter). None is free, and that is the open problem of this lesson.

## Proof sketch

### R1 — why the CBF condition gives forward invariance

**Hypotheses** H1: $\mathcal{C} = \{h\ge0\}$ with $h \in C^1$ and $\nabla h\ne0$ on
$\partial\mathcal{C}$. H2: $u(\cdot)$ is locally Lipschitz and (1) holds on a neighbourhood of
$\mathcal{C}$. H3: $\alpha$ is a locally Lipschitz extended class-$\mathcal{K}$ function.
**Conclusion** C: $x(0)\in\mathcal{C} \Rightarrow x(t)\in\mathcal{C}$ on the maximal interval of
existence.

**Strategy**: the comparison lemma. Compare $h$ along the trajectory with a scalar ODE and show
only that **its solution cannot go below zero**.

1. Put $\eta(t) := h(x(t))$; H2 gives $\dot\eta \ge -\alpha(\eta)$ for almost every $t$.
2. Consider the comparison ODE $\dot y = -\alpha(y)$ with $y(0) = \eta(0) \ge 0$. By H3 the
   solution exists and is unique, and since $\alpha(0)=0$, $y\equiv0$ is a solution. Hence any
   solution with $y(0)\ge0$ satisfies $y(t)\ge0$ for all $t$ (uniqueness forbids **crossing**
   zero).
3. The comparison lemma (Khalil Lemma 3.4) gives $\eta(t) \ge y(t) \ge 0$, i.e. $h(x(t))\ge0$.
4. So $x(t)\in\mathcal{C}$. (The condition $\nabla h\ne0$ on the boundary is the geometric premise
   that makes $\mathcal{C}$ a regular set, so that "touching the boundary" is distinguished from
   "crossing it" — it connects to Nagumo's condition.)

**Remove a hypothesis**: drop the Lipschitz property of $\alpha$ in H3 and uniqueness in step 2
fails, so $y$ can cross zero (as with $\dot y = -\sqrt{y}$) and the conclusion is false. Drop the
Lipschitz control in H2 and existence and uniqueness of solutions go, so step 1 never starts —
which is why it matters **whether the QP filter's solution is Lipschitz** (step 4 of R2). Dropping
$\nabla h \ne 0$ in H1 admits degenerate sets where $h$ is tangent at the boundary and invariance
can fail. Finally, **this theorem gives no stability**: it says only that you stay inside
$\mathcal{C}$, nothing about reaching a goal (R5).

Technical steps omitted: the proof of the comparison lemma and the forward-completeness assumption.
Khalil Lemma 3.4, Ames et al. 2017 §II.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Write the KKT conditions of (2) with **two** constraints and express
the solution in terms of $L_gh_1, L_gh_2$ when both are active. What happens if the two gradients
are parallel and mutually contradictory?
*Solution sketch*: substituting $u = u_{\text{nom}} + \mu_1L_gh_1^\top + \mu_2L_gh_2^\top$ into
both equalities gives a $2\times2$ linear system whose condition is invertibility of the Gram
matrix $[L_gh_iL_gh_j^\top]$. Parallel and contradictory gradients make it singular and the
feasible set empty, so the QP is infeasible.

**P2 (derivation, ★★, R3)** For a relative-degree-three constraint, add one more link to the chain
($\psi_2$) and show that with linear $\alpha_i(s) = \alpha_is$ the whole condition is a linear
combination of $h$ and its derivatives. Say how to read those coefficients as roots of a
characteristic polynomial.
*Solution sketch*: expanding $\psi_2 = \dot\psi_1 + \alpha_2\psi_1$ gives
$h^{(3)} + (\alpha_1+\alpha_2+\alpha_3)\ddot h + \dots \ge 0$, whose coefficients are those of
$\prod(s+\alpha_i)$. So the $\alpha_i$ are "poles of the safety margin" — the reason
Nguyen & Sreenath call it an exponential CBF.

**P3 (numerical, ★, R3·R4)** With $\alpha_1=\alpha_2=3$ and $x_{\max}=1$, find ⓐ the input bound
of (4) at $x=(0,1)$, ⓑ the same at $x=(0.9,\ 1.5)$, ⓒ the smallest $u_{\max}$ for which (6) does
not hold in state ⓑ.
*Answers*: ⓐ $-(3+3)(1) + 9(1-0) = 3$ ⓑ $-6(1.5) + 9(0.1) = -8.1$
ⓒ $u_{\max} \ge 8.1$ (tolerance $10^{-9}$). Check: state ⓑ has
$\psi_1 = -1.5+3(0.1) = -1.2 < 0$, so it is already **outside** $\mathcal{C}_1$ — a negative bound
is normal outside the guaranteed region.

**P4 (implementation, ★★, R2·R3)** Compare the closed form (3) with a QP solver on the same inputs,
implement the double-integrator safety filter and pass the four acceptance criteria of the
reproduction task. Then tabulate, for $\alpha_1=\alpha_2 \in \{1,3,10\}$, ⓐ the mean deviation
from the nominal control and ⓑ the area of $\mathcal{C}_1$.
*Rubric*: ⓐ larger $\alpha$ reduces the deviation while ⓑ the guaranteed region shrinks — the
trade must be shown **numerically** ⓒ the deviation in inactive intervals is exactly zero ⓓ halving
$\Delta t$ does not change the sign of $\min_t h$.

**P5 (counterexample, ★★★, R4·R5)** ① Find an initial condition where input limits break safety
and explain it with (6), and ② construct an example where the CBF-QP creates an equilibrium that is
not the goal (a point where the filtered control is zero while the barrier constraint is active).
*Property checklist*: ① report the time of saturation together with the value of the left side of
(6) ② at the equilibrium verify $f + gu^\star = 0$ with $h = 0$ or $\psi_1 = 0$, and decide by
linearisation whether it is **asymptotically stable**. Showing a trajectory where "safety holds but
the task never finishes" completes it.

**P6 (paper, ★★, R1·R4)** From the Ames et al. 2019 survey, summarise in three sentences each
ⓐ why extended class-$\mathcal{K}$ functions are used (how they differ from class-$\mathcal{K}$),
ⓑ the robust CBF formulation under model error, ⓒ the prescriptions in the section on input limits.
Then pick one that can be verified with this lesson's reproduction task and write the verification
procedure.
*Rubric*: noting "the extension is defined for $h<0$ too, so it can speak about **returning** from
outside the set" passes. Summarising a robust CBF as "shaving the margin by the worst-case
disturbance" earns extra credit.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes and attack questions 4, 5, 6, 7 in the third.

1. **Ames, Xu, Grizzle & Tabuada, "Control barrier function based quadratic programs for safety
   critical systems" (2017, IEEE T-AC; arXiv 2016)** — role: `seminal`.
   <https://arxiv.org/abs/1609.06408>
   §II and §III are R1 and R2 of this lesson.
   Extra questions: ⓐ When the authors put a CLF and a CBF **in the same QP**, how is the priority
   of safety over performance expressed (the role of the relaxation variable)? ⓑ Where is Lipschitz
   continuity of the QP solution guaranteed, and in which states does that assumption fail?
2. **Ames, Coogan, Egerstedt, Notomista, Sreenath & Tabuada, "Control barrier functions: theory and
   applications" (2019, ECC)** — role: `survey`. <https://arxiv.org/abs/1903.11199>
   Extra questions: ⓐ Summarise the open problems the survey lists about input limits and
   feasibility. ⓑ When the safe set is obtained by **learning**, what is the guarantee about?
3. **Nguyen & Sreenath, "Exponential control barrier functions for enforcing high relative-degree
   safety-critical constraints" (2016, ACC)** — role: `standard`.
   <https://doi.org/10.1109/ACC.2016.7524935>
   Extra questions: ⓐ What is it that "exponential" refers to being exponential? ⓑ Rewrite the
   effect of the pole choice ($\alpha_i$) on the guaranteed region and the conservatism in terms of
   (4) of this lesson.

**The ten fixed questions**: (1) which problem under which assumptions (2) what exactly earlier
work could not do (3) the core idea in one equation (4) what is guaranteed and **what is not**
(5) independent and dependent variables and baselines, fairly tuned (6) do the metrics match the
claim, are variance and seeds reported (7) what is missing for reproduction (8) the first
assumption to doubt if the result is wrong (9) computational and memory complexity and real-time
feasibility (10) what you would change to go beyond it in a year.

## Reproduction task

**Tier R2 (re-implementation).** Budget: laptop CPU under ten minutes, numpy plus one QP solver
(for the comparison in criterion 1). The target is the double integrator $\ddot x = u$ with the
wall $x \le 1$; there is no input data.

**Acceptance criteria (all four)**

1. **Comparison with the closed form**: over $10^3$ random
   $(u_{\text{nom}}, L_gh, L_fh, \alpha(h))$ with input dimension 1-3, (3) and the QP solver agree
   componentwise to within $10^{-5}$ (reference $6.1\cdot10^{-7}$), and in **every** inactive case
   ($\lambda>0$) $\lVert u^\star - u_{\text{nom}}\rVert_\infty = 0$ (**exactly** zero — it must come
   from the branch, not from a floating-point comparison).
2. **Zero constraint violation**: with $\alpha_1=\alpha_2=3$, at least 250 random initial
   conditions inside $\mathcal{C}_0\cap\mathcal{C}_1$ and random sinusoidal nominal controls,
   integrated for $T=12$ with $\Delta t \le 10^{-4}$, give $\min_t h \ge -10^{-9}$
   (reference: worst $+1.4\cdot10^{-13}$).
3. **Transparency when inactive**: in the same experiment, at every time when the constraint is
   inactive ($u_{\text{nom}} \le$ the bound of (4) $- 10^{-6}$),
   $\lvert u^\star - u_{\text{nom}}\rvert = 0$.
4. **The input-limit boundary**: add $\lvert u\rvert \le u_{\max}$ and report, for
   $u_{\max}\in\{2,5,20\}$, the fraction of runs that saturate and the worst $\min_t h$. At
   $u_{\max}=2$ a **safety violation must occur** (reference: 95 of 189 runs saturate, worst
   $\min_t h = -0.138$) and at $u_{\max}=20$ there must be no saturation. Print the left side of (6)
   at the moment of violation to confirm the cause.

**Baselines**: ⓐ the nominal control alone (no filter), which must cross the wall from the same
initial conditions (the control group showing what the filter actually prevents); ⓑ naive clipping
$u = \min(u_{\text{nom}}, 0)$, which still crosses the wall when the velocity is already large;
ⓒ the reference numbers of criteria 1, 2 and 4.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| $\min_t h$ is slightly negative, around $-10^{-6}$ | integration error (the constraint is a continuous-time condition) | halve $\Delta t$ and see whether the violation shrinks proportionally — if it does, it is the integrator |
| Criterion 3 fails (deviation even when inactive) | projecting onto the bound always instead of taking a $\min$ | put the $\lambda \ge 0$ branch in explicitly (the $[\cdot]_+$ of (3)) |
| Large violation that is independent of $\Delta t$ | the run started outside $\mathcal{C}_1$ (initial velocity too large) | check $\psi_1 \ge 0$ when generating initial conditions — always |
| Saturation even at $u_{\max}=20$ | sign error in (4) or in the $\alpha_1\alpha_2$ term | verify by hand that the bound at $x=(0,1)$ is 3 (P3ⓐ) |
| Closed form and QP solver differ by about $10^{-3}$ | solver tolerance, or the constraint sign reversed | start from a simple case with $L_gh$ fixed to a positive scalar |

## Open problems

- **(open problem) Feasibility under input limits** — as (6) showed, once saturation occurs the
  guarantee disappears. Current approaches: constructing the invariant set from a backup
  controller's trajectories
  ([backup CBFs, Chen, Jankovic, Santillo & Li 2021](https://doi.org/10.1109/CDC45484.2021.9683111)),
  and CBF synthesis that includes input limits. The gap: a general way to quantify the trade
  between real-time computation and the size of the guaranteed region — integrating the backup
  trajectory longer enlarges the region but costs more per step.
- **(open problem) The equilibria a CBF-QP creates, and finishing the task** — a safety filter can
  create undesired asymptotically stable equilibria on the boundary
  ([Reis, Aguiar & Tabuada 2021](https://doi.org/10.1109/LCSYS.2020.3004797)). Current approaches:
  reshaping the barrier (designing the boundary) or accounting for safety during planning. The gap:
  a constructive design that guarantees **safety and convergence together** (no general condition
  is known).
- **(open problem) Guarantees for a learned safety function** — learning $h$ from data weakens the
  guarantee to one about the learned model. Current approaches: learning CBFs from expert
  demonstrations ([Robey et al. 2020](https://arxiv.org/abs/2004.03315)) and the survey of learned
  certificates by [Dawson, Gao & Fan 2022](https://arxiv.org/abs/2202.11762). The gap: an explicit
  map from learning error to lost safety margin — the same wall as the open problems in
  `c3-lyapunov-stability` and `c3-contraction-incremental`.
- **(open problem) High relative degree together with contact** — joint limits and collision
  avoidance have relative degree two, but once contact occurs the dynamics are non-smooth and the
  derivatives in the $\psi$ chain do not exist. The gap: CBF theory for hybrid and non-smooth
  systems — the same wall appears in `c2-contact-dynamics` and `c4-contact-implicit-hybrid`.

## Concept check

Take it with `rc quiz c3-cbf-safety-filter`. The quiz is **for concept checking only**; the real
work is the problem set and the reproduction task above (`lesson-standard.md` §4). Four questions
ask: the key step in the forward-invariance proof; why the QP returns the nominal control exactly
when the constraint is inactive; the input bound that the exponential CBF gives for a double
integrator; and whether a CBF-QP still guarantees safety under input limits.

## How to study this stage

1. **Compress the proof to three lines (30 min)** — "comparison ODE, cannot cross zero, comparison
   lemma". That is all of R1. Then write one sentence on what breaks if $\alpha$ is not Lipschitz.
2. **Derive (3) from the KKT conditions yourself (40 min)** — one multiplier, so it finishes by
   hand. Once derived, "the filter pushes along $L_gh$ only when active" is visible in the formula.
3. **Meet relative degree by hand (40 min)** — confirm $L_gh = 0$ for $h = x_{\max}-x$ and see that
   a first-order CBF **can do nothing**. Only then build the chain (5).
4. **Run it without the filter first (40 min)** — run baselines ⓐ (no filter) and ⓑ (naive
   clipping) of the reproduction task **first** and watch the wall being crossed. See what has to be
   prevented before turning the filter on.
5. **Break the guarantee with input limits (60 min)** — criterion 4. Watch the violation at
   $u_{\max}=2$ and print the left side of (6) to confirm the cause. This is the step where
   **guarantees have premises** becomes a number.
6. **Tabulate the $\alpha$ trade (40 min)** — the extra part of P4. Larger $\alpha$ is more
   transparent but the guaranteed region shrinks. That table is the whole of safety-filter tuning.
7. **Read the papers for "the premises of the guarantee" (135 min)** — Ames 2017 is the
   formulation, Nguyen & Sreenath the higher-order extension, and the Ames 2019 survey a list of
   premises that fail. Write the one-page note per paper and note how you would measure one of the
   survey's open problems with this lesson's reproduction task.

**Passing bar**: you can derive the proof of R1 and formulas (3) and (4) from memory, write the
condition under which input limits break the guarantee both as a formula and as a number, and you
have code meeting all four acceptance criteria plus one-page notes on the three papers.

**Closing the module**: the six lessons of C3 repeated one structure six times — **a guarantee
comes with its assumptions**. Lyapunov demanded bounded sublevel sets, feedback linearisation
involutivity, contraction a uniform metric and geodesic convexity, passivity a passive environment,
adaptation persistent excitation, and CBFs input margin. It is no accident that every reproduction
task includes an experiment that **breaks** that assumption. From the next module,
`c4-pontryagin-indirect` onward, we start choosing the **optimal** one among the safe and stable
ones.
