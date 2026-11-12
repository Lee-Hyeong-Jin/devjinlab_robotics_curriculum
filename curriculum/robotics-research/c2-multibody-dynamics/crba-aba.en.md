---
id: c2-crba-aba
lang: en
title: The mass matrix (CRBA) and forward dynamics (ABA)
summary: >-
  Derive the closed form of the mass matrix from composite-rigid-body inertia and prove that CRBA
  is output-optimal in the sense that it does constant work per non-zero of its output; then
  derive the articulated-body inertia recursion as a Schur complement and show that ABA is the
  fill-in-free elimination of a tree-structured mass matrix. Ends at the identity that $d_i$ is
  exactly a Schur complement of $M$.
objectives:
  - Define the composite-rigid-body inertia $I^c_i$ and derive $M_{ij} = S_i^\top I^c_i\,{}^iX_jS_j$.
  - Show that the zero pattern of $M$ is decided by the ancestor relation of the tree and argue that CRBA is output-optimal.
  - Derive the articulated-body inertia recursion as the Schur elimination of $\ddot{q}_j$ with no missing steps.
  - Show that $d_i = S_i^\top I^A_i S_i$ equals a Schur complement of $M$ and explain $0 < d_i \le M_{ii}$.
  - Prove $I^A_i \succ 0$ by induction and so guarantee that ABA never divides by zero.
tags: [multibody-dynamics, mass-matrix, crba, aba, forward-dynamics, sparse-elimination, research]
---

# The mass matrix (CRBA) and forward dynamics (ABA)

## Setup and notation

The tree notation of `c2-rnea-inverse-dynamics` is used **unchanged** ($n$, $\lambda(i)$,
$\mu(i)$, $\nu(i)$, $S_i$, $^iX_{\lambda(i)}$, $v_i$, $a_i$, $f_i$, $a_g$, $J_i$). The results
carried over:

- (previous R4-5) calling RNEA with $\dot q = 0$, $a_g = 0$, $\ddot q = e_k$ returns $M(q)e_k$.
  So $M = \sum_k J_k^\top I_kJ_k$, and this lesson computes that **much more cheaply**.
- (previous R1) $J_{i,k} = {}^iX_kS_k$ when $k$ is an ancestor of $i$ or $i$ itself, and $0$ otherwise.
- (previous (3)) the bias term of the acceleration recursion, $c_i := v_i \times v_{J_i}$.
- (previous (5)) the force recursion and $\tau_i = S_i^\top f_i$.

New symbols:

| Symbol | Meaning |
|---|---|
| $I^c_i$ | **Composite-rigid-body inertia**: the spatial inertia of the subtree $\nu(i)$ frozen into a single rigid body, in body-$i$ coordinates |
| $I^A_i$ | **Articulated-body inertia**: the apparent inertia body $i$ presents when the joints of $\nu(i)\setminus\{i\}$ are **free** |
| $p^A_i$ | The articulated bias force; $f_i = I^A_i a_i + p^A_i$ is its defining equation |
| $p_i$ | Body $i$'s own bias force, $= (v_i\times^{*})I_iv_i - f^x_i$ |
| $U_i := I^A_iS_i$ | The articulated-body inertia seen along the joint axis |
| $d_i := S_i^\top U_i = S_i^\top I^A_iS_i$ | The **apparent scalar inertia** at joint $i$ — the protagonist of this lesson |
| $u_i := \tau_i - S_i^\top p^A_i$ | The "leftover torque" at joint $i$ |
| $I^a_i := I^A_i - U_iU_i^\top/d_i$ | The inertia the parent sees after $\ddot q_i$ has been eliminated (a rank-one downdate) |
| $p^a_i := p^A_i + I^a_i c_i + U_i u_i/d_i$ | The bias force after the same elimination |
| $\mathcal{D}(i) := \nu(i)\setminus\{i\}$ | The **proper descendants** of body $i$ |
| $\mathrm{anc}(i)$ | The proper ancestors of body $i$; $\mathrm{depth}(i) := |\mathrm{anc}(i)|$ |

Assumptions: a kinematic tree, single-DOF joints, rigid bodies, and $I_i \succ 0$ for every body
(positive mass, positive-definite inertia). $M(q) \succ 0$ follows (problem P1 (a)).

## Key results

The bracketed grade is the derivation depth (D0 cited / D1 sketched / D2 full derivation /
D3 proof — see `lesson-standard.md` §2 in the track design notes).

- **R1 (closed form of the mass matrix and branch sparsity) [D2]** — define the
  composite-rigid-body inertia
  $$
  I^c_i := \sum_{k\in\nu(i)} {}^iX_k^{*}\,I_k\,{}^kX_i
  \qquad\Longleftrightarrow\qquad
  I^c_i = I_i + \sum_{j\in\mu(i)} {}^iX_j^{*}\,I^c_j\,{}^jX_i. \tag{1}
  $$
  Then, when $j$ is an ancestor of $i$ or $i$ itself,
  $$
  M_{ij} = S_i^\top\,I^c_i\;{}^iX_j\,S_j, \tag{2}
  $$
  and when $i$ and $j$ are on **different branches** ($j \notin \mathrm{anc}(i)\cup\{i\}$ and
  $i \notin \mathrm{anc}(j)$), $M_{ij} = 0$. So the structural non-zero pattern of $M$ is the
  **ancestor relation**, and the number of upper-triangular non-zeros is exactly
  $$
  \mathrm{nnz}_{\triangle}(M) = \sum_{i=1}^{n}\big(1 + \mathrm{depth}(i)\big). \tag{3}
  $$
- **R2 (CRBA is output-optimal) [D3]** — the cost of CRBA is
  $\Theta\big(\sum_i (1+\mathrm{depth}(i))\big) = \Theta(\mathrm{nnz}_\triangle(M))$:
  $\Theta(n^2)$ for a serial chain, $\Theta(n\log n)$ for a balanced binary tree, $\Theta(n)$ for
  a star. Conversely any algorithm that outputs $M$ must write all of its non-zeros, so
  $\Omega(\mathrm{nnz}_\triangle(M))$ is a lower bound. CRBA therefore does **constant work per
  non-zero**, and cannot be improved in order.
- **R3 (the articulated-body recursion = Schur elimination of $\ddot q$) [D3]** — taking
  $f_i = I^A_ia_i + p^A_i$ as the definition, **one Schur complement** — solving the child's joint
  equation for $\ddot q_j$ and eliminating it — produces the recursion:
  $$
  \ddot q_j = \frac{u_j - U_j^\top\big({}^jX_{\lambda(j)}a_{\lambda(j)} + c_j\big)}{d_j}, \tag{4}
  $$
  $$
  I^A_i = I_i + \sum_{j\in\mu(i)} {}^iX_j^{*}\,I^a_j\,{}^jX_i, \qquad
  p^A_i = p_i + \sum_{j\in\mu(i)} {}^iX_j^{*}\,p^a_j, \tag{5}
  $$
  where $I^a_j = I^A_j - U_jU_j^\top/d_j$ is a **rank-one downdate** and, exactly,
  $$
  I^a_j\,S_j = 0 \tag{6}
  $$
  — the algebraic form of the fact that a subtree offers **no resistance at all** along its own
  joint axis.
- **R4 ($d_i$ is a Schur complement of $M$) [D2]** — with $\mathcal{D} = \mathcal{D}(i)$,
  $$
  d_i = S_i^\top I^A_i S_i = M_{ii} - M_{i\mathcal{D}}\,\big(M_{\mathcal{D}\mathcal{D}}\big)^{-1} M_{\mathcal{D}i}. \tag{7}
  $$
  So $d_i$ is "the inertia felt at joint $i$ with the descendant joints left free and the
  ancestor joints locked", and $M \succ 0$ gives $0 < d_i \le M_{ii}$ (with equality exactly when
  $\mathcal{D}(i) = \varnothing$, that is at a leaf). **ABA is therefore the same thing as a
  sparse Cholesky elimination of $M$ in tree order**, and because tree order produces **no
  fill-in** it is $O(n)$ (the dependence of cost on elimination order from
  `r0-sparse-linear-algebra` shows up here in the flesh).
- **R5 ($\Theta(n)$ and no breakdown) [D3]** — if $I_i \succ 0$ for every body then
  $I^A_i \succ 0$ and $I^a_i \succeq 0$ for every $i$, hence $d_i > 0$ and the division in (4) is
  **always safe** (no pivoting needed). The cost is constant per body, so $\Theta(n)$. The
  crossover with the CRBA-plus-dense-Cholesky route ($\Theta(n^2) + \Theta(n^3)$) favours CRBA at
  small $n$, and where it sits is decided by the implementation and the hardware — the cost
  tables are RBDA §6.4 and §7.4. **[D1]**

## Derivation

### R1 — composite-rigid-body inertia and $M$

From the previous lesson's R4-5, $M = \sum_k J_k^\top I_kJ_k$, so in components

$$
M_{ij} = \sum_{k=1}^{n} J_{k,i}^\top\,I_k\,J_{k,j}.
$$

$J_{k,i} \ne 0$ is equivalent to $i \in \mathrm{anc}(k)\cup\{k\}$, that is $k \in \nu(i)$, and the
same applies to $j$, so the sum runs over $k \in \nu(i)\cap\nu(j)$. In a tree, the intersection of
two subtrees is **either one containing the other, or empty**:

- if $j \in \mathrm{anc}(i)\cup\{i\}$ then $\nu(i) \subseteq \nu(j)$ and the intersection is $\nu(i)$;
- if $i \in \mathrm{anc}(j)$ then symmetrically it is $\nu(j)$;
- otherwise (different branches) it is $\varnothing$ and $M_{ij} = 0$.

Compute the first case. With $J_{k,i} = {}^kX_iS_i$ and
$J_{k,j} = {}^kX_jS_j = {}^kX_i\,{}^iX_jS_j$,

$$
M_{ij} = \sum_{k\in\nu(i)} \big({}^kX_iS_i\big)^\top I_k\,{}^kX_i\,\big({}^iX_jS_j\big)
= S_i^\top\underbrace{\left(\sum_{k\in\nu(i)} \big({}^kX_i\big)^\top I_k\,{}^kX_i\right)}_{=\,I^c_i}\,{}^iX_jS_j,
$$

where $({}^kX_i)^\top = {}^iX_k^{*}$ (previous lesson, (2)), so the bracket is the $I^c_i$ of (1).
That is (2). The recursive form of $I^c_i$ follows by substituting
$\nu(i) = \{i\} \cup \bigcup_{j\in\mu(i)}\nu(j)$ into the sum and factoring with
$^iX_k^{*} = {}^iX_j^{*}\,{}^jX_k^{*}$.

**Geometric reading**: $I^c_i$ is "the inertia obtained by welding everything below joint $i$ into
one rigid body". $M_{ii} = S_i^\top I^c_iS_i$ is exactly that reading — the inertia felt at joint
$i$ **with all other joints locked**. (Contrast with the $d_i$ of R4, which leaves the descendants
**free**.)

(3) is pure counting. The non-zero positions of the upper triangle are the pairs $(i, j)$ with
$j \in \mathrm{anc}(i)\cup\{i\}$, and for each $i$ there are $1 + \mathrm{depth}(i)$ of them.

> **Caution**: (3) counts **structural** non-zeros. For a particular geometry an entry may vanish
> numerically — if the joint axes are orthogonal and the centre of mass lies on an axis, $M_{ij}$
> can come out zero by accident. The cost of the algorithm is decided by the structure, so R2
> counts structurally.

### CRBA

```python
def crba(model, q):
    """Composite-rigid-body mass matrix. Returns M (n, n), symmetric positive definite."""
    n = model.n
    Xup = model.Xup(q)
    Ic = [Ii.copy() for Ii in model.I]
    for i in range(n - 1, -1, -1):  # (1): accumulate composite inertias leaf -> root
        p = model.parent[i]
        if p >= 0:
            Ic[p] = Ic[p] + Xup[i].T @ Ic[i] @ Xup[i]
    M = np.zeros((n, n))
    for i in range(n):
        F = Ic[i] @ model.S[i]  # a force in body-i coordinates
        M[i, i] = model.S[i] @ F
        j = i
        while model.parent[j] >= 0:  # (2): walk up the ancestors, carrying F
            F = Xup[j].T @ F  # move the force into the parent's coordinates
            j = model.parent[j]
            M[i, j] = M[j, i] = model.S[j] @ F
    return M
```

The crux is that `F` is an element of force space, so it is moved with `Xup[j].T` (that is,
$X^{*}$) — that one line evaluates the $S_i^\top I^c_i\,{}^iX_j$ of (2) in a **single** left-to-right
sweep. The inner while loop runs $\mathrm{depth}(i)$ times, which makes the total cost equal to (3).

### R3 — the articulated-body inertia recursion

**Start from a clear definition.** When body $i$ and its **descendant joints are free** (the
descendant joints carry only their given $\tau_j$), there is an affine relation between the force
$f_i$ applied to body $i$ and the acceleration $a_i$ of body $i$:

$$
f_i = I^A_i\,a_i + p^A_i. \tag{8}
$$

**That (8) holds at all** is the conclusion of the induction. At a leaf there are no descendants,
so $I^A_i = I_i$ and $p^A_i = p_i$ make the previous lesson's (5) read as (8). Now assume (8)
holds for every child $j$ of body $i$ and establish (8) at body $i$.

**Step 1 — the child's joint equation.** Abbreviating the child's acceleration recursion
(previous lesson, (3)) with $a'_j := {}^jX_{\lambda(j)}a_{\lambda(j)} = {}^jX_i\,a_i$,

$$
a_j = a'_j + c_j + S_j\ddot q_j. \tag{9}
$$

The torque at joint $j$ is $\tau_j = S_j^\top f_j$, and applying (8) at $j$,

$$
\tau_j = S_j^\top\big(I^A_j(a'_j + c_j + S_j\ddot q_j) + p^A_j\big)
= U_j^\top(a'_j + c_j) + d_j\,\ddot q_j + S_j^\top p^A_j.
$$

Writing $u_j = \tau_j - S_j^\top p^A_j$ and solving for $\ddot q_j$ gives (4). **This is the Schur
elimination** — the unknown $\ddot q_j$ has been removed using the one equation that contains only
it. It needs $d_j \ne 0$, which R5 guarantees.

**Step 2 — put the elimination back into $f_j$.** Substitute (4) into (8) with (9):

$$
f_j = I^A_j(a'_j + c_j) + U_j\ddot q_j + p^A_j
= I^A_j(a'_j + c_j) + \frac{U_j\big(u_j - U_j^\top(a'_j+c_j)\big)}{d_j} + p^A_j.
$$

Collecting the terms that multiply $a'_j + c_j$ reveals the rank-one downdate:

$$
f_j = \underbrace{\left(I^A_j - \frac{U_jU_j^\top}{d_j}\right)}_{=\,I^a_j}(a'_j + c_j)
  + p^A_j + \frac{U_ju_j}{d_j}
= I^a_j\,a'_j + \underbrace{\Big(I^a_jc_j + p^A_j + \frac{U_ju_j}{d_j}\Big)}_{=\,p^a_j}. \tag{10}
$$

**Step 3 — add it to the parent's force balance.** In the previous lesson's (5) the reaction body
$i$ receives from a child is $^iX_j^{*}f_j$, and since $a'_j = {}^jX_ia_i$, substituting (10) gives

$$
f_i = I_ia_i + p_i + \sum_{j\in\mu(i)} {}^iX_j^{*}\big(I^a_j\,{}^jX_i\,a_i + p^a_j\big)
= \Big(I_i + \sum_j {}^iX_j^{*}I^a_j\,{}^jX_i\Big)a_i + \Big(p_i + \sum_j {}^iX_j^{*}p^a_j\Big),
$$

so (8) holds at body $i$ too, with the coefficients of (5). The induction is complete.

**Checking (6).** $I^a_jS_j = I^A_jS_j - \dfrac{U_j(U_j^\top S_j)}{d_j}
= U_j - \dfrac{U_jd_j}{d_j} = 0$. One line, but it means a lot: after $\ddot q_j$ has been
eliminated, the inertia the parent sees is **exactly singular along the joint axis**. Physically,
"a free joint transmits no force in that direction"; numerically, "$I^a_j$ is positive
semidefinite but not positive definite" (condition 4 of the reproduction task).

### ABA

```python
def aba(model, q, qd, tau, a_grav):
    """Articulated-body forward dynamics. Returns qdd (n,)."""
    n = model.n
    Xup = model.Xup(q)
    S = model.S
    v, c = [None] * n, [None] * n
    IA = [Ii.copy() for Ii in model.I]
    pA = [None] * n
    for i in range(n):  # pass 1: velocities, bias forces
        vJ = S[i] * qd[i]
        p = model.parent[i]
        v[i] = vJ if p < 0 else Xup[i] @ v[p] + vJ
        c[i] = np.zeros(6) if p < 0 else crm(v[i]) @ vJ
        pA[i] = crf(v[i]) @ IA[i] @ v[i] - model.fx[i]
    U, d, u = [None] * n, np.zeros(n), np.zeros(n)
    for i in range(n - 1, -1, -1):  # pass 2: articulated inertias, leaf -> root
        U[i] = IA[i] @ S[i]
        d[i] = S[i] @ U[i]
        u[i] = tau[i] - S[i] @ pA[i]
        p = model.parent[i]
        if p >= 0:
            Ia = IA[i] - np.outer(U[i], U[i]) / d[i]  # (10): the rank-1 downdate
            pa = pA[i] + Ia @ c[i] + U[i] * (u[i] / d[i])
            IA[p] = IA[p] + Xup[i].T @ Ia @ Xup[i]
            pA[p] = pA[p] + Xup[i].T @ pa
    a, qdd = [None] * n, np.zeros(n)
    for i in range(n):  # pass 3: accelerations, root -> leaf
        p = model.parent[i]
        ap = (Xup[i] @ (-a_grav) if p < 0 else Xup[i] @ a[p]) + c[i]
        qdd[i] = (u[i] - U[i] @ ap) / d[i]  # (4)
        a[i] = ap + S[i] * qdd[i]
    return qdd
```

All three passes do constant work per body. Gravity enters exactly as in RNEA, through
$a_0 = -a_g$.

### R4 — $d_i$ is a Schur complement of $M$

Read (7) as linear algebra. Keep only joint $i$ and its proper descendants
$\mathcal{D} = \mathcal{D}(i)$, and **lock the ancestor joints** ($\ddot q_k = 0$ for
$k \in \mathrm{anc}(i)$). The relevant block of the equation of motion is

$$
\begin{bmatrix} M_{ii} & M_{i\mathcal{D}} \\ M_{\mathcal{D}i} & M_{\mathcal{D}\mathcal{D}}\end{bmatrix}
\begin{bmatrix} \ddot q_i \\ \ddot q_{\mathcal{D}}\end{bmatrix}
= \begin{bmatrix} \tau_i - b_i \\ \tau_{\mathcal{D}} - b_{\mathcal{D}}\end{bmatrix}
$$

(with $b$ the bias and gravity terms), and leaving the descendant joints **free** means that
$\tau_{\mathcal{D}}$ is a given value. Solving the second block row for $\ddot q_{\mathcal{D}}$ and
substituting into the first gives

$$
\underbrace{\Big(M_{ii} - M_{i\mathcal{D}}M_{\mathcal{D}\mathcal{D}}^{-1}M_{\mathcal{D}i}\Big)}_{\text{Schur complement}}\ddot q_i
= (\tau_i - b_i) - M_{i\mathcal{D}}M_{\mathcal{D}\mathcal{D}}^{-1}(\tau_{\mathcal{D}} - b_{\mathcal{D}}).
$$

Meanwhile ABA's (4) gives, in the same situation, $d_i\,\ddot q_i = u_i - U_i^\top(a'_i + c_i)$,
whose coefficient of $\ddot q_i$ is $d_i$. The two are **the same one-dimensional equation in the
same unknown**, so the coefficients must agree — that is (7). ($M_{\mathcal{D}\mathcal{D}}$ is
invertible because it is a principal submatrix of $M \succ 0$.)

So $d_i$ is **positive** directly from the positive definiteness of $M$ (a Schur complement of a
positive-definite matrix is positive definite), and since
$M_{i\mathcal{D}}M_{\mathcal{D}\mathcal{D}}^{-1}M_{\mathcal{D}i} \ge 0$, also $d_i \le M_{ii}$. At
a leaf, $\mathcal{D} = \varnothing$ and $d_i = M_{ii}$ **exactly**.

> **(7) numerically**: at a random configuration of the 7-DOF serial arm, computing ABA's $d$ and
> the Schur complement of $M$ separately and comparing gives a maximum error of
> $4.4\times10^{-16}$. For the two-link arm it can even be checked by hand:
> $d_1 = M_{11} - M_{12}^2/M_{22} = 0.689405914278$ and $d_2 = M_{22} = 0.16$.

**What this identity means.** ABA **eliminates the tree-structured $M$ in leaf-to-root order**,
and each elimination is the rank-one downdate (10). Leaf-to-root order on a tree adds **no new
edges** to the elimination graph (eliminating a child affects only its single parent), so the
fill-in is zero and the cost stays at $\Theta(n)$. Eliminating the same $M$ in an **arbitrary**
order creates fill-in and costs more — precisely the phenomenon the COLAMD experiment of
`r0-sparse-linear-algebra` is about, except that here the physical structure hands us the optimal
order for free. RBDA ch.7 develops this view.

## Proof sketch

### R2 — CRBA is output-optimal

**Hypotheses** H1: a kinematic tree with $n$ single-DOF joints and constant-size data per body.
H2: real arithmetic has unit cost. H3: all of $M$ (or its upper triangle) must be output.
**Conclusions** C1: the cost of CRBA is $\Theta\big(\sum_i(1+\mathrm{depth}(i))\big)$.
C2: any algorithm has the same lower bound, so CRBA is optimal in order.

**Strategy**: count loops for the upper bound; argue from output size for the lower bound. The
shape-dependent values are a combinatorial calculation of $\sum_i\mathrm{depth}(i)$.

1. **Upper bound.** The accumulation loop of (1) does constant work per body over $n$ bodies, so
   $\Theta(n)$. The double loop of (2) runs the while loop $\mathrm{depth}(i)$ times per body with
   constant work each ($X^\top F$ plus an inner product), so
   $\Theta\big(\sum_i \mathrm{depth}(i)\big)$. Together,
   $\Theta\big(\sum_i(1+\mathrm{depth}(i))\big)$.
2. **It matches the output size.** By (3) that quantity is exactly
   $\mathrm{nnz}_\triangle(M)$ — CRBA does **constant work per upper-triangular non-zero**.
3. **Lower bound.** By H3 the algorithm must write $\mathrm{nnz}_\triangle(M)$ numbers, so
   $\Omega(\mathrm{nnz}_\triangle(M))$. (A stronger bound is available: a structurally non-zero
   $M_{ij}$ is actually non-zero for generic geometry and depends on $q$, so producing its value
   requires reading the relevant $q_k$.)
4. **Values by tree shape.** A serial chain has $\mathrm{depth}(i) = i-1$, so
   $\sum_i(1+\mathrm{depth}(i)) = n(n+1)/2 = \Theta(n^2)$. A balanced binary tree has depth
   $O(\log n)$, so $\Theta(n\log n)$. A depth-one star gives $\Theta(n)$ — **there $M$ is nearly
   diagonal and CRBA is linear**.
5. **What is *not* optimal.** The constant, and the question "must $M$ be formed at all". If only
   forward dynamics is wanted, ABA never forms $M$ and is $\Theta(n)$ (R5) — a lower order than
   CRBA's $\Theta(n^2)$ on a serial chain. Use CRBA only when there is a **reason to need $M$**
   (control design, the second-order term of an optimisation, the $\Lambda$ of a contact solver).

**Delete a hypothesis**: without H3, steps 2 and 3 are moot — if the output is $M^{-1}\tau$ rather
than $M$, the lower bound drops to $\Omega(n)$ and ABA attains it. Without the tree in H1, the
zero pattern of $M$ is not decided by the ancestor relation and (3) does not hold at all.

### R5 — $I^A_i \succ 0$, $d_i > 0$, and $\Theta(n)$

**Hypotheses** H1: $I_i \succ 0$ for every $i$ (mass $m_i > 0$, $\bar I_{C,i} \succ 0$).
H2: a kinematic tree with single-DOF joints. **Conclusions** C1: $I^A_i \succ 0$ and
$I^a_i \succeq 0$ for every $i$ (with rank deficiency exactly one, null space
$\mathrm{span}(S_i)$). C2: hence $d_i > 0$ and ABA is always defined, without pivoting.
C3: the cost is $\Theta(n)$.

**Strategy**: leaf-to-root induction. The two supporting facts are "the Schur complement of a
positive-definite matrix is positive semidefinite" (the Schur complement lemma) and "congruence
preserves positive definiteness" (previous lesson, R2).

1. **Base (leaf).** If $\mu(i) = \varnothing$ then $I^A_i = I_i \succ 0$ by H1.
2. **$d_i > 0$.** Since $I^A_i \succ 0$ and $S_i \ne 0$, $d_i = S_i^\top I^A_iS_i > 0$. So the
   division in (4) and the downdate in (10) are defined.
3. **$I^a_i \succeq 0$ and its null space.** $I^a_i = I^A_i - U_iU_i^\top/d_i$ is the Schur
   complement with respect to $d_i$ of the block matrix
   $\begin{bmatrix} I^A_i & U_i \\ U_i^\top & d_i\end{bmatrix}$, and that block matrix is a
   congruence of $I^A_i$ by $\begin{bmatrix}\mathbb{1} \\ S_i^\top\end{bmatrix}$, hence positive
   semidefinite. So $I^a_i \succeq 0$. By (6), $S_i$ lies in the null space, and the rank
   deficiency is no more than one because the downdate has rank one.
4. **Induction step.** In (5), $I^A_i = I_i + \sum_{j\in\mu(i)}{}^iX_j^{*}I^a_j\,{}^jX_i$, and by
   the previous lesson's R2 each term
   $^iX_j^{*}I^a_j\,{}^jX_i = ({}^jX_i)^\top I^a_j({}^jX_i)$ is a congruence of a positive
   semidefinite matrix and so is positive semidefinite. Positive definite plus positive
   semidefinite is positive definite, so $I^A_i \succeq I_i \succ 0$. Climbing to the root gives
   C1 and C2.
5. **$\Theta(n)$ (C3).** Passes 1 and 3 are constant per body (the same count as the previous
   lesson's R5); pass 2 does per body one $U_i$ (one $6\times6$ product), one $d_i$ (inner
   product), one rank-one downdate (one $6\times6$ outer product) and one $X^\top I^a X$
   (congruence, two $6\times6$ products) — all constants independent of $n$. Each body is visited
   three times, so $\Theta(n)$. The lower bound is $\Omega(n)$ (the output $\ddot q$ has $n$
   components), so this is order-optimal.

**Delete a hypothesis**: dropping $m_i > 0$ from H1 (a massless "virtual body") makes $I_i$
singular, so step 4 gives only positive semidefiniteness, and a massless leaf gives $d_i = 0$ and
ABA **divides by zero**. In practice a zero-mass link in a URDF blows up at exactly this point, so
an implementation must merge such a link into its parent or check a lower bound on $d_i$ (see the
diagnosis table of the reproduction task). Without the tree in H2 the child sum of (5) is not even
defined.

> **Caution — numerical versus exact positive definiteness.** Step 3 gives
> $I^a_i \succeq 0$, but in floating point the smallest eigenvalue can come out negative at the
> $-10^{-16}$ level (measured in the author's environment:
> $\lambda_{\min}(I^a) = -7.2\times10^{-16}$). That is the round-off of an eigenvalue which (6)
> says must be **exactly** zero. Trying to confirm positive definiteness by running Cholesky on
> $I^a_i$ will fail, so the check must be "$\lambda_{\min} \ge -\epsilon$ and
> $I^a_iS_i \approx 0$".

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ one hour /
★★★ a day or more.

**P1 (derivation, ★★, R1)** (a) Prove $M(q) \succ 0$ from $M = \sum_k J_k^\top I_kJ_k$, including
the equality condition — for what mechanism does $M$ become singular? (b) Derive the recursive
form of (1) from the sum form. (c) For a star tree ($n$ bodies all attached directly to the base),
check whether $M$ is diagonal, and if there is a case where it is **not**, say which.
*Solution sketch*: (a) use $v^\top Mv = \sum_k \lVert\cdot\rVert^2_{I_k} \ge 0$ with equality
condition "every body's spatial velocity is zero" = "$J\dot q = 0$"; if the forward kinematics is
non-singular then $\dot q = 0$. (c) is a trap — on a star tree the $M_{ij}$ of different branches
are **exactly** zero by R1, but with a floating base the branches become coupled again.

**P2 (derivation, ★★, R3·R4)** (a) Re-derive the $p^a_j$ of (10) with no missing steps, and in
particular say why the term is $I^a_jc_j$ and **not** $I^A_jc_j$. (b) Check that (7) degenerates to
$d_i = M_{ii}$ at a leaf, by comparing with (2). (c) Compute $d_1 = M_{11} - M_{12}^2/M_{22}$ by
hand for the two-link arm and compare against the published number.
*Solution sketch*: the crux of (a) is to treat $a'_j + c_j$ as **one bundle** that the downdated
inertia multiplies. Separating $c_j$ and multiplying it by $I^A_j$ drops the term
$U_jU_j^\top c_j/d_j$ and is wrong whenever $\dot q \ne 0$ — condition 3 of the reproduction task
catches this.

**P3 (proof, ★★★, R2)** (a) For a complete binary tree of depth $h$ ($n = 2^h - 1$), find
$\sum_i(1+\mathrm{depth}(i))$ in closed form and show it is $\Theta(n\log n)$. (b) For a given $n$,
find the tree shapes that **maximise** and **minimise** $\sum_i\mathrm{depth}(i)$, and argue that
those values bound the cost of CRBA above and below. (c) Sharpen the lower bound of R2 step 3 into
the stronger form "producing one non-zero of $M$ requires reading the relevant $q_k$", and state
what assumption on the geometry that argument needs.
*Strategy and key inequality*: for (a) use that depth $d$ holds $2^d$ nodes and evaluate
$\sum_d d\,2^d$. In (b) the maximum is the serial chain and the minimum the star. The point of (c)
is how to formalise "generic geometry" (which measure-zero set is excluded). The expansion is
withheld.

**P4 (proof, ★★★, R5)** (a) Prove the Schur complement lemma: if $A \succ 0$ and
$\begin{bmatrix}A & b\\ b^\top & c\end{bmatrix} \succeq 0$ then $A - bb^\top/c \succeq 0$.
(b) Write down in equations where and how ABA breaks when a leaf link has zero mass, and argue
whether merging that link into its parent gives **exactly** the same dynamics. (c) Say how (4)
changes when a joint has friction or damping $-b_i\dot q_i$ (hint: it is absorbed into $\tau_i$ —
then why does $d_i$ not change?).
*Strategy and key inequality*: for (a) substitute
$\begin{bmatrix}x \\ -b^\top x/c\end{bmatrix}$ into the quadratic form. For (b), a massless leaf
has $I^A_i = 0$ and hence $d_i = 0$, and the equivalence of merging follows from that link giving
no inertia along the joint axis. The expansion is withheld.

**P5 (numerical, ★, R1·R3·R4)** For the two-link arm of `c2-rnea-inverse-dynamics` P4 (the same
model), at $q = (0.3, -0.7)$, $\dot q = (0.5, 1.2)$, $\tau = (2.0, -0.5)$ and gravity $9.81$ along
$-y$, find $M(q)$, the bias-plus-gravity term $b = C\dot q + g$, ABA's $\ddot q$, and $d_1$, $d_2$.
*Answer* (tolerance $10^{-9}$):
$M(q) = \begin{bmatrix} 1.427124249897 & 0.343562124948 \\ 0.343562124948 & 0.16 \end{bmatrix}$,
$b = (18.080196104584,\; 3.575590279233)$,
$\ddot q = (-10.630646761366,\; -2.645641802023)$,
$d_1 = 0.689405914278$, $d_2 = 0.16$.
*Checks*: (a) $M\ddot q + b = \tau$ to within $10^{-12}$; (b) $d_2 = M_{22}$ **exactly** (a leaf);
(c) $d_1 = M_{11} - M_{12}^2/M_{22}$ to within $10^{-12}$; (d) $1/(M^{-1})_{11} = d_1$ (the same
number read differently).

**P6 (implementation, ★★, R1·R3)** Write `crba(model, q)` and
`aba(model, q, qd, tau, a_grav)`.
*Rubric*: (a) reproduces the numbers of P5 to within $10^{-9}$; (b) `crba` gives
$\lVert M - M^\top\rVert_\infty = 0$ **without forcing symmetry** (computing the upper triangle and
assigning it to the lower makes them bitwise equal); (c) on a branching tree the $M_{ij}$ of
different branches are **exactly** zero; (d) `aba` agrees with
`solve(crba(q), tau - rnea(q, qd, 0))` to within $10^{-12}$; (e) unit tests check every
$d_i > 0$ and $\lVert I^a_iS_i\rVert_\infty < 10^{-14}$; (f) a model with a zero-mass link raises a
**clear exception** (silently returning `inf`/`nan` does not pass).

**P7 (paper, ★★, R2·R5)** Read Walker & Orin (1982) and Featherstone (1983) and write: (a) what
cost each paper claims and which step of R2 and R5 here that claim corresponds to; (b) why
Methods 1 and 2 of the 1982 paper are slow, in the vocabulary of this lesson; (c) two **missing
variables** in the cost comparison of the two papers (hint: caches, branch structure).
*Rubric*: for (a), noting that the 1982 paper gives only an upper bound and the 1983 paper too, so
**neither addresses a lower bound**, passes. For (c), naming at least one of memory access pattern
and tree shape concretely passes. Writing only "the hardware was different" does not.

## Paper reading

**Two must-reads.** One from 1982 and one from 1983 — a year apart, claiming $O(n^2)$ and $O(n)$
for the same problem. Explaining to yourself **why two answers coexist** is the reading goal of
this lesson (the answer is in step 5 of R2 and the crossover of R5). Write a one-page note on each
with the ten fixed questions below (`lesson-standard.md` §5). Read in three passes and concentrate
on questions 4, 5 and 9 in the third pass.

1. **Walker & Orin, "Efficient Dynamic Computer Simulation of Robotic Mechanisms"
   (1982, ASME J. Dyn. Syst. Meas. Control)** — role: `seminal`.
   <https://doi.org/10.1115/1.3139699>
   Which sections and why: the whole section that presents and compares Methods 1-4.
   **Method 3 is CRBA**, corresponding one-to-one with (1) and (2) here. Why Methods 1 and 2 are
   slow, restated in the vocabulary of R2, is "they build $M$ at more than constant cost per
   non-zero".
   Extra questions: (a) what metric did the authors use for the comparison, and is that metric
   specific to 1982 hardware? (b) is there anything **different** between the authors' Method 3
   and the CRBA of this lesson (branch handling, choice of coordinates)?
2. **Featherstone, "The Calculation of Robot Dynamics Using Articulated-Body Inertias"
   (1983, IJRR)** — role: `seminal`. <https://doi.org/10.1177/027836498300200102>
   Which sections and why: the ones that define the articulated-body inertia and set up the
   recursion. Read them **line by line** against the derivation of R3 here. How the author
   justifies (8) matters especially.
   Extra questions: (a) where does the author guarantee $d_i > 0$, or is it assumed implicitly?
   (b) is there anything in the paper corresponding to R4 here (= a Schur complement of $M$), and
   if not, why do you think that view was added only later (RBDA ch.7)? (c) when does the constant
   of the $O(n)$ claim actually beat the $O(n^2)$ CRBA — does the paper answer that?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) independent and dependent variables and baselines — were the baselines tuned fairly?
(6) do the metrics match the claim; are variance and seeds reported? (7) what is missing for
reproduction? (8) if it were wrong, which assumption would you suspect first? (9) compute and
memory complexity, and real-time feasibility. (10) what would you change to go beyond it in a year?

## Reproduction task

**Tier R1 (numerical check).** Compute budget: one notebook CPU core, under two minutes, numpy
only. Memory under 200 MB.

The `crba` and `aba` of P6 must satisfy **all four** of the following. Fix the random seed
(`np.random.default_rng(7)`).

1. **Two independent routes to $M$ agree** — over $10^3$ random configurations of the 7-DOF serial
   arm (the **same model** as the previous lesson's reproduction task),
   $$
   \max\big\lVert M^{\text{CRBA}} - \textstyle\sum_k J_k^\top I_kJ_k \big\rVert_\infty < 10^{-14},
   \qquad \big\lVert M^{\text{CRBA}} - (M^{\text{CRBA}})^\top \big\rVert_\infty = 0,
   $$
   and $\lambda_{\min}(M) > 0$. (The symmetry error must be **exactly zero** — if you computed the
   upper triangle and assigned it to the lower, they are bitwise equal. A value of $10^{-16}$ means
   you are computing it twice.)
2. **$M$ versus finite-differenced inverse dynamics** (the criterion the blueprint specifies) — on
   the same model, for
   $M^{\text{fd}}_{\cdot k} = \dfrac{\mathrm{rnea}(q, 0, h e_k) - \mathrm{rnea}(q, 0, -h e_k)}{2h}$
   with $h = 10^{-6}$ and gravity off,
   $$
   \max\big\lVert M^{\text{CRBA}} - M^{\text{fd}} \big\rVert_\infty < 10^{-8}.
   $$
   > Measured in the author's environment: $3.2\times10^{-9}$. This condition is dominated by the
   > **limits of finite differencing**, so sweep $h$ over $10^{-4} \dots 10^{-8}$ and confirm the
   > V curve.
3. **ABA versus the $M^{-1}$ route, and the RNEA round trip** — over $10^3$ random
   $(q, \dot q, \tau)$,
   $$
   \max\big\lVert \mathrm{aba}(q,\dot q,\tau) - \mathrm{solve}\big(M, \tau - \mathrm{rnea}(q,\dot q,0)\big)\big\rVert_\infty < 10^{-12},
   $$
   $$
   \max\big\lVert \mathrm{rnea}\big(q, \dot q, \mathrm{aba}(q,\dot q,\tau)\big) - \tau \big\rVert_\infty < 10^{-12}.
   $$
   > Measured: $8.1\times10^{-15}$ and $1.4\times10^{-14}$.
   > Test with $\dot q \ne 0$ without fail — at $\dot q = 0$ the bug of P2 (a) stays hidden.
4. **Structure checks (this lesson's own condition)** — confirm all four.
   (a) **$d_i$ is a Schur complement of $M$**, (7): for a serial chain
   $\mathcal{D}(i) = \{i+1,\dots,n\}$, so
   $\max_i|d_i - (M_{ii} - M_{i\mathcal{D}}M_{\mathcal{D}\mathcal{D}}^{-1}M_{\mathcal{D}i})| < 10^{-12}$
   (measured $4.4\times10^{-16}$), together with $0 < d_i \le M_{ii}$ and $d_n = M_{nn}$
   **exactly**.
   (b) **$I^a_iS_i = 0$**, (6): $\max_i\lVert I^a_iS_i\rVert_\infty < 10^{-14}$ (it should be
   exactly zero).
   (c) **$I^A_i \succ 0$, $I^a_i \succeq 0$**: $\lambda_{\min}(I^A_i) > 0$ and
   $\lambda_{\min}(I^a_i) > -10^{-14}$ (measured $-7.2\times10^{-16}$ — **a negative value is
   normal**, and you should confirm together with $I^a_iS_i$ that it is the round-off of the
   exactly-zero eigenvalue of (6)).
   (d) **Branch sparsity**, R1: on a four-body branching tree (parents $[-1, 0, 0, 2]$, axes
   $z, y, z, x$, generic offsets and inertias), the $M_{ij}$ of different branches must be
   **exactly** zero and the number of non-zeros must equal
   $2\sum_i(1+\mathrm{depth}(i)) - n$ from (3) (here, 12).
   **Avoid degenerate geometry** where the axes are orthogonal and the centres of mass lie on the
   axes — in such a model structurally non-zero entries also come out zero by accident and (d)
   becomes meaningless.

**Input data**: no external data needed. The 7-DOF model uses the same generating script (and the
same seed) as the previous lesson. The offsets of the branching tree are generated as general
transforms with rotation mixed in.

**Baselines** (at least one):
- First choice: the Jacobian route of condition 1 and the $M^{-1}$ route of condition 3 — both
  independent of CRBA and ABA.
- Second choice: the finite-differenced inverse dynamics of condition 2 (using the previous
  lesson's `rnea` as the answer key).
- Optional check (not required to pass): agreement with `pinocchio`'s `pin.crba` and `pin.aba` to
  within $10^{-10}$ (mind the component order), or with Featherstone's `HandC`, `FDab` and `FDcrb`
  in Octave.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The symmetry error of condition 1 is $10^{-16}$ | $M_{ij}$ and $M_{ji}$ were each computed | Check in the code that only the upper triangle is computed and assigned with `M[j, i] = M[i, j]` |
| $M$ is symmetric but wrong | The accumulation of (1) was done root-to-leaf | Confirm it starts at the leaves (that is, `range(n-1, -1, -1)`) |
| Condition 3 passes only at $\dot q = 0$ | $c_j$ was multiplied by $I^A_j$ instead of $I^a_j$ in (10) | Replace $I^a_jc_j$ with $I^A_jc_j$ in $p^a_j$ and see whether the error matches |
| Condition 4 (b) sits at the $10^{-10}$ level | $d_i$ was computed by some formula other than $S_i^\top I^A_iS_i$ | Check that $U_i = I^A_iS_i$ is formed **first** and then $d_i = S_i^\top U_i$ |
| $\lambda_{\min}(I^a) \approx -10^{-8}$ in condition 4 (c) | $I^a_i$ was not symmetrised — subtracting an outer product introduces asymmetry | Take eigenvalues of $(I^a + (I^a)^\top)/2$ and print the asymmetry $\lVert I^a - (I^a)^\top\rVert$ |
| Condition 4 (d) counts too many non-zeros | Branches were decided by index order rather than the ancestor relation | Build the ancestor sets explicitly from the parent array and compare patterns |
| `nan` or `inf` | A zero-mass link makes $d_i = 0$ | Check $\lambda_{\min}$ and $m_i$ of every $I_i$ at load time and raise |
| ABA is slower than CRBA as $n$ grows | The overhead of numpy's $6\times6$ operations dominates the constant | Count the number of **calls** in each algorithm to confirm the order, and compare wall-clock only for $n \ge 50$ |

## Open problems

- **(open problem) The trade-off between elimination order and conditioning** — ABA is optimal in
  the sense that tree order makes the fill-in zero, but it is not the **numerically** optimal
  order. In sparse linear algebra there is a trade-off between minimum fill-in and stability
  (pivoting), and for systems with large mass ratios tree order can worsen the conditioning. There
  is no theory in multibody dynamics for "an ordering that looks at fill-in and conditioning
  together". Current approaches: the sparse-factorisation reformulation (RBDA ch.7) and
  preconditioned iterative solvers. What is missing: a procedure that predicts conditioning from
  the mechanism's structure and chooses the ordering — the same wall as the first open problem of
  `c2-spatial-vector-algebra`.
- **(open problem) Cost lower bounds for the algorithms that must form $M$** — if only forward
  dynamics is wanted, ABA is $\Theta(n)$; but the operational-space inertia $\Lambda$ (the next
  lesson), the Delassus operator of a contact LCP and the Hessian of a second-order optimisation
  all require $M$ or part of it. The lower bound for "obtaining $\Lambda$ with $k$ constraints or
  contacts" is unknown in both $k$ and $n$, and practice uses only upper bounds of the form
  $O(nk + k^3)$. Current approaches: efficient operational-space inertia algorithms (the
  divide-and-conquer family of
  [Featherstone 1999](https://doi.org/10.1177/02783649922066619)) and convex relaxations of
  contact ([Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751)). What is missing: a lower
  bound in $k$.
- **(open problem) Algorithm choice for batched, differentiable dynamics** — trajectory
  optimisation and reinforcement learning call forward dynamics **and its derivatives** on
  thousands of states at once. In that workload memory access and vectorisability dominate the
  $\Theta(n)$-versus-$\Theta(n^2)$ order, and the CRBA route, which forms $M$ explicitly, can even
  give derivatives more easily. There is no model of which regime favours which. Current
  approaches: analytical derivatives
  ([Carpentier & Mansard 2018](https://doi.org/10.15607/RSS.2018.XIV.038)) and GPU
  implementations of batched dynamics. The question returns in
  `c2-dynamics-derivatives-sysid`.

## Concept check

Run `rc quiz c2-crba-aba`. The quiz is for **concept checking only**; the real work is the problem
set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: when $M_{ij} = 0$ is structurally guaranteed; the cost order of CRBA on a
serial chain; the value of $I^a_jS_j$; what $d_i$ equals in terms of $M$; and which facts the
guarantee $d_i > 0$ actually uses.

## How to study this stage

1. **Lay out just two equations from the previous lesson (15 min)** —
   $M = \sum_kJ_k^\top I_kJ_k$ and $J_{i,k} = {}^iX_kS_k$ (for an ancestor). R1 is nothing but
   **working out the range of the sum** from those two.
2. **Draw a tree and colour in the zero pattern by hand (30 min)** — sketch a branching tree of
   about six bodies and colour the non-zero positions of a $6\times6$ grid, counting (3) yourself.
   Then straighten the same tree into a chain and watch the grid fill up. That **the cost of CRBA
   depends on the shape** becomes visible.
3. **Write R3 from a blank page (90 min)** — write (8) as the definition and expand steps 1, 2 and
   3 (joint equation → Schur elimination → lift to the parent) in order. Where you get stuck is
   almost always step 2, failing to bundle $a'_j + c_j$ and separating out $c_j$ instead (that is
   exactly the point of problem P2 (a)).
4. **Confirm R4 in two directions (50 min)** — first as linear algebra (Schur complement), then
   **numerically**: compute $d_1 = M_{11} - M_{12}^2/M_{22}$ by hand for the two-link arm and match
   it against the published number. The moment that identity checks out, "ABA is sparse
   elimination" stops being a metaphor and becomes an equation.
5. **Implement it wrongly first (70 min)** — when writing P6, make three variants: (a) $I^A_jc_j$
   (before the downdate), (b) root-to-leaf accumulation, (c) $M_{ij}$ and $M_{ji}$ computed
   separately, and tabulate which condition of the reproduction task breaks. The first three rows
   of the diagnosis table are that experiment.
6. **Finish the reproduction task (120 min)** — condition 4 is the heart of this lesson. In
   particular, see for yourself in (c) that $\lambda_{\min}(I^a)$ **coming out negative is
   normal**, and confirm with $I^a S$ that it is the round-off of the exact zero of (6). The habit
   of "verifying positive definiteness with Cholesky" has to break once, here.
7. **Read the two papers a year apart (120 min)** — read the Method 1-4 comparison of Walker &
   Orin 1982 first to see "why making $M$ cheaply was the problem", then see in Featherstone 1983
   the turn to "not building $M$ at all". Note in your write-up that neither paper addresses a
   lower bound (P7 (a)).
8. **End with what cannot be done (20 min)** — pick the elimination-order open problem and write a
   paragraph on why tree order, optimal for fill-in, may not be optimal for conditioning. Putting
   it beside the COLAMD experiment of `r0-sparse-linear-algebra` sharpens the question.

**Passing bar**: you can write (1), (2), (4), (5) and (10) from a blank page; you can state the
three steps of R3 and the induction of R5; you have a `crba` and an `aba` that pass all four
conditions of the reproduction task; and you have one-page notes on both papers.
