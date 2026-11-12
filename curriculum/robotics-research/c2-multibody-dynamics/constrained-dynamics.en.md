---
id: c2-constrained-dynamics
lang: en
title: Constrained dynamics and the operational-space inertia
summary: >-
  Set up the equations of motion of a multibody system with holonomic constraints in KKT form
  with Lagrange multipliers and prove existence and uniqueness; reread that solution through
  Gauss's principle of least constraint as the $M$-weighted projection of the unconstrained
  acceleration; and derive the operational-space inertia $\Lambda$ together with the dynamically
  consistent null-space projection. Ends at the equivalence with reduced coordinates and the error
  ODE of Baumgarte stabilisation.
objectives:
  - Set up constrained dynamics in KKT form and prove the necessary and sufficient condition for the KKT matrix to be non-singular.
  - Derive the explicit multiplier $\lambda = \Lambda(k - JM^{-1}(\tau-b))$ and explain the two readings of $\Lambda$.
  - Reduce Gauss's principle of least constraint to the KKT conditions and state the variational meaning of the constrained acceleration.
  - Derive the dynamically consistent pseudo-inverse $\bar{J}$ and the projector $N^\top$, and prove that null-space torques produce no task acceleration.
  - Derive which ODE Baumgarte stabilisation imposes on the constraint error and distinguish it from integrator error.
tags: [multibody-dynamics, constraints, kkt, operational-space, null-space, baumgarte, research]
---

# Constrained dynamics and the operational-space inertia

## Setup and notation

Everything up to `c2-crba-aba` is assumed, in particular $M(q) \succ 0$ and the ability to compute
$M$ and the bias-plus-gravity term $b(q,\dot q) := C\dot q + g$ in $\Theta(n^2)$ and $\Theta(n)$
with CRBA and RNEA. This lesson works entirely at the level of **joint space** (generalised
coordinates); 6-D spatial vectors appear only inside the construction of $M$, $b$ and $J$.

| Symbol | Meaning |
|---|---|
| $q \in \mathbb{R}^n$ | Generalised coordinates in tree coordinates (a closed loop is cut into a tree and re-tied by a constraint) |
| $\phi(q) \in \mathbb{R}^m$ | The holonomic constraint; $\phi(q) = 0$ defines the constraint manifold |
| $J := \partial\phi/\partial q \in \mathbb{R}^{m\times n}$ | The constraint Jacobian, assumed to have **full row rank** (otherwise see the counterexamples in R1) |
| $k := -\dot{J}\dot q \in \mathbb{R}^m$ | The right-hand side of the acceleration-level constraint, from $\ddot\phi = J\ddot q + \dot J\dot q = 0$ |
| $\lambda \in \mathbb{R}^m$ | The Lagrange multiplier = the constraint force; the sign convention is $M\ddot q + b = \tau + J^\top\lambda$ |
| $a_u := M^{-1}(\tau - b)$ | The **unconstrained** acceleration |
| $\Lambda := (JM^{-1}J^\top)^{-1} \in \mathbb{R}^{m\times m}$ | The constraint-space inertia / the **operational-space inertia**; $\Lambda^{-1}$ is the Delassus operator |
| $\bar J := M^{-1}J^\top\Lambda \in \mathbb{R}^{n\times m}$ | The **dynamically consistent** pseudo-inverse |
| $N^\top := \mathbb{1}_n - J^\top\bar J^\top$ | The null-space projector in torque space |
| $G(q) \in \mathbb{R}^{n\times(n-m)}$ | A basis of the null space of $J$ ($JG = 0$); the tangent map of the reduced coordinates $u$ |
| $\alpha, \beta > 0$ | The Baumgarte gains (at velocity and position level respectively) |

**Sign-convention warning**: this lesson uses

$$
M\ddot q + b = \tau + J^\top\lambda, \qquad J\ddot q = k. \tag{1}
$$

So $\lambda$ is the constraint force **acting on the system**. Many sources write
$M\ddot q + b = \tau - J^\top\lambda$, and then every sign of $\lambda$ flips — this is the
**first thing to check** when matching numbers against an external implementation (the third
convention trap, after the component order and the direction of $f_i$ in the previous lessons).

Constraints come from three places and the equations are identical for all three:
(a) **loop closure** (cutting a closed-loop mechanism into a tree and re-tying the cut);
(b) **a task** (tying the end-effector to a trajectory); (c) **contact** (non-penetration and
no-slip) — except that contact is an **inequality**, which is why the next lesson is needed. This
lesson treats (a) and (b), and goes as far as the doorway to (c).

## Key results

The bracketed grade is the derivation depth (D0 cited / D1 sketched / D2 full derivation /
D3 proof — see `lesson-standard.md` §2 in the track design notes).

- **R1 (KKT form, and existence and uniqueness) [D3]** — writing (1) as one linear system,
  $$
  \underbrace{\begin{bmatrix} M & -J^\top \\ J & 0 \end{bmatrix}}_{=:\,K}
  \begin{bmatrix} \ddot q \\ \lambda \end{bmatrix}
  = \begin{bmatrix} \tau - b \\ k \end{bmatrix}. \tag{2}
  $$
  If $M \succ 0$ and $J$ has **full row rank** then $K$ is non-singular and the solution
  $(\ddot q, \lambda)$ is unique. If $J$ is rank-deficient, $\ddot q$ is still unique (when the
  constraints are consistent) but $\lambda$ is not; and if the constraints are inconsistent there
  is **no** solution.
- **R2 (the explicit solution and Gauss's principle of least constraint) [D2]** — solving (2) by
  Schur complement,
  $$
  \lambda = \Lambda\big(k - J\,a_u\big), \qquad
  \ddot q = a_u + M^{-1}J^\top\lambda = a_u + \bar J\big(k - J a_u\big). \tag{3}
  $$
  And this $\ddot q$ is the solution of the **variational problem**
  $$
  \ddot q = \arg\min_{x}\ \tfrac{1}{2}(x - a_u)^\top M\,(x - a_u) \quad \text{s.t.} \quad Jx = k \tag{4}
  $$
  (Gauss's principle of least constraint). That is, **the constrained acceleration is the
  $M$-weighted projection of the unconstrained acceleration**, and $\lambda$ is the multiplier of
  that constraint. The Udwadia-Kalaba form is (4) solved with a pseudo-inverse, which is why it
  also handles rank-deficient and over-determined constraints.
- **R3 (operational-space inertia and dynamically consistent projection) [D3]** — reading $J$ as a
  **task** Jacobian, $\ddot x = J\ddot q + \dot J\dot q$ and the task-space equation of motion is
  $$
  F = \Lambda\ddot x + \Lambda\big(J M^{-1} b - \dot J\dot q\big), \qquad \tau = J^\top F, \tag{5}
  $$
  so $\Lambda$ is the **apparent inertia** felt at the task point. And decomposing the torque as
  $\tau = J^\top F + N^\top\tau_0$, the null-space torque $N^\top\tau_0$ produces **no task
  acceleration at all**:
  $$
  J M^{-1} N^\top = 0, \qquad J\bar J = \mathbb{1}_m. \tag{6}
  $$
  That is the precise meaning of "dynamically consistent", and the geometric pseudo-inverse
  $J^{+} = J^\top(JJ^\top)^{-1}$ **does not** have this property.
- **R4 (equivalence with reduced coordinates) [D2]** — if $G(q)$ is a basis of the null space of
  $J$ and $w$ is any particular solution of $Jw = k$, the solution of (2) is the **same** as that
  of
  $$
  \big(G^\top M G\big)\,\ddot u = G^\top\big(\tau - b - M w\big), \qquad \ddot q = G\ddot u + w \tag{7}
  $$
  (the multiplier is eliminated because $G^\top J^\top = 0$). Since $G^\top MG \succ 0$, (7) is a
  well-posed system of dimension $(n-m)$. Reduced coordinates satisfy the constraint
  **structurally**, so there is no constraint drift, but $G(q)$ has to be recomputed every step
  and a global parameterisation may not exist.
- **R5 (constraint drift and Baumgarte stabilisation) [D2; the choice of gains is D1]** — the
  acceleration-level constraint $J\ddot q = k$ **does not control** $\phi$ or $\dot\phi$, so both
  diverge under numerical integration (a double integrator). Replacing
  $$
  k \;\longrightarrow\; k - 2\alpha\,\dot\phi - \beta^2\phi \tag{8}
  $$
  makes the constraint error $e := \phi$ satisfy **exactly**
  $$
  \ddot e + 2\alpha\dot e + \beta^2 e = 0, \tag{9}
  $$
  which is exponentially stable for $\alpha, \beta > 0$. With $\alpha = \beta$ it is critically
  damped and the solution is $e(t) = (e_0 + (\dot e_0 + \beta e_0)t)e^{-\beta t}$. But all (9)
  guarantees is the **decay of an injected error**; the actual magnitude of
  $\lVert\phi\rVert$ during an integration is dominated by the **local error of the integrator** —
  confusing the two is the most common mistake on this topic (condition 4 of the reproduction
  task). **[D1]**

## Derivation

### R1·R2 — the KKT form and the explicit solution

Differentiate $\phi(q(t)) = 0$ twice. Once: $\dot\phi = J\dot q = 0$. Twice:

$$
\ddot\phi = J\ddot q + \dot J\dot q = 0 \;\;\Longleftrightarrow\;\; J\ddot q = -\dot J\dot q = k.
$$

Here $\dot J\dot q = \sum_{i,j}\frac{\partial^2\phi}{\partial q_i\partial q_j}\dot q_i\dot q_j$ is
quadratic in $\dot q$ — the same kind of term as the Coriolis terms of the previous lessons. By
the principle of virtual work the constraint force must be **normal to the constraint** (if
$\delta q$ satisfies $J\delta q = 0$ the constraint force must do no work on it), so it lies in the
column space of $J^\top$ and therefore has the form $J^\top\lambda$. Stacking the two equations
gives (2).

Solve (3) by Schur complement. From the first row of (2),

$$
\ddot q = M^{-1}(\tau - b) + M^{-1}J^\top\lambda = a_u + M^{-1}J^\top\lambda,
$$

and substituting into the second row,

$$
J a_u + \underbrace{JM^{-1}J^\top}_{=\,\Lambda^{-1}}\lambda = k
\;\;\Longrightarrow\;\; \lambda = \Lambda(k - Ja_u),
$$

which put back into the first row gives
$\ddot q = a_u + M^{-1}J^\top\Lambda(k - Ja_u) = a_u + \bar J(k - Ja_u)$. That
$\bar J = M^{-1}J^\top\Lambda$ appears here **of its own accord** is the foreshadowing of R3.

**Gauss's principle of least constraint (4).** Writing the KKT conditions of (4) finishes it. For
the Lagrangian $L(x,\mu) = \frac{1}{2}(x-a_u)^\top M(x-a_u) + \mu^\top(Jx - k)$,

$$
\nabla_x L = M(x - a_u) + J^\top\mu = 0, \qquad Jx = k.
$$

Setting $\mu = -\lambda$ makes this exactly (2). The objective is strongly convex because
$M \succ 0$ and the constraint is affine, so the solution is unique and the KKT conditions are
necessary and sufficient. In other words, **(2) and (4) are the same problem**.

What this reading buys: (a) the physical interpretation that
$\lVert\ddot q - a_u\rVert_M$ is **minimal** (Gauss 1829); (b) a natural route for relaxing (4)
into a **least-squares** problem when the constraints are over-determined or inconsistent (the
pseudo-inverse form of Udwadia-Kalaba); (c) the passage by which the **inequality** constraints of
contact extend as the KKT conditions of the same variational problem in the next lesson.

> **(4) numerically**: on the four-bar linkage of the reproduction task the KKT solution has
> $\lVert\ddot q - a_u\rVert_M = 5.523095$, while other points satisfying $Jx = k$
> ($\ddot q + \epsilon g$ with $g \in \mathrm{null}(J)$) give $5.523133$ at $\epsilon = 0.1$ and
> $5.523434$ at $\epsilon = -0.3$ — **strictly larger**.

### R3 — operational-space inertia and the null-space projection

Now read $J$ as a **task** Jacobian ($x = h(q)$, $J = \partial h/\partial q$, $m \le n$). It is an
**output** rather than a constraint, so the second equation of (1) is absent; instead compute the
task acceleration:

$$
\ddot x = J\ddot q + \dot J\dot q = J M^{-1}(\tau - b) + \dot J\dot q. \tag{10}
$$

Driving with a task force $F$ means $\tau = J^\top F$, and substituting into (10),

$$
\ddot x = JM^{-1}J^\top F - JM^{-1}b + \dot J\dot q = \Lambda^{-1}F - JM^{-1}b + \dot J\dot q,
$$

which solved for $F$ gives (5). Since $\Lambda$ is the coefficient of $\ddot x$ it is the
**inertia felt at the task point**, and $\Lambda^{-1} = JM^{-1}J^\top$ is "the task acceleration
produced by a unit task force" — the **Delassus operator** of the contact and constraint
literature. The same matrix read as a constraint is the $\Lambda$ of R2, and read as a task it is
Khatib's operational-space inertia — **that the two readings are one equation** is the axis of
this lesson.

**The null-space projection (6).** Since
$J\bar J = JM^{-1}J^\top\Lambda = \Lambda^{-1}\Lambda = \mathbb{1}_m$, $\bar J$ is a right inverse
(a pseudo-inverse) of $J$. For $N^\top = \mathbb{1} - J^\top\bar J^\top$,

$$
JM^{-1}N^\top = JM^{-1} - JM^{-1}J^\top\bar J^\top
= JM^{-1} - \Lambda^{-1}\big(M^{-1}J^\top\Lambda\big)^\top
= JM^{-1} - \Lambda^{-1}\Lambda J M^{-1} = 0,
$$

using $\bar J^\top = \Lambda JM^{-1}$ (both $\Lambda$ and $M$ are symmetric). Substituting
$\tau = N^\top\tau_0$ into (10) makes the torque contribution to $\ddot x$ equal to
$JM^{-1}N^\top\tau_0 = 0$ — **null-space torques do not change the task acceleration**. That is
what makes $\tau = J^\top F + N^\top\tau_0$ a decomposition that controls task and posture
**separately** (the core of Khatib 1987).

**Contrast with the geometric pseudo-inverse.** With $J^{+} = J^\top(JJ^\top)^{-1}$ one generally
has $JM^{-1}(\mathbb{1} - J^\top (J^{+})^\top)\ne 0$ — the "null-space" torque disturbs the task.
$J^{+}$ minimises $\lVert\dot q\rVert_2$ while $\bar J$ minimises $\lVert\cdot\rVert_M$ (kinetic
energy), so **in a dynamics problem the right metric is $M$**. The two coincide only in the
special case $M = \mathbb{1}$ (problem P3).

### R4 — reduced coordinates

Take a basis $G(q)$ of the null space of $J$ ($JG = 0$, $\mathrm{rank}\,G = n-m$). Every
acceleration satisfying the constraint can be written as $\ddot q = G\ddot u + w$ with $w$ any
particular solution of $Jw = k$. Substituting into the first equation of (1) and **multiplying on
the left by $G^\top$**,

$$
G^\top M G\,\ddot u + G^\top M w + G^\top b = G^\top\tau + \underbrace{G^\top J^\top}_{=\,0}\lambda,
$$

which is (7). **The multiplier has vanished**, and the reason is that the constraint force is
normal to the tangent space of the constraint manifold (the algebraic form of the principle of
virtual work). Since $G$ has full rank and $M \succ 0$, $G^\top MG \succ 0$ and (7) has a unique
solution.

**Trade-offs between the two methods**:

| | Multipliers (2) | Reduced coordinates (7) |
|---|---|---|
| System size | $(n+m) \times (n+m)$, indefinite | $(n-m)\times(n-m)$, positive definite |
| Constraint satisfaction | At acceleration level only — it **drifts** | Structural — no drift |
| $\lambda$ | Obtained directly (needed to monitor contact forces and joint reactions) | Must be recovered separately |
| Cost | Factor $K$; exploiting sparsity gives something like $O(n + m^3)$ | Computing $G$ plus $(n-m)^3$; $G$ is the expensive part |
| Pitfall | Drift; singular where $J$ loses rank | The **gauge** of $G(q)$ (the basis may not be chosen smoothly); no global parameterisation |

The gauge problem catches people in practice: recomputing $G$ each step by SVD or QR makes the
signs and the column order jump, so $\dot u$ becomes discontinuous. That is why the reproduction
task does not integrate $\ddot u$ and compares only at the level of $\ddot q$.

### R5 — the error ODE of Baumgarte stabilisation

The second equation of (2) is $\ddot\phi = 0$. That is a **double integrator** in $\phi$, so any
initial error or round-off grows **linearly**, $\phi(t) = \phi_0 + \dot\phi_0 t$. There is no
damping at all.

With (8) the second equation becomes
$J\ddot q = -\dot J\dot q - 2\alpha\dot\phi - \beta^2\phi$, and substituting
$\ddot\phi = J\ddot q + \dot J\dot q$ gives **exactly**

$$
\ddot\phi + 2\alpha\dot\phi + \beta^2\phi = 0,
$$

which is (9). The characteristic roots are $-\alpha \pm \sqrt{\alpha^2 - \beta^2}$, so

- $\alpha > \beta$: over-damped, and the slow root $\approx -\beta^2/(2\alpha)$ governs convergence;
- $\alpha = \beta$: **critically damped**, a double root at $-\beta$, solution
  $e(t) = (e_0 + (\dot e_0 + \beta e_0)t)e^{-\beta t}$;
- $\alpha < \beta$: damped oscillation.

The standard advice is to take $\alpha = \beta$ and choose $\beta$ so that the time constant
$1/\beta$ is comfortably larger than the integration step and comfortably faster than the dynamics
of interest. Making $\beta$ large makes the system **stiff** and pushes it out of the stability
region of an explicit integrator (a restriction of the form $\beta\,\Delta t \lesssim 1$) — the
harder you stabilise, the less stable the integration. **[D1]**

**Where the assumption breaks — the most common error.** (9) says only that an **injected** error
decays exponentially. For the error created afresh at every step (the integrator's local
truncation error) a **steady-state error** remains, whose size is set by the order of the
integrator. The measurements make this unmistakable (the four-bar linkage of the reproduction
task, 2 seconds):

| Integrator | $\Delta t$ | Stabilisation | $\max\lVert\phi\rVert$ |
|---|---|---|---|
| semi-implicit Euler | $10^{-3}$ | none | $1.5\times10^{-2}$ |
| semi-implicit Euler | $10^{-3}$ | $\alpha=\beta=20$ | $2.2\times10^{-3}$ |
| RK4 | $10^{-3}$ | none | $4.9\times10^{-7}$ |
| RK4 | $10^{-3}$ | $\alpha=\beta=20$ | $1.9\times10^{-9}$ |
| RK4 | $10^{-4}$ | $\alpha=\beta=20$ | $1.9\times10^{-13}$ |
| any integrator + **coordinate projection** | $10^{-3}$ | not needed | $1.0\times10^{-14}$ |

How to read it: with a first-order integrator, turning Baumgarte on still leaves you at the
$10^{-3}$ level — the bottleneck is the **integrator**, not the stabilisation. With a fourth-order
integrator the same stabilisation gives $10^{-9}$. And **coordinate projection** (returning $q$ to
$\phi(q) = 0$ by Newton each step and projecting $\dot q$ onto $\mathrm{null}(J)$) gives Newton
tolerance regardless of the integrator. The practical recommendation: use stabilisation as the
means of **removing an injected error**, not of keeping the error small, and use **projection**
when the constraint has to be tight.

## Proof sketch

### R1 — non-singularity of the KKT matrix

**Hypotheses** H1: $M = M^\top \succ 0$. H2: $J \in \mathbb{R}^{m\times n}$ has full row rank
($\mathrm{rank}\,J = m \le n$). **Conclusions** C1: $K$ is non-singular.
C2: $\Lambda^{-1} = JM^{-1}J^\top \succ 0$. C3: what breaks when H2 fails.

**Strategy**: show directly that the null space is trivial. It is a one-line calculation, and it
makes crystal clear which hypothesis is used where.

1. **The null space.** Suppose $K\begin{bmatrix}x\\y\end{bmatrix} = 0$. The first block gives
   $Mx = J^\top y$, the second $Jx = 0$.
2. **$x = 0$.** Multiplying the first equation by $x^\top$,
   $x^\top Mx = x^\top J^\top y = (Jx)^\top y = 0$. By H1, $x^\top Mx = 0 \Rightarrow x = 0$.
   (This is the **only** place H1 is used, and positive *semi*definiteness would not suffice.)
3. **$y = 0$.** Then $J^\top y = Mx = 0$, and by H2 $J^\top$ has full column rank, so $y = 0$.
4. **C2.** $\Lambda^{-1} = JM^{-1}J^\top$ is a congruence of $M^{-1} \succ 0$, and since $J^\top$
   has full column rank, $y^\top JM^{-1}J^\top y = 0 \Rightarrow J^\top y = 0 \Rightarrow y = 0$,
   so it is positive definite. Hence the $\Lambda$ of (3) exists.
5. **C3 — delete a hypothesis.** Deleting H2 produces two situations.
   (i) If $J$ is rank-deficient but the constraints are **consistent**
   ($k \in \mathrm{range}(J)$), $\ddot q$ is still unique — the objective of (4) is strongly convex
   and the feasible set is non-empty. But $\lambda$ has as many degrees of freedom as
   $\mathrm{null}(J^\top)$ (**the constraint force is not determined** — this really happens in an
   over-constrained closed loop, where the only measurable quantity is $J^\top\lambda$).
   (ii) If they are inconsistent ($k \notin \mathrm{range}(J)$) there is **no** solution; (2) is a
   contradiction and a numerical solver returns an enormous $\lambda$.
   In both cases the pseudo-inverse form of Udwadia-Kalaba gives the natural answer — the
   least-squares solution of (4) relaxed to $\min\lVert Jx - k\rVert$. Omitted: the derivation of
   the pseudo-inverse form, in the pseudo-inverse section of Udwadia & Kalaba 1992.

### R3 — dynamic consistency is the unique $M$-metric choice

**Hypotheses** H1: $M \succ 0$ and $J$ has full row rank. H2: $A \in \mathbb{R}^{n\times m}$ is a
right inverse of $J$ ($JA = \mathbb{1}_m$). **Conclusion** C:
$JM^{-1}(\mathbb{1} - J^\top A^\top) = 0$ holds for every task **only** when
$A = \bar J = M^{-1}J^\top\Lambda$.

**Strategy**: turn the condition into a linear equation in $A$ and read off uniqueness.

1. **Rearrange the condition.** $JM^{-1}(\mathbb{1} - J^\top A^\top) = 0 \iff JM^{-1} =
   JM^{-1}J^\top A^\top = \Lambda^{-1}A^\top$, that is $A^\top = \Lambda J M^{-1}$, that is
   $A = M^{-1}J^\top\Lambda = \bar J$.
2. **Consistency check.** Does that $A$ satisfy H2?
   $J\bar J = \Lambda^{-1}\Lambda = \mathbb{1}_m$ ✓.
3. **Uniqueness.** Step 1 is a chain of equivalences, so no other $A$ exists. Requiring that
   "null-space torques do not disturb the task" therefore **determines the pseudo-inverse, with
   the $M$ weighting**.
4. **Variational reading.** $\bar J$ is also the solution operator of
   $\min \lVert\dot q\rVert_M^2$ s.t. $J\dot q = \dot x$ (the same shape as (4) in R2). So dynamic
   consistency = minimum kinetic energy = $M$-weighted projection. Omitted: the details of the
   equivalence of the two characterisations (null-space non-interference / minimum energy), in the
   operational-space section of Khatib 1987.
5. **Delete a hypothesis.** If $M = \mathbb{1}$ then $\bar J = J^{+}$ and the geometric
   pseudo-inverse coincides — which is why **mistakenly assuming** a uniform mass hides the
   difference. If $J$ is near a singularity, $\Lambda^{-1}$ is near singular, $\Lambda$ blows up
   and the $F$ of (5) diverges. That is a **dynamic singularity**, and the point at which a damped
   pseudo-inverse (damped least squares) becomes necessary.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ one hour /
★★★ a day or more.

**P1 (derivation, ★★, R1·R2)** (a) Write $\dot J\dot q$ explicitly as a second derivative of
$\phi$ and show that it is quadratic in $\dot q$. (b) Show that if $m = n$ (fully constrained) then
$\ddot q$ becomes independent of $\tau$ in (3), and say what $\lambda$ then means. (c) Rewrite (2)
and (3) in full under the opposite sign convention $M\ddot q + b = \tau - J^\top\lambda$.
*Solution sketch*: (a) expand $\frac{d}{dt}(J\dot q)$ by the chain rule. (b) $J$ is now
invertible, so $\ddot q = J^{-1}k$ — the acceleration is fixed by the geometry alone and all of
$\tau$ is absorbed into $\lambda$. (c) is only $\lambda \to -\lambda$, but the point is to
**write it all out yourself**.

**P2 (derivation, ★★, R4·R5)** (a) Show that the choice of $w$ in (7) does not affect $\ddot q$
(replacing $w$ by $w + Gz$ gives the same $\ddot q$). (b) Say what ODE results from applying
Baumgarte at **velocity level only** ($\alpha > 0$, $\beta = 0$) and what is then not guaranteed.
(c) Write the solution of (9) explicitly at $\alpha = \beta$ and compute $e$ at $t = 0.2$ for
$\dot e_0 = 0$, $e_0 = 10^{-3}$, $\beta = 20$.
*Solution sketch*: for (a), $\ddot u$ adjusts so that $G\ddot u$ absorbs $Gz$ — the solution of
(7) depends **affinely** on $w$ but the sum is invariant. The answer to (c) is
$e(0.2) = 10^{-3}(1 + 4)e^{-4} = 9.158\times10^{-5}$ (within 1% of the measured
$9.075\times10^{-5}$).

**P3 (proof, ★★★, R3)** (a) Show with a concrete 2-DOF example that the "null-space" projection
built from the geometric pseudo-inverse $J^{+} = J^\top(JJ^\top)^{-1}$ **does** produce task
acceleration (you must take $M$ non-diagonal). (b) Prove that $\bar J$ is the solution operator of
$\min\lVert\dot q\rVert_M^2$ s.t. $J\dot q = \dot x$. (c) Show that $\bar J = J^{+}$ only when
$M = \mathbb{1}$, and say by what quantity the difference between the two projections can be
estimated when $M$ is "nearly a scalar multiple" (hint: the condition number of $M$).
*Strategy and key inequality*: for (a) compute $JM^{-1}(\mathbb{1} - J^\top(J^{+})^\top)$ directly
and show it is non-zero. (b) is the same KKT calculation as (4) in R2. The expansion is withheld.

**P4 (proof, ★★★, R1)** (a) Prove that when $J$ is rank-deficient and the constraints are
consistent, $\ddot q$ is unique but $\lambda$ is not. (b) Construct a concrete over-constrained
closed loop (the planar four-bar with one redundant constraint added) and say what is
**physically measurable** in that case. (c) Discuss the physical meaning of the $\ddot q$ given by
the least-squares relaxation of (4) when the constraints are inconsistent — is it the right model?
*Strategy and key inequality*: for (a), separate the strong convexity of (4) (uniqueness) from
$\mathrm{null}(J^\top) \ne \{0\}$ (non-uniqueness). (c) is a trap — the least-squares relaxation is
mathematically tidy, but "inconsistent constraints" usually signal that **the model is wrong**, and
the relaxation hides that fact.

**P5 (numerical, ★, R1·R2·R3)** A planar three-link chain tied by loop closure into a four-bar.
Link lengths $l = (0.5, 0.4, 0.3)$, masses $(1.2, 0.9, 0.6)$, each link a uniform rod (centre of
mass at the midpoint, $\bar I_{zz} = m l^2/12$, other components zero), all joints rotating about
$z$, gravity $9.81$ along $-y$. The constraint fixes the tip at
$P_0 = (1.088822376457,\; 0.223713953272)$ ($= \mathrm{tip}(0.6, -0.9, 0.5)$, so $\phi = 0$ at
$q_0 = (0.6, -0.9, 0.5)$). With
$\dot q_0 = (0.103360934922,\; 0.001584047916,\; -0.386411707799)$ (constraint-consistent,
$\lVert\dot q_0\rVert_2 = 0.4$) and $\tau = (1.5, -0.3, 0.2)$, find $k$, $\Lambda$, $\lambda$ and
$\ddot q$.
*Answer* (tolerance $10^{-9}$):
$k = (0.031910645927,\; 0.006436080303)$,
$\Lambda = \begin{bmatrix} 1.349861612345 & 0.307260140613 \\ 0.307260140613 & 0.266141510828\end{bmatrix}$,
$\lambda = (6.011670352967,\; 2.224022466169)$,
$\ddot q = (-15.157426569392,\; -0.062542538530,\; 56.297092789389)$.
*Checks*: (a) $\lVert J\dot q_0\rVert_\infty < 10^{-13}$; (b)
$\lVert J\ddot q - k\rVert_\infty < 10^{-13}$; (c) $\Lambda$ is symmetric with
$\lambda_{\min}(\Lambda) = 0.185088157799 > 0$; (d) $M\ddot q + b = \tau + J^\top\lambda$ to within
$10^{-12}$.

**P6 (implementation, ★★, R1-R5)** (a) `constrained_accel(q, qd, tau, alpha, beta)` — solve (2)
and return $(\ddot q, \lambda)$. (b) `reduced_accel(q, qd, tau)` — return $\ddot q$ via (7).
(c) `project(q, qd)` — project onto $\phi(q) = 0$ by Newton and project $\dot q$ onto
$\mathrm{null}(J)$. (d) `operational_space(q)` — return $\Lambda$, $\bar J$ and $N^\top$.
*Rubric*: (a) reproduces the numbers of P5 to within $10^{-9}$; (b) the $\ddot q$ of (a) and (b)
agree to within $10^{-12}$; (c) `project` reaches $\lVert\phi\rVert_\infty < 10^{-14}$ within 20
Newton iterations; (d) unit tests check both identities of (6); (e) $J$ is computed
**analytically** (no finite differences) and $\dot J\dot q$ analytically too — with finite
differences, condition 1 of the reproduction task cannot break the $10^{-9}$ wall; (f) the sign
convention is stated in the docstring.

**P7 (paper, ★★, R2·R3)** (a) Compare Khatib 1987's argument for introducing $\bar J$ with the
uniqueness proof of R3 here, and say whether the author claims uniqueness or merely constructs it.
(b) Translate the result of Udwadia & Kalaba 1992 into the KKT conditions of (4) and name two
cases the authors can additionally handle thanks to the **pseudo-inverse**. (c) Does Baumgarte 1972
give guidance for choosing the gains? If not, write a paragraph on why that gap has not been filled
in 55 years, grounded in the table of R5.
*Rubric*: for (b), naming rank deficiency (over-constraint) and inconsistency (contradiction)
passes. For (c), arriving at "integrator error and stabilisation error are mixed together, so the
gains alone cannot decide it" passes. Writing only "the paper is old" does not.

## Paper reading

**Three must-reads**: 1972, 1987 and 1992 — papers that read the same equation (2) from three
directions, **constraint stabilisation**, **control decomposition** and **a variational
principle**. Reading all three with the same questionnaire and summarising in one paragraph
"which part of (2) each took as their own problem" is the reading goal of this lesson. Write a
one-page note on each with the ten fixed questions below (`lesson-standard.md` §5). Read in three
passes and concentrate on questions 4, 7 and 8 in the third pass.

1. **Khatib, "A unified approach for motion and force control of robot manipulators: the
   operational space formulation" (1987, IEEE J. Robotics and Automation)** — role: `seminal`.
   <https://doi.org/10.1109/JRA.1987.1087068>
   Which sections and why: the one that sets up the operational-space equation of motion (5) and
   the one that introduces the dynamically consistent inverse. Compare one-to-one with the
   derivation of R3, concentrating on **which property the author requires in order to choose
   $\bar J$**.
   Extra questions: (a) does the author claim uniqueness of $\bar J$, or only construct it?
   (b) in the claim to "unify" force control and motion control, what exactly is unified?
   (c) how does the author handle dynamic singularities (the blow-up of $\Lambda$)?
2. **Udwadia & Kalaba, "A new perspective on constrained motion" (1992, Proc. R. Soc. A)** — role:
   `standard`. <https://doi.org/10.1098/rspa.1992.0158>
   Which sections and why: the one that starts from Gauss's principle and writes the constrained
   acceleration as a single line with a pseudo-inverse. (4) here is that starting point, and the
   authors' result is (4) **relaxed to least squares**.
   Extra questions: (a) what do the authors' equations become when translated into the $\Lambda$
   and $\bar J$ of this lesson? (b) do they claim an extension to non-holonomic constraints — and
   to what form of constraint is that claim limited? (c) what do they **not** treat (hint:
   inequalities, friction)?
3. **Baumgarte, "Stabilization of constraints and integrals of motion in dynamical systems"
   (1972, Comput. Methods Appl. Mech. Eng.)** — role: `seminal`.
   <https://doi.org/10.1016/0045-7825(72)90018-7>
   Which sections and why: the idea of imposing a stable ODE on the constraint violation, which is
   the whole paper. It is short. (8) and (9) here are its equations, and the reading goal is to
   confirm **what the paper says and does not say about choosing the gains**.
   Extra questions: (a) the author's motivation came from celestial mechanics (conserved integrals
   of Keplerian motion) — what does that change in the transfer to multibody dynamics?
   (b) does the paper recognise the stiffness problem?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) independent and dependent variables and baselines — were the baselines tuned fairly?
(6) do the metrics match the claim; are variance and seeds reported? (7) what is missing for
reproduction? (8) if it were wrong, which assumption would you suspect first? (9) compute and
memory complexity, and real-time feasibility. (10) what would you change to go beyond it in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one notebook CPU core, under five minutes, numpy
(`scipy.linalg` optional). Memory under 200 MB.

Implement the four-bar linkage of P5 **in both ways, with multipliers and with reduced
coordinates**, and satisfy **all four** of the following. No simulator is used.

**The model and the constraint — the core code this lesson provides.** Below is the heart of the
code the numbers in the text came from. $M$ and $b$ come from the previous lessons' `crba` and
`rnea`; $J$ and $\dot J\dot q$ are written **analytically** (with finite differences you cannot
break the $10^{-12}$ wall of condition 1).

```python
L = np.array([0.5, 0.4, 0.3])  # link lengths
MASS = np.array([1.2, 0.9, 0.6])


def tip(q):
    s = np.cumsum(q)
    return np.array([np.sum(L * np.cos(s)), np.sum(L * np.sin(s))])


def tip_jac(q):
    """dp/dq, shape (2, 3). Joint i moves every link k >= i."""
    s = np.cumsum(q)
    J = np.zeros((2, 3))
    for k in range(3):
        for i in range(k + 1):
            J[0, i] += -L[k] * np.sin(s[k])
            J[1, i] += L[k] * np.cos(s[k])
    return J


def tip_jdot_qd(q, qd):
    """Jdot qd: the part of d2p/dt2 that is quadratic in qd."""
    s, sd = np.cumsum(q), np.cumsum(qd)
    return np.array([np.sum(-L * sd**2 * np.cos(s)), np.sum(-L * sd**2 * np.sin(s))])


def constrained_accel(q, qd, tau, alpha=0.0, beta=0.0):
    """Solve (2). Sign convention: M qdd + b = tau + J^T lambda, J qdd = k."""
    M = crba(CHAIN, q)
    b = rnea(CHAIN, q, qd, np.zeros(3), A_GRAV)  # Coriolis + gravity
    J = tip_jac(q)
    k = -tip_jdot_qd(q, qd) - 2 * alpha * (J @ qd) - beta**2 * (tip(q) - P0)
    K = np.block([[M, -J.T], [J, np.zeros((2, 2))]])
    sol = np.linalg.solve(K, np.concatenate([tau - b, k]))
    return sol[:3], sol[3:], M, J, k  # qdd, lambda, M, J, k


def reduced_accel(q, qd, tau):
    """Solve (7): G^T M G udd = G^T (tau - b - M w), then qdd = G udd + w."""
    M = crba(CHAIN, q)
    b = rnea(CHAIN, q, qd, np.zeros(3), A_GRAV)
    J = tip_jac(q)
    G = np.linalg.svd(J)[2][2:].T  # a basis of null(J), shape (3, 1)
    w = np.linalg.pinv(J) @ (-tip_jdot_qd(q, qd))  # any particular solution of J w = k
    udd = np.linalg.solve(G.T @ M @ G, G.T @ (tau - b - M @ w))
    return G @ udd + w


def project(q, qd, tol=1e-14):
    """Coordinate projection: Newton onto phi = 0, then qd onto null(J)."""
    for _ in range(20):
        r = tip(q) - P0
        if np.abs(r).max() < tol:
            break
        q = q - np.linalg.pinv(tip_jac(q)) @ r
    G = np.linalg.svd(tip_jac(q))[2][2:].T
    return q, G @ (G.T @ qd)


def operational_space(q):
    """Lambda, the dynamically consistent inverse, and the null-space projector."""
    M, J = crba(CHAIN, q), tip_jac(q)
    Minv = np.linalg.inv(M)
    Lam = np.linalg.inv(J @ Minv @ J.T)
    Jbar = Minv @ J.T @ Lam
    return Lam, Jbar, np.eye(3) - J.T @ Jbar.T
```

`CHAIN` is the previous lessons' model object (parents $[-1,0,1]$, all axes $z$, tree transforms
$X_{T,k} = \mathrm{Xtrans}(l_{k-1}e_x)$, mass properties from P5), `A_GRAV`
$= (0,0,0,\,0,-9.81,0)$ and `P0` $= \mathrm{tip}(0.6,-0.9,0.5)$. Note that `reduced_accel` does
**not** integrate `udd` — the gauge of $G$ is discontinuous, so the comparison is made only at the
level of $\ddot q$ (the table in R4).

1. **Agreement of the two methods at one point, and constraint satisfaction** — at
   $q_0, \dot q_0, \tau$ (the values of P5),
   $$
   \lVert \ddot q^{\text{KKT}} - \ddot q^{\text{reduced}} \rVert_\infty < 10^{-12},
   \qquad \lVert J\ddot q - k \rVert_\infty < 10^{-13},
   $$
   and reproduce the $\Lambda$, $\lambda$ and $\ddot q$ of P5 to within $10^{-9}$.
   > Measured in the author's environment: $2.1\times10^{-14}$ and $9.5\times10^{-16}$.
   > $J$ and $\dot J\dot q$ must be computed **analytically** to reach that level (P6 (e)).
2. **Gauss's principle of least constraint** — (a) the normal-equation residual
   $\lVert M(\ddot q - a_u) - J^\top\lambda\rVert_\infty < 10^{-12}$ (measured
   $1.0\times10^{-14}$). (b) Compute $\lVert\ddot q - a_u\rVert_M$ (measured $5.523095$) and show
   that the $M$-norms of the **feasible** points displaced along $\mathrm{null}(J)$ by
   $\epsilon \in \{\pm0.1, \pm0.3, \pm 1\}$ are all **strictly larger** (measured: $5.523133$ at
   $\epsilon = 0.1$, $5.523434$ at $\epsilon = -0.3$). Confirm at the same time that the displaced
   points still satisfy $\lVert Jx - k\rVert_\infty < 10^{-14}$.
   > Caution: trying to verify (b) with a numerical optimiser (SLSQP and the like) stalls at **the
   > optimiser's own tolerance** (typically around $10^{-6}$). Verify with the normal equations (a).
3. **Operational-space inertia and dynamic consistency** — for $\Lambda$, $\bar J$ and $N^\top$,
   $$
   \lVert J\bar J - \mathbb{1}_m\rVert_\infty < 10^{-14}, \qquad
   \lVert JM^{-1}N^\top\rVert_\infty < 10^{-13},
   $$
   with $\Lambda = \Lambda^\top$ holding **exactly** and $\lambda_{\min}(\Lambda) > 0$.
   > Measured: $8.5\times10^{-16}$, $7.2\times10^{-15}$, symmetry error $0.0$,
   > $\lambda_{\min} = 0.185$.
   Then compute the same quantity for the projection built from the geometric pseudo-inverse
   $J^{+}$ and show that
   $\lVert JM^{-1}(\mathbb{1} - J^\top(J^{+})^\top)\rVert_\infty > 10^{-2}$ — **the step that
   confirms numerically that the $M$ metric is needed**.
4. **Integration: compare the constraint violation four ways (2 s, $\Delta t = 10^{-3}$)** —
   (a) **RK4 + Baumgarte $\alpha = \beta = 20$**: $\max\lVert\phi\rVert_\infty < 10^{-8}$ and
   $\max\lVert J\dot q\rVert_\infty < 10^{-6}$ (measured $1.9\times10^{-9}$ and
   $6.4\times10^{-8}$). **This is the blueprint's "constraint violation < 1e-8" condition, and it
   holds only once the integrator is named.**
   (b) **semi-implicit Euler + the same Baumgarte**: must **fail** the same criterion
   ($\max\lVert\phi\rVert > 10^{-4}$; measured $2.2\times10^{-3}$). This is the step that shows the
   bottleneck is the integrator, not the stabilisation.
   (c) **Any integrator + coordinate projection** (Baumgarte off):
   $\max\lVert\phi\rVert_\infty < 10^{-12}$ and $\max\lVert J\dot q\rVert_\infty < 10^{-12}$
   (measured $\approx 10^{-14}$ for both).
   (d) **The Baumgarte error ODE itself**: inject an error of $10^{-3}$ into $\phi$
   ($q \leftarrow q + J^{+}(10^{-3}, 0)^\top$) and integrate with $\alpha = \beta = 20$, RK4 at
   $\Delta t = 10^{-4}$; at $t \in \{0.05, 0.1, 0.2, 0.4\}$ the value of $\lVert\phi\rVert$ must
   agree with $e_0(1 + \beta t)e^{-\beta t}$ to within a **relative error of 2%**.
   > Measured: $7.308\times10^{-4}$ at $t = 0.05$ (predicted $7.336\times10^{-4}$),
   > $4.028\times10^{-4}$ at $t = 0.1$ (predicted $4.048\times10^{-4}$),
   > $9.075\times10^{-5}$ at $t = 0.2$ (predicted $9.131\times10^{-5}$),
   > $2.990\times10^{-6}$ at $t = 0.4$ (predicted $3.010\times10^{-6}$).

**Input data**: no external data needed; every model constant is written out in P5. It is better to
**compute** $P_0$ as $\mathrm{tip}(0.6,-0.9,0.5)$ so that $\phi(q_0) = 0$ without rounding.

**Baselines** (at least one):
- First choice: multipliers versus reduced coordinates (condition 1) — two completely independent
  routes.
- Second choice: the normal equations of condition 2 (derived independently from the variational
  problem).
- Optional check (not required to pass): agreement to within $10^{-10}$ with `pinocchio`'s
  `pin.forwardDynamics` (with constraints) or with Featherstone's closed-loop examples.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| Condition 1 cannot break the $10^{-9}$ wall | $J$ or $\dot J\dot q$ was computed by finite differences | Switch to the analytic form and see whether the error drops to $10^{-14}$ |
| The sign of $\lambda$ is reversed | The convention $M\ddot q + b = \tau \pm J^\top\lambda$ | Check whether $\ddot q$ is right and only $\lambda$ wrong — then it is the convention |
| Only the reduced-coordinate side of condition 1 is wrong | $w$ (a particular solution of $Jw = k$) was omitted and $\ddot q = G\ddot u$ used | See whether it is right at a state with $k = 0$ ($\dot q = 0$) and wrong for $\dot q \ne 0$ |
| The reduced-coordinate result jumps from step to step | The **gauge** of $G$ — the signs and column order from SVD/QR are discontinuous | Compare only at the level of $\ddot q$ and do not integrate $\ddot u$ |
| The $N^\top$ check of condition 3 fails | $\bar J^\top$ was transposed **again** instead of being written as $\Lambda J M^{-1}$ | Verify by hand, using the symmetry of $\Lambda$ and $M$, that the two expressions agree |
| Condition 4 (a) sits at the $10^{-6}$ level | The Baumgarte terms were evaluated **once** inside RK4 (they must be re-evaluated per stage) | Check that $\phi$ and $\dot\phi$ are recomputed from each stage's state |
| Condition 4 (c) fails | $\dot q$ was left out of the projection (only $q$ was returned to the manifold) | Track $\lVert J\dot q\rVert$ separately — if $\phi$ is small and only $\dot\phi$ large, that is it |
| Condition 4 (d) is off by more than 10% | $\dot e_0 \ne 0$ but it was compared against the $\dot e_0 = 0$ formula | Print $\dot\phi = J\dot q$ right after the injection to check it is zero, and otherwise use the general solution |
| It diverges when $\beta$ is increased | Stiffness — outside the stability region of the explicit integrator | Print $\beta\Delta t$ and halve $\beta$ |

## Open problems

- **(open problem) A principled choice of stabilisation gains** — Baumgarte's (9) is a 55-year-old
  equation and still the standard, but there is no **principled** way to choose $\alpha$ and
  $\beta$. The table in R5 shows why: the actual constraint error is the sum of the stabilisation
  error and the integrator error, and raising the gains reduces the former while making the system
  stiff and raising the latter. The gain that minimises both depends on the integrator, the step
  and the mechanism, and no model captures that dependence. Current approaches: projection and
  post-stabilisation, which **avoid** the choice of gains, and Lie-group integrators that satisfy
  the constraint structurally. What is missing: a procedure for choosing the gains given an
  integrator and a step size.
- **(open problem) The distribution of constraint forces in over-constrained systems** — as C3(i)
  of R1 shows, $\lambda$ is not unique when $J$ is rank-deficient. Real machines are often
  over-constrained (a spatial realisation of a planar four-bar, a multi-fingered grasp, a
  quadruped), and the constraint forces that actually flow are then decided by **stiffness**
  (compliance) — a quantity a rigid-body model cannot answer in principle. The convention of
  taking the minimum-norm $\lambda$ is mathematical convenience with no physical basis. Current
  approaches: formulations that model compliance explicitly, and stiffness-weighted minimum norm.
  What is missing: bounds usable without knowing the compliance.
- **(open problem) Operational-space control near a singularity** —
  $\Lambda = (JM^{-1}J^\top)^{-1}$ blows up at a **dynamic singularity** where $J$ loses rank, and
  a damped pseudo-inverse leaves task error behind. The optimal trade-off of "how much task to
  give up for how much stability" is open in general — especially the comparison between avoiding
  and passing through a singularity when redundancy makes **avoidance possible**. Current
  approaches: damped least squares, and hierarchical control that puts singularity avoidance into
  the null space (the family built by stacking the decomposition of
  [Khatib 1987](https://doi.org/10.1109/JRA.1987.1087068)). What is missing: global optimality for
  singularity-crossing trajectories.

## Concept check

Run `rc quiz c2-constrained-dynamics`. The quiz is for **concept checking only**; the real work is
the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: which assumptions make the KKT matrix non-singular; what Gauss's principle
of least constraint says is minimised; why the dynamically consistent pseudo-inverse is used;
whether Baumgarte stabilisation can keep the constraint violation arbitrarily small; and why the
multiplier disappears in the reduced-coordinate form.

## How to study this stage

1. **Pin down the sign convention first (15 min)** — write (1) on paper and note that $\lambda$ is
   "the force acting on the system". Half the bugs in this lesson are conventions, and this is the
   first place to look when matching external code.
2. **Solve (2) by Schur complement, by hand (40 min)** — two moves: eliminate $\ddot q$ to get
   $\lambda$, then substitute back. See for yourself that
   $\Lambda = (JM^{-1}J^\top)^{-1}$ and $\bar J = M^{-1}J^\top\Lambda$ **appear in the middle of
   the calculation** — then it is clear that R3 is not a new concept but another reading of the
   same algebra.
3. **Memorise the proof of R1 as three lines (30 min)** —
   $x^\top Mx = (Jx)^\top y = 0$ → $x=0$ → $J^\top y = 0$ → $y = 0$. Then **delete the hypotheses
   one at a time** and write down what breaks (problem P4). The fact that $\lambda$ is
   undetermined in an over-constrained system is something you will certainly meet in a lab.
4. **Confirm Gauss's principle numerically (40 min)** — do condition 2 (b) of the reproduction task
   first. Seeing in numbers that a **feasible** acceleration displaced slightly along
   $\mathrm{null}(J)$ has a larger $M$-norm leaves you with (4) as an equation, not a metaphor.
   Resist the temptation to verify with an optimiser — only the normal equations reach $10^{-14}$.
5. **Implement $J^{+}$ and $\bar J$ side by side (50 min)** — apply both projections to the same
   task and compare the task accelerations. Seeing $J^{+}$ disturb the task when $M$ is
   non-diagonal engraves "in dynamics the right metric is $M$" permanently.
6. **Run condition 4 of the reproduction task four times (90 min)** — (a), (b), (c) and (d) each
   say something different. In particular (b) is a condition that **passes by failing**. Put the
   four results in one table, compare with the table in R5, and decompose "constraint error =
   stabilisation error + integrator error" with your own numbers.
7. **Read the three papers around (2) (150 min)** — Khatib → Udwadia-Kalaba → Baumgarte is a good
   order (general → variational → numerical). For each, write one line on "which part of (2) this
   author took as their own problem", then merge the three lines into one paragraph.
8. **End with what cannot be done (25 min)** — pick the over-constraint open problem and write a
   paragraph on what quantity a rigid-body model cannot answer in principle. That paragraph is half
   the reason why **inequalities** are needed in the contact lesson (`c2-contact-dynamics`).

**Passing bar**: you can write (2), (3), (6), (7) and (9) from a blank page; you can state the
three-line proof of R1 and the uniqueness argument of R3; you have both implementations —
multipliers and reduced coordinates — passing all four conditions of the reproduction task; and you
have one-page notes on all three papers.
