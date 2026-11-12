---
id: c8-mdp-pomdp-bellman
lang: en
title: MDPs, POMDPs and Bellman optimality
summary: >-
  Prove that the Bellman optimality operator is a sup-norm contraction, and derive the
  convergence rate and the stopping rule of value iteration and policy iteration down to a
  form you can code mechanically. Then turn a partially observable problem into a belief MDP
  and show, via alpha-vector backups, that the finite-horizon POMDP value function is
  piecewise-linear and convex (PWLC).
objectives:
  - Prove that the Bellman optimality operator is a $\gamma$-contraction in the sup norm with no missing steps.
  - Reconstruct the existence and uniqueness of $V^\*$ and the optimality of the greedy policy from contraction plus the Banach fixed-point theorem.
  - Derive the value-iteration error bound and the stopping rule $\lVert V_{k+1}-V_k \rVert_\infty < \epsilon(1-\gamma)/(2\gamma)$.
  - Prove monotone improvement and finite termination of policy iteration and relate it to value iteration.
  - Convert a POMDP into a belief MDP and write the PWLC property of the finite-horizon value function with alpha vectors.
  - Point out which step collapses first when the discount or bounded-reward assumption is dropped.
tags: [mdp, pomdp, bellman, dynamic-programming, contraction, research]
---

# MDPs, POMDPs and Bellman optimality

## Setup and notation

This is the first lesson of module C8, and every later lesson (policy gradient, value-based,
model-based, offline) reuses the operator notation and the contraction argument fixed here.
The following is **recommended** background — the platform does not lock the lesson, and the
self-diagnostic below is how you decide for yourself:

- Analysis: complete metric spaces, the Banach fixed-point theorem, the sup norm, monotone convergence.
- Linear algebra: spectral radius, the Neumann series for $(I - \gamma P)^{-1}$.
- Probability: conditional expectation, the Markov property, sufficient statistics.
- Optimal-control DP is **not** required — the correspondence with finite-horizon LQR comes back
  in `c8-control-as-inference`.

Notation (fixed for all of module C8):

| Symbol | Meaning |
|---|---|
| $\mathcal{S}, \mathcal{A}$ | finite state and action sets. $\lvert \mathcal{S} \rvert = n$, $\lvert \mathcal{A} \rvert = m$ |
| $P(s' \mid s, a)$ | transition probability. In matrix form $P^\pi \in \mathbb{R}^{n \times n}$, $(P^\pi)_{ss'} = \sum_a \pi(a \mid s) P(s' \mid s,a)$ |
| $r(s,a)$ | reward, with $\lvert r(s,a) \rvert \le R_{\max} < \infty$ (assumption **A1**) |
| $\gamma$ | discount factor, $0 \le \gamma < 1$ (assumption **A2**) |
| $\pi(a \mid s)$ | stationary stochastic policy; a deterministic policy is $\pi : \mathcal{S} \to \mathcal{A}$ |
| $V^\pi \in \mathbb{R}^n$ | $V^\pi(s) = \mathbb{E}^\pi\!\left[\sum_{t\ge0} \gamma^t r(s_t,a_t) \mid s_0 = s\right]$ |
| $V^\*, Q^\*$ | optimal value functions, $V^\*(s) = \sup_\pi V^\pi(s)$ |
| $T^\pi, T^\*$ | the Bellman expectation and optimality operators, (1) and (2) below |
| $\lVert v \rVert_\infty$ | $\max_s \lvert v(s) \rvert$. Every contraction in this lesson is in this norm |
| $b \in \Delta(\mathcal{S})$ | belief, with $b(s) \ge 0$ and $\sum_s b(s) = 1$ |
| $\mathcal{O}, O(o \mid s', a)$ | observation set and observation model |
| $\alpha \in \mathbb{R}^n$ | alpha vector, $V(b) = \max_\alpha \langle \alpha, b \rangle$ |

Define two operators. For $v \in \mathbb{R}^n$,

$$
(T^\pi v)(s) = \sum_a \pi(a \mid s)\Big[r(s,a) + \gamma \sum_{s'} P(s' \mid s,a)\, v(s')\Big], \tag{1}
$$

$$
(T^\* v)(s) = \max_{a \in \mathcal{A}} \Big[r(s,a) + \gamma \sum_{s'} P(s' \mid s,a)\, v(s')\Big]. \tag{2}
$$

The policy that is greedy with respect to $v$ is the deterministic policy
$\pi_v(s) \in \arg\max_a [\,\cdot\,]$ attaining the maximum in (2). Ties may be broken
arbitrarily; nothing below changes.

## Self-diagnostic before starting

Since this is the module's first lesson, it checks the background for all of C8. All five items
are **gradeable** — solve them on paper in ten minutes and compare with the answers. Three or
more correct: start the module. Two or fewer: look at the prerequisite lesson named in the item
first. Prerequisites are **recommended**, not locked.

**D1 (linear solve, prerequisite: `r0-linear-algebra-decompositions`)** For the Markov reward
process with $\gamma = 0.9$, $P = \begin{bmatrix} 0.5 & 0.5 \\ 0 & 1\end{bmatrix}$ and
$r = (2, 0)^\top$, compute the first entry of $V = (I - \gamma P)^{-1} r$.
*Answer*: $V(s_0) = 2/0.55 = 40/11 = 3.636363\ldots$, $V(s_1) = 0$. Tolerance $10^{-9}$.

**D2 (contraction, prerequisite: analysis — the Banach fixed-point theorem)** What is the
smallest constant $L$ for which $\lvert \max_a f(a) - \max_a g(a) \rvert \le L \max_a \lvert f(a) - g(a)\rvert$
holds?
*Answer*: $L = 1$. (Equality is attained when $f$ and $g$ are maximized at the same $a$.)

**D3 (geometric series, prerequisite: `r0-estimation-theory` or S&B ch.3)** With
$\lvert r \rvert \le 2$ and $\gamma = 0.95$, what is the largest possible $\lvert V^\pi(s) \rvert$?
*Answer*: $2/(1-0.95) = 40$. Tolerance $10^{-9}$. (That bound is everything A1 contributes to (4).)

**D4 (convexity, prerequisite: `r0-convex-optimization`)** On the simplex $b = (p, 1-p)$, find the
$p$ at which the two linear pieces of
$f(b) = \max\big(\langle (1,0), b\rangle,\ \langle (0,2), b\rangle\big)$ cross, and the value of
$f$ there.
*Answer*: $p = 2/3$, $f = 2/3$. Tolerance $10^{-9}$. ($f$ is piecewise linear and convex — the
PWLC property of R4 is exactly this structure in $n$ dimensions.)

**D5 (Bayes update, prerequisite: `r0-estimation-theory`)** The state does not change and
$\Pr(o \mid s_0) = 0.9$, $\Pr(o \mid s_1) = 0.3$. Starting from $b(s_0) = 0.5$, what is
$b'(s_0)$ after one observation of $o$?
*Answer*: $0.45/0.6 = 0.75$. Tolerance $10^{-12}$.

## Key results

The bracket gives the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the Bellman optimality operator is a $\gamma$-contraction with a unique fixed point equal
  to $V^\*$) [D3]** — under A1 and A2, for all $u, v$,
  $$\lVert T^\* u - T^\* v \rVert_\infty \le \gamma \lVert u - v \rVert_\infty, \tag{3}$$
  so there is exactly one $v$ with $T^\* v = v$. That $v$ is $V^\*$, and the greedy policy
  $\pi_v$ is **optimal among all policies and is stationary and deterministic**. The same holds
  for $T^\pi$ and $V^\pi$ for each fixed $\pi$.
- **R2 (convergence rate and stopping rule of value iteration; finite termination of policy
  iteration) [D3]** — with $V_{k+1} = T^\* V_k$,
  $$\lVert V_k - V^\* \rVert_\infty \le \gamma^k \lVert V_0 - V^\* \rVert_\infty, \tag{4}$$
  and if $\pi_k$ is greedy with respect to $V_k$ then
  $$\lVert V^{\pi_k} - V^\* \rVert_\infty \le \frac{2\gamma}{1-\gamma}\,\lVert V_{k+1} - V_k \rVert_\infty. \tag{5}$$
  Hence stopping when $\lVert V_{k+1} - V_k \rVert_\infty < \epsilon(1-\gamma)/(2\gamma)$ makes
  $\pi_k$ an $\epsilon$-optimal policy. Policy iteration satisfies $V^{\pi_{k+1}} \ge V^{\pi_k}$
  at every iteration and, since there are only $m^n$ deterministic policies, **terminates exactly
  after finitely many iterations**.
- **R3 (POMDP to belief MDP) [D2]** — the belief $b$ is a sufficient statistic for the whole
  history $(a_0, o_1, \dots, o_t)$, and with the transition $\tau(b,a,o)$ and reward
  $\rho(b,a) = \langle b, r(\cdot,a)\rangle$ on $\Delta(\mathcal{S})$ the POMDP is equivalent to an
  MDP with a **continuous state space**.
- **R4 (the finite-horizon POMDP value function is PWLC) [D2]** — for horizon $h$ there is a
  finite set $\Gamma_h \subset \mathbb{R}^n$ with
  $$V_h(b) = \max_{\alpha \in \Gamma_h} \langle \alpha, b \rangle, \tag{6}$$
  i.e. the value function is piecewise linear and convex, and $\Gamma_h$ is generated from
  $\Gamma_{h-1}$ by an alpha-vector backup.
- **R5 (the complexity wall) [D1]** — deciding the optimal policy of a finite-horizon POMDP is
  PSPACE-complete (Papadimitriou & Tsitsiklis 1987), and deciding the existence of an
  $\epsilon$-optimal infinite-horizon policy is in general undecidable (Madani et al. 2003). The
  concrete face of this is that $\lvert \Gamma_h \rvert$ grows like
  $\lvert \mathcal{A} \rvert \lvert \Gamma_{h-1} \rvert^{\lvert \mathcal{O} \rvert}$ per horizon step.

## Derivation

### R1 — from contraction to optimality

**Step 1: the Lipschitz property of max.** For any bounded $f, g : \mathcal{A} \to \mathbb{R}$,

$$
\big\lvert \max_a f(a) - \max_a g(a) \big\rvert \le \max_a \lvert f(a) - g(a) \rvert. \tag{7}
$$

Proof: pick $a^\star \in \arg\max_a f(a)$; then
$\max_a f - \max_a g \le f(a^\star) - g(a^\star) \le \max_a \lvert f - g\rvert$. Swapping the roles
of $f$ and $g$ gives the same bound in the other direction. (A1 is what makes the maxima exist.)

**Step 2: (3).** Fix $s$ and read the bracket of (2) as $f(a)$ and $g(a)$:

$$
\lvert (T^\* u)(s) - (T^\* v)(s) \rvert
  \overset{(7)}{\le} \max_a \gamma \Big\lvert \sum_{s'} P(s' \mid s,a)\,\big(u(s') - v(s')\big) \Big\rvert
  \le \max_a \gamma \sum_{s'} P(s' \mid s,a)\,\lVert u - v \rVert_\infty
  = \gamma \lVert u - v \rVert_\infty,
$$

where the last equality is $\sum_{s'} P(s' \mid s,a) = 1$. Taking the maximum over $s$ gives (3).
The same computation, without needing (7), makes $T^\pi$ a $\gamma$-contraction.

**Step 3: existence and uniqueness of the fixed point.** $(\mathbb{R}^n, \lVert\cdot\rVert_\infty)$
is complete, and by A1 the operator $T^\*$ maps bounded vectors to bounded vectors. The Banach
fixed-point theorem gives a unique $v^\star$ with $T^\* v^\star = v^\star$, and
$(T^\*)^k V_0 \to v^\star$ from any $V_0$.

**Step 4: $v^\star = V^\*$ and $\pi_{v^\star}$ is optimal.** Two directions.

(i) For any policy $\pi$, $T^\pi v^\star \le T^\* v^\star = v^\star$, because the maximum in (2)
dominates every action. $T^\pi$ is **monotone** ($u \le v \Rightarrow T^\pi u \le T^\pi v$, since
all coefficients in (1) are non-negative) and a $\gamma$-contraction, so applying $T^\pi$ $k$
times gives $(T^\pi)^k v^\star \le v^\star$, and as $k \to \infty$ the left side tends to $V^\pi$.
So $V^\pi \le v^\star$ for every $\pi$.

(ii) Put $\pi^\star := \pi_{v^\star}$. By definition $T^{\pi^\star} v^\star = T^\* v^\star = v^\star$,
i.e. $v^\star$ is a fixed point of $T^{\pi^\star}$. That fixed point is unique and equals
$V^{\pi^\star}$, so $V^{\pi^\star} = v^\star$.

Together, $v^\star = \max_\pi V^\pi = V^\*$, and the maximum is attained by a **stationary,
deterministic, Markov** policy $\pi^\star$. Allowing history-dependent or non-stationary policies
cannot do better — and that fact is why every later lesson may parameterize a policy as
$\pi(a \mid s)$ alone.

**Where the assumptions break.** At $\gamma = 1$ the final equality of step 2 becomes
$1 \cdot \lVert u-v \rVert_\infty$ and the contraction is gone. The fixed point is then not
unique: in an MDP whose rewards are all zero, $T^\* v = v$ is satisfied by **every constant
vector** (problem P5). And if A1 fails, so that $r$ is unbounded, then
$\lVert V_0 - V^\* \rVert_\infty = \infty$ makes (4) vacuous, and step 3's claim that $T^\*$
preserves a space of bounded functions does not even typecheck. The average-reward criterion
drops this contraction argument and rebuilds the theory on the span seminorm plus a unichain
assumption.

### R2 — rate and stopping rule

**(4)** follows by substituting $u = V_k$, $v = V^\*$ into (3), using $T^\* V^\* = V^\*$, and
iterating over $k$.

**(5)** is the bound you actually use. The point of the derivation is **which iterate the greedy
policy is read off**. If $\pi_k$ is greedy with respect to $V_k$, then by definition

$$
T^{\pi_k} V_k = T^\* V_k = V_{k+1}. \tag{8}
$$

Write $d_k := \lVert V_{k+1} - V_k \rVert_\infty$ and split the bound in two.

(a) Distance between the true value of $\pi_k$ and $V_{k+1}$. From $V^{\pi_k} = T^{\pi_k} V^{\pi_k}$
and (8),

$$
\lVert V^{\pi_k} - V_{k+1} \rVert_\infty = \lVert T^{\pi_k} V^{\pi_k} - T^{\pi_k} V_k \rVert_\infty
  \le \gamma \lVert V^{\pi_k} - V_k \rVert_\infty
  \le \gamma\big(\lVert V^{\pi_k} - V_{k+1} \rVert_\infty + d_k\big),
$$

hence $\lVert V^{\pi_k} - V_{k+1} \rVert_\infty \le \gamma d_k / (1-\gamma)$.

(b) Distance between $V_{k+1}$ and $V^\*$. By (3),
$\lVert V_{k+j+1} - V_{k+j} \rVert_\infty \le \gamma^j d_k$, so the telescoping series gives

$$
\lVert V_{k+1} - V^\* \rVert_\infty \le \sum_{j \ge 1} \lVert V_{k+j} - V_{k+j+1} \rVert_\infty
  \le d_k \sum_{j\ge1} \gamma^{j} = \frac{\gamma}{1-\gamma} d_k .
$$

Adding (a) and (b) with the triangle inequality gives (5). So stopping at
$d_k < \epsilon(1-\gamma)/(2\gamma)$ is the **mechanical test** for "I now hold an
$\epsilon$-optimal policy".

> **A common error**: measuring the loss of $\pi_{k+1}$ (greedy with respect to $V_{k+1}$) against
> $d_k$ breaks (8), so the first equality of (a) is unavailable and the bound picks up one more
> factor of $\gamma$ (problem P1). In code this one-index slip either loosens the stopping rule or
> silently invalidates it.

**Policy iteration.** Let $\pi' = \pi_{V^\pi}$ (greedy with respect to $V^\pi$). Then
$T^{\pi'} V^\pi = T^\* V^\pi \ge T^\pi V^\pi = V^\pi$. Applying monotonicity of $T^{\pi'}$
repeatedly gives $(T^{\pi'})^k V^\pi \ge V^\pi$, and as $k \to \infty$ the left side converges to
$V^{\pi'}$, so

$$
V^{\pi'} \ge V^\pi \quad \text{(componentwise)}. \tag{9}
$$

The moment $V^{\pi'} = V^\pi$ we have $V^\pi = T^\* V^\pi$, and uniqueness from R1 gives
$V^\pi = V^\*$. There are only $m^n$ deterministic policies and (9) improves **strictly** until
termination, so the loop is finite. The reason policy iteration takes under ten iterations in
practice, almost independently of $n$, is that each step is also a Newton step
(omitted: the Newton–Kantorovich reading in Puterman ch.6).

**Where the assumptions break.** With infinite state or action sets the "finitely many
deterministic policies" argument disappears and policy iteration loses finite termination (though
not convergence). And if policy evaluation is approximate, (9) can fail, so **some iterations make
the policy worse** — this is the oscillation of approximate policy iteration, the same root cause
as the divergence example in `c8-value-based-rl`.

### R3 — the belief MDP

A POMDP is $(\mathcal{S},\mathcal{A},P,r,\mathcal{O},O,\gamma)$. After action $a$ and observation
$o$ the belief is updated by Bayes' rule:

$$
b'(s') = \tau(b,a,o)(s') = \frac{O(o \mid s',a) \sum_s P(s' \mid s,a)\, b(s)}{\Pr(o \mid b,a)},
  \qquad \Pr(o \mid b,a) = \sum_{s'} O(o \mid s',a)\sum_s P(s'\mid s,a)\,b(s). \tag{10}
$$

**The line that establishes sufficiency.** Let $h_t = (a_0,o_1,\dots,a_{t-1},o_t)$. Equation (10)
shows that $b_t$ is determined by $b_{t-1}, a_{t-1}, o_t$ alone, so $b_t$ is a function of $h_t$.
Conversely, the distribution of the future is
$\Pr(s_{t+1}, o_{t+1} \mid h_t, a_t) = \sum_{s_t} \Pr(s_t \mid h_t) P(s_{t+1}\mid s_t,a_t)
O(o_{t+1}\mid s_{t+1},a_t)$ with $\Pr(s_t \mid h_t) = b_t(s_t)$, so **$h_t$ carries no information
beyond $b_t$**. Therefore $(\Delta(\mathcal{S}), \mathcal{A}, \tau, \rho, \gamma)$ is Markov with
reward $\rho(b,a) = \sum_s b(s) r(s,a)$, and R1 applies verbatim to it:

$$
V^\*(b) = \max_a \Big[ \rho(b,a) + \gamma \sum_{o} \Pr(o \mid b,a)\, V^\*\big(\tau(b,a,o)\big) \Big]. \tag{11}
$$

**Where the assumptions break.** Finiteness of $\mathcal{S}$ is what makes $b$ a point of a
finite-dimensional simplex. For continuous states $b$ is a **measure** and (10) becomes a measure
update; approximating it with a particle filter makes the effective sample size collapse when the
observation space is continuous (see `c8-model-based-world-models` and Sunberg & Kochenderfer
2017). Also (10) is undefined for observations with $\Pr(o \mid b,a) = 0$, so an implementation
needs an explicit zero-division branch.

### R4 — PWLC and alpha vectors

At $h = 0$, $V_0(b) = 0 = \langle 0, b\rangle$, so $\Gamma_0 = \{0\}$ and (6) holds. Assume
$V_{h-1}(b) = \max_{\alpha \in \Gamma_{h-1}} \langle \alpha, b\rangle$ and expand one step of (11).
The key is that $\Pr(o \mid b,a)\,\tau(b,a,o)(s')$ cancels the denominator of (10):

$$
\Pr(o\mid b,a)\, \big\langle \alpha, \tau(b,a,o) \big\rangle
  = \sum_{s'} \alpha(s')\, O(o \mid s',a) \sum_s P(s'\mid s,a)\, b(s)
  = \big\langle g_{a,o,\alpha},\, b \big\rangle, \tag{12}
$$

with $g_{a,o,\alpha}(s) := \sum_{s'} P(s'\mid s,a)\, O(o\mid s',a)\, \alpha(s')$. In other words,
**the nonlinearity in the belief disappears and only terms linear in $b$ remain.** Hence

$$
V_h(b) = \max_a \Big[ \langle r_a, b\rangle + \gamma \sum_o \max_{\alpha \in \Gamma_{h-1}}
  \big\langle g_{a,o,\alpha}, b \big\rangle \Big], \tag{13}
$$

and since maxima and sums of linear functions are again piecewise linear and convex, so is the
result. Writing out the generating rule,

$$
\Gamma_h = \Big\{\, r_a + \gamma \sum_{o} g_{a,o,\alpha_o} \;:\; a \in \mathcal{A},\;
  (\alpha_o)_{o \in \mathcal{O}} \in \Gamma_{h-1}^{\mathcal{O}} \,\Big\}, \tag{14}
$$

so $\lvert \Gamma_h \rvert \le m \lvert \Gamma_{h-1}\rvert^{\lvert \mathcal{O}\rvert}$. This
doubly exponential blow-up is the complexity of R5, and pruning dominated alpha vectors with an LP
is where the real work of classical POMDP solvers goes (Smallwood & Sondik 1973; Kaelbling et al.
1998 §4).

**Where the assumptions break.** (6) yields a finite $\Gamma_h$ only for a **finite horizon**. In
the infinite-horizon case $V^\*$ is still convex but is not exactly representable by finitely many
alpha vectors (in general countably many, or not representable at all). So infinite-horizon POMDPs
are treated only up to $\epsilon$, and even that runs into the undecidability of R5. Rewards that
are nonlinear in the belief — for instance directly rewarding entropy reduction in active
perception — break the cancellation in (12) and lose the PWLC property; such a $\rho$ has to be
remodelled as convex pieces.

## Proof sketch

### R1 — contraction mapping and optimality [D3]

**Hypotheses** H1: $\lvert r \rvert \le R_{\max} < \infty$. H2: $0 \le \gamma < 1$.
H3: $\mathcal{S}, \mathcal{A}$ finite (or $\mathcal{A}$ compact with $r$ continuous).
**Conclusions** C1: $T^\*$ is a $\gamma$-contraction in $\lVert\cdot\rVert_\infty$. C2: a unique
fixed point exists. C3: that fixed point is $V^\*$ and the greedy policy is optimal.

**Strategy**: contraction mapping plus the Banach fixed-point theorem; optimality comes from
**monotonicity**, which supplies the two inequalities.

1. Show (7) — max is 1-Lipschitz in the sup norm. Uses: H3 (the maxima exist).
2. Factor out $\gamma$ using the fact that $P(\cdot\mid s,a)$ is a probability distribution → C1.
   Uses: H2.
3. Apply Banach using completeness of $\mathbb{R}^n$ and H1 → C2.
4. Monotonicity of $T^\pi$ gives $V^\pi \le v^\star$ for every $\pi$, with equality for the greedy
   policy → C3. Uses: the non-negativity of the coefficients in (1).

**Delete one hypothesis**: relaxing H2 to $\gamma = 1$ makes the contraction factor 1 in step 2,
Banach no longer applies, and C2 becomes **false** (every vector shifted by a constant is a fixed
point). Dropping H1 means $T^\*$ does not preserve the space of bounded functions, so step 3 is
meaningless. Dropping compactness of $\mathcal{A}$ in H3 means the maximum may not be attained, so
a greedy policy may not exist and C3 weakens to an $\epsilon$-greedy statement.

Omitted: the extension to continuous states and unbounded rewards is rewritten as a contraction in
a weighted sup norm $\lVert v \rVert_w = \sup_s \lvert v(s)\rvert/w(s)$. See Blackwell 1965 and
Puterman ch.6.10.

### R2 — rate and termination [D3]

**Hypotheses** H1–H3 (as above) plus H4: policy evaluation is **exact**, i.e.
$V^\pi = (I-\gamma P^\pi)^{-1} r^\pi$.
**Conclusions** C1: (4). C2: (5) and the stopping rule. C3: policy iteration terminates exactly
within $m^n$ iterations.

**Strategy**: iterate the contraction (C1); telescoping series plus the triangle inequality (C2);
monotone improvement plus a ladder argument on a finite set (C3).

1. Substitute $V^\*$ into (3) and induct → C1.
2. Read the greedy policy off $V_k$ so that $T^{\pi_k} V_k = V_{k+1}$. This single line is what
   makes the first equality of (a) possible. Uses: (8).
3. (a) $\lVert V^{\pi_k} - V_{k+1}\rVert \le \gamma d_k/(1-\gamma)$ and
   (b) $\lVert V_{k+1} - V^\*\rVert \le \gamma d_k/(1-\gamma)$; add them → (5) → C2.
4. Monotonicity of $T^{\pi'}$ gives (9). Equal values mean a fixed point of $T^\*$, hence optimal.
   Strict improvement on a finite policy set happens finitely often → C3. Uses: H4.

**Delete one hypothesis**: dropping H4 (exact evaluation) breaks (9), so policy iteration is no
longer monotone, and the performance bound for approximate policy iteration becomes
$\lVert V^{\pi_k} - V^\*\rVert \le 2\gamma\epsilon_{\text{eval}}/(1-\gamma)^2$ — note the
**$(1-\gamma)^{-2}$**. That exponent keeps reappearing throughout module C8 (model-error
propagation, the distribution-shift bounds of offline RL).

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Re-derive (5) for $\pi_{k+1}$ (greedy with respect to $V_{k+1}$). State
how many factors of $\gamma$ the bound picks up, and compute how much that changes the stopping
threshold at $\gamma = 0.99$.
*Solution sketch*: since $T^{\pi_{k+1}} V_{k+1} = T^\* V_{k+1} = V_{k+2}$, the quantity playing the
role of (a) becomes $d_{k+1} \le \gamma d_k$. The bound turns into $2\gamma^2 d_k/(1-\gamma)$, so
the threshold shrinks by a factor of $\gamma$. At $\gamma = 0.99$ the ratio of thresholds is
$0.99$ — small-looking, but the iteration count enters logarithmically.

**P2 (proof, ★★★, R1·R2)** Show that policy iteration dominates value iteration: starting from the
same $V_0$ with $V_0 \le V^{\pi_0}$, prove $V_k^{\text{VI}} \le V^{\pi_k}$ for all $k$.
*Strategy and key inequality*: derive $T^\* u \le T^{\pi_u} v$ from $u \le v$ (definition of greedy
plus monotonicity) and push it through by induction. The crux is
$T^\* V_k \le T^{\pi_k} V^{\pi_k} = V^{\pi_k}$. The expansion is withheld.

**P3 (numerical, ★, R1·R2)** A two-state, two-action MDP with $\gamma = 0.9$: in $s_0$, action
$a_0$ stays in $s_0$ with $r=1$, and action $a_1$ moves to $s_1$ with probability $0.8$ (otherwise
stays) with $r=0$. In $s_1$, action $a_0$ moves to $s_0$ with $r=0$, and $a_1$ stays in $s_1$ with
$r=2$. Compute $V^\*$ and the optimal policy, and the number of backups value iteration started at
$V_0 = 0$ needs to satisfy the stopping rule with $\epsilon = 10^{-3}$.
*Answer*: $V^\*(s_1) = 2/(1-0.9) = 20$ and $V^\*(s_0) = 14.4/0.82 = 17.56097561\ldots$ (tolerance
$10^{-9}$); the optimal policy is $a_1$ in both states. The stopping threshold is
$\epsilon(1-\gamma)/(2\gamma) = 5.5555\ldots\times10^{-5}$ and the number of backups is **101**
(defined as the first $k$ at which $d_k$ drops below the threshold).
Check: substitute $V^\*$ into (2) and verify both sides agree to $10^{-12}$, and that
$\lVert V^{\pi^\*} - V^\* \rVert_\infty < 10^{-12}$, where $V^{\pi^\*}$ is obtained by solving
$(I - \gamma P^{\pi^\*})^{-1} r^{\pi^\*}$ directly.

**P4 (implementation, ★★, R2)** Write value iteration and exact policy iteration, factoring the
stopping rule and the $\epsilon$-optimality test into their own functions. Policy evaluation must
be a linear solve.
*Rubric*: ⓐ the stopping rule uses the constant of (5) rather than a hard-coded iteration count;
ⓑ the two methods agree on $V^\*$ to $10^{-9}$; ⓒ the greedy policy is read off $V_k$ (the trap of
P1); ⓓ the tie-breaking rule is documented; ⓔ a plot shows the iteration count growing like
$O\big((1-\gamma)^{-1}\log(1/\epsilon)\big)$ as $\gamma \to 1$.

**P5 (counterexample, ★★, R1)** Construct an MDP in which (3) fails at $\gamma = 1$ and the fixed
point is not unique. Then explain in one paragraph why the claim "with all-negative rewards the
fixed point is unique even at $\gamma = 1$" is false in general.
*Property checklist*: ⓐ if every state is absorbing and $r \equiv 0$, every constant vector is a
fixed point; ⓑ confirm the contraction factor is exactly 1 via the equality case of (7);
ⓒ identify the path along which, even with negative rewards, the value of an absorbing state can
go to $-\infty$, breaking the boundedness that A1 supplies; ⓓ note that the fix is not discounting
but either a properness assumption on policies or the span seminorm.

**P6 (paper, ★★, R3·R4)** Read §3–4 of Kaelbling et al. 1998 together with Smallwood & Sondik
1973, and write, as a formula in $n, m, \lvert\mathcal{O}\rvert, h$, the scale at which running (14)
without alpha-vector pruning exhausts memory. Then find three pieces of information missing for
reproduction.
*Grading rubric*: writing the doubly exponential
$m \lvert\Gamma_{h-1}\rvert^{\lvert\mathcal{O}\rvert}$ correctly and giving a concrete instance
(e.g. $m=3$, $\lvert\mathcal{O}\rvert=3$, $h=5$) passes. For the missing information, naming three
of: the pruning LP's tolerance, tie handling, the initial belief distribution, random seeds.
Writing only "it is computationally expensive" fails.

**P7 (numerical, ★, R3)** A two-state POMDP in which the state never changes ($P = I$) and
$\Pr(o_0 \mid s_0) = 0.85$, $\Pr(o_0 \mid s_1) = 0.15$. Starting from $b(s_0) = 0.5$, compute
$b(s_0)$ after observing $o_0$ twice and three times, as a fraction and as a decimal.
*Answer*: once $17/20 = 0.85$; twice $289/298 = 0.969798657718\ldots$; three times
$4913/4940 = 0.994534412955\ldots$ (tolerance $10^{-12}$).
Check: verify that $\Pr(o_0 \mid b) = 0.85b + 0.15(1-b)$ matches the denominator of (10), and that
the log-odds of $b$ against $1-b$ grow linearly by $\log(0.85/0.15)$ per observation.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read with Keshav's three passes, and attack questions 4, 5, 6 and 7 in
the third pass.

1. **Blackwell, "Discounted dynamic programming" (1965, Ann. Math. Statist.)** — role:
   `seminal`. <https://doi.org/10.1214/aoms/1177700285>
   Why read it: the contraction argument of R1 and the claim that a stationary deterministic
   optimal policy exists originate here. Read §2–3 only.
   Extra questions: ⓐ how do the author's boundedness and measurability assumptions differ from
   A1 and H3 here? ⓑ what does Blackwell optimality (optimal simultaneously for all $\gamma$)
   require beyond optimality at a fixed $\gamma$?
2. **Smallwood & Sondik, "The optimal control of partially observable Markov processes over a
   finite horizon" (1973, Operations Research)** — role: `seminal`.
   <https://doi.org/10.1287/opre.21.5.1071>
   Why read it: the PWLC property of R4 and the alpha-vector backup (14) come from this paper.
   Extra questions: ⓐ what is the authors' definition of a "dominated" alpha vector that the
   pruning step removes? ⓑ which lemma breaks the moment the finite horizon is pushed to infinity?
3. **Kaelbling, Littman & Cassandra, "Planning and acting in partially observable stochastic
   domains" (1998, Artificial Intelligence)** — role: `standard`.
   <https://doi.org/10.1016/S0004-3702(98)00023-X> (focus on §3–4)
   Why read it: this is the paper that fixed the standard vocabulary and experimental design for
   the belief-MDP conversion (R3) and POMDP planning.
   Extra questions: ⓐ which part of the bound in (14) does the reported cost of the witness
   algorithm actually reduce? ⓑ moving the paper's experimental scale to a 2026 robot problem
   where observations are images, what fails first?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation? (4) what is guaranteed and **what is not**?
(5) independent and dependent variables, and the baselines — were they tuned fairly? (6) does the
metric match the claim, and are variance and seeds reported? (7) what information needed for
reproduction is missing? (8) if the result were wrong, which assumption would you doubt first?
(9) compute and memory cost, and real-time feasibility? (10) what would you change to go beyond
this paper in a year?

## Reproduction task

**Tier R1 (numerical check).** Compute budget: under one minute on a laptop CPU, under 200 MB,
numpy only.

Check that the $\gamma^k$ decay of (4) holds **within the theoretical bound and nearly tightly**,
and that the stopping rule of (5) really delivers an $\epsilon$-optimal policy. The input is the
generator script the lesson provides (no user data needed):

```python
import numpy as np


def random_mdp(n_s=100, n_a=5, gamma=0.99, seed=0):
    """Sparse-reward random MDP: Dirichlet(0.1) transitions, reward on 30% of pairs."""
    rng = np.random.default_rng(seed)
    p = rng.dirichlet(np.full(n_s, 0.1), size=(n_s, n_a))
    r = rng.uniform(0.0, 1.0, size=(n_s, n_a)) * (rng.random((n_s, n_a)) < 0.3)
    return p, r, gamma
```

**Acceptance criteria** — all four must hold. Obtain $V^\*$ by exact policy iteration (policy
evaluation via `np.linalg.solve`) and start value iteration from $V_0 = 0$.

1. **Cumulative bound**: with $e_k := \lVert V_k - V^\* \rVert_\infty$ and
   $e_0 = \lVert V^\* \rVert_\infty$,
   $\max_{1 \le k \le 2000,\ e_k > 10^{-6}} e_k / (\gamma^k e_0) \le 1$, and at the same time that
   maximum is $\ge 0.9$ (the bound must be tight, not vacuous).
2. **Per-step ratio**: for every $k$ with $e_k > 10^{-6}$, $e_{k+1}/e_k \le \gamma + 10^{-8}$.
   (The $10^{-8}$ is double-precision slack: when $e_k$ is around $10^{-6}$, the $\sim 10^{-13}$
   rounding of a single backup shows up in the ratio at the $10^{-7}$ level. Without the slack,
   criterion 2 is false.)
3. **Stopping rule**: for $\epsilon \in \{10^{-3}, 10^{-6}\}$, stopping at
   $d_k < \epsilon(1-\gamma)/(2\gamma)$ yields $\lVert V^{\pi_k} - V^\* \rVert_\infty < \epsilon$
   ($\pi_k$ greedy with respect to $V_k$; $V^{\pi_k}$ by linear solve).
4. **Agreement of the two methods**: policy iteration terminates within 20 iterations, and the
   value-iteration solution from criterion 3 with $\epsilon = 10^{-6}$ agrees to
   $\lVert V^{\text{VI}} - V^\* \rVert_\infty < 10^{-6}$.

**Baselines**: ⓐ exact policy iteration — a linear solve, so it plays the role of ground truth.
ⓑ the same problem solved as an LP with `scipy.optimize.linprog`
($\min \sum_s v(s)$ subject to $v(s) \ge r(s,a) + \gamma \sum_{s'} P v$) — optional, but if all
three methods agree to $10^{-6}$ the chance of an implementation bug is essentially gone.

**Reference output** (numpy 2.x, `seed=0`, $\gamma=0.99$): policy iteration terminates in 5
iterations, $V^\* \in [57.21, 58.33]$, the maximum in criterion 1 is $\approx 0.994$, 1160 backups
to stop at $\epsilon=10^{-3}$ and 1848 at $\epsilon=10^{-6}$, with zero policy loss in both cases.
**The acceptance criteria are independent of the generator version, but these reference numbers are
not** — if the `dirichlet` stream of `np.random.Generator` changes, the numbers change, so judge by
the four criteria rather than by the numbers.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| Criterion 2 fails narrowly ($e_{k+1}/e_k = \gamma + 10^{-7}$) | numerical error in $V^\*$ itself contaminates small $e_k$ | raise the floor on $e_k$ to $10^{-6}$, recompute $V^\*$ as a double-precision linear solve and inspect the residual $\lVert (I-\gamma P^{\pi^\*})V^\* - r^{\pi^\*}\rVert_\infty$ |
| Criterion 3 fails | the greedy policy was read off $V_{k+1}$ (the trap of P1) | re-run with $\pi_k$ read off $V_k$ — the loss drops by a factor of $\gamma$ |
| The maximum in criterion 1 is below $0.9$ | $V_0 \ne 0$, or $e_0$ was not taken as $\lVert V_0 - V^\*\rVert$ | print $e_0$ and compare it with $\lVert V^\*\rVert_\infty$ |
| Policy iteration does not terminate | the policy oscillates on ties | fix $\arg\max$ to change only on strict improvement, or keep the first-index rule of `np.argmax` |
| Iteration is slow at $\gamma=0.999$ | the iteration count grows like $(1-\gamma)^{-1}$ | switch to policy iteration, whose iteration count is nearly insensitive to $\gamma$ |

## Open problems

- **(open problem) Guarantees for continuous-state, continuous-observation POMDPs** — R3 holds
  formally once beliefs are lifted to measures, but a particle approximation collapses all weight
  onto one particle when the observation space is continuous, driving the effective sample size to
  one. Online tree search with progressive widening restores consistency (current approach:
  [Sunberg & Kochenderfer 2017](https://arxiv.org/abs/1709.06196)), but no convergence rate is
  known when the observation density is a high-dimensional image. What is missing: a bound that
  carries belief-approximation error into policy loss for high-dimensional observations.
- **(open problem) Structural conditions that sidestep the POMDP complexity wall in robotics** —
  the finite horizon is PSPACE-complete
  ([Papadimitriou & Tsitsiklis 1987](https://doi.org/10.1287/moor.12.3.441)) and infinite-horizon
  $\epsilon$-optimality is undecidable
  ([Madani et al. 2003](https://doi.org/10.1016/S0004-3702(02)00378-8)). The structure that robot
  problems actually have — observations are usually informative, states live on a low-dimensional
  manifold, tasks are hierarchical — has not been **written down as assumptions** that buy
  polynomial-time guarantees. What is missing: a formal definition of "the POMDPs that are common
  in robotics".
- **(open problem) Is a learned belief representation a sufficient statistic?** — latent world
  models replace $b$ with a learned hidden state (current approach:
  [DreamerV3](https://arxiv.org/abs/2301.04104)). The sufficiency argument of R3 holds only for an
  **exact** model, so if the learned hidden state is not sufficient, doing DP on top of it means
  applying the Bellman equation to a problem that is not Markov. Detecting that defect at runtime
  under out-of-distribution inputs is also unsolved (current approach:
  [Sinha et al. 2022](https://arxiv.org/abs/2212.14020)). What is missing: a checkable proxy for
  sufficiency.
- **(open problem) The status of $\gamma$** — the discount factor is usually fixed for modelling
  convenience, yet the bound in (5) scales as $(1-\gamma)^{-1}$ and approximate policy iteration as
  $(1-\gamma)^{-2}$, so **reported performance is sensitive to the choice of $\gamma$**. How far the
  practice of tuning $\gamma$ as a hyperparameter makes comparisons meaningless has not been
  quantified (current approach to evaluation methodology:
  [Agarwal et al. 2021](https://arxiv.org/abs/2108.13264)). What is missing: a principle linking
  the task horizon to $\gamma$.

## Concept check

Run `rc quiz c8-mdp-pomdp-bellman`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: which property of the transition kernel the contraction argument actually
uses; the stopping threshold of value iteration in terms of $\epsilon$ and $\gamma$; whether the
infinite-horizon POMDP value function is exactly representable by finitely many alpha vectors; the
growth rate of the alpha-vector set in (14); and why approximate policy evaluation breaks the
monotone improvement of (9).

## How to study this stage

1. **Fix the operator notation first (30 min)** — copy (1) and (2) onto paper and verify the
   monotonicity and the contraction property of $T^\pi$ and $T^\*$ in one line each. The remaining
   seven lessons of C8 all run on these two operators.
2. **Rewrite (7) through (3) from a blank page (90 min)** — cover the text and reconstruct it. See
   for yourself where the argument stalls if you omit the 1-Lipschitz property of max. Read S&B
   ch.3–4 and LaValle ch.10 side by side as **the same result in different notation**.
3. **Derive the stopping rule by hand (60 min)** — derive (a) and (b) of (5) separately, then solve
   P1 so that the single line "read the greedy policy off $V_k$" becomes muscle memory. This trap
   is the most common silent bug in real implementations.
4. **See the tightness of the bound through code (75 min)** — run the reproduction task first at
   $\gamma = 0.9$ and watch how close the ratio of criterion 1 gets to $1$, then raise it to
   $\gamma = 0.999$ and watch the iteration count grow. The point is to meet the theoretical
   $(1-\gamma)^{-1}$ as a number.
5. **Read the three papers in chronological order (150 min)** — Blackwell (contraction) →
   Smallwood & Sondik (PWLC) → Kaelbling et al. (belief MDP and experiments). Write the one-page
   note for each paper; this is **not** optional. Question 4 ("what is not guaranteed") in
   particular connects directly to this lesson's open problems.
6. **End at what cannot be done (75 min)** — pick one of the four open problems and write a
   paragraph on why it is still open, then write down what breaks when the log-odds observation of
   P7 is scaled up to high-dimensional observations.

**Passing bar**: you can derive (3) and (5) from a blank page, say what breaks first at
$\gamma = 1$, write the growth rate of (14), and you hold code satisfying the four acceptance
criteria of the reproduction task plus notes on the three papers.
