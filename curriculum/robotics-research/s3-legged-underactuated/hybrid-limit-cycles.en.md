---
id: s3-hybrid-limit-cycles
lang: en
title: Hybrid dynamics and limit cycles
summary: >-
  A walking robot is a hybrid system in which smooth dynamics and impacts alternate. Periodic
  walking is treated as a fixed point of the Poincare map, with a proof of why its stability is
  decided by the spectral radius of the map's Jacobian, and the propagation of a perturbation
  through an impact is derived as the saltation matrix. The equations of motion and the impact map
  of a compass gait are derived from scratch, a passive limit cycle is found, and the eigenvalues,
  the energy balance and the saltation matrix are all cross-checked numerically.
objectives:
  - Reconstruct, as a proof sketch, when the Poincare map of a system with impulse effects is well defined and how orbital stability is decided.
  - Expand the event-time perturbation to first order to derive the saltation matrix and show the identity $\Xi f^- = f^+$.
  - Derive the impact map of a compass gait from angular-momentum conservation and show it is dissipative.
  - Find a passive limit cycle numerically and verify that the impact loss equals the gravitational input.
  - Explain the factorisation of the Poincare Jacobian into flow Jacobians and the saltation matrix.
tags: [legged-robots, hybrid-systems, limit-cycle, poincare-map, saltation-matrix, research]
---

# Hybrid dynamics and limit cycles

## Setup and notation

Walking is **not one continuous motion**: the state jumps whenever the support leg changes (an
impact), and between jumps smooth dynamics flow. So the equilibrium theory of
`c3-lyapunov-stability` cannot be used as written — there **is no equilibrium**. For a walking
robot, "stable" means stability of a periodic orbit (a limit cycle), and the tool that decides it
is the Poincare map.

Assumed: flows of ODEs and differentiability in the initial condition, the implicit function
theorem, eigenvalues and spectral radius, the impulsive contact model of `c2-contact-dynamics`,
and the stability definitions of `c3-lyapunov-stability`.

| Symbol | Meaning |
|---|---|
| $\dot x = f(x)$, $x \in \mathcal{D}$ | the continuous (stance) dynamics on a state region $\mathcal{D}$ |
| $\mathcal{G} = \{x : h(x) = 0,\ \nabla h^\top f(x) < 0\}$ | the guard — the surface on which the event happens |
| $R : \mathcal{G} \to \mathcal{D}$ | the reset map (impact plus leg relabelling) |
| $\varphi_t(x)$ | the flow of $f$; $\Phi(t) = \partial\varphi_t/\partial x$ is the flow Jacobian |
| $\Xi$ | the saltation matrix — first-order propagation of a perturbation through the event |
| $P : \Sigma \to \Sigma$ | the Poincare map, with $\Sigma$ the section just after the guard |
| $q = (\theta_{\mathrm s}, \theta_{\mathrm n})$ | stance and non-stance leg angles, measured from the **slope normal**, positive downhill |
| $\alpha$ | half the inter-leg angle at impact; on the guard $\theta_{\mathrm n} = -\theta_{\mathrm s} = -\alpha$ |
| $m, m_H, a, b$ | leg mass, hip mass, foot-to-leg-mass and leg-mass-to-hip distances; $\ell = a+b$ |
| $\gamma$ | the slope angle |

The running example is the **compass gait**: two legs of length $\ell$ pinned at the hip, each with
mass $m$, a hip mass $m_H$, point feet, and **no actuators**. Every number in this lesson was
computed with $m = 5$ kg, $m_H = 10$ kg, $a = b = 0.5$ m, $g = 9.81$ m/s² and
$\gamma = 0.05$ rad.

## Self-diagnosis before starting

This is the first lesson of the module, so check your footing first. **Prerequisite lessons are
not locked** — if you can do all of these, start here and skip the recommended prerequisites
(C1-C4). **If two or more block you**, the lesson in brackets is the faster route. Answers and
tolerances are given immediately.

1. For the linear map $z_{k+1} = Az_k$ with
   $A = \begin{bmatrix}0.5 & 1\\ 0 & -0.8\end{bmatrix}$, is the fixed point $z=0$ stable, and why?
   (`f0-linear-algebra`)
   **Answer**: the eigenvalues $0.5$ and $-0.8$ both have modulus below 1, so it is asymptotically
   stable. Tolerance $10^{-9}$.
2. For a point of mass $m$ at position $r$ moving with velocity $v$, what is its angular momentum
   about a point $P$ (in two dimensions)? (`f0-classical-mechanics`)
   **Answer**: $L_P = m\,(r-P)\times v = m[(r_x-P_x)v_y - (r_y-P_y)v_x]$.
3. Name one quantity that is conserved and one that is not in a perfectly plastic impact.
   (`c2-contact-dynamics`)
   **Answer**: angular momentum about any axis on which the impulse exerts no moment is conserved;
   kinetic energy is not (it decreases).
4. Given that solutions of $\dot x = f(x)$ are $C^1$ in their initial condition, what matrix
   differential equation does the flow Jacobian $\Phi(t) = \partial\varphi_t/\partial x$ satisfy?
   (`c3-contraction-incremental`)
   **Answer**: $\dot\Phi = \frac{\partial f}{\partial x}(\varphi_t(x))\,\Phi$ with $\Phi(0)=I$ (the
   variational equation).
5. What is the step length of a compass gait with half inter-leg angle $\alpha$ (in terms of $\ell$
   and $\alpha$)?
   **Answer**: $2\ell\sin\alpha$; with $\alpha = 0.2668212$ rad and $\ell = 1$ m that is
   $0.527333$ m (tolerance $10^{-6}$).

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the Poincare map and orbital stability) [D3]** — if a periodic orbit of period $T^\star$
  crosses the guard **transversally** ($\nabla h^\top f \ne 0$), the Poincare map $P$ on the
  section $\Sigma$ just after the guard is locally well defined and $C^1$, and at its fixed point
  $z^\star$
  $$
  \rho(DP(z^\star)) < 1 \iff \text{the periodic orbit is orbitally asymptotically stable}. \tag{1}
  $$
  The time direction (the orbit tangent) is **removed** by taking a section, so no eigenvalue 1
  survives in $DP$.
- **R2 (the saltation matrix) [D3]** — the first-order propagation of a perturbation through the
  event is $\delta x^+ = \Xi\,\delta x^-$ with
  $$
  \Xi = DR + \frac{\big(f^+ - DR\,f^-\big)\,\nabla h^\top}{\nabla h^\top f^-},
    \qquad f^- = f(x^-),\; f^+ = f\big(R(x^-)\big). \tag{2}
  $$
  The structural identity $\Xi f^- = f^+$ always holds (substitute and the fraction cancels). The
  second term of (2) exists because the two trajectories **reach the event at different times** —
  drop it and the answer is wrong at first order.
- **R3 (factorisation of the Poincare Jacobian) [D2]** — the Jacobian of one step factorises as
  $$
  DP = \Pi\,\Xi\,\Phi(T^\star)\,\iota \tag{3}
  $$
  where $\iota$ lifts section coordinates into the full state, $\Phi(T^\star)$ is the flow
  Jacobian of the stance phase, $\Xi$ is (2) and $\Pi$ projects back onto the section. So the
  stability of a step is **the product of how much the flow spreads and how much the impact
  folds**.
- **R4 (the impact map of the compass gait) [D2]** — the configuration $(\alpha,-\alpha)$ does not
  change at the impact; only the velocities jump. Conservation along the two axes on which the
  impulses exert no moment — **total angular momentum about the new stance foot** and **the
  angular momentum of the (new) swing leg about the hip** — gives the $2\times2$ linear system
  $$
  Q^+(\alpha)\,\dot q^+ = Q^-(\alpha)\,\dot q^- \tag{4}
  $$
  and relabelling the legs completes the reset map $R$. The map is **dissipative**: over
  $2\times10^4$ random guard states, $\max(T^+-T^-) = -6.43\cdot10^{-4}$ J $< 0$.
- **R5 (energy balance of passive walking, with numbers) [D2]** — on the limit cycle the impact
  loss of one step **exactly** equals the potential energy gained on the slope:
  $$
  T^- - T^+ = (2m+m_H)\,g\sin\gamma\cdot 2\ell\sin\alpha^\star. \tag{5}
  $$
  Numerically both sides are $5.17098115$ J, a relative gap of $4.8\cdot10^{-10}$. The fixed point
  is $z^\star = (\theta_{\mathrm s},\dot\theta_{\mathrm s},\dot\theta_{\mathrm n})
  = (-0.2668212224,\ 1.0839401305,\ 0.3980684049)$ with period $T^\star = 0.7324148$ s and step
  length $0.527333$ m, and the eigenvalues of $DP$ are $-0.158015 \pm 0.560266i$ and $0.13479$ —
  a spectral radius of $0.582123 < 1$, so the walker is **asymptotically stable with no
  actuators**.

## Derivation

### R2 — the saltation matrix: the event time is the whole story

Suppose the nominal trajectory meets the guard at time $t^\star$ at
$x^- := \varphi_{t^\star}(x_0)$ and jumps to $x^+ = R(x^-)$. The perturbed trajectory
$x_0 + \delta x_0$ meets the guard at a **different time** $t^\star + \delta t$. The comparison
must be made at the **same instant** (otherwise it is not even defined), so measure everything at
$t^\star$.

**Step 1 (first-order change of the event time).** Expand the condition that the perturbed
trajectory is on the guard, $h\big(\varphi_{t^\star+\delta t}(x_0+\delta x_0)\big) = 0$, writing
$\delta x^- := \Phi(t^\star)\delta x_0$:

$$
0 = \underbrace{h(x^-)}_{=0} + \nabla h^\top\big(\delta x^- + f^-\,\delta t\big) + O(2)
  \;\Longrightarrow\;
  \delta t = -\frac{\nabla h^\top \delta x^-}{\nabla h^\top f^-}. \tag{6}
$$

That the denominator is non-zero is the **transversality condition**, and where it fails is
grazing.

**Step 2 (state at the event).** The perturbed state **at the moment it touches the guard** is its
state at $t^\star$ flowed by $\delta t$:

$$
x^-_{\text{pert}} = x^- + \delta x^- + f^-\delta t + O(2).
$$

**Step 3 (through the reset).** Expanding the reset to first order,

$$
x^+_{\text{pert}} = R(x^-_{\text{pert}}) = x^+ + DR\big(\delta x^- + f^-\delta t\big) + O(2).
$$

**Step 4 (back to the nominal instant).** The perturbed trajectory jumped at
$t^\star + \delta t$, so to read its state at $t^\star$ we flow by $-\delta t$ under the
post-impact dynamics:

$$
x^+_{\text{pert}}\big|_{t^\star} = x^+ + DR\big(\delta x^- + f^-\delta t\big) - f^+\delta t + O(2).
$$

**Step 5 (collect).** Substituting $\delta t$ from (6) and collecting the coefficient of
$\delta x^-$,

$$
\delta x^+ = \left[DR - \big(DR f^- - f^+\big)\frac{\nabla h^\top}{\nabla h^\top f^-}\right]\delta x^-
  = \left[DR + \frac{(f^+ - DRf^-)\nabla h^\top}{\nabla h^\top f^-}\right]\delta x^-,
$$

which is (2). Substituting $\delta x^- = f^-$ cancels $\nabla h^\top f^-$ and gives
$\Xi f^- = f^+$ **exactly** — the first-order statement of the obvious fact that the orbit tangent
maps to the orbit tangent.

**Numerical check**: at the impact of the compass gait's limit cycle, (2) gives

$$
\Xi = \begin{bmatrix}
-0.210613 & 0.789387 & 0 & 0\\
0.668970 & -0.331030 & 0 & 0\\
-3.385796 & -1.140261 & 0.857958 & -0.099651\\
-7.030771 & -0.958656 & 0.477335 & -0.171592
\end{bmatrix} \tag{7}
$$

and shrinking the perturbation from $10^{-3}$ to $3\cdot10^{-5}$ while actually performing "flow to
the guard, reset, return to the nominal instant" gives an error proportional to $\delta^2$
(error/$\delta^2$ equal to $5.23, 7.17, 6.35, 6.17$ — a constant). Dropping the $\nabla h$ term and
using $\Xi \approx DR$ makes the error **first order** in $\delta$ in the same experiment.

**Where the assumptions break**: ⓐ as $\nabla h^\top f^- \to 0$ (grazing) (6) blows up — a step
whose foot **skims** the ground cannot be linearised by a saltation matrix. ⓑ if $R$ is not
differentiable (a friction transition, two contacts at once) there is no $DR$. ⓒ if a perturbation
changes the **order** of events (mode explosion) the first-order theory does not apply at all.

### R4 — the impact map of the compass gait (two angular momenta)

The stance dynamics come from the Lagrangian. With the stance foot at the origin in slope
coordinates ($x$ downhill, $y$ along the normal), the hip is at
$\ell(\sin\theta_{\mathrm s}, \cos\theta_{\mathrm s})$, the stance leg mass at
$a(\sin\theta_{\mathrm s},\cos\theta_{\mathrm s})$ and the swing leg mass a distance $b$ below the
hip. Gravity is $g(\sin\gamma, -\cos\gamma)$. Building $T-V$ and applying Euler-Lagrange gives
$M(q)\ddot q + N(q,\dot q) = 0$ with

$$
M(q) = \begin{bmatrix}
 (2a^2+2ab+b^2)m + (a+b)^2m_H & -bm(a+b)\cos(\theta_{\mathrm s}-\theta_{\mathrm n})\\
 -bm(a+b)\cos(\theta_{\mathrm s}-\theta_{\mathrm n}) & b^2m
\end{bmatrix} \tag{8}
$$

(the off-diagonal term is the coupling of the two legs, and $N$ contains centrifugal terms of the
form $\dot\theta^2\sin(\theta_{\mathrm s}-\theta_{\mathrm n})$ and gravity terms
$g\sin(\gamma+\theta)$; the expansion is problem P1).

**The impact.** The swing foot touches the slope when its height along the normal vanishes,
$\ell\cos\theta_{\mathrm s} - \ell\cos\theta_{\mathrm n} = 0$, so on the non-trivial branch
$\theta_{\mathrm n} = -\theta_{\mathrm s}$; the guard is

$$
h(q) = \theta_{\mathrm s} + \theta_{\mathrm n} = 0, \qquad \theta_{\mathrm s} = \alpha > 0 \tag{9}
$$

where $\alpha>0$ says the hip is downhill of the stance foot, i.e. a step was actually taken. The
impact is **instantaneous**, so the configuration does not change and only velocities jump. Two
conservation laws are used:

1. **Total angular momentum about the new stance foot (the impacting foot).** The impulse acting
   at that point has no moment about it, so the total angular momentum is conserved.
2. **The angular momentum about the hip of the (post-impact) swing leg.** The hip pin's impulse has
   no moment about the hip, and the foot impulse **does not act on that leg** (its foot is now in
   the air).

Writing each term as $L_P = \sum_i m_i (r_i - P)\times v_i$ and equating pre-impact (old frame,
configuration $(\alpha,-\alpha)$) with post-impact (new frame, configuration $(-\alpha,\alpha)$)
gives the $2\times2$ system (4), whose solution is
$\dot q^+ = Q^+(\alpha)^{-1}Q^-(\alpha)\,\dot q^-$. The only trap is **which body's momentum about
which point**: both laws must be written for the **same physical leg** before and after. (Get it
wrong and the identity map comes out — which is how one learns it.)

**Dissipativity check**: drawing $2\times10^4$ random states with $\alpha \in (0.02, 0.5)$ and
$\dot q \in [-3,3]^2$ and measuring $T^+ - T^-$ gives a maximum of $-6.43\cdot10^{-4}$ J, i.e.
**always negative**. The impact never creates energy — the minimal condition for the model to be
physical.

### R5 — the limit cycle and the energy balance

Take the section "just after the impact". The guard forces
$\theta_{\mathrm n} = -\theta_{\mathrm s}$, so the section is three-dimensional:
$z = (\theta_{\mathrm s}, \dot\theta_{\mathrm s}, \dot\theta_{\mathrm n})$. One step $P(z)$ is
ⓐ integrate the stance dynamics to the guard (9), ⓑ apply the impact map, ⓒ relabel the legs.

Solving $P(z)-z=0$ by Newton gives

$$
z^\star = (-0.2668212224,\ 1.0839401305,\ 0.3980684049), \qquad
  \lVert P(z^\star)-z^\star\rVert_\infty = 6.8\cdot10^{-14} \tag{10}
$$

with period $T^\star = 0.7324148$ s and step length $2\ell\sin\alpha^\star = 0.527333$ m. The
pre-impact state is $(0.266821222, -0.266821222, 1.468389728, 1.764917608)$.

**The energy balance.** The impact leaves the configuration unchanged, so the potential energy is
continuous and the loss is the difference of kinetic energies $T^- - T^+$. Over one step gravity
does work $(2m+m_H)g\sin\gamma\cdot 2\ell\sin\alpha^\star$ as the centre of mass descends by one
step length. On a limit cycle the two must agree — numerically

$$
T^- - T^+ = 5.17098115\ \text{J}, \qquad
(2m+m_H)g\sin\gamma\cdot2\ell\sin\alpha^\star = 5.17098115\ \text{J} \tag{11}
$$

with a relative gap of $4.8\cdot10^{-10}$. **This is the single strongest check of the equations of
motion and the impact map together**: if either is wrong, (11) does not hold.

**Stability.** Taking $DP(z^\star)$ by central differences ($h=10^{-6}$),

$$
DP = \begin{bmatrix}
-1.225306 & -0.549449 & 0.024991\\
2.862189 & 0.960473 & -0.066750\\
0.079840 & -1.128862 & 0.083592
\end{bmatrix},\quad
\operatorname{eig} = \{-0.158015\pm0.560266i,\ 0.134790\} \tag{12}
$$

with spectral radius $0.582123$. So **a passive walker descending a slope is asymptotically stable
without actuators**, and perturbations shrink by about a factor 0.58 per step (oscillating as they
shrink, since the eigenvalues are complex).

**Where the assumptions break**: ⓐ the spectral radius is a **local** verdict. The basin of
attraction can be very small (for passive walkers it is a few percent of the step angle), and no
number in this lesson says anything about its size. ⓑ increasing $\gamma$ produces period-doubling
to two-step and four-step gaits and then chaos (Goswami et al. 1998 §5). ⓒ if the assumptions of
point feet, a rigid floor and a frictionless instantaneous transition fail, the impact map itself
changes.

## Proof sketch

### R1 — existence of the Poincare map and orbital stability

**Hypotheses** H1: $f$ is $C^1$ on $\mathcal{D}$ and $R$ is $C^1$ near $\mathcal{G}$.
H2: the periodic orbit of period $T^\star$ crosses the guard **transversally**:
$\nabla h^\top f(x^-) \ne 0$. H3: the orbit meets the guard exactly once per period (the order of
events is fixed).
**Conclusion** C: near the post-guard section $\Sigma$, $P$ is a well-defined $C^1$ map, and the
periodic orbit through its fixed point $z^\star$ is orbitally asymptotically stable if and only if
$\rho(DP(z^\star))<1$.

**Strategy**: use the implicit function theorem to make the "time to reach the guard" a smooth
function of the state, and then use the ordinary stability theory of **discrete maps**.

1. **The arrival time is smooth.** $F(x, t) := h(\varphi_t(x))$ is $C^1$ with
   $\partial F/\partial t = \nabla h^\top f \ne 0$ (H2), so the implicit function theorem gives a
   unique $C^1$ function $t = \tau(x)$ near $x$ — the dwell time.
2. **Definition of the map.** Setting
   $P(z) = \Pi\,R\big(\varphi_{\tau(\iota z)}(\iota z)\big)$, H1 and H3 make $P$ a $C^1$ map, and
   the periodic orbit is a fixed point of it.
3. **Factorising $DP$.** Differentiating $\tau$ with (6) and applying the chain rule gives (3),
   $DP = \Pi\,\Xi\,\Phi(T^\star)\,\iota$. **This is where the eigenvalue 1 of the time direction
   disappears**: $\Phi(T^\star)$ has eigenvalue 1 along $f$, but that direction is not in the image
   of $\iota$ (the section cuts it away).
4. **Stability of a discrete map.** At a fixed point of $z_{k+1} = P(z_k)$ with $\rho(DP)<1$ there
   is a norm and a $\rho<\mu<1$ with
   $\lVert P(z)-z^\star\rVert \le \mu\lVert z-z^\star\rVert$ nearby (for any $\epsilon$ there is a
   norm with $\lVert A\rVert_\epsilon \le \rho(A)+\epsilon$), so $z_k \to z^\star$ geometrically.
   Conversely, if $\rho>1$ some solution diverges along that direction.
5. **From discrete to continuous.** With $z_k \to z^\star$ and the continuity of $\tau$ from step 1,
   the whole trajectory converges to the **set** that is the periodic orbit. The phase along the
   orbit does not converge — a trajectory can run on the same orbit slightly shifted in phase — so
   the conclusion is not "asymptotic stability" but **"orbital asymptotic stability"**.

**Remove a hypothesis**: without H2 (transversality) the implicit function theorem of step 1 does
not apply and $P$ may not be differentiable — at a grazing bifurcation entries of $DP$ diverge.
Without H3 (several events per period, or a perturbation that reorders events) $P$ becomes a
piecewise map and the first-order theory breaks. And this theorem **says nothing about the basin of
attraction** — which is an open problem of this lesson.

Technical steps omitted: differentiability of solutions in the initial condition (existence of the
variational equation) and the relation between spectral radius and induced norms. Westervelt et al.
ch.4, Grizzle et al. 2001 §III.

## Problem set

Six problems: two derivations, one proof, one numerical, one implementation and one paper problem.
Difficulty is ★ 15 min / ★★ 1 hour / ★★★ a day or more, and each states how much of the solution is
published.

**P1 (derivation, ★★, R4)** Derive the stance dynamics of the compass gait by the Lagrangian method
and write out the mass matrix (8) together with the matching $N(q,\dot q)$ componentwise. Explain
geometrically, in one sentence, why $\cos(\theta_{\mathrm s} - \theta_{\mathrm n})$ appears in the
off-diagonal term.
*Solution sketch*: write the hip position in terms of the stance angle, place the swing leg mass a
distance $b$ below the hip, and expand $T = \tfrac12\sum m_i |v_i|^2$. The off-diagonal term comes
from the inner product of the hip velocity with the swing leg's relative velocity, and that inner
product is the cosine of the angle between the legs. The gravity terms follow from projecting the
tilted gravity $(g\sin\gamma, -g\cos\gamma)$ onto each mass position.

**P2 (derivation, ★★, R2)** Derive the saltation matrix (2). In particular, say (i) why step 4,
returning the perturbed trajectory to the nominal event time, is needed, and (ii) what order the
error becomes in the perturbation size if that step is skipped. Then verify $\Xi f^- = f^+$ by
substitution.
*Solution sketch*: get the first-order event-time change from (6), expand the reset to first order,
then flow by $-\delta t$ under the post-impact dynamics. Skipping step 4 compares the two
trajectories at different instants, leaving a first-order error (as the numbers confirm). The
identity follows by putting $\delta x^- = f^-$, which makes the fraction equal to one.

**P3 (proof, ★★★, R1·R3)** Derive the factorisation (3) by the chain rule and use it to explain why
$DP$ has no eigenvalue 1 even though the flow Jacobian $\Phi(T^\star)$ has one along the orbit
tangent. How does the conclusion change if the section is taken on an arbitrary hyperplane in the
middle of the stance phase instead of "just after the impact"?
*Solution sketch*: strategy — write the derivative of $\tau(x)$ with (6) and differentiate
$P = \Pi R \varphi_\tau$. The tangent direction is not in the image of $\iota$, so it is excluded
from the spectrum of $DP$. A different section gives the same non-zero eigenvalues, because
changing the section is a change of coordinates — showing that is the exercise.

**P4 (numerical, ★, R5)** At $z^\star$ compute (a) the impact loss $T^- - T^+$ in joules, (b) the
gravitational input over one step in joules, and (c) the spectral radius of $DP$. Report all three
to six decimal places.
*Answers*: (a) $5.170981$ J, (b) $5.170981$ J (relative gap $4.8\cdot10^{-10}$), (c) $0.582123$.
Tolerance $10^{-6}$. Check: if (a) and (b) disagree, the equations of motion or the impact map are
wrong; (c) is the modulus of the complex pair $-0.158015 \pm 0.560266i$.

**P5 (implementation, ★★, R1·R2·R5)** Implement the Poincare map, find $z^\star$ and compute the
eigenvalues of $DP$. Then compute the saltation matrix at the same impact with (2) and verify
second-order convergence by shrinking the perturbation from $10^{-3}$ to $3\cdot10^{-5}$ in the
experiment "flow to the guard, reset, return to the nominal instant". Finally replace $\Xi$ by $DR$
and watch the order drop to one.
*Rubric*: passing requires (1) event detection accurate to about $10^{-12}$, by bisection or
`solve_ivp`'s events, (2) a residual below $10^{-10}$ at $z^\star$, (3) eigenvalues matching the
lesson to within $10^{-3}$, (4) error/$\delta^2$ staying constant when $\delta$ shrinks tenfold,
and (5) error/$\delta$ constant in the $DR$ version. Reporting the integrator and step size
alongside every number earns extra credit.

**P6 (paper, ★★, R1·R3)** Read §II-III of Grizzle, Abba & Plestan (2001) and write, in three
sentences each, (a) the list of assumptions the authors require to formulate a "system with impulse
effects", (b) how those map onto H1-H3 of this lesson, and (c) whether their stability test is the
same as our (1).
*Rubric*: passing requires finding the assumptions corresponding to transversality and a fixed
event order, and noting that their test is the linearisation of the Poincare map. Noticing that a
separate erratum was published the same year earns extra credit.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes and attack questions 4, 5, 6, 7 in the third.

1. **Grizzle, Abba & Plestan, "Asymptotically stable walking for biped robots: analysis via
   systems with impulse effects" (2001, IEEE T-AC)** — role: `seminal`.
   <https://doi.org/10.1109/9.898695> (§II, §III). An erratum appeared the same year
   (<https://doi.org/10.1109/TAC.2001.911439>) — read it alongside.
   Extra questions: ⓐ Which of the authors' assumptions do you expect to fail **first on
   hardware**? ⓑ Write a paragraph on what the paper does **not** guarantee (basin of attraction,
   three-dimensional walking, changing terrain).
2. **Garcia, Chatterjee, Ruina & Coleman, "The simplest walking model: stability, complexity, and
   scaling" (1998, ASME J. Biomech. Eng.)** — role: `seminal`.
   <https://doi.org/10.1115/1.2798313>
   Extra questions: ⓐ List what was discarded to make the model "simplest", and say which
   conclusion changes first if you restore one of them. ⓑ Can the scaling law they report be
   checked against our numbers at $\gamma=0.05$?
3. **Goswami, Thuilot & Espiau, "A study of the passive gait of a compass-like biped robot"
   (1998, IJRR)** — role: `standard`. <https://doi.org/10.1177/027836499801701202>
   (§3, §5). The source of this lesson's model and numbers.
   Extra questions: ⓐ What must be computed to reproduce the bifurcation route (period doubling to
   chaos) as $\gamma$ grows? ⓑ If their parameters differ from ours, which of our numbers change?

**The ten fixed questions**: (1) which problem under which assumptions (2) what exactly earlier
work could not do (3) the core idea in one equation (4) what is guaranteed and **what is not**
(5) independent and dependent variables and baselines, fairly tuned (6) do the metrics match the
claim, are variance and seeds reported (7) what is missing for reproduction (8) the first
assumption to doubt if the result is wrong (9) computational and memory complexity and real-time
feasibility (10) what you would change to go beyond it in a year.

## Reproduction task

**Tier R2 (re-implementation).** Budget: laptop CPU under ten minutes, numpy plus scipy. The target
is the compass gait of this lesson ($m=5$, $m_H=10$, $a=b=0.5$, $g=9.81$, $\gamma=0.05$) and there
is no input data. **Derive the equations of motion yourself** (a symbolic-differentiation package
is fine — (8) above was derived with sympy).

**Acceptance criteria (all four)**

1. **Model sanity**: ⓐ on the guard (9) the swing foot's height along the normal is below
   $10^{-12}$, and ⓑ for **every** one of $10^4$ random guard states with
   $\alpha \in (0.02,0.5)$ and $\dot q \in [-3,3]^2$, $T^+ - T^- \le 0$ (reference maximum:
   $-6.43\cdot10^{-4}$ J).
2. **The limit cycle**: find a fixed point with
   $\lVert P(z^\star)-z^\star\rVert_\infty < 10^{-10}$ that matches (10) componentwise to
   $10^{-6}$, and reproduce the period $0.7324148$ s and the step length $0.527333$ m to
   $10^{-5}$.
3. **Energy balance**: compute both sides of (11) and agree to a relative gap $< 10^{-6}$
   (reference $4.8\cdot10^{-10}$). If this fails, the model is wrong even when the values of
   criteria 2 and 4 look right.
4. **Eigenvalues and the saltation matrix**: ⓐ the eigenvalues of $DP$ match (12) to $10^{-3}$ and
   the spectral radius is $0.582123 \pm 10^{-3}$; ⓑ the $\Xi$ computed from (2) satisfies
   $\Xi f^- = f^+$ to $10^{-10}$; ⓒ for
   $\delta \in \{10^{-3}, 3\cdot10^{-4}, 10^{-4}, 3\cdot10^{-5}\}$ the ratio error/$\delta^2$ stays
   within one order of magnitude (reference $5.2$-$7.2$).

**Baselines**: ⓐ iterate the map 20 times from a random state near $z^\star$ — with spectral radius
0.58 the deviation must shrink by about $0.58^{20}\approx10^{-5}$ (an independent check of
stability); ⓑ the version with $\Xi$ replaced by $DR$, which must **fail** criterion 4ⓒ
(error/$\delta$ becomes constant instead); ⓒ the reference numbers (10)-(12).

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| The impact map looks like the identity | the angular momenta were not written for the **same physical leg about the same point** before and after | check that it is "the stance leg about the hip" before and "the swing leg about the hip" after |
| Criterion 3 is off by about 1% | the shift of the coordinate origin downhill at each step was ignored in the energy | measure the loss as the **difference of kinetic energies** and compute the gravitational input separately from the step length |
| The fixed point is never found | scuffing crossings of the guard were not filtered out | add $\theta_{\mathrm s} > 0.02$ and $\dot\theta_{\mathrm s} > 0$ to the event filter |
| The eigenvalues change between runs | the event time is less accurate than the difference step $h$ | tighten the event to $10^{-12}$ by bisection and keep $h=10^{-6}$ |
| The ratio in criterion 4ⓒ grows as $\delta$ shrinks | the perturbed trajectory was compared at **its own** event time (the return to the nominal instant is missing) | check whether the order is one — if so, step 4 of R2 is missing |

## Open problems

- **(open problem) Certifying the basin of attraction** — (1) is a local verdict, and the basin of a
  passive walker is genuinely small. Certifying a hybrid system's basin with SOS means handling the
  image of a set through the impact map, and the S-procedure used in R5 of
  `c3-lyapunov-stability` does not carry over because of the reset. The gap: mechanically
  verifiable lower bounds on the basin for systems with contact transitions — the open problems of
  `c2-contact-dynamics` and `c3-lyapunov-stability` meet here.
- **(open problem) Grazing and mode explosion** — $DP$ diverges where transversality (H2) fails,
  and on rough terrain the **order** of contacts changes from perturbation to perturbation. Current
  approaches: non-smooth bifurcation theory, and lifting the contact schedule into the optimisation
  variables as in
  [phase-based parameterisation (Winkler et al. 2018)](https://doi.org/10.1109/LRA.2018.2798285).
  The gap: a stability verdict that covers perturbations which reorder events.
- **(open problem) Three-dimensional walking and lateral instability** — eigenvalues inside the unit
  circle for a planar model often coexist with unstable lateral (roll and yaw) modes in three
  dimensions. Current approaches: 3D hybrid zero dynamics (`s3-hzd-gait-generation`) and foot
  placement for lateral stabilisation. The gap: a constructive way to lift a planar certificate to
  three dimensions **while preserving** it.
- **(open problem) The gap between the model and the hardware** — point feet, a rigid floor and
  instantaneous impacts all fail on real robots (finite sole area, ground compliance, finite-time
  impacts). Part of why learned locomotion walks better on hardware is exactly this gap
  ([Lee et al. 2020](https://doi.org/10.1126/scirobotics.abc5986)). The gap: a quantitative map
  from a given model error to how far it moves which eigenvalue — the same question returns from
  the other side in `s3-locomotion-rl`.

## Concept check

Take it with `rc quiz s3-hybrid-limit-cycles`. The quiz is **for concept checking only**; the real
work is the problem set and the reproduction task above (`lesson-standard.md` §4). Four questions
ask: why the saltation matrix differs from $DR$; whether $DP$ always has an eigenvalue 1; which
quantity must equal the impact loss on a limit cycle; and which two conservation laws give the
impact map.

## How to study this stage

1. **Start from the fact that there is no equilibrium (30 min)** — write a paragraph on why
   Lyapunov's equilibrium theory cannot be applied to walking as it stands. Then write precisely
   what "stability of a periodic orbit" means (the phase does not converge). Step 5 of R1 is that
   point.
2. **Derive the model by hand (120 min)** — P1. Go from the Lagrangian to (8) yourself. Even with
   symbolic differentiation, confirm the **geometric meaning of the off-diagonal term** by hand. An
   error here makes every later number meaningless.
3. **Get the impact map wrong once (60 min)** — if the angular momenta are not written for the same
   physical leg, the identity map comes out. Do that deliberately, watch criterion 1ⓑ
   (dissipativity) fail, and then fix it.
4. **Validate the model with the energy balance (40 min)** — pass criterion 3 of the reproduction
   task **before** criterion 2. It is how you learn whether the model is right before hunting for a
   fixed point.
5. **Fixed point and eigenvalues (90 min)** — tighten event detection to $10^{-12}$ and find
   $z^\star$ by Newton. Confirm from a trajectory that the eigenvalues are a complex pair
   (convergence with oscillation).
6. **Implement the saltation matrix twice (90 min)** — first with $DR$ alone, then with (2). Watch
   the error go from first to second order. **That comparison is the central experiment of this
   lesson.**
7. **Read the papers as a list of assumptions (150 min)** — tabulate Grizzle 2001's assumptions
   against H1-H3 of this lesson, and compare what Garcia 1998 discarded with what Goswami 1998
   added (the mass distribution). The one-page note per paper is **mandatory**.

**Passing bar**: you can derive (2) and (6) from memory, state the two conservation laws of the
impact map, and you have code meeting all four acceptance criteria plus one-page notes on the three
papers.
