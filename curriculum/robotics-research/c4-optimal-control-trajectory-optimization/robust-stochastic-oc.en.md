---
id: c4-robust-stochastic-oc
lang: en
title: Robust and stochastic optimal control
summary: >-
  Set the two ways of handling uncertainty side by side: as a worst case and as a distribution.
  Treat at proof level the fact that the zero sublevel set of the viscosity solution of the HJI
  variational inequality is the reachable set, and derive the reduction that, when an additive
  disturbance enters through the same channel as the control, the robust set is **exactly the
  nominal set with a reduced control bound** — which yields an analytic oracle. Show numerically
  how much performance robustness costs in the minimax game Riccati equation and where the
  $\mathcal{H}_\infty$ performance limit lies, and confirm by Monte Carlo that certainty
  equivalence breaks under multiplicative noise and the gain shrinks. Finally, carry the recursive
  feasibility of the previous lesson over to the disturbed case with tube MPC.
objectives:
  - Reconstruct, as a proof sketch, the HJI variational inequality and the fact that the zero sublevel set of its viscosity solution is the reachable set.
  - Derive, and verify analytically, that under an additive same-channel disturbance the robust reachable set equals the nominal set with a reduced control bound.
  - Derive the minimax game Riccati equation and explain why the solution disappears below a critical $\gamma$.
  - Derive the failure of certainty equivalence under multiplicative noise and confirm the gain reduction numerically.
  - Explain how tube MPC separates the nominal trajectory from the error set and tightens the constraints.
tags: [optimal-control, robust-control, reachability, hji, minimax, tube-mpc, research]
---

# Robust and stochastic optimal control

## Setup and notation

The previous six lessons assumed the model was **exact**. `c4-dp-lqr-lqg` showed the price of that
assumption through Doyle 1978, and `c4-mpc` left "recursive feasibility under model error" as its
open problem 3. This lesson is the answer to that question. There are two ways to handle
uncertainty — the **worst case** (see it as a set and solve a game) and the **distribution** (see
it as a probability and minimize an expectation). The two give different guarantees and pay
different prices. The recommended prerequisites are the previous six lessons.

What this lesson additionally assumes:

- Partial differential equations: viscosity solutions of first-order HJ equations (introduced in
  the failure mode of `c4-dp-lqr-lqg` R2). We do not use the existence and uniqueness theory, only
  the **characterization**.
- Game theory: two-player zero-sum games, saddle points, the difference between minimax and
  maximin (upper and lower values).
- Probability: conditional expectation, the distinction between additive and **multiplicative**
  noise (failure mode 2 of `c4-dp-lqr-lqg` R5).
- Set operations: the Minkowski sum and difference (Pontryagin difference), invariant sets
  (`c4-mpc` R1).

Notation:

| Symbol | Meaning |
|---|---|
| $d \in \mathbb{D}$ | Disturbance. In the worst-case view it is **adversarial** |
| $\xi$ | Stochastic noise. Additive: $x^+ = f(x,u) + \xi$; multiplicative: $f$ depends on $\xi$ as a product |
| $\mathcal{T}$ | Target set. $\mathcal{T} = \{x : l(x) \le 0\}$ |
| $\mathcal{R}(T)$ | **Backward reachable tube (BRT)**: the states that **can be driven** to $\mathcal{T}$ within time $T$ |
| $V(x,\tau)$ | Level-set value function. $\mathcal{R}(\tau) = \{x : V(x,\tau) \le 0\}$ |
| $H(x,p)$ | The Hamiltonian $\min_u \max_d\, p^\top f(x,u,d)$ |
| $\gamma$ | $\mathcal{H}_\infty$ performance level. The penalty $-\gamma^2\lVert d\rVert^2$ on the disturbance |
| $\mathcal{Z}$ | The **error set** (mRPI) of tube MPC. The set in which the gap between nominal and actual stays |
| $\ominus$ | Pontryagin difference. $\mathbb{X} \ominus \mathcal{Z} = \{x : x + z \in \mathbb{X}\;\forall z \in \mathcal{Z}\}$ |

**The two views contrasted** (the map of this lesson):

| | Worst case (robust) | Distribution (stochastic) |
|---|---|---|
| Uncertainty model | A set $d \in \mathbb{D}$ | A distribution $\xi \sim p$ |
| What is solved | A two-player zero-sum game | Minimization of an expectation |
| Guarantee | Holds for **every** $d$ | Optimal on average |
| Price | Conservative — costs performance (R2) | Weak against tail risk |
| Representatives | HJI reachability, minimax DDP, tube MPC | iLQG, stochastic MPC |

## Key results

The bracket gives the derivation depth (D0 cited / D1 skeleton / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (HJI and the reachable set) [D3]** — the backward reachable tube is the **zero sublevel
  set** of the viscosity solution of the HJI **variational inequality**
  $$
  \min\Big\{\frac{\partial V}{\partial \tau} - H\big(x, \nabla V\big),\; V - l \Big\} = 0,
    \qquad V(x,0) = l(x), \qquad H(x,p) = \min_{u}\max_{d}\, p^\top f(x,u,d) \tag{1}
  $$
  that is, $\mathcal{R}(\tau) = \{x : V(x,\tau) \le 0\}$. The two terms of the inequality mean
  "reachability spreads" and "once reached, it is kept", respectively (Mitchell et al. 2005).
- **R2 (exact reduction for an additive same-channel disturbance) [D2]** — if the disturbance
  enters **additively through the same channel** as the control ($\dot{x}_2 = u + d$,
  $\lvert u\rvert \le 1$, $\lvert d \rvert \le D$) then
  $$
  H(x,p) = p_1 x_2 + \min_{\lvert u\rvert\le1} p_2 u + \max_{\lvert d\rvert\le D} p_2 d
    = p_1 x_2 - (1-D)\lvert p_2\rvert \tag{2}
  $$
  so **the robust reachable set is exactly the nominal set with the control bound reduced to
  $1-D$.** For the double integrator the nominal set is closed-form through the bang-bang
  solution of `c4-pontryagin-indirect` R3, which gives the **analytic oracle**
  $$
  T^*_a(x) = \frac{1}{a}\Big(x_2 + 2\sqrt{a x_1 + \tfrac12 x_2^2}\Big)
    \;\;\big(x_1 \ge -\tfrac{x_2\lvert x_2\rvert}{2a}\big), \qquad
    \mathcal{R}_D(T) = \{x : T^*_{1-D}(x) \le T\} \tag{3}
  $$
  A numerical level-set solution must be checked against it.
- **R3 (the minimax game Riccati equation and the $\mathcal{H}_\infty$ limit) [D2]** — the game
  HJI of $\dot x = ax + bu + cd$, $J = \int(qx^2 + ru^2 - \gamma^2 d^2)dt$ is
  $$
  k\,P^2 - 2aP - q = 0, \qquad k := \frac{b^2}{r} - \frac{c^2}{\gamma^2},
    \qquad P = \frac{a + \sqrt{a^2 + kq}}{k} \tag{4}
  $$
  and decreasing $\gamma$ (= more robustness to the disturbance) increases $P$, so **performance
  is lost**. For $k \le 0$, that is $\gamma \le c\sqrt{r}/b$, **no solution exists** — the
  disturbance wins. This is the $\mathcal{H}_\infty$ performance limit, and as $\gamma \to \infty$
  (4) returns to the LQR of `c4-dp-lqr-lqg`.
- **R4 (certainty equivalence breaks under multiplicative noise) [D2]** — `c4-dp-lqr-lqg` R5
  showed that under **additive** noise the optimal gain does not depend on the noise. If the noise
  enters the control as a **product** ($x^+ = Ax + (B + C\xi)u$, $\xi \sim \mathcal{N}(0,1)$), a
  $C^2 u^2$ term survives in the expectation and
  $$
  K = \frac{PAB}{R + P\,(B^2 + C^2)} \tag{5}
  $$
  where the $PC^2$ in the denominator **reduces** the gain (caution). The reproduction task
  measures a $13.90\%$ reduction and an improvement in the Monte Carlo expected cost.
- **R5 (tube MPC: separating nominal and error) [D1]** — for a linear system with a bounded
  disturbance, split the state into a nominal $\bar{x}$ and an error $e = x - \bar{x}$ and bind
  the error with a fixed feedback $K$; then $e^+ = (A+BK)e + w$, so the error stays in the
  **minimal robust positively invariant set** (mRPI) $\mathcal{Z}$. If the constraints of the
  nominal problem are **tightened** to $\mathbb{X} \ominus \mathcal{Z}$ and
  $\mathbb{U} \ominus K\mathcal{Z}$, the actual trajectory satisfies the original constraints, and
  the recursive feasibility of `c4-mpc` R1 carries over to the disturbed case (Mayne et al. 2005).
  **[D1]**

## Derivation

### R2 — the reduction and the analytic oracle

A numerical level-set solution is hard to verify. So we build one **problem whose answer is
known**.

Consider the double integrator with the control and the disturbance entering through the same
channel:

$$
\dot{x}_1 = x_2, \qquad \dot{x}_2 = u + d, \qquad
  \lvert u \rvert \le 1, \quad \lvert d \rvert \le D < 1. \tag{6}
$$

Compute the Hamiltonian of (1). The control tries to **decrease** $V$ and the disturbance to
**increase** it, so

$$
H(x,p) = p_1 x_2 + \underbrace{\min_{\lvert u\rvert\le1} p_2 u}_{=\,-\lvert p_2\rvert}
  + \underbrace{\max_{\lvert d\rvert\le D} p_2 d}_{=\,+D\lvert p_2\rvert}
  = p_1 x_2 - (1 - D)\lvert p_2 \rvert,
$$

which is (2). **This is, character for character, the Hamiltonian of the problem with no
disturbance and control bound $1-D$.** The two problems have the same HJI and the same initial
condition, hence the same value function, hence the same reachable set. A disturbance $D$ is
**exactly equivalent to taking away $D$ of the control authority**.

**Why this reduction is special**: in general $\min_u\max_d$ differs from $\max_d\min_u$ (upper
and lower values), and a disturbance cannot be traded for "less control authority". The reduction
works because in (6) $u$ and $d$ enter additively along **the same vector-field direction**. The
optimizer and the adversary then fight along the same axis, so a saddle point exists (the sign of
$p_2$ determines both optimal choices at once) and the two values coincide. If $u$ and $d$ enter
along different directions the reduction does not hold (problem P5).

**The analytic oracle.** Thanks to the reduction we can use the closed-form solution of the
nominal problem. `c4-pontryagin-indirect` R3 proved that the minimum-time double integrator with
$\lvert u\rvert \le 1$ is bang-bang with at most one switch. With bound $a$ the switching curve is
$x_1 = -x_2\lvert x_2\rvert/(2a)$ and the minimum time is (3) (the other branch is
$T^*_a = (-x_2 + 2\sqrt{-ax_1 + \tfrac12 x_2^2})/a$). Condition 1 of the reproduction task checks
that $T^*_1(1,0) = 2$, $T^*_1(0.5,-1) = 1$ and $T^*_1(-2,-1) = 1 + \sqrt{10}$ agree with the hand
computations of `c4-pontryagin-indirect` — **the two lessons share the same numbers.**

Then $\mathcal{R}_D(T) = \{x : T^*_{1-D}(x) \le T\}$, and at $T = 3$ its area inside $[-3,3]^2$ is

| $D$ | Effective bound $1-D$ | Area of $\mathcal{R}_D(3)$ |
|---|---|---|
| $0$ | $1.0$ | $13.8439$ |
| $0.1$ | $0.9$ | $12.2047$ |
| $0.3$ | $0.7$ | $8.6691$ |
| $0.5$ | $0.5$ | $4.4817$ |

(on a $601\times601$ grid). **As the disturbance grows the reachable set shrinks** — the price of
robustness is visible as an area.

**Where the assumptions break**: (2) used $D < 1$. If $D \ge 1$ then $1 - D \le 0$, the
disturbance can cancel the control completely, and the reachable set collapses to the target set
itself (or becomes empty). This is the set version of the same phenomenon as the critical $\gamma$
of R3. Also, (3) is the minimum time when the target is the **origin**. If the target is a disc of
radius $r$ the time is shorter by that much, so the difference must be accounted for when (3) is
used to decide set membership (see the diagnosis table of the reproduction task).

### R3 — the minimax game Riccati equation

We solve a scalar game to the end. In $\dot x = ax + bu + cd$,
$J = \int_0^\infty (qx^2 + ru^2 - \gamma^2 d^2)\,dt$ **the control minimizes and the disturbance
maximizes**. The $-\gamma^2d^2$ term is the penalty on the disturbance, and the smaller $\gamma$
is, the **cheaper** and therefore stronger the disturbance.

Put $V = Px^2$, so $V_x = 2Px$, and the HJI is

$$
\min_u \max_d \Big[ qx^2 + ru^2 - \gamma^2 d^2 + 2Px\,(ax + bu + cd) \Big] = 0.
$$

**The inner optimizations.** In $u$: minimize $ru^2 + 2Pxbu$, so $u^* = -Pbx/r$.
In $d$: maximize $-\gamma^2d^2 + 2Pxcd$, so $d^* = Pcx/\gamma^2$.
(Both are quadratic, convex and concave respectively, so a saddle point exists — $r > 0$ and
$\gamma^2 > 0$ are the conditions.)

**Substitute.** Collect the terms:

$$
\begin{aligned}
&qx^2 + r\Big(\frac{Pbx}{r}\Big)^2 - \gamma^2\Big(\frac{Pcx}{\gamma^2}\Big)^2
  + 2Px\Big(ax - \frac{b^2Px}{r} + \frac{c^2Px}{\gamma^2}\Big) \\
&= qx^2 + \frac{P^2b^2x^2}{r} - \frac{P^2c^2x^2}{\gamma^2}
  + 2aPx^2 - \frac{2P^2b^2x^2}{r} + \frac{2P^2c^2x^2}{\gamma^2} \\
&= x^2\Big[q + 2aP - \frac{P^2b^2}{r} + \frac{P^2c^2}{\gamma^2}\Big] = 0,
\end{aligned}
$$

that is, $kP^2 - 2aP - q = 0$ with $k = b^2/r - c^2/\gamma^2$ — this is (4). The stabilizing root
is $P = (a + \sqrt{a^2 + kq})/k$, and the closed loop is $a - b^2P/r + c^2P/\gamma^2$.

**Read it numerically at $a=b=c=q=r=1$.**

| $\gamma$ | $k$ | $P$ | Closed loop | Remark |
|---|---|---|---|---|
| $\infty$ | $1.00000$ | $2.4142135624$ | $-1.4142135624$ | **nominal LQR** ($1+\sqrt2$, $-\sqrt2$) |
| $4.0$ | $0.93750$ | $2.5514038301$ | $-1.3919410907$ | |
| $2.0$ | $0.75000$ | $3.0971675407$ | $-1.3228756555$ | |
| $1.5$ | $0.55556$ | $4.0449944321$ | $-1.2472191289$ | |
| $1.2$ | $0.30556$ | $7.0121752366$ | $-1.1426091001$ | |
| $1.0$ | $0$ | — | — | **no solution** |
| $0.9$ | $-0.23457$ | — | — | **no solution** |

**Three things to read.** (a) As $\gamma \to \infty$, $P = 1 + \sqrt2$ and the closed loop is
$-\sqrt2$, **exactly** P4 of `c4-dp-lqr-lqg` — an infinite disturbance penalty drives the
disturbance to zero and we are back at LQR. (b) Decreasing $\gamma$ increases $P$ monotonically
($2.41 \to 7.01$). $P$ is a cost, so **robustness costs performance**. (c) At
$\gamma \le c\sqrt{r}/b = 1$ we have $k \le 0$ and (4) has no positive solution — that performance
level is **unachievable**. This is why $\mathcal{H}_\infty$ design searches for $\gamma$ by
bisection (it looks for the smallest achievable $\gamma$).

**Where the assumptions break**: (i) the existence of a saddle point used $\gamma^2 > 0$ and
$r > 0$. As $r \to 0$ (cheap control) $k \to \infty$ and $P \to 0$, making the disturbance
powerless, but that is the unrealistic limit of infinitely strong control. (ii) On a finite
horizon (4) becomes a time-varying game Riccati differential equation, and a solution can exist
**for a finite time** even when $k \le 0$ — "no solution" is a statement about the infinite
horizon. (iii) The derivation assumes the disturbance **knows the state** and reacts immediately
(a full-information game). A disturbance that does not know the state is weaker and the limit on
$\gamma$ loosens.

### R4 — certainty equivalence breaks under multiplicative noise

`c4-dp-lqr-lqg` R5 showed that under **additive** noise the optimal gain does not depend on the
noise covariance (certainty equivalence). The crux of that proof was "all that additive noise adds
to a quadratic cost is a trace term independent of $u$". When the noise enters the control as a
**product**, that sentence becomes false.

Take a scalar discrete-time system. Let $\xi_k \sim \mathcal{N}(0,1)$ be independent of each other
and across time, and

$$x_{k+1} = A x_k + (B + C\xi_k)\,u_k. \tag{7}$$

Put $V(x) = Px^2$ and write the one-step Bellman equation. In the expectation over $\xi$,
$\mathbb{E}[\xi] = 0$ and $\mathbb{E}[\xi^2] = 1$, so

$$
\mathbb{E}\big[(Ax + (B + C\xi)u)^2\big]
  = (Ax + Bu)^2 + C^2u^2. \tag{8}
$$

**This $C^2u^2$ term depends on $u$** — where additive noise would have left a constant. So
differentiating

$$
\min_u \Big\{ Qx^2 + Ru^2 + P\big[(Ax+Bu)^2 + C^2u^2\big]\Big\}
$$

with respect to $u$ and setting the result to zero gives

$$
2Ru + 2PB(Ax + Bu) + 2PC^2 u = 0
  \;\Longrightarrow\; u^* = -\frac{PAB}{R + P(B^2 + C^2)}\,x,
$$

which is (5). The extra $PC^2$ in the denominator **reduces the magnitude of the gain**. The
reading is "using control brings noise in with it, so use less", and this is called **cautious
control**. The Riccati equation changes too: use the $K$ of (5) in $P = Q + PA^2 - PAB\,K$.

**Numbers** ($A = 1.1$, $B = 1$, $C = 0.6$, $Q = R = 1$):

| | $P$ | $K$ |
|---|---|---|
| Certainty equivalent ($C$ ignored) | $1.7737707217$ | $0.7034279289$ |
| Noise-aware (5) | $2.1919289904$ | $0.6056537807$ |

The gain is $13.90\%$ smaller, and running both gains on the actual system (7) by Monte Carlo
($4\times10^5$ samples, 60 steps) gives the expected costs

$$
\text{certainty equivalent } 2.258600 \quad > \quad \text{noise-aware } 2.198433
$$

so **the noise-aware gain is $2.7\%$ better**. Under multiplicative noise certainty equivalence is
therefore **not optimal** — failure mode 2 of `c4-dp-lqr-lqg` R5 confirmed in numbers. This is why
iLQG (Todorov & Li 2005) brings the covariance into the backward pass: a term of the form
$\sum_i C_i^\top V'_{xx} C_i$ is added to the $Q_{uu}$ of `c4-ilqr-ddp` (2).

**Where the assumptions break**: (i) (8) used that $\xi$ is **independent** of $x$ and $u$. If the
noise depends on the state (state-dependent covariance), cross terms remain in the expectation,
the quadratic form does not close, and the value function is no longer quadratic. (ii) The
derivation is **risk neutral** (it minimizes an expectation). If tail risk matters one must use a
risk-sensitive objective (the $\exp$ transform) or CVaR, and the gain changes again —
risk-sensitive control is mathematically connected to $\mathcal{H}_\infty$ (problem P7).
(iii) $R + P(B^2+C^2) > 0$ is needed. If $C$ is very large the gain goes to zero and **giving up
control** becomes optimal — the control channel has been ruined by noise, and then the thing to
fix is the hardware, not the controller.

### R5 — tube MPC (skeleton)

`c4-mpc` assumed no disturbance. Step 2 of its R1 ("the trajectory of the previous solution
actually happens") breaks under a disturbance, which voids the proof of recursive feasibility.
Tube MPC repairs it.

**Separation.** Let the actual system be $x^+ = Ax + Bu + w$ ($w \in \mathbb{W}$ bounded) and run
the nominal system $\bar{x}^+ = A\bar{x} + B\bar{u}$ separately. With the control

$$u = \bar{u} + K(x - \bar{x}) \tag{9}$$

the error $e = x - \bar{x}$ obeys

$$e^+ = (A + BK)e + w. \tag{10}$$

If $\rho(A+BK) < 1$ the trajectories of (10) stay in the **minimal robust positively invariant
set** $\mathcal{Z} = \bigoplus_{i\ge0}(A+BK)^i\mathbb{W}$ (if the initial error is in $\mathcal{Z}$
it stays there forever — because $\mathcal{Z}$ is invariant for (10)).

**Constraint tightening.** The actual state must satisfy $\mathbb{X}$, and $x = \bar{x} + e$ with
$e \in \mathcal{Z}$, so if the nominal satisfies the **tightened** constraints

$$\bar{x} \in \mathbb{X} \ominus \mathcal{Z}, \qquad \bar{u} \in \mathbb{U} \ominus K\mathcal{Z} \tag{11}$$

the actual system satisfies the original ones. The nominal problem is then an MPC **without
disturbance**, so `c4-mpc` R1 and R2 apply as they stand, and recursive feasibility and stability
(convergence to the error set) are restored (Mayne et al. 2005).

**The price** is the tightening in (11). If $\mathbb{W}$ is large, $\mathcal{Z}$ grows and
$\mathbb{X} \ominus \mathcal{Z}$ **can become empty** — the same phenomenon as "the set collapses
when $D \ge 1$" in R2. And $\mathcal{Z}$ is an infinite Minkowski sum that cannot be computed
exactly, so an outer approximation is used (which makes things that much more conservative).

**Where the assumptions break**: the clean separation in (10) holds only for **linear systems**
and **additive, bounded** disturbances. For a nonlinear system the error dynamics depend on the
nominal trajectory, so $\mathcal{Z}$ differs from trajectory to trajectory, and the error of a
learned model is **state dependent** and hard to enclose in a bounded set (open problem 3 of
`c4-mpc`).

## Proof sketch

### R1 — the reachable tube is the zero sublevel set of the HJI viscosity solution [D3]

**Hypotheses**
H1: $f(x,u,d)$ is Lipschitz in $x$, $u \in \mathbb{U}$ and $d \in \mathbb{D}$ are compact, and
$f$ is continuous in $(u,d)$.
H2: $l$ is Lipschitz and $\mathcal{T} = \{l \le 0\}$ is closed.
H3 (Isaacs condition): $\min_u\max_d\,p^\top f = \max_d\min_u\,p^\top f$ — the upper and lower
values coincide.
H4: the disturbance does not know the current value of the control (nonanticipative strategies).

**Conclusion** C: for the viscosity solution $V$ of (1),
$\mathcal{R}(\tau) = \{x : V(x,\tau) \le 0\}$, and from the states of that set there exists a
control that reaches the target for **every** admissible disturbance.

**Strategy**: fix the **meaning** of $V$ by dynamic programming (the worst-case minimal reach
cost), show that this function satisfies (1) in the viscosity sense, and obtain uniqueness from
the comparison principle. The crux is "what the $\min$ and the two terms of the variational
inequality each mean".

1. **Definition of the value function.** For nonanticipative strategies $\sigma$ put
   $$
   V(x,\tau) := \inf_{u(\cdot)}\;\sup_{d(\cdot)}\;\min_{s \in [0,\tau]} l\big(x(s)\big).
   $$
   The inner $\min_s$ is the device that measures **"did the trajectory enter the target at least
   once during the interval"** ($\min_s l \le 0 \iff$ it was in $\mathcal{T}$ at some time). Hence
   $V(x,\tau) \le 0$ is precisely "the state can be driven to the target within $\tau$ even under
   the worst disturbance".
2. **The dynamic programming principle.** Written through the value after a time $\delta$,
   $$
   V(x,\tau) = \min\Big\{\, l(x),\;\; \inf_u \sup_d V\big(x + f\delta,\; \tau - \delta\big)\Big\} + o(\delta).
   $$
   The first term of the outer $\min$ is "already inside the target now" and the second is "take
   one more step and look".
3. **Take the limit.** Expanding the second term to first order gives
   $\inf_u\sup_d\big[V + \nabla V^\top f\,\delta - V_\tau \delta\big]$, and by H3 we may write
   $\inf\sup = H$. Letting $\delta \to 0$ while keeping the $\min$ structure of step 2,
   $$\min\big\{\,V_\tau - H(x,\nabla V),\;\; V - l\,\big\} = 0,$$
   which is (1). **The meaning of the two terms**: when the first is zero, reachability
   "propagates" at that point; when the second is zero, $V = l$ is **frozen** (the state is
   already in the target, so nothing improves). The $\min$ picks whichever of the two is
   favourable — this is why the set is a tube that **never shrinks**.
4. **Why it must be read as a viscosity solution.** $V$ is in general not differentiable (for the
   same reason as in the failure mode of `c4-dp-lqr-lqg` R2 — it has a kink on the surface where
   different optimal strategies meet). The expansion of step 3 is classically valid only off that
   surface, and over the whole domain it is read through the test-function definition of a
   viscosity solution.
5. **Uniqueness and characterization.** By the comparison principle for first-order HJ equations
   the viscosity solution of (1) is unique, so the value function of step 1 is **that** solution.
   Its zero sublevel set is therefore the reachable tube. **C**.
   (Omitted: the proof of the comparison principle and the rigorous validity of the dynamic
   programming principle for nonanticipative strategies —
   [Mitchell et al. 2005](https://doi.org/10.1109/TAC.2005.851439) §II–§III and the references
   there.)

**Where it collapses if a hypothesis is removed**

- **Remove H3 (the Isaacs condition)**: $\min_u\max_d \ne \max_d\min_u$ and in step 3 it matters
  which is used as $H$. The two choices give **different sets** — the upper value gives the
  conservative set in which "the disturbance sees first", the lower value the optimistic set in
  which "the control sees first". A safety guarantee must use the **conservative side**. When
  $u, d$ are additive in the same channel as in (6), the Isaacs condition holds and the two
  coincide (R2).
- **Remove H4 (nonanticipation)**: a disturbance that **sees** the current control and reacts is
  stronger, and the set gets smaller. Conversely a disturbance that does not even know the state
  (an open-loop disturbance) gives a larger set. **"The robust set" depends on the information
  structure of the disturbance** — an item to check without fail when reading a paper.
- **Remove the second term of the $\min$** (that is, solve only $V_\tau = H$): trajectories that
  enter the target and leave again are reflected in the value, which then measures "reached at the
  end" rather than "reached at least once". The result is the reachable **set** (reach set,
  exactly at time $\tau$), not the **tube** (any time within $\tau$). Safety analysis almost
  always needs the tube.
- **Raise the dimension**: the characterization is **true** in any dimension but the computation
  is $O(n^d)$ on a grid. Practicality disappears at $d \gtrsim 6$ — the typical case of a theory
  that is right and cannot be used, and open problem 1.

## Problem set

The answer policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R4)** Expand (8) to the end and show that when the noise is **additive**
($x^+ = Ax + Bu + C\xi$) no term depending on $u$ remains. Then write the Riccati equations of the
two cases side by side.
*Answer sketch*: in the additive case $\mathbb{E}[(Ax+Bu+C\xi)^2] = (Ax+Bu)^2 + C^2$ adds a
constant, so the minimizer does not change (certainty equivalence). In the multiplicative case
$C^2u^2$ remains and $PC^2$ enters the denominator. The Riccati equation in the additive case is
$P = Q + PA^2 - P^2A^2B^2/(R+PB^2)$ with a constant term accumulating separately; in the
multiplicative case the denominator becomes $R + P(B^2+C^2)$.

**P2 (derivation, ★★, R3)** Extend (4) to the multivariable case. Write the game Riccati equation
of $\dot x = Ax + Bu + Cd$, $J = \int(x^\top Qx + u^\top Ru - \gamma^2 d^\top d)dt$, state what
the quantity corresponding to $k$ becomes, and which matrix inequality the existence condition
turns into.
*Answer sketch*: $A^\top P + PA + Q - P(BR^{-1}B^\top - \gamma^{-2}CC^\top)P = 0$, with
$BR^{-1}B^\top - \gamma^{-2}CC^\top$ in the place of $k$. The existence condition is that this
matrix be **positive definite** (or at least positive enough for a stabilizing solution to exist),
and the scalar $k > 0$ generalizes to the matrix inequality
$BR^{-1}B^\top \succ \gamma^{-2}CC^\top$.

**P3 (proof, ★★★, R1)** In the variational inequality of step 3 of the proof sketch, prove that
the solution of the equation with the **second term removed**, $V_\tau = H(x,\nabla V)$, gives the
reachable **set** (the states that are in the target exactly at time $\tau$), and that the
solution of (1), with the $\min$, gives the reachable **tube**.
*Answer sketch*: the strategy is to replace $\min_{s\in[0,\tau]}$ by $l(x(\tau))$ in the value
function of step 1 and repeat the same dynamic programming expansion. Key observation: with
$\min_s$ the value is **monotonically non-increasing** in $\tau$, so the set is monotonically
increasing, and that monotonicity appears as the second term of the variational inequality.
Without monotonicity the set can grow and then shrink in $\tau$ — construct one concrete example.

**P4 (numerical, ★, R3)** At $a=b=c=q=r=1$ solve (4) for $\gamma = 4, 2, 1.5, 1.2$ and give $P$
and the closed-loop pole to 10 decimals. Find the critical $\gamma$ and check that the limit
$\gamma \to \infty$ agrees with P4 of `c4-dp-lqr-lqg`.
*Answer*: $k = 1 - 1/\gamma^2$, $P = (1 + \sqrt{1+k})/k$.
$\gamma=4$: $k=0.9375$, $P=2.5514038301$, pole $-1.3919410907$.
$\gamma=2$: $k=0.75$, $P=3.0971675407$, pole $-1.3228756555$.
$\gamma=1.5$: $k=0.5\overline{5}$, $P=4.0449944321$, pole $-1.2472191289$.
$\gamma=1.2$: $k=0.3055\overline{5}$, $P=7.0121752366$, pole $-1.1426091001$.
Critical $\gamma = c\sqrt{r}/b = 1$ (tolerance $10^{-9}$). As $\gamma\to\infty$,
$P = 1+\sqrt2 = 2.4142135624$, pole $-\sqrt2$ ✓.
*Check*: substitute each $P$ into (4) and confirm a residual $< 10^{-12}$, and see that $P$ is
monotonically decreasing in $\gamma$ (that is, $P$ grows as $\gamma$ shrinks).

**P5 (numerical, ★★, R2)** Show that the reduction (2) does not hold when $u$ and $d$ enter
through **different channels**. Concretely, compute the Hamiltonian of $\dot x_1 = x_2 + d$,
$\dot x_2 = u$ ($\lvert u\rvert\le1$, $\lvert d\rvert\le D$) and explain why it does not
equal the nominal problem for any control bound.
*Answer*: $H = p_1x_2 + D\lvert p_1\rvert - \lvert p_2\rvert$. The disturbance term attaches to
$\lvert p_1\rvert$ and the control term to $\lvert p_2\rvert$, so **the two terms cannot be
merged** — for no $a$ does it take the form $p_1x_2 - a\lvert p_2\rvert$. The analytic oracle (3)
is therefore unavailable and the level set really has to be solved.
*Check*: confirm that at $D = 0$ the two Hamiltonians coincide, and see that for $D > 0$ the
$\lvert p_1\rvert$ term raises the value independently of $x_2$.

**P6 (implementation, ★★★, R1, R2)** Implement an HJI level-set solver, compute the robust
reachable tube of (6) and compare it with the analytic set of (3). **Warning**: the author's
Lax-Friedrichs implementation did not converge — on $[-3,3]^2$, $T=2$, target disc $r=0.25$, the
relative symmetric difference over the grids $n = 101 \to 201 \to 401 \to 801$ went
$0.593 \to 0.169 \to 0.240 \to 0.429$, **falling once and then rising again** ($D=0$; $D=0.3$
behaved the same way, $0.609 \to 0.202 \to 0.376 \to 0.641$). Build an implementation that
converges.
*Rubric*: (a) show that the relative symmetric difference **decreases monotonically** over four or
more grids (b) report the rate of decrease and state the scheme used (type of upwind difference,
dissipation coefficient, CFL number) (c) diagnose in one paragraph why the author's implementation
diverged (candidates: the sign of the dissipation term, $\alpha_1 = \max\lvert x_2\rvert$ taken
over the whole domain, the extrapolation in the boundary condition, the mismatch between the
target disc and the origin-based $T^*$) (d) comparing with an existing implementation such as
`helperOC` is allowed (in that case report the difference from your own implementation).

**P7 (counterexample, ★★, R3, R4)** Show in **two ways** that "designing robustly also improves
average performance" is false: (i) $P$ grows as $\gamma$ decreases in R3 (= the nominal cost gets
worse), (ii) numerically, applying a minimax controller to a system that in fact has no
disturbance costs more than LQR.
*Property checklist*: (i) uses the table of P4 and states that $P$ is the nominal cost. (ii) puts
the minimax gain for $\gamma = 1.2$ into the system with $d \equiv 0$ and compares the cost with
that of the LQR gain. Property to confirm: a robust design gives up the average as the price of
guaranteeing the **worst case** — the two metrics are not to be confused. Bonus: write in one line
where risk-sensitive control connects to $\mathcal{H}_\infty$.

**P8 (paper, ★★, R1, R4, R5)** Read Mitchell et al. 2005 §II–§IV, Todorov & Li 2005 §II–§III and
Mayne et al. 2005 §2–§4 and write, in at most three sentences each, (a) whether the information
structure of the disturbance used by Mitchell et al. (nonanticipative strategies) is the same as
H4 of this lesson (b) in which term of the backward pass the iLQG of Todorov and Li puts the
multiplicative noise (c) which outer approximation the computation of $\mathcal{Z}$ by Mayne et
al. actually uses.
*Rubric*: (a) passes if it names nonanticipative strategies and the Isaacs condition. (b) passes
if it writes the covariance term added to $Q_{uu}$ as a formula. (c) passes if it names the outer
approximation by a finite sum plus scaling and its conservatism. "They compute the set" alone
fails.

## Paper reading

**Three must-read papers.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read in three passes, and in the third pass concentrate on questions 4,
5, 6 and 7.

1. **Mitchell, Bayen & Tomlin, "A time-dependent Hamilton-Jacobi formulation of reachable sets
   for continuous dynamic games" (2005, IEEE T-AC)** — role: `seminal`.
   Read: §II (formulation), §III (viscosity solution and characterization), §IV (numerical
   examples).
   The primary source for R1 of this lesson. Attend to why **the two terms of the variational
   inequality** have that form.
   Additional questions: (a) what information structure do the authors give the disturbance, and
   is it the same as H4 of this lesson? (b) do the authors distinguish a "reach set" from a "reach
   tube"? If so, what is the difference in the equations? (c) what is the dimension of the
   numerical examples, and what do the authors say about the dimensional limit?
2. **Todorov & Li, "A generalized iterative LQG method for locally-optimal feedback control of
   constrained nonlinear stochastic systems" (2005, ACC)** — role: `standard`.
   Read: §II (formulation and backward pass), §III (constraint handling).
   The primary source for R4 of this lesson and the stochastic version of `c4-ilqr-ddp`.
   Additional questions: (a) into which term of the backward pass, and in what form, does the
   multiplicative noise enter (as a formula)? (b) is the authors' constraint handling the same as
   the projection of `c4-ilqr-ddp` R4 or different? (c) where does the locality meant by
   "locally-optimal" come from (linearization or non-convexity)?
3. **Mayne, Seron & Raković, "Robust model predictive control of constrained linear systems with
   bounded disturbances" (2005, Automatica)** — role: `standard`.
   Read: §2 (problem and tube), §3 (constraint tightening and feasibility), §4 (stability).
   The primary source for R5 of this lesson; it carries `c4-mpc` R1 over to the disturbed case.
   Additional questions: (a) where does the authors' proof of recursive feasibility agree with the
   five steps of `c4-mpc` R1 and where does it differ? (b) the stability conclusion is not
   "convergence to the origin" but what (convergence to which set)? (c) does outer-approximating
   $\mathcal{Z}$ weaken the guarantee or make it conservative — and do the authors state the
   difference?

**The ten fixed questions**: (1) what problem is solved under what assumptions (2) what exactly
could earlier work not do (3) the key idea in one line of mathematics (4) what is the theoretical
guarantee and **what is not guaranteed** (5) the independent and dependent variables and baselines
of the experiments, and were they tuned fairly (6) do the metrics match the claims, and are
variance and seeds reported (7) what information needed for reproduction is missing (8) if it is
wrong, which assumption to suspect first (9) computational and memory complexity and real-time
capability (10) what would you change to surpass it a year from now.

## Reproduction task

**Tier R2 (algorithm reimplementation).** Compute budget: one laptop CPU core, under 15 minutes in
total, at most 1 GB of memory. numpy + scipy only. No simulator.

**Input data**: none. Everything is specified by constants.

**System A — the double-integrator game**: (6) with $\lvert u\rvert \le 1$, $\lvert d\rvert \le D$,
target the disc of radius $0.1$ centred at the origin, horizon $T = 2$. The grid is
$26\times26$ over $[-2.5, 2.5]^2$ (for drawing the Monte Carlo samples); areas are computed on
$601\times601$ over $[-3,3]^2$. Integration is Euler with step $2\times10^{-4}$.

**System B — the scalar game**: $a=b=c=q=r=1$, $\gamma \in \{\infty, 4, 2, 1.5, 1.2, 1, 0.9\}$.

**System C — multiplicative noise**: $x^+ = Ax + (B + C\xi)u$, $A=1.1$, $B=1$, $C=0.6$, $Q=R=1$,
$\xi\sim\mathcal{N}(0,1)$. The Monte Carlo uses $4\times10^5$ samples, 60 steps, initial
$x_0\sim\mathcal{N}(0,1)$.

**Acceptance criteria** — **all** four conditions must hold to pass.

1. **Analytic oracle (system A).** (a) The $T^*_1$ of (3) gives
   $T^*_1(1,0) = 2$, $T^*_1(0.5,-1) = 1$, $T^*_1(-2,-1) = 1+\sqrt{10} = 4.1622776602$
   **exactly** (error $< 10^{-12}$) — the same numbers as the hand computations of
   `c4-pontryagin-indirect`.
   (b) The area of $\mathcal{R}_D(3)$ obtained through the reduction (2) is $13.8439$, $12.2047$,
   $8.6691$, $4.4817$ at $D = 0, 0.1, 0.3, 0.5$ ($601\times601$ grid, error $\pm0.01$) and
   **decreases monotonically** in $D$.
2. **Monte Carlo confirms the set (system A, $D = 0.3$).** Use the minimax feedback
   $u = -\operatorname{sign}\big(x_1 + \tfrac{x_2\lvert x_2\rvert}{2(1-D)}\big)$ (magnitude 1) and
   show that
   (a) from all states with $T^*_{0.7}(x) \le T - 0.05$ (62 in the author's implementation) the
   target is reached within $T$ in all three cases — **worst-case disturbance**
   ($d = -D\operatorname{sign}(u)$), **random disturbance** and **no disturbance** — the author's
   implementation gives $62/62$, $62/62$, $62/62$,
   (b) from all states with $T^*_{0.7}(x) > T + 1.0$ (476 in the author's implementation) **none
   reaches the target** under the **worst-case disturbance** — the author's implementation gives
   $0/476$,
   (c) from the same 476 states, **without disturbance** some do reach it (the author's
   implementation gives $12/476$); report how many of those belong to the nominal set
   ($\lvert u\rvert\le1$, no disturbance) (16 in the author's implementation).
   **(c) is the point of this condition**: the difference between the nominal set and the robust
   set is the set of "states that work only if the disturbance cooperates".
3. **Minimax game Riccati (system B).** Reproduce the table of P4. At
   $\gamma = \infty, 4, 2, 1.5, 1.2$, $P$ is $2.4142135624$, $2.5514038301$, $3.0971675407$,
   $4.0449944321$, $7.0121752366$ (error $10^{-9}$) and the closed-loop poles are
   $-1.4142135624$, $-1.3919410907$, $-1.3228756555$, $-1.2472191289$, $-1.1426091001$.
   For $\gamma \le 1$ report that $k \le 0$ and (4) has no positive solution. Also confirm that
   the $\gamma\to\infty$ value agrees with the $1+\sqrt2$ of `c4-dp-lqr-lqg`.
4. **The collapse of certainty equivalence (system C).** (a) The certainty-equivalent gain ($C$
   ignored) and the noise-aware gain (5) are $K = 0.7034279289$ and $0.6056537807$
   ($P = 1.7737707217$, $2.1919289904$; error $10^{-8}$) and the gain shrinks by
   $13.90\% \pm 0.1\%$.
   (b) The Monte Carlo expected costs are $2.2586$ for certainty equivalence and $2.1984$ for the
   noise-aware gain ($\pm 0.01$), so **the noise-aware one is lower** (a relative improvement of
   $2.7\% \pm 0.3\%$).
   (c) Switching the noise to **additive** ($x^+ = Ax + Bu + C\xi$) makes the two gains equal —
   confirm it; certainty equivalence holds only in the additive case (P1).

**Comparison**: (1) the three values of condition 1(a) were derived by hand in
`c4-pontryagin-indirect`, so this is a **cross-check** between lessons. (2) The analytic set of
condition 2 is the baseline for the Monte Carlo. (3) The $\gamma\to\infty$ value of condition 3 is
the baseline of P4 in `c4-dp-lqr-lqg`. (4) The additive-noise case of condition 4(c) is the
baseline for certainty equivalence. (5) **Optional**: also compute the set of condition 2 by level
sets and compare with the analytic set (problem P6 — the author's implementation did not
converge).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| $T^*$ is negative or `nan` | The branch test (comparing $x_1$ with the switching curve) is wrong and the radicand went negative | Guard the radicand with `max(·, 0)` and confirm the branch with the three check values |
| Some states inside the set do not reach the target | The target is a **disc** but $T^*$ is the time to the **origin** — the margin is wrong | Shrink the target radius (the author used $0.1$) or put a margin of $-0.05$ on the inside test |
| Some states outside the set reach the target under the worst-case disturbance | The margin of the outside test is too small (the disc radius saves that much time) | Increase the outside margin to $+1.0$. In the author's implementation $6/564$ leaked at $+0.4$ |
| The minimax feedback uses the nominal switching curve | The curve of the robust value function must be computed with **$1-D$** | Check that the denominator of the curve is $2(1-D)$. The control **magnitude** is 1 |
| $P$ comes out negative for small $\gamma$ | The quadratic formula was applied although $k \le 0$ | Test $k > 0$ first and otherwise report "no solution" |
| The two gains come out equal under multiplicative noise | The noise was implemented as additive ($Ax + Bu + C\xi$) | Check that $\xi$ **multiplies** $u$ as in (7) |
| The Monte Carlo cost difference is buried in noise | Too few samples | Use $4\times10^5$ or more and compare the two gains on the same random numbers (common random numbers) |

## Open problems

- **(Open problem) The dimensional barrier of level sets** — the characterization of R1 is true in
  any dimension, but grid computation is $O(n^d)$ and ends at $d \gtrsim 6$. Computing the safe
  set of a quadruped or humanoid ($d \gtrsim 20$) by HJI is impossible. Current approaches:
  decomposing the system into low-dimensional subproblems, and approximating the value function
  with a neural network ([Bansal et al. 2017](https://doi.org/10.1109/CDC.2017.8263977) §IV
  surveys them). What is missing: a way to certify that an approximate value function is wrong
  **on the conservative side** — a safety guarantee is usable only if it errs in one direction.
- **(Open problem) Between the worst case and the distribution** — the worst case is conservative
  (the growth of $P$ in R3) and the expectation is weak in the tails. Risk measures that mediate
  between the two (CVaR, distributionally robust optimization) have been proposed, but a middle
  point that is **both computable and guaranteed** at robotics scale has not been established.
  Current approaches: the mathematical link between risk-sensitive control (the $\exp$ transform)
  and $\mathcal{H}_\infty$, and moment-based distributionally robust MPC. What is missing:
  guarantees when the disturbance set or distribution is estimated **from data**.
- **(Open problem) Set representations of learned-model error** — the tube of R5 requires a
  bounded $w \in \mathbb{W}$, but the error of learned dynamics is state dependent and heavy
  tailed. With a state-dependent tube $\mathcal{Z}$ changes from trajectory to trajectory and the
  invariance argument becomes complicated. Current approaches: using Gaussian-process confidence
  intervals as $\mathbb{W}$, and set estimation based on conformal prediction. What is missing: a
  construction that gives finite-sample guarantees and recursive feasibility **simultaneously**
  (the same gap as open problem 3 of `c4-mpc`, met again from the learning side in
  `c8-rl-theory`).
- **(Open problem) Robustness of systems with contact** — as the previous lesson showed, contact
  is not differentiable near the transition surface and the **order** of transitions can change
  with the disturbance. The error set of R5 then differs per mode and a Minkowski sum arises for
  each mode sequence. Current approaches: per-mode tubes and conservative margins near the
  transition surface. What is missing: a way to enclose the change of mode sequence **as a set** —
  guaranteeing the push recovery of a legged robot requires solving this problem.

## Concept check

Take it with `rc quiz c4-robust-stochastic-oc`. This quiz is a **concept check only**; the real
work is the problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

## How to study this stage

1. **Memorize the table of the two views first (20 min)** — copy the worst-case/distribution
   table of "Setup and notation" onto paper. Every result of this lesson belongs to one of its two
   columns, and confusing them is the most common error on this topic (the illusion that a robust
   design also improves the average — quiz q6).
2. **Build the analytic oracle first (50 min)** — implement condition 1 **first**. Once the $T^*$
   of (3) reproduces the three hand-computed values of `c4-pontryagin-indirect`, you hold a
   **problem whose answer is known** before entering a complicated computation such as level sets.
   This is the right order for writing numerical code in research.
3. **Derive the reduction by hand (40 min)** — write (2) yourself and confirm that the two terms
   merge only when $u$ and $d$ share a channel (see the counterexample in P5). This one line turns
   the intuition "disturbance = loss of control authority" into a precise statement.
4. **Confirm the set by Monte Carlo (70 min)** — condition 2 is the central experience of this
   lesson. Be sure to measure (c) (outside the set, **without disturbance**, some states do reach
   the target). The moment you see in numbers that the difference between the nominal and the
   robust set is "the states that work only if the disturbance cooperates", it becomes clear what
   robustness buys and what it sells.
5. **Expand the game Riccati equation to the end (50 min)** — do the substitution of R3 by hand.
   One sign error flips $k$ and reverses the conclusion, so check that $\gamma\to\infty$ gives the
   $1+\sqrt2$ of `c4-dp-lqr-lqg`. Then find the critical $\gamma$ and build the table (P4).
6. **Break certainty equivalence (60 min)** — implement condition 4. Keep additive and
   multiplicative noise **behind a switch in the same code** and you see at once that the two
   gains agree in the additive case and separate in the multiplicative one. Compare with common
   random numbers or the 2.7% difference is buried in noise.
7. **Only the skeleton of the tube; fill it in from the paper (60 min)** — R5 is D1. Take just the
   structure of (9)–(11) and fill in the details from Mayne et al. §2–§3. Put it next to the five
   steps of `c4-mpc` R1 and write in one paragraph **what changed** (how step 2, "the previous
   trajectory actually happens", is repaired).
8. **Level sets are optional but recommended (optional, one day)** — this is problem P6. You have
   been told even that the author's implementation did not converge, so building one that does is
   good research practice. With the analytic oracle it is **debugging with an oracle**, a rare
   luxury in real research.
9. **Papers in the order set → distribution → practice (150 min)** — Mitchell et al. (sets and
   games) → Todorov & Li (distributions) → Mayne et al. (practical MPC). The first two correspond
   to the two columns of this lesson and the third turns both into an actual controller. The
   one-page note per paper is **mandatory**.
10. **Close the module (40 min)** — this is the last lesson of C4. Collect and read the "Open
    problems" of the seven lessons and write down three places that kept recurring (certifying
    global optimality, gradients under non-smoothness, guarantees under learned models). Those
    three are the actual front line of optimal control in robotics in 2026, and
    `s2-planning-through-contact`, `s3-legged-underactuated` and `c8-rl-theory` each take that
    front line further.

**Pass criterion**: from a blank page you can derive the reduction (2), the game Riccati equation
(4) and the cautious gain (5); you can state the meaning of the two terms of the variational
inequality; you can explain the difference between the nominal and the robust set with numbers you
counted yourself; you have code that satisfies all four conditions of the reproduction task; and
you have notes on the three papers.
