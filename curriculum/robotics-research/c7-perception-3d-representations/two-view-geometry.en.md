---
id: c7-two-view-geometry
lang: en
title: Two-view geometry and the epipolar constraint
summary: >-
  Derive the epipolar constraint, the essential matrix and the fundamental matrix from scratch,
  and treat the characterisation of essential matrices (singular values $(\sigma,\sigma,0)$) at
  the level of proof. Builds the algebraic structure of the eight-point and five-point algorithms,
  and ends at the optimality and the bias of triangulation: why depth is overestimated on average,
  and why that average does not strictly exist.
objectives:
  - Derive the epipolar constraint and $E = \hat{t}R$ from coplanarity with no missing steps.
  - Reconstruct, as a proof sketch, why a real $3\times3$ matrix is essential exactly when its singular values are $(\sigma,\sigma,0)$.
  - Implement the eight-point linear system and the nearest-essential-matrix projection, and explain with numbers where Hartley normalisation helps and where it does nothing.
  - Explain why the five-point problem has at most ten solutions, from the monomial count and the action-matrix construction.
  - Show by a second-order expansion that linear triangulation overestimates depth on average, and explain why the inverse-depth parameterisation behaves differently.
tags: [perception, multi-view-geometry, epipolar-geometry, essential-matrix, triangulation, research]
---

# Two-view geometry and the epipolar constraint

## Setup and notation

This is the first lesson of module C7. The recommended prerequisites are
`c1-so3-se3-exponential` (exponential coordinates of rotation and the $\hat{\cdot}$ notation) and
`m4-camera-model-features` of the `robotics-expert` course (the pinhole model and calibration),
but neither is locked — if you pass the self-diagnosis below, start here. The following is assumed:

- Linear algebra: the SVD, singular values and condition numbers, null spaces, least squares,
  and sign manipulation of orthogonal matrices.
- Probability: expectation, Jensen's inequality, Gaussians, and the standard error of a Monte
  Carlo estimate.
- Projective geometry is used **as little as possible** — homogeneous coordinates and the meaning
  of "up to scale" suffice; things like the degree of a projective variety appear only as citations.

Notation (fixed for all of module C7; $\hat{\cdot}$ is the same as in module C1):

| Symbol | Meaning |
|---|---|
| $X \in \mathbb{R}^3$ | a 3D point; the subscript is the camera frame it is expressed in ($X_1$, $X_2$) |
| $\tilde{x} = (u, v, 1)^\top$ | homogeneous **pixel** coordinates |
| $K$ | the intrinsic matrix, $\tilde{x} = KX/Z$ |
| $x = K^{-1}\tilde{x}$ | **normalized image coordinates**, $x = X/Z$ |
| $(R, t)$ | relative pose: $R = {}^2R_1 \in SO(3)$, $t \in \mathbb{R}^3$, $X_2 = R X_1 + t$ |
| $\hat{t}$ | the skew-symmetric matrix of $t$, $\hat{t}a = t \times a$; the $[t]_\times$ of the vision literature |
| $E = \hat{t}R$ | the essential matrix, defined up to scale |
| $F = K_2^{-\top} E K_1^{-1}$ | the fundamental matrix |
| $e_1, e_2$ | the epipoles: $Ee_1 = 0$, $E^\top e_2 = 0$ |
| $\sigma_i(A)$ | singular values of $A$ in decreasing order |
| $\mathcal{E} \subset \mathbb{P}^8$ | the set of all essential matrices (the essential variety) |
| $d$, $\rho = 1/Z$ | disparity and inverse depth |

**Scale convention**: in the monocular two-view problem $\|t\|$ is not recoverable. Throughout
this lesson $\|t\| = 1$ is enforced, and errors are reported only as the **rotation error**
$\angle(R_{\text{gt}}^\top \hat{R})$ and the **translation direction error**
$\angle(t_{\text{gt}}, \hat{t})$.

## Self-diagnosis before starting

This is the first lesson of the module, so check your readiness first. **Prerequisite lessons are
not locked** — if you can solve all of the following, skip the recommended prerequisites. **If two
or more stop you**, going back to the lesson named in parentheses is faster.

1. For a distortion-free pinhole camera with $f = 500$ and principal point
   $(c_u, c_v) = (320, 320)$, what pixel does $X = (0.4, -0.2, 4.0)$ project to?
   (`m4-camera-model-features`)
   **Answer**: $u = 500 \cdot 0.4/4.0 + 320 = 370$, $v = 500 \cdot (-0.2)/4.0 + 320 = 295$.
2. For $t \ne 0$, what are the rank and the null space of $\hat{t}$? (`c1-so3-se3-exponential`)
   **Answer**: rank 2, null space $\operatorname{span}\{t\}$ (because $\hat{t}t = t \times t = 0$,
   and a skew-symmetric matrix in odd dimension has $\det \hat{t} = 0$).
3. For $A \in \mathbb{R}^{n \times 9}$, what is the value of
   $\min_{\lVert e \rVert = 1} \lVert Ae \rVert$ and where is it attained?
   (`r0-linear-algebra-decompositions`)
   **Answer**: the value is $\sigma_9(A)$, attained at the corresponding **right singular vector**.
   Tolerance in a numerical check: $10^{-12}$.
4. For a positive, non-constant random variable $X$ and $g(x) = 1/x$, compare
   $\mathbb{E}[g(X)]$ with $g(\mathbb{E}[X])$, with the direction of the inequality.
   (`r0-estimation-theory`)
   **Answer**: $1/x$ is strictly convex on $x > 0$, so Jensen's inequality gives
   $\mathbb{E}[1/X] > 1/\mathbb{E}[X]$, with equality only for constant $X$.
5. How many degrees of freedom does a $3\times3$ matrix defined up to scale have, and how many
   after imposing $\det = 0$? (`r0-linear-algebra-decompositions`)
   **Answer**: $9 - 1 = 8$, and $7$ after $\det = 0$. (That 7 is the DOF count of $F$.)

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the epipolar constraint and the essential matrix) [D2]** — two normalized image points
  $x_1, x_2$ of the same 3D point satisfy, independently of depth,
  $$x_2^\top E x_1 = 0, \qquad E = \hat{t}R \tag{1}$$
  and in pixels $\tilde{x}_2^\top F \tilde{x}_1 = 0$ with $F = K_2^{-\top} E K_1^{-1}$.
  The epipoles are $e_1 \propto R^\top t$ and $e_2 \propto t$, and the epipolar lines are
  $l_2 = Ex_1$, $l_1 = E^\top x_2$.
- **R2 (characterisation of essential matrices, and DOF) [D3]** — for $E \ne 0$ the following are
  equivalent: (i) $E = \hat{t}R$ for some $R \in SO(3)$ and $t \ne 0$; (ii) the singular values of
  $E$ are $(\sigma, \sigma, 0)$ with $\sigma > 0$; (iii) the algebraic condition
  $$2EE^\top E - \operatorname{tr}(EE^\top)\,E = 0. \tag{2}$$
  Hence $\mathcal{E}$ is a **five-dimensional** variety in $\mathbb{P}^8$: $E$ has 5 degrees of
  freedom and $F$ has 7. The nine scalar equations of (2) have rank 3 at a generic point of
  $\mathcal{E}$.
- **R3 (the eight-point algorithm and the nearest essential matrix) [D2]** — (1) is linear in
  $\operatorname{vec}(E)$, so $n \ge 8$ correspondences give $A\mathbf{e} = 0$ with row $i$ of $A$
  equal to $(x_{2}^{(i)} \otimes x_{1}^{(i)})^\top$. The right singular vector of $\sigma_9$ is
  the least-squares solution, and the **Frobenius-nearest essential matrix** is then
  $$\hat{E} = U \operatorname{diag}(\bar{\sigma}, \bar{\sigma}, 0) V^\top, \qquad
    \bar{\sigma} = \tfrac{1}{2}(\sigma_1 + \sigma_2) \tag{3}$$
  where $E = U\Sigma V^\top$ is the SVD of the least-squares solution.
- **R4 (how many solutions the five-point problem has) [D2]** — five correspondences leave a
  four-dimensional null space in $\operatorname{vec}(E)$. Imposing (2) and $\det E = 0$ inside it
  gives ten cubics in three unknowns, and since there are twenty monomials of degree $\le 3$, the
  elimination on the $10 \times 20$ coefficient matrix closes into an **action matrix** on a
  ten-dimensional quotient space. The problem therefore has **at most ten** solutions, and exactly
  ten (counting complex ones) in a generic configuration. Each $E$ yields four $(R, t)$
  decompositions, exactly one of which satisfies chirality.
- **R5 (optimality and bias of triangulation) [D3]** — under isotropic Gaussian image noise the
  maximum-likelihood (ML) triangulation minimises the reprojection error, and for two views it
  closes in a degree-six polynomial (Hartley–Sturm). But **no depth estimator is unbiased**: in a
  rectified stereo pair $\hat{Z} = fb/\hat{d}$ satisfies
  $$\mathbb{E}[\hat{Z}] = Z\left(1 + \frac{\sigma_d^2}{d^2}\right) + O\!\left(\frac{\sigma_d^4}{d^4}\right) \tag{4}$$
  so depth is **overestimated**, whereas the inverse depth $\hat{\rho} = \hat{d}/(fb)$ is exactly
  unbiased. More sharply: if the noise really is Gaussian then $\mathbb{E}[\hat{Z}]$ **does not
  exist** (the integral diverges) — (4) is a statement about a tail-truncated conditional
  expectation. **[D3]**

## Derivation

### R1 — the epipolar constraint

In the pinhole model the normalized coordinates are $x_i = X_i / Z_i$, so $X_i = Z_i x_i$ with
$Z_i > 0$. Substituting into the rigid motion $X_2 = R X_1 + t$,

$$Z_2 x_2 = Z_1 R x_1 + t. \tag{5}$$

Eliminating the depths $Z_1, Z_2$ is the whole derivation. Multiplying from the left by $\hat{t}$
and using $\hat{t}t = 0$,

$$Z_2\,\hat{t}x_2 = Z_1\,\hat{t}Rx_1.$$

Now multiply from the left by $x_2^\top$. Since $\hat{t}$ is skew-symmetric, $a^\top \hat{t} a = 0$
for every $a$, and the left-hand side vanishes:

$$0 = Z_1\, x_2^\top \hat{t} R x_1.$$

With $Z_1 \ne 0$ this is (1). **No step was skipped** — all that was used is the pair of
identities $\hat{t}t = 0$ and $a^\top\hat{t}a = 0$.

**Geometric reading**: (1) is the triple product $x_2 \cdot (t \times Rx_1) = 0$, that is, the
baseline $t$ and the two viewing rays are **coplanar**; the parallelepiped they span has zero
volume. That plane is the epipolar plane, and its intersections with the images are the epipolar
lines.

**Epipoles**: $Ev = 0 \iff \hat{t}(Rv) = 0 \iff Rv \parallel t \iff v \propto R^\top t$, so
$e_1 \propto R^\top t$. And $E^\top w = R^\top\hat{t}^\top w = 0 \iff \hat{t}w = 0 \iff w \propto t$,
so $e_2 \propto t$. Physically $e_1$ is the **projection of camera 2's centre into image 1**: that
centre is $-R^\top t$ in frame 1, which lies on the same line as $R^\top t$.

**In pixels**: substituting $x_i = K_i^{-1}\tilde{x}_i$ into (1) gives
$\tilde{x}_2^\top K_2^{-\top} E K_1^{-1} \tilde{x}_1 = 0$, that is, $F = K_2^{-\top}EK_1^{-1}$.
Since $K$ is invertible, $\operatorname{rank}F = \operatorname{rank}E = 2$, but **the singular
values of $F$ are not those of $E$** — $K$ mixes in an anisotropic scaling. That fact leads
directly to the failure mode of R2 and to the normalisation discussion of the eight-point
algorithm.

**Where the assumptions break**: if $t = 0$ (pure rotation) then $E = 0$ and (1) holds for
**every** correspondence — the constraint is vacuous and the relative rotation cannot be recovered
from $E$. One has to use the infinite homography $\tilde{x}_2 = K_2 R K_1^{-1}\tilde{x}_1$ instead.
Points with $Z_1 = 0$ (at the camera centre) are excluded, and $\|t\|$ is **unrecoverable**
because (1) is invariant to the scale of $E$ (the monocular scale ambiguity).

### R3 — the eight-point algorithm

Since $x_2^\top E x_1 = \sum_{i,j} E_{ij}\, x_{2,i}\, x_{1,j}$, writing $E$ row-major as
$\mathbf{e} = \operatorname{vec}(E) \in \mathbb{R}^9$ gives

$$x_2^\top E x_1 = (x_2 \otimes x_1)^\top \mathbf{e} = 0 \tag{6}$$

with $\otimes$ the Kronecker product. Stacking $n$ correspondences yields
$A \in \mathbb{R}^{n\times9}$ and $A\mathbf{e} = 0$. In a generic configuration with $n = 8$,
$\operatorname{rank}A = 8$ and the null space is one-dimensional. Under noise no exact null vector
exists, so one solves

$$\mathbf{e}^\star = \arg\min_{\lVert \mathbf{e}\rVert = 1} \lVert A\mathbf{e}\rVert.$$

Writing $A = U_A\Sigma_A V_A^\top$, we have $\lVert A\mathbf{e}\rVert^2 = \sum_k \sigma_k^2 c_k^2$
with $c = V_A^\top\mathbf{e}$, $\lVert c\rVert = 1$, so the minimum is at $c = e_9$: that is,
$\mathbf{e}^\star$ is the right singular vector of $\sigma_9$.

The resulting $E^\star$ has generic singular values $(\sigma_1, \sigma_2, \sigma_3)$ and is
therefore **not an essential matrix**. It must be projected onto the $(\bar\sigma, \bar\sigma, 0)$
spectrum that R2 demands, and that projection is (3). By Mirsky's theorem (among matrices with a
fixed set of singular values, the Frobenius-nearest one to $A$ shares $A$'s singular vectors),

$$\min_{\substack{\text{singular values } (\sigma,\sigma,0)}} \lVert E^\star - B \rVert_F^2
  = (\sigma_1 - \sigma)^2 + (\sigma_2 - \sigma)^2 + \sigma_3^2 \tag{7}$$

and differentiating in $\sigma$ gives $-2(\sigma_1-\sigma) - 2(\sigma_2-\sigma) = 0$, that is,
$\sigma = \bar\sigma = (\sigma_1+\sigma_2)/2$. The minimum value is
$\tfrac{1}{2}(\sigma_1-\sigma_2)^2 + \sigma_3^2$, and that number is itself **a measure of how
well the data fits the calibrated two-view model** — a cheap diagnostic for degenerate
configurations and calibration errors.

**Coordinate normalisation (Hartley)**: the columns of $A$ are products $x_{2,i}x_{1,j}$ and so
carry the **square** of the coordinate scale. In pixels ($u \sim 10^3$) the same matrix holds
entries of size $u_2u_1 \sim 10^6$ next to entries of size $1$, and the condition number explodes.
Hartley's recipe is to apply, in each image, the similarity $T_i$ that moves the centroid to the
origin and scales the mean distance to $\sqrt{2}$, solve with $y_i = T_ix_i$, and undo it at the
end with $F = T_2^\top F_y T_1$.

Measured in this lesson (the scene generator of the reproduction task, 8 points, pixel noise
$\sigma = 1$px, 200 trials):

| | median $\operatorname{cond}(A)$ | median rotation error | p90 rotation error |
|---|---|---|---|
| $F$, pixels, normalisation **on** | $3.8\times10^{2}$ | $4.22^\circ$ | $10.42^\circ$ |
| $F$, pixels, normalisation **off** | $9.8\times10^{5}$ | $4.99^\circ$ | $16.35^\circ$ |
| $E$, normalized coordinates, on/off | identical | $4.61^\circ$ | $12.89^\circ$ |

Two things to read off. (1) The condition number improves by a factor of 2600 but the median error
improves by only 15% — the benefit of normalisation lives in the **tail** (p90 improves by 36%).
(2) **If you solve for $E$ directly in normalized coordinates, Hartley normalisation has nothing
to do**, because the entries of $x$ are already $O(1)$. The textbook advice "always normalise for
the eight-point algorithm" is advice about **$F$ in pixels**, and carrying it over to a calibrated
$E$ is wrong.

**Where the assumptions break**: if the 3D points lie **on a plane** then
$\operatorname{rank}A = 6$, the null space is three-dimensional, and the set of $F$ satisfying (1)
is the whole three-parameter family $F = \hat{e}_2 H + e_2 a^\top$, with $H$ the homography induced
by that plane. The singular vector of $\sigma_9$ picks an **arbitrary member** of that family, and
the projection (3) faithfully turns it into an essential matrix — the rotation error survives even
at zero noise (measured: $4.95^\circ$ with 20 coplanar points). Pure rotation ($t = 0$) fails the
same quiet way. Neither is **detectable from the residual**, which stays small; to detect them one
has to look at $\sigma_7(A)/\sigma_6(A)$ (measured: of order $10^{-15}$ in the coplanar case).

### R4 — the algebraic structure of the five-point problem

Five correspondences give $A \in \mathbb{R}^{5\times9}$ in (6), whose null space is
four-dimensional in a generic configuration. With a basis $E_1, \dots, E_4$, every candidate is

$$E(x,y,z,w) = xE_1 + yE_2 + zE_3 + wE_4 \tag{8}$$

and, by scale invariance, $w = 1$ may be imposed. (That branch misses solutions with $w = 0$, but
those form a measure-zero set corresponding to a hyperplane of the null space; an implementation
retries with a permuted basis.)

Substituting (8) into (2) makes each component a (non-homogeneous) **cubic** polynomial in
$(x,y,z)$, since $E$ is linear and $EE^\top E$ is cubic; $\det E = 0$ is cubic as well. That gives
**ten** cubics in three unknowns. The number of monomials of degree $\le 3$ is
$\binom{3+3}{3} = 20$:

$$\{x^3, x^2y, x^2z, xy^2, xyz, xz^2, y^3, y^2z, yz^2, z^3\} \cup
  \{x^2, xy, xz, y^2, yz, z^2, x, y, z, 1\}.$$

Put the ten cubic monomials on the left and the other ten on the right, form the coefficient matrix
$M \in \mathbb{R}^{10\times20}$ and run Gauss–Jordan elimination on the left block to get
$[\,I_{10} \mid B\,]$. In other words, **every cubic monomial becomes a linear combination of the
ten lower-degree ones**. The quotient $\mathbb{R}[x,y,z]/I$ then has the basis
$\{x^2, xy, xz, y^2, yz, z^2, x, y, z, 1\}$ (ten-dimensional), and "multiply by $x$" is written in
that basis as a $10\times10$ matrix $A_x$, the action matrix. Each solution
$(x^\star, y^\star, z^\star)$ gives a monomial vector $v^\star$ with
$A_x v^\star = x^\star v^\star$, so **the solutions are read off as the eigenvalues and
eigenvectors of $A_x$**. Being $10\times10$, it admits at most ten solutions.

Nistér 2004 goes one step further and organises the elimination by hand down to **a single
degree-ten univariate polynomial** (§3–4), which is faster than an eigendecomposition. Stewénius
et al. 2006 report that the action-matrix form above is numerically more stable and far shorter to
implement. Both reach the same bound of ten, which agrees with the fact that $\mathcal{E}$ is a
five-dimensional variety of degree 10 in $\mathbb{P}^8$ while five linear constraints cut
$\mathbb{P}^8$ down to $\mathbb{P}^3$ (Demazure; see MVG ch.11.6 **[D0]**).

**Down to $(R,t)$**: the construction of R2 gives four pairs from each $E$, namely $(R, \pm t)$ and
$(R', \pm t)$ with $R' = UWV^\top$ against $UW^\top V^\top$. Exactly one of the four puts the point
at **positive depth in both views** (chirality). The depths come from solving (5) as
$[\,Rx_1 \;\; -x_2\,] (Z_1, Z_2)^\top = -t$.

**Where the assumptions break**: (1) five coplanar points admit a planar ambiguity — the true
solution is still among the candidates (measured: rotation error $0.00^\circ$) but is not unique,
so it cannot be selected without scoring (RANSAC). (2) Five points on a **critical surface** (a
ruled quadric through both camera centres) make several solutions geometrically valid
(MVG ch.22.2 **[D0]**). (3) As $t \to 0$ we get $E \to 0$ and the null-space computation itself
becomes meaningless. (4) The $w = 0$ branch above — rare, but an implementation needs the retry.

### R5 — triangulation: three estimators and the depth bias

**Linear (DLT)**: in each view two of the three equations of $x \times (P X) = 0$ are independent,
so two views give $A \in \mathbb{R}^{4\times4}$ and $AX = 0$, solved by the singular vector of
$\sigma_4$. This minimises the algebraic error $\lVert AX\rVert$ and **not the reprojection
error** — the answer changes with the normalisation of the homogeneous coordinates.

**ML (reprojection error)**: for isotropic Gaussian image noise the negative log-likelihood is

$$\min_{\hat{x}_1, \hat{x}_2} \lVert x_1 - \hat{x}_1\rVert^2 + \lVert x_2 - \hat{x}_2\rVert^2
  \quad \text{s.t.}\quad \hat{x}_2^\top F \hat{x}_1 = 0. \tag{9}$$

Hartley and Sturm parameterised the pencil of epipolar lines in image 1 by a single $s$, turned (9)
into a rational function of $s$, and showed that setting the derivative to zero gives a
**degree-six polynomial**, so the problem closes in closed form. In practice one uses the
first-order Sampson distance

$$\delta_{\text{Samp}} = \frac{x_2^\top Fx_1}
  {\sqrt{(Fx_1)_1^2 + (Fx_1)_2^2 + (F^\top x_2)_1^2 + (F^\top x_2)_2^2}} \tag{10}$$

which is one Newton step onto the constraint.

**Bias**: narrow to a rectified stereo pair with focal length $f$, baseline $b$ and disparity
$d = fb/Z$. If the position noise in each image is $N(0,\sigma_p^2)$ then $\hat{d} = d + \epsilon$
with $\sigma_d^2 = 2\sigma_p^2$, and $\hat{Z} = fb/\hat{d}$. For $\lvert\epsilon\rvert < d$ the
Laurent expansion

$$\frac{1}{d+\epsilon} = \frac{1}{d}\left(1 - \frac{\epsilon}{d} + \frac{\epsilon^2}{d^2}
  - \frac{\epsilon^3}{d^3} + \cdots\right)$$

taken in expectation with $\mathbb{E}[\epsilon] = 0$, $\mathbb{E}[\epsilon^2] = \sigma_d^2$ and
$\mathbb{E}[\epsilon^3] = 0$ gives (4). The relative bias is
$\sigma_d^2/d^2 = (\sigma_d Z/(fb))^2$, which **grows with the square of depth**. By contrast

$$\hat{\rho} = \frac{\hat{d}}{fb} = \rho + \frac{\epsilon}{fb}$$

is an **affine** function of $\hat{d}$, hence exactly unbiased and exactly Gaussian. That is why
SLAM and bundle adjustment parameterise points by inverse depth. And since $1/x$ is monotone
decreasing on $x > 0$, **the median is preserved exactly**:
$\operatorname{med}(\hat{Z}) = fb/\operatorname{med}(\hat{d}) = Z$.

Measured (Monte Carlo with $2\times10^6$ samples, $f=500$, $b=0.5$, conditioned on $\hat{d}>0$):

| $Z$ | $d$ | predicted $\sigma_d^2/d^2$ | measured relative bias | median error |
|---|---|---|---|---|
| 5 | 50.0 | $+0.08\%$ | $+0.08\%$ | $-0.00\%$ |
| 20 | 12.5 | $+1.28\%$ | $+1.35\%$ | $+0.02\%$ |
| 50 ($\sigma_p = 0.5$) | 5.0 | $+2.00\%$ | $+2.15\%$ | $+0.01\%$ |
| 50 ($\sigma_p = 1.0$) | 5.0 | $+8.00\%$ | $+12.72\%$ | $+0.01\%$ |

The last row is where the second-order expansion collapses: $\sigma_d/d = 0.28$, so the
higher-order terms of the Laurent series are no longer small. The median is unbiased in all four
cases.

**Where the assumptions break**: if the noise really is Gaussian then the support of $\hat{d}$
contains 0 and $\int \frac{1}{x}N(x; d, \sigma_d^2)\,dx$ diverges near $x = 0$ — that is,
**$\mathbb{E}[\hat{Z}]$ does not exist**. The table above is a conditional expectation truncated at
$\hat{d} > 0$, and moving the truncation moves the number. In the same setting, truncating at
$\hat{d} > 3\sigma_d$ turns the bias at $Z = 50$ from $+8\%$ into $-9.68\%$ (30% of the samples are
discarded, and what gets discarded is the large depths). **The sentence "triangulation is biased"
means nothing until you say which estimator and which tail handling.** When a paper reports a bias
number, the first question is how the tail was handled.

## Proof sketch

### R2 — characterisation of essential matrices

**Hypotheses** H1: $E \in \mathbb{R}^{3\times3}$, $E \ne 0$.
**Conclusion** C: (i) $\exists R \in SO(3), t \ne 0: E = \hat{t}R$ $\iff$ (ii) the singular values
are $(\sigma,\sigma,0)$ with $\sigma>0$ $\iff$ (iii) equation (2).

**Strategy**: (i)$\Rightarrow$(ii) is a spectral computation on $EE^\top$. (ii)$\Rightarrow$(i)
fixes the signs of the SVD so that both factors lie in $SO(3)$ and then factors
$\operatorname{diag}(1,1,0)$ as "rotation times skew". (ii)$\iff$(iii) is algebra on the diagonal.

1. **(i)$\Rightarrow$(ii)**: $EE^\top = \hat{t}RR^\top\hat{t}^\top = \hat{t}\hat{t}^\top
   = -\hat{t}^2 = \lVert t\rVert^2 I - tt^\top$. The eigenvalues of this symmetric matrix are 0
   along $t$ and $\lVert t\rVert^2$ on $t^\perp$ (multiplicity 2). So the singular values of $E$
   are $(\lVert t\rVert, \lVert t\rVert, 0)$.
2. **(ii)$\Rightarrow$(i)**: let $E = U\Sigma V^\top$ with
   $\Sigma = \operatorname{diag}(\sigma,\sigma,0)$. Flipping the sign of the third column of $U$
   leaves $E$ unchanged, because $\Sigma_{33} = 0$, and flips the sign of $\det U$; the same holds
   independently for $V$. So we may assume $U, V \in SO(3)$. Now put $Z = \hat{e}_3$ and
   $W = \exp(\hat{e}_3\pi/2) \in SO(3)$ and verify by direct multiplication that
   $$ZW^\top = \operatorname{diag}(1,1,0). \tag{11}$$
   Then $\Sigma = \sigma ZW^\top$ and
   $$E = \sigma\,U Z W^\top V^\top = \sigma\,(UZU^\top)(UW^\top V^\top).$$
   By the identity $R\hat{a}R^\top = \widehat{Ra}$ of module C1,
   $UZU^\top = U\hat{e}_3U^\top = \widehat{Ue_3} = \hat{u}_3$ with $u_3$ the third column of $U$,
   and $R := UW^\top V^\top \in SO(3)$. Hence $E = \hat{t}R$ with $t = \sigma u_3$. $\square$
   (By-product: using $W$ instead of $W^\top$, or $-t$ instead of $t$, gives the same $E$, so there
   are **exactly four** decompositions.)
3. **(ii)$\Rightarrow$(iii)**: substituting $E = U\Sigma V^\top$ into (2) gives
   $2EE^\top E - \operatorname{tr}(EE^\top)E = U\big(2\Sigma^3 - (\textstyle\sum_j\sigma_j^2)\Sigma\big)V^\top$,
   whose bracket is diagonal with $i$-th entry
   $\sigma_i(2\sigma_i^2 - \sum_j \sigma_j^2)$. For $(\sigma,\sigma,0)$ the entries are
   $\sigma(2\sigma^2 - 2\sigma^2) = 0$ for $i = 1,2$ and $0$ for $i = 3$, so (2) holds.
4. **(iii)$\Rightarrow$(ii)**: for every $i$, either $\sigma_i = 0$ or
   $2\sigma_i^2 = \sum_j\sigma_j^2$. Suppose no singular value vanishes: then $2\sigma_i^2$ is
   independent of $i$, so $\sigma_1=\sigma_2=\sigma_3=\sigma$ and $2\sigma^2 = 3\sigma^2$ forces
   $\sigma = 0$, contradicting $E \ne 0$ (H1). So at least one vanishes and we may take
   $\sigma_3 = 0$. Among $i = 1,2$, each non-zero one must satisfy
   $2\sigma_i^2 = \sigma_1^2+\sigma_2^2$, hence $\sigma_1 = \sigma_2$. $\square$
   (Note: (2) alone implies $\det E = 0$, so it need not be imposed separately.)
5. **Degrees of freedom**: $(R,t)$ has 6 parameters and $E$ is scale-invariant, so
   $\dim\mathcal{E} = 5$. As $\mathbb{P}^8$ has dimension 8, $\mathcal{E}$ has codimension 3 and
   the nine equations of (2) have **rank 3** at a generic point (problem P2). That is the precise
   reason five points suffice: each correspondence gives one linear constraint, and
   $8 - 3 = 5$.
6. **Remove a hypothesis**: drop "two singular values are equal" from (ii) and ask only for rank 2,
   and what is left is the variety of fundamental matrices (dimension 7). That is exactly what the
   seven-point algorithm solves with $\det F = 0$ alone, and the $(R,t)$ extracted from it is **not
   a Euclidean reconstruction** — an anisotropic (affine) deformation remains. Estimating $F$ from a
   calibrated pair and then using $K^\top F K$ as $E$ loses accuracy for this reason. Dropping H1
   ($E \ne 0$) instead breaks the contradiction in step 4, and (2) holds trivially at $E = 0$ —
   which is precisely the case of pure rotation.

Steps left out: Mirsky's theorem (Frobenius-nearest matrix with a fixed spectrum) and the direct
multiplication in (11). The first is a standard matrix-approximation result and the second is three
lines by hand — both are in the problem set.

### R5 — bias of the depth estimator

**Hypotheses** H1: $f, b$ are known exactly and the stereo pair is rectified. H2:
$\hat{d} = d + \epsilon$ with $\epsilon \sim N(0,\sigma_d^2)$ and $d > 0$. H3: the estimator is
$\hat{Z} = fb/\hat{d}$.
**Conclusions** C1: $\mathbb{E}[\hat{Z}]$ does not exist. C2: under a symmetric truncation
$\lvert\epsilon\rvert \le \delta < d$, $\mathbb{E}[\hat{Z}] > Z$ and (4) holds. C3: $\hat{\rho}$ is
unbiased. C4: $\operatorname{med}(\hat{Z}) = Z$ exactly.

**Strategy**: C1 is divergence of an integral, C2 is Jensen plus the Laurent expansion, C4 is
preservation of quantiles under a monotone map.

1. **C1**: as $x \to 0$ we have $N(x;d,\sigma_d^2) \to c > 0$ and
   $\int_{-\eta}^{\eta}\lvert 1/x\rvert\,dx = \infty$, so $\mathbb{E}\lvert\hat{Z}\rvert = \infty$.
   The principal value exists, but it is not an expectation.
2. **C2**: the truncated law is symmetric about $d$, so $\mathbb{E}[\hat{d}] = d$ holds
   **exactly**. Since $1/x$ is strictly convex on $(d-\delta, d+\delta) \subset (0,\infty)$,
   Jensen gives $\mathbb{E}[1/\hat{d}] > 1/\mathbb{E}[\hat{d}] = 1/d$, i.e. $\mathbb{E}[\hat{Z}] > Z$.
   Its size is $Z\sigma_d^2/d^2 + O(\sigma_d^4/d^4)$ by the Laurent expansion above.
3. **C3**: $\hat{\rho}$ is affine in $\hat{d}$, so $\mathbb{E}[\hat\rho] = \rho$ (and this survives
   a symmetric truncation).
4. **C4**: $\hat{d} \mapsto fb/\hat{d}$ is monotone (decreasing) on $\hat{d} > 0$, and monotone maps
   preserve quantiles; a symmetric law has $\operatorname{med}(\hat d) = d$, which gives C4.
5. **Remove a hypothesis**: drop the symmetric truncation in H2 and step 2 loses
   "$\mathbb{E}[\hat d] = d$". Truncating on one side only (say $\hat{d} > 3\sigma_d$) deletes the
   large depths and **flips the sign of the bias** (measured: $+8\%$ becomes $-9.68\%$ at $Z=50$,
   $\sigma_p=1$). So the "overestimation" of C2 does not hold without a statement about the tail —
   this one paragraph is what separates the common summary ("$1/d$ is convex, so depth is
   overestimated") from what actually happens.

Step left out: the second-order bias of the $N$-view ML estimator (the correction term involving
the inverse Fisher information). See the analysis in Lee & Civera 2019 and its references.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R1)** Derive $e_1 \propto R^\top t$ and $e_2 \propto t$, and show that the
epipolar line $l_2 = Ex_1$ passes through $e_2$ for every $x_1$. Also confirm that the epipoles of
$F$ are $\tilde{e}_i = K_ie_i$.
*Solution sketch*: $e_2^\top l_2 = e_2^\top E x_1 = (E^\top e_2)^\top x_1 = 0$. For the epipoles,
reduce the condition $Ev = \hat{t}(Rv) = 0$ to the null space of $\hat{t}$ (self-diagnosis item 2).

**P2 (proof, ★★★, R2)** Show that the nine scalar equations of (2) have **rank 3** at a generic
point of $\mathcal{E}$: that is, prove that the Jacobian
$D\Phi(E) \in \mathbb{R}^{9\times9}$ of $\Phi(E) = 2EE^\top E - \operatorname{tr}(EE^\top)E$ has
rank 3 at $E = \hat{t}R \in \mathcal{E}$.
*Strategy and key inequality*: one may fix coordinates so that $E = \sigma \hat{e}_3$ without loss
of generality, since $\Phi$ is equivariant under left and right rotations. At that point write
$D\Phi$ in $3\times3$ blocks, show that the tangent space of $\mathcal{E}$ (dimension 5) lies in
the kernel, and then exhibit three explicit perturbations $\delta E$ whose images are independent.
The bound $\operatorname{rank} D\Phi = 9 - \dim\ker \le 9 - 5 - 1$ (the scale direction) gives the
upper bound 3.

**P3 (numerical, ★, R2·R3)** Project the following matrix onto the Frobenius-nearest essential
matrix.
$$
\tilde{E} = \begin{bmatrix} 0 & -0.30 & 0.10 \\ 0.25 & 0 & -0.90 \\ -0.05 & 0.95 & 0 \end{bmatrix}
$$
*Answer*: singular values $(0.99885152,\ 0.93791041,\ 0.01094111)$,
$\bar\sigma = 0.96838096$, $\lVert \tilde{E} - \hat{E}\rVert_F = 0.04445917$, and
$$
\hat{E} = \begin{bmatrix}
 -0.01059627 & -0.29092379 & 0.09748319 \\
  0.25713039 & -0.00816323 & -0.92832907 \\
 -0.05402725 & 0.92212401 & 0.00789420 \end{bmatrix}.
$$
Tolerance $10^{-7}$. Check: the singular values of $\hat{E}$ are $(\bar\sigma, \bar\sigma, 0)$, the
residual of (2) satisfies
$\lVert 2\hat{E}\hat{E}^\top\hat{E} - \operatorname{tr}(\hat{E}\hat{E}^\top)\hat{E}\rVert_F < 10^{-14}$,
and $\lVert\tilde{E}-\hat{E}\rVert_F^2$ agrees with
$\tfrac12(\sigma_1-\sigma_2)^2 + \sigma_3^2$.

**P4 (numerical, ★★, R4)** Let $R$ be a $20^\circ$ rotation about the $y$ axis, $t = (1,0,0)^\top$
and $E = \hat{t}R$. For the correspondence $x_1 = (0.075, -0.05, 1)^\top$,
$x_2 = (0.72480010, -0.05470213, 1)^\top$, compute all four $(R,t)$ decompositions of $E$ and
single out the one satisfying chirality **by the numerical values of the two depths**.
*Answer*: the four candidates have rotation errors $(180^\circ, 180^\circ, 0^\circ, 0^\circ)$ and
depths $(-0.930238, +0.850275)$, $(+0.930238, -0.850275)$, $(+4.000000, +3.656164)$,
$(-4.000000, -3.656164)$. The third passes, i.e. $R' = UW^\top V^\top$ with $t = +u_3$ and
$(Z_1, Z_2) = (4.000000, 3.656164)$. Tolerance $10^{-5}$. Check: map $Z_1x_1$ through $(R,t)$ and
confirm it agrees with $Z_2x_2$ to within $10^{-10}$.

**P5 (implementation, ★★, R3)** Write the eight-point algorithm for $F$ in pixel coordinates in two
versions, with and without Hartley normalisation, and compare $\operatorname{cond}(A)$ and the
rotation error using the scene generator of the reproduction task.
*Rubric*: (a) the median $\operatorname{cond}(A)$ without normalisation is at least $10^3$ times
the one with it; (b) the p90 rotation error improves by at least 20% with normalisation; (c) you
show numerically that **solving for $E$ directly in normalized coordinates makes no difference**;
(d) the undoing transform $F = T_2^\top F_y T_1$ is present and you explain in one line why it is
$T_2^\top$.

**P6 (counterexample, ★★, R3·R4)** Construct a set of correspondences on which the eight-point
algorithm returns a wrong pose **at zero noise**. Exhibit $\operatorname{rank}A$ through the
singular values, and run the five-point solver on five of the same points to confirm that the true
solution is among the candidates.
*Property checklist*: (a) all 3D points lie on one plane; (b) $\sigma_7(A)/\sigma_6(A) < 10^{-8}$
(a three-dimensional null space); (c) the epipolar residual is small while the rotation error
exceeds $1^\circ$; (d) the minimum rotation error of the five-point solver is at most $10^{-6}$
rad; (e) the same phenomenon can be produced with pure rotation ($t = 0$).

**P7 (numerical, ★, R5)** For $f = 500$, $b = 0.5$, $\sigma_p = 1$px and $Z = 20$m, predict the
relative bias of $\hat{Z}$ from (4) and confirm it by Monte Carlo ($N \ge 10^6$). Measure the bias
of $\hat{\rho}$ and of the median in the same setting.
*Answer*: $d = 12.5$px, $\sigma_d = \sqrt{2}$px, prediction $\sigma_d^2/d^2 = 2/156.25 = +1.28\%$,
measured $+1.35\%$ (tolerance: $\pm30\%$ of the prediction). The relative bias of
$\mathbb{E}[\hat\rho]$ is $< 0.05\%$ and that of the median is $< 0.1\%$. Check: truncating the
samples at $\hat{d} > 3\sigma_d$ must change the number — if it does not, $N$ is too small or the
tail was already discarded.

**P8 (paper, ★★, R4)** Read Nistér 2004 and find **three pieces of information that are missing**
if you try to reproduce the method of §3–4 from the paper alone. Then compare it with the
action-matrix solver of Stewénius et al. 2006 and choose, with reasons, which one you would
implement.
*Rubric*: naming something **specific** — the exact monomial ordering, the pivot choice and
numerical scaling in the elimination, or the selection rule among the roots of the degree-ten
polynomial (real roots, chirality, degeneracy handling) — passes. "There is no code" alone fails.

## Paper reading

**Two must-reads.** Write a one-page note on each, using the ten fixed questions
(`lesson-standard.md` §5). Read in three passes, and attack questions 4, 5, 6 and 7 in the third.
For the full bibliography, including the recommended papers, run
`rc papers c7-two-view-geometry` (the course registry
`curriculum/robotics-research/papers.yaml`, ADR 0014).

1. **Longuet-Higgins, "A computer algorithm for reconstructing a scene from two projections"
   (1981, Nature)** — role: `seminal`. <https://doi.org/10.1038/293133a0>
   Two pages. R1 and R3 of this lesson both come from here.
   Extra questions: (a) the author's linear method has neither the singular-value constraint of R2
   nor any coordinate normalisation. Why was that not a problem in 1981, and why is it one now?
   (b) How is chirality handled in the pose-recovery step?
2. **Nistér, "An efficient solution to the five-point relative pose problem" (2004, T-PAMI)** —
   role: `standard`. <https://doi.org/10.1109/TPAMI.2004.17> (§3–4 is the core.)
   Extra questions: (a) in the reported experiments, which condition (field of view, baseline,
   number of points) does the margin of five-point over eight-point depend on most? (b) How does
   selecting the physically valid root among the ten enter the cost inside RANSAC? (c) What changes
   when the conclusions are applied to a planar scene (contrast with the failure mode in R4)?

**The ten fixed questions**: (1) which problem under which assumptions; (2) what exactly earlier
work could not do; (3) the core idea in one equation; (4) what is guaranteed and **what is not**;
(5) the independent and dependent variables and the baselines, fairly tuned or not; (6) whether the
metric matches the claim, and whether variance and seeds are reported; (7) what is missing for
reproduction; (8) the first assumption to doubt if the result were wrong; (9) time and memory
complexity and real-time behaviour; (10) what you would change to go beyond it in a year.

**Recommended**: Huang & Faugeras 1989 (the origin of R2, two and a half pages), Hartley 1997
(normalisation), Hartley & Sturm 1997 (optimal triangulation), Stewénius et al. 2006 (the
action-matrix five-point solver), Lee & Civera 2019 (why optimal triangulation buys less than you
would think).

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 10 minutes in total, numpy and
scipy only. (If the action-matrix five-point implementation blocks you, a multi-start solver that
drives the $3\times3$ minors of
$C(R) = [\,\dots\,(x_2^{(i)} \times Rx_1^{(i)})^\top \dots]$ to zero with
`scipy.optimize.least_squares` over the null space is an acceptable substitute — the criteria below
are decidable either way.)

**Scene generator (fixed)**: $f = 500$, principal point $(320, 320)$, 3D points drawn uniformly
from $[-2,2]\times[-2,2]\times[3.5,6.5]$, $R$ a $10^\circ$ rotation about a uniformly random axis,
$t$ a uniformly random direction with $\lVert t\rVert = 0.5$, and isotropic Gaussian pixel noise
$N(0,\sigma^2)$ added in pixel coordinates. Report with a fixed seed.

All **five conditions** must hold to pass.

1. **Noise-free exactness (eight-point)**: with 8 points in a general configuration and
   $\sigma = 0$, $\max_i \lvert x_2^{(i)\top}\hat{E}x_1^{(i)}\rvert < 10^{-10}$,
   $\sigma_3(\hat{E})/\sigma_1(\hat{E}) < 10^{-10}$, and rotation error $< 10^{-8}$ rad.
   (Reference measurements: $1.4\times10^{-14}$, $7\times10^{-17}$, $0$.)
2. **Noise-free exactness (five-point)**: with 5 points in a general configuration and
   $\sigma = 0$, the returned solution set contains the true solution — minimum rotation error
   $< 10^{-6}$ rad. **Every** returned solution satisfies
   $\lVert 2EE^\top E - \operatorname{tr}(EE^\top)E\rVert_F / \sigma_1(E)^3 < 10^{-8}$ and
   $\lvert\det E\rvert/\sigma_1(E)^3 < 10^{-8}$, and the number of distinct rotations is at most 20
   (ten essential matrices times two rotations). (Reference measurements: 9, 12 and 16 distinct
   rotations; minimum error $0$.)
3. **Planar degeneracy**: with the 3D points on a plane, $n \ge 9$ and $\sigma = 0$,
   $\sigma_7(A)/\sigma_6(A) < 10^{-8}$ (a three-dimensional null space) and the eight-point
   rotation error exceeds $1^\circ$, while the five-point solver run on five of the same points has
   minimum rotation error at most $10^{-6}$ rad. (Reference measurements: ratio
   $1.1\times10^{-15}$, eight-point error $4.95^\circ$, five-point error $0^\circ$.)
4. **Effect of normalisation (pixel $F$)**: at $\sigma = 1$px over at least 200 trials, the median
   $\operatorname{cond}(A)$ without normalisation is at least $10^3$ times the one with it, and the
   p90 rotation error improves by at least 20% with normalisation. Furthermore, **when solving for
   $E$ directly in normalized coordinates** the two versions agree to within $10^{-12}$ in
   rotation error. (Reference measurements: $9.8\times10^5$ against $3.8\times10^2$, p90
   $16.35^\circ \to 10.42^\circ$ (36% better), and exactly identical on the $E$ side.)
5. **Comparison against noise (the main point of this task)**: for
   $\sigma \in \{0.1, 0.5, 1.0, 2.0\}$px over at least 60 trials each, the **median rotation
   error** of the five-point method (on 5 points, taking the minimum-error candidate) is at most
   **0.85 times** that of the eight-point method (on 8 points).
   (Reference measurements — medians in degrees, 60 trials:)

   | $\sigma$ (px) | five-point median | eight-point median | ratio | five-point p90 | eight-point p90 |
   |---|---|---|---|---|---|
   | 0.1 | 0.504 | 0.970 | 0.52 | 4.273 | 3.037 |
   | 0.5 | 2.153 | 3.366 | 0.64 | 6.103 | 8.190 |
   | 1.0 | 3.668 | 4.924 | 0.74 | 8.179 | 16.672 |
   | 2.0 | 4.436 | 6.234 | 0.71 | 19.500 | 15.269 |

   **State this in the report**: unlike the median, p90 does *not* improve consistently — the
   five-point method is worse at $\sigma = 0.1$ and at $2.0$. A minimal solver returns several
   solutions, so its tail is heavy; that is exactly why five-point is used **only inside RANSAC**
   in practice, with the final pose refined by bundle adjustment (`c7-bundle-adjustment`). "The
   five-point algorithm is more accurate than the eight-point algorithm" is **a statement about
   medians**.

**Baselines**: (1) each other (eight-point against five-point); (2) normalisation on against off;
(3) optionally `cv2.findEssentialMat` or `cv2.findFundamentalMat` on the same input, if installed —
check whether the rotation-error distributions overlap.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| rotation error comes out near $180^\circ$ | wrong choice between $W$ and $W^\top$, or the sign of $t$ | print the depths of all four candidates and select by chirality (P4) |
| epipolar residual is $10^{-14}$ but the pose is wrong | a degenerate configuration (coplanar or pure rotation) | look at $\sigma_7(A)/\sigma_6(A)$ and $\sigma_2(E^\star)/\sigma_1(E^\star)$ |
| the result barely changes across the rank-2 projection | the projection was skipped, or applied twice | print $\sigma_3(\hat{E})$ directly |
| $E$ looks like an $F$ (entries of order $10^{-6}$) | pixel coordinates mistaken for normalized ones | check that the entries of $x$ are $O(1)$ |
| the five-point solver returns nothing | the null space is not four-dimensional, or the $w=0$ branch | look at $\sigma_5(A)/\sigma_6(A)$ and retry with a permuted basis |
| the five-point solver returns more than 20 solutions | the residual tolerance is loose and near-solutions were counted | make the tolerance relative and raise the deduplication angle |

## Open problems

- **(open problem) the bias-variance trade-off of multi-view triangulation** — as R5 showed, the
  ML (reprojection-error) solution is not unbiased, while the unbiased inverse-depth
  parameterisation conflicts with the isotropic Gaussian assumption of bundle adjustment. The
  second-order bias is known for two views, but there is no quantitative criterion for which
  parameterisation maximises final map accuracy on $N$ views of a real trajectory with outliers.
  Current approaches: [Lee & Civera 2019](https://arxiv.org/abs/1907.11917) (measuring what
  optimisation actually buys), [Hartley & Sturm 1997](https://doi.org/10.1006/cviu.1997.0547).
  What is missing: a definition of bias that includes the tail handling, and evidence that reducing
  it actually helps map accuracy.
- **(open problem) online certification of degenerate configurations** — planar scenes, pure
  rotation and critical surfaces wreck the pose without raising the residual (the failure modes of
  R3 and R4). There is no method that emits a **certificate** of "this configuration is degenerate"
  during estimation, and practice relies on singular-value ratios and model-selection heuristics.
  Current approaches: the weighted scoring of [MAGSAC++](https://arxiv.org/abs/1912.05909), and the
  theory of critical surfaces in MVG ch.22. What is missing: a degeneracy certificate usable within
  a real-time budget.
- **(open problem) the boundary between geometric minimal solvers and learned
  correspondence/pose estimation** — cases where learned correspondences or depths beat geometric
  solvers in low-texture, wide-baseline settings have piled up, but there is no quantitative
  criterion for **when imposing geometric constraints is a net loss**. Current approaches:
  [DUSt3R](https://arxiv.org/abs/2312.14132) (which drops almost all of the constraints) and
  [DROID-SLAM](https://arxiv.org/abs/2108.10869) (which keeps them through a differentiable bundle
  adjustment). What is missing: a model that predicts the crossover point from scene statistics.
  The question returns in `c7-learned-correspondence-slam`.
- **(open problem) certifying the numerical stability of minimal solvers** — the condition number
  of the action-matrix eigendecomposition degrades by many orders of magnitude depending on the
  configuration, and there is no criterion for judging that **in advance** from the sample.
  Current approach: the stability comparison in
  [Stewénius et al. 2006](https://doi.org/10.1016/j.isprsjprs.2006.03.005). What is missing: a way
  to attach stability guarantees to automatically generated minimal solvers.

## Concept check

Run `rc quiz c7-two-view-geometry`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: why the eight-point algorithm breaks on a coplanar scene
($\operatorname{rank}A = 6$); why Hartley normalisation does nothing for $E$ in normalized
coordinates; the degrees of freedom of $E$ and $F$ (5 and 7); the direction of the depth bias of
$\hat{Z} = fb/\hat{d}$; and what the epipolar constraint becomes under pure rotation ($E = 0$, so
the constraint is vacuous).

## How to study this stage

1. **Write the two lines that eliminate depth by hand (30 min)** — the derivation of R1 uses only
   $\hat{t}t = 0$ and $a^\top\hat{t}a = 0$. Go from (5) to (1) on a blank page, then draw the
   coplanarity condition that the triple product expresses. Derive the epipoles and epipolar lines
   here too (P1).
2. **Reconstruct (ii)$\Rightarrow$(i) of R2 rather than memorising it (60 min)** — the crux is the
   single line (11), $\operatorname{diag}(1,1,0) = ZW^\top$. Multiply $Z$ and $W$ out to confirm it,
   then pull $UZU^\top = \hat{u}_3$ out with $R\hat{a}R^\top = \widehat{Ra}$ (module C1). This
   construction is the source of "four decompositions of an essential matrix" and is all of P4.
   Read MVG ch.9.6 alongside it as the same result in different notation.
3. **Implement the eight-point algorithm wrongly first (90 min)** — run it in pixel coordinates
   **without** the rank-2 projection and **without** normalisation. See for yourself that
   $\sigma_3(E)$ is not zero and that the condition number is $10^6$, and only then put (3) and
   $T_i$ in. Only corrections added after seeing the breakage stick (P5).
4. **Build a degeneracy (60 min)** — put the points on a plane, then set $t = 0$. In both cases see
   the residual stay small while the pose is wrong, and detect it with $\sigma_7(A)/\sigma_6(A)$
   (P6). That experience connects to the degeneracy discussion in `c7-robust-fitting-ransac`.
5. **Get the structure of the five-point method before the code (120 min)** — write the twenty
   monomials on paper and draw the flow $10\times20 \to [I|B] \to$ action matrix. The
   implementation in Stewénius et al. 2006 is the shorter one. If you get stuck, use the
   alternative in the reproduction task (multi-start on the minors) to get numbers first and swap
   in the action matrix later.
6. **Confirm the bias by Monte Carlo (60 min)** — run P7 and see for yourself that truncating the
   tail at $3\sigma_d$ flips the sign. This single experiment teaches the gap between the summary
   "convexity means overestimation" and what actually happens.
7. **Two papers and the notes (120 min)** — read Longuet-Higgins first (it is two pages) and write
   down what the 1981 method was missing, then read Nistér with §3–4 at the centre. Write the
   one-page note per paper **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the open problems and write a paragraph on
   why it is still open.

**Passing bar**: you can write (1) and the (ii)$\Rightarrow$(i) construction of R2 on a blank page,
you have code that meets all five conditions of the reproduction task, you can build and diagnose a
planar degeneracy yourself, you have matched the bias numbers of P7 in prediction and measurement,
and you have notes on both papers.
