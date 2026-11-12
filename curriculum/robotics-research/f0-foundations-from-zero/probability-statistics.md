---
id: f0-probability-statistics
title: 확률·통계
summary: >-
  조건부확률·베이즈 정리·기댓값·분산·대수의 법칙·중심극한정리를 쓰고, 추정과 신뢰구간을 계산하는
  수준까지 올린다. MIT 18.05(문제집·시험 해답 공개)로 안내하고, 영상이 필요하면 6.041 을 쓴다.
objectives:
  - 조건부확률과 베이즈 정리를 쓰고 사전·사후 분포를 구분할 수 있다.
  - 기댓값·분산·공분산을 계산하고 선형 변환 하의 변화를 쓸 수 있다.
  - 가우시안 분포의 성질(선형 변환, 주변화, 조건부)을 말할 수 있다.
  - 대수의 법칙과 중심극한정리를 구분해 설명할 수 있다.
  - 점추정·신뢰구간을 계산하고 가설검정의 의미를 말할 수 있다.
prerequisites: [f0-calculus-multivariable]
difficulty: 1
estimated_minutes: 4200
tags: [foundations, probability, statistics, guide]
activities:
  - id: f0-probability-statistics-diagnostic
    kind: quiz
    title: 시작 전 자가 진단 (통과하면 이 레슨을 건너뛴다)
    estimated_minutes: 40
  - id: f0-probability-statistics-lectures
    kind: reading
    title: MIT 18.05 노트 읽기 (영상이 필요하면 6.041)
    estimated_minutes: 2200
  - id: f0-probability-statistics-problems
    kind: exercise
    title: 문제집과 기출 시험 풀이 (해답으로 자기 채점)
    estimated_minutes: 1960
resources:
  - title: "MIT 18.05 Introduction to Probability and Statistics (Spring 2022)"
    url: https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/
    kind: course
    note: 1순위. 강의 노트·읽기 자료·문제집·시험과 해답 공개(강의 영상은 없다).
  - title: "MIT 6.041 Probabilistic Systems Analysis (Fall 2010)"
    url: https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-fall-2010/
    kind: course
    note: 영상이 필요하면 이쪽. 강의 영상·문제집·시험과 해답 공개. 공학 지향이라 로보틱스에 더 가깝다.
  - title: "NumPy random 문서"
    url: https://numpy.org/doc/stable/reference/random/index.html
    kind: notes
    note: 몬테카를로로 분포·극한 정리를 직접 확인하는 실습에 쓴다.
---

# 확률·통계

## 도달 목표

이 레슨은 **가이드형**이다. 통과하면 건너뛴다.

로보틱스에서 **센서는 노이즈를 주고 추정은 확률 문제**다. C5(상태 추정) 전체, R0 의 추정 이론,
C8 의 학습 이론, R1 의 평가·통계가 이 레슨을 전제한다. 특히 **가우시안의 선형 변환·주변화·조건부**
세 성질과 **베이즈 정리**는 칼만 필터와 인자 그래프를 유도할 때 그대로 쓰인다.

통과 기준은 §시작 전 자가 진단의 6문항 중 5문항 이상이다.

## 시작 전 자가 진단

`rc quiz f0-probability-statistics` 로 푼다. 5/6 이상이면 건너뛰고 `f0-python-numerics-git` 로 간다.

```quiz
activity: f0-probability-statistics-diagnostic
questions:
  - id: q1
    type: short
    prompt: "질병 유병률 1%, 검사 민감도 99%, 특이도 99% 일 때 양성 결과가 나왔을 때 실제 질병일 확률은 약 몇 %인가? (정수)"
    answer: ["50", "50%", "약 50", "50 percent"]
    explanation: "베이즈 정리로 $P = \\frac{0.99\\times0.01}{0.99\\times0.01 + 0.01\\times0.99} = 0.5$. 사전확률이 낮으면 정확한 검사도 사후확률을 크게 올리지 못한다 — 이 직관이 센서 융합에서 그대로 쓰인다."
    concept: { front: "베이즈 정리와 낮은 사전확률", back: "$P(H|E) = P(E|H)P(H)/P(E)$. 사전확률이 낮으면 정확한 관측도 사후확률을 제한적으로만 올린다" }
  - id: q2
    type: short
    prompt: "$x \\sim \\mathcal{N}(\\mu, \\Sigma)$ 이고 $y = Ax + b$ 일 때 $y$ 의 공분산은?"
    answer: ["A Sigma A^T", "AΣA^T", "A\\Sigma A^\\top", "ASigmaA^T", "A Σ A^T"]
    explanation: "$\\mathrm{Cov}(y) = A\\Sigma A^\\top$ (평균은 $A\\mu+b$). 가우시안은 선형 변환에서 가우시안으로 닫히고, 이 한 줄이 칼만 필터의 예측 단계다."
    concept: { front: "가우시안의 선형 변환", back: "$y=Ax+b$ 면 $y \\sim \\mathcal{N}(A\\mu+b,\\ A\\Sigma A^\\top)$ — 가우시안 족이 닫힌다" }
  - id: q3
    type: single
    prompt: "대수의 법칙과 중심극한정리의 차이는?"
    choices:
      - "같은 정리의 다른 이름이다"
      - "대수의 법칙은 표본평균이 참값으로 수렴한다는 것이고, 중심극한정리는 그 **오차의 분포**가 가우시안이 된다는 것이다"
      - "대수의 법칙은 분산에 대한 것이고 중심극한정리는 평균에 대한 것이다"
      - "중심극한정리는 표본이 가우시안일 때만 성립한다"
    answer: 1
    explanation: "대수의 법칙은 수렴(어디로 가는가), 중심극한정리는 수렴 속도와 오차 분포(얼마나 퍼져 있는가)를 말한다. R1 의 신뢰구간 계산이 후자에 의존한다."
    concept: { front: "대수의 법칙 vs 중심극한정리", back: "전자는 표본평균의 수렴, 후자는 그 오차가 $\\mathcal{N}(0,\\sigma^2/n)$ 로 분포한다는 것" }
  - id: q4
    type: single
    prompt: "결합 가우시안에서 일부 변수를 주변화(marginalize)하면?"
    choices:
      - "가우시안이 아니게 된다"
      - "남은 변수의 평균과 공분산의 해당 블록만 떼면 된다"
      - "역공분산(정보행렬)의 해당 블록만 떼면 된다"
      - "항상 분산이 커진다"
    answer: 1
    explanation: "**공분산** 형식에서는 블록을 떼면 끝이지만, **정보행렬** 형식에서는 Schur 보완이 필요하다(그래서 주변화가 그래프를 조밀하게 만든다). C5 의 iSAM2 가 바로 이 차이를 다룬다."
    concept: { front: "가우시안 주변화", back: "공분산에서는 블록 추출, 정보행렬에서는 Schur 보완 — 후자가 희소성을 깨뜨린다" }
  - id: q5
    type: short
    prompt: "표본 100개의 평균이 10, 표준편차가 2 일 때 평균의 95% 신뢰구간 폭(한쪽)은 약 얼마인가? (소수 둘째 자리)"
    answer: ["0.39", "0.392", "0.4", "0.39 (1.96*2/10)"]
    explanation: "$1.96 \\times \\sigma/\\sqrt{n} = 1.96 \\times 2/10 = 0.392$. R1 의 '시행 몇 번이 필요한가'(검정력 분석)가 이 식의 역산이다."
    concept: { front: "평균의 신뢰구간", back: "$\\bar{x} \\pm z\\,\\sigma/\\sqrt{n}$ — 폭이 $1/\\sqrt{n}$ 로 줄어든다" }
  - id: q6
    type: truefalse
    prompt: "두 확률변수가 상관계수 0 이면 서로 독립이다."
    answer: false
    explanation: "독립 ⇒ 무상관이지만 역은 거짓이다(예: $x \\sim U(-1,1)$, $y=x^2$ 는 무상관이나 종속). 단, **결합 가우시안**에서는 무상관 = 독립이다 — 이 예외가 칼만 필터가 공분산만으로 충분한 이유다."
    concept: { front: "무상관과 독립", back: "독립 ⇒ 무상관. 역은 일반적으로 거짓이지만 결합 가우시안에서는 동등" }
```

## 학습 경로

**1순위**: [MIT 18.05 (Spring 2022)](https://ocw.mit.edu/courses/18-05-introduction-to-probability-and-statistics-spring-2022/) —
노트·문제집·시험과 해답이 공개된다(영상 없음).
**영상이 필요하면**: [MIT 6.041 (Fall 2010)](https://ocw.mit.edu/courses/6-041-probabilistic-systems-analysis-and-applied-probability-fall-2010/) —
강의 영상·문제집·시험과 해답 공개. 공학 지향이라 로보틱스에 더 가깝다.

| 단계 | 범위 | 무엇을 할 수 있게 되는가 | 예상 |
|---|---|---|---|
| 1 | 확률 기초 | 표본공간, 조건부확률, 독립, 베이즈 정리 | 15시간 |
| 2 | 확률변수 | 분포, 기댓값·분산, 공분산, 변수변환 | 18시간 |
| 3 | 다변량 가우시안 | 선형 변환, 주변화, 조건부, 공분산 vs 정보행렬 | 15시간 |
| 4 | 극한 정리와 추정 | 대수의 법칙, 중심극한정리, MLE, 신뢰구간, 가설검정 | 22시간 |

합계 약 70시간. **3단계를 가장 꼼꼼히 하라** — C5 의 모든 유도가 이 세 성질 위에 서 있다.

## 이 단계 공부법

1. **진단을 먼저 (40분)** — 5/6 이상이면 끝이다.
2. **몬테카를로로 모든 정리를 확인한다 (매 단계)** — 베이즈 정리, 중심극한정리, 신뢰구간의
   커버리지를 numpy 로 직접 재현한다. "정리를 읽었다"와 "정리가 참인 것을 봤다"는 다르다.
3. **3단계는 손으로 블록 계산을 한다 (15시간)** — 2×2 블록 가우시안의 주변화와 조건부를 손으로
   유도한다. 공분산 형식과 정보행렬 형식을 **둘 다** 해 본다 — 차이가 C5 의 희소성 논의의 핵심이다.
4. **"무상관 ≠ 독립"을 반례로 기억한다 (1시간)** — $y=x^2$ 예를 직접 수치로 확인한다. 가우시안
   예외가 왜 특별한지 알게 된다.
5. **신뢰구간을 역산해 본다 (2시간)** — "성공률 차이 5%p 를 95% 신뢰로 검출하려면 몇 번
   시행해야 하나"를 계산한다. R1 과 S4 의 평가 설계가 이 계산이다.
6. **기출로 판정한다** — 18.05 기출 2회 또는 6.041 기출 2회를 80% 이상.

**통과 기준**: 진단 5/6 이상, 기출 80% 이상, 그리고 중심극한정리와 신뢰구간 커버리지를 몬테카를로로
확인하는 코드를 스스로 쓸 수 있다.
