---
id: c5-sparsity-isam
title: 희소성과 증분 추론
summary: >-
  소거 순서가 fill-in 을 결정한다는 fill-path 정리를 증명하고, 최소 fill-in 이 NP-완전임과 평면
  구조가 주는 상계를 정리한다. Bayes tree 의 조건부 분해에서 iSAM2 의 증분 재소거가 왜 국소적인지
  유도하고, 증분 QR(Givens)의 비용이 변수 순서상 거리로 결정됨을 수치로 확인한다. 주변화가 만드는
  조밀화와, 고정 희소 토폴로지로의 KL 최적 근사가 적률 맞추기임을 유도한다.
objectives:
  - fill-path 정리를 증명해 어떤 간선이 왜 채워지는지 설명할 수 있다.
  - 완전 소거 순서의 존재가 chordality 와 동등함을 유도하고 사슬 그래프에서 fill-in 이 0 인 이유를 말할 수 있다.
  - Bayes tree 의 조건부 분해에서 새 인자가 무효화하는 클리크 집합을 정확히 특정할 수 있다.
  - 증분 QR 의 Givens 회전 수가 변수 순서상 거리로 결정됨을 유도하고 O(1) 과 Θ(N) 경우를 구분할 수 있다.
  - 고정 희소 패턴 아래 KL 최적 가우시안 근사가 그 패턴 위에서 공분산을 맞추는 해임을 유도할 수 있다.
  - 정보행렬 원소를 그냥 0 으로 만드는 희소화가 왜 과신을 만드는지 수치로 보일 수 있다.
prerequisites: [c5-factor-graphs-map]
difficulty: 5
estimated_minutes: 600
tags: [state-estimation, factor-graph, sparsity, fill-in, isam2, bayes-tree, research]
activities:
  - id: c5-sparsity-isam-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 90
  - id: c5-sparsity-isam-papers
    kind: reading
    title: 필독 논문 3편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 150
  - id: c5-sparsity-isam-problems
    kind: exercise
    title: 문제 세트 (증명 1 · 유도 1 · 계산 2 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 180
  - id: c5-sparsity-isam-reproduction
    kind: exercise
    title: 재현 과제 — 순서별 fill-in, 증분 QR, 갱신 비용 척도, KL 희소화 (R2)
    estimated_minutes: 165
  - id: c5-sparsity-isam-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.3.3 (희소성과 배치 vs 재귀). 이 레슨의 교재 진입로. 전문 PDF 무료.
  - title: "Kaess, Johannsson, Roberts et al. — iSAM2 (2012, IJRR)"
    url: https://doi.org/10.1177/0278364911430419
    kind: article
    note: 필독 1. 역할 원전(seminal). 3-5절(Bayes tree, 증분 재소거, fluid relinearization).
  - title: "Rose, Tarjan & Lueker — Algorithmic aspects of vertex elimination on graphs (1976)"
    url: https://doi.org/10.1137/0205021
    kind: article
    note: 필독 2. 역할 원전(seminal). fill-path 정리와 chordality. §2-3 만 읽는다.
  - title: "Carlevaris-Bianco, Kaess & Eustice — Generic node removal for factor-graph SLAM (2014, T-RO)"
    url: https://doi.org/10.1109/TRO.2014.2347571
    kind: article
    note: 필독 3. 역할 표준(standard). 주변화의 조밀화와 희소 근사(GLC). III-IV 절.
  - title: "Yannakakis — Computing the minimum fill-in is NP-complete (1981)"
    url: https://doi.org/10.1137/0602010
    kind: article
    note: 권장. 최소 fill-in 의 NP-완전성. 4쪽짜리 논문이므로 한 번 통독할 가치가 있다.
  - title: "Lipton, Rose & Tarjan — Generalized nested dissection (1979)"
    url: https://doi.org/10.1137/0716027
    kind: article
    note: 권장. separator 가 작은 그래프족의 fill·flops 상계. 2D 포즈 그래프의 실측 성능을 설명한다.
  - title: "Kaess, Ranganathan & Dellaert — iSAM (2008, T-RO)"
    url: https://doi.org/10.1109/TRO.2008.2006706
    kind: article
    note: 권장. Givens 회전으로 R 을 증분 갱신하는 원형. iSAM2 의 전신.
  - title: "CMU 16-833 Robot Localization and Mapping (Kaess)"
    url: https://www.cs.cmu.edu/~kaess/teaching/16833/Fall2024
    kind: course
    note: 이 모듈의 기준 과목. 소개문에 "효율적 확률 추론"이 이 레슨의 주제로 명시되어 있다.
---

# 희소성과 증분 추론

## 전제와 기호

`c5-factor-graphs-map` 의 표기를 그대로 쓴다($\mathcal{X}$, $\Lambda$, $\eta$, $\mathsf{R}$,
$\mathcal{S}(x_i)$, $A$, $b$). 그 레슨의 R3(가우시안 소거 = Schur 보완)과 6단계(separator 가
클리크가 된다)가 이 레슨의 출발점이다. 추가 기호:

| 기호 | 뜻 |
|---|---|
| $\mathcal{G}(\Lambda) = (V, E)$ | 변수 인접 그래프. $V = \{x_1,\dots,x_n\}$, $\{x_i,x_j\}\in E \iff \Lambda_{ij} \ne 0$ |
| $\sigma : V \to \{1,\dots,n\}$ | 소거 순서(전단사). $\sigma(v)$ 가 작을수록 먼저 소거된다 |
| $\mathcal{G}^+_\sigma = (V, E^+_\sigma)$ | **채워진 그래프(filled graph)**. $\sigma$ 로 소거를 끝까지 한 뒤 생긴 모든 간선 |
| $E^+_\sigma \setminus E$ | **fill-in**. 원래 없던 간선 |
| $C$, $F_C$, $S_C$ | Bayes tree 의 클리크와 그 **frontal**(그 클리크에서 소거되는 변수)·**separator**($C \setminus F_C$) |
| $w$ | treewidth $= \min_\sigma \max_C \lvert C\rvert - 1$ |
| $\mathcal{T}$ | 희소화에서 허용하는 비영 패턴(간선 집합) |
| $\mathrm{KL}(p\Vert q)$ | $\mathbb{E}_p[\log p - \log q]$ |

`c5-factor-graphs-map` 과 마찬가지로 변수는 $\mathbb{R}^{d_i}$ 좌표다. 포즈 그래프에서
$d_i = 3$($SE(2)$)이므로 "간선 1개"는 $3\times3$ 블록 1개를 뜻한다. 블록과 스칼라를 섞지 않도록,
그래프 논의는 **블록 단위**로 하고 수치(nnz)는 **스칼라 단위**로 보고한다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(D0 인용 / D1 골격 / D2 완전 유도 / D3 증명 —
`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (fill-path 정리) [D3]** — $u \ne v$ 에 대해
  $$
  \{u,v\} \in E^+_\sigma \iff
    \exists\, u = w_0, w_1, \dots, w_k = v \text{ in } \mathcal{G} \text{ with }
    \sigma(w_i) < \min\big(\sigma(u), \sigma(v)\big) \;\; (0 < i < k). \tag{1}
  $$
  즉 **어떤 간선이 채워지는지는 원 그래프의 경로와 순서만으로 결정된다**(수치와 무관하다).
  따름정리: $\lvert\mathrm{nnz}(\mathsf{R})\rvert = n + \lvert E^+_\sigma\rvert$ (블록이면 블록
  크기로 가중), 그리고 fill-in 이 0 인 순서가 존재하는 것은 $\mathcal{G}$ 가 **chordal**
  (길이 4 이상의 유도 순환이 없음)인 것과 동등하다.
- **R2 (최소 fill-in 은 NP-완전, 그러나 구조는 돕는다) [D1]** — 주어진 $\mathcal{G}$ 에 대해
  $\lvert E^+_\sigma\rvert$ 를 최소화하는 $\sigma$ 를 찾는 문제는 NP-완전이다
  (`yannakakis1981-min-fill-in`). 그래서 실무는 휴리스틱(AMD·COLAMD·nested dissection)을 쓴다.
  반면 $O(\sqrt{n})$ 크기 separator 로 재귀 분할되는 그래프족(평면 그래프 포함)에서는 nested
  dissection 이 fill $O(n\log n)$, flops $O(n^{3/2})$ 를 **보장**한다
  (`lipton1979-nested-dissection`). 2D 포즈 그래프가 거의 평면이라는 것이 실측 성능의 설명이다.
- **R3 (Bayes tree 와 증분 재소거의 국소성) [D2]** — 소거가 끝난 뒤의 분포는 클리크 트리 위에서
  $$
  p(\mathcal{X}) = \prod_{C} p\big(F_C \mid S_C\big) \tag{2}
  $$
  로 분해된다. 변수 집합 $V$ 에 닿는 새 인자 $\phi_{\mathrm{new}}(V)$ 를 넣을 때 **무효화되는
  것은 $V$ 의 변수를 포함하는 클리크들과 그 조상(루트까지의 경로)뿐**이고, 나머지 부분트리의
  조건부는 글자 하나도 바뀌지 않는다. 재소거 비용은 떼어낸 부분트리의 크기에 비례한다.
- **R4 (증분 QR = Givens 회전; 비용은 순서상 거리) [D2]** — 화이트닝된 새 행 $(a^\top, \beta)$ 를
  상삼각 $\mathsf{R}$ 에 접는 데 쓰는 Givens 회전의 수는 $a$ 의 첫 비영 열 $k_0$ 부터 $N$ 까지의
  비영 열 수이고, 상계는 $N - k_0 + 1$ 이다. 따라서 **순서에서 가장 늦게 둔 변수에만 닿는
  인자는 $O(1)$**, 가장 먼저 둔 변수에 닿는 루프 클로저는 $\Theta(N)$ 이다. 재현 과제의 실측:
  마지막 오도메트리 간선은 $N = 300, 600, 1200$ 에서 모두 **14 회전**, 포즈 0 으로의 루프
  클로저는 $898, 1798, 3598 = 3N - 2$ 회전.
- **R5 (주변화의 조밀화와 KL 최적 희소화) [D2]** — 차수 $d$ 인 변수를 주변화하면 Markov blanket
  이 클리크가 되어 간선이 최대 $\binom{d}{2}$ 개까지 늘고, 그 정보는 더는 쌍별 인자로 분해되지
  않는다. 허용 패턴 $\mathcal{T}$ 로 제한한 가우시안 근사 중 $\mathrm{KL}(p\Vert q)$ 를
  최소화하는 것은
  $$
  \mu_q = \mu_p, \qquad (\Lambda_q^{-1})_{ij} = (\Sigma_p)_{ij} \;\;
    \text{for } (i,j) \in \mathcal{T} \cup \{\text{대각}\}, \quad (\Lambda_q)_{ij} = 0 \;\; \text{otherwise} \tag{3}
  $$
  즉 **패턴 위에서 공분산(적률)을 정확히 맞추는 해**다($\mathcal{T}$ 가 트리면 Chow-Liu 해).
  정보행렬 원소를 그냥 0 으로 지우는 것은 (3)이 아니며 주변 분산을 **과소평가**한다.

## 유도

### R3 — 새 인자가 무효화하는 것은 어디까지인가

`c5-factor-graphs-map` 의 R3 로 $\sigma$ 에 따라 전부 소거하면 조건부들의 사슬이 남는다.
소거된 순서의 역순으로 묶으면 각 단계의 조건부 $p(x_i \mid \mathcal{S}(x_i))$ 가 나오고, 같은
separator 를 공유하는 연속된 변수들을 하나의 클리크 $C$ 로 합치면 (2)가 된다. $F_C$ 는 그
클리크에서 소거된 변수들이고 $S_C$ 는 나머지다. $\mathcal{G}^+_\sigma$ 가 chordal 이라는 R1 의
따름정리가 이 묶음이 **트리**가 됨을 보장한다(클리크 트리의 존재는 chordality 와 동등하다).

이제 인자 $\phi_{\mathrm{new}}(V)$ 를 곱한다. 트리를 두 조각으로 나눈다 — $V$ 의 변수를 포함하는
클리크들과 그 조상 전부를 $\mathcal{A}$, 나머지를 $\mathcal{B}$ 라 하자. $\mathcal{B}$ 의 각
클리크 $C$ 는 (2)의 조건부 $p(F_C\mid S_C)$ 를 기여하고, 트리 구조에서 $S_C \subseteq$
(그 클리크의 부모) 이며 $F_C \cap V = \emptyset$ 이다. 따라서

$$
p'(\mathcal{X}) \propto \phi_{\mathrm{new}}(V)\prod_{C\in\mathcal{A}} p(F_C\mid S_C)
  \cdot \prod_{C\in\mathcal{B}} p(F_C\mid S_C). \tag{4}
$$

핵심은 **$\mathcal{B}$ 의 인자들이 조건부이지 주변분포가 아니라는 점**이다. 조건부는 자기
separator 가 어떤 값을 갖든 그 값에 대해 이미 정규화되어 있으므로, $\mathcal{A}$ 쪽에서
$S_C$ 의 분포가 바뀌어도 $p(F_C\mid S_C)$ 자체는 바뀌지 않는다. 그러므로 (4)의 두 번째 곱은
그대로 두고, 첫 번째 곱만 인자 그래프로 되돌려 $\phi_{\mathrm{new}}$ 와 함께 다시 소거하면 된다.
이것이 iSAM2 의 증분 갱신이다(`kaess2012-isam2` §3-4).

왜 조상까지 무효화되는가: $\mathcal{A}$ 의 클리크에서 소거되는 변수의 분포가 바뀌면 그것이
자기 부모의 separator 에 들어가는 **값**을 바꾸므로, 부모의 $p(F\mid S)$ 를 그 값에서 다시
평가해야 한다. 트리에서 루트까지 올라가는 경로가 정확히 그 전파 경로다.

비용은 떼어낸 $\mathcal{A}$ 의 크기로 결정되고, 그것은 **$V$ 의 변수가 트리에서 얼마나 깊이
있는가**로 결정된다. 소거 순서에서 늦게 둔 변수는 루트 근처에 있으므로 $\mathcal{A}$ 가 작고,
먼저 둔(오래된) 변수는 잎 근처에 있어 $\mathcal{A}$ 가 트리 전체가 된다. iSAM2 가 영향받은
변수를 순서의 끝으로 **재정렬**하는 이유가 이것이다.

여기에 두 가지 근사가 더 붙는다.

- **fluid relinearization**: 변수 $x_i$ 의 누적 증분 $\lvert\delta_i\rvert$ 가 임계값
  $\tau_i$ 를 넘을 때만 그 변수를 재선형화하고, 재선형화된 변수가 닿는 부분트리를 다시 소거한다.
- **부분 역대입**: 역대입을 내려가다 증분이 임계값보다 작아지면 그 아래를 건너뛴다.

**가정이 깨지는 곳**: 두 임계값은 **국소** 판정이다. (2)의 분해는 정확하지만, 임계값을 넣은
순간 해는 배치 해가 아니고 그 차이에 대한 전역 상계가 없다. 임계값보다 작은 증분이 수천 개
쌓여 큰 전역 오차가 되는 상황을 구성할 수 있고(문제 P6), 실제로 임계값을 키운 iSAM2 는 조용히
배치 해에서 멀어진다. **정확성이 보장되는 것은 임계값을 0 으로 둘 때뿐이다.**

### R4 — Givens 회전 한 번의 효과와 비용

$\mathsf{R}\delta = d$ 가 현재의 제곱근 정보 형태라 하자($\mathsf{R}$ 상삼각). 새 측정 행
$(a^\top, \beta)$ 를 더한 최소제곱 문제는 쌓은 행렬
$\begin{bmatrix}\mathsf{R} & d\\ a^\top & \beta\end{bmatrix}$ 의 최소제곱이다. 직교 변환은
$\lVert\cdot\rVert_2$ 를 보존하므로 이 행렬에 직교행렬을 왼쪽에서 곱해도 최소제곱 해가 바뀌지
않는다. $a$ 를 위에서부터 0 으로 만든다. $k$ 번째 단계에서 $a_k \ne 0$ 이면 $k$ 행과 새 행이
이루는 평면에서 회전을 적용한다:

$$
r = \sqrt{\mathsf{R}_{kk}^2 + a_k^2}, \qquad c = \frac{\mathsf{R}_{kk}}{r}, \qquad s = \frac{a_k}{r}, \tag{5}
$$

$$
\begin{bmatrix} \mathsf{R}_{k,k:} & d_k \\ a_{k:}^\top & \beta \end{bmatrix}
  \;\longleftarrow\;
  \begin{bmatrix} c & s \\ -s & c \end{bmatrix}
  \begin{bmatrix} \mathsf{R}_{k,k:} & d_k \\ a_{k:}^\top & \beta \end{bmatrix}. \tag{6}
$$

새 행의 $k$ 번째 성분은 $-s\,\mathsf{R}_{kk} + c\,a_k = (-a_k \mathsf{R}_{kk} + \mathsf{R}_{kk}a_k)/r = 0$
이 되어 소멸한다. $k$ 열 왼쪽은 이미 0 이므로 건드리지 않는다. 모든 비영 성분을 처리하면 새 행이
전부 0 이 되고 남은 상삼각이 갱신된 $\mathsf{R}'$ 이다. 직교성에서 바로

$$
\mathsf{R}'^\top\mathsf{R}' = \mathsf{R}^\top\mathsf{R} + a a^\top \tag{7}
$$

이고, 이것이 정규방정식에 행 하나를 더한 것과 같다(정보행렬을 만들지 않고 랭크-1 갱신을 했다).

**비용.** (6)은 $\mathsf{R}$ 의 $k$ 행에서 $k$ 열부터 끝까지를 건드린다. 그리고 회전 뒤 새 행은
$\mathsf{R}_{k,k:}$ 가 비영인 모든 열에서 비영이 된다 — 즉 **새 행이 $\mathsf{R}$ 의 희소 패턴을
따라 번져 나간다**. 그래서 회전 수는 $a$ 의 원래 비영 개수가 아니라, 첫 비영 열 $k_0$ 에서
출발해 패턴을 따라 도달하는 열의 수이고 상계가 $N - k_0 + 1$ 이다. 결론:

- 인자가 **순서의 끝쪽 변수**에만 닿으면 $k_0 \approx N$ 이라 회전 수가 $n$ 과 무관한 상수다.
- 인자가 **순서의 처음쪽 변수**에 닿으면 $k_0 \approx 1$ 이라 회전 수가 $\Theta(N)$ 이다.

재현 과제의 실측값이 이것을 그대로 보여 준다: 마지막 오도메트리 간선 추가는
$N \in \{300, 600, 1200\}$ 에서 전부 14 회전이고, 포즈 0 으로의 루프 클로저는
$3N - 2$ 회전(898·1798·3598)이다.

**가정이 깨지는 곳**: (7)은 $\mathsf{R}$ 이 **고정된 변수 순서**에 대한 것이다. 재정렬을 하면
$\mathsf{R}$ 을 처음부터 다시 만들어야 하므로 재정렬 자체가 $O(\text{fill})$ 비용이다. 또
(7)은 선형 문제의 정확한 갱신이지 비선형 문제의 재선형화가 아니다 — 야코비안이 바뀌면
$aa^\top$ 을 더하는 것으로는 안 되고, 해당 행을 **빼고** 다시 넣어야 한다. Givens 회전으로는
행을 뺄 수 없으므로(쌍곡 회전이 필요하고 수치적으로 불안정하다) iSAM2 는 영향받은 부분트리를
아예 다시 소거한다.

### R5 — 주변화는 조밀화를 만들고, 희소화에는 최적해가 있다

**조밀화.** `c5-factor-graphs-map` R3 의 6단계에서 $x_v$ 를 소거(또는 주변화)하면
$\mathcal{S}(x_v)$ 가 클리크가 된다. $\deg(x_v) = d$ 이고 $\mathcal{S}(x_v)$ 안에 이미
$e$ 개의 간선이 있었다면 새 간선은 $\binom{d}{2} - e$ 개다. 중간 포즈 하나를 지우는 것은 보통
$d = 2$ 라 간선 1개로 끝나지만, 루프 클로저와 랜드마크가 걸린 포즈는 $d$ 가 커지고, 포즈를
연달아 지우면 $d$ 가 누적해 커진다. 이것이 "오래된 포즈를 주변화해 그래프를 줄이자"가
**실패하는** 이유다 — 변수는 줄지만 간선은 늘고, 결국 밀집 블록이 남는다.

**희소화.** 그러면 주변화 결과 $p = \mathcal{N}(\mu_p, \Sigma_p)$ 를, 허용 패턴 $\mathcal{T}$
밖의 정보 원소가 0 인 $q = \mathcal{N}(\mu_q, \Lambda_q^{-1})$ 로 근사하자. 두 가우시안의
KL 은

$$
2\,\mathrm{KL}(p\Vert q) = \mathrm{tr}(\Lambda_q\Sigma_p) - \log\det(\Lambda_q\Sigma_p) - N
  + (\mu_q - \mu_p)^\top \Lambda_q (\mu_q - \mu_p). \tag{8}
$$

마지막 항은 $\Lambda_q \succ 0$ 이므로 $\mu_q = \mu_p$ 에서만 0 이고, 다른 항은 $\mu_q$ 와
무관하다. 따라서 $\mu_q = \mu_p$. 남은 것을 $\Lambda_q$ 로 미분한다. 대칭 행렬에 대해
$\partial\,\mathrm{tr}(\Lambda\Sigma)/\partial\Lambda = \Sigma$ 이고
$\partial \log\det\Lambda/\partial\Lambda = \Lambda^{-1}$ 이므로

$$
\frac{\partial}{\partial \Lambda_q}\Big[\mathrm{tr}(\Lambda_q\Sigma_p) - \log\det\Lambda_q\Big]
  = \Sigma_p - \Lambda_q^{-1}. \tag{9}
$$

$\Lambda_q$ 는 $\mathcal{T}$ 밖에서 0 으로 **제약**되어 있으므로, 최적 조건은 (9)가 0 이 되는
것이 아니라 **$\mathcal{T}$ 와 대각 성분에 사영한 (9)가 0** 이 되는 것이다:

$$
(\Lambda_q^{-1})_{ij} = (\Sigma_p)_{ij} \quad \text{for } (i,j)\in\mathcal{T}\cup\{\text{대각}\}. \tag{10}
$$

즉 (3)이다. **정보에는 0 을 넣고 공분산은 맞춘다** — 이것이 가우시안 그래프 모델의 최대가능도
(= 최대엔트로피) 해이고, $\mathcal{T}$ 가 트리면 닫힌 형태로 나온다: 간선별 2변수 주변분포의
역행렬을 더하고 내부 노드의 중복을 빼면 된다(Chow-Liu),

$$
\Lambda_q = \sum_{(i,j)\in\mathcal{T}} \big[\Sigma_p^{\{i,j\}}\big]^{-1}
  - \sum_{i} (\deg_{\mathcal{T}}(i) - 1)\,\big[(\Sigma_p)_{ii}\big]^{-1}. \tag{11}
$$

(여기서 $\Sigma_p^{\{i,j\}}$ 는 $(i,j)$ 쌍의 $2\times2$ 주변 공분산이고, 각 항은 전체 크기로
영 채움해 더한다.)

**가정이 깨지는 곳 1**: (10)은 $\mathrm{KL}(p\Vert q)$ (M-사영)의 해다. 방향을 바꿔
$\mathrm{KL}(q\Vert p)$ (I-사영)를 최소화하면 다른 답이 나오고, 그쪽은 분산을 과소평가하는
경향이 있다. 어느 방향이 "맞는지"는 목적에 달렸다 — 보수적 불확실성이 필요한 추정에서는
M-사영이다.

**가정이 깨지는 곳 2**: 가장 흔한 실수는 (10)을 풀지 않고 $\Lambda_p$ 의 해당 원소를 그냥
0 으로 지우는 것이다. 그것은 "그 두 변수가 조건부 독립"이라고 주장하면서 **나머지 정보를 그대로
남기는** 것이므로 정보를 과대계상한다. 문제 P4 의 수치가 그 결과다 — 주변 표준편차가
$(0.1,\ 0.13540064,\ 0.15275252)$ 에서 $(0.08401681,\ 0.11504475,\ 0.12833779)$ 로 약 16%
줄어든다. 과신(overconfidence)은 그 자체로 끝나지 않고 다음 루프 클로저의 이상치 판정을
망가뜨린다. 같은 문제가 원 측정을 재사용해 희소화할 때의 **정보 이중계상**으로도 나타난다
(`carlevaris-bianco2014-node-removal` III절).

## 증명 스케치

### R1 — fill-path 정리

**가설** H1: $\mathcal{G} = (V,E)$ 는 유한 무향 그래프, $\sigma$ 는 전단사 소거 순서.
H2: 소거 한 단계는 "정점 $v$ 를 지우고, 그 시점에 살아 있는 $v$ 의 이웃들을 완전 그래프로
만든다"이며, 이를 $\sigma(1), \sigma(2), \dots$ 순으로 반복한다.
**결론** C: (1)의 두 조건이 동등하다.

**전략**: 양방향 귀납. ($\Leftarrow$) 경로의 **내부 정점 수**에 대한 귀납, ($\Rightarrow$)
**소거 단계**에 대한 귀납.

1. **($\Leftarrow$) 기저.** $k = 1$ 이면 경로가 간선 $\{u,v\}\in E$ 자체이고
   $E \subseteq E^+_\sigma$ 이므로 성립.
2. **($\Leftarrow$) 귀납.** $k \ge 2$ 라 하고 내부 정점 중 $\sigma$ 가 최소인 것을 $w_i$ 라 하자.
   $\sigma(w_i) < \min(\sigma(u),\sigma(v))$ 이고 $\sigma(w_i)$ 가 내부 최소이므로, $w_i$ 를
   소거하는 시점에 $w_{i-1}$ 과 $w_{i+1}$ 은 **둘 다 아직 살아 있고** 둘 다 $w_i$ 의 이웃이다.
   H2 로 $\{w_{i-1}, w_{i+1}\}$ 이 간선이 된다. 이 간선으로 $w_i$ 를 건너뛴 경로를 만들면 내부
   정점이 하나 줄고 "내부 정점이 모두 $\min(\sigma(u),\sigma(v))$ 보다 이르다"는 조건은 유지된다.
   귀납 가설로 $\{u,v\}\in E^+_\sigma$.
3. **($\Rightarrow$) 기저.** $\{u,v\}\in E$ 면 $k=1$ 경로가 바로 증거다.
4. **($\Rightarrow$) 귀납.** $\{u,v\}$ 가 fill 간선이면 그것이 **처음 생기는** 소거 단계가 있고,
   그때 지워지는 정점 $w$ 는 그 시점의 (부분적으로 채워진) 그래프에서 $u$ 와 $v$ 에 모두
   인접하며 $u,v$ 보다 먼저 소거되므로 $\sigma(w) < \min(\sigma(u),\sigma(v))$ 다.
   $\{w,u\}$ 와 $\{w,v\}$ 는 그보다 **이른 단계**에 존재하게 된 간선이므로 귀납 가설이 적용되어
   각각 내부 정점이 $\min(\sigma(w),\sigma(u))$ 와 $\min(\sigma(w),\sigma(v))$ 보다 이른
   $\mathcal{G}$ 안의 경로를 갖는다. $\sigma(w) < \min(\sigma(u),\sigma(v))$ 이므로 두 경로를
   $w$ 에서 이어 붙이면 내부 정점이 전부 $\min(\sigma(u),\sigma(v))$ 보다 이르다. C.
5. **따름정리 1 (비용).** $\mathsf{R}$ 의 $j$ 열 비영 개수는 $\mathcal{G}^+_\sigma$ 에서
   $j$ 보다 늦게 소거되는 이웃의 수 + 1 이다. 따라서
   $\mathrm{nnz}(\mathsf{R}) = n + \lvert E^+_\sigma\rvert$ 이고 flops 는
   $\sum_j (\text{그 열의 비영 개수})^2$ 규모다. 클리크 크기의 최대가 $w+1$ 이면
   저장은 $O(nw)$, 연산은 $O(nw^2)$ 이다.
6. **따름정리 2 (chordality).** fill-in 이 0 인 $\sigma$ 가 존재 $\iff$ $\mathcal{G}$ 가
   chordal. ($\Rightarrow$) fill 이 0 이면 (1)에서 모든 유도 순환이 길이 3 이어야 한다.
   ($\Leftarrow$) chordal 그래프는 완전 소거 순서(perfect elimination ordering)를 가진다
   (`rose1976-vertex-elimination`). **사슬과 트리는 chordal** 이므로 오도메트리만 있는 그래프는
   자연 순서에서 fill 이 0 이다 — 필터가 싸게 도는 구조적 이유이고, 루프 클로저가 순환을 만들어
   그 성질을 깨뜨린다.

**가설을 지우면**: H2 에서 "이웃을 완전 그래프로"를 버리면(근사 소거·희소화) $E^+$ 는 작아지지만
결과가 더는 정확한 주변분포가 아니다 — R5 가 그 대가를 정량화한다. 또 (1)이 **수치에 전혀
의존하지 않는다**는 점이 중요하다: 우연한 수치 상쇄로 비영이 0 이 되는 경우를 제외하면, 희소성은
순서와 그래프만으로 미리 계산할 수 있다(기호적 분해, symbolic factorization).

(생략: ($\Rightarrow$) 귀납이 well-founded 하다는 것과 완전 소거 순서의 존재 증명.
`rose1976-vertex-elimination` §2-3 의 보조정리들로.)

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (증명, ★★★, R1)** fill-path 정리의 ($\Leftarrow$) 방향을 빠진 줄 없이 쓰고, 따름정리 2 의
($\Rightarrow$) 방향("fill 이 0 이면 chordal")을 증명하라. 이어서 길이 $m \ge 4$ 인 순환
$C_m$ 에서 **어떤 순서를 쓰든** fill-in 이 정확히 $m - 3$ 임을 보여라.
*전략 + 핵심 부등식*: ($\Leftarrow$)는 본문 2단계의 "내부 최소 정점"을 고르는 것이 전부다 —
왜 최소여야 하는지(둘 다 살아 있어야 한다)를 명시하라. 따름정리는 길이 $\ge 4$ 유도 순환을
가정하고 그 순환의 가장 이른 정점에 (1)을 적용한다. $C_m$ 은 소거가 순환을 삼각분할
(triangulation)하는 것과 같고, $m$-각형의 삼각분할에 필요한 대각선이 항상 $m-3$ 개라는 사실로
끝난다. 전개는 숨긴다.

**P2 (유도, ★★, R4)** (5)(6)에서 출발해 ⓐ (7)을 유도하고, ⓑ 한 행을 접는 데 드는 부동소수점
연산 수를 $\mathsf{R}$ 의 열별 비영 개수로 표현하고, ⓒ Givens 로 갱신한 $\mathsf{R}'$ 이
$\Lambda + aa^\top$ 의 Cholesky 인자와 **행별 부호를 빼면** 같음을 보여라.
*해답 스케치*: ⓐ 회전 $Q_k$ 들의 곱이 직교이므로
$\begin{bmatrix}\mathsf{R}\\a^\top\end{bmatrix}^\top\begin{bmatrix}\mathsf{R}\\a^\top\end{bmatrix}$
가 보존된다는 한 줄. ⓒ 상삼각이고 대각이 양수인 Cholesky 인자의 유일성을 쓴다 — Givens 는
대각 부호를 보장하지 않으므로 $\mathrm{diag}(\pm1)$ 만큼 다를 수 있다.

**P3 (계산, ★, R1)** 포즈 $p_0,\dots,p_4$ 가 사슬로 이어져 있고(간선 4개) 랜드마크 $\ell$ 이
다섯 포즈 **전부**와 연결되어 있다(간선 5개). 블록을 스칼라로 보고 ⓐ 순서
$(\ell, p_0, p_1, p_2, p_3, p_4)$, ⓑ 순서 $(p_0, p_1, p_2, p_3, p_4, \ell)$ 각각의 fill-in 개수와
$\mathrm{nnz}(\mathsf{R})$ 을 구하라. ⓒ 그런데 번들 조정(bundle adjustment)은 랜드마크를 **먼저**
소거한다. 모순이 아닌 이유를 설명하라.
*정답*: ⓐ fill 6개, $\mathrm{nnz}(\mathsf{R}) = 6 + (9 + 6) = 21$. ⓑ fill 0개,
$\mathrm{nnz}(\mathsf{R}) = 6 + 9 = 15$. 허용오차 0(정수).
검산: (1)로 직접 확인한다 — ⓐ 에서 채워지는 간선은 $\{p_i, p_j\}$ 중 사슬에 없던 6개
($\binom52 = 10$ 에서 사슬 4개를 뺀 수)이고, ⓑ 에서는 어떤 $p_i$ 를 소거해도 이웃이
$\{p_{i+1}, \ell\}$ 이고 그 쌍은 이미 간선이다.
*ⓒ의 채점 포인트*: BA 는 fill 총량이 아니라 **남는 밀집 블록의 크기**를 줄이려 한다 —
랜드마크가 수십만 개, 카메라가 수백 개이면 랜드마크를 소거해 얻는 축소 카메라 계
($\binom{n_c}{2}$ 밀집)가 전체보다 훨씬 작다. 또 랜드마크끼리는 서로 간선이 없어 $\Lambda_{11}$
이 블록 대각이고 역행렬이 공짜다. "fill 이 적은 순서가 항상 빠른 순서는 아니다"를 짚어야 통과.

**P4 (계산, ★★, R5)** `c5-factor-graphs-map` P3 의 1차원 포즈 그래프
($\Lambda_p = \begin{bmatrix}225&-100&-25\\-100&200&-100\\-25&-100&125\end{bmatrix}$)에서
$(1,3)$ 정보 원소를 없애는 두 가지 희소화를 비교하라. ⓐ (3)·(11)의 KL 최적해 $\Lambda_q$,
ⓑ $\Lambda_p$ 의 $(1,3)$ 을 그냥 0 으로 놓은 $\Lambda_{\mathrm{naive}}$. 각각의 주변 표준편차와
$\mathrm{KL}(p\Vert q)$ 를 구하라.
*정답*: ⓐ $\Lambda_q = \begin{bmatrix}220 & -120 & 0\\ -120 & 21880/99 & -1000/9\\
0 & -1000/9 & 1100/9\end{bmatrix}$, 주변 표준편차는 $p$ 와 **정확히 같다**
$(0.1,\ 0.13540064,\ 0.15275252)$, $\mathrm{KL}(p\Vert q) = 0.0112364279$. 유일하게 틀리는 적률은
$\Sigma_q[1,3] = 1/110 = 0.00909091$ (참값 $0.01$).
ⓑ 주변 표준편차 $(0.08401681,\ 0.11504475,\ 0.12833779)$ — 약 **16% 과소평가**,
$\mathrm{KL}(p\Vert q) = 0.0758466529$ (6.7배 나쁘다). 허용오차 $10^{-8}$.
검산: (10)이 실제로 성립하는지, 즉 $\lvert(\Lambda_q^{-1} - \Sigma_p)_{ij}\rvert < 10^{-12}$ 가
대각과 $(1,2),(2,3)$ 에서 성립하는지 확인한다.

**P5 (구현, ★★, R3·R4)** 재현 과제의 그래프에 대해 ⓐ Givens 증분 솔버, ⓑ 영향받은 변수를
순서의 끝으로 옮기는 **재정렬**을 구현하고, 루프 클로저 1개를 추가할 때의 비용을 재정렬 전후로
비교하라.
*루브릭*: ⓐ 증분 해가 배치 해와 $10^{-9}$ 이내 일치 ⓑ 재정렬 비용(= 다시 만든 $\mathsf{R}$ 의
회전 수)과 재정렬로 절약한 비용을 **같은 단위**로 보고 ⓒ 재정렬이 언제 이득인지(한 번의 루프
클로저로는 보통 손해, 같은 영역에 반복해서 인자가 들어올 때 이득) 수치로 논증 ⓓ 재정렬 뒤의
$\mathrm{nnz}(\mathsf{R})$ 변화를 함께 보고.

**P6 (반례, ★★, R3)** iSAM2 의 재선형화 임계값 $\tau$ 가 "충분히 작으면 배치 해에 가깝다"는
직관이 보장이 아님을 보여라. $\tau$ 를 고정한 채 **배치 해와의 차이가 임의로 커지는** 인자 수열을
구성하라.
*성질 체크리스트*: ① 각 단계의 증분이 $\tau$ 미만이어야 한다 ② 증분들이 같은 방향으로 쌓여야
한다(상쇄되면 안 된다) ③ 야코비안이 상태에 의존해 재선형화하지 않은 선형화 지점의 오차가
누적되어야 한다 — 회전 각도가 한 방향으로 조금씩 도는 궤적이 전형적인 예다 ④ 결론을
"$\tau \to 0$ 에서만 수렴"으로 써야 한다. 전체 해답은 쓰지 않는다.

**P7 (논문, ★★, R3)** `kaess2012-isam2` 를 읽고 ⓐ 저자들이 **보장하는 것과 보장하지 않는 것**을
각각 두 줄로 구분하고, ⓑ 논문의 실행 시간 그래프를 재현하는 데 필요한 정보 중 빠진 것 3개를
찾고, ⓒ R4 의 실측(마지막 간선 14 회전 vs 루프 클로저 $3N-2$ 회전)이 논문의 "$O(1)$ 갱신"
주장과 어떻게 맞물리는지 쓰라.
*루브릭*: ⓐ "임계값 0 이면 배치와 동일", "임계값이 0 이 아니면 전역 오차 상계 없음"을 구분하면
통과. ⓑ 임계값의 구체적 값과 단위, CCOLAMD 호출 정책, 데이터셋의 루프 클로저 분포 중 셋.
ⓒ "$O(1)$ 은 **영향받은 부분트리가 상수 크기인 갱신**에 대한 주장이고 루프 클로저는 그 가정
밖이다"를 짚으면 우수. 논문이 그 가정을 어디에 적어 놓았는지(또는 적지 않았는지) 인용하면 더 좋다.

## 논문 읽기

**필독 3편.** 각 논문에 아래 고정 질문 10개로 1페이지 노트를 쓴다
(`lesson-standard.md` §5). 3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Kaess, Johannsson, Roberts et al., "iSAM2: incremental smoothing and mapping using the
   Bayes tree" (2012, IJRR)** — 역할: `원전(seminal)`.
   <https://doi.org/10.1177/0278364911430419> (3-5절)
   추가 질문: ⓐ (2)의 분해가 Bayes **net** 이 아니라 Bayes **tree** 여야 하는 이유를 본문 R3 의
   "조건부는 이미 정규화되어 있다"는 문장으로 다시 쓰면? ⓑ fluid relinearization 의 임계값이
   단위를 갖는가, 즉 회전과 평행이동에 같은 임계값을 쓰는 것이 정당한가?
2. **Rose, Tarjan & Lueker, "Algorithmic aspects of vertex elimination on graphs" (1976, SIAM
   J. Comput.)** — 역할: `원전(seminal)`. <https://doi.org/10.1137/0205021> (§2-3)
   추가 질문: ⓐ 이 논문의 결과 중 **로보틱스에서 쓰이지 않는** 것은 무엇이고 왜 쓰이지 않는가?
   ⓑ 기호적 분해(symbolic factorization)를 수치 분해와 분리할 수 있는 근거가 논문의 어느
   정리인가?
3. **Carlevaris-Bianco, Kaess & Eustice, "Generic node removal for factor-graph SLAM"
   (2014, T-RO)** — 역할: `표준(standard)`. <https://doi.org/10.1109/TRO.2014.2347571> (III-IV절)
   추가 질문: ⓐ 저자들의 근사가 본문 (10)의 M-사영과 같은가 다른가 — 같지 않다면 어디가 다른가?
   ⓑ 정보 이중계상을 피하기 위해 저자들이 무엇을 포기했는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU 1코어, 2분 이내, 메모리 1GB 이하
(가장 큰 경우가 $1200\times1200$ 조밀 $\mathsf{R}$ 이다). numpy + scipy 만 쓴다.

**입력 데이터**는 `c5-factor-graphs-map` 재현 과제의 생성기 `make_graph()` 를 **그대로** 쓴다
(같은 시드, 같은 그래프). 선형화 지점은 그 레슨에서 추측 항법 초기값으로 수렴시킨 GN 최적점
$x^\ast$ 다 — 여기서부터는 순수 선형대수이므로 비선형성이 수치를 흔들지 않는다.

**Part A — 순서가 fill-in 을 결정한다.** $x^\ast$ 에서 $A$ 를 만들고 $\Lambda = A^\top A$
($300\times300$)를 구성한다. 네 가지 **스칼라** 변수 순서에 대해 $P^\top\Lambda P$ 의 Cholesky
인자의 비영 개수($\lvert\cdot\rvert > 10^{-9}$)를 센다.

**Part B — 증분 QR.** $\mathsf{R} = 0$, $d = 0$ 에서 시작해 $A$ 의 행을 **한 줄씩** (5)(6)으로
접는다. 각 행에 쓴 Givens 회전 수를 기록한다.

**Part C — 갱신 비용의 척도.** `make_graph(per_lap=50, every=10)`, `per_lap=100, every=20`,
`per_lap=200, every=40` 세 크기에서, Part B 를 끝낸 $\mathsf{R}$ 에 간선 하나를 더 접을 때의
회전 수를 측정한다 — ⓐ 마지막 두 포즈 $(n-2, n-1)$ 사이, ⓑ 포즈 $0$ 과 $n-1$ 사이.
추가 측정에는 $\bar z = (0.1, 0, 0.02)$, $\sigma = \sigma_{\text{loop}}$ 를 쓴다.

**Part D — 희소화.** 문제 P4 의 $3\times3$ 문제에서 (10)을 수치로 풀어 $\Lambda_q$ 를 얻고,
$\Lambda_{\mathrm{naive}}$ 와 비교한다.

**수용 기준 — 네 조건을 모두 만족해야 통과다.**

1. **Part A 의 값** (전부 $\pm2$ 허용 — $10^{-9}$ 임계에서 경계 원소가 한둘 흔들릴 수 있다):

   | 순서 | $\mathrm{nnz}(\mathsf{R})$ |
   |---|---|
   | 자연 순서 `arange(300)` | 3396 |
   | 역순 `arange(300)[::-1]` | 3354 |
   | 무작위 `default_rng(1).permutation(300)` | 5849 |
   | RCM `scipy.sparse.csgraph.reverse_cuthill_mckee(..., symmetric_mode=True)` | 2953 |

   그리고 $\Lambda$ 의 하삼각 비영 개수는 1018 이다. **무작위 순서가 RCM 의 두 배에 가깝다**는
   것이 R2 의 요점이고, 세 "합리적" 순서 사이의 차(3396 vs 2953)는 14% 다.
2. **Part B 의 정확성**: 증분 $\mathsf{R}$ 로 푼 해가 배치 해
   (`numpy.linalg.solve(Lambda, eta)`)와 $\lVert\cdot\rVert_\infty < 10^{-6}$ 이내로 일치
   (참조 구현 $2.6\times10^{-16}$), 그리고 $\lvert\mathsf{R}_{\text{inc}}\rvert$ 와
   $\lvert\mathrm{chol}(\Lambda)^\top\rvert$ 의 최대 차 $< 10^{-9}$ (참조 $1.1\times10^{-13}$).
   **절댓값으로 비교하는 이유**는 Givens 가 행 부호를 보장하지 않기 때문이다(문제 P2ⓒ).
3. **Part C 의 척도**: 아래 값이 정확히 재현된다(정수).

   | $N$ | 간선 $(n-2, n-1)$ | 간선 $(0, n-1)$ |
   |---|---|---|
   | 300 | 14 | 898 |
   | 600 | 14 | 1798 |
   | 1200 | 14 | 3598 |

   즉 전자는 $n$ 과 **무관한 상수**, 후자는 정확히 $3N - 2$ 다. 이 표를 만들지 못하면
   "$O(1)$ 갱신"이라는 말을 쓸 수 없다.
4. **Part D 의 값**: $\Lambda_q$ 가 (10)을 $10^{-12}$ 이내로 만족하고, 주변 표준편차가
   $p$ 와 $10^{-9}$ 이내로 같으며, $\mathrm{KL}(p\Vert q_{\mathrm{opt}}) = 0.0112364279$,
   $\mathrm{KL}(p\Vert q_{\mathrm{naive}}) = 0.0758466529$ (허용오차 $10^{-8}$).
   $q_{\mathrm{naive}}$ 의 표준편차는 $(0.08401681, 0.11504475, 0.12833779)$ 다.

**비교 대상**: ⓐ Part A·B 의 배치 Cholesky(`numpy.linalg.cholesky`)가 베이스라인이다.
ⓑ Part C 의 베이스라인은 **매번 배치 재분해**이고, 그 비용은 $\mathrm{nnz}(\mathsf{R})$ 규모의
회전 수(참조 구현에서 전체 315 행을 접는 데 3928 회전)다. 14 회전과 3928 회전의 비가 증분
추론이 사는 이유다. 선택: `scipy.sparse.linalg.splu` 의 `permc_spec="COLAMD"` 로 얻은
순서를 Part A 의 다섯 번째 행으로 추가해 RCM 과 비교한다.

**보고할 수치**: 위 네 표 전부, Part B 의 회전 수 분포(참조 구현: 오도메트리 행 평균 1.3·최대 2,
루프 클로저 행 평균 176.4·최대 200, 앵커 행 289·299·298 — **같은 인자라도 언제 접는지에 따라
비용이 200배 다르다**), 그리고 Part A 의 네 순서에서 $\mathrm{nnz}(\mathsf{R})/\mathrm{nnz}(\Lambda)$ 비.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| Part A 의 값이 전부 300 근처로 작다 | $\Lambda$ 가 아니라 $A$ 의 희소성을 세고 있다 | $\Lambda$ 의 모양이 $300\times300$ 인지, 하삼각 비영이 1018 인지 확인 |
| Part A 의 RCM 이 자연 순서보다 나쁘다 | `symmetric_mode=True` 를 빼서 RCM 이 비대칭 패턴으로 돌았다, 또는 순열을 전치해서 적용했다 | $P^\top\Lambda P$ 가 대칭·양정부호인지, `perm` 을 열 순서로 썼는지 확인 |
| Part B 의 해가 $10^{-3}$ 수준으로만 맞는다 | 회전을 $d$ 와 $\beta$ 에 적용하지 않았다 | 우변 없이 $\mathsf{R}$ 만 맞는지 보고, $\lVert\mathsf{R}^\top\mathsf{R} - \Lambda\rVert$ 를 따로 확인 |
| Part B 의 $\mathsf{R}$ 이 Cholesky 와 부호만 다른 게 아니라 값이 다르다 | $k$ 열 **왼쪽**까지 회전을 적용했다(이미 0 인 영역을 건드림) | 슬라이스를 `[k:]` 로 제한했는지 확인 |
| Part C 의 $(n-2,n-1)$ 비용이 $n$ 과 함께 커진다 | 비영 판정 임계값이 없어 수치 쓰레기($10^{-18}$)를 비영으로 세고 있다 | $\lvert a_k\rvert < 10^{-14}$ 를 건너뛰는지 확인 |
| Part D 의 `fsolve` 가 수렴하지 않는다 | 초기값을 0 으로 줬다 — $\Lambda_q$ 는 양정부호여야 한다 | $\Lambda_p$ 에서 해당 원소만 0 으로 한 행렬을 초기값으로 준다 |

## 열린 문제

- **(열린 문제) 온라인 변수 순서에 대한 이론이 없다** — AMD·COLAMD·nested dissection 은
  **배치** 설정의 휴리스틱이고 최소 fill-in 자체가 NP-완전이다
  ([Yannakakis 1981](https://doi.org/10.1137/0602010)). 증분 설정에서는 질문이 다르다: 지금
  재정렬에 돈을 쓰는 것이 앞으로 들어올 인자들에 대해 이득인가? 현재 접근은
  [iSAM2](https://doi.org/10.1177/0278364911430419) 의 CCOLAMD 기반 부분 재정렬과,
  separator 가 작은 그래프족의 상계([nested dissection](https://doi.org/10.1137/0716027))다.
  비어 있는 자리: 온라인 재정렬의 **후회(regret) 경계** — 미래 인자 분포를 모르는 상태에서
  최적 오프라인 순서 대비 얼마나 나쁜지에 대한 보장.
- **(열린 문제) 보장이 있는 희소화** — (10)은 고정 패턴에 대한 KL 최적해를 주지만, 그 KL 값이
  추정 **일관성**(NEES)·루프 클로저 성공률·최종 ATE 에 미치는 영향의 상계는 없다. 패턴
  $\mathcal{T}$ 를 **어떻게 고를지**도 열려 있다(트리는 닫힌 해가 있으나 너무 공격적이다).
  현재 접근: [generic node removal](https://doi.org/10.1109/TRO.2014.2347571) 의 GLC 와
  [장기 SLAM 서베이](https://arxiv.org/abs/1606.05830) §V 의 지도 수명 논의. 비어 있는 자리:
  "이 희소화는 ATE 를 $\epsilon$ 이상 악화시키지 않는다"를 말할 수 있는 조건.
- **(열린 문제) 근사 증분 추론의 전역 오차 경계** — iSAM2 의 재선형화·역대입 임계값은 변수별
  **국소** 판정인데, 누적 오차가 배치 해에서 얼마나 멀어질 수 있는지에 대한 상계가 없다(문제 P6).
  현재 접근: 임계값을 보수적으로 두고 주기적으로 배치 재최적화를 섞는 공학적 타협.
  비어 있는 자리: 임계값 수열에서 전역 오차로 가는 명시적 상계, 또는 임계값을 적응적으로
  정하는 **인증 가능한** 규칙.

## 개념 점검

`rc quiz c5-sparsity-isam` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: c5-sparsity-isam-quiz
questions:
  - id: q1
    type: single
    prompt: "fill-path 정리에 따르면 $\\{u,v\\}$ 가 채워진 간선이 되는 조건은?"
    choices:
      - "$u$ 와 $v$ 가 같은 인자에 닿는다"
      - "$\\mathcal{G}$ 에 $u$-$v$ 경로가 있고 그 내부 정점이 모두 $u,v$ 보다 먼저 소거된다"
      - "$u$ 와 $v$ 의 차수가 모두 3 이상이다"
      - "$\\Lambda_{uv}$ 의 수치가 임계값보다 크다"
    answer: 1
    explanation: "(1)이다. 이 조건은 **수치에 전혀 의존하지 않는다** — 그래서 기호적 분해로 희소성을 미리 계산할 수 있다. 같은 인자에 닿는 것은 원래 간선의 조건이고, 차수나 수치 크기는 관계가 없다."
    concept: { front: "fill-path 정리", back: "$\\{u,v\\}$ 가 fill 간선 $\\iff$ 내부 정점이 전부 $\\min(\\sigma(u),\\sigma(v))$ 보다 먼저 소거되는 $u$-$v$ 경로가 있다 (순서와 그래프만으로 결정)" }
  - id: q2
    type: truefalse
    prompt: "오도메트리만 있는 포즈 그래프(사슬)는 자연 순서에서 fill-in 이 0 이다."
    answer: true
    explanation: "사슬은 chordal 이고(길이 4 이상의 유도 순환이 없다) 자연 순서가 완전 소거 순서다. 각 변수의 separator 가 다음 변수 하나뿐이므로 클리크가 커지지 않는다. 루프 클로저가 순환을 만들면서 이 성질이 깨진다 — 순환 $C_m$ 은 어떤 순서에서도 $m-3$ 개의 fill 을 만든다."
    concept: { front: "사슬·트리의 fill-in", back: "0 — chordal 이므로 완전 소거 순서가 있다. 필터가 싼 구조적 이유이고, 루프 클로저가 그것을 깨뜨린다" }
  - id: q3
    type: single
    prompt: "Bayes tree 에 변수 집합 $V$ 에 닿는 새 인자를 넣을 때 다시 소거해야 하는 것은?"
    choices:
      - "트리 전체"
      - "$V$ 를 포함하는 클리크들만"
      - "$V$ 를 포함하는 클리크들과 그 조상(루트까지)"
      - "$V$ 를 포함하는 클리크들과 그 자손"
    answer: 2
    explanation: "조상까지다. 영향받은 클리크의 변수 분포가 바뀌면 부모의 separator 값이 바뀌어 부모의 조건부를 그 값에서 다시 평가해야 한다. 자손은 영향받지 않는다 — 자손의 인자는 **조건부**이고 자기 separator 의 어떤 값에 대해서도 이미 정규화되어 있다."
    concept: { front: "iSAM2 증분 갱신의 범위", back: "$V$ 를 포함하는 클리크 + 루트까지의 조상. 자손은 조건부이므로 불변 — 이것이 Bayes net 이 아니라 Bayes tree 를 쓰는 이유" }
  - id: q4
    type: single
    prompt: "증분 QR 에서 새 측정 행 하나를 접는 비용을 결정하는 것은?"
    choices:
      - "그 행의 원래 비영 개수"
      - "그 행이 닿는 변수의 개수"
      - "그 행의 첫 비영 열 $k_0$ — 비용 상계가 $N - k_0 + 1$ 이다"
      - "$\\Lambda$ 의 조건수"
    answer: 2
    explanation: "회전을 적용하면 새 행이 $\\mathsf{R}$ 의 희소 패턴을 따라 오른쪽으로 번지므로, 원래 비영 개수가 아니라 **첫 비영 열의 위치**가 비용을 정한다. 그래서 순서의 끝쪽 변수만 닿는 인자는 $O(1)$, 포즈 0 에 닿는 루프 클로저는 $\\Theta(N)$ 이다."
    concept: { front: "Givens 증분 갱신의 비용", back: "첫 비영 열 $k_0$ 가 결정한다(상계 $N-k_0+1$). 최근 변수만 닿으면 $O(1)$, 오래된 변수에 닿으면 $\\Theta(N)$" }
  - id: q5
    type: single
    prompt: "주변화로 얻은 밀집 가우시안을 허용 패턴 $\\mathcal{T}$ 로 희소화할 때, $\\mathrm{KL}(p\\Vert q)$ 를 최소화하는 $q$ 는?"
    choices:
      - "$\\Lambda_p$ 에서 $\\mathcal{T}$ 밖 원소를 0 으로 지운 것"
      - "$\\Sigma_p$ 에서 $\\mathcal{T}$ 밖 원소를 0 으로 지운 것"
      - "$\\mathcal{T}$ 위에서 $\\Lambda_q^{-1}$ 이 $\\Sigma_p$ 와 일치하는 $q$"
      - "$\\Lambda_q = \\mathrm{diag}(\\Lambda_p)$ 인 $q$"
    answer: 2
    explanation: "(10)이다 — 정보에는 0 을 넣고 **공분산(적률)은 패턴 위에서 정확히 맞춘다**. 1번처럼 정보 원소를 그냥 지우면 조건부 독립을 주장하면서 나머지 정보를 그대로 남기므로 과대계상이 되고, 문제 P4 에서 주변 표준편차를 16% 과소평가한다."
    concept: { front: "KL 최적 희소화 (M-사영)", back: "$(\\Lambda_q^{-1})_{ij} = (\\Sigma_p)_{ij}$ on $\\mathcal{T}$ — 정보는 0, 적률은 일치. 정보 원소를 지우는 것은 과신을 만든다" }
```

## 이 단계 공부법

1. **그래프로 먼저 생각한다 (45분)** — $8$ 정점 정도의 작은 포즈 그래프를 그리고 두 가지 순서로
   손으로 소거해 fill 간선을 직접 칠한다. 그 다음 (1)로 같은 답이 나오는지 대조한다. 이 대조가
   되면 "희소성은 수치가 아니라 구조"라는 문장이 몸에 남는다.
2. **fill-path 정리의 ($\Leftarrow$)를 백지에서 (60분)** — 핵심은 내부 정점 중 **가장 먼저
   소거되는** 것을 고르는 한 줄이다. 왜 "가장 먼저"여야 하는지 설명할 수 없으면 증명을 이해한
   것이 아니다. P1 을 풀면 그 자리가 보인다.
3. **Givens 를 $3\times3$ 으로 손으로 (45분)** — $\mathsf{R}$ 을 $3\times3$ 으로 두고 행 하나를
   손으로 접어 (7)을 숫자로 확인한다. 그 다음 **첫 비영 열을 바꿔** 회전 수가 달라지는 것을
   본다. R4 의 결론이 여기서 끝난다.
4. **재현 과제의 Part C 를 먼저 한다 (60분)** — 네 Part 중 가장 짧고 가장 인상적이다. 14 vs
   $3N-2$ 를 직접 찍어 보면 iSAM2 논문을 읽을 이유가 생긴다.
5. **Part A·B·D (105분)** — Part A 에서 무작위 순서가 얼마나 나쁜지 보고, Part B 에서 증분과
   배치가 $10^{-16}$ 으로 같은 것을 확인하고, Part D 에서 희소화를 두 방법으로 해 과신을 본다.
   Barfoot SER ch.3.3 을 Part A 와 함께 읽는다.
6. **논문은 순서대로 (150분)** — Rose et al. §2-3 을 먼저(정리의 원문), iSAM2 3-5절을 다음(그
   정리의 응용), node removal III-IV 절을 마지막(그 한계)으로 읽는다. 논문당 1페이지 노트는
   **반드시** 쓴다. Yannakakis 는 4쪽이므로 쉬는 시간에 통독한다.
7. **무엇을 못 하는지로 끝낸다 (30분)** — "열린 문제" 세 개 중 하나를 골라 왜 아직 안 풀렸는지
   한 문단으로 쓴다. 온라인 재정렬의 후회 경계는 이 레슨에서 가장 손에 잡히는 연구 주제다.

**통과 기준**: 백지에서 (1)을 진술하고 ($\Leftarrow$)를 증명할 수 있고, (7)과 Givens 비용
논증을 쓸 수 있고, 재현 과제의 네 표를 전부 재현한 코드를 갖고 있고, 논문 3편의 노트가 있다.
