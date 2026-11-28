---
id: s1-vio-systems
lang: en
title: An anatomy of VIO systems
summary: >-
  Split visual-inertial odometry into its filter-based (MSCKF) and optimisation-based forms, and
  prove with a projector identity that MSCKF's null-space projection is **exact marginalisation of
  the feature, not an approximation**. Confirms through the rank of the Jacobian that the
  unobservable subspace of monocular VIO is exactly four-dimensional (yaw about gravity plus three
  translations), and measures that roll, pitch and scale are only *weakly* observable — so over a
  short window they are numerically indistinguishable from unobservable. Ends with a Monte Carlo
  showing that a filter pays its price in the **tail of the consistency statistic**, not in RMSE.
objectives:
  - Write the state and factor structure of VIO and explain where the filter form and the optimisation form each pay.
  - Prove with a projector identity that MSCKF's null-space projection is equivalent to exact marginalisation of the feature.
  - Confirm that the unobservable subspace of monocular VIO is four-dimensional, from the generators and the rank of the Jacobian.
  - Show numerically that the observability of roll, pitch and scale grows with the IMU interval, and connect that to the difficulty of initialisation.
  - Measure the difference between a filter and batch optimisation with NEES, and say what an RMSE-only evaluation misses.
tags: [slam, vio, msckf, observability, consistency, research]
---

# An anatomy of VIO systems

## Setup and notation

This is the first lesson of module S1. The recommended prerequisites in the design are C1 (Lie
groups), C5 (state estimation) and C7 (perception and 3D representations); of what exists in the
course today, `c7-bundle-adjustment` (normal equations, the Schur complement, gauge) and
`c1-so3-se3-exponential` (exponential coordinates) are the closest. None of them is locked — if you
pass the self-diagnosis below, start here. The lesson assumes:

- Estimation: linear Gaussian models, information matrices, marginalisation, the predict and update
  steps of an EKF, and NEES.
- Linear algebra: orthogonal projectors, null spaces, the SVD, the Schur complement.
- Lie groups: right increments on $SO(3)$ with $\exp/\log$, and taking Jacobians on a manifold.
- Optimisation: Gauss–Newton, relative factors, gauge fixing.

Notation (continuing the C7 conventions):

| Symbol | Meaning |
|---|---|
| $R_i, p_i, v_i$ | rotation, position and velocity of keyframe $i$ in world coordinates |
| $b_a, b_g$ | accelerometer and gyroscope biases |
| $g$ | the gravity vector in world coordinates, $g_u = g/\lVert g\rVert$ |
| $f_k$ | the 3D position of feature $k$ |
| $\Delta R_{ij}, \Delta v_{ij}, \Delta p_{ij}$ | IMU preintegration measurements |
| $H_x, H_f$ | the state and feature Jacobians of a feature's observation residual |
| $N$ | an orthonormal basis for the **left** null space of $H_f$, $N^\top H_f = 0$ |
| $P_f = H_f(H_f^\top H_f)^{-1}H_f^\top$ | the orthogonal projector onto $\operatorname{range}(H_f)$ |
| $\Lambda, \eta$ | the information matrix and information vector |
| NEES | $e^\top \Sigma^{-1} e$ — expectation $d$ for a consistent estimator of dimension $d$ |

**Conventions**: rotation increments are **right increments**
($R \leftarrow R\exp(\widehat{\delta\phi})$) and every Jacobian is taken in those coordinates.
Errors are reported as both **ATE** (absolute trajectory error) and **NEES** — one of this lesson's
conclusions is precisely that "RMSE alone hides the difference between a filter and an optimiser".

## Self-diagnosis before starting

This is the first lesson of the module, so check your readiness first. **Prerequisite lessons are
not locked** — if you can solve all of the following, skip the recommended prerequisites. **If two
or more stop you**, going back to the lesson named in parentheses is faster.

1. For a Gaussian with information matrix
   $\Lambda = \begin{bmatrix} A & B \\ B^\top & C\end{bmatrix}$, what information matrix and
   information vector remain after marginalising the second block?
   (`c7-bundle-adjustment`)
   **Answer**: $\Lambda' = A - BC^{-1}B^\top$ and $\eta' = \eta_1 - BC^{-1}\eta_2$ (the Schur
   complement).
2. For $H \in \mathbb{R}^{m\times n}$ with $m > n$ and full column rank, what are the eigenvalues
   of $P = H(H^\top H)^{-1}H^\top$ and what is $\operatorname{tr}P$?
   (`r0-linear-algebra-decompositions`)
   **Answer**: the eigenvalues are 1 ($n$ of them) and 0 ($m-n$ of them), and
   $\operatorname{tr}P = \operatorname{rank}H = n$. $P$ is an orthogonal projector, so
   $P^2 = P = P^\top$.
3. With $R \leftarrow R\exp(\widehat{\delta\phi})$, compute
   $\partial(R^\top a)/\partial\delta\phi$ at $\delta\phi = 0$ for a constant vector $a$.
   (`c1-so3-se3-exponential`)
   **Answer**: expanding gives
   $\exp(-\widehat{\delta\phi})R^\top a \approx R^\top a - \widehat{\delta\phi}R^\top a$, so the
   derivative is $\widehat{R^\top a}$ (tolerance: $10^{-7}$ against finite differences).
4. Write what it means for an estimator of a three-dimensional state to be **consistent**, in terms
   of NEES. (`r0-estimation-theory`)
   **Answer**: $\mathbb{E}[e^\top\Sigma^{-1}e] = 3$. The 95% upper bound is
   $\chi^2_{3,0.95} = 7.815$, and only 5% of samples should exceed it.
5. How many degrees of freedom are unobservable in a trajectory recovered from a monocular camera
   alone, and which are they? (`c7-two-view-geometry`)
   **Answer**: seven — the similarity transform (3 rotation, 3 translation, 1 scale). Adding an IMU
   makes the scale and the gravity direction observable and reduces it to four (1 yaw about gravity
   plus 3 translations); that is R3 of this lesson.

## Key results

The bracket is the derivation depth (the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (two architectures and what each pays) [D2]** — VIO approximates the same posterior in two
  ways. The **filter form** (MSCKF) **marginalises away** states and features outside a sliding
  window and linearises once. The **optimisation form** (VINS-Mono style) **relinearises**
  iteratively inside the window. The cost they share is the **irreversible freezing of a
  linearisation point** that marginalisation creates; what differs is how often that is refreshed
  inside the window.
- **R2 (null-space projection = exact marginalisation) [D3]** — for a feature observation
  $r = H_x\delta x + H_f\delta f + n$ with $n \sim \mathcal{N}(0,\sigma^2 I)$ and $H_f$ of full
  column rank, the information carried by the projected measurement $N^\top r$ is **exactly** the
  information left after marginalising the feature:
  $$\underbrace{\tfrac{1}{\sigma^2}H_x^\top\!\big(I - P_f\big)H_x}_{\text{marginalisation}}
    = \underbrace{\tfrac{1}{\sigma^2}(N^\top H_x)^\top(N^\top H_x)}_{\text{null-space projection}},
    \qquad I - P_f = NN^\top. \tag{1}$$
  The information vector matches as well. So MSCKF's choice not to put features in the state is
  **not an approximation**.
- **R3 (the unobservable subspace of monocular VIO is exactly four-dimensional) [D2]** — with
  gravity known, the cost of monocular VIO is **invariant** under (1) rotation about the gravity
  axis (yaw) and (2) the three global translations, and under nothing else. The generators are
  $$
  \begin{aligned}
  \text{yaw}(g_u):&\quad \delta\phi_i = R_i^\top g_u,\;\;
    \delta p_i = g_u\times p_i,\;\; \delta v_i = g_u\times v_i,\;\; \delta f_k = g_u\times f_k, \\
  \text{translation}(a):&\quad \delta\phi_i = 0,\;\; \delta p_i = a,\;\; \delta v_i = 0,\;\;
    \delta f_k = a.
  \end{aligned} \tag{2}
  $$
- **R4 (weak observability) [D2]** — roll, pitch and **scale** are observable, but their
  sensitivity enters only through the gravity term, so it grows in proportion to the IMU interval
  $\Delta t$. Over a short window the numerical rank deficiency looks like 5–7 rather than 4 —
  **that one line is why VIO initialisation is hard**.
- **R5 (a filter pays in consistency, not in RMSE) [D2]** — in the low-noise regime the position
  RMSE of a filter and of a batch solver are effectively identical, and the difference appears in
  the **tail of the NEES distribution**. A comparison that reports only RMSE misses this
  structurally.

## Derivation

### R1 — the same posterior, two approximations

The state of VIO is $(R_i, p_i, v_i)$ per keyframe plus the biases $(b_a, b_g)$ and the features
$\{f_k\}$. There are only two kinds of factor.

**The IMU preintegration factor** (keyframe $i \to j$ over an interval $\Delta t$):

$$
\begin{aligned}
r_R &= \log\big((\Delta R_{ij})^\top R_i^\top R_j\big), \\
r_v &= R_i^\top\big(v_j - v_i - g\,\Delta t\big) - \Delta v_{ij}, \\
r_p &= R_i^\top\big(p_j - p_i - v_i\Delta t - \tfrac12 g\,\Delta t^2\big) - \Delta p_{ij}.
\end{aligned} \tag{3}
$$

**The camera factor**: $r_{\text{cam}} = \pi\big(R_i^\top(f_k - p_i)\big) - z_{ik}$.

Up to here the structure is that of the bundle adjustment of `c7-bundle-adjustment` — sparse normal
equations, the Schur complement, gauge. What changes is the **real-time constraint**. One cannot
keep every keyframe forever, so the window is cut and everything outside it is **marginalised**.
Marginalisation is the Schur complement (self-diagnosis item 1), and at that moment **the
linearisation point of that instant freezes into the prior**. That is the cost the two
architectures share.

What differs is what happens **inside** the window.

| | Filter form (MSCKF) | Optimisation form (VINS-Mono style) |
|---|---|---|
| Features | never in the state; eliminated immediately by **null-space projection** (R2) | kept as states inside the window, eliminated by Schur |
| Linearisation | once per measurement | **relinearised** until convergence |
| Outside the window | marginalised (linearisation frozen) | marginalised (linearisation frozen) |
| Cost | $O(n^2)$ propagation in the state dimension, no iterations | Schur plus a factorisation per iteration |
| Typical failure | **loss of consistency** from the frozen linearisation (R5) | latency and compute blow-up, overconfidence in information from outside the window |

**Where the assumptions break**: both architectures assume **the marginalised linearisation point
was right**. Marginalising while the initial biases or the gravity direction are wrong puts that
error into the prior, where it is **irreversible**. That is why implementations invest so heavily in
initialisation, and R4 is the mathematical reason it is hard.

### R2 — why the null-space projection is exact

MSCKF's central technique is to keep features out of the state. Stacking the residuals of one
feature seen in $n$ views,

$$r = H_x\,\delta x + H_f\,\delta f + n \in \mathbb{R}^{2n},
  \qquad n \sim \mathcal{N}(0, \sigma^2 I).$$

Suppose $H_f \in \mathbb{R}^{2n\times3}$ has full column rank (a feature with parallax). Let
$N \in \mathbb{R}^{2n\times(2n-3)}$ be an orthonormal basis of the **left** null space of $H_f$
($N^\top H_f = 0$, $N^\top N = I$). The projected measurement is

$$N^\top r = (N^\top H_x)\,\delta x + N^\top n,
  \qquad N^\top n \sim \mathcal{N}(0, \sigma^2 I) \tag{4}$$

and **the feature is gone**. The noise is still isotropic because $N$ is orthonormal — with a
non-orthonormal $N$ the covariance becomes $\sigma^2 N^\top N$ and whitening is required.

That this throws away no information is (1), and the derivation is two lines. The joint information
matrix is

$$\Lambda = \frac{1}{\sigma^2}\begin{bmatrix} H_x^\top H_x & H_x^\top H_f \\
  H_f^\top H_x & H_f^\top H_f\end{bmatrix}$$

and marginalising $\delta f$ gives, by the Schur complement,

$$\Lambda_x = \frac{1}{\sigma^2}\Big(H_x^\top H_x - H_x^\top H_f(H_f^\top H_f)^{-1}H_f^\top H_x\Big)
  = \frac{1}{\sigma^2}H_x^\top\big(I - P_f\big)H_x.$$

Now $P_f$ is the orthogonal projector onto $\operatorname{range}(H_f)$, so $I - P_f$ projects onto
its orthogonal complement, that is, onto $\operatorname{null}(H_f^\top)$, whose orthonormal basis is
$N$ — hence $I - P_f = NN^\top$. Therefore

$$\Lambda_x = \frac{1}{\sigma^2}H_x^\top NN^\top H_x = \frac{1}{\sigma^2}(N^\top H_x)^\top(N^\top H_x)$$

— the **same matrix** as the information of the measurement (4). The information vector follows the
same way:
$\eta_x = \frac{1}{\sigma^2}H_x^\top NN^\top r = \frac{1}{\sigma^2}(N^\top H_x)^\top(N^\top r)$.

Measured (random $H_x, H_f, r$ with $\sigma^2 = 0.37$):

| views $n$ | state dim | information rel. diff | info-vector rel. diff | $\lVert I - P_f - NN^\top\rVert$ | rows |
|---|---|---|---|---|---|
| 6 | 15 | $2.7\times10^{-16}$ | $5.0\times10^{-16}$ | $9.7\times10^{-16}$ | $12 \to 9$ |
| 10 | 21 | $3.5\times10^{-16}$ | $4.0\times10^{-16}$ | $9.2\times10^{-16}$ | $20 \to 17$ |
| 4 | 9 | $4.2\times10^{-16}$ | $2.7\times10^{-16}$ | $9.5\times10^{-16}$ | $8 \to 5$ |

**Where the assumptions break**: the **full column rank** of $H_f$ is the whole story. A feature
with no parallax (rotation in place, a very distant point, a point near the optical axis during pure
forward motion) makes $\operatorname{rank}H_f < 3$. Measured: making the third column of $H_f$ a
multiple of the first gives $\operatorname{rank}H_f = 2$, so the left null space has dimension
**10** instead of $2n-3 = 9$ (at $n=6$), and $\operatorname{cond}(H_f^\top H_f)$ reaches
$1.24\times10^{16}$, effectively singular. Then (a) marginalisation blows up in $C^{-1}$ and (b) the
null-space projection **silently lets one extra dimension through** — spurious information along the
feature's depth direction flows into the state. That is why an implementation must test for parallax
(or check $\sigma_3(H_f)$) before projecting. It is the only genuine trap of the null-space
technique.

### R3 — the unobservable subspace of monocular VIO

Assume gravity $g$ is known in world coordinates (the IMU gives it during a static interval). Ask
what transformations (3) and the camera factor are invariant to.

**Rotation about the gravity axis.** $Q = \exp(\widehat{g_u}\,\epsilon)$ satisfies $Qg = g$.
Substituting $R_i \mapsto QR_i$, $p_i \mapsto Qp_i$, $v_i \mapsto Qv_i$, $f_k \mapsto Qf_k$:

- $r_R$: $(QR_i)^\top(QR_j) = R_i^\top R_j$ — invariant.
- $r_v$: $(QR_i)^\top(Qv_j - Qv_i - g\Delta t)
  = R_i^\top Q^\top Q(v_j - v_i - Q^\top g\,\Delta t) = R_i^\top(v_j - v_i - g\Delta t)$ —
  invariant because $Q^\top g = g$.
- $r_p$: invariant by the same computation.
- Camera: $(QR_i)^\top(Qf_k - Qp_i) = R_i^\top(f_k - p_i)$ — invariant.

**Global translation.** $p_i \mapsto p_i + a$ and $f_k \mapsto f_k + a$ (rotations and velocities
untouched): $r_p$ depends only on $p_j - p_i$ and is invariant, the camera factor depends only on
$f_k - p_i$ and is invariant, and $r_R$ and $r_v$ do not use $p$ at all.

Differentiating in $\epsilon$ gives the generators (2) (the rotation term is $R_i^\top g_u$ because
the increment is on the right). Together they span four dimensions.

**A rotation that is not about gravity is not an invariance.** If $Q$ does not preserve $g$, the
terms with $Q^\top g \ne g$ survive in $r_v$ and $r_p$ — which is why roll and pitch are observable.
**Scale is observable too**: scaling $p, v, f$ by $s$ does not scale the $g\Delta t$ and
$\tfrac12 g\Delta t^2$ terms of (3), so the residual changes. That is how the seven-dimensional
similarity gauge of a camera alone (`c7-two-view-geometry`) drops to four once an IMU is added.

Measured (synthetic VIO: 5 keyframes and 25 features, biases excluded, parameters
$9\cdot5 + 3\cdot25 = 120$, a finite-difference Jacobian of $286\times120$, $\Delta t = 0.1$ s):
the rank deficiency is **4**,
$\sigma_{n-4}/\sigma_{n-3} = 5.93\times10^{-3}/4.57\times10^{-8} = 1.30\times10^{5}$, and the four
generators of (2) satisfy

| Generator | $\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert)$ |
|---|---|
| yaw about gravity | $3.6\times10^{-12}$ |
| translation $x$ | $6.6\times10^{-12}$ |
| translation $y$ | $2.3\times10^{-12}$ |
| translation $z$ | $4.8\times10^{-12}$ |
| (contrast) roll about $x$ | $1.4\times10^{-5}$ |
| (contrast) global scale | $1.8\times10^{-6}$ |

The four generators sit at machine precision while roll and scale are six to seven orders of
magnitude larger — they are observable.

### R4 — "observable" and "actually estimable" are different

That roll comes out at $1.4\times10^{-5}$ above means it is **observable but with a very small
sensitivity**. The derivation shows why: the only path by which roll and pitch enter the residual is
the gravity term of (3), $g\Delta t$ and $\tfrac12 g\Delta t^2$, so the sensitivity is proportional
to $\Delta t$.

Measured (**the same scene held fixed**, changing only the IMU interval $\Delta t$):

| $\Delta t$ | 0.02 s | 0.05 s | 0.1 s | 0.3 s | 1.0 s |
|---|---|---|---|---|---|
| yaw about gravity | $2.98\times10^{-12}$ | $2.98\times10^{-12}$ | $2.98\times10^{-12}$ | $2.98\times10^{-12}$ | $2.98\times10^{-12}$ |
| roll about $x$ | $3.0\times10^{-7}$ | $7.5\times10^{-7}$ | $1.5\times10^{-6}$ | $4.5\times10^{-6}$ | $1.7\times10^{-5}$ |
| global scale | $3.5\times10^{-7}$ | $2.6\times10^{-7}$ | $1.7\times10^{-7}$ | $7.9\times10^{-7}$ | $3.5\times10^{-6}$ |
| numerical rank deficiency (at $10^{-7}\sigma_1$) | 7 | 7 | 5 | 5 | 5 |

How to read it. (1) **Yaw is exactly $2.98\times10^{-12}$ at every $\Delta t$** — a true invariance.
(2) Roll grows in proportion to $\Delta t$ (a factor of 56 from 0.02 to 1.0 s). (3) As a result the
**numerical rank deficiency looks like 5–7 rather than 4** — roll, pitch and scale fall below the
threshold and become "indistinguishable from unobservable". This is what VIO initialisation really
is: without enough acceleration excitation, or with too short a window, the scale and the gravity
direction are **effectively** unobservable, and marginalising in that state locks R1's frozen
linearisation onto a wrong value.

**Where the assumptions break**: (1) this analysis **excluded the biases**. With biases included
they are observable but again weakly and dependent on excitation, and during a static interval the
accelerometer bias and the gravity direction are nearly indistinguishable (both look like a constant
acceleration) — the commonest initialisation failure in practice **[D0]**. (2) Planar motion (a
ground robot) has no vertical excitation, so the scale sensitivity is even lower. (3) Adding stereo
or a range sensor makes scale come straight out of the geometry and the problem disappears — which
is why only monocular VIO needs an elaborate initialisation procedure.

### R5 — where a filter and a batch solver part ways

The theory says "a filter freezes its linearisation and so loses consistency". What has to be
measured is **in which metric** that shows up. On a planar SLAM problem (a robot $(x,y,\theta)$ plus
point landmarks, odometry plus range-bearing observations) an EKF-SLAM and a batch Gauss–Newton were
run on the same measurements, and the NEES of the final pose ($d = 3$, expectation 3 if consistent,
$\chi^2_{3,0.95} = 7.815$) was compared with the position RMSE.

Measured (a 40-step trajectory, 12 landmarks, observation noise $\sigma_r = 0.08$ m and
$\sigma_b = 1^\circ$, odometry $\sigma_d = 0.05$ m and $\sigma_\theta = 2^\circ$, 60 Monte Carlo
runs):

| | mean NEES | median NEES | $P(\text{NEES} > 7.815)$ | position RMSE |
|---|---|---|---|---|
| EKF-SLAM | 3.904 | 3.044 | **0.117** | 0.0616 m |
| batch GN | 3.754 | 3.322 | **0.067** | 0.0619 m |

How to read it (honestly). (1) **The position RMSE is effectively identical** (0.0616 against
0.0619 m, a 0.5% difference). At this noise level the filter loses almost no accuracy. (2) The
difference is in the **tail**: the fraction exceeding the 95% bound is 11.7% for the filter against
6.7% for the batch, so the filter is more than twice as far from the nominal 5%. (3) Both have a
mean NEES above 3 — the batch is not perfectly consistent either, reflecting both finite samples and
linearisation.

**What this measurement does not say (honestly)**: the same experiment was tried at heading noise
$\sigma_\theta = 5^\circ$ and $10^\circ$, and in that regime **my batch implementation broke
first** — eight Gauss–Newton iterations from a dead-reckoned initial guess did not converge and the
mean NEES jumped to the order of $4\times10^2$. That high-noise comparison therefore measures **the
fragility of my solver**, not the theory, and this lesson does not use those numbers. Comparing the
two fairly at high noise needs a trust region, a robust loss and a better initial guess on the batch
side — which is itself R1's point that the optimisation form is not free.

**So the conclusion is not "the filter is inaccurate".** The conclusion is about **the choice of
metric**. A comparison that reports only ATE or RMSE misses the structural difference between a
filter and an optimiser **structurally**. The difference appears in the trustworthiness of the
covariance, that is, in the quantity the downstream modules consume (loop-closure decisions, sensor
fusion, safety margins in planning). `s1-slam-benchmarking` takes this problem head on.

## Proof sketch

### R2 — equivalence of null-space projection and marginalisation

**Hypotheses** H1: $r = H_x\delta x + H_f\delta f + n$ with
$n \sim \mathcal{N}(0,\sigma^2 I_{2n})$. H2: $H_f$ has full column rank
($\operatorname{rank}H_f = 3$). H3: $N$ satisfies $N^\top H_f = 0$ and
$N^\top N = I_{2n-3}$.
**Conclusions** C1: $I - P_f = NN^\top$. C2: the information matrix and vector after marginalising
the feature are exactly those given by $N^\top r$. C3: $N^\top n$ is still isotropic.

**Strategy**: uniqueness of the orthogonal projector plus the projector form of the Schur complement.

1. **C1**: $P_f$ is the orthogonal projector onto $\operatorname{range}(H_f)$ (H2 makes
   $(H_f^\top H_f)^{-1}$ exist, and $P_f^2 = P_f = P_f^\top$). An orthogonal projector is determined
   uniquely by its image, so $I - P_f$ projects onto
   $\operatorname{range}(H_f)^\perp$. In linear algebra
   $\operatorname{range}(H_f)^\perp = \operatorname{null}(H_f^\top)$, and $N$ is an orthonormal basis
   of that space, so the projector onto it is $NN^\top$. Two projectors onto the same space are
   equal. $\square$
2. **C2**: the Schur complement of the joint information gives
   $\Lambda_x = \sigma^{-2}H_x^\top(I-P_f)H_x$, which by C1 is
   $\sigma^{-2}(N^\top H_x)^\top(N^\top H_x)$. The information vector likewise is
   $\eta_x = \sigma^{-2}H_x^\top(I-P_f)r = \sigma^{-2}(N^\top H_x)^\top(N^\top r)$. Both are what
   measurement (4) provides. $\square$
3. **C3**: $\operatorname{Cov}(N^\top n) = N^\top(\sigma^2 I)N = \sigma^2 N^\top N = \sigma^2 I$
   by H3. Without orthonormality this step fails and whitening is needed. $\square$
4. **Why this matters**: describing MSCKF as "an approximation that discards features" is wrong. It
   does not discard them, it **eliminates them exactly**, with no loss of accuracy at all. The
   filter's real cost is R1's frozen linearisation and R5's consistency, not the null-space technique
   itself. It is **the same theorem wearing a different face** as the Schur complement of
   `c7-bundle-adjustment`.
5. **Remove a hypothesis**: if H2 fails (a feature with no parallax), $P_f$ is undefined and the
   dimension of $N$ exceeds $2n-3$, so **the projection fails to filter out the feature direction**.
   Measured: at $\operatorname{rank}H_f = 2$ the dimension of $N$ is 10 instead of the expected 9 and
   $\operatorname{cond}(H_f^\top H_f) = 1.2\times10^{16}$. Dropping the orthonormality of H3 breaks
   C3, so the noise covariance has to be recomputed (which is why implementations use the $Q$ of a
   QR factorisation).

Steps left out: $\operatorname{range}(A)^\perp = \operatorname{null}(A^\top)$ and the uniqueness of
orthogonal projectors. Both are standard; see `r0-linear-algebra-decompositions`.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Derive (1). Then describe how to obtain $N$ **by a QR factorisation**
(from $H_f = QR$, the trailing $2n-3$ columns of $Q$) and show why those columns are an orthonormal
basis of the left null space.
*Solution sketch*: Schur complement → projector → C1. In the QR factorisation $Q_1$ spans
$\operatorname{range}(H_f)$ and $Q_2$ spans its orthogonal complement, and
$Q_2^\top H_f = Q_2^\top Q_1R_1 = 0$.

**P2 (proof, ★★★, R2)** Treat the case where H2 is **dropped**. What is the "correct" elimination
when $\operatorname{rank}H_f = \rho < 3$? Using the pseudo-inverse form $P_f^{+} = H_fH_f^{+}$, state
exactly which parts of C1 and C2 survive and which break, and write a paragraph on **what the state's
information then loses**.
*Strategy and key inequality*: with $H_f^{+}$, $I - P_f^{+}$ is still an orthogonal projector and C1
holds for an $N$ of matching rank. What breaks is the interpretation "all three feature degrees of
freedom were eliminated" — only $\rho$ dimensions were, and the remaining $3-\rho$ **float freely
with no prior**. Information flowing into the state along those directions is spurious.

**P3 (numerical, ★, R2)** With $n = 5$, draw $H_f \in \mathbb{R}^{10\times3}$ and
$H_x \in \mathbb{R}^{10\times12}$ at random and compute (a) $\operatorname{tr}P_f$, (b) the number of
columns of $N$, (c) the relative difference between the two sides of (1), and (d)
$\lVert I-P_f-NN^\top\rVert$.
*Answer*: (a) $\operatorname{tr}P_f = \operatorname{rank}H_f = 3$ (tolerance $10^{-12}$);
(b) $10-3 = 7$; (c) and (d) at most $10^{-15}$ (reference measurements: $2.7\times10^{-16}$ and
$9.7\times10^{-16}$). Check: confirm that $P_f$ has three eigenvalues 1 and seven 0.

**P4 (derivation, ★★, R3)** Derive the four generators (2). Then argue with equations how the
unobservable dimension changes for **stereo** VIO (known baseline) and for the case where **gravity
is unknown**.
*Solution sketch*: substitute the invariances into (3) and the camera factor and differentiate in
$\epsilon$. Stereo still gives four (yaw plus three translations) because the scale comes from the
geometry. If the gravity direction is unknown, its two degrees of freedom enter the state and all
three global rotations become invariances, raising the unobservable dimension to six (3 rotations
plus 3 translations) — the scale stays observable because of the IMU.

**P5 (numerical, ★★, R3·R4)** Build a synthetic VIO Jacobian and measure (a) the rank deficiency,
(b) $\lVert Jg\rVert/(\lVert J\rVert_F\lVert g\rVert)$ for the four generators of (2), (c) the same
for roll about $x$ and for the global scale, and (d) how (c) changes as $\Delta t$ goes from 0.02 to
1.0 s.
*Answer (reference measurements)*: (a) 4 (at $\Delta t = 0.1$ s with a threshold of
$10^{-7}\sigma_1$); (b) $2.3$ to $6.6\times10^{-12}$; (c) roll $1.4\times10^{-5}$, scale
$1.8\times10^{-6}$; (d) roll goes $3.0\times10^{-7} \to 1.7\times10^{-5}$ (a factor of 56) while yaw
stays **unchanged** at $2.98\times10^{-12}$. Tolerance: the generator values at most $10^{-9}$, and
the growth of roll monotone. Check: confirm you held the scene fixed and changed only $\Delta t$
(redrawing the scene blurs the trend).

**P6 (implementation, ★★★, R5)** Implement both an EKF-SLAM and a batch Gauss–Newton on the same
measurements and compare NEES and RMSE by Monte Carlo.
*Rubric*: (a) both methods use the **same** odometry and observation realisation; (b) the batch
anchors the first pose to remove the gauge; (c) angle wrapping is handled in both the residuals and
the NEES; (d) you report that the RMSEs are nearly equal while the tail fractions differ; (e) the
number of trials and a confidence interval are stated.

**P7 (counterexample, ★★, R2·R4)** (a) Construct a feature configuration on which the null-space
projection injects **spurious information** (no parallax). Show $\operatorname{rank}H_f$, the
dimension of $N$, and the resulting bias in the state estimate. (b) Construct a motion where the
scale is effectively unobservable (constant-velocity straight line plus a short window) and confirm
that the rank deficiency appears as 5.
*Property checklist*: (a) $\sigma_3(H_f)/\sigma_1(H_f) < 10^{-8}$; (b) the dimension of $N$ exceeds
$2n-3$; (c) a component along the feature's depth direction survives in the state information after
projection; (d) the scale generator's value drops to the order of the four generators; (e) in both
cases confirm that **the residual does not detect it**.

**P8 (paper, ★★, R1·R2)** Read §III of Mourikis & Roumeliotis 2007 and §V–VI of Qin et al. 2018, and
(a) tabulate the two papers' state vectors and the moments at which they marginalise; (b) contrast
how the MSCKF paper argues the **exactness** of the null-space projection with R2 here; and (c) find
whether either paper's evaluation verifies the **trustworthiness of the covariance** (if not, write
that it does not).
*Rubric*: for (c), checking whether NEES or an equivalent consistency metric is reported passes. For
(b), distinguishing the implementation detail "obtain $N$ by QR" from the claim "information is
preserved" is excellent.

## Paper reading

**Two must-reads.** Write a one-page note on each, using the ten fixed questions
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read in three passes, and attack questions 4, 5, 6 and 7 in the third.
For the full bibliography, including the recommended papers, run `rc papers s1-vio-systems`.

1. **Mourikis & Roumeliotis, "A multi-state constraint Kalman filter for vision-aided inertial
   navigation" (2007, ICRA)** — role: `seminal`.
   <https://doi.org/10.1109/ROBOT.2007.364024> (§III is the core.)
   Extra questions: (a) rewrite the null-space projection in the form of (1) here. Does the paper
   prove exactness, or assert it? (b) Is there a parallax test for features in the paper — and if
   not, where would R2's failure mode show up? (c) How does the reported computation scale with the
   state dimension?
2. **Qin, Li & Shen, "VINS-Mono: a robust and versatile monocular visual-inertial state estimator"
   (2018, IEEE T-RO)** — role: `standard`. <https://arxiv.org/abs/1708.03852> (§V–VI is the core.)
   Extra questions: (a) how does the initialisation procedure work around the "weak observability"
   problem of R4? (b) Is there any treatment that fixes the linearisation point in the sliding-window
   marginalisation (FEJ-style)? (c) Did the baselines the paper compares against run on the same
   hardware and the same sequences?

**The ten fixed questions**: (1) which problem under which assumptions; (2) what exactly earlier
work could not do; (3) the core idea in one equation; (4) what is guaranteed and **what is not**;
(5) the independent and dependent variables and the baselines, fairly tuned or not; (6) whether the
metric matches the claim, and whether variance and seeds are reported; (7) what is missing for
reproduction; (8) the first assumption to doubt if the result were wrong; (9) time and memory
complexity and real-time behaviour; (10) what you would change to go beyond it in a year.

**Recommended**: Cadena et al. 2016 §III (the whole map of SLAM), Triggs et al. 2000 §4 (the origin
of marginalisation), Barfoot ch.4.

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 15 minutes in total, numpy and
scipy only. The input is a synthetic generator this lesson specifies; no external data and no GPU are
needed.

> **Stated difference from the blueprint**: the reproduction task in the design is "run a public VIO
> on one EuRoC sequence, match the reported ATE to within 30%, and measure the effect of a
> configuration change". The public VIO systems (OpenVINS, VINS-Mono) need a ROS build and several
> gigabytes of data, and setting up the environment would be most of the exercise. Following the
> compute-budget principle of the "Reproduction tasks" section of lesson `f0-how-to-read-this-track`, the mandatory conditions here are **four
> checks decidable on a CPU** and the EuRoC run is separated out as the **optional extension (R4)**
> below. The mandatory conditions target this lesson's three results (R2, R3, R5) head on.

**Generators (fixed)**: (a) for the null space — $H_x \in \mathbb{R}^{2n\times n_x}$,
$H_f \in \mathbb{R}^{2n\times3}$ and $r \in \mathbb{R}^{2n}$ from a standard normal, with
$\sigma^2 = 0.37$ and $(n, n_x) \in \{(6,15),(10,21),(4,9)\}$. (b) For the VIO Jacobian — 5
keyframes (rotations $\sim0.2$ rad, positions $0.4i$, velocities $\approx(4,1,0)$), 25 features
($x \in 2\pm1$, $y \in \pm1$, $z \in [1,3]$), $f = 300$, $g = (0,0,-9.81)$ and
$\Delta t \in \{0.02, 0.05, 0.1, 0.3, 1.0\}$ **with the scene held fixed**. (c) For consistency — a
planar 40-step trajectory ($D = 0.5$ m, $\Delta\theta = 2\pi/40$), 12 landmarks, an observation
radius of 6 m, $\sigma_r = 0.08$ m, $\sigma_b = 1^\circ$, $\sigma_d = 0.05$ m and
$\sigma_\theta = 2^\circ$. Report with a fixed seed.

All **four conditions** must hold to pass. Every reference value was measured for this lesson.

1. **The null-space identity**: for all three settings of generator (a), the relative differences of
   the information matrix and vector in (1) are at most $10^{-12}$,
   $\lVert I-P_f-NN^\top\rVert < 10^{-12}$, and the row count drops $2n \to 2n-3$ (reference:
   around $3\times10^{-16}$ and $9.5\times10^{-16}$, with $12\to9$, $20\to17$ and $8\to5$).
2. **Degeneracy detection**: making one column of $H_f$ a multiple of another gives
   $\operatorname{rank}H_f = 2$, a dimension of $N$ that is **one larger** than $2n-3$, and
   $\operatorname{cond}(H_f^\top H_f) > 10^{14}$ (reference: dimension 10 against the expected 9, and
   a condition number of $1.24\times10^{16}$).
3. **Observability**: with generator (b), (a) the rank deficiency is **4** (for
   $\Delta t \ge 0.1$ s at a threshold of $10^{-7}\sigma_1$); (b) the four generators of (2) are at
   most $10^{-9}$; (c) roll about $x$ and the global scale are **at least four orders of magnitude**
   larger than the generators; and (d) raising $\Delta t$ makes the roll value **increase
   monotonically** (reference: deficiency 4, generators $2.3$ to $6.6\times10^{-12}$, roll
   $1.4\times10^{-5}$ and scale $1.8\times10^{-6}$, and roll
   $3.0\times10^{-7}\to1.7\times10^{-5}$).
4. **Consistency**: with generator (c), running EKF-SLAM and batch GN on the **same realisations**
   over at least 40 Monte Carlo trials, (a) the position RMSEs differ by at most 5% and (b)
   $P(\text{NEES} > 7.815)$ is **larger** for the EKF than for the batch (reference: RMSE 0.0616
   against 0.0619 m, a 0.5% difference, and tail fractions 0.117 against 0.067). State in the report
   that **"RMSE does not distinguish them"**.

**Optional extension (R4, needs an environment build — optional only)**: run OpenVINS or VINS-Mono
on one EuRoC sequence such as `MH_01_easy`, measure the ATE RMSE and match the reported value **to
within 30%**. Then change exactly one setting (window size, feature count, or FEJ on/off) and measure
the change in ATE. When reporting, always state the commit hash, the parameter file, the alignment
convention (SE(3) against Sim(3)) and the number of runs. R4 is **optional** and is not a condition
for passing this lesson.

**Baselines**: (1) the marginalisation computation (condition 1); (2) the analytic generators
(condition 3); (3) each other (EKF against batch, condition 4); (4) optionally the reported values of
a public VIO.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| the two sides of (1) differ at the $10^{-3}$ level | $N$ is not orthonormal (an arbitrary basis, say) | print $\lVert N^\top N - I\rVert$ |
| the marginalisation side gives `nan` | $H_f^\top H_f$ is singular — a feature with no parallax | look at $\sigma_3(H_f)/\sigma_1(H_f)$ (condition 2) |
| the rank deficiency is 7 rather than 4 | $\Delta t$ is short, so roll, pitch and scale fall below the threshold | raise $\Delta t$ and compare with the generator values (R4) |
| the generator values are around $10^{-3}$ | right and left increments confused — the yaw generator is $R_i^\top g_u$ | match the increment convention to the finite-difference Jacobian |
| the scale generator comes out as zero | the IMU factors were omitted (camera only) | with a camera alone seven degrees of freedom is correct — add (3) |
| the EKF NEES is in the hundreds | missing angle wrapping, or accumulated asymmetry in the covariance | check $P \leftarrow (P+P^\top)/2$ and the wrapping |
| the batch NEES is below 1 | the gauge was not fixed, so the covariance is inflated | check that the first pose is anchored strongly |

## Open problems

- **(open problem) undoing the error in a marginalised linearisation point** — the cost R1 identifies
  is that marginalisation freezes the linearisation of that moment into the prior. FEJ-style
  (first-estimates Jacobian) schemes preserve **consistency** but do not correct a wrong
  linearisation point. There is no principled way to **update** a marginalisation prior once a better
  estimate becomes available. Current approaches: fixing the linearisation point (FEJ), rebuilding
  the window, and the partial relinearisation of
  [iSAM2](https://doi.org/10.1177/0278364911430419). What is missing: a posterior correction of the
  marginalisation prior together with its error bound.
- **(open problem) an observability certificate for initialisation** — R4 shows that scale and
  gravity are only **weakly** observable and that the sensitivity depends on excitation. There is no
  certificate that decides from the data whether it is safe to initialise now, and practice relies on
  empirical thresholds (acceleration variance, parallax). Current approaches: the staged
  initialisation of [VINS-Mono](https://arxiv.org/abs/1708.03852), and the discussion in
  [Cadena et al. 2016](https://arxiv.org/abs/1606.05830) §III. What is missing: a quantitative
  observability certificate. It is the same kind of problem as the degeneracy certificate of
  `c7-two-view-geometry`.
- **(open problem) a standard for reporting consistency** — as R5 showed, RMSE does not distinguish a
  filter from an optimiser. And yet VIO papers rarely report NEES or an equivalent consistency
  metric, while downstream modules consume the covariance as if it were trustworthy. Current
  approaches: NEES reporting in some filter papers, and the evaluation guidance of
  [Zhang & Scaramuzza 2018](https://doi.org/10.1109/IROS.2018.8593941). What is missing: a convention
  that includes a consistency metric in public benchmarks. `s1-slam-benchmarking` returns to this.
- **(open problem) choosing between filter and optimiser by design rather than by habit** — the
  choice between the two architectures is currently settled by experience and available compute, and
  there is no **model that predicts** which is better given a scene, a motion and a sensor suite.
  Current approach: empirical comparison on a particular platform. What is missing: design rules that
  **derive** the window size and the number of relinearisations from a compute budget and a
  consistency requirement.

## Concept check

Run `rc quiz s1-vio-systems`. The quiz is for **concept checking only**; the real work is the problem
set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

The five items cover: what MSCKF's null-space projection actually does to the feature; how many
degrees of freedom are unobservable in monocular VIO with known gravity; whether observability means
estimability over a short window; the condition under which the null-space projection injects
spurious information; and which metric first reveals the difference between EKF-SLAM and batch
optimisation.

## How to study this stage

1. **Rewrite marginalisation as a projector (60 min)** — pull $I - P_f$ out of the Schur complement
   and prove $I-P_f = NN^\top$. That single line is all of R2, and confirm it is the same theorem as
   the Schur complement of `c7-bundle-adjustment` (P1).
2. **Check it with random matrices first (40 min)** — build $H_x$ and $H_f$ at random and match the
   two sides of (1) to the $10^{-15}$ level (condition 1). Then deliberately take a
   **non-orthonormal** $N$ and watch it break.
3. **Create a degeneracy (40 min)** — make a column of $H_f$ dependent, watch the null space grow by
   one dimension, and check what gets mixed into the state's information (condition 2, P7).
4. **Observability by hand (60 min)** — substitute the gravity-axis rotation and the global
   translation into (3) and the camera factor, confirm the invariances and derive (2). Work out the
   stereo case and the unknown-gravity case too (P4).
5. **Measure weak observability (60 min)** — with the synthetic Jacobian, measure the rank deficiency
   and the generator values, then, **holding the scene fixed**, change only $\Delta t$ and watch the
   sensitivity of roll grow (condition 3). That experiment is the answer to "why is VIO
   initialisation hard".
6. **Measure consistency (120 min)** — run the EKF-SLAM and the batch on the same realisations and
   compare NEES against RMSE (condition 4). Seeing the RMSEs equal while the tails differ is the
   final experience of this lesson.
7. **Two papers and the notes (130 min)** — read MSCKF §III against R2, then find the initialisation
   and the marginalisation in VINS-Mono §V–VI. Write the one-page note per paper **without
   exception**.
8. **End at what cannot be done (30 min)** — pick one of the open problems and write a paragraph on
   why it is still open. An observability certificate for initialisation is one you could start
   experimenting on immediately.

**Passing bar**: you can prove $I - P_f = NN^\top$ on a blank page, you can write the four generators
of (2), you can point in (3) to the reason the sensitivity of roll scales with $\Delta t$, you have
code that passes all four conditions of the reproduction task, and you have notes on both papers.
