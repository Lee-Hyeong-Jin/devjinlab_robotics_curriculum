---
id: s5-graph-consensus
lang: en
title: Graph theory and consensus
summary: >-
  Analyze the consensus dynamics that underlie multi-robot coordination through the spectrum of
  the graph Laplacian. Prove that the convergence rate of continuous-time consensus is exactly the
  algebraic connectivity lambda_2, and derive in closed form the optimal step size of
  discrete-time consensus and the rate it achieves. Show that on a directed graph the consensus
  value is not the average but a left-null-vector weighted average, that for time-varying graphs
  only joint connectivity matters, and confirm numerically that alternating graphs with
  lambda_2 = 0 still reaches consensus.
objectives:
  - Prove the convergence and the rate lambda_2 of continuous-time consensus from the Laplacian spectrum.
  - Derive the convergence condition, the optimal step size 2/(lambda_2+lambda_n) and its rate for discrete-time consensus.
  - Write the consensus value of a directed graph as a left null vector and show average consensus is equivalent to balancedness.
  - Explain why joint connectivity is close to a necessary and sufficient condition on time-varying graphs.
  - Locate a graph's bottleneck with the Fiedler vector and quantify the effect of adding an edge.
  - Measure the consensus rate numerically and match lambda_2 to within 1e-5.
tags: [multi-robot, consensus, graph-laplacian, algebraic-connectivity, distributed, research]
---

# Graph theory and consensus

## Setup and notation

This is the first lesson of module S5. The following is assumed:

- Linear algebra: spectral decomposition of symmetric matrices, positive semidefiniteness, the
  Rayleigh quotient, the matrix exponential (`f0-linear-algebra`).
- The information-matrix view of `c5-factor-graphs-map`. **The Laplacian is the information matrix
  of an estimation problem built only from relative measurements** — the gauge freedom of that
  lesson (null space = global constant) appears here as "the consensus value is not pinned to any
  one number". The two lessons are looking at the same matrix from different sides.
- Graph theory is not required; the definitions needed are collected below.

| Symbol | Meaning |
|---|---|
| $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ | a graph on $n = \lvert\mathcal{V}\rvert$ nodes. Nodes are robots, edges are communication links |
| $A$ | the adjacency matrix. Undirected means $A = A^\top$. **On a directed graph $A_{ij} = 1$ means "$i$ listens to $j$" ($j\to i$)** |
| $D$ | the degree matrix $\mathrm{diag}(A\mathbf{1})$; the **in-degree** on a directed graph |
| $L := D - A$ | the **Laplacian**; symmetric positive semidefinite when undirected |
| $0 = \lambda_1 \le \lambda_2 \le \cdots \le \lambda_n$ | the eigenvalues of $L$ (undirected). $\lambda_2$ is the **algebraic connectivity** |
| $f$ | the eigenvector of $\lambda_2$, the **Fiedler vector** |
| $\mathbf{1}$ | the all-ones vector. $L\mathbf{1} = 0$ always holds |
| $\delta := x - \bar x\mathbf{1}$ | the **disagreement** vector, with $\bar x = \frac1n\mathbf{1}^\top x$ |
| $P := I - \epsilon L$ | the **Perron matrix** of discrete-time consensus; $\epsilon$ is the step size |
| $w$ | on a directed graph, the **left null vector** with $w^\top L = 0$, $w^\top\mathbf{1} = 1$, $w \ge 0$ |

**The consensus dynamics.** The simplest rule in which each robot corrects its own value by the
difference from its neighbours is

$$
\dot x_i = \sum_{j \in \mathcal{N}_i} a_{ij}\,(x_j - x_i)
\qquad\Longleftrightarrow\qquad
\dot x = -L\,x \tag{1}
$$

with the discrete-time version $x_{k+1} = (I - \epsilon L)x_k = P x_k$. Equation (1) is a
**distributed** algorithm — each node sees only its own neighbours and uses no global information.
This lesson has one question: **when, to where, and how fast does it converge?**

## Self-diagnosis before starting

This is the first lesson of the module, so check your readiness first. **Prerequisite lessons are
not locked** — if you can solve all of the following, skip the recommended prerequisites
(`f0-linear-algebra` and modules C5, C6, C8) and start here. **If two or more stop you**, going
back to the prerequisite lesson named in parentheses is faster.

1. Write the Laplacian of the path graph $1 - 2 - 3$ and find its eigenvalues.
   (`f0-linear-algebra`)
   **Answer**: $L = \begin{bmatrix}1&-1&0\\-1&2&-1\\0&-1&1\end{bmatrix}$ with eigenvalues
   $\{0, 1, 3\}$. Tolerance $10^{-9}$.
2. For a symmetric $M$ with $M\mathbf{1} = 0$, what is
   $\min_{v \perp \mathbf{1},\, v\ne0} \dfrac{v^\top Mv}{v^\top v}$? (`f0-linear-algebra`)
   **Answer**: the smallest eigenvalue other than the one belonging to $\mathbf{1}$, that is
   $\lambda_2$ (Courant-Fischer / the Rayleigh quotient).
3. Write the solution of $\dot x = Mx$ with the matrix exponential, and express the decay rate of
   $\lVert x(t)\rVert$ through the eigenvalues when $M$ is symmetric.
   (`f0-differential-equations`, `f0-linear-algebra`)
   **Answer**: $x(t) = e^{Mt}x(0)$. If $M$ is symmetric with eigenvalues $\mu_i$ then
   $\lVert x(t)\rVert \le e^{\mu_{\max}t}\lVert x(0)\rVert$, and component-wise the decay is
   $e^{\mu_i t}$.
4. In `c5-factor-graphs-map`, what was the null space of the information matrix $\Lambda$ of a pose
   graph built only from relative measurements? And for a one-dimensional scalar variable?
   (`c5-factor-graphs-map`)
   **Answer**: a global rigid transform. For a one-dimensional scalar it is a global constant
   shift, that is $\ker\Lambda = \mathrm{span}(\mathbf{1})$ — exactly $\ker L$.
5. If every row of a matrix $P$ is non-negative and sums to one, what is $P\mathbf{1}$, and what is
   the spectral radius of such a matrix? (`f0-linear-algebra`)
   **Answer**: $P\mathbf{1} = \mathbf{1}$ (eigenvalue 1). A row-stochastic matrix has spectral
   radius 1, and $\lvert\lambda\rvert \le 1$ for every eigenvalue (by Gershgorin or a norm
   argument).

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (continuous-time consensus: convergence, the consensus value and the rate) [D3]** — on a
  connected undirected graph the solution of (1) satisfies
  $$
  x(t) \longrightarrow \bar x(0)\,\mathbf{1}, \qquad
  \lVert \delta(t)\rVert \le e^{-\lambda_2 t}\,\lVert \delta(0)\rVert, \tag{2}
  $$
  and this exponent is **exactly the best possible** (equality along the Fiedler vector). So **the
  convergence rate of consensus is $\lambda_2$.** The average $\bar x$ is preserved for all $t$.
  As measured in the reproduction task, the asymptotic rate matches $\lambda_2$ to a relative
  error of $10^{-6}$ to $10^{-5}$ on four graphs.
- **R2 (discrete-time consensus: the convergence condition and the optimal step size) [D2]** — for
  $P = I - \epsilon L$,
  $$
  \text{convergence} \iff 0 < \epsilon < \frac{2}{\lambda_n}, \qquad
  \text{rate} = \max\big(\lvert1-\epsilon\lambda_2\rvert,\ \lvert1-\epsilon\lambda_n\rvert\big), \tag{3}
  $$
  and the step size minimizing it, together with the rate achieved, is
  $$
  \epsilon^\ast = \frac{2}{\lambda_2 + \lambda_n}, \qquad
  r^\ast = \frac{\lambda_n - \lambda_2}{\lambda_n + \lambda_2} = \frac{\kappa - 1}{\kappa + 1},
  \quad \kappa := \frac{\lambda_n}{\lambda_2}. \tag{4}
  $$
  **What governs the rate is not $\lambda_2$ but the ratio $\kappa$** — a difference from
  continuous time, and one high-degree node raising $\lambda_n$ slows the whole network down. As
  measured: the grid-search optimum agrees with (4) to six or more digits.
- **R3 (on a directed graph the consensus value is not the average) [D2]** — on a directed graph
  $L$ is not symmetric; $L\mathbf{1} = 0$ still holds but $\mathbf{1}^\top L = 0$ generally does
  not. If a rooted out-branching exists, (1) converges and
  $$
  x(t) \longrightarrow (w^\top x(0))\,\mathbf{1}, \qquad w^\top L = 0,\ w \ge 0,\ w^\top\mathbf{1} = 1. \tag{5}
  $$
  **Average consensus $\iff$ the graph is balanced (in-degree = out-degree) $\iff$
  $\mathbf{1}^\top L = 0 \iff w = \mathbf{1}/n$.** As measured: adding one chord to a directed
  cycle makes $w = (\tfrac27,\tfrac17,\tfrac17,\tfrac17,\tfrac27)$ so the consensus value is
  $6/7$, different from the average $0.9$.
- **R4 (on time-varying graphs only joint connectivity matters) [D2]** — the graph need not be
  connected at any instant. If over every bounded interval the **union** of the graphs is connected
  (jointly connected), consensus is reached (`jadbabaie2003-coordination`). The measurement in the
  reproduction task is dramatic: merely alternating two graphs with $\lambda_2 = 0$ (that is,
  **neither** of them connected) drives the disagreement down to $2.2\times10^{-16}$. **The
  instantaneous $\lambda_2$ tells you nothing on a time-varying graph.**
- **R5 (the Fiedler vector points at the bottleneck) [D1]** — the sign of $f$ splits the graph in
  two (the split that minimizes $\lambda_2$ as a Rayleigh quotient), and the nodes of small
  magnitude sit on the boundary. Maximizing $\lambda_2$ by adding edges is a combinatorial problem,
  but a greedy choice joining the extremes of $f$ is the practical heuristic. As measured (a
  barbell graph with $n=10$): $\lambda_2$ goes from $0.29844$ to $0.62772$ (a factor of 2.10) with
  the best single edge, and the Fiedler greedy choice **matches** that optimum — though it is not
  guaranteed to.

## Derivation

### R1 — why the rate is $\lambda_2$

The graph is undirected so $L = L^\top$ and we may use the spectral decomposition
$L = \sum_{i=1}^n \lambda_i u_iu_i^\top$ with $\{u_i\}$ orthonormal. Fix three facts first.

**(a) $L \succeq 0$ and $L\mathbf{1} = 0$.** For any $v$,

$$
v^\top L v = \sum_{\{i,j\}\in\mathcal{E}} a_{ij}\,(v_i - v_j)^2 \;\ge\; 0, \tag{6}
$$

an identity obtained by expanding $L = D - A$ directly (collect
$\sum_i d_i v_i^2 - \sum_{i,j}a_{ij}v_iv_j$ edge by edge). And (6) vanishes at
$v = \mathbf{1}$, so $\lambda_1 = 0$ with $u_1 = \mathbf{1}/\sqrt n$.

**(b) connected $\iff \lambda_2 > 0$.** If (6) is zero then $v_i = v_j$ across every edge, so $v$
is constant on each connected component. Hence $\dim\ker L$ is the number of components, and
connected $\iff$ $\ker L$ is one-dimensional $\iff \lambda_2 > 0$. (This is the **same sentence**
as the gauge argument of R3 in `c5-factor-graphs-map` — the dimension of the null space is the
number of separate pieces.)

**(c) the average is preserved.** Multiplying (1) by $\mathbf{1}^\top$ and using
$\mathbf{1}^\top L = (L\mathbf{1})^\top = 0$ (symmetry!) gives
$\frac{d}{dt}\mathbf{1}^\top x = 0$, so $\bar x(t) = \bar x(0)$ **for all $t$**. Remember where
symmetry was used — that line breaks in R3.

**The rate.** The disagreement $\delta = x - \bar x\mathbf{1} =
(I - \frac1n\mathbf{1}\mathbf{1}^\top)x$ is orthogonal to $\mathbf{1}$, and since
$L\mathbf{1} = 0$,

$$
\dot\delta = \dot x - \underbrace{\dot{\bar x}}_{=0}\mathbf{1} = -Lx = -L(\delta + \bar x\mathbf{1}) = -L\delta. \tag{7}
$$

So $\delta$ follows the same linear system while staying in $\mathbf{1}^\perp$. On that subspace
the eigenvalues of $L$ are $\lambda_2, \dots, \lambda_n$, so for
$\delta(0) = \sum_{i\ge2}c_iu_i$,

$$
\delta(t) = \sum_{i\ge2} c_i e^{-\lambda_i t}u_i,
\qquad
\lVert\delta(t)\rVert^2 = \sum_{i\ge2}c_i^2 e^{-2\lambda_i t} \le e^{-2\lambda_2 t}\lVert\delta(0)\rVert^2, \tag{8}
$$

which is (2). **When is it an equality?** If $\delta(0) = c_2u_2$, along the Fiedler vector, (8)
holds with equality. So $\lambda_2$ is **not an upper bound but the exact worst-case exponent**,
and for a generic $\delta(0)$ the asymptotic decay rate as $t\to\infty$ is also $\lambda_2$ (as
long as $c_2 \ne 0$).

**Where the assumption breaks**: the average preservation of (c) and the orthogonal decomposition
of (8) rest entirely on **the symmetry of $L$**. On a directed graph $\mathbf{1}^\top L \ne 0$ so
(c) collapses (R3), and the eigenvectors are not orthogonal so the component-wise decay argument
of (8) cannot be used as it stands. Also (2) is a statement about a **fixed** graph — on a
time-varying graph convergence can happen even when $\lambda_2$ is zero at every instant (R4). And
saying the rate is $\lambda_2$ means it has **units of inverse time**: doubling the weights
$a_{ij}$ doubles $\lambda_2$, so "faster" is only comparable once the communication and control
bandwidth are fixed.

### R2 — the optimal step size in discrete time

$P = I - \epsilon L$ shares eigenvectors with $L$ and has eigenvalues $1 - \epsilon\lambda_i$. The
$\mathbf{1}$ direction is preserved with eigenvalue 1, and the disagreement decays on
$\mathbf{1}^\perp$ as

$$
\lVert\delta_{k}\rVert \le r(\epsilon)^k\lVert\delta_0\rVert,
\qquad r(\epsilon) := \max_{2\le i\le n}\lvert 1 - \epsilon\lambda_i\rvert. \tag{9}
$$

Since the $\lambda_i$ lie in $[\lambda_2, \lambda_n]$ and $g(\lambda) = \lvert1-\epsilon\lambda\rvert$
is a piecewise-linear function of $\lambda$ (for a fixed $\epsilon>0$), the maximum occurs **only
at the endpoints of the interval**, giving (3). For $r < 1$ both ends must be below 1, so
$0 < \epsilon\lambda_i < 2$ is required for every $i\ge2$, and the binding constraint is $i = n$,
hence $0 < \epsilon < 2/\lambda_n$.

**Minimizing.** For small $\epsilon$ the term $\lvert1-\epsilon\lambda_2\rvert = 1-\epsilon\lambda_2$
decreases while $\lvert1-\epsilon\lambda_n\rvert$ turns from decreasing to increasing at
$\epsilon = 1/\lambda_n$. One decreases and the other (for large enough $\epsilon$) increases, so
the minimum is **where the two are equal**:

$$
1 - \epsilon\lambda_2 = \epsilon\lambda_n - 1
\quad\Longrightarrow\quad
\epsilon^\ast = \frac{2}{\lambda_2+\lambda_n},
\quad
r^\ast = 1 - \epsilon^\ast\lambda_2 = \frac{\lambda_n-\lambda_2}{\lambda_n+\lambda_2}, \tag{10}
$$

which is (4). In terms of the condition number $\kappa = \lambda_n/\lambda_2$ we get
$r^\ast = (\kappa-1)/(\kappa+1)$, so the iteration count needed is on the order of
$\log(1/\varepsilon)/\log(1/r^\ast) \approx \tfrac{\kappa}{2}\log(1/\varepsilon)$. **Continuous
time sees only $\lambda_2$ but discrete time sees $\kappa$** — a distinction that matters in
practice. A star-shaped graph with a single hub has $\lambda_n \approx n$, so $\kappa$ grows and
discrete consensus is slow.

**Where the assumption breaks**: (10) presumes that $\lambda_2$ and $\lambda_n$ are **known**.
Both are global quantities and are not free in a distributed setting — in practice one uses a
**local** bound such as $\epsilon < 1/\max_i d_i$ (from Gershgorin, $\lambda_n \le 2\max_i d_i$)
and gives up optimality. Also (9) assumes the step size is **the same at every node**. Letting each
node pick its own $\epsilon_i$ makes $P$ asymmetric and moves us into the situation of R3 — merely
choosing weights independently destroys average consensus.

### R3 — why the consensus value shifts on a directed graph

On a directed graph $L = D_{\mathrm{in}} - A$ and the row sums are zero, so $L\mathbf{1} = 0$
still holds. The **column** sums, however, are not zero. Revisiting (c) of R1,

$$
\frac{d}{dt}\big(\mathbf{1}^\top x\big) = -\mathbf{1}^\top L x \ne 0 \quad \text{(in general)} \tag{11}
$$

so the average is not preserved. What is preserved then? Taking a left null vector with
$w^\top L = 0$,

$$
\frac{d}{dt}\big(w^\top x\big) = -w^\top L x = 0 \tag{12}
$$

so **the $w$-weighted average is the invariant**. If the dynamics converges then the limit is a
constant vector $c\mathbf{1}$, and (12) gives $c = w^\top x(0)$ (normalizing
$w^\top\mathbf{1} = 1$), which is (5). The existence and non-negativity of $w$ follow from
Perron-Frobenius (with a rooted out-branching, $\ker L^\top$ is one-dimensional and contains a
non-negative vector).

**The balance condition.** $w = \mathbf{1}/n$ $\iff$ $\mathbf{1}^\top L = 0$ $\iff$ in-degree =
out-degree at every node $\iff$ the graph is **balanced**. The equivalence of the three follows
from comparing definitions directly:
$(\mathbf{1}^\top L)_j = \sum_i L_{ij} = d_{\mathrm{in}}(j) - d_{\mathrm{out}}(j)$.

**In numbers.** Adding the chord $0\to3$ to the directed cycle $0\to1\to2\to3\to4\to0$ raises
node 0's out-degree to 2 and breaks the balance. As measured:
$\lVert\mathbf{1}^\top L\rVert_\infty = 1$ and
$w = (\tfrac27, \tfrac17, \tfrac17, \tfrac17, \tfrac27)$, so at
$x(0) = (1, 2, -3, 4, 0.5)$ the consensus value is

$$
w^\top x(0) = \frac{2 + 2 - 3 + 4 + 1}{7} = \frac{6}{7} = 0.857142857\ldots
$$

different from the average $0.9$. Removing the chord to get a plain directed cycle restores the
balance and the consensus value becomes exactly $0.9$.

**Where the assumption breaks**: $w$ depends **only on the graph structure**, not on the initial
values. So on a directed graph it is "who gets listened to" that determines the consensus value —
a node with low in-degree and high out-degree (one that talks a lot and listens little) receives a
large $w_i$. This is the path by which communication asymmetry in a multi-robot system
(differences in transmit power, one-way links caused by terrain) turns directly into **estimation
bias**. And without a rooted out-branching convergence itself fails — strong connectivity is not
required, but "one root that reaches everybody" is.

### R4 — instantaneous connectivity is not required on a time-varying graph

Work in discrete time. With $x_{k+1} = P_k x_k$ and $P_k = I - \epsilon L_k$, choose $\epsilon$ so
that every $P_k$ is row-stochastic (non-negative, rows summing to one), which holds for
$\epsilon \le 1/\max_i d_i$. Then

$$
x_k = P_{k-1}\cdots P_1P_0\,x_0 \tag{13}
$$

and the question is whether **a product of stochastic matrices contracts to rank one**. If each
$P_k$ is connected on its own graph then each is a contraction, but if it is not, $P_k$ is block
diagonal and **mixes nothing by itself**. The key observation is that the product mixes: if $P_0$
mixes $\{0,1\}$ and $\{2,3\}$ separately and $P_1$ mixes $\{1,2\}$, then $P_1P_0$ carries node 0's
information all the way to node 3.

The theorem of `jadbabaie2003-coordination` makes this precise: if over every finite interval
$[k, k+T)$ the union $\bigcup_{s=k}^{k+T-1}\mathcal{G}_s$ is connected (joint connectivity), then
the product in (13) converges to rank one and consensus is reached. The proof shows that the
**Dobrushin (ergodicity) coefficient** of the product over each interval drops below $1-\gamma$,
and then iterates that. **[D2]**

**The measurement is the point.** With $n=6$, alternating
$\mathcal{G}_0 = \{(0,1),(2,3),(4,5)\}$ and $\mathcal{G}_1 = \{(1,2),(3,4)\}$ — **both with
$\lambda_2 = 0$**, so neither is connected — reaches consensus because the union is the path
$0{-}1{-}2{-}3{-}4{-}5$: the disagreement is $2.2\times10^{-16}$ after 4000 steps. Using instead
$\{(0,1),(2,3)\}$ and $\{(1,2)\}$ leaves nodes 4 and 5 isolated even in the union, and the
disagreement stays at $2.5$. **Trying to predict the rate of time-varying consensus from the
instantaneous $\lambda_2$ is meaningless.**

**Where the assumption breaks**: joint connectivity is a **sufficient** condition, and the theorem
bounds the rate only loosely through $T$ and $\gamma$ — it does not give an exact exponent the way
$\lambda_2$ does for a fixed graph. Each $P_k$ must also be stochastic, which requires the bound on
$\epsilon$; and if the graphs are chosen adversarially (the union over each interval connected but
a different link cut each time) convergence can be made arbitrarily slow.

### R5 — the Fiedler vector and adding an edge

By Courant-Fischer,

$$
\lambda_2 = \min_{v\perp\mathbf{1},\,v\ne0}\frac{v^\top Lv}{v^\top v}
  = \min_{v\perp\mathbf{1},\,v\ne0}\frac{\sum_{\{i,j\}\in\mathcal{E}}a_{ij}(v_i-v_j)^2}{\sum_i v_i^2} \tag{14}
$$

and the minimizing $v$ is the Fiedler vector $f$. The numerator of (14) measures "how much $f$
changes across edges", so a small $\lambda_2$ means **there is a split that only a few edges
cross** (the intuition behind Cheeger's inequality). The sign of $f$ gives that split, and the
nodes with small $\lvert f_i\rvert$ sit on the boundary.

**The effect of one edge.** Adding the edge $\{i,j\}$ sends
$L \to L + (e_i-e_j)(e_i-e_j)^\top$, so to first order

$$
\Delta\lambda_2 \approx (f_i - f_j)^2 \tag{15}
$$

(by the eigenvalue perturbation formula at a non-degenerate $\lambda_2$). So **joining the extremes
of $f$ is first-order optimal**, which is the practical heuristic. As measured (a barbell graph of
two 5-cliques joined by a single edge, $n=10$): $\lambda_2 = 0.29844$, the Fiedler vector splits
5:5 at $\pm0.3336$ with only the two bridge nodes at $\pm0.2341$. The best achievable with one
added edge is $\lambda_2 = 0.62772$ (a factor of 2.10), and the Fiedler greedy choice **hits that
optimum**. A random edge gives $0.59834$ on average. **[D1]**

**Where the assumption breaks**: (15) is first order and usable only when $\lambda_2$ is a simple
(non-repeated) eigenvalue. If $\lambda_2$ is repeated — common in highly symmetric graphs — the
perturbation is not differentiable and the greedy choice is not optimal. That it matched on the
barbell graph is **a property of that instance's symmetry, not a guarantee**. Meanwhile the problem
of maximizing $\lambda_2$ is **convex** over edge weights (it can be written as an SDP) but
combinatorial over edge sets (problem P6).

## Proof sketch

### R1 — the convergence of consensus and its exponent

**Hypotheses** H1: $\mathcal{G}$ is undirected with weights $a_{ij} = a_{ji} > 0$. H2:
$\mathcal{G}$ is connected. H3: the dynamics is (1).
**Conclusions** C1: $x(t) \to \bar x(0)\mathbf{1}$. C2:
$\lVert\delta(t)\rVert \le e^{-\lambda_2 t}\lVert\delta(0)\rVert$ and this exponent cannot be
improved.

**Strategy**: one spectral decomposition of a symmetric matrix finishes it. No separate Lyapunov
function is needed — $V = \tfrac12\lVert\delta\rVert^2$ plays that role, but getting the rate too
requires the decomposition.

1. **$\ker L = \mathrm{span}(\mathbf{1})$.** H1 gives (6), and H2 makes the only $v$ with (6) zero
   a constant. So $\lambda_1 = 0$ is a simple eigenvalue and $\lambda_2 > 0$.
2. **Invariant subspace.** By H1 (symmetry) $\mathbf{1}^\top L = 0$, so $\bar x$ is preserved and
   $\delta$ stays in $\mathbf{1}^\perp$ while following the same equation (7). That $L$ leaves
   $\mathbf{1}^\perp$ invariant is a consequence of symmetry.
3. **Decay.** On $\mathbf{1}^\perp$ the eigenvalues of $L$ are $\lambda_2,\dots,\lambda_n > 0$, so
   (8) holds and $\delta \to 0$. This gives C1 and the bound of C2.
4. **Optimality.** Setting $\delta(0) = u_2$ makes (8) an equality, so any bound with an exponent
   larger than $\lambda_2$ is false. This is the "cannot be improved" of C2.
5. **The Lyapunov reading (for reference).** With $V = \tfrac12\delta^\top\delta$ we have
   $\dot V = -\delta^\top L\delta \le -\lambda_2\,\delta^\top\delta = -2\lambda_2 V$, and Grönwall
   gives the same conclusion. This route **does not extend to directed graphs** —
   $\delta^\top L\delta$ becomes $\tfrac12\delta^\top(L+L^\top)\delta$ and the positive
   definiteness of $L+L^\top$ becomes a separate requirement (problem P2).

**Delete a hypothesis**: dropping H2 gives $\lambda_2 = 0$ and makes $\ker L$ as large as the
number of components — each component converges to **its own** average and there is no global
consensus (the counterexample setting of the reproduction task). Dropping the symmetry of H1
breaks step 2 (R3). Dropping the positivity of the weights makes (6) lose its sign and $L$ cease to
be positive semidefinite, so the dynamics can diverge — which is why consensus with negative
weights (adversarial neighbours) becomes unstable.

(Omitted: the proofs of Grönwall's inequality and of Courant-Fischer. Mesbahi & Egerstedt ch.2-3
and `fiedler1973-algebraic-connectivity`.)

### R3' — the existence and non-negativity of $w$

**Hypotheses** H1: $\mathcal{G}$ is directed and has a rooted spanning out-branching.
H2: $L = D_{\mathrm{in}} - A$.
**Conclusions** C1: $\ker L^\top$ is one-dimensional and generated by a non-negative $w$.
C2: $w^\top x$ is an invariant of (1) and $x \to (w^\top x(0))\mathbf{1}$.

**Strategy**: turn $L$ into a stochastic matrix so that Perron-Frobenius applies.

1. **To a stochastic matrix.** With $\epsilon \le 1/\max_i d_{\mathrm{in}}(i)$, the matrix
   $P = I - \epsilon L$ satisfies $P \ge 0$ and $P\mathbf{1} = \mathbf{1}$ (row-stochastic).
2. **Perron-Frobenius.** The out-branching of H1 means the graph of $P$ has "a root that reaches
   every node". For such a non-negative stochastic matrix the eigenvalue 1 is **simple** and the
   left eigenvector $w^\top P = w^\top$ can be taken non-negative (positive, with primitivity).
3. **Back to $L$.** $w^\top P = w^\top \iff w^\top(I - \epsilon L) = w^\top \iff w^\top L = 0$. The
   two conditions are equivalent because $\epsilon > 0$. This is C1.
4. **The invariant and the limit.** By (12) $w^\top x$ is invariant, and by the simplicity of step
   2, $P^k \to \mathbf{1}w^\top$, so $x_k \to (w^\top x_0)\mathbf{1}$. Continuous time is the same
   with $e^{-Lt} \to \mathbf{1}w^\top$. This is C2.
5. **Balanced $\iff$ average.** $w = \mathbf{1}/n$ $\iff \mathbf{1}^\top L = 0$ $\iff$
   $d_{\mathrm{in}} = d_{\mathrm{out}}$ at every node. The equivalence of the three is the
   one-line component computation of R3.

**Delete a hypothesis**: without the out-branching of H1 there are two or more unreachable node
sets, $\ker L^\top$ becomes more than one-dimensional, and the limit splits into several consensus
values that depend on the initial condition. Strong connectivity is **not required** — one root
suffices, which is the point of this hypothesis, and where "one leader reaching everybody is
enough" comes from in multi-robot work.

(Omitted: the Perron-Frobenius theorem and the convergence of $P^k$. Mesbahi & Egerstedt ch.3 and
`olfati-saber2007-consensus` §II.)

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★, R1)** Expand the identity (6),
$v^\top Lv = \sum_{\{i,j\}}a_{ij}(v_i-v_j)^2$, with no missing steps, and from it show in turn
(a) $L\succeq0$, (b) $\dim\ker L$ equals the number of connected components, (c) connected
$\iff\lambda_2>0$. (d) What happens to $\lambda_2$ if every edge weight is scaled by $c$, and what
condition does that place on the claim "convergence got faster"?
*Strategy and key inequality*: (a) and (b) follow directly from (6), and (c) is a special case of
(b). For (d), $\lambda_2 \to c\lambda_2$ so the rate scales by $c$, but the comparison is
meaningless unless the communication period or control bandwidth is held fixed — **this is a
question about units.** The expansion is hidden.

**P2 (proof, ★★★, R1·R3)** State exactly where the Lyapunov argument of R1 (step 5 of the proof
sketch) breaks on a directed graph, then (a) show that $\lVert\delta\rVert$ decreases monotonically
if $L + L^\top \succeq 0$, (b) decide whether that condition is stronger or weaker than
balancedness, and (c) construct a strongly connected directed graph whose $L+L^\top$ is not
positive semidefinite (and which nevertheless reaches consensus).
*Strategy*: (a) uses $\dot V = -\tfrac12\delta^\top(L+L^\top)\delta$. (c) is the crux — the goal is
to show that consensus convergence does **not** require a monotone decrease of $\lVert\delta\rVert$
(the disagreement can grow during a transient). The expansion is hidden.

**P3 (derivation, ★★, R2)** Derive (3) and (4) with no missing steps, then (a) say why the maximum
of $r(\epsilon)$ occurs only at the endpoints of the interval, (b) write the rate when $\epsilon$
is fixed at the Gershgorin bound $1/\max_i d_i$ in terms of $\lambda_2$ and $\max_i d_i$, and
(c) find $\kappa$ and $r^\ast$ as functions of $n$ for a star graph ($n$ nodes, one hub).
*Solution sketch*: for (c), the Laplacian eigenvalues of a star are $\{0, 1^{(n-2)}, n\}$, so
$\lambda_2 = 1$, $\lambda_n = n$, $\kappa = n$ and $r^\ast = (n-1)/(n+1)$. That is, **discrete
consensus slows down linearly as nodes are added.** It is excellent to contrast this with
continuous time, where $\lambda_2 = 1$ independently of $n$.

**P4 (numerical, ★, R1·R2·R5)** For the four graphs of the reproduction task, find (a) $\lambda_2$
and the asymptotic rate, (b) the discrete-time optimal step size and its rate, and (c) for the
barbell graph with $n=10$, $\lambda_2$ and the $\lambda_2$ of the best, worst and Fiedler choices
of one added edge.
*Answer*: (a) and (b) are the tables of acceptance criteria 1 and 2. (c) base
$\lambda_2 = 0.29843788$, best $0.62771868$ (edge $(3,9)$), worst $0.53589838$ (edge $(2,5)$),
Fiedler choice $(6,1)$ → $0.62771868$ (matching the optimum), random edge average $0.59833618$.
Tolerance $10^{-6}$.
Check it: confirm that the barbell's Fiedler vector splits 5:5 and that the two bridge nodes have
the smallest magnitude ($\pm0.2341$ against $\pm0.3336$) — if not, the Laplacian or the graph
construction is wrong.

**P5 (numerical, ★★, R3·R4)** (a) Compute **by hand** the $w$ of the directed cycle
$0\to1\to2\to3\to4\to0$ with the chord $0\to3$ added, and the consensus value at
$x(0) = (1,2,-3,4,0.5)$, then compare against the numerics. (b) Confirm that the consensus value
is the average on the plain directed cycle. (c) Build two graphs on $n=6$ that each have
$\lambda_2 = 0$ but whose union is connected and show consensus is reached, and show it is not for
a pair whose union is disconnected.
*Answer*: (a) $w = (\tfrac27,\tfrac17,\tfrac17,\tfrac17,\tfrac27)$ and the consensus value
$\tfrac{2+2-3+4+1}{7} = \tfrac67 = 0.857142857$ (different from the average $0.9$). (b) exactly
$0.9$. (c) union connected: disagreement $< 10^{-15}$ after 4000 steps (reference
$2.2\times10^{-16}$); union disconnected: the disagreement stalls at $2.5$. Tolerance $10^{-8}$.
*Grading point for (a)*: $w$ must be obtained by solving $w^\top L = 0$ as a system by hand, not by
calling an eigendecomposition. The answer must explain in one line why nodes 0 and 4 receive the
larger weights (out-degree against in-degree).

**P6 (implementation, ★★, R5)** Solve the problem of maximizing $\lambda_2$ two ways and compare.
(a) Maximization over edge **weights**: solve $\max_{a\ge0,\ \sum a = 1}\lambda_2(L(a))$ as an SDP
($\max t$ subject to $L(a) \succeq t(I - \tfrac1n\mathbf{1}\mathbf{1}^\top)$). (b) Compare greedy
addition over edge **sets** (the Fiedler heuristic) against exhaustive search.
*Rubric*: (a) shows convexity from the constraint ($\lambda_2$ is a concave function of $a$) and
reports the numerical solution; (b) shows numerically that greedy and exhaustive search agree for
one edge and diverge for two or three; (c) shows that the first-order perturbation (15) is unusable
on a graph with a repeated $\lambda_2$ (a complete graph or a cycle); (d) summarizes the complexity
difference (convex versus combinatorial) in a paragraph.

**P7 (counterexample, ★★, R2·R4)** (a) Show that "the graph with faster consensus is the one with
larger $\lambda_2$" is false **in discrete time** — construct a pair of graphs where the one with
larger $\lambda_2$ converges more slowly. (b) Show that "time-varying consensus is faster than a
fixed graph if the graph is connected at every instant" is false.
*Property checklist*: (a) uses R2's point that $\kappa = \lambda_n/\lambda_2$ governs — comparing a
star against a cycle will do (for a star $\lambda_2 = 1$ while for a cycle it is
$2(1-\cos(2\pi/n))$, so the star is larger, but the star's $\kappa$ is $n$ while the cycle's is
$O(n^2)$ — compute them yourself and do not reverse the conclusion). (b) uses a construction that
alternates sparse trees, each connected but with few edges. The answer must state that the
counterexample was confirmed numerically.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read with 3-pass and attack questions 4, 5, 6 and 7 on the third pass.

1. **Olfati-Saber, Fax & Murray, "Consensus and cooperation in networked multi-agent systems"
   (2007, Proceedings of the IEEE)** — role: `survey`.
   <https://doi.org/10.1109/JPROC.2006.887293> (§II-III)
   Extra questions: (a) of the consensus variants the authors survey (weighted, leader-follower,
   with delays), which are explained by R1-R4 here and which need new tools? (b) how does the
   exponent of (2) change once time delays enter?
2. **Jadbabaie, Lin & Morse, "Coordination of groups of mobile autonomous agents using nearest
   neighbor rules" (2003, IEEE T-AC)** — role: `seminal`.
   <https://doi.org/10.1109/TAC.2003.812781> (§III)
   Extra questions: (a) is the authors' joint connectivity condition exactly the statement of R4
   here, or weaker? (b) how does the ergodicity (Dobrushin) coefficient used in the proof relate to
   the $\lambda_2$ of a fixed graph? (c) what do the authors **not** guarantee (the rate?)
3. **Fiedler, "Algebraic connectivity of graphs" (1973, Czechoslovak Mathematical Journal)** —
   role: `seminal`. <https://doi.org/10.21136/CMJ.1973.101168> (§2-3)
   Extra questions: (a) write one upper and one lower bound Fiedler proves for $\lambda_2$ and
   connect them to (14) here. (b) why is this paper the first citation in the multi-robot
   literature even though the word "consensus" never appears in it?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) the independent and dependent variables and the baselines — were they tuned fairly?
(6) does the metric match the claim, and are variance and seeds reported? (7) what is missing for
reproduction? (8) if the result were wrong, which assumption would you doubt first?
(9) computational and memory complexity, and real-time feasibility. (10) what would you change to
surpass it in a year?

## Reproduction task

**Tier R1 (numerical check).** Compute budget: one laptop CPU core, under a minute in total, under
200 MB. Only numpy and scipy.

**The input data** is produced by the generator below (fixed seed, deterministic). No external
dataset is needed.

```python
"""s5-graph-consensus reproduction task: graph generators and the Laplacian."""

import numpy as np

SEED = 20261112


def laplacian(A):
    """The symmetric Laplacian when undirected, the in-degree Laplacian L = D_in - A when directed."""
    return np.diag(A.sum(1)) - A


def er_graph(n, p, rng):
    """Erdos-Renyi G(n,p), resampled until connected. Returns the adjacency matrix."""
    while True:
        A = (rng.random((n, n)) < p).astype(float)
        A = np.triu(A, 1)
        A = A + A.T
        if np.linalg.eigvalsh(laplacian(A))[1] > 1e-9:
            return A


def directed_cycle(n, chord=None):
    """The directed cycle i -> i+1. chord=(i, j) adds the edge i -> j."""
    A = np.zeros((n, n))
    for i in range(n):
        A[(i + 1) % n, i] = 1.0  # A[i, j] = 1 means "i listens to j"
    if chord is not None:
        i, j = chord
        A[j, i] = 1.0
    return A


def edge_graph(n, pairs):
    """The Laplacian of the graph with exactly the given undirected edges."""
    A = np.zeros((n, n))
    for i, j in pairs:
        A[i, j] = A[j, i] = 1.0
    return laplacian(A)


def barbell(k):
    """Two k-cliques joined by a single edge (n = 2k)."""
    n = 2 * k
    A = np.zeros((n, n))
    for a in range(k):
        for b in range(a + 1, k):
            A[a, b] = A[b, a] = 1.0
            A[k + a, k + b] = A[k + b, k + a] = 1.0
    A[k - 1, k] = A[k, k - 1] = 1.0
    return A
```

**What to do.** Measure four parts. Use `scipy.linalg.expm` for the continuous-time propagation.

**Part A — the rate equals $\lambda_2$.** With `rng = np.random.default_rng(SEED)`, draw
$(n,p) \in \{(20,0.2), (20,0.5), (40,0.15), (60,0.1)\}$ **in that order** (reusing the same `rng`).
On each graph take $x_0 \sim$ `rng.standard_normal(n)` and $\delta_0 = x_0 - \bar x_0$, and measure
the asymptotic rate by a **two-point slope in a late window**: at $t_1 = 20/\lambda_2$ and
$t_2 = 25/\lambda_2$,
$\text{rate} = \big(\log\lVert\delta(t_1)\rVert - \log\lVert\delta(t_2)\rVert\big)/(t_2-t_1)$.
(An early window mixes in the faster modes and is wrong by about 10% — see the diagnosis table.)

**Part B — the discrete-time optimal step size.** With `np.random.default_rng(SEED + 1)`, draw
$(20,0.3)$ and $(30,0.2)$ in that order. On each graph compute $\epsilon^\ast$ and $r^\ast$ from
(4), then sweep $\epsilon$ over a 20001-point grid on $[10^{-4},\ 2/\lambda_n)$ and compare against
the minimizer of $r(\epsilon)$ from (3).

**Part C — directed and time-varying graphs.** (a) For `directed_cycle(5, chord=(0, 3))` and
`directed_cycle(5)`, find $w$ (the left null vector, normalized to $w^\top\mathbf{1}=1$),
$\lVert\mathbf{1}^\top L\rVert_\infty$, and the consensus value at $x(0) = (1,2,-3,4,0.5)$ (via
`expm` at $t = 400$). (b) With $n=6$, alternate
$\mathcal{G}_0 = \{(0,1),(2,3),(4,5)\}$ and $\mathcal{G}_1 = \{(1,2),(3,4)\}$ at $\epsilon = 0.4$
for 4000 steps, and do the same for the pair $\{(0,1),(2,3)\}$, $\{(1,2)\}$. Use
$x_0 = (1,2,-3,4,0.5,-1.5)$.

**Part D — the Fiedler vector and edge addition.** On `barbell(5)`, find $\lambda_2$ and the
Fiedler vector, then add each absent edge in turn and measure $\lambda_2$ to find the best and
worst, and compare against the Fiedler heuristic (joining $\arg\max f$ to $\arg\min f$).

**Acceptance criteria — all four conditions must hold.**

1. **Part A** — reproduce the table below, with a **relative error $< 10^{-5}$** in all four cases.

   | $n$ | $p$ | $\lambda_2$ | asymptotic rate | relative error |
   |---|---|---|---|---|
   | 20 | 0.20 | $1.483185$ | $1.483190$ | $3.2\times10^{-6}$ |
   | 20 | 0.50 | $2.765269$ | $2.765270$ | $4.5\times10^{-7}$ |
   | 40 | 0.15 | $1.350570$ | $1.350571$ | $4.5\times10^{-7}$ |
   | 60 | 0.10 | $1.253177$ | $1.253180$ | $1.9\times10^{-6}$ |

   The $\lambda_2$ values carry a tolerance of $10^{-6}$ (the graphs are pinned by the seed).
2. **Part B** — the prediction and the grid search agree to **six or more digits**.

   | $n$ | $\lambda_2$ | $\lambda_n$ | $\epsilon^\ast$ (pred / grid) | $r^\ast$ (pred / grid) |
   |---|---|---|---|---|
   | 20 | $1.7280$ | $11.7097$ | $0.14883470$ / $0.14882942$ | $0.74281249$ / $0.74282161$ |
   | 30 | $0.8708$ | $12.7777$ | $0.14653635$ / $0.14653534$ | $0.87239449$ / $0.87239537$ |

   (The grid values differ in the sixth or seventh digit because of the grid spacing; a finer grid
   converges to the prediction.)
3. **Part C** — (a) on the graph with the chord, $\lVert\mathbf{1}^\top L\rVert_\infty = 1$,
   $w = (0.2857, 0.1429, 0.1429, 0.1429, 0.2857)$
   ($=(\tfrac27,\tfrac17,\tfrac17,\tfrac17,\tfrac27)$, tolerance $10^{-6}$), and the consensus
   value is $0.85714286$ ($=6/7$), different from the average $0.9$. On the plain cycle,
   $\lVert\mathbf{1}^\top L\rVert_\infty = 0$, $w = \mathbf{1}/5$ and the consensus value is $0.9$
   (exactly the average). In both cases the final **spread is $< 10^{-14}$** (reference
   $1.1\times10^{-15}$ and $6.7\times10^{-16}$).
   (b) For the pair whose union is connected, the spread after 4000 steps is $< 10^{-14}$
   (reference $2.2\times10^{-16}$) and the average is preserved ($< 10^{-14}$); for the pair whose
   union is disconnected the spread stalls at $2.500$ (tolerance $10^{-3}$). **Report alongside it
   that $\lambda_2$ is zero for each individual graph, and that the $\lambda_2$ of the union
   Laplacian $L_0+L_1$ is $0.2679$ and $0.0000$ respectively** — the point of Part C is that what
   discriminates is not the instantaneous $\lambda_2$ but the $\lambda_2$ of the union.
4. **Part D** — on `barbell(5)`, $\lambda_2 = 0.29843788$, the Fiedler vector splits 5:5 by sign,
   and the two bridge nodes (indices 4 and 5) have magnitude $0.2341$ against $0.3336$ for the rest
   (tolerance $10^{-4}$). The best single added edge gives $\lambda_2 = 0.62771868$, the worst
   $0.53589838$, the Fiedler heuristic $0.62771868$ (matching the optimum to within $10^{-9}$), and
   200 random edges average $0.59833618$ (`default_rng(3)`, tolerance $10^{-3}$).

**Baselines**: (a) the baseline for Part A is $\lambda_2$ itself (the analytic value). (b) The
baseline for Part B is the grid search. (c) The baseline for Part C(a) is the average $\bar x_0$ —
**that it is the wrong answer is what is being measured**. (d) The baselines for Part D are the
exhaustive search and the random edge. Optional: in Part A, also fit a least squares line over the
early window ($t \in [0, 12/\lambda_2]$ entirely) and report that the relative error degrades to
order $10^{-1}$ (reference: up to $1.5\times10^{-1}$) — this makes clear why a late window is used.

**Numbers to report**: every value of the four criteria, plus whether
$\kappa = \lambda_n/\lambda_2$ and $r^\ast = (\kappa-1)/(\kappa+1)$ agree in Part B (for the second
graph $\kappa = 14.67$ and $r^\ast = 0.8724$).

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The Part A rate is about 10% **larger** than $\lambda_2$ | an early window was included in the fit — the faster modes are still alive | push $t_1$ out to $20/\lambda_2$ and report it next to the optional full-window fit |
| $\lVert\delta(t)\rVert$ underflows to zero in Part A so the logarithm blows up | $t_2$ is too large | confirm that $e^{-25} \approx 1.4\times10^{-11}$ is the relative scale and reduce $t_2$ |
| The Part A $\lambda_2$ values differ from the table | a fresh `rng` was created per graph | check that one `rng` is used **consecutively** across the four graphs, and that the resampling loop consumes it |
| The Part B grid optimum matches the prediction to only two digits | the grid is too coarse | raise the point count tenfold and check that it converges to the prediction |
| The $w$ of Part C(a) has negative entries | the sign and normalization of the eigenvector were not fixed | normalize $w$ to $w^\top\mathbf{1} = 1$ and fix the sign to be positive |
| The Part C(a) consensus value comes out equal to the average | the adjacency direction was flipped (the meaning of $A_{ij}$) | check first that $\lVert\mathbf{1}^\top L\rVert_\infty$ is nonzero |
| Part C(b) converges even for the disconnected union | an edge linking nodes 4 and 5 slipped into one of the graphs | print the $\lambda_2$ of the sum of the two Laplacians and check it is zero |
| The Part D Fiedler vector does not split 5:5 | $\lambda_2$ is repeated so the eigenvectors mixed | print $\lambda_3-\lambda_2$ — on barbell(5) it is $4.7016$, a simple eigenvalue |

## Open problems

- **(Open problem) Choosing the optimal step size without knowing $\lambda_2$ in a distributed
  setting** — the $\epsilon^\ast$ of (4) requires the global quantities $\lambda_2$ and
  $\lambda_n$, but each robot knows only its own neighbours. Current approaches use a conservative
  local bound ($\epsilon < 1/\max_i d_i$), a two-stage method that estimates $\lambda_n$ by
  consensus itself, or accelerated (Chebyshev, heavy-ball) consensus; see
  [the consensus survey](https://doi.org/10.1109/JPROC.2006.887293) §II-III. What is missing: a
  fully distributed rule that **adapts** the step size while guaranteeing convergence and
  approaching the optimal $r^\ast$.
- **(Open problem) Consensus with adversarial or non-cooperative nodes** — R1 through R4 assume
  every node follows the same rule. If some send arbitrary values (Byzantine) the consensus value
  can be manipulated arbitrarily, and the theory that handles consensus and robust estimation
  together is still fragmented (the same root as the clustered-outlier problem of
  `c5-robust-global-estimation`). Current approaches: filtering rules that discard extreme values,
  and strengthened connectivity conditions. What is missing: a bound from the adversarial fraction
  and the graph connectivity to the achievable accuracy.
- **(Open problem) The trade-off between communication cost and convergence rate** — raising
  $\lambda_2$ needs edges (communication links), and links cost bandwidth, power and detection
  risk. Maximizing $\lambda_2$ over weights is convex (problem P6), but choosing an **edge set**
  under a cost constraint is combinatorial and not even submodular ($\lambda_2$ is not a submodular
  function of the edge set — which is why the guarantees of
  `s5-active-information-gathering` do not apply here). Current approaches: SDP relaxation with
  rounding, and greedy heuristics. What is missing: an approximation ratio for edge selection.

## Concept check

Run `rc quiz s5-graph-consensus`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: what the decay exponent of continuous-time consensus is; which quantity
governs the rate of discrete-time consensus at the optimal step size; the condition for the
consensus value on a directed graph to be the average; whether a connected graph must appear at
some instant for time-varying consensus; and the justification for the Fiedler greedy
edge-addition heuristic.

## How to study this stage

1. **Expand (6) by hand (30 min)** — verify
   $v^\top Lv = \sum_{\{i,j\}}a_{ij}(v_i-v_j)^2$ directly on the $n=3$ path graph. Positive
   semidefiniteness, the null space and connectivity all come out of that one line. The important
   moment is confirming that it is the **same sentence** as the gauge argument of
   `c5-factor-graphs-map`.
2. **R1 from a blank page (45 min)** — reconstruct (7) and (8). In the margin, note that the step
   "$\delta$ stays in $\mathbf{1}^\perp$" is due to **symmetry**. That line breaks in R3.
3. **Run Part A first (45 min)** — see the full-window fit be wrong by 10% **before** switching to
   the late window and getting $10^{-6}$. The phrase "asymptotic rate" then means something
   concrete.
4. **Optimize R2 on paper (45 min)** — draw the argument that the minimum of (10) is "where the two
   are equal". Then compute the star graph of P3(c) and get $\kappa = n$. That continuous and
   discrete time look at different quantities is the most practical conclusion in this lesson.
5. **Check Part C against hand calculation (60 min)** — solve $w^\top L = 0$ component by component
   by hand to get $(\tfrac27,\tfrac17,\tfrac17,\tfrac17,\tfrac27)$ and compute $6/7$, then match it
   against the code. Then watch consensus happen in the time-varying experiment with graphs whose
   $\lambda_2$ is zero — the most counter-intuitive number in this lesson.
6. **Part D and P6 (60 min)** — print the Fiedler vector and find the barbell's bridge by eye, then
   compare edge addition against the exhaustive search. Solve the SDP of P6 to confirm numerically
   that it is "convex over weights, combinatorial over edge sets".
7. **Read the papers for the scope of their guarantees (150 min)** — confirm in §III of Jadbabaie
   et al. that the joint connectivity theorem **does not give a rate**, skim the variants in §II-III
   of Olfati-Saber et al., and read Fiedler 1973 for the bounds on $\lambda_2$. Write the one-page
   note per paper **without exception**.
8. **End at what cannot be done (30 min)** — pick one of the three open problems and write a
   paragraph. Choosing a step size in a distributed setting is directly motivated by the numbers of
   Part B.

**Passing bar**: you can derive (6), (8) and (10) from a blank page, you can say why the consensus
value on a directed graph is $w^\top x(0)$, you have code that satisfies all four conditions of the
reproduction task, and you have notes on all three papers.
