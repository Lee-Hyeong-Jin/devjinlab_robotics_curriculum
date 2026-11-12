---
id: c5-sparsity-isam
lang: en
title: Sparsity and incremental inference
summary: >-
  Prove the fill-path theorem, which says the elimination order alone decides the fill-in, and
  state both the NP-completeness of minimum fill-in and the bounds that graph structure buys.
  Derive from the conditional factorization of the Bayes tree why iSAM2's incremental
  re-elimination is local, and measure how the cost of an incremental QR update is set by
  distance in the variable order. Derive the densification that marginalization causes and show
  that the KL-optimal approximation on a fixed sparsity pattern is moment matching.
objectives:
  - Prove the fill-path theorem and explain which edges get filled and why.
  - Derive the equivalence between the existence of a zero-fill order and chordality, and say why a chain graph has no fill-in.
  - Identify exactly which cliques of a Bayes tree a new factor invalidates.
  - Derive that the number of Givens rotations in an incremental QR update is set by distance in the variable order, and separate the O(1) and Theta(N) cases.
  - Derive that the KL-optimal Gaussian approximation under a fixed sparsity pattern matches the covariance on that pattern.
  - Show numerically why zeroing out an information entry to sparsify produces overconfidence.
tags: [state-estimation, factor-graph, sparsity, fill-in, isam2, bayes-tree, research]
---

# Sparsity and incremental inference

## Setup and notation

The notation of `c5-factor-graphs-map` carries over unchanged ($\mathcal{X}$, $\Lambda$, $\eta$,
$\mathsf{R}$, $\mathcal{S}(x_i)$, $A$, $b$). Result R3 of that lesson (Gaussian elimination = the
Schur complement) and its step 6 (the separator becomes a clique) are the starting point here.
Additional symbols:

| Symbol | Meaning |
|---|---|
| $\mathcal{G}(\Lambda) = (V, E)$ | the variable adjacency graph: $V = \{x_1,\dots,x_n\}$ and $\{x_i,x_j\}\in E \iff \Lambda_{ij} \ne 0$ |
| $\sigma : V \to \{1,\dots,n\}$ | the elimination order (a bijection); a smaller $\sigma(v)$ is eliminated earlier |
| $\mathcal{G}^+_\sigma = (V, E^+_\sigma)$ | the **filled graph**: every edge that exists after running elimination to the end under $\sigma$ |
| $E^+_\sigma \setminus E$ | the **fill-in**: edges that were not there before |
| $C$, $F_C$, $S_C$ | a clique of the Bayes tree with its **frontal** variables (those eliminated at that clique) and its **separator** ($C \setminus F_C$) |
| $w$ | the treewidth $= \min_\sigma \max_C \lvert C\rvert - 1$ |
| $\mathcal{T}$ | the nonzero pattern (edge set) a sparsification is allowed to keep |
| $\mathrm{KL}(p\Vert q)$ | $\mathbb{E}_p[\log p - \log q]$ |

As in `c5-factor-graphs-map`, the variables are coordinates in $\mathbb{R}^{d_i}$. In a pose graph
$d_i = 3$ (for $SE(2)$), so "one edge" means one $3\times3$ block. To avoid mixing blocks with
scalars, the graph discussion is at **block** level and the measured counts (nnz) are reported at
**scalar** level.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the fill-path theorem) [D3]** — for $u \ne v$,
  $$
  \{u,v\} \in E^+_\sigma \iff
    \exists\, u = w_0, w_1, \dots, w_k = v \text{ in } \mathcal{G} \text{ with }
    \sigma(w_i) < \min\big(\sigma(u), \sigma(v)\big) \;\; (0 < i < k). \tag{1}
  $$
  In other words, **which edges get filled is decided by the paths of the original graph and the
  order alone** — the numerical values play no part. Corollaries:
  $\lvert\mathrm{nnz}(\mathsf{R})\rvert = n + \lvert E^+_\sigma\rvert$ (weighted by block size for
  block variables), and a zero-fill order exists exactly when $\mathcal{G}$ is **chordal** (no
  induced cycle of length four or more).
- **R2 (minimum fill-in is NP-complete, but structure helps) [D1]** — finding the $\sigma$ that
  minimizes $\lvert E^+_\sigma\rvert$ for a given $\mathcal{G}$ is NP-complete
  (`yannakakis1981-min-fill-in`), which is why practice uses heuristics (AMD, COLAMD, nested
  dissection). On the other hand, for graph families that recursively split along separators of
  size $O(\sqrt{n})$ — planar graphs among them — nested dissection **guarantees** $O(n\log n)$
  fill and $O(n^{3/2})$ flops (`lipton1979-nested-dissection`). That 2D pose graphs are nearly
  planar is the explanation of the measured performance.
- **R3 (the Bayes tree and the locality of incremental re-elimination) [D2]** — after elimination
  the distribution factors over a clique tree as
  $$
  p(\mathcal{X}) = \prod_{C} p\big(F_C \mid S_C\big) \tag{2}
  $$
  and when a new factor $\phi_{\mathrm{new}}(V)$ is added, **the only cliques invalidated are
  those containing a variable of $V$ and their ancestors** (the path to the root); not one
  character of the remaining subtrees' conditionals changes. The cost of re-elimination is
  proportional to the size of the detached subtree.
- **R4 (incremental QR = Givens rotations; the cost is distance in the order) [D2]** — the number
  of Givens rotations needed to fold a whitened new row $(a^\top, \beta)$ into an upper
  triangular $\mathsf{R}$ is the number of nonzero columns from the first nonzero column $k_0$ to
  $N$, bounded by $N - k_0 + 1$. Hence **a factor that touches only the variables placed last in
  the order costs $O(1)$**, while a loop closure that touches the variable placed first costs
  $\Theta(N)$. As measured in the reproduction task: adding the last odometry edge takes
  **14 rotations** at $N = 300, 600$ and $1200$ alike, while a loop closure to pose 0 takes
  $898, 1798, 3598 = 3N - 2$ rotations.
- **R5 (densification by marginalization, and KL-optimal sparsification) [D2]** — marginalizing a
  variable of degree $d$ makes its Markov blanket a clique, growing the edge count by up to
  $\binom{d}{2}$, and the resulting information no longer factors into pairwise factors. Among
  Gaussian approximations restricted to an allowed pattern $\mathcal{T}$, the one that minimizes
  $\mathrm{KL}(p\Vert q)$ is
  $$
  \mu_q = \mu_p, \qquad (\Lambda_q^{-1})_{ij} = (\Sigma_p)_{ij} \;\;
    \text{for } (i,j) \in \mathcal{T} \cup \{\text{diagonal}\}, \quad (\Lambda_q)_{ij} = 0 \;\; \text{otherwise} \tag{3}
  $$
  that is, **the solution that matches the covariance (the moments) exactly on the pattern** (the
  Chow-Liu solution when $\mathcal{T}$ is a tree). Simply deleting information entries is not (3)
  and **underestimates** the marginal variances.

## Derivation

### R3 — how far does a new factor reach

By R3 of `c5-factor-graphs-map`, eliminating everything according to $\sigma$ leaves a chain of
conditionals. Grouping them in the reverse of the elimination order gives the conditional
$p(x_i \mid \mathcal{S}(x_i))$ of each step, and merging consecutive variables that share the same
separator into a single clique $C$ yields (2). Here $F_C$ are the variables eliminated at that
clique and $S_C$ the rest. The corollary of R1 that $\mathcal{G}^+_\sigma$ is chordal is what
guarantees this grouping forms a **tree** (the existence of a clique tree is equivalent to
chordality).

Now multiply by a factor $\phi_{\mathrm{new}}(V)$. Split the tree in two — let $\mathcal{A}$ be the
cliques containing a variable of $V$ together with all their ancestors, and $\mathcal{B}$ the rest.
Each clique $C\in\mathcal{B}$ contributes the conditional $p(F_C\mid S_C)$ of (2), and by the tree
structure $S_C$ is contained in its parent while $F_C \cap V = \emptyset$. Therefore

$$
p'(\mathcal{X}) \propto \phi_{\mathrm{new}}(V)\prod_{C\in\mathcal{A}} p(F_C\mid S_C)
  \cdot \prod_{C\in\mathcal{B}} p(F_C\mid S_C). \tag{4}
$$

The key is that **the factors in $\mathcal{B}$ are conditionals, not marginals**. A conditional is
already normalized for every value its separator might take, so even if the distribution of $S_C$
changes on the $\mathcal{A}$ side, $p(F_C\mid S_C)$ itself does not change. So the second product
is left alone and only the first is turned back into a factor graph and re-eliminated together with
$\phi_{\mathrm{new}}$. That is the incremental update of iSAM2 (`kaess2012-isam2` §3-4).

Why the ancestors are invalidated too: if the distribution of a variable eliminated at a clique in
$\mathcal{A}$ changes, it changes the **value** that enters its parent's separator, so the parent's
$p(F\mid S)$ must be re-evaluated at that value. The path up to the root is exactly that
propagation path.

The cost is set by the size of the detached $\mathcal{A}$, which is set by **how deep the variables
of $V$ sit in the tree**. A variable placed late in the elimination order sits near the root, so
$\mathcal{A}$ is small; a variable placed early (an old one) sits near the leaves, so $\mathcal{A}$
becomes the whole tree. That is why iSAM2 **reorders** the affected variables to the end of the
order.

Two further approximations ride on top.

- **Fluid relinearization**: a variable $x_i$ is relinearized only when its accumulated increment
  $\lvert\delta_i\rvert$ exceeds a threshold $\tau_i$, and the subtree touched by the relinearized
  variables is re-eliminated.
- **Partial back-substitution**: descending the tree stops wherever the increment falls below a
  threshold.

**Where the assumption breaks**: both thresholds are **local** tests. The factorization (2) is
exact, but the moment a threshold is introduced the solution is no longer the batch solution and
there is no global bound on the difference. One can construct situations where thousands of
increments each below threshold accumulate into a large global error (problem P6), and in practice
an iSAM2 with loose thresholds drifts quietly away from the batch solution. **Exactness is
guaranteed only at threshold zero.**

### R4 — what one Givens rotation does, and what it costs

Let $\mathsf{R}\delta = d$ be the current square root information form ($\mathsf{R}$ upper
triangular). Adding a new measurement row $(a^\top, \beta)$ gives the least-squares problem of the
stacked matrix $\begin{bmatrix}\mathsf{R} & d\\ a^\top & \beta\end{bmatrix}$. Orthogonal
transformations preserve $\lVert\cdot\rVert_2$, so multiplying this matrix on the left by an
orthogonal matrix leaves the least-squares solution unchanged. Zero out $a$ from the top. At step
$k$, if $a_k \ne 0$, apply a rotation in the plane spanned by row $k$ and the new row:

$$
r = \sqrt{\mathsf{R}_{kk}^2 + a_k^2}, \qquad c = \frac{\mathsf{R}_{kk}}{r}, \qquad s = \frac{a_k}{r}, \tag{5}
$$

$$
\begin{bmatrix} \mathsf{R}_{k,k:} & d_k \\ a_{k:}^\top & \beta \end{bmatrix}
  \;\longleftarrow\;
  \begin{bmatrix} c & s \\ -s & c \end{bmatrix}
  \begin{bmatrix} \mathsf{R}_{k,k:} & d_k \\ a_{k:}^\top & \beta \end{bmatrix}. \tag{6}
$$

The $k$-th component of the new row becomes
$-s\,\mathsf{R}_{kk} + c\,a_k = (-a_k \mathsf{R}_{kk} + \mathsf{R}_{kk}a_k)/r = 0$ and vanishes.
Everything to the left of column $k$ is already zero and is not touched. Once every nonzero has
been processed the new row is entirely zero and what is left is the updated upper triangular
$\mathsf{R}'$. Orthogonality immediately gives

$$
\mathsf{R}'^\top\mathsf{R}' = \mathsf{R}^\top\mathsf{R} + a a^\top \tag{7}
$$

which is the normal equations with one row added — a rank-one update performed without ever
forming the information matrix.

**Cost.** Equation (6) touches row $k$ of $\mathsf{R}$ from column $k$ to the end. And after the
rotation the new row is nonzero in every column where $\mathsf{R}_{k,k:}$ was nonzero — that is,
**the new row spreads along the sparsity pattern of $\mathsf{R}$**. So the rotation count is not
the original number of nonzeros of $a$ but the number of columns reachable along the pattern
starting from the first nonzero column $k_0$, bounded by $N - k_0 + 1$. The conclusion:

- A factor touching only variables at the **end** of the order has $k_0 \approx N$, so the rotation
  count is a constant independent of $n$.
- A factor touching a variable at the **beginning** of the order has $k_0 \approx 1$, so the
  rotation count is $\Theta(N)$.

The measurements of the reproduction task show exactly this: adding the last odometry edge takes
14 rotations at every $N \in \{300, 600, 1200\}$, while a loop closure to pose 0 takes $3N - 2$
rotations (898, 1798, 3598).

**Where the assumption breaks**: (7) holds for a **fixed variable order**. Reordering forces
$\mathsf{R}$ to be rebuilt from scratch, so reordering itself costs $O(\text{fill})$. And (7) is an
exact update of a *linear* problem, not a relinearization of a nonlinear one — once the Jacobian
changes, adding $aa^\top$ is not enough; the row has to be **removed** and re-added. Givens
rotations cannot remove a row (that needs hyperbolic rotations, which are numerically unstable), so
iSAM2 re-eliminates the affected subtree instead.

### R5 — marginalization densifies, and sparsification has an optimum

**Densification.** By step 6 of R3 in `c5-factor-graphs-map`, eliminating (or marginalizing) $x_v$
makes $\mathcal{S}(x_v)$ a clique. If $\deg(x_v) = d$ and $\mathcal{S}(x_v)$ already contained $e$
edges, then $\binom{d}{2} - e$ new edges appear. Removing one intermediate pose usually has $d = 2$
and ends with a single edge, but a pose carrying loop closures and landmarks has a large $d$, and
removing poses one after another makes $d$ grow cumulatively. That is why "shrink the graph by
marginalizing old poses" **fails**: the variables shrink but the edges grow, and what remains is a
dense block.

**Sparsification.** So approximate the marginalization result $p = \mathcal{N}(\mu_p, \Sigma_p)$ by
a $q = \mathcal{N}(\mu_q, \Lambda_q^{-1})$ whose information entries vanish outside an allowed
pattern $\mathcal{T}$. The KL between two Gaussians is

$$
2\,\mathrm{KL}(p\Vert q) = \mathrm{tr}(\Lambda_q\Sigma_p) - \log\det(\Lambda_q\Sigma_p) - N
  + (\mu_q - \mu_p)^\top \Lambda_q (\mu_q - \mu_p). \tag{8}
$$

Since $\Lambda_q \succ 0$, the last term vanishes only at $\mu_q = \mu_p$ and the other terms do
not involve $\mu_q$, so $\mu_q = \mu_p$. Differentiate what remains with respect to $\Lambda_q$.
For symmetric matrices $\partial\,\mathrm{tr}(\Lambda\Sigma)/\partial\Lambda = \Sigma$ and
$\partial \log\det\Lambda/\partial\Lambda = \Lambda^{-1}$, so

$$
\frac{\partial}{\partial \Lambda_q}\Big[\mathrm{tr}(\Lambda_q\Sigma_p) - \log\det\Lambda_q\Big]
  = \Sigma_p - \Lambda_q^{-1}. \tag{9}
$$

$\Lambda_q$ is **constrained** to vanish outside $\mathcal{T}$, so the optimality condition is not
that (9) is zero but that (9) **projected onto $\mathcal{T}$ and the diagonal** is zero:

$$
(\Lambda_q^{-1})_{ij} = (\Sigma_p)_{ij} \quad \text{for } (i,j)\in\mathcal{T}\cup\{\text{diagonal}\}. \tag{10}
$$

That is (3). **Put zeros in the information and match the covariance** — this is the maximum
likelihood (equivalently maximum entropy) solution of a Gaussian graphical model, and when
$\mathcal{T}$ is a tree it has a closed form: add the inverses of the pairwise marginals over the
edges and subtract the double counting at internal nodes (Chow-Liu),

$$
\Lambda_q = \sum_{(i,j)\in\mathcal{T}} \big[\Sigma_p^{\{i,j\}}\big]^{-1}
  - \sum_{i} (\deg_{\mathcal{T}}(i) - 1)\,\big[(\Sigma_p)_{ii}\big]^{-1}. \tag{11}
$$

(Here $\Sigma_p^{\{i,j\}}$ is the $2\times2$ marginal covariance of the pair $(i,j)$, and each term
is zero-padded to full size before summing.)

**Where the assumption breaks, 1**: (10) is the solution for $\mathrm{KL}(p\Vert q)$ (the
M-projection). Reversing the direction and minimizing $\mathrm{KL}(q\Vert p)$ (the I-projection)
gives a different answer that tends to underestimate variances. Which direction is "right" depends
on the purpose — for estimation that needs conservative uncertainty it is the M-projection.

**Where the assumption breaks, 2**: the most common mistake is not to solve (10) at all but simply
to zero out the corresponding entries of $\Lambda_p$. That asserts "these two variables are
conditionally independent" while **keeping all the remaining information**, so information is
over-counted. The numbers of problem P4 are the result: the marginal standard deviations shrink
from $(0.1,\ 0.13540064,\ 0.15275252)$ to $(0.08401681,\ 0.11504475,\ 0.12833779)$, about 16% too
small. Overconfidence does not stop there — it breaks the outlier test of the next loop closure.
The same problem appears as **information double counting** when sparsification re-uses the
original measurements (`carlevaris-bianco2014-node-removal` §III).

## Proof sketch

### R1 — the fill-path theorem

**Hypotheses** H1: $\mathcal{G} = (V,E)$ is a finite undirected graph and $\sigma$ a bijective
elimination order. H2: one elimination step is "delete a vertex $v$ and make the neighbours of $v$
that are still alive at that moment a complete graph", repeated in the order
$\sigma(1), \sigma(2), \dots$
**Conclusion** C: the two conditions in (1) are equivalent.

**Strategy**: induction in both directions. ($\Leftarrow$) induction on the **number of interior
vertices** of the path; ($\Rightarrow$) induction on the **elimination step**.

1. **($\Leftarrow$) base case.** If $k = 1$ the path is the edge $\{u,v\}\in E$ itself, and
   $E \subseteq E^+_\sigma$.
2. **($\Leftarrow$) induction.** Let $k \ge 2$ and let $w_i$ be the interior vertex with the
   smallest $\sigma$. Since $\sigma(w_i) < \min(\sigma(u),\sigma(v))$ and $\sigma(w_i)$ is the
   interior minimum, at the moment $w_i$ is eliminated both $w_{i-1}$ and $w_{i+1}$ are **still
   alive** and both are neighbours of $w_i$. By H2 the pair $\{w_{i-1}, w_{i+1}\}$ becomes an edge.
   Using it to bypass $w_i$ shortens the path by one interior vertex while the condition "every
   interior vertex is earlier than $\min(\sigma(u),\sigma(v))$" still holds. The induction
   hypothesis gives $\{u,v\}\in E^+_\sigma$.
3. **($\Rightarrow$) base case.** If $\{u,v\}\in E$, the $k=1$ path is the witness.
4. **($\Rightarrow$) induction.** If $\{u,v\}$ is a fill edge there is a first elimination step
   that creates it, and the vertex $w$ deleted at that step is adjacent (in the partially filled
   graph at that moment) to both $u$ and $v$ and is eliminated before either, so
   $\sigma(w) < \min(\sigma(u),\sigma(v))$. The edges $\{w,u\}$ and $\{w,v\}$ came into existence
   at **earlier steps**, so the induction hypothesis applies and each has a path in $\mathcal{G}$
   whose interior vertices are earlier than $\min(\sigma(w),\sigma(u))$ and
   $\min(\sigma(w),\sigma(v))$ respectively. Since $\sigma(w) < \min(\sigma(u),\sigma(v))$,
   concatenating the two paths at $w$ gives a path all of whose interior vertices are earlier than
   $\min(\sigma(u),\sigma(v))$. C.
5. **Corollary 1 (cost).** The number of nonzeros in column $j$ of $\mathsf{R}$ equals the number
   of neighbours of $j$ in $\mathcal{G}^+_\sigma$ eliminated after $j$, plus one. Hence
   $\mathrm{nnz}(\mathsf{R}) = n + \lvert E^+_\sigma\rvert$ and the flops are on the order of
   $\sum_j (\text{nonzeros in that column})^2$. If the largest clique has size $w+1$, storage is
   $O(nw)$ and computation $O(nw^2)$.
6. **Corollary 2 (chordality).** A $\sigma$ with zero fill-in exists $\iff$ $\mathcal{G}$ is
   chordal. ($\Rightarrow$) zero fill forces every induced cycle to have length three, by (1).
   ($\Leftarrow$) a chordal graph has a perfect elimination ordering
   (`rose1976-vertex-elimination`). **Chains and trees are chordal**, so an odometry-only graph has
   zero fill in the natural order — the structural reason filters are cheap, and loop closures
   break that property by creating cycles.

**Delete a hypothesis**: dropping "make the neighbours complete" from H2 (approximate elimination,
sparsification) shrinks $E^+$ but the result is no longer the exact marginal — R5 quantifies the
price. It also matters that (1) **does not depend on the values at all**: except for accidental
numerical cancellation, the sparsity can be computed ahead of time from the order and the graph
alone (symbolic factorization).

(Omitted: that the ($\Rightarrow$) induction is well-founded, and the existence proof of a perfect
elimination ordering. See the lemmas of `rose1976-vertex-elimination` §2-3.)

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (proof, ★★★, R1)** Write the ($\Leftarrow$) direction of the fill-path theorem with no
missing steps, and prove the ($\Rightarrow$) direction of Corollary 2 ("zero fill implies
chordal"). Then show that for a cycle $C_m$ with $m \ge 4$ the fill-in is exactly $m - 3$ **under
every order**.
*Strategy and key inequality*: ($\Leftarrow$) is entirely the choice of the "earliest interior
vertex" — state why it must be the earliest (both neighbours have to still be alive). For the
corollary, assume an induced cycle of length $\ge 4$ and apply (1) to its earliest vertex. For
$C_m$, elimination is the same thing as triangulating the cycle, and a triangulation of an
$m$-gon always needs $m-3$ diagonals. The expansion is hidden.

**P2 (derivation, ★★, R4)** Starting from (5) and (6), (a) derive (7); (b) express the number of
floating-point operations needed to fold one row in terms of the per-column nonzero counts of
$\mathsf{R}$; (c) show that the $\mathsf{R}'$ produced by Givens equals the Cholesky factor of
$\Lambda + aa^\top$ **up to row signs**.
*Solution sketch*: (a) is one line — the product of the rotations $Q_k$ is orthogonal, so
$\begin{bmatrix}\mathsf{R}\\a^\top\end{bmatrix}^\top\begin{bmatrix}\mathsf{R}\\a^\top\end{bmatrix}$
is preserved. (c) uses the uniqueness of the Cholesky factor among upper triangular matrices with
positive diagonal — Givens does not guarantee the diagonal sign, so the two can differ by
$\mathrm{diag}(\pm1)$.

**P3 (numerical, ★, R1)** Poses $p_0,\dots,p_4$ form a chain (4 edges) and a landmark $\ell$ is
connected to **all five** poses (5 edges). Treating blocks as scalars, find the fill-in count and
$\mathrm{nnz}(\mathsf{R})$ for (a) the order $(\ell, p_0, p_1, p_2, p_3, p_4)$ and (b) the order
$(p_0, p_1, p_2, p_3, p_4, \ell)$. (c) Bundle adjustment nevertheless eliminates landmarks
**first**. Explain why that is not a contradiction.
*Answer*: (a) 6 fill edges, $\mathrm{nnz}(\mathsf{R}) = 6 + (9 + 6) = 21$. (b) 0 fill edges,
$\mathrm{nnz}(\mathsf{R}) = 6 + 9 = 15$. Tolerance 0 (integers).
Check it with (1): in (a) the filled edges are the 6 pairs $\{p_i, p_j\}$ that were not in the
chain ($\binom52 = 10$ minus the 4 chain edges), and in (b) eliminating any $p_i$ leaves the
neighbours $\{p_{i+1}, \ell\}$, which are already adjacent.
*Grading point for (c)*: BA is not minimizing total fill but **the size of the dense block that
remains** — with hundreds of thousands of landmarks and hundreds of cameras, the reduced camera
system (dense, $\binom{n_c}{2}$) is far smaller than the whole. Also landmarks have no edges among
themselves, so $\Lambda_{11}$ is block diagonal and its inverse is free. An answer must note that
"the order with less fill is not always the faster order".

**P4 (numerical, ★★, R5)** For the one-dimensional pose graph of `c5-factor-graphs-map` P3
($\Lambda_p = \begin{bmatrix}225&-100&-25\\-100&200&-100\\-25&-100&125\end{bmatrix}$), compare two
ways of removing the $(1,3)$ information entry: (a) the KL-optimal solution $\Lambda_q$ of (3) and
(11); (b) $\Lambda_{\mathrm{naive}}$, obtained by simply setting the $(1,3)$ entry of $\Lambda_p$
to zero. Find the marginal standard deviations and $\mathrm{KL}(p\Vert q)$ for each.
*Answer*: (a) $\Lambda_q = \begin{bmatrix}220 & -120 & 0\\ -120 & 21880/99 & -1000/9\\
0 & -1000/9 & 1100/9\end{bmatrix}$; the marginal standard deviations are **exactly** those of $p$,
$(0.1,\ 0.13540064,\ 0.15275252)$, and $\mathrm{KL}(p\Vert q) = 0.0112364279$. The only moment that
is wrong is $\Sigma_q[1,3] = 1/110 = 0.00909091$ (true value $0.01$).
(b) marginal standard deviations $(0.08401681,\ 0.11504475,\ 0.12833779)$ — about **16% too
small** — and $\mathrm{KL}(p\Vert q) = 0.0758466529$, 6.7 times worse. Tolerance $10^{-8}$.
Check it: verify that (10) actually holds, i.e. that
$\lvert(\Lambda_q^{-1} - \Sigma_p)_{ij}\rvert < 10^{-12}$ on the diagonal and at $(1,2)$, $(2,3)$.

**P5 (implementation, ★★, R3·R4)** For the graph of the reproduction task, implement (a) the Givens
incremental solver and (b) a **reordering** that moves the affected variables to the end of the
order, then compare the cost of adding one loop closure before and after reordering.
*Rubric*: (a) the incremental solution matches the batch solution to within $10^{-9}$; (b) the cost
of reordering (the rotation count of rebuilding $\mathsf{R}$) and the cost saved by it are reported
in the **same unit**; (c) when reordering pays off is argued numerically (usually a loss for a
single loop closure, a gain when factors keep arriving in the same region); (d) the change in
$\mathrm{nnz}(\mathsf{R})$ after reordering is reported too.

**P6 (counterexample, ★★, R3)** Show that the intuition "if iSAM2's relinearization threshold
$\tau$ is small enough the answer is close to batch" is not a guarantee. With $\tau$ held fixed,
construct a sequence of factors for which the **difference from the batch solution grows without
bound**.
*Property checklist*: (1) every step's increment must be below $\tau$; (2) the increments must
accumulate in the same direction (no cancellation); (3) the Jacobian must depend on the state so
that the error of the stale linearization point accumulates — a trajectory whose heading turns a
little at a time in one direction is the archetype; (4) the conclusion must be phrased as
"convergence only as $\tau \to 0$". Do not write a full solution.

**P7 (paper, ★★, R3)** Read `kaess2012-isam2` and (a) separate, in two lines each, what the authors
**do** and **do not** guarantee; (b) find three pieces of information missing for reproducing the
paper's timing plots; (c) explain how the measurements of R4 (14 rotations for the last edge versus
$3N-2$ for a loop closure) fit with the paper's "$O(1)$ update" claim.
*Rubric*: (a) passes if it separates "identical to batch at threshold zero" from "no global error
bound at nonzero threshold". (b) three of: the concrete threshold values and their units, the
CCOLAMD invocation policy, the loop-closure distribution of the datasets. (c) is excellent if it
points out that "$O(1)$ is a claim about **updates whose affected subtree has constant size**, and
a loop closure is outside that assumption"; better still if it cites where the paper does (or does
not) state that assumption.

## Paper reading

**Three must-reads.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read with 3-pass and attack questions 4, 5, 6 and 7 on the third pass.

1. **Kaess, Johannsson, Roberts et al., "iSAM2: incremental smoothing and mapping using the
   Bayes tree" (2012, IJRR)** — role: `seminal`.
   <https://doi.org/10.1177/0278364911430419> (sections 3-5)
   Extra questions: (a) restate why (2) has to be a Bayes **tree** and not a Bayes **net**, using
   the sentence from R3 that "a conditional is already normalized"; (b) do the fluid
   relinearization thresholds carry units — is it legitimate to use the same threshold for
   rotation and translation?
2. **Rose, Tarjan & Lueker, "Algorithmic aspects of vertex elimination on graphs" (1976, SIAM
   J. Comput.)** — role: `seminal`. <https://doi.org/10.1137/0205021> (§2-3)
   Extra questions: (a) which of the paper's results are **not** used in robotics, and why not?
   (b) which theorem of the paper justifies separating symbolic factorization from numerical
   factorization?
3. **Carlevaris-Bianco, Kaess & Eustice, "Generic node removal for factor-graph SLAM"
   (2014, T-RO)** — role: `standard`. <https://doi.org/10.1109/TRO.2014.2347571> (§III-IV)
   Extra questions: (a) is the authors' approximation the same as the M-projection of (10) — and if
   not, where does it differ? (b) what did the authors give up in order to avoid information double
   counting?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) the independent and dependent variables and the baselines — were they tuned fairly?
(6) does the metric match the claim, and are variance and seeds reported? (7) what is missing for
reproduction? (8) if the result were wrong, which assumption would you doubt first?
(9) computational and memory complexity, and real-time feasibility. (10) what would you change to
surpass it in a year?

## Reproduction task

**Tier R2 (re-implementation).** Compute budget: one laptop CPU core, under 2 minutes, under 1 GB
(the largest case is a $1200\times1200$ dense $\mathsf{R}$). Only numpy and scipy.

**The input data** is the `make_graph()` generator of the `c5-factor-graphs-map` reproduction task,
used **unchanged** (same seed, same graph). The linearization point is the GN optimum $x^\ast$ that
lesson converged to from the dead-reckoning initial guess — from here on everything is pure linear
algebra, so nonlinearity does not disturb the numbers.

**Part A — the order decides the fill-in.** Build $A$ at $x^\ast$ and form
$\Lambda = A^\top A$ ($300\times300$). For four **scalar** variable orders, count the nonzeros
($\lvert\cdot\rvert > 10^{-9}$) of the Cholesky factor of $P^\top\Lambda P$.

**Part B — incremental QR.** Starting from $\mathsf{R} = 0$ and $d = 0$, fold the rows of $A$ in
**one at a time** with (5) and (6). Record the number of Givens rotations used per row.

**Part C — how the update cost scales.** At the three sizes `make_graph(per_lap=50, every=10)`,
`per_lap=100, every=20` and `per_lap=200, every=40`, measure the rotation count of folding one more
edge into the $\mathsf{R}$ produced by Part B — (a) between the last two poses $(n-2, n-1)$, and
(b) between pose $0$ and $n-1$. Use $\bar z = (0.1, 0, 0.02)$ and
$\sigma = \sigma_{\text{loop}}$ for the added measurement.

**Part D — sparsification.** For the $3\times3$ problem of P4, solve (10) numerically to get
$\Lambda_q$ and compare it against $\Lambda_{\mathrm{naive}}$.

**Acceptance criteria — all four conditions must hold.**

1. **The values of Part A** (all within $\pm2$ — at a $10^{-9}$ threshold a borderline entry or two
   can flip):

   | Order | $\mathrm{nnz}(\mathsf{R})$ |
   |---|---|
   | natural, `arange(300)` | 3396 |
   | reverse, `arange(300)[::-1]` | 3354 |
   | random, `default_rng(1).permutation(300)` | 5849 |
   | RCM, `scipy.sparse.csgraph.reverse_cuthill_mckee(..., symmetric_mode=True)` | 2953 |

   and the lower-triangular nonzero count of $\Lambda$ is 1018. That **the random order is nearly
   twice RCM** is the point of R2, and the spread among the three "reasonable" orders (3396 vs
   2953) is 14%.
2. **The correctness of Part B**: the solution from the incremental $\mathsf{R}$ matches the batch
   solution (`numpy.linalg.solve(Lambda, eta)`) to $\lVert\cdot\rVert_\infty < 10^{-6}$ (the
   reference implementation gives $2.6\times10^{-16}$), and the maximum difference between
   $\lvert\mathsf{R}_{\text{inc}}\rvert$ and $\lvert\mathrm{chol}(\Lambda)^\top\rvert$ is
   $< 10^{-9}$ (reference $1.1\times10^{-13}$). **The comparison is on absolute values** because
   Givens does not fix the row signs (problem P2(c)).
3. **The scaling of Part C**: these values reproduce exactly (integers).

   | $N$ | edge $(n-2, n-1)$ | edge $(0, n-1)$ |
   |---|---|---|
   | 300 | 14 | 898 |
   | 600 | 14 | 1798 |
   | 1200 | 14 | 3598 |

   So the first is a constant **independent of $n$** and the second is exactly $3N - 2$. Without
   this table you are not entitled to the phrase "$O(1)$ update".
4. **The values of Part D**: $\Lambda_q$ satisfies (10) to within $10^{-12}$, its marginal standard
   deviations match those of $p$ to within $10^{-9}$, and
   $\mathrm{KL}(p\Vert q_{\mathrm{opt}}) = 0.0112364279$ while
   $\mathrm{KL}(p\Vert q_{\mathrm{naive}}) = 0.0758466529$ (tolerance $10^{-8}$). The standard
   deviations of $q_{\mathrm{naive}}$ are $(0.08401681, 0.11504475, 0.12833779)$.

**Baselines**: (a) the batch Cholesky (`numpy.linalg.cholesky`) is the baseline for Parts A and B.
(b) The baseline for Part C is **re-factoring in batch every time**, which costs rotations on the
order of $\mathrm{nnz}(\mathsf{R})$ (3928 rotations to fold all 315 rows in the reference
implementation). The ratio between 14 and 3928 is why incremental inference exists. Optional: add
the ordering from `scipy.sparse.linalg.splu` with `permc_spec="COLAMD"` as a fifth row of Part A
and compare it against RCM.

**Numbers to report**: all four tables above; the distribution of rotation counts in Part B (the
reference implementation: odometry rows mean 1.3 and max 2, loop-closure rows mean 176.4 and max
200, anchor rows 289, 299 and 298 — **the same factor costs 200 times more depending on when it is
folded in**); and the ratio
$\mathrm{nnz}(\mathsf{R})/\mathrm{nnz}(\Lambda)$ for the four orders of Part A.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The Part A values are all small, around 300 | you are counting the sparsity of $A$, not of $\Lambda$ | check that $\Lambda$ is $300\times300$ and that its lower-triangular nonzero count is 1018 |
| RCM comes out worse than the natural order in Part A | `symmetric_mode=True` was omitted so RCM ran on an asymmetric pattern, or the permutation was applied transposed | check that $P^\top\Lambda P$ is symmetric positive definite and that `perm` was used as a column order |
| The Part B solution is only correct to about $10^{-3}$ | the rotations were not applied to $d$ and $\beta$ | check whether $\mathsf{R}$ alone is right by comparing $\lVert\mathsf{R}^\top\mathsf{R} - \Lambda\rVert$ separately |
| The Part B $\mathsf{R}$ differs from Cholesky by more than signs | the rotations were applied to the **left** of column $k$ (touching an already-zero region) | check that the slices are restricted to `[k:]` |
| The $(n-2,n-1)$ cost of Part C grows with $n$ | no nonzero threshold, so numerical dust ($10^{-18}$) is being counted as nonzero | check that $\lvert a_k\rvert < 10^{-14}$ is skipped |
| `fsolve` does not converge in Part D | the initial guess was zero — $\Lambda_q$ has to be positive definite | start from $\Lambda_p$ with only the forbidden entry zeroed out |

## Open problems

- **(Open problem) There is no theory of online variable ordering** — AMD, COLAMD and nested
  dissection are heuristics for the **batch** setting, and minimum fill-in is itself NP-complete
  ([Yannakakis 1981](https://doi.org/10.1137/0602010)). In the incremental setting the question is
  different: is paying for a reordering now worth it against the factors still to come? Current
  approaches are the partial, CCOLAMD-based reordering of
  [iSAM2](https://doi.org/10.1177/0278364911430419) and the bounds for graph families with small
  separators ([nested dissection](https://doi.org/10.1137/0716027)). What is missing: a **regret
  bound** for online reordering — a guarantee of how much worse it can be than the optimal offline
  order without knowing the distribution of future factors.
- **(Open problem) Sparsification with guarantees** — (10) gives the KL-optimal solution for a
  fixed pattern, but there is no bound on how that KL value propagates into estimator
  **consistency** (NEES), loop-closure success rate or final ATE. **How to choose** the pattern
  $\mathcal{T}$ is also open (a tree has a closed form but is far too aggressive). Current
  approaches: the GLC of [generic node removal](https://doi.org/10.1109/TRO.2014.2347571) and the
  map-lifetime discussion in §V of the
  [long-term SLAM survey](https://arxiv.org/abs/1606.05830). What is missing: conditions under
  which one can say "this sparsification does not degrade the ATE by more than $\epsilon$".
- **(Open problem) A global error bound for approximate incremental inference** — iSAM2's
  relinearization and back-substitution thresholds are **local**, per-variable tests, and there is
  no bound on how far the accumulated error can drift from the batch solution (problem P6). The
  current approach is the engineering compromise of keeping thresholds conservative and mixing in a
  periodic batch re-optimization. What is missing: an explicit bound from the threshold sequence to
  the global error, or a **certifiable** rule for setting the thresholds adaptively.

## Concept check

Run `rc quiz c5-sparsity-isam`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: the condition under which an edge gets filled (and that it does not depend on
the numerical values); whether an odometry-only chain has zero fill-in in the natural order; which
cliques of a Bayes tree must be re-eliminated when a new factor arrives; what sets the cost of
folding one measurement row into an incremental QR; and which $q$ minimizes $\mathrm{KL}(p\Vert q)$
when sparsifying a dense Gaussian onto an allowed pattern.

## How to study this stage

1. **Think in graphs first (45 min)** — draw a small pose graph of about 8 vertices and eliminate it
   by hand under two orders, shading the fill edges. Then check that (1) gives the same answer.
   Once that check works, the sentence "sparsity is structure, not values" sticks.
2. **The ($\Leftarrow$) direction from a blank page (60 min)** — the crux is the single line that
   picks the interior vertex eliminated **earliest**. If you cannot say why it has to be the
   earliest, you have not understood the proof. Problem P1 exposes that spot.
3. **Givens by hand on $3\times3$ (45 min)** — take $\mathsf{R}$ to be $3\times3$, fold one row by
   hand and verify (7) numerically. Then **change the first nonzero column** and watch the rotation
   count change. That is where the conclusion of R4 lands.
4. **Do Part C of the reproduction task first (60 min)** — it is the shortest and the most striking
   of the four parts. Printing 14 versus $3N-2$ yourself gives you a reason to read the iSAM2 paper.
5. **Parts A, B and D (105 min)** — see how bad the random order is in Part A, confirm that
   incremental and batch agree to $10^{-16}$ in Part B, and see the overconfidence by sparsifying
   two ways in Part D. Read Barfoot SER ch.3.3 alongside Part A.
6. **Read the papers in order (150 min)** — Rose et al. §2-3 first (the original theorem), iSAM2
   sections 3-5 next (its application), node removal §III-IV last (its limits). Write the one-page
   note per paper **without exception**. Yannakakis is four pages, so read it straight through in a
   break.
7. **End at what cannot be done (30 min)** — pick one of the three open problems and write a
   paragraph on why it is still open. The regret bound for online reordering is the most tractable
   research topic in this lesson.

**Passing bar**: you can state (1) and prove the ($\Leftarrow$) direction from a blank page, you can
write (7) and the Givens cost argument, you have code that reproduces all four tables of the
reproduction task, and you have notes on all three papers.
