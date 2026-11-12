---
id: c2-rnea-inverse-dynamics
lang: en
title: Recursive Newton-Euler (RNEA)
summary: >-
  Derive the inverse dynamics of a kinematic tree as a forward kinematic recursion and a backward
  force recursion, show that the bias term of the acceleration recursion comes from the
  non-integrability (the Lie bracket) of the spatial Jacobian, and treat at the level of proof
  both that the output of RNEA is exactly the generalised force (equivalence with Euler-Lagrange)
  and that its $\Theta(n)$ cost is order-optimal.
objectives:
  - Derive the acceleration recursion from the velocity recursion with no missing steps and explain where the bias term $v_i \times S_i\dot{q}_i$ comes from.
  - Derive the backward force recursion and $\tau_i = S_i^\top f_i$, the first from force balance and the second from virtual work.
  - Prove by unrolling the recursion that the output of RNEA is $\sum_j (\partial v_j/\partial \dot{q}_k)^\top f_j$.
  - Write $\partial_{q_l} J_{\cdot k} - \partial_{q_k} J_{\cdot l} = [J_{\cdot k}, J_{\cdot l}]$ for the spatial Jacobian and state the origin of the Coriolis terms.
  - Argue both the upper and the lower bound that make RNEA $\Theta(n)$ and order-optimal.
tags: [multibody-dynamics, inverse-dynamics, rnea, lagrange, complexity, research]
---

# Recursive Newton-Euler (RNEA)

## Setup and notation

The notation of the previous lesson, `c2-spatial-vector-algebra`, is used **unchanged**
(angular components first, $M^6$/$F^6$, $X$/$X^{*}$, $v\times$/$v\times^{*}$, spatial inertia
$I$). The results from there that this lesson keeps using:

- (previous R4) the equation of motion of one rigid body, $f = Ia + (v\times^{*})Iv$;
- (previous R3) $\frac{d}{dt}{}^BX_A = -\,{}^BX_A(v\times)$ and $v\times^{*} = -(v\times)^\top$;
- (previous R2) $^BI = ({}^AX_B)^\top\,{}^AI\,{}^AX_B$.

This lesson treats only a **kinematic tree** — closed loops are `c2-constrained-dynamics` and
contact is `c2-contact-dynamics`. All joints are taken to have a single degree of freedom
(multi-DOF joints follow from replacing $S_i$ with a $6\times n_i$ matrix, after which every
equation holds verbatim — the extension in problem P1).

| Symbol | Meaning |
|---|---|
| $n$ | The number of single-DOF joints = the number of degrees of freedom. Bodies are $1, \dots, n$ and the fixed base is $0$ |
| $\lambda(i)$ | The parent of body $i$. Bodies are numbered so that $\lambda(i) < i$ (topological order) |
| $\mu(i)$ | The set of children of body $i$ |
| $\nu(i)$ | The subtree rooted at body $i$, including $i$ |
| $S_i \in M^6$ | The motion subspace (axis) of joint $i$. **Constant in body-$i$ coordinates** |
| $^iX_{\lambda(i)}(q_i)$ | The parent-to-child transform, $= X_{J_i}(q_i)\,X_{T,i}$, where $X_{T,i}$ is the tree's fixed transform |
| $v_i, a_i$ | The spatial velocity and acceleration of body $i$, **in body-$i$ coordinates** |
| $v_{J_i} = S_i\dot{q}_i$ | The relative velocity across joint $i$ |
| $f_i \in F^6$ | The spatial force transmitted from the parent to body $i$ through joint $i$ |
| $f_i^{x}$ | An external force acting directly on body $i$ (contact, drag); zero if absent |
| $a_g = (0; g) \in M^6$ | The spatial acceleration of gravity; in a ground frame $g = (0, 0, -9.81)$, say |
| $J_i \in \mathbb{R}^{6\times n}$ | The spatial Jacobian of body $i$: $v_i = J_i\dot{q}$, in body-$i$ coordinates |
| $\tau \in \mathbb{R}^n$ | The joint generalised forces (torques) |
| $M(q), C(q,\dot{q}), g(q)$ | Mass matrix, Coriolis matrix and gravity torque: $\tau = M\ddot{q} + C\dot{q} + g$ |

**Sign convention**: $f_i$ is the force the **parent exerts on the child**. With the opposite
convention (child on parent) every sign in the backward recursion flips — that is the second
thing to check when matching numbers against an external implementation (the first is the
component order).

## Key results

The bracketed grade is the derivation depth (D0 cited / D1 sketched / D2 full derivation /
D3 proof — see `lesson-standard.md` §2 in the track design notes).

- **R1 (velocity recursion and the spatial Jacobian) [D2]** —
  $$
  v_i = {}^iX_{\lambda(i)}\,v_{\lambda(i)} + S_i\dot{q}_i, \qquad v_0 = 0, \tag{1}
  $$
  which unrolls to $v_i = J_i\dot{q}$ with columns
  $$
  J_{i,k} = \begin{cases} {}^iX_k\,S_k & k \in \{i\} \cup \text{(the ancestors of } i\text{)} \\ 0 & \text{otherwise.}\end{cases} \tag{2}
  $$
  The **sparsity of $J_i$ is decided by the ancestor relation in the tree**.
- **R2 (acceleration recursion and the origin of the bias term) [D2]** —
  $$
  a_i = {}^iX_{\lambda(i)}\,a_{\lambda(i)} + S_i\ddot{q}_i + v_i \times v_{J_i}, \qquad v_{J_i} = S_i\dot{q}_i. \tag{3}
  $$
  The last term arises from **nothing but the fact that the coordinate transform moves in time**.
  What it really is, is the **non-integrability** of the spatial Jacobian: for every $k$, $l$ and
  every body $i$,
  $$
  \frac{\partial J_{i,k}}{\partial q_l} - \frac{\partial J_{i,l}}{\partial q_k}
    = \big(J_{i,k}\times\big)\,J_{i,l} = [\,J_{i,k},\, J_{i,l}\,]. \tag{4}
  $$
  Because the right-hand side of (4) is not zero, $\dot{J}_i e_k \ne \partial J_i\dot{q}/\partial q_k$,
  and **every Coriolis term comes from there**. Checking (4) by central finite differences at a
  random 7-DOF configuration gives an error of about $1.5\times10^{-10}$ (condition 4 of the
  reproduction task).
- **R3 (backward force recursion and the joint torque) [D2]** — the resultant force on body $i$
  must satisfy its equation of motion, so
  $$
  f_i = \underbrace{I_i a_i + (v_i\times^{*})I_i v_i}_{\text{resultant on body } i} \;-\; f_i^{x}
      \;+\; \sum_{j \in \mu(i)} {}^iX_j^{*}\,f_j, \tag{5}
  $$
  $$
  \tau_i = S_i^\top f_i. \tag{6}
  $$
  (6) comes from **virtual work**: the joint can move only along $S_i$, so only that component of
  the transmitted force appears in the generalised force. Gravity is not a separate term: setting
  $a_0 := -a_g$ for the base acceleration makes (3) and (5) carry the gravity torque **as they
  stand**. **[D1]**
- **R4 (RNEA = the generalised force = the Euler-Lagrange left-hand side) [D3]** — unrolling the
  recursion (5),
  $$
  f_i = \sum_{j \in \nu(i)} {}^iX_j^{*}\,\big(I_j a_j + (v_j\times^{*})I_j v_j - f_j^{x}\big),
  $$
  so by (6) together with $S_i^\top\,{}^iX_j^{*} = \big({}^jX_i S_i\big)^\top = J_{j,i}^\top$,
  $$
  \tau_i = \sum_{j=1}^{n} \left(\frac{\partial v_j}{\partial \dot{q}_i}\right)^{\!\top}
    \big(I_j a_j + (v_j\times^{*})I_j v_j - f_j^{x}\big). \tag{7}
  $$
  The right-hand side of (7) is the **generalised force** of d'Alembert's principle, and for a
  holonomic system that equals the Euler-Lagrange left-hand side
  $\frac{d}{dt}\frac{\partial T}{\partial \dot{q}_i} - \frac{\partial T}{\partial q_i}
  + \frac{\partial V}{\partial q_i}$. **[D1 bridge]**
  Specialising: at $\dot{q} = 0$, $a_g = 0$, $\ddot{q} = e_k$ it gives $\tau = M(q)e_k$ (the
  starting point of `c2-crba-aba`); at $\ddot{q} = 0$, $a_g = 0$ it gives
  $\tau = C(q,\dot{q})\dot{q}$; and at $\dot{q} = \ddot{q} = 0$ it gives $\tau = g(q)$.
- **R5 (the $\Theta(n)$ cost and order-optimality) [D3]** — RNEA uses a **fixed number of 6-D
  operations per body, independent of $n$**, so its time and memory are $\Theta(n)$. Conversely,
  in a serial chain every $\tau_k$ depends on every $\ddot{q}_j$ (the mass matrix is generically
  dense), so any algorithm must read all of the input and $\Omega(n)$ is a lower bound. RNEA is
  therefore **order-optimal**. The route that forms $M$ and $C$ explicitly and then multiplies is
  $\Theta(n^2)$ (CRBA) or worse — RNEA obtains $\Theta(n)$ precisely by **forming neither**.

## Derivation

### R1 — the velocity recursion

Joint $i$ connects body $\lambda(i)$ to body $i$, and by definition the relative motion of the two
bodies is $v_{J_i} = S_i\dot q_i$ (that is exactly what it means for the motion subspace of a
single-DOF joint to be $S_i$). Spatial velocities are vectors, so they add in body-$i$
coordinates:

$$
v_i = \underbrace{{}^iX_{\lambda(i)}v_{\lambda(i)}}_{\text{inherited from the parent}} + \underbrace{S_i\dot{q}_i}_{\text{relative motion of the joint}},
$$

which is (1). For a fixed base, $v_0 = 0$. Unrolling the recursion along $\lambda$,

$$
v_i = \sum_{k \in \{i\}\cup \text{anc}(i)} {}^iX_k\,S_k\,\dot{q}_k,
$$

which is linear in $\dot q$, giving the $J_i$ of (2). If $k$ is neither $i$ nor an ancestor of
$i$, that joint's motion is not transmitted to body $i$ and the column is zero — **this sparsity
decides the cost of every algorithm that follows** (the $O(n^2)$ of CRBA, the branch-induced zero
pattern of $M$).

### R2 — the acceleration recursion

Differentiate (1). The crux is **what we differentiate with respect to**. In the previous lesson
(R5) spatial acceleration was defined as "the componentwise derivative of $v$ in a fixed frame".
For $v_i$ written in body-$i$ coordinates,

$$
a_i\big|_i = \frac{d}{dt}\big(v_i\big)_{\text{components}} + \underbrace{v_i \times v_i}_{=\,0}
  = \frac{d}{dt}\big(v_i\big)_{\text{components}} \tag{8}
$$

holds (the difference between the componentwise and the absolute derivative in a moving frame is
$v_f \times u$, and here $u = v_i$ and $v_f = v_i$, so the correction vanishes). **So we may
simply differentiate both sides of (1) componentwise** — that one line is the practical payoff of
spatial vector algebra.

Differentiate the two terms on the right in turn.

**Second term.** $S_i$ is constant in body-$i$ coordinates, so
$\frac{d}{dt}(S_i\dot q_i) = S_i\ddot{q}_i$.

**First term.** The **only** thing that makes $^iX_{\lambda(i)}$ vary is the motion of joint $i$
(the tree's fixed transform $X_{T,i}$ is constant). The relative spatial velocity of frame $i$
with respect to frame $\lambda(i)$ is $v_{J_i}$, and writing the second identity of the previous
lesson's (5) in body-$i$ coordinates,

$$
\frac{d}{dt}\,{}^iX_{\lambda(i)} = -\big(v_{J_i}\times\big)\,{}^iX_{\lambda(i)}. \tag{9}
$$

(The previous lesson wrote $\frac{d}{dt}{}^BX_A = -{}^BX_A(v\times)$ with $v$ in $A$ coordinates.
Moving coordinates by the adjoint conjugation $X(u\times)X^{-1} = \big((Xu)\times\big)$ gives (9) —
problem P1 (a).) Then

$$
\frac{d}{dt}\Big({}^iX_{\lambda(i)}v_{\lambda(i)}\Big)
= -\big(v_{J_i}\times\big)\,{}^iX_{\lambda(i)}v_{\lambda(i)} + {}^iX_{\lambda(i)}\,\frac{d}{dt}\big(v_{\lambda(i)}\big)_{\text{components}}.
$$

Applying (8) to the parent makes the second term $^iX_{\lambda(i)}a_{\lambda(i)}$. For the first,
(1) gives $^iX_{\lambda(i)}v_{\lambda(i)} = v_i - v_{J_i}$, so

$$
-\big(v_{J_i}\times\big)\big(v_i - v_{J_i}\big)
= -\,v_{J_i} \times v_i + \underbrace{v_{J_i} \times v_{J_i}}_{=\,0}
= v_i \times v_{J_i},
$$

the last equality being the antisymmetry of the motion cross product, $u \times w = -\,w \times u$
(problem P2). Adding the two terms gives (3).

**What the bias term really is.** The term $v_i \times v_{J_i} = \dot{q}_i\,(v_i \times S_i)$ in
(3) is independent of $\ddot{q}$ and **quadratic** in $\dot{q}$. Why it cannot be avoided is what
(4) tells us. Differentiating $v_i = J_i\dot q$ directly gives

$$
a_i = J_i\ddot{q} + \dot{J}_i\dot{q}, \qquad
\dot{J}_i\dot{q} = \sum_{k,l} \frac{\partial J_{i,k}}{\partial q_l}\dot{q}_k\dot{q}_l,
$$

and **if** $\partial_{q_l}J_{i,k}$ were symmetric in $(k, l)$, this double sum would fold into an
exact differential of the form $\partial_{q}\big(\tfrac{1}{2}\dot q^\top \cdots\big)$ and the
Coriolis terms could be removed by a change of coordinates alone. (4) says that the symmetry is
broken by **exactly the Lie bracket**. Proving (4) takes two lines: differentiate (2) with respect
to $q_l$ and use (9) (problem P2 (b)).

> **(4) numerically**: for the planar two-link arm ($l_1 = 0.6$, $l_2 = 0.4$, $q = (0.3, -0.7)$),
> body 2 gives $\partial_{q_2}J_{2,1} - \partial_{q_1}J_{2,2} = (0,0,0,\;0.4589053124,\;0.3865306124,\;0)$
> and $[J_{2,1}, J_{2,2}]$ equals the same value (central differences with $h = 10^{-6}$, error
> $1.9\times10^{-11}$). You can see the **asymmetry itself**: $\partial_{q_1}J_{2,2} = 0$ while
> $\partial_{q_2}J_{2,1} \ne 0$.

### R3 — the backward force recursion and the torque projection

The sum of all spatial forces on body $i$ must satisfy its equation of motion. Body $i$ receives
(a) $f_i$, from the parent through joint $i$; (b) the reaction $-{}^iX_j^{*}f_j$ from each child
$j$ through joint $j$; and (c) the external force $f_i^{x}$. Hence

$$
f_i - \sum_{j\in\mu(i)} {}^iX_j^{*}f_j + f_i^{x} = I_i a_i + (v_i\times^{*})I_i v_i,
$$

and solving for $f_i$ gives (5). Using $X^{*}$ (the **force** transform, not the motion transform)
to move a child's force into the parent's coordinates is the point of the previous lesson's R1;
using $X^\top$ here is immediately wrong in any chain with translation. The recursion starts at
the leaves and climbs along $\lambda$ — every $f_j$ with $j \in \mu(i)$ is computed before $f_i$,
so sweeping the body indices in reverse ($i = n, \dots, 1$) suffices, since the numbering has
$\lambda(i) < i$.

**Deriving (6) — virtual work.** The virtual displacement joint $i$ allows is the single
$\delta q_i$, and the corresponding virtual spatial displacement is $S_i\,\delta q_i$. The virtual
work done by the transmitted force $f_i$ on that displacement is
$f_i \cdot (S_i\delta q_i) = (S_i^\top f_i)\,\delta q_i$. Since the generalised force $\tau_i$ is
by definition "the force paired with $\delta q_i$", $\tau_i = S_i^\top f_i$. The remaining
component $(\mathbb{1} - S_i(S_i^\top S_i)^{-1}S_i^\top)f_i$ is the **constraint reaction** and
does no work — that decomposition carries straight over into the null-space projection of
`c2-constrained-dynamics`.

**Handling gravity.** Gravity may be added as $f_i^{x} = I_i\,{}^iX_0\,a_g$ per body, but the
cheaper way is to set $a_0 := -a_g$. Why: the recursion (3) is **affine** in $a$ and the
dependence on $a_0$ propagates as $^iX_0 a_0$, so $a_0 = -a_g$ is the same as giving every body a
frame that accelerates upward at $g$ — an algorithmic use of the equivalence principle. The extra
cost is **zero**. **[D1]**

### The algorithm

```python
def rnea(model, q, qd, qdd, a_grav):
    """Recursive Newton-Euler. Returns tau (n,). Angular-first spatial vectors."""
    n = model.n
    Xup = model.Xup(q)  # i X parent(i) for every body
    v, a, f = [None] * n, [None] * n, [None] * n
    for i in range(n):  # forward pass: kinematics
        S = model.S[i]
        vJ = S * qd[i]
        p = model.parent[i]
        if p < 0:
            v[i] = vJ
            a[i] = Xup[i] @ (-a_grav) + S * qdd[i]
        else:
            v[i] = Xup[i] @ v[p] + vJ
            a[i] = Xup[i] @ a[p] + S * qdd[i] + crm(v[i]) @ vJ
        f[i] = model.I[i] @ a[i] + crf(v[i]) @ model.I[i] @ v[i] - model.fx[i]
    tau = np.zeros(n)
    for i in range(n - 1, -1, -1):  # backward pass: forces
        tau[i] = model.S[i] @ f[i]
        p = model.parent[i]
        if p >= 0:
            f[p] = f[p] + Xup[i].T @ f[i]
    return tau
```

`Xup[i].T @ f[i]` is $^{\lambda(i)}X_i^{*}f_i$ — the previous lesson's (2),
$^BX_A^{*} = ({}^AX_B)^\top$, written as **one** transpose, with no inverse computed. That single
line is the second practical payoff of spatial vector algebra.

## Proof sketch

### R4 — the output of RNEA is the generalised force

**Hypotheses** H1: the system is a kinematic tree (no closed loops) and all joints are holonomic.
H2: $S_i$ is constant in body-$i$ coordinates. H3: each body's mass distribution is constant
(rigidity).
**Conclusion** C: (7) holds for every $i$, and its right-hand side is the generalised force of the
holonomic system.

**Strategy**: unroll the backward recursion all the way into closed form and recognise
$S_i^\top {}^iX_j^{*}$ as the transpose of a Jacobian column. No variational calculus is used —
it is all linear algebra.

1. **Unroll the recursion.** Write $f_i^{\text{net}} := I_ia_i + (v_i\times^{*})I_iv_i - f_i^{x}$,
   so that (5) reads $f_i = f_i^{\text{net}} + \sum_{j\in\mu(i)}{}^iX_j^{*}f_j$. Substituting the
   same expression into the children repeatedly and using
   $^iX_j^{*}\,{}^jX_k^{*} = {}^iX_k^{*}$ (composition of force transforms — previous lesson, P5 (d)),
   $$
   f_i = \sum_{j\in\nu(i)} {}^iX_j^{*}\,f_j^{\text{net}}.
   $$
   Because the system is a tree, each $j$ appears **exactly once** (the first place H1 is used —
   in a closed loop the same body is counted along two paths and this identity fails).
2. **Project onto the torque.** Substitute into (6) and move the transpose:
   $$
   \tau_i = S_i^\top \sum_{j\in\nu(i)} {}^iX_j^{*}f_j^{\text{net}}
   = \sum_{j\in\nu(i)} \big(({}^iX_j^{*})^\top S_i\big)^\top f_j^{\text{net}}
   = \sum_{j\in\nu(i)} \big({}^jX_i\,S_i\big)^\top f_j^{\text{net}},
   $$
   the last equality being $({}^iX_j^{*})^\top = {}^jX_i$ from the previous lesson's (2).
3. **Recognise the Jacobian columns.** By (2), $^jX_iS_i = J_{j,i}$, and for $j \notin \nu(i)$ we
   have $J_{j,i} = 0$ (since $i$ is then not an ancestor of $j$). So widening the sum to
   $j = 1, \dots, n$ changes nothing, and since $J_{j,i} = \partial v_j/\partial\dot q_i$, this is (7).
4. **Confirm it is the generalised force.** (7) is "project each body's inertial force
   $f_j^{\text{net}}$ onto the virtual velocity field of $\dot q_i$ and sum", which is the
   definition of the generalised force in d'Alembert's principle. For a holonomic system
   d'Alembert ⟺ Euler-Lagrange, so the right-hand side of (7) equals
   $\frac{d}{dt}\partial T/\partial\dot q_i - \partial T/\partial q_i + \partial V/\partial q_i$.
   (Omitted: the standard proof that d'Alembert implies Lagrange. MLS ch.4, or any analytical
   mechanics text. This bridge is **[D1]**, and conditions 2 and 3 of the reproduction task are
   what check it numerically.)
5. **Specialise.** With $\dot q = 0$ and $a_g = 0$ every $v_j = 0$, so the bias terms vanish and
   $a_j = J_j\ddot q$. Substituting into (7) gives
   $\tau = \big(\sum_j J_j^\top I_jJ_j\big)\ddot q$, and since
   $T = \frac{1}{2}\sum_j v_j^\top I_jv_j = \frac{1}{2}\dot q^\top\big(\sum_j J_j^\top I_jJ_j\big)\dot q$,
   the bracket is exactly $M(q)$. So **calling RNEA $n$ times yields every column of $M$** — at
   cost $\Theta(n^2)$, the same order that the CRBA of `c2-crba-aba` achieves with a smaller constant.

**Delete a hypothesis**: without H1 (a tree), the "exactly once" of step 1 fails and the subtree
sum is not even well defined — closed loops must be handled separately with multipliers
(`c2-constrained-dynamics`). Without H2 ($S_i$ constant), a term $\dot S_i\dot q_i$ survives in
the second term of R2 (this is the extra term for multi-DOF and non-standard joints, and writing
$\dot S_i = v_i \times S_i$ merges it with the bias term of (3)). Without H3, the assumption
$\dot I = 0$ behind the previous lesson's R4 fails and $f_j^{\text{net}}$ gains a $\dot I_j v_j$ term.

### R5 — $\Theta(n)$ and order-optimality

**Hypotheses** H1: a kinematic tree with $n$ single-DOF joints, with $S_i$, $X_{T,i}$ and $I_i$
constant-size data per body. H2: real arithmetic has unit cost.
**Conclusions** C1: the time and space cost of RNEA is $\Theta(n)$. C2: in a serial chain
$\Omega(n)$ is a lower bound, so RNEA is order-optimal.

**Strategy**: count operations per body for the upper bound; argue from dependence (every output
depends on every input) for the lower bound.

1. **The cost per body is constant.** In the forward pass, body $i$ does (a) assemble
   $X_{J_i}(q_i)$ (two trigonometric calls plus a fixed number of assignments); (b) compute
   $^iX_{\lambda(i)}v_{\lambda(i)}$ and $^iX_{\lambda(i)}a_{\lambda(i)}$ — two $6\times6$
   matrix-vector products; (c) two scalings of $S_i$; (d) $v_i \times v_{J_i}$ — one $6\times6$
   product; (e) $I_ia_i$ and $(v_i\times^{*})(I_iv_i)$ — one symmetric product plus two general
   ones. The backward pass does (f) the inner product $S_i^\top f_i$ and (g) one $X^\top f_i$
   product plus an addition. All are of **fixed size $6\times6$**, so the cost per body is a
   constant $c$ independent of $n$ (the exact flop tables per joint type are in the cost section of RBDA ch.5).
2. **Each body is visited exactly twice.** Because the numbering is topologically sorted with
   $\lambda(i) < i$, the forward pass is the **plain loop** $i = 1 \dots n$ and the backward pass
   $i = n \dots 1$, with no recursion stack. The number of visits is exactly $2n$. What is stored
   is $v_i, a_i, f_i, X_i$ — a constant per body, so space is $\Theta(n)$ too.
3. **Upper bound.** From 1 and 2 the total cost is $\le 2cn = O(n)$. And the forward pass alone
   needs at least $n$ transform assemblies, so $\Omega(n)$, hence $\Theta(n)$.
4. **Lower bound (C2).** The output $\tau$ has $n$ components, so writing it alone costs
   $\Omega(n)$. More strongly: in a serial chain $M(q)$ is generically dense, so computing even a
   **single** $\tau_k$ correctly requires reading every $\ddot{q}_j$ — an algorithm that does not
   read some $\ddot q_j$ cannot distinguish two inputs for which $M_{kj} \ne 0$. So any algorithm
   that computes $\tau$ is $\Omega(n)$, and RNEA is order-optimal.
5. **What is *not* optimal.** The constant is not. Specialising the joint type (so that $S_i$ is
   sparse), or expanding components instead of assembling $X$, reduces it considerably. And in a
   **parallel** model $\Theta(n)$ is not optimal — divide and conquer gives $O(\log n)$
   ([Featherstone 1999](https://doi.org/10.1177/02783649922066619)). The lower bound of step 4 is
   a **sequential**-model bound.

**Delete a hypothesis**: dropping "single-DOF" from H1 makes the cost $\Theta(\sum_i n_i)$, since
$S_i$ becomes $6\times n_i$ and (f), (g) grow to $O(n_i)$ — the order survives. Dropping H2
(unit-cost arithmetic) — in arbitrary precision, say — means recounting in bit complexity.

## Problem set

The solution policy is stated per problem. Difficulty: ★ 15 minutes / ★★ one hour /
★★★ a day or more.

**P1 (derivation, ★★, R2)** (a) Prove the adjoint conjugation
$X(u\times)X^{-1} = \big((Xu)\times\big)$ and use it to obtain (9) from the second identity of the
previous lesson's (5). (b) For a joint with $n_i > 1$ degrees of freedom
($S_i \in \mathbb{R}^{6\times n_i}$, $\dot q_i \in \mathbb{R}^{n_i}$), show that (3) becomes
$a_i = {}^iX_{\lambda(i)}a_{\lambda(i)} + S_i\ddot q_i + \dot S_i\dot q_i + v_i \times v_{J_i}$,
and confirm that $\dot S_i = 0$ for a joint whose $S_i$ is constant in body coordinates.
*Solution sketch*: for (a) the shortest route is to read $u\times$ as the adjoint action of an
element of $\mathfrak{se}(3)$ and use that $X(\cdot)X^{-1}$ is a Lie-algebra isomorphism;
expanding components works too but is long. For (b) just track that differentiating
$S_i\dot q_i$ in (1) now produces two terms.

**P2 (derivation, ★★, R2)** (a) Show the antisymmetry $u \times w = -w \times u$ of the motion
cross product directly from the block form of (6). (b) Prove (4): differentiate (2) with respect
to $q_l$ and use (9), splitting into two cases according to which of $k$ and $l$ is the ancestor.
*Solution sketch*: for (b), take without loss of generality $l$ to be on the descendant side of
$k$; the case $\partial_{q_k}J_{i,l} = 0$ and the other case then separate. The only way $^iX_k$
depends on $q_l$ is through (9), and the term that comes out is exactly
$(J_{i,k}\times)J_{i,l}$. Cross-check the sign with central differences at $h = 10^{-6}$ —
**always** — because this sign is easy to get wrong by hand.

**P3 (proof, ★★★, R4·R5)** (a) Show with a concrete four-bar linkage how step 1 of R4 ("because
the system is a tree, each $j$ appears exactly once") fails for a closed loop, and write how (7)
would then have to be modified. (b) Explain why the lower-bound argument in step 4 of R5 does not
carry over to a **tree** (as opposed to a serial chain), and exhibit a tree shape for which the
$\tau_k$ of different branches can be computed in $o(n)$.
*Strategy and key inequality*: for (b) look at a depth-one star tree — $n$ bodies each attached
directly to the base. $M$ becomes nearly block diagonal and each $\tau_k$ depends on only $O(1)$
inputs. (The expansion is withheld.)

**P4 (numerical, ★, R1-R4)** A planar two-link arm: both joints rotate about $z$, with point
masses at the link tips. $m_1 = 1.5$, $l_1 = 0.6$ (the centre of mass of body 1 is at $x = l_1$
from joint 1), $m_2 = 1.0$, $l_2 = 0.4$ (the origin of the body-2 frame is at $x = l_1$ in body 1,
and its centre of mass at $x = l_2$ from there), $\bar{I}_{C,1} = \bar{I}_{C,2} = 0$, gravity
$9.81$ along $-y$ of the base. At $q = (0.3, -0.7)$, $\dot q = (0.5, 1.2)$,
$\ddot q = (-0.4, 0.9)$, find $\tau$, $M(q)$, and the three-way split of $\tau$ (gravity only /
bias only / $M\ddot q$).
*Answer* (tolerance $10^{-9}$):
$\tau = (17.818552317079,\; 3.582165429254)$,
$M(q) = \begin{bmatrix} 1.427124249897 & 0.343562124948 \\ 0.343562124948 & 0.16 \end{bmatrix}$,
$g(q) = (17.672019777951,\; 3.614243340467)$,
$C\dot q = (0.408176326634,\; -0.038653061234)$,
$M\ddot q = (-0.261643787505,\; 0.006575150021)$.
*Checks*: (a) the three parts sum to $\tau$ to within $10^{-12}$; (b) $M_{22} = m_2l_2^2 = 0.16$
must come out exactly (independent of $q$); (c) compare against the closed form
$M_{11} = (m_1+m_2)l_1^2 + m_2l_2^2 + 2m_2l_1l_2\cos q_2$.

**P5 (implementation, ★★, R1-R3)** On top of the spatial vector functions of the previous lesson,
write `rnea(model, q, qd, qdd, a_grav)`. The model is given by `parent`, `jtype`, `Xtree` and
`(m, c, Ic)`, and must support trees (with branching).
*Rubric*: (a) reproduces the numbers of P4 to within $10^{-9}$; (b) on a branching tree (two
bodies sharing a parent) $\tau$ reflects both branches; (c) a unit test confirms **affinity** in
$\ddot q$:
$\tau(\ddot q_1 + \ddot q_2) - \tau(0) = [\tau(\ddot q_1) - \tau(0)] + [\tau(\ddot q_2) - \tau(0)]$
to within $10^{-12}$; (d) gravity handled as $a_0 = -a_g$ agrees to within $10^{-12}$ with an
implementation that adds it per body as $f^x$; (e) the component order and the sign convention for
$f_i$ are stated in the docstring.

**P6 (paper, ★★, R5)** Read Luh, Walker & Paul (1980) and write: (a) what the authors claim by
"on-line (real-time) computation", and which hardware and which robot that claim presupposes;
(b) which step of R5 here their $O(n)$ claim corresponds to, and **what it does not claim**;
(c) three pieces of information missing for reproduction.
*Rubric*: for (b), distinguishing "constant cost per body" (the upper bound) from
"order-optimal" (the lower bound) passes — the 1980 paper does not address the lower bound. For
(c), naming at least two of the frame conventions, the provenance of the inertial parameters, and
the timing methodology passes. Writing only "there is no code" does not.

## Paper reading

**Two must-reads**: one is the original (1980), the other a map of the terrain twenty years later
(2000). Reading both **with the same questionnaire** and writing for yourself what changed over
those twenty years is the reading goal of this lesson. Write a one-page note on each with the ten
fixed questions below (`lesson-standard.md` §5). Read in three passes and concentrate on
questions 4, 7 and 9 in the third pass.

1. **Luh, Walker & Paul, "On-Line Computational Scheme for Mechanical Manipulators"
   (1980, ASME J. Dyn. Syst. Meas. Control)** — role: `seminal`.
   <https://doi.org/10.1115/1.3149599>
   Which sections and why: the ones that set up the forward kinematic recursion and the backward
   force recursion. They correspond one-to-one with (1), (3) and (5) here, but the notation is
   split into $3\times3$ rotations and vectors, which shows **how much shorter the same algorithm
   becomes in spatial vectors**. Read the section on cost as well.
   Extra questions: (a) how many lines do the authors' recursions become when rewritten in the
   $^iX_{\lambda(i)}$ notation of this lesson? (b) how do the authors handle gravity — is it the
   same as the $a_0 = -a_g$ trick? (c) what does the erratum in the same volume
   (<https://doi.org/10.1115/1.3139629>) correct?
2. **Featherstone & Orin, "Robot dynamics: equations and algorithms" (2000, ICRA)** — role:
   `survey`. <https://doi.org/10.1109/ROBOT.2000.844153>
   Which sections and why: the ones that compare inverse dynamics, forward dynamics and
   mass-matrix algorithms within one framework. The complexity landscape of R5 here and of the
   next lesson (CRBA and ABA) is there.
   Extra questions: (a) in the authors' cost comparison, is there a point where the ordering
   reverses for small $n$ ($n \le 6$), and what decides that crossover? (b) what has changed since
   2000 (analytical derivatives, GPUs and vectorisation, contact) — find one place where this
   survey is wrong **today**.

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation. (4) what is guaranteed theoretically, and **what is
not**? (5) independent and dependent variables and baselines — were the baselines tuned fairly?
(6) do the metrics match the claim; are variance and seeds reported? (7) what is missing for
reproduction? (8) if it were wrong, which assumption would you suspect first? (9) compute and
memory complexity, and real-time feasibility. (10) what would you change to go beyond it in a year?

## Reproduction task

**Tier R1 (numerical check).** Compute budget: one notebook CPU core, under two minutes, numpy
(plus either sympy or jax for condition 2). Memory under 200 MB.

The `rnea` of P5 must satisfy **all four** of the following. Fix every random seed.

1. **Agreement with the two-link closed form** — for the model of P4, on $10^4$ random
   $(q, \dot q, \ddot q)$ (components drawn uniformly from
   $[-\pi, \pi] \times [-3, 3] \times [-3, 3]$),
   $$
   \max_k \frac{|\tau_k^{\text{RNEA}} - \tau_k^{\text{closed}}|}{1 + \lVert \tau^{\text{closed}}\rVert_\infty} < 10^{-12}.
   $$
   **Derive** the closed form of the two-link point-mass model yourself rather than copying it —
   the derivation *is* check (c) of P4.
2. **Agreement with the exact Euler-Lagrange equations at 7 DOF** — for a seven-DOF serial arm
   (joint axes $z,y,z,y,z,y,z$, with link offsets and inertias generated by the script), build
   $T = \frac{1}{2}\dot q^\top M(q)\dot q$ and $V(q)$, differentiate them by **symbolic (sympy) or
   automatic (jax) differentiation** to get
   $\tau^{\text{EL}} = \frac{d}{dt}\partial T/\partial\dot q - \partial T/\partial q + \partial V/\partial q$,
   and require
   $$
   \max_k \frac{|\tau_k^{\text{RNEA}} - \tau_k^{\text{EL}}|}{1 + \lVert\tau^{\text{EL}}\rVert_\infty} < 10^{-9}
   $$
   over $10^2$ random states. Build $M(q)$ **independently of RNEA**, as
   $M = \sum_j J_j^\top I_j J_j$ (the Jacobian route).
3. **Agreement with a finite-difference Euler-Lagrange, plus an $h$ sweep** — on the same 7-DOF
   model, with the derivatives of $M$ and $V$ taken by central differences, $\tau^{\text{FD}}$
   must satisfy, at $h = 10^{-5}$,
   $$
   \max_k \frac{|\tau_k^{\text{RNEA}} - \tau_k^{\text{FD}}|}{1 + \lVert\tau^{\text{RNEA}}\rVert_\infty} < 10^{-7},
   $$
   and over the sweep $h \in \{10^{-3}, \dots, 10^{-8}\}$ the error must trace a **V shape** with
   its minimum near $10^{-5}$.
   > Note: this condition is looser than condition 2 because of the **limits of finite
   > differencing**, not of the algorithm. The 7-DOF absolute errors measured in the author's
   > environment were $8.9\times10^{-10}$ at $h = 10^{-5}$, $7.9\times10^{-9}$ at $h = 10^{-6}$
   > and $1.4\times10^{-7}$ at $h = 10^{-7}$. The blueprint's "within 1e-9" applies to condition 2
   > (exact differentiation) only.
4. **Confirm the non-integrability (4) numerically** — on the same 7-DOF model, at random $q$ and
   over all triples $(i, k, l)$,
   $$
   \max_{i,k,l}\big\lVert \big(\partial_{q_l}J_{i,k} - \partial_{q_k}J_{i,l}\big) - \big(J_{i,k}\times\big)J_{i,l} \big\rVert_\infty < 10^{-8}
   $$
   (central differences, $h = 10^{-6}$). Then compute the same quantity against the
   **sign-flipped** hypothesis $-\big(J_{i,k}\times\big)J_{i,l}$ and show that it is **large**,
   above $10^{-1}$ — the step that confirms the sign is actually determined.
   Then run an implementation that **omits** the bias term (dropping $v_i\times v_{J_i}$ from (3))
   on the state of P4 and show that
   $\lVert\tau^{\text{bug}} - \tau\rVert_\infty > 10^{-2}$ while at $\dot q = 0$ the difference
   vanishes below $10^{-14}$.

**Input data**: no external data needed. The link offsets, masses and inertias of the 7-DOF model
are generated with a fixed seed (`np.random.default_rng(7)`), with the inertia matrices built in
the form $0.02\,AA^\top + 0.05\,\mathbb{1}$ so that they are positive definite and satisfy the
triangle inequalities.

**Baselines** (at least one):
- First choice: the Jacobian-based Euler-Lagrange path of condition 2 — a completely independent
  second implementation.
- Second choice: the two-link closed form of condition 1 (the equations you derived by hand).
- Optional check (not required to pass): agreement with `pinocchio`'s `pin.rnea` to within
  $10^{-10}$ (mind that its component order is linear first), or a comparison against
  Featherstone's `ID` in Octave.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| Correct only at $\dot q = 0$ | The $v_i \times v_{J_i}$ of (3) was omitted | Check whether both components differ by the **same value** at the state of P4 (here, $0.0927673470$) |
| Only gravity is wrong | The sign of $a_0 = -a_g$, or $a_g$ was not transformed into body coordinates | At $\dot q = \ddot q = 0$, check $\tau$ against $\partial V/\partial q$ by finite differences |
| Two links fine, 7 DOF wrong | The assembly of $X_J$ for joints whose axis is not $z$, or the order in which $X_{T,i}$ is applied | Set $\dot q_i = 1$ with the rest zero for each joint in turn and compare $v_i$ against finite-differenced forward kinematics |
| Wrong on a branching tree | The backward recursion lifted the child's force with $X$ instead of $X^\top$ | Attach two children to one parent and zero the mass of one of them to test the symmetry |
| Every torque sign is reversed | The direction convention for $f_i$ (parent-to-child versus child-to-parent) | Hold a one-link pendulum at rest and check the sign of the gravity torque by hand |
| Only the affinity test fails | $\ddot q$ leaked into the bias term (for instance, $v_i\times$ was built from $a_i$) | Double $\ddot q$ and check that $\tau - \tau(0)$ is exactly doubled |

## Open problems

- **(open problem) Is inverse dynamics even well posed when contact is involved** — RNEA rests on
  the fact that $\tau$ is **unique** given $(q, \dot q, \ddot q)$, and that fact holds only for a
  tree. Once contact enters, there may be several $(\tau, \lambda)$ producing the same $\ddot q$,
  or none (the complementarity of `c2-contact-dynamics`), and "inverse dynamics" has to be
  redefined as a problem. Current approaches: formulations that treat contact forces inside a QP
  ([Todorov 2014](https://doi.org/10.1109/ICRA.2014.6907751)), and trajectory optimisation with
  complementarity constraints. What is missing: a definition of inverse dynamics that stays
  continuous across a change of contact mode.
- **(open problem) What $\Theta(n)$ means in a regime dominated by model error** — RNEA is exact
  to machine precision for the inertial parameters it is given, but on a real robot almost all of
  the error in $\tau$ comes from **model error** (joint friction, harmonic-drive compliance,
  cabling, thermal drift). Beyond some accuracy the problem is identification and compensation,
  not algorithms, and there is no way to estimate in advance "where model error takes over".
  Current approaches: identification with physical consistency as a constraint
  ([Wensing et al. 2018](https://doi.org/10.1109/LRA.2017.2729659)), and residual learning.
  The question is faced head-on in `c2-dynamics-derivatives-sysid`.
- **(open problem) Lower bounds on parallel and heterogeneous hardware** — the lower bound of R5
  is a sequential one. Divide and conquer gives $O(\log n)$ but with a constant large enough that
  sequential RNEA is faster at real robot sizes ($n \le 30$). There is no model of "from which $n$
  and which batch size does parallel win" on GPUs and SIMD, and with today's workloads — where
  trajectory optimisation calls RNEA on thousands of states at once — this is the actual
  bottleneck. Current approaches: vectorised batch dynamics and analytical derivatives
  ([Carpentier & Mansard 2018](https://doi.org/10.15607/RSS.2018.XIV.038)), and the
  divide-and-conquer algorithm of
  [Featherstone 1999](https://doi.org/10.1177/02783649922066619). What is missing: a cost model
  that holds batch size, $n$ and memory bandwidth together.

## Concept check

Run `rc quiz c2-rnea-inverse-dynamics`. The quiz is for **concept checking only**; the real work
is the problem set and the reproduction task above (`lesson-standard.md` §4).

The five items cover: where the bias term $v_i \times v_{J_i}$ of (3) comes from; which transform
lifts a child's force to its parent in the backward recursion; what RNEA returns at $\dot q = 0$
with gravity off and $\ddot q = e_k$; whether the spatial Jacobian is integrable; and which facts
the $\Theta(n)$ conclusion actually uses.

## How to study this stage

1. **Lay out just four equations from the previous lesson (15 min)** —
   $f = Ia + (v\times^{*})Iv$, $\frac{d}{dt}{}^BX_A = -{}^BX_A(v\times)$,
   $v\times^{*} = -(v\times)^\top$ and $^BX_A^{*} = ({}^AX_B)^\top$. Every derivation here is a
   combination of those four.
2. **Draw the tree notation (20 min)** — sketch a branching tree of about five bodies and colour
   in $\lambda$, $\mu$, $\nu$ and the sparsity pattern of each $J_i$ by hand. Seeing the structure
   of (2) with your own hand makes the CRBA of the next lesson nearly obvious.
3. **Rewrite R2 from a blank page (60 min)** — write (1), remember only (9), and get to (3). Where
   you get stuck is almost always the substitution
   $^iX_{\lambda(i)}v_{\lambda(i)} = v_i - v_{J_i}$. When you are done, **check (4) by finite
   differences yourself** (problem P2 (b)) — that single numerical experiment settles "why are
   there Coriolis terms at all" permanently.
4. **Write steps 1-3 of R4 three times rather than memorising them (50 min)** — unroll the
   recursion, move the transpose, recognise the Jacobian columns. Do **not** prove step 4 (the
   d'Alembert bridge) now: knowing that the bridge is [D1] and moving on, then checking it
   numerically with condition 2 of the reproduction task, is the design of this lesson.
5. **Implement it wrongly first (60 min)** — when writing P5, make three variants: (a) the bias
   term omitted, (b) $X$ instead of $X^\top$, (c) $a_0 = +a_g$, and tabulate which condition of
   the reproduction task breaks and how. All six rows of the diagnosis table came out of that
   experiment.
6. **Finish the reproduction task (105 min)** — build the symbolic/automatic differentiation path
   of condition 2 first. Once you have it, it is the answer key for every later lesson (CRBA, ABA,
   constraints, contact). **Do** plot the V curve of the $h$ sweep in condition 3 — you have to
   see with your eyes "why 1e-9 is not reachable by finite differencing" before the acceptance
   criteria become readable.
7. **Read the two papers twenty years apart (120 min)** — read Luh 1980 first and transcribe its
   recursions into spatial vectors. Then see in Featherstone & Orin 2000 which point of the
   landscape that algorithm occupies. Finding one place where the 2000 survey is wrong today
   (P6 (b)) is the research training of this lesson.
8. **End with what cannot be done (20 min)** — pick the contact-related open problem and write a
   paragraph on where the premise "inverse dynamics is unique" breaks. That paragraph becomes the
   introduction to `c2-contact-dynamics`.

**Passing bar**: you can write (1), (3), (5) and (6) from a blank page; you can state steps 1-3 of
R4 and both bounds of R5; you have an `rnea` that passes all four conditions of the reproduction
task; and you have one-page notes on both papers.
