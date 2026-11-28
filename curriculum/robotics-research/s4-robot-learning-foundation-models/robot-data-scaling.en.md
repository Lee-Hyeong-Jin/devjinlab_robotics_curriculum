---
id: s4-robot-data-scaling
lang: en
title: Large-scale robot data and scaling
summary: >-
  Derive from the excess risk of least squares why a scaling law has the form "power-law term plus
  a floor that does not shrink", and show in closed form that mixing datasets that disagree
  creates a **bias floor no number of samples can remove**. The sample size at which that floor
  overtakes the variance term is the collapse condition — the point past which more data does not
  help. The lesson closes by deriving how the optimal domain weight (rebalancing) depends on the
  size of the disagreement and on how much target data you have, and confirms it numerically.
objectives:
  - Derive $L(N) = \sigma^2 + \sigma^2 p/(N-p-1)$ from the excess risk of least squares.
  - Explain separately where the power-law exponent and the floor of a scaling law come from.
  - Derive the asymptotic bias of a data mixture in closed form and show it is independent of $N$.
  - Compute the collapse condition (the sample size at which the bias floor overtakes the variance term).
  - Derive how the domain weight $\gamma^\star$ depends on the disagreement and on the amount of target data.
  - Decide numerically whether collecting more data or fixing the mixing ratio is the effective move.
tags: [scaling-laws, robot-data, data-mixture, open-x-embodiment, research]
---

# Large-scale robot data and scaling

## Setup and notation

This is the first lesson of the S4 specialization module. It uses the distribution-shift viewpoint
of `c8-offline-rl` and the average-objective discussion of `c8-generalization-sim2real`.
Additional **recommended** background:

- Linear algebra: normal equations, pseudo-inverses, quadratic forms of symmetric positive definite
  matrices.
- Probability: conditional expectation, the bias-variance decomposition of an estimator, the law of
  large numbers.
- Statistics: the distribution of the least-squares estimator, degrees of freedom.

Notation:

| Symbol | Meaning |
|---|---|
| $\phi(x) \in \mathbb{R}^p$ | a fixed feature map (a frozen representation or random features); $p$ is the **number of learned parameters** |
| $w \in \mathbb{R}^p$ | the linear policy (or regression) coefficients; the truth is $w_A$, $w_B$ per domain |
| $\sigma^2$ | the variance of the label noise — the **irreducible floor** (aleatoric) |
| $N$ | the number of training samples, split as $N_A$, $N_B$ per domain |
| $\beta$ | the mixing fraction: the share of domain B in the total $N$ |
| $\gamma$ | the loss weight on domain-B samples (rebalancing); $\gamma=1$ is plain concatenation, $\gamma=0$ is discarding |
| $\Sigma_D$ | the feature second moment $\mathbb{E}_D[\phi\phi^\top]$ of domain $D$ |
| $\Delta$ | the domain disagreement, $\Delta = w_B - w_A$ |
| $L_A(\pi)$ | the expected (squared-error) loss on the target domain A |

**Why narrow the scope.** Proving "scaling laws" for deep networks is an open problem. This lesson
derives the **form** of the law exactly in a reduced model: **a linear policy on top of a frozen
representation**. That model matches actual S4 practice (freeze a pretrained representation, train
a small head — `s4-pretrained-representations`) and shows without hiding anything where the
exponent and the floor each come from. Why the extension to deep networks is hard is taken up in
the open problems.

## Self-diagnosis before starting

Since this is the first lesson of module S4, it checks the background for the whole module. All
four items are **gradeable** — solve them on paper in ten minutes and compare with the answers.
Three or more correct: start the module. Prerequisites are **recommended**; the platform does not
lock them.

**D1 (least squares, prerequisite: `r0-linear-algebra-decompositions`)** With a design matrix
$F \in \mathbb{R}^{N\times p}$ of full column rank, write
$\hat{w} = \arg\min_w \lVert y - Fw\rVert_2^2$ via the normal equations, and compute
$\mathrm{Cov}(\hat{w})$ when $y = Fw^\star + \varepsilon$ with $\mathbb{E}[\varepsilon]=0$ and
$\mathrm{Cov}(\varepsilon) = \sigma^2 I$.
*Answer*: $\hat{w} = (F^\top F)^{-1}F^\top y$ and $\mathrm{Cov}(\hat{w}) = \sigma^2 (F^\top F)^{-1}$.

**D2 (degrees of freedom, prerequisite: statistics)** In the same setting, what is the expectation
of the **in-sample** mean squared residual $\frac{1}{N}\lVert y - F\hat{w}\rVert^2$?
*Answer*: $\sigma^2 (N-p)/N$. No tolerance (it is exact). So the training loss comes out **below**
$\sigma^2$, and that difference is exactly the size of the overfit.

**D3 (distribution shift, prerequisite: `c8-generalization-sim2real`)** With
$\lvert J_\xi \rvert \le V_{\max}$, bound $\lvert \mathbb{E}_p[J] - \mathbb{E}_q[J]\rvert$ by
$D_{\mathrm{TV}}(p,q)$.
*Answer*: $\le 2 V_{\max} D_{\mathrm{TV}}(p,q)$.

**D4 (reading a power law, prerequisite: none)** On log-log axes, a line of slope $-1$ expresses
what relation between $L$ and $N$? If $N$ grows tenfold, what happens to $L$?
*Answer*: $L \propto N^{-1}$, so $L$ becomes one tenth (no tolerance). If there is a floor
$L_\infty$, the slope bends toward $0$ at large $N$ — reading that bend as the existence of a floor
is the central reading skill of this lesson.

## Key results

The bracket gives the derivation depth (the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (the form of a scaling law) [D2]** — for least squares on frozen features, assuming a
  Gaussian design and a well-specified model ($y = \phi^\top w_A + \varepsilon$), the expected test
  loss on the target domain is
  $$
  L_A(N) \;=\; \sigma^2\Big(1 + \frac{p}{N-p-1}\Big)
    \;=\; \underbrace{\sigma^2}_{\text{irreducible floor}} \;+\; \underbrace{\frac{\sigma^2 p}{N-p-1}}_{\;\propto\, N^{-1}} \tag{1}
  $$
  **The power-law exponent comes from "effective degrees of freedom over sample size", not from the
  parameter count, and the floor comes from label noise.** The bend in a log-log plot is not a
  limitation of the model: it is **seeing $\sigma^2$**.
- **R2 (the bias floor of a data mixture = the collapse condition) [D2]** — mixing in domain-B
  samples at share $\beta$ with weight $\gamma$ makes the estimator converge, as $N\to\infty$, to
  $$
  \hat{w} \;\longrightarrow\; w_A + \gamma\beta\, M^{-1}\Sigma_B \Delta,
    \qquad M := (1-\beta)\Sigma_A + \gamma\beta\,\Sigma_B \tag{2}
  $$
  and the excess loss on the target domain,
  $$
  \mathrm{bias}(\beta,\gamma) \;=\; \big(\gamma\beta\, M^{-1}\Sigma_B\Delta\big)^\top
    \Sigma_A \big(\gamma\beta\, M^{-1}\Sigma_B\Delta\big) \tag{3}
  $$
  remains **independent of $N$**. So past the sample size at which
  $\mathrm{bias}(\beta,\gamma) > \sigma^2 p/(N-p-1)$, **more data does not help** — that is the
  collapse condition.
- **R3 (the optimal rebalancing weight) [D2]** — splitting the loss into
  $\mathrm{bias}(\gamma) + \sigma^2 p/N_{\mathrm{eff}}(\gamma)$, the optimal weight $\gamma^\star$
  balances the two terms, and
  $$
  \gamma^\star \;\downarrow\; \text{as the disagreement } \lVert\Delta\rVert \text{ grows}, \qquad
  \gamma^\star \;\downarrow\; \text{as the target data } N_A \text{ grows}. \tag{4}
  $$
  The reproduction task measures four combinations: with a small disagreement and little target
  data, $\gamma^\star = 0.4$ and it is **3.16 times better than discarding**. With a large
  disagreement and ample target data, $\gamma^\star = 0$ — **off-domain data is a pure loss**.
- **R4 (why this bites especially hard in robot data) [D1]** — a mixture like Open X-Embodiment is
  **dozens of small, mutually disagreeing domains**. Different robots, grippers, control rates and
  action frames make the correct action for the same observation differ, so $\Delta$ is large. (3)
  says the floor then grows like $\gamma^2\beta^2$, which makes **fixing the weights, not adding
  more datasets**, the dominant design variable.

## Derivation

### R1 — the form of a scaling law

**Setup.** The features $\phi(x)\in\mathbb{R}^p$ are fixed (frozen) and labels are generated as
$y = \phi(x)^\top w_A + \varepsilon$ with $\varepsilon \sim \mathcal{N}(0,\sigma^2)$. Writing the
design matrix of $N$ samples as $F$ and the labels as $y$, $\hat{w} = (F^\top F)^{-1}F^\top y$.

**Step 1: excess risk as a quadratic form.** The expected squared error at a fresh point $x$ is

$$
L_A(\hat{w}) = \mathbb{E}_{x,\varepsilon}\big[(\phi^\top\hat{w} - \phi^\top w_A - \varepsilon)^2\big]
  = \sigma^2 + (\hat{w}-w_A)^\top \Sigma_A (\hat{w}-w_A),
$$

the cross term vanishing because $\varepsilon$ is independent of $x$. **The floor $\sigma^2$
separates out right here.**

**Step 2: covariance of the estimation error.** Since
$\hat{w} - w_A = (F^\top F)^{-1}F^\top \varepsilon$, conditioning on the design $F$,

$$
\mathbb{E}\big[(\hat{w}-w_A)(\hat{w}-w_A)^\top \mid F\big] = \sigma^2 (F^\top F)^{-1}.
$$

So the conditional excess risk is $\sigma^2 \operatorname{tr}\big(\Sigma_A (F^\top F)^{-1}\big)$.

**Step 3: expectation over the design.** If $\phi(x)$ is Gaussian with covariance $\Sigma_A$ then
$F^\top F \sim \mathrm{Wishart}_p(N, \Sigma_A)$, and the mean of the inverse Wishart is
$\mathbb{E}[(F^\top F)^{-1}] = \Sigma_A^{-1}/(N-p-1)$ for $N > p+1$, so

$$
\mathbb{E}\big[\sigma^2\operatorname{tr}(\Sigma_A (F^\top F)^{-1})\big]
  = \frac{\sigma^2}{N-p-1}\operatorname{tr}(\Sigma_A\Sigma_A^{-1}) = \frac{\sigma^2 p}{N-p-1},
$$

which is (1). (For a non-Gaussian design this is not an equality but the asymptotic
$\sigma^2 p/N$ for $N\gg p$.)

**How to read it — the exponent and the floor come from different places.** Plotting (1) on log-log
axes gives a line of slope $-1$ below the crossover with the floor, and a flat floor above it.
Measuring the slope of an empirical curve reads off the **effective degrees of freedom**; measuring
the height of the bend reads off **$\sigma^2$** (label noise, multi-modal demonstrations, sensor
noise). The two are independent, so "enlarge the model to improve the slope" and "lower the floor"
are **different jobs** — which is why Kaplan et al. fit parameters, data and compute separately.

**Where the assumptions break.** We assumed the model is **well specified** ($w_A$ lies in the
feature space). With misspecification, step 1's decomposition acquires an **approximation error
unrelated to the noise** and the floor sits above $\sigma^2$. That floor does not come down with
$N$, so reading an empirical floor as "label noise" is wrong — separating misspecification from
noise requires varying the model capacity and seeing whether the floor moves (problem P5). Also
(1) diverges for $N \le p+1$, where double descent actually appears; the neighbourhood of the
interpolation threshold is outside the scope of this derivation.

### R2 — the bias floor a mixture creates

**Weighted least squares.** Collect $N_A = (1-\beta)N$ samples from domain A and $N_B = \beta N$
from B, weighting B's squared loss by $\gamma$:

$$
\hat{w} = \arg\min_w \; \sum_{i \in A}\big(y_i - \phi_i^\top w\big)^2
  + \gamma \sum_{j \in B}\big(y_j - \phi_j^\top w\big)^2 .
$$

**Step 1: the large-sample limit.** Dividing each sum by $N$, the law of large numbers makes the
objective converge to

$$
(1-\beta)\,\mathbb{E}_A\big[(y-\phi^\top w)^2\big] + \gamma\beta\,\mathbb{E}_B\big[(y-\phi^\top w)^2\big] .
$$

Differentiating in $w$ and setting it to zero gives the **weighted normal equations**

$$
\big[(1-\beta)\Sigma_A + \gamma\beta\Sigma_B\big] w
  = (1-\beta)\Sigma_A w_A + \gamma\beta\Sigma_B w_B \tag{5}
$$

(using $\mathbb{E}_D[\phi y] = \Sigma_D w_D$).

**Step 2: write the solution relative to $w_A$.** Adding and subtracting $M w_A$ on the right of
(5), with $M = (1-\beta)\Sigma_A + \gamma\beta\Sigma_B$,

$$
M w = M w_A + \gamma\beta\Sigma_B (w_B - w_A)
  \;\Longrightarrow\; w_\infty = w_A + \gamma\beta\, M^{-1}\Sigma_B\Delta ,
$$

which is (2). **There is no $N$ anywhere** — that is the point.

**Step 3: carry it to the target loss.** Applying step 1 of R1 to $w_\infty$, the excess loss is
$(w_\infty - w_A)^\top\Sigma_A(w_\infty-w_A)$, and substituting (2) gives (3).

**The collapse condition.** At finite $N$ the loss is approximately

$$
L_A(N,\beta,\gamma) \;\approx\; \sigma^2 \;+\; \mathrm{bias}(\beta,\gamma)
  \;+\; \frac{\sigma^2 p}{N_{\mathrm{eff}}(\beta,\gamma) - p - 1} \tag{6}
$$

and past the $N$ at which the third term drops below the second, **increasing the sample size
barely changes the total loss**. The simplest estimate takes $N_{\mathrm{eff}} \approx N$:

$$
N^\dagger \;=\; p + 1 + \frac{\sigma^2 p}{\mathrm{bias}(\beta,\gamma)} \tag{7}
$$

In the setting of the reproduction task ($p=40$, $\sigma^2=0.01$, $\beta=0.5$, $\gamma=1$,
$\mathrm{bias}=0.01226$) this is $N^\dagger \approx 74$ — **past about 74 samples, collecting more
is nearly pointless.** The measurement: raising $N$ from $200$ to $3200$ (sixteenfold) reduces the
loss only from $0.0291$ to $0.0228$ — **22%** — and it sticks to the floor
$\sigma^2 + \mathrm{bias} = 0.0223$.

**Where the assumptions break.** (7) treats $N_{\mathrm{eff}}$ as $N$, but in a mixture the
effective sample count along the target domain's directions is smaller than $N$, so the transient
lasts longer (measured: at $N=200$ the variance term exceeds (7)'s estimate). So (7) should be read
as a **lower bound** on the collapse point. Also (5) presumes the weight is **constant per
domain**; per-sample importance weights (density ratios) reweight $\Sigma$ and can drive the bias
to zero, but estimating an unknown density ratio makes the variance explode (the same problem as
the effective sample size of `c8-offline-rl` R5).

### R3 — the optimal rebalancing weight

Read the two terms of (6) as functions of $\gamma$. At $\gamma\to0$ the bias is $0$ and the
variance is at its maximum $\sigma^2 p/(N_A-p-1)$. Raising $\gamma$ adds B's samples to the
effective count and shrinks the variance, but the bias grows like $\gamma^2$ (exactly
proportional to $\gamma^2\beta^2$ if one ignores the $\gamma$-dependence of $M$ in (3)). To first
order in small $\gamma$,

$$
L_A(\gamma) \approx \sigma^2 + c_1\gamma^2\beta^2\lVert\Sigma_B\Delta\rVert^2_{\Sigma_A}
  + \frac{\sigma^2 p}{N_A + \gamma N_B - p - 1},
$$

and differentiating in $\gamma$ and setting it to zero gives

$$
2c_1\gamma\beta^2\lVert\Sigma_B\Delta\rVert^2_{\Sigma_A}
  = \frac{\sigma^2 p\,N_B}{(N_A+\gamma N_B-p-1)^2}, \tag{8}
$$

i.e. **$\gamma^\star$ is inversely related to $\lVert\Delta\rVert^2$ and shrinks as $N_A$ grows**
(the right side shrinks) — which is (4). The reproduction task confirms both directions with four
combinations.

| disagreement $\lVert\Delta\rVert$ | target data $N_A$ | $\gamma^\star$ | versus $\gamma=0$ |
|---|---|---|---|
| large (0.6) | small (60) | $0.05$ | $1.15\times$ better |
| large (0.6) | ample (400) | $0$ | off-domain data is a pure loss |
| small (0.08) | small (60) | $0.4$ | **$3.16\times$ better** |
| small (0.08) | ample (400) | $0.4$ | $1.05\times$ better |

**How to read it.** "Collect more data or fix the mixing ratio?" is answered by (8). When target
data is scarce and the domains are similar, mixing wins overwhelmingly (3.16×); when target data is
ample and the domains disagree, mixing **hurts**. Saying "more data is always better" without
separating those two cases is the error this lesson is aimed at.

**Where the assumptions break.** (8) is a first-order approximation that ignores the
$\gamma$-dependence of $M$. When $\gamma\beta$ approaches 1, $M$ tilts toward $\Sigma_B$ and (3)
leaves the $\gamma^2$ regime and **saturates** (visible in the measurement as the loss increase
flattening at large $\gamma$). And with dozens of domains rather than two, $\gamma$ becomes a vector
and (8) a system of equations — estimating its solution from data is an open problem.

## Proof sketch

### R1 — the form of a scaling law [D2, stated as a proof]

**Hypotheses** H1: the features $\phi$ are fixed and
$\Sigma_A = \mathbb{E}_A[\phi\phi^\top] \succ 0$. H2: the model is well specified
($y = \phi^\top w_A + \varepsilon$). H3: $\varepsilon$ is independent of $x$ with mean 0 and
variance $\sigma^2$. H4: $\phi(x)$ is Gaussian and $N > p+1$.
**Conclusion** C: (1).

**Strategy**: separate the excess risk into a quadratic form → conditional covariance → the mean of
the inverse Wishart.

1. Decompose the expected squared error into $\sigma^2$ plus a quadratic form. Uses: H2 and H3 (the
   cross term vanishes).
2. Obtain the conditional covariance from $\hat{w}-w_A = (F^\top F)^{-1}F^\top\varepsilon$.
   Uses: H3.
3. Compute the design expectation of $\operatorname{tr}(\Sigma_A(F^\top F)^{-1})$ with the inverse
   Wishart mean → C. Uses: H4.

**Delete one hypothesis**: dropping H2 (misspecification) adds an $N$-independent approximation
error in step 1, so the floor no longer reads off the noise. Dropping the Gaussianity in H4 breaks
the equality of step 3 and leaves only the **asymptotic** $\sigma^2 p/N$. For $N \le p+1$ the mean
of the inverse does not exist and (1) is undefined.

Omitted: the exact risk in the double-descent region ($N \approx p$) requires random matrix theory.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Re-derive (1) with the design held fixed to obtain
$\sigma^2\operatorname{tr}(\Sigma_A(F^\top F)^{-1})$, then approximate
$F^\top F \approx N\Sigma_A$ to get $\sigma^2 p/N$. Then say in one sentence where the $-p-1$ comes
from.
*Solution sketch*: multiply the conditional covariance $\sigma^2(F^\top F)^{-1}$ by $\Sigma_A$ and
take the trace. Substituting $F^\top F \approx N\Sigma_A$ gives $\operatorname{tr}(I_p)/N = p/N$.
The $-p-1$ appears when averaging over the design, because the mean of the inverse Wishart is
$\Sigma^{-1}/(N-p-1)$ — and that is exactly where the risk diverges as $N$ approaches $p$.

**P2 (proof, ★★★, R2)** Write the limit of (2) rigorously: state the condition under which the
weighted empirical objective converges **uniformly** to the population objective, and conclude
convergence of the minimizer. Then write the **necessary and sufficient** condition for
$\mathrm{bias}(\beta,\gamma) = 0$ in terms of $\Sigma_B$ and $\Delta$.
*Strategy and key inequality*: the objective is strongly convex in $w$ ($M \succ 0$), so uniform
convergence gives convergence of the minimizer (continuity of argmin). The bias vanishes only when
$\Sigma_B\Delta = 0$ — **when the disagreement is invisible in B's feature space** — as long as
$\gamma\beta > 0$. The expansion is withheld.

**P3 (numerical, ★, R1·R2)** With $p = 40$ and $\sigma^2 = 0.01$, compute (ⓐ) the value of (1) at
$N = 200$ and $N = 3200$, (ⓑ) $N^\dagger$ from (7) when $\mathrm{bias} = 0.01226$, and (ⓒ) the $N$
at which the variance term is 10% of the bias.
*Answer*: (ⓐ) $0.01 + 0.4/159 = 0.012516$ and $0.01 + 0.4/3159 = 0.010127$ (tolerance $10^{-6}$).
(ⓑ) $N^\dagger = 41 + 0.4/0.01226 = 73.6$ (tolerance $0.1$). (ⓒ)
$41 + 0.4/0.001226 = 367.3$ (tolerance $0.5$).
Check: compare the two values of (ⓐ) with the reproduction task's $\beta=0$ measurements
$0.012666$ and $0.010162$ and confirm the ratios are near $1.0$ ($1.012$ and $1.003$).

**P4 (implementation, ★★, R1·R2·R3)** Implement the reproduction task and confirm (ⓐ) the
pure-domain curve against (1), (ⓑ) the mixture floor against (3), and (ⓒ) the two directions of
$\gamma^\star$.
*Rubric*: ⓐ $p < N_{\min}$ so the double-descent region is avoided (otherwise (1) does not apply);
ⓑ $\Sigma_A$ and $\Sigma_B$ are estimated from many samples so that (3) is computed **in closed
form**; ⓒ weighted least squares is implemented by $\sqrt{\gamma}$ scaling ($\gamma$ on the loss,
$\sqrt{\gamma}$ on the design matrix); ⓓ 20-seed means and standard errors are reported; ⓔ the
log-log slope is measured on the **excess loss with the floor removed** (measuring the raw loss
bends the slope toward zero).

**P5 (counterexample, ★★, R1·R2)** Show that **both** claims are false: (i) "more data always
helps" and (ii) "data from another domain always hurts". Point to a counterexample for each on the
reproduction task's grid, and (iii) say why concluding "the label noise is $\sigma^2$" from the
log-log floor can be wrong.
*Property checklist*: (i) at $\beta=0.5$, sixteenfold more data improves the loss by only 22% (the
floor dominates); (ii) at disagreement 0.08 with $N_A=60$, $\gamma^\star=0.4$ is 3.16 times better
than $\gamma=0$; (iii) with misspecification the floor is $\sigma^2 +$ approximation error, so one
must vary the capacity $p$ and see whether the floor moves. That is why a scaling study must sweep
**capacity as well**, not only data.

**P6 (paper, ★★, R1·R4)** Read Kaplan et al. 2020 (§1–3, §6) and Open X-Embodiment (§3–5) and
write, in at most three sentences each: (i) how far Kaplan's form of $L(N)$ agrees with (1) and
where it differs; (ii) whether their "irreducible loss" is the same thing as this lesson's
$\sigma^2$; (iii) what plays the role of $\Delta$ in (3) in OXE's mixture design and how the paper
handles it.
*Grading rubric*: (i) passes if it notes both are a power law plus a floor but Kaplan's exponent is
$\approx 0.095$, far from 1, and that this reflects effective degrees of freedom growing with $N$
in a deep network. (ii) the shared property of a component that does not come down with data scale,
and that the paper does not separate label noise from misspecification. (iii) mismatches of robot,
gripper, action frame and control rate, plus the paper's remedies (action-space normalization,
dataset weighting). Writing only "scaling works well" fails.

**P7 (derivation, ★★, R3)** Reduce to one dimension ($p=1$, $\Sigma_A=\Sigma_B=1$), solve (8)
explicitly, and write $\gamma^\star$ in terms of $\Delta$, $N_A$, $N_B$ and $\sigma^2$. What are the
limits as $\Delta\to0$ and as $N_A\to\infty$?
*Solution sketch*: in one dimension
$\mathrm{bias} = (\gamma\beta\Delta/((1-\beta)+\gamma\beta))^2$ and the variance is
$\sigma^2/(N_A+\gamma N_B)$. Differentiating and rearranging leaves $\gamma^\star$ with a term
proportional to $\Delta^{-2}$. As $\Delta\to0$, $\gamma^\star\to\infty$ (mix without limit); as
$N_A\to\infty$, $\gamma^\star\to0$ (the target data alone suffices).

## Paper reading

**Two must-reads.** Write a one-page note on each using the ten fixed questions
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read with three passes and attack questions 4, 5, 6 and 7 in the third.

1. **Kaplan, McCandlish, Henighan et al., "Scaling laws for neural language models" (2020, arXiv)**
   — role: `seminal`. <https://arxiv.org/abs/2001.08361> — §1–3 and §6.
   Why read it: the first systematic report of the power-law-plus-floor **form**, which (1) explains
   in a reduced model.
   Extra questions: ⓐ the authors obtain different exponents for $N$ (parameters), $D$ (data) and
   $C$ (compute) — in the framework of (1), what does "a different exponent" mean is different?
   ⓑ what does the extrapolation claim of §6 guarantee, and what does it not?
2. **Open X-Embodiment Collaboration, "Open X-Embodiment: robotic learning datasets and RT-X
   models" (2023, arXiv / ICRA 2024)** — role: `frontier`.
   <https://arxiv.org/abs/2310.08864> — §3–5.
   Why read it: a case study of what $\Delta$ in (3) concretely is in robot data, and of how mixture
   weights are actually chosen.
   Extra questions: ⓐ does the paper state the procedure by which dataset weights were set, and if
   not, what stood in for it? ⓑ is the difference between the combinations that report positive
   transfer and those that do not explained by the two directions of (4)?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation? (4) what is guaranteed and **what is not**?
(5) independent and dependent variables, and the baselines — were they tuned fairly? (6) does the
metric match the claim, and are variance and seeds reported? (7) what information needed for
reproduction is missing? (8) if the result were wrong, which assumption would you doubt first?
(9) compute and memory cost, and real-time feasibility? (10) what would you change to go beyond
this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: under **two minutes** on a laptop CPU, under
500 MB, numpy only. **No GPU is needed** — the reduced model is a linear head on frozen features.
Extending to real robot data is the **optional extension (R4)** below.

**Generator.** Input dimension $8$, random ReLU features $p = 40$ (fixed and frozen), label noise
$\sigma = 0.1$. Domain B shifts the input mean by $1.5$ and has coefficients
$w_B = w_A + d\cdot\lVert w_A\rVert v$ ($v$ a unit vector, $d$ the size of the disagreement).

```python
import numpy as np

D_IN, P, SIGMA = 8, 40, 0.1


def make_world(seed=0, shift=1.5, disagree=0.6):
    rng = np.random.default_rng(seed)
    W = rng.standard_normal((D_IN, P)) / np.sqrt(D_IN)
    b = rng.standard_normal(P) * 0.1
    wA = rng.standard_normal(P) / np.sqrt(P)
    v = rng.standard_normal(P)
    v /= np.linalg.norm(v)
    muB = np.zeros(D_IN)
    muB[0] = shift
    return dict(W=W, b=b, wA=wA, wB=wA + disagree * np.linalg.norm(wA) * v, muB=muB)


def sample(w, n, domain, rng):
    X = rng.standard_normal((n, D_IN)) + (w["muB"] if domain == "B" else 0.0)
    F = np.maximum(X @ w["W"] + w["b"], 0.0)
    tgt = w["wA"] if domain == "A" else w["wB"]
    return F, F @ tgt + SIGMA * rng.standard_normal(n)
```

Implement weighted least squares by scaling the design matrix by $\sqrt{\gamma}$ (equivalent to
weighting the loss by $\gamma$). Estimate the test risk on domain A with 40,000 samples.

**Acceptance criteria** — all four must hold.

1. **Agreement with (1)**: at $\beta=0$ and $N \in \{120, 200, 400, 800\}$, the 20-seed mean excess
   loss $L_A - \sigma^2$ divided by $\sigma^2 p/(N-p-1)$ lies in $[0.95,\,1.25]$ for **all four**
   (measured $1.165$, $1.019$, $1.101$, $1.057$). Exclude $N = 60$ and $N = 3200$ — the former is
   outside the asymptotic regime and the latter is dominated by estimation noise — and **report that
   reason** (measured ratios $1.363$ and $1.358$).
2. **The power-law slope**: over the same range, the regression slope of $\log(L_A-\sigma^2)$
   against $\log N$ is $-1 \pm 0.15$. Report alongside it that **measuring the raw $\log L_A$ bends
   the slope toward $0$**, showing why the floor must be subtracted.
3. **Agreement of the mixture floor with (3)**: at $N = 25600$, $\gamma=1$ and
   $\beta \in \{0.25, 0.5, 0.75\}$, the measured excess loss $L_A - \sigma^2$ divided by the closed
   form (3) lies in $[0.95,\,1.20]$ (measured $1.048$, $1.024$, $1.017$). Estimate $\Sigma_A$ and
   $\Sigma_B$ from 400,000 samples. Report at the same time that at $\beta=0.5$, raising $N$ from
   $200$ to $3200$ (sixteenfold) reduces the loss only from $0.0291$ to $0.0228$ — **22%** — and it
   sticks to the floor $0.0223$: the collapse condition measured.
4. **Both directions of $\gamma^\star$**: with $N_B = 1200$ fixed and
   $\gamma \in \{0, 0.05, 0.15, 0.4, 1.0\}$, ⓐ disagreement $0.6$ with $N_A=400$ gives
   $\gamma^\star = 0$; ⓑ disagreement $0.08$ with $N_A=60$ gives $\gamma^\star = 0.4$, which is
   **$3.16\times$** better than $\gamma=0$; ⓒ reducing the disagreement from $0.6$ to $0.08$, or
   reducing $N_A$ from $400$ to $60$, **increases** $\gamma^\star$ (the two directions of (4)).
   Judge on 20-seed means.

**Baselines**: ⓐ $\gamma=0$ (target data only) — the reference for whether mixing pays.
ⓑ $\gamma=1$ (plain concatenation) — the practical default. ⓒ the closed forms (1) and (3) — that is
what criteria 1 and 3 compare against. ⓓ optional: sweep $p \in \{10, 20, 40, 80\}$ and confirm the
floor does not move from $\sigma^2$ (if it moves there is misspecification, which is the diagnostic
of P5 (iii)).

**Optional extension (R4, may need a GPU — not required)**: take two or three subsets of Open
X-Embodiment, train the same linear head on a frozen visual representation, and sweep the dataset
weight $\gamma$ to see whether a curve of the same shape as criterion 4 appears. **No acceptance
criterion is set** — differences in public checkpoints and preprocessing may prevent the numbers
from reproducing. The purpose is to check whether the reduced model's conclusion shows up
**qualitatively** in a real mixture.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The ratio in criterion 1 exceeds 2 at small $N$ | $N$ is close to $p+1$, i.e. the double-descent region | print $N/p$ — criterion 1's range has $N/p \ge 3$ |
| The slope in criterion 2 is near $-0.2$ | the regression was run on the raw loss without subtracting the floor | plot $L_A$ and $L_A-\sigma^2$ together |
| The ratio in criterion 3 exceeds $1.5$ | too few samples for estimating $\Sigma_A, \Sigma_B$, so (3) is inaccurate | raise the estimation sample to $4\times10^5$ and watch the ratio change |
| The floor in criterion 3 keeps falling with $N$ | the weights were per-sample rather than per-domain constants (implicit importance weighting) | print the number of unique values in the weight vector — it must be 2 |
| $\gamma^\star$ is always 0 in criterion 4 | the disagreement $d$ is so large that all four combinations sit in the same regime | print $\lVert\Sigma_B\Delta\rVert_{\Sigma_A}$ and confirm the two $d$ values really differ |
| $\gamma^\star$ changes between seeds | too few seeds and too coarse a grid | use 20-seed means and refine the $\gamma$ grid logarithmically |

## Open problems

- **(open problem) Why the exponent is not 1 in deep networks** — the exponent in (1) is exactly
  $1$, whereas measured deep networks give $0.05$–$0.3$. The explanation that the effective degrees
  of freedom grow with $N$ exists, but there is no theory that **predicts** the exponent for a given
  architecture and dataset. In robot data the exponent varies strongly across tasks, which makes
  extrapolation especially dangerous. Current approaches:
  [Kaplan et al. 2020](https://arxiv.org/abs/2001.08361),
  [Hestness et al. 2017](https://arxiv.org/abs/1712.00409),
  [Hoffmann et al. 2022](https://arxiv.org/abs/2203.15556). What is missing: a rule predicting the
  exponent from the architecture.
- **(open problem) A procedure for setting mixture weights from data** — (8) gives $\gamma^\star$
  only if $\Delta$ and $\Sigma_B$ are known. With dozens of domains $\gamma$ is a vector, and when
  target-domain validation data is scarce (common in robotics) its estimate overfits. Current
  approaches: OXE's manual weights ([OXE 2023](https://arxiv.org/abs/2310.08864)),
  compute-optimal allocation ([Hoffmann et al. 2022](https://arxiv.org/abs/2203.15556)). What is
  missing: a weight-selection rule for scarce target data.
- **(open problem) Decomposing the floor** — an empirical floor is the sum of label noise,
  multi-modal demonstrations, misspecification and action-space quantization. With no procedure for
  separating those components, "we have hit the floor" cannot be told apart from "more data is
  useless" versus "the model must change". The multi-modality side connects to the quantization
  error of `s4-vla-architectures` and the measurement side to `s4-evaluation-science`. What is
  missing: an experimental design that identifies the components of the floor.
- **(open problem) Predicting negative transfer in advance** — (3) gives the **condition** under
  which transfer hurts, but there is no way to estimate $\Sigma_B\Delta$ when a dataset is handed to
  you. The weak correlation between simulated evaluation and hardware is the same problem
  (`s4-evaluation-science`, [Li et al. 2024](https://arxiv.org/abs/2405.05941)). What is missing: a
  cheap indicator that detects negative transfer before training.

## Concept check

Run `rc quiz s4-robot-data-scaling`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

The five items cover: what the flattening of a log-log curve at large $N$ is showing; whether more
samples remove the loss a disagreeing mixture creates; when the domain weight $\gamma^\star$
shrinks; the exact condition under which the mixture bias is zero; and whether the measured height
of the floor equals the label noise.

## How to study this stage

1. **Derive (1) from a blank page (60 min)** — separating the excess risk into $\sigma^2$ plus a
   quadratic form in step 1 is the whole thing. Once you can do that separation, it becomes
   automatic that the "floor" and the "slope" are different quantities. Memorize the inverse Wishart
   mean and only check why $N>p+1$ is needed.
2. **Separate floor from slope numerically (45 min)** — solve problem P3, then run criteria 1 and 2
   of the reproduction task and see for yourself that **regressing the raw loss bends the slope**.
   Making that mistake once changes how you read a scaling plot in a paper.
3. **Solve the mixture limit by hand (60 min)** — write the two lines from (5) to (2) from a blank
   page. Confirming for yourself that "there is no $N$ anywhere" is the turning point of this
   lesson. Then use P2 to confirm that the bias vanishes not when $\Delta = 0$ but when
   $\Sigma_B\Delta = 0$.
4. **Run the grid yourself (125 min)** — run criteria 3 and 4 to see the collapse condition and the
   two directions of $\gamma^\star$. In particular, look at the cell with a **3.16× gain** (small
   disagreement, little target data) next to the cell with $\gamma^\star=0$ (large disagreement,
   ample target data). Anyone who has built this table states "more data is better" only
   conditionally.
5. **Read the two papers against the reduced model (110 min)** — explain, within the framework of
   (1), why Kaplan et al.'s exponent is not 1, and compare OXE's weight-setting procedure with (8).
   Write the one-page note for each; this is **not** optional.
6. **End at what cannot be done (80 min)** — pick the open problem of decomposing the floor and
   write a paragraph on how baseline ⓓ (sweeping $p$) could be extended to separate noise from
   misspecification.

**Passing bar**: you can derive (1) and (2) from a blank page, say where the floor and the slope
each come from, compute the collapse condition (7), quote both directions of $\gamma^\star$
numerically, and you hold code satisfying the four acceptance criteria plus notes on the two papers.
