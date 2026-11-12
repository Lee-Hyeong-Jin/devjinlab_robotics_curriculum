---
id: c5-observability-consistency
lang: en
title: Observability and estimator consistency
summary: >-
  State the Lie-derivative rank condition of nonlinear observability (Hermann-Krener), and derive
  from the invariance group that the unobservable subspace of monocular visual-inertial estimation
  is four-dimensional: one yaw about gravity plus three global translations. Then show that the
  inconsistency of EKF-SLAM is the phenomenon of "the linearization point differing from epoch to
  epoch so the null space breaks", and confirm by numerical rank the mechanism of FEJ - that of
  two algebraically identical Jacobians, only one preserves the null space.
objectives:
  - State the Hermann-Krener local weak observability theorem with hypotheses and conclusion separated, and compute the rank condition.
  - Write the four unobservable directions of monocular visual-inertial estimation directly as generators of the invariance group.
  - Measure the null space dimension of the linearized system by numerical rank and confirm that it grows under degenerate motion.
  - Explain how an EKF's Jacobian evaluation points break the null space and inject spurious information.
  - Say why two algebraically identical Jacobian expressions become different filters after linearization.
  - Report observability, consistency and accuracy as three separate axes, with numbers.
tags: [state-estimation, observability, consistency, fej, ekf-slam, vio, research]
---

# Observability and estimator consistency

## Setup and notation

The Lie group and NEES notation of `c5-manifold-estimation` and the IMU model of
`c5-imu-preintegration` carry over. Additional symbols:

| Symbol | Meaning |
|---|---|
| $\dot x = f(x, u)$, $z = h(x)$ | the nonlinear dynamics and measurement, with $x \in \mathcal{M}$ (the state manifold) |
| $L_f^k h$ | the $k$-th Lie derivative of $h$: $L_f h = \nabla h \cdot f$ and $L_f^{k+1}h = L_f(L_f^k h)$ |
| $\mathcal{O}$ | the **observability codistribution** $= \mathrm{span}\{\mathrm{d}L_f^k h_j : k \ge 0\}$ |
| $\Phi_{k,0}$ | the state transition of the linearized system, $\Phi_{k-1}\cdots\Phi_0$ |
| $H_k$ | the measurement Jacobian at epoch $k$ |
| $M$ | the **observability matrix**, stacked from the row blocks $H_k\Phi_{k,0}$ |
| $\mathcal{N} = \ker M$ | the **unobservable subspace** of the linearized system |
| $N$ | an analytic basis of $\mathcal{N}$ (the invariance generators as columns) |
| $\hat x_{k\mid k-1}$, $\hat x_{k\mid k}$ | the propagated (predicted) and the updated estimate. **FEJ uses the former as its linearization point** |
| $u_g = g/\lVert g\rVert$ | the unit gravity direction in the world frame |

**Three things to keep apart.** Almost every confusion in this lesson comes from mixing them:

- **Observability** — do the measurements determine the state? A property **of the problem**,
  independent of any estimator.
- **Consistency** — does the covariance the estimator reports match the actual error distribution
  ($\mathbb{E}[\mathrm{NEES}] = \dim$)? A property **of the estimator**.
- **Accuracy** — is the error small? It can move independently of the other two.

R5 and Part C of the reproduction task show these three genuinely coming apart, with numbers.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (Hermann-Krener: the rank condition for local weak observability) [D3]** — for an analytic
  system $\dot x = f(x,u)$, $z = h(x)$,
  $$
  \dim \mathcal{O}(x_0) = \dim\mathcal{M}
    \quad\Longrightarrow\quad x_0 \text{ is locally weakly observable.} \tag{1}
  $$
  The converse fails in general, but for analytic systems the rank condition is also necessary at
  **almost every** point. What practice actually uses is the contrapositive — **if the rank is
  deficient, that direction cannot be determined by any estimator.**
- **R2 (the unobservable subspace of monocular visual-inertial estimation is four-dimensional)
  [D3]** — with the state $\{(R_k, v_k, p_k)\}_{k} \cup \{p_{f_i}\}_i$ and measurements from an
  IMU (body frame) and monocular bearings, the group of transformations that preserves every
  residual is
  $$
  (R_k, v_k, p_k, p_{f_i}) \;\longmapsto\;
    \big(R_\psi R_k,\ R_\psi v_k,\ R_\psi p_k + t,\ R_\psi p_{f_i} + t\big),
    \qquad R_\psi := \exp(\psi\,\hat u_g),\ t\in\mathbb{R}^3 \tag{2}
  $$
  a Lie group of dimension $1 + 3 = 4$. Its four generators span the null space of the linearized
  system **exactly**. As measured in the reproduction task: on a 45-dimensional problem the
  numerical rank is 41 and the null space dimension **4** (the singular value gap is
  $1.3\times10^{-3}$ against $7.4\times10^{-11}$, eight orders of magnitude).
- **R2' (degenerate motion enlarges the null space) [D2]** — (2) is a **structural**
  unobservability, independent of the motion. Particular motions add directions to it. As measured
  in the reproduction task, switching to a trajectory whose world-frame acceleration is constant
  raises the null space dimension of the same problem to **5** — the scale ambiguity of
  `c5-imu-preintegration` R4 showing up as a rank deficiency.
- **R3 (the inconsistency of EKF-SLAM: the null space breaks) [D2]** — with ideal linearization
  (evaluated at the truth), $H_k\Phi_{k,0}N = 0$ holds. But an EKF evaluates $H_k$ and $\Phi_k$ at
  **different estimates at different epochs**, so the identity fails and the rank of $M$ rises.
  The dimensions it rises by are **spurious information**, and since information was added along
  unobservable directions the covariance becomes smaller than it should be. As measured in the
  reproduction task (2D EKF-SLAM, $n = 11$): null space 3 with ideal Jacobians versus 2 for the
  standard EKF, with $\lVert MN\rVert/\lVert N\rVert$ rising from $6.07\times10^{-16}$ to
  $2.658\times10^{-1}$.
- **R4 (FEJ: of two algebraically identical expressions, only one preserves the null space) [D2]**
  — the $(1,3)$ block of the transition Jacobian of 2D SLAM can be written in two ways that are
  **identical** in the true system:
  $$
  J\,R(\theta_k)u_k \qquad\text{or}\qquad J\,(p_{k+1} - p_k), \tag{3}
  $$
  since $p_{k+1} = p_k + R(\theta_k)u_k$. Substituting estimates they differ, and **only the
  $J(\hat p_{k+1\mid k} - \hat p_{k\mid k-1})$ form** satisfies $\Phi_k N_k = N_{k+1}$. Combined
  with evaluating the measurement Jacobian at the first estimates (FEJ), the null space is
  preserved **exactly**. As measured: FEJ gives null space 3 and
  $\lVert MN\rVert/\lVert N\rVert = 6.12\times10^{-16}$ — the same as ideal Jacobians to machine
  precision.
- **R5 (observability ≠ consistency ≠ accuracy) [D1]** — R3 and R4 are statements about
  **removing** spurious information, not about making NEES equal to one. The measurements of Part
  C of the reproduction task show it: in the 30-step all-visible setting the
  $\mathrm{ANEES}/\dim$ of the standard EKF and of FEJ are **indistinguishable** at $0.738$ each,
  and in the 300-step range-limited setting the standard EKF gives $0.915$ against FEJ's $1.265$
  — **FEJ is the more overconfident of the two**, and its position RMSE is worse as well.
  Preserving the null space is necessary, not sufficient.

## Derivation

### R2 — reading the four unobservable directions off the invariance group

Before looking at observability as a rank computation, find **what leaves the measurements
unchanged**. It is faster and geometrically exact.

There are two kinds of measurement.

1. **IMU** ((1) of `c5-imu-preintegration`): the gyroscope gives the body rate $\omega_k$ and the
   accelerometer gives $R_k^\top(a_k - g)$.
2. **Monocular bearing**: the normalized direction of $R_k^\top(p_{f_i} - p_k)$.

Substitute the transformation (2) and check each. Since $R_\psi = \exp(\psi\hat u_g)$ is a rotation
about the gravity axis, $R_\psi g = g$ and $R_\psi^\top g = g$. That is the whole derivation.

**Gyroscope.** $\omega_k$ is a body-frame quantity, and $R_k' = R_\psi R_k$ still satisfies
$\dot R' = R'\hat\omega$ (indeed $\dot R' = R_\psi\dot R = R_\psi R\hat\omega = R'\hat\omega$).
Invariant ✓

**Accelerometer.** Since $a_k' = \ddot p_k' = R_\psi \ddot p_k = R_\psi a_k$,

$$
R_k'^\top(a_k' - g) = R_k^\top R_\psi^\top(R_\psi a_k - g)
  = R_k^\top\big(a_k - R_\psi^\top g\big) = R_k^\top(a_k - g). \tag{4}
$$

**That one line**, using $R_\psi^\top g = g$, answers "why is only rotation about gravity
unobservable". For a rotation $R_\chi$ off the gravity axis, $R_\chi^\top g \ne g$, (4) fails, and
that is why roll and pitch are observable.

**Bearing.** The $t$ cancels and $R_\psi$ preserves norms:

$$
\frac{R_k'^\top(p_{f_i}' - p_k')}{\lVert p_{f_i}' - p_k'\rVert}
  = \frac{R_k^\top R_\psi^\top\big(R_\psi p_{f_i} + t - R_\psi p_k - t\big)}{\lVert R_\psi(p_{f_i}-p_k)\rVert}
  = \frac{R_k^\top(p_{f_i} - p_k)}{\lVert p_{f_i} - p_k\rVert}. \tag{5}
$$

So the whole four-parameter group (2) leaves the measurements unchanged. Writing its
**generators** (differentiating at the identity) gives a basis for the null space of the linearized
system. The translation direction $t = \epsilon e$ gives

$$
n_e = \big(\underbrace{0}_{\delta\phi_k},\ \underbrace{0}_{\delta v_k},\
  \underbrace{e}_{\delta p_k},\ \underbrace{e}_{\delta p_{f_i}}\big), \tag{6}
$$

and the yaw direction $\psi = \epsilon$ gives, in the right-perturbation convention
$R_k \leftarrow R_k\exp(\delta\phi_k)$,

$$
n_\psi = \big(\underbrace{R_k^\top u_g}_{\delta\phi_k},\
  \underbrace{u_g\times v_k}_{\delta v_k},\
  \underbrace{u_g\times p_k}_{\delta p_k},\
  \underbrace{u_g\times p_{f_i}}_{\delta p_{f_i}}\big). \tag{7}
$$

The first component of (7): since
$\exp(\epsilon\hat u_g)R_k = R_k\exp(\epsilon\,\widehat{R_k^\top u_g})$, the right-perturbation
coordinate is $\delta\phi_k = R_k^\top u_g$ (the same computation as the $\mathrm{Ad}$
transformation of R2 in `c5-manifold-estimation`). The remaining components are
$\frac{d}{d\epsilon}\exp(\epsilon\hat u_g)x = u_g\times x$.

**Where the assumption breaks**: (2) rests on three premises — (a) gravity's **magnitude and
direction are fixed**, (b) the accelerometer bias is not in the state, and (c) the only
measurements are bearings (no scale). A single range measurement (stereo, LiDAR) leaves $t$
unobservable but makes the scale observable. Putting the bias in the state adds $b^a$ to (4) and
can create further degeneracies (see "where the assumption breaks" in R4 of
`c5-imu-preintegration`). And (2) gives only the unobservability that is **independent of the
motion** — what the motion adds is R2'.

### R3 — how an EKF manufactures spurious information

Stack the observability matrix of the linearized system as

$$
M = \begin{bmatrix} H_0 \\ H_1\Phi_{1,0} \\ \vdots \\ H_K\Phi_{K,0}\end{bmatrix}. \tag{8}
$$

The unobservable directions are by definition $\mathcal{N} = \ker M$, and R2 says that for
$H_k, \Phi_k$ evaluated **at the truth**, $MN = 0$. It holds at the truth because of two
identities:

$$
H_k N_k = 0, \qquad \Phi_k N_k = N_{k+1}, \tag{9}
$$

where $N_k$ is the generators evaluated at the state at epoch $k$. Combining them gives
$H_k\Phi_{k,0}N_0 = H_kN_k = 0$. The second identity is the crucial one — the null space is **a
different vector at every epoch**, and the transition matrix carries it exactly.

Now consider the EKF. It evaluates $H_k$ at $\hat x_{k\mid k}$ (or at an intermediate value during
the update) and $\Phi_k$ at $\hat x_{k\mid k}$. Then neither identity in (9) holds:

- $H_k$ is evaluated at $\hat x_{k\mid k}$ while $\Phi_{k-1}$ was evaluated at
  $\hat x_{k-1\mid k-1}$, so the premise "the same state at the same linearization point" is gone.
- In particular, **the same state is evaluated at different values at different epochs**
  ($\hat x_{k\mid k-1}$ versus $\hat x_{k\mid k}$, and the landmarks move at every update).

The consequence is $MN \ne 0$. The rank of $M$ rises, and the dimensions it rises by are
**unobservable** directions. The filter believes it has gained information along them, so $P$
shrinks while the true error does not, and NEES grows. That is the inconsistency of EKF-SLAM, and
it appears first in yaw and heading.

**How to measure the spurious information.** Use $\lVert MN\rVert/\lVert N\rVert$. With ideal
Jacobians it is machine precision (the reproduction task gives $6.07\times10^{-16}$), and for the
standard EKF it rises to $O(10^{-1})$. That single number is a direct measure of "how much
information this filter put into unobservable directions".

**Where the assumption breaks**: this argument is about the **linearized** system. Even with zero
spurious information (FEJ), second- and higher-order nonlinearities remain; conversely, spurious
information can be present while other effects (an over-set noise model, conservative outlier
rejection) cancel it and NEES looks close to one. R5 and Part C are exactly that case.

### R4 — two expressions for the same Jacobian make different filters

Use 2D EKF-SLAM. State $x = (p_R, \theta, p_{f_1},\dots,p_{f_L})$, motion
$p_{R,k+1} = p_{R,k} + R(\theta_k)u_k$ and $\theta_{k+1} = \theta_k + \omega_k$, measurement
$z_{k,i} = R(\theta_k)^\top(p_{f_i} - p_{R,k})$. With
$J := \begin{bmatrix}0&-1\\1&0\end{bmatrix}$, in 2D we have $R(\theta)J = JR(\theta)$ (both belong
to the same one-parameter group).

The Jacobians are

$$
\Phi_k = \begin{bmatrix} I_2 & \star & 0\\ 0 & 1 & 0\\ 0 & 0 & I\end{bmatrix}, \qquad
H_{k,i} = \begin{bmatrix} -R(\theta_k)^\top & -J R(\theta_k)^\top(p_{f_i}-p_{R,k}) & R(\theta_k)^\top\end{bmatrix}, \tag{10}
$$

and the null space basis is the 2D version of R2 (two global translations plus one global
rotation):

$$
N_k = \begin{bmatrix} I_2 & J p_{R,k}\\ 0 & 1\\ I_2 & J p_{f_i}\end{bmatrix}. \tag{11}
$$

**Checking $H_kN_k = 0$.** The translation columns give $-R^\top + R^\top = 0$. The rotation column
gives

$$
-R^\top J p_{R} - JR^\top(p_f - p_R) + R^\top J p_f
  = R^\top J(p_f - p_R) - JR^\top(p_f - p_R) = 0, \tag{12}
$$

the last equality being $R^\top J = JR^\top$ (2D commutativity). **This identity holds whatever
value $R$ is evaluated at** — so the $H$ side is insensitive to the linearization point. The
problem is $\Phi$.

**Checking $\Phi_kN_k = N_{k+1}$.** The only thing that changes in (11) is the first block of the
rotation column, $Jp_{R,k}$, so the required condition is

$$
\star + J p_{R,k} = J p_{R,k+1} \quad\Longleftrightarrow\quad \star = J\,(p_{R,k+1} - p_{R,k}). \tag{13}
$$

In the true system $p_{R,k+1} - p_{R,k} = R(\theta_k)u_k$, so $\star$ can be written in **either**
of the two forms of (3). Substituting estimates, however,

$$
\hat p_{R,k+1\mid k} - \hat p_{R,k\mid k-1}
  \;\ne\; R(\hat\theta_{k\mid k-1})u_k \tag{14}
$$

because the left-hand side is propagated from the updated estimate $\hat p_{R,k\mid k}$ while the
right-hand side uses the pre-update heading. The difference is exactly the update correction at
epoch $k$. Hence **the only form that satisfies (13) is
$\star = J(\hat p_{R,k+1\mid k} - \hat p_{R,k\mid k-1})$**, and using it while evaluating $H$ and
$N$ at the first estimates ($\hat x_{k\mid k-1}$, and for landmarks their initial estimate) is
**FEJ**.

The measurements of the reproduction task show this directly — on the same data with the same
filter, changing only the expression for $\star$ drops $\lVert MN\rVert/\lVert N\rVert$ from
$2.658\times10^{-1}$ to $6.12\times10^{-16}$ and restores the null space dimension from 2 to 3.

**Where the assumption breaks**: FEJ evaluates its Jacobians at **older** estimates, so the
linearization error itself **grows** — the price of protecting the null space is the quality of the
first-order approximation. When that trade pays off depends on the problem, and Part C of the
reproduction task exhibits one setting where it does not. Also (12) relies on $R^\top J = JR^\top$,
which is special to 2D — in 3D, $R^\top\hat u \ne \hat u R^\top$, so the $H$ side also becomes
sensitive to the linearization point, which is why improving consistency in VIO is harder than in
2D SLAM (`li2013-vio-observability`).

### R5 — the three axes move separately

What R3 and R4 guarantee is "no information is injected into unobservable directions". They do
**not** guarantee NEES equal to one. There are at least three causes of inconsistency: (a)
spurious information (R3), (b) linearization error (R4 of `c5-manifold-estimation`), and (c) a
misspecified noise model. FEJ removes (a) while **increasing** (b). The two settings measured in
Part C of the reproduction task are the result. **[D1]**

When reporting, write the three axes separately: the null space dimension and $\lVert MN\rVert$
(observability and spurious information), $\mathrm{ANEES}/\dim$ (consistency), and RMSE or ATE
(accuracy). Be suspicious of a paper that argues one of them from another.

## Proof sketch

### R1 — the Hermann-Krener rank condition

**Hypotheses** H1: $f$ and $h$ are analytic and $\mathcal{M}$ is a $d$-dimensional analytic
manifold. H2: $\mathcal{O}(x_0) := \mathrm{span}\{\mathrm{d}L^k_{f_{u}}h_j(x_0)\}$ has dimension
$d$ at $x_0$.
**Conclusion** C: there is a neighbourhood $U$ of $x_0$ such that every $x \ne x_0$ in $U$ is
**distinguishable** from $x_0$ (local weak observability).

**Strategy**: build local coordinates out of the elements of the observability codistribution —
one application of the inverse function theorem is the whole proof.

1. **Build coordinates.** By H2 one can select $d$ linearly independent differentials
   $\mathrm{d}\varphi_1,\dots,\mathrm{d}\varphi_d$ from $\mathcal{O}(x_0)$ (each $\varphi_i$ being
   some $L^{k}_f h_j$).
2. **Inverse function theorem.** The Jacobian of
   $\varphi = (\varphi_1,\dots,\varphi_d) : \mathcal{M}\to\mathbb{R}^d$ is invertible at $x_0$, so
   $\varphi$ is a diffeomorphism on a neighbourhood of $x_0$. That is, $\varphi(x)$ **determines
   $x$ locally**.
3. **$\varphi$ is computed from the measurements.** Along a trajectory with the input $u$ held
   fixed, $L^k_f h_j$ is the $k$-th time derivative of the measurement $z(t) = h(x(t))$, so
   $\varphi(x_0)$ is a function of the measurements.
4. **Conclusion.** If two initial states produce the same measurement trajectory then their
   $\varphi$ values agree, and by step 2 they are locally the same point. Taking the
   contrapositive gives C.
5. **The subtlety in the converse.** The rank condition is **sufficient**. Even with deficient
   rank, states can be distinguishable in finite time (for non-analytic systems, or through
   structure that only appears under input switching). For analytic systems, however, the rank
   condition is also necessary at **generic** points — which is what licenses reading a rank
   deficiency as "unobservable" in practice.

**Delete a hypothesis**: weakening H1's analyticity to $C^\infty$ breaks the necessity direction
of step 5 (counterexamples are built from flat functions). If H2 holds only at $x_0$ and the rank
drops nearby, one does not obtain a **uniform** neighbourhood for local weak observability.

(Omitted: how the observability codistribution is generated over the inputs, and the involutivity
discussion for $\mathcal{O}$. `hermann1977-observability` Theorem 3.1 and its lemmas.)

### R2 — the four generators span the null space exactly

**Hypotheses** H1: the only measurements are a body-frame gyroscope and accelerometer plus
monocular bearings. H2: $g$ is constant with fixed magnitude and direction. H3: the accelerometer
bias is not in the state. H4: the motion is not degenerate (the negation of R2').
**Conclusions** C1: the group (2) preserves every measurement. C2: its generators (6) and (7) span
the null space of the linearized system **exactly** (dimension 4).

**Strategy**: show the inclusion both ways. $\subseteq$ by the invariance computation (derivation
R2), $\supseteq$ by a rank computation.

1. **$\mathrm{span}\{n_e, n_\psi\} \subseteq \ker M$.** Since the group preserves the measurements
   (C1, equations (4) and (5)), the residuals have no first-order change along the group
   directions, i.e. $M\,n = 0$. This step finishes **without numerics**.
2. **$\dim\mathrm{span}\{n_e, n_\psi\} = 4$.** The three vectors of (6) are independent along the
   translation directions, and (7) has a component $\delta\phi_k = R_k^\top u_g \ne 0$ that does
   not lie in their span.
3. **$\ker M \subseteq \mathrm{span}\{\cdot\}$ is shown only by rank.** This inclusion **depends
   on the motion**, so there is no general analytic proof. The standard procedure under H4 is to
   confirm that the numerical rank is $N - 4$, which is Part A of the reproduction task (the
   singular value gap is $1.3\times10^{-3}$ against $7.4\times10^{-11}$).
4. **If H4 fails.** The inclusion of step 3 fails and $\ker M$ grows. The reproduction task
   measures dimension 5 on a constant-acceleration trajectory, and the identity of that fifth
   direction is the scale/gravity family of `c5-imu-preintegration` R4 (confirmed in problem P6).

**Delete a hypothesis**: leaving the gravity **direction** unknown in H2 (the initialization stage)
adds two dimensions for roll and pitch, and dropping H3 creates degeneracies coupled to the bias.
Adding a single range measurement to H1 makes the scale observable but leaves the four dimensions
of (2) untouched — **a range sensor does not fix structural unobservability.**

(Omitted: proving the inclusion of step 3 analytically for particular motion classes.
`li2013-vio-observability` §3 and `hesch2014` organize it by motion class.)

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★, R2)** Rewrite (4) and (5) with no missing steps, then show: (a) point out exactly
where (4) fails for a rotation $R_\chi$ **off** the gravity axis; (b) conclude from that why roll
and pitch are observable while yaw is not; (c) state which parts of (2) survive and which
disappear when a single range measurement (a stereo baseline or LiDAR) is added.
*Strategy and key inequality*: (a) is the single line that $R_\chi^\top g = g$ holds only when
$\chi \parallel g$. The crux of (c) is that the denominator of (5) disappears — a range measurement
fixes $\lVert p_f - p_k\rVert$ and so determines the scale, but $R_\psi$ and $t$ still preserve
norms. **The purpose of this problem is to refute the common belief that "attaching a range sensor
makes everything observable".** The expansion is hidden.

**P2 (proof, ★★★, R1)** (a) Write the sufficiency argument of the Hermann-Krener rank condition
following steps 1-4 here, and (b) construct a counterexample of a system with deficient rank that
is nevertheless distinguishable. (c) Write a paragraph on why analyticity is needed for the
necessity direction.
*Strategy*: for (b), put a flat but non-analytic $C^\infty$ function (for instance 0 for $x < 0$
and $e^{-1/x}$ for $x > 0$) into the measurement function, so that all Lie derivatives vanish at
the origin while $x$ remains distinguishable. (c) passes if it uses the fact that an analytic
function is determined by all its derivatives at one point. The expansion is hidden.

**P3 (derivation, ★★, R4)** Derive (12) and (13) with no missing steps, and summarize in one
sentence the difference between (a) why (12) is insensitive to the linearization point and (b) why
(13) is sensitive. (c) Point out where the argument of (12) breaks in 3D.
*Solution sketch*: the difference between (a) and (b) is that "the null space condition on $H$ is
an identity **within one epoch** while the condition on $\Phi$ is an identity **linking two
epochs**". Only the latter is exposed to the temporal inconsistency of the estimates. (c) passes if
it uses the fact that the commutation relation of the form
$R^\top\hat u = \widehat{R^\top u}R^\top$ rotates the axis in 3D (the $\mathrm{Ad}$).

**P4 (numerical, ★, R2·R2')** On the VIO problem of the reproduction task, find (a) the numerical
rank and the null space dimension, (b) the singular values on either side of the rank boundary,
(c) $\lVert Mn\rVert/\lVert n\rVert$ for the four analytic generators, and (d) the null space
dimension after switching to the constant-acceleration trajectory.
*Answer*: (a) $N = 45$, 63 rows, rank **41**, null space **4**. (b)
$\sigma_{41} = 1.325\times10^{-3}$ and $\sigma_{42} = 7.368\times10^{-11}$ (eight orders apart).
(c) all four below $10^{-10}$ (reference $6.87, 4.63, 5.48, 8.40 \times10^{-11}$ — the noise floor
of central differences). (d) rank 40, null space **5**
($\sigma_{40} = 2.336\times10^{-2}$, $\sigma_{41} = 1.119\times10^{-10}$). Tolerances: rank and
dimension exactly; singular values within 10% relative error (they depend on the
finite-difference step).

**P5 (implementation, ★★★, R3·R4)** Implement 2D EKF-SLAM in three variants — ideal (true-state
Jacobians), standard EKF, and FEJ. Stack $M$ for each and report the null space dimension and
$\lVert MN\rVert/\lVert N\rVert$.
*Rubric*: (a) the three null space dimensions are 3 / 2 / 3 and the
$\lVert MN\rVert/\lVert N\rVert$ are of order $10^{-15}$ / $10^{-1}$ / $10^{-15}$; (b) the $N$ of
FEJ is evaluated at the **first estimates** and that of the ideal variant at the **truth** (mixing
them is an immediate reject); (c) both expressions of (3) are implemented and interchangeable, with
the effect of swapping only the expression reported; (d) it is shown numerically that changing $H$
to the first estimates is not enough on its own (without fixing the $\Phi$ expression the null
space is not restored).

**P6 (counterexample, ★★, R2'·R5)** (a) Confirm numerically that the fifth unobservable direction
that appears on the constant-acceleration trajectory of the reproduction task is the scale/gravity
family of `c5-imu-preintegration` R4 (project the four analytic generators out of the null space
basis and compare what is left against that family's generator). (b) Show with the two settings of
Part C that "preserving the null space improves consistency" is false, and (c) explain why using
the three causes of R5.
*Property checklist*: (a) must note that the scale generator takes the form
$(0,\ v_k,\ p_k,\ p_{f_i})$ mixed with a rotation component that is **not** about gravity — if it
does not match exactly, explaining **why it mixes** (in a frame where gravity is fixed, a change of
scale couples to a change of tilt) is the passing condition for (a). (b) may quote the numbers
directly, and (c) is the crux — it must identify the trade that FEJ removes spurious information at
the cost of a larger linearization error. "It depends on the case" does not pass.

**P7 (paper, ★★, R3·R4)** Read §3-5 of `huang2010-fej` and (a) confirm by equation number whether
the authors' FEJ makes the same correction as (13) here; (b) separate, in two lines each, what the
authors do and do not guarantee; (c) find three differences between the authors' NEES experiment
setup and Part C of the reproduction task, and discuss whether those differences could change the
direction of the result.
*Rubric*: (a) passes if it identifies that the relevant block of the transition Jacobian is written
as a difference of position estimates. (b) passes if it separates "null space preservation is
guaranteed" from "NEES = dim is not". (c) is excellent if it names three of trajectory length,
sensor range, landmark count and initial uncertainty, and Monte Carlo count, and says **in which
direction** each would move the result.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read with 3-pass and attack questions 4, 5, 6 and 7 on the third pass.

1. **Huang, Mourikis & Roumeliotis, "Observability-based rules for designing consistent EKF SLAM
   estimators" (2010, IJRR)** — role: `seminal`.
   <https://doi.org/10.1177/0278364909353640> (§3-5)
   Extra questions: (a) can the authors' "spurious information" be quantified by the
   $\lVert MN\rVert/\lVert N\rVert$ used here? (b) which choice in (3) does the difference between
   FEJ and OC-EKF correspond to?
2. **Li & Mourikis, "High-precision, consistent EKF-based visual-inertial odometry" (2013, IJRR)**
   — role: `standard`. <https://doi.org/10.1177/0278364913481251> (§3-4)
   Extra questions: (a) is the unobservable dimension the authors count the same 4 as in R2 here,
   and how does it change if the state definition differs? (b) how do the authors handle the
   problem that in 3D the $H$ side is also sensitive to the linearization point?
3. **Hermann & Krener, "Nonlinear controllability and observability" (1977, IEEE T-AC)** —
   role: `seminal`. <https://doi.org/10.1109/TAC.1977.1101601> (around Theorem 3.1)
   Extra questions: (a) distinguish the four variants (observable, locally observable, weakly
   observable, locally weakly observable) in one sentence each. (b) which of them do robotics
   papers prove while speaking of which?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) the independent and dependent variables and the baselines — were they tuned fairly?
(6) does the metric match the claim, and are variance and seeds reported? (7) what is missing for
reproduction? (8) if the result were wrong, which assumption would you doubt first?
(9) computational and memory complexity, and real-time feasibility. (10) what would you change to
surpass it in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one laptop CPU core. Parts A and B take under
five seconds each and the Monte Carlo of Part C under five minutes, in under 300 MB. Only numpy.

**The input data** is produced by the two generators below (deterministic, fixed seed). No external
dataset is needed.

**Part A — the VIO null space.** The generator below produces the true states and noise-free
measurements. Differentiate the residual function by central differences to build $M$, measure the
numerical rank from the singular values, and check that the analytic generators (6) and (7) lie in
the null space. Then switch to `const_acc=True` and see what happens to the null space dimension.

```python
"""c5-observability-consistency Part A: the VIO residual and the analytic null space generators."""

import numpy as np

G = np.array([0.0, 0.0, -9.81])
K, L, DTK = 4, 3, 0.5
LANDMARKS = np.array([[4.0, 1.0, 2.0], [-2.0, 3.0, 0.5], [1.0, -5.0, 3.0]])


def skew(w):
    return np.array([[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]])


def exp_so3(phi):
    t, W = float(np.linalg.norm(phi)), skew(phi)
    if t < 1e-10:
        return np.eye(3) + W + 0.5 * W @ W
    return np.eye(3) + np.sin(t) / t * W + (1.0 - np.cos(t)) / t**2 * W @ W


def log_so3(R):
    c = min(1.0, max(-1.0, (np.trace(R) - 1.0) / 2.0))
    t = float(np.arccos(c))
    W = 0.5 * (R - R.T) if t < 1e-10 else 0.5 * (R - R.T) * (t / np.sin(t))
    return np.array([W[2, 1], W[0, 2], W[1, 0]])


def truth(const_acc=False):
    """True attitudes, velocities and positions. const_acc=True gives constant world acceleration."""
    Rs, vs, ps = [], [], []
    for k in range(K):
        t = k * DTK
        Rs.append(exp_so3(np.array([0.1 * t, -0.2 * t, 0.6 * t + 0.3])))
        vs.append(np.array([1.0 + 0.2 * t, 0.3 * t, 0.1 * np.sin(t)]))
        if const_acc:
            ps.append(np.array([0.5 * t + 0.4 * t**2, 0.2 * t**2, 0.1 * t]))
        else:
            ps.append(
                np.array(
                    [
                        0.5 * t + 0.4 * t**2 + 0.3 * np.sin(2 * t),
                        0.2 * t**2,
                        0.1 * t + 0.2 * np.cos(t),
                    ]
                )
            )
    return Rs, vs, ps


def measurements(Rs, vs, ps):
    """Noise-free preintegrated measurements and bearings (so the residual vanishes at the truth)."""
    dRb = [Rs[k].T @ Rs[k + 1] for k in range(K - 1)]
    dvb = [Rs[k].T @ (vs[k + 1] - vs[k] - G * DTK) for k in range(K - 1)]
    dpb = [Rs[k].T @ (ps[k + 1] - ps[k] - vs[k] * DTK - 0.5 * G * DTK**2) for k in range(K - 1)]
    bear = []
    for k in range(K):
        for i in range(L):
            d = Rs[k].T @ (LANDMARKS[i] - ps[k])
            bear.append(d / np.linalg.norm(d))
    return dRb, dvb, dpb, bear
```

The state vector is laid out as $x = (\delta\phi_0..\delta\phi_{K-1},\ v_0..v_{K-1},\
p_0..p_{K-1},\ p_{f_0}..p_{f_{L-1}}) \in \mathbb{R}^{45}$, with the attitudes parameterized by the
right perturbation $R_k \leftarrow \bar R_k\exp(\delta\phi_k)$. The residuals are
$\mathrm{Log}(\bar{\Delta R}_k^\top R_k^\top R_{k+1})$,
$R_k^\top(v_{k+1}-v_k-g\Delta t) - \bar{\Delta v}_k$,
$R_k^\top(p_{k+1}-p_k-v_k\Delta t-\tfrac12 g\Delta t^2) - \bar{\Delta p}_k$, and the bearing
residual $\widehat{R_k^\top(p_{f_i}-p_k)} - \bar b$ (63 rows in total). Use a central-difference
step of $10^{-6}$ and a rank threshold of $\sigma_1\cdot10^{-8}$.

**Parts B and C — 2D EKF-SLAM and FEJ.** Use the generator below.

```python
"""c5-observability-consistency Parts B and C: a 2D EKF-SLAM simulator."""

import numpy as np

JM = np.array([[0.0, -1.0], [1.0, 0.0]])
SEED = 20261112
STEPS, L2 = 30, 4
SIG_U, SIG_W, SIG_Z = 0.03, 0.01, 0.05
U_ODO = np.array([0.2, 0.0])
OMEGA = 0.12
LM2 = np.array([[3.0, 1.0], [-1.0, 3.5], [2.0, -2.5], [-3.0, -1.0]])
LM_OFFSET = np.array([0.15, -0.10])
N_DIM = 3 + 2 * L2


def rot2(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])


def simulate2(seed):
    """The true trajectory, the odometry measurements and the landmark observations."""
    rng = np.random.default_rng(seed)
    p, th = np.zeros(2), 0.0
    tr, odo, obs = [(p.copy(), th)], [], []
    for _ in range(STEPS):
        u = U_ODO + rng.normal(scale=SIG_U, size=2)
        w = OMEGA + rng.normal(scale=SIG_W)
        p = p + rot2(th) @ u
        th = th + w
        tr.append((p.copy(), th))
        odo.append((u, w))
        obs.append([rot2(th).T @ (pl - p) + rng.normal(scale=SIG_Z, size=2) for pl in LM2])
    return tr, odo, obs


def h_block(theta, p, pf, i):
    """The measurement Jacobian of (10)."""
    H = np.zeros((2, N_DIM))
    Rt = rot2(theta).T
    H[:, :2] = -Rt
    H[:, 2] = -JM @ Rt @ (pf - p)
    H[:, 3 + 2 * i : 5 + 2 * i] = Rt
    return H


def null_basis(p_robot, lms):
    """The null space basis of (11): two global translations plus one global rotation."""
    N = np.zeros((N_DIM, 3))
    N[:2, :2] = np.eye(2)
    N[:2, 2] = JM @ p_robot
    N[2, 2] = 1.0
    for i in range(len(lms)):
        N[3 + 2 * i : 5 + 2 * i, :2] = np.eye(2)
        N[3 + 2 * i : 5 + 2 * i, 2] = JM @ lms[i]
    return N
```

**What to do.** The initial state has the robot pose at the truth (covariance $10^{-6}I_3$) and the
landmarks at `LM2 + LM_OFFSET` (covariance $0.3^2 I$). Implement three variants.

| Variant | where $H$ is evaluated | the $(1,3)$ block of $\Phi$ | where $N$ is evaluated |
|---|---|---|---|
| ideal | the true state | $J R(\theta_k)u_k$, at the truth | the true state |
| standard EKF | the current estimate $\hat x_{k\mid k}$ | $J R(\hat\theta_{k\mid k})u_k$ | the true state |
| FEJ | the first estimate $\hat x_{k\mid k-1}$, landmarks at their initial estimate | $J(\hat p_{k+1\mid k} - \hat p_{k\mid k-1})$ | the first estimates |

Stack $M$ as in (8) ($L_2$ measurements × 2 rows per epoch, 240 rows in total). Use a rank
threshold of $\sigma_1\cdot10^{-10}$.

**Part C — NEES.** With the setting above (setting 1), measure the $\mathrm{ANEES}/\dim$ of the
standard EKF and of FEJ over 500 Monte Carlo runs (seeds $\mathrm{SEED}+m$). Then switch to
**setting 2** and measure again — $\mathrm{STEPS} = 300$, $u = (0.15, 0)$, $\omega = 0.05$,
$\sigma_u = 0.03$, $\sigma_w = 0.03$, $\sigma_z = 0.08$, a sensing radius of $3.0$ (only landmarks
inside it are observed), landmarks `np.random.default_rng(11).uniform(-6.0, 6.0, (25, 2))`, initial
landmark estimates at the truth plus Gaussian noise of standard deviation $0.5$ (covariance
$0.5^2 I$), a robot pose prior of $10^{-6}I_3$, and 200 runs.

**Acceptance criteria — all four conditions must hold.**

1. **Part A (varying acceleration)** — rank **41** and null space dimension **4** (exactly),
   $\sigma_{41} = 1.325\times10^{-3}$ and $\sigma_{42} = 7.368\times10^{-11}$ (within 10% relative
   error — they depend on the finite-difference step), and all four analytic generators satisfy
   $\lVert Mn\rVert/\lVert n\rVert < 10^{-9}$ (reference $6.9, 4.6, 5.5, 8.4\times10^{-11}$).
2. **Part A (constant acceleration)** — the same code with `const_acc=True` gives rank **40** and
   null space dimension **5** ($\sigma_{40} = 2.336\times10^{-2}$,
   $\sigma_{41} = 1.119\times10^{-10}$). The four generators are still in the null space. The point
   is that **the motion adds a direction to the structural unobservability.**
3. **Part B** — reproduce the table below (the null space dimensions exactly, the norms to within
   an order of magnitude).

   | Variant | rows | rank | null dim | $\lVert MN\rVert/\lVert N\rVert$ |
   |---|---|---|---|---|
   | ideal | 240 | 8 | 3 | $6.07\times10^{-16}$ |
   | standard EKF | 240 | 9 | 2 | $2.658\times10^{-1}$ |
   | FEJ | 240 | 8 | 3 | $6.12\times10^{-16}$ |

   In addition, report that reverting only the $(1,3)$ block of $\Phi$ in FEJ to
   $JR(\hat\theta_{k\mid k-1})u_k$ **fails to restore** the null space (the reference
   implementation gives $\lVert MN\rVert/\lVert N\rVert = 4.3\times10^{-2}$ and null space
   dimension 2) — **changing $H$ to the first estimates is not enough on its own.**
4. **Part C** — report the $\mathrm{ANEES}/\dim$ of both settings. Reference implementation:
   setting 1 (30 steps, all visible, 500 runs) gives standard $0.738$ / FEJ $0.738$
   (**indistinguishable**), and setting 2 (300 steps, range limited, 200 runs) gives standard
   $0.915$ / FEJ $1.265$ (**FEJ is the more overconfident**). The position RMSEs are
   $0.0438$ / $0.0434$ m and $0.1409$ / $0.1543$ m respectively — in setting 2 FEJ is worse in
   accuracy too. Tolerances $\pm0.05$ (ANEES) and $\pm0.01$ m.
   **The passing condition for this part is not to reproduce "FEJ is better", but to report with
   numbers that the three axes (spurious information, consistency, accuracy) move separately, and
   to explain it with the three causes of R5.**

**Baselines**: (a) the baseline for Parts A and B is the "ideal Jacobian" variant (same data,
linearized at the truth). (b) The second baseline for Part B is the FEJ variant with only the
$\Phi$ expression changed (the additional report of criterion 3). (c) The baseline for Part C is
the standard EKF. Optional: reduce the initial landmark uncertainty from $0.3$ to $0.05$ and see how
the standard EKF's value in Part B changes (spurious information shrinks together with the
estimation error).

**Numbers to report**: every value of the four criteria, plus the magnitude of what is left after
projecting the four analytic generators out of the null space basis in both cases of Part A (the
noise floor for varying acceleration, $O(1)$ for constant — the starting point of problem P6).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The Part A null space is 0 or 1 | an anchor or prior factor was included, which fixes the gauge and removes the null space | check that the residuals contain no absolute measurement (IMU and bearings only) |
| The Part A null space is larger than 4 but the generators are right | too few landmarks or keyframes, or degenerate motion | raise $K$ to 5-6 and $L$ to 6-8 and see whether it returns to 4 |
| $\lVert Mn\rVert$ for the Part A generators is of order $10^{-6}$ | the central-difference step is too small or too large (round-off or truncation) | sweep the step over $10^{-4}$ to $10^{-7}$ and find the minimum |
| Only the Part A yaw generator is not in the null space | $u_g$ was put directly into $\delta\phi_k$ of (7) (the left-perturbation coordinate) | in the right-perturbation convention it must be $R_k^\top u_g$ |
| Even the ideal variant of Part B does not give null space 3 | $N$ was evaluated at the landmark **estimates** | the ideal variant's $N$ is evaluated at the truth |
| Part B FEJ matches the standard EKF | the $(1,3)$ block of $\Phi$ was not changed | first reproduce the additional report of criterion 3 |
| The Part B ranks jump around between variants | the threshold is too loose | print the singular values on a log scale and locate the gap by eye |
| The Part C ANEES is of order $10^2$ | the angle error was not wrapped | check that $\mathrm{atan2}(\sin\delta,\cos\delta)$ is used |

## Open problems

- **(Open problem) A quantitative link between null space preservation and consistency** — R3 and
  R4 give a way to remove spurious information, but there is no quantitative statement about how
  much that improves NEES. Part C of the reproduction task exhibits a setting with no improvement
  (indeed a reversal). Current approaches are per-setting experimental reports
  ([Huang et al.](https://doi.org/10.1177/0278364909353640),
  [Li & Mourikis](https://doi.org/10.1177/0278364913481251)) and designs that reduce the
  linearization error itself, like invariant filtering
  ([InEKF](https://arxiv.org/abs/1410.1465)). What is missing: a bound from a spurious-information
  measure such as $\lVert MN\rVert$ to $\mathbb{E}[\mathrm{NEES}]$.
- **(Open problem) Detecting degenerate motion online** — R2' shows that motion enlarges the null
  space, but what is actually needed is a real-time measure of "how close is the motion over this
  interval to degeneracy". The smallest singular value of $M$ is scale dependent and sensitive to
  the state units, which makes thresholding hard. Current approaches: per-motion-class degeneracy
  lists ([Hesch et al.](https://doi.org/10.1177/0278364913509675)) and condition-number
  heuristics. What is missing: a unit-invariant degeneracy index with a guarantee on its verdict.
- **(Open problem) Observability of systems with a learned front end** — R1 and R2 analyze the case
  where the measurement model is given analytically. If the measurement is the output of a neural
  network (a learned relative pose, a depth, a feature matching score), Lie derivatives are
  unavailable and the invariance group is not guaranteed. Current approaches: treating the learned
  output as a "virtual measurement" with an attached covariance, and the discussion in §III-IV of
  the [long-term SLAM survey](https://arxiv.org/abs/1606.05830). What is missing: a way to
  **define and measure** unobservable directions for a learned measurement model.

## Concept check

Run `rc quiz c5-observability-consistency`. The quiz is for **concept checking only**; the real
work is the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: why yaw is unobservable while roll and pitch are observable in monocular
visual-inertial estimation; what happens to the unobservable subspace when a range measurement is
added; whether evaluating only the measurement Jacobian at the first estimates fixes EKF
inconsistency; why two algebraically identical Jacobian expressions give different EKFs; and what
exactly is guaranteed when a filter's null space is preserved to machine precision.

## How to study this stage

1. **Check the invariance group by hand first (45 min)** — write (4) and (5) on paper and mark the
   place where $R_\psi^\top g = g$ is used. Then substitute a rotation off the gravity axis and
   watch (4) fail. R2 of this lesson is those two lines and nothing more.
2. **Write the generators yourself (30 min)** — reconstruct (6) and (7) from a blank page. In
   particular, confirm against R2 of `c5-manifold-estimation` that the $R_k^\top u_g$ in (7) comes
   from the right-perturbation convention. Getting the convention wrong makes exactly the yaw
   generator fail in Part A.
3. **Run Part A first (60 min)** — plot the singular values on a log axis and see the eight-order
   gap with your own eyes. Then switch to `const_acc=True`, watch the dimension become 5, and track
   down what the extra direction is with P6. Connecting it to `c5-imu-preintegration` R4 is the
   best moment in this lesson.
4. **Do (12) and (13) on paper (60 min)** — if you can state their difference ("an identity within
   one epoch" versus "an identity linking two epochs") in one sentence, you have understood FEJ.
   P3 asks for exactly that spot.
5. **Part B in three variants (90 min)** — implement ideal, then standard, then FEJ. Watch
   $\lVert MN\rVert$ jump to $10^{-1}$ for the standard EKF, and measure FEJ **both before and
   after** fixing $\Phi$. The value before the fix ($4.3\times10^{-2}$) — "so close and yet not
   there" — is the most memorable number in this lesson.
6. **Write Part C up as a report (60 min)** — measure the ANEES of both settings and write honestly
   about **the case where FEJ is worse**. The habit of reporting the three axes separately starts
   here, and it is the habit you will use most when reading papers.
7. **Read the papers separating claims from measurements (150 min)** — go through §3-5 of Huang et
   al. marking where "null space preservation" and "NEES improvement" are each claimed and each
   measured. Find in §3-4 of Li & Mourikis the extra difficulties of moving to 3D, and fix the
   definitions precisely with Hermann & Krener. Write the one-page note per paper **without
   exception**.
8. **End at what cannot be done (30 min)** — pick one of the three open problems and write a
   paragraph. A bound from the spurious-information measure to NEES is directly motivated by
   Part C.

**Passing bar**: you can write (4), (5) and the generators (6), (7) from a blank page, you can
explain the difference between (12) and (13), you have code that satisfies all four conditions of
the reproduction task, and you have notes on all three papers.
