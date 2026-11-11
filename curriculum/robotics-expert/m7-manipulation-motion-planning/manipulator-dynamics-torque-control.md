---
id: m7-manipulator-dynamics-torque-control
title: "매니퓰레이터 동역학 기초와 토크 제어"
summary: 라그랑지안으로 2-link 팔의 운동 방정식 $M(\theta)\ddot{\theta} + c(\theta,\dot{\theta}) + g(\theta) = \tau$ 를 세우고, 관성·코리올리·중력항의 역할을 확인한 뒤 PD, 중력 보상 PD, 계산 토크 제어의 추종 성능을 numpy 시뮬레이션으로 비교한다.
objectives:
  - 라그랑지안 $L = K - P$ 로부터 매니퓰레이터 운동 방정식을 유도하고 질량 행렬·코리올리/원심항·중력항을 구분할 수 있다.
  - 역동역학(토크 계산)과 순동역학(가속도 계산·적분)의 쓰임새를 구분하고 에너지 보존으로 시뮬레이터를 검증할 수 있다.
  - PD, 중력 보상 PD, 계산 토크(computed torque) 제어를 구현해 모델 정보가 추종 오차에 주는 영향을 설명할 수 있다.
prerequisites: [m7-jacobian-singularity, m3-pid-control]
difficulty: 4
estimated_minutes: 140
tags: [manipulator, dynamics, lagrangian, computed-torque, control]
activities:
  - id: m7-manipulator-dynamics-torque-control-reading
    kind: reading
    title: 본문과 Modern Robotics Ch. 8·11 영상
    estimated_minutes: 50
  - id: m7-manipulator-dynamics-torque-control-quiz
    kind: quiz
    title: 운동 방정식 항과 제어기 비교 퀴즈
    estimated_minutes: 20
  - id: m7-manipulator-dynamics-torque-control-exercise
    kind: exercise
    title: 2-link 동역학 시뮬레이터와 계산 토크 제어 구현
    estimated_minutes: 70
resources:
  - title: "Modern Robotics: Mechanics, Planning, and Control (Lynch, Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: Ch. 8 Dynamics of Open Chains(8.1 라그랑지안), Ch. 11 Robot Control(11.4 계산 토크).
  - title: "Modern Robotics Ch. 8 Dynamics 영상"
    url: https://www.youtube.com/playlist?list=PLggLP4f-rq00TQamz2pXjzPWpuxhVN_Vy
    kind: video
    note: Ch. 8, 10편 50:19.
  - title: "Modern Robotics Ch. 11 Robot Control 영상"
    url: https://www.youtube.com/playlist?list=PLggLP4f-rq02N54sD6xwdDWlDScvb32Pp
    kind: video
    note: Ch. 11, 13편 57:51.
  - title: "Coursera Modern Robotics Specialization"
    url: https://www.coursera.org/specializations/modernrobotics
    kind: course
    note: Course 3 Robot Dynamics(Ch. 8–9). 한국어판 modernrobotics-course3-ko. 청강 무료.
  - title: "Pinocchio practical exercises (ROS Jazzy package docs)"
    url: https://docs.ros.org/en/jazzy/p/pinocchio/doc/d-practical-exercises/4-dyn.html
    kind: article
    note: 연습 4 direct/inverse dynamics. 강체 동역학 라이브러리로 손 유도 결과를 검증(심화·선택).
---

# 매니퓰레이터 동역학 기초와 토크 제어

M3 의 PID 는 모델 없이 오차만 보고 제어했다. 매니퓰레이터는 자세에 따라 관성이 바뀌고, 관절끼리
힘을 주고받으며, 늘 중력을 버텨야 한다. 이 레슨은 그 효과를 식 하나로 정리하고 제어에 넣어 본다.

## 개념

### 라그랑지안 운동 방정식

$L = K - P$(운동 에너지 − 위치 에너지)에 오일러-라그랑주 방정식을 적용하면, 모든 개방 사슬 팔은
같은 꼴의 식이 된다.

- **질량 행렬 $M(\theta)$:** 대칭·양의 정부호이며 자세에 따라 바뀐다. 팔을 펴면 첫 관절의 관성이 커진다.
- **코리올리·원심항 $c(\theta, \dot{\theta})$:** 속도의 2차식. 빠를 때 관절끼리 밀고 당기는 효과다.
- **중력항 $g(\theta)$:** 정지해 있어도 필요한 토크. 저속에서 가장 큰 항이다.

**역동역학**은 원하는 $\ddot{\theta}$ 에 필요한 $\tau$ 를(제어기), **순동역학**은 $\tau$ 에서
$\ddot{\theta} = M^{-1}(\tau - c - g)$ 를 구해 적분한다(시뮬레이터). 6자유도 이상은 Pinocchio 같은
라이브러리가 $O(n)$ 재귀로 계산한다.

### 토크 제어 세 단계

1. **PD:** $\tau = K_p e + K_d \dot{e}$. 중력 때문에 정상 오차가 남는다.
2. **중력 보상 PD:** $g(\theta)$ 를 더한다. 정지 유지는 정확하지만 빠른 궤적에서는 오차가 남는다.
3. **계산 토크:** 모델로 비선형성을 지워 각 관절을 선형계 $\ddot{e} + K_d\dot{e} + K_p e = 0$ 으로 만든다.
   모델 오차는 PD 항이 흡수한다.

## 핵심 수식

$$M(\theta)\ddot{\theta} + c(\theta, \dot{\theta}) + g(\theta) = \tau$$

계산 토크 제어($\theta_d$ 는 기준 궤적, $e = \theta_d - \theta$):

$$\tau = M(\theta)\big(\ddot{\theta}_d + K_d \dot{e} + K_p e\big) + c(\theta, \dot{\theta}) + g(\theta)$$

## 예제

링크 끝에 점질량이 있는 2-link 팔이다. 에너지 보존으로 식을 검증한 뒤 세 제어기로 사인파를 추종한다.

```python
import numpy as np

L1, L2, M1, M2, G = 1.0, 0.8, 2.0, 1.0, 9.81  # 질량은 각 링크 끝의 점질량


def dynamics_terms(q, qd):
    c2, s2 = np.cos(q[1]), np.sin(q[1])
    M = np.array(
        [
            [M1 * L1**2 + M2 * (L1**2 + 2 * L1 * L2 * c2 + L2**2), M2 * (L1 * L2 * c2 + L2**2)],
            [M2 * (L1 * L2 * c2 + L2**2), M2 * L2**2],
        ]
    )
    h = M2 * L1 * L2 * s2
    c = np.array([-h * (2 * qd[0] * qd[1] + qd[1] ** 2), h * qd[0] ** 2])  # 코리올리·원심
    g = np.array(
        [
            (M1 + M2) * L1 * G * np.cos(q[0]) + M2 * L2 * G * np.cos(q[0] + q[1]),
            M2 * L2 * G * np.cos(q[0] + q[1]),
        ]
    )
    return M, c, g


def energy(q, qd):
    M, _, _ = dynamics_terms(q, qd)
    y1 = L1 * np.sin(q[0])
    y2 = y1 + L2 * np.sin(q[0] + q[1])
    return 0.5 * qd @ M @ qd + G * (M1 * y1 + M2 * y2)


def step(q, qd, tau, dt):
    """순동역학을 RK4 로 적분."""

    def f(x):
        M, c, g = dynamics_terms(x[:2], x[2:])
        return np.concatenate([x[2:], np.linalg.solve(M, tau - c - g)])

    x = np.concatenate([q, qd])
    k1 = f(x)
    k2 = f(x + dt / 2 * k1)
    k3 = f(x + dt / 2 * k2)
    k4 = f(x + dt * k3)
    x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return x[:2], x[2:]


# 1) 토크 0 이면 에너지 보존
q, qd, dt = np.array([0.3, 0.5]), np.zeros(2), 1e-3
E0 = energy(q, qd)
for _ in range(3000):
    q, qd = step(q, qd, np.zeros(2), dt)
print(f"3초 자유 운동 후 에너지 변화: {energy(q, qd) - E0:.2e} J")


# 2) 기준 궤적 추종
def ref(t, w=2.0):
    qr = np.array([0.5 + 0.5 * np.sin(w * t), 0.8 * np.cos(w * t)])
    qdr = np.array([0.5 * w * np.cos(w * t), -0.8 * w * np.sin(w * t)])
    qddr = np.array([-0.5 * w**2 * np.sin(w * t), -0.8 * w**2 * np.cos(w * t)])
    return qr, qdr, qddr


Kp, Kd = 100.0, 20.0  # 임계 감쇠: Kd = 2*sqrt(Kp)
for name in ["PD", "PD+중력", "계산 토크"]:
    q, qd = ref(0)[0].copy(), ref(0)[1].copy()
    errs = []
    for k in range(4000):
        qr, qdr, qddr = ref(k * dt)
        e, ed = qr - q, qdr - qd
        M, c, g = dynamics_terms(q, qd)
        if name == "PD":
            tau = Kp * e + Kd * ed
        elif name == "PD+중력":
            tau = Kp * e + Kd * ed + g
        else:
            tau = M @ (qddr + Kp * e + Kd * ed) + c + g
        q, qd = step(q, qd, tau, dt)
        errs.append(np.linalg.norm(e))
    print(f"{name:7s} 마지막 2초 최대 오차 {np.degrees(max(errs[2000:])):7.3f}°")
```

에너지 변화가 $10^{-10}$ J 수준이므로 $M, c, g$ 가 서로 맞다. 최대 추종 오차는 PD 약 26°, 중력 보상
PD 약 7°, 계산 토크 약 0.01° 다.

**연습 과제(exercise):** (1) 제어기 안의 `M2` 만 1.2 배로 틀리게 써서(모델 오차) 계산 토크의 오차를
보라. (2) `w` 를 1, 2, 4 로 바꿔 세 제어기의 오차 표를 만들어라.

## 자가 점검 질문

1. 팔을 펴고 접을 때 $M_{11}$ 의 변화를 식으로 설명하라.
2. 중력 보상 없는 PD 에 정상 오차가 남는 이유는?
3. 계산 토크 제어가 관절을 선형 2차계로 만드는 원리와 모델 오차 시의 한계를 설명하라.

## 확인 퀴즈

`rc quiz m7-manipulator-dynamics-torque-control` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m7-manipulator-dynamics-torque-control-quiz
questions:
  - id: q1
    type: single
    prompt: '중력 보상이 없는 PD 제어로 팔을 특정 자세에 유지하면 정상 오차가 남는 이유는?'
    choices:
      - '$K_p$ 가 너무 작게 설정되었기 때문'
      - '중력 토크를 버티려면 0 이 아닌 토크가 필요한데 PD 는 오차가 0 이면 토크도 0 이기 때문'
      - '질량 행렬이 자세에 따라 바뀌기 때문'
      - '코리올리 항이 정지 상태에서도 크기 때문'
    answer: 1
    explanation: '$\tau = K_p e + K_d\dot e$ 에서 $e = 0, \dot e = 0$ 이면 토크가 0 이다. 중력항 $g(\theta)$ 를 버틸 토크가 없으니 팔이 조금 처진 지점에서 균형을 이룬다. $g(\theta)$ 를 더해 주면(중력 보상 PD) 정지 유지가 정확해진다. M3 의 P 제어 정상 오차와 같은 구조다.'
    concept: { front: 'PD 만으로 정상 오차가 남는 이유', back: '오차 0 → 토크 0 인데 중력은 계속 작용. $g(\theta)$ 보상이 필요' }
  - id: q2
    type: single
    prompt: '2-link 팔을 쭉 펼 때 첫 관절의 유효 관성 $M_{11}$ 은?'
    choices:
      - '작아진다 — 질량이 축에 가까워진다'
      - '커진다 — 질량이 회전축에서 멀어져 관성 모멘트가 증가한다'
      - '변하지 않는다'
      - '음수가 될 수 있다'
    answer: 1
    explanation: '$M_{11}$ 에는 $2 m_2 l_1 l_{c2}\cos\theta_2$ 처럼 $\theta_2$ 에 의존하는 항이 있어, 펴면($\cos\theta_2 = 1$) 최대가 된다. 관성 모멘트는 거리의 제곱에 비례하므로 질량이 멀어질수록 같은 각가속도에 더 큰 토크가 필요하다.'
    concept: { front: '질량 행렬이 자세에 의존하는 이유', back: '관성은 거리² 에 비례 — 팔을 펴면 $M_{11}$ 증가, 접으면 감소' }
  - id: q3
    type: multiple
    prompt: '계산 토크 제어(computed torque)에 대해 옳은 설명을 모두 고르시오.'
    choices:
      - '모델로 $M$, $c$, $g$ 를 상쇄해 각 관절을 선형 2차계로 만든다'
      - '오차 방정식이 $\ddot e + K_d\dot e + K_p e = 0$ 이 되어 이득으로 응답을 직접 설계할 수 있다'
      - '모델 오차가 있으면 상쇄가 불완전해 PD 항이 그 잔차를 흡수해야 한다'
      - '모델이 정확하지 않아도 항상 PD 보다 안전하다'
    answer: [0, 1, 2]
    explanation: '$\tau = M(\ddot\theta_d + K_d\dot e + K_p e) + c + g$ 를 넣으면 비선형성이 지워지고 선형 오차 방정식이 남는다. 다만 질량·마찰 추정이 틀리면 상쇄가 불완전하고, 큰 모델 오차에서는 잘못된 보상이 오히려 불안정을 키울 수 있으므로 "항상 더 안전"하지는 않다.'
```

## 이 단계 공부법

1. **영상(먼저):** Modern Robotics Ch. 8 영상에서 라그랑지안 유도와 2-link 예를 본다.
2. **예제:** 한 항을 일부러 틀려 에너지가 새는지 본다.
3. **제어:** Ch. 11 영상의 계산 토크 부분을 본다.
4. **심화(선택):** Coursera Course 3 과제나 Pinocchio 연습 4로 6자유도 동역학을 계산해 본다.

## 참고 자료

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 8, 11 — <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics 영상 Ch. 8 <https://www.youtube.com/playlist?list=PLggLP4f-rq00TQamz2pXjzPWpuxhVN_Vy>, Ch. 11 <https://www.youtube.com/playlist?list=PLggLP4f-rq02N54sD6xwdDWlDScvb32Pp>
- Coursera Modern Robotics Specialization — <https://www.coursera.org/specializations/modernrobotics>
- Pinocchio 연습 4 — <https://docs.ros.org/en/jazzy/p/pinocchio/doc/d-practical-exercises/4-dyn.html>
