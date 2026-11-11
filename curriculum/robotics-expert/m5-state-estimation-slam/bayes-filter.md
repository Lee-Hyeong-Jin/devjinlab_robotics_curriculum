---
id: m5-bayes-filter
title: "확률·베이즈 필터 기초"
summary: 로봇의 상태를 하나의 값이 아니라 확률 분포(belief)로 표현하고, 모션 모델로 예측하고 관측 모델로 보정하는 베이즈 필터의 두 단계를 이산(히스토그램) 필터로 구현한다. M5 의 모든 필터가 이 구조를 공유한다.
objectives:
  - 사전·우도·사후 확률과 베이즈 정리를 로봇 위치 추정 문제에 대응시켜 설명할 수 있다.
  - 베이즈 필터의 예측(prediction)과 보정(correction) 단계를 수식과 코드로 쓸 수 있다.
  - 1차원 격자 세계에서 히스토그램 필터를 구현하고 모션·관측 노이즈가 belief 에 주는 영향을 설명할 수 있다.
prerequisites: [m4-sensor-models, m3-differential-drive]
difficulty: 3
estimated_minutes: 100
tags: [probability, bayes-filter, histogram-filter, markov-localization, state-estimation]
activities:
  - id: m5-bayes-filter-reading
    kind: reading
    title: 본문과 Labbe Ch. 2 Discrete Bayes 읽기
    estimated_minutes: 40
  - id: m5-bayes-filter-quiz
    kind: quiz
    title: 베이즈 정리와 belief 갱신 퀴즈
    estimated_minutes: 15
  - id: m5-bayes-filter-exercise
    kind: exercise
    title: 복도 로봇 히스토그램 필터 실험
    estimated_minutes: 45
resources:
  - title: "Kalman and Bayesian Filters in Python (Labbe)"
    url: https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python
    kind: book
    note: Ch. 2 Discrete Bayes. 이 레슨 예제와 같은 복도·문 문제를 Jupyter 로 따라간다.
  - title: "Bayes Filter (Stachniss)"
    url: https://www.youtube.com/watch?v=0lKHFJpaZvE
    kind: video
    note: Online Training – Mobile Robotics, Robotics 블록 첫 강의.
  - title: "Stachniss Online Training – Mobile Robotics"
    url: https://www.ipb.uni-bonn.de/online-training-robotics/
    kind: course
    note: 확률 기초가 약하면 Basics 블록의 Probability Primer 부터 본다. 2020 연습문제 포함.
  - title: "Probabilistic Robotics (Thrun, Burgard, Fox)"
    url: https://robots.stanford.edu/probabilistic-robotics/
    kind: book
    note: Ch. 2 Recursive State Estimation(베이즈 필터 유도), Ch. 8 Grid Localization.
---

# 확률·베이즈 필터 기초

M3 에서 휠 엔코더를 적분해 위치를 구했고, M4 에서 센서마다 노이즈가 있다는 것을 봤다. 둘을
합치면 문제가 분명해진다. 로봇은 자기 위치를 **정확히 알 수 없다.** 그래서 상태 추정은 "로봇은
(2.0, 1.5) 에 있다" 대신 "로봇이 각 위치에 있을 확률은 이렇다"는 분포를 다룬다. 이 분포를
**belief** $bel(x_t)$ 라 부르고, 움직일 때와 관측할 때마다 갱신하는 규칙이 베이즈 필터다.
칼만 필터, 파티클 필터, SLAM 모두 이 틀의 특수한 구현이다.

## 개념

### 사전·우도·사후

- **사전(prior)** $p(x)$: 관측 전 믿음. 처음에 아무것도 모르면 균일 분포.
- **우도(likelihood)** $p(z \mid x)$: 로봇이 $x$ 에 있을 때 관측 $z$ 가 나올 확률. M4 의
  센서 모델이 바로 이것이다.
- **사후(posterior)** $p(x \mid z)$: 관측을 반영한 믿음.

베이즈 정리는 사후가 우도 × 사전에 비례한다고 말한다. 분모 $p(z)$ 는 $x$ 와 무관하므로
정규화 상수 $\eta$ 로 처리하면 된다. 코드에서는 곱한 뒤 합으로 나누는 한 줄이다.

### 마르코프 가정

현재 상태 $x_t$ 가 과거 정보를 모두 요약한다고 가정한다. 다음 상태는 $x_{t-1}$ 과 제어 $u_t$
에만, 관측 $z_t$ 는 $x_t$ 에만 의존한다. 덕분에 전체 기록을 저장하지 않고 직전 belief 하나만
들고 재귀적으로 갱신할 수 있다. 바퀴 미끄러짐이 누적되거나 사람이 지나가 지도와 다른 측정이
생기면 이 가정이 깨지며, 실전 필터는 노이즈를 조금 크게 잡아 이를 흡수한다.

### 두 단계

1. **예측:** 제어 $u_t$(예: "한 칸 전진")를 모션 모델에 넣어 belief 를 옮긴다. 모션에 노이즈가
   있으므로 분포는 **퍼진다**(불확실성 증가).
2. **보정:** 관측 $z_t$ 의 우도를 곱해 정규화한다. 관측과 맞는 위치의 확률이 커지고 분포는
   **좁아진다**(불확실성 감소).

상태 공간을 격자로 나눠 확률 배열로 저장하면 **히스토그램(이산 베이즈) 필터**, 위치 추정에
쓰면 **마르코프 로컬라이제이션**이다. 격자가 커지면 계산량이 폭발하므로 다음 레슨들에서 가우시안
(칼만)이나 샘플(파티클)로 분포를 근사한다.

## 핵심 수식

베이즈 정리:

$$p(x \mid z) = \frac{p(z \mid x)\,p(x)}{p(z)} = \eta\,p(z \mid x)\,p(x)$$

베이즈 필터(예측 → 보정):

$$\overline{bel}(x_t) = \sum_{x_{t-1}} p(x_t \mid u_t, x_{t-1})\,bel(x_{t-1})$$

$$bel(x_t) = \eta\,p(z_t \mid x_t)\,\overline{bel}(x_t)$$

연속 상태에서는 합이 적분이 된다. 예측 단계는 belief 와 모션 노이즈 커널의 **합성곱**이다.

## 예제

10칸짜리 원형 복도에 문이 세 개 있다. 로봇은 "문 보임/안 보임" 센서(75% 정확)를 갖고 한 칸씩
이동한다(80% 정확, 10% 덜·10% 더).

```python
import numpy as np

world = np.array([1, 1, 0, 0, 0, 0, 0, 0, 1, 0])  # 1 = 문, 0 = 벽
belief = np.full(10, 0.1)  # 처음엔 위치를 모른다(균일 분포)


def predict(belief, move, p_exact=0.8, p_under=0.1, p_over=0.1):
    """모션 모델: move 칸 이동하되 한 칸 덜/더 갈 수 있다(원형 복도)."""
    return (
        p_exact * np.roll(belief, move)
        + p_under * np.roll(belief, move - 1)
        + p_over * np.roll(belief, move + 1)
    )


def update(belief, z, p_hit=0.75):
    """관측 모델: 문 센서가 p_hit 확률로 맞게 읽는다."""
    likelihood = np.where(world == z, p_hit, 1 - p_hit)
    posterior = likelihood * belief
    return posterior / posterior.sum()  # 정규화 상수 η


for step, (move, z) in enumerate([(0, 1), (1, 1), (1, 0), (1, 0), (1, 0)]):
    belief = update(predict(belief, move), z)
    print(step, np.round(belief, 2), "최빈 위치:", belief.argmax())
```

첫 관측 직후에는 문 앞 세 칸(0, 1, 8)이 비슷한 확률을 갖는다. "문 → 문 → 벽 → 벽 → 벽"
패턴이 이어지면 이 패턴과 맞는 출발점은 0 번 칸뿐이므로 확률이 4 번 칸 근처로 모인다.
한 번의 관측으로는 모호하지만, **움직임과 관측의 순서**가 모호성을 없앤다는 것이 핵심이다.

**연습 과제(exercise):** (1) `p_hit` 를 0.55 와 0.95 로 바꿔 수렴 속도를 비교하라. (2) 관측 없이
`predict` 만 10 번 반복해 belief 가 균일 분포로 퍼지는 것을 확인하라. (3) 로봇을 실제로 움직이는
시뮬레이션(실제 위치 + 잡음 섞인 센서)을 만들어 필터의 최빈 위치가 참값을 따라가는지 그려라.

## 자가 점검 질문

1. 베이즈 필터의 예측 단계에서 belief 가 넓어지고 보정 단계에서 좁아지는 이유를 각각 설명하라.
2. 정규화 상수 $\eta$ 를 계산하지 않고 생략하면 히스토그램 필터에서 어떤 문제가 생기는가?
3. 2 m × 2 m 방을 1 cm 격자와 1° 방향 해상도로 나누면 상태 칸은 몇 개인가? 이것이 칼만·파티클
   필터가 필요한 이유와 어떻게 연결되는가?

## 확인 퀴즈

`rc quiz m5-bayes-filter` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m5-bayes-filter-quiz
questions:
  - id: q1
    type: single
    prompt: '베이즈 필터에서 예측 단계와 보정 단계는 belief 의 퍼짐에 각각 어떤 영향을 주는가?'
    choices:
      - '예측은 좁히고, 보정은 넓힌다'
      - '예측은 넓히고, 보정은 좁힌다'
      - '둘 다 넓힌다'
      - '둘 다 좁힌다'
    answer: 1
    explanation: '예측은 노이즈가 있는 모션 모델로 belief 를 옮기므로 불확실성이 커진다(퍼짐). 보정은 관측 우도를 곱해 관측과 맞지 않는 위치의 확률을 깎으므로 불확실성이 줄어든다(좁아짐). 필터는 이 두 작용의 균형이다.'
    concept: { front: '예측 vs 보정의 효과', back: '예측 = 모션 노이즈로 퍼짐(불확실성 증가), 보정 = 우도 곱으로 좁아짐(감소)' }
  - id: q2
    type: truefalse
    prompt: '정규화 상수 $\eta$ 를 생략해도 belief 의 **최댓값 위치**는 같으므로 히스토그램 필터에 아무 문제가 없다.'
    answer: false
    explanation: '한 스텝의 최댓값 위치는 같지만, 정규화하지 않으면 매 스텝 우도를 곱할 때마다 전체 합이 1에서 멀어져 값이 0으로 수렴(언더플로)하거나 발산한다. 재귀 필터에서는 매 스텝 합으로 나눠 확률 분포를 유지해야 한다.'
  - id: q3
    type: short
    prompt: '2 m × 2 m 방을 1 cm 격자, 방향 1° 해상도로 나누면 상태 칸은 몇 개인가? (숫자만, 예: 14400000)'
    answer: ['14400000', '14,400,000', '1.44e7', '14400000개']
    explanation: '$200 \times 200 \times 360 = 14{,}400{,}000$ 칸이다. 방 하나에 이미 천만 칸이 넘으므로 격자 전체를 들고 가는 방식은 금방 한계에 부딪힌다. 가우시안으로 요약하거나(칼만) 샘플로 근사하는(파티클) 이유가 이것이다.'
    concept: { front: '이산 베이즈 필터의 한계', back: '상태 칸이 차원·해상도에 따라 폭발 — 2 m 방·1 cm·1° 로도 1,440만 칸' }
```

## 이 단계 공부법

1. **영상(먼저):** Stachniss "Bayes Filter" 강의로 전체 그림을 잡는다. 확률 기초가 흔들리면
   Basics 블록의 Probability Primer 를 먼저 본다.
2. **교재 + 노트북:** Labbe Ch. 2 를 Jupyter 에서 실행하며 이 레슨 예제와 비교한다.
3. **본문 + 예제:** 예제를 돌리고 연습 과제 (1)–(3)을 수행한다.
4. **문제:** 퀴즈의 베이즈 정리 계산(사전·우도 → 사후)을 손으로 한 번 푼다.
5. **심화(선택):** *Probabilistic Robotics* Ch. 2 로 베이즈 필터 유도를 따라가 본다.

## 참고 자료

- Roger Labbe, *Kalman and Bayesian Filters in Python*, Ch. 2 Discrete Bayes —
  <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
- Cyrill Stachniss, "Bayes Filter" — <https://www.youtube.com/watch?v=0lKHFJpaZvE>
- Cyrill Stachniss, Online Training – Mobile Robotics — <https://www.ipb.uni-bonn.de/online-training-robotics/>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, MIT Press —
  <https://robots.stanford.edu/probabilistic-robotics/>
