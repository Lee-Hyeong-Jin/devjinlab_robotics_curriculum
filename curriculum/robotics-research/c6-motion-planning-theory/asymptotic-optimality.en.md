---
id: c6-asymptotic-optimality
lang: en
title: Asymptotic optimality
summary: >-
  Moving from probabilistic completeness to asymptotic optimality. First establish that the cost of
  an RRT solution does not converge to the optimum, then derive at the level of proof where RRT*'s
  connection radius $r_n = \gamma(\log n/n)^{1/d}$ comes from — why the $\log n$, and why the
  exponent $1/d$. Quantify the speed-up of informed/BIT* through the volume of an ellipsoid and
  write its shrink factor in closed form as a function of dimension. The reproduction task measures,
  over 200 runs, RRT stalling while RRT* converges.
objectives:
  - Derive why the cost of an RRT solution does not converge to the optimum, from "a parent, once chosen, is never changed".
  - Explain at which step of the covering and union-bound argument the $\log n / n$ form of the connection radius arises.
  - Derive the explicit constant $\gamma^\ast$ and compute it numerically for a given environment.
  - Derive the volume of the informed set (a prolate hyperspheroid) and write its shrink factor as a function of dimension.
  - Show numerically what asymptotic optimality does not guarantee at finite $n$.
tags: [motion-planning, sampling-based, rrt-star, asymptotic-optimality, informed-sampling, research]
---

# Asymptotic optimality

## Setup and notation

`c6-sampling-completeness` is assumed. In particular its ball-cover construction (radius $\eta/4$,
spacing $\eta/2$) and the statement that "completeness does not give optimality" (its R4(a)) are the
starting point here. Also assumed:

- Probability: the union bound, the Borel–Cantelli lemma, almost sure convergence.
- The connectivity threshold $(\log n/n)^{1/d}$ of a random geometric graph is **not** assumed — it
  is derived here.
- The volume of an ellipsoid; principal-axis transformation of a quadratic form (recommended
  prerequisite `r0-linear-algebra-decompositions`).

Notation (in addition to the module's):

| Symbol | Meaning |
|---|---|
| $c(\sigma)$ | path cost; taken here to be the length $\ell(\sigma)$ |
| $c^\ast$ | optimal cost $\inf_\sigma c(\sigma)$; in the reproduction task, $L^\ast$ |
| $Y_n$ | cost of the best solution the algorithm holds after $n$ samples |
| $r_n$ | connection radius (the neighbour radius of RRT* and PRM*) |
| $\gamma$ | radius constant, with $r_n = \gamma(\log n/n)^{1/d}$ |
| $\gamma^\ast$ | the critical value of $\gamma$ (R1) |
| $\zeta_d$ | volume of the unit ball, $\pi^{d/2}/\Gamma(d/2+1)$ |
| $c_{\min}$ | $\lVert q_g - q_s \rVert$ — the obstacle-free lower bound |
| $\kappa$ | $c_{best}/c_{\min}$ — the relative quality of the current solution |
| $X_{\hat f}(c_{best})$ | the informed set $\{x : \lVert x - q_s\rVert + \lVert x - q_g\rVert \le c_{best}\}$ |

**Definition (asymptotic optimality).** An algorithm is **asymptotically optimal** if, on a problem
admitting an optimal path with clearance $\epsilon > 0$,
$\mathbb{P}[\lim_{n\to\infty} Y_n = c^\ast] = 1$. Probabilistic completeness only requires
$\mathbb{P}[Y_n < \infty] \to 1$ — **the two are entirely different claims.**

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof).

- **R1 (asymptotic optimality of RRT* and the radius rule) [D3]** — with the connection radius
  $$r_n = \gamma\left(\frac{\log n}{n}\right)^{1/d},
    \qquad \gamma > \gamma^\ast = 2\left(1 + \frac{1}{d}\right)^{1/d}
      \left(\frac{\mu(\mathcal{X}_{free})}{\zeta_d}\right)^{1/d} \tag{1}$$
  RRT* is asymptotically optimal. The $\log n$ comes from the union bound that keeps **$n$ balls
  simultaneously non-empty**, and the exponent $1/d$ from the single fact that **volume goes as the
  $d$-th power of a radius**.
- **R2 (RRT is not asymptotically optimal) [D3]** — RRT fixes a node's parent once and never changes
  it. The costs stored in the tree therefore never decrease, and $Y_n$ converges almost surely to a
  random variable that is **not** the optimum: $\mathbb{P}[\lim_n Y_n = c^\ast] = 0$
  ([Karaman & Frazzoli 2011](https://arxiv.org/abs/1105.1186), Theorem 33).
- **R3 (the informed set and its shrink factor) [D2]** — when the cost is path length, the region
  that can contain a better solution than the current one is exactly the **prolate hyperspheroid**
  with foci $q_s, q_g$ and transverse diameter $c_{best}$, whose volume is
  $$\mu\big(X_{\hat f}\big) = \frac{\zeta_d}{2^d}\, c_{best}\,
    \big(c_{best}^2 - c_{\min}^2\big)^{(d-1)/2}. \tag{2}$$
  Its ratio to the ball of diameter $c_{best}$ is a function of $\kappa = c_{best}/c_{\min}$ alone,
  $$\frac{\mu(X_{\hat f})}{\zeta_d (c_{best}/2)^d}
    = \big(1 - \kappa^{-2}\big)^{(d-1)/2}, \tag{3}$$
  so it **collapses rapidly in high dimension** — at the same $\kappa = 1.07$ it is 0.356 at
  $d = 2$, $2.02\times10^{-3}$ at $d = 7$ and $9.11\times10^{-5}$ at $d = 10$.
- **R4 (curse of dimensionality, and no guarantee at finite $n$) [D2]** — (a) the expected neighbour
  count is $\mathbb{E}[|N(x)|] \approx n \zeta_d r_n^d/\mu = \gamma^d \zeta_d \log n / \mu$, so the
  per-iteration cost of RRT* is $O(\log n)$ — the **intended consequence** of the radius rule.
  (b) But covering the space to resolution $\epsilon$ needs $n \sim \epsilon^{-d}$, so the
  **rate** of convergence degrades exponentially with dimension. (c) Asymptotic optimality
  **guarantees nothing at finite $n$**: in the reproduction task RRT* at $n = 2000$ is at 1.0081
  times the optimum, while RRT in the same environment **stalls** at 1.1325.

## Derivation

### R1 — why $\log n / n$, and why the $1/d$ power

The radius rule is the intersection of three requirements. Derive the condition each imposes on
$r_n$ separately, then combine them.

**Requirement 1 (local covering) — the neighbourhood of the optimal path must be covered by
samples.** Reuse the construction of R1 of the previous lesson: cover the optimal path
$\sigma^\ast$ with $m_n = \Theta(L/r_n)$ balls of radius $r_n/4$ and demand at least one sample in
each. One ball is empty with probability $(1 - p_n)^n$ where
$p_n = \zeta_d (r_n/4)^d/\mu$. The union bound gives

$$
\mathbb{P}[\text{some ball is empty}] \;\le\; m_n (1 - p_n)^n \;\le\; m_n e^{-n p_n}
  \;=\; \Theta\!\left(\frac{1}{r_n}\right) \exp\!\left(-\frac{n \zeta_d r_n^d}{4^d \mu}\right).
  \tag{4}
$$

This probability must be **summable in $n$** for Borel–Cantelli to give "it fails only finitely
often", i.e. almost sure convergence. Substituting
$r_n = \gamma(\log n/n)^{1/d}$,

$$
n p_n = \frac{n \zeta_d \gamma^d}{4^d \mu}\cdot\frac{\log n}{n}
  = \frac{\zeta_d \gamma^d}{4^d \mu}\,\log n \;=\; \beta \log n,
$$

so $e^{-np_n} = n^{-\beta}$. The leading factor of (4) is $r_n^{-1} = O((n/\log n)^{1/d})$, so the
whole expression is $O(n^{1/d - \beta})$, which is summable when $\beta > 1 + 1/d$. **That is what
the $\log n$ is for**: $e^{-np_n}$ must fall as a **power** of $n$, and for that $np_n$ must be
proportional to $\log n$. Setting $r_n \propto n^{-1/d}$ alone makes $np_n$ constant, so
$e^{-np_n}$ is constant and never summable.

Solving $\beta > 1 + 1/d$ for $\gamma$,

$$
\gamma^d > \frac{4^d \mu (1 + 1/d)}{\zeta_d}
  \;\Longleftrightarrow\;
  \gamma > 4\left(1 + \frac{1}{d}\right)^{1/d}\left(\frac{\mu}{\zeta_d}\right)^{1/d}.
  \tag{5}
$$

The constant 2 in (1) differs from the 4 in (5) because the covering balls were taken of radius
$r_n/4$. The original paper chooses them more cleverly (consecutive balls overlapping, radius
$r_n/2$) and gets 2 instead of 4. **The structure is the same and only the constant differs** —
either way $\gamma^\ast$ is proportional to $(\mu/\zeta_d)^{1/d}$.

**Requirement 2 (connection) — the neighbour radius must exceed the spacing between samples.** Even
if requirement 1 puts a sample in every ball, no edge appears in the graph unless the samples of
consecutive balls are **recognized as neighbours**. With spacing $r_n/2$ and radius $r_n/4$, two
such samples are at most $r_n/4 + r_n/2 + r_n/4 = r_n$ apart, so **the radius $r_n$ is exactly what
is needed**. This is the same inequality as $2\rho + h \le \eta$ in step 1 of R1 of the previous
lesson, with $r_n$ in the place of $\eta$.

**Requirement 3 (cost) — the neighbour count must not grow.** The expected number of neighbours
within $r_n$ is

$$
\mathbb{E}[|N(x)|] \;=\; n\cdot\frac{\zeta_d r_n^d}{\mu}
  \;=\; \frac{\zeta_d \gamma^d}{\mu}\,\log n
  \tag{6}
$$

which is proportional to $\log n$. With a constant radius $r$ the neighbour count would be
$\Theta(n)$ and the total cost $\Theta(n^2)$. **The $\log n/n$ rule is the smallest radius that
still gives almost sure optimality, and the price is $O(\log n)$ per iteration** — (1) is exactly
where the two requirements meet.

**Combining the three** gives $r_n = \gamma(\log n/n)^{1/d}$ with $\gamma > \gamma^\ast$. The
exponent $1/d$ comes from $p_n \propto r_n^d$ in requirement 1 — that is, from the single fact that
**volume is the $d$-th power of a radius**.

**Where the assumptions break**: (a) without $\mu(\mathcal{X}_{free})$ one cannot compute
$\gamma^\ast$. In practice the box volume is used, which **overestimates** $\mu$ when there are many
obstacles, making $\gamma$ larger than necessary and raising the neighbour count — the guarantee
survives and only the cost rises (the safe direction). Underestimating loses the guarantee.
(b) If the cost is not path length (time, curvature, energy) the argument $p_n \propto r_n^d$
survives but "defining neighbours by a radius" loses its meaning — that is the case with
differential constraints and is taken up again in `c6-kinodynamic-planning`. (c) The original proof
had a gap and the condition on $\gamma$ was revised
([Solovey et al. 2020](https://arxiv.org/abs/1909.09688)) — problem P8.

### R3 — the volume of the informed set

**What the set is.** If the cost is length and the current best solution is $c_{best}$, then the
length of any path through a point $x$ is bounded below by
$\lVert x - q_s\rVert + \lVert x - q_g \rVert$ (triangle inequality). Hence

$$
\lVert x - q_s\rVert + \lVert x - q_g \rVert > c_{best}
  \;\Longrightarrow\; \text{no path through } x \text{ is shorter than } c_{best}.
$$

So only points inside $X_{\hat f}(c_{best}) =
\{x : \lVert x - q_s\rVert + \lVert x - q_g\rVert \le c_{best}\}$ can contribute to an improvement.
That set is an **ellipsoid with foci $q_s, q_g$**: a prolate hyperspheroid whose axis through the
foci (the transverse axis) has length $c_{best}$ and whose other $d-1$ axes all have length
$\sqrt{c_{best}^2 - c_{\min}^2}$.

*Deriving the semi-axes.* With focal distance $2c = c_{\min}$ and semi-transverse axis
$a = c_{best}/2$, the standard relation $b^2 = a^2 - c^2$ gives
$$b = \sqrt{\left(\frac{c_{best}}{2}\right)^2 - \left(\frac{c_{\min}}{2}\right)^2}
  = \frac{1}{2}\sqrt{c_{best}^2 - c_{\min}^2}.$$

**Volume.** An ellipsoid with semi-axes $a, b, b, \dots, b$ ($d-1$ copies of $b$) has volume
$\zeta_d\, a\, b^{d-1}$, so

$$
\mu(X_{\hat f}) = \zeta_d \cdot \frac{c_{best}}{2} \cdot
  \left(\frac{\sqrt{c_{best}^2 - c_{\min}^2}}{2}\right)^{d-1}
  = \frac{\zeta_d}{2^d}\,c_{best}\,\big(c_{best}^2 - c_{\min}^2\big)^{(d-1)/2},
$$

which is (2). Dividing by the volume $\zeta_d (c_{best}/2)^d$ of the **ball** of diameter
$c_{best}$,

$$
\frac{\mu(X_{\hat f})}{\zeta_d (c_{best}/2)^d}
  = \frac{\big(c_{best}^2 - c_{\min}^2\big)^{(d-1)/2}}{c_{best}^{d-1}}
  = \left(1 - \frac{c_{\min}^2}{c_{best}^2}\right)^{(d-1)/2}
  = \big(1-\kappa^{-2}\big)^{(d-1)/2},
$$

which is (3) — a function of $\kappa$ alone, with the dimension in the exponent.

**Where the assumption breaks — when informed sampling does not help**: (3) is a ratio **to a
ball**, whereas the actual benefit of informed sampling is
$\mu(X_{\hat f})/\mu(\mathcal{X}_{free})$. In the environment of the reproduction task ($d = 2$,
$\mu(\mathcal{X}_{free}) = 80$, $c_{\min} = 12.72792$), evaluating (2) gives

| $c_{best}$ | $1.3\,L^\ast = 17.704$ | $1.1\,L^\ast = 14.980$ | $L^\ast = 13.6185$ |
|---|---|---|---|
| $\mu(X_{\hat f})$ | 171.1 | 92.95 | 51.81 |
| $\mu(X_{\hat f})/\mu(\mathcal{X}_{free})$ | 2.139 | 1.162 | 0.648 |

**In the first two columns the ratio exceeds 1** — the ellipsoid covers the whole free space, so
informed sampling is **identical** to uniform sampling. Only on reaching the optimum does it cut
35%. In other words, **in low dimension and on short paths informed sampling is nearly useless**,
and, as (3) says, the benefit appears as $d$ grows. That is why the paper's figures are drawn at six
or more degrees of freedom. Computing this table yourself is problem P3.

## Proof sketch

### R2 — RRT is not asymptotically optimal

**Hypotheses** H1: $\mathcal{X}_{free}$ is bounded and the optimal path is not unique, or at least
lies in a measure-zero subset of the free space (which it always does for a length cost).
H2: RRT fixes a new node's parent to the **nearest node once and never changes it** (no rewiring).
H3: samples are independent with positive density on $\mathcal{X}_{free}$.
**Conclusion** C: $Y_n$ converges almost surely, but its limit is not $c^\ast$ —
$\mathbb{P}[\lim_n Y_n = c^\ast] = 0$.

**Strategy**: establish "the tree holds no decreasing quantity" not by a martingale argument but by
plain monotonicity. The crux is that (a) each node's **cost is fixed at the moment it is created**
and (b) approaching the optimal path arbitrarily closely would require **infinitely many nodes to
change parents**.

1. **$Y_n$ is non-increasing and bounded, hence convergent.** The tree only gains nodes and existing
   paths never disappear, so $Y_{n+1} \le Y_n$, bounded below by $c^\ast$. So the limit $Y_\infty$
   exists almost surely. (Up to here RRT* is the same.)
2. **$Y_\infty = c^\ast$ would require a sequence of tree paths converging to $c^\ast$.** A path is
   the **unique path to the root** in the tree, so for its cost to fall below $c^\ast + \epsilon$,
   the stored cost of **every node** on it must be near optimal.
3. **H2 prevents that.** The cost of node $v$ is fixed by the nearest parent available at creation
   time. The tree at that moment is finite, so $v$'s cost is whatever that finite tree offers, and
   in general it is **strictly greater** than $c^\ast(v)$, the optimal cost from the start to $v$. By
   H1, the probability that $v$ lands exactly on the optimal path is zero.
4. **The "strictly greater" never goes away.** A near-optimal path requires every node on it to be
   near optimal, but each node's excess cost is fixed at creation and **never decreases** afterwards.
   So building a sequence of nodes converging to the optimal path would require **each node to be
   already near optimal when created**, and the probability of that tends to zero as the number of
   nodes grows (it demands an independent measure-zero event at every node). (Omitted: the step that
   makes the lower bound on the excess cost explicit —
   the proof of Theorem 33 in [Karaman & Frazzoli 2011](https://arxiv.org/abs/1105.1186).)
5. Therefore $Y_\infty > c^\ast$ with probability 1. C.

**Removing a hypothesis**: replacing H2 **with rewiring** (RRT*) destroys step 3 — a node's cost can
later decrease, so "fixed at creation" becomes false, and indeed R1 then holds. **What separates
RRT from RRT* is not the sampling but one line of rewiring.** Removing H1 (an artificial cost for
which the optimal path occupies a set of positive measure) breaks the "probability zero" argument of
step 3 and RRT could be optimal — but no such cost arises in robotics.

## Problem set

Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Generalize the derivation of requirement 1 to a radius
$\rho_n = \lambda r_n$ with $0 < \lambda \le 1/2$ and find how $\gamma^\ast$ depends on $\lambda$.
Confirm that $\lambda = 1/4$ gives (5) and $\lambda = 1/2$ gives (1).
*Solution sketch*: $p_n = \zeta_d(\lambda r_n)^d/\mu$, so
$\beta = \zeta_d \lambda^d \gamma^d/\mu$, and $\beta > 1 + 1/d$ gives
$\gamma > \lambda^{-1}(1+1/d)^{1/d}(\mu/\zeta_d)^{1/d}$. At $\lambda = 1/2$ the coefficient is 2.

**P2 (derivation, ★★, R3)** Expand (2) explicitly at $d = 2$ and $d = 3$ and confirm it agrees with
the area $\pi a b$ of an ellipse and the volume $\frac{4}{3}\pi a b^2$ of a spheroid. Then write the
**order** at which (2) goes to zero as $c_{best} \to c_{\min}$, as a function of $d$.
*Solution sketch*: substitute $\zeta_2 = \pi$, $\zeta_3 = 4\pi/3$ with $a = c_{best}/2$ and
$b = \sqrt{c_{best}^2-c_{\min}^2}/2$. Writing $c_{best} = c_{\min}(1+\epsilon)$ gives
$c_{best}^2 - c_{\min}^2 = c_{\min}^2(2\epsilon + \epsilon^2) = \Theta(\epsilon)$, so the volume is
$\Theta(\epsilon^{(d-1)/2})$.

**P3 (numerical, ★, R3)** For the environment of the reproduction task ($[0,10]^2$, three obstacles
of total area 20, $q_s = (0.5,0.5)$, $q_g = (9.5,9.5)$), find $c_{\min}$, $L^\ast$ and $\kappa$, and
compute (2) and $\mu(X_{\hat f})/\mu(\mathcal{X}_{free})$ for
$c_{best} \in \{1.3L^\ast, 1.1L^\ast, L^\ast\}$. Also find the threshold $c_{best}$ at which
informed sampling begins to help.
*Answer*: $c_{\min} = \sqrt{162} = 12.727922061$, $L^\ast = 13.618501326$ (P3 of the previous
lesson), $\kappa = 1.069970515$, $\mu(\mathcal{X}_{free}) = 80$.
Then $\mu(X_{\hat f}) = 171.109,\ 92.949,\ 51.810$ with ratios $2.1389,\ 1.1619,\ 0.6476$.
The threshold solves $\mu(X_{\hat f}) = 80$, i.e. $\frac{\pi}{4}c\sqrt{c^2 - 162} = 80$, giving
$c \approx 14.3$ — so informed sampling differs from uniform sampling only **within 1.05 times the
optimum**. Tolerance: relative error $10^{-3}$.

**P4 (numerical, ★, R1·R4)** In the same environment compute $\gamma^\ast$ from (1), and for
$\gamma = 1.1\gamma^\ast$ compute $r_n$ and the expected neighbour count (6) at
$n \in \{250, 500, 1000, 2000\}$.
*Answer*: $\gamma^\ast = 2(1.5)^{1/2}(80/\pi)^{1/2} = 12.360774465$ and
$\gamma = 13.596851911$. Then $r_n = 2.020670,\ 1.515864,\ 1.130074,\ 0.838216$, and the expected
neighbour count $= \zeta_2\gamma^2\log n/\mu = \pi(13.5969)^2\log n/80 = 7.2600\log n
= 40.08,\ 45.11,\ 50.15,\ 55.18$. Tolerance $10^{-4}$ relative.
Check: compute $n\zeta_2 r_n^2/\mu$ directly and confirm the same values.

**P5 (proof, ★★★, R2)** Fill in step 4 of R2 explicitly: for the gap
$\Delta(v) = \mathrm{cost}(v) - c^\ast(v)$ between a node's stored and optimal cost in RRT, show
that there is an $\epsilon > 0$ with $\mathbb{P}[\Delta(v) < \epsilon] < 1$ at the moment $v$ is
created, and deduce $Y_\infty > c^\ast$ from it.
*Strategy*: the tree at creation time is finite, so the choice of nearest parent is finite, and the
event that none of them attains $c^\ast(v)$ has positive probability. Then use **independence** to
show that the probability of "every node of a path being near optimal" tends to zero. The hard part
is that the length of that node sequence grows with $n$ — a lower bound on it is needed.

**P6 (proof, ★★, R1)** Write out precisely the step of requirement 1 that uses Borel–Cantelli: for
the event $A_n$ = "at iteration $n$ some covering ball is empty", explain why
$\sum_n \mathbb{P}[A_n] < \infty$ yields "almost surely it happens only finitely often" and why
$Y_n \to c^\ast$ follows. What breaks at the boundary case $\beta = 1 + 1/d$?
*Strategy*: state the first Borel–Cantelli lemma and note that if $A_n$ happens finitely often then
beyond some $N$ every ball is filled. At equality, $O(n^{1/d-\beta}) = O(n^{-1})$ and
$\sum 1/n$ diverges, so summability fails — the guarantee disappears, which is not the same as being
disproved.

**P7 (implementation, ★★, R1·R2·R4)** Write the RRT and RRT* of the reproduction task.
Requirements: the radius rule (1), parent reselection and rewiring, and **cost propagation to the
subtree after rewiring**.
*Rubric*: (a) the cost-ratio tables of both algorithms match the reproduction task within tolerance;
(b) the median relative improvement of RRT is 0; (c) the relative improvement of RRT* is positive
for every seed; (d) you run it **without** cost propagation and show numerically that RRT*'s
convergence slows (a common bug).

**P8 (counterexample/paper, ★★★, R1)** Read Solovey et al. 2020, identify which of requirements 1,
2, 3 of R1 the gap in the original Karaman–Frazzoli proof corresponds to, and state how the revised
condition on $\gamma$ differs from (1). Decide numerically whether the difference affects the
$\gamma^\ast$ of the reproduction task.
*Property checklist*: distinguish whether the gap concerns "whether the samples of covering balls
are **connected as neighbours**" (requirement 2) or summability (requirement 1). Check whether the
revised condition changes $\gamma^\ast$ by a constant factor or changes its dependence on $d$, and
compute the ratio numerically in two dimensions.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions.

1. **Karaman & Frazzoli, "Sampling-based algorithms for optimal motion planning" (2011, IJRR)** —
   role: `seminal`. <https://arxiv.org/abs/1105.1186> (§4 and §6, Theorems 33, 34, 38)
   *Why read it*: both R1 and R2 come from here. The point is to read Theorem 33 (non-optimality of
   RRT) and Theorem 38 (asymptotic optimality of RRT*) **side by side**.
   Extra questions: (a) find, in the authors' covering construction, why their constant in
   $\gamma^\ast$ differs from (5) in this lesson. (b) why do PRM* and RRT* share the same radius
   rule? (c) at which step of the proof of Theorem 33 does the "probability zero" appear?
2. **Gammell, Srinivasa & Barfoot, "Informed RRT*" (2014, IROS)** — role: `standard`.
   <https://arxiv.org/abs/1404.2334>
   *Why read it*: (2) of R3 comes from here, as does the **method for sampling the ellipsoid
   uniformly and directly** (a unit-ball sample plus a linear transform).
   Extra questions: (a) at how many dimensions were the experiments run, and can
   $(1-\kappa^{-2})^{(d-1)/2}$ from (3) explain that choice? (b) why does informed sampling not harm
   **completeness**?
3. **Gammell, Srinivasa & Barfoot, "Batch Informed Trees (BIT*)" (2015, ICRA)** — role: `standard`.
   <https://arxiv.org/abs/1405.5848>
   *Why read it*: it is the bridge between sampling and heuristic search (the A* of the next
   lesson). "Search an implicit random geometric graph in batches" is the whole idea, and that
   sentence is what ties `c6-search-based-planning` to this lesson.
   Extra questions: (a) how does the batch size interact with the radius rule (1)? (b) what breaks
   if the heuristic is inconsistent (contrast with R1 of the next lesson)?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation or one figure. (4) what is guaranteed theoretically,
and **what is not**? (5) the independent and dependent variables and the baselines, and were the
baselines tuned fairly? (6) does the metric match the claim, and are variance and seeds reported?
(7) what is missing for reproduction? (8) if the result were wrong, which assumption would you doubt
first? (9) computational and memory complexity, and real-time feasibility. (10) what would you change
to go beyond this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 20 minutes for 200 seeds × two
algorithms × $n = 2000$, under 1 GB of memory. numpy only.

**Input data (given by the lesson).** Use the **same environment** as the reproduction task of
`c6-combinatorial-gcs`, so that the comparison target $L^\ast$ is known in closed form. Workspace
$[0,10]^2$, point robot, obstacles $R_1 = [2,3]\times[1,8]$, $R_2 = [5,6]\times[3,10.5]$,
$R_3 = [7,8]\times[-0.5,6]$, $q_s = (0.5,0.5)$, $q_g = (9.5,9.5)$.
$$L^\ast = \tfrac12(\sqrt{26}+\sqrt{74}) + \sqrt{13} + \sqrt{10} = 13.618501326,
  \qquad \mu(\mathcal{X}_{free}) = 100 - 20 = 80.$$

Fixed settings: step $\eta = 0.6$, **no goal bias** (pure uniform sampling — a goal bias muddies a
cost-convergence measurement), samples landing inside an obstacle are discarded, seeds
$0,\dots,199$. RRT*'s radius is $r_n = 1.1\gamma^\ast(\log n/n)^{1/2}$ with
$\gamma^\ast = 12.360774465$ (P4). The "current solution cost" is defined as the minimum over all
tree nodes $v$ of $\mathrm{cost}(v) + \lVert v - q_g\rVert$ among those whose segment $v \to q_g$ is
free (the goal is not inserted into the tree). The checkpoints are
$n \in \{250, 500, 1000, 2000\}$.

**Acceptance criteria — all five must hold.**

1. **Matched sample** — use only the seeds for which **both** algorithms found a solution at
   $n = 250$ (measured 77/200). On that set the median of the cost ratio $Y_n/L^\ast$ matches the
   following to within an absolute error of 0.01.

   | $n$ | 250 | 500 | 1000 | 2000 |
   |---|---|---|---|---|
   | RRT | 1.1328 | 1.1328 | 1.1328 | 1.1325 |
   | RRT* | 1.0201 | 1.0148 | 1.0104 | 1.0081 |

2. **RRT stalls (checking R2)** — on the matched sample the median of RRT's relative improvement
   $(Y_{250} - Y_{2000})/Y_{250}$ is **exactly 0** and the fraction of seeds that improve at all is
   below 0.2 (measured: median 0.00000, fraction 0.117).
3. **RRT* converges (checking R1)** — on the same sample RRT*'s relative improvement is **positive
   for every seed** (fraction 1.000) with median $0.0100 \pm 0.004$ (measured 0.01002), and the
   median cost ratio **decreases monotonically** across the four checkpoints.
4. **Minimum and tail** — at $n = 2000$ over all 200 seeds, the minimum cost ratio is
   $1.0347 \pm 0.005$ for RRT and $1.0018 \pm 0.002$ for RRT*. That is, **even RRT's best solution
   is 3% off the optimum**, and that value **does not change** across the four checkpoints.
5. **Checking the radius rule** — log $r_n$ and the mean neighbour count during the run and confirm
   they match $r_n = 2.020670,\ 1.515864,\ 1.130074,\ 0.838216$ from P4 to within a relative error
   of $10^{-6}$, and that the mean neighbour count is linear in $\log n$ ($r^2 \ge 0.95$).

**Baselines.** (a) The closed form $L^\ast$ (independently confirmed with the visibility graph in the
previous lesson). (b) RRT (criteria 2 and 4). (c) A variant of itself: run RRT* without cost
propagation and show the improvement fraction of criterion 3 drops (rubric (d) of P7).

**Failure table**

| Symptom | Cause | How to check |
|---|---|---|
| RRT* behaves like RRT | no rewiring, or no cost propagation to the subtree after rewiring | count the rewirings — there should be hundreds or more by $n = 2000$ |
| RRT*'s cost ratio is below 1 | the cost was computed as a straight-line distance rather than along the tree path, or the goal connection segment was not collision-checked | extract the best path as a vertex list, re-measure its length and collision-check each leg |
| the cost ratio increases across checkpoints | the matched sample was not used, so hard seeds that solved late entered only the later checkpoints | check that the mask of criterion 1 is applied |
| the neighbour count grows proportionally to $n$ | the radius was constant, or the exponent of $(\log n/n)$ was not $1/2$ | print $r_n$ and compare with the values of P4 |
| the run takes over 20 minutes | the neighbour query was written as a Python loop | vectorize the distance computation with `np.einsum` and leave only the collision checks in a loop |
| many seeds find no solution | there is no goal bias and $\eta$ is too small | check that the number of successful seeds at $n = 250$ is near 77 |

## Open problems

- **(open problem) A theory of the convergence rate** — asymptotic optimality speaks only of the
  limit; there is no general theory of how fast $\mathbb{E}[Y_n] - c^\ast$ decreases in $n$. The
  improvement of about 1% across the four checkpoints of the reproduction task (criterion 3) is the
  practical size of that hole. Current approaches: dispersion-based rate bounds for deterministic
  sequences ([Janson, Ichter & Pavone 2018](https://arxiv.org/abs/1505.00023)), the reorganization in
  [Solovey et al. 2020](https://arxiv.org/abs/1909.09688). What is missing: upper and lower bounds on
  $\mathbb{E}[Y_n]$ under random sampling.
- **(open problem) What can be guaranteed on a finite budget** — a robot does not wait for
  $n \to \infty$. There is no result of the form "given $n$ iterations and the geometry of the
  environment, $Y_n \le (1+\epsilon)c^\ast$ with probability $1-\gamma$" (the same root as the
  "computable difficulty parameter" problem of the previous lesson). Current approaches: the
  empirical curves of anytime algorithms
  ([Strub & Gammell 2020](https://arxiv.org/abs/2002.06589)), the per-batch guarantees of
  [BIT*](https://arxiv.org/abs/1405.5848). What is missing: a finite-$n$ sub-optimality certificate —
  the same kind of thing the GCS relaxation of `c6-combinatorial-gcs` provides.
- **(open problem) The informed set when the cost is not length** — (2) is an ellipsoid only for a
  Euclidean length cost. For time-optimal, energy, curvature-constrained or differentially
  constrained costs the shape of the "can-still-improve" region is unknown, so informed sampling
  cannot be used. Current approach: reachable-set approximations under differential constraints (R1
  of `c6-kinodynamic-planning`). What is missing: a computable informed-set approximation for general
  costs, together with a proof that it preserves completeness.

## Concept check

Run `rc quiz c6-asymptotic-optimality`. Concept checking only; the real work is the problem set and
the reproduction task.

The six items cover: the one essential change from RRT to RRT*; why the radius rule needs the
$\log n$; what $\gamma^\ast$ requires and which way an error in it is safe; why informed sampling
barely helps in two dimensions; the scope of asymptotic optimality; and the expected neighbour count
under the radius rule.

## How to study this stage

1. **Write the two theorems side by side (20 min)** — put "RRT is not optimal" (R2) and "RRT* is
   optimal" (R1) on one page and mark the **single differing line** in the hypothesis lists
   (rewiring). That one line is the whole lesson.
2. **Decompose the radius rule into three requirements (70 min)** — derive requirements 1, 2 and 3 of
   R1 separately. Requirement 1 produces the $\log n$, requirement 2 a lower bound on the radius and
   requirement 3 an upper bound. Solving P1 and P6 alongside shows that the constant in $\gamma^\ast$
   is a function of the covering design.
3. **Turn it into numbers (40 min)** — do P3 and P4. Compute $\gamma^\ast = 12.3608$,
   $r_{2000} = 0.8382$, a neighbour count of 55, and the fact that the informed ellipsoid at
   $c_{best} = 1.1L^\ast$ is **larger** than the free space. That last fact is the most
   counter-intuitive point of the lesson.
4. **Run both algorithms from the same code (95 min)** — the reproduction task. Run RRT and RRT* on
   the **same seeds and the same sample stream** and overlay their cost curves. The goal is to see
   RRT's curve become a flat line, which is the proof of R2 as a picture. Then run once more without
   cost propagation.
5. **Three papers (130 min)** — read Theorems 33 and 38 of Karaman–Frazzoli first, the ellipsoid of
   Informed RRT* next, and BIT* last. BIT* also reads as the introduction to the next lesson
   (search-based planning), so leave a line in your note on "what the heuristic does".
6. **Problem set (160 min)** — P3 and P4 (numerical) and P7 (implementation) first, then P1 and P2
   (derivation), then P5, P6 and P8 with whatever time remains. P8 takes longest because it needs one
   more paper.

**Passing bar**: you can write a paragraph on each of the three requirements of the radius rule, you
can compute $\gamma^\ast$ and the informed-ellipsoid volume in a given environment, you have code
satisfying the five criteria of the reproduction task, and you can explain that "what separates RRT
from RRT* is one line of rewiring". You have notes on all three papers.
