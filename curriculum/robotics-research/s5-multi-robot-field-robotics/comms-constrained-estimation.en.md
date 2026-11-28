---
id: s5-comms-constrained-estimation
lang: en
title: Communication constraints and distributed estimation
summary: >-
  Prove why fusing estimates received over a network as if they were independent is overconfident.
  Derive that two estimates sharing a common prior have cross-covariance $P_a\Lambda_0P_b$, which
  gives the size of the overconfidence in closed form, and prove in one line of convexity that
  covariance intersection (CI) is consistent **for any correlation**. Derive the critical arrival
  probability $1-1/a^2$ of the Kalman filter under packet loss from a two-sided bound, and derive
  and measure that using a delayed measurement as if it were current makes the NEES grow linearly
  in the delay.
objectives:
  - Derive the cross-covariance of two estimates that share a common prior and write the actual covariance of independence-assuming fusion in closed form.
  - Explain, and confirm numerically, that double counting of information (rumor propagation) doubles the NEES at every exchange.
  - Prove that covariance intersection is consistent under unknown correlation and quantify its price (conservatism).
  - Derive the critical arrival probability of the Kalman filter with intermittent observations from upper and lower recursions.
  - Derive the NEES of a filter that uses delayed measurements as current and compare it with the correct handling.
tags: [multi-robot, distributed-estimation, covariance-intersection, consistency, packet-loss, research]
---

# Communication constraints and distributed estimation

## Setup and notation

We use the definition of consistency and the NEES of `c5-observability-consistency` as they stand,
and inherit from `s5-distributed-optimization` the setting in which robots exchange **summaries**
(an estimate and a covariance) **instead of raw data**. This lesson asks one question — **when
summaries received over a network are fused, when does the reported covariance lie?** The
recommended prerequisites are those two lessons.

| Symbol | Meaning |
|---|---|
| $x \in \mathbb{R}^d$ | The quantity to estimate. Prior $x \sim \mathcal{N}(x_0, P_0)$, $\Lambda_0 = P_0^{-1}$ |
| $(a, P_a)$, $(b, P_b)$ | The estimates of two nodes and their **reported** covariances |
| $e_a = a - x$ | Estimation error. $\tilde{P}_a = \mathbb{E}[e_ae_a^\top]$ is the **actual** mean squared error |
| $P_{ab} = \mathbb{E}[e_ae_b^\top]$ | Cross-covariance. Usually **not transmitted** over the network |
| Consistency | $P \succeq \tilde{P}$ — the reported covariance is not smaller than the actual error |
| NEES | $e^\top P^{-1} e$. Consistent and exactly matched gives $\mathbb{E}[\mathrm{NEES}] = d$; overconfident gives $> d$ |
| $\omega \in [0,1]$ | The weight of covariance intersection (CI) |
| $\gamma$ | Arrival probability of a measurement packet (independent Bernoulli) |
| $a,\ q,\ r$ | Coefficient and noise variances of the scalar system $x_{k+1} = a x_k + w_k$, $y_k = x_k + v_k$ |

**Three communication defects** are the map of this lesson.

| Defect | What breaks | Consequence | Treated in |
|---|---|---|---|
| Summaries of unknown provenance | The independence assumption | Overconfidence (NEES $> d$) | R1, R2; the remedy is R3 |
| Packet loss | An update at every step | The expected covariance can diverge | R4 |
| Delay | Measurement time = now | Overconfidence, linear in the delay | R5 |

## Key results

The bracket gives the derivation depth (D0 cited / D1 skeleton / D2 full derivation / D3 proof —
the "Derivation depth" section of lesson `f0-how-to-read-this-track`).

- **R1 (fusion that ignores common information is overconfident) [D3]** — if two nodes start from
  the same prior information $\Lambda_0$ and update with mutually independent measurements, the
  cross-covariance of their errors is
  $$
  P_{ab} = P_a\,\Lambda_0\,P_b \tag{1}
  $$
  and the **actual** covariance of the independence-assuming fusion
  $P_n = (P_a^{-1} + P_b^{-1})^{-1}$ that ignores it is
  $$
  \tilde{P}_n = P_n + 2\,P_n\Lambda_0P_n \;\succ\; P_n,
  \qquad \mathbb{E}[\mathrm{NEES}] = d + 2\operatorname{tr}(\Lambda_0P_n). \tag{2}
  $$
  It is thus **always overconfident**, by an amount in closed form. The exact remedy is to
  subtract the common information once: $P_c^{-1} = P_a^{-1} + P_b^{-1} - \Lambda_0$ (the channel
  filter). Measured in the reproduction task: at $d = 3$ the NEES is $4.156$ (predicted $4.149$),
  and $3.004$ for the channel filter.
- **R2 (rumor propagation: the NEES doubles at every exchange) [D2]** — exchanging the fused
  estimates again and fusing them as independent once more leaves the estimate unchanged while the
  reported covariance alone shrinks to $P_n/2^n$. The actual error does not change, so the NEES is
  multiplied by $2^n$. Measured: $4.156 \to 8.312 \to 16.625 \to 33.250 \to 66.499$.
- **R3 (covariance intersection is consistent for any correlation) [D2]** — if
  $P_a \succeq \tilde{P}_a$ and $P_b \succeq \tilde{P}_b$ then, **whatever $P_{ab}$ is**,
  $$
  P_{\mathrm{CI}}^{-1} = \omega P_a^{-1} + (1-\omega)P_b^{-1}, \qquad
  c = P_{\mathrm{CI}}\big(\omega P_a^{-1}a + (1-\omega)P_b^{-1}b\big) \tag{3}
  $$
  satisfies $P_{\mathrm{CI}} \succeq \tilde{P}_c$. The proof is one line of convexity, and its
  **slack** is exactly
  $\omega(1-\omega)\,P_{\mathrm{CI}}\,\mathbb{E}[(p-q)(p-q)^\top]P_{\mathrm{CI}}$
  ($p = P_a^{-1}e_a$, $q = P_b^{-1}e_b$). The price is conservatism — for scalars of equal
  variance $\mathbb{E}[\mathrm{NEES}] = (1+\rho)/2$, so under independence ($\rho = 0$) half the
  information is thrown away.
- **R4 (the critical arrival probability under packet loss) [D2]** — for an unstable scalar system
  ($\lvert a\rvert > 1$) whose measurements arrive only with probability $\gamma$, the expectation
  of the prediction covariance is bounded only when
  $$
  \gamma > \gamma_c = 1 - \frac{1}{a^2}. \tag{4}
  $$
  In the bounded regime it is sandwiched as $S \le \mathbb{E}[P_k] \le V$ ($S$ the fixed point of
  a linear lower bound, $V$ the fixed point of the modified Riccati equation), and for the
  variance to be finite as well the stronger $\gamma > 1 - 1/a^4$ is needed. At $a = 1.2$,
  $\gamma_c = 0.3056$, and the measurement at $\gamma = 0.2$ is **a median of $10.5$ with a mean
  in the thousands to tens of thousands** — what diverges is not the typical trajectory but the
  tail.
- **R5 (using a delayed measurement as current makes the NEES linear in the delay) [D2]** — for a
  random walk, using a measurement delayed by $d$ steps as if it were the current one turns the
  filter into the correct estimator of **the state $d$ steps ago**, and
  $$
  \mathbb{E}[\mathrm{NEES}] = 1 + \frac{d\,q}{P_\infty},
  \qquad P_\infty = \tfrac12\big(-q + \sqrt{q^2 + 4qr}\big). \tag{5}
  $$
  At $q = 0.2$, $r = 0.5$ the predictions $1.863, 2.727, 4.453, 7.907$ for $d = 1, 2, 4, 8$ are
  met by the measured $1.857, 2.718, 4.434, 7.866$. The fix is one prediction — add $dq$ to the
  reported covariance.

## Derivation

### R1 — the cross-covariance and the closed form of the overconfidence

**Setting.** Two nodes hold the same prior information $(x_0, P_0)$ and each takes a measurement:
$y_a = H_ax + n_a$, $y_b = H_bx + n_b$, $n_a \sim \mathcal{N}(0,R_a)$, $n_b \sim \mathcal{N}(0,R_b)$,
with $n_a$, $n_b$ and the prior error $e_0 = x_0 - x$ mutually independent. The information-form
update is

$$
P_a^{-1} = \Lambda_0 + H_a^\top R_a^{-1}H_a, \qquad
a = P_a\big(\Lambda_0x_0 + H_a^\top R_a^{-1}y_a\big), \tag{6}
$$

and likewise for $b$.

**Decompose the errors into their sources.** Inserting $x_0 = x + e_0$, $y_a = H_ax + n_a$ into
(6),

$$
a = P_a\big[(\Lambda_0 + H_a^\top R_a^{-1}H_a)x + \Lambda_0e_0 + H_a^\top R_a^{-1}n_a\big]
  = x + P_a\big(\Lambda_0e_0 + H_a^\top R_a^{-1}n_a\big),
$$

that is,

$$
e_a = P_a\Lambda_0e_0 + P_aH_a^\top R_a^{-1}n_a, \qquad
e_b = P_b\Lambda_0e_0 + P_bH_b^\top R_b^{-1}n_b. \tag{7}
$$

**The two errors share $e_0$.** Since $n_a \perp n_b$ and $\mathbb{E}[e_0e_0^\top] = P_0$,

$$
P_{ab} = \mathbb{E}[e_ae_b^\top] = P_a\Lambda_0\,P_0\,\Lambda_0P_b = P_a\Lambda_0P_b,
$$

which is (1). **The cross-covariance is not zero, and it is larger the stronger the prior (= the
larger $\Lambda_0$).**

**The actual covariance of independence-assuming fusion.** Fusing in the belief that the two are
independent gives $c = P_n(P_a^{-1}a + P_b^{-1}b)$, $P_n^{-1} = P_a^{-1} + P_b^{-1}$, with error
$e_c = P_n(P_a^{-1}e_a + P_b^{-1}e_b)$. Its covariance is

$$
\begin{aligned}
\tilde{P}_n &= P_n\big[P_a^{-1}P_aP_a^{-1} + P_b^{-1}P_bP_b^{-1}
   + P_a^{-1}P_{ab}P_b^{-1} + P_b^{-1}P_{ab}^\top P_a^{-1}\big]P_n \\
 &= P_n\big[P_a^{-1} + P_b^{-1} + 2\Lambda_0\big]P_n
  = P_n + 2P_n\Lambda_0P_n,
\end{aligned}
$$

where the second line used $P_a^{-1}P_{ab}P_b^{-1} = \Lambda_0$ from (1). This is the first
expression of (2), and
$\mathbb{E}[\mathrm{NEES}] = \operatorname{tr}(P_n^{-1}\tilde{P}_n) = d + 2\operatorname{tr}(\Lambda_0P_n)$
follows.

**How to read it.** $P_n^{-1} = 2\Lambda_0 + (\text{measurement information})$ contains the prior
information **twice**. The $2P_n\Lambda_0P_n$ of (2) is the price of that double counting. Correct
fusion subtracts one copy:

$$
P_c^{-1} = P_a^{-1} + P_b^{-1} - \Lambda_0, \qquad
c^\star = P_c\big(P_a^{-1}a + P_b^{-1}b - \Lambda_0x_0\big). \tag{8}
$$

(8) **equals** the centralized solution that gathers both measurements in one place and updates
(problem P1). Implementing it by recording, for every communication link, "the information shared
with the peer" and subtracting it is the channel filter (`grime1994-decentralized-data-fusion`).

**Numbers.** $P_0 = \operatorname{diag}(4, 1, 0.25)$; node $a$ measures $x_1, x_2$ with variances
$0.5, 0.5$ and node $b$ measures $x_2, x_3$ with variances $0.5, 0.2$. Measured over
$4\times10^5$ samples:

| Estimator | Reported $\operatorname{tr}P$ | Actual $\operatorname{tr}\tilde{P}$ | NEES ($d = 3$) | $\lambda_{\min}(P - \tilde{P})$ |
|---|---|---|---|---|
| Node $a$ alone | $1.0278$ | $1.0294$ | $3.004$ | $-0.002$ |
| Independence-assuming fusion | $0.6436$ | $0.8283$ | $4.156$ | $-0.081$ |
| Channel filter (8) | $0.7556$ | $0.7567$ | $3.004$ | $-0.002$ |
| CI ($\omega = 0.837$) | $1.0608$ | $0.8987$ | $2.539$ | $+0.030$ |

The prediction of (2) is $\operatorname{tr}\tilde{P}_n = 0.8265$ and
$\mathbb{E}[\mathrm{NEES}] = 3 + 2\times0.5744 = 4.149$. **Two things to read.** (a) The **point
estimate** of independence-assuming fusion is not bad (the actual $0.8283$ is better than the
$1.0294$ of a single node). What lies is the **covariance** (it reports $0.6436$). (b) That lie
becomes a cost at the next stage — an overconfident estimate trusts later measurements less,
closes outlier-rejection gates wrongly, and, as in R2, deteriorates geometrically when fused
again.

**Where the assumptions break**: (1) is the formula for two nodes that start from the **same**
prior and whose later measurements are independent. If the common information is not a prior but
**common process noise** (the two nodes track the same moving target), the cross-covariance
accumulates recursively over time and the closed form (1) does not hold — then one propagates the
cross-covariance directly or goes to the CI of R3. Also, the subtraction in (8) is possible only
when one **knows** "what was shared". If the communication graph has a **cycle**, the same
information returns along several paths and per-link records cannot identify the common
information (the channel filter is exact only on trees).

### R2 — rumor propagation

Suppose **both** nodes performed the fusion of R1. Now both hold the same $(c, P_n)$. Exchanging
once more without any new measurement and fusing as independent gives

$$
c' = \big(P_n^{-1} + P_n^{-1}\big)^{-1}\big(P_n^{-1}c + P_n^{-1}c\big) = c, \qquad
P' = \big(2P_n^{-1}\big)^{-1} = \tfrac12P_n.
$$

**The estimate is unchanged and only the covariance halves.** After $n$ repetitions
$P^{(n)} = P_n/2^n$, and since the actual error $\tilde{P}_n$ does not change,

$$
\mathbb{E}[\mathrm{NEES}^{(n)}] = \operatorname{tr}\big((P_n/2^n)^{-1}\tilde{P}_n\big)
 = 2^n\big(d + 2\operatorname{tr}(\Lambda_0P_n)\big). \tag{9}
$$

The measured $4.156, 8.312, 16.625, 33.250, 66.499$ agree with (9). This is **rumor propagation**
(data incest) — the same error as believing a rumor more because several people repeated it, and
the extreme case in which the correlation coefficient of the two errors is exactly 1 (they are
the same estimate).

**Where the assumptions break**: the clean $2^n$ of (9) is for the case of **no** new measurement
between exchanges. With new measurements the double-counted and the new information mix and the
factor is below $2^n$, but the overconfidence itself does not go away, and **the filter trusts
new measurements less**, so the actual error gets worse too (problem P6). And with three or more
robots and a cycle in the communication graph the same thing happens without any robot receiving
its own estimate back directly.

### R3 — consistency of covariance intersection

We build a fusion that can be used when the cross-covariance is **unknown**. The error of (3) is

$$
e_c = P_{\mathrm{CI}}\big(\omega P_a^{-1}e_a + (1-\omega)P_b^{-1}e_b\big)
    = P_{\mathrm{CI}}\big(\omega p + (1-\omega)q\big),
\qquad p := P_a^{-1}e_a,\; q := P_b^{-1}e_b.
$$

**One line of convexity.** For arbitrary vectors $p, q$ and $\omega\in[0,1]$ the following
identity holds (expand to check — problem P2):

$$
\omega\,pp^\top + (1-\omega)\,qq^\top - \big(\omega p + (1-\omega)q\big)\big(\omega p + (1-\omega)q\big)^\top
 = \omega(1-\omega)\,(p-q)(p-q)^\top \;\succeq\; 0. \tag{10}
$$

Taking expectations,

$$
\mathbb{E}\big[(\omega p + (1-\omega)q)(\cdot)^\top\big]
 \;\preceq\; \omega\,\mathbb{E}[pp^\top] + (1-\omega)\,\mathbb{E}[qq^\top]. \tag{11}
$$

**Use the consistency of the inputs.**
$\mathbb{E}[pp^\top] = P_a^{-1}\tilde{P}_aP_a^{-1} \preceq P_a^{-1}P_aP_a^{-1} = P_a^{-1}$ (a
congruence of $\tilde{P}_a \preceq P_a$ by $P_a^{-1}$). The same holds for $q$. The right side of
(11) is therefore at most $\omega P_a^{-1} + (1-\omega)P_b^{-1} = P_{\mathrm{CI}}^{-1}$, and

$$
\tilde{P}_c = P_{\mathrm{CI}}\,\mathbb{E}\big[(\omega p + (1-\omega)q)(\cdot)^\top\big]\,P_{\mathrm{CI}}
 \;\preceq\; P_{\mathrm{CI}}P_{\mathrm{CI}}^{-1}P_{\mathrm{CI}} = P_{\mathrm{CI}}. \qquad\square
$$

**Nowhere in the proof did $P_{ab}$ appear.** That is because (10) is an identity independent of
the joint distribution of $p$ and $q$. This is all there is to CI.

**The exact size of the slack (conservatism).** Collecting what (10) and (11) discarded,

$$
P_{\mathrm{CI}} - \tilde{P}_c = P_{\mathrm{CI}}\Big[\,\underbrace{\omega(1-\omega)\,\mathbb{E}[(p-q)(p-q)^\top]}_{\text{slack of convexity}}
 + \underbrace{\omega P_a^{-1}(P_a - \tilde{P}_a)P_a^{-1} + (1-\omega)P_b^{-1}(P_b-\tilde{P}_b)P_b^{-1}}_{\text{slack of the inputs}}\Big]P_{\mathrm{CI}}. \tag{12}
$$

The first term vanishes only when $p = q$ (almost surely). For scalars of equal variance
($P_a = P_b = \sigma^2$, correlation coefficient $\rho$, $\omega = \tfrac12$) we have
$P_{\mathrm{CI}} = \sigma^2$ and $\tilde{P}_c = \sigma^2(1+\rho)/2$, so

$$
\mathbb{E}[\mathrm{NEES}_{\mathrm{CI}}] = \frac{1+\rho}{2}, \qquad
\mathbb{E}[\mathrm{NEES}_{\text{independence}}] = 1 + \rho. \tag{13}
$$

| $\rho$ | Independence-assuming fusion (measured / predicted) | CI (measured / predicted) |
|---|---|---|
| $0$ | $1.004$ / $1.0$ | $0.502$ / $0.50$ |
| $0.3$ | $1.299$ / $1.3$ | $0.649$ / $0.65$ |
| $0.6$ | $1.600$ / $1.6$ | $0.800$ / $0.80$ |
| $0.9$ | $1.908$ / $1.9$ | $0.954$ / $0.95$ |
| $1.0$ | $1.995$ / $2.0$ | $0.998$ / $1.00$ |

**The two fusions are exact at opposite ends.** The independence assumption is exactly right at
$\rho = 0$ and more overconfident the larger $\rho$. CI is exactly right at $\rho = 1$ and more
conservative the smaller $\rho$ — under independence it reports $P_{\mathrm{CI}} = \sigma^2$,
**the same covariance as not fusing at all**. CI is the fusion that assumes the worst
correlation.

**Choosing $\omega$.** (3) is consistent for every $\omega$, so $\omega$ is chosen by a
performance criterion — usually a one-dimensional search minimizing $\det P_{\mathrm{CI}}$ or
$\operatorname{tr}P_{\mathrm{CI}}$. In the numerical example of R1, minimizing $\det$ gives
$\omega = 0.837$ and $\det P_{\mathrm{CI}} = 0.0360$, only slightly below node $a$ alone
($0.0370$). Yet **the point estimate improves** — the actual $\operatorname{tr}\tilde{P}$ goes
$1.0294 \to 0.8987$. CI is a fusion that "does not report everything it gained".

**Where the assumptions break**: (a) the proof used that **the inputs are consistent**
($P_a \succeq \tilde{P}_a$). If an input is already overconfident (it has been through R2 even
once), the output of CI is overconfident too — CI merely **does not create** overconfidence; it
does not **repair** it. (b) CI guarantees consistency as defined through the mean and the
covariance only. If the distribution is multimodal or heavy tailed, $P \succeq \tilde{P}$ does not
mean "the confidence region contains the truth". (c) Applying CI to **independent** information
(a new measurement from one's own sensor) throws information away. In practice the independent
part and the part of unknown correlation are separated, the former handled by a Kalman update and
only the latter by CI (split CI).

### R4 — packet loss and the critical arrival probability

**Setting.** $x_{k+1} = ax_k + w_k$, $y_k = x_k + v_k$ ($w \sim \mathcal{N}(0,q)$,
$v\sim\mathcal{N}(0,r)$), and a measurement arrives with probability $\gamma$ (the arrival
indicators $\gamma_k \in \{0,1\}$ are mutually independent and **known to the filter**). The
recursion of the prediction covariance $P_k := P_{k\mid k-1}$ is

$$
P_{k+1} = a^2P_k + q - \gamma_k\,\frac{a^2P_k^2}{P_k + r}
 = \begin{cases} a^2P_k + q & \gamma_k = 0 \\[2pt] \dfrac{a^2rP_k}{P_k + r} + q & \gamma_k = 1 \end{cases} \tag{14}
$$

**$P_k$ becomes a random variable** — it depends on the loss pattern. The question is therefore
whether $\mathbb{E}[P_k]$ is bounded.

**Lower bound (a necessary condition for boundedness).** In the branch $\gamma_k = 1$,
$a^2rP_k/(P_k+r) \ge 0$, so combining the two branches $P_{k+1} \ge (1-\gamma_k)a^2P_k + q$.
Since $\gamma_k$ is independent of $P_k$ ($P_k$ is a function of $\gamma_0,\dots,\gamma_{k-1}$),

$$
\mathbb{E}[P_{k+1}] \;\ge\; (1-\gamma)a^2\,\mathbb{E}[P_k] + q. \tag{15}
$$

If $(1-\gamma)a^2 \ge 1$ the recursion on the right diverges, so $\mathbb{E}[P_k] \to \infty$.

**Upper bound (a sufficient condition for boundedness).** In the branch $\gamma_k = 1$,
$a^2rP_k/(P_k + r) \le a^2r$, so $P_{k+1} \le (1-\gamma_k)a^2P_k + \gamma_ka^2r + q$ and

$$
\mathbb{E}[P_{k+1}] \;\le\; (1-\gamma)a^2\,\mathbb{E}[P_k] + \gamma a^2r + q. \tag{16}
$$

If $(1-\gamma)a^2 < 1$ the right side converges, so $\mathbb{E}[P_k]$ is bounded. Together, (15)
and (16) give **bounded $\iff (1-\gamma)a^2 < 1 \iff \gamma > 1 - 1/a^2$**, which is (4).

**A tighter upper bound.** Write the right side of (14) as $g_{\gamma_k}(P_k)$. Since
$P \mapsto P^2/(P+r)$ is convex, $g$ is concave in $P$. By Jensen,
$\mathbb{E}[P_{k+1}] = \mathbb{E}[\bar{g}_\gamma(P_k)] \le \bar{g}_\gamma(\mathbb{E}[P_k])$
($\bar{g}_\gamma(P) = a^2P + q - \gamma a^2P^2/(P+r)$, the **modified Riccati** map), so its fixed
point $V$ is an upper bound, and the fixed point $S = q/(1-(1-\gamma)a^2)$ of (15) is a lower
bound:

$$
S \;\le\; \lim_k \mathbb{E}[P_k] \;\le\; V. \tag{17}
$$

**Numbers** ($a = 1.2$, $q = r = 1$, $\gamma_c = 0.3056$; $4\times10^4$ trajectories, $k = 400$):

| $\gamma$ | $S$ | Measured mean | $V$ | Measured median |
|---|---|---|---|---|
| $1.0$ | $1.000$ | $1.952$ | $1.952$ | $1.952$ |
| $0.9$ | $1.168$ | $2.195$ | $2.211$ | $1.952$ |
| $0.75$ | $1.563$ | $2.752$ | $2.807$ | $1.982$ |
| $0.6$ | $2.358$ | $3.861$ | $3.988$ | $2.173$ |
| $0.2$ | $\infty$ | $6.7\times10^3$ – $4.5\times10^4$ (unstable) | $\infty$ | $10.5$ |

**The last row is the point.** At $\gamma = 0.2 < \gamma_c$ **the median is a perfectly sane
$10.5$** while the mean is in the thousands to tens of thousands and differs every time it is
sampled ($6727$, $4058$, $45465$ at $k = 200, 300, 400$). What diverges is not the typical
trajectory but the tail produced by **the rare event of a long run of losses**. The theorem "the
expectation diverges" must therefore not be read as "the filter breaks"; it is to be read as "on
rare long losses the error grows arbitrarily, and their frequency dominates the mean".

**The threshold for the variance.** Applying the same argument to $P_k^2$: in the branch
$\gamma_k = 0$, $P_{k+1}^2 \ge a^4P_k^2$, so
$\mathbb{E}[P_{k+1}^2] \ge (1-\gamma)a^4\,\mathbb{E}[P_k^2]$, and a finite variance requires
$\gamma > 1 - 1/a^4$ ($0.5177$ at $a = 1.2$). In between ($0.3056 < \gamma < 0.5177$) the mean is
finite but **the variance is infinite**, so a Monte Carlo mean appears not to converge — which is
why the table above compares means only for $\gamma \ge 0.6$ (problem P5).

**Where the assumptions break**: (a) the threshold of (4) **with equality** is for invertible $C$
(here, a scalar). For a general system only bounds
$\underline{\gamma} \le \gamma_c \le \bar{\gamma}$ are known
($\underline{\gamma} = 1 - 1/\max_i\lvert\lambda_i(A)\rvert^2$), and the two need not coincide
(`sinopoli2004-intermittent-observations` §III). (b) Losses were assumed **independent**. Losses
on a real wireless channel come in clusters (bursts). Under Markov losses the threshold is set
not by the average loss rate but by **the probability of staying in the loss state**. (c) The
filter was assumed to **know about the loss**. A filter that does not know and reuses the last
value as a new measurement (zero-order hold) loses consistency as well — an error of the same
kind as R5.

### R5 — delayed measurements

**Setting.** A random walk $x_{k+1} = x_k + w_k$, $y_k = x_k + v_k$. Measurements arrive $d$ steps
late and the filter uses them as if they were **current**: at time $k$ it updates with $y_{k-d}$
as a measurement of $x_k$.

**The key observation.** The recursion of this filter (predict $P \leftarrow P + q$, update
$K = P/(P+r)$) is, **character for character, the standard Kalman filter** that uses the
measurement sequence $y_1, y_2, \dots$ once each, in order. Only the clock differs. The estimate
$\hat{x}_k$ at time $k$ is therefore in fact

$$
\hat{x}_k = \mathbb{E}\big[x_{k-d} \mid y_{1:k-d}\big]
$$

and its error variance is the steady-state posterior variance $P_\infty$. $P_\infty$ is the
positive solution of $P = (P+q)r/(P+q+r)$, that is of $P^2 + qP - qr = 0$, which gives the
expression in (5).

**The actual error.** What the filter **claims** to estimate is $x_k$. Since
$x_k = x_{k-d} + \sum_{i=k-d}^{k-1}w_i$,

$$
\hat{x}_k - x_k = \underbrace{(\hat{x}_k - x_{k-d})}_{\text{variance } P_\infty}
 - \underbrace{\textstyle\sum_{i=k-d}^{k-1}w_i}_{\text{variance } dq},
$$

and the two terms are independent ($\hat{x}_k$ is a function of $y_{1:k-d}$ and unrelated to
future process noise). The actual variance is therefore $P_\infty + dq$ while $P_\infty$ is
reported, which gives (5).

| Delay $d$ | 0 | 1 | 2 | 4 | 8 |
|---|---|---|---|---|---|
| Predicted $1 + dq/P_\infty$ | $1.000$ | $1.863$ | $2.727$ | $4.453$ | $7.907$ |
| Measured NEES | $0.998$ | $1.857$ | $2.718$ | $4.434$ | $7.866$ |

($q = 0.2$, $r = 0.5$, $P_\infty = 0.2317$, mean over the last 50 steps of $2\times10^4$
trajectories.)

**The fix.** If the delay $d$ is **known**, the remedy is one line: the estimate is that of
$x_{k-d}$, so **predict** it $d$ steps before reporting. For a random walk the estimate is
unchanged and the covariance becomes $P_\infty + dq$, which returns the NEES to 1. For a general
system $\hat{x}_k = A^d\hat{x}_{k-d}$,
$P = A^dP_\infty(A^d)^\top + \sum_{i=0}^{d-1}A^iQ(A^i)^\top$. If the delay varies from measurement
to measurement so that they arrive **out of sequence**, a state that has already been updated has
to be updated with a measurement from its past, and the exact one-step solution is
`bar-shalom2002-oosm`.

**Where the assumptions break**: (a) the "one-line fix" is for a **known** delay. Without
timestamps, or with unsynchronized clocks, $d$ itself has to be estimated. (b) (5) is the formula
for a random walk ($a = 1$). In a stable system ($\lvert a\rvert < 1$) less of the past state
remains in the present, so the cost of the delay saturates, and in an unstable system it explodes
as $a^{2d}$ (problem P4). (c) Correcting for the delay **does not bring the information back** —
the reported covariance growing to $P_\infty + dq$ means it became honest, not better. Delay is a
performance problem before it is a consistency problem.

## Proof sketch

### R1' — fusion that ignores a common prior is strictly overconfident [D3]

**Hypotheses**
H1: the two nodes hold the same prior information $(x_0, P_0)$, $P_0 \succ 0$.
H2: each node's measurement is linear with Gaussian noise, and $n_a$, $n_b$, $e_0$ are mutually
independent.
H3: each node performed the **exact** update (6) with its own measurement (each input is
consistent and exactly matched).

**Conclusion** C: the actual covariance of independence-assuming fusion is
$\tilde{P}_n = P_n + 2P_n\Lambda_0P_n$ and $\tilde{P}_n - P_n \succ 0$. That is, it is
overconfident in every direction.

**Strategy**: write the two errors as linear combinations of the independent sources
$(e_0, n_a, n_b)$ and find the source they share.

1. **Decomposition of the errors.** By H2 and H3, (7):
   $e_a = P_a\Lambda_0e_0 + P_aH_a^\top R_a^{-1}n_a$.
2. **Cross-covariance.** By the independence in H2 only $e_0$ survives in the cross term:
   $P_{ab} = P_a\Lambda_0P_0\Lambda_0P_b = P_a\Lambda_0P_b$.
3. **Covariance of the fused error.** Expanding $e_c = P_n(P_a^{-1}e_a + P_b^{-1}e_b)$ and using
   $\mathbb{E}[e_ae_a^\top] = P_a$ from H3, the bracket is $P_a^{-1} + P_b^{-1} + 2\Lambda_0$.
4. **Strictness.** From $P_0 \succ 0$ in H1, $\Lambda_0 \succ 0$ and $P_n \succ 0$, so
   $P_n\Lambda_0P_n \succ 0$ (a congruence preserves positive definiteness). **C**.

**Where it collapses if a hypothesis is removed**

- **Weaken H1** (the prior is infinitely weak in one direction, $\Lambda_0$ singular): the strict
  inequality of step 4 weakens to $\succeq$. In a direction with no prior information there is
  nothing to double count, so the fusion in that direction is exact. Overconfidence arises **only
  in the directions where information was shared**.
- **Remove the independence in H2** (the measurement noises of the two nodes are correlated): a
  cross term of $n_a$ and $n_b$ is added in step 2. Its sign is not fixed, so the overconfidence
  can grow or, **for negative correlation, shrink**. "Ignoring correlation is always
  overconfident" is false; the correct statement is "overconfident if the symmetric part of the
  cross term is PSD" (problem P7).
- **Remove H3** (the inputs are already overconfident): the $\mathbb{E}[e_ae_a^\top] = P_a$ of
  step 3 becomes $\succ P_a$ and overconfidence is added. R2 is that case.

## Problem set

The answer policy is stated per problem. Difficulty: ★ 15 minutes / ★★ 1 hour / ★★★ a day or more.

**P1 (derivation, ★★, R1)** Show that the $c^\star$ of (8) equals the centralized solution that
gathers the two measurements $y_a$, $y_b$ at one node and updates once. Then, for three robots
whose communication graph is a **triangle**, construct one concrete message order for which
per-link subtraction alone cannot remove the common information correctly.
*Answer sketch*: the information of the centralized solution is
$\Lambda_0 + H_a^\top R_a^{-1}H_a + H_b^\top R_b^{-1}H_b$, and adding the two copies of (6)
contains one $\Lambda_0$ too many. Match the information vectors the same way. In the triangle,
sending in the order $a \to b$, $b \to c$, $c \to a$ means the information $a$ receives from $c$
contains $a$'s own information, which the record of the link $c$–$a$ does not hold.

**P2 (proof, ★, R3)** Prove the identity (10) by expansion and confirm that it uses no assumption
on the joint distribution of $p$ and $q$. Then prove in the same way the consistency of CI for
three or more estimates ($P^{-1} = \sum_i\omega_iP_i^{-1}$, $\sum_i\omega_i = 1$).
*Strategy + key inequality*: factor $\omega(1-\omega)$ out of the left side. For several, it
suffices to show
$\sum_i\omega_ip_ip_i^\top - (\sum_i\omega_ip_i)(\cdot)^\top = \sum_{i<j}\omega_i\omega_j(p_i-p_j)(p_i-p_j)^\top$
(the pairwise form of a variance). The expansion is withheld.

**P3 (proof, ★★★, R4)** Write (15)–(17) with no line missing, and (a) confirm the concavity of
$\bar{g}_\gamma$ through its second derivative, (b) show that for $\gamma > \gamma_c$ the fixed
point $V$ of the modified Riccati map exists and is unique, (c) show that as $\gamma \to 1$, $V$
tends to the standard Riccati solution while $S$ does **not**, and explain why the lower bound is
loose.
*Strategy + key inequality*: (a) $d^2/dP^2\,[P^2/(P+r)] = 2r^2/(P+r)^3 > 0$. (b) Use that
$\bar{g}_\gamma$ is concave and increasing with $\bar{g}_\gamma(0) = q > 0$ and slope
$(1-\gamma)a^2 < 1$ for large $P$. (c) $S \to q$ while the standard solution exceeds $q$ — because
(15) discarded the whole $a^2rP/(P+r)$ of the arrival branch.

**P4 (derivation, ★★, R5)** Extend (5) to the general scalar system $x_{k+1} = ax_k + w_k$. Write
the actual variance and the NEES of the filter that uses delayed measurements as current in terms
of $a$, $d$, $q$ and $P_\infty$, and compare the behaviour as $d \to \infty$ for
$\lvert a\rvert < 1$ and $\lvert a\rvert > 1$.
*Answer sketch*: the filter is still the correct estimator of $x_{k-d}$ (the recursion is the
same). Since $x_k = a^dx_{k-d} + \sum_ia^iw$, the error is
$(\hat{x} - x_{k-d}) + (1 - a^d)x_{k-d} - \sum_i a^iw$, and because of the middle term the error
depends on **the size of the state itself** — a term absent for the random walk. For
$\lvert a\rvert < 1$ it saturates at the stationary variance and for $\lvert a\rvert > 1$ it grows
as $a^{2d}$.

**P5 (numerical, ★, R4)** At $a = 1.2$, $q = r = 1$, (a) find $\gamma_c$ and the variance
threshold $1 - 1/a^4$, and (b) find $S$ and $V$ to three decimals at
$\gamma = 0.6, 0.75, 0.9, 1.0$.
*Answer*: (a) $\gamma_c = 1 - 1/1.44 = 0.3056$, variance threshold $1 - 1/2.0736 = 0.5177$.
(b) $S = 2.358, 1.563, 1.168, 1.000$; $V = 3.988, 2.807, 2.211, 1.952$ (tolerance $\pm0.002$).
*Check*: substitute $V$ into $\bar{g}_\gamma$ and confirm a residual $< 10^{-9}$, and that the
$V$ of $\gamma = 1$ is the positive solution $1.9522$ of $P = a^2rP/(P+r) + q$.

**P6 (implementation, ★★★, R1, R2)** Build a simulation in which two nodes each track the same
random-walk target and every $m$ steps exchange their estimates and fuse them as independent, and
for the exchange periods $m \in \{1, 5, 20\}$ compare the NEES and the **actual** mean squared
error with a centralized filter. In the same setting implement CI fusion as well.
*Rubric*: (a) show that the NEES of independence-assuming fusion is larger the smaller $m$ (the
more frequent the exchange) (b) show that the **actual error** of independence-assuming fusion is
also worse than centralized (an overconfident filter trusts new measurements less) (c) show that
the NEES of CI is at most 1 for every $m$ (d) use common random numbers to compare the three
methods on the same trajectories.

**P7 (counterexample, ★★, R1, R3)** (a) Construct a counterexample to "fusion that ignores
correlation is always overconfident" — it suffices to show for scalars that fusing two estimates
with **negative** cross-covariance as independent is conservative. (b) Find a counterexample to
"CI always gives a worse point estimate than independence-assuming fusion", or, if you cannot,
state how far you searched.
*Property checklist*: (a) uses that the $1 + \rho$ of (13) is below 1 for $\rho < 0$ and names
one physical situation in which negative correlation actually arises (for example, two estimates
that split a **constant-sum** constraint between them). (b) has to investigate the case
$\rho \to 1$ with **different** variances — there the weights of independence-assuming fusion are
not optimal. Varying a single axis falls short.

**P8 (paper, ★★, R3, R4)** Read sections 2-3 of `julier1997-covariance-intersection` and sections
II-III of `sinopoli2004-intermittent-observations` and write, in at most three sentences each,
(a) whether the consistency definition of Julier and Uhlmann is the same as the one in the table
of this lesson, (b) by what criterion the authors choose $\omega$, (c) how the upper and lower
bounds of Sinopoli et al. correspond to (15)–(17) of this lesson, (d) under what condition the
upper and lower bounds on the critical probability coincide for a general system.
*Rubric*: (a) and (b) pass by citing the formulas. (c) must name the modified algebraic Riccati
equation (MARE) and the linear lower bound separately. (d) is the core — naming "when $C$ is
invertible" passes, and adding that the general case was left open is excellent.

## Paper reading

**Two must-read papers.** Write a one-page note on each using the ten fixed questions below
(the "Reading papers" section of lesson `f0-how-to-read-this-track`). Read in three passes, and in the third pass concentrate on questions 3,
4 and 8.

1. **Julier & Uhlmann, "A non-divergent estimation algorithm in the presence of unknown
   correlations" (1997, American Control Conference)** — role: `seminal`.
   <https://doi.org/10.1109/ACC.1997.609105> (sections 2-3)
   The primary source for R3 of this lesson. It is a five-page paper, so read it to the end.
   Additional questions: (a) is the authors' consistency proof the same as the convexity argument
   (10) of this lesson, or a different route? (b) the "non-divergent" of the title refers to the
   divergence of what (connect it to the rumor propagation of R2)? (c) how does the geometric
   picture the authors give (the intersection of covariance ellipses) correspond to the formula
   (3)?
2. **Sinopoli, Schenato, Franceschetti, Poolla, Jordan & Sastry, "Kalman filtering with
   intermittent observations" (2004, IEEE T-AC)** — role: `standard`.
   <https://doi.org/10.1109/TAC.2004.834121> (§II-III)
   The primary source for R4 of this lesson.
   Additional questions: (a) why do the authors go through upper and lower bounds instead of
   computing $\mathbb{E}[P_k]$ directly? (b) how do the authors distinguish the cases in which
   the upper and lower bounds on the critical probability coincide from those in which they do
   not? (c) where in the result is the independence of the losses used — which step of (15) in
   this lesson?

**Two recommended papers.** `grime1994-decentralized-data-fusion` (the channel filter — it
implements the subtraction of (8) through per-link records,
<https://doi.org/10.1016/0967-0661(94)90349-2>) and `bar-shalom2002-oosm` (the exact update for
out-of-sequence measurements, <https://doi.org/10.1109/TAES.2002.1039398>). Read them when
solving problems P1 and P4.

**The ten fixed questions**: (1) what problem is solved under what assumptions (2) what exactly
could earlier work not do (3) the key idea in one line of mathematics (4) what is the theoretical
guarantee and **what is not guaranteed** (5) the independent and dependent variables and baselines
of the experiments, and were they tuned fairly (6) do the metrics match the claims, and are
variance and seeds reported (7) what information needed for reproduction is missing (8) if it is
wrong, which assumption to suspect first (9) computational and memory complexity and real-time
capability (10) what would you change to surpass it a year from now.

## Reproduction task

**Tier R1 (numerical verification).** Compute budget: one laptop CPU core, under 2 minutes in
total, at most 1 GB of memory. numpy only. No simulator.

**Input data**: none. The constants below are everything, and `np.random.default_rng(SEED)` is
created **afresh** for every setting.

```python
"""Reproduction task of s5-comms-constrained-estimation: constants and NEES."""

import numpy as np

SEED = 20261117

# Parts A/B/C: two nodes sharing a common prior (d = 3)
P0 = np.diag([4.0, 1.0, 0.25])
HA = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
RA = np.diag([0.5, 0.5])
HB = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
RB = np.diag([0.5, 0.2])
N_SAMPLES = 400_000

# Part D: intermittent observations (scalar)
A_UNSTABLE, Q_D, R_D = 1.2, 1.0, 1.0
GAMMAS = [0.2, 0.6, 0.75, 0.9, 1.0]
N_TRAJ, N_STEPS = 40_000, 400

# Part E: delay (random walk)
Q_E, R_E = 0.2, 0.5
DELAYS = [0, 1, 2, 4, 8]


def mean_nees(est, truth, cov):
    """Mean NEES. est and truth are (N, d); cov is the (d, d) reported covariance."""
    err = est - truth
    return float(np.mean(np.einsum("ni,ij,nj->n", err, np.linalg.inv(cov), err)))
```

**Conventions (must be followed).** (a) The truth is drawn from the prior
($x \sim \mathcal{N}(0, P_0)$, $x_0 = 0$). (b) Fusion is computed in **information form**. (c) The
$P_k$ of Part D is the **prediction** covariance $P_{k\mid k-1}$ with initial value 1. (d) Part E
uses $2\times10^4$ trajectories and 200 steps and averages the NEES over the last 50 steps.

**Part A — double counting.** Build the two node estimates (6), the independence-assuming fusion
and the channel filter (8), and report the mean NEES, $\operatorname{tr}P$ and the actual
$\operatorname{tr}\tilde{P}$ of each. Also check that the sample cross-covariance agrees with (1).

**Part B — rumor propagation.** Report the NEES when the independence-assuming fusion of Part A is
fused with itself $n = 0,\dots,4$ more times.

**Part C — covariance intersection.** (a) Fuse the two estimates of Part A by CI ($\omega$
minimizes $\det P_{\mathrm{CI}}$ over a 1001-point grid on $[0,1]$). (b) For two scalar errors
with variance 1 and correlation coefficient $\rho \in \{0, 0.3, 0.6, 0.9, 1\}$, compare the NEES
of independence-assuming fusion and of CI ($\omega = \tfrac12$) with (13).

**Part D — intermittent observations.** Run (14) for each value in `GAMMAS`, report the mean and
the median of $P_k$ at $k = 400$, and compare with $S$ and $V$.

**Part E — delay.** For each value in `DELAYS` measure the NEES of the filter that uses delayed
measurements as current and compare with (5). Then measure the NEES of the corrected filter that
adds $dq$ to the reported covariance.

**Acceptance criteria — all five conditions must hold to pass.**

1. **Part A** — (a) the maximum absolute error between the sample cross-covariance and
   $P_a\Lambda_0P_b = \operatorname{diag}(0.4444, 0.1111, 0.1111)$ is $< 0.01$. (b) The NEES of
   independence-assuming fusion is $4.149 \pm 0.03$, with reported
   $\operatorname{tr}P_n = 0.6436$ and actual $\operatorname{tr}\tilde{P}_n = 0.8265 \pm 0.005$.
   (c) The NEES of the channel filter is $3.000 \pm 0.02$ and $\operatorname{tr}P_c = 0.7556$.
2. **Part B** — the NEES at $n = 0,\dots,4$ is $4.156, 8.312, 16.625, 33.250, 66.499$ (1%
   relative error each) and **consecutive ratios are exactly 2** (relative error $10^{-9}$ — only
   the covariance is halved on the same samples, so there must be no statistical error).
3. **Part C** — (a) $\omega = 0.837 \pm 0.005$, the NEES of CI is $2.539 \pm 0.03$, **below
   $d = 3$**, and $\lambda_{\min}(P_{\mathrm{CI}} - \tilde{P}_c) > 0$ (measured $+0.030$). On the
   same samples independence-assuming fusion has $\lambda_{\min}(P_n - \tilde{P}_n) < 0$
   (measured $-0.081$). (b) The ten values of the scalar table are within $0.01$ absolute error
   of the predictions of (13).
4. **Part D** — (a) at $\gamma = 0.6, 0.75, 0.9, 1.0$ the measured means are
   $3.861, 2.752, 2.195, 1.952$ (2% relative error) and **all satisfy $S \le$ mean $\le V$**
   ($S = 2.358, 1.563, 1.168, 1.000$; $V = 3.988, 2.807, 2.211, 1.952$). (b) At $\gamma = 0.2$
   **the median is $10.5 \pm 0.2$** while the mean exceeds $10^3$. The value of the mean itself is
   not an acceptance criterion (it does not converge) — **printing the gap between median and
   mean explicitly** is.
5. **Part E** — (a) the NEES at $d = 0, 1, 2, 4, 8$ is within 2% relative error of
   $1.000, 1.863, 2.727, 4.453, 7.907$. (b) The NEES of the corrected filter is $1.00 \pm 0.03$
   for every $d$. (c) Confirm that the reported covariance is $P_\infty = 0.2317$ regardless of
   the delay (relative error $10^{-4}$) — **the filter does not know that it is late.**

**Comparison**: (a) the baseline of Parts A, B and C is the channel filter (= the centralized
optimum). (b) For the scalar table of Part C the analytic values of (13) are the baseline.
(c) For Part D, $S$ and $V$ are the baselines and $\gamma = 1$ is the standard Kalman filter.
(d) For Part E, $d = 0$ and the corrected filter are the baselines.

**Failure diagnosis table**

| Symptom | Cause | How to check |
|---|---|---|
| The NEES of independence-assuming fusion in Part A is 3 | The two nodes were given **different** prior samples (there is no common information) | Check that both nodes use the same $x_0$ and the same truth $x$. Here $x_0 = 0$ is the common one |
| The NEES of the channel filter exceeds 3 | $\Lambda_0$ was subtracted from the information matrix only, not from the information vector | Check the $-\Lambda_0x_0$ term of (8) (it is invisible when $x_0 = 0$, so test with $x_0 \ne 0$) |
| The ratio in Part B is slightly off 2 | New samples were drawn every round | Compute the NEES on the same estimates, changing only the covariance to $P_n/2^n$ |
| The NEES of CI exceeds 3 | $\omega$ was used in the covariance only, not in the weighting of the mean | Check that the same $\omega$ enters both formulas of (3) |
| The $\omega$ of CI is 0 or 1 | The reciprocal of $\det$ was minimized instead of $\det$ | Check that at $\omega = 0, 1$ $P_{\mathrm{CI}}$ becomes $P_b, P_a$ |
| In Part D the mean at $\gamma = 0.6$ exceeds $V$ | The posterior covariance was tracked, or there are too few trajectories | Check that the prediction covariance (14) is used and that there are $4\times10^4$ trajectories |
| In Part D the mean at $\gamma = 0.2$ comes out small | Too few trajectories to draw a long run of losses | Print the maximum as well (measured at the level of $10^7$–$10^8$) |
| The NEES in Part E is 1 regardless of the delay | The truth was also taken from $d$ steps ago | Check that the error is computed as $\hat{x}_k - x_k$ (the current truth) |

## Open problems

- **(Open problem) Exact removal of common information on communication graphs with cycles** —
  the subtraction of R1 is exact only on trees, and with cycles one retreats to CI and throws
  away a large part of the information (half under independence — (13)). Current approaches:
  tagging information with its provenance as it is forwarded (the messages grow in proportion to
  the number of robots), and exchanging **the original factors**, as in distributed pose graphs
  (`s5-distributed-optimization`). What is missing: a fusion with constant message size that is
  strictly less conservative than CI and provably consistent.
- **(Open problem) A measure of the trade between consistency and conservatism** — CI assumes the
  worst correlation and pushes $\mathbb{E}[\mathrm{NEES}]$ below $d$. If a **range** for the
  correlation is known (say $\lvert\rho\rvert\le\bar\rho$) a less conservative fusion is possible
  (the bounded-correlation CI family), but no established procedure **estimates and validates**
  that range **from data** on a real system. Current approaches: ellipsoidal-intersection fusion
  and inverse covariance intersection. What is missing: online estimation of the correlation
  range and how its estimation error propagates into the consistency guarantee.
- **(Open problem) Burst losses and nonlinear estimators** — the threshold of R4 is a result for
  independent losses, a linear system and known losses. For an estimator that is nonlinear and
  whose linearization point depends on the estimate, as in visual-inertial SLAM, there is no
  theory that bounds in advance **the outage length at which divergence begins** when
  communication or perception outages get long. Current approaches: threshold conditions under
  Markov loss models, and empirical outage-tolerance tests. What is missing: a way to predict the
  outage tolerance of a nonlinear estimator from its observability structure
  (`c5-observability-consistency`).

## Concept check

Take it with `rc quiz s5-comms-constrained-estimation`. This quiz is a **concept check only**; the
real work is the problem set and the reproduction task above (the "Problem sets" section of lesson `f0-how-to-read-this-track`).

## How to study this stage

1. **Copy the table of the three defects first (15 min)** — the table in "Setup and notation".
   Summaries of unknown provenance, loss and delay each break **a different thing**. Loss does not
   break consistency; delay and double counting do — this distinction is the skeleton of the
   whole lesson.
2. **From (7) to (2) by hand (50 min)** — decomposing the errors into independent sources is the
   core technique. The moment $P_a^{-1}P_{ab}P_b^{-1} = \Lambda_0$ appears, the phrase "the prior
   went in twice" becomes a formula.
3. **Run Parts A and B (50 min)** — see the NEES of $4.156$ and check it against the prediction
   $4.149$ of (2). Then with Part B watch one mistake inflate as $2^n$. Reproduce the first row of
   the diagnosis table **on purpose** (giving the two nodes different prior samples makes the
   overconfidence vanish) — nothing shows more clearly that the common information is the cause.
4. **The proof of CI from a blank page (40 min)** — expand (10) and continue to (11) and (12).
   Confirm for yourself that the proof is three lines and that $P_{ab}$ is nowhere in it. The
   slack term of (12) is the most useful formula of this lesson — how much CI throws away is right
   there.
5. **See the two ends of the two fusions with Part C (40 min)** — in the scalar table the
   independence assumption is exact at $\rho = 0$ and CI at $\rho = 1$. The practical question is
   not "which one is right" but "where does the correlation of my system lie".
6. **(15) and (16) by hand, then Part D (60 min)** — the derivation of the critical probability is
   just two inequalities. In Part D print **the median and the mean together** for $\gamma = 0.2$.
   Looking only at the mean you misread it as "the filter diverges"; looking only at the median
   you misread the theorem as wrong.
7. **Part E and (5) (40 min)** — the single sentence "a late filter is the correct filter of a
   past state" yields (5). Implement the corrected filter, watch the NEES return to 1, and confirm
   that the larger reported covariance means it became honest, not better.
8. **Papers, the short one first (120 min)** — read Julier and Uhlmann (five pages) to the end
   first and compare with the proof in this lesson, then go to Sinopoli et al. For the latter,
   sections II-III suffice — the purpose is to see how the upper and lower bounds correspond to
   (15)–(17) of this lesson. The one-page note per paper is **mandatory**.
9. **End with what cannot be done (30 min)** — pick one of the "Open problems" and write a
   paragraph on what form it takes in a multi-robot system you work with (or in the two-robot
   pose graph of `s5-distributed-optimization`).

**Pass criterion**: from a blank page you can derive (1), (2), (10)–(12), (15), (16) and (5); you
can say at which correlation independence-assuming fusion and CI are each exact; you can explain
**what** diverges below the critical probability (the tail); you have code that satisfies all five
conditions of the reproduction task; and you have notes on the two papers.
