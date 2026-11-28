---
id: c4-dp-lqr-lqg
lang: en
title: Dynamic programming, LQR and LQG
summary: >-
  Build the Bellman equation and the HJB equation from the principle of optimality, and prove with
  a verification theorem that dynamic programming supplies the **sufficient** condition the PMP
  could not. Show that the costate is the gradient of the value function,
  $\lambda = \partial V/\partial x$, tying this lesson to the previous one; then derive LQR along
  three routes - DP, PMP and completion of squares - and confirm they reach the same Riccati
  equation. Prove monotone convergence of the Riccati recursion and closed-loop stability, and see
  numerically how a loss of detectability produces an LQR that is optimal yet unstable. Finish
  with the LQG separation theorem and with Doyle 1978, which shows that its guarantee is **not**
  robustness.
objectives:
  - Derive the discrete Bellman equation and the continuous HJB equation from the principle of optimality, and reconstruct the verification theorem as a proof sketch.
  - Differentiate the HJB in the state to obtain $\lambda = \partial V/\partial x$ and the adjoint equation, and explain what breaks where the value function is non-differentiable.
  - Derive LQR along the DP, PMP and completion-of-squares routes and show all three give the same Riccati equation.
  - State separately the conditions for monotone convergence of the Riccati recursion and for closed-loop stability, and construct a counterexample where detectability fails.
  - Derive the LQG separation theorem from orthogonality of the estimation error, and explain with Doyle's example why it guarantees no stability margin.
tags: [optimal-control, dynamic-programming, hjb, lqr, lqg, riccati, research]
---

# Dynamic programming, LQR and LQG

## Setup and notation

The previous lesson, `c4-pontryagin-indirect`, established the **necessary** conditions of optimal
control. This lesson looks at the same problem through the **value function** and obtains a
**sufficient** condition. The price is the curse of dimensionality, and the value function stays
in closed form only for linear-quadratic problems — which is LQR. The recommended prerequisites
are the previous lesson and module R0.

What this lesson additionally assumes:

- Linear algebra: the symmetric positive semidefinite order ($P \succeq 0$), Schur complements,
  eigenvalues and the spectral radius.
- Probability: conditional expectation, orthogonal projection, linear transformations of
  Gaussians. The derivation of the Kalman filter itself lives in `c5-manifold-estimation`; here we
  use only the **result**.
- Control: controllability, stabilizability, detectability.

Notation (shared across module C4, continuing from the previous lesson):

| Symbol | Meaning |
|---|---|
| $V(x, t)$ | value function — the **optimal** remaining cost from $(x,t)$ |
| $x_{k+1} = Ax_k + Bu_k$ | discrete-time linear system, $A \in \mathbb{R}^{n\times n}$, $B \in \mathbb{R}^{n \times m}$ |
| $Q \succeq 0$, $R \succ 0$ | stage-cost weights; $Q_f \succeq 0$ is the terminal weight |
| $P_k \succeq 0$ | the quadratic coefficient of the value function, $V_k(x) = \tfrac12 x^\top P_k x$ |
| $K_k$ | feedback gain, $u_k^* = -K_k x_k$ |
| $S_k$ | $R + B^\top P_{k+1} B \succ 0$ (the Hessian in the control) |
| $\rho(M)$ | spectral radius $\max_i \lvert \mu_i(M)\rvert$ |
| $w_k \sim \mathcal{N}(0, W)$, $v_k \sim \mathcal{N}(0, V)$ | process and measurement noise (LQG), independent of each other and across time |
| $\hat{x}_k$, $e_k$ | the estimate $\mathbb{E}[x_k \mid y_{0:k}]$ and the error $x_k - \hat{x}_k$ |

**Cost convention**: this course **includes the $\tfrac12$** —
$J = \tfrac12\sum (x^\top Qx + u^\top Ru) + \tfrac12 x_N^\top Q_f x_N$. Many textbooks omit it, so
their $P$ differs by a factor of two. This is the second thing to check when reading a paper (the
first is the sign convention of the previous lesson).

The reference problem. **Discrete**:

$$
\min_{u_{0:N-1}} \; \tfrac12\sum_{k=0}^{N-1}\big(x_k^\top Q x_k + u_k^\top R u_k\big)
  + \tfrac12 x_N^\top Q_f x_N \quad \text{s.t.} \quad x_{k+1} = Ax_k + Bu_k,\; x_0 \text{ given}. \tag{1}
$$

**Continuous** (the same $(\mathrm{P})$ as the previous lesson):
$\min \int_t^{t_f}\ell(x,u,s)\,ds + \varphi(x(t_f))$ s.t. $\dot x = f(x,u,s)$, $x(t) = x$.

## Key results

The bracket gives the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (the Bellman equation and the verification theorem) [D3]** — by the principle of
  optimality the value function satisfies
  $$V_k(x) = \min_{u}\big\{\tfrac12(x^\top Qx + u^\top Ru) + V_{k+1}(Ax + Bu)\big\}, \quad V_N(x) = \tfrac12 x^\top Q_f x \tag{2}$$
  and, in continuous time, the **HJB equation**
  $$-\frac{\partial V}{\partial t} = \min_{u \in U}\left\{\ell(x,u,t) + \frac{\partial V}{\partial x}f(x,u,t)\right\}, \qquad V(x, t_f) = \varphi(x). \tag{3}$$
  The converse also holds (the **verification theorem**): if any $C^1$ function $W$ satisfies (3)
  together with the terminal condition, then $W$ **is** the value function and a minimiser of (3)
  is an optimal control. So DP supplies the **sufficient** condition the PMP could not.
- **R2 (the costate is the gradient of the value function) [D2]** — if $V$ is $C^2$ then along the
  optimal trajectory
  $$\lambda(t) := \left(\frac{\partial V}{\partial x}(x^*(t), t)\right)^\top \tag{4}$$
  satisfies **exactly** the adjoint equation $\dot\lambda = -\ell_x^\top - f_x^\top\lambda$ of the
  previous lesson together with the terminal condition $\lambda(t_f) = \varphi_x^\top$. For LQR,
  $V = \tfrac12 x^\top Px$, so $\lambda = Px$ — which explains the "sweep" ansatz of indirect
  methods.
- **R3 (three derivations of LQR) [D3]** — the solution of (1) is $u_k^* = -K_k x_k$ with
  $$
  K_k = S_k^{-1}B^\top P_{k+1}A, \quad S_k = R + B^\top P_{k+1}B, \quad
    P_k = Q + A^\top P_{k+1}A - A^\top P_{k+1}B\,S_k^{-1}B^\top P_{k+1}A, \quad P_N = Q_f, \tag{5}
  $$
  and the same (5) comes out of **DP** (a quadratic ansatz plus completion of squares), the
  **PMP** (a linear two-point boundary value problem plus $\lambda_k = P_kx_k$), and a
  **completion-of-squares identity**. The third route gives
  $$J(u_{0:N-1}) = \tfrac12 x_0^\top P_0 x_0 + \tfrac12\sum_{k=0}^{N-1}(u_k + K_kx_k)^\top S_k (u_k + K_kx_k), \tag{6}$$
  which holds for **every** control sequence, so optimality follows immediately (it is the
  shortest way to check DP's sufficient condition by hand in the LQR case).
- **R4 (Riccati convergence and closed-loop stability) [D3]** — with $Q \succeq 0$, $R \succ 0$
  and $(A,B)$ stabilizable, running (5) backwards from $Q_f = 0$ gives a $P^{(n)}$ that is
  **monotone increasing and bounded** in $n$, hence convergent, and the limit $P_\infty$ solves
  the discrete algebraic Riccati equation (DARE). Adding **detectability** of $(A, Q^{1/2})$ gives
  $P_\infty \succ 0$ and
  $$\rho\big(A - BK_\infty\big) < 1. \tag{7}$$
  If detectability fails, the DARE acquires several PSD solutions and the recursion can converge
  to a **non-stabilizing** one — an LQR that is optimal yet unstable.
- **R5 (the LQG separation theorem and its limits) [D2]** — if $w$ and $v$ are additive, Gaussian
  and independent and the cost is the quadratic of (1), the optimal control is
  $$u_k^* = -K_k \hat{x}_k, \qquad \hat{x}_k = \mathbb{E}[x_k \mid y_{0:k}] \;(\text{the Kalman filter}), \tag{8}$$
  i.e. the **deterministic LQR gain applied directly to the estimate** ($K_k$ does not depend on
  the noise covariances — certainty equivalence). But that optimality concerns only the
  **expected cost under an exact model**: Doyle 1978 showed the gain margin of an LQG loop can be
  made **arbitrarily small**. **[D2]**

## Derivation

### R1 — the Bellman equation and the HJB equation

**The principle of optimality** (Bellman 1954): from any intermediate state of an optimal
trajectory, the **remaining** trajectory is optimal for the problem started at that state. This
follows straight from the definition — if the remaining trajectory were not optimal we could
replace just that piece and lower the total cost, so the original would not have been optimal.
(All it uses is that **the cost adds up over stages**. Where additivity fails, DP fails — see the
failure modes below.)

In discrete time, define $V_k(x) :=$ (the optimal remaining cost starting at stage $k$ in state
$x$); peel off one stage and apply the principle to the rest to get (2). To pass to continuous
time, take a time step $\Delta$ and write

$$
V(x, t) = \min_{u}\Big\{\ell(x,u,t)\Delta + V\big(x + f(x,u,t)\Delta,\; t+\Delta\big)\Big\} + o(\Delta),
$$

then expand $V$ to first order about $(x,t)$:

$$
V(x,t) = \min_u\Big\{\ell\Delta + V(x,t) + \frac{\partial V}{\partial x}f\Delta
  + \frac{\partial V}{\partial t}\Delta\Big\} + o(\Delta).
$$

$V(x,t)$ and $\partial V/\partial t\,\Delta$ do not depend on $u$, so pull them out of the
minimum, cancel $V(x,t)$ from both sides, divide by $\Delta$ and let $\Delta \to 0$: that is (3).
**Using a first-order expansion is where the assumption $V \in C^1$ sits.**

### R1 (continued) — the verification theorem

(3) can be read as a necessary condition: "if an optimum exists, $V$ satisfies this". What matters
is the **converse**: find, by **any** means, one $C^1$ function satisfying (3), and it is the value
function and its minimiser is the optimal control. The PMP of the previous lesson gave no such
converse (an extremal need not be optimal). The proof is in the "Proof sketch" section; the
one-line summary is "integrate (3) along an arbitrary admissible trajectory and you get an
inequality; along the minimiser's trajectory you get equality."

### R2 — $\lambda = \partial V/\partial x$

Let $u^*(x,t)$ be the minimiser in (3) and suppose $V$ is $C^2$. Differentiate (3) in $x$. Since
$u^*$ attains the minimum, the term through $u$ vanishes (the envelope theorem — the same step as
(14) of the previous lesson):

$$
-\frac{\partial^2 V}{\partial t \partial x} = \ell_x + \frac{\partial V}{\partial x}f_x
  + f^\top \frac{\partial^2 V}{\partial x^2}. \tag{9}
$$

Now take the time derivative of $\lambda(t)^\top := \partial V/\partial x$ along the optimal
trajectory $x^*(t)$. Since $\dot{x}^* = f$, the chain rule gives

$$
\dot\lambda^\top = \frac{d}{dt}\frac{\partial V}{\partial x}
  = \underbrace{f^\top\frac{\partial^2 V}{\partial x^2}}_{\text{change through the state}}
  + \underbrace{\frac{\partial^2 V}{\partial t \partial x}}_{\text{change through time}}. \tag{10}
$$

Substituting (9) into (10) **cancels** the $f^\top V_{xx}$ term:

$$
\dot\lambda^\top = f^\top V_{xx} - \ell_x - \lambda^\top f_x - f^\top V_{xx}
  = -\ell_x - \lambda^\top f_x
  \;\;\Longleftrightarrow\;\; \dot\lambda = -\ell_x^\top - f_x^\top\lambda, \tag{11}
$$

which is exactly the adjoint equation (2) of the previous lesson (in the normal case
$\lambda_0 = 1$). The terminal condition matches too: $V(x,t_f) = \varphi(x)$ gives
$\lambda(t_f) = \varphi_x^\top$.

**How to read this**: the costate is "the gradient of the value function", and the $\lambda(0)$
that an indirect method had to guess is $\partial V/\partial x(x_0, 0)$ — which is why the last
open problem of the previous lesson (supplying $\lambda(0)$ by learning) is a natural idea. The
PMP is the method that carries **only the gradient** of the value function; DP is the method that
carries **the whole function**. The former costs $O(n)$ per trajectory, the latter
$O(\text{grid}^n)$ — that is the precise location of the curse of dimensionality.

**Where the assumptions break**: (4) needs $V$ differentiable. But value functions generally are
**not**. The minimum-time double integrator of the previous lesson is exactly such a case — two
optimal trajectories meet on the switching curve $x_1 = -\tfrac12 x_2\lvert x_2\rvert$, and
$\partial V/\partial x$ jumps across it. At those points (4) is undefined, yet the PMP still
supplies (several) costates. What bridges the gap is the theory of **viscosity solutions**
([Crandall & Lions 1983](https://doi.org/10.1090/S0002-9947-1983-0690039-8)): solving the HJB in
that weak sense extends the verification theorem to the non-smooth case. The second failure mode
is a **non-additive cost** — if the cost is something like $\max_t g(x(t))$ rather than a sum of
stage costs, the decomposition (2) does not hold at all, and the state must be enlarged (e.g. by
carrying the running maximum) to restore additivity.

### R3 — three derivations of LQR

#### (a) The DP route

Put the quadratic ansatz $V_{k+1}(x) = \tfrac12 x^\top P_{k+1}x$ into (2) (the induction base is
correct, since we start from $P_N = Q_f$):

$$
V_k(x) = \min_u \tfrac12\Big[x^\top Qx + u^\top Ru + (Ax+Bu)^\top P_{k+1}(Ax+Bu)\Big].
$$

The bracket is a quadratic form in $u$ whose Hessian is $R + B^\top P_{k+1}B = S_k \succ 0$
(because $R \succ 0$ and $P_{k+1}\succeq 0$), so there is a unique minimum. Differentiating in
$u$ and setting it to zero:

$$
Ru + B^\top P_{k+1}(Ax + Bu) = 0 \;\Longrightarrow\; S_k u = -B^\top P_{k+1}Ax
  \;\Longrightarrow\; u^* = -\underbrace{S_k^{-1}B^\top P_{k+1}A}_{K_k}x. \tag{12}
$$

Substitute $u^*$ back. Collecting the cross terms (using symmetry of $P_{k+1}$),

$$
2V_k(x) = x^\top\Big[Q + A^\top P_{k+1}A - A^\top P_{k+1}BK_k - K_k^\top B^\top P_{k+1}A
  + K_k^\top S_k K_k\Big]x.
$$

Here $K_k^\top S_kK_k = (S_k^{-1}B^\top P_{k+1}A)^\top S_k (S_k^{-1}B^\top P_{k+1}A)
= A^\top P_{k+1}B\,S_k^{-1}B^\top P_{k+1}A = A^\top P_{k+1}BK_k$, and the same expression equals
$K_k^\top B^\top P_{k+1}A$. So two of the three cross terms cancel, leaving one:

$$
P_k = Q + A^\top P_{k+1}A - A^\top P_{k+1}BK_k
  = Q + A^\top P_{k+1}A - A^\top P_{k+1}B\,S_k^{-1}B^\top P_{k+1}A, \tag{13}
$$

which is (5). $V_k$ is quadratic too, so the induction closes.

**The Joseph form of the same equation.** Grouping the computation the other way gives

$$
P_k = Q + K_k^\top R K_k + (A - BK_k)^\top P_{k+1}(A - BK_k) \tag{14}
$$

(problem P1 shows (13) $\Leftrightarrow$ (14)). In (14) **all three terms are $\succeq 0$**, so
round-off cannot push $P_k$ out of the symmetric PSD cone. (13) is a difference of two large
positive quantities, so it loses symmetry and definiteness when $P$ is nearly singular. In the
reproduction task you implement both and confirm they agree — but production code uses (14).

#### (b) The PMP route

Write the previous lesson's PMP in discrete time. From
$H_k = \tfrac12(x_k^\top Qx_k + u_k^\top Ru_k) + \lambda_{k+1}^\top(Ax_k + Bu_k)$,

$$
\frac{\partial H_k}{\partial u_k} = Ru_k + B^\top\lambda_{k+1} = 0,
  \qquad \lambda_k = \frac{\partial H_k}{\partial x_k} = Qx_k + A^\top\lambda_{k+1},
  \qquad \lambda_N = Q_fx_N. \tag{15}
$$

Substituting $u_k = -R^{-1}B^\top\lambda_{k+1}$ makes (15) a **linear two-point boundary value
problem** in $(x, \lambda)$. The conditioning blow-up of R4 of the previous lesson applies to
exactly this problem, so do not solve it directly. Instead insert the **ansatz** R2 handed us,
$\lambda_k = P_kx_k$ (this is the "Riccati sweep"):

$$
P_kx_k = Qx_k + A^\top P_{k+1}x_{k+1} = Qx_k + A^\top P_{k+1}(Ax_k + Bu_k),
$$
$$
Ru_k + B^\top P_{k+1}(Ax_k + Bu_k) = 0 \;\Longrightarrow\; u_k = -S_k^{-1}B^\top P_{k+1}Ax_k.
$$

The second equation **is** (12), and substituting it into the first gives (13). Since $x_k$ is
arbitrary, both can be read as matrix identities. At the terminal time $\lambda_N = Q_fx_N$ gives
$P_N = Q_f$.

**What this bought us**: the two-point boundary value problem has been split into a **backward
Riccati recursion plus a forward state propagation**. The conditioning $e^{2\sigma T}$ disappeared
because the unknowns were not collected at $t=0$ but **decomposed stage by stage** — the Riccati
recursion is the "multiple shooting" logic of R4 of the previous lesson pushed to its limit on a
linear problem.

#### (c) The completion-of-squares route

This route uses neither an ansatz nor induction. **Define** $P_k$ by (5) and verify directly, for
an arbitrary control sequence, that at each stage

$$
\tfrac12 x_k^\top P_kx_k - \tfrac12x_{k+1}^\top P_{k+1}x_{k+1}
  + \tfrac12(x_k^\top Qx_k + u_k^\top Ru_k)
  = \tfrac12(u_k + K_kx_k)^\top S_k(u_k + K_kx_k) \tag{16}
$$

(problem P2). Summing (16) over $k = 0, \dots, N-1$ makes the $x_k^\top P_kx_k$ terms on the left
**telescope**, and $\tfrac12 x_N^\top P_Nx_N = \tfrac12x_N^\top Q_fx_N$ meets the terminal cost,
producing (6). The right-hand side of (6) has every term $\ge 0$ because $S_k \succ 0$, and it is
**exactly zero** when $u_k = -K_kx_k$. So

- $J \ge \tfrac12x_0^\top P_0x_0$ for **every** control sequence (a lower bound), and
- equality is achieved at $u_k = -K_kx_k$ (the bound is attained).

That is the proof of optimality. (6) is the verification theorem written out by hand for LQR, and
it also hands us, for free, a measure of how far a trajectory is from optimal,
$\sum \lVert u_k + K_kx_k\rVert_{S_k}^2$ — the quantity used for the expected cost reduction and
line search of `c4-ilqr-ddp`.

**Where the assumptions break**: all three routes used $R \succ 0$. If $R$ is singular, $S_k$ can
be singular too (when some direction of $B$ lies in the null space of $P_{k+1}$) and the minimum
in (12) is not unique — the "cheap control" limit, which in the extreme $R = 0$ drives the optimal
control to an impulse. And if $Q \succeq 0$ fails and $Q$ is indefinite, the Hessian in $u$ may
still be $S_k \succ 0$, so each stage has a minimum, but $P_k$ can diverge (the value function
going to $-\infty$ in finite time at a **conjugate point**). On a finite horizon, test whether
$P_k$ diverges by checking that $S_k \succ 0$ holds at every $k$.

### R4 — convergence of the Riccati recursion and closed-loop stability

The proof is in the "Proof sketch" section. Here we only separate out the point that **the two
hypotheses do different jobs**.

- **Stabilizability of $(A,B)$** → $P^{(n)}$ is **bounded**. Any stabilizing gain $\bar{K}$ has
  finite infinite-horizon cost, and the optimum cannot be worse, so $P^{(n)} \preceq \bar{P}$ for
  all $n$.
- **Detectability of $(A, Q^{1/2})$** → the limit **stabilizes**. Without it, unstable modes "that
  the cost cannot see" appear.

Pin the second one down numerically. Take $n = m = 1$, $A = 2$, $B = 1$, $Q = 0$, $R = 1$. Here
$(A,B)$ is stabilizable, but since $Q = 0$ the pair $(A, Q^{1/2}) = (2, 0)$ is not detectable. The
DARE reads

$$
P = 0 + 4P - \frac{(2P)^2}{1 + P} \;\Longrightarrow\; P(1+P) = 4P(1+P) - 4P^2
  \;\Longrightarrow\; P^2 = 3P, \tag{17}
$$

so there are **two** PSD solutions: $P = 0$ and $P = 3$.

- $P = 0$: $K = 0$, closed loop $A - BK = 2$, $\rho = 2 > 1$ — **unstable**. And yet, since
  $Q = 0$, the cost is zero no matter how far the state diverges, so this really **is** optimal.
- $P = 3$: $K = (1+3)^{-1}\cdot 1\cdot 3\cdot 2 = 1.5$, closed loop $2 - 1.5 = 0.5$, $\rho = 0.5$
  — the stabilizing solution.

Running the backward recursion from $Q_f = 0$ gives $P_k \equiv 0$, so it **converges to the
non-stabilizing solution**. Running it from $Q_f = 1$ converges to $P \to 3$
($1 \to 2 \to 2.6\overline{6} \to 2.9091 \to \cdots$). This is condition 4 of the reproduction
task. The lesson: **"LQR always stabilizes" is false.** Choosing $Q$ so that it sees every
unstable mode (i.e. so the pair is detectable) is the designer's responsibility, and when picking
a numerical solver one must be conscious of **which DARE solution it converges to** (selecting the
stabilizing solution is the purpose of Schur-decomposition solvers and of
[Kleinman's 1968](https://doi.org/10.1109/TAC.1968.1098829) iteration).

### R5 — the LQG separation theorem

The problem: $x_{k+1} = Ax_k + Bu_k + w_k$, $y_k = Cx_k + v_k$, with the cost the expectation of
(1). The control $u_k$ must be a function of the measurement history $y_{0:k}$ (the **information
constraint**).

The key step is to split the state into **estimate plus error**: $x_k = \hat{x}_k + e_k$ with
$\hat{x}_k = \mathbb{E}[x_k\mid y_{0:k}]$. By the definition of conditional expectation
$\mathbb{E}[e_k \mid y_{0:k}] = 0$, hence $\mathbb{E}[e_k^\top h(y_{0:k})] = 0$ for **any**
function $h$ of $y_{0:k}$ (orthogonality). Both $\hat{x}_k$ and $u_k$ are such functions, so

$$
\mathbb{E}[x_k^\top Qx_k]
  = \mathbb{E}[\hat{x}_k^\top Q\hat{x}_k] + 2\,\mathbb{E}[e_k^\top Q\hat{x}_k] + \mathbb{E}[e_k^\top Qe_k]
  = \mathbb{E}[\hat{x}_k^\top Q\hat{x}_k] + \mathbb{E}[e_k^\top Qe_k]. \tag{18}
$$

The second term **does not depend on the control** — in a linear Gaussian system the estimation
error covariance $\Sigma_k = \mathbb{E}[e_ke_k^\top]$ is determined by the Kalman filter's own
Riccati recursion, in which $u$ does not appear (the control moves $\hat{x}$ but does not change
the error — because of linearity and additive noise). So the total cost splits as

$$
J = \underbrace{\tfrac12\mathbb{E}\Big[\sum(\hat{x}_k^\top Q\hat{x}_k + u_k^\top Ru_k) + \hat{x}_N^\top Q_f\hat{x}_N\Big]}_{\text{control-dependent}}
  + \underbrace{\tfrac12\sum\operatorname{tr}(Q\Sigma_k) + \tfrac12\operatorname{tr}(Q_f\Sigma_N)}_{\text{constant, control-independent}}. \tag{19}
$$

The first term is an **LQR problem with additive white noise** for the dynamics of $\hat{x}$,

$$
\hat{x}_{k+1} = A\hat{x}_k + Bu_k + L_{k+1}\underbrace{(y_{k+1} - C(A\hat{x}_k + Bu_k))}_{\text{the innovation, white}}. \tag{20}
$$

Applying the DP of (2) to it, the only thing the noise adds to the quadratic ansatz is a term of
the form $\tfrac12\operatorname{tr}(P_{k+1}\Lambda_{k+1})$, **independent of $u$**, so the
minimiser is **identical** to the deterministic (12). That is (8), and the gain $K_k$ does not
depend on $W$ or $V$.

**Where the assumptions break — four ways**

1. **It is not robustness (Doyle 1978).** (8) is optimal for the **expected cost under an exact
   model**. Doyle took $A = \begin{bmatrix}1&1\\0&1\end{bmatrix}$,
   $B = \begin{bmatrix}0\\1\end{bmatrix}$, $C = \begin{bmatrix}1&0\end{bmatrix}$,
   $Q = q\begin{bmatrix}1&1\\1&1\end{bmatrix}$, $W = \sigma\begin{bmatrix}1&1\\1&1\end{bmatrix}$,
   $R = V = 1$, and showed that the interval of input gains $m$ for which the loop stays stable
   **shrinks to a point** as $q = \sigma \to \infty$. Numerically: at $q = \sigma = 1$,
   $m \in (0.9208, 1.056)$; at $q = \sigma = 10^4$, $m \in (0.9905, 1.0000)$ (problem P5). LQR
   alone has a guaranteed gain margin of $(\tfrac12, \infty)$, but **inserting an observer
   destroys that guarantee.**
2. **Where certainty equivalence fails.** If the noise enters **multiplicatively** in the state or
   control (model parameter uncertainty), the expected cost acquires products of $u$ with the
   covariance, so the optimal gain depends on the covariance. The control then has a component
   that "shakes the system deliberately to gain information" (dual control).
3. **When the information constraint is not linear.** If $U$ is constrained
   ($\lvert u\rvert \le 1$) or the cost is not quadratic, the decomposition (19) fails. The
   optimal policy of constrained LQG is in general not a linear function of $\hat{x}$, and
   practice turns to MPC (`c4-mpc`).
4. **When the noise is not Gaussian.** The orthogonality in (18) is a property of conditional
   expectation and survives without Gaussianity, but the claim that **the Kalman filter computes**
   $\hat{x}_k = \mathbb{E}[x\mid y]$ is the Gaussian assumption. Without it the Kalman filter is
   only the optimal **linear** estimator, and the separation theorem weakens to "optimal among
   linear policies".

## Proof sketch

### R1 — the verification theorem [D3]

**Hypotheses**
H1: $W \in C^1(\mathbb{R}^n \times [0, t_f])$ satisfies (3) and $W(x, t_f) = \varphi(x)$ at every
$(x,t)$.
H2: at each $(x,t)$ the minimum in (3) is attained at some $u^\sharp(x,t) \in U$, and the
trajectory generated by that feedback, $\dot{x} = f(x, u^\sharp(x,t), t)$, exists on
$[t_0, t_f]$.
H3: $\ell$ and $f$ are smooth enough to integrate (as in H1 of the previous lesson).

**Conclusion** C: $W(x_0, t_0) = V(x_0, t_0)$ and $u^\sharp$ is an optimal feedback.

**Strategy**: read (3) as "an inequality along any admissible control, an equality along
$u^\sharp$", integrate from $t_0$ to $t_f$ to **bound the cost from below**, and then **attain**
that bound. It is the generalisation of the completion of squares (6).

1. **Pick any admissible control $u(\cdot)$.** Along its trajectory $x(\cdot)$,
   $\frac{d}{dt}W(x(t),t) = W_t + W_x f(x,u,t)$.
2. **Write (3) as an inequality.** Since (3) is a minimum, for any $u$ we have
   $-W_t \le \ell(x,u,t) + W_x f(x,u,t)$, i.e.
   $$\frac{d}{dt}W(x(t),t) \ge -\ell(x(t), u(t), t).$$
3. **Integrate.** From $t_0$ to $t_f$,
   $W(x(t_f), t_f) - W(x_0,t_0) \ge -\int_{t_0}^{t_f}\ell\,dt$, and the terminal condition of H1
   gives
   $$W(x_0, t_0) \le \int_{t_0}^{t_f}\ell\,dt + \varphi(x(t_f)) = J[u].$$
   Since $u$ was arbitrary, $W(x_0,t_0) \le \inf_u J[u] = V(x_0,t_0)$ — a **lower bound**.
4. **Attain the bound.** With $u = u^\sharp$, step 2 is an **equality**, hence so is step 3, and
   $W(x_0,t_0) = J[u^\sharp] \ge V(x_0,t_0)$.
5. Combining 3 and 4, $W = V$ and $J[u^\sharp] = V$, so $u^\sharp$ is optimal. **C**.

**Deleting a hypothesis: where does it collapse?**

- **Delete the $C^1$ of H1**: $\frac{d}{dt}W$ of step 1 does not exist. The minimum-time double
  integrator from R2's failure mode is such a case, its value function being non-differentiable on
  the switching curve. Reading (3) in the **viscosity** sense restores an analogue of the
  verification theorem, but the classical calculus of step 1 becomes a sub/superdifferential
  inequality ([Crandall & Lions 1983](https://doi.org/10.1090/S0002-9947-1983-0690039-8)).
- **Delete the attainment in H2**: the lower bound of step 3 still holds but step 4 is impossible,
  leaving only $W \le V$. $W$ becomes a **function supplying a lower bound** — which is the
  skeleton of the "build lower bounds on the value function by polynomial optimization" approach
  (open problem 2 of the previous lesson): give up equality and ask only for the inequality, and
  you get a **certifiable lower bound**.
- **Delete additivity of the cost**: the whole integral argument of steps 1–3 fails. Costs like
  $\max_t g(x(t))$ must be made additive again by enlarging the state.

(Omitted: whether the $\inf$ is attained, existence and uniqueness of trajectories, and
measurability conditions on $V$. The standard statements are in the textbooks after Bellman 1954 —
see UA ch.7 and Rawlings et al. 2017 ch.2.)

### R4 — convergence of the Riccati recursion and closed-loop stability [D3]

**Hypotheses**
H1: $Q = Q^\top \succeq 0$ and $R = R^\top \succ 0$.
H2: $(A, B)$ is stabilizable — there is $\bar{K}$ with $\rho(A - B\bar{K}) < 1$.
H3: $(A, Q^{1/2})$ is detectable — there is no $z \ne 0$ with $Q^{1/2}z = 0$, $Az = \mu z$ and
$\lvert\mu\rvert \ge 1$.

**Conclusions** C1 (for $P^{(n)}$, the result of $n$ backward steps from $Q_f = 0$):
$P^{(n)} \preceq P^{(n+1)}$ and $P^{(n)} \preceq \bar{P}$, hence $P^{(n)} \to P_\infty$ and
$P_\infty$ solves the DARE. C2: under H3, $\rho(A - BK_\infty) < 1$.

**Strategy**: C1 is **monotone plus bounded convergence** (monotonicity comes from the analytic
meaning of the value function). C2 uses $V(x) = \tfrac12x^\top P_\infty x$ as a **Lyapunov
function**: if an unstable mode existed, its cost would have to be zero, contradicting H3.

1. **Monotonicity.** The analytic meaning of $P^{(n)}$ is "the optimal cost with $n$ stages to go
   and no terminal cost":
   $\tfrac12x^\top P^{(n)}x = \min_{u_{0:n-1}}\tfrac12\sum_{k=0}^{n-1}(x_k^\top Qx_k + u_k^\top Ru_k)$.
   The optimum of the $(n+1)$-stage problem pays one more stage cost, which is $\succeq 0$, so it
   cannot be smaller: the first $n$ stages of any $(n+1)$-stage control sequence cost at least the
   $n$-stage optimum, and the remaining stage costs $\ge 0$. Hence
   $x^\top P^{(n+1)}x \ge x^\top P^{(n)}x$ for every $x$.
2. **Boundedness.** Using H2's $\bar{K}$ as a **fixed policy**, its infinite-horizon cost is
   $\tfrac12x^\top\bar{P}x$, where $\bar{P}$ solves the discrete Lyapunov (Stein) equation
   $\bar{P} = Q + \bar{K}^\top R\bar{K} + (A - B\bar{K})^\top\bar{P}(A-B\bar{K})$ and is
   **finite** (the series converges because $\rho(A - B\bar{K}) < 1$). The optimum is no worse
   than this fixed policy, so $P^{(n)} \preceq \bar{P}$.
3. **Convergence.** For each fixed $x$, the sequence $x^\top P^{(n)}x$ is monotone increasing and
   bounded above, hence convergent (scalar monotone convergence). The limiting values define a
   quadratic form, and the polarisation identity
   $4y^\top Pz = (y+z)^\top P(y+z) - (y-z)^\top P(y-z)$ recovers entrywise convergence. Call the
   limit $P_\infty$; since $S = R + B^\top PB \succ 0$ persists in the limit, the right-hand side
   of (5) is continuous in $P$ and $P_\infty$ satisfies the DARE.
4. **A Lyapunov identity.** Writing the Joseph form (14) of the DARE with
   $A_c := A - BK_\infty$,
   $$P_\infty - A_c^\top P_\infty A_c = Q + K_\infty^\top RK_\infty \succeq 0,$$
   so along the closed-loop trajectory $x_{k+1} = A_cx_k$,
   $$2\big(V(x_{k+1}) - V(x_k)\big) = -x_k^\top(Q + K_\infty^\top RK_\infty)x_k \le 0. \tag{21}$$
5. **The contradiction.** Suppose $A_c z = \mu z$ with $\lvert\mu\rvert \ge 1$ and $z \ne 0$.
   Summing (21) from $k = 0$ along the trajectory $x_k = \mu^kz$, the left-hand side is
   $2(\lvert\mu\rvert^{2N} - 1)V(z) \ge 0$ while the right-hand side is
   $-\sum_{k<N}\lvert\mu\rvert^{2k}z^\top(Q + K_\infty^\top RK_\infty)z \le 0$. For both signs to
   be possible we need $z^\top(Q + K_\infty^\top RK_\infty)z = 0$, and since $Q \succeq 0$ and
   $R \succ 0$ that means $Q^{1/2}z = 0$ **and** $K_\infty z = 0$. But then
   $Az = A_cz + BK_\infty z = \mu z$, so $z$ is an eigenvector of $A$ with
   $\lvert\mu\rvert \ge 1$ and $Q^{1/2}z = 0$ — contradicting H3. Hence $\rho(A_c) < 1$. **C2**.

**Deleting a hypothesis: where does it collapse?**

- **Delete H3 (detectability)**: the contradiction of step 5 disappears. Indeed for $A = 2$,
  $B = 1$, $Q = 0$, $R = 1$ the DARE has the two PSD solutions $P \in \{0, 3\}$, and
  $P_\infty = 0$ gives $\rho(A_c) = 2$ — the numerical example in R4's derivation. "Optimal" and
  "stable" are **different things**.
- **Delete H2 (stabilizability)**: the boundedness of step 2 fails and $P^{(n)} \to \infty$.
  Analytically, an unstable mode the control cannot reach is visible to $Q$, so the cost diverges.
  On a finite horizon everything is still well defined, so **finite-horizon LQR is still
  computable** — it is only that the gains do not converge as the horizon grows.
- **Delete $R \succ 0$ from H1**: step 3 loses invertibility of $S$. Weakening to
  $R \succeq 0$ allows $S_k$ to be singular, and writing (5) with a pseudo-inverse amounts to
  picking the minimum-norm solution, so the optimal control loses uniqueness.
- **Delete the premise of monotonicity, "start from $Q_f = 0$"**: for $Q_f \succ 0$, $P^{(n)}$
  need not be monotone (it may come down from above). Convergence still holds — in R4's numerical
  example, starting from $Q_f = 1$ gives $1 \to 2 \to 2.667 \to 2.909 \to \cdots \to 3$, rising
  **from below** to the stabilizing solution. Monotonicity is a convenience of the proof, weaker
  than the conclusion.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R3)** Show that (13) and the Joseph form (14) are the same equation. Then
write a paragraph on why (14) is better in floating point.
*Solution sketch*: verify $K^\top S K = A^\top PBK$ and $K^\top B^\top PA = A^\top PBK$ by
substituting $K = S^{-1}B^\top PA$, then expand (14) and watch two of the three cross terms
cancel. For the numerical part, note "all three terms are $\succeq 0$, so symmetry and
definiteness survive round-off" against "(13) is a difference of two large positive quantities,
which cancels catastrophically".

**P2 (derivation, ★★, R3)** Expand the completion-of-squares identity (16) from the left-hand side
all the way. Then sum (16) over $k$ to obtain (6), and write how "$u_k = -K_kx_k$ is the unique
optimum" follows from (6). Where is $S_k \succ 0$ needed?
*Solution sketch*: substitute $x_{k+1} = Ax_k + Bu_k$ and (13) into the left-hand side and collect
into quadratic forms in $x_k$ and $u_k$. The $u_ku_k$ coefficient is $S_k$, the $x_ku_k$ cross
coefficient is $S_kK_k$, and the $x_kx_k$ coefficient is $K_k^\top S_kK_k$, which completes the
square. Uniqueness comes from $S_k \succ 0$: only one $u_k$ makes each term of (6) vanish. With
only $S_k \succeq 0$ the optimum becomes an affine subspace.

**P3 (proof, ★★★, R4)** Show that the **stabilizing solution of the DARE is unique among PSD
solutions**: if $P_1$ and $P_2$ both satisfy the DARE and both give $\rho(A - BK_i) < 1$, then
$P_1 = P_2$.
*Solution sketch*: the strategy is "show the difference $\Delta := P_1 - P_2$ satisfies a Stein
equation $\Delta = A_{c,1}^\top\Delta A_{c,2}$ with **stable** coefficients, whose unique solution
is $0$". Subtract the two DAREs and substitute $K_i = S_i^{-1}B^\top P_iA$, then tidy the cross
terms into that form. The key fact: if $\rho(M_1)\rho(M_2) < 1$, the only solution of
$\Delta = M_1^\top\Delta M_2$ is $\Delta = 0$ (iterate: $\Delta = (M_1^\top)^k\Delta M_2^k \to 0$).
Also write one line on why this argument does **not** apply to non-stabilizing solutions.

**P4 (numerical, ★, R4)** Write the CARE for the continuous-time scalar problem
$\dot x = ax + bu$, $J = \tfrac12\int_0^\infty(qx^2 + ru^2)dt$ and find its positive solution. For
$a = b = q = r = 1$, give $P$, $K$ and the closed-loop pole to ten decimal places, and say how
they relate to $\sigma = \sqrt{a^2+q}$ from (23) of the previous lesson.
*Answer*: the CARE is $2aP - b^2P^2/r + q = 0$, so
$P = (r/b^2)\big(a + \sqrt{a^2 + qb^2/r}\big)$. With $a=b=q=r=1$,
$$
P = 1 + \sqrt{2} = 2.4142135624, \quad K = bP/r = 2.4142135624, \quad a - bK = -\sqrt2 = -1.4142135624
$$
(tolerance $10^{-9}$). The closed-loop pole is exactly $-\sigma$ — the unstable eigenvalue of the
indirect method flipped into the **stable** pole of the LQR loop, which is the same act as
selecting the stable half of the $\pm$ pair in the Hamiltonian spectrum. *Check*: substitute $P$
into the CARE and confirm a residual $< 10^{-12}$.

**P5 (numerical, ★★, R5)** Reproduce Doyle's 1978 example numerically. With
$A = \begin{bmatrix}1&1\\0&1\end{bmatrix}$, $B = \begin{bmatrix}0\\1\end{bmatrix}$,
$C = \begin{bmatrix}1&0\end{bmatrix}$, $Q = qM$, $W = \sigma M$
($M = \begin{bmatrix}1&1\\1&1\end{bmatrix}$), $R = V = 1$, compute the LQR gain $K$ and the Kalman
gain $L$, and find by bisection the interval of input gains $m$ for which the loop
($\dot x = Ax - mBK\hat{x}$, $\dot{\hat{x}} = A\hat x - BK\hat x + LC(x - \hat x)$) is stable, for
$q = \sigma \in \{1, 10, 10^2, 10^3, 10^4\}$.
*Answer*: $K = L = \big(2 + \sqrt{4+q}\big)\begin{bmatrix}1 & 1\end{bmatrix}$ (tolerance
$10^{-8}$; $4.2360679775$ at $q = 1$ and $102.0199980$ at $q = 10^4$). The stable interval is
$m \in (0.920844,\ 1.056)$ at $q=\sigma=1$ and $m \in (0.990486,\ 1.0000)$ at $q=\sigma=10^4$ —
the upper margin converges to 1 (tolerance $10^{-4}$).
*Checks*: first confirm that at $m = 1$ all closed-loop eigenvalues have negative real part
(otherwise the premise of the bisection is broken), and check $K$ against the CARE residual. With
the same code, confirm that LQR alone ($u = -Kx$, no $L$) has the stable interval
$m \in (\tfrac12, \infty)$, for contrast.

**P6 (implementation, ★★, R1 and R2)** Compute the value function $V(x)$ = minimum time to the
origin for the minimum-time double integrator ($\dot x_1 = x_2$, $\dot x_2 = u$,
$\lvert u\rvert\le1$) on a grid, then plot $\partial V/\partial x$ by central differences and show
that the gradient jumps across the switching curve $x_1 = -\tfrac12x_2\lvert x_2\rvert$.
*Rubric*: (a) the grid solution converges to the closed form (the two bang-bang arcs integrated
analytically) at first order in the grid spacing; (b) plotting $\partial V/\partial x_1$ along a
line crossing the switching curve, you show the discontinuity **does not vanish as the grid is
refined** (it is not numerical noise); (c) you write a paragraph saying that (4) is undefined at
those points while the PMP still supplies two costates; (d) one sentence on why viscosity
solutions are needed.

**P7 (counterexample, ★★, R4)** Show in **two different ways** that "LQR always stabilizes the
closed loop" is false: (i) an example where detectability fails and the recursion converges to a
non-stabilizing DARE solution, and (ii) an example with $Q \succ 0$ where the closed loop is
unstable on a **finite** horizon (the horizon being so short there is no reason to stabilize yet).
*Property checklist*: for (i) use $A=2,B=1,Q=0,R=1$ from R4's derivation, and additionally show
that changing $Q_f$ between $0$ and a positive value changes which solution the recursion reaches.
For (ii) take $N = 1$ and $Q_f = 0$ and it falls out immediately — $K_0 = 0$, so the state
diverges for one stage. Properties to check: that finite-horizon LQR has a **time-varying** gain
so "closed-loop stability" is not even defined for it, and that $\rho(A - BK_k)$ can exceed 1 at
some $k$.

**P8 (paper, ★★, R5)** Read Doyle's two pages and write, in at most three sentences each: (a) the
**exact proposition** the author refutes; (b) why $q, \sigma \to \infty$ is needed in the
counterexample; (c) what robotics actually adopted in response (what is used instead of LQG).
*Rubric*: (a) must identify the proposition "there are **guaranteed** gain and phase margins for
LQG designs"; writing "LQG is bad" fails. (b) should note that growing the weights grows the gains
and creates a structure in which the observer poles cancel the plant's unstable modes, destroying
the margin. (c) passes if it names one of $\mathcal{H}_\infty$ / LQG-LTR, or MPC with explicit
constraints and replanning, and states what that approach guarantees.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read with three passes, attacking questions 4, 5, 6 and 7 on the third.

1. **Bellman, "The theory of dynamic programming" (1954, Bull. Amer. Math. Soc.)** — role:
   `seminal`. <https://doi.org/10.1090/S0002-9904-1954-09848-8>
   What to read: all of it (14 pages). Note **which problem classes** the principle of optimality
   and the functional equation were proposed for (sequential decisions, inventory, search).
   Extra questions: (a) when Bellman speaks of the "curse of dimensionality", what exactly is he
   counting — a state grid, or a policy space? (b) Does this paper contain a **convergence
   proof**, or is it a proposal of the functional equation? If the latter, who closed the gap?
   (c) Within this paper's framework, where is the $C^1$ assumption of (3) hiding?
2. **Kalman, "Contributions to the theory of optimal control" (1960, Bol. Soc. Mat. Mexicana; the
   URL above is the 2009 IEEE Press reprint)** — role: `seminal`.
   <https://doi.org/10.1109/9780470544334.ch8>
   What to read: the sections setting up LQR and the Riccati equation, and the discussion of
   stability and controllability.
   Extra questions: (a) which of the three routes of this lesson is Kalman's derivation closest
   to? (b) When he says "optimality gives stability", what assumption is he using implicitly, and
   which side of it does R4's counterexample break? (c) This result is stated in continuous time —
   can it be recovered in discrete time by $\Delta \to 0$?
3. **Doyle, "Guaranteed margins for LQG regulators" (1978, IEEE T-AC)** — role: `critique`.
   <https://doi.org/10.1109/TAC.1978.1101812>
   What to read: all of it (2 pages). This is the shortest and the most important reading of the
   lesson.
   Extra questions: (a) why does **one** counterexample suffice (look at the form of the
   proposition)? (b) Why does the author grow $q$ and $\sigma$ together — what happens if only one
   grows (confirm with P5)? (c) What does this paper **not** claim — where does the reading "LQG is
   always fragile" go wrong?

**The ten fixed questions**: (1) What problem is solved, under what assumptions? (2) What exactly
could prior work not do? (3) Reduce the core idea to one equation. (4) What are the theoretical
guarantees, and **what is not guaranteed**? (5) What are the independent and dependent variables
and the baselines, and were the baselines tuned fairly? (6) Do the metrics match the claims, and
are variance and seeds reported? (7) What information needed for reproduction is missing? (8) If
the result were wrong, which assumption would you doubt first? (9) What are the computational and
memory complexity and the real-time behaviour? (10) What would you change to go beyond this paper
in a year?

## Reproduction task

**Tier R1 (numerical check).** Compute budget: one notebook CPU core, under 1 minute total, under
200 MB of memory. numpy and scipy only (`scipy.linalg.solve_discrete_are`, `eig`). No simulator.

**Input data**: none; everything is given as constants. The reference system is the discretised
double integrator ($\Delta t = 0.1$):

$$
A = \begin{bmatrix} 1 & 0.1 \\ 0 & 1\end{bmatrix}, \quad
B = \begin{bmatrix} 0.005 \\ 0.1 \end{bmatrix}, \quad
Q = I_2, \quad R = [1], \quad Q_f = I_2, \quad x_0 = (1, 0).
$$

**The task**: (i) compute $K_\infty$ by **four independent methods** — the recursion (13), the
Joseph-form recursion (14), `solve_discrete_are`, and an eigenvalue method that reads $P$ off the
**invariant subspace inside the unit circle** of the symplectic matrix
$Z = \begin{bmatrix} A + GA^{-\top}Q & -GA^{-\top} \\ -A^{-\top}Q & A^{-\top}\end{bmatrix}$ with
$G = BR^{-1}B^\top$; (ii) check the closed-loop poles; (iii) confirm numerically that the three
derivations of R3 agree; (iv) reproduce R4's detectability counterexample.

**Acceptance criteria** — all four must hold to pass.

1. **The four methods agree.** Taking the 20000-step recursion as the reference,
   $$
   K_\infty = \begin{bmatrix} 0.917074563114 & 1.635596185047 \end{bmatrix}, \qquad
     P_\infty = \begin{bmatrix} 17.834931322189 & 10.012492197250 \\
       10.012492197250 & 17.856586460329 \end{bmatrix}
   $$
   and the pairwise differences of the four methods satisfy
   $\max\lVert \Delta K\rVert_\infty < 10^{-10}$ and
   $\max\lVert\Delta P\rVert_\infty < 10^{-10}$ (for reference, the author's implementation gave
   $3.8\times10^{-14}$ and $4.9\times10^{-13}$). In the eigenvalue method, the stable eigenvalues
   of $Z$ are a **complex conjugate pair**, so the real invariant subspace must be taken as
   $[\operatorname{Re}v, \operatorname{Im}v]$ — using the real parts of both columns gives a
   singular matrix (see the failure table).
2. **The closed loop is stable.** The eigenvalues of $A - BK_\infty$ are
   $0.915927504340 \pm 0.045853692377\,i$ with $\rho = 0.917074563114$, matching to within
   $10^{-9}$, and $\rho < 1$. Also check that the moduli of $Z$'s four eigenvalues,
   $\{0.917074563114,\ 0.917074563114,\ 1.090423876336,\ 1.090423876336\}$, split 2:2 about the
   unit circle (the outer two are the reciprocals of the inner two — the discrete-time version of
   the $\pm$ pair of R4 of the previous lesson).
3. **The three derivations agree.** With $N = 60$ and $Q_f = I$: (a) solve the linear two-point
   boundary value problem (15) directly as one dense linear system and verify
   $\max_k\lVert\lambda_k - P_kx_k\rVert_\infty < 10^{-10}$ ((4) of R2); (b) the $u_k$ so obtained
   matches $-K_kx_k$ to within $\max_k\lVert\cdot\rVert_\infty < 10^{-10}$; (c) the completion of
   squares (6) holds for **200 random** control sequences to within
   $\lvert J(u) - \tfrac12x_0^\top P_0x_0 - \tfrac12\sum(u_k+K_kx_k)^\top S_k(u_k+K_kx_k)\rvert
   < 10^{-9}$; (d) the optimal cost $\tfrac12x_0^\top P_0x_0 = 8.91648483301953$ agrees with the
   actual rollout cost to within $10^{-12}$.
4. **The detectability counterexample.** For $A = [2]$, $B = [1]$, $Q = [0]$, $R = [1]$:
   (a) 500 backward steps from $Q_f = 0$ give exactly $P = 0$, $K = 0$ and
   $\rho(A-BK) = 2$; (b) 500 steps from $Q_f = 1$ give $P = 3$, $K = 1.5$ and $\rho = 0.5$ to
   within $10^{-10}$; (c) `solve_discrete_are` returns $P = 3$ (the stabilizing solution);
   (d) so confirm by hand from the quadratic (17) that the DARE has the two PSD solutions
   $\{0, 3\}$, and record in your report that (a) and (c) select **different** solutions.

**Baselines**: (i) `scipy.linalg.solve_discrete_are` is the primary baseline (an independent
implementation). (ii) The two-point boundary value problem of condition 3 is a second baseline,
independent of DP. (iii) For condition 4 the baseline is the hand-solved quadratic (17) giving
$P \in \{0,3\}$.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The eigenvalue method dies with `Singular matrix` | the stable eigenvalues are a complex conjugate pair but you used the real parts of both eigenvectors | print the imaginary parts of the eigenvalues; if they are a pair, build the subspace as $[\operatorname{Re}v, \operatorname{Im}v]$ |
| $P$ drifts asymmetric as it grows | you used form (13) and round-off accumulated | switch to the Joseph form (14), or symmetrise with $(P+P^\top)/2$ each step; check the difference between the two results is inside condition 1's tolerance |
| The recursion oscillates instead of converging to $K$ | the $\tfrac12$ convention was applied to only one of $Q$ and $R$ | check whether $P_\infty$ differs from `solve_discrete_are` by exactly a factor of two — if so it is a convention mismatch |
| The boundary value problem's solution disagrees with $P_kx_k$ | the index convention of the discrete PMP — $H_k$ takes $\lambda_{k+1}$ and produces $\lambda_k$ | shrink to $N=1$ and match against the hand-solved answer |
| The completion-of-squares identity breaks on random controls | you wrote $S_k$ as $R + B^\top P_k B$ (index $k$) | check that $S_k$ uses $P_{k+1}$; at $N=1$ the difference between the two choices is immediately visible |
| In the counterexample the $Q_f = 0$ recursion goes to 3 | you entered $Q$ as a small positive number rather than zero (e.g. `1e-12`) | set $Q$ to exactly zero and check at the first step that $P_1 = Q + \cdots$ is **exactly** zero |

## Open problems

- **(open problem) The dimension at which value functions stop being usable** — DP supplies the
  sufficient condition, but grid-based computation costs $O(\text{grid}^n)$. Approximating the
  value function with a neural network raises the dimension, but there is no guarantee that the
  resulting $\hat{V}$ satisfies the **inequality** of the verification theorem (step 3 of the
  proof sketch), so nothing can be said about how close to optimal it is. Current approaches: SOS
  lower bounds for polynomial value functions
  ([Henrion & Korda 2014](https://doi.org/10.1109/TAC.2013.2283095)) and level-set computation in
  HJ reachability ([Bansal et al. 2017](https://doi.org/10.1109/CDC.2017.8263977)). What is
  missing: a **computable a posteriori gap bound** for a learned $\hat V$. The question returns in
  `c4-robust-stochastic-oc` and `c8-rl-theory`.
- **(open problem) Validity of gradient-based methods on non-smooth value functions** — the value
  function of a robot with contact is almost certainly non-differentiable, yet iLQR, DDP and
  policy gradients all use quantities of the form $\partial V/\partial x$. Viscosity-solution
  theory gives **existence and uniqueness**, but there is no general theory of in what sense the
  gradients these algorithms use are the right ones. Current approaches: non-smooth optimization
  using subdifferentials and Clarke derivatives, and smooth relaxations of contact
  (`c4-contact-implicit-hybrid`). What is missing: a **quantitative** guarantee that the solution
  converges to the original problem's as the relaxation parameter goes to zero.
- **(open problem) A robust version of the separation theorem** — after Doyle 1978,
  $\mathcal{H}_\infty$ and LQG/LTR gave designs that recover the margins, but whether estimation
  and control may be separated under a **learned model** is open. When the model error is
  correlated with the state estimation error, the orthogonality in (18) fails. Current approaches:
  combining tube MPC with set-membership estimation (`c4-mpc` and
  [Mayne et al. 2005](https://doi.org/10.1016/j.automatica.2004.08.019) in
  `c4-robust-stochastic-oc`). What is missing: a **tight** bound on closed-loop performance
  degradation given a bound on the learning error.
- **(open problem) A structural alternative to the Riccati recursion** — as $n$ grows, solving the
  DARE costs $O(n^3)$, and when it must be re-solved every cycle as in MPC this becomes the
  bottleneck. Solvers exploiting sparsity and low rank exist problem by problem, but there is no
  general theory. Current approaches: Newton iterations in the style of
  [Kleinman 1968](https://doi.org/10.1109/TAC.1968.1098829) and their low-rank variants, and
  first-order methods that never form the DARE explicitly. What is missing: a solver that is
  **nearly linear** in the state dimension, with convergence guarantees.

## Concept check

Run `rc quiz c4-dp-lqr-lqg`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

The six items cover: what the verification theorem adds over the PMP; what the costate equals in
terms of the value function; why the Joseph form of the Riccati recursion is preferred; whether
stabilizability alone guarantees a stable LQR loop; the grounds on which the LQG gain is
independent of the noise covariances; and what Doyle 1978 did and did not show.

## How to study this stage

1. **Fix the conventions first (20 min)** — write down the $\tfrac12$ convention from "Setup and
   notation". Textbooks differ by a factor of two in $P$, and it is common to lose hours to a
   wrong gain because of it. Two lines suffice: the sign convention from the previous lesson and
   the $\tfrac12$ convention here.
2. **Build (2) and (3) yourself (60 min)** — write the principle of optimality in one sentence and
   derive the HJB by the $\Delta$ expansion. Mark on the page "this is where $C^1$ was used". That
   mark is what later connects to why viscosity solutions are needed. Read UA ch.7 alongside as
   **the same result explained differently**.
3. **Reconstruct the verification theorem in four lines rather than memorising it (50 min)** —
   "(1) any control, (2) the HJB is an inequality, (3) integrating gives a lower bound, (4) at the
   minimiser it is an equality". Once you see that those four lines have the **same structure** as
   the completion of squares (6), the optimality proof of LQR and the general verification theorem
   are remembered as one thing.
4. **Derive LQR three times (120 min)** — one per day is fine. DP (quadratic ansatz), PMP (sweep),
   completion of squares. The third is the shortest and the strongest (an identity for every
   control sequence, with no ansatz and no induction). Solving P1 and P2 shows that the three
   routes really are the same algebra.
5. **Build "optimal but unstable" by hand (40 min)** — work $A=2,B=1,Q=0,R=1$ from R4's derivation
   all the way on paper to get $P \in \{0,3\}$, then switch $Q_f$ between 0 and 1 and watch the
   recursion go to **different solutions**. These twenty lines permanently erase the false memory
   that "LQR stabilizes".
6. **In the reproduction task, do condition 4 first (110 min)** — it is scalar and takes five
   minutes, and it verifies your conventions before you write the matrix code for conditions 1–3.
   Then do condition 1 (four methods); getting caught by the complex conjugate pair in the
   eigenvalue method is what makes the link between Riccati and symplectic structure stick.
7. **Read Doyle last (90 min)** — Bellman → Kalman → Doyle is this lesson's narrative. Doyle is
   two pages, but it only sticks if you **reproduce it yourself** with P5. Build the table of
   shrinking stable intervals with your own hands as $q$ grows.
8. **End with what cannot be done (30 min)** — pick one of the four open problems and write a
   paragraph on why it is still open. The first (the dimension limit) is the motivation for the
   whole of `c4-ilqr-ddp`.

**Passing bar**: you can write (12)–(13) (the DP route) and (6) (completion of squares) from a
blank page, you can reconstruct the verification theorem in four lines, you can find the two DARE
solutions of the detectability counterexample by hand, you have code satisfying all four
acceptance criteria of the reproduction task, and you have notes on all three papers.
