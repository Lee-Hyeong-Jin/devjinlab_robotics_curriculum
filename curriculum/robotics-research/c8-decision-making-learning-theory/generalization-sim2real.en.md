---
id: c8-generalization-sim2real
lang: en
title: Generalization and sim-to-real theory
summary: >-
  Show that what domain randomization actually optimizes is the **average over the randomization
  distribution**, and compute exactly where that picks a different policy from the worst-case
  (robust) objective. Then derive the bound that limits the performance gap under distribution
  shift by a total-variation distance, and reproduce numerically how excessive randomization
  lowers performance at the unseen parameter. The lesson closes by showing that the information gap
  of privileged learning (teacher-student) is a Jensen gap.
objectives:
  - Derive that the implicit objective of domain randomization is $\mathbb{E}_{\xi\sim p}[J_\xi(\pi)]$.
  - Construct an instance where the average and worst-case objectives select different policies.
  - Derive the distribution-shift bound $\lvert\mathbb{E}_p[J] - \mathbb{E}_q[J]\rvert \le 2 V_{\max} D_{\mathrm{TV}}(p,q)$.
  - Compute the width at which performance at the unseen parameter drops as randomization widens.
  - Show that the performance gap between a teacher using privileged information and a student using observations is a Jensen gap.
  - Explain why teacher-student distillation cannot close that gap.
tags: [sim-to-real, domain-randomization, generalization, privileged-learning, research]
---

# Generalization and sim-to-real theory

## Setup and notation

The MDP notation of `c8-mdp-pomdp-bellman`, the distribution-shift viewpoint of
`c8-imitation-learning` and the model-error propagation of `c8-model-based-world-models` carry
over. Additional **recommended** background:

- Probability: total variation distance, Jensen's inequality, exchanging expectations over
  measures.
- Convex optimization: why swapping $\max$ and an expectation yields an inequality
  (`r0-convex-optimization`).
- Information theory: conditional entropy and the precise form of the intuition that "more
  information cannot reduce value".

Added notation:

| Symbol | Meaning |
|---|---|
| $\xi \in \Xi$ | domain parameters (mass, friction, latency, slip probability, …) that the simulator takes |
| $M_\xi$ | the MDP with parameter $\xi$; $J_\xi(\pi)$ is the value of $\pi$ in it |
| $p(\xi)$ | the **randomization distribution** (chosen by the designer); $q(\xi)$ is the real one (unknown) |
| $\xi_{\mathrm{real}}$ | the true parameter of the hardware; the extreme $q = \delta_{\xi_{\mathrm{real}}}$ is common |
| $\Pi_{\mathrm{mem}}$ | the set of memoryless policies that **do not see** $\xi$ |
| $\Pi_{\mathrm{full}}$ | the set of policies that see $\xi$ (privileged information) |
| $V_{\max}$ | $R_{\max}/(1-\gamma)$; every $J_\xi$ lies in $[0, V_{\max}]$ |
| $w$ | randomization width, $p = \mathrm{Unif}\big(\max(0, c-w),\, c+w\big)$ |

**This lesson in one line.** The practitioner's rule "randomize the simulator a lot and it will
work on hardware" is **not a theorem**. We follow, down to the numbers, exactly which objective
randomization optimizes (R1), how that objective connects to hardware performance (R2), and when
**widening is a loss** (R3).

## Key results

The bracket gives the derivation depth (`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the implicit objective of domain randomization) [D2]** — if $\xi\sim p$ is drawn at the
  start of each episode and the policy **does not see** $\xi$, then what learning optimizes is
  exactly
  $$
  \pi_{\mathrm{DR}} \in \arg\max_{\pi\in\Pi_{\mathrm{mem}}}\;
    \mathbb{E}_{\xi\sim p}\big[J_\xi(\pi)\big]. \tag{1}
  $$
  That is a **risk-neutral average**. It is a different problem from the robust objective
  $\max_\pi \min_{\xi\in\mathrm{supp}(p)} J_\xi(\pi)$, and the reproduction task computes exactly
  an instance where the two **select different policies** (at $w=0.3$ and $0.4$ the average
  optimum is the fast route while the worst-case optimum is the safe route).
- **R2 (the bound on performance under distribution shift) [D2]** — if $J_\xi \in [0, V_{\max}]$
  then for any two distributions $p, q$,
  $$
  \big\lvert \mathbb{E}_{p}[J_\xi(\pi)] - \mathbb{E}_{q}[J_\xi(\pi)] \big\rvert
    \;\le\; 2\,V_{\max}\,D_{\mathrm{TV}}(p, q), \tag{2}
  $$
  and if the hardware is **outside** the randomization support then $D_{\mathrm{TV}} = 1$ and (2)
  is **vacuous**. So the only theoretical role of randomization is "to put $q$ inside the
  support", which is a **coverage assumption** — an assumption, not a guarantee.
- **R3 (the harm of excessive randomization) [D2]** — widening $w$ makes the expectation in (1)
  cover more $\xi$, but **a single policy that cannot see $\xi$** cannot fit all $\xi$ at once.
  Widen far enough and the average-optimal policy **switches**, and at that moment performance at
  $\xi_{\mathrm{real}}$ falls like a step. The reproduction task computes a drop of **23.3%**, from
  $7.6950$ at $w \le 0.4$ to $5.9049$ at $w \ge 0.5$.
- **R4 (the information gap of privileged learning is a Jensen gap) [D2]** — the performance
  difference between a teacher that sees $\xi$ and a student that does not is
  $$
  \underbrace{\mathbb{E}_{\xi\sim p}\Big[\max_{\pi} J_\xi(\pi)\Big]}_{\text{teacher}}
  \;-\;
  \underbrace{\max_{\pi\in\Pi_{\mathrm{mem}}}\mathbb{E}_{\xi\sim p}\big[J_\xi(\pi)\big]}_{\text{the student's ceiling}}
  \;\ge\; 0 \tag{3}
  $$
  which is the **Jensen gap from swapping $\max$ and $\mathbb{E}$**. However well distillation
  imitates the teacher, that gap does not shrink — what the student lacks is not skill but
  **information**. The reproduction task computes a non-monotone curve in which the gap grows from
  $0$ to $0.5436$ and then shrinks again.
- **R5 (the only way to close the gap is to recover information) [D1]** — give the student an
  **observation history** and it can estimate $\xi$ implicitly, shrinking the gap. That is the
  principle of RMA and teacher-student adaptation, and read through the belief MDP of
  `c8-mdp-pomdp-bellman` R3 it is the statement that "the student solves a POMDP while the teacher
  solves an MDP". The exact size of the gap depends on how identifiable $\xi$ is from observations,
  and quantifying that in general is an open problem.

## Derivation

### R1 — what randomization optimizes

Write the training loop literally. Each episode draws $\xi_i \sim p$, collects a trajectory with
$\pi_\theta$ in that environment and obtains a return $\hat{J}_i$. Using the policy gradient
(`c8-policy-gradient` R1), the expectation of the estimator is

$$
\mathbb{E}_{\xi\sim p}\Big[\nabla_\theta J_\xi(\pi_\theta)\Big]
  = \nabla_\theta\,\mathbb{E}_{\xi\sim p}\big[J_\xi(\pi_\theta)\big]
$$

(the exchange is legitimate because $J_\xi$ is bounded and smooth in $\theta$). So **the gradient
is the gradient of the average objective** and the limit point is a stationary point of (1). That
the policy does not take $\xi$ as an input is decisive — if it did, the problem would separate into
an independent optimization per $\xi$.

**Average is not worst case.** $\mathbb{E}_p[J_\xi]$ is a linear functional of $p$, so it sees only
the **average** (linear in $p$ even for a nonlinear $J_\xi$). A bad $\xi$ in the tail is therefore
penalized only in proportion to its mass. By contrast $\min_{\xi\in\mathrm{supp}(p)} J_\xi$ is
decided by the worst point **regardless of mass**. On the grid of the reproduction task, at
$w = 0.3$ the average optimum is the fast route (its expected return is higher) while the
worst-case optimum is the safe route (it does not collapse in the worst case) — they **split**.

**Where the assumptions break.** If the policy can see $\xi$ **indirectly** (history, sensors), the
separation of (1) breaks and the problem becomes a belief MDP (R5). And randomizing "within an
episode" (redrawing $\xi$ every step) is not the average objective at all but solving **a single
MDP with different dynamics** — calling both of these by the same name is a common practical
confusion.

### R2 — the limits of distribution shift

Assume $J_\xi(\pi) \in [0, V_{\max}]$. Using the definition
$D_{\mathrm{TV}}(p,q) = \tfrac12\int\lvert p-q\rvert$,

$$
\big\lvert \mathbb{E}_p[J] - \mathbb{E}_q[J] \big\rvert
  = \Big\lvert \int J_\xi\big(p(\xi) - q(\xi)\big)\,d\xi \Big\rvert
  \le \sup_\xi \lvert J_\xi \rvert \int \lvert p - q\rvert
  = V_{\max}\cdot 2 D_{\mathrm{TV}}(p,q),
$$

which is (2). To tighten it, $\sup\lvert J\rvert$ can be replaced by the **span**
$\tfrac12(\max J - \min J)$ (the same technique as P1 of `c8-model-based-world-models`).

**How to read it, and its limit.** (2) is the only general guarantee that carries "average
performance in simulation" to "average performance in reality". But if the hardware is a single
point $\xi_{\mathrm{real}}$ outside $\mathrm{supp}(p)$ then
$D_{\mathrm{TV}}(p, \delta_{\xi_{\mathrm{real}}}) = 1$ and the bound is $2V_{\max}$ — **no
information at all**. Even inside the support, the TV distance to a point mass is close to 1. To
make (2) useful one must add an assumption that $J_\xi$ is **continuous and gentle** in $\xi$
(Lipschitz) and look near $\xi_{\mathrm{real}}$ instead of at $\mathbb{E}_p$:

$$
J_{\xi_{\mathrm{real}}}(\pi) \;\ge\; \mathbb{E}_p[J_\xi(\pi)]
  - L\,\mathbb{E}_p\big[\lVert \xi - \xi_{\mathrm{real}}\rVert\big] , \tag{4}
$$

where $L$ is the Lipschitz constant of $\xi \mapsto J_\xi(\pi)$. (4) shows immediately that
**widening is not free** — the second term grows with the width.

**Where the assumptions break.** If $J_\xi$ is discontinuous in $\xi$ then $L$ in (4) is infinite.
The boundary where contact appears and disappears, the critical friction at which a wheel starts to
slip — **situations that are common in robotics** — are exactly such discontinuities. So the
relation between randomization width and performance is not a smooth curve but a **step**, and the
switch of R3 is that step.

### R3 — the point at which widening becomes a loss

Use the environment of the reproduction task directly. At the start state one chooses between two
routes.

- **Fast route**: reaches the goal in 2 steps but fails with probability $\xi$ into an absorbing
  state. $J_{\mathrm{fast}}(\xi) = \gamma^2 \frac{1}{1-\gamma}(1-\xi) = 8.1\,(1-\xi)$ at
  $\gamma=0.9$.
- **Safe route**: reaches the goal in 5 steps **with certainty**.
  $J_{\mathrm{slow}} = \gamma^5\frac{1}{1-\gamma} = 5.9049$.

The two are equal when $1-\xi = \gamma^3$, i.e. at

$$
\xi^\star = 1 - \gamma^3 = 0.271 . \tag{5}
$$

Below $\xi^\star$ the fast route is better; above it the safe route is.

**Now apply (1).** With $p = \mathrm{Unif}(\max(0,c-w),\,c+w)$ and $J$ **linear** in $\xi$,
$\mathbb{E}_p[J_{\mathrm{fast}}] = 8.1(1 - \bar{\xi})$ with $\bar{\xi} = \mathbb{E}_p[\xi]$. So the
average-optimal policy is decided by $\bar{\xi}$ alone:

$$
\pi_{\mathrm{DR}} = \begin{cases}
  \text{fast route} & \bar{\xi} < \xi^\star,\\
  \text{safe route} & \bar{\xi} > \xi^\star .
\end{cases} \tag{6}
$$

**The key is that $\bar{\xi}$ depends on $w$.** Physically $\xi \ge 0$, so the lower end is clipped
at zero and

$$
\bar{\xi}(w) = \begin{cases} c & w \le c,\\[2pt] \dfrac{c+w}{2} & w > c, \end{cases} \tag{7}
$$

i.e. **widening raises the mean itself**. At $c = 0.05$ the switch in (6) happens when
$(0.05+w)/2 > 0.271$, i.e. at $w > 0.492$. As a result, performance at the true value
$\xi_{\mathrm{real}} = 0.05$

$$
J_{0.05}(\pi_{\mathrm{DR}}) = \begin{cases} 8.1\times0.95 = 7.6950 & w \le 0.49,\\
  5.9049 & w \ge 0.50, \end{cases}
$$

**falls by 23.3%**. That is the simplest exact form of "the harm of excessive randomization".

**Why a step?** Because $\Pi_{\mathrm{mem}}$ is finite (or the decision is discrete). In a
continuous policy space the switch becomes smooth, but in tasks with a **discrete decision** — such
as "which route to take" — the step remains. Selecting a locomotion mode or a grasp strategy on a
robot is such a discrete decision.

**Where the assumptions break.** (7) holds because of the clipping at the lower end. For a
parameter that can be extended symmetrically (a sensor bias, say) the mean does not change, there is
no switch, and the harm shows up only through the **variance** channel (problem P5). And (6) used
the special fact that $J$ is linear in $\xi$ — if it is nonlinear, $\mathbb{E}_p[J]$ depends on
moments beyond the mean and the switching condition changes.

### R4 — the teacher-student information gap

The teacher sees $\xi$, so it can be optimal separately at each $\xi$:
$\mathbb{E}_p[\max_\pi J_\xi(\pi)]$. The student cannot see $\xi$ and must **commit** to one policy:
$\max_{\pi\in\Pi_{\mathrm{mem}}}\mathbb{E}_p[J_\xi(\pi)]$. Since $\max$ is a convex functional,

$$
\mathbb{E}_p\Big[\max_\pi J_\xi(\pi)\Big] \;\ge\; \max_\pi \mathbb{E}_p\big[J_\xi(\pi)\big] , \tag{8}
$$

which is (3). Equality holds only when **some single policy is simultaneously optimal for every
$\xi \in \mathrm{supp}(p)$**.

**The shape of the gap.** In the environment of the reproduction task, when $w$ is small enough that
$\mathrm{supp}(p)$ lies entirely on one side of $\xi^\star$, one route is optimal for every $\xi$
and the gap is **exactly zero** (measured $0$ for $w \le 0.2$). Once the width **starts to straddle**
$\xi^\star$ a gap appears ($0.0735$ at $w=0.3$), it is maximal at the width that covers the
neighbourhood of $\xi^\star$ most ($0.5436$ at $w=0.5$), and widening further dilutes the mass and
shrinks it again ($0.2873$ at $w=1.0$). It is **non-monotone**.

**Distillation does not close the gap.** Teacher-student distillation makes the student imitate the
teacher's action distribution. But the student's best is
$\mathbb{E}[\pi_{\text{teacher}}(\cdot\mid s,\xi)\mid s]$ — an **average** conditioned on the
observation. A policy that mixes two routes half and half may travel neither properly (the same
structure as the multi-modal expert problem of `c8-imitation-learning`). So however high the quality
of distillation, the gap in (8) remains — **what the student lacks is information, not imitation
ability.**

**Where the assumptions break.** (8) presumes the student gets **no information at all** about
$\xi$. A real student can partially identify $\xi$ from its observation history (if the floor is
slippery, its feet slip), and the gap shrinks accordingly. That identifiability is R5, and
quantifying it exactly is an open problem.

## Proof sketch

### R1, R3 and R4 — the average objective, the switch, and the Jensen gap [D2]

**Hypotheses** H1: $\xi\sim p$ is drawn once at the start of an episode and held fixed within it.
H2: the policy takes neither $\xi$ nor the history as input ($\Pi_{\mathrm{mem}}$). H3:
$J_\xi \in [0,V_{\max}]$ and $\theta\mapsto J_\xi$ is smooth. H4: $\Pi_{\mathrm{mem}}$ is finite
(or the decision is discrete).
**Conclusions** C1: (1). C2: (6), (7) and the resulting performance step. C3: (3).

**Strategy**: C1 by **exchanging expectation and gradient**; C2 by using the $\xi$-linearity of $J$
to leave only the mean and substituting the clipped uniform mean (7); C3 by the **convexity of
$\max$** (Jensen).

1. Show the expectation of the gradient estimator is $\nabla\mathbb{E}_p[J_\xi]$ → C1. Uses: H1,
   H2, H3.
2. In the reproduction environment, obtain $J_{\mathrm{fast}}(\xi) = 8.1(1-\xi)$ and
   $J_{\mathrm{slow}} = 5.9049$ by linear solve and get the crossover (5).
3. Use that $\mathbb{E}_p[J_{\mathrm{fast}}]$ depends on $\bar{\xi}$ alone and substitute (7)
   → (6) → C2. Uses: $\xi$-linearity of $J$, H4 (a discrete decision, hence a step).
4. Use that $\max$ is a convex functional → (8) → C3. Equality requires a common optimal policy.

**Delete one hypothesis**: allowing history in H2 lets the student estimate $\xi$, shrinking the gap
of C3 (R5), and the problem becomes a belief MDP so the "average objective" reading of C1 is no
longer exact. Redrawing $\xi$ every step in H1 makes it **a single different MDP**, a different
problem from (1). Dropping H4 (a continuous policy space) smooths the switch and turns the step of
C2 into a gentle curve.

Omitted: the argument that a stationary point of (1) exists for continuous $\Xi$ and a continuous
policy space relies on standard stochastic-approximation assumptions.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Derive (2) and write the tightened form with $\sup\lvert J\rvert$
replaced by the span. Then explain why (2) becomes vacuous when the hardware is a point mass
$\delta_{\xi_{\mathrm{real}}}$, and how (4) circumvents that.
*Solution sketch*: (2) is one line of Hölder. The span version uses $\int(p-q) = 0$, so subtracting
a constant from $J$ does not change the value. At a point mass $D_{\mathrm{TV}} = 1$ (disjoint
supports, or a continuous distribution against a point mass) and the bound is the trivial
$2V_{\max}$. (4) uses a distance in **parameter space** with a Lipschitz constant instead of a
distance between distributions, so it stays finite even at a point mass.

**P2 (proof, ★★★, R4)** Prove (8) and state the **necessary and sufficient** condition for
equality. Then explain, in terms of the observation-conditional average, why the claim "with
perfect distillation the student catches up with the teacher" is false.
*Strategy and key inequality*: $\max$ is the supremum of pointwise suprema, so for any fixed $\pi$,
$\mathbb{E}_p[\max_{\pi'}J_\xi(\pi')] \ge \mathbb{E}_p[J_\xi(\pi)]$, and taking the $\max$ of the
right side finishes it. Equality holds only when **a $\pi$ optimal at every $\xi$ exists**. The
limit of distillation follows from the student's optimum being
$\mathbb{E}[\pi_{\text{teacher}}\mid o]$. The expansion is withheld.

**P3 (numerical, ★, R3)** In the reproduction environment with $\gamma = 0.9$ and $c = 0.05$,
compute $\xi^\star$ of (5), $\bar{\xi}(w)$ of (7), and the width $w^\star$ at which the
average-optimal policy switches. What is the performance at $\xi_{\mathrm{real}} = 0.05$ before and
after the switch, and the drop?
*Answer*: $\xi^\star = 1-\gamma^3 = 0.271$ (tolerance $10^{-6}$).
$\bar{\xi}(w) = c$ for $w\le c$ and $(c+w)/2$ for $w>c$. The switch is at $(0.05+w)/2 = 0.271$,
i.e. $w^\star = 0.492$. The performance goes $8.1\times0.95 = 7.6950 \to 5.9049$, a drop of
$1 - 5.9049/7.6950 = 23.26\%$ (tolerance $0.01\%$).
Check: change $\gamma$ to $0.95$ and confirm that $\xi^\star = 1-0.95^3 = 0.1426$ becomes
**smaller** and so does $w^\star$ — with weaker discounting the penalty of the slow route is smaller
so the safe route wins sooner.

**P4 (implementation, ★★, R1·R3·R4)** Implement the grid of the reproduction task and tabulate the
average optimum of (1), the worst-case optimum, and the information gap of (3) against the width
$w$.
*Rubric*: ⓐ $J_\xi(\pi)$ is computed exactly by a **linear solve** (no Monte Carlo — this task
admits exact computation); ⓑ the memoryless deterministic policies are **fully enumerated**
($2^{\lvert\mathcal{S}\rvert}$); ⓒ the three objectives (average, worst case, teacher) are compared
on the same grid; ⓓ the $\xi$ grid is fine enough that the switching width does not depend on its
resolution; ⓔ the clipping of $\bar{\xi}$ in (7) is handled explicitly in the code.

**P5 (counterexample, ★★, R3)** Show that **both** of the claims "widening randomization always
lowers average performance" and "it always raises it" are false. Construct a counterexample to each,
and say what changes for a symmetric parameter with no clipping as in (7).
*Property checklist*: ⓐ widening $\xi$ symmetrically (holding $\mathbb{E}[\xi]$) leaves the average
objective **unchanged** in a task where $J$ is linear in $\xi$ — no switch and no harm; ⓑ if $J$ is
convex in $\xi$, Jensen makes the average **rise**; ⓒ if concave, it falls; ⓓ so harm or benefit is
decided not by the width itself but by **the curvature of $J_\xi$ and the shift of the mean**. That
distinction is the heart of R3.

**P6 (paper, ★★, R1·R3·R4)** Read Tobin et al. 2017 (§III–IV), EPOpt (§3–4) and Learning by
Cheating (§3–4) and write, in at most three sentences each: (i) which distribution of (1) Tobin et
al.'s randomization corresponds to and what evidence is offered for real-world transfer; (ii) the
objective EPOpt optimizes instead of the average and where it sits in the contrast of R1; (iii)
whether the student-teacher performance difference in Learning by Cheating is explained by the gap
of (3).
*Grading rubric*: (i) that the visual randomization distribution was fixed by hand by the designer
and that the evidence is **experimental** transfer. (ii) that it is a CVaR-style **tail** objective
and sits on the robust side of R1. (iii) passes if it distinguishes whether the cause of the gap is
information (privileged state) or capacity and optimization. Writing only "randomization helps"
fails.

**P7 (derivation, ★★, R2·R5)** Derive (4), and explain through the belief MDP of
`c8-mdp-pomdp-bellman` R3 why giving the student an observation history shrinks the gap of (3). When
is the gap zero?
*Solution sketch*: (4) follows by averaging
$J_{\xi_{\mathrm{real}}} \ge J_\xi - L\lVert\xi-\xi_{\mathrm{real}}\rVert$ over $p$. With a history
the state becomes $(s, b(\xi))$, so the policy set grows and the $\max$ increases. The gap is zero
when ⓐ $\xi$ is **fully identified** from observations (the belief collapses to a point mass) or
ⓑ a policy optimal at every $\xi$ exists.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions
(`lesson-standard.md` §5). Read with three passes and attack questions 4, 5, 6 and 7 in the third.

1. **Tobin, Fong, Ray, Schneider, Zaremba & Abbeel, "Domain randomization for transferring deep
   neural networks from simulation to the real world" (2017, IROS)** — role: `seminal`.
   <https://arxiv.org/abs/1703.06907> — §III-IV.
   Why read it: the origin of randomization as a practice, and a case where the distribution $p$ of
   (1) was **fixed by hand by the designer**.
   Extra questions: ⓐ which components of $\xi$ are the elements the authors randomized (textures,
   lighting, camera), and why did they not randomize the dynamics? ⓑ is the evidence offered for
   real-world transfer a theorem or an experiment?
2. **Rajeswaran, Ghotra, Ravindran & Levine, "EPOpt: learning robust neural network policies using
   model ensembles" (2017, ICLR)** — role: `standard`. <https://arxiv.org/abs/1610.01283> — §3-4.
   Why read it: it optimizes the **tail** (CVaR) instead of the average, standing on the robust side
   of the contrast in R1.
   Extra questions: ⓐ what does the CVaR level $\epsilon$ become at 1 and what does it approach near
   0? ⓑ how does the authors' model adaptation (Bayesian update) correspond to the information
   recovery of R5?
3. **Chen, Zhou, Koltun & Krähenbühl, "Learning by cheating" (2020, CoRL)** — role: `standard`.
   <https://arxiv.org/abs/1912.12294> — §3-4.
   Why read it: an explicit two-stage privileged-teacher to observation-student structure, where one
   can see where the gap of (3) actually appears.
   Extra questions: ⓐ can the paper's experiments distinguish whether the reported student-teacher
   difference is a lack of **information** or of **capacity and optimization**? ⓑ which of the
   privileged inputs given to the teacher can the student **not** recover from observations?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation? (4) what is guaranteed and **what is not**?
(5) independent and dependent variables, and the baselines — were they tuned fairly? (6) does the
metric match the claim, and are variance and seeds reported? (7) what information needed for
reproduction is missing? (8) if the result were wrong, which assumption would you doubt first?
(9) compute and memory cost, and real-time feasibility? (10) what would you change to go beyond
this paper in a year?

## Reproduction task

**Tier R1 (numerical check).** Compute budget: under **one minute** on a laptop CPU (measured: 10
widths × 201 grid points × 256 policies, about 510,000 $8\times8$ linear solves, roughly 15 s),
under 100 MB, numpy only. **No Monte Carlo** — everything here is computed exactly by linear solves. That is the
point: claims that "randomization helps or hurts" are decided **without estimation error**.

**The environment.** Eight states: the start $S$, the fast corridor $F$, the slow corridor
$L_1..L_4$, the goal $G$ (absorbing, reward 1) and failure $B$ (absorbing, reward 0). From $S$,
action 0 goes to $F$ and action 1 to $L_1$. From $F$ one reaches $G$ with probability $1-\xi$ and
$B$ with probability $\xi$. The chain $L_1\to L_2\to L_3\to L_4\to G$ is deterministic.
$\gamma = 0.9$. The randomization distribution is
$p_w = \mathrm{Unif}\big(\max(0,c-w),\,c+w\big)$ with $c = 0.05$, and the hardware is
$\xi_{\mathrm{real}} = 0.05$.

```python
import numpy as np

GAMMA = 0.9
NS, NA = 8, 2
S, F, L1, L2, L3, L4, G, B = range(8)


def mdp(xi):
    P = np.zeros((NS, NA, NS))
    R = np.zeros((NS, NA))
    P[S, 0, F] = 1.0
    P[S, 1, L1] = 1.0
    for a in range(NA):
        P[F, a, G], P[F, a, B] = 1.0 - xi, xi
        P[L1, a, L2] = P[L2, a, L3] = P[L3, a, L4] = P[L4, a, G] = 1.0
        P[G, a, G] = P[B, a, B] = 1.0
        R[G, a] = 1.0
    return P, R
```

**Fully enumerate** the $2^8 = 256$ memoryless deterministic policies and, at each $\xi$ grid
point, compute $J_\xi(\pi) = \big[(I-\gamma P^\pi)^{-1}r^\pi\big]_S$ by linear solve.

**Acceptance criteria** — all five must hold.

1. **Agreement with the closed form**: the two routes' values match
   $J_{\mathrm{fast}}(\xi) = \frac{\gamma^2}{1-\gamma}(1-\xi) = 8.1(1-\xi)$ and
   $J_{\mathrm{slow}} = \frac{\gamma^5}{1-\gamma} = 5.9049$ to within $10^{-12}$, and the crossover
   matches $\xi^\star = 1-\gamma^3 = 0.271$ to within $10^{-9}$.
2. **The switching width of the average objective**: computing $\bar{\xi}(w)$ of (7) in code, the
   width at which the average-optimal policy switches matches
   $w^\star = 2\xi^\star - c = 0.492$ to within the grid resolution. On the grid
   $w \in \{0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0\}$, $w \le 0.4$ gives the fast route
   and $w \ge 0.5$ the safe route.
3. **The harm of excessive randomization**: at $\xi_{\mathrm{real}} = 0.05$,
   $J(\pi_{\mathrm{DR}})$ is $7.6950$ for $w \le 0.4$ and $5.9049$ for $w \ge 0.5$, a drop of
   $23.26\%$ ($\pm0.01\%$).
4. **Average $\neq$ worst case**: at $w \in \{0.3, 0.4\}$ the average-optimal policy is the fast
   route while the worst-case ($\min_{\xi\in\mathrm{supp}(p_w)} J_\xi$) optimum is the safe route —
   the two objectives **select different policies**. They agree for $w \le 0.2$ and $w \ge 0.5$.
5. **Non-monotonicity of the information gap**: with the $\xi$ grid **fixed at 201 uniform points**
   per width, the gap of (3) is exactly $0$ for $w \le 0.2$, $0.0735$ at $w = 0.3$, $0.2906$ at
   $w = 0.4$, a maximum of $0.5436$ at $w = 0.5$, and then **shrinks again** to $0.4608$ at
   $w = 0.6$ and $0.2873$ at $w = 1.0$ (all $\pm10^{-4}$). Report together the reason the gap is
   zero on that interval (the existence of a common optimal policy). **Raising the grid to 2001
   points lowers the values by about $4\times10^{-3}$** (measured: $0.5436 \to 0.5411$ at
   $w=0.5$) — the error of approximating the integral by a Riemann sum, shrinking as $O(1/n)$.
   Compare against the reference numbers with the grid fixed at 201, and separately increase $n$ to
   confirm that the drift is $O(1/n)$.

**Baselines**: ⓐ the two fixed policies (always fast / always safe) — a sanity check that the
enumeration returns one of these two. ⓑ the teacher (optimal at each $\xi$) — the ceiling for
criterion 5. ⓒ optional: run a variant that widens $\xi$ **symmetrically** ($c = 0.25$ with
$w \le 0.25$, so no clipping occurs) and confirm that both the switch and the harm **disappear** —
as $w$ grows from $0$ to $0.25$ the measured mean stays $0.2500$, the choice stays the fast route,
and $J$ stays at $6.0750$ (problem P5).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| $J_{\mathrm{slow}}$ in criterion 1 comes out as $6.561$ | the slow corridor was given length 3 instead of 4 | print the first time $G$ is reached — it must be 5 (hence $\gamma^5$) |
| The switching width in criterion 2 differs | $\bar{\xi}$ was fixed at $c$ and the clipping (7) was not handled | print $\bar{\xi}$ and check it equals $(c+w)/2$ for $w > c$ |
| The drop in criterion 3 is zero | the evaluation was at the $p_w$ average rather than at $\xi_{\mathrm{real}}$ | print the $\xi$ used for evaluation — it must always be $0.05$ |
| The two objectives always agree in criterion 4 | the worst case was computed as a mean rather than the grid minimum | print `JJ.min(axis=1)` and `JJ.mean(axis=1)` side by side |
| The gap in criterion 5 is negative | the order of $\max$ and $\mathbb{E}$ was swapped between teacher and student | the teacher is `JJ.max(axis=0).mean()` and the student `JJ.mean(axis=1).max()` |
| Criterion 5's values differ from the reference by about $10^{-3}$ | the grid is not 201 points — the gap is a Riemann sum and depends on $n$ as $O(1/n)$ | print the grid size; check that the gap at $w=0.5$ converges as $0.5436/0.5415/0.5411$ for 201/801/2001 |

## Open problems

- **(open problem) A principle for choosing the randomization distribution** — (1) says that
  randomization optimizes the **average** but not which $p$ to choose. Widening increases coverage
  but also the second term of (4) and the switching harm of R3. There is no rule for choosing $p$
  without hardware data, and practice tunes it by hand. Current approaches: learning the
  randomization distribution ([active domain randomization](https://arxiv.org/abs/1904.04762)),
  optimizing the tail ([EPOpt](https://arxiv.org/abs/1610.01283)). What is missing: a criterion for
  setting the width of $p$ given a target performance.
- **(open problem) Quantifying the information gap of privileged information** — (3) gives that a
  gap **exists** and that it is a Jensen gap, but there is no way to compute its size **in advance**
  for a given observation space. A general theorem linking the identifiability of $\xi$ from
  observations to the gap is missing. Current approaches: compressing privileged information into a
  latent variable the student estimates online ([RMA](https://arxiv.org/abs/2107.04034)), two-stage
  teacher-student training ([Lee et al. 2020](https://arxiv.org/abs/2010.11251),
  [Miki et al. 2022](https://arxiv.org/abs/2201.08117)). What is missing: a theorem from
  identifiability to a bound on the gap.
- **(open problem) The correlation between simulated evaluation and hardware performance** — (2) and
  (4) give **upper bounds** on the performance difference, but what practice needs is **order
  preservation**: if A beats B in simulation, does it on hardware? An upper bound does not guarantee
  an ordering. Current approaches: measuring the correlation directly
  ([SIMPLER](https://arxiv.org/abs/2405.05941)), evaluation methodology
  ([Agarwal et al. 2021](https://arxiv.org/abs/2108.13264)). What is missing: a simulated-evaluation
  design that guarantees order preservation.
- **(open problem) Transfer at discontinuous boundaries** — the Lipschitz constant of (4) is
  infinite at **discontinuous** boundaries such as contact onset, the slip threshold and mode
  switches. Robot failures mostly happen at those boundaries, yet randomization only shakes the
  boundary and covers it on average — it does not guarantee **performance near the boundary**.
  Current approaches: trajectory optimization that treats contact explicitly
  ([Posa et al. 2014](https://doi.org/10.1177/0278364913506757)), runtime out-of-distribution
  detection ([Sinha et al. 2022](https://arxiv.org/abs/2212.14020)). What is missing: a transfer
  guarantee near discontinuous boundaries.

## Concept check

Run `rc quiz c8-generalization-sim2real`. The quiz is for **concept checking only**; the real work
is the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: which objective is optimized when $\xi\sim p$ is drawn per episode and the
policy cannot see it; whether widening randomization monotonically improves performance at the
unseen parameter; what the bound of (2) becomes when the hardware lies outside the support; whether
distillation lets the student catch the teacher; and the crossover slip probability in terms of
$\gamma$.

## How to study this stage

1. **Write down "what is being optimized" first (45 min)** — write the one-line derivation of R1
   from a blank page and put the average, the worst case and the average-parameter MDP side by side.
   Deciding which of the three a practitioner's sentence ("randomize and it gets robust") means is
   the first gain of this lesson.
2. **Confirm that the bound is vacuous (30 min)** — derive (2) and see for yourself that the bound
   becomes $2V_{\max}$ when the hardware is a point mass. Then move to (4) and write down **what
   must be assumed additionally** for it to be useful.
3. **Compute the switching width by hand (45 min)** — compute $\xi^\star$ of (5) and the clipped
   mean of (7) to derive $w^\star = 2\xi^\star - c$. Solving problem P3 and varying $\gamma$ gives a
   feel for which way discounting pushes the switch.
4. **Build the grid yourself (95 min)** — the reproduction task is all linear solves, so **there is
   no estimation error**. Pass criteria 1–3, then move to criterion 4 (average versus worst case) and
   5 (the information gap). Seeing the interval where the gap is zero and the width where it is
   maximal turns (3) into a picture.
5. **Separate the information gap from distillation (60 min)** — solve problem P2 and write "the
   student's best = the observation-conditional average". Then reread the multi-modal expert item of
   `c8-imitation-learning` and confirm it is **the same structure**. Connecting the two lessons is
   the last link of this module.
6. **The three papers and the open problems (170 min)** — Tobin et al. (the origin) → EPOpt (the
   robust side) → Learning by Cheating (teacher-student). Write the one-page note for each; this is
   **not** optional. Finally, pick the open problem of quantifying the information gap and write a
   paragraph on how much the gap would shrink in the reproduction environment if the student were
   given **one experience of slipping at $F$**.

**Passing bar**: you can derive (1), (2) and (8) from a blank page, compute
$w^\star = 2\xi^\star - c$, quote the width at which the average and worst-case objectives split and
the width at which the information gap is maximal, and you hold code satisfying the five acceptance
criteria plus notes on the three papers.
