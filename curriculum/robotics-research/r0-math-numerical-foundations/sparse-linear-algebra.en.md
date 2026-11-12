---
id: r0-sparse-linear-algebra
lang: en
title: Sparse linear algebra and large-scale least squares
summary: >-
  Derive how fill-in in a sparse Cholesky factorisation depends on the elimination ordering, use
  the Schur complement to exploit block structure, and confirm that the convergence of conjugate
  gradients is governed by the square root of the condition number.
objectives:
  - Explain graphically the condition under which fill-in appears in a sparse Cholesky factorisation.
  - Derive how the elimination ordering changes fill-in and state the purpose of ordering algorithms.
  - Eliminate a block with the Schur complement and explain why the result densifies.
  - Write the convergence bound of conjugate gradients in terms of the square root of the condition number.
  - Identify the sparse structure of robotics problems (pose graphs, bundle adjustment) and pick an appropriate solver.
tags: [numerical-linear-algebra, sparsity, cholesky, conjugate-gradient, research]
---

# Sparse linear algebra and large-scale least squares

## Setup and notation

| Symbol | Meaning |
|---|---|
| $\Lambda \in \mathbb{R}^{n\times n}$ | symmetric positive definite information matrix ($= A^\top A$ or $J^\top\Sigma^{-1}J$) |
| $G(\Lambda)$ | the **adjacency graph** of $\Lambda$: vertices are variables, edges non-zero entries |
| $L$ | the Cholesky factor ($\Lambda = LL^\top$) |
| $\mathrm{nnz}(\cdot)$ | number of non-zero entries |
| $\pi$ | elimination ordering (a permutation) |
| $\kappa$ | the condition number of $\Lambda$ |

Assumed: `r0-linear-algebra-decompositions` (conditioning and decompositions) and `f0-linear-algebra`.

## Key results

- **R1 (the graph condition for fill-in) [D2]** — eliminating variable $k$ makes its neighbours
  **a complete graph (a clique)**. Hence the non-zeros of $L$ satisfy

$$
L_{ij} \ne 0 \iff j < i \text{ in the ordering and } G \text{ has a } j \to i \text{ path whose interior vertices are all } < j \tag{1}
$$

  — this is fill-in: edges appear that $\Lambda$ did not have.
- **R2 (dependence on the ordering) [D2]** — for the same $\Lambda$, $\mathrm{nnz}(L)$ varies by
  **tens of times** with the ordering. Finding an optimal ordering is NP-hard, and practice uses
  approximations (COLAMD, AMD, nested dissection) **[D0]**.
- **R3 (the Schur complement) [D3]** — for the block partition
  $\Lambda = \begin{bmatrix}\Lambda_{11} & \Lambda_{12}\\ \Lambda_{21} & \Lambda_{22}\end{bmatrix}$,
  eliminating the first block gives

$$
S = \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}, \tag{2}
$$

  and $S$ is positive definite but **generally denser than $\Lambda_{22}$** — that fact is why
  marginalisation densifies a graph.
- **R4 (the convergence bound of CG) [D2]** — the error of conjugate gradients at iteration $k$ obeys

$$
\frac{\lVert x_k - x^\star\rVert_\Lambda}{\lVert x_0 - x^\star\rVert_\Lambda}
\le 2\left(\frac{\sqrt{\kappa}-1}{\sqrt{\kappa}+1}\right)^{k} , \tag{3}
$$

  so the number of iterations needed is $O(\sqrt{\kappa})$. Unlike the $\kappa$ dependence of a
  direct method, a **square root** appears, and the aim of preconditioning is to reduce that $\kappa$.
- **R5 (two structures in robotics) [D1]** — a pose graph is **nearly banded**, so ordering works
  well and direct methods are fast. Bundle adjustment is a **bipartite** pose-landmark structure,
  where eliminating the landmarks first by Schur complement is standard (only the reduced camera
  block has to be solved).

## Derivation

### R1 — elimination creates a clique

One step of Cholesky eliminates variable $k$, which in formulas is the one-dimensional case of the
Schur complement (2):

$$
\Lambda^{(k+1)}_{ij} = \Lambda^{(k)}_{ij} - \frac{\Lambda^{(k)}_{ik}\Lambda^{(k)}_{kj}}{\Lambda^{(k)}_{kk}} .
$$

If $\Lambda_{ik} \ne 0$ and $\Lambda_{kj} \ne 0$ then the updated entry is non-zero even when
$\Lambda_{ij}$ was zero. **Read graphically**: $i$ and $j$ were connected through $k$, so removing
$k$ requires a new $i$-$j$ edge. This happens for every pair of neighbours of $k$, so the
neighbours become a **clique**.

**Therefore**: eliminating a high-degree vertex first produces a large clique. That is why the
basic idea of ordering algorithms is "eliminate low-degree vertices first" (minimum degree).

**Where the assumption breaks**: the update requires $\Lambda_{kk} \ne 0$. Positive definiteness
guarantees it, but for a matrix that is not positive definite (gauge deficiency) the pivot becomes
zero and the factorisation fails — the gauge null space of `c1-manifold-optimization` appears here
as a **factorisation failure**.

### R4 — where the CG bound comes from

The iterate of CG at step $k$ minimises the $\Lambda$-norm error over the Krylov subspace
$\mathrm{span}\{r_0, \Lambda r_0, \dots, \Lambda^{k-1}r_0\}$. The error is therefore written as a
**minimum over degree-$k$ polynomials $p$ with $p(0)=1$**:

$$
\frac{\lVert x_k-x^\star\rVert_\Lambda}{\lVert x_0-x^\star\rVert_\Lambda}
\le \min_{p:\,p(0)=1,\ \deg p \le k}\ \max_{\lambda \in [\lambda_{\min}, \lambda_{\max}]} |p(\lambda)| .
$$

The solution of that minimax problem is the **Chebyshev polynomial equioscillating on the
interval**, and evaluating it gives (3) (omitted: the extremal property of Chebyshev polynomials —
Nocedal-Wright Theorem 5.5).

**How to read it**: at $\kappa = 10^6$ a direct method loses accuracy like $\kappa\epsilon$, while
CG needs about $\sqrt{10^6}=10^3$ iterations. **Clustered eigenvalues make it far faster** — (3) is
a loose bound that uses only the interval, and real convergence depends on the spectral
distribution. It is more accurate to understand preconditioning as "clustering the eigenvalues"
than as "reducing the condition number".

## Proof sketch

### R3 — positive definiteness and densification of the Schur complement

**Hypotheses** H1: $\Lambda$ is symmetric positive definite. H2: $\Lambda_{11}$ is invertible
(which follows from H1).
**Conclusion** C: $S = \Lambda_{22} - \Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ is symmetric
positive definite and is the information matrix of the marginal of $x_2$.

**Strategy**: write $\Lambda$ by block LDL factorisation and separate the quadratic form.

1. Block elimination gives
   $\Lambda = \begin{bmatrix}I & 0\\ \Lambda_{21}\Lambda_{11}^{-1} & I\end{bmatrix}
   \begin{bmatrix}\Lambda_{11} & 0\\ 0 & S\end{bmatrix}
   \begin{bmatrix}I & \Lambda_{11}^{-1}\Lambda_{12}\\ 0 & I\end{bmatrix}$.
2. Both triangular factors are invertible, so $\Lambda \succ 0 \iff \Lambda_{11} \succ 0$ and
   $S \succ 0$. Hence $S$ is positive definite.
3. Probabilistic reading: for $x \sim \mathcal{N}(\mu, \Lambda^{-1})$, marginalising $x_1$ leaves
   exactly $S$ as the information matrix of $x_2$ (Gaussian marginalisation —
   `f0-probability-statistics`).
4. **Densification**: $\Lambda_{21}\Lambda_{11}^{-1}\Lambda_{12}$ is dense because
   $\Lambda_{11}^{-1}$ generally is, so the components of $x_2$ that were neighbours of $x_1$
   become **connected to each other** — the block version of the clique creation in R1.

**Delete a hypothesis**: without H1, $\Lambda_{11}$ may be singular and $S$ undefined. Practice
uses a pseudo-inverse or regularisation, but then the interpretation of the marginal changes.

**Why it matters**: step 4 is why iSAM2 in C5 is designed to **keep** variables rather than
marginalise them, whereas bundle adjustment deliberately marginalises landmarks to produce a small
dense block (R5).

## Problem set

★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** For the $\Lambda$ of a 5-vertex path graph (1-2-3-4-5), compute
$\mathrm{nnz}(L)$ for (a) the ordering $(1,2,3,4,5)$ and (b) the ordering $(3,1,5,2,4)$.
*Solution sketch*: (a) has no fill-in (a banded structure eliminated in order). (b) removes the
centre first, connecting both sides, so fill-in appears. Draw the clique at each elimination and count.

**P2 (derivation, ★★, R4)** From (3), derive "the iteration count is $O(\sqrt{\kappa})$" — write an
upper bound on the $k$ achieving relative error $\delta$, in terms of $\kappa$ and $\delta$.
*Solution sketch*: take logarithms in
$\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^k \le \delta/2$ and use
$\log\frac{\sqrt\kappa+1}{\sqrt\kappa-1} \approx 2/\sqrt\kappa$ to get
$k \gtrsim \tfrac{1}{2}\sqrt\kappa\log(2/\delta)$.

**P3 (proof, ★★★, R3)** Verify step 1 of R3 by expanding the block LDL factorisation, and prove
step 3 (that Gaussian marginalisation yields the Schur complement).
*Solution sketch*: complete the square in $x_1$ in the exponent of the joint density and integrate.
The $x_1$ terms vanish and the coefficient of the remaining quadratic form is $S$.

**P4 (numerical, ★, R4)** At $\kappa = 10^4$, what is the upper bound on the number of CG
iterations needed for a relative error of $10^{-6}$?
*Answer*: $k \gtrsim \tfrac12\sqrt{10^4}\log(2\times10^6) = 50 \times 14.5 \approx 725$.
Tolerance: the right order of magnitude (several hundred) passes. You should also note that at this
scale a direct method may well be preferable.

**P5 (implementation, ★★, R1·R2·R4)** Build a pose-graph-shaped sparse $\Lambda$ (a chain plus a
few loop closures) and compare $\mathrm{nnz}(L)$ (a) with no ordering and (b) with COLAMD/AMD, then
(c) solve the same system by CG and compare the iteration count with the bound (3).
*Rubric*: (a) sparse (csc) formats are used, never densified; (b) the problem is large enough
($n \gtrsim 2000$) that the $\mathrm{nnz}$ difference is **tenfold or more**; (c) the CG iteration
count is confirmed to be below the bound (3); (d) Cholesky is shown to fail without fixing the
gauge, and to succeed after adding a prior.

**P6 (counterexample, ★★, R3·R5)** Construct one structure in which marginalisation **helps** and
one in which it **hurts**. Show with $\mathrm{nnz}$ why marginalising landmarks helps in bundle
adjustment while marginalising old poses can hurt in a pose graph.
*Property checklist*: in a bipartite structure, marginalisation helps when one side has many
variables **not connected to each other** (landmarks share no edges). Conversely, if the eliminated
variable has many neighbours a large clique appears and it hurts.

## Paper reading

**The textbook exception applies** (lesson standard §5). Read the two chapters below and write a
one-page note for each (fixed questions 1, 3, 4 and 8).

1. **Barfoot, *State Estimation for Robotics*, ch.3** — the sparse structure of linear-Gaussian
   estimation. Questions: (a) write down **where** the author derives the sparsity of an estimation
   problem from (locality of measurements?). (b) does ordering change estimation accuracy, or only cost?
2. **Nocedal & Wright, *Numerical Optimization*, ch.5** — conjugate gradients and preconditioning.
   Questions: (a) under what conditions do the authors present CG as better than a direct method?
   (b) what principles do they offer for choosing a preconditioner, and are those applicable to
   robotics problems?

**One methodological source**: the CHOLMOD and COLAMD documentation of
[SuiteSparse](https://people.engr.tamu.edu/davis/suitesparse.html) — what ordering algorithms
actually minimise.

## Reproduction task

**Tier R1 (numerical check).** Budget: under one minute on a laptop CPU, scipy.sparse only. All
four conditions must pass.

1. **Ordering dependence of fill-in**: on a pose-graph-shaped $\Lambda$ ($n = 2000$ variables, a
   chain plus 20 loop closures), compare $\mathrm{nnz}(L)$ for (a) the natural ordering and
   (b) AMD/COLAMD, confirming a difference of **tenfold or more**.
2. **Densification by Schur complement**: build a bipartite structure of 50 poses and 500
   landmarks, and show numerically that the density ($\mathrm{nnz}/n^2$) of the reduced system
   after marginalising the landmarks is **higher** than that of the original pose block. At the
   same time, confirm the full solution agrees to within $10^{-10}$ before and after marginalisation.
3. **CG convergence against (3)**: for systems designed with condition numbers $10^2, 10^4, 10^6$,
   count CG iterations and confirm they are below the bound (3) and grow like $\sqrt\kappa$
   (log-log slope 0.5±0.15).
4. **Factorisation failure under gauge deficiency**: for a $\Lambda$ built only from relative
   measurements, confirm Cholesky fails or a pivot drops below $10^{-12}$, then show it succeeds
   after adding one prior.

**Baseline**: the difference between your solution and `scipy.sparse.linalg.splu` (or `cholmod` if
installable) is within $10^{-10}$.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| no visible effect of ordering | the problem is too small or has no loop closures | increase $n$ and add loop edges; for a pure chain the natural ordering is already optimal |
| Cholesky fails | gauge deficiency (a zero pivot per R1) or numerical indefiniteness | check the smallest eigenvalue of $\Lambda$ and add a prior |
| CG is slower than the bound | the condition number estimate is wrong, or an unnormalised problem without preconditioning | estimate the extreme eigenvalues with `eigsh` and recompute $\kappa$ |
| the solution changes after marginalisation | the right-hand-side update of the Schur complement was omitted | check $b_2 - \Lambda_{21}\Lambda_{11}^{-1}b_1$ |

## Open problems

- **(Open) Orderings tailored to robotics structure** — COLAMD and AMD are for general sparse
  matrices, and dedicated orderings exploiting the **known structure** of pose graphs and bundle
  adjustment (a chain plus sparse loops, a bipartite structure) are not systematised; practice
  relies on heuristics (`c5-sparsity-isam`).
- **(Open) Reusing preconditioners on manifolds** — because the tangent space changes every
  iteration, there is no principled way to reuse a preconditioner (the same item as the open
  problem of `c1-manifold-optimization`).
- **(Open) When to switch between direct and iterative methods** — given a problem size, condition
  number and sparsity pattern, there is no quantitative criterion for deciding **in advance** which
  is faster. At bundle-adjustment scale this is a particularly practical problem.

## Concept check

Run `rc quiz r0-sparse-linear-algebra` (add `--lang en` for the English text). It is for concept
checking only.

The four items cover: what elimination does to the graph; whether the ordering changes accuracy or
only cost; why bundle adjustment eliminates landmarks first; and how the CG iteration count scales
with the condition number.

## How to study this stage

1. **See it as a graph first (40 min)** — learn R1 as a picture, not a formula. On a small graph
   (5-6 vertices) eliminate by hand and draw the cliques appearing. P1 is that exercise.
2. **See the fill-in difference as a number (60 min)** — do condition 1 of the reproduction task
   first. Once you have seen the tenfold difference, it is obvious why ordering is a research area
   of its own.
3. **Write the Schur complement two ways (60 min)** — derive it in linear algebra (block
   elimination) and in probability (Gaussian marginalisation). iSAM2 in C5 and bundle adjustment in
   C7 alternate between those views.
4. **Meet gauge deficiency as a factorisation failure (40 min)** — do condition 4 of the
   reproduction task. What you learned as a "null space" in `c1-manifold-optimization` appears here
   as a "zero pivot": two faces of the same phenomenon.
5. **Understand CG spectrally (50 min)** — (3) is loose. Confirming that CG converges much faster
   than the bound on a system with deliberately clustered eigenvalues makes it clear that the goal
   of preconditioning is clustering eigenvalues rather than shrinking a condition number.
6. **Read the textbooks looking for where structure comes from (100 min)** — in Barfoot ch.3, find
   "where does the sparsity come from" (locality of measurements). The answer to that question is
   the design rationale of all of C5.

**Passing bar**: you can explain R1 graphically, can derive the Schur complement two ways, can
extract the iteration bound from (3), and have code meeting all four acceptance conditions plus
notes on both textbook chapters.
