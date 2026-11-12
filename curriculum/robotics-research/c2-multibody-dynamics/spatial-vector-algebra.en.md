---
id: c2-spatial-vector-algebra
lang: en
title: Spatial vector algebra
summary: >-
  Rewrite rigid-body dynamics as a dual pair of six-dimensional spaces, a motion space and a
  force space; derive the transformation law of spatial inertia and the motion and force cross
  products; and show at the level of proof how the Coriolis and centrifugal terms fall out of the
  time derivative of spatial inertia. Ends at the root cause of the most common error in the
  field: that spatial acceleration is not the acceleration of a point.
objectives:
  - Derive the duality of motion and force space from the invariance of power and show that the force transform is $X^{-\top}$.
  - Assemble the spatial inertia matrix directly from the definition of momentum and derive its coordinate transformation law.
  - Write the relation between the motion cross product $v\times$ and the force cross product $v\times^{*}$ and differentiate a spatial transform.
  - Prove $\dot{I} = v\times^{*} I - I\, v\times$ and separate the Newton-Euler bias force out of it.
  - Explain the difference between spatial acceleration and the classical acceleration of a body-fixed point, and name the errors the confusion produces.
tags: [multibody-dynamics, spatial-vectors, plucker, rigid-body, research]
---

# Spatial vector algebra

## Setup and notation

Assumptions: $A$ and $B$ are both coordinate frames defined **at the same instant**, and the body
is a rigid body whose mass distribution does not change. Deformable and variable-mass bodies are
outside this module. The recommended prerequisite is module C1 (`c1-so3-se3-exponential`,
`c1-twists-wrenches-adjoint`), and it is not locked — use the self-diagnosis below to decide.

The whole module uses **Featherstone's convention** (RBDA ch.2). The two choices that matter most:

- **The components of a 6-D vector are ordered angular first**: $v = (\omega; v_O)$,
  $f = (n_O; f_\ell)$. Featherstone's RBDA and spatial_v2, and the twist
  $\mathcal{V} = (\omega, v)$ of Modern Robotics, all use this order, so it carries over from C1
  unchanged. **Pinocchio, by contrast, puts the linear part first** ($v$, then $\omega$) — check
  that first whenever you compare numbers against external code; the reproduction task writes
  that permutation out explicitly.
- **Motion and force live in two different vector spaces.** They are implemented as the same
  $\mathbb{R}^6$ but they transform by different rules.

| Symbol | Meaning |
|---|---|
| $M^6$ | Motion space: the 6-D space of spatial velocities, accelerations and joint axes |
| $F^6$ | Force space: the dual of $M^6$, where spatial forces, momenta and impulses live |
| $v = (\omega; v_O) \in M^6$ | Spatial velocity. $\omega$ is the angular velocity; $v_O$ is the velocity of the **body-fixed point that instantaneously coincides with the coordinate origin** |
| $f = (n_O; f_\ell) \in F^6$ | Spatial force. $n_O$ is the moment about the origin, $f_\ell$ the resultant force |
| $a = \dot{v} \in M^6$ | Spatial acceleration: **the componentwise derivative of $v$ in a fixed frame** (see R5) |
| $h = (h_\omega; h_\ell) \in F^6$ | Spatial momentum. $h_\ell$ is linear momentum, $h_\omega$ the angular momentum about the origin |
| $I \in \mathbb{R}^{6\times6}$ | Spatial inertia: a symmetric positive-definite map $M^6 \to F^6$ |
| $^B X_A$ | Coordinate transform of motion vectors, $M^6 \to M^6$: $v_B = {}^BX_A\,v_A$ |
| $^B X_A^{*}$ | Coordinate transform of force vectors, $F^6 \to F^6$: $f_B = {}^BX_A^{*}\,f_A$ |
| $E = {}^B R_A \in SO(3)$, $p \in \mathbb{R}^3$ | Orientation and origin of frame $B$; $p$ is **the origin of $B$ written in $A$ coordinates** |
| $\hat{x}$ | The skew-symmetric matrix of $x \in \mathbb{R}^3$. $\hat{x}y = x \times y$, $\hat{x}^\top = -\hat{x}$ |
| $v\times$, $v\times^{*}$ | The motion and force cross products ($6\times6$ matrices, see R3) |
| $\mathbb{1}_3$ | The $3\times3$ identity |

The two identities from C1 are used throughout (expand them yourself to check):

$$\hat{x}\hat{x}^\top = -\hat{x}^2 = \lVert x \rVert^2 \mathbb{1}_3 - xx^\top, \qquad \widehat{Rx} = R\hat{x}R^\top \;\; (R \in SO(3)). \tag{1}$$

## Self-diagnosis before starting

This is the first lesson of the module, so check your readiness first. **Prerequisite lessons are
not locked** — if you can solve all of the following, skip the recommended prerequisites (module
C1 and M7 of the `robotics-expert` course) and start here. **If two or more stop you**, going back
to the prerequisite lesson named in parentheses is faster. Every derivation in this lesson is a
combination of these five things.

1. For $x = (1, -2, 2)$, write $\hat{x}\hat{x}^\top$ as a numeric matrix.
   (`c1-so3-se3-exponential`)
   **Answer** (tolerance $10^{-12}$): $\hat{x}\hat{x}^\top = \lVert x\rVert^2\mathbb{1} - xx^\top
   = \begin{bmatrix} 8 & 2 & -2 \\ 2 & 5 & 4 \\ -2 & 4 & 5\end{bmatrix}$.
   Checks: the trace is $2\lVert x\rVert^2 = 18$, and $\hat{x}\hat{x}^\top x = 0$.
2. For $R(t) \in SO(3)$, show that $S = \dot{R}R^\top$ is skew-symmetric and say which vector
   corresponds to $S$. (`c1-so3-se3-exponential`)
   **Answer**: differentiating $RR^\top = \mathbb{1}$ gives $\dot{R}R^\top + R\dot{R}^\top = 0$,
   i.e. $S + S^\top = 0$. Then $S = \hat{\omega}$ where $\omega$ is the angular velocity
   **expressed in the fixed frame** (the body-frame angular velocity is $R^\top\dot{R}$ instead) —
   this distinction fixes the signs throughout the lesson.
3. For a rigid body with $m = 3$, centre of mass $c = (0, 0, 0.5)$ and rotational inertia about
   the centre of mass $\bar{I}_C = \mathrm{diag}(0.2, 0.2, 0.1)$, find the rotational inertia
   $I_O$ **about the origin**. (M7 of the `robotics-expert` course, or MR ch.8.2)
   **Answer** (tolerance $10^{-12}$): $I_O = \bar{I}_C + m(\lVert c\rVert^2\mathbb{1} - cc^\top)
   = \mathrm{diag}(0.95,\ 0.95,\ 0.1)$. That the $z$ component does not change is the point of the
   parallel-axis theorem.
4. For a homogeneous transform $T = (R, p)$, write the adjoint representation $\mathrm{Ad}_T$
   acting on a twist $(\omega; v)$ as a $6\times6$ block matrix.
   (`c1-twists-wrenches-adjoint`)
   **Answer**: $\mathrm{Ad}_T = \begin{bmatrix} R & 0 \\ \hat{p}R & R\end{bmatrix}$ (angular
   components first). The $^AX_B$ of this lesson is exactly this matrix, and
   $\mathrm{Ad}_T^{-\top}$ is the $\mathrm{Ad}_T^{*}$ that acts on wrenches.
5. For an invertible matrix-valued function $A(t)$, write $\frac{d}{dt}(A^{-1})$ in terms of $A$
   and $\dot{A}$. (`r0-linear-algebra-decompositions`)
   **Answer**: differentiating $AA^{-1} = \mathbb{1}$ gives
   $\dot{A}A^{-1} + A\frac{d}{dt}(A^{-1}) = 0$, hence
   $\frac{d}{dt}(A^{-1}) = -A^{-1}\dot{A}A^{-1}$. That one line produces the second identity in (5).

## Key results

The bracketed grade is the derivation depth (D0 cited / D1 sketched / D2 full derivation /
D3 proof — see `lesson-standard.md` §2 in the track design notes).

- **R1 (duality of motion and force space) [D2]** — the power $p = f \cdot v$ is a scalar
  independent of the coordinate frame. In a dual basis it is computed as $p = f^\top v$, and that
  **single requirement** determines the transformation rule for forces:
  $$
  f_B^\top v_B = f_A^\top v_A \;\; \forall v_A \in M^6
    \quad\Longrightarrow\quad {}^BX_A^{*} = \big({}^BX_A\big)^{-\top} = \big({}^AX_B\big)^{\top}. \tag{2}
  $$
  Explicitly, for $E = {}^BR_A$ and $p$ (the origin of frame $B$ in $A$ coordinates),
  $$
  {}^BX_A = \begin{bmatrix} E & 0 \\ -E\hat{p} & E \end{bmatrix}, \qquad
  {}^BX_A^{*} = \begin{bmatrix} E & -E\hat{p} \\ 0 & E \end{bmatrix}. \tag{3}
  $$
- **R2 (spatial inertia and its transformation law) [D2]** — for a rigid body with mass $m$,
  centre of mass $c$ (in the current frame) and rotational inertia $\bar{I}_C$ about the centre of
  mass, $h = Iv$ with
  $$
  I = \begin{bmatrix} \bar{I}_C + m\,\hat{c}\hat{c}^\top & m\,\hat{c} \\[2pt] m\,\hat{c}^\top & m\,\mathbb{1}_3 \end{bmatrix}, \qquad
  {}^BI = {}^BX_A^{*}\;{}^AI\;{}^AX_B = \big({}^AX_B\big)^\top {}^AI \;{}^AX_B. \tag{4}
  $$
  Inertia is a map $M^6 \to F^6$, so it moves by a **congruence**, **not** by the similarity
  transform $X^{-1}IX$ that uses the transpose of the motion transform on both sides.
- **R3 (motion and force cross products, and the derivative of a transform) [D2]** — if frame $B$
  moves with spatial velocity $v$ (in $A$ coordinates) relative to frame $A$, then
  $$
  \frac{d}{dt}\,{}^AX_B = (v\times)\;{}^AX_B, \qquad
  \frac{d}{dt}\,{}^BX_A = -\,{}^BX_A\,(v\times), \qquad
  \frac{d}{dt}\,{}^AX_B^{*} = (v\times^{*})\;{}^AX_B^{*}, \tag{5}
  $$
  where, for $v = (\omega; v_O)$,
  $$
  v\times = \begin{bmatrix} \hat{\omega} & 0 \\ \hat{v}_O & \hat{\omega}\end{bmatrix} \in \mathbb{R}^{6\times6},
  \qquad v\times^{*} = \begin{bmatrix} \hat{\omega} & \hat{v}_O \\ 0 & \hat{\omega}\end{bmatrix} = -\,(v\times)^\top. \tag{6}
  $$
  $v\times$ acts on $M^6$ and $v\times^{*}$ on $F^6$. They are **not two notations for one
  operation but two different actions on dual spaces**, and the sign and transpose appear for the
  same reason as in (2).
- **R4 (time derivative of spatial inertia, and separation of the bias force) [D3]** — the spatial
  inertia of a rigid body seen from a fixed frame varies in time, and
  $$
  \dot{I} = (v\times^{*})\,I - I\,(v\times). \tag{7}
  $$
  Hence in $f = \dot{h} = \dot{I}v + I\dot{v}$, using $v\times v = 0$, the Newton-Euler equation
  splits as
  $$
  f = I\,a + (v\times^{*})\,I\,v. \tag{8}
  $$
  The second term is the **bias force**: independent of acceleration, and since
  $v^\top\!\big((v\times^{*})Iv\big) = 0$ it **does no work** — this is the coordinate-free
  definition of the Coriolis and centrifugal terms.
- **R5 (spatial acceleration is not the acceleration of a point) [D2]** — $a = \dot{v} =
  (\dot{\omega}; \dot{v}_O)$, whereas the **classical acceleration** of the body-fixed point
  currently coinciding with the coordinate origin is
  $$
  a_{\text{classical}} = \dot{v}_O + \omega \times v_O \;\ne\; a_\ell \;(= \dot{v}_O). \tag{9}
  $$
  The two differ by $\omega \times v_O$. Substituting $a_{\text{classical}}$ into (8) gives the
  wrong torque — but in the special case where the origin sits at the centre of mass and
  $v_O = 0$ it is accidentally right, so the test passes. **[D2]**

## Derivation

### R1 — duality determines the transformation rule for forces

The starting point is a single physical fact: **power does not change when you change frames.**
The power that a spatial force $f$ delivers to a body moving with spatial velocity $v$ is
independent of the observer's choice of coordinates.

Pick a basis $\{m_i\}$ for $M^6$ and the **dual basis** $\{f^j\}$ for $F^6$, i.e. the basis with
$f^j \cdot m_i = \delta^j_i$. Then power in components is simply $p = f^\top v$. (With a
non-dual basis a metric matrix appears in the middle and this identity breaks — which is the root
reason why "transforming a force vector as if it were a motion vector" is wrong.)

Writing the same physical pair $(f, v)$ in two frames with $v_B = {}^BX_A v_A$, invariance of power
demands

$$
f_B^\top\,{}^BX_A\,v_A = f_A^\top v_A \quad \forall v_A \in M^6.
$$

Since $v_A$ is arbitrary, the row vectors on both sides must agree:
$\big({}^BX_A\big)^\top f_B = f_A$. Multiplying by $\big({}^BX_A\big)^{-\top}$ gives

$$
f_B = \big({}^BX_A\big)^{-\top} f_A \;\;\Longrightarrow\;\; {}^BX_A^{*} = \big({}^BX_A\big)^{-\top} = \big({}^AX_B\big)^{\top},
$$

which is (2); the last equality follows from $\big({}^BX_A\big)^{-1} = {}^AX_B$.

Now set up the left half of (3). The origin of frame $B$ sits at $p$ in $A$ coordinates and its
orientation is $E = {}^BR_A$. By the velocity relation between two points of a rigid body,
$v_P = v_Q + \omega \times (p - q)$,

$$
\omega_B = E\,\omega_A, \qquad
v_{OB} = E\big(v_{OA} + \omega_A \times p\big) = E\big(v_{OA} - \hat{p}\,\omega_A\big),
$$

where $\omega_A \times p = \hat{\omega}_A p = -\hat{p}\,\omega_A$ (anticommutativity of the skew
form) was used. Collecting the blocks gives $^BX_A$ in (3). Its inverse is checked by direct
multiplication:

$$
\begin{bmatrix} E^\top & 0 \\ \hat{p}E^\top & E^\top\end{bmatrix}
\begin{bmatrix} E & 0 \\ -E\hat{p} & E\end{bmatrix}
= \begin{bmatrix} \mathbb{1} & 0 \\ \hat{p} - \hat{p} & \mathbb{1}\end{bmatrix} = \mathbb{1}_6
\;\;\Longrightarrow\;\; {}^AX_B = \begin{bmatrix} E^\top & 0 \\ \hat{p}E^\top & E^\top\end{bmatrix}.
$$

Transposing and using $\hat{p}^\top = -\hat{p}$ gives the right half of (3),
$^BX_A^{*} = \begin{bmatrix} E & -E\hat{p} \\ 0 & E\end{bmatrix}$. Cross-checking against physics:
$f_{\ell B} = Ef_{\ell A}$ and $n_{OB} = E(n_{OA} - p \times f_{\ell A})$ — exactly the formula for
moving the moment reference point to $p$. Derivation and physics agree.

**Where the assumption breaks**: (2) presupposes a **dual basis**. If you treat a 6-D vector as
"just $\mathbb{R}^6$" and use the same transform for motion and force, then for a pure translation
($E = \mathbb{1}$, $p \ne 0$) the sign of the moment-transfer term flips and the result is
immediately wrong. Some sources also order the components of $M^6$ and $F^6$ differently (angular
first for motion, linear first for force); then $p = f^\top v$ does not hold and becomes
$p = f^\top \Sigma v$ with $\Sigma$ a block-swap matrix. Check both of these first when matching
external code.

### R2 — assembling spatial inertia, and its transformation

Assemble it directly from the definition of momentum. The velocity of the centre of mass is, by
the same two-point relation, $v_C = v_O + \omega \times c = v_O - \hat{c}\,\omega$, so the linear
momentum is

$$
h_\ell = m\,v_C = m\,v_O - m\hat{c}\,\omega = m\hat{c}^\top \omega + m\,v_O,
$$

using $\hat{c}^\top = -\hat{c}$. The angular momentum about the origin $O$ is the intrinsic
angular momentum about the centre of mass plus the moment of the linear momentum concentrated at
the centre of mass:

$$
h_\omega = \bar{I}_C\,\omega + c \times h_\ell = \bar{I}_C\omega + \hat{c}\big(m v_O - m\hat{c}\omega\big)
  = \big(\bar{I}_C - m\hat{c}^2\big)\omega + m\hat{c}\,v_O.
$$

By (1), $-\hat{c}^2 = \hat{c}\hat{c}^\top$, so
$h_\omega = (\bar{I}_C + m\hat{c}\hat{c}^\top)\omega + m\hat{c}v_O$. Collecting the two into
$h = Iv$ gives the $I$ of (4). The term $m\hat{c}\hat{c}^\top = m(\lVert c\rVert^2\mathbb{1} - cc^\top)$
in the upper-left block is exactly the **parallel-axis (Steiner) term**, and the off-diagonal
blocks are the **coupling** produced by the centre-of-mass offset. $I$ is symmetric: since
$(m\hat{c})^\top = m\hat{c}^\top$, the off-diagonal blocks are transposes of each other.

The transformation law follows from $I$ being a **map**. We have $h_A = {}^AI\,v_A$, and $h$ lives
in force space, so

$$
h_B = {}^BX_A^{*}\,h_A = {}^BX_A^{*}\,{}^AI\,v_A = {}^BX_A^{*}\,{}^AI\,{}^AX_B\,v_B,
$$

which holds for every $v_B$, hence $^BI = {}^BX_A^{*}\,{}^AI\,{}^AX_B$. By (2),
$^BX_A^{*} = ({}^AX_B)^\top$, so this is a congruence $Y^\top I Y$ with $Y = {}^AX_B$, and
therefore **symmetry and positive definiteness are preserved**. Reading it through kinetic energy
says the same thing: $T = \frac{1}{2}v^\top I v$ is a scalar, so $I$ must transform like a
quadratic form.

**Where the assumption breaks**: moving $I$ by the similarity transform $X^{-1}IX$ destroys
symmetry (for a pure rotation, $p = 0$, we have $X^{-1} = X^\top$ and it is **accidentally
right**; it becomes wrong the moment a translation is involved). That is why condition 2 of the
reproduction task exists. Also, the $I$ of (4) is **referred to the current coordinate origin** —
putting $\bar{I}_C$ into the upper-left block while $c \ne 0$ simply omits the parallel-axis term.

### R3 — cross products and the derivative of a transform

The definition of $v\times$ is "the term that appears when you differentiate a motion vector in a
moving frame". The shortest route starts from the first identity in (5). Write $^AX_B$ in
components and differentiate $E(t) = {}^BR_A(t)$ and $p(t)$. Setting $^AR_B = E^\top \equiv R$, C1
gives $\dot{R} = \hat{\omega}R$ (with $\omega$ the angular velocity in $A$ coordinates), and the
velocity of the origin of frame $B$ is $\dot{p} = v_O + \omega \times p$ (when that origin is
fixed in the body — the two-point relation again). Then

$$
{}^AX_B = \begin{bmatrix} R & 0 \\ \hat{p}R & R \end{bmatrix}
\;\;\Longrightarrow\;\;
\frac{d}{dt}{}^AX_B = \begin{bmatrix} \hat{\omega}R & 0 \\ \dot{\hat{p}}R + \hat{p}\hat{\omega}R & \hat{\omega}R\end{bmatrix}.
$$

Tidy up the lower-left block. We have $\dot{\hat{p}} = \widehat{\dot{p}} = \hat{v}_O + \widehat{\omega \times p}$,
and with the Jacobi identity for skew matrices,
$\widehat{\omega \times p} = \hat{\omega}\hat{p} - \hat{p}\hat{\omega}$,

$$
\dot{\hat{p}}R + \hat{p}\hat{\omega}R = \big(\hat{v}_O + \hat{\omega}\hat{p} - \hat{p}\hat{\omega} + \hat{p}\hat{\omega}\big)R
  = \big(\hat{v}_O + \hat{\omega}\hat{p}\big)R.
$$

Therefore

$$
\frac{d}{dt}{}^AX_B = \begin{bmatrix} \hat{\omega} & 0 \\ \hat{v}_O & \hat{\omega}\end{bmatrix}
\begin{bmatrix} R & 0 \\ \hat{p}R & R\end{bmatrix} = (v\times)\,{}^AX_B,
$$

which is the first identity in (5) and at the same time the **definition** of the $v\times$ in
(6). Applying item 5 of the self-diagnosis ($\frac{d}{dt}A^{-1} = -A^{-1}\dot{A}A^{-1}$) to
$^BX_A = ({}^AX_B)^{-1}$ gives the second identity,

$$
\frac{d}{dt}{}^BX_A = -\,{}^BX_A\,(v\times)\,{}^AX_B\,{}^BX_A = -\,{}^BX_A\,(v\times),
$$

and transposing, with $^AX_B^{*} = ({}^BX_A)^\top$,

$$
\frac{d}{dt}{}^AX_B^{*} = \big(-{}^BX_A (v\times)\big)^\top = -(v\times)^\top\,{}^AX_B^{*} = (v\times^{*})\,{}^AX_B^{*},
$$

which is the third identity in (5) and simultaneously the claim $v\times^{*} = -(v\times)^\top$ of
(6). In components,
$-\begin{bmatrix}\hat{\omega} & 0\\ \hat{v}_O & \hat{\omega}\end{bmatrix}^\top
= -\begin{bmatrix}-\hat{\omega} & -\hat{v}_O\\ 0 & -\hat{\omega}\end{bmatrix}
= \begin{bmatrix}\hat{\omega} & \hat{v}_O\\ 0 & \hat{\omega}\end{bmatrix}$, agreeing with (6).

**Reading**: $v\times$ is the adjoint representation $\mathrm{ad}_v$ of $\mathfrak{se}(3)$ and
$v\times^{*}$ is its dual $\mathrm{ad}_v^{*}$ (the $\mathrm{Ad}$ and $\mathrm{Ad}^{*}$ of
`c1-twists-wrenches-adjoint` are the finite transforms; these two are their infinitesimal
versions). Spatial vector algebra is just that Lie-algebraic structure **written out in
coordinates**, which is why every result of C1 is reused here.

### R5 — spatial acceleration and the acceleration of a point

$v_O(t)$ is "the velocity of the body-fixed point that coincides with the coordinate origin at
each instant". The body-fixed point playing that role at time $t$ and at $t + \delta$ are
**different points**. So $\dot{v}_O$ is not the acceleration of any one point.

Call the point currently at the origin $P$ and follow that material point: its position is
$r_P(t)$ and its velocity $\dot{r}_P = v_O$ at the present instant. One time step later it has
left the origin, so

$$
a_{\text{classical}} = \ddot{r}_P = \frac{d}{dt}\big(v_O + \omega \times (r_P - 0)\big)\Big|_{r_P = 0} = \dot{v}_O + \omega \times v_O,
$$

which is (9). Conversely $a_\ell = \dot{v}_O$ differentiates "the velocity field at the origin",
and it is precisely that choice which lets us write (8) as a **linear map** — the only reason for
using spatial acceleration at all. With the classical acceleration one gets
$f = I a_{\text{classical}} + \text{(a different bias term)}$, and the bias term then mixes in the
choice of coordinates.

**Where the assumption breaks**: the two definitions differ by $\omega \times v_O$, so the
difference vanishes when (i) $\omega = 0$, (ii) $v_O = 0$ (the origin is instantaneously at rest),
or (iii) $\omega \parallel v_O$. If you test only with the origin at the centre of mass and the
body at rest, **the bug will not show up**. Condition 4 of the reproduction task targets exactly
this.

## Proof sketch

### R4 — $\dot{I} = (v\times^{*})I - I(v\times)$ and the bias force

**Hypotheses** H1: the body is rigid, so the spatial inertia $^BI$ seen in a body-fixed frame $B$
is **constant**. H2: frame $A$ is an inertial (fixed) frame. H3: $B$ moves relative to $A$ with
spatial velocity $v$ (in $A$ coordinates).
**Conclusions** C1: $\frac{d}{dt}{}^AI = (v\times^{*})\,{}^AI - {}^AI\,(v\times)$.
C2: $f = I a + (v\times^{*})Iv$, and the second term is orthogonal to $v$.

**Strategy**: write the inertia as $^AI = ({}^BX_A)^\top\,{}^BI\,({}^BX_A)$ and substitute nothing
but the differentiation rule (5). No differential geometry is needed — everything is already in (5).

1. **Congruence form.** By the transformation law of R2 together with (2),
   $^AI = {}^AX_B^{*}\,{}^BI\,{}^BX_A = ({}^BX_A)^\top\,{}^BI\,({}^BX_A)$, and $^BI$ is constant by H1.
2. **Differentiate.** By the product rule and the second identity of (5),
   $\frac{d}{dt}{}^BX_A = -{}^BX_A(v\times)$:
   $$
   \frac{d}{dt}{}^AI = \big(-{}^BX_A(v\times)\big)^\top {}^BI\,{}^BX_A + ({}^BX_A)^\top {}^BI\big(-{}^BX_A(v\times)\big).
   $$
3. **Collect.** The first term is $-(v\times)^\top\big(({}^BX_A)^\top {}^BI\,{}^BX_A\big) =
   (v\times^{*})\,{}^AI$ (the last equality being $v\times^{*} = -(v\times)^\top$ from (6)). The
   second is $-\,{}^AI\,(v\times)$. Adding them gives C1.
4. **Newton-Euler.** The spatial momentum is $h = Iv$, and in an inertial frame the spatial force
   is the time derivative of momentum (Newton's second law in $F^6$ — Featherstone 2010 Part 2 의 운동량 절):
   $$
   f = \dot{h} = \dot{I}v + I\dot{v} = (v\times^{*})Iv - I\underbrace{(v\times)v}_{=\,0} + Ia = Ia + (v\times^{*})Iv.
   $$
   $(v\times)v = 0$ is checked directly from (6): the blocks are $\hat{\omega}\omega = 0$ and
   $\hat{v}_O\omega + \hat{\omega}v_O = v_O \times \omega + \omega \times v_O = 0$.
5. **The bias force does no work.** $v^\top (v\times^{*})Iv = \big((v\times^{*})^\top v\big)^\top Iv
   = \big(-(v\times)v\big)^\top Iv = 0$, so it contributes nothing to the kinetic-energy budget —
   this is the precise content of the textbook statement that the Coriolis and centrifugal terms
   "do no work".

**Delete a hypothesis**: without H2 (inertial frame), step 4's $f = \dot{h}$ fails. Differentiating
components in a moving frame adds an extra adjoint term, and that term is exactly what appears in
the recursions of RNEA (`c2-rnea-inverse-dynamics`). Without H1 (rigidity), $^BI$ is not constant
and a $\dot{}^BI$ term survives from step 1 onward; that term is the extra contribution in
deformable-body and variable-mass dynamics.

Technical step omitted: that the derivative of momentum in $F^6$ is the spatial force is itself
Newton's second law lifted to 6-D. For a derivation see the momentum section of Featherstone 2010 Part 2, or the
momentum discussion in RBDA ch.2.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ one hour /
★★★ a day or more.

**P1 (derivation, ★★, R1·R2)** For a pure translation ($E = \mathbb{1}$, $p \ne 0$), expand the
transformation law (4) and show that the upper-left block of $^BI$ agrees exactly with the
parallel-axis theorem. Then redo **the same calculation with the wrong formula**
$({}^BX_A)^\top\,{}^AI\,{}^BX_A$ and write down which block goes wrong and how.
*Solution sketch*: with $^BX_A = \begin{bmatrix}\mathbb{1} & 0\\ -\hat{p} & \mathbb{1}\end{bmatrix}$
and $^AX_B = \begin{bmatrix}\mathbb{1} & 0\\ \hat{p} & \mathbb{1}\end{bmatrix}$, multiply blockwise
and compare against the centre of mass having moved to $c - p$. With the wrong formula the sign of
the off-diagonal blocks flips and $I$ becomes non-symmetric.

**P2 (derivation, ★★, R3)** Confirm that $v\times$ and $v\times^{*}$ are the $\mathrm{ad}_v$ and
$\mathrm{ad}_v^{*}$ of $\mathfrak{se}(3)$. Concretely, for $v_1, v_2 \in M^6$ show antisymmetry
$(v_1\times)v_2 = -(v_2\times)v_1$ and the Jacobi identity
$\big((v_1\times)v_2\big)\times = (v_1\times)(v_2\times) - (v_2\times)(v_1\times)$.
*Solution sketch*: expand blockwise and apply the three-dimensional Jacobi identity
$\widehat{a \times b} = \hat{a}\hat{b} - \hat{b}\hat{a}$ to each block. The crux is whether
$\hat{\omega}_1\hat{v}_2 - \hat{v}_2\hat{\omega}_1 + \hat{v}_1\hat{\omega}_2 - \hat{\omega}_2\hat{v}_1$
in the lower-left block collects into $\widehat{\omega_1 \times v_2 - \omega_2 \times v_1}$.

**P3 (proof, ★★★, R4)** Prove from (4) that the spatial inertia $I$ is symmetric positive
definite, and show that the flow (7) of R4 is a **symmetry-preserving flow**: if $I(0)$ is
symmetric then $I(t)$ is symmetric for all $t$.
*Strategy and key inequality*: positive definiteness follows from $v^\top I v = 2T \ge 0$ together
with the equality condition ($\omega = 0$ and $v_C = 0$). For preservation of symmetry, compute
$\frac{d}{dt}(I - I^\top)$ using (7), observe that it is a linear ODE in $(I - I^\top)$, and close
with uniqueness. (The expansion is withheld.)

**P4 (numerical, ★, R2·R4)** For a rigid body with $m = 2$, $c = (0.1, -0.2, 0.3)$ and
$\bar{I}_C = \mathrm{diag}(0.05, 0.08, 0.11)$, and for
$v = (0.3, -0.5, 0.9,\; 0.2, 0.4, -0.1)$, compute the $I$ of (4), the spatial momentum $h = Iv$,
and the bias force $(v\times^{*})Iv$.
*Answer* (tolerance $10^{-9}$):

$$
I = \begin{bmatrix}
 0.31 & 0.04 & -0.06 & 0 & -0.6 & -0.4\\
 0.04 & 0.28 & 0.12 & 0.6 & 0 & -0.2\\
 -0.06 & 0.12 & 0.21 & 0.4 & 0.2 & 0\\
 0 & 0.6 & 0.4 & 2 & 0 & 0\\
 -0.6 & 0 & 0.2 & 0 & 2 & 0\\
 -0.4 & -0.2 & 0 & 0 & 0 & 2
\end{bmatrix},
$$

$h = (-0.181,\; 0.12,\; 0.271,\; 0.46,\; 0.8,\; -0.22)$,
$(v\times^{*})Iv = (-0.2515,\; -0.2462,\; -0.0785,\; -0.61,\; 0.48,\; 0.47)$.
*Checks*: (a) $I = I^\top$ with all eigenvalues positive; (b)
$v^\top (v\times^{*})Iv = 0$ (error $< 10^{-15}$); (c) the lower three components of the linear
momentum agree with $m(v_O + \omega \times c)$.

**P5 (implementation, ★★, R1·R2·R3)** Implement `skew`, `crm` ($v\times$), `crf` ($v\times^{*}$),
`xform` ($^BX_A$), `xform_dual` ($^BX_A^{*}$) and `spatial_inertia`
($m, c, \bar{I}_C \mapsto I$) in numpy. Assemble them from the closed forms of (3) — **do not**
compute transposes or inverses numerically.
*Rubric*: (a) `xform_dual(E, p)` agrees with `inv(xform(E, p)).T` to within $10^{-14}$;
(b) `crf(v) == -crm(v).T` holds exactly (bitwise); (c) `crm(v) @ v` is zero for arbitrary $v$;
(d) composition $^CX_B\,{}^BX_A = {}^CX_A$ holds (check with three frames);
(e) the component-order convention is stated in the docstring.

**P6 (counterexample, ★★, R5)** Show by a **numerical counterexample** that the claim "the lower
three components of spatial acceleration are the acceleration of the body-fixed point at the
origin" is false. The counterexample must show **both** that (i) using that claim makes the torque
of (8) wrong and (ii) the error disappears when the origin is the centre of mass and the body is
at rest.
*Property checklist*: $\omega \ne 0$, $v_O \ne 0$, $\omega \not\parallel v_O$, origin $\ne$ centre
of mass. The counterexample is right if the difference between the two computations is exactly
$I\,(0; \omega \times v_O)$.

## Paper reading

**Two must-reads.** Both are tutorials and together run to under twenty pages, but the entire
notation of this module comes from them. Write a one-page note on each using the ten fixed
questions below (`lesson-standard.md` §5). Read in three passes and concentrate on questions
4, 7 and 9 in the third pass — in tutorial papers those are the items that blur fastest: what is
*not* guaranteed, and what it costs.

1. **Featherstone, "A Beginner's Guide to 6-D Vectors (Part 1)" (2010, IEEE RAM)** — role:
   `standard`. <https://doi.org/10.1109/MRA.2010.937853>
   Which sections and why: the one that sets up motion space and force space as **two different
   vector spaces**, and the one that introduces Plücker coordinates. R1 of this lesson is that
   section's requirement (invariance of power) written as an equation.
   Extra questions: (a) with which example does the author support the claim that "6-D vectors
   shorten the equations", and is that example fair? (b) where does the author's notation clash
   with the $^BX_A$ and $^BX_A^{*}$ of this lesson?
2. **Featherstone, "A Beginner's Guide to 6-D Vectors (Part 2)" (2010, IEEE RAM)** — role:
   `standard`. <https://doi.org/10.1109/MRA.2010.939560>
   Which sections and why: the ones that set up spatial inertia, the cross products and the
   differentiation rules, and the last one that connects them to dynamics algorithms. They
   correspond one-to-one with R2, R3 and R4 here, so read them **against** the derivations above.
   Extra questions: (a) do the author's $\times$ and $\times^{*}$ agree with (6) down to the sign,
   and if not, which convention differs? (b) where does the author warn about the difference
   between spatial and classical acceleration, and is the warning enough? (c) what would the RNEA
   recursion of the next lesson look like without this notation?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) independent and dependent variables and baselines — were the baselines tuned fairly?
(6) do the metrics match the claim; are variance and seeds reported? (7) what is missing for
reproduction? (8) if it were wrong, which assumption would you suspect first? (9) compute and
memory complexity, and real-time feasibility. (10) what would you change to go beyond it in a year?

> Neither paper is an experimental paper, so apply questions 5 and 6 to "the examples the author
> offers in support of the claims". Do not skip the questions: writing one line on why a question
> does not apply is part of the note.

## Reproduction task

**Tier R1 (numerical check).** Compute budget: one notebook CPU core, under one minute, numpy only
(`scipy.linalg.expm` is used only for the finite-difference comparison — you may implement it
yourself). Memory under 100 MB.

The functions written in P5 must satisfy **all four** of the following. Fix the random seed.

1. **Consistency of duality and the transforms** — for $10^4$ random $(E, p)$ and random
   $v \in M^6$, $f \in F^6$,
   $$
   \max\big|f^\top v - (\,{}^BX_A^{*}f)^\top({}^BX_A v)\,\big| < 10^{-12},\qquad
   \max\big\lVert {}^BX_A^{*} - ({}^BX_A)^{-\top} \big\rVert_\infty < 10^{-12}.
   $$
2. **Spatial inertia transform ≡ recomputation via the homogeneous transform** — for $10^4$ draws
   of random $m \in (0.1, 10)$, $c$ with $\lVert c\rVert < 1$ and random positive-definite
   $\bar{I}_C$: the $^BI_{\text{law}}$ obtained from the transformation law (4), and the
   $^BI_{\text{direct}}$ rebuilt from the assembly formula of (4) after first moving the mass
   properties ($c_B = E(c - p)$, $\bar{I}_{C,B} = E\bar{I}_C E^\top$), must satisfy
   $$
   \max \big\lVert {}^BI_{\text{law}} - {}^BI_{\text{direct}} \big\rVert_\infty < 10^{-10}, \qquad
   \max \big\lVert {}^BI_{\text{law}} - ({}^BI_{\text{law}})^\top \big\rVert_\infty < 10^{-12}.
   $$
   (This is the acceptance criterion the blueprint specifies. The point is that the two paths are
   **independent**: one is a $6\times6$ congruence, the other the $3\times3$ parallel-axis theorem.)
3. **The $\dot{I}$ identity (7)** — for fixed $I$ and fixed $v$, take central finite differences
   ($h = 10^{-6}$) of $J(t) = \big(\exp(-(v\times)t)\big)^\top I \exp(-(v\times)t)$ and require
   $$
   \big\lVert \tfrac{J(h) - J(-h)}{2h} - \big((v\times^{*})I - I(v\times)\big) \big\rVert_\infty < 10^{-8}.
   $$
   Then verify the no-work property of the bias force,
   $\big|v^\top (v\times^{*})Iv\big| < 10^{-14}$, on $10^4$ random draws.
4. **Isolate the difference of R5 numerically** — pick one state with $\omega \ne 0$, $v_O \ne 0$,
   $\omega \not\parallel v_O$ and $c \ne 0$, compute the torque of (8) twice — once with
   $a = \dot{v}$, once with the lower components replaced by
   $a_{\text{classical}} = \dot{v}_O + \omega \times v_O$ — and show that the difference satisfies
   $$
   \big\lVert f_{\text{wrong}} - f_{\text{right}} - I\,(0;\, \omega \times v_O) \big\rVert_\infty < 10^{-12}
   $$
   while $\lVert f_{\text{wrong}} - f_{\text{right}}\rVert_\infty > 10^{-2}$ (that is, the error is
   genuinely **large**). Then set $c = 0$ and $v_O = 0$ and confirm that the difference vanishes
   below $10^{-14}$.

**Input data**: no external data needed. Every input is drawn with a fixed seed
(`np.random.default_rng(0)`). The positive-definite $\bar{I}_C$ of condition 2 must use only
**physically realisable** values, satisfying the triangle inequalities
($I_{xx} + I_{yy} \ge I_{zz}$ and so on) — otherwise condition 2 still passes but the physical
consistency constraint of `c2-dynamics-derivatives-sysid` will reject them.

**Baselines** (at least one):
- First choice: a second independent path implemented yourself (condition 2 already has this shape).
- Second choice: compute the same transform with `pinocchio`'s `pin.Inertia` / `pin.SE3.act` and
  agree to within $10^{-10}$. Mind that its component order is linear first — write the permutation
  matrix out explicitly.
- Reference: Featherstone's published implementation (<https://royfeatherstone.org/spatial/>) lets
  you compare numbers against `Xtrans`, `mcI`, `crm` and `crf` (Octave).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| Only the second equation of condition 1 fails | $^BX_A^{*}$ written as $({}^BX_A)^\top$ (the inverse was dropped) | Set $E = \mathbb{1}$, $p \ne 0$ and look at the **sign** of the moment-transfer term |
| Condition 2 passes only for pure rotations | A similarity transform $X^{-1}IX$ was used instead of a congruence | Fix $p \ne 0$, $E = \mathbb{1}$ and look at $\lVert I - I^\top\rVert$ |
| Condition 2 stalls at the $10^{-6}$ level | $\bar{I}_C$ nearly singular, or $m$ below $10^{-3}$ — a conditioning problem | Print the condition numbers of $m$ and $\bar{I}_C$ and narrow the sampling range |
| Condition 3 has the opposite sign | $J(t)$ written with $\exp(+(v\times)t)$ ($^AX_B$ confused with $^BX_A$) | Check that $J(0) = I$ and that $J$ moves in the **decreasing** direction |
| Condition 4 gives a difference of zero | The test state has $v_O = 0$, or $\omega \parallel v_O$, or $c = 0$ | Assert all three conditions **explicitly** in the unit test |
| Everything breaks after swapping the component order | The swap must enter $M^6$ and $F^6$ with the **same** permutation | Introduce the block-swap matrix $\Sigma$ explicitly and check $\Sigma^\top = \Sigma^{-1} = \Sigma$ |

## Open problems

- **(open problem) How the choice of coordinates affects numerical conditioning** — the condition
  number of the mass matrix varies by tens of times depending on which frame the same mechanism is
  expressed in, and for long chains or systems with large mass ratios (a lightweight arm with a
  heavy end-effector, say) this dominates the accuracy of integrators and contact solvers. Spatial
  vector algebra gives no answer to "which frame is numerically best" — there is no theory that
  **predicts** the conditioning from the structure of the mechanism. Current approaches:
  preconditioning the mass matrix, and $O(n)$ solvers that exploit the branch structure
  ([Featherstone 1983](https://doi.org/10.1177/027836498300200102); divide and conquer,
  [Featherstone 1999](https://doi.org/10.1177/02783649922066619)). What is missing: a procedure
  that chooses frames and coordinates automatically against a conditioning criterion.
- **(open problem) How friendly 6-D algebra is to automatic differentiation** — spatial vector
  algebra is optimal for a human writing recursions by hand, but because $v\times$ and
  $v\times^{*}$ obey different transformation rules, the computational graph produces redundant work
  when **derivatives are obtained automatically**. That is why analytical derivatives are an order
  of magnitude faster than automatic differentiation
  ([Carpentier & Mansard 2018](https://doi.org/10.15607/RSS.2018.XIV.038)). What is still missing:
  a representation in which a compiler understands the dual structure well enough that automatic
  differentiation reaches the same cost. The question returns in
  `c2-dynamics-derivatives-sysid`.
- **(open problem) Extension to systems that are not chains** — the algorithmic gains of spatial
  vector algebra (the $O(n)$ and $O(n^2)$ of the next two lessons) depend on a **tree structure**.
  Once closed loops or contacts create cycles in the graph, multipliers or null-space projections
  enter and the cost returns to something close to $O(n^3)$ (`c2-constrained-dynamics`). Current
  approaches: divide-and-conquer $O(\log n)$ parallelisation, and convex relaxation of contact
  ([Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751)). What is missing: an exact solver
  that is linear in the number of contacts.

## Concept check

Run `rc quiz c2-spatial-vector-algebra`. The quiz is for **concept checking only**; the real work
is the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: the transformation rule for force vectors; why spatial inertia moves by a
congruence rather than a similarity transform; that spatial acceleration is not the acceleration
of a body-fixed point; the power delivered by the bias force; and which hypotheses the identity
$\dot{I} = (v\times^{*})I - I(v\times)$ actually uses.

## How to study this stage

1. **Start with the self-diagnosis (20 min)** — solve the five items above first. If items 2 and 5
   stop you, the derivations here will be hard to follow, so read C1 and your linear algebra
   first. You can make progress even if the others stop you.
2. **Nail down the component order on paper (20 min)** — write out $(\omega; v_O)$ and
   $(n_O; f_\ell)$, write the four matrices of (3) and (6) by hand, and pin them to the wall. Most
   bugs in this module are order and sign.
3. **Derive R1 backwards (40 min)** — do **not** memorise the $^BX_A$ of (3); assemble it from the
   velocity relation between two points of a rigid body. Then pull $^BX_A^{*}$ out of nothing but
   the invariance of power, and only at the end compare against the moment-transfer formula to
   check that the physics agrees. Done in that order, "why two kinds of transform" stays with you.
4. **Reconstruct R4 from a blank page (60 min)** — remember only the second identity of (5) and
   rewrite steps 1–4 of the proof sketch. Where you get stuck is almost always the transpose in
   step 3. Then compare the same result in Featherstone Part 2 **down to the signs**.
5. **Build a wrong implementation first (50 min)** — when writing P5, deliberately produce three
   variants: (a) $X^{*} = X^\top$, (b) the similarity transform, (c) the classical acceleration,
   and watch which condition of the reproduction task breaks and how. A test written without
   having seen it break catches nothing in the next lesson.
6. **Finish the reproduction task (75 min)** — write the four conditions as four test functions.
   For the finite difference of condition 3, sweep $h$ from $10^{-4}$ to $10^{-8}$ and plot the
   error curve. You should see a **V shape** with its minimum near $10^{-6}$ and the error growing
   again below it (truncation error versus round-off).
7. **Read the two papers against the notation (120 min)** — read Part 1 then Part 2, and transcribe
   each paper's notation into the symbol table of this lesson. Write the one-page notes: you
   **will** come back to them when writing RNEA, CRBA and ABA.
8. **End with what cannot be done (20 min)** — pick one of the open problems and write a paragraph
   on why it is still open. You already touched the conditioning problem with your hands, in the
   third failure mode of condition 2 of the reproduction task.

**Passing bar**: you can write (3), (4) and (6) from a blank page, you can state the proof of (7)
in four steps, you have code that passes all four conditions of the reproduction task, and you
have one-page notes on both papers.
