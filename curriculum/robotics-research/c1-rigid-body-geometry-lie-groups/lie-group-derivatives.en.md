---
id: c1-lie-group-derivatives
lang: en
title: Derivatives on Lie groups - the left and right Jacobians
summary: >-
  Derive the differential of the exponential map from Duhamel's formula to obtain closed forms for
  the left and right Jacobians, and use the BCH expansion to fix the order of the linearisation
  error of a group product. Ends at invariant distances and the Fréchet mean, which is where it
  becomes clear why estimation must use these Jacobians rather than Euclidean addition.
objectives:
  - Derive Duhamel's (Dyson's) formula for the differential of the exponential map and write the integral form of the left and right Jacobians.
  - Integrate that form to get the closed expressions for J_l and J_r and their small-angle series.
  - Prove that J_l(phi) = Exp(phi) J_r(phi) and J_l(phi) = J_r(-phi).
  - Show with the BCH expansion that the first-order term of Log(Exp(phi)Exp(delta)) is J_r inverse.
  - Define invariant distances and the Fréchet mean, and compute the mean by Riemannian gradient descent.
tags: [lie-groups, so3, jacobian, bch, frechet-mean, research]
---

# Derivatives on Lie groups - the left and right Jacobians

## Setup and notation

The notation of the previous two lessons (`c1-so3-se3-exponential`, `c1-twists-wrenches-adjoint`)
carries over. Additional symbols:

| Symbol | Meaning |
|---|---|
| $\mathrm{Exp}(\phi) := \exp(\hat{\phi})$ | the exponential map taking a vector; $\mathrm{Log}$ is its inverse |
| $R \oplus \delta := R\,\mathrm{Exp}(\delta)$ | a **right** increment: a perturbation in the body frame |
| $\delta \oplus R := \mathrm{Exp}(\delta)\,R$ | a **left** increment: a perturbation in the reference frame |
| $R_2 \ominus R_1 := \mathrm{Log}(R_1^{-1}R_2)$ | right difference; $\ominus$ inverts $\oplus$ |
| $J_l(\phi),\ J_r(\phi) \in \mathbb{R}^{3\times3}$ | the left and right Jacobians |
| $\theta = \lVert\phi\rVert$, $\hat{u} = \hat{\phi}/\theta$ | angle and unit axis |

**Why this lesson exists**: $SO(3)$ is not a vector space, so $R + \delta$ is not a rotation.
Estimation and optimization therefore use $R \oplus \delta$ — and then "the derivative with
respect to $\delta$" differs from the Euclidean derivative. The left and right Jacobians are
exactly what captures that difference, and getting them wrong makes covariances silently wrong.

## Key results

- **R1 (Duhamel's formula and the integral form) [D3]** — for $A(t) = \hat{\phi} + t\hat{\delta}$,

$$
\left.\frac{d}{dt}e^{A(t)}\right|_{t=0} = \int_0^1 e^{\alpha\hat{\phi}}\,\hat{\delta}\,e^{(1-\alpha)\hat{\phi}}\,d\alpha,
\tag{1}
$$

  from which

$$
J_l(\phi) = \int_0^1 \mathrm{Exp}(\alpha\phi)\,d\alpha, \qquad
J_r(\phi) = \int_0^1 \mathrm{Exp}(-\alpha\phi)\,d\alpha. \tag{2}
$$

- **R2 (closed forms) [D2]** — integrating (2),

$$
J_l(\phi) = I + \frac{1-\cos\theta}{\theta^2}\hat{\phi} + \frac{\theta-\sin\theta}{\theta^3}\hat{\phi}^2,
\qquad J_r(\phi) = J_l(-\phi). \tag{3}
$$

  The small-angle series are $J_l \approx I + \tfrac12\hat{\phi} + \tfrac16\hat{\phi}^2$ and
  $J_r \approx I - \tfrac12\hat{\phi} + \tfrac16\hat{\phi}^2$.
- **R3 (left-right relation) [D3]** — with $R = \mathrm{Exp}(\phi)$,

$$
J_l(\phi) = R\,J_r(\phi), \qquad J_l(\phi) = J_r(-\phi) = J_r(\phi)^\top. \tag{4}
$$

- **R4 (the first BCH term and the linearisation error) [D2]** — for small $\lVert\delta\rVert$,

$$
\mathrm{Log}\big(\mathrm{Exp}(\phi)\,\mathrm{Exp}(\delta)\big)
= \phi + J_r^{-1}(\phi)\,\delta + O(\lVert\delta\rVert^2), \tag{5}
$$

  with $J_r^{-1}(\phi) = I + \tfrac12\hat{\phi} + \tfrac1{12}\hat{\phi}^2 + O(\theta^4)$.
  The closed form is in Barfoot ch.7.1 and in Forster et al. **[D0]** — do not memorise its signs;
  verifying it numerically is this lesson's reproduction task.
- **R5 (invariant distance and the Fréchet mean) [D2]** —
  $d(R_1,R_2) = \lVert\mathrm{Log}(R_1^\top R_2)\rVert$ is bi-invariant on $SO(3)$ and relates to
  the Frobenius distance by

$$
\lVert R_1 - R_2\rVert_F = 2\sqrt{2}\,\big|\sin(\theta/2)\big|, \qquad \theta = d(R_1,R_2). \tag{6}
$$

  The geodesic (Fréchet) mean $\bar{R} = \arg\min_R \sum_i d^2(R, R_i)$ is computed by Riemannian
  gradient descent

$$
\bar{R} \leftarrow \bar{R}\,\mathrm{Exp}\!\left(\frac{1}{N}\sum_i \mathrm{Log}(\bar{R}^\top R_i)\right)
\tag{7}
$$

  and is unique when the samples lie in a ball of radius $\pi/2$ **[D0]** (Karcher's condition).

## Derivation

### R1 — Duhamel's formula

Set $F(t,s) := e^{sA(t)}$ and write its ODE in $s$: $\partial_s F = A F$ with $F(t,0)=I$.
Differentiate both sides in $t$ and write $G := \partial_t F$:

$$
\partial_s G = A G + \dot{A}F, \qquad G(t,0) = 0 .
$$

This is an inhomogeneous linear ODE for $G$. Using the homogeneous solution $e^{sA}$ as the
integrating factor (Duhamel's principle),

$$
G(t,s) = \int_0^s e^{(s-\alpha)A}\,\dot{A}\,e^{\alpha A}\,d\alpha .
$$

At $s=1$, $t=0$ we have $A = \hat{\phi}$ and $\dot{A} = \hat{\delta}$, which is (1). Substituting
$\alpha \to 1-\alpha$ shows that the form with the two exponentials swapped is the same expression.

**The one line that gives (2)**: multiply (1) on the right by $e^{-\hat{\phi}}$ and use the adjoint
identity $e^{\alpha\hat{\phi}}\hat{\delta}e^{-\alpha\hat{\phi}} = \widehat{\mathrm{Exp}(\alpha\phi)\delta}$
(R1 of the previous lesson):

$$
\left.\frac{d}{dt}\mathrm{Exp}(\phi + t\delta)\right|_{t=0}\mathrm{Exp}(-\phi)
= \widehat{\left(\int_0^1 \mathrm{Exp}(\alpha\phi)\,d\alpha\right)\delta},
$$

so the derivative seen as a **left** increment is $J_l(\phi)\delta$. Multiplying on the left
instead runs the same computation and yields $J_r$. In $\oplus$ notation this is the familiar form:

$$
\mathrm{Exp}(\phi + \delta) \approx \mathrm{Exp}(\phi)\,\mathrm{Exp}\big(J_r(\phi)\delta\big)
\approx \mathrm{Exp}\big(J_l(\phi)\delta\big)\,\mathrm{Exp}(\phi). \tag{8}
$$

### R2 — closed forms

Substitute Rodrigues' formula into (2) and integrate in $\alpha$. Since $\hat{\phi} = \theta\hat{u}$,

$$
J_l(\phi) = \int_0^1\! \Big(I + \sin(\alpha\theta)\hat{u} + \big(1-\cos(\alpha\theta)\big)\hat{u}^2\Big) d\alpha
= I + \frac{1-\cos\theta}{\theta}\hat{u} + \Big(1 - \frac{\sin\theta}{\theta}\Big)\hat{u}^2 .
$$

Converting back with $\hat{u} = \hat{\phi}/\theta$ and $\hat{u}^2 = \hat{\phi}^2/\theta^2$ gives
(3). The small-angle limits of the two coefficients are
$\frac{1-\cos\theta}{\theta^2}\to\frac12$ and $\frac{\theta-\sin\theta}{\theta^3}\to\frac16$,
which gives the series.

**Getting the series for $J_r^{-1}$ directly**: multiplying
$J_r \approx I - \frac12 X + \frac16 X^2$ (with $X := \hat{\phi}$) by
$J_r^{-1} = I + \frac12 X + cX^2$,

$$
\Big(I - \tfrac12 X + \tfrac16 X^2\Big)\Big(I + \tfrac12 X + cX^2\Big)
= I + \big(c - \tfrac14 + \tfrac16\big)X^2 + O(X^3),
$$

so $c = \frac1{12}$. That single line gives the series in R4.

**Where the assumptions break**: (3) is usable only for $\theta>0$, and both coefficients are 0/0
as $\theta\to0$ — implementations switch to the series below about $\theta \lesssim 10^{-4}$. The
nastier case is the closed form of $J_r^{-1}$, whose denominator contains $\sin\theta$ and which
therefore **diverges** as $\theta \to \pi$: the inverse Jacobian exists only for $\theta<\pi$.
That is the mathematical reason a large rotational perturbation cannot be linearised in one step.

### R5 — invariant distance and (6)

$\lVert R_1 - R_2\rVert_F^2 = \operatorname{tr}\big((R_1-R_2)^\top(R_1-R_2)\big)
= 6 - 2\operatorname{tr}(R_1^\top R_2)$, and since the rotation angle of $R_1^\top R_2$ is
$\theta$, we have $\operatorname{tr}(R_1^\top R_2) = 1 + 2\cos\theta$ (R3 of the first lesson).
Substituting,

$$
\lVert R_1 - R_2\rVert_F^2 = 6 - 2(1+2\cos\theta) = 4(1-\cos\theta) = 8\sin^2(\theta/2),
$$

which is (6). The two distances nearly agree at small angles
($2\sqrt2\sin(\theta/2)\approx\sqrt2\,\theta$) but diverge as $\theta$ grows, and the Frobenius
distance saturates at $2\sqrt2$ when $\theta=\pi$. **This is why a Frobenius-based mean
(arithmetic mean followed by SVD projection) gives a different answer from the geodesic mean for
spread-out samples** — problem P5.

Equation (7) follows from the fact that the Riemannian gradient of
$f(R) = \frac12\sum_i \lVert\mathrm{Log}(R^\top R_i)\rVert^2$ is
$-\sum_i \mathrm{Log}(R^\top R_i)$ (differentiate with a right increment and apply R1).

## Proof sketch

### R3 — $J_l(\phi) = \mathrm{Exp}(\phi)J_r(\phi)$

**Hypotheses** H1: the integral form (2). H2: $\mathrm{Exp}$ is not a group homomorphism, but
rotations about the same axis satisfy
$\mathrm{Exp}(a\phi)\mathrm{Exp}(b\phi) = \mathrm{Exp}((a+b)\phi)$ (they commute).
**Conclusion** C: (4).

**Strategy**: change variables inside the integral, using nothing but the commutativity of
same-axis rotations.

1. From (2), $J_r(\phi) = \int_0^1 \mathrm{Exp}(-\alpha\phi)d\alpha$.
2. Multiply on the left by $\mathrm{Exp}(\phi)$ and move it inside (the integral is over $\alpha$
   and $\mathrm{Exp}(\phi)$ is constant):
   $\mathrm{Exp}(\phi)J_r(\phi) = \int_0^1 \mathrm{Exp}(\phi)\mathrm{Exp}(-\alpha\phi)\,d\alpha$.
3. By H2, $\mathrm{Exp}(\phi)\mathrm{Exp}(-\alpha\phi) = \mathrm{Exp}((1-\alpha)\phi)$.
4. Substituting $\beta := 1-\alpha$ gives $\int_0^1 \mathrm{Exp}(\beta\phi)d\beta = J_l(\phi)$. C.
5. $J_l(\phi) = J_r(-\phi)$ is immediate from (2). And since
   $\mathrm{Exp}(\alpha\phi)^\top = \mathrm{Exp}(-\alpha\phi)$, we get $J_l(\phi)^\top = J_r(\phi)$,
   the last equality in (4).

**Delete a hypothesis**: H2 (same-axis commutativity) is the crux. Two rotations about different
axes do not commute, so step 3 fails — for general Lie algebra elements
$\mathrm{Exp}(X)\mathrm{Exp}(Y) \ne \mathrm{Exp}(X+Y)$, and measuring that gap is exactly the BCH
expansion (R4). The two results of this lesson are two sides of one fact.

**What breaks on $SE(3)$**: the geodesic distance on $SO(3)$ is bi-invariant, but **$SE(3)$ admits
no bi-invariant Riemannian metric** [D0]. Rotation and translation have different units, so any
single metric combining them makes an arbitrary choice. "Distance" and "mean" on $SE(3)$ therefore
depend on a weighting — problem P6 and `c5-manifold-estimation`.

## Problem set

★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Write every step from (1) to (2). In particular, identify where the
adjoint identity $e^{\alpha\hat\phi}\hat\delta e^{-\alpha\hat\phi} = \widehat{\mathrm{Exp}(\alpha\phi)\delta}$
is used, and why the result is the **left** Jacobian.
*Solution sketch*: multiplying (1) on the right by $e^{-\hat\phi}$ produces the form
$\dot{R}R^{-1}$ (angular velocity seen in the reference frame), which is a left increment.
Multiplying on the left gives $R^{-1}\dot{R}$ (body frame) and hence the right Jacobian.

**P2 (derivation, ★★★, R4)** Derive the **closed form** of $J_r^{-1}(\phi)$ (not the series).
Since $J_r$ is a linear combination of $I$, $\hat\phi$ and $\hat\phi^2$ and
$\hat\phi^3 = -\theta^2\hat\phi$, the inverse has the same form. Solve for the coefficients.
*Solution sketch*: set $J_r^{-1} = aI + b\hat\phi + c\hat\phi^2$, expand $J_rJ_r^{-1} = I$, and
match the coefficients of $I$, $\hat\phi$ and $\hat\phi^2$ ($\hat\phi^3$ reduces to $\hat\phi$).
Confirm that $\sin\theta$ appears in a denominator and that the result diverges as $\theta\to\pi$.
**Always verify the result numerically** — the signs are easy to get wrong, and a wrong sign does
not show up at small angles.

**P3 (proof, ★★, R3·R4)** Derive from (8) that the first-order term of
$\mathrm{Log}(\mathrm{Exp}(\phi)\mathrm{Exp}(\delta))$ is $J_r^{-1}(\phi)\delta$, and explain via
the commutator term of the BCH expansion why the remainder is $O(\lVert\delta\rVert^2)$.
*Solution sketch*: substitute $\delta \mapsto J_r^{-1}\delta$ in the first equality of (8). The
second BCH term $\frac12[\hat\phi,\hat\delta]$ is **first order** in $\lVert\delta\rVert$ but is
already absorbed into $J_r^{-1}$; what remains starts at $\lVert\delta\rVert^2$. Stating that
distinction precisely is the point of the problem.

**P4 (numerical, ★, R2)** Compute $J_l(\phi)$ and $J_r(\phi)$ at $\phi = (0, 0, \pi/2)$.
*Answer*: $\theta=\pi/2$, $\frac{1-\cos\theta}{\theta^2} = 4/\pi^2 \approx 0.405285$,
$\frac{\theta-\sin\theta}{\theta^3} = (\pi/2-1)/(\pi/2)^3 \approx 0.147942$. With
$\hat\phi = \frac{\pi}{2}\begin{psmallmatrix}0&-1&0\\1&0&0\\0&0&0\end{psmallmatrix}$,
$J_l \approx \begin{psmallmatrix}0.635&-0.637&0\\0.637&0.635&0\\0&0&1\end{psmallmatrix}$ and
$J_r = J_l^\top$. Tolerance $10^{-3}$. Check numerically that $J_l = \mathrm{Exp}(\phi)J_r$.

**P5 (counterexample, ★★, R5)** Construct a sample for which the Frobenius-based mean (arithmetic
mean of the rotation matrices, then SVD projection onto $SO(3)$) and the geodesic mean (7) give
**different** answers. Show numerically how the gap grows with the spread of the sample, and
explain with (6) why they are indistinguishable at small spread.
*Property checklist*: two rotations at $\pm\psi$ about one axis make the two means coincide (by
symmetry) — a counterexample must be **asymmetric** or have **three or more** samples. The gap
appears as $\psi$ approaches $\pi/2$.

**P6 (counterexample / discussion, ★★, extending R5)** Explain what the absence of a bi-invariant
Riemannian metric on $SE(3)$ means in practice. Give two different ways to define the "distance"
between two poses and state the unit choice each one implicitly makes.
*Rubric*: a pass notes that combining rotation and translation into one number requires choosing a
length scale (e.g. a characteristic length of the robot), and that the choice changes the results
(nearest pose, mean, covariance).

## Paper reading

**Two must-read papers.** Write a one-page note per paper against the ten fixed questions
(the lesson standard in the research-track design notes, §5).

1. **Solà, Deray & Atchuthan, "A micro Lie theory for state estimation in robotics" (2018)** —
   role: `standard`. <https://arxiv.org/abs/1812.01537> (sections 2-4)
   Extra questions: (a) build a table mapping the authors' Jacobian notation onto this lesson's
   $J_l$ and $J_r$. (b) what decides whether to use "right-plus" or "left-plus"?
2. **Forster, Carlone, Dellaert & Scaramuzza, "On-manifold preintegration" (2017)** —
   role: `seminal`. <https://arxiv.org/abs/1512.02363> (sections II-III and the appendix)
   Extra questions: (a) find every equation in which $J_r$ appears and state in one line **why**
   it is needed there. (b) which result of this lesson justifies correcting to first order, rather
   than redoing the preintegration, when the bias changes? (c) under what condition does that
   first-order approximation break?

## Reproduction task

**Tier R1 (numerical check).** Budget: under one minute on a laptop CPU, numpy only. All four
conditions must pass.

1. **The Jacobian matches the derivative**: for 1000 values of $\phi$ with
   $\lVert\phi\rVert \in (10^{-6}, \pi-10^{-3})$ and random directions $\delta$, a central finite
   difference of
   $\partial\,\mathrm{Log}\big(\mathrm{Exp}(\phi)^\top\mathrm{Exp}(\phi+t\delta)\big)/\partial t|_{t=0}$
   agrees with $J_r(\phi)\delta$ to within $10^{-7}$.
2. **Left-right relation**: for the same $\phi$,
   $\lVert J_l(\phi) - \mathrm{Exp}(\phi)J_r(\phi)\rVert_F < 10^{-12}$ and
   $\lVert J_l(\phi) - J_r(\phi)^\top\rVert_F < 10^{-12}$.
3. **Inverse**: with the closed form derived in P2,
   $\lVert J_r(\phi)J_r^{-1}(\phi) - I\rVert_F < 10^{-10}$. Sweep $\theta \to \pi$ and confirm on a
   log plot that **the condition number diverges** (it should).
4. **Fréchet mean**: scatter 50 rotations about a true mean with standard deviation
   $0.3\,\mathrm{rad}$ and run (7) to convergence. (a) 100 restarts from random initial values all
   converge to the same solution (maximum pairwise distance $< 10^{-9}$); (b) at convergence
   $\lVert\sum_i\mathrm{Log}(\bar R^\top R_i)\rVert < 10^{-10}$ (the first-order condition);
   (c) report the gap to the Frobenius mean on the same sample, and show that it grows when the
   spread is increased to $1.2\,\mathrm{rad}$.

**Baseline**: `scipy.spatial.transform.Rotation.mean()` (a geodesic-mean implementation) must agree
with the solution of condition 4(a) to within $10^{-8}$.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| condition 1 fails only for large $\theta$ | left and right Jacobians were swapped | plot the error against $\theta$; at small angles $J_l\approx J_r$ hides it |
| `nan` at small angles | the coefficients of (3) are 0/0 | substitute $\theta=10^{-12}$ and check the series branch threshold |
| condition 3 fails as $\theta\to\pi$ | **this is correct** — $J_r^{-1}$ exists only for $\theta<\pi$ | check that the range is capped at $\pi-10^{-3}$ |
| the mean converges to different solutions | the sample is too spread (Karcher's condition violated), or the $\mathrm{Log}$ branch is mishandled | reduce the spread and retry; look for samples with $\theta\approx\pi$ |

## Open problems

- **(Open) Linearisation under large uncertainty** — because $J_r^{-1}$ diverges as
  $\theta\to\pi$, a large rotational error cannot be linearised in one step. Practice works around
  this with repeated re-linearisation, but there is **no quantitative criterion for how much
  uncertainty a tangent-space Gaussian can still represent**. Current approaches: the left/right
  uncertainty representations in
  [Barfoot SER ch.7](https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf) and the group-affine
  error dynamics of the [invariant EKF](https://arxiv.org/abs/1410.1465). What is missing: when to
  abandon linearisation for a multi-modal representation.
- **(Open) The arbitrariness of distance on $SE(3)$** — with no bi-invariant metric, rotation and
  translation must be weighted, and that choice changes nearest poses, means and covariances. There
  is no principled way to set the weighting from the task. The same problem reappears in
  `c5-manifold-estimation` and in the definition of ATE in `s1-slam-benchmarking`.
- **(Open) Jacobians inside learned models** — gradients passing through $\mathrm{Log}/\mathrm{Exp}$
  in a differentiable pipeline are numerically unstable near $\theta\approx\pi$. How far the
  gradients given by automatic differentiation can be trusted is unsettled
  ([Pinocchio's analytical derivatives](https://doi.org/10.15607/RSS.2018.XIV.038) are one alternative).

## Concept check

Run `rc quiz c1-lie-group-derivatives` (add `--lang en` for the English text). It is for concept
checking only; the real work is the problem set and the reproduction task.

The four items cover: which Jacobian goes with a right increment; the range in which $J_r^{-1}$
exists; the small-angle coefficient $1/12$; and the relation between geodesic and Frobenius distance.

## How to study this stage

1. **Write down left vs right before anything else (30 min)** — put at the top of the page whether
   your $\oplus$ is on the right or the left. Every error in this lesson starts here. Build a
   mapping table against Solà et al.'s notation.
2. **Understand Duhamel's formula as an ODE (60 min)** — do not memorise (1); see it as "an
   inhomogeneous linear ODE solved with an integrating factor". Setting up the ODE for $G$ yourself
   makes the integral form feel inevitable.
3. **Do the integral by hand (40 min)** — deriving (3) takes three lines. The last substitution
   back from $\hat u$ to $\hat\phi$ is where the powers of $\theta$ go wrong.
4. **Series first for $J_r^{-1}$, closed form second (90 min)** — do the one-line series
   computation ($c=1/12$) from the text first, then derive the closed form in P2. **Always** verify
   what you derive against condition 3 of the reproduction task; sign errors do not surface at
   small angles.
5. **Implement the mean yourself (60 min)** — (7) is five lines. Then plot the gap to the Frobenius
   mean as the spread of the sample grows. That single plot is the answer to "why bother with
   manifolds".
6. **Count every place the Jacobian appears in the papers (120 min)** — go through Forster et al.
   marking each equation containing $J_r$ and write why it is needed there. That exercise is
   preparation for the whole of C5 (state estimation).

**Passing bar**: you can derive (1)→(2)→(3) in sequence on a blank page, can prove
$J_l = \mathrm{Exp}(\phi)J_r$, have derived the closed form of $J_r^{-1}$ and verified it
numerically, have a Fréchet mean implementation meeting all four acceptance conditions, and have
notes on both papers.
