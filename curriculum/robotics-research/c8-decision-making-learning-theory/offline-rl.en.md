---
id: c8-offline-rl
lang: en
title: Offline RL and distribution shift
summary: >-
  Organize the extrapolation error that arises when improving a policy from offline data alone,
  prove why a conservative value iteration with an uncertainty penalty gives a lower bound on the
  true value, and prove why the suboptimality is controlled by uncertainty measured **only on the
  optimal policy's distribution**. Then show that behaviour regularization and value conservatism
  are different things, and compute exactly how the variance of importance-weighted offline
  evaluation grows exponentially in the horizon.
objectives:
  - Prove that the fixed point of a Bellman operator with an uncertainty penalty is a lower bound on $Q^\*$.
  - Derive the suboptimality bound $2(1-\gamma)^{-1}\mathbb{E}_{d^{\pi^\*}}[\Gamma]$ with no missing steps.
  - Explain why single-policy concentrability is a weaker assumption than all-policy concentrability.
  - Show by example that behaviour regularization and value conservatism admit different policy sets.
  - Derive that the variance of the importance-weighted estimator grows as $m^T$ and compute the effective sample size.
  - Find experimentally the point at which BC and conservative offline RL swap places as data quality changes.
tags: [offline-rl, pessimism, distribution-shift, cql, off-policy-evaluation, research]
---

# Offline RL and distribution shift

## Setup and notation

The operator and weighted-norm notation of `c8-value-based-rl` and the distribution-shift
viewpoint of `c8-imitation-learning` carry over. Additional **recommended** background:

- Probability: Hoeffding's inequality, effective sample size, unbiasedness and variance of
  importance weighting.
- Linear algebra: non-negativity (all entries $\ge 0$) and monotonicity of
  $(I-\gamma P^\pi)^{-1}$.
- Convex optimization: the equivalence of constrained and penalized forms through duality
  (`r0-convex-optimization`).

Added notation:

| Symbol | Meaning |
|---|---|
| $\mathcal{D}$ | the offline dataset; $n(s,a)$ is the visit count of $(s,a)$ |
| $\pi_b$ | the behaviour policy that generated $\mathcal{D}$ |
| $\hat{T}$ | the empirical Bellman operator, $(\hat{T}Q)(s,a) = \hat{r}(s,a) + \gamma\sum_{s'}\hat{P}(s'\mid s,a)\max_{a'}Q(s',a')$ |
| $\Gamma(s,a)$ | uncertainty penalty; it must satisfy $\lvert(\hat{T}Q)(s,a) - (TQ)(s,a)\rvert \le \Gamma(s,a)$ |
| $\tilde{T}$ | the pessimistic operator, $\tilde{T}Q = \hat{T}Q - \Gamma$ |
| $\tilde{Q}, \tilde{V}, \tilde{\pi}$ | the fixed point of $\tilde{T}$ and its greedy policy |
| $d^\pi$ | normalized discounted occupancy, $(1-\gamma)\sum_t\gamma^t\Pr(s_t,a_t)$ |
| $C^\star$ | single-policy concentrability, $C^\star = \max_{s,a} d^{\pi^\star}(s,a)/d^{\pi_b}(s,a)$ |
| $\varrho_{0:T-1}$ | trajectory importance ratio, $\prod_{t<T}\pi(a_t\mid s_t)/\pi_b(a_t\mid s_t)$ |
| $V_{\max}$ | $R_{\max}/(1-\gamma)$ |

**The core difficulty in one line.** Online RL can "go and find out" about what it does not know;
offline RL cannot. Yet the $\max$ of `c8-value-based-rl` keeps **actions with no data** as
candidates, and the $\hat{Q}$ of such an action can be arbitrarily wrong — optimization then
**actively seeks out** that error. This is extrapolation error, and it has the same structure as
the model exploitation of `c8-model-based-world-models`.

## Key results

The bracket gives the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (pessimism gives a lower bound) [D3]** — if $\Gamma$ is a valid uncertainty bound, the fixed
  point of $\tilde{T}$ satisfies
  $$
  \tilde{Q} \le Q^\* \quad\text{(entrywise)}, \qquad \tilde{V} \le V^\* \tag{1}
  $$
  So a conservative estimate **never overestimates** — which is why a report that "$\tilde{V}$ is
  high" can be trusted (the converse is not).
- **R2 (single-policy suboptimality bound) [D3]** — under the same conditions, the suboptimality of
  $\tilde{\pi}$ is bounded by
  $$
  V^\*(s_0) - V^{\tilde{\pi}}(s_0) \;\le\; \frac{2}{1-\gamma}\,
    \mathbb{E}_{(s,a)\sim d^{\pi^\*}}\big[\Gamma(s,a)\big] \tag{2}
  $$
  The point is that **the expectation is taken only under $d^{\pi^\star}$** — the data need only
  cover where the optimal policy goes, not the whole space. With
  $\Gamma \propto V_{\max}\sqrt{\log(\cdot)/n}$, (2) becomes
  $\tilde{O}\big(V_{\max}\sqrt{C^\star/n}/(1-\gamma)\big)$.
- **R3 (no guarantee without conservatism) [D2]** — remove $\Gamma$ and (1) fails: a single
  $(s,a)$ with no data can inflate $\hat{V}$ up to $V_{\max}$. The narrower the data distribution,
  the larger the effect, so **on narrow data conservative methods win and on broad data
  non-conservative ones do** — the reproduction task measures this reversal.
- **R4 (behaviour regularization $\neq$ value conservatism) [D2]** — behaviour regularization (a
  support constraint) keeps $\pi$ inside the support of $\pi_b$, so **an optimal action $\pi_b$
  never took can never be chosen**. Value conservatism (the CQL family) can still choose such an
  action if its $Q$ remains highest after the penalty. The two admit different policy sets, and the
  former is capped near $J(\pi_b)$.
- **R5 (variance of OPE: the curse of horizon) [D2]** — the trajectory importance-weighted
  estimator is unbiased, but
  $$
  \mathbb{E}\big[\varrho_{0:T-1}^2\big] = \prod_{t<T}
    \Big(\textstyle\sum_a \pi(a\mid s_t)^2/\pi_b(a\mid s_t)\Big), \tag{3}
  $$
  which is **exactly $m^T$** when $\pi$ is deterministic and $\pi_b$ is uniform over $m$ actions.
  The effective sample size is $n/m^T$, so at $m=4$ and $T=8$ two million trajectories are
  worth **31** effective samples.

## Derivation

### R1 — why conservatism gives a lower bound

**Assumption.** For every $Q$ (or at least every $Q$ appearing in the iteration),

$$
\big\lvert (\hat{T}Q)(s,a) - (TQ)(s,a) \big\rvert \;\le\; \Gamma(s,a) \qquad \forall (s,a). \tag{4}
$$

For an $(s,a)$ with no data, setting $\Gamma = V_{\max}$ makes (4) automatic (no estimate can be
off by more than $V_{\max}$).

**Step 1: $\tilde{T}$ does not dominate $T$.** From (4), $\hat{T}Q \le TQ + \Gamma$, so

$$
\tilde{T}Q = \hat{T}Q - \Gamma \;\le\; TQ \qquad \forall Q. \tag{5}
$$

**Step 2: monotonicity and contraction.** $\tilde{T}$ has the same structure as $T$ (a $\max$ with
non-negative coefficients), so it is monotone and a $\gamma$-contraction in the sup norm (the same
computation as step 2 of R1 in `c8-mdp-pomdp-bellman`). Hence a unique fixed point $\tilde{Q}$
exists.

**Step 3: the ladder argument.** Start from $Q^\*$ and iterate $\tilde{T}$. By (5),
$\tilde{T}Q^\* \le TQ^\* = Q^\*$, and monotonicity gives
$\tilde{T}^2 Q^\* \le \tilde{T}Q^\* \le Q^\*$ and, by induction, $\tilde{T}^k Q^\* \le Q^\*$. As
$k\to\infty$ the left side converges to $\tilde{Q}$, so

$$
\tilde{Q} \le Q^\* ,
$$

which is (1). Taking the $\max$ preserves the ordering, so $\tilde{V}\le V^\*$.

**Where the assumptions break.** (4) must hold for **every** iterate $Q$. A practical $\Gamma$
comes from a finite-sample concentration inequality, so it is a high-probability statement about a
fixed $Q$; if $Q$ depends on the data, a union bound or a splitting technique is needed — which is
why the papers carry logarithmic factors. And making $\Gamma$ **too small makes (1) false**,
destroying the meaning of conservatism. The coefficient $\alpha$ of practical CQL is exactly this
choice: too small and you overestimate, too large and you are needlessly conservative.

### R2 — why the suboptimality is measured only under $d^{\pi^\star}$

**Step 1: split in two.**

$$
V^\*(s_0) - V^{\tilde{\pi}}(s_0)
  = \underbrace{\big[V^\*(s_0) - \tilde{V}(s_0)\big]}_{\text{(a)}}
  + \underbrace{\big[\tilde{V}(s_0) - V^{\tilde{\pi}}(s_0)\big]}_{\text{(b)}} .
$$

**Step 2: (b) $\le 0$.** Since $\tilde{\pi}$ is greedy with respect to $\tilde{Q}$ we have
$\tilde{V} = \tilde{T}_{\tilde{\pi}}\tilde{V}$, and the policy version of (5) gives
$\tilde{T}_{\tilde\pi}\tilde{V} \le T_{\tilde\pi}\tilde{V}$. So
$\tilde{V} \le T_{\tilde\pi}\tilde{V}$, and applying the monotonicity of $T_{\tilde\pi}$
repeatedly gives $\tilde{V} \le (T_{\tilde\pi})^k\tilde{V} \to V^{\tilde{\pi}}$, i.e. (b) $\le 0$.
**A conservative estimate does not overestimate the true value of its own policy.**

**Step 3: move (a) to $\pi^\star$'s distribution.** Since $\tilde{V}$ is the fixed point of
$\tilde{T}$, for any policy — in particular $\pi^\star$ — we have
$\tilde{V} \ge \tilde{T}_{\pi^\star}\tilde{V}$ (the $\max$ dominates $\pi^\star$). Using (4) twice,

$$
\tilde{T}_{\pi^\star}\tilde{V} = \hat{T}_{\pi^\star}\tilde{V} - \Gamma_{\pi^\star}
  \;\ge\; T_{\pi^\star}\tilde{V} - 2\Gamma_{\pi^\star},
$$

with $\Gamma_{\pi^\star}(s) := \Gamma(s,\pi^\star(s))$. Combining the two inequalities gives
$\tilde{V} \ge T_{\pi^\star}\tilde{V} - 2\Gamma_{\pi^\star}$, and subtracting
$V^\* = T_{\pi^\star}V^\*$,

$$
V^\* - \tilde{V} \;\le\; T_{\pi^\star}V^\* - T_{\pi^\star}\tilde{V} + 2\Gamma_{\pi^\star}
  = \gamma P^{\pi^\star}\big(V^\* - \tilde{V}\big) + 2\Gamma_{\pi^\star}.
$$

**Step 4: the inverse produces the distribution.** Rearranging gives
$(I - \gamma P^{\pi^\star})(V^\* - \tilde{V}) \le 2\Gamma_{\pi^\star}$, and since every entry of
$(I-\gamma P^{\pi^\star})^{-1} = \sum_t \gamma^t (P^{\pi^\star})^t$ is non-negative, the direction
of the inequality is preserved:

$$
V^\* - \tilde{V} \;\le\; 2\sum_{t\ge0}\gamma^t (P^{\pi^\star})^t \Gamma_{\pi^\star} .
$$

Averaging over $s_0 \sim \rho_0$ makes the right side exactly
$\frac{2}{1-\gamma}\mathbb{E}_{d^{\pi^\star}}[\Gamma]$. With (a) bounded by that and (b) $\le 0$,
we get (2).

**Why this matters.** What appears is $(P^{\pi^\star})^t$ and nothing else — the distribution of
$\tilde{\pi}$ is nowhere in the bound. So **uncertainty in regions $\pi^\star$ never visits does
not contribute.** All-policy concentrability ($\max_\pi \lVert d^\pi/d^{\pi_b}\rVert_\infty$) is
effectively infinite in robot problems, whereas single-policy concentrability $C^\star$ is the
realistic assumption that "the data covers the path the expert took".

**Where the assumptions break.** (2) holds only when $\Gamma$ is a **valid** bound. Using an
uncalibrated proxy such as ensemble variance does not guarantee (4), and then both (1) and (2) are
void. And since $d^{\pi^\star}$ is unknown, (2) is a **post hoc** guarantee — the inability to
estimate $C^\star$ from data is the practical limitation.

### R3 — what breaks without conservatism

With $\Gamma \equiv 0$ the ladder argument of step 3 cannot start without (5). Concretely, the
common convention of setting $\hat{r}$ to 0 and $\hat{P}$ to uniform at an $(s_0,a_0)$ with no data
gives $\hat{Q}(s_0,a_0) = \gamma\,\overline{\hat{V}}$, and the $\max$ **chooses that action** if
this exceeds the others. In other words, an action with no data at all can be selected on the
strength of an average value.

The cost in the other direction is just as clear. If $\Gamma$ is large, the penalty can overwhelm
the reward even where data is **plentiful**, and $\tilde{\pi}$ can end up worse than $\pi_b$. The
reproduction task measures how the crossover moves when the penalty scale $c$ is raised from
$0.05$ to $0.2$. **The amount of conservatism is a hyperparameter that depends on data quality**,
and choosing it offline is an open problem.

### R4 — behaviour regularization versus value conservatism

**Behaviour regularization (a support constraint).** Enforce $\pi(a\mid s) = 0$ for
$a \notin \mathrm{supp}(\pi_b(\cdot\mid s))$. The admissible policy set is then
$\Pi_b := \{\pi : \mathrm{supp}(\pi)\subseteq\mathrm{supp}(\pi_b)\}$, and the best achievable value
is $\max_{\pi\in\Pi_b} J(\pi)$. If the optimal action at some state lies outside
$\mathrm{supp}(\pi_b)$, that state can **never** be made optimal. In the extreme, a deterministic
$\pi_b$ gives $\Pi_b = \{\pi_b\}$ and zero improvement — identical to behavior cloning.

**Value conservatism.** $\tilde{T}$ constrains no support and applies **only a penalty**. So an
out-of-support action is still chosen if $\hat{Q} - \Gamma$ remains the largest. As soon as the
data covers $(s,a)$ even slightly, $\Gamma$ drops below $V_{\max}$ and that action stays a
candidate. That is,

$$
\Pi_b \;\subsetneq\; \{\text{policies that value conservatism admits}\}, \tag{6}
$$

and the bound (2) still holds even when $\pi^\star \notin \Pi_b$ (as long as $\Gamma$ is small
along its path). **That is why value conservatism beats behaviour regularization when the data is
broad and shallow.** Conversely, when the data is narrow and deep (expert trajectories),
$\pi^\star$ is already inside $\Pi_b$ and behaviour regularization is simpler and safer — the
reversal of the reproduction task has this structure.

**Where the assumptions break.** (6) presumes that $\Gamma$ **decreases with visit counts**. In a
deep network, estimating $\Gamma$ from ensemble variance often yields a **smaller** value out of
distribution (overconfidence). The advantage of value conservatism then disappears and behaviour
regularization is the safer choice.

### R5 — the variance of OPE

The trajectory importance-weighted (IS) estimator is
$\hat{J}_{\mathrm{IS}} = \frac1N\sum_{i}\varrho^{(i)}_{0:T-1}G^{(i)}$ and is unbiased,
$\mathbb{E}[\hat{J}_{\mathrm{IS}}] = J(\pi)$, since each trajectory came from $\pi_b$. For the
variance, count the second moment. Because the steps are independent,

$$
\mathbb{E}\big[\varrho_{0:T-1}^2\big]
  = \prod_{t<T}\mathbb{E}_{a\sim\pi_b}\!\left[\left(\frac{\pi(a\mid s_t)}{\pi_b(a\mid s_t)}\right)^{2}\right]
  = \prod_{t<T}\sum_a \frac{\pi(a\mid s_t)^2}{\pi_b(a\mid s_t)} ,
$$

which is (3). When $\pi$ is deterministic and $\pi_b$ is uniform over $m$ actions, each factor is
$\frac{1^2}{1/m} = m$, so $\mathbb{E}[\varrho^2] = m^T$ and
$\mathrm{Var}(\varrho_{0:T-1}) = m^T - 1$. The effective sample size is

$$
\mathrm{ESS} \;=\; \frac{N}{\mathbb{E}[\varrho^2]} \;=\; \frac{N}{m^T} . \tag{7}
$$

At $m=4$, $T=8$ and $N = 2\times10^6$ this is $\mathrm{ESS} = 31$ — two million trajectories are
worth **31 effective samples**. Indeed, a Monte Carlo run under those conditions has
$\hat{\mathbb{E}}[\varrho]$ drift to $0.95$ (away from the true value 1).

**Mitigations and their limits.** Per-decision IS and weighted IS (WIS) reduce the constants but
not the exponential dependence. The doubly robust estimator uses a model $\hat{Q}$ as a control
variate to cut variance, but a wrong $\hat{Q}$ introduces bias in proportion — it trades variance
for bias and is not free (Thomas & Brunskill 2016).

**Where the assumptions break.** (3) assumes $\pi_b$ is **known exactly**. Estimating $\pi_b$ from
human demonstrations or recorded logs makes the denominator wrong and destroys unbiasedness itself.
And if $\pi$ puts mass on an $a$ with $\pi_b(a\mid s) = 0$ the ratio is infinite — support
inclusion is an implicit premise of (3).

## Proof sketch

### R1 and R2 — the lower bound and the suboptimality of pessimism [D3]

**Hypotheses** H1: (4) holds for every $Q$ appearing in the iteration. H2: $0\le\gamma<1$ with
bounded rewards. H3: $\Gamma \ge 0$. H4: the fixed point of $\tilde{T}$ exists (from H2).
**Conclusions** C1: (1). C2: (2).

**Strategy**: C1 is **operator domination plus a monotone ladder argument**. C2 bounds **(b)$\le0$
and the distribution shift of (a)** using the non-negativity of
$(I-\gamma P^{\pi^\star})^{-1}$.

1. From (4) and H3, $\tilde{T}Q \le TQ$ (operator domination) → (5). Uses: H1, H3.
2. Monotonicity and contraction of $\tilde{T}$ → a unique fixed point. Uses: H2, H4.
3. Iterate $\tilde{T}$ from $Q^\*$ to get $\tilde{T}^kQ^\*\le Q^\*$ → C1. Uses: steps 1 and 2.
4. For the greedy policy, $\tilde{V}\le V^{\tilde\pi}$ → (b)$\le0$.
5. For $\pi^\star$, establish
   $\tilde{V}\ge T_{\pi^\star}\tilde{V}-2\Gamma_{\pi^\star}$ and divide by
   $(I-\gamma P^{\pi^\star})$ → the bound on (a) → C2. Uses: (4) twice, non-negativity of the
   inverse.

**Delete one hypothesis**: dropping H3 ($\Gamma\ge0$) breaks the operator domination of step 1 and
makes C1 false (overestimation returns). Weakening H1 to "it does not hold for data-dependent $Q$"
turns step 3 into a high-probability statement and attaches logarithmic factors to (2). Dropping
$\gamma<1$ in H2 means the inverse in step 5 does not exist.

Omitted: constructing $\Gamma$ explicitly from Hoeffding or Bernstein and extending it to every $Q$
with a union bound — the lemmas of Jin et al. 2021 §3.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Specialize (2) to
$\Gamma(s,a) = c\,V_{\max}\sqrt{\log(2/\delta)/n(s,a)}$ and, substituting
$n(s,a) \approx N d^{\pi_b}(s,a)$, write the bound as a function of $C^\star$ and $N$.
*Solution sketch*:
$\mathbb{E}_{d^{\pi^\star}}[\Gamma] = c V_{\max}\sqrt{\log(2/\delta)/N}\,
\mathbb{E}_{d^{\pi^\star}}\big[\sqrt{1/d^{\pi_b}}\big]$, and Cauchy–Schwarz bounds
$\mathbb{E}_{d^{\pi^\star}}[\sqrt{1/d^{\pi_b}}]$ by something of the form
$\sqrt{C^\star\,\lvert\mathrm{supp}\rvert}$. The result is
$\tilde{O}\big(V_{\max}\sqrt{C^\star/N}/(1-\gamma)\big)$ — the product of $N^{-1/2}$ and
$\sqrt{C^\star}$ is the point.

**P2 (proof, ★★★, R1·R2)** Prove the (b)$\le 0$ step exactly: show $\tilde{V}\le V^{\tilde\pi}$ by
monotone iteration of $T_{\tilde\pi}$, and point out why $\tilde\pi$ must be greedy with respect to
**$\tilde{Q}$**. Then say what breaks if $\tilde\pi$ is taken greedy with respect to a different
$Q$.
*Strategy and key inequality*: the starting point is
$\tilde{V} = \max_a\tilde{Q}(\cdot,a) = \tilde{T}_{\tilde\pi}\tilde{V} \le T_{\tilde\pi}\tilde{V}$,
after which monotonicity of $T_{\tilde\pi}$ makes $(T_{\tilde\pi})^k\tilde{V}$ increase to
$V^{\tilde\pi}$. The expansion is withheld.

**P3 (numerical, ★, R5)** For a uniform $\pi_b$ over $m = 4$ actions and a deterministic $\pi$,
compute $\mathbb{E}[\varrho^2]$ for $T = 2, 4, 8$ and the effective sample size at
$N = 2\times10^6$. What is the largest $T$ that keeps $\mathrm{ESS} \ge 1000$?
*Answer*: $\mathbb{E}[\varrho^2] = 4^T = 16,\ 256,\ 65536$ and
$\mathrm{ESS} = N/4^T = 125000,\ 7812,\ 31$ (tolerance: integer rounding down).
$\mathrm{ESS}\ge1000$ requires $4^T \le 2000$, i.e. $T \le 5$ ($4^5 = 1024$,
$\mathrm{ESS} = 1953$).
Check: estimate $\mathbb{E}[\varrho^2]$ by Monte Carlo with $2\times10^6$ samples and confirm it
matches $4^T$ within $\pm10\%$ (at $T=8$ the estimate itself becomes unstable — and that
instability is the conclusion).

**P4 (implementation, ★★, R1·R2·R3)** Implement tabular offline RL, verify (1) and (2)
numerically, and find the reversal point by varying the penalty scale $c$ and the data quality
$\beta$.
*Rubric*: ⓐ $\Gamma$ at an unvisited $(s,a)$ is set to $V_{\max}$ (otherwise (4) is violated);
ⓑ $\tilde{Q}\le Q^\*$ is checked entrywise; ⓒ the left side of (2) is confirmed to be at most the
right side and the **looseness ratio** is reported; ⓓ $d^{\pi^\star}$ is computed by a linear solve
(not by sampling); ⓔ a table reports the cells of the $\beta \times c$ grid where the winner
changes.

**P5 (counterexample, ★★, R4)** Show that the claim "offline RL cannot be worse than the behaviour
policy" is false: construct an instance where excessive conservatism makes
$J(\tilde\pi) < J(\pi_b)$. Then say why behaviour regularization does guarantee at least
$J(\pi_b)$.
*Property checklist*: ⓐ if $\Gamma$ overwhelms the reward scale, $\tilde{Q}$ becomes nearly equal
across actions and the greedy choice becomes **arbitrary**; ⓑ that arbitrary choice can be worse
than $\pi_b$; ⓒ behaviour regularization has $\pi_b \in \Pi_b$, so "at least $\pi_b$" is among its
candidates (if the policy improvement step is monotone); ⓓ hence conservatism **gives a lower bound
but does not guarantee improvement** — distinguishing (1) from (2) is the point of this problem.

**P6 (paper, ★★, R1·R2·R4)** Read Jin et al. 2021 (§3–4), Levine et al. 2020 (§4–5) and Kumar et
al. 2020 (§3 and appendix A) and write, in at most three sentences each: (i) how Jin et al.'s
construction of $\Gamma$ guarantees (4); (ii) one cause of extrapolation error catalogued by Levine
et al. that this lesson does not cover; (iii) why CQL's penalty gives a **lower bound** and whether
that bound is the same as (1).
*Grading rubric*: (i) that a concentration inequality plus a union bound (or splitting) covers
data-dependent $Q$. (ii) one of function-approximation error, iterative error accumulation, or the
optimization difficulty of policy constraints. (iii) passes if it notes that CQL penalizes
$\mathbb{E}_{\mu}[Q] - \mathbb{E}_{\pi_b}[Q]$ and so is a lower bound **at the level of the
expected policy value**, weaker than the entrywise bound of (1). Writing only "it is conservative"
fails.

**P7 (derivation, ★★, R5)** Derive (3), then say why the second moment of the per-decision IS
estimator $\frac1N\sum_i\sum_t\gamma^t\varrho^{(i)}_{0:t}r^{(i)}_t$ is smaller, and why the
exponential dependence nevertheless remains.
*Solution sketch*: trajectory IS multiplies every reward by $\varrho_{0:T-1}$, whereas per-decision
IS multiplies $r_t$ by $\varrho_{0:t}$ only. Terms with small $t$ have variance $m^{t+1}$ and so
shrink the total, but the $t = T-1$ term is still $m^T$ — **the latest reward decides the
exponential term**. The only mitigation is the discount $\gamma^t$ suppressing the late terms.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions
(`lesson-standard.md` §5). Read with three passes and attack questions 4, 5, 6 and 7 in the third.

1. **Jin, Yang & Wang, "Is pessimism provably efficient for offline RL?" (2021, ICML)** — role:
   `seminal`. <https://arxiv.org/abs/2012.15085> — §3–4.
   Why read it: (1) of R1 and (2) of R2 are theorems of this paper, and the notion of
   **single-policy concentrability** becomes sharp here.
   Extra questions: ⓐ where is it shown that the authors' $\Gamma$ (their confidence interval)
   satisfies (4), and which concentration inequality is used? ⓑ what does the lower-bound theorem
   say about conservatism being **necessary**?
2. **Levine, Kumar, Tucker & Fu, "Offline reinforcement learning: tutorial, review, and
   perspectives on open problems" (2020, arXiv)** — role: `survey`.
   <https://arxiv.org/abs/2005.01643> — §4–5.
   Why read it: the standard map classifying the causes of extrapolation error and distribution
   shift. This lesson covers only part of it.
   Extra questions: ⓐ which of the failure causes they list is **not** explained by the (4)
   framework of this lesson? ⓑ how do the authors treat the problem (§5) of choosing
   hyperparameters without online evaluation?
3. **Kumar, Zhou, Tucker & Levine, "Conservative Q-learning for offline reinforcement learning"
   (2020, NeurIPS)** — role: `standard`. <https://arxiv.org/abs/2006.04779> — §3 and appendix A.
   Why read it: the standard algorithm that actually implements the value conservatism of R4; the
   aim is to compare its lower-bound claim with (1).
   Extra questions: ⓐ in which norm and under which distribution is the lower-bound theorem of
   appendix A stated? ⓑ does the paper give a procedure for choosing $\alpha$ from data, and if not,
   how was it set in the experiments?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation? (4) what is guaranteed and **what is not**?
(5) independent and dependent variables, and the baselines — were they tuned fairly? (6) does the
metric match the claim, and are variance and seeds reported? (7) what information needed for
reproduction is missing? (8) if the result were wrong, which assumption would you doubt first?
(9) compute and memory cost, and real-time feasibility? (10) what would you change to go beyond
this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: under **two minutes** on a laptop CPU, under
200 MB, numpy only. The data comes from a generator script (a tabular reduction of D4RL's
random/medium/expert split — the same **structure** reproduced without the public dataset).

```python
import numpy as np

GAMMA = 0.95


def make_mdp(n_s=20, n_a=4, seed=0):
    rng = np.random.default_rng(seed)
    p = rng.dirichlet(np.full(n_s, 0.4), size=(n_s, n_a))
    r = rng.uniform(0.0, 1.0, size=(n_s, n_a))
    return p, r


def behaviour(pi_star, beta, n_s, n_a):
    """beta of the mass on the expert action, the rest uniform (beta=0 random, 1 expert)."""
    b = np.full((n_s, n_a), (1 - beta) / n_a)
    b[np.arange(n_s), pi_star] += beta
    return b / b.sum(axis=1, keepdims=True)
```

Collect 10 trajectories of length 40 and set the penalty to
$\Gamma(s,a) = c\,V_{\max}\sqrt{\log 4 / n(s,a)}$ (or $V_{\max}$ if unvisited). Compare three
methods: **BC** (most frequent action per state), **conservative VI** (the fixed point of
$\tilde{T}$) and **non-conservative VI** ($\Gamma\equiv0$).

**Acceptance criteria** — all four must hold.

1. **The lower bound (1)**: for trajectory counts $\in\{2,5,20,100\}$ (uniform behaviour policy),
   $\tilde{Q} \le Q^\* + 10^{-9}$ holds **entrywise** (measured: holds in all four cases).
2. **The suboptimality bound (2)**: in the same four cases,
   $V^\*(s_0)-V^{\tilde\pi}(s_0) \le \frac{2}{1-\gamma}\mathbb{E}_{d^{\pi^\star}}[\Gamma]$ holds,
   and the **looseness ratio** (left over right) is reported (measured $0.006$–$0.017$, so the
   bound is 60–160 times loose). Obtain $d^{\pi^\star}$ by the **linear solve**
   $(1-\gamma)(I-\gamma (P^{\pi^\star})^\top)^{-1}\rho_0$.
3. **The reversal with data quality**: with $c = 0.05$,
   $\beta \in \{0, 0.25, 0.5, 0.75, 1\}$ and 12 seeds averaged,
   ⓐ at $\beta=0$ BC is **worse than even the behaviour policy** ($7.74 < 8.54$);
   ⓑ conservative VI is at least as good as the behaviour policy at every $\beta$;
   ⓒ conservative VI $>$ BC for $\beta \le 0.5$, while for $\beta \ge 0.75$ both reach $J^\star$
   and tie (measured $J^\star = 13.285$).
4. **Conservatism is not free**: on the same grid, ⓐ at $\beta=0$ (broad data) non-conservative VI
   beats conservative VI ($12.894 > 12.498$); ⓑ at $\beta\in\{0.25,0.5,0.75\}$ (narrow data)
   conservative VI wins ($13.156>12.940$, $13.283>12.911$, $13.285>12.948$); ⓒ raising $c$ from
   $0.05$ to $0.2$ **switches** the winner at $\beta=0.25$ from conservative to non-conservative VI.

**Baselines**: ⓐ the behaviour policy's own value $J(\pi_b)$ — computed exactly by a linear solve;
it is the reference for "did we improve on the data?". ⓑ $J^\star$ — the attainable ceiling.
ⓒ optional: implement a behaviour-regularized (support-constrained) version and confirm that for
small $\beta$ it gets **stuck** near $J(\pi_b)$ — (6) of R4 made visible in code.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| Criterion 1 fails ($\tilde{Q} > Q^\*$) | $\Gamma$ at unvisited $(s,a)$ was not set to $V_{\max}$ | print $\Gamma[n=0]$ — it must be $R_{\max}/(1-\gamma)$ |
| The ratio in criterion 2 exceeds 1 | $d^{\pi^\star}$ was not normalized (the $(1-\gamma)$ is missing) or the transpose was omitted | check that $\sum_s d^{\pi^\star}(s) = 1$ |
| No reversal appears | there is so much data that every $(s,a)$ is covered | print the number of pairs with $n(s,a)=0$ — it must grow with $\beta$ |
| BC does well even at $\beta=0$ | the expert action was used as the default at unvisited states (leakage) | fix the default action to 0 and re-run |
| Conservative VI loses at every $\beta$ | $c$ is so large that the penalty overwhelms the reward ($\le 1$) | print the median of $\Gamma$ next to $R_{\max}$ |
| The winner changes between seeds | with 12 seeds the difference is inside the standard error | increase the seed count and tally wins per seed |

## Open problems

- **(open problem) A principle for choosing the amount of conservatism offline** — (2) holds
  whenever $\Gamma$ is valid, but **how large** to make $\Gamma$ depends on data quality
  (criterion 4 of the reproduction task) and cannot be chosen offline with a validation set. One
  online evaluation would settle it, but the premise of offline RL is that one evaluation is
  expensive. Current approaches: automatic tuning of CQL's $\alpha$
  ([CQL](https://arxiv.org/abs/2006.04779)), designs that **never query** out of distribution
  ([IQL](https://arxiv.org/abs/2110.06169)). What is missing: a selection rule using offline data
  alone.
- **(open problem) Obtaining a calibrated $\Gamma$ in deep networks** — in the tabular case visit
  counts give $\Gamma$. In a deep network, ensemble variance is often overconfident out of
  distribution, so (4) is not guaranteed. Current approaches:
  [conformal prediction](https://arxiv.org/abs/2107.07511),
  [system-level OOD detection](https://arxiv.org/abs/2212.14020). What is missing: a $\Gamma$ that
  certifies (4) inside the control loop.
- **(open problem) Breaking OPE's curse of horizon with structure** — the $m^T$ of (7) cannot be
  avoided without assumptions. The structure of robot tasks (low-dimensional state manifolds,
  sparse and delayed rewards, local policies) has not been written down as assumptions that buy
  polynomial variance. Current approaches:
  [doubly robust estimation](https://arxiv.org/abs/1604.00923), model-based OPE
  (`c8-model-based-world-models`). What is missing: a variance bound that uses robot structure.
- **(open problem) Diagnosing data quality in advance** — the reversal of the reproduction task is
  observed when $\beta$ is **known**. In practice one receives a dataset and must decide
  **beforehand** whether to use BC or offline RL, and there is no metric that makes that call from
  the data alone. Current approaches: the quality classes of
  [D4RL](https://arxiv.org/abs/2004.07219), statistics of the behaviour policy's entropy and return
  distribution. What is missing: a dataset metric that predicts the algorithm choice.

## Concept check

Run `rc quiz c8-offline-rl`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: why the fixed point of the pessimistic operator is a lower bound; under which
distribution the uncertainty is averaged in the suboptimality bound; whether conservative offline
RL can be worse than the behaviour policy; whether behaviour regularization and value conservatism
admit the same policy set; and the second moment of the trajectory importance ratio.

## How to study this stage

1. **Look at operator domination first (45 min)** — write the single line
   $\tilde{T}Q \le TQ$ of (5) and go from there to (1) on a blank page via the ladder argument.
   The key is to notice that **unbiasedness is never used** — the guarantees of offline RL rest on
   **ordering (inequalities)**, not on statistical unbiasedness.
2. **Check by hand why the distribution in (2) is $\pi^\star$ (75 min)** — rewrite steps 3 and 4
   and track where $\tilde\pi$ disappears. This single fact is the turning point of offline RL
   theory, and reading it against the covariate shift of `c8-imitation-learning` makes the structure
   visible.
3. **Meet the curse of horizon as a number (45 min)** — solve problem P3 and compute the ESS of 31
   at $m=4$, $T=8$ yourself. Then estimate $\mathbb{E}[\varrho]$ from $2\times10^6$ samples and
   watch it drift from the true value 1 — the stage at which you feel that an "unbiased estimator"
   can be useless.
4. **Produce the reversal experimentally (120 min)** — pass criteria 1 and 2 (the theory checks)
   before moving to criteria 3 and 4 (the reversal). Run the $\beta \times c$ grid yourself and find
   **the cells where the winner changes**. Anyone who has built that table does not write the
   sentence "offline RL is better than BC" again.
5. **The three papers, theory → practice (150 min)** — Jin et al. (the guarantee) → Levine et al.
   (the map) → CQL (the implementation). Write the one-page note for each; this is **not** optional.
   In the CQL note, write one line on "in which norm and under which distribution the lower bound
   holds" and compare it with (1).
6. **End at what cannot be done (105 min)** — pick the open problem of choosing the conservatism
   level, propose one rule for picking $c$ **from the data alone** on the grid of the reproduction
   task, and write down a case where that rule fails.

**Passing bar**: you can derive (1) and (2) from a blank page and say why the expectation in (2) is
over $d^{\pi^\star}$, compute (3) and the ESS, and you hold code that located the reversal on the
data-quality grid plus notes on the three papers.
