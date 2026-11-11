---
id: m7-trajectory-generation
title: "궤적 생성: 관절·작업 공간 보간과 시간 최적화"
summary: 경로와 시간 스케일링을 분리해 3차·5차 다항식과 사다리꼴 속도 프로파일로 매니퓰레이터 궤적을 만들고, 속도·가속도 제한 아래 최소 시간을 구하며, 관절 공간 보간과 작업 공간 직선 보간의 차이를 numpy 로 비교한다.
objectives:
  - 궤적을 경로 $\theta(s)$ 와 시간 스케일링 $s(t)$ 로 나누고, 3차·5차 다항식의 경계 조건과 최대 속도·가속도를 계산할 수 있다.
  - 관절별 속도·가속도 제한에서 최소 이동 시간을 구하고, 여러 관절을 동기화하는 방법을 설명할 수 있다.
  - 관절 공간 보간과 작업 공간(직교 좌표) 보간의 장단점을 말단 경로와 관절 움직임으로 비교할 수 있다.
prerequisites: [m7-jacobian-singularity, m6-path-smoothing-trajectory]
difficulty: 3
estimated_minutes: 110
tags: [manipulator, trajectory, time-scaling, polynomial, interpolation]
activities:
  - id: m7-trajectory-generation-reading
    kind: reading
    title: 본문과 Modern Robotics Ch. 9 읽기
    estimated_minutes: 40
  - id: m7-trajectory-generation-quiz
    kind: quiz
    title: 시간 스케일링·보간 공간 비교 퀴즈
    estimated_minutes: 15
  - id: m7-trajectory-generation-exercise
    kind: exercise
    title: 3차·5차·사다리꼴 궤적과 작업 공간 보간 구현
    estimated_minutes: 55
resources:
  - title: "Modern Robotics: Mechanics, Planning, and Control (Lynch, Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: Ch. 9 Trajectory Generation(9.2 점대점 궤적, 9.3 다항식 경유점, 9.4 시간 최적 시간 스케일링).
  - title: "Modern Robotics 강의 영상"
    url: https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos
    kind: video
    note: Ch. 9 재생목록.
  - title: "Coursera Modern Robotics Specialization"
    url: https://www.coursera.org/specializations/modernrobotics
    kind: course
    note: Course 3 Robot Dynamics 의 Ch. 9 궤적 생성 과제.
  - title: "Robotics Toolbox for Python (Corke)"
    url: https://github.com/petercorke/robotics-toolbox-python
    kind: other
    note: "`jtraj`(관절 공간 5차)·`ctraj`(직교 좌표) 궤적 함수와 결과 비교(선택)."
---

# 궤적 생성: 관절·작업 공간 보간과 시간 최적화

M6 에서 "경로(시간 없음)"와 "궤적(시간 포함)"을 구분했다. 매니퓰레이터도 관절 값의 열에 한계를 넘지
않는 시간을 붙여야 움직일 수 있다. 결과물은 앞 레슨의 계산 토크 제어기가 받는 기준 궤적
$\theta_d(t), \dot{\theta}_d(t), \ddot{\theta}_d(t)$ 다.

## 개념

### 경로와 시간 스케일링의 분리

점대점 이동은 $\theta(s) = \theta_a + s(\theta_b - \theta_a)$, $s \in [0, 1]$ 로 경로를 정하고, 시간 스케일링
$s(t)$ 로 속도를 정한다. 그러면 $\dot{\theta} = \dot{s}(\theta_b - \theta_a)$ 이므로 모든 관절이 같은 비율로
동시에 출발해 동시에 도착한다(관절 동기화).

- **3차 다항식:** 양 끝 속도 0. 끝점 가속도가 0 이 아니라 출발·정지 순간 토크가 튄다.
- **5차 다항식:** 양 끝 속도·가속도 0. 진동이 적지만 같은 시간이면 최대 속도가 크다.
- **사다리꼴 속도:** 최대 가속 → 등속 → 최대 감속. 한계 안에서 가장 빠르지만 가속도가 불연속이라
  실제로는 S-커브(저크 제한)로 다듬는다.

### 시간 최적화

모든 관절이 한계 안에 드는 가장 짧은 $T$ 를 고른다. 한계 대비 이동량이 가장 큰 관절이 시간을 정하고,
나머지는 동기화를 위해 천천히 움직인다. 경유점이 많은 경로 전체의 최소 시간 매개화는 Modern Robotics
9.4 절의 위상 평면($s, \dot{s}$) 방법으로 풀며, MoveIt 2 의 TOTG 가 이 계열이다.

### 관절 공간 vs 작업 공간

- **관절 공간 보간:** 계산이 싸고 관절 한계·특이점 문제가 없다. 말단 경로는 곡선이 된다.
- **작업 공간 보간:** 말단이 직선(서랍 당기기, 용접)을 따른다. 매 점 IK 가 필요하고, 특이점을 지나면
  관절 속도가 폭주한다(레슨 1).

## 핵심 수식

3차·5차 시간 스케일링($\tau = t/T$)과 최대값:

$$s_3 = 3\tau^2 - 2\tau^3,\quad \max\dot{\theta} = \tfrac{3}{2}\tfrac{\Delta}{T},\quad \max\ddot{\theta} = 6\tfrac{\Delta}{T^2}$$

$$s_5 = 10\tau^3 - 15\tau^4 + 6\tau^5,\quad \max\dot{\theta} = \tfrac{15}{8}\tfrac{\Delta}{T},\quad \max\ddot{\theta} = \tfrac{10}{\sqrt{3}}\tfrac{\Delta}{T^2}$$

사다리꼴 최소 시간($\Delta > v_{max}^2 / a_{max}$ 일 때): $T = \Delta / v_{max} + v_{max} / a_{max}$.

## 예제

```python
import numpy as np


def cubic(tau):
    """3차 시간 스케일링 s(τ), τ = t/T ∈ [0, 1]. 양 끝 속도 0."""
    return 3 * tau**2 - 2 * tau**3, 6 * tau - 6 * tau**2, 6 - 12 * tau


def quintic(tau):
    """5차 시간 스케일링. 양 끝 속도·가속도 0."""
    s = 10 * tau**3 - 15 * tau**4 + 6 * tau**5
    sd = 30 * tau**2 - 60 * tau**3 + 30 * tau**4
    sdd = 60 * tau - 180 * tau**2 + 120 * tau**3
    return s, sd, sdd


tau = np.linspace(0, 1, 2001)
for name, fn in [("cubic", cubic), ("quintic", quintic)]:
    s, sd, sdd = fn(tau)
    print(
        f"{name:7s} a(0)={sdd[0]:.0f}  최대 v·T/Δ={sd.max():.3f}  최대 a·T²/Δ={np.abs(sdd).max():.3f}"
    )

# 1) 시간 최적화: 관절 이동량 Δ 와 한계 vmax, amax 에서 가능한 최소 시간 T
delta = np.array([1.2, -0.6, 2.0])  # 3관절 이동량 [rad]
vmax, amax = 1.0, 2.0  # rad/s, rad/s²
d = np.abs(delta).max()  # 가장 많이 움직이는 관절이 시간을 정한다
for name, kv, ka in [("cubic", 1.5, 6.0), ("quintic", 1.875, 10 / np.sqrt(3))]:
    T = max(kv * d / vmax, np.sqrt(ka * d / amax))
    print(f"{name:7s} 최소 T = {T:.2f} s")
T_trap = d / vmax + vmax / amax if d > vmax**2 / amax else 2 * np.sqrt(d / amax)
print(f"사다리꼴 최소 T = {T_trap:.2f} s")

# 2) 관절 공간 vs 작업 공간 직선 보간
L1, L2 = 1.0, 0.8


def fk(q):
    return np.array(
        [L1 * np.cos(q[0]) + L2 * np.cos(q[0] + q[1]), L1 * np.sin(q[0]) + L2 * np.sin(q[0] + q[1])]
    )


def ik(p):  # elbow-down 해석적 IK (M2)
    c2 = (p @ p - L1**2 - L2**2) / (2 * L1 * L2)
    q2 = np.arccos(np.clip(c2, -1, 1))
    q1 = np.arctan2(p[1], p[0]) - np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
    return np.array([q1, q2])


pa, pb = np.array([1.4, -0.4]), np.array([0.4, 1.2])
qa, qb = ik(pa), ik(pb)
s = quintic(np.linspace(0, 1, 101))[0]
u = (pb - pa) / np.linalg.norm(pb - pa)  # 직선 방향 단위벡터


def dist_to_line(p):
    r = p - pa
    return np.linalg.norm(r - (r @ u) * u)


dev_joint = max(dist_to_line(fk(qa + si * (qb - qa))) for si in s)
q_task = [ik(pa + si * (pb - pa)) for si in s]
len_task = np.abs(np.diff(q_task, axis=0)).sum(axis=0)
print(f"관절 공간: 직선 이탈 {dev_joint * 100:.1f} cm, 관절 이동량 {np.abs(qb - qa).round(2)}")
print(f"작업 공간: 직선 그대로, 관절 이동량 {len_task.round(2)}")
```

5차는 최대 속도가 3차보다 25% 커서 최소 시간이 3차 3.00 s, 5차 3.75 s, 사다리꼴 2.50 s 로 매끄러울수록
느리다. 관절 공간 보간은 말단이 직선에서 약 39 cm 벗어나고, 작업 공간 보간은 직선을 지키는 대신
팔을 접었다 펴느라 둘째 관절 이동량이 0.33 → 1.17 rad 로 늘어난다.

**연습 과제(exercise):** (1) 예제 1의 3관절 5차 궤적이 한계 안에 드는지 확인하라. (2) 사다리꼴 $s(t)$ 를
삼각형 경우까지 구현하라. (3) 작업 공간 직선이 원점 근처를 지나도록 `pb` 를 바꾸고 관절 속도를 관찰하라.

## 자가 점검 질문

1. 5차 다항식이 3차보다 선호되는 이유와 그 대가는?
2. 관절마다 이동량이 다를 때 전체 시간은 어떻게 정해지는가?
3. 작업 공간 직선 보간이 더 위험할 수 있는 두 상황을 써라.

## 이 단계 공부법

1. **교재(먼저):** Modern Robotics Ch. 9.1–9.2 로 경로·시간 스케일링 분리를 정리한다.
2. **본문 + 예제:** 표의 계수 1.5, 1.875, 6, 5.77 을 직접 유도해 코드와 맞춰 본다.
3. **영상:** Ch. 9 영상에서 경유점 다항식과 시간 최적 스케일링(9.4)을 본다.
4. **검증(선택):** Robotics Toolbox 의 `jtraj`·`ctraj` 결과를 예제와 비교한다.

## 참고 자료

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 9 — <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics 강의 영상 — <https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos>
- Coursera Modern Robotics Specialization — <https://www.coursera.org/specializations/modernrobotics>
- Peter Corke, Robotics Toolbox for Python — <https://github.com/petercorke/robotics-toolbox-python>
- Tobias Kunz, Mike Stilman, "Time-Optimal Trajectory Generation for Path Following with Bounded Acceleration and Velocity", RSS 2012 (TOTG 원논문, 링크 없음)
