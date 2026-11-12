---
id: s2-planning-through-contact
lang: en
title: Planning and control through contact
summary: >-
  Two ways of planning with contact as a **decision variable**, carried through to numbers. First,
  relax the complementarity constraint by $\varepsilon$ and derive in closed form **how far the body
  floats**: the gap is $h^2\varepsilon/\lvert f\rvert$ and the force bias is
  $\varepsilon/\lvert f\rvert$, and at a resting contact the gap becomes $\varepsilon/g$,
  **independent of the time step**, while the force bias $\varepsilon/(h^2 g)$ **blows up**. Second,
  build a real-time splitting (ADMM) on the fact that projection onto the complementarity set is
  closed form, and watch by measurement that the iteration carries **no guarantee** on a nonconvex
  set — a fixed penalty converges to a feasible but **do-nothing** fixed point at 2.443 times the
  optimum, while a growing penalty schedule finishes the task at 1.132 times. Finally prove the
  convex hull theorem of disjunctive programming and confirm numerically why per-step convexification
  is not the hull of the trajectory set.
objectives:
  - Derive the gap and force bias of a relaxed complementarity step and explain the $\varepsilon \propto h^2$ rule.
  - Write the projection onto the complementarity set in closed form and say why it makes a real-time splitting possible.
  - Show numerically that the fixed points of nonconvex ADMM trade feasibility against optimality.
  - Prove the convex hull theorem of disjunctive programming and derive that a complementarity pair's hull is a triangle.
  - Measure how the per-step relaxation gap depends on the force bound and explain the motivation for GCS.
  - Implement contact-implicit MPC on a reduced-scale planar pushing task inside a real-time budget.
tags: [manipulation, contact-implicit, mpc, complementarity, convex-relaxation, gcs, research]
---

# Planning and control through contact

## Setup and notation

This lesson assumes `s2-contact-modes-dexterity` and `c6-combinatorial-gcs`. The earlier lessons
already showed that contact **modes** are a combinatorial object and why enumerating them grows
exponentially. This lesson pushes that combinatorial structure **into the optimization**, along two
routes — complementarity constraints and graphs of convex sets — and carries both to numbers.

Also assumed:

- The **statement** of a linear complementarity problem (LCP): that
  $0 \le \varphi \perp \lambda \ge 0$ abbreviates $\varphi \ge 0$, $\lambda \ge 0$,
  $\varphi^\top\lambda = 0$. Existence and uniqueness theorems are not used.
- Basic convex analysis: convex hulls, uniqueness of projection onto a convex set, polyhedra.
- Only the **shape** of ADMM (three steps: the $z$-step, the projection step, the dual update). The
  convergence theorems are for **convex** problems and do not apply to this lesson's problem — that
  is the point of R2.

Notation:

| Symbol | Meaning |
|---|---|
| $\varphi \ge 0$ | gap function; $0$ at contact |
| $\lambda \ge 0$ | normal contact impulse or force |
| $h$ | time step |
| $f$ | next position under **free motion** (no contact force) |
| $\varepsilon$ | complementarity relaxation parameter |
| $S$ | the complementarity set $\{(a,b) \ge 0 : ab = 0\}$ |
| $\Lambda, \Phi$ | upper bounds (a box) on force and gap |
| $X_i,\, y_i$ | mode $i$'s convex set and its indicator variable |
| $\rho$ | the ADMM penalty |
| $N$ | the MPC horizon |
| $J^\ast$ | the optimal cost obtained by enumerating modes |
| $s, p, u$ | slider position, jaw centre, jaw velocity |

**The model used here.** A reduced-scale planar push along one axis. Parallel jaws of fixed span
$2d$ sit at centre $p$ and the slider is at $s$ between them. The slider is quasi-static and viscous,
so it moves in proportion to the contact force:

$$
s_{k+1} = s_k + \frac{h}{b}\,(\lambda_{1,k} - \lambda_{2,k}), \qquad
p_{k+1} = p_k + h\,u_k,
$$

$$
\varphi_{1,k} = s_{k+1} - p_{k+1} + d \;\ge\; 0 \;\perp\; \lambda_{1,k} \ge 0, \qquad
\varphi_{2,k} = p_{k+1} + d - s_{k+1} \;\ge\; 0 \;\perp\; \lambda_{2,k} \ge 0 .
$$

Since $\varphi_1 + \varphi_2 = 2d$ is an **identity**, the two plates can never touch at once — each
step has three modes: left-plate contact, right-plate contact, or no contact. The numbers are
$h = 0.05$ s, $b = 1$, $d = 0.10$ m, $u \in [-2, 2]$, $\lambda \in [0, 20]$, cost
$\sum_k (s_k - s^\ast)^2 + 10^{-3}\sum_k u_k^2$, target $s^\ast = 0.06$ m, horizon $N = 6$.

Two assumptions, stated:

- **(A1) Normal contact only** — there is no friction in this model. Friction cones and the mode
  branching they cause belong to `s2-grasp-mechanics` and `s2-contact-modes-dexterity`; the
  nonconvexity treated here appears **in full** with normal complementarity alone.
- **(A2) Semi-implicit time discretization** — velocities and positions are evaluated one step ahead,
  as above (Stewart & Trinkle 1996, registry id `stewart1996-implicit-timestepping`). It is written
  at the impulse level, so the restitution coefficient is zero.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof).

- **R1 (the relaxation floats the body) [D2]** — relaxing one step's complementarity to
  $\varphi\lambda = \varepsilon$ gives a closed-form solution, and at a contact step where free
  motion penetrates by $\lvert f\rvert$,
  $$
  \varphi^+ = \frac{h^2\varepsilon}{\lvert f\rvert} + O(\varepsilon^2), \qquad
  \lambda - \lambda^{\text{exact}} = \frac{\varepsilon}{\lvert f\rvert} + O(\varepsilon^2) .
  \tag{1}
  $$
  The body therefore **takes force without touching** (force at a distance). The measured ratio
  $\varphi^+ \big/ (h^2\varepsilon/\lvert f\rvert)$ is $0.96157$ at $\varepsilon = 10^{-2}$ and
  $1.00000$ at $\varepsilon \le 10^{-6}$. At a **resting contact** $\lvert f\rvert = h^2 g$, so
  $$
  \varphi^+ = \frac{\varepsilon}{g}\ \ (\text{independent of the time step}), \qquad
  \Delta\lambda = \frac{\varepsilon}{h^2 g}\ \ (\text{diverges as } h \to 0) .
  \tag{2}
  $$
  So **do not shrink $h$ at fixed $\varepsilon$** — $\varepsilon$ must shrink in proportion to $h^2$
  for the force bias to stay bounded.
- **R2 (closed-form projection and real-time splitting) [D2]** —
  $S = \{(a,b) \ge 0 : ab = 0\}$ is a union of two rays, and projection onto it is an **$O(1)$
  closed form** that compares two distances:
  $$
  \Pi_S(x,y) = \begin{cases}
    (\max(x,0),\, 0) & \min(x,0)^2 + y^2 \le x^2 + \min(y,0)^2,\\[2pt]
    (0,\, \max(y,0)) & \text{otherwise.}
  \end{cases}
  \tag{3}
  $$
  That single fact makes one ADMM iteration a **back-substitution through a pre-factorized matrix
  plus one (3) per contact**: measured at $0.0229$ ms per iteration ($N = 4$) rising to $0.0630$ ms
  ($N = 24$), with a 240-iteration solve taking $6.43$ ms on average (max $8.19$ ms) inside a
  $50$ ms budget. **However**, the set is nonconvex and there is no convergence guarantee: a fixed
  $\rho = 1$ reaches a **feasible** fixed point with residual $1.7\times10^{-12}$ whose cost is
  $2.443$ times $J^\ast$ and whose $u_0 = 0$ — a **do-nothing** plan. Growing $\rho$ from $0.1$ to
  $30$ gives $1.132\,J^\ast$ with residual $7.8\times10^{-3}$ and finishes the task. Feasibility and
  optimality are traded **directly through the penalty schedule**.
- **R3 (the convex hull of a disjunction) [D3]** — for nonempty bounded convex sets
  $X_1,\dots,X_m \subset \mathbb{R}^n$,
  $$
  \operatorname{conv}\Big(\bigcup_{i=1}^m X_i\Big)
  = \Big\{ \sum_{i=1}^m x_i \;:\; x_i \in y_i X_i,\ \sum_i y_i = 1,\ y_i \ge 0 \Big\},
  \tag{4}
  $$
  where $yX = \{yx : x \in X\}$ for $y > 0$ and $0\cdot X = \{0\}$. This is the **perspective
  lifting** behind GCS, and it says the relaxation is **exact set by set** when every mode is given
  a convex set ([Marcucci, Umenberger, Parrilo, Tedrake 2024](https://arxiv.org/abs/2101.11565)).
- **R4 (a complementarity pair's hull is a triangle, and the relaxation is tied to the bound) [D2]** —
  as a corollary of (4), the hull of the complementarity set on a box
  $S_{\square} = \{(a,b) \in [0,\Lambda]\times[0,\Phi] : ab = 0\}$ is
  $$
  \operatorname{conv}(S_{\square})
  = \Big\{ (a,b) \ge 0 \;:\; \frac{a}{\Lambda} + \frac{b}{\Phi} \le 1 \Big\},
  \tag{5}
  $$
  a **triangle**, exactly half the area of the box (with $n$ pairs, $2^{-n}$: $0.0156$ at $n = 6$).
  Yet the lower bound this per-step hull gives is measured at $0$ when $\Lambda = 20$ (a $100\%$
  gap), and even tightening the bound to the smallest value that still contains the optimizer,
  $\Lambda = 1.06$, only reaches $0.00154435$ (an $82.534\%$ gap). **The intersection of per-step
  hulls is not the hull of the trajectory set** — the remaining gap comes not from geometry but from
  **sequencing**. That is exactly why GCS puts a **whole mode** in one convex set and applies (4) at
  the level of the graph.

## Derivation

### R1 — the $\varepsilon$ relaxation floats the body

**Setup.** Take one step of one degree of freedom with one contact. Writing the next position
without contact force as $f$ (free motion), the next position with contact force $\lambda$ is

$$
\varphi^+ = f + h^2\lambda
$$

(unit mass, semi-implicit integration). The exact problem is $0 \le \varphi^+ \perp \lambda \ge 0$
and the solution comes in two cases:

- if $f \ge 0$, then $\lambda = 0$ and $\varphi^+ = f$ (no contact);
- if $f < 0$, then $\varphi^+ = 0$ and $\lambda^{\text{exact}} = -f/h^2 > 0$ (contact).

**Relaxation.** What interior-point, penalty and smoothing methods all do is replace
$\varphi^+\lambda = 0$ with $\varphi^+\lambda = \varepsilon > 0$
([Scholtes 2001](https://doi.org/10.1137/S1052623499361233)). Substituting at a contact step
($f < 0$) gives a quadratic in $\lambda$:

$$
(f + h^2\lambda)\lambda = \varepsilon
\quad\Longleftrightarrow\quad
h^2\lambda^2 + f\lambda - \varepsilon = 0 .
$$

There is exactly one root with $\lambda > 0$:

$$
\lambda(\varepsilon) = \frac{-f + \sqrt{f^2 + 4h^2\varepsilon}}{2h^2},
\qquad
\varphi^+(\varepsilon) = f + h^2\lambda = \frac{f + \sqrt{f^2 + 4h^2\varepsilon}}{2} .
\tag{6}
$$

**Expansion.** Since $f < 0$ we have $\lvert f\rvert = -f$ and
$\sqrt{f^2 + 4h^2\varepsilon} = \lvert f\rvert\sqrt{1 + 4h^2\varepsilon/f^2}
= \lvert f\rvert + 2h^2\varepsilon/\lvert f\rvert + O(\varepsilon^2)$. Putting that into (6),

$$
\varphi^+ = \frac{f + \lvert f\rvert + 2h^2\varepsilon/\lvert f\rvert}{2} + O(\varepsilon^2)
          = \frac{h^2\varepsilon}{\lvert f\rvert} + O(\varepsilon^2),
\qquad
\lambda - \frac{\lvert f\rvert}{h^2} = \frac{\varepsilon}{\lvert f\rvert} + O(\varepsilon^2),
$$

which is (1). The two biases shrink at **the same rate** — that is why the two ratio columns of the
measured table agree to five decimals ($0.96157$, $0.99588$, $0.99958$, $1.00000$, $1.00000$).

**The resting-contact specialization.** For a body simply at rest, one step of free fall gives
$\lvert f\rvert = h^2 g$. Substituting into (1) yields (2):

$$
\varphi^+ = \frac{h^2\varepsilon}{h^2 g} = \frac{\varepsilon}{g},
\qquad
\Delta\lambda = \frac{\varepsilon}{h^2 g} .
$$

**Failure mode.** The gap stays at $\varepsilon/g$ regardless of $h$ ($1.019\times10^{-5}$ m at
$\varepsilon = 10^{-4}$, $g = 9.81$ — measured $1.018945\times10^{-5}$), while the force bias is
divided by $h^2$ and **grows**. So the intuition "refine $h$ to get accuracy" breaks here: integrate
more finely while leaving $\varepsilon$ alone and the contact force is wrong by $h^{-2}$. The
correct coupling is $\varepsilon \propto h^2$, which becomes the practical rule that in real-time
MPC **$h$ and $\varepsilon$ must not be tuned separately**.

### R2 — closed-form projection and real-time splitting

**Projection.** $S = R_a \cup R_b$ is the union of two rays $R_a = \{(t,0) : t \ge 0\}$ and
$R_b = \{(0,t) : t \ge 0\}$. Each is convex, so projection onto it is unique and closed form:
$\Pi_{R_a}(x,y) = (\max(x,0), 0)$ and $\Pi_{R_b}(x,y) = (0, \max(y,0))$. Projection onto the union
is **whichever of the two is nearer**, and since the squared distances are

$$
\operatorname{dist}(x,y;R_a)^2 = \min(x,0)^2 + y^2, \qquad
\operatorname{dist}(x,y;R_b)^2 = x^2 + \min(y,0)^2,
$$

one comparison settles it — that is (3). Because the union is nonconvex the projection **need not be
unique** (on the diagonal where the two distances tie), but either choice is a projection.

**Splitting.** Collect the decision variables (jaw velocities and contact forces) into $z$ and write
the complementarity pairs as $x = Mz + m$; the problem is

$$
\min_z \; z^\top Q z + q^\top z \quad \text{s.t.} \quad x = Mz + m \in S^{2N} .
$$

Splitting the constraint off onto a **copy** $w$ gives the three ADMM steps

$$
z \leftarrow \arg\min_z \Big\{ z^\top Qz + q^\top z
  + \frac{\rho}{2}\lVert Mz + m - w + y\rVert^2 \Big\},
\qquad
w \leftarrow \Pi_{S^{2N}}(Mz + m + y),
\qquad
y \leftarrow y + (Mz + m) - w .
$$

**Why this is real time.** The $z$-step is an unconstrained strongly convex quadratic, so it is one
normal equation

$$
(2Q + \rho M^\top M)\,z = -q - \rho M^\top (m - w + y)
\tag{7}
$$

whose left-hand matrix is **constant** once $\rho$ is fixed. Factor it once with Cholesky and every
iteration is a **back-substitution**. The $w$-step is one (3) per contact — **linear** in the number
of contacts and the horizon. Measured, the per-iteration time grows almost linearly in $N$
($0.0229 \to 0.0630$ ms for $N: 4 \to 24$) and a 240-iteration solve averages $6.43$ ms, which is
$13\%$ of a $50$ ms budget. That is the **whole** reason the consensus complementarity control of
[Aydinoglu & Posa 2021](https://arxiv.org/abs/2109.07076) and
[Aydinoglu et al. 2024](https://doi.org/10.1109/TRO.2024.3435423) runs in real time.

**Failure mode (measured).** The convergence theorems for convex ADMM do not apply because $S$ is
nonconvex, and the measurements show it plainly. On the same problem ($s = p = 0$, $N = 6$,
enumerated optimum $J^\ast = 0.00884227$), after 240 iterations:

| Penalty | $J$ | $J/J^\ast$ | complementarity residual | $u_0$ |
|---|---|---|---|---|
| $\rho = 1$ fixed | $0.02160000$ | $2.443$ | $1.7\times10^{-12}$ | $0.0000$ |
| $\rho: 0.1 \to 30$ | $0.01000814$ | $1.132$ | $7.8\times10^{-3}$ | $+1.6456$ |

The fixed-penalty fixed point satisfies complementarity **to machine precision** while costing 2.4
times the optimum, with a first input of $0$ — run it in closed loop for 80 steps and the slider
**never moves** ($|s - s^\ast| = 6.0\times10^{-2}$ m throughout). The growing schedule leaves a
residual of $7.8\times10^{-3}$ and in exchange reaches the target **exactly** ($s = 0.06000$,
$|s - s^\ast| = 0$). The computation time is effectively the same either way (mean $6.42$ versus
$6.43$ ms).

So what this method buys is "**some** feasible plan in real time"; a **good** plan in real time is
decided by the penalty schedule and the initialization. Global optimality remains open
([Venkatesh et al. 2025](https://doi.org/10.1109/LRA.2025.3615030)).

### R3 — the convex hull of a disjunction

**Theorem.** If $X_1,\dots,X_m \subset \mathbb{R}^n$ are nonempty bounded convex sets, (4) holds.

**Proof ($\supseteq$).** Take a point $x = \sum_i x_i$ of the right-hand side and let
$I = \{i : y_i > 0\}$. For $i \in I$, $x_i \in y_i X_i$ gives $x_i / y_i \in X_i$. For
$i \notin I$, $x_i \in 0\cdot X_i = \{0\}$, so $x_i = 0$ and contributes nothing. Hence

$$
x = \sum_{i \in I} y_i \cdot \frac{x_i}{y_i}, \qquad \sum_{i \in I} y_i = 1, \quad y_i > 0,
$$

is a convex combination of points of $\bigcup_i X_i$, so $x \in \operatorname{conv}(\bigcup_i X_i)$.

**Proof ($\subseteq$).** If $x \in \operatorname{conv}(\bigcup_i X_i)$ there is a finite convex
combination $x = \sum_{j=1}^J \theta_j z_j$ with $\theta_j > 0$, $\sum_j \theta_j = 1$ and
$z_j \in X_{i(j)}$. Grouping by $i$, set

$$
y_i = \sum_{j:\, i(j) = i} \theta_j, \qquad
x_i = \sum_{j:\, i(j) = i} \theta_j z_j ,
$$

so that $\sum_i y_i = 1$ and $\sum_i x_i = x$. For every $i$ with $y_i > 0$,

$$
\frac{x_i}{y_i} = \sum_{j:\, i(j)=i} \frac{\theta_j}{y_i} z_j
$$

is a convex combination of points of $X_i$, so convexity of $X_i$ gives $x_i/y_i \in X_i$, that is
$x_i \in y_i X_i$. For $i$ with $y_i = 0$ no term was grouped, so $x_i = 0 \in 0\cdot X_i$.
$\blacksquare$

**Why this is GCS.** The right-hand side of (4) is a relaxation that keeps $y_i$ **continuous** and
is still exact set by set. Relaxing $y_i \in \{0,1\}$ to $y_i \in [0,1]$ normally loosens a
mixed-integer problem, but when each piece is a convex set and its lifting is written in perspective
form, **nothing is lost within a piece**. GCS puts each contact mode (including its dynamics) into a
convex set and applies (4) on the edges of a graph, so the remaining gap comes only from **path
selection**, not from the geometry of the pieces
([Marcucci et al. 2024](https://arxiv.org/abs/2101.11565),
[Marcucci, Petersen, von Wrangel, Tedrake 2023](https://arxiv.org/abs/2205.04422)).

**Failure mode.** Drop boundedness and (4) no longer holds as written — for unbounded sets one must
take the closure of the right-hand side and add recession directions separately. This is the
practical reason for bounding forces in contact problems: without a bound, the lifting itself does
not give a closed set.

## Proof sketch

### R4 — the pair's hull, and the relaxation gap

**Corollary.** Taking $m = 2$, $X_1 = [0,\Lambda] \times \{0\}$ and
$X_2 = \{0\} \times [0,\Phi]$ in (4) gives $X_1 \cup X_2 = S_\square$ and (5).

**Proof.** ($\subseteq$) A point of (4) has the form $y_1(\alpha, 0) + y_2(0, \beta)
= (y_1\alpha,\, y_2\beta)$ with $\alpha \in [0,\Lambda]$, $\beta \in [0,\Phi]$, $y_1 + y_2 = 1$ and
$y \ge 0$. Then

$$
\frac{a}{\Lambda} + \frac{b}{\Phi}
= y_1\frac{\alpha}{\Lambda} + y_2\frac{\beta}{\Phi}
\le y_1 + y_2 = 1 .
$$

($\supseteq$) Conversely, if $(a,b) \ge 0$ satisfies $a/\Lambda + b/\Phi \le 1$, set
$y_1 = a/\Lambda$ and $y_2 = 1 - y_1$. If $y_2 = 0$ then $b = 0$ and $(a,0) \in X_1$. If
$y_2 > 0$ then $\beta = b/y_2$ and

$$
\beta \le \Phi
\iff b \le \Phi\Big(1 - \frac{a}{\Lambda}\Big)
\iff \frac{a}{\Lambda} + \frac{b}{\Phi} \le 1 ,
$$

so $\beta \in [0,\Phi]$ and $(a,b) = y_1(\Lambda, 0) + y_2(0, \beta)$. $\blacksquare$

**It is the same as big-M.** In the mixed-integer encoding $\lambda \le \Lambda y$,
$\varphi \le \Phi(1-y)$, $y \in \{0,1\}$, relaxing $y$ to $[0,1]$ and eliminating it gives exactly
$\lambda/\Lambda + \varphi/\Phi \le 1$ — precisely (5). So the **per-step big-M relaxation is one
pair's convex hull**, and per step it cannot be tightened further.

**Measured: and still the gap is large.** On the same $N = 6$ problem the enumerated optimum is
$J^\ast = 0.00884227$ (only **42** of 4096 mode branches are feasible), the optimizer's largest
contact force is $\max\lambda^\ast = 1.055766$ N, its first input is $u_0^\ast = +2.0$ (saturated at
the bound), and its gaps satisfy $\varphi_1 = 0$ at every step — it **pushes against the left plate
from start to finish**. The lower bounds are:

| $\Lambda$ | contains optimizer | complementarity dropped | per-step hull (5) | gap (dropped) | gap (hull) |
|---|---|---|---|---|---|
| $20.00$ | yes | $0.00000000$ | $0.00000000$ | $100.000\%$ | $100.000\%$ |
| $10.00$ | yes | $0.00000000$ | $0.00000000$ | $100.000\%$ | $100.000\%$ |
| $5.00$ | yes | $0.00000000$ | $0.00001115$ | $100.000\%$ | $99.874\%$ |
| $2.00$ | yes | $0.00000000$ | $0.00055652$ | $100.000\%$ | $93.706\%$ |
| $1.06$ | yes (smallest) | $0.00004900$ | $0.00154435$ | $99.446\%$ | $82.534\%$ |
| $1.00$ | **no** | $0.00010000$ | $0.00167301$ | — | — |

Three ways to read it.

1. **A loose bound makes the relaxation meaningless.** Both bounds are $0$ at $\Lambda = 20$ — if
   force can grow for free, the slider can be **dragged without being touched**.
2. **The hull always beats dropping.** The hull bound in (5) is larger in every row. That is free.
3. **And still a gap remains.** Even at $\Lambda = 1.06$, the smallest bound that still contains the
   optimizer, the gap is $82.5\%$. The intersection of all the per-step hulls is **not the hull of
   the trajectory set** — each pair's hull is half its box, so $n$ pairs give a volume ratio of
   $2^{-n}$ ($2^{-12} \approx 2\times10^{-4}$ for the 12 pairs of $N = 6$), and the intersection
   still contains **plenty** of unrealizable trajectories. The last row shows that tightening the
   bound further raises the bound but **cuts off the optimizer** — it is no longer a relaxation.

This is where GCS's design comes from: make the vertex of a graph a **whole mode** (a convex set
holding the dynamics, the input limits and the contact condition together) and apply (4) on the
edges, and the looseness leaves the geometry, with only **path selection** remaining. The attempt to
push this all the way for contact-rich manipulation is
[Graesdal et al. 2024](https://arxiv.org/abs/2402.10312) — and note that even there the gap is
**measured**, not **proved**.

## Problem set

All you need is numpy, scipy and paper. Problems 7 and 8 involve code.

1. **(Derivation)** For one step with $n_c$ contacts, relax as $\varphi_i\lambda_i = \varepsilon$
   ($i = 1,\dots,n_c$) and show that (1) holds separately for each contact when the inertia matrix is
   the identity and the contact Jacobians are mutually orthogonal. Where do cross terms appear once
   orthogonality fails?
2. **(Derivation)** Show that taking $\varepsilon \propto h^2$ keeps **both** biases of (2) bounded
   as $O(h^0)$, and determine the proportionality constant from an allowed gap $\delta$ (check
   whether $\varepsilon = \delta g$ is the answer).
3. **(Proof)** Show that at a point with $\varphi = \lambda = 0$ **both** LICQ and MFCQ fail for the
   constraints $\varphi \ge 0$, $\lambda \ge 0$, $\varphi\lambda = 0$. Hint: evaluate
   $\nabla(\varphi\lambda) = \lambda\nabla\varphi + \varphi\nabla\lambda$ at that point. Conclude
   that the standard NLP convergence theorems are unavailable.
4. **(Proof)** Point out exactly where boundedness was used in the proof of (4), and build a
   counterexample with $X_1 = \{(t,0) : t \ge 0\}$ and $X_2 = \{(0,t) : t \ge 0\}$ (unbounded)
   showing that the right-hand side is not closed.
5. **(Numerical)** Confirm by integration that the triangle of (5) is exactly half the area of the
   box, and show that $n$ independent pairs give a volume ratio of $2^{-n}$. Tabulate
   $n = 1, 2, 4, 6, 12$ (answers: $0.5$, $0.25$, $0.0625$, $0.0156$, $0.0002$).
6. **(Numerical)** Reproduce the hull bound $0.00055652$ at $\Lambda = 2.00$ for the pushing problem
   in the text. Then say in one sentence why, if $\Lambda$ is set slightly below $1.055766$, the
   resulting number cannot be called a lower bound even though it is **larger**.
7. **(Implementation)** Implement ADMM with (3) and (7) and reproduce both rows of the table
   (fixed $\rho = 1$ → $J/J^\ast = 2.443$, residual $\le 10^{-11}$, $u_0 = 0$;
   $\rho: 0.1 \to 30$ → $J/J^\ast = 1.132$). Measure the per-iteration time and report its slope
   in $N$.
8. **(Counterexample)** Refute the claim "a point satisfying every per-step hull is close to the
   trajectory of some mode sequence". That is, exhibit a point that satisfies (5) at every step but
   is realizable by **no** mode sequence, and show its cost is below $J^\ast$ (the $82.5\%$ gap in
   the text is caused by exactly such points).

## Paper reading

**Two must-reads.** Write a one-page note on each, answering the questions below.

1. [Aydinoglu, Wei, Huang, Posa 2024, "Consensus Complementarity Control for Multicontact MPC"](https://doi.org/10.1109/TRO.2024.3435423) — §3–5.
   - What does their splitting separate from what? Point to the paper's own symbols for the
     counterpart of the $z$-step in (7) and for the counterpart of (3).
   - What **exactly** do the authors claim about convergence — global optimality, a property of the
     fixed points, or empirical performance? Does the "feasible but do-nothing fixed point" measured
     in the text contradict that claim?
   - How do they meet the real-time budget: a fixed iteration count, a fixed time budget, or early
     termination? Does the paper measure the effect of that choice on solution quality?
2. [Marcucci, Petersen, von Wrangel, Tedrake 2023, "Motion Planning around Obstacles with Convex Optimization"](https://arxiv.org/abs/2205.04422) — §3.
   The theory of the perspective lifting is in the same authors'
   [Shortest Paths in Graphs of Convex Sets](https://arxiv.org/abs/2101.11565)
   (SIAM J. Optim. 34(1):507-532, 2024).
   - How does the perspective lifting correspond to (4) in the text? State in your own words the
     claim that the relaxation is "exact set by set".
   - Where does the remaining gap come from (geometry versus path)? Does the paper **prove** a bound
     on the gap?
   - To use this formulation for contact modes, what set must be built per mode? Once friction
     enters, is that set still convex (recall the friction cones of `s2-grasp-mechanics`)?

**Keep nearby.**
[Posa, Cantu, Tedrake 2014](https://doi.org/10.1177/0278364913506757) is the prototype of putting
contact in as complementarity and optimizing a trajectory, and
[Scholtes 2001](https://doi.org/10.1137/S1052623499361233) is the convergence theory of relaxation
schemes (the source of the bias treated in R1).
[Aydinoglu & Posa 2021](https://arxiv.org/abs/2109.07076) is the first report of the ADMM splitting,
and [Graesdal et al. 2024](https://arxiv.org/abs/2402.10312) carries GCS into contact-rich
manipulation. For real control of planar pushing see
[Hogan & Rodriguez 2020](https://doi.org/10.1177/0278364920913938), and for a recent approach to the
global problem, [Venkatesh et al. 2025](https://doi.org/10.1109/LRA.2025.3615030).

## Reproduction task

**R3 — contact-implicit MPC for planar pushing, and the relaxation gap.** Implement the model from
the text as written. There is no training; numpy and scipy suffice. Three parts, and each part's
acceptance criteria are **measured** values.

**(a) The law of the relaxation bias.** For one step at $q = v = 0$ with $h = 0.05$ and $g = 9.81$,
evaluate (6) directly and reproduce the table below ($f = -0.024525$, exact
$\lambda^{\text{exact}} = 9.81$).

| $\varepsilon$ | gap $\varphi^+$ | $h^2\varepsilon/\lvert f\rvert$ | ratio | $\Delta\lambda$ | $\varepsilon/\lvert f\rvert$ | ratio |
|---|---|---|---|---|---|---|
| $10^{-2}$ | $9.801926\times10^{-4}$ | $1.019368\times10^{-3}$ | $0.96157$ | $3.920770\times10^{-1}$ | $4.077472\times10^{-1}$ | $0.96157$ |
| $10^{-3}$ | $1.015166\times10^{-4}$ | $1.019368\times10^{-4}$ | $0.99588$ | $4.060664\times10^{-2}$ | $4.077472\times10^{-2}$ | $0.99588$ |
| $10^{-4}$ | $1.018945\times10^{-5}$ | $1.019368\times10^{-5}$ | $0.99958$ | $4.075779\times10^{-3}$ | $4.077472\times10^{-3}$ | $0.99958$ |
| $10^{-6}$ | $1.019364\times10^{-7}$ | $1.019368\times10^{-7}$ | $1.00000$ | $4.077455\times10^{-5}$ | $4.077472\times10^{-5}$ | $1.00000$ |
| $10^{-8}$ | $1.019368\times10^{-9}$ | $1.019368\times10^{-9}$ | $1.00000$ | $4.077472\times10^{-7}$ | $4.077472\times10^{-7}$ | $1.00000$ |

*Acceptance*: both ratio columns equal $1.00000$ (error $<10^{-4}$) for $\varepsilon \le 10^{-6}$,
and the gap agrees with $\varepsilon/g$ from (2) to a relative error of $10^{-3}$.

**(b) Real-time contact-implicit MPC.** Implement ADMM with (3) and (7). Factor the $z$-step matrix
once and only back-substitute per iteration. Horizon $N = 6$, 240 iterations per penalty schedule,
80 closed-loop steps, **warm starting** each step by shifting the previous solution by one. The
simulator solves the LCP in closed form (the two-case branch of R1).

*Acceptance*:
- Reproduce the enumerated optimum $J^\ast = 0.00884227$ and confirm that 42 of 4096 branches are
  feasible. At the optimizer, $\max\lambda^\ast = 1.055766$, $u_0^\ast = +2.0$, and $\varphi_1 = 0$
  at every step.
- Fixed $\rho = 1$: complementarity residual $\le 10^{-11}$, $J/J^\ast = 2.443 \pm 0.01$, $u_0 = 0$
  ($|u_0| < 10^{-6}$), and the slider does not move in closed loop ($|s - s^\ast| = 0.06$
  throughout).
- $\rho: 0.1 \to 30$: $J/J^\ast = 1.132 \pm 0.01$, residual of order $7.8\times10^{-3}$, and
  $|s - s^\ast| < 10^{-6}$ after 80 closed-loop steps.
- Mean solve time per step $< 10$ ms and max $< 50$ ms (measured: mean $6.43$, max $8.19$ ms), with
  per-iteration time of order $0.0229$ ms at $N = 4$ and $0.0630$ ms at $N = 24$.

**(c) The relaxation gap.** Compute the optimum of the convex problem with the per-step hull
constraint (5) and of the convex problem with complementarity dropped entirely, for
$\Lambda \in \{20, 10, 5, 2, 1.06\}$, and reproduce the table in the text.

*Acceptance*: in every row the hull bound $\ge$ the dropped bound and both $\le J^\ast$; both bounds
are $0$ at $\Lambda = 20$ (a $100\%$ gap); and the hull bound at $\Lambda = 1.06$ is
$0.00154435 \pm 5\times10^{-5}$ (an $82.5\%$ gap). Write one sentence on why lowering $\Lambda$
below $\max\lambda^\ast$ raises the number but stops it being a bound.

**Common traps.** ① Putting the input limits into the $z$-step destroys the closed form — send them
to the projection step instead (box projection is closed form too). ② With no regularization at all
on the contact forces the matrix in (7) is singular ($10^{-9}$ is enough). ③ The per-branch QPs of
the enumeration can **fail silently** — if convergence failures are not filtered out, $J^\ast$ comes
out wrong (the author produced a non-monotone table this way once). Supply analytic gradients per
branch and filter on a residual $< 10^{-7}$.

## Open problems

- **Global optimality in real time.** Can the fixed points of nonconvex ADMM be **guaranteed** to
  correspond to a good mode sequence? Recent work mixes sampling with local complementarity
  ([Venkatesh et al. 2025](https://doi.org/10.1109/LRA.2025.3615030)), but there is still no
  guarantee.
- **A theory of the penalty schedule.** In the text $\rho: 0.1 \to 30$ separated $2.443\,J^\ast$
  from $1.132\,J^\ast$. Can the schedule be **derived** from the problem's conditioning and contact
  count? Today it is tuned.
- **Tightening with friction included.** (5) is the hull of a normal pair. With a friction cone the
  mode set becomes a second-order cone and the hull is more complicated — can that hull be written
  in closed form?
- **A provable bound on the gap.** GCS relaxation gaps are measured, not **proved**. Is there a
  theorem bounding the gap in terms of contact structure (the diameter of the mode graph, the number
  of contacts)? This is the question of
  [Graesdal et al. 2024](https://arxiv.org/abs/2402.10312).
- **Coupling $\varepsilon$ and $h$.** (2) demands $\varepsilon \propto h^2$. How is that coupling
  maintained in an integrator with adaptive time steps?

## Concept check

Take it with `rc quiz s2-planning-through-contact`. It is only a concept check; the real work is the
problem set and the reproduction task.

## How to study this stage

**Order.** ① Do R1 by hand all the way — solve the quadratic in (6) and expand to get (1) and (2)
yourself. The coupling rule between $h$ and $\varepsilon$ falls out here, and it is the single thing
most often got wrong in practice. ② Prove (3), then implement ADMM **yourself** with (7). Feel that
the one line moving the factorization out of the loop is the whole of the real-time claim. ③ Run it
with fixed $\rho$ and **see the do-nothing fixed point for yourself** before adding the penalty
schedule. Reverse this order and ADMM looks like a method that simply works. ④ Write the proof of R3
and get R4 as its corollary, then reproduce the $\Lambda$ rows of the table and watch where the
relaxation goes slack. ⑤ Read the two must-reads — after implementing, the papers' symbols map
straight onto lines of your own code.

**How to check yourself.** Make each stage's "it is right" a number: does the ratio in (1) converge
to $1.00000$; does the enumeration give $J^\ast = 0.00884227$ with 42 branches; does fixed $\rho$
give the $2.443$ factor; is the hull bound $0.00154435$ at $\Lambda = 1.06$. When a number is off,
**suspect the enumeration first** — silent convergence failures in the per-branch QPs are the most
common cause.

**Time.** 110 minutes on the text and derivations, 120 on the two must-reads and notes, 180 on the
problem set, 115 on the reproduction task, 15 on the concept check. Part (b) of the reproduction is
the longest — the implementation itself is short, and the point is to spend the time varying the
penalty schedule and watching how the fixed point changes.

**Next.** This is the last lesson of the module. The combinatorial side of contact modes as a graph
was already seen in `c6-combinatorial-gcs`, and this lesson opened the road to **using** that graph
for contact. For the perception side of manipulation (tactile and visual), go back and reread
`s2-tactile-contact-estimation` and `s2-learned-grasping`: you will see why the state-estimation
accuracy that planning demands is exactly what those lessons' limits bear on.
