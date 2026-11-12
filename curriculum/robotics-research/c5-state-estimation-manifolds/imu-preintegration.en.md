---
id: c5-imu-preintegration
lang: en
title: IMU preintegration and inertial fusion
summary: >-
  Start from IMU kinematics and prove that the three relative motion quantities (dR, dv, dp) are
  functions of the IMU measurements and the bias alone, independent of the initial state. Derive
  the Jacobian recursions of the first-order correction that avoids re-integrating when the bias
  changes, and the nine-dimensional covariance propagation of preintegration noise. Then derive,
  and confirm numerically, that under constant acceleration the scale and gravity direction of
  monocular visual-inertial fusion admit two exact solutions.
objectives:
  - Integrate the IMU kinematics and derive the preintegration identity with no missing steps.
  - Explain why the preintegrated quantities are independent of the initial state and where the gravity bookkeeping works out.
  - Derive the Jacobian recursions of bias relinearization and confirm numerically that the correction error is second order.
  - Write the covariance propagation matrices A and B of preintegration noise and validate them by Monte Carlo.
  - Find the second solution for scale and gravity direction under constant acceleration in closed form.
  - Distinguish preintegration error from discretization error.
tags: [state-estimation, imu, preintegration, visual-inertial, observability, research]
---

# IMU preintegration and inertial fusion

## Setup and notation

The Lie group notation of `c5-manifold-estimation` ($\exp$, $\log$, $J_r$, $\mathrm{Ad}$) and the
factor graph notation of `c5-factor-graphs-map` carry over. Additional symbols:

| Symbol | Meaning |
|---|---|
| $R_t \in SO(3)$, $v_t, p_t \in \mathbb{R}^3$ | attitude, velocity and position at time $t$; velocity and position are in the **world frame** |
| $g \in \mathbb{R}^3$ | the gravity vector in the world frame; here $(0,0,-9.81)$ |
| $\tilde\omega_k$, $\tilde a_k$ | the angular rate and acceleration of IMU sample $k$ (**body frame**) |
| $b^g$, $b^a$ | gyroscope and accelerometer biases (body frame), taken constant within one interval |
| $\eta^g_k$, $\eta^a_k$ | per-sample white noise, $\eta^g_k\sim\mathcal{N}(0,\sigma_g^2 I)$ and $\eta^a_k\sim\mathcal{N}(0,\sigma_a^2 I)$ |
| $\Delta t$, $n$, $\Delta t_{ij} = n\Delta t$ | the IMU sample interval, the number of samples from keyframe $i$ to $j$, and the interval length |
| $\Delta R_{ij}$, $\Delta v_{ij}$, $\Delta p_{ij}$ | the **preintegrated measurements**, defined in (4)-(6) |
| $J^R_g$, $J^v_g$, $J^v_a$, $J^p_g$, $J^p_a$ | the bias Jacobians of the preintegrated quantities |
| $\delta\xi = (\delta\phi, \delta v, \delta p) \in \mathbb{R}^9$ | the error state of the preintegration noise |

**The measurement model** (body frame, additive bias plus white noise):

$$
\tilde\omega_k = \omega_k + b^g + \eta^g_k, \qquad
\tilde a_k = R_k^\top\!\left(a_k - g\right) + b^a + \eta^a_k. \tag{1}
$$

Here $a_k$ is the **world-frame acceleration**, and the $-g$ appears because an accelerometer
measures non-gravitational ("proper") acceleration. The second equation of (1) is why an IMU at
rest reports $9.81\,\mathrm{m/s^2}$ upward.

**The discretization convention (important).** This lesson **fixes by definition** the following
rectangular rule:

$$
R_{k+1} = R_k\exp\!\big((\tilde\omega_k - b^g - \eta^g_k)\Delta t\big), \quad
v_{k+1} = v_k + a^w_k\Delta t, \quad
p_{k+1} = p_k + v_k\Delta t + \tfrac12 a^w_k\Delta t^2, \tag{2}
$$

$$
a^w_k := R_k(\tilde a_k - b^a - \eta^a_k) + g. \tag{3}
$$

The identity in R1 is **exact under this convention**. Switching to a midpoint or Runge-Kutta rule
changes the form of the identity (problem P1) — which is why **the discretization convention is
the first thing to check** when comparing an implementation against a paper.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the preintegration identity) [D3]** — defining the relative motion quantities as
  $$
  \Delta R_{ij} := R_i^\top R_j, \tag{4}
  $$
  $$
  \Delta v_{ij} := R_i^\top\!\big(v_j - v_i - g\,\Delta t_{ij}\big), \tag{5}
  $$
  $$
  \Delta p_{ij} := R_i^\top\!\big(p_j - p_i - v_i\,\Delta t_{ij} - \tfrac12 g\,\Delta t_{ij}^2\big) \tag{6}
  $$
  then under (2) and (3) all three are **functions of the IMU measurements and the bias alone**,
  with no dependence whatsoever on $R_i, v_i, p_i$:
  $$
  \Delta R_{ij} = \prod_{k=i}^{j-1}\exp(\psi_k), \quad
  \Delta v_{ij} = \sum_{k} \Delta R_{ik}\,\alpha_k\,\Delta t, \quad
  \Delta p_{ij} = \sum_{k}\Big[\Delta v_{ik}\Delta t + \tfrac12 \Delta R_{ik}\,\alpha_k\Delta t^2\Big], \tag{7}
  $$
  where $\psi_k := (\tilde\omega_k - b^g - \eta^g_k)\Delta t$ and
  $\alpha_k := \tilde a_k - b^a - \eta^a_k$. So **the preintegration is never recomputed** when the
  keyframe states are updated — that is the whole of preintegration.
- **R2 (the first-order bias relinearization) [D2]** — to reuse a preintegration computed at
  $\bar b$ at a new bias $\bar b + \delta b$, instead of re-integrating one uses
  $$
  \Delta R_{ij}(\bar b + \delta b) \approx \Delta R_{ij}(\bar b)\exp\!\big(J^R_g\,\delta b^g\big), \quad
  \begin{aligned}
  \Delta v_{ij} &\approx \Delta v_{ij} + J^v_g\delta b^g + J^v_a\delta b^a,\\
  \Delta p_{ij} &\approx \Delta p_{ij} + J^p_g\delta b^g + J^p_a\delta b^a.
  \end{aligned} \tag{8}
  $$
  The Jacobians come out of recursions run **in the same loop** as the integration ((11)-(15)), and
  the correction error is $O(\lVert\delta b\rVert^2)$. As measured in the reproduction task,
  raising $\lVert\delta b\rVert$ by three decades from $10^{-4}$ to $10^{-1}$ raises the error by
  exactly $10^6$ (quadratic constants: $0.0094$ for $\Delta R$, $0.164$ for $\Delta v$, $0.0240$
  for $\Delta p$).
- **R3 (covariance propagation of preintegration noise) [D2]** — the error state
  $\delta\xi_{ik} \in \mathbb{R}^9$ propagates linearly as
  $\delta\xi_{i,k+1} = A_k\,\delta\xi_{ik} + B_k\,\eta_k$, so
  $$
  \Sigma_{i,k+1} = A_k\Sigma_{ik}A_k^\top + B_k\Sigma_\eta B_k^\top, \qquad
  \Sigma_\eta = \mathrm{diag}(\sigma_g^2 I,\ \sigma_a^2 I), \tag{9}
  $$
  with $A_k$ and $B_k$ given explicitly in (16) and (17). The $9\times9$ covariance comes out of
  the integration loop, ready for the IMU factor of a factor graph.
- **R4 (a second solution for scale and gravity under constant acceleration) [D2]** — if the
  world-frame acceleration is constant, $a_t \equiv c$, then scaling the scene and the trajectory
  by $\lambda$ and replacing gravity by $g^\ast = g + (\lambda-1)c$ produces **the same IMU
  measurements and the same bearings**. Fixing the magnitude $\lVert g\rVert$ leaves only two
  admissible values of $\lambda$:
  $$
  \lambda = 1 \qquad\text{or}\qquad
  \lambda^\ast = 1 - \frac{2\,g^\top c}{\lVert c\rVert^2}. \tag{10}
  $$
  In other words, in monocular visual-inertial initialization **the scale and the gravity
  direction cannot be told apart over a constant-acceleration interval.** As measured in the
  reproduction task, at $c = (0.5,-0.3,1.2)$ with $g = (0,0,-9.81)$ we get
  $\lambda^\ast = 6331/445 = 14.2269662921$ — a scale error of a factor of 14 that matches the
  measurements **perfectly**.
- **R5 (preintegration error and discretization error are different things) [D1]** — R1 is an
  **exact identity** for the discrete model (2). The model (2) itself, however, is an
  $O(\Delta t)$ approximation of the continuous one. So the $10^{-15}$ agreement of Part A of the
  reproduction task means "preintegration is exact", and the error against the continuous
  trajectory has to be measured separately by shrinking $\Delta t$. Always check which of the two
  a paper means by "preintegration error".

## Derivation

### R1 — the preintegrated quantities forget the initial state

Unroll (2) from $i$ to $j$. Rotation is a product, so immediately

$$
R_j = R_i\prod_{k=i}^{j-1}\exp(\psi_k) \quad\Longrightarrow\quad
  \Delta R_{ij} = R_i^\top R_j = \prod_{k=i}^{j-1}\exp(\psi_k). \tag{7a}
$$

$R_i$ cancels. The intermediate rotations follow the same way: $R_k = R_i\Delta R_{ik}$.

**Velocity.** Summing the second equation of (2),

$$
v_j - v_i = \sum_{k=i}^{j-1} a^w_k\Delta t
  = \sum_{k} \big[R_k\alpha_k + g\big]\Delta t
  = g\,\Delta t_{ij} + \sum_{k} R_i\Delta R_{ik}\,\alpha_k\,\Delta t.
$$

Multiplying by $R_i^\top$ and moving $g\Delta t_{ij}$ across turns the definition (5) directly
into the second equation of (7). $R_i$ is absorbed into $\Delta R_{ik}$ and $v_i$ is gone from the
definition.

**Position.** This is the only delicate point. Summing the third equation of (2),

$$
p_j - p_i = \sum_{k=i}^{j-1}\Big[v_k\Delta t + \tfrac12 a^w_k\Delta t^2\Big]
  = \underbrace{\sum_k v_k\Delta t}_{(\mathrm{I})}
  + \underbrace{\sum_k \tfrac12 g\Delta t^2}_{(\mathrm{II})}
  + \underbrace{\sum_k \tfrac12 R_i\Delta R_{ik}\alpha_k\Delta t^2}_{(\mathrm{III})}.
$$

Into (I) substitute $v_k = v_i + g\,\Delta t_{ik} + R_i\Delta v_{ik}$, which is (5) written for
$i\to k$ (with $\Delta t_{ik} = (k-i)\Delta t$):

$$
(\mathrm{I}) = v_i\Delta t_{ij}
  + g\,\Delta t^2\sum_{k=i}^{j-1}(k-i)
  + R_i\sum_k \Delta v_{ik}\Delta t
  = v_i\Delta t_{ij} + g\,\Delta t^2\frac{n(n-1)}{2} + R_i\sum_k\Delta v_{ik}\Delta t,
$$

while $(\mathrm{II}) = \tfrac12 g\,n\,\Delta t^2$. Adding the two gravity terms works out
**exactly**:

$$
g\Delta t^2\left[\frac{n(n-1)}{2} + \frac n2\right] = g\Delta t^2\frac{n^2}{2}
  = \tfrac12 g\,\Delta t_{ij}^2. \tag{7b}
$$

Hence

$$
p_j - p_i = v_i\Delta t_{ij} + \tfrac12 g\Delta t_{ij}^2
  + R_i\sum_k\Big[\Delta v_{ik}\Delta t + \tfrac12\Delta R_{ik}\alpha_k\Delta t^2\Big],
$$

and rearranging into the form of (6) gives the third equation of (7). All of $R_i$, $v_i$ and
$p_i$ have moved to the left-hand side.

**Where the assumption breaks**: the bookkeeping in (7b) works because $v$ and $p$ were updated
with **the same $a^w_k$ and the same rectangular rule**. Switching to a midpoint rule (updating
$p$ with $v_{k+1/2}$) turns $\sum(k-i)$ into $\sum(k-i+\tfrac12)$, and (7b) then **does not**
produce $\tfrac12 g\Delta t_{ij}^2$. An implementation that uses a midpoint rule while keeping
definition (6) acquires a systematic position bias proportional to the interval length, on the
order of $\tfrac12\cdot9.81\cdot(\Delta t/2)\cdot\Delta t_{ij}$ at
$\Delta t_{ij} = 0.5\,\mathrm{s}$. Taking $b^g, b^a$ constant within the interval is also a
premise of (7) — a bias random walk does not belong in the noise of R3 and has to be modelled as a
separate factor.

### R2 — the recursions for the bias Jacobians

Start with $\Delta R$. We have $\Delta R_{i,k+1} = \Delta R_{ik}\exp(\psi_k)$ and
$\partial\psi_k/\partial b^g = -I\Delta t$. Defining $J^R_g$ through
$\Delta R_{ik}(\bar b^g + \delta) \approx \Delta R_{ik}\exp(J^R_{g,k}\delta)$,

$$
\Delta R_{i,k+1}(\bar b + \delta)
  \approx \Delta R_{ik}\exp\!\big(J^R_{g,k}\delta\big)\,
    \exp(\psi_k)\exp\!\big(-J_r(\psi_k)\Delta t\,\delta\big),
$$

where the last exponential comes from
$\exp(\psi_k + \partial\psi_k\delta) \approx \exp(\psi_k)\exp(J_r(\psi_k)\partial\psi_k\delta)$,
the defining property of the right Jacobian (the notation table of `c5-manifold-estimation`). Now
swap the order of the two middle exponentials — in $SO(3)$,
$\exp(u)\exp(\psi) = \exp(\psi)\exp(\exp(-\psi)\,u)$ since $\mathrm{Ad}_{R} = R$:

$$
\Delta R_{i,k+1}(\bar b+\delta) \approx \Delta R_{i,k+1}
  \exp\!\Big(\big[\exp(-\psi_k)J^R_{g,k} - J_r(\psi_k)\Delta t\big]\delta\Big)
$$

$$
\Longrightarrow\quad
J^R_{g,k+1} = \Delta R_{k,k+1}^\top J^R_{g,k} - J_r(\psi_k)\,\Delta t,
  \qquad J^R_{g,i} = 0. \tag{11}
$$

For $\Delta v$: differentiating the second equation of (7) in $b^a$ changes $\alpha_k$ by
$-\delta b^a$, so

$$
J^v_{a,k+1} = J^v_{a,k} - \Delta R_{ik}\,\Delta t. \tag{12}
$$

Differentiating in $b^g$ instead moves $\Delta R_{ik}$. Since
$\Delta R_{ik}(\bar b+\delta)\alpha_k \approx \Delta R_{ik}(I + \widehat{J^R_{g,k}\delta})\alpha_k
= \Delta R_{ik}\alpha_k - \Delta R_{ik}\widehat{\alpha_k}J^R_{g,k}\delta$ (using
$\hat x y = -\hat y x$),

$$
J^v_{g,k+1} = J^v_{g,k} - \Delta R_{ik}\,\widehat{\alpha_k}\,J^R_{g,k}\,\Delta t. \tag{13}
$$

For $\Delta p$, apply the same two rules to the third equation of (7):

$$
J^p_{a,k+1} = J^p_{a,k} + J^v_{a,k}\Delta t - \tfrac12\Delta R_{ik}\Delta t^2, \tag{14}
$$

$$
J^p_{g,k+1} = J^p_{g,k} + J^v_{g,k}\Delta t
  - \tfrac12\Delta R_{ik}\widehat{\alpha_k}J^R_{g,k}\Delta t^2. \tag{15}
$$

**Mind the order**: (14) and (15) use the **pre-update** $J^v$ and $\Delta R_{ik}$, (12) and (13)
the pre-update $\Delta R_{ik}$ and $J^R_{g,k}$, and (11) the pre-update $J^R_{g,k}$. The loop must
therefore go $p \to v \to R$ — this is the single most common implementation bug (see the
diagnosis table).

**Where the assumption breaks**: (8) is a first-order expansion, so the error is
$O(\lVert\delta b\rVert^2)$. The reproduction task measures that quadratic constant directly, and
at $\lVert\delta b^g\rVert = 0.1\ \mathrm{rad/s}$ (a large change in the gyro bias) the $\Delta v$
correction is already off by $1.6\times10^{-3}\,\mathrm{m/s}$. So when the bias estimate moves a
lot, **re-integrate** — this is where the fluid relinearization threshold of iSAM2
(`c5-sparsity-isam` R3) acquires a concrete meaning.

### R3 — the covariance of preintegration noise

Define the errors as
$\delta\phi_{ik} := \mathrm{Log}(\Delta R_{ik}^\top\Delta\tilde R_{ik})$,
$\delta v_{ik} := \Delta\tilde v_{ik} - \Delta v_{ik}$ and
$\delta p_{ik} := \Delta\tilde p_{ik} - \Delta p_{ik}$ (the tilde carries the noise). Applying the
two rules of R2 — pulling a perturbation out of an exponential with $J_r$, and
$\hat x y = -\hat y x$ — gives

$$
A_k = \begin{bmatrix}
  \Delta R_{k,k+1}^\top & 0 & 0\\
  -\Delta R_{ik}\widehat{\alpha_k}\Delta t & I & 0\\
  -\tfrac12\Delta R_{ik}\widehat{\alpha_k}\Delta t^2 & I\Delta t & I
\end{bmatrix}, \qquad
B_k = \begin{bmatrix}
  J_r(\psi_k)\Delta t & 0\\
  0 & \Delta R_{ik}\Delta t\\
  0 & \tfrac12\Delta R_{ik}\Delta t^2
\end{bmatrix} \tag{16}
$$

to be propagated by (9). Note that the first column of $A_k$ has **the same structure** as (13)
and (15) of R2 — because a bias perturbation and a noise perturbation travel the same path. The
initial value is $\Sigma_{ii} = 0_{9\times9}$.

$$
\eta_k = \begin{bmatrix}\eta^g_k\\ \eta^a_k\end{bmatrix}
  \sim \mathcal{N}\!\left(0, \Sigma_\eta\right),
  \qquad \Sigma_\eta = \mathrm{diag}(\sigma_g^2 I_3,\ \sigma_a^2 I_3). \tag{17}
$$

**Mind the units**: (17) is the **per-sample discrete** noise. If the datasheet gives a noise
density $\sigma^{\mathrm{cont}}$ (in $\mathrm{rad/s/\sqrt{Hz}}$), it must be converted as
$\sigma_g = \sigma_g^{\mathrm{cont}}/\sqrt{\Delta t}$; forgetting this makes the covariance wrong
by a factor of $\Delta t$. The reproduction task specifies the discrete noise directly to avoid
the confusion.

**A sanity check.** For small steps where $J_r \approx I$, the rotation error is
$\delta\phi \approx \sum_k \eta^g_k\Delta t$, so its standard deviation is
$\sigma_g\Delta t\sqrt n$. In the reproduction task's setting ($\sigma_g = 0.004$,
$\Delta t = 0.005$, $n = 100$) this is $0.004\cdot0.005\cdot10 = 2\times10^{-4}$, and the measured
analytic value is exactly $2.000\times10^{-4}$. The $\delta v$ standard deviation is
$1.126\times10^{-3}$, 12.6% larger than $\sigma_a\Delta t\sqrt n = 10^{-3}$, and the difference is the
contribution of the $-\Delta R\widehat\alpha\Delta t$ coupling in $A_k$ — the path by which
rotation error leaks into velocity.

**Where the assumption breaks**: (16) is first order and treats $\Sigma_\eta$ as constant and
white. A real IMU has a bias random walk (low frequency) and mechanical resonance and saturation
(high frequency), neither of which is white. The longer the interval, the more the first-order
expansion errs on the underestimating side, and no bound on that is known (an open problem).

### R4 — over a constant-acceleration interval, scale and gravity are indistinguishable

A monocular camera supplies only **bearings** (directions). Scaling both the scene and the
trajectory by $\lambda > 0$ gives

$$
\frac{R_k^\top(\lambda p_\ell - \lambda p_k)}{\lVert \lambda p_\ell - \lambda p_k\rVert}
  = \frac{R_k^\top(p_\ell - p_k)}{\lVert p_\ell - p_k\rVert}
$$

so **the bearings do not change at all.** What pins the scale down is the IMU. By the second
equation of (1) an accelerometer sees $R_k^\top(a_k - g)$, and scaling the trajectory by $\lambda$
sends $a_k \to \lambda a_k$. So producing the same measurements requires, for some $g^\ast$,

$$
R_k^\top(\lambda a_k - g^\ast) = R_k^\top(a_k - g) \quad \forall k
  \quad\Longleftrightarrow\quad (\lambda - 1)\,a_k = g^\ast - g \quad \forall k. \tag{18}
$$

If $a_k$ varies in time then so does the left-hand side of (18), leaving only $\lambda = 1$ and
$g^\ast = g$ — **when the acceleration varies, the scale is observable.** But if
$a_k \equiv c$ is constant, (18) becomes a single equation in the single unknown $\lambda$, and

$$
g^\ast = g + (\lambda - 1)\,c \tag{19}
$$

holds for every $\lambda$. Adding the condition that the gravity **magnitude** is known,
$\lVert g^\ast\rVert = \lVert g\rVert$, gives

$$
\lVert g + (\lambda-1)c\rVert^2 = \lVert g\rVert^2
  \;\Longleftrightarrow\;
  (\lambda-1)\Big[(\lambda-1)\lVert c\rVert^2 + 2\,g^\top c\Big] = 0, \tag{20}
$$

the two roots of (10). **If the gravity direction is also known**, $g^\ast = g$ is forced and (19)
gives $(\lambda-1)c = 0$, so $\lambda = 1$ alone. The ambiguity shows up in practice precisely
because monocular VIO initialization estimates the scale and the gravity direction (roll and
pitch) **jointly**.

**In numbers.** At $c = (0.5, -0.3, 1.2)$ and $g = (0,0,-9.81)$ we have $g^\top c = -11.772$ and
$\lVert c\rVert^2 = 1.78$, so

$$
\lambda^\ast = 1 + \frac{2\cdot11.772}{1.78} = \frac{6331}{445} = 14.2269662921\ldots,
$$

with $g^\ast = (6.613483,\ -3.968090,\ 6.062360)$ and $\lVert g^\ast\rVert = 9.81$. A solution
whose scale is wrong by a factor of 14 reproduces the IMU measurements and the bearings
**perfectly, at the $10^{-15}$ level**. This is why initialization must not be attempted over a
constant-acceleration interval, and why real systems wait for "enough variation in acceleration".

**Where the assumption breaks**: (18) treated the accelerometer bias as known. If $b^a$ is also
unknown there is one more degree of freedom and degeneracies can appear even without constant
acceleration — Martinelli's closed-form solution treats exactly this coupling (scale, speed,
attitude and bias), and that paper's list of degenerate conditions is broader than (18). Equation
(18) also assumes gravity is spatially constant, which is reasonable at indoor scale.

## Proof sketch

### R1 — the preintegration identity

**Hypotheses** H1: the discrete kinematics is exactly (2) and (3). H2: $b^g$ and $b^a$ are
constant on the interval $[i,j)$. H3: $g$ is constant.
**Conclusion** C: $\Delta R_{ij}, \Delta v_{ij}, \Delta p_{ij}$ as defined by (4)-(6) equal (7),
and therefore do not depend on $\{R_i, v_i, p_i\}$.

**Strategy**: telescoping sums plus the arithmetic of the gravity terms. The manifold structure is
used only for the rotation.

1. **Rotation.** Multiplying the first equation of H1 over $k = i,\dots,j-1$ gives
   $R_j = R_i\prod\exp(\psi_k)$, and multiplying on the left by $R_i^\top$ gives (7a). The
   intermediate rotations are $R_k = R_i\Delta R_{ik}$, which is the only tool that cancels $R_i$
   in the later steps.
2. **Velocity.** Sum the second equation of H1. Because $g$ is constant (H3) the sum
   $\sum g\Delta t$ collapses to $g\Delta t_{ij}$, and substituting step 1 into the rest pulls
   $R_i$ out in front. Definition (5) is the result.
3. **The gravity bookkeeping of the position.** Sum the third equation of H1 and substitute the
   result of step 2 into (I). The crux is the arithmetic identity
   $\sum_{m=0}^{n-1} m + \tfrac n2 = \tfrac{n^2}{2}$, which gives (7b). That one line answers
   "why does definition (6) contain $\tfrac12 g\Delta t_{ij}^2$".
4. **Conclusion.** What collected on the left-hand side in steps 2 and 3 is exactly definitions
   (5) and (6), and the right-hand side is a function of $\psi_k$ and $\alpha_k$ alone (by H2 the
   bias is constant, so $\alpha_k$ is determined by the measurements). C.
5. **Why this is useful.** Even as the keyframe states $\{R_i,v_i,p_i,R_j,v_j,p_j\}$ move during
   optimization, the right-hand side of (7) is unchanged, so writing the IMU factor's residual as
   "preintegrated measurement versus the left-hand side of (4)-(6)" means only the Jacobians need
   recomputing. Avoiding re-integration is the entire cost argument (the same structure as the
   linearization in R2 of `c5-factor-graphs-map`).

**Delete a hypothesis**: replacing H1 by a midpoint rule makes the arithmetic of step 3 fail to
produce $\tfrac{n^2}{2}$, so definition (6) no longer equals (7) (problem P1). Dropping H2 — a
bias that varies within the interval — makes $\alpha_k$ an unknown time series, so the
preintegrated quantities are no longer functions of a finite-dimensional parameter; practice keeps
intervals short so that H2 holds approximately and inserts bias random-walk factors between
intervals. Dropping H3 means $\sum g_k\Delta t$ does not collapse (this matters at orbital scale).

(Omitted: the local truncation error analysis between the continuous model and (2). Barfoot SER
ch.9 and Forster et al. §IV.)

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★★, R1)** (a) Prove the arithmetic identity (7b). (b) Show that replacing the
position update of (2) by the midpoint rule
$p_{k+1} = p_k + \tfrac12(v_k + v_{k+1})\Delta t$ makes definition (6) differ from the third
equation of (7), and express the difference in terms of $n$, $\Delta t$ and $g$. (c) Find the
**corrected definition** of $\Delta p$ that holds under the midpoint rule.
*Strategy and key inequality*: (a) is the single line $\sum_{m=0}^{n-1}m = n(n-1)/2$. For (b),
first notice the trap that the midpoint rule combined with $v_{k+1} = v_k + a^w_k\Delta t$ is
**identical** to $p_{k+1} = p_k + v_k\Delta t + \tfrac12 a^w_k\Delta t^2$ — a real difference
appears only once the $v$ update is also made midpoint. In that case $\sum(k-i)$ becomes
$\sum(k-i+\tfrac12)$ and the gravity term becomes
$\tfrac12 g\Delta t_{ij}^2 + \tfrac12 g\,n\Delta t^2$. The expansion is hidden.

**P2 (derivation, ★★, R2)** Derive (11) with no missing steps. In particular (a) state in which
direction you used the right-Jacobian relation of the form
$\exp(\psi + J_r^{-1}u) \approx \exp(\psi)\exp(u)$, and (b) justify
$\exp(u)\exp(\psi) = \exp(\psi)\exp(\exp(-\psi)u)$ via $\mathrm{Ad}$. (c) Show that the sign in
(13) comes from $\hat x y = -\hat y x$.
*Solution sketch*: (b) combines two facts,
$\exp(\psi)^{-1}\exp(u)\exp(\psi) = \exp(\mathrm{Ad}_{\exp(-\psi)}u)$ and $\mathrm{Ad}_R = R$ in
$SO(3)$ (the notation table of `c5-manifold-estimation`). The crux of (a) is that the perturbation
has to sit on the **right** for the $\Delta R^\top$ propagation of (11) to appear.

**P3 (numerical, ★, R1)** Compute the preintegrated quantities from the reproduction task's
simulator at the true biases.
*Answer*: $\mathrm{Log}(\Delta R_{ij}) = (0.070574508,\ 0.231862532,\ 0.397082183)$,
$\Delta v_{ij} = (2.166640013,\ 0.085362195,\ 4.498185860)$ and
$\Delta p_{ij} = (0.549102630,\ 0.029297900,\ 1.117894720)$. Tolerance $10^{-9}$.
Check it: compute the left-hand sides of (4)-(6) separately by dense integration and confirm they
agree to within $10^{-12}$ (Part A of the reproduction task). If they do not, your discretization
convention differs from (2).

**P4 (numerical, ★★, R4)** At $c = (0.5,-0.3,1.2)$ and $g = (0,0,-9.81)$, (a) find $\lambda^\ast$
and $g^\ast$, (b) verify $\lVert g^\ast\rVert = \lVert g\rVert$, and (c) confirm numerically that
the two solutions give the same IMU measurements and the same bearings. (d) What is $\lambda^\ast$
when $c$ is parallel to $g$? (e) When $c \perp g$?
*Answer*: (a) $\lambda^\ast = 6331/445 = 14.2269662921$ and
$g^\ast = (6.613483,\ -3.968090,\ 6.062360)$. (b) $\lVert g^\ast\rVert = 9.81$ exactly.
(c) accelerometer difference $< 10^{-14}$, bearing difference $< 10^{-14}$. Tolerance $10^{-8}$.
(d) With $c = \mu g$ we get $g^\top c = \mu\lVert g\rVert^2$ and
$\lVert c\rVert^2 = \mu^2\lVert g\rVert^2$, so $\lambda^\ast = 1 - 2/\mu$ — **the ambiguity
survives even when they are parallel** (at $\mu = 1$ it gives $\lambda^\ast = -1$, excluded since
$\lambda > 0$, but at $\mu = 4$ it gives a valid $\lambda^\ast = 0.5$). (e) If $g^\top c = 0$ then
$\lambda^\ast = 1$, the two roots coincide and **the ambiguity disappears** — constant
acceleration perpendicular to gravity does determine the scale. An answer without the contrast
between (d) and (e) does not pass.

**P5 (implementation, ★★★, R2·R3)** Implement preintegration together with the Jacobians
(11)-(15) and the covariance (9), (16) **in the same loop**.
*Rubric*: (a) Part A passes to within $10^{-12}$; (b) the Jacobian correction error is reported as
scaling with $\lVert\delta b\rVert^2$ to at least four significant figures (the table of Part B);
(c) the covariance agrees with Monte Carlo to within 3% (Part D); (d) the in-loop update order
($p \to v \to R$) is stated in a code comment **with its reason**; (e) the noise units (discrete
versus density) are documented.

**P6 (counterexample, ★★, R4)** Show that "using an IMU always makes monocular scale observable"
is false, and characterize the failure condition in **two different ways**: (a) directly from
(18), and (b) through the null space dimension of the linearized system. (c) Then state what is
and is not observable at rest ($a_k \equiv 0$).
*Property checklist*: (a) must cover every case where $a_k$ is constant, including rest, constant
velocity and constant acceleration. (b) borrows the tools of
`c5-observability-consistency` ahead of time, so a statement at the level of "the null space
dimension grows by one" passes. (c) must note that at $c = 0$ equation (20) becomes
$(\lambda-1)^2\cdot0 = 0$ and therefore admits **every** $\lambda$ — the scale is completely
undetermined and only the gravity direction is observable.

**P7 (paper, ★★, R1·R2·R3)** Read §IV-V and the appendix of `forster2017-preintegration` and
(a) check whether the authors' discretization convention matches (2), stating where it differs if
it does; (b) separate, in two lines each, what the authors do and do not guarantee; (c) find three
pieces of information missing for reproducing the paper's tables and figures.
*Rubric*: (a) passes if it identifies, by equation number, that "the rotation is the same but the
integration rule for position and velocity, and where the noise is injected into the Lie algebra,
may differ". (b) passes if it separates "the identity is exact" from "the noise and bias
propagation are first order". (c) three of: the units and provenance of the IMU noise parameters,
the keyframe selection rule, and the initialization procedure.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read with 3-pass and attack questions 4, 5, 6 and 7 on the third pass.

1. **Forster, Carlone, Dellaert & Scaramuzza, "On-manifold preintegration for real-time
   visual-inertial odometry" (2017, IEEE T-RO)** — role: `seminal`.
   <https://arxiv.org/abs/1512.02363> (§IV-V and the appendix)
   Extra questions: (a) restate why the authors emphasize "on-manifold" in terms of the retraction
   invariance of R1 in `c5-manifold-estimation`; (b) do the appendix's Jacobians agree with
   (11)-(15) here, signs included?
2. **Lupton & Sukkarieh, "Visual-inertial-aided navigation for high-dynamic motion in built
   environments without initial conditions" (2012, IEEE T-RO)** — role: `seminal`.
   <https://doi.org/10.1109/TRO.2011.2170332> (§III-IV)
   Extra questions: (a) which parameterization does this paper's preintegration use for rotation,
   and why is that choice the target of Forster et al.'s criticism? (b) what exactly does "without
   initial conditions" claim?
3. **Martinelli, "Vision and IMU data fusion: closed-form solutions for attitude, speed,
   absolute scale, and bias" (2012, IEEE T-RO)** — role: `standard`.
   <https://doi.org/10.1109/TRO.2011.2160468>
   Extra questions: (a) does the author's list of degenerate motions include "the acceleration is
   constant" from (18), or is it broader? (b) given that a closed-form solution exists, why do real
   systems still use iterative optimization?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) the independent and dependent variables and the baselines — were they tuned fairly?
(6) does the metric match the claim, and are variance and seeds reported? (7) what is missing for
reproduction? (8) if the result were wrong, which assumption would you doubt first?
(9) computational and memory complexity, and real-time feasibility. (10) what would you change to
surpass it in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one laptop CPU core, under a second each for
Parts A-C and under three minutes for the 20000-run Monte Carlo of Part D, under 200 MB. Only
numpy.

**The input data** is produced by the simulator below (fixed seed, deterministic). No external
dataset is needed. The $SO(3)$ utilities are provided too, so **the only things to write are
`preintegrate`, `dense` and `propagate_cov`.**

```python
"""c5-imu-preintegration reproduction task: an IMU simulator and SO(3) utilities."""

import numpy as np

SEED = 20261112
DT, NSTEP = 0.005, 100  # 200 Hz, 0.5 s between keyframes
G = np.array([0.0, 0.0, -9.81])
SIGMA_G, SIGMA_A = 0.004, 0.02  # per-sample discrete noise std: rad/s, m/s^2
B_G = np.array([0.01, -0.02, 0.005])
B_A = np.array([0.05, 0.02, -0.03])
R0_PHI = np.array([0.2, -0.3, 0.5])
V0 = np.array([0.7, -0.2, 0.1])
P0 = np.array([1.0, 2.0, -0.5])


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


def jac_r_so3(phi):
    """The right Jacobian J_r(phi) = J_l(-phi)."""
    t, W = float(np.linalg.norm(phi)), skew(phi)
    if t < 1e-10:
        return np.eye(3) - 0.5 * W + W @ W / 6.0
    return np.eye(3) - (1.0 - np.cos(t)) / t**2 * W + (t - np.sin(t)) / t**3 * W @ W


def truth_signals():
    """True body rates and true world-frame accelerations of an analytic trajectory."""
    t = DT * np.arange(NSTEP)
    omega = np.column_stack([0.3 * np.sin(2.0 * t), 0.5 * np.cos(1.5 * t), 0.8 + 0.0 * t])
    acc_w = np.column_stack([1.5 * np.cos(t), -1.0 * np.sin(1.2 * t), 0.4 * np.sin(0.7 * t)])
    return omega, acc_w


def imu_readings(omega, acc_w, noise_rng=None):
    """Build the IMU readings from the true signals (eq. (1); attitude advances by (2))."""
    R, wm, am = exp_so3(R0_PHI), [], []
    for k in range(NSTEP):
        w = omega[k] + B_G
        a = R.T @ (acc_w[k] - G) + B_A
        if noise_rng is not None:
            w = w + noise_rng.normal(scale=SIGMA_G, size=3)
            a = a + noise_rng.normal(scale=SIGMA_A, size=3)
        wm.append(w)
        am.append(a)
        R = R @ exp_so3(omega[k] * DT)
    return np.array(wm), np.array(am)
```

**What to do.** (a) `preintegrate(wm, am, bg, ba)` — the three quantities of (7) and the five
Jacobians of (11)-(15), in one loop. (b) `dense(wm, am, bg, ba, R0, v0, p0)` — integrate (2) and
(3) directly to get $(R_j, v_j, p_j)$. (c) `propagate_cov(wm, am, bg, ba)` — the $9\times9$
covariance of (9) and (16).

**Part A — the preintegration identity.** Check that the quantities reconstructed from
`preintegrate`, namely $R_i\Delta R$, $v_i + g\Delta t_{ij} + R_i\Delta v$ and
$p_i + v_i\Delta t_{ij} + \tfrac12 g\Delta t_{ij}^2 + R_i\Delta p$, match the output of `dense`
(noise free, at the true biases).

**Part B — the first-order accuracy of the bias correction.** For
$\lVert\delta b^g\rVert = \lVert\delta b^a\rVert \in \{10^{-4}, 10^{-3}, 10^{-2}, 10^{-1}\}$,
compare the correction of (8) against **re-integration** at $\bar b + \delta b$. Draw the
directions with `np.random.default_rng(7)` and normalize them.

**Part C — the scale and gravity ambiguity.** Compute $\lambda^\ast$ from (10) and $g^\ast$ from
(19), then check on a constant-acceleration trajectory with $c = (0.5,-0.3,1.2)$ that the two
solutions give the same accelerometer readings and the same bearings. Use the landmarks
$(4,1,2)$, $(-2,3,0.5)$ and $(1,-5,3)$, scaled by $\lambda^\ast$.

**Part D — the covariance.** Compare the analytic covariance from `propagate_cov` against a Monte
Carlo covariance obtained by drawing noise 20000 times and re-running the preintegration (seed
`SEED`).

**Acceptance criteria — all four conditions must hold.**

1. **Part A** — the $\max\lvert\cdot\rvert$ error is $< 10^{-12}$ for $R_j$, $v_j$ and $p_j$ alike
   (the reference implementation gives $1.0\times10^{-15}$, $1.4\times10^{-15}$ and
   $6.7\times10^{-16}$). **This is an algebraic identity, not a numerical approximation**, so it
   must hold to machine precision; agreement only at the $10^{-6}$ level means your
   discretization convention differs from (2). The preintegrated quantities themselves must also
   match the answer to P3 within $10^{-9}$.
2. **Part B** — reproduce the table below (each value within 1% relative error) and show that
   **error$/\lVert\delta b\rVert^2$ is the same across the four rows**.

   | $\lVert\delta b\rVert$ | $\Delta R$ error (rad) | $\Delta v$ error (m/s) | $\Delta p$ error (m) |
   |---|---|---|---|
   | $10^{-4}$ | $9.401\times10^{-11}$ | $1.642\times10^{-9}$ | $2.403\times10^{-10}$ |
   | $10^{-3}$ | $9.401\times10^{-9}$ | $1.642\times10^{-7}$ | $2.403\times10^{-8}$ |
   | $10^{-2}$ | $9.401\times10^{-7}$ | $1.642\times10^{-5}$ | $2.403\times10^{-6}$ |
   | $10^{-1}$ | $9.402\times10^{-5}$ | $1.645\times10^{-3}$ | $2.406\times10^{-4}$ |

   The quadratic constants are $0.00940$ for $\Delta R$, $0.1642$ for $\Delta v$ and $0.02403$ for
   $\Delta p$.
3. **Part C** — $\lambda^\ast = 14.2269662921$ ($= 6331/445$, tolerance $10^{-9}$),
   $g^\ast = (6.613483,\ -3.968090,\ 6.062360)$ ($10^{-6}$),
   $\lVert g^\ast\rVert = 9.81$ ($10^{-9}$), and both the **accelerometer difference** and the
   **bearing difference** between the two solutions are $< 10^{-14}$ (reference
   $3.6\times10^{-15}$ and $3.3\times10^{-16}$).
4. **Part D** — the analytic standard deviations match the table below (to $10^{-8}$) and agree
   with the 20000-run Monte Carlo to within 3% on the diagonal and 5% over the whole $9\times9$
   normalized by $\sigma_i\sigma_j$ (reference 1.07% and 2.13%).

   | Block | analytic standard deviation |
   |---|---|
   | $\delta\phi$ | $(2.000, 2.000, 2.000)\times10^{-4}$ |
   | $\delta v$ | $(1.12614, 1.152626, 1.029786)\times10^{-3}$ |
   | $\delta p$ | $(3.05226, 3.08985, 2.92659)\times10^{-4}$ |

   Report alongside it that $\delta\phi$ equals $\sigma_g\Delta t\sqrt n = 2\times10^{-4}$
   **exactly** while $\delta v$ is 12.6% larger than $\sigma_a\Delta t\sqrt n = 10^{-3}$ — the
   difference being the rotation-velocity coupling term of $A_k$.

**Baselines**: (a) `dense` is itself the baseline for Part A. (b) The baseline for Part B is
**re-integrating every time**, which in the reference implementation costs $n$ times what the
correction costs ($n = 100$). (c) The baseline for Part D is the Monte Carlo. Optional: shrink
$\Delta t$ from $0.005$ to $0.0025$ to $0.00125$ and contrast that the Part A error **does not
change** (the identity is independent of $\Delta t$) while the error against the continuous
trajectory does shrink — this confirms R5.

**Numbers to report**: every value of the four criteria, the three quadratic constants of Part B,
and the ratio of the $\delta\phi$ analytic value of Part D to $\sigma_g\Delta t\sqrt n$.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The Part A error is on the order of $10^{-3}$ | the $\tfrac12 g\Delta t_{ij}^2$ was omitted from the definition of $\Delta p$ | see whether the error is a multiple of $\tfrac12\cdot9.81\cdot0.25 = 1.23$ m |
| The Part A error grows with $\Delta t_{ij}$ | mismatched integration rules — `dense` rectangular and `preintegrate` midpoint, or vice versa | compare the $v$ and $p$ update order of the two functions side by side |
| Only $v$ is wrong in Part A | $\Delta R_{i,k+1}$ was used instead of $\Delta R_{ik}$ in $\Delta v$ | reduce to $n = 1$ and check by hand |
| The Part B error is **linear** in $\lVert\delta b\rVert$ | the Jacobian recursion update order is wrong ($R$ updated first) | check that the loop goes $p\to v\to R$ and that (14) and (15) use the **pre-update** $J^v$ |
| Only the $\Delta R$ error of Part B is linear | (11) used $\Delta R_{k,k+1}$ instead of $\Delta R_{k,k+1}^\top$ | set $\delta b^a = 0$ and isolate $\Delta R$ |
| Part D is off by a factor of $\Delta t$ | the noise was entered as a density | compare the $\delta\phi$ standard deviation against $\sigma_g\Delta t\sqrt n$ |
| Only $\delta p$ is wrong in Part D | the $\tfrac12\Delta R\Delta t^2$ term of $B_k$ is missing | turn on $\sigma_a$ only (set $\sigma_g=0$) and check that the $\delta p/\delta v$ ratio is $\approx\Delta t_{ij}/3$ |
| The Part C bearings differ | the landmarks were not scaled by $\lambda^\ast$ | first confirm the difference is zero at $\lambda = 1$ |

## Open problems

- **(Open problem) The conflict between a time-varying bias and the group structure** — (7) relies
  on H2, that the bias is constant within the interval, and putting the bias into the state makes
  the dynamics no longer group-affine (the hypothesis of R3 in `c5-manifold-estimation`). Current
  approaches keep the interval short and insert random-walk factors, or look for a larger group
  that contains the bias (the same kind of move that
  [contact-aided InEKF](https://doi.org/10.1177/0278364919894385) makes for contact state). What
  is missing: a group structure that **preserves log-linearity** for a state containing the bias,
  or a proof that none exists.
- **(Open problem) Deciding online whether initialization is informative enough** — R4 is an
  **exact** statement that the scale takes two values over a constant-acceleration interval, but
  what is actually needed is a quantitative verdict on "how well do the intervals collected so far
  determine the scale". Current approaches are heuristics (a threshold on acceleration variance,
  the condition-number check of [VINS-Mono](https://arxiv.org/abs/1708.03852) §V) and the
  [list of degenerate conditions of the closed-form
  solution](https://doi.org/10.1109/TRO.2011.2160468). What is missing: a rule that computes a
  **certifiable lower bound** on the scale estimation error (of Cramér-Rao type) online and uses
  it to decide that initialization has succeeded.
- **(Open problem) The trustworthiness of the preintegration covariance over long intervals** —
  (16) is a first-order expansion and treats $\Sigma_\eta$ as white and constant. As the interval
  lengthens or the motion becomes more vibratory it errs on the underestimating side, with no bound
  on that bias. Current approach: limit the interval length as an engineering choice and check
  $\chi^2$ afterwards ([Forster et al.](https://arxiv.org/abs/1512.02363) appendix, Barfoot SER
  ch.9). What is missing: an explicit bound from interval length and motion intensity to the
  covariance bias, or a cheap way to include the second-order terms.

## Concept check

Run `rc quiz c5-imu-preintegration`. The quiz is for **concept checking only**; the real work is
the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: why $-v_i\Delta t_{ij} - \tfrac12 g\Delta t_{ij}^2$ is subtracted in the
definition of $\Delta p_{ij}$; whether the preintegration identity is a first-order approximation
of the continuous kinematics; how the error of the first-order bias correction grows; what happens
to monocular scale over a constant-acceleration interval; and the standard deviation of the
rotation error of an $n$-sample preintegration.

## How to study this stage

1. **Check the signs of the measurement model by hand first (30 min)** — substitute rest
   ($a = 0$, $R = I$) into the second equation of (1) and confirm the accelerometer reports
   $(0,0,+9.81)$. Get this sign wrong and everything afterwards is wrong.
2. **Make (7b) work out on paper (45 min)** — set $n = 3$, expand the position sum by hand, and
   watch the gravity term land exactly on $\tfrac12 g(3\Delta t)^2$. That one line is all of R1,
   and P1(b) shows the condition under which it breaks.
3. **Do the Jacobian recursion by hand for $n=2$ (60 min)** — run (11)-(15) for two steps by hand
   and see directly what breaks when the update order is changed. Compare against the appendix of
   Forster et al., signs included.
4. **Implement Parts A and B first (90 min)** — keep fixing until Part A agrees to $10^{-15}$ (if
   it does not, the problem is the discretization convention), then confirm the quadratic scaling
   of Part B's table to four significant figures. **A wrong Jacobian makes Part B come out
   linear** — it is the most sensitive test available.
5. **Do Part C with a calculator first (30 min)** — put $\lambda^\ast$ into (10) by hand to get
   14.23, then confirm with code that the measurements really are the same. Seeing a 14-fold scale
   error reproduce the measurements perfectly is what makes "initialization" click as a separate
   problem.
6. **Part D (90 min)** — validate the covariance by Monte Carlo. Check first that $\delta\phi$
   matches $\sigma_g\Delta t\sqrt n$ exactly, then confirm that the 12.6% excess in $\delta v$ comes
   from the coupling term by setting $\sigma_g = 0$.
7. **Read the papers with equation numbers in hand (150 min)** — compare the appendix of Forster
   et al. line by line against (11)-(16) here (signs included), find the point where the idea of
   "preintegration" first appears in Lupton & Sukkarieh, and compare Martinelli's list of
   degenerate conditions against (18). Write the one-page note per paper **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the three open problems and write a
   paragraph. The initialization verdict is easiest, since the $\lambda^\ast$ of the reproduction
   task is its motivation.

**Passing bar**: you can derive (7) and (7b) from a blank page, you can derive (11), you have code
that satisfies all four conditions of the reproduction task, and you have notes on all three
papers.
