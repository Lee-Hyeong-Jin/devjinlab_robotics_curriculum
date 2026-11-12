---
id: c1-poe-analytic-ik
lang: en
title: The product of exponentials and analytic inverse kinematics
summary: >-
  Write forward kinematics as a product of exponentials of screw axes, and decompose inverse
  kinematics into geometric Paden-Kahan subproblems with closed-form solutions. Covers the number
  of solutions and the branch structure of a general 6R arm, and where one has to switch to a
  numerical solver.
objectives:
  - Set up PoE forward kinematics from screw axes and convert between the space and body forms.
  - Derive the solvability condition and the closed-form solution of Paden-Kahan subproblem 1 from scratch.
  - Explain the strategy of subproblems 2 and 3 geometrically and count their solutions.
  - List the solution branches of a 6R manipulator and state, with a source, why there are at most 16.
  - Justify when to abandon a closed form and switch to a numerical solver.
tags: [lie-groups, kinematics, product-of-exponentials, inverse-kinematics, research]
---

# The product of exponentials and analytic inverse kinematics

## Setup and notation

The notation of the previous three lessons carries over. Additional symbols:

| Symbol | Meaning |
|---|---|
| $\mathcal{S}_i = (\omega_i, v_i)$ | the screw axis of joint $i$, as seen in the **zero configuration** |
| $M \in SE(3)$ | the end-effector pose at $\theta = 0$ (the home pose) |
| $T(\theta)$ | the end-effector pose at joint angles $\theta \in \mathbb{R}^n$ |
| $\mathcal{B}_i$ | the screw axis as seen in the body frame |
| $p, r \in \mathbb{R}^3$ | the point to be moved and its target, in a subproblem |
| $q_i$ | a point on axis $i$ |

**Convention**: a revolute joint has $\mathcal{S} = (\omega, -\omega \times q)$ with
$\lVert\omega\rVert=1$; a prismatic joint has $\mathcal{S} = (0, v)$ with $\lVert v\rVert=1$.
These are the cases $h=0$ and $\omega=0$ of the screw decomposition (R3) of the previous lesson.

**Why not DH parameters**: the DH convention leaves freedom in how frames are assigned, so one
robot admits several different tables, and misreading a table fails silently. A screw axis is
**the geometry itself** (the direction and location of the axis), so there is no convention to
choose. That is the shift of view Brockett 1984 (must-read 1) brought.

## Key results

- **R1 (PoE forward kinematics) [D2]** — the space form is

$$
T(\theta) = \mathrm{Exp}(\mathcal{S}_1\theta_1)\,\mathrm{Exp}(\mathcal{S}_2\theta_2)\cdots
\mathrm{Exp}(\mathcal{S}_n\theta_n)\,M, \tag{1}
$$

  and the body form is
  $T(\theta) = M\,\mathrm{Exp}(\mathcal{B}_1\theta_1)\cdots\mathrm{Exp}(\mathcal{B}_n\theta_n)$;
  the two are related by $\mathcal{B}_i = \mathrm{Ad}_{M^{-1}}\mathcal{S}_i$.
- **R2 (Paden-Kahan subproblem 1) [D3]** — rotating about the axis $(\omega, q)$ to move the point
  $p$ onto $r$ is solvable **exactly when**

$$
\omega^\top(p - q) = \omega^\top(r - q), \qquad \lVert u'\rVert = \lVert v'\rVert \tag{2}
$$

  (with $u = p-q$, $v = r-q$, $u' = u - \omega\omega^\top u$, $v' = v - \omega\omega^\top v$),
  and the solution is then **unique**:

$$
\theta = \operatorname{atan2}\big(\omega^\top(u' \times v'),\; u'^\top v'\big). \tag{3}
$$

  If $u' = 0$ the point lies on the axis and $\theta$ is **arbitrary** (degenerate).
- **R3 (subproblems 2 and 3) [D2]** — subproblem 2 (moving a point with two intersecting axes) has
  in general **0, 1 or 2** solutions, and so does subproblem 3 (rotating to achieve a given
  distance $\delta$). Both reduce to subproblem 1, and the count is decided by **how two circles
  in a plane intersect**.
- **R4 (number of 6R solutions) [D0]** — the inverse kinematics of a general 6R manipulator has at
  most **16** solutions, reducible to a degree-16 polynomial. This is cited, not derived — it is a
  result of algebraic geometry, collected with modern algorithms in Husty et al. 2007 (must-read 2).
- **R5 (structures with closed forms) [D1]** — Paden-Kahan yields a closed form when the axes
  **intersect or are parallel** (for example a 3-axis arm with a spherical wrist). For a general
  structure one goes numerical (manifold Newton / Gauss-Newton in `c1-manifold-optimization`).

## Derivation

### R1 — PoE forward kinematics and the two forms

**What the space form means**: $\mathrm{Exp}(\mathcal{S}_i\theta_i)$ is "the rigid motion that
turns the screw axis $\mathcal{S}_i$, as seen in the reference frame, by $\theta_i$". Reading from
joint $n$ backwards: moving $\theta_n$ screws the end-effector about $\mathcal{S}_n$, and the
motion of $\theta_{n-1}$ then carries that result along. That nesting is the **left-to-right
product** in (1).

The key point is that $\mathcal{S}_i$ is a **fixed value taken in the zero configuration**. Moving
$\theta_1$ does move the actual location of axis 2, but (1) lets the left factor absorb that
change, so the axes are never recomputed. That is why a list of axes replaces a DH table.

**Relating the two forms**: insert $M M^{-1}$ into (1) and move each factor past $M$. By R1 of the
previous lesson (the adjoint),

$$
M^{-1}\mathrm{Exp}(\mathcal{S}\theta)M = \mathrm{Exp}\big(\mathrm{Ad}_{M^{-1}}\mathcal{S}\,\theta\big)
$$

(conjugation inside the exponential becomes the adjoint — apply the conjugation term by term to
the series), hence

$$
T(\theta) = M\,\mathrm{Exp}(\mathrm{Ad}_{M^{-1}}\mathcal{S}_1\,\theta_1)\cdots
\mathrm{Exp}(\mathrm{Ad}_{M^{-1}}\mathcal{S}_n\,\theta_n),
$$

so $\mathcal{B}_i = \mathrm{Ad}_{M^{-1}}\mathcal{S}_i$.

**Where the assumption breaks**: (1) holds only for a **serial chain**. With a closed loop the
joint angles are not independent, so $T$ is not a function of $\theta$ at all — the constraint
equations must be solved alongside, which is the subject of `c2-constrained-dynamics`.

## Proof sketch

### R2 — Paden-Kahan subproblem 1

**Hypotheses** H1: the axis is given by a unit $\omega$ and a point $q$ on it (revolute, zero
pitch). H2: we seek a rotation $\mathrm{Exp}(\mathcal{S}\theta)$ carrying $p$ to $r$.
**Conclusion** C: a solution exists iff (2) holds, and if $u' \ne 0$ it is unique and given by (3).

**Strategy**: split into the component along the axis and the component perpendicular to it. A
rotation **preserves** the axial component and **preserves the length** of the perpendicular one,
so the only freedom left is one angle in the perpendicular plane.

1. **Translate to the axis.** Put $u := p - q$ and $v := r - q$; the problem becomes "rotate $u$
   onto $v$ about the axis $\omega$ through the origin" (the point $q$ on the axis is fixed by the
   rotation).
2. **Decompose.** Write $u = \omega(\omega^\top u) + u'$ and $v = \omega(\omega^\top v) + v'$.
   Since $R = \mathrm{Exp}(\omega\theta)$ fixes $\omega$, we get
   $R u = \omega(\omega^\top u) + Ru'$ with $Ru' \perp \omega$ and $\lVert Ru'\rVert = \lVert u'\rVert$.
3. **Necessity.** For $Ru = v$ the axial components must agree ($\omega^\top u = \omega^\top v$)
   and the perpendicular lengths must agree ($\lVert u'\rVert = \lVert v'\rVert$). That is (2).
4. **Sufficiency and uniqueness.** If (2) holds and $u' \ne 0$, then $u'$ and $v'$ are vectors of
   equal length in the same plane perpendicular to $\omega$, so exactly one rotation of that plane
   takes $u'$ to $v'$. Its angle is the included angle, with the sign fixed by taking $\omega$ as
   the normal — $\cos\theta \propto u'^\top v'$ and $\sin\theta \propto \omega^\top(u'\times v')$,
   which is (3). The planar rotation is unique, so the solution is unique.
5. **Degeneracy.** If $u' = 0$ the point lies on the axis and no $\theta$ moves it. Then every
   $\theta$ is a solution if the first condition of (2) holds, and none is otherwise.

**Why atan2**: writing $\arccos(u'^\top v'/\lVert u'\rVert^2)$ **loses the sign** (it only returns
$[0,\pi]$), and the derivative of $\arccos$ blows up where $u' \parallel v'$, which is numerically
poor. Using both components, `atan2` covers $(-\pi,\pi]$ and is better conditioned. It is the same
lesson as the difficulty at $\theta=\pi$ for the logarithm in the first lesson.

**Delete a hypothesis**: for a screw joint with non-zero pitch (violating H1) the axial component
is **not preserved** — it slides in proportion to $\theta$. The first condition in step 3 becomes
$\omega^\top(v-u) = h\theta$, so $\theta$ appears on both sides and the problem is no longer
"find one angle in a plane".

### R3 — the strategy and solution counts of subproblems 2 and 3

- **Subproblem 2** (two intersecting axes $\omega_1, \omega_2$ meeting at $q$):
  $\mathrm{Exp}(\mathcal{S}_1\theta_1)\mathrm{Exp}(\mathcal{S}_2\theta_2)p = r$. Both rotations fix
  $q$, so $\lVert p-q\rVert = \lVert r-q\rVert$ is necessary. Strategy: the intermediate point
  $c := \mathrm{Exp}(\mathcal{S}_2\theta_2)p$ must (a) lie on the same cone about axis 2 as $p$ and
  (b) lie on the same cone about axis 1 as $r$. The intersection of those two cones (two circles in
  two planes) gives the candidates for $c$, so there are **0, 1 or 2**. For each $c$, apply
  subproblem 1 twice to get $(\theta_1,\theta_2)$.
- **Subproblem 3** (rotate to achieve a distance): $\lVert \mathrm{Exp}(\mathcal{S}\theta)p - r\rVert = \delta$.
  Removing the axial component turns this into "which angle puts a point on a circle of radius
  $\lVert u'\rVert$ at distance $\delta'$ from a fixed point", and the law of cosines gives

$$
\theta = \theta_0 \mp \phi, \quad
\cos\phi = \frac{\lVert u'\rVert^2 + \lVert v'\rVert^2 - \delta'^2}{2\lVert u'\rVert\,\lVert v'\rVert},
\quad \delta'^2 = \delta^2 - \big(\omega^\top(p-r)\big)^2, \tag{4}
$$

  where $\theta_0$ is the angle of (3). There is no solution if $\lvert\cos\phi\rvert > 1$, one if
  it equals 1, and two if it is less — **the tangent case is where the count changes**, and it is
  numerically the most dangerous place.

## Problem set

★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Show $M^{-1}\mathrm{Exp}(\mathcal{S}\theta)M =
\mathrm{Exp}(\mathrm{Ad}_{M^{-1}}\mathcal{S}\,\theta)$ directly from the series, and derive
$\mathcal{B}_i = \mathrm{Ad}_{M^{-1}}\mathcal{S}_i$ from it.
*Solution sketch*: $M^{-1}(\hat{\mathcal{S}}\theta)^k M = (M^{-1}\hat{\mathcal{S}}\theta M)^k$, and
$M^{-1}\hat{\mathcal{S}}M = \widehat{\mathrm{Ad}_{M^{-1}}\mathcal{S}}$ (previous lesson, R1), so the
conjugation can be pushed through the series term by term.

**P2 (derivation, ★★, R3)** Derive (4) from the law of cosines. In particular say why $\delta'^2$
subtracts the axial component, and what $\delta'^2 < 0$ means.
*Solution sketch*: a rotation cannot change the axial distance, so that component is constant —
Pythagoras separates out the in-plane distance $\delta'$ that must be matched. If $\delta'^2<0$
the axial component alone already exceeds $\delta$, so there is no solution.

**P3 (proof, ★★★, R2)** Prove that the solution of subproblem 1 is unique when $u'\ne0$. Do not
assume "a planar rotation is unique": suppose two rotations $R = \mathrm{Exp}(\omega\theta)$
satisfy $Ru'=v'$ and derive a contradiction.
*Solution sketch*: if $\theta_1,\theta_2$ both solve it then
$\mathrm{Exp}(\omega(\theta_1-\theta_2))$ fixes $v'$. Since $v' \ne 0$ and $v' \perp \omega$, that
rotation must be the identity (a rotation fixing a non-zero vector perpendicular to its axis is
the identity — step 2 of R2 in the first lesson), so $\theta_1 \equiv \theta_2 \pmod{2\pi}$.

**P4 (numerical, ★, R2)** With axis $\omega = (0,0,1)$, $q = 0$, $p = (1,0,2)$ and $r = (0,1,2)$,
solve subproblem 1. Check solvability with (2) first.
*Answer*: $\omega^\top u = \omega^\top v = 2$ ✓; $u' = (1,0,0)$, $v' = (0,1,0)$, both of length 1 ✓.
$u'^\top v' = 0$ and $\omega^\top(u'\times v') = 1$, so
$\theta = \operatorname{atan2}(1,0) = \pi/2 \approx 1.5707963$. Tolerance $10^{-9}$.

**P5 (implementation, ★★, R2·R3)** Write `subproblem1(omega, q, p, r)` and
`subproblem3(omega, q, p, r, delta)`. No solution, degeneracy and multiple solutions must be
distinguished **by return value, not by exceptions**.
*Rubric*: (a) (2) is checked with a tolerance and "no solution" is returned when violated;
(b) the $u'=0$ degeneracy returns its own marker; (c) subproblem 3 checks whether
$\lvert\cos\phi\rvert$ is outside tolerance **before** clipping it to 1 (so it does not silently
invent solutions near tangency); (d) every returned solution satisfies the original equation to
within $10^{-9}$.

**P6 (counterexample, ★★, R4·R5)** Construct a 6R structure for which Paden-Kahan yields no closed
form, and explain from the geometry of the axes why it does not decompose into subproblems. How
can the number of solutions be known for that structure?
*Property checklist*: the subproblems rely on "some point is invariant on an axis". If the axes
neither intersect nor are parallel, no such invariant point exists. A general 6R (skew axes) is the
example, and the count is known only from the algebraic result of R4 (at most 16) and numerical
algebra (Husty 2007).

## Paper reading

**Two must-read papers.** Write a one-page note per paper against the ten fixed questions (the
lesson standard, §5).

1. **Brockett, "Robotic manipulators and the product of exponentials formula" (1984, LNCIS)** —
   role: `seminal`. <https://doi.org/10.1007/BFb0031048>
   Extra questions: (a) what exactly did this paper **remove** relative to a DH table (a
   convention choice? arithmetic? differentiability?) (b) why does the author's view call for the
   language of Lie groups — could the same formula be written with linear algebra alone?
2. **Husty, Pfurner & Schröcker, "A new and efficient algorithm for the inverse kinematics of a
   general serial 6R manipulator" (2007, Mechanism and Machine Theory)** — role: `standard`.
   <https://doi.org/10.1016/j.mechmachtheory.2006.02.001>
   Extra questions: (a) summarise, as the paper states it, where the bound of 16 solutions comes
   from. (b) what numerical difficulties do the authors report, and how do they connect to the
   degenerate cases of this lesson (tangency, a point on the axis)? (c) where do the authors place
   the boundary between analytic and numerical methods?

## Reproduction task

**Tier R2 (re-implementation).** Budget: under ten minutes on a laptop CPU, numpy only.

**Target**: a 6R arm with a spherical wrist (axes 1-3 the arm, axes 4-6 meeting at one point). The
zero-configuration screw axes $\mathcal{S}_1..\mathcal{S}_6$ and $M$ come from a generator script
supplied with the lesson.

1. **Forward kinematics**: $T(\theta)$ implemented from (1) agrees with the Modern Robotics
   reference (`FKinSpace`) to $\lVert T - T_{\text{ref}}\rVert_F < 10^{-12}$ on 1000 random $\theta$.
2. **The two forms agree**: for the same $\theta$, the space and body forms agree to $10^{-12}$
   (computing $\mathcal{B}_i = \mathrm{Ad}_{M^{-1}}\mathcal{S}_i$ explicitly).
3. **Analytic IK round trip**: for $10^4$ random targets inside the workspace, find all solutions
   by Paden-Kahan decomposition, and check that **every returned solution** satisfies
   $\lVert T(\theta_{\text{sol}}) - T_{\text{goal}}\rVert_F < 10^{-9}$. Fewer than 1% of targets
   return no solution at all (excluding samples outside the workspace).
4. **Branch count**: report a histogram of the number of solutions over the same $10^4$ samples. A
   spherical-wrist 6R should generally give **8** (arm 2 × wrist 2 × shoulder/elbow 2), and the
   count should drop near singular configurations. More than 8 means duplicate solutions were not
   removed.

**Baseline**: run the Modern Robotics numerical IK (`IKinSpace`) on the same targets and compare
(a) whether it converges to one of the analytic solutions and (b) its iteration count and failure
rate. The key observation is that the numerical method returns **only one** solution, depending on
the initial guess.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| forward kinematics right, IK wrong | the order of subproblem application (wrist first vs arm first) | verify each stage separately against an intermediate target obtained by back-computing the wrist centre |
| more than 8 solutions | duplicates were not removed | normalise joint angles to $(-\pi,\pi]$ and deduplicate |
| `nan` at singular configurations | $u'=0$ in (3), or the clipping of $\cos\phi$ in (4) | check that the degeneracy test runs **before** the clipping |
| solutions missed near the boundary | the tolerance in (2) is too tight | relax it from $10^{-9}$ to $10^{-7}$ and re-examine the round-trip error |

## Open problems

- **(Open) Certifying global IK for general structures** — the bound of 16 for a 6R is known, but
  practical ways to **certify that all solutions for a given target have been found** are limited.
  Numerical algebra (resultants, homotopy continuation) is expensive, and numerical IK returns one
  solution. Whether the certifiable global optimization used for $SE(3)$ problems
  ([SE-Sync](https://arxiv.org/abs/1612.07386), in `c5-robust-global-estimation`) extends to IK is open.
- **(Open) IK for redundant and continuum robots** — with seven or more axes, or a continuum
  structure, the solutions form a manifold and "all solutions" is not a finite set. There is no
  general method for parameterising that manifold and combining it with task requirements
  (obstacle avoidance, joint limits) — this connects to `c6-tamp`.
- **(Open) Guarantees for learned IK** — neural IK is fast but offers no guarantee of existence,
  accuracy or branch completeness. How far a hybrid that injects the analytic decomposition as
  prior knowledge can recover those guarantees is unsettled.

## Concept check

Run `rc quiz c1-poe-analytic-ik` (add `--lang en` for the English text). It is for concept checking
only; the real work is the problem set and the reproduction task.

The four items cover: which configuration the screw axes are taken in; the solvability conditions
of subproblem 1; why `atan2` rather than `arccos`; and the upper bound on 6R solutions.

## How to study this stage

1. **Practise writing a robot as a list of axes (40 min)** — draw a 3-axis arm and write down
   $\mathcal{S}_i$ and $M$ yourself. A revolute joint is $(\omega, -\omega\times q)$. Nothing after
   this works if this does not.
2. **See subproblem 1 geometrically first (50 min)** — the picture beats the formula. Draw $u'$ and
   $v'$ in the plane perpendicular to the axis, confirm they are two points on a circle of the same
   radius, then write that the angle is (3). Check with P4.
3. **Code the degeneracies first (60 min)** — in P5, design the "no solution", "degenerate" and
   "multiple" return values **before** filling in the normal path. Doing it the other way round
   tangles the error handling and makes debugging hard.
4. **See the branch count with your own eyes (60 min)** — plot the histogram of condition 4. Watching
   the count fall as you approach a singular configuration, in a structure that normally gives 8,
   is the central experience of this lesson.
5. **Compare with numerical IK (40 min)** — run a numerical solver on the same targets and confirm
   it returns **one** solution. That is the answer to "why is a closed form worth having", and at
   the same time the reason one goes numerical for general structures.
6. **Read the papers looking for the boundary (100 min)** — Brockett 1984 gives the change of view,
   Husty 2007 the limits of the analytic approach. In both notes, write one paragraph on "how far
   is closed form, and where does one go numerical".

**Passing bar**: you can set up PoE from a list of axes alone, can derive the solvability condition
and (3) of subproblem 1 on a blank page, have an implementation that distinguishes degeneracies by
return value and meets all four acceptance conditions, and have notes on both papers.
