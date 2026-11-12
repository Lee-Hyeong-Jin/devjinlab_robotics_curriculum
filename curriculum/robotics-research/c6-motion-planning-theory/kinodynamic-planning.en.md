---
id: c6-kinodynamic-planning
lang: en
title: Differential constraints and lattice planning
summary: >-
  Breaking assumption (A2), that "a path need only be continuous". Under a differential constraint
  $\dot x = f(x,u)$, joining two states is itself an optimal control problem, and for a linear system
  its solution is closed-form through the controllability Gramian. Derive fixed-time minimum-effort
  steering, obtain the stationarity condition satisfied by the optimal steering time $\tau^\ast$ of
  the time-weighted cost, and then see why putting that steering into RRT* requires cost sublevel
  sets rather than balls. Finally derive the closure condition of the other route — motion
  primitives and a state lattice. The reproduction task runs a double-integrator kinodynamic RRT*
  and measures its convergence.
objectives:
  - Derive the solution and cost of fixed-time minimum-effort steering through the controllability Gramian.
  - Write the stationarity condition for the optimal steering time of the time-weighted cost and solve it in closed form for the double integrator.
  - Explain by counterexample why kinodynamic RRT* must use cost sublevel sets rather than Euclidean balls.
  - Derive, from a Dubins arc, the condition for a state lattice to close (primitives joining lattice points exactly).
  - Explain how asymptotic optimality is recovered on systems where steering is unavailable (forward propagation plus pruning).
tags: [motion-planning, kinodynamic, differential-constraints, steering, state-lattice, research]
---

# Differential constraints and lattice planning

## Setup and notation

The five earlier lessons of this module are assumed. This lesson **breaks assumption (A2)** of
`c6-cspace-complexity`: a path may no longer be merely continuous, it must **satisfy the
dynamics**. Also assumed:

- Linear systems: state-space models, the matrix exponential $e^{At}$, controllability and its
  Gramian. The Riccati equation is **not** needed.
- Only the **vocabulary** of optimal control: cost functional, costate. No general calculus of
  variations — here the problem is reduced to a minimum-norm problem under a linear constraint (a
  pseudo-inverse) (recommended prerequisites `r0-linear-algebra-decompositions`, `c4-dp-lqr-lqg`).

Notation (in addition to the module's):

| Symbol | Meaning |
|---|---|
| $x \in \mathbb{R}^n$ | state; $(p, v)$ for a double integrator |
| $u \in \mathbb{R}^m$ | control input |
| $\dot x = Ax + Bu$ | linear dynamics (the assumption of R1 and R2) |
| $\mathcal{R}(x_0, \tau)$ | the set reachable within time $\tau$ |
| $G(\tau)$ | controllability Gramian $\int_0^\tau e^{As}BR^{-1}B^\top e^{A^\top s}\,ds$ |
| $d(\tau)$ | $x_1 - e^{A\tau}x_0$ — the part the free motion does not cover |
| $c(x_0, x_1)$ | optimal steering cost $\min_\tau c(\tau)$ |
| $\tau^\ast$ | optimal steering time |
| $\lambda$ | terminal costate $G(\tau)^{-1}d(\tau)$ |
| $\mathcal{P}$ | set of motion primitives |
| $\Lambda$ | state lattice |

**The cost.** This lesson uses the cost that charges both time and control effort,

$$
J(u, \tau) \;=\; \int_0^\tau \big(1 + u(t)^\top R\, u(t)\big)\,dt
  \;=\; \tau + \int_0^\tau u^\top R\,u\,dt
  \tag{1}
$$

with $R \succ 0$. Charging time alone ($R \to 0$) drives the cost to zero without input bounds, and
charging effort alone ($1 \to 0$) makes infinitely slow motion optimal. **Both terms are needed, and
their trade-off determines $\tau^\ast$.**

One assumption, stated explicitly: **(A6) steerability** — for any two states $x_0, x_1$ there is a
control taking $x_0$ exactly to $x_1$, and its optimal cost is computable. For linear controllable
systems R1 provides this. **For nonlinear systems it is generally false**, and what to do then is R4.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof).

- **R1 (fixed-time optimal steering and the stationarity condition for $\tau^\ast$) [D2]** — if
  $(A,B)$ is controllable, the minimum-effort steering over a fixed time $\tau$ is
  $$u^\ast(t) = R^{-1}B^\top e^{A^\top(\tau - t)}\,\lambda, \quad \lambda = G(\tau)^{-1}d(\tau),
    \qquad c(\tau) = \tau + d(\tau)^\top G(\tau)^{-1} d(\tau) \tag{2}$$
  and the optimal steering time satisfies
  $$\dot c(\tau^\ast) = 1 - 2\,(A x_1)^\top \lambda - \lambda^\top B R^{-1} B^\top \lambda = 0
    \tag{3}$$
  **For the double integrator this solves in closed form**: going from rest to rest over a
  displacement $(\Delta p_1, \Delta p_2)$ gives
  $c(\tau) = \tau + 12(\Delta p_1^2+\Delta p_2^2)/\tau^3$, so for $\Delta p = (1,1)$
  $$c(\tau) = \tau + \frac{24}{\tau^3},\quad \tau^\ast = 72^{1/4} = 2.912950630244,
    \quad c^\ast = \tfrac43\,72^{1/4} = 3.883934173659. \tag{4}$$
- **R2 (conditions for asymptotic optimality of kinodynamic RRT*) [D2]** — three things are needed
  at once. (a) **Exact optimal steering** (A6) — approximate steering makes rewiring wrong.
  (b) The neighbour set must be defined as a **cost sublevel set**,
  $N(x) = \{x' : c(x', x) \le r_n\}$. With a Euclidean ball, asymmetry
  ($c(x_0,x_1) \ne c(x_1,x_0)$) and dynamically inaccessible directions make most of the neighbours
  unconnectable and asymptotic optimality fails. (c) The radius rule must be rewritten in terms of
  the **volume of the reachable set** — the effective dimension is not $n$ but a value set by the
  dynamics (for $\dot x = Ax+Bu$ the volume of $\mathcal{R}(x_0,\tau)$ is a power of $\tau$ whose
  exponent is fixed by the Kalman controllability index).
- **R3 (closure condition of a state lattice) [D2]** — a lattice $\Lambda$ with a primitive set
  $\mathcal{P}$ is **closed** when every $\pi \in \mathcal{P}$ starts at a point of $\Lambda$ and
  ends **exactly** at a point of $\Lambda$. A left arc of curvature radius $\rho$ turning from
  heading $\theta_i$ to $\theta_j$ displaces
  $$\Delta p = \rho\big(\sin\theta_j - \sin\theta_i,\; \cos\theta_i - \cos\theta_j\big) \tag{5}$$
  so if $\Lambda$'s positions are $\mathbb{Z}^2$, the primitive exists **only when (5) is an integer
  vector**. That condition is why lattice designs take "Pythagorean" headings (rational $\sin$ and
  $\cos$).
- **R4 (when steering is unavailable) [D1]** — if (A6) fails on a nonlinear system, rewiring itself
  is impossible. The alternative is **forward propagation plus pruning**: grow the tree by
  integrating random controls and cull bad branches by a domination relation within
  $\delta$-neighbourhoods of the cost-state space. That structure gives asymptotic
  (near-)optimality without steering
  ([Li, Littlefield & Bekris 2016](https://arxiv.org/abs/1407.2896)).

## Derivation

### R1 — fixed-time optimal steering

**The reachable set.** The solution of a linear system is
$$x(\tau) = e^{A\tau}x_0 + \underbrace{\int_0^\tau e^{A(\tau - s)}B\,u(s)\,ds}_{=:\ \mathcal{L}_\tau u},$$
so $x(\tau) = e^{A\tau}x_0 + \mathcal{L}_\tau u$ where $\mathcal{L}_\tau$ is a **linear** operator
$L^2([0,\tau];\mathbb{R}^m) \to \mathbb{R}^n$. Hence **the reachable set is the image of
$\mathcal{L}_\tau$ translated by $e^{A\tau}x_0$**, an affine subspace, and controllability makes that
image all of $\mathbb{R}^n$. The steering problem reduces to the **minimum-norm solution** of the
linear equation $\mathcal{L}_\tau u = d(\tau)$ — no differential geometry and no calculus of
variations required.

**The minimum-norm solution.** With the inner product
$\langle u, w\rangle_R = \int_0^\tau u^\top R w \, dt$, the adjoint of $\mathcal{L}_\tau$ is
$(\mathcal{L}_\tau^\ast \lambda)(t) = R^{-1}B^\top e^{A^\top(\tau - t)}\lambda$ (verify
$\langle \mathcal{L}_\tau u, \lambda\rangle = \langle u, \mathcal{L}_\tau^\ast\lambda\rangle_R$
directly), and therefore

$$
\mathcal{L}_\tau \mathcal{L}_\tau^\ast
  = \int_0^\tau e^{A(\tau-s)} B R^{-1} B^\top e^{A^\top(\tau - s)}\,ds
  = \int_0^\tau e^{A\sigma} B R^{-1} B^\top e^{A^\top \sigma}\,d\sigma = G(\tau),
$$

substituting $\sigma = \tau - s$. The minimum-norm solution is
$u^\ast = \mathcal{L}_\tau^\ast G(\tau)^{-1}d$, which is the first equation of (2), and its norm is

$$
\int_0^\tau u^{\ast\top} R u^\ast dt = \langle u^\ast, u^\ast\rangle_R
  = \langle \mathcal{L}_\tau^\ast \lambda, \mathcal{L}_\tau^\ast\lambda\rangle_R
  = \lambda^\top \mathcal{L}_\tau\mathcal{L}_\tau^\ast \lambda
  = d^\top G(\tau)^{-1} d,
$$

the second equation of (2). **$\lambda$ is the costate and $G^{-1}$ measures "how hard you must
push".** As $\tau \to 0$, $G(\tau) \to 0$ and the cost diverges — the quantitative form of the
obvious fact that going far in little time takes unbounded effort.

**The optimal steering time.** The total cost (1) is
$c(\tau) = \tau + d(\tau)^\top G(\tau)^{-1}d(\tau)$, and differentiating gives (3):
$$\dot c(\tau) = 1 - 2\,(Ax_1)^\top \lambda - \lambda^\top B R^{-1}B^\top \lambda.$$
Each term has a clear meaning — the 1 is the growth of the time cost, the second is the benefit of
the target state "drifting towards you" under the free motion, and the third is the effort saved by
taking longer. For small $\tau$ the third dominates and $\dot c < 0$; for large $\tau$ the 1
dominates and $\dot c > 0$, so **the zero of $\dot c$ is the unique minimum**. (Equation (3) was
checked numerically against finite differences on 200 random instances, agreeing to
$2.3\times10^{-7}$, the level of the difference error.)

**Closed form for the double integrator.** With $n=4$, $x = (p_1,p_2,v_1,v_2)$,
$e^{A\tau} = \begin{bmatrix} I & \tau I \\ 0 & I\end{bmatrix}$ and $R = I$, each axis has

$$
G_{\text{axis}}(\tau) = \begin{bmatrix} \tau^3/3 & \tau^2/2 \\ \tau^2/2 & \tau \end{bmatrix},
\qquad
G_{\text{axis}}^{-1} = \frac{12}{\tau^4}\begin{bmatrix} \tau & -\tau^2/2 \\ -\tau^2/2 & \tau^3/3\end{bmatrix}
$$

(since $\det G_{\text{axis}} = \tau^4/3 - \tau^4/4 = \tau^4/12$). Writing
$a_i = \Delta p_i - \tau v_{0,i}$ and $b_i = \Delta v_i$,

$$
c(\tau) = \tau + \sum_{i}\left(\frac{12 a_i^2}{\tau^3} - \frac{12 a_i b_i}{\tau^2}
  + \frac{4 b_i^2}{\tau}\right). \tag{6}
$$

Going from rest to rest ($v_0 = v_1 = 0$) over $\Delta p$ gives $a_i = \Delta p_i$, $b_i = 0$, so
$c(\tau) = \tau + 12\lVert\Delta p\rVert^2/\tau^3$, and
$\dot c = 1 - 36\lVert\Delta p\rVert^2/\tau^4 = 0$ gives
$\tau^\ast = (36\lVert\Delta p\rVert^2)^{1/4}$ with $c^\ast = \tfrac43\tau^\ast$. For
$\Delta p = (1,1)$, $\lVert\Delta p\rVert^2 = 2$, so $\tau^\ast = 72^{1/4}$ and
$c^\ast = \tfrac43 72^{1/4}$ — equation (4). **The relation $c^\ast = \tfrac43\tau^\ast$ is
tidy**: at the optimum the effort cost is exactly one third of the time cost (problem P2).

**Where the assumptions break**: (a) with an input bound $\lVert u\rVert \le u_{max}$, (2) is
**wrong** — the minimum-norm solution can violate the bound, and the constrained problem has no
closed form (the time-optimal solution becomes bang-bang, which is the starting point of the
Dubins and Reeds–Shepp classifications). The practical workaround is to raise $\tau$ to lower the
norm, which is how the time term of (1) acts as a **proxy for the bound**. (b) If $(A,B)$ is not
controllable, $G(\tau)$ is singular and has no inverse. The reachable set is a subspace, so states
outside it are unreachable **at any time** — note that this is **different** from the nonholonomic
phenomenon of "locally unreachable but globally reachable" (for a linear system, reachability does
not depend on time).

### R2 — why a cost sublevel set and not a ball

Carry the three requirements of RRT* (`c6-asymptotic-optimality` R1) over to differential
constraints.

**Requirement 1 (covering) survives unchanged.** Covering the neighbourhood of the optimal
trajectory is still needed; only "ball" is replaced by **a piece of the reachable set**.

**Requirement 2 (connection) breaks.** Most points in a Euclidean ball
$\lVert x' - x\rVert \le r$ **cannot be reached cheaply** from $x$. Take the double integrator: the
cost from $x = (0,0)$ (at rest) to $x' = (\epsilon, 0)$ (nearby position, at rest) is, by (4),
$c = \tfrac43(36\epsilon^2)^{1/4} \propto \epsilon^{1/2}$, whereas the cost to
$x'' = (0, \epsilon)$ (same position, different velocity) follows from (6) with $a = 0$,
$b = \epsilon$: $c = \tau + 4\epsilon^2/\tau$, minimized at $\tau = 2\epsilon$ with
$c = 4\epsilon$. So **at the same Euclidean distance $\epsilon$ the costs have different orders,
$\epsilon^{1/2}$ versus $\epsilon$.** A Euclidean ball is **anisotropic** with respect to the cost,
and that anisotropy grows without bound as $\epsilon \to 0$. Defining the neighbourhood as the
**sublevel set** $c(x',x) \le r_n$ is what makes requirements 1 and 2 mesh.

**Requirement 3 (cost) must also be rewritten.** The volume of the sublevel set
$\{x' : c(x_0,x') \le r\}$ is a power of $r$, but **the exponent is not $n$**. For the double
integrator the position directions spread as $r^2$ and the velocity directions as $r$ (the order
difference computed above), so the volume is of the form $r^{d_{\text{eff}}}$ with
$d_{\text{eff}} > n$. The $d$ of the radius rule $r_n = \gamma(\log n/n)^{1/d}$ must therefore be
**replaced by $d_{\text{eff}}$** for the expected neighbour count to be proportional to $\log n$.
The reproduction task takes the **conservative choice** $d_{\text{eff}} = 4$ (the state dimension)
and criterion 4 checks that this errs in the safe direction.

**Where the assumption breaks**: the cost $c$ is **not a metric** — it is not symmetric
($c(x,y) = c(y,x)$ fails) and the triangle inequality generally fails too. So the proof of
`c6-asymptotic-optimality` cannot be transcribed, and Karaman–Frazzoli 2010 add **weak local
controllability** and a local Lipschitz property of the cost as extra assumptions. When those hold
for a nonlinear system is an **open problem**.

### R3 — the closure condition of a state lattice

**Why a lattice.** Even when (A6) holds, expensive steering (solving a nonlinear optimal control
problem per edge) makes sampling slow. A lattice **precomputes steering and reuses it**: discretize
the state into a lattice $\Lambda$ and build, offline, a set $\mathcal{P}$ of trajectory pieces
(motion primitives) joining lattice points, so that planning reduces to the **graph search** of
`c6-search-based-planning`.

**The closure condition.** A trajectory built by concatenating primitives must stay on the lattice
**without error**. If a primitive's terminal state is off the lattice point by $\epsilon$, then
chaining $k$ of them **accumulates** $O(k\epsilon)$ of error and the result is no longer a
trajectory of the dynamics. Hence:

> every $\pi \in \mathcal{P}$ must start at a point of $\Lambda$ and end **exactly** at a point
> of $\Lambda$.

**The condition seen through a Dubins arc.** Consider a left arc of curvature radius $\rho$. At
heading $\theta$ the position changes as $\dot p = (\cos\theta, \sin\theta)$ while
$\dot\theta = 1/\rho$, so reparameterizing by $ds = \rho\,d\theta$,

$$
\Delta p = \int_{\theta_i}^{\theta_j} \rho\,(\cos\theta, \sin\theta)\,d\theta
  = \rho\big(\sin\theta_j - \sin\theta_i,\; \cos\theta_i - \cos\theta_j\big),
$$

which is (5). If the position lattice is $\mathbb{Z}^2$ (unit cells) then **both components of (5)
must be integers** for the primitive to exist. Two examples:

- $\theta_i = 0$, $\theta_j = \pi/2$: $\Delta p = \rho(1, 1)$ → only for $\rho \in \mathbb{Z}$.
- $\theta_i = 0$, $\theta_j = \arctan(3/4)$ (so $\sin\theta_j = 3/5$, $\cos\theta_j = 4/5$):
  $\Delta p = \rho(3/5,\ 1/5)$ → only when $\rho$ is a **multiple of 5**.

The latter is why **Pythagorean headings** are used: choosing headings with rational $\sin$ and
$\cos$, as in $(3,4,5)$ or $(5,12,13)$, lets the least common denominator be absorbed into $\rho$
and the lattice close. Using arbitrary equispaced headings ($2\pi/N_\theta$) makes (5) irrational and
the lattice **does not close**; implementations then "snap" the terminal state to a lattice point,
and at that instant the trajectory violates the dynamics — the most common correctness defect in
lattice planners.

**Where the assumption breaks**: achieving closure requires designing the heading set and $\rho$
together, so **the lattice resolution cannot be chosen freely**. Raising the resolution explodes the
number of primitives (roughly headings × reachable cells), and removing redundant primitives is the
"path set" problem of Pivtoraiko et al. And a lattice is only **resolution complete**, not complete —
a passage thinner than the lattice resolution is never seen.

## Proof sketch

### R2 — conditions for asymptotic optimality of kinodynamic RRT*

**Hypotheses** H1: (A6) — for any two states the **exact** optimal steering and its cost are
computable. H2: the cost $c(x,x')$ is locally Lipschitz and the optimal trajectory has positive
"dynamic clearance" (every state in a $\delta$-tube around it is free). H3: the neighbour set is the
cost sublevel set $N(x) = \{x' : c(x',x) \le r_n\}$ with
$r_n = \gamma(\log n/n)^{1/d_{\text{eff}}}$ and $\gamma$ large enough. H4: rewiring uses the
**exact** steering of (A6) and propagates costs to the subtree.
**Conclusion** C: the algorithm is asymptotically optimal.

**Strategy**: restate the three requirements of R1 of `c6-asymptotic-optimality` **in cost space**.
Replacing every place that used Euclidean structure by a cost sublevel set is the whole proof.

1. **Make the cover out of cost.** Cut the optimal trajectory $\sigma^\ast$ at cost spacing $r_n/2$
   into states $x_0^\ast, \dots, x_m^\ast$ and use the **cost balls**
   $\{x : c(x_i^\ast, x) \le r_n/4\}$ as the cover. H2 guarantees those balls lie in the free space.
2. **The probability a sample lands in a cost ball.** Its Lebesgue measure is
   $\Theta(r_n^{d_{\text{eff}}})$, so $p_n = \Theta(r_n^{d_{\text{eff}}}/\mu)$. That
   $d_{\text{eff}}$ is **set by the dynamics rather than being the state dimension** is the only
   difference from the geometric case.
3. **Connection.** The triangle inequality is unavailable (the cost is not a metric), so the
   Lipschitz property of H2 is used to get
   $c(y_i, y_{i+1}) \le c(x_i^\ast, x_{i+1}^\ast) + L(\,\cdot\,) \le r_n$.
   (Omitted: tracking the constant factors through the Lipschitz constant — the lemma of
   [Karaman & Frazzoli 2010](https://doi.org/10.1109/CDC.2010.5717430).)
4. **Summability and Borel–Cantelli.** Choosing $\gamma$ so that $np_n \propto \log n$ in 2 and 3,
   **the same computation** as requirement 1 of the previous lesson's R1 makes the failure
   probability summable and yields almost sure convergence.
5. **Correctness of rewiring.** Without H4 (approximate steering) rewiring inserts **a trajectory
   that does not exist** into the tree. The cost is then underestimated and the solution reported is
   infeasible — **validity** breaks before asymptotic optimality does.

**Removing a hypothesis**: drop H1 (a nonlinear system) and step 5 collapses, so the RRT* structure
cannot be used at all — one must go to the forward propagation of R4. Replace the "sublevel set" of
H3 by a Euclidean ball and connection fails at step 3 (the $\epsilon^{1/2}$ versus $\epsilon$ order
difference of derivation R2 is the cause). Drop the dynamic clearance of H2 and the cover of step 1
cannot be placed inside the free space.

## Problem set

Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Verify directly from the definition of the inner product that the
adjoint of $\mathcal{L}_\tau$ is
$(\mathcal{L}_\tau^\ast\lambda)(t) = R^{-1}B^\top e^{A^\top(\tau-t)}\lambda$, and derive
$\mathcal{L}_\tau\mathcal{L}_\tau^\ast = G(\tau)$.
*Solution sketch*: move $\langle \mathcal{L}_\tau u, \lambda\rangle = \lambda^\top\int_0^\tau
e^{A(\tau-s)}Bu(s)ds$ inside the integral and match the form $\langle u, w\rangle_R$. The
substitution $\sigma = \tau - s$ produces the standard form of the Gramian.

**P2 (derivation, ★★, R1)** Show that $c^\ast = \tfrac43\tau^\ast$ for rest-to-rest steering of the
double integrator, and confirm that **at the optimum the ratio of effort cost to time cost is always
1:3**. Explain why that ratio is independent of the displacement.
*Solution sketch*: from $c(\tau) = \tau + K/\tau^3$, $\dot c = 0$ gives $K = \tau^4/3$ and
$c^\ast = \tau^\ast + \tau^\ast/3$. The independence follows because $c$ is of **homogeneous form**
in $\tau$ and the displacement enters only through $K$.

**P3 (numerical, ★, R1)** For the double integrator with $x_0 = (0,0,0,0)$, $x_1 = (1,1,0,0)$ and
$R = I$, find $\tau^\ast$ and $c^\ast$, and the costs at $\tau = 2$ and $\tau = 3$.
*Answer*: $c(\tau) = \tau + 24/\tau^3$, so $\tau^\ast = 72^{1/4} = 2.912950630244$ and
$c^\ast = \tfrac43 72^{1/4} = 3.883934173659$; $c(2) = 2 + 3 = 5$ exactly and
$c(3) = 3 + 24/27 = 3.888888889$. Tolerance $10^{-9}$.
Check: $\dot c(\tau) = 1 - 72/\tau^4$ vanishes at $\tau^\ast$, and substituting
$\lambda = (12/\tau^3, 12/\tau^3, -6/\tau^2, -6/\tau^2)$ with $Ax_1 = 0$ into the general form (3)
gives $1 - \lVert B^\top\lambda\rVert^2 = 1 - 72/\tau^4$, the same expression.

**P4 (numerical, ★, R3)** With curvature radius $\rho$ and the position lattice $\mathbb{Z}^2$, find
the smallest $\rho$ for which a left arc from $\theta_i = 0$ to $\theta_j$ closes the lattice:
(i) $\theta_j = \pi/2$, (ii) $\sin\theta_j = 3/5$, (iii) $\sin\theta_j = 5/13$.
*Answer*: from (5), $\Delta p = \rho(\sin\theta_j,\ 1-\cos\theta_j)$.
(i) $\rho(1,1)$ → $\rho_{\min} = 1$. (ii) $\cos\theta_j = 4/5$, so $\rho(3/5,\ 1/5)$, denominator 5
→ $\rho_{\min} = 5$. (iii) $\cos\theta_j = 12/13$, so $\rho(5/13,\ 1/13)$ → $\rho_{\min} = 13$.
So **finer headings force a larger minimum radius** — the trade-off between resolution and
curvature. Tolerance: exact integers.

**P5 (counterexample, ★★, R2)** Show with concrete numbers that "using Euclidean balls as
neighbourhoods breaks asymptotic optimality" for the double integrator: from $x = (0,0,0,0)$, compute
the steering cost to the two states at Euclidean distance $\epsilon = 10^{-2}$,
$x' = (\epsilon, 0, 0, 0)$ and $x'' = (0,0,\epsilon,0)$, and take their ratio. What happens to that
ratio as $\epsilon \to 0$?
*Property checklist*: $c(x,x') = \tfrac43(36\epsilon^2)^{1/4} = \tfrac43\sqrt{6\epsilon}$ and
$c(x,x'') = 4\epsilon$. At $\epsilon = 10^{-2}$ these are $0.3266$ and $0.04$ — a factor **8.2**.
The ratio $\propto \epsilon^{-1/2} \to \infty$. Write down that the cost becomes unboundedly
anisotropic inside a Euclidean ball.

**P6 (proof, ★★, R3)** Show that snapping a primitive's terminal state to a lattice point
accumulates $O(k\epsilon)$ of state error over $k$ concatenations, and state explicitly that the
result does not satisfy the dynamics. Also write the limitation of absorbing that error with feedback
control.
*Strategy*: snapping inserts a jump of $\epsilon$ into the state, and a jump is not a solution of
$\dot x = f(x,u)$. Write the accumulation as propagation from a wrong initial state for each piece
(for a linear system $e^{A\tau}$ is the amplification factor). Feedback reduces the **tracking**
error, but the cost evaluation at planning time is already wrong, so optimality is lost.

**P7 (proof, ★★★, R2)** Complete step 3 (connection) of R2 using only the Lipschitz property of the
cost: with $c(x_i^\ast, x) \le r_n/4$, $c(x_{i+1}^\ast, y) \le r_n/4$ and
$c(x_i^\ast, x_{i+1}^\ast) \le r_n/2$, find a constant $C$ with $c(x, y) \le C\,r_n$ (the crux being
that the triangle inequality is unavailable because the cost is not a metric).
*Strategy*: construct explicitly a **feasible** control that concatenates the three trajectories and
use its cost as the upper bound (the optimal cost is below it). The concatenation requires the
intermediate states to match exactly, which is where exactness of the steering (H1) is used.

**P8 (implementation, ★★, R1·R2)** Write the kinodynamic RRT* of the reproduction task.
Requirements: neighbours defined by the cost (6), steering taken as the minimum over a fixed $\tau$
grid, collision checking by sampling the cubic Hermite trajectory, rewiring with subtree cost
propagation.
*Rubric*: (a) the numbers of criteria 1 and 2 match; (b) every solution cost is at least the
free-space lower bound; (c) you show numerically that switching the neighbourhood to a Euclidean ball
makes the cost worse (confirming P5); (d) you show that removing the subtree propagation stops the
convergence.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions.

1. **Webb & van den Berg, "Kinodynamic RRT*" (2013, ICRA)** — role: `standard`.
   <https://arxiv.org/abs/1205.5088>
   *Why read it*: (2) and (3) of R1 come from here; look in particular at the section optimizing
   $\tau$ — it is the same equation as (3) in this lesson.
   Extra questions: (a) how do the authors handle input bounds (or not)? (b) is their definition of
   the neighbour set the same as (b) of R2 here? (c) what exponent do they use in the radius rule?
2. **Karaman & Frazzoli, "Optimal kinodynamic motion planning using incremental sampling-based
   methods" (2010, CDC)** — role: `seminal`.
   <https://doi.org/10.1109/CDC.2010.5717430>
   *Why read it*: hypotheses H2 and H3 of R2 are formalized here. The point is to establish exactly
   what "weak local controllability" demands.
   Extra questions: (a) is the double integrator covered by the paper's assumptions? A car model?
   (b) state in one sentence each what the authors do and do not prove.
3. **Pivtoraiko, Knepper & Kelly, "Differentially constrained mobile robot motion planning in state
   lattices" (2009, JFR)** — role: `standard`. <https://doi.org/10.1002/rob.20285>
   *Why read it*: the source of R3. Lattice design (choosing the heading set and the radius jointly)
   and removing redundancy from the path set are the paper's two contributions.
   Extra questions: (a) how does their lattice satisfy the integrality condition of (5)? (b) how do
   they measure the trade-off between the number of primitives and planning quality? (c) where does
   the paper state the difference between "resolution complete" and "complete"?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation or one figure. (4) what is guaranteed theoretically,
and **what is not**? (5) the independent and dependent variables and the baselines, and were the
baselines tuned fairly? (6) does the metric match the claim, and are variance and seeds reported?
(7) what is missing for reproduction? (8) if the result were wrong, which assumption would you doubt
first? (9) computational and memory complexity, and real-time feasibility. (10) what would you change
to go beyond this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 30 minutes for 30 seeds ×
$n = 3000$, under 1 GB of memory. numpy only.

**Input data (given by the lesson).** A two-dimensional **double integrator**: state
$x = (p_1,p_2,v_1,v_2)$ with $\dot p = v$, $\dot v = u$, and the cost (1) with $R = I$. Positions are
confined to $[0,1]^2$ and velocities to $[-2,2]^2$. $x_{start} = (0,0,0,0)$,
$x_{goal} = (1,1,0,0)$. The obstacle is the rectangle $[0.40,\ 0.60] \times [0.00,\ 0.65]$ in
**position space**, with a blocked interior.

Fixed settings: samples are uniform on $[0,1]^2$ in position and $[-2,2]^2$ in velocity, with samples
inside the obstacle discarded. Steering time is taken as the minimum of (6) over the **fixed grid**
$\tau \in \{0.1\,e^{k\ln(80)/23} : k = 0,\dots,23\}$ (24 log-spaced points in $[0.1, 8]$), making the
result fully deterministic. The radius is $r_n = 4.0\,(\log n/n)^{1/4}$, parent candidates are the 25
cheapest, and collision checking samples the cubic Hermite trajectory at 16 points. Seeds
$0,\dots,29$; checkpoints $n \in \{500, 1000, 2000, 3000\}$.

**Acceptance criteria — all four must hold.**

1. **The analytic lower bound (checking R1)** — the free-space optimal steering cost,
   **ignoring** the obstacle, matches
   $$c_{lb} = \tfrac43\,72^{1/4} = 3.883934173659, \qquad \tau^\ast = 72^{1/4} = 2.912950630244$$
   to a relative error of $10^{-9}$, and $|\dot c(\tau^\ast)|$ computed from the general form (3) is
   below $10^{-9}$. **Every solution cost at every seed and checkpoint is at least $c_{lb}$** (zero
   violations).
2. **Convergence (checking R2)** — all 30 seeds find a solution at all four checkpoints (30/30) and
   the median cost matches

   | $n$ | 500 | 1000 | 2000 | 3000 |
   |---|---|---|---|---|
   | median | 4.9967 | 4.6841 | 4.4782 | 4.4417 |
   | median/$c_{lb}$ | 1.2865 | 1.2060 | 1.1530 | 1.1436 |

   to an absolute error of 0.05, decreasing **monotonically**. The minimum over the 30 seeds is
   $4.1561 \pm 0.02$ and **does not change** across the four checkpoints (the estimate of the
   obstacle-constrained optimum).
3. **Convergence within 1.1×** — at $n = 3000$ the ratio of the median to the minimum is
   $4.4417/4.1561 = 1.0687 \le 1.10$, and that ratio decreases monotonically across the four
   checkpoints (measured 1.2023, 1.1270, 1.0775, 1.0687). So it **converges to within 1.1 times the
   estimated optimum**.
4. **The Euclidean-neighbour control (checking (b) of R2)** — rerun the same setup with the
   neighbour set replaced by a **Euclidean ball** ($\lVert x' - x\rVert \le r_n$) and report that the
   median at $n = 3000$ gets **worse**. Also compute the two costs of P5,
   $\tfrac43\sqrt{6\epsilon}$ and $4\epsilon$, at $\epsilon = 10^{-2}$, obtaining $0.3266$ and
   $0.0400$ (a ratio of 8.165).

**Baselines.** (a) The analytic free-space bound $c_{lb}$ — criterion 1. (b) The 30-seed minimum —
criteria 2 and 3. (c) Variants of itself (Euclidean neighbours; rewiring without propagation) —
criterion 4 and the rubric of P8.

**Failure table**

| Symptom | Cause | How to check |
|---|---|---|
| a cost below $c_{lb}$ | the trajectory was treated as a straight line for collision and cost (ignoring the dynamics) | re-integrate each leg of the best solution as a cubic Hermite and check the terminal states agree |
| some seeds find no solution | the velocity range was sampled too narrowly, or the upper end of the $\tau$ grid is too small | lower the $\tau$ grid's upper end from 8 to 2 and see whether the success rate falls |
| the median rises across checkpoints | subtree costs were not propagated after rewiring | print the number of rewirings and of propagated nodes |
| the median barely decreases | neighbours were defined by a Euclidean ball (the broken version of criterion 4) | print the mean neighbour-set size and the fraction of them that connect |
| the run exceeds 30 minutes | the cost was computed in a Python loop over the $\tau$ grid | vectorize (6) over the (node, $\tau$, axis) axes |
| a solution with a collision passes | fewer than 16 Hermite samples, or the velocity limits were not checked | raise the sample count to 64 and see whether the cost rises |

## Open problems

- **(open problem) Steering for nonlinear systems** — (A6) holds in closed form only for linear
  systems. For a general nonlinear system the optimal steering between two states is itself a
  non-convex optimal control problem, and solving one per planner edge is incompatible with real
  time. Current approaches: give up steering and propagate forward, as in
  [SST](https://arxiv.org/abs/1407.2896); fold the cost into the state to turn the problem into a
  feasibility problem ([Hauser & Zhou 2016](https://doi.org/10.1109/tro.2016.2602363)); local
  linearization plus iLQR (`c4-ilqr-ddp`). What is missing: a steering approximation with bounded
  per-edge cost that keeps the optimality guarantee.
- **(open problem) Closed-form optimal steering under input bounds** — (2) is wrong under
  $\lVert u\rVert \le u_{max}$. The time-optimal solution is bang-bang and a **classification** is
  possible, as for Dubins and Reeds–Shepp, but for a composite cost like (1) with bounds there is
  neither a classification nor a closed form. Current approaches: the classical classifications of
  [Dubins 1957](https://doi.org/10.2307/2372560) and
  [Reeds & Shepp 1990](https://doi.org/10.2140/pjm.1990.145.367), and numerical optimal control.
  What is missing: a way to solve the constrained composite-cost steering at planner speed.
- **(open problem) Determining the effective dimension $d_{\text{eff}}$** — the radius rule of R2
  requires the exponent $d_{\text{eff}}$ of the reachable-set volume, but there is no method to
  compute it for general dynamics. Practice takes the **conservative choice** of the state dimension
  (as does the reproduction task) and ends up with more neighbours than necessary. Current approach:
  case analysis via the Kalman index for linear systems
  ([Karaman & Frazzoli 2010](https://doi.org/10.1109/CDC.2010.5717430)). What is missing: a procedure
  for estimating $d_{\text{eff}}$ on a nonlinear system.

## Concept check

Run `rc quiz c6-kinodynamic-planning`. Concept checking only; the real work is the problem set and
the reproduction task.

The six items cover: why linear steering is closed-form; the relation $c^\ast = \tfrac43\tau^\ast$ at
the optimum; what breaks if neighbours are Euclidean balls; why an arbitrary heading set cannot close
a lattice; which parts of the RRT* argument survive differential constraints; and the structure used
when steering is unavailable.

## How to study this stage

1. **Write down the assumption that breaks (20 min)** — list what changes once (A2) is gone: the
   definition of a neighbourhood, the symmetry of the cost, the exponent of the radius rule, the
   validity of rewiring. Those four lines are the structure of the lesson.
2. **Reduce steering to linear algebra (70 min)** — rewrite R1 from a blank page. The crux is the
   single line "the terminal state is a **linear** function of the control"; the rest is a
   minimum-norm solution. Solving P1 alongside, and checking the adjoint by hand, fixes in memory
   that the Gramian is $\mathcal{L}\mathcal{L}^\ast$.
3. **Turn the closed form into numbers (40 min)** — do P2 and P3. Obtain $\tau^\ast = 72^{1/4}$ and
   $c^\ast = \tfrac43\tau^\ast$ yourself and confirm the general form (3) gives the same value.
   **Only after seeing the general form and the closed form agree do you believe (3).**
4. **Meet the anisotropy numerically (30 min)** — do P5. Computing that the costs differ by a factor
   8.2 at the same Euclidean distance $10^{-2}$ shows that (b) of R2 is not a design choice but a
   **necessity**.
5. **Design a lattice (40 min)** — do P4. Seeing the minimum closing radius grow 1 → 5 → 13 as the
   headings get finer settles why lattice planners insist on particular heading sets.
6. **Implement it, and the broken version too (95 min)** — the reproduction task. After hitting
   criteria 1, 2 and 3, **deliberately** run criterion 4 (Euclidean neighbours) and confirm it gets
   worse. Do the no-propagation experiment at the same time.
7. **Three papers (130 min)** — Webb–van den Berg (steering) → Karaman–Frazzoli 2010 (assumptions) →
   Pivtoraiko (lattices). The first two are the "solution" and the "conditions" of the same problem;
   the third is the route that **avoids** the problem. Record that framing in your notes.

**Passing bar**: you can derive R1 by the linear-algebra reduction from a blank page, obtain
$\tau^\ast = 72^{1/4}$ and $c^\ast = \tfrac43\tau^\ast$ by hand, say numerically why a Euclidean ball
cannot be used, have code satisfying the four criteria of the reproduction task (especially the
control experiment of criterion 4), and explain the lattice closure condition through a Dubins arc.
You have notes on all three papers.
