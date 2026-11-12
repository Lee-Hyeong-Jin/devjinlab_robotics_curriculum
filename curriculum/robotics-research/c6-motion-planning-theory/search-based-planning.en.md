---
id: c6-search-based-planning
lang: en
title: Search-based planning
summary: >-
  Heuristic search on a discrete graph, treated from the point of view of its guarantees. Prove the
  optimality of A* from the one-line lemma that "there is always an OPEN node on an optimal path
  whose g is optimal", and watch the $w$-sub-optimality bound of weighted A* fall out of the same
  lemma in two lines. Then derive what ARA* reuses and what it must repair when it lowers the weight
  (inconsistent nodes and the INCONS list), how the D* family responds to a changing environment,
  and the structure by which Multi-Heuristic A* keeps a bound while using inadmissible heuristics.
  The reproduction task reproduces the cost-time trade-off curve and counts how loose the bound is.
objectives:
  - Prove the lemma that an OPEN node with $g = g^\ast$ exists on an optimal path.
  - Derive from that lemma both the optimality of A* and the $w C^\ast$ bound of weighted A*.
  - Explain, through monotonicity of $f$, why a consistent heuristic removes re-expansions.
  - State why ARA* needs inconsistent nodes and the INCONS list, and what it reuses.
  - Explain the structure by which Multi-Heuristic A* keeps the $w_1 w_2 C^\ast$ bound while using inadmissible heuristics.
tags: [motion-planning, heuristic-search, a-star, anytime, replanning, research]
---

# Search-based planning

## Setup and notation

The four earlier lessons of this module are assumed. In particular R1 of
`c6-combinatorial-gcs` (cell decomposition into a graph) and BIT* from
`c6-asymptotic-optimality` (sweeping an implicit random geometric graph with **heuristic search**)
lead into this lesson. Also assumed:

- Graph algorithms: correctness of Dijkstra, priority queues, the invariant of relaxation.
- Induction and proof by contradiction. Probability is **not** needed — this lesson is entirely
  deterministic.

Notation:

| Symbol | Meaning |
|---|---|
| $\mathcal{G} = (S, E, c)$ | finite directed graph with edge costs $c(s,s') > 0$ |
| $s_{start}, s_{goal}$ | start and goal states |
| $g^\ast(s)$ | optimal cost from $s_{start}$ to $s$ |
| $h^\ast(s)$ | optimal cost from $s$ to $s_{goal}$ |
| $C^\ast$ | $g^\ast(s_{goal}) = h^\ast(s_{start})$ |
| $g(s)$ | the cost to $s$ the search has found so far; always $g(s) \ge g^\ast(s)$ |
| $h(s)$ | the heuristic, with $h(s_{goal}) = 0$ |
| $f(s)$ | $g(s) + h(s)$ |
| $f_w(s)$ | $g(s) + w\,h(s)$ — the key of weighted A* |
| OPEN, CLOSED | the open and closed lists |
| INCONS | ARA*'s list of inconsistent nodes (§R3) |
| $v(s)$ | the value of $g(s)$ when $s$ was last expanded |

**Three properties, kept apart.** That distinction is the whole lesson.

- **admissible**: $h(s) \le h^\ast(s)$ for all $s$. **Gives optimality.**
- **consistent**: $h(s) \le c(s,s') + h(s')$ for every edge. Stronger than admissibility
  (monotonicity), and **gives the absence of re-expansions.**
- **$w$-admissible**: $h(s) \le w\, h^\ast(s)$, or an admissible $h$ inflated by $w$.
  **Gives $w$-sub-optimality.**

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof).

- **R1 (the key lemma and the optimality of A*) [D3]** — if $h$ is admissible then, at every moment
  before A* expands $s_{goal}$, **there is an OPEN node $s$ on some optimal path with
  $g(s) = g^\ast(s)$.** From that one line the optimality $g(s_{goal}) = C^\ast$ follows at once.
  If $h$ is moreover **consistent**, $f$ is non-decreasing along any path and therefore **no node is
  expanded twice.**
- **R2 ($w$-sub-optimality bound of weighted A*) [D3]** — if $h$ is admissible and $w \ge 1$, then
  A* run with the key $f_w = g + wh$ satisfies
  $$g(s_{goal}) \;\le\; w\,C^\ast \tag{1}$$
  The proof is the lemma of R1 plus two lines of inequalities. **The bound is loose** — in the
  reproduction task, $w = 5$ permits a factor 5 while the actual cost is 1.13 times the optimum.
- **R3 (ARA*'s consistency repair and the D* family) [D2]** — lowering the weight through
  $w_1 > w_2 > \cdots$ while reusing $g$ makes already-expanded nodes **inconsistent**
  ($v(s) \ne g(s)$) as their $g$ drops later. Collecting those nodes in **INCONS and returning them
  to OPEN at the next iteration** keeps every iteration $w_i$-sub-optimal while the total number of
  expansions stays below that of independent reruns (reproduction task: 21889 versus 26510, a
  **17% saving**). D* and D* Lite apply the same idea to **changing edge costs**, re-establishing
  consistency only on the affected nodes.
- **R4 (Multi-Heuristic A*) [D2]** — run inadmissible heuristics $h_1,\dots,h_k$ in their own queues,
  with the **anchor queue** of an admissible $h_0$ inflated by $w_1$ watching them all. Permitting an
  expansion from queue $i$ only when $\mathrm{key}_i \le w_2\,\mathrm{key}_0$ gives
  $$g(s_{goal}) \;\le\; w_1 w_2\, C^\ast \tag{2}$$
  — the only structural way to **use heuristics without admissibility and still keep a bound.**

## Derivation

### R1 — the key lemma

**Lemma.** Let $h$ be admissible. At any moment before A* expands $s_{goal}$, there is an optimal
path $P = (s_0 = s_{start}, s_1, \dots, s_k = s_{goal})$ and an index $i$ with
$s_i \in \mathrm{OPEN}$ and $g(s_i) = g^\ast(s_i)$.

*Proof.* Fix any optimal path $P$ and let $i$ be the **smallest index on $P$ that is in OPEN**
(existence in step 1).

1. **Such an $i$ exists.** $s_0 = s_{start}$ is in OPEN initially with $g(s_0) = 0 = g^\ast(s_0)$.
   Since $s_{goal}$ has not been expanded, $P$ cannot be entirely CLOSED — if it were, $s_k =
   s_{goal}$ would have been expanded, contradicting the assumption.
2. **$g(s_i) = g^\ast(s_i)$.** Trivial for $i = 0$. For $i \ge 1$, minimality of $i$ puts $s_{i-1}$
   outside OPEN, and it is not unexpanded either, so it is CLOSED. By the induction hypothesis
   $g(s_{i-1}) = g^\ast(s_{i-1})$ when $s_{i-1}$ was expanded, and an expansion relaxes every
   successor, so
   $$g(s_i) \;\le\; g(s_{i-1}) + c(s_{i-1}, s_i) \;=\; g^\ast(s_{i-1}) + c(s_{i-1},s_i)
     \;=\; g^\ast(s_i),$$
   the last equality because a subpath of an optimal path is optimal. Since always
   $g(s_i) \ge g^\ast(s_i)$, equality holds. $\square$

**Optimality of A*.** Take $w = 1$ and look at the moment A* expands $s_{goal}$. The lemma's $s_i$
is in OPEN and A* **pops the node of minimum $f$**, so
$$f(s_{goal}) \;\le\; f(s_i) \;=\; g^\ast(s_i) + h(s_i) \;\le\; g^\ast(s_i) + h^\ast(s_i) \;=\; C^\ast.$$
As $h(s_{goal}) = 0$ we have $f(s_{goal}) = g(s_{goal})$, and since always
$g(s_{goal}) \ge C^\ast$, equality holds. **Admissibility is used in exactly one place**
($h(s_i) \le h^\ast(s_i)$).

**Consistency ⇒ no re-expansion.** If $h$ is consistent then for any edge $(s,s')$,
$$f(s') = g(s') + h(s') \le g(s) + c(s,s') + h(s') \quad\text{and}\quad h(s) \le c(s,s') + h(s')$$
give $f(s') \ge g(s) + h(s) = f(s)$, so **$f$ is non-decreasing along a path**. Hence the $f$ values
A* pops are non-decreasing, and when a node is expanded its $g$ is already optimal (otherwise a node
of smaller $f$ would appear later, contradicting monotonicity). So no CLOSED node needs reopening.

**Where the assumption breaks**: with an $h$ that is admissible but **not consistent**, optimality
survives but nodes can be expanded several times, and in the worst case the number of expansions is
**exponential** (problem P5). Practice therefore demands consistency, which is why grids use the
octile distance — the Euclidean distance is admissible on an 8-neighbour grid but a **weaker** lower
bound and hence slower, while the Manhattan distance is **not admissible** once diagonal moves exist
(it overestimates).

### R2 — the bound of weighted A*

Changing the key to $f_w = g + wh$ with $w \ge 1$ leaves the lemma of R1 **untouched** — its proof
never mentions $f$ (only relaxation and the OPEN/CLOSED structure). That is why the proof takes two
lines.

At the moment $s_{goal}$ is popped, the lemma's $s_i$ is in OPEN and the popped node has minimum
key, so

$$
g(s_{goal}) = f_w(s_{goal}) \;\le\; f_w(s_i) = g^\ast(s_i) + w\,h(s_i)
  \;\overset{(a)}{\le}\; g^\ast(s_i) + w\,h^\ast(s_i)
  \;\overset{(b)}{\le}\; w\big(g^\ast(s_i) + h^\ast(s_i)\big) = w\,C^\ast,
$$

where (a) is admissibility and (b) uses $w \ge 1$, so $g^\ast(s_i) \le w g^\ast(s_i)$. That is (1).

**Inequality (b) is the source of the looseness.** It inflates $g^\ast(s_i)$ by $w$ although there
is no need to — if $s_i$ is near the start then $g^\ast(s_i) \approx 0$ and almost nothing is lost.
So the actual sub-optimality comes out far below $w$; that is why the measured cost ratio at
$w = 5$ is 1.13 in the reproduction task. A tighter bound can be computed **during the run**:

$$
g(s_{goal}) \;\le\; \varepsilon\, C^\ast, \qquad
  \varepsilon = \max\!\left(1,\; \frac{g(s_{goal})}{\min_{s \in \mathrm{OPEN} \cup \mathrm{INCONS}} (g(s) + h(s))}\right).
  \tag{3}
$$

The denominator is a lower bound on $C^\ast$ (the lemma's $s_i$ is in that set, and
$g(s_i)+h(s_i) \le C^\ast$). ARA* **reports** this $\varepsilon$ — an a posteriori certificate
rather than an a priori $w$, and **the same kind of object** the GCS relaxation of
`c6-combinatorial-gcs` provides.

**Where the assumption breaks**: for $w < 1$ the direction of (b) flips and there is **no** bound
(and $g(s_{goal})$ really can exceed $C^\ast$). If $h$ is not admissible, (a) breaks and the bound
vanishes altogether — R4 solves exactly that situation structurally.

### R4 — Multi-Heuristic A*

**The problem.** Good heuristics are usually not admissible: a hand-made score for "is the hand near
the object" in a manipulation task, a learned cost-to-go regressor, several different devices for
escaping different local minima. Using them breaks (a) in R2, so **there is no bound at all.**

**The structure.** Keep $k+1$ queues. Queue 0 is the **anchor**, using an admissible $h_0$ inflated
by $w_1$; queues $1..k$ use $h_i$ (admissibility not required). All queues **share the same $g$
values**. Visit queue $i$ round-robin, but permit an expansion only when

$$
\mathrm{key}_i(\text{top}) \;\le\; w_2 \cdot \mathrm{key}_0(\text{top}).
  \tag{4}
$$

**Deriving the bound.** Looking at the anchor queue alone, R2 applies verbatim, so the anchor's
minimum key never exceeds $w_1 C^\ast$. By (4), an expansion from any queue has key at most
$w_2 \cdot (\text{anchor's minimum key}) \le w_1 w_2 C^\ast$. Whichever queue pops $s_{goal}$,
$g(s_{goal})$ is at most that key, giving (2). **The crux is the single fact that the inadmissible
heuristics only move under the anchor's supervision.**

**Where the assumption breaks**: if the queues do not share $g$, an improvement found in one queue
never reaches another and the comparison in (4) loses its meaning. Replacing (4) by "queue $i$'s own
past key" instead of the anchor's key — a common implementation error — **removes the bound**. And
as $k$ grows, memory grows by a factor $k$ and the round-robin overhead rises, which is why the paper
experiments with only a few heuristics.

## Proof sketch

### R3 — ARA*'s consistency repair

**Hypotheses** H1: $h$ is admissible and consistent. H2: a weight sequence
$w_1 > w_2 > \cdots > w_T \ge 1$. H3: within an iteration, if the $g$ of an already-expanded node
decreases, that node goes into **INCONS** and is not expanded again in that iteration.
H4: at the start of iteration $t$, set $\mathrm{OPEN} \leftarrow \mathrm{OPEN} \cup \mathrm{INCONS}$,
recompute all keys with $w_t$, and clear CLOSED.
**Conclusion** C: the solution of iteration $t$ is $w_t$-sub-optimal, and the total number of
expansions is **below the sum of independent reruns** at each $w_t$.

**Strategy**: maintain one invariant — **$\mathrm{OPEN} \cup \mathrm{INCONS}$ contains every
inconsistent node.** That invariant is what lets the lemma of R1 be reapplied at every iteration.

1. **Definition of inconsistency.** A node $s$ is **inconsistent** if $v(s) \ne g(s)$, i.e. its value
   at last expansion differs from its current value. In the first search, every node whose $g$ drops
   is put into OPEN, so all inconsistent nodes are in OPEN.
2. **Lowering the weight makes CLOSED nodes inconsistent.** A smaller $w$ changes the search order and
   cheaper paths to nodes expanded in an earlier iteration are found. H3 does not put them back into
   OPEN (re-expanding within an iteration would break the $w_t$-sub-optimality proof) — it collects
   them in INCONS instead.
3. **The invariant is maintained.** By 1 and 2 every inconsistent node is in OPEN or INCONS, and H4
   merges the two, so at the start of iteration $t+1$ **all inconsistent nodes are in OPEN**.
4. **$w_t$-sub-optimality of each iteration.** The invariant lets the lemma of R1 be applied to
   iteration $t$'s OPEN (an OPEN node with $g = g^\ast$ exists on an optimal path), and the two lines
   of R2 then give $g(s_{goal}) \le w_t C^\ast$. The tighter value is reported via (3).
5. **Where the saving comes from.** Iteration $t+1$ **does not discard** the $g$ values. Nodes whose
   $g$ is already optimal are never relaxed again and so are not candidates for re-expansion; the
   search only works on "what changed". (Omitted: the quantitative upper bound on the number of
   expansions — Theorems 2 and 3 of the original paper. The size of the saving depends on the graph
   and the weight sequence, and there is no general guarantee.)

**Removing a hypothesis**: drop H3 and return CLOSED nodes directly to OPEN, and re-expansion occurs
within an iteration, destroying the "one expansion per iteration" structure of step 4 and with it the
$w_t$-sub-optimality proof. Drop the "merge INCONS" of H4 and the invariant of step 3 breaks, so
**a node on the optimal path may be in neither list**; the lemma then fails and the bound disappears
— the most common correctness bug in ARA* implementations. Drop consistency from H1 and re-expansion
becomes necessary within an iteration and the saving vanishes.

**The relation to the D* family.** D* and D* Lite maintain the same invariant **when edge costs
change**. They mark both endpoints of a changed edge as inconsistent and "propagate inconsistency"
with a priority queue, re-establishing consistency only on the affected region. Reversing the search
direction, **from goal to start**, is the key implementation choice: as the robot moves, the start
changes and the whole $g$ of a forward search would be invalidated.

## Problem set

Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★, R1)** In step 2 of the lemma of R1, identify exactly what the "induction
hypothesis" is an induction over (number of nodes? number of expansions? the index $i$?) and show
the induction is not circular.
*Strategy*: it is induction over the **time of expansion**, not over the index $i$. Noting that
$s_{i-1}$ was expanded strictly earlier than now removes the circularity.

**P2 (derivation, ★★, R2)** Prove that the $\varepsilon$ of (3) is a valid a posteriori bound: show
$\min_{s \in \mathrm{OPEN} \cup \mathrm{INCONS}}(g(s)+h(s)) \le C^\ast$ and deduce
$g(s_{goal}) \le \varepsilon C^\ast$.
*Solution sketch*: by the lemma of R1 a node with $g(s_i) = g^\ast(s_i)$ is in that set and
$g^\ast(s_i) + h(s_i) \le g^\ast(s_i) + h^\ast(s_i) = C^\ast$. As the denominator is a lower bound on
$C^\ast$, the ratio is an upper bound.

**P3 (proof, ★★, R1)** Prove "consistent ⇒ admissible" and give a counterexample to the converse.
*Strategy*: sum $h(s) \le c(s,s') + h(s')$ along an optimal path to make a telescoping sum and use
$h(s_{goal}) = 0$. For the converse, build a three-node graph where the middle node's $h$ is dropped
to zero.

**P4 (numerical, ★, R2)** On the grid of the reproduction task $C^\ast = 342.693434176$. At
$w = 1.5$, compute the cost bound permitted by (1) and its ratio to the measured
$359.379726$, and estimate the range of values the $\varepsilon$ of (3) would report.
*Answer*: the bound is $1.5 \times 342.693434176 = 514.040151$. Measured/bound $= 0.699$ and
measured/optimal $= 1.04869$, so the bound is **43% looser than reality** (a factor
$1.5/1.04869 = 1.4304$). The $\varepsilon$ of (3) lies in $[1.04869,\ 1.5]$, approaching 1.04869 as
the minimum $g+h$ on OPEN approaches $C^\ast$. Tolerance $10^{-6}$ relative.

**P5 (counterexample, ★★★, R1)** Construct a family of graphs on which A* with an admissible but
inconsistent heuristic re-expands nodes **exponentially** often ($2^{\Omega(n)}$ expansions on $n$
nodes).
*Property checklist*: on a chain graph, set edge costs to powers of two and alternate $h$ between 0
and nearly $h^\ast$, so that later nodes repeatedly receive improvements from earlier ones. Martelli's
classical construction has this shape — and write down each of the two ways to stop the
re-expansions (making $h$ consistent, or forbidding re-expansion and accepting sub-optimality).

**P6 (proof, ★★, R4)** Reprove (2) in your own words, and show by counterexample why the bound
disappears if the condition (4) is changed from "the anchor's minimum key" to "queue $i$'s own past
minimum key".
*Strategy*: the anchor holding the upper bound $w_1 C^\ast$ is the only source of the guarantee. A
queue's own past key has no relation to $C^\ast$ and so transmits no bound.

**P7 (implementation, ★★, R1·R2·R3)** Write the A*, weighted A* and ARA* of the reproduction task.
Requirements: 8-neighbour octile heuristic, no diagonal corner cutting, ARA*'s INCONS and key
recomputation, reporting the $\varepsilon$ of (3).
*Rubric*: (a) $C^\ast$ and the expansion counts match the tables of the reproduction task;
(b) $\text{cost} \le w C^\ast$ at every $w$; (c) ARA*'s cumulative expansions are below the sum of
independent reruns; (d) you run it **without** INCONS and report at which $w$ the sub-optimality
bound breaks.

**P8 (proof, ★★★, R1)** State precisely the claim of Dechter & Pearl 1985 that A* is "optimally
efficient", and write the conditions under which it holds (which class of algorithms, which
tie-breaking, which heuristic). Explain how the fact that Dijkstra expanded 27801 nodes and A* 13994
in the reproduction task relates to that claim.
*Strategy*: the claim has the form "any **admissible algorithm** using the same heuristic must expand
every node A* expands with $f < C^\ast$". Dijkstra is the specialization of A* with $h \equiv 0$, so
it uses a **different heuristic** and the comparison falls outside the claim's scope.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions.

1. **Hart, Nilsson & Raphael, "A formal basis for the heuristic determination of minimum cost paths"
   (1968, IEEE T-SSC)** — role: `seminal`. <https://doi.org/10.1109/TSSC.1968.300136>
   *Why read it*: R1 comes from here. The point is to see how the 1968 vocabulary ("admissible",
   "consistency assumption") differs from today's.
   Extra questions: (a) is the authors' "consistency assumption" the same as consistency here?
   (b) how does the paper handle re-expansion?
2. **Likhachev, Gordon & Thrun, "ARA*: anytime A* with provable bounds on sub-optimality"
   (2003, NIPS)** — role: `seminal`.
   <https://papers.nips.cc/paper_files/paper/2003/hash/ee8fe9093fbbb687bef15a38facc44d2-Abstract.html>
   *Why read it*: the source of R3. INCONS and the a posteriori bound (3) are its two pillars.
   Extra questions: (a) is the $\varepsilon$ the authors report the same as (3)? (b) how is the weight
   sequence chosen, and is there a theoretical basis for the choice? (c) were the experimental
   baselines tuned fairly?
3. **Aine, Swaminathan, Narayanan, Hwang & Likhachev, "Multi-Heuristic A*" (2016, IJRR)** — role:
   `standard`. <https://doi.org/10.1177/0278364915594029>
   *Why read it*: the source of R4. The problem statement itself — "how to use inadmissible
   heuristics safely" — is central in the era of learned heuristics.
   Extra questions: (a) how does the difference between Shared and Independent MHA* affect the bound
   (2)? (b) how does the paper measure the relation between the number of heuristics $k$ and
   performance? (c) which assumption breaks first when this structure is applied to a learned
   heuristic?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation or one figure. (4) what is guaranteed theoretically,
and **what is not**? (5) the independent and dependent variables and the baselines, and were the
baselines tuned fairly? (6) does the metric match the claim, and are variance and seeds reported?
(7) what is missing for reproduction? (8) if the result were wrong, which assumption would you doubt
first? (9) computational and memory complexity, and real-time feasibility. (10) what would you change
to go beyond this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 2 minutes in total, under 1 GB of
memory. numpy plus the standard `heapq` only. No external data.

**Input data (given by the lesson).** A $201 \times 201$ grid. The obstacles are a **deterministic
random field**: cells where a uniform draw from numpy `default_rng(7)` is below $0.30$ are blocked,
with the $3\times3$ corners around the start and the goal cleared. $s_{start} = (1,1)$,
$s_{goal} = (199,199)$. Eight neighbours, diagonal cost $\sqrt{2}$, and **no diagonal corner
cutting** (a diagonal move is forbidden if either orthogonal neighbour is blocked). The heuristic is
the octile distance $h = (dx+dy) + (\sqrt2 - 2)\min(dx,dy)$, which is **admissible and consistent**
on this grid. The number of free cells is 28339.

**Acceptance criteria — all five must hold.**

1. **The optimum and two reference runs** — $C^\ast = 342.693434176$ (relative error $10^{-9}$).
   $h \equiv 0$ (Dijkstra) and octile A* give the **same cost** (difference $< 10^{-9}$) with
   $27801$ and $13994$ expansions respectively (these must match exactly — with the same
   tie-breaking the runs are deterministic).
2. **The cost-time trade-off** — the cost and expansion counts of weighted A* match the following
   **exactly**.

   | $w$ | 1.0 | 1.1 | 1.25 | 1.5 | 2.0 | 3.0 | 5.0 |
   |---|---|---|---|---|---|---|---|
   | cost | 342.693434 | 343.279221 | 347.865007 | 359.379726 | 368.450793 | 379.622366 | 387.764502 |
   | cost/$C^\ast$ | 1.00000 | 1.00171 | 1.01509 | 1.04869 | 1.07516 | 1.10776 | 1.13152 |
   | expansions | 13994 | 8910 | 1881 | 681 | 548 | 496 | 485 |

3. **Checking the bound (R2)** — $\text{cost} \le w\,C^\ast$ at every $w$, and the looseness
   $w / (\text{cost}/C^\ast)$ **grows** with $w$ (1.098 at $w=1.1$, 4.419 at $w=5$) — write in the
   report that inequality (b) of derivation R2 is the cause.
4. **ARA*'s reuse (R3)** — run ARA* with the weight sequence $(3.0, 2.0, 1.5, 1.25, 1.1, 1.0)$ and
   confirm the cumulative expansions are $21889$ while the sum of **independent reruns** over the same
   sequence is $26510$ (a $17.4\%$ saving). Each iteration's cost must not exceed its $w_t C^\ast$,
   and the last iteration must reach $C^\ast$ **exactly**.
5. **Removing INCONS** — run the same ARA* without INCONS (discarding inconsistent nodes) and report
   at which iteration the cost exceeds $w_t C^\ast$ or the last iteration fails to reach $C^\ast$.
   **This is the experimental evidence for why hypothesis H4 of R3 is needed.**

**Baselines.** (a) Dijkstra ($h \equiv 0$) — criterion 1. (b) The sum of independent reruns —
criterion 4. (c) A deliberately broken version of itself — criterion 5.

**Failure table**

| Symptom | Cause | How to check |
|---|---|---|
| $C^\ast$ differs from the table | corner cutting was allowed (the diagonal condition is missing) | count the diagonal moves — allowing corner cutting lowers the cost |
| the expansion counts differ | the priority queue breaks ties differently, or CLOSED is tested on push rather than pop | check that you push $(f, \text{node})$ tuples and test CLOSED right after the pop |
| expansions do not fall as $w$ grows | the key was written $w(g+h)$ instead of $g + wh$ (which does not change the order) | check whether expansions fall below 500 at $w = 10$ |
| cost $> wC^\ast$ at some $w$ | CLOSED nodes are re-expanded, or the key is not updated when $g$ is | print the offending $w$ and the path, and re-sum the edge costs |
| ARA*'s cumulative expansions exceed the independent sum | $g$ was reset at each iteration (the whole point of the reuse was discarded) | print the size of $g$ at the start of iteration 2 |
| ARA* fails to reach $C^\ast$ at the last iteration | INCONS was not returned to OPEN (violating H4) | compare with the outcome of the experiment in criterion 5 |

## Open problems

- **(open problem) Guarantees for learned heuristics** — a neural cost-to-go estimate is not
  admissible, (a) of R2 breaks and the sub-optimality bound disappears. MHA* (R4) blocks that
  structurally, but **$w_1 w_2$ compounds multiplicatively** so the bound is not practical, and
  **calibrating** a learned heuristic to be admissible is so conservative that it erases the gain.
  Current approaches: [MHA*](https://doi.org/10.1177/0278364915594029), and the analogous problem on
  the sampling side ([Ichter et al. 2018](https://arxiv.org/abs/1709.05448)). What is missing: a
  non-vacuous a posteriori bound for a learned heuristic.
- **(open problem) Predicting the expansion count in advance** — (3) is an a posteriori bound, and
  there is no theory that says in advance "on this graph at this $w$, this many expansions". Raising
  $w$ from 1.1 to 1.25 in the reproduction task cuts expansions from 8910 to 1881, a factor
  **4.7**, and the location of that jump cannot be predicted. Current approach: analysis in terms of
  the distribution of heuristic error ([Dechter & Pearl 1985](https://doi.org/10.1145/3828.3830)).
  What is missing: a prediction in terms of quantities measurable on a practical graph — the same
  root as the identical hole on the sampling side (the first open problem of
  `c6-sampling-completeness`).
- **(open problem) Unifying search and sampling in continuous spaces** — BIT*
  (`c6-asymptotic-optimality`) bridges the two, but when evaluating an edge of the "implicit graph"
  is expensive (collision checking), the order in which to evaluate is a separate problem and no
  optimal strategy is known. Current approaches: lazy evaluation and path selection in one framework
  in [BIT*](https://arxiv.org/abs/1405.5848) and [ABIT*](https://arxiv.org/abs/2002.06589). What is
  missing: an optimal search policy with the edge-evaluation cost modelled explicitly.

## Concept check

Run `rc quiz c6-search-based-planning`. Concept checking only; the real work is the problem set and
the reproduction task.

The six items cover: how many places admissibility is used in the optimality proof; why the
$wC^\ast$ bound is loose; what breaks if INCONS is not returned to OPEN; the relation between
admissibility and consistency; the three elements of MHA*; and the property that removes
re-expansions.

## How to study this stage

1. **Separate the three properties first (20 min)** — tabulate admissibility, consistency and
   $w$-admissibility by their definitions and **the guarantee each gives**. That table is the index
   of the whole lesson. Solving P3 alongside fixes the inclusions in your hands.
2. **Memorize one lemma (60 min)** — prove the lemma of R1 from a blank page. The single line "there
   is an OPEN node on an optimal path with $g = g^\ast$" is the source of **every** guarantee in A*,
   weighted A* and ARA*. The moment you confirm that its proof never mentions $h$, R2 becomes two
   lines.
3. **See the looseness as numbers (40 min)** — do P4. Confirm by computation that $w = 5$ permits a
   factor 5 while reality is 1.13, and that (3) recovers that loss. **The difference between an a
   priori bound and an a posteriori certificate** is the most practical lesson here.
4. **Run ARA* twice (75 min)** — the reproduction task. First implement INCONS correctly and hit
   criterion 4, then **deliberately discard INCONS** and reproduce criterion 5. Watching the guarantee
   break is the only way to remember H4.
5. **Three papers (120 min)** — read them 1968 → 2003 → 2016. The guarantee is defined in 1968, made
   anytime in 2003, and in 2016 a structure appears that gives up admissibility while keeping the
   guarantee. Note that all three stand on the same lemma.
6. **Problem set (150 min)** — P4 and P7 first, then P1, P2 and P3, then P5, P6 and P8 with whatever
   time remains. P5 (exponential re-expansion) is the hardest, and solving it settles "why everybody
   uses consistent heuristics".

**Passing bar**: you can prove the lemma of R1 from a blank page and derive from it both the
optimality of A* and the bound of weighted A*, you have code satisfying the five criteria of the
reproduction task (especially the INCONS-removal experiment of criterion 5), and you can state the
difference between "the a priori $w$ bound" and "the a posteriori $\varepsilon$ certificate". You
have notes on all three papers.
