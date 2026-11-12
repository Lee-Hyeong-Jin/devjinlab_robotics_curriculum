---
id: r0-estimation-theory
title: 확률과 추정 이론
summary: >-
  선형 가우시안 모델에서 MAP 추정이 가중 최소제곱과 같음을 유도하고, Cramér–Rao 하한을 증명하며,
  일관성·효율성과 Fisher 정보의 관계를 정리한다.
objectives:
  - 선형 가우시안 모델의 MAP 추정이 가중 최소제곱임을 유도할 수 있다.
  - Fisher 정보를 정의하고 선형 가우시안에서 그것이 정보행렬과 같음을 보일 수 있다.
  - Cramér–Rao 하한을 증명하고 그 가정(불편성, 정칙성)을 말할 수 있다.
  - 일관성·효율성·점근 정규성을 구분하고 추정기를 그 기준으로 평가할 수 있다.
  - 공분산을 보고하는 추정기가 과확신(overconfident)인지 NEES 로 판정할 수 있다.
prerequisites: [r0-numerical-optimization]
difficulty: 4
estimated_minutes: 450
tags: [estimation, probability, cramer-rao, fisher-information, research]
activities:
  - id: r0-estimation-theory-reading
    kind: reading
    title: 본문 읽기와 유도 따라가기
    estimated_minutes: 85
  - id: r0-estimation-theory-textbook
    kind: reading
    title: 교재 읽기 (Barfoot ch.2-3, Thrun ch.2-3) + 1페이지 노트
    estimated_minutes: 110
  - id: r0-estimation-theory-problems
    kind: exercise
    title: 문제 세트 (유도 2 · 증명 1 · 계산 1 · 구현 1 · 반례 1)
    estimated_minutes: 140
  - id: r0-estimation-theory-reproduction
    kind: reproduction
    title: 재현 과제 — 몬테카를로로 CRLB 와 NEES 검증 (R1)
    estimated_minutes: 100
  - id: r0-estimation-theory-quiz
    kind: quiz
    title: 개념 점검 퀴즈
    estimated_minutes: 15
resources:
  - title: "Barfoot, State Estimation for Robotics (2nd ed., 2024)"
    url: https://asrl.utias.utoronto.ca/~tdb/bib/barfoot_ser24.pdf
    kind: book
    note: ch.2 (확률 입문), ch.3 (선형-가우시안 추정). 1순위, 무료 전문 PDF.
  - title: "Thrun, Burgard & Fox, Probabilistic Robotics"
    kind: book
    note: ch.2-3 (재귀 상태 추정, 가우시안 필터). 로보틱스 맥락의 표준. (공식 URL 미확인)
  - title: "NumPy random 문서"
    url: https://numpy.org/doc/stable/reference/random/index.html
    kind: notes
    note: 몬테카를로로 CRLB·NEES 를 검증하는 데 쓴다.
---

# 확률과 추정 이론

## 전제와 기호

| 기호 | 뜻 |
|---|---|
| $x \in \mathbb{R}^n$ | 추정할 상태(또는 매개변수) |
| $z = Hx + w$, $w \sim \mathcal{N}(0,R)$ | 선형 가우시안 관측 모델 |
| $\hat{x}$ | 추정값, $\Sigma = \mathrm{Cov}(\hat{x})$ |
| $\Lambda = H^\top R^{-1}H$ | 정보행렬 |
| $\mathcal{I}(x)$ | Fisher 정보 행렬 |
| $\mathrm{NEES}$ | 정규화 추정오차 제곱, $e^\top\Sigma^{-1}e$ |

전제: `f0-probability-statistics`(베이즈, 가우시안 세 성질), `r0-numerical-optimization`(최소제곱 해법).

## 핵심 결과

- **R1 (MAP = 가중 최소제곱) [D2]** — 사전 $x \sim \mathcal{N}(\mu_0, \Sigma_0)$, 관측
  $z = Hx+w$, $w\sim\mathcal{N}(0,R)$ 일 때 MAP 추정은

$$
\hat{x} = \arg\min_x \tfrac12\lVert z - Hx\rVert^2_{R^{-1}} + \tfrac12\lVert x-\mu_0\rVert^2_{\Sigma_0^{-1}}, \tag{1}
$$

  즉 **가중 최소제곱**이고, 해는 $(\Sigma_0^{-1} + H^\top R^{-1}H)\hat{x} =
  \Sigma_0^{-1}\mu_0 + H^\top R^{-1}z$ 다.
- **R2 (사후 공분산 = 정보행렬의 역) [D2]** — 위 모델에서 사후 분포는 가우시안이고

$$
\Sigma_{\text{post}} = \big(\Sigma_0^{-1} + H^\top R^{-1}H\big)^{-1} . \tag{2}
$$

  **관측이 정보를 더한다**(역공분산이 더해진다)는 것이 이 식의 읽는 법이다.
- **R3 (Fisher 정보와 CRLB) [D3]** — 정칙 조건 아래, **불편 추정기** $\hat{x}$ 의 공분산은

$$
\mathrm{Cov}(\hat{x}) \succeq \mathcal{I}(x)^{-1}, \qquad
\mathcal{I}(x) = \mathbb{E}\big[\nabla_x\log p(z|x)\,\nabla_x\log p(z|x)^\top\big] . \tag{3}
$$

  선형 가우시안에서는 $\mathcal{I} = H^\top R^{-1}H = \Lambda$ 이고 MLE 가 하한을 **달성**한다.
- **R4 (일관성·효율성·점근 정규성) [D2]** — 세 개념은 다르다:
  **일관성**(표본이 늘면 참값으로 수렴), **효율성**(CRLB 달성), **점근 정규성**(오차 분포가
  가우시안으로 수렴). MLE 는 정칙 조건에서 일관·점근 정규·점근 효율이지만 **유한 표본에서는
  편향될 수 있다**.
- **R5 (NEES 로 과확신 판정) [D2]** — 추정기가 보고한 $\Sigma$ 가 옳다면
  $\mathrm{NEES} = e^\top\Sigma^{-1}e \sim \chi^2_n$ 이므로 $\mathbb{E}[\mathrm{NEES}] = n$ 이다.
  **$\mathrm{NEES} \gg n$ 이면 과확신**(공분산을 너무 작게 보고), $\ll n$ 이면 과보수적이다.

## 유도

### R1 — MAP 이 가중 최소제곱이 되는 이유

베이즈 정리에서 $p(x|z) \propto p(z|x)p(x)$ 이고, 가우시안의 밀도는 지수 안에 이차형식을 갖는다:

$$
-\log p(x|z) = \tfrac12(z-Hx)^\top R^{-1}(z-Hx) + \tfrac12(x-\mu_0)^\top\Sigma_0^{-1}(x-\mu_0) + \text{const} .
$$

$\log$ 를 취하면 **지수의 이차형식이 그대로 비용함수가 된다** — 이것이 (1)이다. 최대화가
최소화로 바뀌는 것은 부호 때문이고, 상수항은 $x$ 에 무관하므로 버린다.

$x$ 로 미분해 0 으로 두면

$$
-H^\top R^{-1}(z-Hx) + \Sigma_0^{-1}(x-\mu_0) = 0
\;\Longrightarrow\; (\Sigma_0^{-1}+H^\top R^{-1}H)x = \Sigma_0^{-1}\mu_0 + H^\top R^{-1}z .
$$

**읽는 법 세 가지**: ⓐ 가중치는 **역공분산**이다 — 불확실한 관측은 가볍게 들어간다 ⓑ 사전은
"관측 하나 더"와 같은 자격으로 들어간다 ⓒ 좌변의 행렬이 바로 사후 정보행렬이므로 (2)가 따라온다.
C5 의 인자 그래프 전체가 (1)의 항이 많아진 형태다.

**가정이 깨지는 곳**: 비선형 관측 $z = h(x)+w$ 에서는 $-\log p$ 가 이차형식이 아니므로 (1)이
정확하지 않다. 선형화하면 가중 최소제곱이 되지만, 그때 **야코비안이 현재 추정에 의존**하므로
반복해야 한다 — `c1-manifold-optimization` 의 Gauss–Newton 이 그 반복이다.

### R5 — NEES 와 그 분포

$\hat{x}$ 의 오차 $e = \hat{x}-x$ 가 $\mathcal{N}(0,\Sigma)$ 이고 보고된 공분산이 참값과 같으면,
$\Sigma^{-1/2}e \sim \mathcal{N}(0,I_n)$ 이므로

$$
\mathrm{NEES} = e^\top\Sigma^{-1}e = \lVert\Sigma^{-1/2}e\rVert^2 \sim \chi^2_n ,
$$

따라서 $\mathbb{E}[\mathrm{NEES}] = n$, $\mathrm{Var} = 2n$ 이다. $M$ 회 몬테카를로 평균을 쓰면
$\overline{\mathrm{NEES}}$ 의 95% 구간이 $\chi^2_{nM}/M$ 분위수로 주어지고, 그 구간을 벗어나면
**공분산 보고가 틀렸다**고 판정한다.

**왜 중요한가**: 추정기를 "오차가 작다"로만 평가하면 과확신을 못 잡는다. 과확신은 융합에서
치명적이다 — 틀린 정보를 과도하게 신뢰해 다른 관측을 눌러 버린다. C5 의 EKF 비일관성 논의와
S1 의 평가 절차가 이 지표를 쓴다.

## 증명 스케치

### R3 — Cramér–Rao 하한

**가설** H1: $p(z|x)$ 가 $x$ 에 대해 미분가능하고 적분과 미분을 교환할 수 있다(정칙 조건).
H2: $\hat{x}(z)$ 는 **불편**($\mathbb{E}[\hat{x}] = x$). **결론** C: (3).

**전략**: 점수 함수(score)와 추정오차의 공분산에 Cauchy–Schwarz 를 적용한다.

1. 점수 함수 $s(z,x) := \nabla_x\log p(z|x)$ 는 평균 0 이다:
   $\mathbb{E}[s] = \int \nabla_x p\,dz = \nabla_x\int p\,dz = \nabla_x 1 = 0$
   (H1 이 여기서 쓰인다 — 적분과 미분의 교환).
2. 불편성을 미분한다: $\nabla_x\mathbb{E}[\hat{x}] = I$ 이고 좌변을 전개하면
   $\int \hat{x}\,\nabla_x p\,dz = \int \hat{x}\,s\,p\,dz = \mathbb{E}[\hat{x}s^\top] = I$.
   1 에서 $\mathbb{E}[s]=0$ 이므로 $\mathrm{Cov}(\hat{x}, s) = \mathbb{E}[(\hat{x}-x)s^\top] = I$.
3. 결합 공분산 행렬
   $\begin{bmatrix}\mathrm{Cov}(\hat{x}) & I\\ I & \mathcal{I}\end{bmatrix} \succeq 0$
   (임의의 두 확률벡터의 결합 공분산은 양반정).
4. Schur 보완 조건(`r0-sparse-linear-algebra` R3)에서 $\mathcal{I} \succ 0$ 이면
   $\mathrm{Cov}(\hat{x}) - I\mathcal{I}^{-1}I \succeq 0$, 즉 C.
5. **등호 조건**: $\hat{x}-x$ 와 $s$ 가 선형 종속일 때, 즉 $\hat{x}-x = \mathcal{I}^{-1}s$ 일 때
   달성된다. 선형 가우시안에서 MLE 가 정확히 이 형태다.

**가설을 지우면**: H2(불편성)를 빼면 **편향 추정기가 CRLB 보다 작은 분산을 가질 수 있다**
(극단적으로 $\hat{x} \equiv 0$ 은 분산 0). 그래서 CRLB 를 "달성 불가능한 벽"으로 오해하면 안
된다 — 불편 추정기들 사이의 한계다. 정칙 조건(H1)이 깨지는 예로는 지지(support)가 $x$ 에
의존하는 분포(균등분포의 경계 추정)가 있다.

**실무적 함의**: 로보틱스에서 CRLB 는 **센서 배치와 궤적 설계의 상한 평가**에 쓰인다
(`s5-active-information-gathering` 의 정보 수집 계획). 또 $\mathcal{I} = \Lambda$ 이므로
"정보행렬의 역이 달성 가능한 최소 공분산"이라는 해석이 C5 전체에서 쓰인다.

## 문제 세트

★ 15분 / ★★ 1시간 / ★★★ 하루 이상.

**P1 (유도, ★★, R1·R2)** 사전이 없는 경우($\Sigma_0^{-1} \to 0$) (1)의 해가 일반 최소제곱으로
환원되는 것을 보이고, 그때 사후 공분산이 $(H^\top R^{-1}H)^{-1}$ 임을 확인하라. $H$ 가 랭크
결핍이면 무슨 일이 생기는가?
*해답 스케치*: 사전이 사라지면 정보행렬이 $H^\top R^{-1}H$ 뿐이고, 랭크 결핍이면 역이 없다 —
**관측만으로 결정되지 않는 방향**이 남는다. 그 방향이 `c1-manifold-optimization` 의 게이지다.

**P2 (유도, ★★, R3)** 선형 가우시안에서 $\mathcal{I} = H^\top R^{-1}H$ 임을 직접 계산하라.
*해답 스케치*: $\log p(z|x) = -\tfrac12(z-Hx)^\top R^{-1}(z-Hx)+c$ 이므로
$s = H^\top R^{-1}(z-Hx)$ 이고, $\mathbb{E}[ss^\top] = H^\top R^{-1}\mathbb{E}[ww^\top]R^{-1}H
= H^\top R^{-1}H$.

**P3 (증명, ★★★, R3)** CRLB 의 증명을 빈틈 없이 쓰고, 2단계에서 적분과 미분의 교환이 왜 필요한지
명시하라. 그 교환이 성립하지 않는 분포의 예를 들라.
*해답 스케치*: 지지가 $x$ 에 의존하면(예: $\mathrm{Unif}(0,x)$) 미분이 적분 경계를 움직여
교환이 깨진다. 그런 경우 CRLB 가 성립하지 않고, 실제로 더 작은 분산의 불편 추정기가 존재한다.

**P4 (계산, ★, R2·R5)** $H = [1]$ (스칼라), $R = 4$, 관측 $N$ 개를 독립적으로 얻을 때
ⓐ 사후 공분산 ⓑ CRLB ⓒ $N=100$ 에서 NEES 의 기대값을 구하라.
*정답*: ⓐ $(N/4)^{-1} = 4/N$ ⓑ 같다($4/N$) — MLE 가 효율적이다 ⓒ $n=1$ 이므로
$\mathbb{E}[\mathrm{NEES}]=1$ (표본 수와 무관). 허용오차 $10^{-9}$.

**P5 (구현, ★★, R3·R5)** 선형 가우시안 모델에서 ⓐ MLE 의 표본 공분산을 $M=10^4$ 회
몬테카를로로 추정해 CRLB 와 비교하고 ⓑ NEES 의 평균과 $\chi^2_n$ 95% 구간을 비교하라.
*루브릭*: ⓐ 상대오차 5% 이내로 CRLB 를 달성함을 보인다 ⓑ NEES 평균이 구간 안에 있다
ⓒ **일부러 $R$ 을 2배 작게 보고**하는 추정기를 만들어 NEES 가 구간 위로 나가는 것을 보인다
ⓓ 표본 수를 바꿔 가며 공분산이 $1/N$ 로 줄어드는 것을 확인한다.

**P6 (반례, ★★, R3·R4)** CRLB 보다 **작은** 분산을 갖는 추정기를 만들어라(힌트: 편향을 허용한다).
그리고 그 추정기가 일관성이 있는지 판정하라. "CRLB 를 깼다"는 주장이 왜 위반이 아닌지 설명하라.
*성질 체크리스트*: $\hat{x} = \alpha\bar{z}$ ($0<\alpha<1$)는 분산이 작지만 편향이 있다.
$\alpha \to 1$ 이 아니면 일관성도 없다. CRLB 의 가정이 **불편성**이므로 위반이 아니다.

## 논문 읽기

**교재 예외 적용**(레슨 표준 §5). 아래를 읽고 1페이지 노트 2편을 쓴다(고정 질문 1·3·4·8).

1. **Barfoot, *State Estimation for Robotics*, ch.2–3** — 질문: ⓐ 저자가 MAP 와 최대가능도(MLE)를
   구분하는 방식을 쓰라(사전이 있을 때와 없을 때). ⓑ 저자가 "모든 것이 가우시안이면 추정이 선형
   대수로 환원된다"고 말하는 지점을 찾아 그 조건을 정리하라.
2. **Thrun, Burgard & Fox, *Probabilistic Robotics*, ch.2–3** — 질문: ⓐ 재귀 베이즈 필터의
   유도에서 쓰이는 두 가정(Markov, 관측 독립)을 명시하고 언제 깨지는지 쓰라. ⓑ 이 책이 공분산의
   **일관성**을 다루는가? 다루지 않으면 그것이 왜 문제인지 쓰라.

**보조 문헌 1편**(방법론): NEES 와 공분산 일관성 평가 절차 — `s1-slam-benchmarking` 의 평가
도구와 연결해 읽는다.

## 재현 과제

**티어 R1 (수치 검증).** 예산: 노트북 CPU 1분 이내, numpy 만. 네 조건을 모두 만족해야 한다.

1. **CRLB 달성**: 선형 가우시안 모델($n=3$, 관측 $m=10$)에서 MLE 를 $M=10^4$ 회 반복해 표본
   공분산을 구하고, CRLB $=(H^\top R^{-1}H)^{-1}$ 와 **각 성분이 상대오차 5% 이내**로 일치하는 것을
   확인한다.
2. **NEES 구간**: 1 의 실험에서 NEES 의 평균이 $\chi^2_{nM}/M$ 의 95% 구간 안에 있는 것을 확인한다
   (구간을 코드로 계산해 출력).
3. **과확신 검출**: 보고 공분산을 참값의 **1/2** 로 축소한 추정기를 만들어 NEES 평균이 구간
   **위로** 나가는 것을 보이고, **2배**로 키운 추정기는 아래로 나가는 것을 보인다.
4. **$1/N$ 수렴**: 관측 수를 $N \in \{10, 100, 1000\}$ 로 바꿔 사후 공분산의 대각 성분이 $1/N$ 에
   비례해 줄어드는 것을 로그-로그 기울기 $-1\pm0.1$ 로 확인한다.

**비교 대상**: `numpy.linalg.lstsq` 의 가중 최소제곱 해와 (1)의 해석적 해가 $10^{-10}$ 이내로 일치.

**실패 진단표**

| 증상 | 원인 | 확인 방법 |
|---|---|---|
| 표본 공분산이 CRLB 보다 작다 | 같은 난수를 재사용했거나(상관) 추정기가 편향됐다 | 시드를 반복마다 바꾸고 $\mathbb{E}[\hat{x}]-x$ 를 출력 |
| NEES 가 구간을 크게 벗어난다 | 보고 공분산과 참 공분산이 다르다(의도적이 아니라면 버그) | $R$ 과 $\Sigma$ 를 출력해 모델과 생성 과정이 일치하는지 확인 |
| 조건 4 의 기울기가 $-1$ 이 아니다 | 관측을 독립적으로 생성하지 않았다 | 노이즈 샘플의 상관을 확인 |
| CRLB 계산이 특이하다 | $H$ 가 랭크 결핍(P1) | $H$ 의 수치 랭크를 임계값과 함께 출력 |

## 열린 문제

- **(열린 문제) 비선형·비가우시안에서의 달성 가능 한계** — CRLB 는 불편·정칙 조건 아래의 한계다.
  매니폴드 위(C1) 와 다봉 사후분포에서 **무엇이 달성 가능한 하한인지**가 일반적으로 정리되지
  않았다. 매니폴드 CRLB 의 변형들이 제안됐지만 로보틱스 실무에 표준이 없다.
- **(열린 문제) 유한 표본 보장** — MLE 의 효율성은 **점근적**이다. 로보틱스는 관측이 적은
  상황(초기화, 짧은 궤적)에서 추정해야 하는데, 유한 표본에서의 편향·공분산 보장이 부족하다.
- **(열린 문제) 일관성 평가의 표준화** — NEES 는 참값을 알아야 계산되므로 실기 실험에서 쓰기
  어렵다. **참값 없이 공분산 일관성을 평가**하는 방법이 제한적이다(`s1-slam-benchmarking` 과
  `s4-evaluation-science` 의 열린 문제와 같은 항목).

## 개념 점검

`rc quiz r0-estimation-theory` 로 푼다. 개념 점검 전용이다.

```quiz
activity: r0-estimation-theory-quiz
questions:
  - id: q1
    type: single
    prompt: "선형 가우시안 모델에서 MAP 추정은 무엇과 같은가?"
    choices:
      - "일반 최소제곱 (가중치 없음)"
      - "역공분산으로 가중된 최소제곱 + 사전 항"
      - "최대 엔트로피 추정"
      - "중앙값 추정"
    answer: 1
    explanation: "가우시안 밀도의 지수에 있는 이차형식이 그대로 비용이 되므로 가중치는 역공분산이고, 사전도 같은 자격의 항으로 들어간다. C5 의 인자 그래프는 이 항이 많아진 형태다."
    concept: { front: "선형 가우시안의 MAP", back: "역공분산 가중 최소제곱 + 사전 항. 가중치가 역공분산인 이유는 지수의 이차형식" }
  - id: q2
    type: short
    prompt: "선형 가우시안 모델($z=Hx+w$, $w\\sim\\mathcal{N}(0,R)$)의 Fisher 정보 행렬은?"
    answer: ["H^T R^-1 H", "H^T R^{-1} H", "HTR-1H", "H' R^-1 H", "H^\\top R^{-1}H"]
    explanation: "점수 함수가 $s = H^\\top R^{-1}(z-Hx)$ 이므로 $\\mathcal{I} = \\mathbb{E}[ss^\\top] = H^\\top R^{-1}H$ 다. 이것이 정보행렬 $\\Lambda$ 와 같고, 그 역이 달성 가능한 최소 공분산이다."
    concept: { front: "선형 가우시안의 Fisher 정보", back: "$\\mathcal{I} = H^\\top R^{-1}H = \\Lambda$ (정보행렬). 역이 CRLB" }
  - id: q3
    type: truefalse
    prompt: "어떤 추정기의 분산이 Cramér-Rao 하한보다 작다면 계산에 오류가 있다."
    answer: false
    explanation: "CRLB 는 **불편** 추정기에 대한 한계다. 편향을 허용하면 더 작은 분산이 가능하다(극단적으로 상수 추정기는 분산 0). 그래서 '하한을 깼다'는 보고는 먼저 불편성을 확인해야 한다."
    concept: { front: "CRLB 의 가정", back: "불편성과 정칙 조건. 편향 추정기는 하한보다 작은 분산을 가질 수 있다" }
  - id: q4
    type: single
    prompt: "$n$ 차원 상태 추정에서 NEES 평균이 $3n$ 으로 나왔다. 무슨 뜻인가?"
    choices:
      - "추정이 정확하다"
      - "공분산을 너무 작게 보고하고 있다 (과확신)"
      - "공분산을 너무 크게 보고하고 있다 (과보수적)"
      - "오차가 가우시안이 아니다"
    answer: 1
    explanation: "보고 공분산이 옳으면 $\\mathbb{E}[\\mathrm{NEES}]=n$ 이다. $3n$ 은 실제 오차가 보고된 불확실성보다 크다는 뜻, 즉 과확신이다 — 융합에서 다른 관측을 눌러 버려 치명적이다."
    concept: { front: "NEES 로 읽는 공분산 품질", back: "$\\mathbb{E}[\\mathrm{NEES}]=n$ 이 정상. $\\gg n$ 은 과확신, $\\ll n$ 은 과보수적" }
```

## 이 단계 공부법

1. **(1)을 백지에서 유도한다 (40분)** — 베이즈 → 로그 → 이차형식의 세 줄이다. "가중치가 왜
   역공분산인가"에 답할 수 있으면 C5 의 모든 유도가 쉬워진다.
2. **CRLB 를 Schur 보완으로 본다 (70분)** — 증명의 3·4 단계가 `r0-sparse-linear-algebra` 의 R3
   과 같은 도구다. 같은 수학이 다른 맥락에서 반복되는 것을 확인하면 기억에 남는다.
3. **불편성 가정을 반례로 각인한다 (40분)** — P6 을 푼다. "CRLB 를 깼다"는 말이 왜 보통 버그가
   아니라 **가정 위반**인지 알게 된다.
4. **NEES 를 직접 돌려 본다 (80분)** — 재현 과제 조건 2·3 을 함께 한다. 공분산을 일부러 틀리게
   보고해 지표가 반응하는 것을 보는 것이 이 레슨의 핵심 경험이다. C5 와 S1 의 평가가 이 지표를 쓴다.
5. **랭크 결핍을 추정 관점에서 다시 본다 (40분)** — P1 에서 "관측만으로 결정되지 않는 방향"이
   나온다. 이것이 `c1-manifold-optimization` 의 게이지와 같은 것임을 확인한다 — 선형대수·최적화·
   추정 세 관점이 같은 현상을 가리킨다.
6. **교재는 가정의 목록을 찾으며 읽는다 (110분)** — Thrun ch.2 의 재귀 필터 유도에서 Markov 와
   관측 독립 가정이 쓰이는 **정확한 지점**을 찾는다. 그 지점이 C5 에서 깨지는 자리다.

**통과 기준**: (1)과 (2)를 백지에서 유도할 수 있고, CRLB 를 증명하고 그 가정을 말할 수 있고,
NEES 로 과확신을 판정하는 코드가 재현 과제 네 조건을 만족하고, 교재 노트 2편이 있다.
