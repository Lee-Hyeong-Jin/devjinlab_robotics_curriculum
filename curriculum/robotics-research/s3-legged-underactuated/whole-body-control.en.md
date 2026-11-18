---
id: s3-whole-body-control
lang: en
title: Whole-body control and hierarchical QPs
summary: >-
  The step that pushes the centroidal plan of the previous lesson down to joint commands. The
  classical way of respecting priorities when tasks conflict (null-space projection) is derived and
  its priority-preservation theorem proved; then **once inequality constraints enter, projection
  breaks and only a lexicographic QP survives** — shown numerically. Why a weighted sum cannot
  imitate a priority is confirmed by measuring that the leakage is proportional to the weight, and
  the lesson ends with why the order of slack matters when a task is infeasible.
objectives:
  - Derive the hierarchical null-space projection solution and prove that a higher-priority task is unaffected by lower ones.
  - Confirm numerically that with equality tasks only, a lexicographic QP and null-space projection give the same solution.
  - Show with concrete numbers how a projection-based solution loses priority under inequality constraints.
  - Measure that the task leakage of a weighted QP is proportional to the weight and explain why that cannot be a priority.
  - State what a lexicographic QP guarantees when the higher-priority task is infeasible.
tags: [legged-robots, whole-body-control, hierarchical-qp, null-space, research]
---

# Whole-body control and hierarchical QPs

## Setup and notation

`s3-centroidal-mpc` planned in the language of the centre of mass and contact forces. That plan is
not a set of joint commands. A whole-body controller must push it down to joint accelerations,
torques and contact forces at every control tick, and in doing so **several tasks conflict at
once**: tracking the centroidal plan, holding the feet, keeping a posture, joint limits, torque
limits, friction cones. When they cannot all be satisfied, **what gets given up first** is the
subject of this lesson.

Assumed: Jacobians and pseudo-inverses (`c1-poe-analytic-ik`), QPs and KKT conditions
(`r0-convex-optimization`), and the centroidal dynamics of `s3-centroidal-mpc`.

| Symbol | Meaning |
|---|---|
| $\dot q \in \mathbb{R}^n$ | the decision variable (joint velocity; the acceleration and torque levels have the same structure) |
| $J_i \in \mathbb{R}^{m_i\times n}$, $\dot x_i$ | the Jacobian and target of the task at level $i$ |
| $A^{+}$ | the Moore-Penrose pseudo-inverse |
| $N_i = I - J_{1:i}^{+}J_{1:i}$ | the projector onto directions that satisfy levels $1..i$ |
| $r_i^\star$ | the **optimal residual** of level $i$, $\min\lVert J_i\dot q - \dot x_i\rVert^2$ |
| $\lvert\dot q\rvert \le \bar v$ | joint velocity limits (the representative inequality) |
| $w_i$ | the weights of a weighted-sum QP |

The numerical example is a three-link planar arm ($\ell = (0.5,0.4,0.3)$ m,
$q = (0.4,0.6,-0.3)$ rad). Level 1 is the end-effector velocity (two-dimensional)
$\dot x_1 = (0.05,-0.03)$ and level 2 is a posture velocity (three-dimensional)
$\dot x_2 = 2(q_{\mathrm{ref}} - q)$ with $q_{\mathrm{ref}} = (0.3,-0.4,0.2)$. With three degrees of
freedom and level 1 using two, level 2 has **only one left** — the conflict is deliberate.

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (hierarchical null-space projection and priority preservation) [D3]** — for two levels,
  $$
  \dot q_1 = J_1^{+}\dot x_1, \qquad
  N_1 = I - J_1^{+}J_1, \qquad
  \dot q_2 = \dot q_1 + (J_2N_1)^{+}\big(\dot x_2 - J_2\dot q_1\big) \tag{1}
  $$
  and $J_1\dot q_2 = J_1\dot q_1$ holds **identically** (because $J_1N_1 = 0$). Whatever level 2 is
  changed to, what level 1 achieves does not move. Numerically: changing the level-2 target at
  random 100 times leaves a maximum level-1 error of $1.0\cdot10^{-6}$ (solver tolerance).
- **R2 (with equality tasks, a lexicographic QP equals null-space projection) [D2]** — solving
  $\min\lVert J_i\dot q - \dot x_i\rVert^2$ level by level, **with the previous level's optimal
  residual imposed as a constraint**, gives the solution of (1). Numerically
  $\max\lvert\dot q_{\text{lex}} - \dot q_{\text{ns}}\rvert = 7.4\cdot10^{-6}$, with level-2
  residuals $1.7909159$ against $1.7909232$.
- **R3 (inequalities break projection) [D3]** — an inequality such as
  $\lvert\dot q\rvert\le\bar v$ **cannot be expressed by a projector**. Solving (1) and then
  **clipping** destroys the priority. Numerically, with $\bar v = 0.35$ the solution of (1) has
  $\max\lvert\dot q\rvert = 1.099$, and clipping raises the level-1 error to $0.172$ rad/s. Solving
  the same problem as a lexicographic QP gives a level-1 residual of $3.6\cdot10^{-17}$, and
  changing the level-2 target leaves that residual changed by **exactly zero**.
- **R4 (a weighted sum is not a priority) [D2]** — in the single QP
  $\min \lVert J_1\dot q-\dot x_1\rVert^2 + w_2\lVert J_2\dot q-\dot x_2\rVert^2$, the level-1
  leakage is **proportional** to $w_2$:

  | $w_2$ | $1$ | $10^{-2}$ | $10^{-4}$ | $10^{-6}$ | $10^{-8}$ |
  |---|---|---|---|---|---|
  | level-1 error | $4.18\cdot10^{-1}$ | $6.15\cdot10^{-2}$ | $1.03\cdot10^{-3}$ | $1.03\cdot10^{-5}$ | $1.03\cdot10^{-7}$ |

  No finite $w_2$ gives the priority **exactly**, and $w_2\to0$ wrecks the conditioning.
- **R5 (infeasibility and the order of slack) [D2]** — if level 1 is unachievable to begin with
  (if $\dot x_1$ cannot be produced within $\bar v$), the lexicographic QP **minimises level 1's
  residual first** and level 2 cannot make it worse. Numerically the level-1 optimal residual
  $3.12603864$ changes by **zero** over 60 different level-2 targets.

## Derivation

### R1 — null-space projection and priority preservation

**Step 1 (level 1).** The solution set of $\min\lVert J_1\dot q - \dot x_1\rVert^2$ is
$\dot q = J_1^{+}\dot x_1 + N_1 v$ with $v$ free. $J_1^{+}$ gives the minimum-norm solution and
$N_1 = I - J_1^+J_1$ projects onto the directions that **do not change** what level 1 achieves
(from $J_1N_1 = 0$, immediate from the pseudo-inverse identity $J_1J_1^{+}J_1 = J_1$).

**Step 2 (level 2 in what is left).** Substituting $\dot q = \dot q_1 + N_1v$ into the level-2 cost,

$$
\min_v \big\lVert J_2N_1 v - (\dot x_2 - J_2\dot q_1)\big\rVert^2
\;\Longrightarrow\;
v^\star = (J_2N_1)^{+}(\dot x_2 - J_2\dot q_1),
$$

which is (1). **Priority preservation** is one line:

$$
J_1\dot q_2 = J_1\dot q_1 + \underbrace{J_1N_1}_{=0}v^\star = J_1\dot q_1. \tag{2}
$$

For $k$ levels the same step repeats with the projectors accumulated. Induction then gives that
what level $i$ achieves is **independent** of levels $j>i$ (see the proof sketch).

**Numerical check**: in the example, (1) gives
$\dot q = (-0.20727997,\ -0.21183933,\ 1.09916894)$ with a level-1 residual of $1.1\cdot10^{-16}$
and a level-2 residual of $1.79092324$.

**A numerical trap**: when computing $(J_2N_1)^{+}$, **misjudging the rank** of $N_1$ makes the
solution explode. The same formula computed with numpy's default `rcond` gives
$\max\lvert\dot q\rvert = 6.2\cdot10^{14}$ and a level-1 residual of $8.0\cdot10^{14}$ — a projector
should have only the singular values $0$ and $1$, but numerical error leaves singular values of
order $10^{-16}$ **alive**, and they are amplified by inversion. With a threshold of $10^{-10}$ the
solution is normal again. Half of the field reports of "the priority controller blew up" are this
problem (the other half is $J_1^{+}$ near a singularity, handled by a damped pseudo-inverse).

### R3 — inequalities: why projection breaks

With an inequality $\lvert\dot q\rvert\le\bar v$, the solution set of level 1 is **a polyhedron, not
an affine subspace**. Equation (1) depends on the **linear** structure "solution set =
$\dot q_1 + \operatorname{range}(N_1)$", so once that structure is gone it cannot be used. Three
common responses, compared numerically ($\bar v = 0.35$, the example above):

| Method | level-1 error | Note |
|---|---|---|
| (1) as is | $1.1\cdot10^{-16}$ | **violates the limit**: $\max\lvert\dot q\rvert = 1.099 > 0.35$ |
| (1) then clipped | $1.7\cdot10^{-1}$ | respects the limit but **the priority is gone** |
| lexicographic QP | $7.9\cdot10^{-7}$ | level-1 optimal **within** the limit ($\max\lvert\dot q\rvert = 0.35$) |

The lexicographic QP optimises level 1 **inside the constraints** ($r_1^\star = 3.6\cdot10^{-17}$)
and then solves level 2 with that optimal residual imposed as an equality. Changing the level-2
target 100 times leaves $r_1$ changed by **exactly zero**.

**Why clipping is wrong**: clipping changes each component independently and so leaves the image of
$N_1$. The only directions that preserve what level 1 achieves are
$\operatorname{range}(N_1)$, and clipping steps outside, breaking the premise of (2). **Constraints
belong in the problem formulation, not in post-processing** — that is the one-sentence summary of
this lesson.

### R4 — why a weighted sum cannot imitate a priority

Writing the KKT conditions of the single QP, the solution is
$\dot q(w_2) = (J_1^\top J_1 + w_2 J_2^\top J_2)^{+}(J_1^\top\dot x_1 + w_2J_2^\top\dot x_2)$.
Expanding in $w_2$ makes the level-1 error appear at order $w_2$:

$$
J_1\dot q(w_2) - \dot x_1 = -w_2\,J_1(J_1^\top J_1)^{+}J_2^\top\big(J_2\dot q_1 - \dot x_2\big) + O(w_2^2). \tag{3}
$$

The measurements are exactly that: reducing $w_2$ by a factor 100 reduces the level-1 error by 100
($1.03\cdot10^{-3} \to 1.03\cdot10^{-5} \to 1.03\cdot10^{-7}$). Hence

- **the priority is obtained only in the limit** $w_2\to0$; at any finite $w_2$ there is leakage;
- shrinking $w_2$ raises the condition number like $1/w_2$ and breaks numerically. The common field
  choice $w_2 = 10^{-6}$ is "a compromise between $10^{-5}$ leakage and a $10^{6}$ condition
  number";
- with three or more tasks the weight **ratios** must be tuned by hand, and retuned when the robot
  configuration changes. A lexicographic QP replaces that tuning **with structure**.

**Where the assumptions break**: a lexicographic QP is not free either. One QP per level makes the
cost proportional to the number of levels, and imposing level 1's optimal residual as an
**equality** propagates that level's numerical error downwards (§4 of Escande et al. 2014 handles
this with a shared active-set decomposition). So in practice the number of levels is kept to three
to five and the rest are blended with weights.

## Proof sketch

### R1 — priority preservation for $k$ levels

**Hypotheses** H1: each $J_i$ has finite rank and $N_i$ is computed exactly. H2: all levels are
equality tasks (no inequalities). H3: each level's cost is a quadratic norm.
**Conclusion** C: what level $i$ achieves, $J_i\dot q$, is **independent** of the targets
$\dot x_j$ of levels $j > i$.

**Strategy**: only two properties of projectors are used — $J_{1:i}N_i = 0$ and that $N_i$ is the
identity on its range.

1. **The recursive solution.** Define
   $\dot q_i = \dot q_{i-1} + N_{i-1}v_i$ with
   $v_i = (J_iN_{i-1})^{+}(\dot x_i - J_i\dot q_{i-1})$, accumulating
   $N_i = N_{i-1} - (J_iN_{i-1})^{+}(J_iN_{i-1})$.
2. **Higher levels are invariant.** Show by induction that $J_jN_i = 0$ for $j\le i$ (using the
   definition of $N_i$ and $J_jN_{i-1}=0$). Hence
   $J_j\dot q_{i} = J_j\dot q_{i-1} = \dots = J_j\dot q_j$.
3. **Independence.** The equalities of step 2 **do not contain** $\dot x_{j+1},\dots$ — those enter
   only $v_{j+1}$ and beyond, all of which are projected into the range of $N_j$ and are therefore
   invisible to $J_j$. That is C.
4. **What optimality means here.** Each level is optimal "within the solution set of the previous
   levels". Globally this is a lexicographic optimum, and it **forbids** the trade of increasing
   level 1's residual by 1 to reduce level 2's by 100. That is the definition of a priority.

**Remove a hypothesis**: without H2 (no inequalities), the solution set in step 1 is not a subspace
and $N_i$ is not even defined — the numbers of R3 are the consequence. If H1 (exact rank) fails,
every equation of the derivation still holds while the numerical solution explodes (the
$6.2\cdot10^{14}$ of the trap above). Changing H3 to a 1-norm cost makes the solution non-unique and
destroys the projection structure, so the hierarchy must be rebuilt as a cascade of LPs or QPs.

Technical steps omitted: existence of $(J_iN_{i-1})^{+}$ and idempotence of $N_i$ (Escande et al.
2014 §2), and the fact that a damped pseudo-inverse leaks priority at order $\lambda^2$.

## Problem set

Six problems: one derivation, one proof, one numerical, one implementation and two counterexamples.

**P1 (derivation, ★★, R1)** Derive (1) and show the priority preservation (2) using only
pseudo-inverse identities. Then add a third level, write the accumulation formula for $N_2$ and
prove $J_1 N_2 = 0$ by induction.
*Solution sketch*: write level 1's solution set as the minimum-norm solution plus its null space and
substitute into the level-2 cost. $J_1 N_1 = 0$ follows directly from $J_1 J_1^+ J_1 = J_1$. For the
third level take $N_2 = N_1 - (J_2 N_1)^+ (J_2 N_1)$ and induct with
$J_1 N_2 = J_1 N_1 - (J_1 N_1)(\cdots) = 0$.

**P2 (proof, ★★★, R2·R4)** Prove that with equality tasks only, and all levels feasible, the
lexicographic QP solution equals (1). Then show the weighted QP solution converges to (1) as
$w_2 \to 0$, and confirm with (3) that the rate is $O(w_2)$.
*Solution sketch*: strategy — show that imposing level 1's optimal residual as an equality is the
same as fixing the solution set to an affine subspace, and that minimising level 2 inside it gives
the same KKT conditions as the second term of (1). For the weighted side, perturb the normal
equations in $w_2$; the first-order term is (3).

**P3 (numerical, ★, R1·R4)** For the three-link example find (a) the null-space projection solution
$\dot q$, (b) the level-2 residual, and (c) the level-1 error of the weighted QP at
$w_2 = 10^{-4}$.
*Answers*: (a) $\dot q = (-0.20727997, -0.21183933, 1.09916894)$, (b) $1.79092324$,
(c) $1.025\cdot10^{-3}$. Tolerance $10^{-6}$. Check: (c) falls by a factor 100 whenever $w_2$ does
($1.032\cdot10^{-5}$, $1.032\cdot10^{-7}$).

**P4 (implementation, ★★, R2·R3·R5)** Implement the lexicographic QP and pass the four acceptance
criteria of the reproduction task. Then extend to three levels (end-effector velocity, posture,
minimum effort) and confirm numerically that each level's optimal residual is independent of lower
levels' targets.
*Rubric*: passing requires (1) agreement with the projection solution to $10^{-5}$ with equalities
only, (2) a level-1 residual change below $10^{-12}$ under inequalities, (3) higher residuals
unchanged as levels are added, and (4) reporting each QP's status and tolerances.

**P5 (counterexample, ★★, R3)** Give concrete numbers showing that computing the projection solution
and then clipping it to the joint velocity limits destroys the priority. Then explain why "it only
exceeded the limit a little, so clipping is fine" is wrong in general.
*Rubric*: passing requires showing $\max\lvert\dot q\rvert = 1.099$ at $\bar v = 0.35$ and a level-1
error rising to $0.172$ after clipping, and noting that clipping leaves
$\operatorname{range}(N_1)$ so $J_1\dot q$ is not preserved, with the size of the error depending on
the conditioning of $J_1$ rather than on the amount of excess.

**P6 (counterexample, ★★, R1)** Reproduce the case where leaving the pseudo-inverse truncation
threshold (`rcond`) at its default makes the solution explode when computing $(J_2 N_1)^{+}$, explain
the cause in terms of the singular values of $N_1$, and propose a rule for choosing the threshold.
*Rubric*: passing requires reproducing $\max\lvert\dot q\rvert \sim 6\cdot10^{14}$ and a level-1
residual $\sim 8\cdot10^{14}$ with the default, and printing the singular values of $N_1$ as
$\{1, \sim10^{-16}, \sim10^{-16}\}$. Example rule: `rcond` $=10^{-10}$, or determine the rank first
by SVD (using the fact that it is a projector) and truncate at that rank.

## Paper reading

**Three must-reads.** Write a one-page note on each with the ten fixed questions
(`lesson-standard.md` §5).

1. **Sentis & Khatib, "Synthesis of whole-body behaviors through hierarchical control of behavioral
   primitives" (2005, Int. J. Humanoid Robotics)** — role: `seminal`.
   <https://doi.org/10.1142/S0219843605000594> (§3, §4). The classic of stacking whole-body tasks
   by null-space projection.
   Extra questions: ⓐ What is the authors' criterion for splitting behaviour into "behavioral
   primitives"? ⓑ How are inequality constraints (joint and torque limits) handled in that
   framework, and how does that handling compare with the numbers of R3?
2. **Escande, Mansard & Wieber, "Hierarchical quadratic programming: fast online humanoid-robot
   motion generation" (2014, IJRR)** — role: `standard`.
   <https://doi.org/10.1177/0278364914521306> (§2, §4). Formulating a hierarchy **including
   inequalities** as a cascade of QPs and solving it quickly by sharing the active set.
   Extra questions: ⓐ Is the authors' definition of a lexicographic optimum the same as our R2?
   ⓑ How do they report the computational cost in the number of levels and the real-time limit
   (hardware, rate, number of tasks)?
3. **Herzog et al., "Momentum control with hierarchical inverse dynamics on a torque-controlled
   humanoid" (2016, Autonomous Robots)** — role: `standard`.
   <https://doi.org/10.1007/s10514-015-9476-6> (§III, §V). Centroidal momentum tasks pushed down by
   hierarchical inverse dynamics and validated on hardware (a torque-controlled humanoid) — the link
   between the previous lesson and this one.
   Extra questions: ⓐ How do the authors handle the **feasibility mismatch** between the centroidal
   plan and the whole-body QP? ⓑ At which level do they put torque limits and friction cones, and
   on what grounds?

**The ten fixed questions**: (1) which problem under which assumptions (2) what exactly earlier
work could not do (3) the core idea in one equation (4) what is guaranteed and **what is not**
(5) independent and dependent variables and baselines, fairly tuned (6) do the metrics match the
claim, are variance and seeds reported (7) what is missing for reproduction (8) the first
assumption to doubt if the result is wrong (9) computational and memory complexity and real-time
feasibility (10) what you would change to go beyond it in a year.

## Reproduction task

**Tier R2 (re-implementation).** Budget: laptop CPU under five minutes, numpy plus one QP solver.
The target is the three-link planar arm above; there is no input data.

**Acceptance criteria (all four)**

1. **Equivalence with equality tasks**: with no inequalities, ⓐ the projection solution of (1) and
   ⓑ the lexicographic QP solution agree with
   $\max\lvert\dot q_{\text{lex}}-\dot q_{\text{ns}}\rvert < 10^{-4}$ (reference
   $7.4\cdot10^{-6}$) and the level-2 residuals match to five decimals (reference $1.79092$). The
   projection solution must match $\dot q = (-0.20727997,\ -0.21183933,\ 1.09916894)$ to $10^{-6}$.
2. **Priority preservation**: changing the level-2 target at random 100 times gives ⓐ with
   equalities only, a level-1 error $< 10^{-5}$ (reference $1.0\cdot10^{-6}$), and ⓑ under
   $\lvert\dot q\rvert\le0.35$, a change in level 1's **optimal residual** below $10^{-12}$
   (reference exactly $0$).
3. **The leakage of a weighted sum**: measure the level-1 error for
   $w_2 \in \{1, 10^{-2},10^{-4},10^{-6},10^{-8}\}$, match the table in the text to within $10^{-2}$
   relative each, and show the leakage is **linear** in $w_2$ (a log-log line of slope 1).
4. **Inequalities and infeasibility**: ⓐ the clipped-projection version has a level-1 error
   $> 10^{-2}$ (reference $0.172$) while the lexicographic QP has $< 10^{-5}$ (reference
   $7.9\cdot10^{-7}$); ⓑ with level 1 made unachievable ($\dot x_1 = (2.0,-1.5)$, $\bar v = 0.35$)
   the level-1 optimal residual is $3.12603864 \pm 10^{-6}$ and changes by $< 10^{-12}$ over 60
   level-2 targets.

**Baselines**: ⓐ the weighted QP (criterion 3) — at no weight does the level-1 error become exactly
zero; ⓑ projection plus clipping (criterion 4ⓐ) — the priority breaks; ⓒ the projection solution
computed with the default `rcond` — it must explode to
$\max\lvert\dot q\rvert \approx 6\cdot10^{14}$ (reproducing the numerical trap).

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| The projection solution explodes to $10^{14}$ | the truncation threshold of $(J_2N_1)^{+}$ is too small (the default `rcond`) | print the singular values of $N_1$ — if they are $\{1, \sim10^{-16},\sim10^{-16}\}$, raise the threshold to $10^{-10}$ |
| The lexicographic QP differs from the projection solution | level 1's residual was imposed as an inequality $\le r_1+\epsilon$ with a large $\epsilon$ | reduce $\epsilon$ to $10^{-12}$ and compare again |
| Criterion 2ⓑ wobbles at the $10^{-6}$ level | solver tolerance; the solution vector was compared instead of level 1's residual | compare $r_1^\star$ itself (the objective value) — it is the stable quantity |
| The leakage is not linear in $w_2$ | the task Jacobian is near a singularity, making $(J_1^\top J_1)^{+}$ unstable | move $q$ away from the singularity and report the condition number too |
| The residual of criterion 4ⓑ differs run to run | the solution of an infeasible QP is not unique (the objective is) | compare the **optimal value**, not the solution vector |

## Open problems

- **(open problem) The number of levels and real-time execution** — one QP per level costs
  proportionally in the number of levels, and when the active set changes between levels the
  recomputation grows. Escande et al. 2014 reduced this greatly by sharing active sets, but there is
  still no **guaranteed** computation time for a setting with ten or more levels at 1 kHz. The gap:
  predicting the worst-case execution time at design time.
- **(open problem) The feasibility mismatch between the centroidal plan and the whole body** — the
  centroidal MPC of the previous lesson knows nothing of joint limits, so level 1 of the whole-body
  QP can turn out infeasible. What is then given up is decided by a hand-written priority table. The
  gap: a feasibility signal sent **back** to the centroidal stage (two-way coupling).
- **(open problem) Learning the priorities themselves** — task priorities are set by hand. They
  should change with the task and terrain, but there is no way to keep the guarantee that learned
  priorities never violate safety constraints (friction, torque limits). The open problems of
  `s3-locomotion-rl` and `c3-cbf-safety-filter` meet here.
- **(open problem) Non-smooth transitions** — when contact changes, the task set and the active set
  change together and the QP solution jumps discontinuously. That jump appearing as a torque spike is
  a chronic hardware problem. The gap: a formulation guaranteeing continuity of the solution through
  the transition (the saltation matrix of `s3-hybrid-limit-cycles` handles the same structure).

## Concept check

Take it with `rc quiz s3-whole-body-control`. The quiz is **for concept checking only**; the real
work is the problem set and the reproduction task above (`lesson-standard.md` §4). Four questions
ask: why a higher-priority task is unaffected by lower ones; whether small enough weights reproduce
a strict priority; what breaks when a projection solution is clipped; and what a lexicographic QP
guarantees when the higher level is infeasible.

## How to study this stage

1. **Memorise one line (20 min)** — $J_1N_1 = 0$. That is all of priority preservation. Write (2)
   out twice by hand.
2. **Match two equality levels by hand and in code (60 min)** — criterion 1 of the reproduction
   task. Once the projection solution and the lexicographic QP agree, it becomes clear that they
   differ **only under inequalities**.
3. **Step on the numerical trap deliberately (30 min)** — P6. See the $6\cdot10^{14}$ with the
   default `rcond`. Half the field reports of "the priority controller blew up" are this.
4. **Try to imitate a priority with weights (40 min)** — criterion 3. Plot the log-log slope of 1
   yourself. You learn in numbers that "use a smaller weight" is not the answer.
5. **Add inequalities and compare the two methods (60 min)** — criterion 4ⓐ. See the $0.172$ of the
   clipped version. **Constraints belong in the formulation** is the conclusion of this lesson.
6. **Design an infeasible case (40 min)** — criterion 4ⓑ. Make level 1 unachievable and confirm that
   level 2 cannot touch its residual. This is the property used most often on hardware.
7. **Read the papers for "where inequalities are handled" (135 min)** — Sentis 2005 (projection),
   Escande 2014 (a QP hierarchy), Herzog 2016 (centroidal momentum plus hardware). Tabulate at which
   layer each solves the same problem.

**Passing bar**: you can derive (1) and (2) from memory, say why the leakage of a weighted sum is
$O(w_2)$, and you have code meeting all four acceptance criteria plus notes on the three papers.
