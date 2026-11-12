---
id: c8-value-based-rl
lang: en
title: Value-based RL and function approximation
summary: >-
  Treat both sides of the question at the level of proof: when linear TD converges and when it
  diverges. On-policy, the projected Bellman operator is a contraction in a weighted norm, which
  yields convergence and an approximation-error bound; in Baird's counterexample the expected
  update matrix has eigenvalues with negative real part and the iteration diverges. The lesson
  ends by computing the overestimation bias of the max operator exactly and explaining why a
  double estimator removes it.
objectives:
  - Prove $\lVert P^\pi v\rVert_D \le \lVert v \rVert_D$ and point out exactly where the on-policy assumption is used.
  - Show that the projected Bellman operator is a $\gamma$-contraction and derive the $1/\sqrt{1-\gamma^2}$ error bound.
  - Construct Baird's counterexample and prove divergence from the spectrum of the expected TD update matrix.
  - Show that the residual-gradient update matrix is symmetric positive semidefinite and explain why it converges.
  - Compute the bias of the maximum of $m$ noisy estimates exactly and explain why a double estimator removes it.
  - Explain which step is restored when one leg of the deadly triad (function approximation, bootstrapping, off-policy) is removed.
tags: [value-based-rl, function-approximation, td-learning, dqn, overestimation, research]
---

# Value-based RL and function approximation

## Setup and notation

The MDP notation and Bellman operators of `c8-mdp-pomdp-bellman` carry over. Additional
**recommended** background:

- Linear algebra: weighted inner products and norms, orthogonal projection, the spectrum of a
  non-symmetric matrix, transient response of a non-normal matrix
  (`r0-linear-algebra-decompositions`).
- Probability: stationary distributions, Jensen's inequality, importance ratios.
- Stochastic approximation from the ODE viewpoint: if the ODE of the expected update is stable,
  the stochastic iteration with a small step size goes to the same place (Robbins–Monro). This
  lesson works only with the **expected** update, so the ODE level is enough.

Added notation:

| Symbol | Meaning |
|---|---|
| $\Phi \in \mathbb{R}^{n\times k}$ | feature matrix, whose row $\phi(s)^\top$ holds the features of state $s$ |
| $v_\theta = \Phi\theta$ | the linear value approximation, $\theta \in \mathbb{R}^k$ |
| $D = \operatorname{diag}(d)$ | state weighting, $\lVert v \rVert_D^2 = \sum_s d(s) v(s)^2$ |
| $\Pi$ | orthogonal projection onto $\operatorname{span}(\Phi)$ in $\lVert\cdot\rVert_D$, $\Pi = \Phi(\Phi^\top D\Phi)^{-1}\Phi^\top D$ |
| $\delta_t$ | TD error, $\delta_t = r_t + \gamma v_\theta(s_{t+1}) - v_\theta(s_t)$ |
| $\varrho_t$ | importance ratio, $\varrho_t = \pi(a_t\mid s_t)/b(a_t\mid s_t)$ ($b$ is the behaviour policy) |
| $A, b$ | expected TD update, $A = \Phi^\top D(I - \gamma P^\pi)\Phi$, $b = \Phi^\top D r^\pi$ |
| $\mathrm{MSBE}$ | mean squared Bellman error, $\lVert T^\pi v_\theta - v_\theta \rVert_D^2$ |

The expected update in one line. Linear TD(0) with step size $\alpha$ is

$$
\theta_{k+1} = \theta_k + \alpha\,(b - A\,\theta_k), \tag{1}
$$

so the error in $\theta$ propagates through the linear map $(I - \alpha A)$. **Every convergence
and divergence verdict in this lesson is a statement about the spectrum of $A$.**

## Key results

The bracket gives the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (on-policy convergence and the projected Bellman error bound) [D2]** — if $d$ is the
  stationary distribution of $P^\pi$ then $\lVert P^\pi v \rVert_D \le \lVert v\rVert_D$, and
  therefore $\Pi T^\pi$ is a $\gamma$-contraction in $\lVert\cdot\rVert_D$. A unique fixed point
  $v_{\mathrm{TD}} = \Phi\theta_{\mathrm{TD}}$ exists and
  $$
  \lVert v_{\mathrm{TD}} - V^\pi \rVert_D \;\le\; \frac{1}{\sqrt{1-\gamma^2}}\,
    \lVert \Pi V^\pi - V^\pi \rVert_D . \tag{2}
  $$
  At the same time the symmetric part of $A$ is positive definite, so (1) converges for a small
  enough $\alpha$.
- **R2 (divergence of off-policy linear TD: Baird's counterexample) [D3]** — for a concrete MDP
  with 7 states and 8 features and the weighting $d$ below, $A$ has eigenvalues with **negative
  real part**:
  $$
  \min_i \operatorname{Re}\lambda_i(A) = -0.2392504642\ldots < 0, \tag{3}
  $$
  so (1) diverges for every $\alpha > 0$ and $\lVert\theta_k\rVert$ grows asymptotically by a
  factor $(1 + \alpha\,\lvert\lambda_{\min}\rvert)$ per step. This happens even though all rewards
  are zero and the true value is $V^\pi \equiv 0$ — **the divergence is a deterministic fact, not
  noise.**
- **R3 (convergence of the residual gradient) [D2]** — descending the MSBE directly makes the
  update matrix $B = \Phi^\top_\Delta D_\varrho \Phi_\Delta$ (rows of $\Phi_\Delta$ being
  $\phi(s) - \gamma\,\mathbb{E}[\phi(s')]$) **symmetric positive semidefinite**, so the MSBE is
  monotonically non-increasing. The price is that (i) the limit is not the projected Bellman fixed
  point and (ii) stochastic transitions require **double sampling**.
- **R4 (overestimation bias of the maximum and the double estimator) [D2]** — if all true values
  $Q(s,a)$ are equal and the estimates carry independent noise $\eta_a$, Jensen gives
  $\mathbb{E}[\max_a \hat{Q}] \ge \max_a \mathbb{E}[\hat{Q}]$, and for
  $\eta_a \sim \mathrm{Unif}(-\epsilon,\epsilon)$ the bias is **exactly**
  $$
  \mathbb{E}\big[\max_{a \in \mathcal{A}} \eta_a\big] = \epsilon\,\frac{m-1}{m+1},
    \qquad m = \lvert\mathcal{A}\rvert . \tag{4}
  $$
  Separating **selection from evaluation** with two independent estimates $\hat{Q}_A, \hat{Q}_B$
  gives $\mathbb{E}\big[\hat{Q}_B(\arg\max_a \hat{Q}_A(a))\big] = 0$, removing the positive bias
  (at the cost of a downward one).
- **R5 (the deadly triad) [D1]** — divergence needs **all three** of ⓐ function approximation,
  ⓑ bootstrapping and ⓒ an off-policy distribution. Removing ⓐ from Baird's counterexample (one-hot
  features) makes $\min_i\operatorname{Re}\lambda_i(A) = (1-\gamma)/7 > 0$ and it converges;
  removing ⓒ puts us under R1. Removing ⓑ (Monte Carlo) makes the target independent of $\theta$
  and turns the problem into supervised learning.

## Derivation

### R1 — contraction in a weighted norm

**Step 1: $P^\pi$ is non-expansive in $\lVert\cdot\rVert_D$.** Assume $d$ is the **stationary
distribution** of $P^\pi$ ($d^\top P^\pi = d^\top$). By Jensen's inequality (squaring is convex),

$$
\lVert P^\pi v\rVert_D^2 = \sum_s d(s)\Big(\sum_{s'} P^\pi_{ss'} v(s')\Big)^2
  \;\le\; \sum_s d(s) \sum_{s'} P^\pi_{ss'}\, v(s')^2
  = \sum_{s'} \Big(\underbrace{\sum_s d(s) P^\pi_{ss'}}_{= \,d(s')}\Big) v(s')^2
  = \lVert v \rVert_D^2 . \tag{5}
$$

**The on-policy assumption enters at exactly one place: the underlined equality.** If $d$ is not
stationary for $P^\pi$, that equality is neither $\le$ nor $\ge$, and all of (5) collapses. That is
the seed of R2.

**Step 2: $T^\pi$ is a $\gamma$-contraction.** Since $T^\pi u - T^\pi v = \gamma P^\pi(u-v)$, (5)
gives $\lVert T^\pi u - T^\pi v\rVert_D \le \gamma\lVert u - v\rVert_D$.

**Step 3: $\Pi$ is non-expansive.** $\Pi$ is the orthogonal projection for $\lVert\cdot\rVert_D$,
so $\lVert \Pi x \rVert_D \le \lVert x \rVert_D$. Hence $\Pi T^\pi$ is a $\gamma$-contraction and
Banach gives a unique fixed point $v_{\mathrm{TD}}$. Written in $\theta$, the fixed point satisfies
$\Phi\theta = \Pi T^\pi \Phi\theta$, which unfolds to $A\theta = b$.

**Step 4: the error bound (2).** Split $v_{\mathrm{TD}} - V^\pi$ into its projected and orthogonal
parts. Since $v_{\mathrm{TD}} - \Pi V^\pi \in \operatorname{span}(\Phi)$ and $\Pi V^\pi - V^\pi$ is
orthogonal to it, Pythagoras holds:

$$
\lVert v_{\mathrm{TD}} - V^\pi\rVert_D^2
  = \lVert v_{\mathrm{TD}} - \Pi V^\pi\rVert_D^2 + \lVert \Pi V^\pi - V^\pi\rVert_D^2 .
$$

The first term, using $v_{\mathrm{TD}} = \Pi T^\pi v_{\mathrm{TD}}$ and
$\Pi V^\pi = \Pi T^\pi V^\pi$, obeys

$$
\lVert v_{\mathrm{TD}} - \Pi V^\pi\rVert_D = \lVert \Pi T^\pi v_{\mathrm{TD}} - \Pi T^\pi V^\pi \rVert_D
  \le \gamma \lVert v_{\mathrm{TD}} - V^\pi \rVert_D .
$$

Combining, $\lVert v_{\mathrm{TD}} - V^\pi\rVert_D^2 \le \gamma^2\lVert v_{\mathrm{TD}} - V^\pi\rVert_D^2
+ \lVert \Pi V^\pi - V^\pi\rVert_D^2$, which rearranges to (2).

**How to read it**: (2) says the TD solution is at most $1/\sqrt{1-\gamma^2}$ times worse than the
best achievable approximation $\Pi V^\pi$. At $\gamma = 0.99$ that factor is $7.09$, and at
$\gamma = 0.999$ it is $22.4$ — as the discount approaches one, **the guarantee itself loosens**.

**Where the assumptions break.** Without the stationarity in (5), steps 2–4 are all void. And (2)
is a statement about an **existing** fixed point; if $A$ is singular there may be none, or no
unique one. If the features are linearly dependent, $\Phi^\top D\Phi$ is singular and $\Pi$ itself
is undefined.

### R2 — Baird's counterexample

**The construction.** States $1,\dots,7$ and two actions.

- `solid`: from any state, go to state $7$.
- `dashed`: go to one of states $1,\dots,6$ uniformly.

All rewards are $0$ and $\gamma = 0.99$. The target policy is $\pi(\texttt{solid}\mid s) = 1$ and
the behaviour policy is $b(\texttt{solid}\mid s) = 1/7$, $b(\texttt{dashed}\mid s) = 6/7$, so
$\varrho = \pi/b = 7$ (solid) or $0$ (dashed). The weighting matches the behaviour policy's visits,
$d(s) = 1/7$ (uniform). The features, for $\theta \in \mathbb{R}^8$, are

$$
v_\theta(s_i) = 2\theta_i + \theta_8 \;(i=1,\dots,6), \qquad v_\theta(s_7) = \theta_7 + 2\theta_8, \tag{6}
$$

i.e. $\phi(s_i) = 2e_i + e_8$ and $\phi(s_7) = e_7 + 2e_8$. **That $\theta_8$ is shared across all
states** is the role of function approximation here. The true value is $V^\pi \equiv 0$ and is
represented exactly by $\theta = 0$ — so limited expressiveness is not the cause.

**The expected update.** Since $r \equiv 0$ we have $b = 0$, and the expected update of
importance-weighted off-policy TD(0) is

$$
A = \sum_{s} d(s)\, b(\texttt{solid}\mid s)\, \varrho \; \phi(s)\big(\phi(s) - \gamma\,\phi(s_7)\big)^\top
  = \frac{1}{7}\sum_{s=1}^{7} \phi(s)\big(\phi(s) - \gamma\phi(s_7)\big)^\top , \tag{7}
$$

since $d(s)\,b(\texttt{solid}\mid s)\,\varrho = \tfrac17\cdot\tfrac17\cdot 7 = \tfrac17$. Because
$\theta_{k+1} = (I - \alpha A)\theta_k$, convergence hinges on **whether every eigenvalue of $A$
has positive real part**. Diagonalizing (7) numerically,

$$
\operatorname{spec}(A) = \{\,-0.2392504642,\; -0.0221781072,\; 0,\;
  \underbrace{0.5714285714,\dots}_{5\text{ of them}}\,\}, \tag{8}
$$

two of which have negative real part. The component along a $\lambda < 0$ direction grows by
$(1 - \alpha\lambda) > 1$ per step, so $\lVert\theta_k\rVert \to \infty$, and the asymptotic rate is
set by the most negative eigenvalue:

$$
\frac{\lVert\theta_{k+1}\rVert}{\lVert\theta_k\rVert} \;\longrightarrow\; 1 + \alpha\,\lvert\lambda_{\min}\rvert
  = 1 + 0.2392504642\,\alpha . \tag{9}
$$

With $\alpha = 0.01$ and $\theta_0 = (1,1,1,1,1,1,10,1)$, $\lVert\theta_{20000}\rVert \approx
2.6\times10^{22}$ and the ratio in (9) matches $1.002393$ to six decimals for $k \ge 5000$.

**Why a negative eigenvalue appears (one paragraph).** Each term of (7) is an **asymmetric** outer
product of $\phi(s)$ with $\phi(s) - \gamma\phi(s_7)$. On-policy, the stationarity in (5) makes
$\sum_s d(s)\phi(s)\phi(s)^\top$ dominant and the symmetric part positive definite; here $d$ is
uniform while every transition of the target policy goes to state $7$, so the direction
$\phi(s_7)$ is over-represented. Raising the value of state $7$ through the shared component
$\theta_8$ raises the value of every state, which raises the target again — a **self-reinforcing
loop**. The loop closes only when all three elements (a shared feature, a bootstrapped target, a
mismatched distribution) are present at once.

**Where the assumptions break = cutting the triad.** Replacing the features with one-hot ones
($\Phi = I$, tabular) turns (7) into $A = \tfrac17\big(I - \gamma\,\mathbf{1}e_7^\top\big)$ whose
eigenvalues $\{(1-\gamma)/7,\ 1/7\ (\times6)\}$ are **all positive**. In practice, at
$\alpha=0.01$, $\lVert\theta_k\rVert$ first **rises transiently** to $21.3$ around $k\approx10^3$
and then decreases, reaching $1.0\times10^{-11}$ at $k=2\times10^6$. That transient rise is because
$A$ is **non-normal**, and it is a good example of why "all eigenvalues positive $\Rightarrow$ the
norm decreases monotonically" is **false**.

### R3 — the residual gradient

Writing the MSBE directly makes the objective a quadratic in $\theta$. With the deterministic
transitions of Baird's setting, $\delta(s) = \gamma v_\theta(s_7) - v_\theta(s)$ and

$$
J_{\mathrm{MSBE}}(\theta) = \sum_s w(s)\,\big(\phi_\Delta(s)^\top\theta\big)^2,
  \qquad \phi_\Delta(s) := \phi(s) - \gamma\,\phi(s_7), \tag{10}
$$

with $w(s) = d(s)b(\texttt{solid}\mid s)\varrho$. The gradient-descent update is
$\theta \leftarrow \theta - \alpha\, B\theta$ with
$B = \sum_s w(s)\,\phi_\Delta(s)\phi_\Delta(s)^\top$. $B$ is **symmetric positive semidefinite** (a
non-negatively weighted sum of outer products), so all eigenvalues are $\ge 0$ and
$J_{\mathrm{MSBE}}$ is monotonically non-increasing for $\alpha < 2/\lambda_{\max}(B)$.
Numerically $\operatorname{spec}(B) = \{0,\ 2.4\times10^{-5},\ 0.571\ (\times5),\ 2.235\}$, and
that $2.4\times10^{-5}$ makes **convergence slow** — at $\alpha=0.05$ and $2\times10^5$ iterations
the MSBE is $3.4\times10^{-5}$. Still, $\max_s\lvert v_\theta(s)\rvert \le 2$ stays **bounded**
(TD under the same conditions exceeds $10^{10}$).

**Two prices to pay.**
1. **A different fixed point**: the solutions of $B\theta = 0$ are not the projected Bellman fixed
   point. In general the MSBE minimizer differs from the best approximation in
   $\lVert \cdot \rVert_D$ as well, and with stochastic transitions it **counts noise as a penalty**
   and moves to an over-smoothed solution.
2. **Double sampling**: with stochastic transitions
   $\nabla_\theta \mathbb{E}[\delta]^2 \ne \mathbb{E}[\nabla_\theta \delta^2]$, so two
   **independent successor-state samples** from the same $(s,a)$ are required. On a real robot,
   which cannot be rewound, that is hard to satisfy — which is why practice uses a target network
   to break the self-reinforcing loop of bootstrapping instead of the residual gradient.

### R4 — overestimation and the double estimator

Let the true values of $m$ actions all be $0$ with estimates $\hat{Q}(a) = \eta_a$ ($\eta_a$ i.i.d.
with $\mathbb{E}[\eta_a]=0$). Since $\max$ is convex, Jensen gives

$$
\mathbb{E}\big[\max_a \hat{Q}(a)\big] \;\ge\; \max_a \mathbb{E}\big[\hat{Q}(a)\big] = 0, \tag{11}
$$

so **estimating a maximum is systematically biased upward**. Equality holds only for constant
$\eta$. For $\eta_a \sim \mathrm{Unif}(-\epsilon,\epsilon)$, the maximum of
$U_a = (\eta_a+\epsilon)/2\epsilon \sim \mathrm{Unif}(0,1)$ has mean $m/(m+1)$, so

$$
\mathbb{E}[\max_a \eta_a] = -\epsilon + 2\epsilon\cdot\frac{m}{m+1} = \epsilon\,\frac{m-1}{m+1},
$$

which is (4). For $\eta_a \sim \mathcal{N}(0,\sigma^2)$ with $m=2$,
$\mathbb{E}[\max] = \sigma/\sqrt{\pi}$. This bias accumulates at every bootstrap through $\gamma$,
so the longer the horizon the more $Q$ is systematically inflated and **the policy tilts toward
over-valued actions**.

**The double estimator.** Keep two independent estimates $\hat{Q}_A, \hat{Q}_B$ and use
$a^\star = \arg\max_a \hat{Q}_A(a)$ only for **selection** and $\hat{Q}_B(a^\star)$ only for
**evaluation**. Since $a^\star$ is a function of $\hat{Q}_A$ and independent of $\hat{Q}_B$,

$$
\mathbb{E}\big[\hat{Q}_B(a^\star)\big]
  = \sum_a \Pr(a^\star = a)\,\mathbb{E}\big[\hat{Q}_B(a)\big] = 0 . \tag{12}
$$

The positive bias is gone. But (12) does **not** mean the maximum is estimated without bias — when
the true values differ, $\mathbb{E}[\hat{Q}_B(a^\star)] \le \max_a \mathbb{E}[\hat{Q}(a)]$, a
downward bias (problem P7). Double Q is a device that **flips the sign** of the bias.

**Where the assumptions break.** (12) uses $\hat{Q}_A \perp \hat{Q}_B$. Double DQN selects with the
online network and evaluates with the target network, but the target network is a **delayed copy**
of the online one and so is not independent — the bias shrinks without reaching zero. (11) also
assumes the noise is independent across actions. A neural network shares features across actions,
so the noise is correlated, and with perfect correlation the overestimation disappears (at the cost
of being unable to rank actions at all).

## Proof sketch

### R2 — divergence in Baird's counterexample [D3]

**Hypotheses** H1: the features of (6) and the transitions, policies and weighting above.
H2: $\gamma = 0.99$. H3: we use the expected update (1) (the noise of stochastic samples is not the
point).
**Conclusion** C: $\lVert\theta_k\rVert \to \infty$ for every $\alpha > 0$, at the rate (9).

**Strategy**: spectral test for a linear iteration. Show $\rho(I - \alpha A) > 1$ in
$\theta_{k+1} = (I-\alpha A)\theta_k$.

1. Write $A$ explicitly via (7). Uses: H1 (especially that $\varrho$ is nonzero only for solid).
2. Diagonalize $A$ to obtain (8). The crux is the **single numerical fact** that
   $\lambda_{\min} < 0$; by hand, isolate the $2\times2$ subspace spanned by the shared component
   $\theta_8$ and $\theta_7$ (omitted: the remaining five dimensions separate out — Baird 1995 §3).
3. If $\lambda < 0$ then $\lvert 1 - \alpha\lambda\rvert = 1 + \alpha\lvert\lambda\rvert > 1$, so
   that eigendirection grows geometrically → C. Uses: H3.
4. The rate is set by the dominant eigenvalue → (9).

**Delete one hypothesis**: removing the shared feature $\theta_8$ from H1 ($\Phi = I$) makes the
eigenvalues of $A$ equal $\{(1-\gamma)/7,\ 1/7\}$, all positive, and C false. Changing the
weighting $d$ to the stationary distribution of the target policy puts us under R1 and again makes
C false. So this theorem is a statement **about the conjunction of three conditions**; change any
one and it fails.

### R1 — the projected Bellman error bound [D2, stated as a proof]

**Hypotheses** H1: $d^\top P^\pi = d^\top$ with $d > 0$. H2: $\Phi$ has full column rank.
H3: $\gamma<1$.
**Conclusion** C: $\Pi T^\pi$ is a $\gamma$-contraction, the fixed point is unique, and (2) holds.

**Strategy**: contraction in a weighted norm + non-expansiveness of orthogonal projection +
Pythagoras.

1. (5) by Jensen and H1. Uses: convexity of squaring, stationarity.
2. $\gamma$-contraction of $T^\pi$ (the difference is $\gamma P^\pi(u-v)$).
3. $\Pi$ non-expansive → $\Pi T^\pi$ a $\gamma$-contraction → Banach. Uses: H2 (so $\Pi$ is
   well defined).
4. Pythagoras plus step 2 → (2) → C.

**Delete one hypothesis**: dropping H1 breaks step 1, and R2 supplies the counterexample. Dropping
H2 leaves $\Pi$ undefined and step 3 meaningless. Pushing H3 toward $\gamma\to1$ sends the
contraction factor to 1 and the coefficient $1/\sqrt{1-\gamma^2}$ of (2) to infinity — the
guarantee formally survives but **becomes useless**.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Write (5) with no missing steps, then show numerically how the
underlined equality fails for Baird's $d$ (uniform) and the target policy's $P^\pi$.
*Solution sketch*: Jensen holds regardless of $d$; the only thing that breaks is
$\sum_s d(s)P^\pi_{ss'} = d(s')$. In Baird's example $P^\pi$ sends all mass to $s_7$, so the left
side is $1$ at $s'=7$ and $0$ elsewhere while $d(s') = 1/7$. Build an instance with a vector such
as $v = e_7$ for which $\lVert P^\pi v\rVert_D / \lVert v\rVert_D$ exceeds $1$.

**P2 (proof, ★★★, R1)** Prove (2) and construct a case that approaches equality. Then compute the
factor $1/\sqrt{1-\gamma^2}$ for $\gamma \in \{0.9, 0.99, 0.999\}$ and state how loose the
guarantee becomes.
*Strategy and key inequality*: Pythagorean decomposition plus
$\lVert \Pi T v_{\mathrm{TD}} - \Pi T V^\pi\rVert_D \le \gamma\lVert v_{\mathrm{TD}} - V^\pi\rVert_D$.
The factors are $2.29$, $7.09$ and $22.4$. For near-equality take $\Phi$ one-dimensional and align
the residual of $V^\pi$ with the "slowest" direction of $P^\pi$. The expansion is withheld.

**P3 (numerical, ★, R4)** Derive (4) and compute the bias for $m = 2, 10, 100$ with $\epsilon = 1$.
Also write the bias in closed form for $\eta_a\sim\mathcal{N}(0,1)$ with $m=2$.
*Answer*: $1/3 = 0.333333\ldots$, $9/11 = 0.818181\ldots$, $99/101 = 0.980198\ldots$ (tolerance
$10^{-9}$). The Gaussian case with $m=2$ is $1/\sqrt{\pi} = 0.5641895835\ldots$.
Check: a Monte Carlo run with $2\times10^6$ samples reproduces each value within a standard error
of about $4\times10^{-4}$. The double estimator's mean should agree with $0$ within $3\sigma$ on
the same samples.

**P4 (implementation, ★★, R2·R3)** Implement the expected update (7) and the residual-gradient
update (10) of Baird's counterexample and report the spectrum of $A$, the spectrum of $B$ and the
$\lVert\theta_k\rVert$ trajectories of both iterations.
*Rubric*: ⓐ $\min\operatorname{Re}\lambda(A)$ agrees with (3) to $10^{-6}$; ⓑ the smallest
eigenvalue of $B$ is $\ge -10^{-12}$ (symmetric PSD); ⓒ the asymptotic growth rate (9) is
reproduced to $10^{-5}$ for $k\ge5000$; ⓓ the MSBE is numerically confirmed to be monotonically
non-increasing; ⓔ the importance ratio $\varrho$ is computed as $\pi/b$ rather than hard-coded
as the constant 7.

**P5 (counterexample, ★★, R2·R5)** Make Baird's counterexample converge in **three different
ways**: (i) remove function approximation, (ii) remove off-policy, (iii) remove bootstrapping. For
each, state how $A$ in (7) changes and what happens to its eigenvalues. Then explain why
$\lVert\theta_k\rVert$ **rises transiently** in case (i).
*Property checklist*: (i) $\Phi = I$ → $A = \tfrac17(I - \gamma\mathbf{1}e_7^\top)$, eigenvalues
$\{(1-\gamma)/7,\ 1/7\times6\}$, all positive. (ii) $d$ becomes the stationary distribution of
$\pi$ → R1 applies and the symmetric part is positive semidefinite. (iii) a Monte Carlo target →
$A = \Phi^\top D\Phi$, symmetric positive definite. The transient rise is because $A$ is
non-normal, so $\lVert(I-\alpha A)^k\rVert$ exceeds 1 early on (eigenvalues alone do not reveal
transient response).

**P6 (paper, ★★, R2·R4·R5)** Read DQN (Methods) and Double DQN (§3–4) and write, in at most three
sentences each: (i) which leg of the triad experience replay and the target network weaken, and
how; (ii) why Double DQN's target network reduces the bias even though it violates the independence
assumption of (12); (iii) three pieces of information missing for reproduction in the two papers'
experiments.
*Grading rubric*: (i) passes if it distinguishes that replay makes things **more** off-policy while
breaking sample correlation, and that the target network delays the self-reinforcing bootstrap
loop. (ii) a delayed copy is not fully independent but **lowers the noise correlation** between
selection and evaluation. (iii) three of: preprocessing, seeds, the evaluation protocol (no-op
starts, episode boundaries), the hyperparameter search range. Writing only "performance improved"
fails.

**P7 (derivation, ★★, R4)** Show that (12) is not an "unbiased estimate of the maximum": prove that
when the true values $q_a$ differ, $\mathbb{E}[\hat{Q}_B(a^\star)] \le \max_a q_a$, and state the
equality condition. Sketch the bias as a function of $\Delta/\sigma$ for $m=2$, $q = (0, \Delta)$
and $\eta \sim \mathcal{N}(0,\sigma^2)$.
*Solution sketch*: $\mathbb{E}[\hat{Q}_B(a^\star)] = \sum_a \Pr(a^\star=a)\,q_a \le \max_a q_a$ — a
probability-weighted average cannot exceed the maximum. Equality holds only when
$\Pr(a^\star = \arg\max q) = 1$. As $\Delta/\sigma \to 0$ the bias tends to $-\Delta/2$, and as
$\Delta/\sigma \to \infty$ it tends to $0$.

## Paper reading

**Four must-reads.** Write a one-page note on each using the ten fixed questions
(`lesson-standard.md` §5). Read with three passes and attack questions 4, 5, 6 and 7 in the third.

1. **Baird, "Residual algorithms: reinforcement learning with function approximation" (1995, ICML)**
   — role: `seminal`. <https://doi.org/10.1016/B978-1-55860-377-6.50013-X>
   Why read it: both the counterexample of R2 and the residual gradient of R3 are this paper. Read
   §2–3 only.
   Extra questions: ⓐ what is the difference between the author's residual **gradient** and
   residual **algorithm** (a mixture of the two updates), and what does the mixing coefficient
   trade? ⓑ how does the author handle the double-sampling requirement, and why is that hard on a
   robot?
2. **Tsitsiklis & Van Roy, "An analysis of temporal-difference learning with function
   approximation" (1997, IEEE T-AC)** — role: `seminal`. <https://doi.org/10.1109/9.580874>
   Why read it: (5) and (2) of R1 are theorems of this paper. Read §3–5.
   Extra questions: ⓐ which of the authors' assumptions corresponds to "on-policy", and in exactly
   which condition is it used? ⓑ how does the factor in (2) change for $\lambda > 0$
   ($\mathrm{TD}(\lambda)$)?
3. **Mnih et al., "Human-level control through deep reinforcement learning" (2015, Nature)** —
   role: `standard`. <https://doi.org/10.1038/nature14236> (focus on the Methods section)
   Why read it: a case of stabilizing the triad **by engineering** rather than removing it. There
   is no guarantee, but what worked matters.
   Extra questions: ⓐ what do the limits $C \to 0$ and $C \to \infty$ of the target-network update
   period correspond to? ⓑ which term of (2) does reward clipping affect?
4. **van Hasselt, Guez & Silver, "Deep reinforcement learning with double Q-learning" (2016, AAAI)**
   — role: `standard`. <https://arxiv.org/abs/1509.06461> (§3–4)
   Why read it: this is where (4) and (12) of R4 are **measured** at real scale.
   Extra questions: ⓐ is the authors' way of measuring overestimation fair (what stands in for the
   true value)? ⓑ if a game shows reduced bias but essentially unchanged performance, what does
   that mean?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation? (4) what is guaranteed and **what is not**?
(5) independent and dependent variables, and the baselines — were they tuned fairly? (6) does the
metric match the claim, and are variance and seeds reported? (7) what information needed for
reproduction is missing? (8) if the result were wrong, which assumption would you doubt first?
(9) compute and memory cost, and real-time feasibility? (10) what would you change to go beyond
this paper in a year?

## Reproduction task

**Tier R1 (numerical check).** Compute budget: under **ten seconds** on a laptop CPU (measured
about 3 s), under 100 MB, numpy only. No data is needed — the counterexample is one $7\times8$
matrix.

Construct Baird's counterexample and show that ⓐ importance-weighted TD diverges, ⓑ the residual
gradient converges, and ⓒ removing one leg of the triad makes TD converge too. Use the
construction of R2 for the features, transitions, policies and weighting, with
$\theta_0 = (1,1,1,1,1,1,10,1)$, $\alpha = 0.01$ (TD) and $\alpha = 0.05$ (residual gradient).

**Acceptance criteria** — all four must hold.

1. **Spectrum**: for $A$ in (7),
   $\lvert \min_i \operatorname{Re}\lambda_i(A) - (-0.2392504642)\rvert < 10^{-6}$, and $B$ in (10)
   is symmetric ($\lVert B - B^\top\rVert_\infty < 10^{-12}$) with $\lambda_{\min}(B) \ge -10^{-12}$.
2. **Divergence of TD**: at $\alpha=0.01$ and $k \le 20000$, $\lVert\theta_k\rVert$ is
   **monotonically increasing**, $\lVert\theta_{20000}\rVert > 10^{20}$, and for $k\ge5000$,
   $\big\lvert \lVert\theta_{k+1}\rVert/\lVert\theta_k\rVert - (1+0.2392504642\,\alpha)\big\rvert < 10^{-5}$.
3. **Convergence of the residual gradient**: at $\alpha=0.05$ and $2\times10^5$ iterations the MSBE
   is **monotonically non-increasing** (with $10^{-18}$ numerical slack) and
   $\mathrm{MSBE} < 10^{-4}$, while $\max_s\lvert v_\theta(s)\rvert \le 2$ throughout. At the same
   $k$, TD has $\max_s\lvert v_\theta(s)\rvert > 10^{10}$.
4. **Cutting the triad**: for $A_{\text{tab}}$ with one-hot features,
   $\lvert \min_i\operatorname{Re}\lambda_i(A_{\text{tab}}) - (1-\gamma)/7\rvert < 10^{-9}$, and
   $2\times10^6$ iterations at $\alpha=0.01$ give $\lVert\theta_k\rVert < 10^{-9}$. Confirm at the
   same time that the trajectory is **not monotone** ($\lVert\theta\rVert > \lVert\theta_0\rVert$
   around $k\approx10^3$).

**Baselines**: ⓐ tabular (one-hot) TD — criterion 4 plays that role. ⓑ the projected Bellman
solution in closed form: under on-policy weighting, solving $A\theta = b$ directly must agree with
the iterative solution to $10^{-9}$. ⓒ optional: run $\mathrm{TD}(\lambda)$ with $\lambda = 0.9$ and
check that the divergence is mitigated (not removed).

**Reference output** (numpy 2.x): $\operatorname{spec}(A)$ is (8),
$\operatorname{spec}(B) = \{0,\ 2.4\times10^{-5},\ 0.5714\ (\times5),\ 2.2348\}$, TD gives
$\lVert\theta_{1000}\rVert = 436.9$ and $\lVert\theta_{20000}\rVert = 2.56\times10^{22}$ with
growth rate $1.002393$; the residual gradient gives $\mathrm{MSBE} = 3.39\times10^{-5}$ and
$\max_s\lvert v\rvert = 1.54$; one-hot TD goes from $\lVert\theta_{10^3}\rVert = 21.3$ to
$\lVert\theta_{2\times10^6}\rVert = 1.0\times10^{-11}$. **These values are deterministic (there is
no randomness), so if they are not reproduced the implementation is wrong** — this is the one
reproduction task where the numbers themselves must match.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| $\min\operatorname{Re}\lambda(A) > 0$ | the importance ratio was omitted, or $\varrho>0$ was given to the dashed action too | print $\varrho = \pi/b$ — it must be $7$ for solid and $0$ for dashed |
| TD converges | the shared component $\theta_8$ is missing from the features | check that the last column of $\Phi$ is $(1,1,1,1,1,1,2)^\top$ |
| The growth rate differs from (9) | $k$ is too small for the dominant eigenmode to establish itself | print the ratio at both $k=1000$ and $k=10000$ ($1.002656$ vs $1.002393$) |
| The residual gradient diverges too | $-\gamma\phi(s_7)$ was omitted from $\phi_\Delta$, making $B$ asymmetric | print $\lVert B-B^\top\rVert_\infty$ |
| The MSBE will not go below $10^{-4}$ | the smallest nonzero eigenvalue of $B$ is $2.4\times10^{-5}$, so it is slow | raise the iteration count above $2\times10^5$ or raise $\alpha$ toward $2/\lambda_{\max}$ |
| One-hot TD is reported as divergent | the verdict was based only on the transient rise | extend $k$ to $2\times10^6$ — this is the transient response of a non-normal matrix |

## Open problems

- **(open problem) The triad in deep networks — what actually creates the instability** — in the
  linear case divergence is settled cleanly by the spectrum as in (3), but in a deep network the
  features are learned and change, so $A$ itself is time-varying. There is no theory of why target
  networks, replay buffers and normalization work, only empirical decomposition (current approach:
  [van Hasselt et al. 2018](https://arxiv.org/abs/1812.02648)). What is missing: a diagnostic that
  predicts divergence under learned features.
- **(open problem) Connecting projected Bellman error to actual policy performance** — (2) bounds
  the **value** error and connects to policy performance only through
  $\lVert V^{\pi_v} - V^\*\rVert \le 2\gamma\lVert v - V^\*\rVert/(1-\gamma)$. Multiplying the
  looseness of the two stages makes the guarantee essentially vacuous at $\gamma=0.99$. Current
  approach: global convergence analyses of policy gradients
  ([Agarwal et al. 2019](https://arxiv.org/abs/1908.00261)). What is missing: a tight path from
  value-approximation quality to policy performance.
- **(open problem) A principle for choosing the sign of the overestimation** — Double Q turns a
  positive bias into a negative one, and TD3's twin minimum pushes further into conservatism. There
  is no criterion for which sign and magnitude suits a task: in the offline setting conservatism is
  a **benefit** (`c8-offline-rl`) while under a need for exploration it is a cost. Current
  approaches: [Double DQN](https://arxiv.org/abs/1509.06461),
  [TD3](https://arxiv.org/abs/1802.09477). What is missing: a rule linking the sign of the bias to
  task properties.
- **(open problem) Sidestepping the double-sampling requirement at robot scale** — the convergence
  guarantee of R3 demands two independent successor samples from the same state, and a real robot
  cannot be rewound. Learning a model to produce the second sample imports model error
  (`c8-model-based-world-models`). Current approach: the gradient-TD family (GTD2 and TDC, S&B
  ch.11.7). What is missing: an estimator of the true MSBE gradient without rewinding.

## Concept check

Run `rc quiz c8-value-based-rl`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: where the on-policy assumption enters the proof of
$\lVert P^\pi v\rVert_D \le \lVert v\rVert_D$; whether Baird's divergence is caused by limited
expressiveness; the exact expectation of the maximum of $m$ uniform noises; the structural reason
the residual gradient converges; and whether the double estimator is an unbiased estimate of
$\max_a \mathbb{E}[\hat{Q}(a)]$.

## How to study this stage

1. **Relearn contraction in a weighted norm (60 min)** — write (5) from a blank page and circle the
   underlined stationarity equality. Write a paragraph on **what has changed** relative to the
   sup-norm contraction of `c8-mdp-pomdp-bellman`. Read S&B ch.9.4 and Tsitsiklis–Van Roy §3 side
   by side.
2. **Meet the error factor as a number (45 min)** — derive (2) and compute the factor at three
   values of $\gamma$ ($2.29$, $7.09$, $22.4$). What "TD converges" **does not** guarantee lives in
   those numbers.
3. **Build the counterexample by hand (90 min)** — write the features of (6) and the matrix $A$ of
   (7) yourself, check the eigenvalues with numpy, and then try to explain **why** a negative one
   appears in terms of the self-reinforcing loop through $\theta_8$. Construct first and compare
   with Baird 1995 §3 afterwards — the other order leaves you with something merely read.
4. **Cut each leg of the triad (90 min)** — run criterion 4 of the reproduction task for all three
   variants (one-hot / on-policy / Monte Carlo). In the one-hot case especially, watch the norm
   **rise transiently** and remember that eigenvalues alone cannot settle transient response.
5. **Read the four papers theory → practice (180 min)** — Baird (counterexample) →
   Tsitsiklis–Van Roy (convergence) → DQN (engineering stabilization) → Double DQN (measuring the
   bias). Write the one-page note for each; this is **not** optional. In the DQN note, write one
   line on which leg of the triad was touched.
6. **End at what cannot be done (75 min)** — pick the deep-network triad open problem and write a
   paragraph on what you can no longer compute once the $A$ of the reproduction task is replaced by
   learned features.

**Passing bar**: you can derive (5) and (2) from a blank page, construct Baird's counterexample and
exhibit the negative eigenvalue of $A$, derive (4) and quote its numbers, and you hold code
satisfying the four acceptance criteria plus notes on the four papers.
