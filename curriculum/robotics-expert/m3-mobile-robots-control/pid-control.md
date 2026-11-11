---
id: m3-pid-control
title: PID 제어
summary: 피드백 제어의 기본인 PID 제어기의 각 항이 하는 일을 이해하고, 이산 시간으로 구현해 이동 로봇의 방향 제어에 적용한다.
objectives:
  - 비례·적분·미분 항이 응답(상승 시간, 오버슈트, 정상 상태 오차)에 주는 영향을 설명할 수 있다.
  - 이산 시간 PID 를 구현하고 적분 와인드업과 미분 킥을 완화할 수 있다.
  - 차동 구동 로봇의 방향(heading) 제어 루프를 설계하고 게인을 단계적으로 조정할 수 있다.
prerequisites: [m3-differential-drive]
difficulty: 3
estimated_minutes: 90
tags: [control, pid, feedback]
activities:
  - id: m3-pid-control-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 30
  - id: m3-pid-control-quiz
    kind: quiz
    title: P·I·D 항의 효과 퀴즈
    estimated_minutes: 15
  - id: m3-pid-control-exercise
    kind: exercise
    title: 방향 제어 시뮬레이션에서 게인 조정과 와인드업 실험
    estimated_minutes: 45
resources:
  - title: "Brian Douglas / MATLAB Tech Talks: Control Systems"
    url: https://mathworks.com/videos/tech-talks/controls
    kind: video
    note: PID 와 피드백 제어 직관을 짧은 영상으로. 먼저 본다.
  - title: "Feedback Systems: An Introduction for Scientists and Engineers (Åström & Murray)"
    kind: book
    note: PID 제어 장(적분 와인드업, 게인 튜닝). 저자가 무료 온라인판을 공개하고 있다.
  - title: "Modern Robotics, 11장 Robot Control (Lynch & Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: 11.2–11.3절 오차 동역학과 PID 형태의 운동 제어.
  - title: QUT Robot Academy (Peter Corke)
    url: https://robotacademy.net.au/
    kind: course
    note: Dynamics & Control 분야의 관절 제어 강의(선택).
---

# PID 제어

지금까지는 "명령을 주면 그대로 움직인다" 고 가정했다. 실제 로봇은 마찰, 모터 지연, 바퀴
미끄러짐 때문에 명령과 결과가 다르다. **피드백 제어**는 측정값과 목표값의 차이(오차)를 보고
명령을 계속 고친다. PID 는 그중 가장 단순하면서 산업 현장의 대다수 제어 루프에 쓰이는 방식이다.
이 레슨에서 만든 제어기는 다음 레슨(경로 추종)의 핵심 부품이 된다.

## 개념

### 피드백 루프

목표(setpoint) $r(t)$, 측정값 $y(t)$, 오차 $e(t) = r(t) - y(t)$ 에서 제어 입력 $u(t)$ 를
계산해 대상(plant)에 넣고, 다시 측정한다. 이동 로봇 방향 제어라면 $r$ 은 목표 방향,
$y$ 는 현재 $\theta$, $u$ 는 각속도 명령 $\omega$ 다.

### 세 항의 역할

- **P (비례):** 현재 오차에 비례해 민다. $K_p$ 를 키우면 빨라지지만 오버슈트와 진동이 커진다.
  마찰·외란이 있으면 P 만으로는 **정상 상태 오차**가 남을 수 있다.
- **I (적분):** 과거 오차를 누적해 정상 상태 오차를 없앤다. 너무 크면 느린 진동을 만들고,
  액추에이터가 포화된 동안 적분이 계속 쌓이는 **적분 와인드업**이 생긴다.
- **D (미분):** 오차의 변화율에 반응해 "브레이크" 역할을 하므로 오버슈트를 줄인다. 대신
  센서 노이즈를 증폭하며, 목표가 계단처럼 바뀌면 순간적으로 큰 출력(**미분 킥**)이 생긴다.
  측정값의 미분 $-\dot{y}$ 를 쓰거나 저역 통과 필터를 붙여 완화한다.

### 각도 오차는 감아야 한다

방향 제어에서 목표 $179^\circ$, 현재 $-179^\circ$ 이면 실제 오차는 $-358^\circ$ 가 아니라
$+2^\circ$ 다. 오차를 항상 $(-\pi, \pi]$ 범위로 감아(wrap) 주어야 한다. 경로 추종에서도
반복해서 쓰는 처리다.

### 게인 조정의 실전 순서

1. $K_i = K_d = 0$ 에서 $K_p$ 를 올려 빠르지만 약간 진동하는 지점을 찾는다.
2. $K_d$ 를 더해 오버슈트를 줄인다.
3. 정상 상태 오차가 남을 때만 작은 $K_i$ 를 더하고, 출력 제한과 와인드업 방지를 함께 넣는다.

Ziegler–Nichols 같은 경험 규칙도 있지만, 시뮬레이션에서 응답을 그려 보며 조정하는 것이
학습에 가장 좋다.

## 핵심 수식

$$u(t) = K_p\,e(t) + K_i\int_0^t e(\tau)\,d\tau + K_d\,\frac{de(t)}{dt}$$

이산 시간(샘플 주기 $\Delta t$):

$$u_k = K_p e_k + K_i \sum_{j=0}^{k} e_j\,\Delta t + K_d\,\frac{e_k - e_{k-1}}{\Delta t}$$

각도 오차 감기:

$$e = \operatorname{atan2}\big(\sin(\theta_d - \theta),\ \cos(\theta_d - \theta)\big)$$

## 예제

차동 구동 로봇($\dot\theta = \omega$)의 방향을 $0$ 에서 $90^\circ$ 로 돌린다. 모터 한계로
$|\omega| \le 3$ rad/s 이고, 바닥 마찰 때문에 명령의 일부가 사라지는 일정한 외란
$d = -0.3$ rad/s 를 넣어 P 와 PI 의 차이를 본다.

```python
import numpy as np


def wrap(a):
    return np.arctan2(np.sin(a), np.cos(a))


class PID:
    def __init__(self, kp, ki, kd, dt, u_max):
        self.kp, self.ki, self.kd, self.dt, self.u_max = kp, ki, kd, dt, u_max
        self.integral, self.prev_y = 0.0, None

    def update(self, e, y):
        d_y = 0.0 if self.prev_y is None else wrap(y - self.prev_y) / self.dt
        self.prev_y = y
        u = self.kp * e + self.ki * self.integral - self.kd * d_y  # 측정값 미분
        u_sat = float(np.clip(u, -self.u_max, self.u_max))
        if u == u_sat:  # 포화 중에는 적분 중지 (anti-windup)
            self.integral += e * self.dt
        return u_sat


def run(kp, ki, kd, T=5.0, dt=0.01, disturbance=-0.3):
    ctrl, th, target = PID(kp, ki, kd, dt, u_max=3.0), 0.0, np.pi / 2
    for _ in range(int(T / dt)):
        w = ctrl.update(wrap(target - th), th)
        th += (w + disturbance) * dt
    return np.rad2deg(wrap(target - th))


print(f"P  only : {run(4, 0, 0):6.2f} deg 남음")  # 약 4.3 deg 정상 상태 오차
print(f"PI      : {run(4, 2, 0):6.2f} deg 남음")  # 1 deg 미만
print(f"PID     : {run(4, 2, 0.2):6.2f} deg 남음")  # 1 deg 미만 (5초 시점)
```

P 만 쓰면 $K_p e = 0.3$ 이 되는 지점, 즉 $e = 0.075$ rad $\approx 4.3^\circ$ 에서 멈춘다.
적분 항이 이 잔여 오차를 없앤다.

**연습 과제(exercise):** (1) 각 경우의 $\theta(t)$ 를 그려 상승 시간과 오버슈트를 비교하라.
(2) anti-windup 줄을 지우고 $K_i$ 를 키워 와인드업으로 인한 큰 오버슈트를 재현하라.
(3) 측정값에 표준편차 $1^\circ$ 의 노이즈를 더하고 $K_d$ 를 바꿔 가며 출력 $\omega$ 가 얼마나
떨리는지 관찰하라.

## 자가 점검 질문

1. P 제어만으로 정상 상태 오차가 남는 이유를 위 예제의 외란으로 설명하라.
2. 적분 와인드업은 어떤 조건에서 생기며, 이를 막는 방법 두 가지는 무엇인가?
3. 각도 오차를 감지 않으면 목표 $170^\circ$, 현재 $-170^\circ$ 에서 로봇은 어떻게 움직이는가?

## 확인 퀴즈

`rc quiz m3-pid-control` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m3-pid-control-quiz
questions:
  - id: q1
    type: single
    prompt: '마찰 같은 일정한 외란이 있을 때 P 제어만으로 정상 상태 오차가 남는 이유는?'
    choices:
      - '$K_p$ 가 음수이기 때문'
      - '오차가 0이면 제어 출력도 0이 되어 외란을 상쇄할 수 없기 때문'
      - 'P 항이 센서 노이즈를 증폭하기 때문'
      - '적분 와인드업이 생기기 때문'
    answer: 1
    explanation: '$u = K_p e$ 이므로 오차가 0이면 출력도 0이다. 외란을 버티려면 0이 아닌 출력이 필요하므로 오차가 조금 남은 지점에서 균형을 이룬다. 과거 오차를 누적하는 I 항이 이 남은 오차를 없애 준다.'
    concept: { front: 'P 제어의 정상 상태 오차', back: '오차 0 → 출력 0 이라 외란을 상쇄할 수 없다. I 항이 필요한 이유' }
  - id: q2
    type: multiple
    prompt: '적분 와인드업(integral windup)에 대해 옳은 설명을 모두 고르시오.'
    choices:
      - '액추에이터가 포화된 동안에도 적분이 계속 쌓여서 생긴다'
      - '적분 항에 상한·하한을 두어(클램핑) 막을 수 있다'
      - '포화 상태에서 적분 누적을 멈춰서(conditional integration) 막을 수 있다'
      - 'D 항의 게인을 키우면 근본적으로 막을 수 있다'
    answer: [0, 1, 2]
    explanation: '출력이 한계에 걸려 더 밀 수 없는데도 적분이 쌓이면, 목표에 도달한 뒤에도 쌓인 적분이 과도한 출력을 유지해 큰 오버슈트를 만든다. 적분 클램핑이나 포화 중 적분 중단이 표준 처방이고, D 항으로는 해결되지 않는다.'
    concept: { front: '적분 와인드업과 대처', back: '포화 중 적분 누적 → 오버슈트. 적분 클램핑 또는 포화 중 적분 중단' }
  - id: q3
    type: short
    prompt: '목표 $170^\circ$, 현재 $-170^\circ$ 일 때 올바르게 감은 각도 오차는 몇 도인가? (부호 포함, 숫자만)'
    answer: ['-20', '-20도', '-20deg']
    explanation: '$170 - (-170) = 340^\circ$ 를 $(-180^\circ, 180^\circ]$ 로 감으면 $-20^\circ$ 다. 감지 않으면 로봇이 짧은 쪽 $20^\circ$ 가 아니라 긴 쪽으로 $340^\circ$ 를 돌려고 한다.'
```

## 이 단계 공부법

1. **영상(먼저):** MATLAB Tech Talks 의 Brian Douglas 제어 강의에서 PID 소개 영상들을 보고
   P·I·D 각 항의 직관을 잡는다.
2. **교재:** Åström & Murray *Feedback Systems* 의 PID 제어 장에서 적분 와인드업과 튜닝
   부분을 읽는다. 로봇 관점의 정리는 Modern Robotics 11장 11.2–11.3절로 보완한다.
3. **본문 + 예제:** 예제를 실행하고 P / PI / PID 결과 숫자를 직접 확인한다.
4. **문제:** 확인 퀴즈 → 연습 과제 (1)~(3) 순으로 푼다. 그래프를 반드시 그려 볼 것.
5. **보강(선택):** QUT Robot Academy 의 관절 제어 강의로 모터 수준 PID 를 살펴본다.

## 참고 자료

- Brian Douglas, MATLAB Tech Talks "Control Systems" — <https://mathworks.com/videos/tech-talks/controls>
- Karl J. Åström, Richard M. Murray, *Feedback Systems: An Introduction for Scientists and
  Engineers*, Princeton University Press — PID 제어 장.
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, 11장 "Robot Control" —
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- QUT Robot Academy (Peter Corke) — <https://robotacademy.net.au/>
