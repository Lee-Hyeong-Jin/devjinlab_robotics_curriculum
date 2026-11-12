---
id: c8-model-based-world-models
lang: en
title: Model-based RL and world models
summary: >-
  Derive how model error propagates into value error, both as an exact identity and as the
  simulation lemma, and see why the bound carries $(1-\gamma)^{-2}$. Then show the bias by which
  Dyna-style updates converge to the model's own optimum, and reproduce numerically the
  performance-bias trade-off in the branched rollout length $k$. The lesson closes by deriving the
  training objective (ELBO) of a latent world model and constructing a case where that objective
  disagrees with value accuracy.
objectives:
  - Derive the exact identity linking model error to value error and obtain the simulation lemma from it.
  - Point out which step produces the $(1-\gamma)^{-2}$ in the bound and measure numerically how loose the bound is.
  - Show that the fixed point of Dyna-style updates is the model's optimal value and quantify that bias.
  - Separate experimentally how the optimal branched rollout length $k$ depends on critic noise and model quality.
  - Derive the ELBO of a sequential latent variable model and explain what each term penalizes.
  - Construct a model with higher held-out log-likelihood but worse value error.
tags: [model-based-rl, world-models, simulation-lemma, dyna, elbo, research]
---

# Model-based RL and world models

## Setup and notation

The operator notation of `c8-mdp-pomdp-bellman` and the weighted norm of `c8-value-based-rl` carry
over. Additional **recommended** background:

- Linear algebra: the Neumann series for $(I - \gamma P)^{-1}$ and
  $\lVert(I-\gamma P)^{-1}\rVert_\infty \le 1/(1-\gamma)$.
- Probability: the relation between total variation and $\ell_1$ distance, concentration of the
  multinomial, Jensen's inequality.
- Variational inference: the ELBO, KL divergence, the reparameterization trick
  (`r0-estimation-theory`).

Added notation:

| Symbol | Meaning |
|---|---|
| $\hat{P}, \hat{r}$ | the learned model; the true model is $P, r$ |
| $\epsilon_P$ | transition error, $\epsilon_P = \max_{s,a} \lVert \hat{P}(\cdot\mid s,a) - P(\cdot\mid s,a)\rVert_1$ |
| $\epsilon_r$ | reward error, $\epsilon_r = \max_{s,a}\lvert \hat{r}(s,a) - r(s,a)\rvert$ |
| $\hat{V}^\pi, \hat{Q}^\pi$ | values in the model MDP; values in the true MDP are $V^\pi, Q^\pi$ |
| $k$ | branched rollout length (how many model steps before bootstrapping with the critic) |
| $V_\varphi$ | the critic; here simulated as $V^\* + \mathcal{N}(0,\sigma_V^2)$ |
| $z_t$ | latent state; $o_t$ is the observation, $q(z_t\mid\cdot)$ the inference distribution, $p(z_t \mid z_{t-1},a_{t-1})$ the prior |
| $R_{\max}$ | $\max_{s,a}\lvert r(s,a)\rvert$, hence $\lVert V^\pi\rVert_\infty \le R_{\max}/(1-\gamma)$ |

Every bound in this lesson comes from the single fact that **the norm of $(I-\gamma P)^{-1}$ is
bounded by $1/(1-\gamma)$**. Before starting, check that you can write that in one line with the
Neumann series (item D1 of the self-diagnosis in `c8-mdp-pomdp-bellman`).

## Key results

The bracket gives the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (model error → value error: the exact identity and the simulation lemma) [D3]** — for any
  policy $\pi$ the **exact identity**
  $$
  \hat{V}^\pi - V^\pi = \big(I - \gamma \hat{P}^\pi\big)^{-1}
    \Big[\big(\hat{r}^\pi - r^\pi\big) + \gamma\big(\hat{P}^\pi - P^\pi\big) V^\pi\Big] \tag{1}
  $$
  holds, and taking norms gives
  $$
  \big\lVert \hat{V}^\pi - V^\pi \big\rVert_\infty \;\le\;
    \frac{\epsilon_r}{1-\gamma} \;+\; \frac{\gamma\,\epsilon_P\,R_{\max}}{(1-\gamma)^2} . \tag{2}
  $$
  The $(1-\gamma)^{-2}$ is **the product of the $1/(1-\gamma)$ from $(I-\gamma\hat{P}^\pi)^{-1}$ and
  the $1/(1-\gamma)$ from $\lVert V^\pi\rVert_\infty$**. (2) is true but very loose — the
  reproduction task measures the actual error at around $10^{-3}$ of the bound.
- **R2 (the bias of Dyna-style updates) [D2]** — updating only from model samples converges to the
  fixed point of the model Bellman operator $\hat{T}^\*$, so the solution is $\hat{Q}^\*$ with bias
  $$
  \big\lVert \hat{Q}^\* - Q^\* \big\rVert_\infty \;\le\;
    \frac{\epsilon_r}{1-\gamma} \;+\; \frac{\gamma\,\epsilon_P\,R_{\max}}{(1-\gamma)^2} \tag{3}
  $$
  — the **same order** as (2), and a bias that **does not vanish with more real data unless the
  model is fixed**. Moreover $\epsilon_P$ is small only on the distribution the data came from, so
  as the policy improves and the distribution shifts, the bias grows again.
- **R3 (the performance-bias trade-off in branched rollouts) [D2]** — rolling the model $k$ steps
  and bootstrapping with the critic $V_\varphi$ gives a value error of roughly
  $$
  \mathrm{err}(k) \;\lesssim\; \underbrace{\gamma^k \,\sigma_V}_{\text{decay of critic error}}
    \;+\; \underbrace{\frac{k}{1-\gamma}\,c\,\epsilon_P}_{\text{accumulation of model error}} \tag{4}
  $$
  (model error accumulates **linearly** in the rollout length — the total variation of the
  $k$-step distribution is of order $k\epsilon_P$), and the sum has an interior minimum
  $k^\star$. That $k^\star$ **increases monotonically with the critic noise $\sigma_V$** (confirmed
  in the reproduction task over 5 model qualities × 4 noise levels × 20 seeds). (4) is an
  **empirical decomposition** simplifying the bound of MBPO §4, not a theorem — its prediction in
  the $\epsilon_P$ direction actually **fails** (problem P5).
- **R4 (the training objective of a latent world model) [D2]** — the log-likelihood of a sequential
  latent variable model is lower-bounded by
  $$
  \log p(o_{1:T}\mid a_{1:T}) \;\ge\; \sum_{t=1}^{T}
    \mathbb{E}_{q}\big[\log p(o_t \mid z_t)\big]
    - \mathbb{E}_{q}\Big[D_{\mathrm{KL}}\big(q(z_t \mid o_{\le t}, a_{<t}) \,\big\Vert\,
      p(z_t \mid z_{t-1}, a_{t-1})\big)\Big] \tag{5}
  $$
  and this is the training objective of the PlaNet and Dreamer family. The first term demands
  **observation reconstruction**, the second **predictability**.
- **R5 (objective mismatch: likelihood and value give different orderings) [D2]** — maximizing (5)
  is not the same as reducing the $\epsilon_P$ of (2). Constructively, a model with **higher**
  held-out log-likelihood can have a value error that is **more than twice as large**
  (reproduction criterion 4). The reason is that likelihood weighs errors in every direction
  equally while the value sees only the component along $V^\pi$ — the bracket of (1) is an
  **inner product** $(\hat{P}-P)V^\pi$.

## Derivation

### R1 — from the exact identity to the bound

$\hat{V}^\pi$ and $V^\pi$ each satisfy their own Bellman equation:

$$
\hat{V}^\pi = \hat{r}^\pi + \gamma \hat{P}^\pi \hat{V}^\pi, \qquad
  V^\pi = r^\pi + \gamma P^\pi V^\pi .
$$

Subtract, and the only trick is to **add and subtract** $\gamma\hat{P}^\pi V^\pi$:

$$
\hat{V}^\pi - V^\pi
  = (\hat{r}^\pi - r^\pi) + \gamma \hat{P}^\pi \hat{V}^\pi - \gamma P^\pi V^\pi
  = (\hat{r}^\pi - r^\pi) + \gamma \hat{P}^\pi (\hat{V}^\pi - V^\pi)
    + \gamma(\hat{P}^\pi - P^\pi) V^\pi .
$$

Moving $\gamma\hat{P}^\pi(\hat{V}^\pi - V^\pi)$ to the left gives
$(I - \gamma\hat{P}^\pi)(\hat{V}^\pi - V^\pi) = (\hat{r}^\pi - r^\pi) + \gamma(\hat{P}^\pi - P^\pi)V^\pi$,
and $(I - \gamma\hat{P}^\pi)$ is invertible because $\hat{P}^\pi$ is a stochastic matrix. That is
(1).

**The bound (2).** Bound three pieces separately.

1. $\big\lVert (I-\gamma\hat{P}^\pi)^{-1}\big\rVert_\infty
   = \big\lVert \sum_{t\ge0}\gamma^t(\hat{P}^\pi)^t\big\rVert_\infty \le \sum_{t\ge0}\gamma^t
   = \frac{1}{1-\gamma}$ (a stochastic matrix has $\infty$-norm 1).
2. $\lVert \hat{r}^\pi - r^\pi\rVert_\infty \le \epsilon_r$ (by definition).
3. $\big\lvert \big[(\hat{P}^\pi - P^\pi)V^\pi\big](s)\big\rvert
   \le \lVert \hat{P}^\pi(\cdot\mid s) - P^\pi(\cdot\mid s)\rVert_1 \lVert V^\pi\rVert_\infty
   \le \epsilon_P \cdot \frac{R_{\max}}{1-\gamma}$ (Hölder).

Substituting into (1) gives (2). **The $(1-\gamma)^{-2}$ arises in exactly one place: the product
of the $1/(1-\gamma)$ of step 1 with the $1/(1-\gamma)$ of step 3.**

**Where the assumptions break.** The looseness comes mainly from step 3 using
$\lVert V^\pi\rVert_\infty$ in Hölder's inequality. In reality $(\hat{P}-P)V^\pi$ is an **inner
product**, so a model error orthogonal to $V^\pi$ contributes nothing. A tighter form replaces
$\lVert V^\pi\rVert_\infty$ with the **span** $\tfrac12(\max V - \min V)$ and measures $\epsilon_P$
in total variation, but even that is a worst-state quantity and remains loose. The reproduction
task measures the ratio of actual error to bound at $6\times10^{-4}$–$5\times10^{-3}$ — **the bound
is correct but cannot be used as a design guide.**

### R2 — the bias of Dyna

Dyna fits a model on real data and updates values from **imagined transitions drawn from the
model**. In the limit of using only imagined transitions, the update iterates the model Bellman
optimality operator
$(\hat{T}^\*v)(s) = \max_a[\hat{r}(s,a) + \gamma\sum_{s'}\hat{P}(s'\mid s,a)v(s')]$. R1 of
`c8-mdp-pomdp-bellman` applies to the model MDP as well, so the limit is $\hat{V}^\*$ and Dyna's
solution is **the model's optimum**. The difference between the two optimal values follows from the
1-Lipschitz property of $\max$:

$$
\lVert \hat{V}^\* - V^\*\rVert_\infty
  \le \frac{1}{1-\gamma}\Big(\epsilon_r + \gamma\,\epsilon_P \frac{R_{\max}}{1-\gamma}\Big), \tag{6}
$$

the same order as (2). The point is that **this error depends only on model error, not on how much
real data was collected**. Mixing in real data (real ratio $\beta$) reduces the bias in proportion
to $\beta$, but it reduces the model's sample-efficiency gain by the same amount — that trade-off
is MBPO's design variable.

**Why distribution shift is worse.** $\epsilon_P$ is small only on the data distribution $\mu$ the
model was trained on. As the policy improves, the visitation distribution moves toward
$d^{\pi_{\text{new}}}$, and wherever $\mu$ does not cover, $\hat{P}$ may be arbitrarily wrong. But
policy optimization seeks out **wherever the model says things are good**, so it **actively
exploits** the regions with large error (model exploitation). This is the classic failure mode of
model-based RL and has the same structure as the extrapolation error of `c8-offline-rl`.

**Where the assumptions break.** (6) measures $\epsilon_P$ as a maximum over **all** $(s,a)$, so a
single point where the model is wrong inflates the bound. Measuring a $d^\pi$-weighted average
instead gives a smaller bound, but then **it guarantees nothing** under model exploitation — the
policy moves precisely so as to break the average.

### R3 — the rollout length $k$

The estimator for a $k$-step model rollout plus critic bootstrap is

$$
Q_k(s,a) = \mathbb{E}_{\hat{P}}\Big[\sum_{t=0}^{k-1}\gamma^t \hat{r}_t
  + \gamma^k V_\varphi(s_k) \,\Big|\, s_0=s, a_0=a\Big].
$$

Separate the two error sources. The critic error $V_\varphi - V^\*$ is **damped** by $\gamma^k$,
while model error **accumulates** across $t = 0,\dots,k-1$. Together that is (4). $k=0$ is pure
critic (never trust the model) and $k\to\infty$ is pure model (never trust the critic); the optimum
is usually in between.

**Why the accumulation is linear.** Each model step adds about $\epsilon_P$ of total-variation
error to the state distribution, so after $k$ steps it is of order $k\epsilon_P$. When that
distribution error enters the value it is multiplied by $R_{\max}/(1-\gamma)$, giving the second
term of (4). The **linearity in $k$** matters — writing it as a saturating
$(1-\gamma^k)/(1-\gamma)$ would give both terms the same $\gamma^k$ factor, making
$\mathrm{err}(k)$ monotone and destroying the interior minimum.

Differentiating (4) in $k$ (treating $\gamma^k$ as continuous),
$-\ln(1/\gamma)\,\gamma^k \sigma_V + c\epsilon_P/(1-\gamma) = 0$, so

$$
k^\star \;\approx\; \frac{1}{\ln(1/\gamma)}\,
  \ln\!\frac{\sigma_V\,(1-\gamma)\,\ln(1/\gamma)}{c\,\epsilon_P}
  \quad (\text{where this is positive}). \tag{7}
$$

So $k^\star$ grows **logarithmically** in $\sigma_V$ and shrinks **logarithmically** in
$\epsilon_P$. In the reproduction task the monotone increase in $\sigma_V$ is confirmed at all five
model qualities, while the $\epsilon_P$ direction is **not** — changing the sample count in a
tabular model does not move $k^\star$ monotonically (problem P5 asks why). (7) is a property of the
**approximate model** (4), not a theorem, and watching the prediction fail on one side is the
experimental point of this lesson.

### R4 — the ELBO of a latent world model

For observations $o_{1:T}$, actions $a_{1:T}$ and latents $z_{1:T}$, take the generative model
$p(o_{1:T}, z_{1:T}\mid a_{1:T}) = \prod_t p(z_t\mid z_{t-1},a_{t-1})\,p(o_t\mid z_t)$ and the
inference distribution $q(z_{1:T}\mid o_{1:T},a_{1:T}) = \prod_t q(z_t\mid o_{\le t}, a_{<t})$
(filtering form). Insert $q$ into the log-likelihood and apply Jensen:

$$
\log p(o_{1:T}\mid a_{1:T})
  = \log \mathbb{E}_{q}\!\left[\frac{p(o_{1:T},z_{1:T}\mid a_{1:T})}{q(z_{1:T}\mid o_{1:T},a_{1:T})}\right]
  \;\ge\; \mathbb{E}_{q}\!\left[\log \frac{p(o_{1:T},z_{1:T}\mid a_{1:T})}{q(z_{1:T}\mid \cdot)}\right].
$$

Splitting numerator and denominator per time step gives

$$
\mathbb{E}_q\Big[\sum_t \log p(o_t\mid z_t) + \log p(z_t\mid z_{t-1},a_{t-1}) - \log q(z_t\mid o_{\le t},a_{<t})\Big],
$$

and collecting the last two terms into a per-step KL gives (5). **What each term means**: the first
demands that observations be recoverable from the latent state (information preservation); the
second demands that the inference distribution be **predictable** (close to the prior). Modelling
the reward as well adds a $\log p(r_t\mid z_t)$ term to the first — which is what the Dreamer family
does.

**Where the assumptions break.** (5) demands **observation reconstruction**, so high-dimensional
background irrelevant to the task (swaying leaves, changing light) consumes capacity. Dropping the
reconstruction term and keeping only reward and value prediction is no longer an ELBO, so the lower
bound guarantee is gone. More fundamentally, maximizing (5) is a **different problem** from reducing
the $\epsilon_P$ of (2) — which is the next result.

### R5 — objective mismatch

Look again at the bracket of (1). Model error enters the value through
$\gamma(\hat{P}^\pi - P^\pi)V^\pi$, which is an **inner product** of the error vector with $V^\pi$.
So if $\hat{P} - P$ is orthogonal to $V^\pi$, the value is exact no matter how wrong the model is.
Conversely a small error aligned with $V^\pi$ produces a large value error.

Log-likelihood knows **nothing** about this directional structure. Pushing $\hat{P}$ along the
centred value direction $c = (V^\pi - \bar{V}^\pi)/\lVert\cdot\rVert$ can raise the likelihood while
increasing the value error. The reproduction task measures the following (seed 0, $n=200$):

| Model | change in held-out log-likelihood | value error |
|---|---|---|
| base $\hat{P}$ | — | $0.0472$ |
| $\hat{P} + 0.02\,u$ ($u \perp c$) | $+8{,}931$ | $0.0370$ |
| $\hat{P} + 0.004\,c$ | $+24{,}060$ | $0.0957$ |

The model whose likelihood rose **more** has a value error $2.6$ times worse. This is the simplest
form of "objective mismatch".

**Where the assumptions break.** The argument presumes that $V^\pi$ is **known**. In practice it is
not, so the "direction aligned with the value" cannot be identified in advance — which is why
likelihood became the convention. That is exactly why value-aware model learning is an open problem.

## Proof sketch

### R1 — the simulation lemma [D3]

**Hypotheses** H1: $\lvert r\rvert, \lvert\hat{r}\rvert \le R_{\max} < \infty$. H2: $\gamma<1$.
H3: $\hat{P}(\cdot\mid s,a)$ is a probability distribution. H4: $\epsilon_P, \epsilon_r$ finite.
**Conclusions** C1: the identity (1). C2: the bound (2).

**Strategy**: in the difference of the two Bellman equations, **add and subtract**
$\gamma\hat{P}^\pi V^\pi$ to gather the unknown $(\hat{V}^\pi - V^\pi)$ on one side; then bound each
piece with the Neumann series and Hölder.

1. Write both Bellman equations and take the difference. Uses: that a fixed point exists in both
   MDPs (R1 of `c8-mdp-pomdp-bellman`, H2 and H3).
2. Add and subtract $\gamma\hat{P}^\pi V^\pi$ to obtain
   $(I-\gamma\hat{P}^\pi)(\hat{V}^\pi - V^\pi)$ → C1. **This one line is the whole lemma.**
3. Bound the norm of $(I-\gamma\hat{P}^\pi)^{-1}$ by $1/(1-\gamma)$ with the Neumann series.
   Uses: H3.
4. $\lVert V^\pi\rVert_\infty \le R_{\max}/(1-\gamma)$ and Hölder → C2. Uses: H1 and H4.

**Delete one hypothesis**: if $\hat{P}$ is not a probability distribution in H3 (an unnormalized
network output), $\lVert\hat{P}^\pi\rVert_\infty = 1$ fails in step 3 and even the invertibility of
$(I-\gamma\hat{P}^\pi)$ is not guaranteed — omitting the softmax normalization in an
implementation makes **the identity (1) itself meaningless**, not just the bound. Dropping H1 makes
$R_{\max}$ infinite in step 4 and C2 vacuous (C1 still holds).

Omitted: the continuous-state version follows by replacing $\ell_1$ with a total-variation measure
and sums with integrals. See the lemma in Kearns & Singh 2002 §3.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Re-derive (2) using the **span**
$\mathrm{sp}(V^\pi) = \max_s V^\pi(s) - \min_s V^\pi(s)$ in place of $\lVert V^\pi\rVert_\infty$.
State how the constant changes and why the span version is tighter.
*Solution sketch*: since $\sum_{s'}(\hat{P}-P)(s') = 0$, for any constant $c$ we have
$(\hat{P}-P)V = (\hat{P}-P)(V - c\mathbf{1})$. Choosing $c = \tfrac12(\max V+\min V)$ makes
$\lVert V - c\mathbf{1}\rVert_\infty = \tfrac12\mathrm{sp}(V)$, so the factor in step 3 changes from
$R_{\max}/(1-\gamma)$ to $\tfrac12\mathrm{sp}(V^\pi)$. In an MDP whose rewards are nearly constant
that difference is tens of times.

**P2 (proof, ★★★, R2·R3)** Write the equation satisfied by the fixed point of an update that mixes
real and model data in the ratio $\beta : 1-\beta$, and bound how the error of that solution varies
with $\beta$. Check what the limits $\beta \to 1$ and $\beta \to 0$ become.
*Strategy and key inequality*: show the mixed operator $T_\beta = \beta T^\* + (1-\beta)\hat{T}^\*$
is still a $\gamma$-contraction (a convex combination of contractions), then bound the difference of
its fixed point from $Q^\*$ via
$\lVert T_\beta Q^\* - Q^\*\rVert \le (1-\beta)\lVert \hat{T}^\* Q^\* - T^\* Q^\*\rVert$ and divide
by the contraction factor. The expansion is withheld.

**P3 (numerical, ★, R1)** With $\gamma = 0.95$, $R_{\max} = 1$, $\epsilon_r = 0.14$ and
$\epsilon_P = 1.31$, compute the bound (2). Then, if the measured error was $0.309$, compute how
many times looser the bound is.
*Answer*: the bound is $0.14/0.05 + 0.95\cdot1.31\cdot(1/0.05)/0.05 = 2.8 + 497.8 = 500.6$
(tolerance $0.5$; computing $R_{\max}/(1-\gamma) = 20$ first gives
$0.95\cdot1.31\cdot20/0.05 = 497.8$). The looseness is $500.6/0.309 \approx 1.6\times10^3$.
Check: reduce $\epsilon_P$ tenfold and verify that the bound shrinks almost tenfold (i.e. that the
$\epsilon_P$ term dominates).

**P4 (implementation, ★★, R1·R3)** On a tabular MDP, verify the **identity** (1) numerically and
plot the value-error curve of the $k$-step rollout for four values of $\sigma_V$.
*Rubric*: ⓐ the difference of the two sides of (1) is at most $10^{-12}$; ⓑ the bound (2) bounds the
actual error **from above**; ⓒ $k^\star$ is shown to increase monotonically in $\sigma_V$, averaged
over 20 seeds; ⓓ the limits $k=0$ and $k\to\infty$ are confirmed in code to be pure critic and pure
model; ⓔ the model is built by plain count estimation with row normalization (omitting the
normalization violates hypothesis H3 of R1).

**P5 (counterexample, ★★, R3)** (7) predicts that $k^\star$ decreases monotonically in
$\epsilon_P$, yet varying the sample count $n$ in a tabular model **does not** exhibit that
monotonicity. Explain why, and propose an experimental design in which it would appear.
*Property checklist*: ⓐ the limiting error at $k\to\infty$ is already small by (6), so the
accumulated model-error term never overtakes the critic term; ⓑ the $c\epsilon_P$ in (4) is a
**worst-case** error while a rollout stays, on average, in well-modelled regions; ⓒ in the tabular
case $\hat{P}$ is distributed unbiasedly around the truth so errors partly cancel; ⓓ to see the
monotonicity, use a model with **systematic bias** (e.g. $\hat{P}$ pushed in one direction) or start
rollouts outside the data distribution.

**P6 (paper, ★★, R3·R4·R5)** Read MBPO (§4–5) and DreamerV3 (§2–3) and write, in at most three
sentences each: (i) which term of MBPO's performance bound carries $k$ and which term of (4) it
corresponds to; (ii) how the objective of DreamerV3 modifies which term of (5); (iii) three pieces
of information missing for reproduction in the two papers.
*Grading rubric*: (i) passes if it distinguishes the model-error term entering **linearly** in the
rollout length from the policy-shift term damped by $\gamma^{k}$. (ii) passes if it names the added
reward and value prediction terms and the reconstruction weighting or normalization (symlog, KL
balancing). (iii) three of: model ensemble size, replay ratio, the $k$ schedule, seeds,
normalization statistics. Writing only "it performs well" fails.

**P7 (derivation, ★★, R4)** Derive (5), then state how the bound changes if the inference
distribution is replaced by the **smoothing** form $q(z_t\mid o_{1:T},a_{1:T})$, and why planning
needs the filtering form.
*Solution sketch*: Jensen holds for any $q$, so the bound still holds and in fact becomes tighter
(smoothing uses more information). But at planning time $t$ there are no future observations, so the
smoothing distribution **cannot be executed** — when the information sets of training and execution
differ, the model is fitted to a state estimate that cannot be run.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions
(`lesson-standard.md` §5).

1. **Kearns & Singh, "Near-optimal reinforcement learning in polynomial time" (2002, Machine
   Learning)** — role: `seminal`. <https://doi.org/10.1023/A:1017984413808>
   Why read it: the simulation lemma of R1 is a lemma of this paper. Read §3 only.
   Extra questions: ⓐ the authors' lemma has different constants from (2) — which assumption
   accounts for the difference? ⓑ how does the criterion by which $E^3$ switches between
   exploration and exploitation connect to model error?
2. **Janner, Fu, Zhang & Levine, "When to trust your model: model-based policy optimization" (2019,
   NeurIPS)** — role: `standard`. <https://arxiv.org/abs/1906.08253> (§4–5)
   Why read it: it treats the $k$ trade-off of R3 both as a theorem and experimentally.
   Extra questions: ⓐ in the performance bound, identify the term that **increases** and the term
   that **decreases** as $k$ grows. ⓑ is the $k$ the actual algorithm uses the one the theorem
   recommends, and if not, why?
3. **Hafner, Pasukonis, Ba & Lillicrap, "Mastering diverse domains through world models" (2023,
   arXiv)** — role: `frontier`. <https://arxiv.org/abs/2301.04104> (§2–3)
   Why read it: a case study of how the objective of (5) is modified and stabilized at scale.
   Extra questions: ⓐ which term of (5) do the symlog transform and KL balancing touch, and does the
   lower-bound guarantee survive? ⓑ what does the claim of solving diverse domains with a single
   hyperparameter set guarantee, and what does it not?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation? (4) what is guaranteed and **what is not**?
(5) independent and dependent variables, and the baselines — were they tuned fairly? (6) does the
metric match the claim, and are variance and seeds reported? (7) what information needed for
reproduction is missing? (8) if the result were wrong, which assumption would you doubt first?
(9) compute and memory cost, and real-time feasibility? (10) what would you change to go beyond
this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: under **ten seconds** on a laptop CPU (measured:
1.3 s for the grid of criterion 3 — 5 qualities × 4 noise levels × 20 seeds × 31 values of $k$ —
and under 1 s for criteria 1, 2 and 4 together), under 200 MB, numpy only. The data comes from the generator the lesson provides.

```python
import numpy as np

GAMMA = 0.95


def make_mdp(n_s=30, n_a=4, seed=0):
    """True MDP: Dirichlet(0.3) transitions, U(0,1) rewards."""
    rng = np.random.default_rng(seed)
    p = rng.dirichlet(np.full(n_s, 0.3), size=(n_s, n_a))
    r = rng.uniform(0.0, 1.0, size=(n_s, n_a))
    return p, r


def fit_model(P, R, n, rng):
    """Count estimate from n transition samples per (s,a), plus N(0, 0.05) reward noise."""
    Ph = np.empty_like(P)
    for s in range(P.shape[0]):
        for a in range(P.shape[1]):
            Ph[s, a] = rng.multinomial(n, P[s, a]) / n
    return Ph, R + rng.normal(0.0, 0.05, size=R.shape)
```

**Acceptance criteria** — all four must hold.

1. **Numerical check of the identity (1)**: for $n \in \{10, 50, 500\}$ the two sides of (1) differ
   by at most $10^{-12}$ in max norm (measured $\le 2.7\times10^{-14}$). At the same time, the bound
   (2) bounds the actual error from above, and the **looseness ratio** (actual/bound) is at most
   $10^{-2}$ and is reported (measured $6\times10^{-4}$–$5\times10^{-3}$).
2. **Concentration rate of the model error**: for $n \in \{10, 50, 500, 5000\}$ the five-seed mean
   $\epsilon_P$ satisfies $\epsilon_P\sqrt{n} \in [3.5,\ 5.5]$ — matching the $\ell_1$ concentration
   of the multinomial,
   $\mathbb{E}\lVert\hat{p}-p\rVert_1 \approx \sqrt{2\lvert\mathcal{S}\rvert/(\pi n)} = 4.37/\sqrt{n}$
   (measured $4.28$–$4.79$).
3. **Monotone shift of $k^\star$**: over the grid of model qualities
   $n \in \{2,3,5,20,100\}$ and critic noises $\sigma_V \in \{0.1, 0.3, 1, 3\}$, the 20-seed mean
   $k^\star = \arg\min_k \lVert Q_k - Q^\*\rVert_\infty$ ($k \in \{0,\dots,30\}$) is
   **non-decreasing in $\sigma_V$ for every $n$** (measured, at $n=2$:
   $0.55 \to 2.20 \to 11.40 \to 28.80$). Report as well that the monotonicity in the $\epsilon_P$
   direction (i.e. in $n$) **does not hold** — problem P5 asks why.
4. **Constructing objective mismatch**: for the model $\hat{P}$ at $n=200$ and seed 0, let $c$ be
   the centred unit vector along $V^\pi$ and $u$ a unit vector orthogonal to $c$, and build the two
   models $\hat{P} + 0.02u$ and $\hat{P} + 0.004c$ (each row reprojected onto the simplex). With
   held-out counts drawn from the true model (2,000 per $(s,a)$), require
   $\mathrm{LL}(\hat{P}+0.004c) > \mathrm{LL}(\hat{P}+0.02u)$ while
   $\mathrm{err}(\hat{P}+0.004c) > 2\,\mathrm{err}(\hat{P}+0.02u)$ (measured: log-likelihood
   $+24{,}060$ vs $+8{,}931$, value error $0.0957$ vs $0.0370$, a factor of $2.6$).

**Baselines**: ⓐ $k=0$ (pure critic) and $k=30$ (effectively pure model) — the two extremes of
criterion 3 serve as baselines. ⓑ the $k$-step rollout run with the **true** model: since
$\epsilon_P = 0$, it must improve monotonically in $k$ (a sanity check that the model-error term is
really gone). ⓒ optional: implement the mixed update with real ratio $\beta$ (problem P2) and plot
the bias reduction against $\beta$.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The identity residual in criterion 1 is around $10^{-6}$ | $(I-\gamma\hat{P}^\pi)^{-1}$ was approximated iteratively | solve with `np.linalg.solve` and look at the residual again |
| The bound (2) is **smaller** than the actual error | $\epsilon_P$ was measured in $\ell_2$ or total variation, or the mean reward was used instead of $R_{\max}$ | fix the definition of $\epsilon_P$ to the max over rows of the $\ell_1$ sum |
| Criterion 2 fails ($\epsilon_P\sqrt{n}$ above 7) | $\epsilon_P$ is a max over many $(s,a)$ pairs rather than a mean | print the number of $(s,a)$ pairs — the maximum grows logarithmically in that count |
| The monotonicity of criterion 3 fails | too few seeds, so $k^\star$ jumps around on a flat stretch | use the 20-seed mean and also print the standard deviation of $k^\star$ |
| In criterion 4 the two likelihoods barely differ | the perturbation was clipped away by the simplex reprojection | print the row sums and the smallest entry before and after perturbing |
| The value-error ordering in criterion 4 is reversed | $c$ was taken along $V^\*$ instead of $V^\pi$, or the centring was omitted | check that $c$ has mean zero and $\lVert c\rVert = 1$ |

## Open problems

- **(open problem) Value-aware model learning** — R5 shows that likelihood disagrees with value,
  but using a value-aligned loss requires the very $V^\pi$ that is unknown. Iteratively estimating
  and fitting has no convergence guarantee, and there is no instance of it working stably at robot
  scale. Current approaches: limiting rollouts to be short as in
  [MBPO](https://arxiv.org/abs/1906.08253), weighting by ensemble uncertainty as in
  [PETS](https://arxiv.org/abs/1805.12114). What is missing: a convergence guarantee for a
  value-aligned loss.
- **(open problem) Principled uncertainty that prevents model exploitation** — policy optimization
  actively seeks out regions where model error is large. Penalizing by ensemble variance or
  out-of-distribution detection is either too much or too little without calibration. Current
  approaches: [PETS](https://arxiv.org/abs/1805.12114),
  [Sinha et al. 2022](https://arxiv.org/abs/2212.14020),
  [conformal prediction](https://arxiv.org/abs/2107.07511). What is missing: an uncertainty
  guarantee that remains valid **inside** the policy-optimization loop.
- **(open problem) Is the latent state a sufficient statistic?** — (5) demands observation
  reconstruction, but that does not deliver the sufficiency of R3 in `c8-mdp-pomdp-bellman`. If the
  latent state is insufficient, doing DP on top of it means applying the Bellman equation to a
  problem that is not Markov. Current approaches:
  [PlaNet](https://arxiv.org/abs/1811.04551), [DreamerV3](https://arxiv.org/abs/2301.04104). What
  is missing: a procedure that verifies the sufficiency of a learned latent state.
- **(open problem) The structure of model error in contact dynamics** — (2) measures error at the
  worst state, but the error of contact dynamics **concentrates near the contact switching
  surface**. There is no bound reflecting that structure, so the value error induced by a smoothed
  model cannot be predicted. Current approaches:
  [Posa et al. 2014](https://doi.org/10.1177/0278364913506757),
  [Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751). What is missing: a local bound that
  carries state-dependent model error into value error.

## Concept check

Run `rc quiz c8-model-based-world-models`. The quiz is for **concept checking only**; the real work
is the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: where the $(1-\gamma)^{-2}$ of the simulation lemma comes from; whether Dyna's
bias disappears with more real data; how the optimal rollout length responds to critic noise;
whether a higher held-out log-likelihood implies a smaller value error; and what the KL term of the
ELBO pulls the inference distribution toward.

## How to study this stage

1. **The identity first, the bound second (60 min)** — derive (1) from a blank page. Remember only
   the single line "add and subtract $\gamma\hat{P}^\pi V^\pi$" and the rest is algebra. The bound
   (2) then takes ten minutes. In the other order you memorize the bound and cannot write the
   identity.
2. **Meet the looseness as a number (45 min)** — solve problem P3, then measure the actual/bound
   ratio with criterion 1 of the reproduction task. Only after seeing $10^{-3}$ does it stick why a
   "$(1-\gamma)^{-2}$ guarantee" must not be used as a design guide. Then build the span version
   with P1 and see how much tighter it gets.
3. **Turn the $k$ knob yourself (90 min)** — run criterion 3 while varying $\sigma_V$ and watch
   $k^\star$ move. Then vary $n$ and watch **the monotonicity fail**, and solve P5. Seeing a
   prediction fail first-hand is the core experience of this lesson.
4. **Derive the ELBO and interpret each term (60 min)** — pull (5) out of a single Jensen step and
   write one sentence on what each of the two terms demands. Read it against the derivation in
   PlaNet §3.
5. **Construct objective mismatch yourself (90 min)** — build criterion 4. All it takes is
   separating the value direction $c$ from an orthogonal direction $u$. People who have done this
   construction hear "just learn a better model" differently from those who have not.
6. **The three papers and the open problems (195 min)** — Kearns & Singh (the lemma) → MBPO (the
   $k$ trade-off) → DreamerV3 (the objective at scale). Write the one-page note for each; this is
   **not** optional. Finally, pick the value-aware model learning open problem and write a paragraph
   on why the construction of criterion 4 is not a solution (you do not know $V^\pi$).

**Passing bar**: you can derive (1) from a blank page and point out where the $(1-\gamma)^{-2}$ of
(2) arises, say how $k^\star$ depends on $\sigma_V$ and $\epsilon_P$, derive (5) and construct an
objective mismatch, and you hold code satisfying the four acceptance criteria plus notes on the
three papers.
