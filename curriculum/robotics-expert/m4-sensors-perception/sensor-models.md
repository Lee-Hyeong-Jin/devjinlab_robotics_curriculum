---
id: m4-sensor-models
title: 로봇 센서와 노이즈·관측 모델
summary: 인코더·IMU·거리 센서(LiDAR·초음파·깊이)의 측정 원리와 오차 원인을 정리하고, 측정을 "참값 + 노이즈"로 쓰는 관측 모델과 우도로 표현한다.
objectives:
  - 인코더·IMU·LiDAR 가 각각 무엇을 측정하고 어떤 오차(양자화, 바이어스, 백색 잡음, 이상치)를 갖는지 설명할 수 있다.
  - 측정을 z = h(x) + v 형태의 관측 모델로 쓰고, 가우시안 우도 p(z|x)를 계산할 수 있다.
  - 바이어스가 적분을 거치며 드리프트로 커지는 이유를 수식과 코드로 보일 수 있다.
prerequisites: [m1-coordinate-transforms, m3-differential-drive]
difficulty: 2
estimated_minutes: 90
tags: [sensors, encoder, imu, lidar, noise-model, observation-model]
activities:
  - id: m4-sensor-models-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 30
  - id: m4-sensor-models-quiz
    kind: quiz
    title: 센서별 오차 원인 퀴즈
    estimated_minutes: 15
  - id: m4-sensor-models-exercise
    kind: exercise
    title: 인코더·자이로·LiDAR 노이즈 시뮬레이션
    estimated_minutes: 45
resources:
  - title: "Cyrill Stachniss, Observation Models"
    url: https://www.youtube.com/watch?v=SfwxLpdFB-o
    kind: video
    note: Robotics 블록. 빔 모델과 우도 관점의 관측 모델. 먼저 본다.
  - title: "Cyrill Stachniss, Probability Primer"
    url: https://www.youtube.com/watch?v=JS5ndD8ans4
    kind: video
    note: Basics 블록. 가우시안·조건부 확률이 낯설면 먼저 본다.
  - title: "Kalman and Bayesian Filters in Python (Labbe)"
    url: https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python
    kind: book
    note: Ch. 1–3 (g-h 필터, 이산 베이즈, 가우시안). Jupyter 노트북.
  - title: "현직자가 알려주는 로보틱스 시스템 완전 해부 (인프런, jelly)"
    url: https://www.inflearn.com/course/a-complete-breakdown
    kind: course
    note: 17강 58분. 센서·모터드라이버·Serial/CAN/EtherCAT (한국어, 유료 29,700원, 선택).
  - title: awesome-2d-lidars
    url: https://github.com/kaiaai/awesome-2d-lidars
    kind: article
    note: ROS 지원 2D LiDAR 목록(LD19·RPLIDAR A1). 실제 사양표 읽기 연습용.
---

# 로봇 센서와 노이즈·관측 모델

M3 에서는 로봇이 자기 위치를 정확히 안다고 가정하고 제어기를 만들었다. 실제 로봇은 센서로만
세상을 본다. 그리고 모든 센서는 틀린다. 이 레슨은 기초 단계 마지막 모듈의 출발점으로, "센서가
무엇을, 얼마나 틀리게 재는가"를 수식으로 적는 법을 익힌다. 여기서 만든 노이즈 모델은 다음
레슨(필터링)과 중급 M5 의 베이즈·칼만 필터에서 그대로 입력이 된다.

## 개념

### 고유 감각 센서 vs 외부 감각 센서

- **고유 감각(proprioceptive):** 로봇 자신의 상태를 잰다. 바퀴 **인코더**(회전량), **IMU**
  (자이로 = 각속도, 가속도계 = 비력(specific force), 지자기계 = 방향).
- **외부 감각(exteroceptive):** 주변 환경을 잰다. **LiDAR**·초음파(거리), 카메라(밝기), 깊이 카메라.

고유 감각 센서는 빠르고 주변 환경에 영향을 덜 받지만 **적분하면 오차가 쌓인다**. 외부 감각
센서는 절대 기준(벽, 랜드마크)을 주지만 느리고 이상치가 많다. 둘을 섞는 것이 센서 융합의 동기다.

### 센서별 대표 오차

| 센서 | 원리 | 대표 오차 |
|---|---|---|
| 인코더 | 한 바퀴당 펄스 수(CPR) 계수 | 양자화, 바퀴 미끄러짐, 반지름 오차 |
| 자이로 | 코리올리 효과(MEMS) | 바이어스(시간에 따라 변함), 백색 잡음, 스케일 오차 |
| 가속도계 | 질량-스프링 변위 | 중력과 운동 가속도 구분 불가, 진동 잡음 |
| LiDAR | 빛의 비행 시간(ToF)·삼각측량 | 거리 비례 잡음, 반사 실패(최대값), 유리·검은 물체 |
| 초음파 | 음파 왕복 시간 | 넓은 빔 폭, 다중 반사 |

### 관측 모델

상태 $x$ (로봇 자세, 벽까지 거리 등)에서 센서가 이상적으로 내놓을 값을 $h(x)$ 라 하면,
측정은 $z = h(x) + v$ 다. $v$ 를 확률 변수로 두면 "이 측정이 이 상태에서 나올 확률",
즉 **우도** $p(z \mid x)$ 를 계산할 수 있다. 위치 추정은 결국 우도가 큰 $x$ 를 찾는 일이다.

LiDAR 처럼 이상치가 많은 센서는 하나의 가우시안으로 부족하다. **빔 모델**은 정상 반사(가우시안),
앞을 가린 물체(짧은 값), 반사 실패(최대 거리), 무작위 값의 혼합으로 측정 분포를 표현한다.

## 핵심 수식

가우시안 관측 모델과 우도:

$$z = h(x) + v,\quad v \sim \mathcal{N}(0, \sigma^2),\quad
p(z \mid x) = \frac{1}{\sqrt{2\pi}\,\sigma}\exp\!\left(-\frac{(z - h(x))^2}{2\sigma^2}\right)$$

인코더 분해능(바퀴 반지름 $r$): $\Delta s = 2\pi r / \text{CPR}$.

자이로 모델과 방향 오차(샘플 주기 $\Delta t$, 시간 $t$):

$$\omega_m = \omega + b + n,\quad n \sim \mathcal{N}(0, \sigma_n^2)
\;\Rightarrow\; e_\theta(t) \approx b\,t + \text{std}\;\sigma_n\sqrt{\Delta t\, t}$$

바이어스는 시간에 **선형으로**, 백색 잡음은 $\sqrt{t}$ 로 커진다(랜덤 워크).

빔 모델(가중치 합 = 1):

$$p(z \mid x) = w_\text{hit}\,p_\text{hit} + w_\text{short}\,p_\text{short}
+ w_\text{max}\,p_\text{max} + w_\text{rand}\,p_\text{rand}$$

## 예제

```python
import numpy as np

rng = np.random.default_rng(0)

# 1) 인코더: 1024 CPR, 바퀴 반지름 5 cm
cpr, r = 1024, 0.05
true_angle = 3.3  # rad
ticks = np.floor(true_angle / (2 * np.pi) * cpr)
meas_angle = ticks * 2 * np.pi / cpr
print(f"인코더 양자화 오차: {(true_angle - meas_angle) * r * 1000:.3f} mm")

# 2) 자이로: 정지 상태인데 바이어스 0.01 rad/s + 백색 잡음, 100 Hz 로 60초 적분
dt, n = 0.01, 6000
gyro = 0.01 + rng.normal(0.0, 0.05, n)
heading = np.cumsum(gyro) * dt
print(f"60초 후 방향 드리프트: {np.rad2deg(heading[-1]):.1f} deg")

# 3) LiDAR 빔 모델: 가우시안 + 짧은 이상치 + 최대 거리
z_true, sigma, z_max, m = 2.0, 0.02, 8.0, 200
z = rng.normal(z_true, sigma, m)
u = rng.random(m)
short = u < 0.05
z[short] = rng.uniform(0.0, z_true, short.sum())  # 앞을 가린 물체
z[(u >= 0.05) & (u < 0.08)] = z_max  # 반사 실패
print(f"평균 {z.mean():.3f} m, 중앙값 {np.median(z):.3f} m")


def likelihood(z, z_exp, sigma=0.02):
    return np.exp(-0.5 * ((z - z_exp) / sigma) ** 2) / (np.sqrt(2 * np.pi) * sigma)


print(f"p(z=2.01 | 2.00) = {likelihood(2.01, 2.0):.2f}")
print(f"p(z=2.01 | 2.10) = {likelihood(2.01, 2.1):.2e}")
```

출력에서 볼 것: 양자화 오차는 0.25 mm 로 작지만, 자이로는 60초 만에 약 34° 나 돌아간다
($0.01 \times 60 = 0.6$ rad). LiDAR 는 이상치 8% 때문에 평균이 2.2 m 로 틀리지만 중앙값은
거의 정확하다. 마지막 두 줄은 같은 측정이 "벽이 2.00 m" 가설을 "2.10 m" 가설보다 약 2만 배
더 지지한다는 뜻이다.

**연습 과제(exercise):** (1) 자이로 바이어스를 0 으로 두고 60초 드리프트를 100번 시뮬레이션해
표준편차가 $\sigma_n\sqrt{\Delta t\,t}$ 와 맞는지 확인하라. (2) LiDAR 측정 히스토그램을 그리고
빔 모델의 네 성분을 눈으로 찾아라. (3) awesome-2d-lidars 목록에서 LiDAR 하나를 골라 사양표의
거리 정확도·각 분해능을 $\sigma$ 로 옮겨 적어라.

## 자가 점검 질문

1. 인코더 오도메트리가 긴 주행에서 틀어지는 원인을 양자화 외에 두 가지 들어라.
2. 자이로의 바이어스와 백색 잡음은 적분 후 오차가 시간에 따라 각각 어떻게 커지는가?
3. LiDAR 측정에 이상치가 섞일 때 평균 대신 중앙값이나 빔 모델을 쓰는 이유는 무엇인가?

## 이 단계 공부법

1. **영상(먼저):** Stachniss *Probability Primer* 로 가우시안·조건부 확률을 복습한 뒤
   *Observation Models* 를 보고 빔 모델 그림을 노트에 따라 그린다.
2. **교재:** Labbe 노트북 Ch. 1–3 을 직접 실행하며 "측정 = 분포" 감각을 익힌다.
3. **본문 + 예제:** 예제를 실행하고 각 숫자가 핵심 수식과 맞는지 손으로 확인한다.
4. **문제:** 퀴즈 → 연습 과제 (1)~(3). 그래프를 반드시 그린다.
5. **보강(선택):** 실제 하드웨어 배선·통신이 궁금하면 인프런 강의를 본다.

## 참고 자료

- Cyrill Stachniss, "Observation Models" — <https://www.youtube.com/watch?v=SfwxLpdFB-o>
- Cyrill Stachniss, "Probability Primer" — <https://www.youtube.com/watch?v=JS5ndD8ans4>
- Roger Labbe, *Kalman and Bayesian Filters in Python*, Ch. 1–3 —
  <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
- 인프런, 현직자가 알려주는 로보틱스 시스템 완전 해부 — <https://www.inflearn.com/course/a-complete-breakdown>
- awesome-2d-lidars — <https://github.com/kaiaai/awesome-2d-lidars>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, 6장 Robot Perception (심화).
