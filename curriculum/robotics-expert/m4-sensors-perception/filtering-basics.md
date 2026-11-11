---
id: m4-filtering-basics
title: "필터링 기초: 이동 평균·저역통과·상보 필터"
summary: 노이즈 낀 센서 신호를 이동 평균과 1차 저역통과 필터로 다듬고, 자이로와 가속도계를 상보 필터로 합쳐 기울기를 추정한다. 칼만 필터(M5)로 가기 전의 직관을 만든다.
objectives:
  - 이동 평균과 1차 저역통과(IIR) 필터를 구현하고 노이즈 감소와 지연의 트레이드오프를 설명할 수 있다.
  - 시정수 τ 와 샘플 주기 Δt 로부터 필터 계수 α 를 계산할 수 있다.
  - 상보 필터로 자이로(고주파)와 가속도계(저주파)를 결합해 기울기를 추정할 수 있다.
prerequisites: [m4-sensor-models]
difficulty: 2
estimated_minutes: 90
tags: [filtering, low-pass, complementary-filter, imu, sensor-fusion]
activities:
  - id: m4-filtering-basics-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 30
  - id: m4-filtering-basics-quiz
    kind: quiz
    title: 필터 계수와 지연 퀴즈
    estimated_minutes: 15
  - id: m4-filtering-basics-exercise
    kind: exercise
    title: IMU 기울기 추정 필터 비교 실험
    estimated_minutes: 45
resources:
  - title: "Kalman and Bayesian Filters in Python (Labbe)"
    url: https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python
    kind: book
    note: Ch. 1 g-h 필터. "예측과 측정 사이에서 비율로 섞는다"는 상보·칼만 필터의 공통 직관.
  - title: "Brian Douglas / MATLAB Tech Talks: Control Systems"
    url: https://mathworks.com/videos/tech-talks/controls
    kind: video
    note: 주파수 응답·필터 직관이 필요할 때 참고(선택).
  - title: "Introduction to Autonomous Robots (Correll 외)"
    url: https://introduction-to-autonomous-robots.github.io/
    kind: book
    note: 센서 장. IMU·거리 센서와 노이즈 처리 기초(무료).
  - title: "Probabilistic Robotics (Thrun, Burgard, Fox)"
    url: https://robots.stanford.edu/probabilistic-robotics/
    kind: book
    note: 다음 단계(M5) 준비용. 2–3장 베이즈 필터·칼만 필터를 훑어본다.
---

# 필터링 기초: 이동 평균·저역통과·상보 필터

앞 레슨에서 본 것처럼 센서 값은 그대로 쓰기에 너무 떨린다(가속도계)거나 시간이 갈수록
흘러간다(자이로). 이 레슨은 가장 단순한 세 가지 필터로 이 문제를 다룬다. 계산은 몇 줄이지만
"노이즈를 줄이면 반응이 느려진다", "서로 다른 약점을 가진 센서를 섞는다"는 생각은 중급 M5 의
칼만 필터까지 그대로 이어진다. 1차원 칼만 필터는 M5 에서 베이즈 필터와 함께 정식으로 다룬다.

## 개념

### 이동 평균

최근 $N$ 개 샘플의 평균이다. 독립 백색 잡음의 표준편차는 $1/\sqrt{N}$ 로 줄어든다.
대신 출력은 약 $(N-1)/2$ 샘플만큼 **늦는다**. 신호가 빠르게 변하면 평균이 따라가지 못한다.
메모리에 $N$ 개 샘플을 보관해야 한다는 점도 마이크로컨트롤러에서는 부담이다.

### 1차 저역통과(지수 이동 평균)

새 샘플과 이전 출력을 비율 $\alpha$ 로 섞는다. 상태 하나만 저장하면 되고, 시정수 $\tau$ 보다
느린 변화는 통과시키고 빠른 변화(노이즈)는 깎는다. $\alpha$ 가 1 에 가까울수록 매끄럽지만 느리다.
PID 의 미분 항에 붙이는 필터가 바로 이것이다.

### 상보 필터

IMU 로 기울기 $\theta$ 를 구하는 방법은 두 가지다.

- **자이로 적분:** 짧은 시간엔 정확하고 매끄럽지만 바이어스 때문에 **흘러간다**(저주파 오차).
- **가속도계:** 중력 방향으로 $\theta = \operatorname{atan2}(a_x, a_z)$ 를 바로 구한다. 흘러가지
  않지만 진동·운동 가속도 때문에 **떨린다**(고주파 오차).

두 오차가 서로 다른 주파수에 있으므로, 자이로 쪽은 고역통과, 가속도계 쪽은 저역통과해서
더하면 된다. 두 필터의 합이 1 이 되도록(상보적으로) 고르면 실제 신호는 왜곡 없이 통과한다.
드론·밸런싱 로봇에서 지금도 널리 쓰는 방식이다.

## 핵심 수식

이동 평균: $y_k = \dfrac{1}{N}\sum_{i=0}^{N-1} x_{k-i}$

1차 저역통과(시정수 $\tau$, 샘플 주기 $\Delta t$):

$$y_k = \alpha\,y_{k-1} + (1-\alpha)\,x_k,\qquad \alpha = \frac{\tau}{\tau + \Delta t}$$

차단 주파수는 $f_c = 1/(2\pi\tau)$ 다.

상보 필터:

$$\hat\theta_k = \alpha\,(\hat\theta_{k-1} + \omega_k\,\Delta t) + (1-\alpha)\,\theta_{\text{acc},k}$$

괄호 안은 자이로로 한 스텝 **예측**, 뒤 항은 가속도계 **측정**이다. "예측과 측정을 비율로
섞는다"는 구조가 칼만 필터와 같고, 칼만 필터는 이 비율을 노이즈 분산으로부터 매 스텝 계산한다.

## 예제

실제 기울기 $\theta(t) = 0.5\sin(0.5t)$ 를 따라가는 IMU 를 시뮬레이션한다. 자이로에는
$0.02$ rad/s 바이어스, 가속도계 각도에는 $\sigma = 0.1$ rad 잡음을 넣는다.

```python
import numpy as np

rng = np.random.default_rng(1)
dt = 0.01
t = np.arange(0, 10, dt)
theta = 0.5 * np.sin(0.5 * t)  # 실제 기울기 [rad]
omega = 0.25 * np.cos(0.5 * t)  # 실제 각속도 [rad/s]

gyro = omega + 0.02 + rng.normal(0, 0.02, t.size)  # 바이어스 + 잡음
acc_angle = theta + rng.normal(0, 0.1, t.size)  # 가속도계로 구한 각도


def moving_average(x, n):
    c = np.cumsum(np.insert(x, 0, 0.0))
    y = np.empty_like(x)
    y[n - 1 :] = (c[n:] - c[:-n]) / n
    y[: n - 1] = c[1:n] / np.arange(1, n)  # 시작 구간은 있는 만큼만 평균
    return y


def low_pass(x, tau, dt):
    a = tau / (tau + dt)
    y = np.empty_like(x)
    y[0] = x[0]
    for k in range(1, x.size):
        y[k] = a * y[k - 1] + (1 - a) * x[k]
    return y


def complementary(gyro, acc_angle, tau, dt):
    a = tau / (tau + dt)
    est = np.empty_like(gyro)
    est[0] = acc_angle[0]
    for k in range(1, gyro.size):
        est[k] = a * (est[k - 1] + gyro[k] * dt) + (1 - a) * acc_angle[k]
    return est


def rms(e):
    return np.sqrt(np.mean(e**2))


estimates = {
    "가속도계 원신호": acc_angle,
    "자이로 적분": np.cumsum(gyro) * dt,
    "이동 평균(25)": moving_average(acc_angle, 25),
    "저역통과(0.2 s)": low_pass(acc_angle, 0.2, dt),
    "상보 필터(0.5 s)": complementary(gyro, acc_angle, 0.5, dt),
}
for name, est in estimates.items():
    print(f"{name:12s} RMS 오차 {np.rad2deg(rms(est - theta)):5.2f} deg")
```

결과는 대략 원신호 5.9°, 자이로 적분 6.3°(바이어스로 계속 증가), 이동 평균 1.7°,
저역통과 2.2°, 상보 필터 0.85° 다. 단일 센서 필터는 노이즈와 지연 사이에서 타협해야 하지만,
상보 필터는 두 센서의 장점을 모두 가져온다.

**연습 과제(exercise):** (1) 저역통과의 $\tau$ 를 0.05~1.0 s 로 바꿔 RMS 오차 곡선을 그리고
최적점이 생기는 이유를 설명하라. (2) $\theta(t)$ 와 각 추정을 겹쳐 그려 이동 평균의 지연을
눈으로 확인하라. (3) 상보 필터에서 $\tau$ 를 매우 크게/작게 하면 어떤 센서처럼 행동하는지 확인하라.

## 자가 점검 질문

1. 이동 평균 창 크기 $N$ 을 두 배로 늘리면 노이즈와 지연은 각각 어떻게 변하는가?
2. $\Delta t = 0.01$ s 에서 시정수 $\tau = 0.1$ s 인 저역통과의 $\alpha$ 와 차단 주파수는?
3. 상보 필터에서 자이로 항이 고역통과, 가속도계 항이 저역통과 역할을 한다는 말의 의미를 설명하라.

## 확인 퀴즈

`rc quiz m4-filtering-basics` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m4-filtering-basics-quiz
questions:
  - id: q1
    type: single
    prompt: '이동 평균의 창 크기 $N$ 을 두 배로 늘리면 백색 잡음과 지연은 각각 어떻게 변하는가?'
    choices:
      - '잡음 표준편차는 $1/2$ 배, 지연은 그대로'
      - '잡음 표준편차는 $1/\sqrt{2}$ 배, 지연은 약 두 배'
      - '잡음과 지연이 모두 두 배'
      - '잡음은 그대로, 지연만 두 배'
    answer: 1
    explanation: '독립 백색 잡음의 표준편차는 $1/\sqrt{N}$ 로 줄어들므로 $N$ 을 두 배로 하면 $1/\sqrt{2}$ 배가 된다. 지연은 약 $(N-1)/2$ 샘플이므로 거의 두 배로 늘어난다. 매끄러움과 반응 속도는 맞바꾸는 관계다.'
    concept: { front: '이동 평균의 $N$ 트레이드오프', back: '잡음은 $1/\sqrt{N}$ 로 감소, 지연은 약 $(N-1)/2$ 샘플로 증가' }
  - id: q2
    type: short
    prompt: '$\Delta t = 0.01$ s, 시정수 $\tau = 0.1$ s 인 1차 저역통과 필터의 $\alpha$ 값은? (소수 둘째 자리까지)'
    answer: ['0.91', '0.909', '10/11']
    explanation: '$\alpha = \tau / (\tau + \Delta t) = 0.1 / 0.11 \approx 0.909$ 다. 차단 주파수는 $f_c = 1/(2\pi\tau) \approx 1.6$ Hz 가 된다.'
  - id: q3
    type: truefalse
    prompt: '상보 필터에서 자이로 항은 저주파 성분, 가속도계 항은 고주파 성분을 담당한다.'
    answer: false
    explanation: '반대다. 자이로 적분은 짧은 시간(고주파)에 정확하고 저주파에서 흘러가므로 **고역통과**로 쓴다. 가속도계는 흘러가지 않지만 진동 때문에 떨리므로 **저역통과**로 쓴다. 두 가중치의 합이 1이면 실제 신호는 왜곡 없이 통과한다.'
    concept: { front: '상보 필터의 역할 분담', back: '자이로 = 고역통과(단기 정확, 장기 드리프트), 가속도계 = 저역통과(장기 안정, 단기 진동)' }
```

## 이 단계 공부법

1. **교재(먼저):** Labbe Ch. 1 의 g-h 필터 노트북을 실행하며 "예측 + 측정의 가중 평균" 구조를 익힌다.
2. **본문 + 예제:** 예제를 실행한 뒤 연습 과제 (1)로 $\tau$ 를 바꿔 가며 그래프를 그린다.
3. **문제:** 퀴즈에서 $\alpha$, $f_c$ 계산을 손으로 푼다.
4. **보강:** Correll 교재 센서 장에서 IMU 실제 특성을 읽고, 필터 주파수 직관이 부족하면
   MATLAB Tech Talks 를 참고한다.
5. **예습(선택):** *Probabilistic Robotics* 2–3장을 훑어 M5 칼만 필터로 연결한다.

## 참고 자료

- Roger Labbe, *Kalman and Bayesian Filters in Python*, Ch. 1 —
  <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
- Brian Douglas, MATLAB Tech Talks "Control Systems" — <https://mathworks.com/videos/tech-talks/controls>
- Nikolaus Correll 외, *Introduction to Autonomous Robots* — <https://introduction-to-autonomous-robots.github.io/>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, MIT Press —
  <https://robots.stanford.edu/probabilistic-robotics/>
