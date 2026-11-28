---
id: c4-contact-implicit-hybrid
lang: en
title: Contact-implicit and hybrid trajectory optimization
summary: >-
  Set up the through-contact transcription that pulls contact into the optimization without a mode
  schedule, and prove that its price — the complementarity constraint — **breaks LICQ at every
  feasible point**. That voids the SQP guarantees of the previous lesson wholesale and makes
  relaxation mandatory; but the relaxation is always tight at the optimum, which numerically yields
  a **physically false, cheaper** trajectory. On the other side, where contact is seen as a mode
  transition, measure directly why the saltation matrix is needed — omit it and the gradient is
  eight digits wrong.
objectives:
  - Prove that the complementarity set is non-convex and that LICQ fails at every feasible point.
  - Derive the time-stepping complementarity transcription and explain why through-contact can dispense with a mode schedule.
  - Derive the saltation matrix from the guard and the reset map, and verify it against a finite-difference Jacobian.
  - Measure the effect of the relaxation parameter on cost, convergence and the contact schedule, and state the trade-off.
  - Explain the complexity trade-off between enumerating mode schedules and through-contact.
tags: [optimal-control, contact, complementarity, hybrid-systems, saltation, licq, research]
---

# Contact-implicit and hybrid trajectory optimization

## Setup and notation

All five previous lessons assumed $f$ was smooth. Each marked the point where that assumption
breaks under "where the assumptions break", and this lesson is the bill that collects them.
Contact is the **unavoidable** non-smoothness in robotics, and there are two routes. Lift the
contact forces into the decision variables and tie them with complementarity constraints —
**through-contact**, which then needs no mode schedule — or state the modes explicitly and correct
the derivative at the transition surface — the **hybrid** view, which then needs the saltation
matrix. We do both. The recommended prerequisites are the previous five lessons; contact dynamics
itself is covered by `c2-contact-dynamics`.

What this lesson additionally assumes:

- Optimization: the constraint qualifications (LICQ, MFCQ) and the fact that when they fail the KKT
  conditions need not be necessary (H2 of `c4-direct-collocation-sqp` R3).
- Contact dynamics: the gap function, the friction cone, complementarity. Derived in
  `c2-contact-dynamics`; here they are used **as constraints in an optimization**.
- Hybrid systems: guards, reset maps, modes.

Notation:

| Symbol | Meaning |
|---|---|
| $q, v$ | position and velocity, $x = (q,v)$ |
| $\phi(q) \ge 0$ | the **gap function**; $\phi = 0$ is contact |
| $\lambda \ge 0$ | contact force (normal component); friction is $\lambda_t$ |
| $0 \le a \perp b \ge 0$ | **complementarity**: $a \ge 0$, $b \ge 0$, $a^\top b = 0$ |
| $\varepsilon \ge 0$ | the complementarity **relaxation** parameter, $a^\top b \le \varepsilon$ |
| $g(x) = 0$ | the **guard** (transition surface) of a hybrid system |
| $R(x)$ | the **reset map**; for an impact, $v \mapsto -e\,v$ |
| $f^-, f^+$ | the vector fields just **before** and **after** the transition |
| $\Xi$ | the **saltation matrix**, the derivative of the flow across the transition surface |
| $e \in [0,1]$ | the coefficient of restitution |
| $h$, $N$ | time step and number of steps |

**The two views this lesson covers**:

| | through-contact (complementarity) | hybrid (explicit modes) |
|---|---|---|
| Mode schedule | **not needed** — the optimizer picks it | given by a human, or enumerated |
| Constraints | complementarity (non-convex, LICQ fails) | smooth within each mode |
| Derivatives | usable only after relaxation | corrected by the **saltation matrix** |
| Representative | Posa 2014, Mordatch 2012 | per-mode DDP, saltation-based feedback |

## Key results

The bracket gives the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (complementarity is non-convex and LICQ fails at every feasible point) [D3]** —
  $\mathcal{C} := \{(a,b) \in \mathbb{R}^2 : a \ge 0,\, b \ge 0,\, ab = 0\}$ is **non-convex**, and
  at **every** point of $\mathcal{C}$ the gradients of the active constraints are linearly
  dependent. At $a = b = 0$ in particular, the gradient of the equality constraint,
  $\nabla(ab) = (b, a)$, is the **zero vector**. So H2 (LICQ) of
  `c4-direct-collocation-sqp` R3 fails, and **not one** of that theorem's conclusions (necessity of
  KKT, boundedness of the multipliers, quadratic convergence of SQP) is guaranteed.
- **R2 (the time-stepping complementarity transcription) [D2]** — one semi-implicit step is
  $$
  M(q_k)\,\frac{v_{k+1} - v_k}{h} = f_{\mathrm{ext}}(q_k, v_k, u_k) + J(q_k)^\top \lambda_k,
    \qquad q_{k+1} = q_k + h\,v_{k+1}, \tag{1}
  $$
  $$0 \le \phi(q_{k+1}) \;\perp\; \lambda_k \ge 0, \tag{2}$$
  and **lifting $\lambda_k$ into the decision variables** lets the optimization choose at which
  steps contact occurs — no mode schedule need be enumerated. This is the through-contact
  transcription of Posa 2014.
- **R3 (the saltation matrix) [D2]** — for a hybrid system with guard $g$ and reset $R$, the
  derivative of the flow **across** the transition surface is not $DR$ but
  $$
  \Xi = DR + \frac{\big(f^+ - DR\,f^-\big)\,\nabla g^\top}{\nabla g^\top f^-}. \tag{3}
  $$
  For a bouncing ball ($\dot y = v$, $\dot v = -g$, guard $y = 0$, reset $v \mapsto -ev$),
  $$
  \Xi = \begin{bmatrix} -e & 0 \\ -\dfrac{(1+e)g}{v^-} & -e \end{bmatrix}, \tag{4}
  $$
  which in the reproduction task matches a finite-difference Jacobian to within $10^{-9}$. **Using
  only $DR$ gives an $O(1)$ error** (measured: a ratio of eight to nine digits).
- **R4 (relaxation is not free) [D2]** — relaxing $ab = 0$ to $ab \le \varepsilon$ restores LICQ,
  but at the optimum that constraint is **always active as an equality** ($ab = \varepsilon$) — the
  optimizer **spends the relaxation to lower the cost**. The consequences: the cost error is
  $O(\varepsilon)$; at loose $\varepsilon$ the solution is **physically false**, with forces acting
  while not in contact; and as $\varepsilon \to 0$ the iteration count explodes. The reproduction
  task measures all three.
- **R5 (combinatorial explosion of mode enumeration) [D1]** — with $m$ contact points and $N$
  steps there are $2^{mN}$ mode sequences. The hybrid view must **fix** one of them to get a
  smooth problem; through-contact avoids the enumeration but accepts **non-convexity**. Neither is
  free, and that trade-off is the central tension of the subject. **[D1]**

## Derivation

### R2 — time stepping and through-contact

**Why time stepping.** Integrating a system with contact in an event-driven way (stop at each guard
and apply an impulse) makes the events accumulate as contacts multiply (Zeno behaviour) and the
integration may never finish. Stewart & Trinkle 1996 instead use a **fixed step** and lump the
contact force within a step into an **impulse**, solving a complementarity problem. Then no events
need be found and each step finishes in finite work.

**One step.** Integrating the equations of motion over the step interval and writing the contact
impulse as $\lambda_k$ (units of force $\times$ time $/\,h$, i.e. an average force) gives (1). It
matters that the **velocity is updated first and the position with that new velocity**
(semi-implicit): update the position first and the contact force cannot prevent penetration at the
next step.

**What complementarity means.** Read the three conditions of (2) one at a time.

- $\phi(q_{k+1}) \ge 0$: **no penetration**. The gap cannot go negative.
- $\lambda_k \ge 0$: the contact force only **pushes**. The ground cannot pull on a foot.
- $\phi(q_{k+1})\,\lambda_k = 0$: **apart means no force, force means together**.

The third is the crux and the source of the non-convexity. It is a **logical or** — "at least one
of the two is zero" — and a disjunction does not make a convex set (R1).

**The idea of through-contact (Posa 2014).** The classical approach **first fixes** a mode schedule
(which contacts are active on which intervals) and solves a smooth trajectory optimization within
each mode. Then a wrong schedule means no answer, and there are $2^{mN}$ schedules (R5). Posa 2014
lifts $\lambda_k$ into the **decision variables** and imposes (2) as a constraint. Then

- the optimization **chooses for itself** $\lambda_k > 0$ (contact) or $\phi > 0$ (no contact) at
  each step, and
- the mode schedule becomes an **output** of the solution.

The price is the non-convexity of (2) and the failure of LICQ, which are R1 and R4.

**Where the assumptions break**: the semi-implicit step of (1) assumes a restitution coefficient of
**zero** (inelastic collision). Once $\phi(q_{k+1}) = 0$, the normal velocity is absorbed to zero in
that step. Wanting an elastic collision ($e > 0$) requires adding a restitution term to a
velocity-level complementarity, and then energy leaks in a step-size-dependent way. Second, (2)
evaluates the gap at $q_{k+1}$, and if $\phi$ is nonlinear that constraint is nonlinear; linearising
it ($\phi(q_k) + J h v_{k+1} \ge 0$) **does not fully prevent penetration** (the linear
complementarity formulation of Anitescu & Potra 1997 makes exactly this choice — easier to solve, at
the price of allowing small penetration).

### R3 — deriving the saltation matrix

Now the opposite view: state the modes **explicitly** and correct the derivative at the transition.

A hybrid system: $\dot{x} = f^-(x)$ where $g(x) > 0$; at the guard $g(x) = 0$ the reset
$x^+ = R(x^-)$; and thereafter $\dot{x} = f^+(x)$. Suppose the nominal trajectory **crosses** the
guard transversally at time $t_i$ (i.e. $\nabla g^\top f^- < 0$, so it genuinely passes through).

Perturbing the initial state by $\delta x_0$ also **changes the time at which the guard is met**,
and that change of time is what the saltation matrix is. Write it in three steps.

**Step 1 — the change in transition time.** Let $\delta x^-$ be the variation before the nominal
transition. The perturbed trajectory meets the guard at $\tilde{t} = t_i + \delta t$. Expanding
$g(\tilde{x}(\tilde{t})) = 0$ to first order,

$$
0 = g\big(x(\tilde t) + \delta x^-\big)
  \approx \underbrace{g(x(t_i))}_{=0} + \nabla g^\top f^-\,\delta t + \nabla g^\top \delta x^-,
$$

so

$$\delta t = -\frac{\nabla g^\top \delta x^-}{\nabla g^\top f^-}. \tag{5}$$

(A zero denominator is **grazing** contact and voids this derivation — see the failure mode below.)

**Step 2 — just after the transition.** The perturbed pre-transition state is
$x(t_i) + f^-\delta t + \delta x^-$, so expanding the reset to first order,

$$
\tilde{x}^+(\tilde t) \approx R\big(x(t_i)\big) + DR\big(\delta x^- + f^-\delta t\big).
$$

**Step 3 — return to a common time.** The two trajectories must be compared **at the same time**.
The nominal is $x^+(t) \approx R(x(t_i)) + f^+(t - t_i)$, while the perturbed flows with $f^+$ from
$\tilde t$, so $\tilde{x}(t) \approx \tilde{x}^+(\tilde t) + f^+(t - \tilde t)$. Subtracting,

$$
\delta x^+ = DR\,\delta x^- + DR\,f^-\delta t - f^+\delta t
  = DR\,\delta x^- - \big(f^+ - DR\,f^-\big)\delta t,
$$

and substituting (5),

$$
\delta x^+ = \left[DR + \frac{(f^+ - DR\,f^-)\,\nabla g^\top}{\nabla g^\top f^-}\right]\delta x^-
  =: \Xi\,\delta x^-,
$$

which is (3). **The correction term comes from the single fact that the transition time wobbles** —
so using $DR$ alone ignores wholesale the change in **when** the trajectory meets the surface.

**Made concrete on the bouncing ball.** With $x = (y, v)$, $f^- = (v, -g)$, reset
$R(y,v) = (y, -ev)$, $\nabla g = (1,0)^\top$ and $f^+ = (-ev^-, -g)$, computing each piece gives
$DR = \mathrm{diag}(1, -e)$, $\nabla g^\top f^- = v^-$, $DR f^- = (v^-, eg)$ and
$f^+ - DR f^- = \big(-(1+e)v^-,\; -(1+e)g\big)$, so

$$
\Xi = \begin{bmatrix}1 & 0\\ 0 & -e\end{bmatrix}
  + \frac{1}{v^-}\begin{bmatrix}-(1+e)v^- \\ -(1+e)g\end{bmatrix}\begin{bmatrix}1 & 0\end{bmatrix}
  = \begin{bmatrix}-e & 0 \\ -\dfrac{(1+e)g}{v^-} & -e\end{bmatrix},
$$

which is (4). Two things can be read off. (a) $\det\Xi = e^2$ — perfectly elastic ($e=1$) preserves
area and inelastic ($e<1$) contracts it. (b) The $(2,1)$ entry **diverges** as $v^- \to 0$.

**Where the assumptions break**: (i) **Grazing contact.** If $\nabla g^\top f^- \to 0$ the
denominator of (5) vanishes and $\Xi$ diverges. Physically this is "almost touching", and near it
the flow is **continuous but not differentiable** in the initial condition, because whether contact
happens at all flips. This is the fundamental reason gradient-based methods are hard on systems with
contact (Burden et al. 2016 justify (3) by showing the flow is **piecewise differentiable** as long
as transversality holds). (ii) **Simultaneous contact.** Meeting two guards at once leaves it
ambiguous which reset applies first, and (3) is not uniquely defined. (iii) **Accumulation (Zeno).**
A ball with $e < 1$ bounces infinitely often in finite time, so (3) must be multiplied infinitely
many times — the product goes to zero like a power of $e$, but numerically the transition detection
never terminates.

### R4 — measuring the price of relaxation

Because of the LICQ failure R1 will prove, (2) must not be handed to an NLP solver as it stands. The
practical standard is **relaxation**:

$$\phi(q_{k+1})\,\lambda_k \le \varepsilon, \qquad \phi \ge 0,\; \lambda \ge 0. \tag{6}$$

With $\varepsilon > 0$ an interior point exists and LICQ is restored. The trouble is that **the
optimizer exploits that slack**.

Measure it on the one-dimensional problem of the reproduction task. A unit-mass ball rests on the
ground ($y \ge 0$) and must be pushed by a force $u$ ($\lvert u\rvert \le 40$) over $T = 1$ s to
reach $y(T) = 0.5$. The cost is $\int u^2 dt$, the transcription is (1) and (6), with $h = 0.05$ and
$N = 20$. Tightening the relaxation:

| $\varepsilon$ | cost | $\max \phi\lambda$ | $\lvert y_N - 0.5\rvert$ | iterations | steps with $\lambda > 10^{-6}$ |
|---|---|---|---|---|---|
| $10^{-1}$ | $57.810722$ | $1.000\times10^{-1}$ | $1.3\times10^{-14}$ | $2213$ | $20$ |
| $10^{-2}$ | $72.172341$ | $1.000\times10^{-2}$ | $7.2\times10^{-16}$ | $172$ | $20$ |
| $10^{-3}$ | $74.289430$ | $1.000\times10^{-3}$ | $1.1\times10^{-16}$ | $361$ | $20$ |
| $10^{-4}$ | $74.508709$ | $1.000\times10^{-4}$ | $4.8\times10^{-15}$ | $217$ | $20$ |
| $10^{-5}$ | $74.530709$ | $9.999\times10^{-6}$ | $5.1\times10^{-15}$ | $134$ | $20$ |
| $10^{-6}$ | $74.532909$ | $9.995\times10^{-7}$ | $5.3\times10^{-15}$ | $149$ | $20$ |
| $10^{-8}$ | $74.533151$ | $9.896\times10^{-9}$ | $5.1\times10^{-15}$ | $171$ | $6$ |
| $0$ | $74.533199$ | $1.2\times10^{-13}$ | $8.9\times10^{-14}$ | $3407$ | $6$ |

**Three things to read.**

(a) **The relaxation is always tight.** The $\max\phi\lambda$ column is exactly $\varepsilon$. The
optimizer leaves none of the slack unused — it **spends all of it**, because that lowers the cost.
At $\varepsilon = 10^{-1}$ the cost is $57.81$, **22% cheaper** than the limit $74.53$. That
trajectory is physically false: the ball is off the ground ($\phi > 0$) and yet the ground is
pushing it ($\lambda > 0$). "Relaxed contact" is not a small numerical blemish but a **free force**.

(b) **The cost error is $O(\varepsilon)$.** At $\varepsilon = 10^{-3}, 10^{-4}, 10^{-5}, 10^{-6}$
the gap to the limit is $-0.2438, -0.0245, -0.00249, -0.00029$, shrinking **tenfold** each time. So a
target accuracy determines the required $\varepsilon$ — and conversely, choosing $\varepsilon$
arbitrarily leaves you not knowing what percentage of the cost is fictitious.

(c) **The contact schedule is wrong.** The last column is decisive. For
$\varepsilon \ge 10^{-6}$, contact force is applied at **all 20 steps** — including while the ball
is in flight. Only at $\varepsilon \le 10^{-8}$ does it drop to 6 and recover the physical schedule
(on the ground for a while, then leaving). The **output** of through-contact is the contact
schedule, and when the relaxation is loose **that output is false**.

(d) And $\varepsilon = 0$ costs $3407$ iterations — **twenty times** the roughly $150$ of a moderate
$\varepsilon$. That is the bill for the LICQ failure.

**Where the assumptions break**: the table above is the result of **tightening $\varepsilon$ in an
outer loop**, warm-starting each stage from the previous solution (which is why the iteration count
sometimes *falls* as $\varepsilon$ shrinks). Starting directly at a small $\varepsilon$ without a
warm start does not converge. In other words the numbers are the result of a **procedure** —
"relaxation continuation" — and not of solving at a single $\varepsilon$. That procedure is the
practical standard, and there is no theory for its stopping criterion (open problem 1).

## Proof sketch

### R1 — complementarity is non-convex and LICQ fails at every feasible point [D3]

**Hypothesis** H1: regard
$\mathcal{C} = \{(a,b) \in \mathbb{R}^2 : a \ge 0,\, b \ge 0,\, ab = 0\}$ as a constraint set — two
inequalities and one equality.

**Conclusions** C1: $\mathcal{C}$ is non-convex. C2: at **every** point of $\mathcal{C}$ the active
constraint gradients are linearly dependent (LICQ fails). C3: therefore the conclusions of
`c4-direct-collocation-sqp` R3 do not apply.

**Strategy**: C1 is one counterexample. C2 writes $\mathcal{C}$ as a union of two rays and checks
directly that the gradients are parallel in each case — with only two cases, that is a complete
proof.

1. **The shape of $\mathcal{C}$.** $ab = 0$ means $a = 0$ or $b = 0$, so
   $$\mathcal{C} = \underbrace{\{(0,b) : b \ge 0\}}_{\text{vertical ray}} \;\cup\;
     \underbrace{\{(a,0) : a \ge 0\}}_{\text{horizontal ray}},$$
   a **union of two rays**, bent at the origin.
2. **Non-convexity (C1).** $(0,1) \in \mathcal{C}$ and $(1,0) \in \mathcal{C}$, but the midpoint
   $(\tfrac12,\tfrac12)$ has $ab = \tfrac14 \ne 0$ and is not in $\mathcal{C}$. **C1**. (The same
   holds in general dimension — complementarity is essentially a **logical or**, and a disjunction
   breaks convexity.)
3. **Case 1: $a = 0$, $b > 0$.** The active constraints are $a \ge 0$ (holding with equality) and
   the equality $ab = 0$. Their gradients are
   $$\nabla(a) = (1, 0), \qquad \nabla(ab) = (b, a) = (b, 0),$$
   which are **parallel** ($\nabla(ab) = b\,\nabla(a)$ with $b > 0$). Two rows of rank 1 are not
   linearly independent → LICQ fails.
4. **Case 2: $b = 0$, $a > 0$.** Symmetric: $\nabla(b) = (0,1)$ and
   $\nabla(ab) = (0, a) = a\,\nabla(b)$ → rank 1 → LICQ fails.
5. **Case 3: $a = b = 0$.** Three constraints are active ($a\ge0$, $b\ge0$, $ab=0$) and
   $$\nabla(ab) = (b,a) = (0,0)$$
   — the equality's gradient is the **zero vector**. A set containing the zero vector is never
   linearly independent, so LICQ fails in the strongest way. (Numerical check: the three rows have
   rank 2.)
6. By 1–5 every point of $\mathcal{C}$ falls into one of cases 3, giving **C2**.
7. **Conclusion C3.** `c4-direct-collocation-sqp` R3 obtained invertibility of the KKT matrix from
   H2 (LICQ) and H3 (SOSC) and derived quadratic convergence from it. When H2 fails, step 3 of that
   argument collapses and, more fundamentally, **the KKT conditions need not be first-order
   necessary** — there can be optimal points at which no multipliers exist. Even when they exist
   they may be unbounded.

**Deleting a hypothesis: where does it collapse?**

- **Relax it ($ab \le \varepsilon$, $\varepsilon > 0$)**: the equality becomes an inequality and an
  interior point exists ($a = b = \sqrt\varepsilon$). Near the origin fewer constraints are active,
  LICQ is restored, and the SQP theorem applies again. The price is R4 — **this is the only reason
  relaxation is used.**
- **Weakening to MFCQ does not help**: MFCQ (Mangasarian-Fromovitz), weaker than LICQ, also fails in
  case 3. If the equality's gradient is zero, MFCQ's very first condition — that the equality
  gradients be linearly independent — fails. So complementarity problems use a **dedicated theory**
  (MPCC, mathematical programs with complementarity constraints), which replaces LICQ with weaker
  conditions such as MPCC-LICQ and states modified stationarity concepts (S-stationarity,
  M-stationarity and others).
- **"So is checking KKT meaningless?"**: not entirely. The KKT points of the relaxed problem
  converge, as $\varepsilon \to 0$, to **weak** stationary points of the original problem (under
  suitable conditions). But that convergence has weak guarantees and no guaranteed rate — which is
  why practice uses relaxation continuation and still has to inspect the result
  **physically** (R4c).
- **How to detect diverging multipliers**: record the multiplier norm against $\varepsilon$ during
  the continuation. If it stays bounded, the solution is likely a strong stationary point of the
  MPCC; if it diverges, the LICQ failure has actually bitten (problem P4).

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R3)** Re-derive (3) for a general $n$-dimensional hybrid system, this time
extending it to a **time-dependent reset map** $R(x,t)$. What extra term appears?
*Solution sketch*: the expansion of step 3 gains $\partial R/\partial t\,\delta t$. Substituting (5)
changes the numerator of $\Xi$'s correction term to $f^+ - DR f^- - \partial_t R$. Time-dependent
resets arise when an external input acts at the instant of transition (a torque at the moment of
impact, say).

**P2 (derivation, ★★, R2)** Show that the variant of the semi-implicit step (1) that updates the
**position first** ($q_{k+1} = q_k + h v_k$, then $v_{k+1}$) fails to prevent penetration via the
complementarity (2). Estimate how negative the gap can become in one step.
*Solution sketch*: updating the position first makes $q_{k+1}$ independent of $\lambda_k$, so the
first condition of (2) is not controlled by $\lambda$. The size of the negative gap is about the
approach velocity $\times\,h$ — so an $O(h)$ penetration appears and shrinks only at first order in
$h$. In the semi-implicit step, $q_{k+1}$ depends on $\lambda_k$ through $v_{k+1}$, so the
constraint actually acts.

**P3 (proof, ★★, R1)** Extend R1's proof to the general complementarity
$0 \le \phi \perp \lambda \ge 0$ with $m$ contacts ($\phi,\lambda \in \mathbb{R}^m$). Describe the
**set of points** at which LICQ fails and decide whether it is the whole feasible set or only part
of it.
*Solution sketch*: the strategy is to repeat R1's case analysis componentwise. The key is that the
gradient of the active equality $\phi_i\lambda_i = 0$ has the form $(\lambda_i e_i, \phi_i e_i)$.
Since for each $i$ either $\phi_i = 0$ or $\lambda_i = 0$, that gradient is parallel to the
corresponding active inequality's gradient, so it fails at **every** feasible point. A component
with $\phi_i = \lambda_i = 0$ makes the gradient zero, failing even more strongly; such a component
is called a **degenerate** contact.

**P4 (proof, ★★★, R1 and R4)** Show that the multipliers can diverge during relaxation
continuation. Concretely, find the solution of
$\min_{a,b} \;(a - 1)^2 + b^2$ s.t. $0 \le a \perp b \ge 0$, and the solution and multipliers of the
relaxed problem with $ab \le \varepsilon$ as functions of $\varepsilon$, and describe the
$\varepsilon \to 0$ behaviour.
*Solution sketch*: the original's solution is $(a,b) = (1,0)$ with objective 0 (here the multipliers
stay bounded). To build a diverging example, change the objective so that it pushes toward the
complementarity **corner** — for instance $\min -(a + b)$ subject to the same constraints plus
$a + b \le 1$. The strategy is "solve the relaxed problem's KKT conditions by hand and read off the
order of the multiplier in $\varepsilon$", and the key is to find the case where the multiplier of
$ab \le \varepsilon$ grows like $1/\sqrt\varepsilon$. That divergence is the numerical symptom that
"the LICQ failure has bitten".

**P5 (numerical, ★, R3)** For the bouncing ball with $e = 0.7$, $g = 9.81$ and initial state
$(y_0, v_0) = (1, 0)$, compute the transition time $t_i$, the velocity just before transition $v^-$,
and the $\Xi$ of (4) numerically. Check that $\det\Xi$ equals $e^2$.
*Answer*: $t_i = \sqrt{2y_0/g} = 0.4515236410$ s, $v^- = -g t_i = -4.4294469181$ m/s, and
$$
\Xi = \begin{bmatrix} -0.7 & 0 \\ 3.7650298804 & -0.7\end{bmatrix}
$$
(tolerance $10^{-9}$; the $(2,1)$ entry is $-(1+e)g/v^- = -1.7\times9.81/(-4.4294469181)$).
$\det\Xi = 0.49 = e^2$ ✓.
*Check*: since $\Xi$ is lower triangular, both eigenvalues are $-e$. Confirm algebraically as well
that the $(2,1)$ entry diverges as $v^- \to 0$.

**P6 (implementation, ★★, R3)** Implement the bouncing ball's flow analytically on $[0, T]$ (with
$T$ after the transition), compute $d x(T)/d x_0$ by central differences, and compare with
$\Phi(T - t_i)\,\Xi\,\Phi(t_i)$ where $\Phi(t) = \begin{bmatrix}1 & t\\0&1\end{bmatrix}$. Then do
the same comparison using $DR$ in place of $\Xi$.
*Rubric*: (a) at three or more distinct $x_0$, the prediction with $\Xi$ matches the finite
differences to within $10^{-8}$; (b) you show the prediction with $DR$ alone has $O(1)$ error and
report the ratio of the two errors (the author's implementation gave $10^8$–$10^9$); (c) bringing
$T$ close to $t_i$ and varying the finite-difference step $h$, you explain **why** the finite
differences become unstable near the transition time; (d) you show that at an $x_0$ close to grazing
($v^- \approx 0$) the prediction and the finite differences **both** break down.

**P7 (counterexample, ★★, R4)** Show in **two ways** that "making the relaxation parameter smaller
always gives a better answer" is false: (i) an example where setting $\varepsilon$ too small and
solving **without a warm start** does not converge; (ii) an example where the solution at a loose
$\varepsilon$ has lower cost but is **physically impossible**.
*Property checklist*: for (i), re-run the reproduction task's table without warm starts and show the
failure at $\varepsilon \le 10^{-6}$. For (ii), find in the $\varepsilon = 10^{-1}$ solution the
steps with $\phi_k > 0$ and $\lambda_k > 0$ and print the interval in which **the ball is airborne
while the ground pushes it**. The property to check: a lower cost does not mean a better solution —
if the constraints are false, comparing costs is meaningless.

**P8 (paper, ★★, R1, R2 and R4)** Read Posa et al. 2014 §3–§4 and Stewart & Trinkle 1996 §2–§4,
then write: (a) whether Posa et al. relax the complementarity and, if so, how they choose
$\varepsilon$; (b) how Stewart-Trinkle's time stepping treats (or does not treat) the restitution
coefficient; (c) three pieces of reproduction information the two papers do **not** report.
*Rubric*: (a) passes on identifying the authors' relaxation and scaling treatment and the grounds
for the choice (or the absence of grounds); writing only "they relax it" fails. (b) passes on noting
the inelastic assumption and the role of velocity-level complementarity. (c) passes with three of
"the relaxation schedule, how the initial trajectory is generated, the solver and its tolerances,
the scaling, the polygonal approximation order of the friction cone".

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read with three passes, attacking questions 4, 5, 6 and 7 on the third.

1. **Posa, Cantu & Tedrake, "A direct method for trajectory optimization of rigid bodies through
   contact" (2014, IJRR)** — role: `seminal`. What to read: §3 (the transcription), §4
   (experiments). This is the primary source for R2. See how "leave the mode schedule to the
   optimization" becomes a concrete transcription.
   Extra questions: (a) is what the authors claim to have solved compatible with the price of
   relaxation that R4 of this lesson measured? (b) What are the baselines in the experiments — do
   they compare against a human-specified mode schedule? (c) How do the authors confirm that the
   reported solutions are **physically valid** (do they report complementarity residuals)?
2. **Stewart & Trinkle, "An implicit time-stepping scheme for rigid body dynamics with inelastic
   collisions and Coulomb friction" (1996, IJNME)** — role: `seminal`. What to read: §2
   (formulation), §3 (existence of solutions to the complementarity problem), §4 (numerics). This
   is the primary source for (1) and (2). Note that the **existence proof** is this paper's core
   contribution.
   Extra questions: (a) under what assumptions is the existence they prove (is there a bound on the
   friction coefficient)? (b) What is "implicit" implicit in — position, velocity or force?
   (c) What is the energy behaviour of the scheme (dissipative or conservative)?
3. **Howell, Jackson & Manchester, "ALTRO: a fast solver for constrained trajectory optimization"
   (2019, IROS)** — role: `standard`. What to read: §III (augmented Lagrangian plus DDP), §IV
   (projection). This is the answer at the point where `c4-ilqr-ddp` R4 concluded that "state
   constraints can only be pushed into the cost".
   Extra questions: (a) what effect does the augmented Lagrangian's outer loop have on the quadratic
   convergence of `c4-ilqr-ddp`? (b) Compare what their "projection" step does with the relaxation
   of R4 here. (c) Can ALTRO be applied directly to complementarity constraints — is the LICQ
   failure of R1 not a problem for an augmented Lagrangian?

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
under 500 MB of memory. numpy and scipy only. No simulator.

> **A stated deviation from the blueprint**: the design placed this lesson's reproduction at R3
> (reproducing a paper figure). Reproducing a figure from Posa 2014 requires reading the paper's
> kinematic and mass parameters and relaxation schedule out of the paper, and those values are
> outside what this lesson has **verified**. So the task below is **R2**, and reproducing Posa's
> figure is offered as the **optional** part of condition 4 with a rubric. This follows the
> principle of not using numbers one has not verified oneself as acceptance criteria
> (the "Reproduction tasks" section of lesson `f0-how-to-read-this-track`).

**Input data**: none; everything is given as constants.

**System A — a bouncing ball** (for verifying the saltation matrix): $\dot y = v$, $\dot v = -g$
with $g = 9.81$, guard $y = 0$, reset $v \mapsto -e v$ with $e = 0.7$. Implement the flow
**analytically** (no step integration needed): the free-fall arcs are quadratics and the transition
time is closed form, $t_i = (v + \sqrt{v^2 + 2gy})/g$.

**System B — a one-dimensional contact transcription**: mass $m = 1$, gravity $g = 9.81$, ground
$y \ge 0$, control $\lvert u\rvert \le 40$, contact force $0 \le \lambda \le 40$. The transcription
from (1) and (6) is

$$
v_{k+1} = v_k + \frac{h}{m}\big(u_k - mg + \lambda_k\big), \qquad
  y_{k+1} = y_k + h\,v_{k+1}, \qquad \phi = y,
$$

with $h = 0.05$, $N = 20$, initial $(y_0, v_0) = (0,0)$ (at rest on the ground), terminal constraint
$y_N = 0.5$, and cost $h\sum u_k^2$. The initial guess is $u_k = mg$, $\lambda_k = 0$ (hovering —
since $y \equiv 0$ it is **feasible**).

**Acceptance criteria** — all four must hold to pass.

1. **Confirm the LICQ failure numerically.** Computing the rank of the active-constraint Jacobian of
   the complementarity set $\{a\ge0, b\ge0, ab=0\}$ at three points, obtain
   (a) $(a,b)=(0,0)$: **3** active rows, rank **2** (the equality gradient is
   $\nabla(ab) = (0,0)$); (b) $(0,1)$: 2 active rows, rank **1**; (c) $(1,0)$: 2 active rows, rank
   **1**. Also confirm the non-convexity via the midpoint of $(0,1)$ and $(1,0)$
   ($ab = 0.25 \ne 0$).
2. **The saltation matrix (system A).** With $e=0.7$ and $g=9.81$, for the three initial states
   $(1,0)$, $(2,1.5)$ and $(0.5,-1)$ and $T = t_i + 0.3$: (a) the transition times and pre-transition
   velocities are $(0.4515236410,\,-4.4294469181)$, $(0.8095079680,\,-6.4412731661)$ and
   $(0.2332167630,\,-3.2878564446)$ (to within $10^{-9}$); (b) the maximum difference between the
   finite-difference $dx(T)/dx_0$ and $\Phi(T-t_i)\,\Xi\,\Phi(t_i)$ is $< 10^{-8}$ in all three
   cases (author's implementation $5.0\times10^{-9}$, $9.0\times10^{-9}$, $1.2\times10^{-9}$);
   (c) using $DR = \mathrm{diag}(1,-e)$ in place of $\Xi$ gives errors $> 1$ in all three cases, a
   ratio against (b) of $> 10^{7}$ (author's $7.5\times10^8$, $2.9\times10^8$, $4.3\times10^9$);
   (d) $\det\Xi = e^2 = 0.49$ to within $10^{-12}$.
3. **Relaxation continuation (system B).** Tighten $\varepsilon$ through
   $10^{-1} \to 10^{-2} \to \dots \to 10^{-6} \to 10^{-8} \to 0$, warm-starting each stage from the
   previous solution, and reproduce the table of R4's derivation. The criteria are: (a) at every
   stage $\max\phi\lambda$ **equals** $\varepsilon$ to within $10^{-3}$ relative (the relaxation is
   tight); (b) the cost is **monotone increasing** in $\varepsilon$ and converges to the
   $\varepsilon \to 0$ limit $74.5332 \pm 0.01$, with the gap to the limit shrinking by one digit at
   $10^{-3}, 10^{-4}, 10^{-5}, 10^{-6}$ (confirming $O(\varepsilon)$; the author's values
   $-0.2438, -0.0245, -0.00249, -0.00029$); (c) the number of steps with $\lambda_k > 10^{-6}$ is
   $N = 20$ (all of them) at loose $\varepsilon$ and drops below $10$ for
   $\varepsilon \le 10^{-8}$ (author's $20 \to 6$); (d) the iteration count at $\varepsilon = 0$ is
   at least **five times** that at intermediate $\varepsilon$ (author's $3407$ against $134$–$361$).
4. **Point out the physical falsehood — and (optionally) reproduce Posa.** (a) In the
   $\varepsilon = 10^{-1}$ solution, find the steps with $\phi_k > 10^{-3}$ **and**
   $\lambda_k > 10^{-3}$ and print their count and one $(\phi_k, \lambda_k)$ pair — the goal is to
   show "the ball is airborne while the ground pushes it" in numbers. (b) Confirm that solution's
   cost is below the limit and report by what percentage (author's $57.81$ against $74.53$, 22%
   lower). (c) **Optional (R3)**: pick one figure from Posa et al. 2014 and reproduce that
   trajectory with the paper's parameters. *Rubric*: passes if you tabulate the values **read from
   the paper separately from the values you guessed**, report the complementarity residual and the
   cost, and state explicitly what does not reproduce and why (the missing information). An
   identical figure is not required.

**Baselines**: (i) the finite-difference Jacobian of condition 2 is the independent baseline for the
saltation matrix. (ii) $\det\Xi = e^2$ in condition 2(d) is the analytic baseline. (iii) The
$\varepsilon = 0$ solution of condition 3 is the baseline for the relaxed solutions. (iv) An
analytic lower bound for system B: lifting the ball to $y_N = 0.5$ needs at least the potential
energy $mgy_N = 4.905$ J, and while $\int u^2dt$ is not directly comparable to that, it is worth
solving the **contact-free** problem (removing both the ground constraint and $\lambda$) separately
and reporting how much the contact raises the cost.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| No convergence at all for small $\varepsilon$ | you started directly at a small $\varepsilon$ with no warm start | confirm you are using continuation; condition 3 demands the **procedure** |
| The initial guess is reported infeasible | you started from $u_k = 0$ rather than $u_k = mg$ and the ball sinks through the ground | print $\min y$ and $\max\phi\lambda$ of the initial guess (both should be zero) |
| The relaxation is not tight ($\max\phi\lambda \ll \varepsilon$) | you flipped the relaxation's inequality ($\ge$), or the cost penalises the contact force | check that the cost contains no $\lambda$ term |
| The saltation prediction matches only to two or three digits | the finite-difference step is too large or too small | sweep around $h \sim 10^{-7}$ for the optimum. If $T$ is too close to $t_i$, the perturbed trajectory's transition order changes |
| The saltation prediction is completely wrong | the sign of $\nabla g$, or $f^+$ not evaluated at the **post-reset** state | check that $f^+ = (-ev^-, -g)$; $v^-$ is the value just **before** the transition |
| The $(2,1)$ entry comes out `inf` | $v^- \approx 0$ (grazing) | that is the intended failure; all three states of condition 2 have $\lvert v^-\rvert > 3$ |
| The number of contact steps stays at 20 regardless of $\varepsilon$ | the threshold is too low (you counted $\lambda > 0$) | set the threshold to $10^{-6}$ and check you tightened down to $\varepsilon \le 10^{-8}$ |

## Open problems

- **(open problem) A stopping criterion for relaxation continuation** — as R4 showed, $\varepsilon$
  simultaneously sets the cost error $O(\varepsilon)$, the difficulty of convergence, and even the
  **truth** of the contact schedule. Yet there is no **a priori** criterion for "how far must
  $\varepsilon$ be tightened on this problem". Practice checks physical validity after the fact.
  Current approaches: the stationary-point convergence results of MPCC theory and the empirical
  schedule of [Posa et al. 2014](https://doi.org/10.1177/0278364913506757). What is missing: a rule
  for choosing $\varepsilon$ that guarantees both a target cost accuracy and the correctness of the
  contact schedule.
- **(open problem) Derivatives near grazing contact** — failure mode (i) of R3. As
  $\nabla g^\top f^- \to 0$, $\Xi$ diverges and the flow is not differentiable. That neighbourhood
  is the boundary between touching and not, and systems with repeated contact such as walking pass
  through it **often**. Current approaches: the theory of
  [Burden et al. 2016](https://doi.org/10.1137/15M1016588), which guarantees piecewise
  differentiability wherever transversality holds, and smooth relaxations of contact that remove the
  divergence. What is missing: the **quantitative** trade-off between enlarging the relaxation
  parameter to obtain derivatives and losing physical accuracy — the same gap as open problem 4 of
  `c4-ilqr-ddp`.
- **(open problem) Globality without mode enumeration** — the $2^{mN}$ of R5 gives the global
  optimum if solved exactly as a mixed-integer transcription, but does not scale. Through-contact
  avoids the enumeration and returns only local solutions. Current approaches: grouping contact
  modes by convex decomposition (the GCS of `c6-combinatorial-gcs`) and the contact-invariant
  optimization of [Mordatch et al. 2012](https://doi.org/10.1145/2185520.2185539), which relaxes by
  treating contact activation as a continuous variable. What is missing: a transcription that is
  **polynomial** in the number of contacts and certifies a global gap.
- **(open problem) The non-convexity of friction** — this lesson treated only normal contact.
  Coulomb friction adds a cone constraint and the **principle of maximum dissipation**, which
  creates another complementarity (between tangential velocity and friction force) and, under a
  polygonal approximation, multiplies the modes further. Rigid-body contact with friction **may have
  no solution, or several** (the Painlevé paradox). Current approaches: the relaxed LCP formulation
  of [Anitescu & Potra 1997](https://doi.org/10.1023/A:1008292328909), which guarantees existence at
  the price of a little penetration and tangential slip, and convex approximations. What is missing:
  a formulation that gives physical fidelity and existence at once — a problem that returns in
  `c2-contact-dynamics` and `s2-planning-through-contact`.

## Concept check

Run `rc quiz c4-contact-implicit-hybrid`. The quiz is for **concept checking only**; the real work
is the problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

The seven items cover: at which points complementarity breaks LICQ; whether the complementarity set
is convex; how through-contact dispenses with a mode schedule; the origin of the saltation
correction term; whether the relaxation is active at the optimum; the measurement that best shows
the contact schedule cannot be trusted at a loose relaxation; and whether the order of the
semi-implicit update matters.

## How to study this stage

1. **Read the bill first (30 min)** — collect and re-read the paragraphs from the previous five
   lessons' "where the assumptions break" that mention contact (H1 of `c4-pontryagin-indirect` R1;
   H1 and open problem 4 of `c4-ilqr-ddp` R2; the non-smooth value function of
   `c4-dp-lqr-lqg` R2). Having that map first — this lesson is the answer to those paragraphs — is
   the key.
2. **Prove R1 by hand, all the way (50 min)** — draw the union of two rays and write the gradients
   out in all three cases. Confirming by hand in particular that $\nabla(ab) = (0,0)$ at $a=b=0$
   makes "why relaxation is mandatory rather than optional" self-explanatory. Verify condition 1 in
   ten lines of code.
3. **Derive the saltation matrix in three steps (70 min)** — (5) → step 2 → step 3. The only insight
   is that **the transition time wobbles**; the rest is a first-order expansion. Then substitute the
   bouncing ball to get (4) and confirm $\det\Xi = e^2$ (P5).
4. **Break it by removing the correction (60 min)** — do condition 2(c) **first**. Seeing the
   prediction with $DR$ alone be $O(1)$ wrong against the finite differences fixes "do not use the
   smooth chain rule on a system with contact" in your memory as an eight-digit number. Then put
   $\Xi$ in and bring it to $10^{-9}$.
5. **Implement the transcription, respecting the order (80 min)** — when implementing system B, keep
   **velocity first, position second** (P2 explains why). Start the initial guess at $u = mg$ so it
   is feasible — starting at $u = 0$ sinks the ball through the ground and the solver fails
   immediately.
6. **Build the table by tightening the relaxation (90 min)** — this is the lesson's central
   experience. Build the table of condition 3 yourself and read **three columns together**: that
   $\max\phi\lambda$ is exactly $\varepsilon$; that the cost converges as $O(\varepsilon)$; and that
   the number of contact steps is all of them while $\varepsilon$ is loose. The third is the most
   important and the most overlooked.
7. **Look at the false trajectory yourself (40 min)** — use condition 4(a) to print the steps where
   "the ball is airborne while the ground pushes it". That single line of output permanently engraves
   "a solution with lower cost is not a better solution".
8. **Read the papers existence → transcription → solver (150 min)** — Stewart & Trinkle (existence
   of solutions) → Posa et al. (the transcription) → Howell et al. (the solver). Reading the first
   is what makes "why the complementarity formulation has that shape" understandable, and the third
   is the answer to the question `c4-ilqr-ddp` left open. Write the one-page note per paper —
   **without exception**.
9. **End with what cannot be done (40 min)** — pick **two** of the four open problems and write a
   paragraph on each (this lesson's open problems are especially live). The fourth (friction) is
   taken up by `c2-contact-dynamics` and `s2-planning-through-contact`, and the second (grazing
   contact) by the robustness discussion of the next lesson.

**Passing bar**: you can write R1's three cases and the three steps of the derivation of (3) from a
blank page, you can state that the saltation correction comes from the variation in transition time,
you can explain the three prices of relaxation (cost $O(\varepsilon)$, convergence, and **the truth
of the contact schedule**) with numbers you measured yourself, you have code satisfying all four
acceptance criteria of the reproduction task, and you have notes on all three papers.
