---
id: c7-learned-correspondence-slam
lang: en
title: Learned correspondence and SfM/SLAM
summary: >-
  Derive the gradient of a differentiable bundle adjustment layer by implicit differentiation, and
  show numerically that the usual Gauss-Newton Hessian shortcut introduces a bias that **does not
  go away**. Derives the SuperGlue matching layer as entropically regularised optimal transport,
  covering the dustbin and the entropic bias, and pins down the scale ambiguity of joint
  depth-and-pose learning as a null direction of the Jacobian. Ends by measuring that
  correspondence fails from **structural ambiguity**, not from noise magnitude.
objectives:
  - Derive the gradient of a differentiable BA layer by implicit differentiation of the stationarity condition and quantify the bias of the Gauss-Newton Hessian approximation.
  - Derive the SuperGlue matching layer as entropically regularised optimal transport and explain why the Sinkhorn iteration converges to a doubly stochastic plan.
  - Show numerically that row-wise argmax decoding is a permutation only as $\epsilon \to 0$, and explain the role of the dustbin mass.
  - Show that the loss of joint depth-and-pose learning is invariant to a scale change, and confirm the rank deficiency of one in the Jacobian.
  - Separate experimentally the claim that learned correspondence fails from distribution shift into noise magnitude and structural ambiguity.
tags: [perception, learned-correspondence, differentiable-optimization, slam, scale-ambiguity, research]
---

# Learned correspondence and SfM/SLAM

## Setup and notation

The recommended prerequisites are `c7-bundle-adjustment` in this module (normal equations, the
Schur complement, gauge) and `c7-robust-fitting-ransac` (unidentifiability), together with
learning basics at the level of `c8-policy-gradient-theory`. None of them is locked. The lesson
assumes:

- Optimisation: Gauss–Newton, stationarity conditions, the implicit function theorem, and the
  rudiments of convex duality.
- Linear algebra: null spaces of Jacobians, singular values, block inverses.
- Learning: that backpropagation is the chain rule over a computation graph. No network
  architecture is needed — this lesson is only about **what changes mathematically when a learned
  quantity enters an optimisation layer**.
- Optimal transport: not required. Entropic regularisation and Sinkhorn are derived here.

Notation (continuing the C7 conventions):

| Symbol | Meaning |
|---|---|
| $r(x) \in \mathbb{R}^n$ | residuals; $x \in \mathbb{R}^p$ are the geometric parameters (poses, depths) |
| $J = \partial r/\partial x$ | the Jacobian |
| $w \in \mathbb{R}^n_{>0}$ | the **learned** weights, $W = \operatorname{diag}(w)$ |
| $x^\star(w)$ | the weighted least-squares solution — the output of the differentiable BA layer |
| $H_{\mathrm{GN}} = J^\top W J$ | the Gauss–Newton Hessian |
| $H = H_{\mathrm{GN}} + \sum_i w_i r_i \nabla^2 r_i$ | the full Hessian |
| $S \in \mathbb{R}^{m\times n}$ | the matching score matrix (inner products of learned descriptors) |
| $P$ | the transport plan (soft assignment); $\epsilon$ the entropic regularisation strength |
| $D_j > 0$, $\rho_j = 1/D_j$ | depth and inverse depth of point $j$ |
| $\tau$ | the perturbation norm in descriptor space |

**The stance of this lesson**: neither "learning replaces geometry" nor "geometry beats learning"
is asserted here. What is treated is **what drops out of the guarantees when a learned quantity
enters an optimisation layer**. The learning itself, which needs a GPU, is separated out as an
optional extension.

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the gradient of a differentiable BA layer) [D2]** — the gradient of the solution with
  respect to learned weights $w$ follows from implicit differentiation of the stationarity
  condition $g(x,w) = J(x)^\top W r(x) = 0$:
  $$\frac{\partial x^\star}{\partial w_k} = -H^{-1}\,J_k^\top r_k,
    \qquad H = J^\top W J + \sum_i w_i r_i \nabla^2 r_i \tag{1}$$
  The shortcut $H \approx H_{\mathrm{GN}}$, which implementations commonly use, gives a **biased
  gradient whenever the residual is non-zero**, and that bias does not shrink with more iterations.
- **R2 (the matching layer is entropic optimal transport) [D2]** — for a score matrix augmented
  with a dustbin,
  $$P^\star = \arg\max_{P \in \mathcal{U}(a,b)} \langle P, S\rangle + \epsilon H(P),
    \qquad H(P) = -\sum_{ij}P_{ij}\log P_{ij} \tag{2}$$
  has the solution $P^\star = \operatorname{diag}(u)\,K\,\operatorname{diag}(v)$ with
  $K = \exp(S/\epsilon)$, where $u, v$ are the fixed point of the Sinkhorn iteration
  $u \leftarrow a \oslash Kv$, $v \leftarrow b \oslash K^\top u$.
- **R3 (decoding is a permutation only as $\epsilon \to 0$) [D2]** — the correspondences obtained
  by a row-wise argmax are **not a permutation** when $\epsilon$ is large (two rows pick the same
  column). As $\epsilon \to 0$, $P^\star$ converges to the solution of the assignment problem and
  only then agrees with the Hungarian solution. The dustbin mass shrinks with $\epsilon$ as well.
- **R4 (the scale ambiguity of joint depth-and-pose learning) [D2]** — the monocular
  reprojection/photometric loss is **exactly invariant** under
  $$(D_j,\; t_i) \;\longmapsto\; (sD_j,\; s\,t_i), \qquad s > 0 \tag{3}$$
  so the Jacobian has rank deficiency exactly one, with the generator of that null direction
  $\delta D_j = D_j$, $\delta t_i = t_i$, $\delta R_i = 0$. Scale does not come out of the data.
- **R5 (the generalisation failure of correspondence is structural) [D2]** — perturbing descriptors
  isotropically does not break matching. What breaks it is **structural ambiguity** (repeated
  patterns, duplicated structure), which the ratio test on local descriptors cannot fix in
  principle — the reason global-context matchers exist, and they hit the same wall.

## Derivation

### R1 — the gradient of a differentiable BA layer

Using the weighted least-squares problem with learned weights $w$,

$$x^\star(w) = \arg\min_x \tfrac12 \sum_i w_i\, r_i(x)^2$$

as a layer of a network is differentiable bundle adjustment (the DBA layer of must-read 1). What
training needs is $\partial x^\star/\partial w$. Now $x^\star$ is defined **implicitly** by the
stationarity condition

$$g(x, w) := J(x)^\top W\, r(x) = 0 \tag{4}$$

and applying the implicit function theorem to (4),

$$\frac{\partial x^\star}{\partial w_k}
  = -\left(\frac{\partial g}{\partial x}\right)^{-1}\frac{\partial g}{\partial w_k}.$$

Compute the two partials. Since $\partial g/\partial w_k$ touches only the $k$-th entry of $W$,

$$\frac{\partial g}{\partial w_k} = J_k^\top r_k$$

($J_k$ is the $k$-th row of $J$ and $r_k$ a scalar). And $\partial g/\partial x$ is the **full
Hessian**:

$$\frac{\partial g}{\partial x}
  = J^\top W J + \sum_i w_i r_i \nabla^2 r_i(x) = H. \tag{5}$$

The second term comes from differentiating $J^\top$ itself, with $\nabla^2 r_i$ the Hessian of the
residual. That is (1).

**The shortcut implementations take**: backpropagate through
$H_{\mathrm{GN}} = J^\top W J$, which is free because Gauss–Newton has already factorised it. Let
us measure what that costs.

Measured (nonlinear residual $r_i(x) = a_i^\top x + \tfrac12(a_i^\top x)^2 - b_i$, $n = 30$,
$p = 4$, with $\lVert J^\top W r\rVert = 2.3\times10^{-16}$ after convergence):

| weight $k$ | relative error of (1) with $H_{\mathrm{GN}}$ | relative error with the full $H$ |
|---|---|---|
| 0 | $6.92\times10^{-2}$ | $1.83\times10^{-10}$ |
| 3 | $3.99\times10^{-2}$ | $1.11\times10^{-9}$ |
| 11 | $8.32\times10^{-2}$ | $1.35\times10^{-9}$ |
| 29 | $5.70\times10^{-2}$ | $4.87\times10^{-10}$ |

(The reference is a central difference of the converged solution.) With the full Hessian the
gradient is right to machine precision; the Gauss–Newton shortcut is **4 to 8% wrong**. Its size
is the size of the dropped term:
$\lVert \sum_i w_i r_i \nabla^2 r_i\rVert / \lVert J^\top W J\rVert = 0.086$.

**Where the assumptions break — and where they do not**:
(1) This bias **does not disappear with more iterations**. Measured: unrolling the solved problem
for 1, 2, 3, 5, 10 and 60 GN iterations and taking central differences gives relative differences
$1.08\times10^{-1} \to 4.4\times10^{-2} \to \cdots \to 3.87\times10^{-2}$, **flattening at
$3.87\%$** — convergence makes the solution exact, but the gradient bias comes from the Hessian
approximation.
(2) Conversely, **a small residual means a small bias**: the dropped term is proportional to
$w_i r_i$, so $H \to H_{\mathrm{GN}}$ as $r \to 0$. For a well-converged BA (reprojection error
under a pixel) the shortcut is sound; early in training, or with outliers still present, it is not.
**"Is the gradient of a DBA layer trustworthy?" is a question about the size of the residual.**
(3) For a linear model $\nabla^2 r_i = 0$, the two Hessians coincide and the bias is zero
(measured: relative error $3.4\times10^{-9}$). A linear test case hides this bug entirely — a
nonlinear one is needed.

### R2 — the matching layer as optimal transport

Given scores $S_{ij} = \langle d_i^A, d_j^B\rangle$ from learned descriptors, the matching layer is
the mathematical statement of "pair them one to one, but allow a feature to have no partner".
First add a dustbin: extend $S$ by one row and one column into
$\bar{S} \in \mathbb{R}^{(m+1)\times(n+1)}$ whose entries are a learnable constant $z$. The
marginals are

$$a = (\underbrace{1,\dots,1}_{m}, n), \qquad b = (\underbrace{1,\dots,1}_{n}, m)$$

— each feature spends mass 1 and the dustbin absorbs whatever is left. The assignment problem is

$$\max_{P \ge 0,\; P\mathbf{1} = a,\; P^\top\mathbf{1} = b} \langle P, \bar{S}\rangle$$

which is a linear program whose derivative is zero almost everywhere, so it cannot be trained
through. Adding the entropy term gives (2), whose solution follows from Lagrangian duality. With
multipliers $\alpha, \beta$ for the constraints,

$$\mathcal{L} = \langle P, \bar{S}\rangle - \epsilon\sum_{ij}P_{ij}\log P_{ij}
  + \alpha^\top(a - P\mathbf{1}) + \beta^\top(b - P^\top\mathbf{1})$$

and $\partial\mathcal{L}/\partial P_{ij} = \bar{S}_{ij} - \epsilon(\log P_{ij} + 1)
- \alpha_i - \beta_j = 0$ gives

$$P_{ij} = \underbrace{e^{-\alpha_i/\epsilon - 1/2}}_{u_i}\;
           \underbrace{e^{\bar{S}_{ij}/\epsilon}}_{K_{ij}}\;
           \underbrace{e^{-\beta_j/\epsilon - 1/2}}_{v_j} \tag{6}$$

that is, $P = \operatorname{diag}(u)K\operatorname{diag}(v)$. All that is left is to find $u, v$
satisfying the marginals, and enforcing the two constraints alternately gives

$$u \leftarrow a \oslash (Kv), \qquad v \leftarrow b \oslash (K^\top u) \tag{7}$$

($\oslash$ is elementwise division). This is the Sinkhorn iteration, and it converges whenever
$K > 0$ (Sinkhorn–Knopp; see the proof sketch). Each iteration is a matrix-vector product and is
therefore **differentiable**, which is what lets the whole matching layer be backpropagated. The
matching layer of SuperGlue is exactly this (must-read 2, §3).

**The two faces of $\epsilon$**: a large $\epsilon$ spreads the solution out (high entropy) so
gradients flow well but the assignment is blurred. As $\epsilon \to 0$, (2) returns to the linear
program and gives the exact assignment, but the dynamic range of $K$ explodes like
$e^{\Delta S/\epsilon}$ and breaks numerically (a log-domain implementation is required).

### R3 — decoding: when is the argmax a permutation?

The rule used to extract correspondences from a learned $P$ is usually "row-wise argmax, mutual
check, threshold". There is **no guarantee** that this gives a valid assignment (a permutation).
Measured ($m = 10$, a hard instance with only $+0.8$ added on the ground-truth matches, 5000
Sinkhorn iterations):

| $\epsilon$ | duplicate columns in the row argmax | $\max P$ | dustbin mass | permutation | matches Hungarian |
|---|---|---|---|---|---|
| 2.0 | 3 | 0.198 | 4.96 | no | — |
| 1.0 | 1 | 0.445 | 4.71 | no | — |
| 0.5 | 1 | 0.804 | 4.00 | no | — |
| 0.2 | 1 | 0.988 | 2.58 | no | — |
| 0.05 | 1 | 1.000 | 0.758 | no | — |
| 0.01 | 0 | 1.000 | 0.024 | **yes** | **yes** |

How to read it. (1) As $\epsilon$ shrinks, $\max P$ goes to 1 and the entropy to zero, and yet
**the duplicate survives even at $\epsilon = 0.05$**. "$P$ is almost binary" and "the argmax of
$P$ is a permutation" are different statements. (2) At $\epsilon = 0.01$ it becomes a permutation
for the first time, and there it agrees with the Hungarian (exact assignment) solution **completely**.
(3) Note too that the dustbin mass shrinks with $\epsilon$ — changing $\epsilon$ changes the
sensitivity of the "no match" decision along with everything else. $\epsilon$ is a single
temperature knob that moves **accuracy and rejection rate together**.

On an easy instance ($+3.0$ added on the ground-truth matches), the argmax accuracy is 1.00 even at
$\epsilon = 1.0$, and at $\epsilon = 0.03$ the score matched Hungarian to six decimals
($24.170641$ against $24.170641$). **Easy data hides this problem entirely** — the classic shape
of a saturated benchmark.

### R4 — the scale ambiguity of joint depth-and-pose learning

The loss of monocular joint depth-and-pose learning back-projects points with the predicted depth
$D_j$ and projects them into another frame with the predicted pose $(R_i, t_i)$, measuring the
reprojection (or photometric) error. With the bearing $\bar{x}_j$ fixed in the reference frame, a
point is $X_j = D_j\bar{x}_j$ and in frame $i$

$$X_{c} = R_i\,D_j\bar{x}_j + t_i, \qquad \pi(X_c) = f\,\frac{X_{c,xy}}{X_{c,z}}.$$

Substituting the transform (3) gives $X_c \mapsto R_i sD_j\bar{x}_j + st_i = s\,X_c$, and since
$\pi$ sees only the direction of $X_c$, $\pi(sX_c) = \pi(X_c)$ — **the loss is exactly invariant**.
Differentiating in $\epsilon$ reads off the generator $\delta D_j = D_j$, $\delta t_i = t_i$,
$\delta R_i = 0$.

Measured (4 cameras, 30 points, bearings fixed, $6\cdot4 + 30 = 54$ parameters,
$J \in \mathbb{R}^{240\times54}$): the smallest singular values break at
$[\dots,\ 1.8742,\ 1.90\times10^{-8}]$ with
$\sigma_{53}/\sigma_{54} = 9.89\times10^{7}$, the rank deficiency is **exactly one**, and the scale
generator satisfies $\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert) = 2.7\times10^{-12}$. The
reason it is one rather than the seven gauge freedoms of `c7-bundle-adjustment` is that the
bearings are fixed in the reference frame — rotations and translations change the bearings, so they
are no longer invariances.

**Where the assumptions break (and this matters in practice)**:
(1) **Per-frame median scaling.** The procedure commonly used in monocular depth evaluation is to
scale the predicted depth to the median of the ground truth and then measure the error. That spends
the freedom (3) separately in every frame, and therefore **erases scale drift from the metric**. It
systematically disagrees with an evaluation that allows a single global $s$ for the whole trajectory
(the global scale alignment of ATE). When reading a depth table in a paper, the first question is
how many times the scale was aligned.
(2) **Scale does not come from the data.** Without extra information (a stereo baseline, an IMU, a
known object size, the height of the ground plane) metric scale cannot be recovered. A claim that
"the network learns metric scale from monocular input" is a claim that it learned the **prior** of
the training data (camera height, typical scene scale), and it breaks when the distribution changes.
(3) The null direction is a flat direction of the loss, so the optimiser **drifts freely** along it.
Without a normalisation (fixing the mean depth to 1, say) training is numerically unstable.

### R5 — where the generalisation failure of correspondence comes from

"Learned correspondence breaks when the domain changes" is a common statement, but **what breaks
it** has to be measured separately. Two things are applied independently in descriptor space:
(a) an isotropic perturbation of norm $\tau$ and (b) structural ambiguity (replacing some
descriptors with copies of other points — a model of a repeated pattern).

Measured (synthetic descriptor model, $d = 128$, $n = 400$, unit norm, mutual nearest neighbour
plus a Lowe ratio test at 0.8, averaged over 12 runs; the typical inter-descriptor distance is
$\sqrt{2}$):

| Condition | precision | recall | matches kept |
|---|---|---|---|
| in-distribution $\tau = 0.30$ | 1.000 | 1.000 | 400/400 |
| perturbation $\times2$ ($\tau = 0.60$) | 1.000 | 1.000 | 400/400 |
| perturbation $\times3$ ($\tau = 0.90$) | 1.000 | 1.000 | 400/400 |
| repeated structure 20% | 0.939 | 0.643 | 274/400 |
| repeated structure 40% | 0.691 | 0.363 | 210/400 |

**Tripling the perturbation does not break matching at all.** In high dimension, isotropic noise
does not easily invert the correct nearest-neighbour relation (concentration of measure). What
breaks it is structure — with 20% duplicated structure the recall drops to 0.64, with 40% to 0.36,
and the precision falls too.

It is important not to over-read this. It is a **synthetic model** and it does not measure the
generalisation of a real network. Exactly one thing can be claimed: **the ratio test is a device
that demands "the second nearest neighbour is far", so when the ambiguity is structurally present
in the data it is powerless in principle.** A matcher that sees only local descriptors cannot get
past this wall, which is why SuperGlue-style methods add **global context** (attention over all the
other features) and an **assignment constraint** (the marginals of R2). And even that fails when
repeated structure dominates the scene — that is open problem 1.

## Proof sketch

### R2 — convergence of the Sinkhorn iteration and the form (6)

**Hypotheses** H1: $S$ is finite, so $K = \exp(\bar{S}/\epsilon) > 0$ entrywise. H2: $a > 0$,
$b > 0$ and $\sum a = \sum b$. H3: $\epsilon > 0$.
**Conclusions** C1: the solution of (2) is unique and has the form (6). C2: the iteration (7)
converges to it.

**Strategy**: uniqueness from a strongly convex objective, the form from Lagrangian duality, and
convergence as a contraction in the Hilbert projective metric.

1. **C1 (uniqueness)**: $-H(P) = \sum P_{ij}\log P_{ij}$ is **strongly convex** on the simplex and
   $\langle P, \bar{S}\rangle$ is linear, so the objective is strongly concave. The feasible set
   $\mathcal{U}(a,b)$ is a non-empty compact convex set (H2), so the maximiser is unique.
2. **C1 (the form)**: the first-order condition of the Lagrangian above gives (6). For
   $\log P_{ij}$ to be differentiable there we need $P_{ij} > 0$, and since the gradient of the
   entropy term diverges to $-\infty$ on the boundary, the optimum is an **interior point** — that
   is what entropic regularisation buys, and simultaneously the price it charges ("no exact zeros").
3. **C2 (convergence)**: (7) applies diagonal scalings to $K$ alternately, and for $K > 0$ (H1) the
   Sinkhorn–Knopp theorem gives convergence to a unique $(u,v)$ up to a scalar. The rate is
   **linear (geometric)** in the Hilbert projective metric with contraction factor
   $\big(\frac{\sqrt{\kappa}-1}{\sqrt{\kappa}+1}\big)^2$ where $\kappa = \max K / \min K$. As
   $\epsilon \to 0$, $\kappa = e^{(\max\bar S - \min \bar S)/\epsilon}$ explodes and the
   contraction factor approaches 1 — which is what the measurements show: at $\epsilon \le 0.1$ a
   marginal error of $2.5\times10^{-4}$ remained, against $10^{-16}$ at $\epsilon = 1.0$.
   (Left out: the proof of the Sinkhorn–Knopp theorem and the contraction factor. See the
   computational optimal transport text of Peyré and Cuturi.)
4. **The $\epsilon \to 0$ limit**: $P^\star(\epsilon)$ converges to the solution set of the linear
   program (the entropy term vanishes as $O(\epsilon)$). If the optimal assignment is unique it
   converges to that assignment's indicator matrix. Measured: at $\epsilon = 0.01$ the argmax agreed
   with the Hungarian solution exactly.
5. **Remove a hypothesis**: if H1 fails and $K$ has zeros (a forbidden pair, $S_{ij} = -\infty$),
   the convergence guarantee is void and depending on the support there may be no solution. If
   $\sum a = \sum b$ in H2 fails, $\mathcal{U}(a,b)$ is empty and transport is undefined — which is
   exactly why the dustbin masses were chosen as $n$ and $m$, to balance the two. If $\epsilon = 0$
   in H3, the interior-point argument of step 2 collapses and differentiability is lost.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Derive (1) and (5) from (4). In particular show line by line where the
term $\sum_i w_i r_i \nabla^2 r_i$ in $\partial g/\partial x$ comes from, and write $\nabla^2 r_i$
explicitly for the residual $r_i(x) = a_i^\top x + \tfrac12(a_i^\top x)^2 - b_i$.
*Solution sketch*: expanding $g = J^\top W r$ by the product rule gives
$(\partial J^\top/\partial x)Wr$ and $J^\top W J$; the components of the first are
$\sum_i w_i r_i \nabla^2 r_i$. Here $\nabla^2 r_i = a_ia_i^\top$.

**P2 (proof, ★★★, R2)** Prove that the solution of (2) is unique and has the form (6). Then show
that $P^\star(\epsilon)$ converges to the optimal set of the linear program as $\epsilon \to 0$, and
say what it converges to **when the optimal assignment is not unique**.
*Strategy and key inequality*: strong concavity on a compact convex set gives uniqueness. For the
limit, squeeze both sides of an inequality of the form
$\langle P^\star, \bar S\rangle \ge \langle P_{\mathrm{LP}}, \bar S\rangle - \epsilon(H(P^\star) - H(P_{\mathrm{LP}}))$.
With several optima it converges to the **maximum-entropy** optimal solution.

**P3 (numerical, ★★, R1)** Build your own nonlinear residual example and compute (1) with (a)
$H_{\mathrm{GN}}$ and (b) the full $H$, comparing both against central differences. Report (c) the
relative size of the dropped term
$\lVert\sum w_ir_i\nabla^2r_i\rVert/\lVert J^\top WJ\rVert$ alongside (d) the relative error of (a).
*Answer (reference measurements)*: the relative error of (a) is
$4.0\times10^{-2}$ to $8.3\times10^{-2}$, that of (b) is $10^{-10}$ to $10^{-9}$, and (c) is
$0.086$. Tolerance: (b) must be at most $10^{-7}$, and (a) and (c) must agree in order of magnitude
— that they are the same size is the point. Check: making the residual linear drops the error of
(a) below $10^{-8}$.

**P4 (numerical, ★★, R2·R3)** Implement Sinkhorn and tabulate, for
$\epsilon \in \{2, 1, 0.5, 0.2, 0.05, 0.01\}$, (a) the marginal error, (b) the number of duplicate
columns in the row argmax, (c) the dustbin mass and (d) agreement with the Hungarian solution. Use
a hard score matrix with only $+0.8$ added on the ground truth.
*Answer (reference measurements)*: duplicate columns 3 at $\epsilon = 2$, 1 from $1$ down to
$0.05$, and 0 at $0.01$, where it agrees with Hungarian. Dustbin mass $4.96 \to 0.024$. Tolerance:
the trend must match and the permutation/agreement at $\epsilon = 0.01$ must reproduce. Check: on an
easy instance with $+3.0$ the accuracy must be 1.00 already at $\epsilon = 1$.

**P5 (derivation, ★, R4)** Show the invariance (3) from $\pi(sX_c) = \pi(X_c)$ and write the scale
generator. Then show with equations how that null direction disappears in a **stereo** setting where
the baseline $b$ is known.
*Solution sketch*: the invariance is that the projection is homogeneous of degree zero. In stereo
$t_{\text{stereo}}$ is a **constant**, so the $t \mapsto st$ part of (3) is unavailable; scaling the
depth alone changes the disparity by $1/s$ and the residual changes — the null direction closes.

**P6 (implementation, ★★★, R1·R4)** Implement a differentiable BA layer and (a) compute the
gradient with respect to the learned weights using the full Hessian, and (b) confirm the scale null
direction numerically in a monocular depth-and-pose setting.
*Rubric*: (a) the gradient matches central differences to $10^{-7}$; (b) the rank deficiency is
exactly one and the generator lies in the null space; (c) you report the bias of the
$H_{\mathrm{GN}}$ shortcut numerically; (d) you compare convergence behaviour with and without a
normalisation on the depths.

**P7 (counterexample, ★★, R3·R5)** (a) Construct a score matrix on which the Sinkhorn argmax is not
a permutation, and (b) construct data (repeated structure) on which the ratio test fails in
principle, showing precision and recall dropping. Then (c) say what adding the mutual
nearest-neighbour check improves and what it leaves untouched.
*Property checklist*: (a) two rows have their maximum in the same column and $\epsilon$ is large;
(b) raising the duplicate fraction to 20% and 40% makes the recall decrease monotonically; (c) the
mutual check raises precision but does not recover recall; (d) a paragraph arguing that this failure
is **ambiguity in the data**, not "the model has not learned enough".

**P8 (paper, ★★, R1·R2)** Read §3 of DROID-SLAM and §3 of SuperGlue and (a) tabulate which
quantities each paper learns and which it leaves to optimisation. (b) Find in DROID-SLAM how the
gradient of the DBA layer is computed (implicit or unrolled, and with which Hessian) and contrast it
with R1 here. (c) Write down what each paper's reported metric (ATE, matching precision) **hides**.
*Rubric*: for (b), writing "the paper does not state it" where that is the case passes (presenting a
guess as fact fails). For (c), naming the scale alignment procedure behind ATE (failure mode (1) of
R4) is an excellent answer.

## Paper reading

**Two must-reads.** Write a one-page note on each, using the ten fixed questions
(`lesson-standard.md` §5). Read in three passes, and attack questions 4, 5, 6 and 7 in the third.
For the full bibliography, including the recommended papers, run
`rc papers c7-learned-correspondence-slam`.

1. **Teed & Deng, "DROID-SLAM: deep visual SLAM for monocular, stereo, and RGB-D cameras"
   (2021, NeurIPS)** — role: `frontier`. <https://arxiv.org/abs/2108.10869> (§3 is the core.)
   Extra questions: (a) what does the DBA layer learn and what does the optimisation handle — point
   at $w$ and $x$ in the notation of R1. (b) Where does the scale of the monocular mode come from
   (R4)? How many times was the scale aligned in the reported ATE? (c) What kind of failure case do
   you think the paper does not report?
2. **Sarlin, DeTone, Malisiewicz & Rabinovich, "SuperGlue: learning feature matching with graph
   neural networks" (2020, CVPR)** — role: `standard`. <https://arxiv.org/abs/1911.11763>
   (§3 is the core.)
   Extra questions: (a) are the number of Sinkhorn iterations and $\epsilon$ stated in the paper?
   Where do those values sit in the table of R3? (b) What breaks without the dustbin? (c) Does
   global attention resolve the ambiguity of repeated structure **in principle**, or does it
   mitigate it with a prior (R5)?

**The ten fixed questions**: (1) which problem under which assumptions; (2) what exactly earlier
work could not do; (3) the core idea in one equation; (4) what is guaranteed and **what is not**;
(5) the independent and dependent variables and the baselines, fairly tuned or not; (6) whether the
metric matches the claim, and whether variance and seeds are reported; (7) what is missing for
reproduction; (8) the first assumption to doubt if the result were wrong; (9) time and memory
complexity and real-time behaviour; (10) what you would change to go beyond it in a year.

**Recommended**: DUSt3R (a design that drops almost all the constraints) and Triggs et al. 2000 §4
(the reference point on the optimisation side).

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 10 minutes in total, numpy and
scipy only. The input is a generator this lesson specifies; no external data and no GPU are needed.

> **Stated difference from the blueprint**: the reproduction task in the design is "run a pretrained
> DROID-SLAM-class model on one TUM RGB-D sequence and match the reported ATE to within 20%". That
> task needs a CUDA GPU in practice, and §6 of the lesson standard requires any task that may need a
> GPU to be marked **optional (R4)**. So this lesson makes the mandatory conditions **four checks
> decidable on a CPU** and separates the original ATE reproduction out as the **optional extension
> (R4)** below. Both target the same key results (R1 and R4).

**Generators (fixed)**: (a) for R1 — the nonlinear residual
$r_i(x) = a_i^\top x + \tfrac12(a_i^\top x)^2 - b_i$ with $a_i \sim N(0, I_4)$,
$b_i \sim 0.2\,N(0,1)$, $n = 30$ and weights $w_i \sim U(0.3, 1.5)$. (b) For R2 — an $m = 10$ score
matrix $S \sim N(0,1)$ with $+0.8$ added on the ground-truth permutation. (c) For R4 — 4 cameras
(rotations $\sim 0.15$ rad, translations $\sim 0.3$), 30 points in
$[-1,1]^2 \times [4,6]$, $f = 500$, with the bearings of the reference frame held fixed. Report with
a fixed seed.

All **four conditions** must hold to pass. Every reference value was measured for this lesson.

1. **Correctness of the differentiable BA gradient**: at the solution
   ($\lVert J^\top Wr\rVert < 10^{-12}$), (1) computed with the **full Hessian** matches central
   differences to a relative error of $10^{-7}$ (reference: $1.8\times10^{-10}$ to
   $1.4\times10^{-9}$ over four weights).
2. **The bias of the Gauss–Newton shortcut**: on the same problem, the gradient computed with
   $H_{\mathrm{GN}}$ has relative error **at least** $10^{-2}$, of the same order as the relative
   size of the dropped term $\lVert\sum w_ir_i\nabla^2r_i\rVert/\lVert J^\top WJ\rVert$ (reference:
   error $4.0$ to $8.3\times10^{-2}$, dropped term $0.086$). And raising the number of GN iterations
   to 1, 2, 5 and 60 does not bring that bias below $10^{-2}$ (reference: it flattens at
   $3.87\times10^{-2}$).
3. **Sinkhorn and decoding**: for $\epsilon \in \{2, 1, 0.5, 0.2, 0.05, 0.01\}$, (a) the marginal
   error is at most $10^{-12}$ for $\epsilon \ge 0.2$; (b) the number of duplicate columns in the row
   argmax decreases monotonically with $\epsilon$ and reaches 0 at $\epsilon = 0.01$; (c) there it
   agrees **exactly** with `scipy.optimize.linear_sum_assignment`; (d) the dustbin mass decreases
   monotonically (reference: duplicates 3/1/1/1/1/0, dustbin $4.96 \to 0.024$).
4. **The scale null space**: with generator (c) the rank deficiency of the Jacobian is **exactly
   one** ($\sigma_{n-1}/\sigma_n > 10^{6}$, reference $9.89\times10^{7}$) and the scale generator
   $(\delta D_j, \delta t_i, \delta R_i) = (D_j, t_i, 0)$ satisfies
   $\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert) < 10^{-8}$ (reference $2.7\times10^{-12}$).

**Optional extension (R4, may need a GPU — optional only)**: run a pretrained DROID-SLAM on one TUM
RGB-D sequence such as `freiburg1_desk`, measure the ATE RMSE and match the value reported in the
paper **to within 20%**. When reporting, state (1) whether the scale was aligned once globally or
per frame, (2) the association tolerance of the evaluation script (TUM's `evaluate_ate.py`), and
(3) the seeds and the number of runs. R4 is **optional** and is not a condition for passing this
lesson.

**State this in the report**: the conclusion of condition 2 — "the gradient of a differentiable
optimisation layer may be replaced by the Gauss–Newton Hessian only when the residual is small" —
and the implication of condition 4 for evaluation procedures (failure mode (1) of R4).

**Baselines**: (1) central differences (conditions 1 and 2); (2)
`scipy.optimize.linear_sum_assignment` (condition 3); (3) the Sinkhorn implementation in
`SuperGluePretrainedNetwork` (iteration count, log-domain handling) — reading the code is enough.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| the gradient of condition 1 is 10% off from central differences | the second-order term was left out of $\partial g/\partial x$ | print $\lVert H - H_{\mathrm{GN}}\rVert$ and see that it is non-zero |
| it is right on a linear example and wrong on a nonlinear one | the same cause — the two Hessians coincide in the linear case | add a quadratic term to the residual and look again |
| the central differences are noisy | not converged, or an unsuitable step $h$ | drive $\lVert J^\top Wr\rVert$ below $10^{-12}$ first |
| Sinkhorn returns `nan` | $\exp(S/\epsilon)$ overflows at small $\epsilon$ | move to the log domain (log-sum-exp) |
| the marginals do not match | the dustbin masses were not set to $n$ and $m$, so $\sum a \ne \sum b$ | print and compare $\sum a$ and $\sum b$ |
| the rank deficiency is 7 rather than 1 | the bearings were not fixed, so the world similarity gauge is still alive | check that the reference frame's bearings are constants |
| the rank deficiency is 0 | a normalisation (mean depth fixed to 1, say) is already applied | turn it off and look again — that normalisation *is* the gauge fixing |

## Open problems

- **(open problem) calibrating learned weights into an observation noise model** — the $w$ of a DBA
  layer is trained only to reduce the loss, and there is no basis for reading it as $1/\sigma^2$.
  Yet every covariance and uncertainty interpretation of BA rests on exactly that reading. Current
  approaches: the learned confidences of [DROID-SLAM](https://arxiv.org/abs/2108.10869), and the
  noise-scale marginalisation of [MAGSAC++](https://arxiv.org/abs/1912.05909). What is missing: a
  procedure that calibrates learned weights so that BA's uncertainty reporting is restored. This
  overlaps the gauge-invariant uncertainty problem of `c7-bundle-adjustment`.
- **(open problem) when is imposing geometric constraints a net loss** — designs that drop almost
  all the constraints ([DUSt3R](https://arxiv.org/abs/2312.14132)) coexist with designs that keep
  them through differentiable BA ([DROID-SLAM](https://arxiv.org/abs/2108.10869)), and there is no
  model that predicts the crossover from scene statistics (texture, viewpoint change, fraction of
  repeated structure). The measurements of R5 go only as far as saying that local descriptors are
  powerless in principle when the ambiguity is structural. What is missing: a criterion that
  predicts the benefit of the constraints from the scene **in advance**.
- **(open problem) an evaluation convention that does not hide the scale ambiguity** — as R4 showed,
  per-frame scale alignment erases drift from the metric. There is no standard for which alignment,
  and how many of them, a monocular depth or trajectory evaluation may use, which makes numbers from
  different papers effectively incomparable. Current approaches: the single-global-alignment
  convention of TUM and KITTI, and scale-invariant metrics in the
  [DUSt3R](https://arxiv.org/abs/2312.14132) line. What is missing: a convention that states the
  alignment degrees of freedom and reports the corresponding error decomposition.
- **(open problem) convergence guarantees for differentiable optimisation layers** — during training
  a DBA layer passes an optimisation that has **not yet converged**. The premise of the implicit
  differentiation (1), namely stationarity, then fails, and unrolling trades memory against bias.
  There is no theory for when the layer's output and its gradient are both stable. Current approach:
  a fixed iteration count plus unrolling, as in
  [DROID-SLAM](https://arxiv.org/abs/2108.10869). What is missing: an error bound for the gradient
  of a non-converged optimisation layer.

## Concept check

Run `rc quiz c7-learned-correspondence-slam`. The quiz is for **concept checking only**; the real
work is the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: what happens when a DBA layer's gradient is backpropagated through the
Gauss–Newton Hessian; whether the row argmax of a Sinkhorn plan is always a permutation; the rank
deficiency of joint depth-and-pose learning (one); what actually broke matching in the synthetic
descriptor experiment; and why per-frame median scaling is a problem in monocular depth evaluation.

## How to study this stage

1. **Do the implicit differentiation by hand (60 min)** — derive (1) and (5) from (4) on a blank
   page. Seeing the second-order term appear where $J^\top$ is differentiated is half of this lesson
   (P1).
2. **Verify with a linear and then a nonlinear model (90 min)** — implement with a linear residual
   first and confirm that the GN shortcut and the full Hessian give the **same** answer (both match
   central differences), then add the quadratic term and watch them diverge (conditions 1 and 2).
   Feel for yourself why an implementation tested only on a linear case hides the bug.
3. **Derive Sinkhorn from the dual (60 min)** — write out how the first-order condition of the
   Lagrangian gives (6), and confirm that the iteration (7) is just enforcing the two constraints
   alternately. Then reimplement it in the log domain and see the `nan` at small $\epsilon$ disappear.
4. **Distrust the decoding (60 min)** — sweep $\epsilon$, measuring the duplicate-column count and
   the dustbin mass, and compare with Hungarian (condition 3). You have to run **both** an easy and
   a hard instance to see the phenomenon at all.
5. **Look at the scale null direction (60 min)** — build the Jacobian with generator (c), print the
   singular values and check that the scale generator is in the null space (condition 4). Then fix
   the mean depth to 1 and see the deficiency become zero — confirming with your own eyes that **a
   normalisation is a gauge fixing**.
6. **Separate the causes of failure (60 min)** — in the descriptor experiment, raise the noise and
   the structure separately (P7). This is where the phrase "it is weak to domain change" splits into
   what it actually means.
7. **Two papers and the notes (130 min)** — read SuperGlue §3 first, against R2 and R3, then find
   $w$ and $x$ in DROID-SLAM §3. Write the one-page note per paper **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the open problems and write a paragraph on
   why it is still open. Calibrating the learned weights is one you could start experimenting on
   today.

**Passing bar**: you can derive (1) and (5) on a blank page, you can exhibit the bias of the GN
shortcut numerically, you have derived and implemented Sinkhorn from the dual, you have confirmed
the scale null direction, you have code that passes all four conditions of the reproduction task,
and you have notes on both papers.
