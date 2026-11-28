---
id: s3-dynamic-maneuvers
lang: en
title: Rough terrain and dynamic maneuvers
summary: >-
  Look at dynamic maneuvers such as jumps and gap crossings from two sides. On the planning side,
  count that the number of contact schedules explodes as $2^{nN}$ and that a minimum dwell-time
  constraint merely lowers the base from 2 to 1.32 without removing the exponential, and derive
  that the stance time of a jump is fixed by the leg stroke as $T_s = 2L/v$, at which the force
  needed is $1 + h/L$ times body weight. On the evaluation side, start from the fact that "10
  successes out of 10" says only that the success rate is at least 69%, fit a success-probability
  curve against difficulty to estimate the operating limit (the difficulty of 90% success) with
  its interval, and design where to place the trials. The final deliverable is an analysis of the
  maneuver results of real papers in the same framework.
objectives:
  - Count contact schedules and derive, from the characteristic equation, their growth rate under a minimum dwell-time constraint.
  - Derive the stance time and ground reaction force of a jump from the leg stroke and the jump height, and find the effort-optimal stance time.
  - Derive and compute the sensitivity of the jump height to an error in stance time.
  - Fit a success-probability curve to success and failure data by difficulty and estimate the operating limit with its interval.
  - Design in advance the success criterion, the number of trials and the placement of difficulties for a maneuver evaluation, and justify the design.
tags: [legged-robots, dynamic-maneuvers, contact-schedule, jumping, hardware-evaluation, research]
---

# Rough terrain and dynamic maneuvers

## Setup and notation

This is the last lesson of S3. Where the earlier lessons covered the **nominal operation** of
legged locomotion (periodic orbits, centroidal MPC, whole-body control, learned policies), this
one covers what lies outside it — jumps, gaps, irregular terrain. There are two questions: **how
to plan** (when and where to place contacts) and **how to show that it was done** (how many
attempts with how many successes warrant saying "it works"). Complementarity and transitions of
contact are those of `c4-contact-implicit-hybrid`, centroidal dynamics those of
`s3-centroidal-mpc`, and the statistics of evaluation those of `s4-evaluation-science` and
`s5-field-deployment`. The recommended prerequisites are `s3-centroidal-mpc`,
`s3-locomotion-rl` and `c4-contact-implicit-hybrid`.

| Symbol | Meaning |
|---|---|
| $n$, $N$ | Number of legs and number of time steps of the planning horizon |
| Contact schedule | The binary table ($n \times N$) of whether each leg touches the ground at each step |
| $m$ | Minimum dwell time — once begun, a stance or a flight lasts at least $m$ steps |
| $h$, $L$ | Jump height (rise of the centre of mass) and leg stroke (the distance the centre of mass can travel during stance) |
| $v$, $T_s$ | Takeoff speed $\sqrt{2gh}$ and stance time |
| $F$ | Ground reaction force during stance (vertical). $mg$ is body weight |
| $g$ | (difficulty) The difficulty variable of the maneuver — in the example of this lesson, the width of the gap to cross |
| $p(g)$ | Probability of success at difficulty $g$ |
| $g_{50}$, $g_{90}$ | The difficulty at which the success probability is 50% and 90%. $g_{90}$ is **the operating limit** |

## Key results

The bracket gives the derivation depth (D0 cited / D1 skeleton / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (the explosion of contact schedules) [D2]** — there are $2^{nN}$ contact schedules for
  $n$ legs and $N$ steps ($1.2\times10^{24}$ for a quadruped over 20 steps). Under the constraint
  that every stance and flight segment lasts at least $m$ steps, the number of schedules of one
  leg grows as $\rho_m^N$, where $\rho_m$ is the largest root of
  $$
  x^m = x^{m-1} + 1. \tag{1}
  $$
  $\rho_1 = 2$, $\rho_2 = 1.618$, $\rho_3 = 1.466$, $\rho_5 = 1.325$. At $N = 20$, $m = 5$ there
  are 68 for one leg and $2.1\times10^7$ for four — **the constraint lowers the base but does not
  remove the exponent.** So real systems fix the schedule (a gait), optimize only the timings as
  continuous variables, or treat contact implicitly.
- **R2 (the stance time of a jump is set by the stroke) [D2]** — jumping to height $h$ with a
  constant force requires
  $$
  T_s = \frac{2L}{v}, \qquad \frac{F}{mg} = 1 + \frac{h}{L}. \tag{2}
  $$
  For $h = 0.5$ m and $L = 0.25$ m, $T_s = 0.160$ s and $F = 3mg$. The stance time that minimizes
  the integral of the squared force (the effort) is $T_s^\star = v/g$, at which $F = 2mg$ and the
  stroke needed **equals the jump height** ($L = h$). With a shorter stroke the stance time
  shrinks and the force grows — **the contact schedule is not chosen freely; the mechanism and
  the actuators set it.**
- **R3 (sensitivity to an error in stance time) [D2]** — if the stance is longer or shorter by
  $\delta T$, the takeoff speed changes by $(F/m - g)\,\delta T$ and the jump height by
  $$
  \delta h = \frac{v}{g}\Big(\frac{F}{m} - g\Big)\delta T = \frac{2h}{T_s}\,\delta T. \tag{3}
  $$
  In the example above $\delta T = 10$ ms gives $6.3$ cm, **12.5%** of the height. This is why
  dynamic maneuvers demand precision in contact timing, and since the relative error is
  $2\,\delta T/T_s$, **the shorter the stance the greater the sensitivity**.
- **R4 (what "10/10 successes" means, and estimating the operating limit) [D2]** — succeeding in
  all 10 attempts at one difficulty supports, at 95% confidence, only a success rate
  $\ge 0.692$. Using the difficulty axis says more: model the success probability as
  $$
  p(g) = \frac{1}{1 + \exp\big((g - g_{50})/s\big)} \tag{4}
  $$
  and fit by maximum likelihood to obtain $g_{90} = g_{50} - s\ln 9$. On the 60 trials of the
  reproduction task $\hat{g}_{90} = 0.506$ m (truth $0.490$) with a bootstrap 95% interval of
  $[0.463, 0.566]$ m — **60 trials determine the operating limit to about $\pm5$ cm.**
- **R5 (where to place the trials) [D2]** — for the same 60 trials the estimation error of
  $g_{90}$ depends on the placement of difficulties. The RMSE is $0.036$ for 6 uniform levels,
  $0.034$ for 3 levels near the 90% point (but the fit degenerates in 4.6% of cases), $0.044$ for
  2 levels, and $0.026$ m for a 3-successes-1-failure staircase. **A design that adaptively
  gathers the trials near the limit is 27% better.** A demonstration that piles up successes
  under easy conditions says nothing about the limit.

## Derivation

### R1 — counting contact schedules

**Unconstrained.** Each leg at each step has the two choices touching/airborne, hence $2^{nN}$.
The trajectory optimization within each schedule is a smooth problem (the fixed-mode problem of
`c4-contact-implicit-hybrid`), but the number of schedules is exponential.

**Minimum dwell time.** Physically, contacts and flights that are too short are useless (no time
to produce force, no time to move the leg). Let $c_N$ be the number of binary sequences of length
$N$ in which every run has length at least $m$. Splitting by the length of the last run — exactly
$m$, or longer (in which case the sequence with its last step removed is also valid) —

$$
c_N = c_{N-1} + c_{N-m} \quad (\text{for } N \text{ large enough}), \tag{5}
$$

($c_{N-1}$: the last run extended by one step; $c_{N-m}$: a new run of length $m$ appended — the
symbol of the new run is forced to be the opposite of the preceding one). The characteristic
equation is (1) and $c_N \sim \rho_m^N$.

| $m$ | $\rho_m$ | $c_{10}$ | $c_{20}$ | $c_{40}$ |
|---|---|---|---|---|
| 1 | $2.000$ | $1024$ | $1.05\times10^6$ | $1.10\times10^{12}$ |
| 2 | $1.618$ | $68$ | $8362$ | $1.26\times10^8$ |
| 3 | $1.466$ | $18$ | $812$ | $1.70\times10^6$ |
| 5 | $1.325$ | $4$ | $68$ | $1.90\times10^4$ |

**Four legs.** $N = 20$, $m = 5$: with independent legs $68^4 = 2.1\times10^7$. Tying the
diagonal legs together (the trot structure) gives $68^2 = 4624$. Choosing the gait among five
(walk, trot, pace, bound, gallop) gives 5.

**Three remedies.** (a) **Fix the schedule** — pick from a gait library and set the timings by
the period. Convex MPC in the style of `bledt2018-mit-cheetah` works this way, and given the
schedule the problem is convex (a QP) (`s3-centroidal-mpc`). The price is that motions absent
from the schedule cannot be done. (b) **Fix the order and make the timings continuous
variables** — set, for each leg, the order "stance–flight–stance…" and take the **duration** of
each segment as an optimization variable (`winkler2018-phase-based`). The binary variables
disappear and a smooth nonlinear program remains, but the **number** of segments has to be fixed
in advance. (c) **Treat contact implicitly** — obtain the schedule as an output through
complementarity constraints (`c4-contact-implicit-hybrid`). The schedule is unrestricted but the
problem is non-convex and real time is hard. `grandia2023-perceptive-locomotion` is given the
schedule and optimizes **the foothold positions** inside convex regions of the terrain — a
structure in which perception filters the exploding discrete choices beforehand.

**Where the assumptions break**: the count of (5) takes a "step" to have a fixed length. In a
real maneuver the stance time itself is set by physics as in R2, so a uniform grid does not fit,
and refining the grid increases $N$ and makes the count explode again. And contact is not only
feet — in multi-contact maneuvers that brace with knees, the trunk or hands, the number of
contact **candidates** itself increases $n$.

### R2 — the jump: stroke, force, stance time

**The model.** A point of mass $m$ accelerates under a vertical force $F$ during stance and takes
off when the leg is fully extended (when the centre of mass has risen by $L$). After takeoff the
motion is ballistic.

**Constant force.** Covering the distance $L$ with acceleration $a = F/m - g$ gives $v^2 = 2aL$
and $T_s = v/a = 2L/v$. After takeoff $h = v^2/(2g)$, so $a = v^2/(2L) = gh/L$, that is
$F/(mg) = 1 + h/L$ — this is (2).

| Jump height $h$ | Stroke $L$ | Takeoff speed | $T_s$ | $F/mg$ |
|---|---|---|---|---|
| $0.25$ m | $0.25$ m | $2.21$ m/s | $0.226$ s | $2.00$ |
| $0.5$ m | $0.15$ m | $3.13$ m/s | $0.096$ s | $4.33$ |
| $0.5$ m | $0.25$ m | $3.13$ m/s | $0.160$ s | $3.00$ |
| $0.5$ m | $0.5$ m | $3.13$ m/s | $0.319$ s | $2.00$ |
| $1.0$ m | $0.25$ m | $4.43$ m/s | $0.113$ s | $5.00$ |

**The effort-optimal stance time.** Without a stroke constraint, what stance time is best?
Measuring the effort by $\int_0^{T}F^2dt$ and producing the takeoff speed $v$ with a constant
force, $F = m(v/T + g)$ and

$$
E(T) = m^2\Big(\frac{v}{T} + g\Big)^2T, \qquad
\frac{dE}{dT} = m^2\Big(\frac{v}{T} + g\Big)\Big(g - \frac{v}{T}\Big) = 0
\;\Longrightarrow\; T^\star = \frac{v}{g}. \tag{6}
$$

Then the acceleration is $g$, the force $2mg$, and the stroke used is
$vT^\star/2 = v^2/(2g) = h$. **The effort-optimal jump pushes with twice body weight over a
stroke equal to the height jumped.** A robot whose stroke is shorter than $h$ cannot reach that
optimum and has to go to the shorter stance and larger force of (2). The ratio of efforts is
$E(T_s)/E(T^\star) = (1 + h/L)^2(L/h)/4$, that is $1.125$ at $L = h/2$ and $1.41$ at $L = 0.3h$.

**How to read it.** (a) The stance times of the table are $0.1$–$0.3$ s — shorter than the
stance of nominal walking (hundreds of ms), within which 3 to 5 times body weight has to be
produced. **The peak torque and the bandwidth** of the actuators are the limit of the maneuvering
capability — the reason quasi-direct drives of high torque density became the hardware standard
of this field (`katz2019-mini-cheetah`). (b) If a planner **assumes** "stance 0.3 s" and demands
$h = 0.5$ m, a stroke of $L = 0.47$ m is needed. If the mechanism cannot provide it the plan is
infeasible — the schedule and the trajectory cannot be decided separately.

**Where the assumptions break**: a constant force is an idealization. In a real stance the
vertical force a leg can produce depends on its posture through the kinematics (it drops as the
knee straightens), and actuators have a speed-dependent torque limit — the faster the extension,
the smaller the force. The actual takeoff speed is therefore below (2). And the point-mass model
ignores the rotation of the trunk: holding the attitude during a jump requires keeping the
angular momentum near zero, which restricts the line of action of the force (the centroidal
dynamics of `s3-centroidal-mpc`).

### R3 — sensitivity to contact timing

If the stance lasts $\delta T$ longer than planned (takeoff is detected late, or the control
period is out of step), the acceleration $a = F/m - g$ continues for that time and
$\delta v = a\,\delta T$. From $h = v^2/(2g)$,

$$
\delta h = \frac{v}{g}\,\delta v = \frac{v\,a}{g}\,\delta T, \qquad
\frac{\delta h}{h} = \frac{2a}{v}\,\delta T = \frac{2\,\delta T}{T_s}, \tag{7}
$$

using $T_s = v/a$ at the end. This is (3).

| $\delta T$ ($h = 0.5$ m, $L = 0.25$ m, $T_s = 0.16$ s) | $\delta v$ | $\delta h$ | Relative error |
|---|---|---|---|
| 5 ms | $0.098$ m/s | $3.1$ cm | $6.3\%$ |
| 10 ms | $0.196$ m/s | $6.3$ cm | $12.5\%$ |
| 20 ms | $0.392$ m/s | $12.5$ cm | $25.1\%$ |

**How to read it.** Even with a 1 kHz control loop, the detection of contact (a force threshold,
the foot speed) has a delay of several ms. An error of $10$ ms changes the height by $12.5\%$,
and the landing point is the product of horizontal speed and flight time, so in a gap crossing
it **separates success from failure**. This is why "landing short" is the most common failure
mode of the reproduction task. And the relative error of (7) is inversely proportional to $T_s$
— the robot of R2 with a short stroke and therefore a short stance is shaken more by the same
timing error.

**Where the assumptions break**: (7) considers only the timing error at the end of stance.
Landing is worse — if the touchdown time is mispredicted the leg is not yet extended, or is
already pushing on the ground. The impact of landing is the reset map of
`c4-contact-implicit-hybrid` and its sensitivity is computed through the saltation matrix. One
reason learned policies (`s3-locomotion-rl`) are strong at dynamic maneuvers is that they do not
estimate contact timing explicitly but react implicitly from the proprioceptive history.

### R4 — success rate, and the operating limit

**At one difficulty.** A gap of $0.48$ m was attempted 10 times and crossed 10 times. The
Clopper–Pearson lower limit of `s4-evaluation-science` R1 is $0.025^{1/10} = 0.692$. The
statistical content of "crosses reliably" is "the success rate is at least 69%".

**Use the difficulty axis.** A maneuver usually has a continuous difficulty (the width of a gap,
the height of a step, a slope, a speed). Take the success probability to be an S-shaped curve
decreasing monotonically in difficulty and fit (4). For data $(g_i, y_i)$, $y_i \in \{0, 1\}$,
the log-likelihood is

$$
\ell(g_{50}, s) = \sum_i\Big[y_i\log p(g_i) + (1 - y_i)\log\big(1 - p(g_i)\big)\Big] \tag{8}
$$

and it is maximized. The operating limit is, from $p(g_{90}) = 0.9$,
$g_{90} = g_{50} - s\ln 9$.

**The trial log of the reproduction task** (6 levels × 10 trials, true model $g_{50} = 0.60$ m,
$s = 0.05$ m):

| Gap (m) | Successes / 10 | Clopper–Pearson 95% interval | True success probability |
|---|---|---|---|
| $0.40$ | 10 | $[0.692, 1.000]$ | $0.982$ |
| $0.48$ | 10 | $[0.692, 1.000]$ | $0.917$ |
| $0.56$ | 6 | $[0.262, 0.878]$ | $0.690$ |
| $0.64$ | 3 | $[0.067, 0.652]$ | $0.310$ |
| $0.72$ | 1 | $[0.003, 0.445]$ | $0.083$ |
| $0.80$ | 0 | $[0.000, 0.308]$ | $0.018$ |

The fit: $\hat{g}_{50} = 0.600$ m, $\hat{s} = 0.043$ m, $\hat{g}_{90} = 0.506$ m (truth
$0.490$). The 95% interval over 2000 bootstrap resamples of the trials is $[0.463, 0.566]$ m.

**How to read it.** (a) The per-level intervals are wide ($[0.26, 0.88]$ at $0.56$ m). But
**fitting the whole curve lets the 60 trials help one another** — $g_{90}$ is known to
$\pm5$ cm. Looking at each level separately cannot answer "how far does it work". (b) The
operating limit $0.51$ m differs from the hardest success (1 at $0.72$ m). What appears in videos
is the latter. **The largest difficulty at which it once succeeded is not a measure of
capability but the tail of a distribution** — in the table above the true success probability at
$0.72$ m is 8%. (c) Failures are data too. The mode classification of the 30 failed trials is
landing short 17, slip at takeoff 8, instability after landing 5, and "what to fix first" is
decided in the manner of `s5-field-deployment` R4 (problem P5).

**Where the assumptions break**: (a) (4) takes the success probability to be a function of
**one** difficulty. In reality several conditions are mixed in (approach speed, ground friction,
battery voltage), and if they vary from trial to trial the curve looks flatter than it is ($s$
grows). (b) The logistic form is a choice. It cannot capture the shape of the tail (failures
that remain at easy difficulties — causes unrelated to difficulty, such as a slip). In that case
a **floor failure rate** $\epsilon$ has to be included, as in $p(g) = (1-\epsilon)\cdot$(4), and
leaving it out biases $g_{90}$ (problem P6). (c) Trials were taken to be independent. Adjusting
after a failure and trying again is the routine of field testing, and then the later trials
concern a different system from the earlier ones (`s5-field-deployment` R5).

### R5 — the placement of trials

**The question.** With a budget of 60 trials, at which difficulties should one attempt in order
to know $g_{90}$ most accurately?

**Intuition.** Trials at a difficulty whose success probability is near 0 or 1 carry little
information — the outcome is already known. In the logistic model the Fisher information of one
trial is proportional to $p(1-p)$, so the location $g_{50}$ is determined by trials near
$p = 0.5$ and the slope $s$ by trials on either side. $g_{90}$ is a combination of the two, so
trials **spread around the limit** are good. The trouble is that where the limit lies is
**unknown** (that is what the test is for), hence adaptive designs.

**Four designs compared** (60 trials each, 3000 simulations, estimation error of $g_{90}$):

| Design | Placement of difficulties | RMSE (m) | Bias (m) | Degenerate fits |
|---|---|---|---|---|
| Uniform | 6 levels over $0.40$–$0.80$ × 10 | $0.0356$ | $+0.005$ | $0\%$ |
| Near the limit | $0.44, 0.49, 0.54$ × 20 | $0.0336$ | $+0.002$ | $4.6\%$ |
| Two levels | $0.49, 0.60$ × 30 | $0.0439$ | $0.000$ | $0\%$ |
| Staircase | $+0.03$ after 3 consecutive successes, $-0.03$ after a failure | $0.0260$ | $+0.008$ | $0\%$ |

**How to read it.** (a) The staircase has an RMSE 27% below the uniform placement. A staircase
makes things harder after a run of successes and easier after a failure, so it **gathers near
the limit by itself** — the 3-successes-1-failure rule converges to the difficulty with a
success probability of about 79%. (b) The "near the limit" design was chosen **knowing** the
truth and is still worse than the staircase, and its fit degenerates in 4.6% of cases (when
almost everything succeeds at all three levels the slope cannot be determined). Concentrating on
a narrow range loses the slope information. (c) The two-level design is the worst — with two
levels the two parameters are barely determined and there is no way to see whether the model is
wrong.

**What to fix in advance.** What a maneuver evaluation plan has to answer: (a) **the operational
definition of success** — what if it crossed but fell? Crossed and fell three steps later? Was
caught by the operator? Choosing the definition after seeing the results yields whatever success
rate is wanted. (b) **The difficulty variable and its range**, and the conditions to be held
fixed (approach speed, ground). (c) **The number of trials and the placement rule** (for a
staircase: the starting point, the step, the stopping condition). (d) **A record of every
attempt** — not only the successes. (e) **The moments at which the system was changed** — data
after a change belong to a new curve.

**Where the assumptions break**: a staircase requires that the difficulty **can be changed** from
trial to trial. Adjusting the width of a gap by 3 cm is easy, but difficulties such as the
roughness of terrain or the arrangement of rocks are not continuous variables and are hard to
reproduce. And if a failure **damages the hardware**, trials near the limit are expensive — the
most informative trials are the most dangerous ones. A design that includes that trade (a
sequential design accounting for the cost of failure) is needed, and in practice the answer is
to get the rough shape of the curve from simulation first and spare the hardware trials.

## Problem set

The answer policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Derive (5) (including the initial conditions) and show that for
$m = 2$, $c_N$ is twice a Fibonacci number. Then find the characteristic equation when the
constraint is asymmetric: "stance at least $m_s$ steps, flight at least $m_f$ steps".
*Answer sketch*: the length generating function of one period (a stance run + a flight run) is
$x^{m_s+m_f}/((1-x)^2)$, so the growth rate is the reciprocal of the smallest positive root of
$(1-x)^2 = x^{m_s+m_f}$. For $m_s = m_f = m$ this is $1 - x = x^m$, the same as (1) (with
$x \to 1/x$).

**P2 (derivation, ★★, R2)** Derive (2) and (6), and write the maximum height that can be jumped
when the force is limited to $F_{\max}$, in terms of $F_{\max}$ and $L$. Then, for a jump across
a gap of **horizontal distance** $w$, assume a takeoff angle of $45^\circ$ and find the takeoff
speed and the $F/mg$ required ($w = 0.6$ m, $L = 0.25$ m).
*Answer sketch*: $h_{\max} = (F_{\max}/mg - 1)L$. The gap: from the range $w = v^2/g$,
$v = \sqrt{gw} = 2.43$ m/s, acceleration along the takeoff direction $a = v^2/(2L) = 11.8$ m/s²,
and pushing at $45^\circ$ against gravity needs a force of magnitude
$m\sqrt{(a/\sqrt2)^2 + (a/\sqrt2 + g)^2} \approx 2.0\,mg$.

**P3 (derivation, ★★, R4)** Write the score equations of (8) (gradient = 0), and show that for
data in which the success rate is 0 or 1 at every level (complete separation) the
maximum-likelihood estimate does not exist. State when that situation arises in an actual
maneuver evaluation.
*Answer sketch*: for separated data the likelihood grows as $s \to 0$ (a step function fits
perfectly). It arises when attempts were made only at easy levels and all succeeded, or when the
spacing between levels is much larger than the width of the curve. "All succeeded" means there
is no information about the limit.

**P4 (numerical, ★, R2, R3, R4)** (a) For a robot of mass 12 kg and stroke 0.2 m, find the force
and the stance time needed to jump 0.4 m and the height error produced by a 5 ms timing error.
(b) Find the 95% interval for 14 successes out of 15 at one difficulty. (c) For
$\hat{g}_{50} = 0.62$, $\hat{s} = 0.04$, find $g_{90}$ and $g_{99}$.
*Answer*: (a) $F = (1 + 0.4/0.2)mg = 3\times117.7 = 353$ N, $v = 2.80$ m/s, $T_s = 0.143$ s,
$\delta h = 2h\,\delta T/T_s = 0.028$ m (7%). (b) $[0.681, 0.998]$.
(c) $g_{90} = 0.62 - 0.04\ln 9 = 0.532$, $g_{99} = 0.62 - 0.04\ln 99 = 0.436$. (Tolerance 1%.)
*Check*: in (c) see that 90% and 99% are $0.096$ m apart — **raising the reliability requirement
pushes the operating limit back a long way**.

**P5 (implementation, ★★★, R4, R5)** Add an analysis by failure mode to the trial log of the
reproduction task: show, by a multinomial logistic model or a per-level table, how the weight of
each mode changes with difficulty (landing short at large gaps, slips evenly), and estimate the
$g_{90}$ that would result from removing each mode.
*Rubric*: (a) report the counts per mode with their Clopper–Pearson intervals (b) test the
association between difficulty and mode (for example, compare the half with large gaps to the
half with small gaps) (c) build the hypothetical success curve with "landing short" removed and
find the change in $g_{90}$ (d) show that a mode **unrelated** to difficulty governs $g_{99}$
rather than $g_{90}$.

**P6 (counterexample, ★★, R4)** (a) Give, from the log of the reproduction task, a
counterexample to "the hardest successful case is the capability of the robot". (b) Generate
data with a difficulty-independent floor failure rate $\epsilon = 0.05$, show in which direction
$g_{90}$ is biased when (4) is fitted as it stands, and compare with the model that includes the
floor.
*Property checklist*: (a) uses the single success at $0.72$ m and states with it the true success
probability of that difficulty (8%) and the interval $[0.003, 0.445]$. (b) simulates at least
500 times and reports **the sign and the size** of the bias — the floor failures cut the success
rate of the easy levels and flatten the curve, and in which direction that pushes $g_{90}$
depends on the design, so it has to be measured.

**P7 (paper, ★★, R1, R4, R5)** Read `bledt2018-mit-cheetah` and
`grandia2023-perceptive-locomotion` and (a) classify how each system determines the contact
schedule (fixed, timing optimization, implicit) into the three remedies of R1, (b) for each
maneuver the papers report (jumps, stairs, gaps, …) find **the number of attempts and the number
of successes**, tabulate them and attach Clopper–Pearson intervals, (c) check whether the
definition of success is stated and whether the limit was sought by varying the difficulty,
(d) separate which of the five "what to fix in advance" items of R5 the papers answer and which
they do not.
*Rubric*: (a) passes by quoting the supporting sentence. (b) is the core — a maneuver whose
count is not reported is recorded as **"count not reported"** (a single video does not even
count as $n = 1$ — because the number of attempts is unknown). (c) and (d) are submitted as a
table. Discovering that most cells are filled with "not reported" is the answer to this problem.

## Paper reading

**Two must-read papers.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read in three passes, and in the third pass concentrate on questions 5,
6 and 7.

1. **Bledt, Powell, Katz, Di Carlo, Wensing & Kim, "MIT Cheetah 3: design and control of a
   robust, dynamic quadruped robot" (2018, IROS)** — role: `standard`.
   <https://doi.org/10.1109/IROS.2018.8593885> (the part on the mechanical and actuator design
   and the part on the control architecture)
   A system paper that reports the hardware design (the stroke and force of R2) together with
   the control (a fixed schedule + reaction-force planning).
   Additional questions: (a) computing from (2) the height that can be jumped with the stroke of
   the leg and the peak force of the actuators, what is it, and does it agree with the maneuvers
   the paper reports? (b) how is the contact schedule given and how is contact detected (R3)?
   (c) are the experimental results presented as videos, figures or tables, and is there a
   number of trials?
2. **Grandia, Jenelten, Yang, Farshidian & Hutter, "Perceptive locomotion through nonlinear model
   predictive control" (2023, IEEE T-RO)** — role: `frontier`.
   <https://arxiv.org/abs/2208.08373> (the part on the problem formulation and the experimental
   part)
   A system that walks rough terrain by putting the convex foothold regions obtained from terrain
   perception into the MPC as constraints. The case study for "perception filters the discrete
   choices beforehand" of R1 in this lesson.
   Additional questions: (a) who determines the contact schedule and who the foothold
   **positions** (fixed, optimized, perception)? (b) what is the defence when perception is
   wrong (holes in the map, a wrong plane)? (c) how do the authors report the number of hardware
   trials and the failure cases?

**Two recommended papers.** `winkler2018-phase-based` (trajectory optimization that takes the
durations of the contact segments as continuous variables — remedy (b) of R1,
<https://doi.org/10.1109/LRA.2018.2798285>) and `katz2019-mini-cheetah` (actuator and mechanism
design for dynamic maneuvers — the hardware side of R2,
<https://doi.org/10.1109/ICRA.2019.8793865>).

**The ten fixed questions**: (1) what problem is solved under what assumptions (2) what exactly
could earlier work not do (3) the key idea in one line of mathematics (4) what is the theoretical
guarantee and **what is not guaranteed** (5) the independent and dependent variables and baselines
of the experiments, and were they tuned fairly (6) do the metrics match the claims, and are
variance and seeds reported (7) what information needed for reproduction is missing (8) if it is
wrong, which assumption to suspect first (9) computational and memory complexity and real-time
capability (10) what would you change to surpass it a year from now.

## Reproduction task

**Tier R3 (re-analysis of published results).** Compute budget: one laptop CPU core, under 3
minutes in total, at most 500 MB of memory. numpy + scipy only. No robot or simulator is needed.

The task has two halves. **Parts A–D** build and validate the analysis tools on a trial log
produced by a generator (data whose true model is known). **Part E** applies those tools to
**published maneuver results**.

```python
"""Reproduction task of s3-dynamic-maneuvers: generator of a gap-crossing trial log."""

import numpy as np

SEED = 20261117
G50, S = 0.60, 0.05  # true success curve: 50% point 0.60 m, scale 0.05 m
LEVELS = (0.40, 0.48, 0.56, 0.64, 0.72, 0.80)


def success_prob(gap):
    return 1.0 / (1.0 + np.exp((gap - G50) / S))


def trial_log(rng, levels=LEVELS, n_per=10):
    """Gap width, success flag, failure mode (-1 success, 0 short, 1 takeoff slip, 2 unstable)."""
    gap = np.repeat(levels, n_per)
    ok = rng.random(gap.size) < success_prob(gap)
    w = np.stack(
        [np.clip((gap - 0.5) / 0.3, 0.05, 0.9), np.full(gap.size, 0.25), np.full(gap.size, 0.2)],
        1,
    )
    w = w / w.sum(1, keepdims=True)
    mode = np.array([rng.choice(3, p=wi) for wi in w])
    return gap, ok, np.where(ok, -1, mode)
```

**Conventions.** "The log" is one call of `trial_log` on a generator created with
`np.random.default_rng(SEED)`. The bootstrap and the simulations of Part D use a generator
**newly** created with `SEED`. The logistic fit is an unconstrained minimization over
$(g_{50}, \log s)$.

**Part A — the number of contact schedules.** For $m \in \{1, 2, 3, 5\}$ and
$N \in \{10, 20, 40\}$ count $c_N$ by dynamic programming, and confirm that the consecutive
ratio $c_{41}/c_{40}$ agrees with the largest root of (1).

**Part B — the jump.** For the five cases of the table in the text compute $v$, $T_s$ and
$F/mg$, and minimize the effort of (6) numerically over $T \in [0.05, 1]$ s to compare with
$T^\star = v/g$. Obtain $\delta h$ for $\delta T = 5, 10, 20$ ms both from (7) and by integrating
the stance directly, and compare.

**Part C — the success curve.** From the trial log report (a) the number of successes per level
with Clopper–Pearson intervals, (b) the maximum-likelihood fit of (4) and $\hat{g}_{90}$, (c) the
95% interval of $g_{90}$ over 2000 bootstrap resamples of the trials, (d) the counts per failure
mode.

**Part D — comparing designs.** Simulate each of the four designs of the table in the text 3000
times and find the RMSE and bias of $\hat{g}_{90}$ and the fraction of degenerate fits
($\hat{s} < 10^{-3}$ or $> 1$). The staircase starts at $0.45$ m with a step of $0.03$ m, goes
up after 3 consecutive successes (resetting the streak) and down after a failure.

**Part E — re-analysis of published results.** From the two must-read papers (the recommended
ones may be added) (a) build the table of problem P7(b) (maneuver, attempts, successes,
interval, source location), (b) if some maneuver is reported at varying difficulty, fit (4) and
estimate the operating limit; if none is, write **that fact and what it means**, (c) present in
one page, on the basis of the results of Part D, a design for the test — which trials, how many
— that would actually estimate the operating limit of that system.

**Acceptance criteria — all five conditions must hold to pass.**

1. **Part A** — $c_{20}$ is $1048576, 8362, 812, 68$ for $m = 1, 2, 3, 5$ (exactly) and the
   growth rates are $2.0000, 1.6180, 1.4656, 1.3247$ (tolerance $10^{-4}$). Print the count
   $68^4 = 2.14\times10^7$ for four legs, $N = 20$, $m = 5$ next to $2^{80} = 1.21\times10^{24}$.
2. **Part B** — the values of the table agree with the text ($T_s$ to $10^{-3}$ s, $F/mg$ to
   $0.01$). The $T^\star$ of the numerical minimization equals $v/g$ to within $10^{-3}$ s, with
   $F = 2mg$ there. The $\delta h$ of (7) is $3.1, 6.3, 12.5$ cm, and the directly integrated
   value is larger by the second-order term $a^2\delta T^2/(2g)$, namely $3.2, 6.5, 13.3$ cm
   (tolerance $0.1$ cm) — print the difference alongside.
3. **Part C** — (a) the successes are $10, 10, 6, 3, 1, 0$ (when the conventions are followed).
   The lower limit of the interval at $0.48$ m is $0.692$. (b) $\hat{g}_{50} = 0.600 \pm 0.002$,
   $\hat{s} = 0.043 \pm 0.002$, $\hat{g}_{90} = 0.506 \pm 0.003$ m. (c) The bootstrap interval is
   $[0.463, 0.566] \pm 0.01$ m and **contains** the truth $0.490$. (d) The modes of the 30
   failures are $17, 8, 5$.
4. **Part D** — the RMSE is $0.036$ for uniform, $0.034$ for near the limit, $0.044$ for two
   levels and $0.026$ m for the staircase ($\pm0.003$), **the staircase being the smallest**. The
   degenerate fraction of the near-the-limit design is $0.03$–$0.07$.
5. **Part E** — every row of the table has a source location (section, figure or table number).
   Maneuvers whose number of attempts is not reported are marked "count not reported" and **no
   interval has been made up**. The design states the definition of success, the difficulty
   variable, the number of trials, the placement rule and its grounds (which number of Part D).

**Comparison**: (a) the baseline of Part A is the root of (1), and of Part B the analytic values
of (2), (6) and (7). (b) The baseline of Part C is the true parameters of the generator
($g_{50} = 0.60$, $s = 0.05$, $g_{90} = 0.490$). (c) The baseline of Part D is the uniform
design.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| $c_N$ is larger than the table | No length constraint was imposed on the runs at the two ends | The count of this lesson requires **every** run to be at least $m$. Check that $c_{10}$ ($m = 5$) is 4 |
| The growth rate differs from the root of (1) | $N$ is small | Use the ratio at large $N$, such as $c_{41}/c_{40}$ |
| The effort-optimal $T^\star$ sticks to the end of the interval | The effort was taken as $\int F\,dt$ (the impulse) | Check that it is the squared integral. The impulse is monotone increasing in $T$ |
| The successes differ from the reference | Other random numbers were drawn from the generator first | Check that `trial_log` is the **first** call on a new generator |
| The logistic fit diverges | The data are separated (it happens in bootstrap samples) | If $\hat{s}$ is below $10^{-3}$, count that sample as degenerate and drop it. Report how many were dropped |
| The bootstrap interval is too narrow | Only the success counts were redrawn, level by level | Resample the 60 trials as a whole, with replacement |
| The RMSE of the staircase exceeds that of uniform | The success streak was not reset after stepping up | 3 successes → step up → streak 0 |

## Open problems

- **(Open problem) Global optimality of the contact schedule** — all three remedies of R1 give
  up global optimality (fixed, fixed order, local solution). Certifying the global solution of
  trajectory optimization with contact works only at small scale (the open problem of
  `c4-contact-implicit-hybrid`). Current approaches: mixed-integer convex programming,
  formulation as graphs of convex sets (`c6-combinatorial-gcs`), learning to propose good
  schedules and refining them by optimization. What is missing: schedule search **close to real
  time** at the scale of multi-contact, whole-body maneuvers, with a guarantee on the quality of
  the solution.
- **(Open problem) A standard benchmark for maneuvers** — as problem P7 reveals, the results of
  dynamic maneuvers are reported as videos and single cases. The difficulty axis, the definition
  of success and the number of trials are not standardized, so systems cannot be compared.
  Current approaches: the obstacle courses of competitions, the difficulty sweeps of some papers.
  What is missing: a reporting convention for difficulty **normalized by body size** and for the
  operating limit (such as $g_{90}$ divided by leg length) across robots with different
  hardware.
- **(Open problem) Designing tests in which failure is expensive** — R5 shows that trials near
  the limit are the most informative and the most dangerous. Optimal sequential designs that
  include the cost of failure exist in reliability engineering, but the design for cases such as
  robot maneuvers, in which a failure brings hardware damage and repair time and **changes the
  system**, has not been established. Current approaches: building a prior from simulation and
  using hardware for confirmation, tests with a protective device (a safety tether). What is
  missing: a correction for the effect of the tether on the result — a success with a tether is
  not the same as a success without one.
- **(Open problem) Combining model-based control and learning** — a model-based planner can
  **compose** a maneuver never seen before (the physics of R2), and a learned policy is robust to
  the uncertainty of contact timing (R3). How to divide the work between the two is open.
  Current approaches: a learned policy tracking a reference trajectory given by a planner, an
  optimizer refining a contact schedule produced by a learned policy. What is missing: a
  principle that fixes the boundary of that division of labour — it touches "behaviour a teacher
  cannot teach" of `s3-locomotion-rl`.

## Concept check

Take it with `rc quiz s3-dynamic-maneuvers`. This quiz is a **concept check only**; the real work
is the problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

## How to study this stage

1. **Write the two questions down separately (10 min)** — "how to plan" (R1–R3) and "how to show
   that it was done" (R4, R5). This lesson gives the two equal weight — seeing how empty the
   latter is in papers on dynamic maneuvers is half the purpose.
2. **Derive (5), then Part A (40 min)** — one recurrence and a characteristic equation. Build the
   table and put the four-leg count next to $2^{80}$. Write one line each on what the three
   remedies give up.
3. **The jump by hand (50 min)** — (2) and (6). The derivative that yields $T^\star = v/g$ is two
   lines. Put in the stroke and the peak force of a robot you know and compute the height it can
   jump.
4. **(7) and the sensitivity (30 min)** — compute the figure "$10$ ms is $12.5\%$" yourself and
   compare with the control period and the delay of contact detection.
5. **Analyse the log with Part C (60 min)** — look at the per-level intervals first (wide), fit
   the curve, and look at the bootstrap interval. Putting "it crossed $0.72$ m" next to "the
   operating limit is $0.51$ m" is the central experience of this lesson.
6. **Compare the designs with Part D (50 min)** — run the four designs and explain through the
   Fisher information why the staircase wins and why two levels lose. Redesign the next hardware
   test of your own research as a staircase.
7. **The two papers (150 min)** — system papers are long. Track only three things: the
   mechanical and actuator figures (to put into R2), how the contact schedule is determined (R1)
   and the number of trials of the experiments (R4). The one-page note per paper is
   **mandatory**.
8. **Part E: the table of published results (60 min)** — record "count not reported" honestly.
   The emptiness of that table is the emptiness of evaluation in this field. End by writing a
   one-page test design.
9. **Close the module (30 min)** — place the six lessons of S3 in a 2×2 table of "model-based ↔
   learned" and "nominal operation ↔ maneuvers", and write one line each on the guarantee (what
   is proved) and the evaluation (what earns trust) of every cell. The empty cells are research
   topics.

**Pass criterion**: from a blank page you can write the relation between (5) and (1), (2), (6)
and (7), and how $g_{90}$ is obtained from the fit of (8); you can answer with intervals what
"10/10 successes" and "the largest difficulty at which it once succeeded" each say; you can write
the five items of the advance plan of a maneuver evaluation; you have code that satisfies all
five conditions of the reproduction task and **a re-analysis table with sources**; and you have
notes on the two papers.
