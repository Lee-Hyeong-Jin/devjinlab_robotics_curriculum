---
id: s4-vla-architectures
lang: en
title: VLA architectures and action representations
summary: >-
  Derive, from high-resolution quantization theory, the error incurred when actions are discretized
  into tokens, and show with the Panter-Dite formula and measurements that **the common practice of
  equal-mass (quantile) bins is worse than uniform bins**. Then derive, down to an exact crossover
  sample size, when freezing a pretrained representation pays, and compute how a regression (MSE)
  head collapses to an infeasible midpoint on a multimodal action distribution while just two
  tokens avoid it.
objectives:
  - Derive that the mean squared error of uniform quantization is $\Delta^2/12$.
  - State via the Panter-Dite formula that the MSE-optimal bin density is proportional to $p^{1/3}$ and explain why quantile bins are not optimal.
  - Derive and compute the condition under which a frozen pretrained representation pays, and its crossover sample size $N^\star$.
  - Show that on a multimodal action distribution the regression head's cost is the squared half-gap between modes.
  - Explain that a token head's cost is governed by **center-mode alignment** rather than bin width.
  - State the case for flow and diffusion heads, and its price, by comparing the loss of three heads.
tags: [vla, action-tokenization, quantization, diffusion-policy, transfer, research]
---

# VLA architectures and action representations

## Setup and notation

This lesson uses the bias-variance ledger of `s4-robot-data-scaling` and the multimodal-expert
discussion of `c8-imitation-learning`. Additional **recommended** background:

- Probability: conditional distributions, the high-resolution approximation, Jensen's inequality.
- Analysis: change of variables in integrals, Hölder's inequality (used once in the Panter-Dite
  derivation).
- Linear algebra: orthogonal projection and residuals (the approximation error of a pretrained
  representation is read as a projection).

Notation:

| Symbol | Meaning |
|---|---|
| $a \in \mathbb{R}^{d}$ | the action; assuming per-dimension independent quantization, $d$ enters only as a multiplier |
| $B$ | tokens (bins) per dimension; $\Delta$ is the bin width |
| $c_1,\dots,c_B$ | bin representatives (the action a token decodes to) |
| $p(a)$ | the conditional density of the expert's actions |
| $\mathrm{MSE}_B$ | the quantization error $\mathbb{E}\big[(a - c_{k(a)})^2\big]$ |
| $\phi_{\mathrm{pre}}$ | the frozen pretrained representation, of dimension $p_{\mathrm{pre}}$ |
| $\phi_{\mathrm{task}}$ | a task-specific (or full) representation, $p_{\mathrm{task}} > p_{\mathrm{pre}}$ |
| $\varepsilon_{\mathrm{approx}}$ | the **approximation error** of the frozen representation: the excess of the best loss achievable in its span |
| $A$ | half the gap between modes of a multimodal distribution (modes at $\pm A$) |

**The confusion this lesson is aimed at.** The advantage of "turn actions into tokens so you can
reuse an LLM" is clear, but **what is paid for it** is often blurred. The price is not one thing
but three: ⓐ quantization error, ⓑ the optimality of the bin allocation, and ⓒ whether
multimodality can be represented at all. Computing all three exactly turns the choice among
"tokens versus regression versus diffusion" from a matter of taste into **a function of the
distribution and the budget**.

## Key results

The bracket gives the derivation depth (the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (the error of uniform quantization) [D2]** — if the density is nearly flat within a bin (the
  high-resolution assumption),
  $$
  \mathrm{MSE}_B \;=\; \frac{\Delta^2}{12}, \qquad \Delta = \frac{a_{\max}-a_{\min}}{B}
    \;\Longrightarrow\; \mathrm{MSE}_B \;\propto\; B^{-2}. \tag{1}
  $$
  Quantizing $d$ dimensions independently gives a total of $d\Delta^2/12$. The reproduction task
  matches this for $U(-1,1)$ to a ratio of $0.999$–$1.001$ over $B = 4,\dots,64$.
- **R2 (the MSE-optimal bin density is $p^{1/3}$ — quantile bins are not optimal) [D2]** — for a
  bin density $\lambda(a)$ (with $\int\lambda = 1$ and bin width $\approx 1/(B\lambda)$), the
  high-resolution distortion is
  $$
  D(\lambda) \;=\; \frac{1}{12B^2}\int \frac{p(a)}{\lambda(a)^2}\,da \tag{2}
  $$
  and the density minimizing it is $\lambda^\star \propto p^{1/3}$, with minimum distortion
  $$
  D^\star \;=\; \frac{1}{12B^2}\left(\int p(a)^{1/3}\,da\right)^{3} \tag{3}
  $$
  (Panter-Dite). **Quantile bins use $\lambda \propto p$ and so are not optimal.** In the
  reproduction task, for Gaussian actions, quantile bins are **worse** than uniform bins
  ($3.4\times$ at $B=64$) and Lloyd-Max matches (3) to within $1.05$.
- **R3 (when a frozen pretrained representation pays) [D2]** — applying the ledger of
  `s4-robot-data-scaling` R1 to the two representations, the frozen one wins when
  $$
  \varepsilon_{\mathrm{approx}} \;<\; \frac{\sigma^2\,(p_{\mathrm{task}} - p_{\mathrm{pre}})}{N},
  \qquad\text{i.e.}\qquad
  N \;<\; N^\star \;=\; p_{\mathrm{pre}} + 1 + \frac{\sigma^2\,(p_{\mathrm{task}}-p_{\mathrm{pre}})}{\varepsilon_{\mathrm{approx}}} \tag{4}
  $$
  **A better representation (smaller $\varepsilon_{\mathrm{approx}}$) keeps winning for longer.**
  In the reproduction task three representations predict $N^\star$ of $54$, $140$ and $411$, and
  the measured crossovers fall in $(50,80]$, $(120,200]$ and $(400,1200]$ respectively.
- **R4 (the collapse of a regression head on a multimodal distribution) [D2]** — with modes at
  $\pm A$ of equal weight and a task cost that is the **squared distance to the nearer mode**, the
  cost of a regression head, which outputs the conditional mean, is
  $$
  \mathbb{E}\big[\min\{(a-A)^2,(a+A)^2\}\big]\Big|_{a=\mathbb{E}[a]=0} \;=\; A^2 \tag{5}
  $$
  which is the **worst possible** output, independent of how the modes are spread. A head that
  samples from the true distribution pays only the within-mode variance. Measured: regression head
  $0.9985$ ($A^2=1$), sampling head $0.0100$ ($\mathrm{spread}^2$).
- **R5 (a token head's cost is governed by alignment, not bin width) [D2]** — for a sharply peaked
  distribution the averaging argument of (1) does not apply and the cost is set by the **distance
  from the nearest representative to a mode**:
  $$
  \mathrm{cost}(B) \;\approx\; \min_k (c_k - A)^2 . \tag{6}
  $$
  It is therefore **not monotone** in $B$. Measured: at $B=2$ the representatives land exactly on
  the modes at $\pm1$ for a cost of $0.0000$; $B=4$ gives $0.2500$, $B=8$ gives $0.0625$ and
  $B=16$ gives $0.0156$. So **two tokens can beat sixteen, and either beats the regression head
  ($A^2=1$).**

## Derivation

### R1 — the $\Delta^2/12$ of uniform quantization

Let bin $k$ be $[e_k, e_{k+1})$ of width $\Delta$ with representative the midpoint $c_k$. The
high-resolution assumption is that "$\Delta$ is small enough that $p(a)$ is nearly constant within
each bin". Then the conditional error within bin $k$ is distributed as
$a - c_k \sim \mathrm{Unif}(-\Delta/2, \Delta/2)$ and

$$
\mathbb{E}\big[(a-c_k)^2 \mid k\big] = \int_{-\Delta/2}^{\Delta/2} \frac{u^2}{\Delta}\,du
  = \frac{\Delta^2}{12}.
$$

Taking the expectation over bins gives the same value, which is (1). Under per-dimension
independent quantization the errors are independent and add, so the total MSE is $d\Delta^2/12$.

**Why the midpoint is optimal.** With the bins fixed, the optimal representative is the bin's
**conditional mean** (the loss is squared error), and under the high-resolution assumption that
mean equals the midpoint. If $p$ is tilted within a bin the optimal representative shifts off the
midpoint, and that correction is half of what Lloyd-Max iteration does (the other half is moving
the boundary to the midpoint between two representatives).

**Where the assumptions break.** The high-resolution assumption fails when $B$ is small or the
density is peaked. In particular, if the expert's actions are **multimodal**, an entire peak can sit
inside one bin and the conditional error looks nothing like a uniform distribution — then (1) is
the wrong model and (6) of R5 is the right one. Robot actions often put mass on "stop" and "full
speed", so this exception is not exceptional.

### R2 — the optimal bin density and the error of quantile bins

**Step 1: write the distortion in terms of a density.** Describe the bin boundaries by a density
$\lambda(a)$: near position $a$ the bin width is $\Delta(a) \approx 1/(B\lambda(a))$ (with
$\int\lambda = 1$ giving $B$ bins in total). Applying (1) locally and integrating against $p$,

$$
D(\lambda) = \int p(a)\,\frac{\Delta(a)^2}{12}\,da
  = \frac{1}{12B^2}\int \frac{p(a)}{\lambda(a)^2}\,da ,
$$

which is (2).

**Step 2: minimize.** Minimize (2) subject to $\int\lambda = 1$. Hölder's inequality with exponents
$(3, 3/2)$ gives

$$
\int p^{1/3}\,da = \int \Big(\frac{p}{\lambda^2}\Big)^{1/3}\lambda^{2/3}\,da
  \;\le\; \Big(\int \frac{p}{\lambda^2}\Big)^{1/3}\Big(\int \lambda\Big)^{2/3}
  = \Big(\int \frac{p}{\lambda^2}\Big)^{1/3},
$$

and cubing both sides gives $\int p/\lambda^2 \ge \big(\int p^{1/3}\big)^3$, with equality — by
Hölder's equality condition — when $p/\lambda^2 \propto \lambda$, i.e. when

$$
\lambda^\star(a) \;\propto\; p(a)^{1/3} . \tag{7}
$$

Substituting into (2) gives (3).

**Step 3: why quantile bins are not optimal.** Quantile (equal-mass) bins give each bin mass $1/B$,
so $\lambda \propto p$. Since (7) asks for $p^{1/3}$, quantile bins place **too many bins where the
density is high and too few in the tails**. In the tails the bins are wide, the error is large, and
it enters squared — so the distortion contribution is large even though the mass is small. Measured
in the reproduction task ($\mathcal{N}(0,1)$ truncated to $[-3,3]$):

| $B$ | uniform | quantile | Lloyd-Max | (3) Panter-Dite |
|---|---|---|---|---|
| 8 | $4.71\times10^{-2}$ | $4.83\times10^{-2}$ | $3.29\times10^{-2}$ | $3.28\times10^{-2}$ |
| 16 | $1.18\times10^{-2}$ | $1.85\times10^{-2}$ | $8.62\times10^{-3}$ | $8.19\times10^{-3}$ |
| 64 | $7.36\times10^{-4}$ | $2.47\times10^{-3}$ | $6.90\times10^{-4}$ | $5.12\times10^{-4}$ |

At $B=64$ the quantile bins are **3.4 times worse** than uniform. The practice of "split by
quantiles to match the action distribution" is intuitive but is the **wrong direction** under
squared error.

**Where the assumptions break.** (2) is a high-resolution approximation and is inaccurate for small
$B$ (the trace of this is that at $B=4$ Lloyd-Max comes out **below** (3) — measured ratio
$0.877$). It also assumes squared error is a good proxy for task cost. If the cost is of the form
"reaching any mode suffices", (6) is the right model and the $p^{1/3}$ rule is beside the point.

### R3 — when a frozen representation pays

Apply the ledger of `s4-robot-data-scaling` R1 to each representation. The frozen one has a small
dimension and hence small variance, but it incurs an **approximation error**:

$$
L_{\mathrm{pre}}(N) \approx \sigma^2 + \varepsilon_{\mathrm{approx}}
  + \frac{\sigma^2 p_{\mathrm{pre}}}{N - p_{\mathrm{pre}} - 1}, \qquad
L_{\mathrm{task}}(N) \approx \sigma^2 + \frac{\sigma^2 p_{\mathrm{task}}}{N - p_{\mathrm{task}} - 1}.
$$

$\varepsilon_{\mathrm{approx}}$ is the **orthogonal projection residual** onto the frozen feature
span (zero for the full representation). Comparing the two and approximating the denominators by
$N$ for $N \gg p$,

$$
L_{\mathrm{pre}} < L_{\mathrm{task}}
  \iff \varepsilon_{\mathrm{approx}} < \frac{\sigma^2 (p_{\mathrm{task}} - p_{\mathrm{pre}})}{N},
$$

which is (4). Keeping the denominators as $N-p-1$ puts the crossover at
$N^\star = p_{\mathrm{pre}} + 1 + \sigma^2(p_{\mathrm{task}}-p_{\mathrm{pre}})/\varepsilon_{\mathrm{approx}}$.

**How to read it.** The value of pretraining is **"borrowed variance savings while data is
scarce"**, and $N^\star$ is its shelf life. The better the representation
($\varepsilon_{\mathrm{approx}} \downarrow$) the longer the shelf life. In the reproduction task,
reducing the approximation error through
$5.6\times10^{-3} \to 7.5\times10^{-4} \to 1.1\times10^{-4}$ raises the predicted $N^\star$ through
$54 \to 140 \to 411$, and the measured crossovers fall in the bracketing intervals $(50,80]$,
$(120,200]$ and $(400,1200]$.

**Where the assumptions break.** (4) presumes the two representations see the **same noise level**.
If the pretrained representation mixes in directions irrelevant to the task, the effective noise
grows and the comparison is unfair. It also assumes the "full representation" can be trained from
scratch — in practice, as $p_{\mathrm{task}}$ grows, optimization itself gets harder, so the
measured $L_{\mathrm{task}}$ is worse than this formula and pretraining looks correspondingly
better. **Reporting that difference as "the value of the representation" overstates it** (problem
P5).

### R4 and R5 — multimodality: regression collapse and token alignment

**The regression head's collapse.** Suppose the expert uses $+A$ and $-A$ with equal probability at
the same observation. The deterministic output minimizing squared error is the conditional mean,
$0$. If the task cost is of the form "reaching either mode succeeds", i.e.
$\min\{(a-A)^2, (a+A)^2\}$, then the cost at $a=0$ is $A^2$, which is the **worst** among possible
outputs. That is (5), and it is the same structure as the multimodal-expert item of
`c8-imitation-learning` ("the average of two avoidance paths drives into the obstacle").

**The token head.** A token head can represent a distribution and so can pick one of the modes. Its
cost is set by the **distance from the nearest representative to that mode** — equation (6). With
uniform bins over $[-2A, 2A]$, the representatives are $c_k = -2A + (k+\tfrac12)\cdot 4A/B$ and

$$
\min_k \lvert c_k - A\rvert = \begin{cases}
  0 & B = 2 \;(\text{representatives } \pm A),\\
  A/2 & B = 4 \;(\text{representatives } \pm A/2, \pm 3A/2),\\
  A/4 & B = 8,\\
  A/8 & B = 16 .
\end{cases}
$$

So the costs are $0,\ A^2/4,\ A^2/16,\ A^2/64$, matching the measurements $0.0000,\ 0.2500,\
0.0625,\ 0.0156$ ($A=1$) **exactly**. That $B=2$ beats $B=4$ looks at odds with the $\Delta^2/12$
intuition of (1), but (1) is an **average** for a flat density, and here the peaks are sharp so
alignment is everything.

**Comparing the three heads (measured, $A=1$, within-mode standard deviation $0.1$)**

| Head | Cost | Theory |
|---|---|---|
| regression (MSE) | $0.9985$ | $A^2 = 1$ |
| token $B=2$ | $0.0000$ | $\min_k(c_k-A)^2 = 0$ |
| token $B=4$ | $0.2500$ | $A^2/4$ |
| sampling (flow, diffusion) | $0.0100$ | within-mode variance $=0.01$ |

**How to read it — why flow and diffusion heads.** A token head is excellent when the alignment
happens to be right, but **the alignment cannot be guaranteed** (the action range and bin count
differ per task, and the mode locations are unknown). A sampling head does not depend on alignment
and gets down to the within-mode variance. The price is ⓐ several function evaluations at inference
(diffusion steps) and ⓑ a training objective that is score matching rather than a likelihood,
making diagnosis harder. **The choice is not taste but a function of "do you know where the modes
are / do you have the inference budget".**

**Where the assumptions break.** (5) and (6) assume the cost is "distance to the nearer mode". If
the cost is smooth and convex in the mean action (a tracking error, say), the conditional mean is
the **right** answer and the regression head is optimal. So the rule is not "multimodal, therefore
diffusion" but "**multimodal and the cost is mode-selective**, therefore diffusion". Missing that
distinction turns a perfectly good regression head into a diffusion head that only costs more at
inference.

## Proof sketch

### R2 — the optimal bin density $\lambda^\star \propto p^{1/3}$ [D2, stated as a proof]

**Hypotheses** H1: high resolution — $B$ is large enough that $p$ is nearly constant within each
bin. H2: $p$ is continuous on a bounded support with $\int p^{1/3} < \infty$. H3: the
representative is the bin midpoint (or the conditional mean).
**Conclusion** C: the density minimizing (2) is (7) and the minimum distortion is (3).

**Strategy**: write the distortion as a functional of the density and pin the minimizer with
**Hölder's equality condition**.

1. Localize (1) to get $D(\lambda) = \frac{1}{12B^2}\int p/\lambda^2$. Uses: H1, H3.
2. Hölder with exponents $(3, 3/2)$ gives
   $\int p^{1/3} \le (\int p/\lambda^2)^{1/3}(\int\lambda)^{2/3}$. Uses: H2.
3. Substitute $\int\lambda = 1$ and cube to get the lower bound $(\int p^{1/3})^3$ → (3).
4. Hölder's equality condition $p/\lambda^2 \propto \lambda$ gives (7) → C.

**Delete one hypothesis**: dropping H1 invalidates the localization of step 1, and for small $B$ (3)
is neither a lower nor an upper bound (in the measurement Lloyd-Max at $B=4$ came out below (3)).
If $\int p^{1/3}$ diverges in H2 (a heavy-tailed distribution) the optimal distortion is not finite
and the bin allocation is undefined — which is why actions must be clipped first.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1·R2)** Derive (1), then compute to first order how far the optimal
representative shifts off the midpoint when $p$ is linearly tilted within the bin. By what order
does that correction reduce the MSE?
*Solution sketch*: writing $p(a) \approx p_0(1 + \kappa(a-c))$ and computing the conditional mean
shifts the optimal representative by $\kappa\Delta^2/12$ off the midpoint. The MSE reduction is of
the order of its square, $O(\Delta^4)$, hence **negligible** at high resolution — which is why
Lloyd-Max's gain comes from **relocating boundaries** (matching $\lambda$ to $p^{1/3}$) rather than
from correcting representatives.

**P2 (proof, ★★★, R2)** Re-derive (7) by variational calculus instead of Hölder: introduce a
Lagrange multiplier for $\int\lambda=1$ and solve $\delta D/\delta\lambda = 0$. Then write the
distortion of quantile bins ($\lambda\propto p$) and uniform bins ($\lambda$ constant) via (2), and
find the condition on the distribution for **quantile to beat uniform**.
*Strategy and key inequality*: the variational condition is $-2p/\lambda^3 + \nu = 0$, hence
$\lambda \propto p^{1/3}$. Comparing quantile with uniform reduces to comparing $\int p^{-1}$ with
$\int p$, and quantile approaches uniform **only when $p$ is nearly flat** (and never beats
Lloyd-Max). The expansion is withheld.

**P3 (numerical, ★, R1·R3·R5)** Compute (ⓐ) the MSE of uniformly quantizing $[-1,1]$ with $B=32$,
(ⓑ) $N^\star$ from (4) with $\varepsilon_{\mathrm{approx}} = 7.5\times10^{-4}$,
$\sigma^2 = 0.01$, $p_{\mathrm{pre}}=32$ and $p_{\mathrm{task}}=40$, and (ⓒ) the cost from (6) with
$A=1$, uniform bins on $[-2,2]$ and $B=4$.
*Answer*: (ⓐ) $\Delta = 2/32 = 0.0625$ and $\mathrm{MSE} = 0.0625^2/12 = 3.255\times10^{-4}$
(tolerance $10^{-7}$). (ⓑ) $32 + 1 + 0.01\cdot8/7.5\times10^{-4} = 33 + 106.7 = 139.7$
(tolerance $0.5$). (ⓒ) the representatives are $\pm0.5, \pm1.5$, so
$\min_k(c_k-1)^2 = 0.25$ (exact).
Check: compare (ⓐ) with the reproduction task's measured $3.257\times10^{-4}$ for a ratio of
$1.001$, and confirm that the $139.7$ of (ⓑ) lies inside the measured crossover interval
$(120, 200]$.

**P4 (implementation, ★★, R1·R2·R3·R5)** Implement the reproduction task and pass all four criteria.
*Rubric*: ⓐ Lloyd-Max is run to convergence (report the iteration count and the change in
representatives); ⓑ the representatives of the quantile bins are the **bin conditional means**
(using boundary midpoints makes quantile look worse and the comparison unfair); ⓒ the integral in
(3) is computed on a fine enough grid; ⓓ in the transfer experiment the approximation error is
computed **directly as an orthogonal projection residual** (not estimated from a learning curve);
ⓔ in the multimodal experiment the cost is written explicitly as `min((a-A)^2, (a+A)^2)` and noted
as a task assumption.

**P5 (counterexample, ★★, R4·R5·R3)** Show that **all three** claims are false: (i) "more tokens is
always better"; (ii) "if the action distribution is multimodal you must not use a regression head";
(iii) "if a frozen pretrained representation beats one trained from scratch, the representation is
good".
*Property checklist*: (i) the measurement where $B=2$ beats $B=4$ (alignment dominates);
(ii) if the cost is convex in the mean action, the conditional mean is **optimal** and the
regression head is right — multimodality only means something together with the cost structure;
(iii) at large $p_{\mathrm{task}}$ optimization gets harder, so $L_{\mathrm{task}}$ can be worse
than (4) predicts, and that difference is **optimization difficulty**, not the value of the
representation. A fair comparison adds a random-projection baseline at the frozen representation's
dimension.

**P6 (paper, ★★, R1·R2·R5)** Read RT-2 (§3–4), OpenVLA (§3, §5) and $\pi_0$ (§3–4) and write, in at
most three sentences each: (i) whether each paper discretizes actions or keeps them continuous and,
if discretized, whether the bin allocation is uniform, quantile or learned; (ii) which of (3) and
(6) is the right framework for evaluating that choice; (iii) whether the three papers **measure**
the price of their action representation and, if so, with what metric.
*Grading rubric*: (i) passes if it distinguishes RT-2's and OpenVLA's quantile (or uniform)
tokenization from $\pi_0$'s flow-matching head. (ii) the distinction that flat axes call for (3) and
peaked ones for (6). (iii) passes if it notes that success rate is usually all that is reported and
quantization error is not measured separately. Writing only "performance is good" fails.

**P7 (derivation, ★★, R3)** Re-derive (4) without approximating the denominators, write the exact
expression for $N^\star$, and state what happens in the limits
$p_{\mathrm{pre}} \to p_{\mathrm{task}}$ and $\varepsilon_{\mathrm{approx}} \to 0$.
*Solution sketch*: solving
$\sigma^2 p_{\mathrm{pre}}/(N-p_{\mathrm{pre}}-1) + \varepsilon
= \sigma^2 p_{\mathrm{task}}/(N-p_{\mathrm{task}}-1)$ for $N$ gives a quadratic. As
$p_{\mathrm{pre}}\to p_{\mathrm{task}}$ the crossover does not go to infinity — with
$\varepsilon>0$ it disappears (the frozen one always loses). As $\varepsilon \to 0$,
$N^\star\to\infty$: a lossless representation means the smaller one always wins.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions
(the "Reading papers" section of lesson `f0-how-to-read-this-track`).

1. **Brohan et al., "RT-2: vision-language-action models transfer web knowledge to robotic control"
   (2023, CoRL)** — role: `seminal`. <https://arxiv.org/abs/2307.15818> — §3–4.
   Why read it: the origin of the design that turns actions into **text tokens** so a VLM can be
   reused directly, and a case study of how that price reads through (1) and (6).
   Extra questions: ⓐ how were the number of action bins and their range chosen, and does the paper
   give a rationale? ⓑ in the framework of (4), what do the experiments offered as evidence of "web
   knowledge transfer" actually show?
2. **Kim et al., "OpenVLA: an open-source vision-language-action model" (2024, CoRL)** — role:
   `standard`. <https://arxiv.org/abs/2406.09246> — §3 and §5.
   Why read it: being an open implementation, the details of tokenization and normalization are
   visible, and its fine-tuning experiments can be compared with the $N^\star$ of (4).
   Extra questions: ⓐ point out where the (quantile-based) action normalization conflicts with (7).
   ⓑ is there an experiment varying the fine-tuning data volume, and if so is a crossover visible?
3. **Black et al., "$\pi_0$: a vision-language-action flow model for general robot control" (2024,
   arXiv)** — role: `frontier`. <https://arxiv.org/abs/2410.24164> — §3–4.
   Why read it: the case for dropping discrete tokens in favour of a **flow-matching** head can be
   evaluated with R4 and R5.
   Extra questions: ⓐ is the advantage of a continuous head that the authors cite the same as the
   alignment problem of (6), or a different one? ⓑ do they report the trade-off between the number
   of inference steps and performance — and if not, what cannot be known?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation? (4) what is guaranteed and **what is not**?
(5) independent and dependent variables, and the baselines — were they tuned fairly? (6) does the
metric match the claim, and are variance and seeds reported? (7) what information needed for
reproduction is missing? (8) if the result were wrong, which assumption would you doubt first?
(9) compute and memory cost, and real-time feasibility? (10) what would you change to go beyond
this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: under **three minutes** on a laptop CPU, under
500 MB, numpy only. **No GPU is needed.** Fine-tuning a real VLA is the **optional extension (R4)**
below.

**Acceptance criteria** — all four must hold.

1. **Verifying (1)**: quantizing $U(-1,1)$ with uniform bins at $B \in \{4,8,16,32,64\}$, the MSE
   divided by $\Delta^2/12$ lies in $[0.99,\,1.01]$ for **all** (measured $1.0003$, $0.9994$,
   $1.0002$, $1.0005$, $0.9990$; $4\times10^5$ samples).
2. **(3) and the inferiority of quantile bins**: for actions from $\mathcal{N}(0,1)$ truncated to
   $[-3,3]$, ⓐ Lloyd-Max's MSE divided by (3) lies in $[0.95,\,1.10]$ for
   $B \in \{8,16,32\}$ (measured $1.005$, $1.052$, $1.064$); ⓑ **quantile bins are worse than
   uniform**: $\mathrm{MSE}_{\text{quantile}} > \mathrm{MSE}_{\text{uniform}}$ at every
   $B \in \{8,16,32,64\}$, with a ratio $\ge 3.0$ at $B=64$ (measured
   $2.47\times10^{-3}/7.36\times10^{-4} = 3.35$); ⓒ confirm that (3) is not a lower bound at $B=4$
   (measured ratio $0.877$ — evidence that the high-resolution assumption has broken).
3. **The crossover of (4)**: for three frozen representations with different approximation errors
   ($\varepsilon_{\mathrm{approx}} = 5.6\times10^{-3},\ 7.5\times10^{-4},\ 1.1\times10^{-4}$ at
   $p_{\mathrm{pre}} = 24, 32, 36$ with $p_{\mathrm{task}} = 40$ and $\sigma=0.1$), the $N^\star$
   predicted by (4) — $54,\ 140,\ 411$ — falls **inside the measured crossover interval**
   (measured $(50,80]$, $(120,200]$, $(400,1200]$). Compute the approximation error directly as an
   orthogonal projection residual.
4. **Multimodal collapse and token alignment**: with modes at $\pm1$, within-mode standard
   deviation $0.1$ and cost $\min\{(a-1)^2,(a+1)^2\}$, ⓐ the regression head's cost is
   $1.00 \pm 0.01$ (measured $0.9985$); ⓑ the sampling head's cost is $0.0100 \pm 0.0005$;
   ⓒ with uniform bins on $[-2,2]$ the token head's cost at $B=2,4,8,16$ matches
   $0,\ 0.25,\ 0.0625,\ 0.0156$ to within $10^{-3}$ and is **not monotone in $B$**; ⓓ at every $B$
   the token head beats the regression head.

**Baselines**: ⓐ uniform bins — criterion 2 compares quantile and Lloyd-Max against them.
ⓑ the sampling head (true distribution) — the lower bound for criterion 4. ⓒ a **random
projection** at the frozen representation's dimension — in criterion 3 this separates "it won
because the representation is good" from "it won because the dimension is small" (problem P5 (iii)).

**Optional extension (R4, may need a GPU — not required)**: fine-tune an OpenVLA-style public
checkpoint on a small task and vary the number of action tokens to see whether the success-rate
curve has the shape of criterion 4 (alignment-dependent, non-monotone). **No acceptance criterion is
set** — differences in preprocessing and normalization may prevent the numbers from reproducing.
The purpose is to check whether the reduced model's conclusion shows up **qualitatively** in a real
VLA.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The ratio in criterion 1 exceeds $1.01$ | too few samples, so the MSE estimate is noisy | raise the sample count to $4\times10^5$ and print the standard error of the ratio |
| The ratio in criterion 2ⓐ exceeds $1.3$ | Lloyd-Max has not converged | print the change in representatives per iteration — it must fall below $10^{-6}$ |
| Quantile bins come out **better** than uniform | the quantile representatives were set to boundary midpoints (they must be conditional means) | print the difference between the representatives and the bin conditional means |
| No crossover appears in criterion 3 | the approximation error is so large that $N^\star$ is below $p$ | compute $N^\star$ first — it must exceed $p_{\mathrm{pre}}+1$ for a crossover to be visible |
| The frozen one always wins in criterion 3 | the full representation was fitted at $N \le p_{\mathrm{task}}+2$ | report the full representation only for $N > p_{\mathrm{task}}+2$ |
| Criterion 4ⓒ does not match $\Delta^2/12$ | (1) was applied to a peaked distribution | switch to (6) and compute $\min_k(c_k-A)^2$ — this is the central lesson of criterion 4 |

## Open problems

- **(open problem) Allocating action bins against the task cost** — (7) is the optimal density under
  **squared error**. Real task costs are mode-selective (R5), asymmetric, or contain constraints.
  There is no general theory giving the optimal bins for a known cost, and practice uses uniform or
  quantile bins (both at odds with (7)). Current approaches: the classical result of
  [Panter & Dite 1951](https://doi.org/10.1109/JRPROC.1951.230446), sidestepping it with a
  continuous head ([$\pi_0$](https://arxiv.org/abs/2410.24164)). What is missing: optimal
  quantization for a task cost.
- **(open problem) Separating the value of a pretrained representation from optimization
  difficulty** — (4) counts only approximation error and variance. In a real comparison, "trained
  from scratch" may lose because of optimization and regularization difficulty, and there is no
  experimental design that separates that component. Reported transfer gains may therefore be
  systematically overstated. Current approaches: random-projection and frozen-random-feature
  baselines (`s4-pretrained-representations`), the ablations of
  [OpenVLA](https://arxiv.org/abs/2406.09246). What is missing: a fair-comparison protocol isolating
  the value of the representation.
- **(open problem) The inference-budget versus performance trade-off of continuous heads** —
  diffusion and flow heads avoid the alignment problem but pay inference steps. Reducing the step
  count degrades the distribution approximation, and there is no quantitative model of how that
  degradation propagates to task success. In real-time control this dominates the design. Current
  approaches: [diffusion policy](https://arxiv.org/abs/2303.04137),
  [$\pi_0$](https://arxiv.org/abs/2410.24164),
  [action chunking](https://arxiv.org/abs/2304.13705). What is missing: a bound from the step budget
  to task performance.
- **(open problem) Separating multimodality from the floor** — the floor in
  `s4-robot-data-scaling` contains demonstration multimodality, and multimodality is a component
  that a head choice **can remove**, as in (5). Yet there is no procedure for measuring what
  percentage of a given dataset's floor is multimodality. What is missing: a way to estimate the
  multimodality component of the floor from data.

## Concept check

Run `rc quiz s4-vla-architectures`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

The five items cover: what the MSE-minimizing bin density is proportional to; whether more action
tokens always reduce the task cost on a multimodal distribution; why the regression head's cost is
$A^2$; the condition under which a frozen pretrained representation wins; and whether multimodality
by itself calls for a diffusion head.

## How to study this stage

1. **Do $\Delta^2/12$ by hand (30 min)** — derive (1) and run criterion 1 of the reproduction task
   to watch the ratio sit on $1.000$. That one line is the reference point for every later
   quantization argument.
2. **Derive $p^{1/3}$ and refute the quantile practice (75 min)** — go from (2) to (7) with Hölder,
   then redo it by variational calculus in problem P2. Then run criterion 2ⓑ and see for yourself
   that **quantile is worse than uniform**. One measurement that contradicts intuition sticks longer
   than a chapter of text.
3. **Compute the transfer crossover and confirm it (60 min)** — derive (4), compute
   $N^\star = 139.7$ in problem P3(ⓑ), and check in criterion 3 that it falls inside the measured
   interval $(120,200]$. This is the step where "pretraining helps" becomes a **statement
   conditional on data volume**, as a number.
4. **Reproduce the multimodal collapse (75 min)** — run criterion 4 and watch the regression head
   collapse to $A^2$ and $B=2$ beat $B=4$. Then **change the cost to a convex tracking error** and
   confirm the regression head becomes optimal (problem P5 (ii)) — that contrast is the conclusion
   of this lesson.
5. **Read the three papers along the axis of representation choice (140 min)** — RT-2 (tokens) →
   OpenVLA (open tokenization details) → $\pi_0$ (flow head). Write the one-page note for each; this
   is **not** optional. In each note, write one line on which of (3) and (6) that paper's action
   representation should be evaluated with.
6. **End at what cannot be done (70 min)** — pick the open problem of quantization against the task
   cost and write a paragraph on how the optimal bin allocation would change if criterion 4's cost
   were made asymmetric (missing one mode causes a collision, say).

**Passing bar**: you can derive (1) and (7) from a blank page, explain why quantile bins are not
optimal, compute the $N^\star$ of (4), quote numerically both the $A^2$ collapse of the regression
head and the non-monotonicity of token alignment, and you hold code satisfying the four acceptance
criteria plus notes on the three papers.
