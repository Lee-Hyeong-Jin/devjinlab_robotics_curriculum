---
id: c8-control-as-inference
lang: en
title: Control as inference
summary: >-
  Derive, by Lagrange duality, that the optimal policy of maximum-entropy RL is a Boltzmann
  distribution and that the optimal value is the fixed point of a soft-max backup, and show that
  the soft Bellman operator is a contraction. Then show that the variational lower bound of a
  graphical model with optimality variables is **exactly** the maximum-entropy objective, and
  expose the failure mode in which naive inference bends the dynamics to be optimistic. The lesson
  closes by deriving path-integral control and MPPI's weighted-average update from a free energy.
objectives:
  - Derive the Boltzmann policy and the soft-max backup from the entropy-regularized objective by Lagrange duality.
  - Prove that the soft Bellman operator is a sup-norm $\gamma$-contraction and explain the $\alpha\to0$ limit.
  - Show that the ELBO of the optimality-variable model equals the maximum-entropy RL objective.
  - Point out where naive inference bends the dynamics to be optimistic and measure that bias numerically.
  - Derive the path-integral solution and MPPI's exponentially weighted update from the free energy of KL control.
  - Chart the cost-versus-sample trade-off of MPPI and iLQR experimentally on the same task.
tags: [control-as-inference, maxent-rl, soft-bellman, mppi, path-integral, research]
---

# Control as inference

## Setup and notation

The Bellman operators of `c8-mdp-pomdp-bellman`, the policy parameterization of
`c8-policy-gradient` and the maximum-entropy derivation of `c8-imitation-learning` R5 carry over.
Additional **recommended** background:

- Convex optimization: Lagrange duality for entropy maximization on the simplex, convexity and
  smoothness of log-sum-exp (`r0-convex-optimization`).
- Variational inference: the ELBO, KL divergence, importance weighting and Jensen's inequality.
- Numerical optimization: Newton's method, regularization and line search
  (`r0-numerical-optimization`), the backward recursion of LQR.

Added notation:

| Symbol | Meaning |
|---|---|
| $\alpha$ | temperature, the weight of the entropy bonus; $\alpha\to0$ is standard RL |
| $H(\pi(\cdot\mid s))$ | $-\sum_a \pi(a\mid s)\log\pi(a\mid s)$ |
| $J_\alpha(\pi)$ | $\mathbb{E}_\pi\big[\sum_t \gamma^t\big(r(s_t,a_t) + \alpha H(\pi(\cdot\mid s_t))\big)\big]$ |
| $Q_\alpha, V_\alpha$ | entropy-regularized values; $V_\alpha$ is the soft-max of (3) |
| $\mathcal{T}_\alpha$ | the soft Bellman optimality operator, (4) |
| $O_t$ | the optimality variable, $p(O_t=1\mid s_t,a_t) \propto \exp(r(s_t,a_t)/\alpha)$ |
| $q$ | the variational distribution: $q(a_t\mid s_t)$ over actions, with states fixed to the true dynamics |
| $S(\mathbf{u})$ | the cumulative cost of a control sequence $\mathbf{u} = (u_0,\dots,u_{H-1})$ |
| $\lambda$ | MPPI's temperature, playing the role of $\alpha$ on the cost side |
| $w_k$ | MPPI's sample weights, $w_k \propto \exp(-S(\mathbf{u}_k)/\lambda)$ |

**This lesson in one line.** Replace the $\max$ of `c8-mdp-pomdp-bellman` **with a log-sum-exp**
and a control problem becomes an inference problem. We follow all the way through why that
substitution is legitimate (R1, R2), what it gives for free (differentiability, exploration,
multi-modal solutions) and what it charges for (temperature bias, optimistic dynamics).

## Key results

The bracket gives the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the maximum-entropy optimal policy is a Boltzmann distribution) [D3]** — for a fixed $Q$,
  the solution of
  $\max_{\pi(\cdot\mid s)}\big[\sum_a \pi(a\mid s)Q(s,a) + \alpha H(\pi(\cdot\mid s))\big]$ is
  $$
  \pi_\alpha(a\mid s) = \frac{\exp\!\big(Q(s,a)/\alpha\big)}{\sum_{a'}\exp\!\big(Q(s,a')/\alpha\big)}, \tag{1}
  $$
  and the attained maximum is
  $$
  \alpha\log\sum_a \exp\!\big(Q(s,a)/\alpha\big) \;=:\; \operatorname{softmax}_\alpha Q(s,\cdot). \tag{2}
  $$
  In other words, **the entropy bonus smooths the $\max$ into a log-sum-exp.**
- **R2 (the soft Bellman operator and its fixed point) [D3]** —
  $$
  V_\alpha(s) = \alpha\log\sum_a \exp\!\Big(\frac{r(s,a) + \gamma\sum_{s'}P(s'\mid s,a)V_\alpha(s')}{\alpha}\Big), \tag{3}
  $$
  $$
  (\mathcal{T}_\alpha v)(s) := \alpha\log\sum_a \exp\!\Big(\frac{r(s,a) + \gamma (Pv)(s,a)}{\alpha}\Big) \tag{4}
  $$
  is a $\gamma$-contraction in the sup norm, so (3) has a unique solution. That $V_\alpha$ is
  **exactly the entropy-regularized value of the policy (1)**, and since
  $0 \le V_\alpha - V^\* \le \frac{\alpha\log m}{1-\gamma}$ it converges to the standard optimal
  value as $\alpha\to0$.
- **R3 (equivalence with variational inference) [D3]** — in the graphical model with optimality
  variables $O_{0:T-1}$, if the variational distribution's **state transitions are fixed to the
  true dynamics** and only the actions are free as $q(a_t\mid s_t)$, then
  $$
  \log p(O_{0:T-1}=1) \;\ge\; \mathbb{E}_q\!\Big[\sum_t \big(r(s_t,a_t)/\alpha + H(q(\cdot\mid s_t))\big)\Big]
    \;=\; \frac{1}{\alpha}J_\alpha(q) \tag{5}
  $$
  with equality when $q$ is (1). **Maximum-entropy RL is the same problem as maximizing this
  ELBO.**
- **R4 (naive inference bends the dynamics to be optimistic) [D2]** — if the state transitions are
  also replaced by their posterior,
  $p(s_{t+1}\mid s_t,a_t,O=1) \propto P(s_{t+1}\mid s_t,a_t)\exp(V(s_{t+1})/\alpha)$, one is
  effectively **assuming the environment cooperates**. The backup then contains a **log-sum-exp
  over next states** instead of an expectation, and the value is systematically overestimated —
  the reproduction task measures that bias growing as $\alpha$ shrinks ($0.107$ at $\alpha=1$,
  $1.448$ at $\alpha=0.01$).
- **R5 (path-integral control and MPPI) [D2]** — for a prior $p(\mathbf{u})$ over control sequences
  and a cost $S(\mathbf{u})$, the minimizer of the free-energy bound
  $-\lambda\log\mathbb{E}_{p}\big[e^{-S/\lambda}\big] \le \mathbb{E}_q[S] + \lambda\,
  D_{\mathrm{KL}}(q\Vert p)$ is
  $$
  q^\star(\mathbf{u}) = \frac{1}{Z}\,p(\mathbf{u})\exp\!\big(-S(\mathbf{u})/\lambda\big), \tag{6}
  $$
  and when $p$ is Gaussian with mean $\bar{\mathbf{u}}$, the mean of $q^\star$ is estimated by the
  **exponentially weighted average** $\bar{\mathbf{u}} + \sum_k w_k\,\boldsymbol{\epsilon}_k$ with
  $w_k \propto \exp(-S_k/\lambda)$. That is MPPI's update.

## Derivation

### R1 — the Boltzmann policy and log-sum-exp

For a fixed $s$ and $Q(s,\cdot)$, solve the problem on the simplex $\Delta(\mathcal{A})$

$$
\max_{\pi \ge 0,\ \sum_a \pi(a) = 1}\; \sum_a \pi(a)Q(s,a) - \alpha\sum_a \pi(a)\log\pi(a) .
$$

The Lagrangian is $\mathcal{L} = \sum_a \pi(a)Q(s,a) - \alpha\sum_a\pi(a)\log\pi(a)
+ \nu(1-\sum_a\pi(a))$, and

$$
\frac{\partial\mathcal{L}}{\partial\pi(a)} = Q(s,a) - \alpha\log\pi(a) - \alpha - \nu = 0
  \;\Longrightarrow\; \pi(a) = \exp\!\Big(\frac{Q(s,a) - \alpha - \nu}{\alpha}\Big).
$$

Fixing $\nu$ by $\sum_a\pi(a)=1$ gives (1) (the non-negativity constraint is automatically
satisfied since $\pi > 0$ — the $\log$ of the entropy pushes away from the boundary). Substituting
the optimum,

$$
\sum_a \pi_\alpha(a)Q(s,a) + \alpha H(\pi_\alpha)
  = \sum_a \pi_\alpha(a)\Big[Q(s,a) - \alpha\log\pi_\alpha(a)\Big]
  = \sum_a \pi_\alpha(a)\cdot \alpha\log\!\sum_{a'}e^{Q(s,a')/\alpha} ,
$$

the last equality because (1) makes
$Q(s,a) - \alpha\log\pi_\alpha(a) = \alpha\log\sum_{a'}e^{Q(s,a')/\alpha}$ **independent of $a$**.
Since $\sum_a\pi_\alpha(a)=1$ this is (2).

**How to read it.** $\alpha\log\sum_a e^{Q/\alpha}$ tends to $\max_a Q$ as $\alpha\to0$ and to
$\alpha\log m + \bar{Q}$ as $\alpha\to\infty$: the temperature **interpolates continuously between
greedy and uniform**. And since
$\max_a Q \le \operatorname{softmax}_\alpha Q \le \max_a Q + \alpha\log m$, the bias is one-sided
(upward) and at most $\alpha\log m$.

**Where the assumptions break.** With an infinite (continuous) action set, $\sum_a$ becomes an
integral and the partition function has no closed form. Restricting to Gaussian policies makes (1)
no longer the **exact** optimum, and that approximation (a policy projection) is what SAC does.
Also, for very small $\alpha$ the quantity $e^{Q/\alpha}$ overflows, so an implementation must use
the log-sum-exp stabilization that factors out the $\max$.

### R2 — contraction of the soft Bellman operator and its limit

**Contraction.** Use the fact that $\operatorname{softmax}_\alpha$ is 1-Lipschitz in each argument.
Indeed

$$
\frac{\partial}{\partial Q(a)}\,\alpha\log\sum_{a'}e^{Q(a')/\alpha}
  = \frac{e^{Q(a)/\alpha}}{\sum_{a'}e^{Q(a')/\alpha}} = \pi_\alpha(a) \ge 0,
  \qquad \sum_a \pi_\alpha(a) = 1,
$$

i.e. **the gradient is a probability vector**. So by the mean value theorem, for any $u, v$,

$$
\big\lvert \operatorname{softmax}_\alpha u - \operatorname{softmax}_\alpha v \big\rvert
  \le \max_a \lvert u(a) - v(a)\rvert , \tag{7}
$$

playing **the same role** as (7) of `c8-mdp-pomdp-bellman`. The rest is literally identical:
$\lvert(\mathcal{T}_\alpha u)(s) - (\mathcal{T}_\alpha v)(s)\rvert \le \max_a \gamma\lvert (Pu)(s,a)
- (Pv)(s,a)\rvert \le \gamma\lVert u-v\rVert_\infty$, and Banach makes the solution of (3) unique.

**The fixed point is the actual value of the policy (1).** Let $V_\alpha$ solve (3) and
$\pi_\alpha$ be (1). The optimal-value identity of R1 gives
$V_\alpha(s) = \sum_a \pi_\alpha(a\mid s)\big[Q_\alpha(s,a) - \alpha\log\pi_\alpha(a\mid s)\big]$,
which is the entropy-regularized Bellman expectation equation of $\pi_\alpha$. Its solution is
unique, so $V_\alpha = V^{\pi_\alpha}_\alpha$. (Criterion 1 of the reproduction task verifies this
identity to about $10^{-14}$.)

**The $\alpha\to0$ limit.** Substituting the two-sided bound of (2) into the operators gives
$\mathcal{T}^\* v \le \mathcal{T}_\alpha v \le \mathcal{T}^\* v + \alpha\log m$. Both operators are
$\gamma$-contractions, so their fixed points differ by at most

$$
0 \;\le\; V_\alpha - V^\* \;\le\; \frac{\alpha\log m}{1-\gamma} \tag{8}
$$

(the standard argument that the fixed point of a contraction is $1/(1-\gamma)$-stable under
perturbation of the operator). At $\gamma=0.9$, $m=3$ and $\alpha=0.01$ the bound is $0.110$ while
the **measured difference is $0.0107$** — the bound is ten times loose.

**Where the assumptions break.** (8) is a statement for a **fixed** temperature. When $\alpha$ is
auto-tuned as a constraint ($H \ge \bar{H}$) as in SAC, it varies with state and time and the
fixed-point argument of (3) does not apply directly. And if $\alpha$ is large the bias of (8) is
large, so **the entropy bonus changes the task** — which is why a reported score must always come
with its $\alpha$ when compared against standard RL.

### R3 — the ELBO equals the maximum-entropy objective

**The model.** Put a prior over states and actions and attach a binary **optimality variable**
$O_t$ at each step with $p(O_t = 1\mid s_t,a_t) = \exp\big(r(s_t,a_t)/\alpha\big)$ (shift the reward
to be $\le 0$ so this reads as a probability). Take the action prior to be uniform. What we want is
the log-likelihood of the evidence "every step was optimal", $\log p(O_{0:T-1}=1)$.

**The variational bound.** Take the variational distribution
$q(s_{0:T},a_{0:T-1}) = \rho_0(s_0)\prod_t q(a_t\mid s_t) P(s_{t+1}\mid s_t,a_t)$ — the key is that
**the state transitions are pinned to the true dynamics**. By Jensen,

$$
\log p(O_{0:T-1}=1) \;\ge\; \mathbb{E}_q\!\left[\log\frac{p(s_{0:T},a_{0:T-1},O=1)}{q(s_{0:T},a_{0:T-1})}\right].
$$

The numerator is $\rho_0\prod_t \big[\tfrac{1}{m}P(s_{t+1}\mid s_t,a_t)e^{r_t/\alpha}\big]$ and the
denominator is $\rho_0\prod_t\big[q(a_t\mid s_t)P(s_{t+1}\mid s_t,a_t)\big]$. **The $\rho_0$ and
the $P$ cancel.** What remains is

$$
\mathbb{E}_q\!\Big[\sum_t \Big(\frac{r(s_t,a_t)}{\alpha} - \log\big(m\,q(a_t\mid s_t)\big)\Big)\Big]
  = \mathbb{E}_q\!\Big[\sum_t \Big(\frac{r_t}{\alpha} + H\big(q(\cdot\mid s_t)\big)\Big)\Big] - T\log m ,
$$

which, up to a constant, is (5). Multiplying by $\alpha$ gives exactly $J_\alpha(q)$. Equality
holds when the variational distribution is the exact posterior $p(a_t\mid s_t, O_{t:T-1}=1)$, and
that posterior is (1) of R1 — computing it backwards reproduces the soft backup of (3).

**What this buys.** ① Exploration enters the objective (the entropy term). ② Multi-modal solutions
are natural (if the posterior is multi-modal so is the policy). ③ The $\max$ becomes a
differentiable $\operatorname{softmax}$, which suits first-order methods. ④ The **same exponential
family** appears as in inverse RL (`c8-imitation-learning` R5), so the two problems live in one
framework.

**Where the assumptions break.** The reward has to be shifted to $r \le 0$ for $e^{r/\alpha}$ to be
a probability. The shift adds a constant to the value and so does not change the optimal policy
(ⓐ and ⓑ of `c8-imitation-learning` R4), but with discounting the constant is amplified by
$1/(1-\gamma)$ and the **numerical scale** changes. And (5) was written for a finite horizon — the
discounted infinite-horizon case requires a geometric number of $O_t$ or discounting inside the
prior.

### R4 — the optimistic dynamics of naive inference

If the variational distribution is allowed to change **the state transitions as well**, the ELBO
gets larger (more freedom). Its optimum is

$$
q^\star(s_{t+1}\mid s_t,a_t) \;\propto\; P(s_{t+1}\mid s_t,a_t)\,\exp\big(V(s_{t+1})/\alpha\big),
$$

i.e. **it inflates the probability of transitions to good outcomes.** The backup then becomes

$$
V_{\mathrm{opt}}(s) = \operatorname{softmax}_\alpha\Big[r(s,a)
  + \underbrace{\alpha\log\sum_{s'}P(s'\mid s,a)\exp\big(\gamma V_{\mathrm{opt}}(s')/\alpha\big)}_{\text{a soft-max over next states}}\Big] \tag{9}
$$

so the expectation $\sum_{s'}P V$ **turns into a log-sum-exp**. By Jensen,
$\alpha\log\mathbb{E}[e^{\gamma V/\alpha}] \ge \gamma\mathbb{E}[V]$, hence
$V_{\mathrm{opt}} \ge V_\alpha$, and the difference is a **risk-seeking bias**: it plans as though
luck will cooperate, which cannot be used on a robot.

The size of the bias is proportional to the variance and to $1/\alpha$ (applying
$\log\mathbb{E}[e^{X}] \approx \mathbb{E}[X] + \tfrac12\mathrm{Var}(X)$ to $X = \gamma V/\alpha$
gives $\tfrac{\gamma^2}{2\alpha}\mathrm{Var}(V)$). So **the lower the temperature the larger the
bias** — the reproduction task measures it growing from $0.107$ to $1.448$ as $\alpha$ drops from
$1$ to $0.01$.

**Where the assumptions break.** With deterministic dynamics $\mathrm{Var}(V) = 0$, so (9) and (3)
coincide and **the bias vanishes**. That is how a method developed in a deterministic simulator can
break on a stochastic real system. Conversely, pinning the variational distribution to the true
dynamics (R3) removes the bias at the price of a looser ELBO — a rare case where **choosing the
looser bound is the correct decision**.

### R5 — from the free energy to MPPI

**The free-energy inequality.** For any distribution $q$ and prior $p$,

$$
-\lambda\log\mathbb{E}_{p}\big[e^{-S(\mathbf{u})/\lambda}\big]
  \;\le\; \mathbb{E}_q\big[S(\mathbf{u})\big] + \lambda\,D_{\mathrm{KL}}(q\Vert p) \tag{10}
$$

(Donsker–Varadhan). The proof is to check that the right side minus the left is
$\lambda D_{\mathrm{KL}}(q\Vert q^\star) \ge 0$, with equality when $q = q^\star$, i.e. (6). Let us
verify it directly:

$$
\mathbb{E}_q[S] + \lambda D_{\mathrm{KL}}(q\Vert p)
  = \lambda\,\mathbb{E}_q\!\left[\log\frac{q}{p\,e^{-S/\lambda}}\right]
  = \lambda\,\mathbb{E}_q\!\left[\log\frac{q}{q^\star}\right] - \lambda\log Z ,
$$

where $Z = \mathbb{E}_p[e^{-S/\lambda}]$. The first term is
$\lambda D_{\mathrm{KL}}(q\Vert q^\star)\ge0$ and the second is the left side of (10), which
finishes it.

**MPPI's update.** Take $p$ Gaussian with mean $\bar{\mathbf{u}}$ and covariance $\Sigma$ and
estimate the mean of (6) by importance weighting. Drawing $K$ samples
$\mathbf{u}_k = \bar{\mathbf{u}} + \boldsymbol{\epsilon}_k$ with
$\boldsymbol{\epsilon}_k \sim \mathcal{N}(0,\Sigma)$,

$$
\mathbb{E}_{q^\star}[\mathbf{u}] \;\approx\; \bar{\mathbf{u}} + \sum_{k=1}^{K} w_k\,\boldsymbol{\epsilon}_k,
  \qquad w_k = \frac{\exp\big(-(S_k - S_{\min})/\lambda\big)}{\sum_{j}\exp\big(-(S_j - S_{\min})/\lambda\big)} , \tag{11}
$$

where subtracting $S_{\min}$ is numerical stabilization and does not change $w$. Iterating this is
MPPI, and **as $\lambda\to0$ the weights collapse onto the single lowest-cost sample**, recovering
the "pick the best sample" of random shooting. As $\lambda\to\infty$ the weights become uniform and
the update goes to zero.

**Contrast with iLQR.** iLQR solves the same problem by a **second-order expansion plus a backward
recursion**. Using derivatives, it needs no samples and converges quickly, but it requires
differentiability and local convexity and gets stuck in local minima. MPPI uses no derivatives, so
it applies to contact and discontinuous costs, but its sample requirement is sensitive to
dimension. The reproduction task measures this trade-off on the same task.

**Where the assumptions break.** (11) uses the mean of $q^\star$, but if $q^\star$ is
**multi-modal** the mean can be a control sequence belonging to no mode — the classic failure in
which the average of two avoidance paths drives straight into the obstacle. And if $\lambda$ is
small relative to the cost scale the effective sample size collapses to one (the same phenomenon as
the ESS of `c8-offline-rl` R5), while if it is large the update disappears.

## Proof sketch

### R1 and R2 — Boltzmann optimality and the soft contraction [D3]

**Hypotheses** H1: $\mathcal{A}$ finite ($\lvert\mathcal{A}\rvert = m$) with bounded rewards.
H2: $0\le\gamma<1$. H3: $\alpha > 0$.
**Conclusions** C1: (1) and (2). C2: $\mathcal{T}_\alpha$ is a $\gamma$-contraction and (3) has a
unique solution. C3: $V_\alpha = V^{\pi_\alpha}_\alpha$ and (8).

**Strategy**: C1 by **Lagrange duality on the simplex**. C2 by the fact that **the gradient of
$\operatorname{softmax}$ is a probability vector**, which gives 1-Lipschitzness and lets the
argument of `c8-mdp-pomdp-bellman` be reused. C3 by fixed-point stability under operator
perturbation.

1. First-order conditions of the entropy-regularized linear problem on the simplex → (1). Uses: H3
   (so the $\log$ term exists), H1 (a finite sum).
2. Substitute (1) and use that $Q - \alpha\log\pi_\alpha$ is independent of $a$ → (2).
3. $\partial\operatorname{softmax}/\partial Q(a) = \pi_\alpha(a)$ is a probability vector → (7)
   → C2. Uses: H2.
4. The optimal-value identity of R1 coincides with the entropy Bellman expectation equation of
   $\pi_\alpha$ → the first part of C3.
5. $\mathcal{T}^\* v \le \mathcal{T}_\alpha v \le \mathcal{T}^\* v + \alpha\log m$ plus fixed-point
   stability → (8). Uses: H1 (so $\log m$ is finite).

**Delete one hypothesis**: allowing $\alpha\to0$ in H3 removes the $\log\pi$ term of step 1, so the
solution becomes a **vertex** of the simplex (a deterministic policy) and (1) is undefined — the
limit has to be handled through (8). Letting $m\to\infty$ in H1 makes the bound of (8) infinite and
the temperature bias uncontrollable. For continuous actions, replacing $\log m$ by a **differential
entropy** does not even guarantee a sign.

Omitted: existence of the partition function and the exchange conditions for continuous actions are
in Haarnoja et al. 2017 §3 and Levine 2018 §2.3.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1·R2)** Prove the two-sided bound
$\max_a Q \le \operatorname{softmax}_\alpha Q \le \max_a Q + \alpha\log m$ and use it to derive (8).
At $\gamma = 0.9$ and $m = 3$, how small must $\alpha$ be for the bias bound to be at most $0.01$?
*Solution sketch*: for the lower bound keep a single term; for the upper bound raise every term to
the $\max$. (8) is the standard argument that the fixed points of two contractions differ by at
most $1/(1-\gamma)$ times the operator difference.
$\alpha\log 3/(1-0.9) \le 0.01 \Rightarrow \alpha \le 0.01\cdot0.1/\log 3 = 9.1\times10^{-4}$.

**P2 (proof, ★★★, R3)** Derive (5) and show that equality holds when $q$ is the exact posterior.
Then show that freeing the state transitions in the variational distribution makes the ELBO
**larger** but that its solution is the optimistic backup of (9).
*Strategy and key inequality*: the ELBO gap is
$D_{\mathrm{KL}}(q\Vert p(\cdot\mid O=1))$, so equality holds when the KL is zero. Freeing the
transitions gives the same first-order condition
$q^\star(s'\mid s,a)\propto P\,e^{V/\alpha}$, and substituting it back into the ELBO yields (9).
The expansion is withheld.

**P3 (numerical, ★, R2·R4)** On a small MDP with $\gamma=0.9$ and $m=3$, compute the bound (8) for
$\alpha = 1, 0.1, 0.01$ and determine what fraction of the bound the measured difference
$V_\alpha - V^\*$ is. Also explain, by a second-order expansion, why the optimistic bias of (9)
**grows** as $\alpha$ shrinks.
*Answer*: the bound is $\alpha\log 3/(1-\gamma) = 10.986\,\alpha$, i.e. $10.986,\ 1.0986,\ 0.10986$
(tolerance $10^{-3}$). The measured difference at $\alpha=0.01$ is $0.0107$, about $1/10$ of the
bound. For the bias,
$\log\mathbb{E}[e^{\gamma V/\alpha}] \approx \gamma\mathbb{E}[V]/\alpha
+ \tfrac{\gamma^2}{2\alpha^2}\mathrm{Var}(V)$, and multiplying by $\alpha$ gives
$\gamma\mathbb{E}[V] + \tfrac{\gamma^2}{2\alpha}\mathrm{Var}(V)$ — the second term grows as
$1/\alpha$.
Check: write one line on why the ratio of the measured values $0.107$ ($\alpha=1$) and $1.448$
($\alpha=0.01$) is **smaller** than the factor of $100$ predicted at fixed variance (because $V$
itself changes with $\alpha$).

**P4 (implementation, ★★, R5)** Implement MPPI and iLQR on the same pendulum swing-up task and
chart the cost as a function of the **number of rollouts**. Tune $\lambda$ and the sample count $K$
for MPPI, and the regularization and line search for iLQR.
*Rubric*: ⓐ the cost function, horizon and initial control sequence are **identical** for both
methods; ⓑ the horizontal axis is the **number of rollouts (or dynamics calls)** rather than
iterations — not counting iLQR's finite-difference Jacobian cost makes the comparison unfair;
ⓒ the $S_{\min}$ subtraction is included in MPPI's weights; ⓓ $\lambda$ is tuned to the cost scale
and the effective sample size is reported alongside; ⓔ iLQR increases the regularization when the
line search fails.

**P5 (counterexample, ★★, R5)** Show that the claim "MPPI always improves with more samples" is
false. Construct a case in which, with $\lambda$ far too small relative to the cost scale,
increasing $K$ does not help (or hurts), and explain the cause in terms of the effective sample
size.
*Property checklist*: ⓐ when $\lambda \ll$ the cost standard deviation, $w$ collapses onto the
single lowest-cost sample; ⓑ the update then becomes "the noise of the lowest-cost sample", i.e. a
**high-variance random search**; ⓒ increasing $K$ makes that lowest-cost sample more extreme, so
the update can fluctuate more; ⓓ the diagnostic is to print
$\mathrm{ESS} = 1/\sum_k w_k^2$, and the prescription is to adapt $\lambda$ to the cost variance.

**P6 (paper, ★★, R3·R4·R5)** Read Levine 2018 (§2–4), SAC (§3–4) and MPPI (§II–III) and write, in
at most three sentences each: (i) how Levine 2018 organizes the "optimistic dynamics" problem and
what it prescribes; (ii) the gap created when SAC projects the Boltzmann policy of (1) onto a
Gaussian, and its price; (iii) the equation in MPPI's information-theoretic derivation that
corresponds to (10), and the role of $\lambda$.
*Grading rubric*: (i) passes if it names the prescription of pinning the variational state
transitions to the true dynamics. (ii) that the projection loosens the ELBO and loses multi-modal
solutions (and that the price is paid through reparameterization gradients). (iii) the free-energy
or Donsker–Varadhan inequality, with $\lambda$ as the weight of the KL penalty (hence the
exploration width). Writing only "it averages samples with weights" fails.

**P7 (derivation, ★★, R5)** Prove (10) directly, and explain by importance weighting why the mean
of (6) is estimated by the weighted average of (11) when $p$ is Gaussian. What does the update
become in the limits $\lambda\to0$ and $\lambda\to\infty$?
*Solution sketch*: writing $\mathbb{E}_q[S] + \lambda D_{\mathrm{KL}}(q\Vert p) = \lambda
D_{\mathrm{KL}}(q\Vert q^\star) - \lambda\log Z$ finishes it. (11) is reading
$q^\star/p = e^{-S/\lambda}/Z$ as an importance weight. $\lambda\to0$ gives lowest-cost sample
selection (random shooting) and $\lambda\to\infty$ gives a zero update.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions
(`lesson-standard.md` §5). Read with three passes and attack questions 4, 5, 6 and 7 in the third.

1. **Levine, "Reinforcement learning and control as probabilistic inference: tutorial and review"
   (2018, arXiv)** — role: `survey`. <https://arxiv.org/abs/1805.00909> — §2-4.
   Why read it: R1 through R4 are this review's framework, and in particular the optimistic-dynamics
   problem and its prescription are organized in §4.
   Extra questions: ⓐ which of (3) and (9) corresponds to the author's distinction between "exact
   inference" and "variational inference"? ⓑ what does the author propose for putting the discount
   $\gamma$ into the graphical model?
2. **Haarnoja, Zhou, Abbeel & Levine, "Soft actor-critic" (2018, ICML)** — role: `standard`.
   <https://arxiv.org/abs/1801.01290> — §3-4.
   Why read it: this is the actual method for **projecting** (1) onto a Gaussian for continuous
   actions, and a case study of how automatic temperature tuning handles the bias of (8).
   Extra questions: ⓐ how exactly does the KL minimization of the policy improvement step differ
   from (1) (the projection error)? ⓑ when the temperature becomes a constraint, which part of the
   fixed-point argument of R2 stops holding?
3. **Williams, Aldrich & Theodorou, "Model predictive path integral control: from theory to
   parallel computation" (2017, JGCD)** — role: `standard`.
   <https://doi.org/10.2514/1.G001921> — §II-III.
   Why read it: (10) and (11) of R5 are this paper's information-theoretic derivation.
   Extra questions: ⓐ where in the authors' free-energy derivation do the control cost and the
   state cost separate? ⓑ what criterion does the paper give for choosing the sample count and the
   horizon in a real-time implementation?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation? (4) what is guaranteed and **what is not**?
(5) independent and dependent variables, and the baselines — were they tuned fairly? (6) does the
metric match the claim, and are variance and seeds reported? (7) what information needed for
reproduction is missing? (8) if the result were wrong, which assumption would you doubt first?
(9) compute and memory cost, and real-time feasibility? (10) what would you change to go beyond
this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: under **five minutes** on a laptop CPU (about a
hundred million pure-Python dynamics calls), under 200 MB, numpy only. No data needed.

It has two parts. **A is a tabular soft-Bellman verification** (does the theory hold exactly?) and
**B is MPPI versus iLQR** (how does the practical trade-off come out?). Pass A before moving to B.

**A. Tabular soft Bellman.** Generate $\lvert\mathcal{S}\rvert=12$, $\lvert\mathcal{A}\rvert=3$,
$\gamma=0.9$, Dirichlet(0.5) transitions and $U(0,1)$ rewards. Implement the soft value iteration
of (3), the Boltzmann policy of (1), that policy's entropy-regularized value (by linear solve),
standard value iteration, and the optimistic iteration of (9).

**B. Pendulum swing-up.** $\dot\omega = \tfrac{3g}{2l}\sin\theta + \tfrac{3}{ml^2}u$ with Euler
integration $\Delta t = 0.05$, $m=l=1$, $u\in[-5,5]$, horizon $H=50$, initial state
$(\theta,\omega)=(\pi,0)$. The per-step cost is
$\mathrm{wrap}(\theta)^2 + 0.1\omega^2 + 0.001u^2$ and the terminal cost is
$10(\mathrm{wrap}(\theta)^2 + 0.1\omega^2)$. The initial control sequence is $u\equiv0$ (cost
$592.18$). Implement iLQR with finite-difference Jacobians, regularization and a line search, and
MPPI with (11), smoothing the noise in time as
$\epsilon_t \leftarrow \beta\epsilon_{t-1} + (1-\beta)\epsilon_t$ ($\beta=0.8$, $\sigma=4$).

**Acceptance criteria** — all five must hold.

1. **The soft fixed point is the Boltzmann policy's actual value**: for every
   $\alpha \in \{1, 0.3, 0.1, 0.03, 0.01\}$,
   $\max_s\lvert V_\alpha(s) - V^{\pi_\alpha}_\alpha(s)\rvert < 10^{-12}$ (measured
   $4\times10^{-15}$–$7\times10^{-15}$). Obtain $V^{\pi_\alpha}_\alpha$ as the linear solve with
   $\alpha H(\pi_\alpha)$ added to the reward.
2. **Contraction (7)**: over 300 random pairs $u,v$,
   $\lVert\mathcal{T}_\alpha u - \mathcal{T}_\alpha v\rVert_\infty / \lVert u-v\rVert_\infty \le \gamma$
   for every $\alpha$ (measured maxima $0.598$–$0.630 \le 0.9$).
3. **Temperature bias (8)**: $0 \le V_\alpha - V^\* \le \alpha\log m/(1-\gamma)$ holds, and at
   $\alpha=0.01$ the measured difference $0.0107$ is reported as about $1/10$ of the bound
   $0.1099$. At the same time, at $\alpha=0.01$ the greedy action of the Boltzmann policy agrees
   with the standard optimal policy at **12 of 12 states**.
4. **Optimistic-dynamics bias (9)**: $V_{\mathrm{opt}} \ge V_\alpha$ for every $\alpha$, and the
   maximum difference **increases monotonically** as $\alpha$ shrinks (measured $\alpha=1$:
   $0.107$, $0.3$: $0.292$, $0.1$: $0.597$, $0.03$: $1.117$, $0.01$: $1.448$).
5. **MPPI versus iLQR (B)**: ⓐ iLQR's cost **decreases monotonically** and reaches $J \le 105$
   within 20,000 rollout-equivalents (measured $99.79$ at 16,350). ⓑ MPPI ($\lambda=5$, $K=64$, 60
   iterations) reaches $J \le 130$ within 4,000 rollouts (measured $119.0$ at 3,840). ⓒ MPPI's mean
   effective sample size is **at most** $0.1K$ ($1.7$ at $K=256$, $3.3$ at $K=1024$) — the
   diagnostic that the weights are collapsing. ⓓ at the same $\lambda$, raising $K$ from $64$ to
   $1024$ makes the final cost **worse** ($119.0 \to 162.9$) — the counterexample of problem P5
   actually happens.

**Baselines**: ⓐ the do-nothing control sequence ($J_0 = 592.18$) — the common starting point of
both methods. ⓑ standard value iteration ($\alpha\to0$) — the reference for criterion 3.
ⓒ optional: adapt MPPI's $\lambda$ in proportion to the cost standard deviation (e.g.
$\lambda_t = \mathrm{std}(S_k)$) and check whether criteria ⓒ and ⓓ improve. That is the experiment
testing whether the prescription of P5 works in code.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The difference in criterion 1 is around $10^{-6}$ | the entropy term was not added to the reward; only the policy value was computed | print the reward vector with $\alpha H(\pi_\alpha)$ added |
| `inf`/`nan` at small $\alpha$ | the log-sum-exp stabilization is missing | check that $\max_a Q$ is factored out before exponentiating |
| The sign in criterion 3 is negative ($V_\alpha < V^\*$) | the $\alpha$ factors in the soft backup are misplaced | check that both $\alpha$'s of $\alpha\log\sum e^{Q/\alpha}$ are present |
| $V_{\mathrm{opt}} < V_\alpha$ in criterion 4 | the $\gamma$ was left out of the exponent in (9) | check the form $\alpha\log\sum_{s'}P e^{\gamma V/\alpha}$ |
| iLQR diverges | the regularization is not increased when the line search fails | print the smallest eigenvalue of $Q_{uu}$ and the regularizer every iteration |
| iLQR's cost goes up and down | a step was accepted without checking improvement in the line search | add the $J_{\mathrm{new}} < J$ test |
| MPPI does not improve at all | $\lambda$ is so small relative to the cost scale that $\mathrm{ESS}\approx1$ | print $\mathrm{ESS} = 1/\sum_k w_k^2$ and try a larger $\lambda$ |
| MPPI cannot swing up | the noise is white, so the trajectory only jitters | set $\beta = 0.8$ for time-smoothed noise (at $\lambda=10,\sigma=4,K=512$ over 30 iterations, $\beta=0$ gives $337.3$ and $\beta=0.8$ gives $152.2$) |

## Open problems

- **(open problem) A principle for setting the temperature per task** — (8) quantifies that
  $\alpha$ **creates a bias** but says nothing about how large it should be. SAC auto-tunes it
  through an entropy constraint, but the target entropy $\bar{H}$ is a new hyperparameter and its
  choice changes the outcome. Current approaches: the bilevel optimization of
  [SAC](https://arxiv.org/abs/1801.01290), [soft Q-learning](https://arxiv.org/abs/1702.08165).
  What is missing: a rule that back-solves $\alpha$ from a task metric.
- **(open problem) The risk attitude of inference-based control under stochastic dynamics** — R4
  shows that naive inference becomes risk-seeking and that pinning the variational distribution to
  the true dynamics removes it. But which variational family is correct for a robot task that needs
  **risk aversion** has not been settled. Current approaches: the discussion in
  [Levine 2018](https://arxiv.org/abs/1805.00909) §4, linearly-solvable MDPs
  ([Todorov 2009](https://doi.org/10.1073/pnas.0710743106)). What is missing: an inference
  formulation with a specified risk attitude.
- **(open problem) MPPI's sample complexity and dimension** — the estimate in (11) is importance
  weighting, so the effective sample size is exponentially sensitive to control dimension and
  horizon (in the reproduction task $K=1024$ yields $\mathrm{ESS}=3.3$). Adding samples is
  therefore not the answer, and there is no theory of which structure (smoothed noise,
  low-dimensional parameterizations, learned priors) breaks that dependence. Current approaches:
  [MPPI](https://doi.org/10.2514/1.G001921),
  [PI^2](https://www.jmlr.org/papers/v11/theodorou10a.html). What is missing: a sample-complexity
  guarantee polynomial in the control dimension.
- **(open problem) Avoiding the averaging of multi-modal solutions** — (11) uses the **mean** of
  $q^\star$, so the failure in which the average of two avoidance paths drives into the obstacle is
  structurally possible. Approaches that track modes separately (mixture models, multiple
  hypotheses) cost more compute and require the number of modes in advance. Current approaches: the
  policy-improvement view of
  [Theodorou et al. 2010](https://www.jmlr.org/papers/v11/theodorou10a.html), graph-based trajectory
  sets (the planning theory of the `c6-*` module). What is missing: an update rule that avoids mean
  collapse without knowing the number of modes.

## Concept check

Run `rc quiz c8-control-as-inference`. The quiz is for **concept checking only**; the real work is
the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: why the optimal policy of the entropy-regularized objective is a Boltzmann
distribution; the ground for the soft Bellman operator being a $\gamma$-contraction; whether the
state transitions should be left free in the variational distribution; MPPI's weights in terms of
cost and temperature; and whether increasing MPPI's sample count always helps.

## How to study this stage

1. **Start from the problem on the simplex (45 min)** — write the Lagrange first-order condition of
   R1 from a blank page. That the Boltzmann policy is **a result, not an assumption** is the first
   turning point of this lesson. Then check the two-sided bound of (2) by hand to get a feel for the
   size of the temperature bias.
2. **Reuse the contraction argument (45 min)** — once you confirm the single line that the gradient
   of $\operatorname{softmax}$ is a probability vector, the argument of `c8-mdp-pomdp-bellman` runs
   unchanged. Write the two lessons' (7) side by side and see **what has been replaced**.
3. **Derive the ELBO and watch the cancellation (75 min)** — the point of R3 is where $\rho_0$ and
   $P$ cancel. If you can write in one sentence why they cancel (because the variational state
   transitions were pinned to the true dynamics), the failure mode of R4 becomes obvious by itself.
4. **Meet the optimistic bias as a number (60 min)** — run criterion 4 of part A and watch the bias
   grow as $\alpha$ drops. Then make the dynamics deterministic and confirm that the bias
   **disappears** — one precise cause of "it was fine in the simulator and broke on the robot".
5. **Compare MPPI and iLQR on the same axis (120 min)** — run part B. Putting **rollouts** rather
   than iterations on the horizontal axis is the key to fairness. Print the ESS to see the weight
   collapse directly, confirm that increasing $K$ does not help, and then solve problem P5.
6. **The three papers and the open problems (150 min)** — Levine 2018 (the framework) → SAC
   (continuous actions) → MPPI (sample-based). Write the one-page note for each; this is **not**
   optional. Finally, pick the risk-attitude open problem and write a paragraph on which sign in (9)
   would have to change to turn the optimistic iteration of part A into a **risk-averse** one.

**Passing bar**: you can derive (1), (2) and (10) from a blank page, say why $P$ cancels in the ELBO
and what bias appears when that is violated, and you hold code satisfying the five acceptance
criteria plus notes on the three papers.
