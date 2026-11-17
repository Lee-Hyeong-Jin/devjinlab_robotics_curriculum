---
id: s5-active-information-gathering
lang: en
title: Active perception and information gathering
summary: >-
  Derive that mutual information closes to a $\tfrac12\log\det$ form in the linear-Gaussian model,
  and prove from nothing but the PSD order of covariances that it is monotone submodular when the
  measurements are conditionally independent given the state. After proving the $(1-1/e)$
  guarantee of the greedy algorithm in full, measure numerically that the bound is **36
  percentage points loose on this problem family** and that **submodularity itself breaks when the
  measurement noise is correlated**.
objectives:
  - Derive the mutual information of the linear-Gaussian model as a log-determinant of the information matrix.
  - Prove through the PSD order that mutual information is monotone submodular under conditional independence.
  - Prove the $(1-1/e)$ guarantee of the greedy algorithm and point out which assumption is used where.
  - Distinguish numerically that the bound is over the whole function class and is loose on a specific problem family.
  - Show by counterexample that submodularity breaks when the measurement noise is correlated.
  - Explain, by comparing sequential and simultaneous selection, that one round of communication buys the guarantee.
tags: [multi-robot, active-perception, mutual-information, submodularity, greedy, research]
---

# Active perception and information gathering

## Setup and notation

We use the information matrix $\Lambda = \Sigma^{-1}$ of `c5-factor-graphs-map` and the information
contribution $A^\top R^{-1} A$ of a linearized measurement as they stand. The sequential-decision
view of `c8-mdp-pomdp-bellman` is used in the last point of R1 (in the linear-Gaussian case
open-loop planning is optimal).

| Symbol | Meaning |
|---|---|
| $x \in \mathbb{R}^d$ | The quantity to estimate (map, target, state). Prior $x \sim \mathcal{N}(0, \Sigma_0)$, $\Lambda_0 = \Sigma_0^{-1}$ |
| $\mathcal{V}$ | The set of candidate measurements (sensor locations, times), $\lvert\mathcal{V}\rvert = m$ |
| $y_i = A_i x + n_i$ | The measurement of candidate $i$. $n_i \sim \mathcal{N}(0, R_i)$ |
| $S \subseteq \mathcal{V}$ | The selected set of measurements. The budget is $\lvert S\rvert \le k$ |
| $\Lambda_S$ | The information matrix after receiving $S$: $\Lambda_0 + \sum_{i\in S} A_i^\top R_i^{-1} A_i$, $\Sigma_S = \Lambda_S^{-1}$ |
| $f(S)$ | The objective $= I(x; y_S)$ (mutual information). $f(\emptyset) = 0$ |
| $\Delta_j(S)$ | The marginal gain $f(S \cup \{j\}) - f(S)$ |
| $A \preceq B$ | The PSD order ($B - A \succeq 0$) |

**The problem.** Maximize $f(S)$ subject to $\lvert S\rvert \le k$. Choosing $k$ out of $m$
candidates gives $\binom{m}{k}$ combinations, so exhaustive search is exponential, and the problem
is in fact NP-hard. The subject of this lesson is **why, and how well, the greedy algorithm
does**.

## Key results

The bracket gives the derivation depth (D0 cited / D1 skeleton / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (linear-Gaussian mutual information is a log-determinant) [D2]** —
  $$
  f(S) = I(x; y_S) = \tfrac12 \log\det\Lambda_S - \tfrac12\log\det\Lambda_0
  = \tfrac12 \log\det\!\left(I + \Sigma_0\sum_{i\in S} A_i^\top R_i^{-1}A_i\right). \tag{1}
  $$
  Two things follow. (a) $f$ is the objective of **D-optimal design** (the same object as the
  experiment design of `c4`). (b) (1) **does not depend on the measured value $y$** — in the
  linear-Gaussian case, deciding in advance what to look at yields the same information as
  deciding after actually looking, so **open-loop planning is optimal** (the separation property
  that `atanasov2015-decentralized-active` uses). In the nonlinear or non-Gaussian case this
  breaks and closed loop (a POMDP) is needed.
- **R2 (under conditional independence mutual information is monotone submodular) [D3]** — the
  marginal gain is
  $$
  \Delta_j(S) = \tfrac12\log\det\!\left(I + R_j^{-1}A_j \Sigma_S A_j^\top\right) \tag{2}
  $$
  and $S \subseteq T \Rightarrow \Lambda_S \preceq \Lambda_T \Rightarrow \Sigma_S \succeq \Sigma_T$,
  so by the PSD monotonicity of $\log\det$, $\Delta_j(S) \ge \Delta_j(T) \ge 0$. That is,
  **monotonicity and submodularity both come from the single PSD order of the covariances**. It
  is a three-line proof with no limits involved, and in measurement there were 0 violations in
  4000 trials.
- **R3 (the $(1-1/e)$ guarantee of the greedy algorithm) [D3]** — if $f$ is monotone submodular
  and $f(\emptyset)=0$, the greedy solution $S_k$ satisfies
  $$
  f(S_k) \;\ge\; \left(1 - \left(1-\tfrac1k\right)^{\!k}\right) f(\mathrm{OPT}) \;\ge\; \left(1-\tfrac1e\right) f(\mathrm{OPT}) \tag{3}
  $$
  (Nemhauser–Wolsey–Fisher). The whole proof is "the marginal gains of the elements of
  $\mathrm{OPT}$ sum to cover the remaining gap + greedy picks the largest of them", from which
  the geometric decay of the gap follows.
- **R4 (that bound is 36 points loose on this problem family) [D2]** — (3) is the worst case over
  **the whole class of monotone submodular functions**. Measured in the reproduction task: on 50
  random Gaussian mutual-information instances the mean of greedy/optimal is $0.9941$, the
  minimum $0.9621$, and **60% are exactly optimal** — 36 percentage points above the bound
  $0.6321$. Conversely, on the classical tight family of max coverage the ratio is
  $0.7500, 0.6724, 0.6515, 0.6417$ for $k=2,5,10,20$, **attaining $1-(1-1/k)^k$ to three
  decimals**. Citing (3) as "the expected performance of greedy" is therefore wrong — it is a
  **guarantee**, and the tight family comes from coverage.
- **R5 (correlated noise breaks submodularity) [D2]** — R2 depends on the assumption that the
  measurements are **conditionally independent** given the state. The counterexample of the
  reproduction task: for $x\in\mathbb{R}^2$, let two sensors measure $x_1+x_2$ and $x_1-x_2$ with
  noise correlation coefficient $\rho = 0.99$; then $f(\{1\}) = f(\{2\}) = 1.5726$ but
  $f(\{1,2\}) = 5.1027$. The marginal gain of sensor 2 **increases** from $1.5726$ alone to
  $3.5302$ after sensor 1 (a synergy of $+1.9576$). Submodularity is broken, so the guarantee (3)
  is gone. **If the noise of a sensor network is correlated, the greedy guarantee cannot be
  cited.**
- **R6 (one round of communication buys the guarantee) [D2]** — in the problem where 2 robots
  pick 2 each, **sequential** selection (the later robot sees the earlier robot's choice) is **the
  same algorithm** as central greedy, so (3) applies unchanged and the measured mean is $0.9968$
  (minimum $0.9692$). **Simultaneous** selection (no communication) has both pick the same
  sensors and carries no constant-factor guarantee: measured mean $0.5654$, **minimum $0.4386$,
  below $1/2$**. Submodularity also gives a free speed-up — lazy greedy (CELF) cuts the number of
  evaluations $225.0 \to 98.9$ ($2.28\times$) while returning **the same selection** in 30/30.

## Derivation

### R1 — why mutual information becomes a log-determinant

The differential entropy of a Gaussian $x \sim \mathcal{N}(0,\Sigma_0)$ is
$h(x) = \tfrac12\log\big((2\pi e)^d \det\Sigma_0\big)$. The posterior after receiving the
measurements $y_S$ is also Gaussian, and its covariance is $\Sigma_S = \Lambda_S^{-1}$
**regardless of the measured values** (the heart of the linear-Gaussian case). Hence
$h(x\mid y_S) = \tfrac12\log\big((2\pi e)^d\det\Sigma_S\big)$ and

$$
I(x;y_S) = h(x) - h(x\mid y_S) = \tfrac12\log\frac{\det\Sigma_0}{\det\Sigma_S}
= \tfrac12\log\det(\Lambda_S\Sigma_0), \tag{4}
$$

and inserting $\Lambda_S = \Lambda_0 + \sum_{i\in S}A_i^\top R_i^{-1}A_i$ gives (1). Since
$\log\det(\Lambda_S\Sigma_0) = \log\det\Lambda_S - \log\det\Lambda_0$, the two are the same
expression.

**What the second equality means.** The conditional entropy in $h(x\mid y_S)$ is normally an
expectation over $y$, but in the linear-Gaussian case **the posterior covariance does not depend
on $y$**, so no expectation is needed. (1) can therefore be computed **before** the measurements
are taken, and the following holds:

$$
\max_{\text{policy}} \mathbb{E}\big[I(x;y_{S(\pi)})\big] = \max_{\lvert S\rvert\le k} I(x;y_S)
\quad\Longrightarrow\quad \text{open-loop planning is optimal.} \tag{5}
$$

That is, an adaptive policy that "decides the next measurement after looking" gains nothing. This
is the ground on which `atanasov2015-decentralized-active` can turn active information gathering
into **deterministic optimal control** rather than a POMDP.

**Where the assumptions break**: (5) holds only when (a) the measurement model is linear, (b) the
noise is Gaussian and (c) **which measurements are available does not depend on the state**. If
the variance of a range measurement depends on the range (a state-dependent measurement model), or
occlusion depends on the state, the posterior covariance depends on $y$ and an adaptive policy
really is better. This is why active perception is hard in general.

### R2 — submodularity comes from the PSD order

**The closed form of the marginal gain.** Adding $j$ after receiving $S$ gives
$\Lambda_{S\cup j} = \Lambda_S + A_j^\top R_j^{-1}A_j$, so

$$
\Delta_j(S) = \tfrac12\log\frac{\det\Lambda_{S\cup j}}{\det\Lambda_S}
= \tfrac12\log\det\!\left(I + \Sigma_S A_j^\top R_j^{-1}A_j\right)
= \tfrac12\log\det\!\left(I + R_j^{-1}A_j\Sigma_S A_j^\top\right), \tag{6}
$$

where the last equality is $\det(I+UV) = \det(I+VU)$ (Sylvester). The important point: the right
side of (6) is a determinant of size $\dim y_j$, the measurement dimension, so it is cheap to
compute even when $d$ is large.

**Monotonicity.** Since $\Sigma_S \succeq 0$, $R_j^{-1/2}A_j\Sigma_SA_j^\top R_j^{-1/2} \succeq 0$
and $\det(I + \cdot) \ge 1$, so $\Delta_j(S) \ge 0$. That is, **information does no harm.**

**Submodularity.** Let $S \subseteq T$. Then
$\Lambda_T - \Lambda_S = \sum_{i\in T\setminus S}A_i^\top R_i^{-1}A_i \succeq 0$, so
$\Lambda_S \preceq \Lambda_T$, and by the PSD order reversal of the inverse

$$
\Sigma_S = \Lambda_S^{-1} \;\succeq\; \Lambda_T^{-1} = \Sigma_T
\;\Longrightarrow\; A_j\Sigma_SA_j^\top \succeq A_j\Sigma_TA_j^\top
\;\Longrightarrow\; \Delta_j(S) \ge \Delta_j(T). \tag{7}
$$

The last implication is the fact that $\log\det$ is monotone in the PSD order ($A \succeq B \succ 0
\Rightarrow \det A \ge \det B$). This is the very definition of submodularity. $\square$

**What the three-line proof means.** Submodularity is introduced as the combinatorial property of
"diminishing returns", but here it is exactly the same as the fact from estimation theory that
**the covariance gets smaller in the PSD order as information arrives**. There is thus a single
assumption — that $\Lambda_T - \Lambda_S$ is PSD, that is, **that the information contributions of
the measurements add**. That is the conditional-independence assumption.

**Where the assumptions break**: if the measurement noise is **correlated** across sensors,
$\Lambda_{S}$ is no longer the sum of the $A_i^\top R_i^{-1}A_i$ and
$\Lambda_{S\cup j} - \Lambda_S$ need not be PSD. Then (7) collapses — the counterexample of R5 is
exactly this. Also, if the objective is the **prediction at unobserved locations** treated by
Krause et al. ($I(\text{observed}; \text{unobserved})$), the objective is strictly speaking not
submodular and is only **approximately** submodular under a discretization condition
(`krause2008-submodular` §3). That is what the "near-optimal" in the title of the paper means.

### R3 — the proof of $(1-1/e)$

Let $S_i$ be the set greedy has picked up to step $i$, $\mathrm{OPT}$ an optimal solution
($\lvert\mathrm{OPT}\rvert = k$), and $\delta_i = f(\mathrm{OPT}) - f(S_i)$ the gap.

**Step 1 (covering).** From monotonicity and submodularity,

$$
f(\mathrm{OPT}) \;\le\; f(\mathrm{OPT}\cup S_i)
\;=\; f(S_i) + \sum_{o\in\mathrm{OPT}\setminus S_i}\Delta_o\big(S_i \cup \{\text{the earlier } o\text{'s}\}\big)
\;\le\; f(S_i) + \sum_{o\in\mathrm{OPT}}\Delta_o(S_i). \tag{8}
$$

The first inequality is monotonicity, the middle is a telescoping sum, and the last is
submodularity (the marginal gain on a set that has had elements added to $S_i$ is $\le$ the
marginal gain on $S_i$).

**Step 2 (the greedy choice).** Greedy picks the element with the largest marginal gain, so
$f(S_{i+1}) - f(S_i) \ge \Delta_o(S_i)$ for every $o$. The sum in (8) has $k$ terms, so

$$
\delta_i = f(\mathrm{OPT}) - f(S_i) \;\le\; \sum_{o\in\mathrm{OPT}}\Delta_o(S_i)
\;\le\; k\big(f(S_{i+1}) - f(S_i)\big) = k(\delta_i - \delta_{i+1}). \tag{9}
$$

**Step 3 (geometric decay).** Rearranging (9) gives $\delta_{i+1} \le (1 - 1/k)\delta_i$, and from
$\delta_0 = f(\mathrm{OPT})$

$$
\delta_k \le \left(1-\tfrac1k\right)^{\!k} f(\mathrm{OPT})
\;\Longrightarrow\;
f(S_k) \ge \left(1-\left(1-\tfrac1k\right)^{\!k}\right)f(\mathrm{OPT})
\ge \left(1-\tfrac1e\right)f(\mathrm{OPT}). \tag{10}
$$

The last inequality is $(1-1/k)^k \le e^{-1}$ (for every $k \ge 1$). $\square$

**Which assumption was used where.** Monotonicity was used only in the first inequality of (8),
submodularity only in the last inequality of (8), and $f(\emptyset)=0$ only in
$\delta_0 = f(\mathrm{OPT})$. Removing any one of the three therefore breaks the proof in a
different way (problem P1).

**Where the assumptions break**: (3) is for a **cardinality constraint** ($\lvert S\rvert\le k$).
If the constraint is a cost budget (each measurement has a different cost), greedy loses the
guarantee, and cost-benefit greedy + partial enumeration recovers $(1-1/e)$. If the constraint is
a matroid, plain greedy gives only $1/2$ and $(1-1/e)$ requires continuous greedy. And (10)
assumes the evaluation of $f$ is **exact** — with a mutual information estimated from samples the
estimation error is added to the guarantee.

### R4 — a guarantee and a performance are different things

(3) is the worst case over **all** monotone submodular functions. Two measurements make the
difference visible.

**Gaussian mutual information (this problem family).** With $d=4$, $m=16$ candidates, $k=4$ and 50
random instances, comparing greedy with exhaustive search ($\binom{16}{4} = 1820$ combinations)
gives:

| Metric | Value |
|---|---|
| Mean of greedy/optimal | $0.9941$ |
| Minimum | $0.9621$ |
| Maximum | $1.0000$ |
| Fraction exactly optimal | $0.600$ |
| The bound (3) | $0.6321$ |

**The tight family of max coverage.** In the classical construction (elements laid out in $k$ rows
and $m$ columns, the elements of column $j$ having weight $(1-1/k)^{j-1}$, the covering sets being
each row and each column, budget $k$) greedy necessarily picks columns first and the ratio
**attains** $1-(1-1/k)^k$:

| $k$ | Greedy/optimal (measured) | $1-(1-1/k)^k$ |
|---|---|---|
| 2 | $0.7500$ | $0.7500$ |
| 5 | $0.6724$ | $0.6723$ |
| 10 | $0.6515$ | $0.6513$ |
| 20 | $0.6417$ | $0.6415$ |

(The measured value is slightly larger in the third decimal because, with the finite number of
columns $m = 8k$, the coverage of the optimal solution falls short of the total weight by
$(1-1/k)^{m}$.)

**How to read this.** (3) is **not false, it is loose.** The looseness comes from the bound being
over the whole function class and the tight family coming from coverage. Gaussian mutual
information does not belong to that family — the log-determinant of (6) is far "smoother" than a
coverage function. So in a paper or report (a) writing "greedy is at least 63% of optimal" is
correct, but (b) writing "greedy achieves about 63% of optimal" is wrong. On this problem family
it is 99%. **[D2]**

### R5 — correlated noise breaks submodularity

Put two sensors on $x = (x_1,x_2)^\top \sim \mathcal{N}(0, I)$:
$y_1 = x_1 + x_2 + n_1$, $y_2 = x_1 - x_2 + n_2$, with

$$
\begin{pmatrix} n_1 \\ n_2\end{pmatrix} \sim
\mathcal{N}\!\left(0,\ \sigma^2\begin{pmatrix}1 & \rho \\ \rho & 1\end{pmatrix}\right),
\qquad \sigma = 0.3,\ \rho = 0.99. \tag{11}
$$

When $f(S)$ is computed through (1), **using the two sensors together makes the inverse of $R$
blow up because of $\rho$** — the variance of $n_1 - n_2$ is $2\sigma^2(1-\rho) = 0.0018$, almost
zero, so $y_1 - y_2 = 2x_2 + (n_1-n_2)$ gives $x_2$ almost perfectly. Measured:

| Set | $f$ |
|---|---|
| $\{1\}$ | $1.5726$ |
| $\{2\}$ | $1.5726$ |
| $\{1,2\}$ | $5.1027$ |

So $\Delta_2(\emptyset) = 1.5726$ while $\Delta_2(\{1\}) = 5.1027 - 1.5726 = 3.5302$.
Submodularity requires $\Delta_2(\{1\}) \le \Delta_2(\emptyset)$, so this is a **violation**, and
the synergy is $f(\{1,2\}) - f(\{1\}) - f(\{2\}) = +1.9576$.

**What broke.** The proof of R2 relied on $\Lambda_{S\cup j} = \Lambda_S + A_j^\top R_j^{-1}A_j$.
With correlated noise $\Lambda_{\{1,2\}} \ne \Lambda_{\{1\}} + A_2^\top R_{22}^{-1}A_2$ and the
information contributions do not add. Hence (7) does not hold.

**When this happens in practice.** (a) Common-mode error — sensors that share the same clock, the
same atmospheric delay or the same calibration error (multiple GNSS receivers, multiple cameras
using the same IMU). (b) Illumination and weather correlation between cameras looking at the same
scene. (c) Estimates received over communication that have a common ancestor (the subject of
`s5-comms-constrained-estimation`). In these cases the greedy guarantee cannot be cited, and the
options are to put the correlation in the model and use the full $R$ (then (6) depends on the set
and becomes expensive) or to use a degraded guarantee through a weak-submodularity measure
($\kappa$-submodularity). **[D2]**

**The opposite direction, stated honestly**: correlation breaks the guarantee but **increases the
information** — in the example above $f(\{1,2\}) = 5.1027$ is larger than the value under
independent noise. Correlated noise is therefore not "a bad thing"; it is **something the analysis
of greedy cannot handle**.

### R6 — one round of communication, and lazy evaluation

**Sequential vs simultaneous.** Two robots pick 2 each. There are two ways.

- **Sequential (sequential greedy)**: robot 1 picks 2, sends the result, then robot 2 picks. This
  is **the same algorithm as central greedy** for the cardinality constraint $k=4$, so (3) applies
  unchanged.
- **Simultaneous (no communication)**: each picks its top 2 by stand-alone gain. Both pick **the
  same ones**, so the budget of 4 is effectively 2 and there is no constant-factor guarantee.

Measured (50 random instances, $d=4$, $m=12$, relative to exhaustive search):

| Method | Mean | Minimum |
|---|---|---|
| Sequential greedy / optimal | $0.9968$ | $0.9692$ |
| Simultaneous (no communication) / optimal | $0.5654$ | $0.4386$ |

The point is that the minimum of simultaneous selection is $0.4386$, **below $1/2$** — there is no
constant-factor guarantee at all. The **one round of communication per selection** (or sequential
assignment) used by `atanasov2015-decentralized-active` is precisely the price that buys (3).

**Lazy greedy (CELF).** Submodularity also gives a free speed-up: the $\Delta_j$ computed in an
earlier round is an **upper bound** on the $\Delta_j$ of the current round (this is exactly (7)),
so if the upper bound is below the current best there is no need to recompute. Measured ($d=4$,
$m=40$, $k=6$, 30 instances): the number of evaluations goes $225.0 \to 98.9$ (a $2.28\times$
reduction) and the selection is **identical** in 30/30. The guarantee is the same and only the
computation drops.

**Where the assumptions break**: sequential greedy equals central greedy when the constraint is a
**common cardinality**. If each robot picks from its own candidate set — a **partition matroid** —
sequential greedy guarantees only $1/2$. And the upper bound of lazy greedy relies on
submodularity, so under the correlated noise of R5 it can return a **wrong selection** (problem
P5). **[D2]**

## Proof sketch

### R2' — submodularity of mutual information

**Hypotheses** H1: $x$ and all measurements are jointly Gaussian and the measurement model is
linear. H2: the measurement noise is **independent** across sensors (conditional independence).
H3: $\Lambda_0 \succ 0$.
**Conclusion** C: $f(S) = I(x;y_S)$ is monotone and submodular with $f(\emptyset)=0$.

**Strategy**: reduce the combinatorial property to the PSD order of linear algebra.

1. **Closed form.** From H1 and H3, (4) holds and $f(\emptyset)=0$.
2. **Additivity of information.** From H2, $\Lambda_S = \Lambda_0 + \sum_{i\in S}A_i^\top R_i^{-1}A_i$,
   so $S\subseteq T \Rightarrow \Lambda_T - \Lambda_S \succeq 0$.
3. **Order reversal of the covariance.** $0 \prec \Lambda_S \preceq \Lambda_T \Rightarrow \Sigma_S \succeq \Sigma_T$
   (the PSD order reversal of the matrix inverse).
4. **Monotonicity of the marginal gain.** In (6), $\Delta_j(S) = \tfrac12\log\det(I+R_j^{-1}A_j\Sigma_SA_j^\top)$,
   and step 3 with the PSD monotonicity of $\log\det$ gives $\Delta_j(S)\ge\Delta_j(T)$. Also
   $\Sigma_S\succeq0$ gives $\Delta_j(S)\ge0$.
5. **Conclusion.** Step 4 is the definition of submodularity, and monotonicity. C. $\square$

**If a hypothesis is removed**: without H2, step 2 collapses and submodularity (actually) becomes
false (the counterexample of R5). Without the linearity in H1, (4) does not hold, $f$ must be
computed through a Laplace approximation, and submodularity survives only approximately. Without
H3 ($\Lambda_0$ singular) the initial $\log\det$ is $-\infty$ and $f$ is undefined — there is an
unobservable direction, which must be split off before redefining the problem.

### R3' — the $(1-1/e)$ of greedy

**Hypotheses** H1: $f$ is monotone. H2: $f$ is submodular. H3: $f(\emptyset)=0$. H4: the
constraint is the cardinality $\lvert S\rvert \le k$. H5: the evaluation of $f$ is exact.
**Conclusion** C: $f(S_k) \ge (1-(1-1/k)^k)f(\mathrm{OPT}) \ge (1-1/e)f(\mathrm{OPT})$.

**Strategy**: show that the gap $\delta_i$ shrinks by a factor of at least $1/k$ of itself at
every step.

1. **Covering.** By H1, $f(\mathrm{OPT}) \le f(\mathrm{OPT}\cup S_i)$; by telescoping and H2, (8).
2. **Maximality of greedy.** By the definition of greedy and H5, $\delta_i - \delta_{i+1} \ge \Delta_o(S_i)$ for every $o$.
3. **$k$ terms.** By H4 the sum in (8) has $k$ terms, so (9): $\delta_i \le k(\delta_i-\delta_{i+1})$.
4. **Geometric decay.** $\delta_{i+1}\le(1-1/k)\delta_i$, and by H3 $\delta_0 = f(\mathrm{OPT})$, hence (10).
5. **Conclusion.** $(1-1/k)^k \le e^{-1}$. C. $\square$

**If a hypothesis is removed**: without H1, step 1 breaks (non-monotone submodular maximization
has different guarantees, with a constant of at most $1/2$, and greedy can be arbitrarily bad).
Without H2 the last inequality of step 1 breaks and the guarantee is gone (R5). Replacing H4 by a
matroid makes the "there are $k$ terms" of step 3 meaningless and plain greedy keeps only $1/2$.
Without H5 (sample estimates) step 2 loosens by the error and a $-\epsilon$ term attaches to the
guarantee.

## Problem set

The answer policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★, R3)** Write the five steps of R3' with no line missing, and point out **which
inequality of which step** breaks when each of three hypotheses is removed: (a) monotonicity
(b) submodularity (c) $f(\emptyset)=0$.
*Strategy + key inequality*: (c) is the trap — if $f(\emptyset) = c > 0$ then
$\delta_0 \ne f(\mathrm{OPT})$ and the guarantee changes to the form
$f(S_k) - c \ge (1-1/e)(f(\mathrm{OPT})-c)$. That is, subtracting the constant revives the
guarantee. The expansion is withheld.

**P2 (proof, ★★, R2)** Prove the last equality of (6) ($\det(I+UV)=\det(I+VU)$) and explain in
terms of dimensions why it makes the computation cheap. Then prove (a) the PSD monotonicity of
$\log\det$ and (b) the PSD order reversal of the inverse
($0\prec A\preceq B \Rightarrow A^{-1}\succeq B^{-1}$).
*Strategy*: expand the determinant of the block matrix $\begin{pmatrix}I & -U\\ V& I\end{pmatrix}$
in two directions. For (b), rewrite as $B^{-1/2}AB^{-1/2} \preceq I$ and argue through
eigenvalues. The expansion is withheld.

**P3 (derivation, ★★, R1)** State (5) precisely and prove it. Then design the structure of one
counterexample each for (a) the case in which the availability of a measurement depends on the
state (occlusion) and (b) the case in which the noise variance depends on the state (a range
measurement whose variance is proportional to the range) — they must be cases in which an adaptive
policy is **strictly** better than open loop.
*Answer sketch*: (b) is the easy one — in a setting where the target is at one of two places and
measuring the nearer one has smaller variance, once the first measurement tells you which side it
is on, the second measurement can be sent there. Open loop cannot do that. To show "strictly" the
expected mutual information of the two policies has to be computed directly.

**P4 (numerical, ★, R4, R5, R6)** In the reproduction task find (a) the mean, minimum and
exactly-optimal fraction of greedy/optimal, (b) the number of submodularity violations, (c) the
three values and the synergy of the correlated-noise counterexample, (d) the ratios of the
coverage tight family, (e) the sequential and simultaneous ratios, (f) the evaluation counts of
lazy greedy.
*Answer*: (a) $0.9941 / 0.9621 / 0.600$. (b) 0 in 4000 trials. (c) $1.5726, 1.5726, 5.1027$,
synergy $+1.9576$. (d) $0.7500, 0.6724, 0.6515, 0.6417$. (e) $0.9968$ (minimum $0.9692$) /
$0.5654$ (minimum $0.4386$). (f) $225.0 \to 98.9$, $2.28\times$, selection identical in 30/30.
Tolerance: 2% relative error on the means, three decimals on the coverage ratios.
Check: if the ratio in (a) **exceeds 1**, the exhaustive search is wrong (the greedy solution is
also inside the search space). If (b) is not 0, most likely covariances were added instead of
information matrices.

**P5 (implementation, ★★★, R2, R3, R6)** Implement greedy, lazy greedy and exhaustive search.
*Rubric*: (a) (1) is computed in **information form** (the covariance is not inverted every time)
(b) numerical stability through `slogdet` (c) lazy greedy returns **the same set** as plain
greedy, confirmed in 30/30 (d) show that in the correlated-noise setting of R5 lazy greedy can
give a **different** answer from plain greedy, or explain why in this particular instance it does
not (e) report the number of combinations of the exhaustive search and confirm that it equals
$\binom{m}{k}$.

**P6 (counterexample, ★★, R4, R5)** (a) Show with the two measured tables that "$(1-1/e)$ is the
expected performance of greedy" is false, (b) look for a Gaussian mutual-information instance that
pushes the ratio below $0.9621$, and if you cannot find one **write that you did not** and state
how far you searched. (c) Vary the correlation coefficient $\rho$ from $0$ to $0.999$ and measure
when the synergy becomes positive.
*Property checklist*: (a) passes only if **both** tables are cited — showing only the Gaussian one
can be misread as "the bound is wrong", and the coverage table has to show that the bound is
**tight**. In (b), writing that you did not find one loses no marks. The transition point in (c)
depends on $\sigma$ and $A$ as well as on $\rho$, so varying a single axis falls short.

**P7 (paper, ★★, R2, R6)** Read sections 3-5 of `krause2008-submodular` and sections III-V of
`atanasov2015-decentralized-active` and (a) distinguish in formulas that the objectives of the two
papers are **different** (prediction at unobserved locations vs mutual information with the
state), (b) write which assumption of R2 in this lesson the "near-optimal" of Krause et al.
relates to, (c) check whether the ground on which Atanasov et al. can go open loop is the same as
(5) in this lesson.
*Rubric*: distinguishing (a) passes. (b) is the core — it must point out that in a GP the mutual
information for predicting unobserved locations is not strictly submodular and that under a
discretization condition one gets a guarantee degraded by $\epsilon$. Pointing out the role of the
linear-Gaussian assumption in (c) is excellent.

## Paper reading

**Two must-read papers.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes, and in the third pass concentrate on questions 4,
5, 7 and 8.

1. **Krause, Singh & Guestrin, "Near-optimal sensor placements in Gaussian processes:
   theory, efficient algorithms and empirical studies" (2008, JMLR 9:235-284)** — role: `seminal`.
   <https://jmlr.org/papers/v9/krause08a.html> (sections 3-5)
   Additional questions: (a) how does the authors' objective differ from (1) in this lesson (it
   is the mutual information about what)? (b) what are the conditions (discretization, sensor
   density) behind "near-optimal", and what remains when they fail? (c) how much speed-up do lazy
   evaluation and the locality (local kernel) approximation each give, and how much guarantee do
   they lose?
2. **Atanasov, Le Ny, Daniilidis & Pappas, "Decentralized active information acquisition:
   theory and application to multi-robot SLAM" (2015, ICRA)** — role: `standard`.
   <https://doi.org/10.1109/ICRA.2015.7139863> (§III-V)
   Additional questions: (a) is the ground on which the authors reduce the problem to
   deterministic optimal control the same as (5) in this lesson? (b) **how many rounds of
   communication** does the decentralized guarantee require? (c) is there a point at which,
   because of a matroid constraint, the guarantee drops from $(1-1/e)$ to $1/2$?

**The ten fixed questions**: (1) what problem is solved under what assumptions (2) what exactly
could earlier work not do (3) the key idea in one line of mathematics (4) what is the theoretical
guarantee and **what is not guaranteed** (5) the independent and dependent variables and baselines
of the experiments, and were they tuned fairly (6) do the metrics match the claims, and are
variance and seeds reported (7) what information needed for reproduction is missing (8) if it is
wrong, which assumption to suspect first (9) computational and memory complexity and real-time
capability (10) what would you change to surpass it a year from now.

## Reproduction task

**Tier R2 (algorithm reimplementation).** Compute budget: one laptop CPU core, under 3 minutes in
total, at most 300 MB of memory. Only numpy and the standard library (`heapq`, `itertools`).

**The input data** is produced by the generator below (fixed seed, deterministic). No external
dataset is needed. **What the learner writes is four functions: the mutual-information
evaluation, greedy, lazy greedy and exhaustive search.**

```python
"""Reproduction task of s5-active-information-gathering: generator and MI evaluation."""

import numpy as np

SEED = 20261113


def mi_gain(prior_inf, blocks, subset):
    """f(S) = 0.5 * (logdet(Lambda_0 + sum_i blocks[i]) - logdet(Lambda_0))."""
    inf = prior_inf.copy()
    for i in subset:
        inf = inf + blocks[i]
    s0, ld0 = np.linalg.slogdet(prior_inf)
    s1, ld1 = np.linalg.slogdet(inf)
    assert s0 > 0 and s1 > 0
    return 0.5 * (ld1 - ld0)


def make_instance(d, m, rng, noise=0.5):
    """Prior information matrix I and the information contributions of m candidates,
    each measuring a random direction in one dimension."""
    prior_inf = np.eye(d) * 1.0
    blocks = []
    for _ in range(m):
        a = rng.normal(size=(1, d))
        blocks.append(a.T @ a / noise**2)
    return prior_inf, blocks


def coverage_weights(k, m=None):
    """Tight family of max coverage: elements of column j weigh (1-1/k)^j, k rows and m columns."""
    m = 8 * k if m is None else m
    return np.array([(1 - 1 / k) ** j for j in range(m)])
```

**Conventions (must be followed).** (a) $f$ is computed in **information form** (do not build
covariances and add them). (b) Determinants are computed with `np.linalg.slogdet` (`det`
underflows). (c) Create `np.random.default_rng(SEED)` **afresh** for every setting. (d) In the
coverage family greedy picks a **column** when marginal gains tie (the construction is designed
that way, and the column weight is strictly larger than the row weight by $k(1-1/k)^m$). (e) Lazy
greedy keeps the upper bounds in a heap and commits a popped item only when its recomputed value
is at least the next upper bound in the heap.

**Part A — greedy vs exhaustive search.** $d=4$, $m=16$, $k=4$, 50 instances. Report the mean,
minimum and maximum of greedy/optimal and the fraction exactly optimal. Also report the number of
combinations of the exhaustive search.

**Part B — checking submodularity.** For 200 instances with $d=3$, $m=8$, 20 times each, draw
$A\subset B$ and $i \notin B$ at random and check $\Delta_i(A) - \Delta_i(B) \ge 0$. Report the
number of violations and the minimum.

**Part C — the correlated-noise counterexample.** In the setting of (11) ($\sigma=0.3$,
$\rho=0.99$, $A_1 = [1\ 1]$, $A_2 = [1\ -1]$) report $f(\{1\}), f(\{2\}), f(\{1,2\})$ and the
synergy. Here the full $R$ must be used, so compute
$\Lambda_S = \Lambda_0 + A_S^\top R_{SS}^{-1} A_S$.

**Part D — sequential vs simultaneous.** $d=4$, $m=12$, 2 robots × 2 picks, 50 instances. Report
sequential greedy (= central greedy with $k=4$) and simultaneous selection (each robot picks its
top 2 by stand-alone gain → the same set, so the effective size is 2) as ratios to exhaustive
search ($k=4$).

**Part E — the coverage tight family.** For $k = 2, 5, 10, 20$ compare greedy/optimal with
$1-(1-1/k)^k$.

**Part F — lazy greedy.** $d=4$, $m=40$, $k=6$, 30 instances. Report the **number of
mutual-information evaluations** of plain greedy and lazy greedy and whether the selections agree.

**Acceptance criteria — all six conditions must hold to pass.**

1. **Part A** — mean of greedy/optimal $0.9941$, minimum $0.9621$, maximum $1.0000$, fraction
   exactly optimal $0.600$ (2% relative error on the mean, $\pm0.08$ on the fraction). The number
   of combinations of the exhaustive search is $\binom{16}{4} = 1820$. State explicitly that these
   values are **far above** the bound $0.6321$.
2. **Part B** — **0 violations** in 4000 trials and $\min(\Delta_i(A)-\Delta_i(B)) > 0$ (measured
   $5.129\times10^{-5}$). A single violation means the accumulation of the information matrix is
   wrong.
3. **Part C** — $f(\{1\}) = f(\{2\}) = 1.5726$, $f(\{1,2\}) = 5.1027$ (absolute error $10^{-3}$),
   hence $\Delta_2(\{1\}) = 3.5302 > \Delta_2(\emptyset) = 1.5726$ and the synergy is $+1.9576$.
   **Print the submodularity violation explicitly.**
4. **Part D** — sequential/optimal mean $0.9968$ (minimum $0.9692$), simultaneous/optimal mean
   $0.5654$ (minimum $0.4386$). State explicitly that the **minimum of simultaneous is below
   $1/2$**.
5. **Part E** — the ratios are $0.7500, 0.6724, 0.6515, 0.6417$ for $k=2,5,10,20$ and agree with
   $1-(1-1/k)^k$ to three decimals. The first greedy pick is a **column** in all four cases.
6. **Part F** — plain greedy evaluations $225.0$, lazy evaluations $98.9$ ($2.28\times$),
   selections agree in **30/30**. The evaluation count of plain greedy must be **exactly**
   $\sum_{i=0}^{5}(40-i) = 225$.

**Comparison**: (a) the baseline of Parts A and D is exhaustive search (the optimum). (b) The
baseline of Part E is the analytic value $1-(1-1/k)^k$. (c) The baseline of Part F is the
evaluation count of plain greedy. Optional: sweeping $\rho$ over $0 \to 0.999$ in Part C and
finding where the sign of the synergy changes solves problem P6(c).

**Numbers to report**: every value of the six conditions above, and the distribution (minimum,
median) of the ratio over the 20 instances of Part A in which greedy differs from the optimum.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The ratio in Part A exceeds 1 | The exhaustive search uses a different objective from greedy (or misses combinations) | Check that the number of combinations is $\binom{16}{4}=1820$ and that both use the same `mi_gain` |
| Violations appear in Part B | Covariances were added instead of information matrices | Check that $\Lambda_S = \Lambda_0 + \sum A^\top R^{-1}A$. Covariances do not add |
| The minimum in Part B is exactly 0 | $A = B$ was drawn instead of $A \subset B$ | Check that the two sets differ in size and are nested |
| The synergy in Part C is 0 | The two sensors were added separately, ignoring the off-diagonal of $R$ | Check that $\Lambda_{\{1,2\}}$ is computed with the inverse of the full $2\times2$ $R$ |
| $f$ diverges in Part C | $R$ is close to singular as $\rho \to 1$ | Use $\rho = 0.99$ and compute with `slogdet`. $\rho = 1$ is undefined |
| The ratio in Part E is $1.0$ | Greedy picked a **row** on a tie | Print and compare the column weight $k\cdot w_1 = k$ and the row weight $\sum_j w_j < k$ directly |
| The ratio in Part E is off in the third decimal | The number of columns $m$ is too small and the optimal solution falls short of the total weight | Check that $m \ge 8k$. A fixed $m=60$ is off by 0.4% at $k=20$ |
| The plain-greedy evaluation count in Part F is not 225 | Already selected candidates were evaluated again | Compare with $\sum_{i=0}^{k-1}(m-i)$ |
| The selections differ in Part F | The commit condition of lazy is wrong (committing without comparing against the upper bound) | Check that it commits only when the recomputed gain is at least the next upper bound in the heap |

## Open problems

- **(Open problem) Guarantees under correlated noise** — R5 shows that with correlated sensor
  noise submodularity breaks and (3) disappears. A degraded guarantee is available through weak
  submodularity ($\kappa$-submodularity, the submodularity ratio), but there is **no way to
  compute that constant, or lower-bound it usefully, for the correlation structure of an actual
  sensor network**. Current approach: put the correlation in the model and do the expensive exact
  computation that inverts the full $R$ for each set. What is missing: a lower bound that goes
  from the structure (rank, magnitude) of common-mode noise to the submodularity ratio.
- **(Open problem) A theory that explains the gap between guarantee and performance** — R4 shows
  that on Gaussian mutual information greedy has mean $0.9941$ and minimum $0.9621$ while the
  guarantee is $0.6321$. The **problem-family-specific** analyses that would explain this
  36-point gap (curvature $\kappa$, the smoothness of the log-determinant, concentration in random
  designs) exist only in part. Current approach: the curvature-based guarantee
  $\tfrac1\kappa(1-e^{-\kappa})$. What is missing: a high-probability lower bound on the ratio of
  greedy in random linear-Gaussian designs.
- **(Open problem) The gain from adaptivity under nonlinear, state-dependent measurements** — (5)
  says that open loop is optimal in the linear-Gaussian case, but when **the measurement model
  depends on the state**, as with occlusion or range-dependent noise, an adaptive policy is
  strictly better. No way is known to **bound** the size of that gain in advance from the
  structure of the problem — that is, "is it worth going closed loop on this problem" cannot be
  answered before planning. Current approach: adaptive submodularity recovers $(1-1/e)$ for
  particular structures. What is missing: a problem-structure-dependent upper bound on the
  adaptivity gap.

## Concept check

Take it with `rc quiz s5-active-information-gathering`. This quiz is a **concept check only**; the
real work is the problem set and the reproduction task above (`lesson-standard.md` §4).

## How to study this stage

1. **Derive (1) from a blank page (30 min)** — from the Gaussian entropy up to (4). The most
   important line is "the posterior covariance does not depend on the measured values", which
   leads to the open-loop optimality of (5).
2. **Rewrite submodularity as linear algebra (45 min)** — (6) and (7) from a blank page. They are
   three lines, so do not memorize them; be able to explain **why** those three lines (additivity
   of information → order reversal of the covariance → monotonicity of $\log\det$). The densest 30
   minutes of this lesson.
3. **(8), (9) and (10) of R3 by hand (60 min)** — the proof of $(1-1/e)$. Once you have seen the
   structure in which each of the three hypotheses is used **in exactly one inequality**, it is
   immediately visible what breaks when you switch to a matroid or a cost budget.
4. **Run Parts A and B first (60 min)** — see that greedy is exactly optimal in 60% of instances,
   and confirm in Part B that there are 0 submodularity violations. Getting the code that adds
   information matrices wrong once is good for learning (second row of the diagnosis table).
5. **Break the assumption with Part C (45 min)** — raise $\rho$ from 0 to 0.99 and watch the
   synergy become positive. **The most important experiment** of this lesson: you see directly how
   the assumption of a theorem breaks in practice.
6. **Settle two confusions with Parts D and E (60 min)** — in Part E see that the bound is
   **tight**, and put it next to Part A to fix "guarantee $\ne$ performance". See the value of one
   round of communication with Part D.
7. **Get the free speed-up with Part F (30 min)** — lazy greedy. Once you confirm that the upper
   bound is exactly (7), you know that submodularity is both an analysis tool and an
   implementation tool.
8. **In the papers, tell the objectives apart first (120 min)** — the objective of Krause et al.
   is the mutual information for **prediction at unobserved locations** and differs from (1) in
   this lesson. That difference is the basis of "near-optimal". Atanasov et al. use (5) to avoid a
   POMDP. The one-page note per paper is **mandatory**.
9. **End with what cannot be done (30 min)** — pick one of the three "Open problems" and write a
   paragraph on it. For guarantees under correlated noise, Part C is the direct motivation.

**Pass criterion**: from a blank page you can write (1), (6), (7) and (8), (9), (10); you can
explain with the two measured tables that $(1-1/e)$ is a guarantee and not an expected
performance; you have reproduced the correlated-noise counterexample; you have code that satisfies
all six conditions of the reproduction task; and you have notes on the two papers.
