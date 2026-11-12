---
id: c7-bundle-adjustment
lang: en
title: N-view geometry and bundle adjustment
summary: >-
  Why the normal equations of the reprojection error are sparse, and why the Schur complement is
  an exact elimination rather than an approximation — proved through the block LDL factorisation
  and the preservation of inertia. Derives the seven gauge freedoms of bundle adjustment down to
  their generators, counts the linear constraints that decide when self-calibration is solvable,
  and shows numerically how that count saturates on a critical motion sequence.
objectives:
  - Derive the block-diagonal structure of the camera and point blocks of the normal equations from the dependency structure of the residuals.
  - Prove that the Schur complement is an exact elimination via the block LDL factorisation, and interpret it as the Hessian of the reduced cost.
  - Show that the sparsity of the reduced matrix $S$ equals the camera co-visibility graph, and measure its density.
  - Exhibit the seven gauge generators of bundle adjustment and confirm numerically that they span the null space.
  - Count the linear constraints of self-calibration to derive the number of views required, and show that the count saturates on a critical motion sequence.
tags: [perception, bundle-adjustment, schur-complement, gauge-freedom, self-calibration, research]
---

# N-view geometry and bundle adjustment

## Setup and notation

The recommended prerequisites are `c7-two-view-geometry` in this module (epipolar geometry and
pose recovery), `r0-sparse-linear-algebra` (sparse Cholesky and elimination orderings) and
`r0-numerical-optimization` (Gauss–Newton and trust regions). None of them is locked. The lesson
assumes:

- Linear algebra: block matrix arithmetic, Cholesky, positive definiteness, Sylvester's law of
  inertia (used as a one-line citation in the proof sketch if you have not met it), and the notion
  of nnz for a sparse matrix.
- Optimisation: Gauss–Newton and Levenberg–Marquardt, normal equations, trust-region damping.
- Lie groups: treating a pose as an element of $SE(3)$ and taking increments through the right
  Jacobian (`c1-so3-se3-exponential`).
- Projective geometry: the ambiguity $\{P_iH^{-1}, HX_j\}$ of a projective reconstruction and the
  meaning of the plane at infinity. The absolute dual quadric is used only as far as needed.

Notation (continuing the C7 conventions; $i$ indexes cameras, $j$ points, $(i,j) \in \mathcal{O}$
observations):

| Symbol | Meaning |
|---|---|
| $n_c$, $n_p$, $\lvert\mathcal{O}\rvert$ | number of cameras, points, observations |
| $\theta_i \in \mathbb{R}^{d_c}$ | parameters of camera $i$: $d_c = 6$ for pose only, $d_c = 9$ in the BAL model (pose 6 plus $f, k_1, k_2$) |
| $X_j \in \mathbb{R}^3$ | coordinates of point $j$ |
| $z_{ij} \in \mathbb{R}^2$ | the observed image point, $r_{ij} = \pi(\theta_i, X_j) - z_{ij}$ |
| $A_{ij} = \partial r_{ij}/\partial\theta_i$ | $2 \times d_c$ |
| $B_{ij} = \partial r_{ij}/\partial X_j$ | $2 \times 3$ |
| $H = J^\top J = \begin{bmatrix} B & E \\ E^\top & C\end{bmatrix}$ | the normal matrix; $B$ is the camera block, $C$ the point block |
| $S = B - EC^{-1}E^\top$ | the reduced camera matrix, the Schur complement |
| $\Omega^*$ | the absolute dual quadric, $4\times4$ symmetric of rank 3 |
| $\omega^* = KK^\top$ | the dual image of the absolute conic (DIAC) |

**Cost convention**: $C(\Theta,\mathcal{X}) = \frac{1}{2}\sum_{(i,j)\in\mathcal{O}}\lVert r_{ij}\rVert^2$.
The factor $\frac{1}{2}$ is the same convention as Ceres, and every cost figure reported in this
lesson uses it. The reprojection RMS is
$\sqrt{\sum\lVert r_{ij}\rVert^2 / \lvert\mathcal{O}\rvert}$ in pixels.

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (sparse structure of the normal equations) [D2]** — because $r_{ij}$ depends on exactly
  **one** $\theta_i$ and **one** $X_j$, $B$ is block diagonal with one $d_c \times d_c$ block per
  camera, $C$ is block diagonal with one $3\times3$ block per point, and $E$ has exactly one
  $d_c\times3$ block per observation $(i,j)$. Hence
  $$\operatorname{nnz}(B) = d_c^2 n_c,\quad \operatorname{nnz}(C) = 9n_p,\quad
    \operatorname{nnz}(E) = 3d_c\lvert\mathcal{O}\rvert. \tag{1}$$
- **R2 (the Schur complement is not an approximation) [D3]** — if $C \succ 0$ then $H$ admits the
  block LDL factorisation
  $$H = \begin{bmatrix} I & EC^{-1} \\ 0 & I\end{bmatrix}
        \begin{bmatrix} S & 0 \\ 0 & C\end{bmatrix}
        \begin{bmatrix} I & 0 \\ C^{-1}E^\top & I\end{bmatrix} \tag{2}$$
  from which (a) the solution of $H\delta = (v, w)$ is **exactly** given by
  $S\delta_c = v - EC^{-1}w$ together with $\delta_p = C^{-1}(w - E^\top\delta_c)$; (b)
  $H \succ 0 \iff S \succ 0$ (preservation of inertia); and (c) $S$ is the Hessian of the
  **reduced cost** obtained by eliminating the points.
- **R3 (the sparsity of the reduced matrix is co-visibility) [D2]** — since
  $S_{ik} = B_{ik} - \sum_j E_{ij}C_{jj}^{-1}E_{kj}^\top$, the $(i,k)$ block of $S$ is non-zero
  **exactly when cameras $i$ and $k$ see at least one point in common**. The sparsity pattern of
  $S$ is the adjacency matrix of the camera co-visibility graph.
- **R4 (there are exactly seven gauge freedoms) [D2]** — the reprojection cost is invariant under
  a **similarity** transform of the world frame. The generators are
  $$
  \begin{aligned}
  \text{rotation}(\omega):&\quad \delta\theta_i^{\mathrm{rot}} = -\omega,\;
    \delta t_i = 0,\; \delta X_j = \omega \times X_j, \\
  \text{translation}(a):&\quad \delta\theta_i^{\mathrm{rot}} = 0,\;
    \delta t_i = -R_i a,\; \delta X_j = a, \\
  \text{scale}(s):&\quad \delta\theta_i^{\mathrm{rot}} = 0,\;
    \delta t_i = t_i,\; \delta X_j = X_j
  \end{aligned} \tag{3}
  $$
  and the seven are independent. So the null space of $J$ is seven-dimensional and the rank
  deficiency of $H$ is 7 (leaving the intrinsics free does not change the similarity gauge).
- **R5 (solvability of self-calibration) [D2]** — given a projective reconstruction $\{P_i\}$, the
  absolute dual quadric satisfies $\omega_i^* = P_i\Omega^*P_i^\top$. Assuming zero skew, unit
  aspect ratio and a principal point at the origin gives **four linear constraints per view**, so
  pinning down the ten entries of $\Omega^*$ (nine up to scale) needs $4N \ge 9$, that is,
  $N \ge 3$ views. That count is **necessary only**: on a critical motion sequence the rank
  saturates at 8 no matter how many views are added.

## Derivation

### R1 — why the blocks are block diagonal

The residual $r_{ij}$ depends only on camera $i$ and point $j$. So for $k \ne i$ we have
$\partial r_{ij}/\partial\theta_k = 0$, and the camera-camera block of the normal equations,

$$H_{\theta_i\theta_k} = \sum_{(m,j)\in\mathcal{O}}
  \left(\frac{\partial r_{mj}}{\partial\theta_i}\right)^\top
  \left(\frac{\partial r_{mj}}{\partial\theta_k}\right),$$

has every term requiring $m = i$ and $m = k$ at once, so it vanishes for $i \ne k$. The
point-point blocks vanish for $j \ne l$ for the same reason. What remains is

$$B_{ii} = \sum_{j:(i,j)\in\mathcal{O}} A_{ij}^\top A_{ij}, \quad
  C_{jj} = \sum_{i:(i,j)\in\mathcal{O}} B_{ij}^\top B_{ij}, \quad
  E_{ij} = A_{ij}^\top B_{ij} \tag{4}$$

with the right-hand side $v_i = -\sum_j A_{ij}^\top r_{ij}$ and $w_j = -\sum_i B_{ij}^\top r_{ij}$.
The nnz formulas (1) are read straight off (4): $B$ holds $n_c$ blocks of size
$d_c\times d_c$, $C$ holds $n_p$ blocks of size $3\times3$, and $E$ holds one $d_c\times3$ block
per observation.

Measured (BAL `problem-49-7776-pre.txt`, $n_c = 49$, $n_p = 7776$,
$\lvert\mathcal{O}\rvert = 31843$, $d_c = 9$): $\operatorname{nnz}(B) = 81\cdot49 = 3969$,
$\operatorname{nnz}(C) = 9\cdot7776 = 69984$, $\operatorname{nnz}(E) = 27\cdot31843 = 859761$. In
total $\operatorname{nnz}(H) = 3969 + 69984 + 2\cdot859761 = 1\,793\,475$, and since $n = 23769$
the density is $3.17\times10^{-3}$. **Storing $H$ densely would take
$23769^2\cdot8$ bytes = 4.21 GiB**; storing it sparsely takes tens of megabytes. That one line
explains everything about how bundle adjustment is implemented.

**Where the assumptions break**: if a residual depends on two cameras at once — a relative-pose
prior between cameras, an IMU preintegration factor, rolling-shutter interpolation between
neighbouring frames — then $B$ is no longer block diagonal. The Schur complement still applies,
but the elimination ordering of $B$ now matters, and from that point on this is general sparse
Cholesky territory with AMD/COLAMD orderings (`r0-sparse-linear-algebra`).

### R2 — the Schur complement (derivation)

From the second row of

$$\begin{bmatrix} B & E \\ E^\top & C\end{bmatrix}
  \begin{bmatrix}\delta_c\\\delta_p\end{bmatrix}
  = \begin{bmatrix}v\\w\end{bmatrix} \tag{5}$$

solve for $\delta_p$ (assuming $C$ invertible):

$$\delta_p = C^{-1}\big(w - E^\top\delta_c\big) \tag{6}$$

and substitute into the first row: $B\delta_c + EC^{-1}w - EC^{-1}E^\top\delta_c = v$, that is,

$$\underbrace{\left(B - EC^{-1}E^\top\right)}_{S}\delta_c = v - EC^{-1}w. \tag{7}$$

Because $C$ is block diagonal, $C^{-1}$ means inverting $3\times3$ blocks one at a time, at cost
$O(n_p)$ — this is where bundle adjustment becomes cheap. The size of (7) is $d_cn_c$, far smaller
than the original $d_cn_c + 3n_p$.

**Reading it as a reduced cost**: minimising the quadratic model
$q(\delta) = \frac12\delta^\top H\delta - \delta^\top g$ over $\delta_p$ first puts its minimiser
exactly at (6), and substituting back gives

$$\tilde{q}(\delta_c) = \tfrac12\delta_c^\top S\delta_c - \delta_c^\top(v - EC^{-1}w) + \text{const}.$$

So **$S$ is the Hessian of the cost that remains after the points have been eliminated by exact
minimisation**: the Schur complement does not "ignore the points", it "optimises over them
exactly". That is R2 (a) and (c); the proof sketch bundles (b) in with them.

**Cost accounting**: forming $S$ costs $\sum_j m_j^2$ ($m_j$ = number of cameras seeing point $j$)
times the block-product cost, and factorising $S$ costs $O((d_cn_c)^3/3)$. For BAL-49,
$\dim S = 441$, so $2.86\times10^7$ flops, against $4.48\times10^{12}$ flops for a dense
factorisation of $H$ — a factor of $1.57\times10^5$. Measured: one Jacobian build plus one Schur
step takes 0.634 s in numpy, and 40 LM iterations take about 30 s.

**Where the assumptions break**: the most common way to lose $C \succ 0$ is a **point seen in a
single view** — one observation gives only two residuals, so
$C_{jj} = B_{ij}^\top B_{ij}$ has rank at most 2 and the $3\times3$ matrix is singular. The fixes
are to drop such points or to lean on the LM damping $C + \lambda D_C$. (The `-pre` files of BAL
are pre-filtered — measured: minimum 2 observations per point, maximum 29, mean 4.10, with 3449
points having exactly 2. There are no singular $3\times3$ blocks, and their median condition
number is 290.) The trap in the other direction is large $n_c$: at city scale, $\dim S$ reaches
$10^5$, (7) can no longer be factorised densely, and iterative methods (CG) with preconditioners
become necessary — the subject of must-read 2.

### R3 — sparsity of the reduced matrix

Writing out the blocks of (7),

$$S_{ik} = B_{ik} - \sum_{j} E_{ij}\,C_{jj}^{-1}\,E_{kj}^\top \tag{8}$$

and $E_{ij} \ne 0$ is equivalent to $(i,j) \in \mathcal{O}$. So for $i \ne k$, $S_{ik} \ne 0$ iff
**there exists $j$ with $(i,j), (k,j) \in \mathcal{O}$** — iff the two cameras see a common point.
The sparsity pattern of $S$ is the adjacency matrix of the camera co-visibility graph (plus the
diagonal).

Measured (BAL-49): the density of the co-visibility graph is 0.835 and the density of $S$ is
0.835 — **the same number**. The 49 cameras mostly overlap, so $S$ is effectively dense, and at
$441\times441$ that costs nothing. At street-view or internet-photo scale this graph becomes
sparse, and exploiting that sparsity as a preconditioner is the visibility-based preconditioner of
must-read 2.

### R4 — seven gauge freedoms

First confirm that changing the world frame by a similarity leaves every reprojection untouched.
The camera coordinates are $X_c = R_iX_j + t_i$ and the projection only sees the **direction** of
$X_c$, so:

- **Rotation** $Q \in SO(3)$: $X_j \mapsto QX_j$, $R_i \mapsto R_iQ^\top$, $t_i \mapsto t_i$.
  Then $R_iQ^\top\cdot QX_j + t_i = R_iX_j + t_i$ — invariant.
- **Translation** $a$: $X_j \mapsto X_j + a$, $t_i \mapsto t_i - R_ia$. Then
  $R_i(X_j+a) + t_i - R_ia = R_iX_j + t_i$ — invariant.
- **Scale** $s > 0$: $X_j \mapsto sX_j$, $t_i \mapsto st_i$. Then $sR_iX_j + st_i = sX_c$, and
  since the projection is $-X_{c,xy}/X_{c,z}$ the factor $s$ cancels — invariant. (The intrinsics
  $f, k_1, k_2$ are untouched, so this holds for the BAL model too.)

Differentiating in $\epsilon$ reads off the generators (3). For the rotation,
$Q = \exp(\hat\omega\epsilon)$ gives $R_i \mapsto R_i\exp(-\hat\omega\epsilon)$, so the **right
increment** is $-\epsilon\omega$ (that is the $\delta\theta_i^{\mathrm{rot}} = -\omega$ of (3)) and
the points move by $QX_j = X_j + \epsilon\,\omega\times X_j + O(\epsilon^2)$. The seven generators
are independent in a generic configuration, so $\dim\ker J = 7$ and
$\operatorname{rank} H = n - 7$.

Measured (synthetic problem: 6 cameras, 40 points, $f$ fixed, $n = 6\cdot6 + 3\cdot40 = 156$): the
singular values of $J$ drop from $\sigma_{149} = 4.7078$ to $\sigma_{150} = 4.37\times10^{-8}$,
**a factor of $1.08\times10^{8}$** — the rank deficiency is exactly 7. The generators $g$ of (3)
satisfy $\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert) = 0$ to machine precision, and the
largest principal angle between the span of the generators and the numerical seven-dimensional
null space is $9.1\times10^{-8}$ degrees. At the converged solution of BAL-49 all seven generators
gave $\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert) \le 4.5\times10^{-12}$.

**Four ways to fix it**: (a) **gauge fixing** — hold the 6 pose parameters of camera 0 constant and
fix one distance (say the length of the 0-1 baseline) at 1, removing 7 in total. (b) **Free
network** — use the Moore–Penrose pseudo-inverse of $H$ to take the minimum-norm step, which does
not move along the gauge directions (the inner constraints of Triggs §9). (c) **Prior /
Tikhonov** — add a weak prior on the poses so that $H + \Lambda$ is invertible. (d) **Lean on the
LM damping** — $H + \lambda D$ is always invertible for $\lambda > 0$.

**Where the assumptions break (important)**: because of (d), **bundle adjustment "works" without
fixing the gauge at all** — which is why many implementations converge in complete ignorance of
the issue. Two things do break. (1) As $\lambda \to 0$ the step norm diverges along the gauge
directions, so the steps rattle at the end of convergence (measured: once $\lambda$ drops below
$10^{-10}$ in BAL-49, the relative cost decrease is under $10^{-6}$ while the step norm does not
shrink). (2) **Covariance depends on the gauge** — a parameter covariance extracted through a
pseudo-inverse differs with the choice of gauge, and reporting it as "the uncertainty of the map"
is wrong. What is gauge invariant are quantities like relative poses and reprojections (Triggs §9).
BA covariances reported without this distinction are not comparable across systems.

### R5 — solvability of self-calibration

A projective reconstruction is ambiguous up to $H \in PGL(4)$: $\{P_i, X_j\}$ and
$\{P_iH^{-1}, HX_j\}$ produce identical images. Climbing to a Euclidean reconstruction means
pinning $H$ down, and self-calibration takes that information from the **structure of the
intrinsics**. The device is the absolute dual quadric

$$\Omega^* = H\,\operatorname{diag}(1,1,1,0)\,H^\top \tag{9}$$

In a Euclidean frame the dual of the plane at infinity is $\operatorname{diag}(1,1,1,0)$, so (9) is
the symmetric rank-3 $4\times4$ matrix that records where the plane at infinity and the absolute
conic have gone in the projective frame. The key relation is

$$\omega_i^* = K_iK_i^\top = P_i\,\Omega^*\,P_i^\top \tag{10}$$

with $P_i$ the cameras of the projective reconstruction. (10) is **linear** in the ten entries of
$\Omega^*$.

Putting assumptions on the intrinsics into the left-hand side of (10) produces constraints. With
zero skew, unit aspect ratio and a principal point at the origin,
$K = \operatorname{diag}(f, f, 1)$, so $\omega^* \propto \operatorname{diag}(f^2, f^2, 1)$, which
per view means the four linear constraints

$$\omega^*_{12} = 0,\quad \omega^*_{13} = 0,\quad \omega^*_{23} = 0,\quad
  \omega^*_{11} - \omega^*_{22} = 0 \tag{11}$$

($f$ is eliminated, so it may differ between views). With $N$ views that is $4N$ equations, against
nine unknowns (ten entries of $\Omega^*$ less one scale), so

$$4N \ge 9 \;\Longrightarrow\; N \ge 3. \tag{12}$$

Measured ($f = 500$; the rank of the $4N\times10$ coefficient matrix after moving to a projective
frame by a random projective transform):

| Motion | $N=2$ | $N=3$ | $N=4$ | $N=6$ | error in recovered $\Omega^*$ |
|---|---|---|---|---|---|
| general | rank 8 | **rank 9** | rank 9 | rank 9 | $5\times10^{-16}$ for $N\ge3$ |
| pure translation | rank 7 | rank 8 | rank 8 | rank 8 | $0.35 \sim 1.0$ (failure) |
| fixed-axis rotation + arbitrary translation | rank 7 | rank 8 | rank 8 | rank 8 | $0.92 \sim 0.98$ (failure) |
| pure rotation ($t_i = 0$) | rank 5 | rank 5 | rank 5 | rank 5 | 1.4 (failure) |

Under general motion the rank fills to 9 at $N = 3$, exactly as (12) predicts. In addition, the
linear solution never imposed the **rank-3 constraint** on $\Omega^*$ and yet the recovered
$\Omega^*$ came out with a fourth singular value at the $10^{-16}$ level — under general motion the
data implies the rank condition by itself. On a critical motion sequence it does not.

**Where the assumptions break — critical motion sequences**: the last three rows of that table.
Under pure translation and under fixed-axis rotation the rank **saturates at 8** even with six
views, leaving a one-parameter ambiguity. The inequality (12) is **necessary only, and it hides the
assumption that the motion is general.** Pure rotation is worse still: with $t_i = 0$ the fourth
column of $P_i = K[R_i\,\vert\,0]$ is zero, so (10) only touches the upper-left $3\times3$ block of
$\Omega^*$ (six entries) and the measured rank is 5. In that case self-calibration has to be solved
through the conjugacy structure of the infinite homography $H_\infty = KR_iK^{-1}$ rather than
through $\Omega^*$ (MVG ch.19 **[D0]**). In short: **"three views suffice for self-calibration" is
true only for general motion, and the typical motions of a robot — planar driving, turning about a
fixed axis — are precisely the exceptions.**

## Proof sketch

### R2 — exactness of the Schur complement and preservation of inertia

**Hypotheses** H1: $H = \begin{bmatrix} B & E \\ E^\top & C\end{bmatrix}$ is symmetric. H2: $C$ is
invertible.
**Conclusions** C1: the factorisation (2) holds. C2: the solution of (5) is exactly given by (6)
and (7). C3: if $C \succ 0$ then $H \succ 0 \iff S \succ 0$.

**Strategy**: write the block elimination as a **congruence** and invoke Sylvester's law of
inertia.

1. **C1 (direct multiplication)**: put $L = \begin{bmatrix} I & EC^{-1} \\ 0 & I\end{bmatrix}$ and
   $D = \begin{bmatrix} S & 0 \\ 0 & C\end{bmatrix}$ and multiply:
   $$LD = \begin{bmatrix} S & EC^{-1}C \\ 0 & C\end{bmatrix} = \begin{bmatrix} S & E \\ 0 & C\end{bmatrix},$$
   $$LDL^\top = \begin{bmatrix} S & E \\ 0 & C\end{bmatrix}
     \begin{bmatrix} I & 0 \\ C^{-1}E^\top & I\end{bmatrix}
     = \begin{bmatrix} S + EC^{-1}E^\top & E \\ E^\top & C\end{bmatrix} = H,$$
   where the last equality is the definition $S = B - EC^{-1}E^\top$. $\square$
2. **C2**: $L$ is unit upper triangular, so $\det L = 1 \ne 0$. (5) reads $LDL^\top\delta = g$, and
   with $L^{-1} = \begin{bmatrix} I & -EC^{-1}\\0&I\end{bmatrix}$ we get
   $DL^\top\delta = L^{-1}g = (v - EC^{-1}w,\; w)$. The first block is
   $S(\delta_c) = v - EC^{-1}w$, which is (7), and the second is
   $C(C^{-1}E^\top\delta_c + \delta_p) = w$, which is (6). This is not an approximation but **the
   same linear system eliminated in a different order**. $\square$
3. **C3**: (2) has the form $H = LDL^\top$, so $H$ and $D$ are congruent and, by Sylvester's law of
   inertia, have the same number of positive, negative and zero eigenvalues. $D$ is block diagonal,
   so $D \succ 0 \iff S\succ0 \text{ and } C\succ0$. Having assumed $C\succ0$, we get
   $H\succ0 \iff S\succ0$. $\square$
4. **Why this matters in practice**: LM solves $H + \lambda D_H$. If the damping is added to $B$ and
   $C$ **separately** and the Schur complement is then applied, (2) still holds, so the reduced
   system remains positive definite and Cholesky is safe. Adding the damping **after** forming $S$
   solves a different problem instead (the trust region no longer constrains the point parameters).
   This is a classic hiding place for implementation bugs.
5. **Remove a hypothesis**: if H2 ($C$ invertible) fails then (2) is not even defined. A point seen
   in a single view is exactly that case, and computing $S$ then lets `inf`/`nan` spread silently.
   And if $C$ is only semi-definite rather than positive definite, the equivalence in C3 survives in
   one direction only — $S \succ 0$ no longer implies that $H$ is non-singular (the gauge is exactly
   that case: $H$ has rank deficiency 7 while, with damping, $S$ is positive definite).

Step left out: Sylvester's law of inertia. It is the standard result that $A$ and $LAL^\top$ have
the same inertia for any invertible $L$; see a linear algebra text or
`r0-linear-algebra-decompositions`.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R1)** Derive (4) and write down the nnz formulas (1). For BAL
`problem-49-7776-pre.txt` ($n_c=49$, $n_p=7776$, $\lvert\mathcal{O}\rvert=31843$, $d_c=9$),
compute $\operatorname{nnz}(B), \operatorname{nnz}(C), \operatorname{nnz}(E),
\operatorname{nnz}(H)$ and the density of $H$.
*Solution sketch*: all you use is that $r_{ij}$ depends on two variables. The answers are
$3969,\; 69984,\; 859761,\; 1\,793\,475$ and a density of $3.17\times10^{-3}$.

**P2 (proof, ★★★, R2)** State exactly which direction of C3 fails when $C \succeq 0$ is singular,
and show which extra (range) condition makes C2 still hold for the generalised Schur complement
$S = B - EC^{+}E^\top$ defined through the pseudo-inverse.
*Strategy and key inequality*: assume $H \succeq 0$ and
$\operatorname{range}(E^\top) \subseteq \operatorname{range}(C)$ and rewrite $LDL^\top$ with the
pseudo-inverse. The crux is that $CC^{+}E^\top = E^\top$ must hold for step 2 to eliminate without
losing information. Build a $2\times2$ block counterexample violating the range condition to see
one direction collapse.

**P3 (numerical, ★, R2·R3)** For BAL-49 compute (a) the memory needed to store $H$ densely,
(b) $\dim S$, (c) the ratio of dense Cholesky flops for $S$ and for $H$, and (d) the expected
density of $S$.
*Answer*: (a) $23769^2\cdot8 = 4.52\times10^9$ B $= 4.21$ GiB. (b) $9\cdot49 = 441$.
(c) $(441^3/3)/(23769^3/3) = 2.86\times10^7 / 4.48\times10^{12} = 6.4\times10^{-6}$, i.e. cheaper
by $1.57\times10^5$. (d) the same as the camera co-visibility density — 0.835 for this file.
Tolerance 5%. Check: build $S$ and measure `(abs(S)>0).mean()`; it must come out at 0.835.

**P4 (derivation, ★★, R4)** Derive the seven generators (3). Then argue, through the rank of the
Jacobian with the fixed parameters deleted, that holding the 6 pose parameters of camera 0 and the
constraint "length of the 0-1 baseline = 1" removes the gauge **exactly**. Say in one line why
leaving the intrinsics free does not change the 7.
*Solution sketch*: show that $X_c$ is invariant under a world similarity and differentiate in
$\epsilon$; for the rotation, read the right increment off $R_i\exp(-\hat\omega\epsilon)$. The rank
argument is that the seven-dimensional null space and the seven fixed coordinate axes are
transversal. The intrinsics are untouched by a similarity, so the invariance itself is unchanged.

**P5 (numerical, ★★, R5)** Redo the count behind (11) for three cases: (a) assuming zero skew only;
(b) zero skew plus unit aspect ratio; (c) all intrinsics unknown but **identical across all views**.
State the number of constraints per view and the number of unknowns in each case.
*Answer*: (a) 1 equation per view against 9 unknowns, so $N \ge 9$. (b) 2 equations per view, so
$N \ge 5$. (c) the unknowns are not the 9 of $\Omega^*$ but
$\{\pi_\infty \text{ of } H\ (3), K\ (5)\} = 8$, with two Kruppa equations per pair of views, so
$2\cdot\binom{N}{2} \ge 8$ gives $N \ge 3$ (3 by the count; in practice degeneracies may require
more). No tolerance (integers). Check: verifying (b) numerically, the rank of the $2N\times10$
matrix must reach 9 at $N = 5$. **Caution**: all of these counts are necessary conditions, and the
exact results in the literature (for instance the discussion that 8 views suffice in case (a)) use
extra algebraic structure — the point of this problem is not to claim sufficiency from a count.

**P6 (implementation, ★★★, R1·R2·R3)** Implement an LM bundle adjuster using the Schur complement
and pass the five conditions of the reproduction task.
*Rubric*: (a) the sign of $p = -P/P_z$ in the BAL camera model is right, so the initial cost is
within 0.1% of the reference; (b) the damping is added to $B$ and $C$ separately before the Schur
complement; (c) $C^{-1}$ is computed as $3\times3$ block inverses (no full inverse); (d) the density
of $S$ is reported against the co-visibility density; (e) the cost decreases monotonically.

**P7 (counterexample, ★★, R5)** Construct **two** motion sequences on which self-calibration fails
no matter how many views are added, and show through singular values that the rank of the
$4N\times10$ coefficient matrix saturates at 8. Then show that mixing in a very small general
motion component raises the rank to 9 but **with a terrible condition number**.
*Property checklist*: (a) the two cases are pure translation and fixed-axis rotation; (b) the ranks
at $N = 2,3,4,6$ are $7,8,8,8$; (c) the distance between the recovered $\Omega^*$ and the truth is
$O(1)$; (d) shrinking the perturbation $\epsilon$ makes $\sigma_9/\sigma_1 \to 0$ in proportion to
$\epsilon$; (e) a paragraph on why "the rank is 9" does not mean "the reconstruction works".

**P8 (paper, ★★, R2·R3)** Read §4 and §9 of Triggs et al. 2000 together with Agarwal et al. 2010
and write down why (7) of this lesson can no longer be used once $n_c$ reaches $10^5$, and where
exactly the two papers diverge. Then find **three pieces of missing information** for reproducing
the timing tables of Agarwal et al.
*Rubric*: going beyond "because $\dim S$ grows" and naming at least two of (a) the memory of
forming $S$ explicitly, (b) how the density of the co-visibility graph changes with scale, (c) the
effect of the preconditioner choice on the CG iteration count. For the missing information, be
specific: hardware, BLAS, the convergence criterion, or how the initial values were produced.

## Paper reading

**Two must-reads.** Write a one-page note on each, using the ten fixed questions
(`lesson-standard.md` §5). Read in three passes, and attack questions 4, 5, 6 and 7 in the third.
For the full bibliography, including the recommended papers, run
`rc papers c7-bundle-adjustment` (the course registry
`curriculum/robotics-research/papers.yaml`, ADR 0014).

1. **Triggs, McLauchlan, Hartley & Fitzgibbon, "Bundle adjustment: a modern synthesis"
   (2000, Vision Algorithms: Theory and Practice)** — role: `standard`.
   <https://doi.org/10.1007/3-540-44480-7_21> (§4 on sparsity and the Schur complement, §9 on
   gauge freedom, are the core.)
   Extra questions: (a) by what argument do the authors say that fixing the gauge changes the
   covariance but not the estimate, and how does that argument mesh with R4 (b) of this lesson?
   (b) Where does the elimination ordering they recommend in 2000 differ from the defaults of
   today's implementations (Ceres, GTSAM)?
2. **Agarwal, Snavely, Seitz & Szeliski, "Bundle adjustment in the large" (2010, ECCV)** — role:
   `standard`. <https://doi.org/10.1007/978-3-642-15552-9_3>
   Extra questions: (a) recompute the memory-versus-compute trade-off between the explicit and
   implicit Schur complement using the measurements in this lesson (the nnz values and $\dim S$):
   where is the crossover? (b) Why does their preconditioner come out of the co-visibility graph
   (R3)? (c) Is the reported convergence criterion based on the cost or on the step, and how does
   that choice affect the iteration counts in the tables?

**The ten fixed questions**: (1) which problem under which assumptions; (2) what exactly earlier
work could not do; (3) the core idea in one equation; (4) what is guaranteed and **what is not**;
(5) the independent and dependent variables and the baselines, fairly tuned or not; (6) whether the
metric matches the claim, and whether variance and seeds are reported; (7) what is missing for
reproduction; (8) the first assumption to doubt if the result were wrong; (9) time and memory
complexity and real-time behaviour; (10) what you would change to go beyond it in a year.

**Recommended**: MVG ch.18-19, Barfoot SER ch.10, SE-Sync (open problem 1), iSAM2 (open problem 3).

## Reproduction task

**Tier R3 (figure reproduction).** Budget: one laptop CPU core, 40 iterations in under 5 minutes,
under 1 GiB of memory, numpy and scipy only. The input is a public BAL dataset.

**Input**: the Ladybug problem `problem-49-7776-pre.txt.bz2` from
`https://grail.cs.washington.edu/projects/bal/` ($n_c = 49$, $n_p = 7776$,
$\lvert\mathcal{O}\rvert = 31843$). Use the camera model exactly as that page defines it — in
particular the **negative sign in $p = -P/P_z$** and
$\text{pred} = f(1 + k_1r^2 + k_2r^4)p$; getting either wrong trips condition 1 immediately.

All **five conditions** must hold to pass. Every reference value below was measured for this
lesson (under the cost convention $\frac12\sum\lVert r\rVert^2$).

1. **Parsing and model correctness**: the initial cost is within **0.1%** of
   $8.509125\times10^{5}$ and the initial reprojection RMS within 0.1% of $7.310557$ px.
2. **Convergence**: the cost decreases monotonically and, within 40 iterations, the final cost is
   within **1%** of $1.334424\times10^{4}$ and the final reprojection RMS within 1% of
   $0.915493$ px. (Reference: a reduction of 63.8x.)
3. **The Schur complement is an exact elimination, numerically**: on a small synthetic problem
   (at most 8 cameras, at most 50 points), the dense solution $\delta_{\text{full}}$ and the Schur
   solution $\delta_{\text{schur}}$ satisfy
   $\lVert\delta_{\text{full}} - \delta_{\text{schur}}\rVert/\lVert\delta_{\text{full}}\rVert
   < 10^{-8}$. (Reference measurement: $2.2\times10^{-10}$, with
   $\dim H = 156 \to \dim S = 36$.)
4. **The gauge null space**: on the synthetic problem the singular values of $J$ break at
   $\sigma_{n-7}/\sigma_{n-6} > 10^{6}$ (reference: $1.08\times10^{8}$) and the seven generators of
   (3) satisfy $\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert) < 10^{-8}$ (reference: at most
   $4.5\times10^{-12}$ at the converged solution of BAL-49).
5. **Sparsity accounting**: $\operatorname{nnz}(B), \operatorname{nnz}(C), \operatorname{nnz}(E)$
   match the formulas (1) **exactly** ($3969,\ 69984,\ 859761$), and the density of $S$ equals the
   density of the camera co-visibility graph to within $10^{-12}$ (reference: both 0.835).

**State this in the report**: after reaching the final cost, shrinking $\lambda$ further makes the
step norm grow along the gauge directions (failure mode (1) of R4). An implementation that does not
fix the gauge "appears to converge" but cannot report a parameter covariance.

**Baselines**: (1) run Ceres Solver's `examples/bundle_adjuster` on the same file and compare the
final cost (if you can install it) — the cost definition is the same, so it must converge to the
same place. (2) Solve the same problem **without** the Schur complement, using a sparse least
squares from scipy (`scipy.sparse.linalg.lsqr` or
`scipy.optimize.least_squares(jac_sparsity=...)`), and compare the time per iteration. (3) Your own
dense solution on the small synthetic problem (condition 3).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| the initial cost is about 4x the reference | $p = +P/P_z$ (the negative sign is missing) | compute the prediction for one observation by hand and match its sign against the observation |
| the initial cost is right but it diverges | the rotation Jacobian confuses the right and left Jacobians | compare $\partial(RX)/\partial\theta = -R\hat{X}J_r(\theta)$ against finite differences |
| `nan` appears in $C^{-1}$ | a point with one observation, or the damping was not added to $C$ | print the minimum observation count per point and the smallest singular value of the $3\times3$ blocks |
| the cost decreases and then rattles | the damping was added after forming $S$ | add the damping to $B$ and $C$ separately and rerun |
| more than 10 s per iteration | $C$ was inverted densely as a whole | switch to $3\times3$ block inverses (`np.linalg.inv` applied to an $(n_p,3,3)$ array) |
| the final cost is 10% above the reference | stopped before convergence, or the $\lambda$ update is too conservative | plot the cost history on a log axis and check that it has flattened |
| the density of $S$ differs from co-visibility | an indexing error in the blocks of $E$ | delete one observation and check that the corresponding block of $S$ changes |

## Open problems

- **(open problem) certifying global optimality of bundle adjustment** — BA is non-convex, and there
  is no way to decide whether a converged local minimum is the global one. For pose-only problems
  (no points) the conditions under which the dual relaxation is tight, and the accompanying
  certificates, are known ([SE-Sync](https://arxiv.org/abs/1612.07386),
  [Carlone et al. 2015](https://arxiv.org/abs/1506.00746)), but this does not extend to a full BA
  with points, intrinsics and a robust loss. What is missing: a practical global-optimality
  certificate for the reprojection cost.
- **(open problem) a gauge-invariant standard for reporting uncertainty** — as R4 showed, the
  parameter covariance that BA produces depends on the choice of gauge. There is no agreement on
  what the **gauge-invariant summary statistic** should be for downstream consumers (loop-closure
  decisions, planning, sensor fusion), and papers report different things. Current approaches: the
  inner constraints of Triggs et al. 2000 §9, and the marginalisation of
  [iSAM2](https://doi.org/10.1177/0278364911430419). What is missing: a convention that makes
  numbers from different systems comparable.
- **(open problem) error bounds for incremental and distributed BA** — real-time systems reuse
  elimination orderings and marginalise old variables, giving up exact BA. There is no **guaranteed
  bound** on the resulting deviation, so one cannot separate drift caused by the approximation from
  drift caused by the data. Current approaches:
  [iSAM2](https://doi.org/10.1177/0278364911430419) (narrowing the scope of exact relinearisation)
  and Agarwal et al. 2010 (inexact Newton with CG). What is missing: error bounds for approximate
  elimination.
- **(open problem) combining learned weights with BA** — differentiable BA feeds learned
  correspondence weights into the cost, and if those weights are not probabilistically calibrated
  the covariance interpretation of BA collapses. Current approach: the learned confidences of
  [DROID-SLAM](https://arxiv.org/abs/2108.10869). What is missing: a calibration procedure that
  converts learned weights into an observation noise model. The question returns in
  `c7-learned-correspondence-slam`.

## Concept check

Run `rc quiz c7-bundle-adjustment`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: why the camera block $B$ is block diagonal; whether the Schur complement is
an approximation (it is not); the dimension of the gauge null space (7); what the sparsity pattern
of $S$ equals (the camera co-visibility graph); and the view count that the linear count demands
for self-calibration, together with the limits of that count.

## How to study this stage

1. **Draw the sparsity by hand (40 min)** — sketch 3 cameras, 5 points and a handful of
   observations on paper and colour in the non-zero pattern of $J$ and $H$ yourself. Read the nnz
   formulas (1) off that picture and match them against the BAL numbers with P1. That single
   picture is all of R1 and R3.
2. **See the Schur complement as elimination (60 min)** — write the three lines from (5) to (7) on
   a blank page, then multiply out the $LDL^\top$ of (2) to confirm it. Whoever proves "it is not an
   approximation" for themselves and whoever memorises it part ways while debugging. Read Triggs §4
   alongside as the same result in different notation.
3. **Implement small first (120 min)** — on a synthetic problem with 6 cameras and 40 points,
   implement both (a) the dense solution and (b) the Schur solution and make them agree to about
   $10^{-10}$ (condition 3). Do not move on to BAL before that matches. On the same problem, take
   the singular values of $J$ and see the rank deficiency of 7 with your own eyes (condition 4).
4. **Create a gauge and then remove it (60 min)** — apply the generators (3) in code and confirm
   that the cost does not change; then fix camera 0 and the scale and see $H$ become invertible.
   After that, converge with LM without fixing anything and watch **the step norm fail to shrink**.
   That contrast is the central experience of this lesson.
5. **Move to BAL (180 min)** — download the data and start from the parser. Touch nothing else
   until the initial cost is within 0.1% of the reference (condition 1); the negative sign in
   $p = -P/P_z$ is where most people get stuck. Then match the final cost in 40 iterations
   (condition 2).
6. **Self-calibration begins with the count (60 min)** — write the four equations (11) out, build
   the $4N\times10$ matrix and measure its rank. Then switch to pure translation and watch the rank
   saturate (P7). The point is to confirm by hand why "the count works out" does not mean "it is
   solvable".
7. **Two papers and the notes (130 min)** — Triggs §4 and §9 first, then Agarwal et al. in full.
   Write a paragraph on what the decade between the two papers changed. Write the one-page note per
   paper **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the open problems and write a paragraph on
   why it is still open. Gauge-invariant uncertainty is a question you could start research on today.

**Passing bar**: you can multiply out the $LDL^\top$ of (2) on a blank page, you can write the seven
generators of (3), you have code that passes all five conditions of the reproduction task on
BAL-49, you have built a critical motion sequence and shown the rank saturating, and you have notes
on both papers.
