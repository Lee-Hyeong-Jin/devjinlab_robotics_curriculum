---
id: s2-grasp-mechanics
lang: en
title: Contact mechanics and grasp stability
summary: >-
  Reducing grasping to a convex-geometry problem in wrench space. Turn the friction cone into finitely
  many generators, prove by a separating hyperplane that force closure is equivalent to "the
  generators positively span wrench space", i.e. "the origin lies in the interior of their convex
  hull", and move that to an LP test. Derive the Ferrari–Canny quality metric and solve it in closed
  form for an antipodal grasp of the unit disc, which shows the metric is **not monotone** in the
  friction coefficient but peaks at $\mu = 2^{1/4}$ with value $\sqrt2 - 1$. Finally separate caging
  from force closure. The reproduction task charts the force-closure feasible region against the
  number of contacts.
objectives:
  - Discretize a friction cone into finitely many generators and write a contact wrench as a point in wrench space.
  - Prove that force closure is equivalent to "the origin is interior to the convex hull of the generators", by a separating hyperplane.
  - Move that test to a linear program and explain why the rank condition is still needed separately.
  - Derive the Ferrari–Canny metric and compute it in closed form for an antipodal grasp of the unit disc.
  - Separate caging from force closure in the language of configuration space, and show by example that neither implies the other.
tags: [manipulation, grasping, friction-cone, force-closure, wrench-space, caging, research]
---

# Contact mechanics and grasp stability

## Setup and notation

This is the module's first lesson. The recommended prerequisites are C1–C4 and C6; in particular the
following is assumed:

- `c2-contact-dynamics` — the complementarity conditions (normal gap $\phi \ge 0$, normal force
  $\lambda \ge 0$, $\phi\lambda = 0$) and the Coulomb friction cone. Only their **static** side is
  used here.
- `c6-tamp` — that there are $3^{n_c}$ contact modes (its R3). Here the mode is fixed and only
  **force equilibrium** is considered.
- Convex analysis: convex cones, convex hulls, the separating hyperplane theorem, Farkas' lemma and
  LP duality (recommended prerequisite `r0-convex-optimization`).

Notation (fixed for all of module S2):

| Symbol | Meaning |
|---|---|
| $\mathcal{B} \subset \mathbb{R}^d$ | the object; $d = 2$ in the plane, $d = 3$ in space |
| $p_i$ | position of contact $i$ (object frame) |
| $\hat n_i$ | unit normal at contact $i$, pointing **into** the object |
| $\mu$ | friction coefficient; $\alpha = \arctan\mu$ is the half-angle of the friction cone |
| $FC_i$ | friction cone of contact $i$: $\{f : \lVert f_t\rVert \le \mu f_n,\ f_n \ge 0\}$ |
| $w = (f, \tau)$ | a wrench; $w \in \mathbb{R}^3$ in the plane ($\tau$ scalar), $\mathbb{R}^6$ in space |
| $W = \{w_1,\dots,w_m\}$ | the discretized set of **wrench generators** |
| $\mathcal{W} = \mathrm{cone}(W)$ | the cone the generators positively span |
| $Q$ | the Ferrari–Canny quality metric (§R2) |
| $\mathcal{C}_{\mathcal{B}}$ | configuration space of the object (fingers treated as obstacles), used for caging |

**The problem (force closure).** Given the contacts and the friction coefficient, the grasp is
**force closure** if for **every** external wrench $w_{ext}$ there exist contact forces
$f_i \in FC_i$ inside the friction cones with

$$
\sum_{i=1}^{n} w_i(f_i) \;+\; w_{ext} \;=\; 0.
  \tag{1}
$$

That is, the set of wrenches the hand can apply must be **all** of wrench space. What matters is that
this is **a condition on forces and not on motion** — that distinction is the starting point of R3
(caging).

Two assumptions, stated explicitly.

- **(A1) rigid bodies, point contacts, Coulomb friction** — contacts are points, friction follows the
  Coulomb model and the object is rigid. Surface contact and deformable bodies appear in the failure
  modes of §R1.
- **(A2) no bound on contact force** — $f_n$ is unbounded. With a bound, force closure stops being a
  binary property and becomes the **quantitative** question "up to how large a disturbance", which is
  the $Q$ of R2.

## Self-diagnosis before starting

This is the module's first lesson, so check your readiness first. **Prerequisite lessons are not
locked** — if you can do all of the following, skip the recommended prerequisites and start here.
**If two or more items block you**, going back to the lesson in parentheses is faster.

1. In the plane, what is the torque about the origin of a force $f = (0, 2)$ applied at
   $p = (1, 0)$? In space, with $p = (1,0,0)$ and $f = (0,0,3)$, what is the torque vector?
   (`c1-twists-wrenches-adjoint`)
   **Answer**: in the plane $\tau = p_x f_y - p_y f_x = 1\cdot2 - 0 = 2$; in space
   $\tau = p \times f = (0\cdot3 - 0\cdot0,\ 0\cdot0 - 1\cdot3,\ 0) = (0, -3, 0)$.
2. Write the Coulomb friction cone in terms of the normal force $f_n$ and the tangential force $f_t$,
   and explain in one line why its half-angle is $\arctan\mu$. (`c2-contact-dynamics`)
   **Answer**: $FC = \{(f_n, f_t) : \lVert f_t \rVert \le \mu f_n,\ f_n \ge 0\}$. On the cone's
   surface $\lVert f_t\rVert / f_n = \mu$, and that ratio is the tangent of the angle measured from
   the normal, so the half-angle is $\arctan\mu$.
3. Four points in $\mathbb{R}^3$ are given. Write "the origin is in the **interior** of their convex
   hull" as linear equalities and inequalities. (`r0-convex-optimization`)
   **Answer**: there exists $\lambda$ with $\sum_j \lambda_j w_j = 0$, $\sum_j \lambda_j = 1$ and
   $\lambda_j > 0$ (all **strictly** positive). In addition the points must **affinely span**
   $\mathbb{R}^3$, or the interior is empty.
4. State the separating hyperplane theorem for a convex set $K$ and a point $x \notin K$.
   (`r0-convex-optimization`)
   **Answer**: if $K$ is closed and convex and $x \notin K$, there are $u \ne 0$ and $c$ with
   $u^\top x > c \ge u^\top y$ for all $y \in K$. For a cone one can take $c = 0$.
5. Can the rows of an $m \times 3$ matrix of rank less than 3 positively span $\mathbb{R}^3$?
   (`r0-linear-algebra-decompositions`)
   **Answer**: no. Positive spanning implies linear spanning, so the rank must be 3. That is why the
   LP test needs a **separate** rank condition (§R1).

If all five went through, go straight to `## Key results`. If 2 or 4 blocked you, read
`r0-convex-optimization` first; if 1 did, read `c1-twists-wrenches-adjoint`.

## Key results

The bracket is the derivation depth (D0 cited / D1 sketched / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (convex-geometry test for force closure) [D3]** — under (A1) and (A2), with the friction cone
  discretized into $k$ edges to give the wrench generators $W$, the following are **equivalent**:
  (a) the grasp is force closure; (b) $\mathrm{cone}(W) = \mathbb{R}^{d'}$ ($d' = 3$ in the plane,
  $6$ in space); (c) **the origin lies in the interior of $\mathrm{conv}(W)$**; (d) there is **no**
  $u \ne 0$ with $u^\top w_j \le 0$ for all $j$. The test is therefore the **linear program**
  $$\max_{\lambda,\,\epsilon}\ \epsilon \quad \text{s.t.}\quad
    W^\top \lambda = 0,\ \ \mathbf{1}^\top\lambda = 1,\ \ \lambda_j \ge \epsilon,\ \ \epsilon \ge 0
    \tag{2}$$
  and force closure holds $\iff$ $\mathrm{rank}\,W = d'$ **and** $\epsilon^\ast > 0$. The rank
  condition is not absorbed by the LP — and the discretization is **conservative** (an inner
  approximation of the cone).
- **R2 (the Ferrari–Canny metric and its non-monotonicity) [D2]** — normalizing the magnitude of the
  contact forces, the quality metric is the radius of the largest origin-centred inscribed ball,
  $$Q = \min_{\text{facets } (a,b) \text{ of } \mathrm{conv}(W)} \frac{-b}{\lVert a\rVert}
    \qquad (a^\top x + b \le 0) \tag{3}$$
  with $Q > 0 \iff$ force closure. For an **antipodal** pair of contacts on the unit disc it has the
  closed form
  $$Q(\mu) \;=\; \frac{\sin\alpha\,\cos\alpha}{\sqrt{1 + \cos^2\alpha}},
    \qquad \alpha = \arctan\mu \tag{4}$$
  which is **not monotone** in $\mu$: it peaks at $\mu^\ast = 2^{1/4} = 1.189207115$ with
  $Q_{\max} = \sqrt2 - 1 = 0.414213562$ and decreases thereafter.
- **R3 (separating caging from force closure) [D2]** — caging is a property of **configuration space,
  not of forces**: treating the fingers as obstacles, the configuration is a cage if the free
  component of the object's configuration space $\mathcal{C}_{\mathcal{B}}$ containing it is
  **bounded**. Neither property implies the other — there are configurations that cage without force
  closure (a loose cage) and configurations with force closure that do not cage (two points held by
  friction alone). But **some cages converge to force closure as the fingers close**, and identifying
  that class is the result of
  [Rodriguez et al. 2012](https://doi.org/10.1177/0278364912442972).
- **R4 (frictionless lower bounds) [D1]** — with $\mu = 0$ the minimum number of contacts for force
  closure is 4 in the plane and 7 in space
  ([Mishra, Schwartz & Sharir 1987](https://doi.org/10.1007/bf01840373)). And **a disc or a sphere
  can never be force closure without friction, however many contacts are used** — every normal passes
  through the centre, so the torque component vanishes identically (the failure mode of §R1).

## Derivation

### R1 — from friction cones to wrench generators

**The contact wrench.** Applying a force $f_i$ at contact $i$ exerts on the object the wrench

$$
w_i(f_i) \;=\; \begin{bmatrix} f_i \\ p_i \times f_i \end{bmatrix}
  \quad (d = 3), \qquad
w_i(f_i) \;=\; \begin{bmatrix} f_i \\ p_{i,x} f_{i,y} - p_{i,y} f_{i,x} \end{bmatrix}
  \quad (d = 2).
  \tag{5}
$$

$w_i$ is **linear** in $f_i$. So as $f_i$ ranges over the convex cone $FC_i$, $w_i$ ranges over a
convex cone too, and the set of wrenches the whole hand can apply is their **Minkowski sum**

$$
\mathcal{W} \;=\; \Big\{\textstyle\sum_i w_i(f_i) \;:\; f_i \in FC_i\Big\}
  \;=\; \mathrm{cone}\Big(\bigcup_i w_i(\mathrm{ext}\,FC_i)\Big)
  \tag{6}
$$

The second equality is **the justification for discretizing**: the Minkowski sum of convex cones
equals the cone positively spanned by each cone's **extreme rays**. In the plane $FC_i$ has exactly
two extreme rays ($\hat n_i$ rotated by $\pm\alpha$); in space it has **infinitely many** (the cone's
rim is a circle). So in space one takes an **inner approximation** with $k$ edges, and that
approximation is always conservative ($\mathcal{W}_k \subseteq \mathcal{W}$, so "a verdict of force
closure is true, while a verdict of no force closure may be wrong").

**Relating (1) to $\mathcal{W}$.** Equation (1) says "$-w_{ext} \in \mathcal{W}$". Since $w_{ext}$ is
arbitrary,

$$
\text{force closure} \iff \mathcal{W} = \mathbb{R}^{d'},
  \tag{7}
$$

which is (a) $\iff$ (b). That is the first equivalence of R1; the rest is convex geometry
(§Proof sketch).

**Three places the assumptions break.**

1. **Frictionless grasp of a disc or sphere.** On the unit disc with contacts $p_i$ and inward
   normals $\hat n_i = -p_i$, a frictionless force is $f_i = \lambda_i \hat n_i \parallel p_i$ and its
   torque is $p_{i,x}f_{i,y} - p_{i,y}f_{i,x} =
   \lambda_i(p_{i,x}(-p_{i,y}) - p_{i,y}(-p_{i,x})) = 0$. **Every generator has zero torque**, so
   $\mathrm{rank}\,W \le 2 < 3$ and no number of contacts gives force closure. Criterion 2 of the
   reproduction task checks this up to $n = 12$.
2. **Surface contact.** Dropping the point-contact part of (A1) makes the contact region
   two-dimensional and the "extreme rays" no longer a finite set. The standard workaround is a
   **soft-finger** model (adding a normal-torque term) or a polygonal approximation, after which the
   LP (2) is used unchanged; only the **size of the conservatism** changes.
3. **Bounded contact force.** Dropping (A2) makes force closure less useful as a binary verdict,
   because resisting an arbitrarily large disturbance needs an arbitrarily large contact force. So
   practice adds a normalization like $\sum_i f_{n,i} \le 1$ and measures **how large a disturbance
   is resisted** — which is the $Q$ of R2.

### R2 — the Ferrari–Canny metric

**Definition.** Normalize the contact forces. With the $L^1$ normalization
$\sum_i f_{n,i} \le 1$ the set of applicable wrenches is $\mathrm{conv}(W \cup \{0\})$; with the
$L^\infty$ normalization $f_{n,i} \le 1$ it is the Minkowski sum of the per-contact hulls. Either way
one gets a **bounded convex polytope** $P$, and

$$
Q \;=\; \max\{\,r \ge 0 \;:\; B(0, r) \subseteq P \,\}.
  \tag{8}
$$

For a polytope, $B(0,r) \subseteq P$ means "every facet is at distance at least $r$", and with a facet
written $a^\top x + b \le 0$ (so $b < 0$ when the origin is on its inner side) the distance from the
origin to it is $-b/\lVert a\rVert$. Taking the minimum gives (3). Since
**$Q > 0 \iff$ the origin is interior $\iff$ force closure**, $Q$ is the **continuous extension** of
the binary verdict.

**Closed form for an antipodal grasp of the unit disc.** With $p_1 = (1,0)$, $p_2 = (-1,0)$ and
inward normals $\hat n_1 = (-1,0)$, $\hat n_2 = (1,0)$, the extreme rays are the normals rotated by
$\pm\alpha$, and computing torques from (5) gives the four generators

$$
\begin{aligned}
A_\pm &= (-\cos\alpha,\ \mp\sin\alpha,\ \mp\sin\alpha), \\
B_\pm &= (\ \ \cos\alpha,\ \pm\sin\alpha,\ \mp\sin\alpha).
\end{aligned}
  \tag{9}
$$

(Check the signs yourself — the torque is $+1\cdot f_y$ at $p_1$ and $-1\cdot f_y$ at $p_2$.) The
four points sum to zero, so **the origin is the centroid of this tetrahedron** and all four facets are
equidistant from it. Taking the cross product for the facet through $A_+, A_-, B_+$,

$$
(A_- - A_+)\times(B_+ - A_+) = (0, 2s, 2s)\times(2c, 2s, 0) = (-4s^2,\ 4sc,\ -4sc),
  \qquad s = \sin\alpha,\ c = \cos\alpha,
$$

and since it passes through $A_+$ the constant term is
$(-4s^2)(-c) + (4sc)(-s) + (-4sc)(-s) = 4s^2c$. The distance from the origin is therefore

$$
\frac{4s^2 c}{\lVert(-4s^2, 4sc, -4sc)\rVert} = \frac{4s^2c}{4s\sqrt{s^2 + 2c^2}}
  = \frac{sc}{\sqrt{s^2 + 2c^2}} = \frac{\sin\alpha\cos\alpha}{\sqrt{1 + \cos^2\alpha}},
$$

which is (4) (using $s^2 + 2c^2 = 1 + c^2$). Numerical check: at $\mu = 1$, $\alpha = \pi/4$ and
$Q = \tfrac12/\sqrt{3/2} = 1/\sqrt6 = 0.408248290$.

**Non-monotonicity.** Setting $u = \cos^2\alpha$ gives $Q^2 = u(1-u)/(1+u)$, and

$$
\frac{d}{du}\frac{u(1-u)}{1+u} = \frac{1 - 2u - u^2}{(1+u)^2} = 0
  \;\Longrightarrow\; u^2 + 2u - 1 = 0 \;\Longrightarrow\; u = \sqrt2 - 1.
$$

Then $\tan^2\alpha = (1-u)/u = (2-\sqrt2)/(\sqrt2-1) = \sqrt2$, so $\mu^\ast = \tan\alpha = 2^{1/4}$,
and $Q_{\max}^2 = u(1-u)/(1+u) = (\sqrt2-1)^2$ gives $Q_{\max} = \sqrt2 - 1$. **More friction does
not make the grasp better.**

**Where the assumption breaks — $Q$ depends on units.** The "ball" of (3) treats force and torque
components in the **same units**. In reality force is in N and torque in N·m, so $Q$ depends on the
choice of a **characteristic length** (the torque must be normalized as $\tau/\ell$). Whether $\ell$
is taken as the object diameter or the grasp width **can reverse the ranking of two grasps**. And the
non-monotonicity of (4) is itself a consequence of taking the extreme-ray vectors to be **unit
length** — normalizing instead to unit normal force ($f_n = 1$, i.e. scaling the rays by
$1/\cos\alpha$) makes $Q$ monotonically increasing in $\mu$. Problem P5 covers this.
**Comparing metrics without stating the normalization is meaningless** — it becomes a problem when
labels for learned grasping are generated, and returns in `s2-learned-grasping`.

### R3 — caging: configuration space, not force

**Definition.** Treat the fingers as fixed obstacles and consider the configuration space of the
**object**, $\mathcal{C}_{\mathcal{B}}$ (which is $\mathbb{R}^2 \times S^1$ for a planar rigid body,
`c6-cspace-complexity` R2). If the free component
$\mathcal{F}(q_0) \subseteq \mathcal{C}_{\mathcal{B},free}$ containing the current configuration
$q_0$ is **bounded**, the configuration **cages** $q_0$. Meaning: the object cannot get arbitrarily
far away without passing through a finger.

**The two properties are independent.** All four combinations occur.

| | force closure | not force closure |
|---|---|---|
| **cage** | a disc held firmly by three fingers | four loose fingers around a disc (it can move but cannot escape) |
| **not a cage** | an antipodal pair held by friction ($\mu > 0$, R2) — spread the fingers and the object leaves | a single point contact |

The three cells other than the bottom right are the point. In particular, **an antipodal two-point
grasp is force closure but not a cage** — its free component is unbounded (push the object
tangentially and it recedes while keeping contact). Conversely a loose cage resists no wrench at all
yet never loses the object. Reading **force closure as "blocks any disturbance immediately" and caging
as "never loses it in the end"** keeps the distinction.

**Why caging is useful.** Force closure demands the **exact** contact positions and normals, which is
sensitive to perception error. Caging is an **open condition** on position error (boundedness of the
free component survives small finger motions), so it can be used under uncertainty. Rodriguez et al.
go one step further and identify **the class of cages that converge to force closure when the fingers
are tightened**, which gives a guarantee to the strategy "cage first, then squeeze".

**Where the assumption breaks**: deciding a cage is a **topological** computation on configuration
space, so it inherits the cost of `c6-cspace-complexity` R4 — feasible for a planar rigid body
(3-dimensional C-space) but with no practical algorithm for a spatial body (6-dimensional) plus an
articulated hand. And "bounded" is a condition that **uses no friction at all**, so it is excessively
conservative when friction is present (it declares a friction-only configuration not to be a cage).

## Proof sketch

### R1 — equivalence of the four conditions

**Hypotheses** H1: (A1) and (A2). H2: the generator set $W$ is finite and each $w_j$ comes from an
extreme ray of some $FC_i$ through (5). H3: wrench space is $\mathbb{R}^{d'}$ and the contact forces
can be chosen **independently**.
**Conclusion** C: (a) $\iff$ (b) $\iff$ (c) $\iff$ (d), and the LP (2) decides (c).

**Strategy**: (a)$\Leftrightarrow$(b) is unfolding the definition, (b)$\Leftrightarrow$(d) is the
**separating hyperplane**, (c)$\Leftrightarrow$(d) relates the cone to the convex hull, and
(c)$\Leftrightarrow$LP is a restatement of the definition.

1. **(a) $\Leftrightarrow$ (b).** Equation (1) is equivalent to $-w_{ext} \in \mathcal{W}$
   (derivation (7)). Holding for every $w_{ext}$ $\iff$ $\mathcal{W} = \mathbb{R}^{d'}$.
2. **(b) $\Rightarrow$ (d).** If $u \ne 0$ satisfies $u^\top w_j \le 0$ for all $j$, then
   $u^\top w \le 0$ for every positive combination too, so
   $\mathcal{W} \subseteq \{w : u^\top w \le 0\}$ and $\mathcal{W} \ne \mathbb{R}^{d'}$. The
   contrapositive is (b)$\Rightarrow$(d).
3. **(d) $\Rightarrow$ (b).** $\mathcal{W}$ is a finitely generated convex cone and hence **closed**
   (Minkowski–Weyl). If $\mathcal{W} \ne \mathbb{R}^{d'}$ there is some $v \notin \mathcal{W}$, and
   applying the separating hyperplane theorem to a closed convex cone and an outside point yields
   $u \ne 0$ with $u^\top v > 0 \ge u^\top w$ for all $w \in \mathcal{W}$. In particular
   $u^\top w_j \le 0$ for all $j$, so (d) is false. **Closedness is decisive here** — without finite
   generation (the surface contact of failure mode 2) this step can collapse.
4. **(c) $\Leftrightarrow$ (d).** Suppose $0 \notin \mathrm{int}\,\mathrm{conv}(W)$. Then a separating
   (or supporting) hyperplane for $\mathrm{conv}(W)$ and $\{0\}$ exists, giving $u \ne 0$ with
   $u^\top w_j \le 0$ for all $j$. Conversely, if such a $u$ exists then $\mathrm{conv}(W)$ lies in
   the half-space $\{u^\top x \le 0\}$ and the origin is not interior.
5. **(c) $\Leftrightarrow$ LP.** $0 \in \mathrm{int}\,\mathrm{conv}(W)$ is equivalent to "there is a
   $\lambda$ with $\sum\lambda_j w_j = 0$, $\sum\lambda_j = 1$, $\lambda_j > 0$, and $W$ affinely
   spans $\mathbb{R}^{d'}$". The first is $\epsilon^\ast > 0$ in (2) and the second is
   $\mathrm{rank}\,W = d'$. **The LP cannot see the rank condition**: if all generators lie in one
   subspace, $\epsilon^\ast > 0$ can hold without force closure (the frictionless disc is exactly
   that case — a symmetric $\lambda$ sums to zero). So an implementation must do **both** checks.

**Removing a hypothesis**: dropping the independence of H3 (one actuator driving two fingers
together) makes the set of applicable wrenches a **subset** of a cone rather than a cone, so (6) is no
longer an equality and (2) gives only a **necessary** condition. Dropping the finiteness of H2
requires rebuilding the closedness argument of step 3. Dropping the rigidity of H1 breaks the
linearity of (5) itself (the $p_i$ move as the body deforms).

## Problem set

Difficulty: ★ 15 min / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Prove the second equality of (6) — that the Minkowski sum of convex cones
equals the positive span of their extreme rays. Then write why a planar contact has exactly two
extreme rays while a spatial contact has infinitely many.
*Solution sketch*: write each $f_i \in FC_i$ as a non-negative combination of extreme rays and use the
linearity of $w_i$. The reverse inclusion holds because the extreme rays themselves lie in $FC_i$. A
planar cone is two-dimensional so it has two extreme rays; a spatial cone has a circular cross-section
so its extreme points form a continuum.

**P2 (derivation, ★★, R2)** Derive the four generators of (9) including the signs, and verify that
they sum to zero. Then rewrite (4) in terms of $\mu$ as
$Q(\mu) = \mu/\big((1+\mu^2)\sqrt{1 + 1/(1+\mu^2)}\big)$ and show $Q \to 0$ as $\mu \to \infty$.
*Solution sketch*: substitute $s = \mu/\sqrt{1+\mu^2}$ and $c = 1/\sqrt{1+\mu^2}$ into (4). As
$\mu \to \infty$, $c \to 0$ and the numerator $sc \to 0$ — include the geometric meaning, that
**the extreme rays lie down towards the tangent direction and lose their normal component**.

**P3 (numerical, ★, R2)** For an antipodal grasp of the unit disc, compute $Q$ from (4) at
$\mu = 0.1,\ 0.5,\ 1,\ 2$, and find the $\mu^\ast$ maximizing $Q$ together with $Q_{\max}$.
*Answer*: $Q(0.1) = 0.070184512$, $Q(0.5) = 0.298142397$, $Q(1) = 1/\sqrt6 = 0.408248290$,
$Q(2) = 0.365148372$. The maximum is at $\cos^2\alpha = \sqrt2 - 1$, i.e.
$\mu^\ast = 2^{1/4} = 1.189207115$, with $Q_{\max} = \sqrt2 - 1 = 0.414213562$. Tolerance $10^{-9}$.
Check: $Q(1) < Q(\mu^\ast)$ and $Q(2) < Q(1)$ — confirm the **non-monotonicity** numerically.

**P4 (numerical, ★★, R1)** With two contacts on the unit disc at angles $\theta_1, \theta_2$, write
the force-closure condition in terms of $\Delta\theta$ and $\alpha$, and find in closed form the
probability of force closure when $\theta_1, \theta_2$ are independent and uniform.
*Answer*: the triangle $O p_1 p_2$ is isosceles with apex angle $\Delta\theta$ (the angular difference
folded into $[0,\pi]$), so its base angles are $(\pi - \Delta\theta)/2$. The chord lies inside both
friction cones iff $(\pi - \Delta\theta)/2 \le \alpha$, i.e. $\Delta\theta \ge \pi - 2\alpha$. Since
$\Delta\theta$ is uniform on $[0,\pi]$,
$$\mathbb{P}[\text{force closure}] = \frac{2\alpha}{\pi} = \frac{2\arctan\mu}{\pi},$$
exactly $1/2$ at $\mu = 1$. Tolerance: within $\pm 2\,\mathrm{SE}$ over $2\times10^4$ Monte Carlo
trials (measured $0.0625/0.1250/0.2951/0.4991$ at $\mu = 0.1/0.2/0.5/1.0$ against predictions
$0.063451/0.125666/0.295167/0.500000$, maximum $z = 0.55$).

**P5 (counterexample/proof, ★★, R2)** Show that the non-monotonicity of $Q$ comes from the
**normalization of the extreme rays**: recompute (4) with the rays scaled to unit **normal** component
($f_n = 1$, i.e. length $1/\cos\alpha$) and show the resulting metric increases monotonically in
$\mu$. Answer which normalization is "correct", and explain that the answer **depends on the problem
setting**.
*Property checklist*: the new metric is $Q/\cos\alpha = \sin\alpha/\sqrt{1+\cos^2\alpha}$, increasing
in $\alpha$. The "correct" normalization depends on whether the actuator limit applies to the
**normal force** (then $f_n = 1$) or to the **total force magnitude** (then unit rays). Note that the
characteristic length $\ell$ for the torque must be declared as well.

**P6 (proof, ★★, R1)** Make the claim of step 5 of the R1 proof concrete — that the LP cannot see the
rank condition — using the frictionless unit disc. For $n$ equally spaced contacts, construct an
explicit $\lambda$ with $\epsilon^\ast > 0$ and say why force closure nevertheless fails.
*Strategy*: taking $\lambda_j = 1/n$ gives
$\sum \lambda_j w_j = (\frac1n\sum \hat n_j,\ 0) = (0, 0)$ (the normals sum to zero by symmetry), so
the LP (2) returns $\epsilon^\ast = 1/n > 0$. But every generator has zero torque, so
$\mathrm{rank}\,W = 2$ and no torque disturbance can be resisted.

**P7 (implementation, ★★, R1·R2)** Write the LP tester and the $Q$ calculator of the reproduction
task. Requirements: the LP of (2) via `scipy.optimize.linprog(method="highs")`, a rank check, and (3)
via `scipy.spatial.ConvexHull`.
*Rubric*: (a) the numbers of criteria 1, 2 and 3 match; (b) you show that **removing** the rank check
makes the frictionless disc be misclassified as force closure; (c) you check that $Q$ and the LP's
$\epsilon^\ast$ agree in **sign** and explain why their magnitudes differ; (d) for spatial contacts
(cone discretized into $k$ edges) you show that increasing $k$ from 8 to 32 changes verdicts in one
direction only (conservatism).

**P8 (paper, ★★, R2·R3)** Read Ferrari & Canny 1992 and Rodriguez et al. 2012 and (a) transcribe
exactly the normalization Ferrari–Canny use and compare it with (3) here; (b) state for which class
Rodriguez et al. prove that "tightening a cage converges to force closure", and whether the condition
identifying that class is **computable**.
*Rubric*: for (a), pass if you identify the difference between the $L^1$ and $L^\infty$
normalizations and the torque scaling. For (b), pass if you identify that the result is not about
**all** cages. Writing only "it is a good metric" fails.

## Paper reading

**Two must-reads.** Write a one-page note on each using the ten fixed questions
(`lesson-standard.md` §5).

1. **Ferrari & Canny, "Planning optimal grasps" (1992, ICRA)** — role: `seminal`.
   <https://doi.org/10.1109/ROBOT.1992.219918> (§2–3)
   *Why read it*: the $Q$ of R2 comes from here. The point is **where the normalization is chosen**
   (total force versus per-contact force) and how that choice changes the optimal grasp.
   Extra questions: (a) what changes if their metric is rewritten in the form of (3)? (b) how is the
   unit of the torque component handled (does a characteristic length appear)? (c) is finding the
   "optimal" grasp a convex problem?
2. **Rodriguez, Mason & Ferry, "From caging to grasping" (2012, IJRR)** — role: `standard`.
   <https://doi.org/10.1177/0278364912442972> (§1–2, §6)
   *Why read it*: the source of R3, and the only primary source defining caging as **boundedness in
   configuration space** and connecting it to force closure. It is also the theoretical basis for
   grasping strategies under uncertainty.
   Extra questions: (a) transcribe the authors' definition of a "grasping cage" and compare it with
   the table in R3 here. (b) what is the dimensional limit of their decision algorithm? (c) how do the
   authors handle the conservatism of a condition that uses no friction?

**The ten fixed questions**: (1) what problem, under what assumptions? (2) what exactly could prior
work not do? (3) the core idea in one equation or one figure. (4) what is guaranteed theoretically,
and **what is not**? (5) the independent and dependent variables and the baselines, and were the
baselines tuned fairly? (6) does the metric match the claim, and are variance and seeds reported?
(7) what is missing for reproduction? (8) if the result were wrong, which assumption would you doubt
first? (9) computational and memory complexity, and real-time feasibility. (10) what would you change
to go beyond this paper in a year?

## Reproduction task

**Tier R2 (re-implementation).** Budget: one laptop CPU core, under 5 minutes in total, under 1 GB of
memory. numpy plus scipy (`optimize.linprog`, `spatial.ConvexHull`) only. No external data.

**Input data (given by the lesson).** The object is the **unit disc**. Contacts are given by angles
$\theta_i$ on its boundary, with inward normals $\hat n_i = -p_i$ (pointing at the centre). The
friction cone is planar, so it has two extreme rays and each contact contributes two generators.
Wrenches use the planar form of (5).

**Acceptance criteria — all four must hold.**

1. **Against the closed form (checking R2)** — for the antipodal pair ($\theta = 0, \pi$), the $Q$
   computed from (3) agrees with the closed form (4) to a relative error of $10^{-12}$. Specifically

   | $\mu$ | 0.0 | 0.1 | 0.3 | 0.5 | 1.0 | 2.0 |
   |---|---|---|---|---|---|---|
   | $Q$ | 0 | 0.070184512 | 0.198762689 | 0.298142397 | 0.408248290 | 0.365148372 |

   and at $\mu^\ast = 2^{1/4}$ you obtain $Q = \sqrt2 - 1$ to a relative error of $10^{-9}$.
   **Write one paragraph in the report on the non-monotonicity $Q(2.0) < Q(1.0)$.**
2. **The frictionless disc (checking the failure mode of R1 and R4)** — at $\mu = 0$, all of
   $n \in \{2,3,4,6,12\}$ equally spaced contacts are classified as **not** force closure, with
   $\mathrm{rank}\,W \le 2$ and every generator's torque component zero to within $10^{-15}$.
   Also show that **turning the rank check off** yields $\epsilon^\ast = 1/(2n) > 0$ and a
   misclassification (P6).
3. **The feasible-region chart (the blueprint task)** — drawing contacts independently and uniformly
   from $[0, 2\pi)$ ($n$ of them, seed $s\cdot97 + n$ for $s = 0..1999$), the force-closure fraction
   is

   | $\mu$ | $n=1$ | $n=2$ | $n=3$ | $n=4$ |
   |---|---|---|---|---|
   | 0.0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
   | 0.1 | 0.0000 | 0.0585 | 0.3325 | 0.5805 |
   | 0.2 | 0.0000 | 0.1245 | 0.4195 | 0.6520 |
   | 0.5 | 0.0000 | 0.2940 | 0.6245 | 0.8270 |
   | 1.0 | 0.0000 | 0.5030 | 0.8060 | 0.9405 |

   to within an absolute error of 0.02. The $n = 1$ column must be **exactly 0 at every $\mu$**.
4. **Against the closed form (checking P4)** — the $n = 2$ column agrees with the closed form
   $\frac{2}{\pi}\arctan\mu$. Increasing the trials to $2\times10^4$, the measurements
   $0.0625/0.1250/0.2951/0.4991$ at $\mu = 0.1/0.2/0.5/1.0$ agree with the predictions
   $0.063451/0.125666/0.295167/0.500000$ within $|z| \le 1$ (where
   $z = |\hat p - p|/\mathrm{SE}$; the measured maximum is $z = 0.55$).

**Baselines.** (a) The closed forms (4) and $\frac2\pi\arctan\mu$ — criteria 1 and 4. (b) Two
independent verdicts: check that $\epsilon^\ast > 0$ from the LP and $Q > 0$ from the convex hull give
**the same conclusion** on all 2000 random configurations (zero disagreements). (c) A deliberately
broken version of itself: the rank check removed — criterion 2.

**Failure table**

| Symptom | Cause | How to check |
|---|---|---|
| the frictionless disc comes out as force closure | the rank check was skipped and only the LP result used | print the singular values of the generator matrix and check the third is of order $10^{-15}$ |
| $Q$ differs from the closed form | the extreme rays were normalized to unit normal force rather than unit length (P5) | first match $1/\sqrt6$ at $\mu = 1$ |
| the torque sign is flipped | the planar torque was written $p_y f_x - p_x f_y$ | check that $\tau = +1$ for $p = (1,0)$, $f = (0,1)$ |
| the $n = 2$ fraction is twice the closed form | $\Delta\theta$ was taken in $[0, 2\pi)$ and not folded into the apex angle | check that the histogram of $\Delta\theta$ is uniform on $[0,\pi]$ |
| ConvexHull raises an exception | the generators are degenerate (frictionless) and no 3D hull exists | handle the exception as $Q = 0$ and report the rank separately |
| the fractions change between runs | the seed was not created inside the loop | run the same command twice and check the table is identical |

## Open problems

- **(open problem) Normalization invariance of quality metrics** — as the failure mode of R2 shows,
  $Q$ depends on the force normalization and on the characteristic length for the torque, so
  **grasp-quality numbers from different papers cannot be compared.** Since the labels for learned
  grasping are generated with this metric, the problem passes straight into the data
  (`s2-learned-grasping`). Current approaches: surveys that require the metric to be reported with
  its definition ([Bicchi & Kumar 2000](https://doi.org/10.1109/ROBOT.2000.844081),
  [Prattichizzo & Trinkle 2016](https://doi.org/10.1007/978-3-319-32552-1_38)). What is missing: a
  grasp-quality measure invariant to units and normalization.
- **(open problem) Force closure under uncertainty** — the test (3) assumes the contact positions and
  normals are known **exactly**. Deciding "force closure with probability $1-\gamma$" under a
  perception error $\pm\delta$ is non-convex, and practice approximates it by sampling perturbations
  (the robust metric of Dex-Net). Current approaches: using the open condition of caging
  ([Rodriguez et al. 2012](https://doi.org/10.1177/0278364912442972)), and handling contact
  perturbation by second-order mobility
  ([Rimon & Burdick 1998](https://doi.org/10.1109/70.720346)). What is missing: a **certifiable**
  grasp test with perception error modelled explicitly.
- **(open problem) The wrench set for surface contact and deformable bodies** — dropping (A1) breaks
  the finite generation of (6) and the closedness argument of step 3 of the proof must be rebuilt. The
  soft-finger approximation is a stopgap that merely adds generators, and for large deformations (soft
  grippers) the wrench set itself varies with configuration. Current approaches: the classical model
  approximating the contact region by a polygon, and differentiable contact models
  (`c2-contact-dynamics`). What is missing: a computable convex approximation of the wrench set for a
  deformable grasp.

## Concept check

Run `rc quiz s2-grasp-mechanics`. The quiz is for **concept checking only**; the real work is the
problem set and the reproduction task above (`lesson-standard.md` §4).

The six items cover: why the LP's $\epsilon^\ast > 0$ is not enough without the rank condition; why a
frictionless disc can never be grasped; the friction coefficient maximizing the Ferrari–Canny metric;
how caging and force closure relate; which way cone discretization errs; and the closed-form
force-closure probability for two contacts on a disc.

## How to study this stage

1. **Separate force from motion first (20 min)** — write "force closure = positively spans wrench
   space" and "caging = the free component of configuration space is bounded" on one page, and fill in
   the 2×2 table of R3 yourself. Being able to fill that table is half of this lesson.
2. **Memorize the four equivalences, one line each (60 min)** — rewrite (a)–(d) of R1 and the
   justification of each arrow (unfolding the definition / separating hyperplane / closedness of the
   cone) from a blank page. Identifying where **closedness** is used is the crux — that is the spot
   that breaks for surface contact.
3. **Get the closed form by hand (50 min)** — do P2 and P3. Match the signs of the four generators of
   (9) yourself and compute the facet distance to obtain (4). Then confirm the non-monotonicity and
   $\mu^\ast = 2^{1/4}$ by differentiation. **Until you differentiate the metric by hand you will not
   give up the intuition that more friction is better.**
4. **Meet the normalization trap (30 min)** — do P5. Confirm by computation that the same grasp is
   ranked differently under different normalizations, and note that this becomes the label problem of
   learned grasping (revisited in `s2-learned-grasping`).
5. **Implement it, and the broken version too (80 min)** — the reproduction task. Match criterion 1
   (the closed form) first, then **deliberately remove the rank check** in criterion 2 and watch the
   frictionless disc be misclassified. Draw the table of criterion 3 to see with your own eyes how the
   number of contacts and the friction widen the feasible region.
6. **Two papers (120 min)** — read them 1992 → 2012. The 1992 paper gives the metric and the 2012 one
   gives a way to **circumvent** the exactness that metric demands. Organize them in your notes as the
   contrast "an exact force condition versus an open topological condition".
7. **Problem set (150 min)** — P3, P4 and P7 first, then P1 and P2, then P5, P6 and P8 with whatever
   time remains. P5 (normalization) is the item that causes the most trouble in practice.

**Passing bar**: you can prove the four equivalences of R1 from a blank page, derive (4) by hand to
obtain $\mu^\ast = 2^{1/4}$ and $Q_{\max} = \sqrt2-1$, have code satisfying the four criteria of the
reproduction task, and fill in the 2×2 table of caging versus force closure with examples. You have
notes on both papers.
