---
id: s4-pretrained-representations
lang: en
title: Pretrained representations and transfer
summary: >-
  Derive in closed form that what a linear probe measures is not information content but a
  **projection residual**, and construct a ranking reversal in which a representation holding all
  the information but coded nonlinearly is scored **below** one that has thrown information away
  linearly. Then show that the slope of loss against probe capacity is a diagnostic separating
  "inaccessible" from "absent", and derive that the linear limit of a temporal contrastive
  objective is CCA between consecutive frames — which recovers the slow subspace, while a
  reconstruction objective follows variance instead.
objectives:
  - Derive that the linear probe loss is $\sigma^2$ plus a projection residual and explain why that is not information content.
  - Compute in closed form the linear residual of a nonlinearly coded representation.
  - Construct an example in which the ranking of representations reverses with probe capacity.
  - Diagnose from the capacity-loss slope whether information is hidden or destroyed.
  - Derive that the linear limit of a temporal contrastive objective is CCA and show that the canonical correlations recover the autocorrelations.
  - State the condition under which a reconstruction objective misses the slow subspace.
tags: [representation-learning, linear-probing, temporal-contrastive, cca, transfer, research]
---

# Pretrained representations and transfer

## Setup and notation

This lesson uses the bias-variance ledger of `s4-robot-data-scaling` and the transfer crossover of
`s4-vla-architectures` R3. Additional **recommended** background:

- Linear algebra: orthogonal projection, principal angles between subspaces, generalized eigenvalue
  problems.
- Probability: covariance, correlation, the autocorrelation of an AR(1) process.
- Information theory (lightly): the definition of mutual information and its **invariance under
  invertible transformations** — the counterexample of R1 rests on that.

Notation:

| Symbol | Meaning |
|---|---|
| $\phi(x) \in \mathbb{R}^{p}$ | the frozen representation; $\Pi_\phi$ is the orthogonal projection onto $\mathrm{span}(\phi)$ |
| $y$ | what the probe must predict (an action, reward or state), with noise variance $\sigma^2$ |
| $\mathcal{F}$ | the probe function class (linear, finite-capacity, oracle) |
| $L_{\mathcal{F}}(\phi)$ | the probe loss $\min_{f\in\mathcal{F}} \mathbb{E}\big[(f(\phi)-y)^2\big]$ |
| $g$ | an invertible coordinate-wise coding; here $g(u) = u + u^3$ |
| $s_t \in \mathbb{R}^{d_s}$ | the latent state, split into slow and fast (nuisance) components |
| $\rho$ | the AR(1) autocorrelation; slow components have $\rho \to 1$, fast ones $\rho \to 0$ |
| $\theta_i$ | the $i$-th principal angle between two subspaces |

**The confusion this lesson is aimed at.** The claim "this representation is good" is almost always
supported by a **linear probe score**. But a linear probe does not measure information content — it
measures whether the information **sits in a form a linear map can extract**. The two quantities
behave completely differently under invertible transformations, so a report that representation A
beats B can reverse when the probe changes. This lesson **constructs** that reversal and then builds
a procedure for telling which side is right.

## Key results

The bracket gives the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (a linear probe measures a projection residual) [D2]** — if the target is
  $y = h(x) + \varepsilon$ with $\mathbb{E}[\varepsilon]=0$ and $\mathrm{Var}(\varepsilon)=\sigma^2$,
  $$
  L_{\mathrm{lin}}(\phi) \;=\; \sigma^2 \;+\; \big\lVert (I - \Pi_\phi)\,h \big\rVert^2_{L^2(p_x)} . \tag{1}
  $$
  So the probe score is **how much of $h$ lies in $\mathrm{span}(\phi)$**, a different quantity from
  the information $\phi$ carries: mutual information is invariant under invertible transformations
  while (1) is not.
- **R2 (the linear residual of an invertible nonlinear coding has a closed form) [D2]** — if
  $\phi_B = g(\phi_A)$ for a coordinate-wise invertible map, the linear residual fraction is
  $$
  1 - \frac{\big(\mathbb{E}[u\,g(u)]\big)^2}{\mathrm{Var}(u)\,\mathrm{Var}(g(u))},
  \qquad g(u) = u+u^3,\; u\sim\mathcal{N}(0,1)
  \;\Longrightarrow\; 1 - \frac{16}{22} = \frac{3}{11} = 0.2727 \tag{2}
  $$
  (using $\mathbb{E}[u g] = 1+3 = 4$ and $\mathrm{Var}(g) = 1+6+15 = 22$). The measured $0.27243$
  agrees with (2) plus $\sigma^2 = 0.2752$ at a ratio of $0.990$.
- **R3 (the ranking reverses with probe capacity) [D2]** — taking a nonlinear representation B that
  holds all the information and a linear representation C that has discarded $1/6$ of it,
  $$
  L_{\mathrm{lin}}(B) = 0.2724 \;>\; L_{\mathrm{lin}}(C) = 0.1699,
  \qquad
  L_{\mathrm{oracle}}(B) = 0.0025 \;\ll\; L_{\mathrm{oracle}}(C) = 0.1699 \tag{3}
  $$
  so the **ranking flips** (by $67.8\times$ at the oracle). The reversal does not even need the
  oracle — a probe with just $100$ random features already puts B ahead of C
  ($0.0764 < 0.1711$).
- **R4 (the capacity-loss slope separates "hidden" from "destroyed") [D2]** — sweeping the probe
  capacity $m$,
  $$
  \text{B: } 0.2724 \to 0.0764 \to 0.0504 \to 0.0305 \to \sigma^2, \qquad
  \text{C: } 0.1699 \to 0.1711 \to 0.1726 \to 0.1789 \to 0.1699 \tag{4}
  $$
  (for $m = \text{linear}, 100, 300, 1200, \text{oracle}$). **B falls with capacity and C does
  not.** The sign of the slope therefore tells whether the information is **inaccessible** or
  **absent** — something a single probe score can never reveal.
- **R5 (the linear limit of a temporal contrastive objective is CCA) [D2]** — restricting a
  contrastive objective over adjacent-frame pairs to a linear encoder makes the population optimum
  the **canonical correlation analysis (CCA)** between $x_t$ and $x_{t+1}$, whose leading components
  recover the **slow (time-predictable) subspace**. With AR(1) latents the canonical correlations
  recover the autocorrelations ($\rho_{\text{slow}} = 0.98$, measured $0.972$–$0.980$). A
  reconstruction (PCA) objective instead follows the **high-variance directions**, so if the
  nuisance components carry more variance it misses the slow subspace (measured principal angles:
  CCA $5.4^\circ$ versus PCA $78.7^\circ$).

## Derivation

### R1 — the probe loss is a projection residual

Let $y = h(x) + \varepsilon$ and let the probe be of the form $f(\phi(x)) = w^\top\phi(x)$. The
squared loss splits as

$$
\mathbb{E}\big[(w^\top\phi - h - \varepsilon)^2\big]
  = \sigma^2 + \mathbb{E}\big[(w^\top\phi - h)^2\big]
$$

because $\varepsilon$ is independent of $x$. Minimizing the second term over $w$ is exactly the
**orthogonal projection** of $h$ onto $\mathrm{span}(\phi)$ in $L^2(p_x)$, whose minimum is
$\lVert (I-\Pi_\phi)h\rVert^2$, giving (1).

**Why this is not information content.** If $\phi' = T(\phi)$ is invertible then $\phi$ and $\phi'$
carry **the same information** ($I(\phi; y) = I(\phi'; y)$ — mutual information is invariant under
invertible maps). Yet $\mathrm{span}(\phi')$ can be entirely different from $\mathrm{span}(\phi)$,
so $L_{\mathrm{lin}}$ **can be made arbitrarily large**. A linear probe score is not the
representation's information content but "the degree to which the information is aligned with a
linear coordinate system", and conflating the two is this lesson's target.

**Where the assumptions break.** (1) is an equality when the probe class is exactly the **linear
span of $\phi$**. A practical "linear probe" usually includes a bias and mild regularization, which
adds a regularization bias to (1). And if $y$ is categorical with a cross-entropy loss, the
projection reading does not carry over — then one is measuring "linear separability", a different
quantity. The conclusion of this lesson (capacity dependence) survives, but the closed form of (1)
does not apply.

### R2 — the linear residual of an invertible nonlinear coding

Take $\phi_A = s Q$ (with $Q$ orthogonal) and $\phi_B = g(sQ)Q_2$ with $g$ a coordinate-wise
**monotone** map. The target is $y = s^\top w + \varepsilon$. Since the coordinates of $s$ are
independent standard normals and $Q$ is orthogonal, $u := (sQ)_i$ is also standard normal. Looking
at a single coordinate, the best a linear probe can do in recovering $u$ from $g(u)$ is to project
$u$ onto $g(u)$, with residual fraction

$$
1 - \frac{\mathrm{Cov}(u, g(u))^2}{\mathrm{Var}(u)\,\mathrm{Var}(g(u))} .
$$

For $g(u) = u+u^3$ we have $\mathbb{E}[u] = \mathbb{E}[g] = 0$, and the Gaussian moments
($\mathbb{E}[u^2]=1$, $\mathbb{E}[u^4]=3$, $\mathbb{E}[u^6]=15$) give

$$
\mathrm{Cov}(u,g) = \mathbb{E}[u^2] + \mathbb{E}[u^4] = 1+3 = 4, \qquad
\mathrm{Var}(g) = \mathbb{E}[u^2] + 2\mathbb{E}[u^4] + \mathbb{E}[u^6] = 1+6+15 = 22,
$$

so the residual fraction is $1 - 16/22 = 3/11 = 0.2727$ — equation (2). Since the coordinates are
independent and $w$ is uniform across them, the overall residual has the same fraction and the probe
loss is $\sigma^2 + 0.2727 = 0.2752$. The measured $0.27243$ gives a ratio of $0.990$.

**The contrast: a linear representation that discarded information.** Let $\phi_C$ keep only the
first $K$ coordinates of $sQ$. The signal variance carried by the $D-K$ discarded coordinates
becomes residual outright, so

$$
L_{\mathrm{lin}}(C) = L_{\mathcal{F}}(C) = \sigma^2 + \frac{D-K}{D} \qquad (\text{for every } \mathcal{F}) \tag{5}
$$

With $D=6$ and $K=5$ this is $0.0025 + 1/6 = 0.1692$, and the measured $0.16990$ gives a ratio of
$1.004$. **The key is that (5) does not depend on the probe class** — discarded information never
comes back.

**Where the assumptions break.** (2) requires that $g$ **does not saturate**. A map like
$g(u)=\tanh(4u)$ is injective mathematically but destroys information numerically: even though an
inverse exists, it is not recoverable at finite precision with finite samples (the first design of
this lesson fell into that trap — problem P5). The real condition for using (2) is that $g$ has a
derivative bounded below ($g'(u) \ge 1$).

### R3 and R4 — the ranking reversal and the capacity-slope diagnostic

Putting (2) and (5) side by side lets one **design the linear probe's ranking to be the reverse of
the information ranking**. With $D=6$, $K=5$ and $g(u)=u+u^3$,

$$
L_{\mathrm{lin}}(B) = 0.2752 \;>\; L_{\mathrm{lin}}(C) = 0.1692
  \quad\text{but}\quad
L_{\mathrm{oracle}}(B) = \sigma^2 \;\ll\; L_{\mathrm{oracle}}(C) = 0.1692 ,
$$

i.e. **the linear probe picks C while the oracle picks B.** The oracle probe applies $g^{-1}$ and
then does linear regression, and since $g$ is monotone it is computed exactly by Newton iteration.

**Sweep the capacity to diagnose.** In practice $g$ is unknown, so the oracle is unavailable.
Instead sweep the probe capacity $m$ (the number of random features) and read the **slope** of the
loss. Reading (4) again:

| representation | linear | $m=100$ | $m=300$ | $m=1200$ | oracle |
|---|---|---|---|---|---|
| A (lossless, linear) | $0.00250$ | $0.00361$ | $0.00262$ | $0.00265$ | $0.00250$ |
| B (lossless, nonlinear) | $0.27243$ | $0.07637$ | $0.05043$ | $0.03051$ | $0.00250$ |
| C (lossy, linear) | $0.16990$ | $0.17106$ | $0.17260$ | $0.17887$ | $0.16990$ |

Three readings. ⓐ **A is at the floor under every probe** (the slight rise at $m=100$ is estimation
variance and comes back down as capacity grows). ⓑ **B falls monotonically with capacity** and
converges to the oracle's floor — the information was there and the probe was the limitation.
ⓒ **C does not fall with capacity and even rises slightly** (only estimation variance is added) —
there is no information to find, so capacity does not help.

$$
\textbf{Diagnostic rule: } \frac{\partial L_{\mathcal{F}_m}(\phi)}{\partial m} < 0
  \;\Rightarrow\; \text{the information is present but inaccessible}; \qquad
  \approx 0 \;\Rightarrow\; \text{the information is absent}. \tag{6}
$$

**This is the lesson's practical conclusion.** What must be reported when comparing representations
is not one score but a **capacity-loss curve**, whose slope separates "the representation must
change (slope $\approx 0$)" from "the head must grow (slope $< 0$)". A single linear-probe number on
a public benchmark erases that distinction, and can therefore invert the ranking between
representations.

**Where the assumptions break.** (6) needs the **sample size to grow with the capacity**. Holding
the samples fixed while raising capacity overfits and the loss rises, making B look like C (C rising
to $0.17887$ at $m=1200$ is a small instance of that effect). The diagnostic is therefore valid only
when capacity and samples are swept **together**, or after the regularization has been fixed by
cross-validation.

### R5 — the temporal contrastive objective and CCA

**The objective.** Take a contrastive objective (InfoNCE) with adjacent frames $(x_t, x_{t+1})$ as
positive pairs and arbitrary time pairs as negatives, and restrict the encoder to be **linear**
($z = W^\top x$) with a bilinear critic. In the population limit of many negatives, the optimal
critic is proportional to the density ratio $p(z_{t+1}\mid z_t)/p(z_{t+1})$, and for Gaussian latents
the log of that ratio is determined by the **correlation structure** of $z_t$ and $z_{t+1}$ alone.
So the optimal linear encoder solves, sequentially,

$$
\max_{u,v} \;\; \mathrm{corr}\big(u^\top x_t,\; v^\top x_{t+1}\big) \tag{7}
$$

— that is, **CCA** between $x_t$ and $x_{t+1}$. The solution comes from the generalized eigenvalue
problem

$$
\Sigma_{xx}^{-1}\Sigma_{xy}\Sigma_{yy}^{-1}\Sigma_{yx}\,u = \lambda\, u,
\qquad \Sigma_{xy} = \mathrm{Cov}(x_t, x_{t+1}) \tag{8}
$$

with $\sqrt{\lambda}$ the canonical correlations.

**Why the slow subspace comes out.** If the latents are independent AR(1) processes and
$x_t = A s_t + \text{noise}$, then $\mathrm{Cov}(s_t, s_{t+1}) = \mathrm{diag}(\rho_i \mathrm{Var}(s_i))$.
The maximum in (7) is $\max_i \rho_i$ and its direction is the one **reading the slowest latent**.
So the canonical correlations recover the autocorrelations outright. Measured: against
$\rho_{\text{slow}} = 0.98$ the canonical correlations are $0.972$–$0.980$, and the maximum
principal angle between the recovered subspace and the true slow subspace is **$5.4^\circ$**
(mean over 5 seeds).

**The contrast with a reconstruction objective.** Reconstruction (PCA) picks the leading eigenvectors
of $\mathrm{Var}(x)$ and so follows the **high-variance directions**. Setting the nuisance
components' variance to nine times the slow components' makes PCA miss the slow subspace, with a
measured maximum principal angle of **$78.7^\circ$**. Slowness and variance are different axes, and
which one the pretraining objective picks determines what information is usable downstream.

**Where the assumptions break.** (7) reduces to CCA for a **linear encoder with Gaussian latents**.
With a nonlinear encoder the optimum is a nonlinear function of the density ratio and is not CCA
(there, CCA is useful only as an initialization giving a lower bound). And the premise that "slow is
useful" is task-dependent — if the target is a fast-changing contact event, the slow subspace is
**useless** and the temporal contrastive objective picks the wrong axis (problem P5).

## Proof sketch

### R1 — the projection representation of the probe loss [D2, stated as a proof]

**Hypotheses** H1: $y = h(x) + \varepsilon$ with $\varepsilon \perp x$,
$\mathbb{E}\varepsilon = 0$ and $\mathrm{Var}\,\varepsilon = \sigma^2$. H2: the probe class is
$\mathrm{span}(\phi)$ (with a bias). H3: $h \in L^2(p_x)$ and
$\mathbb{E}\lVert\phi\rVert^2 < \infty$.
**Conclusion** C: (1), and that for invertible $T$ the value $L_{\mathrm{lin}}(T\circ\phi)$ can
differ arbitrarily from $L_{\mathrm{lin}}(\phi)$.

**Strategy**: separate the noise → minimality of the $L^2$ orthogonal projection → a counterexample
in which an invertible map changes the span.

1. Split the loss into $\sigma^2$ and an approximation error. Uses: H1 (the cross term vanishes).
2. Show the minimum of the approximation error is the orthogonal projection residual (the projection
   theorem). Uses: H2, H3.
3. Take $T$ to be a coordinate-wise monotone nonlinearity so that $\mathrm{span}(T\circ\phi)$
   contains almost none of $h$ → the second part of C. The concrete construction is (2) of R2, whose
   residual is **computed** to be $3/11$.

**Delete one hypothesis**: replacing H2 with a finite-capacity nonlinear class breaks the equality
in (1), and the loss then depends on the class's approximation power — that dependence is exactly the
capacity slope of R4. Dropping the independence in H1 (so $\varepsilon$ depends on $x$) means
$\sigma^2$ does not separate and the floor itself depends on $\phi$.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Generalize (2) to $g(u) = u + \alpha u^3$ and write the residual
fraction as a function of $\alpha$. What are the limits $\alpha \to 0$ and $\alpha \to \infty$?
*Solution sketch*: $\mathrm{Cov}(u,g) = 1 + 3\alpha$ and
$\mathrm{Var}(g) = 1 + 6\alpha + 15\alpha^2$, so the residual fraction is
$1 - (1+3\alpha)^2/(1+6\alpha+15\alpha^2) = 6\alpha^2/(1+6\alpha+15\alpha^2)$. It tends to $0$ as
$\alpha\to0$ (converging to linear) and **saturates** at $6/15 = 2/5$ as $\alpha\to\infty$ — a
coordinate-wise odd nonlinearity alone cannot erase more than $2/5$ of the linear accessibility. At
$\alpha=1$ it gives $6/22 = 3/11$, matching (2).

**P2 (proof, ★★★, R1)** Prove (1) rigorously (variationally, without citing the projection theorem),
and show that for an invertible $T$ we have $I(\phi;y) = I(T\circ\phi; y)$ while
$L_{\mathrm{lin}}$ is not preserved. Then characterize the **set of $T$ for which
$L_{\mathrm{lin}}$ is preserved**.
*Strategy and key inequality*: the variational condition
$\mathbb{E}[(w^\top\phi - h)\phi] = 0$ is the normal equation and its solution is the projection.
The invariance of mutual information follows from invertibility. $L_{\mathrm{lin}}$ is preserved only
for **invertible affine** $T$ (those are the only span-preserving maps). The expansion is withheld.

**P3 (numerical, ★, R2·R3)** With $D = 6$ and $\sigma = 0.05$, compute (ⓐ) the linear probe loss of
the representation coded by $g(u)=u+u^3$, (ⓑ) the loss of the lossy representation keeping $K=5$,
and (ⓒ) the $K$ at which the two losses coincide.
*Answer*: (ⓐ) $0.0025 + 3/11 = 0.27523$ (tolerance $10^{-5}$). (ⓑ) $0.0025 + 1/6 = 0.16917$.
(ⓒ) $(D-K)/D = 3/11 \Rightarrow K = D(1 - 3/11) = 6\cdot8/11 = 4.36$ — not an integer, so at
$K = 4$ the lossy representation is **worse** ($0.3358$) and at $K = 5$ it is **better**
($0.1692$). The reversal therefore happens only at $K = 5$.
Check: divide the measured $0.27243$ and $0.16990$ by (ⓐ) and (ⓑ) and confirm ratios of $0.990$ and
$1.004$.

**P4 (implementation, ★★, R3·R4·R5)** Implement the reproduction task and pass all four criteria.
*Rubric*: ⓐ $g^{-1}$ is implemented by Newton iteration and the maximum residual
$\lvert g(g^{-1}(v)) - v\rvert$ is reported; ⓑ the random-feature probe standardizes its inputs and
selects the regularizer from a grid; ⓒ it is stated that the **sample size was held fixed** while
sweeping capacity, with the limitation noted (the assumption of R4); ⓓ CCA is solved via Cholesky
with a small regularizer added to $\Sigma$; ⓔ principal angles are computed by QR plus SVD.

**P5 (counterexample, ★★, R2·R5)** Construct both traps: (i) a saturating coding
($g(u) = \tanh(4u)$) is invertible mathematically but its information is not recoverable at finite
precision with finite samples — show that even the oracle probe fails to reach the floor;
(ii) construct a task for which "slow features are useful" is false.
*Property checklist*: (i) $\tanh(4u)$ saturates for $\lvert u\rvert \gtrsim 1$, so the derivative of
$g^{-1}$ blows up, and in the measurement a random-feature probe stalls at $0.209$ (floor
$0.0025$). The condition is $g' \ge c > 0$ (bounded below), which $u+u^3$ satisfies and $\tanh$ does
not. (ii) make the target a function of the **fast** latents — then the slow subspace CCA chose
holds no information about it, so the temporal contrastive objective picked the **wrong axis** and
reconstruction or task supervision would be better.

**P6 (paper, ★★, R1·R3·R4)** Read R3M (§3–4) and VC-1 (§4–5) and write, in at most three sentences
each: (i) what probe was used to evaluate representations, and was its capacity swept; (ii) whether
the reported ranking passes the diagnostic of (6) — i.e. is there a capacity-loss curve;
(iii) if a temporal contrastive (or comparable) objective was used, does the paper address the
slowness-versus-variance distinction of (7).
*Grading rubric*: (i) passes if it notes that it is usually a single fixed-capacity linear or small
MLP probe. (ii) passes if it points out that without a capacity curve the ranking could flip as in
(3). (iii) the presence or absence of discussion of the temporal contrastive term (R3M's) and the
axis it selects. Writing only "the representation transfers well" fails.

**P7 (derivation, ★★, R5)** Derive (8): write (7) as a constrained optimization in $u, v$ and extract
the generalized eigenvalue problem from the Lagrange conditions. Then show that when the latents are
independent AR(1) processes and $A$ is orthogonal, the canonical correlations equal $\rho_i$.
*Solution sketch*: the first-order conditions of
$\max u^\top\Sigma_{xy}v$ subject to $u^\top\Sigma_{xx}u = v^\top\Sigma_{yy}v = 1$ are
$\Sigma_{xy}v = \lambda\Sigma_{xx}u$ and $\Sigma_{yx}u = \lambda\Sigma_{yy}v$, and eliminating gives
(8). With $A$ orthogonal and small noise,
$\Sigma_{xx} \approx A\mathrm{diag}(\mathrm{Var})A^\top$ and
$\Sigma_{xy} \approx A\mathrm{diag}(\rho_i\mathrm{Var})A^\top$, so the generalized eigenvalues are
$\rho_i^2$.

## Paper reading

**Two must-reads.** Write a one-page note on each using the ten fixed questions
(`lesson-standard.md` §5).

1. **Nair, Rajeswaran, Kumar, Finn & Gupta, "R3M: a universal visual representation for robot
   manipulation" (2022, CoRL)** — role: `seminal`. <https://arxiv.org/abs/2203.12601> — §3–4.
   Why read it: the paper that established a pretraining objective including a temporal contrastive
   term, together with the evaluation style of a small policy head on a frozen representation. Both
   R5's "which axis does the objective pick" and R4's "probe capacity" are at stake.
   Extra questions: ⓐ which axis does each of the temporal contrastive term and the language
   alignment term pick, and do the ablations separate them? ⓑ was the evaluation probe's capacity
   swept — and if not, how much confidence does the reported ranking deserve?
2. **Majumdar et al., "Where are we in the search for an artificial visual cortex for embodied AI?"
   (2023, NeurIPS)** — role: `standard`. <https://arxiv.org/abs/2303.18240> — §4–5.
   Why read it: a large-scale comparison of many representations under one protocol, and a case study
   for whether the diagnostic of (6) can actually be applied.
   Extra questions: ⓐ is the conclusion that "no single representation is best on every task"
   explained by the task dependence of (1) (that $h$ differs per task)? ⓑ were the probe and
   fine-tuning budgets matched fairly across tasks, and if not, which conclusions wobble?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation? (4) what is guaranteed and **what is not**?
(5) independent and dependent variables, and the baselines — were they tuned fairly? (6) does the
metric match the claim, and are variance and seeds reported? (7) what information needed for
reproduction is missing? (8) if the result were wrong, which assumption would you doubt first?
(9) compute and memory cost, and real-time feasibility? (10) what would you change to go beyond
this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: under **five minutes** on a laptop CPU (measured:
$272$ s for the full capacity sweep, under $1$ minute if $m=1200$ is dropped; the CCA part is under
$10$ s), under 500 MB, numpy only. **No GPU is needed.** Extending to real pretrained
representations is the **optional extension (R4)** below.

**Generator (probe part).** The latent $s \in \mathbb{R}^6$ is standard normal and the target is
$y = s^\top w + \varepsilon$ ($w$ uniform, $\sigma = 0.05$). The three representations are
A $= sQ$, B $= g(sQ)Q_2$ with $g(u) = u+u^3$, and C $= $ only the first $5$ coordinates of $sQ$
($Q, Q_2$ random orthogonal).

```python
import numpy as np


def g(u):
    return u + u**3  # monotone, g' = 1 + 3u^2 >= 1, no saturation


def g_inv(v, iters=60):
    u = np.cbrt(v)
    for _ in range(iters):
        u = u - (u + u**3 - v) / (1.0 + 3.0 * u**2)
    return u
```

**Acceptance criteria** — all four must hold.

1. **Agreement with the closed forms**: the 5-seed mean linear probe loss is ⓐ within $10^{-4}$ of
   $\sigma^2 = 0.0025$ for A, ⓑ within a ratio of $[0.97,\,1.03]$ of (2)'s
   $\sigma^2 + 3/11 = 0.27523$ for B (measured $0.27243$, ratio $0.990$), and ⓒ within a ratio of
   $[0.97,\,1.03]$ of (5)'s $\sigma^2 + 1/6 = 0.16917$ for C (measured $0.16990$, ratio $1.004$).
2. **The oracle probe and the ranking reversal**: a linear probe applied after $g^{-1}$ ⓐ agrees
   with $\sigma^2$ to within $10^{-4}$ for B (measured $0.00251$), ⓑ is **identical** to the linear
   probe for C (measured $0.16990$ for both — discarded information does not return), and
   ⓒ therefore produces a **ranking reversal** in which the linear probe picks C and the oracle picks
   B, with an oracle ratio $\ge 50\times$ (measured $67.8\times$). Report the accuracy of $g^{-1}$ as
   $\max\lvert g(g^{-1}(v)) - v\rvert < 10^{-10}$.
3. **The capacity-slope diagnostic (6)**: sweeping a random ReLU feature probe over
   $m \in \{100, 300\}$ (optionally $1200$), ⓐ B's loss **decreases monotonically** (measured
   $0.2724 \to 0.0764 \to 0.0504 \to 0.0305$), ⓑ C's loss **does not decrease** (measured
   $0.1699 \to 0.1711 \to 0.1726 \to 0.1789$ — it rises because of estimation variance, the samples
   being held fixed), and ⓒ B already beats C at $m=100$ (measured $0.0764 < 0.1711$). Report that
   the sample size was held fixed and how that limits the assumption behind (6).
4. **CCA recovers the slow subspace**: with $6$ latents (3 slow at $\rho=0.98$ with variance $1$,
   3 fast at $\rho=0.10$ with variance $9$), a $20$-dimensional observation and a trajectory of
   length $4\times10^4$, ⓐ the maximum principal angle between the top $3$ consecutive-frame CCA
   components and the directions reading the slow latents is **below $10^\circ$** (measured
   $2.1$–$6.3^\circ$ over 5 seeds, mean $5.4^\circ$); ⓑ the maximum principal angle between the top
   $3$ PCA components and the slow latent subspace **exceeds $30^\circ$** (measured mean
   $78.7^\circ$); ⓒ the leading canonical correlation agrees with $\rho_{\text{slow}} = 0.98$ to
   within $\pm0.01$ (measured $0.972$–$0.980$).

**Baselines**: ⓐ representation A — the "ideal" representation, at the floor under every probe.
ⓑ the oracle probe — the ceiling for criterion 2 (a proxy for information content). ⓒ PCA — the
control for criterion 4. ⓓ optional: a **random orthogonal projection** at C's dimension — this
separates "it lost because the dimension is small" from "it lost because the information is gone".

**Optional extension (R4, may need a GPU — not required)**: extract frozen features from
R3M-style or VC-1-style public checkpoints, run the same capacity sweep, and see whether the
reported ranking changes with capacity. **No acceptance criterion is set** — differences in
checkpoints and preprocessing may prevent the numbers from reproducing. The purpose is to check
whether the diagnostic of (6) is applicable to real representations.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The ratio in criterion 1ⓑ exceeds $1.1$ | $Q$ is not orthogonal, so the coordinates are not standard normal | print the norm of $Q^\top Q - I$ and the coordinate variances of $sQ$ |
| Criterion 2ⓐ does not reach the floor | the Newton iteration for $g^{-1}$ did not converge (initial value) | print $\max\lvert g(g^{-1}(v))-v\rvert$ — it must be below $10^{-10}$ |
| No reversal appears in criterion 2 | $K$ is not $5$ — at $K=4$, C is worse and the reversal disappears | print $(D-K)/D$ next to $3/11$ (the reversal needs $1/6 < 3/11$) |
| Criterion 3ⓐ is not monotone | the regularizer was not selected from a grid, so large $m$ overfits | print the $\lambda$ chosen at each $m$ |
| The angle in criterion 4ⓐ is large | CCA was solved without regularizing $\Sigma$ and broke numerically | print the condition number of $\Sigma_{xx}$ and add $10^{-6}I$ |
| The angle in criterion 4ⓑ is small | the fast components were not given more variance than the slow ones | print both variances — PCA must **miss** the slow axis for the contrast to hold |

## Open problems

- **(open problem) A practical probe that measures information content** — (1) shows a linear probe
  is not information content and (6) offers the capacity sweep as a workaround. But
  **extrapolating** the capacity-loss curve (estimating the oracle floor) has no guarantee, and a
  sweep with fixed samples is entangled with overfitting. Mutual information estimators have too much
  variance in high dimensions to serve as an alternative. Current approaches: the
  [InfoNCE lower bound](https://arxiv.org/abs/1807.03748), large-scale protocol comparisons
  ([VC-1](https://arxiv.org/abs/2303.18240)). What is missing: an estimator that separates
  accessibility from content on a finite budget.
- **(open problem) Matching the axis a pretraining objective picks to the task** — R5 shows that
  temporal contrast picks the **slow** axis and reconstruction the **high-variance** one. But the
  axis a downstream task needs may be neither (contact events are fast and low-variance). There is no
  principle for choosing the axis without knowing the task. Current approaches:
  [R3M](https://arxiv.org/abs/2203.12601)'s multi-term objective,
  [slow feature analysis](https://doi.org/10.1162/089976602317318938). What is missing: a way to
  back out the objective from a task distribution.
- **(open problem) Transfer of representation rankings across tasks** — the residual in (1) depends
  on $h$, so the ranking can differ per task, and indeed no large comparison reports a representation
  that is best on every task. That leaves it unclear what the goal of a "universal representation"
  even means. Current approaches: per-task-family analysis in
  [VC-1](https://arxiv.org/abs/2303.18240), evaluation correlation in
  [SIMPLER](https://arxiv.org/abs/2405.05941). What is missing: an aggregation criterion for
  comparing representations over a task distribution.
- **(open problem) The boundary between freezing and fine-tuning** — the $N^\star$ of
  `s4-vla-architectures` R3 gives the crossover between freezing and full training, but practice uses
  **partial fine-tuning** (adapters, the last block). There is no way to count the effective degrees
  of freedom of that middle ground, so an $N^\star$-style analysis cannot be applied. What is
  missing: the effective parameter count of partial fine-tuning.

## Concept check

Run `rc quiz s4-pretrained-representations`. The quiz is for **concept checking only**; the real work
is the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: what the linear probe loss (1) measures; whether a representation holding all
the information always scores better on a linear probe; what it means when loss does not change with
probe capacity; what the population optimum of an adjacent-frame contrastive objective with a linear
encoder is; and whether reconstruction and temporal contrast pick the same subspace.

## How to study this stage

1. **Derive (1) from a blank page (40 min)** — two steps: separate the noise, then the orthogonal
   projection. Then write in one sentence that "mutual information is invariant under invertible maps
   but (1) is not". That sentence is the summary of the whole lesson.
2. **Compute (2) by hand (45 min)** — only the Gaussian moments $1, 3, 15$ are needed to get
   $3/11$. Generalizing to $\alpha$ in problem P1 also shows the limit that **a coordinate-wise odd
   function cannot erase more than $2/5$ of the linear accessibility**. With the closed form in hand,
   run criterion 1 of the reproduction task and check the ratio is $0.99$.
3. **Construct the reversal yourself (60 min)** — confirm with problem P3(ⓒ) why $K=5$ is required
   ($1/6 < 3/11$), then run criterion 2 and watch the oracle pick B. Seeing that **the reversal can
   be designed** changes how you read a single benchmark number.
4. **Sweep the capacity and diagnose (75 min)** — run criterion 3 and watch B fall while C does not.
   Then keep the samples fixed and push $m$ higher to see **C rise**, and write down how that limits
   the assumption behind (6). The point is to break the diagnostic's premise yourself.
5. **Recover the slow axis with CCA (60 min)** — derive (7) through (8) and run criterion 4. Look at
   the angle gap against PCA ($5.4^\circ$ versus $78.7^\circ$), then build a task in which **slow is
   useless** via problem P5(ii). The conclusion is that the axis an objective picks has to match the
   task.
6. **The two papers and the open problems (110 min)** — R3M (the objective) → VC-1 (the large
   comparison). Write the one-page note for each; this is **not** optional. In each note, write one
   line on whether that paper's probe passes the diagnostic of (6).

**Passing bar**: you can derive (1) and (2) from a blank page, say why the reversal happens only at
$K=5$, explain the diagnostic (6) and its premise, derive why CCA picks the slow axis, and you hold
code satisfying the four acceptance criteria plus notes on the two papers.
