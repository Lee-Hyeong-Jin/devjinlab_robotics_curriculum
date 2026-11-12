---
id: c7-event-tactile-sensing
lang: en
title: Event cameras and tactile sensing
summary: >-
  Set up the event generation model as a threshold crossing of log intensity, derive that the event
  rate is $|\nabla L\cdot v|/C$, and confirm numerically that **quantisation makes it overpredict
  for short windows**. Formulates contrast maximisation as maximising the variance of the image of
  warped events, estimates angular velocity on public event data (measured error 1.2-3.2%), and
  shows by a failure case that the objective is non-convex. On the tactile side it solves
  GelSight's photometric stereo as a linear system and measures where contact geometry and force
  estimation break down.
objectives:
  - Write the event generation model as a threshold crossing of log intensity and derive the rate $|\nabla L\cdot v|/C$.
  - Show numerically that the rate model overpredicts for short integration windows because of quantisation, and state its valid regime.
  - Formulate contrast maximisation as a warp plus variance maximisation and estimate angular velocity on public data to within 10%.
  - Explain the non-convexity of the contrast maximisation objective and the degeneracy (event collapse) of richer warp families.
  - Solve GelSight's photometric stereo as a linear system, recover normals and depth, and identify the failure conditions of force estimation.
tags: [perception, event-camera, contrast-maximization, tactile-sensing, photometric-stereo, research]
---

# Event cameras and tactile sensing

## Setup and notation

The recommended prerequisites are `c7-two-view-geometry` in this module (the camera model and
rotation), `c7-robust-fitting-ransac` (non-convex objectives and global optimality) and
`c1-so3-se3-exponential` (exponential coordinates of rotation). None of them is locked. The lesson
assumes:

- Analysis: total derivatives and directional derivatives, the Poisson equation, Taylor expansion.
- Linear algebra: $3\times3$ linear systems, least squares, solving Poisson with a DCT (code
  provided).
- Probability: Gaussian noise, correlation coefficients.
- Optimisation: non-convex objectives, multi-start, derivative-free methods such as Nelder–Mead.

Notation (continuing the C7 conventions):

| Symbol | Meaning |
|---|---|
| $L(\mathbf{x}, t) = \log I$ | log intensity |
| $C > 0$ | the contrast threshold, typically 0.05-0.5 |
| $e_k = (\mathbf{x}_k, t_k, p_k)$ | an event: pixel, time, polarity $p_k \in \{+1,-1\}$ |
| $\mathbf{v}(\mathbf{x})$ | optical flow, in pixels per second |
| $\mathbf{W}(\mathbf{x}_k, t_k; \boldsymbol{\theta})$ | the warp that moves an event to the reference time |
| $\mathcal{I}(\mathbf{x};\boldsymbol{\theta})$ | the image of warped events (IWE) |
| $\boldsymbol{\omega} \in \mathbb{R}^3$ | angular velocity in rad/s |
| $z(\mathbf{x}) \ge 0$ | indentation depth of the gel surface |
| $\mathbf{n}(\mathbf{x})$, $(p,q) = (-z_x, -z_y)$ | surface normal and gradient |
| $\mathbf{l}_c$, $\rho$ | illumination directions ($c = 1,2,3$) and albedo |

**A note on units**: $C$ is a difference of **log** intensity and so is dimensionless, and the rate
is a count per pixel per second. Angular velocity is reported in rad/s, and because a dataset's IMU
frame and the warp's sign convention may differ, the **magnitude and the axis direction are
reported separately** (the measurements in R3 are an example of why).

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the event generation model) [D2]** — a pixel $\mathbf{x}$ fires when the log intensity has
  changed by the threshold since its last event:
  $$L(\mathbf{x}, t) - L(\mathbf{x}, t - \Delta t) = p\,C. \tag{1}$$
  With brightness constancy $\dot{L} + \nabla L\cdot\mathbf{v} = 0$, over a short window
  $$\Delta L \approx -\nabla L\cdot \mathbf{v}\,\Delta t
    \;\Longrightarrow\;
    N(\mathbf{x}) \approx \frac{\lvert\nabla L\cdot\mathbf{v}\rvert\,\Delta t}{C} \tag{2}$$
  so **events fire in proportion to the spatial gradient along the motion**. Where the gradient is
  perpendicular to the motion ($\nabla L \perp \mathbf{v}$) nothing fires.
- **R2 (the valid regime of the rate model) [D2]** — (2) holds only when the per-pixel count is
  **well above one**. The threshold model is a quantiser, so over a short window most pixels have
  $\lvert\Delta L\rvert < C$ and fire nothing at all, and (2) **overpredicts** the total count.
- **R3 (contrast maximisation) [D2]** — warping the events to a reference time with parameters
  $\boldsymbol{\theta}$ and accumulating them gives
  $$\mathcal{I}(\mathbf{x};\boldsymbol{\theta})
    = \sum_k w_k\,\delta\big(\mathbf{x} - \mathbf{W}(\mathbf{x}_k,t_k;\boldsymbol{\theta})\big) \tag{3}$$
  and maximising its **variance** recovers the true motion. For pure rotation
  $\mathbf{W} = \pi\big(R(-\boldsymbol{\omega}\,t_k)\,\pi^{-1}(\mathbf{x}_k)\big)$ and
  $\boldsymbol{\theta} = \boldsymbol{\omega}$ has three degrees of freedom.
- **R4 (two failure modes of contrast maximisation) [D2]** — (1) it is **non-convex**: a single
  start lands in a local maximum (measured: starting from $\boldsymbol{\omega} = 0$ gives a
  magnitude error of 44.9%, while ten multi-starts give 1.2%). (2) With a richer warp family, a
  **degenerate (event collapse)** solution that piles all events onto one point is known to give a
  larger variance (Shiba et al. 2022 **[D0]**) — because variance measures *clustering*, not
  "motion compensation".
- **R5 (tactile: photometric stereo and force) [D2]** — on a Lambertian gel surface under three
  coloured lights the channel intensities are $I_c = \rho\,\mathbf{n}\cdot\mathbf{l}_c$, so the
  normal is recovered by a **linear system**:
  $$\mathbf{n} \propto \rho^{-1}A^{-1}\mathbf{I},\qquad A = [\mathbf{l}_1\ \mathbf{l}_2\ \mathbf{l}_3]^\top. \tag{4}$$
  Integrating the gradient $(p,q)$ with Poisson gives the depth, and the contact area and the
  (calibrated) normal force follow from it. The depth is **undetermined up to a constant** (a
  gauge), and the normal force is not identifiable without a per-sensor calibration constant.

## Derivation

### R1 — the event generation model

Each pixel of an event camera monitors the **log intensity** $L = \log I$ asynchronously and fires
whenever the difference from the value at its last event, $L_{\text{ref}}$, exceeds $\pm C$ — that
is (1). The reason for the logarithm is to make the sensor respond to **relative contrast**: since
$\Delta L = \Delta I / I$, a small absolute change in a dark region and a large one in a bright
region are treated alike.

If the scene brightness merely moves over a short window (brightness constancy),

$$\frac{dL}{dt} = \frac{\partial L}{\partial t} + \nabla L\cdot\mathbf{v} = 0
  \;\Longrightarrow\;
  \frac{\partial L}{\partial t} = -\nabla L\cdot\mathbf{v}$$

so the change over a window $\Delta t$ is
$\Delta L \approx -\nabla L\cdot\mathbf{v}\,\Delta t$. One event consumes $C$ of that change, which
gives (2). Three things follow immediately:

1. **No texture, no events** ($\nabla L = 0$).
2. **A gradient perpendicular to the motion produces nothing** ($\nabla L\cdot\mathbf{v} = 0$) —
   the **aperture problem** survives intact on an event camera.
3. The polarity is $\operatorname{sign}(-\nabla L\cdot\mathbf{v})$, so as an edge passes, the same
   pixel sees a $+$ and then a $-$ — **a polarity-summed IWE therefore cancels when the alignment
   is correct**. This is why contrast maximisation usually uses the **count image** (ignoring
   polarity).

The flow of pure rotation is independent of depth (which is why rotation estimation is the easy
case):

$$\mathbf{v}(\mathbf{x}) = f\begin{bmatrix}
  \omega_1 XY - \omega_2(1+X^2) + \omega_3 Y \\
  \omega_1(1+Y^2) - \omega_2 XY - \omega_3 X \end{bmatrix},
  \qquad (X, Y) = \left(\tfrac{x-c_x}{f}, \tfrac{y-c_y}{f}\right). \tag{5}$$

### R2 — where (2) holds and where it does not

(2) uses the linearisation together with a **continuum approximation** (treating the event count as
a real number). The threshold model is a quantiser, so a pixel with $\lvert\Delta L\rvert < C$ emits
**zero** events while (2) predicts a fractional count. Over a short window, therefore, (2)
overpredicts the total. Measured (synthetic: $180\times240$, band-limited texture, $C = 0.05$,
$\boldsymbol{\omega} = (0.2, -0.15, 0.6)$ rad/s):

| window $\Delta t$ | 1.0 ms | 2.0 ms | 5.0 ms | 20.0 ms |
|---|---|---|---|---|
| actual events | 6 | 990 | 12,802 | 92,850 |
| measured/predicted | 0.000 | 0.058 | 0.405 | 0.813 |
| spatial correlation (after smoothing) | 0.010 | 0.664 | 0.957 | 0.985 |

How to read it. (1) The ratio climbs towards one as the window grows, because the quantisation error
shrinks relative to a larger per-pixel count. (2) The **spatial distribution** matches much sooner
(correlation 0.957 at 5 ms): (2) predicts *where* events fire well and *how many* only later.
(3) So the right way to use (2) is as a **normalised prediction** (a relative distribution); backing
$C$ out of absolute counts needs a window that accumulates tens of events per pixel.

**Where the assumptions break**: cases where brightness constancy fails — illumination change,
shadows, occlusion — have
$\partial L/\partial t \ne -\nabla L\cdot\mathbf{v}$. And a real sensor's $C$ varies per pixel
(manufacturing spread), drifts with brightness and temperature, and has a refractory period that
saturates the count at high-contrast edges. Estimating $C$ from (2) requires all of that to be
constant.

### R3 — contrast maximisation

A single event carries almost no information. Motion is estimated by **collecting the events of a
short window into one image**, and if the motion is compensated correctly the events from one edge
land on the same line, making the image **sharp**. Measuring sharpness by variance is contrast
maximisation (Gallego et al. 2018):

$$\boldsymbol{\theta}^\star = \arg\max_{\boldsymbol{\theta}}\;
  \operatorname{Var}\big[\mathcal{I}(\cdot\,;\boldsymbol{\theta})\big],
  \qquad \operatorname{Var}[\mathcal{I}] = \frac{1}{|\Omega|}\sum_{\mathbf{x}}
  \big(\mathcal{I}(\mathbf{x}) - \bar{\mathcal{I}}\big)^2. \tag{6}$$

The warp of a pure rotation can be applied without knowing depth: lift event $k$'s pixel to a
bearing, rotate it by $-\boldsymbol{\omega}t_k$ and project it back,

$$\mathbf{W}(\mathbf{x}_k, t_k; \boldsymbol{\omega})
  = \pi\Big(\exp\big(-\widehat{\boldsymbol{\omega}}\,t_k\big)\,\pi^{-1}(\mathbf{x}_k)\Big). \tag{7}$$

The $\pi^{-1}$ has to undo the lens distortion (the dataset's radtan coefficients). Accumulation
uses **bilinear splatting** into the four neighbours — that is what makes (6) continuous and
differentiable in $\boldsymbol{\omega}$.

**Measured on public data**: on ECD `shapes_rotation` (DAVIS 240C, $240\times180$), three 30 ms
windows were chosen, (6) was maximised with multi-start Nelder–Mead (10 starts), and the result was
compared against the mean IMU angular velocity over the same window.

| window start $t_0$ | events | $\lvert\boldsymbol{\omega}\rvert$ GT (rad/s) | estimate | magnitude rel. error | angle between axes | variance ratio (estimate/static) |
|---|---|---|---|---|---|---|
| 58.25 s | 17,198 | 12.1176 | 12.2603 | **1.18%** | 2.18° | 5.60 |
| 51.75 s | 20,270 | 9.4163 | 9.7173 | **3.20%** | 2.70° | 5.50 |
| 48.00 s | 22,795 | 9.8247 | 10.1175 | **2.98%** | 3.20° | 6.81 |

All three are inside 10%. **One thing to watch**: the estimated vector comes out with the
**opposite sign** from the one the IMU reports, because the dataset's IMU frame and the sign
convention of (7) differ. That is why the table reports the magnitude and the **angle between the
axes** (on $|\cos|$) separately. Comparing the vectors directly without reconciling the sign leads
to the conclusion "completely wrong", which is the single most common trap in this task.

### R4 — the failure modes of contrast maximisation

**(1) Non-convexity.** (6) is a non-convex function of $\boldsymbol{\omega}$ with many local
maxima. Measured (the same $t_0 = 58.25$ s window): a **single** Nelder–Mead started at
$\boldsymbol{\omega} = 0$ stalled at a local maximum of variance 0.901 with a magnitude error of
**44.9%**, while ten multi-starts on the same data reached variance 3.195 with an error of
**1.18%**. **The variance value is itself a diagnostic** — if it does not rise to at least five
times the static warp's variance (0.571), suspect a local maximum. The practical remedies are
multi-start, a coarse-to-fine pyramid, and initialising from the IMU.

**(2) Degeneracy (event collapse).** (6) does not measure "motion compensation" but **clustering**.
With a sufficiently rich warp family (per-pixel flow, added divergence or shear), the solution that
piles every event onto one point gives the largest variance — physically meaningless, yet optimal
for the objective. Shiba et al. 2022 catalogue the phenomenon and propose mitigations (backward
warping, regularisation terms) **[D0]**.

**An honest report**: in this lesson's experiment, adding one divergence parameter to the 3-DOF
rotation and solving in 4 DOF **did not produce a collapse** — the optimum's divergence was
$-0.002$, effectively zero (69.6% of events remained inside the frame), and in fact the extra
parameter helped the optimiser escape a local maximum and find a better solution with a magnitude
error of 0.27% (variance 2.319, 2.57 times the 3-DOF single-start value). In other words, **for this
configuration (3 DOF plus one divergence, 30 ms, a pure-rotation scene) non-convexity dominates and
collapse does not appear.** Collapse is reported for wider warp families, and where the boundary
lies is open problem 2.

### R5 — tactile: from photometric stereo to contact geometry and force

A GelSight-style sensor is an elastic gel with an opaque coating, three coloured LEDs from different
directions, and a camera. If the gel surface is Lambertian with uniform albedo $\rho$, the intensity
of channel $c$ is

$$I_c(\mathbf{x}) = \rho\,\mathbf{n}(\mathbf{x})\cdot\mathbf{l}_c, \qquad c = 1,2,3 \tag{8}$$

and collecting the three gives $\mathbf{I} = \rho A\mathbf{n}$ (the rows of $A$ being
$\mathbf{l}_c^\top$), so when $A$ is invertible (4) **recovers the normal with one linear solve**.
The coating, which makes the measurement independent of illumination and viewpoint, is the key
design element of this sensor — the colour and material of the object do not enter the measurement.

Going from normals to depth means integrating the gradient field. Now
$(p, q) = (-n_1/n_3, -n_2/n_3)$ should satisfy $z_x = p$ and $z_y = q$, but noise breaks the
integrability condition ($p_y = q_x$), so one solves it in the least-squares sense — and those
normal equations are the Poisson equation:

$$\nabla^2 z = \frac{\partial p}{\partial x} + \frac{\partial q}{\partial y}. \tag{9}$$

Solved with a DCT under Neumann boundary conditions this is $O(n\log n)$. **The solution is
undetermined up to a constant** — another gauge, with the same structure as R4 of
`c7-bundle-adjustment`. In practice one sets the median of the non-contact region to zero.

Contact geometry and force are read off the depth. The contact region is $\{z > \tau\}$, the
indentation volume is $V = \int z\,d\mathbf{x}$, and in a thin elastic-layer model the normal force
is $F_n \approx \kappa V$ with $\kappa$ a per-sensor calibration constant.

Measured (synthetic GelSight: $160\times160$, a sphere of radius 40 px pressed to depth $d$, three
illumination directions, albedo 0.9, with channel noise given as a standard deviation in intensity
units):

| indentation $d$ | noise | mean normal error | depth RMSE | contact area rel. error | volume ratio (recovered/true) |
|---|---|---|---|---|---|
| 1.0 | 0 | $0.0000^\circ$ | 0.0010 | 0.000 | 1.0034 |
| 1.0 | 0.01 | $1.0863^\circ$ | 0.1215 | 14.54 | **8.82** |
| 1.0 | 0.05 | $5.4336^\circ$ | 0.5839 | 45.40 | **41.99** |
| 3.0 | 0.01 | $1.0880^\circ$ | 0.1688 | 2.92 | 2.89 |
| 6.0 | 0.01 | $1.0864^\circ$ | 0.1613 | 0.025 | 1.383 |
| 6.0 | 0.05 | $5.4029^\circ$ | 0.6180 | 3.80 | 2.52 |

Without noise the normals are recovered **exactly** (it is a linear system), the depth RMSE is at
the $10^{-3}$ level and the volume ratio is 1.003. At 1% noise the normal error is a modest
$1.1^\circ$ and yet **the volume ratio explodes to 8.8 for a shallow contact** — the noise outside
the contact integrates into a spurious volume that swamps the small true one. Deeper indentation
(6.0) brings the ratio back to 1.38 at the same noise. **Conclusion: volume-based force estimation
is unreliable for light contact, and establishing a contact mask first is mandatory.**

The linearity of the volume itself is clean. Without noise, regressing the recovered volume on the
true one over $d \in [0.5, 8]$ gives slope 1.0005 and $R^2 = 1.000000$, and the true volume grows
as $d^{1.979}$, matching the exponent 2 of the spherical-cap formula
$V = \pi d^2(3R-d)/3 \approx \pi R d^2$.

**Where the assumptions break**: (1) the $\max(0,\cdot)$ of (8) and **saturation**. If the sensor's
dynamic range is too small and a channel clips, the linear system (4) is fed wrong values.
Measured: capping at 0.6 clips 98.2% of pixels, so the **mean** normal error looks small at
$0.81^\circ$ while **the p99 is $17.7^\circ$** (at $0.45$, p99 is $24.2^\circ$) — the error
concentrates at the steep contact boundary, so looking only at the mean misses it. (2) The
assumption that $\rho$ is uniform: it fails as the gel wears or picks up debris. (3) The gel's
nonlinear elasticity and hysteresis: $F_n \approx \kappa V$ is a small-indentation linear
approximation, $\kappa$ must be calibrated per sensor, and **it is not identifiable from the image
alone**. (4) Shear forces and torques are not explained by volume alone — the marker displacement
field (GelSight's black dots) has to be used as well.

## Proof sketch

### R1 and R2 — the rate model and its valid regime

**Hypotheses** H1: brightness constancy $\dot{L} = -\nabla L\cdot\mathbf{v}$ holds over the window
$\Delta t$. H2: the threshold $C$ is constant in space and time. H3: the refractory period is
shorter than the window (no count saturation).
**Conclusions** C1: the expected per-pixel count is $\lvert\Delta L\rvert/C$, of which (2) is the
first-order approximation. C2: the actual count is
$\lfloor \lvert\Delta L\rvert/C \rfloor$, so (2) **always overpredicts**, with a relative error of
order the reciprocal of the per-pixel count.

**Strategy**: treat threshold crossings as a counting process and account for the bias of the floor
function.

1. **C1**: where the log intensity changes monotonically, an event fires each time $L$ crosses
   $L_{\text{ref}} \pm C$, so the count is $\lfloor\lvert\Delta L\rvert/C\rfloor$. Substituting
   $\Delta L \approx -\nabla L\cdot\mathbf{v}\,\Delta t$ from H1 gives (2). $\square$
2. **C2**: $\lfloor u\rfloor \le u$ and $u - \lfloor u\rfloor \in [0,1)$, so at a single pixel the
   prediction $u$ and the reality differ by less than one. The relative error
   $(u - \lfloor u\rfloor)/u < 1/u$ is near one for $u \ll 1$ (everything is overpredicted, since
   $\lfloor u\rfloor = 0$) and vanishes as $1/u$ for $u \gg 1$. The overall ratio is an average over
   pixels and so climbs towards one with $\Delta t$. The measured sequence
   $0.000 \to 0.058 \to 0.405 \to 0.813$ is this. $\square$
3. **Why the spatial distribution matches sooner**: the floor function is **monotone**, so it
   preserves the ordering of $u$. The correlation coefficient therefore approaches one much faster
   than the ratio does (measured: ratio 0.405 but correlation 0.957 at 5 ms).
4. **Remove a hypothesis**: if H1 fails (illumination change, occlusion) the right-hand side of (2)
   is itself wrong. If H2 fails (a real sensor's $C$ scatters by 10-20% across pixels), the
   prediction is spatially biased and that bias **does not vanish** with a longer window — unlike
   the quantisation bias, it is a *consistent* error. If H3 fails, the count saturates at
   high-contrast edges and (2) flips to **under**prediction.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R1)** Derive (2) from brightness constancy, and derive the pure-rotation flow
(5). Then use "an edge with $\nabla L \perp \mathbf{v}$ produces no events" to explain in one
paragraph that the aperture problem survives on an event camera.
*Solution sketch*: (5) is the time derivative of the projection when $\mathbf{X}_c$ moves as
$\dot{\mathbf{X}} = \boldsymbol{\omega}\times\mathbf{X}$. Confirm that the depth cancels — which is
why rotational flow is depth-independent.

**P2 (proof, ★★★, R2)** Prove C2, and express the overall measured/predicted ratio in terms of the
distribution of the per-pixel expected count $u$. Then show that if $C$ scatters per pixel as
$\mathcal{N}(C_0, s^2)$, the bias of (2) has a component independent of the window length.
*Strategy and key inequality*: compute $\mathbb{E}[\lfloor u\rfloor]/\mathbb{E}[u]$. With
$\lfloor u \rfloor = u - \{u\}$ and $\{u\}$ roughly uniform in expectation, the ratio is
$1 - \mathbb{E}[\{u\}]/\mathbb{E}[u]$. When $C$ scatters, Jensen enters through
$\mathbb{E}[u] \propto \mathbb{E}[1/C]$ and leaves a window-independent bias.

**P3 (numerical, ★, R1·R5)** (a) With $C = 0.2$, $\lvert\nabla L\rvert = 0.5$ per pixel and a flow
of 200 px/s along the gradient, how many events per pixel per second? (b) For illumination
directions $(0,-0.6,0.8)$, $(0.52,0.3,0.8)$, $(-0.52,0.3,0.8)$ (before normalisation), compute the
condition number of $A$ and state the noise amplification of the normal recovery.
*Answer*: (a) $0.5\times200/0.2 = 500$ ev/px/s. (b) after normalisation the singular values of $A$
are $(1.385456,\ 0.735244,\ 0.734798)$ with $\kappa_2(A) = 1.885492$ and
$\lVert A^{-1}\rVert_2 = 1.360918$ — intensity noise is amplified into the normal by at most a
factor 1.36 (tolerance $10^{-5}$). Check: confirm that
$\lVert A^{-1}\rVert_2 = 1/\sigma_{\min}$.

**P4 (numerical, ★★, R3)** For one 30 ms window of ECD `shapes_rotation`, report (a) the event count
and the rate per second, (b) the IWE variance of the static warp ($\boldsymbol{\omega} = 0$),
(c) the variance of the optimal warp and their ratio, and (d) the magnitude relative error and the
angle between the axes against the IMU.
*Answer (reference measurements, $t_0 = 58.25$ s)*: (a) 17,198 events, 573 kev/s; (b) 0.5709;
(c) 3.1951, ratio 5.60; (d) magnitude error 1.18%, angle 2.18°. Tolerance: the event count must be
exact; the variance depends on the splatting scheme, so a **ratio of at least 5** passes, and the
magnitude error must be within 10%. Check: confirm that the estimated vector comes out with the
opposite sign from the IMU's (that is normal).

**P5 (implementation, ★★★, R3·R5)** (a) Implement the warp (7) and the variance (6) and estimate
angular velocity on the public data; (b) implement (4) and (9) and recover normals and depth from a
synthetic tactile image.
*Rubric*: (a) distortion correction is applied, bilinear splatting is used, multi-start finds the
global maximum, and the magnitude and axis are compared separately against the IMU; (b) at zero
noise the normal error is $< 10^{-6}$ degrees and the constant ambiguity of the Poisson solution is
handled explicitly; (c) one failure mode is reproduced and reported numerically in each case.

**P6 (counterexample, ★★, R4)** (a) Find a window where single-start contrast maximisation lands in
a local maximum, report the variance and the magnitude error, and show that multi-start fixes it.
(b) Add a divergence (radial) parameter to the warp, check whether the variance grows, and report
whether a collapse occurs **exactly as you observe it**.
*Property checklist*: (a) find a local maximum whose ratio to the static variance is below 2;
(b) report the fraction of events remaining inside the frame (the indicator of collapse); (c) if no
collapse appears, write that it did not — this lesson's measurements did not either; (d) a paragraph
on variance being a measure of clustering rather than of motion compensation.

**P7 (numerical, ★★, R5)** On the synthetic tactile image, set the channel noise standard deviation
to $0, 0.01, 0.05$ and measure the normal error, the depth RMSE and the volume ratio for
indentations $1.0$ and $6.0$. Explain why the volume ratio explodes for a shallow contact and
implement one mitigation, showing its effect numerically.
*Answer (reference measurements)*: at zero noise the normal error is $0.0000^\circ$ and the volume
ratio 1.003; at 0.01 the error is $1.09^\circ$ with a volume ratio of 8.82 ($d=1.0$) against 1.383
($d=6.0$); at 0.05 the error is $5.40^\circ$ with a ratio of 41.99 ($d=1.0$). Tolerance: the normal
error within $\pm20\%$, the volume ratio to the right order of magnitude. One mitigation: build a
contact mask by thresholding plus connected components and integrate only inside it — the ratio
must approach one.

**P8 (paper, ★★, R3·R5)** Read the contrast maximisation section of the Gallego et al. 2020 survey
and Yuan et al. 2017 and (a) rewrite the event representations the survey classifies (count image,
time surface, voxel grid) as choices of $w_k$ in (3); (b) find in the GelSight paper what has to be
**redone per sensor** in the force calibration procedure; and (c) argue, with evidence from each
paper's evaluation section, that both sensors share the problem of having no standard benchmark.
*Rubric*: for (a), translating into $w_k = 1$ (count), $w_k = p_k$ (polarity) and $w_k = t_k$ (time
surface) passes. For (b), noting that it is not a single constant $\kappa$ but includes the
illumination, gel thickness and markers is excellent.

## Paper reading

**Two must-reads.** Write a one-page note on each, using the ten fixed questions
(`lesson-standard.md` §5). Read in three passes, and attack questions 4, 5, 6 and 7 in the third.
For the full bibliography, including the recommended papers, run
`rc papers c7-event-tactile-sensing`.

1. **Gallego, Delbrück, Orchard, Bartolozzi et al., "Event-based vision: a survey" (2020, IEEE
   T-PAMI)** — role: `survey`. <https://arxiv.org/abs/1904.08405> (§2–4 and the contrast
   maximisation section.)
   Extra questions: (a) among the advantages the survey lists for event cameras (latency, dynamic
   range, power), separate those **backed by measurements** from the structural claims. (b) How does
   the choice of event representation (count, time surface, voxel) reduce to $w_k$ in (3)?
   (c) Of the items the survey calls open problems, are any already settled as of 2026?
2. **Yuan, Dong & Adelson, "GelSight: high-resolution robot tactile sensors for estimating geometry
   and force" (2017, Sensors)** — role: `seminal`. <https://doi.org/10.3390/s17122762>
   Extra questions: (a) is the paper's normal recovery a linear system like (4), or a lookup table?
   What are the trade-offs of that choice? (b) List every quantity in the force calibration
   procedure that has to be redone per sensor. (c) Under what conditions (indentation depth,
   material, speed) were the reported resolution and accuracy measured?

**The ten fixed questions**: (1) which problem under which assumptions; (2) what exactly earlier
work could not do; (3) the core idea in one equation; (4) what is guaranteed and **what is not**;
(5) the independent and dependent variables and the baselines, fairly tuned or not; (6) whether the
metric matches the claim, and whether variance and seeds are reported; (7) what is missing for
reproduction; (8) the first assumption to doubt if the result were wrong; (9) time and memory
complexity and real-time behaviour; (10) what you would change to go beyond it in a year.

**Recommended**: Gallego et al. 2018 (the origin of contrast maximisation, §3), Shiba et al. 2022
(the degeneracy and its mitigations), Szeliski ch.13.1 (photometric stereo).

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 10 minutes in total (excluding
the download), numpy and scipy only. The inputs are one public dataset and a generator this lesson
specifies.

**Inputs**: (a) the text version of `shapes_rotation` from ECD
(`https://rpg.ifi.uzh.ch/davis_data.html`) — `events.txt` (t x y p), `imu.txt` (the last three
columns are angular velocity in rad/s) and `calib.txt` (fx fy cx cy k1 k2 p1 p2 k3); 157 MB
compressed. (b) Synthetic tactile — $160\times160$, a sphere of radius 40 px pressed to depth $d$,
illumination $(0,-0.6,0.8)$, $(0.52,0.3,0.8)$, $(-0.52,0.3,0.8)$ (normalised), albedo 0.9, Gaussian
smoothing with $\sigma = 1.0$. Report with a fixed seed.

All **four conditions** must hold to pass. Every reference value was measured for this lesson.

1. **Angular velocity estimation (the main point)**: on `shapes_rotation`, for **at least three**
   30 ms windows with a large $\lvert\boldsymbol{\omega}\rvert$, maximise (6) with multi-start and
   match the mean IMU angular velocity to within **10% in magnitude** and **10° in axis angle**.
   (Reference: at $t_0 = 58.25/51.75/48.00$ s, 1.18%/3.20%/2.98% and 2.18°/2.70°/3.20°.) Confirm
   that the estimated vector's **sign** is opposite to the IMU's and say so in the report.
2. **The variance-ratio diagnostic**: in each window the IWE variance of the optimal warp is at
   least **five times** that of the static warp ($\boldsymbol{\omega}=0$) (reference:
   5.60/5.50/6.81). A result with a ratio below 2 is a local maximum and does not count as a pass.
3. **The valid regime of the rate model**: on the synthetic stream, as the integration window grows
   from $1$ to $20$ ms, the measured/predicted ratio of (2) **increases monotonically** and exceeds
   $0.7$ at 20 ms, while the spatial correlation is already above $0.9$ at 5 ms (reference: ratios
   0.000/0.058/0.405/0.813 and correlations 0.010/0.664/0.957/0.985).
4. **Tactile photometric stereo**: with generator (b) at zero noise, the mean normal error is
   $< 10^{-6}$ degrees, the depth RMSE $< 10^{-2}$ and the volume ratio $1.00 \pm 0.01$ (reference:
   $0.0000^\circ$, 0.001-0.004, 1.003-1.001). At a channel noise of 0.01 the normal error is around
   $1.1^\circ$ and **the volume ratio exceeds five for a shallow contact ($d=1$)** (reference 8.82)
   — showing numerically that force must not be estimated from volume without a contact mask.

**State this in the report**: (1) the sign convention issue of condition 1; (2) how to use the
variance ratio of condition 2 as a local-maximum diagnostic; (3) the volume-ratio explosion of
condition 4 and the effect of your mitigation.

**Baselines**: (1) the IMU angular velocity (condition 1); (2) the static warp (condition 2);
(3) the analytic prediction (2) (condition 3); (4) the synthetic ground-truth normals and depth
(condition 4). Optionally switch to a different sequence such as `shapes_translation` and confirm
that the pure-rotation warp no longer fits.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| the estimated angular velocity differs from the IMU only in sign | a frame/warp sign convention difference — **this is normal** | compare the magnitude and the axis angle (on $|\cos|$) |
| the magnitude error is around 50% | a single start landed in a local maximum | look at the variance ratio (below 2 means a local maximum); use multi-start or an IMU initialisation |
| the variance barely responds to the warp | distortion was not corrected, or the window is too long | compare the IWE before and after undistortion by eye, and shorten the window to 10 ms |
| the optimal variance is abnormally large and the events piled into a few pixels | the warp family is wide enough to collapse | look at the fraction of events inside the frame and the size of the IWE support |
| the accumulation is jagged in $\boldsymbol{\omega}$ | nearest-neighbour splatting was used | switch to bilinear splatting |
| the normals are not unit vectors | the normalisation after (4) was skipped | histogram $\lVert\mathbf{n}\rVert$ |
| the depth is globally offset | the constant ambiguity of the Poisson solution was not handled | set the median of the non-contact region to zero |
| the volume ratio exceeds 10 | the integration was global, with no contact mask | integrate only inside the mask and compare again |

## Open problems

- **(open problem) justifying the contrast maximisation objective** — maximising the variance (or
  one of its variants: sum of squares, entropy) measures **clustering**, not motion compensation.
  There is no general theory of which objective is the maximum-likelihood (or even a consistent)
  estimator under which noise model. Current approaches: the family of objectives in
  [Gallego et al. 2018](https://arxiv.org/abs/1804.01306), and the degeneracy analysis and
  regularisation of [Shiba et al. 2022](https://arxiv.org/abs/2207.04007). What is missing: an
  objective **derived** from the event generation model.
- **(open problem) where the warp family starts to degenerate** — in this lesson's measurements,
  3-DOF rotation plus one divergence parameter (4 DOF in total) produced no collapse and
  non-convexity dominated instead. With much richer families, such as per-pixel flow, collapse is
  reported. There is no criterion for **where the boundary is**. Current approach: the mitigations
  of [Shiba et al. 2022](https://arxiv.org/abs/2207.04007) (backward warping, regularisation). What
  is missing: a quantitative condition linking a warp family's degrees of freedom to the possibility
  of degeneracy.
- **(open problem) the absence of a standard tactile benchmark** — the event side has public data
  such as ECD and MVSEC and metrics such as ATE and angular velocity, but tactile sensors differ in
  gel, illumination and markers, so **two groups cannot share an input**. Claims that "our method is
  better" are therefore incomparable. Current approaches: publishing per-sensor calibrations, and
  simulators. What is missing: a common task and metric that can measure transfer across sensors.
- **(open problem) estimating contact state — physics, not geometry** — photometric stereo gives the
  **geometry** (normals, depth), but what a robot needs is incipient slip, the friction coefficient
  and the contact mode (point, line, patch). Whether these are even identifiable from a single image
  (observability) has not been settled. Current approaches: the marker displacement field of
  [GelSight](https://doi.org/10.3390/s17122762), and learned slip detection. What is missing:
  identifiability conditions for contact physics from a tactile image. The question returns in
  `s2-tactile-contact-estimation`.

## Concept check

Run `rc quiz c7-event-tactile-sensing`. The quiz is for **concept checking only**; the real work is
the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: why an event camera thresholds log intensity; in which direction the rate
model errs as the window shortens; what maximising the IWE variance actually measures; what to check
first when the estimated angular velocity has the opposite sign from the IMU; and the first
condition under which volume-based force estimation breaks.

## How to study this stage

1. **The generation model by hand (40 min)** — derive (1) through (2), and the rotational flow (5).
   Confirm that the depth cancels, and draw the picture of why nothing fires when
   $\nabla L \perp \mathbf{v}$ (P1).
2. **See the quantisation yourself (60 min)** — build a synthetic stream and measure the
   measured/predicted ratio and the correlation as the window grows from 1 to 20 ms (condition 3),
   confirming that the intuition "shorter is more accurate" is wrong.
3. **Read the data correctly first (60 min)** — download the ECD text version, undo the distortion
   with `calib.txt`, and simply plot the accumulated events of a 30 ms window. See the blurred image
   first, and only then put the warp in.
4. **Implement the warp and the variance (120 min)** — write (7) and (6) and maximise with
   multi-start (conditions 1 and 2). Experience the opposite sign from the IMU **first hand** and
   build the habit of comparing the magnitude and axis separately.
5. **Meet a local maximum on purpose (40 min)** — run a single start from
   $\boldsymbol{\omega} = 0$ and watch it stall at a solution whose variance ratio is below 2 (P6).
   Learn to use the variance ratio as a diagnostic.
6. **Tactile starts with the linear system (90 min)** — recover the normals with (4) and confirm they
   are **exact** at zero noise (condition 4), then handle the constant ambiguity of the Poisson
   integration (9) explicitly. Then add noise, watch the volume ratio explode, and fix it with a
   contact mask (P7).
7. **Two papers and the notes (130 min)** — read the survey's contrast maximisation section against
   (3) and (6), and find the calibration procedure in the GelSight paper. Write the one-page note
   per paper **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the open problems and write a paragraph on
   why it is still open. Justifying the objective leads straight into theory, the tactile benchmark
   straight into experiment.

**Passing bar**: you can derive (2) and state its valid regime, you have code that estimates angular
velocity on public data to within 10%, you can diagnose a local maximum from the variance ratio, you
have solved photometric stereo as a linear system and shown numerically the failure condition of
volume-based force estimation, and you have notes on both papers.
