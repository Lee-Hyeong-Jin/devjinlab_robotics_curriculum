---
id: c1-twists-wrenches-adjoint
lang: en
title: Twists, wrenches and the adjoint representation
summary: >-
  Bundle rigid-body velocity into a twist and force into a wrench as six-dimensional vectors, and
  derive their transformation laws (the adjoint Ad and its dual Ad^T) from the invariance of power.
  Decompose any twist into a screw axis and pitch via Chasles–Mozzi, and prove that Ad is a group
  representation.
objectives:
  - Derive the coordinate transformation law for twists from conjugation by a homogeneous transform.
  - Derive why wrenches transform by the transpose of Ad, using only the invariance of power.
  - Decompose an arbitrary twist into screw axis, pitch and magnitude, and explain why pure translation is the exception.
  - Prove that Ad is a group representation of SE(3) and relate it to the Lie bracket ad.
  - Diagnose the bugs that the (ω, v) versus (v, ω) convention mismatch causes in real code.
tags: [lie-groups, se3, twist, wrench, screw-theory, research]
---

# Twists, wrenches and the adjoint representation

## Setup and notation

The notation of the previous lesson ([`c1-so3-se3-exponential`](so3-se3-exponential.en.md)) carries
over. Additional symbols:

| Symbol | Meaning |
|---|---|
| $\mathcal{V} = (\omega, v) \in \mathbb{R}^6$ | twist; $\omega$ angular velocity, $v$ linear velocity. **This ordering is fixed** |
| $[\mathcal{V}] = \begin{bmatrix} \hat{\omega} & v \\ 0 & 0 \end{bmatrix}$ | the corresponding element of $\mathfrak{se}(3)$ (4×4) |
| $\mathcal{F} = (m, f) \in \mathbb{R}^6$ | wrench; $m$ moment, $f$ force. **Same ordering** as the twist |
| $[\mathrm{Ad}_T] \in \mathbb{R}^{6\times6}$ | the adjoint representation of $T \in SE(3)$ |
| $[\mathrm{ad}_{\mathcal{V}}] \in \mathbb{R}^{6\times6}$ | matrix representation of the Lie bracket |
| $\mathcal{S} = (\hat{s}, -\hat{s}\times q + h\hat{s})$ | screw axis; $\hat{s}$ unit direction, $q$ a point on the axis, $h$ pitch |

**Convention warning**: this course uses the $(\omega, v)$ ordering (Modern Robotics, MLS).
Featherstone's spatial vectors and Pinocchio use $(v, \omega)$. When reading must-read papers 1
and 2, **first confirm that the ordering is flipped** — this mismatch is the most common 6-D bug
in practice (see problem P5).

We use $\hat{a}b = a \times b = -\hat{b}a$ and $R\hat{\omega}R^\top = \widehat{R\omega}$
throughout. Verify the latter yourself (same trick as P1 of the previous lesson).

## Key results

- **R1 (transformation law for twists) [D2]** — for $T_{ab} = (R, p) \in SE(3)$,
  $\mathcal{V}_a = [\mathrm{Ad}_{T_{ab}}] \mathcal{V}_b$ with

$$
[\mathrm{Ad}_T] = \begin{bmatrix} R & 0 \\ \hat{p}R & R \end{bmatrix}. \tag{1}
$$

- **R2 (dual transformation for wrenches) [D2]** — from the single fact that the power
  $\mathcal{V}^\top \mathcal{F}$ is frame-independent,

$$
\mathcal{F}_b = [\mathrm{Ad}_{T_{ab}}]^\top \mathcal{F}_a. \tag{2}
$$

  Twists move by $\mathrm{Ad}$, wrenches by $\mathrm{Ad}^\top$ — **in the opposite direction**.
- **R3 (Chasles–Mozzi: screw decomposition) [D2]** — every twist with $\omega \ne 0$ decomposes
  uniquely into a screw axis $(\hat{s}, q)$, a pitch $h$ and a magnitude
  $\dot{\theta} = \lVert\omega\rVert$:

$$
\hat{s} = \frac{\omega}{\lVert\omega\rVert}, \qquad
h = \frac{\omega^\top v}{\lVert\omega\rVert^2}, \qquad
q_\perp = \frac{\omega \times v}{\lVert\omega\rVert^2}. \tag{3}
$$

  $\omega = 0$ (pure translation) is the **exception**: the axis goes to infinity and the pitch is undefined.
- **R4 ($\mathrm{Ad}$ is a group representation) [D3]** —
  $[\mathrm{Ad}_{T_1 T_2}] = [\mathrm{Ad}_{T_1}][\mathrm{Ad}_{T_2}]$ and
  $[\mathrm{Ad}_T]^{-1} = [\mathrm{Ad}_{T^{-1}}]$. Differentiating gives the Lie bracket:

$$
[\mathrm{ad}_{\mathcal{V}}] = \begin{bmatrix} \hat{\omega} & 0 \\ \hat{v} & \hat{\omega} \end{bmatrix},
\qquad [\mathcal{V}_1, \mathcal{V}_2] = [\mathrm{ad}_{\mathcal{V}_1}]\mathcal{V}_2. \tag{4}
$$

- **R5 (motion and force live in different spaces) [D1]** — twists live in the tangent space
  $\mathfrak{se}(3)$, wrenches in its dual $\mathfrak{se}(3)^*$. Both are six-dimensional and look
  like the same array in code, but **their transformation laws differ**. Using one 6×6 matrix for
  both fails silently.

## Derivation

### R1 — transformation law for twists

A twist is not a vector but **an element of $\mathfrak{se}(3)$**, and changing frames acts by
conjugation with a homogeneous transform:

$$
[\mathcal{V}_a] = T_{ab}\,[\mathcal{V}_b]\,T_{ab}^{-1}. \tag{5}
$$

That (5) is the starting point is the heart of this lesson — why conjugation appears follows from
differentiating $T_a(t) = T_{ab} T_b(t)$ (problem P1). Substituting $T = (R, p)$ and
$T^{-1} = (R^\top, -R^\top p)$ and expanding blockwise:

$$
\begin{bmatrix} R & p \\ 0 & 1 \end{bmatrix}
\begin{bmatrix} \hat{\omega} & v \\ 0 & 0 \end{bmatrix}
\begin{bmatrix} R^\top & -R^\top p \\ 0 & 1 \end{bmatrix}
= \begin{bmatrix} R\hat{\omega} & Rv \\ 0 & 0 \end{bmatrix}
\begin{bmatrix} R^\top & -R^\top p \\ 0 & 1 \end{bmatrix}
= \begin{bmatrix} R\hat{\omega}R^\top & -R\hat{\omega}R^\top p + Rv \\ 0 & 0 \end{bmatrix}.
$$

Applying $R\hat{\omega}R^\top = \widehat{R\omega}$ to the upper-left block gives
$\omega_a = R\omega_b$. The upper-right block is

$$
v_a = -\widehat{R\omega_b}\,p + Rv_b = p \times (R\omega_b) + Rv_b = \hat{p}R\omega_b + Rv_b,
$$

using $-\hat{a}b = \hat{b}a$. Stacking the two gives (1).

**The easiest sign to get wrong** is the single line turning $-\widehat{R\omega}p$ into
$\hat{p}R\omega$: the sign is absorbed because $-a \times b = b \times a$. Skip that line and the
sign of $\hat{p}$ flips, so the velocity transform is silently wrong — angular velocity stays
correct and only linear velocity breaks, so rotation-only tests will not catch it.

**Where the assumption breaks**: (5) is the transformation for a **constant** $T_{ab}$. If the
frame moves, a $\dot{T}_{ab} \ne 0$ term is added (the Coriolis term of a moving observation
frame). That term reappears as the Coriolis term of spatial acceleration in
`c2-spatial-vector-algebra`.

### R2 — dual transformation for wrenches

The work done by a force (power) does not depend on which coordinate frame we pick. That is all we use:

$$
\mathcal{V}_b^\top \mathcal{F}_b = \mathcal{V}_a^\top \mathcal{F}_a
\quad \text{for every } \mathcal{V}_b. \tag{6}
$$

Substituting $\mathcal{V}_a = [\mathrm{Ad}_{T_{ab}}]\mathcal{V}_b$ from R1,

$$
\mathcal{V}_b^\top \mathcal{F}_b = \big([\mathrm{Ad}_{T_{ab}}]\mathcal{V}_b\big)^\top \mathcal{F}_a
= \mathcal{V}_b^\top [\mathrm{Ad}_{T_{ab}}]^\top \mathcal{F}_a .
$$

Since this holds for every $\mathcal{V}_b$, it can be cancelled, giving (2).

**How to read it**: $\mathrm{Ad}_{T_{ab}}$ carries twists from $b$ to $a$, while the transpose of
the same matrix carries wrenches from $a$ to $b$ — the opposite direction. This is what the
duality of R5 means concretely, and it is the same structure that makes $\Lambda$ and $J^\top$
appear in operational-space control (`c2-constrained-dynamics`).

**Failure mode**: writing $\mathcal{F}_a = [\mathrm{Ad}_{T_{ab}}]\mathcal{F}_b$ (i.e. forgetting
the transpose) produces **no visible error** for rotation-only transforms ($p = 0$), because there
$[\mathrm{Ad}]$ is block diagonal and orthogonal. It only breaks when there is translation — so
tests must include $p \ne 0$.

### R3 — screw decomposition

Assume $\omega \ne 0$ and set $\dot{\theta} = \lVert\omega\rVert$, $\hat{s} = \omega/\dot{\theta}$.
By definition, the twist of a screw motion whose axis passes through $q$ with pitch $h$ is

$$
\omega = \hat{s}\dot{\theta}, \qquad v = (-\hat{s} \times q + h\hat{s})\dot{\theta}. \tag{7}
$$

Normalise $\dot{\theta} = 1$ and invert (7) for $h$ and $q$.

- **Pitch**: $\hat{s}^\top v = \hat{s}^\top(-\hat{s}\times q) + h\,\hat{s}^\top\hat{s} = 0 + h$,
  using $\hat{s} \perp (\hat{s}\times q)$ in the first term. Undoing the normalisation gives $h$ in (3).
- **Position of the axis**: $\hat{s} \times v = \hat{s}\times(-\hat{s}\times q) + h(\hat{s}\times\hat{s})
  = -\big(\hat{s}(\hat{s}^\top q) - q\big) = q - \hat{s}(\hat{s}^\top q) = q_\perp$, the component
  of $q$ perpendicular to the axis. The component **along** the axis is not recovered — as it
  should not be, since any point on the axis describes the same screw. That is why (3) returns
  $q_\perp$ rather than $q$.

**The case $\omega = 0$**: the denominators in (3) vanish. Geometrically the axis has receded to
infinity and rotation has degenerated into translation; algebraically $\mathcal{V} = (0, v)$ can
only be treated as "pitch $\infty$". Implementations handle it with a **branch** (problem P4). The
same degeneracy appears at the same place in the screw interpolation of `c6-kinodynamic-planning`.

## Proof sketch

### R4 — $\mathrm{Ad}$ is a group representation

**Hypotheses** H1: $T_1, T_2 \in SE(3)$. H2: $\mathrm{Ad}$ is defined by the conjugation (5).
**Conclusion** C: $[\mathrm{Ad}_{T_1T_2}] = [\mathrm{Ad}_{T_1}][\mathrm{Ad}_{T_2}]$.

**Strategy**: associativity of conjugation. Show it **from the definition** rather than by
multiplying matrices — shorter than expanding 6×6 blocks, and it also shows *why* it holds.

1. Write the definition (5) as
   $[\mathrm{Ad}_T]\mathcal{V} = \big(T[\mathcal{V}]T^{-1}\big)^\vee$, where $(\cdot)^\vee$ inverts $[\cdot]$.
2. For any $\mathcal{V}$,
   $$
   [\mathrm{Ad}_{T_1T_2}]\mathcal{V} = \big((T_1T_2)[\mathcal{V}](T_1T_2)^{-1}\big)^\vee
   = \big(T_1\big(T_2[\mathcal{V}]T_2^{-1}\big)T_1^{-1}\big)^\vee,
   $$
   using only $(T_1T_2)^{-1} = T_2^{-1}T_1^{-1}$ and associativity of matrix multiplication.
3. The inner bracket is $[\,[\mathrm{Ad}_{T_2}]\mathcal{V}\,]$ by step 1, so the whole expression
   is $[\mathrm{Ad}_{T_1}]\big([\mathrm{Ad}_{T_2}]\mathcal{V}\big)$.
4. Equality for every $\mathcal{V}$ means equality as matrices. C.
5. Setting $T_2 = T_1^{-1}$ gives $[\mathrm{Ad}_T][\mathrm{Ad}_{T^{-1}}] = [\mathrm{Ad}_I] = I$,
   so the inverse formula follows too.
6. Setting $T = \exp([\mathcal{V}_1]t)$ and differentiating at $t=0$ yields $\mathrm{ad}$ in (4)
   (omitted: the differential of the exponential map — see `c1-lie-group-derivatives`).

**Delete a hypothesis**: if $T$ were a general invertible matrix rather than an element of
$SE(3)$, steps up to 2 would still hold but $T[\mathcal{V}]T^{-1}$ would not stay in
$\mathfrak{se}(3)$ — the upper-left block would cease to be skew-symmetric and $(\cdot)^\vee$
would be undefined. So **conjugation preserving the Lie algebra** is what the $SE(3)$ structure buys.

## Problem set

★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Derive why (5) is the transformation law for twists. Differentiate
$T_a(t) = T_{ab}T_b(t)$, express $\dot{T}_a T_a^{-1}$ in terms of $\dot{T}_b T_b^{-1}$, and show
the result is (5).
*Solution sketch*: $\dot{T}_a = T_{ab}\dot{T}_b$ and $T_a^{-1} = T_b^{-1}T_{ab}^{-1}$ multiply to
$\dot{T}_aT_a^{-1} = T_{ab}(\dot{T}_bT_b^{-1})T_{ab}^{-1}$. The brackets on each side are
$[\mathcal{V}_a]$ and $[\mathcal{V}_b]$ (the definition of the spatial twist).

**P2 (derivation, ★★, R2·R4)** Verify $[\mathrm{Ad}_T]^{-1} = [\mathrm{Ad}_{T^{-1}}]$ by direct
computation from the block form (1), and compare with step 5 of R4 (which follows from the
definition). Which is shorter? Which tells you more?
*Solution sketch*: the block inverse is
$\begin{bmatrix} R^\top & 0 \\ -R^\top\hat{p} & R^\top\end{bmatrix}$, and
$-R^\top\hat{p} = \widehat{(-R^\top p)}R^\top$ turns it into $[\mathrm{Ad}_{T^{-1}}]$.

**P3 (proof, ★★★, R4)** Show that $[\mathrm{ad}_{\mathcal{V}}]$ in (4) correctly represents the
Lie bracket
$[\mathcal{V}_1,\mathcal{V}_2] = ([\mathcal{V}_1][\mathcal{V}_2] - [\mathcal{V}_2][\mathcal{V}_1])^\vee$,
and confirm the Jacobi identity.
*Solution sketch*: expanding the 4×4 block product gives upper-left
$\hat{\omega}_1\hat{\omega}_2 - \hat{\omega}_2\hat{\omega}_1 = \widehat{\omega_1\times\omega_2}$
and upper-right $\hat{\omega}_1v_2 - \hat{\omega}_2v_1$. Jacobi reduces to a property of matrix commutators.

**P4 (implementation, ★★, R1·R2·R3)** Write `Ad(T)`, `ad(V)`, `twist_to_screw(V)` and
`screw_to_twist(s, q, h, dtheta)`. `twist_to_screw` must handle the $\omega = 0$ branch.
*Rubric*: (a) for $\lVert\omega\rVert < 10^{-12}$ it returns a "pure translation" marker instead
of raising; (b) the round trip `screw_to_twist(*twist_to_screw(V))` meets the reproduction
criteria; (c) the wrench transform uses $[\mathrm{Ad}]^\top$ with the transpose not forgotten;
(d) the $(\omega, v)$ ordering is documented.

**P5 (counterexample, ★★, R2·R5)** Construct one test that a transpose-forgetting wrench
transform ($\mathcal{F}_a \leftarrow [\mathrm{Ad}_{T_{ab}}]\mathcal{F}_b$) **passes** and one that
it **catches**. Why can a rotation-only test never catch this bug?
*Property checklist*: with $p = 0$, $[\mathrm{Ad}]$ is block diagonal $\mathrm{diag}(R, R)$ and
$[\mathrm{Ad}]^\top = \mathrm{diag}(R^\top, R^\top) = [\mathrm{Ad}]^{-1}$, so a round-trip test
that only checks "does the inverse transform return the original" cannot distinguish the two cases.

**P6 (numerical, ★, R3)** Find the screw axis, pitch and magnitude of
$\mathcal{V} = (\omega, v)$ with $\omega = (0, 0, 2)$ and $v = (0, 4, 6)$.
*Answer*: $\dot{\theta} = 2$, $\hat{s} = (0,0,1)$,
$h = \omega^\top v/\lVert\omega\rVert^2 = 12/4 = 3$,
$q_\perp = (\omega\times v)/\lVert\omega\rVert^2 = (-8, 0, 0)/4 = (-2, 0, 0)$.
Tolerance $10^{-9}$. Check by substituting into (7):
$(-(0,0,1)\times(-2,0,0) + (0,0,3))\cdot 2 = ((0,2,0)+(0,0,3))\cdot2 = (0,4,6)$. ✓

## Paper reading

**Three must-read papers.** Write a one-page note per paper against the ten fixed questions
(`research_notes/연구 트랙 설계/lesson-standard.md` §5).

1. **Featherstone, "A beginner's guide to 6-D vectors", part 1 (2010, IEEE RAM)** —
   role: `standard`. <https://doi.org/10.1109/MRA.2010.937853>
   Extra questions: (a) if you map the author's $(v, \omega)$ ordering into this lesson's
   $(\omega, v)$, how are the blocks of $[\mathrm{Ad}]$ rearranged? (b) explain, in terms of R2
   and R5, why the author insists that motion vectors and force vectors be **different types**.
2. **Featherstone, part 2 (2010, IEEE RAM)** — role: `standard`.
   <https://doi.org/10.1109/MRA.2010.939560>
   Extra question: what is the operation-count difference between transforming "once as 6×6" and
   "twice as 3×3"?
3. **Brockett, "Robotic manipulators and the product of exponentials formula" (1984, LNCIS)** —
   role: `seminal`. <https://doi.org/10.1007/BFb0031048>
   Extra question: what does viewing joints as twists simplify, compared with DH parameters?
   (This is the starting point of the next lesson, `c1-poe-analytic-ik`.)

## Reproduction task

**Tier R1 (numerical check).** Budget: under one minute on a laptop CPU, numpy only. All four
conditions must pass. **Include transforms with $p \ne 0$ in every test** — using only $p = 0$
misses the failure mode of R2.

1. **$\mathrm{Ad}$ agrees with conjugation**: for 1000 random pairs of $T \in SE(3)$ and
   $\mathcal{V} \in \mathbb{R}^6$,
   $\big\lVert \big(T[\mathcal{V}]T^{-1}\big)^\vee - [\mathrm{Ad}_T]\mathcal{V} \big\rVert_\infty < 10^{-12}$.
2. **Representation property**: for 1000 random pairs $T_1, T_2$,
   $\lVert [\mathrm{Ad}_{T_1T_2}] - [\mathrm{Ad}_{T_1}][\mathrm{Ad}_{T_2}] \rVert_F < 10^{-12}$ and
   $\lVert [\mathrm{Ad}_T]^{-1} - [\mathrm{Ad}_{T^{-1}}] \rVert_F < 10^{-12}$.
3. **Invariance of power**: for random $T$, $\mathcal{V}_b$, $\mathcal{F}_a$,
   $\big| \mathcal{V}_b^\top([\mathrm{Ad}_T]^\top\mathcal{F}_a) - ([\mathrm{Ad}_T]\mathcal{V}_b)^\top\mathcal{F}_a \big| < 10^{-12}$.
   Additionally, **check that a deliberately transpose-free implementation fails this test** (run
   the wrong version on purpose).
4. **Screw round trip**: for $10^4$ twists with $\lVert\omega\rVert \in (10^{-6}, 10)$,
   `screw_to_twist(*twist_to_screw(V))` agrees with the original $\mathcal{V}$ to $10^{-10}$. For
   10 inputs with $\omega = 0$, the pure-translation case is handled without raising.

**Baseline**: velocity by finite differences. Numerically differentiating
$T_a(t) = T_{ab}\exp([\mathcal{V}_b]t)$ must give a $\mathcal{V}_a$ agreeing with
$[\mathrm{Ad}_{T_{ab}}]\mathcal{V}_b$ to within $10^{-6}$.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| angular velocity right, linear velocity wrong | sign of the $\hat{p}R$ block ($-\widehat{R\omega}p = \hat{p}R\omega$) | hand-check with $p = (1,0,0)$, $\omega = (0,0,1)$, $v = 0$ |
| rotation-only tests pass, translation ones fail | the transpose was forgotten in the wrench transform | run condition 3 with $p \ne 0$ |
| 6-D components get scrambled | mixing with a library's $(v,\omega)$ ordering | feed the unit twists $e_1 \dots e_6$ and see which block moves |
| screw axis blows up as $\omega \to 0$ | the $1/\lVert\omega\rVert^2$ in (3) | sweep the branch threshold on a log scale and plot the error |

## Open problems

- **(Open) Numerical conditioning of 6-D formulations with contact and constraints** — projection
  into the constraint space (forms like $J\Lambda^{-1}J^\top$) has exploding condition numbers
  near singular configurations. There is no general guidance on which 6-D coordinates and scaling
  minimise that condition number, since length and angle units are mixed and the scaling therefore
  depends on physical units. Current approaches: the operational-space formulation of
  `c2-constrained-dynamics` ([Khatib 1987](https://doi.org/10.1109/JRA.1987.1087068)) and weighted
  pseudo-inverses.
- **(Open) Propagating derivatives of $\mathrm{Ad}$ in differentiable simulators** — where contact
  is non-smooth and gradients are undefined, which gradient is legitimate while preserving Lie
  group structure is unsettled. Current approaches:
  [Pinocchio's analytical derivatives](https://doi.org/10.15607/RSS.2018.XIV.038) and
  [convex contact relaxations](https://doi.org/10.1109/ICRA.2014.6907751). Revisited in `c2-contact-dynamics`.
- **(Open) The reproducibility cost of convention mismatch** — $(\omega,v)$ versus $(v,\omega)$,
  left versus right Jacobians, body versus spatial twists all differ between libraries, and papers
  frequently leave the convention unstated. No quantitative study measures how often this causes
  reproduction failures — a good case study for `r1-reproducibility-artifacts`.

## Concept check

Run `rc quiz c1-twists-wrenches-adjoint` (add `--lang en` for the English text). It is for concept
checking only; the real work is the problem set and the reproduction task.

The four items cover: how wrenches transform relative to twists; why a rotation-only test cannot
catch a forgotten transpose; the screw pitch formula; and the shortest way to prove that
$\mathrm{Ad}$ is a group representation.

## How to study this stage

1. **Nail down the ordering first (20 min)** — decide to write $(\omega, v)$, then check and note
   the ordering of every reference you use. Featherstone's is flipped. Saving these 20 minutes
   costs you a day later.
2. **Expand R1 blockwise yourself (60 min)** — reproduce the three-line expansion on paper. If you
   stall on $-\widehat{R\omega}p = \hat{p}R\omega$, all you need is $-a\times b = b\times a$.
3. **For R2, remember only "power is invariant" (30 min)** — do not memorise where the transpose
   comes from; be able to pull it out of (6) again. Anyone who confuses signs and transposes here
   is someone who cannot redo this derivation.
4. **Do the screw decomposition by hand once (40 min)** — solve P6 first and check it against (7).
   Draw why only $q_\perp$ is recovered (any point on the axis will do).
5. **Introduce the bug deliberately (60 min)** — in condition 3 of the reproduction task, run the
   transpose-free version and confirm **the test actually fails**. If it passes, your test is weak (P5).
6. **Read the papers by mapping conventions (110 min)** — read Featherstone part 1 transcribing his
   $(v,\omega)$ into this lesson's notation, then see the operation-count discussion in part 2.
   Brockett 1984 is a prerequisite for the next lesson, so take away the view of joints as twists.

**Passing bar**: you can derive (1) and (2) on a blank page, can explain why a forgotten transpose
in the wrench transform survives rotation-only tests, have code meeting all four acceptance
conditions, and have notes on all three papers.
