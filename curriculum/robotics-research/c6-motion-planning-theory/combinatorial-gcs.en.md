---
id: c6-combinatorial-gcs
lang: en
title: Combinatorial planning and convex decomposition
summary: >-
  The combinatorial approach: cut the free space into finitely many convex cells and reduce planning
  to graph search. Prove the completeness of cell decomposition, derive the optimality of the
  visibility graph from the fact that a shortest path in a polygonal environment turns only at
  obstacle vertices, and then lift the same idea to continuous optimization through the perspective
  relaxation of a graph of convex sets (GCS). The reproduction task confirms that the visibility
  graph solution is never longer than any of 500 sampled solutions.
objectives:
  - Build a vertical cell decomposition with its adjacency graph and prove "a path exists iff a graph path exists".
  - Derive that a shortest path in a polygonal free space is a polyline turning only at convex obstacle vertices.
  - Show that the visibility graph contains a shortest path, and state the cost of building and searching it.
  - Write the shortest-path problem on a graph of convex sets as a mixed-integer convex program and derive its perspective relaxation.
  - Explain why the relaxation is a lower bound and why the gap need not be zero.
tags: [motion-planning, combinatorial-planning, visibility-graph, convex-optimization, gcs, research]
---

# Combinatorial planning and convex decomposition

## Setup and notation

The results of `c6-cspace-complexity` are assumed. In particular, by its R1(b) a **translating
robot is equivalent to a point robot among inflated obstacles**, so this lesson assumes a **point
robot** throughout. Also assumed:

- Convex analysis: convex sets and functions, support functions, convexity of a norm, the shape of
  a second-order cone program (SOCP), Lagrangian duality and weak duality (recommended
  prerequisite `r0-convex-optimization`).
- Graph algorithms: correctness of Dijkstra and its $O(E + V\log V)$ cost.
- Only the **vocabulary** of mixed-integer programming: binary variables, relaxation, integrality
  gap. The internals of branch and bound are not needed.

Notation (in addition to the module's):

| Symbol | Meaning |
|---|---|
| $\mathcal{C}_{free} \subset \mathbb{R}^d$ | free space of a point robot; here assumed to have polygonal (polyhedral) boundary |
| $\mathcal{K} = \{K_1, \dots, K_M\}$ | a cell decomposition: $\bigcup_i \overline{K_i} = \overline{\mathcal{C}_{free}}$, interiors disjoint |
| $G_{\mathcal{K}} = (\mathcal{K}, E)$ | adjacency graph; $(K_i, K_j) \in E \iff \overline{K_i} \cap \overline{K_j}$ is $(d-1)$-dimensional |
| $V_{obs}$ | the obstacle vertices, $|V_{obs}| = V$ |
| $G_{vis}$ | visibility graph on $\{q_s, q_g\} \cup V_{obs}$, with an edge per mutually visible pair |
| $\ell(\sigma)$ | path length $\int_0^1 \lVert \dot\sigma \rVert \, dt$ (total variation for paths of bounded variation) |
| $L^\ast$ | shortest path length $\inf_\sigma \ell(\sigma)$ |
| $X_v \subset \mathbb{R}^d$ | the **convex** set attached to vertex $v$ of a GCS |
| $y_{uv} \in \{0,1\}$ | indicator for using edge $(u,v)$ |
| $\tilde f(x, y)$ | the perspective of a convex $f$: $y f(x/y)$ for $y > 0$ |

One more assumption, stated explicitly: **(A4) polygonal** — the boundary of $\mathcal{C}_{free}$
consists of finitely many segments (polygonal faces in 3D). This is what gives "finitely many cells"
and "finitely many vertices", and hence makes the problem **combinatorial**. With curved obstacles
the number of cells is still finite but the cell boundaries become algebraic curves, which pushes
the cost up to the algebraic algorithms of `c6-cspace-complexity` R4.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof).

- **R1 (completeness of cell decomposition) [D3]** — if $\mathcal{K}$ decomposes
  $\mathcal{C}_{free}$, each $K_i$ is **connected**, and the shared boundary of two adjacent cells is
  a $(d-1)$-dimensional **connected** piece, then
  $$\exists\,\sigma : q_s \rightsquigarrow q_g \text{ in } \mathcal{C}_{free}
    \iff \exists\,\text{path } K_{i_0} \to \cdots \to K_{i_k} \text{ in } G_{\mathcal{K}},$$
  with $q_s \in K_{i_0}$, $q_g \in K_{i_k}$. That is, **cell decomposition plus graph search is
  complete.**
- **R2 (optimality of the visibility graph) [D2]** — under (A4) a shortest path **exists**, it is a
  polyline of finitely many segments, and **every interior turn is at a convex obstacle vertex**.
  Hence
  $$L^\ast = \text{(shortest path length in } G_{vis}) \tag{1}$$
  computed exactly by Dijkstra. The cost is $O(V^2 \log V)$ to build the graph ($O(V^2)$ with a
  rotational sweep) plus $O(V^2)$ to search it.
- **R3 (mixed-integer convex formulation of GCS shortest paths and its perspective relaxation)
  [D2]** — on a graph whose vertices carry convex sets $X_v$, the problem "pick a point
  $x_v \in X_v$ at each vertex and minimize the sum of edge lengths" is
  $$
  \min \sum_{(u,v) \in E} \lVert z_{uv} - z_{vu} \rVert
  \quad\text{s.t.}\quad z_{uv} \in y_{uv} X_u,\;\; z_{vu} \in y_{uv} X_v,\;\;
    y \in \{0,1\}^{|E|},\;\; y \in \mathcal{F} \tag{2}
  $$
  with $\mathcal{F}$ the $q_s \to q_g$ flow constraints. Relaxing $y \in \{0,1\}$ to
  $y \in [0,1]$ gives a **convex** (SOCP) problem whose optimum is a **lower bound** on $L^\ast$. The
  gap is not zero in general — SPP-GCS is NP-hard.
- **R4 (the dimensional barrier of combinatorial planning) [D1]** — in the plane, shortest paths
  are polynomial time, but the Euclidean shortest path among polyhedral obstacles in three
  dimensions is NP-hard ([Canny & Reif 1987](https://doi.org/10.1109/SFCS.1987.42)). The number of
  cells in a decomposition also blows up as $O(V^d)$. **The reason combinatorial approaches stay in
  low dimension is this, not implementation difficulty.**

## Derivation

### R2 — optimality of the visibility graph

Three steps: existence, polyline structure, location of the turns.

**(i) A shortest path exists.** The closure of $\mathcal{C}_{free}$ is compact (bounded
workspace); suppose some path has length $L_0 = \ell(\sigma_0) < \infty$ (otherwise $q_s$ and $q_g$
are in different components and the problem is infeasible). Parameterized by arc length, the paths of
length $\le L_0$ form a family of functions with Lipschitz constant $L_0$, so by Arzelà–Ascoli they
have a uniformly convergent subsequence, and since length is lower semicontinuous the limit attains
the infimum. The limit stays in $\overline{\mathcal{C}_{free}}$ because every term does.

> **The subtle point about open versus closed.** $\mathcal{C}_{free}$ is open (R1(a) of the previous
> lesson), so a shortest path is usually **not attained inside** $\mathcal{C}_{free}$ — it turns by
> **grazing** the obstacles. So $L^\ast$ is defined as the minimum over
> $\overline{\mathcal{C}_{free}}$, and in practice one adds a margin $\rho > 0$ to the robot radius
> (inflating the obstacles by $\rho$) and re-solves. Omit that line and you get bug reports saying
> "the optimal path scrapes the obstacle".

**(ii) A shortest path is a polyline.** Let $\sigma$ be shortest and let $t_0$ be a time at which
$\sigma(t_0)$ does **not** touch an obstacle boundary. Since $\mathcal{C}_{free}$ is open there is a
ball $B(\sigma(t_0), r) \subset \mathcal{C}_{free}$ with $r > 0$. Pick times $t_1 < t_0 < t_2$ at
which $\sigma$ enters and leaves the ball; the **segment** joining those two points lies in the ball
and is therefore free. The triangle inequality gives

$$
\lVert \sigma(t_2) - \sigma(t_1) \rVert \;\le\; \ell\big(\sigma|_{[t_1,t_2]}\big),
$$

with equality only if $\sigma|_{[t_1,t_2]}$ is that segment. As $\sigma$ is shortest, equality must
hold, so $\sigma$ is **straight in a neighbourhood of every point that does not touch an obstacle**.
The touching points lie on finitely many segments by (A4), and (iii) below leaves only vertices among
them. Hence $\sigma$ is a concatenation of finitely many segments.

**(iii) Turns occur only at convex vertices.** Suppose $\sigma$ turns at a point $p$ (incoming
direction $u^-$, outgoing $u^+$, $u^- \ne u^+$). By (ii), $p$ is on an obstacle boundary. Two cases.

- **$p$ in the relative interior of an edge**: near that edge the obstacle is a half-plane $H$ with
  $p \in \partial H$. The path arrives through the free half-plane and leaves into it, so the turning
  angle measured on the free side satisfies $\angle(u^-, u^+) < \pi$. Then taking a point $a$ before
  and $b$ after $p$ in a small ball, the segment $\overline{ab}$ lies on the side where the angle is
  less than $\pi$, i.e. the **free** side, and
  $\lVert b - a \rVert < \lVert p - a \rVert + \lVert b - p \rVert$ is shorter. Contradiction with
  optimality; so turns cannot occur in the interior of an edge.
- **$p$ an obstacle vertex**: the same argument fails at a **reflex** vertex (interior angle on the
  free side greater than $\pi$), because $\overline{ab}$ would enter the obstacle. If the obstacle is
  convex then all of its vertices are reflex as seen from the free space, so the only points where a
  turn can occur are **convex obstacle vertices**.

By (ii) and (iii) the vertex sequence of a shortest path is a subsequence of
$\{q_s\} \cup V_{obs} \cup \{q_g\}$, and consecutive points must see each other, i.e. they are edges
of $G_{vis}$. Hence (1), and Dijkstra is exact.

**Where the assumption breaks**: drop (A4) — disc obstacles — and a shortest path becomes an
alternating sequence of **arcs and tangent lines**, whose turning points are not a finite set (the
tangency point moves continuously). The visibility graph becomes a tangent graph and the
combinatorial property "finitely many vertices" is gone. In three dimensions (iii) breaks more
severely: a shortest path can cross the **interior of an edge**, and that crossing point is a
continuous variable. So the 3D shortest path is not a combinatorial problem, which is where the
NP-hardness of R4 comes from.

### R3 — GCS: the perspective reformulation

**The problem.** A graph $G = (\mathcal{V}, E)$, a convex set $X_v \subset \mathbb{R}^d$ at each
vertex, a source $s$ and a target $t$. Choose a path $v_0 = s, \dots, v_k = t$ and points
$x_{v_i} \in X_{v_i}$ minimizing $\sum_i \lVert x_{v_{i+1}} - x_{v_i} \rVert$. **Why this is motion
planning**: cover the free space with convex regions (via IRIS or similar), make each region a
vertex and each overlapping pair an edge, and the formulation solves "which regions, in what order"
(combinatorial) and "which point inside each region" (continuous) **as one problem** — in contrast
with cell decomposition (R1), which handles only the combinatorics, and trajectory optimization,
which handles only the continuum.

**The naive formulation and what is wrong with it.** With binaries $y_{uv}$,

$$
\min \sum_{(u,v)\in E} y_{uv} \lVert x_u - x_v \rVert, \qquad x_v \in X_v,\;\; y \in \mathcal{F}
$$

puts a **binary × convex** product $y \cdot \lVert x_u - x_v\rVert$ in the objective. Relaxing
$y \in [0,1]$ makes that term **non-convex** (bilinear), and the usual workaround, big-M,

$$
c_{uv} \ge \lVert x_u - x_v \rVert - M(1 - y_{uv}),
$$

is convex but constrains $x_u, x_v$ not at all when $y_{uv} = 0$, so the relaxation is **very
loose** (the relaxed solution turns many edges on a little and absorbs the cost into $M$).

**The road to the perspective.** The key is to **fold the variables of a switched-off edge to zero**.
Define the perspective of a convex $f : \mathbb{R}^n \to \mathbb{R}$ as

$$
\tilde f(x, y) = \begin{cases} y\, f(x/y), & y > 0 \\ 0, & y = 0,\ x = 0 \\ +\infty, & \text{otherwise}\end{cases}
  \tag{3}
$$

Then $\tilde f$ is **convex** in $(x,y)$. Derivation: $\mathrm{epi}\,f$ is convex and
$\mathrm{epi}\,\tilde f = \mathrm{cl}\{(x, y, s) : y > 0,\ (x/y, s/y) \in \mathrm{epi}\, f\}$ is the
closure of $\mathrm{epi}\,f$ **stretched into a cone with apex at the origin**, hence convex.
Moreover $\tilde f$ is the **convex hull** of the set
$\{(x,0,0)\} \cup \{(x,1,s) : s \ge f(x)\}$ obtained by restricting $y \in \{0,1\}$ — i.e. the
relaxation that **cannot be tightened**. That is the whole difference from big-M.

**Deriving (2).** The function $f(\cdot) = \lVert \cdot \rVert$ is **1-homogeneous**, which makes its
perspective especially simple. Substituting $z_{uv} = y_{uv} x_u$ and $z_{vu} = y_{uv} x_v$,

$$
y_{uv}\lVert x_u - x_v \rVert = \lVert y_{uv}x_u - y_{uv}x_v \rVert = \lVert z_{uv} - z_{vu} \rVert,
  \tag{4}
$$

so **the product disappears and the objective is simply a norm**. The set constraint
$x_u \in X_u$ becomes

$$
z_{uv} \in y_{uv} X_u \;:=\; \{y_{uv} x : x \in X_u\},
$$

which for $X_u = \{x : A_u x \le b_u\}$ reads $A_u z_{uv} \le b_u\, y_{uv}$ — **linear** (for a
general convex $X_u$ it is the perspective of its indicator, i.e. the homogenization cone of $X_u$).
The flow constraints $\mathcal{F}$ are linear in $y$ (inflow = outflow at each vertex, $+1$ at $s$,
$-1$ at $t$, $0 \le y \le 1$). This gives (2), and dropping only the integrality of $y$ leaves an
SOCP.

**Why it is a lower bound.** For any integer feasible $(x, y)$, the point $z = y x$ is feasible for
the relaxation with the same objective value by (4). So the relaxed optimum is $\le L^\ast$ — this
comes directly from **containment of feasible sets**, not from weak duality. And rounding a relaxed
solution by looking only at the edges with $y_{uv} > 0$ and recovering $x_u = z_{uv}/y_{uv}$ gives an
upper bound, so **a single convex solve yields the interval
$[\text{relaxed value}, \text{rounded value}]$, i.e. a certificate of sub-optimality.** Neither
combinatorial methods nor pure trajectory optimization has that property.

**Where the assumption breaks**: there is **no** guarantee that the gap is zero. SPP-GCS is NP-hard
in general (it specializes to Hamiltonian path), and the constraint forbidding revisits to a vertex
cannot be expressed by flow alone, so a relaxed solution can **push flow around a cycle**. The
authors' claim is not "always tight" but "the gap is very small on practical instances", and
establishing exactly what the paper's theorem does claim is the task of must-read 3 (problem P7).
Where the $X_v$ come from is also outside this formulation — covering the free space with convex
regions is itself a non-convex problem
([Deits & Tedrake 2015](https://doi.org/10.1007/978-3-319-16595-0_7)) and, if the cover misses part
of the free space, **completeness is lost as well**.

### R4 — the dimensional barrier [D1]

1. In the plane: the visibility graph has $O(V^2)$ edges and Dijkstra is polynomial, so shortest
   paths are polynomial time. A trapezoidal decomposition takes $O(V \log V)$ by sweep and has
   $O(V)$ cells.
2. In three dimensions the argument of R2(iii) breaks, a shortest path crosses the interior of an
   edge and the crossing point becomes a continuous variable. The combinatorial structure of the
   optimum ("which edges, in what order") is exponentially large.
3. From this, Canny & Reif 1987 obtain **NP-hardness** of the 3D Euclidean shortest path problem.
   $(1+\epsilon)$-approximation algorithms exist in polynomial time but with large constants.
4. Cell decomposition hits the same wall: in $d$ dimensions the arrangement of $V$ hyperplanes has
   $\Theta(V^d)$ cells. **So complete combinatorial planning is a tool for $d \le 3$**, and above
   that one goes to the sampling of `c6-sampling-completeness` or to the convex covers of R3.

## Proof sketch

### R1 — completeness of cell decomposition

**Hypotheses** H1: $\mathcal{K}$ is a finite decomposition and each $K_i$ is **connected** (convex
suffices). H2: adjacency is defined by $\overline{K_i} \cap \overline{K_j}$ being a
$(d-1)$-dimensional **connected** piece. H3:
$\overline{\mathcal{C}_{free}} = \bigcup_i \overline{K_i}$ with disjoint interiors.
**Conclusion** C: a path $q_s \rightsquigarrow q_g$ exists in $\mathcal{C}_{free}$ $\iff$ a path
$K_{i_0} \rightsquigarrow K_{i_k}$ exists in $G_{\mathcal{K}}$.

**Strategy**: construct in both directions. ($\Leftarrow$) **builds** a path using connectedness
inside cells and the shared boundaries. ($\Rightarrow$) **cuts** a path into cells and reads off the
graph path.

1. **($\Leftarrow$) graph path → path.** Along the graph path $K_{i_0} \to \cdots \to K_{i_k}$, pick a
   point $p_j \in \overline{K_{i_j}} \cap \overline{K_{i_{j+1}}}$ on each shared boundary. By H1 there
   is a path $p_{j-1} \rightsquigarrow p_j$ inside $K_{i_j}$ (a segment if the cell is convex), and
   concatenating gives $q_s \rightsquigarrow q_g$. (Here **$p_j$ must be free** — the decomposition
   must be chosen so that shared boundaries do not coincide with obstacle boundaries. An
   implementation that omits this condition produces paths that go through walls.)
2. **($\Rightarrow$) path → graph path.** Let $\sigma$ be a free path and let $\tau_j$ be the times at
   which it changes cell. By H3, $\sigma(t)$ always lies in some $\overline{K_i}$, and since $\sigma$
   is continuous and the cells are finite, the set of change times can be taken finite (general
   position: if needed, perturb $\sigma$ by $\epsilon$ to avoid $(d-2)$-dimensional intersections.
   Omitted: the perturbation lemma — [LaValle PA](http://lavalle.pl/planning/) 6.3.2).
3. At each transition time, $\sigma(\tau_j)$ lies on a shared boundary which is $(d-1)$-dimensional by
   H2, so that pair is an edge of $G_{\mathcal{K}}$. Reading off the sequence of transitions gives the
   graph path.
4. Both directions hold, giving C. **Finiteness** (H1) gives termination of the algorithm;
   **connectedness of the shared boundary** (H2) makes the concatenation in step 1 work.

**Removing a hypothesis**: drop "connected" from H1 and step 1 collapses — if two points of a cell
are not joined inside the cell, a graph path does not yield a real path and you get a **false
positive**. Drop the "$(d-1)$-dimensional" from H2 and call cells adjacent when they share a single
vertex, and in the plane two cells touching only diagonally, as on a chessboard, become adjacent,
producing a path **through a point that cannot be crossed**. This is the **same error** as the
"4-neighbour versus 8-neighbour" issue in the reproduction task of `c6-cspace-complexity`. Drop
"connected" from H2 and, when a shared boundary splits into two pieces, the choice of $p_j$ in step 1
can land on the other piece and the concatenation breaks.

## Problem set

Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R2)** Rewrite "no turn in the interior of an edge" from R2(iii) in
coordinates. Take the obstacle to be $H = \{(x,y) : y \le 0\}$, $p = (0,0)$, and $u^\pm$ unit vectors
entering and leaving on the free side $y > 0$; with $a = p - \epsilon u^-$ and $b = p + \epsilon u^+$,
express the condition $\lVert b - a \rVert < 2\epsilon$ in terms of the angle and show that
$\overline{ab}$ is free.
*Solution sketch*: reduce $\lVert b - a\rVert^2$ to the form
$2\epsilon^2(1 - \langle u^-, u^+\rangle)$ (watch the sign convention for $u^-$) and use that a
turning angle below $\pi$ makes the inner product strictly less than 1. Freeness follows because both
$a$ and $b$ have positive $y$ and the segment is a convex combination.

**P2 (derivation, ★★, R3)** Show **directly** that the perspective (3) is convex: for
$y_1, y_2 > 0$ and $\lambda \in [0,1]$, derive
$\tilde f(\lambda x_1 + (1-\lambda)x_2, \lambda y_1 + (1-\lambda)y_2) \le \lambda \tilde f(x_1,y_1) +
(1-\lambda)\tilde f(x_2,y_2)$ using only the convexity of $f$. Then check that a 1-homogeneous $f$
gives $\tilde f(x,y) = f(x)$, which is (4).
*Solution sketch*: set $\mu = \lambda y_1 / (\lambda y_1 + (1-\lambda)y_2)$, so the argument on the
left becomes $f(\mu \cdot x_1/y_1 + (1-\mu)\cdot x_2/y_2)$, and apply convexity of $f$. For a
1-homogeneous $f$, $y f(x/y) = f(x)$ is immediate from the definition.

**P3 (numerical, ★, R2)** For the environment of the reproduction task (below), find the **exact**
length of the visibility-graph shortest path in closed form.
*Answer*: the optimum is $(0.5, 0.5) \to (3, 1) \to (6, 3) \to (7, 6) \to (9.5, 9.5)$ with
$$L^\ast = \tfrac{1}{2}\big(\sqrt{26} + \sqrt{74}\big) + \sqrt{13} + \sqrt{10}
  = 13.618501325950\ldots$$
(the four legs are $\sqrt{6.5},\ \sqrt{13},\ \sqrt{10},\ \sqrt{18.5}$). Tolerance $10^{-9}$.
Check: the second-shortest homotopy class has length $13.650130399\ldots$, only 0.23% longer — so a
visibility test with a loose tolerance of order $10^{-3}$ will pick the wrong path. That proximity is
why this instance was chosen.

**P4 (proof, ★★, R1)** Show by **counterexample** why step 1 of R1 needs the condition that the
point $p_j$ on a shared boundary be free: construct a decomposition in which two cells share a
$(d-1)$-dimensional boundary that consists entirely of obstacle boundary, and state what false
conclusion R1 then yields.
*Strategy*: let the obstacle be a **zero-thickness wall** between two free regions (a degenerate
obstacle), so the decomposition has two cells sharing that wall. Numerically, the same phenomenon
appears for a wall of thickness $\epsilon \to 0$, i.e. an obstacle thinner than the grid resolution.

**P5 (proof, ★★★, R3)** Prove that the optimum of the relaxation (2) is a lower bound on $L^\ast$ by
**containment of feasible sets**, and construct a concrete graph on which the relaxed solution has an
edge with $y_{uv} \in (0,1)$ (three vertices with singleton sets will do). Compute the gap
numerically on that instance.
*Strategy*: the lower bound is the one line "$z = yx$ is relaxed-feasible". For the second part, try
the construction with **two parallel paths of equal length** where the flow splits in half — but
first verify that with a **linear** cost the gap is still zero (the shortest-path LP is tight). To
create a gap you need no-revisit constraints or a non-linear cost; pointing at exactly that is a
pass.

**P6 (implementation, ★★, R2)** Write the visibility graph of the reproduction task. Requirements: a
segment-versus-rectangle-interior test (Liang–Barsky clipping or separating axis), exclusion of
vertices outside the workspace, Dijkstra.
*Rubric*: (a) you get 10 vertices and 15 edges; (b) the length agrees with the closed form of P3 to
$10^{-9}$; (c) segments **grazing** a boundary (running along an obstacle edge) are classified as
free — 6 of the 15 edges lie on obstacle edges (the four edges of $R_1$, the bottom edge
$(5,3)\!-\!(6,3)$ of $R_2$, the top edge $(7,6)\!-\!(8,6)$ of $R_3$), so classifying them as
collisions disconnects the graph; (d) you report which path is chosen when the intersection tolerance
is changed to $10^{-3}$.

**P7 (paper, ★★, R3)** Find in Marcucci et al. 2024 the **exact statement** of the theorem about
tightness of the relaxation, transcribe it, and say how it differs from "the relaxation is always
tight". Then summarize what kind of instances (degrees of freedom, number of regions, cost terms) the
gaps and runtimes reported in Marcucci et al. 2023 refer to.
*Rubric*: pass if you identify that the theorem concerns a **specific structure** (or specific cost
terms) rather than a general guarantee, and why that does not contradict NP-hardness. Writing only
"tight / not tight" fails.

**P8 (counterexample, ★★, R2·R4)** Show by a concrete example that "the turning points of a shortest
path are always obstacle vertices" is false in three dimensions (one box obstacle and two points on
opposite sides). Characterize which point in the interior of the edge the turn occurs at, using a
variational condition of the "angle of incidence equals angle of reflection" kind.
*Property checklist*: unfold the two faces about the edge; the shortest path becomes straight, and the
crossing point before unfolding is determined by a **continuous parameter**. That continuous degree of
freedom is the structure behind the NP-hardness of R4.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions.

1. **Lozano-Pérez & Wesley, "An algorithm for planning collision-free paths among polyhedral
   obstacles" (1979, CACM)** — role: `seminal`. <https://doi.org/10.1145/359156.359164>
   *Why read it*: the visibility graph (VGRAPH) and C-space inflation are in the **same paper**. The
   point is to see R1(b) of the previous lesson and R2 of this one presented together in 1979.
   Extra questions: (a) how do the authors handle rotation (or not)? (b) does their algorithm claim
   optimality, or only feasibility?
2. **Marcucci, Petersen, von Wrangel & Tedrake, "Motion planning around obstacles with convex
   optimization" (2023, Science Robotics)** — role: `frontier`. <https://arxiv.org/abs/2205.04422>
   *Why read it*: how the formulation of R3 is used on real robot problems (a 7-DoF arm, dual arms),
   and what changes when the cost is time or curvature instead of length.
   Extra questions: (a) how were the regions $X_v$ produced, and how does their number affect
   solution quality? (b) were the sampling-based baselines tuned fairly (which planner, how many
   seeds, post-processing or not)?
3. **Marcucci, Umenberger, Parrilo & Tedrake, "Shortest Paths in Graphs of Convex Sets" (2024, SIAM
   J. Optim.)** — role: `standard`. <https://arxiv.org/abs/2101.11565>
   *Why read it*: the **exact statements and tightness results** for the perspective reformulation
   are here. This is the target of P7.
   Extra questions: (a) how do the flow constraints the authors use differ from $\mathcal{F}$ in (2)?
   (b) what do the valid inequalities added to shrink the gap exclude?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation or one figure. (4) what is guaranteed theoretically,
and **what is not**? (5) the independent and dependent variables and the baselines, and were the
baselines tuned fairly? (6) does the metric match the claim, and are variance and seeds reported?
(7) what is missing for reproduction? (8) if the result were wrong, which assumption would you doubt
first? (9) computational and memory complexity, and real-time feasibility. (10) what would you change
to go beyond this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 10 minutes for all 500 runs,
under 1 GB of memory. numpy only. No external data.

**Input data (given by the lesson).** Workspace $[0,10]^2$, a **point robot**, three axis-aligned
rectangular obstacles whose interiors are blocked (their boundaries are free).

| Obstacle | Extent |
|---|---|
| $R_1$ | $[2,3] \times [1,8]$ |
| $R_2$ | $[5,6] \times [3,10.5]$ |
| $R_3$ | $[7,8] \times [-0.5,6]$ |

$q_s = (0.5, 0.5)$, $q_g = (9.5, 9.5)$. ($R_2$ and $R_3$ stick out of the box so as to be attached to
a wall; vertices outside the workspace are excluded from the visibility graph.)

The sampling baseline is fixed to **RRT**: step $\eta = 0.5$, goal bias 5%, goal tolerance radius
0.25, at most 20000 iterations, seeds $0, \dots, 499$. Smoothing is 200 random shortcuts (draw a pair
of indices uniformly and cut between them if the two points see each other).

**Acceptance criteria — all four must hold.**

1. **Correctness**: the visibility graph has 10 vertices and 15 edges, the Dijkstra length agrees
   with $L^\ast = \tfrac12(\sqrt{26}+\sqrt{74}) + \sqrt{13} + \sqrt{10} = 13.618501325950$ to
   $10^{-9}$, and the path visits the four vertices of P3 in that order.
2. **Optimality (checking the theory)**: **all** 500 RRT path lengths are at least
   $L^\ast - 10^{-9}$ (zero violations), and still zero after smoothing. If R2 is true this must
   hold — **a single violation means a bug in the visibility test or in the length computation.**
3. **Quantitative comparison**: with the parameters above, the median of the ratio $\ell/L^\ast$
   falls in $1.25 \pm 0.10$ before smoothing and $1.05 \pm 0.03$ after (measured: 1.2457 and 1.0514).
   The minimum is $\ge 1.08$ before and $\ge 1.005$ after (measured: 1.0980 and 1.0105).
   *A different implementation may fall outside those windows for the median — what must hold is
   criterion 2 and the fact that smoothing decreases the ratio monotonically.*
4. **Tolerance sensitivity**: show that raising the intersection tolerance of the visibility test to
   $10^{-3}$ changes the chosen path or moves the length towards $13.65$ (the second homotopy class
   has length $13.650130399$). That is, confirm that **this instance really does test the
   tolerance**.

**Baselines.** (a) The closed form $L^\ast$ (criterion 1). (b) 500 RRT runs (criteria 2 and 3).
(c) An independent implementation: code the segment–rectangle intersection both by Liang–Barsky and by
a separating axis and confirm the visibility matrices agree exactly.

**Failure table**

| Symptom | Cause | How to check |
|---|---|---|
| the length is **shorter** than $L^\ast$ | a segment passing through an obstacle interior is classified free (clipping sign, or open/closed handling) | test separately whether the midpoint of each leg of the optimum is inside an obstacle |
| fewer than 15 edges | segments **running along** an obstacle edge are classified as collisions | feed in a boundary-hugging pair such as $(5,3) \to (6,3)$ (the bottom edge of $R_2$) by hand |
| 14 vertices | vertices outside the workspace ($y = 10.5$, $y = -0.5$) were not filtered | print the vertex list and count those outside $[0,10]^2$ |
| RRT returns a path shorter than $L^\ast$ | path length is being counted by tree depth, or smoothing uses a loose visibility test | resample that path at $10^{-4}$ and test it for collisions |
| the RRT failure rate is not zero | the goal tolerance or the iteration cap differs from the specified value, or samples near the boundary land inside an obstacle | look at the tree size of the failing seed and check whether it hit the iteration cap |

## Open problems

- **(open problem) Where do the convex covers come from** — the formulation of R3 assumes the $X_v$
  are given, but the problem of **covering the free space with few large convex regions** is itself
  non-convex and has no quality guarantee. If the cover misses part of the free space, completeness is
  lost as well. Current approaches:
  [Deits & Tedrake 2015](https://doi.org/10.1007/978-3-319-16595-0_7) (IRIS grows one locally large
  region with an SDP), the region-generation pipeline of
  [Marcucci et al. 2023](https://arxiv.org/abs/2205.04422). What is missing: a theory quantifying the
  trade-off between the number of regions and solution quality, and cover generation in high
  dimension.
- **(open problem) Structural characterization of the GCS gap** — no **structural** condition
  (graph shape, geometry of the sets, type of cost term) is known for when the relaxation is tight.
  Nor has it been separated whether the small gaps on practical instances are due to geometry or to
  the sparsity of the graph. Current approach: the valid inequalities and tightness results of
  [Marcucci et al. 2024](https://arxiv.org/abs/2101.11565). What is missing: a criterion that decides
  **in advance** that a given instance will be tight.
- **(open problem) Practical exact shortest paths in three dimensions** — because of the NP-hardness
  of R4, $(1+\epsilon)$-approximation is the standard, but the constants are too large for practice
  and robotics substitutes sampling plus smoothing. For domains that genuinely need an exact
  geometric shortest path (cable routing, contact paths) no usable algorithm exists. Current
  approaches: the lower bound of
  [Canny & Reif 1987](https://doi.org/10.1109/SFCS.1987.42) and the approximation algorithms that
  followed. What is missing: a method giving $10^{-6}$-level accuracy at practical scale.

## Concept check

Run `rc quiz c6-combinatorial-gcs`. Concept checking only; the real work is the problem set and the
reproduction task.

The five items cover: why a shortest path cannot turn in the relative interior of an obstacle edge;
why big-M is looser than the perspective formulation; what the GCS relaxation does and does not
guarantee; the three conditions that make cell decomposition complete; and the perspective of a
1-homogeneous function.

## How to study this stage

1. **Separate the combinatorial from the continuous on paper (20 min)** — tabulate the three methods
   of this lesson: cell decomposition (combinatorial only, completeness), visibility graph
   (combinatorial only, optimality), GCS (both, lower bound plus certificate). Columns: what it
   guarantees / what it assumes / its dimensional limit. That table is the skeleton of the lesson.
2. **Rewrite R2 as three pictures (60 min)** — (i) existence, (ii) straightness, (iii) turning points.
   Draw the half-plane picture of (iii) yourself and confirm by hand where the argument stops at a
   reflex vertex. Solve P1 alongside.
3. **Derive the perspective by hand (70 min)** — do P2 **first**. Writing out the convexity inequality
   makes (3) and (4) stick. Then compare with big-M and write the sentence "fold the switched-off
   edge's variables to zero" in your own words. Reversed order, reading the paper first, buries you in
   notation.
4. **Meet the tolerance through implementation (75 min)** — write the visibility graph of the
   reproduction task and **deliberately** break criterion 4 (tolerance sensitivity). Seeing directly
   that the second homotopy class is only 0.23% longer is what makes "tolerances in geometric
   algorithms" legible as a research topic of its own.
5. **Three papers (140 min)** — read them 1979 → 2023 → 2024. The 1979 paper fixes the problem
   statement, the 2023 one lifts it to robot scale, and the 2024 one fills in the theory. Write P7
   while reading the 2024 paper.
6. **Problem set (150 min)** — P3 and P6 first, then P1 and P2, then P4, P5, P7, P8 with whatever
   time remains. If you can write P8, you have understood the dimensional barrier of R4.

**Passing bar**: you can reconstruct the three steps of R2 from a blank page, you can derive the
perspective formulation (2) and (4), you have code satisfying the four criteria of the reproduction
task, and you can state the difference between "the relaxation gives a lower bound" and "the gap is
zero". You have notes on all three papers.
