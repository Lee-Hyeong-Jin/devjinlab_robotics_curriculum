---
id: c4-mpc
lang: en
title: MPC and stability
summary: >-
  In MPC, where a finite-horizon optimization is re-solved every cycle to produce feedback,
  establish with two theorems **why the terminal set and the terminal cost are indispensable** —
  control invariance of the terminal set gives recursive feasibility, and a terminal cost that is
  a control Lyapunov function makes the optimal value function a Lyapunov function. Then count on
  a grid how many states are "feasible now but infeasible later" when the terminal condition is
  dropped (178 out of 507), derive from the KKT conditions that the explicit MPC solution is
  piecewise affine, and see why real-time iteration runs only one SQP step per cycle.
objectives:
  - Reconstruct, as a proof sketch, MPC's recursive feasibility from control invariance of the terminal set.
  - Prove that the optimal value function is a Lyapunov function when the terminal cost is a control Lyapunov function, and state the region of attraction.
  - Construct and count states at which both recursive feasibility and stability fail without a terminal condition.
  - Derive from the KKT conditions that the explicit MPC solution is piecewise affine on a polyhedral partition.
  - Explain the preparation/feedback split of real-time iteration and the condition for its convergence.
tags: [optimal-control, mpc, recursive-feasibility, lyapunov, explicit-mpc, rti, research]
---

# MPC and stability

## Setup and notation

The previous four lessons solved a trajectory optimization **once**. MPC (model predictive
control) re-solves the same problem **every cycle** and uses **only the first control** of the
resulting open-loop trajectory. That re-solving is what creates feedback, and it also creates new
questions — **is there any guarantee that what is solvable now will be solvable next time?** And
**is the feedback built this way stable?** The two theorems of this lesson are the answers. The
recommended prerequisites are the previous four lessons.

What this lesson additionally assumes:

- Control: Lyapunov stability (discrete time), invariant and control invariant sets, regions of
  attraction.
- Optimization: the KKT conditions and active sets of a QP, polyhedra and their partitions.
- Results from earlier lessons: the Riccati solution $P_\infty$ and its Lyapunov identity
  (`c4-dp-lqr-lqg` R4), transcription and sparse QPs (`c4-direct-collocation-sqp` R1), and SQP
  (R3 of that lesson).

Notation (shared across module C4):

| Symbol | Meaning |
|---|---|
| $x^+ = f(x,u)$ | discrete dynamics; $Ax + Bu$ in the linear case |
| $\mathbb{X}$, $\mathbb{U}$ | state and control constraint sets, assumed to contain the origin in their interior |
| $N$ | the **prediction horizon**; the same $N$ is used every cycle |
| $\ell(x,u) \ge 0$ | stage cost, with $\ell(0,0) = 0$ and positive away from the origin |
| $V_f(x)$, $\mathbb{X}_f$ | the **terminal cost** and the **terminal set** |
| $J_N^*(x)$ | the optimal value of the $N$-horizon problem solved at state $x$ |
| $\mathbb{X}_N$ | the set of initial states for which the $N$-horizon problem is **feasible** |
| $\kappa_f(x)$ | the **local control law** on $\mathbb{X}_f$ (usually the LQR gain) |
| $\mu_N(x)$ | the control MPC actually applies, $= u_0^*(x)$ |
| $P_\infty$, $K_\infty$ | the Riccati solution and gain of infinite-horizon LQR |

**A note on the word**: the horizon is a **prediction** horizon and it never closes — every cycle
predicts $N$ fresh steps (a receding horizon). So MPC's stability claim is not "the finite-horizon
optimum is stable" but "**the concatenation of the first pieces of finite-horizon solutions** is
stable", and those are different statements.

The problem solved each cycle:

$$
\begin{aligned}
J_N^*(x) = \min_{u_{0:N-1}} \;& \sum_{k=0}^{N-1}\ell(x_k, u_k) + V_f(x_N) \\
  \text{s.t.}\;& x_0 = x, \quad x_{k+1} = f(x_k, u_k), \\
  & x_k \in \mathbb{X},\; u_k \in \mathbb{U}, \quad x_N \in \mathbb{X}_f,
\end{aligned} \tag{1}
$$

and the closed loop is $x^+ = f\big(x, \mu_N(x)\big)$ with $\mu_N(x) = u_0^*(x)$.

## Key results

The bracket gives the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (recursive feasibility) [D3]** — if $\mathbb{X}_f$ is **control invariant** under $\kappa_f$
  ($x \in \mathbb{X}_f \Rightarrow \kappa_f(x) \in \mathbb{U}$ and
  $f(x,\kappa_f(x)) \in \mathbb{X}_f$) and $\mathbb{X}_f \subseteq \mathbb{X}$, then
  $$x \in \mathbb{X}_N \;\Longrightarrow\; f\big(x, \mu_N(x)\big) \in \mathbb{X}_N. \tag{2}$$
  That is, **feasible once means feasible forever**. The proof is a one-line construction — "shift
  the previous solution by one and append $\kappa_f$ to the tail" — and the only reason that
  construction is possible is control invariance of $\mathbb{X}_f$.
- **R2 (Lyapunov stability) [D3]** — if in addition $V_f$ is a **control Lyapunov function** on
  $\mathbb{X}_f$, i.e.
  $$V_f\big(f(x,\kappa_f(x))\big) - V_f(x) \le -\ell\big(x, \kappa_f(x)\big)
    \qquad \forall x \in \mathbb{X}_f, \tag{3}$$
  then the optimal value function decreases along the closed loop by at least the stage cost:
  $$J_N^*\big(f(x,\mu_N(x))\big) - J_N^*(x) \le -\ell\big(x, \mu_N(x)\big). \tag{4}$$
  So $J_N^*$ is a Lyapunov function on $\mathbb{X}_N$, the origin is **asymptotically stable**, and
  the region of attraction contains $\mathbb{X}_N$.
- **R3 (the linear-quadratic MPC solution is piecewise affine) [D2]** — with linear $f$, quadratic
  $\ell$ and $V_f$, and polyhedral constraints, (1) is a QP parameterised by $x$ and its optimal
  solution is a **piecewise affine function on a polyhedral partition**,
  $$\mu_N(x) = F_i\,x + g_i \quad (x \in \mathcal{R}_i), \qquad
    \mathbb{X}_N = \bigcup_i \mathcal{R}_i. \tag{5}$$
  Each $\mathcal{R}_i$ corresponds to one active set, and the number of regions grows
  combinatorially in the number of constraints. This is **explicit MPC**, and the price of turning
  an online QP into a table lookup is exactly that combinatorial explosion.
- **R4 (without a terminal condition, both fail) [D2]** — dropping $\mathbb{X}_f$ makes (2) false,
  and dropping $V_f$ makes (4) false. These are **different** failures. (a) On the
  two-dimensional unstable system of the reproduction task at $N=3$, **178 of the 507** grid points
  at which the QP is feasible become infeasible a few steps later (for example $x_0 = (-10, 4)$ at
  step 5). The remaining 329 are the actual region of attraction, and that number is **exactly**
  the size of the feasible set once it converges at $N \ge 8$. (b) On the same system with no
  terminal cost and $N = 1$, the closed-loop spectral radius is $\rho(A) = 1.2$, **the same as
  open loop** — MPC does nothing. With the terminal cost $P_\infty$, even $N=1$ gives
  $\rho = 0.4482078910$, **exactly infinite-horizon LQR**.
- **R5 (real-time iteration, RTI) [D1]** — nonlinear MPC has no time to solve an NLP **to
  convergence** every cycle. RTI runs **one SQP step** per cycle and splits that step into a
  **preparation phase** that can run before the measurement arrives (evaluating Jacobians and
  Hessians and factorising) and a **feedback phase** after it (one QP). Convergence is guaranteed
  under a condition that each cycle's single step is a **contraction**, which holds when the
  sampling period is short enough that the true solution moves only a little between cycles.
  **[D1]**

## Derivation

### R4 — what breaks without a terminal condition (look first)

Before setting up the theorems, see **why they are needed**, numerically. Use the system of the
reproduction task:

$$
A = \begin{bmatrix} 1.2 & 1 \\ 0 & 1.2\end{bmatrix}, \quad
B = \begin{bmatrix} 0 \\ 1\end{bmatrix}, \quad
Q = I, \; R = 1, \quad \lvert u \rvert \le 1, \; \lVert x \rVert_\infty \le 10. \tag{6}
$$

Since $\rho(A) = 1.2$, the open loop is unstable.

**What breaks, part one: stability.** Solving (1) with no terminal cost ($V_f = 0$) and no
constraints gives the finite-horizon LQR of `c4-dp-lqr-lqg`, and the spectral radius of the closed
loop built from its first gain $K_0$ is

| $N$ | $V_f = 0$ | $V_f = \tfrac12x^\top Qx$ | $V_f = \tfrac12x^\top P_\infty x$ |
|---|---|---|---|
| 1 | $1.2000000000$ | $0.6221710168$ | $0.4482078910$ |
| 2 | $0.6221710168$ | $0.4948716593$ | $0.4482078910$ |
| 3 | $0.4948716593$ | $0.4572180009$ | $0.4482078910$ |
| 5 | $0.4497440558$ | $0.4484804500$ | $0.4482078910$ |
| 10 | $0.4482085743$ | $0.4482080211$ | $0.4482078910$ |

There are three things to read here. (a) At $V_f = 0$, $N = 1$ we get $\rho = 1.2 = \rho(A)$ —
**the same as open loop**. The reason is structural: since the first row of $B$ is zero, $u_0$
moves only the **second** component of $x_1$, while the cost of the $N=1$, $V_f=0$ problem,
$\ell(x_0,u_0)$, does not look at $x_1$ at all. So the optimum is $u_0 = 0$ and MPC does nothing.
(b) The $N$-th entry of the first column equals the $(N-1)$-th of the second — because
$V_f = \tfrac12x^\top Qx$ is the same as appending one more stage. (c) The third column is
$0.4482078910$ **independently of $N$**. Because $V_f = \tfrac12x^\top P_\infty x$ satisfies (3)
**with equality** (by the Lyapunov identity of `c4-dp-lqr-lqg` R4), the finite-horizon Riccati
recursion sits at the fixed point $P_\infty$ and MPC *is* infinite-horizon LQR.

**What breaks, part two: recursive feasibility.** Now switch the constraints on, with $N = 3$ and
no terminal condition. Sweeping $[-10,10]^2$ on a $41\times41$ grid:

- grid points at which the QP is **feasible** at $t = 0$: **507** ($30.16\%$)
- points from which the closed loop stays feasible throughout and converges to the origin:
  **329** ($19.57\%$)
- the difference of **178** points are states that are "solvable now, unsolvable later".

A concrete witness: $x_0 = (-10,\,4)$ is feasible at $t=0$ but the QP becomes infeasible **at step
5**. The trajectory is

$$
(-10,\,4) \to (-8,\,3.8) \to (-5.8,\,3.56) \to (-3.4,\,3.272)
  \to (-0.808,\,2.926) \to (1.957,\,2.512)
$$

— the velocity component never falls below about $2.5$ while the position is pushed toward $+10$,
and with $\lvert u\rvert\le1$ there is no longer any way to stay inside the box. **MPC was looking
only three steps ahead, and took no responsibility for the world beyond them.**

And the decisive number: those **329** survivors are **exactly** the value to which the feasible
set $\lvert\mathbb{X}_N\rvert$ of the same system converges as $N$ grows:

| $N$ | constraints only (no terminal condition) | $+$ terminal equality $x_N = 0$ |
|---|---|---|
| 3 | $507$ ($30.16\%$) | $23$ ($1.37\%$) |
| 5 | $361$ ($21.48\%$) | $91$ ($5.41\%$) |
| 8 | $329$ ($19.57\%$) | $231$ ($13.74\%$) |
| 12 | $329$ ($19.57\%$) | $313$ ($18.62\%$) |

The left column **shrinks** with $N$ and converges to 329 (the set of states that can be kept
inside the box forever — the viability set). The right column **grows** toward the same value (the
set of states that can be driven to the origin within $N$ steps). Where the two columns meet is
this problem's true region of attraction.

**This table explains R1 and R2.** Adding the terminal equality at $N=3$ shrinks the feasible set
to $1.37\%$, but **within it recursive feasibility is guaranteed** ($x_N = 0$ is a terminal set
that is control invariant under $\kappa_f = 0$). Dropping the terminal condition widens the set to
$30.16\%$, but $35\%$ of that is a false promise. **A terminal condition is not a device for
enlarging the region; it is a device for making the region honest.**

**Where the assumptions break**: the numbers above depend on the grid resolution ($41\times41$).
Measuring the **true** volume of these sets needs polyhedral computation. Also, adding only a
terminal **cost** does **not** restore (2) — in the author's implementation, adding
$V_f = \tfrac12x^\top P_\infty x$ alone at $N=3$ gave a region of attraction of $269$ points
($16.00\%$), which is actually **smaller**. The terminal cost is what the stability argument ((4))
needs; the feasibility argument ((2)) needs the terminal **set**. Confusing the two is the
commonest misunderstanding in this subject.

### R3 — explicit MPC is piecewise affine

With linear dynamics, quadratic cost and polyhedral constraints, (1) is a QP parameterised by $x$.
Condensing the decision variables to $U = (u_0,\dots,u_{N-1})$ puts it in the form

$$
\min_U \; \tfrac12 U^\top H U + x^\top F^\top U + \text{const}
  \quad \text{s.t.}\quad G U \le w + E x \tag{7}
$$

with $H \succ 0$ (and $G, w, E$ condensing the state and control constraints). This is a
**multiparametric QP**.

**Fix the active set and it is affine.** Let $\mathcal{A}$ be the set of rows active at the optimum
and write its submatrices as $G_\mathcal{A}, w_\mathcal{A}, E_\mathcal{A}$. The KKT conditions are

$$
H U + F x + G_\mathcal{A}^\top \lambda_\mathcal{A} = 0, \qquad
  G_\mathcal{A} U = w_\mathcal{A} + E_\mathcal{A} x \tag{8}
$$

(inactive multipliers being zero). Substituting
$U = -H^{-1}(Fx + G_\mathcal{A}^\top\lambda_\mathcal{A})$ from the first into the second gives

$$
-G_\mathcal{A}H^{-1}G_\mathcal{A}^\top \lambda_\mathcal{A}
  = w_\mathcal{A} + \big(E_\mathcal{A} + G_\mathcal{A}H^{-1}F\big)x,
$$

so $\lambda_\mathcal{A}$ is an **affine function** of $x$, and therefore so is $U$:

$$
U^*(x) = \underbrace{-H^{-1}\big(F - G_\mathcal{A}^\top M_\mathcal{A}(E_\mathcal{A} + G_\mathcal{A}H^{-1}F)\big)}_{=:\,\tilde{F}_\mathcal{A}}x
  + \tilde{g}_\mathcal{A}, \qquad
  M_\mathcal{A} := -\big(G_\mathcal{A}H^{-1}G_\mathcal{A}^\top\big)^{-1}. \tag{9}
$$

($G_\mathcal{A}$ must have full row rank for the inverse to exist — that is LICQ, the same
assumption as H2 of `c4-direct-collocation-sqp` R3.)

**The regions are polyhedra.** The set of $x$ for which the same active set is optimal is given by
two families of **linear** inequalities: (a) the inactive constraints actually hold
($G_i U^*(x) \le w_i + E_i x$ for $i \notin \mathcal{A}$), and (b) the active multipliers are
nonnegative ($\lambda_\mathcal{A}(x) \ge 0$). Both are affine in $x$, so that set
$\mathcal{R}_\mathcal{A}$ is a **polyhedron**. Since $\mu_N(x)$ is the first block of $U^*(x)$,
(5) follows.

**Combinatorial explosion.** There is one region per active set, so the upper bound is $2^q$ for
$q$ constraints. In practice it is far fewer, but still exponential in $N$ and the number of
constraints — which is why explicit MPC is used only on problems with a small state dimension
(typically $n \le 5$) and a short horizon. At robot scale, solving the QP online is cheaper.

**Where the assumptions break**: (9) used $H \succ 0$ and LICQ. If $H$ is singular (cheap control,
$R = 0$), the solution is not unique and the piecewise affine selection becomes arbitrary. If LICQ
fails (redundant or degenerate constraints), several active sets correspond to the same $x$, the
partition overlaps, and the explicit solution can be discontinuous on those boundaries. And if the
dynamics are **nonlinear**, (7) is not a QP and this whole derivation is void — the solution of
nonlinear MPC is not piecewise affine, which is why it **has to be solved online**, as in R5.

### R5 — real-time iteration (RTI)

For nonlinear MPC, (1) is an NLP. Solving it with the SQP of
`c4-direct-collocation-sqp` costs one Jacobian and Hessian evaluation plus one QP per iteration.
If the control period is $1\,\mathrm{ms}$ and convergence needs 20 iterations, it is unusable.

**RTI's idea** (Diehl et al. 2009): run **one SQP step** per cycle. Since the solution used is not
converged, each cycle's control is not optimal, but because the true solution moves only a little
per cycle, **spreading the iterations over time** tracks it. The justification is that "one step
per cycle" is a **contraction** — if the Newton contraction factor of one step times the motion of
the true solution is below one, the tracking error stays bounded.

**The preparation/feedback split.** One SQP step per cycle is cut in two.

- **Preparation phase** — everything that can be done **without** the measurement
  $x_{\text{meas}}$: evaluate $f_x$, $f_u$ and the Hessian along the previous trajectory, build the
  QP matrices, and factorise them. This is the bulk of the computation.
- **Feedback phase** — once the measurement arrives, update **only the right-hand side** of the QP
  (the initial-state constraint $x_0 = x_{\text{meas}}$) and solve the already factorised system
  for $u_0$.

So the **measurement-to-control latency** is not the total computation time but the feedback
phase's time — typically more than an order of magnitude shorter. That is why RTI became the
standard for real-time NMPC.

**Where the assumptions break**: the contraction condition holds when the sampling period is short
enough that the true solution moves only a little. Under large disturbances or an abruptly changing
reference, one step cannot keep up and the tracking error accumulates — then several SQP steps (or
a shorter period) are needed. Also, RTI uses an **unconverged** solution, so the guarantees of R1
and R2 do not apply as stated; there is not even a guarantee that the terminal set is satisfied.
Practice fills the gap with (i) conservative constraint backoff, (ii) softened constraints with
slack penalties, and (iii) a backup trajectory for the worst case. **RTI's stability guarantee is
weaker than the two theorems of this lesson** — this is open problem 1.

## Proof sketch

### R1 — recursive feasibility [D3]

**Hypotheses**
H1: $\mathbb{X}_f \subseteq \mathbb{X}$ and $0 \in \mathbb{X}_f$.
H2 (control invariance): for every $x \in \mathbb{X}_f$, $\kappa_f(x) \in \mathbb{U}$ and
$f(x, \kappa_f(x)) \in \mathbb{X}_f$.
H3: the minimum in (1) is attained and $\mu_N(x) = u_0^*(x)$ is well defined.

**Conclusion** C: $x \in \mathbb{X}_N \Rightarrow x^+ := f(x,\mu_N(x)) \in \mathbb{X}_N$.

**Strategy**: **construct by hand one feasible candidate** at $x^+$. It need not be optimal; being
feasible is enough to put $x^+ \in \mathbb{X}_N$.

1. **Take the previous solution.** Let the optimum at $x$ be
   $u^* = (u_0^*, u_1^*, \dots, u_{N-1}^*)$ with trajectory
   $x^* = (x_0^*=x, x_1^*, \dots, x_N^*)$. By definition $x_k^* \in \mathbb{X}$,
   $u_k^* \in \mathbb{U}$ and $x_N^* \in \mathbb{X}_f$.
2. **Shift by one.** Since $x^+ = x_1^*$ (MPC applied $u_0^*$), take as candidate at $x^+$
   $$\tilde{u} := \big(u_1^*, u_2^*, \dots, u_{N-1}^*,\; \kappa_f(x_N^*)\big). \tag{10}$$
   The first $N-1$ entries reuse the previous solution and **only the last one is new**.
3. **The first $N-1$ pieces are already feasible.** The first $N-1$ states of the trajectory
   generated by $\tilde{u}$ are **the same** as $x_1^*, \dots, x_N^*$ (same controls, same
   dynamics), so they satisfy the state and control constraints as before.
4. **The tail closes by H2.** The last state is
   $x_{N+1}^* := f(x_N^*, \kappa_f(x_N^*))$, and since $x_N^* \in \mathbb{X}_f$, H2 gives
   $\kappa_f(x_N^*) \in \mathbb{U}$ and $x_{N+1}^* \in \mathbb{X}_f$; H1's
   $\mathbb{X}_f \subseteq \mathbb{X}$ gives the state constraint as well.
5. So $\tilde{u}$ is a **feasible solution** of (1) at $x^+$, hence
   $x^+ \in \mathbb{X}_N$. **C**.

**Deleting a hypothesis: where does it collapse?**

- **Delete H2 (control invariance)**: step 4 is impossible. Either there is no control to append, or
  appending one leaves $\mathbb{X}_f$. Then $\tilde{u}$ is not feasible and **(2) can be false** —
  the 178 states of R4's derivation are exactly that case (no $\mathbb{X}_f$ at all).
- **Delete H1 ($\mathbb{X}_f \subseteq \mathbb{X}$)**: step 4 cannot guarantee the state
  constraint. Taking $\mathbb{X}_f$ loosely as "a neighbourhood of the origin" without checking the
  state constraints is a common mistake.
- **If $\mathbb{X}_f$ is merely invariant rather than control invariant**: guaranteeing only
  $f(x, 0) \in \mathbb{X}_f$ without a $\kappa_f$ is not enough — there must exist **some** control
  in $\mathbb{U}$ keeping the state in $\mathbb{X}_f$, and that control must be used
  **explicitly** in step 2.
- **Note — this theorem gives no stability**: step 5 claimed only feasibility. It made no claim
  about cost, so there is no guarantee the trajectory goes to the origin. That is R2.

### R2 — the optimal value function is a Lyapunov function [D3]

**Hypotheses** H1–H3 (as in R1), plus
H4 (terminal cost is a CLF): (3) holds for every $x \in \mathbb{X}_f$.
H5: there is a positive definite $\alpha$ with $\ell(x,u) \ge \alpha(\lVert x\rVert)$ and
$\ell(0,0)=0$, $V_f(0) = 0$, $V_f \ge 0$.

**Conclusions** C1: (4) holds. C2: the origin is an asymptotically stable equilibrium with region
of attraction $\mathbb{X}_N$.

**Strategy**: **compute the cost** of R1's candidate $\tilde{u}$. The optimum is no larger, so an
inequality follows — and that inequality is exactly (4). In other words, **use R1's construction
once more, on the cost side**.

1. **Write the candidate's cost.** Since the trajectory of (10) coincides with the previous one by
   step 3, the cost of $\tilde{u}$ at $x^+$ is
   $$
   J_N(x^+, \tilde{u}) = \underbrace{\sum_{k=1}^{N-1}\ell(x_k^*, u_k^*)}_{\text{the reused piece}}
     + \underbrace{\ell\big(x_N^*, \kappa_f(x_N^*)\big)}_{\text{the new tail}}
     + V_f\big(f(x_N^*, \kappa_f(x_N^*))\big).
   $$
2. **Compare with the previous optimum.** Since
   $J_N^*(x) = \sum_{k=0}^{N-1}\ell(x_k^*,u_k^*) + V_f(x_N^*)$, subtracting gives
   $$
   J_N(x^+,\tilde{u}) - J_N^*(x) = -\ell(x, u_0^*)
     + \Big[\ell\big(x_N^*,\kappa_f(x_N^*)\big) + V_f\big(f(x_N^*,\kappa_f(x_N^*))\big) - V_f(x_N^*)\Big].
   $$
3. **H4 kills the bracket.** Applying (3) at $x = x_N^* \in \mathbb{X}_f$ makes the bracket
   $\le 0$, so
   $$J_N(x^+, \tilde{u}) \le J_N^*(x) - \ell(x, u_0^*).$$
4. **The optimum is below the candidate.** Since $J_N^*(x^+) \le J_N(x^+,\tilde{u})$,
   $$J_N^*(x^+) \le J_N^*(x) - \ell\big(x, \mu_N(x)\big),$$
   which is **C1** = (4).
5. **The Lyapunov argument.** $J_N^* \ge 0$, $J_N^*(0) = 0$, and by (4) $J_N^*$ is
   non-increasing along the closed loop. Since
   $\sum_t \ell(x_t, u_t) \le J_N^*(x_0) < \infty$, we get $\ell(x_t,u_t) \to 0$ and by H5
   $x_t \to 0$. If $J_N^*$ is sandwiched by class-$\mathcal{K}$ functions near the origin,
   asymptotic stability follows. The region of attraction is the set on which $J_N^*$ is defined,
   i.e. $\mathbb{X}_N$ (R1 guaranteed we never leave it). **C2**.

(Omitted: continuity of $J_N^*$ and existence of the class-$\mathcal{K}$ upper bound — for
polyhedral constraints and a quadratic cost, $J_N^*$ is piecewise quadratic and continuous, so both
hold. For the general case see
[Mayne et al. 2000](https://doi.org/10.1016/S0005-1098(99)00214-9) §3 and Rawlings et al. 2017
ch.2. The measurable selection when the minimiser is not unique is also omitted.)

**Deleting a hypothesis: where does it collapse?**

- **Delete H4 (CLF)**: the bracket of step 3 can be positive and (4) becomes false. Then $J_N^*$ can
  **increase** along the closed loop and there is no Lyapunov argument. With a long horizon it is
  empirically stable (the table in R4's derivation, $N \ge 2$), but the point is that there is **no
  guarantee**.
- **When H4 can be made an equality**: on a linear-quadratic problem, taking
  $V_f = \tfrac12x^\top P_\infty x$ and $\kappa_f = -K_\infty x$ makes (3) hold **with equality** —
  it is precisely the Lyapunov identity
  $P_\infty - A_c^\top P_\infty A_c = Q + K_\infty^\top R K_\infty$ from step 4 of
  `c4-dp-lqr-lqg` R4. The author's implementation confirmed
  $\lvert V_f(x^+) - V_f(x) + \ell(x,-K_\infty x)\rvert < 6.4\times10^{-14}$ over 1000 random
  states. And $\mathbb{X}_f$ can be taken as $\{x : x^\top P_\infty x \le \gamma\}$, where the
  largest $\gamma$ guaranteeing $\lvert K_\infty x\rvert \le 1$ is
  $$\gamma = \frac{1}{K_\infty P_\infty^{-1}K_\infty^\top} = 2.1809033495392$$
  (condition 2 of the reproduction task), on which $\max\lvert x_1\rvert = 0.9810784190$ and
  $\max\lvert x_2\rvert = 0.8622875072$, so $\mathbb{X}_f \subseteq \mathbb{X}$ (H1) holds too.
  **In other words, for linear-quadratic MPC every hypothesis of R1 and R2 can be verified by
  computation.**
- **Delete H5 (positive definiteness of $\ell$)**: in step 5, $\ell \to 0$ no longer gives
  $x \to 0$. If $Q$ is singular so that some state direction is invisible to the cost, the state can
  diverge along it — **the same failure** as the detectability counterexample of
  `c4-dp-lqr-lqg` R4.
- **Over-trusting "region of attraction $=\mathbb{X}_N$"**: that equality holds only when R1 does.
  Without a terminal set, convergence happens from only part of $\mathbb{X}_N$ (R4's derivation:
  329 of 507), and $\mathbb{X}_N$ is merely an **upper bound** on the region of attraction.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R3)** Write the condensed form (7) by hand at $N = 2$ for the system (6)
(giving $H$, $F$, $G$, $w$, $E$ numerically). Then confirm that with an empty active set, (9)
reduces to the finite-horizon LQR gain.
*Solution sketch*: stack $x_k = A^kx + \sum_{j<k}A^{k-1-j}Bu_j$ and collect the sum of $\ell$ into a
quadratic form in $U$. With an empty active set the second line of (8) disappears, so
$U^* = -H^{-1}Fx$ and its first block must equal the $K_0$ of `c4-dp-lqr-lqg` (5) — the two
computations are the same QP eliminated differently (`c4-direct-collocation-sqp` R1).

**P2 (proof, ★★★, R1)** Extend R1 to a **time-varying terminal set**: replace $\mathbb{X}_f$ by a
sequence $\{\mathbb{X}_f^{(t)}\}$, assume
$f(x,\kappa_f^{(t)}(x)) \in \mathbb{X}_f^{(t+1)}$, and state and prove the conclusion corresponding
to (2). Then explain how recursive feasibility changes for a **shrinking-horizon** MPC
($N_t = N - t$).
*Solution sketch*: the strategy is step 5 of R1 verbatim, with the appended control replaced by
$\kappa_f^{(t)}$. The key is that the candidate must be feasible for **the next time step's**
problem, which is what the forward condition on the set sequence provides. With a shrinking horizon
no tail need be appended (the last problem has $N=0$), so recursive feasibility holds without a
terminal set — but the control law becomes **time-varying** and the notion of infinite-time
stability disappears.

**P3 (proof, ★★, R2)** From (4), show that the closed-loop cost sums to
$\sum_{t=0}^{\infty}\ell(x_t,u_t) \le J_N^*(x_0)$. Then explain why this inequality does **not**
mean "MPC's closed-loop performance is no worse than the infinite-horizon optimum".
*Solution sketch*: sum (4) from $t = 0$ to $T-1$, telescope, and use $J_N^* \ge 0$. Why it does not
follow: $J_N^*(x_0)$ is a **finite**-horizon optimum plus a terminal cost, which differs from the
infinite-horizon optimum $J_\infty^*(x_0)$. The relation between them depends on the choice of
$V_f$; with $V_f = J_\infty^*$ it becomes an equality and MPC is infinite-horizon optimal (the
third column of R4's derivation).

**P4 (numerical, ★, R2)** For the system (6), compute $P_\infty$, $K_\infty$, the closed-loop
eigenvalues, and the terminal-set level
$\gamma = 1/(K_\infty P_\infty^{-1}K_\infty^\top)$. Compute $\max\lvert x_i\rvert$ on that set to
confirm $\mathbb{X}_f \subseteq \mathbb{X}$.
*Answer*:
$$
P_\infty = \begin{bmatrix} 4.7648309659 & 3.9260682124 \\
  3.9260682124 & 6.1680907586\end{bmatrix}, \quad
K_\infty = \begin{bmatrix} 0.6572575618 & 1.5803060402\end{bmatrix},
$$
closed-loop eigenvalues $0.4098469799 \pm 0.1814270284\,i$ with $\rho = 0.4482078910$,
$\gamma = 2.1809033495$, and $\max\lvert x_1\rvert = 0.9810784190$,
$\max\lvert x_2\rvert = 0.8622875072$ (all to within $10^{-9}$). Both are below $10$, so H1 holds.
*Check*: $\max\lvert K_\infty x\rvert$ on that set must be exactly $1$ (that is how $\gamma$ was
chosen). Also substitute $P_\infty$ into the DARE and confirm a residual $< 10^{-10}$.

**P5 (numerical, ★★, R4)** For the system (6), compute the closed-loop spectral radius of
unconstrained MPC with $V_f = 0$ for $N = 1,\dots,10$ and reproduce the first column of R4's table.
Then explain the **structural reason** that $\rho = \rho(A)$ at $N=1$, in terms of the shape of
$B$.
*Answer*: $N=1$: $1.2000000000$; $N=2$: $0.6221710168$; $N=3$: $0.4948716593$;
$N=5$: $0.4497440558$; $N=10$: $0.4482085743$ (tolerance $10^{-9}$). The reason: with
$B = (0,1)^\top$, $u_0$ changes only the second component of $x_1$, while the $N=1$, $V_f=0$ cost
$\ell(x_0,u_0) = \tfrac12(x_0^\top Qx_0 + Ru_0^2)$ does not contain $x_1$. So $u_0^* = 0$ and the
closed loop is the open loop. *Check*: confirm that the $N$-th value of the first column equals the
$(N-1)$-th of the $V_f = \tfrac12x^\top Qx$ column (a terminal cost of $Q$ is the same as appending
one stage).

**P6 (implementation, ★★, R4)** For the system (6) on a $41\times41$ grid, compute (a) the size of
the feasible set at $N=3$ and (b) the size of the closed-loop region of attraction, then
(c) pick a state in the difference and report after how many steps it becomes infeasible.
*Rubric*: passes on reproducing (a) $507$, (b) $329$ and (c) a difference of $178$ (compare by
proportion if your grid differs). You must print the witness's trajectory and state **which
constraint breaks first** (the state box or the control limit). $x_0 = (-10,4)$ breaks at step 5.
(d) Also confirm that adding the terminal equality $x_N = 0$ shrinks the feasible set to $23$ but
makes it **equal** to the region of attraction.

**P7 (counterexample, ★★, R1 and R2)** Show that "with a long enough horizon you do not need a
terminal condition" is only **partly** right: (a) show numerically that growing $N$ on the system
(6) enlarges the region of attraction enough to be practical without a terminal condition;
(b) write why recursive feasibility is nevertheless not guaranteed by any theorem **for any $N$**;
(c) state the price of a long horizon (computation, accumulation of model error).
*Property checklist*: for (a), use the left column of R4's derivation converging to $329$ — note
that it **shrinks** to its limit rather than growing (you must distinguish the feasible set from
the region of attraction). For (b), the point is that step 4 of R1 cannot be performed for any $N$
without an $\mathbb{X}_f$. For (c), the QP size is linear in $N$ and model error dominates as the
prediction lengthens.

**P8 (paper, ★★, R1, R2 and R5)** Read Mayne et al. 2000 §3–§4 and Diehl et al. 2009 §4–§5, then:
(a) confirm whether the roles the authors assign to the "terminal cost" and the "terminal
constraint" match this lesson's R1/R2 split; (b) pick one of their terminal-set constructions,
apply it to the system (6), and compare with $\gamma$; (c) identify where Diehl et al.'s RTI
**loses** the guarantees of R1 and R2.
*Rubric*: (a) passes on identifying the split "terminal constraint → feasibility, terminal cost →
stability". Writing "both are for stability" fails. (b) passes on naming either the maximal
LQR-invariant polyhedron or an ellipsoid and saying, with reasons, whether it is larger or smaller
than this lesson's ellipsoid ($\gamma = 2.1809$). (c) passes on noting that an unconverged solution
gives no guarantee that the terminal set is met.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read with three passes, attacking questions 4, 5, 6 and 7 on the third.

1. **Mayne, Rawlings, Rao & Scokaert, "Constrained model predictive control: stability and
   optimality" (2000, Automatica)** — role: `seminal`. What to read: §3 (stability), §4 (terminal
   conditions). This is the primary source for R1 and R2 of this lesson, the paper that gathered
   conditions scattered until 2000 into one framework.
   Extra questions: (a) of the four kinds of terminal condition the authors classify (terminal
   equality, terminal set, terminal cost, unconstrained with a long horizon), which is this
   lesson's R1/R2 combination? (b) Where do the authors distinguish "optimality" from "stability" —
   do they give a case where MPC is stable but not infinite-horizon optimal? (c) What does this
   paper **not** cover (computation for nonlinear systems, disturbances, model error)?
2. **Rawlings, Mayne & Diehl, "Model Predictive Control: Theory, Computation, and Design"
   (2017, Nob Hill)** — role: `standard`. What to read: all of ch.2 (stability theory). It is the
   textbook version of the paper above, with complete proofs; the steps omitted in R2 are here.
   Extra questions: (a) how do the authors construct the class-$\mathcal{K}$ upper and lower bounds
   on $J_N^*$? (b) Why is a "weak controllability" assumption needed? (c) Which of the textbook's
   assumptions is not among this lesson's H1–H5, and what does it rule out?
3. **Diehl, Ferreau & Haverbeke, "Efficient numerical methods for nonlinear MPC and moving horizon
   estimation" (2009, LNCIS)** — role: `standard`. What to read: §4 (RTI), §5
   (structure-exploiting QP solvers). This is the primary source for R5.
   Extra questions: (a) do the authors report the ratio of computation between the preparation and
   feedback phases? By what factor? (b) In what form do they state RTI's contraction condition — as
   a condition on the sampling period or on how far the solution moves? (c) What do they gain in
   exchange for losing the guarantees of R1 and R2, and do they state that trade-off explicitly?

**The ten fixed questions**: (1) What problem is solved, under what assumptions? (2) What exactly
could prior work not do? (3) Reduce the core idea to one equation. (4) What are the theoretical
guarantees, and **what is not guaranteed**? (5) What are the independent and dependent variables
and the baselines, and were the baselines tuned fairly? (6) Do the metrics match the claims, and
are variance and seeds reported? (7) What information needed for reproduction is missing? (8) If
the result were wrong, which assumption would you doubt first? (9) What are the computational and
memory complexity and the real-time behaviour? (10) What would you change to go beyond this paper
in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one notebook CPU core, under 15 minutes total,
under 500 MB of memory. numpy and scipy only (`scipy.linalg.solve_discrete_are`,
`scipy.optimize.linprog`, `scipy.optimize.minimize`). No simulator.

**Input data**: none; the system is fixed as (6) —
$A = \begin{bmatrix}1.2 & 1\\ 0 & 1.2\end{bmatrix}$,
$B = \begin{bmatrix}0\\1\end{bmatrix}$, $Q = I_2$, $R = [1]$,
$\lvert u\rvert \le 1$, $\lVert x\rVert_\infty \le 10$, cost
$\tfrac12\sum(x_k^\top Qx_k + Ru_k^2) + V_f(x_N)$. The grid is $[-10,10]^2$ at $41\times41$
(1681 points), closed-loop simulations run 60 steps, and convergence is declared at
$\lVert x\rVert_\infty < 10^{-3}$.

**Acceptance criteria** — all four must hold to pass.

1. **Closed-loop poles of unconstrained MPC.** Reproduce the table of R4's derivation. With
   $V_f = 0$, the $\rho(A - BK_0)$ for $N = 1,2,3,5,10$ are
   $1.2000000000$, $0.6221710168$, $0.4948716593$, $0.4497440558$, $0.4482085743$
   (tolerance $10^{-9}$), and with $V_f = \tfrac12x^\top P_\infty x$ it is $0.4482078910$ **for
   every $N$**. Also confirm that the $N$-th value of the first column equals the $(N-1)$-th of the
   $V_f = \tfrac12x^\top Qx$ column.
2. **Terminal set and the CLF identity.** $P_\infty$, $K_\infty$ and $\gamma$ match the values of
   P4 to within $10^{-9}$, and over 1000 random states
   $\max\lvert V_f(x^+) - V_f(x) + \ell(x,-K_\infty x)\rvert < 10^{-12}$ (author's implementation
   $6.4\times10^{-14}$) — confirming that (3) holds **with equality**. Also confirm that on
   $\mathbb{X}_f$, $\max\lvert K_\infty x\rvert = 1$ and $\max\lvert x_i\rvert < 1$.
3. **How the feasible set moves with $N$.** Sweeping the grid with LP feasibility, reproduce
   | $N$ | constraints only | $+\,x_N = 0$ |
   |---|---|---|
   | 3 | $507$ | $23$ |
   | 5 | $361$ | $91$ |
   | 8 | $329$ | $231$ |
   | 12 | $329$ | $313$ |
   (each value $\pm 2$ points). Record in your report that the left column **shrinks** to its limit
   and the right column **grows** toward the same value.
4. **Count the states where recursive feasibility fails.** Running the closed loop at $N = 3$ with
   no terminal condition: (a) show the region of attraction is $329$ points ($19.57\%$) and that its
   difference from the $t=0$ feasible set of $507$ points is **178** (each $\pm 3$ points);
   (b) for at least one of those 178, print the number of steps to infeasibility and the trajectory
   ($x_0 = (-10,4)$ takes **5 steps**; the trajectory is in R4's derivation); (c) confirm that
   $329$ equals the converged value of condition 3 at $N \ge 8$; (d) show that adding only the
   terminal cost $V_f = \tfrac12x^\top P_\infty x$ **shrinks** the region of attraction to
   $269$ points ($16.00\%$), confirming that "a terminal cost does not fix feasibility"
   ($\pm 5$ points).

**Baselines**: (i) for the $V_f = P_\infty$ column of condition 1, the infinite-horizon LQR gain
from `scipy.linalg.solve_discrete_are` is the baseline (the two computations must agree).
(ii) For condition 2, the analytic identity from step 4 of `c4-dp-lqr-lqg` R4 is the baseline.
(iii) For condition 3, the LP (feasibility only) and the QP (optimization) must give the **same**
set — computing it both ways catches implementation errors. (iv) The $329$ of condition 4(a) must
agree with the independent computation of condition 3.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| $\rho \ne 1.2$ at $N=1$, $V_f=0$ | you passed $Q$ as the default terminal cost (a common default) | set $V_f$ to exactly zero and print whether $u_0^* = 0$ |
| $\rho$ varies with $N$ even at $V_f = P_\infty$ | a $\tfrac12$ convention mismatch — $P_\infty$ is off by a factor of two | compare `solve_discrete_are` against the fixed point of your own Riccati recursion |
| The region of attraction comes out equal to the feasible set | you checked only $t=0$ feasibility instead of running the closed loop | confirm you re-solve the QP every step and apply only the first control |
| The region of attraction comes out larger than the feasible set | you did not check the state constraints along the closed-loop trajectory | check $\lVert x\rVert_\infty \le 10$ at every step |
| The feasible set is empty with the terminal equality $x_N=0$ | you imposed the equality on $x_{N-1}$ rather than $x_N$ | shrink to $N=1$ and check by hand |
| LP and QP give different feasible sets | the QP solver reports a convergence failure as infeasibility | take the LP as the reference and count the QP's `status` values separately |
| $\gamma$ is negative or enormous | you did not extract $K_\infty P_\infty^{-1}K_\infty^\top$ as a scalar | print that quantity and confirm it is positive, around $0.4585$ |

## Open problems

- **(open problem) Guarantees for MPC that uses an unconverged solution** — the RTI of R5 runs one
  SQP step per cycle, so it does not satisfy the hypotheses of R1 and R2 (which assume the optimum
  is used). The conditions under which a single step still guarantees stability are known for
  linear systems and small disturbances, but **practical** conditions for nonlinear, constrained
  systems under large disturbances are open. Current approaches: the Lyapunov argument of
  suboptimal MPC, which demands only **descent** rather than optimality, and the contraction
  analysis of [Diehl et al. 2009](https://doi.org/10.1007/978-3-642-01094-1_32). What is missing: a
  condition binding the iteration count, the period and the disturbance magnitude in one
  inequality.
- **(open problem) Computing terminal sets at robot scale** — R1 demands a control invariant
  terminal set, but computing the maximal invariant polyhedron is exponential in the state
  dimension and ellipsoidal approximations are conservative. For $n \gtrsim 20$ (quadrupeds,
  humanoids) with **changing contact modes** there is no practical way to compute a control
  invariant set. Current approaches: finding Lyapunov functions by SOS, and learned invariant sets.
  What is missing: a way to obtain a **certifiable** terminal set at robot scale — which is why
  practical walking MPC runs with no terminal set on a short horizon and its stability is only
  confirmed empirically.
- **(open problem) Recursive feasibility under model error** — step 2 of R1 used "the previous
  solution's trajectory actually happens". If the model is wrong then $x^+ \ne x_1^*$ and the
  candidate $\tilde{u}$ may not be feasible. Robust MPC (tube MPC) solves this under an assumption
  of bounded disturbances (`c4-robust-stochastic-oc` and
  [Mayne et al. 2005](https://doi.org/10.1016/j.automatica.2004.08.019)), but the error of a
  **learned model** depends on the state and is hard to wrap in a bounded set. What is missing: a
  recursive-feasibility guarantee given a bound on the learning error.
- **(open problem) A representation that avoids explicit MPC's combinatorial explosion** — the
  piecewise affine solution of R3 has exponentially many regions, so it is usable only for
  $n \le 5$. Approximating $\mu_N$ with a neural network makes evaluation cheap but loses **any
  guarantee that the approximate policy satisfies the constraints and is stable**. Current
  approaches: equivalent representations exploiting the fact that a ReLU network is exactly
  piecewise affine, and constraint enforcement by projection. What is missing: a way to certify the
  approximation error and the stability margin together (the same gap as `c8-rl-theory`).

## Concept check

Run `rc quiz c4-mpc`. The quiz is for **concept checking only**; the real work is the problem set
and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

The seven items cover: where control invariance of the terminal set is used in the
recursive-feasibility proof; where the terminal cost's CLF condition is used; whether
$V_f = P_\infty$ makes linear-quadratic MPC equal infinite-horizon LQR for any horizon; the
mechanism by which "feasible now, infeasible later" arises; whether adding a terminal cost restores
recursive feasibility; the grounds on which the explicit solution is piecewise affine; and how RTI
reduces the measurement-to-control latency.

## How to study this stage

1. **State the questions that "re-solving" creates (20 min)** — the previous four lessons solved
   once. Re-solving every cycle creates **two new** questions: "will what is solvable now be
   solvable next time" and "is the concatenated control stable". Write those two on paper and check
   that they pair with R1 and R2 respectively — that is the map of this lesson.
2. **See what breaks first (80 min)** — read R4's derivation first and implement conditions 1 and
   4(b) of the reproduction task **first**. Seeing with your own eyes that $u_0^* = 0$ at $N=1$,
   $V_f=0$ and that $x_0=(-10,4)$ goes infeasible at step 5 makes the two theorems' hypotheses
   self-explanatory.
3. **Memorise R1's proof as five lines (40 min)** — "(1) previous solution, (2) shift by one,
   (3) the front is feasible as it was, (4) close the tail with $\kappa_f$, (5) hence feasible".
   Those five lines are the whole of MPC theory; the rest is that construction transplanted to
   other settings (P2).
4. **R2 uses R1's construction once more, on the cost (50 min)** — compute the cost of the same
   candidate $\tilde{u}$, subtract the previous optimum, and see that a bracket is left and that the
   CLF condition is exactly what removes it. Grasping that **the two theorems are two faces of one
   construction** means you need not memorise them separately.
5. **In the linear-quadratic case, compute every hypothesis (60 min)** — obtain $P_\infty$,
   $K_\infty$ and $\gamma = 1/(K_\infty P_\infty^{-1}K_\infty^\top)$, and confirm numerically that
   the CLF condition holds **with equality** (condition 2). Recognising this as the Lyapunov
   identity of `c4-dp-lqr-lqg` binds the two lessons.
6. **Plot the two trends of the feasible set yourself (90 min)** — build the table of condition 3.
   With constraints only the set **shrinks** as $N$ grows; with the terminal equality it **grows**;
   and they meet at the same value. That single picture corrects the common misconception that
   "just lengthen the horizon".
7. **Do explicit MPC by hand at $N=2$ (60 min)** — solve P1 to write the condensed QP numerically
   and confirm that an empty active set gives the LQR gain. Then compute (9) for one active set and
   hold one affine piece in your hands. Counting the regions makes it immediately clear why
   $n \le 5$.
8. **Take RTI from the paper (60 min)** — R5 is D1, so the text gives only the skeleton. Read Diehl
   et al. §4 and write down the computation ratio of the preparation and feedback phases. Then write
   a paragraph on "where do R1 and R2 break if an unconverged solution is used" — that is open
   problem 1.
9. **Read the papers theory → textbook → computation (150 min)** — Mayne et al. 2000 (the
   framework) → Rawlings et al. ch.2 (the complete proofs) → Diehl et al. (the computation). Items
   1 and 2 are the paper and textbook versions of the same content, so read the second **looking for
   the steps the first omitted**. Write the one-page note per paper — **without exception**.
10. **End with what cannot be done (30 min)** — pick one of the four open problems and write a
    paragraph. The second (terminal sets at robot scale) is the answer to why practical walking MPC
    has no terminal set, and the third (model error) is the starting point of the next lesson,
    `c4-robust-stochastic-oc`.

**Passing bar**: you can write R1's five steps and R2's four steps from a blank page, you can
explain the division of labour "terminal set → feasibility, terminal cost → stability", you can
state in numbers you counted yourself the states at which feasibility fails without a terminal
condition, you have code satisfying all four acceptance criteria of the reproduction task, and you
have notes on all three papers.
