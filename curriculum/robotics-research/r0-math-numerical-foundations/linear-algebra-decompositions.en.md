---
id: r0-linear-algebra-decompositions
lang: en
title: Decompositions and condition numbers
summary: >-
  Solve least squares three ways - normal equations, QR and SVD - and derive, then confirm
  numerically, that the normal equations square the condition number. Covers the pseudo-inverse,
  null spaces and the diagnosis of rank deficiency.
objectives:
  - Derive the normal equations of least squares and prove that the condition number is squared.
  - Solve least squares by QR and by SVD and compare the numerical stability of the three methods.
  - Define the pseudo-inverse via the SVD and explain the minimum-norm solution under rank deficiency.
  - Decide numerical rank from singular values and justify the choice of threshold.
  - Derive how the condition number enters the bound on the relative error of the solution.
tags: [numerical-linear-algebra, conditioning, least-squares, research]
---

# Decompositions and condition numbers

## Setup and notation

| Symbol | Meaning |
|---|---|
| $A \in \mathbb{R}^{m\times n}$, $m \ge n$ | the coefficient matrix of an overdetermined system |
| $\sigma_1 \ge \cdots \ge \sigma_n \ge 0$ | the singular values of $A$ |
| $\kappa_2(A) = \sigma_1/\sigma_n$ | the 2-norm condition number (for full rank) |
| $A^+ = V\Sigma^+U^\top$ | the Moore-Penrose pseudo-inverse |
| $\epsilon \approx 2.2\times10^{-16}$ | double-precision machine epsilon |
| $\hat{x}$ | the solution as computed in finite precision |

Assumed: `f0-linear-algebra` (elimination, subspaces, eigenvalues, SVD) and
`f0-python-numerics-git` (floating point, finite differences). This module is **optional and can
be skipped by diagnosis**, and prerequisites are advisory.

## Self-diagnosis before starting

This is the module's first lesson, so check your readiness. If you can solve all of the following,
skip R0 and go straight to C1. **If two or more stop you**, returning to the prerequisite lesson
named in parentheses is faster.

1. If the singular values of $A$ are $(4, 2, 0.5)$, what are $\kappa_2(A)$ and
   $\kappa_2(A^\top A)$? (`f0-linear-algebra`)
   **Answer**: $\kappa_2(A) = 4/0.5 = 8$ and $\kappa_2(A^\top A) = 8^2 = 64$, because the singular
   values of $A^\top A$ are the squares of those of $A$.
2. Why is an acceptance criterion demanding a relative error of $10^{-18}$ meaningless in double
   precision? (`f0-python-numerics-git`)
   **Answer**: machine epsilon is $\approx 2.2\times10^{-16}$, so a smaller relative error cannot
   even be represented. An absolute-error criterion might still be attainable depending on scale.
3. Derive the normal equations of $\min_x \lVert Ax-b\rVert^2$. (`f0-linear-algebra`)
   **Answer**: $\nabla_x = 2A^\top(Ax-b) = 0 \Rightarrow A^\top Ax = A^\top b$.
4. For $f(x)=x^\top Mx$ with symmetric $M$, what are the gradient and the Hessian?
   (`f0-calculus-multivariable`)
   **Answer**: $\nabla f = 2Mx$ and $\nabla^2 f = 2M$.
5. Which is numerically safer in numpy, `np.linalg.lstsq` or
   `np.linalg.solve(A.T@A, A.T@b)`, and why? (`f0-python-numerics-git`)
   **Answer**: `lstsq`; being QR/SVD based it does not square the condition number. R1 of this
   lesson derives why.

## Key results

- **R1 (the normal equations square the condition number) [D2]** — for full-rank $A$,

$$
\kappa_2(A^\top A) = \kappa_2(A)^2 . \tag{1}
$$

  Forming and solving the normal equations therefore costs **half of the significant digits**.
- **R2 (least-squares perturbation bound) [D3]** — under a perturbation $\delta b$ of $b$, the
  relative error of the solution satisfies

$$
\frac{\lVert \delta x\rVert}{\lVert x\rVert} \le \kappa_2(A)\,\frac{\lVert \delta b\rVert}{\lVert b_{\mathcal{R}}\rVert}, \tag{2}
$$

  where $b_{\mathcal{R}}$ is the component of $b$ in the column space. The condition number is
  **the error amplification factor**.
- **R3 (QR and SVD) [D2]** — with $A = QR$ the least-squares solution comes from back-substituting
  $Rx = Q^\top b$, a process whose condition number is $\kappa_2(A)$ (not squared). The SVD
  solution is $x = A^+b$ and is defined even under rank deficiency.
- **R4 (pseudo-inverse and minimum-norm solution) [D3]** — when the rank is $r < n$ the
  least-squares solution is not unique and the solution set is $x_0 + \mathcal{N}(A)$. Among them
  **a unique minimum-norm solution** exists, namely $x = A^+b$.
- **R5 (numerical rank) [D2]** — numerical rank is the number of singular values with
  $\sigma_i > \tau$, with a default threshold $\tau = \sigma_1 \cdot \max(m,n)\cdot\epsilon$.
  **Because the threshold changes the verdict**, any rank claim in a rank-deficiency diagnosis
  must state it.

## Derivation

### R1 — squaring of the condition number

With the thin SVD $A = U\Sigma V^\top$,

$$
A^\top A = V\Sigma^\top U^\top U \Sigma V^\top = V\Sigma^2 V^\top ,
$$

so the eigenvalues of $A^\top A$ (which are also its singular values, being symmetric positive
semidefinite) are the $\sigma_i^2$. Hence

$$
\kappa_2(A^\top A) = \frac{\sigma_1^2}{\sigma_n^2} = \left(\frac{\sigma_1}{\sigma_n}\right)^2 = \kappa_2(A)^2 .
$$

**What is lost**: the relative error goes roughly as $\kappa \cdot \epsilon$. At
$\kappa_2(A)=10^8$ a QR solution sits near $10^8 \cdot 2.2\times10^{-16} \approx 2\times10^{-8}$,
while the normal equations give $10^{16}\cdot 2.2\times10^{-16} \approx 2$ — **no significant digit
survives.** The reproduction task shows this boundary numerically.

**Where the assumption breaks**: (1) is an identity for full-rank $A$. Under rank deficiency
$\sigma_n = 0$ leaves both sides undefined, and one must instead use an **effective** condition
number (from the smallest non-zero singular value) or regularise.

### R3 — why QR avoids the squaring

Substituting $A = QR$ (with $Q^\top Q = I$) into the least-squares objective,

$$
\lVert Ax - b\rVert^2 = \lVert QRx - b\rVert^2 = \lVert Rx - Q^\top b\rVert^2 + \lVert (I-QQ^\top)b\rVert^2,
$$

an orthogonal decomposition whose second term does not depend on $x$ (the residual orthogonal to
the column space). The solution is therefore $Rx = Q^\top b$. **The point is that $A^\top A$ is
never formed**: orthogonal transformations preserve singular values, so $\kappa_2(R) = \kappa_2(A)$
and the condition number is not squared.

### R5 — numerical rank and the threshold

Mathematical rank is "the number of non-zero singular values", but in finite precision almost no
singular value is exactly zero. A perturbation of size $\eta$ in the entries of $A$ moves the
singular values by at most $\eta$ (Weyl's inequality). Hence **singular values with
$\sigma_i \lesssim \sigma_1\epsilon$ cannot be distinguished from zero**, which is where numpy's
default $\tau = \sigma_1\max(m,n)\epsilon$ comes from.

**Practical consequence**: the gauge-freedom diagnosis of C5 and the over-parameterisation
null-space diagnosis of C1 both use "numerical rank", so a rank claim without a stated threshold
is not reproducible.

## Proof sketch

### R2 — the least-squares perturbation bound

**Hypotheses** H1: $A$ has full rank. H2: $x = A^+b$ and $x+\delta x = A^+(b+\delta b)$.
**Conclusion** C: (2).

**Strategy**: combine the fact that the norm of the pseudo-inverse is $1/\sigma_n$ with a lower
bound on the norm of the solution.

1. $\delta x = A^+\delta b$, by linearity of the pseudo-inverse.
2. $\lVert A^+\rVert_2 = 1/\sigma_n$ (immediate from the SVD), so
   $\lVert\delta x\rVert \le \lVert\delta b\rVert/\sigma_n$.
3. Meanwhile $b_{\mathcal{R}} = Ax$ gives
   $\lVert b_{\mathcal{R}}\rVert \le \sigma_1\lVert x\rVert$, i.e.
   $\lVert x\rVert \ge \lVert b_{\mathcal{R}}\rVert/\sigma_1$.
4. Dividing 2 by 3 yields
   $\frac{\lVert\delta x\rVert}{\lVert x\rVert} \le \frac{\sigma_1}{\sigma_n}\cdot
   \frac{\lVert\delta b\rVert}{\lVert b_{\mathcal{R}}\rVert}$, which is C.
5. **The bound is attained**: taking $\delta b$ along the left singular vector of $\sigma_n$ and
   $b$ along that of $\sigma_1$ gives equality — so (2) is not a loose bound.

**Delete a hypothesis**: without H1, $\sigma_n = 0$ breaks step 2. Under rank deficiency the
null-space component of $\delta b$ can change the solution arbitrarily, so the relative error has
**no bound** — the problem has to be redefined by regularisation (Tikhonov) or by the
minimum-norm solution (R4).

### R4 — uniqueness of the minimum-norm solution

**Hypotheses** rank $r<n$, and $x_0$ any least-squares solution.
**Conclusion** $x = A^+b$ is the unique minimum-norm solution.

1. The solution set is the affine subspace $x_0 + \mathcal{N}(A)$ (all points with the same residual).
2. $A^+b$ lies in $\mathcal{R}(A^\top) = \mathcal{N}(A)^\perp$ (it is expressed by the first $r$
   columns of $V$ alone in the SVD).
3. In an affine subspace $x_0 + \mathcal{N}(A)$ the point of least norm is the one with only a
   $\mathcal{N}(A)^\perp$ component, and such a point is **unique** (uniqueness of the orthogonal
   decomposition).
4. That point is therefore $A^+b$.

**Why it matters**: the correct reading is not "rank deficiency means no solution" but "there are
infinitely many solutions and a rule is needed to pick one". Handling gauge freedom in C1 (adding
a prior) is the same kind of choice.

## Problem set

★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Derive $\kappa_2(A^\top A) = \kappa_2(A)^2$ without the SVD, from the
definition of eigenvalues alone, and show that the relation fails for a Frobenius-based condition number.
*Solution sketch*: use that the extreme Rayleigh quotients of $A^\top A$ are $\sigma_1^2$ and
$\sigma_n^2$. The Frobenius norm sums all singular values, which breaks the squaring relation.

**P2 (derivation, ★★, R3)** Show that the condition number **of the back-substitution** in a QR
least-squares solve is $\kappa_2(R)$, and that $\kappa_2(R) = \kappa_2(A)$.
*Solution sketch*: orthogonality of $Q$ gives $A^\top A = R^\top R$, so the singular values are preserved.

**P3 (proof, ★★★, R2)** Prove constructively that the bound (2) is attained (step 5, precisely).
*Solution sketch*: set $b = \sigma_1 u_1$ and $\delta b = \eta u_n$ and evaluate both sides.

**P4 (numerical, ★, R1·R5)** For $m=n=3$ and singular values $(1, 10^{-4}, 10^{-9})$, find
(a) $\kappa_2(A)$, (b) $\kappa_2(A^\top A)$, (c) the numerical rank at numpy's default threshold.
*Answer*: (a) $10^9$; (b) $10^{18}$; (c) $\tau = 1\cdot3\cdot2.22\times10^{-16} \approx
6.7\times10^{-16}$, and all three singular values exceed $\tau$, so the numerical rank is **3** —
though with $\kappa_2 = 10^9$ only about seven significant digits of the solution survive.
Tolerance $10^{-9}$ (relative).

**P5 (implementation, ★★, R1·R2·R3)** Generate $A$ with condition numbers from $10^2$ to
$10^{12}$ and plot the relative error against the true solution for (a) the normal equations
(`solve`), (b) QR (`lstsq`) and (c) the SVD (`pinv`).
*Rubric*: (a) the condition number is **designed** via an SVD rather than left to a random matrix;
(b) $b$ is constructed so that the true solution is known; (c) the three curves are shown to
follow slopes $\kappa\epsilon$ and $\kappa^2\epsilon$; (d) the point near $\kappa \approx 10^8$
where the normal equations become meaningless is identified.

**P6 (counterexample, ★★, R4·R5)** Construct a matrix whose numerical rank changes with the
threshold alone, and show which solution each rank produces. Say why the claim "the rank is 2" is
meaningless without a threshold.
*Property checklist*: place singular values **deliberately** near $\tau$ (e.g.
$\sigma = (1, 10^{-15}, 10^{-17})$). A small change of threshold flips the rank between 2 and 1
and changes the minimum-norm solution.

## Paper reading

**The textbook exception applies** (lesson standard §5): the primary sources of this lesson are
standard textbooks rather than papers. Read the two chapters below and write a **one-page note**
for each, applying fixed questions 1, 3, 4 and 8 (problem, idea, guarantees, which assumption to doubt).

1. **Trefethen & Bau, *Numerical Linear Algebra*, Lectures 11-20** — QR, least squares, condition
   numbers, stability. Questions: (a) write down how the authors define **backward stability** and
   explain how it differs from "the exact solution". (b) what is the basis for the claim that the
   normal equations are **not** backward stable?
2. **Nocedal & Wright, *Numerical Optimization*, ch.10** — least-squares problems. Questions:
   (a) when do the authors justify using the normal equations (under what conditions do they say it
   is acceptable)? (b) do those conditions hold for the estimation problems of robotics (C5)?

**One methodological source**: appendices A and C of Boyd & Vandenberghe — linear algebra
background and a summary of numerical linear algebra.

## Reproduction task

**Tier R1 (numerical check).** Budget: under one minute on a laptop CPU, numpy only. All four
conditions must pass.

1. **Controlled condition number**: build $A = U\Sigma V^\top$ for a specified $\kappa$ ($U, V$
   random orthogonal, $\Sigma$ logarithmically spaced with $\sigma_1=1$ and $\sigma_n=1/\kappa$).
   `np.linalg.cond(A)` must match the target $\kappa$ to a relative error of $10^{-10}$.
2. **Error curves of the three methods**: for $\kappa \in \{10^2, 10^4, \dots, 10^{12}\}$, plot the
   relative error $\lVert\hat{x}-x^\star\rVert/\lVert x^\star\rVert$ of the normal-equation, QR and
   SVD solutions. The result must follow **$\approx \kappa^2\epsilon$ for the normal equations and
   $\approx \kappa\epsilon$ for QR and SVD** (log-log slopes of 2 and 1, estimated to within ±0.2).
3. **The threshold boundary**: for $\kappa = 10^{16}$, confirm that the normal-equation error is
   $O(1)$ (meaningless) while QR stays at or below $10^{-1}$.
4. **Minimum-norm solution**: for a rank-2 $3\times3$ matrix $A$, confirm that the `pinv` solution
   (a) minimises the residual, (b) has a null-space component below $10^{-12}$, and (c) has smaller
   norm than any other least-squares solution.

**Baseline**: `scipy.linalg.lstsq` and `numpy.linalg.lstsq` must agree to within $10^{-10}$.

**Failure diagnosis**

| Symptom | Cause | How to check |
|---|---|---|
| all three error curves look the same | the condition number is not large enough | print `cond(A)` and compare with the target; a random matrix usually has $\kappa \sim 10^2$ |
| the slopes do not separate into 2 and 1 | the component of $b$ outside the column space dominates | first check with $b = Ax^\star$ (zero residual), then add noise |
| the `pinv` solution has a large null-space component | the threshold is too large and the rank is underestimated | pass `pinv(A, rcond=...)` explicitly and print the singular values |
| the condition number differs from the target | $U, V$ are not orthogonal (not built by QR) | check `norm(U.T@U - I)` |

## Open problems

- **(Open) Estimating condition numbers for sparse problems at robotics scale** — the condition
  number of a dense matrix follows from an SVD, but at bundle-adjustment scale ($10^6$ variables)
  an SVD is impossible. Practical ways to **estimate it cheaply** by iterative methods are lacking,
  and the choice of preconditioner is largely empirical (connecting to `c7-bundle-adjustment` and
  `c5-sparsity-isam`).
- **(Open) A principled choice of numerical-rank threshold** — the default threshold assumes the
  perturbation is of the size of machine epsilon, whereas real measurement noise is far larger.
  There is no principled way to **tie measurement uncertainty to the threshold**, which makes
  gauge-deficiency diagnosis sensitive to that choice.
- **(Open) The valid range of mixed precision** — there is interest in using GPU single and half
  precision for robotics estimation, but no criterion exists for how far that is safe on
  ill-conditioned problems.

## Concept check

Run `rc quiz r0-linear-algebra-decompositions` (add `--lang en` for the English text). It is for
concept checking only; the real work is the problem set and the reproduction task.

The four items cover: the condition number of the normal equations; why QR is better; whether a
rank-deficient least-squares problem has a solution; and what must accompany a numerical-rank claim.

## How to study this stage

1. **Derive (1) on a blank page (30 min)** — two lines of SVD. That single line is the whole reason
   not to use the normal equations, so be able to derive rather than recall it.
2. **Plot the error curves first (90 min)** — do condition 2 of the reproduction task at the
   **beginning** of this lesson. Once you have seen the slopes 2 and 1 separate, the rest of the
   derivations read as explanations.
3. **Design the condition number rather than sampling it** — random matrices are too well
   conditioned for the difference to show. Building $\Sigma$ explicitly via an SVD is a technique
   reused throughout the research track.
4. **See rank deficiency as a question of choice (60 min)** — solve P6 and watch the threshold
   change the solution. Gauge freedom in C1 and null-space diagnosis in C5 have the same structure.
5. **Read the textbooks for the stability concept (100 min)** — Trefethen and Bau's definition of
   backward stability is the key. "The exact solution of a slightly different problem" rather than
   "the exact solution" is the centre of numerical analysis, and it is also how the acceptance
   criteria of a reproduction task are written.
6. **Check the link to the next lesson (20 min)** — `r0-sparse-linear-algebra` treats the same
   problem with sparse structure, where this discussion of conditioning turns into preconditioning.

**Passing bar**: you can derive (1) and (2) on a blank page, can prove the uniqueness of the
minimum-norm solution in R4, and have code meeting all four acceptance conditions plus notes on
both textbook chapters.
