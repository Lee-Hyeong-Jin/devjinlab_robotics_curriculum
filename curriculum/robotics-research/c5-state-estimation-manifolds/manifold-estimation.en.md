---
id: c5-manifold-estimation
lang: en
title: Estimation on manifolds and invariant filtering
summary: >-
  Set estimation up properly when the state lives on a Lie group. Prove that Gauss-Newton lifted
  to the tangent space by a retraction is independent of the retraction at first order, and derive
  how left and right uncertainty representations transform by Ad. Derive, with no missing steps,
  that on a group-affine system the invariant error obeys dynamics that do not depend on the
  state, then compare the consistency (NEES) of a standard EKF and an invariant EKF on SE(3) over
  a thousand Monte Carlo runs.
objectives:
  - Lift a least-squares problem on a Lie group to the tangent space and write one step of on-manifold Gauss-Newton.
  - Prove from the definition of a retraction that the first-order model and the critical points do not depend on the retraction.
  - Derive the Ad transformation between left and right uncertainty representations and compute the amplification numerically.
  - Derive the autonomous error dynamics g_u(eta) = f_u(eta) - eta f_u(I) under the group-affine condition.
  - Explain why the log-linear property holds for large errors and where its scope ends (the update step).
  - Judge filter consistency with NEES and show numerically that a standard EKF is overconfident at large errors.
tags: [state-estimation, lie-groups, invariant-ekf, retraction, consistency, nees, research]
---

# Estimation on manifolds and invariant filtering

## Setup and notation

The notation of `c5-factor-graphs-map` and `c5-sparsity-isam` carries over, together with the
$\exp$, $\log$ and $SE(3)$ conventions of `c1-so3-se3-exponential`. Those two lessons placed the
variables in $\mathbb{R}^d$ coordinates. **This lesson corrects that.**

| Symbol | Meaning |
|---|---|
| $G$, $\mathfrak{g}$ | a matrix Lie group and its Lie algebra. The running example is $G = SE(3)$ with $\dim\mathfrak{g} = 6$ |
| $\xi = (\phi, \rho) \in \mathbb{R}^6$ | exponential coordinates of $SE(3)$, with $\xi^\wedge = \begin{bmatrix}\hat\phi & \rho\\ 0 & 0\end{bmatrix}$ — rotation **first** |
| $X = (R, p) \in SE(3)$ | $\begin{bmatrix}R & p\\ 0 & 1\end{bmatrix}$ |
| $\mathrm{Ad}_X$ | the adjoint: $X\exp(\xi^\wedge)X^{-1} = \exp\big((\mathrm{Ad}_X\xi)^\wedge\big)$, $\mathrm{Ad}_X = \begin{bmatrix}R & 0\\ \hat p R & R\end{bmatrix}$ |
| $J_l(\phi)$, $J_r(\phi)$ | the left and right Jacobians of $SO(3)$: $J_r(\phi) = J_l(-\phi)$, $J_l(\phi) = \exp(\hat\phi)J_r(\phi)$ |
| $X \oplus \tau$, $Y \ominus X$ | $X\exp(\tau^\wedge)$ and $\log(X^{-1}Y)$ — the **right** convention (Solà et al.) |
| $\mathcal{R}_X : T_XG \to G$ | a **retraction**: $\mathcal{R}_X(0) = X$ and $D\mathcal{R}_X(0) = \mathrm{id}_{T_XG}$ |
| $\eta_L = X^{-1}\hat X$ | the **left-invariant error** (body frame), $\eta_L = \exp(\xi_L^\wedge)$ |
| $\eta_R = \hat X X^{-1}$ | the **right-invariant error** (world frame), $\eta_R = \exp(\xi_R^\wedge)$ |
| $\mathrm{NEES}$ | $\xi^\top \Sigma^{-1}\xi$. A consistent filter has $\mathbb{E}[\mathrm{NEES}] = \dim\mathfrak{g}$ |

**A warning about conventions.** "Error" and "covariance" mean nothing until two things are
stated: (1) left or right, and (2) relative to the truth or to the estimate. This lesson uses only
$\eta_L = X^{-1}\hat X$ and $\eta_R = \hat X X^{-1}$, and a covariance is always the covariance of
that $\xi$. This convention is the first thing to check when reading a paper, and R2 shows that
the transformation between the two is **not** the identity.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (on-manifold Gauss-Newton and retraction invariance) [D3]** — lifting
  $\min_{X\in G} F(X)$ with $F(X) = \tfrac12\sum_k\lVert r_k(X)\rVert^2_{\Sigma_k}$ to the tangent
  space at the current estimate $\hat X$ as $\tilde F(\tau) = F(\mathcal{R}_{\hat X}(\tau))$ and
  applying Euclidean Gauss-Newton gives
  $$
  \Big(\textstyle\sum_k J_k^\top\Sigma_k^{-1}J_k\Big)\,\tau^\ast = -\sum_k J_k^\top\Sigma_k^{-1}r_k(\hat X),
    \qquad J_k = \frac{\partial\, r_k(\mathcal{R}_{\hat X}(\tau))}{\partial \tau}\bigg|_{\tau=0}, \tag{1}
  $$
  with the update $\hat X \leftarrow \mathcal{R}_{\hat X}(\tau^\ast)$. **The $J_k$ and the critical
  points do not depend on the choice of retraction** — exponential, Cayley or quaternion
  normalization all agree at first order. The second-order terms do differ, so Newton's method and
  the convergence constants are affected.
- **R2 (left and right uncertainty and the Ad transformation) [D2]** — writing the same error in
  the two conventions,
  $$
  \xi_R = \mathrm{Ad}_{\hat X}\,\xi_L \quad\Longrightarrow\quad
    \Sigma_R = \mathrm{Ad}_{\hat X}\,\Sigma_L\,\mathrm{Ad}_{\hat X}^\top. \tag{2}
  $$
  In $SE(3)$ the $\hat p R$ block of $\mathrm{Ad}$ **amplifies rotational uncertainty into
  translation**: at $\lVert p\rVert = 10\,\mathrm{m}$ with
  $\sigma_\phi = \sigma_\rho = 0.01$, the world-frame position standard deviations become
  $(0.01,\ 0.10049876,\ 0.10049876)$ — ten times larger. A covariance reported without its
  convention can be wrong by a factor of ten.
- **R3 (group-affine systems and autonomous invariant-error dynamics) [D3]** — if
  $\dot X = f_u(X)$ is **group-affine**,
  $$
  f_u(XY) = X f_u(Y) + f_u(X)\,Y - X f_u(I)\,Y \qquad \forall X, Y \in G \tag{3}
  $$
  then the right-invariant error $\eta_R = \hat X X^{-1}$ satisfies a differential equation that
  **does not depend on $X$**:
  $$
  \dot\eta_R = g_u(\eta_R), \qquad g_u(\eta) = f_u(\eta) - \eta\, f_u(I). \tag{4}
  $$
  Example: body-frame odometry $f_u(X) = X\hat u$ is group-affine with $g_u \equiv 0$ — the
  **right-invariant error is exactly constant**.
- **R3' (the log-linear property) [D3]** — in addition to (4), if $\xi$ satisfies the linear ODE
  $\dot\xi = A_u \xi$ (with $A_u$ the first-order expansion of $g_u$ at the identity), then
  $\exp(\xi(t)^\wedge)$ is the **exact** solution of (4). The linearization holds without any
  small-error assumption, so covariance propagation is exact **for arbitrarily large errors**.
  That is the whole of the invariant EKF.
- **R4 (the overconfidence of a standard EKF versus the consistency of an invariant EKF) [D2]** —
  for the discrete $SE(3)$ model $X_{k+1} = X_k\Delta_k\exp(\nu_k^\wedge)$ the propagation
  Jacobians of the two filters are
  $$
  F_{\mathrm{InEKF}} = \mathrm{Ad}_{\Delta_k^{-1}} \;\;(\text{estimate-free}), \qquad
  F_{\mathrm{EKF}} = \begin{bmatrix} I & 0 \\ -\widehat{\hat R p_\Delta} & I\end{bmatrix}
    \;\;(\text{depends on } \hat R). \tag{5}
  $$
  As measured in the reproduction task (propagation only, 2000 Monte Carlo runs): at an initial
  error of $\sigma_0 = 0.5$ rad/m the EKF's $\mathrm{NEES}/\dim$ climbs to 1.95 while the
  invariant EKF stays **flat** at 1.00-1.05. With the update included (1000 runs) the
  $\mathrm{ANEES}/\dim$ is 6.858 for the EKF against 3.234 for the invariant EKF.
- **R5 (a covariance is relative to its convention) [D1]** — the reparameterization
  non-invariance of R5 in `c5-factor-graphs-map` appears on a manifold as the choice of
  **retraction and of the left/right convention**. Comparing covariances requires stating the
  convention; copying numbers from a paper without it is wrong by exactly (2).

## Derivation

### R2 — left and right uncertainty transform by Ad

Write the same truth $X$ and estimate $\hat X$ in both ways:

$$
X = \hat X \exp(-\xi_L^\wedge) \;\; (\text{left}, \; \eta_L = X^{-1}\hat X = \exp(\xi_L^\wedge)),
\qquad
X = \exp(-\xi_R^\wedge)\hat X \;\; (\text{right}, \; \eta_R = \hat X X^{-1}). \tag{6}
$$

Equating the two gives $\exp(-\xi_R^\wedge)\hat X = \hat X\exp(-\xi_L^\wedge)$, that is

$$
\exp(-\xi_R^\wedge) = \hat X \exp(-\xi_L^\wedge)\hat X^{-1}
  = \exp\!\big(-(\mathrm{Ad}_{\hat X}\xi_L)^\wedge\big), \tag{7}
$$

where the second equality is the definition of $\mathrm{Ad}$ ($X\exp(\xi^\wedge)X^{-1} =
\exp((\mathrm{Ad}_X\xi)^\wedge)$). Since $\exp$ is injective near the identity,
$\xi_R = \mathrm{Ad}_{\hat X}\xi_L$, and the covariance law for a linear map gives (2).

**In numbers.** Take $\hat X = (R_z(\pi/2),\ (10,0,0)^\top)$ and $\Sigma_L = 10^{-4} I_6$. Since
$\mathrm{Ad}_{\hat X} = \begin{bmatrix}R & 0\\ \hat pR & R\end{bmatrix}$, the translation block of
(2) is

$$
(\Sigma_R)_{\rho\rho} = \hat p R\,(\sigma_\phi^2 I)\,R^\top \hat p^\top + R(\sigma_\rho^2 I)R^\top
  = -\sigma_\phi^2\,\hat p^2 + \sigma_\rho^2 I, \tag{8}
$$

using $\hat p^\top = -\hat p$. At $p = (10,0,0)^\top$ we have $-\hat p^2 =
\mathrm{diag}(0, 100, 100)$, so the standard deviations are
$(\sigma_\rho,\ \sqrt{100\sigma_\phi^2 + \sigma_\rho^2},\ \cdot) =
(0.01,\ 0.10049876,\ 0.10049876)$. The lever arm $\lVert p\rVert$ amplifies rotational
uncertainty linearly — the same phenomenon as a gyro error turning into a position error far away.

**Where the assumption breaks**: (7) uses the local injectivity of $\exp$. Once
$\lVert\phi\rVert$ grows to $\pi$, $\xi_L$ itself is not unique (the logarithm singularity of
$SO(3)$, R3 of `c1-so3-se3-exponential`) and the "covariance" in (2) loses its meaning. Also (2)
uses $\mathrm{Ad}$ evaluated at $\hat X$, so **the coordinate representation of the same
uncertainty changes at every step** as $\hat X$ is updated — a common source of bugs when
covariances are logged and compared.

### R3 — on a group-affine system the invariant error forgets the state

Derive (4). Set $\eta := \hat X X^{-1}$ and differentiate. Both $\hat X$ and $X$ follow the same
dynamics, $\dot{\hat X} = f_u(\hat X)$ and $\dot X = f_u(X)$ (the estimate is propagated with the
same model). Using $\frac{d}{dt}X^{-1} = -X^{-1}\dot X X^{-1}$,

$$
\dot\eta = \dot{\hat X}X^{-1} + \hat X\,\frac{d}{dt}\big(X^{-1}\big)
  = f_u(\hat X)X^{-1} - \hat X X^{-1} f_u(X) X^{-1}
  = f_u(\hat X)X^{-1} - \eta\, f_u(X)X^{-1}. \tag{9}
$$

Now substitute $\hat X = \eta X$ into the first term and apply (3) with $(X, Y) \to (\eta, X)$:

$$
f_u(\eta X) = \eta f_u(X) + f_u(\eta)X - \eta f_u(I) X
  \quad\Longrightarrow\quad
  f_u(\hat X)X^{-1} = \eta f_u(X)X^{-1} + f_u(\eta) - \eta f_u(I). \tag{10}
$$

Putting (10) into (9), the term $\eta f_u(X)X^{-1}$ **cancels exactly**:

$$
\dot\eta = \eta f_u(X)X^{-1} + f_u(\eta) - \eta f_u(I) - \eta f_u(X)X^{-1}
  = f_u(\eta) - \eta f_u(I). \tag{11}
$$

$X$ is gone. The right-hand side of (11) is a function of $\eta$ and of the (known) input $u$
alone — this is (4). What matters is that there is **not one line of approximation**: no
linearization and no small-error assumption were used.

**Example 1 (body-frame odometry).** $f_u(X) = X\hat u$ with constant $\hat u \in \mathfrak{g}$.
Check (3): $f_u(XY) = XY\hat u$ while the right-hand side is
$XY\hat u + X\hat uY - X\hat u Y = XY\hat u$. And $f_u(I) = \hat u$, so (4) gives
$g_u(\eta) = \eta\hat u - \eta\hat u = 0$ — **the right-invariant error is constant.**
Geometrically this is obvious: if $\hat X$ and $X$ are multiplied on the right by the same
quantity, $\hat X X^{-1}$ does not change.

**Example 2 (left-invariant error).** For the same dynamics,
$\dot\eta_L = -X^{-1}\dot X X^{-1}\hat X + X^{-1}\dot{\hat X} = -\hat u\,\eta_L + \eta_L\hat u
= [\eta_L, \hat u]$, again independent of $X$. Its first-order expansion is
$\dot\xi_L = -\mathrm{ad}_{\hat u}\xi_L$ and its discrete form is
$\xi_{L,k+1} = \mathrm{Ad}_{\Delta_k^{-1}}\xi_{L,k} - \nu_k$, which is the
$F_{\mathrm{InEKF}}$ of (5).

**Which error should be chosen.** Both are autonomous as far as propagation goes; the
**measurement** decides. If the measurement has the form $y = X^{-1}d + n$ (a known point $d$ seen
in the body frame), substituting $X^{-1} = \eta_L\hat X^{-1}$ gives $y = \eta_L\,\hat y + n$ with
$\hat y := \hat X^{-1}d$, so the innovation is a function of $\eta_L$ alone — use the
left-invariant error. If the measurement has the form $y = Xd + n$ (world frame), the same
argument with $\hat X y$ as the innovation calls for the right-invariant error. **If the
invariance is not matched to the measurement, state dependence comes straight back and the
advantage of the invariant EKF disappears.**

### R4 — the Jacobians of the two filters, and how consistency is judged

Fix the discrete model. With $\Delta_k = \exp((u_k\Delta t)^\wedge) = (R_\Delta, p_\Delta)$,

$$
X_{k+1} = X_k\,\Delta_k\,\exp(\nu_k^\wedge), \qquad \nu_k\sim\mathcal{N}(0, Q),
\qquad \hat X_{k+1} = \hat X_k \Delta_k. \tag{12}
$$

**Invariant EKF (left-invariant error).** $\eta_{L,k+1} = X_{k+1}^{-1}\hat X_{k+1}
= \exp(-\nu_k^\wedge)\Delta_k^{-1}\,\eta_{L,k}\,\Delta_k
= \exp(-\nu_k^\wedge)\exp\big((\mathrm{Ad}_{\Delta_k^{-1}}\xi_{L,k})^\wedge\big)$. Taking first
order **in $\nu$ only**,

$$
\xi_{L,k+1} = \mathrm{Ad}_{\Delta_k^{-1}}\,\xi_{L,k} - \nu_k + O(\lVert\nu_k\rVert^2),
\qquad P_{k+1} = \mathrm{Ad}_{\Delta_k^{-1}} P_k \mathrm{Ad}_{\Delta_k^{-1}}^\top + Q. \tag{13}
$$

The term in $\xi_{L,k}$ is **not an approximation** ($\mathrm{Ad}$ is the exact conjugation), so
$F$ does not depend on the estimate and covariance propagation does not go wrong when the error is
large.

**Standard EKF.** Take the error to be $e = (\phi, e_p)$ with $\hat R = \exp(\phi^\wedge)R$ and
$e_p = \hat p - p$ (a world-frame rotation error plus a world-frame position error — the most
common choice in VIO implementations). From (12),
$R_{k+1} = R_kR_\Delta\exp(\hat\nu_\phi)$ and
$p_{k+1} = p_k + R_kp_\Delta + R_kR_\Delta\nu_\rho$, so

$$
\exp(\phi_{k+1}^\wedge) = \hat R_{k+1}R_{k+1}^\top
  = \exp(\phi_k^\wedge)\,R_kR_\Delta\exp(-\hat\nu_\phi)R_\Delta^\top R_k^\top
  = \exp(\phi_k^\wedge)\exp\!\big(-(R_kR_\Delta\nu_\phi)^\wedge\big)
$$

$$
\Longrightarrow \quad \phi_{k+1} \approx \phi_k - \hat R_kR_\Delta\,\nu_\phi, \tag{14}
$$

$$
e_{p,k+1} = e_{p,k} + (\hat R_k - R_k)p_\Delta - R_kR_\Delta\nu_\rho
  \approx e_{p,k} - \widehat{(\hat R_kp_\Delta)}\,\phi_k - \hat R_kR_\Delta\nu_\rho. \tag{15}
$$

In (15) we used $\hat R_k - R_k = (\exp(\phi^\wedge) - I)R_k \approx \hat\phi R_k$ and
$\hat\phi\,a = -\hat a\,\phi$ — **this is the only place a first-order approximation enters, and
it is simultaneously the place where $\hat R_k$ enters the Jacobian.** Equations (14) and (15)
give the $F_{\mathrm{EKF}}$ of (5) together with
$G_{\mathrm{EKF}} = -\mathrm{diag}(\hat R_kR_\Delta,\ \hat R_kR_\Delta)$.

**Measurement Jacobians.** For $y = R^\top(p_\ell - p) + n$:
- standard EKF: expanding $y = \hat R^\top\exp(\phi^\wedge)(p_\ell - \hat p + e_p)$ gives
  $H_{\mathrm{EKF}} = \big[-\hat R^\top\widehat{(p_\ell - \hat p)},\;\; \hat R^\top\big]$.
- invariant EKF: from $y = \eta_L\hat y + n$ with $\hat y = \hat X^{-1}\tilde p_\ell$ we get
  $y \approx \hat y - \widehat{\hat y}\,\phi_L + \rho_L$, i.e.
  $H_{\mathrm{InEKF}} = \big[-\widehat{\hat y},\;\; I\big]$. Replacing $\hat y$ by the
  **measurement $y$** makes $H$ independent of the estimate altogether — that is the "invariant"
  update, and it is the form the reproduction task uses.

**Judging consistency.** For an error $\xi$ with covariance $\Sigma$, define
$\mathrm{NEES} = \xi^\top\Sigma^{-1}\xi$. If the error really is $\mathcal{N}(0,\Sigma)$ then
$\mathbb{E}[\mathrm{NEES}] = \dim\mathfrak{g}$ (a $\chi^2_{\dim}$ distribution). A Monte Carlo
average $\mathrm{ANEES}/\dim$ above 1 means **overconfident**, below 1 conservative. Each filter's
NEES must be measured in **its own error definition** — $\xi_L = \log(X^{-1}\hat X)$ for the
invariant EKF and $e = (\log(\hat RR^\top),\ \hat p - p)$ for the standard EKF.

**Where the assumption breaks**: the exactness of (13) applies **to propagation only**. The
measurement Jacobian is still a first-order expansion, and using $y$ in place of $\hat y$ brings
the noise $n$ into $H$. So at large initial errors the invariant EKF's NEES is not 1 either — in
the reproduction task the $\mathrm{NEES}/\dim$ at the first observation epoch is 96.9 for the EKF
and 33.3 for the invariant EKF. **The invariant EKF reduces inconsistency; it does not remove
it.** And once the error becomes small the two filters are numerically the same (1.005 against
1.020 at the last epoch in the measurements). That the advantage of invariant filtering is
confined to the large-error regime is something to verify whenever reading these papers.

### R5 — comparing covariances on a manifold

R5 of `c5-factor-graphs-map` said MAP is not reparameterization invariant. On a Lie group that
"parameterization" has two layers: (1) the choice of retraction $\mathcal{R}$ (first order agrees
by R1, but the result of a finite step does not) and (2) the left/right convention (differing by
$\mathrm{Ad}$, by R2). So a report of "$\sigma_\theta = 0.5^\circ$" is not comparable without its
convention. When reporting, state (a) the group, (b) the error definition, (c) left or right, and
(d) the component order (whether $(\phi,\rho)$ or $(\rho,\phi)$). **[D1]**

## Proof sketch

### R1 — the choice of retraction does not change the answer at first order

**Hypotheses** H1: $G$ is a smooth manifold and $F : G \to \mathbb{R}$ is $C^2$.
H2: $\mathcal{R}_X : T_XG \to G$ is a retraction — $\mathcal{R}_X(0) = X$ and
$D\mathcal{R}_X(0) = \mathrm{id}_{T_XG}$.
H3: $\tilde F_{\hat X}(\tau) := F(\mathcal{R}_{\hat X}(\tau))$.
**Conclusions** C1: $\nabla\tilde F_{\hat X}(0) = \nabla F(\hat X)$ (the Riemannian gradient), so
the right-hand side of (1) and the set of critical points do not depend on $\mathcal{R}$.
C2: if $\hat X$ is a critical point then $\nabla^2\tilde F_{\hat X}(0)$ does not depend on
$\mathcal{R}$ either.

**Strategy**: one application of the chain rule, plus the observation that at second order the
"gradient times the retraction's second derivative" term vanishes at a critical point.

1. **First order.** By the chain rule $D\tilde F_{\hat X}(0)[\tau] =
   DF(\hat X)[D\mathcal{R}_{\hat X}(0)\tau] = DF(\hat X)[\tau]$, by H2. Hence C1. The residual
   Jacobians are the same for the same reason,
   $J_k = Dr_k(\hat X)\circ D\mathcal{R}_{\hat X}(0) = Dr_k(\hat X)$, so the left-hand side of (1)
   is also unchanged.
2. **Critical points.** By C1, $\nabla\tilde F_{\hat X}(0) = 0 \iff \nabla F(\hat X) = 0$. The
   critical points of the lifted problem and of the original problem **coincide as sets**.
3. **Second order.** Differentiating twice in $\tau$,
   $$
   D^2\tilde F_{\hat X}(0)[\tau,\tau] = D^2F(\hat X)[\tau,\tau]
     + DF(\hat X)\big[D^2\mathcal{R}_{\hat X}(0)[\tau,\tau]\big].
   $$
   The second term is the only one that depends on $\mathcal{R}$, and **it vanishes when $\hat X$
   is a critical point, since $DF(\hat X) = 0$**. Hence C2.
4. **Convergence.** By 2 and 3 the Hessian near a critical point is the same, so the local
   quadratic convergence of Riemannian Newton and the local linear rate of Gauss-Newton (whose
   constant is set by the residual size) are independent of the retraction
   (`absil2008-manifold-opt` ch.4 and ch.7, the theorems around 4.5.6 and 7.4.11).

**Delete a hypothesis**: dropping $D\mathcal{R}_X(0) = \mathrm{id}$ from H2 breaks step 1 and the
Jacobians are wrong by a factor of $D\mathcal{R}_X(0)$. The accidents that actually happen are
**adding quaternions as 4-vectors without normalizing** and **adding rotation vectors as plain
vectors**. The first has an $\mathcal{R}$ that does not land on the manifold; the second does not
merely fail $D\mathcal{R}(0) = \mathrm{id}$ but disagrees with the group operation outright as
$\theta$ grows (R4 of `c1-so3-se3-exponential`). Both leave you with a filter that "converges" but
whose covariance is wrong.

(Omitted: the existence of retractions and the proof that $\exp$ is one, and global convergence
away from the optimum. `absil2008-manifold-opt` §4.1 and ch.7.)

### R3' — the log-linear property holds even for large errors

**Hypotheses** H1: $f_u$ satisfies the group-affine condition (3). H2: $\eta(t)$ solves (4) with
$\eta(0) = \exp(\xi_0^\wedge)$ — **with no bound on the size of $\xi_0$**. H3: $A_u$ is the
constant matrix defined by the first-order expansion of $g_u$ near the identity,
$g_u(\exp(\xi^\wedge)) = (A_u\xi)^\wedge + O(\lVert\xi\rVert^2)$.
**Conclusion** C: if $\xi(t)$ solves $\dot\xi = A_u\xi$ with $\xi(0) = \xi_0$, then
$\eta(t) = \exp(\xi(t)^\wedge)$ solves (4).

**Strategy**: uniqueness. Show two curves satisfy the same ODE with the same initial condition.

1. **The structure of $g_u$.** Setting $Y = I$ in (3) gives a tautology, but substituting
   $X = \exp(s\xi^\wedge)$ and differentiating in $s$ shows that $g_u$ acts on the Lie algebra
   only through the **exponential of a linear map** (the key lemma of the original paper).
2. **The candidate curve.** Put $\zeta(t) := \exp(\xi(t)^\wedge)$ and differentiate:
   $\dot\zeta = \mathrm{d}\exp_{\xi}[\dot\xi]$, and the structure from step 1 shows this equals
   $g_u(\zeta)$ exactly.
3. **Uniqueness.** $g_u$ is (locally) Lipschitz, so by Picard-Lindelöf the solution of (4) is
   unique. Since $\zeta(0) = \exp(\xi_0^\wedge) = \eta(0)$, we get $\zeta \equiv \eta$. C.
4. **Why "even for large errors".** Steps 2 and 3 **never use** that $\lVert\xi\rVert$ is small.
   In an ordinary EKF, linearization requires a small error because a Taylor expansion is taken in
   the state space; here it is not an expansion but a **change of coordinates**
   ($\eta \mapsto \xi$) that produces linear dynamics.
5. **Scope.** C is a statement about (4), and (4) itself requires H1 (group-affine). For dynamics
   that are not group-affine (parts of an IMU model with the bias in the state, aerodynamic terms)
   $X$ survives in $\dot\eta$ and the theorem does not apply. The measurement update is also
   outside its scope.

**Delete a hypothesis**: without H1 the cancellation in (11) does not happen, $\dot\eta$ depends on
$X$, and the premise "dynamics of the error alone" is gone. The $A_u$ of H3 is **constant** only
in the group-affine case; otherwise it becomes $A_u(t, X)$ and we are back to an ordinary EKF. In
that sense **group-affineness is close to a necessary condition for log-linearity** (see the
converse discussion around Theorems 1-2 of the original paper).

(Omitted: the $\mathrm{d}\exp$ computation of steps 1-2 and the proof that $g_u$ is linear on the
Lie algebra. `barrau2017-invariant-ekf` Theorems 1-2 and their proofs.)

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★, R1)** Write C1 and C2 of R1 with no missing steps, then show that on $SO(3)$ both
$\mathcal{R}_R(\phi) = R\exp(\hat\phi)$ and the Cayley retraction
$\mathcal{R}_R(\phi) = R\,(I - \tfrac12\hat\phi)^{-1}(I + \tfrac12\hat\phi)$ are retractions that
agree at first order but differ at second order.
*Strategy and key inequality*: the retraction conditions reduce to checking
$\mathcal{R}(0) = R$ and $\frac{d}{ds}\mathcal{R}(s\phi)|_{s=0} = R\hat\phi$. Expand Cayley as
$(I-\tfrac12\hat\phi)^{-1} = I + \tfrac12\hat\phi + \tfrac14\hat\phi^2 + \cdots$. The second-order
difference shows up by comparing the $\hat\phi^2$ coefficient against the $\tfrac12$ of $\exp$.
The expansion is hidden.

**P2 (proof, ★★★, R3)** (a) Show that $f_u(X) = X\hat u + \hat w X$ (with constant
$\hat u, \hat w \in \mathfrak{g}$) is group-affine and find $g_u$. (b) Show that
$f_u(X) = X\hat u X$ is **not** group-affine, and point out exactly where $X$ survives in (9).
(c) Discuss in one paragraph how strong a constraint (3) is, in the sense that knowing $f_u(I)$
fully determines the "nonlinear part" of $f_u$.
*Strategy*: (a) expand both sides of (3) and compare; the answer is
$g_u(\eta) = \hat w\eta - \eta\hat w = [\hat w, \eta]$ — include the reading that a world-frame
input survives in the error while a body-frame input cancels. (b) the counterexample
$X = Y = \exp(\epsilon\hat v)$ suffices. (c) passes if it differentiates (3) in $Y$ and notes that
the derivative of $f_u$ is generated by left and right translations. The expansion is hidden.

**P3 (derivation, ★★, R4)** Derive the discrete propagation of the **right-invariant** error
$\eta_R = \hat X X^{-1}$ under (12) and show that $\mathrm{Ad}_{X_k}$ appears in the noise term.
From that, argue that for the combination "body-frame noise plus world-frame measurements" one of
the two choices is always state-dependent.
*Solution sketch*: rearranging
$\eta_{R,k+1} = \hat X_k\Delta\exp(-\nu^\wedge)\Delta^{-1}X_k^{-1}$ into the form
$X_k\exp(\cdot)X_k^{-1}$ gives
$\eta_{R,k}\exp\big(-(\mathrm{Ad}_{X_k}\mathrm{Ad}_\Delta\nu)^\wedge\big)$. The conclusion is
that "invariance is complete only when dynamics, noise **and** measurement all sit on the same
side", and it is excellent to point out that the IMU model on $SE_2(3)$ is a design that makes
that combination line up (treated in `c5-imu-preintegration`).

**P4 (numerical, ★, R2)** For $\hat X = (R_z(\pi/2),\ (10, 0, 0)^\top)$ and
$\Sigma_L = 10^{-4}I_6$, find (a) $\mathrm{Ad}_{\hat X}$, (b) the translation block of $\Sigma_R$
and its standard deviations, (c) the rotation-translation cross block. (d) What happens to (b) if
$\lVert p\rVert$ becomes 100 m?
*Answer*: (a) $\mathrm{Ad} = \begin{bmatrix}R_z(\pi/2) & 0\\ \hat pR_z(\pi/2) & R_z(\pi/2)\end{bmatrix}$.
(b) $(\Sigma_R)_{\rho\rho} = \mathrm{diag}(10^{-4},\ 1.01\times10^{-2},\ 1.01\times10^{-2})$ with
standard deviations $(0.01,\ 0.10049876,\ 0.10049876)$.
(c) $(\Sigma_R)_{\phi\rho} = \sigma_\phi^2 \hat p^\top = -10^{-4}\hat p$, an antisymmetric block
whose nonzero entries are $\pm10^{-3}$. (d) the standard deviations become
$(0.01,\ 1.00005,\ 1.00005)$ — amplification is **linear** in the lever arm. Tolerance $10^{-8}$.
Check it: draw $4\times10^5$ samples from $\Sigma_L$ and compare the sample covariance of
$\log(\hat X\exp(\xi_L^\wedge)\hat X^{-1})$ against (b) — the relative error should be under 1%
(the reference implementation gives 0.24%).

**P5 (numerical, ★★, R3·R4)** Put (13) and (5) into code, run both filters with **propagation
only**, and measure $\mathrm{NEES}/6$ at $\sigma_0 \in \{0.05,\ 0.2,\ 0.5\}$ (Part A of the
reproduction task). (a) Tabulate both filters' values. (b) Point out which step of R3' explains
why the invariant EKF's value is 1 **independently of** $\sigma_0$.
*Answer*: the table of acceptance criterion 1 of the reproduction task is the answer. The
invariant EKF stays at $1.00$-$1.05$ in all three cases while the EKF climbs to $1.95$ at
$\sigma_0 = 0.5$ (near step 120). Tolerances: $[0.95, 1.10]$ for the invariant EKF and a maximum
above $1.8$ for the EKF.
*Grading point for (b)*: step 4 of R3' — linearity comes from a **change of coordinates** rather
than a Taylor expansion, so $F$ is exact however large $\lVert\xi\rVert$ is. "Because Ad is
linear" does not pass; the answer must say that $\mathrm{Ad}$ is the **exact** conjugation.

**P6 (implementation, ★★★, R4)** Implement Part B of the reproduction task — both filters with the
measurement update, and the 1000-run Monte Carlo NEES.
*Rubric*: (a) each filter's NEES is computed in **its own error definition** (mixing them is an
immediate reject); (b) the invariant EKF is run **both** with $H$ built from the measurement $y$
and with $H$ built from $\hat y$, and the difference is reported; (c) the first and last
observation epochs are reported separately; (d) the final RMSE is reported as nearly identical for
both filters, with "consistency $\ne$ accuracy" stated explicitly.

**P7 (counterexample, ★★, R3·R4)** Show that "an invariant EKF is always better than an EKF" is
false. (a) Construct a case where the measurement does not match the invariant structure (for
example body-frame noise with world-frame position measurements) and give numbers for a regime
where the invariant EKF is equal to or worse than the EKF; (b) explain why the two filters become
numerically identical when the error is small.
*Property checklist*: (a) uses the conclusion of P3 — if the invariance of the measurement differs
from that of the noise, either $H$ or $F$ becomes state-dependent. In the reproduction task's
setting, reverting $H$ to $\hat y$ actually makes things worse (the reference implementation's
$\mathrm{ANEES}/6$ rises from $3.23$ to $13.35$, worse even than the EKF's $6.86$). (b) passes if it shows the two Jacobians differ by
$O(\lVert\xi\rVert)$ using $\mathrm{Ad}_{\exp(\xi)} = I + \mathrm{ad}_\xi + O(\xi^2)$.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read with 3-pass and attack questions 4, 5, 6 and 7 on the third pass.

1. **Barrau & Bonnabel, "The invariant extended Kalman filter as a stable observer" (2017,
   IEEE T-AC)** — role: `seminal`. <https://arxiv.org/abs/1410.1465> (§II-III)
   Extra questions: (a) restate the authors' Theorems 1 and 2 as (11) and the statement of R3'
   respectively; (b) the stability claim in the title is stability **of what**, and does it
   guarantee estimation accuracy? (c) what do the authors say, and not say, about the
   nonlinearity of the measurement update?
2. **Solà, Deray & Atchuthan, "A micro Lie theory for state estimation in robotics" (2018,
   arXiv)** — role: `standard`. <https://arxiv.org/abs/1812.01537> (§4-7)
   Extra questions: (a) which of $\eta_L$ and $\eta_R$ does this text's $\oplus/\ominus$
   convention correspond to? (b) check the signs of the $SE(3)$ Jacobian table in the appendix
   against the $F$ of (13).
3. **Absil, Mahony & Sepulchre, "Optimization Algorithms on Matrix Manifolds" (2008)** —
   role: `standard`. <https://doi.org/10.1515/9781400830244> (§4.1 and ch.7)
   Extra questions: (a) if the condition $D\mathcal{R}_X(0) = \mathrm{id}$ is dropped from the
   definition of a retraction, which of the authors' convergence theorems fails first?
   (b) what does the authors' "vector transport" correspond to in an estimation problem (hint: R2)?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) the independent and dependent variables and the baselines — were they tuned fairly?
(6) does the metric match the claim, and are variance and seeds reported? (7) what is missing for
reproduction? (8) if the result were wrong, which assumption would you doubt first?
(9) computational and memory complexity, and real-time feasibility. (10) what would you change to
surpass it in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one laptop CPU core, under 5 minutes for the
2000-run Part A plus the 1000-run Part B (pure numpy, $6\times6$ matrix operations), under 500 MB.

**The input data** is produced by the simulator below (fixed seed). No external dataset is needed.
The Lie group utilities are provided too, so **the only thing to write is the two filters.**

```python
"""c5-manifold-estimation reproduction task: an SE(3) simulator and Lie group utilities."""

import numpy as np

SEED = 20261112
DT, STEPS, OBS_EVERY = 0.05, 200, 10
SIGMA_PHI, SIGMA_RHO, SIGMA_Y = 0.02, 0.01, 0.10
U = np.array([0.1, -0.2, 0.5, 1.0, 0.0, 0.0])  # body twist (omega, v)
LANDMARKS = np.array([[8.0, 0.0, 1.0], [0.0, 8.0, -1.0], [-8.0, 0.0, 2.0], [0.0, -8.0, 0.0]])
Q = np.diag([SIGMA_PHI**2] * 3 + [SIGMA_RHO**2] * 3)
RY = SIGMA_Y**2 * np.eye(3)


def skew(w):
    return np.array([[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]])


def pose(R, p):
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, p
    return T


def inv(T):
    R, p = T[:3, :3], T[:3, 3]
    return pose(R.T, -R.T @ p)


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


def jac_l_so3(phi):
    """The left Jacobian J_l: the translation block of the SE(3) exponential."""
    t, W = float(np.linalg.norm(phi)), skew(phi)
    if t < 1e-10:
        return np.eye(3) + 0.5 * W + W @ W / 6.0
    return np.eye(3) + (1.0 - np.cos(t)) / t**2 * W + (t - np.sin(t)) / t**3 * W @ W


def exp_se3(xi):
    return pose(exp_so3(xi[:3]), jac_l_so3(xi[:3]) @ xi[3:])


def log_se3(T):
    phi = log_so3(T[:3, :3])
    return np.concatenate([phi, np.linalg.solve(jac_l_so3(phi), T[:3, 3])])


def adjoint(T):
    R, p = T[:3, :3], T[:3, 3]
    A = np.zeros((6, 6))
    A[:3, :3], A[3:, :3], A[3:, 3:] = R, skew(p) @ R, R
    return A


def simulate(seed, p0_cov):
    """Return the true trajectory, the initial estimate, the odometry increment and the observations."""
    rng = np.random.default_rng(seed)
    delta = exp_se3(U * DT)
    x = np.eye(4)
    x0_hat = x @ exp_se3(rng.multivariate_normal(np.zeros(6), p0_cov))
    truth, obs = [], {}
    for k in range(STEPS):
        x = x @ delta @ exp_se3(rng.multivariate_normal(np.zeros(6), Q))
        truth.append(x.copy())
        if (k + 1) % OBS_EVERY == 0:
            xi = inv(x)
            obs[k] = [
                xi[:3, :3] @ pl + xi[:3, 3] + rng.normal(scale=SIGMA_Y, size=3) for pl in LANDMARKS
            ]
    return truth, x0_hat, delta, obs
```

**What to do.** Implement the invariant EKF of (13) and the standard EKF of (5), (14) and (15).
Use the `x0_hat` returned by `simulate` as the initial estimate for **both** filters, and set the
initial covariance of both to $P_0 = \sigma_0^2 I_6$ (since $X_0 = I$ this is the same in both
conventions — check why with (2)). Compute each filter's NEES in its own error definition.

**Part A — propagation only.** Propagate 200 steps without using the measurements and record
$\mathrm{NEES}/6$ at steps 0, 40, 80, 120, 160 and 199, for
$\sigma_0 \in \{0.05,\ 0.2,\ 0.5\}$, over 2000 Monte Carlo runs (seeds $5000 + m$). Call
`simulate` exactly as given, so that the random stream is the same even though the observations go
unused.

**Part B — the full filter.** Feed the four landmarks into the update every 10 steps. Use
$\sigma_0 = 0.5$ over 1000 Monte Carlo runs (seeds $\mathrm{SEED} + m$) and record the NEES at the
20 observation epochs.

**Part C — the left/right transformation.** Verify (2) numerically in the setting of problem P4.

**Part D — the group-affine check.** For $f_u(X) = X\hat u$, measure both sides of (3) and
$g_u(\eta)$ at random $X$, $Y$ and $\eta$.

**Acceptance criteria — all four conditions must hold.**

1. **Part A** — reproduce the table below (each value within $\pm0.05$, except that for the EKF's
   $\sigma_0 = 0.5$ row it is enough to confirm the maximum exceeds $1.8$).

   | $\sigma_0$ | filter | step 0 / 40 / 80 / 120 / 160 / 199 |
   |---|---|---|
   | 0.05 | EKF | 1.01 / 1.01 / 1.07 / 1.07 / 1.06 / 1.05 |
   | 0.05 | invariant EKF | 1.02 / 1.00 / 1.01 / 1.00 / 1.01 / 1.00 |
   | 0.20 | EKF | 1.01 / 1.07 / 1.17 / 1.16 / 1.11 / 1.07 |
   | 0.20 | invariant EKF | 1.02 / 1.02 / 1.01 / 1.01 / 1.03 / 1.02 |
   | 0.50 | EKF | 1.00 / 1.34 / 1.89 / 1.95 / 1.59 / 1.24 |
   | 0.50 | invariant EKF | 1.02 / 1.02 / 1.02 / 1.03 / 1.05 / 1.04 |

   **The contrast in the last two rows is the point**: the invariant EKF's values barely react to
   $\sigma_0$.
2. **Part B** — $\mathrm{ANEES}/6$ of $6.86 \pm 0.3$ for the EKF and $3.23 \pm 0.2$ for the
   invariant EKF (ratio $\ge 2.0$); at the first observation epoch $96.9 \pm 5$ and
   $33.3 \pm 2$ (ratio $\ge 2.5$); at the last observation epoch **both** $1.00 \pm 0.05$. The
   final position RMSE is $0.0617$ m for the EKF and $0.0624$ m for the invariant EKF
   ($\pm 0.002$, within 5% of each other) — **report explicitly that consistency differs by a
   factor of two while accuracy is the same.**
3. **Part C** — the translation standard deviations of $\Sigma_R$ agree with
   $(0.01,\ 0.10049876,\ 0.10049876)$ to within $10^{-8}$, and the $4\times10^5$-sample Monte
   Carlo covariance agrees to within 1% relative error (reference 0.24%).
4. **Part D** — over 500 random pairs $X, Y$ the difference of the two sides of (3) satisfies
   $\max\lvert\cdot\rvert < 10^{-14}$ (reference $2.2\times10^{-16}$), and $g_u(\eta) = 0$ holds
   with $\max\lvert\cdot\rvert < 10^{-15}$ (reference exactly 0).

**Baselines**: (a) the baseline for Parts A and B is the standard EKF itself (same data, same
initial estimate). (b) Run a third filter — the invariant EKF with $H$ built from the prediction
$\hat y$ instead of the measurement $y$ — and report its ANEES; this isolates where the invariance
comes from. The reference implementation measures $\mathrm{ANEES}/6 = 13.348$ over 300 runs —
**worse even than the standard EKF ($6.858$)**: the advantage of the invariant EKF does not come
automatically from the group structure but from the choice of building $H$ from the measurement. (c) Optional: reduce $\sigma_0$ to $0.05$ and rerun Part B to confirm that the
difference between the two filters disappears.

**Numbers to report**: every value of the four criteria, the per-epoch NEES curve of Part B (the
reference implementation gives EKF
$96.95 \to 15.67 \to 5.37 \to 2.37 \to 1.46 \to 1.15 \to \cdots \to 1.00$ and invariant EKF
$33.25 \to 9.47 \to 3.63 \to 1.76 \to 1.24 \to 1.08 \to \cdots \to 1.02$), and the final rotation
RMSE (reference $0.0133$ rad for both).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| Both filters give identical NEES | the NEES was computed with a single error definition | check that it is $\log(X^{-1}\hat X)$ for the invariant EKF and $(\log(\hat RR^\top), \hat p - p)$ for the EKF |
| The invariant EKF is **worse** than the EKF | $H$ was built from $\hat y$ (not the invariant form), or the $\xi$ component order was mixed up as $(\rho,\phi)$ | check that $H = [-\widehat{y},\ I]$ and that the block layout of $\mathrm{Ad}$ matches the notation table |
| NEES diverges monotonically with the step | $P$ lost its symmetry (the Joseph form was not used) | print $\lVert P - P^\top\rVert_\infty$ every step and use $(I-KH)P(I-KH)^\top + KRK^\top$ |
| `log_se3` jumps at $\sigma_0 = 0.5$ | $\lVert\phi\rVert$ left the principal branch by exceeding $\pi$ | before computing NEES, look at the distribution of $\lVert\log(\cdot)\rVert$ and report the fraction of samples near $\pi$ |
| The invariant EKF also leaves 1 in Part A | $\mathrm{Ad}_{\Delta}$ was used instead of $\mathrm{Ad}_{\Delta^{-1}}$ | check that the two coincide when $\Delta$ is the identity and that the difference is $O(u)$ for small $u$ |
| The estimate diverges after an update | the correction sign — with a left-invariant error it is $\hat X \leftarrow \hat X\exp(-\delta\xi^\wedge)$ | run a single step and check that $\lVert\log(X^{-1}\hat X)\rVert$ decreases |

## Open problems

- **(Open problem) A systematic design procedure for systems that are not group-affine** — parts
  of a real robot's state (IMU biases, scale factors, aerodynamics, contact state) do not satisfy
  (3). Today one searches case by case for a larger group ($SE_2(3)$, or an extension with contact
  points in the state — [contact-aided
  InEKF](https://doi.org/10.1177/0278364919894385)) or uses a mixed "invariant plus
  non-invariant" filter. What is missing: a procedure that, given a dynamics-measurement pair,
  either **finds** a group-affine structure or **proves there is none**, together with a bound on
  the inconsistency that remains when there is none.
- **(Open problem) Inconsistency of the update step** — R3' is a theorem about propagation, and the
  measurement update is still a first-order expansion. The measurements of the reproduction task
  are the price (NEES$/6$ of 33 at the first epoch even for the invariant EKF). Current
  approaches: iterated EKF, designing invariant measurement models, and smoothing that uses
  posterior information ([the factor graph back end](https://doi.org/10.1561/2300000043)). What is
  missing: a manifold filter that is exact (or whose error is bounded) **through the update** at
  large errors.
- **(Open problem) Whether a tangent-space Gaussian is appropriate at all under large
  uncertainty** — as $\lVert\phi\rVert$ approaches $\pi$, $\xi$ is not unique and a tangent-space
  Gaussian cannot represent a distribution on $SO(3)$ properly (the same root as the open problem
  in `c1-so3-se3-exponential`). Current approaches: directional statistics such as Bingham and
  von Mises-Fisher distributions, the variational inference of
  [Barfoot SER ch.6](https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf), and the
  convention results of [micro Lie theory](https://arxiv.org/abs/1812.01537). What is missing: a
  quantitative criterion, at robotics scale, for **when to abandon** the tangent-space Gaussian.

## Concept check

Run `rc quiz c5-manifold-estimation`. The quiz is for **concept checking only**; the real work is
the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: what the condition $D\mathcal{R}_X(0) = \mathrm{id}$ in the definition of a
retraction guarantees; how a left-invariant covariance transforms into the right convention; the
autonomous error dynamics $g_u(\eta)$ of a group-affine system; whether the log-linear property
extends to the measurement update; and what an $\mathrm{ANEES}/\dim$ of 6.9 means.

## How to study this stage

1. **Fix the conventions first (45 min)** — copy the notation table's $\eta_L$, $\eta_R$,
   $\mathrm{Ad}$ and $(\phi,\rho)$ ordering onto paper, and expand (7) by hand to get
   $\xi_R = \mathrm{Ad}_{\hat X}\xi_L$ yourself. Every bug this lesson produces lives in that
   table.
2. **Do P4 next (30 min)** — watching the numbers spread from $0.01$ to $0.1005$, a factor of ten,
   makes "a covariance without its convention" viscerally meaningless. Read the left/right
   uncertainty section of Barfoot SER ch.7 alongside.
3. **Rewrite (9)-(11) from a blank page (60 min)** — the cancellation in R3 is **three lines**.
   Do not memorize them; be able to explain where $\hat X = \eta X$ is substituted and where the
   group-affine condition is applied. Then compute Examples 1 and 2 yourself to get $g_u = 0$ and
   $[\eta,\hat u]$.
4. **Write one paragraph on why it works for large errors (30 min)** — step 4 of R3' is the answer.
   When you can say "not a linearization but a change of coordinates" in your own words, the core
   of this lesson is done.
5. **Do Part A of the reproduction task first (60 min)** — propagation only, no measurements.
   Printing the table in which the invariant EKF's row does not react to $\sigma_0$ is the most
   convincing experience in this lesson. If it comes out wrong, look first at the direction of
   $\mathrm{Ad}_{\Delta^{-1}}$ and at the $(\phi,\rho)$ ordering.
6. **Parts B, C and D (135 min)** — in Part B, watch **both** filters leave 1 once the update is
   included, see that the final RMSE is the same, and write "consistency $\ne$ accuracy" into the
   report. Run the third filter with $H$ reverted to $\hat y$ to isolate where the invariance comes
   from.
7. **Read the papers in order (150 min)** — align the conventions with Solà et al. §4-7, then
   confirm (11) and R3' in the original text of Barrau & Bonnabel §II-III, then read §4.1 of
   Absil et al. for the exact definition of a retraction. Write the one-page note per paper
   **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the three open problems and write a
   paragraph. The inconsistency of the update step is the easiest to write, because the
   reproduction task's numbers are the evidence.

**Passing bar**: you can derive (2) and (9)-(11) from a blank page, you can write the "not a
linearization but a change of coordinates" argument of R3', you have code that satisfies all four
conditions of the reproduction task, and you have notes on all three papers.
