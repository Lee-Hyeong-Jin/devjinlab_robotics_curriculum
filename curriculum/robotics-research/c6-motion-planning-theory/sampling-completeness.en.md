---
id: c6-sampling-completeness
lang: en
title: Sampling-based planning and probabilistic completeness
summary: >-
  Prove the probabilistic completeness of PRM and RRT all the way through, by a ball-covering plus
  binomial-tail argument. Derive, with explicit constants, that a positive clearance $\delta$ of the
  solution path makes the failure probability decay exponentially in the number of iterations, and
  then explain with the $\epsilon$-good and expansiveness assumptions why those constants are
  uselessly conservative in a narrow passage. The reproduction task measures the exponential decay
  directly and counts how the classical bound only wakes up $10^3$ times later than the planner
  actually succeeds.
objectives:
  - Turn a solution path of clearance $\delta$ into a ball cover and prove the one-step advance lemma with no missing steps.
  - Derive the failure-probability bounds of RRT and PRM with explicit constants (the ball count $m$ and the per-step probability $p$).
  - State separately what probabilistic completeness does not guarantee (optimality, finite-time termination, infeasibility detection).
  - Write down the definitions of $\epsilon$-goodness and $(\epsilon,\alpha,\beta)$-expansiveness and relate them to clearance-based bounds.
  - Demonstrate numerically the two reasons the classical bound is conservative (the ball-volume argument, and ignoring the Voronoi bias).
tags: [motion-planning, sampling-based, prm, rrt, probabilistic-completeness, narrow-passage, research]
---

# Sampling-based planning and probabilistic completeness

## Setup and notation

`c6-cspace-complexity` and `c6-combinatorial-gcs` are assumed. In particular, two results from them
are the starting point here: (a) $\mathcal{C}_{free}$ is **open**, so every free configuration has a
ball of positive clearance around it; (b) complete combinatorial planning is a tool for $d \le 3$.
Also assumed:

- Probability: the binomial distribution, Chernoff/Hoeffding-type tail bounds, the union bound,
  monotonicity of a measure. Martingales are not needed (recommended prerequisite
  `r0-estimation-theory`).
- Lebesgue measure on $\mathbb{R}^d$. Here $\zeta_d$ is the volume of the unit ball
  ($\zeta_2 = \pi$, $\zeta_3 = 4\pi/3$).

Notation (in addition to the module's):

| Symbol | Meaning |
|---|---|
| $\sigma$ | the solution path, of length $L = \ell(\sigma)$ |
| $\delta$ | the **clearance** of the solution path, $\min_t \operatorname{dist}(\sigma(t), \mathcal{C}_{obs}) > 0$ |
| $\eta$ | the RRT step size |
| $x_0, \dots, x_m$ | points placed along $\sigma$ at spacing $\eta/2$ |
| $B_i$ | $B(x_i, \eta/4)$ — the ball **the sample must land in** |
| $p$ | probability that one sample lands in a given ball, $\ge \zeta_d (\eta/4)^d / \mu(\mathcal{C}_{free})$ |
| $\mathcal{V}(q)$ | the set of free configurations visible from $q$ in a straight line |
| $\epsilon, \alpha, \beta$ | the expansiveness parameters (§R3) |
| $\gamma$ | the tolerated failure probability |

**The two algorithms.** Both "draw configurations at random and connect the collision-free ones",
but their structure differs.

- **PRM** — draw $n$ points **first**, connect every pair within distance $r$ by a straight line to
  build a roadmap, then attach $q_s, q_g$ and search the graph. For multi-query use.
- **RRT** — grow a single tree. Draw a sample $s$ and extend from the tree's **nearest node** $u$
  towards $s$ by $\eta$. For single-query use. Using the nearest node is the **Voronoi bias**, and it
  explains every numerical observation in R3.

One assumption, stated explicitly: **(A5) positive clearance** — if a solution path exists, then one
with **clearance $\delta > 0$** exists. Without it none of the guarantees below hold. Tasks that
require contact ($\delta = 0$) are outside this theory and belong to `c6-tamp` and
`s2-planning-through-contact`.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof).

- **R1 (one-step advance lemma and probabilistic completeness of RRT) [D3]** — under (A5) with
  $\eta \le \delta/2$: if the tree has a node in $B_i$ and the sample lands in $B_{i+1}$, then **the
  new node is exactly that sample** and the new edge is collision-free. Hence, with
  $m = \lceil 2L/\eta \rceil$ and $p \ge \zeta_d(\eta/4)^d/\mu(\mathcal{C}_{free})$,
  $$
  \mathbb{P}[\text{failure after } n] \;\le\; \mathbb{P}[\mathrm{Bin}(n, p) < m]
    \;\le\; \exp\!\left(-\frac{(np - m)^2}{2np}\right) \quad (m \le np). \tag{1}
  $$
  That is, the failure probability decays **exponentially** in $n$:
  $\mathbb{P}[\text{failure}] \le a e^{-bn}$.
- **R2 (probabilistic completeness of PRM) [D3]** — on the same ball cover, if the connection radius
  satisfies $r \ge \eta$, then having at least one sample in every $B_i$ already makes the roadmap
  connect $q_s$ to $q_g$. By the union bound,
  $$
  \mathbb{P}[\text{failure after } n \text{ samples}] \;\le\; m\,(1 - p)^n \;\le\; m\, e^{-np}, \tag{2}
  $$
  so $n \ge \frac{1}{p}\ln\frac{m}{\gamma}$ suffices for $\mathbb{P}[\text{failure}] \le \gamma$.
- **R3 (narrow passages, $\epsilon$-goodness and expansiveness) [D2]** — the $p$ in (1) and (2) is
  proportional to $\delta^d$, so it collapses **with the dimension in the exponent** as the passage
  narrows ($\delta \to 0$). Rewriting this in terms of **visibility** instead of clearance gives
  $\epsilon$-goodness and $(\epsilon, \alpha, \beta)$-expansiveness, under which the required number
  of samples takes the form
  $$
  n = O\!\left(\frac{1}{\epsilon\alpha}\log\frac{1}{\epsilon\alpha\gamma} + \frac{1}{\beta}\right)
    \tag{3}
  $$
  ([Hsu, Latombe & Motwani 1999](https://doi.org/10.1142/S0218195999000285)). Both frameworks give
  **sufficient conditions** only, and the measured decay is far faster than the bound — the
  reproduction task counts the classical bound waking up $6\times10^3$ times later than the planner
  actually succeeds.
- **R4 (what probabilistic completeness does not give) [D1]** — (a) **optimality**: the cost of the
  RRT solution does not converge to the optimum (`c6-asymptotic-optimality` R3).
  (b) **finite-time termination**: when **no** solution exists the algorithm never stops and cannot
  declare infeasibility (it does not solve the decision problem). (c) **no separation from the
  deterministic alternative**: a deterministic grid of dispersion $\delta/2$ is complete under the
  same conditions and is in fact faster in low dimension
  ([Janson, Ichter & Pavone 2018](https://arxiv.org/abs/1505.00023)) — **randomness itself is not the
  source of the advantage.**

## Derivation

### R1 — the one-step advance lemma

The overall strategy is: turn the solution path into a **chain of balls** and count the binomial tail
of the event "hit each ball once". There is exactly one hard spot: **the nearest node need not be the
node you had in mind.** This section is about choosing the radii and spacing so that worry
disappears.

**Construction.** Take $\eta \le \delta/2$, parameterize $\sigma$ by arc length and place points
$x_0 = q_s, x_1, \dots, x_m = q_g$ at **spacing $\eta/2$**, so that
$\lVert x_{i+1} - x_i \rVert \le \eta/2$ and
$m = \lceil L/(\eta/2) \rceil = \lceil 2L/\eta \rceil$. Let the balls be $B_i = B(x_i, \eta/4)$.

**Lemma (one-step advance).** If the tree $T$ has a node $v \in B_i$ and this iteration's sample is
$s \in B_{i+1}$, then the new node is $s$ itself ($s$ is added to the tree) and the new edge is
collision-free.

*Proof.*
1. **Distance.** By the triangle inequality,
   $$
   \lVert v - s \rVert \;\le\; \underbrace{\lVert v - x_i \rVert}_{\le \eta/4}
     + \underbrace{\lVert x_i - x_{i+1} \rVert}_{\le \eta/2}
     + \underbrace{\lVert x_{i+1} - s \rVert}_{\le \eta/4} \;=\; \eta. \tag{4}
   $$
   **This is where the choice of radius $\eta/4$ and spacing $\eta/2$ shows itself** — they are
   chosen so that the three terms sum to exactly the step $\eta$. With radius $\eta/2$ the sum would
   be $3\eta/2$ and step 2 below would break.
2. **The nearest node is also within $\eta$.** If $u$ is the tree node nearest to $s$, then by
   definition $\lVert u - s \rVert \le \lVert v - s \rVert \le \eta$. **Who $u$ is does not matter** —
   the distance is enough.
3. **The extension reaches the sample.** The RRT extension is
   $\mathrm{new} = u + \eta\,(s-u)/\lVert s-u \rVert$ if $\lVert s-u\rVert > \eta$, and
   $\mathrm{new} = s$ otherwise. Step 2 gives $\lVert u-s\rVert \le \eta$, so it is the **latter**:
   $\mathrm{new} = s \in B_{i+1}$.
4. **The new edge is free.** $\lVert s - x_{i+1} \rVert \le \eta/4$ and
   $\lVert u - x_{i+1} \rVert \le \lVert u - s\rVert + \lVert s - x_{i+1}\rVert \le \eta + \eta/4
   = 5\eta/4 \le 5\delta/8 < \delta$. By the definition of clearance
   $B(x_{i+1}, \delta) \subset \mathcal{C}_{free}$, and a ball is convex, so the whole segment from
   $u$ to $s$ is free. $\square$

**The binomial tail.** The tree starts in $B_0$ (as $q_s = x_0$), so applying the lemma for
$i = 0, 1, \dots, m-1$ in turn shows that **hitting $B_1, \dots, B_m$ once each, in order,
suffices**. With uniform sampling, the probability of "hitting the next ball" in one iteration is

$$
p \;=\; \frac{\mu\big(B(x_{i+1}, \eta/4)\big)}{\mu(\mathcal{C}_{free})}
  \;\ge\; \frac{\zeta_d\,(\eta/4)^d}{\mu(\mathcal{C}_{free})} \tag{5}
$$

(the ball lies entirely inside $\mathcal{C}_{free}$, so its volume may be used as is — the same
reason as in step 4). Samples in different iterations are independent and each iteration either
"succeeds" (hits the next ball) or not, so the number of successes in $n$ iterations **stochastically
dominates** $\mathrm{Bin}(n, p)$ (every iteration succeeds with probability at least $p$). Once $m$
successes have accumulated the tree has reached $q_g$, so

$$
\mathbb{P}[\text{failure}] \le \mathbb{P}[\mathrm{Bin}(n,p) < m],
$$

and substituting $\theta = 1 - m/(np)$ into the Chernoff lower tail
$\mathbb{P}[X < (1-\theta)np] \le e^{-\theta^2 np/2}$ gives (1). Setting $a = e^{m/2}$ and
$b = p/2$ exhibits the form $\mathbb{P}[\text{failure}] \le a e^{-bn}$.

**Three places the assumptions break** — this paragraph determines how useful R1 actually is.

1. **$\eta \le \delta/2$ is sufficient, not necessary.** In the reproduction task, RRT succeeds more
   than 80% of the time with $\eta = 0.02 > \delta/2 = w/4$. With a large step, step 3 does not take
   the "latter" branch and the lemma simply does not apply; the planner can still get through the
   passage another way. **Do not read "the algorithm works where the theorem is silent" as "the
   theorem is wrong".**
2. **The lower bound on $p$ is extremely loose.** Equation (5) makes no use of the Voronoi bias. RRT
   benefits from the large Voronoi regions of its frontier nodes, so the effective set of samples
   that "extend towards the passage" is far larger than the ball. In the reproduction task, the
   measured $b$ comes out $10^1$–$10^2$ times larger than the $p/2$ of (5).
3. **$\delta$ is unknown.** In practice $\delta$ can only be known once a solution is known, so (1)
   is an **a posteriori** bound and cannot be used to choose the iteration budget in advance. That
   this is not fixed by the expansiveness parameters of R3 either was the first open problem of
   `c6-cspace-complexity`.

### R3 — narrow passages: from clearance to visibility

**The limits of a clearance-based bound.** In (5), $p \propto (\eta/4)^d \propto \delta^d$. Halving
the passage width multiplies $p$ by $2^{-d}$ and the $n$ needed for the same success rate by $2^d$.
For a 7-DoF arm, halving a passage costs a factor $2^7 = 128$. That is the quantitative content of
the "narrow passage problem", and it is everything a clearance-only theory gives.

The trouble is that **clearance is not the right parameter**. Two spaces with the same $\delta$ can
differ wildly in difficulty: (a) a space with one short passage and (b) a space with 100 passages of
the same width in series have the same $\delta$ but differ by a factor 100 in $m$. So Hsu et al.
switch to a **visibility measure**.

**Definition ($\epsilon$-good).** $q \in \mathcal{C}_{free}$ is $\epsilon$-good if
$\mu(\mathcal{V}(q)) \ge \epsilon\,\mu(\mathcal{C}_{free})$, and the space is $\epsilon$-good if
every free configuration is. Meaning: **from any point, a fraction $\epsilon$ of the space is visible
in a straight line.**

**Definition ($\beta$-lookout and expansiveness).** For a connected
$S \subset \mathcal{C}_{free}$ let

$$
\mathrm{LOOKOUT}_\beta(S) = \big\{\, q \in S \;:\;
  \mu\big(\mathcal{V}(q) \setminus S\big) \ge \beta\,\mu\big(\mathcal{C}_{free} \setminus S\big) \,\big\},
$$

and call the space $(\epsilon, \alpha, \beta)$-**expansive** if it is $\epsilon$-good and
$\mu(\mathrm{LOOKOUT}_\beta(S)) \ge \alpha\,\mu(S)$ for every connected $S$. Meaning: **however much
of the space you have already covered, a fraction $\alpha$ of it consists of vantage points that see
a lot of what is still uncovered.** The three parameters measure, respectively, (a) the probability
that a roadmap node is useful ($\epsilon$), (b) the fraction of footholds from which one can cross
into unexplored territory ($\alpha$), and (c) the probability of crossing from such a foothold
($\beta$); (3) follows from them.

**Why this beats clearance.** $\epsilon, \alpha, \beta$ **do not have the dimension in an exponent**.
In a space with a single narrow passage, $\delta^d$ shrinks exponentially while $\epsilon$ can stay
constant if the rooms on either side are large. Conversely, many passages make $\alpha$ small, so the
difficulty is reflected.

**Where the assumption breaks**: $\epsilon, \alpha, \beta$ are **not computable**. Their definition
quantifies over every connected subset of $\mathcal{C}_{free}$ and requires a visibility measure, so
even estimating them requires already knowing the space. So (3) **explains** why narrow passages are
hard but does not **predict** an iteration count. What practice uses instead is not theory but
sampler design: visibility-based PRM
([Nissoux, Siméon & Laumond 1999](https://doi.org/10.1109/iros.1999.811662)), the bridge test
([Hsu et al. 2003](https://doi.org/10.1109/ROBOT.2003.1242285)), learned samplers
([Ichter, Harrison & Pavone 2018](https://arxiv.org/abs/1709.05448)). These change the measure, so
the $p$ of (5) must be recomputed and **the completeness proof must be redone** — if the changed
distribution does not put positive density near the solution path, completeness is lost. That is
exactly why guarantees for learned samplers are empty.

## Proof sketch

### R2 — probabilistic completeness of PRM

**Hypotheses** H1: (A5) — there is a solution path $\sigma$ of clearance $\delta > 0$ and length
$L$. H2: samples are independent and uniform on $\mathcal{C}_{free}$ (or from a distribution with
positive density near the solution path). H3: the connection radius satisfies $r \ge \eta$ with
$\eta \le \delta/2$, and **every** free pair at distance $\le r$ is attempted as a straight-line
connection.
**Conclusion** C: $\mathbb{P}[\text{failure}] \le m e^{-np}$, in particular $\to 0$ as
$n \to \infty$.

**Strategy**: ball cover plus the **union bound**. Unlike RRT no "order" is needed — it is enough
that all the balls get filled. That is why the proof is shorter and the constants better.

1. Reuse the construction of R1 (spacing $\eta/2$, radius $\eta/4$). Let $A_i$ be the event "$B_i$
   contains at least one sample".
2. **Connection lemma.** If $\bigcap_i A_i$ holds, pick one sample $y_i$ in each $B_i$; then
   $$\lVert y_i - y_{i+1}\rVert \le \eta/4 + \eta/2 + \eta/4 = \eta \le r,$$
   so H3 makes the roadmap attempt the edge $(y_i, y_{i+1})$, and by the same argument as step 4 of
   R1 ($y_i, y_{i+1} \in B(x_{i+1}, \delta)$, which is convex and free) that edge is collision-free.
   Hence $y_0 \rightsquigarrow y_m$ lies in the roadmap, and $q_s, q_g$ attach because
   $\lVert q_s - y_0 \rVert \le \eta/4 \le r$.
3. **Union bound.** $\mathbb{P}[A_i^c] = (1 - p_i)^n \le (1-p)^n \le e^{-np}$, so
   $$\mathbb{P}\Big[\bigcup_i A_i^c\Big] \le \sum_{i=1}^{m} \mathbb{P}[A_i^c] \le m\,e^{-np}.$$
   Independence of the events is **not needed** — the union bound does not require it.
4. $m e^{-np} \le \gamma \iff n \ge \frac{1}{p}\ln\frac{m}{\gamma}$. (Omitted: the treatment of the
   variant that connects only the $k$ nearest neighbours instead of every pair within $r$ —
   [Kavraki et al. 1996](https://doi.org/10.1109/70.508439) §4 and the $k_n = O(\log n)$ discussion
   in `c6-asymptotic-optimality`.)

**Removing a hypothesis**: drop $r \ge \eta$ from H3 and step 2's bound
$\lVert y_i - y_{i+1}\rVert \le \eta$ exceeds $r$, the connection is never attempted and the roadmap
is disconnected — this is the practical phenomenon of "$r$ chosen too small, so PRM cannot get
through the passage". Drop "positive density" from H2 and the $p$ of (5) can be zero, making step 3
vacuous (the trap of learned samplers). Drop $\delta > 0$ from H1 and the balls cannot be placed
inside $\mathcal{C}_{free}$ at all, so the convexity argument of step 4 collapses.

## Problem set

Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** In step 1 of R1, keep the radius $\rho$ and the spacing $h$ as
**unknowns** and show that $2\rho + h \le \eta$ is what step 3 requires. Then, taking into account
the trade-off between $p \propto \rho^d$ and $m \propto L/h$, find the $(\rho, h)$ minimizing the
right-hand side of (1) for fixed $\eta$.
*Solution sketch*: maximize $np - m$ subject to $2\rho + h = \eta$. For large $n$ the $p$ term
dominates, which suggests $\rho \to \eta/2$ and $h \to 0$, but then $m \to \infty$. In the regime
$np \gg m$, the choice $\rho = \eta/4$, $h = \eta/2$ puts the two terms at the same order; showing
that the optimum depends on $n$ and $d$ is enough.

**P2 (derivation, ★★, R1·R2)** Compare (1) and (2): express the $n$ needed for a given $\gamma$ in
terms of $p, m, \gamma$ in each case and decide which is smaller. Write one paragraph on the
**structural** reason for the difference (ordered versus unordered).
*Solution sketch*: (2) gives $n \ge p^{-1}\ln(m/\gamma)$ — **logarithmic** in $m$. (1) gives
$n \gtrsim m/p$ — **linear** in $m$. RRT must hit the balls **in order**, so it needs $m$ successes;
PRM only needs every ball filled, which is a coupon-collector problem.

**P3 (numerical, ★, R1·R3)** For the environment of the reproduction task ($d = 2$, unit square,
passage width $w = 0.03$, solution path length $L = 0.8$), compute every explicit constant of R1:
$\delta$, $\eta = \delta/2$, the ball radius, the lower bound on $p$, $m$, and the **smallest
iteration count at which (1) becomes non-vacuous**, $n_{\min} = m/p$.
*Answer*: $\delta = w/2 = 0.015$, $\eta = 0.0075$, radius $\eta/4 = 0.001875$,
$\mu(\mathcal{C}_{free}) = 1 - w(1-w) = 0.9709$,
$$p \ge \frac{\pi (0.001875)^2}{0.9709} = 1.13757\times10^{-5},\qquad
  m = \lceil 2L/\eta \rceil = \lceil 213.33 \rceil = 214,$$
$n_{\min} = m/p = 1.8812\times10^{7}$. Tolerance: relative error $10^{-4}$ on $p$ and $n_{\min}$.
Check: the measured 90%-success point is $n_{90} \approx 3.06\times10^{3}$, so the bound wakes up
$n_{\min}/n_{90} \approx 6.2\times10^{3}$ times later than reality.

**P4 (proof, ★★, R1)** Redo the stochastic-domination step of R1 rigorously. The issue: the event
"hit the next ball" has a **conditional** probability (given that the tree has already reached
$B_i$), and the conditioning differs from iteration to iteration. Define a suitable filtration and
show that the number of successes dominates $\mathrm{Bin}(n,p)$.
*Strategy*: let $\mathcal{F}_k$ be the $\sigma$-algebra generated by the first $k$ iterations'
samples. For the indicator $Z_k = \mathbb{1}[\text{iteration } k \text{ advances}]$, confirm by the
lemma that $\mathbb{P}[Z_k = 1 \mid \mathcal{F}_{k-1}] \ge p$ for **every** past, then cite the
standard lemma that such a sequence of indicators sums to something dominating
$\mathrm{Bin}(n,p)$. (Omitted: the proof of the domination lemma, by coupling —
[Kleinbort et al. 2019](https://doi.org/10.1109/LRA.2018.2888947) §III.)

**P5 (proof, ★★★, R3)** If $\mathcal{C}_{free}$ admits a solution path of clearance $\delta$, is it
$\epsilon$-good? If so, give $\epsilon$ in terms of $\delta, d, \mu(\mathcal{C}_{free})$; if not,
construct a counterexample. Decide the converse too ($\epsilon$-good $\Rightarrow$ a solution path of
positive clearance).
*Strategy*: for the forward direction use
$\mathcal{V}(q) \supset B(q, \operatorname{dist}(q, \mathcal{C}_{obs}))$, but note that $q$ can be
**arbitrarily close** to an obstacle — the definition quantifies over all free points, so there are
configurations for which no positive $\epsilon$ works. For the converse, consider whether $\epsilon$
can stay constant as the width of a passage between two rooms goes to zero.

**P6 (implementation, ★★, R1·R3)** Write the RRT and the two sweeps of the reproduction task.
Requirements: continuous segment–rectangle collision test, brute-force vectorized nearest-neighbour
search, fixed seeds.
*Rubric*: (a) the measurements of both sweeps match the tables of the reproduction task within
tolerance; (b) the linear fit of $-\log(\text{failure rate})$ has $r^2 \ge 0.98$; (c) you explain why
$n = 125$ is excluded from the fit (the tree needs at least $0.4/\eta = 20$ steps just to reach the
passage, and the success rate is 0.5%); (d) you compute $n_{\min}$ of P3 in code and print its ratio
to the measurement.

**P7 (counterexample, ★★, R4)** Construct a case in which "if it is probabilistically complete, run
it long enough and it will find a solution" becomes **meaningless in practice**: for $d = 10$ and
passage width $w$, compute the $p$ of (5) under uniform sampling and the $n$ needed for
$\gamma = 0.1$, at $w = 0.1$ and at $w = 0.05$. Then answer: what does the algorithm output on an
instance with no solution?
*Property checklist*: from $p \propto (w/8)^{10}$, note that the ratio of the two values is $2^{10}$,
and for the second question answer **"it runs forever"** — probabilistic completeness gives no
infeasibility verdict.

**P8 (paper, ★★, R1·R3)** Read Kleinbort et al. 2019 and state (a) exactly what gap the authors point
out in earlier RRT completeness proofs, (b) which step of R1 in this lesson that gap corresponds to,
and (c) how much better their improved bound is than (1), and in which factor.
*Rubric*: pass if you identify that the gap concerns "the identity of the nearest node" (steps 2–3
of R1) and distinguish whether the improvement is at the level of a constant factor or an exponential
one. Writing only "they fixed the proof" fails.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions.

1. **Kavraki, Svestka, Latombe & Overmars, "Probabilistic roadmaps for path planning in
   high-dimensional configuration spaces" (1996, IEEE T-RA)** — role: `seminal`.
   <https://doi.org/10.1109/70.508439>
   *Why read it*: the prototype of R2. Look at the roadmap construction (learning phase plus query
   phase) and at how the **expansion step** tries to handle narrow passages.
   Extra questions: (a) which step of R2 in this lesson does the authors' completeness argument
   correspond to, and what differs? (b) which parameter of R3 is the "expansion step" heuristic
   trying to increase?
2. **LaValle & Kuffner, "Randomized kinodynamic planning" (2001, IJRR)** — role: `seminal`.
   <https://doi.org/10.1177/02783640122067453>
   *Why read it*: the primary source for RRT and the only one where the **Voronoi bias** is stated as
   a design intention. The extension to differential constraints is reread in
   `c6-kinodynamic-planning`.
   Extra questions: (a) what exactly is the completeness statement the authors claim, and which part
   of the proof is a sketch? (b) is there any quantity in the paper that quantifies the Voronoi bias
   (and if not, why not)?
3. **Hsu, Latombe & Motwani, "Path planning in expansive configuration spaces" (1999, IJCGA)** —
   role: `standard`. <https://doi.org/10.1142/S0218195999000285>
   *Why read it*: the source of (3) and the only framework that defines a narrow passage **by a
   measure**.
   Extra questions: (a) find and transcribe the exact constants of (3) from the paper (this lesson
   wrote only $O(\cdot)$). (b) which of $\epsilon, \alpha, \beta$ measures the "number" of narrow
   passages and which the "width"? (c) do the authors give any way to estimate these parameters?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation or one figure. (4) what is guaranteed theoretically,
and **what is not**? (5) the independent and dependent variables and the baselines, and were the
baselines tuned fairly? (6) does the metric match the claim, and are variance and seeds reported?
(7) what is missing for reproduction? (8) if the result were wrong, which assumption would you doubt
first? (9) computational and memory complexity, and real-time feasibility. (10) what would you change
to go beyond this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 15 minutes for both sweeps
together, under 1 GB of memory. numpy only. No external data.

**Input data (given by the lesson).** Workspace $[0,1]^2$, point robot. Erect a **wall of thickness
$w$** at $x = 0.5$ and cut a **$w \times w$ square passage** at $y = 0.5$. The obstacles are the two
rectangles

$$
\Big[\tfrac{1-w}{2},\, \tfrac{1+w}{2}\Big] \times \Big[0,\, \tfrac{1-w}{2}\Big],
\qquad
\Big[\tfrac{1-w}{2},\, \tfrac{1+w}{2}\Big] \times \Big[\tfrac{1+w}{2},\, 1\Big]
$$

with blocked interiors. $q_s = (0.1, 0.5)$, $q_g = (0.9, 0.5)$. The solution path is a straight line
with $L = 0.8$ and clearance $\delta = w/2$. Because the passage is square, **the clearance shrinks
in proportion to the width** — only one variable moves.

Fixed RRT settings: step $\eta = 0.02$, goal bias 5%, goal tolerance radius 0.03, seeds
$0, \dots, 399$ (400 trials). Samples uniform on $[0,1]^2$.

**Acceptance criteria — all five must hold.**

1. **Sweep A (width)** — with $n = 2000$ fixed, varying $w$, the success rate matches the following
   to within an absolute error of 0.05 and is **monotonically increasing in $w$**.

   | $w$ | 0.03 | 0.04 | 0.05 | 0.07 | 0.10 | 0.15 |
   |---|---|---|---|---|---|---|
   | success | 0.7975 | 0.8550 | 0.9300 | 0.9725 | 0.9975 | 1.0000 |

2. **Sweep B (iterations)** — with $w = 0.03$ fixed, varying $n$, the success rate matches the
   following to within an absolute error of 0.05.

   | $n$ | 125 | 250 | 500 | 1000 | 2000 | 4000 |
   |---|---|---|---|---|---|---|
   | success | 0.0050 | 0.3000 | 0.4750 | 0.6575 | 0.7975 | 0.9450 |

3. **Exponential decay (checking R1)** — on the five points of sweep B with $n \ge 250$, a **linear
   fit** of $-\log(\text{failure rate})$ against $n$ has coefficient of determination
   $r^2 \ge 0.98$ and slope $b = (6.6 \pm 1.0)\times 10^{-4}$ (measured $6.554\times10^{-4}$,
   $r^2 = 0.9936$). This is a **direct confirmation** of the form
   $\mathbb{P}[\text{failure}] \le a e^{-bn}$.
4. **Comparison with the classical bound (checking R1's failure mode)** — compute $n_{\min} = m/p$
   of P3 in code and obtain $1.8812\times10^{7}$ (relative error $10^{-4}$); compute
   $n_{90} = (\ln 10 - \text{intercept})/b$ from the fit of criterion 3 and confirm it is of order
   $3.1\times10^{3}$; then show that the ratio satisfies $n_{\min}/n_{90} \ge 10^{3}$ (measured
   $6.2\times10^{3}$).
5. **Width exponent (checking R3)** — on the points of sweep A whose success rate is in
   $(0.02, 0.99)$, a log–log fit of $-\log(\text{failure rate}) \propto w^{\alpha}$ gives
   $\alpha = 1.0 \pm 0.3$ (measured 0.990). **This differs from the $\delta^d = w^2$ of the theory**
   — no contradiction, since (5) is a lower bound, and the cause of the difference is the Voronoi
   bias. Write that interpretation as one paragraph in the report.

**Baselines.** (a) The analytic bound: $(p, m, n_{\min})$ of P3. (b) A deterministic baseline: on a
grid of resolution $h = w/4$ ($N = \lceil 1/h \rceil$, i.e. $134 \times 134$ at $w = 0.03$), a
4-neighbour BFS **reaches the goal for all six values of $w$** (verified). Its number of collision
checks is $N^2 \approx 1.8\times10^4$, the same order as the 2000–4000 used by RRT, so this is a
**fair, comparable-budget comparison** — it confirms in the same environment that in two dimensions
sampling is not better than a deterministic grid (R4(c)). (c) An independent check: rerun with the
goal bias set to 0% and confirm that the success rate only moves downwards.

**Failure table**

| Symptom | Cause | How to check |
|---|---|---|
| success is 1.0 at every $w$ | collisions are tested only at the endpoints, so the wall is jumped over | raise $\eta$ to 0.2 — if the success rate is still 1.0 there is no continuous test |
| success above 0.99 even at $w = 0.03$ | the wall thickness is near 0 rather than $w$ (the rectangles' $x$ extent is miscomputed) | measure $\mu(\mathcal{C}_{obs})$ on a grid and compare with $w(1-w)$ |
| success above 0.3 at $n = 125$ | the goal tolerance is too large, or the goal bias exceeds 5% | print the node count and see whether the goal is reached in fewer than $0.8/\eta = 40$ steps |
| the linear fit has $r^2 < 0.9$ | saturated points (success 1.0 at large $n$) or $n = 125$ were included | exclude points outside $(0.02, 0.995)$ |
| the measured slope $b$ is of order $10^{-5}$ | the failure rate was taken to be the success rate rather than $1 - \text{success}$ | check that $-\log(\text{failure})$ increases with $n$ |
| results differ between runs | seeds were not fixed (`default_rng(s)` created outside the loop) | run the same command twice and check the success counts are identical |

## Open problems

- **(open problem) A computable difficulty parameter** — neither $\delta$ nor
  $(\epsilon,\alpha,\beta)$ can be known **without already knowing a solution**, so no theory answers
  "how many iterations does this problem need?" Criterion 4 of the reproduction task shows the size
  of that gap numerically (a factor $6\times10^3$). Current approaches: expansiveness in
  [Hsu, Latombe & Motwani 1999](https://doi.org/10.1142/S0218195999000285), the improved bound of
  [Kleinbort et al. 2019](https://doi.org/10.1109/LRA.2018.2888947), the smoothed analysis of
  [Chaudhuri & Koltun 2009](https://doi.org/10.1016/j.comgeo.2008.10.005). What is missing: a theory
  predicting the iteration count from quantities **directly measurable** on an instance.
- **(open problem) Completeness of learned samplers** — changing the sampling distribution changes
  the $p$ of (5) and the completeness proof must be redone, but a neural sampler has no guarantee of
  putting positive density near the solution path (the failure mode of R3). Mixing with the uniform
  distribution restores completeness, but **the mixing ratio nearly erases the performance gain** —
  and there is no theory of that trade-off. Current approaches:
  [Ichter, Harrison & Pavone 2018](https://arxiv.org/abs/1709.05448),
  [Qureshi et al. 2018](https://arxiv.org/abs/1806.05767). What is missing: a principled way to
  change the distribution while keeping the guarantee.
- **(open problem) Is randomness really needed** — deterministic low-dispersion sequences are
  complete under the same conditions, faster in low dimension, and admit dispersion-based bounds in
  high dimension too ([Janson, Ichter & Pavone 2018](https://arxiv.org/abs/1505.00023)). Yet practice
  uses random sampling almost exclusively. There is no separated evidence for which dimensions and
  geometries randomness **actually** helps in. What is missing: a systematic deterministic-versus-
  random comparison (equal collision-check budget, equal post-processing).

## Concept check

Run `rc quiz c6-sampling-completeness`. Concept checking only; the real work is the problem set and
the reproduction task.

The six items cover: why the ball radius is $\eta/4$ and the spacing $\eta/2$; why the bound depends
on $m$ logarithmically for PRM and linearly for RRT; what probabilistic completeness does not
guarantee; why a measured decay faster than the bound is not a contradiction; how $p$ scales when the
passage width halves; and what expansiveness buys over clearance.

## How to study this stage

1. **Write the two algorithms in five lines each (20 min)** — write the pseudocode of PRM and RRT in
   at most five lines apiece and mark that the difference is **whether the nearest node is used**.
   That single line produces both the difference in proof structure between R1 and R2 (ordered versus
   unordered) and every numerical observation of R3.
2. **Close the lemma on paper (60 min)** — rewrite steps 1–4 of R1 from a blank page. In particular
   confirm by hand why the three terms of step 1 sum to exactly $\eta$ and where the argument breaks
   if the radius is changed to $\eta/2$. Solving P1 alongside shows that the choice is not arbitrary
   but **a design under the constraint $2\rho + h \le \eta$**.
3. **Turn the constants into numbers (30 min)** — do P3. Compute $p = 1.14\times10^{-5}$, $m = 214$
   and $n_{\min} = 1.9\times10^{7}$ yourself and see how large that is next to the measured
   $3\times10^{3}$. **Until you turn a theorem into numbers you do not know how big the word
   "conservative" is.**
4. **Run the two sweeps (90 min)** — the reproduction task. Do sweep B (iterations) first to see the
   exponential decay with your own eyes, then see $\alpha \approx 1$ come out of sweep A (width) and
   write the interpretation paragraph of criterion 5 yourself. That paragraph is the most important
   artifact of this lesson.
5. **Three papers (120 min)** — read them not in the order 1996 → 2001 → 1999 but
   **1996 → 1999 → 2001**: see the roadmap and its limitation (narrow passages) first, and only then
   how RRT attacks the same problem differently with the Voronoi bias. Read the optional Kleinbort
   2019 when writing P8.
6. **Problem set (150 min)** — P3 and P6 first, then P1 and P2, then P4, P5, P7, P8 with whatever
   time remains. P5 (the relation between clearance and $\epsilon$-goodness) is the hardest and the
   most often left over.

**Passing bar**: you can reconstruct the four steps of R1 from a blank page, you can explain the
difference in $m$-dependence between (1) and (2), you have code satisfying the five criteria of the
reproduction task plus the interpretation paragraph of criterion 5, and you can name the three things
probabilistic completeness does not guarantee. You have notes on all three papers.
