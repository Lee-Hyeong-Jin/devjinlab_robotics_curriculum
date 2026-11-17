---
id: s1-semantic-scene-graphs
lang: en
title: Semantic and object-level SLAM
summary: >-
  Derive, from the standpoint of data association, what is gained and what remains when objects
  rather than points become the unit of the map. Adding the likelihood ratio of a semantic label
  to the error probability $\Phi(-r/2)$ of geometry-only association reduces the error in closed
  form, and in the limit where geometry becomes ambiguous that error converges to the error rate
  $1-q$ of the classifier. Between objects of the same class semantics contribute nothing and the
  confusion remains; in a localization experiment on an object map, measure that the association
  error drops from 6.2% to 2.9% but that the gain is concentrated on pairs of different classes.
  In the hierarchy of a scene graph, derive that the error of inferring the type of a room from
  its objects decays with the Chernoff exponent and that label noise cuts that exponent.
objectives:
  - Derive the error probability of maximum-a-posteriori association using geometry and semantics together and compare it with geometry alone.
  - Explain through the likelihood ratio why semantic information cannot help association between objects of the same class.
  - Measure the effect of wrong associations on an estimator and explain what probabilistic association changes.
  - Derive the error of hierarchical inference in a scene graph (objects → room) through the Chernoff information and compute the effect of label noise.
  - Measure the association error rate of object-level SLAM and report the gain over geometry alone by a paired comparison.
tags: [slam, semantic-slam, object-slam, data-association, scene-graph, research]
---

# Semantic and object-level SLAM

## Setup and notation

Maps so far were points, surfaces and voxels (`s1-dense-neural-slam`). This lesson raises the
unit of the map to **objects**, and then to the **relations** above them (rooms, floors,
buildings). The problems of data association and false loops are inherited from
`s1-loop-closure-lifelong` — there we saw the damage when place recognition is wrong; here we
compute how much putting semantic information into the association reduces that error, and where
it does not. The recommended prerequisites are `s1-loop-closure-lifelong` and
`s1-dense-neural-slam`.

| Symbol | Meaning |
|---|---|
| $l_j \in \mathbb{R}^2$, $c_j$ | Position and class of object $j$ (one of $C$ classes) |
| $z$, $\ell$ | The geometric measurement of a detection (position relative to the robot) and the label output by the classifier |
| $a$ | The data association — which object of the map the detection came from |
| $\sigma$ | Standard deviation of the prediction error at association time (measurement noise + robot position uncertainty) |
| $\Delta$, $r = \Delta/\sigma$ | The distance between two confusable objects and their **separation ratio** |
| $q$ | Accuracy of the classifier. When wrong, uniform over the other $C-1$ classes |
| $\lambda$ | Log-likelihood ratio of the label. For two classes, $\log\frac{q}{1-q}$ |
| Scene graph | A hierarchical graph: mesh → objects → places → rooms → building. Edges are containment and adjacency relations |

**What changes when objects are the unit.**

| | Point features | Objects |
|---|---|---|
| Size of the map | Tens of thousands to millions of points | Tens to thousands of objects |
| Information in one observation | A bearing, 2 degrees of freedom | Position (and orientation), 3 to 6 degrees of freedom + class |
| Cue for association | Appearance of a descriptor | Geometry + **semantics** |
| Failure mode | Mismatch of points with similar appearance | Confusion between **objects of the same kind** |
| What can be built on top | — | The hierarchy of rooms, floors and buildings; queries; task planning |

## Key results

The bracket gives the derivation depth (D0 cited / D1 skeleton / D2 full derivation / D3 proof —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (the error probability of association with semantics) [D2]** — choosing by geometry alone
  between two objects with separation ratio $r$ has error probability $\Phi(-r/2)$. If the two
  objects are of different classes and the classifier has accuracy $q$, the error of the
  maximum-a-posteriori association that adds the log-likelihood ratios of geometry and label is
  $$
  P_{\mathrm{err}} = q\,\Phi\!\Big(-\frac{r}{2} - \frac{\lambda}{r}\Big)
   + (1-q)\,\Phi\!\Big(-\frac{r}{2} + \frac{\lambda}{r}\Big), \qquad \lambda = \log\frac{q}{1-q}. \tag{1}
  $$
  At $q = 0.9$ this is $0.309 \to 0.099$ for $r = 1$ and $0.067 \to 0.034$ for $r = 3$. As
  $r \to 0$ (geometry separates nothing) $P_{\mathrm{err}} \to 1 - q$ — **semantics replace the
  floor at which geometry collapses by the error rate of the classifier.**
- **R2 (between objects of the same class nothing is gained) [D2]** — if the two candidates have
  the same class, the likelihood ratio of the label is exactly 0 and the error returns to
  $\Phi(-r/2)$. Measured in the reproduction task: with semantics the association error of pairs
  of different classes drops $7.1\% \to 2.0\%$, while pairs of the same class only go
  $5.2\% \to 3.8\%$. **The confusion of object SLAM gathers on repeated things (chairs, doors,
  windows).**
- **R3 (association errors inflate the tail, not the mean) [D2]** — a wrong association is
  "accepting a wrong measurement with full confidence". In localization on 40 maps the mean ATE
  is $0.172$ for geometry alone, $0.146$ with semantics and $0.129$ m for the true association,
  while the **maximum** is $1.05$, $0.37$ and $0.38$ m — semantics close 60% of the mean gap to
  the true association and remove the worst case. Probabilistic association, which spreads
  weights over the candidates instead of committing to one, is the structural defence against
  that tail **[D1]**.
- **R4 (the error of hierarchical inference decays with the Chernoff exponent) [D2]** — with two
  types of room whose distributions of object classes are $p_K$ and $p_O$, the error of inferring
  the type from the $n$ objects in the room satisfies
  $$
  P_{\mathrm{err}}(n) \le e^{-n\,\mathcal{C}}, \qquad
  \mathcal{C} = -\min_{0\le s\le1}\log\sum_c p_K(c)^s\,p_O(c)^{1-s}. \tag{2}
  $$
  For the distributions of this lesson $\mathcal{C} = 0.172$ and the measured error at
  $n = 1, 5, 10, 20$ is $0.199, 0.109, 0.033, 0.004$. With noisy object labels ($q = 0.9$, $0.7$)
  the exponent is cut to $0.123$ and $0.055$ — **a detector of 70% accuracy needs 3.1 times the
  objects for the same confidence.**
- **R5 (the hierarchy reduces the candidates of search and association) [D1]** — the upper layers
  of a scene graph (rooms, buildings) are an **index** of the lower ones. When looking for "the
  mug in the kitchen", choosing the room first cuts the objects to compare to
  $1/(\text{number of rooms})$ of the total, and loop-closure candidates are filtered the same
  way. The price is that if the inference at the upper layer is wrong, everything below searches
  among the wrong candidates (the hierarchical structure of `rosinol2021-kimera`).

## Derivation

### R1 — association using geometry and semantics together

**Setting.** On one axis object 1 is at $0$ and object 2 at $\Delta$. The detection actually came
from object 1 and the geometric measurement is $z \sim \mathcal{N}(0, \sigma^2)$ ($\sigma$
combines the measurement noise and the uncertainty of the robot position). Object 1 has class A
and object 2 class B, and the classifier outputs the true class A with probability $q$ and B with
probability $1-q$.

**Geometry alone.** The likelihood ratio of the two hypotheses is

$$
\log\frac{p(z\mid 2)}{p(z\mid 1)} = \frac{z^2 - (z-\Delta)^2}{2\sigma^2} = \frac{\Delta}{\sigma^2}\Big(z - \frac{\Delta}{2}\Big), \tag{3}
$$

and object 2 is chosen when this is positive (that is, $z > \Delta/2$) — the nearest neighbour.
The error probability is $\Pr[z > \Delta/2] = \Phi(-\Delta/(2\sigma)) = \Phi(-r/2)$.

**Add semantics.** If the label is conditionally independent of the geometry, the log-likelihood
ratios **add**. The contribution of the label is

$$
\log\frac{p(\ell\mid 2)}{p(\ell\mid 1)} = \begin{cases} -\lambda & \ell = \mathrm{A}\ (\text{probability } q) \\ +\lambda & \ell = \mathrm{B}\ (\text{probability } 1-q).\end{cases} \tag{4}
$$

Solving the condition (3)+(4) $> 0$ for $z$ gives $z > \Delta/2 \pm \sigma^2\lambda/\Delta$ —
**the label moves the decision boundary by $\sigma^2\lambda/\Delta$.** A correct label pushes the
boundary towards object 2 and reduces the error; a wrong one pulls it towards object 1 and
increases the error. Mixing the two cases with their probabilities,

$$
P_{\mathrm{err}} = q\,\Pr\Big[\frac{z}{\sigma} > \frac{r}{2} + \frac{\lambda}{r}\Big]
 + (1-q)\,\Pr\Big[\frac{z}{\sigma} > \frac{r}{2} - \frac{\lambda}{r}\Big],
$$

which is (1).

| Separation ratio $r$ | Geometry alone, $\Phi(-r/2)$ | $q = 0.7$ | $q = 0.9$ | $q = 0.99$ |
|---|---|---|---|---|
| $0.5$ | $0.401$ | $0.296$ | $0.100$ | $0.010$ |
| $1$ | $0.309$ | $0.253$ | $0.099$ | $0.010$ |
| $2$ | $0.159$ | $0.139$ | $0.070$ | $0.010$ |
| $3$ | $0.067$ | $0.060$ | $0.034$ | $0.006$ |
| $4$ | $0.023$ | $0.021$ | $0.012$ | $0.003$ |
| $6$ | $0.001$ | $0.001$ | $0.001$ | $0.000$ |

(A simulation of 2 million draws gives $0.3087$ and $0.0985$ at $r = 1$ and $0.0670$ and
$0.0337$ at $r = 3$, in agreement with the table.)

**Three things to read.** (a) The gain of semantics is largest when $r$ is small (nearby
objects, or an uncertain robot position), and the error converges to $1 - q$ — in that limit the
decision is made **by the label alone**. (b) When $r$ is large geometry is already sufficient
and semantics have nothing to add. (c) A weak classifier ($q = 0.7$) hardly helps:
$0.309 \to 0.253$ at $r = 1$. The gain depends on $\lambda$, and $\lambda$ is large only when $q$
is close to 1 ($0.85$ at $q = 0.7$, $2.20$ at $0.9$, $4.60$ at $0.99$).

**The separation ratio is not a fixed number.**
$\sigma^2 = \sigma_z^2 + \sigma_{\text{position}}^2$, and the uncertainty of the robot position
**grows with time** through odometry drift. Two objects $0.5$ m apart in the map have $r = 5$
when the position is well known and $r = 1$ once drift has accumulated. Association gets hard
right after a long stretch of seeing nothing — at the very moment of closing a loop.

**Where the assumptions break**: (a) we used the **conditional independence** of label and
geometry. A real detector gets both the position and the class wrong together on far or occluded
objects (a common cause). Adding (4) as it stands then double counts the evidence — the same
structure as the double counting of `s5-comms-constrained-estimation`. (b) The accuracy $q$ of
the classifier was assumed **known**, and calibrated. The confidence scores of neural networks
are usually overconfident ($q$ is believed higher than it is), which inflates $\lambda$, and then
a wrong label overturns a right geometry (problem P2). (c) There were two candidates. With $M$
candidates the error is roughly a sum over the nearest competitors, and if even one candidate has
the same class we are in R2.

### R2 — objects of the same class

If the two candidates have the same class (both A), $p(\ell\mid 1) = p(\ell\mid 2)$ and (4) is
**0**. Whatever label comes out, the decision boundary stays at $\Delta/2$ and the error is
$\Phi(-r/2)$ — exactly that of geometry alone.

**Measured — localization on an object map.** In a $20\times20$ m area 40 objects are placed as
20 **close pairs** (spacing $0.5$ m). In half the pairs the two objects have different classes
and in half the same. A robot goes twice around a square path (240 steps), detects the objects
within a radius of 4 m, and fuses odometry ($\sigma_o = 0.15$ m per step) and detections
($\sigma_z = 0.10$ m) with a Kalman filter. The map is known and **only the association** is
not. Averages over 40 maps × about 1170 detections:

| Association | Error rate (all) | Pairs of different classes | Pairs of the same class | Mean ATE (m) | Maximum ATE (m) |
|---|---|---|---|---|---|
| Geometry alone (nearest, Mahalanobis) | $6.18\%$ | $7.13\%$ | $5.20\%$ | $0.172$ | $1.051$ |
| Geometry + semantics ($q = 0.9$) | $2.91\%$ | $2.01\%$ | $3.81\%$ | $0.146$ | $0.374$ |
| True association (oracle) | $0$ | $0$ | $0$ | $0.129$ | $0.380$ |

**How to read it.** (a) Semantics cut the overall error to less than half ($6.2\% \to 2.9\%$).
The error rate with semantics is lower on **all** 40 maps, and the paired difference has a mean
of $3.3$ points (standard deviation $1.8$ points, $t = 11.8$) — the paired analysis of
`s1-slam-benchmarking` R5. (b) The gain is **concentrated on the pairs of different classes**:
$7.1\% \to 2.0\%$ (a factor of 3.5). The pairs of the same class improve only a little,
$5.2\% \to 3.8\%$, and even that small improvement is not given by semantics directly but is the
indirect effect of **the robot position being better because the other associations were right**
(the separation ratio $r$ grew). (c) Even as the classifier improves, the wall of the same class
remains:

| Classifier accuracy $q$ | Pairs of different classes | Pairs of the same class |
|---|---|---|
| $0.6$ | $4.86\%$ | $4.09\%$ |
| $0.75$ | $4.05\%$ | $4.10\%$ |
| $0.9$ | $2.01\%$ | $3.81\%$ |
| $0.99$ | $0.71\%$ | $3.00\%$ |

Raising $q$ from $0.6$ to $0.99$ cuts the error on different classes to a seventh, while the
same class goes $4.1\% \to 3.0\%$. **However much the detector is improved, it does not tell
apart things of the same kind.**

**What gets over that wall.** Separating instances within a class needs a cue finer than the
class: (a) instance-level appearance descriptors (this chair versus that chair), (b) the **pose
and shape** of the object (`salas-moreno2013-slampp` holds 3D models of the objects in advance
and fits the full 6-DoF pose — one observation constrains more degrees of freedom, so $r$
grows), (c) **relations to the surroundings** — this chair is next to the desk, that one by the
window. (c) is how the edges of a scene graph are used in association: not one object but a
**subgraph** is matched.

**Where the assumptions break**: in this experiment the map is **given** and fixed. Real object
SLAM estimates the map and the associations together, so a wrong association contaminates the
position estimate of the object, which makes later associations more wrong — the error feeds
itself. And the decision "a new object or an existing one" (map management) is another source of
association error: the same chair is registered twice, or two chairs are merged into one.

### R3 — what a wrong association does to the estimator

**The tail.** In the table above the difference in **maximum** ATE ($1.05$ against $0.37$) is
far larger than the difference in mean ($0.172$ against $0.146$). While the associations are
right the filter moves almost like the true association. Once one is wrong, the wrong
measurement "object $j$ was seen" drags the estimate **while shrinking the covariance** (the
filter does not know it is wrong), and the shrunken covariance narrows the gate of the next
association and pushes out the right candidate. One error starts a chain — the same dynamics as
the false loop of `s1-loop-closure-lifelong`.

**Probabilistic association (skeleton).** Instead of committing to one association, give each
candidate the posterior probability

$$
w_j \;\propto\; p(z\mid a = j)\,p(\ell\mid c_j) \tag{5}
$$

and perform an update **mixed** with those weights. If one candidate is clear, $w$ concentrates
on it and the result equals the committed association; if it is ambiguous the weights are split
and the update is weakened — **trusting less** when ambiguous. Formulating this as
expectation-maximization with the association as a latent variable is
`bowman2017-probabilistic-data-association`: the E step computes the weights (5) and the M step
solves the factor graph with those weights attached. **[D1]**

**Summary.** Three layers of defence against association errors run through the whole of S1:
**making fewer** errors (this lesson — semantics, relations), **accepting** the errors made
**weakly** (probabilistic association, robust kernels — `s1-loop-closure-lifelong`), and
**finding** the errors accepted (goodness-of-fit tests — `s1-certifiable-slam` R5; the
certificate lets plausible wrong associations through).

**Where the assumptions break**: the weights of (5) are right only when the **list** of
candidates is right. If the true object is not yet in the map (a new object), the weights are
normalized over wrong candidates only and every update goes the wrong way. A hypothesis "none of
these" has to be included, and its prior probability becomes one more tuning parameter.

### R4 — hierarchical inference: from objects to rooms

**Setting.** There are two types of room, kitchen (K) and office (O), and for each type the
objects inside come from four classes with the distributions

$$
p_K = (0.5, 0.3, 0.1, 0.1), \qquad p_O = (0.1, 0.2, 0.4, 0.3) \tag{6}
$$

(say the classes are tableware, chair, monitor, book). The type is decided from the classes
$c_1,\dots,c_n$ of the $n$ objects in the room. With equal priors the optimal rule is the sign of
the sum of log-likelihood ratios $\sum_i\log\frac{p_K(c_i)}{p_O(c_i)}$.

**An upper bound on the error.** When the truth is K, an error is the sum being negative. For
any $s \in [0,1]$, by Markov's inequality,

$$
\Pr_K\Big[\sum_i\log\frac{p_O(c_i)}{p_K(c_i)} \ge 0\Big]
 \le \mathbb{E}_K\Big[\prod_i\Big(\frac{p_O(c_i)}{p_K(c_i)}\Big)^{1-s}\Big]
 = \Big(\sum_cp_K(c)^s\,p_O(c)^{1-s}\Big)^n,
$$

(the assumption that the objects are independent turns the product into a power). The same
expression results when the truth is O, so minimizing over $s$ gives (2). $\mathcal{C}$ is the
**Chernoff information**; it measures how distinguishable the two distributions are as "the
exponent of the evidence one object gives".

**Numbers.** For (6), $\mathcal{C} = 0.172$ ($s^\star = 0.507$). With noisy object labels the
observed distribution is blurred to $\tilde{p} = q\,p + (1-q)(1-p)/3$ and the exponent drops:

| Label accuracy $q$ | $\mathcal{C}$ | $n = 1$ | $n = 5$ | $n = 10$ | $n = 20$ | Bound $e^{-20\mathcal{C}}$ |
|---|---|---|---|---|---|---|
| $1.0$ | $0.172$ | $0.199$ | $0.109$ | $0.033$ | $0.004$ | $0.032$ |
| $0.9$ | $0.123$ | $0.239$ | $0.121$ | $0.055$ | $0.013$ | $0.085$ |
| $0.7$ | $0.055$ | $0.320$ | $0.230$ | $0.147$ | $0.069$ | $0.330$ |

(The errors are measured over 200,000 simulations.) **How to read it.** (a) One object gets the
room wrong 20% of the time, but 10 objects 3% and 20 objects 0.4% — inference at the upper layer
is made robust by the **number** below. This is why a hierarchy works even though individual
detections are imperfect. (b) Label noise cuts the exponent: at $q = 0.7$, $\mathcal{C}$ goes
$0.172 \to 0.055$ and the same error needs $0.172/0.055 = 3.1$ times the objects. (c) The bound
(2) is valid but loose (measured $0.004$ against the bound $0.032$ at $n = 20$, $q = 1$) — the
exponent is right and the constant in front differs.

**Where the assumptions break**: (a) the objects were assumed **independent**. Objects of the
same room come together (table and chairs, monitor and keyboard) — the evidence is correlated
and the effective $n$ is smaller than the actual count. (b) The **boundary** of the room was
taken as given. In reality which object belongs to which room has to be inferred first (the
partitioning of the place graph), and if that partition is wrong the objects of the kitchen are
mixed into the tally of the office. Each layer of the hierarchy inherits the errors of the layer
below. (c) The types of room were taken to form a **closed set**. A room of a type not in the
table is classified, with confidence, as the most similar type — the problem of `s4-safety-ood`.

### R5 — what the hierarchy gives (skeleton)

**The 3D dynamic scene graph.** The structure of `rosinol2021-kimera` is layered: a
metric-semantic **mesh** (surfaces carrying geometry and class) → **objects and agents** (poses
and bounding boxes of static objects, trajectories of moving people) → **places** (a topological
graph of free space) → **rooms** → **building**. Edges within a layer are adjacency and
visibility relations, and edges between layers are containment relations.

**The hierarchy as an index.** Suppose $N$ objects are spread evenly over $R$ rooms. For the
query "the mug in the kitchen", a flat search takes $N$ comparisons and a hierarchical one $R$ to
choose the room + $N/R$ for the objects of that room. The sum $R + N/R$ is minimized at
$R = \sqrt{N}$ with value $2\sqrt{N}$, and with $L$ layers it is $L\,N^{1/L}$ — a cost **close
to logarithmic**. The same filtering serves loop closure: choose candidate rooms by a room-level
descriptor (the distribution of object classes) and match geometry only inside them. The number
of candidates of R1 then drops and so does the association error. **[D1]**

**The price.** A hierarchy propagates errors from the top down. If the wrong room is chosen, the
whole search below takes place among wrong candidates, and the room inference of R4 takes the
errors of object association (R1, R2) as its input. And when the map is updated (poses change
through a loop closure), the positions of the mesh, the objects and the rooms have to move
together **consistently** — a deformation of the whole hierarchy is needed, and that is the
problem of scene-graph optimization.

**Where the assumptions break**: the count $R + N/R$ is for objects spread **evenly** over the
rooms and a query that narrows to one room. A query that cannot be narrowed at an upper layer,
such as "a red mug somewhere", is the same as a flat search. And the layers of the hierarchy
(rooms, buildings) belong to indoor environments — a forest, a cave or a road has no "rooms", and
what should define the hierarchy of such environments is open.

## Problem set

The answer policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Derive (1) with no line missing, and (a) find the limits $r \to 0$
and $r \to \infty$, (b) state how $\lambda$ changes when there are $C$ classes and a wrong
classifier output is uniform over the others, and what the decision becomes when the wrong label
is a **third class**.
*Answer sketch*: (a) $r \to 0$: the first term $\to 0$ and the second $\to (1-q)\cdot1$, hence
$1-q$. $r \to \infty$: both go as $\Phi(-r/2) \to 0$, the same as the geometric error.
(b) $\lambda = \log\frac{q}{(1-q)/(C-1)}$ grows (a wrong label is less likely to be one
particular class, so the evidence of a correct label is stronger). If the label is a third
class, neither A nor B, the two hypotheses have equal likelihood and (4) is 0 — the decision is
by geometry alone. So for $C > 2$ a third term appears in (1).

**P2 (derivation, ★★, R1)** Let the actual accuracy of the classifier be $q$ while the estimator
**believes** it to be $\hat{q}$. Generalize (1) to this case, and for $q = 0.8$, $r = 3$ find the
error probability at $\hat{q} \in \{0.6, 0.8, 0.95, 0.999\}$ to show the asymmetry between
**overconfidence** ($\hat{q} > q$) and underconfidence.
*Answer sketch*: only $\lambda$ becomes $\hat\lambda = \log\frac{\hat{q}}{1-\hat{q}}$, while the
mixing probability stays the true $q$:
$q\,\Phi(-r/2 - \hat\lambda/r) + (1-q)\,\Phi(-r/2 + \hat\lambda/r)$. Under overconfidence the
second term (a wrong label overturning a right geometry) grows towards $1 - q$, so the error
**can become worse than with geometry alone**. The optimum is $\hat{q} = q$ — the reason a
calibrated classifier is needed.

**P3 (derivation, ★★, R4)** Derive (2), and state what the optimal decision rule and the error
exponent become when the priors are unequal ($\pi_K \ne \pi_O$). Then explain why, with $R$ types
of room, the error exponent is set by the Chernoff information of **the closest pair**.
*Answer sketch*: the threshold merely moves to $\log(\pi_O/\pi_K)$ and the exponent is unchanged
(the prior is a constant factor in $n$). For multiple hypotheses the union bound gives an error
$\le \sum_{\text{pairs}}e^{-n\mathcal{C}_{ij}}$, dominated for large $n$ by the smallest
$\mathcal{C}_{ij}$ — **the two most similar types of room** decide the overall performance.

**P4 (numerical, ★, R1, R4)** (a) Two objects are $0.6$ m apart, the measurement noise is $0.1$ m
and the uncertainty of the robot position is $0.25$ m. Find the separation ratio, the
geometry-only error and the error at $q = 0.9$. (b) For the distributions (6), find the mean
log-likelihood ratio of one object when the truth is the kitchen (= the KL divergence). (c) With
$\mathcal{C} = 0.123$, find the number of objects needed to bring the bound on the room-inference
error below 1%.
*Answer*: (a) $\sigma = \sqrt{0.1^2 + 0.25^2} = 0.2693$, $r = 2.228$, $\Phi(-1.114) = 0.1326$;
$\lambda = 2.197$, $\lambda/r = 0.986$:
$0.9\,\Phi(-2.100) + 0.1\,\Phi(-0.128) = 0.9\times0.0179 + 0.1\times0.4491 = 0.0610$.
(b) $\sum p_K\log(p_K/p_O) = 0.5\ln5 + 0.3\ln1.5 + 0.1\ln0.25 + 0.1\ln(1/3) = 0.678$.
(c) $n \ge \ln 100/0.123 = 37.4 \to 38$. (Tolerance 1%.)
*Check*: see that the KL divergence of (b) ($0.678$) is far larger than the Chernoff information
($0.172$) — the mean evidence and the error exponent are different quantities.

**P5 (implementation, ★★★, R3)** Put probabilistic association into the filter of the
reproduction task: compute the weights (5) for every candidate, update with the weighted-mean
innovation, and carry the uncertainty created by the mixed update into the covariance (the
probabilistic data association filter). Compare the mean and the maximum of the ATE with the
committed associations (geometry, semantics).
*Rubric*: (a) show that the weights sum to 1 and concentrate on one candidate when it is clear
(b) report whether the **maximum** ATE drops below that of committed association (the mean may
get slightly worse — less is updated when ambiguous) (c) compare with and without the "none of
these" hypothesis (d) compare paired over the 40 maps.

**P6 (counterexample, ★★, R1, R2)** (a) Give numerically, with the overconfident setting of P2,
a counterexample to "adding semantic information always improves association". (b) Change the
map of the reproduction task so that **every pair has the same class**, show that the gain of
semantics disappears, and explain the cause of the small difference that remains.
*Property checklist*: (a) finds one $(q, \hat{q}, r)$ with $\hat{q}$ above the actual $q$ at
which the error exceeds $\Phi(-r/2)$. (b) points out that within a pair the gain is 0 but that
semantics still help against confusion **between pairs** (mistaking an object for one of another
pair).

**P7 (paper, ★★, R2, R5)** Read `salas-moreno2013-slampp` and `rosinol2021-kimera` and (a) write
how SLAM++ represents an object (a prior model? the degrees of freedom of its pose?) and what
factor one observation adds to the pose graph, (b) find how SLAM++ separates instances when there
are several objects of the same kind, (c) tabulate the layers of the scene graph of Kimera with
the nodes and edges of each, (d) write how the authors partition and classify rooms, and by which
metric they report that accuracy.
*Rubric*: (a) and (c) pass by citing the figure or section of the paper. (b) is the core — find
in the paper by what means that system gets over the wall of R2 in this lesson (or does not). If
there is no explicit answer, **write that there is none**. (d) copies the name and the value of
the metric from the tables of the paper.

## Paper reading

**Two must-read papers.** Write a one-page note on each using the ten fixed questions below
(`lesson-standard.md` §5). Read in three passes, and in the third pass concentrate on questions 1,
5 and 8.

1. **Salas-Moreno, Newcombe, Strasdat, Kelly & Davison, "SLAM++: simultaneous localisation and
   mapping at the level of objects" (2013, CVPR)** — role: `seminal`.
   <https://doi.org/10.1109/CVPR.2013.178> (the parts on object recognition and on the pose
   graph)
   The first real-time system to raise the unit of the map to objects. The starting point of R1
   and R2 of this lesson.
   Additional questions: (a) what does the assumption of having 3D models of the objects in
   advance make easy, and what does it make impossible? (b) how does the constraint one
   observation of an object puts on the camera pose differ from that of a point feature? (c) do
   the authors experiment on scenes with repeated objects (several identical chairs)?
2. **Rosinol, Violette, Abate et al., "Kimera: from SLAM to spatial perception with 3D dynamic
   scene graphs" (2021, IJRR)** — role: `frontier`.
   <https://arxiv.org/abs/2101.06894> (the part defining the scene graph and the parts that
   build each layer)
   A system paper that extends the output of SLAM to a hierarchical scene graph. The primary
   source for R4 and R5 of this lesson. It is long, so read the **definition** of the scene
   graph and the part that builds the **room layer** first.
   Additional questions: (a) what are the nodes of each layer and what do the edges between
   layers mean? (b) when the trajectory is corrected by a loop closure, how are the mesh and the
   upper layers corrected with it? (c) how are moving agents (people) separated from the static
   map?

**Two recommended papers.** `bowman2017-probabilistic-data-association` (semantic SLAM with the
association as a latent variable — the probabilistic association of R3,
<https://doi.org/10.1109/ICRA.2017.7989203>) and `armeni2019-3d-scene-graph` (the paper that
defined the building-scale 3D scene graph — the hierarchy of R5,
<https://arxiv.org/abs/1910.02527>).

**The ten fixed questions**: (1) what problem is solved under what assumptions (2) what exactly
could earlier work not do (3) the key idea in one line of mathematics (4) what is the theoretical
guarantee and **what is not guaranteed** (5) the independent and dependent variables and baselines
of the experiments, and were they tuned fairly (6) do the metrics match the claims, and are
variance and seeds reported (7) what information needed for reproduction is missing (8) if it is
wrong, which assumption to suspect first (9) computational and memory complexity and real-time
capability (10) what would you change to surpass it a year from now.

## Reproduction task

**Tier R3 (reduced reproduction).** Compute budget: one laptop CPU core, under 5 minutes in
total, at most 500 MB of memory. numpy + scipy only. No detector, camera or simulator is needed —
the detections are produced by the generator.

**The input data** is produced by the generator below. **What the learner writes is the
association rules (geometry, semantics), the Kalman filter update, the tally of error rates and
the room inference.**

```python
"""Reproduction task of s1-semantic-scene-graphs: generators of the object map, path, detections."""

import numpy as np

SEED = 20261117
N_CLASS = 4
SIGMA_O, SIGMA_Z, RANGE, Q = 0.15, 0.10, 4.0, 0.9  # odometry/detection noise (m), range (m), accuracy


def make_map(rng, n_pairs=20, size=20.0, sep=0.5):
    """2 * n_pairs objects. The first half of the pairs have different classes, the rest the same."""
    centres = rng.uniform(1.5, size - 1.5, size=(n_pairs, 2))
    ang = rng.uniform(0, 2 * np.pi, n_pairs)
    off = 0.5 * sep * np.stack([np.cos(ang), np.sin(ang)], 1)
    pos = np.concatenate([centres - off, centres + off])
    cls = np.empty(2 * n_pairs, int)
    for k in range(n_pairs):
        a = rng.integers(N_CLASS)
        b = (a + 1 + rng.integers(N_CLASS - 1)) % N_CLASS if k < n_pairs // 2 else a
        cls[k], cls[k + n_pairs] = a, b
    return pos, cls


def path(n_steps=240):
    """Twice around the square with corners (3,3)-(17,3)-(17,17)-(3,17)."""
    corners = np.array([[3, 3], [17, 3], [17, 17], [3, 17]], float)
    per = n_steps // 2
    pts = []
    for k in range(n_steps):
        s = (k % per) / per * 4
        i, f = int(s), s - int(s)
        pts.append(corners[i] * (1 - f) + corners[(i + 1) % 4] * f)
    return np.array(pts)


def noisy_label(rng, true_class, q=Q):
    """The true class with probability q, otherwise one of the other classes uniformly."""
    if rng.random() < q:
        return int(true_class)
    return int((true_class + 1 + rng.integers(N_CLASS - 1)) % N_CLASS)
```

**Conventions (must be followed).** (a) For each method (geometry, semantics, oracle) create
`np.random.default_rng(SEED)` afresh and repeat, on that generator, **a map → the run on that
map** 40 times in sequence. (b) Within a run, at every step $k \ge 1$ draw the odometry noise (2
numbers) first and predict; then process the objects within range of the true position **in
index order**, drawing for each object the detection noise (2 numbers) and then the label
(`noisy_label`). (c) The state of the filter is the robot position (two-dimensional), initialized
at the true position with covariance $10^{-4}I$. The measurement model is $z = l_a - x + v$, so
the update is $x \leftarrow x - PS^{-1}\nu$, $P \leftarrow P - PS^{-1}P$
($S = P + \sigma_z^2I$, $\nu = z - (l_a - x)$). (d) Geometric association is the minimum
Mahalanobis distance and semantic association the maximum of
$-\tfrac12\nu^\top S^{-1}\nu + \log p(\ell\mid c_j)$ ($p = q$ or $(1-q)/(C-1)$). (e) The two
objects of pair $k$ have indices $k$ and $k + 20$, and $k < 10$ are the "pairs of different
classes".

**Part A — the formula for the error probability.** Compute (1) for
$r \in \{0.5, 1, 2, 3, 4, 6\}$ and $q \in \{0.7, 0.9, 0.99\}$, and confirm $r = 1, 3$
($q = 0.9$) with a simulation of 2 million draws.

**Part B — association on the object map.** Report for the three methods the association error
rate (overall, pairs of different classes, pairs of the same class) and the mean, median and
maximum of the ATE. Pair the error rates of geometry and of semantics map by map and report the
mean, standard deviation and $t$ value of the difference and "the number of maps on which
semantics are better".

**Part C — the accuracy of the classifier.** Run semantic association at
$q \in \{0.6, 0.75, 0.9, 0.99\}$ and report the error rates of the two kinds of pair (the same
value for the labels of the generator and for the $q$ of the association rule).

**Part D — room inference.** For the distributions (6) find the Chernoff information by a grid
search over $s$, and for label noise $q \in \{1, 0.9, 0.7\}$ measure the error at
$n \in \{1, 5, 10, 20\}$ with 200,000 simulations and compare with $e^{-n\mathcal{C}}$ (count
ties as one half).

**Optional task (public data).** Run a public detector on one public RGB-D sequence with object
annotations and (a) perform frame-to-frame object association with geometry alone and with
geometry + class and measure the error rates, (b) report separately scenes with several objects
of the same class and scenes without. There are no numerical reference values — report the
dataset, the detector and how the ground truth of the association was built, and write whether
the prediction of R2 in this lesson (the gain is concentrated on different classes) holds.

**Acceptance criteria — all four conditions must hold to pass.**

1. **Part A** — the 18 values of the table agree with the text to within $10^{-3}$, and the
   simulation gives $0.3087 / 0.0985$ at $r = 1$ and $0.0670 / 0.0337$ at $r = 3$
   ($\pm0.001$). Confirm with $r = 0.1$ that the $q = 0.9$ column converges to $0.100$ as
   $r \to 0$.
2. **Part B** — (a) the error rates are $6.18\%$ for geometry (different classes $7.13\%$, same
   class $5.20\%$) and $2.91\%$ with semantics ($2.01\%$, $3.81\%$) (tolerance $\pm0.3$ points;
   when the conventions are followed). (b) The mean ATE is $0.172, 0.146, 0.129$ m ($\pm0.01$)
   and the maximum $1.05, 0.37, 0.38$ m ($\pm0.05$). (c) The paired difference has a mean of
   $3.3$ points ($\pm0.3$), with **semantics lower on all 40 maps**. (d) Print explicitly that
   **the improvement factor of the pairs of different classes ($\approx3.5$) exceeds that of the
   pairs of the same class ($\approx1.4$)**.
3. **Part C** — the error rate of the pairs of different classes is $4.9, 4.1, 2.0, 0.7\%$ and of
   the pairs of the same class $4.1, 4.1, 3.8, 3.0\%$ ($\pm0.4$ points). Confirm that the error
   of the pairs of the same class is at least $2.5\%$ even at $q = 0.99$.
4. **Part D** — $\mathcal{C} = 0.1723, 0.1233, 0.0554$ (tolerance $10^{-3}$) and the errors are
   within $\pm0.005$ of the table in the text. Confirm that in every cell the measured error is
   **at most** $e^{-n\mathcal{C}}$.

**Comparison**: (a) for Part A the simulation is the baseline for the formula. (b) For Parts B
and C geometry alone is the lower and the oracle the upper baseline. (c) For Part D the bound (2)
is the baseline.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| Even the oracle diverges | The sign of the update is reversed ($H = -I$, yet $+K\nu$ was used) | The measurement is $l - x$, so $x \leftarrow x - PS^{-1}\nu$. A mistake the author actually made |
| The error rate is several times the reference | The uncertainty $P$ of the robot position was left out of the innovation covariance | Check that $S = P + \sigma_z^2I$ |
| Semantics give the same result as geometry | The label term was added with the same value to every candidate | It must differ per candidate $j$ according to whether $c_j = \ell$ |
| The error of the pairs of the same class is 0 | The kinds of pair were split wrongly by the first and second half of the indices | Pair $k$ has indices $k$ and $k + 20$; $k < 10$ are the different classes |
| The values differ slightly from the reference | The order of the random draws differs | Odometry 2 → (per object) detection 2 → label |
| Changing $q$ in Part C changes nothing | Only the $q$ of the association rule was changed and the labels of the generator stayed at $0.9$ | Use the same value for both |
| The error of Part D exceeds the bound | $s$ was fixed at 0.5, or the sign of the logarithm is wrong | Check that $\mathcal{C} > 0$ and $s^\star \approx 0.507$ |

## Open problems

- **(Open problem) Separating instances of the same class** — the wall of R2. A class label does
  not distinguish repeated objects, and environments such as offices, warehouses and car parks
  are full of repetition. Current approaches: learned instance-level descriptors, matching the 3D
  shape and pose of objects, matching relations between objects (subgraphs). What is missing: a
  way to **quantify the ambiguity** of subgraph matching — in some layouts even the relations
  repeat (a classroom with rows of the same desk-and-chair combination), and it cannot be decided
  in advance down to which level of cue one has to go.
- **(Open problem) Open vocabulary and association** — R1 assumes a closed set of classes and
  known confusion probabilities. Representing objects by the embeddings of a vision-language
  model turns the class into a point of a continuous space, and the counterpart of the likelihood
  ratio $\lambda$ is hard to obtain **in a calibrated way**. Current approaches: thresholding the
  cosine similarity of embeddings, averaging embeddings over viewpoints. What is missing: a
  calibration that turns embedding similarity into a probability of association — as P2 showed,
  overconfidence can be worse than using geometry alone.
- **(Open problem) Error propagation and consistency in the hierarchy** — as seen in R4 and R5,
  inference at an upper layer inherits the errors of the layer below, and an error at an upper
  layer ruins the search below. And when a loop closure corrects the trajectory the whole
  hierarchy has to deform consistently. Current approaches: optimization that places the whole
  hierarchy in one factor graph, propagation of per-layer confidences. What is missing: a
  **representation of uncertainty** over the whole hierarchical graph — present scene graphs say
  "this room is a kitchen", not "with what probability".
- **(Open problem) Evaluating scene graphs** — trajectories have the ATE (`s1-slam-benchmarking`)
  but scene graphs have no agreed metric. The accuracy of nodes, the accuracy of edges, the
  consistency of the hierarchy and the gain it brings to actual tasks (question answering,
  planning) are reported separately. Current approaches: object-detection metrics carried over to
  3D, precision and recall of room segmentation, task success rates. What is missing: a metric
  that weights errors in the graph structure **by their effect on the task**.

## Concept check

Take it with `rc quiz s1-semantic-scene-graphs`. This quiz is a **concept check only**; the real
work is the problem set and the reproduction task above (`lesson-standard.md` §4).

## How to study this stage

1. **Read the points-versus-objects table first (10 min)** — the table in "Setup and notation".
   Confirm that moving up to objects makes the map smaller and the observations richer, and in
   exchange **changes the failure mode** (appearance mismatch → confusion of the same kind).
2. **From (3) and (4) to (1) by hand (50 min)** — adding the log-likelihood ratios of the two
   hypotheses is all there is. Draw "the label moves the decision boundary by
   $\sigma^2\lambda/\Delta$" as a picture and compute one cell of the table yourself.
3. **Confirm the formula with Part A (30 min)** — see the simulation agree with the formula to
   the fourth decimal. Send $r$ to 0 and confirm the convergence to $1-q$.
4. **Run Part B (70 min)** — the central experiment of this lesson. Mind the sign of the filter
   update (first row of the diagnosis table). The point is to print the error rate **split by
   kind of pair** — looking only at the overall mean, R2 is invisible.
5. **See the wall with Part C (30 min)** — see the error of the pairs of the same class remain
   with the classifier raised to 99%. Write in one sentence where the intuition "improving the
   detector solves it" goes wrong.
6. **Derive (2), then Part D (50 min)** — the Chernoff bound is one line of Markov's inequality.
   Fill in the table and see label noise cut the exponent. With the accuracy of a detector you
   know, compute "how many objects does it take to be confident about one room".
7. **The two papers (150 min)** — read SLAM++ for the idea "an object becomes a factor" and
   Kimera for the idea "stack a hierarchy on top". In both look for how the wall of R2 in this
   lesson (objects of the same kind) is handled. The one-page note per paper is **mandatory**.
8. **Tie S1 together (30 min)** — build a table that maps the three layers of defence against
   association errors (make fewer, accept weakly, find) to the lessons of S1. This lesson is the
   first layer, `s1-loop-closure-lifelong` the second, and `s1-certifiable-slam` and
   `s1-slam-benchmarking` the third.
9. **End with what remains (30 min)** — pick one of the "Open problems" and write a paragraph on
   how the setting of the reproduction task could be changed to **experiment on** that problem
   (for example, adding a relational cue to the pairs of the same class).

**Pass criterion**: from a blank page you can derive (3), (4), (1) and (2); you can state through
the likelihood ratio the conditions under which semantic information helps association and those
under which it does not; you can explain why association errors inflate the tail rather than the
mean; you have code that satisfies all four conditions of the reproduction task; and you have
notes on the two papers.
