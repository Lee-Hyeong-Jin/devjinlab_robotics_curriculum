---
id: r0-manifolds-lie-groups
lang: en
title: An introduction to manifolds and matrix Lie groups
summary: >-
  Define smooth manifolds and tangent spaces, treat matrix Lie groups as objects that are both a
  group and a manifold, and see why the matrix exponential is the bridge from the Lie algebra to
  the group. A bridge lesson that teaches the language C1 uses.
objectives:
  - Define smooth manifolds and tangent spaces and state when a constraint set is a manifold.
  - State the definition of a matrix Lie group and confirm that SO(3) and SE(3) are examples.
  - Define the Lie algebra as the tangent space at the identity and derive that so(3) is the skew-symmetric matrices.
  - Show that the matrix exponential maps the Lie algebra into the group and state its properties.
  - Explain why "differentiation" and "addition" need care on a manifold.
tags: [differential-geometry, lie-groups, manifolds, research]
---

# An introduction to manifolds and matrix Lie groups

## Setup and notation

| Symbol | Meaning |
|---|---|
| $\mathcal{M}$ | a smooth manifold |
| $T_p\mathcal{M}$ | the tangent space at $p$ |
| $G$ | a matrix Lie group (a group of matrices that is also a manifold) |
| $\mathfrak{g} = T_I G$ | the Lie algebra of $G$ (the tangent space at the identity) |
| $\exp: \mathfrak{g} \to G$ | the matrix exponential |
| $h(x)=0$ | the constraint defining a manifold |

**Where this lesson sits**: it is a **bridge**. All of C1, starting from
`c1-so3-se3-exponential`, is written in the language learned here, and treats Rodrigues' formula,
surjectivity and the Jacobians **at the level of proof**. The aim here is to make those derivations
**readable**, and the same results are not proved twice.

Assumed: `f0-linear-algebra`, `f0-calculus-multivariable` (the implicit function theorem) and
`r0-estimation-theory`.

## Key results

- **R1 (when a constraint defines a manifold) [D3]** — if $h: \mathbb{R}^n \to \mathbb{R}^m$ is
  $C^1$ and $\mathrm{rank}\,Dh(x) = m$ (full rank) at every point of
  $\mathcal{M} = \{x : h(x)=0\}$, then $\mathcal{M}$ is a smooth manifold of dimension $n-m$ and

$$
T_x\mathcal{M} = \ker Dh(x) = \{v : Dh(x)\,v = 0\} . \tag{1}
$$

  (A consequence of the implicit function theorem.)
- **R2 (matrix Lie groups and Lie algebras) [D2]** —
  $SO(3) = \{R : R^\top R=I,\ \det R=1\}$ satisfies the condition of R1 and is a 3-dimensional
  manifold, and the tangent space at the identity is

$$
\mathfrak{so}(3) = T_I SO(3) = \{\Omega : \Omega^\top = -\Omega\} \tag{2}
$$

  — the **skew-symmetric** matrices. Its dimension 3 matches the degrees of freedom of rotation.
- **R3 (the exponential is the bridge) [D2]** — for $\Omega \in \mathfrak{g}$ we have
  $\exp(\Omega) \in G$, and $t \mapsto \exp(\Omega t)$ is a curve in $G$ through $I$ whose velocity
  is $\Omega$:

$$
\left.\frac{d}{dt}\exp(\Omega t)\right|_{t=0} = \Omega . \tag{3}
$$

  The exponential map is therefore the natural map **turning a tangent vector into a group element**.
- **R4 (two properties the group structure gives) [D2]** — (a)
  $\exp(\Omega)^{-1} = \exp(-\Omega)$; (b) exponentials of the same $\Omega$ commute, with
  $\exp(\Omega s)\exp(\Omega t) = \exp(\Omega(s+t))$. But **in general
  $\exp(A)\exp(B) \ne \exp(A+B)$**, and measuring that gap is the BCH expansion of C1.
- **R5 (there is no addition on a manifold) [D1]** — $\mathcal{M}$ is not a vector space, so there
  is no guarantee that $p + v$ lies in $\mathcal{M}$. Hence (a) points are group elements,
  (b) increments are tangent vectors, and (c) they combine as $p\,\exp(v)$. All estimation and
  optimization in C1 and C5 rests on that convention.

## Derivation

### R2 — why $\mathfrak{so}(3)$ is skew-symmetric

Let $R(t)$ be a curve in $SO(3)$ through $R(0)=I$. Differentiating the constraint $R^\top R = I$,

$$
\dot{R}^\top R + R^\top\dot{R} = 0 .
$$

At $t=0$ we have $R=I$, so $\dot{R}(0)^\top + \dot{R}(0) = 0$: $\dot{R}(0)$ is **skew-symmetric**.
Conversely, for any skew-symmetric $\Omega$ the curve $R(t) = \exp(\Omega t)$ lies in $SO(3)$ by
R3, so the tangent space is exactly the set of skew-symmetric matrices — (2).

**Checking the dimension**: a $3\times3$ skew-symmetric matrix has zero diagonal and three
independent entries above it, so **dimension 3**. R1 gives the same count: $R^\top R=I$ is an
equality of symmetric matrices, i.e. 6 equations ($3\cdot4/2$), and $9-6=3$. The two agree.

**Why $\det R = 1$ does not reduce the dimension**: under $R^\top R=I$ the determinant can only be
$\pm1$, so it is a **discrete** condition that selects a connected component rather than changing
the dimension. $O(3)$ and $SO(3)$ therefore have the same dimension, with $SO(3)$ the component
containing $I$.

### R3 — why the exponential stays inside the group

For skew-symmetric $\Omega$, show directly that $\exp(\Omega) \in SO(3)$:

$$
\exp(\Omega)^\top\exp(\Omega) = \exp(\Omega^\top)\exp(\Omega) = \exp(-\Omega)\exp(\Omega) = \exp(0) = I ,
$$

using (a) $\exp(A)^\top = \exp(A^\top)$ (transpose the series term by term),
(b) $\Omega^\top = -\Omega$, and (c) that **exponentials of the same matrix commute**, so
$\exp(-\Omega)\exp(\Omega) = \exp(0)$. For the determinant,
$\det\exp(\Omega) = e^{\mathrm{tr}\,\Omega} = e^0 = 1$ (skew-symmetry gives a zero diagonal and
hence zero trace), so $\det=1$ holds too.

Equation (3) follows immediately by differentiating the series
$\exp(\Omega t) = I + \Omega t + O(t^2)$.

**Where the assumption breaks**: the condition **"the same matrix"** in (c) is decisive. Replacing
$\exp(A)\exp(B)$ by $\exp(A+B)$ requires $AB=BA$. Rotations about different axes do not commute, so
the substitution is unavailable, and the difference is measured by the BCH expansion
(`c1-lie-group-derivatives` in C1).

## Proof sketch

### R1 — when a constraint set is a manifold

**Hypotheses** H1: $h \in C^1$. H2: $Dh$ has full rank $m$ at every point of $\mathcal{M}$.
**Conclusion** C: $\mathcal{M}$ is a smooth manifold of dimension $n-m$ with tangent space (1).

**Strategy**: build a local parameterisation with the implicit function theorem. The definition of
a manifold is precisely "locally it looks like $\mathbb{R}^{n-m}$", so constructing that
parameterisation finishes the job.

1. At $x_0 \in \mathcal{M}$, $Dh(x_0)$ has rank $m$, so the coordinates can be reordered so that
   in $Dh = [D_1h \;|\; D_2h]$ the block $D_2h \in \mathbb{R}^{m\times m}$ is invertible.
2. Implicit function theorem: near $x_0$ there is a $C^1$ function $\varphi$ with
   $x_2 = \varphi(x_1)$ and $h(x_1, \varphi(x_1)) = 0$.
3. So locally $\mathcal{M}$ is the graph of $x_1 \in \mathbb{R}^{n-m}$, and that graph map is a
   local parameterisation (a chart) — satisfying the definition of a manifold, of dimension $n-m$.
4. **Tangent space**: differentiating $h(x(t))=0$ along a curve in $\mathcal{M}$ gives
   $Dh(x)\dot{x} = 0$, so every tangent vector lies in $\ker Dh$. Both have dimension $n-m$, so
   they coincide — (1).

**Delete a hypothesis**: at points where H2 (full rank) fails, $\mathcal{M}$ **may not be smooth**.
For example the zero set of $h(x,y)=x^2-y^2$ is two lines crossing at the origin, which is not a
manifold, and there $Dh = (2x, -2y) = (0,0)$ has rank 0. **The rank condition is substance, not formality.**

**Use in robotics**: the configuration space of a closed-chain mechanism (a four-bar linkage) is
exactly such a constraint manifold, and the points where the rank drops are **singular
configurations** (constrained dynamics in C2, configuration space in C6). The rank condition of R1
is therefore the same thing as the practical notion of a singularity.

## Problem set

★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Derive the Lie algebra $\mathfrak{se}(3)$ of $SE(3)$ by the method of
R2 (differentiate the constraints on a homogeneous transform). Confirm its dimension is 6 in two ways.
*Solution sketch*: for $T = \begin{bmatrix}R & p\\ 0 & 1\end{bmatrix}$, differentiate $R^\top R=I$
and the constancy of the last row. The dimension is (a) skew-symmetric 3 + translation 3, or
(b) $16 - 6 - 4$ (the fixed last row) $= 6$.

**P2 (derivation, ★★, R3·R4)** Confirm from the series that $\exp(A)\exp(B) = \exp(A+B)$ holds in
general only when $AB=BA$, and build a counterexample from a $2\times2$ skew-symmetric and a
diagonal matrix.
*Solution sketch*: comparing second-order terms, the difference between $\tfrac12(AB+BA)$ and
$\tfrac12(A+B)^2$ leaves $\tfrac12[A,B]$. A non-zero commutator breaks it.

**P3 (proof, ★★★, R1)** Write the proof of R1 with no gaps, and justify "the dimensions agree so
they coincide" in step 4 (why inclusion alone is not enough).
*Solution sketch*: differentiation shows the set of tangent vectors is contained in $\ker Dh$; to
show equality one must **construct** $n-m$ independent tangent vectors from the parameterisation of step 3.

**P4 (numerical, ★, R2·R3)** For
$\Omega = \begin{psmallmatrix}0&-1&0\\1&0&0\\0&0&0\end{psmallmatrix}$, check (a) that $\Omega$ is
skew-symmetric, (b) compute $\exp(\Omega\cdot\pi/2)$, and (c) verify $\det$ and $R^\top R$.
*Answer*: (a) yes; (b) a 90° rotation about $z$,
$\begin{psmallmatrix}0&-1&0\\1&0&0\\0&0&1\end{psmallmatrix}$; (c) $\det=1$ and $R^\top R=I$.
Tolerance $10^{-12}$.

**P5 (implementation, ★★, R1·R3)** Write (a) the sphere $\lVert x\rVert=1$ and (b) the closed-loop
constraint of a four-bar linkage as $h(x)=0$, and at random points compute the numerical rank of
$Dh$ and a basis of $\ker Dh$. Confirm that stepping along that basis violates the constraint by
$O(\epsilon^2)$.
*Rubric*: (a) use an analytic or finite-difference $Dh$ and state the rank threshold; (b) show the
constraint violation of a tangent step is second order, by a log-log slope of 2; (c) contrast with
a normal-direction step whose violation is first order; (d) find and report a singular
configuration of the four-bar linkage where the rank drops.

**P6 (counterexample, ★★, R1·R5)** Give (a) a constraint set that is not a manifold because the
rank condition fails and (b) an example where "addition" leaves the set on a manifold. Explain why
$p\exp(v)$ is safe in (b).
*Property checklist*: (a) the origin of $x^2-y^2=0$; (b) $R + \Omega$ is not a rotation matrix
($R^\top R \ne I$). Since $p\exp(v)$ is a group operation, its result is necessarily in the group.

## Paper reading

**The textbook exception applies** (lesson standard §5). Read one textbook chapter and one paper,
and write a one-page note for each (fixed questions 1, 3, 4 and 8).

1. **Barfoot, ch.7** — questions: (a) write how the author connects the view of a rotation as a
   "constrained matrix" with the view of it as a "Lie group". (b) make a list of the notations
   introduced in this chapter that C1 will use.
2. **Solà, Deray & Atchuthan, "A micro Lie theory for state estimation in robotics" (2018), up to
   §2** — <https://arxiv.org/abs/1812.01537>
   Questions: (a) write the **motivation** the authors give for introducing $\oplus$ and $\ominus$,
   connecting it to R5. (b) note three things in the article you do **not** yet understand — after
   finishing C1, come back and the answers will be there.

## Reproduction task

**Tier R1 (numerical check).** Budget: under one minute on a laptop CPU, numpy/scipy only. All four
conditions must pass.

1. **The exponential stays in the group**: for 1000 random skew-symmetric $\Omega$,
   $R=\exp(\Omega)$ satisfies $\lVert R^\top R - I\rVert_F < 10^{-12}$ and
   $|\det R - 1| < 10^{-12}$.
2. **Numerical check of (3)**: a central finite difference of
   $\frac{d}{dt}\exp(\Omega t)|_{t=0}$ agrees with $\Omega$ to within $10^{-7}$.
3. **The tangent space is the null space of the constraint**: for the sphere and the four-bar
   linkage, (a) compute a basis of $\ker Dh$; (b) show the constraint violation of a step
   $\epsilon$ along it is $O(\epsilon^2)$ (log-log slope $2\pm0.2$); (c) show a normal-direction
   step violates by $O(\epsilon)$ (slope $1\pm0.2$).
4. **Where addition fails**: for a random $R \in SO(3)$ and small skew-symmetric $\Omega$,
   contrast (a) $\lVert(R+\Omega)^\top(R+\Omega)-I\rVert_F$ growing as
   $O(\lVert\Omega\rVert)$ with (b) $R\exp(\Omega)$ staying in the group to within $10^{-12}$.

**Baseline**: `scipy.linalg.expm` and (if you implemented Rodrigues' formula directly) your result
must agree to within $10^{-12}$.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| condition 1 fails for large $\lVert\Omega\rVert$ | not the accuracy limit of `expm` but $\Omega$ failing to be skew-symmetric | print $\lVert\Omega+\Omega^\top\rVert$ |
| the error in condition 2 is large | the finite-difference step is too small or too large | set $h\sim\epsilon^{1/3}$ (`f0-python-numerics-git`) |
| the slope in condition 3 is not 2 | the tangent basis is not orthonormal, or the rank verdict is wrong | obtain the basis by SVD and print the threshold |
| the four-bar linkage always has full rank | you never passed through a singular configuration | sweep the link angles and plot the smallest singular value of $Dh$ |

## Open problems

- **(Open) Numerical treatment near singular configurations** — where the rank condition fails
  **marginally**, tangent-space computation is unstable. How to pass safely through singular
  configurations of closed-chain mechanisms and contact constraints is unsettled (connecting to
  constrained dynamics in C2).
- **(Open) Combining manifold constraints with learning** — there are several ways to constrain a
  network output to a manifold (projection, parameterisation, regularisation), and their effects on
  expressiveness and training stability have not been compared (connecting to
  `c7-learned-correspondence-slam`).
- **(Open) Non-smooth constraint sets** — a configuration space with contact and collision is not a
  manifold but a **set with boundary**. The theory of differentiation and optimization over such
  sets is less settled than the smooth case (the planning theory of C6).

## Concept check

Run `rc quiz r0-manifolds-lie-groups` (add `--lang en` for the English text). It is for concept
checking only.

The four items cover: the dimension of a constraint manifold; what $\mathfrak{so}(3)$ consists of;
whether $\exp(A)\exp(B) = \exp(A+B)$ in general; and the correct way to apply a small increment to
a rotation.

## How to study this stage

1. **Do the differentiation of R2 by hand (30 min)** — the three lines from $R^\top R=I$ to
   skew-symmetry are the heart of this lesson. Use the same trick for $\mathfrak{se}(3)$ in P1.
2. **Count the dimension two ways (30 min)** — by counting a basis, and by the $n-m$ formula of R1.
   Checking that the two agree is a habit used later when counting the dimension of a gauge freedom.
3. **See "staying in the group" numerically (60 min)** — do conditions 1 and 4 of the reproduction
   task together. The contrast between $R+\Omega$ leaving the group and $R\exp(\Omega)$ staying in
   it is the design reason behind all of C1 and C5.
4. **Compute a tangent space as a null space (70 min)** — condition 3. The sphere is intuitive and
   the four-bar linkage is a real robotics constraint. Seeing the rank drop at a singular
   configuration shows why the hypothesis of R1 is substantive.
5. **Leave BCH as "not yet known" (20 min)** — in R4, only confirm that
   $\exp(A)\exp(B)\ne\exp(A+B)$ and move on. Measuring the gap is the job of
   `c1-lie-group-derivatives`. **Being greedy here makes the bridge duplicate the core.**
6. **Write down the "three things I do not understand" from the paper (100 min)** — read Solà et al.
   up to §2 and record what you did not follow. Revisiting that list after C1 makes the relation
   between the two lessons clear.

**Passing bar**: you can derive $\mathfrak{so}(3)$ from $R^\top R=I$, can state the rank condition
and tangent-space formula of R1, and have code meeting all four acceptance conditions plus both notes.
