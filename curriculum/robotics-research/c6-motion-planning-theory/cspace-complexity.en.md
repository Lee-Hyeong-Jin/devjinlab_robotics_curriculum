---
id: c6-cspace-complexity
lang: en
title: Configuration space and complexity
summary: >-
  Restate motion planning as a connectivity question about the configuration space, and derive the
  structure of the obstacle map $\mathcal{C}_{obs}$ (Minkowski sum, the cylinder structure of a
  serial chain) from scratch. Then reconstruct the PSPACE-completeness of generalized motion
  planning from both sides, lower and upper bound, and end at what a complexity class does *not*
  say about an instance. The C-space of a 2-link arm is computed on a grid and its holes counted.
objectives:
  - Prove from the obstacle map $q \mapsto A(q) \cap O$ that $\mathcal{C}_{free}$ is open.
  - Derive the Minkowski-sum form of $\mathcal{C}_{obs}$ for a translating rigid body and state the cylinder structure for a serial chain.
  - State the topology of a planar $n$R chain, a planar rigid body and a spatial rigid body, and explain why none of them admits a global chart.
  - Reconstruct the PSPACE-completeness of generalized motion planning from both the reduction (lower bound) and the algebraic decision procedure (upper bound).
  - Explain by counterexample what PSPACE-completeness does not guarantee about the difficulty of a particular instance.
tags: [motion-planning, configuration-space, complexity, topology, pspace, research]
---

# Configuration space and complexity

## Setup and notation

This is the first lesson of module C6, and the whole module uses the notation fixed here.
Assumed:

- `c1-so3-se3-exponential` — in particular the result (its R4) that $SO(3) \cong \mathbb{RP}^3$ is
  compact and therefore admits no global three-parameter chart. It is used verbatim below.
- Topology: open sets, compactness, connected components, homotopy equivalence, the Betti numbers
  $b_0, b_1, b_2$ and the Euler characteristic $\chi = b_0 - b_1 + b_2$. General homology is **not**
  needed — nothing beyond counting $\chi = V - E + F$ on a surface is used.
- Computational complexity: decision problems, polynomial-time reductions, PSPACE and
  PSPACE-completeness, and the consequence of Savitch's theorem (NPSPACE $=$ PSPACE).
- Real algebraic geometry is not assumed. Semialgebraic sets appear only as far as R4 needs them.

Notation (fixed for all of module C6):

| Symbol | Meaning |
|---|---|
| $\mathcal{C}$ | configuration space; the robot's number of degrees of freedom is $n = \dim \mathcal{C}$ |
| $q \in \mathcal{C}$ | one configuration |
| $\mathcal{W}$ | workspace, $\mathbb{R}^2$ or $\mathbb{R}^3$ |
| $A(q) \subset \mathcal{W}$ | the **closed** region the robot occupies at $q$ |
| $O \subset \mathcal{W}$ | the union of the obstacles; assumed **closed** |
| $\mathcal{C}_{obs}$ | $\{q \in \mathcal{C} : A(q) \cap O \neq \emptyset\}$ |
| $\mathcal{C}_{free}$ | $\mathcal{C} \setminus \mathcal{C}_{obs}$ |
| $\sigma : [0,1] \to \mathcal{C}_{free}$ | a path; continuity suffices, no differentiability is required |
| $\delta(q)$ | clearance, $\operatorname{dist}(A(q), O)$ |
| $T^n$ | the $n$-torus $(S^1)^n$ |
| $X \oplus Y$ | Minkowski sum $\{x + y : x \in X, y \in Y\}$ |

**The problem (PATH).** The input is $(\mathcal{C}, A, O, q_s, q_g)$ and the output is the yes/no
answer to "does a continuous path $\sigma : [0,1] \to \mathcal{C}_{free}$ with $\sigma(0) = q_s$ and
$\sigma(1) = q_g$ exist?" In other words, **motion planning is a connectivity question about
$\mathcal{C}_{free}$**. That one line is the whole lesson, and the remaining six lessons of the
module are different ways of answering it.

Three assumptions, stated explicitly; later lessons break them one at a time.

- **(A1) geometry** — $A(q)$ is a closed set moving continuously with $q$, and $O$ is closed.
- **(A2) no constraints** — a path need only be continuous. Differential constraints enter in
  `c6-kinodynamic-planning`.
- **(A3) full information** — $O$ and $A$ are known exactly. Uncertainty is outside this module.

## Self-diagnosis before starting

This is the module's first lesson, so check your readiness first. **Prerequisite lessons are not
locked** — if you can do all of the following, skip the recommended prerequisites and start here.
**If two or more items block you**, going back to the lesson in parentheses is faster.

1. A closed surface has $V = 8$ vertices, $E = 16$ edges and $F = 8$ faces. What is its Euler
   characteristic, and which surface is it? (`f0-proofs-math-maturity`)
   **Answer**: $\chi = V - E + F = 8 - 16 + 8 = 0$. For a closed orientable surface
   $\chi = 2 - 2g$, so $g = 1$ — a **torus**. A sphere would give $\chi = 2$.
2. What is the area of the Minkowski sum $X \oplus Y$ of $X = \{(x,y) : x^2 + y^2 \le 1\}$ and
   $Y = \{(x,y) : |x| \le 2, |y| \le 1\}$? (`f0-linear-algebra`)
   **Answer**: a rounded rectangle, $8 + 12 + \pi = 20 + \pi \approx 23.1416$ (tolerance
   $10^{-4}$): the rectangle's area $8$, a band of thickness 1 along its boundary
   ($\mathrm{per}(Y) = 12$), and four quarter-discs summing to $\pi$. This is Steiner's formula
   $|X \oplus rB| = |X| + r\,\mathrm{per}(X) + \pi r^2$ with $r = 1$.
3. In one sentence, why is $SO(3)$ compact and not diffeomorphic to $\mathbb{R}^3$?
   (`c1-so3-se3-exponential`)
   **Answer**: $SO(3) \cong \mathbb{RP}^3 = S^3/\{\pm1\}$ is a quotient of the compact $S^3$ and
   hence compact; a diffeomorphism preserves compactness, so it cannot be diffeomorphic to the
   non-compact $\mathbb{R}^3$.
4. What is known about the inclusion between PSPACE and NP? Define "PSPACE-complete" in one line.
   (`f0-proofs-math-maturity`)
   **Answer**: $\mathrm{NP} \subseteq \mathrm{PSPACE}$, and whether the inclusion is strict is open
   (Savitch gives $\mathrm{NPSPACE} = \mathrm{PSPACE}$). $L$ is PSPACE-complete iff
   $L \in \mathrm{PSPACE}$ and every $L' \in \mathrm{PSPACE}$ reduces to $L$ in polynomial time.
5. Write, in at most two lines of numpy/scipy, code that counts the 4-connected components of a
   2D boolean array, and say why that result is wrong when the array is a **torus** (opposite
   edges identified). (`f0-python-numerics-git`)
   **Answer**: `from scipy import ndimage` then `lab, n = ndimage.label(free)`. `label` treats the
   array border as a wall, so on a torus, where $j = 0$ and $j = N-1$ are adjacent, one component is
   split in two and $n$ overcounts — the seam has to be stitched back with a union–find.

If all five went through, go straight to `## Key results`. If 3 or 5 blocked you, read
`c1-so3-se3-exponential` and the
failure table of the reproduction task respectively.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (structure of the obstacle map) [D2]** — under (A1):
  (a) $\mathcal{C}_{obs}$ is closed and $\mathcal{C}_{free}$ is open.
  (b) For a body that only **translates** in $\mathcal{W} = \mathbb{R}^d$, i.e.
  $A(q) = A(0) \oplus \{q\}$,
  $$\mathcal{C}_{obs} = O \oplus (-A(0)). \tag{1}$$
  (c) In a serial chain of links $1, \dots, n$, the pose of link $i$ depends only on
  $q_1, \dots, q_i$, so the obstacle region it generates is a **cylinder over the first $i$
  coordinates**:
  $$\mathcal{C}_{obs}^{(i)} = \Pi_i^{-1}\!\big(S_i\big), \quad \Pi_i(q) = (q_1,\dots,q_i), \quad
    \mathcal{C}_{obs} = \bigcup_{i=1}^{n} \mathcal{C}_{obs}^{(i)}. \tag{2}$$
- **R2 (topology of configuration space, and counting holes) [D2]** — a planar $n$R chain has
  $\mathcal{C} = T^n$, a planar rigid body $\mathbb{R}^2 \times S^1$, a spatial rigid body
  $\mathbb{R}^3 \times \mathbb{RP}^3$. None is diffeomorphic to $\mathbb{R}^n$, so **there is no
  global chart**. When $\mathcal{C}_{free}$ and $\mathcal{C}_{obs}$ meet along a 1-manifold (a union
  of circles),
  $$\chi(\mathcal{C}_{free}) + \chi(\mathcal{C}_{obs}) = \chi(\mathcal{C}), \tag{3}$$
  and a compact subsurface with boundary has $b_2 = 0$, so the number of holes is determined by
  $b_1 = b_0 - \chi$, i.e. **by grid counting alone**.
- **R3 (PSPACE-completeness of generalized motion planning) [D2]** — when the number of degrees of
  freedom $n$ is part of the input, the generalized mover's problem is PSPACE-complete. The lower
  bound is a reduction from acceptance of polynomial-space Turing machines
  ([Reif 1979](https://doi.org/10.1109/SFCS.1979.10)), and it already holds for axis-aligned
  rectangles translating in the plane
  ([Hopcroft, Schwartz & Sharir 1984](https://doi.org/10.1177/027836498400300405)). The upper bound
  comes from $\mathcal{C}_{free}$ being semialgebraic together with a roadmap algorithm that decides
  connectivity in polynomial space ([Canny 1988](https://openlibrary.org/works/OL4626080W)).
- **R4 (cost of exact algebraic algorithms) [D1]** — with $m$ constraint polynomials of degree $d$
  in $n$ variables, cylindrical algebraic decomposition (CAD) costs $(md)^{2^{O(n)}}$ —
  **doubly exponential** — while Canny's roadmap costs $m^n d^{O(n^4)}$ — **singly exponential**.
  For fixed $n$ both are polynomial in $m$ and $d$, so "motion planning is hard" is true **only
  when the number of degrees of freedom is part of the input**.

## Derivation

### R1(a) — $\mathcal{C}_{free}$ is open

It suffices to show $\mathcal{C}_{obs}$ is closed. Let $q_k \to q$ with $q_k \in \mathcal{C}_{obs}$,
so by definition there is $x_k \in A(q_k) \cap O$.

1. The closure of $\{q_k\}$ is compact, and $A(\cdot)$ maps compact sets to compact sets (the body
   is closed and bounded), so $\{x_k\}$ is bounded. Pass to a subsequence with $x_k \to x$.
2. $O$ is closed and $x_k \in O$, hence $x \in O$.
3. $A$ is continuous in $q$ (in the Hausdorff metric), so from $x_k \in A(q_k)$, $q_k \to q$ and
   $x_k \to x$ we get $x \in A(q)$. Thus $x \in A(q) \cap O \ne \emptyset$, i.e.
   $q \in \mathcal{C}_{obs}$.

So $\mathcal{C}_{obs}$ is closed and $\mathcal{C}_{free}$ is open. **Why this matters**: being open,
$\mathcal{C}_{free}$ contains a ball with $\delta(q) > 0$ around every one of its points, and that is
what makes **finite-precision sampling meaningful**. Every probabilistic-completeness proof in
lesson 3 is carried out on those balls.

**Where the assumption breaks**: modelling $O$ as an **open** set makes $\mathcal{C}_{obs}$ open and
$\mathcal{C}_{free}$ closed. Configurations that graze an obstacle then become free, paths with
$\delta(q) = 0$ are admitted, and every clearance-based completeness guarantee collapses. Planning
that deliberately allows contact lives on exactly this boundary and is the subject of
`s2-planning-through-contact`.

### R1(b) — a translating body: the Minkowski sum

With $A(q) = A(0) \oplus \{q\} = \{a + q : a \in A(0)\}$,

$$
q \in \mathcal{C}_{obs}
  \iff \exists a \in A(0),\; a + q \in O
  \iff \exists a \in A(0),\, \exists o \in O,\; q = o - a,
$$

that is $q \in O \oplus (-A(0))$, and the converse holds as well, giving (1). Three lines, but a
strong conclusion: **planning for a translating robot is exactly planning for a point among
inflated obstacles.** If $A(0)$ and $O$ are convex so is $O \oplus (-A(0))$; if $A(0)$ is a union of
$k$ convex pieces, $\mathcal{C}_{obs}$ is a union of $k$ convex pieces — and that decomposition is
the starting point of `c6-combinatorial-gcs`.

**Where the assumption breaks**: with rotation, (1) is **false**. For
$A(q) = R(\theta)A(0) \oplus \{p\}$ one gets
$\mathcal{C}_{obs} = \bigcup_\theta \big(O \oplus (-R(\theta)A(0))\big) \times \{\theta\}$, a
different Minkowski sum in every slice, and the slices change **topology** with $\theta$ (a rod
passing a narrow gap: two components at some $\theta$, one at another). Carrying planar-translation
intuition over to a spatial rigid body breaks here.

### R1(c) — the cylinder structure of a serial chain

In a planar $n$R chain the pose of link $i$ is
$T_i(q) = T_1(q_1) T_2(q_2) \cdots T_i(q_i)$, so $A_i(q) = T_i(q) A_i^{\text{local}}$ does **not**
depend on $q_{i+1}, \dots, q_n$. Defining

$$
S_i \;=\; \{(q_1,\dots,q_i) : A_i \cap O \ne \emptyset\} \subset (S^1)^i
$$

gives $q \in \mathcal{C}_{obs}^{(i)} \iff \Pi_i(q) \in S_i$, which is (2). The set
$\mathcal{C}_{obs}^{(i)}$ is determined by the first $i$ coordinates and is **stretched out whole**
along the remaining $n-i$.

For $n = 2$ the consequence is visible. The region $\mathcal{C}_{obs}^{(1)} = S_1 \times S^1$
generated by link 1 is a **band wrapping the torus** in the $\theta_2$ direction, and therefore (if
non-empty) **never contractible**. An obstacle that only link 2 can touch, by contrast, can be a
local blob depending on both $\theta_1$ and $\theta_2$. Hence the following, verified numerically in
the reproduction task:

> If the obstacle is farther than $\ell_1$ from the base ($\ell_1$ the first link length), link 1
> can never touch it and $\mathcal{C}_{obs}$ can be a contractible blob inside the torus. If the
> distance is $\le \ell_1$, there is an interval of $\theta_1$ at which link 1 collides and
> $\mathcal{C}_{obs}$ **necessarily** contains a band wrapping $\theta_2$.

### R2 — topology, and counting holes

**Topology.** Each joint of a planar $n$R chain is an $S^1$ and they are independent, so
$\mathcal{C} = T^n$. A planar rigid body gives $\mathbb{R}^2 \times S^1$ and a spatial one
$SE(3) \cong \mathbb{R}^3 \times SO(3) \cong \mathbb{R}^3 \times \mathbb{RP}^3$
(`c1-so3-se3-exponential` R4).
$T^n$ and $\mathbb{RP}^3$ are compact and $\mathbb{R}^n$ is not, so there is no global chart.
**The practical consequence**: a planner that treats $[0,2\pi)^n$ as a box loses adjacency across
the seam $\theta = 0 \equiv 2\pi$. A grid search must index modulo $N$; a sampling planner must use
the distance $\min(|\Delta\theta|, 2\pi - |\Delta\theta|)$. Omit that one line and you get a
"planner finds no solution" bug whose cause is not the algorithm but the topology.

**Counting holes.** Split $\mathcal{C} = T^2$ into two closed subcomplexes
$F = \overline{\mathcal{C}_{free}}$ and $B = \mathcal{C}_{obs}$. Inclusion–exclusion gives

$$
\chi(F) + \chi(B) = \chi(T^2) + \chi(F \cap B) = 0 + \chi(F \cap B).
$$

If $F \cap B$ is a smooth boundary, i.e. a finite union of circles, then $\chi(S^1) = 0$ gives
$\chi(F \cap B) = 0$ and hence (3). $F$ is a compact surface with boundary, so it has no closed
component and $b_2(F) = 0$, whence

$$
b_1(F) = b_0(F) - \chi(F). \tag{4}
$$

On a grid, count $\chi(F) = V - E + F$ (free pixels as 2-cells, their edges as 1-cells, their
corners as 0-cells, with **indices taken modulo $N$**) and get $b_0$ by stitching the seam with a
union–find; then $b_1$ follows. Concretely, for the 2R arm with $\ell_1 = \ell_2 = 1$ and disc
obstacles of radius $r$:

| Obstacle | does link 1 touch it? | $\chi(F)$ | $b_0$ | $b_1$ | shape of $\mathcal{C}_{obs}$ |
|---|---|---|---|---|---|
| $c=(1.5,0)$, $r=0.2$ | no ($1.3 > \ell_1$) | $-1$ | 1 | 2 | one contractible blob |
| $c=(1.5,0)$ and $(0,1.5)$, $r=0.2$ | no | $-2$ | 1 | 3 | two blobs |
| $c=(1.3,0)$, $r=0.35$ | yes ($0.95 \le \ell_1$) | $0$ | 1 | 1 | a band wrapping $\theta_2$ |
| $c=(0.6,0)$, $r=0.3$ | yes | $0$ | 1 | 1 | a band wrapping $\theta_2$ |

Check the first row by hand: removing one open disc from the torus gives $\chi = 0 - 1 = -1$; it
stays connected so $b_0 = 1$, and (4) gives $b_1 = 2$ — both generators of the torus survive. In the
third row the band kills the $\theta_2$ generator and $b_1$ drops to 1. **The cylinder structure of
R1(c) is visible directly in the topology.**

**Where the assumption breaks**: (3) applies only when $F$ and $B$ meet along a 1-manifold. If the
obstacle is tangent at a single point (say a disc pinches $\mathcal{C}_{free}$ at exactly one
point), $F \cap B$ acquires a point with $\chi = 1$ and (3) is off by one. On a grid this shows up
as a free region connected only through a pixel diagonal, so if the 4-neighbour and 8-neighbour
answers differ, suspect a tangency.

### R4 — cost of exact algebraic algorithms [D1]

1. Schwartz & Sharir 1983 decompose $\mathcal{C}$ by **cylindrical algebraic decomposition**:
   project out one variable at a time, taking discriminants and resultants at each step, and split
   into cells on which signs are constant.
2. Each projection step **squares the number and degree** of the polynomials, so after $n$ steps the
   cost is $(md)^{2^{O(n)}}$ — **doubly exponential**. Complete, but impossible to compute beyond
   $n = 3$.
3. Canny 1988 gives up on the full decomposition and builds only a one-dimensional roadmap, bringing
   this down to $m^n d^{O(n^4)}$ — **singly exponential**. The key idea is "do not enumerate cells;
   keep one representative curve per component".
4. For constant $n$ both are polynomial in $m$ and $d$. So **for a robot with a fixed number of
   degrees of freedom, motion planning is polynomial time**, and the practical difficulty lies not
   in the complexity class but in the constant $d^{O(n^4)}$ and in handling geometric degeneracies
   numerically.

## Proof sketch

### R3 — PSPACE-completeness

R3 is a [D2] result, but its claims — "a reduction exists" and "a decision procedure exists" — are
**existence claims**, so it is written in the format of `lesson-standard.md` §3 (hypotheses and
conclusion separated → strategy → steps → gaps → why the hypotheses are needed).

**Hypotheses** H1: the number of degrees of freedom $n$ (or of moving bodies) is **part of the
input**. H2: $A$ and $O$ are described finitely by polynomial inequalities with rational
coefficients. H3: paths carry no differential constraints (assumption (A2)).
**Conclusion** C: PATH is PSPACE-complete.

**Strategy (lower bound).** "**Make the free configuration space of a linkage into the
configuration graph of a Turing machine.**"

1. For a decision problem $L \in$ PSPACE and an input $w$ with $|w| = n$, take a deterministic
   Turing machine $M$ that uses only $p(n)$ cells. A configuration of $M$ (tape contents, head
   position, state) is one of $2^{O(p(n))}$, but **writing one down takes $O(p(n))$ bits**.
2. Build a linkage with one joint per tape cell. Which of two regions ($\approx 0$ / $\approx \pi$)
   the angle of joint $j$ lies in encodes that cell's bit. The length of the chain and the number of
   obstacles are polynomial in $p(n)$.
3. **The key lemma (Reif 1979 §3–4)**: obstacles can be arranged as "channels" so that a path in the
   free space can move **one joint at a time** between the two regions, and only when a transition
   rule of $M$ permits it. (Omitted: the channel geometry — Lemmas 1–3 and Figures 2–4 of Reif 1979.
   Three dimensions are needed because the wiring has to cross without the links passing through one
   another.)
4. Then a path from $q_s$ to $q_g$ inside $\mathcal{C}_{free}$ exists $\iff$ $M$ accepts $w$. The
   reduction is computable in time polynomial in $n$, so PATH is PSPACE-hard.
5. **The degrees of freedom are essential; the linkage is not.** Hopcroft, Schwartz & Sharir 1984
   obtain the same conclusion for **axis-aligned rectangles translating inside a rectangular box**
   (the warehouseman's problem). No joints, no rotation, no third dimension are required — only that
   **the number of moving bodies is part of the input**.

**Strategy (upper bound).** "**Turn the connectivity question into a first-order formula over the
reals.**"

1. If $A$ and $O$ are given by polynomial inequalities, the collision condition
   $A(q) \cap O \neq \emptyset$ is a boolean combination of polynomial inequalities in $q$. Hence
   $\mathcal{C}_{free}$ is a **semialgebraic set** defined by $m$ polynomials of degree $\le d$ in
   $n$ variables.
2. By Tarski–Seidenberg, "$q_s$ and $q_g$ lie in the same connected component" is a first-order
   formula admitting quantifier elimination, hence **decidable**. That alone yields no complexity
   bound.
3. Canny's roadmap: construct a one-dimensional semialgebraic set
   $\mathcal{R} \subset \mathcal{C}_{free}$ such that (a) $\mathcal{R}$ meets every connected
   component of $\mathcal{C}_{free}$ and (b) $\mathcal{R} \cap$ (each component) is connected. The
   connectivity question then reduces to graph search on $\mathcal{R}$.
4. $\mathcal{R}$ need **not be stored in full**: it can be generated locally by solving critical-point
   conditions, and if each step runs in polynomial space so does the whole algorithm. Hence
   PATH $\in$ PSPACE. Combining 2 and 4 with the lower bound gives **PSPACE-completeness**.
   (Omitted: the roadmap's critical-point conditions and the general-position handling — Canny 1988
   ch.3.)

**Removing a hypothesis / misreading the result**: PSPACE-completeness is a property of a **problem
family**, not of an **instance**. The lower-bound construction of step 3 makes the free space out of
exponentially many **channels of width $2^{-\Theta(p(n))}$**. On a family of instances whose
clearance $\delta$ is bounded below by a constant, a grid of resolution $O(\delta)$ is already
complete, at cost $O((1/\delta)^n)$ — still exponential, but exponential **for reasons that have
nothing to do with the Turing-machine reduction**. So the common sentence "motion planning is
PSPACE-hard, therefore we use sampling" is logically empty. Sampling wins not because of a
complexity class but because **its expected cost is low on instances with large clearance**, and
quantifying that is the $\epsilon$-good / expansiveness material of `c6-sampling-completeness`.

Removing H1 (fixing the degrees of freedom) breaks step 2 of the lower bound, since the chain can no
longer be grown to length $p(n)$, and the polynomial upper bound of R4 applies instead. Removing H2
(transcendental functions, or non-constructive obstacles) breaks step 1 of the upper bound, where
semialgebraicity is used, so decidability itself is no longer guaranteed.

## Problem set

Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more. The solution policy is stated per item.

**P1 (derivation, ★★, R1)** Show that when $A(0)$ and $O$ are convex polygons, $O \oplus (-A(0))$ in
(1) is a convex polygon whose number of edges is the **sum** of theirs. Then show that if $A(0)$ is a
union of $k$ convex pieces and $O$ a union of $l$ convex pieces, $\mathcal{C}_{obs}$ is a union of
$kl$ convex pieces.
*Solution sketch*: the support function adds under Minkowski sums, $h_{X \oplus Y} = h_X + h_Y$,
which gives convexity and the edge count at once (sort normals by angle and merge). Unions
distribute: $\big(\bigcup_i X_i\big) \oplus Y = \bigcup_i (X_i \oplus Y)$.

**P2 (numerical, ★, R1·R2)** Planar 2R arm with $\ell_1 = \ell_2 = 1$, base at the origin, obstacle a
disc of radius $r = 0.3$ centred at $c = (0.6, 0)$. Considering **link 1 only**, determine
$\mathcal{C}_{obs}^{(1)}$ exactly and the fraction of the torus $[0,2\pi)^2$ it occupies.
*Answer*: the distance from the length-1 segment out of the origin to $c$ is
$|c|\,|\sin\theta_1| = 0.6|\sin\theta_1|$ when $\cos\theta_1 > 0$ (the projection
$0.6\cos\theta_1 \in (0,0.6] \subset [0,1]$ is not clipped), and $|c| = 0.6 > r$ when
$\cos\theta_1 \le 0$ (the endpoint is nearest). So the collision condition is
$|\sin\theta_1| \le 1/2$ with $\cos\theta_1 > 0$, i.e.
$$\mathcal{C}_{obs}^{(1)} = \{\theta_1 : |\theta_1| \le \pi/6\} \times S^1,$$
a fraction of exactly $\dfrac{(\pi/3)(2\pi)}{4\pi^2} = \dfrac{1}{6} = 0.1666667$.
Check: an $N \times N$ grid count must land within $2/N$ of this value (at $N = 2048$ it gives
$0.1665039$, an error of $1.6\times10^{-4} < 2/N \approx 9.8\times10^{-4}$).

**P3 (proof, ★★, R1·R2)** Prove that for the planar 2R arm, if
$\mathcal{C}_{obs}^{(1)} \ne \emptyset$ and $\ne T^2$, then every connected component of
$\mathcal{C}_{obs}^{(1)}$ is non-contractible in the torus. Then decide whether this alone implies
$b_1(\mathcal{C}_{free}) \le 1$.
*Strategy and key inequality*: a component has the form $J \times S^1$ with $J \subset S^1$ an arc,
hence contains $\{ \ast \} \times S^1$. That circle maps to the generator $(0,1)$ of
$\pi_1(T^2) = \mathbb{Z}^2$ and is therefore non-trivial. The answer to the second question is
**no** — building the counterexample is left to P5.

**P4 (proof, ★★★, R3)** Prove that if a roadmap $\mathcal{R}$ satisfying conditions (a) and (b) of
step 3 of the upper bound exists, then the connectivity question is **equivalent** to graph
connectivity on $\mathcal{R}$. Then state concretely what kind of wrong answer becomes possible if
(b) is dropped.
*Strategy*: one direction is immediate from $\mathcal{R} \subset \mathcal{C}_{free}$. For the other,
use (a) to pick intersection points of $\mathcal{R}$ with the components containing $q_s$ and $q_g$,
and connectedness of the component to reach them. (b) is what guarantees that those intersection
points are joined **inside** $\mathcal{R}$. Without (b) two points of the same component can be
disconnected in $\mathcal{R}$, producing a **false negative**.

**P5 (counterexample, ★★, R2·R3)** Construct two things. (i) A 2R instance with
$\mathcal{C}_{obs}^{(1)} \ne \emptyset$ but $b_1(\mathcal{C}_{free}) \ge 2$. (ii) Using the fact that
the channels of the PSPACE-hardness reduction shrink to width $2^{-\Theta(n)}$ as $n$ grows, exhibit
a family of instances that belongs to a PSPACE-hard problem family and yet is solved for every
instance in under a second by grid search at resolution $10^{-2}$.
*Property checklist*: (i) uses one band plus one blob that the band does not touch (the band kills
one generator, the blob adds one — check with $\chi$). (ii) keeps the degrees of freedom as part of
the input but bounds the clearance $\delta$ below by a constant, and invokes completeness of a grid
of resolution $\delta/2$.

**P6 (implementation, ★★, R1·R2)** Write the grid C-space calculator of the reproduction task.
Requirements: torus indices modulo $N$, 4-neighbour components (seam stitched with union–find),
$\chi = V - E + F$.
*Rubric*: (a) the $(b_0, \chi, b_1)$ of the four instances match the table in the text; (b) doubling
$N$ leaves $(b_0, \chi)$ unchanged; (c) you check whether switching to 8-neighbour connectivity
changes the answer and, if so, report at which pixel the tangency arises; (d) you show numerically
how $b_0$ goes wrong if the seam handling is removed.

**P7 (paper, ★★, R3)** Read Reif 1979 and Hopcroft–Schwartz–Sharir 1984 and state exactly what each
reduction takes to be part of the input (degrees of freedom? number of bodies? coordinate
precision?). Then evaluate the claim "if an arm's degrees of freedom are fixed at 7, neither result
says anything about that robot."
*Rubric*: pass if you identify that the input size includes the degrees of freedom (or body count)
and that for fixed $n$ the polynomial bound of R4 applies. Writing only "hard / easy" fails.
Noting additionally that the coordinate bit-precision enters the input size is excellent.

## Paper reading

**Two must-reads.** Write a one-page note on each, using the ten fixed questions below
(`lesson-standard.md` §5). Read with Keshav's three passes and attack questions 4, 5, 6 and 7 on the
third pass.

1. **Reif, "Complexity of the mover's problem and generalizations" (1979, FOCS)** — role:
   `seminal`. <https://doi.org/10.1109/SFCS.1979.10> (§2–4)
   *Why read it*: it is the only primary source for the lower bound of R3. The figures of §3–4, where
   the channel geometry enforces the transition rules, are the whole idea of "free space =
   configuration graph".
   Extra questions: (a) exactly where are three dimensions needed (point at the step that breaks in
   two)? (b) estimate the minimum clearance $\delta$ of the free space the reduction builds, as a
   function of $n$. (c) what does this result say about the **upper** bound (and if nothing, why)?
2. **Canny, "The Complexity of Robot Motion Planning" (1988, MIT Press)** — role: `seminal`.
   <https://openlibrary.org/works/OL4626080W> (ch.1 and ch.3)
   *Why read it*: the upper bound of R3 and the singly exponential bound of R4 come from here. ch.1
   sets up the problem, ch.3 constructs the roadmap.
   Extra questions: (a) which of the author's theorems corresponds to conditions (a) and (b) of the
   roadmap, and where is general position used? (b) at which step does the $n^4$ of $d^{O(n^4)}$
   arise? (c) can you locate, in the author's own assumptions, the reason this algorithm has never
   been implemented as a general-purpose planner?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation or one figure. (4) what is guaranteed theoretically,
and **what is not**? (5) the independent and dependent variables and the baselines, and were the
baselines tuned fairly? (6) does the metric match the claim, and are variance and seeds reported?
(7) what is missing for reproduction? (8) if the result were wrong, which assumption would you doubt
first? (9) computational and memory complexity, and real-time feasibility. (10) what would you
change to go beyond this paper in a year?

> Both papers here are **theory papers**, so read questions 5 and 6 as being about "the components of
> the proof and their validity" rather than experiments: which lemma carries the weight of the proof,
> and do its assumptions hold on a robot?

## Reproduction task

**Tier R1 (numerical check).** Budget: one laptop CPU core, under 2 minutes in total, under 1 GB of
memory. numpy plus scipy (`ndimage.label`) only. No external data is needed.

**Input data (given by the lesson).** Planar 2R arm with $\ell_1 = \ell_2 = 1$, base at the origin,
links modelled as zero-thickness segments. The obstacles are discs, and the four instances are:

| Instance | discs $(c, r)$ |
|---|---|
| A | $((1.5, 0), 0.2)$ |
| B | $((1.3, 0), 0.35)$ |
| C | $((1.5, 0), 0.2)$ and $((0, 1.5), 0.2)$ |
| D | $((0.6, 0), 0.3)$ |

Take the $N \times N$ grid at $\theta_k = 2\pi j / N$, $j = 0, \dots, N-1$, and evaluate pixel
$(i,j)$ at $(\theta_1, \theta_2) = (2\pi i/N, 2\pi j/N)$. Decide segment–disc collision by the
distance to the nearest point **on the segment** (including the clipping).

**Acceptance criteria — all four must hold.**

1. **Topology**: at $N = 512$, $(b_0, \chi, b_1)$ equals **exactly** A $=(1,-1,2)$, B $=(1,0,1)$,
   C $=(1,-2,3)$, D $=(1,0,1)$, with $b_1$ computed from (4).
2. **Grid stability**: for $N \in \{256, 512, 1024\}$, $(b_0, \chi)$ is unchanged on all four
   instances.
3. **Area convergence**: the area fraction of $\mathcal{C}_{obs}$ satisfies
   $|A_{1024} - A_{512}| / A_{512} < 10^{-2}$ and, at $N = 1024$, lies in A $= 0.0257 \pm 0.0005$,
   B $= 0.1065 \pm 0.002$, C $= 0.0513 \pm 0.001$, D $= 0.2104 \pm 0.002$.
4. **Against the closed form (baseline)**: on instance D, the area fraction of the **link-1-only**
   obstacle agrees with $1/6$ to within $2/N$ (P2), and on instance A the link-1-only area is
   **exactly 0**.

**Baselines.** (a) The closed form $1/6$ of criterion 4. (b) An independent implementation: compute
the same grid a second time with `shapely` or with your own point–segment distance and check that the
number of disagreeing pixels is at most $10^{-4} N^2$. (c) Path validation: for 1000 random pairs of
configurations in the same component, extract a grid path, resample it at resolution $10^{-3}$ and
confirm zero workspace collisions.

**Failure table**

| Symptom | Cause | How to check |
|---|---|---|
| $b_0$ comes out $\ge 2$ | the torus seam ($j = 0$ with $j = N-1$) was not stitched | turn the seam union–find off and on and see whether $b_0$ changes |
| $\chi$ fluctuates with $N$ | edges or vertices double-counted in the cell count | run on an obstacle-free grid and check that $\chi = 0$ (as for $T^2$) |
| instance D gives $\chi = -1$ | link-1 collisions were omitted (only link 2 tested) | plot the per-link $\mathcal{C}_{obs}$ and look for the band |
| the area barely responds to $r$ | the clipping at the nearest point was omitted, so the distance to the **line** is used | check whether a collision is reported at $\theta_1 = \pi$ (away from the obstacle) |
| path validation reports collisions | only pixel centres are tested, so the space **between** pixels is skipped | double the resolution and see whether the collision count falls — if it does, it is a discretization issue |

## Open problems

- **(open problem) Complexity parameterized by clearance** — PSPACE-completeness does not predict
  the difficulty of an instance (the failure mode of R3), and the parameters that do explain planner
  cost are clearance and expansiveness. But those can only be estimated **after the fact** (you must
  already know the space to know its $\epsilon$), and there is no theory predicting cost from
  quantities measurable on a robot instance. Current approaches: expansiveness in
  [Hsu, Latombe & Motwani 1999](https://doi.org/10.1142/S0218195999000285), the improved bound of
  [Kleinbort et al. 2019](https://doi.org/10.1109/LRA.2018.2888947). What is missing: a difficulty
  measure computable directly from the input.
- **(open problem) Making exact algebraic planning practical** — Canny's singly exponential roadmap
  has had no general-purpose implementation since 1988. The barriers are degeneracy handling
  (removing the general-position assumption) and the constant in $d^{O(n^4)}$. Current approaches:
  per-piece guarantees on analytic pieces in
  [Vega-Brown & Roy 2020](https://doi.org/10.1007/978-3-030-43089-4_34), global optimality through
  convex decomposition in [Marcucci et al. 2023](https://arxiv.org/abs/2205.04422). What is missing:
  a complete and exact planner for 6 degrees of freedom with curved obstacles.
- **(open problem) Configuration space on a constraint manifold** — for closed chains, dual-arm
  manipulation and contact-maintaining tasks, $\mathcal{C}_{free}$ is not an open set but a
  **stratified set of lower-dimensional manifolds glued together**, and the "open set" argument of
  R1(a) does not even apply. The completeness and complexity theory for that case is unsettled.
  Current approach: the survey of
  [Kingston, Moll & Kavraki 2018](https://doi.org/10.1146/annurev-control-060117-105226). What is
  missing: the right definition of "completeness" on a stratified space.

## Concept check

Run `rc quiz c6-cspace-complexity`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: why openness of $\mathcal{C}_{free}$ matters; why an obstacle reachable by the
first link forces a band wrapping the torus; counting $b_1$ from $b_0$ and $\chi$; what
PSPACE-completeness does and does not say; and the Minkowski-sum form of $\mathcal{C}_{obs}$ for a
translating body.

## How to study this stage

1. **Fix the problem statement in one line (20 min)** — write down "motion planning = connectivity
   of $\mathcal{C}_{free}$" and copy the three assumptions (A1)(A2)(A3) onto paper. The next six
   lessons break them one at a time; tabulating now which lesson breaks which gives you the map of
   the whole module.
2. **Derive R1 by hand (50 min)** — reconstruct the three-line limit argument of (a), the three-line
   set identity of (b) and the cylinder structure of (c) from a blank page. In (c), do not stop until
   you see that the single line "a function of the first $i$ coordinates only" explains the entire
   topology table of the reproduction task.
3. **Count the topology before believing it (60 min)** — **implement the four instances first** and
   count $\chi$ and $b_0$. Once the numbers of the table come out, reread (3) and (4). Reversing the
   order traps you into "studying homology" — all you need is $V - E + F$.
4. **Read the two directions of the complexity result apart (70 min)** — read the lower bound (Reif
   §3–4) and the upper bound (Canny ch.3) **on different days**. Summarize each in one line ("design
   the free space as a graph" / "turn connectivity into algebra"), then rewrite the failure-mode
   paragraph of R3 in your own words. Once you can write that paragraph, complexity arguments in
   later modules will not sway you.
5. **Two paper notes (120 min)** — the ten fixed questions plus the per-paper extras. These are
   theory papers, so read questions 5 and 6 as "the lemma that carries the proof and its
   assumptions". Skip the notes and you will reread the decidability discussion from scratch in
   `c6-tamp`.
6. **Problem set (100 min)** — P2 (numerical) and P6 (implementation) first, then P1 and P3
   (derivation and proof), then P4, P5 and P7 if time allows. If you can write P5 (ii), the lesson
   has done its job.

**Passing bar**: you can derive (1) and (2) from a blank page, you have code reproducing
$(b_0, \chi, b_1)$ on the four instances, you can write a paragraph each on the lower and upper
bounds of PSPACE-completeness, and you can explain why "it is PSPACE-hard, therefore we sample" is
logically empty. You have notes on both papers.
