---
id: s2-generative-policies
lang: en
title: Generative policies
summary: >-
  Policies that output actions as a **distribution** rather than regressing a single one. First prove,
  down to the constant, why the denoising score matching objective is the same as minimizing the
  distance to the true score, and derive that the velocity field of the probability-flow ODE is an
  affine function of the score. Then write the bias-variance trade-off of the action chunk length $H$
  in closed form and confirm numerically that an interior optimum exists — the tracking cost grows
  linearly in $H$ while the action jitter falls roughly as $1/H$. Finally watch, end to end and
  numerically, MSE regression collapse between two modes while a score-based sampler recovers both.
objectives:
  - Prove that the denoising score matching objective differs from the $L^2$ distance to the true score only by a constant.
  - Derive that on a Gaussian path the probability-flow velocity field is an affine function of the score.
  - Say why MSE regression collapses between the modes of a multimodal action distribution, and show it numerically.
  - Write the bias-variance trade-off of the action chunk length in closed form and confirm the interior optimum numerically.
  - Explain that flow matching and score-based diffusion learn the same path under different parameterizations.
tags: [manipulation, policy-learning, diffusion, score-matching, flow-matching, action-chunking, research]
---

# Generative policies

## Setup and notation

`s2-learned-grasping` is assumed; in particular its conclusion — that the statistics of labels and
distributions matter more than architecture — holds here too. Also assumed:

- Probability: conditional expectation, the reparameterization of a Gaussian, and the **statement
  only** of the Fokker–Planck equation (no derivation). No change of measure is used.
- That the minimizer of a least-squares regression is the conditional expectation. That is the whole
  of the mode collapse in R2.
- Network architectures and training techniques are **not** needed — the reproduction task runs a
  sampler with an analytic score and **no training at all**.

Notation (in addition to module S2's):

| Symbol | Meaning |
|---|---|
| $o$ | the observation (image, point cloud, state) |
| $a \in \mathbb{R}^{d}$ | the action; for a chunk, $a = (a_1,\dots,a_H)$ |
| $\pi(a \mid o)$ | the policy — a **distribution** |
| $x_t$ | the noised action along the diffusion path, $x_0 \sim \pi$, $x_1 \approx \mathcal{N}(0, I)$ |
| $\alpha_t, \sigma_t$ | path coefficients, with $x_t = \alpha_t x_0 + \sigma_t \epsilon$ |
| $s_\theta(x, t)$ | the learned score model, $\approx \nabla_x \log q_t(x)$ |
| $u_t(x)$ | the velocity field of the probability-flow ODE |
| $H$ | the action chunk length |
| $\sigma_w^2, \sigma_o^2$ | disturbance and observation-noise variances |
| $\lambda$ | the weight on action jitter |

**Why a distribution.** Human demonstration data is **multimodal** — from the same observation one
may go left or right. Regressing a single action (an $L^2$ loss) gives the **conditional
expectation**, which lands **between** the modes, and that midpoint may be neither (it drives into
the wall). So the policy outputs a distribution. This lesson covers how to represent that
distribution by its **score**, and the trade-off of emitting actions in **chunks**.

Two assumptions, stated explicitly.

- **(A1) Gaussian path** — the forward process is an affine Gaussian path
  $x_t = \alpha_t x_0 + \sigma_t\epsilon$. That gives both the closed forms of R1 and the affine
  relation of R3.
- **(A2) quasi-static execution** — no observation is used while a chunk executes (open loop).
  Variants that mix in observations are in the failure modes of §R2.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof).

- **R1 (equivalence of denoising score matching) [D3]** — under (A1),
  $$\mathbb{E}_{x_0,\epsilon}\Big\lVert s_\theta(x_t,t) - \nabla_{x_t}\log q(x_t \mid x_0)\Big\rVert^2
    \;=\; \mathbb{E}_{x_t}\Big\lVert s_\theta(x_t,t) - \nabla_{x_t}\log q_t(x_t)\Big\rVert^2
    \;+\; C,
    \tag{1}$$
  with $C$ independent of $\theta$. So minimizing the **computable** left side (the conditional score
  is $-(x_t - \alpha_t x_0)/\sigma_t^2$ in closed form) minimizes the **incomputable** right side
  (the distance to the true score). That is the whole of diffusion-policy training
  ([Vincent 2011](https://doi.org/10.1162/NECO_a_00142)).
- **R2 (mode collapse of MSE regression) [D2]** — the minimizer of an $L^2$ loss is
  $\mathbb{E}[a \mid o]$. If the action distribution has two equally weighted modes at $\pm m$, the
  regression solution is **exactly the midpoint**, a distance $m$ from each mode. In the reproduction
  task $m = 1$ and the regression solution is $0$, while a sampler integrating the probability-flow
  ODE with the analytic score **recovers both modes**
  ($P[\text{left}] = 0.5020$; mode means $-0.9974 / +1.0050$; standard deviations
  $0.2482/0.2449$; 99.8% within $3\sigma$ of a mode).
- **R3 (the score and the velocity field are affinely related) [D2]** — on the path of (A1), the
  velocity field of the probability-flow ODE $\dot x = u_t(x)$ is
  $$u_t(x) \;=\; \frac{\dot\alpha_t}{\alpha_t}\,x
    \;+\; \left(\frac{\dot\alpha_t \sigma_t^2}{\alpha_t} - \dot\sigma_t\sigma_t\right) s_t(x),
    \qquad s_t = \nabla\log q_t,
    \tag{2}$$
  so **the velocity field and the score are affine transforms of each other**. Flow matching
  (regressing the velocity field) and score-based diffusion (regressing the score) therefore learn
  **the same object under different parameterizations** — the differences lie in the loss weighting
  and in the stability of the numerical integration, not in expressiveness.
- **R4 (bias-variance of an action chunk) [D2]** — under (A2), an open-loop chunk of length $H$ makes
  the tracking cost **grow linearly** ($\sigma_o^2 + \sigma_w^2(H-1)/2$) while the action jitter
  **falls** roughly as $1/H$, so the total cost has an **interior optimum**. The measured slope of
  the tracking cost is $0.004941$ (predicted $\sigma_w^2/2 = 0.005$) and the total cost is minimal at
  $H = 8$. The naive closed form $H^\ast = \sqrt{2\lambda K/\sigma_w^2} = 10.18$ **overestimates**,
  because the per-chunk jitter $K$ itself depends on $H$.

## Derivation

### R1 — the equivalence of denoising score matching

**The problem.** The true score $\nabla\log q_t$ cannot be computed because $q_t$ is unknown. But the
score of the conditional $q(x_t \mid x_0) = \mathcal{N}(\alpha_t x_0, \sigma_t^2 I)$ is

$$
\nabla_{x_t}\log q(x_t \mid x_0) = -\frac{x_t - \alpha_t x_0}{\sigma_t^2}
  = -\frac{\epsilon}{\sigma_t}
  \tag{3}
$$

in **closed form** (since $x_t = \alpha_t x_0 + \sigma_t\epsilon$). Equation (1) claims that
replacing the former by the latter leaves the optimum unchanged.

**Proof.** Expand the left side. Since $q_t(x) = \int q(x \mid x_0) q_0(x_0)\,dx_0$,

$$
\begin{aligned}
\mathbb{E}_{x_0, x_t}\big\lVert s_\theta - \nabla\log q(x_t\mid x_0)\big\rVert^2
 &= \underbrace{\mathbb{E}\lVert s_\theta\rVert^2}_{(\mathrm{i})}
  - 2\underbrace{\mathbb{E}\big\langle s_\theta,\ \nabla\log q(x_t\mid x_0)\big\rangle}_{(\mathrm{ii})}
  + \underbrace{\mathbb{E}\lVert\nabla\log q(x_t\mid x_0)\rVert^2}_{(\mathrm{iii})}.
\end{aligned}
$$

(iii) is independent of $\theta$, hence constant. (i) is an expectation over the marginal of $x_t$,
so it is $\mathbb{E}_{x_t}\lVert s_\theta\rVert^2$ as it stands. The crux is (ii):

$$
\begin{aligned}
\mathbb{E}\big\langle s_\theta, \nabla\log q(x_t\mid x_0)\big\rangle
 &= \int\!\!\int q_0(x_0)\,q(x_t\mid x_0)\,
    \Big\langle s_\theta(x_t),\ \frac{\nabla_{x_t} q(x_t\mid x_0)}{q(x_t\mid x_0)}\Big\rangle dx_t\,dx_0 \\
 &= \int \Big\langle s_\theta(x_t),\ \nabla_{x_t}\!\!\int q_0(x_0) q(x_t\mid x_0)\,dx_0\Big\rangle dx_t
  \qquad(\text{the } q \text{ cancels; differentiation under the integral}) \\
 &= \int \big\langle s_\theta(x_t),\ \nabla_{x_t} q_t(x_t)\big\rangle dx_t
  = \int q_t(x_t)\big\langle s_\theta(x_t),\ \nabla\log q_t(x_t)\big\rangle dx_t \\
 &= \mathbb{E}_{x_t}\big\langle s_\theta,\ \nabla\log q_t\big\rangle .
\end{aligned}
$$

**Those four lines are the whole theorem.** The denominator $q(x_t\mid x_0)$ of the conditional score
cancels against the measure, leaving only $\nabla q$, and the integral over $x_0$ produces the
gradient of the marginal. Collecting (i) and (ii),

$$
\mathbb{E}\lVert s_\theta\rVert^2 - 2\mathbb{E}\langle s_\theta, \nabla\log q_t\rangle
 = \mathbb{E}\big\lVert s_\theta - \nabla\log q_t\big\rVert^2 - \mathbb{E}\lVert\nabla\log q_t\rVert^2,
$$

and the last term is also independent of $\theta$. Folding it together with (iii) into $C$ gives (1).
$\square$

**Why this determines practice.** Since the conditional score in (3) is $-\epsilon/\sigma_t$,
regressing the **noise $\epsilon$** instead of the score is equivalent ($\epsilon$-prediction) — only
the weighting differs, not the optimum. That is why implementations mix $\epsilon$-prediction,
$x_0$-prediction and $v$-prediction and are all **reweightings of the same objective**. Problem P1
makes that reweighting explicit.

**Two places the assumptions break.**

1. **Differentiation under the integral.** The third line above moves $\nabla_{x_t}$ inside the
   integral over $x_0$. If $q_0$ is not smooth at the boundary of a compact support (a discrete
   action space) or has heavy tails, that exchange is not justified. Practical action spaces are
   bounded intervals, so the score diverges at the boundary and **training becomes unstable near
   it** — which is why implementations scale actions to $[-1,1]$ and avoid $\tanh$.
2. **$\sigma_t \to 0$.** The conditional score of (3) diverges as $1/\sigma_t$, so the variance blows
   up at small $t$. Every implementation therefore weights the loss by something like $\sigma_t^2$ or
   truncates $t$ from below. This is a numerical matter rather than a theoretical one, but it
   **dominates the outcome**.

### R2 — why MSE regression goes between the modes

The minimizer of the $L^2$ loss $\mathbb{E}\lVert f(o) - a\rVert^2$ is the conditional expectation

$$
f^\ast(o) = \mathbb{E}[a \mid o]
  \tag{4}
$$

(by orthogonal decomposition: $\mathbb{E}\lVert f - a\rVert^2 =
\mathbb{E}\lVert f - \mathbb{E}[a\mid o]\rVert^2 + \mathbb{E}\mathrm{Var}[a \mid o]$, and the second
term does not involve $f$). If the action distribution is
$\frac12\mathcal{N}(-m, \varsigma^2) + \frac12\mathcal{N}(+m, \varsigma^2)$, then $f^\ast = 0$,
**a distance $m$ from each mode**. For $m \gg \varsigma$ that action **never appears** in the data.

**Why a score-based sampler differs.** The sampler does not average; it **draws** from $q_0$. The
reproduction task measures the following on two modes with $m = 1$ and $\varsigma = 0.25$.

| Quantity | MSE regression | score sampler | target |
|---|---|---|---|
| output | $0$ (constant) | a distribution | — |
| $P[\text{left mode}]$ | — | $0.5020$ | $0.5$ |
| left mode mean / sd | — | $-0.9974 / 0.2482$ | $-1 / 0.25$ |
| right mode mean / sd | — | $+1.0050 / 0.2449$ | $+1 / 0.25$ |
| fraction within $3\sigma$ of a mode | $0$ | $0.9980$ | $\approx 1$ |

**The last row is the conclusion**: the regression output falls within $3\sigma$ of neither mode.

**Where the assumption breaks**: (4) is unproblematic for a **unimodal** action distribution — there
MSE regression is right and a generative model is overkill. Multimodality is a property of how the
data was collected (several people, several attempts), so it must be **judged from the data**. If the
conditional variance $\mathrm{Var}[a\mid o]$ is large and bimodal a generative model is needed, and
if it is small it is not. "It is diffusion, therefore it is better" is not an argument.

### R3 — the score and the velocity field are affinely related

Fix the path $x_t = \alpha_t x_0 + \sigma_t\epsilon$. By definition the velocity field of the
probability-flow ODE is $u_t(x) = \mathbb{E}\big[\dot x_t \mid x_t = x\big]$, and since
$\dot x_t = \dot\alpha_t x_0 + \dot\sigma_t\epsilon$,

$$
u_t(x) = \dot\alpha_t\,\mathbb{E}[x_0 \mid x_t = x] + \dot\sigma_t\,\mathbb{E}[\epsilon \mid x_t = x].
  \tag{5}
$$

Both conditional expectations can be written with the score. On a Gaussian path, Tweedie's identity
gives

$$
\mathbb{E}[\epsilon \mid x_t = x] = -\sigma_t\,s_t(x),
\qquad
\mathbb{E}[x_0 \mid x_t = x] = \frac{x + \sigma_t^2 s_t(x)}{\alpha_t}.
  \tag{6}
$$

(The second follows from substituting the first into $x = \alpha_t x_0 + \sigma_t\epsilon$.)
Substituting (6) into (5),

$$
u_t(x) = \frac{\dot\alpha_t}{\alpha_t}x
  + \left(\frac{\dot\alpha_t\sigma_t^2}{\alpha_t} - \dot\sigma_t\sigma_t\right) s_t(x),
$$

which is (2). Being **an affine term in $x$ plus a multiple of the score**, $u_t$ and $s_t$ convert
into each other one to one.

**Conclusion: flow matching and diffusion learn the same thing.** Flow matching regresses $u_t$ and
score-based diffusion regresses $s_t$, and (2) connects them. **There is therefore no difference in
expressiveness.** The real differences are three: (a) the implicit weighting of the loss (the
$t$-weighting of a $u_t$ regression differs from that of an $s_t$ regression); (b) the choice of path
(flow matching can use a straight path, needing fewer integration steps); and (c) the conditioning of
the numerical integration ($s_t$ diverges at small $\sigma_t$ while $u_t$ can stay bounded). When a
paper says "flow matching is better", that is a claim about (b) and (c) and **not** about
expressiveness.

**Where the assumption breaks**: Tweedie's identity (6) depends on the **Gaussian** path of (A1). On
a non-Gaussian path (discrete diffusion, a jump process) the conditional expectation is not an affine
function of the score and (2) fails. Then flow matching and score-based methods really are
**different model families**.

## Proof sketch

### R4 — the bias-variance trade-off of an action chunk

**Hypotheses** H1: the scalar plant $x_{k+1} = x_k + u_k + w_k$ with
$w_k \sim \mathcal{N}(0,\sigma_w^2)$ independent. H2: the cost is
$\mathbb{E}[x_k^2] + \lambda\,\mathbb{E}[(u_k - u_{k-1})^2]$ (tracking plus jitter). H3: every $H$
steps the policy receives an observation $z = x + n$ ($n \sim \mathcal{N}(0,\sigma_o^2)$) and emits
the chunk $(-z, 0, \dots, 0)$ — one correction, then hold. $H = 1$ is per-step replanning.
**Conclusion** C: the tracking cost is $\sigma_o^2 + \sigma_w^2(H-1)/2$, growing linearly in $H$,
while the jitter falls roughly as $1/H$, so the total cost has an interior optimum.

**Strategy**: count the in-chunk state variance as an **accumulating random walk**, and count the
jitter as a cost incurred **only at chunk boundaries**. The two terms depend on $H$ oppositely, so
the optimum is interior.

1. **The state just after a correction.** At a replanning step, applying $u_0 = -z = -(x+n)$ gives
   $x_1 = x + u_0 + w_0 = -n + w_0$, so $\mathrm{Var}[x_1] = \sigma_o^2 + \sigma_w^2$.
   **The observation noise enters the state through the correction** — that is the cost of
   replanning.
2. **Accumulation within the chunk.** The next $H-1$ steps have $u = 0$, so
   $x_{j+1} = x_j + w_j$, a random walk, with $\mathrm{Var}[x_j] = \sigma_o^2 + j\sigma_w^2$, and the
   chunk average is
   $$\frac{1}{H}\sum_{j=1}^{H}\big(\sigma_o^2 + (j-1)\sigma_w^2\big)
     = \sigma_o^2 + \sigma_w^2\frac{H-1}{2}.$$
   This **grows linearly in $H$** with slope $\sigma_w^2/2$.
3. **Jitter occurs once per chunk.** Since $u$ changes only at chunk boundaries, the jitter cost is
   incurred once every $H$ steps, so the per-step average is $\lambda K(H)/H$ with $K(H)$ the squared
   jitter per chunk. **Assuming** $K$ is independent of $H$, the total is
   $\sigma_o^2 + \sigma_w^2(H-1)/2 + \lambda K/H$, and differentiating gives
   $$H^\ast = \sqrt{\frac{2\lambda K}{\sigma_w^2}}.
     \tag{7}$$
4. **That assumption is false — so (7) overestimates.** $K(H)$ is the squared difference of
   consecutive corrections, and with a longer chunk the state drifts further in between, so **the
   correction grows**. Hence $K$ increases with $H$, the third term falls more slowly than $1/H$, and
   the optimum is **smaller** than (7). In the measurements $H^\ast_{(7)} = 10.18$ while the actual
   minimum is $H = 8$.
5. **Numerical confirmation.** With $\sigma_w^2 = 0.01$, $\sigma_o^2 = 0.04$, $\lambda = 2$ and
   $4\times10^5$ steps:

   | $H$ | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 12 | 20 |
   |---|---|---|---|---|---|---|---|---|---|
   | tracking (measured) | 0.04996 | 0.05461 | 0.06010 | 0.06459 | 0.06926 | 0.07459 | 0.08451 | 0.10417 | 0.14384 |
   | tracking (step 2 prediction) | 0.04000 | 0.04500 | 0.05000 | 0.05500 | 0.06000 | 0.06500 | 0.07500 | 0.09500 | 0.13500 |
   | jitter per step | 0.25913 | 0.09886 | 0.07359 | 0.05989 | 0.05174 | 0.04644 | 0.03976 | 0.03303 | 0.02800 |
   | **total** | 0.56822 | 0.25233 | 0.20728 | 0.18437 | 0.17273 | 0.16748 | **0.16404** | 0.17022 | 0.19983 |

   The measured slope of the tracking cost is $(0.14384-0.04996)/19 = 0.004941$, within $1.2\%$ of
   the prediction $\sigma_w^2/2 = 0.005$. (Omitted: the constant $+0.0096$ offset against the step-2
   prediction — it comes from how the correction step itself is counted in the chunk average.)

**Removing a hypothesis**: replacing the chunk of H3, $(-z, 0,\dots,0)$, by **a full planned
trajectory** (as a real policy does) removes the random walk of step 2 and slows the growth of the
tracking cost — the optimal $H$ then grows. Dropping the jitter term of H2 removes the third term and
$H = 1$ is always optimal (**so the jitter cost is the chunk's only reason to exist**). Making the
plant of H1 stable bounds the accumulation and reduces the penalty of a long chunk.

## Problem set

Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Using (3), rewrite the score-regression objective in
**$\epsilon$-prediction** form and show the two objectives differ only by a $t$-dependent weight.
Then write the $x_0$-prediction form and tabulate the weights of all three parameterizations.
*Solution sketch*: setting $s_\theta = -\epsilon_\theta/\sigma_t$ gives
$\lVert s_\theta - (-\epsilon/\sigma_t)\rVert^2 = \sigma_t^{-2}\lVert\epsilon_\theta - \epsilon\rVert^2$.
For $x_0$-prediction, the second identity of (6) gives a weight of the form
$\alpha_t^2/\sigma_t^4$.

**P2 (proof, ★★★, R1)** State the conditions justifying the exchange of differentiation and
integration in the proof of (1), and show concretely what fails when the action space is a bounded
interval $[-1,1]$ and $q_0$ places mass on the boundary.
*Strategy*: use the conditions of the dominated convergence theorem (integrability of the gradient).
Boundary mass means $q_0$ has a delta component as a measure, and then the score of $q_t$ diverges as
$1/\sigma_t^2$ at the boundary, so the training target is not square integrable.

**P3 (derivation, ★★, R3)** Derive both identities of (6) on a Gaussian path, and write (2)
explicitly for the **VP path** ($\alpha_t = \sqrt{1-t}$, $\sigma_t = \sqrt t$) and the
**straight path** ($\alpha_t = 1-t$, $\sigma_t = t$).
*Solution sketch*: $\mathbb{E}[\epsilon\mid x_t]$ is the posterior mean of a Gaussian mixture and is
$-\sigma_t$ times the score. For the VP path substitute
$\dot\alpha_t = -\frac{1}{2\sqrt{1-t}}$ and $\dot\sigma_t = \frac{1}{2\sqrt t}$. For the straight
path $\dot\alpha = -1$ and $\dot\sigma = 1$, so $u_t = -x/(1-t) + (\ldots)s_t$ is simpler — **which is
why it needs fewer integration steps**.

**P4 (numerical, ★, R2·R4)** In the setting of the reproduction task, write (a) the MSE regression
output and its distance to each mode, (b) the predicted and measured slope of the tracking cost, and
(c) the $H^\ast$ of (7) against the measured minimum, and explain the discrepancy in (c).
*Answer*: (a) output $0$, distance $1.0$ to each mode (**four times** the mode standard deviation
$0.25$). (b) predicted $\sigma_w^2/2 = 0.005$, measured $0.004941$ (a $1.2\%$ difference).
(c) $H^\ast_{(7)} = \sqrt{2\cdot2\cdot0.25913/0.01} = 10.18$ against a measured minimum of $H = 8$.
The discrepancy is that $K(H)$ grows with $H$ (step 4 of the proof sketch) — the jitter falls more
slowly than $1/H$, pulling the optimum earlier. Tolerance $10^{-3}$.

**P5 (numerical, ★★, R4)** Differentiate (7) with respect to $\lambda$ and $\sigma_o^2$ to get its
**sensitivity**, and say how the optimal chunk length changes when the observation noise quadruples.
What if the jitter weight is zero?
*Answer*: $K$ is proportional to the variance of the correction, which is linear in $\sigma_o^2$, so
$H^\ast \propto \sqrt{\lambda\sigma_o^2}/\sigma_w$. Quadrupling $\sigma_o^2$ doubles $H^\ast$ (worse
observations favour longer chunks). With $\lambda = 0$, $H^\ast = 1$ — **without a jitter cost a chunk
is a pure loss.** Tolerance: the ratio is $2.0 \pm 0.1$.

**P6 (proof, ★★, R2)** Prove (4) by orthogonal decomposition, and write the condition (relating $m$
and $\varsigma$) under which the MSE regression output lies **outside the support of the data** for a
bimodal action distribution.
*Strategy*: expand $\mathbb{E}\lVert f-a\rVert^2$ about $\mathbb{E}[a\mid o]$. Lying outside the
support means the $k\sigma$ intervals of the two modes do not overlap, i.e. $m > k\varsigma$ — in the
reproduction task $m/\varsigma = 4$.

**P7 (implementation, ★★, R1·R2·R3·R4)** Write the reproduction task. Requirements: the analytic
score of a Gaussian mixture, RK2 integration of the probability-flow ODE, and the chunk simulator.
*Rubric*: (a) the numbers of criteria 1–3 agree within tolerance; (b) you show the mode-mean error
falls as the ODE steps go from $500$ to $2000$; (c) you state explicitly that **no training was
done** (the score is closed form); (d) you show the mode standard deviation grows when the lower
bound on $t$ is raised from $10^{-4}$ to $10^{-2}$ (a numerical confirmation of failure mode 2 of R1).

**P8 (counterexample, ★★, R2)** Construct a case where "a generative policy is always better on
multimodal data" fails: exhibit a setting in which the action distribution is bimodal but **neither
mode succeeds at the task while their average does**. Then give the standard opposite example (going
around an obstacle on either side) and write that **which case you are in is decided by the task, not
the data**.
*Property checklist*: the former is "two clumsy demonstrators whose errors point opposite ways" — the
average cancels the error. The latter is an average that drives into the obstacle. Note that what
separates the two is the **convexity** of the success set.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions.

1. **Chi et al., "Diffusion Policy: visuomotor policy learning via action diffusion" (2023, RSS)** —
   role: `frontier`. <https://arxiv.org/abs/2303.04137> (§3–4)
   *Why read it*: the objective of R1 and the chunking of R4 are assembled **in the same paper**. Look
   in particular at the design decision to emit actions in chunks and the justification for the chunk
   length.
   Extra questions: (a) which parameterization ($\epsilon$/$x_0$/$v$) is used and is the choice
   justified? (b) how is the chunk length chosen, and is the trade-off of R4 made explicit?
   (c) are tasks that genuinely need multimodality distinguished from those that do not (P8)?
2. **Zhao et al., "Learning fine-grained bimanual manipulation with low-cost hardware (ACT)"
   (2023, RSS)** — role: `frontier`. <https://arxiv.org/abs/2304.13705>
   *Why read it*: a control group that uses **chunks without a generative model** (a variational
   autoencoder plus a transformer). It shows that the trade-off of R4 exists independently of
   diffusion.
   Extra questions: (a) is the relation between chunk length and performance reported? (b) how is
   multimodality handled, and does that avoid (4) of R2? (c) are the failure modes related to the
   chunk length?
3. **Black et al., "$\pi_0$: a vision-language-action flow model for general robot control"
   (2024)** — role: `frontier`. <https://arxiv.org/abs/2410.24164>
   *Why read it*: a large-scale policy using flow matching. Contrast the paper's design decisions
   with R3's claim that there is no difference in expressiveness, only in path, weighting and
   numerics.
   Extra questions: (a) is flow matching chosen for reason (b) or (c), or is expressiveness claimed?
   (b) is the relation between the number of integration steps and latency reported? (c) how are the
   chunk length and the replanning period set?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation or one figure. (4) what is guaranteed theoretically,
and **what is not**? (5) the independent and dependent variables and the baselines, and were the
baselines tuned fairly? (6) does the metric match the claim, and are variance and seeds reported?
(7) what is missing for reproduction? (8) if the result were wrong, which assumption would you doubt
first? (9) computational and memory complexity, and real-time feasibility. (10) what would you change
to go beyond this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 10 minutes in total, under 1 GB
of memory. numpy only. **No training** — the score of a Gaussian mixture is written in closed form,
so neither a network nor a dataset is needed. The blueprint's "retrain on a small public dataset"
needs a GPU and data, so the task instead **verifies the same theory without training**.

**Input data (given by the lesson).**

*(a) Mode collapse versus score sampling.* The target distribution is
$\frac12\mathcal{N}(-1, 0.25^2) + \frac12\mathcal{N}(+1, 0.25^2)$. The path is of VP form
$\alpha_t = \sqrt{1-t}$, $\sigma_t = \sqrt t$, so $\alpha_t^2 + \sigma_t^2 = 1$. The diffused
distribution $q_t$ is a Gaussian mixture with a closed-form score. Integrate the probability-flow ODE
(2) from $t = 1 - 10^{-5}$ to $t = 10^{-4}$ by RK2 in 2000 steps, starting from $2\times10^4$ draws
from $\mathcal{N}(0,1)$. Seed 0.

*(b) Chunk length.* The H1–H3 setting of the R4 proof sketch with $\sigma_w^2 = 0.01$,
$\sigma_o^2 = 0.04$, $\lambda = 2$, $4\times10^5$ steps and seed 1, for
$H \in \{1,2,3,4,5,6,8,12,20\}$.

**Acceptance criteria — all four must hold.**

1. **Mode recovery (a joint check of R1 and R3)** — the sampler gives
   $P[\text{left mode}] = 0.502 \pm 0.015$, left mode mean $-0.997 \pm 0.01$ and standard deviation
   $0.248 \pm 0.01$, right mode mean $+1.005 \pm 0.01$ and standard deviation $0.245 \pm 0.01$, with
   at least $0.99$ of the samples within $3\sigma$ of a mode (measured $0.9980$). **Passing this
   verifies the objective of (1) and the affine relation of (2) together** — the analytic score put
   into (2) and integrated reproduced the target distribution.
2. **The collapse of MSE regression (checking R2)** — confirm by computation that the $L^2$ minimizer
   is $0$ and the distance to each mode is $1.0$, i.e. **four times** the mode standard deviation.
   State that it falls within $3\sigma$ of neither mode.
3. **The chunk trade-off (checking R4)** — reproduce the table of step 5 of the proof sketch. The
   tracking cost increases monotonically in $H$ with a least-squares slope of
   $0.00494 \pm 0.0005$ (predicted $\sigma_w^2/2 = 0.005$), the jitter per step decreases
   monotonically, and **the total cost is minimal at $H = 8$** (total $0.16404 \pm 0.005$).
4. **The overestimate of the closed form (checking step 4 of R4)** — show that the
   $H^\ast = \sqrt{2\lambda K/\sigma_w^2} = 10.18 \pm 0.1$ of (7) (with $K = 0.25913$, the jitter per
   step at $H=1$) is **larger** than the measured minimum $H = 8$, and write one paragraph on the
   reason ($K(H)$ grows with $H$). Present $K(H)$ measured at each $H$
   (measured: jitter per step × $H$ = $0.259, 0.198, 0.221, 0.240, 0.259, 0.279, 0.318, 0.396,
   0.560$). It **dips once at $H = 2$ and then increases monotonically**, exceeding the $H = 1$ value
   already at $H \ge 5$ — and since (7) fixes $K$ at its $H=1$ value, it overestimates.

**Baselines.** (a) The analytic parameters of the target distribution — criterion 1. (b) The
conditional expectation (4) — criterion 2. (c) The analytic tracking cost of step 2 of the proof
sketch — criterion 3. (d) The closed form (7) — criterion 4.

**Failure table**

| Symptom | Cause | How to check |
|---|---|---|
| the samples collect in one mode | the ODE was integrated in the direction of increasing $t$ (it must be reversed) | check that $t$ decreases from 1 to 0 |
| the mode standard deviation exceeds the target | the lower bound on $t$ was set too large (order $10^{-2}$) | lower it to $10^{-4}$ and check the standard deviation converges to 0.25 |
| the samples bunch near 0 | the sign of the score is wrong | check that at large $t$, where $q_t$ is unimodal, the samples do collect at the origin (which is correct) |
| the tracking cost is independent of $H$ | $u$ was updated within the chunk (it is not open loop) | print $u$ and check it is constant within a chunk |
| the total cost is minimal at $H=1$ | the jitter term was left out of the cost | check that with $\lambda = 0$, $H=1$ is indeed optimal (that is correct) |
| the jitter per step is exactly $K/H$ | the jitter was **assumed** constant per chunk rather than measured | check that the actual $(u_k - u_{k-1})^2$ is accumulated at each $H$ |

## Open problems

- **(open problem) A principled choice of chunk length** — R4 establishes that **an interior optimum
  exists** but gives no way to choose it **in advance** for a real task. Equation (7) overestimates
  because of the $H$-dependence of $K(H)$ (criterion 4), and a real policy's chunk is a full planned
  trajectory rather than "correct once and hold", so the random-walk model of step 2 does not apply
  either. Current approach: empirical search
  ([Chi et al. 2023](https://arxiv.org/abs/2303.04137),
  [Zhao et al. 2023](https://arxiv.org/abs/2304.13705)). What is missing: a procedure predicting $H$
  from the task's disturbance and observation statistics.
- **(open problem) Safety verification of generative policies** — since the policy is a distribution,
  the "worst action" lives in its tail and there is no way to bound that tail. Appending the safety
  filter of `c3-cbf-safety-filter` is the standard workaround, but when the filter intervenes the
  distribution changes and **the learned multimodality breaks** (the filter passes only one mode).
  Current approaches: filter plus resampling, conservative action limits. What is missing: a
  projection that guarantees safety while preserving the distribution.
- **(open problem) Deciding when multimodality is needed** — as the failure mode of R2 and P8 show,
  whether the average is fatal or beneficial depends on the **convexity** of the success set, and
  there is no way to decide that from data. At present there are only post-hoc observations that
  "using diffusion helped". What is missing: a criterion deciding **in advance**, from the data and
  the task definition, whether a generative model is needed.

## Concept check

Run `rc quiz s2-generative-policies`. Concept checking only; the real work is the problem set and the
reproduction task.

The six items cover: the key step making denoising score matching equivalent; the minimizer of an
$L^2$ regression on a bimodal distribution; whether flow matching is more expressive; how the
tracking cost grows with the chunk length; what is true of action chunks; and Tweedie's identity.

## How to study this stage

1. **Write "why a distribution" as one paragraph (20 min)** — that the MSE minimizer is the
   conditional expectation, and that on bimodal data it can lie outside the support. That paragraph
   is the entire motivation of this lesson. Solving P6 alongside fixes the condition
   $m > k\varsigma$ in your hands.
2. **Memorize the DSM equivalence in four lines (70 min)** — memorize only the cross-term computation
   of the R1 proof: cancel the denominator → differentiate under the integral → integrate over $x_0$ →
   the gradient of the marginal. Confirming that **Gaussianity is not needed for the equivalence**
   (only for convenience) completes the understanding. Use P1 to tabulate the three
   parameterizations' weights.
3. **Derive the velocity field with Tweedie (50 min)** — do P3. Put (6) into (5) to get (2), and write
   it explicitly for the VP and the straight path. Deriving **"flow matching and diffusion learn the
   same thing"** yourself lets you classify papers' claims.
4. **Run the sampler without training (50 min)** — part (a) of the reproduction task. Write the
   mixture's score in closed form and integrate the ODE; that is all. **The experience of verifying
   theory without a neural network** is the purpose of this task, and passing criterion 1 confirms R1
   and R3 at once.
5. **Measure the chunk trade-off (45 min)** — part (b). See the tracking-cost slope match
   $\sigma_w^2/2$, find the interior optimum, and confirm **why the closed form overestimates** by
   measuring $K(H)$ (criterion 4). That paragraph is this lesson's second key artifact.
6. **Three papers (130 min)** — Diffusion Policy → ACT → $\pi_0$. The first is diffusion plus
   chunking, the second is chunking **without** diffusion, and the third is flow matching at scale.
   The goal of the reading is to organize all three under the frame "chunking and generative modelling
   are two independent choices".
7. **Problem set (160 min)** — P4, P5 and P7 first, then P1 and P3, then P2, P6 and P8 with whatever
   time remains. P2 (the conditions for differentiating under the integral) is the hardest and
   explains the boundary-mass problem.

**Passing bar**: you can compute the cross term of (1) from a blank page, derive (2) from (6), have
code satisfying the four criteria of the reproduction task plus the interpretation paragraph of
criterion 4, and explain that "chunking and generative modelling are independent choices". You have
notes on all three papers.
