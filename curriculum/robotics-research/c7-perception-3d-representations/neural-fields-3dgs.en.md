---
id: c7-neural-fields-3dgs
lang: en
title: Neural fields and 3D Gaussian splatting
summary: >-
  Derive the volume rendering integral from the absorption-emission model, prove that NeRF's
  alpha-compositing discretisation is an **exact** integral for piecewise-constant density, and
  then measure its convergence order for smooth density. Quantifies the spectral bias of positional
  encoding through the eigenvalues of the kernel, showing numerically that NeRF's equal-amplitude
  encoding removes the bias inside its band, and measures by Monte Carlo where the affine
  projection approximation of 3D Gaussian splatting breaks.
objectives:
  - Derive the volume rendering integral and the transmittance from the absorption-emission model.
  - Prove that the alpha-compositing discretisation is exact for piecewise-constant density, and measure its convergence order for smooth density.
  - Quantify the spectral bias of positional encoding through the eigenvalues of the Gram matrix and predict the per-frequency convergence time.
  - Derive the affine (EWA) projected covariance $\Sigma' = JW\Sigma W^\top J^\top$ of a 3D Gaussian and identify numerically the regime where the approximation fails.
  - Show that alpha compositing depends on the ordering while the accumulated alpha does not, and explain what that forces on a rasteriser's design.
tags: [perception, neural-fields, nerf, gaussian-splatting, volume-rendering, research]
---

# Neural fields and 3D Gaussian splatting

## Setup and notation

The recommended prerequisites are `c7-two-view-geometry` in this module (the camera model and
projection), `r0-estimation-theory` (numerical integration and estimation) and
`r0-numerical-optimization` (convergence of gradient descent). None of them is locked. The lesson
assumes:

- Analysis: first-order linear ODEs, numerical approximation of integrals and convergence orders,
  Taylor's theorem.
- Linear algebra: symmetric positive definite matrices, eigendecomposition, Gram matrices,
  condition numbers.
- Probability: linear transforms of a Gaussian, covariance, the standard error of a Monte Carlo
  estimate.
- Learning: that gradient descent on a quadratic objective converges as $(1-\eta\lambda_k)^t$ along
  each eigendirection. No network architecture is needed — the spectral bias is quantified in a
  **linear feature model**.

Notation (continuing the C7 conventions):

| Symbol | Meaning |
|---|---|
| $\mathbf{r}(t) = \mathbf{o} + t\mathbf{d}$ | the ray, $t \in [t_n, t_f]$ |
| $\sigma(t) \ge 0$ | density (the extinction coefficient), in units of length$^{-1}$ |
| $c(t) \in \mathbb{R}^3$ | emitted colour |
| $T(t) = \exp\!\big(-\int_{t_n}^{t}\sigma(s)\,ds\big)$ | transmittance |
| $\delta_i = t_{i+1} - t_i$, $\alpha_i = 1 - e^{-\sigma_i\delta_i}$ | interval length and alpha |
| $\gamma(x)$ | the positional encoding $[\sin(2^k\pi x), \cos(2^k\pi x)]_{k<L}$ |
| $\Phi$, $G = \Phi^\top\Phi/m$ | the feature matrix and its Gram matrix, with eigenvalues $\lambda_k$ |
| $\mu, \Sigma$ | mean and covariance of a 3D Gaussian, $\Sigma = RSS^\top R^\top$ |
| $W$, $J$ | the view transform (a rotation) and the Jacobian of the projection |
| $\Sigma' = JW\Sigma W^\top J^\top$ | the 2D covariance under the affine approximation |

**Scale convention**: every measurement is reported against the **dimensionless ratio $s/Z$** for
focal length $f = 500$, depth $Z$ and Gaussian extent $s$ — the validity of the affine
approximation depends on that ratio, not on absolute size.

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the volume rendering integral) [D2]** — in the absorption-emission model the colour
  accumulated along a ray is
  $$C = \int_{t_n}^{t_f} T(t)\,\sigma(t)\,c(t)\,dt,
    \qquad T(t) = \exp\!\Big(-\int_{t_n}^{t}\sigma(s)\,ds\Big) \tag{1}$$
  where $T$ solves $T' = -\sigma T$ with $T(t_n) = 1$.
- **R2 (exactness of the alpha-compositing discretisation) [D3]** — if $\sigma$ and $c$ are
  **constant** on each interval $[t_i, t_{i+1})$, then
  $$C = \sum_{i=1}^{N} T_i\,\alpha_i\,c_i, \qquad
    T_i = \prod_{j<i}(1-\alpha_j) = \exp\!\Big(-\sum_{j<i}\sigma_j\delta_j\Big),\quad
    \alpha_i = 1 - e^{-\sigma_i\delta_i} \tag{2}$$
  is an **identity, not an approximation**. The accumulated alpha is
  $\sum_i T_i\alpha_i = 1 - T_{N+1} \le 1$ and is **invariant** to the ordering of the intervals.
  For smooth $\sigma, c$ with midpoint sampling, the error of (2) is $O(\delta^2)$.
- **R3 (the spectral bias of positional encoding) [D2]** — gradient descent on features $\Phi$
  converges as $(1-\eta\lambda_k)^t$ along eigendirection $k$ of the Gram matrix, so the number of
  iterations needed to halve the residual is
  $$t_{1/2}(k) = \frac{\ln 2}{\eta\,\lambda_k} \tag{3}$$
  For Fourier features of amplitude $a_k$, $\lambda_k = a_k^2/2$, so **an equal-amplitude encoding
  ($a_k = 1$), as NeRF uses, makes every frequency inside the encoded band learn at the same rate**
  — the bias appears outside the band, as "not representable".
- **R4 (the affine projection of a 3D Gaussian) [D2]** — expanding the projection
  $m(X) = (fX/Z,\ fY/Z)$ to first order at $\mu$ gives
  $$J = \frac{\partial m}{\partial X}\Big|_{\mu}
      = \begin{bmatrix} f/Z & 0 & -fX/Z^2 \\ 0 & f/Z & -fY/Z^2 \end{bmatrix},
    \qquad \Sigma' = J\,W\,\Sigma\,W^\top J^\top \tag{4}$$
  and the parameterisation $\Sigma = RSS^\top R^\top$ is always positive semi-definite. The
  approximation error grows with $s/Z$ and with the off-axis distance together.
- **R5 (alpha compositing depends on the ordering) [D2]** — the sum (2) depends on the order of the
  intervals. The accumulated alpha is invariant but **the colour is not**. That is why 3DGS has to
  depth-sort per tile, and why approximating the sort is itself a rendering error.

## Derivation

### R1 — from the absorption-emission model to the integral

Consider the light crossing an infinitesimal interval $[t, t+dt]$ along the ray. The density
$\sigma(t)$ is the extinction probability per unit length, so the probability of passing the
interval is $1 - \sigma(t)dt$. Writing $T(t)$ for the probability of reaching $t$ from $t_n$
unobstructed,

$$T(t + dt) = T(t)\big(1 - \sigma(t)\,dt\big) \;\Longrightarrow\;
  \frac{dT}{dt} = -\sigma(t)\,T(t), \quad T(t_n) = 1$$

and this first-order linear ODE has the solution $T(t) = \exp(-\int_{t_n}^t\sigma)$. The light
emitted in the same interval is $\sigma(t)c(t)dt$, and its probability of reaching the camera is
$T(t)$, so the total is (1). (Max 1995 catalogues the derivation and variants of the
absorption-emission model **[D0]**.)

**The units and meaning of $\sigma$**: $\sigma$ is not a probability density but an **extinction
coefficient** (units of length$^{-1}$). Multiplying $\sigma$ by a constant makes the scene that
much more opaque, and changing the units of the ray parameter $t$ changes $\sigma$ inversely.
Reading the $\sigma$ a network outputs as an "occupancy probability" is wrong — the quantity that
is a probability is $\alpha_i = 1 - e^{-\sigma_i\delta_i}$, and **the interval length enters it**.

### R2 — the discretisation: why it is not an approximation

Let $\sigma \equiv \sigma_i$ and $c \equiv c_i$ on $[t_i, t_{i+1})$ and split the integral (1) by
interval:

$$C = \sum_i \int_{t_i}^{t_{i+1}} T(t)\,\sigma_i\,c_i\,dt.$$

Inside the interval $T(t) = T_i\,e^{-\sigma_i(t - t_i)}$ with $T_i := T(t_i)$, so

$$\int_{t_i}^{t_{i+1}} T(t)\sigma_i c_i\,dt
  = T_i\,\sigma_i c_i \int_0^{\delta_i} e^{-\sigma_i u}\,du
  = T_i\,c_i\,\big(1 - e^{-\sigma_i\delta_i}\big)
  = T_i\,\alpha_i\,c_i$$

which is (2). And since $T_{i+1} = T_i e^{-\sigma_i\delta_i} = T_i(1-\alpha_i)$, we get
$T_i = \prod_{j<i}(1-\alpha_j)$ — that is alpha compositing. **This is not a numerical
approximation of the integral but the integral closed under the piecewise-constant assumption.**
The distinction matters: presenting NeRF's equation (3) as a "Riemann sum" is what makes people put
the exponential of the transmittance in the wrong place.

**Accumulated alpha**: setting $c_i \equiv 1$ in (2) gives
$\sum_i T_i\alpha_i = \sum_i (T_i - T_{i+1}) = 1 - T_{N+1}$ (a telescoping sum). So the accumulated
alpha is always at most one and is **the same however the intervals are ordered** (because
$T_{N+1} = \exp(-\sum\sigma_j\delta_j)$ is order-independent). The colour is not — see R5.

Measured (12 piecewise-constant intervals, random $\sigma \in [0,3]$ and $c \in [0,1]$): the
difference between the analytic value and (2) is **exactly zero** ($0.000\times10^{0}$ in double
precision) and the accumulated alpha is $0.9908 \le 1$.

**The order for smooth $\sigma, c$**: real scenes are not piecewise constant. Evaluating $\sigma, c$
at interval midpoints and using (2) gives an $O(\delta^2)$ error. Measured
($\sigma(t) = 1.5 + 2\sin^2 3t$, $c(t) = 0.5 + 0.4\cos 2t$, $t \in [0,4]$, reference
$0.7376020086$):

| $N$ | 8 | 16 | 32 | 64 | 128 | 256 | 512 |
|---|---|---|---|---|---|---|---|
| error | $7.94\times10^{-3}$ | $3.26\times10^{-3}$ | $8.00\times10^{-4}$ | $1.99\times10^{-4}$ | $4.97\times10^{-5}$ | $1.24\times10^{-5}$ | $3.10\times10^{-6}$ |
| observed order | — | 1.28 | 2.03 | 2.01 | 2.00 | 2.00 | 2.00 |

Second order. **Where the assumptions break**: (1) if $\sigma$ is nearly discontinuous near a
surface, the second-order behaviour of midpoint evaluation collapses to first order or worse, and
uniform intervals **step over** the surface entirely. That is the reason for NeRF's hierarchical
sampling (coarse then fine resampling). (2) Adding a random jitter per interval (stratified
sampling) makes the estimator **unbiased** at the price of variance — during training that variance
acts like a regulariser, but leaving the jitter on at evaluation time makes the PSNR
irreproducible. (3) Changing $\delta_i$ makes the same $\sigma$ give a different $\alpha$. Code
that changes the sample count while assuming "the density is unchanged" is wrong.

### R3 — positional encoding and spectral bias

**Reduction to a linear feature model.** Training a linear model $\hat{y} = \Phi w$ on $m$ samples
with a squared loss, gradient descent is

$$w_{t+1} = w_t - \eta\,\frac{1}{m}\Phi^\top(\Phi w_t - y)$$

and in the eigenbasis of $G = \Phi^\top\Phi/m = U\Lambda U^\top$ each coordinate
$\tilde{w} = U^\top w$ evolves independently as
$\tilde{w}_{t+1,k} - \tilde{w}^\star_k = (1-\eta\lambda_k)(\tilde{w}_{t,k} - \tilde{w}^\star_k)$.
The iterations needed to halve the residual follow from $(1-\eta\lambda_k)^t = 1/2$:

$$t_{1/2}(k) = \frac{\ln 2}{-\ln(1-\eta\lambda_k)} \approx \frac{\ln 2}{\eta\lambda_k}
  \quad (\eta\lambda_k \ll 1)$$

which is (3). **Directions with large eigenvalues are learned first** — that is all spectral bias is.

**The eigenvalues of Fourier features.** On a uniform grid $x_j = j/m$ with
$\phi_k(x) = a_k[\sin(2\pi kx), \cos(2\pi kx)]$, columns of different frequencies are orthogonal and
each frequency's Gram block is $\frac{a_k^2}{2}I_2$. So $\lambda_k = a_k^2/2$ and (3) becomes

$$t_{1/2}(k) = \frac{2\ln 2}{\eta\,a_k^2}. \tag{5}$$

**Three cases were measured** ($m = 512$, target
$y = \frac{1}{16}\sum_{f=1}^{16}\sin 2\pi fx$, $\eta = 0.5/\lambda_{\max}$, iterations until the
per-frequency residual halves):

| $a_k$ | $f=1$ | 2 | 3 | 4 | 5 | 6 | 7 | 8 | $\cdots$ | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $k^{0}$ (equal amplitude, NeRF) measured | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | | 2 | 2 | 2 |
| $k^{0}$ predicted by (5) | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | | 2 | 2 | 2 |
| $k^{-1}$ measured | 1 | 6 | 13 | 22 | 35 | 50 | 68 | 89 | | 272 | 312 | 355 |
| $k^{-1}$ predicted by (5) | 1 | 6 | 12 | 22 | 35 | 50 | 68 | 89 | | 272 | 312 | 355 |

With equal amplitudes **every frequency halved in exactly the same number of iterations (2)** and
the measured/predicted ratio was 1.000 at every frequency. With $a_k = k^{-1}$, $t_{1/2}$ grows as
$k^{2}$ and matches (5) down to the $\ln 2$ factor (median ratio 0.694 = $\ln 2$). Dropping further
to $a_k = k^{-2}$ pushed $t_{1/2}$ of the highest frequency past $9\times10^{4}$ iterations, beyond
the experiment's budget.

**Without any encoding**: with $x$ as the only feature, none of the target's frequencies is
representable — measured, the relative error stayed at $0.9410$ and **did not move at all** over
4000 iterations. An $L = 4$ encoding fit $f \le 4$ exactly and left the residuals of $f = 8, 16$ at
their initial values (0.186, 0.193). $L = 8$ fit everything (relative error $6\times10^{-4}$).

**To summarise**: positional encoding does two things. (1) **It extends the band** — $L$ sets the
frequency ceiling, and above it the issue is not learning speed but **representability**. (2) **It
flattens the band** — an equal-amplitude encoding equalises the eigenvalues inside the band and so
removes the spectral bias.

**Where the assumptions break**: (1) this analysis is a **linear feature model**. A real MLP's NTK
changes during training and its eigenvalue distribution depends on depth. The linear model bounds
what the encoding *can* do; it does not describe what an MLP actually learns (Tancik et al. 2020 go
further with the NTK **[D0]**). (2) If the grid is not uniform, the orthogonality of the frequency
columns fails and $\lambda_k = a_k^2/2$ does not hold — with non-uniform samples you have to look at
the Gram matrix directly. (3) Widening the band brings **aliasing** and overfitting: once
frequencies above the training resolution are representable, novel views show high-frequency
artefacts. That is the starting point of the Mip-NeRF line.

### R4 — projecting a 3D Gaussian (splatting)

Sending a 3D Gaussian $\mathcal{N}(\mu, \Sigma)$ through a camera does not give a Gaussian, because
**the projection is nonlinear**. The practical answer is to expand the projection to first order at
$\mu$ (EWA splatting, Zwicker et al. 2002 **[D0]**). With camera coordinates
$X_c = W(X - \mathbf{o})$ and the projection $m(X_c) = (fX_c/Z_c,\ fY_c/Z_c)$,

$$m(X_c) \approx m(\mu_c) + J\,(X_c - \mu_c), \qquad
  J = \begin{bmatrix} f/Z & 0 & -fX/Z^2 \\ 0 & f/Z & -fY/Z^2 \end{bmatrix}_{\mu_c}$$

and since an affine transform of a Gaussian is Gaussian,

$$X \sim \mathcal{N}(\mu, \Sigma) \;\Longrightarrow\;
  m(X) \approx \mathcal{N}\big(m(\mu_c),\; JW\Sigma W^\top J^\top\big)$$

which is (4). The third column of $J$ is the gradient along depth, and this is where **depth
variance mixes into the on-screen shape** — the reason an elongated Gaussian appears sheared on
screen.

**Parameterising $\Sigma$**: $\Sigma$ must stay positive semi-definite throughout optimisation, so
one uses $\Sigma = R\,S\,S^\top R^\top$ (with $R$ parameterised by a quaternion and $S$ by positive
diagonal scales). By construction $\Sigma = (RS)(RS)^\top \succeq 0$. Measured: over 20,000 random
(scale, rotation) pairs there were **no** negative eigenvalues.

**Where the affine approximation breaks (measured)**: $4\times10^6$ samples were drawn from
$\mathcal{N}(\mu,\Sigma)$ and actually projected, and the sample covariance
$\Sigma'_{\mathrm{MC}}$ was compared with (4) ($f = 500$, $Z = 5$, Gaussian semi-axes
$s, 0.6s, 1.4s$ under an arbitrary rotation):

| $s/Z$ | off-axis 0 px | off-axis 200 px | off-axis 500 px | mean shift (max) |
|---|---|---|---|---|
| 0.002 | $7.1\times10^{-4}$ | $6.2\times10^{-4}$ | $6.7\times10^{-5}$ | 0.003 px |
| 0.01 | $3.8\times10^{-4}$ | $8.1\times10^{-4}$ | $2.5\times10^{-3}$ | 0.10 px |
| 0.05 | $1.4\times10^{-2}$ | $1.9\times10^{-2}$ | $2.9\times10^{-2}$ | 2.37 px |
| 0.2 | $9.9\times10^{-1}$ | $9.4\times10^{-1}$ | $9.9\times10^{-1}$ | 56.0 px |

(The values are
$\lVert\Sigma'_{\text{affine}} - \Sigma'_{\mathrm{MC}}\rVert_F / \lVert\Sigma'_{\mathrm{MC}}\rVert_F$.)
How to read it: for $s/Z \le 0.01$ the approximation is accurate to the $10^{-3}$ level, at
$s/Z = 0.05$ it degrades to a few percent, and at $s/Z = 0.2$ it is **entirely invalid** (relative
error near one). Increasing the off-axis distance worsens the error at the same $s/Z$
($s/Z = 0.01$: $3.8\times10^{-4} \to 2.5\times10^{-3}$). The mean position moves too — by
**56 pixels** at $s/Z = 0.2$ and 500 px off axis.

**Where the assumptions break**: (1) large Gaussians close to the camera (large $s/Z$) and (2) the
edges of a wide-angle frame (large off-axis) break the affine approximation. That is why
implementations cap the on-screen size of a Gaussian and clip near the camera. (3) A Gaussian with
$Z \le 0$ has no defined projection at all and must be culled, and the gradient is discontinuous at
the culling boundary. (4) An optimisation solution that uses a single very large Gaussian for a
low-frequency region (floor, sky) lands in exactly this regime, so a good reported PSNR can still
break down at a novel view.

### R5 — alpha compositing and sorting

The sum (2) depends explicitly on the order of $i$, because $T_i$ is the product of what comes
before. Measured (6 primitives, $\alpha \in [0.1, 0.6]$, colours in $[0,1]$):

| Order | colour $C$ | accumulated alpha |
|---|---|---|
| by depth (front to back) | 0.481154 | 0.943034 |
| unsorted | 0.564796 | 0.943034 |
| back to front | 0.591136 | 0.943034 |

**The accumulated alpha is identical in all three cases and the colour is different in all three.**
So the tile rasteriser of 3DGS must depth-sort, and using a **per-tile approximate sort** for speed
introduces a rendering error of its own (must-read 2 treats that trade-off as a design choice).
This is an important difference from NeRF: integrating sequentially along a ray makes sorting free,
while gathering primitives and rasterising them makes you pay for it.

## Proof sketch

### R2 — exactness of the alpha-compositing discretisation

**Hypotheses** H1: $\sigma(t) = \sigma_i \ge 0$ and $c(t) = c_i$ are constant on each
$[t_i, t_{i+1})$. H2: the intervals partition $[t_n, t_f]$. H3: $T(t_n) = 1$.
**Conclusions** C1: (2) holds as an **identity**. C2:
$\sum_i T_i\alpha_i = 1 - T_{N+1} \le 1$, and it is order-invariant. C3: with midpoint evaluation
for smooth $\sigma, c$ the error is $O(\delta^2)$.

**Strategy**: write $T$ in closed form on each interval and integrate exactly. C2 is a telescoping
sum, C3 a Taylor expansion.

1. **C1**: under H1, $T(t) = T_i e^{-\sigma_i(t-t_i)}$ on $[t_i, t_{i+1})$, which is the solution of
   $T' = -\sigma T$ stitched interval by interval (H3 gives $T_1 = 1$). Using
   $\int_0^{\delta_i}e^{-\sigma_i u}du = (1-e^{-\sigma_i\delta_i})/\sigma_i$, the $\sigma_i$ cancels
   and $T_i\alpha_i c_i$ remains. An interval with $\sigma_i = 0$ is handled correctly as
   $\alpha_i = 0$ (in the limit). Summing gives C1. $\square$
2. **C2**: from $T_{i+1} = T_i(1-\alpha_i)$ we get $T_i\alpha_i = T_i - T_{i+1}$, so
   $\sum_{i=1}^N T_i\alpha_i = T_1 - T_{N+1} = 1 - T_{N+1}$. Since
   $T_{N+1} = \exp(-\sum_j \sigma_j\delta_j) > 0$ the sum is below one, and because the sum in the
   exponent is order-independent, so is the accumulated alpha. $\square$
3. **C3**: evaluating $\sigma, c$ at the midpoint $\bar{t}_i$ makes each interval's integration error
   of the midpoint-rule form $\frac{\delta_i^3}{24}\max|g''|$, and with $O(1/\delta)$ intervals the
   total is $O(\delta^2)$. The measured order converging to 2.00 is this. (Left out: that the
   accumulated integral inside $T$ is approximated to the same order, and that the error of the
   product propagates at the same order.) $\square$
4. **Why "not an approximation" matters**: describing (2) as a Riemann sum creates the wrong
   intuition that "more samples make it exact". In fact it is exact under the **piecewise-constant
   assumption**, and what more samples reduce is only the gap between that assumption and the real
   scene. That is why, near a surface, **concentrating** samples (hierarchical sampling) beats
   increasing their number by a wide margin.
5. **Remove a hypothesis**: if H1 fails (if $\sigma$ varies inside an interval), C1 becomes an
   approximation rather than an identity and the error is controlled only at the order of C3. In
   particular, if $\sigma$ is nearly discontinuous at a surface, the second-order behaviour of
   midpoint evaluation fails and the intervals can step over the surface — which is how thin
   structures disappear under uniform sampling.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R1)** Derive $T' = -\sigma T$ from the infinitesimal transmission argument and
write (1). Then compute (1) in closed form for constant $\sigma \equiv \sigma_0$ and confirm that
$C \to c_0$ as $t_f \to \infty$.
*Solution sketch*: $T(t+dt) = T(t)(1-\sigma dt)$ gives the ODE. At constant density
$C = c_0(1 - e^{-\sigma_0(t_f-t_n)})$, which tends to $c_0$.

**P2 (proof, ★★★, R2)** Prove C1, C2 and C3. In C3 in particular, make explicit **how the
approximation error of the transmittance $T$ propagates** and show that the total error is still
$O(\delta^2)$.
*Strategy and key inequality*: bound $|\hat{T}_i - T(t_i)|$ by $O(\delta^2)$ and split with the
triangle inequality
$|\hat{T}\hat{\alpha}\hat{c} - T\alpha c| \le |\hat{T}-T|\,\alpha c + T|\hat\alpha-\alpha|c
+ T\alpha|\hat c - c|$. It suffices to show each term is $O(\delta^2)$ (that is, $O(\delta^3)$ per
interval).

**P3 (numerical, ★, R2)** For piecewise-constant $\sigma = (0.5, 2.0, 0.0, 3.0)$,
$c = (0.2, 0.9, 0.5, 0.1)$ and $\delta = (0.5, 0.5, 1.0, 0.5)$, compute $\alpha_i$, $T_i$, $C$ and
the accumulated alpha by hand.
*Answer*: $\alpha = (0.221199, 0.632121, 0, 0.776870)$,
$T = (1, 0.778801, 0.286505, 0.286505)$,
$C = 0.221199\cdot0.2 + 0.778801\cdot0.632121\cdot0.9 + 0 + 0.286505\cdot0.776870\cdot0.1
= 0.509564$, and the accumulated alpha is
$1 - e^{-(0.25+1.0+0+1.5)} = 0.936072$. Tolerance $10^{-6}$. Check: compute the accumulated alpha
also as $\sum T_i\alpha_i$ and confirm the same value.

**P4 (numerical, ★★, R3)** Build Fourier features of amplitude $a_k = k^{-p}$ on a uniform grid with
$m = 512$ and compare, for $p \in \{0, 1, 2\}$, (a) the eigenvalues of the Gram matrix, (b) the
$t_{1/2}(k)$ predicted by (5), and (c) the $t_{1/2}(k)$ measured by gradient descent.
*Answer (reference measurements)*: at $p=0$ all $\lambda_k = 0.5$ and the measured
$t_{1/2} = 2$ at every frequency, with a measured/predicted ratio of 1.000. At $p=1$ the measured
$t_{1/2} = 1, 6, 13, 22, 35, 50, 68, 89, \dots, 355$ and the median ratio against
$1/(\eta\lambda_k)$ is $0.694 = \ln 2$. Tolerance: the ratio must be within $\pm10\%$ of $\ln 2$.
Check: confirm that at $p=2$ the $t_{1/2}$ of $f=16$ exceeds $10^{4}$.

**P5 (derivation, ★★, R4)** Derive the $J$ of (4) and compute $\Sigma'$ by hand for
$\Sigma = \operatorname{diag}(s^2, s^2, s_z^2)$ and $\mu = (0,0,Z)$. Under what condition does the
depth variance $s_z^2$ **not** enter the screen covariance?
*Solution sketch*: $\partial(fX/Z)/\partial Z = -fX/Z^2$ is the third column. If $\mu$ lies on the
optical axis then $X = Y = 0$, the third column vanishes and
$\Sigma' = (f/Z)^2\operatorname{diag}(s^2, s^2)$ — **only on the optical axis** does the depth
variance stay out of the screen. Off axis, $-fX/Z^2 \ne 0$ lets $s_z^2$ in.

**P6 (implementation, ★★, R2·R4)** (a) Implement (2) and match the analytic value to within
$10^{-15}$ on a piecewise-constant case; (b) confirm convergence order 2 on a smooth case; and
(c) compare the $\Sigma'$ of (4) against a Monte Carlo projection, plotting the error curve as
$s/Z$ is swept.
*Rubric*: (a) the difference is at most $10^{-15}$; (b) the observed order is $2.0 \pm 0.1$;
(c) the relative error is $< 10^{-2}$ for $s/Z \le 0.01$ and $> 0.5$ at $s/Z = 0.2$; (d) the Monte
Carlo sample count and standard error are reported.

**P7 (counterexample, ★★, R2·R5)** (a) Construct a scene where uniform sampling **steps over** a
thin surface so the colour is nearly zero, and show that doubling the sample count (without
hierarchical sampling) improves it only slowly. (b) Construct an example where changing the
compositing order changes the colour while the accumulated alpha stays the same.
*Property checklist*: (a) put a large $\sigma$ on a narrow interval and take $\delta$ larger than
that width; (b) show that as the sample count grows the error is erratic rather than $O(\delta^2)$;
(c) the accumulated alpha agrees to several decimals across three different orders; (d) a paragraph
on why "more samples make it exact" is only half true.

**P8 (paper, ★★, R2·R4)** Read NeRF §4 and 3DGS §4–6 and (a) rewrite each paper's rendering
equation in the notation of (2) and (4) here; (b) find in the paper how 3DGS handles sorting (exact
or approximate) and contrast it with R5; and (c) write down **what was not controlled** in the
reported PSNR and speed comparisons.
*Rubric*: for (c), naming at least two of resolution, scene, iteration count and hardware
specifically passes. For (b), writing "the paper does not state it" where that is so is excellent.

## Paper reading

**Two must-reads.** Write a one-page note on each, using the ten fixed questions
(`lesson-standard.md` §5). Read in three passes, and attack questions 4, 5, 6 and 7 in the third.
For the full bibliography, including the recommended papers, run `rc papers c7-neural-fields-3dgs`.

1. **Mildenhall, Srinivasan, Tancik et al., "NeRF: representing scenes as neural radiance fields
   for view synthesis" (2020, ECCV)** — role: `seminal`. <https://arxiv.org/abs/2003.08934>
   (§4 is the core.)
   Extra questions: (a) is the paper's rendering equation the same as (2) here? Where does the
   exponential of the transmittance sit? (b) Why is $L$ chosen differently for the coordinates and
   the directions, and which of the two effects in R3 ("band extension" against "flattening") is
   that aiming at? (c) With uniform sampling only, no hierarchical sampling, which kind of scene
   breaks first (failure mode (1) of R2)?
2. **Kerbl, Kopanas, Leimkühler & Drettakis, "3D Gaussian splatting for real-time radiance field
   rendering" (2023, ACM TOG)** — role: `frontier`. <https://arxiv.org/abs/2308.04079>
   (§4–6 is the core.)
   Extra questions: (a) explain from an optimisation standpoint why the covariance is parameterised
   as $\Sigma = RSS^\top R^\top$. (b) How does the limit of the affine projection (the measurement
   table of R4) show up in the paper's design choices (on-screen size caps, clipping, density
   control)? (c) In the speed comparison, are the NeRF-side baseline's implementation and hardware
   fair?

**The ten fixed questions**: (1) which problem under which assumptions; (2) what exactly earlier
work could not do; (3) the core idea in one equation; (4) what is guaranteed and **what is not**;
(5) the independent and dependent variables and the baselines, fairly tuned or not; (6) whether the
metric matches the claim, and whether variance and seeds are reported; (7) what is missing for
reproduction; (8) the first assumption to doubt if the result were wrong; (9) time and memory
complexity and real-time behaviour; (10) what you would change to go beyond it in a year.

**Recommended**: Max 1995 (the origin of the absorption-emission model), Zwicker et al. 2002 (the
origin of the affine approximation), Tancik et al. 2020 (the NTK analysis of spectral bias).

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 10 minutes in total, numpy and
scipy only. The input is an analytic generator this lesson specifies; no external data and no GPU
are needed.

> **Stated difference from the blueprint**: the reproduction task in the design is "train NeRF and
> 3DGS on a small scene and reproduce the reported PSNR trend (3DGS is faster)". Training either
> method requires a GPU, and §6 of the lesson standard requires any GPU-dependent task to be marked
> **optional (R4)**. So this lesson makes the mandatory conditions **four checks decidable on a
> CPU** and separates the PSNR trend out as the **optional extension (R4)** below. The mandatory
> conditions target the **rendering mathematics** of both methods head on (R2, R3, R4, R5).

**Generators (fixed)**: (a) piecewise constant — 12 intervals, $\sigma_i \sim U(0,3)$,
$c_i \sim U(0,1)$, with boundaries sorted at random in $[0,4]$. (b) Smooth —
$\sigma(t) = 1.5 + 2\sin^2(3t)$, $c(t) = 0.5 + 0.4\cos(2t)$, $t \in [0,4]$. (c) Fourier features —
a uniform grid with $m = 512$, frequencies $1..16$, amplitudes $a_k = k^{-p}$, target
$y = \frac{1}{16}\sum_f \sin 2\pi fx$. (d) Gaussian — $f = 500$, $Z = 5$, semi-axes
$(s, 0.6s, 1.4s)$ rotated by the rotation vector $(0.3,-0.2,0.5)$. Report with a fixed seed.

All **four conditions** must hold to pass. Every reference value was measured for this lesson.

1. **Exactness and order of the discretisation**: with generator (a) the difference between the
   analytic value and (2) is at most $10^{-15}$ (reference: exactly zero) and the accumulated alpha
   matches $\sum_i T_i\alpha_i = 1 - T_{N+1}$ to within $10^{-15}$. With generator (b) the observed
   convergence order over $N = 32 \dots 512$ is $2.0 \pm 0.1$ (reference: 2.03, 2.01, 2.00, 2.00,
   2.00).
2. **Quantitative prediction of the spectral bias**: with generator (c) at $p = 0$ the $t_{1/2}$ of
   all frequencies is **the same** (reference: 2 iterations for all, measured/predicted ratio 1.000),
   and at $p = 1$ the $t_{1/2}(k)$ grows as $k^2$ with a ratio to the prediction (5) within $\pm10\%$
   of $\ln 2$ (reference: median 0.694).
3. **The band limit of the encoding**: fitting the target of generator (c) with an $L$-term encoding
   ($f \le 2^{L-1}$), the residual of a frequency outside the band **does not decrease from its
   initial value** (reference: at $L=4$ the residuals of $f=8,16$ stay at 0.186 and 0.193; with no
   encoding the relative error does not move from 0.9410).
4. **The valid regime of the affine projection**: with generator (d), comparing (4) against the
   covariance of a $4\times10^6$-sample Monte Carlo projection, the relative error is $< 10^{-2}$
   for $s/Z \le 0.01$ and $> 0.5$ at $s/Z = 0.2$ (reference: $10^{-4}$ to $10^{-3}$ against $0.94$
   to $0.99$). Increasing the off-axis distance from 0 to 500 px raises the error at the same
   $s/Z$ (reference at $s/Z=0.01$: $3.8\times10^{-4} \to 2.5\times10^{-3}$), and
   $\Sigma = RSS^\top R^\top$ produces **no** negative eigenvalues over 20,000 random pairs.

**Optional extension (R4, needs a GPU — optional only)**: train NeRF and 3DGS on one NeRF synthetic
(Blender) scene and compare (1) the PSNR under the same time budget and (2) the time to reach a
target PSNR, reproducing the **trend** that 3DGS is faster. When reporting, always state the
resolution, iteration count, hardware, data split and seeds. R4 is **optional** and is not a
condition for passing this lesson.

**State this in the report**: the interpretation of condition 1 — that (2) is **exact** under the
piecewise-constant assumption, and what more samples reduce is only the gap between that assumption
and the real scene. And how condition 4 connects to the clipping and size caps of a 3DGS
implementation.

**Baselines**: (1) the analytic value (condition 1); (2) the analytic prediction (5) (condition 2);
(3) the Monte Carlo projection (condition 4); (4) optionally the rendering function of the NeRF
reference implementation — reading the code is enough.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| the difference in condition 1 is around $10^{-3}$ | $T_i$ includes its own interval's alpha (off by one) | check that $T_1 = 1$ and that $T_i$ multiplies only $j<i$ |
| the accumulated alpha exceeds one | $\sum\alpha_i$ was summed without updating $T_i$ | compare against $1 - \prod(1-\alpha_i)$ |
| the convergence order comes out as 1 | $\sigma, c$ were evaluated at the left end of the interval | switch to the midpoint $\bar t_i$ |
| at $p=0$ the per-frequency $t_{1/2}$ differ | the grid is not uniform, or the frequencies do not fit the grid | check that $\Phi^\top\Phi/m$ is diagonal |
| it diverges because the learning rate is too large | $\eta > 2/\lambda_{\max}$ | set $\eta = 0.5/\lambda_{\max}$ |
| the Monte Carlo of condition 4 is unstable | samples with $Z \le 0$ were projected anyway | filter to $Z > 0$ and report the discarded fraction |
| the error is large even at small $s/Z$ | the third (depth) column of $J$ was omitted | check that $\Sigma'$ shears for an off-axis $\mu$ |

## Open problems

- **(open problem) uncertainty of neural and Gaussian representations** — NeRF and 3DGS output only
  point estimates of density and colour, and cannot express "this region is unobserved, so I do not
  know". A robot using the map needs exactly that (choosing exploration targets, collision margins).
  Current approaches: ensemble or dropout approximations, and the scale-aware representations of the
  [Mip-NeRF 360](https://jonbarron.info/mipnerf360/) line. What is missing: calibrated uncertainty
  usable within a real-time budget.
- **(open problem) differentiable rasterisation without the affine approximation** — the
  measurements of R4 show that the EWA approximation is off by more than a few percent once
  $s/Z \gtrsim 0.05$ and is invalid at $0.2$ — and yet the optimisation naturally drifts into the
  regime that favours large Gaussians (floor, sky). There is no method that keeps the projection
  exact while retaining rasterisation speed. Current approaches: engineering constraints such as
  on-screen size caps and near clipping ([3DGS](https://arxiv.org/abs/2308.04079) §6), and ray-based
  hybrids. What is missing: a rasteriser whose approximation error is bounded.
- **(open problem) a principled balance between band and aliasing** — R3 goes as far as saying that
  the $L$ of the encoding sets the representable frequency ceiling and that the bias vanishes inside
  the band. But raising $L$ makes frequencies absent from the training views appear as artefacts in
  novel views. There is no principle for setting $L$ from the observed resolution of the scene.
  Current approaches: the bandwidth selection of
  [Tancik et al. 2020](https://arxiv.org/abs/2006.10739) and Mip-NeRF's integrated positional
  encoding. What is missing: a rule that derives the band from the observations.
- **(open problem) separating geometry from appearance** — both representations optimise density and
  colour together, so they can converge to a solution that **explains view-dependent appearance
  (specularity, transparency) with geometry** — the so-called floaters. The rendering PSNR is then
  good while the surface and collision geometry are unusable, which is fatal for robotics. Current
  approaches: density regularisation, normal and depth priors. What is missing: identifiability
  conditions that **separate** the component explained by appearance from the geometry. It is the
  same kind of problem as the gauge discussion in `c7-bundle-adjustment`.

## Concept check

Run `rc quiz c7-neural-fields-3dgs`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: what NeRF's alpha-compositing formula is with respect to the volume rendering
integral; whether changing the compositing order changes the colour and the accumulated alpha; the
effect of giving every frequency the same amplitude in the positional encoding; the dimensionless
ratio at which the affine projection starts to fail; and why 3DGS parameterises the covariance as
$\Sigma = RSS^\top R^\top$.

## How to study this stage

1. **From the ODE to the integral, by hand (40 min)** — derive $T' = -\sigma T$ from the
   infinitesimal argument and write (1). Write down, with units, that $\sigma$ is an extinction
   coefficient and not a probability, and that the quantity which *is* a probability is $\alpha_i$
   (P1).
2. **Prove "it is exact" yourself (60 min)** — write $T$ in closed form inside an interval and
   integrate to get (2). Then build a piecewise-constant case in code and see that the difference is
   **exactly zero** (condition 1). That experience removes the "more samples make it exact"
   misconception.
3. **Measure the order (40 min)** — with smooth $\sigma, c$, double $N$ repeatedly, measure the
   error and extract the order from the $\log_2$ ratio (the second half of condition 1). Switch to
   left-end evaluation and watch the order drop to 1.
4. **Measure spectral bias in a linear model (90 min)** — print the Gram eigenvalues of the Fourier
   features and compare the prediction (5) with the measured $t_{1/2}$ (condition 2). Sweep
   $p = 0, 1, 2$ and confirm numerically that equal amplitudes remove the bias.
5. **Check outside the band (40 min)** — reduce $L$ and watch the target's high frequencies **not
   decrease at all** (condition 3). Learn to tell "slow" from "impossible" by eye.
6. **Break the affine approximation (90 min)** — implement (4), compare against a Monte Carlo
   projection and sweep $s/Z$ (condition 4). Plotting the error curve on log-log axes shows where
   design constraints become necessary.
7. **Two papers and the notes (130 min)** — read NeRF §4 first against (2), then find the covariance
   parameterisation and the sorting treatment in 3DGS §4–6. Write the one-page note per paper
   **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the open problems and write a paragraph on
   why it is still open. Uncertainty for neural representations is a question robotics needs now.

**Passing bar**: you can derive (1) and (2) on a blank page, you have shown both by proof and
numerically that (2) is exact for piecewise-constant density, you have predicted and matched the
per-frequency convergence time with (5), you can state the valid regime of the affine approximation
in terms of $s/Z$, you have code that passes all four conditions of the reproduction task, and you
have notes on both papers.
