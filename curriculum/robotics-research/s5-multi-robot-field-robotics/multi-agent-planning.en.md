---
id: s5-multi-agent-planning
lang: en
title: Multi-robot path planning
summary: >-
  Establish that optimal multi-agent path finding (MAPF) is NP-hard, and prove that conflict-based
  search (CBS) is complete and optimal by showing that the constraint tree covers the solution space
  without losing a single solution. Prove that prioritized planning is incomplete with a
  counterexample on which **every** priority order fails, and then measure that under a fixed
  computation budget the optimal algorithm has a *lower* success rate than the incomplete one.
objectives:
  - Define MAPF and distinguish vertex from edge conflicts and the two objectives (sum-of-costs, makespan).
  - Explain the structure of the reduction that makes optimal MAPF NP-hard.
  - Prove the completeness and optimality of CBS from the covering property of the constraint tree and lower-bound-first search.
  - Prove that prioritized planning is incomplete with a counterexample on which every order fails.
  - Measure that the cost of CBS is exponential in the number of conflicts via constraint-tree node counts.
  - Separate theoretical completeness from success rate under a fixed budget, numerically.
tags: [multi-robot, mapf, cbs, prioritized-planning, np-hardness, completeness, research]
---

# Multi-robot path planning

## Setup and notation

We reuse A*, consistent heuristics and the optimality argument from `c6-search-based-planning`, and
the configuration-space and complexity view of `c6-cspace-complexity`. **MAPF is a search in the
joint configuration space of $n$ robots**, and the fact that this joint space blows up as
$\lvert V\rvert^n$ is the source of every difficulty in this lesson.

| Symbol | Meaning |
|---|---|
| $G = (V, E)$ | Grid graph. This lesson uses a 4-connected grid plus a wait-in-place action |
| $n$ | Number of robots (agents). Starts $s_i$ and goals $g_i$ are all distinct |
| $\pi_i$ | The **space-time path** of robot $i$. $\pi_i(t) \in V$, $\pi_i(0) = s_i$, and it stays at the goal once reached |
| Vertex conflict | $\pi_i(t) = \pi_j(t)$ — the same cell at the same time |
| Edge conflict (swap) | $\pi_i(t) = \pi_j(t{+}1)$ and $\pi_j(t) = \pi_i(t{+}1)$ — an exchange of places |
| sum-of-costs | $\sum_i \lvert\pi_i\rvert$ (the sum of the path lengths). The objective of this lesson |
| makespan | $\max_i \lvert\pi_i\rvert$. A different objective, with **a different optimal solution** |
| CT | The **constraint tree** of CBS. A node is (constraint set, path set, cost) |
| $\mathcal{C}_i$ | The constraint set attached to robot $i$: vertex constraints $(t, v)$ and edge constraints $(t, u, v)$ |

**Two algorithms.** This lesson compares exactly two.

- **CBS (conflict-based search)** — plan each robot **separately** and optimally; when a conflict
  appears, add one constraint forbidding that conflict and branch into two children. The high level
  is a best-first search on a cost lower bound and the low level is a single-robot A* that respects
  the constraints.
- **Prioritized planning** — fix one order and plan the robots in turn, treating the
  **already-planned robots as moving obstacles**. It is fast and **incomplete**.

## Self-diagnosis before starting

This is the third lesson of the module, so there is no self-diagnosis section — the earlier lessons
of the same module (`s5-graph-consensus`, `s5-distributed-optimization`) are the prerequisites. We
do assume the optimality argument for A* (`c6-search-based-planning`) and the definition of
NP-hardness (`c6-cspace-complexity`).

## Key results

The bracketed grade is the derivation depth (D0 citation / D1 skeleton / D2 full derivation /
D3 proof — `research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (optimal MAPF is NP-hard) [D1]** — MAPF **feasibility** alone is solvable in polynomial time
  on a grid (a constructive token-swapping algorithm). But **minimizing sum-of-costs or makespan is
  NP-hard** (`yu2013-mapf-complexity`). The reduction comes from 3-SAT or from multi-commodity flow,
  and the source of hardness is the combinatorial choice of **which robot gives way**. Finding a
  polynomial-time optimal algorithm is therefore not the goal; designing an **exponential but
  practical** search is.
- **R2 (CBS is complete and optimal) [D3]** — if CBS returns a solution it is sum-of-costs optimal,
  and if a solution exists CBS finds it. The proof has three pillars:
  $$
  \text{(i) lower bound: } \mathrm{cost}(N) \le \mathrm{cost}(\text{any solution respecting $N$'s constraints}), \tag{1}
  $$
  $$
  \text{(ii) the branching loses nothing: for a conflict } (i,j,t,v) \text{, any solution satisfies } (t,v)\!\notin\!\pi_i \text{ or } (t,v)\!\notin\!\pi_j, \tag{2}
  $$
  $$
  \text{(iii) lower-bound-first search: the first conflict-free node popped is optimal.} \tag{3}
  $$
- **R3 (prioritized planning is incomplete — for every order) [D2]** — there exist solvable
  instances on which **every** priority order fails. The counterexample in the reproduction task: a
  width-1 corridor of length 5 with a single alcove at its centre, and two robots that exchange the
  two ends. CBS finds the optimal solution of cost 11 in 11 CT nodes, while prioritized planning
  fails for **both** orders (with 2 robots there are only two orders, so this *is* a proof for
  "every order"). The sum of the individually optimal paths is 8, so the coordination cost is 3.
  Recovering completeness requires a structural condition on the environment (well-formed
  infrastructure, `cap2015-prioritized-planning`).
- **R4 (the cost of CBS is exponential in the number of conflicts) [D2]** — the branching factor of
  the CT is 2, but its depth is proportional to the number of conflicts, so the node count grows
  exponentially. Measured in the reproduction task (random grids, 15% obstacles): the mean CT node
  count moves $1.9 \to 8.1 \to 4.2 \to 79.8 \to 13.2$ with agent density and the time
  $0.7 \to 77.6\,\mathrm{ms}$. **Density, not grid size, sets the cost** — 8 robots on $12\times12$
  are 6 times more expensive than 8 robots on $16\times16$.
- **R5 (theoretical completeness $\ne$ success rate under a fixed budget) [D2]** — CBS is complete
  and prioritized planning is not, yet **imposing a node budget reverses the ordering.** Measured in
  the reproduction task (30-35% obstacles): the success rate of CBS falls $0.957 \to 0.846$ with
  density while prioritized planning scores $1.000$ on all 68 instances. And every CBS failure is a
  **node-cap hit** (2 cap hits, 0 tree exhaustions); raising the cap $3000 \to 30000$ solves 2/2 —
  **CBS is not wrong, it is slow**. The price is cost: prioritized planning lands
  $15\!-\!19\%$ above optimal.

## Derivation

### R2 — why CBS is optimal

**Setup.** A CT node $N$ consists of (a) a constraint set $\{\mathcal{C}_i\}$, (b) for each robot a
path $\pi_i$ that is a **single-robot optimal path respecting $\mathcal{C}_i$**, and (c) a cost
$\mathrm{cost}(N) = \sum_i\lvert\pi_i\rvert$. The root has no constraints. The high level is a
best-first search on $\mathrm{cost}$.

**(i) Lower bound.** Consider **any** conflict-free solution $\{\sigma_i\}$ respecting $N$'s
constraints. Each $\sigma_i$ is one path respecting $\mathcal{C}_i$, so the optimality of the low-level
A* under those constraints gives $\lvert\pi_i\rvert \le \lvert\sigma_i\rvert$ **for every $i$**.
Summing,

$$
\mathrm{cost}(N) = \sum_i \lvert\pi_i\rvert \;\le\; \sum_i\lvert\sigma_i\rvert = \mathrm{cost}(\{\sigma_i\}), \tag{4}
$$

that is, $\mathrm{cost}(N)$ is a **lower bound** on the cost of every solution in the subtree of $N$.
The low-level optimality is essential here — if the low level is not optimal, (4) breaks and the
optimality of CBS collapses with it (problem P1).

**(ii) The branching loses nothing.** Suppose $N$'s paths have a conflict $(i, j, t, v)$ (a vertex
conflict). Any conflict-free solution $\{\sigma_i\}$ in the subtree of $N$ cannot have
$\sigma_i(t) = \sigma_j(t) = v$, so **at least one** of the two is not at $v$ at time $t$. Hence

$$
\{\sigma\} \ \text{satisfies} \ (t,v)\notin\sigma_i \ \text{or} \ (t,v)\notin\sigma_j. \tag{5}
$$

CBS creates two children, putting $(t,v)$ into $\mathcal{C}_i$ in one and into $\mathcal{C}_j$ in the
other. What (5) says is that **the two children's subtrees cover all solutions of $N$** — the
branching loses no solution (the two may overlap; the CT is a **cover**, not a partition). Edge
conflicts follow the same argument, differing only in that the constraint must be oriented per robot.

**(iii) Optimality.** Let $N^\ast$ be the first conflict-free node popped by the best-first search.
Every node $N'$ remaining in the queue has $\mathrm{cost}(N') \ge \mathrm{cost}(N^\ast)$ (the
best-first property). Take any solution $\{\sigma\}$: by (ii) we can descend from the root always
choosing the child that still covers $\{\sigma\}$, and some node $N'$ on that path is in the queue
(or has been expanded, so a descendant of it is). From (4),
$\mathrm{cost}(\{\sigma\}) \ge \mathrm{cost}(N') \ge \mathrm{cost}(N^\ast)$, and $N^\ast$ is itself a
conflict-free solution so $\mathrm{cost}(N^\ast)$ is attainable. Therefore $N^\ast$ is **optimal**.

**Completeness.** The CT is not finite (constraints can be piled up indefinitely), but costs increase
monotonically and only finitely many nodes share a cost, so if a solution exists the search reaches
that cost level in finite time. If no solution exists, the low-level A* fails, no children are made,
and the queue dries up.

**Where the assumptions break**: (4) requires the low level to be **optimal under the constraints**.
Approximating the low level for speed (depth limits, weighted A*) makes CBS **lose optimality** —
variants exist that give $w$-optimality instead. And (ii) relies on picking **one** conflict, and
*which* conflict is picked changes the CT size dramatically (conflict-selection heuristics are a
major strand of CBS research). Finally, this argument is about **sum-of-costs**. Switching to
makespan replaces the sum in (4) by a maximum, so the low-level optimality no longer hands you the
lower bound in the same way (problem P3).

### R3 — an instance where prioritized planning fails for every order

Prioritized planning fixes an order $\sigma$ and, when planning the $k$-th robot, treats the paths of
the preceding $k-1$ as **space-time obstacles** (including their stay at the goal). Each step is a
single-robot A*, so it is fast.

**The counterexample.** On a $2\times5$ grid, lay out a width-1 corridor with one alcove (`#` is an
obstacle):

```
. . . . .
# # . # #
```

Robot A: $s_A = (0,0)$, $g_A = (0,4)$. Robot B: $s_B = (0,4)$, $g_B = (0,0)$ — they exchange the ends.

**It is solvable.** While A waits once at $(0,1)$, B goes $(0,3)\to(0,2)\to(1,2)$ into the alcove;
after A passes, B comes out and goes $(0,1)\to(0,0)$. The CBS solution in the reproduction task is
exactly this, of cost 11 (the sum of the individual optima is $4+4 = 8$, so the coordination cost
is 3).

**Order $[A, B]$ fails.** A knows nothing of B, so it takes the shortest path
$(0,0)\to(0,1)\to(0,2)\to(0,3)\to(0,4)$, arrives at $(0,4)$ at $t=4$ and **stays there**. But B is at
$(0,4)$ at $t=0$, so it must leave by $t \le 3$. To reach $(0,0)$ B must pass $(0,2)$, which is two
steps from $(0,4)$, so the earliest it can be there is $t=2$ — and A is at $(0,2)$ at exactly that
$t=2$. Waiting at $(0,3)$ does not help, because A arrives at $(0,3)$ at $t=3$. Dodging into the
alcove does not help either, since the alcove's entrance *is* $(0,2)$, the same conflict. So no plan
exists for B.

**Order $[B, A]$ fails too.** The grid and the problem are left-right symmetric, so the same argument
applies verbatim.

**With 2 robots there are only two orders and both fail — that is, every order fails.** This proves
prioritized planning **incomplete** (one instance suffices). The reproduction task runs both and
confirms it.

**Why it fails.** The crux is that **the robot planned first stays at its goal forever.** If that goal
blocks the only passage of a later robot, the later robot has no solution. The optimal solution
requires "the robot that went first steps aside for a moment", and the structure of prioritized
planning cannot express that.

**Where the assumptions break**: this counterexample depends on the environment having a **width-1
corridor**. `cap2015-prioritized-planning` shows that imposing a "well-formed infrastructure"
condition on the environment (every start and goal sits where it does not block other robots'
passage) makes prioritized planning **complete**. Incompleteness is therefore not a property of the
algorithm alone but of the **pair (algorithm, environment)**. This is exactly why warehouse
automation guarantees aisle widths by design.

### R4 — how fast the CT grows

The branching factor of the CT is **always 2** (two children per conflict). So why exponential — the
**depth** is the problem. Forbidding one conflict makes the low-level A* produce a different path, and
that path creates new conflicts. If $d$ conflicts must be resolved to reach a solution, the CT has
$O(2^d)$ nodes in the worst case. Since $d$ grows with the robot count and the density,

$$
\text{CT nodes} \sim 2^{\Theta(\text{\#conflicts})}, \qquad
\text{\#conflicts} \sim \text{robot density} \times \text{path length}. \tag{6}
$$

Measured in the reproduction task (15% obstacles, sum-of-costs):

| Grid | Robots | Mean CT nodes | Mean time (ms) | Mean cost |
|---|---|---|---|---|
| $8\times8$ | 3 | $1.9$ | $0.7$ | $16.90$ |
| $8\times8$ | 5 | $8.1$ | $7.4$ | $28.74$ |
| $12\times12$ | 5 | $4.2$ | $4.1$ | $40.38$ |
| $12\times12$ | 8 | $79.8$ | $77.6$ | $66.39$ |
| $16\times16$ | 8 | $13.2$ | $15.3$ | $92.24$ |

**A larger grid is actually cheaper.** 8 robots on $12\times12$ (density $8/144$) take 6 times the CT
nodes and 5 times the time of 8 robots on $16\times16$ (density $8/256$). What sets the cost is
**density, not grid size**: density sets the number of conflicts and the number of conflicts sets the
node count via (6). This is why MAPF benchmarks are always reported on a "map $\times$ agent count"
grid.

**Where the assumptions break**: (6) is a worst-case upper bound; in practice conflicts are not
independent and the count can be far smaller (the non-monotonicity in the table above is the
evidence). Conversely, adversarially constructed instances attain the bound. And (6) ignores
**conflict selection** — which conflict is branched first changes $d$, which is why most of the work
on improving CBS concentrates on conflict selection and heuristics (ICBS, CBSH).

### R5 — a budget reverses the ordering

R2 says CBS is complete; R3 says prioritized planning is not. But practice **does not grant
unlimited time.** Under a node cap $B$, CBS must report "no solution exists" and "could not find one
within the budget" as different outcomes, and the latter grows with density.

Measured in the reproduction task (30-35% obstacles, node cap $B = 3000$; the denominator is the
number of individually reachable instances):

| Grid | Robots | Obstacles | Instances | CBS success | Cap hit | Tree exhausted | Prioritized success | Cost gap |
|---|---|---|---|---|---|---|---|---|
| $10\times10$ | 4 | 0.30 | 23 | $0.957$ | 1 | 0 | $1.000$ | $0.70\%$ |
| $10\times10$ | 4 | 0.35 | 13 | $1.000$ | 0 | 0 | $1.000$ | $5.06\%$ |
| $10\times10$ | 6 | 0.30 | 19 | $0.895$ | 2 | 0 | $1.000$ | $19.43\%$ |
| $14\times14$ | 6 | 0.35 | 13 | $0.846$ | 2 | 0 | $1.000$ | $15.45\%$ |

Read three things off this.

1. **Every CBS failure is a budget failure.** The "tree exhausted" column is all zeros — CBS never
   concluded "no solution exists"; it always hit $B$. Raising the cap $3000 \to 30000$ solves **2/2**
   of the hard instances. **CBS is not wrong, it is slow.**
2. **Yet prioritized planning solves more under a fixed budget.** It never failed on any of the 68
   dense instances ($1.000$). Theoretical incompleteness needs a **structural bottleneck**, and random
   grids barely produce one even at 35% obstacles. The counterexample of R3 was hand-designed.
3. **The price is cost.** The prioritized solutions are $0.7\!-\!19.4\%$ above optimal, and the gap
   widens with density ($0.70\%$ at 4 robots on $10\times10$, $19.43\%$ at 6).

**So report three axes separately**: (a) theoretical completeness and optimality (a property of the
algorithm), (b) success rate under a fixed budget (a property of the budget and the instance
distribution), (c) solution cost (quality). When a paper writes "complete and optimal", check that it
is not claiming (b). **[D2]**

## Proof sketch

### R2' — the optimality of CBS

**Hypotheses** H1: the low level returns an **optimal** path for each robot under the given
constraints. H2: the high level is a best-first search on $\mathrm{cost}$. H3: the branching on one
conflict satisfies (5) (for vertex and edge conflicts alike).
**Conclusion** C: the first conflict-free node CBS returns is a sum-of-costs optimal solution.

**Strategy**: the **same structure** as the optimality argument for A* — an evaluation function that
is a lower bound, a best-first search, and tightness of the bound at the goal node. The difference is
that a "node" here is not a state but a **subset of the solution space**.

1. **Lower bound.** H1 gives (4): $\mathrm{cost}(N)$ is at most the cost of every solution respecting
   $N$'s constraints. This plays the role of $f = g + h$ being a lower bound in A*.
2. **Cover.** H3 gives (5), so for any solution $\{\sigma\}$ we can start at the root and at each
   branch pick a child that still contains $\{\sigma\}$. Hence **no solution is ever lost in the CT.**
3. **Queue invariant.** Throughout the run, for any solution $\{\sigma\}$ some node on the path of
   step 2 is in the queue (induction: the root is in the queue initially, and expanding a node inserts
   its children, which lets step 2 pick at least one).
4. **Tightness at the goal.** At a conflict-free node $N^\ast$ the paths $\{\pi_i\}$ are themselves a
   solution, so $\mathrm{cost}(N^\ast)$ is **attainable**. By H2, at the moment it is popped every node
   in the queue has $\mathrm{cost} \ge \mathrm{cost}(N^\ast)$.
5. **Conclusion.** For any solution $\{\sigma\}$ take the node $N'$ of step 3; then
   $\mathrm{cost}(\{\sigma\}) \overset{(1)}{\ge} \mathrm{cost}(N') \overset{(4)}{\ge} \mathrm{cost}(N^\ast)$.
   So $N^\ast$ is optimal. C. $\square$

**Delete a hypothesis**: weakening H1 (a $w$-optimal low level) loosens the bound of step 1 by a
factor $w$ and weakens the conclusion to $w$-optimality — that is the precise statement of weighted
CBS. Replacing H2 by depth-first search destroys step 4, so the first solution found is not optimal
(in exchange for less memory). Replacing H3 by "constrain both robots" makes (5) false and therefore
**loses solutions** — that the branching must be a cover is the heart of the CBS design, and a common
implementation bug lives exactly here (problem P5).

### R1' — the NP-hardness of optimal MAPF (skeleton)

**Hypotheses** H1: the input is a graph $G$ and a set of agents, and we minimize sum-of-costs (or
makespan).
**Conclusion** C: the decision version ("is there a solution of cost $\le k$?") is NP-complete.

**Strategy**: membership in NP is immediate because a solution is verifiable in polynomial time.
Hardness is by reduction from 3-SAT or multi-commodity flow.

1. **Membership in NP.** Given a set of paths, conflict checking and cost computation are polynomial.
   One technical condition: the path lengths must be polynomially bounded, which needs **$k$ in unary**
   or a length bound.
2. **The idea of the reduction.** Give each variable a "two-branch passage" so that which branch a
   robot takes encodes true or false. Put a bottleneck at each clause so that the branches **cannot be
   traversed simultaneously**; then the existence of a solution of cost $\le k$ corresponds to
   satisfiability.
3. **The source of hardness.** What raises the cost in step 2 is the choice of "who gives way", and
   that choice is **coupled** across clauses. Asking only for feasibility ignores the cost of giving
   way, so feasibility can be solved constructively — hence the gap: **feasibility polynomial,
   optimality NP-hard**.
4. **Consequence.** Searching for a polynomial-time optimal algorithm is (under P $\ne$ NP) futile.
   Research goes instead to (a) exponential but well-constant complete-and-optimal search (the CBS
   family), (b) bounded-suboptimal algorithms, (c) polynomial algorithms under structural assumptions
   (the well-formed condition of `cap2015-prioritized-planning`). **[D1]**

(Omitted: the concrete gadget construction of the reduction and the handling of the length bound.
`yu2013-mapf-complexity` §3-4.)

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★, R2)** Write (4) and (5) with no line missing, then (a) show with a concrete small
instance how (4) breaks if the low-level A* is not optimal, (b) show by counterexample that (5)
becomes false if the branching constrains **both** robots, and (c) state (5) precisely for edge
conflicts.
*Strategy + key inequality*: (b) is the crux — forbidding both robots leaves the solutions in which
"only one of the two steps aside" in neither child, so the cover breaks. A two-cell example in a
width-1 corridor suffices. (c) must use the fact that edge constraints are oriented ($(t,u,v)$ and
$(t,v,u)$ are different). The derivation is withheld.

**P2 (proof, ★★★, R3)** For the counterexample of R3, (a) write the failure of order $[A,B]$ as a
complete time-by-time argument (enumerating every action available to B), (b) argue that $[B,A]$ fails
by symmetry, (c) decide which order succeeds if the alcove is widened to two cells at $(1,1)$ and
$(1,3)$, and (d) from that, conjecture what the well-formed condition of
`cap2015-prioritized-planning` requires.
*Strategy*: for (a) it suffices to show that B's only first move is $(0,3)$ and that its entry time
into $(0,2)$ is then pinned at $t\ge2$. For (c), confirm numerically and then explain **why** it
succeeds (the place to step aside is off the corridor) — that is the graded part. The derivation is
withheld.

**P3 (derivation, ★★, R2)** State exactly where the lower-bound argument (4) breaks when the objective
changes from sum-of-costs to makespan, then (a) propose the correct node cost for makespan CBS,
(b) show that it is a lower bound, and (c) construct a concrete instance whose optimal solutions differ
under the two objectives.
*Solution sketch*: (4) uses monotonicity of $\sum$ — under $\max$ the inequality
$\max_i\lvert\pi_i\rvert \le \max_i\lvert\sigma_i\rvert$ **still holds**, so the lower-bound argument
survives. The real problem is that the low-level A* gives "shortest under the constraints" whereas
makespan cares about **not being longer than the other robots**, so the low-level objective is
misaligned with the global one. Two robots suffice for (c) (a solution where one detours far to let the
other go fast).

**P4 (numerical, ★, R3·R4·R5)** From the reproduction task, obtain (a) the CBS cost and CT node count
of the counterexample and the outcome of both orders, (b) the CT node / time / cost table for random
grids (15% obstacles), (c) the success rate / cap hit / cost gap table for dense grids, and (d) the
change when the node cap is raised.
*Answers*: (a) CBS cost 11, CT nodes 11, prioritized fails for both orders, sum of individual optima 8.
(b) the table of R4. (c) the table of R5. (d) the 2 instances unsolved at cap $3000$ are solved 2/2 at
cap $30000$. Tolerances: integers exactly, means within 5% relative (random averages).
Cross-check: in (b), verify that the CBS cost is **always at least** the sum of the individually optimal
path lengths — if it is smaller, the conflict check or the cost computation is wrong.

**P5 (implementation, ★★★, R2·R3)** Implement CBS and prioritized planning.
*Rubric*: (a) CBS finds cost 11 on the counterexample and prioritized fails for both orders;
(b) **both** vertex and edge (swap) conflicts are detected, and edge constraints are oriented correctly
per robot; (c) it is verifiable from the code that the branching constrains **one robot only**
(evidence that the bug of P1(b) was avoided); (d) staying at the goal after arrival is reflected in
**both** the conflict check and the obstacle model of prioritized planning; (e) CBS failures are
reported separately as "tree exhausted" and "cap hit".

**P6 (counterexample, ★★, R5)** (a) Show with the reproduction-task tables that "a complete and optimal
algorithm solves more in practice" is false; (b) argue with the cap experiment that the reversal is
**a property of the budget and the instance distribution, not of the algorithm**; (c) conversely, design
an instance distribution on which the incompleteness of prioritized planning does show up, and
demonstrate it numerically.
*Property checklist*: (b) must cite **both** "0 tree exhaustions" and "raising the cap solves 2/2" —
citing only one fails to answer the objection "maybe CBS is actually incomplete". For (c), randomizing
the counterexample of R3 (corridor + alcove placed at random) works. "Just raise the density" is
insufficient — the reproduction task shows that even 35% does not do it.

**P7 (paper, ★★, R2·R3)** Read `sharon2015-cbs` §3-5 and `cap2015-prioritized-planning` §III-IV, then
(a) write one sentence each on **what each paper guarantees**, (b) match Sharon et al.'s optimality
proof against the steps of R2' above by equation and theorem number, and (c) explain how Čáp et al.'s
well-formed condition excludes the counterexample of R3.
*Rubric*: for (a), separating "sum-of-costs complete and optimal" (Sharon) from "prioritized planning
is complete in well-formed environments" (Čáp) passes. (c) is the crux — pointing out that the condition
constrains the **positions of starts and goals** and showing that the corridor's two ends violate it is
excellent.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes, attacking questions 4, 5, 6 and 7 in the third.

1. **Sharon, Stern, Felner & Sturtevant, "Conflict-based search for optimal multi-agent
   pathfinding" (2015, Artificial Intelligence)** — role: `seminal`.
   <https://doi.org/10.1016/j.artint.2014.11.006> (§3-5)
   Extra questions: (a) How does the authors' optimality proof correspond to steps 1-5 of R2' above?
   (b) Does the criterion they report for "when CBS beats A*-style methods" agree with the conflict
   count in (6)? (c) What do they say, and what do they leave open, about conflict-selection strategies?
2. **Yu & Rus (Yu & LaValle), "Structure and intractability of optimal multi-robot path planning on
   graphs" (2013, AAAI)** — role: `seminal`.
   <https://doi.org/10.1609/aaai.v27i1.8541> (§3-4)
   Extra questions: (a) With what structure do the authors explain the complexity gap between
   feasibility and optimality? (b) Does the reduction apply to both sum-of-costs and makespan, or only
   one? (c) Which special cases do they show to be polynomial-time solvable?
3. **Čáp, Novák, Kleiner & Selecký, "Prioritized planning algorithms for trajectory coordination of
   multiple mobile robots" (2015, IEEE T-ASE)** — role: `standard`.
   <https://doi.org/10.1109/TASE.2015.2445780> (§III-IV)
   Extra questions: (a) State the definition of well-formed infrastructure in one sentence and explain
   why the counterexample of R3 violates it. (b) Does their completeness guarantee depend on the
   **choice of order**? (c) Do real warehouse and factory layouts satisfy the condition?

**The ten fixed questions**: (1) which problem under which assumptions (2) what exactly could prior work
not do (3) the core idea in one equation (4) what is guaranteed theoretically and **what is not**
(5) the independent and dependent variables, the baselines, and whether they were tuned fairly (6) do the
metrics match the claim, are variances and seeds reported (7) what information needed for reproduction is
missing (8) if it were wrong, which assumption would you doubt first (9) computational and memory
complexity and real-time behaviour (10) what would you change to surpass it in a year.

## Reproduction task

**Tier R2 (algorithm re-implementation).** Compute budget: 1 laptop CPU core, under 3 minutes total,
under 300MB. Use only numpy and the standard library (`heapq`).

The **input data** is produced by the generator below (fixed seed, deterministic). No external dataset
is needed. **What the learner writes is the four functions**: space-time A*, conflict detection, CBS,
and prioritized planning.

```python
"""s5-multi-agent-planning reproduction task: grid generator and counterexample."""

import numpy as np

SEED = 20261112
MOVES = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))  # wait + 4-connected


def make_grid(size, obstacle_frac, n_agents, rng):
    """A random obstacle grid with starts and goals on distinct free cells."""
    while True:
        occ = rng.random((size, size)) < obstacle_frac
        free = [(r, c) for r in range(size) for c in range(size) if not occ[r, c]]
        if len(free) < 2 * n_agents:
            continue
        idx = rng.choice(len(free), 2 * n_agents, replace=False)
        return occ, [free[i] for i in idx[:n_agents]], [free[i] for i in idx[n_agents:]]


def corridor_counterexample():
    """2x5 corridor with a central alcove. Solvable, yet prioritized planning fails for every order."""
    occ = np.ones((2, 5), dtype=bool)
    occ[0, :] = False
    occ[1, 2] = False
    return occ, [(0, 0), (0, 4)], [(0, 4), (0, 0)]
```

**Conventions (match these exactly).** (a) Paths are space-time paths and a robot **stays at its goal
after arriving** (reflected in **both** the conflict check and the obstacle model of prioritized
planning). (b) Conflicts are both vertex $\pi_i(t)=\pi_j(t)$ and edge/swap
$\pi_i(t)=\pi_j(t{+}1) \wedge \pi_j(t)=\pi_i(t{+}1)$. (c) The cost is sum-of-costs
$=\sum_i(\lvert\pi_i\rvert-1)$. (d) A CBS branch constrains **one robot only** (edge constraints
oriented per robot). (e) Goal-constraint handling: a vertex constraint on the goal cell during the stay
is still a violation, so the low-level A* must check that no constraint on that cell remains after the
arrival time.

**Part A — the counterexample.** Run CBS and prioritized planning (both orders) on
`corridor_counterexample()`. Also report the sum of the individually optimal path lengths.

**Part B — random grids (open terrain).** Create `np.random.default_rng(SEED)` **afresh for each
setting**, take $(\text{size}, n, \text{runs})$ as $(8,3,40), (8,5,40), (12,5,40), (12,8,30),
(16,8,25)$ and generate with 15% obstacles. For each instance, first check that every robot can reach
its goal individually (skip if not), then run CBS (node cap 3000) and prioritized planning, and report
the mean CT nodes, time and cost, plus the cost gap.

**Part C — dense grids (success rate).** The same way, run $(10,4,0.30,60), (10,4,0.35,60),
(10,6,0.30,50), (14,6,0.35,40)$. **The denominator of the success rate is the number of instances not
skipped.** Count CBS failures separately as "cap hit" and "tree exhausted".

**Part D — the budget effect.** On $(10, 6, 0.30)$, collect only the instances unsolved at cap 3000 and
rerun them at cap 30000.

**Acceptance criteria — all four conditions must hold.**

1. **Part A** — CBS finds a solution of sum-of-costs **11** in **11** CT nodes (tolerance: cost exactly,
   node count $\pm2$), and prioritized planning fails for **both** order $[0,1]$ and order $[1,0]$. The
   sum of the individually optimal path lengths is **8** (coordination cost 3). Check that one robot
   passes through the $(1,2)$ alcove in the CBS solution.
2. **Part B** — reproduce the table below (means within 5% relative; times vary by machine, so check
   only the **ratios**).

   | Grid | Robots | CT nodes | Cost | Gap |
   |---|---|---|---|---|
   | $8\times8$ | 3 | $1.9$ | $16.90$ | $5.75\%$ |
   | $8\times8$ | 5 | $8.1$ | $28.74$ | $9.77\%$ |
   | $12\times12$ | 5 | $4.2$ | $40.38$ | $4.22\%$ |
   | $12\times12$ | 8 | $79.8$ | $66.39$ | $3.56\%$ |
   | $16\times16$ | 8 | $13.2$ | $92.24$ | $3.67\%$ |

   State explicitly that **8 robots on $12\times12$ take 6 times the CT nodes of 8 robots on
   $16\times16$**, and report that density is what sets the cost.
3. **Part C** — reproduce the table below (success rates $\pm0.05$, gaps within 10% relative).

   | Grid | Robots | Obstacles | Instances | CBS success | Cap | Exhausted | Prioritized success | Gap |
   |---|---|---|---|---|---|---|---|---|
   | $10\times10$ | 4 | 0.30 | 23 | $0.957$ | 1 | 0 | $1.000$ | $0.70\%$ |
   | $10\times10$ | 4 | 0.35 | 13 | $1.000$ | 0 | 0 | $1.000$ | $5.06\%$ |
   | $10\times10$ | 6 | 0.30 | 19 | $0.895$ | 2 | 0 | $1.000$ | $19.43\%$ |
   | $14\times14$ | 6 | 0.35 | 13 | $0.846$ | 2 | 0 | $1.000$ | $15.45\%$ |

   You must also report that **the "exhausted" column is all zeros and every prioritized success rate is
   $1.000$** — that is the point of R5.
4. **Part D** — **2** instances are unsolved at cap 3000 and **2/2** are solved at cap 30000. The CBS
   failures of Part C are therefore entirely a budget matter, not a completeness matter.

**Baselines**: (a) the baseline of Part A is the sum of the individually optimal path lengths (lower
bound 8). (b) The baseline of Parts B and C is CBS (optimal), against which prioritized planning is
compared. (c) The baseline of Part D is the cap-3000 result. Optional: in Part B, change the conflict
selection from "first conflict" to "earliest-time conflict" or random and report how the CT node count
changes — that confirms "conflict selection changes $d$" from R4.

**Numbers to report**: all values of the four conditions above, plus the mean amount by which the CBS
cost exceeds the sum of the individual optima in Part B (the coordination cost).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| CBS finds no solution in Part A | A* used **one axis only** for the bounds check ($2\times5$ is not square) | Check that both values of `occ.shape` are used separately; the bug is invisible on square grids |
| One order succeeds in Part A | The first-planned robot's stay at its goal was not added as an obstacle | Check that the obstacle horizon extends well past the path length and keeps blocking the last cell |
| The CBS cost is below the sum of the individual optima | The cost was counted as $\lvert\pi\rvert$, discounting waits | Check that it is $\sum(\lvert\pi_i\rvert-1)$ and that waiting after arrival is not charged |
| Swap conflicts are missed | The edge-conflict check is absent, or checks one direction only | Put two robots face to face in a width-1 corridor; if a solution comes out, it is a bug |
| CBS loses solutions (one exists but is not found) | The branching constrained both robots | Check that each of the two children constrains **one robot only** (problem P1(b)) |
| Constraints during the stay at the goal are violated | The low-level A* ignored vertex constraints after the arrival time | Check that the goal-return condition includes "no constraint on the goal cell at any later time" |
| The success rates in Part C are all 1.0 | Skipped instances were counted in the denominator | Check that the denominator is the number of individually reachable instances |
| The tables of Parts B and C do not reproduce | `rng` was not recreated per setting | Check that `np.random.default_rng(SEED)` is created afresh for each row |

## Open problems

- **(Open problem) A theory of conflict selection** — in (6) of R4 the CT size is set by the number
  $d$ of conflicts that must be resolved, and $d$ depends on **which conflict is branched first**. Good
  conflict-selection heuristics make a large empirical difference (the ICBS and CBSH families), but
  there is no theory of which selection rule is optimal or has an approximation ratio. Current
  approach: the empirical comparisons of
  [the CBS paper](https://doi.org/10.1016/j.artint.2014.11.006) and the later heuristic work. The empty
  seat: lower bounds and approximation ratios from conflict selection to CT size.
- **(Open problem) The boundary between structural assumptions and completeness** — the well-formed
  condition of `cap2015-prioritized-planning` makes prioritized planning complete, but **how weak a
  condition suffices** is open. What hierarchy of conditions lies between the counterexample of R3 and a
  well-formed environment, and what the complexity of deciding whether a given environment satisfies the
  condition is, are both unknown. Current approach: the engineering workaround of guaranteeing warehouse
  layouts by design. The empty seat: a decision algorithm for "is prioritized planning complete in this
  environment?" and its complexity.
- **(Open problem) Quality guarantees under a budget** — R5 shows that under a fixed budget the optimal
  algorithm solves fewer instances. What practice needs is a statement of the form "spending budget $B$
  **guarantees** a solution within such-and-such of optimal", and while bounded-suboptimal MAPF gives
  the quality guarantee it gives no guarantee on the **success rate**. Current approach: anytime
  algorithms and bounded-suboptimal variants. The empty seat: guarantees mapping budget and instance
  distribution to a (success rate, quality) pair.

## Concept check

Solve it with `rc quiz s5-multi-agent-planning`. The quiz is **for concept checking only**; the real
work is the problem set and the reproduction task above (`lesson-standard.md` §4).

## How to study this stage

1. **Solve the counterexample by hand first (45 min)** — draw the $2\times5$ corridor with its alcove on
   paper and find the optimal solution yourself (cost 11). Then, for order $[A,B]$, write down every
   action available to B time by time and confirm that it is stuck. These are the most important
   30 minutes of the lesson.
2. **(4) and (5) from a blank page (45 min)** — the two pillars of CBS optimality. In particular, be able
   to say in one sentence why the "at least one" of (5) gives a **cover**, and why constraining both
   sides breaks it.
3. **Extend A* to space-time (60 min)** — all it takes is making the state $(v, t)$ and filtering by
   constraints. Check that the optimality argument of `c6-search-based-planning` survives intact (a
   consistent heuristic = Manhattan distance). The traps are handling the stay at the goal and
   constraints on the goal cell afterwards.
4. **Run Part A first (45 min)** — see for yourself that CBS finds cost 11 and that prioritized planning
   fails for both orders. Since the grid is not square, the A* bounds-check bug surfaces right here (the
   first row of the diagnosis table).
5. **Separate the two axes with Parts B and C (90 min)** — in Part B see the CT nodes grow exponentially
   with density, and in Part C see that **the optimal algorithm has the lower success rate**. Then confirm
   with Part D that this is a budget matter. Putting the three tables side by side in one report is the
   deliverable of this lesson.
6. **Change the objective with P3 (60 min)** — going to makespan, separate what breaks from what survives.
   Finding on your own that "the lower-bound argument survives and the low-level objective is misaligned"
   means you have understood CBS.
7. **Read the papers as sentences about guarantees (150 min)** — match Sharon et al. §3-5's optimality
   proof step by step against R2' above, see the feasibility-optimality gap in Yu & Rus §3-4, and get the
   condition that recovers completeness from Čáp et al. §III-IV. Write the one-page note per paper
   **without exception**.
8. **Finish with what it cannot do (30 min)** — pick one of the three open problems and write a paragraph.
   The (success rate, quality) guarantee under a budget is motivated directly by the tables of Parts C
   and D.

**Passing bar**: you can write (4), (5) and the counterexample argument of R3 from a blank page, you can
explain why CBS constrains one robot only, you have code satisfying all four conditions of the
reproduction task, and you have notes on all three papers.
