---
id: c4-direct-collocation-sqp
lang: en
title: Direct methods, collocation and SQP
summary: >-
  Set up the route that transcribes trajectory optimization into one large sparse nonlinear
  program. Derive the Hermite-Simpson defect directly from "cubic Hermite interpolation plus
  collocation at the midpoint" and confirm numerically that its global order is four. Count the
  nonzeros of the transcribed constraint Jacobian exactly, and show that the Riccati recursion is
  the same banded elimination; then prove that SQP is Newton's method on the KKT system and
  therefore converges quadratically. Finally, measure on the acrobot — across seventeen orders of
  magnitude — that **a zero defect is not an accurate trajectory**.
objectives:
  - Derive the sparsity structure of the transcribed NLP's constraint Jacobian and count its nonzeros exactly.
  - Derive the Hermite-Simpson defect from cubic Hermite interpolation with midpoint collocation, and measure its order numerically.
  - Show that the KKT conditions of the SQP subproblem are the Newton equations of the nonlinear KKT system, and state the conditions for quadratic convergence.
  - Distinguish the defect from the true trajectory error, and explain why mesh refinement uses the interpolant residual.
  - Compare direct methods against indirect methods and iLQR along constraint handling, conditioning and problem size, backed by measurements.
tags: [optimal-control, direct-collocation, hermite-simpson, sqp, nlp, sparsity, research]
---

# Direct methods, collocation and SQP

## Setup and notation

The iLQR/DDP of the previous lesson kept **only the control sequence** as decision variables and
eliminated the states through the dynamics. The price was that there was nowhere to put a state
constraint (R4 of that lesson). This lesson goes the other way — **lift both states and controls
into the decision variables and impose the dynamics as constraints**. Then a state constraint
becomes **just a few more rows**, and the price is the problem size and the need for a sparse NLP
solver. The recommended prerequisites are the previous three lessons and module R0 (numerical
optimization, sparse linear algebra).

What this lesson additionally assumes:

- Numerical optimization: the KKT conditions, LICQ, the second-order sufficient condition (SOSC),
  active sets, trust regions and line search.
- Sparse linear algebra: banded and block tridiagonal structure, nonzero counts and elimination
  ordering (`r0-sparse-linear-algebra`).
- Numerical analysis: the order of a Runge-Kutta method, the error order of an interpolating
  polynomial.

Notation (shared across module C4, continuing from the previous lessons):

| Symbol | Meaning |
|---|---|
| $N$ | number of intervals; the grid is $t_0, \dots, t_N$ and $h = T/N$ |
| $x_k \in \mathbb{R}^n$, $u_k \in \mathbb{R}^m$ | state and control at a grid point; **both are decision variables** |
| $z \in \mathbb{R}^{n_z}$ | the stacked decision vector, $n_z = (N+1)(n+m)$ |
| $f_k$ | $f(x_k, u_k)$; $f_m$ is the value at the midpoint |
| $\zeta_k \in \mathbb{R}^n$ | the **defect** of interval $k$; $\zeta_k = 0$ is the dynamics constraint |
| $x_m$, $u_m$ | state and control at the interval midpoint |
| $c(z) \in \mathbb{R}^{n_c}$ | all equality constraints (defects plus boundary conditions) |
| $\nabla c \in \mathbb{R}^{n_c \times n_z}$ | the constraint Jacobian — the protagonist of this lesson |
| $\mathcal{L}(z, \lambda)$ | the Lagrangian $J(z) + \lambda^\top c(z)$ |
| $W = \nabla^2_{zz}\mathcal{L}$ | the Hessian of the Lagrangian |
| $r(t)$ | the **dynamics residual** of the interpolated trajectory, $\dot{x}_{\text{interp}}(t) - f(x_{\text{interp}}(t), u_{\text{interp}}(t))$ |

**A note on the word**: "collocation" means "force the interpolated trajectory to satisfy the
differential equation **at specified points**". Outside those points it does not hold — and R4 of
this lesson measures how large that gap can be.

The problem (the same problem as (1) of the previous lesson, transcribed):

$$
\min_{z} \; J(z) \quad \text{s.t.}\quad
  \underbrace{\zeta_k(z) = 0,\; k = 0,\dots,N-1}_{\text{dynamics}}, \quad
  \underbrace{x_0 = x_{\mathrm{init}},\; x_N = x_{\mathrm{goal}}}_{\text{boundary}}, \quad
  \lvert u_k \rvert \le \bar{u}. \tag{1}
$$

## Key results

The bracket gives the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (the sparsity of the transcription, and its identity with Riccati) [D2]** — the defect
  $\zeta_k$ depends **only** on $(x_k, x_{k+1}, u_k, u_{k+1})$, so the constraint Jacobian has
  exactly
  $$\operatorname{nnz}(\nabla c) = n\,(2n + 2m)\,N + 2n \tag{2}$$
  nonzeros (the final $2n$ from the boundary conditions), and the fill tends to $2/N$ as
  $N \to \infty$. Moreover, reordering $z$ stage by stage as $(x_0, u_0, x_1, u_1, \dots)$ makes
  the KKT matrix **block banded with bandwidth $O(n+m)$**, so a sparse factorisation costs
  $O(N(n+m)^3)$. **Eliminating that banded matrix from the back is exactly the Riccati recursion
  of `c4-dp-lqr-lqg`** — on a linear-quadratic problem the two methods are the same computation.
- **R2 (Hermite-Simpson: derivation and order) [D2]** — representing the state on
  $[t_k, t_{k+1}]$ by the cubic Hermite interpolant matched to $(x_k, f_k, x_{k+1}, f_{k+1})$ and
  enforcing the differential equation **at the midpoint** *produces*
  $$
  x_m = \tfrac12(x_k + x_{k+1}) + \tfrac{h}{8}(f_k - f_{k+1}), \qquad u_m = \tfrac12(u_k + u_{k+1}),
  $$
  $$
  \zeta_k = x_{k+1} - x_k - \tfrac{h}{6}\big(f_k + 4f_m + f_{k+1}\big) = 0 \tag{3}
  $$
  (Simpson's quadrature is a conclusion, not an assumption). The method coincides with three-stage
  Lobatto IIIA, so the local error is $O(h^5)$ and the **global order is four**. In the
  reproduction task it measures $4.001$ and $3.996$ on a linear and a nonlinear ODE respectively.
- **R3 (SQP = Newton on the KKT system, quadratic convergence) [D3]** — the KKT conditions of the
  equality-constrained SQP subproblem
  $$\min_d \; \nabla J^\top d + \tfrac12 d^\top W d \quad \text{s.t.}\quad c + \nabla c\,d = 0 \tag{4}$$
  are **exactly** the Newton equations of the nonlinear KKT system
  $F(z,\lambda) = (\nabla J + \nabla c^\top\lambda,\; c) = 0$. Under LICQ and SOSC,
  $\nabla F(z^*)$ is invertible, so full-step SQP converges locally quadratically. But Newton goes
  to a **KKT point**, not to a minimum — a merit function and a line search are needed, and the
  price is the Maratos effect.
- **R4 (the defect is not the trajectory error) [D2]** — $\zeta_k = 0$ says that the interpolated
  trajectory satisfies the dynamics at only **three points** per interval ($t_k$, the midpoint and
  $t_{k+1}$). The residual $r(t)$ in between shrinks as $O(h^4)$ but **is not small at all on a
  coarse grid**. On acrobot swing-up, solving the defect down to $9 \times 10^{-15}$ still leaves a
  residual of $1.2\times10^{2}$ at the interior Gauss points — **seventeen orders of magnitude**.
  So the error estimate driving mesh refinement must be the **interpolant residual**, not the
  defect (Betts 1998 §5).
- **R5 (direct against indirect and iLQR) [D2]** — they part along three axes. (i) **Constraints**:
  a state constraint is a few rows for a direct method and structurally impossible for iLQR (R4 of
  the previous lesson). (ii) **Conditioning**: the transcription is local to each interval, so
  there is no $e^{\sigma T}$ blow-up (R4 of `c4-pontryagin-indirect`). (iii) **Size**: there are
  $O(N(n+m))$ decision variables and a sparse NLP solver is needed. Measured on the acrobot, the
  direct method satisfies the terminal constraint **exactly** to $6\times10^{-23}$ while spending
  $\int u^2dt = 41.34$, whereas iLQR with a quadratic terminal penalty reduces the terminal error
  as the penalty grows ($0.223 \to 0.0385$ rad) but multiplies the control effort twentyfold
  ($23.1 \to 471.0$) and its regularization diverges. **[D2]**

## Derivation

### R1 — counting the sparsity

Stack the decision variables. The simplest order is states first, controls second:

$$
z = \big(x_0, x_1, \dots, x_N,\; u_0, u_1, \dots, u_N\big) \in \mathbb{R}^{n_z},
  \qquad n_z = (N+1)(n+m). \tag{5}
$$

The constraints are $N$ defect blocks ($n$ rows each) plus $2n$ boundary rows, so
$n_c = nN + 2n$.

**The key observation**: only $x_k, x_{k+1}, u_k, u_{k+1}$ appear in the $\zeta_k$ of (3). $x_m$
enters through $f_k$ and $f_{k+1}$, but those are functions of the same four variables. So row
block $k$ of the Jacobian is nonzero in only four column blocks:

$$
\frac{\partial \zeta_k}{\partial z} = \Big[\;\cdots\;
  \underbrace{\tfrac{\partial\zeta_k}{\partial x_k}}_{n\times n}\;
  \underbrace{\tfrac{\partial\zeta_k}{\partial x_{k+1}}}_{n\times n}\;\cdots\;
  \underbrace{\tfrac{\partial\zeta_k}{\partial u_k}}_{n\times m}\;
  \underbrace{\tfrac{\partial\zeta_k}{\partial u_{k+1}}}_{n\times m}\;\cdots\Big]. \tag{6}
$$

Writing each block out (chain rule, with $A_\bullet = \partial f/\partial x$ and
$B_\bullet = \partial f/\partial u$):

$$
\frac{\partial x_m}{\partial x_k} = \tfrac12 I + \tfrac{h}{8}A_k, \quad
  \frac{\partial x_m}{\partial x_{k+1}} = \tfrac12 I - \tfrac{h}{8}A_{k+1}, \quad
  \frac{\partial x_m}{\partial u_k} = \tfrac{h}{8}B_k, \quad
  \frac{\partial x_m}{\partial u_{k+1}} = -\tfrac{h}{8}B_{k+1}, \tag{7}
$$
$$
\frac{\partial \zeta_k}{\partial x_k} = -I - \tfrac{h}{6}\Big(A_k + 4A_m\big(\tfrac12 I + \tfrac{h}{8}A_k\big)\Big),
  \qquad
  \frac{\partial \zeta_k}{\partial u_k} = -\tfrac{h}{6}\Big(B_k + 4\big(A_m\tfrac{h}{8}B_k + \tfrac12 B_m\big)\Big), \tag{8}
$$

and the other two differ only in sign and index (problem P1). Counting nonzeros gives
$n\cdot(2n + 2m)$ per interval plus $2n$ boundary entries, which is (2). The fill is

$$
\text{fill} = \frac{n(2n+2m)N + 2n}{(nN + 2n)\,(N+1)(n+m)}
  \;\xrightarrow[N\to\infty]{}\; \frac{2n+2m}{N(n+m)} = \frac{2}{N}. \tag{9}
$$

For the acrobot ($n=4$, $m=1$), (2) is $40N + 8$; at $N = 40$ the Jacobian is $168\times205$ with
1608 nonzeros and a fill of $4.669\%$ — condition 1 of the reproduction task checks exactly this.
Doubling $N$ doubles the nonzeros but quadruples the dense size, so the fill halves.

**The identity with Riccati.** Instead of (5), group $z$ **stage by stage**:

$$\tilde{z} = \big(x_0, u_0,\; x_1, u_1,\; \dots,\; x_N, u_N\big). \tag{10}$$

In this order $\zeta_k$ touches only two consecutive stage blocks, so $\nabla c$ is **block
bidiagonal** and the KKT matrix

$$
\begin{bmatrix} W & \nabla c^\top \\ \nabla c & 0 \end{bmatrix} \tag{11}
$$

is **block banded** with bandwidth $O(n+m)$ (the cost separates stagewise, so $W$ is block
diagonal too). A banded Cholesky/LDL$^\top$ factorisation costs
$O(N \cdot \text{bandwidth}^3) = O(N(n+m)^3)$, a factor of $N^2$ cheaper than the dense
$O((N(n+m))^3)$.

And eliminating that banded matrix **from $k = N$ down to $k = 0$** produces one Schur complement
per stage — and that Schur complement is exactly the $P_k$ of `c4-dp-lqr-lqg`. In other words, on
a linear-quadratic problem **"direct method plus sparse KKT factorisation" and "the Riccati
recursion" are the same floating-point operations**. All the direct method adds on a nonlinear
problem is to **repeat** that elimination, once per SQP iteration. The previous lesson's "iLQR's
backward pass = elimination of a block tridiagonal Newton system" says the same thing.

**Where the assumptions break**: (2) holds only when a defect couples **two adjacent grid points**.
A higher-order transcription (a pseudospectral method of polynomial degree $p$, say) couples every
point inside an interval, making each block of $\nabla c$ **dense**; a global pseudospectral method
(a single interval) gives a fully dense Jacobian — spectral convergence at the cost of sparsity.
Also, the "$2/N$" of (9) assumes **the dynamics are the only constraints**. Adding state
constraints $g(x_k) \le 0$ adds rows, but each row sees a single grid point, so the sparsity
survives — which is precisely point (i) of R5.

### R2 — deriving Hermite-Simpson

On $[t_k, t_{k+1}]$, put $s = (t - t_k)/h \in [0,1]$ and represent the state by the cubic Hermite
interpolant matched to the **values and derivatives** at both ends:

$$
x(s) = x_k H_{00}(s) + h f_k H_{10}(s) + x_{k+1}H_{01}(s) + h f_{k+1}H_{11}(s), \tag{12}
$$
$$
H_{00} = 2s^3 - 3s^2 + 1, \quad H_{10} = s^3 - 2s^2 + s, \quad
  H_{01} = -2s^3 + 3s^2, \quad H_{11} = s^3 - s^2.
$$

**By construction** this interpolant satisfies $x(0) = x_k$, $x(1) = x_{k+1}$,
$\dot{x}(0) = f_k$ and $\dot{x}(1) = f_{k+1}$ — that is, the dynamics already hold **at the two
endpoints**. No degrees of freedom are left, so the only thing we can additionally enforce is
**one interior point**. Take the midpoint $s = 1/2$.

**The midpoint value.** At $s = 1/2$ we have $H_{00} = \tfrac12$, $H_{10} = \tfrac18$,
$H_{01} = \tfrac12$ and $H_{11} = -\tfrac18$, so

$$x_m := x(\tfrac12) = \tfrac12(x_k + x_{k+1}) + \tfrac{h}{8}(f_k - f_{k+1}). \tag{13}$$

**The midpoint derivative.** Evaluating $H_{00}' = 6s^2 - 6s$, $H_{10}' = 3s^2 - 4s + 1$,
$H_{01}' = -6s^2 + 6s$ and $H_{11}' = 3s^2 - 2s$ at $s = 1/2$ gives $-\tfrac32$, $-\tfrac14$,
$\tfrac32$ and $-\tfrac14$. Since $\dot{x} = (1/h)\,dx/ds$,

$$
\dot{x}(\tfrac12) = \frac{1}{h}\Big[-\tfrac32 x_k - \tfrac{h}{4}f_k
  + \tfrac32 x_{k+1} - \tfrac{h}{4}f_{k+1}\Big]
  = \frac{3}{2h}(x_{k+1} - x_k) - \tfrac14(f_k + f_{k+1}). \tag{14}
$$

Imposing the **collocation condition** $\dot{x}(\tfrac12) = f(x_m, u_m) =: f_m$ on (14) and
rearranging:

$$
\frac{3}{2h}(x_{k+1} - x_k) = f_m + \tfrac14(f_k + f_{k+1})
  \;\Longrightarrow\;
  x_{k+1} - x_k = \tfrac{2h}{3}f_m + \tfrac{h}{6}(f_k + f_{k+1})
  = \tfrac{h}{6}\big(f_k + 4f_m + f_{k+1}\big),
$$

which is (3). **Simpson's quadrature rule came out as a conclusion, not an assumption** — that is
what the name Hermite-Simpson means, and it says far more than an explanation starting from "let
us integrate with Simpson's rule". In particular it explains **why $x_m$ carries that odd $h/8$
term**: (13).

**The order.** The method is the **Lobatto IIIA** implicit Runge-Kutta scheme on the three Lobatto
points $s \in \{0, \tfrac12, 1\}$. An $s$-stage Lobatto IIIA has order $2s - 2$, so $s = 3$ gives
order **four** with local error $O(h^5)$. Condition 2 of the reproduction task measures this on
two ODEs (measured: local order rising $4.46 \to 4.93$ toward 5, global order $4.001$ on the
linear problem and $3.996$ on the nonlinear one).

**Where the assumptions break**: (12) assumes $x$ is a **$C^1$ cubic polynomial inside the
interval**. If the state derivative is discontinuous, as with contact, the interpolation itself is
wrong on that interval and the order collapses — which is why hybrid problems **place the
transition time at a grid point** and split intervals by mode (`c4-contact-implicit-hybrid`).
Also, (3) assumes $u$ is **linear** inside the interval ($u_m$ is the average). If the optimal
control is bang-bang (R3 of the previous lesson), the true control jumps inside an interval, so
unless the grid aligns with the switching time the order drops to one — which is why direct
methods on bang-bang problems either use many grid points or lift the switching times into the
variables.

### R4 — a zero defect can still be a wrong trajectory

This section is the most practically important result of the lesson.

After solving (3), all we know is that the interpolated trajectory satisfies the dynamics at
**three points** per interval. How wrong it is in between must be **measured separately**. Define
the residual

$$
r(t) := \dot{x}_{\text{interp}}(t) - f\big(x_{\text{interp}}(t),\, u_{\text{interp}}(t)\big). \tag{15}
$$

$r$ is zero at the three collocation points and nonzero in between. In theory
$\max_t \lVert r(t)\rVert = O(h^4)$ — but **$O(h^4)$ is a statement about small enough $h$**.

The values measured on the reproduction task's acrobot show the gap ($T = 10$ s,
$\lvert u\rvert \le 20$, linear initial guess):

| $N$ | $h$ | $\max_k\lVert\zeta_k\rVert_\infty$ (defect) | $\max_t\lVert r(t)\rVert_\infty$ (interior Gauss points) |
|---|---|---|---|
| 20 | 0.5 | $5.3\times10^{-15}$ | $5.5\times10^{1}$ |
| 40 | 0.25 | $8.9\times10^{-15}$ | $1.2\times10^{2}$ |
| 80 | 0.125 | $3.6\times10^{-15}$ | $6.6\times10^{1}$ |

The defect is at machine precision and the residual is $10^{2}$ — **seventeen orders of
magnitude**. The NLP solver satisfied the constraints it was given perfectly, and those
constraints said **almost nothing** about the accuracy of the trajectory.

So the mesh refinement procedure becomes (Betts 1998 §5): (i) solve the NLP on the current grid;
(ii) estimate the residual $\int_{t_k}^{t_{k+1}}\lVert r\rVert dt$ per interval **at
non-collocation points**; (iii) split the intervals with a large residual; (iv) interpolate onto
the new grid as a warm start and re-solve. If (ii) used the defect it would always be zero, so
**no refinement would ever happen**.

**Where the assumptions break**: the $O(h^4)$ convergence means something only **along a single
local solution**. The acrobot has several (R5 of the previous lesson), so changing the grid
changes the solution. In the author's implementation, warm-started refinement from $N = 20$ to
$320$ made the cost wander, $4.91 \to 1.83 \to 10.79 \to 20.89 \to 23.16$, and while the residual
did fall, $55.4 \to 161.5 \to 98.7 \to 33.5 \to 9.98$, the observed order over the last refinement
was $1.75$, short of four. Two reasons: (a) each grid reached a different local solution, and
(b) at $N = 320$ the solver hit its iteration cap and the defect stalled at $10^{-8}$. **To
observe the order you must pin the local solution and converge the solver properly** (problem P6).
That is why the order is measured on ODE test problems (condition 2).

### R5 — comparing along three axes

| Axis | Indirect (shooting) | iLQR/DDP | Direct (collocation) |
|---|---|---|---|
| State constraints | the costate becomes a measure (R1 of `c4-pontryagin-indirect`) | nowhere to put them in the backward QP | **a few rows**; each row sees one grid point, so sparsity survives |
| Conditioning | $e^{2\sigma T}$ (R4 there) | local per interval; needs $Q_{uu}$ regularization | local per interval; the conditioning of the banded KKT matrix |
| Decision variables | $n$ (+ $t_f$) | $Nm$ | $(N+1)(n+m)$ |
| Dynamics satisfaction | **exact** to integrator tolerance | **exact** in the forward pass | to solver tolerance, and **only at grid points** (R4) |
| Convergence order | Newton, quadratic (within the conditioning limit) | DDP quadratic / iLQR linear | SQP quadratic (exact Hessian), quasi-Newton superlinear |
| Tooling needed | integrator + root finder | none (write it yourself) | a **sparse NLP solver** (SNOPT, IPOPT) + automatic differentiation |

The last row is the deciding factor in practice. iLQR is two hundred lines; a direct method needs
a solver. In exchange, a direct method **can use constraints**.

**The trade-off, measured.** Acrobot swing-up ($T = 10$ s, $\lvert u\rvert \le 20$, minimising
$\int u^2dt$, terminal $x(T) = (\pi,0,0,0)$):

| Method | $\int u^2 dt$ | terminal error $\lVert x_N - x_{\mathrm{goal}}\rVert_\infty$ | note |
|---|---|---|---|
| direct, $N=40$ | $41.34$ | $6\times10^{-23}$ (**hard constraint**) | $\max\lvert u\rvert = 7.83$, 103 iterations |
| iLQR, terminal penalty $10^3 I$ | $23.09$ | $2.23\times10^{-1}$ | 400 iterations (cap), never reaches the target |
| iLQR, terminal penalty $10^4 I$ | $314.6$ | $1.84\times10^{-1}$ | regularization diverges at 64 iterations |
| iLQR, terminal penalty $10^5 I$ | $471.0$ | $3.85\times10^{-2}$ | regularization diverges at 96 iterations |

How to read it: trying to imitate a hard constraint by growing a penalty does reduce the terminal
error, but **multiplies the cost twentyfold and makes the problem ill-conditioned**. The direct
method meets the same terminal condition to machine precision while spending the
$\int u^2dt$ in between. That is the quantitative case for "use a direct method when you have
constraints".

**Where the assumptions break**: the iLQR in that table is a basic implementation with a
**quadratic terminal penalty**. Lifting it to an augmented Lagrangian (ALTRO) satisfies the
constraint exactly at finite penalty, so the gap narrows — the accurate statement is not "iLQR
cannot use constraints" but "**plain** iLQR's penalty route is expensive, and using constraints
properly requires an outer loop". Conversely the direct method's weakness is in the table too: the
dynamics hold **only at grid points**, so feeding the resulting trajectory to a real robot
open-loop drifts by the residual of R4. A collocation trajectory is **always** used together with
feedback (TVLQR, `c4-dp-lqr-lqg`).

## Proof sketch

### R3 — SQP is Newton on the KKT system and converges quadratically [D3]

**Hypotheses**
H1: $J$ and $c$ are twice continuously differentiable with locally Lipschitz second derivatives.
H2 (LICQ): $\nabla c(z^*)$ has full row rank at the solution $z^*$.
H3 (SOSC): $d^\top \nabla^2_{zz}\mathcal{L}(z^*,\lambda^*)\,d > 0$ for every $d \ne 0$ with
$\nabla c(z^*)d = 0$.
H4: every iteration takes a unit step and the subproblem (4) uses the **exact**
$W = \nabla^2_{zz}\mathcal{L}$.

**Conclusion** C: $(z_k, \lambda_k) \to (z^*, \lambda^*)$ and the convergence is $q$-quadratic.

**Strategy**: write the KKT conditions of subproblem (4) and show they are **the same equations**
as the Newton equations of the nonlinear KKT system
$F(z,\lambda) = \big(\nabla J + \nabla c^\top\lambda,\; c\big) = 0$. Then obtain invertibility of
$\nabla F(z^*)$ from H2 and H3 and apply the standard convergence theorem for Newton's method.

1. **The subproblem's KKT conditions.** (4) is an equality-constrained quadratic program in $d$,
   so with multiplier $\lambda_+$,
   $$W d + \nabla c^\top \lambda_+ = -\nabla J, \qquad \nabla c\,d = -c. \tag{16}$$
2. **The Newton equations of $F = 0$.** The Jacobian of $F$ is
   $\nabla F = \begin{bmatrix} W & \nabla c^\top \\ \nabla c & 0\end{bmatrix}$, so the Newton step
   $(d, \delta\lambda)$ at $(z_k, \lambda_k)$ solves
   $$
   \begin{bmatrix} W & \nabla c^\top \\ \nabla c & 0\end{bmatrix}
     \begin{bmatrix} d \\ \delta\lambda\end{bmatrix}
     = -\begin{bmatrix}\nabla J + \nabla c^\top\lambda_k \\ c\end{bmatrix}. \tag{17}
   $$
   Writing the first row out gives
   $Wd + \nabla c^\top\delta\lambda = -\nabla J - \nabla c^\top\lambda_k$, i.e.
   $Wd + \nabla c^\top(\lambda_k + \delta\lambda) = -\nabla J$. Setting
   $\lambda_+ := \lambda_k + \delta\lambda$ makes this **literally (16)**, and the second rows
   agree too. So **one SQP iteration is one Newton step on the KKT system**.
3. **Invertibility of the KKT matrix.** Suppose $[d; v]$ is in the null space:
   $Wd + \nabla c^\top v = 0$ and $\nabla c\,d = 0$. Premultiplying the first by $d^\top$ gives
   $d^\top W d + (\nabla c\,d)^\top v = d^\top W d = 0$, and since $d$ lies in the null space of
   the constraints, H3 forces $d = 0$. Then $\nabla c^\top v = 0$ and H2 (full row rank) forces
   $v = 0$. So $\nabla F(z^*, \lambda^*)$ is invertible.
4. **Quadratic convergence of Newton.** By H1, $\nabla F$ is locally Lipschitz, and by step 3
   $\nabla F(z^*)$ is invertible, so the standard theorem (Nocedal-Wright Thm. 11.2) gives
   $q$-quadratic convergence in a neighbourhood. **C**.
5. **Inequality constraints.** With inequalities such as $\lvert u\rvert \le \bar{u}$, if **strict
   complementarity** holds at the solution the active set is identified in finitely many
   iterations, after which the argument above applies verbatim to the active constraints treated as
   equalities.

(Omitted: the active-set identification lemma, and the resolution of the Maratos effect, in which
a correct step can **increase** the merit function during globalization — Nocedal-Wright §15.5 and
§18.11, and for an actual implementation
[SNOPT](https://doi.org/10.1137/S0036144504446096) §2.)

**Deleting a hypothesis: where does it collapse?**

- **Delete "exact Hessian" from H4**: quasi-Newton (BFGS) gives superlinear and Gauss-Newton
  first-order convergence. Measured: solving the reproduction task's acrobot with
  `scipy.optimize`'s `trust-constr` (a BFGS approximation) takes 103 iterations at $N = 40$ and
  642 at $N = 80$. Solvers supplied with exact second derivatives (IPOPT with exact Hessians)
  typically take tens. **Quadratic convergence is what second derivatives buy.**
- **Delete "unit step" from H4** (i.e. add globalization): Newton goes to a **KKT point**, which
  need not be a minimum. Measured: Hock-Schittkowski problem 7
  ($\min \ln(1+x_1^2) - x_2$ s.t. $(1+x_1^2)^2 + x_2^2 = 4$, minimum $(0,\sqrt3)$) solved with
  full Newton steps from $x_0 = (2,2)$, $\lambda_0 = -1$ drives the KKT residual
  $4.5\times10^{-1} \to 4.5\times10^{-2} \to 1.8\times10^{-3} \to 5.5\times10^{-6}
  \to 5.5\times10^{-11}$ — **quadratically** (quadratic constants $0.2$–$1.8$) — but lands on
  $(0.4996209240,\, -1.5615528128)$, which is **not the minimum**. Adding an $\ell_1$ merit
  function with backtracking reaches $(0,\sqrt3)$ to $2.2\times10^{-16}$, but only after seven
  iterations stuck at $\alpha \le 2^{-6}$ before $\alpha = 1$ is accepted and quadratic
  convergence resumes. It is **the same structure** as the merit discussion in R3 of the previous
  lesson.
- **Delete H3 (SOSC)**: step 3 fails, the KKT matrix can be singular, and the step is undefined or
  not a descent direction. The remedy is, as in the previous lesson, **regularization**
  ($W + \mu I$ or a trust region).
- **Delete H2 (LICQ)**: multipliers are non-unique or unbounded and the subproblem (4) can be
  infeasible. This **actually happens** in transcriptions — for instance when terminal conditions
  are stated redundantly (both $x_N = x_{\mathrm{goal}}$ and
  $\lVert x_N - x_{\mathrm{goal}}\rVert = 0$), or when the number of active state constraints
  exceeds the available degrees of freedom. **Counting the independence of the constraints** is the
  first step in debugging a transcription.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R1)** Write out the two blocks not given in (8),
$\partial\zeta_k/\partial x_{k+1}$ and $\partial\zeta_k/\partial u_{k+1}$, from (7). Then say
which block simplifies when $f$ is **affine in the control**.
*Solution sketch*: differentiating $\zeta_k$ with respect to $x_{k+1}$ produces $+I$ and the rest
differs from (8) only in sign and index. Affineness in $u$ makes $B_\bullet$ a function of the
state alone with $\partial B/\partial u = 0$, so the second-derivative terms vanish — though $B_m$
still depends on all four variables through $x_m$.

**P2 (derivation, ★★, R2)** Show that the cubic Hermite interpolant (12) is the **unique** cubic
polynomial satisfying the four conditions $x(0)=x_k$, $x(1)=x_{k+1}$, $\dot x(0)=f_k$,
$\dot x(1)=f_{k+1}$. Then derive the defect you get by collocating at $s = 1/3$ instead of the
midpoint, and explain why that method has order below four.
*Solution sketch*: a cubic has four coefficients and there are four conditions, so uniqueness
follows from invertibility of the resulting Vandermonde-like system. For the $s=1/3$ defect,
substitute $H_\bullet(1/3)$ and $H_\bullet'(1/3)$. The order drops because of the **accuracy of
the quadrature**: Simpson on the Lobatto points $(0, 1/2, 1)$ is exact for cubics, while
$\{0, 1/3, 1\}$ is not. The quadrature's order sets the collocation method's order.

**P3 (proof, ★★★, R1)** Show that in the stagewise order (10) the KKT matrix (11) has bandwidth
$O(n+m)$, and prove, for a linear-quadratic problem, that the Schur complement produced by block
eliminating that banded matrix from $k = N$ down to $0$ is the (13) of `c4-dp-lqr-lqg` (the
Riccati recursion).
*Solution sketch*: the strategy is "eliminate the last stage block, write its effect on the rest as
a Schur complement, confirm that the complement is what gets added to the quadratic coefficient of
$x_{N-1}$, then induct". There is no key inequality; the key **identity** is that the
$-\nabla c_{\text{last}}^\top (\text{block})^{-1}\nabla c_{\text{last}}$ from the elimination
equals $-A^\top P B (R + B^\top P B)^{-1} B^\top P A$. Also write one line on why, on a
**non**linear problem, the identity holds only per iteration.

**P4 (numerical, ★, R1)** For $n = 13$, $m = 12$ (quadruped scale) and $N = 100$, compute the
nonzero count of (2), the number of entries in the dense Jacobian, and the fill. Estimate, to an
order of magnitude, the ratio of the operation counts of a dense LDL$^\top$ factorisation and a
banded one.
*Answer*: $n_z = 101\cdot25 = 2525$ and $n_c = 13\cdot100 + 26 = 1326$;
$\operatorname{nnz} = 13(2\cdot13 + 2\cdot12)\cdot100 + 26 = 13\cdot50\cdot100 + 26 = 65\,026$;
the dense entry count is $1326 \cdot 2525 = 3\,348\,150$ and the fill is $1.942\%$ (tolerance
$0.001\%$). The factorisation costs are dense $O((n_z + n_c)^3) \approx (3851)^3
\approx 5.7\times10^{10}$ against banded $O(N(n+m)^3) = 100\cdot 25^3 = 1.6\times10^{6}$, about
**four orders of magnitude**.
*Check*: compare the approximation $2/N = 2\%$ of (9) against the exact $1.942\%$.

**P5 (numerical, ★★, R2)** Apply one Hermite-Simpson step to the scalar problem
$\dot{x} = \lambda x$, obtain the amplification factor $x_{k+1}/x_k$ as a rational function of
$z = h\lambda$, and expand its difference from $e^z$ to show the local order is five.
*Answer*: substituting $f = \lambda x$ into (13) and (3) and solving gives
$$
\frac{x_{k+1}}{x_k} = \frac{1 + \tfrac{z}{2} + \tfrac{z^2}{12}}{1 - \tfrac{z}{2} + \tfrac{z^2}{12}}
$$
(tolerance: the coefficients must match exactly). This is the $(2,2)$ Padé approximant of $e^z$,
and $e^z - (\cdot) = \tfrac{z^5}{720} + O(z^6)$, so the local order is five and the global order
four.
*Check*: measuring the local error numerically at $\lambda = -2$ for
$h = 0.4, 0.2, 0.1, 0.05, 0.025$ gives $2.12\times10^{-4}$, $9.62\times10^{-6}$,
$3.65\times10^{-7}$, $1.26\times10^{-8}$, $4.13\times10^{-10}$, with observed order rising
$4.46 \to 4.93$ toward five. Confirm as well that the limit of this rational function as
$\lvert z \rvert \to \infty$ is one, so the method is **A-stable but not L-stable** (which matters
on stiff problems).

**P6 (implementation, ★★★, R4)** Show that the interpolant residual on the reproduction task's
acrobot **really does** fall as $O(h^4)$. The author's implementation reported in the text got
stuck at an observed order of $1.75$, for two reasons: (a) each grid reached a different local
solution, and (b) incomplete convergence at large $N$. Remove both.
*Rubric*: (a) you show the local solution was pinned (e.g. warm-start by interpolating the coarse
solution and confirm consecutive grids lie on the same homotopy branch, by cost and control
shape); (b) you converge the KKT residual below the same threshold on every grid (defect
$< 10^{-10}$, first-order optimality $< 10^{-8}$); (c) on at least four grids the slope of
$\log\max_t\lVert r\rVert$ against $\log h$ is $4 \pm 0.3$; (d) you list each failed attempt and
its cause in one line; (e) succeeding first on an easier problem (pendulum swing-up, say) is
allowed, in which case you write why the acrobot is harder.

**P7 (counterexample, ★★, R4)** Show in **two different ways** that "making the defect small
enough makes the trajectory accurate" is false: (i) an example in which the defect is at machine
precision while the interpolant residual is $O(1)$ (reproduce the table in the text); (ii) an
extreme example (a couple of grid points) in which the defect is zero yet the interpolated
trajectory is **not a solution of the dynamics at all**.
*Property checklist*: for (i), reproduce the table and evaluate the residual densely inside an
interval to see where the maximum sits (far from the midpoint). For (ii), take $N = 1$ or 2 with
the endpoint conditions far apart and plot the interpolated trajectory — the defect is zero by
definition but that cubic has nothing to do with the true trajectory. The property to check: the
defect is a condition **at the grid points**, so on a coarse grid it carries no information.

**P8 (paper, ★★, R1 and R4)** Read Betts 1998 §4–§6 and Kelly 2017 §5, §7, then: (a) confirm
whether the mesh-refinement criterion Betts recommends is the same quantity as (15) of this
lesson; (b) list three things Kelly names as "the most common bugs in a direct-method
implementation" and say which result of this lesson each connects to; (c) give two transcription
design decisions that **neither** text addresses.
*Rubric*: (a) passes if it identifies "the integral of the per-interval residual (or its relative
value)" and states explicitly that it is a different quantity from the defect. (b) passes if it
names three of "derivative sign/transpose errors, grid misaligned with switching times, an
infeasible initial guess, scaling" and connects each to R1, R2 or R5. (c) passes with two of
"variable scaling, handling a free terminal time, where state constraints are discretised (grid
points only, or inside intervals too), how the Hessian is supplied to the solver".

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read with three passes, attacking questions 4, 5, 6 and 7 on the third.

1. **Hargraves & Paris, "Direct trajectory optimization using nonlinear programming and
   collocation" (1987, AIAA JGCD)** — role: `seminal`. What to read: §II–§III. This is the
   original source for (3) of this lesson. See **why** the method was needed in 1987 (path
   constraints in aerospace).
   Extra questions: (a) what do the authors say they pay for lifting both states and controls into
   the variables? (b) What NLP size (number of variables) was current then, and how many orders of
   magnitude away is that from today? (c) Do the authors distinguish the defect from the trajectory
   error? If not, where is the gap first pointed out?
2. **Betts, "Survey of numerical methods for trajectory optimization" (1998, AIAA JGCD)** — role:
   `survey`. What to read: §4 (direct methods), §5 (mesh refinement and error estimation),
   §6 (recommendations). You read §3 in `c4-pontryagin-indirect`; this time it is the other side.
   Extra questions: (a) translate the error estimate of §5 into the (15) of this lesson. (b) Is
   there a passage recommending "use a direct method but verify with an indirect one"? What exactly
   does that verification compare? (c) Which of the 1998 recommendations have changed by 2026
   (automatic differentiation, interior-point methods, mature sparse solvers)?
3. **Kelly, "An introduction to trajectory optimization: how to do your own direct collocation"
   (2017, SIAM Review)** — role: `standard`. What to read: §2–§5, §7 (practical advice). This is
   the implementation guide for the lesson. Read **after** writing the reproduction task and §7
   reads as your own bug list.
   Extra questions: (a) on what criteria does the author compare trapezoidal against
   Hermite-Simpson, and what practical differences beyond the order does he name? (b) What is his
   method for generating an initial guess, and how does it relate to the local-solution problem of
   R4? (c) To what depth does this text treat **state constraints**?

**The ten fixed questions**: (1) What problem is solved, under what assumptions? (2) What exactly
could prior work not do? (3) Reduce the core idea to one equation. (4) What are the theoretical
guarantees, and **what is not guaranteed**? (5) What are the independent and dependent variables
and the baselines, and were the baselines tuned fairly? (6) Do the metrics match the claims, and
are variance and seeds reported? (7) What information needed for reproduction is missing? (8) If
the result were wrong, which assumption would you doubt first? (9) What are the computational and
memory complexity and the real-time behaviour? (10) What would you change to go beyond this paper
in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one notebook CPU core, under 20 minutes total,
under 1 GB of memory. numpy and scipy only
(`scipy.optimize.minimize(method="trust-constr")`, `scipy.sparse`). No simulator.

**Input data**: none; everything is given as constants.

**System A — two scalar ODEs** (for measuring the order): $\dot{x} = \lambda x$ with
$\lambda = -2$, $x_0 = 1$ on $[0,2]$ (solution $e^{-4}$), and $\dot{x} = -x + x^2/2$ with
$x_0 = 0.5$ on $[0,2]$ (reference value by fine-step RK4: $0.08632906595998$).

**System B — the acrobot** (Spong parameters): $m_1 = m_2 = 1$, $l_1 = 1$, $l_2 = 2$,
$l_{c1} = 0.5$, $l_{c2} = 1$, $I_1 = 0.083$, $I_2 = 0.33$, $g = 9.81$. $q_1$ is measured from the
**downward vertical** and the torque acts **at the elbow only** ($B = (0,1)^\top$). The mass
matrix and the bias are

$$
M = \begin{bmatrix}
  I_1 + I_2 + m_1 l_{c1}^2 + m_2(l_1^2 + l_{c2}^2) + 2k\cos q_2 &
  I_2 + m_2 l_{c2}^2 + k\cos q_2 \\
  I_2 + m_2 l_{c2}^2 + k\cos q_2 & I_2 + m_2 l_{c2}^2
  \end{bmatrix}, \quad k := m_2 l_1 l_{c2},
$$
$$
\mathrm{bias} = \begin{bmatrix}
  -k\dot q_2^2 \sin q_2 - 2k\dot q_1\dot q_2 \sin q_2
  + (m_1 l_{c1} + m_2 l_1)g\sin q_1 + m_2 l_{c2}g\sin(q_1+q_2) \\
  k\dot q_1^2 \sin q_2 + m_2 l_{c2}g\sin(q_1+q_2)
  \end{bmatrix}
$$

with $M\ddot q = (0, u)^\top - \mathrm{bias}$. The problem is $T = 10$ s,
$x_{\mathrm{init}} = (0,0,0,0)$ (hanging), $x_{\mathrm{goal}} = (\pi,0,0,0)$ (upright),
$\lvert u \rvert \le 20$, cost $\int_0^T u^2 dt$ (Simpson quadrature), and the initial guess is
$x$ **linearly interpolated** between the endpoints with $u = 0$.

**Acceptance criteria** — all four must hold to pass.

1. **Dynamics and sparsity.** (a) Integrating with RK4 ($h = 10^{-4}$) for ten seconds at zero
   torque, the energy drift is $\lvert E(10) - E(0)\rvert < 10^{-12}$ (from the two initial states
   $(0.1,0,0,0)$ and $(1,-0.5,0.3,0.2)$; the author's implementation gave $7\times10^{-15}$ and
   $2\times10^{-13}$). If this check fails, $M$, the bias and $V$ are mutually inconsistent, so
   **do not proceed**. (b) The nonzero count of the constraint Jacobian matches the $40N + 8$ of
   (2) **exactly**: at $N = 20, 40, 80$ it is $808$, $1608$, $3208$ with shapes
   $(88,105)$, $(168,205)$, $(328,405)$ and fills $8.745\%$, $4.669\%$, $2.415\%$ (tolerance
   $0.001\%$).
2. **The order of Hermite-Simpson (system A).** (a) Local: at $\lambda = -2$ and
   $h = 0.4 \to 0.025$, the one-step error runs
   $2.123\times10^{-4} \to 4.129\times10^{-10}$ with observed order rising $4.46 \to 4.93$ toward
   five. (b) Global: splitting $[0,2]$ into $N = 5,10,20,40,80$ gives observed orders
   $4.042, 4.010, 4.003, 4.001$ on the linear problem and
   $3.969, 3.993, 3.998, 3.996$ on the nonlinear one (each $\pm 0.05$). (c) The amplification
   factor of P5 matches $(1 + z/2 + z^2/12)/(1 - z/2 + z^2/12)$ coefficient for coefficient.
3. **Acrobot swing-up.** From the linear initial guess at $N = 40$: (a)
   $\max_k\lVert\zeta_k\rVert_\infty < 10^{-10}$ (author's implementation
   $8.9\times10^{-15}$); (b) the boundary residual is $< 10^{-10}$ (author's
   $5.9\times10^{-23}$) and each component of $x_N$ is within $10^{-9}$ of $(\pi, 0, 0, 0)$;
   (c) $\lvert u_k\rvert \le 20 + 10^{-9}$ at every $k$ (the author's maximum was $7.829233$);
   (d) you report the cost $\int u^2dt$ (the author's was $41.34485538$ — since there are several
   local solutions, **the value itself is not an acceptance criterion**; write down yours and
   confirm that changing the initial guess changes it).
4. **Separate the defect from the error.** (a) Measuring the residual (15) at the two interior
   Gauss points $s = \tfrac12 \mp \tfrac{\sqrt3}{6}$, show that
   $\max_t\lVert r\rVert_\infty$ is **greater than one** for $N = 20, 40, 80$ (the author's values:
   $55.4$, $122.2$, $65.6$). (b) The defect of the same solutions is below $10^{-14}$; report that
   the ratio of the two quantities exceeds $10^{15}$. (c) Solve the same problem with iLQR (the
   previous lesson's implementation) using a quadratic terminal penalty $q I$ for
   $q \in \{10^3, 10^4, 10^5\}$, tabulate $\int u^2dt$ and the terminal error, and confirm the
   trend that growing the penalty **reduces the terminal error while raising the cost and
   diverging the regularization** (the author's: $23.09/0.223$, $314.6/0.184$, $471.0/0.0385$).

**Baselines**: (i) the closed form and fine-step RK4 are the baselines for system A's two ODEs.
(ii) The energy conservation of condition 1(a) is an independent baseline for the dynamics
implementation (recomputing the bias from the Lagrangian by finite differences and matching the
analytic expression to within $10^{-8}$ is also recommended — the author confirmed
$6.4\times10^{-9}$ over 500 random states). (iii) The iLQR of condition 4(c) is the baseline for
the direct method. (iv) The Jacobian must match a full finite-difference Jacobian to within
$10^{-6}$ (check at small $N$ only).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The acrobot integration diverges to `nan` | the $m_1 l_{c1}^2$ and $m_2 l_{c2}^2$ terms are missing from the mass matrix, making $M$ indefinite | print $\det M$ at $q_2 = 0, \pi/2, \pi$; all must be positive (author's values $0.773$, $1.773$, $0.773$) |
| Energy is not conserved even at zero torque | the Coriolis terms of the bias are inconsistent with $M$ and $V$ | recompute the bias from the Lagrangian by finite differences and compare with the analytic form (the baseline of condition 1a) |
| The NLP terminates as infeasible | the initial guess satisfies the dynamics not at all, or $T$ is too short for the target to be reachable | try a larger $T$, and print the norm of the initial defect to see its size |
| Convergence is extremely slow (thousands of iterations) | the solver approximates the Hessian by quasi-Newton (H4 violated) | record the iteration count against $N$; a solver given exact second derivatives takes tens |
| The defect is $10^{-15}$ but the trajectory looks wrong | **not a bug** — this is R4 itself | measure the residual of condition 4(a) and refine the grid |
| The Jacobian disagrees with finite differences | the $u$ dependence of $x_m$ in (7) is missing (the commonest bug) | shrink to $N = 2$ and compare block by block |
| Refining the grid makes the cost larger | you reached a different local solution | use a warm start and overlay the control shapes of the two solutions |
| The cost you report differs from the author's | that is normal — there are several local solutions | condition 3(d) asks for a **report**, not a value |

## Open problems

- **(open problem) A guarantee tying transcription error to optimality error** — a direct method
  makes two kinds of error: the discretisation error ($O(h^4)$, R2 and R4) and the solver's
  optimality error. Practice looks at them separately, but for a general nonlinear problem there
  is no **computable bound** on "how far the trajectory obtained with grid $h$ and solver tolerance
  $\epsilon$ is from the optimum of the continuous problem". Current approaches: a posteriori error
  estimation in mesh refinement ([Betts 1998](https://doi.org/10.2514/2.4231) §5) and duality gaps
  of convex relaxations. What is missing: an a posteriori bound combining both errors in one
  inequality.
- **(open problem) Grid design for problems with bang-bang controls and singular arcs** — as R2's
  failure mode showed, a control that jumps inside an interval drops the order to one. Lifting the
  switching times into variables (a multi-phase transcription) restores the order but requires
  **knowing the number and order of the switches in advance** — the same gap as open problem 3 of
  `c4-pontryagin-indirect`. Current approaches: adaptive meshes that cluster grid points near
  switches, and transcriptions that include the phase structure. What is missing: a transcription
  that treats the switching structure **as part of the problem being solved** while staying
  polynomial time.
- **(open problem) Real-time transcription** — with $O(N(n+m))$ variables, a transcription is too
  heavy to re-solve every cycle as MPC does. Sparsity, warm starts and real-time iteration have cut
  that a great deal, but solving a transcription **including contact** at kHz rates at
  quadruped or humanoid scale ($n \gtrsim 30$) is still open. Current approaches: real-time
  iteration and structure-exploiting QP solvers (`c4-mpc` and
  [Diehl et al. 2009](https://doi.org/10.1007/978-3-642-01094-1_32)), and constraint handling that
  preserves the $O(N)$ structure of the DDP family
  ([Crocoddyl](https://doi.org/10.1109/ICRA40945.2020.9196673)). What is missing: a solver
  **linear** in the number of constraints that keeps DDP's constants.
- **(open problem) Global optimality of a non-convex transcription** — transcription does not
  change the local solutions (R4's failure mode). Convex decomposition (GCS,
  `c6-combinatorial-gcs`) has opened a route back to globality, but it extends only partially to
  problems with dynamics. Current approaches: shortest-path relaxations on a graph and
  mixed-integer transcriptions. What is missing: a **tractable** convex relaxation with a gap bound
  for problems including contact and dynamics — the gap repeated in the previous three lessons.

## Concept check

Run `rc quiz c4-direct-collocation-sqp`. The quiz is for **concept checking only**; the real work
is the problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

The seven items cover: the fundamental reason the transcribed Jacobian is sparse; where the $h/8$
term of the midpoint state comes from; the global order of Hermite-Simpson; whether a
machine-precision defect means an accurate trajectory; the grounds for SQP's quadratic
convergence; whether full Newton steps on the KKT system always reach a minimum; and the relation
between sparse KKT elimination and the Riccati recursion.

## How to study this stage

1. **Check the dynamics first (40 min)** — port the $M$ and bias of system B into code and confirm
   **energy conservation at zero torque** (condition 1a). The author's first implementation omitted
   the $m l_c^2$ terms of $M$, making the mass matrix indefinite, and grouped the Coriolis terms of
   the bias wrongly, drifting the energy by 8 units. Recomputing the bias from the Lagrangian by
   finite differences and matching the analytic form is the fastest diagnosis. **Skip this step and
   you will have to suspect everything else.**
2. **Derive Hermite-Simpson on paper (60 min)** — (12)→(14)→(3). Computing $H_\bullet(1/2)$ and
   $H_\bullet'(1/2)$ yourself shows that the $h/8$ term and the Simpson weights $(1,4,1)/6$ come
   **out of the same interpolant**. Then do P5 for the amplification factor and confirm the Padé
   form and the order.
3. **Measure the order on the scalar ODEs (50 min)** — system A is ten lines. Having extracted the
   global order 4.00 with your own hands, you can later blame **the problem rather than the code**
   when the acrobot does not show the order.
4. **Count the sparsity (50 min)** — derive (6)→(9), then compute the Jacobian by full finite
   differences at small $N$ and match the nonzero count against (2). Working P4's quadruped-scale
   numbers by hand makes "why a sparse solver" felt in orders of magnitude.
5. **Implement the transcription, writing the Jacobian yourself (150 min)** — a finite-difference
   Jacobian works but is slow, and writing (7)–(8) by hand is what puts R1 in your hands. The
   commonest bug is omitting the **$u$ dependence** of $x_m$
   ($\partial x_m/\partial u_k = \tfrac{h}{8}B_k$). Compare block by block against finite
   differences at $N=2$.
6. **Pry the defect and the error apart yourself (80 min)** — this is the central experience of the
   lesson. On a solution whose defect is $10^{-15}$, the residual at the interior Gauss points is
   $10^2$. That single measurement permanently fixes the definition "collocation holds only at the
   specified points". Then refine the grid and watch the residual fall — while also watching the
   cost wander (local solutions).
7. **Run SQP by hand on a small problem (60 min)** — solve HS7 with full Newton steps and see both
   that the KKT residual falls quadratically and that **the point reached is not the minimum**.
   Then add an $\ell_1$ merit function so it does reach the minimum. Recognising the same structure
   as the previous lesson's $z$ test binds the two lessons into one.
8. **Put it side by side with iLQR (60 min)** — build the table of condition 4(c) yourself. The
   number "imitating a hard constraint with a penalty costs twenty times the effort" stands in for
   R5's conclusion.
9. **Read the papers after implementing (150 min)** — Hargraves & Paris (the original) → Betts
   §4–§6 (mesh refinement) → Kelly §7 (practical advice). Kelly §7 in particular must be read
   **after** writing the code for it to read as your own bug list. Write the one-page note per
   paper — **without exception**.
10. **End with what cannot be done (30 min)** — pick one of the four open problems and write a
    paragraph. The third (real-time transcription) is the starting point of the very next lesson,
    `c4-mpc`.

**Passing bar**: you can derive (13), (14) and (3) from a blank page, you can count and write the
nonzero formula (2), you can explain "SQP = Newton on the KKT system" via (16) and (17), you can
state the difference between the defect and the interpolant residual in numbers you measured
yourself, you have code satisfying all four acceptance criteria of the reproduction task, and you
have notes on all three papers.
