---
id: c3-passivity-impedance
lang: en
title: Passivity, energy shaping and impedance control
summary: >-
  Control rewritten from the viewpoint of a robot that **exchanges energy** with its environment.
  The passivity of a manipulator is derived from the skew symmetry of $\tfrac12\dot{M} - C$, and
  why a feedback interconnection of passive systems is stable is treated at the level of proof.
  Energy shaping with damping injection and impedance control follow, and how a digital
  implementation destroys passivity is derived as a **closed-form boundary** and compared with the
  classical Colgate-Schenkel condition.
objectives:
  - Derive the passivity of a manipulator from the skew symmetry of $\tfrac12\dot{M}-C$ with no missing steps.
  - Explain why a feedback interconnection of two passive systems is stable and where that conclusion weakens.
  - Design an energy-shaping plus damping-injection controller and conclude convergence with LaSalle.
  - Compute the per-cycle energy of a sampled virtual wall in closed form and derive the passivity boundary.
  - Show numerically why the stability boundary and the passivity boundary differ, and which is more conservative.
tags: [nonlinear-control, passivity, impedance-control, energy-shaping, contact, research]
---

# Passivity, energy shaping and impedance control

## Setup and notation

The three previous lessons treated the robot **alone**: an equilibrium (Lyapunov), coordinates
(feedback linearisation) and the distance between trajectories (contraction) are all internal
matters. But manipulation is by definition **interaction with an environment**, and the model of
the environment is unknown. The one general tool for coupling stably to an unknown counterpart is
energy — passivity.

Assumed: Lagrangian dynamics and the structure of the mass matrix (`robotics-expert` M2 and M7, or
the research track's `c2` module), LaSalle's theorem from `c3-lyapunov-stability`, and transfer
functions and Nyquist plots for linear systems.

| Symbol | Meaning |
|---|---|
| $M(q)\ddot q + C(q,\dot q)\dot q + g(q) = \tau + \tau_{\text{ext}}$ | manipulator dynamics, $M \succ 0$, $g = \partial U/\partial q$ |
| $C(q,\dot q)$ | the centrifugal/Coriolis matrix — the standard **Christoffel** choice is used |
| $U(q)$ | gravitational potential energy |
| $V = \tfrac12\dot q^\top M\dot q + U(q)$ | total energy (the storage function) |
| one-port | a pair of force $f$ and velocity $v$; the energy into the port is $\int f v\,dt$ |
| passive | there is a storage function $V \ge 0$ with $\dot V \le f v$ (it never returns more than it was given) |
| $Z(s)$ | impedance $F(s)/V(s)$; passive $\iff$ $Z$ positive real, in particular $\operatorname{Re}Z(j\omega)\ge0$ |
| $K, B$ | stiffness and damping of the virtual wall (numbers inside the controller) |
| $b$, $m$ | the **physical** damping and mass of the device |
| $T$ | the sampling period; $\theta := \omega T$ |

The two running examples are ⓐ a two-link planar manipulator (R2, R3) and ⓑ a **virtual wall**
implemented on a 1-DOF haptic device (R5).

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (passivity theorem and stability of the interconnection) [D3]** — interconnecting two
  passive systems by negative feedback ($u_1 = -y_2$, $u_2 = y_1$) gives a passive system whose
  storage function is $V_1+V_2$. If one of them is **output strictly passive** and
  zero-state detectable, the origin of the interconnection is asymptotically stable.
- **R2 (passivity of a manipulator) [D2]** — with the Christoffel choice of $C$, the matrix
  $\tfrac12\dot M - C$ is **skew-symmetric**, so $V = \tfrac12\dot q^\top M \dot q + U$ satisfies
  $$
  \dot V = \dot q^\top \tau + \dot q^\top \tau_{\text{ext}} \tag{1}
  $$
  That is, the robot is **exactly passive** — indeed lossless — at the $(\tau, \dot q)$ port.
- **R3 (energy shaping and damping injection) [D2]** — on a fully actuated system,
  $$
  \tau = g(q) - K_p (q - q_d) - K_d \dot q \tag{2}
  $$
  makes the shaped energy
  $V_d = \tfrac12 \dot q^\top M \dot q + \tfrac12 (q-q_d)^\top K_p (q-q_d)$ satisfy
  $\dot V_d = -\dot q^\top K_d \dot q \le 0$, and LaSalle gives $q \to q_d$, $\dot q \to 0$.
  The point is **replacing** $U$ by a desired $U_d$ while cancelling gravity. On an underactuated
  system the same move requires solving the matching equations (IDA-PBC). **[D1]**
- **R4 (impedance control and coupled stability) [D2]** — a controller realising a target
  impedance $M_d\ddot e + B_d \dot e + K_d e = -f_{\text{ext}}$ (with $e = q - q_d$) is stable
  against **any passive** environment — but only if the controller itself is passive at the port.
  For a linear 1-DOF case that condition is $\operatorname{Re}Z_c(j\omega) \ge 0$, and shaping the
  mass ($M_d \ne m$) requires force measurement and can break passivity.
- **R5 (energy boundary of a sampled virtual wall) [D2]** — for a port made of a zero-order-hold
  virtual wall $F_k = -Kx_k - B(x_k - x_{k-1})/T$ plus physical damping $b$, a sinusoidal motion
  $x(t) = A\sin(\omega t + \varphi)$ gives the energy flowing **into** the port per cycle in
  **closed form**:
  $$
  W = A^2 N\left\{\sin^2\!\tfrac{\theta}{2}\left[-K + \tfrac{2B}{T}\cos\theta\right]
    + \frac{b\,\theta^2}{2T}\right\},\qquad \theta = \omega T,\ N = \frac{2\pi}{\theta} \tag{3}
  $$
  so passivity against sinusoidal motions is equivalent to
  $$
  b \;\ge\; g(\theta) := \frac{2T}{\theta^2}\sin^2\!\frac{\theta}{2}
    \left[K - \frac{2B}{T}\cos\theta\right] \quad \forall \theta \in (0,\pi]. \tag{4}
  $$
  The limit $\theta\to0$ is $KT/2 - B$ and $\theta = \pi$ gives $2KT/\pi^2 + 4B/\pi^2$. The
  classical Colgate-Schenkel sufficient condition $b > KT/2 + \lvert B\rvert$ **coincides exactly**
  with the maximum of (4) for $B \le 0$ and is conservative for $B>0$ (numerically: with
  $K=2000$, $T=1$ms and $B=0.5$, $\max_\theta g = 0.85568$ against
  $KT/2+\lvert B\rvert = 1.5$).

## Derivation

### R2 — why a manipulator is passive at its port

**Step 1 (the skew structure).** With $C$ defined through Christoffel symbols,
$C_{ij} = \sum_k \tfrac12\left(\frac{\partial M_{ij}}{\partial q_k} + \frac{\partial M_{ik}}{\partial q_j}
- \frac{\partial M_{kj}}{\partial q_i}\right)\dot q_k$, and since
$\dot M_{ij} = \sum_k \frac{\partial M_{ij}}{\partial q_k}\dot q_k$,

$$
\left(\tfrac12\dot M - C\right)_{ij}
  = \sum_k \tfrac12\left(\frac{\partial M_{kj}}{\partial q_i} - \frac{\partial M_{ik}}{\partial q_j}\right)\dot q_k
$$

and swapping $i \leftrightarrow j$ flips the sign of the bracket (using the symmetry
$M_{kj}=M_{jk}$). So $S := \tfrac12\dot M - C$ is skew-symmetric and in particular

$$
\dot q^\top \left(\tfrac12 \dot M - C\right)\dot q = 0 \qquad \text{for all } \dot q. \tag{5}
$$

**Numerical check**: on a two-link planar arm, drawing $q$ and $\dot q$ at random 2000 times and
computing $\dot M$ by central differences ($h=10^{-7}$) gives
$\max\lVert S + S^\top\rVert_{\max} = 5.6\cdot10^{-9}$ and
$\max\lvert \dot q^\top S \dot q\rvert = 3.4\cdot10^{-8}$ — at the level of the difference error.

**Step 2 (differentiating the energy).** Differentiate
$V = \tfrac12\dot q^\top M\dot q + U(q)$ and substitute the dynamics:

$$
\dot V = \dot q^\top M\ddot q + \tfrac12 \dot q^\top \dot M \dot q + \dot q^\top \frac{\partial U}{\partial q}
  = \dot q^\top(\tau + \tau_{\text{ext}} - C\dot q - g) + \tfrac12\dot q^\top \dot M\dot q + \dot q^\top g,
$$

where $g = \partial U/\partial q$ **cancels** the gravity term and (5) removes the $C$ term, leaving
(1). The robot neither creates nor loses energy (absent friction). The definition of passivity
$\dot V \le \dot q^\top \tau$ holds with equality, so the robot is **lossless**.

**Where the assumptions break**: ⓐ if $C$ is written in any way other than the Christoffel choice,
(5) fails — many $C$ give the same $M\ddot q + C\dot q$, and only the Christoffel one is skew in
this sense. ⓑ joint flexibility, gearbox friction or actuator dynamics **move the port** away from
$(\tau,\dot q)$, and passivity seen from the motor side must be shown separately. ⓒ a discrete
implementation destroys passivity — that is R5.

### R3 — energy shaping and damping injection

**Step 1 (swap the energy).** The goal is to make the system behave as one with a desired
potential $U_d(q)$ whose minimum is at $q_d$. In (2) the term $g(q)$ **cancels** the real gravity
and $-K_p(q-q_d)$ **inserts** $-\partial U_d/\partial q$ with
$U_d = \tfrac12(q-q_d)^\top K_p (q-q_d)$. What is left, $-K_d\dot q$, is damping injection.

**Step 2 (differentiating the shaped energy).** Repeating the computation of R2 on
$V_d = \tfrac12\dot q^\top M\dot q + U_d(q)$, now substituting (2) for $\tau$,

$$
\dot V_d = \dot q^\top\left(\tau - g + \frac{\partial U_d}{\partial q}\right)
  = \dot q^\top\left(-K_p(q-q_d) - K_d\dot q + K_p(q-q_d)\right) = -\dot q^\top K_d \dot q \le 0. \tag{6}
$$

**Step 3 (convergence by LaSalle).** $V_d$ is positive definite about $(q_d, 0)$ and its sublevel
sets are bounded when $K_p \succ 0$. Also $\dot V_d = 0 \iff \dot q = 0$, and a solution with
$\dot q \equiv 0$ must have $\ddot q = 0$, so substituting (2) into the dynamics gives
$K_p(q-q_d) = 0$, i.e. $q = q_d$. Since that point is the only solution remaining in $E$, R3
(Barbashin-Krasovskii) of `c3-lyapunov-stability` gives **asymptotic stability**.

**Numerical check**: on the two-link arm with $K_p = \operatorname{diag}(25,16)$,
$K_d = \operatorname{diag}(10,6)$, $q_0 = (-1.0,\ 1.5)$ and $q_d = (0.3,\ -0.6)$, integrating 15
seconds with RK4 ($\Delta t = 10^{-3}$) gives
$\lvert q - q_d\rvert_\infty = 2.9\cdot10^{-12}$, and the energy balance
$\lvert V_d(t) - V_d(0) + \int_0^t \dot q^\top K_d\dot q\,ds\rvert$ peaks at $7.0\cdot10^{-4}$,
a relative error of $1.2\cdot10^{-5}$ against $V_d(0) = 56.4$ (integration and quadrature error).

**Where the assumptions break**: (2) presumes **full actuation**. With fewer inputs than states
even cancelling $g$ is impossible, and inserting a desired energy requires $U_d$ to satisfy the
**matching equations** (a PDE) rather than being arbitrary — solving that PDE is the body of
IDA-PBC (Ortega et al. 2002). Also (6) assumes the model's $g$ is exact: with
$\hat g \ne g$ a steady-state error of $K_p^{-1}(\hat g - g)$ remains, and erasing that error by
adaptation is `c3-adaptive-control`.

### R5 — per-cycle energy of a sampled virtual wall (closed form)

**Setting.** Let $x$ be the position of a 1-DOF device with port variables $(f, v=\dot x)$. The
controller samples $x$ every $T$ and **holds** the force for the period:

$$
F_k = -K x_k - \frac{B}{T}\left(x_k - x_{k-1}\right), \qquad t \in [kT, (k+1)T). \tag{7}
$$

Velocity is not measured but formed from the backward difference of sampled positions (the
standard implementation on real haptic devices). The port is "virtual wall plus physical damping
$b$", and the energy the user supplies is computable once the motion is prescribed.

**Step 1 (prescribe the motion and integrate the energy).** Put
$x(t) = A\sin(\omega t + \varphi)$ and write the energy into the port per cycle. The conservative
elements (virtual spring, kinetic energy) return to where they started after a cycle, so

$$
W = \int_{\text{1 cycle}}\left(-F\,v + b\,v^2\right)dt
  = \underbrace{\sum_k \left(-F_k\right)\left(x_{k+1}-x_k\right)}_{\text{work of the held force}}
    + \underbrace{\pi b A^2\omega}_{\int b v^2}. \tag{8}
$$

(Since $F$ is constant on each interval, $\int F v\,dt = F_k \Delta x_k$ **exactly** — that is why
a closed form exists.)

**Step 2 (both sums by trigonometric identities).** Let $\theta := \omega T$ divide one cycle into
an integer $N = 2\pi/\theta$ samples. For $x_k = A\sin(\theta k + \varphi)$ the standard sums

$$
\sum_{k=1}^{N} x_k x_{k+1} = \frac{A^2N}{2}\cos\theta, \qquad \sum_{k=1}^N x_k^2 = \frac{A^2N}{2}
$$

give the spring term

$$
\sum_k K x_k(x_{k+1}-x_k) = \frac{KA^2N}{2}(\cos\theta - 1) = -K A^2 N \sin^2\frac{\theta}{2}.
$$

For the damping term, the difference
$d_k := x_k - x_{k-1} = 2A\sin\frac{\theta}{2}\cos\!\left(\theta(k-\tfrac12)+\varphi\right)$ has
amplitude $2A\sin\frac\theta2$, and the same sums give

$$
\sum_k \frac{B}{T} d_k\,d_{k+1} = \frac{B}{T}\cdot\frac{(2A\sin\frac\theta2)^2 N}{2}\cos\theta
  = \frac{2BA^2N}{T}\sin^2\frac{\theta}{2}\cos\theta.
$$

Adding $\pi b A^2\omega = b A^2 N\theta^2/(2T)$ (from $\pi = N\theta/2$ and $\omega = \theta/T$)
gives (3). The phase $\varphi$ **drops out** — it is a full-cycle average.

**Step 3 (the passivity condition).** Requiring $W \ge 0$ for every $\theta \in (0,\pi]$ and every
$A$ cancels $A^2$ and $N>0$ and leaves (4). Two limits carry the meaning:

$$
\lim_{\theta\to0} g(\theta) = \frac{KT}{2} - B, \qquad
  g(\pi) = \frac{2KT}{\pi^2} + \frac{4B}{\pi^2}. \tag{9}
$$

The $KT/2$ in the first limit is the **negative damping created by sampling**: the held force acts
half a period late and injects $K A^2 \theta^2/4$ per cycle, which looks like an equivalent damping
of $-KT/2$. The $-B$ is the part where backward-difference damping **helps** at low frequency, and
because of $\cos\theta$ that sign flips and it **hurts** as $\theta$ approaches $\pi$.

**Numbers (all produced by running it, $T = 1$ms)**

| $K$ | $B$ | $\max_\theta g$ (at $\theta$) | $KT/2 - B$ | $KT/2+\lvert B\rvert$ |
|---|---|---|---|---|
| 2000 | 0 | $1.00000$ ($\theta\to0$) | 1.0000 | 1.0000 |
| 2000 | $+0.5$ | $0.85568$ ($0.648\pi$) | 0.5000 | 1.5000 |
| 1000 | $+0.5$ | $0.52506$ ($0.742\pi$) | 0.0000 | 1.0000 |
| 2000 | $+1.0$ | $1.05012$ ($0.742\pi$) | 0.0000 | 2.0000 |
| 2000 | $-0.5$ | $1.50000$ ($\theta\to0$) | 1.5000 | 1.5000 |

The closed form (3) agrees with direct summation to a relative error below $10^{-6}$ (for
$K=2000$, $B=0.5$, $N=8$, $b=1$: direct $952.6815$, closed form $952.6825$).

**The stability boundary and the passivity boundary are different.** Closing the same virtual wall
**with no environment** (the device alone), the critical damping at which the spectral radius of
the discrete transition matrix reaches 1 is numerically

$$
b_{\text{stab}} = \max\left(0,\ \frac{KT}{2} - B\right) \tag{10}
$$

($K=2000, B=0$: $0.99983$ against $1$; $K=2000, B=0.5$: $0.50042$ against $0.5$;
$K=1000, B=0.5$: $0.00031$ against $0$). Hence

$$
\underbrace{\frac{KT}{2}-B}_{\text{stable against that one environment}}
  \;\le\; \underbrace{\max_\theta g(\theta)}_{\text{passive against sinusoidal motions}}
  \;\le\; \underbrace{\frac{KT}{2}+\lvert B\rvert}_{\text{Colgate-Schenkel sufficient condition}} \tag{11}
$$

and all three **coincide** for $B\le0$. The middle value probes with sinusoids only, so it is a
**lower** bound on the true passivity threshold while the right-hand side is an **upper** bound
(motions with harmonics can extract more energy). What this means in practice: demanding passivity
(safe however a human pushes) caps the stiffness $K$ at about $2b/T$, while demanding stability
against one particular environment allows a higher stiffness — but **pushing differently can
destabilise it**. That trade is the Z-width of haptics (Colgate & Brown 1994).

**Where the assumptions break**: (3) assumes ⓐ a linear virtual wall (permanent contact),
ⓑ sinusoidal motion, ⓒ no quantisation or delay, and ⓓ that $\omega T$ divides a cycle into an
integer number of samples. A real wall is **nonlinear**, switching between contact and free motion
(the entry instant falls between samples and injects extra energy), and quantisation and
communication delay increase the negative damping further. So even the right-hand side of (11) can
be optimistic on a real device.

## Proof sketch

### R1 — feedback interconnection of passive systems

**Hypotheses** H1: each $\Sigma_i$ is passive with a storage function $V_i \ge 0$, i.e.
$\dot V_i \le u_i^\top y_i$. H2: the interconnection is $u_1 = -y_2 + e$, $u_2 = y_1$ (negative
feedback). H3 (for asymptotic stability): $\Sigma_1$ is output strictly passive
($\dot V_1 \le u_1^\top y_1 - \rho(\lvert y_1\rvert)$ with $\rho$ positive definite) and $\Sigma_2$
is zero-state detectable ($y_2 \equiv 0$ with $u_2 \equiv 0 \Rightarrow x_2 \to 0$).
**Conclusion** C: with $e=0$ the sum $V=V_1+V_2$ is non-increasing, so the origin is stable, and
under H3 it is asymptotically stable.

**Strategy**: add the energies. The whole content is that the **cross terms cancel exactly**.

1. Set $V := V_1 + V_2$ and add the two inequalities of H1:
   $\dot V \le u_1^\top y_1 + u_2^\top y_2$.
2. Substituting H2,
   $u_1^\top y_1 + u_2^\top y_2 = (-y_2+e)^\top y_1 + y_1^\top y_2 = e^\top y_1$.
   **The $y_1^\top y_2$ terms cancel** — that one line is the whole passivity theorem.
3. So with $e \equiv 0$, $\dot V \le 0$ and R1 of `c3-lyapunov-stability` gives stability. With
   $e \ne 0$, $\dot V \le e^\top y_1$ gives $L_2$ stability (a finite gain).
4. (Asymptotic) H3 gives $\dot V \le -\rho(\lvert y_1\rvert)$, so LaSalle yields $y_1 \to 0$; then
   $y_1 = -u_2 \to 0$ and detectability of $\Sigma_2$ give $x_2 \to 0$, and from
   $u_1 = -y_2 \to 0$ detectability of $\Sigma_1$ gives $x_1\to0$.

**Remove a hypothesis**: drop **non-negativity of the storage function** in H1 and step 1
collapses — a system allowed to go into energy debt passes that debt to its partner in the
interconnection. Without output strict passivity (H3) the conclusion stops at stability and gives
no convergence (two lossless systems interconnected oscillate forever). And if the environment is
**not passive** — a human injecting energy, another controller, a powered assist — the theorem does
not apply at all, which is the most common practical failure of passivity-based design.

Technical steps omitted: differentiability of the storage function and the precise definition of
zero-state detectability (Khalil ch.6 and ch.14.2, Colgate & Hogan 1988 §3).

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Prove componentwise that $\tfrac12\dot M - C$ is skew for the
Christoffel choice of $C$. Then say what happens to (5) if $C$ is replaced by $C' = C + S'$ with a
non-zero $S'$ satisfying $S'\dot q = 0$.
*Solution sketch*: repeat the component computation of step 1, calling $M_{kj}=M_{jk}$ explicitly.
$C'$ leaves the dynamics unchanged but (5) becomes
$\dot q^\top(\tfrac12\dot M - C')\dot q = -\dot q^\top S'\dot q$, which is generally non-zero —
**the passivity proof depends on the choice of $C$.**

**P2 (derivation, ★★★, R5)** Derive (3). Compute the two trigonometric sums
$\sum x_kx_{k+1}$ and $\sum x_k^2$ directly, and say why the difference $d_k$ has amplitude
$2A\sin(\theta/2)$. Point to the step where the phase $\varphi$ disappears.
*Solution sketch*: use $\sin a \sin b = \tfrac12[\cos(a-b)-\cos(a+b)]$ and
$\sum_k \cos(2\theta k + c) = 0$ (since $\theta N = 2\pi$). For $d_k$, fold
$\sin(\theta k+\varphi) - \sin(\theta(k-1)+\varphi)$ with the product formula. Both sums are
independent of $\varphi$, so it drops out in step 2.

**P3 (numerical, ★, R5)** With $K = 2000$ N/m and $T = 1$ ms, find $\max_\theta g(\theta)$ and the
maximising $\theta$ for ⓐ $B=0$, ⓑ $B=+0.5$, ⓒ $B=-0.5$.
*Answers*: ⓐ $1.00000$ at $\theta\to0$ ⓑ $0.85568$ at $\theta = 2.03531\,\text{rad} = 0.648\pi$
ⓒ $1.50000$ at $\theta\to0$. Tolerance $10^{-4}$. Check: ⓐ and ⓒ must equal $KT/2-B$ from (9), and
ⓑ must lie **strictly inside** $(KT/2-B,\ KT/2+\lvert B\rvert) = (0.5,\ 1.5)$.

**P4 (numerical, ★, R3)** With $K_p = \operatorname{diag}(25,16)$ and a gravity model error
$\hat g = g + \epsilon$ where $\epsilon = (0.5, -0.2)^\top$ N·m, find the steady-state error
$q_\infty - q_d$ of (2).
*Answer*: $K_p^{-1}\epsilon = (0.02,\ -0.0125)^\top$ rad (tolerance $10^{-9}$). Check: at steady
state $\ddot q = \dot q = 0$ in (2) and the dynamics give $K_p(q-q_d) = \hat g - g$.

**P5 (implementation, ★★, R4·R5)** Implement a 1-DOF virtual wall ⓐ in continuous time, ⓑ with ZOH
sampling and ⓒ with ZOH plus a one-step delay, and plot the stable region in the $(K, b)$ plane.
*Rubric*: ⓐ is stable for every $K>0$ ⓑ reproduces the boundary of (10) to within 1% ⓒ has a more
conservative boundary (delay increases the negative damping) ⓓ plots all three on one figure with
the axis normalised by $KT$.

**P6 (counterexample, ★★, R1)** Refute the claim that "an impedance controller is passive, so it
is stable against any environment", with ① an environment that is not passive and ② an environment
that is passive but where the **implementation** is not.
*Property checklist*: ① attaching a human, another controller or a powered assist (an energy
source) at the port breaks H1 of R1. ② a digital implementation with $b < \max_\theta g$ from
(11) — energy is injected even against a passive spring-mass. Exhibiting a frequency where
$\operatorname{Re}Z_c(j\omega) < 0$ completes it.

**P7 (paper, ★★, R4·R5)** Read Colgate & Schenkel 1997 and Colgate & Hogan 1988 and state ⓐ what
each paper claims stability **about** (one environment versus the whole class), ⓑ the consequence
of that difference for design freedom (the cap on $K$), ⓒ two quantities the authors do not
measure that block reproduction.
*Rubric*: naming "port passivity is a guarantee against the whole class of environments and its
price is a stiffness cap" passes. Naming friction, quantisation or the velocity-estimation scheme
among the missing items earns extra credit.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes and attack questions 4, 5, 6, 7 in the third.

1. **Hogan, "Impedance control: an approach to manipulation" (1985, ASME JDSMC)**
   — role: `seminal`. <https://doi.org/10.1115/1.3140713>
   What is verified is the 1985 JDSMC version of Parts II and III (Part I is ACC 1984).
   Extra questions: ⓐ On what grounds does the author argue that neither position nor force
   control suffices — what is assumed unknown about the environment? ⓑ What measurement does mass
   shaping ($M_d \ne m$) require, and at what cost?
2. **Colgate & Hogan, "Robust control of dynamically interacting systems" (1988, Int. J. Control)**
   — role: `seminal`. <https://doi.org/10.1080/00207178808906161>
   Extra questions: ⓐ Write a paragraph on how to read the coupled-stability condition off a
   Nyquist plot. ⓑ Give two manipulation tasks in which the assumption "the environment is
   passive" fails.
3. **Colgate & Schenkel, "Passivity of a class of sampled-data systems: application to haptic
   interfaces" (1997, J. Robotic Systems)** — role: `standard`.
   <https://doi.org/10.1002/(SICI)1097-4563(199701)14:1<37::AID-ROB4>3.0.CO;2-V>
   The original of the reproduction task. Write their condition and our (4) side by side **in the
   same symbols**.
   Extra questions: ⓐ Is their condition necessary or sufficient, and over which class of motions
   is the verdict taken? ⓑ Can you explain why, for $B>0$, the maximum of our (4) is below
   $KT/2+\lvert B\rvert$?

**The ten fixed questions**: (1) which problem under which assumptions (2) what exactly earlier
work could not do (3) the core idea in one equation (4) what is guaranteed and **what is not**
(5) independent and dependent variables and baselines, fairly tuned (6) do the metrics match the
claim, are variance and seeds reported (7) what is missing for reproduction (8) the first
assumption to doubt if the result is wrong (9) computational and memory complexity and real-time
feasibility (10) what you would change to go beyond it in a year.

## Reproduction task

**Tier R2 (re-implementation).** Budget: laptop CPU under ten minutes, numpy only (no SDP needed).
The targets are ⓐ the 1-DOF virtual wall (criteria 1-3) and ⓑ the two-link manipulator
(criterion 4). There is no input data.

**Acceptance criteria (all four)**

1. **Stability boundary**: build the discrete transition matrix of the ZOH virtual wall plus
   physical damping, and for $(K,B) \in \{500,1000,2000\}\times\{0,\ 0.5\}$ find by bisection the
   $b$ at which the spectral radius reaches 1, matching (10) **within 1% relative**. Reference
   values: $(2000,0) \to 0.99983$, $(2000,0.5) \to 0.50042$, $(1000,0.5) \to 0.00031$,
   $(1000,0) \to 0.49996$, $(500,0) \to 0.24999$.
2. **Closed-form check**: compute the per-cycle energy ⓐ by direct integration ($\ge 200$
   substeps per period) and ⓑ from (3), agreeing **within $10^{-5}$ relative**. Check at least
   three $(K,B,N,b)$ combinations, one of which has $B<0$. Reference: at
   $(K,B,N,b) = (2000,0.5,8,1)$, direct $952.6815$ and closed form $952.6825$.
3. **Ordering of the three boundaries**: compute $\max_\theta g(\theta)$ numerically over a
   $(K,B)$ grid and check that the ordering
   $KT/2-B \le \max_\theta g \le KT/2+\lvert B\rvert$ of (11) holds at **every** grid point, and
   that all three agree to within $10^{-6}$ for $B \le 0$. At $B = +0.5$ and $K=2000$,
   $\max_\theta g = 0.85568 \pm 10^{-4}$ (maximiser $\theta = 0.648\pi$).
4. **The manipulator side**: ⓐ over $10^3$ random $(q,\dot q)$,
   $\max\lVert S+S^\top\rVert_{\max} < 10^{-7}$ (central differences, $h=10^{-7}$) ⓑ integrating
   the controller (2) for 15 s with RK4 ($\Delta t \le 10^{-3}$) gives
   $\lvert q-q_d\rvert_\infty < 10^{-9}$ and an energy-balance **relative** error below $10^{-4}$
   (reference: $2.9\cdot10^{-12}$ and $1.2\cdot10^{-5}$).

**Baselines**: ⓐ the continuous-time implementation, which must be stable for every $K>0$ and
$b\ge0$ (the control group that isolates discretisation as the cause); ⓑ the Colgate-Schenkel
sufficient condition $b>KT/2+\lvert B\rvert$, the upper bound of criterion 3; ⓒ the reference
numbers of criteria 1, 2 and 3.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| The stability boundary comes out **twice** that of (10) | virtual damping implemented with the continuous velocity instead of $B(x_k-x_{k-1})/T$ | set $B=0$ first and check that the boundary is $KT/2$ |
| Direct integration in criterion 2 disagrees | the force was **recomputed** inside the interval (violating ZOH) | print $F$ within one interval and confirm it is constant |
| $\max_\theta g$ exceeds $KT/2+\lvert B\rvert$ | wrong sign of $\cos\theta$ or wrong $2B/T$ coefficient | check that the $\theta\to0$ limit is $KT/2+\lvert B\rvert$ for $B<0$ |
| Criterion 4ⓐ stalls around $10^{-5}$ | $\dot M$ taken by forward difference, or $h$ too large | switch to central differences with $h=10^{-7}$ and vary $h$ by 10 to see the error scale like $h^2$ |
| The energy balance diverges | the dissipation integral was accumulated with Euler | switch to Simpson quadrature and halve $\Delta t$ to confirm |

## Open problems

- **(open problem) Passivity guarantees for learned variable impedance** — varying the impedance
  with the task helps performance, but time-varying gains **can inject energy** (a growing $K_d$
  increases the storage function). Current approaches: learning impedance by reinforcement
  learning ([Buchli et al. 2010](https://doi.org/10.15607/RSS.2010.VI.020)), and energy tanks that
  account for the injection. The gap: guaranteeing passivity **by construction** over a whole
  learned policy while quantifying the performance lost.
- **(open problem) Passivity of a port with delay and communication** — teleoperation injects
  energy through the round-trip delay. Wave variables buy passivity independent of the delay
  ([Niemeyer & Slotine 1991](https://doi.org/10.1109/48.64895)) at the cost of transparency. The
  gap: the achievable frontier between passivity and transparency under variable delay and packet
  loss.
- **(open problem) Theoretical limits of the realisable impedance range (Z-width)** — the **exact**
  boundary of the $(K,B)$ region that can be implemented passively, with sampling, quantisation,
  friction and sensor noise acting together, is unknown. Current approaches: the experimental
  Z-width of [Colgate & Brown 1994](https://doi.org/10.1109/ROBOT.1994.351077) and partial closed
  forms such as (4) in this lesson. The gap: a boundary that includes quantisation and the
  nonlinear contact switch.
- **(open problem) Energy shaping for underactuated systems** — the matching equations of IDA-PBC
  are a PDE with no general solution. Current approaches: the constructive solutions of
  [Ortega et al. 2002](https://doi.org/10.1109/TAC.2002.800770) and case-by-case solutions for
  special structures (nonholonomic and walking systems). The gap: characterising which energies can
  be shaped on systems whose contact changes — it returns in `s3-legged-underactuated`.

## Concept check

Take it with `rc quiz c3-passivity-impedance`. The quiz is **for concept checking only**; the real
work is the problem set and the reproduction task above (`lesson-standard.md` §4). Four questions
ask: which structure is decisive in proving a manipulator passive; the size of the equivalent
negative damping created by a ZOH virtual spring; whether stability against one environment implies
stability against all passive ones; and what $\dot V_d$ is under energy shaping with damping
injection.

## How to study this stage

1. **Write the skew identity out componentwise once (40 min)** — solve P1 first. Once you have seen
   **why** the Christoffel choice is special, every later passivity argument reads as a repetition
   of the same cancellation.
2. **Check the energy balance in code (40 min)** — implement (2) and watch
   $V_d(t) - V_d(0) + \int\dot q^\top K_d\dot q$ sit at zero **numerically**. That single check
   catches every sign error.
3. **Memorise only step 2 of R1 (20 min)** — the line where the cross term $y_1^\top y_2$ cancels.
   The rest of the passivity theorem is Lyapunov and LaSalle reused.
4. **Implement the virtual wall three times (90 min)** — continuous, then ZOH, then ZOH with delay.
   Watch criterion 1 of the reproduction task land on $KT/2 - B$, and watch the delay make it
   worse. This is the step where **digital implementation destroys passivity** becomes something
   you have felt.
5. **Derive (3) from blank paper (90 min)** — P2. The two trigonometric sums are the whole thing,
   and the point is that the work of the held force falls out exactly as $F_k\Delta x_k$. When the
   derivation is done, verify the two limits of (9) yourself.
6. **Plot the three boundaries on one figure (60 min)** — criterion 3. Sweep $B$ into negative
   values and watch the three lines coincide for $B\le0$ and separate for $B>0$. That picture is
   the conclusion of this lesson.
7. **Read the papers for "a guarantee about what" (150 min)** — Hogan is about the relation,
   Colgate & Hogan about the whole class of environments, Colgate & Schenkel about the digital
   implementation. Tabulate how the **scope** of the guarantee differs and write the one-page note
   per paper.

**Passing bar**: you can derive (1), (6) and (3) from memory, explain numerically why the stability
and passivity boundaries differ, and you have code meeting all four acceptance criteria plus
one-page notes on the three papers.
