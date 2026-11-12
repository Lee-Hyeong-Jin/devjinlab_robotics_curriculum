---
id: c1-so3-se3-exponential
lang: en
title: SO(3), SE(3) and exponential coordinates
summary: >-
  Describe rigid rotations and motions as the matrix Lie groups SO(3) and SE(3), derive Rodrigues'
  formula and the SE(3) exponential from scratch, and treat the surjectivity of the exponential
  map and the singularities of the logarithm at the level of proof. Ends at why the double cover
  of unit quaternions rules out any global three-parameter representation.
objectives:
  - Derive Rodrigues' formula from the matrix exponential power series with no missing steps.
  - Reconstruct, as a proof sketch, why every rotation is a rotation about some axis (surjectivity of the exponential map).
  - Explain how the logarithm breaks down as θ → 0 and θ → π, and implement numerically safe branches.
  - Derive the translation block G(θ) of the SE(3) exponential and relate it to the left Jacobian.
  - Argue from the quaternion double cover that SO(3) admits no global singularity-free three-parameter chart.
tags: [lie-groups, so3, se3, exponential-map, rotation, research]
---

# SO(3), SE(3) and exponential coordinates

## Setup and notation

This is the first lesson of the research track, and every later module uses the notation fixed
here. The following is assumed (if it is missing, work through modules M1–M2 of the
`robotics-expert` course and the R0 bridge module first):

- Linear algebra: eigenvalues and eigenspaces, orthogonal matrices, the matrix exponential, minimal polynomials.
- Analysis: convergence of power series, existence and uniqueness for matrix-valued ODEs, Taylor's theorem.
- Differential geometry is **not** required — tangent spaces and manifolds are used here only as
  far as needed; the general theory comes in `c1-manifold-optimization`.

Notation (fixed for the whole course):

| Symbol | Meaning |
|---|---|
| $R \in SO(3)$ | $3\times3$ rotation matrix with $R^\top R = I$, $\det R = +1$ |
| $\hat{\omega}$ | skew-symmetric matrix of $\omega \in \mathbb{R}^3$, so that $\hat{\omega} x = \omega \times x$ |
| $\mathfrak{so}(3)$ | the set of $3\times3$ skew-symmetric matrices $=\{\hat{\omega} : \omega \in \mathbb{R}^3\}$, the Lie algebra of $SO(3)$ |
| $\phi = \theta u$ | rotation vector (exponential coordinates); $u$ the unit axis, $\theta = \lVert\phi\rVert$ the angle |
| $T = (R, p) \in SE(3)$ | homogeneous transform $\begin{bmatrix} R & p \\ 0 & 1\end{bmatrix}$ |
| $\xi = (\omega, v) \in \mathbb{R}^6$ | twist, with $\hat{\xi} = \begin{bmatrix} \hat{\omega} & v \\ 0 & 0\end{bmatrix} \in \mathfrak{se}(3)$ |
| $^A R_B$ | the rotation taking frame $B$ into frame $A$. Coordinates are **column vectors**; transforms multiply **on the left** |

Two identities for $\lVert \omega \rVert = 1$ are used throughout. Expand both by hand to confirm them:

$$\hat{\omega}^2 = \omega\omega^\top - I, \qquad \hat{\omega}^3 = -\hat{\omega}. \tag{1}$$

## Self-diagnosis before starting

This is the first lesson of the module, so check your readiness first. **Prerequisite lessons are
not locked** — if you can solve all of the following, skip the recommended prerequisites (the R0
module and M1 of the `robotics-expert` course) and start here. **If two or more stop you**, going
back to the prerequisite lesson named in parentheses is faster.

1. What is the 2-norm condition number $\kappa_2(A)$ of $A = \mathrm{diag}(3, 1, 0.01)$?
   (`r0-linear-algebra-decompositions`)
   **Answer**: $\kappa_2 = \sigma_{\max}/\sigma_{\min} = 3/0.01 = 300$.
2. If $R \in \mathbb{R}^{3\times3}$ satisfies $R^\top R = I$, which values can $\det R$ take,
   and which of them belong to $SO(3)$? (`m1-rotation-representations`)
   **Answer**: $\det R = \pm1$ (from $\det(R^\top R) = (\det R)^2 = 1$). $SO(3)$ takes only $+1$.
3. Write the series definition of the matrix exponential $\exp(A)$ and state when
   $\exp(A+B) = \exp(A)\exp(B)$ holds. (`r0-ad-and-integrators`)
   **Answer**: $\exp(A) = \sum_{k\ge0} A^k/k!$. The identity holds only when $AB = BA$.
4. For $f(x) = x^\top M x$ with symmetric $M$, write $\nabla f$ and the first-order Taylor
   expansion at $x_0$. (`f0-calculus-multivariable`)
   **Answer**: $\nabla f = 2Mx$ and $f(x_0 + \delta) \approx f(x_0) + 2(Mx_0)^\top\delta$.
5. In at most three lines of numpy, compute the Jacobian of $g: \mathbb{R}^3 \to \mathbb{R}^3$
   by central finite differences, and say why a step size of $10^{-5}$ is a reasonable choice.
   (`r0-ad-and-integrators`)
   **Answer**: column $i$ is $(g(x + he_i) - g(x - he_i))/(2h)$. Central differences have
   truncation error $O(h^2)$ and round-off error $O(\epsilon/h)$, so in double precision
   ($\epsilon \approx 2\times10^{-16}$) the optimum is near
   $h \sim \epsilon^{1/3} \approx 6\times10^{-6}$.

## Key results

The bracketed tag is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
see the lesson standard in the research-track design notes, §2).

- **R1 (Rodrigues' formula) [D3]** — for $\lVert \omega \rVert = 1$,
  $$\exp(\hat{\omega}\theta) = I + \sin\theta\,\hat{\omega} + (1 - \cos\theta)\,\hat{\omega}^2. \tag{2}$$
- **R2 (surjectivity of the exponential = Euler's rotation theorem) [D3]** — for every
  $R \in SO(3)$ there exist a unit $\omega$ and $\theta \in [0, \pi]$ with $R = \exp(\hat{\omega}\theta)$.
  So $\exp : \mathfrak{so}(3) \to SO(3)$ is surjective, and every rotation is **a single rotation
  about some axis**.
- **R3 (the logarithm and its singularities) [D3]** — for $\theta \in (0, \pi)$,
  $$
  \theta = \arccos\!\left(\frac{\operatorname{tr} R - 1}{2}\right), \qquad
    \hat{\omega} = \frac{R - R^\top}{2\sin\theta}. \tag{3}
  $$
  The axis is **undefined** as $\theta \to 0$ (0/0), and as $\theta \to \pi$ the numerator
  $R - R^\top \to 0$ so the **axis information is lost**. Both cases need separate branches.
- **R4 (quaternion double cover and the absence of a global chart) [D2]** — the unit quaternions
  give a 2:1 cover $S^3 \to SO(3)$, with $q$ and $-q$ producing the same rotation. Hence
  $SO(3) \cong \mathbb{RP}^3$, which is compact and therefore cannot be diffeomorphic to
  $\mathbb{R}^3$: **no global singularity-free three-parameter chart exists.**
- **R5 (the SE(3) exponential) [D2]** — for $\lVert \omega \rVert = 1$ and $\xi = (\omega, v)$,
  $$
  \exp(\hat{\xi}\theta) = \begin{bmatrix} \exp(\hat{\omega}\theta) & G(\theta)\,v \\ 0 & 1 \end{bmatrix},
    \quad G(\theta) = I\theta + (1 - \cos\theta)\hat{\omega} + (\theta - \sin\theta)\hat{\omega}^2. \tag{4}
  $$
  Here $G(\theta) = \theta J_l(\theta u)$, where $J_l$ is the **left Jacobian** of $SO(3)$ — that
  connection is the starting point of `c1-lie-group-derivatives`. **[D1]**

## Derivation

### R1 — Rodrigues' formula

Fix $\omega$ as a unit vector and define rotation as the solution of the angular-velocity ODE:

$$
\dot{R}(t) = \hat{\omega} R(t), \qquad R(0) = I
  \;\;\Longrightarrow\;\; R(\theta) = \exp(\hat{\omega}\theta) = \sum_{k=0}^{\infty} \frac{(\hat{\omega}\theta)^k}{k!}. \tag{5}
$$

The series converges absolutely for any matrix, so its terms may be rearranged. By
$\hat{\omega}^3 = -\hat{\omega}$ from (1), the powers close with period 4:

$$
\hat{\omega}^1 = \hat{\omega}, \quad \hat{\omega}^2 = \hat{\omega}^2, \quad
  \hat{\omega}^3 = -\hat{\omega}, \quad \hat{\omega}^4 = -\hat{\omega}^2, \quad
  \hat{\omega}^5 = \hat{\omega}, \; \dots
$$

So every term with $k \ge 1$ collects into **odd powers → multiples of $\hat{\omega}$** and
**even powers → multiples of $\hat{\omega}^2$**. Gathering coefficients,

$$
\exp(\hat{\omega}\theta) = I
  + \underbrace{\left(\theta - \frac{\theta^3}{3!} + \frac{\theta^5}{5!} - \cdots\right)}_{=\,\sin\theta}\hat{\omega}
  + \underbrace{\left(\frac{\theta^2}{2!} - \frac{\theta^4}{4!} + \frac{\theta^6}{6!} - \cdots\right)}_{=\,1-\cos\theta}\hat{\omega}^2,
$$

which is (2). The easiest sign to get wrong is where $\hat{\omega}^4 = -\hat{\omega}^2$ makes the
even series $1 - \cos\theta$ rather than $\cos\theta$. Write out two terms and check it yourself.

**Where the assumption breaks**: (1) holds only for $\lVert \omega \rVert = 1$. Applying (2)
directly to a non-unit $\phi$ is wrong — you must split $\theta = \lVert \phi \rVert$,
$u = \phi/\theta$ first, and that split is itself 0/0 as $\theta \to 0$. In an implementation,
replace $\sin\theta/\theta$ and $(1-\cos\theta)/\theta^2$ by their **Taylor series** and use the
form that takes $\phi$ directly:

$$
\exp(\hat{\phi}) = I + \frac{\sin\theta}{\theta}\hat{\phi} + \frac{1 - \cos\theta}{\theta^2}\hat{\phi}^2
  \;\xrightarrow[\theta \to 0]{}\; I + \hat{\phi} + \tfrac{1}{2}\hat{\phi}^2. \tag{6}
$$

Switching to the series below about $\theta \lesssim 10^{-4}$ keeps the relative error at machine precision.

### R5 — the SE(3) exponential

Compute the powers of $\hat{\xi}$ blockwise. Confirm by induction that
$\hat{\xi}^k = \begin{bmatrix} \hat{\omega}^k & \hat{\omega}^{k-1}v \\ 0 & 0\end{bmatrix}$ for
$k \ge 1$, and substitute into the series:

$$
\exp(\hat{\xi}\theta) = \begin{bmatrix}
  \sum_k \frac{(\hat{\omega}\theta)^k}{k!} &
  \left(\sum_{k\ge1} \frac{\theta^k \hat{\omega}^{k-1}}{k!}\right) v \\ 0 & 1 \end{bmatrix}.
$$

The upper-left block is R1. Collecting the upper-right series into $I$, $\hat{\omega}$ and
$\hat{\omega}^2$ components the same way gives $G(\theta)$ in (4). The expansion is left as problem P1.

**Geometric reading**: $G(\theta)v$ is the translation of a screw motion — rotating about the axis
while sliding along it. Pure translation ($\omega = 0$) is a separate degenerate case in which (4)
reduces to $G \to I\theta$; the exponential is still well defined there.

## Proof sketch

### R2 — surjectivity of the exponential map (Euler's rotation theorem)

**Hypotheses** H1: $R^\top R = I$. H2: $\det R = +1$.
**Conclusion** C: $R$ has a real eigenvector $u$ with eigenvalue 1 and acts as a planar rotation
on the plane orthogonal to $u$; hence $R = \exp(\hat{u}\theta)$.

**Strategy**: show $\det(R - I) = 0$ directly to get the eigenvalue 1, then reduce to the
orthogonal complement of the invariant axis.

1. **Existence of eigenvalue 1.** From H1 and H2,
   $$
   \det(R - I) = \det(R^\top)\det(R - I) = \det(R^\top R - R^\top) = \det(I - R^\top)
     = \det\!\big((I-R)^\top\big) = \det(I - R) = (-1)^3\det(R - I),
   $$
   so $\det(R-I) = -\det(R-I)$, giving $\det(R - I) = 0$. Hence there is $u \ne 0$ with $Ru = u$;
   normalise to $\lVert u \rVert = 1$. (The **odd dimension** is decisive here — for even $n$ the
   factor $(-1)^n$ is $+1$ and the argument collapses. It does not carry over to $SO(2)$ or $SO(4)$.)
2. **Reduction to the plane.** $u^\perp$ is $R$-invariant: if $x \perp u$ then
   $\langle Rx, u\rangle = \langle Rx, Ru\rangle = \langle x, u \rangle = 0$. In an orthonormal
   basis of $u^\perp$ the restriction of $R$ is a $2\times2$ orthogonal matrix of determinant
   $+1$, hence a planar rotation by some $\theta$.
3. **Writing it as an exponential.** In the basis $\{u, e_1, e_2\}$,
   $R = \operatorname{diag}(1, R_{2\times2}(\theta))$, and $\exp(\hat{u}\theta)$ has the same form
   in that basis (substitute into R1). Two matrices agreeing in a basis agree, which gives C.
4. **Range.** $\theta$ may be restricted to $[0, \pi]$, since
   $\exp(\hat{u}\theta) = \exp(\widehat{(-u)}(-\theta))$ and $\theta \mapsto \theta + 2\pi$ gives
   the same rotation. At $\theta = \pi$, $u$ and $-u$ give the same rotation, so **uniqueness
   fails** — this is exactly the singularity in R3.

**Delete a hypothesis**: drop H2 ($\det = +1$) and reflections are admitted, so the $2\times2$
block in step 2 may have determinant $-1$; no such transform can be written as
$\exp(\hat{\omega}\theta)$, since the image of $\exp$ always has $\det = +1$. The theorem is false on $O(3)$.

Technical step omitted: the block-diagonalisation theorem for real orthogonal matrices. See the
corresponding lemma in Barfoot ch.7 or MLS ch.2.

### R4 — the argument that no global chart exists [D2]

1. The rotation $R(q)$ induced by a unit quaternion satisfies $R(q) = R(-q)$, so $S^3 \to SO(3)$ is 2:1.
2. The map is smooth, surjective and a local diffeomorphism, hence $SO(3) \cong S^3/\{\pm 1\} = \mathbb{RP}^3$.
3. $S^3$ is compact and the quotient map is continuous, so $SO(3)$ is **compact**.
4. $\mathbb{R}^3$ is not compact, and diffeomorphisms preserve compactness, so
   $SO(3) \not\cong \mathbb{R}^3$: no globally smooth bijective three-parameter chart can exist.
5. Consequence: every three-parameter representation has a singularity — Euler angles have gimbal
   lock, exponential coordinates degenerate at $\theta = \pi$ (and their Jacobian degenerates at
   $\theta = 2\pi$). The way out is not to remove the singularity but to
   **over-parameterise (quaternions, rotation matrices) and represent only increments in local
   coordinates**. That strategy is the whole design of `c1-manifold-optimization` and
   `c5-manifold-estimation`.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R5)** Expand $G(\theta)$ in (4) in full. Split the series
$\sum_{k\ge1} \theta^k \hat{\omega}^{k-1}/k!$ into $I$, $\hat{\omega}$ and $\hat{\omega}^2$
components and show the coefficients are $\theta$, $1-\cos\theta$ and $\theta - \sin\theta$.
*Solution sketch*: separate $k = 1$, even $k$, and odd $k \ge 3$; reduce the powers with (1); then
gather as in R1. The $\hat{\omega}^2$ coefficient comes from the difference of the $\theta$ and
$\sin\theta$ series.

**P2 (proof, ★★★, R2)** State exactly where step 1 of R2 fails for $SO(2)$ and $SO(4)$, and give a
counterexample showing that a rotation in $SO(4)$ is in general *not* a single rotation about one axis.
*Solution sketch*: in $\det(R-I) = (-1)^n \det(R-I)$, even $n$ makes this a tautology carrying no
information. For $SO(4)$ use a **double rotation** turning by different angles in two orthogonal
planes (block diagonal $\operatorname{diag}(R_2(\alpha), R_2(\beta))$ with $\alpha \ne \beta$,
which has no eigenvalue 1).

**P3 (numerical, ★, R1·R3)** Find the exponential coordinates $(\theta, u)$ of
$$R = \begin{bmatrix} 0 & 0 & 1 \\ 1 & 0 & 0 \\ 0 & 1 & 0 \end{bmatrix}$$
*Answer*: $\operatorname{tr} R = 0$, so $\theta = \arccos(-1/2) = 2\pi/3 \approx 2.0943951$ and
$u = (1, 1, 1)/\sqrt{3} \approx (0.57735027, 0.57735027, 0.57735027)$. Tolerance $10^{-7}$.
Check by substituting into (2) and confirming $\lVert \exp(\hat{u}\theta) - R \rVert_F < 10^{-12}$.

**P4 (implementation, ★★, R1·R3·R5)** Write `exp_so3(phi)` and `log_so3(R)` taking
$\phi \in \mathbb{R}^3$, and `exp_se3(xi)` taking $\xi \in \mathbb{R}^6$. Both the small-angle
branch ((6)) and the $\theta \approx \pi$ branch must be handled.
*Rubric*: (a) no `nan` at $\theta = 0$; (b) relative axis error below $10^{-6}$ near $\theta = \pi$;
(c) the round-trip error meets the acceptance criteria of the reproduction task; (d) the branch
threshold is documented and justified by machine precision, not picked arbitrarily.

**P5 (counterexample, ★★, R4)** Show in **two different ways** that the claim "exponential
coordinates $\phi \in \mathbb{R}^3$ are a global chart for $SO(3)$" is false: (i) a concrete pair
$\phi, \phi'$ where injectivity fails; (ii) a value of $\theta$ at which the determinant of the
differential of $\exp$ (the left Jacobian) vanishes.
*Property checklist*: for (i) use $\theta$ and $\theta + 2\pi$, or $\pm u$ at $\theta = \pi$. For
(ii) use $\det J_l(\theta u) = 2(1 - \cos\theta)/\theta^2$ and find $\theta = 2\pi$.

**P6 (paper, ★★, R3·R5)** Read sections II–III of Forster et al. 2017 and write, in at most three
sentences each, where the authors use the right Jacobian $J_r$ and what goes wrong if rotation
errors are simply subtracted in Euclidean space. If that choice were wrong, what would break first?
*Rubric*: a pass needs both that it is used in bias re-linearisation and uncertainty propagation,
and that $SO(3)$ is not a vector space so addition does not agree with the group operation.
"Because it is nonlinear" alone does not pass.

## Paper reading

**Two must-read papers.** Write a one-page note per paper against the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes, attacking questions 4, 5, 6 and 7 in the third pass.

1. **Solà, Deray & Atchuthan, "A micro Lie theory for state estimation in robotics" (2018, arXiv)**
   — role: `standard`. <https://arxiv.org/abs/1812.01537>
   Extra questions: (a) rewrite this paper's $\oplus$/$\ominus$ notation in the $\exp$/$\log$
   notation of this lesson; (b) what does the difference between the left and the right Jacobian
   actually change in an estimation problem?
2. **Forster, Carlone, Dellaert & Scaramuzza, "On-manifold preintegration for real-time
   visual-inertial odometry" (2017, IEEE T-RO)** — role: `seminal`.
   <https://arxiv.org/abs/1512.02363> (sections II–III only)
   Extra questions: (a) which equation would be wrong without the manifold notation?
   (b) is anything needed for reproduction missing from the paper?

**The ten fixed questions**: (1) what problem, under which assumptions? (2) what exactly could
prior work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and
**what is not**? (5) independent/dependent variables and baselines — were the baselines tuned
fairly? (6) do the metrics match the claim, and are variance and seeds reported? (7) what is
missing for reproduction? (8) which assumption would you doubt first if the result were wrong?
(9) computational and memory cost, and real-time feasibility. (10) what would you change to go
beyond this a year from now?

## Reproduction task

**Tier R1 (numerical check).** Budget: under one minute on a laptop CPU, numpy only.

The `exp_so3`/`log_so3`/`exp_se3` written for P4 must satisfy **all four** conditions.

1. **Round trip (generic region)**: for $10^5$ rotation vectors drawn uniformly with
   $\lVert \phi \rVert \in (10^{-8},\ \pi - 10^{-3})$,
   $\max \lVert \log(\exp(\hat{\phi})) - \phi \rVert_\infty < 10^{-12}$.
2. **Round trip ($\theta \to \pi$)**: for $10^3$ vectors with
   $\lVert \phi \rVert \in (\pi - 10^{-6},\ \pi)$, the error of the rotation itself satisfies
   $\lVert \exp(\widehat{\log(R)}) - R \rVert_F < 10^{-6}$ — compare **rotations, not vectors**,
   because the sign of the axis is not unique at $\theta = \pi$.
3. **Small angle**: at $\lVert \phi \rVert = 10^{-10}$, $\exp(\hat{\phi})$ returns no `nan` and
   satisfies $\lVert \exp(\hat{\phi}) - (I + \hat{\phi}) \rVert_F < 10^{-18}$.
4. **Differential check**: the differential of $\exp$ at $\phi = 0$ is the identity — a finite
   difference estimate of $\partial \log(\exp(\hat{\epsilon}))/\partial \epsilon$ agrees with $I$
   to within $10^{-7}$. (Jacobians at general $\phi$ come in `c1-lie-group-derivatives`.)

**Baseline**: `scipy.spatial.transform.Rotation` with `from_rotvec`/`as_rotvec` must agree with
your rotation matrices to $10^{-12}$ on the same inputs (watch the component-order convention).

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| `nan` or 0/0 at small angles | terms divided by $\theta$ were not replaced by series | substitute $\theta = 10^{-12}$ directly |
| axis jumps near $\theta \approx \pi$ | $R - R^\top$ in (3) vanishes — cancellation error | sweep $\theta$ towards $\pi$ and plot the axis error on a log scale |
| round-trip error grows with iteration | numerical drift takes $R$ off $SO(3)$ | track $\lVert R^\top R - I \rVert_F$ and re-project with an SVD |
| signs are flipped | the convention $\hat{\omega}x = \omega \times x$ was violated (skew sign) | check that $\hat{e}_1 e_2 = e_3$ |

## Open problems

- **(Open) Which local chart is best under uncertainty?** R4 forbids a global chart, so practice
  represents increments in local coordinates. But under large rotational uncertainty the local
  Gaussian assumption itself breaks down (once the distribution of $\theta$ spreads over
  $[0,\pi]$, a tangent-space Gaussian loses meaning), and there is no general theory of which
  retraction best preserves estimator consistency. Current approaches: the left/right uncertainty
  representations in [Barfoot SER ch.7](https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf)
  and the [invariant EKF](https://arxiv.org/abs/1410.1465). What is missing: a selection criterion
  in the large-uncertainty regime.
- **(Open) What is actually gained by building Lie-group structure into learned models?** No
  quantitative criterion is established, at robotics data scale, for when an equivariant
  architecture beats data augmentation. The question returns in
  `c7-learned-correspondence-slam` and `s4-pretrained-representations`.
- **(Open) How far does certifiable global optimality extend over $SE(3)$?** Tightness conditions
  for the dual relaxation are known for pose graphs ([SE-Sync](https://arxiv.org/abs/1612.07386)
  in `c5-robust-global-estimation`), but they do not extend to general non-convex problems on $SE(3)$.

## Concept check

Run `rc quiz c1-so3-se3-exponential` (add `--lang en` for the English text). The quiz is for
**concept checking only**; the real work is the problem set and the reproduction task above
(`lesson-standard.md` §4).

The four items cover: the identity $\hat{\omega}^3 = -\hat{\omega}$; why the logarithm breaks at
$\theta \to \pi$; why no global three-parameter chart exists; and the rotation angle of a matrix
with $\operatorname{tr} R = 0$.

## How to study this stage

1. **Fix the notation first (30 min)** — copy the notation table out by hand and expand both
   identities in (1) yourself. Every later module uses this notation.
2. **Rewrite the derivation instead of following it (90 min)** — reconstruct R1 on a blank page
   with the text closed. If you get stuck where the even series becomes $1 - \cos\theta$, reread
   only that step. Read Barfoot ch.7 against Modern Robotics ch.3.2 as **the same result in
   different notation**.
3. **Memorise the strategy, not the trick (60 min)** — step 1 of R2 ($\det(R-I) = 0$) is a
   one-line trick. Remember *why odd dimension is needed* rather than the trick itself; solving
   P2 makes that spot visible.
4. **Meet the singularities by hand, in code (90 min)** — implement P4 and the reproduction task
   **without branches** first, watch them break at $\theta \to 0$ and $\theta \to \pi$, and only
   then add the branches. A branch added without seeing the failure does not stick.
5. **Read the papers by mapping notation (120 min)** — read Solà et al. first and transcribe
   $\oplus/\ominus$ into this lesson's $\exp/\log$. Then see in Forster et al. II–III how that
   notation is used in a real estimation problem. Write the one-page note per paper — **always**;
   skip it and you will be rereading the paper in the next module.
6. **Finish with what is not known (30 min)** — read the open problems, pick one, and write a
   paragraph on why it is still open. This habit is what turns into choosing a research topic.

**Passing bar**: you can derive (2) and (4) on a blank page, can state the proof strategy for R2,
have code meeting all four acceptance conditions, and have notes on both papers.
