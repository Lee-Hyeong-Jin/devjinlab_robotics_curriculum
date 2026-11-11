---
id: m9-sim-to-real-domain-randomization
title: "시뮬레이션 기반 RL 과 sim-to-real(도메인 랜덤화)"
summary: 보행·조작 정책을 GPU 병렬 시뮬레이터에서 강화학습으로 훈련하고 실제 로봇으로 옮길 때 생기는 현실 격차(reality gap)의 원인과, 시스템 식별·도메인 랜덤화·sim2sim 검증 같은 대응법을 읽는다. 작은 numpy 예제로 공칭 시뮬레이터에 과적합된 정책과 랜덤화로 학습한 정책의 실제 성능을 비교한다.
objectives:
  - GPU 병렬 시뮬레이션이 PPO 기반 로봇 RL 의 표준 작업 흐름이 된 이유와 그 흐름(훈련→sim2sim→실기)을 설명할 수 있다.
  - 현실 격차의 주요 원인(동역학 파라미터, 작동기 지연·한계, 센서 노이즈, 시각 차이)을 구분하고 각각의 대응법을 고를 수 있다.
  - 도메인 랜덤화를 "파라미터 분포에 대한 기대 성능 최적화"로 정식화하고, 강건성과 공칭 성능의 맞교환을 예제로 설명할 수 있다.
prerequisites: [m9-reinforcement-learning-basics, m4-sensor-models]
difficulty: 4
estimated_minutes: 120
tags: [sim-to-real, domain-randomization, reality-gap, gpu-simulation, locomotion, system-identification]
activities:
  - id: m9-sim-to-real-domain-randomization-reading
    kind: reading
    title: 본문과 Isaac Lab·MuJoCo Playground 문서 읽기
    estimated_minutes: 50
  - id: m9-sim-to-real-domain-randomization-quiz
    kind: quiz
    title: 현실 격차 원인과 대응 퀴즈
    estimated_minutes: 20
  - id: m9-sim-to-real-domain-randomization-exercise
    kind: exercise
    title: 랜덤화 범위와 강건성 실험
    estimated_minutes: 50
resources:
  - title: "Robot Learning Fundamentals (NVIDIA Physical AI Learning)"
    url: https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/robot-learning-fundamentals/index.html
    kind: course
    note: >-
      무료 등록. 읽기 위주로. RL·PPO·보상 설계·sim-to-real 9개 레슨 중 08 Simulation to Reality 가
      이 레슨과 가장 가깝다. Isaac Lab 3.0 은 Newton 백엔드로 Isaac Sim 없이 실행되나 NVIDIA GPU(Turing+) 필요.
  - title: "Visual Domain Randomization (Isaac Lab, NVIDIA Physical AI Learning)"
    url: https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/transfer-policies-from-simulation-to-reality/03-bridging-the-gap-simulation-enhancement/01-visual-domain-randomization.html
    kind: article
    note: 조명·재질·카메라 랜덤화를 설정 파일에서 어떻게 지정하는지 보는 실습 단원.
  - title: "MuJoCo Playground"
    url: https://playground.mujoco.org/
    kind: other
    note: 1.0. CartpoleBalance 는 CPU 약 1분, G1 motion tracking, SO-101 sim-to-real 예제.
  - title: "unitree_rl_mjlab"
    url: https://github.com/unitreerobotics/unitree_rl_mjlab
    kind: other
    note: Go2·G1 평지 속도 추종 → policy.onnx → unitree_mujoco sim2sim 의 실제 작업 흐름 읽기.
  - title: "Sim-to-Real with SO-101 (NVIDIA Physical AI Learning)"
    url: https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/index.html
    kind: course
    note: 텔레오퍼레이션 도메인 랜덤화, 실데이터 co-training, Actuation Gap 모듈.
---

# 시뮬레이션 기반 RL 과 sim-to-real(도메인 랜덤화)

앞 레슨에서 PPO 는 표본 효율이 낮다고 했다. 실제 4족 로봇으로 수억 스텝을 모을 수는 없으니, 보행 정책은
거의 예외 없이 **시뮬레이터에서 훈련하고 실제 로봇으로 옮긴다(sim-to-real)**. 이 레슨은 그 작업 흐름과, 옮길 때
성능이 무너지는 이유를 다룬다. 시뮬레이터 실습은 이 플랫폼 범위 밖이므로 문서 읽기와 numpy 모형으로 대신한다.

## 개념

### GPU 병렬 시뮬레이션 작업 흐름

Isaac Lab, MuJoCo Playground, mjlab 은 GPU 한 장에서 수천 개 로봇을 동시에 시뮬레이션한다. 전형적 흐름은
(1) 관측·행동·보상을 정의한 과제(예: 속도 명령 추종)를 PPO 로 훈련 → (2) 정책을 ONNX 로 내보내 **다른
시뮬레이터에서 재검증(sim2sim)** → (3) 실기 배포다. unitree_rl_mjlab 은 학습 후 `unitree_mujoco` 에서 먼저
돌려 보라고 권한다. 서로 다른 물리 엔진에서도 버티는 정책이어야 현실에서도 버틸 가능성이 높다.

### 현실 격차(reality gap)의 원인

- **동역학:** 질량·관성·마찰·접촉 모델이 다르다.
- **작동기:** 모터 지연, 토크 한계, 기어 백래시. NVIDIA SO-101 과정이 따로 "Actuation Gap" 모듈을 둘 만큼 크다.
- **센서:** M4 에서 본 노이즈·편향·지연, 카메라 노출과 질감 차이.
- **제어 주기:** 시뮬레이터는 정확히 50 Hz 지만 실기는 흔들린다.

### 대응법

- **시스템 식별(system identification):** 실기 데이터로 시뮬레이터 파라미터를 맞춘다. 격차를 줄이는 정공법.
- **도메인 랜덤화(domain randomization):** 파라미터를 하나로 맞추는 대신 넓은 분포에서 매 에피소드 뽑아 훈련한다.
  정책은 "어느 세계에서든 통하는" 행동을 배우고, 현실은 그 분포의 한 표본이 되기를 기대한다. 시각 랜덤화는
  조명·질감·카메라 위치를 바꾼다.
- **관측 설계:** 지연·노이즈를 시뮬레이션에 넣고, 과거 관측 몇 스텝을 함께 넣어 정책이 숨은 파라미터를 추정하게 한다.
- **실데이터 혼합:** 시뮬레이션 데이터에 소량의 실기 시연을 섞어 학습한다(co-training).

## 핵심 수식

공칭 시뮬레이터 파라미터 $\xi_0$ 에 대한 최적화와 도메인 랜덤화 목표:

$$\theta_\text{nom} = \arg\max_\theta J(\theta; \xi_0),\qquad \theta_\text{DR} = \arg\max_\theta \mathbb{E}_{\xi \sim p(\xi)}\big[J(\theta; \xi)\big]$$

실기 파라미터 $\xi_\text{real}$ 이 $p(\xi)$ 의 지지 집합 안에 있으면 $\theta_\text{DR}$ 이 강건하다. 분포가 너무 넓으면 모든
세계에 대비하느라 보수적이 되어 공칭 성능을 잃는다.

## 예제

관절 하나를 PD 정책으로 0 에 보내는 문제에서 "학습"을 이득 격자 탐색으로 대신한다. 실제 로봇은 질량·지연·마찰이
시뮬레이터와 다르다.

```python
import numpy as np

# 1자유도 관절을 위치 0 으로 보내는 PD 정책 u = -kp·x - kd·v. "학습" = kp, kd 격자 탐색.
DT, STEPS = 0.01, 300
rng = np.random.default_rng(0)


def cost(kp, kd, mass, delay, friction):
    x, v = 1.0, 0.0
    buf = [0.0] * delay  # 작동기 지연: delay 스텝 전에 낸 명령이 지금 적용된다
    total = 0.0
    for _ in range(STEPS):
        buf.append(float(np.clip(-kp * x - kd * v, -200, 200)))  # 토크 한계
        u = buf.pop(0)
        v += DT * (u - friction * v) / mass
        x += DT * v
        total += DT * (x**2 + 1e-6 * u**2)
        if abs(x) > 10:
            return 1e3  # 발산
    return total


GAINS = [(kp, kd) for kp in (10, 30, 100, 300, 1000) for kd in (1, 3, 10, 30)]


def train(params_list):
    scores = [np.mean([cost(kp, kd, *p) for p in params_list]) for kp, kd in GAINS]
    return GAINS[int(np.argmin(scores))]


nominal = [(1.0, 0, 0.1)]  # 시뮬레이터 기본값: 질량 1 kg, 지연 0, 마찰 0.1
randomized = [
    (rng.uniform(0.5, 2.0), int(rng.integers(0, 6)), rng.uniform(0.0, 1.0)) for _ in range(30)
]
real = (1.6, 4, 0.6)  # "실제 로봇": 더 무겁고 40 ms 지연, 마찰도 크다(학습 때는 모름)

for name, params in [("공칭 시뮬", nominal), ("도메인 랜덤화", randomized)]:
    kp, kd = train(params)
    sim, real_cost = cost(kp, kd, *nominal[0]), cost(kp, kd, *real)
    print(f"{name}: kp={kp}, kd={kd} | 시뮬 비용 {sim:.3f}, 실제 비용 {real_cost:.3f}")
```

출력:

```text
공칭 시뮬: kp=1000, kd=30 | 시뮬 비용 0.052, 실제 비용 11.287
도메인 랜덤화: kp=100, kd=10 | 시뮬 비용 0.088, 실제 비용 0.169
```

공칭 시뮬레이터에서 고른 높은 이득은 시뮬레이터 안에서는 가장 빠르지만, 40 ms 지연이 있는 실기에서는 토크 한계
사이를 오가며 진동한다. 랜덤화로 고른 이득은 시뮬레이터에서 조금 느린 대신 실기에서 안정적이다.

**연습 과제(exercise):** (1) 랜덤화 범위에서 지연만 0 으로 고정하면 결과가 어떻게 되는지 보라. 어떤 격차 원인이
결정적이었나? (2) 질량 범위를 0.1–10 kg 으로 넓혀 지나친 랜덤화가 성능을 얼마나 깎는지 재라. (3) `real` 을 여러 개
뽑아 두 정책의 실패율을 비교하라.

## 자가 점검 질문

1. sim2sim 검증이 실기 배포 전에 잡아낼 수 있는 문제와 잡아낼 수 없는 문제를 하나씩 들어라.
2. 시스템 식별과 도메인 랜덤화는 서로 대체재인가, 보완재인가? 둘을 함께 쓰는 순서를 제안하라.
3. 랜덤화 분포를 넓힐수록 공칭 성능이 떨어지는 이유를 위 목표식으로 설명하라.

## 확인 퀴즈

`rc quiz m9-sim-to-real-domain-randomization` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m9-sim-to-real-domain-randomization-quiz
questions:
  - id: q1
    type: single
    prompt: 'sim2sim 검증(다른 물리 엔진에서 재실행)이 잡아낼 수 있는 문제와 잡아낼 수 없는 문제의 짝으로 알맞은 것은?'
    choices:
      - '잡아냄: 특정 엔진의 접촉·적분 방식에 과적합된 정책 / 못 잡음: 실제 모터 지연·백래시 같은 실기 고유 특성'
      - '잡아냄: 실제 센서 노이즈 / 못 잡음: 접촉 모델 과적합'
      - '둘 다 잡아낸다'
      - '둘 다 잡아내지 못한다'
    answer: 0
    explanation: '다른 엔진에서도 버티면 한 시뮬레이터의 수치적 특이점에 기대지 않는 정책임이 확인된다. 그러나 두 시뮬레이터 모두 갖지 못한 것(실제 작동기 지연, 기어 백래시, 제어 주기 흔들림, 실제 카메라 특성)은 잡아낼 수 없다.'
    concept: { front: 'sim2sim 검증의 범위', back: '엔진 과적합은 걸러내지만 실기 고유 특성(작동기 지연·백래시·주기 흔들림)은 못 잡는다' }
  - id: q2
    type: single
    prompt: '시스템 식별과 도메인 랜덤화의 관계로 가장 적절한 것은?'
    choices:
      - '보완재 — 먼저 식별로 분포의 중심을 실기에 맞추고, 그 주변을 랜덤화해 남은 불확실성을 덮는다'
      - '대체재 — 랜덤화를 쓰면 식별은 불필요하다'
      - '대체재 — 식별이 되면 랜덤화는 해롭다'
      - '둘은 무관한 기법이다'
    answer: 0
    explanation: '식별만 하면 남은 모델 오차에 취약하고, 랜덤화만 하면 중심이 실기에서 멀어 분포가 불필요하게 넓어진다. 실무 순서는 식별로 질량·마찰·지연의 중심값을 맞춘 뒤 그 주변으로 랜덤화하는 것이다.'
    concept: { front: '시스템 식별 + 도메인 랜덤화', back: '식별로 분포 중심을 맞추고 그 주변을 랜덤화 — 대체재가 아니라 보완재' }
  - id: q3
    type: single
    prompt: '랜덤화 분포를 넓힐수록 공칭(평균) 성능이 떨어지는 이유는?'
    choices:
      - '목표가 분포 전체에 대한 기대 성능이라, 넓은 분포에서 모두 통하는 보수적 행동을 고르게 되기 때문'
      - '학습 스텝이 부족해지기 때문'
      - '랜덤화가 보상 함수를 바꾸기 때문'
      - '넓은 분포에서는 정책이 수렴하지 않기 때문'
    answer: 0
    explanation: '$\max_\theta \mathbb{E}_{\xi \sim p(\xi)}[J(\theta, \xi)]$ 에서 $p$ 가 넓어지면 어떤 세계에서도 무너지지 않는 행동이 유리해진다. 한 세계에 특화된 공격적 행동은 평균을 깎으므로 버려진다. 강건성과 공칭 성능의 거래이고, 그래서 분포는 "필요한 만큼만" 넓힌다.'
    concept: { front: '랜덤화 폭과 성능의 거래', back: '넓으면 강건하지만 보수적(공칭 성능 하락) — 필요한 만큼만 넓힌다' }
```

## 이 단계 공부법

1. **문서(먼저):** NVIDIA "Robot Learning Fundamentals" 를 읽으며 과제·보상·랜덤화 설정이 어디에 있는지
   표시하고, 08 Simulation to Reality 와 Visual Domain Randomization 단원을 이어서 본다.
2. **본문 + 예제:** 예제와 연습 과제 (1) 로 어떤 격차가 결정적인지 찾는 습관을 들인다.
3. **코드 읽기:** unitree_rl_mjlab 의 속도 추종 과제에서 보상 항과 랜덤화 항목을 목록으로 뽑는다.
4. **확장(선택, GPU 필요):** MuJoCo Playground CartpoleBalance 를 CPU 로, 이후 SO-101 sim-to-real 과정을 읽는다.

## 참고 자료

- NVIDIA Physical AI Learning, "Robot Learning Fundamentals" —
  <https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/robot-learning-fundamentals/index.html>
- NVIDIA Physical AI Learning, "Visual Domain Randomization" —
  <https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/transfer-policies-from-simulation-to-reality/03-bridging-the-gap-simulation-enhancement/01-visual-domain-randomization.html>
- MuJoCo Playground — <https://playground.mujoco.org/>
- Unitree Robotics, unitree_rl_mjlab — <https://github.com/unitreerobotics/unitree_rl_mjlab>
- NVIDIA Physical AI Learning, "Sim-to-Real with SO-101" —
  <https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/index.html>
- Josh Tobin 외, "Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World" (IROS 2017)
