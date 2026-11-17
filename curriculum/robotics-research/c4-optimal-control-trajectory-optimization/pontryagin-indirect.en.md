---
id: c4-pontryagin-indirect
lang: en
title: Pontryagin's maximum principle and indirect methods
summary: >-
  Establish the first-order necessary conditions of optimal control (Pontryagin's minimum
  principle, PMP) via needle variations and a separating hyperplane; derive directly that the
  adjoint equation is the transpose of the variational equation, that the Hamiltonian is
  conserved, and where bang-bang structure comes from. Then show why the conditioning of
  indirect methods blows up exponentially in the horizon length, starting from the symplectic
  structure of the Hamiltonian flow, and solve the brachistochrone by shooting, matching the
  closed form to $10^{-13}$.
objectives:
  - Reconstruct the first-order necessary conditions of the PMP from needle variations and a separating-hyperplane argument.
  - Show that the adjoint equation is the transpose of the variational equation and derive conservation of the Hamiltonian for autonomous problems.
  - Decide from the switching function when a control-affine problem is bang-bang and when singular arcs appear.
  - Explain why the single-shooting Jacobian grows like $e^{\sigma T}$ from the $\pm$ eigenvalue pairs of a Hamiltonian matrix, and confirm it numerically.
  - Solve the brachistochrone with an indirect method and compare it against the closed-form cycloid numerically.
tags: [optimal-control, pontryagin, indirect-method, shooting, bang-bang, research]
---

# Pontryagin's maximum principle and indirect methods

## Setup and notation

This is the first lesson of module C4, and every later C4 lesson (LQR, iLQR, direct methods, MPC)
uses the Hamiltonian notation and the adjoint equation fixed here. The recommended prerequisites
are module R0 (convex optimization, numerical optimization, integrators) and module C1, but
**nothing is locked** — if you can do the self-diagnosis below, start here.

What this lesson assumes:

- Linear algebra: eigenvalues, the matrix exponential, transposes and duality, condition numbers.
- Analysis: existence and uniqueness for ODEs, state-transition matrices, the implicit function theorem.
- Optimization: Lagrange multipliers and KKT, the separating hyperplane theorem.
- Measure theory is **not** required — the places where "for almost every $t$" enters the needle
  variation are marked, and the technical details are left to the primary sources.

Notation (fixed for the whole of module C4):

| Symbol | Meaning |
|---|---|
| $x \in \mathbb{R}^n$ | state; the trajectory is $x(\cdot)$ and the optimum $x^*(\cdot)$ |
| $u \in U \subseteq \mathbb{R}^m$ | control; $U$ is a **closed** admissible set (it need not be convex) |
| $f(x, u, t) \in \mathbb{R}^n$ | dynamics $\dot{x} = f(x, u, t)$ |
| $\ell(x, u, t) \in \mathbb{R}$ | running cost; $\varphi(x, t)$ is the terminal cost |
| $\lambda(t) \in \mathbb{R}^n$ | costate (adjoint); a **column vector**, the same dimension as $f$ |
| $\lambda_0 \ge 0$ | the multiplier on the cost. The case normalised to $\lambda_0 = 1$ is **normal**, $\lambda_0 = 0$ is **abnormal** |
| $H(x, u, \lambda, t)$ | Hamiltonian $\lambda_0\,\ell(x,u,t) + \lambda^\top f(x,u,t)$ |
| $\psi(x, t) \in \mathbb{R}^q$ | terminal constraint $\psi(x(t_f), t_f) = 0$ |
| $\Phi(t, s) \in \mathbb{R}^{n \times n}$ | state-transition matrix of the linearisation $\dot{\delta x} = f_x\,\delta x$ |
| $z = (x, \lambda) \in \mathbb{R}^{2n}$ | state of the Hamiltonian system |

**Sign convention**: this course uses the **minimum principle** — the optimal control
**minimises** $H$. Pontryagin's original uses the sign convention in which $H$ is maximised, and
the two differ only in the sign of $\lambda$. This is the first thing to check when opening a paper.

The reference problem (called $(\mathrm{P})$ throughout this lesson):

$$
\min_{u(\cdot) \in U,\ t_f} \; J[u] = \int_0^{t_f} \ell(x, u, t)\,dt + \varphi(x(t_f), t_f)
  \quad \text{s.t.} \quad \dot{x} = f(x, u, t), \; x(0) = x_0, \; \psi(x(t_f), t_f) = 0. \tag{1}
$$

## Self-diagnosis before starting

This is the first lesson of the module, so check your readiness first. **Prerequisite lessons are
not locked** — if you can do all of the following, skip the recommended prerequisites and start
here. **If two or more block you**, it is faster to go back to the lesson named in parentheses.

1. Write the solution of $\dot{\delta x} = A(t)\,\delta x$ using a state-transition matrix, and
   state the differential equation $\Phi(t, s)$ satisfies together with the value of $\Phi(t,t)$.
   (`r0-ad-and-integrators`)
   **Answer**: $\delta x(t) = \Phi(t,s)\delta x(s)$, $\partial_t \Phi(t,s) = A(t)\Phi(t,s)$,
   $\Phi(t,t) = I$. Also $\partial_t \Phi(t,s)^{-1} = -\Phi(t,s)^{-1}A(t)$, so the **transpose**
   flows backwards with $-A^\top$ — that is exactly what the adjoint equation is.
2. Write the first-order conditions (KKT) of $\min_x c(x)$ s.t. $h(x) = 0$. What is needed for
   the Lagrange multiplier to exist and be *unique*? (`r0-convex-optimization`)
   **Answer**: $\nabla c + (\partial h/\partial x)^\top \nu = 0$, $h(x) = 0$. Existence and
   uniqueness follow from LICQ ($\partial h/\partial x$ of full row rank). When the rank drops
   there is either no multiplier or infinitely many — the abnormal case $\lambda_0 = 0$ of the
   PMP is the counterpart of exactly this.
3. Give the eigenvalues of $A = \begin{bmatrix} 1 & -1 \\ -1 & -1\end{bmatrix}$ and the
   behaviour of $\lVert e^{At} \rVert_2$ as $t \to \infty$.
   (`r0-linear-algebra-decompositions`)
   **Answer**: $\mu = \pm\sqrt{2}$ (tolerance $10^{-9}$). The eigenvalues come as a $\pm$ pair,
   so one direction blows up like $e^{\sqrt2 t}$ while another decays at the same rate:
   $\lVert e^{At}\rVert_2 \sim c\,e^{\sqrt2 t}$.
4. State the separating hyperplane theorem for a convex set $K \subset \mathbb{R}^d$ and a point
   $p \notin K$. What breaks if $K$ is **not** convex? (`r0-convex-optimization`)
   **Answer**: there is $a \ne 0$ with $a^\top p \le \inf_{y \in K} a^\top y$. Without convexity
   a separating hyperplane need not exist — which is why the proof of the PMP has to establish
   separately that the cone of needle variations is convex.
5. In a problem where the terminal time is a decision variable, such as $\min_{t_f} t_f$, what
   does the first-order condition in $t_f$ become? Explain with the simplest example
   $\min_{T} \int_0^T 1\,dt$ s.t. $x(T) = 0$. (`f0-calculus-multivariable`)
   **Answer**: it is a derivative with respect to the upper limit of an integral, so the terminal
   value of the integrand enters the condition — in general
   $H(t_f) + \partial\varphi/\partial t_f = 0$. For an autonomous minimum-time problem with no
   terminal cost, $H \equiv 0$.

## Key results

The bracket gives the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (Pontryagin's minimum principle) [D3]** — if $(u^*, x^*, t_f^*)$ solves $(\mathrm{P})$,
  then there exist $\lambda_0 \ge 0$ and an absolutely continuous
  $\lambda : [0, t_f^*] \to \mathbb{R}^n$ with $(\lambda_0, \lambda(t)) \ne 0$ for all $t$, such that
  $$
  \dot{x}^* = \frac{\partial H}{\partial \lambda} = f, \qquad
    \dot{\lambda} = -\frac{\partial H}{\partial x}
    = -\lambda_0 \ell_x^\top - f_x^\top \lambda, \tag{2}
  $$
  $$
  u^*(t) \in \arg\min_{w \in U} H\big(x^*(t), w, \lambda(t), t\big)
    \quad \text{for almost every } t, \tag{3}
  $$
  $$
  \lambda(t_f) = \lambda_0 \varphi_x^\top + \psi_x^\top \nu \;\;(\exists \nu \in \mathbb{R}^q),
    \qquad H(t_f) + \lambda_0\frac{\partial \varphi}{\partial t_f} = 0 \;\;(t_f \text{ free}). \tag{4}
  $$
  These are **necessary conditions only** — a trajectory satisfying (2)–(4) (an **extremal**)
  need not be optimal.
- **R2 (what the adjoint equation is, and conservation of the Hamiltonian) [D2]** — the adjoint
  equation in (2) is the **transpose of the variational equation** $\dot{\delta x} = f_x \delta x$
  run backwards in time, so $\lambda(t)^\top \delta x(t)$ is conserved when there is no cost term.
  Moreover, if $f$ and $\ell$ do not depend explicitly on $t$,
  $$\frac{d}{dt}H\big(x^*(t), u^*(t), \lambda(t), t\big) = 0 \quad \text{for almost every } t, \tag{5}$$
  and if $t_f$ is free and $\varphi$ does not depend on $t_f$, then $H \equiv 0$.
- **R3 (bang-bang structure and singular arcs in control-affine problems) [D2]** — if
  $f = f_0(x,t) + F(x,t)u$, $\ell = \ell_0(x,t)$ and $U = \prod_i [a_i, b_i]$, then $H$ is affine
  in $u$,
  $$H = \lambda_0 \ell_0 + \lambda^\top f_0 + s(t)^\top u, \qquad s(t) := F(x^*,t)^\top \lambda(t), \tag{6}$$
  so (3) is solved componentwise by $u_i^* = a_i\,(s_i > 0)$, $u_i^* = b_i\,(s_i < 0)$. On an
  interval where $s_i \equiv 0$ the first-order condition **says nothing at all** about $u_i$
  (a singular arc). For the minimum-time double integrator $s$ is affine in $t$, so there is
  **at most one** switch.
- **R4 (sensitivity blow-up of single shooting) [D2]** — an indirect method takes $\lambda(0)$ as
  the unknown and root-finds on the terminal conditions. The Jacobian of that shooting map
  contains the state-transition matrix of the linearised Hamiltonian system, whose coefficient
  matrix is a **Hamiltonian matrix**, so its eigenvalues come in $\pm\mu$ pairs. Under
  hyperbolicity ($\sigma := \max_i \operatorname{Re}\mu_i > 0$),
  $$
  \left\lVert \frac{\partial S}{\partial p} \right\rVert \sim c\,e^{\sigma T}, \qquad
    \kappa\!\left(\frac{\partial S}{\partial p}\right) \sim e^{2\sigma T}, \tag{7}
  $$
  and in double precision the horizon on which a residual $\mathrm{tol}$ is reachable is capped at
  $T \le \sigma^{-1}\ln\!\big(\mathrm{tol}/(c\,\varepsilon_{\mathrm{mach}})\big)$.
  **The two-point boundary value problem itself is perfectly conditioned** — what breaks is the
  reduction to an initial value problem.
- **R5 (the PMP solution of the brachistochrone: the path angle is affine in time) [D2]** — for
  minimum-time descent in a gravity field the optimal path angle $\theta(t)$ satisfies
  $$\dot{\theta} = -\frac{g\cos\theta}{v} = \text{const} =: -k, \qquad v(t) = \frac{g}{k}\cos\theta(t), \tag{8}$$
  so $\theta(t) = \theta_0 - kt$ is affine in $t$ and the trajectory is a cycloid. The costates
  are available in closed form: $\lambda_x = -k/g$, $\lambda_y = -(k/g)\tan\theta_f$,
  $\lambda_v(t) = g^{-1}(\tan\theta_f\cos\theta - \sin\theta)$. **[D2]**

## Derivation

### R2 — the adjoint equation is the transpose of the variational equation

Before proving the PMP, see where (2) comes from. This is the key to reading steps 4 and 5 of the
proof of R1.

Perturbing the control around the optimal trajectory $x^*$ to $u^* + \delta u$, the state follows,
to first order,
$$\dot{\delta x} = f_x\,\delta x + f_u\,\delta u, \qquad \delta x(0) = 0 \tag{9}$$
(with $f_x := \partial f/\partial x$ evaluated at $(x^*(t), u^*(t), t)$). The solution of (9), in
terms of the state-transition matrix, is
$$\delta x(t) = \int_0^t \Phi(t, s)\,f_u(s)\,\delta u(s)\,ds. \tag{10}$$

The first-order change in the cost is $\delta J = \int_0^{t_f}(\ell_x \delta x + \ell_u \delta u)\,dt
+ \varphi_x \delta x(t_f)$. Substituting (10) makes $\delta x$ enter as a **double integral of
$\delta u$**, which is awkward. Exchanging the order of integration is the key step:

$$
\int_0^{t_f}\!\!\ell_x(t)\!\int_0^t \Phi(t,s) f_u(s)\delta u(s)\,ds\,dt
  = \int_0^{t_f}\!\!\left[\int_s^{t_f}\!\! \ell_x(t)\Phi(t,s)\,dt\right] f_u(s)\,\delta u(s)\,ds.
$$

So if we *define* $\lambda$ as the transpose of the bracketed quantity, everything collapses to a
single integral:

$$
\lambda(s)^\top := \lambda_0\!\int_s^{t_f}\! \ell_x(t)\,\Phi(t,s)\,dt
  + \lambda_0 \varphi_x \Phi(t_f, s). \tag{11}
$$

Differentiate (11) in $s$. Using $\partial_s \Phi(t,s) = -\Phi(t,s) f_x(s)$ (self-diagnosis 1) and
picking up $\Phi(s,s) = I$ from the lower limit of the integral,

$$
\dot{\lambda}(s)^\top = -\lambda_0 \ell_x(s) - \lambda(s)^\top f_x(s)
  \;\;\Longleftrightarrow\;\; \dot{\lambda} = -\lambda_0 \ell_x^\top - f_x^\top \lambda
  = -\frac{\partial H}{\partial x}, \tag{12}
$$

which is (2). The terminal value comes from putting $s = t_f$ in (11):
$\lambda(t_f) = \lambda_0 \varphi_x^\top$ — the case of (4) without $\psi$. And the cost change is

$$
\delta J = \int_0^{t_f}\Big(\lambda_0 \ell_u + \lambda^\top f_u\Big)\delta u\,dt
  = \int_0^{t_f} \frac{\partial H}{\partial u}\,\delta u\,dt. \tag{13}
$$

**How to read this**: $\lambda$ is "the sensitivity of the cost to the state, pulled back from the
terminal time". The reason $f_x$ appears transposed and flowing backwards is entirely contained in
the exchange of integration order in (11). This is the **same computation** as reverse-mode
automatic differentiation, and its counterpart is the backward pass of `c4-ilqr-ddp`.

**Where the assumptions break**: (13) yields $\partial H/\partial u = 0$ only when $u$ can be
perturbed **in both directions**, i.e. $U = \mathbb{R}^m$. If $u^*$ lies on the boundary of $U$,
only one-sided $\delta u$ is admissible and the conclusion weakens to
$\partial H/\partial u \cdot \delta u \ge 0$; and if $U$ is not convex the first variation is
unusable altogether. That is exactly why (3) of the PMP is written as a **minimisation** rather
than as a derivative — the proof of R1 abandons the linearisation (9) and uses needle variations.

### R2 (continued) — conservation of the Hamiltonian

Let $H^*(t) := \min_{w \in U} H(x^*(t), w, \lambda(t), t)$. As a minimum-value function it is
locally Lipschitz by Danskin's theorem, and for almost every $t$

$$
\frac{dH^*}{dt} = \underbrace{H_x \dot{x}^* + H_\lambda \dot{\lambda}}_{\text{state and costate}}
  + \frac{\partial H}{\partial t}\bigg|_{u = u^*}. \tag{14}
$$

(The term differentiating the minimising $w$ drops out — the envelope theorem. At a switching
instant, where $u^*$ jumps, the two candidate values of $H$ agree, so $H^*$ is **continuous** and
(14) holds off that finite set.)

Substituting (2) into (14), the state and costate terms cancel exactly:

$$
H_x \dot{x}^* + H_\lambda \dot{\lambda}
  = H_x H_\lambda^\top + H_\lambda(-H_x^\top) = 0. \tag{15}
$$

Hence $dH^*/dt = \partial H/\partial t = \lambda_0 \ell_t + \lambda^\top f_t$, and if $f$ and
$\ell$ do not depend explicitly on $t$ then $H^* \equiv \text{const}$ — this is (5). Combining
with the free-$t_f$ condition in (4), that constant is zero.

**Where the assumptions break**: (i) Non-autonomous problems. If $t$ appears explicitly in $\ell$
or $f$, $H$ is not conserved — and the common practice of using
$\lvert H(t) - H(0)\rvert$ of a numerical solution as a convergence diagnostic then raises false
alarms. (ii) State constraints $g(x) \le 0$. Where a constraint is active, $\lambda$ is no longer
absolutely continuous but of bounded variation (BV): it **jumps**, and $H$ may jump there too
(Hartl et al. 1995 §3). (iii) If $U$ is not closed, the minimum in (3) need not exist and $H^*$
is undefined.

### R3 — bang-bang and singular arcs

(6) writes $H$ as an affine function of $u$. Minimising an affine function over a box
$\prod_i[a_i, b_i]$ needs only the sign of each coefficient:

$$
u_i^*(t) = \begin{cases}
  a_i, & s_i(t) > 0, \\
  b_i, & s_i(t) < 0, \\
  \text{undetermined}, & s_i(t) = 0.
\end{cases} \tag{16}
$$

$s(t) = F^\top\lambda$ is the **switching function**. If the zeros of $s_i$ are isolated, the
control is bang-bang between the bounds; an interval on which $s_i \equiv 0$ is a singular arc.

Make this concrete with the **minimum-time double integrator**: $\dot{x}_1 = x_2$,
$\dot{x}_2 = u$, $\lvert u \rvert \le 1$, $\ell = 1$, $\varphi = 0$, terminal $x(t_f) = 0$,
$t_f$ free.

$$H = \lambda_0 + \lambda_1 x_2 + \lambda_2 u. \tag{17}$$

The adjoint equation (2) gives $\dot\lambda_1 = -\partial H/\partial x_1 = 0$ and
$\dot\lambda_2 = -\partial H/\partial x_2 = -\lambda_1$, so

$$\lambda_1(t) = c_1, \qquad \lambda_2(t) = c_2 - c_1 t. \tag{18}$$

$\lambda_2$ is affine in $t$. An affine function is either identically zero or has at most one zero.

- If $\lambda_2 \equiv 0$ then $c_1 = c_2 = 0$, so by (18) $\lambda \equiv 0$, and then (17) gives
  $H = \lambda_0$. Since $t_f$ is free, $H \equiv 0$, so $\lambda_0 = 0$, violating
  $(\lambda_0, \lambda) \ne 0$. **A singular arc cannot exist.**
- Hence $\lambda_2$ has at most one zero, and by (16)
  $u^* = -\operatorname{sign}\lambda_2 \in \{-1, +1\}$ with **at most one** switch.

Write out the solution from $x(0) = (1, 0)$ to the origin. Since $x_1 > 0$ we must decelerate
first, so take $u = -1$ initially: $x_2 = -t$, $x_1 = 1 - t^2/2$. After the switching time $t_s$
we have $u = +1$, and reaching the origin requires $x_2(t_f) = 0$, i.e. $t_f - t_s = t_s$, so
$t_f = 2t_s$. Also $x_1(t_f) = 1 - t_s^2/2 - t_s\cdot t_s + t_s^2/2 = 1 - t_s^2 = 0$, hence

$$t_s = 1, \qquad t_f = 2, \qquad x(t_s) = (0.5,\, -1). \tag{19}$$

**Where the assumptions break**: (i) **Singular arcs.** Give the same dynamics the cost
$\ell = x_1^2$ (least squared deviation rather than minimum time): $H$ is still affine in $u$ but
$\lambda_2$ is no longer affine, and Fuller 1963 showed that the optimal control switches
**infinitely many times** in finite time (Fuller's phenomenon). Every indirect method that
assumes a finite switching structure fails on that problem. (ii) **Detecting singular arcs.**
Where $s_i \equiv 0$, determining $u$ requires higher-order conditions such as $\ddot{s}_i = 0$
(the Kelley condition), and **there is no general algorithm** for finding in advance which
intervals are singular (Betts 1998 §4). (iii) If $H$ is not affine in $u$ — say $\ell$ contains
$u^\top R u$ — then (16) does not hold and the minimum is interior; that is the world of
`c4-dp-lqr-lqg`.

### R4 — the condition number of single shooting grows like $e^{\sigma T}$

The structure of an indirect (single-shooting) method is this. Using (3) to eliminate $u$ as a
function $u^*(x,\lambda,t)$ of $(x, \lambda)$ turns (2) into a **closed** differential equation in
$z = (x, \lambda) \in \mathbb{R}^{2n}$:

$$
\dot{z} = \mathcal{H}(z, t) := \begin{bmatrix} \partial H/\partial \lambda \\
  -\partial H/\partial x \end{bmatrix}_{u = u^*(x,\lambda,t)}
  = J\,\nabla_z H, \qquad J = \begin{bmatrix} 0 & I \\ -I & 0\end{bmatrix}. \tag{20}
$$

The unknown is $p := \lambda(0) \in \mathbb{R}^n$ (plus $t_f$ when free), and the conditions are
the terminal ones (4). Writing the shooting map as $S(p) := r\big(z(T; p)\big)$ (with $r$ the
terminal residual),

$$
\frac{\partial S}{\partial p} = \frac{\partial r}{\partial z}\,\Phi_{\mathcal H}(T, 0)
  \begin{bmatrix} 0 \\ I \end{bmatrix}, \qquad
  \dot{\Phi}_{\mathcal H} = \underbrace{J\,\nabla_z^2 H}_{=: \mathcal{A}(t)}\,\Phi_{\mathcal H}. \tag{21}
$$

$\mathcal{A} = J\,\nabla^2_z H$ is a **Hamiltonian matrix** (since $\nabla^2_z H$ is symmetric,
$(J\mathcal{S})^\top J + J (J \mathcal{S}) = 0$). The eigenvalues of a Hamiltonian matrix come in
**$\pm$ pairs**: if $\mu$ is an eigenvalue so is $-\mu$. Hence in the constant-coefficient case
the singular values of $\Phi_{\mathcal H}(T,0) = e^{\mathcal{A}T}$ split into $e^{\sigma T}$ and
$e^{-\sigma T}$ (with $\sigma = \max_i \operatorname{Re}\mu_i$), and the condition number is
$e^{2\sigma T}$ — this is (7).

**A scalar example, down to the constant.** Take $\dot{x} = ax + u$,
$J = \tfrac12\int_0^T (qx^2 + u^2)dt$, $x(0) = x_0$, terminal free ($\varphi = 0$). Then
$H = \tfrac12(qx^2 + u^2) + \lambda(ax + u)$, and $\partial H/\partial u = u + \lambda = 0$ gives
$u^* = -\lambda$, so

$$
\begin{bmatrix}\dot{x} \\ \dot{\lambda}\end{bmatrix}
  = \underbrace{\begin{bmatrix} a & -1 \\ -q & -a\end{bmatrix}}_{=:\,M}
  \begin{bmatrix}x \\ \lambda\end{bmatrix}, \qquad
  \operatorname{tr} M = 0, \; \det M = -(a^2 + q). \tag{22}
$$

$\operatorname{tr} M = 0$ *is* the $\pm$ pair: $\mu^2 = a^2 + q$, so $\mu = \pm\sigma$ with
$\sigma = \sqrt{a^2+q}$. Since $e^{MT} = \cosh(\sigma T)I + \sigma^{-1}\sinh(\sigma T)M$, the
residual of the terminal condition $\lambda(T) = 0$,
$r(p) = \lambda(T) = (e^{MT})_{21}x_0 + (e^{MT})_{22}\,p$, satisfies

$$
\frac{dr}{dp} = (e^{MT})_{22} = \cosh\sigma T - \frac{a}{\sigma}\sinh\sigma T
  \;\xrightarrow[T \to \infty]{}\; \underbrace{\frac{1}{2}\left(1 - \frac{a}{\sigma}\right)}_{=:\,c}
  e^{\sigma T}. \tag{23}
$$

For $a = q = 1$: $\sigma = \sqrt2 = 1.4142135624$ and $c = 0.1464466094$. At $T = 10$,
$dr/dp = 2.03 \times 10^{5}$; at $T = 20$, $2.81\times10^{11}$. Since $p$ can only be represented
to a relative error $\varepsilon_{\mathrm{mach}} = 2.22\times10^{-16}$, the smallest attainable
residual is $\lvert dr/dp\rvert\,\lvert p^*\rvert\,\varepsilon_{\mathrm{mach}}$, and the point at
which that exceeds $\mathrm{tol} = 10^{-6}$ is

$$T^* = \frac{1}{\sigma}\ln\frac{\mathrm{tol}}{c\,\varepsilon_{\mathrm{mach}}} = 17.08 \tag{24}$$

(the reproduction task measures this: the actual crossover is $T = 17$). Doubling $T$ multiplies
the required precision by $e^{\sigma T}$, so **no better root-finding algorithm can fix this.**

**Why the boundary value problem itself is fine**: it is true that $e^{MT}$ splits into a stable
and an unstable subspace, but the two-point problem can propagate $x(0)$ **forwards along the
unstable directions** and $\lambda(T)$ **backwards along the stable ones**, so the norm of its
solution operator is $O(1)$. What breaks is the *reduction* — "collect all unknowns at $t=0$ and
integrate the whole interval forwards". That is why multiple shooting splits the interval into $N$
pieces, turning $e^{\sigma T}$ into $e^{\sigma T/N}$, and why collocation corresponds to taking
$N$ to the number of grid points (`c4-direct-collocation-sqp`).

**Where the assumptions break**: the blow-up is tied to **hyperbolicity** ($\sigma > 0$). If
$a^2 + q < 0$ then $\mu = \pm i\lvert\sigma\rvert$ is purely imaginary, $e^{MT}$ is a bounded
oscillation, and the condition number of single shooting does not grow. "Indirect methods always
blow up" is false — in fact the reproduction task of this lesson (the brachistochrone, with
$t_f \approx 0.47\,\mathrm{s}$) reaches a residual of $4\times10^{-16}$ by single shooting. For
short or non-hyperbolic horizons, indirect methods are the **most accurate** option.

### R5 — solving the brachistochrone with the PMP, all the way

Take $y$ positive **downwards** and let $\theta$ be the path angle below the horizontal. State
$(x, y, v)$, control $\theta \in \mathbb{R}$ (unconstrained), gravity $g$:

$$
\dot{x} = v\cos\theta, \qquad \dot{y} = v\sin\theta, \qquad \dot{v} = g\sin\theta, \tag{25}
$$

with $x(0) = y(0) = 0$, $v(0) = v_0 > 0$, terminal $(x(t_f), y(t_f)) = (x_f, y_f)$, $v(t_f)$ free,
minimising $t_f$. In the normal case, setting $\lambda_0 = 1$,

$$H = 1 + \lambda_x v\cos\theta + \lambda_y v \sin\theta + \lambda_v g \sin\theta. \tag{26}$$

The adjoint equation (2):

$$
\dot\lambda_x = 0, \qquad \dot\lambda_y = 0, \qquad
  \dot\lambda_v = -(\lambda_x\cos\theta + \lambda_y\sin\theta) =: -A. \tag{27}
$$

Since $\theta$ is free, (3) becomes $\partial H/\partial\theta = 0$:

$$
-\lambda_x v \sin\theta + \lambda_y v\cos\theta + \lambda_v g \cos\theta = 0
  \;\;\Longleftrightarrow\;\; vB = \lambda_v g \cos\theta, \tag{28}
$$

where $B := \lambda_x\sin\theta - \lambda_y\cos\theta$. Because $v(t_f)$ is free and there is no
terminal cost, (4) gives $\lambda_v(t_f) = 0$; and because $t_f$ is free and the problem is
autonomous, $H \equiv 0$.

**Step 1 — find $\lambda_x$.** Substitute $\lambda_v g = vB/\cos\theta$ from (28) into $H = 0$:

$$
0 = 1 + vA + \frac{vB}{\cos\theta}\sin\theta
  = 1 + v\left[\lambda_x\cos\theta + \lambda_y\sin\theta
  + (\lambda_x\sin\theta - \lambda_y\cos\theta)\tan\theta\right].
$$

Tidy up the bracket. The $\lambda_y$ terms **cancel**,
$\lambda_y\sin\theta - \lambda_y\sin\theta = 0$, and the $\lambda_x$ terms collect into
$\lambda_x(\cos^2\theta + \sin^2\theta)/\cos\theta = \lambda_x/\cos\theta$. Therefore

$$0 = 1 + \frac{v\lambda_x}{\cos\theta} \quad\Longrightarrow\quad \lambda_x = -\frac{\cos\theta}{v}. \tag{29}$$

By (27) $\lambda_x$ is constant, so **$\cos\theta/v$ is constant along the whole trajectory** —
the classical conserved quantity of the brachistochrone, in the form of Snell's law.

**Step 2 — show $\dot\theta$ is constant.** Differentiating (29),

$$
0 = \frac{d}{dt}\frac{\cos\theta}{v}
  = \frac{-\dot\theta \sin\theta\, v - \cos\theta\,\dot{v}}{v^2}
  = \frac{-\dot\theta\sin\theta\,v - g\sin\theta\cos\theta}{v^2}
$$

(using $\dot v = g\sin\theta$). Dividing by $\sin\theta$ where $\sin\theta \ne 0$,

$$\dot\theta = -\frac{g\cos\theta}{v}. \tag{30}$$

By (29), $\cos\theta/v = -\lambda_x$ is constant, so the right-hand side of (30) is that constant
times $g$:

$$
\dot\theta = -\frac{g\cos\theta}{v} = g\lambda_x = \text{const} =: -k, \qquad
  k := -g\lambda_x > 0, \qquad v(t) = \frac{g}{k}\cos\theta(t), \tag{31}
$$

(the last equality is (29) solved for $v$ with $\lambda_x = -k/g$ substituted). So
$\theta(t) = \theta_0 - kt$ and $\lambda_x = -k/g$ — this is (8). The initial condition
$v(0) = v_0$ fixes $\theta_0$ through $\cos\theta_0 = k v_0/g$.

**Step 3 — $\lambda_y$ and $\lambda_v$.** Substituting $v = (g/k)\cos\theta$ into (28) gives
$\lambda_v = B/k$. Since $\lambda_v(t_f) = 0$ we need $B(t_f) = 0$, i.e.
$\lambda_x \sin\theta_f = \lambda_y\cos\theta_f$, hence

$$
\lambda_y = \lambda_x \tan\theta_f = -\frac{k}{g}\tan\theta_f, \qquad
  \lambda_v(t) = \frac{1}{g}\big(\tan\theta_f\cos\theta(t) - \sin\theta(t)\big). \tag{32}
$$

Check directly that $\dot\lambda_v = -A$ from (27) agrees with (32) — that is problem P1.

**Step 4 — the trajectory (a cycloid).** Substituting (31) into (25) and integrating, with
$\theta_t := \theta_0 - kt$,

$$
x(t) = \frac{g}{k}\left[\frac{t}{2} + \frac{\sin 2\theta_0 - \sin 2\theta_t}{4k}\right],
  \qquad y(t) = \frac{g\,(\cos 2\theta_t - \cos 2\theta_0)}{4k^2}. \tag{33}
$$

In the classical case $v_0 = 0$ we have $\theta_0 = \pi/2$, and substituting $\phi := 2kt$ and
$R := g/(4k^2)$ turns (33) into $x = R(\phi - \sin\phi)$, $y = R(1 - \cos\phi)$ — a cycloid.
Energy conservation $v^2 = v_0^2 + 2gy$ also follows directly from (31) and (33) (problem P2).

**Where the assumptions break**: (i) Step 2 used $\sin\theta \ne 0$. At $\theta = 0$ (horizontal
motion) $\dot v = 0$, so the particle does not accelerate; and if $v_0 = 0$ the right-hand side of
(30) is $0/0$ — the **starting point of the classical brachistochrone is a singularity**, which is
why the reproduction task avoids it by taking $v_0 > 0$. For $v_0 = 0$ the PMP forces
$\theta_0 = \pi/2$ and $k$ survives as the free coefficient of a series expansion. (ii) If
$\lambda_x = 0$ then (29) reads $1 = 0$, a contradiction, so $\lambda_x \ne 0$ is guaranteed in
the normal case; but if the problem degenerates — $x_f = 0$, i.e. pure vertical descent — abnormal
($\lambda_0 = 0$) extremals appear. (iii) If $y_f \le 0$ (the target above the start), the first
question is whether $v_0$ makes it reachable at all, and if it is not, there is no extremal.

## Proof sketch

### R1 — Pontryagin's minimum principle [D3]

**Hypotheses**
H1: $f$ and $\ell$ are $C^1$ in $x$, continuous in $u$, measurable and locally bounded in $t$.
H2: $U \subseteq \mathbb{R}^m$ is closed (it need not be convex or bounded).
H3: $u^*$ solves $(\mathrm{P})$ and the corresponding $x^*$ exists on $[0, t_f^*]$.
H4: $\psi$ is $C^1$.

**Conclusion** C: there exist $(\lambda_0, \lambda) \ne 0$ with $\lambda_0 \ge 0$ satisfying
(2), (3) and (4).

**Strategy**: lift the cost into a zeroth state component to turn the problem into one about the
**boundary of the reachable set**, then separate the **convex cone** generated by needle
variations from the "cost-decreasing" directions with a hyperplane. Pulling that covector back
along the flow yields $\lambda$, and the separation inequality applied to each needle is exactly
(3). The crux is to take variations that are **short in duration** (needles) rather than **small
in magnitude** ($\delta u$ small) — only then do they work on the boundary of $U$.

1. **Lift the cost into the state.** Append $x_c(t) := \int_0^t \ell\,ds$ as a zeroth component,
   $\tilde{x} = (x_c, x) \in \mathbb{R}^{1+n}$ and $\tilde{f} = (\ell, f)$. If $u^*$ is optimal,
   the terminal point $\tilde{x}^*(t_f)$ cannot have its $x_c$ component lowered inside the
   reachable set
   $\mathcal{R} := \{\tilde{x}(t_f; u) : u(\cdot) \in \mathcal{U},\ \psi = 0\}$; that is,
   $\tilde{x}^*(t_f)$ is a **boundary point** of $\mathcal{R}$.
2. **Needle variation.** For $\tau \in (0, t_f)$, $w \in U$ and small $\varepsilon > 0$, set
   $u_\varepsilon := w$ on $[\tau, \tau+\varepsilon]$ and $u^*$ elsewhere. To first order in
   $\varepsilon$ the terminal point moves by
   $$
   \Delta\tilde{x}(t_f) = \varepsilon\,\tilde\Phi(t_f, \tau)
     \big[\tilde f(x^*(\tau), w, \tau) - \tilde f(x^*(\tau), u^*(\tau), \tau)\big] + o(\varepsilon),
   $$
   where $\tilde\Phi$ is the state-transition matrix of the linearisation (9). Here $\tau$ must be
   a **Lebesgue point** of $u^*$ — i.e. almost every $\tau$, which is where the "almost every $t$"
   of (3) comes from.
3. **The cone is convex.** Needles at distinct times **concatenate**, so their first-order changes
   add; and shortening a needle to length $\alpha\varepsilon$ scales its change by $\alpha$.
   Hence the set of all first-order changes,
   $$
   K := \operatorname{cone}\Big\{\tilde\Phi(t_f,\tau)\big[\tilde f(x^*(\tau), w, \tau)
     - \tilde f(x^*(\tau), u^*(\tau), \tau)\big] : \tau \in (0,t_f),\ w \in U \Big\},
   $$
   is a **convex cone**. (This step is the heart of the proof — it is where convexity of $K$ is
   obtained *without* convexity of $U$. This is what self-diagnosis 4 was for.)
4. **Separation.** The boundary property of step 1 says that $K$ contains no direction that
   lowers $x_c$ while staying in the tangent space of the terminal constraint. So there is a
   nonzero $(\lambda_0, -\lambda_f) \in \mathbb{R}^{1+n}$ separating $K$ from that convex set of
   forbidden directions. The sign in the $x_c$ direction gives $\lambda_0 \ge 0$, and
   orthogonality to the tangent space of the terminal constraint gives
   $\lambda(t_f) = \lambda_0\varphi_x^\top + \psi_x^\top\nu$ in (4).
5. **Pull the separating covector back.** Define $\lambda(t)^\top$ as the state part of
   $-(\lambda_0, -\lambda_f)$ pulled back by $\tilde\Phi(t_f, t)$. Since
   $\partial_t\tilde\Phi(t_f,t) = -\tilde\Phi(t_f,t)\tilde f_x(t)$, this $\lambda$ satisfies
   exactly the adjoint equation (2) (the same computation as (11)–(12) in R2). Applying the
   separation inequality to each generator of step 3 then gives, for almost every $\tau$ and every
   $w \in U$,
   $$
   \lambda_0\ell(x^*,w,\tau) + \lambda(\tau)^\top f(x^*,w,\tau)
     \;\ge\; \lambda_0\ell(x^*,u^*,\tau) + \lambda(\tau)^\top f(x^*,u^*,\tau),
   $$
   i.e. $H(x^*, w, \lambda, \tau) \ge H(x^*, u^*, \lambda, \tau)$ — this is (3).
6. **Free $t_f$.** Adding the variation $t_f \mapsto t_f \pm \varepsilon$ admits **both** signs,
   which upgrades the inequality to the equality
   $H(t_f) + \lambda_0\partial_{t_f}\varphi = 0$.

(Omitted: the lemma that the first-order approximation of $\mathcal{R}$ really is $K$, which needs
a contraction-mapping or Brouwer fixed-point argument. The original is the variational-cone lemma
of Pontryagin et al. 1962; the modern statement is
[Sussmann & Willems 1997](https://doi.org/10.1109/37.588098) §V. The absolute-continuity argument
for measurable controls is also omitted.)

**Deleting a hypothesis: where does it collapse?**

- **Delete H1 ($C^1$)**: the $\tilde\Phi$ of step 2 does not exist. When $f$ is discontinuous in
  $x$, as with rigid contact, the costate **jumps** across the mode-transition surface, and what
  describes that jump is the saltation matrix (`c4-contact-implicit-hybrid`). Applying the smooth
  PMP as-is yields the wrong gradient.
- **Delete the assumption of no state constraints**: on an interval where $g(x) \le 0$ is active,
  the reachable set of step 1 is pressed against the constraint surface, and the separating
  covector acquires a **measure** supported on it. $\lambda$ becomes BV rather than absolutely
  continuous and (2) turns into $d\lambda = -H_x dt + g_x^\top d\eta$ (Hartl et al. 1995 §3).
- **Expect $\lambda_0 > 0$**: the separating covector of step 4 may have $\lambda_0 = 0$ (the
  abnormal case). Then $\ell$ does not enter (3) at all, the conditions say nothing **about the
  cost**, and the PMP is vacuous. This happens when the terminal point barely sits on the boundary
  of the reachable set, i.e. when controllability only just holds.
- **Read the necessary conditions as sufficient**: step 1 used only "boundary point", never global
  minimality. An extremal can therefore be a local minimum, a local maximum or a saddle.
  Sufficiency needs separate conditions (the Jacobi condition, or existence of a solution of the
  HJB equation) — the subject of `c4-dp-lqr-lqg`.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R5)** Verify by direct differentiation that
$\lambda_v(t) = g^{-1}(\tan\theta_f\cos\theta - \sin\theta)$ from (32) satisfies the adjoint
equation $\dot\lambda_v = -(\lambda_x\cos\theta + \lambda_y\sin\theta)$, using $\dot\theta = -k$,
$\lambda_x = -k/g$ and $\lambda_y = -(k/g)\tan\theta_f$.
*Solution sketch*: the left-hand side is
$g^{-1}\dot\theta(-\tan\theta_f\sin\theta - \cos\theta) = (k/g)(\tan\theta_f\sin\theta + \cos\theta)$.
Substitute $\lambda_x$ and $\lambda_y$ into the right-hand side and check you get the same thing.
The point is that the two expressions must agree **for every $\theta$**.

**P2 (derivation, ★★, R5)** Derive (33) by integrating (31) and (25) all the way, and show that
energy conservation $v(t)^2 = v_0^2 + 2g\,y(t)$ follows from (31) and (33). Then check that in the
limit $v_0 \to 0$ we get $\theta_0 \to \pi/2$ and (33) becomes the cycloid
$x = R(\phi-\sin\phi)$, $y = R(1-\cos\phi)$ with $\phi = 2kt$ and $R = g/4k^2$.
*Solution sketch*: do $\int\cos^2\theta_t\,dt$ with the half-angle formula and
$\int\cos\theta_t\sin\theta_t\,dt$ as $\tfrac12\int\sin 2\theta_t\,dt$. For the energy, square
$v = (g/k)\cos\theta$ and expand $y$ from (33) using $\cos 2\theta = 2\cos^2\theta - 1$; watch the
$\cos^2\theta_0$ terms cancel.

**P3 (proof, ★★★, R3)** Generalise "at most one switch" from the double integrator. For
$\dot{x} = Ax + bu$, $\lvert u\rvert \le 1$, minimum time, show that when all eigenvalues of
$A \in \mathbb{R}^{n\times n}$ are **real** the number of switches is at most $n-1$. Why does the
bound fail when $A$ has complex eigenvalues?
*Solution sketch*: the strategy is to convert "number of zeros of the switching function" into
"number of zeros of a combination of real exponentials".
$s(t) = b^\top\lambda(t) = b^\top e^{-A^\top t}\lambda(t_f)$ has the form
$\sum_j p_j(t)e^{-\mu_j t}$ with polynomials $p_j$ and $\sum(\deg p_j + 1) \le n$. The key
inequality is an **analytic version of Descartes' rule**: such a real exponential polynomial has
at most $n-1$ real zeros (by induction plus Rolle's theorem — divide out $e^{\mu_1 t}$ and
differentiate to reduce the number of terms by one). With complex eigenvalues $s$ picks up
$\sin$ and $\cos$ and can have infinitely many zeros; minimum-time control of a harmonic
oscillator is the example.

**P4 (numerical, ★, R3)** For the double integrator $\dot x_1 = x_2$, $\dot x_2 = u$,
$\lvert u\rvert \le 1$, find the switching time $t_s$, the switching point, and the terminal time
$t_f$ of the minimum-time control taking $x(0) = (-2, -1)$ to the origin. Then apply the same
procedure to $x(0) = (1, 0)$ and check it against (19).
*Answer*: the switching curve is $x_1 = -\tfrac12 x_2\lvert x_2\rvert$. The point $(-2,-1)$ lies
to its left (at $x_2 = -1$ the curve is at $x_1 = 0.5$, while we are at $x_1 = -2$), so start with
$u = +1$. Substituting $x_1(t) = -2 - t + t^2/2$ and $x_2(t) = -1 + t$ into the lower branch
$x_1 = -x_2^2/2$ gives $t^2 - 2t - \tfrac32 = 0$, hence
$$
t_s = 1 + \tfrac12\sqrt{10} = 2.5811388301, \quad
  x(t_s) = \big(-1.25,\ \tfrac12\sqrt{10}\big), \quad
  t_f = 1 + \sqrt{10} = 4.1622776602
$$
(tolerance $10^{-9}$). From $x(0) = (1,0)$: $t_s = 1$, $t_f = 2$, $x(t_s) = (0.5, -1)$.
*Checks*: verify the switching point lies on the curve
($\lvert x_1 + \tfrac12 x_2\lvert x_2\rvert\rvert < 10^{-12}$) and that the terminal value of the
two analytically concatenated arcs satisfies $\lVert x(t_f)\rVert_\infty < 10^{-12}$. Each
$u = \pm 1$ arc is a quadratic polynomial, so no numerical integration is needed.

**P5 (implementation, ★★, R4)** Implement single shooting for the scalar LQ problem (22) and, for
$T = 1, 2, \dots, 25$, (i) measure $dr/dp$ by central finite differences and (ii) record the final
$\lvert r\rvert$ reached by Newton's method. Plot $\log\lvert dr/dp\rvert$ against $T$ and check
that the slope is $\sigma$ and the intercept is $\ln c$.
*Rubric*: (a) the measured slope matches $\sqrt2$ to within 1%; (b) $e^{\text{intercept}}$ matches
$0.1464466$ to within 1%; (c) you report the first $T$ at which $\lvert r\rvert < 10^{-6}$ becomes
unreachable and compare it with the prediction 17.08 from (24); (d) you check that loosening the
integrator tolerance beyond $10^{-12}$ hides the blow-up behind integration error, and you say so.

**P6 (counterexample, ★★, R1)** Show in **two different ways** that "satisfying the PMP implies
optimality" is false: (i) a concrete problem with several extremals of which only one is optimal,
and (ii) a problem with an abnormal extremal ($\lambda_0 = 0$) for which (3) carries no
information about the cost.
*Property checklist*: for (i), the easiest setting is a problem with a terminal constraint
reachable along several paths (e.g. a system moving on the unit circle where the target can be
reached clockwise or counter-clockwise) — you must be able to compare the two extremals' $J$
directly. For (ii), construct a problem whose terminal point lies **exactly** on the boundary of
the reachable set (e.g. $\dot x = u$, $\lvert u\rvert \le 1$, $T = 1$ fixed, $x(0) = 0$,
$x(1) = 1$ — the control is uniquely determined, so the solution is the same whatever $\ell$ is).
Properties to check: does $(\lambda_0, \lambda) \ne 0$ still hold, and can $\lambda_0$ be
normalised to 1?

**P7 (paper, ★★, R2 and R4)** Read §3–§4 of Betts 1998 and extract **four** practical weaknesses
the author attributes to indirect methods, saying for each which result of this lesson it
corresponds to (the conserved-quantity diagnostic of R2, the singular-arc detection of R3, the
conditioning of R4 — and one that this lesson does not cover). Then, from §3 of Hartl et al. 1995,
write in a single equation how (2) changes once state constraints are present.
*Rubric*: pass if the four weaknesses cover the categories "the switching structure must be known
in advance / the costate's initial guess has no physical meaning so it is hard to guess / the
condition number blows up / changing the constraints forces you to redo the derivation". A mere
"it is hard to implement" fails. For the state-constraint part, pass if you note that $\lambda$
becomes BV and a measure term $g_x^\top d\eta$ appears.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read with three passes, attacking questions 4, 5, 6 and 7 on the third.

1. **Sussmann & Willems, "300 years of optimal control: from the brachystochrone to the maximum
   principle" (1997, IEEE Control Systems Magazine)** — role: `standard`.
   <https://doi.org/10.1109/37.588098>
   What to read: all of it (14 pages). §V is the modern statement of the PMP, and §II–§IV walk
   through R5 of this lesson in historical order.
   Extra questions: (a) exactly where do the authors say the calculus of variations is not enough
   and the PMP is needed (which assumption breaks)? (b) Is the paper's sign convention the maximum
   or the minimum principle, and what must change to line it up with (2) and (3) of this lesson?
   (c) What extra information do the authors say the PMP gives for the brachistochrone that the
   calculus of variations does not?
2. **Hartl, Sethi & Vickson, "A survey of the maximum principles for optimal control problems with
   state constraints" (1995, SIAM Review)** — role: `survey`.
   <https://doi.org/10.1137/1037043>
   What to read: §2 (problem setting and constraint classification), §3 (direct vs indirect
   adjoining), §4 (examples).
   Extra questions: (a) the "direct" and "indirect" adjoining formulations give different
   $\lambda$ for the same problem — what transformation connects them? (b) What gets harder as the
   constraint order increases? (c) In what form does R2 (conservation of the Hamiltonian) survive
   when state constraints are present?
3. **Betts, "Survey of numerical methods for trajectory optimization" (1998, AIAA JGCD)** — role:
   `survey`. <https://doi.org/10.2514/2.4231>
   What to read: §2 (problem classes), §3 (indirect methods: shooting and multiple shooting),
   §4 (direct methods), §6 (comparison and recommendations).
   Extra questions: (a) quantify the author's recommendation of multiple shooting using (7) of
   this lesson. (b) Which of the 1998 recommendations have changed by 2026 (automatic
   differentiation, interior-point solvers, GPUs)? (c) Under what conditions is the author's claim
   that "indirect methods are more accurate" true?

**The ten fixed questions**: (1) What problem is solved, under what assumptions? (2) What exactly
could prior work not do? (3) Reduce the core idea to one equation. (4) What are the theoretical
guarantees, and **what is not guaranteed**? (5) What are the independent and dependent variables
and the baselines, and were the baselines tuned fairly? (6) Do the metrics match the claims, and
are variance and seeds reported? (7) What information needed for reproduction is missing? (8) If
the result were wrong, which assumption would you doubt first? (9) What are the computational and
memory complexity and the real-time behaviour? (10) What would you change to go beyond this paper
in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one notebook CPU core, under 2 minutes total,
under 200 MB of memory. numpy and scipy only (`solve_ivp`, `fsolve`/`root`). No simulator.

**Input data**: none. Both problems are specified by constants given in the lesson.
- Problem A (brachistochrone): $g = 9.81\,\mathrm{m/s^2}$, $v_0 = 1.0\,\mathrm{m/s}$,
  $(x_f, y_f) = (1.0,\ 0.5)\,\mathrm{m}$.
- Problem B (scalar LQ): in (22), $a = 1$, $q = 1$, $x_0 = 1$, $T \in \{1,\dots,30\}$.

**The task**: (i) solve problem A with the closed form (33); (ii) solve the same problem by single
shooting on the Hamiltonian system (20) (unknowns
$p = (\lambda_x, \lambda_y, \lambda_v(0), t_f) \in \mathbb{R}^4$, residual
$r = (x(t_f) - x_f,\ y(t_f) - y_f,\ \lambda_v(t_f),\ H(t_f))$) and compare with (i);
(iii) use problem B to measure the conditioning blow-up of (7) and (24); and (iv) show that
multiple shooting removes it.

**Acceptance criteria** — all four must hold to pass.

1. **The closed-form values.** Solving (33) for $(k, t_f)$ gives
   $$
   k = 2.9625143878\ \mathrm{s^{-1}}, \quad t_f = 0.4669260667\ \mathrm{s}, \quad
     \theta_0 = 1.2640177030, \quad \theta_f = -0.1192574876\ \mathrm{rad}
   $$
   (to within $10^{-8}$ relative error). Check: $v(t_f) = 3.2878564446\,\mathrm{m/s}$ must agree
   with $\sqrt{v_0^2 + 2gy_f} = \sqrt{10.81}$ to within $10^{-9}$.
2. **Shooting recovers the closed form.** With integrator tolerances `rtol=1e-12, atol=1e-14`,
   reach $\lVert r(p^*)\rVert_\infty < 10^{-12}$, and that $p^*$ must agree with the closed-form
   $$
   \lambda_x = -0.3019892342, \quad \lambda_y = 0.0361861911, \quad
     \lambda_v(0) = -0.1008662107, \quad t_f = 0.4669260667
   $$
   to within $\lVert\cdot\rVert_\infty < 10^{-10}$.
3. **Conserved quantities and control structure.** On a uniform grid of 1001 points over
   $[0, t_f]$: (a) $\max_t \lvert H(t)\rvert < 10^{-10}$ ($H \equiv 0$ from R2); (b) the residual
   of a least-squares line fitted to $\theta(t)$ satisfies
   $\max_t\lvert\theta(t) - (\theta_0 - kt)\rvert < 10^{-9}$ with the slope matching $-k$ to
   within $10^{-8}$ (the "affine in $t$" of R5); (c)
   $\max_t \lvert \cos\theta(t)/v(t) - \lvert\lambda_x\rvert \rvert < 10^{-10}$ (the conserved
   quantity of (29)).
4. **Blow-up and multiple shooting.** On problem B: (a) the line fitted to
   $\log\lvert dr/dp\rvert$ over $T = 5,\dots,20$ has slope matching $\sqrt2$ and
   $e^{\text{intercept}}$ matching $0.1464466$, each to within **1% relative error**; (b) the
   first $T$ at which single shooting fails to reach $\lvert r\rvert < 10^{-6}$ is $17 \pm 2$
   (the prediction (24) is 17.08); (c) with multiple shooting of segment length $\Delta = 2$
   ($N = \lceil T/\Delta\rceil$), the 2-norm of the per-segment transition matrix is
   **independent of $T$** and matches $e^{2\sqrt2} = 16.9188$ to within $10^{-4}$, and
   $\lVert r \rVert_\infty < 10^{-8}$ is reached up to $T = 100$.

**Baselines**: (i) the closed form (33) is the primary baseline for problem A. (ii) Additionally,
solve the same boundary value problem with `scipy.integrate.solve_bvp` and check that $t_f$ agrees
to within $10^{-7}$ (this needs a time reparameterisation — substitute $\tau = t/t_f$ and lift
$t_f$ to a parameter). (iii) The answer to problem B is closed-form via Riccati: as
$T \to \infty$, $p^* \to (a + \sigma)x_0 = 2.4142135624$ and the closed-loop pole is
$a - (a+\sigma) = -\sigma$.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| Shooting converges to $t_f < 0$, or $\theta$ passes $\pi$ | you picked the **maximising** branch of (3), not the minimising one — a branch cut of $\arctan$ | extract $\theta$ with $\operatorname{atan2}$ and assert $\partial^2 H/\partial\theta^2 > 0$ at every step |
| The residual stalls at $10^{-6}$ and will not go lower | the integrator tolerance is looser than the residual you demand | tighten `rtol` from $10^{-10}$ to $10^{-12}$ and watch the residual follow |
| $H$ is conserved at a constant $\ne 0$ instead of $0$ | the free-$t_f$ condition (4) is missing from the residual | check that the fourth component of $r$ is $H(t_f)$ |
| You dropped $\lambda_v(t_f) = 0$ and used only three unknowns, and the solution comes out as a one-parameter family | the terminal condition from $v(t_f)$ being free is missing — $\lambda_y$ is then undetermined | run from two different initial guesses and see whether the converged $\lambda_y$ differs (see the paragraph before (32)) |
| In problem B the conditioning does not grow with $T$ | you chose $q < -a^2$, so $\mu$ is purely imaginary (non-hyperbolic) | print $\sigma = \sqrt{a^2+q}$ first and confirm it is real |
| The finite-difference $dr/dp$ is noisy at large $T$ | $e^{\sigma T}$ is large, so round-off dominates the difference | use a step $h \sim \varepsilon^{1/3}$ and compare against the analytic (23) |

## Open problems

- **(open problem) What is the costate of a system with contact?** — this is where H1 breaks. If
  the mode schedule is **given in advance**, the costate's jump can be written with a saltation
  matrix; but when the mode sequence is itself a decision variable, there is no general,
  numerically stable way to apply the PMP. Current approaches:
  [Sussmann's 1999 hybrid maximum principle](https://doi.org/10.1109/cdc.1999.832814),
  [the complementarity transcription of Posa et al. 2014](https://doi.org/10.1177/0278364913506757).
  What is missing: complexity lower bounds as the number of modes grows combinatorially, and a
  criterion for when the gradient automatic differentiation returns at a non-smooth point is the
  correct costate.
- **(open problem) Certifying global optimality of an extremal** — the PMP gives only necessary
  conditions, and for nonlinear problems there is no general way to prove "this extremal is the
  global optimum". Current approaches: moment/SOS relaxations that build lower bounds on the value
  function, in the style of [Henrion & Korda 2014](https://doi.org/10.1109/TAC.2013.2283095), and
  [HJ reachability](https://doi.org/10.1109/CDC.2017.8263977). What is missing: both scale
  exponentially in the state dimension, so neither is usable for robots with $n \gtrsim 6$, and
  there is no practical **gap certificate** at robot scale.
- **(open problem) Automatic detection of singular arcs** — there is no algorithm that finds in
  advance where $s_i \equiv 0$, so indirect methods require a human to posit the switching
  structure. Sometimes no finite structure exists at all, as in Fuller's phenomenon
  ([Fuller 1963](https://doi.org/10.1080/00207216308937555)). Current approaches: numerical checks
  of the higher-order (Kelley and Goh) conditions and the empirical procedure in
  [Betts 1998](https://doi.org/10.2514/2.4231) §4. What is missing: a transcription that treats
  the number and location of singular intervals **as part of the problem being solved**.
- **(open problem) Can a learned model supply the costate's initial guess?** — the practical
  barriers to indirect methods are the conditioning of (7) and the fact that $\lambda(0)$ has no
  physical intuition behind it. Since the gradient of the value function *is* the costate
  ($\lambda = \partial V/\partial x$, `c4-dp-lqr-lqg`), learning an approximate value function to
  predict $\lambda(0)$ is an open avenue. What is missing: there is no **guarantee** that a
  learned $\lambda(0)$ lands inside Newton's basin of convergence, and the size of that basin
  itself shrinks like $e^{-\sigma T}$ by (7).

## Concept check

Run `rc quiz c4-pontryagin-indirect`. The quiz is for **concept checking only**; the real work is
the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: why (3) is written as a minimisation over $U$ rather than as
$\partial H/\partial u = 0$; the value of $H$ for an autonomous problem with free terminal time;
what actually bounds the number of bang-bang switches; whether the exponential conditioning of
single shooting is a property of the boundary value problem itself; and why the eigenvalues of the
linearised Hamiltonian system come in $\pm$ pairs.

## How to study this stage

1. **Fix the sign convention first (20 min)** — copy the notation table onto paper and mark that
   this lesson uses the **minimum** principle. Pontryagin's original and many papers use the
   maximum-principle convention, in which $\lambda$ has the opposite sign. Making this the first
   check whenever you open a paper removes half of all derivation mistakes.
2. **Build the adjoint equation by hand (80 min)** — reconstruct (9)→(13) of R2 with the text
   closed. The exchange of integration order (the line after (10)) is the only trick, and it is
   what produces the **definition** (11) of $\lambda$. Having done this computation once yourself,
   the backward pass of `c4-ilqr-ddp` and backpropagation will look like the same thing.
3. **Memorise only the strategy and three steps of the proof (70 min)** — of the six steps of R1,
   what to remember is "(1) lift the cost into the state to get a boundary-point problem,
   (3) the cone of needles is convex, (4) separating hyperplane". Steps 2, 5 and 6 are computation.
   Then read the four "deleting a hypothesis" paragraphs and summarise each in one line — those
   four lines are the map to the rest of C4 (contact, constraints, sufficiency).
4. **Solve bang-bang by hand, then check it numerically (60 min)** — rewrite (17)→(19) and solve
   P4 **analytically** (no numerical integration). Sketching the switching curve
   $x_1 = -\tfrac12 x_2\lvert x_2\rvert$ makes the contrast with the LQR feedback of the next
   lesson much sharper.
5. **See the blow-up yourself (100 min)** — do problem B of the reproduction task **first** (it is
   shorter than problem A). You have to produce the plot of $\log\lvert dr/dp\rvert$ rising as a
   straight line with your own hands for (7) to stick. Then solve problem A by single shooting and
   you will simultaneously see how accurate indirect methods are on a short horizon (residuals at
   the $10^{-16}$ level). **The two experiences are a pair** — doing only one leaves you
   misremembering either "indirect methods are useless" or "indirect methods are best".
6. **Read the papers as a contrast (150 min)** — read Sussmann & Willems first to place R5 in
   historical context, take Betts §3–§4 for "so why does practice use direct methods", and finish
   with Hartl et al. §3 for "how does (2) break when constraints appear". Write the one-page note
   per paper — **without exception**.
7. **End with what cannot be done (30 min)** — pick one of the four open problems and write a
   paragraph on why it is still open. The last two lessons of C4 (contact, robustness) return to
   two of them.

**Passing bar**: you can write (11)–(12) (the definition and derivation of the adjoint equation)
and (19) (the double-integrator solution) from a blank page, you can state the proof strategy of
R1 and the four "deleting a hypothesis" cases, you have code satisfying all four acceptance
criteria of the reproduction task, and you have notes on all three papers.
