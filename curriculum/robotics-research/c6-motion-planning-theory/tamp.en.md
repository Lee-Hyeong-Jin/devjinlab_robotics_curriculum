---
id: c6-tamp
lang: en
title: TAMP (task and motion planning)
summary: >-
  Solving the symbolic and the continuous in one problem. First settle decidability — fixing the plan
  skeleton makes feasibility decidable by Tarski–Seidenberg, but with no bound on the length the
  problem is in general only semi-decidable, so **infeasibility cannot be decided**. Then derive the
  three conditions a sampling-based TAMP needs for probabilistic completeness (dense streams, a
  complete symbolic search, fair interleaving), and finally see the structure by which contact-mode
  enumeration blows up as $3^{n_c}$. The reproduction task runs a reduced-scale block-stacking TAMP
  and measures plan length growing linearly while the search grows exponentially.
objectives:
  - Explain why feasibility of a TAMP with a fixed plan skeleton is decidable and why its cost is doubly exponential.
  - Argue that without a bound on the length, TAMP is only semi-decidable and infeasibility cannot be decided.
  - State each of the three conditions for probabilistic completeness of a sampling-based TAMP, with a counterexample for each.
  - Count the $3^{n_c}$ contact modes and the $|\mathcal{M}|^K$ mode sequences, and write the ways of mitigating that blow-up.
  - Separate "what is hard" by measuring the growth rates of the search-node count and the plan length.
tags: [motion-planning, tamp, decidability, symbolic-planning, contact-modes, research]
---

# TAMP (task and motion planning)

## Setup and notation

The six earlier lessons of this module are assumed. Assumption **(A3) full information** of
`c6-cspace-complexity` still holds, but the free space is no longer a single open set — picking an
object up changes the configuration space itself. Also assumed:

- Symbolic planning: states, actions, preconditions and effects at the level of STRIPS/PDDL. That
  planning is PSPACE-complete (symbolic only, finite states) is the same framework as the complexity
  discussion of `c6-cspace-complexity`.
- Real algebraic geometry: only the **conclusion** of Tarski–Seidenberg about semialgebraic sets
  (already used in the upper bound of `c6-cspace-complexity` R3).
- Decidability vocabulary: decidable, semi-decidable (recursively enumerable).

Notation:

| Symbol | Meaning |
|---|---|
| $s \in \mathcal{S}$ | symbolic (discrete) state, e.g. `on(A,B)`, `holding(C)` |
| $a(\theta)$ | parameterized action; $\theta$ is a **continuous parameter** (grasp, placement pose, trajectory) |
| $\pi = \langle a_1, \dots, a_K\rangle$ | a **plan skeleton** — a sequence of actions with parameters undetermined |
| $\Theta(\pi)$ | parameter space of the skeleton $\pi$, with $\theta \in \Theta(\pi)$ |
| $\mathcal{F}(\pi) \subset \Theta(\pi)$ | the parameters satisfying the geometric and dynamic constraints |
| $\mathcal{M}$ | set of contact modes |
| $n_c$ | number of contact points |
| $K$ | length of a mode sequence (or of a skeleton) |
| $\ell$ | stream sampling level — how many candidates each sampler has produced |

**The TAMP problem.** The input is a symbolic domain (actions, preconditions, effects), the geometry
(robot, objects, obstacles), an initial state and a goal condition. The output is a pair
**skeleton $\pi$ and parameters $\theta \in \mathcal{F}(\pi)$**. In other words TAMP is a
**two-layer search**:

$$
\exists\, \pi \;\; \exists\, \theta \in \Theta(\pi): \quad \theta \in \mathcal{F}(\pi).
  \tag{1}
$$

The outer quantifier ranges over a **discrete, infinite** set (there is no bound on the length) and
the inner one over a continuum. That structure determines everything about decidability (R1) and
completeness (R2).

One assumption, stated explicitly: **(A7) parameter clearance** — if a solution exists, one exists
**in the interior** of $\mathcal{F}(\pi)$ (i.e. $\mathcal{F}(\pi)$ contains a neighbourhood of
$\theta$ of positive measure). It is the counterpart of the clearance $\delta > 0$ of the earlier
lessons, and every guarantee of R2 depends on it. Tasks demanding exact contact (an assembly where
faces must meet exactly) make $\mathcal{F}$ a **lower-dimensional manifold** and (A7) fails.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof).

- **R1 (two layers of decidability) [D2]** — (a) **With the skeleton fixed**, if the constraints are
  semialgebraic then $\mathcal{F}(\pi) \ne \emptyset$ is **decidable**, at a cost doubly exponential
  in the number of variables (the same bound as `c6-cspace-complexity` R4). (b) **With no bound on
  the skeleton length**, (1) admits only the **semi-decision** procedure of enumerating skeletons and
  deciding each — it finds a solution when one exists but **does not halt when none does**.
  (c) Hence **no algorithm outputs "infeasible"** for general TAMP. That is the same conclusion as
  `c6-sampling-completeness` R4(b) but for a different reason — there it was a property of sampling,
  here it is **the structure of the problem**.
- **R2 (conditions for probabilistic completeness of sampling-based TAMP) [D2]** — under (A7),
  three conditions are **all** needed. (a) **Dense streams**: every sampler draws densely, with
  positive density, on its constraint manifold. (b) **Completeness of the symbolic search**: given the
  objects and parameters generated so far, the symbolic planner finds a plan if one exists.
  (c) **Fair interleaving**: every (skeleton, sample-count) pair is tried in finite time (iterative
  deepening). With all three,
  $$\mathbb{P}[\text{failure up to level } \ell] \longrightarrow 0 \quad (\ell \to \infty)
    \tag{2}$$
  and dropping any one of them admits a counterexample (§R2).
- **R3 (blow-up of contact-mode enumeration) [D2]** — if each of $n_c$ contact points is in one of
  {separated, sticking, sliding}, the number of modes is
  $$|\mathcal{M}| = 3^{n_c} \tag{3}$$
  and there are $3^{n_c K}$ mode sequences of length $K$. Discretizing the sliding direction into $k$
  directions makes it $(2 + k)^{n_c}$. **Because the mode sequence plays the role of the symbolic
  skeleton**, the enumeration of R1(b) appears here as a concrete number.
- **R4 (separating what is hard) [D2]** — in the reproduction task, stacking $n$ blocks has a
  **plan length of $2n$, linear**, while the **number of search nodes grows exponentially** in $n$
  ($\approx 12.5^n$, $r^2 = 0.993$). So the difficulty of TAMP lies not in the length of the solution
  but in the **branching factor of the skeleton space**, which is why research targets **shrinking
  the skeleton space** rather than faster motion planning.

## Derivation

### R1 — two layers of decidability

**(a) With the skeleton fixed, it is decidable.** Fixing $\pi = \langle a_1,\dots,a_K\rangle$ gives
parameters $\theta = (\theta_1,\dots,\theta_K) \in \mathbb{R}^N$ with constraints:

- **Geometric**: each action's preconditions (the grasp lies on the object, the placement lies on the
  support) and non-collision. For polyhedral or quadric objects these are **polynomial
  inequalities**.
- **Motion**: a collision-free path exists between consecutive actions. This is a **first-order
  formula** in $\theta$ (quantifying over the existence of a path) and, by the upper-bound argument
  of `c6-cspace-complexity` R3, a connectivity question about a semialgebraic set.

So $\mathcal{F}(\pi)$ is semialgebraic and $\mathcal{F}(\pi) \ne \emptyset$ is **decidable** by
quantifier elimination, at a cost doubly exponential in the number of variables $N$ (CAD) or singly
exponential (Canny-style). **$N = \sum_k \dim\theta_k$ grows with the skeleton length, so this layer
alone becomes uncomputable for long skeletons.**

**(b) With no bound on the length, only semi-decision.** The outer quantifier of (1) ranges over a
**countably infinite** set (skeletons are finite sequences, but of unboundedly many lengths). The
procedure is natural:

> for $K = 1, 2, 3, \dots$, enumerate every skeleton of length $K$ and decide each by (a).

If a solution exists it is found at some finite $K$, so the procedure **halts on YES instances**. On
NO instances it increases $K$ forever and does not halt. That is semi-decidability.

**A stronger claim needs care.** The sentence "TAMP is undecidable" is **true or false depending on
the model**: if the symbolic states are finite and the parameter space has fixed dimension, the state
space is bounded and the problem can be decidable (detect repetition). Undecidability arises when the
state **accumulates continuous values** — moving an object a little at a time to create infinitely
many distinguishable states. That boundary coincides with the decidability boundary for reachability
in hybrid systems ([Henzinger et al. 1995](https://doi.org/10.1145/225058.225162)), so the
decidability of TAMP depends on **a modelling choice about the domain**. How the survey of must-read
1 handles that distinction is problem P8.

**(c) What "no infeasibility verdict" means in practice.** A TAMP planner cannot say "there is no
solution", so it can only **stop on a time limit**, and that stop means "not found", not "none
exists". Why the difference matters in robot system design: a higher level cannot derive the
judgement "this goal is impossible, switch to another" **from the planner's failure**. The practical
workaround is to model the domain **deliberately finitely** (placements on a grid, a finite set of
grasps) — only layer (a) then remains and it becomes decidable, but **completeness is lost** (a
solution outside the grid is never seen). The reproduction task is exactly that model.

### R2 — the three conditions for probabilistic completeness

**The structure.** A sampling-based TAMP (of the PDDLStream kind) interleaves two components.

- **Streams**: samplers that **emit, one at a time**, parameters satisfying a constraint, e.g.
  `grasp(obj) → g`, `place(obj, surf) → p`, `motion(q1, q2) → traj`. Streams are conditional —
  `motion` can be called only once $q_1, q_2$ exist.
- **A symbolic planner**: it searches for a symbolic plan over the **finite** set of objects the
  streams have produced so far.

At level $\ell$ each stream may emit up to $\ell$ candidates, and if no plan is found, $\ell$ is
increased (iterative deepening).

**(a) Dense streams are needed.** By (A7) let a neighbourhood $B(\theta^\ast, \rho)$ of a solution
$\theta^\ast$ lie in $\mathcal{F}(\pi^\ast)$. If a stream lands in that neighbourhood with positive
probability $p_\rho > 0$, the probability of **never hitting it up to level $\ell$** is
$(1 - p_\rho)^{\ell} \to 0$. Since the parameters must come from $K$ different streams, the union
bound gives

$$
\mathbb{P}[\pi^\ast \text{ is not realized at level } \ell]
  \;\le\; \sum_{k=1}^{K} (1 - p_{\rho,k})^{\ell} \;\le\; K\,(1-p_{\min})^{\ell},
  \tag{4}
$$

**exponentially decreasing in $\ell$** — **the same shape** as the PRM argument of
`c6-sampling-completeness` R2 (one sample per ball, union bound).
*Counterexample (if (a) fails)*: a learned grasp sampler emitting only certain modes makes
$p_\rho = 0$ and (4) vacuous. Mixing with a uniform sampler restores it, but the mixing ratio erases
the gain — **the same problem** as the second open problem of `c6-sampling-completeness`.

**(b) Completeness of the symbolic search is needed.** (4) only says the parameters exist. Actually
**finding the skeleton $\pi^\ast$** that uses them is the symbolic planner's job. If that planner is
incomplete (a node cap on the heursitic search, or a precondition-relaxation heuristic that excludes
a skeleton forever), the plan is not found even when all the parameters are present.
*Counterexample (if (b) fails)*: a depth limit $D < K^\ast$ leaves the failure probability at 1 even
as $\ell \to \infty$.

**(c) Fair interleaving is needed.** Stream calls can be **infinitely many** (a conditional stream
creates new objects which call further streams). The order matters — calling one stream infinitely
means another is never called.
*Counterexample (if (c) fails)*: depth-first calling of only the `place` stream leaves the `grasp`
samples at one, and if that one is outside the neighbourhood the solution needs, the algorithm fails
forever. Iterative deepening (raising $\ell$ on **all** streams together) prevents this.

**Putting the three together** gives (2). Structurally this proof is the same as
`c6-sampling-completeness` R2 (PRM); **what is added is (b) and (c)** — only the fact that "finding
the continuous parameters" and "finding the skeleton that uses them" are separate.

**Where the assumption breaks**: if (A7) fails (an assembly demanding exact contact),
$\mathcal{F}(\pi)$ has measure zero, $p_\rho = 0$ and (4) collapses. The workaround is to sample
**directly on the constraint manifold** (projection, continuation), and then density must be
redefined with respect to that manifold's measure — which meets the third open problem of
`c6-cspace-complexity` ("completeness on a stratified space").

### R3 — the number of contact modes

**Defining a mode.** At contact point $i$, with normal gap $\phi_i \ge 0$, normal force
$\lambda_i \ge 0$, tangential relative velocity $v_{t,i}$ and friction coefficient $\mu$, there are
three exclusive states:

| Mode | Condition |
|---|---|
| separated | $\phi_i > 0$, $\lambda_i = 0$ |
| sticking | $\phi_i = 0$, $v_{t,i} = 0$, $\lVert \lambda_{t,i}\rVert \le \mu\lambda_i$ |
| sliding | $\phi_i = 0$, $v_{t,i} \ne 0$, $\lambda_{t,i} = -\mu\lambda_i\,v_{t,i}/\lVert v_{t,i}\rVert$ |

Each point is independently in one of three states, giving the $3^{n_c}$ of (3). Discretizing the
sliding **direction** in three dimensions ($k$ directions) gives $(2+k)^{n_c}$.

**Why this is the same problem as enumerating skeletons.** Within a mode the dynamics are
**smooth** (the complementarity conditions are fixed and become equalities). So "fixing the mode
sequence" produces a continuous optimization problem — this is the through-contact transcription of
`c4-contact-implicit-hybrid` and the structure of LGP — and the mode sequence plays the **role of the
plan skeleton** of R1. With $3^{n_c K}$ sequences of length $K$, the enumeration of R1(b) becomes a
concrete number: $n_c = 4$ (four fingers) and $K = 5$ give
$3^{20} \approx 3.5\times10^9$.

**Three ways to mitigate it.**
1. **Reduce the modes** — keep only "stable modes" or rule out physically impossible combinations in
   advance ([Toussaint et al. 2018](https://doi.org/10.15607/RSS.2018.XIV.044)).
2. **Do not enumerate** — keep the complementarity constraints and solve a non-convex optimization
   (`c4-contact-implicit-hybrid`), giving up global optimality.
3. **Use the piecewise-analytic structure** — treat each mode as an analytic constraint piece and
   recover asymptotic optimality
   ([Vega-Brown & Roy 2020](https://doi.org/10.1007/978-3-030-43089-4_34)).

**Where the assumption breaks**: the three modes above assume **point contact** and **Coulomb
friction**. With surface contact or deformable bodies the number of contact points is not even
defined and $n_c$ becomes a modelling choice. Then the count (3) is **a property of the model, not of
the physics** — the same task can be modelled with $n_c = 3$ or $n_c = 12$, a difference of $3^9$ in
difficulty. That is what makes benchmark comparison in contact planning so hard.

## Proof sketch

### R4 — plan length linear, search exponential

**Hypotheses** H1: $n$ blocks, $m+1$ table slots (including the target slot 0), the robot holds one
at a time. H2: the actions are `pick(b)` (b clear, hand empty) and `place(b, sup)` (sup a slot or a
clear block). H3: for each (block, support) pair a stream emits pose candidates one at a time, each
passing a deterministic geometric test with probability $3/5$. H4: the symbolic search is
**breadth-first** (complete and optimal) and the level $\ell$ is raised from 1.
**Conclusion** C: the shortest plan length is **exactly $2n$**, while the number of nodes expanded
before a solution is found grows exponentially in $n$.

**Strategy**: pin the length exactly by a **constructive lower and upper bound**, and bound the node
count below by a **power of the branching factor**, fixing the constant by measurement.

1. **Lower bound on the length.** The goal has every block stacked in order on the target slot. Each
   block must travel from its initial slot to its final position, and by H2 the only way to move a
   block is `pick` followed by `place`. All $n$ blocks must move, so $\ge 2n$.
2. **Upper bound on the length.** Picking and stacking bottom-up gives each block exactly one
   `pick`+`place`, achieving the goal in $2n$ actions (the initial layout has no stacks, so no
   rearrangement is needed). By 1 and 2 the shortest length is $2n$. **The measurements are
   $4,6,8,10,12,14$ for $n = 2..7$, exactly $2n$.**
3. **Lower bound on the node count.** Breadth-first search expands **almost all** states reachable
   within depth $2n$. A state is (each block's location, what is held), and a block's location has
   $(m+1) + (n-1)$ options, so the number of states is $\Omega\big((m+n)^{n}\big)$. The node count
   is therefore **exponential**, with a base close to $m + n$.
4. **Fix the constant by measurement.** In the reproduction setting ($m+1 = 4$, $p = 3/5$), the
   cumulative expanded nodes for $n = 2,\dots,7$ are
   $18,\ 106,\ 945,\ 28238,\ 290849,\ 3846267$, and a linear fit of $\log(\text{nodes})$ against $n$
   gives slope $2.5289$ with $r^2 = 0.9932$, i.e. about **$e^{2.5289} = 12.54$ times per added
   block**. This is consistent with the bound of step 3 (the base grows with $n$ as $m+n$, so a
   single-exponential fit yields a slope larger than that).
5. **What the conclusion means.** The solution itself is short (linear) and each action's motion
   planning is easy, yet **the search is exponential**. So the lever in TAMP research is not faster
   motion planning but **shrinking the skeleton space** (heuristics, abstraction, learned guidance,
   symbolic pruning). (Omitted: the extra factor the growth of the level $\ell$ contributes to the
   node count — in the measurements $\ell = 2$ was needed for $n \ge 5$, and its cost is about 10% of
   the cumulative nodes.)

**Removing a hypothesis**: replacing the breadth-first search of H4 by a heuristic search greatly
reduces the constant (the weighted A* of `c6-search-based-planning`) but **does not change the
base** — the exponential growth is a property of the state space, not of the search strategy. Raising
the pass probability of H3 to 1 makes $\ell = 1$ enough and lowers the node count, but it is still
exponential. Changing H1's "one at a time" to two arms shortens the plan and raises the branching
factor, producing a **trade-off**.

## Problem set

Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Show concretely that $\mathcal{F}(\pi)$ is semialgebraic for a fixed
$\pi$: for a single `pick`–`place` pair, write each of the four constraints — (a) the grasp lies on
the object's surface, (b) the placement lies on the support, (c) object–obstacle non-penetration,
(d) a free path exists between the two configurations — as a polynomial inequality or a first-order
formula.
*Solution sketch*: (a), (b) and (c) are linear or quadratic inequalities for polyhedra. For (d), reuse
the argument of the upper bound in `c6-cspace-complexity` R3 — turning the existence of a path into
the connectivity of a roadmap makes it a formula admitting quantifier elimination.

**P2 (proof, ★★, R1)** Write rigorously that "TAMP with no length bound is semi-decidable": show the
enumeration procedure halts on YES, and construct an instance on which it does not halt on NO.
*Strategy*: halting follows from "if a solution exists it has finite length". For the NO instance use
a goal that is geometrically impossible (an object outside the robot's reach), and derive from the
unboundedness of the length that **its impossibility cannot be confirmed by finitely many (a)
decisions**.

**P3 (proof, ★★, R2)** Derive (4). In particular handle the fact that the events "each of $K$ streams
must hit the neighbourhood of the solution" **need not be independent** (conditional streams depend
on earlier samples).
*Strategy*: the union bound does not require independence. For conditional streams, use (A7) to
guarantee that the next stream's success probability is positive **given that the earlier samples lie
in the good neighbourhood**, and bound by the **sum of complements** rather than a product of
conditional probabilities.

**P4 (numerical, ★, R3)** Find the number of modes and the number of mode sequences of length
$K = 4$ in each case: (i) $n_c = 2$ in the plane (two sliding directions), (ii) $n_c = 4$ in three
dimensions with sliding discretized into 8 directions, (iii) $n_c = 6$ with modes simplified to
{separated, in contact}.
*Answer*: (i) planar sliding is left or right, so $\{$separated, sticking, left, right$\} = 4$ modes
per point → $4^2 = 16$ and $16^4 = 65536$ sequences. (ii) $2 + 8 = 10$ modes per point →
$10^4$ and $(10^4)^4 = 10^{16}$. (iii) 2 per point → $2^6 = 64$ and $64^4 = 16777216$.
Tolerance: exact integers. **That the ratio of (ii) to (iii) is
$10^{16}/1.68\times10^7 \approx 6\times10^8$ is the failure mode of R3, "the mode count is a property
of the model".**

**P5 (numerical/implementation, ★★, R4)** Write the TAMP of the reproduction task and measure the
cumulative expanded nodes for $n = 2,\dots,7$, fitting the slope of the $\log$-linear growth. Also
confirm the plan length is $2n$.
*Rubric*: (a) the plan lengths are $4,6,8,10,12,14$; (b) the cumulative nodes match
$18, 106, 945, 28238, 290849, 3846267$ **exactly** (the setting is deterministic); (c) the fitted
slope is $2.53 \pm 0.15$ with $r^2 \ge 0.98$; (d) you report that the level $\ell$ rises to 2 for
$n \ge 5$.

**P6 (counterexample, ★★, R2)** For each of the three conditions of R2, construct a concrete instance
on which, **dropping only that condition**, the algorithm fails forever although a solution exists.
*Property checklist*: (a) a sampler emitting only a finite set with the solution outside it; (b) a
depth limit $D < K^\ast$ on the symbolic search; (c) depth-first calling of a single stream
infinitely. State explicitly in all three that **a solution exists**.

**P7 (proof, ★★★, R4)** Make step 3 of R4 rigorous: give a lower bound, in terms of the number of
states, on the nodes a breadth-first search expands down to depth $2n$, and turn "almost all" into a
precise statement (which states are reachable within depth $2n$?).
*Strategy*: counting the reachable states is the crux. Count the configurations in which blocks are
stacked on one another (ordered partitions) and characterize the subset reachable within depth $2n$.
Giving an upper bound as well narrows the base of the exponential.

**P8 (paper, ★★, R1)** Find the statements about decidability and completeness in must-read 1 (the
survey) and contrast them with (a), (b) and (c) of R1 here. In particular, transcribe exactly the
**model assumptions** at the places where the survey says "undecidable", and decide whether those
assumptions hold for the reproduction task's model (finite slots, finite pose candidates).
*Rubric*: pass if you identify that decidability depends on **a modelling choice about the domain**,
and that the reproduction model is finite and hence decidable at the price of completeness. Writing
only "TAMP is hard" fails.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions.

1. **Garrett, Chitnis, Holladay, Kim, Silver, Kaelbling & Lozano-Pérez, "Integrated task and motion
   planning" (2021, Annual Review)** — role: `survey`. <https://arxiv.org/abs/2010.01083>
   *Why read it*: the reference for the problem definition (1) and the taxonomy of approaches. Being
   a survey, the aim is to memorize the **axes of the taxonomy** — does it fix the skeleton, use
   streams, or dissolve everything into optimization?
   Extra questions: (a) what are the model assumptions behind its decidability and completeness
   statements (P8)? (b) do the benchmarks it presents report the "length versus search" separation of
   R4?
2. **Garrett, Lozano-Pérez & Kaelbling, "PDDLStream" (2020, ICAPS)** — role: `standard`.
   <https://arxiv.org/abs/1802.08705>
   *Why read it*: the three conditions of R2 become an algorithm here. Look in particular at how
   "optimistic" planning and iterative deepening guarantee condition (c).
   Extra questions: (a) are the assumptions of the authors' completeness theorem the same as (A7)
   here? (b) how does the conditional structure of the streams complicate the union bound of (4)
   (P3)? (c) on which instances does the cost of iterative deepening dominate?
3. **Toussaint, "Logic-geometric programming" (2015, IJCAI)** — role: `standard`.
   <https://www.ijcai.org/Proceedings/15/Papers/274.pdf>
   *Why read it*: the source of R3, and the representative of fixing the mode sequence symbolically
   and then solving **one continuous optimization**. It contrasts exactly with the sampling-based
   approach of must-read 2.
   Extra questions: (a) what reduces the enumeration of mode sequences? (b) how is the non-convexity
   of the continuous problem handled, and what is claimed about global optimality? (c) is there a
   completeness claim, and if not, why not?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation or one figure. (4) what is guaranteed theoretically,
and **what is not**? (5) the independent and dependent variables and the baselines, and were the
baselines tuned fairly? (6) does the metric match the claim, and are variance and seeds reported?
(7) what is missing for reproduction? (8) if the result were wrong, which assumption would you doubt
first? (9) computational and memory complexity, and real-time feasibility. (10) what would you change
to go beyond this paper in a year?

## Reproduction task

**Tier R3 (figure reproduction).** Budget: one laptop CPU core, under 30 minutes in total (mostly
$n = 7$), under 2 GB of memory. Standard library plus numpy only. No external data.

**Input data (given by the lesson).** $n$ blocks; the table slots are the target slot 0 and work
slots 1, 2 and 3 (four in all). Initially block $i$ is in slot $i+1$ (for $n \le 3$ each in a
different slot; for $n > 3$ slots repeat but remain symbolically distinct), and the goal is to stack
blocks $0, 1, \dots, n-1$ **bottom to top** on slot 0. The actions are `pick(b)` (b clear, hand
empty) and `place(b, sup)` (sup one of slots 0–3 or another clear block).

**The stream (deterministic).** For each (block $b$, support $sup$) pair there are pose candidates
$0,1,2,\dots$, and whether candidate $j$ passes the geometric test is fixed **deterministically** by
$$\mathrm{feasible}(b, sup, j) \;=\; \big[\ \mathrm{blake2b}(\text{"}b|sup|j\text{"},\ 8\text{ bytes}) \bmod 5 \;<\; 3\ \big]$$
(a pass rate of $3/5$). At level $\ell$ only candidates $0,\dots,\ell-1$ are available, and
`place(b,sup)` is possible if any of them passes.

**The search.** A symbolic state is (each block's location, the block held). Breadth-first search
(complete and shortest), with a visited set for de-duplication. Start at level $\ell = 1$ and, if no
plan is found, raise $\ell$ by one and **search again from scratch**. An expansion is counted when a
node is popped from the queue.

**Acceptance criteria — all four must hold.**

1. **Plan length (checking steps 1 and 2 of R4)** — the shortest plan lengths for
   $n = 2,\dots,7$ are $4, 6, 8, 10, 12, 14$, i.e. **exactly $2n$**.
2. **Node count (deterministic, so an exact match)** — the cumulative expanded nodes up to finding a
   solution match

   | $n$ | 2 | 3 | 4 | 5 | 6 | 7 |
   |---|---|---|---|---|---|---|
   | level $\ell$ needed | 1 | 1 | 1 | 2 | 2 | 2 |
   | cumulative nodes | 18 | 106 | 945 | 28238 | 290849 | 3846267 |

   **exactly**. (The need for $\ell = 2$ at $n \ge 5$ comes from the $3/5$ pass rate: the first
   candidate of some (block, support) pair fails.)
3. **Growth-rate fit (step 4 of R4)** — a linear fit of $\log(\text{cumulative nodes})$ against $n$
   has slope $2.5289 \pm 0.15$ with $r^2 \ge 0.98$ (measured $r^2 = 0.9932$), i.e. about
   $e^{2.5289} = 12.54$ times per block. Write one paragraph in the report on **"length linear,
   search exponential"**.
4. **Mode-count contrast (R3)** — compute and print the three values of P4,
   $16/65536$, $10^4/10^{16}$ and $64/16777216$, and write one paragraph on how the skeleton
   enumeration of the reproduction task ($12.54^n$) and contact-mode enumeration ($3^{n_c K}$) are
   **the same kind of blow-up**.

**Baselines.** (a) Analytic bounds: the plan length $2n$ (steps 1 and 2 of R4) and the state count
$\Omega((m+n)^n)$ (step 3). (b) A variant of itself: replace the breadth-first search by A* with a
"fewest blocks remaining" heuristic and show the node count falls while **the slope barely changes**
(verifying the "removing a hypothesis" paragraph of R4). (c) Raise the pass rate to $5/5$ and confirm
$\ell = 1$ suffices.

**Failure table**

| Symptom | Cause | How to check |
|---|---|---|
| the node count differs from the table | expansions were counted when **pushing** onto the queue, or the held block was omitted from the visited state | first get 18 right at $n = 2$ |
| the plan length exceeds $2n$ | the clear condition was omitted from `place`'s support candidates, so rearrangements creep in | print the plan and check each block moves once |
| every $n$ solves at $\ell = 1$ | the geometric test always passes (an error in the hash condition) | measure the pass rate of $\mathrm{feasible}$ over $10^4$ samples and check it is near $0.6$ |
| $n = 7$ exceeds memory | the whole path was stored in the visited set | store only states and carry the depth |
| the fit has a low $r^2$ | $n = 2$ should be dropped, or per-level rather than cumulative nodes were used | use cumulative nodes and include all six points |
| the goal is never recognized | the goal was not written as "hand empty and every block in place" | construct the goal state directly and check it is in the search's visited set |

## Open problems

- **(open problem) A principled way to shrink the skeleton space** — as R4 shows, the difficulty is
  the branching factor of the skeletons. Learned guidance (symbolic heuristics, feasibility
  prediction) works empirically but has **no guarantee of preserving completeness** (it is the
  classic way condition (b) of R2 breaks). Current approaches: the optimistic planning of
  [PDDLStream](https://arxiv.org/abs/1802.08705), incremental skeleton generation with SMT in
  [Dantam et al. 2016](https://doi.org/10.15607/RSS.2016.XII.002), and repairing the symbolic level
  from failure explanations in
  [Srivastava et al. 2014](https://doi.org/10.1109/ICRA.2014.6906922). What is missing: an
  abstraction that **provably** reduces the branching factor while keeping completeness.
- **(open problem) Completeness on measure-zero constraint manifolds** — on tasks where (A7) fails
  (assembly requiring exact contact, bimanual coordination), $\mathcal{F}(\pi)$ becomes
  lower-dimensional and (4) collapses. Sampling directly on the constraint manifold restores it, but
  "density" must be redefined with respect to that manifold's measure, and there is no theory for
  when the manifold splits into strata. Current approaches: the constrained-planning survey of
  [Kingston, Moll & Kavraki 2018](https://doi.org/10.1146/annurev-control-060117-105226), and
  [Vega-Brown & Roy 2020](https://doi.org/10.1007/978-3-030-43089-4_34). What is missing: a
  definition and proof of probabilistic completeness on a stratified space (the same root as the
  third open problem of `c6-cspace-complexity`).
- **(open problem) Model-independence of the contact-mode count** — the $3^{n_c}$ of (3) varies by up
  to $10^8$ depending on how $n_c$ is counted (P4). With no way to measure a task's difficulty
  **independently of the modelling choice**, benchmark comparison in contact planning does not hold
  up. Current approaches: reducing to stable modes
  ([Toussaint et al. 2018](https://doi.org/10.15607/RSS.2018.XIV.044)), and complementarity
  optimization that does not enumerate modes (`c4-contact-implicit-hybrid`). What is missing: a
  model-invariant measure of contact complexity.

## Concept check

Run `rc quiz c6-tamp`. Concept checking only; the real work is the problem set and the reproduction
task.

The six items cover: why fixing the skeleton makes feasibility decidable; what an algorithm cannot do
when the length is unbounded; the three conditions for completeness of a sampling-based TAMP; the
number of contact modes; which of plan length and search grows exponentially; and the name for a
sequence of actions with undetermined parameters.

## How to study this stage

1. **Write the two-layer structure as one formula (20 min)** — write (1) and mark that the outer
   quantifier is discrete and infinite while the inner one is continuous. Then add "outer = skeleton
   search, inner = constraint satisfaction". From that single line come R1 (decidability), R2
   (completeness) and R4 (where the difficulty sits).
2. **Separate the two layers of decidability (50 min)** — write (a) and (b) of R1 as a paragraph
   each. (a) reuses the semialgebraic argument of the earlier lesson, (b) is a property of
   enumeration. Solving P2 alongside fixes in your hands why "no infeasibility verdict" is **a
   property of the problem**.
3. **Memorize the completeness conditions through counterexamples (50 min)** — remember the three
   conditions of R2 by the **counterexample that breaks each** (P6). Counterexamples stick better
   than conditions and let you diagnose which condition an implementation is violating.
4. **Count the modes yourself (30 min)** — do P4. Computing that the same task can be modelled with
   $n_c = 4$ or $n_c = 6$ at a difficulty difference of $10^8$ changes how you read the experiments in
   contact-planning papers.
5. **Implement it and plot the two growth rates apart (95 min)** — the reproduction task. The aim is
   to **plot the plan length and the node count on the same figure** (one linear, the other linear on
   a log axis). That single figure is the conclusion of this lesson and the close of the module. Also
   run the heuristic A* variant and confirm the slope barely moves.
6. **Three papers (130 min)** — skim the survey (must-read 1) **first**, then read PDDLStream
   (sampling) and LGP (optimization) against each other. They are **opposite design choices** on the
   same problem: one searches skeletons while adding samples, the other fixes the skeleton (mode
   sequence) and solves one continuous problem. Write that contrast as the conclusion of your notes.
7. **Problem set (160 min)** — P4 and P5 first, then P1 and P3, then P2, P6, P7 and P8 with whatever
   time remains. P7 (bounding the node count by counting states) is the hardest.

**Passing bar**: you can write the two-layer structure of (1) and derive R1, R2 and R4 from it, state
the three conditions of R2 with counterexamples, have code satisfying the four criteria of the
reproduction task together with the "length linear, search exponential" figure, and compute how the
mode count changes with the modelling choice. You have notes on all three papers.

**Closing the module.** The seven lessons of C6 are ordered by breaking the three assumptions of
`c6-cspace-complexity` one at a time — (A2), no differential constraints, fell in
`c6-kinodynamic-planning`, and "a single open free space" fell in this lesson. Breaking the remaining
(A3), full information, gives planning under uncertainty (POMDPs), which is outside this module.
Notice that the open problems of every lesson converge on **one hole**: the guarantees are given only
in the limit, and **there is no theory of what can be guaranteed on a finite budget.**
