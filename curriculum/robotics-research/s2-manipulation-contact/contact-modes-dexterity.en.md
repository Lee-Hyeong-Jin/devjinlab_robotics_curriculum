---
id: s2-contact-modes-dexterity
lang: en
title: Contact modes and extrinsic dexterity
summary: >-
  Moving an object without grasping it. First derive that the constraint a single contact places on
  the object's twist space is a polyhedral cone, and put mode enumeration on top of it. Then derive
  the central object of quasi-static pushing, the limit surface — obtained by integrating friction
  over the support patch, it is convex, and the object's twist is **normal** to it (the maximum-work
  inequality). For a uniform circular patch, $f_{\max}$ and $\tau_{\max} = \tfrac23\mu N R$ come out
  in closed form and the error of the ellipsoidal approximation is measured. Finally, read extrinsic
  dexterity — using gravity, inertia and environmental contact in place of fingers — in the language
  of mode sequences.
objectives:
  - Write the constraint a contact places on the object twist as a polyhedral cone and split it by mode.
  - Define the limit surface of quasi-static pushing as an integral of friction and argue that it is convex.
  - Derive the normality rule from the maximum-work inequality and verify it numerically.
  - Compute $f_{\max}$ and $\tau_{\max}$ for a uniform circular patch in closed form and assess the ellipsoidal approximation.
  - Describe extrinsic dexterity as a mode sequence and explain why it reduces the finger degrees of freedom needed.
tags: [manipulation, pushing, limit-surface, contact-modes, extrinsic-dexterity, research]
---

# Contact modes and extrinsic dexterity

## Setup and notation

`s2-grasp-mechanics` is assumed; in particular friction cones, wrench space and generator
discretization are used unchanged. Also assumed:

- `c2-contact-dynamics` — the complementarity conditions and the definition of the modes
  (separated, sticking, sliding).
- `c6-tamp` R3 — that there are $3^{n_c}$ modes. This lesson views that enumeration from the
  **motion** side.
- Convex analysis: polyhedral cones, dual cones, support functions, and the normal cone at the
  boundary of a convex set (recommended prerequisite `r0-convex-optimization`).

Notation (in addition to module S2's):

| Symbol | Meaning |
|---|---|
| $\xi = (v, \omega)$ | the object's planar twist, $v \in \mathbb{R}^2$, $\omega \in \mathbb{R}$ |
| $r_c$ | centre of rotation (COR); $\xi = \omega\,(r_{c,y},\ -r_{c,x},\ 1)$ |
| $\phi_i(\xi)$ | separation speed along the normal at contact $i$ |
| $N$ | total normal load on the support patch |
| $\mu$ | object–support friction coefficient (distinct from the finger–object one) |
| $p(x)$ | pressure distribution on the patch, with $\int p\,dA = N$ |
| $\mathcal{L}$ | the **limit surface** — the boundary of the wrenches the patch can exert while sliding |
| $f_{\max}, \tau_{\max}$ | friction force and moment for pure translation and pure rotation |
| $c$ | characteristic length $\tau_{\max}/f_{\max}$ |

**The problem.** Move an object with fingers that do **not** enclose it (non-prehensile). Grasping
only required force equilibrium (equation (1) of the previous lesson), but in pushing the object
**moves**, so motion and force must be solved together. Under the quasi-static assumption, that
coupling is the pair

$$
\underbrace{w_{push} + w_{support}(\xi) = 0}_{\text{force equilibrium}},
\qquad
\underbrace{w_{support}(\xi) \in \partial\mathcal{L},\ \ \xi \perp \mathcal{L}}_{\text{friction law}}
  \tag{1}
$$

The second line is the heart of this lesson, and **why it is "normal"** is R2.

Three assumptions, stated explicitly.

- **(A1) quasi-static** — inertia is neglected ($m\dot v \approx 0$). Valid when pushing is slow and
  friction dominates; where it breaks is in the failure modes of §R2.
- **(A2) the pressure distribution is known** — $p(x)$ is given. In practice it is **not**, and this
  is the single largest source of error in pushing models (§Open problems).
- **(A3) Coulomb friction, isotropic and velocity-independent** — the friction force density is
  $-\mu p(x)\hat u(x)$ with $\hat u$ the unit vector of the local sliding direction.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof).

- **R1 (polyhedral cone of contact constraints and mode enumeration) [D2]** — at contact $i$ the
  non-penetration condition places a **linear** inequality $\phi_i(\xi) = a_i^\top \xi \ge 0$ on the
  object twist, and sticking versus sliding places further linear conditions on the tangential
  component on that equality face. So fixing one mode makes the set of admissible twists a
  **polyhedral cone**, and changing the mode changes which faces that cone has. That there are
  $3^{n_c}$ modes is the same as `c6-tamp` R3; what is new here is that **each mode gives one linear
  program**.
- **R2 (the limit surface and the normality rule) [D3]** — the set of wrenches the patch can exert
  while sliding is **convex**, and the object twist $\xi$ corresponding to a point $w$ on its
  boundary $\mathcal{L}$ is **normal** to $\mathcal{L}$:
  $$\xi \in N_{\mathcal{L}}(w) \quad\text{(the normal cone)}.
    \tag{2}$$
  The basis is the **maximum work dissipation** inequality of Coulomb friction,
  $(w - w')^\top \xi \ge 0$ for all $w' \in \mathcal{L}$. For a uniform circular patch (radius $R$,
  uniform pressure),
  $$f_{\max} = \mu N, \qquad \tau_{\max} = \tfrac{2}{3}\,\mu N R,
    \qquad c = \tau_{\max}/f_{\max} = \tfrac23 R
    \tag{3}$$
  come out in closed form.
- **R3 (the ellipsoidal approximation and its error) [D2]** — practice approximates $\mathcal{L}$ by
  the ellipsoid $(\lVert f\rVert/f_{\max})^2 + (\tau/\tau_{\max})^2 = 1$. The approximation always
  lies **outside** ($g \le 1$), its maximum error on a uniform disc is $12.2\%$, and that maximum
  occurs **at $|r_c| = c = 2R/3$**. Using the ellipsoid makes the normality rule (2) give a
  closed-form expression for the twist, so obtaining the velocity costs an algebraic computation
  instead of an integral — that trade is the reason the approximation exists.
- **R4 (extrinsic dexterity) [D2]** — even with too few finger degrees of freedom, using
  **gravity, inertia and environmental contact** as extra "fingers" can change the object's pose. In
  the language of mode sequences: a mode transition the hand cannot produce is **produced by the
  environment**. This has the same structure as the skeleton search of `c6-tamp`, the difference
  being that **physics supplies part of the skeleton for free**
  ([Chavan-Dafle et al. 2014](https://doi.org/10.1109/ICRA.2014.6907062)).

## Derivation

### R1 — why contact constraints are linear

At the contact point $x_i$, let $\hat n_i$ be the inward normal of the object surface and
$\hat t_i$ the tangent. If the object moves with twist $\xi = (v, \omega)$, the velocity of that
point is

$$
\dot x_i = v + \omega\, \hat z \times x_i,
  \tag{4}
$$

which is **linear** in $\xi$. Non-penetration (the finger does not sink into the object) is a
condition on the normal component,

$$
\phi_i(\xi) = \hat n_i^\top \dot x_i = \underbrace{\big[\hat n_i^\top,\ (\hat z\times x_i)^\top \hat n_i\big]}_{=: a_i^\top}\,\xi \;\ge\; 0,
  \tag{5}
$$

and $a_i$ is **the same vector** as the wrench of equation (5) of `s2-grasp-mechanics` (the duality
between contact wrenches and motion constraints). The three modes are distinguished on the boundary
of (5):

| Mode | Condition on the twist |
|---|---|
| separated | $a_i^\top\xi > 0$ (contact is lost) |
| sticking | $a_i^\top\xi = 0$ **and** zero tangential relative velocity — two equalities |
| sliding | $a_i^\top\xi = 0$ **and** non-zero tangential relative velocity — one equality plus a sign |

**Conclusion**: fixing a single mode makes the set of admissible twists a **polyhedral cone**
defined by finitely many linear equalities and inequalities. Fixing a mode sequence makes each
interval an LP (or an LCP), so planning contact manipulation has **the same structure** as "fix the
skeleton and a continuous problem remains" in `c6-tamp`.

**Where the assumption breaks**: the linearity of (4) depends on the contact point $x_i$ being
**fixed**. Under rolling, or when the contact point travels along the surface, $x_i$ depends on the
integral of $\xi$ and the constraint becomes non-linear. That is why the literature on rolling puts
the contact coordinates into the state and writes a differential equation.

### R2 — the limit surface: from the integral to normality

**Definition.** When the object slides with twist $\xi$, the sliding velocity of each patch point
$x$ is (4), and Coulomb friction acts **opposite** to it with magnitude $\mu p(x)$. The total
wrench is

$$
w_{support}(\xi) = -\mu \int_A p(x)\,
  \begin{bmatrix} \hat u(x) \\ x \times \hat u(x) \end{bmatrix} dA,
  \qquad \hat u(x) = \frac{v + \omega \hat z \times x}{\lVert v + \omega\hat z \times x\rVert}.
  \tag{6}
$$

Since $\hat u$ is a **unit** vector, it does not depend on the magnitude of $\xi$ — doubling the
speed leaves the friction wrench unchanged. So $w_{support}$ is a function of the **direction** of
$\xi$ only, and its image is a two-dimensional surface
$\mathcal{L} \subset \mathbb{R}^3$. That is the **limit surface**.

**Two pure motions (closed form).** For a uniform disc (radius $R$, uniform pressure
$p = N/\pi R^2$):

- **Pure translation** ($\omega = 0$): every point has the same $\hat u$, so
  $\lVert f\rVert = \mu\int p\,dA = \mu N$ and $\tau = 0$. Hence $f_{\max} = \mu N$.
- **Pure rotation** ($v = 0$, COR at the centre): $\hat u$ is tangential and
  $x \times \hat u = \lVert x\rVert$, so
  $$\tau_{\max} = \mu\int_A p(x)\lVert x\rVert\,dA
    = \mu\frac{N}{\pi R^2}\int_0^R r\,(2\pi r)\,dr
    = \mu\frac{N}{\pi R^2}\cdot\frac{2\pi R^3}{3} = \frac{2}{3}\mu N R,$$
  with $f = 0$ by symmetry. That is (3). The characteristic length
  $c = \tau_{\max}/f_{\max} = 2R/3$ is the length that puts force and torque on the same scale, and
  it plays **the same role** as the length that caused trouble in the failure mode of
  `s2-grasp-mechanics` R2.

**The normality rule.** The basic property of Coulomb friction is **maximum work dissipation**: the
actual friction wrench $w$ **maximizes** the dissipation $-w'^\top\xi$ over all admissible
$w' \in \mathcal{L}$. Pointwise this is obvious — since $\hat u$ is the sliding direction,
$-\mu p\,\hat u$ maximizes that point's dissipation — and the integral is linear, so the total does
too. Hence for every $w' \in \mathcal{L}$

$$
(-w)^\top \xi \;\ge\; (-w')^\top\xi
  \quad\Longleftrightarrow\quad
  (w - w')^\top \xi \;\le\; 0 .
  \tag{7}
$$

Equation (7) says that **$\xi$ is an inward normal of $\mathcal{L}$ at $w$**, and flipping the sign
to $-w$ gives exactly the normal-cone condition (2). **So normality is not an extra assumption; it
follows from Coulomb friction.** And (7) implies $\mathcal{L}$ is **convex**: the support function
$h(\xi) = \max_{w\in\mathcal{L}}(-w^\top\xi)$ is well defined and the set is the boundary of the
convex set it represents.

**What this means in practice.** Combining the second line of (1) with (2) gives **a formula for the
pushing velocity**: given the pushing wrench $w_{push}$, find $w_{support} = -w_{push}$ on
$\mathcal{L}$ and the normal at that point gives the object twist. Instead of inverting the integral
(6), one just **reads off a normal**.

**Three places the assumptions break.**

1. **(A1) quasi-static fails.** In fast pushing, inertia enters and the force equilibrium of (1)
   becomes $m\dot v = \sum w$, so there is no guarantee the twist is normal to the limit surface. The
   criterion is the dimensionless ratio $\mu g / a$ (frictional deceleration versus acceleration),
   and for $a \gtrsim \mu g$ the quasi-static assumption must be dropped.
2. **(A2) the pressure distribution is unknown.** Equation (6) is linear in $p(x)$, but **the shape
   of $\mathcal{L}$ is sensitive to $p$**. Supporting the same object on three points rather than a
   face changes $\tau_{\max}$ by tens of percent, and $p$ is hard to measure. This is the dominant
   source of pushing-model error and the reason data-driven identification is needed
   ([Zhou et al. 2016](https://arxiv.org/abs/1602.06056)).
3. **(A3) isotropic Coulomb fails.** With anisotropic friction (a grained surface) or
   velocity-dependent friction, $\hat u$ is no longer the unit vector of the sliding direction and
   the pointwise maximization of (7) breaks. Then normality fails and the very notion of a limit
   surface must be redefined.

### R3 — the ellipsoidal approximation and its error

The integral (6) is too expensive to solve at every time step. The standard workaround is to
approximate $\mathcal{L}$ by the ellipsoid

$$
g(w) \;=\; \left(\frac{\lVert f\rVert}{f_{\max}}\right)^2 + \left(\frac{\tau}{\tau_{\max}}\right)^2 \;=\; 1 .
  \tag{8}
$$

At the two poles (pure translation and pure rotation) it is **exact**, because (3) was used to fit
those two points. The question is how wrong it is in between.

**The structure of the error.** Putting the COR at $r_c = (0, d)$ and sweeping $d$ from 0 to
$\infty$ traces a meridian of $\mathcal{L}$ through (6). Since $d = 0$ is pure rotation and
$d \to \infty$ pure translation, $g = 1$ at both ends and $g < 1$ in between — **the true surface
lies inside the ellipsoid**. Numerical integration on a uniform disc gives

| $d$ | 0 | 0.25 | 0.5 | $2/3$ | 1.0 | 1.5 | 2.0 | 4.0 | 10 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|
| $\lVert f\rVert$ | 0 | 0.2480 | 0.4838 | 0.6272 | 0.8488 | 0.9408 | 0.9677 | 0.9921 | 0.9987 | 1.0000 |
| $-\tau$ | 0.6667 | 0.6358 | 0.5477 | 0.4643 | 0.2829 | 0.1738 | 0.1278 | 0.0628 | 0.0250 | 0.0025 |
| $g$ | 1.0000 | 0.9710 | 0.9092 | 0.8785 | 0.9006 | 0.9531 | 0.9732 | 0.9932 | 0.9989 | 1.0000 |

(normalized to $\mu N = 1$, $R = 1$). **The maximum error is $12.2\%$ and it occurs at
$d = 2/3 = c$** — the point where force and torque mix "equally" is the worst, which is
geometrically natural.

**Why it is used anyway.** Substituting (8) into (2) gives the normal analytically:
$\nabla g \propto (f_x/f_{\max}^2,\ f_y/f_{\max}^2,\ \tau/\tau_{\max}^2)$, so

$$
v \;\propto\; \frac{f}{f_{\max}^2}, \qquad \omega \;\propto\; \frac{\tau}{\tau_{\max}^2}
  \;\Longrightarrow\;
  \frac{\omega}{\lVert v\rVert} = \frac{\tau}{\lVert f\rVert}\cdot\frac{f_{\max}^2}{\tau_{\max}^2}
    = \frac{\tau}{\lVert f \rVert\, c^2}.
  \tag{9}
$$

That is **a closed-form map from pushing wrench to object twist**. One integral becomes one
division, so it can be used inside an MPC, at the price of $12\%$ model error. The pressure-
distribution uncertainty of (A2) is usually larger than that, so **in practice this approximation is
not the dominant error** — which is the real reason it is ubiquitous.

## Proof sketch

### R2 — the normality rule and the convexity of $\mathcal{L}$

**Hypotheses** H1: (A1) and (A3) — quasi-static with isotropic Coulomb friction. H2: the pressure
distribution $p \ge 0$ is fixed with $\int_A p\,dA = N$. H3: sliding is **global** (every patch point
slides; there is no sticking region).
**Conclusion** C: $\mathcal{L}$ is convex, and the twist $\xi$ corresponding to $w$ on
$\mathcal{L}$ lies in the normal cone at $-w$ (equation (2)).

**Strategy**: **pointwise maximization → integration → support function.** That the integral
preserves the pointwise property of Coulomb friction is the whole argument, and convexity follows
automatically from the support-function representation.

1. **Pointwise maximum dissipation.** Let $s(x) = v + \omega\hat z\times x$ be the sliding velocity
   at $x$. The friction force available there is the disc $\{f : \lVert f\rVert \le \mu p(x)\}$, and
   the $f$ maximizing the dissipation $-f^\top s(x)$ is **unique**,
   $f^\ast = -\mu p(x)\,s(x)/\lVert s(x)\rVert$ (when $s(x) \ne 0$). That is the integrand of (6).
2. **Integration preserves maximality.** The total dissipation is $-\int f(x)^\top s(x)\,dA$ and is
   separable pointwise, so maximizing at each point maximizes the total. Hence (7) holds for any
   admissible friction wrench $w' = \int [f'; x\times f']dA$.
3. **Support function and convexity.** Writing (7) as
   $h(\xi) := \max_{w'}(-w'^\top\xi) = -w(\xi)^\top\xi$, $h$ is a function of a maximum and hence
   convex and positively homogeneous in $\xi$. The set whose support function is such an $h$,
   $\{w : -w^\top \xi \le h(\xi)\ \forall\xi\}$, is closed and convex, and its boundary is
   $\mathcal{L}$. (Omitted: checking that $h$ is finite in every direction and that $0$ is interior
   — both follow from $p \ge 0$ and $\int p = N > 0$.)
4. **The normal cone.** For a convex set $K$ and a boundary point $w$, the set of $\xi$ for which (7)
   holds for all $w' \in K$ is exactly the normal cone of $K$ at $w$. At a differentiable point the
   cone collapses to one direction, giving **$\xi \parallel \nabla$**, which is the basis of (9).
5. **What an edge means.** If $\mathcal{L}$ has a non-differentiable point (an edge), the normal cone
   is two-dimensional and **several twists correspond to the same pushing wrench** — physically, "the
   pushing direction is on the boundary, so whether the object turns or just slides is undetermined",
   which appears in pushing control as **mode ambiguity** (and returns as the problem of resolving it
   by observation in `s2-tactile-contact-estimation`).

**Removing a hypothesis**: dropping H3 (part of the patch sticks) breaks the assumption
"$s(x) \ne 0$" of step 1, so the friction force there may be any value **inside** the disc. Then $w$
lies in the **interior** of $\mathcal{L}$ and (2) survives only as an inclusion — which is exactly
the case when the object does not move. Dropping the quasi-static H1 breaks the equilibrium of (1),
so $\mathcal{L}$ is still defined but no longer determines the twist. Dropping H2 (pressure varying
with motion — a tilting object) makes $\mathcal{L}$ itself move in time.

## Problem set

Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Show that the $a_i$ of (5) is the same vector as the contact wrench of
equation (5) of `s2-grasp-mechanics`, and explain how that fact is the same statement as "the motion
directions a contact blocks and the force directions it can exert are dual". Also say why the
sticking mode gives **two** equalities.
*Solution sketch*: expand $\hat n^\top(v + \omega\hat z\times x) = [\hat n; x\times\hat n]^\top\xi$.
Sticking sets **both** the normal and the tangential relative velocity to zero, which is two
equalities in the plane.

**P2 (derivation, ★★, R2)** Derive $\tau_{\max}$ for the uniform disc as an integral as in (3), then
compute $\tau_{\max}$ for a pressure concentrated at the centre (close to $p \propto \delta$) and for
one concentrated at the rim ($p \propto \delta(r - R)$), and state the range of the characteristic
length $c$.
*Solution sketch*: $\tau_{\max} = \mu\int p\,r\,dA$ is the **first moment** of $p$. Centre
concentration gives $c \to 0$, rim concentration $c \to R$, and uniform $c = 2R/3$. **So $c$ can be
anywhere in $[0, R]$ and is fixed by the pressure distribution alone** — which is where the severity
of (A2) becomes visible.

**P3 (numerical, ★, R2·R3)** For a uniform disc with $\mu N = 1$ and $R = 1$, find $f_{\max}$,
$\tau_{\max}$ and $c$; then, for a COR at $r_c = (0, 1)$, read $g$ from the table of the reproduction
task and express the approximation error as a percentage. Also answer at which $d$ the error is
largest.
*Answer*: $f_{\max} = 1$, $\tau_{\max} = 2/3 = 0.666666667$, $c = 2/3$. At $d = 1$,
$g = 0.90063262$, so the ellipsoid is $1/\sqrt{g} - 1 = 5.37\%$ larger than the true surface. The
maximum error is at $d = c = 2/3$, where $g = 0.87847392$, i.e. $12.15\%$ measured as $1 - g$ or
$\sqrt{1/g} - 1 = 6.70\%$ measured as a radius. Tolerance $10^{-6}$.
**Distinguishing the two kinds of "percentage" is the point of this item.**

**P4 (numerical, ★★, R3)** Derive (9), and for a disc with $\mu N = 1$ and $R = 1$ pushed at its
centre of mass by a wrench with $\lVert f\rVert = 0.5$ and $\tau = 0.2$, find
$\omega/\lVert v\rVert$. What else is needed to compare that value against one computed from the
normal of the true limit surface?
*Answer*: from (9), $\omega/\lVert v\rVert = \tau/(\lVert f\rVert c^2) = 0.2/(0.5\cdot(2/3)^2) =
0.2/0.2222222 = 0.9$. To compare with the truth, $w = (f, \tau)$ must lie **on** $\mathcal{L}$, so it
must first be projected onto the surface (the given $w$ has $g = 0.25 + 0.09 = 0.34 < 1$, i.e. it is
interior, so the object does not move). Tolerance $10^{-9}$.

**P5 (proof, ★★, R2)** Fill in step 3 of the proof sketch: show that
$h(\xi) = \max_{w'\in\mathcal{L}}(-w'^\top\xi)$ is convex and positively homogeneous, and that the
set whose support function is such an $h$ is closed and convex.
*Strategy*: a function of a maximum is convex (a supremum of affine functions); positive homogeneity
comes from $\hat u$ being independent of the magnitude of $\xi$. The second claim is the one-to-one
correspondence between support functions and convex sets (Fenchel).

**P6 (proof, ★★★, R2)** Handle the case where H3 (global sliding) is dropped: show that with a
sticking region on the patch, $w$ lies in the interior of $\mathcal{L}$, and write the condition for
the object to stay at rest in terms of $w_{push}$. Say how that condition resembles and how it differs
from the force-closure test of `s2-grasp-mechanics`.
*Strategy*: at a sticking point the friction force is any value inside the disc, so the set of
achievable wrenches is the **whole convex body** bounded by $\mathcal{L}$. The rest condition is that
$-w_{push}$ belongs to that body — symmetric to force closure's "the origin is interior", except that
here one asks about the membership of **a particular wrench**.

**P7 (implementation, ★★, R2·R3)** Write the limit-surface integrator and checker of the
reproduction task. Requirements: grid quadrature for (6), finite-difference estimation of the surface
normal, and `ConvexHull` to confirm convexity.
*Rubric*: (a) the numbers of criteria 1–4 agree within tolerance; (b) refining the quadrature from
$450\times900$ to $900\times1800$ reduces the $\tau_{\max}$ error about fourfold (second-order
convergence); (c) changing the pressure to rim concentration drives $c \to R$ numerically (P2);
(d) you report the maximum of $|\sin\angle(\xi, n)|$ in the normality check.

**P8 (counterexample, ★★, R2·R4)** Construct a counterexample to the common misconception that "in
quasi-static pushing the object moves in the pushing direction": using (9), give a case where pushing
a uniform disc off-centre makes it **rotate** and move along a direction different from the pushing
direction. Then write one paragraph on how extrinsic dexterity (R4) **exploits** this phenomenon.
*Property checklist*: off-centre pushing gives $\tau \ne 0$ and (9) gives $\omega \ne 0$. The
direction of $v$ matches $f$, but **points** on the object move with $v + \omega\hat z\times x$, so
the trajectory of the contact point differs from the pushing direction. Extrinsic dexterity uses that
rotation as **the desired pose change**, so the environment produces mode transitions the fingers
cannot.

## Paper reading

**Two must-reads.** Write a one-page note on each using the ten fixed questions.

1. **Lynch & Mason, "Stable pushing: mechanics, controllability, and planning" (1996, IJRR)** —
   role: `seminal`. <https://doi.org/10.1177/027836499601500602> (§2–4)
   *Why read it*: R1 and R2 are combined here. In particular, see how **stable pushing** — the set of
   pushing directions for which the contact keeps sticking — is described exactly by the polyhedral
   cone of R1. When that set is non-empty, pushing becomes **controllable**.
   Extra questions: (a) the authors' controllability claim is the condition that which set is
   non-empty? (b) how is the limit surface approximated, and how does that choice affect planning?
   (c) how is pressure-distribution uncertainty handled (or not)?
2. **Chavan-Dafle et al., "Extrinsic dexterity: in-hand manipulation with external forces"
   (2014, ICRA)** — role: `seminal`. <https://doi.org/10.1109/ICRA.2014.6907062>
   *Why read it*: the source of R4, and an exercise in reading "too few finger degrees of freedom can
   be made up for by the environment" as a **mode sequence**. Contrast it with the skeleton search of
   `c6-tamp`.
   Extra questions: (a) enumerate the kinds of "external force" the authors use and say what role each
   plays in a mode transition. (b) on which model assumptions does each strategy's success depend?
   (c) writing this approach's planning problem in the form of (1) of `c6-tamp`, what is the skeleton
   and what are the parameters?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation or one figure. (4) what is guaranteed theoretically,
and **what is not**? (5) the independent and dependent variables and the baselines, and were the
baselines tuned fairly? (6) does the metric match the claim, and are variance and seeds reported?
(7) what is missing for reproduction? (8) if the result were wrong, which assumption would you doubt
first? (9) computational and memory complexity, and real-time feasibility. (10) what would you change
to go beyond this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 10 minutes in total, under 1 GB
of memory. numpy plus scipy (`spatial.ConvexHull`) only. No external data.

**Input data (given by the lesson).** The support patch is a **uniform-pressure disc of radius
$R = 1$** with total load $N = 1$ and friction coefficient $\mu = 1$ (so $f_{\max} = 1$ and
$\tau_{\max} = 2/3$). Quadrature uses a polar grid of $N_r \times N_\theta = 900 \times 1800$ with
cell-centre samples and weights $dA = r\,dr\,d\theta$ normalized so that they sum to $N$. Twists are
parameterized by the COR $r_c$, using
$\hat u(x) = \hat z\times(x - r_c)/\lVert x - r_c\rVert$.

**Acceptance criteria — all four must hold.**

1. **Against the closed form (checking R2)** — for pure rotation ($r_c = 0$) you obtain
   $|\tau| = 2/3$ to an absolute error of $10^{-6}$ with $\lVert f\rVert < 10^{-15}$. For pure
   translation ($|r_c| = 10^7$) you obtain $\lVert f\rVert = 1$ to an absolute error of $10^{-8}$
   with $|\tau| < 10^{-7}$. (Measured: $\tau = -0.666666461$, error $2.1\times10^{-7}$;
   $\lVert f\rVert = 1.000000000$; $\tau = -2.5\times10^{-8}$.)
2. **The normality rule (checking the [D3] of R2)** — for
   $r_c \in \{(0.3,0), (0,0.5), (0.4,0.4), (1,0), (0,2), (1.5,-0.7), (3,1)\}$, the quantity
   $|\sin\angle(\xi, n)|$ between the finite-difference surface normal $n$ (step $10^{-3}$) and the
   twist $\xi = (r_{c,y}, -r_{c,x}, 1)$ is **below $10^{-5}$ in every case** (measured maximum
   $1.81\times10^{-6}$). That is, **the twist is exactly normal to the limit surface**.
3. **Convexity** — drawing 400 CORs with $|r_c| = 10^{u}$, $u \sim U(-1.3, 1.2)$ and uniform
   direction, and combining both senses of rotation for 800 samples, **all 800** are vertices of the
   `ConvexHull` (every sample lies on the hull). The distance from the origin to the nearest facet is
   within $\pm 0.01$ of $\tau_{\max} = 2/3$ (measured $0.665308$).
4. **Error of the ellipsoidal approximation (checking R3)** — putting the COR at $r_c = (0, d)$ for
   $d \in \{0, 0.25, 0.5, 2/3, 1, 1.5, 2, 4, 10, 100\}$ and computing $g$ reproduces the table in the
   text to an absolute error of $10^{-5}$, with **$g \le 1$ for every $d$** and the **maximum error
   $1 - g = 0.121526$ occurring at $d = 2/3 = c$**. Write one paragraph in the report on "the true
   surface lies **inside** the ellipsoid, and the worst case is at the characteristic length".

**Baselines.** (a) The closed form (3) — criterion 1. (b) Two independent computations: compute the
normality once from the finite-difference normal and once from the derivative of the support function
$h(\xi)$, and check they give the same twist. (c) Quadrature convergence: refining
$450\times900 \to 900\times1800$ should reduce the $\tau_{\max}$ error about fourfold (second order).

**Failure table**

| Symptom | Cause | How to check |
|---|---|---|
| $\tau_{\max}$ comes out $1/2$ | the pressure was spread uniformly in radius rather than in area ($p \propto 1/r$) | check that the weights sum to $N$ and that the $r$ of $dA = r\,dr\,d\theta$ is present |
| $\tau \ne 0$ for pure translation | the COR was not placed far enough away ($|r_c|$ comparable to $R$) | increase $|r_c|$ through $10^3, 10^5, 10^7$ and watch $\tau \to 0$ |
| the normality error is of order $10^{-2}$ | the finite-difference step is too large or too small (quadrature noise) | try steps $10^{-2}, 10^{-3}, 10^{-4}$ and find the best |
| some points give $g > 1$ | $f_{\max}$ or $\tau_{\max}$ was mixed between the analytic and the numerical value | normalize by the numerical values at the two poles and recompute |
| interior points appear in the convex hull | only one sense of rotation was sampled (half the surface) | check that the samples' $\tau$ takes both signs |
| the integration exceeds 10 minutes | the grid was rebuilt for every COR | build the grid and weights once and reuse them |

## Open problems

- **(open problem) Identifying the pressure distribution** — (A2) is **almost always false** in
  practice, and since $c$ can be anywhere in $[0, R]$ (P2) the shape of the limit surface is
  undetermined. Learning the force–motion relation directly from data exists but must be redone per
  object and offers no extrapolation guarantee. Current approaches: identification with a convex
  polynomial model ([Zhou et al. 2016](https://arxiv.org/abs/1602.06056)), fitting the model to
  measured trajectories ([Hogan & Rodriguez 2020](https://doi.org/10.1177/0278364920913938)). What is
  missing: a way to estimate $p$ or $\mathcal{L}$ from few contacts **with a certified error bound**.
- **(open problem) The boundary of the quasi-static assumption** — quantitative criteria for when
  (A1) fails exist only at the level of a dimensionless number. In fast pushing, throwing and hitting
  (dynamic non-prehensile), inertia dominates and the normality rule fails, but there is no unified
  model covering the transition region. Current approach: using the quasi-static model inside an MPC
  and absorbing the error by feedback
  ([Hogan & Rodriguez 2020](https://doi.org/10.1177/0278364920913938)). What is missing: a contact
  model spanning the quasi-static-to-dynamic transition, and guarantees on top of it.
- **(open problem) Generalizing extrinsic dexterity** — the strategies of R4 are **mode sequences
  designed by hand**, and automatically finding the feasible sequences for a given object and
  environment suffers the same blow-up as the skeleton search of `c6-tamp`. Environmental contacts
  increase $n_c$, so $3^{n_c K}$ explodes even faster. Current approaches: the hand-built strategies
  of [Chavan-Dafle et al. 2014](https://doi.org/10.1109/ICRA.2014.6907062), and optimization that
  does not enumerate modes (`s2-planning-through-contact`). What is missing: automatic search over
  mode sequences including external contacts while keeping completeness.

## Concept check

Run `rc quiz s2-contact-modes-dexterity`. Concept checking only; the real work is the problem set and
the reproduction task.

The six items cover: why the limit surface does not depend on the magnitude of the twist; where the
normality rule comes from; $\tau_{\max}$ for a uniform disc; which way the ellipsoidal approximation
errs; what the set of admissible twists is once a mode is fixed; and the closed-form force-motion
formula of the ellipsoidal approximation.

## How to study this stage

1. **Write the force problem and the motion problem as a pair (20 min)** — write the two lines of (1)
   and mark that the previous lesson handled only the first. The second line (friction law plus
   normality) is this entire lesson.
2. **Confirm the linearity of the contact constraint by hand (40 min)** — expand (4) into (5) and see
   that $a_i$ is **the same vector** as the previous lesson's contact wrench (P1). Seeing that duality
   reduces "a mode is a choice of faces of a polyhedral cone" to one line.
3. **Go from the integral to normality in one pass (70 min)** — rewrite R2 from a blank page:
   pointwise maximum dissipation → integration → support function → normal cone. Obtain
   $\tau_{\max} = \frac23\mu NR$ by integrating yourself (P2) and confirm by computation that the
   pressure distribution fixes $c$. **That $c$ ranges over all of $[0, R]$ is the most practically
   important fact in this lesson.**
4. **Turn the approximation error into numbers (40 min)** — do P3 and P4. Confirming where the
   $12.2\%$ comes from, and that it is smaller than the pressure-distribution uncertainty, settles
   "why everybody uses the ellipsoid".
5. **Implement it and see normality with your own eyes (95 min)** — the reproduction task. Match
   criterion 1 (the poles) first, then confirm criterion 2 (normality) at the $10^{-6}$ level.
   **Verifying a theorem numerically is the key artifact of this lesson.** Draw the table of criterion
   4 to see that the true surface lies inside the ellipsoid.
6. **Two papers (120 min)** — Lynch–Mason first (mechanics plus controllability), Chavan-Dafle next
   (the environment as a finger). Organize them in your notes as the contrast "plan with an exactly
   known model" versus "use a loose model and leave it to the environment".
7. **Problem set (160 min)** — P3, P4 and P7 first, then P1 and P2, then P5, P6 and P8 with whatever
   time remains. P6 (with a sticking region) is the hardest and prepares
   `s2-planning-through-contact`.

**Passing bar**: you can write the two lines of (1) and derive the normality of the second from
pointwise maximum dissipation, obtain $\tau_{\max} = \frac23\mu NR$ by integration, have code
satisfying the four criteria of the reproduction task (especially normality below $10^{-5}$), and
state the direction and the worst case of the ellipsoidal approximation error. You have notes on both
papers.
