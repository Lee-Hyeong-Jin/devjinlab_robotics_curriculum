---
id: c1-manifold-optimization
lang: en
title: Optimization on manifolds - retractions and Gauss-Newton
summary: >-
  Formulate optimization on a Lie group as lift-solve-retract and treat the local convergence of
  retraction-based Gauss-Newton at the level of proof. Ends at why over-parameterisation with a
  normalisation penalty produces singular normal equations, and at how the gauge freedom of a pose
  graph shows up as the null space of the information matrix.
objectives:
  - State the conditions for a retraction and verify that the exponential map satisfies them.
  - Derive that lift-solve-retract agrees with the Riemannian gradient to first order.
  - Reconstruct, as a proof sketch, the local convergence rate of retraction-based Gauss-Newton together with its dependence on the residual size.
  - Show why the normal equations of an over-parameterised formulation are rank deficient, and compare with a local parameterisation.
  - Explain how the gauge freedom of a pose graph appears as the dimension of the information matrix's null space.
tags: [lie-groups, optimization, gauss-newton, retraction, gauge-freedom, research]
---

# Optimization on manifolds - retractions and Gauss-Newton

## Setup and notation

The notation of the previous four lessons carries over; in particular $\oplus$, $\ominus$ and
$J_r$ from `c1-lie-group-derivatives` are the tools of this lesson. Additional symbols:

| Symbol | Meaning |
|---|---|
| $\mathcal{M}$ | a smooth manifold; here $SO(3)$, $SE(3)$ or a product of them |
| $T_X\mathcal{M}$ | the tangent space at $X$ |
| $\mathrm{R}_X : T_X\mathcal{M} \to \mathcal{M}$ | a **retraction** at $X$ |
| $X \oplus \delta := X\,\mathrm{Exp}(\delta)$ | the retraction used here (a right increment) |
| $f : \mathcal{M} \to \mathbb{R}$ | the objective, in least-squares form $f(X) = \tfrac12\sum_k \lVert e_k(X)\rVert^2_{\Sigma_k}$ |
| $J_k$ | the Jacobian of the residual $e_k$ **with respect to the tangent space** ($\partial e_k(X\oplus\delta)/\partial\delta|_0$) |
| $\Lambda = J^\top \Sigma^{-1} J$ | the information matrix |

**Conditions for a retraction**: $\mathrm{R}_X(0) = X$ and $\mathrm{D}\mathrm{R}_X(0) = \mathrm{id}$
(local rigidity). That is, it only has to agree with the tangent space to first order at the
origin — **it need not be a geodesic.** $\mathrm{Exp}$ satisfies this (from $J_r(0)=I$ in the
previous lesson), and so does quaternion normalisation
$q \mapsto (q+\delta)/\lVert q+\delta\rVert$. Both are retractions, but they behave differently — §3.

## Key results

- **R1 (lift-solve-retract) [D2]** — optimization on a manifold is an iteration of three steps:

$$
\text{(lift)}\ \ \tilde{f}_X(\delta) := f(X \oplus \delta), \qquad
\text{(solve)}\ \ \delta^\star = \arg\min_\delta \tilde{f}_X(\delta), \qquad
\text{(retract)}\ \ X \leftarrow X \oplus \delta^\star. \tag{1}
$$

  $\tilde{f}_X$ is a function on **Euclidean space**, so ordinary calculus applies, and
  $\nabla\tilde{f}_X(0)$ agrees with the Riemannian gradient to first order.
- **R2 (manifold Gauss-Newton) [D2]** — expanding the residuals to first order gives the normal equations

$$
\Big(\underbrace{\sum_k J_k^\top \Sigma_k^{-1} J_k}_{\Lambda}\Big)\delta
= -\sum_k J_k^\top \Sigma_k^{-1} e_k(X), \tag{2}
$$

  where $J_k$ is the Jacobian **with respect to the tangent space**. Its width is the dimension of
  the manifold (6 per $SE(3)$, not the 7 of a quaternion over-parameterisation).
- **R3 (local convergence) [D3]** — if $X^\star$ is a local minimum and $\Lambda(X^\star)$ is
  positive definite, retraction-based Gauss-Newton converges **linearly** in some neighbourhood of
  $X^\star$, at a rate proportional to the residual size:

$$
\lVert \delta_{i+1} \rVert \le c_1 \lVert r^\star \rVert\,\lVert \delta_i \rVert
+ c_2 \lVert \delta_i \rVert^2. \tag{3}
$$

  For a zero-residual problem ($r^\star = 0$) this becomes **quadratic** convergence. The
  conclusion is unchanged if the retraction is not a geodesic — only local rigidity is used.
- **R4 (over-parameterisation creates rank deficiency) [D2]** — if a rotation is carried as 7 free
  variables with $\lVert q \rVert = 1$ handled by a penalty, the coefficient matrix of the normal
  equations has a **null space along $q$**: a perturbation in that direction does not change the
  rotation, so every residual Jacobian vanishes there. Without damping the system cannot be
  solved, and damping slows convergence. A local parameterisation never creates that direction.
- **R5 (gauge freedom) [D2]** — in a pose graph built only from relative measurements, $\Lambda$
  has a null space of dimension **$\dim SE(3) = 6$** (rigidly transforming the whole trajectory
  leaves every residual unchanged). Uniqueness requires fixing one pose or adding a prior. For
  monocular vision the scale is unobservable too, making it 7.

## Derivation

### R1 — lift-solve-retract and first-order equivalence

Fix $X \in \mathcal{M}$ and **lift** the objective to $\tilde{f}_X(\delta) = f(X \oplus \delta)$.
Since $\delta \in \mathbb{R}^n$, $\tilde{f}_X$ is an ordinary multivariate function. From the
retraction conditions $\mathrm{R}_X(0)=X$ and $\mathrm{D}\mathrm{R}_X(0)=\mathrm{id}$,

$$
\tilde{f}_X(\delta) = f(X) + \nabla\tilde{f}_X(0)^\top\delta + O(\lVert\delta\rVert^2),
\qquad \nabla\tilde{f}_X(0) = \mathrm{grad}\,f(X)
$$

— **to first order every retraction gives the same gradient.** That is the basis for "no geodesic
needed" in R2 and R3. From the second order on, the retraction matters, so in a second-order method
(Newton) its second-order behaviour enters the convergence constants (see the second-order
retraction in R5).

**Caution**: $\delta$ is **a fresh coordinate every iteration**. Because $X$ changes each time, the
$\delta_i$ must never be added together or compared. Convergence is judged by
$\lVert\delta_i\rVert$, and accumulation happens only through $\oplus$. Breaking this rule is the
most common bug in manifold optimization.

### R2 — tangent-space Jacobians and the normal equations

Expand the residual $e_k(X \oplus \delta)$ to first order in $\delta$:

$$
e_k(X \oplus \delta) \approx e_k(X) + J_k\delta, \qquad
J_k := \left.\frac{\partial e_k(X \oplus \delta)}{\partial \delta}\right|_{\delta = 0}.
$$

Differentiating $\tilde{f}_X(\delta) \approx \tfrac12\sum_k \lVert e_k(X) + J_k\delta\rVert^2_{\Sigma_k}$
in $\delta$ and setting it to zero gives (2). It has **the same form** as Euclidean Gauss-Newton;
the only difference is that $J_k$ is a derivative with respect to the tangent space. That is why
sparse Cholesky, Schur complements and the rest carry over unchanged (`c5-sparsity-isam`).

**How to obtain $J_k$ in practice**: if the residual has the form $e(X) = \mathrm{Log}(Z^{-1}X)$,
then $e(X\oplus\delta) = \mathrm{Log}(Z^{-1}X\,\mathrm{Exp}(\delta))$, and by the first BCH term
(R4 of the previous lesson),

$$
e(X \oplus \delta) \approx e(X) + J_r^{-1}\big(e(X)\big)\,\delta
\;\;\Longrightarrow\;\; J = J_r^{-1}\big(e(X)\big). \tag{4}
$$

**This is where the previous lesson's $J_r^{-1}$ is used.** Setting it to $I$ (computing the
Jacobian as if Euclidean) works for small errors but converges more slowly as the error grows, and
it makes the covariance wrong.

### R4 — the null space created by over-parameterisation

Suppose a rotation is carried as a unit quaternion $q \in \mathbb{R}^4$ with $\lVert q\rVert = 1$
imposed by a penalty $\tfrac{\mu}{2}(\lVert q\rVert^2-1)^2$. The residuals depend on $q$ only
through the rotation $R(q)$, and $R(sq) = R(q)$ (homogeneity), so perturbing along $q$ itself does
not change the rotation:

$$
\left.\frac{\partial e_k(R(q + t q))}{\partial t}\right|_{t=0} = 0 \quad \text{for all } k .
$$

The data term $\sum_k J_k^\top\Sigma_k^{-1}J_k$ therefore **has $q$ in its null space**. Only the
penalty supplies curvature in that direction, and that curvature is proportional to $\mu$, so

- small $\mu$ leaves the direction nearly flat and the normal equations ill-conditioned, while
- large $\mu$ mismatches the scale of the data term and slows convergence in other directions.

A local parameterisation (3 variables per $SO(3)$, 6 per $SE(3)$) **removes the direction from the
coordinates in the first place**, so neither damping nor a penalty is needed. The reproduction task
makes this visible as a difference in iteration count.

**Do not conflate the two**: the null space in R4 is **an artefact of over-parameterisation**,
whereas the gauge null space in R5 is **a property of the problem**. The former can be removed by
changing coordinates; the latter needs more measurements or a fixed reference. Covering both with
the same damping term means never learning why convergence is slow.

## Proof sketch

### R3 — local convergence of retraction-based Gauss-Newton

**Hypotheses** H1: $f(X) = \tfrac12\sum_k\lVert e_k(X)\rVert^2$ with each $e_k$ of class $C^2$.
H2: $X^\star$ is a local minimum and $\Lambda^\star := J^{\star\top}J^\star$ is positive definite.
H3: $\mathrm{R}$ is a retraction ($\mathrm{R}_X(0)=X$, $\mathrm{D}\mathrm{R}_X(0)=\mathrm{id}$).
**Conclusion** C: (3) — linear convergence near $X^\star$, quadratic if $r^\star=0$.

**Strategy**: apply the classical Euclidean Gauss-Newton analysis to the lifted function and
absorb the manifold-side error using local rigidity. That is, **do not invent a new theorem;
change coordinates so an existing one applies.**

1. **Fix coordinates.** Near $X^\star$ use the error coordinate $\varepsilon := X \ominus X^\star$.
   By H3 the map $\varepsilon \mapsto X$ is a diffeomorphism near 0 with derivative $\mathrm{id}$.
2. **The lifted problem.** $g(\varepsilon) := f(X^\star \oplus \varepsilon)$ is a $C^2$ function on
   $\mathbb{R}^n$ with $\nabla g(0)=0$ and
   $\nabla^2 g(0) = \Lambda^\star + \sum_k e_k^\star \nabla^2 e_k^\star$. The second term is the
   **residual term** and produces the $c_1\lVert r^\star\rVert$ of (3).
3. **Invoke the classical result.** Applying the local convergence theorem for Euclidean
   Gauss-Newton (Nocedal-Wright ch.10) to $g$ gives
   $\lVert\varepsilon_{i+1}\rVert \le \tilde{c}_1\lVert r^\star\rVert\lVert\varepsilon_i\rVert
   + \tilde{c}_2\lVert\varepsilon_i\rVert^2$. (Omitted: the proof of that theorem — Nocedal-Wright
   Theorem 10.1.)
4. **Absorb the retraction error.** The actual algorithm lifts afresh at each $X_i$ rather than in
   the $\varepsilon$ coordinate. The difference between the two coordinates is
   $O(\lVert\delta_i\rVert^2)$ (first-order agreement, H3), and that term is absorbed into
   $\tilde{c}_2\lVert\varepsilon_i\rVert^2$ of step 3. Only the constant grows; **the order does not change.**
5. **Conclude.** $\lVert\delta_i\rVert$ and $\lVert\varepsilon_i\rVert$ are equivalent near 0, giving C.

**Delete a hypothesis**: drop the positive definiteness of $\Lambda^\star$ in H2 (i.e. the gauge
freedom of R5 is present) and the solution is not unique — the iteration drifts along the null
space. $\lVert\delta\rVert$ still decreases while the answer differs every run, which is why
fixing the gauge is **a precondition for convergence**. Drop the local rigidity of H3 and the
diffeomorphism of step 1 fails, so the analysis does not even start.

## Problem set

★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Derive (4) for the residual $e(X) = \mathrm{Log}(Z^{-1}X)$. Substitute
$X \oplus \delta$ and use the first BCH term from the previous lesson. Why does it matter that
$J = J_r^{-1}(e(X))$ depends on $e(X)$ (i.e. is not constant)?
*Solution sketch*: $\mathrm{Log}(Z^{-1}X\mathrm{Exp}(\delta)) = \mathrm{Log}(\mathrm{Exp}(e)\mathrm{Exp}(\delta))
= e + J_r^{-1}(e)\delta + O(\lVert\delta\rVert^2)$. Because the Jacobian depends on the current
error it must be **recomputed every iteration**, and for large errors $J_r^{-1}$ departs from $I$
(previous lesson: it diverges as $\theta\to\pi$).

**P2 (derivation, ★★, R5)** Show that the null space of $\Lambda$ has dimension 6 for a pose graph
with only relative measurements, and write down a basis for it. Also say why it becomes 7 for a
monocular problem.
*Solution sketch*: left-multiplying every pose by the same $T \in SE(3)$ leaves the relative
measurements $T_i^{-1}T_j$ unchanged; the six one-parameter groups of that transformation give a
basis. In the monocular case rescaling the whole reconstruction leaves the reprojection residuals
unchanged, adding one more direction.

**P3 (proof, ★★★, R3)** Write step 4 of R3 ("the retraction error is absorbed into the
second-order term") precisely. Compare how the constant $\tilde{c}_2$ differs when $\mathrm{R}$ is
the geodesic ($\mathrm{Exp}$) and when it is quaternion normalisation.
*Solution sketch*: the two retractions first differ at second order — comparing the quadratic
terms of the Taylor expansions, $\mathrm{Exp}$ contributes the second-order term of $J_r$ while
normalisation contributes a term of the form $-\tfrac12 q(\delta^\top\delta)$. The order is the
same; only the constant differs.

**P4 (numerical, ★, R4)** For a problem with one rotation and one measurement
($e = \mathrm{Log}(Z^{-1}R)$), find the eigenvalues of the $4\times4$ coefficient matrix of the
quaternion over-parameterisation with penalty $\mu$, as a function of $\mu$, at the solution
($R = Z$).
*Answer*: at the solution $e=0$, so the data term is $J^\top J$, whose rank is 3 (the tangent-space
dimension) with $q$ in its null space. The Hessian of the penalty at the solution
($\lVert q\rVert=1$) is $2\mu\,qq^\top$, so the eigenvalues are the three positive ones of the data
term plus **$2\mu$**. The condition number diverges as $\mu \to 0$. Tolerance $10^{-9}$.

**P5 (implementation, ★★, R1·R2)** Write `gn_manifold(X0, residuals, jacobians)`. Each iteration
must (a) build (2) from tangent-space Jacobians, (b) solve for $\delta$, and (c) retract
$X \leftarrow X \oplus \delta$.
*Rubric*: (a) the $\delta_i$ are never accumulated or compared (the code reflects that they are
fresh coordinates); (b) the stopping test looks at **both** $\lVert\delta\rVert$ and the cost
decrease; (c) $J$ is recomputed each iteration; (d) for a problem with gauge freedom it requires a
prior or a fixed pose and refuses explicitly if neither is given (rather than silently covering it
with damping).

**P6 (counterexample, ★★, R4·R5)** Construct an example in which damping (Levenberg-Marquardt)
**covers both kinds of null space** and makes diagnosis impossible. Propose a diagnostic procedure
that distinguishes the over-parameterisation null space from the gauge null space.
*Property checklist*: the diagnosis is to inspect the numerical rank and null-space basis of the
**undamped** coefficient matrix. An over-parameterisation null vector points along $q$ (one
dimension per variable), whereas a gauge null vector is a global direction **spanning all poses**
(six dimensions) — they are told apart by whether the support of the basis vector is local or global.

## Paper reading

**Two must-read papers.** Write a one-page note per paper against the ten fixed questions (the
lesson standard, §5).

1. **Absil, Mahony & Sepulchre, *Optimization Algorithms on Matrix Manifolds* (2008)** —
   role: `standard`. <https://doi.org/10.1515/9781400830244> (ch.4 and ch.7)
   Extra questions: (a) compare the authors' definition of a retraction with the conditions in this
   lesson — what is weaker or stronger? (b) state, following the authors' argument, why using an
   arbitrary retraction instead of a geodesic does not affect the **order** of convergence.
   (c) when is the trust-region version preferable to a line-search one?
2. **Dellaert & Kaess, "Factor Graphs for Robot Perception" (2017, FnT Robotics)** —
   role: `survey`. <https://doi.org/10.1561/2300000043> (§3-4)
   Extra questions: (a) summarise in one paragraph how this work exploits the sparsity of (2).
   (b) how does it say gauge freedom is handled in a real system (fixing? a prior? what is the
   difference?) (c) which equation becomes wrong if tangent-space Jacobians are not used?

## Reproduction task

**Tier R2 (re-implementation).** Budget: under five minutes on a laptop CPU, numpy/scipy only.

**Problem**: $SE(3)$ pose registration. From point correspondences $\{(a_i, b_i)\}$ generated by a
true transform $T^\star$ ($b_i = T^\star a_i + \text{noise}$, $N=200$), estimate $T$. The residual
is $e_i(T) = T a_i - b_i$.

1. **Manifold GN**: solve (2) with tangent-space Jacobians (6 columns) and retract
   $T \leftarrow T\,\mathrm{Exp}(\delta)$. With noise $\sigma = 0.01$ it must reach
   $\lVert\delta\rVert < 10^{-10}$ **within 10 iterations**.
2. **Over-parameterised comparison**: solve the same problem with 7 quaternion variables and a
   penalty $\mu$, reporting the iteration count for each $\mu \in \{10^{-2}, 1, 10^2\}$. **No value
   of $\mu$ should beat manifold GN** on iteration count. Also compare the smallest eigenvalue of
   the undamped coefficient matrix between the two formulations and show that the over-parameterised
   one is near zero.
3. **Jacobian correctness**: the tangent-space Jacobian agrees with a central finite difference to
   within $10^{-7}$. Also run a version that **approximates $J$ by $I$** (ignoring $J_r^{-1}$) and
   tabulate how the iteration count grows as the initial error increases (initial rotation error
   $0.1, 0.5, 1.5\,\mathrm{rad}$).
4. **Gauge diagnosis**: build a problem with two poses and one relative measurement between them,
   and confirm that the numerical rank of the undamped $\Lambda$ is $12 - 6 = 6$. Then add one
   prior and show the rank recovers to 12.

**Baseline**: where a closed form exists (point-correspondence registration), the Umeyama/Kabsch
solution and manifold GN must agree to within $10^{-9}$. If GTSAM can be installed, give it the
same problem and compare iteration counts (optional).

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| slow convergence when the initial error is large | $J_r^{-1}$ was omitted from $J$ | compare iteration counts against the $J=I$ version of condition 3 |
| the cost decreases but the answer differs each run | the gauge null space (R5) — no reference is fixed | inspect the numerical rank of the undamped $\Lambda$ and the support of its null-space basis |
| it only works with large damping | the over-parameterisation null space (R4) is being covered by damping | switch to a local parameterisation and check that it works with no damping |
| $\delta$ oscillates instead of shrinking | the $\delta_i$ were accumulated, or the retraction was skipped | check that $X$ really is updated each iteration and that $J$ is recomputed |

## Open problems

- **(Open) How far certifiable global optimality extends** — manifold GN is a local method. For
  pose graphs the tightness conditions of the dual relaxation are known
  ([SE-Sync](https://arxiv.org/abs/1612.07386) in `c5-robust-global-estimation`), but they do not
  extend to manifold least squares in general. A classification of which problem structures are
  certifiable is missing.
- **(Open) Non-smooth manifold optimization** — robust costs (Huber, truncated) and contact or
  combinatorial structure make the objective non-smooth. The convergence theory for non-smooth
  optimization on manifolds is less settled than the Euclidean case, and the IRLS and
  graph-pruning methods robotics uses are largely empirical.
- **(Open) Preconditioning on manifolds** — preconditioners exploiting sparsity are mature in the
  Euclidean setting, but there is no principled way to **reuse** a preconditioner when the tangent
  space changes every iteration. This is a practical bottleneck for large-scale bundle adjustment
  (`c7-bundle-adjustment`).

## Concept check

Run `rc quiz c1-manifold-optimization` (add `--lang en` for the English text). It is for concept
checking only; the real work is the problem set and the reproduction task.

The four items cover: the conditions for a retraction; the tangent-space Jacobian of a
$\mathrm{Log}$ residual; why over-parameterisation with a penalty is rank deficient; and the
dimension of the gauge null space of an $SE(3)$ pose graph.

## How to study this stage

1. **Burn in "a fresh coordinate every iteration" first (20 min)** — $\delta_i$ is a vector in a
   different coordinate system each iteration. Never add them, never compare them. Miss this line
   and the implementation is silently wrong.
2. **Confirm that (2) has the Euclidean form (40 min)** — the only difference is the definition of
   $J$. That is why sparse linear algebra and LM damping carry over unchanged. The feeling that
   matters is that this is **a change of coordinates, not a new theory**.
3. **Derive (4) by hand (50 min)** — the previous lesson's $J_r^{-1}$ is used here. Solve P1 and be
   able to say why it must be recomputed every iteration.
4. **Learn to tell the two null spaces apart (90 min)** — do both P4 and condition 4 of the
   reproduction task, and print the null-space basis of the undamped coefficient matrix yourself.
   **Local support means over-parameterisation; global support means gauge.** Without that
   distinction you will spend a career raising LM damping.
5. **Compare by iteration count (60 min)** — the table from condition 2 is this lesson's
   conclusion. The answer to "why bother with manifolds" arrives as a number: convergence speed.
6. **Read the papers at two levels (110 min)** — Absil et al. gives the theory of why an arbitrary
   retraction is acceptable; Dellaert & Kaess gives how that combines with sparsity in a real
   system. In both notes, write one paragraph on "which assumption of the theory breaks in practice".

**Passing bar**: you can write lift-solve-retract on a blank page, can derive (4), can state the
proof strategy of R3, can distinguish the two null spaces numerically, and have code meeting all
four acceptance conditions plus notes on both papers.
