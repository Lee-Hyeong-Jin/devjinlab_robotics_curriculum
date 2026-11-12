---
id: s2-tactile-contact-estimation
lang: en
title: Tactile sensing and contact-state estimation
summary: >-
  Inverting contact state from a tactile sensor, at two layers. First the **solvability** of the
  inverse problem: from the Boussinesq solution for an elastic half-space, derive that surface
  displacement and traction are related in the Fourier domain by $\hat w \propto \hat p/|k|$, so the
  inversion amplifies by $|k|$ and the problem is **ill-posed of degree 1**; then measure the
  convergence rate of Tikhonov regularization. Second, show why the posterior over contact state is
  supported on a **measure-zero manifold**, so a standard particle filter degenerates immediately,
  and reproduce how a manifold particle filter fixes it and how mode ambiguity is resolved by
  accumulating observations.
objectives:
  - Derive from the Boussinesq solution that the spectrum of the tactile forward operator is $1/|k|$.
  - State that the inverse problem is therefore ill-posed of degree 1 and measure the error-versus-noise relation of Tikhonov regularization.
  - Explain why the posterior over contact state is supported on a measure-zero set and predict the degeneracy of a standard particle filter.
  - State what a manifold particle filter fixes and what it assumes in exchange.
  - Predict the rate at which mode ambiguity is resolved using the log-likelihood ratio and confirm it numerically.
tags: [manipulation, tactile, inverse-problem, particle-filter, contact-estimation, research]
---

# Tactile sensing and contact-state estimation

## Setup and notation

`s2-contact-modes-dexterity` is assumed. In particular the **mode ambiguity** of its R2 (at an edge
of the limit surface, several twists correspond to the same wrench) is the problem this lesson sets
out to solve. Also assumed:

- Bayesian estimation at the level of `c5-factor-graphs-map`: prior, likelihood, posterior,
  resampling, effective sample size (ESS). The standard account of particle filters is Barfoot ch.4.
- The Fourier transform and the convolution theorem; ill-posedness of a linear inverse problem and
  Tikhonov regularization (recommended prerequisite `r0-linear-algebra-decompositions`).
- Elasticity theory is **not** assumed — the Boussinesq solution is used as a result only.

Notation (in addition to module S2's):

| Symbol | Meaning |
|---|---|
| $p(x)$ | normal traction distribution on the contact surface; unknown |
| $w(x)$ | normal displacement of the sensor surface; the measurement (the tactile image) |
| $G$ | the forward operator $w = G p$ (convolution with a Green's function) |
| $E, \nu$ | Young's modulus and Poisson's ratio of the sensor elastomer |
| $k$ | spatial frequency vector, with $|k|$ its magnitude |
| $\lambda(k)$ | eigenvalue of $G$ (the Fourier multiplier of the periodic convolution) |
| $\alpha$ | Tikhonov regularization parameter |
| $s$ | contact state: mode (discrete) plus pose and contact point (continuous) |
| $\mathcal{M}_s$ | the **contact manifold** of mode $s$ — the set of poses consistent with it |
| $\mathrm{ESS}$ | effective sample size, $1/\sum_i w_i^2$ |

**Two inverse problems.** Tactile estimation is the composition of two problems of different
character.

1. **A continuous inverse problem**: recover the traction $p$ and the contact geometry from the
   tactile image $w$. It is linear and **ill-posed** (R1).
2. **A mixed discrete–continuous estimation problem**: estimate which mode holds (discrete) and the
   pose within it (continuous) at once. The posterior **concentrates on a measure-zero set**, which
   breaks a standard particle filter (R2).

Three assumptions, stated explicitly.

- **(A1) linear elasticity, half-space** — the sensor surface is an isotropic linear elastic
  half-space. In a real gel of finite thickness, high frequencies decay faster (§R1 failure modes).
- **(A2) rigid object and rigid sensor mount** — the contact manifold is a function of pose alone.
  For a deformable body, $\mathcal{M}_s$ itself depends on the deformation state.
- **(A3) independent observations** — the noise of successive tactile observations is independent. In
  reality the gel's hysteresis introduces correlation (§R2 failure modes).

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof).

- **R1 (solvability of the tactile inverse problem and its degree of ill-posedness) [D2]** — under
  (A1) the Boussinesq solution gives the surface displacement under a point normal force as
  $w(r) = \frac{1-\nu^2}{\pi E}\frac{P}{r}$. So $G$ is convolution with the kernel $1/r$, and from
  the two-dimensional Fourier transform $\mathcal{F}[1/r] = 2\pi/|k|$,
  $$\hat w(k) = \frac{2(1-\nu^2)}{E}\,\frac{\hat p(k)}{|k|}
    \;\Longleftrightarrow\;
    \hat p(k) = \frac{E}{2(1-\nu^2)}\,|k|\,\hat w(k).
    \tag{1}$$
  The inversion is therefore a derivative-like operation amplifying **linearly** in $|k|$, and the
  problem is **ill-posed of degree 1**. On a grid of resolution $N$ the condition number grows as
  $O(N)$.
- **R2 (measure-zero posterior and the manifold particle filter) [D2]** — contact is an **equality
  constraint** ($\phi_s(q) = 0$), and under (A2) the contact manifold
  $\mathcal{M}_s = \{q : \phi_s(q) = 0\}$ has **Lebesgue measure zero** in pose space. So the
  posterior given the observation "in contact" concentrates on a measure-zero set, and a particle
  drawn from a continuous proposal has **zero likelihood with probability 1**. A standard particle
  filter degenerates at the first update with $\mathrm{ESS} \to 0$. The manifold particle filter
  fixes this by **projecting** particles onto $\mathcal{M}_s$
  ([Koval et al. 2015](https://doi.org/10.1177/0278364915571007)).
- **R3 (rate at which mode ambiguity is resolved) [D2]** — if two modes have observation models
  $\mathcal{N}(a_1, \sigma^2)$ and $\mathcal{N}(a_2, \sigma^2)$, the log-likelihood ratio from one
  observation is
  $$\mathrm{LLR} \sim \mathcal{N}\!\left(\frac{d^2}{2\sigma^2},\ \frac{d^2}{\sigma^2}\right),
    \qquad d = |a_1 - a_2|,
    \tag{2}$$
  so **the mean is half the variance**. After $T$ observations the expected LLR grows linearly as
  $T d^2/(2\sigma^2)$, and the number of observations needed to resolve the ambiguity is
  $T \sim \sigma^2/d^2$. **If the modes are geometrically close (small $d$), the cost grows
  quadratically.**
- **R4 (what touch solves and what it does not) [D1]** — touch gives **local** geometry and
  traction, but (a) says nothing about the shape outside the contact region; (b) by the
  ill-posedness of R1, cannot recover high-frequency traction (sharp edges); and (c) has a narrow
  field of view, so the global pose is fixed only after several touches
  ([Petrovskaya & Khatib 2011](https://doi.org/10.1109/TRO.2011.2138450)). So practice uses touch as
  a **complement to vision**, and that fusion leads into `s2-learned-grasping`.

## Derivation

### R1 — from the Boussinesq kernel to the degree of ill-posedness

**The forward operator.** Under (A1), a normal point force $P$ on the surface of a half-space
produces the surface normal displacement

$$
w(r) = \frac{1-\nu^2}{\pi E}\,\frac{P}{r}
  \tag{3}
$$

(Boussinesq; Johnson ch.3). For a distributed traction $p(x)$, superposition gives

$$
w(x) = \frac{1-\nu^2}{\pi E}\int \frac{p(x')}{\lVert x - x'\rVert}\,dx'
  \;=\; (g * p)(x),
  \qquad g(x) = \frac{1-\nu^2}{\pi E}\frac{1}{\lVert x\rVert}.
  \tag{4}
$$

**In the Fourier domain.** In two dimensions
$\mathcal{F}[1/\lVert x\rVert](k) = 2\pi/|k|$ (compute directly: in polar coordinates
$\int_0^\infty \frac{1}{r}J_0(|k|r)\,r\,dr = 1/|k|$, times $2\pi$). The convolution theorem gives

$$
\hat w(k) = \hat g(k)\,\hat p(k) = \frac{1-\nu^2}{\pi E}\cdot\frac{2\pi}{|k|}\cdot\hat p(k)
  = \frac{2(1-\nu^2)}{E}\,\frac{\hat p(k)}{|k|},
$$

which is (1). **So the eigenvalues of $G$ are $\lambda(k) = 2(1-\nu^2)/(E|k|)$** and tend to zero as
$|k| \to \infty$ — $G$ is a compact (smoothing) operator and its inverse is unbounded.

**The degree of ill-posedness.** The inverse amplifies as $|k|^{+1}$, so the problem is **ill-posed
of degree 1** (comparable to undoing one integration — qualitatively different from the
exponentially ill-posed inverse heat equation). On a grid of spacing $h$ and side $L = Nh$,
$|k| \in [2\pi/L,\ \pi/h]$, so

$$
\mathrm{cond}(G) = \frac{\lambda_{\max}}{\lambda_{\min}}
  = \frac{\pi/h}{2\pi/L} = \frac{N}{2}.
  \tag{5}
$$

**The condition number is linear in the resolution** — doubling the sensor resolution doubles the
noise amplification. That is why high-resolution sensors of the GelSight kind do not simply get
better with more pixels.

**Regularization and the convergence rate.** The Tikhonov solution is
$\hat p_\alpha = \frac{\overline{\lambda}}{|\lambda|^2+\alpha}\hat w$, and choosing the optimal
$\alpha$ for a noise level $\eta$ makes the relative error decay like $\eta^{\theta}$, with $\theta$
set jointly by the smoothness of the true traction and the degree of ill-posedness; for degree 1 with
a smooth truth, $\theta \in (1/2, 1)$. The reproduction task measures $\theta = 0.577$ for a
Gaussian patch.

**Three places the assumptions break.**

1. **A gel of finite thickness.** A real sensor is a layer of thickness $t$. Then $\hat g(k)$ is not
   $1/|k|$ but decays **exponentially** for $|k| t \gg 1$, worsening the ill-posedness from degree 1
   to exponential. Traction information above $|k| \gtrsim 1/t$ is effectively unrecoverable —
   **the sensor thickness sets the physical ceiling on spatial resolution.**
2. **Tangential traction.** Equation (3) covers normal force only. With friction, tangential
   traction (the Cerruti solution) also enters the displacement, and separating normal from
   tangential is impossible without extra information (a measurement of tangential surface
   displacement). That is why a tactile sensor cannot easily read the **friction state**
   (sticking versus sliding) directly.
3. **An unknown contact region.** Equation (4) is solved without knowing the support of $p$ (the
   contact region), and an inverse problem with unknown support is **non-linear** (a free-boundary
   problem). Practice uses two stages: threshold $w$ to fix the region, then solve the linear inverse
   problem inside it.

### R2 — why a standard particle filter dies immediately

**Contact is an equality constraint.** Fix the object pose $q$ and the mode $s$. If mode $s$ is "in
contact with face $i$", that condition is the **equality** of the gap function,

$$
\phi_s(q) = 0
  \tag{6}
$$

($\phi_s > 0$ is separation and $\phi_s < 0$ is penetration, which is impossible). If $\phi_s$ is
smooth with non-vanishing gradient, $\mathcal{M}_s = \{q : \phi_s(q) = 0\}$ is a smooth manifold of
codimension 1 and has **Lebesgue measure zero** in pose space.

**The mechanism of degeneracy.** A standard particle filter draws particles from a continuous
proposal (say the prior plus Gaussian perturbation). That distribution assigns **measure zero** to
$\mathcal{M}_s$, so

$$
\mathbb{P}[\text{a particle lies on } \mathcal{M}_s] = 0 .
$$

The likelihood of "in contact" is zero off $\mathcal{M}_s$, so **every particle's weight is zero**
and $\mathrm{ESS} = 0$ — the filter dies at the first update. Criterion 4 of the reproduction task
shows this numerically. **This is not fixed by increasing the number of particles** (measure zero is
independent of the sample size) — a common misconception.

**The manifold particle filter.** The fix is simple and its cost is explicit.

1. **Represent particles on the manifold.** Attach a mode $s_i$ to each particle and keep its pose
   **projected onto** $\mathcal{M}_{s_i}$. The prior becomes a mixture of "a discrete distribution
   over modes × a continuous distribution on each manifold".
2. **Write the likelihood as a density on the manifold.** It is no longer measure zero, so particles
   consistent with (6) receive positive likelihood.
3. **The cost**: (a) the possible modes must be **enumerated** — the $3^{n_c}$ of `c6-tamp` R3 enters
   as a cost directly; (b) the projection distorts the distribution, so its Jacobian must be
   reflected in the weights (otherwise a bias appears); (c) handling mode transitions requires a
   proposal that moves between manifolds.

**Where the assumption breaks**: if (A3) independence fails (gel hysteresis, sensor drift), the
product of likelihoods **over-counts** the evidence and the posterior becomes too sharp. The LLR
accumulation of (2) then looks faster than it is and the filter converges confidently to the wrong
mode — the most dangerous failure in contact estimation.

### R3 — the rate at which ambiguity is resolved

Let two modes have observation models $z \mid s_j \sim \mathcal{N}(a_j, \sigma^2)$ with $s_1$ the
truth. The log-likelihood ratio of one observation is

$$
\mathrm{LLR} = \log\frac{\mathcal{N}(z; a_1,\sigma^2)}{\mathcal{N}(z; a_2,\sigma^2)}
  = \frac{(z-a_2)^2 - (z-a_1)^2}{2\sigma^2}
  = \frac{(a_1 - a_2)}{\sigma^2}\left(z - \frac{a_1+a_2}{2}\right).
$$

Substituting $z = a_1 + \sigma\epsilon$ gives
$\mathrm{LLR} = \frac{d^2}{2\sigma^2} + \frac{d}{\sigma}\epsilon$ with $d = a_1 - a_2$, which is (2):
**mean $d^2/2\sigma^2$, variance $d^2/\sigma^2$ — the mean is half the variance.** That is a general
property of log-likelihood ratios (an exact identity in the Gaussian case), and hence after $T$
observations

$$
\mathbb{E}[\mathrm{LLR}_T] = \frac{T d^2}{2\sigma^2},
\qquad
\mathrm{sd}[\mathrm{LLR}_T] = \frac{d\sqrt{T}}{\sigma}.
  \tag{7}
$$

Taking "the mean is twice the standard deviation" as the confidence criterion gives
$T \gtrsim 16\sigma^2/d^2$. So **the number of observations needed is inversely proportional to the
square of the geometric distance between the modes.** The reproduction task confirms that with
$d = 0.35$ and $\sigma = 0.5$ the expected LLR is $0.245$ per observation, and measures the mean
posterior rising to $0.828$ after 12 observations.

> **Mind the Jensen gap.** The probability computed from the mean LLR of (7),
> $\sigma(\mathbb{E}[\mathrm{LLR}_{12}]) = \sigma(2.94) = 0.950$, **differs from the measured mean
> posterior $0.828$.** The posterior is a non-linear (logistic) function of the LLR, so
> $\mathbb{E}[\sigma(X)] \ne \sigma(\mathbb{E}[X])$. Reporting the two interchangeably is a common
> error.

## Proof sketch

### R2 — degeneracy on a measure-zero posterior, and its fix

**Hypotheses** H1: (A2) — the contact condition is a smooth function $\phi_s$ of pose alone with
$\nabla\phi_s \ne 0$. H2: the proposal (prior plus transition) is **absolutely continuous** with
respect to Lebesgue measure on pose space. H3: the likelihood of the "in contact" observation is zero
off $\mathcal{M}_s$.
**Conclusion** C: $\mathbb{P}[\mathrm{ESS} = 0] = 1$ — the standard particle filter degenerates at
the first update. And replacing H2 by "a distribution on the manifold" removes the degeneracy.

**Strategy**: get that a codimension-1 manifold has measure zero from the implicit function theorem,
and use that an absolutely continuous distribution assigns probability zero to a measure-zero set.
Two lines, but a strong conclusion.

1. **$\mathcal{M}_s$ has measure zero.** By H1 and the implicit function theorem, $\mathcal{M}_s$ is
   locally the graph of an $(n-1)$-dimensional function, and it is covered by countably many such
   pieces, so it has measure zero in $\mathbb{R}^n$.
2. **A particle lands on it with probability zero.** By H2 the proposal $\pi$ is absolutely
   continuous, so $\mu(\mathcal{M}_s) = 0 \Rightarrow \pi(\mathcal{M}_s) = 0$.
3. **All weights are zero.** By H3 the likelihood off $\mathcal{M}_s$ is zero, so every particle's
   weight is zero and normalization is impossible. In an implementation this appears as 0/0 or
   $\mathrm{ESS} = 0$.
4. **More particles do not help.** The probability in step 2 does not depend on the number of
   particles, so the degeneracy probability remains 1 as $n_{part} \to \infty$. (Omitted: the variance
   blow-up when the likelihood is relaxed by $\epsilon$ — shrinking the relaxation width $\epsilon$
   reduces the effective sample to $\epsilon^{n-1}$, so the same problem returns in another form; see
   §3 of [Koval et al. 2015](https://doi.org/10.1177/0278364915571007).)
5. **The fix.** Dropping H2 and representing particles with an $(n-1)$-dimensional measure on
   $\mathcal{M}_s$ removes the premises of steps 1–3. Weights are computed as densities on that
   manifold, and a Jacobian correction is applied wherever a projection is used.

**Removing a hypothesis**: dropping $\nabla\phi_s \ne 0$ from H1 (a degenerate tangential contact)
gives the manifold a singularity and the projection is ill defined. Relaxing H3 so that the
likelihood becomes a band of thickness $\epsilon$ removes the degeneracy, but as in the omitted item
of step 4 the **effective sample falls as $\epsilon^{n-1}$**, so the same problem reappears in high
dimension — **relaxation is a delay, not a solution.**

## Problem set

Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Compute $\mathcal{F}[1/\lVert x\rVert](k) = 2\pi/|k|$ directly in two
dimensions (polar coordinates plus a Bessel integral). Then show that for a one-dimensional line load
(plane strain) the kernel is $\log\lVert x\rVert$ and its transform is $-\pi/|k|$, confirming that
**the degree is the same**.
*Solution sketch*: $\int_{\mathbb{R}^2}\frac{e^{-ik\cdot x}}{\lVert x\rVert}dx
= 2\pi\int_0^\infty J_0(|k|r)\,dr = 2\pi/|k|$. For one dimension use the transform of $\log$.
**Both give $|k|^{-1}$, so the degree of ill-posedness is independent of the dimension.**

**P2 (derivation, ★★, R1)** Argue by dimensional analysis that in an elastic layer of finite
thickness $t$, $\hat g(k)$ decays exponentially for $|k|t \gg 1$, and from that write the
**smallest recoverable feature size** in terms of $t$.
*Solution sketch*: the layer's boundary conditions introduce terms of the form $e^{-|k|t}$ (because
the depth-wise solutions of Laplace's equation are $e^{\pm|k|z}$). At noise level $\eta$ the
recovery condition is $e^{-|k|t} \gtrsim \eta$, so $|k| \lesssim \ln(1/\eta)/t$ and the smallest
feature size is $\sim 2\pi t/\ln(1/\eta)$.

**P3 (numerical, ★, R1)** With $N = 128$, $L = 1$, $E = 1$, $\nu = 0.3$, predict the condition number
from (5) and compare it with the measurement in the reproduction task. What is it at $N = 256$?
*Answer*: (5) gives $\mathrm{cond} = N/2 = 64$. The measurement is **941**, far larger — the discrete
kernel's self-term and the periodization lower $\lambda_{\min}$ further. The scaling is linear, so
$N = 256$ gives about $2\times$, i.e. of order $1.9\times10^3$. **Distinguishing "the scaling is
right and the constant is wrong" in your report is the point of this item.** Tolerance: the scaling
ratio is $2.0 \pm 0.3$.

**P4 (numerical, ★★, R3)** For two modes with $d = 0.35$ and $\sigma = 0.5$, find the expected LLR
per observation and its standard deviation, and the smallest number of observations $T$ at which "the
mean is twice the standard deviation". By what factor does $T$ change if $d$ is halved?
*Answer*: per observation $\mathbb{E} = d^2/2\sigma^2 = 0.1225/0.5 = 0.245$ and
$\mathrm{sd} = d/\sigma = 0.7$. After $T$ observations $\mathbb{E} = 0.245T$ and
$\mathrm{sd} = 0.7\sqrt{T}$, and $0.245T \ge 2\cdot0.7\sqrt T$ gives $\sqrt T \ge 5.714$,
$T \ge 32.7$, so $T = 33$ (the general form $T \ge 16\sigma^2/d^2$ gives the same,
$16\cdot0.25/0.1225 = 32.65$). Halving $d$ multiplies $T$ by **4**. Tolerance $10^{-2}$.

**P5 (proof, ★★, R2)** Make step 2 of the proof sketch rigorous: derive from the definition that an
absolutely continuous distribution gives probability zero to a measure-zero set, and state
explicitly that this is **independent of the number of particles**.
*Strategy*: use the definition of absolute continuity ($\mu(A) = 0 \Rightarrow \pi(A) = 0$) directly.
Since the particles are i.i.d., the probability that "at least one lies on the manifold" is
$1 - (1-0)^{n} = 0$.

**P6 (proof, ★★★, R2)** Fill in the omitted item of step 4: when the likelihood is relaxed to a band
$\{|\phi_s(q)| \le \epsilon\}$, write the exponent with which the effective sample size falls in
$\epsilon$, in terms of the pose-space dimension $n$ and the manifold's codimension. How does that
support the claim "relaxation is a delay, not a solution"?
*Strategy*: the measure of the band is proportional to
$\epsilon \cdot (\text{the }(n-1)\text{-volume of the manifold})$, so the fraction of particles inside
it is $O(\epsilon)$; with codimension $m$ it is $O(\epsilon^m)$. As $\epsilon \to 0$ the number of
particles required blows up as $\epsilon^{-m}$.

**P7 (implementation, ★★, R1·R2·R3)** Write (a) the spectral analyzer and (b) the particle filter of
the reproduction task. Requirements: get the eigenvalues of the periodic convolution exactly by FFT,
grid-search the optimal Tikhonov $\alpha$, and implement the manifold projection and the ESS.
*Rubric*: (a) the numbers of criteria 1–4 agree within tolerance; (b) you show the spectral slope is
close to $-1$ in the low-frequency band and moves away as the band widens; (c) you show that the
standard particle filter's $\mathrm{ESS} = 0$ does not change as the particle count goes from $10^3$
to $10^6$; (d) you show numerically that omitting the projection's Jacobian correction biases the
posterior.

**P8 (counterexample, ★★, R1·R4)** Construct a case where "raising the sensor resolution gives a
more accurate contact traction" fails: using the condition number (5) at a fixed noise level $\eta$,
show by the Tikhonov error expression that there is a regime in which the recovery error **grows**
with resolution. Combine that with the finite-thickness result of P2 and write the practical
conclusion in one paragraph.
*Property checklist*: with the regularization held fixed, high-frequency noise amplification grows
linearly in $N$. Re-optimizing $\alpha$ reduces the error, but the **effective resolution** stays
capped by the ceiling set by $\eta$ and $t$ — so raising the sensor resolution beyond that ceiling
buys nothing.

## Paper reading

**Two must-reads.** Write a one-page note on each using the ten fixed questions.

1. **Yuan, Dong & Adelson, "GelSight: high-resolution robot tactile sensors for estimating geometry
   and force" (2017, Sensors)** — role: `seminal`. <https://doi.org/10.3390/s17122762> (§2–4)
   *Why read it*: see how the inverse problem of R1 is actually set up on a real sensor. In
   particular, examine **how geometry recovery and force recovery are separated** and what
   assumptions that separation uses.
   Extra questions: (a) how does the spatial resolution the authors report compare with the thickness
   limit of P2? (b) does the force-estimation calibration solve the inverse problem of R1 explicitly,
   or sidestep it by regression? (c) what is claimed, and what is not, about tangential traction (the
   friction state)?
2. **Koval, Pollard & Srinivasa, "Pose estimation for planar contact manipulation with manifold
   particle filters" (2015, IJRR)** — role: `standard`.
   <https://doi.org/10.1177/0278364915571007> (§3–5)
   *Why read it*: the source of R2. Both the diagnosis (**a measure-zero posterior**) and the
   prescription (manifold projection) are here. It is the paper that breaks the habit of thinking a
   particle filter can be fixed by drawing more particles.
   Extra questions: (a) how do the authors handle the projection's Jacobian (or not)? (b) how is the
   proposal for mode transitions designed? (c) can the cost as the number of modes grows be connected
   to the $3^{n_c}$ of `c6-tamp` R3?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation or one figure. (4) what is guaranteed theoretically,
and **what is not**? (5) the independent and dependent variables and the baselines, and were the
baselines tuned fairly? (6) does the metric match the claim, and are variance and seeds reported?
(7) what is missing for reproduction? (8) if the result were wrong, which assumption would you doubt
first? (9) computational and memory complexity, and real-time feasibility. (10) what would you change
to go beyond this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 5 minutes in total, under 1 GB of
memory. numpy only (including its FFT). No external data.

**Input data (given by the lesson).**

*(a) Spectral analysis.* A periodic grid with $N = 128$ and $L = 1$ (so $h = L/N$), $E = 1$,
$\nu = 0.3$. The kernel is $g(x) = \frac{1-\nu^2}{\pi E}\frac{1}{\lVert x\rVert}$ with the self-term
($x = 0$) set to $\frac{1-\nu^2}{\pi E}\cdot\frac{2\ln(1+\sqrt2)}{h}$. The eigenvalues of the
periodic convolution are $\lambda = \mathrm{FFT}_2[g]\cdot h^2$. The true traction is a Gaussian
patch with $\sigma_p = 0.06L$ (normalized to a maximum of 1), the noise is white Gaussian scaled by
the standard deviation of $w$, and the seed is 0.

*(b) Contact particle filter.* The pose is $(x, y) \ge 0$ with two walls, $x = 0$ (mode A) and
$y = 0$ (mode B). The observation is a noisy measurement of the contact normal angle, with mode A at
$a_1 = 0$ and mode B at $a_2 = 0.35$, $\sigma = 0.5$, and mode A the truth. The prior is uniform on
$[0, 0.3]^2$ (for the standard filter); the manifold filter projects half the particles to $x = 0$
and half to $y = 0$. 2000 particles, 12 observations, seeds $100..299$ (averaged over 200 runs).

**Acceptance criteria — all five must hold.**

1. **The spectral law (checking R1)** — on the low-frequency band $|k| < 0.1\,\pi/h$ (128 modes), a
   linear fit of $\log\lambda$ against $\log|k|$ has slope $-1.078 \pm 0.05$ with $r^2 \ge 0.99$
   (measured slope $-1.0778$, $r^2 = 0.9977$). Widening the band to $0.2\pi/h$ and $0.4\pi/h$ moves
   the slope to $-1.118$ and $-1.246$, **away from $-1$** — write one paragraph in the report
   attributing this to the discrete self-term and the periodization.
2. **Condition number** — over all modes with $k \ne 0$,
   $\lambda_{\max}/\lambda_{\min} = 941 \pm 10$, and doubling $N$ multiplies that ratio by
   $2.0 \pm 0.3$ (the signature of degree-1 ill-posedness). Also report that this is **an order of
   magnitude away** from the prediction $N/2 = 64$ of (5) (P3).
3. **Tikhonov convergence rate** — for noise $\eta \in \{10^{-4}, 10^{-3}, 10^{-2}, 10^{-1}\}$,
   grid-searching the optimal $\alpha$ reproduces the relative errors
   $0.00238, 0.00955, 0.03675, 0.12766$ to within 5% relative, and a log fit gives
   $\theta = 0.577 \pm 0.03$.
4. **Degeneracy of the standard particle filter (checking R2)** — the standard filter with a uniform
   prior on $[0,0.3]^2$ has **$\mathrm{ESS} = 0$ at the first update** (all weights exactly zero).
   Increasing the particle count from $2\times10^3$ to $10^6$ changes nothing.
5. **The manifold filter and ambiguity resolution (checking R3)** — the 200-run mean posterior
   $\mathbb{P}[\text{mode A}]$ of the manifold filter **increases monotonically** over 12
   observations and matches

   | observation | 1 | 2 | 4 | 6 | 8 | 10 | 12 |
   |---|---|---|---|---|---|---|---|
   | $\mathbb{P}[A]$ | 0.543 | 0.585 | 0.641 | 0.709 | 0.769 | 0.804 | 0.828 |

   to within an absolute error of 0.03, with the mean ESS falling from $1825$ to $1285$. Also compute
   and print the analytic values of (2) — $\mathbb{E}[\mathrm{LLR}] = 0.245$ per observation,
   $\mathrm{sd} = 0.7$ — and write one paragraph on **why** $\sigma(\mathbb{E}[\mathrm{LLR}_{12}])
   = 0.950$ differs from the measured mean posterior $0.828$ (the Jensen gap).

**Baselines.** (a) The analytic spectrum $\lambda = 2(1-\nu^2)/(E|k|)$ — criterion 1. (b) The
analytic LLR of (2) — criterion 5. (c) Deliberately broken versions of itself: the standard filter
(criterion 4) and a projection without the Jacobian correction (P7 (d)).

**Failure table**

| Symptom | Cause | How to check |
|---|---|---|
| the spectral slope is near $-2$ | the kernel was written $1/r^2$ (the strain Green's function rather than the displacement one) | check whether $\lambda$ diverges as $k \to 0$ (degree 1) or converges |
| negative $\lambda$ appears | the self-term was set too small, making the kernel non-positive-definite | recompute the self-term with the factor $2\ln(1+\sqrt2)/h$ |
| the Tikhonov error is independent of the noise | $\alpha$ was held fixed (not re-chosen per noise level) | check that the optimal $\alpha$ grows with $\eta$ |
| the standard filter's ESS is not zero | the likelihood was not set to zero off the manifold (it was relaxed to a Gaussian) | send the relaxation width to zero and watch the ESS go to zero |
| the posterior is not monotone | only one seed was run (the LLR is a random walk) | confirm you are averaging 200 runs — monotonicity is a property of the **expectation** |
| the posterior jumps straight to 1 | the angular separation $d$ was set large (say $\pi/2$) | confirm $d = 0.35$ and $\sigma = 0.5$ |

## Open problems

- **(open problem) The inverse problem with an unknown contact region** — as in failure mode 3 of
  R1, not knowing the support of the traction makes the problem a **non-linear free-boundary
  problem**, and practice's two stages (threshold, then linear inversion) come with no guarantee on
  error propagation. Current approach: learning-based segmentation of the contact region from the
  displacement field ([Bauza et al. 2019](https://arxiv.org/abs/1904.10944)). What is missing: joint
  estimation of the region and the traction with an error bound.
- **(open problem) The absence of a standard tactile benchmark** — sensors differ in their physics
  (thickness, elasticity, illumination), so results on the same task cannot be compared, and since
  the condition number of R1 depends on the sensor resolution, even the comparison "higher resolution
  is better" does not hold up. Current approaches: open sensor designs and datasets
  ([Yuan et al. 2017](https://doi.org/10.3390/s17122762),
  [Calandra et al. 2018](https://arxiv.org/abs/1805.11085)). What is missing: a task set and metrics
  normalized for sensor physics.
- **(open problem) Estimation when there are many modes** — the manifold filter must enumerate
  modes, so it inherits the $3^{n_c}$ of `c6-tamp` R3 directly. With several fingers or mixed
  environmental contacts the enumeration is impossible, and then there is no way to represent the
  posterior. Current approaches: the reduced problem of finding one external contact from joint
  torques ([Manuelli & Tedrake 2016](https://doi.org/10.1109/IROS.2016.7759743)), and global tactile
  localization ([Petrovskaya & Khatib 2011](https://doi.org/10.1109/TRO.2011.2138450)). What is
  missing: a way to represent the posterior over contact state without enumerating modes.

## Concept check

Run `rc quiz s2-tactile-contact-estimation`. Concept checking only; the real work is the problem set
and the reproduction task.

The six items cover: the Fourier multiplier of the tactile forward operator; why more particles do
not fix the degeneracy; the mean-variance relation of the log-likelihood ratio; why the mean
posterior differs from the probability of the mean LLR; the three costs of a manifold particle
filter; and the resolution ceiling set by the gel thickness.

## How to study this stage

1. **Write the two inverse problems apart (20 min)** — put "the continuous inverse problem
   (displacement → traction, ill-posed)" and "the mixed discrete–continuous estimation problem
   (mode + pose, measure zero)" on one page with the pathology specific to each. Without that
   separation you stay at the vague "tactile estimation is hard".
2. **Get the spectrum by hand (60 min)** — rewrite (3)→(4)→(1) from a blank page and compute
   $\mathcal{F}[1/r] = 2\pi/|k|$ yourself (P1). Then write out that the condition number (5) is
   linear in the resolution. **This is where "the degree of ill-posedness" becomes concrete.**
3. **Compute that the thickness sets a ceiling (40 min)** — do P2. Seeing that $e^{-|k|t}$ turns
   degree-1 ill-posedness into an exponential one leaves the conclusion that the limit of a
   high-resolution sensor is not electronic but **material**. Solve it together with P8 for a sharper
   picture.
4. **Memorize the measure-zero result in two lines (40 min)** — steps 1–3 of the R2 proof sketch are
   short: "the manifold has measure zero → an absolutely continuous distribution gives it probability
   zero → every weight is zero". Do P5 to confirm from the definition that it is **independent of the
   particle count**.
5. **Implement it and see both pathologies (90 min)** — the reproduction task. In (a), see the
   spectral slope near $-1$ on the low band and moving away as the band widens; in (b), see the
   standard filter die with $\mathrm{ESS} = 0$ and the manifold filter's posterior rise from 0.543 to
   0.828. **The Jensen-gap paragraph of criterion 5 is the most important artifact of this lesson.**
6. **Two papers (120 min)** — read GelSight (the sensor side) first and Koval (the estimation side)
   next. Organize them as the contrast "measure the physics better" versus "reflect the structure of
   the measurement in the estimator".
7. **Problem set (150 min)** — P3, P4 and P7 first, then P1 and P2, then P5, P6 and P8 with whatever
   time remains. P6 (the exponent of the relaxation) is the hardest and explains the limits of
   high-dimensional contact estimation.

**Passing bar**: you can derive (1) and state the degree of ill-posedness, show by computation that
the thickness sets the resolution ceiling, write the measure-zero argument in two lines, and have code
satisfying the five criteria of the reproduction task together with the Jensen-gap paragraph. You have
notes on both papers.
