---
id: c8-policy-gradient
lang: en
title: The policy gradient theorem
summary: >-
  Derive the policy gradient theorem from the value-function recursion with no missing steps,
  and work out why a baseline is unbiased and how much variance it removes, down to the
  variance-minimizing baseline. Then build the monotone improvement bound of TRPO from the
  performance difference lemma, show that the natural gradient is the second-order solution of a
  KL-constrained step, and pin down why PPO's clipping does not inherit the guarantee.
objectives:
  - Derive the policy gradient theorem from the recursion for $V^\pi$ with no missing steps.
  - Prove that a state-dependent baseline is unbiased and compute the variance-minimizing baseline.
  - Prove the performance difference lemma and show the first-order agreement of the surrogate objective.
  - Explain the monotone improvement bound $J(\pi') \ge L_\pi(\pi') - C\,D_{\mathrm{KL}}^{\max}$ of TRPO and where the constant $C$ comes from.
  - Derive the natural gradient as the solution of a second-order expansion under a KL constraint and explain its reparameterization invariance.
  - Point out what PPO's clipping does not guarantee and where implementation details account for the reported gap.
tags: [policy-gradient, trpo, ppo, natural-gradient, variance-reduction, research]
---

# The policy gradient theorem

## Setup and notation

The MDP notation and the two Bellman operators of `c8-mdp-pomdp-bellman` carry over unchanged.
In addition the following is **recommended** background (the platform does not lock the lesson):

- Multivariable calculus: the chain rule, exchanging differentiation and summation (dominated
  convergence), gradients and Hessians.
- Probability: the score-function identity, the variance of a Monte Carlo estimator, the tower
  rule for conditional expectation.
- Convex optimization: Lagrange duality with equality and inequality constraints, second-order
  expansions and trust regions (`r0-convex-optimization`).

Added notation (shared across module C8):

| Symbol | Meaning |
|---|---|
| $\pi_\theta(a \mid s)$ | a differentiable policy parameterized by $\theta \in \mathbb{R}^p$, with $\pi_\theta(a\mid s) > 0$ (assumption **A3**) |
| $J(\theta)$ | $\mathbb{E}_{s_0 \sim \rho_0}\big[V^{\pi_\theta}(s_0)\big]$ |
| $\rho^\pi(s)$ | **unnormalized** discounted occupancy, $\rho^\pi(s) = \sum_{t \ge 0} \gamma^t \Pr(s_t = s \mid \pi, \rho_0)$ |
| $d^\pi(s)$ | normalized occupancy distribution, $d^\pi(s) = (1-\gamma)\,\rho^\pi(s)$, $\sum_s d^\pi(s) = 1$ |
| $A^\pi(s,a)$ | advantage, $A^\pi(s,a) = Q^\pi(s,a) - V^\pi(s)$ |
| $g_\theta(s,a)$ | score, $g_\theta(s,a) = \nabla_\theta \log \pi_\theta(a \mid s) \in \mathbb{R}^p$ |
| $F(\theta)$ | Fisher information matrix, $F(\theta) = \mathbb{E}_{d^\pi,\pi}\big[g_\theta g_\theta^\top\big] \in \mathbb{R}^{p\times p}$ |
| $D_{\mathrm{KL}}^{\max}(\pi \Vert \pi')$ | $\max_s D_{\mathrm{KL}}\big(\pi(\cdot\mid s) \Vert \pi'(\cdot\mid s)\big)$ |
| $L_\pi(\pi')$ | surrogate objective, $L_\pi(\pi') = \frac{1}{1-\gamma}\mathbb{E}_{s \sim d^\pi, a\sim\pi'}\big[A^\pi(s,a)\big]$ |

A3 (the policy gives every action positive probability) is what makes $\log \pi_\theta$ defined,
and it is also the reason the gradient **vanishes** along a path that converges to a deterministic
policy (the background of problem P5).

## Key results

The bracket gives the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the policy gradient theorem) [D3]** — under A1–A3,
  $$
  \nabla_\theta J(\theta) = \sum_s \rho^\pi(s) \sum_a \nabla_\theta \pi_\theta(a\mid s)\, Q^\pi(s,a)
    = \frac{1}{1-\gamma}\, \mathbb{E}_{s \sim d^\pi,\, a \sim \pi_\theta}\!\big[\, g_\theta(s,a)\, Q^\pi(s,a) \,\big]. \tag{1}
  $$
  The content of the theorem is that **the $\theta$-dependence of the occupancy $\rho^\pi$
  disappears** — the transition model of the environment never has to be differentiated.
- **R2 (unbiasedness and the optimal baseline) [D3]** — for any $b : \mathcal{S} \to \mathbb{R}$ we
  have $\mathbb{E}_{a\sim\pi}[g_\theta(s,a)\, b(s)] = 0$, so replacing $Q^\pi$ with $Q^\pi - b$
  leaves (1) **unbiased**. For a scalar parameter the variance-minimizing baseline is
  $$
  b^\star(s) = \frac{\mathbb{E}_{a\sim\pi}\big[\lVert g_\theta(s,a)\rVert^2\, Q^\pi(s,a)\big]}
                    {\mathbb{E}_{a\sim\pi}\big[\lVert g_\theta(s,a)\rVert^2\big]}, \tag{2}
  $$
  which is in general **not** $V^\pi(s)$ (problem P3 computes an instance where the $V^\pi$
  baseline is nine times worse than $b=0$). Using the reward-to-go $G_t$ instead of the total
  return $G_0$ (causality) is also unbiased and reduces variance.
- **R3 (the performance difference lemma) [D3]** — for any two policies $\pi, \pi'$,
  $$
  J(\pi') - J(\pi) = \frac{1}{1-\gamma}\,
    \mathbb{E}_{s \sim d^{\pi'},\, a \sim \pi'}\big[A^\pi(s,a)\big]. \tag{3}
  $$
  That the occupancy on the right belongs to **$\pi'$** is the starting point of every trust-region
  argument.
- **R4 (the monotone improvement bound of TRPO) [D3]** — the surrogate $L_\pi(\pi')$, obtained
  from (3) by replacing $d^{\pi'}$ with $d^\pi$, agrees with $J$ in value and first derivative at
  $\pi' = \pi$, and with $\epsilon := \max_{s,a}\lvert A^\pi(s,a)\rvert$,
  $$
  J(\pi') \;\ge\; J(\pi) + L_\pi(\pi') - \frac{4\epsilon\gamma}{(1-\gamma)^2}\, D_{\mathrm{KL}}^{\max}(\pi\Vert\pi'). \tag{4}
  $$
  So whenever the improvement in $L_\pi(\pi')$ exceeds the penalty, **true performance increases
  monotonically**. The constant $4\epsilon\gamma/(1-\gamma)^2$ is enormous at practical scale, so
  using the bound literally drives the step size to nearly zero — which is why TRPO replaces
  $D_{\mathrm{KL}}^{\max}$ with a mean-KL constraint.
- **R5 (the natural gradient is the second-order KL-constrained step) [D2]** — maximizing the
  first-order objective inside a KL trust region of radius $\delta$ gives
  $$
  \Delta\theta^\star = \sqrt{\frac{2\delta}{\nabla J^\top F^{-1} \nabla J}}\; F(\theta)^{-1}\nabla_\theta J(\theta)
    + O(\delta) \tag{5}
  $$
  and, because $F$ is the Hessian of the KL divergence, this step is **invariant to
  reparameterization of $\theta$**.
- **R6 (what PPO's clipping does not guarantee) [D1]** — the clipped objective **zeroes the
  gradient** of samples whose ratio $\rho_t = \pi'(a_t\mid s_t)/\pi(a_t\mid s_t)$ has left the
  window; it does not constrain $D_{\mathrm{KL}}$. The premise of (4) therefore does not hold and
  there is no monotone improvement guarantee. A substantial part of the reported performance gap
  comes not from the algorithm but from implementation details (advantage normalization,
  observation normalization, learning-rate annealing, gradient clipping) — Engstrom et al. 2020.

## Derivation

### R1 — the policy gradient theorem

Unroll $\nabla_\theta V^\pi(s)$ recursively. From $V^\pi(s) = \sum_a \pi_\theta(a\mid s) Q^\pi(s,a)$
and $Q^\pi(s,a) = r(s,a) + \gamma\sum_{s'} P(s'\mid s,a) V^\pi(s')$, the product rule gives

$$
\nabla V^\pi(s) = \sum_a \Big[ \nabla \pi_\theta(a\mid s)\, Q^\pi(s,a)
  + \pi_\theta(a\mid s)\, \nabla Q^\pi(s,a) \Big]. \tag{6}
$$

Inside $Q^\pi$, neither $r(s,a)$ nor $P$ depends on $\theta$, so
$\nabla Q^\pi(s,a) = \gamma \sum_{s'} P(s'\mid s,a)\nabla V^\pi(s')$. Substituting into (6),

$$
\nabla V^\pi(s) = \underbrace{\sum_a \nabla \pi_\theta(a\mid s) Q^\pi(s,a)}_{=:\;\phi(s)}
  + \gamma \sum_{s'} \Big(\sum_a \pi_\theta(a\mid s) P(s'\mid s,a)\Big) \nabla V^\pi(s')
  = \phi(s) + \gamma \sum_{s'} P^\pi_{ss'}\, \nabla V^\pi(s'). \tag{7}
$$

Equation (7) is a **linear fixed-point equation** in $\nabla V^\pi$. Since $\lvert\gamma\rvert < 1$
and $P^\pi$ is a stochastic matrix, $(I - \gamma P^\pi)$ is invertible and the Neumann series gives

$$
\nabla V^\pi = \sum_{t\ge0} \gamma^t (P^\pi)^t \phi
  \quad\Longrightarrow\quad
  \nabla J(\theta) = \rho_0^\top \nabla V^\pi = \sum_s \Big(\sum_{t\ge0}\gamma^t \Pr(s_t = s)\Big)\phi(s)
  = \sum_s \rho^\pi(s)\,\phi(s),
$$

which is the first equality of (1). The second uses $\nabla \pi = \pi \nabla\log\pi$ (valid only
under A3) and $d^\pi = (1-\gamma)\rho^\pi$.

**Why this is surprising.** $\Pr(s_t = s)$ does depend on $\theta$ while (7) is being unrolled. Yet
the gradient of that dependence is **absorbed into the series**, so the final expression contains
$\rho^\pi$ only undifferentiated. That is what makes (1) estimable from samples without knowing
the transition model $P$.

**Where the assumptions break.** If A3 fails and $\pi_\theta(a\mid s) = 0$ for some $(s,a)$, then
$\nabla\log\pi$ is undefined and that action's $Q$ contributes nothing at all to the gradient — a
saturated softmax policy has an exponentially small gradient, so **exploration stops**. Also, the
expectation in (1) is over $d^\pi$, so the $Q$ values of states that $d^\pi$ never reaches cannot
change the gradient however large they are. This dependence on the data distribution becomes the
central problem again in offline RL and imitation learning (`c8-offline-rl`,
`c8-imitation-learning`).

### R2 — baselines, causality, the optimal baseline

**Unbiasedness.** Under A3, differentiating $\sum_a \pi_\theta(a\mid s) = 1$ with respect to
$\theta$ gives

$$
\mathbb{E}_{a\sim\pi}\big[g_\theta(s,a)\big] = \sum_a \pi_\theta(a\mid s)\nabla\log\pi_\theta(a\mid s)
  = \sum_a \nabla \pi_\theta(a\mid s) = \nabla 1 = 0. \tag{8}
$$

Since $b(s)$ does not depend on $a$, $\mathbb{E}_a[g_\theta b(s)] = b(s)\,\mathbb{E}_a[g_\theta] = 0$.
So replacing $Q^\pi$ by $Q^\pi - b$ in (1) leaves the expectation unchanged. If $b$ depends on
$a$, (8) is unavailable and a **bias appears** (problem P5 computes it exactly).

**Causality.** In the trajectory estimator $\hat{g} = \sum_t \gamma^t g_\theta(s_t,a_t)\, G$, taking
$G = G_0$ (the total return) includes rewards $r_0,\dots,r_{t-1}$ that are independent of $a_t$, so
those terms have expectation zero by (8). Replacing $G_0$ with the reward-to-go
$G_t = \sum_{k\ge t}\gamma^{k-t} r_k$ is therefore still unbiased, and removing terms with zero
mean **reduces variance only**. The reproduction task measures this effect at roughly a factor of
three.

**The optimal baseline.** For a scalar $\theta$ at a fixed $s$, the variance of
$\hat{g}(a) = g_\theta(s,a)\,(Q^\pi(s,a) - b)$ is quadratic in $b$. The mean does not depend on
$b$, so minimizing $\mathbb{E}[\hat{g}^2]$ suffices:

$$
\frac{\partial}{\partial b}\, \mathbb{E}_a\Big[ g_\theta^2 (Q^\pi - b)^2 \Big]
  = -2\,\mathbb{E}_a\big[g_\theta^2 (Q^\pi - b)\big] = 0
  \;\Longrightarrow\; b^\star = \frac{\mathbb{E}_a[g_\theta^2 Q^\pi]}{\mathbb{E}_a[g_\theta^2]},
$$

which is (2). For a vector $\theta$, replacing $g_\theta^2$ with $\lVert g_\theta \rVert^2$ gives
the optimum under the trace criterion. So **$b^\star$ is the average of $Q$ weighted by
$\lVert g_\theta\rVert^2$**, and it does not coincide with the unweighted
$V^\pi = \mathbb{E}_a[Q^\pi]$.

**Where the assumptions break.** The habit of using $V^\pi$ as the baseline rests on the intuition
that "a zero-mean advantage has small variance", but when the weighting is asymmetric
$b = V^\pi$ can be **worse than $b = 0$** (problem P3: variance $0.0064 \to 0.0576$, a factor of
nine). And estimating $b$ from data correlates it with $a$, so strict unbiasedness is lost — fitting
the baseline on the same batch used for the gradient introduces a small bias.

### R3 — the performance difference lemma

Expand the discounted sum of $A^\pi$ along trajectories of $\pi'$. With
$A^\pi(s,a) = r(s,a) + \gamma \mathbb{E}_{s'}[V^\pi(s')] - V^\pi(s)$,

$$
\mathbb{E}_{\pi'}\Big[\sum_{t\ge0}\gamma^t A^\pi(s_t,a_t)\Big]
 = \mathbb{E}_{\pi'}\Big[\sum_{t\ge0}\gamma^t \big(r_t + \gamma V^\pi(s_{t+1}) - V^\pi(s_t)\big)\Big].
$$

The $V^\pi$ terms **telescope**:
$\sum_t \gamma^t(\gamma V^\pi(s_{t+1}) - V^\pi(s_t)) = -V^\pi(s_0)$ (the tail vanishes by the
boundedness A1). Hence

$$
\mathbb{E}_{\pi'}\Big[\sum_{t\ge0}\gamma^t A^\pi(s_t,a_t)\Big] = J(\pi') - J(\pi),
$$

and rewriting the left side with the occupancy distribution as
$\frac{1}{1-\gamma}\mathbb{E}_{s\sim d^{\pi'}, a\sim\pi'}[A^\pi]$ gives (3).

**How to read it**: (3) says that measuring $\pi$'s advantage under $\pi'$'s distribution recovers
the performance difference exactly. The problem is that $d^{\pi'}$ is unknown, and policy
gradients, TRPO and offline RL are three different answers to how that single term is approximated.

**Where the assumptions break.** The telescoping uses $\gamma < 1$ and boundedness of $V^\pi$. With
$\gamma = 1$ and no absorbing state both sides diverge. And (3) presumes the **exact** $A^\pi$;
substituting an estimate $\hat{A}$ lets the error be amplified by $1/(1-\gamma)$.

### R4 — the surrogate objective and the trust region

$L_\pi(\pi')$ is (3) with $d^{\pi'}$ replaced by $d^\pi$. Check two properties.

**First-order agreement.** At $\pi' = \pi$ we have $\mathbb{E}_{a\sim\pi}[A^\pi(s,a)] = 0$, so
$L_\pi(\pi) = 0$, and differentiating in $\theta$ gives
$\nabla_{\theta'} L_{\pi_\theta}(\pi_{\theta'})\big|_{\theta'=\theta} =
\frac{1}{1-\gamma}\mathbb{E}_{d^\pi,\pi}[g_\theta A^\pi] = \nabla_\theta J(\theta)$ — exactly (1)
with the baseline $V^\pi$. So $L$ is a **first-order model** of $J$.

**The error term.** The difference between $d^{\pi'}$ and $d^\pi$ is governed by the first time the
two policies disagree along a trajectory. Building a coupling with the total variation
$\alpha = \max_s D_{\mathrm{TV}}(\pi\Vert\pi')$, the probability of no disagreement up to time $t$
is at least $(1-\alpha)^t$, and each disagreement contributes at most $2\epsilon$ to the advantage,
which bounds the error by $O(\epsilon\gamma\alpha^2/(1-\gamma)^2)$. Converting $\alpha^2$ into KL
with Pinsker's inequality $D_{\mathrm{TV}}^2 \le \tfrac12 D_{\mathrm{KL}}$ produces the constant
$4\epsilon\gamma/(1-\gamma)^2$ of (4) (omitted: the details of the coupling are lemmas 1–3 of TRPO
appendix A).

**Where the assumptions break.** In (4), $\epsilon$ is a **maximum** advantage and
$D^{\max}_{\mathrm{KL}}$ a **maximum** KL. Both are decided by the worst state, so with a large
state space the penalty explodes and the admissible step goes to zero. Practical TRPO replaces
$D^{\max}_{\mathrm{KL}}$ with $\bar{D}_{\mathrm{KL}} = \mathbb{E}_{s\sim d^\pi}[D_{\mathrm{KL}}]$,
and **that substitution destroys the monotone improvement guarantee.** Practical TRPO is therefore
not the algorithm of the theorem but an algorithm inspired by it.

### R5 — the natural gradient

Maximize the first-order objective inside a KL trust region of radius $\delta$:

$$
\max_{\Delta\theta}\; \nabla J^\top \Delta\theta
  \quad\text{s.t.}\quad \bar{D}_{\mathrm{KL}}(\theta \Vert \theta + \Delta\theta) \le \delta .
$$

The KL divergence has zero value and zero first derivative at $\Delta\theta = 0$, and its Hessian
is the Fisher matrix:

$$
\bar{D}_{\mathrm{KL}}(\theta\Vert\theta+\Delta\theta)
  = \tfrac12 \Delta\theta^\top F(\theta)\,\Delta\theta + O(\lVert\Delta\theta\rVert^3). \tag{9}
$$

Substituting (9) into the constraint and writing the Lagrange condition gives
$\nabla J = \lambda F \Delta\theta$, i.e. $\Delta\theta \propto F^{-1}\nabla J$; filling the
constraint with equality fixes the coefficient in (5).

**Reparameterization invariance.** Under a change of coordinates $\theta = h(\psi)$ we have
$\nabla_\psi J = H^\top \nabla_\theta J$ and $F_\psi = H^\top F_\theta H$ with
$H = \partial h/\partial\psi$, so $F_\psi^{-1}\nabla_\psi J = H^{-1} F_\theta^{-1}\nabla_\theta J$
— **the same change of policy**. The ordinary gradient lacks this property, so its step depends on
how the network is parameterized.

**Where the assumptions break.** (9) is a second-order expansion and fails for large $\delta$. And
an $F$ estimated from samples is badly conditioned, making $F^{-1}$ unstable — practice solves
$F^{-1}\nabla J$ matrix-free with conjugate gradients and then **tests** the actual KL and surrogate
improvement with a line search. That line search is the only device holding the guarantee together
in a TRPO implementation.

## Proof sketch

### R1 — the policy gradient theorem [D3]

**Hypotheses** H1: A1 (bounded reward) and A2 ($\gamma<1$). H2: $\pi_\theta(a\mid s)$ is
differentiable in $\theta$. H3: A3 ($\pi_\theta > 0$), or only the form that uses $\nabla\pi$
directly.
**Conclusion** C: (1).

**Strategy**: fixed-point expansion of the value recursion (Neumann series); exchange of
differentiation and infinite summation by bounded convergence.

1. Expand $V^\pi(s) = \sum_a \pi Q^\pi$ with the product rule → (6). Uses: H2.
2. Use the fact that $r$ and $P$ do not depend on $\theta$ to turn $\nabla Q^\pi$ back into
   $\nabla V^\pi$ → (7).
3. Read (7) as $(I - \gamma P^\pi)\nabla V^\pi = \phi$ and solve with the Neumann series. Uses: H1
   (absolute convergence of the series and termwise differentiation).
4. Weight by $\rho_0$ to get $\rho^\pi$, and use $\nabla\pi = \pi\nabla\log\pi$ from H3 → C.

**Delete one hypothesis**: dropping $\gamma<1$ from H1 makes the Neumann series in step 3 divergent
and the expansion impossible (average-reward policy gradients differentiate the stationary
distribution separately). Dropping H3 makes the second (score-function) form of (1) unusable,
leaving only the first — which is why the deterministic policy gradient takes the other route
through $\nabla_a Q$.

Omitted: the exchange conditions for continuous states and actions follow from dominated
convergence; see theorems 1–2 of Sutton et al. 2000.

### R4 — the monotone improvement bound [D3]

**Hypotheses** H1–H2 (as above). H4: $\epsilon = \max_{s,a}\lvert A^\pi(s,a)\rvert < \infty$.
**Conclusion** C: (4), and that $L_\pi(\pi') > C D^{\max}_{\mathrm{KL}}$ implies $J(\pi') > J(\pi)$.

**Strategy**: performance difference lemma (an exact identity) → bound the error of substituting
the occupancy distribution with a coupling → replace TV with KL via Pinsker.

1. Establish (3) (telescoping). Uses: H1.
2. Bound the error of replacing $d^{\pi'}$ with $d^\pi$ using the probability
   $\ge (1-\alpha)^t$ that the two policies agree up to time $t$. Uses: H4, the coupling.
3. One disagreement contributes at most $2\epsilon$ to the advantage and the discounted sum is of
   order $\gamma/(1-\gamma)^2$, so the error is $\le 4\epsilon\gamma\alpha^2/(1-\gamma)^2$.
4. Convert with Pinsker, $\alpha^2 \le \tfrac12 D^{\max}_{\mathrm{KL}}$ → C.

**Delete one hypothesis**: dropping H4 (unbounded advantage) makes the constant infinite and the
bound vacuous. And replacing $D^{\max}$ in step 2 with a mean KL leaves the coupling unable to
cover the worst state, so **the inequality no longer holds** — this is exactly the gap between
practical TRPO and the theorem.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Re-derive R1 for a finite horizon $T$ without discounting
($\gamma=1$). State what takes the place of $\rho^\pi$ and why it diverges as $T \to \infty$.
*Solution sketch*: the expansion of (7) terminates after $T$ steps, leaving
$\sum_{t=0}^{T-1}(P^\pi)^t$. This grows proportionally to $T$ and has no convergence factor from
the Neumann series. $\gamma<1$ is the device that keeps the sum bounded, so discounting is both a
"modelling assumption" and a "regularizer of the estimator" (this is the bias Baxter & Bartlett
2001 analyze).

**P2 (proof, ★★★, R3·R4)** Prove the performance difference lemma (3) directly and use it to show
$\nabla_{\theta'}L_{\pi_\theta}(\pi_{\theta'})|_{\theta'=\theta} = \nabla_\theta J(\theta)$. Then
construct a *wrong* argument for step 2 of (4) that yields only $\alpha$ instead of $\alpha^2$, and
say exactly where it fails.
*Strategy and key inequality*: (3) is a telescoping expansion; the first-order agreement is
$\mathbb{E}_\pi[A^\pi]=0$. The wrong argument usually assumes that disagreement happens only once
and counts $\alpha$ a single time — the **distribution difference after** the disagreement
multiplies by $\alpha$ again. The expansion is withheld.

**P3 (numerical, ★, R2)** A single-state, two-action problem ($\gamma=0$): $\pi(a_1) =
\sigma(\theta) = 0.8$, $r(a_1) = 1$, $r(a_2) = 0$. For the scalar estimator
$\hat{g}(a) = \nabla\log\pi(a)\,(r(a) - b)$ compute (i) $\mathbb{E}[\hat{g}]$, (ii) the variance for
$b=0$, $b = V^\pi$ and $b = b^\star$, and (iii) $b^\star$.
*Answer*: $\nabla\log\pi(a_1) = 1-p = 0.2$ and $\nabla\log\pi(a_2) = -p = -0.8$;
$\mathbb{E}[\hat{g}] = p(1-p) = 0.16$ for every $b$. The variances are $0.0064$ for $b=0$,
$0.0576$ for $b=V^\pi=0.8$, and **exactly $0$** for $b^\star = 1-p = 0.2$. Tolerance $10^{-12}$.
So the $V^\pi$ baseline is **nine times worse** than $b=0$, and the optimal baseline is not the
mean reward.
Check: at $b=0.2$ verify directly that $\hat{g}(a_1) = \hat{g}(a_2) = 0.16$ — the estimator is
constant, hence zero variance.

**P4 (implementation, ★★, R1·R2)** On a small random MDP (6 states, 3 actions, softmax policy),
compute the analytic gradient of (1) exactly with a linear solve and compare it with central
differences. Then check that the sample means of three Monte Carlo estimators (total return /
reward-to-go / reward-to-go minus a linear baseline) all converge to the analytic gradient.
*Rubric*: ⓐ the relative error between analytic gradient and central difference is at most
$10^{-6}$; ⓑ $\rho^\pi$ was computed as $(I-\gamma (P^\pi)^\top)^{-1}\rho_0$ (a linear solve, not
sampling); ⓒ changing the baseline leaves the analytic gradient unchanged to $10^{-12}$; ⓓ the
sample variances of the three estimators are reported alongside; ⓔ the choice of $h$ for the
central difference is justified (truncation versus rounding error).

**P5 (counterexample, ★★, R2)** Show, in the setting of P3, that an action-dependent baseline
$b(s,a)$ breaks unbiasedness, with the **exact value of the bias**. Then explain why the
observation "using the advantage $A^\pi(s,a)$ as a baseline makes the estimator zero" is not a
contradiction.
*Property checklist*: ⓐ with $b(a) = r(a)$ the estimator is $\hat{g} \equiv 0$, so
$\mathbb{E}[\hat{g}] = 0$ and the bias is $-0.16$; ⓑ identify exactly where (8) becomes
unusable (as a function of $a$, $b$ cannot be pulled out of the expectation); ⓒ distinguish
subtracting $Q$ — which changes the objective rather than acting as a baseline; ⓓ state in one line
how unbiasedness can be recovered with an action-dependent baseline (a correction term is needed).

**P6 (paper, ★★, R4·R6)** Read TRPO (§2–3 and appendix A) and PPO (§3) and write, in at most three
sentences each: (i) the difference between what the TRPO theorem guarantees and what the TRPO
implementation does; (ii) why PPO's clipping fails to constrain the KL divergence; (iii) the share
of PPO's gains attributable to clipping in the ablations of Engstrom et al. 2020.
*Grading rubric*: (i) passes if it names the $D^{\max}_{\mathrm{KL}} \to \bar{D}_{\mathrm{KL}}$
substitution and the line search. (ii) the gradient becomes zero once the ratio leaves the window,
but **the movement that already happened** is not constrained, and a ratio constraint is a
different quantity from a per-state KL. (iii) the report that observation and advantage
normalization and learning-rate annealing contribute as much as or more than clipping. Writing only
"PPO is simpler" fails.

**P7 (derivation, ★★, R5)** Show that $F(\theta) = \nabla^2_{\Delta\theta} \bar{D}_{\mathrm{KL}}
(\theta\Vert\theta+\Delta\theta)\big|_{\Delta\theta=0}$ and verify that the natural gradient step
is invariant under $\theta = h(\psi)$.
*Solution sketch*: in the second-order Taylor expansion of the log, the first-order term vanishes
by (8), and in the second-order term use the identity
$\mathbb{E}[\nabla\log\pi \nabla\log\pi^\top] = -\mathbb{E}[\nabla^2\log\pi]$. For invariance,
substitute $F_\psi = H^\top F_\theta H$ and $\nabla_\psi = H^\top\nabla_\theta$; only $H^{-1}$
survives.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions
(`lesson-standard.md` §5). Read with three passes and attack questions 4, 5, 6 and 7 in the third.

1. **Sutton, McAllester, Singh & Mansour, "Policy gradient methods for reinforcement learning with
   function approximation" (2000, NIPS 12)** — role: `seminal`.
   <https://papers.nips.cc/paper_files/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html>
   Why read it: it is the origin of R1, and its compatible-function-approximation condition leads
   straight to the natural gradient (R5).
   Extra questions: ⓐ which term of (1) does the authors' "compatible features" condition change?
   ⓑ what does the convergence claim of theorem 2 guarantee, and what does it not (local? global?)
2. **Schulman, Levine, Abbeel, Jordan & Moritz, "Trust region policy optimization" (2015, ICML)** —
   role: `seminal`. <https://arxiv.org/abs/1502.05477> (§2–3, appendix A)
   Why read it: R3 and R4 are lemmas of this paper. The point is to see the gap between theorem and
   implementation first-hand.
   Extra questions: ⓐ point, by equation number, to where $\alpha^2$ arises in the coupling argument
   of appendix A. ⓑ how does the paper justify what is given up when $D^{\max}_{\mathrm{KL}}$ is
   replaced by a mean?
3. **Schulman, Wolski, Dhariwal, Radford & Klimov, "Proximal policy optimization algorithms" (2017,
   arXiv)** — role: `standard`. <https://arxiv.org/abs/1707.06347> (focus on §3)
   Why read it: it is the de facto standard algorithm, and **a case of becoming standard without a
   theoretical guarantee**.
   Extra questions: ⓐ draw the region of $\rho_t$ in which the clipped objective zeroes the
   gradient. ⓑ how many seeds does the paper use and does it report confidence intervals
   (question 6)?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation? (4) what is guaranteed and **what is not**?
(5) independent and dependent variables, and the baselines — were they tuned fairly? (6) does the
metric match the claim, and are variance and seeds reported? (7) what information needed for
reproduction is missing? (8) if the result were wrong, which assumption would you doubt first?
(9) compute and memory cost, and real-time feasibility? (10) what would you change to go beyond
this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: under **one minute** on a laptop CPU (measured:
about 10 s for the 15 training runs, about 2 s for the variance measurement), under 200 MB,
numpy only. No simulator — the CartPole dynamics are written out in twenty lines.

The environment has the dynamics and termination of CartPole-v1: $m_c = 1.0$, $m_p = 0.1$,
half-length $l = 0.5$, $F = \pm 10$, $\Delta t = 0.02$ (Euler), termination at
$\lvert x\rvert > 2.4$ or $\lvert\vartheta\rvert > 12^\circ$, at most 500 steps, reward $1$ per
step. The policy is $\pi_\theta(a\mid s) = \mathrm{softmax}(\theta\,\phi(s))$ with
$\phi(s) = (s, 1) \in \mathbb{R}^5$ and $\theta \in \mathbb{R}^{2\times5}$, $\theta_0 = 0$.
Discount $\gamma = 0.99$, GAE $\lambda = 0.95$.

Implement **three estimators**: ⓐ total-return REINFORCE ($G_0$), ⓑ reward-to-go REINFORCE
($G_t$), ⓒ reward-to-go minus a linear value baseline. And **three algorithms**: REINFORCE (no
baseline), REINFORCE + baseline, PPO (clip $0.2$, 20 epochs per batch, advantage normalization).

**Acceptance criteria** — all four must hold.

1. **Unbiasedness (analytic check)**: on the small MDP of problem P4, the relative error between
   the analytic gradient and the central difference is at most $10^{-6}$, and changing the baseline
   from $0$ to $V^\pi$ to a constant changes the analytic gradient by at most $10^{-12}$.
2. **Variance ordering (CartPole)**: at a fixed $\theta$ (the result of training the baseline
   version for 10,000 steps), the covariance trace $\mathrm{tr}\,\widehat{\mathrm{Cov}}$ of 400
   per-episode gradient estimates satisfies, **for all five seeds**,

$$
\frac{\mathrm{tr}_{\text{total return}}}{\mathrm{tr}_{\text{reward-to-go}}} \ge 2.5, \qquad
  \frac{\mathrm{tr}_{\text{reward-to-go}}}{\mathrm{tr}_{\text{baseline}}} \ge 1.4, \qquad
  \frac{\mathrm{tr}_{\text{total return}}}{\mathrm{tr}_{\text{baseline}}} \ge 4.0 . \tag{10}
$$

   (Measured: $2.93$–$3.63$, $1.65$–$1.99$ and $5.49$–$6.00$ respectively.)
3. **Direction agreement**: the cosine similarity between the sample mean of the reward-to-go
   estimator and that of the baseline estimator is $\ge 0.85$ for every seed (measured
   $0.874$–$0.987$). The total-return estimator has so much variance that 400 episodes do not
   stabilize its direction ($0.58$–$0.94$) — **that is itself the content of criterion 2**, so no
   direction condition is imposed on it.
4. **Sample efficiency (mean of five seeds)**: with a budget of 60,000 environment steps and
   batches of 2,000 steps,
   ⓐ PPO reaches a batch-mean return of $200$ in **all five** seeds, and the median number of
   steps to reach it is at most $60\%$ of that of REINFORCE + baseline (measured 26,902 vs 49,152,
   i.e. $55\%$);
   ⓑ REINFORCE + baseline reaches $200$ in $\ge 4$ of 5 seeds, and its five-seed mean of the final
   batch-mean return exceeds that of REINFORCE without a baseline (measured $165.6$ vs $87.7$).

**Baselines**: ⓐ REINFORCE without a baseline — the lower bound of the three algorithms;
ⓑ the analytic gradient of criterion 1 — ground truth for the estimator implementation;
ⓒ optional: in the same code, turn PPO's clipping off ($\epsilon_{\text{clip}} = \infty$) and run
20 epochs to see whether performance collapses. If it does, the reading of R6 — that clipping is
the device that makes multi-epoch reuse possible — is confirmed in code.

**Reference output** (numpy 2.x, seeds 0–4): REINFORCE reaches 200 in 4/5 seeds (median 53,116
steps, final mean $87.7$); REINFORCE + baseline in 5/5 (median 49,152, final mean $165.6$); PPO in
5/5 (median 26,902, final mean $282.0$). These numbers depend on the random stream, so **judge by
the four criteria only**.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The first ratio of criterion 2 is close to 1 | the total-return estimator also used $G_t$ (causality removed twice) | print the coefficient arrays of both estimators and see whether $G_0$ is the same value at every $t$ |
| Baseline invariance in criterion 1 fails | the baseline was fitted on the **same batch** used for the gradient | fit the baseline on a separate (or the previous) batch and re-run |
| PPO does not learn (stuck near a return of $45$) | the learning rate is too small to fill the trust region even in 20 epochs | check that advantages are normalized and raise the learning rate by factors of ten (it worked at $1.0$ in the measurement) |
| PPO collapses early | multiple epochs were run without clipping | histogram the ratios $\rho_t$ — a tail beyond $10$ means a blow-up |
| All methods have abnormally large variance | the $\gamma^t$ weight was omitted | check the line that multiplies by $\gamma^t$ in the estimator (without it, this is not the estimator of (1)) |
| Conclusions flip between seeds | the comparison used one or two seeds | report all five — this is the failure mode Henderson et al. 2017 documented |

## Open problems

- **(open problem) The validity of policy gradients under contact and nonsmooth dynamics** — the
  derivation of (1) never differentiates $P$, but in systems with contact the reward and the value
  are **discontinuous** in the state, and a simulator's smooth approximation (soft contact) returns
  a gradient of a different objective. There is no guarantee that a gradient obtained from the
  smoothed model is a descent direction for the original one. Current approaches: trajectory
  optimization treating contact as complementarity constraints
  ([Posa et al. 2014](https://doi.org/10.1177/0278364913506757)), convex-relaxed contact models
  ([Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751)), contact-implicit MPC
  ([Aydinoglu et al. 2024](https://arxiv.org/abs/2304.11259)). What is missing: a quantitative
  criterion linking the smoothing parameter to gradient quality.
- **(open problem) The gap between trust-region guarantees and real implementations** — the constant
  in (4) is effectively infinite in practice, so using the theorem literally gives a zero step, and
  the algorithms actually used (mean-KL TRPO, PPO) carry no monotone improvement guarantee. Whether
  the performance gap comes from the algorithm or the implementation is itself contested. Current
  approaches: ablations ([Engstrom et al. 2020](https://arxiv.org/abs/2005.12729)), evaluation
  methodology ([Henderson et al. 2017](https://arxiv.org/abs/1709.06560),
  [Agarwal et al. 2021](https://arxiv.org/abs/2108.13264)). What is missing: an improvement bound
  that is tight at practical step sizes.
- **(open problem) Sample complexity of policy gradients and the distribution-mismatch term** —
  global convergence of softmax policies has been proven under exact gradients and sufficient
  exploration, but the distribution-mismatch factor
  $\lVert d^{\pi^\*}/d^{\pi_0}\rVert_\infty$ that appears in the rate can be exponentially large in
  robot problems. Current approaches:
  [Agarwal, Kakade, Lee & Mahajan 2019](https://arxiv.org/abs/1908.00261),
  [Mei et al. 2020](https://arxiv.org/abs/2005.06392). What is missing: structural assumptions that
  actually bound that factor at robot-scale state spaces.
- **(open problem) A principled choice of the bias-variance knobs** — GAE's $\lambda$, how the
  baseline is fitted, and reward scaling all trade bias against variance, yet the choices are
  empirical. Current approaches: [GAE](https://arxiv.org/abs/1506.02438) and the discounting-bias
  analysis of [Baxter & Bartlett 2001](https://doi.org/10.1613/jair.806). What is missing: a rule
  for choosing $\lambda$ and $\gamma$ given a target performance.

## Concept check

Run `rc quiz c8-policy-gradient`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: what is surprising about the policy gradient theorem; whether the
variance-minimizing baseline is always $V^\pi$; whose occupancy distribution averages the advantage
in the performance difference lemma; what is lost when practical TRPO replaces the maximum KL with
a mean KL; and whether PPO's clipping constrains the KL divergence.

## How to study this stage

1. **Derive (1) from a blank page (90 min)** — write (6) → (7) → the Neumann series by hand. The
   step people get stuck on is almost always turning $\nabla Q^\pi$ back into $\nabla V^\pi$. Read
   S&B ch.13.2 and theorem 1 of Sutton et al. 2000 side by side as **the same result in different
   notation**.
2. **Meet the baseline as a number (45 min)** — solve problem P3 first and compute by hand the
   instance in which the $V^\pi$ baseline is worse. The goal is to turn "advantages reduce variance"
   from an article of faith into a conditional fact. Then confirm the bias of an action-dependent
   baseline with P5.
3. **Performance difference lemma first, trust region second (90 min)** — the telescoping expansion
   of (3) is short, and with it in hand TRPO appendix A becomes readable. Grasp the structure that
   swapping $d^{\pi'}$ for $d^\pi$ is the *only* approximation before following the coupling and
   Pinsker.
4. **Confirm the variance ordering in code (105 min)** — pass criterion 1 (analytic unbiasedness)
   before moving to criterion 2 (variance ordering). In the other order you cannot tell high
   variance from a broken implementation. Do PPO last, together with the version that has clipping
   turned off.
5. **Read the three papers theory → implementation (150 min)** — Sutton et al. (theorem) → TRPO
   (guarantee) → PPO (practice). Write the one-page note for each; this is **not** optional. In the
   TRPO note, put "what the theorem guarantees" and "what the code does" in two parallel columns.
6. **End at what cannot be done (60 min)** — pick the contact-dynamics open problem and write a
   paragraph on which assumption of (1) wobbles first if contact (a wall the cart can hit) is added
   to the CartPole of the reproduction task.

**Passing bar**: you can derive (1) and (3) from a blank page, say where the constant of (4) comes
from and why it is vacuous in practice, give a numerical instance showing the optimal baseline is
not $V^\pi$, and you hold code satisfying the four acceptance criteria plus notes on the three
papers.
