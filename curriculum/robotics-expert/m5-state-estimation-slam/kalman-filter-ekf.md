---
id: m5-kalman-filter-ekf
title: "칼만 필터(1D→다차원)와 EKF"
summary: belief 를 가우시안 하나로 근사하면 베이즈 필터가 평균과 분산의 닫힌 식, 즉 칼만 필터가 된다. 1차원 칼만 필터에서 칼만 이득의 의미를 잡고, 행렬 형태의 다차원 칼만 필터와 비선형 모델을 선형화하는 EKF 로 확장한다.
objectives:
  - 1차원 칼만 필터의 예측·갱신 식을 유도 없이 쓰고 칼만 이득이 예측과 측정의 신뢰도 비율임을 설명할 수 있다.
  - 상태 벡터·F·H·Q·R 행렬을 정해 등속 모델 다차원 칼만 필터를 numpy 로 구현할 수 있다.
  - 비선형 모션·관측 모델에서 야코비안으로 선형화하는 EKF 의 구조와 한계를 설명할 수 있다.
prerequisites: [m5-bayes-filter, m1-vectors-matrices, m4-filtering-basics]
difficulty: 3
estimated_minutes: 130
tags: [kalman-filter, ekf, gaussian, jacobian, state-estimation]
activities:
  - id: m5-kalman-filter-ekf-reading
    kind: reading
    title: 본문과 Labbe Ch. 4–6 읽기
    estimated_minutes: 50
  - id: m5-kalman-filter-ekf-quiz
    kind: quiz
    title: 칼만 이득과 공분산 퀴즈
    estimated_minutes: 20
  - id: m5-kalman-filter-ekf-exercise
    kind: exercise
    title: 1D·등속 칼만 필터 튜닝 실험
    estimated_minutes: 60
resources:
  - title: "Kalman and Bayesian Filters in Python (Labbe)"
    url: https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python
    kind: book
    note: Ch. 4–10(1D/다변량 KF, KF 수학, KF 설계, 비선형, UKF, EKF). 예제는 filterpy 사용.
  - title: "Kalman Filter & EKF (Stachniss)"
    url: https://www.youtube.com/watch?v=E-6paM_Iwfc
    kind: video
    note: Online Training – Mobile Robotics, Robotics 블록.
  - title: "EKF Localization (Stachniss)"
    url: https://www.youtube.com/watch?v=PiCC-SxWlH8
    kind: video
    note: 랜드마크 관측으로 로봇 자세를 추정하는 EKF 적용 사례.
  - title: "Michigan ROB 530 Mobile Robotics"
    url: https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public
    kind: course
    note: HW 2–3(KF·비선형 필터)으로 연습량을 늘린다(선택).
---

# 칼만 필터(1D→다차원)와 EKF

히스토그램 필터는 직관적이지만 상태가 여러 차원이면 격자가 폭발한다. 칼만 필터는 belief 를
**가우시안** $\mathcal{N}(\mu, \Sigma)$ 로 가정한다. 선형 모델과 가우시안 노이즈라면 예측·보정
뒤에도 가우시안이 유지되므로 평균과 공분산만 갱신하면 된다. M4 의 상보 필터가 고정 비율 $\alpha$
로 섞었다면, 칼만 필터는 그 비율(칼만 이득)을 매 스텝 불확실성으로부터 계산한다.

## 개념

### 1차원 칼만 필터

상태가 스칼라 $x$ 하나일 때, belief 는 평균 $\mu$ 와 분산 $P$ 다.

- **예측:** 이동량 $u$ 를 더하고, 모션 노이즈 분산 $Q$ 만큼 불확실성이 커진다.
- **갱신:** 측정 $z$(분산 $R$)와 예측의 차이(혁신, innovation)에 이득 $K$ 를 곱해 더한다.
  $P$ 가 $R$ 보다 크면 $K \to 1$(측정을 믿음), 작으면 $K \to 0$(예측을 믿음).

두 가우시안을 곱하면 분산이 둘 중 작은 것보다도 작아진다. 서로 독립인 정보 두 개를 합치면
어느 하나보다 더 확실해진다는 뜻이다.

### 다차원 칼만 필터

상태를 벡터로(예: 위치와 속도), 모델을 행렬로 쓴다. $F$ 는 상태 전이, $B$ 는 제어 입력,
$H$ 는 상태에서 측정으로의 사상, $Q$, $R$ 은 공분산이다. 위치만 측정해도 위치·속도 사이의
**공분산**을 통해 속도까지 추정된다는 점이 핵심이다.

### EKF

로봇 모델은 대부분 비선형이다(차동 구동의 $\cos\theta$, 거리·방위 측정의 $\sqrt{\cdot}$,
$\operatorname{atan2}$). EKF 는 현재 추정점에서 야코비안 $F_t = \partial f/\partial x$,
$H_t = \partial h/\partial x$ 로 선형화해 같은 식을 쓴다. 평균은 비선형 함수로 그대로 옮기고
공분산만 야코비안으로 전파한다. 선형화 오차가 크거나(불확실성이 클 때, 강한 회전) 초기값이
틀리면 발산할 수 있다. 그 대안이 UKF 와 다음 레슨의 파티클 필터다.

## 핵심 수식

예측:

$$\bar\mu_t = F\mu_{t-1} + Bu_t,\qquad \bar\Sigma_t = F\Sigma_{t-1}F^\top + Q$$

갱신:

$$K_t = \bar\Sigma_t H^\top (H\bar\Sigma_t H^\top + R)^{-1}$$

$$\mu_t = \bar\mu_t + K_t(z_t - H\bar\mu_t),\qquad \Sigma_t = (I - K_t H)\bar\Sigma_t$$

1차원에서는 $K = P/(P+R)$ 로 줄어든다. EKF 는 $F\mu$ 를 $f(\mu, u)$ 로, $H\bar\mu$ 를
$h(\bar\mu)$ 로 바꾸고 $F$, $H$ 자리에 야코비안을 넣는다.

## 예제

먼저 1차원: 매 스텝 1 m 씩 전진 명령을 받는 로봇의 위치를 GPS 같은 위치 센서($\sigma=2$ m)로 추정한다.

```python
import numpy as np

rng = np.random.default_rng(0)
Q, R = 0.1**2, 2.0**2  # 모션·측정 노이즈 분산
x_true, mu, P = 0.0, 0.0, 10.0**2  # 참값, 초기 추정, 초기 분산(모른다)
errs_raw, errs_kf = [], []

for k in range(50):
    x_true += 1.0 + rng.normal(0, np.sqrt(Q))  # 실제 이동
    z = x_true + rng.normal(0, np.sqrt(R))  # 위치 측정

    mu, P = mu + 1.0, P + Q  # 예측
    K = P / (P + R)  # 칼만 이득
    mu, P = mu + K * (z - mu), (1 - K) * P  # 갱신

    errs_raw.append(z - x_true)
    errs_kf.append(mu - x_true)
    if k in (0, 1, 5, 49):
        print(f"k={k:2d}  K={K:.3f}  sigma={np.sqrt(P):.2f}")

print("측정만 RMS", np.sqrt(np.mean(np.square(errs_raw))).round(2))
print("KF RMS   ", np.sqrt(np.mean(np.square(errs_kf))).round(2))
```

처음엔 $P$ 가 커서 $K \approx 1$ 이고 측정을 그대로 믿다가, 스텝마다
줄어 50 스텝 뒤에는 $K \approx 0.05$ 로 예측을 주로 믿는다. 오차는 측정만 쓸 때(약 2 m)보다 크게 작아진다.

다음은 위치만 측정하면서 위치·속도를 함께 추정하는 등속 모델이다.

```python
import numpy as np

rng = np.random.default_rng(1)
dt = 0.1
F = np.array([[1, dt], [0, 1]])
H = np.array([[1.0, 0.0]])
Q = 0.05 * np.array([[dt**3 / 3, dt**2 / 2], [dt**2 / 2, dt]])  # 가속도 잡음
R = np.array([[0.5**2]])

x = np.array([0.0, 2.0])  # 참값: 2 m/s 로 이동
mu, S = np.zeros(2), np.eye(2) * 10.0
for _ in range(100):
    x = F @ x
    z = H @ x + rng.normal(0, 0.5, 1)
    mu, S = F @ mu, F @ S @ F.T + Q
    K = S @ H.T @ np.linalg.inv(H @ S @ H.T + R)
    mu = mu + K @ (z - H @ mu)
    S = (np.eye(2) - K @ H) @ S

print("참 속도 2.0, 추정 속도", mu[1].round(2), "±", np.sqrt(S[1, 1]).round(2))
```

**연습 과제(exercise):** (1) 1D 예제에서 $Q$ 를 100 배로 키우면 정상 상태 $K$ 와 RMS 가 어떻게
바뀌는지 설명하라. (2) 일부러 $R$ 을 실제보다 10 배 작게 설정해 필터가 "측정을 과신"할 때를
관찰하라. (3) 등속 예제의 관측을 거리 $\sqrt{x^2 + d^2}$(옆 $d$ m 에 있는 비콘)로 바꾸고
야코비안 $H_t$ 를 손으로 구해 EKF 로 고쳐라.

## 자가 점검 질문

1. 1차원 칼만 필터에서 $P \gg R$ 일 때와 $P \ll R$ 일 때 칼만 이득과 갱신 결과는 각각 어떻게 되는가?
2. 위치만 측정하는데 속도가 추정되는 이유를 공분산 $\Sigma$ 의 비대각 성분으로 설명하라.
3. EKF 가 발산하기 쉬운 상황 두 가지와, 그때 고려할 대안을 써라.

## 확인 퀴즈

`rc quiz m5-kalman-filter-ekf` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m5-kalman-filter-ekf-quiz
questions:
  - id: q1
    type: single
    prompt: '1차원 칼만 필터에서 예측 분산 $P$ 가 측정 분산 $R$ 보다 훨씬 클 때($P \gg R$) 칼만 이득 $K$ 와 갱신 결과는?'
    choices:
      - '$K \to 0$ — 측정을 거의 무시하고 예측을 유지한다'
      - '$K \to 1$ — 측정 쪽으로 거의 완전히 이동한다'
      - '$K < 0$ — 측정의 반대 방향으로 간다'
      - '$K$ 는 $P$, $R$ 과 무관하다'
    answer: 1
    explanation: '$K = P/(P+R)$ 이므로 $P \gg R$ 이면 $K \to 1$ 이고, 추정은 측정값 쪽으로 거의 다 끌려간다. 예측이 매우 불확실할 때 신뢰할 수 있는 측정을 받으면 그것을 믿는 것이 합리적이다. 반대로 $P \ll R$ 이면 $K \to 0$ 이다.'
    concept: { front: '칼만 이득 $K = P/(P+R)$', back: '$P \gg R$ → $K \to 1$(측정 신뢰), $P \ll R$ → $K \to 0$(예측 신뢰)' }
  - id: q2
    type: single
    prompt: '위치만 측정하는데도 속도가 추정되는 이유는?'
    choices:
      - '측정 행렬 $H$ 가 속도를 직접 관측하기 때문'
      - '공분산 $\Sigma$ 의 비대각 성분이 위치와 속도의 상관을 담고 있어, 위치 보정이 속도에도 전파되기 때문'
      - '속도는 항상 상수로 가정하기 때문'
      - '칼만 이득이 속도만 갱신하기 때문'
    answer: 1
    explanation: '상태 전이 $F$ 가 위치를 속도로 밀기 때문에 예측 단계에서 두 변수 사이에 상관(비대각 공분산)이 생긴다. 갱신에서 $K = \bar\Sigma H^\top(\cdot)^{-1}$ 가 그 상관을 통해 위치 혁신을 속도 보정으로 옮긴다. 이것이 칼만 필터가 미분기보다 조용히 속도를 얻는 방식이다.'
    concept: { front: '관측하지 않은 상태가 추정되는 원리', back: '공분산의 비대각 성분(상관)을 통해 관측 혁신이 다른 상태로 전파된다' }
  - id: q3
    type: multiple
    prompt: 'EKF 가 발산하기 쉬운 상황과 그 대안에 대해 옳은 설명을 모두 고르시오.'
    choices:
      - '불확실성이 커서 선형화 지점에서 멀리까지 퍼질 때 위험하다'
      - '초기 추정이 실제와 크게 다르면 틀린 지점에서 선형화해 발산할 수 있다'
      - '분포가 여러 봉우리(multi-modal)일 때 단일 가우시안으로 표현할 수 없다'
      - '야코비안을 쓰므로 비선형 모델에서도 선형화 오차가 전혀 없다'
    answer: [0, 1, 2]
    explanation: 'EKF 는 현재 추정점의 1차 근사를 쓰므로 퍼짐이 크거나 초기값이 틀리면 근사가 무너진다. 또 belief 가 가우시안 하나라서 "복도 A 아니면 복도 B" 같은 다봉 분포를 담지 못한다. 대안은 UKF(더 나은 비선형 전파)와 파티클 필터(다봉 가능)다.'
```

## 이 단계 공부법

1. **교재(먼저):** Labbe 의 Gaussians·One Dimensional Kalman Filters 장을 실행하며 이 레슨 1D 예제와 비교한다.
2. **영상:** Stachniss "Kalman Filter & EKF" 로 행렬 형태를 정리하고, "EKF Localization" 으로 적용 예를 본다.
3. **본문 + 예제:** 두 예제를 돌리고 연습 과제 (1)–(3)을 한다. (3)이 EKF 의 첫 구현이다.
4. **심화:** Labbe 의 Multivariate Kalman Filters·Kalman Filter Math 장과 Extended Kalman Filters 장을 읽는다. `filterpy` 의
   `KalmanFilter` 로 같은 문제를 풀어 손 구현과 결과를 맞춰 본다.
5. **연습량(선택):** ROB 530 HW 2–3 으로 비선형 필터를 더 연습한다.

## 참고 자료

- Roger Labbe, *Kalman and Bayesian Filters in Python*, Ch. 4–10 —
  <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
- Cyrill Stachniss, "Kalman Filter & EKF" — <https://www.youtube.com/watch?v=E-6paM_Iwfc>
- Cyrill Stachniss, "EKF Localization" — <https://www.youtube.com/watch?v=PiCC-SxWlH8>
- University of Michigan, ROB 530 Mobile Robotics — <https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public>
