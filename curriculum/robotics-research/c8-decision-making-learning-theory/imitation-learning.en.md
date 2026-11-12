---
id: c8-imitation-learning
lang: en
title: Imitation learning and covariate shift
summary: >-
  Derive why the error of behavior cloning (BC) grows as $O(\epsilon T^2)$ in the horizon, and show
  that the order is tight by constructing a matching lower bound. Then build the argument by which
  DAgger, querying on the learner's own distribution, brings the regret down to $O(\epsilon T)$,
  using the no-regret property of online learning. The lesson closes by organizing the reward
  ambiguity of inverse RL and deriving the maximum-entropy solution through Lagrange duality.
objectives:
  - Derive the compound-error bound $O(\epsilon T^2)$ of BC with no missing steps.
  - Construct a lower-bound MDP showing that the order is tight.
  - Reconstruct DAgger's regret bound $O(\epsilon T)$ from no-regret online learning.
  - Separate the horizon exponents of BC and DAgger numerically into 2 and 1.
  - Show with two transformations that a reward function is not identified by an optimal policy alone.
  - Derive that the maximum-entropy solution under feature-expectation matching is $p(\tau)\propto\exp(\theta^\top f(\tau))$.
tags: [imitation-learning, behavior-cloning, dagger, covariate-shift, irl, research]
---

# Imitation learning and covariate shift

## Setup and notation

The MDP notation of `c8-mdp-pomdp-bellman` and the occupancy notation of `c8-policy-gradient` carry
over. This lesson uses a **finite horizon** $T$ without discounting (a sum of costs). Additional
**recommended** background:

- Probability: the union bound, total variation distance, first-order coupling arguments that need
  no martingales.
- Online learning: the definition of regret and the property of a no-regret algorithm
  (Follow-the-Leader family).
- Convex optimization: entropy maximization under equality constraints and Lagrange duality
  (`r0-convex-optimization`).

Added notation:

| Symbol | Meaning |
|---|---|
| $T$ | the horizon; the cost is $J(\pi) = \mathbb{E}\big[\sum_{t=0}^{T-1} c(s_t,a_t)\big]$ with $c \in [0,1]$ |
| $\pi^\star$ | the expert policy; $\hat{\pi}$ is the learned policy |
| $d_\pi^t$ | the state distribution after following $\pi$ for $t$ steps; $d_\pi = \frac1T\sum_{t<T} d_\pi^t$ |
| $\epsilon$ | supervised error, $\epsilon = \mathbb{E}_{s\sim d_{\pi^\star}}\big[\mathbf{1}\{\hat{\pi}(s)\neq\pi^\star(s)\}\big]$ |
| $\epsilon_N$ | DAgger's average online loss over $N$ iterations, $\epsilon_N = \min_\pi \frac1N\sum_{i=1}^N \ell_i(\pi)$ |
| $u$ | bound on the cost-to-go gap, $u = \max_{s,a}\big(Q^{\pi^\star}_{T-t}(s,a) - V^{\pi^\star}_{T-t}(s)\big)$ |
| $f(\tau)$ | trajectory features, $f(\tau) = \sum_t \phi(s_t,a_t) \in \mathbb{R}^m$ |
| $\theta$ | reward parameters, with the linear reward $r_\theta(s,a) = \theta^\top\phi(s,a)$ |

Costs are normalized to $[0,1]$, so $J(\pi^\star) \ge 0$ and no policy exceeds $J \le T$ — **every
bound saturates trivially at $T$**, so the meaningful regime is $\epsilon T \ll 1$.

## Key results

The bracket gives the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (BC's compound error) [D3]** — when $\hat{\pi}$ has supervised error $\epsilon$ on the
  expert's distribution,
  $$
  J(\hat{\pi}) \;\le\; J(\pi^\star) + \epsilon\,T^2 , \tag{1}
  $$
  and more precisely
  $J(\hat{\pi}) - J(\pi^\star) \le \sum_{t=0}^{T-1} \epsilon\,(T-t) \le \tfrac12\epsilon T(T+1)$.
  **The $T^2$ is the product of "the probability of erring at all, $\epsilon T$" and "the cost
  remaining after the error, $T$".**
- **R2 (lower bound: the $T^2$ is tight) [D3]** — with only two states (on-track and off-track)
  and two actions one can build an MDP and a $\hat{\pi}$ with
  $J(\hat{\pi}) - J(\pi^\star) = \Omega(\epsilon T^2)$. So the order in (1) is not slack in the
  proof technique but **a property of the BC algorithm**.
- **R3 (DAgger's regret bound) [D3]** — running DAgger as no-regret online learning gives, after
  $N$ iterations, some $\hat{\pi} \in \{\pi_1,\dots,\pi_N\}$ with
  $$
  J(\hat{\pi}) \;\le\; J(\pi^\star) + u\,T\,\epsilon_N + O(1), \tag{2}
  $$
  which is **linear** in $T$. What makes the difference is measuring the loss on the **learner's
  own distribution** $d_{\pi_i}$, so the learner learns the recovery action at the off-track states
  it actually visits.
- **R4 (reward ambiguity in IRL) [D2]** — an optimal policy alone does not identify the reward.
  There are at least two degrees of freedom: ⓐ positive scaling $r \mapsto \alpha r$ ($\alpha>0$)
  and ⓑ potential shaping $r(s,a,s') \mapsto r(s,a,s') + \gamma\Phi(s') - \Phi(s)$ — both preserve
  the set of optimal policies. So IRL is an **underdetermined problem without an extra principle**.
- **R5 (the maximum-entropy solution) [D2]** — maximizing the entropy of a trajectory distribution
  under the feature-matching constraint
  $\mathbb{E}_{p}[f(\tau)] = \mathbb{E}_{\text{expert}}[f(\tau)]$ gives
  $$
  p_\theta(\tau) \;=\; \frac{1}{Z(\theta)}\exp\!\big(\theta^\top f(\tau)\big),
    \qquad Z(\theta) = \sum_\tau \exp\!\big(\theta^\top f(\tau)\big), \tag{3}
  $$
  with $\theta$ determined by a **convex** log-likelihood problem. The gradient is
  $\nabla_\theta \log p_\theta(\tau_{\text{data}}) = f(\tau_{\text{data}}) - \mathbb{E}_{p_\theta}[f(\tau)]$
  — a **difference of feature expectations**.

## Derivation

### R1 — BC's compound error

**Setup.** Run $\hat{\pi}$ and $\pi^\star$ from the same initial state simultaneously (a coupling).
Let $A_t$ be the event that the two policies have not chosen a different action up to step $t$.

**Step 1: the probability of a first disagreement.** While $A_t$ holds, the distribution of the
states $\hat{\pi}$ visits is **identical** to $d^t_{\pi^\star}$ (it took the same actions). So the
probability of first differing at step $t$ is bounded by the error under $d^t_{\pi^\star}$:

$$
\Pr\!\big[\text{first disagreement at step } t\big]
  \;\le\; \mathbb{E}_{s\sim d^t_{\pi^\star}}\big[\mathbf{1}\{\hat{\pi}(s)\neq\pi^\star(s)\}\big]
  \;=:\; \epsilon_t , \qquad \frac{1}{T}\sum_{t<T}\epsilon_t = \epsilon . \tag{4}
$$

**Step 2: the cost after a disagreement.** Once they differ there is no guarantee at all. Since
costs lie in $[0,1]$, the cost of the remaining $T-t$ steps is at most $T-t$, while the expert pays
$\ge 0$ over the same stretch. So that event contributes at most $(T-t)$.

**Step 3: summation.** Decomposing into the mutually exclusive events "first disagreement at step
$t$",

$$
J(\hat{\pi}) - J(\pi^\star)
  \;\le\; \sum_{t=0}^{T-1} \epsilon_t \,(T-t)
  \;\le\; \Big(\max_t \epsilon_t\Big)\sum_{t=0}^{T-1}(T-t) ,
$$

and using the looser form that replaces $\epsilon_t$ by its mean $\epsilon$, with
$\sum_t (T-t) = T(T+1)/2$, gives (1). To write it without assuming the $\epsilon_t$ are uniform,
bound $\sum_t \epsilon_t (T-t) \le T\sum_t \epsilon_t = \epsilon T^2$ — that is the form in (1).

**Reading the $T^2$.** Two factors multiply: the probability of erring **at least once** is
$O(\epsilon T)$, and the cost that then accumulates is $O(T)$. Remove either and the bound becomes
linear — DAgger does not reduce the former; it reduces **the latter** (by learning recovery).

**Where the assumptions break.** Step 1 requires a **coupling**. Non-deterministic transitions are
fine if the same random numbers are used, but if both policies are stochastic the probability of
"the same action" has to be recounted and the definition of $\epsilon$ becomes a total-variation
distance. The $(T-t)$ of step 2 is a worst case that presumes **no recovery**. In a task where
recovery takes $O(1)$ steps the actual cost approaches $O(\epsilon T)$ — so "BC is $T^2$" is also
**a statement about task structure** (problem P5).

### R2 — the lower-bound construction

To show the $T^2$ is not slack in the proof, we need an example that **attains** it.

**Construction.** The states are $\{g, b\}$ (on track, off track) and the actions are
$\{\texttt{stay}, \texttt{fix}\}$. Transitions are deterministic: from $g$, $\texttt{stay}$ goes to
$g$ and $\texttt{fix}$ goes to $b$; from $b$, **both actions** go to $b$ (absorbing). The costs are
$c(g,\cdot) = 0$ and $c(b,\cdot) = 1$. The expert has $\pi^\star(g) = \texttt{stay}$, and $b$
**never appears** in the expert's distribution.

Take $\hat{\pi}$ to be "at $g$, choose $\texttt{fix}$ with probability $\epsilon$, otherwise
$\texttt{stay}$". The expert's distribution has mass only at $g$, so the supervised error is exactly
$\epsilon$.

**Computing the cost.** Let $\tau$ be the first time $\texttt{fix}$ is chosen, so
$\Pr[\tau = t] = \epsilon(1-\epsilon)^{t}$, after which every step costs 1:

$$
J(\hat{\pi}) = \sum_{t=0}^{T-1}\epsilon(1-\epsilon)^{t}\,(T-1-t) .
$$

Rather than writing the closed form, expand with $(1-\epsilon)^t \approx 1$ in the regime
$\epsilon T \ll 1$:

$$
J(\hat{\pi}) \;\approx\; \epsilon \sum_{t=0}^{T-1}(T-1-t) = \epsilon\,\frac{T(T-1)}{2}
  \;=\; \Omega(\epsilon T^2), \tag{5}
$$

while $J(\pi^\star) = 0$. So the order in (1) is tight. **The absorbing state is decisive** — allow
recovery from $b$ and the construction collapses.

### R3 — DAgger

**The algorithm.** For $i = 1,\dots,N$: ⓐ collect trajectories with the current policy $\pi_i$;
ⓑ label the states of those trajectories with the **expert's** actions and **aggregate** them into
the dataset; ⓒ train $\pi_{i+1}$ on the aggregated data. The key is that the states in ⓑ come from
$d_{\pi_i}$.

**Step 1: define the loss together with its distribution.** Let the loss of iteration $i$ be
$\ell_i(\pi) = \mathbb{E}_{s \sim d_{\pi_i}}\big[\mathbf{1}\{\pi(s)\neq\pi^\star(s)\}\big]$. DAgger
is **online learning** on this sequence of losses, and training on the aggregated data is
Follow-the-Leader.

**Step 2: use the no-regret property.** When the loss sequence is convex (or randomized over a
finite hypothesis set), a no-regret algorithm gives

$$
\frac{1}{N}\sum_{i=1}^{N}\ell_i(\pi_i) \;\le\; \underbrace{\min_\pi \frac1N\sum_{i=1}^N \ell_i(\pi)}_{=\;\epsilon_N}
  \;+\; \underbrace{\frac{\gamma_N}{N}}_{\to\,0} , \tag{6}
$$

so the **average error on its own distribution** converges to the error $\epsilon_N$ of the best
fixed policy. The only difference from BC is that BC controlled this quantity only under the
**expert's** distribution.

**Step 3: move to cost with the performance difference lemma.** Writing R3 of
`c8-policy-gradient` in finite-horizon cost form,

$$
J(\pi) - J(\pi^\star) = \sum_{t=0}^{T-1}
  \mathbb{E}_{s\sim d^t_{\pi}}\Big[ Q^{\pi^\star}_{T-t}\big(s,\pi(s)\big) - V^{\pi^\star}_{T-t}(s)\Big].
$$

The bracket is 0 when $\pi$ chooses the same action as $\pi^\star$ and at most $u$ otherwise. Hence

$$
J(\pi_i) - J(\pi^\star) \;\le\; u\,T\,\ell_i(\pi_i) .
$$

Averaging with (6), at least one $i$ has $\ell_i(\pi_i) \le \epsilon_N + \gamma_N/N$, and that
$\pi_i$ satisfies (2).

**Why $T$ appears only once.** Because the distribution is $d_{\pi_i}$, the "error at off-track
states" is already inside $\ell_i$. There is no need to give up as in step 2 of BC ("after leaving
we know nothing"), so the step that multiplies by $(T-t)$ disappears and $u$ — the cost-to-go gap
created by one mistake — takes its place. **In a task where $u$ must be of order $T$** (no
recovery), DAgger falls back to $T^2$.

**Where the assumptions break.** (6) needs the loss sequence to be no-regret learnable — a finite
hypothesis set or convex losses — and there is no guarantee for deep networks. It also needs the
ability to **query the expert at arbitrary states**. Putting a human expert into an off-track state
on a real robot and asking "what would you do now?" is expensive and the labels are poor — DAgger's
practical barrier is this query model, not the theory.

### R4 — reward ambiguity

**ⓐ Scale.** With $r' = \alpha r$ ($\alpha > 0$), every policy's value scales by $\alpha$ and the
ordering is preserved, so the optimal policy is unchanged. The **magnitude** of the reward is
therefore not determined by observation.

**ⓑ Potential shaping.** For any $\Phi:\mathcal{S}\to\mathbb{R}$, setting
$r'(s,a,s') = r(s,a,s') + \gamma\Phi(s') - \Phi(s)$ gives, along any trajectory,

$$
\sum_{t}\gamma^t\big(\gamma\Phi(s_{t+1}) - \Phi(s_t)\big) = -\Phi(s_0)
$$

(a telescoping sum), so every policy's value shifts by the **same constant** $-\Phi(s_0)$. A
constant shift does not change the ordering, so the set of optimal policies is preserved.

The degrees of freedom created by ⓐ and ⓑ have dimension $\lvert\mathcal{S}\rvert$ (that of $\Phi$)
plus one. In other words, **even observing the optimal policy perfectly determines the reward only
within a manifold of dimension $\lvert\mathcal{S}\rvert+1$.** IRL must introduce an **extra
principle** to pick one point of that manifold — maximum margin (Abbeel & Ng 2004) and maximum
entropy (Ziebart 2008) are two such principles.

**Where the assumptions break.** ⓑ requires $\Phi$ to be a function of the state only. If $\Phi$
depends on the action the telescoping fails and the optimal policy changes — the most common bug in
designing shaping rewards.

### R5 — the maximum-entropy solution

**The problem.** Over trajectory distributions $p$,

$$
\max_p \; H(p) = -\sum_\tau p(\tau)\log p(\tau)
  \quad\text{s.t.}\quad \sum_\tau p(\tau) f(\tau) = \tilde{f},\;\; \sum_\tau p(\tau) = 1 ,
$$

where $\tilde{f}$ is the empirical feature expectation of the expert data.

**Lagrange duality.** Introducing multipliers $\theta \in \mathbb{R}^m$ (feature constraint) and
$\lambda$ (normalization),

$$
\mathcal{L} = -\sum_\tau p\log p + \theta^\top\Big(\tilde{f} - \sum_\tau p f(\tau)\Big)
  + \lambda\Big(1 - \sum_\tau p\Big).
$$

From $\partial\mathcal{L}/\partial p(\tau) = -\log p(\tau) - 1 - \theta^\top f(\tau) - \lambda = 0$,

$$
p(\tau) = \exp\!\big(-1-\lambda\big)\exp\!\big(-\theta^\top f(\tau)\big),
$$

and absorbing $\lambda$ into the normalizer and flipping the sign $\theta \to -\theta$ gives (3).
Since entropy is strongly convex and the constraints are linear, the solution is **unique**.

**Determining $\theta$.** The dual function is $g(\theta) = \log Z(\theta) - \theta^\top\tilde{f}$
with $\nabla g = \mathbb{E}_{p_\theta}[f] - \tilde{f}$ and
$\nabla^2 g = \mathrm{Cov}_{p_\theta}(f) \succeq 0$, so this is **convex minimization**. The
stationary point is feature-expectation matching, which is the gradient in R5. The difficulty is
that $Z(\theta)$ and $\mathbb{E}_{p_\theta}[f]$ are **sums over all trajectories** — computable
exactly by dynamic programming in a deterministic finite MDP (the backward pass of Ziebart 2008),
but requiring approximation (sampling, soft value iteration) in stochastic or continuous problems.
That soft value iteration is the starting point of `c8-control-as-inference`.

**Where the assumptions break.** The premise that the reward is linear in features
($r_\theta = \theta^\top\phi$) is essential. A reward the features cannot express is not even a
candidate, so "the reward IRL found" is **determined by the feature design**. And (3) assumes the
expert is not **optimal** but **Boltzmann-rational** (suboptimality penalized exponentially) — if
the expert really is optimal, the MaxEnt solution is more stochastic than the expert.

## Proof sketch

### R1 and R2 — the upper and lower bounds [D3]

**Hypotheses** H1: $c \in [0,1]$. H2: finite horizon $T$, no discounting. H3: deterministic
transitions (or a coupling with shared random numbers). H4:
$\epsilon = \mathbb{E}_{d_{\pi^\star}}[\mathbf{1}\{\hat\pi\neq\pi^\star\}]$.
**Conclusions** C1: (1). C2: an MDP attaining that order exists.

**Strategy**: for the upper bound, **coupling plus decomposition by the first disagreement time**;
for the lower bound, a **two-state MDP with an absorbing state**.

1. Show that under $A_t$ the state distribution of $\hat{\pi}$ equals $d^t_{\pi^\star}$ → (4).
   Uses: H3 (the coupling).
2. Bound the cost after a disagreement by $(T-t)$. Uses: H1.
3. Sum over the mutually exclusive events → C1. Uses: H4.
4. Lower bound: make $b$ absorbing so that the worst case of step 2 is **realized** → C2.

**Delete one hypothesis**: dropping the boundedness of costs in H1 makes step 2 meaningless.
Dropping the coupling in H3 breaks the "same distribution" of step 1, and with stochastic policies
$\epsilon$ must be measured in total variation. Dropping absorption in step 4 (recovery possible)
collapses the lower bound, and $T^2$ becomes **only an upper bound** — this is where problem P5
lives.

### R3 — DAgger's linear regret [D3]

**Hypotheses** H1–H2 (as above). H5: the expert can be queried at arbitrary states. H6: a no-regret
algorithm is used on the loss sequence $\{\ell_i\}$ ($\gamma_N/N \to 0$). H7:
$u = \max(Q^{\pi^\star}-V^{\pi^\star})$ is finite.
**Conclusion** C: (2).

**Strategy**: use the performance difference lemma to turn cost into **classification error on the
learner's own distribution**, then bound it with no-regret.

1. Apply the finite-horizon performance difference lemma. Uses: H2.
2. Bound the bracket by $u\cdot\mathbf{1}\{\pi\neq\pi^\star\}$ to get
   $J(\pi_i)-J(\pi^\star) \le uT\ell_i(\pi_i)$. Uses: H7.
3. Apply (6) to get $\frac1N\sum_i \ell_i(\pi_i) \le \epsilon_N + \gamma_N/N$. Uses: H5 and H6.
4. Some $i$ is at or below the average, and that $\pi_i$ satisfies C.

**Delete one hypothesis**: if $u$ in H7 is of order $T$, (2) becomes
$uT\epsilon_N = O(T^2\epsilon_N)$ and **degenerates** to BC's order. So DAgger's gain depends on the
task property that recovery is cheap. Dropping H5 makes the algorithm itself unrunnable — with only
offline data DAgger cannot be used, and that case is `c8-offline-rl`.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Re-derive (1) for non-uniform $\epsilon_t$ and find the arrangement of
$\{\epsilon_t\}$ (with the mean $\epsilon$ fixed) that makes the bound worst.
*Solution sketch*: maximize $\sum_t \epsilon_t(T-t)$ subject to $\sum_t \epsilon_t = \epsilon T$.
The weight $(T-t)$ is largest at $t=0$, so the worst arrangement **puts all the error at the
earliest steps**, giving $\epsilon T\cdot T = \epsilon T^2$. Putting it at the end drops to
$O(\epsilon T)$ — the precise form of the practitioner's intuition that errors in the initial state
are fatal.

**P2 (proof, ★★★, R3)** Make the role of $u$ in (2) precise: write its definition, construct a task
with $u \le 1$ and one with $u = \Theta(T)$, and show that in the latter DAgger's bound has the same
order as BC's.
*Strategy and key inequality*:
$u = \max_{s,a}(Q^{\pi^\star}_{T-t}(s,a) - V^{\pi^\star}_{T-t}(s))$ is "the largest extra cost one
mistake can create". An example with $u\le1$ is a tracking task with one-step recovery; one with
$u=\Theta(T)$ is the absorbing construction of R2. The expansion is withheld.

**P3 (numerical, ★, R1·R2)** With $\epsilon = 10^{-3}$ and $T = 200$, compute the bound (1) and the
actual cost of the lower-bound construction (5). What is their ratio?
*Answer*: the bound is $\epsilon T^2 = 40$ and the tighter form is $\tfrac12\epsilon T(T+1) = 20.1$.
The **exact** cost of the lower-bound construction is
$\sum_{t<T}\epsilon(1-\epsilon)^t(T-1-t) = 18.6488$ (tolerance $10^{-3}$), slightly below the
approximation $\epsilon T(T-1)/2 = 19.9$ that ignores the decay of $\epsilon(1-\epsilon)^t$. The
ratio is $40/18.6488 = 2.145$ — **the bound is loose only by a factor of about two in the constant;
the order is exact.**
Check: double $T$ and verify that both values grow by roughly a factor of four (while
$\epsilon T \ll 1$).

**P4 (implementation, ★★, R1·R3)** In the environment of the reproduction task, train BC and DAgger
with the **same expert query budget** and regress the regret on $T$ in log-log to obtain the slopes.
*Rubric*: ⓐ both methods use the same query budget (number of labels); ⓑ DAgger samples states
**uniformly** from the learner's own trajectories (using only the start of each trajectory never
sees the off-track states — the most common implementation bug); ⓒ the slopes are BC $\approx 2$ and
DAgger $\approx 1$; ⓓ the horizon range stays inside $\epsilon T \ll 1$; ⓔ the number of seeds and
the standard error are reported.

**P5 (counterexample, ★★, R1·R2)** Show that the claim "BC's error always grows as $T^2$" is false:
construct an MDP where recovery takes $O(1)$ steps and BC with the same $\epsilon$ loses only
$O(\epsilon T)$. Then say why DAgger is (or is not) still advantageous there.
*Property checklist*: ⓐ the structure must recover from the off-track state using an action **the
learner already knows** (for example a state with a single action); ⓑ then $u = O(1)$, so the bound
of R3 is also $O(\epsilon T)$; ⓒ hence the two methods share an order and differ only in constants;
ⓓ conclusion: $T^2$ is not a property of BC but of **BC × irrecoverability**.

**P6 (paper, ★★, R1·R3·R5)** Read Ross & Bagnell 2010 (§2–3), Ross et al. 2011 (§3–4) and Ziebart
et al. 2008 (§3–4) and write, in at most three sentences each: (i) how the lower-bound construction
of the 2010 paper differs from R2 here; (ii) where the 2011 paper uses no-regret and which step
breaks without it; (iii) which quantity of (3) the backward pass of MaxEnt IRL computes.
*Grading rubric*: (i) passes if it names the cost structure (absorbing versus stochastic recovery)
and the difference in the definition of $\epsilon$. (ii) that the loss sequence is non-stationary,
so a fixed-distribution assumption is unavailable. (iii) passes if it names $Z(\theta)$ and
$\mathbb{E}_{p_\theta}[f]$ (the partition function and the feature expectation). Writing only "it
performs well" fails.

**P7 (derivation, ★★, R4·R5)** Show by telescoping that potential shaping preserves the optimal
policy, and explain how that degree of freedom is **removed** in MaxEnt IRL. Where does it break if
$\Phi$ depends on the action?
*Solution sketch*: the telescoping is
$\sum_t\gamma^t(\gamma\Phi(s_{t+1})-\Phi(s_t)) = -\Phi(s_0)$. MaxEnt **restricts the functional
form** to $r_\theta = \theta^\top\phi$, so the freedom survives only when the shaping term lies in
the span of the features. With $\Phi(s,a)$, the term $\gamma\Phi(s_{t+1},a_{t+1})$ brings in the next
action, the telescoping does not close, a policy-dependent term remains, and the optimal policy
changes.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions
(`lesson-standard.md` §5). Read with three passes and attack questions 4, 5, 6 and 7 in the third.

1. **Ross & Bagnell, "Efficient reductions for imitation learning" (2010, AISTATS)** — role:
   `seminal`. <https://proceedings.mlr.press/v9/ross10a.html> — read §2–3 only.
   Why read it: the $O(\epsilon T^2)$ upper bound of R1 and the lower bound of R2 are this paper.
   Extra questions: ⓐ why is the authors' forward training algorithm, which achieves
   $O(\epsilon T)$, not used in practice (the cost of a non-stationary policy)? ⓑ how does the bound
   change if $\epsilon$ is measured with a surrogate loss rather than 0-1 loss?
2. **Ross, Gordon & Bagnell, "A reduction of imitation learning and structured prediction to
   no-regret online learning" (2011, AISTATS)** — role: `seminal`.
   <https://arxiv.org/abs/1011.0686> — §3–4 and the appendix.
   Why read it: (2) of R3 and its proof are theorems of this paper.
   Extra questions: ⓐ what does the schedule of $\beta_i$ (the mixing rate between expert and
   learner) do, and what breaks if $\beta_i = 0$? ⓑ were the expert query counts matched fairly in
   the experiments?
3. **Ziebart, Maas, Bagnell & Dey, "Maximum entropy inverse reinforcement learning" (2008, AAAI)** —
   role: `seminal`. <https://cdn.aaai.org/AAAI/2008/AAAI08-227.pdf> — §3–4.
   Why read it: this is the paper that closes the ambiguity of R4 with the principle of R5.
   Extra questions: ⓐ write the quantities computed by the authors' backward and forward passes in
   the notation of (3). ⓑ how does not assuming the expert is optimal change the result?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation? (4) what is guaranteed and **what is not**?
(5) independent and dependent variables, and the baselines — were they tuned fairly? (6) does the
metric match the claim, and are variance and seeds reported? (7) what information needed for
reproduction is missing? (8) if the result were wrong, which assumption would you doubt first?
(9) compute and memory cost, and real-time feasibility? (10) what would you change to go beyond
this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: under **two minutes** on a laptop CPU (about forty
million pure-Python loop steps across the two experiments), under 100 MB, numpy only. No data is
needed — the lesson supplies the environment and the expert.

**The environment (drift tracking).** The state is the distance off track
$d \in \{0,\dots,5\}$ and the action $a \in \{-1,0,+1\}$ moves $d$ by that amount (clipped to the
range). At every step, with probability $p = 0.002$, a disturbance pushes $d$ by $+1$. The cost is 1
when $d > 0$ and 0 otherwise. The expert is $\pi^\star(d) = -1\ (d>0)$, $0\ (d=0)$. The learner is a
lookup table and, **at unseen states, takes action 0** (it does not recover).

```python
import numpy as np

D_MAX, P_DRIFT = 5, 0.002


def step(d, a, rng):
    drift = 1 if rng.random() < P_DRIFT else 0
    return int(np.clip(d + a + drift, 0, D_MAX))


def expert(d):
    return -1 if d > 0 else 0
```

Run two experiments.

**Experiment A (error-model simulation).** Skip learning and simulate the theory's two error models
directly. The BC model is "leave the track with probability $\epsilon$ at $d=0$ and never recover
afterwards"; the DAgger model is "err with probability $\epsilon$ at every state but recover from
off-track states".

**Experiment B (actual learning).** Train BC and DAgger with the same expert query budget (20
labels, 10 iterations). BC samples states uniformly from **expert** trajectories; DAgger samples
them uniformly from **learner** trajectories.

**Acceptance criteria** — all four must hold.

1. **Order in experiment A**: with $\epsilon = 10^{-3}$ and $T \in \{20,40,80,160\}$, the log-log
   regression slope is BC $\in [1.8,\,2.15]$ and DAgger $\in [0.9,\,1.1]$ (measured $1.906$ and
   $0.989$ over 4,000 repetitions).
2. **Constants in experiment A**: over the same range, BC's cost lies within $\pm15\%$ of
   $\tfrac12\epsilon T^2$ and DAgger's within $\pm15\%$ of $\epsilon T$ (measured BC
   $0.2045/0.2 = 1.02$ and $12.376/12.8 = 0.97$; DAgger $0.6462/0.64 = 1.01$).
3. **Order in experiment B**: for $T \in \{10,\dots,320\}$ over 800 runs, the log-log slope of the
   regret is BC $\in [1.8,\,2.2]$ and DAgger $\in [0.8,\,1.3]$ (measured $1.990$ and $1.077$).
4. **Gap in experiment B**: at $T = 320$, BC's regret is **at least ten times** DAgger's (measured
   $76.86$ versus $2.54$, a factor of $30$).

**Baselines**: ⓐ the expert's own cost (measured $0.64$ at $T=320$) — the reference point for
regret. ⓑ the theoretical values $\tfrac12\epsilon T^2$ and $\epsilon T$ of experiment A — that is
what criterion 2 compares against. ⓒ optional: rerun with DAgger's sampling changed to "the first
$k$ states of the trajectory" and confirm that **the advantage disappears** (in the measurement
DAgger's slope rose from $1.08$ to $2.22$, matching BC). This sanity check is what fixes the meaning
of criterion 3.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| DAgger's slope is close to 2 | only the **beginning** of the learner's trajectories was labelled, so off-track states were never seen | print a histogram of the labelled states — no $d\ge1$ at all means this bug |
| BC's slope is close to 1 | $\epsilon T \gtrsim 1$, so the cost saturated at $T$ | print $\epsilon T$; with $p=0.002$ it needs $T\le 320$ |
| The regret of either method is negative | the expert's cost was measured with different random numbers | fix the evaluation seed **independently of** the policy (the same disturbance sequence) |
| The regret swings a lot between seeds | too few runs; the events are rare because $p$ is small | use at least 800 runs and print the standard error |
| BC's constant in experiment A is twice too large | it was compared against $\epsilon T^2$ instead of $\tfrac12\epsilon T^2$ | use the $T(T-1)/2$ of (5) |
| DAgger is **worse** than BC | only the last iteration's data was used, without aggregation | check that the dataset grows with each iteration |

## Open problems

- **(open problem) Handling covariate shift without a queryable expert** — DAgger's guarantee rests
  entirely on H5, the ability to query the expert at arbitrary states. On a real robot, putting a
  human expert into an off-track state is expensive, yields poor labels and may be unsafe. No method
  is known that achieves the same linear order from offline data alone. Current approaches:
  imitation as occupancy matching ([GAIL](https://arxiv.org/abs/1606.03476)), conservative offline
  learning (`c8-offline-rl`). What is missing: an assumption that buys $O(\epsilon T)$ without
  queries.
- **(open problem) Defining the error for a multi-modal expert** — $\epsilon$ is defined with a 0-1
  loss, but a human expert uses several correct actions at the same state. A regression loss that
  averages them produces an **unexecutable average** between modes. Current approaches: modelling
  the distribution directly with a [diffusion policy](https://arxiv.org/abs/2303.04137), exploiting
  temporal correlation with action chunking ([ACT](https://arxiv.org/abs/2304.13705)). What is
  missing: an $\epsilon$ suited to multi-modal experts and a matching compound-error bound.
- **(open problem) Choosing the principle that closes reward ambiguity** — closing the degrees of
  freedom of R4 with maximum entropy is an **empirical assumption** that the expert is
  Boltzmann-rational. If human suboptimality does not take that form, the recovered reward is
  systematically wrong. Current approaches:
  [MaxEnt IRL](https://cdn.aaai.org/AAAI/2008/AAAI08-227.pdf),
  [maximum margin](https://doi.org/10.1145/1015330.1015430). What is missing: a verifiable model of
  human suboptimality.
- **(open problem) Detecting the failure of an imitation policy at runtime** — BC fails outside its
  distribution, yet the policy itself does not know that. Attaching out-of-distribution detection
  and conformal prediction has been tried, but there is no guarantee inside the control loop.
  Current approaches: [Sinha et al. 2022](https://arxiv.org/abs/2212.14020),
  [conformal prediction](https://arxiv.org/abs/2107.07511). What is missing: a detector that signals
  the moment of departure within $O(1)$ steps, with a guarantee.

## Concept check

Run `rc quiz c8-imitation-learning`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: which two factors multiply to give the $T^2$ of BC's bound; whether that order
is an artifact of the proof; the one-line reason DAgger beats BC; whether observing the optimal
policy identifies the reward; and what the MaxEnt IRL log-likelihood gradient is a difference of.

## How to study this stage

1. **Do the decomposition by hand (60 min)** — write (4), the "decomposition by first disagreement
   time", from a blank page. The single line where the coupling makes the state distributions equal
   is the whole thing. Then compute $\sum_t(T-t) = T(T+1)/2$ yourself and see where the $T^2$ comes
   from.
2. **Build the lower bound first (45 min)** — design the two-state MDP of R2 yourself and check why
   it collapses without absorption (problem P5). Whether you can build the **lower** bound, not the
   upper one, is what separates understanding here.
3. **Reread DAgger through the performance difference lemma (60 min)** — transcribe R3 of
   `c8-policy-gradient` into finite-horizon form and point out where $u$ replaces $(T-t)$. Keeping
   one task with $u = \Theta(T)$ in mind dispels the misconception that DAgger is always better.
4. **Separate the orders experimentally (120 min)** — pass experiment A (the error models) of the
   reproduction task before moving to experiment B (actual learning). In the other order you cannot
   tell whether a slope that is not 2 is due to theory or to the implementation. Finally, change
   DAgger's sampling to "the start of the trajectory" and watch **the advantage disappear**.
5. **Close the IRL ambiguity by derivation (75 min)** — write the telescoping of potential shaping
   (P7), then derive the Lagrange dual of R5 yourself. Deriving once **why entropy maximization
   produces an exponential family** makes the soft Bellman equation of `c8-control-as-inference` look
   like the same structure.
6. **The three papers and the open problems (180 min)** — Ross & Bagnell 2010 (upper and lower
   bounds) → Ross et al. 2011 (DAgger) → Ziebart et al. 2008 (MaxEnt). Write the one-page note for
   each; this is **not** optional. Finally pick the queryable-expert open problem and write a
   paragraph on how H5 could be relaxed on a real robot.

**Passing bar**: you can derive (1) from a blank page and sketch the lower-bound construction, state
the role of $u$ in DAgger's (2), derive potential shaping and the MaxEnt solution, and you hold code
satisfying the four acceptance criteria plus notes on the three papers.
