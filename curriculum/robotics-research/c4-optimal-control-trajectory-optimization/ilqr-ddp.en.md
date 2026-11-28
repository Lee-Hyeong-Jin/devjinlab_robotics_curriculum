---
id: c4-ilqr-ddp
lang: en
title: iLQR/DDP and regularization
summary: >-
  Derive the second-order backward pass of DDP with no missing steps, and confirm by proof sketch
  and by measurement that DDP converges quadratically because one of its iterations *is* a Newton
  step on the control sequence, while iLQR is Gauss-Newton and converges linearly. Treat why
  $Q_{uu}$ going indefinite away from the optimum makes regularization, a merit function and a
  line search mandatory, and why control box constraints can be handled exactly while state
  constraints cannot. The reproduction task measures the convergence order on a pendulum and
  solves cart-pole swing-up under a torque limit.
objectives:
  - Derive the second-order backward pass of DDP (from $Q_x$ through $V_{xx}$) with no missing steps.
  - Explain why DDP is second-order and iLQR first-order in terms of Newton against Gauss-Newton, and measure the rates numerically.
  - State the conditions under which iLQR and DDP diverge without regularization, and distinguish $Q_{uu}$ regularization from $V_{xx}$ regularization.
  - Write down and implement what the merit function and the expected-reduction ratio test do in the line search.
  - Handle control box constraints exactly by projection, and explain why the same device fails for state constraints.
tags: [optimal-control, ilqr, ddp, regularization, line-search, research]
---

# iLQR/DDP and regularization

## Setup and notation

The previous lesson used the fact that the value function of a **linear** problem closes in
quadratic form. This lesson repeats that computation **around a nominal trajectory** of a
nonlinear problem. That is iLQR/DDP, the working tool of robotics trajectory optimization. The
recommended prerequisites are the previous two lessons and module R0 (numerical optimization).

What this lesson additionally assumes:

- Numerical optimization: the difference between Newton and Gauss-Newton, line search and trust
  regions, the Armijo condition, and the definitions of quadratic and linear convergence.
- That $f_x$ and $f_u$ can be obtained by automatic differentiation or finite differences
  (`r0-ad-and-integrators`).

Notation (shared across module C4, continuing from the previous lessons):

| Symbol | Meaning |
|---|---|
| $x_k \in \mathbb{R}^n$, $u_k \in \mathbb{R}^m$ | state and control of the nominal trajectory $(\bar{x}, \bar{u})$; the subscript is the stage |
| $f(x,u)$ | discrete dynamics $x_{k+1} = f(x_k, u_k)$; $f_x, f_u$ are Jacobians and $f_{xx}$ a 3-tensor |
| $\ell(x,u)$, $\ell_f(x)$ | stage cost and terminal cost |
| $V_k(x)$ | value function at stage $k$; its quadratic model has coefficients $V_x, V_{xx}$ |
| $Q_k(\delta x, \delta u)$ | quadratic model of the one-stage action value |
| $k_k \in \mathbb{R}^m$, $K_k \in \mathbb{R}^{m\times n}$ | feedforward term and feedback gain, $\delta u = k_k + K_k\delta x$ |
| $\mu \ge 0$ | regularization strength |
| $\alpha \in (0, 1]$ | line-search step, $u_k = \bar{u}_k + \alpha k_k + K_k(x_k - \bar{x}_k)$ |
| $\Delta_1, \Delta_2$ | first- and second-order coefficients of the expected cost reduction |
| $\bar{u}$ (scalar) | control limit, $\lvert u \rvert \le \bar{u}$ |

**The $\tfrac12$ convention** is as in the previous lesson: the cost is
$J = \sum_k \ell(x_k,u_k) + \ell_f(x_N)$ and quadratic forms carry the $\tfrac12$.

**An important distinction**: **iLQR** is what you get by **dropping** the
$f_{xx}, f_{ux}, f_{uu}$ terms from the backward pass; **DDP** keeps them. They are two settings
of one algorithm, and R2 of this lesson shows that the difference shows up as the convergence
order. Papers frequently say "iLQR" and mean DDP, so check the backward-pass equations yourself.

The problem:

$$
\min_{u_{0:N-1}} \; J = \sum_{k=0}^{N-1}\ell(x_k, u_k) + \ell_f(x_N)
  \quad \text{s.t.}\quad x_{k+1} = f(x_k, u_k), \; x_0 \text{ given},
  \; \lvert u_k \rvert \le \bar{u}. \tag{1}
$$

## Key results

The bracket gives the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (the second-order backward pass of DDP) [D2]** — expanding the value function to second
  order around the nominal trajectory, the coefficients $(V'_x, V'_{xx})$ of $V' := V_{k+1}$ give
  $$
  \begin{aligned}
  Q_x &= \ell_x + f_x^\top V'_x, &
  Q_u &= \ell_u + f_u^\top V'_x, \\
  Q_{xx} &= \ell_{xx} + f_x^\top V'_{xx} f_x + V'_x \!\cdot\! f_{xx}, &
  Q_{ux} &= \ell_{ux} + f_u^\top V'_{xx} f_x + V'_x \!\cdot\! f_{ux}, \\
  Q_{uu} &= \ell_{uu} + f_u^\top V'_{xx} f_u + V'_x \!\cdot\! f_{uu}, & &
  \end{aligned} \tag{2}
  $$
  and, with no constraints, the minimiser is
  $$k = -Q_{uu}^{-1}Q_u, \qquad K = -Q_{uu}^{-1}Q_{ux}, \tag{3}$$
  while the value-function coefficients update as
  $$
  V_x = Q_x - Q_{ux}^\top Q_{uu}^{-1}Q_u, \qquad
    V_{xx} = Q_{xx} - Q_{ux}^\top Q_{uu}^{-1}Q_{ux}, \qquad
    \Delta V = -\tfrac12 Q_u^\top Q_{uu}^{-1}Q_u. \tag{4}
  $$
  Dropping the three terms of the form $V'_x \!\cdot\! f_{xx}$ gives **iLQR**.
- **R2 (convergence order: DDP second, iLQR first) [D3]** — viewing (1) as an unconstrained
  problem in $u_{0:N-1}$ alone, one DDP iteration **coincides with a Newton step** on that
  problem, hence converges locally quadratically (Liao & Shoemaker 1991). iLQR approximates the
  Hessian by the amount it dropped, making it **Gauss-Newton**, with local rate
  $$\limsup_{n\to\infty}\frac{\lVert k^{(n+1)}\rVert}{\lVert k^{(n)}\rVert} = r < 1 \tag{5}$$
  — first-order (linear) convergence, with $r$ set by the relative size of the dropped terms. On
  the pendulum of the reproduction task $r = 0.2592$ (stable to four digits), while DDP gives
  $\lVert k^{(n+1)}\rVert/\lVert k^{(n)}\rVert^2 \approx 0.02$, i.e. second order.
- **R3 (why regularization, a merit function and a line search are mandatory) [D2]** — away from
  the optimum $Q_{uu}$ can be indefinite (because of the $V'_x\!\cdot\!f_{uu}$ term in (2) and of
  a negative $V'_{xx}$), and then (3) returns a **saddle or a maximum** rather than a minimiser.
  Two regularizations are in use:
  $$
  \tilde{Q}_{uu} = Q_{uu} + \mu I \quad\text{(control regularization)}, \qquad
    \tilde{Q}_{uu} = \ell_{uu} + f_u^\top (V'_{xx} + \mu I) f_u + \cdots
    \quad\text{(state regularization, Tassa 2012)} \tag{6}
  $$
  and the latter is preferred — as $\mu \to \infty$ the former sends $k \to 0$ so the solver
  **stops on the nominal trajectory**, whereas the latter shrinks $K$ too and converges to
  **a feedback that tracks the previous trajectory**, which is what a trust region should mean.
  The step is accepted using the expected reduction
  $$
  \Delta J(\alpha) = \alpha\,\Delta_1 + \tfrac12\alpha^2\Delta_2, \quad
    \Delta_1 = \sum_k k_k^\top Q_{u,k}, \quad \Delta_2 = \sum_k k_k^\top Q_{uu,k}k_k \tag{7}
  $$
  only when its ratio to the actual reduction, $z = (J - J')/(-\Delta J(\alpha))$, exceeds a
  threshold (usually $0.1$). Without the $z$ test, steps that reduce the cost for reasons the
  model knows nothing about are accepted, and the regularization never grows.
- **R4 (control constraints exactly, state constraints not at all) [D2]** —
  $\lvert u\rvert \le \bar{u}$ can be solved exactly by the box-constrained QP of the backward
  pass,
  $$
  \min_{\delta u:\ \underline{b} \le \delta u \le \overline{b}}
    \tfrac12\delta u^\top Q_{uu}\delta u + (Q_u + Q_{ux}\delta x)^\top \delta u. \tag{8}
  $$
  For $m = 1$, **clamping the unconstrained solution to the interval** is the exact solution, and
  the feedback row of a clamped component is set to zero. For $m > 1$ a projected Newton method is
  needed (Tassa 2014). A state constraint $g(x_k) \le 0$, by contrast, **is not a constraint on
  $\delta u$**, so it cannot enter (8) and has no natural place inside the DDP structure — the
  current route is to **put it in the cost** with an augmented Lagrangian (ALTRO) or a barrier.
- **R5 (iLQR is a local method) [D2]** — (1) is non-convex and iLQR/DDP use only a quadratic
  model around the nominal trajectory, so they reach **different local optima for different
  initial guesses**. On the cart-pole of the reproduction task, a zero initial guess converges to
  $J^* = 307.815$ and a random one to $J^* = 199.299$ — same problem, same constraints,
  different solution.

## Derivation

### R1 — the second-order backward pass

Take a nominal trajectory $(\bar{x}_{0:N}, \bar{u}_{0:N-1})$ and deviations around it,
$\delta x_k = x_k - \bar{x}_k$ and $\delta u_k = u_k - \bar{u}_k$. Expand the value function to
second order on the nominal trajectory:

$$
V_k(\bar{x}_k + \delta x) \approx V_k(\bar{x}_k) + V_{x,k}^\top\delta x
  + \tfrac12 \delta x^\top V_{xx,k}\,\delta x. \tag{9}
$$

Write the Bellman equation ((2) of the previous lesson) in deviation variables; abbreviating
$V' := V_{k+1}$,

$$
V_k(\bar{x}_k + \delta x) = \min_{\delta u}\Big\{
  \ell(\bar{x}_k + \delta x,\ \bar{u}_k + \delta u)
  + V'\big(f(\bar{x}_k + \delta x,\ \bar{u}_k + \delta u)\big)\Big\}. \tag{10}
$$

Call what is inside the braces $Q_k(\delta x, \delta u)$ and expand it **to second order**. Take
the two terms separately.

**The first term (stage cost)** is just a Taylor expansion:
$\ell \approx \ell + \ell_x^\top\delta x + \ell_u^\top\delta u
+ \tfrac12(\delta x^\top \ell_{xx}\delta x + 2\delta u^\top \ell_{ux}\delta x
+ \delta u^\top \ell_{uu}\delta u)$.

**The second term** is the whole of the derivation. First expand the dynamics to second order:

$$
\delta x' := f(\bar{x}+\delta x, \bar{u}+\delta u) - \bar{x}_{k+1}
  = f_x\delta x + f_u\delta u
  + \tfrac12\Big[\delta x^\top f_{xx}\delta x + 2\,\delta u^\top f_{ux}\delta x
  + \delta u^\top f_{uu}\delta u\Big] + O(\lVert\cdot\rVert^3), \tag{11}
$$

where $f_{xx}$ and friends are 3-tensors and the bracket is a vector whose each component is one
quadratic form. Substitute this into the $V'$ of (9):

$$
V'(\bar{x}_{k+1} + \delta x') \approx V' + V_x'^\top\delta x'
  + \tfrac12\delta x'^\top V'_{xx}\delta x'.
$$

**Where the second-order part of $\delta x'$ goes is the crux.**

- In $V_x'^\top \delta x'$, the **quadratic bracket** of (11) survives:
  $\tfrac12 V_x'\!\cdot\![\delta x^\top f_{xx}\delta x + \cdots]$. These are the three terms
  $V'_x\!\cdot\!f_{xx}$, $V'_x\!\cdot\!f_{ux}$ and $V'_x\!\cdot\!f_{uu}$ of (2), and they are
  **what separates DDP from iLQR**.
- In $\tfrac12\delta x'^\top V'_{xx}\delta x'$, only the **first-order** part of (11) contributes
  at second order (the quadratic part of $\delta x'$ meeting $V'_{xx}$ is third order or higher,
  so it is dropped). That leaves
  $\tfrac12(f_x\delta x + f_u\delta u)^\top V'_{xx}(f_x\delta x + f_u\delta u)$, which gives the
  three terms $f_x^\top V'_{xx}f_x$, $f_u^\top V'_{xx}f_x$ and $f_u^\top V'_{xx}f_u$ of (2).

Collecting both terms coefficient by coefficient gives exactly (2), i.e.

$$
Q_k(\delta x, \delta u) = \text{const} + Q_x^\top\delta x + Q_u^\top\delta u
  + \tfrac12\begin{bmatrix}\delta x \\ \delta u\end{bmatrix}^\top
  \begin{bmatrix} Q_{xx} & Q_{ux}^\top \\ Q_{ux} & Q_{uu}\end{bmatrix}
  \begin{bmatrix}\delta x \\ \delta u\end{bmatrix}. \tag{12}
$$

**Minimisation.** If $Q_{uu} \succ 0$, differentiating (12) in $\delta u$ and setting it to zero
gives $Q_u + Q_{uu}\delta u + Q_{ux}\delta x = 0$, i.e.

$$\delta u^*(\delta x) = -Q_{uu}^{-1}(Q_u + Q_{ux}\delta x) = k + K\delta x, \tag{13}$$

which is (3). **$k$ is the feedforward term that corrects the nominal trajectory itself, and $K$
is feedback on the deviation.** That distinction is decisive in the forward pass (see R3).

**Value-function update.** Substitute (13) back into (12). Using
$\delta u^* = k + K\delta x$ with $k = -Q_{uu}^{-1}Q_u$ and $K = -Q_{uu}^{-1}Q_{ux}$,

$$
\begin{aligned}
Q_u^\top\delta u^* + \tfrac12 \delta u^{*\top}Q_{uu}\delta u^* + \delta u^{*\top}Q_{ux}\delta x
  &= Q_u^\top k + Q_u^\top K\delta x + \tfrac12 k^\top Q_{uu}k + k^\top Q_{uu}K\delta x \\
  &\quad + \tfrac12 \delta x^\top K^\top Q_{uu}K\delta x + k^\top Q_{ux}\delta x
  + \delta x^\top K^\top Q_{ux}\delta x.
\end{aligned}
$$

Now cancel terms using $Q_{uu}k = -Q_u$ and $Q_{uu}K = -Q_{ux}$. Since
$\tfrac12 k^\top Q_{uu}k = -\tfrac12 k^\top Q_u$, the constant term is
$Q_u^\top k - \tfrac12 k^\top Q_u = \tfrac12 Q_u^\top k = -\tfrac12 Q_u^\top Q_{uu}^{-1}Q_u$ —
the $\Delta V$ of (4). The coefficient of $\delta x$ collects to
$K^\top Q_u + Q_{ux}^\top k + K^\top Q_{uu}k = K^\top Q_u + Q_{ux}^\top k - K^\top Q_u
= Q_{ux}^\top k = -Q_{ux}^\top Q_{uu}^{-1}Q_u$, so
$V_x = Q_x - Q_{ux}^\top Q_{uu}^{-1}Q_u$. The quadratic coefficient collects the same way to
$K^\top Q_{uu}K + 2K^\top Q_{ux} = -Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$, so
$V_{xx} = Q_{xx} - Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$ — this is (4).

> **Implementation note**: the form in (4) is a "difference of two quantities", just like (13) of
> the previous lesson. Production code uses the counterpart of that lesson's Joseph form,
> $V_{xx} = Q_{xx} + K^\top Q_{uu}K + K^\top Q_{ux} + Q_{ux}^\top K$, and symmetrises with
> $(V_{xx} + V_{xx}^\top)/2$ at every step. The two forms agree once (3) is substituted
> (problem P1).

**Where the assumptions break**: (13) used $Q_{uu} \succ 0$. Even with $\ell_{uu} \succ 0$,
$Q_{uu}$ becomes indefinite if $V'_{xx}$ has a negative eigenvalue or $V'_x\!\cdot\!f_{uu}$ is
large. Then (13) is not a minimiser — growing $\delta u$ along a negative eigendirection of
$Q_{uu}$ sends the model cost to $-\infty$ and the forward pass diverges. **This is the starting
point of R3.** A second failure: the expansion (11) is valid only for small
$\lVert\delta x\rVert$ and $\lVert\delta u\rVert$ — if $k$ is large, third-order terms dominate
and the quadratic model lies. That is why $\alpha$ is needed.

### R3 — regularization, merit function, line search

#### Regularization

The two ways to fix an indefinite $Q_{uu}$ are those in (6).

**Control regularization** $\tilde{Q}_{uu} = Q_{uu} + \mu I$ is Levenberg-Marquardt. Growing
$\mu$ sends $k \to -\mu^{-1}Q_u \to 0$ and $K \to -\mu^{-1}Q_{ux} \to 0$, so in the limit the
**control stops at the nominal $\bar{u}$**. The trouble is that $\bar{u}$ is an open-loop
sequence with **no** feedback. For large $\mu$ the forward pass effectively rolls out a trajectory
that "does nothing", so the centre of the trust region becomes an **open-loop trajectory**.

**State regularization** (Tassa 2012 §III-A) adds $\mu I$ to $V'_{xx}$ instead:

$$
\tilde{Q}_{uu} = \ell_{uu} + f_u^\top(V'_{xx} + \mu I)f_u + V'_x\!\cdot\!f_{uu}, \qquad
  \tilde{Q}_{ux} = \ell_{ux} + f_u^\top(V'_{xx} + \mu I)f_x + V'_x\!\cdot\!f_{ux}. \tag{14}
$$

As $\mu \to \infty$ we get $\tilde{Q}_{uu} \approx \mu f_u^\top f_u$ and
$\tilde{Q}_{ux} \approx \mu f_u^\top f_x$, so $K \to -(f_u^\top f_u)^{-1}f_u^\top f_x$, a
**nonzero** limit. That $K$ is the least-squares feedback that "cancels $\delta x$ as far as
possible", and the forward pass rolls out a **closed loop tracking the previous trajectory**. The
centre of the trust region is the trajectory itself, which suppresses divergence — much safer at
the same $\mu$. This is why production implementations use (14).

$\mu$ is adjusted in the standard trust-region way: **shrink it when a step is accepted**
($\mu \leftarrow \mu/10$, with a floor) and **grow it when a step is rejected**
($\mu \leftarrow 10\mu$). On reaching an upper bound (around $10^{10}$) report failure and stop —
never build an infinite loop (the engineering rule: loops have a termination condition and an
iteration cap).

#### Merit function and the expected-reduction ratio

The forward pass uses the $k$ and $K$ of (13) **differently**:

$$
u_k = \bar{u}_k + \alpha\,k_k + K_k\,(x_k - \bar{x}_k). \tag{15}
$$

That $\alpha$ multiplies $k$ and **not** $K$ matters. Multiplying $K$ by $\alpha$ too would make
feedback vanish as $\alpha \to 0$, letting the nonlinear dynamics drift away from the nominal
trajectory, so that a small step gives a **worse** trajectory. $\alpha$ measures "how much to
change the nominal trajectory", not "how much feedback to use". (Problem P5 makes you see this
numerically.)

Whether to accept a step is decided with the expected reduction (7). From (4), the model reduction
of one stage was $-\tfrac12 Q_u^\top Q_{uu}^{-1}Q_u = \tfrac12 k^\top Q_u$; inserting a step
$\alpha$ makes $\delta u = \alpha k$, so the change in model cost is

$$
Q_u^\top(\alpha k) + \tfrac12(\alpha k)^\top Q_{uu}(\alpha k)
  = \alpha\,k^\top Q_u + \tfrac12\alpha^2 k^\top Q_{uu}k,
$$

and summing over stages gives (7). The **merit test** is

$$
z = \frac{J(\bar{u}) - J(u(\alpha))}{-\Delta J(\alpha)} > c \quad (c = 0.1 \text{ is standard}), \tag{16}
$$

and if $z$ fails the threshold, halve $\alpha$ and try again (backtracking). If every $\alpha$
fails, grow $\mu$ and redo the backward pass.

**Why the $z$ test is needed**: with only "accept if $J$ decreased", a large step for which the
quadratic model is utterly wrong passes whenever the cost happens to dip. Then $\mu$ shrinks
(because a step was accepted) and the next iteration tries an even larger step and diverges. $z$
measures "did it decrease by as much as the model predicted", so in a region where the model is
wrong it is the signal to **raise** $\mu$. It is the trust-region version of the Armijo condition.

**Where the assumptions break**: $\Delta J(\alpha)$ is computed from $Q_{uu}$, and computing it
from the regularized $\tilde{Q}_{uu}$ underestimates the expected reduction, making $z > 1$
common and the test toothless. **(7) must be computed with the unregularized $Q_{uu}$.** Second,
if the control was clamped at the box (R4), (7) must use the clamped $k$ — using the
unconstrained $k$ predicts a larger reduction than is possible, so $z$ is always small and the
line search fails forever.

### R4 — control boxes exactly, state constraints not at all

#### Control box constraints

The constraint $\lvert u_k\rvert \le \bar{u}$ of (1) becomes a box on $\delta u_k$ with
$\underline{b} = -\bar{u} - \bar{u}_k$ and $\overline{b} = \bar{u} - \bar{u}_k$, so the
minimisation (13) of the backward pass becomes the box-constrained QP (8). At $\delta x = 0$ (on
the nominal trajectory), looking only at the feedforward term,

$$
k = \arg\min_{\underline{b}\le\delta u\le\overline{b}}
  \tfrac12\delta u^\top Q_{uu}\delta u + Q_u^\top\delta u. \tag{17}
$$

- **For $m = 1$ it is exact.** Minimising a one-dimensional quadratic over an interval is
  **clamping** the unconstrained minimiser $-Q_u/Q_{uu}$ to the interval (it is convex since
  $Q_{uu} > 0$). No extra iteration is needed.
- **If clamped, zero the feedback row.** A $k$ stuck on a bound means that component is at an
  active constraint, and a small change in $\delta x$ leaves it on the bound. So $K = 0$ in that
  row is correct to first order. This is the projection of Tassa 2014, and for $m=1$ it is an
  exact active-set decision.
- **For $m > 1$ the active set must be found.** A box-constrained QP is solvable in polynomial
  time but has no closed form. Tassa 2014 solves it by projected Newton (factorising $Q_{uu}$
  only on the free components).

The forward pass also clamps $u_k$ to the box (a `clip` after (15)). **Both** must be done — clamp
only in the forward pass and the backward $K$ is a gain that "does not know clamping is possible",
so the line search fails; clamp only in the backward pass and the nonlinear forward pass violates
the constraint.

#### State constraints

$g(x_k) \le 0$ is a different matter. (8) is a minimisation over $\delta u$, and a state
constraint affects $\delta u$ only **several stages later**. Therefore

- there is **no place for it** in the backward pass's QP, because $\delta x_k$ is not a decision
  variable but a value handed over by the forward pass;
- clamping the state in the forward pass would **violate the dynamics** (unlike controls, states
  cannot be edited freely).

So there are only three options in practice, and all of them **put it in the cost**.
(i) **Penalty**: $\ell \mathrel{+}= \rho\max(0, g)^2$. Simple, but as $\rho$ grows $Q_{uu}$
becomes ill-conditioned, and exact constraint satisfaction needs $\rho \to \infty$.
(ii) **Augmented Lagrangian**: add multiplier terms to the penalty and get exact satisfaction at
finite $\rho$ ([ALTRO](https://doi.org/10.1109/IROS40897.2019.8967788)); an outer loop updates the
multipliers.
(iii) **Barrier / interior point**: stay inside the feasible set. The requirement that the initial
trajectory be feasible is often unrealistic in robotics.

**Where the assumptions break**: (i) and (ii) produce trajectories that **violate** the constraint
at intermediate iterations. For a constraint like collision avoidance, where violation is
physically meaningless, evaluating the dynamics and the cost on such a trajectory can itself be
meaningless. And when the active set changes between iterations, DDP's quadratic model changes
discontinuously and convergence slows sharply — that is the phenomenon seen in the reproduction
task's cart-pole when the constraint is active on 66 of 100 stages.

### R5 — iLQR is a local method

(1) is generally non-convex. iLQR/DDP use only a quadratic model around the nominal trajectory, so
the point they converge to is a **local** optimum (a point satisfying the first-order condition
$Q_u = 0$) and which one depends on the initial guess. In a problem like cart-pole swing-up, where
"swing up to the left", "swing up to the right" and "pump twice then swing up" are all possible,
there are several local optima and the cost differences reach **tens of percent**. Condition 4 of
the reproduction task measures this.

**Where the assumptions break**: reading "lower cost means a better solution" is valid only
**within** a single local solution. Comparing different local solutions requires looking not only
at the cost but at whether the trajectory is actually usable (constraint margin, sensitivity to
model error). Global solutions need multi-start, a combination with graph-based planning
(`c6-sampling-based-planning`), or convex relaxation.

## Proof sketch

### R2 — DDP converges quadratically, iLQR linearly [D3]

**Hypotheses**
H1: $f$, $\ell$ and $\ell_f$ are $C^3$ with locally Lipschitz Jacobians and Hessians.
H2: at the local optimum $u^*$, the Hessian $\nabla^2\hat{J}(u^*)$ of the reduced objective
$\hat{J}(u_{0:N-1})$ (the states eliminated by the dynamics) is positive definite.
H3: at each iteration $\alpha = 1$ is accepted and the regularization is $\mu = 0$ (the local
convergence regime).

**Conclusions** C1 (DDP): $\lVert u^{(n+1)} - u^*\rVert \le C\lVert u^{(n)} - u^*\rVert^2$.
C2 (iLQR):
$\lVert u^{(n+1)} - u^*\rVert \le r\lVert u^{(n)} - u^*\rVert + O(\lVert\cdot\rVert^2)$, with
$r < 1$ the relative size of the dropped curvature.

**Strategy**: reduce (1) to an unconstrained problem in $u$ alone, show that the backward pass
solves **exactly** the linear system of that problem's Hessian, then apply the standard
convergence theorems for Newton and Gauss-Newton.

1. **Reduce the problem.** Since $x_0$ is fixed and the dynamics are deterministic, the states are
   functions of the controls. Setting $\hat{J}(u) := J(x(u), u)$ turns (1) into the unconstrained
   problem $\min_u \hat{J}(u)$ with $Nm$ decision variables.
2. **The backward pass builds a Newton step.** The $k$-th block of $\nabla\hat{J}$ is exactly
   $Q_{u,k}$ (writing $\lambda = V_x$ from R2 of the previous lesson makes this the costate
   computation), and the blocks of $\nabla^2\hat{J}$ are expressed by the $Q_{uu}$ and $Q_{ux}$
   of (2) together with the state-transition matrices. DDP's backward pass is **the elimination,
   from the back, of that block tridiagonal linear system**, and the resulting
   $\delta u = k + K\delta x$ **equals** the solution of
   $\nabla^2\hat{J}\,\delta u = -\nabla\hat{J}$ (Liao & Shoemaker 1991, Thm. 1). So one DDP
   iteration is one Newton step. (Omitted: the lemma that the elimination is a repeated Schur
   complement and the intermediate matrices are invertible — §III of the original.)
3. **Quadratic convergence of Newton.** Under H1 and H2 the standard theorem
   (Nocedal-Wright ch.3) gives $\lVert u^{(n+1)} - u^*\rVert \le C\lVert u^{(n)} - u^*\rVert^2$.
   **C1**.
4. **iLQR changes the Hessian.** iLQR drops the $V'_x\!\cdot\!f_{xx}$-type terms from (2), so the
   linear system of step 2 uses an approximation $B \approx \nabla^2\hat{J}$ rather than
   $\nabla^2\hat{J}$. What was dropped is proportional to $V'_x$ (i.e. the costate), and $V'_x$
   does **not** go to zero at the optimum (because of the terminal conditions). So
   $B \ne \nabla^2\hat{J}$ persists in the limit — this is what makes it **different** from
   Gauss-Newton on a least-squares problem (there, the approximation error vanishes with the
   residual).
5. **A fixed Hessian error gives first-order convergence.** A modified Newton method
   $\delta u = -B^{-1}\nabla\hat J$ propagates error as
   $e^{(n+1)} = (I - B^{-1}\nabla^2\hat{J})e^{(n)} + O(\lVert e^{(n)}\rVert^2)$, so
   $$r = \rho\big(I - B^{-1}\nabla^2\hat{J}\big)$$
   is the rate. If $r < 1$ it converges linearly; if $r \ge 1$ it **does not converge**. **C2**.
6. **Numerical confirmation.** On the pendulum of the reproduction task $r = 0.2592$ is stable to
   four digits and takes the **same value** from three different initial guesses — showing that
   (5) is a property of the solution, not of the starting point. DDP on the same problem gives
   $\lVert k^{(n+1)}\rVert/\lVert k^{(n)}\rVert^2 \approx 0.02$, i.e. second order.

**Deleting a hypothesis: where does it collapse?**

- **Delete H2 (positive definite Hessian)**: the linear system of step 2 becomes singular or
  indefinite and the Newton direction is not a descent direction. The practical regularization (6)
  is exactly the device for this case — and turning it on makes $\mu > 0$, breaking H3 and
  destroying quadratic convergence. **DDP's quadratic convergence is observed only in the last few
  iterations, once the regularization is off.**
- **Delete H3 ($\alpha = 1$)**: if $\alpha < 1$ persists every iteration, the rate is governed by
  $\alpha$. In the reproduction task's cart-pole the line search picks $\alpha = 0.25$ for dozens
  of iterations, and as a result **iLQR and DDP both** show first-order convergence with a
  $\lVert k\rVert$ ratio of about $0.46$. In other words, the commonest cause of "I used DDP but
  see no quadratic convergence" is not the second-order terms but the **step size**.
- **Delete H1 ($C^3$)**: with non-smooth $f$, as in contact, $f_{xx}$ does not exist and the DDP
  terms of (2) are undefined. In relaxed contact models $f_{xx}$ is **very large** and easily
  makes $Q_{uu}$ indefinite, which is why iLQR (the one that drops the second-order terms) is the
  more stable choice on contact problems (`c4-contact-implicit-hybrid`).
- **Read it as "second-order convergence is always better"**: DDP's second-order terms are also
  the main culprit in making $Q_{uu}$ indefinite when **far** from the optimum. On the
  reproduction task's pendulum, **starting from a random initial guess, DDP hits the
  regularization ceiling and fails while iLQR converges to the same solution** — second-order
  information pays off only in the last stretch and is a liability early on. That is why the
  practical default is iLQR.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R1)** Show that the $V_{xx} = Q_{xx} - Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$ of (4)
and the implementation form
$V_{xx} = Q_{xx} + K^\top Q_{uu}K + K^\top Q_{ux} + Q_{ux}^\top K$ are the same equation once (3)
is substituted. Why use the latter?
*Solution sketch*: substituting $K = -Q_{uu}^{-1}Q_{ux}$ gives
$K^\top Q_{uu}K = Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$ and
$K^\top Q_{ux} = -Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$, so the three terms sum to
$-Q_{ux}^\top Q_{uu}^{-1}Q_{ux}$. The reason is the same as in P1 of the previous lesson (a sum of
PSD terms against a difference of two quantities).

**P2 (derivation, ★★, R1)** State precisely the claim that "the quadratic part of $\delta x'$
meeting $V'_{xx}$ is third order or higher" in the expansion (11). Then show which of the three
DDP terms in (2) vanish when $f$ is **affine in the control**, $f = a(x) + B(x)u$.
*Solution sketch*: the quadratic part of $\delta x'$ is
$O(\lVert(\delta x,\delta u)\rVert^2)$ and the quadratic form with $V'_{xx}$ has two factors, so
the cross term is $O(\lVert\cdot\rVert^3)$. Affineness gives $f_{uu} = 0$, while
$f_{ux} = \partial B/\partial x$ is generally nonzero, and $f_{xx}$ survives through the second
derivatives of $a$ and $B$. So **even in the affine case the DDP terms do not all disappear**.

**P3 (proof, ★★★, R2)** Derive the error propagation
$e^{(n+1)} = (I - B^{-1}H)e^{(n)} + O(\lVert e^{(n)}\rVert^2)$ of step 5 of the proof sketch
(with $H = \nabla^2\hat{J}(u^*)$), and write a sufficient condition for
$r = \rho(I - B^{-1}H) < 1$ in terms of the spectra of $B$ and $H$. Confirm also that $B = H$
recovers quadratic convergence.
*Solution sketch*: expand $\nabla\hat{J}(u) = H e + O(\lVert e\rVert^2)$ from
$\nabla\hat{J}(u^*) = 0$ and substitute into
$u^{(n+1)} = u^{(n)} - B^{-1}\nabla\hat{J}(u^{(n)})$. The key inequality: if $B, H \succ 0$ and
$\tfrac12 H \preceq B$, then the eigenvalues of $I - B^{-1}H$ lie in $(-1, 1)$ (use the fact that
the eigenvalues of a product of two symmetric positive definite matrices are real and positive).
With $B = H$ the first-order term vanishes, leaving $O(\lVert e\rVert^2)$.

**P4 (numerical, ★, R1)** For the scalar system
$x_{k+1} = x_k + \Delta(x_k^2 + u_k)$ with $\ell = \tfrac12(x^2 + u^2)$,
$\ell_f = \tfrac12 c x^2$, $N = 1$, $\Delta = 0.1$, $c = 10$, $\bar{x}_0 = 1$ and
$\bar{u}_0 = 0$, compute by hand every coefficient of (2) and the $k, K$ of (3). Write the iLQR
and the DDP values **separately** and say where the difference comes from.
*Answer*: $\bar{x}_1 = 1 + 0.1(1 + 0) = 1.1$, so $V'_x = c\bar{x}_1 = 11$ and $V'_{xx} = c = 10$;
$f_x = 1 + 2\Delta\bar{x}_0 = 1.2$, $f_u = \Delta = 0.1$, $f_{xx} = 2\Delta = 0.2$,
$f_{ux} = f_{uu} = 0$; $\ell_x = 1$, $\ell_u = 0$, $\ell_{xx} = \ell_{uu} = 1$, $\ell_{ux} = 0$.
Hence both methods give $Q_u = 0 + 0.1\cdot11 = 1.1$,
$Q_{uu} = 1 + 0.1\cdot10\cdot0.1 = 1.1$ and $Q_{ux} = 0 + 0.1\cdot10\cdot1.2 = 1.2$, so
$$
k = -1, \qquad K = -1.0909090909
$$
(tolerance $10^{-9}$) — **the same**. The difference appears only in $Q_{xx}$: iLQR gives
$1 + 1.2\cdot10\cdot1.2 = 15.4$ and DDP $15.4 + V'_x f_{xx} = 15.4 + 11\cdot0.2 = 17.6$.
*Checks*: since $f_{uu} = f_{ux} = 0$, there are no DDP terms in $Q_u$, $Q_{uu}$ or $Q_{ux}$ —
which is why the two methods give the **same control** on a single stage ($N=1$). The difference
only appears once it **propagates to earlier stages** through $V_{xx}$. Confirm this directly by
going to $N = 2$.

**P5 (implementation, ★★, R3)** Implement a version of the forward pass (15) in which $\alpha$
multiplies $K$ as well as $k$, and compare the iteration count and final cost of the two versions
on the reproduction task's cart-pole.
*Rubric*: (a) you show by cost that the version with $\alpha$ on $K$ gives a **worse** trajectory
at small $\alpha$; (b) you explain this as "without feedback the nonlinear dynamics drift away
from the nominal trajectory"; (c) you compare the distributions of accepted $\alpha$ for the two
versions as histograms; (d) you cap the regularization in both so neither diverges, and report
when the cap is hit and stop.

**P6 (implementation, ★★★, R3 and R5)** Get the iteration count of cart-pole swing-up **down to
20 or fewer**. The reproduction task's base setting (zero initial guess) needs on the order of a
hundred. Permitted means: warm starts (starting from the solution of an easier problem),
continuation (homotopy) in the terminal weight, lengthening the horizon, multi-start.
*Rubric*: (a) you achieve 20 or fewer iterations and also report whether that reduced the
**total computation time** (a fair comparison must include the cost of the warm start);
(b) you explain why your means worked in terms of H3 of R2 (did you enter the region where
$\alpha = 1$ is accepted?); (c) you decide by cost whether the solution found is the same local
solution as the base setting's; (d) you list each failed attempt in one line.

**P7 (counterexample, ★★, R2 and R3)** Show in **two different ways** that "DDP is always better
than iLQR" is false: (i) an initial guess for which DDP fails and iLQR converges; (ii) a problem
in which DDP's quadratic convergence is not observed because of the step size.
*Property checklist*: (i) falls straight out of giving the reproduction task's pendulum a random
initial control sequence — count the stages at which $Q_{uu}$ becomes indefinite and compare the
norm of the $V'_x\!\cdot\!f_{xx}$ term against $f_u^\top V'_{xx}f_u$. For (ii), log the accepted
$\alpha$ on the cart-pole and check whether the $\lVert k\rVert$ ratios of the two methods agree
while $\alpha < 1$ persists. The property to check: quadratic convergence is a **local** property
and means something only where the regularization is off and $\alpha = 1$.

**P8 (paper, ★★, R3 and R4)** Read §III of Tassa et al. 2012 and §III of Tassa et al. 2014, and
write: (a) which of the two regularizations in (6) the 2012 paper uses and what grounds the
authors give for the choice; (b) whether the 2014 projected Newton reduces, at $m=1$, to this
lesson's "clamp and zero the feedback row"; (c) three pieces of reproduction information the two
papers do **not** report.
*Rubric*: (a) passes if it identifies $V_{xx}$ regularization and the grounds "as
$\mu\to\infty$ it goes to a feedback tracking the previous trajectory". (b) should note that in
one dimension the active set coincides with clamping. (c) passes if it names three of
"regularization bounds, the $\alpha$ grid, the convergence threshold, how the initial trajectory
is generated, how derivatives are obtained". Writing only "there is no code" fails (the 2012 code
is public).

## Paper reading

**Four must-reads.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read with three passes, attacking questions 4, 5, 6 and 7 on the third.

1. **Mayne, "A second-order gradient method for determining optimal trajectories of non-linear
   discrete-time systems" (1966, Int. J. Control)** — role: `seminal`.
   <https://doi.org/10.1080/00207176608921369>
   What to read: the section setting up the second-order expansion. Read it against (2) of this
   lesson, comparing notation.
   Extra questions: (a) in the 1966 notation, what are the quantities corresponding to this
   lesson's $Q_{uu}$ and $V_{xx}$? (b) Does the author treat regularization or line search? If
   not, what would break if you implemented the algorithm exactly as written? (c) Is the relation
   of the name "second-order gradient method" to Newton's method explained in the author's own
   terms?
2. **Liao & Shoemaker, "Convergence in unconstrained discrete-time differential dynamic
   programming" (1991, IEEE T-AC)** — role: `standard`. <https://doi.org/10.1109/9.86943>
   What to read: the theorem that one DDP iteration equals a Newton step, and the structure of its
   proof. Step 2 of R2 comes from here.
   Extra questions: (a) which of the authors' assumptions is not among H1–H3 of this lesson?
   (b) Does "unconstrained" mean no control constraints, no state constraints, or both? (c) In the
   authors' framework, write in one sentence why the theorem does not apply to iLQR.
3. **Tassa, Erez & Todorov, "Synthesis and stabilization of complex behaviors through online
   trajectory optimization" (2012, IROS)** — role: `standard`.
   <https://doi.org/10.1109/IROS.2012.6386025>
   What to read: all of §III (regularization, line search, acceptance test). This is the primary
   source for R3 of this lesson.
   Extra questions: (a) which of the regularizations in (6) do the authors choose, and on what
   grounds? (b) The real-time performance they report (control rate) is on what hardware and at
   what model complexity? (c) Do the experiments have a baseline? If not, how could the claim be
   verified?
4. **Tassa, Mansard & Todorov, "Control-limited differential dynamic programming" (2014, ICRA)** —
   role: `standard`. <https://doi.org/10.1109/ICRA.2014.6907001>
   What to read: the box-constrained QP and projected Newton sections, and the comparisons in the
   experiments.
   Extra questions: (a) write in this lesson's R4 terms why the "naive clamping" they compare
   against fails. (b) How much does projected Newton add to the per-iteration cost relative to
   unconstrained DDP? (c) What is the structural reason this method cannot be extended to
   **state** constraints?

**The ten fixed questions**: (1) What problem is solved, under what assumptions? (2) What exactly
could prior work not do? (3) Reduce the core idea to one equation. (4) What are the theoretical
guarantees, and **what is not guaranteed**? (5) What are the independent and dependent variables
and the baselines, and were the baselines tuned fairly? (6) Do the metrics match the claims, and
are variance and seeds reported? (7) What information needed for reproduction is missing? (8) If
the result were wrong, which assumption would you doubt first? (9) What are the computational and
memory complexity and the real-time behaviour? (10) What would you change to go beyond this paper
in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one notebook CPU core, under 5 minutes total,
under 500 MB of memory. numpy only (scipy not needed). No simulator.

**Input data**: none; both systems are given as constants.

**System A — a pendulum** (for measuring convergence order; its first and second derivatives are
analytic, so the order is clean): mass $m = 1$, length $\ell = 1$, damping $b = 0.1$,
$g = 9.81$, **explicit Euler** with $\Delta t = 0.05$,

$$
x = (\theta, \dot\theta), \quad
  \dot{x} = \big(\dot\theta,\ (u - b\dot\theta - mg\ell\sin\theta)/(m\ell^2)\big),
$$

$N = 100$, $Q = \mathrm{diag}(1, 0.1)$, $R = [0.01]$, $Q_f = \mathrm{diag}(200, 20)$,
$x_0 = (\pi, 0)$ (hanging down), $x_{\mathrm{goal}} = (0,0)$, no control constraint. The only
nonzero component of $f_{xx}$ is
$\partial^2 f_2/\partial\theta^2 = \Delta t\,(g/\ell)\sin\theta$.

**System B — a cart-pole** (for the torque limit and locality): $m_c = 1$, $m_p = 0.1$,
$\ell = 0.5$, $g = 9.81$. With $\theta$ measured from the **upward vertical** and
$x = (q, \theta, \dot q, \dot\theta)$,

$$
\begin{bmatrix} m_c + m_p & m_p\ell\cos\theta \\ \cos\theta & \ell \end{bmatrix}
  \begin{bmatrix}\ddot q \\ \ddot\theta\end{bmatrix}
  = \begin{bmatrix} u + m_p\ell\dot\theta^2\sin\theta \\ g\sin\theta\end{bmatrix},
$$

integrated by the **midpoint rule (RK2)** with $\Delta t = 0.05$, $N = 100$,
$Q = \mathrm{diag}(0.1, 1, 0.01, 0.01)$, $R = [0.01]$,
$Q_f = \mathrm{diag}(100, 500, 50, 50)$, $x_0 = (0, \pi, 0, 0)$, $x_{\mathrm{goal}} = 0$, torque
limit $\lvert u\rvert \le \bar{u}$.

**Algorithm specification** (the acceptance criteria depend on it, so use it as written):
regularization is the $V_{xx}$ form (14) with $\mu_0 = 10^{-6}$,
$\mu \leftarrow \max(\mu/10, 10^{-9})$ on acceptance, $\mu \leftarrow 10\mu$ on rejection, and an
upper bound of $10^{12}$. The line search tries $\alpha \in \{2^{-j}\}_{j=0}^{13}$ largest first,
and accepts when $J' < J$ **and** $z > 0.1$ in (16) (skipping the $z$ test when
$-\Delta J(\alpha) \le 0$). Convergence is declared when an accepted step's cost reduction falls
below $\varepsilon\max(1, \lvert J\rvert)$. The forward pass is (15), with $\alpha$ on $k$ only.

**Acceptance criteria** — all four must hold to pass.

1. **The two methods reach the same solution (system A).** With $\varepsilon = 10^{-13}$ from a
   zero initial guess,
   $$
   J^*_{\text{iLQR}} = J^*_{\text{DDP}} = 66.156792572835
   $$
   agree to within $10^{-11}$ relative, and the iteration counts are **14** for iLQR and **7** for
   DDP (±1 allowed). In both cases the cost of accepted steps is **monotone decreasing**, with
   $\lVert x_N\rVert_\infty < 10^{-4}$ and $\max_k\lvert u_k\rvert = 26.889 \pm 0.01$.
2. **The convergence order matches the prediction (system A).** Recording
   $\lVert k^{(n)}\rVert_\infty$ at iteration $n$: (a) for iLQR the last five ratios
   $\lVert k^{(n+1)}\rVert/\lVert k^{(n)}\rVert$ are all $0.2592 \pm 0.001$ (first order, (5));
   (b) for DDP the same ratios run $0.40 \to 0.085 \to 0.009 \to 0.0001$, **going to zero**, while
   $\lVert k^{(n+1)}\rVert/\lVert k^{(n)}\rVert^2$ stays in $[0.015,\ 0.045]$ over the last four
   (second order); (c) from three different initial guesses (zero, and two drawn from
   $\mathcal{N}(0,1)$ and $\mathcal{N}(0,25)$) iLQR gives the **same ratio** $0.2592$ — confirming
   that the rate is a property of the solution, not of the starting point.
3. **Swing-up within the torque limit (system B).** From a zero initial guess with
   $\varepsilon = 10^{-11}$: (a) at $\bar{u} = 30$, $J^* = 46.8449 \pm 0.01$,
   $\lVert x_N\rVert_\infty < 0.01$ and $1 \pm 1$ saturated stages; (b) at $\bar{u} = 10$,
   $J^* = 307.815 \pm 0.1$, $\lVert x_N\rVert_\infty < 0.05$ and $66 \pm 3$ saturated stages;
   (c) in both cases $\lvert u_k \rvert \le \bar{u} + 10^{-12}$ at **every** $k$ and the cost
   decreases monotonically; (d) tightening $\bar{u}$ multiplies the cost by **more than six** and
   raises the saturated stages from 1 to over 60 (evidence that the constraint changes the shape of
   the trajectory).
4. **Measure locality and DDP's fragility.** (a) On system B with $\bar{u} = 10$, run from five
   different random initial control sequences and obtain **at least two distinct final costs**
   (differing by more than 1%), one of which is **lower** than the zero initial guess's
   $307.815$ (the author's implementation gave $J^* = 199.299$ with 47 saturated stages). (b) On
   system A, running DDP from random initial guesses ($\mathcal{N}(0,1)$, $\mathcal{N}(0,25)$)
   **fails** by hitting the regularization ceiling $10^{12}$, while iLQR from the same guesses
   converges to the solution of condition 1. (c) Report the number of stages at which
   $Q_{uu} \preceq 0$ in the failed DDP runs.

**Baselines**: (i) iLQR and DDP on system A are each other's baseline (they must reach the same
solution). (ii) On system A, compute $\nabla\hat{J}$ directly by finite differences in $u$ and
check it matches the backward pass's $Q_{u,k}$ to within $10^{-6}$ (the numerical check of step 2
of the proof sketch — the fastest way to catch a backward-pass bug). (iii) The $\bar{u} = 30$
result of system B should be nearly the same as the $\bar{u} = \infty$ result
($J^* = 46.8413$, 0 saturated stages), since the constraint is barely active.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The forward pass diverges to `nan` | $Q_{uu}$ is indefinite and regularization is off | print the smallest eigenvalue of $Q_{uu}$ at each stage; if negative, raise $\mu$ by (14) and redo the backward pass |
| The line search fails at every $\alpha$ | you computed (7) with the regularized $\tilde{Q}_{uu}$ | recompute $\Delta_2$ with the $\mu = 0$ $Q_{uu}$; or check whether you used the clamped $k$ |
| The cost falls and then suddenly rises | you dropped the $z$ test and used only "$J' < J$" | log $z$ for accepted steps; a step with $z < 0.1$ means the test is missing |
| Small $\alpha$ makes the trajectory **worse** | you multiplied $K$ by $\alpha$ as well | multiply only $k$, as in (15). Problem P5 is this phenomenon |
| DDP is slower than iLQR | the accepted $\alpha$ keeps coming out below 1 (H3 violated) | print the $\alpha$ history; while $\alpha < 1$ persists, quadratic convergence is not observable |
| The control exceeds the limit by about $10^{-3}$ | you clamped only in the forward pass and did not project in the backward pass | check that $k$ is clamped in the backward pass and that row of $K$ is set to zero |
| The backward pass's $Q_u$ differs from the finite-difference gradient | a transpose on $\ell_{ux}$, or you used $V_x$ before updating it | run baseline (ii) at $N = 2$ first |
| The pendulum's $r$ is not $0.2592$ | you **included** $f_{xx}$ on the iLQR side, or $\Delta t$ / the weights differ | re-check the input constants and confirm $f_{xx}$ was set to zero |

## Open problems

- **(open problem) How to use second-order information safely** — DDP's second-order terms pay off
  in the final stretch and cause divergence early on (acceptance criterion 4b). There is no
  **decision rule** for when to switch them on, so practice simply uses iLQR. Current approaches:
  blending in the second-order terms according to the trust-region radius, and the regularization
  schedule of [Tassa et al. 2012](https://doi.org/10.1109/IROS.2012.6386025). What is missing: a
  cheap condition, evaluable **inside the backward pass**, certifying that "turning on the
  second-order terms now keeps $Q_{uu} \succ 0$".
- **(open problem) Handling state constraints inside the DDP structure** — as R4 showed, state
  constraints cannot enter the $\delta u$ QP and get pushed into the cost. The augmented
  Lagrangian ([ALTRO](https://doi.org/10.1109/IROS40897.2019.8967788)) adds an outer loop that
  weakens the convergence guarantee, and interior-point methods demand a feasible initial
  trajectory. What is missing: a transcription that handles state constraints in a **single loop**
  while keeping both DDP's $O(N)$ complexity and its quadratic convergence. This question is
  compared against the direct-method answer in `c4-direct-collocation-sqp`.
- **(open problem) Globality of non-convex trajectory optimization** — the locality of R5 is a
  measurable fact, but there is no theory of how many local solutions a problem has or which
  initial guess reaches which. Current approaches: statistical analysis of multi-start, convex
  relaxation (shortest paths on a graph), and hybrid schemes that build the initial trajectory with
  a planner from `c6-sampling-based-planning`. What is missing: a certificate at robot scale saying
  "this solution is within x% of the global one" — the same gap as open problem 1 of the previous
  lesson.
- **(open problem) $f_{xx}$ for non-smooth dynamics** — with contact, $f$ is not $C^2$, so the DDP
  terms of (2) are undefined; and in relaxed models $f_{xx}$ grows like the inverse of the
  relaxation parameter and drives $Q_{uu}$ indefinite. Current approaches: smooth relaxations of
  contact with annealing of the parameter, and differentiable contact models. What is missing: a
  principle for choosing the relaxation parameter and the regularization $\mu$ **together** (seen
  again in `c4-contact-implicit-hybrid`).

## Concept check

Run `rc quiz c4-ilqr-ddp`. The quiz is for **concept checking only**; the real work is the problem
set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

The seven items cover: which term of (2) separates iLQR from DDP; the grounds for DDP's quadratic
convergence; why Tassa 2012 regularizes $V'_{xx}$ rather than $Q_{uu}$; whether the line-search
step multiplies the feedback gain as well as the feedforward term; what breaks without the
expected-reduction ratio test; why a state constraint cannot enter the backward pass's QP; and
whether DDP beats iLQR from any initial guess.

## How to study this stage

1. **Build the backward pass on paper (100 min)** — reconstruct (9)→(12) with the text closed. The
   only trap is the one line "the quadratic part of $\delta x'$ meets $V'_x$ but not $V'_{xx}$".
   Writing that line by hand fixes the iLQR/DDP distinction permanently. Read UA ch.10.3 alongside
   as **the same result in different notation**.
2. **Do it by hand at $N = 1$ (30 min)** — solve problem P4 first. Confirming that at one stage the
   two methods give the same control and differ only in $Q_{xx}$ reveals that the difference arises
   when it **propagates to earlier stages**. Do this before writing code and debugging gets easy.
3. **Implement the pendulum first (120 min)** — system A has analytic $f_x$ and $f_{xx}$, which
   isolates implementation errors. Run baseline (ii) (finite-difference gradient against $Q_u$) at
   $N=2$ to validate the backward pass, then run the whole thing. **Skip that check and you will
   have to suspect everything else.**
4. **Extract the convergence order yourself (60 min)** — tabulate the ratios of
   $\lVert k^{(n)}\rVert$. The moment you see iLQR's $0.2592$ **constant to four decimals**
   alongside DDP's ratios going to zero, the proof of R2 sticks. Also confirm that $0.2592$ is the
   same when you change the initial guess — meaning the rate is a **property of the solution**.
5. **Turn regularization off and break it (50 min)** — give the pendulum a random initial control
   sequence and run DDP with $\mu = 0$ fixed. Printing the smallest eigenvalue of $Q_{uu}$ shows
   the stages where it goes negative. Seeing it break first is what makes the form of (14)
   memorable.
6. **On the cart-pole, put the constraint in from the start (120 min)** — solve it unconstrained
   first and clamp later and you will miss that the backward projection and the forward clamping
   must be done **together**. Implement $\bar{u} = 10$ from the beginning and see both that 66 of
   100 stages saturate and that the cost grows sixfold. Log the accepted $\alpha$ — that
   $\alpha = 0.25$ persists for dozens of iterations is the answer to "why a hundred and forty
   iterations rather than twenty".
7. **Measure locality (40 min)** — run from five random initial control sequences and tabulate the
   final costs. Seeing that the zero initial guess is **not the best** is the most practical lesson
   here.
8. **Read the papers in implementation order (180 min)** — Mayne 1966 (the prototype) → Liao &
   Shoemaker 1991 (why second order) → Tassa 2012 (how to make it run) → Tassa 2014 (constraints).
   Read 2012 and 2014 **after** writing the code and every line of §III reads as a bug you have
   already met. Write the one-page note per paper — **without exception**.
9. **End with what cannot be done (30 min)** — pick one of the four open problems and write a
   paragraph. The second (state constraints) gets a different answer from the very next lesson,
   `c4-direct-collocation-sqp`.

**Passing bar**: you can derive (2) and (4) from a blank page, you can explain "DDP = Newton,
iLQR = Gauss-Newton" in terms of the reduced problem $\hat{J}(u)$, you can state the difference
between the two regularizations via the $\mu\to\infty$ limit, you have code satisfying all four
acceptance criteria of the reproduction task, and you have notes on all four papers.
