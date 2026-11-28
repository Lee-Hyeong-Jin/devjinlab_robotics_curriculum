---
id: s3-hzd-gait-generation
lang: en
title: Hybrid zero dynamics and gait generation
summary: >-
  Underactuated bipedal walking treated as "tie the degrees of freedom together with virtual
  constraints and design the one that is left". The reduction of the dynamics to two dimensions on
  the zero dynamics surface is derived, and the condition that makes that surface invariant
  **through the impact** (the H of HZD) is used as a design condition. The reduced dynamics turn
  out to be a one-dimensional affine return map, so the stability test collapses to the single line
  $\delta_{\mathrm{zero}}^2 < 1$ — and that prediction is compared with the Poincare eigenvalue of
  the full four-state model to eight digits.
objectives:
  - Derive the relative degree of the output and the zero dynamics surface from a virtual constraint, and count the surface's dimension.
  - Translate the impact-invariance condition $\Delta(S\cap Z)\subset Z$ into boundary conditions on the virtual constraint.
  - Derive the one-dimensional affine return map from the fact that angular momentum about the stance foot is unaffected by the actuator.
  - Separate the existence condition $\zeta^\star>0$ from the stability condition $\delta_{\mathrm{zero}}^2<1$ and explain both.
  - Compare the reduced model's prediction with the full model's Poincare eigenvalues and name the cause of any mismatch.
tags: [legged-robots, hybrid-zero-dynamics, virtual-constraints, underactuated, research]
---

# Hybrid zero dynamics and gait generation

## Setup and notation

`s3-hybrid-limit-cycles` decided the stability of a **given** gait. This lesson **designs** one.
The difficulty is underactuation: with point feet there is no torque at the ground, so there are
fewer actuators than degrees of freedom, and the strategy "put every joint on a desired trajectory"
is impossible from the start.

The HZD answer has two parts: ⓐ tie the joints together with as many **virtual constraints** as
there are actuators, reducing the system to one degree of freedom, and ⓑ **accept** the dynamics of
that remaining degree of freedom and design its limit cycle. "Accept" is the operative word: the
remaining degree of freedom is governed by gravity and **cannot be changed by the actuator**.

Assumed: relative degree, input-output linearisation and zero dynamics from
`c3-feedback-linearization`; guards, resets and the Poincare map from `s3-hybrid-limit-cycles`;
angular momentum.

| Symbol | Meaning |
|---|---|
| $q = (\theta_{\mathrm s},\theta_{\mathrm n})$ | stance and swing leg angles (from the slope normal, positive downhill) |
| $u$ | hip torque; the generalised force is $Bu$ with $B = (-1, +1)^\top$ |
| $\theta$ | the phase variable (here $\theta = \theta_{\mathrm s}$, monotone over a step) |
| $h_{\mathrm d}(\theta)$ | the virtual constraint — what is being designed |
| $y = \theta_{\mathrm n} - h_{\mathrm d}(\theta_{\mathrm s})$ | the output (virtual constraint error) |
| $Z = \{(q,\dot q) : y = 0,\ \dot y = 0\}$ | the zero dynamics surface |
| $S$ | the guard $\{\theta_{\mathrm s} = \alpha\}$; $\Delta$ the reset (impact plus relabelling) |
| $\sigma$ | **total angular momentum about the stance foot** |
| $\zeta = \tfrac12\sigma^2$ | the state of the reduced dynamics |
| $\delta_{\mathrm{zero}}$ | the factor by which the impact scales $\sigma$, $\sigma^+/\sigma^-$ (constant on $Z$) |
| $V_{\mathrm{zero}}$ | the effective potential of the reduced dynamics |

The numbers use the **same walker** as `s3-hybrid-limit-cycles` ($m=5$, $m_H=10$, $a=b=0.5$,
$g=9.81$, $\gamma = 0.05$) with one hip torque added, and the design variables are
$\alpha = 0.25$ rad and $h_{\mathrm d}'(\alpha) = -0.8$.

## Key results

The bracket is the derivation depth (the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (virtual constraints and the zero dynamics surface) [D3]** — the output
  $y = \theta_{\mathrm n} - h_{\mathrm d}(\theta_{\mathrm s})$ has relative degree 2, and if the
  decoupling term
  $$
  L_{g}\dot y = \begin{bmatrix}-h_{\mathrm d}'(\theta_{\mathrm s}) & 1\end{bmatrix} M(q)^{-1}B \tag{1}
  $$
  is non-zero there is a feedback enforcing $y \equiv 0$, and $Z$ is a two-dimensional manifold
  **invariant under the continuous flow** (with $\theta_{\mathrm s}$ and $\dot\theta_{\mathrm s}$
  as coordinates).
- **R2 (HZD: impact invariance is a **design condition**) [D3]** — continuous invariance is not
  enough. If the impact throws the state off $Z$ at every step, a transient is re-excited every
  step. So one demands
  $$
  \Delta\big(S \cap Z\big) \subset Z \tag{2}
  $$
  which translates into **boundary conditions on the virtual constraint**. For the compass gait
  they are $h_{\mathrm d}(-\alpha) = \alpha$, $h_{\mathrm d}(\alpha) = -\alpha$ and the **single
  scalar**
  $$
  h_{\mathrm d}'(-\alpha) = \frac{w_2}{w_1},\qquad
    w = Q^+(\alpha)^{-1}Q^-(\alpha)\begin{bmatrix}1\\ h_{\mathrm d}'(\alpha)\end{bmatrix} \tag{3}
  $$
  With a cubic Bezier, four coefficients are determined **exactly** by these three conditions plus
  the design freedom $h_{\mathrm d}'(\alpha)$ (numerically
  $h_{\mathrm d}'(-\alpha) = 0.7192862572$).
- **R3 (the reduced one-dimensional affine return map) [D3]** — **the hip torque exerts no moment
  about the stance foot**. So $\dot\sigma = \tau_{\mathrm g}(q)$ (the gravity moment) is all there
  is, and since the configuration on $Z$ is determined by $\theta$ alone,
  $\sigma = c(\theta)\dot\theta$ and
  $$
  \frac{d\zeta}{d\theta} = c(\theta)\,\tau_{\mathrm g}(\theta) =: -\frac{dV_{\mathrm{zero}}}{d\theta}
  \;\Longrightarrow\;
  \zeta^- = \zeta^+ - \Delta V_{\mathrm{zero}}. \tag{4}
  $$
  The impact multiplies $\sigma$ by a **constant** ($\delta_{\mathrm{zero}}$) on $Z$, so the step
  map is **affine**:
  $$
  \zeta^+_{k+1} = \delta_{\mathrm{zero}}^2\big(\zeta^+_k - \Delta V_{\mathrm{zero}}\big),
  \qquad
  \zeta^\star = \frac{-\delta_{\mathrm{zero}}^2\,\Delta V_{\mathrm{zero}}}{1-\delta_{\mathrm{zero}}^2}. \tag{5}
  $$
  **Existence** ($\zeta^\star > 0$ and $\zeta(\theta) > 0$ throughout the step, i.e. the walker
  does not stall) and **stability** ($\delta_{\mathrm{zero}}^2 < 1$) separate **completely**.
- **R4 (the reduced prediction is the full model's dominant eigenvalue) [D2]** — if the transverse
  stabiliser is fast enough, the Poincare eigenvalues of the four-state hybrid model are
  $\{\delta_{\mathrm{zero}}^2,\ \approx0,\ \approx0\}$. Numerically the design value is
  $\delta_{\mathrm{zero}}^2 = 0.7601914255$ and the full model measures
  $\{4.6\cdot10^{-5},\ 0.76019143,\ 0\}$ — agreement to **eight digits**.
- **R5 (design freedom and its price) [D2]** — $\alpha$ and the shape of $h_{\mathrm d}$ are free,
  and that choice fixes **both the walking speed and the convergence rate** through
  $\delta_{\mathrm{zero}}$ and $\Delta V_{\mathrm{zero}}$. On the same walker the passive gait had
  spectral radius $0.582$ ($\gamma=0.05$, R5 of `s3-hybrid-limit-cycles`) while this designed HZD
  gait has $0.760$ — it converges more slowly, but the step length and period can be **chosen**
  (period $0.4957$ s against the passive $0.7324$ s).

## Derivation

### R1 — from a virtual constraint to the zero dynamics surface

The plant is $M(q)\ddot q + N(q,\dot q) = Bu$ (with gravity and centrifugal terms inside $N$ and
$B=(-1,1)^\top$). Differentiating $y = \theta_{\mathrm n} - h_{\mathrm d}(\theta_{\mathrm s})$,

$$
\dot y = \dot\theta_{\mathrm n} - h_{\mathrm d}'\dot\theta_{\mathrm s}
  = \begin{bmatrix}-h_{\mathrm d}' & 1\end{bmatrix}\dot q
$$

contains no $u$ (so the relative degree is at least 2). Differentiating once more,

$$
\ddot y = \begin{bmatrix}-h_{\mathrm d}' & 1\end{bmatrix}\ddot q - h_{\mathrm d}''\dot\theta_{\mathrm s}^2
 = \underbrace{\begin{bmatrix}-h_{\mathrm d}' & 1\end{bmatrix}M^{-1}(-N) - h_{\mathrm d}''\dot\theta_{\mathrm s}^2}_{=:A(q,\dot q)}
 + \underbrace{\begin{bmatrix}-h_{\mathrm d}' & 1\end{bmatrix}M^{-1}B}_{=:b(q)}\,u \tag{6}
$$

so wherever $b(q) \ne 0$ the relative degree is exactly 2 and

$$
u = \frac{1}{b(q)}\Big(-A(q,\dot q) - K_p\,y - K_d\,\dot y\Big) \tag{7}
$$

produces $\ddot y = -K_py - K_d\dot y$, driving $y\to0$ exponentially. Under (7) the set
$Z = \{y=0,\dot y=0\}$ is **invariant under the continuous flow**, and since two of the four states
are constrained it is two-dimensional. On $Z$ we have
$\theta_{\mathrm n} = h_{\mathrm d}(\theta_{\mathrm s})$ and
$\dot\theta_{\mathrm n} = h_{\mathrm d}'\dot\theta_{\mathrm s}$, so the state is just
$(\theta_{\mathrm s}, \dot\theta_{\mathrm s})$.

**Where the assumptions break**: if $b(q) = 0$, (7) blows up — a carelessly chosen virtual
constraint can pass through such a configuration mid-step, so always check
$\min_\theta \lvert b \rvert$ after designing. And large $K_p, K_d$ in (7) kill the transverse
dynamics quickly at the price of large torques — the same trade as the $1/d$ blow-up in
`c3-feedback-linearization`.

### R3 — the reduction: find the quantity the actuator cannot touch

**Step 1 (why $\sigma$).** Put the stance foot at the origin and consider the total angular
momentum $\sigma = \sum_i m_i (r_i)\times v_i$. The hip torque is an **internal** force between
the legs, so it has no moment about the stance foot, and the ground reaction acts at the stance
foot, so it has none either. Only gravity is left:

$$
\dot\sigma = \tau_{\mathrm g}(q) = \sum_i m_i\,(r_i \times g). \tag{8}
$$

**Numerical check**: over 2000 random $(q,\dot q,u)$ the difference between $d\sigma/dt$ computed
from the dynamics and (8) is at most $7.6\cdot10^{-9}$ — **it does not move when $u$ is swung over
$\pm50$ N·m**. That is the physical core of the HZD reduction: there is one quantity the actuator
cannot change, and that quantity is the "speed" of the gait.

**Step 2 (one dimension on $Z$).** On $Z$,
$\dot q = (1, h_{\mathrm d}'(\theta))^\top\dot\theta$, so $\sigma$ is linear in $\dot\theta$:
writing $\sigma = c(\theta)\dot\theta$ with
$c(\theta) = \rho(\theta)^\top(1, h_{\mathrm d}'(\theta))^\top$ (where $\rho$ is the row vector of
$\sigma$), setting $\zeta := \tfrac12\sigma^2$ and changing the derivative to $\theta$,

$$
\frac{d\zeta}{d\theta} = \sigma\frac{d\sigma}{d\theta}
  = \sigma\frac{\dot\sigma}{\dot\theta} = c(\theta)\,\tau_{\mathrm g}(\theta),
$$

which is (4). **Time has disappeared** — what remains is a one-dimensional integral in $\theta$,
not a trajectory. Defining
$V_{\mathrm{zero}}(\theta) := -\int_{-\alpha}^{\theta} c\,\tau_{\mathrm g}\,d\vartheta$ gives
$\zeta(\theta) = \zeta^+ - \big(V_{\mathrm{zero}}(\theta)-V_{\mathrm{zero}}(-\alpha)\big)$.
Numerically
$\Delta V_{\mathrm{zero}} = V_{\mathrm{zero}}(\alpha)-V_{\mathrm{zero}}(-\alpha) = -49.65652176$
(negative because the slope descends — $\zeta$ **grows** over a step).

**Step 3 (why the impact is a constant factor).** On $Z$ the configuration at impact is **always
the same** ($\theta_{\mathrm s}=\alpha$, $\theta_{\mathrm n}=-\alpha$). The impact map is linear in
velocity, and on $Z$ the velocity direction is fixed at $(1,h_{\mathrm d}'(\alpha))$ with only its
magnitude free. Hence

$$
\sigma^+ = \delta_{\mathrm{zero}}\,\sigma^-, \qquad
\delta_{\mathrm{zero}} = \frac{\rho(q^+)^\top Q^+(\alpha)^{-1}Q^-(\alpha)\,(1,h_{\mathrm d}'(\alpha))^\top}
  {\rho(q^-)^\top (1,h_{\mathrm d}'(\alpha))^\top} \tag{9}
$$

is a **constant** (numerically $\delta_{\mathrm{zero}} = 0.8718895718$). Since $\zeta$ is the
square of $\sigma$, $\zeta^+ = \delta_{\mathrm{zero}}^2\,\zeta^-$, and combining with (4) gives the
affine map (5).

**Step 4 (existence and stability separate).** (5) is a scalar affine map
$\zeta \mapsto \delta^2(\zeta - \Delta V)$, so ⓐ its fixed point
$\zeta^\star = -\delta^2\Delta V/(1-\delta^2)$ is **closed form** and ⓑ its convergence rate is the
slope $\delta^2$, **independent of the initial condition**. Numerically
$\zeta^\star = 157.4108104$, $\sigma^{+\star} = -17.74321337$ (negative in this sign convention for
forward motion) and $\dot\theta_{\mathrm s}^{+\star} = 1.32639024$ rad/s.

**One more condition for actually walking**: $\zeta(\theta)>0$ throughout the step. If $\zeta$
reaches zero the walker **stops** there (it cannot pass over the stance leg). Numerically the
minimum along the step is $\zeta = 87.86 > 0$, with margin.

**Where the assumptions break**: ⓐ if $\delta_{\mathrm{zero}}^2 \ge 1$, (5) diverges — a design in
which the impact does not shave off enough angular momentum. ⓑ if
$\Delta V_{\mathrm{zero}} > 0$ (level ground or uphill) then $\zeta^\star<0$ and there is **no
solution**, because no amount of torque can increase $\sigma$. Level-ground walking needs
**additional actuation** such as a torso or ankles, and then an input enters the reduced dynamics
and (5) becomes more complicated. ⓒ if the transverse convergence is slow, R4's "dominant
eigenvalue $=\delta^2$" fails.

### R2 — impact invariance as Bezier boundary conditions

Write (2) out. On $Z$ at the end of a step, $q^- = (\alpha,-\alpha)$ and
$\dot q^- = \dot\theta^-(1, h_{\mathrm d}'(\alpha))^\top$. Through the impact map,
$\dot q^+ = \dot\theta^-\,w$ with
$w := Q^+(\alpha)^{-1}Q^-(\alpha)(1,h_{\mathrm d}'(\alpha))^\top$, and after relabelling the
configuration is $q^+ = (-\alpha, \alpha)$. For the new state to lie on $Z$,

$$
\underbrace{\alpha = h_{\mathrm d}(-\alpha)}_{y^+=0}, \qquad
\underbrace{w_2 = h_{\mathrm d}'(-\alpha)\,w_1}_{\dot y^+=0} \tag{10}
$$

and for the step to end on the guard, $h_{\mathrm d}(\alpha) = -\alpha$. Putting these three
conditions plus the design freedom $h_{\mathrm d}'(\alpha) = k$ into a cubic Bezier
$h_{\mathrm d}(s) = \sum_{i=0}^3 c_i\binom{3}{i}s^i(1-s)^{3-i}$ with
$s = (\theta+\alpha)/2\alpha$ gives the coefficients in **closed form**:

$$
c_0 = \alpha,\quad c_3 = -\alpha,\quad
c_1 = c_0 + \frac{2\alpha}{3}\frac{w_2}{w_1},\quad
c_2 = c_3 - \frac{2\alpha}{3}k. \tag{11}
$$

Numerically (with $\alpha=0.25$, $k=-0.8$): $c = (0.25,\ 0.36988104,\ -0.11666667,\ -0.25)$ and
$h_{\mathrm d}'(-\alpha) = 0.7192862572$ matches the requirement of (10) in **every digit**.

**What violating it looks like**: deliberately offsetting $h_{\mathrm d}'(-\alpha)$ by $0.2$ leaves
$y^+ \ne 0$ at every step, injecting a transient each step, and the full model's dominant
eigenvalue no longer matches $\delta_{\mathrm{zero}}^2$ (baseline ⓐ of the reproduction task).

### R4 — checking the reduced prediction against the full model

Integrating the **four-state** model with the controller (7) ($K_p=400$, $K_d=40$) from the
$\dot\theta_{\mathrm s}^{+\star} = 1.32639024$ obtained from the fixed point of (5):

| step | period (s) | $\dot\theta_{\mathrm s}^+$ | $\lvert y^+\rvert$ | $\sigma^+$ |
|---|---|---|---|---|
| 1 | 0.495686 | 1.32639024 | $1.7\cdot10^{-16}$ | $-17.74321337$ |
| 2-6 | 0.495686 | 1.32639024 | $\le 1.7\cdot10^{-16}$ | $-17.74321337$ |

so it is **on the limit cycle from the first step** (which is what it means for the reduced model to
have hit the fixed point exactly). Differentiating the one-dimensional return map numerically gives
a slope of $0.76019143$, matching $\delta_{\mathrm{zero}}^2 = 0.76019143$ to eight digits, and the
eigenvalues of the three-dimensional Poincare map are

$$
\{4.6\cdot10^{-5},\quad 0.76019143,\quad 0\} \tag{12}
$$

— the dominant one is exactly $\delta_{\mathrm{zero}}^2$ and the other two are the remains of the
collapsed transverse directions. **This is what HZD buys**: the stability of a four-state hybrid
system is known **in advance**, at design time, from two one-dimensional integrals
($\Delta V_{\mathrm{zero}}$ and $\delta_{\mathrm{zero}}$).

## Proof sketch

### R2 — why impact invariance is the definition of *hybrid* zero dynamics

**Hypotheses** H1: $Z$ is invariant under the continuous flow, by (7). H2: the reset $\Delta$ is
$C^1$ near $S$. H3: (2), $\Delta(S\cap Z)\subset Z$. H4: the reduced dynamics on $Z$ have a fixed
point of (5) with $\zeta^\star>0$ and $\zeta>0$ throughout the step.
**Conclusion** C: $Z$ is invariant for the whole **hybrid** system, and the periodic orbit on $Z$
is orbitally asymptotically stable **within** $Z$ if and only if $\delta_{\mathrm{zero}}^2<1$; if
the transverse dynamics are exponentially stable it is orbitally asymptotically stable for the full
system.

**Strategy**: build one invariant manifold and solve a **lower-dimensional** problem on it. For a
hybrid system the whole content is that invariance under the flow and invariance under the reset
must be shown **separately**.

1. **The flow side.** By H1, $y(0)=\dot y(0)=0$ implies $y\equiv0$, so the trajectory never leaves
   $Z$.
2. **The reset side.** H3 is exactly that requirement. Without (2) the trajectory leaves $Z$, and
   although (7) pulls $y$ back to zero, **that transient repeats every step** and the reduced
   model's prediction breaks.
3. **The reduced dynamics.** In coordinates $(\theta,\zeta)$ on $Z$ the dynamics are (4)-(5) and the
   step map is a scalar affine map. The fixed point of
   $\zeta\mapsto \delta^2(\zeta-\Delta V)$ is unique and globally exponentially stable when
   $\lvert\delta^2\rvert<1$ (in one dimension the **basin is all of $\zeta>0$**).
4. **Lifting to the full system.** If $Z$ is hybrid invariant and the transverse coordinates
   $(y,\dot y)$ shrink exponentially from step to step, the spectrum of the full Poincare map
   splits into "the $\delta^2$ of the reduced direction ⊕ small transverse values" (a block
   triangular structure). The numbers (12) are that picture.
   (Omitted: quantifying "the transverse convergence is **fast enough** relative to the reduced
   direction" — the theorem in Westervelt et al. 2003 §IV.)

**Remove a hypothesis**: without H3, step 2 fails, $Z$ is not hybrid invariant and the prediction of
(5) is wrong — that condition is the H of HZD. Without the $\zeta>0$ of H4 the walker stalls
mid-step and never reaches the guard, and without $\zeta^\star>0$ the fixed point does not exist
physically. And passing through a configuration with $b(q)=0$ (R1) breaks H1 itself.

## Problem set

Six problems: two derivations, one proof, one numerical, one implementation and one counterexample.
Difficulty is ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1·R3)** Write the decoupling term $b(q)$ of (6) explicitly with the compass
gait's mass matrix, and check numerically, for the design $\alpha = 0.25$,
$h_{\mathrm d}'(\alpha) = -0.8$, whether any configuration with $b(q) = 0$ occurs. Then explain in a
paragraph why the torque does not enter the dynamics of $\sigma$ but does enter those of $y$.
*Solution sketch*: expand $b(q) = [-h_{\mathrm d}'(\theta_{\mathrm s}), 1] M(q)^{-1} B$ with the
$2\times2$ inverse, take the minimum of $\lvert b\rvert$ over the step numerically and show it is
bounded away from zero. The torque is an internal force between the legs, so it has no moment about
the stance foot and does not affect $\sigma$; $y$, by contrast, is the relative degree of freedom
between the legs, which an internal force accelerates directly — that is exactly how the actuated
and unactuated directions separate.

**P2 (derivation, ★★, R2)** Derive (11) from (10). With a quintic Bezier instead of a cubic, how
many degrees of freedom are left, and what can they optimise? (Pick one of peak torque, walking
speed or foot clearance and write the objective.)
*Solution sketch*: use the fact that a Bezier's endpoint values and endpoint slopes are given by
$c_0, c_3$ and $(c_1-c_0), (c_3-c_2)$. A quintic spends four of its six coefficients on boundary
conditions and leaves two. Those can minimise $\max_t \lvert u(t)\rvert$ (a minimax torque problem)
or match a target period, and both are evaluated **inside the reduced model**, so the design needs
no integration of the full model.

**P3 (proof, ★★★, R3)** From the fact that the step map on $Z$ is affine (5), prove (a) uniqueness
of the fixed point, (b) that the basin is all of $\zeta > 0$, and (c) that the convergence rate is
independent of the initial condition. Then say what happens on the boundary $\delta^2 = 1$.
*Solution sketch*: a scalar affine map is a geometric sequence. At $\delta^2 = 1$ the map becomes
the translation $\zeta \mapsto \zeta - \Delta V$, which has no fixed point when $\Delta V \ne 0$ and
every point as a fixed point when $\Delta V = 0$ — the former is a non-periodic gait whose speed
changes monotonically every step, the latter neutral stability at any speed. Physically it is the
case where the balance between impact loss and gravitational input has broken.

**P4 (numerical, ★, R2·R3·R4)** For the design $\alpha = 0.25$, $h_{\mathrm d}'(\alpha) = -0.8$,
$\gamma = 0.05$ find (a) $h_{\mathrm d}'(-\alpha)$, (b) $\delta_{\mathrm{zero}}^2$,
(c) $\Delta V_{\mathrm{zero}}$, (d) $\zeta^\star$ and (e) $\dot\theta_{\mathrm s}^{+\star}$.
*Answers*: (a) $0.7192862572$, (b) $0.7601914255$, (c) $-49.65652176$, (d) $157.4108104$,
(e) $1.32639024$ rad/s. Tolerance $10^{-6}$. Check: (d) $= -$(b)(c)$/(1-$(b)$)$, and (e) is
$\sigma^{+\star} = -\sqrt{2\zeta^\star}$ divided by $c(\theta)$ on $Z$.

**P5 (implementation, ★★, R1·R2·R4)** Design the virtual constraint with (11), integrate the
four-state model with the controller (7) and pass the four acceptance criteria of the reproduction
task. Then lower $K_p$ and $K_d$ by a factor of ten to slow the transverse convergence, and
tabulate how far the full model's dominant eigenvalue drifts from $\delta_{\mathrm{zero}}^2$.
*Rubric*: passing requires (1) the boundary conditions on $h_{\mathrm d}$ met to $10^{-12}$,
(2) $\lvert y^+\rvert < 10^{-12}$ from the very first step at the predicted initial state, (3) the
dominant eigenvalue matching $\delta_{\mathrm{zero}}^2$ to $10^{-6}$, and (4) numbers showing that
lowering the gains breaks that match in the expected direction (the transverse eigenvalue grows and
the dominant one wanders).

**P6 (counterexample, ★★, R2·R3)** (a) Deliberately break the impact invariance (10) (offset
$h_{\mathrm d}'(-\alpha)$ by $0.2$), run the full model and show what changes. (b) Try the same
design on level ground ($\gamma = 0$), show that $\zeta^\star < 0$, and explain with (8) why no
amount of hip torque fixes it.
*Property checklist*: (a) $\lvert y^+\rvert \ne 0$ persists every step, the one-dimensional
prediction and the full model's dominant eigenvalue disagree, and a transient repeats each period.
(b) $\Delta V_{\mathrm{zero}} > 0$ makes the fixed point of (5) negative; the torque never enters
equation (8) for $\sigma$, so it cannot change the reduced dynamics — level-ground walking needs
extra actuation such as ankles or a torso.

## Paper reading

**Two must-reads plus one recommended.** Write a one-page note on each using the ten fixed
questions (the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read in three passes and attack questions 4, 5, 6, 7 in the
third.

1. **Westervelt, Grizzle & Koditschek, "Hybrid zero dynamics of planar biped walkers" (2003,
   IEEE T-AC)** — role: `seminal`. <https://doi.org/10.1109/TAC.2002.806653> (§III, §IV).
   R1-R4 of this lesson are a scaled-down version of this paper.
   Extra questions: ⓐ Write the authors' "hybrid invariance" condition and our (2) and (10) side by
   side in the same symbols. ⓑ Explain why the authors build the reduced map on **angular
   momentum**, by saying what breaks if another quantity (total energy, say) is used.
2. **Ames, "Human-inspired control of bipedal walking robots" (2014, IEEE T-AC)**
   — role: `standard`. <https://doi.org/10.1109/TAC.2014.2299342> (§II, §V). A case in which the
   virtual constraints come from **human data** and the result runs on hardware (NAO).
   Extra questions: ⓐ If the virtual constraints are chosen from human data, how is the impact
   invariance of (10) then guaranteed? ⓑ Which of the failure modes reported in the hardware
   experiments connects directly to this lesson's assumptions (point feet, rigid ground)?
3. **Grizzle, Abba & Plestan (2001)** — role: `recommended`.
   <https://doi.org/10.1109/9.898695> (§III). The paper read in `s3-hybrid-limit-cycles`. Read it
   this time as the way to reach the same verdict **without** a reduction, and write a paragraph on
   what the reduction saves.

**The ten fixed questions**: (1) which problem under which assumptions (2) what exactly earlier
work could not do (3) the core idea in one equation (4) what is guaranteed and **what is not**
(5) independent and dependent variables and baselines, fairly tuned (6) do the metrics match the
claim, are variance and seeds reported (7) what is missing for reproduction (8) the first
assumption to doubt if the result is wrong (9) computational and memory complexity and real-time
feasibility (10) what you would change to go beyond it in a year.

## Reproduction task

**Tier R2 (re-implementation).** Budget: laptop CPU under ten minutes, numpy only. The target is the
compass gait of `s3-hybrid-limit-cycles` with a hip torque added ($\gamma=0.05$), and the design
variables are $\alpha = 0.25$, $h_{\mathrm d}'(\alpha) = -0.8$. There is no input data.

**Acceptance criteria (all four)**

1. **Structural check**: over $10^3$ random $(q,\dot q,u)$ with $\lvert u\rvert \le 50$, the
   difference between $d\sigma/dt$ from the dynamics and the gravity moment (8) is $< 10^{-8}$
   (reference $7.6\cdot10^{-9}$). Report also that the value does not move when $u$ changes.
2. **Impact invariance**: with the Bezier coefficients of (11),
   $h_{\mathrm d}(-\alpha)=\alpha$, $h_{\mathrm d}(\alpha)=-\alpha$ and
   $h_{\mathrm d}'(\alpha)=-0.8$ each hold to $10^{-12}$, and
   $h_{\mathrm d}'(-\alpha) = 0.7192862572 \pm 10^{-9}$ matches the requirement of (10).
3. **The reduced prediction**: reproduce $\delta_{\mathrm{zero}}^2 = 0.7601914255$,
   $\Delta V_{\mathrm{zero}} = -49.65652176$, $\zeta^\star = 157.4108104$ and
   $\dot\theta_{\mathrm s}^{+\star} = 1.32639024$ to a relative error of $10^{-6}$ each, and check
   $\zeta>0$ throughout the step (reference minimum $87.86$).
4. **Agreement with the full model**: starting from the predicted state, integrate ten steps and
   show ⓐ the period stays at $0.495686$ s, ⓑ $\lvert y^+\rvert < 10^{-12}$ at every step, and
   ⓒ the dominant eigenvalue of the three-dimensional Poincare map matches $0.76019143$ to
   $10^{-6}$ while the other two have modulus below $10^{-3}$.

**Baselines**: ⓐ the version with impact invariance broken ($h_{\mathrm d}'(-\alpha)$ offset by
$+0.2$) — criteria 4ⓑ and 4ⓒ must **fail**; ⓑ level ground ($\gamma=0$) — criterion 3 must give
$\zeta^\star<0$, i.e. **no solution**; ⓒ the passive gait of `s3-hybrid-limit-cycles` (spectral
radius $0.582$, period $0.7324$ s) — tabulate the trade that the designed gait is faster
($0.4957$ s) but converges more slowly ($0.760$).

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| Criterion 1 fails (the value changes with $u$) | $\sigma$ was computed about a point other than the stance foot (the hip or the centre of mass) | check that the stance foot is the origin and that every mass is included |
| $\lvert y^+\rvert$ stays around $10^{-3}$ | the second condition of (10) was written with $\dot q^-$ instead of $w$ (the impact map was skipped) | print $w = Q^{+-1}Q^-(1,h_{\mathrm d}'(\alpha))^\top$ |
| The dominant eigenvalue is **larger** than $\delta^2$ | $K_p, K_d$ too small, so the transverse dynamics do not die within a step | raise $K_p$ fourfold and see whether the eigenvalue converges to $\delta^2$ |
| $\zeta^\star$ comes out with the wrong sign | the sign in (5) — it is $\zeta^\star = -\delta^2\Delta V/(1-\delta^2)$ | check that $\Delta V<0$ (downhill) gives $\zeta^\star>0$ |
| Torques spike to hundreds of N·m during integration | the step passes through a configuration with small $b(q)$ | print $\min\lvert b\rvert$ over the step and adjust $h_{\mathrm d}'(\alpha)$ |

## Open problems

- **(open problem) Optimal design of virtual constraints** — (11) only meets the boundary
  conditions, and what the remaining freedom (a higher-order Bezier) should optimise is unsettled.
  Minimising torque, maximising efficiency and maximising the convergence rate give different
  solutions, and there is no general way to characterise the Pareto frontier of the three inside the
  reduced model. This is where it meets the trajectory optimisation of
  `c4-direct-collocation-sqp`.
- **(open problem) Extension to three dimensions and multiple contacts** — the elegance of planar
  HZD rests on "exactly one remaining degree of freedom". In three dimensions several remain, and
  with finite-area soles and ankle torques the reduction does not collapse to one dimension. Current
  approaches: human-data constraints in
  [Ames 2014](https://doi.org/10.1109/TAC.2014.2299342), multi-domain HZD. The gap: a closed-form
  verdict when the reduced dimension is two or more.
- **(open problem) HZD under model error** — both $\delta_{\mathrm{zero}}$ and
  $\Delta V_{\mathrm{zero}}$ are integrals of the model. There is no sensitivity bound saying how
  far the predicted eigenvalue moves when masses, inertias or the impact model are off by a few per
  cent. The gap: a **robust** version of the reduced model — applying the tube bound of
  `c3-contraction-incremental` in the reduced coordinates is the natural attempt.
- **(open problem) Combining with learning** — learning virtual constraints from data means
  imposing (10) **as a constraint**, and how to preserve the guarantee that a learned constraint is
  impact invariant is not established. `s3-locomotion-rl` compares the opposite direction (learning
  with no constraint at all).

## Concept check

Take it with `rc quiz s3-hzd-gait-generation`. The quiz is **for concept checking only**; the real
work is the problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`). Four questions
ask: why the hip torque cannot change the angular momentum about the stance foot; whether
output-zeroing feedback alone makes $Z$ invariant for the hybrid system; the fixed point of the
affine step map; and why the reduced prediction matched the full model to eight digits.

## How to study this stage

1. **Write down what underactuation means first (30 min)** — a paragraph on why "put every joint on
   a trajectory" is impossible for a point-footed robot, and on what HZD gives up instead (the
   **time trajectory** of the remaining degree of freedom).
2. **Confirm by hand and in code that $\sigma$ is torque-free (60 min)** — pass criterion 1 of the
   reproduction task first. Without that fact it is not visible why the reduction in R3 works.
3. **Solve the Bezier boundary conditions by hand (60 min)** — (10) → (11). Locate exactly where the
   impact map $w$ enters. Solving P2 shows what freedom a higher-order Bezier leaves.
4. **Finish the design inside the reduced model (90 min)** — criteria 2 and 3. Obtain $\delta^2$,
   $\Delta V$, $\zeta^\star$ and $\dot\theta^{+\star}$ **without integrating the full model even
   once**. That is the real value of HZD.
5. **Only then check against the full model (90 min)** — criterion 4. It must be on the limit cycle
   from the first step; if it is not, something in 2 or 3 is wrong.
6. **Break it in two ways (60 min)** — baselines ⓐ (impact invariance violated) and ⓑ (level
   ground). The first shows "without the H it is not HZD", the second that "the reduced dynamics
   cannot be changed by torque".
7. **Read the papers for "what the reduction saves" (135 min)** — put Westervelt 2003 and
   Grizzle 2001 side by side and count what must be computed to reach the same verdict without a
   reduction. Read Ames 2014 as the list of what must be added to put that reduction on hardware.

**Passing bar**: you can derive (4), (5) and (10) from memory, state why $\sigma$ is unaffected by
the torque, and you have code meeting all four acceptance criteria plus notes on the three papers.
