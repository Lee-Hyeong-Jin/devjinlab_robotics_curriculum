---
id: c2-contact-dynamics
lang: en
title: Contact dynamics and complementarity
summary: >-
  Set up unilateral contact as a complementarity condition and treat at the level of proof why a
  velocity-level time-stepping scheme is a solvable problem while the acceleration level need not
  be. Derive the critical friction coefficient of the friction cone and the Painlevé paradox in
  closed form ($\mu_{\mathrm{crit}} = 4/3$), and decompose numerically the energy non-increase of
  the contact impulse and the order of non-penetration.
objectives:
  - Write contact as complementarity conditions at position, velocity and acceleration level and explain why they are inequalities rather than equalities.
  - Show that frictionless velocity-level time stepping is a positive-semidefinite LCP and prove that a solution exists.
  - Derive the inconsistency (Painlevé) condition of acceleration-level Coulomb friction and find the critical $\mu$ of a uniform rod in closed form.
  - Prove from complementarity and maximum dissipation that a contact impulse does not increase kinetic energy.
  - Derive that non-penetration holds to first order with a residual penetration of $O(h^2)$, and confirm it numerically.
tags: [multibody-dynamics, contact, complementarity, lcp, friction, painleve, research]
---

# Contact dynamics and complementarity

## Setup and notation

The results of `c2-constrained-dynamics` are assumed, in particular the KKT form (2), the
Delassus operator $\Lambda^{-1} = JM^{-1}J^\top$, and the principle of virtual work saying that
**the constraint force is normal to the constraint**. Exactly **one** thing changes in this
lesson: the constraint goes from the equality $\phi = 0$ to the **inequality** $g \ge 0$, and as a
result the linear system becomes a **complementarity problem**.

| Symbol | Meaning |
|---|---|
| $g(q) \in \mathbb{R}^{n_c}$ | The gap function; $g_i \ge 0$ is non-penetration, $g_i = 0$ is contact |
| $J_n := \partial g/\partial q$ | The normal Jacobian; $v_n := J_n\dot q$ is the normal approach velocity |
| $J_t$ | The tangential Jacobian: one row in the plane, two in space |
| $\lambda_n \ge 0$, $\lambda_t$ | Normal and tangential **forces** (acceleration level) |
| $p_n \ge 0$, $p_t$ | Normal and tangential **impulses** (velocity level); $p = h\lambda$ in the smooth case |
| $\mu \ge 0$ | The Coulomb friction coefficient |
| $0 \le a \perp b \ge 0$ | Complementarity: $a \ge 0$, $b \ge 0$, $a^\top b = 0$ |
| $A := J M^{-1} J^\top$ | The Delassus operator (with $J = [J_n; J_t]$); positive semidefinite |
| $h$ | The integration step |
| $v^-, v^+$ | Generalised velocity at the start and end of the step; $v_f := v^- + hM^{-1}(\tau - b)$ is the **free velocity** |

Assumptions and scope: rigid bodies (no deformation), point contact, isotropic Coulomb friction,
restitution zero (perfectly inelastic — restitution is problem P2). No simulator is used; every
number is obtained by solving the problem directly in numpy.

**How to read the complementarity symbol**: $0 \le p_n \perp v_n^+ \ge 0$ bundles three
conditions. (a) There is no pulling force ($p_n \ge 0$); (b) nothing penetrates
($v_n^+ \ge 0$); (c) **one of the two is zero** ($p_n v_n^+ = 0$: if it is separating there is no
force, and if there is a force it is not separating). It is (c) that makes an inequality
constraint a **non-smooth** problem, and every difficulty in this lesson comes from there.

## Key results

The bracketed grade is the derivation depth (D0 cited / D1 sketched / D2 full derivation /
D3 proof — see `lesson-standard.md` §2 in the track design notes).

- **R1 (complementarity at three levels) [D2]** — at position level contact is
  $$
  0 \le g(q) \perp \lambda_n \ge 0, \tag{1}
  $$
  and at an active contact with $g_i = 0$, differentiating gives the **velocity level**
  $0 \le v_n \perp p_n \ge 0$ and, differentiating again, the **acceleration level**
  $0 \le \dot v_n \perp \lambda_n \ge 0$. Friction is written with a cone and **maximum
  dissipation**:
  $$
  \lVert \lambda_t\rVert \le \mu\lambda_n, \qquad
  \lambda_t \in \arg\min_{\lVert z\rVert \le \mu\lambda_n} \; v_t^\top z. \tag{2}
  $$
  The second expression in (2) is a one-line statement of "if it slips, friction saturates
  opposite to the slip; if it is at rest, anything inside the cone is possible".
- **R2 (velocity-level time stepping and existence of a solution) [D3]** — write one step as
  $$
  M(v^+ - v_f) = J_n^\top p_n + J_t^\top p_t, \qquad
  0 \le p_n \perp \Big(J_nv^+ + \frac{g}{h}\Big) \ge 0, \qquad \text{plus the discrete form of } (2). \tag{3}
  $$
  **Without friction** ($\mu = 0$), (3) is a **monotone LCP** with matrix
  $A_n = J_nM^{-1}J_n^\top \succeq 0$, and therefore **a solution always exists**. With friction
  the LCP matrix becomes non-symmetric and the acceleration level may have no solution (R3), but
  **the velocity-level problem (3) is still solvable** — which is what the title of
  Anitescu-Potra 1997 asserts.
- **R3 (the friction cone and the Painlevé paradox) [D2]** — at acceleration level, if the contact
  point slips in the $+t$ direction then $\lambda_t = -\mu\lambda_n$ and the gap acceleration is
  $$
  \ddot g = \underbrace{\big(J_nM^{-1}J_n^\top - \mu\,J_nM^{-1}J_t^\top\big)}_{=:\,a}\lambda_n
    + \ddot g_{\text{free}}. \tag{4}
  $$
  If $a \le 0$ and $\ddot g_{\text{free}} < 0$ then **no $\lambda_n \ge 0$ can make
  $\ddot g \ge 0$** — no solution exists (the Painlevé paradox). For a uniform rod of mass $m$ and
  length $2l$ slipping on its lower end,
  $$
  a = \frac{1}{m}\Big[\big(1 + 3\cos^2\theta\big) - 3\mu\,\lvert\sin\theta\rvert\cos\theta\Big],
  \qquad
  \mu_{\mathrm{crit}} = \min_{\theta}\frac{1+3\cos^2\theta}{3\lvert\sin\theta\rvert\cos\theta} = \frac{4}{3}, \tag{5}
  $$
  the minimum being attained at $\theta = -\arctan 2 \approx -63.4349^\circ$. So **for
  $\mu > 4/3$ this mechanism is inconsistent at acceleration level**.
- **R4 (a contact impulse does not increase energy) [D2]** — at the solution of (3),
  $$
  \tfrac{1}{2}v^{+\top}Mv^+ - \tfrac{1}{2}v_f^\top M v_f \;=\; -\tfrac{1}{2}\lVert v^+ - v_f\rVert_M^2 + (v^+)^\top\!\big(J_n^\top p_n + J_t^\top p_t\big) \;\le\; 0, \tag{6}
  $$
  because complementarity gives $v_n^{+\top}p_n \le 0$ and maximum dissipation gives
  $v_t^{+\top}p_t \le 0$. Contact is therefore **dissipative**, and this is the first thing to
  check in a numerical experiment.
- **R5 (the order of non-penetration, and convex relaxation) [D2; the design of the relaxation is D1]** —
  the $g/h$ term in (3) guarantees $g^{k+1} \ge 0$ only to **first order**. For a geometry with
  constant $J_n$ (a disk on a plane) the penetration is **exactly zero**, but when $J_n$ depends on
  the configuration an $O(h^2)$ penetration remains (measured: for one step of the rod, halving
  $h$ reduces the penetration by a factor of $3.9{-}4.0$). Separately, **relaxing** the
  complementarity of (3) into a strongly convex problem (the MuJoCo family) makes the solution
  unique and makes $v^+ \mapsto p$ **invertible**, so that it can be used in control and
  estimation — at the price of a small non-physical slip in static friction. **[D1]**

## Derivation

### R1 — why an inequality rather than an equality

The constraints of the previous lesson were bilateral: $\phi = 0$, and the constraint force
$\lambda$ was **free in sign** (a joint can push both ways). Contact is **unilateral** — the floor
can only push, never pull. That single physical fact produces three conditions:

1. **Non-penetration**, $g(q) \ge 0$.
2. **No tension**, $\lambda_n \ge 0$ (the normal force can only push away).
3. **Complementarity**, $g\,\lambda_n = 0$ — if it is separated ($g > 0$) there is no force, and
   if there is a force ($\lambda_n > 0$) it is touching. Without this condition, a solution in
   which "the floor pushes up an object floating in the air" would be admissible.

Bundling the three gives (1). At an **active** contact, where $g$ is already zero, differentiate to
lower the level: $\dot g = J_n\dot q = v_n$, maintaining contact requires $v_n \ge 0$, and if it is
separating ($v_n > 0$) the force must be zero, so $0 \le v_n \perp \lambda_n \ge 0$. One more
differentiation gives the acceleration level.

**Why lower the level, and at what cost.** The position-level (1) is a nonlinear complementarity
problem (NCP) in $q$ and is hard to solve within one step. The velocity level is **linear in
$v^+$**, so it becomes an LCP solvable by a finite algorithm (Lemke) — which is why practice uses
the velocity level. The cost is that $g$ is not controlled directly, and the $g/h$ term in (3) is
the correction (the same role as the position term of Baumgarte in the previous lesson, with the
same first-order limitation).

**Reading friction (2).** The principle of maximum dissipation says "friction picks, within the
given cone, the force that maximises dissipation". The solution of
$\min_{\lVert z\rVert\le\mu\lambda_n} v_t^\top z$ is
$z = -\mu\lambda_n\,v_t/\lVert v_t\rVert$ when $v_t \ne 0$ (saturated on the boundary,
**opposite to the slip**), and when $v_t = 0$ the objective is zero so **the whole cone is the
solution set** (the indeterminacy of static friction). Those two are the **sliding** and
**sticking** modes.

### R2 — one velocity-level step, and mode enumeration

From the first equation of (3), $v^+ = v_f + M^{-1}(J_n^\top p_n + J_t^\top p_t)$, so the normal
and tangential velocities are **affine** functions of the impulses:

$$
\begin{bmatrix} v_n^+ \\ v_t^+\end{bmatrix}
= \begin{bmatrix} J_nv_f \\ J_tv_f\end{bmatrix}
+ \underbrace{\begin{bmatrix} a_{nn} & a_{nt} \\ a_{tn} & a_{tt}\end{bmatrix}}_{A\,=\,JM^{-1}J^\top}
\begin{bmatrix} p_n \\ p_t\end{bmatrix}. \tag{7}
$$

With one contact in the plane there are only two unknowns $(p_n, p_t)$, so the problem can be
solved exactly by **enumerating the modes**. There are exactly three:

- **separate**: $p_n = p_t = 0$. This is the answer when $J_nv_f + g/h \ge 0$.
- **stick**: solve $v_n^+ = -g/h$ together with $v_t^+ = 0$ for $(p_n, p_t)$, then check
  $p_n \ge 0$ and $\lvert p_t\rvert \le \mu p_n$ (inside the cone).
- **slide** (with sign $s = \pm1$): assume $p_t = -s\,\mu p_n$ and get, from $v_n^+ = -g/h$,
  $$
  p_n = \frac{-g/h - J_nv_f}{a_{nn} - s\,\mu\,a_{nt}},
  $$
  then check $p_n \ge 0$ and $\operatorname{sign}(v_t^+) = s$ (the result agrees with the assumed
  slip direction).

The point is that **enumeration is the same thing as solving the LCP** — the solution of an LCP is
the problem of choosing which of the complementary pairs is active on which side, and with one
planar contact there are only three such combinations. With $n_c$ contacts the combinations grow
exponentially and enumeration becomes impossible, which is why algorithms such as Lemke or
projected Gauss-Seidel are needed — but **what they solve is the same thing**.

> **(7) numerically** (the disk of the reproduction task: $m = 1$, $R = 0.2$,
> $I = \tfrac12 mR^2 = 0.02$): $a_{nn} = 1$, $a_{tt} = 3$, $a_{nt} = 0$. Normal and tangential are
> **decoupled** (a peculiarity of the disk — problem P1 (c)), which is why $p_n$ is independent of
> $\mu$. The rod has $a_{nt} \ne 0$ and is coupled, and **that coupling is the cause of Painlevé**.

### R3 — the critical friction coefficient of Painlevé in closed form

A uniform rod: mass $m$, length $2l$, centre $(x, y)$, angle $\theta$, $q = (x, y, \theta)$,
$M = \operatorname{diag}(m, m, I)$ with $I = \tfrac{1}{12}m(2l)^2 = \tfrac{1}{3}ml^2$. Its lower
end $P = (x - l\cos\theta,\; y - l\sin\theta)$ touches the floor $y = 0$, so

$$
g = y - l\sin\theta, \qquad
J_n = \big[\,0,\; 1,\; -l\cos\theta\,\big], \qquad
J_t = \big[\,1,\; 0,\; l\sin\theta\,\big].
$$

Compute the Delassus entries. Since $M^{-1} = \operatorname{diag}(1/m, 1/m, 1/I)$,

$$
a_{nn} = J_nM^{-1}J_n^\top = \frac{1}{m} + \frac{l^2\cos^2\theta}{I} = \frac{1 + 3\cos^2\theta}{m},
$$
$$
a_{nt} = J_nM^{-1}J_t^\top = \frac{(-l\cos\theta)(l\sin\theta)}{I} = \frac{-3\sin\theta\cos\theta}{m},
$$

substituting $I = ml^2/3$. If the contact point slips in $+t$, the coefficient in (4) is

$$
a = a_{nn} - \mu\,a_{nt} = \frac{1}{m}\Big[(1+3\cos^2\theta) + 3\mu\sin\theta\cos\theta\Big].
$$

For $a \le 0$ we need $\sin\theta\cos\theta < 0$ — the rod must be **tilted in the direction of
slip**. Taking $\theta \in (-\pi/2, 0)$ ($\sin\theta < 0$, $\cos\theta > 0$) and writing
$c = \cos\theta$, $\lvert s\rvert = -\sin\theta$,

$$
a \le 0 \iff \mu \ge \frac{1+3c^2}{3\lvert s\rvert c} =: f(\theta),
$$

which is (5). Minimise $f$ **in closed form**. Substituting $t := \tan\lvert\theta\rvert > 0$, so
that $c^2 = 1/(1+t^2)$ and $\lvert s\rvert c = t/(1+t^2)$,

$$
f = \frac{1 + 3/(1+t^2)}{3t/(1+t^2)} = \frac{(1+t^2) + 3}{3t} = \frac{t^2 + 4}{3t},
\qquad
\frac{df}{dt} = \frac{3t^2 - 12}{9t^2} = 0 \iff t = 2.
$$

At $t = 2$, $f = (4+4)/6 = 4/3$, and this is the only critical point for $t > 0$ while
$f \to \infty$ as $t \to 0^+$ and $t \to \infty$, so it is the minimum. Therefore

$$
\mu_{\mathrm{crit}} = \frac{4}{3}, \qquad \theta^{*} = -\arctan 2 = -63.434948823^\circ.
$$

**Where the assumption breaks — what the paradox is.** The paradox is not that the **physics** is
contradictory but that the **model** is. Holding rigidity, Coulomb friction and the acceleration
level all at once can leave the solution set empty. Releasing any one of the three resolves it:
(a) release rigidity (compliant contact) and a solution exists; (b) release the acceleration level
(impulses, the velocity level) and a solution exists — **R2 is that route**; (c) release Coulomb
(regularised friction) and a solution exists. Practice almost always takes (b), and the Painlevé
situation is then resolved as an **impulsive stick** (measured: at $\theta^{*}$ with $\mu = 2$ the
acceleration level gives $\lambda_n = -12.2625 < 0$, inconsistent, while one velocity-level step
gives a **stick** solution with $p_n = 0.3083$ and $p_t = -0.4029$).

### R4 — energy non-increase

Write $\Delta v := v^+ - v_f = M^{-1}(J_n^\top p_n + J_t^\top p_t)$ and expand the change in
kinetic energy:

$$
\tfrac12 v^{+\top}Mv^+ - \tfrac12 v_f^\top Mv_f
= \tfrac12(v^+ + v_f)^\top M\,\Delta v
= (v^+)^\top M\Delta v - \tfrac12\Delta v^\top M\Delta v,
$$

(the middle equality by substituting $v_f = v^+ - \Delta v$). Since
$M\Delta v = J_n^\top p_n + J_t^\top p_t$,

$$
\tfrac12 v^{+\top}Mv^+ - \tfrac12 v_f^\top Mv_f
= \underbrace{v_n^{+\top}p_n}_{\le\,0} + \underbrace{v_t^{+\top}p_t}_{\le\,0}
  - \underbrace{\tfrac12\lVert\Delta v\rVert_M^2}_{\ge\,0} \;\le\; 0,
$$

which is (6). Check the sign of each of the three terms:

- $v_n^{+\top}p_n$: complementarity $0 \le p_n \perp (v_n^+ + g/h) \ge 0$ gives
  $p_n^\top(v_n^+ + g/h) = 0$, hence $v_n^{+\top}p_n = -p_n^\top g/h \le 0$ (as $p_n \ge 0$ and
  $g \ge 0$). **When the contact is already established with $g = 0$ it is exactly zero.**
- $v_t^{+\top}p_t$: by maximum dissipation (2), $p_t$ minimises $v_t^{+\top}z$ over the cone and
  $z = 0$ is admissible, so $v_t^{+\top}p_t \le 0$.
- The last term is non-negative because $M \succ 0$ — it is the **dissipation of the impulse
  itself**, exactly the energy lost in a perfectly inelastic collision.

> **(6) numerically**: feeding the disk in contact with $5\times10^4$ random pre-velocities and
> $\mu \sim U(0,1)$, over the $25{,}031$ steps where an impulse actually occurred the **maximum**
> change in kinetic energy is $-3.02\times10^{-6}$ (that is, all of them strictly negative). On
> separating steps it is exactly zero.

### R5 — the order of non-penetration, and convex relaxation

The complementarity in (3) requires $v_n^+ + g/h \ge 0$, so at an active contact $v_n^+ = -g/h$
and $g^{k+1} \approx g + h v_n^+ = 0$ — non-penetration holds **to first order**. A second-order
term remains because $J_n$ depends on $q$:
$g^{k+1} = g + hJ_n v^+ + \tfrac{h^2}{2}\dot J_nv^+ + O(h^3)$.

So for a geometry where $J_n$ is **constant** (a disk on a flat floor — the normal does not depend
on the configuration) the penetration is exactly zero, and for a geometry where $J_n$ depends on
the configuration (the rod) an $O(h^2)$ penetration remains. The measurements:

| Geometry | $h$ | Gap after one step | Ratio |
|---|---|---|---|
| Rod, $\mu=2$, $\theta^{*}$ | $4\times10^{-3}$ | $-6.1842\times10^{-6}$ | — |
| Rod | $2\times10^{-3}$ | $-1.5778\times10^{-6}$ | $3.92$ |
| Rod | $1\times10^{-3}$ | $-3.9846\times10^{-7}$ | $3.96$ |
| Rod | $5\times10^{-4}$ | $-1.0012\times10^{-7}$ | $3.98$ |
| Rod | $2.5\times10^{-4}$ | $-2.5093\times10^{-8}$ | $3.99$ |
| Disk, $\mu=0.3$, 2 s | $10^{-3}$ … $2.5\times10^{-4}$ | $0$ (exactly) | — |

The ratio converges to 4, so the penetration is exactly $O(h^2)$. The practical prescription is the
same as in the previous lesson: if non-penetration has to be tight, **project** at the end of the
step.

**Convex relaxation (the Todorov 2014 family).** (3) has two problems because of the
complementarity: (a) the solution may not be unique, and (b) $p \mapsto v^+$ is non-smooth, so
**the derivative is undefined or there is no inverse map**. The relaxation turns the contact
problem into a strongly convex QP — schematically,

$$
p = \arg\min_{p\,\in\,\mathcal{K}} \; \tfrac12 p^\top A p + p^\top Jv_f + \tfrac12 p^\top R p,
$$

where $\mathcal{K}$ is the (linearised or conic) friction set and $R \succ 0$ is a regulariser.
What is gained: a **unique solution**, **$C^1$ dependence** (essential for trajectory optimisation
and differentiable simulation), and **invertibility** of $v^+ \mapsto p$ (invertible analytically —
the "analytically-invertible" of the paper's title). What is lost: because $R \ne 0$, a small
**non-physical slip** appears in static friction (a boundary layer), and the size of $R$ directly
sets the trade-off between model error and numerical stability. **[D1]**

## Proof sketch

### R2 — the frictionless velocity-level LCP is always solvable

**Hypotheses** H1: $M \succ 0$. H2: $\mu = 0$ (frictionless). H3: $g \ge 0$ (no penetration at the
start of the step). **Conclusions** C1: (3) is an LCP with $A_n = J_nM^{-1}J_n^\top \succeq 0$ and
**a solution exists**. C2: if $J_n$ has full row rank then $v_n^+$ is unique; if it is
rank-deficient, $p_n$ may not be. C3: which hypothesis breaks, and how, when friction is added.

**Strategy**: put the problem in standard LCP form and use the solvability of a
positive-semidefinite LCP (Cottle-Pang-Stone). That solvability is shortest to see through the
equivalent **convex QP**.

1. **Standard form.** By H2, $p_t = 0$, so only the normal block of (7) remains:
   $$
   w := v_n^+ + \frac{g}{h} = A_np_n + \underbrace{\Big(J_nv_f + \frac{g}{h}\Big)}_{=:\,c},
   \qquad 0 \le p_n \perp w \ge 0.
   $$
   This is $\mathrm{LCP}(A_n, c)$.
2. **$A_n \succeq 0$.** It is a congruence of $M^{-1} \succ 0$, so
   $x^\top A_nx = \lVert J_n^\top x\rVert^2_{M^{-1}} \ge 0$. (If $J_n$ is rank-deficient, equality
   is possible, so it is **not positive definite** — that is the case of redundant contacts.)
3. **The equivalent convex QP.** When $A_n \succeq 0$, the solutions of
   $\mathrm{LCP}(A_n, c)$ coincide **exactly** with the KKT points of
   $$
   \min_{p_n \ge 0} \; \tfrac12 p_n^\top A_n p_n + c^\top p_n
   $$
   (writing the KKT conditions gives $A_np_n + c \ge 0$, $p_n \ge 0$,
   $p_n^\top(A_np_n+c) = 0$). The objective is convex and the feasible set $\{p_n \ge 0\}$ is
   non-empty, so a minimiser exists **provided the objective is bounded below**.
4. **It is bounded below.** With $A_n \succeq 0$, the only way the objective is unbounded below is
   a direction $d$ with $A_nd = 0$, $c^\top d < 0$ and $d \ge 0$. But $A_nd = 0$ means, by step 2,
   that $J_n^\top d = 0$, and then
   $c^\top d = d^\top J_nv_f + d^\top g/h = (J_n^\top d)^\top v_f + d^\top g/h = d^\top g/h \ge 0$
   (by H3 and $d \ge 0$). Contradiction, so it is bounded below and a solution exists — C1.
5. **Uniqueness (C2).** $v_n^+$ and $v^+$ are **unique**, since the QP's objective depends on
   $p_n$ only through $J_n^\top p_n$. If $J_n$ is rank-deficient, several $p_n$ keep
   $J_n^\top p_n$ the same, so **the distribution of the impulse is not unique** — the same
   phenomenon as the over-constraint of R1 in the previous lesson, and exactly the case of the
   four feet of a quadruped.
6. **C3 — adding friction.** With friction, normal and tangential couple through (7), and in the
   sliding mode the effective matrix $a_{nn} - s\mu a_{nt}$ becomes **non-symmetric**. A
   non-symmetric matrix need not be positive semidefinite, and indeed by (5) it becomes negative
   when $\mu > 4/3$, which destroys the convexity of step 3. **At the acceleration level** a
   solution may therefore fail to exist (R3). At the **velocity level** (3), if the sliding mode is
   infeasible the **sticking mode** remains, and the matrix of the sticking mode is a principal
   submatrix of $A$ and hence positive semidefinite, so a solution exists — that structure is the
   skeleton of the solvability proof of Anitescu-Potra 1997.
   (Omitted: the general proof for multiple contacts and polyhedral cones, in the solvability
   theorem of Anitescu & Potra 1997. That paper keeps the problem an LCP by using a linearised
   (polyhedral) cone — **linearising the cone is the price paid for solvability**.)

**Delete a hypothesis**: deleting H3 ($g \ge 0$) breaks step 4 — from an already-penetrating state
($g < 0$) it is possible to have $c^\top d < 0$ and the LCP can be infeasible. So an
implementation must either forbid penetration at the start of a step or clip $g$ to
$\max(g, 0)$ (see the diagnosis table). Deleting H1 ($M \succ 0$) leaves step 2's congruence
argument with only semidefiniteness and breaks the lower-boundedness of step 3.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ one hour /
★★★ a day or more.

**P1 (derivation, ★★, R1·R2)** (a) From the principle of maximum dissipation (2), find the
solution sets of the sliding and sticking cases explicitly. (b) In a spatial (3D) contact, where
$J_t$ has two rows and the cone is $\lVert\lambda_t\rVert_2 \le \mu\lambda_n$, count how many modes
arise when the cone is **linearised into a polyhedron** with $k$ facets. (c) Give the **geometric
reason** why $a_{nt} = 0$ for the disk of the reproduction task, and show that $p_n$ is therefore
independent of $\mu$. For which geometries is $a_{nt} \ne 0$?
*Solution sketch*: (a) is minimising a linear objective over a ball. (c) holds because the disk's
normal Jacobian does not depend on $\theta$ ($J_n = [0,1,0]$) while only the $\theta$ component of
the tangential Jacobian carries $R$ — with a diagonal mass matrix the two blocks do not mix. The
rod has a $\theta$ component in $J_n$ and they do mix.

**P2 (derivation, ★★, R1·R4)** (a) Say how the complementarity of (3) must be modified to include
a restitution coefficient $e \in [0,1]$ (Newton's restitution law), and check whether the
inequality in (6) becomes an **equality** at $e = 1$. (b) Identify which of the three terms in (6)
is the energy loss of a perfectly inelastic collision, and compute its value for a one-DOF ball
striking the floor at speed $v$. (c) Show that $v_n^{+\top}p_n$ is exactly zero when the contact is
already established ($g = 0$), and state the physical meaning of that term being **negative** on a
step where a contact with $g > 0$ becomes active.
*Solution sketch*: (a) change it to $v_n^+ \ge -e\,v_n^-$. (b) is the
$\tfrac12\lVert\Delta v\rVert_M^2$ term, which at one DOF is the whole of $\tfrac12 mv^2$. The
negative value in (c) means "it consumes the gap and stops within the step", and this term is the
channel through which the $g/h$ correction **takes** energy out.

**P3 (proof, ★★★, R2)** (a) Prove in full, from the KKT conditions, the equivalence of a
positive-semidefinite LCP and a convex QP (step 3 of the proof sketch). (b) Prove that when $J_n$
is rank-deficient, $v^+$ is unique but $p_n$ is not, and make it concrete for a quadruped with all
four feet on a plane. (c) Construct a concrete counterexample where the lower-boundedness argument
of step 4 breaks for $g < 0$ (initial penetration).
*Strategy and key inequality*: for (a) write the KKT conditions of
$\min_{p\ge0} \frac12p^\top Ap + c^\top p$ as $Ap + c - s = 0$, $s \ge 0$, $p \ge 0$,
$p^\top s = 0$ and read $s = w$. For (c) it suffices to build $d \ge 0$ with $J_n^\top d = 0$ and
$d^\top g < 0$. The expansion is withheld.

**P4 (proof, ★★★, R3)** (a) Re-derive the substitution $f(\theta) = (t^2+4)/(3t)$ in (5) with no
missing steps and show that $t = 2$ is the **only** critical point. (b) If the **inertia
distribution** rather than the length is changed ($I = \kappa ml^2$ with $\kappa > 0$), find
$\mu_{\mathrm{crit}}$ as a function of $\kappa$ and interpret the limits $\kappa \to 0$ and
$\kappa \to \infty$. (c) Painlevé situations with **multiple** solutions (non-uniqueness) also
exist; say which combination of signs in (4) produces that case.
*Strategy and key inequality*: for (b), substitute $I = \kappa ml^2$ into
$a_{nn} = 1/m + l^2c^2/I$ and $a_{nt} = -l^2sc/I$ to get
$f_\kappa(\theta) = \frac{\kappa + c^2}{\lvert s\rvert c}$ and use the same substitution (minimum
at $t = \sqrt{\kappa+1}$, with $\mu_{\mathrm{crit}}$ of the form $2\sqrt{\kappa+1}$ times a
constant). **Always** check that $\kappa = 1/3$ recovers $4/3$. The expansion is withheld.

**P5 (numerical, ★, R2·R4)** A uniform disk on a plane: $m = 1$, $R = 0.2$,
$I = \tfrac12 mR^2 = 0.02$, $q = (x, y, \theta)$, gap $g = y - R$, $J_n = [0,1,0]$,
$J_t = [1,0,R]$, gravity $g_0 = 9.81$ (entering as the generalised force $-b$ with
$b = (0, mg_0, 0)$). In contact at $q = (0, 0.2, 0)$ with $v^- = (1.5, -0.5, -2.0)$ and
$h = 10^{-3}$, find the mode, $p_n$, $p_t$, $v^+$ and the change in kinetic energy due to the
impulse, for each $\mu \in \{0,\ 0.3,\ 1.0\}$.
*Answer* (tolerance $10^{-9}$). All three cases give $p_n = 0.50981$ (independent of $\mu$, since
$a_{nt} = 0$):

| $\mu$ | Mode | $p_t$ | $v^+$ | $\Delta E_k$ |
|---|---|---|---|---|
| $0$ | slide$+$ | $0$ | $(1.5,\; 0,\; -2)$ | $-0.129953118050$ |
| $0.3$ | slide$+$ | $-0.152943$ | $(1.347057,\; 0,\; -3.52943)$ | $-0.263103076177$ |
| $1.0$ | stick | $-0.366666666667$ | $(1.133333333333,\; 0,\; -5.666666666667)$ | $-0.331619784717$ |

*Checks*: (a) $a_{nn} = 1$, $a_{tt} = 3$, $a_{nt} = 0$; (b) the free velocity
$v_f = (1.5, -0.50981, -2)$ is independent of $\mu$; (c) all three cases have $v_n^+ = 0$
(tolerance $10^{-15}$); (d) at $\mu = 1$, $v_t^+ = 0$ and
$\lvert p_t\rvert = 0.3667 \le \mu p_n = 0.5098$ (inside the cone); (e) at $\mu = 0.3$,
$v_t^+ = 0.641171 > 0$, agreeing with the assumed slip direction; (f) $\Delta E_k$ decreases
monotonically in $\mu$.

**P6 (implementation, ★★, R2·R4·R5)** Write the one-step mode-enumeration solver
`step(q, v, h, mu)` (the core code of the reproduction task below is the skeleton). One planar
contact, zero restitution.
*Rubric*: (a) reproduces the three values of P5 to within $10^{-9}$; (b) there is a test that
**reaches** all three modes (separate, stick, slide); (c) when no mode is consistent it raises an
**exception** rather than quietly returning a wrong answer; (d) it actually checks that the assumed
slip direction agrees with the resulting $\operatorname{sign}(v_t^+)$; (e) it warns, or clips to
$\max(g, 0)$, if $g < 0$ at the start of a step (H3 of the proof sketch); (f) at $\mu = 0$ the
result matches the closed-form solution of the scalar LCP.

**P7 (counterexample, ★★, R3·R5)** (a) Show **numerically** that there is no acceleration-level
solution for the rod at $\theta^{*} = -\arctan 2$ with $\mu = 2$ (it suffices to show that no
$\lambda_n \ge 0$ makes $\ddot g \ge 0$). (b) Show that one velocity-level step at the same state
**is** solvable and say in which mode it is resolved. (c) Check whether the velocity level is still
solvable when $\mu$ is raised to $5$ at the same state, and write a paragraph on how that fact fits
step 6 of C3 in R2.
*Property checklist*: (a) must confirm both signs, $a < 0$ and $\ddot g_{\text{free}} < 0$ (where
$\ddot g_{\text{free}} = -9.81$). The answer to (b) is **stick**, and in (c) the reason the same
sticking solution appears at higher $\mu$ is that the matrix of the sticking mode is a principal
submatrix of $A$ and does not depend on $\mu$ — $\mu$ enters only the cone **check**.

## Paper reading

**Three must-reads** (plus two recommended). 1996, 1997 and 2014 — papers that attack the same
problem from the directions of **the integrator**, **solvability** and **convexity**. Reading all
three and summarising in one paragraph "which assumption of rigid contact each one gave up" is the
reading goal of this lesson (the answer is in (a), (b), (c) of R3 and in R5). Write a one-page note
on each with the ten fixed questions below (`lesson-standard.md` §5). Read in three passes and
concentrate on questions 4, 7 and 8 in the third pass.

1. **Stewart & Trinkle, "An implicit time-stepping scheme for rigid body dynamics with inelastic
   collisions and Coulomb friction" (1996, Int. J. Numer. Methods Eng.)** — role: `seminal`.
   <https://doi.org/10.1002/(SICI)1097-0207(19960815)39:15<2673::AID-NME972>3.0.CO;2-I>
   Which sections and why: the ones that set up the time discretisation and discuss the solvability
   of its LCP. (3) here is its prototype, and the crux is **why it has to be implicit**.
   Extra questions: (a) what exactly do the authors gain by being implicit (stability?
   solvability? both?) (b) in which limit ($h \to 0$) and **to what** is their convergence claim a
   convergence? (c) how does a Painlevé situation appear in this scheme — does it disappear, or
   turn into a different solution?
2. **Anitescu & Potra, "Formulating dynamic multi-rigid-body contact problems with friction as
   solvable linear complementarity problems" (1997, Nonlinear Dynamics)** — role: `standard`.
   <https://doi.org/10.1023/A:1008292328909>
   Which sections and why: this is a paper whose title is its claim — the section that proves
   **solvability**. Step 6 of the proof sketch here is its skeleton, and the focus of the reading
   is **what the authors sacrifice** to buy solvability (cone linearisation, the velocity level).
   Extra questions: (a) list every assumption their solvability theorem requires and compare with
   H1, H2 and H3 here. (b) what becomes physically wrong when the cone is linearised into a
   polyhedron (isotropy? magnitude?) (c) do the authors claim **uniqueness** as well?
3. **Todorov, "Convex and analytically-invertible dynamics with contacts and constraints: theory
   and implementation in MuJoCo" (2014, ICRA)** — role: `standard`.
   <https://doi.org/10.1109/ICRA.2014.6907751>
   Which sections and why: the one that converts complementarity into a strongly convex problem and
   the one that discusses invertibility. R5 is the summary, and the crux is **what is given up to
   buy differentiability and uniqueness**.
   Extra questions: (a) what exactly does the author mean by "analytically invertible", and why is
   it needed in control and estimation? (b) how does the author quantify the model error the
   relaxation creates — is there a bound? (c) how does this relaxation handle a Painlevé situation?

**Two recommended** (not required): **Stewart, "Rigid-Body Dynamics with Friction and Impact"
(2000, SIAM Review)** <https://doi.org/10.1137/S0036144599360110> — the survey of the field, which
shows the mathematical landscape of Painlevé, existence and uniqueness at once; and
**Génot & Brogliato, "New results on Painlevé paradoxes" (1999, Eur. J. Mech. A/Solids)**
<https://doi.org/10.1016/S0997-7538(99)00144-8> — a deeper classification behind R3.

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) independent and dependent variables and baselines — were the baselines tuned fairly?
(6) do the metrics match the claim; are variance and seeds reported? (7) what is missing for
reproduction? (8) if it were wrong, which assumption would you suspect first? (9) compute and
memory complexity, and real-time feasibility. (10) what would you change to go beyond it in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one notebook CPU core, under three minutes, numpy
only. Memory under 200 MB. No simulator is used.

**Core code — the one-step mode-enumeration solver.** Below is the heart of the code every number
in the text came from. With one planar contact the LCP can be solved **exactly**, which is why the
acceptance criteria can be written at machine precision.

```python
G0 = 9.81
M_D, R_D = 1.0, 0.2
I_D = 0.5 * M_D * R_D**2  # uniform disk
MASS = np.diag([M_D, M_D, I_D])
MINV = np.linalg.inv(MASS)
JN = np.array([0.0, 1.0, 0.0])  # d(gap)/dq with gap = y - R
JT = np.array([1.0, 0.0, R_D])  # tangential contact-point velocity: xdot + R thetadot
B = np.array([0.0, M_D * G0, 0.0])  # gravity enters the equation of motion as -B


def step(q, v, h, mu, tau=np.zeros(3)):
    """One velocity-level step, solved exactly by enumerating the three contact modes."""
    g = max(q[1] - R_D, 0.0)  # H3 of the proof sketch: no initial penetration
    vf = v + h * MINV @ (tau - B)  # free velocity
    an, at, ant = JN @ MINV @ JN, JT @ MINV @ JT, JN @ MINV @ JT
    if JN @ vf + g / h >= 0.0:  # mode 1: separating
        return q + h * vf, vf, 0.0, 0.0, "separate", vf
    A = np.array([[an, ant], [ant, at]])  # mode 2: sticking
    pn, pt = np.linalg.solve(A, np.array([-g / h - JN @ vf, -JT @ vf]))
    if pn >= 0.0 and abs(pt) <= mu * pn + 1e-14:
        vp = vf + MINV @ (JN * pn + JT * pt)
        return q + h * vp, vp, pn, pt, "stick", vf
    for s in (+1.0, -1.0):  # mode 3: sliding, pt = -s mu pn
        den = an - s * mu * ant
        if den <= 0.0:
            continue  # the Painleve case: this mode is inconsistent
        pn = (-g / h - JN @ vf) / den
        if pn < 0.0:
            continue
        pt = -s * mu * pn
        vp = vf + MINV @ (JN * pn + JT * pt)
        if abs(JT @ vp) < 1e-12 or np.sign(JT @ vp) == s:
            return q + h * vp, vp, pn, pt, f"slide{int(s):+d}", vf
    raise RuntimeError("no consistent contact mode: the LCP is infeasible")


def painleve_coeff(theta, mu, m=1.0, ell=0.5):
    """Coefficient of lambda_n in the gap acceleration (4), for a rod sliding in +t."""
    inertia = m * (2 * ell) ** 2 / 12
    minv = np.diag([1 / m, 1 / m, 1 / inertia])
    c, s = np.cos(theta), np.sin(theta)
    jn = np.array([0.0, 1.0, -ell * c])  # gap = y - ell sin(theta)
    jt = np.array([1.0, 0.0, ell * s])  # x of the contact point
    return jn @ minv @ jn - mu * (jn @ minv @ jt)
```

`step` returns $(q^{k+1}, v^+, p_n, p_t, \text{mode}, v_f)$. Returning $v_f$ as well is what
condition 2 needs — the baseline for the energy comparison is not $v^-$ but the **free velocity
$v_f$** (otherwise the work done by gravity is mistaken for contact dissipation).

**All four** of the following must hold.

1. **Integration: non-penetration and mode coverage** — drop the disk from $q = (0, 0.5, 0)$ with
   $v = (1.5, 0, -2)$ and integrate for $2$ seconds. For all four combinations of
   $h \in \{10^{-3}, 10^{-4}\}$ and $\mu \in \{0,\ 0.3\}$,
   $$
   \min_k \; g(q^k) \;\ge\; 0 \quad\text{(tolerance } 0\text{: there must be no negative value at all)},
   $$
   and `separate` and `slide+1` must appear for $\mu = 0$, with `stick` as well for $\mu = 0.3$ —
   **all three modes**.
   > Measured: $\min g = 0$ (exactly) for all four combinations. The disk has constant $J_n$, which
   > is why the penetration is zero — condition 4 confirms the reason.
2. **Energy non-increase** — in contact at $q = (0, R, 0)$, draw $5\times10^4$ samples of
   $v^- \sim 2\,\mathcal{N}(0, I_3)$ and $\mu \sim U(0,1)$ and take one step each. On the steps
   where an impulse actually occurs ($p_n > 0$),
   $$
   \max\Big(\tfrac12 v^{+\top}Mv^+ - \tfrac12 v_f^\top Mv_f\Big) \;<\; 0
   $$
   (strictly negative). Separately confirm that on separating steps ($p_n = 0$) the value is
   **exactly zero**.
   > Measured: $25{,}031/50{,}000$ impulse steps, with a maximum of
   > $-3.022041\times10^{-6}$. Fix the seed with `np.random.default_rng(0)`.
3. **The Painlevé threshold, and acceleration level versus velocity level** — (a) minimise
   $f(\theta) = \frac{1+3\cos^2\theta}{3\lvert\sin\theta\rvert\cos\theta}$ over
   $\theta \in (-\pi/2, 0)$ and show
   $$
   \lvert \mu_{\mathrm{crit}} - 4/3\rvert < 10^{-9}, \qquad
   \lvert \theta^{*} + \arctan 2\rvert < 10^{-5}
   $$
   (a grid of $2\times10^6$ points suffices; measured: $1.333333333333$ at
   $-63.434946528^\circ$ versus the closed form $-63.434948823^\circ$).
   (b) Confirm that `painleve_coeff` changes sign at $\mu = 4/3 \mp 10^{-9}$ (measured
   $\pm1.2\times10^{-9}$).
   (c) At $\theta^{*}$ with the contact point slipping at $1\,\mathrm{m/s}$ in $+x$, solve the
   **acceleration level** and show that $\mu = 1$ is feasible with $\lambda_n = +24.525$ while
   $\mu = 2$ is **infeasible** with $\lambda_n = -12.2625 < 0$ (where
   $\ddot g_{\text{free}} = -9.81$).
   (d) At the same state, show that one **velocity-level** step ($h = 10^{-3}$) is solvable for all
   of $\mu \in \{1, 2, 5\}$, and confirm that for $\mu \in \{2, 5\}$ the mode is `stick` with
   $p_n = 0.3083385$ and $p_t = -0.402943$ (**the same values** for both $\mu$ — the sticking mode
   does not depend on $\mu$, which enters only the cone check).
4. **The order of non-penetration** — take **one step only** of the rod at $\theta^{*}$ with
   $\mu = 2$, $g = 0$ and the contact point slipping in $+x$, and sweep
   $h \in \{4, 2, 1, 0.5, 0.25\}\times10^{-3}$; show that the magnitude of the gap after the step
   shrinks by a factor of $3.8$ to $4.2$ each time $h$ is halved (that is, $O(h^2)$).
   > Measured: $-6.1842\times10^{-6}$, $-1.5778\times10^{-6}$, $-3.9846\times10^{-7}$,
   > $-1.0012\times10^{-7}$, $-2.5093\times10^{-8}$ (ratios $3.92,\ 3.96,\ 3.98,\ 3.99$).
   Then show that for the disk (same sweep) the penetration is **exactly zero**, and write one line
   explaining the difference as the configuration dependence of $J_n$.

**Input data**: no external data needed; every model constant is in P5 and in the code above. Fix
the random seed with `np.random.default_rng(0)`.

**Baselines** (at least one):
- First choice: at $\mu = 0$, the **closed-form** solution of the scalar LCP
  ($p_n = \max(0, -(g/h + J_nv_f)/a_{nn})$) must agree with the mode enumeration to within
  $10^{-15}$.
- Second choice: the grid minimisation of condition 3 (a) and the closed form $4/3$ of (b) — two
  mutually independent routes.
- Optional check (not required to pass): implement a general LCP solver (Lemke or projected
  Gauss-Seidel) and check that it gives the same answer as the mode enumeration. With two or more
  contacts enumeration becomes impossible, so this is the serious route.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The penetration shrinks as $O(h)$ | The $g/h$ term of the complementarity was omitted | Print $v_n^+$ on a step where a contact with $g > 0$ becomes active and see whether it is $-g/h$ |
| The energy increases | The baseline was taken as $v^-$ (the work done by gravity got mixed in) | Change the baseline to the free velocity $v_f$ — that is what the left side of (6) is |
| The energy increases (with the right baseline) | In the sliding mode the **sign** of $p_t$ agrees with the slip direction | Assert $v_t^{+}p_t \le 0$ in a unit test |
| The sticking mode leaves the cone | The check $\lvert p_t\rvert \le \mu p_n$ was skipped | Set $\mu$ to zero and confirm the sticking mode is never chosen |
| The sliding mode oscillates ($s$ flips every step) | The agreement between the resulting $\operatorname{sign}(v_t^+)$ and the assumption was not checked | Try both signs and accept only the consistent one |
| `nan` or an enormous $p_n$ | The sliding denominator $a_{nn} - s\mu a_{nt}$ is near zero (close to Painlevé) | Print the denominator and **skip** that mode when it is $\le 0$ (the `continue` in the code) |
| $\lambda_n$ comes out positive in condition 3 (c) | The sign in (4) — if the slip is $+t$ then $\lambda_t = -\mu\lambda_n$ | Check that $\lambda_n = 9.81/a_{nn}$ at $\mu = 0$ to fix the sign |
| The LCP does not solve from a penetrating state | H3 of the proof sketch is violated | Clip $g$ to $\max(g, 0)$ or project before the step |

## Open problems

- **(open problem) Differentiability of contact dynamics and the validity of the gradients used in
  learning** — a complementarity solution is **non-smooth** where the contact mode changes, and
  what automatic differentiation returns there is either a one-sided derivative or meaningless. A
  convex relaxation (R5) buys smoothness, but its gradient is the gradient of the **relaxed model**
  and there is no bound on how far it is from the gradient of the original problem. Since policy
  learning and trajectory optimisation depend entirely on these gradients, this is a practical
  problem. Current approaches: convex relaxation with analytical derivatives
  ([Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751)) and randomized smoothing. What is
  missing: an error bound between the relaxed gradient and the true one.
- **(open problem) Bounds on the model error of real friction and deformation** — the Coulomb cone
  assumes isotropy, velocity independence and area independence, and real friction is none of the
  three (Stribeck, contact-area dependence, preload history). As Painlevé shows, modelling
  assumptions can even create contradictions, yet there is no guarantee of **how wrong** a given
  contact model can be relative to given experimental data. Almost all of the sim-to-real gap in
  manipulation comes from here. Current approaches: identifying contact parameters from data,
  residual learning, and distributionally robust control. What is missing: worst-case error bounds
  over a model class. The mathematical landscape of Painlevé is organised by
  [Stewart 2000](https://doi.org/10.1137/S0036144599360110) and
  [Génot & Brogliato 1999](https://doi.org/10.1016/S0997-7538(99)00144-8).
- **(open problem) Cost lower bounds in the number of contacts** — the same wall as the open
  problem of the previous lesson. With $n_c$ contacts the LCP has size $O(n_c)$, forming the
  Delassus operator costs $O(n\,n_c + n_c^2)$, and solving it is exponential in the worst case
  (pivoting algorithms). Whether a solver that is both polynomial in the number of contacts and
  exact exists is open, and practice **gives up exactness** by using iterative solvers. Current
  approaches: first-order solvers of the projected Gauss-Seidel and ADMM families, and convex
  relaxation. What is missing: a lower bound in $n_c$, and an analysis of how the error of an
  iterative solver accumulates at the level of a trajectory.

## Concept check

Run `rc quiz c2-contact-dynamics`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: which physical conditions normal complementarity bundles; the grounds on
which the frictionless velocity-level discretisation always has a solution; the critical friction
coefficient of the Painlevé paradox for a uniform rod; whether the Painlevé paradox means the
physics is contradictory; and what changes if the $g/h$ term is dropped.

## How to study this stage

1. **Write down first what one inequality changes (20 min)** — put the previous lesson's
   $\phi = 0$ beside this lesson's $g \ge 0$ and write a paragraph on the path by which that
   difference turns a linear system into a complementarity problem. Every difficulty in this
   lesson comes from that one line.
2. **Classify the three modes by hand (40 min)** — write (7) down and tabulate, for each of
   separate, stick and slide, which unknown is zero and which equation is active. Confirming by
   hand that **enumeration is solving the LCP** lets you finish this lesson without knowing Lemke.
3. **Carry Painlevé through to closed form (60 min)** — compute the two Delassus entries of R3
   yourself and go all the way to $4/3$ with the substitution $t = \tan\lvert\theta\rvert$. Then
   **cross-check by grid minimisation** (condition 3 (a) of the reproduction task). The experience
   of closed form and numerics meeting at $10^{-9}$ is the centre of this lesson.
4. **See by hand why the energy baseline is $v_f$ (30 min)** — confirm in the derivation that the
   left side of (6) is the difference from $v_f$ rather than from $v^-$, and construct numerically
   the wrong conclusion ("the energy increases") that taking $v^-$ produces. That is the second row
   of the diagnosis table.
5. **Implement it wrongly first (60 min)** — when writing P6, make three variants: (a) the $g/h$
   term omitted, (b) the cone check omitted, (c) the slip-direction consistency check omitted, and
   note which condition of the reproduction task breaks. (c) in particular shows up as
   **oscillation with the sign flipping every step**, and seeing that symptom once teaches in the
   body why an LCP solver is "a problem of choosing a combination".
6. **Finish the reproduction task (150 min)** — condition 3 is the heart of this lesson. Put (c)
   and (d) side by side and confirm with your own numbers that "same state, same $\mu$, the
   acceleration level is infeasible but the velocity level solves". That single experiment explains
   the whole title of Anitescu-Potra.
7. **Read the three papers for "what did they give up" (150 min)** — Stewart-Trinkle (implicitness),
   Anitescu-Potra (cone linearisation plus the velocity level), Todorov (convex relaxation) is a
   good order. For each, write one line on "which assumption of rigid contact this author gave up,
   and what they got for it", then merge the three lines into one paragraph. That paragraph becomes
   the introduction to the next lesson (derivatives and identification).
8. **End with what cannot be done (25 min)** — pick the differentiability open problem and write a
   paragraph on why using the gradient of a relaxed model as the true gradient is not justified.
   The question returns in `c2-dynamics-derivatives-sysid` and in the manipulation and contact
   specialisation.

**Passing bar**: you can write (1), (2), (3), (4) and (6) from a blank page; you can state the four
steps of the solvability proof of R2 and the derivation of $4/3$ in R3; you have a
mode-enumeration solver that passes all four conditions of the reproduction task; and you have
one-page notes on all three must-read papers.
