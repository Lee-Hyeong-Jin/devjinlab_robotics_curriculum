---
id: m6-local-planning-dwa-mppi
title: "지역 계획과 장애물 회피(DWA, MPPI 개요)"
summary: 전역 경로를 따라가면서 지금 보이는 장애물을 피하는 지역 계획(컨트롤러)을 다룬다. 속도 공간을 격자로 훑는 DWA 와, 무작위 제어 열을 굴려 비용 가중 평균을 내는 MPPI 를 같은 차동 구동 모델 위에 numpy 로 구현해 비교한다.
objectives:
  - 전역 계획과 지역 계획의 역할·주기·사용하는 비용 지도의 차이를 설명할 수 있다.
  - 동적 창(dynamic window)과 궤적 점수 함수로 DWA 를 구현하고, 점수 항의 가중치가 행동에 주는 영향을 설명할 수 있다.
  - MPPI 의 샘플링·비용 가중 평균·제어 열 이동(warm start) 과정을 설명하고 간단히 구현할 수 있다.
prerequisites: [m6-costmap-global-planning, m3-differential-drive, m3-path-following]
difficulty: 4
estimated_minutes: 140
tags: [local-planner, controller, dwa, mppi, obstacle-avoidance, nav2]
activities:
  - id: m6-local-planning-dwa-mppi-reading
    kind: reading
    title: 본문과 Nav2 컨트롤러 문서 읽기
    estimated_minutes: 45
  - id: m6-local-planning-dwa-mppi-quiz
    kind: quiz
    title: DWA·MPPI 비교 퀴즈
    estimated_minutes: 20
  - id: m6-local-planning-dwa-mppi-exercise
    kind: exercise
    title: 점수 가중치와 MPPI 온도 실험
    estimated_minutes: 75
resources:
  - title: "Nav2 Documentation"
    url: https://docs.nav2.org/rolling/index.html
    kind: article
    note: Navigation Concepts 의 컨트롤러 서버, Configuration Guide 의 DWB·MPPI·Regulated Pure Pursuit 컨트롤러 항목.
  - title: "PythonRobotics (Sakai)"
    url: https://atsushisakai.github.io/PythonRobotics/
    kind: other
    note: Path Planning 모듈의 Dynamic Window Approach 샘플 코드.
  - title: "Modern Robotics: Mechanics, Planning, and Control (Lynch, Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: Ch. 13 Wheeled Mobile Robots(운동 모델·제약) 복습.
  - title: "The Dynamic Window Approach to Collision Avoidance (Fox, Burgard, Thrun)"
    kind: article
    note: IEEE Robotics & Automation Magazine, 1997. DWA 원논문(링크 없음).
---

# 지역 계획과 장애물 회피(DWA, MPPI 개요)

전역 경로는 계산된 뒤 사람이 지나가거나 문이 닫히면 틀린 정보가 된다. **지역 계획(Nav2 의
컨트롤러)** 은 10–50 Hz 로 돌면서 로봇 주변의 지역 비용 지도만 보고 다음 속도 $(v, \omega)$ 를 정한다.
M3 의 경로 추종과 달리 장애물과 가속 한계까지 함께 본다.

## 개념

### DWA(Dynamic Window Approach)

1. **동적 창:** 현재 속도 $(v_0, \omega_0)$ 에서 한 제어 주기 $\Delta t$ 동안 가속 한계로 도달할 수
   있는 속도 범위만 후보로 둔다.
2. **전방 시뮬레이션:** 각 후보 속도를 일정하게 유지한다고 보고 M3 의 차동 구동 모델로 1–3 초 궤적을 만든다.
3. **점수:** 목표(또는 전역 경로) 접근, 장애물 여유, 속도를 가중합해 최고 점수 후보를 고른다.

단순하지만 일정 속도 궤적만 보므로 복잡한 기동은 표현하지 못한다. Nav2 의 DWB 컨트롤러가 이 계열이며,
점수 항을 "critic" 플러그인으로 조합한다.

### MPPI(Model Predictive Path Integral)

MPPI 는 모델 예측 제어(MPC)의 샘플링 버전이다. 지난 주기의 최적 제어 열을 평균으로 삼아 잡음을 더한
$K$ 개의 제어 열을 만들고, 모두 굴려(rollout) 비용을 매긴 뒤, 비용이 낮을수록 지수적으로 큰 가중치를
주어 평균 낸다. 첫 제어만 실행하고 열을 한 칸 밀어 다음 주기에 쓴다. 비용이 미분 가능할 필요가 없고
벡터화로 수천 개 샘플을 돌릴 수 있다. Nav2 에도 MPPI 컨트롤러가 있다.

## 핵심 수식

DWA 의 동적 창과 점수:

$$V_d = [v_0 - \dot v_{max}\Delta t,\ v_0 + \dot v_{max}\Delta t] \times [\omega_0 - \dot\omega_{max}\Delta t,\ \omega_0 + \dot\omega_{max}\Delta t]$$

$$(v, \omega)^{\star} = \arg\max_{(v,\omega) \in V_d} \big[\alpha\,\text{heading} + \beta\,\text{clearance} + \gamma\,v\big]$$

MPPI 의 가중 평균($S_k$ 는 $k$ 번째 rollout 의 비용, $\lambda$ 는 온도):

$$w_k = \frac{\exp\!\big(-(S_k - \min_j S_j)/\lambda\big)}{\sum_i \exp\!\big(-(S_i - \min_j S_j)/\lambda\big)},\qquad u_t \leftarrow \sum_k w_k\, u_t^{(k)}$$

## 예제

점 장애물 네 개를 지나 (6, 0) 으로 가는 차동 구동 로봇. 두 방법이 `rollout`, `traj_cost` 를
공유한다(점수 최대화 대신 비용 최소화).

```python
import numpy as np

rng = np.random.default_rng(0)
obstacles = np.array([[2.0, 0.1], [3.0, -0.4], [3.2, 0.6], [4.5, 0.0]])  # 점 장애물 [m]
goal = np.array([6.0, 0.0])
DT, HORIZON = 0.1, 15  # 0.1 s 간격으로 1.5 s 앞을 본다
V_MAX, W_MAX, A_MAX, AW_MAX, RADIUS = 0.6, 1.5, 1.0, 3.0, 0.25


def rollout(state, controls):
    """(K, T, 2) 제어 열 → (K, T, 3) 궤적. 차동 구동 모델."""
    x = np.repeat(state[None, :3], len(controls), axis=0)
    traj = []
    for t in range(controls.shape[1]):
        v, w = controls[:, t, 0], controls[:, t, 1]
        x = x + DT * np.c_[v * np.cos(x[:, 2]), v * np.sin(x[:, 2]), w]
        traj.append(x)
    return np.stack(traj, axis=1)


def traj_cost(traj, controls):
    d = np.linalg.norm(traj[:, :, None, :2] - obstacles[None, None], axis=3).min(axis=(1, 2))
    to_goal = np.linalg.norm(traj[:, -1, :2] - goal, axis=1)
    collide = np.where(d < RADIUS, 1e6, 0.0)
    return 1.0 * to_goal + 0.3 / np.maximum(d, 1e-3) - 0.2 * controls[:, -1, 0] + collide


def dwa(state):
    v0, w0 = state[3], state[4]  # 동적 창: 한 주기 안에 낼 수 있는 속도만 후보로
    vs = np.linspace(max(0.0, v0 - A_MAX * DT), min(V_MAX, v0 + A_MAX * DT), 7)
    ws = np.linspace(max(-W_MAX, w0 - AW_MAX * DT), min(W_MAX, w0 + AW_MAX * DT), 15)
    cand = np.array([(v, w) for v in vs for w in ws])
    controls = np.repeat(cand[:, None, :], HORIZON, axis=1)  # 창 안에서 일정 속도 유지
    return cand[np.argmin(traj_cost(rollout(state, controls), controls))]


mean_seq = np.zeros((HORIZON, 2))


def mppi(state, K=256, lam=0.1, sigma=(0.2, 0.6)):
    global mean_seq
    noise = rng.normal(0, sigma, (K, HORIZON, 2))
    controls = np.clip(mean_seq + noise, [0, -W_MAX], [V_MAX, W_MAX])
    cost = traj_cost(rollout(state, controls), controls)
    w = np.exp(-(cost - cost.min()) / lam)  # 비용이 낮은 샘플일수록 큰 가중치
    mean_seq = np.einsum("k,ktc->tc", w / w.sum(), controls)
    u = mean_seq[0].copy()
    mean_seq = np.vstack([mean_seq[1:], mean_seq[-1:]])  # 다음 주기용으로 한 칸 민다
    return u


for name, controller in [("DWA", dwa), ("MPPI", mppi)]:
    state = np.array([0.0, 0.0, 0.0, 0.0, 0.0])  # x, y, θ, v, ω
    min_clear = np.inf
    elapsed = 0.0
    while elapsed < 30.0:  # 최대 30 s
        v, w = controller(state)
        x, y, th = rollout(state, np.array([[[v, w]]]))[0, 0]
        state = np.array([x, y, th, v, w])
        elapsed += DT
        min_clear = min(min_clear, np.linalg.norm(obstacles - state[:2], axis=1).min())
        if np.linalg.norm(state[:2] - goal) < 0.15:
            break
    reached = np.linalg.norm(state[:2] - goal) < 0.15
    print(
        f"{name:4s} {'도착' if reached else '실패'} {elapsed:4.1f} s, "
        f"최종 위치 {np.round(state[:2], 2)}, 최소 장애물 거리 {min_clear:.2f} m"
    )
```

DWA 는 약 11.8 s, MPPI 는 약 16 s 만에 도착하고, 둘 다 반경 0.25 m 보다 넓은 여유를 둔다.

**연습 과제(exercise):** (1) `traj_cost` 의 장애물 항 계수 0.3 을 0.05, 1.0 으로 바꿔 두 방법의 여유와
도착 시간을 비교하라. (2) MPPI 의 `lam` 을 0.02–1.0 으로 바꾸며 성공·실패를 기록하라.

## 자가 점검 질문

1. 지역 계획이 전역 비용 지도 대신 로봇을 따라다니는 작은 지역 비용 지도를 쓰는 이유는?
2. DWA 의 동적 창이 없다면(모든 속도를 후보로 두면) 어떤 문제가 생기는가?
3. MPPI 에서 온도 $\lambda$ 가 0 에 가까울 때와 클 때 제어가 각각 어떻게 되는가?

## 이 단계 공부법

1. **본문 + 예제(먼저):** 예제를 돌리고 두 방법의 궤적을 겹쳐 그린다.
2. **코드 읽기:** PythonRobotics 의 DWA 코드와 예제의 `dwa` 를 비교해 점수 항을 대응시킨다.
3. **문서:** Nav2 Configuration Guide 의 DWB·MPPI critic 목록을 예제 `traj_cost` 의 항과 대응시킨다.
4. **심화(선택):** DWA·MPPI 원논문(참고 자료)으로 유도를 확인한다.

## 참고 자료

- Nav2 Documentation — <https://docs.nav2.org/rolling/index.html>
- Atsushi Sakai, PythonRobotics — <https://atsushisakai.github.io/PythonRobotics/>
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 13 — <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Dieter Fox, Wolfram Burgard, Sebastian Thrun, "The Dynamic Window Approach to Collision Avoidance", IEEE RAM 1997 (링크 없음)
- Grady Williams 외, "Information Theoretic MPC for Model-Based Reinforcement Learning", ICRA 2017 (MPPI, 링크 없음)
