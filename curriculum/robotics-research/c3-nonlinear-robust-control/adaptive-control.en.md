---
id: c3-adaptive-control
lang: en
title: Adaptive control and persistent excitation
summary: >-
  The Slotine-Li adaptive controller, which tracks while estimating unknown parameters online, is
  derived from a Lyapunov function, and the fact that **tracking converges while the parameters do
  not** is made precise through persistent excitation. It goes on to the trap of certainty
  equivalence and the instability caused by unmodelled dynamics (the Rohrs counterexample), then
  compares the prescriptions of robust adaptive control.
objectives:
  - Construct the linear-in-parameter structure $Y(q,\dot q,\dot q_r,\ddot q_r)a$ of manipulator dynamics yourself.
  - Set up the Lyapunov function of the Slotine-Li controller and derive $\dot V = -s^\top K_D s$ with no missing steps.
  - Write the persistent-excitation condition as an integral inequality and explain why it is the boundary of parameter convergence.
  - Produce numerically a case with zero tracking error but persistent parameter error, and name the column that was not excited.
  - Explain the mechanism by which adaptation goes unstable under unmodelled dynamics and choose a robust prescription.
tags: [nonlinear-control, adaptive-control, persistent-excitation, manipulator, research]
---

# Adaptive control and persistent excitation

## Setup and notation

The energy shaping of `c3-passivity-impedance` assumed the gravity model $g(q)$ was exact, and
model error remained as a steady-state offset $K_p^{-1}(\hat g - g)$. This lesson erases that
offset by **estimating online**. There are two questions: ⓐ can tracking succeed while the
estimate is wrong (it can), and ⓑ does the estimate approach the truth (**only conditionally**).

Assumed: Lagrangian dynamics and the structure of the mass matrix, LaSalle and the comparison
lemma from `c3-lyapunov-stability`, and the skew identity (5) of `c3-passivity-impedance`. From
linear algebra: Gram matrices and their smallest eigenvalue.

| Symbol | Meaning |
|---|---|
| $a \in \mathbb{R}^p$ | the true parameter vector (combinations of masses, inertias and link lengths) |
| $\hat a$, $\tilde a = \hat a - a$ | the estimate and the estimation error |
| $Y(q,\dot q,\dot q_r,\ddot q_r)$ | the regressor: $M\ddot q_r + C\dot q_r + g = Y a$ |
| $\tilde q = q - q_d$ | tracking error |
| $\dot q_r = \dot q_d - \Lambda \tilde q$ | reference velocity, $\Lambda \succ 0$ |
| $s = \dot q - \dot q_r = \dot{\tilde q} + \Lambda\tilde q$ | the composite (filtered) error |
| $K_D \succ 0$, $\Gamma \succ 0$ | feedback gain and adaptation gain |
| $W(t)$ | the regressor evaluated along the desired trajectory, $Y(q_d,\dot q_d,\dot q_d,\ddot q_d)$ |

The running example is a two-link planar manipulator, with the parameters grouped as

$$
a = \begin{bmatrix} m_1\ell_{c1}^2 + I_1 + m_2\ell_1^2 \\ m_2\ell_{c2}^2 + I_2 \\
  m_2\ell_1\ell_{c2} \\ (m_1\ell_{c1}+m_2\ell_1)g \\ m_2\ell_{c2}g \end{bmatrix}
  \;\xrightarrow{\text{numbers used below}}\;
  \begin{bmatrix} 1.333333 \\ 0.333333 \\ 0.5 \\ 14.715 \\ 4.905 \end{bmatrix}. \tag{1}
$$

($m_i = 1$ kg, $\ell_i = 1$ m, $\ell_{ci} = 0.5$ m, $I_i = 1/12$, $g = 9.81$.)

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (linear-in-parameter structure) [D2]** — manipulator dynamics are **linear in the
  parameters**:
  $$
  M(q)\ddot q_r + C(q,\dot q)\dot q_r + g(q) = Y(q,\dot q,\dot q_r,\ddot q_r)\,a \tag{2}
  $$
  with $Y$ a known function. The $Y$ of the two-link arm is constructed componentwise below.
- **R2 (the Slotine-Li controller and tracking convergence) [D3]** — for the control and
  adaptation laws
  $$
  \tau = Y\hat a - K_D s, \qquad \dot{\hat a} = -\Gamma Y^\top s \tag{3}
  $$
  the function $V = \tfrac12 s^\top M s + \tfrac12\tilde a^\top \Gamma^{-1}\tilde a$ satisfies
  $$
  \dot V = -s^\top K_D s \le 0. \tag{4}
  $$
  Hence $s \in L_2 \cap L_\infty$, $s \to 0$, and since $s = \dot{\tilde q} + \Lambda\tilde q$,
  also $\tilde q \to 0$. **$\tilde a$ is only bounded; nothing guarantees it tends to zero.**
- **R3 (persistent excitation and parameter convergence) [D3]** — if $W(t)$ is **persistently
  exciting (PE)**, i.e.
  $$
  \exists\,\alpha, T_0 > 0: \quad \int_t^{t+T_0} W(\sigma)^\top W(\sigma)\,d\sigma \succeq \alpha I
    \quad \text{for all } t \ge 0, \tag{5}
  $$
  then $\tilde a \to 0$ exponentially. Conversely, where PE fails ($\alpha = 0$) the parameter
  error in the unexcited direction **stays forever**. For the linear error system PE is
  **necessary and sufficient** for exponential convergence (Boyd & Sastry 1986).
- **R4 (the trap of certainty equivalence) [D2]** — at a set-point the rank of $W$ drops (on the
  two-link arm to **2** of 5 columns, the gravity ones only), so the tracking error can fall to
  $10^{-14}$ while the inertial parameter error stays **fixed** at 34%. The inference "it tracks
  well, so the model must be right" is false.
- **R5 (robust adaptation) [D1]** — with unmodelled dynamics the argument of (4) breaks and
  parameter drift and bursting appear (Rohrs et al. 1985). The prescriptions are projection,
  dead-zones, $\sigma$-modification, and $L_1$ adaptive control, which separates adaptation speed
  from robustness with a low-pass filter.

## Derivation

### R1 — the regressor of the two-link arm

Group the left side of (2) by the parameters of (1). The mass matrix and gravity are

$$
M(q) = \begin{bmatrix} a_1 + a_2 + 2a_3\cos q_2 & a_2 + a_3\cos q_2 \\
  a_2 + a_3 \cos q_2 & a_2\end{bmatrix}, \qquad
g(q) = \begin{bmatrix} a_4\cos q_1 + a_5 \cos(q_1+q_2) \\ a_5\cos(q_1+q_2)\end{bmatrix},
$$

and the Christoffel choice of $C$ is, with $h := -a_3 \sin q_2$,

$$
C(q,\dot q) = \begin{bmatrix} h\dot q_2 & h(\dot q_1 + \dot q_2) \\ -h\dot q_1 & 0\end{bmatrix}.
$$

Expanding $M\ddot q_r + C\dot q_r + g$ and collecting the coefficients of each $a_j$ gives

$$
Y = \begin{bmatrix}
\ddot q_{r1} & \ddot q_{r1}+\ddot q_{r2} &
  2c_2\ddot q_{r1} + c_2\ddot q_{r2} - s_2\dot q_2\dot q_{r1} - s_2(\dot q_1+\dot q_2)\dot q_{r2}
  & \cos q_1 & \cos(q_1+q_2) \\[2pt]
0 & \ddot q_{r1}+\ddot q_{r2} & c_2\ddot q_{r1} + s_2\dot q_1\dot q_{r1} & 0 & \cos(q_1+q_2)
\end{bmatrix} \tag{6}
$$

with $c_2 = \cos q_2$ and $s_2 = \sin q_2$. **Numerical check**: setting $\dot q_r = \dot q$ and
$\ddot q_r = \ddot q$ and drawing 2000 random $(q,\dot q,\ddot q)$,
$\max\lvert Ya - (M\ddot q + C\dot q + g)\rvert = 7.1\cdot10^{-15}$ — machine precision.

**Where the assumptions break**: (2) is written **without friction or actuator dynamics**. Coulomb
friction $\tau_f = F_c\operatorname{sgn}(\dot q)$ is linear in the parameters but non-smooth, so
$Y$ is ill-defined near $\dot q = 0$; viscous friction only adds a column but makes the excitation
condition (R3) harder. Note also that avoiding $\ddot q$ is the design point of (3) — acceleration
measurements are noisy, so only $\ddot q_r$ (a computable reference) appears.

### R2 — the Lyapunov function and tracking convergence

**Step 1 (error dynamics).** Substitute (3) into the dynamics and rearrange in
$s = \dot q - \dot q_r$. Since $M\dot s = M\ddot q - M\ddot q_r$ and
$M\ddot q = \tau - C\dot q - g$,

$$
M\dot s = Y\hat a - K_Ds - C\dot q - g - M\ddot q_r
  \overset{(2)}{=} Y\hat a - K_Ds - C\dot q - (Ya - C\dot q_r)
  = Y\tilde a - K_D s - Cs, \tag{7}
$$

that is, $M\dot s + Cs + K_Ds = Y\tilde a$. The point of this line is that **the gravity and
$\ddot q_r$ terms disappear wholesale**, thanks to (2).

**Step 2 (differentiating the Lyapunov function).** Differentiate
$V = \tfrac12 s^\top Ms + \tfrac12\tilde a^\top\Gamma^{-1}\tilde a$ and insert (7). Since
$\dot{\tilde a} = \dot{\hat a}$,

$$
\dot V = s^\top M\dot s + \tfrac12 s^\top \dot M s + \tilde a^\top\Gamma^{-1}\dot{\hat a}
  = s^\top\big(Y\tilde a - K_Ds - Cs\big) + \tfrac12 s^\top\dot Ms + \tilde a^\top\Gamma^{-1}\dot{\hat a}.
$$

Here the skew identity $s^\top(\tfrac12\dot M - C)s = 0$ from `c3-passivity-impedance` kills the
$C$ term (it matters that the identity holds for an **arbitrary vector** $s$, not just $\dot q$ —
it does, because $\tfrac12\dot M - C$ is skew as a matrix). What is left is

$$
\dot V = s^\top Y\tilde a - s^\top K_D s + \tilde a^\top \Gamma^{-1}\dot{\hat a}.
$$

Inserting the adaptation law $\dot{\hat a} = -\Gamma Y^\top s$ of (3) gives
$\tilde a^\top\Gamma^{-1}(-\Gamma Y^\top s) = -\tilde a^\top Y^\top s = -s^\top Y\tilde a$, which
**cancels the first term exactly**, leaving (4). The form of the adaptation law is **designed** to
produce that cancellation.

**Step 3 (to the tracking error).** By (4), $V$ is non-increasing, so $s$ and $\tilde a$ are
bounded. Since $V$ is bounded below, $\int_0^\infty s^\top K_D s\,dt = V(0) - V(\infty) < \infty$,
i.e. $s \in L_2$. From (7), $\dot s$ is bounded, so Barbalat's lemma gives $s \to 0$. Finally
$s = \dot{\tilde q} + \Lambda\tilde q$ is an exponentially stable linear filter driven by $s$, so
$s \to 0$ implies $\tilde q \to 0$ and $\dot{\tilde q}\to0$ (the simplest instance of the ISS
estimate in R4 of `c3-lyapunov-stability`).

**Where the assumptions break**: (4) is only semi-definite in $\tilde a$ — no $\tilde a$ term
appears in $\dot V$ at all. So the Lyapunov argument alone cannot claim $\tilde a \to 0$, and
indeed it does not happen. That gap is R3. Also, a large $\Gamma$ in (3) adapts quickly, but with
unmodelled dynamics present that same speed turns into instability (R5).

### R4 — when tracking succeeds and the parameters are wrong (numbers)

Running (3) on the two-link arm with $\Lambda = 4I$, $K_D = 20I$, $\Gamma = 20I$ and
$\hat a(0) = 0.5\,a$ (RK2 integration, $\Delta t = 5\cdot10^{-4}$, 180 s).

| Trajectory | $\max\lvert\tilde q\rvert_\infty$ (last 10 s) | $\lVert\tilde a\rVert/\lVert a\rVert$ (at 180 s) | PE Gram $\lambda_{\min}$ (10 s window) |
|---|---|---|---|
| PE: $q_{d1} = 0.4\sin t + 0.3\sin\sqrt2 t$, $q_{d2} = 0.5\cos 1.3t - 0.2\sin 0.7t$ | $1.0\cdot10^{-5}$ | $1.0\cdot10^{-4}$ | $0.663$ (rank 5) |
| set-point $q_d = (0.3,\ -0.5)$ | $4.8\cdot10^{-14}$ | $0.337$ | $0$ (rank 2) |
| (control) non-adaptive, parameters fixed at $0.5a$ | $0.127$ / $0.119$ | — | — |

On the PE trajectory the parameter error falls below 5% at 35 s and below 1% at 51 s, reaching
$10^{-4}$ at 180 s (at 30, 60 and 120 s it is $0.075$, $0.0074$, $0.0001$). At the set-point the
**tracking error is essentially perfect at $5\cdot10^{-14}$**, and yet the estimate is

$$
\hat a = (-2.0943,\ 4.1927,\ 1.4563,\ 14.7150,\ 4.9050) \quad\text{versus}\quad
  a = (1.3333,\ 0.3333,\ 0.5,\ 14.7150,\ 4.9050),
$$

so **only the gravity parameters $a_4, a_5$ converge exactly** while the inertial ones $a_1,a_2,a_3$
stop at values whose sign is even wrong. The reason is visible in (6): with
$\dot q_d = \ddot q_d = 0$, columns 1, 2 and 3 (built only from $\ddot q_r$ and $\dot q_r$)
**become zero** after the transient, and only columns 4 and 5 (gravity) remain. The rank of the
Gram matrix falls from 5 to 2, and the adaptation law **cannot see** the error in the null-space
directions.

That is the trap of certainty equivalence. The inference "control works, so the estimated model may
be reused elsewhere (planning, simulation, another controller)" has **no basis** without PE.

## Proof sketch

### R3 — why persistent excitation gives parameter convergence

**Hypotheses** H1: from (4), $s \to 0$, $s \in L_2$, all signals bounded. H2: $W(t)$ is PE in the
sense of (5). H3: $W$ and $\dot W$ are bounded (a smooth bounded trajectory).
**Conclusion** C: $\tilde a \to 0$ exponentially.

**Strategy**: using $s \to 0$ reduces the error system to a **linear time-varying** one,
$\dot{\tilde a} = -\Gamma W^\top W \tilde a + (\text{vanishing terms})$, and PE is equivalent to
exponential stability of that LTV system.

1. **Reduction.** Since $s \to 0$, (7) gives $Y\tilde a \to 0$ and $Y \to W$ (the trajectory
   converges to the desired one). Rewriting the adaptation law in terms of the prediction error
   leaves $\dot{\tilde a} = -\Gamma W^\top W\tilde a$ as the dominant term with the rest vanishing
   in $L_2$ (omitted: the ISS treatment of the perturbation, Khalil ch.9).
2. **PE $\Rightarrow$ exponential stability.** With
   $U = \tfrac12\tilde a^\top\Gamma^{-1}\tilde a$ we get $\dot U = -\lVert W\tilde a\rVert^2 \le 0$,
   which can vanish instantaneously. So argue over an **interval**: (5) gives an $\alpha' > 0$ with
   $$
   U(t+T_0) - U(t) = -\int_t^{t+T_0}\lVert W\tilde a\rVert^2 d\sigma \le -\alpha'\,U(t)
   $$
   (show with H3 that $\tilde a$ barely changes over the interval, then use
   $\int W^\top W \succeq \alpha I$). So $U$ decreases **geometrically from interval to interval**,
   which is exponential convergence.
3. **Necessity.** Conversely, if PE fails — if for some unit vector $v$ and all $t$ the integral
   $\int_t^{t+T_0}\lVert Wv\rVert^2 \to 0$ — then the solution from $\tilde a(0) = cv$ has
   $\dot U \approx 0$ and does not converge. For the linear error system this argument is exact, so
   PE is **necessary and sufficient** (Boyd & Sastry 1986 §3).

**Remove a hypothesis**: without H3 (bounded $\dot W$) the approximation "$\tilde a$ is almost
constant over the interval" in step 2 fails and the interval argument collapses. Without the
boundedness in H1 the reduction of step 1 is impossible — and **unmodelled dynamics** break exactly
H1. Adaptation then pushes the estimate energetically in the wrong direction (drift) and excites
high-frequency modes until the loop goes unstable. That is what Rohrs et al. 1985 showed, and the
prescriptions either restrict the adaptation itself (projection, dead-zone, $\sigma$-modification)
or **structurally separate** adaptation speed from closed-loop bandwidth ($L_1$ adaptive control).

Technical steps omitted: Barbalat's lemma and the test for uniform exponential stability of LTV
systems (Khalil Lemma 8.2, Thm 8.5), and the quantitative form of the perturbed PE argument
(Boyd & Sastry 1986 §4).

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Derive the third column of (6) (the coefficient of $a_3$) in full. Show
how the $\cos q_2$ terms of $M$ and the $\sin q_2$ terms of $C$ merge into one column, and say why
$\dot q_2$ **does not appear** in the second row.
*Solution sketch*: the $a_3$ coefficients of $M\ddot q_r$ are $2c_2\ddot q_{r1}+c_2\ddot q_{r2}$ in
row 1 and $c_2\ddot q_{r1}$ in row 2, and factoring $h = -a_3s_2$ out of $C\dot q_r$ gives
$-s_2[\dot q_2\dot q_{r1} + (\dot q_1+\dot q_2)\dot q_{r2}]$ in row 1 and $+s_2\dot q_1\dot q_{r1}$
in row 2. The second entry of row 2 of $C$ is zero, which removes $\dot q_2$.

**P2 (derivation, ★★, R2)** Point to where the skew identity is used in deriving (4), and say why
it also holds for $s$ rather than $\dot q$. Then, what happens to $\dot V$ if the adaptation law's
sign is changed to $+\Gamma Y^\top s$?
*Solution sketch*: $\tfrac12\dot M - C$ is skew **as a matrix**, so its quadratic form vanishes for
any vector. Flipping the sign gives $\dot V = 2s^\top Y\tilde a - s^\top K_Ds$, which is sign
indefinite, and the stability argument is gone.

**P3 (proof, ★★★, R3)** Derive the geometric decrease
$U(t+T_0) \le (1-\alpha')U(t)$ of step 2 with an explicit $\alpha'$. How is the variation of
$\tilde a$ within the interval controlled?
*Solution sketch*: write $\tilde a(\sigma) = \tilde a(t) + \int_t^\sigma \dot{\tilde a}$ and bound
$\lVert\dot{\tilde a}\rVert \le \lVert\Gamma\rVert\lVert W\rVert^2\lVert\tilde a\rVert$ to get
$\lVert\tilde a(\sigma) - \tilde a(t)\rVert \le \epsilon\lVert \tilde a(t)\rVert$ on
$\sigma \in [t,t+T_0]$. Then
$\int\lVert W\tilde a\rVert^2 \ge \alpha\lVert\tilde a(t)\rVert^2(1-\epsilon)^2$.

**P4 (numerical, ★, R3·R4)** For the set-point $q_d = (0.3, -0.5)$ find ⓐ the rank and ⓑ the
smallest eigenvalue of the Gram matrix $\int_0^{10} W^\top W\,dt$, and the same two for the PE
trajectory $q_{d1} = 0.4\sin t + 0.3\sin\sqrt2 t$, $q_{d2} = 0.5\cos1.3t - 0.2\sin0.7t$.
*Answers*: set-point ⓐ 2 ⓑ $0$ (numerically $< 10^{-12}$); PE trajectory ⓐ 5 ⓑ $0.663$
(tolerance $10^{-2}$ with $\Delta t = 10^{-3}$ quadrature). Check: at a set-point the only non-zero
columns of (6) are 4 and 5.

**P5 (implementation, ★★, R2·R4)** Implement (3), meet the four acceptance criteria of the
reproduction task, and additionally tabulate ⓐ the parameter convergence time and ⓑ the peak
torque for $\Gamma = 2$, $20$, $200$.
*Rubric*: ⓐ convergence gets faster while ⓑ peak torque and high-frequency content grow —
the trade must be visible ⓒ a still larger $\Gamma$ forces a smaller $\Delta t$ (stiffness), shown
numerically ⓓ every number is reported with its $\Delta t$ and integrator.

**P6 (counterexample, ★★★, R5)** Build a Rohrs-type counterexample: put an unmodelled
**high-frequency pole** in the actuator (say $1/(\tau s + 1)$ with $\tau \ll 1$) and, on a
non-PE target, raise $\Gamma$ until you observe ① parameter drift ② bursting ③ divergence, in that
order. Then add projection or a dead-zone to prevent ③.
*Property checklist*: ⓐ first show that **without** the unmodelled dynamics the same $\Gamma$ is
stable (isolating the cause) ⓑ identify drift as the estimate running off in one direction without
bound ⓒ report the price of the dead-zone, namely a bias left in the tracking error.

**P7 (paper, ★★, R3·R5)** Read Boyd & Sastry 1986 and Rohrs et al. 1985 and write, in three
sentences each, ⓐ which **promise** of adaptive control each paper verifies or refutes, ⓑ whether
the Rohrs example violates the PE condition of Boyd-Sastry or some other assumption, ⓒ the lesson
each result carries for today's "learning-based control".
*Rubric*: distinguishing "PE gives convergence **under the assumption that the model class is
right**, and Rohrs breaks that very assumption" passes. Naming the same distinction (model-class
error versus lack of excitation) in learning-based control earns extra credit.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes and attack questions 4, 5, 6, 7 in the third.

1. **Slotine & Li, "On the adaptive control of robot manipulators" (1987, IJRR)**
   — role: `seminal`. <https://doi.org/10.1177/027836498700600303>
   §2-§3 are R1 and R2 of this lesson.
   Extra questions: ⓐ What quantity do the authors introduce to avoid measuring acceleration, and
   at what cost? ⓑ Does the paper claim parameter convergence or only tracking convergence — which
   sentence draws the distinction?
2. **Boyd & Sastry, "Necessary and sufficient conditions for parameter convergence in adaptive
   control" (1986, Automatica)** — role: `standard`.
   <https://doi.org/10.1016/0005-1098(86)90002-6>
   Extra questions: ⓐ Translated into the frequency domain (a count of spectral lines), what does
   PE become — what is the minimum number of frequencies for $p$ unknown parameters? ⓑ State the
   relation between "sufficient richness" and PE in one line.
3. **Rohrs, Valavani, Athans & Stein, "Robustness of continuous-time adaptive control algorithms
   in the presence of unmodeled dynamics" (1985, IEEE T-AC)** — role: `critique`.
   <https://doi.org/10.1109/TAC.1985.1104070>
   Extra questions: ⓐ Describe the route to instability **at the level of signals** (which
   frequency is excited and what amplifies it). ⓑ If the authors' conclusion is not "adaptive
   control is unusable", what exactly is it?

**The ten fixed questions**: (1) which problem under which assumptions (2) what exactly earlier
work could not do (3) the core idea in one equation (4) what is guaranteed and **what is not**
(5) independent and dependent variables and baselines, fairly tuned (6) do the metrics match the
claim, are variance and seeds reported (7) what is missing for reproduction (8) the first
assumption to doubt if the result is wrong (9) computational and memory complexity and real-time
feasibility (10) what you would change to go beyond it in a year.

## Reproduction task

**Tier R2 (re-implementation).** Budget: laptop CPU under ten minutes, numpy only. The target is
the two-link arm of (1) and there is no input data — the desired trajectories are given below as
formulas.

**Acceptance criteria (all four)**

1. **Regressor check**: over $10^3$ random $(q,\dot q,\ddot q)$ with
   $\lvert\dot q\rvert,\lvert\ddot q\rvert\le4$, setting $\dot q_r = \dot q$ and
   $\ddot q_r = \ddot q$, $\max\lvert Y a - (M\ddot q + C\dot q + g)\rvert < 10^{-12}$
   (reference: $7.1\cdot10^{-15}$).
2. **Measuring the excitation**: the smallest eigenvalue of $\int_0^{10}W^\top W\,dt$ is $\ge 0.5$
   on the PE trajectory (reference $0.663$, rank 5) and $< 10^{-10}$ with rank 2 at the set-point
   (reference $0$). Report both ranks.
3. **The PE trajectory**: integrate (3) for 180 s with $\Lambda = 4I$, $K_D = 20I$, $\Gamma = 20I$
   and $\hat a(0) = 0.5a$ ($\Delta t \le 5\cdot10^{-4}$), reaching
   $\lvert\tilde q\rvert_\infty < 10^{-4}$ over the last 10 s and
   $\lVert\tilde a\rVert/\lVert a\rVert < 10^{-3}$. Report the times to 5% and 1% (reference 35 s
   and 51 s).
4. **The set-point (counterexample)**: with the same gains, track $q_d = (0.3,-0.5)$ for 180 s and
   show $\lvert\tilde q\rvert_\infty < 10^{-6}$ **while**
   $\lVert\tilde a\rVert/\lVert a\rVert > 0.1$, and confirm that only the gravity components
   converge: $\lvert\hat a_4 - a_4\rvert/a_4 < 10^{-3}$ and
   $\lvert\hat a_5-a_5\rvert/a_5 < 10^{-3}$ while
   $\lvert \hat a_1 - a_1\rvert/\lvert a_1\rvert > 0.5$ (reference: tracking $4.8\cdot10^{-14}$,
   parameter error $0.337$, $\hat a_1 = -2.09$).

**Baseline**: the non-adaptive computed-torque controller with the **wrong** parameters $0.5a$ —
with the same gains its tracking error over the last 10 s must remain at $0.127$ rad on the PE
trajectory and $0.119$ rad at the set-point (the control group that shows what adaptation actually
buys).

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| $V$ increases | sign error in the adaptation law, or $\ddot q$ used instead of $\ddot q_r$ | print $\dot V + s^\top K_Ds$ every step and check that it is zero |
| Tracking works but criterion 1 fails | $\dot q$ and $\dot q_r$ mixed up in the third column of $Y$ | set $\dot q_r = \dot q$ and pass criterion 1 first |
| Parameters do not converge even on the PE trajectory | the excitation frequencies are in **rational** ratio, so the columns are dependent | mix in an irrational ratio such as $\sqrt2$ and measure $\lambda_{\min}$ of criterion 2 again |
| Divergence in criterion 3 | $\Gamma$ so large that adaptation outruns the integrator (stiffness) | halve $\Delta t$ and see whether the result changes — if it does, the integrator is the problem |
| Tracking error in criterion 4 stalls near $10^{-3}$ | the gravity parameters are still converging (transient) | integrate longer or raise $\Lambda$; by 180 s it reaches about $10^{-13}$ |

## Open problems

- **(open problem) Control that creates its own excitation** — PE is a property of the trajectory,
  so the problem becomes generating, **online**, a trajectory that both tracks and excites enough.
  When the task demands a set-point, excitation conflicts with the task. Current approaches:
  concurrent learning, which reuses past data, and trajectory optimisation with the information
  matrix in the cost (overlapping `c4-mpc`). The gap: a design that gives the Pareto frontier
  between task performance and identification quality.
- **(open problem) Adaptation under model-class error** — the essence of the Rohrs counterexample
  is that the **structure**, not the parameters, is wrong. $L_1$ adaptive control separates
  adaptation speed from robustness with a filter
  ([Cao & Hovakimyan 2006](https://doi.org/10.1109/ACC.2006.1657244)), but the choice of filter
  bandwidth sets a performance limit. The gap: turning the size of the structural error into a
  **measurable quantity** and setting the adaptation bandwidth from it.
- **(open problem) Joining learning and adaptation** — learning residual dynamics with a neural
  network and adapting only linear coefficients online has worked on real hardware
  ([O'Connell et al., Neural-Fly, 2022](https://doi.org/10.1126/scirobotics.abm6597)). But there is
  still no guarantee for the case where the learned basis **does not contain** the true dynamics.
  The gap: an explicit map from basis-representation error to tracking and convergence guarantees —
  the same wall as the open problem in `c3-contraction-incremental`.
- **(open problem) Adaptation with contact and friction** — Coulomb friction is linear in the
  parameters but non-smooth, so the regressor is undefined near $\dot q \approx 0$, and contact
  switching breaks PE piecewise. The gap: an identifiability theory that includes non-smooth terms —
  it returns from the identification side in `c2-contact-dynamics` and
  `c2-dynamics-derivatives-sysid`.

## Concept check

Take it with `rc quiz c3-adaptive-control`. The quiz is **for concept checking only**; the real
work is the problem set and the reproduction task above (`lesson-standard.md` §4). Four questions
ask: what it means that no parameter-error term appears in $\dot V = -s^\top K_D s$; the PE
condition as an integral inequality; whether converged tracking licenses reuse of the estimated
parameters; and why the Gram rank falls from 5 to 2 at a set-point.

## How to study this stage

1. **Build $Y$ by hand (60 min)** — solve P1 first. Do not copy (6): expand
   $M\ddot q_r + C\dot q_r + g$ and collect column by column, then pass criterion 1 in code.
   **If the regressor is wrong, everything else in this lesson is meaningless.**
2. **Use the cancellation twice (40 min)** — the gravity and $\ddot q_r$ cancellation in (7), and
   the $s^\top Y\tilde a$ cancellation in (4). Both say the same thing: the design is built to
   produce a cancellation. Flipping the sign of the adaptation law shows why that form is forced
   (P2).
3. **See PE as a Gram matrix (40 min)** — run criterion 2 and confirm $\lambda_{\min}=0$ at the
   set-point. This is the step where PE stops being an abstract condition and becomes **a matrix
   rank**.
4. **Run the counterexample first (60 min)** — do criterion 4 (the set-point) **before**
   criterion 3. Anyone who has watched perfect tracking next to a wrong parameter vector never
   forgets the trap of certainty equivalence.
5. **Then confirm convergence on the PE trajectory (60 min)** — criterion 3. Check in the
   diagnosis table why irrational frequency ratios are used, and watch convergence slow down when
   you switch to a rational ratio.
6. **Meet the wall of robustness (90 min)** — the Rohrs-type experiment of P6. Insert an
   unmodelled pole and raise $\Gamma$ until **the same code** goes unstable, then stop it with
   projection or a dead-zone. That experience explains the motivation for $L_1$ adaptive control.
7. **Read the papers as "promise and refutation" (150 min)** — Slotine & Li promise, Boyd & Sastry
   give the exact condition for that promise, and Rohrs shows the collapse outside the
   assumptions. Writing one paragraph on how the three relate finishes this lesson.

**Passing bar**: you can derive one column of (6) and all of (4) from memory, write the PE
condition as an integral inequality, produce numerically a case where tracking succeeds and
identification fails, and you have code meeting all four acceptance criteria plus one-page notes on
the three papers.
