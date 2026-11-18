---
id: s3-centroidal-mpc
lang: en
title: Centroidal dynamics and MPC walking
summary: >-
  The motion of a whole-body robot condensed into the six-dimensional momentum about its centre of
  mass (the centroidal dynamics), with what contact forces can and cannot do expressed through the
  centre of pressure (CoP, the ZMP). Under a constant-height assumption this gives the linear
  inverted pendulum and the divergent component of motion (the DCM, the capture point), and that
  unstable mode is why a linear MPC **without a terminal constraint reports success while the robot
  falls over** — shown numerically. It ends by deriving and measuring the exact limit on the
  disturbance that can be recovered without stepping.
objectives:
  - Derive the centroidal dynamics from whole-body Newton-Euler and explain why joint torques do not appear.
  - Derive the CoP/ZMP equation from the contact wrench and check the difference between point and flat feet numerically.
  - Derive the LIPM and the closed form of the DCM, and separate the unstable mode.
  - Pose the linear MPC as a QP and show why a terminal DCM constraint is needed for recursive feasibility.
  - Derive the bound $\omega p_{\max}$ on the recoverable disturbance without stepping and measure it with MPC experiments.
tags: [legged-robots, centroidal-dynamics, zmp, capture-point, mpc, research]
---

# Centroidal dynamics and MPC walking

## Setup and notation

The two previous lessons treated a two-degree-of-freedom walker **all the way through**. A real
robot has 20-30 degrees of freedom, and optimising all of them at every control tick is still
expensive. The practical compromise is **condensation**: view the robot as "one centre of mass plus
some contact forces", plan there, and let a whole-body controller (the next lesson) push that plan
down to the joints.

There is exactly one reason this condensation is legitimate — **joint torques cannot change the
total momentum.** Only external forces (gravity and contacts) can, so dynamics written in the
language of "centre of mass and contact forces" are **exact**, not an approximation. The
approximation enters later, with the LIPM.

Assumed: contact constraints and wrenches from `c2-constrained-dynamics`, the walking models of
`s3-hybrid-limit-cycles`, and the QP form of linear MPC (if you have not seen `c4-mpc`, this
lesson is a scaled-down version of it).

| Symbol | Meaning |
|---|---|
| $M$ | total mass; $r_{\mathrm{com}} = (x, z)$ is the centre of mass (planar) |
| $h_G = (l_G, L_G)$ | centroidal momentum — linear $l_G = M\dot r_{\mathrm{com}}$ and angular $L_G$ about the CoM |
| $f_i, p_i$ | the force and location of the $i$-th contact |
| $p_{\mathrm{zmp}}$ | the centre of pressure (CoP), which on flat ground is the ZMP |
| $p_{\max}$ | half-length of the support polygon (planar model) |
| $z$ | height of the centre of mass (constant in the LIPM) |
| $\omega = \sqrt{g/z}$ | the inverse time constant of the LIPM |
| $\xi = x + \dot x/\omega$ | the DCM (divergent component of motion) = the capture point |
| $N$, $\Delta t$ | MPC horizon length and time step |

The numbers use $z = 0.8$ m and $g = 9.81$ m/s² (so $\omega = 3.5017852590$ 1/s and
$1/\omega = 0.2855686246$ s), $p_{\max} = 0.05$ m, and an MPC with $N = 40$, $\Delta t = 0.05$ s.
The centroidal dynamics are verified on the compass gait of `s3-hybrid-limit-cycles` (point feet,
hip torque only).

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (centroidal dynamics) [D3]** — for any multibody robot,
  $$
  M\ddot r_{\mathrm{com}} = \sum_i f_i + Mg, \qquad
  \dot L_G = \sum_i (p_i - r_{\mathrm{com}}) \times f_i + \sum_i \tau_i \tag{1}
  $$
  and **joint torques appear nowhere** (they are internal). With point feet ($\tau_i = 0$),
  $\dot L_G$ is completely determined by the moment of the contact forces. Numerical check: on the
  compass gait, swinging the hip torque over $\pm60$ N·m leaves
  $\lvert \dot L_G - (p_{\text{foot}}-r_{\mathrm{com}})\times f_c\rvert \le 5.7\cdot10^{-14}$.
- **R2 (CoP and ZMP) [D3]** — solving the moment balance of the contact wrench in the plane gives
  $$
  p_{\mathrm{zmp}} = x + \frac{\dot L_G/M - z\,\ddot x}{\ddot z + g}. \tag{2}
  $$
  Unilateral contact (a foot cannot pull) forces
  $p_{\mathrm{zmp}} \in [\,-p_{\max}, p_{\max}]$. With point feet the CoP is **pinned to the foot**,
  so (2) *determines* $\dot L_G$ (numerically $\lvert p_{\mathrm{zmp}}\rvert \le 4.7\cdot10^{-15}$).
  A flat foot buys a **margin** of size $p_{\max}$, and that margin is what the rest of this lesson
  is about.
- **R3 (LIPM and DCM) [D2]** — with $z$ constant and $\dot L_G = 0$, (2) linearises to
  $$
  \ddot x = \omega^2\,(x - p_{\mathrm{zmp}}), \qquad \omega = \sqrt{g/z} \tag{3}
  $$
  and $\xi := x + \dot x/\omega$ extracts **only the unstable mode**:
  $$
  \dot\xi = \omega\,(\xi - p_{\mathrm{zmp}}),
  \qquad
  \xi(t) = p + (\xi_0 - p)e^{\omega t}\ \ (p\ \text{constant}). \tag{4}
  $$
  (Verified numerically to $10^{-16}$.) The complementary component $x - \xi$ converges **on its
  own** like $e^{-\omega t}$, so walking control reduces to handling $\xi$ alone.
- **R4 (linear MPC and recursive feasibility) [D2]** — discretising (4) with step $\Delta t$ gives
  $\xi_{k+1} = e^{\omega\Delta t}\xi_k + (1-e^{\omega\Delta t})p_k$, and minimising a cost subject to
  $\lvert p_k\rvert \le p_{\max}$ is a QP. **Because $e^{\omega\Delta t} > 1$, without a terminal
  constraint the QP only reduces the cost inside the horizon and abandons what follows**: under a
  disturbance of $\Delta v = 0.3$ m/s the QP returns an "optimal" solution whose
  $\lvert\xi_N\rvert$ at the end of the horizon is $39.3$ m. Adding the terminal constraint
  $\lvert\xi_N\rvert \le \epsilon$ makes it report **infeasible** for the same disturbance, which is
  the honest answer.
- **R5 (the limit of recovery without stepping) [D2]** — by (4), shrinking $\xi$ requires
  $p > \xi$, and $p \le p_{\max}$, so recovery without changing the foot position is possible
  exactly when
  $$
  \lvert \xi \rvert < p_{\max} \;\Longleftrightarrow\;
  \lvert \Delta v \rvert < \omega\,p_{\max} \quad(\text{for a push from rest}). \tag{5}
  $$
  Numerically $\omega p_{\max} = 0.17508926$ m/s, and bisecting on MPC feasibility measures the
  threshold at $0.17493343$ m/s (a relative difference of $0.09\%$, from discretisation and the
  terminal tolerance). This is the quantitative form of "**if the capture point leaves the support
  polygon you must move a foot**".

## Derivation

### R1 — centroidal dynamics: why joint torques disappear

View the robot as a collection of rigid bodies $i = 1,\dots,n$ and **add up** every body's
Newton-Euler equation. Internal forces (what the joints exchange) cancel in pairs by action and
reaction, so only external forces survive:

$$
\sum_i m_i \ddot r_i = \sum_j f_j + Mg
\;\Longrightarrow\;
M\ddot r_{\mathrm{com}} = \sum_j f_j + Mg,
$$

using the definition $r_{\mathrm{com}} = \frac1M\sum m_i r_i$. Collect angular momentum **about the
centre of mass**. Differentiating
$L_G = \sum_i \big[I_i\omega_i + m_i (r_i - r_{\mathrm{com}})\times \dot r_i\big]$,

$$
\dot L_G = \sum_i \big[I_i\dot\omega_i + m_i (r_i-r_{\mathrm{com}})\times\ddot r_i\big]
  + \underbrace{\sum_i m_i(\dot r_i - \dot r_{\mathrm{com}})\times\dot r_i}_{=\,0}
$$

(the last term vanishes by $\sum m_i \dot r_i \times \dot r_i = 0$ and
$\dot r_{\mathrm{com}}\times M\dot r_{\mathrm{com}} = 0$). Substituting each body's Euler equation
and cancelling internal moments gives (1). **Gravity exerts no moment about the centre of mass**
($\sum m_i(r_i-r_{\mathrm{com}})\times g = 0$) — which is why the centre of mass is the reference
point to choose.

**Numerical check (point feet)**: drawing $(q,\dot q)$ and a hip torque $u \in [-60,60]$ N·m at
random 3000 times on the compass gait, then ⓐ solving the dynamics for $\ddot q$, ⓑ computing $L_G$
and $\dot L_G$ directly and ⓒ comparing with the moment of the contact force
$f_c = M(\ddot r_{\mathrm{com}} - g)$ about the foot, gives a maximum difference of
$5.7\cdot10^{-14}$. Recomputing $\dot L_G$ by finite differences agrees to $5.7\cdot10^{-9}$ (the
difference error). **However the torque is swung, the identity does not move.**

**Where the assumptions break**: with an ankle torque (a flat foot with an actuated ankle)
$\sum\tau_i \ne 0$ and an input enters the second equation of (1) — that is why flat-footed robots
are easier than point-footed ones, and it appears in (2) as $p_{\max}$. Also, (1) assumes **the
contact locations are known**. Slip and terrain error enter as uncertainty in $p_i$, which the
centroidal plan does not see — the subject of `s3-dynamic-maneuvers`.

### R2 — the CoP: the limit on the moment contact can produce

Write the contact wrench as "a force $f$ at one point $p$ plus a moment $m_p$ about that point", and
define the **CoP** as the point where $m_p = 0$ (flat ground, ignoring the vertical moment). Then
the second equation of (1) is

$$
\dot L_G = (p - r_{\mathrm{com}}) \times f, \qquad f = M(\ddot r_{\mathrm{com}} - g)
$$

and substituting the planar components $p = (p_{\mathrm{zmp}}, 0)$, $r_{\mathrm{com}} = (x,z)$ and
$f = (M\ddot x,\ M(\ddot z + g))$ gives

$$
\dot L_G = (p_{\mathrm{zmp}} - x)\,M(\ddot z+g) + z\,M\ddot x
$$

which rearranges into (2). **Unilateral contact** ($f_z \ge 0$: the foot cannot pull on the ground)
confines the CoP to the sole, so (2) is a **constraint** defining the set of achievable
$(\ddot x, \dot L_G)$.

- **Point foot**: the support polygon is a single point, so $p_{\mathrm{zmp}}$ is pinned to the foot
  and (2) **computes** $\dot L_G$ — there is no freedom. Numerically
  $\lvert p_{\mathrm{zmp}}\rvert \le 4.7\cdot10^{-15}$, glued to the foot (compass gait, random
  torques).
- **Flat foot**: $p_{\mathrm{zmp}}$ may be chosen in $[-p_{\max},p_{\max}]$. That **one interval**
  is the input of walking control.

**Where the assumptions break**: ⓐ on sloped or uneven terrain the "support polygon" is not a planar
polygon and the friction cone must be included (the contact wrench cone,
`c2-contact-dynamics`). ⓑ with several contacts the CoP is a weighted average of the individual
contact forces, so a CoP inside the polygon is compatible with an **individual** force exceeding its
friction limit — the CoP condition is **only necessary**. That fact is what separates flat-foot ZMP
walking from multi-contact MPC (Di Carlo et al. 2018 keep the contact forces as variables).

### R3 — LIPM and DCM: peeling off the unstable mode

Put two assumptions into (2): $z$ constant ($\ddot z = 0$) and $\dot L_G = 0$. Then
$p_{\mathrm{zmp}} = x - z\ddot x/g$, which is (3). The eigenvalues of this linear system are
$\pm\omega$ — **one of them is unstable**. Choose a coordinate for the unstable mode:

$$
\xi := x + \frac{\dot x}{\omega}
\;\Longrightarrow\;
\dot\xi = \dot x + \frac{\ddot x}{\omega} = \dot x + \omega(x - p) = \omega\left(x + \frac{\dot x}{\omega} - p\right)
 = \omega(\xi - p),
$$

the first equation of (4). The opposite combination $\eta := x - \dot x/\omega$ obeys
$\dot\eta = -\omega(\eta - p)$ and **converges by itself**. So in coordinates $(\xi,\eta)$ walking
control is the problem of keeping $\xi$ inside the support polygon; $\eta$ can be left alone.

When $p$ is piecewise constant, (4) solves in **closed form**:
$\xi(t) = p + (\xi_0-p)e^{\omega t}$. Numerical check: over 2000 random $(x,\dot x,p,\Delta t)$,
propagating with the exact LIPM solution and comparing with (4) gives a maximum difference of
$4.4\cdot10^{-16}$.

**The names of $\xi$**: divergent component of motion (DCM), capture point, instantaneous capture
point — the same quantity. Physically: **if you put your foot at $\xi$ right now, the robot comes
to rest (within the LIPM)**. Setting $p = \xi$ makes $\dot\xi = 0$ in (4), so $\xi$ **stays where it
is** — it does not shrink. To shrink it, $p$ must go **beyond** $\xi$, and the available margin is
$p_{\max}$. That one sentence is R5.

**Where the assumptions break**: $\dot L_G = 0$ and $\ddot z = 0$ are **choices**, not facts.
Swinging the arms or bending the knees breaks both, and then (3) is wrong — though (2) remains
exact. The practical order is "plan with the LIPM, and let the whole-body controller **make**
$\dot L_G$ zero", and that whole-body controller is the next lesson.

### R4 and R5 — MPC, the terminal constraint, and the recovery limit

Discretise (4) with step $\Delta t$ (with $p$ constant on each interval):

$$
\xi_{k+1} = a\,\xi_k + (1-a)\,p_k, \qquad a := e^{\omega\Delta t} > 1. \tag{6}
$$

The MPC is the QP that minimises $\sum_{k=1}^{N}\xi_k^2 + \rho\sum_k p_k^2$ subject to
$\lvert p_k\rvert\le p_{\max}$. The trouble is $a>1$: reducing $\xi_k$ **inside** the horizon and
not diverging **after** it are different demands.

**Experiment (no terminal constraint)**: for a push of $\Delta v = 0.3$ m/s
($\xi_0 = 0.08567$ m $> p_{\max}$) the QP returns "optimal" with a finite cost. And the DCM at the
end of that solution's horizon is $\lvert\xi_N\rvert = 39.307468$ m — **the QP succeeded and the
robot fell over**. Adding the terminal constraint $\lvert\xi_N\rvert\le10^{-3}$ makes the QP report
**infeasible** for the same push, which is the honest answer: that disturbance cannot be recovered
without stepping.

**Deriving the recovery limit.** For $\lvert\xi\rvert$ to shrink in (4), $p$ must lie **further out**
than $\xi$ (checking signs). Since $\lvert p\rvert\le p_{\max}$, the condition
$\lvert\xi\rvert < p_{\max}$ is necessary — and sufficient, since the constant choice
$p = p_{\max}\operatorname{sign}\xi$ drives $\xi\to0$ in finite time. A push $\Delta v$ from rest
produces $\xi_0 = \Delta v/\omega$, which gives (5). Numerically, bisecting on MPC feasibility
measures the threshold at $0.17493343$ m/s against $\omega p_{\max} = 0.17508926$ m/s, a difference
of $0.09\%$ (explained by $\Delta t=0.05$ s and the terminal tolerance $10^{-3}$).

| $\Delta v$ (m/s) | $\xi_0$ (m) | QP with terminal constraint |
|---|---|---|
| 0.050 | 0.01428 | feasible |
| 0.150 | 0.04284 | feasible |
| 0.174 | 0.04969 | feasible |
| **0.176** | **0.05026** | **infeasible** |
| 0.300 | 0.08567 | infeasible |

**Where the assumptions break**: (5) presumes **no stepping**. Moving a foot shifts the support
polygon, so the recoverable set becomes much larger — that is the contact-schedule optimisation of
`s3-dynamic-maneuvers`. And (5) is a statement inside the LIPM: swinging the arms
($\dot L_G \ne 0$) and bending the knees ($\ddot z \ne 0$) buy extra margin through (2). That is why
humans use both.

## Proof sketch

### R4 — why a terminal constraint gives recursive feasibility

**Hypotheses** H1: (6) holds with $a>1$. H2: $\lvert p_k\rvert\le p_{\max}$. H3: the terminal set is
$\mathcal{X}_f = \{\lvert\xi\rvert\le\epsilon\}$ with $\epsilon < p_{\max}$. H4: $\mathcal{X}_f$ is
**control invariant** — from $\lvert\xi\rvert\le\epsilon$ some $\lvert p\rvert\le p_{\max}$ keeps
$\lvert\xi^+\rvert\le\epsilon$.
**Conclusion** C: if the QP is feasible at time $k$ it is feasible at $k+1$, and the closed loop
converges to $\mathcal{X}_f$.

**Strategy**: the standard MPC argument (`c4-mpc`), where the only real work is **checking** H4.

1. **Splicing the tail.** The optimal solution at $k$, $(p_k^\star,\dots,p_{k+N-1}^\star)$, satisfies
   $\xi_{k+N}\in\mathcal{X}_f$. At $k+1$, reuse its tail and **append the one input H4 provides**.
   That candidate satisfies (6), H2 and H3, so the QP at $k+1$ is feasible.
2. **Checking H4.** In (6), $\xi^+ = a\xi + (1-a)p$ with $a>1$, so $p = \xi$ gives $\xi^+ = \xi$ (a
   stand-still) while $p = p_{\max}\operatorname{sign}\xi$ gives
   $\lvert\xi^+\rvert = \lvert a\xi - (a-1)p_{\max}\operatorname{sign}\xi\rvert$, which **shrinks**
   whenever $\lvert\xi\rvert < p_{\max}$. So any $\mathcal{X}_f$ with $\epsilon < p_{\max}$ is
   control invariant.
3. **Convergence.** Using the optimal cost as a Lyapunov function, the candidate of step 1 makes the
   cost non-increasing, and since the cost contains $\sum\xi_k^2$ we get
   $\xi_k\to\mathcal{X}_f$ (R3 of `c3-lyapunov-stability` applied to a discrete map).

**Remove a hypothesis**: without H3 (the terminal constraint), the tail splice of step 1 guarantees
nothing about $\xi_{k+N}$ and, because $a>1$, the state **diverges beyond the horizon** — the
$39.3$ m of the experiment is that picture. If H4 fails ($\epsilon \ge p_{\max}$) the terminal set
itself is a promise that cannot be kept. Dropping H2 (an unbounded support polygon) makes the
problem trivial — all the difficulty of walking control comes from H2.

Technical steps omitted: the variant using a terminal cost (a $P$-weighted terminal cost instead of
a terminal set) and its equivalence, the theorem in `c4-mpc`; and the condition under which the
discretisation error of (6) does not destroy recursive feasibility (robust MPC).

## Problem set

Six problems: two derivations, one proof, one numerical, one implementation and one counterexample.

**P1 (derivation, ★★, R1·R2)** Derive (2) from (1). Mark where you use the step of writing the
contact wrench at the CoP and where you use the fact that gravity exerts no moment about the centre
of mass. Then write how (2) changes for a flat foot with an ankle torque $\tau_a$.
*Solution sketch*: put $f = M(\ddot r_{\mathrm{com}} - g)$ into
$\dot L_G = (p - r_{\mathrm{com}}) \times f$ and expand in planar components. The cancellation of
gravity's moment comes from defining $L_G$ about the centre of mass. With an ankle torque a
$+\tau_a$ appears on the right and shifts $p_{\mathrm{zmp}}$ by
$\tau_a/(M(\ddot z+g))$ — the margin a flat foot provides can also be bought with torque.

**P2 (derivation, ★★, R3)** Change coordinates to $\xi = x + \dot x/\omega$ and
$\eta = x - \dot x/\omega$ to split (3) into two first-order equations. Explain, with the numerical
value of $1/\omega$, why the $\eta$ component of the initial condition is negligible on the time
scale of a step.
*Solution sketch*: the eigenvectors of $[[0,1],[\omega^2,0]]$ are $(1,\pm\omega)$ and $\xi,\eta$ are
those coordinates. $\eta$ decays like $e^{-\omega t}$ and $1/\omega = 0.2856$ s, so within one step
(0.5-0.8 s) it is down by more than $e^{-2}$. That is why walking control handles only $\xi$.

**P3 (proof, ★★★, R4·R5)** Prove that the terminal set $\mathcal{X}_f = \{\lvert\xi\rvert\le\epsilon\}$
is control invariant when $\epsilon < p_{\max}$, and use it to prove recursive feasibility. Then show
what breaks if $\epsilon \ge p_{\max}$.
*Solution sketch*: strategy — put $p = p_{\max}\operatorname{sign}(\xi)$ into (6) to show
$\lvert\xi^+\rvert < \lvert\xi\rvert$ (which needs $a > 1$), then propagate feasibility by splicing
the tail. If $\epsilon \ge p_{\max}$ then $\mathcal{X}_f$ contains states with
$\lvert\xi\rvert > p_{\max}$, and from those no $p$ can shrink $\lvert\xi\rvert$, so invariance
fails.

**P4 (numerical, ★, R3·R5)** With $z = 0.8$ m, $g = 9.81$ m/s² and $p_{\max} = 0.05$ m, find
(a) $\omega$, (b) $1/\omega$, (c) the largest push velocity recoverable from rest without stepping,
and (d) the $\xi$ immediately after that push.
*Answers*: (a) $\omega = 3.5017852590$ 1/s, (b) $0.2855686246$ s, (c)
$\omega p_{\max} = 0.17508926$ m/s, (d) $\xi = \Delta v/\omega = p_{\max} = 0.05$ m. Tolerance
$10^{-6}$. Check: bisecting on MPC feasibility measures $0.17493343$ m/s, a relative difference of
$0.09\%$ (discretisation and the terminal tolerance).

**P5 (implementation, ★★, R4·R5)** Implement the linear MPC of (6) as a QP and pass the four
acceptance criteria of the reproduction task. Then vary the horizon $N$ over 10, 20, 40, 80 and
tabulate (a) the measured threshold and (b) $\lvert\xi_N\rvert$ for the version without a terminal
constraint, and discuss whether increasing $N$ can replace the terminal constraint.
*Rubric*: passing requires (1) the measured threshold approaching $\omega p_{\max}$ monotonically in
$N$, (2) showing $\lvert\xi_N\rvert$ of the unconstrained version growing exponentially in $N$, and
(3) noting that a "long enough horizon" approximates the terminal constraint but creates a
conditioning problem of order $e^{\omega N\Delta t}$. Report the solver and tolerances.

**P6 (counterexample, ★★, R3·R4)** (a) Show with (4) that $p = \xi$ (the "intuitive" controller that
puts the CoP at the capture point) does not reduce $\xi$, and confirm numerically. (b) Reproduce the
case where an MPC without a terminal constraint "succeeds" while the robot falls over, and write why
a design cannot be judged by its cost function alone.
*Rubric*: passing requires (a) $\dot\xi = 0$ at $p = \xi$, so the DCM stays put and does not
converge; (b) showing solver status "optimal" at $\Delta v = 0.3$ m/s with
$\lvert\xi_N\rvert = 39.3$ m, contrasted with "infeasible" once the terminal constraint is added.

## Paper reading

**Two must-reads plus two recommended.** Write a one-page note on each with the ten fixed questions
(`lesson-standard.md` §5).

1. **Kajita et al., "Biped walking pattern generation by using preview control of zero-moment
   point" (2003, ICRA)** — role: `seminal`. <https://doi.org/10.1109/ROBOT.2003.1241826>
   (§II, §III). Preview control tracking the ZMP is in effect "a linear MPC that sees the future".
   Extra questions: ⓐ How do the preview gains relate to our MPC of (6) — are they the same when
   there are no constraints? ⓑ Where do the authors use $\dot L_G = 0$ and $\ddot z = 0$, and what do
   they do on hardware when those assumptions fail?
2. **Di Carlo et al., "Dynamic locomotion in the MIT Cheetah 3 through convex model-predictive
   control" (2018, IROS)** — role: `standard`.
   <https://doi.org/10.1109/IROS.2018.8594448> (§III, §IV). A centroidal MPC that keeps the contact
   forces as **direct** variables.
   Extra questions: ⓐ How does using friction cones and force bounds instead of a CoP constraint
   resolve the "only necessary" problem of R2? ⓑ What did the authors give up to keep the problem
   convex (the angular momentum term, the contact schedule)?
3. **Pratt et al., "Capture Point: a step toward humanoid push recovery" (2006, Humanoids)**
   — role: `recommended`. <https://doi.org/10.1109/ICHR.2006.321385> — the origin of (5).
4. **Orin, Goswami & Lee, "Centroidal dynamics of a humanoid robot" (2013, Autonomous Robots)**
   — role: `recommended`. <https://doi.org/10.1007/s10514-013-9341-4> (§2, §4) — the structure and
   computation of the centroidal momentum matrix $A_G(q)$.

**The ten fixed questions**: (1) which problem under which assumptions (2) what exactly earlier
work could not do (3) the core idea in one equation (4) what is guaranteed and **what is not**
(5) independent and dependent variables and baselines, fairly tuned (6) do the metrics match the
claim, are variance and seeds reported (7) what is missing for reproduction (8) the first
assumption to doubt if the result is wrong (9) computational and memory complexity and real-time
feasibility (10) what you would change to go beyond it in a year.

## Reproduction task

**Tier R2 (re-implementation).** Budget: laptop CPU under ten minutes, numpy plus one QP solver.
The targets are ⓐ the compass gait of `s3-hybrid-limit-cycles` (criterion 1) and ⓑ the LIPM
($z=0.8$ m, $p_{\max}=0.05$ m, $N=40$, $\Delta t=0.05$ s) (criteria 2-4). There is no input data.

**Acceptance criteria (all four)**

1. **Centroidal dynamics and the CoP**: over $10^3$ random $(q,\dot q,u)$ with
   $\lvert u\rvert\le60$, ⓐ
   $\lvert \dot L_G - (p_{\text{foot}}-r_{\mathrm{com}})\times f_c\rvert < 10^{-10}$
   (reference $5.7\cdot10^{-14}$), ⓑ the $p_{\mathrm{zmp}}$ of (2) satisfies
   $\lvert p_{\mathrm{zmp}}\rvert < 10^{-12}$ (it must sit on the foot; reference
   $4.7\cdot10^{-15}$), and ⓒ recomputing $\dot L_G$ by finite differences agrees to $10^{-7}$
   (reference $5.7\cdot10^{-9}$).
2. **The DCM closed form**: over $10^3$ random $(x,\dot x,p,\Delta t)$ the difference between (4) and
   the exact LIPM solution is $< 10^{-12}$ (reference $4.4\cdot10^{-16}$). Report
   $\omega = 3.5017852590$ and $1/\omega = 0.2855686246$ as well.
3. **The recovery threshold**: bisect on the feasibility of the MPC with a terminal constraint to
   obtain $\Delta v^\star$, matching $\omega p_{\max} = 0.17508926$ m/s to **within 1% relative**
   (reference $0.17493343$, a difference of $0.09\%$). Show feasibility at $\Delta v = 0.174$ and
   infeasibility at $0.176$.
4. **The effect of the terminal constraint**: at $\Delta v = 0.3$ m/s, ⓐ show that the QP without the
   terminal constraint reports "optimal" while $\lvert\xi_N\rvert > 1$ m (reference $39.3$ m) and
   ⓑ contrast it with the same QP becoming **infeasible** once the terminal constraint is added.
   Report the solver status verbatim in both cases.

**Baselines**: ⓐ holding the CoP at the centre of the polygon ($p\equiv0$) — $\xi$ must diverge like
$e^{\omega t}$; ⓑ $p = \xi$ (the intuitive capture-point controller) — show that $\xi$ **stays put
instead of shrinking**; ⓒ the numbers in the text.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| Criterion 1ⓐ is off by $O(10)$ | a base (ankle) joint torque was treated as internal — an actuated ankle is an **external** moment | confirm the model is point-footed (hip torque only); actuating the pin leaves a $\tau$ in (1) |
| The $p_{\mathrm{zmp}}$ of criterion 1ⓑ is $O(10)$ | the sign of the $\dot L_G$ term — it is $p = x + (\dot L_G/M - z\ddot x)/(\ddot z+g)$ | fix the sign by requiring zero on a point foot |
| The DCM comparison is at the $10^{-3}$ level | the LIPM was integrated with Euler | use the exact $\cosh/\sinh$ solution, or shrink $\Delta t$ and confirm second-order convergence |
| The measured threshold is **above** $\omega p_{\max}$ | the terminal tolerance $\epsilon$ is too large ($\epsilon \gtrsim p_{\max}$) | tighten $\epsilon$ to $10^{-3}$ and increase $N$ |
| The QP is feasible for every disturbance | no terminal constraint, or no bound on $p$ | print both $\lvert p_k\rvert\le p_{\max}$ and $\lvert\xi_N\rvert\le\epsilon$ |

## Open problems

- **(open problem) Quantifying recovery that uses angular momentum** — (5) is the limit under
  $\dot L_G = 0$. Humans beat it by swinging their arms to make $\dot L_G \ne 0$. Equation (2)
  describes that margin exactly, but computing the recoverable set **including arm joint limits and
  whole-body feasibility** remains expensive. The gap: a real-time approximation of the recoverable
  set over the whole body.
- **(open problem) Centroidal MPC with the contact schedule as a variable** — Di Carlo et al. 2018
  **fix** the schedule to stay convex. Making it a variable turns the problem mixed-integer and
  breaks real-time. Current approaches: phase-based parameterisation
  ([Winkler et al. 2018](https://doi.org/10.1109/LRA.2018.2798285)), differentiable relaxations.
  The gap: a formulation that allows schedule changes within real time while guaranteeing
  feasibility — met again in `s3-dynamic-maneuvers`.
- **(open problem) The cost of condensation** — a centroidal MPC knows nothing of whole-body
  kinematics or torque limits, so on hardware a centroidal plan can turn out **infeasible** for the
  whole-body controller. The gap: conditions at the centroidal stage (conservative but tight) that
  guarantee whole-body feasibility. This connects directly to the QP feasibility of the next lesson,
  `s3-whole-body-control`.
- **(open problem) Model error and robust MPC** — when $z$ is not constant and contact locations
  carry error, the recursive feasibility of (6) is not guaranteed. Current approaches: tube MPC (the
  same tool as the tube bound of `c3-contraction-incremental`), scenario MPC. The gap: tube
  estimates tight enough to be useful in walking.

## Concept check

Take it with `rc quiz s3-centroidal-mpc`. The quiz is **for concept checking only**; the real work
is the problem set and the reproduction task above (`lesson-standard.md` §4). Four questions ask:
why joint torques do not appear in the centroidal dynamics; the definition of the DCM; whether
putting the CoP at the capture point makes the DCM converge; and the typical symptom of a linear MPC
without a terminal DCM constraint.

## How to study this stage

1. **Write down what is exact and what is an approximation (30 min)** — (1) and (2) are **exact**;
   (3) is an **approximation**. Without that distinction written down first, you cannot later tell
   which conclusion came from a modelling assumption.
2. **Verify the centroidal dynamics on a point foot (60 min)** — criterion 1 of the reproduction
   task. Seeing the identity hold while the torque is swung is the starting point of this lesson.
   Then confirm that adding an actuated ankle breaks it.
3. **Fix the sign of the CoP equation yourself (40 min)** — derive (2) and calibrate the sign by
   requiring $p_{\mathrm{zmp}}=0$ on a point foot. The first two rows of the diagnosis table are
   exactly those mistakes.
4. **Split the DCM by hand (40 min)** — P2. Seeing it as an eigenvector coordinate makes "why only
   $\xi$ matters" visible in the formula. Remember the number $1/\omega = 0.2856$ s.
5. **Run the MPC twice (90 min)** — without and with the terminal constraint. See the $39.3$ m
   yourself. The lesson that **a design cannot be judged by its cost function** only sticks through
   that number.
6. **Measure the recovery limit (60 min)** — criterion 3. Bisect to $0.1749$ m/s and compare with
   $\omega p_{\max}$. Being able to explain the difference ($\Delta t$, $\epsilon$) is the passing
   bar.
7. **Read the papers for "what is kept as a variable" (150 min)** — Kajita 2003 keeps the ZMP,
   Di Carlo 2018 the contact forces. Tabulate what that choice does to the constraints (unilateral,
   friction) and to convexity.

**Passing bar**: you can derive (1), (2) and (4) from memory, say why $p=\xi$ is not enough, and you
have code meeting all four acceptance criteria plus the paper notes.
