---
id: s4-robot-data-scaling
title: 대규모 로봇 데이터와 스케일링
summary: >-
  스케일링 법칙이 왜 "거듭제곱 항 + 줄지 않는 바닥"의 형태를 갖는지를 최소제곱의 초과 위험에서
  유도하고, 서로 어긋나는 데이터셋을 섞으면 **표본 수로 지워지지 않는 편향 바닥**이 생김을
  닫힌 형태로 보인다. 그 바닥이 분산 항을 넘어서는 지점이 "데이터를 더 모아도 나아지지 않는"
  붕괴 조건이다. 마지막으로 도메인 가중(리밸런싱)의 최적값이 불일치 크기와 목표 데이터 양에
  어떻게 의존하는지 유도하고 수치로 확인한다.
objectives:
  - 최소제곱의 초과 위험에서 $L(N) = \sigma^2 + \sigma^2 p/(N-p-1)$ 를 유도할 수 있다.
  - 스케일링 법칙의 거듭제곱 지수와 바닥이 각각 무엇에서 오는지 구분해 설명할 수 있다.
  - 혼합 데이터의 점근 편향을 닫힌 형태로 유도하고 그것이 $N$ 과 무관함을 보일 수 있다.
  - 붕괴 조건(편향 바닥이 분산 항을 넘는 표본 수)을 계산할 수 있다.
  - 도메인 가중 $\gamma^\star$ 가 불일치 크기와 목표 데이터 양에 어떻게 의존하는지 유도할 수 있다.
  - 데이터를 더 모으는 것과 섞는 비율을 고치는 것 중 무엇이 효과적인지 수치로 판정할 수 있다.
prerequisites: [c8-offline-rl, c8-generalization-sim2real]
difficulty: 4
estimated_minutes: 480
tags: [scaling-laws, robot-data, data-mixture, open-x-embodiment, research]
activities:
  - id: s4-robot-data-scaling-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 80
  - id: s4-robot-data-scaling-papers
    kind: paper
    title: 필독 논문 2편 읽기 + 논문별 1페이지 노트
    estimated_minutes: 110
  - id: s4-robot-data-scaling-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1 · 논문 1)
    estimated_minutes: 150
  - id: s4-robot-data-scaling-reproduction
    kind: reproduction
    title: 재현 과제 — 성능-데이터 곡선과 혼합 편향 바닥 (R2)
    estimated_minutes: 125
  - id: s4-robot-data-scaling-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
papers:
  - id: kaplan2020-scaling-laws
    required: true
    role: seminal
    note: "§1-3, §6"
  - id: oxe2023-open-x-embodiment
    required: true
    role: frontier
    note: "§3-5"
resources:
  - title: "Hastie, Tibshirani & Friedman, The Elements of Statistical Learning (2nd ed.)"
    url: https://hastie.su.domains/ElemStatLearn/
    kind: book
    note: ch.3 (선형 회귀의 편향-분산), ch.7 (모델 평가). 전문 PDF 무료.
  - title: "Open X-Embodiment 데이터셋"
    url: https://robotics-transformer-x.github.io/
    kind: dataset
    note: 레슨의 선택 확장에서 쓰는 공개 로봇 데이터 혼합(60여 개 데이터셋).
  - title: "Hoffmann et al. — Training compute-optimal large language models (2022)"
    url: https://arxiv.org/abs/2203.15556
    kind: paper
    note: 권장. 계산 예산 하에서 모델 크기와 데이터 양의 배분(Chinchilla).
  - title: "Hestness et al. — Deep learning scaling is predictable, empirically (2017)"
    url: https://arxiv.org/abs/1712.00409
    kind: paper
    note: 권장. 거듭제곱 법칙과 "되돌릴 수 없는 오차 바닥"을 처음 체계적으로 측정한 글.
---

# 대규모 로봇 데이터와 스케일링

## 전제와 기호

이 레슨은 specialization 트랙 S4 의 첫 레슨이다. `c8-offline-rl` 의 분포 이동 관점과
`c8-generalization-sim2real` 의 평균 목적함수 논의를 쓴다. 추가 **권장 선수**:

- 선형대수: 정규방정식, 유사역행렬, 대칭 양정부호 행렬의 2차형식.
- 확률: 조건부 기댓값, 추정량의 편향-분산 분해, 큰 수의 법칙.
- 통계: 최소제곱 추정량의 분포, 자유도(degrees of freedom).

표기:

| 기호 | 뜻 |
|---|---|
| $\phi(x) \in \mathbb{R}^p$ | 고정된 특징 사상(동결 표현 또는 랜덤 특징). $p$ 는 **학습되는 매개변수 수** |
| $w \in \mathbb{R}^p$ | 선형 정책(또는 회귀) 계수. 참값은 도메인마다 $w_A$, $w_B$ |
| $\sigma^2$ | 라벨 잡음의 분산. **되돌릴 수 없는 바닥**(aleatoric) |
| $N$ | 학습 표본 수. 도메인별로 $N_A$, $N_B$ |
| $\beta$ | 혼합 비율. 전체 $N$ 중 도메인 B 의 비중 |
| $\gamma$ | 도메인 B 표본의 손실 가중(리밸런싱). $\gamma=1$ 은 그냥 합치기, $\gamma=0$ 은 버리기 |
| $\Sigma_D$ | 도메인 $D$ 의 특징 2차 모멘트 $\mathbb{E}_D[\phi\phi^\top]$ |
| $\Delta$ | 도메인 불일치. $\Delta = w_B - w_A$ |
| $L_A(\pi)$ | 목표 도메인 A 에서의 기대 손실(제곱 오차) |

**범위를 좁히는 이유.** "스케일링 법칙"을 심층망에서 증명하는 것은 열린 문제다. 이 레슨은
**동결 표현 위의 선형 정책**이라는 축소 모형에서 법칙의 **형태**를 정확히 유도한다. 그 모형은
S4 의 실제 관행(사전학습 표현 동결 + 작은 헤드 학습, `s4-pretrained-representations`)과
일치하고, 거듭제곱 지수와 바닥이 각각 어디서 오는지를 숨김 없이 보여준다. 심층망으로의 확장이
왜 어려운지는 열린 문제에서 다룬다.

## 시작 전 자가 진단

S4 모듈의 첫 레슨이므로 모듈 전체의 선수지식을 여기서 점검한다. 네 문항 모두 **채점 가능**하다 —
종이와 계산기로 10분 안에 풀고 정답과 맞춰 본다. 3문항 이상 맞으면 이 모듈을 바로 시작한다.
선수는 **권장**이고 플랫폼이 잠그지 않는다.

**D1 (최소제곱, 선수: `r0-linear-algebra-decompositions`)** 설계행렬
$F \in \mathbb{R}^{N\times p}$ 가 열 완전계수일 때 $\hat{w} = \arg\min_w \lVert y - Fw\rVert_2^2$ 를
정규방정식으로 쓰고, $y = Fw^\star + \varepsilon$ ($\mathbb{E}[\varepsilon]=0$,
$\mathrm{Cov}(\varepsilon) = \sigma^2 I$)일 때 $\mathrm{Cov}(\hat{w})$ 를 구하라.
*정답*: $\hat{w} = (F^\top F)^{-1}F^\top y$, $\mathrm{Cov}(\hat{w}) = \sigma^2 (F^\top F)^{-1}$.

**D2 (자유도, 선수: 통계)** 위 설정에서 **학습 표본에서의** 잔차 제곱 평균
$\frac{1}{N}\lVert y - F\hat{w}\rVert^2$ 의 기댓값은?
*정답*: $\sigma^2 (N-p)/N$. 허용오차 없음(정확한 식). 즉 학습 손실은 $\sigma^2$ 보다 **작게**
나오고, 그 차이가 과적합의 정확한 크기다.

**D3 (분포 이동, 선수: `c8-generalization-sim2real`)** $\lvert J_\xi \rvert \le V_{\max}$ 일 때
$\lvert \mathbb{E}_p[J] - \mathbb{E}_q[J]\rvert$ 를 $D_{\mathrm{TV}}(p,q)$ 로 묶으면?
*정답*: $\le 2 V_{\max} D_{\mathrm{TV}}(p,q)$.

**D4 (거듭제곱 법칙 읽기, 선수: 없음)** 로그-로그 축에서 기울기가 $-1$ 인 직선은 $L$ 과 $N$ 의
어떤 관계인가? $N$ 을 10배 늘리면 $L$ 은 몇 배가 되는가?
*정답*: $L \propto N^{-1}$, 즉 $1/10$ 배(허용오차 없음). 바닥 $L_\infty$ 가 있으면 큰 $N$ 에서
기울기가 $0$ 으로 꺾인다 — 그 꺾임을 바닥의 존재로 읽는 것이 이 레슨의 핵심 독법이다.

## 핵심 결과

괄호 안은 유도 깊이 등급이다(`research_notes/연구 트랙 설계/lesson-standard.md` §2).

- **R1 (스케일링 법칙의 형태) [D2]** — 동결 특징 위 최소제곱에서, 가우시안 설계와 잘 지정된
  모형($y = \phi^\top w_A + \varepsilon$)을 가정하면 목표 도메인의 기대 시험 손실이
  $$
  L_A(N) \;=\; \sigma^2\Big(1 + \frac{p}{N-p-1}\Big)
    \;=\; \underbrace{\sigma^2}_{\text{되돌릴 수 없는 바닥}} \;+\; \underbrace{\frac{\sigma^2 p}{N-p-1}}_{\;\propto\, N^{-1}} \tag{1}
  $$
  이다. **거듭제곱 지수는 매개변수 수가 아니라 "유효 자유도 / 표본 수"에서 나오고, 바닥은
  라벨 잡음에서 나온다.** 로그-로그 도표의 꺾임은 모형의 한계가 아니라 **$\sigma^2$ 의 존재**를
  보는 것이다.
- **R2 (혼합 데이터의 편향 바닥 = 붕괴 조건) [D2]** — 도메인 B 의 표본을 비중 $\beta$, 가중
  $\gamma$ 로 섞으면 추정량이 $N\to\infty$ 에서
  $$
  \hat{w} \;\longrightarrow\; w_A + \gamma\beta\, M^{-1}\Sigma_B \Delta,
    \qquad M := (1-\beta)\Sigma_A + \gamma\beta\,\Sigma_B \tag{2}
  $$
  로 수렴하고, 목표 도메인의 초과 손실이
  $$
  \mathrm{bias}(\beta,\gamma) \;=\; \big(\gamma\beta\, M^{-1}\Sigma_B\Delta\big)^\top
    \Sigma_A \big(\gamma\beta\, M^{-1}\Sigma_B\Delta\big) \tag{3}
  $$
  로 **$N$ 과 무관하게** 남는다. 따라서 $\mathrm{bias}(\beta,\gamma) > \sigma^2 p/(N-p-1)$ 가
  되는 표본 수를 넘으면 **데이터를 더 모아도 나아지지 않는다** — 이것이 붕괴 조건이다.
- **R3 (리밸런싱의 최적 가중) [D2]** — 손실을 $\mathrm{bias}(\gamma) + \sigma^2 p/N_{\mathrm{eff}}(\gamma)$
  로 쪼개면 최적 가중 $\gamma^\star$ 는 두 항의 균형점이고,
  $$
  \gamma^\star \;\downarrow\; \text{불일치 } \lVert\Delta\rVert \text{ 가 커질 때}, \qquad
  \gamma^\star \;\downarrow\; \text{목표 데이터 } N_A \text{ 가 많아질 때}. \tag{4}
  $$
  재현 과제에서 네 조합을 측정한다: 불일치가 작고 목표 데이터가 적을 때 $\gamma^\star$ 는
  $0.4$ 이고 **버리는 것보다 3.16배 좋다**. 불일치가 크고 목표 데이터가 넉넉하면
  $\gamma^\star = 0$ — **off-도메인 데이터는 순손실**이다.
- **R4 (왜 로봇 데이터에서 특히 문제인가) [D1]** — Open X-Embodiment 류의 혼합은 **수십 개의
  작고 서로 어긋나는 도메인**이다. 로봇·그리퍼·제어 주기·행동 좌표계가 다르면 같은 관측에
  대한 올바른 행동이 달라져 $\Delta$ 가 크다. (3)은 그 경우 바닥이 $\gamma^2\beta^2$ 로 커짐을
  말하므로, **데이터셋 수를 늘리는 것이 아니라 가중을 고치는 것**이 지배적인 설계 변수가 된다.

## 유도

### R1 — 스케일링 법칙의 형태

**설정.** 특징 $\phi(x)\in\mathbb{R}^p$ 는 고정(동결)이고, 라벨은
$y = \phi(x)^\top w_A + \varepsilon$, $\varepsilon \sim \mathcal{N}(0,\sigma^2)$ 로 생성된다.
$N$ 개 표본의 설계행렬을 $F$, 라벨을 $y$ 라 하면 $\hat{w} = (F^\top F)^{-1}F^\top y$ 다.

**1단계: 초과 위험을 2차형식으로.** 새 점 $x$ 에서의 기대 제곱 오차는

$$
L_A(\hat{w}) = \mathbb{E}_{x,\varepsilon}\big[(\phi^\top\hat{w} - \phi^\top w_A - \varepsilon)^2\big]
  = \sigma^2 + (\hat{w}-w_A)^\top \Sigma_A (\hat{w}-w_A),
$$

$\varepsilon$ 이 $x$ 와 독립이므로 교차항이 사라진다. **바닥 $\sigma^2$ 가 여기서 분리된다.**

**2단계: 추정 오차의 공분산.** $\hat{w} - w_A = (F^\top F)^{-1}F^\top \varepsilon$ 이므로
설계 $F$ 를 조건으로

$$
\mathbb{E}\big[(\hat{w}-w_A)(\hat{w}-w_A)^\top \mid F\big] = \sigma^2 (F^\top F)^{-1}.
$$

따라서 조건부 초과 위험은 $\sigma^2 \operatorname{tr}\big(\Sigma_A (F^\top F)^{-1}\big)$ 다.

**3단계: 설계에 대한 기댓값.** $\phi(x)$ 가 공분산 $\Sigma_A$ 의 가우시안이면
$F^\top F \sim \mathrm{Wishart}_p(N, \Sigma_A)$ 이고, 역 Wishart 의 평균이
$\mathbb{E}[(F^\top F)^{-1}] = \Sigma_A^{-1}/(N-p-1)$ ($N > p+1$)이므로

$$
\mathbb{E}\big[\sigma^2\operatorname{tr}(\Sigma_A (F^\top F)^{-1})\big]
  = \frac{\sigma^2}{N-p-1}\operatorname{tr}(\Sigma_A\Sigma_A^{-1}) = \frac{\sigma^2 p}{N-p-1},
$$

즉 (1)이다. (비가우시안 설계에서는 등식이 아니라 $N\gg p$ 의 점근식 $\sigma^2 p/N$ 이다.)

**읽는 법 — 지수와 바닥은 다른 데서 온다.** (1)을 로그-로그로 그리면 $N \ll$ 바닥 교차점에서
기울기 $-1$ 의 직선, 그 뒤로 평평한 바닥이다. 실측 곡선에서 기울기를 재면 **유효 자유도**를
읽는 것이고, 꺾임 높이를 재면 **$\sigma^2$**(라벨 잡음·시연 다봉성·센서 노이즈)를 읽는 것이다.
두 양은 서로 독립이므로 "모델을 키워 기울기를 개선한다"와 "바닥을 내린다"는 **다른 작업**이다 —
Kaplan et al. 이 매개변수·데이터·계산을 각각 따로 맞춘 이유가 이것이다.

**가정이 깨지는 곳.** 모형이 **잘 지정**되어 있다고 가정했다($w_A$ 가 특징 공간 안에 있다).
오지정(misspecification)이 있으면 1단계의 분해에 **잡음과 무관한 근사 오차**가 더해져
바닥이 $\sigma^2$ 보다 높아진다. 그 바닥은 $N$ 으로 내려가지 않으므로, 실측 바닥을 보고
"라벨 잡음"이라고 단정하면 틀린다 — 오지정과 잡음을 구분하려면 모형 용량을 바꿔 바닥이
움직이는지 봐야 한다(문제 P5). 또 $N \le p+1$ 에서는 (1)이 발산하고 실제로는 이중 하강
(double descent)이 나타난다 — 보간 임계점 근방은 이 유도의 범위 밖이다.

### R2 — 혼합이 만드는 편향 바닥

**가중 최소제곱.** 도메인 A 에서 $N_A = (1-\beta)N$ 개, B 에서 $N_B = \beta N$ 개를 모으고
B 의 제곱 손실에 가중 $\gamma$ 를 준다:

$$
\hat{w} = \arg\min_w \; \sum_{i \in A}\big(y_i - \phi_i^\top w\big)^2
  + \gamma \sum_{j \in B}\big(y_j - \phi_j^\top w\big)^2 .
$$

**1단계: 큰 표본 극한.** 각 합을 $N$ 으로 나누면 큰 수의 법칙으로 목적함수가

$$
(1-\beta)\,\mathbb{E}_A\big[(y-\phi^\top w)^2\big] + \gamma\beta\,\mathbb{E}_B\big[(y-\phi^\top w)^2\big]
$$

로 수렴한다. 각 항을 $w$ 로 미분해 0 으로 두면 **가중 정규방정식**

$$
\big[(1-\beta)\Sigma_A + \gamma\beta\Sigma_B\big] w
  = (1-\beta)\Sigma_A w_A + \gamma\beta\Sigma_B w_B \tag{5}
$$

을 얻는다($\mathbb{E}_D[\phi y] = \Sigma_D w_D$ 를 썼다).

**2단계: 해를 $w_A$ 기준으로 쓴다.** (5)의 우변에서 $M w_A$ 를 더하고 빼면
($M = (1-\beta)\Sigma_A + \gamma\beta\Sigma_B$)

$$
M w = M w_A + \gamma\beta\Sigma_B (w_B - w_A)
  \;\Longrightarrow\; w_\infty = w_A + \gamma\beta\, M^{-1}\Sigma_B\Delta ,
$$

즉 (2)다. **$N$ 이 어디에도 없다** — 이것이 요점이다.

**3단계: 목표 손실로 옮긴다.** R1 의 1단계 분해를 $w_\infty$ 에 적용하면 초과 손실이
$(w_\infty - w_A)^\top\Sigma_A(w_\infty-w_A)$ 이고, (2)를 대입하면 (3)이다.

**붕괴 조건.** 유한 $N$ 에서 손실은 대략

$$
L_A(N,\beta,\gamma) \;\approx\; \sigma^2 \;+\; \mathrm{bias}(\beta,\gamma)
  \;+\; \frac{\sigma^2 p}{N_{\mathrm{eff}}(\beta,\gamma) - p - 1} \tag{6}
$$

이고, 셋째 항이 둘째 항보다 작아지는 $N$ 을 넘으면 **표본 수를 늘려도 총 손실이 거의 변하지
않는다**. 가장 단순한 추정은 $N_{\mathrm{eff}} \approx N$ 으로 두고

$$
N^\dagger \;=\; p + 1 + \frac{\sigma^2 p}{\mathrm{bias}(\beta,\gamma)} \tag{7}
$$

이다. 재현 과제의 설정($p=40$, $\sigma^2=0.01$, $\beta=0.5$, $\gamma=1$, $\mathrm{bias}=0.01226$)
에서 $N^\dagger \approx 74$ — **표본 74개를 넘으면 더 모으는 것이 거의 무의미하다.**
실측은 $N$ 을 $200 \to 3200$ 으로 16배 늘렸을 때 손실이 $0.0291 \to 0.0228$ 로 **22%만**
줄고 바닥 $\sigma^2 + \mathrm{bias} = 0.0223$ 에 붙는다.

**가정이 깨지는 곳.** (7)은 $N_{\mathrm{eff}} = N$ 으로 보지만, 혼합에서는 목표 도메인 방향의
유효 표본이 $N$ 보다 적어 전이 구간이 더 길다(실측 $N=200$ 에서 분산 항이 (7)의 추정보다 큼).
따라서 (7)은 붕괴 지점의 **하한**으로 읽어야 한다. 또 (5)는 가중이 **도메인 단위로 상수**임을
전제한다 — 표본별 중요도 가중(밀도비)을 쓰면 $\Sigma$ 가 재가중되어 편향이 0 이 될 수 있지만,
밀도비를 모르고 추정하면 분산이 폭발한다(`c8-offline-rl` R5 의 유효 표본 수와 같은 문제).

### R3 — 리밸런싱의 최적 가중

(6)의 두 항을 $\gamma$ 의 함수로 본다. $\gamma\to0$ 에서 편향은 $0$, 분산은
$\sigma^2 p/(N_A-p-1)$ 로 최대다. $\gamma$ 를 키우면 B 표본이 유효 표본에 더해져 분산이
줄지만 편향이 $\gamma^2$ 규모로 늘어난다((3)에서 $M$ 의 $\gamma$ 의존을 무시하면 정확히
$\gamma^2\beta^2$ 비례). 작은 $\gamma$ 에 대한 1차 근사로

$$
L_A(\gamma) \approx \sigma^2 + c_1\gamma^2\beta^2\lVert\Sigma_B\Delta\rVert^2_{\Sigma_A}
  + \frac{\sigma^2 p}{N_A + \gamma N_B - p - 1},
$$

$\gamma$ 로 미분해 0 으로 두면

$$
2c_1\gamma\beta^2\lVert\Sigma_B\Delta\rVert^2_{\Sigma_A}
  = \frac{\sigma^2 p\,N_B}{(N_A+\gamma N_B-p-1)^2}, \tag{8}
$$

즉 **$\gamma^\star$ 는 $\lVert\Delta\rVert^2$ 에 반비례하고 $N_A$ 가 커지면(우변이 작아지면)
작아진다** — (4)다. 재현 과제가 네 조합으로 이 두 방향을 모두 확인한다.

| 불일치 $\lVert\Delta\rVert$ | 목표 데이터 $N_A$ | $\gamma^\star$ | $\gamma=0$ 대비 |
|---|---|---|---|
| 큼 (0.6) | 적음 (60) | $0.05$ | $1.15$배 좋음 |
| 큼 (0.6) | 많음 (400) | $0$ | off-도메인은 순손실 |
| 작음 (0.08) | 적음 (60) | $0.4$ | **$3.16$배 좋음** |
| 작음 (0.08) | 많음 (400) | $0.4$ | $1.05$배 좋음 |

**읽는 법.** "데이터를 더 모을까, 섞는 비율을 고칠까"는 (8)이 답한다. 목표 데이터가 적고
도메인이 비슷하면 혼합이 압도적으로 이득이고(3.16배), 목표 데이터가 충분하고 도메인이
어긋나면 혼합은 **해롭다**. 두 경우를 구분하지 않고 "데이터가 많을수록 좋다"고 말하는 것이
이 레슨이 겨누는 오류다.

**가정이 깨지는 곳.** (8)은 $M$ 의 $\gamma$ 의존을 무시한 1차 근사다. $\gamma\beta$ 가 1 에
가까우면 $M$ 이 $\Sigma_B$ 쪽으로 기울어 (3)이 $\gamma^2$ 비례를 벗어나 **포화**한다(실측에서
$\gamma$ 가 커질 때 손실 증가가 둔화되는 것이 그 흔적이다). 또 도메인이 둘이 아니라 수십 개면
$\gamma$ 가 벡터가 되고 (8)이 연립방정식이 되는데, 그 해를 데이터로 추정하는 문제가
열린 문제다.

## 증명 스케치

### R1 — 스케일링 법칙의 형태 [D2 → 증명 형태]

**가설** H1: 특징 $\phi$ 가 고정이고 $\Sigma_A = \mathbb{E}_A[\phi\phi^\top] \succ 0$.
H2: 모형이 잘 지정됨($y = \phi^\top w_A + \varepsilon$). H3: $\varepsilon$ 이 $x$ 와 독립,
평균 0, 분산 $\sigma^2$. H4: $\phi(x)$ 가 가우시안이고 $N > p+1$.
**결론** C: (1).

**전략**: 초과 위험을 2차형식으로 분리 → 조건부 공분산 → 역 Wishart 의 평균.

1. 기대 제곱 오차를 $\sigma^2$ 와 2차형식으로 분해한다. 쓰는 것: H2·H3(교차항 소멸).
2. $\hat{w}-w_A = (F^\top F)^{-1}F^\top\varepsilon$ 에서 조건부 공분산을 얻는다. 쓰는 것: H3.
3. $\operatorname{tr}(\Sigma_A(F^\top F)^{-1})$ 의 설계 기댓값을 역 Wishart 평균으로 계산 → C.
   쓰는 것: H4.

**가설 하나를 지우면**: H2 를 지우면(오지정) 1단계에 $N$ 과 무관한 근사 오차가 더해져 바닥이
$\sigma^2$ 보다 높아지고, 실측 바닥에서 잡음을 읽을 수 없게 된다. H4 의 가우시안을 지우면
3단계의 등식이 깨지고 $\sigma^2 p/N$ 의 **점근식**만 남는다. $N \le p+1$ 에서는 역행렬의
평균이 존재하지 않아 (1) 자체가 정의되지 않는다.

생략: 이중 하강 영역($N \approx p$)의 정확한 위험은 랜덤 행렬 이론이 필요하다.

## 문제 세트

해답 방침은 문제마다 적어 두었다. 난이도: ★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1)** (1)을 고정 설계(design-fixed)에서 다시 유도해
$\sigma^2\operatorname{tr}(\Sigma_A(F^\top F)^{-1})$ 를 얻고, $F^\top F \approx N\Sigma_A$ 로
근사해 $\sigma^2 p/N$ 이 됨을 보이라. 그 다음 $-p-1$ 이 어디서 오는지 한 문장으로 쓰라.
*해답 스케치*: 조건부 공분산 $\sigma^2(F^\top F)^{-1}$ 에 $\Sigma_A$ 를 곱해 trace 를 취한다.
$F^\top F \approx N\Sigma_A$ 를 넣으면 $\operatorname{tr}(I_p)/N = p/N$. $-p-1$ 은 설계에 대한
평균을 취할 때 역 Wishart 의 평균이 $\Sigma^{-1}/(N-p-1)$ 이기 때문이고, $N$ 이 $p$ 에 가까울 때
위험이 발산하는 것이 그 자리에서 보인다.

**P2 (증명, ★★★, R2)** (2)의 극한이 $N$ 과 무관함을 엄밀히 쓰라: 가중 경험 목적함수가
모집단 목적함수로 **균등 수렴**한다는 조건을 적고, 최소점의 수렴을 결론하라. 그 다음
$\mathrm{bias}(\beta,\gamma) = 0$ 이 되는 **필요충분조건**을 $\Sigma_B$, $\Delta$ 로 쓰라.
*전략과 핵심 부등식*: 목적함수가 $w$ 에 대해 강볼록($M \succ 0$)이므로 균등 수렴이 최소점의
수렴을 준다(argmin 의 연속성). 편향이 0 인 조건은 $\Sigma_B\Delta = 0$, 즉 **불일치가 B 의
특징 공간에서 보이지 않을 때**뿐이다($\gamma\beta > 0$ 인 한). 전개는 숨긴다.

**P3 (계산, ★, R1·R2)** $p = 40$, $\sigma^2 = 0.01$ 일 때 (ⓐ) $N = 200$ 과 $N = 3200$ 에서
(1)의 값, (ⓑ) $\mathrm{bias} = 0.01226$ 일 때 (7)의 $N^\dagger$, (ⓒ) 분산 항이 편향의 10%
가 되는 $N$ 을 구하라.
*정답*: (ⓐ) $0.01 + 0.4/159 = 0.012516$ 과 $0.01 + 0.4/3159 = 0.010127$ (허용오차 $10^{-6}$).
(ⓑ) $N^\dagger = 41 + 0.4/0.01226 = 73.6$ (허용오차 $0.1$). (ⓒ) $41 + 0.4/0.001226 = 367.3$
(허용오차 $0.5$).
검산: (ⓐ)의 두 값을 재현 과제의 $\beta=0$ 측정값 $0.012666$·$0.010162$ 와 비교해 비가
$1.0$ 근처(각각 $1.012$·$1.003$)인지 확인한다.

**P4 (구현, ★★, R1·R2·R3)** 재현 과제를 구현해 (ⓐ) 순수 도메인 곡선과 (1)의 일치,
(ⓑ) 혼합 바닥과 (3)의 일치, (ⓒ) $\gamma^\star$ 의 두 방향 의존을 확인하라.
*루브릭*: ⓐ $p < N_{\min}$ 으로 두어 이중 하강 영역을 피했다(피하지 않으면 (1)이 적용되지
않는다) ⓑ $\Sigma_A$·$\Sigma_B$ 를 큰 표본으로 추정해 (3)을 **닫힌 형태로** 계산했다
ⓒ 가중 최소제곱을 $\sqrt{\gamma}$ 스케일링으로 구현했다(손실에 $\gamma$, 설계행렬에
$\sqrt{\gamma}$) ⓓ 시드 20개 평균과 표준오차를 보고했다 ⓔ 로그-로그 기울기를 **바닥을 뺀
초과 손실**에 대해 재었다(생 손실에 재면 기울기가 $0$ 으로 꺾인다).

**P5 (반례, ★★, R1·R2)** 두 주장이 **모두** 틀림을 보이라: (i) "데이터를 더 모으면 항상
나아진다", (ii) "다른 도메인 데이터는 항상 해롭다". 각각의 반례를 재현 과제의 격자에서
지목하고, (iii) 로그-로그 바닥을 보고 "라벨 잡음이 $\sigma^2$ 다"라고 결론하는 것이 왜 틀릴 수
있는지 쓰라.
*성질 체크리스트*: (i) $\beta=0.5$ 에서 $N$ 을 16배 늘려도 22%만 개선(바닥이 지배)
(ii) 불일치 0.08·$N_A=60$ 에서 $\gamma^\star=0.4$ 가 $\gamma=0$ 보다 3.16배 좋다
(iii) 오지정이 있으면 바닥 $=\sigma^2 + $ 근사 오차이므로, 모형 용량 $p$ 를 키워 바닥이
내려가는지 봐야 두 성분을 구분할 수 있다. 그래서 스케일링 실험은 반드시 **용량도 함께** 쓸어야
한다.

**P6 (논문, ★★, R1·R4)** Kaplan et al. 2020(§1–3, §6)과 Open X-Embodiment(§3–5)를 읽고 각각
3문장 이내로 쓰라: (i) Kaplan 의 $L(N)$ 형태가 (1)과 어디까지 같고 어디서 다른가,
(ii) 그들이 보고하는 "되돌릴 수 없는 손실"이 이 레슨의 $\sigma^2$ 와 같은 것인가,
(iii) OXE 의 혼합 설계에서 (3)의 $\Delta$ 에 해당하는 양은 무엇이고 논문이 그것을 어떻게
다루는가.
*채점 루브릭*: (i) 둘 다 거듭제곱 + 바닥이지만 Kaplan 의 지수는 $\approx 0.095$ 로 1 과 크게
다르며, 그것이 유효 자유도가 $N$ 과 함께 증가하는 심층망의 성질임을 짚으면 통과.
(ii) 데이터 규모를 늘려도 내려가지 않는 성분이라는 공통점과, 그것이 라벨 잡음인지 오지정인지
논문이 구분하지 않는다는 점. (iii) 로봇·그리퍼·행동 좌표계·제어 주기의 불일치, 그리고 논문의
처방(행동 공간 정규화, 데이터셋 가중)을 짚으면 통과. "스케일링이 잘 된다"만 쓰면 미달.

**P7 (유도, ★★, R3)** 1차원($p=1$, $\Sigma_A=\Sigma_B=1$)으로 축소해 (8)을 명시적으로 풀고
$\gamma^\star$ 를 $\Delta$, $N_A$, $N_B$, $\sigma^2$ 의 식으로 쓰라. $\Delta\to0$ 과
$N_A\to\infty$ 의 극한에서 각각 무엇이 되는가?
*해답 스케치*: 1차원에서 $\mathrm{bias} = (\gamma\beta\Delta/((1-\beta)+\gamma\beta))^2$ 이고
분산은 $\sigma^2/(N_A+\gamma N_B)$ 다. 미분해 정리하면 $\gamma^\star$ 가 $\Delta^{-2}$ 에
비례하는 항을 갖는다. $\Delta\to0$ 에서 $\gamma^\star\to\infty$(즉 제한 없이 섞어도 좋다),
$N_A\to\infty$ 에서 $\gamma^\star\to0$(목표 데이터만으로 충분하다).

## 논문 읽기

**필독 2편.** 각 논문에 고정 질문 10개로 1페이지 노트를 쓴다(`lesson-standard.md` §5).
3-pass 로 읽고, 3번째 패스에서 질문 4·5·6·7 을 집중 공략한다.

1. **Kaplan, McCandlish, Henighan et al., "Scaling laws for neural language models" (2020, arXiv)**
   — 역할: `원전(seminal)`. <https://arxiv.org/abs/2001.08361> — §1–3 과 §6.
   읽는 이유: 거듭제곱 + 바닥이라는 **형태**를 처음 체계적으로 보고한 글이고, 이 레슨의 (1)이
   그 형태가 어디서 오는지를 축소 모형에서 설명한다.
   추가 질문: ⓐ 저자들이 $N$(매개변수)·$D$(데이터)·$C$(계산)를 각각 쓸 때 다른 지수를 얻는데,
   (1)의 틀에서 "지수가 다르다"는 것은 무엇이 다르다는 뜻인가? ⓑ §6 의 외삽 주장은 무엇을
   보장하고 무엇은 보장하지 않는가?
2. **Open X-Embodiment Collaboration, "Open X-Embodiment: robotic learning datasets and RT-X
   models" (2023, arXiv/ICRA 2024)** — 역할: `최신(frontier)`.
   <https://arxiv.org/abs/2310.08864> — §3–5.
   읽는 이유: (3)의 $\Delta$ 가 로봇 데이터에서 구체적으로 무엇인지, 그리고 혼합 가중을 실제로
   어떻게 정하는지 보는 사례다.
   추가 질문: ⓐ 데이터셋 가중을 정한 절차가 논문에 있는가, 없으면 무엇으로 대체했는가?
   ⓑ 긍정 전이(positive transfer)를 보고한 조합과 보고하지 않은 조합의 차이는 (4)의 두 방향으로
   설명되는가?

**고정 질문 10개**: (1) 어떤 문제를 어떤 가정 아래 푸는가 (2) 이전 연구가 못 한 것은 정확히 무엇인가
(3) 핵심 아이디어를 수식 한 줄로 (4) 이론적 보장은 무엇이고 **무엇은 보장하지 않는가**
(5) 실험의 독립·종속변수와 베이스라인, 공정하게 튜닝되었는가 (6) 지표가 주장과 맞는가, 분산·시드를
보고하는가 (7) 재현에 필요한 정보 중 빠진 것 (8) 틀렸다면 가장 먼저 의심할 가정
(9) 계산·메모리 복잡도와 실시간성 (10) 1년 뒤 넘어서려면 무엇을 바꾸겠는가.

## 재현 과제

**티어 R2 (알고리즘 재구현).** 계산 예산: 노트북 CPU **2분 이내**, 메모리 500 MB 이내,
numpy 만. **GPU 가 필요 없다** — 동결 표현 위 선형 헤드라는 축소 모형을 쓰기 때문이다.
실제 로봇 데이터로의 확장은 아래 **선택 확장(R4)** 이다.

**생성 스크립트.** 입력 $8$ 차원, 랜덤 ReLU 특징 $p = 40$ (고정·동결), 라벨 잡음
$\sigma = 0.1$. 도메인 B 는 입력 평균이 $1.5$ 만큼 이동하고 계수가 $w_B = w_A + d\cdot\lVert w_A\rVert v$
($v$ 는 단위 벡터, $d$ 는 불일치 크기)다.

```python
import numpy as np

D_IN, P, SIGMA = 8, 40, 0.1


def make_world(seed=0, shift=1.5, disagree=0.6):
    rng = np.random.default_rng(seed)
    W = rng.standard_normal((D_IN, P)) / np.sqrt(D_IN)
    b = rng.standard_normal(P) * 0.1
    wA = rng.standard_normal(P) / np.sqrt(P)
    v = rng.standard_normal(P)
    v /= np.linalg.norm(v)
    muB = np.zeros(D_IN)
    muB[0] = shift
    return dict(W=W, b=b, wA=wA, wB=wA + disagree * np.linalg.norm(wA) * v, muB=muB)


def sample(w, n, domain, rng):
    X = rng.standard_normal((n, D_IN)) + (w["muB"] if domain == "B" else 0.0)
    F = np.maximum(X @ w["W"] + w["b"], 0.0)
    tgt = w["wA"] if domain == "A" else w["wB"]
    return F, F @ tgt + SIGMA * rng.standard_normal(n)
```

가중 최소제곱은 설계행렬에 $\sqrt{\gamma}$ 를 곱해 구현한다(손실의 $\gamma$ 가중과 동등).
시험 위험은 도메인 A 에서 40,000 표본으로 추정한다.

**수용 기준** — 네 조건을 모두 만족해야 통과다.

1. **(1)과의 일치**: $\beta=0$, $N \in \{120, 200, 400, 800\}$ 에서 시드 20개 평균 초과 손실
   $L_A - \sigma^2$ 를 $\sigma^2 p/(N-p-1)$ 로 나눈 비가 **모두 $[0.95,\,1.25]$** 에 들어온다
   (측정값 $1.165$, $1.019$, $1.101$, $1.057$). $N = 60$ 과 $N = 3200$ 은 각각 점근 영역 밖과
   추정 잡음 지배라 제외하고, 그 **제외 이유를 보고한다**(측정 비 $1.363$·$1.358$).
2. **거듭제곱 기울기**: 같은 구간에서 $\log(L_A-\sigma^2)$ 대 $\log N$ 의 회귀 기울기가
   $-1 \pm 0.15$ 다. **생 손실 $\log L_A$ 로 재면 기울기가 $0$ 쪽으로 꺾이는 것**을 함께 보고해
   바닥을 빼야 하는 이유를 보인다.
3. **혼합 편향 바닥 (3)과의 일치**: $N = 25600$, $\gamma=1$, $\beta \in \{0.25, 0.5, 0.75\}$ 에서
   측정 초과 손실 $L_A - \sigma^2$ 를 (3)의 닫힌 형태로 나눈 비가 **$[0.95,\,1.20]$** 다
   (측정값 $1.048$, $1.024$, $1.017$). $\Sigma_A,\Sigma_B$ 는 400,000 표본으로 추정한다.
   동시에 $\beta=0.5$ 에서 $N$ 을 $200 \to 3200$ (16배)으로 늘려도 손실이
   $0.0291 \to 0.0228$ 로 **22% 만** 줄고 바닥 $0.0223$ 에 붙는 것을 보고한다 — 붕괴 조건의 실측.
4. **$\gamma^\star$ 의 두 방향**: $N_B = 1200$ 고정, $\gamma \in \{0, 0.05, 0.15, 0.4, 1.0\}$ 격자에서
   ⓐ 불일치 $0.6$·$N_A=400$ 은 $\gamma^\star = 0$,
   ⓑ 불일치 $0.08$·$N_A=60$ 은 $\gamma^\star = 0.4$ 이고 $\gamma=0$ 대비 **$3.16$배** 좋다,
   ⓒ 불일치를 $0.6 \to 0.08$ 로 줄이거나 $N_A$ 를 $400 \to 60$ 으로 줄이면 $\gamma^\star$ 가
   **증가한다**((4)의 두 방향). 시드 20개 평균으로 판정한다.

**비교 대상(베이스라인)**: ⓐ $\gamma=0$ (목표 데이터만) — 혼합이 이득인지의 기준점.
ⓑ $\gamma=1$ (그냥 합치기) — 실무의 기본값. ⓒ (1)·(3)의 닫힌 형태 — 조건 1·3 이 그 비교다.
ⓓ 선택: $p$ 를 $\{10, 20, 40, 80\}$ 로 쓸어 바닥이 $\sigma^2$ 에서 움직이지 않는지 확인한다
(움직이면 오지정이 있다는 뜻이고, 문제 P5 의 (iii)이 그 진단이다).

**선택 확장 (R4, GPU 필요 가능 — 필수 아님)**: Open X-Embodiment 의 하위집합 2–3개를 받아
동결 시각 표현 위에 같은 선형 헤드를 학습하고, 데이터셋 가중 $\gamma$ 를 쓸어 조건 4 와 같은
모양의 곡선이 나오는지 본다. **수용 기준은 두지 않는다** — 공개 체크포인트·전처리 차이로
수치가 재현되지 않을 수 있다. 목적은 축소 모형의 결론이 실제 혼합에서 **정성적으로** 보이는지
확인하는 것이다.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 조건 1 의 비가 $N$ 이 작을 때 2 를 넘는다 | $N$ 이 $p+1$ 에 가까워 이중 하강 영역이다 | $N/p$ 를 출력한다 — 조건 1 의 구간은 $N/p \ge 3$ 이다 |
| 조건 2 의 기울기가 $-0.2$ 근처 | 바닥을 빼지 않고 생 손실에 회귀했다 | $L_A$ 와 $L_A-\sigma^2$ 두 곡선을 함께 그린다 |
| 조건 3 의 비가 $1.5$ 를 넘는다 | $\Sigma_A,\Sigma_B$ 추정 표본이 적어 (3)이 부정확하다 | 추정 표본을 $4\times10^5$ 로 올리고 비의 변화를 본다 |
| 조건 3 에서 바닥이 $N$ 과 함께 계속 내려간다 | 가중을 도메인별 상수가 아니라 표본별로 줬다(암묵적 중요도 가중) | 가중 벡터의 유일값 개수를 출력한다 — 2 여야 한다 |
| 조건 4 에서 $\gamma^\star$ 가 항상 0 | 불일치 $d$ 가 커서 네 조합이 모두 같은 영역에 있다 | $\lVert\Sigma_B\Delta\rVert_{\Sigma_A}$ 를 출력해 두 $d$ 가 실제로 다른지 확인한다 |
| 시드마다 $\gamma^\star$ 가 바뀐다 | 시드 수가 적고 격자가 거칠다 | 20 시드 평균을 쓰고 $\gamma$ 격자를 로그 간격으로 촘촘히 한다 |

## 열린 문제

- **(열린 문제) 심층망에서 지수가 왜 1 이 아닌가** — (1)의 지수는 정확히 $1$ 인데 실측 심층망은
  $0.05$–$0.3$ 규모다. 유효 자유도가 $N$ 과 함께 자라기 때문이라는 설명이 있으나, 주어진
  구조·데이터에서 지수를 **예측**하는 이론은 없다. 로봇 데이터에서는 지수가 과제별로 크게 달라
  외삽이 특히 위험하다. 현재 접근:
  [Kaplan et al. 2020](https://arxiv.org/abs/2001.08361),
  [Hestness et al. 2017](https://arxiv.org/abs/1712.00409),
  [Hoffmann et al. 2022](https://arxiv.org/abs/2203.15556). 비어 있는 자리: 지수를 구조에서
  예측하는 규칙.
- **(열린 문제) 혼합 가중을 데이터로 정하는 절차** — (8)은 $\Delta$ 와 $\Sigma_B$ 를 알아야
  $\gamma^\star$ 를 준다. 도메인이 수십 개면 $\gamma$ 가 벡터이고, 목표 도메인의 검증 데이터가
  적을 때(로봇에서 흔하다) 그 추정이 과적합된다. 현재 접근: OXE 의 수동 가중
  ([OXE 2023](https://arxiv.org/abs/2310.08864)), 계산 최적 배분
  ([Hoffmann et al. 2022](https://arxiv.org/abs/2203.15556)). 비어 있는 자리: 목표 데이터가
  희소할 때의 가중 선택 규칙.
- **(열린 문제) 바닥의 성분 분해** — 실측 바닥은 라벨 잡음·시연 다봉성·오지정·행동 공간
  양자화의 합이다. 각 성분을 데이터에서 분리하는 절차가 없어, "바닥에 닿았다"가 "데이터를 더
  모아도 소용없다"를 뜻하는지 "모형을 바꿔야 한다"를 뜻하는지 구분할 수 없다. 다봉성 쪽은
  `s4-vla-architectures` 의 양자화 오차와, 평가 쪽은 `s4-evaluation-science` 와 이어진다.
  비어 있는 자리: 바닥의 성분을 식별하는 실험 설계.
- **(열린 문제) 음의 전이를 사전에 예측하기** — (3)은 전이가 해로운 **조건**을 주지만
  $\Sigma_B\Delta$ 를 모르는 상태에서 데이터셋을 받았을 때 그것을 추정할 방법이 없다.
  시뮬레이션 평가와 실기의 상관이 약한 것도 같은 문제다(`s4-evaluation-science`,
  [Li et al. 2024](https://arxiv.org/abs/2405.05941)). 비어 있는 자리: 학습 전에 음의 전이를
  탐지하는 저비용 지표.

## 개념 점검

`rc quiz s4-robot-data-scaling` 로 푼다. 이 퀴즈는 **개념 점검 전용**이고, 실제 과제는 위
문제 세트와 재현 과제다(`lesson-standard.md` §4).

```quiz
activity: s4-robot-data-scaling-quiz
questions:
  - id: q1
    type: single
    prompt: "스케일링 법칙 (1)에서 로그-로그 곡선이 큰 $N$ 에서 평평해지는 것은 무엇을 보는 것인가?"
    choices:
      - "모형 용량이 포화한 것"
      - "라벨 잡음 등 되돌릴 수 없는 바닥 $\\sigma^2$ 의 존재"
      - "최적화가 수렴하지 못한 것"
      - "표본이 서로 상관된 것"
    answer: 1
    explanation: "(1)은 $\\sigma^2 + \\sigma^2 p/(N-p-1)$ 이므로 둘째 항이 $N^{-1}$ 로 사라지면 $\\sigma^2$ 만 남는다. 꺾임의 **높이**가 바닥이고 꺾임 **전의 기울기**가 유효 자유도를 읽는 자리다. 다만 오지정이 있으면 바닥에 근사 오차가 섞이므로 $\\sigma^2$ 로 단정할 수 없다."
    concept: { front: "로그-로그 꺾임의 의미", back: "바닥 $L_\\infty$ 의 존재 — 높이는 잡음(+오지정), 꺾임 전 기울기는 유효 자유도" }
  - id: q2
    type: truefalse
    prompt: "서로 어긋나는 도메인을 섞어 생긴 손실 증가는 표본 수를 충분히 늘리면 사라진다."
    answer: false
    explanation: "가중 정규방정식 (5)의 해 (2)에는 $N$ 이 들어 있지 않다. 추정량은 $w_A$ 가 아니라 $w_A + \\gamma\\beta M^{-1}\\Sigma_B\\Delta$ 로 수렴하므로 초과 손실 (3)이 **바닥으로 남는다**. 실측에서 $\\beta=0.5$ 로 $N$ 을 16배 늘려도 22%만 줄고 바닥에 붙었다."
    concept: { front: "혼합 편향 바닥", back: "(2)에 $N$ 이 없다 — 데이터 양으로는 지워지지 않고 가중·분포로만 지워진다" }
  - id: q3
    type: single
    prompt: "도메인 가중 $\\gamma^\\star$ 가 **작아지는** 상황은?"
    choices:
      - "목표 도메인 데이터가 적어질 때"
      - "도메인 불일치 $\\lVert\\Delta\\rVert$ 가 커질 때"
      - "off-도메인 표본 수 $N_B$ 가 늘어날 때"
      - "라벨 잡음 $\\sigma^2$ 이 커질 때"
    answer: 1
    explanation: "(8)에서 좌변(편향 쪽)이 $\\lVert\\Sigma_B\\Delta\\rVert^2$ 에 비례하므로 불일치가 커지면 $\\gamma^\\star$ 가 작아진다. 목표 데이터가 적어지거나 잡음이 커지면 분산 항이 커져 $\\gamma^\\star$ 는 **커진다**. 실측: 불일치 0.08·$N_A=60$ 에서 $\\gamma^\\star=0.4$(3.16배 이득), 불일치 0.6·$N_A=400$ 에서 $\\gamma^\\star=0$."
    concept: { front: "$\\gamma^\\star$ 의 의존성", back: "불일치 ↑ → $\\gamma^\\star$ ↓; 목표 데이터 ↑ → $\\gamma^\\star$ ↓; 잡음 ↑ → $\\gamma^\\star$ ↑" }
  - id: q4
    type: short
    prompt: "혼합 편향이 정확히 0 이 되는 조건을 $\\Sigma_B$ 와 $\\Delta$ 로 쓰면? (등식으로)"
    answer: ["Sigma_B Delta = 0", "Sigma_B * Delta = 0", "\\Sigma_B \\Delta = 0", "SigmaB Delta = 0", "Sigma_B·Delta=0"]
    explanation: "(3)의 편향은 $(\\gamma\\beta M^{-1}\\Sigma_B\\Delta)^\\top \\Sigma_A (\\cdot)$ 이고 $\\Sigma_A \\succ 0$, $M \\succ 0$ 이므로 $\\gamma\\beta>0$ 인 한 $\\Sigma_B\\Delta = 0$ 일 때만 0 이다. 즉 **불일치가 B 의 특징 공간에서 보이지 않을 때**만 공짜로 섞을 수 있다 — 단순히 $\\Delta$ 가 작은 것과는 다른 조건이다."
    concept: { front: "공짜로 섞을 수 있는 조건", back: "$\\Sigma_B\\Delta = 0$ — 불일치가 그 도메인의 특징 공간에서 보이지 않을 때" }
  - id: q5
    type: truefalse
    prompt: "로그-로그 도표에서 측정한 바닥의 높이는 라벨 잡음 $\\sigma^2$ 과 같다."
    answer: false
    explanation: "모형이 오지정되어 있으면 바닥 $=\\sigma^2 + $ 근사 오차다. 두 성분은 $N$ 으로 구분되지 않으므로, 모형 용량 $p$ 를 쓸어 바닥이 움직이는지 봐야 한다(움직이면 오지정이 섞여 있다). 그래서 스케일링 실험은 데이터 양만이 아니라 **용량도 함께** 쓸어야 한다."
    concept: { front: "바닥의 성분", back: "라벨 잡음 + 오지정(+다봉성·양자화) — 용량을 쓸어야 분리된다" }
```

## 이 단계 공부법

1. **(1)을 백지에서 유도한다 (60분)** — 초과 위험을 $\sigma^2$ 와 2차형식으로 분리하는 1단계가
   전부다. 그 분리를 쓸 수 있으면 "바닥"과 "기울기"가 다른 양이라는 것이 자동으로 보인다.
   역 Wishart 평균은 외워 쓰고, 왜 $N>p+1$ 이 필요한지만 확인한다.
2. **바닥과 기울기를 숫자로 분리한다 (45분)** — 문제 P3 을 풀고, 재현 과제 조건 1·2 를 돌려
   **생 손실에 회귀하면 기울기가 꺾이는 것**을 직접 본다. 이 한 번의 실수를 해 보면 논문의
   스케일링 도표를 읽는 눈이 달라진다.
3. **혼합 극한을 손으로 푼다 (60분)** — (5)에서 (2)로 가는 두 줄을 백지에서 쓴다. "$N$ 이
   어디에도 없다"를 스스로 확인하는 것이 이 레슨의 전환점이다. 그 다음 P2 로 편향이 0 이 되는
   조건이 $\Delta = 0$ 이 아니라 $\Sigma_B\Delta = 0$ 임을 확인한다.
4. **격자를 직접 돌린다 (125분)** — 재현 과제 조건 3·4 를 돌려 붕괴 조건과 $\gamma^\star$ 의
   두 방향을 본다. 특히 불일치가 작고 목표 데이터가 적을 때 **3.16배 이득**이 나는 칸과
   불일치가 크고 목표 데이터가 넉넉할 때 $\gamma^\star=0$ 인 칸을 나란히 본다. 이 표를 만들어
   본 사람은 "데이터가 많을수록 좋다"를 조건부로만 말하게 된다.
5. **논문 2편을 축소 모형과 대조해 읽는다 (110분)** — Kaplan et al. 의 지수가 1 이 아닌 이유를
   (1)의 틀에서 설명해 보고, OXE 의 가중 결정 절차를 (8)과 비교한다. 논문당 1페이지 노트는
   **반드시** 쓴다.
6. **무엇을 못 하는지로 끝낸다 (80분)** — "열린 문제" 중 바닥의 성분 분해를 골라, 재현 과제의
   베이스라인 ⓓ($p$ 쓸기)를 어떻게 확장하면 잡음과 오지정을 분리할 수 있을지 한 문단으로 쓴다.

**통과 기준**: 백지에서 (1)과 (2)를 유도할 수 있고, 바닥과 기울기가 각각 무엇에서 오는지 말할
수 있고, 붕괴 조건 (7)을 계산할 수 있고, $\gamma^\star$ 의 두 방향을 수치로 댈 수 있고,
재현 과제의 네 조건을 만족하는 코드와 논문 2편의 노트를 갖고 있다.
