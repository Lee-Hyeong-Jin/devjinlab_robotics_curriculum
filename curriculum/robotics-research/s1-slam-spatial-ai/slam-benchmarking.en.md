---
id: s1-slam-benchmarking
lang: en
title: The science of evaluation — SLAM benchmarking
summary: >-
  Work out to the end what the single line "ATE 0.03 m" in the table of a SLAM paper depends on.
  Prove the closed-form solution of trajectory alignment (Umeyama) including the reflection
  correction, and show numerically that the alignment must match the gauge freedom of the
  estimator — aligning the scale makes a 5% scale error vanish from 0.173 m to 0.029 m, and
  aligning the full rotation makes a gravity-direction error vanish entirely. Derive and measure
  that ATE grows with trajectory length while RPE does not, and compute through power that, under
  the run-to-run variation of one system (CV 23%) and the variation across sequences, claiming a
  difference requires a paired analysis and enough sequences.
objectives:
  - Prove the closed-form solution of similarity alignment including the reflection correction.
  - Define ATE and RPE and explain why the alignment must match the unobservable degrees of freedom of the estimator.
  - Derive how much error alignment absorbs for a drifting trajectory and that ATE grows with length.
  - Derive and measure the error a timestamp offset adds to ATE.
  - Test the difference between two systems by a paired analysis under run-to-run and sequence-to-sequence variation, and compute the number of sequences required.
tags: [slam, evaluation, ate, rpe, umeyama, benchmarking, research]
---

# The science of evaluation — SLAM benchmarking

## Setup and notation

The earlier lessons of S1 covered how to **build** SLAM systems. This lesson is about how to
**measure** them. We use the unobservable degrees of freedom (the gauge) of
`c5-observability-consistency` and the four-dimensional null space of VIO from `s1-vio-systems` as
they stand. The statistical part is easy with `r1-robotics-evaluation-statistics`. The recommended
prerequisites are `s1-loop-closure-lifelong` and `c5-observability-consistency`.

| Symbol | Meaning |
|---|---|
| $p_i \in \mathbb{R}^3$, $R_i \in SO(3)$ | **Reference** (ground truth) position and orientation at time $t_i$ |
| $\hat{p}_i$, $\hat{R}_i$ | **Estimated** position and orientation at the same time. The world frame of the estimate differs from that of the reference |
| $(s, R, t)$ | Alignment transform. $\hat{p} \mapsto sR\hat{p} + t$. Fixing $s = 1$ gives $SE(3)$ alignment |
| $\mu_x$, $\sigma_x^2$ | Mean of a point set and $\frac1n\sum\lVert x_i - \mu_x\rVert^2$ |
| $C$ | Cross-covariance $\frac1n\sum(y_i - \mu_y)(x_i - \mu_x)^\top$ |
| ATE | RMSE of the position error after alignment (m). Measures global consistency |
| $\mathrm{RPE}_\Delta$ | RMSE of the relative pose error over the interval $\Delta$. Measures local drift |
| Gauge | Degrees of freedom the estimator cannot observe and that are therefore fixed arbitrarily. Monocular 7, stereo and RGB-D 6, VIO 4 |

**The five things "ATE 0.03 m" depends on** are the map of this lesson.

| What | If it changes | Result |
|---|---|---|
| Alignment ($\mathrm{Sim}(3)$ / $SE(3)$ / 4-DoF) | Scale and gravity errors hide | R2 |
| Trajectory length | ATE grows with it | R3 |
| Timestamp association | $v\,\delta t$ is added | R4 |
| The run (seed, thread order) | One system scatters with a CV of 23% | R5 |
| The sequence | Differences between sequences exceed differences between systems | R5 |

## Key results

The bracket gives the derivation depth (D0 cited / D1 skeleton / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (the closed-form solution of similarity alignment) [D3]** — the solution of
  $\min_{s,R,t}\frac1n\sum_i\lVert y_i - (sRx_i + t)\rVert^2$ is, from the singular value
  decomposition $C = UDV^\top$,
  $$
  R = USV^\top, \quad S = \operatorname{diag}\big(1, 1, \det(U)\det(V)\big), \qquad
  s = \frac{\operatorname{tr}(DS)}{\sigma_x^2}, \qquad t = \mu_y - sR\mu_x \tag{1}
  $$
  with minimum residual $\sigma_y^2 - \operatorname{tr}(DS)^2/\sigma_x^2$ (Umeyama 1991). $S$ is
  the **reflection correction** — without it, on noisy nearly planar data the "rotation" is a
  mirror image. Measured in the reproduction task: for 20 nearly planar points, **935** cases out
  of 2000 need the correction.
- **R2 (the alignment must match the gauge) [D2]** — the larger the group of transforms the
  alignment allows, the smaller the ATE:
  $$
  \mathrm{ATE}_{\mathrm{Sim}(3)} \;\le\; \mathrm{ATE}_{SE(3)} \;\le\; \mathrm{ATE}_{4\text{-DoF}}. \tag{2}
  $$
  Aligning with a group **larger** than the gauge of the estimator absorbs real error. Measured:
  the ATE of a trajectory with a 5% scale error is $0.1728$ m under $SE(3)$ alignment and
  $0.0290$ m under $\mathrm{Sim}(3)$ alignment — using $\mathrm{Sim}(3)$ on a system that observes
  scale (stereo, VIO) makes the scale error disappear. And a gravity-direction error of
  $0.5^\circ$ is **exactly 0** under $SE(3)$ alignment and $0.0189$ m when only yaw is aligned.
- **R3 (ATE grows with length, and alignment hides 42% of the drift) [D2]** — for random-walk
  drift with per-step variance $\sigma^2$,
  $$
  \mathbb{E}\big[\mathrm{MSE}_{\text{first pose fixed}}\big] = \sigma^2\frac{N+1}{2}, \qquad
  \mathbb{E}\big[\mathrm{MSE}_{\text{translation aligned}}\big] = \sigma^2\frac{N^2-1}{6N} \tag{3}
  $$
  (per axis). Both are proportional to $N$, so **ATE $\propto \sqrt{N}$**, and the ratio of the
  RMSEs is $1/\sqrt{3} = 0.577$ — the optimal alignment absorbs 42% of the drift error. With
  rotational drift it grows faster: the measured ATE at $N = 150, 300, 600$ is
  $0.0136, 0.0280, 0.0471$ m while $\mathrm{RPE}_{10}$ is $0.0109, 0.0110, 0.0110$ m and **does
  not change**.
- **R4 (a timestamp offset adds $v\,\delta t$) [D2]** — if the clocks of the estimate and the
  reference are off by $\delta t$,
  $$
  \mathrm{ATE}^2 \;\approx\; \mathrm{ATE}_0^2 + v_{\mathrm{rms}}^2\,\delta t^2. \tag{4}
  $$
  At $v_{\mathrm{rms}} = 2.04$ m/s, $\delta t = 20$ ms gives $0.0407$ m — **more** than the
  odometry drift ATE of this lesson ($0.029$ m). A rigid alignment cannot absorb a time
  misalignment.
- **R5 (one run on one sequence cannot support a claim of difference) [D2]** — (a) running the
  same system 200 times with only the noise changed scatters the ATE with mean $0.0471$,
  standard deviation $0.0108$ (CV 23%) and range $0.024$–$0.078$. (b) Averaging the **paired** log
  ATE ratio of two systems over $n$ sequences has standard error
  $$
  \mathrm{SE} = \sqrt{\frac{\sigma_{\mathrm{int}}^2 + 2\sigma_{\mathrm{run}}^2/r}{n}} \tag{5}
  $$
  ($\sigma_{\mathrm{int}}$: system × sequence interaction, $\sigma_{\mathrm{run}}$: run-to-run
  variation, $r$: runs per sequence). **More runs reduce only the second term; only more
  sequences reduce the first.** The power to detect an 8% improvement with 11 sequences is
  $0.51, 0.66, 0.70$ at 1, 5 and 50 runs, and $0.94$ when the sequences are doubled to 22. The
  power of an unpaired test is $0.00$.

## Derivation

### R2 — alignment and gauge

**Definition of the metrics.** For associated pose pairs $(T_i, \hat{T}_i)$,
$T = (R, p) \in SE(3)$,

$$
\mathrm{ATE} = \Big(\frac1n\sum_i\big\lVert p_i - (sR\hat{p}_i + t)\big\rVert^2\Big)^{1/2}, \qquad
(s, R, t) = \arg\min(\text{the same expression}), \tag{6}
$$

$$
E_i = \big(T_i^{-1}T_{i+\Delta}\big)^{-1}\big(\hat{T}_i^{-1}\hat{T}_{i+\Delta}\big), \qquad
\mathrm{RPE}_\Delta = \Big(\frac1m\sum_i\lVert\operatorname{trans}(E_i)\rVert^2\Big)^{1/2}. \tag{7}
$$

ATE **depends** on the alignment, while RPE uses relative poses only and is therefore
**invariant** to a global rigid transform (`sturm2012-tum-rgbd`). The rotational part of RPE is
$\angle(\operatorname{rot}(E_i))$.

**Proof of (2).** $\mathrm{Sim}(3) \supset SE(3) \supset$ (yaw + translation), so minimizing the
same objective over a larger set gives a smaller value. That is all. What matters is the
**consequence**.

**The gauge principle.** The degrees of freedom the estimator cannot observe are arbitrary in the
estimate and **must be removed** in evaluation — they are not error. The degrees of freedom it
**can** observe are the estimator's responsibility and **must not be removed**.

| Sensor configuration | Gauge (unobservable) | Correct alignment | Common mistake |
|---|---|---|---|
| Monocular | Translation 3 + rotation 3 + scale 1 | $\mathrm{Sim}(3)$ | — |
| Stereo, RGB-D, LiDAR | Translation 3 + rotation 3 | $SE(3)$ | $\mathrm{Sim}(3)$ → hides scale error |
| Visual-inertial (VIO) | Translation 3 + yaw 1 | 4-DoF (yaw + translation) | $SE(3)$ → hides gravity-direction error |

(`zhang2018-trajectory-eval` sets out this correspondence.)

**Numbers 1 — scale.** An estimate with odometry drift (the generator of the reproduction task,
one run) and the same estimate multiplied by a scale of $1.05$:

| Estimate | ATE, $SE(3)$ alignment | ATE, $\mathrm{Sim}(3)$ alignment |
|---|---|---|
| Drift only | $0.029443$ | $0.028958$ |
| Drift + 5% scale | $0.172775$ | $0.028958$ |

The two values of the $\mathrm{Sim}(3)$ column are **equal to six decimals** — the scale error
was absorbed whole by the alignment. A calibration (baseline) error of a stereo system produces
exactly such a scale error, and evaluating with $\mathrm{Sim}(3)$ alignment makes it invisible.

**Numbers 2 — gravity.** An "estimate" obtained by tilting the reference trajectory slightly
about the $x$ axis (a roll error = a gravity-direction error) and then applying an arbitrary yaw
and translation:

| Tilt | ATE, $SE(3)$ alignment | ATE, 4-DoF alignment | Prediction (tilt × extent of the trajectory) |
|---|---|---|---|
| $0.25^\circ$ | $< 10^{-14}$ | $0.0094$ | $0.0093$ |
| $0.5^\circ$ | $< 10^{-14}$ | $0.0189$ | $0.0186$ |
| $1^\circ$ | $< 10^{-14}$ | $0.0378$ | $0.0373$ |
| $2^\circ$ | $< 10^{-14}$ | $0.0755$ | $0.0745$ |

A tilt is a rigid rotation, so $SE(3)$ alignment removes it **completely**. But a VIO observes
gravity (through the accelerometer), so roll and pitch are not gauge, and a $1^\circ$ gravity
error is a real position error of $3.8$ cm on this trajectory. The yaw of the 4-DoF alignment is
closed form: in centred $xy$ coordinates,
$\theta = \operatorname{atan2}\big(\sum(x_1y_2 - x_2y_1),\ \sum(x_1y_1 + x_2y_2)\big)$ (problem P2).

**Where the assumptions break**: (a) the gauge principle is clean when "observable" is a
dichotomy. In reality some degrees of freedom are only weakly observed — a VIO in
constant-velocity straight motion barely observes scale, and a VIO in planar motion barely
observes additional directions (`s1-vio-systems`). Which alignment is right then depends on
**the motion of the sequence**, and reporting the results of both alignments is the honest
course. (b) The segment used for alignment is a choice too. Aligning on the whole trajectory
absorbs drift as in R3; aligning on the first few seconds only exposes the drift but is sensitive
to the noise of the initial estimates. A paper must say which it did.

### R3 — drift, length, and what alignment hides

**The model.** Take the position error of an odometry to be a random walk per axis:
$e_k = \sum_{i\le k}w_i$ with independent $w_i \sim \mathcal{N}(0,\sigma^2)$. Then
$\mathbb{E}[e_je_k] = \sigma^2\min(j,k)$.

**First pose fixed.** Matching the first pose to the reference leaves the error as $e_k$, and

$$
\mathbb{E}\Big[\frac1N\sum_{k=1}^{N}e_k^2\Big] = \frac{\sigma^2}{N}\sum_{k=1}^{N}k = \sigma^2\frac{N+1}{2}.
$$

**Optimal translation alignment.** Aligning the translation only, the optimal $t$ subtracts the
mean error $\bar{e}$. First,

$$
\mathbb{E}[\bar{e}^2] = \frac{\sigma^2}{N^2}\sum_{j=1}^{N}\sum_{k=1}^{N}\min(j,k)
 = \frac{\sigma^2}{N^2}\cdot\frac{N(N+1)(2N+1)}{6} = \sigma^2\frac{(N+1)(2N+1)}{6N},
$$

($\sum_j\sum_k\min(j,k) = \sum_k k^2$ — it counts $k\times k$ squares). Then

$$
\mathbb{E}\Big[\frac1N\sum_k(e_k - \bar{e})^2\Big] = \sigma^2\frac{N+1}{2} - \sigma^2\frac{(N+1)(2N+1)}{6N}
 = \sigma^2\frac{(N+1)(3N - 2N - 1)}{6N} = \sigma^2\frac{N^2 - 1}{6N}.
$$

This is (3). For large $N$ the ratio is $(N/6)/(N/2) = 1/3$, so the RMSE ratio is $1/\sqrt{3}$.

| $N$ | First-pose-fixed MSE (measured / (3)) | Aligned MSE (measured / (3)) | RMSE ratio |
|---|---|---|---|
| 100 | $50.7$ / $50.5$ | $16.66$ / $16.67$ | $0.573$ |
| 400 | $201.5$ / $200.5$ | $66.8$ / $66.7$ | $0.576$ |
| 1600 | $813$ / $800.5$ | $271$ / $266.7$ | $0.577$ |

($\sigma = 1$, mean of 4000 draws.) **Two things to read.** (a) ATE grows as $\sqrt{N}$. So **the
ATEs of sequences of different length cannot be compared directly** — "0.02 on sequence A, 0.08 on
sequence B" may mean not that B is four times harder but that it is sixteen times longer. This is
why KITTI reports error as a percentage of the distance travelled (`geiger2012-kitti`).
(b) Alignment hides 42% of the drift. How much it hides depends on the shape of the trajectory
(a rotational alignment absorbs more), so the aligned ATE is a **lower bound** on the drift.

**With rotational drift.** A real odometry accumulates error in orientation too, and a heading
error is multiplied by the distance travelled afterwards to become position error. With the
generator of the reproduction task (per-step translation noise 2 mm, rotation noise 0.0005 rad),
the mean of 200 runs:

| Frames $N$ | Path length | ATE ($SE(3)$) | $\mathrm{RPE}_{10}$ |
|---|---|---|---|
| 150 | $14.5$ m | $0.0136$ | $0.0109$ |
| 300 | $29.1$ m | $0.0280$ | $0.0110$ |
| 600 | $58.8$ m | $0.0471$ | $0.0110$ |

ATE grows by factors of $2.06$ and $1.69$ as the length doubles, while $\mathrm{RPE}_{10}$ stays
put. **RPE is a property of the system; ATE is a property of system × trajectory.** For a SLAM
system with loop closure the ATE saturates in length, so "does it grow with length" becomes the
very test of "is it globally consistent" — the reason both must be reported **together**.

**Where the assumptions break**: (3) is the formula for independent error increments and
translation only. The error increments of a real visual odometry are correlated with the scene
(they all get worse at once in feature-poor stretches), and scale drift (monocular) enters the
position **multiplicatively**, so the error is proportional to the distance from the origin. In
that case not the $\sqrt{N}$ law but the geometry of the trajectory governs the ATE.

### R4 — timestamps

The clocks of the reference (motion capture) and of the estimate (camera) differ. Evaluation
**associates** poses by timestamp, and if an offset $\delta t$ remains between the two clocks the
estimate $\hat{p}(t)$ is compared with the reference $p(t + \delta t)$. To first order

$$
p(t + \delta t) - \hat{p}(t) \approx \big(p(t) - \hat{p}(t)\big) + v(t)\,\delta t,
$$

and if the estimation error is uncorrelated with the velocity the cross term vanishes in the mean
square, which gives (4).

| $\delta t$ | Measured ATE (error-free estimate) | $v_{\mathrm{rms}}\,\delta t$ |
|---|---|---|
| 5 ms | $0.0102$ | $0.0102$ |
| 10 ms | $0.0204$ | $0.0204$ |
| 20 ms | $0.0407$ | $0.0409$ |
| 50 ms | $0.1018$ | $0.1022$ |

($v_{\mathrm{rms}} = 2.044$ m/s. The measurement is slightly smaller because the rigid alignment
absorbs a very small part.) One frame of a 30 Hz camera is 33 ms, so an evaluation that associates
by **nearest frame** injects a random offset of up to $\pm16.7$ ms. On a fast platform such as a
drone ($5$ m/s) that alone is $8$ cm. The defence is to **interpolate** the reference trajectory
at the timestamps of the estimate, to estimate the clock offset by a one-dimensional search that
minimizes the ATE, and to **report that value**.

**Where the assumptions break**: there are cases in which "error and velocity are unrelated" in
(4) fails — if motion blur degrades the estimate during fast rotation, error and velocity are
positively correlated and the cross term remains. And estimating the offset by minimizing the ATE
is **one more alignment degree of freedom**: by the principle of R2 it is justified only when the
clock offset is not a quantity the estimator is responsible for (only when hardware
synchronization between sensors is outside the scope of the evaluation).

### R5 — the variance of runs and of sequences

**Run-to-run variation.** SLAM is not deterministic — the random numbers of RANSAC, the execution
order of multiple threads, frame drops in real-time processing. The reproduction task imitates
this with the seed of the odometry noise. The ATE distribution of 200 runs of **the same system**
is

| Statistic | Value |
|---|---|
| Mean | $0.0471$ m |
| Standard deviation | $0.0108$ m (CV 23%) |
| Minimum – maximum | $0.0238$ – $0.0784$ m |

A number obtained from one run is one sample of this distribution. **Reporting the best run**
produces exactly the selection bias of `s4-evaluation-science` R3 — here the minimum is half the
mean.

**Sequence-to-sequence variation and pairing.** Run systems A and B $r$ times each on sequences
$j = 1,\dots,n$. Model the log ATE as

$$
\log\mathrm{ATE}_{Aj}^{(k)} = b_j + \varepsilon_{Aj}^{(k)}, \qquad
\log\mathrm{ATE}_{Bj}^{(k)} = b_j + \delta + \eta_j + \varepsilon_{Bj}^{(k)}. \tag{8}
$$

$b_j$ is the difficulty of the sequence (its variance is **large** — the ATE differs by factors
from sequence to sequence), $\delta$ the true improvement of B (a log ratio),
$\eta_j \sim (0, \sigma_{\mathrm{int}}^2)$ the interaction "B does particularly well or badly on
this sequence", and $\varepsilon \sim (0, \sigma_{\mathrm{run}}^2)$ the run-to-run variation.

Forming the per-sequence difference
$d_j = \overline{\log\mathrm{ATE}}_{Bj} - \overline{\log\mathrm{ATE}}_{Aj}$, **$b_j$ cancels in the
subtraction**:

$$
d_j = \delta + \eta_j + (\bar\varepsilon_{Bj} - \bar\varepsilon_{Aj}), \qquad
\operatorname{Var}(d_j) = \sigma_{\mathrm{int}}^2 + \frac{2\sigma_{\mathrm{run}}^2}{r},
$$

and the standard error of $\hat\delta = \frac1n\sum_jd_j$ is (5). The test is a one-sample $t$
test on the $d_j$ (with $n-1$ degrees of freedom).

**Numbers** ($\delta = \log 0.92$, an 8% improvement; $\sigma_{\mathrm{int}} = 0.10$,
$\sigma_{\mathrm{run}} = 0.05$, standard deviation of $b_j$ $0.8$; 4000 simulations):

| Sequences $n$ | Runs $r$ | SE of (5) | Paired power | Unpaired power | Coverage of the 95% interval |
|---|---|---|---|---|---|
| 11 | 1 | $0.0369$ | $0.509$ | $0.000$ | $0.952$ |
| 11 | 5 | $0.0316$ | $0.665$ | $0.000$ | $0.950$ |
| 11 | 50 | $0.0303$ | $0.696$ | $0.000$ | $0.949$ |
| 22 | 5 | $0.0224$ | $0.942$ | $0.000$ | $0.948$ |
| 44 | 5 | $0.0158$ | $0.999$ | $0.000$ | $0.948$ |

**Three things to read.** (a) The unpaired test (comparing the per-sequence mean ATEs of the two
systems as independent samples) has zero power — the variance of sequence difficulty completely
covers the 8% difference. (b) Raising the runs from 5 to 50, **tenfold**, moves the power only
from $0.665$ to $0.696$. In (5), $r$ reduces the second term only, and the first term
$\sigma_{\mathrm{int}}^2/n$ is the floor. (c) Raising the sequences from 11 to 22, **twofold**,
gives $0.665 \to 0.942$. Recalling that KITTI has 11 sequences with public ground truth, an 8%
difference is detected on that benchmark with a power of only about 2/3.

**Where the assumptions break**: (a) (8) treats the log ATE as symmetrically distributed. A
tracking **failure** (divergence, reinitialization) is not the tail of that distribution but an
event of a different kind, and averaging after dropping the failed runs favours a system that
"fails often but is accurate when it succeeds". The failure rate must be reported in **a separate
column** from the ATE. (b) The sequences were assumed to be a random sample from a population.
Benchmark sequences were **chosen** by someone, and the whole field has tuned to them (the
adaptive overfitting of `s4-evaluation-science`). The interval of (5) speaks only of
generalization to "sequences like these". (c) Several runs on the same sequence are independent,
but several sequences recorded in the same **environment** may not be — the effective $n$ is
closer to the number of environments than to the number of sequences.

## Proof sketch

### R1 — Umeyama alignment [D3]

**Hypotheses**
H1: $\sigma_x^2 > 0$ (the points do not all coincide).
H2: $\operatorname{rank}(C) \ge 2$ (the points do not lie on one line) — needed for uniqueness of
the rotation.

**Conclusion** C: (1) minimizes $\frac1n\sum_i\lVert y_i - (sRx_i + t)\rVert^2$ over $s > 0$,
$R \in SO(3)$, $t \in \mathbb{R}^3$, and under H2 the $R$ is unique.

**Strategy**: eliminate $t$ first to obtain a centred problem, turn the rotational part into the
maximization of $\operatorname{tr}(R^\top C)$ and solve it by singular value decomposition, and
finally solve for $s$ as a one-dimensional quadratic.

1. **Eliminating the translation.** For fixed $(s, R)$ the objective is a convex quadratic in $t$
   and setting the gradient to zero gives $t = \mu_y - sR\mu_x$. Substituting leaves
   $\frac1n\sum\lVert y_i' - sRx_i'\rVert^2$ with $x_i' = x_i - \mu_x$, $y_i' = y_i - \mu_y$.
2. **Expansion.** Since $\lVert Rx'\rVert = \lVert x'\rVert$,
   $$
   \frac1n\sum\lVert y_i' - sRx_i'\rVert^2 = \sigma_y^2 - 2s\operatorname{tr}(R^\top C) + s^2\sigma_x^2,
   $$
   using
   $\frac1n\sum y_i'^\top Rx_i' = \operatorname{tr}\big(R^\top\frac1n\sum y_i'x_i'^\top\big) = \operatorname{tr}(R^\top C)$.
   Since $s > 0$, $R$ must **maximize** $\operatorname{tr}(R^\top C)$ whatever $s$ is.
3. **The rotation.** With $C = UDV^\top$, $D = \operatorname{diag}(d_1 \ge d_2 \ge d_3 \ge 0)$,
   $\operatorname{tr}(R^\top UDV^\top) = \operatorname{tr}(MD) = \sum_im_{ii}d_i$ where
   $M := V^\top R^\top U$. $M$ is orthogonal with $\det M = \det(U)\det(V)$ (as $\det R = 1$). The
   diagonal entries of an orthogonal matrix satisfy $\lvert m_{ii}\rvert \le 1$, so:
   - if $\det(U)\det(V) = +1$, $M = I$ is admissible and attains $\sum m_{ii}d_i \le \sum d_i$;
   - if $\det(U)\det(V) = -1$, $M$ must have $\det M = -1$ and $M = I$ is **forbidden**. For such
     $M$, $\sum m_{ii}d_i \le d_1 + d_2 - d_3$ (lemma: an orthogonal matrix of determinant $-1$
     has trace at most $n - 2$, and giving the $-1$ to the smallest singular value is best), and
     $M = \operatorname{diag}(1, 1, -1)$ attains it.
   Together the two cases give $M = S$, that is $R = USV^\top$, with maximum
   $\operatorname{tr}(DS)$.
4. **The scale.** Substituting into step 2 gives
   $\sigma_y^2 - 2s\operatorname{tr}(DS) + s^2\sigma_x^2$, and by H1
   $s = \operatorname{tr}(DS)/\sigma_x^2$ with minimum
   $\sigma_y^2 - \operatorname{tr}(DS)^2/\sigma_x^2$.
5. **Uniqueness.** By H2, $d_2 > 0$ and the maximizer of step 3 is unique (if $d_2 = d_3 = 0$ any
   rotation about the first axis gives the same value). **C**.
   (Omitted: the proof of the lemma of step 3 — the lemma of
   [Umeyama 1991](https://doi.org/10.1109/34.88573).)

**Where it collapses if a hypothesis is removed**

- **Remove $S$ (the reflection correction)**: $R = UV^\top$ can be a **mirror image** with
  $\det = -1$. It does not happen for noise-free points spread in three dimensions, but it is
  common for a **nearly planar trajectory** (a ground robot, level flight) with noise — because
  the direction of the smallest singular value is decided by the noise. The measured 935/2000 of
  the reproduction task is this. A trajectory aligned by a mirror image looks fine within the
  plane, so the ATE number alone does not give it away.
- **Remove H2** (a straight trajectory): the rotation about the line is undetermined. The ATE,
  which uses positions only, is unaffected, but evaluating **orientation** error with that
  alignment gives an arbitrary value. This is the problem that arises when aligning on the
  opening stretch of a driving sequence that only goes straight.
- **Leave $s$ free** (for a system that observes scale): step 4 absorbs the scale error — the
  $0.1728 \to 0.0290$ of R2. The theorem is true; the fault is **choosing the wrong problem to
  apply it to**.

## Problem set

The answer policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★★, R1)** Write the five steps of the proof sketch with no line missing and prove
the lemma of step 3 — for an orthogonal $M$ with $\det M = -1$ and $d_1 \ge d_2 \ge d_3 \ge 0$,
$\sum_im_{ii}d_i \le d_1 + d_2 - d_3$.
*Strategy + key inequality*: if $\det M = -1$ then $M$ has the eigenvalue $-1$, so
$\operatorname{tr}M \le n - 2$. Write
$\sum m_{ii}d_i = d_3\operatorname{tr}M + \sum_i m_{ii}(d_i - d_3)$ and use $m_{ii} \le 1$ and
$d_i - d_3 \ge 0$. The expansion is withheld.

**P2 (derivation, ★★, R2)** Derive the closed-form solution of the 4-DoF alignment that allows
only yaw and translation. Then show that it solves the problem (1) with $R$ restricted to
rotations about the $z$ axis, and state what must be done first in a coordinate frame whose $z$
axis is not the gravity direction.
*Answer sketch*: after centring, differentiating $\operatorname{tr}(R_z(\theta)^\top C)$ in
$\theta$ gives $\theta = \operatorname{atan2}(c_{21} - c_{12},\ c_{11} + c_{22})$. The $z$
coordinate is unaffected by the rotation and is matched by translation only. If the $z$ of the
frame differs from gravity, both trajectories must first be rotated to the gravity direction of
the **reference** — using the gravity of the estimate would hide its error again.

**P3 (derivation, ★★, R3)** Derive (3), and find the fraction absorbed by an alignment that
removes a **linear trend** in addition to the translation (fit the error by $a + bk$ and
subtract). Give one situation in which such an alignment actually occurs.
*Answer sketch*: the expected MSE of the residual of a random walk after removing the mean and
the linear trend is $\sigma^2N/15$ for large $N$, so the RMSE ratio is $\sqrt{2/15} = 0.365$ —
63% of the drift is hidden. Situation: when the scale is included in the alignment, on a
trajectory that moves away from the origin the scale absorbs the linear trend of the position.

**P4 (numerical, ★, R3, R4, R5)** (a) For random-walk drift with $N = 1000$, $\sigma = 2$ mm,
find the three-dimensional ATE (RMSE) with the first pose fixed and with translation alignment.
(b) For a sequence with speed $v_{\mathrm{rms}} = 1.2$ m/s and drift ATE $0.05$ m, what is the
largest offset $\delta t$ whose effect on the ATE is at most 10%? (c) For
$\sigma_{\mathrm{int}} = 0.15$, $\sigma_{\mathrm{run}} = 0.08$, $r = 3$, find by the normal
approximation the number of sequences needed to detect a 5% improvement
($\delta = \log 0.95$) with power 0.8.
*Answer*: (a) multiply the per-axis MSEs $\sigma^2(N+1)/2$ and $\sigma^2(N^2-1)/(6N)$ by 3 and
take the square root: $0.002\sqrt{3\times500.5} = 0.0775$ m and
$0.002\sqrt{3\times166.67} = 0.0447$ m. (b) From $\sqrt{0.05^2 + (1.2\,\delta t)^2} \le 0.055$,
$\delta t \le 0.0191$ s (19 ms). (c) $\operatorname{Var}(d_j) = 0.0225 + 2\times0.0064/3 = 0.02677$,
$n = (1.960 + 0.842)^2\times0.02677/(0.0513)^2 = 79.9 \to 80$. (Tolerance 2%.)
*Check*: see that the answer of (c) is far above the number of sequences of a benchmark (10 to
20) — the conclusion is that **a 5% difference cannot be detected with current benchmarks**.

**P5 (implementation, ★★★, R1–R5)** Extend the evaluation tool of the reproduction task into a
command-line tool that reads TUM-format files.
*Rubric*: (a) implement timestamp association by **interpolation** (linear for position,
spherical linear for orientation) and report the difference in ATE from nearest-frame association
(b) make the alignment ($\mathrm{Sim}(3)$ / $SE(3)$ / 4-DoF / first $k$ frames only) an option and
print **which alignment was used** in the output (c) implement the one-dimensional search for the
clock offset and report the estimate (d) print ATE, RPE (translation and rotation), path length
and the number of associated poses together (e) show agreement of the ATE with one public tool
(`evo` or `rpg_trajectory_evaluation`) on one public sequence to within $10^{-6}$ m.

**P6 (counterexample, ★★, R2, R3)** (a) Construct a counterexample to "a system with lower ATE
also has lower RPE" — a system that is locally accurate but drifts globally, and one that jitters
locally but is globally tied down, will do. (b) Give numerically a counterexample to "more
alignment degrees of freedom is always fairer".
*Property checklist*: (a) builds (i) random-walk drift (no noise) and (ii) an estimate with no
drift but large independent per-frame noise, and shows that the ranking by the two metrics is
**reversed** — the typical contrast between loop-closing SLAM and odometry. (b) reproduces with
your own numbers the scale example of the lesson ($0.1728 \to 0.0290$) or the gravity example.
Property to confirm: the two metrics measure **different things**, and alignment is a matter of
gauge, not of fairness.

**P7 (paper, ★★, R2, R3, R5)** Read the section on evaluation metrics of `sturm2012-tum-rgbd`,
the sections on alignment and error metrics of `zhang2018-trajectory-eval` and the part on
odometry evaluation of `geiger2012-kitti`, and (a) transcribe the ATE and RPE definitions of
Sturm et al. as formulas and compare them with (6) and (7) of this lesson, (b) check whether the
alignment Zhang and Scaramuzza recommend per sensor configuration is the same as the table of
this lesson, (c) write how the KITTI metric handles the segment length (over which lengths it
averages) and explain how that avoids the problem of R3, (d) find whether any of the three papers
deals with **run-to-run variation**.
*Rubric*: (a) and (b) pass by citing the formula or table (if it differs from this lesson, treat
it as an error of this lesson and write down the difference). (c) passes by naming the structure
of averaging over lengths and the normalization by distance. (d) is the core — if you find none,
**write that you found none**, and say in one sentence what that means (the standard metrics of
the benchmarks lack a report of variance).

## Paper reading

**Three must-read papers.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read in three passes, and in the third pass concentrate on questions 5,
6 and 7.

1. **Sturm, Engelhard, Endres, Burgard & Cremers, "A benchmark for the evaluation of RGB-D SLAM
   systems" (2012, IROS)** — role: `seminal`.
   <https://doi.org/10.1109/IROS.2012.6385773> (the section defining the evaluation metrics)
   The paper that established the two metrics ATE and RPE in their present form. The source of
   (6) and (7) of this lesson.
   Additional questions: (a) why do the authors propose **both** metrics — what does each
   measure? (b) how do the authors handle the accuracy of the reference trajectory (motion
   capture) and clock synchronization? (c) how do they say the interval $\Delta$ of RPE should be
   chosen?
2. **Zhang & Scaramuzza, "A tutorial on quantitative trajectory evaluation for
   visual(-inertial) odometry" (2018, IROS)** — role: `standard`.
   <https://doi.org/10.1109/IROS.2018.8593941> (the sections on alignment and on error metrics)
   The primary source for R2 of this lesson. It formulates alignment as "the gauge of the
   estimation problem".
   Additional questions: (a) on what grounds do the authors use a different alignment group for
   each sensor configuration? (b) how do the authors show the effect on the result of the number
   of poses used for alignment (all versus the first few)? (c) how is their way of reporting
   relative error by segment length the same as, and different from, KITTI's?
3. **Geiger, Lenz & Urtasun, "Are we ready for autonomous driving? The KITTI vision benchmark
   suite" (2012, CVPR)** — role: `standard`.
   <https://doi.org/10.1109/CVPR.2012.6248074> (the part on the odometry benchmark and its
   evaluation metric)
   The benchmark that set the standard of distance-normalized relative error. The case study for
   R3 and R5 of this lesson.
   Additional questions: (a) why did the authors choose segment-wise relative error rather than
   absolute trajectory error? (b) how many sequences have public ground truth, and what does that
   number mean as the $n$ of (5)? (c) what information is lost when a leaderboard ranks by one
   number?

**One recommended paper.** `umeyama1991-least-squares` (the original of R1; four pages, and it
contains the proof of the lemma, <https://doi.org/10.1109/34.88573>).

**The ten fixed questions**: (1) what problem is solved under what assumptions (2) what exactly
could earlier work not do (3) the key idea in one line of mathematics (4) what is the theoretical
guarantee and **what is not guaranteed** (5) the independent and dependent variables and baselines
of the experiments, and were they tuned fairly (6) do the metrics match the claims, and are
variance and seeds reported (7) what information needed for reproduction is missing (8) if it is
wrong, which assumption to suspect first (9) computational and memory complexity and real-time
capability (10) what would you change to surpass it a year from now.

## Reproduction task

**Tier R2 (algorithm reimplementation).** Compute budget: one laptop CPU core, under 5 minutes in
total, at most 1 GB of memory. numpy + scipy only (a public tool is installed only for the
comparison of Part G).

**The input data** is produced by the generator below. The reference trajectory is an analytic
curve (600 frames, 20 Hz, length $58.77$ m, $v_{\mathrm{rms}} = 2.044$ m/s), and the estimate is
an odometry that adds noise to the relative motions of the reference and re-integrates them **in
an arbitrary world frame**. **What the learner writes is the alignment (Umeyama, 4-DoF), ATE, RPE
and the statistical analysis.**

```python
"""Reproduction task of s1-slam-benchmarking: generator of the reference and the odometry."""

import numpy as np

SEED = 20261117


def exp_so3(w):
    """Exponential map of the rotation vector w (Rodrigues)."""
    theta = np.linalg.norm(w)
    k = np.array([[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]])
    if theta < 1e-12:
        return np.eye(3) + k
    return np.eye(3) + np.sin(theta) / theta * k + (1 - np.cos(theta)) / theta**2 * k @ k


def ground_truth(n=600, dt=0.05):
    """Times t, positions p (n, 3), orientations R (n, 3, 3). x along the velocity, z up."""
    t = np.arange(n) * dt
    p = np.stack([4 * np.cos(0.4 * t), 3 * np.sin(0.8 * t), 0.5 * np.sin(0.3 * t) + 0.02 * t], 1)
    v = np.stack([-1.6 * np.sin(0.4 * t), 2.4 * np.cos(0.8 * t), 0.15 * np.cos(0.3 * t) + 0.02], 1)
    rot = np.empty((n, 3, 3))
    for i in range(n):
        x = v[i] / np.linalg.norm(v[i])
        y = np.cross([0.0, 0.0, 1.0], x)
        y /= np.linalg.norm(y)
        rot[i] = np.stack([x, y, np.cross(x, y)], 1)
    return t, p, rot


def odometry_estimate(p, rot, rng, sigma_t=0.002, sigma_r=0.0005):
    """Estimate re-integrated in an arbitrary world frame from noisy relative motions."""
    n = len(p)
    p_hat, rot_hat = np.empty_like(p), np.empty_like(rot)
    rot_hat[0] = exp_so3(np.array([0.3, -0.2, 1.1]))
    p_hat[0] = np.array([3.0, -2.0, 1.0])
    for i in range(1, n):
        d_rot = rot[i - 1].T @ rot[i] @ exp_so3(sigma_r * rng.normal(size=3))
        d_p = rot[i - 1].T @ (p[i] - p[i - 1]) + sigma_t * rng.normal(size=3)
        p_hat[i] = p_hat[i - 1] + rot_hat[i - 1] @ d_p
        rot_hat[i] = rot_hat[i - 1] @ d_rot
    return p_hat, rot_hat
```

**Conventions (must be followed).** (a) Create `np.random.default_rng(SEED)` afresh for each
Part, and inside `odometry_estimate` draw, at every step, the rotation noise (3 numbers) first
and the translation noise (3 numbers) second (exactly as in the code above). (b) ATE is the RMSE
of the positions and the estimate is aligned to the reference ($x = \hat{p}$, $y = p$). (c) RPE is
computed with full poses as in (7), using all overlapping pairs $i = 0,\dots,n-\Delta-1$.

**Part A — Umeyama.** (a) On points obtained by applying a known transform ($s = 1.7$, a rotation
of $0.7$ rad about the axis $(1,2,3)$, $t = (0.5, -1.2, 2.0)$) to the reference trajectory,
confirm that (1) recovers that transform. (b) For 2000 cases of 20 nearly planar points (standard
deviation of $z$: $10^{-3}$) given a random rotation and noise of standard deviation $0.05$,
report the number of cases with $\det(U)\det(V) < 0$ and the maximum of $\lvert\det R - 1\rvert$
after the correction.

**Part B — alignment and gauge.** (a) For one odometry estimate and the same estimate multiplied
by $1.05$, find the ATE under $SE(3)$ and $\mathrm{Sim}(3)$ alignment. (b) For the "estimates"
obtained by tilting the reference trajectory by $0.25, 0.5, 1, 2^\circ$ about the $x$ axis and
applying a yaw of $0.9$ rad and a translation $(1, 2, -0.5)$, find the ATE under $SE(3)$ alignment
and under 4-DoF alignment.

**Part C — drift and length.** (a) For three-dimensional random walks with $\sigma = 1$
($N = 100, 400, 1600$; 4000 draws) compare the first-pose-fixed MSE, the translation-aligned MSE
and the RMSE ratio with (3). (b) For 200 odometry estimates find the mean ATE ($SE(3)$) and
$\mathrm{RPE}_{10}$ over the first $N = 150, 300, 600$ frames.

**Part D — timestamps.** Find the ATE of the error-free estimate $\hat{p}(t) = p(t + \delta t)$
at $\delta t = 5, 10, 20, 50$ ms and compare with $v_{\mathrm{rms}}\,\delta t$.

**Part E — run-to-run variation.** From the 200 runs of Part C (b), report the mean, standard
deviation, minimum and maximum of the $N = 600$ ATE and the 95% confidence interval of the mean.

**Part F — sequences and pairing.** With the model (8) simulate the five settings of the table in
the text 4000 times each and find the power of the paired $t$ test and of the unpaired Welch test
(on the per-sequence mean ATE), and the coverage of the 95% interval of $\hat\delta$.

**Part G — comparison with a public tool.** Save the estimate and the reference of Part B (a) as
TUM-format files, obtain the APE RMSE under $SE(3)$ alignment and under $\mathrm{Sim}(3)$
alignment with a public tool (`evo_ape` of `evo` is recommended) and compare with your own
implementation. **Note: the author could not install and run a public tool in the environment in
which this lesson was written.** The reference values below are those of the author's
implementation, verified only by the recovery of the transform in Part A ($10^{-12}$) and the
analytic solution (3) in Part C. The verdict of this Part is therefore "agreement between your
implementation and the public tool", and if the value of the public tool differs from the
reference values below by more than $10^{-6}$, **the reference values of this lesson are the ones
in error** — report the difference.

**Acceptance criteria — all seven conditions must hold to pass.**

1. **Part A** — (a) $\lvert s - 1.7\rvert$, $\max\lvert R - R_0\rvert$ and
   $\max\lvert t - t_0\rvert$ are all below $10^{-12}$. (b) The cases needing the reflection
   correction number $935 \pm 60$ out of 2000 and after the correction
   $\lvert\det R - 1\rvert < 10^{-12}$. **Print alongside that without the correction those cases
   have $\det R = -1$.**
2. **Part B** — (a) the ATE is $0.029443$ under $SE(3)$ and $0.028958$ under $\mathrm{Sim}(3)$,
   and at scale $1.05$ it is $0.172775$ under $SE(3)$ and $0.028958$ under $\mathrm{Sim}(3)$
   (tolerance $10^{-5}$; when the random-number convention is followed). **The two
   $\mathrm{Sim}(3)$ values agree to within $10^{-9}$.** (b) The ATE under $SE(3)$ alignment is
   below $10^{-12}$ for all four tilts and the ATE under 4-DoF alignment is
   $0.00944, 0.01887, 0.03775, 0.07549$ (tolerance $10^{-4}$).
3. **Part C** — (a) the RMSE ratios are $0.573, 0.576, 0.577$ ($\pm0.01$) and the two MSEs are
   within 3% relative error of (3). (b) The mean ATE is $0.0136, 0.0280, 0.0471$ (8% relative
   error), **monotonically increasing**, and the mean $\mathrm{RPE}_{10}$ is $0.0110 \pm 0.0003$
   at all three lengths.
4. **Part D** — the ATE is $0.0102, 0.0204, 0.0407, 0.1018$ (tolerance $10^{-4}$) and within 1%
   relative error of $v_{\mathrm{rms}}\,\delta t$.
5. **Part E** — mean $0.0471 \pm 0.003$, standard deviation $0.0108 \pm 0.002$, and **a CV of at
   least $0.15$**. Show that the minimum is at most $0.6$ times and the maximum at least $1.5$
   times the mean, and report the 95% interval of the mean.
6. **Part F** — the paired power is $0.51, 0.66, 0.70, 0.94, 1.00$ ($\pm0.03$), the unpaired
   power is below $0.02$ in all five settings, and the coverage of the interval is
   $0.95 \pm 0.01$. Confirm that under the null ($\delta = 0$) the rejection rate of the paired
   test is $0.05 \pm 0.01$.
7. **Part G** — the ATE of your implementation and the APE RMSE of the public tool agree to
   within $10^{-6}$ m for both alignments. Report the name and version of the tool and the
   commands run.

**Comparison**: (a) the baseline of Part A is the known transform, of Part C (a) the analytic
solution (3), and of Part D $v_{\mathrm{rms}}\,\delta t$. (b) The baseline of Part G is the
public tool. (c) The baseline of Part F is the unpaired test.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The scale of Part A (a) comes out as $1/1.7$ | $x$ and $y$ were swapped (the reference was aligned to the estimate) | (1) maps $x \mapsto y$. ATE aligns the estimate to the reference |
| The scale is slightly off | $\sigma_x^2$ was computed as a sample variance ($n-1$ degrees of freedom) or as the mean of the per-axis variances | $\sigma_x^2 = \frac1n\sum\lVert x_i - \mu_x\rVert^2$ (the **sum** over the three axes) |
| $\det R = -1$ remains in Part A (b) | $S$ was used in $R$ only and not in the $\operatorname{tr}(DS)$ of $s$, or was left out altogether | Check that $S_{33}$ is set by the sign of $\det(U)\det(V)$ |
| The values of Part B differ from the reference values in the third decimal | The order of the random numbers differs | Check that each step draws 3 rotation numbers then 3 translation numbers, from a generator newly created with `SEED` |
| The ATE under 4-DoF alignment equals that under $SE(3)$ | The full rotation was estimated, not yaw only | Check that the $z$ axis of the alignment rotation is $(0,0,1)$ |
| $\mathrm{RPE}$ changes with the alignment | It was computed from differences of aligned positions (orientations were not used) | Check that $\hat{T}_i^{-1}\hat{T}_{i+\Delta}$ is used as in (7). It must be invariant to a global transform |
| The ATE of Part D is 0 | The reference was evaluated with the same offset | Compare $\hat{p}_i = p(t_i + \delta t)$ with $p(t_i)$ |
| The paired power of Part F is near 0.05 | $d_j$ was formed per run rather than per sequence, or $b_j$ was drawn separately for the two systems | Check that the same $b_j$ is common to A and B |
| In Part G the difference is at the level of $10^{-4}$ | The files were saved with truncated digits | Save at least 9 decimals. Also check the order of the orientation quaternion (qx qy qz qw) |

## Open problems

- **(Open problem) The error of the reference trajectory itself** — every metric assumes the
  reference is the truth, but motion capture has millimetre and RTK-GNSS/INS centimetre errors,
  and the ATE of the latest systems has come close to that level. When the error of the reference
  is the same size as that of the estimate, the ranking is noise. Current approaches: more
  precise references built with laser trackers and survey-grade scans, and methods that optimize
  the reference and the estimate jointly. What is missing: a standard procedure that
  **propagates the uncertainty of the reference into the confidence interval of the metric** —
  current leaderboards take the reference error to be zero.
- **(Open problem) The relation between trajectory error and task performance** — nothing
  guarantees that a system with lower ATE does better on the actual task (navigation,
  manipulation, AR). A task may be more sensitive to local consistency, latency and failure
  recovery. Current approaches: map-quality metrics (reconstruction accuracy and completeness),
  task-based evaluation. What is missing: a systematic study of **which metric predicts
  performance** for each task — the same gap as the proxy-metric validity problem of
  `s4-evaluation-science`.
- **(Open problem) Aggregation that includes failures** — as seen under "where the assumptions
  break" of R5, a tracking failure is not the tail of the ATE. Every way of merging failure rate
  and accuracy into one number (giving failures a penalty ATE, evaluating successful stretches
  only) involves an arbitrary choice, and that choice changes the ranking. Current approach:
  reporting cumulative error distribution curves (the fraction of successes per error threshold).
  What is missing: principles of aggregation based on application-specific utility, reflecting
  that the **cost** of a failure differs between applications.
- **(Open problem) Evaluation in long-term and dynamic environments** — for maps on a scale of
  decades, changing environments and SLAM over many sessions, the very notion of a "reference
  trajectory" weakens (when the environment changes the same pose sees something different).
  Current approaches: the success rate of relocalization across sessions, and the precision and
  recall of change detection. What is missing: a metric for the **shelf life** of a map and an
  evaluation protocol on public data spanning years that can measure it.

## Concept check

Take it with `rc quiz s1-slam-benchmarking`. This quiz is a **concept check only**; the real work
is the problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

## How to study this stage

1. **Read the table of the five dependencies first (10 min)** — the table in "Setup and
   notation". Memorize the five questions to ask of an ATE number in a paper (alignment, length,
   timestamps, runs, sequences).
2. **Umeyama from a blank page (60 min)** — five steps. Steps 1 and 2 (eliminating the translation
   and expanding) are mechanical; the core is the two cases of step 3. Run Part A (b) to see **how
   often** the reflection is needed and then read it again: $S$ is not decoration.
3. **See what alignment hides with Part B (50 min)** — see for yourself that the two values of
   the $\mathrm{Sim}(3)$ column agree to the sixth decimal, and that a tilt error becomes
   $10^{-14}$ under $SE(3)$ alignment. Rewrite the gauge table in your own words.
4. **Derive (3), then Part C (50 min)** — $\sum\sum\min(j,k) = \sum k^2$ is the key. After
   confirming $1/\sqrt3$ in numbers, build the table in which ATE grows with length and RPE does
   not.
5. **See the two noise sources with Parts D and E (40 min)** — a 20 ms offset produces a larger
   error than the drift ATE, and the ATE of one system scatters from $0.024$ to $0.078$. These two
   numbers are the answer to the practice of "comparing single-run ATEs to the third decimal".
6. **Derive (5), then Part F (50 min)** — the one line in which $b_j$ cancels when the difference
   is formed is the core. Put the row with ten times the runs next to the row with twice the
   sequences.
7. **Validate your tool with Part G (40 min)** — match the public tool to $10^{-6}$. If it does
   not match, start from the last row of the diagnosis table (digits, quaternion order). The task
   extends to **reporting it if the reference values of this lesson differ from the public
   tool**.
8. **The three papers (150 min)** — Sturm et al. (definition of the metrics) → Zhang and
   Scaramuzza (alignment and gauge) → Geiger et al. (distance normalization). In all three look
   for "how are variance and the number of runs reported". The one-page note per paper is
   **mandatory**.
9. **Close the module (30 min)** — write a one-page evaluation protocol for your own research (or
   for the reproduction tasks of the earlier lessons of S1): the alignment and its justification,
   timestamp handling, runs per sequence, paired analysis, the reporting of failures. There must
   be an answer to each of the five dependencies.

**Pass criterion**: from a blank page you can derive the five steps of Umeyama, (3), (4) and (5);
you can say which alignment is right for each sensor configuration and why; you can tell apart
what ATE and RPE are each a property of; you have code that satisfies all seven conditions of the
reproduction task (including the comparison of Part G); and you have notes on the three papers.
