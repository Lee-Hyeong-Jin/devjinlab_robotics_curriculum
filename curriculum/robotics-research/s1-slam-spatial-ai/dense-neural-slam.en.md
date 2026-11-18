---
id: s1-dense-neural-slam
lang: en
title: Dense and neural SLAM
summary: >-
  Derive that the recursive weighted average of TSDF fusion is **exactly** the batch weighted
  average under independent Gaussian depth noise, and confirm it to machine precision. Derive that
  the ray-wise distance overstates the true signed distance by $1/\cos\theta$, and then correct a
  common misconception by measuring that **the zero crossing (the surface) does not move**. For
  neural implicit maps, shows that **parameter locality alone does not prevent forgetting**, and
  identifies numerically what does (replay, or a prior).
objectives:
  - Derive the recursive weighted average of a TSDF and confirm it matches the batch weighted average and its posterior variance.
  - Derive that the ray-wise signed distance overstates the true one by $1/\cos\theta$ and quantify the consequence.
  - Separate by measurement what truncation and angular weighting do, and do not do, to the fused field.
  - Formulate the forgetting of incremental learning as a sequential fit without replay and measure its size.
  - Separate numerically the roles of parameter locality, replay and a prior in forgetting.
tags: [slam, tsdf, dense-mapping, neural-fields, catastrophic-forgetting, research]
---

# Dense and neural SLAM

## Setup and notation

The recommended prerequisites are `s1-loop-closure-lifelong` in this module (information matrices
and marginalisation), `c7-neural-fields-3dgs` (volume rendering and the spectral bias of positional
encoding) and `r0-estimation-theory` (weighted least squares and posterior variance). None of them
is locked. The lesson assumes:

- Estimation: products of Gaussians, weighted averages, precision weighting, posterior variance.
- Geometry: signed distance fields, point-to-plane distance, incidence angle.
- Learning: the least-squares and ridge solutions of a linear feature model, Gram matrices. No
  network architecture is needed — forgetting is quantified in a **linear feature model**.

Notation:

| Symbol | Meaning |
|---|---|
| $d_i$ | the signed distance reported by observation $i$, with standard deviation $\sigma_i$ and weight $w_i = 1/\sigma_i^2$ |
| $D, W$ | the fused distance and accumulated weight stored in a voxel |
| $\mu$ | the truncation distance |
| $\theta$ | the angle between the ray and the surface normal (incidence angle) |
| $s_\perp$, $s_\parallel$ | the true point-to-surface distance and the **ray-wise** distance |
| $\Phi$ | the feature matrix with coefficients $w$; $G = \Phi^\top\Phi/m$ |
| $A, B$ | the region seen first and the region seen later (disjoint) |
| $\mathrm{err}_A\vert_B$ | the error measured on $A$ after fitting on $B$ alone |

**Conventions**: distances are in metres and angles in degrees. "Forgetting" is reported as the
ratio $\mathrm{err}_A\vert_B / \mathrm{err}_A\vert_A$, alongside the **RMS of the signal itself**
(0.7896 for this lesson's generator) as the reference — once the error reaches that value,
**no** information is left.

## Key results

The bracket is the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (TSDF fusion is a precision-weighted average) [D2]** — if the observations are independent
  with $d_i \sim \mathcal{N}(s, \sigma_i^2)$, the maximum-likelihood estimate is the
  precision-weighted average, computed exactly by the recursion
  $$D \leftarrow \frac{W\,D + w_i\,d_i}{W + w_i}, \qquad W \leftarrow W + w_i \tag{1}$$
  so KinectFusion's one-line update is **exact sequential estimation, not an approximation**. The
  posterior standard deviation is $1/\sqrt{W}$.
- **R2 (the $1/\cos\theta$ overstatement of the ray-wise distance) [D2]** — a depth camera measures
  along the ray, so the value written into a voxel is not the true point-to-surface distance:
  $$s_\parallel = \frac{s_\perp}{\cos\theta}
    \;\Longrightarrow\; \frac{s_\parallel}{s_\perp} = \frac{1}{\cos\theta}. \tag{2}$$
  That is a factor of 2 at $\theta = 60^\circ$ and 11.5 at $85^\circ$.
- **R3 (and yet the surface does not move) [D2]** — the error of (2) is an **odd function** of the
  signed distance ($s_\perp \mapsto s_\perp/\cos\theta$), so it **does not shift the zero
  crossing**. Fusing several views with mixed incidence angles, with truncation and noise included,
  leaves the measured bias in surface position at about one fiftieth of the noise standard
  deviation. What does break is **the gradient of the field (normals and scale) and the truncation
  band**.
- **R4 (forgetting in incremental learning) [D2]** — after seeing region $A$, refitting on region
  $B$ alone **without replay** raises the error on $A$ to the RMS of the signal itself — **all** the
  information is gone. Measured: forgetting factors of $370\times$ to $2.3\times10^{5}$, with
  $\mathrm{err}_A\vert_B$ of $0.72$ to $0.82$ against a signal RMS of $0.7896$.
- **R5 (locality does not prevent forgetting) [D2]** — forgetting happens even in representations
  whose parameters are spatially local (narrow RBFs, voxel grids). The reason is that **$B$'s
  objective has no term at all for $A$'s parameters** — their values are decided by the
  regulariser rather than by data, and in the measurements 94–100% of the parameters change. What
  prevents forgetting is not locality but **replay** or **a prior anchored at $w_A$**.

## Derivation

### R1 — why the one-line update is exact

Suppose $n$ observations of one voxel have arrived. Each gives, independently,
$d_i = s + \epsilon_i$ with $\epsilon_i \sim \mathcal{N}(0, \sigma_i^2)$ about the voxel's true
signed distance $s$. The likelihood is

$$p(d_1,\dots,d_n \mid s) \propto \exp\!\Big(-\tfrac12\sum_i w_i (d_i - s)^2\Big),
  \qquad w_i = \frac{1}{\sigma_i^2}$$

and differentiating in $s$ and setting it to zero gives

$$\hat{s} = \frac{\sum_i w_i d_i}{\sum_i w_i}, \qquad
  \operatorname{Var}(\hat{s}) = \frac{1}{\sum_i w_i} \tag{3}$$

— a precision-weighted average. Computing it in one shot would require storing every $d_i$, but
keeping just the two numbers $(D, W)$ per voxel and updating with (1) gives **the same value**:

$$\frac{W D + w_n d_n}{W + w_n}
  = \frac{\sum_{i<n} w_i d_i + w_n d_n}{\sum_{i<n} w_i + w_n}
  = \frac{\sum_{i\le n} w_i d_i}{\sum_{i\le n} w_i}.$$

One line of induction. So **the streaming update and the batch estimate are identical** and storage
is $O(1)$. This is Curless and Levoy's weighted average, and the formula KinectFusion runs on the
GPU unchanged.

Measured (random $d_i$ with $\sigma_i \in [0.01, 0.1]$):

| $n$ | recursive (1) | batch (3) | difference | posterior sd | $1/\sqrt{\sum w}$ |
|---|---|---|---|---|---|
| 3 | 0.128710002091406 | 0.128710002091406 | $0$ | 0.011294 | 0.011294 |
| 10 | $-0.500281401756240$ | $-0.500281401756240$ | $0$ | 0.009400 | 0.009400 |
| 100 | 0.286944269229488 | 0.286944269229488 | $3.3\times10^{-16}$ | 0.003249 | 0.003249 |

Monte Carlo ($n = 20$, $\sigma = 0.05$, 200,000 runs): the variance of the fused estimate is
$1.2508\times10^{-4}$ against a prediction of $1/\sum w = 1.25\times10^{-4}$, a ratio of 1.0007.
The variance expression of (3) checks out too.

**Where the assumptions break**: (1) **independence**. Neighbouring voxels in one frame share the
same depth measurement, and repeated observations from the same viewpoint share systematic error
(calibration, depth bias) — then the variance of (3) is optimistic and $W$ grows faster than the
real information. (2) **A static scene.** For a voxel on a moving object $s$ is not constant, so the
average places a "ghost" between the two surfaces. The practical remedy is to cap $W$, turning (1)
into an **exponential moving average** ($W \leftarrow \min(W + w_i, W_{\max})$) — it keeps weight on
recent observations so the map can track change, but it gives up the ML interpretation of (3) at
that moment. (3) Depth noise is not Gaussian and depends on range ($\sigma \propto z^2$ is the usual
model for stereo and ToF). Treating $w_i$ as constant overvalues distant observations.

### R2 and R3 — what the ray-wise distance gets wrong, and what it does not

A depth camera gives distance **along the ray**. The standard implementation computes a voxel's
signed distance as "the depth measurement $z$ minus the voxel's ray-wise depth $z_v$", which is not
the true point-to-surface distance. If the surface is inclined at an angle $\theta$ to the ray, then
trigonometry gives (2).

Measured:

| incidence $\theta$ | $0^\circ$ | $15^\circ$ | $30^\circ$ | $45^\circ$ | $60^\circ$ | $75^\circ$ | $85^\circ$ |
|---|---|---|---|---|---|---|---|
| $s_\parallel/s_\perp$ | 1.0000 | 1.0353 | 1.1547 | 1.4142 | 2.0000 | 3.8637 | 11.4737 |
| $1/\cos\theta$ | 1.0000 | 1.0353 | 1.1547 | 1.4142 | 2.0000 | 3.8637 | 11.4737 |

Exactly $1/\cos\theta$ (as it must be — the derivation is trigonometry). From this one often hears
that "TSDF pushes the surface away at grazing incidence". **That is wrong.** The error of (2) is
**proportional** to $s_\perp$, so it is an **odd function** of the signed distance and vanishes at
the zero crossing ($s_\perp = 0$). Averaging several views with positive weights leaves every term
zero at the crossing, so **the sum keeps the crossing where it was**.

Measured (a one-dimensional probe, fusing mixed incidence angles with the angular weight
$\cos\theta$, depth noise $\sigma = 10$ mm, truncation $\mu = 40$ mm, averaged over 4,000 runs):

| incidence angles | no truncation | with truncation | sd of the zero crossing |
|---|---|---|---|
| $[0,0,0]$ | $+0.119$ mm | $+0.067$ mm | 5.69 mm |
| $[0,45,60]$ | $+0.163$ mm | $+0.007$ mm | 5.74 mm |
| $[60,70,80]$ | $+0.083$ mm | $-0.092$ mm | 5.95 mm |
| $[80,82,85]$ | $+0.049$ mm | $-0.003$ mm | 6.34 mm |

**In every case the bias in surface position is below one fiftieth of the noise standard
deviation** ($\le 0.17$ mm against 5.7–6.3 mm). In this setting, grazing incidence and truncation do
**not** measurably push the surface.

So what does (2) break? Three things.
(1) **The scale and gradient of the field**: $\lvert\nabla D\rvert = 1/\cos\theta$, so the fused
field **is not a distance field**. Taking normals from $\nabla D$ keeps the direction but gets the
magnitude normalisation wrong, and distance-based weighting, collision margins and the linear
interpolation of marching cubes all assume that scale.
(2) **Asymmetry of the truncation band**: the ray-wise value is clipped at $\mu$, so the band of
true distances that actually gets updated is $\lvert s_\perp\rvert \le \mu\cos\theta$, **narrowed by
$\cos\theta$**. At $85^\circ$ the band shrinks by a factor of 11.5, so only voxels right at the
surface are updated and beyond that there is no information.
(3) **Noise amplification**: depth noise $\sigma_z$ enters the true-distance direction as
$\sigma_z\cos\theta$ while the variance of the stored value is $\sigma_z^2$, which justifies the
standard remedy of **shaving the weight by $\cos\theta$** at grazing incidence (KinectFusion's
angular weighting).

**Where the assumptions break**: the measurements above use a **plane** and a **one-dimensional
probe**. On a surface with high curvature, or at an edge, the ray crosses the surface twice or
grazes it, so (2) itself fails — and there the zero crossing does move. The rounding of corners in a
TSDF is exactly that, and it is worst when the truncation $\mu$ exceeds the radius of curvature.

### R4 and R5 — incremental learning and forgetting

Neural SLAM (the iMAP line) makes the map **a single network**. The advantage is memory
$O(\text{parameters})$ and interpolation into unobserved regions; the price is **incremental
learning**. When the robot passes region $A$ and moves into region $B$, the parameters are updated
to lower $B$'s loss, and the question is what happens to $A$.

Measure that exactly in a **linear feature model** — the most favourable possible setting, with the
nonlinearity of a network removed. Split the target
$y(x) = \sin(2\pi\cdot3x) + 0.5\sin(2\pi\cdot11x)$ ($x\in[0,1]$, RMS $0.7896$) into
$A = \{x<0.5\}$ and $B = \{x\ge0.5\}$, fit ridge on $A$ first and then, **without replay**, refit
ridge on $B$ alone ($\lambda = 10^{-6}$).

Measured:

| Features | dim | $\mathrm{err}_A\vert_A$ | $\mathrm{err}_A\vert_B$ | forgetting | $\mathrm{err}_B\vert_B$ | parameters changed by >1% |
|---|---|---|---|---|---|---|
| Fourier $K{=}8$ (global) | 17 | 0.0963 | 815.23 | $8.5\times10^{3}$x | 0.0963 | 47.1% |
| Fourier $K{=}16$ (global) | 33 | 0.0000 | 0.7154 | $2.3\times10^{5}$x | 0.0000 | 24.2% |
| RBF 32, $s{=}0.05$ (local) | 32 | 0.0087 | 7.359 | $851$x | 0.0087 | 100.0% |
| RBF 64, $s{=}0.02$ (local) | 64 | 0.0020 | 0.7394 | $369$x | 0.0020 | 93.8% |
| RBF 128, $s{=}0.01$ (local) | 128 | 0.0008 | 0.7702 | $960$x | 0.0008 | 93.8% |

How to read it. (1) The rows with $\mathrm{err}_A\vert_B$ around $0.72$ to $0.77$ are **the same
size as the signal's own RMS, $0.7896$** — the model holds no information about $A$ at all. The 815
of global Fourier $K{=}8$ is worse still (extrapolation blow-up). (2) **Local features forget too.**
Narrow RBFs (width 0.01) have a Gram overlap between $A$ and $B$ of 0.0081, nearly orthogonal, and
yet 93.8% of the parameters changed. (3) The reason is not the overlap — since **$B$'s objective has
no data term for $A$-only parameters**, their values are decided by the ridge regulariser, which
pulls them to zero. **A parameter that the data does not speak about is erased by the regulariser.**

**What prevents forgetting.** Adding **replay** to the same features (fitting $A$ and $B$ jointly):

| Features | $\mathrm{err}_A$ | $\mathrm{err}_B$ |
|---|---|---|
| Fourier $K{=}16$ (global) | 0.0000 | 0.0000 |
| RBF 128, $s{=}0.01$ (local) | 0.0008 | 0.0008 |

restores it to the fitting floor. So there are only two remedies: (a) **replay**, keeping past
keyframes in the loss (which is exactly what iMAP's keyframe selection is, and why the claim of
$O(\text{parameters})$ memory does not count the keyframe storage); or (b) **a prior**, adding a
term $\lambda_A\lVert w - w_A\rVert^2$ that anchors $A$'s parameters (the elastic-weight family).
Both are the same principle — "keep the past information somewhere" — and **there is no free
incremental learning**.

**Where the assumptions break**: (1) the linear model is **more favourable** than a network — a
closed-form global optimum with no local minima. Forgetting is total even so, which leaves no reason
to expect better from an MLP. (2) Conversely, in the **overparameterised** regime (parameters far
exceeding data) the fit on $B$ can select a solution near $w_A$, so implicit regularisation reduces
forgetting — one reason real neural SLAM does not forget completely, but the extent depends on the
initialisation and the optimisation path and **carries no guarantee**. (3) In this framework a voxel
grid is "fully local features with a data term only in the observed voxels", so it has
**structurally** no forgetting — at the cost of $O(\text{volume})$ memory. That is the real trade-off
between dense and neural SLAM.

## Proof sketch

### R1 — exactness of the recursive update and the posterior variance

**Hypotheses** H1: $d_i = s + \epsilon_i$ with $\epsilon_i \sim \mathcal{N}(0,\sigma_i^2)$
independent. H2: $w_i = 1/\sigma_i^2$ and $W_n = \sum_{i\le n} w_i$. H3: no prior (or an
uninformative one).
**Conclusions** C1: the ML estimate is (3). C2: the recursion (1) equals (3) at every $n$.
C3: $\operatorname{Var}(\hat{s}_n) = 1/W_n$, so information is **the sum of the weights**.

**Strategy**: the quadratic form of a Gaussian likelihood, completing the square, then induction.

1. **C1**: differentiating the log-likelihood $-\tfrac12\sum_i w_i(d_i-s)^2$ in $s$ gives
   $\sum_i w_i(d_i - s) = 0$, that is, (3). The second derivative is $-\sum w_i < 0$, so it is a
   maximum. $\square$
2. **C2**: at $n=1$, $D_1 = d_1$. Assuming $D_{n-1} = \sum_{i<n}w_id_i/W_{n-1}$,
   $$D_n = \frac{W_{n-1}D_{n-1} + w_nd_n}{W_{n-1}+w_n}
   = \frac{\sum_{i<n}w_id_i + w_nd_n}{W_n} = \frac{\sum_{i\le n}w_id_i}{W_n}.\;\square$$
3. **C3**: $\hat{s}$ is a linear combination of independent Gaussians, so
   $\operatorname{Var} = \sum_i (w_i/W)^2\sigma_i^2 = \sum_i w_i/W^2 = 1/W$. The measured ratio of
   1.0007 is this. $\square$
4. **Why this matters**: the memory claim of dense SLAM ("two numbers per voxel") rests on the fact
   that **nothing is given up in accuracy**. It is the same structure as the accumulation of
   information in `c7-bundle-adjustment` — under a Gaussian assumption information adds, and all
   that has to be stored is a sufficient statistic.
5. **Remove a hypothesis**: dropping the independence of H1 makes $W$ overstate the information
   (correlated observations). Adding a prior to H3 only means initialising $(D_0, W_0)$, with the
   formula unchanged — which is why an implementation may start $W$ at a small value rather than
   zero. Capping $W$ at $W_{\max}$ breaks C2 and the estimator becomes an exponential moving average
   rather than the ML one — a **deliberate** sacrifice of exactness for dynamic scenes.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★, R1)** Derive (3) and (1) and show $\operatorname{Var}(\hat s) = 1/W$. Then say
what weight the estimator gives to past observations once $W$ is capped at $W_{\max}$ (the decay rate
of the exponential moving average).
*Solution sketch*: completing the square and induction. With the cap, each update becomes
$D \leftarrow (1-\alpha)D + \alpha d$ with $\alpha = w/(W_{\max}+w)$, so the weight of an
observation $k$ steps back decays geometrically as $(1-\alpha)^k$.

**P2 (proof, ★★★, R3)** Show that the error of (2) is an odd function of the signed distance, and
**therefore** that averaging any set of incidence angles with any positive weights preserves the zero
crossing. Then state **exactly** the conditions under which that preservation fails (which of
truncation, curvature and asymmetric weighting breaks it, and how).
*Strategy and key inequality*: $f_i(s) = s/\cos\theta_i$ is odd, and $\sum_i \lambda_i f_i(s)$ with
$\lambda_i > 0$ is odd **and monotone**, so its zero is unique at $s=0$. What breaks it is (a) the
clip $\mathrm{clip}(\cdot,\pm\mu)$, which stays odd but **loses monotonicity in the saturated
region** (so an asymmetric weighting moves the zero), (b) a curved surface, where $f_i$ is not odd,
and (c) noise interacting with saturation so that the expectation becomes asymmetric.

**P3 (numerical, ★, R2·R3)** For incidence angles $\theta = 30^\circ, 60^\circ, 80^\circ$ compute
(a) $s_\parallel/s_\perp$, (b) the band of true distances actually updated under truncation
$\mu = 0.04$ m, namely $\lvert s_\perp\rvert \le \mu\cos\theta$, and (c) the relative weight under
the angular weighting $\cos\theta$.
*Answer*: (a) $1.1547, 2.0000, 5.7588$; (b) $0.03464, 0.02000, 0.00695$ m; (c)
$0.866, 0.500, 0.174$. Tolerance $10^{-4}$. Check: (b) divided by $\mu$ must equal $\cos\theta$.

**P4 (derivation, ★★, R4·R5)** Write the solution of "ridge fit on $B$ alone" in a linear feature
model and show what value the $A$-only parameters (those whose columns of $\Phi_B$ are zero) take.
Then explain why $\mathrm{err}_A\vert_B$ converges to the **RMS of the signal**.
*Solution sketch*: in $w_B = (\Phi_B^\top\Phi_B + \lambda I)^{-1}\Phi_B^\top y_B$, a coordinate whose
column of $\Phi_B$ is zero has a zero numerator and only $\lambda$ in the denominator, so it is
**exactly zero**. Once the prediction on $A$ approaches zero, the error tends to
$\sqrt{\mathbb{E}[y^2]}$, the signal RMS.

**P5 (numerical, ★★, R4·R5)** With this lesson's generator, measure (a) the forgetting factor for
all five feature sets, (b) the ratio of $\mathrm{err}_A\vert_B$ to the signal RMS, (c) the fraction
of parameters that changed by more than 1%, and (d) $\mathrm{err}_A$ once replay is added.
*Answer (reference measurements)*: (a) $369\times$ to $2.3\times10^5\times$; (b) between $0.9$ and
$1.0$ for global Fourier $K{=}16$ and every RBF (that is, no information left), while Fourier
$K{=}8$ gives 1032 (extrapolation blow-up); (c) 24.2% to 100%; (d) 0.0000 for Fourier $K{=}16$ and
0.0008 for RBF 128. Tolerance: ratio (b) within $\pm0.2$, the rest to the right order of magnitude.
Check: compute the signal RMS directly and confirm it is 0.7896.

**P6 (implementation, ★★★, R1·R2·R3)** Implement 3D TSDF fusion and (a) confirm that (1) matches
(3), then (b) fuse a plane from several incidence angles, extract the surface with marching cubes and
measure the distance to the true plane.
*Rubric*: (a) the difference is at most $10^{-14}$; (b) the mean surface error is at most a tenth of
the depth noise standard deviation; (c) you measure $\lvert\nabla D\rvert$ and compare with
$1/\cos\theta$; (d) you show numerically that the truncation band narrows as $\mu\cos\theta$; (e) you
report the result both with and without angular weighting.

**P7 (counterexample, ★★, R3·R5)** (a) Construct a configuration where the preservation of the zero
crossing in (2) **fails** (an edge or high curvature with a large $\mu$) and measure a surface bias
exceeding the noise standard deviation. (b) Show that local features forget too, then add a prior
term $\lambda_A\lVert w - w_A\rVert^2$ and measure the mitigation as $\lambda_A$ is swept.
*Property checklist*: (a) an edge with a radius of curvature below $\mu$; (b) a surface bias larger
than $\sigma$; (c) a forgetting factor above 100 even for local RBFs; (d) raising $\lambda_A$ lowers
$\mathrm{err}_A$ and raises $\mathrm{err}_B$, showing the trade-off; (e) a paragraph on "there is no
free incremental learning".

**P8 (paper, ★★, R1·R4)** Read §3 of Newcombe et al. 2011 and §3–4 of Sucar et al. 2021, and
(a) tabulate the map representation, memory and update rule of each; (b) find how iMAP handles
forgetting and decide which of R5's two remedies it is; and (c) say whether either paper's memory
comparison leaves something **uncounted**.
*Rubric*: for (b), identifying keyframe replay passes. For (c), pointing out that the neural side
does not count keyframe storage as memory is excellent — that hidden cost is exactly what R5 exposes.

## Paper reading

**Two must-reads.** Write a one-page note on each, using the ten fixed questions
(`lesson-standard.md` §5). Read in three passes, and attack questions 4, 5, 6 and 7 in the third.
For the full bibliography, including the recommended papers, run `rc papers s1-dense-neural-slam`.

1. **Newcombe, Izadi, Hilliges et al., "KinectFusion: real-time dense surface mapping and tracking"
   (2011, ISMAR)** — role: `seminal`. <https://doi.org/10.1109/ISMAR.2011.6092378>
   (§3 is the core.)
   Extra questions: (a) rewrite the paper's fusion equation in the form of (1) and find what it uses
   for the weight $w$. (b) How is the truncation $\mu$ chosen — is there any argument tying it to the
   depth noise? (c) Does the frame-to-model ICP inherit the $1/\cos\theta$ distortion of (2)?
2. **Sucar, Liu, Ortiz & Davison, "iMAP: implicit mapping and positioning in real-time"
   (2021, ICCV)** — role: `frontier`. <https://arxiv.org/abs/2103.12352> (§3–4 is the core.)
   Extra questions: (a) is the keyframe selection R5's "replay" or its "prior"? What is the selection
   criterion? (b) Does the reported memory include the keyframe buffer? (c) Is the interpolation into
   unobserved regions **guaranteed**, or merely made plausible by a prior?

**The ten fixed questions**: (1) which problem under which assumptions; (2) what exactly earlier
work could not do; (3) the core idea in one equation; (4) what is guaranteed and **what is not**;
(5) the independent and dependent variables and the baselines, fairly tuned or not; (6) whether the
metric matches the claim, and whether variance and seeds are reported; (7) what is missing for
reproduction; (8) the first assumption to doubt if the result were wrong; (9) time and memory
complexity and real-time behaviour; (10) what you would change to go beyond it in a year.

**Recommended**: Curless & Levoy 1996 §2–3 (the origin of the weighted average and of truncation),
NeRF §4 (the volume-rendering counterpoint).

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 10 minutes in total, numpy and
scipy only. The input is a generator this lesson specifies; no external data and no GPU are needed.

> **Stated difference from the blueprint**: the reproduction task in the design is "compare the
> memory and accuracy of a TSDF reconstruction and a neural SLAM on a small RGB-D sequence" (R3).
> Training a neural SLAM needs a GPU, so following §6 of the lesson standard the mandatory conditions
> are **four checks decidable on a CPU** and the RGB-D comparison is separated out as the **optional
> extension (R3)** below. The mandatory conditions target the mathematical difference between the two
> representations (R1, R3, R4, R5) head on — in particular they expose forgetting as the source of
> the "memory-accuracy trade-off".

**Generators (fixed)**: (a) fusion — $d_i$ from a standard normal, $\sigma_i \sim U(0.01, 0.1)$,
$n \in \{3,10,100\}$; the Monte Carlo uses $n = 20$, $\sigma = 0.05$ and $2\times10^5$ runs.
(b) The ray-wise distance — a plane at incidence angles $\{0,15,30,45,60,75,85\}^\circ$, truncation
$\mu = 0.04$ m, depth noise $\sigma = 0.01$ m, a one-dimensional probe over
$x \in [-0.05, 0.05]$, angular weighting $\cos\theta$, 4,000 runs. (c) Forgetting —
$y = \sin(2\pi\cdot3x) + 0.5\sin(2\pi\cdot11x)$, $m = 400$, $A = \{x<0.5\}$, ridge
$\lambda = 10^{-6}$, with features Fourier $K \in \{8,16\}$ and RBF $(32, 0.05), (64, 0.02),
(128, 0.01)$. Report with a fixed seed.

All **four conditions** must hold to pass. Every reference value was measured for this lesson.

1. **The fusion identity**: with generator (a), the recursion (1) and the batch weighted average (3)
   differ by at most $10^{-14}$ (reference: $0$ and $3.3\times10^{-16}$), the posterior standard
   deviation matches $1/\sqrt{\sum w}$ to within $10^{-12}$, and the Monte Carlo variance matches
   $1/\sum w$ to within **1%** (reference ratio 1.0007).
2. **The $1/\cos\theta$ of the ray-wise distance**: with generator (b), $s_\parallel/s_\perp$ matches
   $1/\cos\theta$ to within $10^{-12}$ (reference: 11.4737 at $85^\circ$), and you show numerically
   that the updated band of true distances is $\mu\cos\theta$.
3. **The surface does not move**: for all four incidence-angle combinations of generator (b), the
   absolute bias of the fused field's zero crossing is at most **one twentieth** of the standard
   deviation of that crossing (reference: $\le 0.17$ mm against 5.7–6.3 mm). State in the report that
   **"grazing incidence does not push the surface — what breaks is the gradient and the truncation
   band"**.
4. **Forgetting and its remedies**: with generator (c), (a) **all five** feature sets have a
   forgetting factor above **100**; (b) even the local RBFs have **over 90%** of parameters changed
   by more than 1%; (c) $\mathrm{err}_A\vert_B$ is $0.8$ to $1.2$ times the signal RMS ($0.7896$),
   with the extrapolating Fourier $K{=}8$ reported as the exception; and (d) adding replay (a joint
   fit) restores $\mathrm{err}_A$ to the fitting floor (reference: forgetting
   $369\times$ to $2.3\times10^5\times$, 93.8–100% of parameters changed, and 0.0000 / 0.0008 after
   replay).

**Optional extension (R3, public data; GPU optional)**: on a short TUM RGB-D sequence such as
`freiburg1_xyz`, (a) reconstruct with Open3D's TSDF and measure the memory (number of voxels times 8
bytes) and the surface accuracy, and (b) if possible run a neural SLAM (the NICE-SLAM line) on the
same sequence and measure the same two quantities for comparison. When reporting, **include the
keyframe buffer in the neural side's memory** and give the numbers both with and without it — that is
where the hidden cost R5 exposes becomes visible.

**Baselines**: (1) the batch weighted average (condition 1); (2) the analytic $1/\cos\theta$
(condition 2); (3) the joint fit with replay (condition 4); (4) optionally Open3D's
`ScalableTSDFVolume`.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| the recursion and the batch differ at the $10^{-3}$ level | the weight was taken as $1/\sigma$ instead of $1/\sigma^2$ | check that the posterior sd matches $1/\sqrt{\sum w}$ |
| the Monte Carlo variance is twice the prediction | the same noise samples were reused (correlation) | confirm independence across samples |
| the zero crossing moves a lot | the angular weight was multiplied into the signed distance instead of the weight | print the weight and the value separately |
| the truncation band stays at $\mu$ for every angle | the clip was applied to the true distance instead of the ray-wise value | print, per angle, the $s_\perp$ at which saturation starts |
| the forgetting factor is near 1 | the fit on $B$ included data from $A$ | print the sample indices used in the fit |
| fewer than 10% of parameters changed for local RBFs | the ridge $\lambda$ was zero, so undetermined coordinates were left untouched | set $\lambda > 0$ and look again |
| $\mathrm{err}_A\vert_B$ is far above the signal RMS | extrapolation of global features — this is normal | compare with the 815 that Fourier $K{=}8$ produces |

## Open problems

- **(open problem) incremental learning with a guarantee** — R5 shows forgetting is total without
  replay or a prior. And yet there is no bound on **how much** the implicit regularisation of an
  overparameterised network reduces it. Current approaches: the keyframe replay of
  [iMAP](https://arxiv.org/abs/2103.12352) and the priors of the elastic-weight family. What is
  missing: a relation between the replay budget (the number of keyframes) and a bound on forgetting.
- **(open problem) the geometric interpretation of a field that is not a distance field** — R3 shows
  that a fused TSDF **is not a distance field**, because $\lvert\nabla D\rvert = 1/\cos\theta$. Yet
  downstream modules (collision margins, normals, marching-cubes interpolation) assume one. Methods
  that renormalise (an eikonal regulariser) exist, but none with a guarantee when combined with
  real-time fusion. Current approaches: neural SDFs with an eikonal loss, and the angular weighting
  of [KinectFusion](https://doi.org/10.1109/ISMAR.2011.6092378). What is missing: a distance-field
  correction compatible with streaming fusion.
- **(open problem) a quantitative model of the memory-accuracy trade-off** — voxels cost
  $O(\text{volume})$ memory and do not forget; neural maps cost $O(\text{parameters})$ and do forget
  (and the replay buffer is a hidden cost). There is no model that **predicts** which wins given the
  statistics of a scene. Current approaches: empirical comparison on particular datasets, and hybrid
  hash-voxel or grid-MLP designs. What is missing: a rule deriving the number of parameters needed
  from the scene's frequency content and the distribution of observations (continuing the bandwidth
  problem of `c7-neural-fields-3dgs` R3).
- **(open problem) a fusion rule for dynamic scenes** — the ML interpretation of (1) rests on a
  static scene. The practical remedy of an exponential moving average through $W_{\max}$ tracks
  change but abandons the estimator's statistical meaning. Current approaches: weight caps, and
  dynamic-voxel detection with resets. What is missing: a formulation that treats change detection
  and optimal fusion as one estimation problem.

## Concept check

Run `rc quiz s1-dense-neural-slam`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: what the one-line TSDF update is with respect to the batch estimate; the factor
by which the ray-wise signed distance overstates the true one; whether grazing incidence pushes the
surface; whether spatially local parameters avoid forgetting; and what is commonly left out of the
memory comparison for neural SLAM.

## How to study this stage

1. **Derive the weighted average (40 min)** — derive (3) from the likelihood and confirm by induction
   that (1) equals it. Then write down what breaks once $W_{\max}$ is introduced (P1). The section is
   short, and being short it has to be exact.
2. **Confirm the identity numerically (30 min)** — compare (1) and (3) on random data to the
   $10^{-16}$ level and confirm the variance expression by Monte Carlo (condition 1).
3. **The ray-wise distance by trigonometry (30 min)** — derive (2) from a diagram and tabulate the
   ratio per angle (condition 2). Compute alongside it how the truncation band narrows as
   $\mu\cos\theta$ (P3).
4. **Doubt "the surface gets pushed" (60 min)** — measure the zero crossing with a one-dimensional
   probe and confirm it does **not** move (condition 3). Then use P2 to state exactly when the
   preservation fails. Correcting received wisdom by measurement is the centre of this lesson.
5. **Measure forgetting in a linear model (90 min)** — do the sequential $A \to B$ ridge fit and
   measure the forgetting factor and the fraction of parameters changed (condition 4). See that local
   features forget too, and write the reason as an equation with P4.
6. **Try both remedies (60 min)** — add replay (a joint fit) and a prior (the $\lambda_A$ term) and
   measure the trade-off between $\mathrm{err}_A$ and $\mathrm{err}_B$ (P7(b)). "There is no free
   incremental learning" becomes visible in numbers.
7. **Two papers and the notes (130 min)** — read KinectFusion §3 against (1), and find the keyframe
   strategy and the memory reporting in iMAP §3–4. Write the one-page note per paper **without
   exception**.
8. **End at what cannot be done (30 min)** — pick one of the open problems and write a paragraph on
   why it is still open. The relation between replay budget and a bound on forgetting is one you can
   start experimenting on immediately.

**Passing bar**: you can write the equivalence of (3) and (1) by induction, you can derive
$1/\cos\theta$ and explain through oddness why it does **not** push the surface, you can write with
the ridge solution why local features forget too, you have code that passes all four conditions of
the reproduction task, and you have notes on both papers.
