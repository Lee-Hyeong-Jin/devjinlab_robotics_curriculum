---
id: m9-reinforcement-learning-basics
title: "강화학습 기초(Q-learning, 정책 경사, PPO 개요)"
summary: 전이 확률을 모른 채 경험만으로 MDP 를 푸는 강화학습을 가치 기반(TD·Q-learning)과 정책 기반(REINFORCE·actor-critic·PPO)으로 나눠 정리한다. 앞 레슨의 격자 세계를 표 형식 Q-learning 으로 풀어 가치 반복 결과와 비교한다.
objectives:
  - 모델 기반 계획(가치 반복)과 모델 없는(model-free) 강화학습의 차이를 설명하고, TD 오차와 Q-learning 갱신식을 쓸 수 있다.
  - ε-greedy 탐험을 포함한 표 형식 Q-learning 을 구현하고, 탐험 부족이 학습된 정책에 주는 영향을 진단할 수 있다.
  - 정책 경사 정리, 기준선(baseline)·어드밴티지, PPO 의 클리핑 목표가 각각 어떤 문제를 해결하는지 설명할 수 있다.
prerequisites: [m9-mdp-decision-making, m9-robot-learning-overview]
difficulty: 4
estimated_minutes: 150
tags: [reinforcement-learning, q-learning, td-learning, policy-gradient, actor-critic, ppo]
activities:
  - id: m9-reinforcement-learning-basics-reading
    kind: reading
    title: 본문과 CS 285 정책 경사·Q-learning 강의
    estimated_minutes: 60
  - id: m9-reinforcement-learning-basics-quiz
    kind: quiz
    title: TD·정책 경사·PPO 퀴즈
    estimated_minutes: 20
  - id: m9-reinforcement-learning-basics-exercise
    kind: exercise
    title: 표 형식 Q-learning 과 탐험 실험
    estimated_minutes: 70
resources:
  - title: "Berkeley CS 285 Deep Reinforcement Learning"
    url: https://rail.eecs.berkeley.edu/deeprlcourse/
    kind: course
    note: Fall 2023 YouTube 강의 + HW2 Policy Gradients·HW3 Q-Learning/Actor-Critic. Spring 2026 개설.
  - title: "DeepMind x UCL RL Lecture Series 2021"
    url: https://discuss.ai.google.dev/t/deepminds-reinforcement-learning-lecture-series-2021/29496
    kind: video
    note: 13편. Lecture 1 Introduction to RL 부터 MDP·동적 계획·model-free 예측/제어 순서로.
  - title: "Underactuated Robotics (Tedrake)"
    url: https://underactuated.mit.edu/
    kind: book
    note: Ch. 20 Model-Free Policy Search(로봇 관점의 RL 장).
  - title: "CleanRL"
    url: https://github.com/vwxyzjn/cleanrl
    kind: other
    note: 알고리즘 하나를 파일 하나로 구현(PPO·DQN·SAC). 2026 기준 Spinning Up 대신 구현 참고용.
---

# 강화학습 기초(Q-learning, 정책 경사, PPO 개요)

앞 레슨의 가치 반복은 전이 확률 $P(s' \mid s, a)$ 를 알고 있었다. 실제 로봇은 그 표를 주지 않는다.
대신 행동해 보고 결과를 관찰할 수 있다. **강화학습(reinforcement learning, RL)** 은 이 경험만으로 벨만 방정식을
근사해 푸는 방법이다. 보행 정책처럼 보상은 쓸 수 있지만 동역학 모델을 정확히 쓰기 어려운 문제에서 강하다.

## 개념

### 가치 기반: TD 학습과 Q-learning

가치 반복의 기댓값 $\sum_{s'} P(\cdot)[\dots]$ 를 **한 번의 표본**으로 바꾸면 TD(temporal difference) 학습이 된다.
행동 가치 $Q(s, a)$ 를 표로 두고, 한 걸음 경험 $(s, a, r, s')$ 마다 목표값 $r + \gamma \max_{a'} Q(s', a')$ 쪽으로 조금씩
움직인다. 이것이 **Q-learning** 이다. 행동은 $\varepsilon$ 확률로 무작위, 나머지는 $\arg\max_a Q$ 로 고른다(ε-greedy).
탐험을 해야 모르는 칸의 가치를 알 수 있고, 활용을 해야 보상을 얻는다.

상태가 고차원이면 표 대신 신경망 $Q_\phi$ 를 쓰고(DQN), 연속 행동에서는 $\max_a$ 가 어려워 SAC 같은
actor-critic 을 쓴다.

### 정책 기반: 정책 경사와 actor-critic

정책 $\pi_\theta(a \mid s)$ 를 직접 파라미터화하고 기대 보상 $J(\theta)$ 를 경사 상승으로 올린다. 정책 경사 정리는
"좋았던 궤적의 행동 확률을 올려라"를 수식으로 쓴 것이다(REINFORCE). 분산이 매우 커서 두 장치를 더한다.

- **기준선(baseline):** 보상 합에서 상태 가치 $V(s)$ 를 빼 어드밴티지 $A = Q - V$ 를 쓴다. 기대값은 그대로, 분산은 준다.
- **actor-critic:** $V_\phi$ 를 따로 학습하는 critic 이 어드밴티지를 추정하고, actor 는 정책을 갱신한다.

### PPO: 로봇 RL 의 기본값

정책 경사는 한 번에 너무 크게 움직이면 정책이 무너진다. **PPO(Proximal Policy Optimization)** 는 새 정책과 옛
정책의 확률 비 $\rho_t$ 를 $[1-\epsilon, 1+\epsilon]$ 로 잘라 한 배치에서 여러 번 안전하게 갱신한다. 구현이 단순하고
병렬 시뮬레이션과 잘 맞아 Isaac Lab·MuJoCo Playground 의 보행 예제(RSL-RL 등)가 기본으로 쓴다.
다만 on-policy 라 표본 효율이 낮아 GPU 시뮬레이터에서 수천 개 환경을 동시에 돌린다.

## 핵심 수식

Q-learning 갱신(TD 오차 $\delta$):

$$\delta = r + \gamma \max_{a'} Q(s', a') - Q(s, a),\qquad Q(s, a) \leftarrow Q(s, a) + \alpha\,\delta$$

정책 경사 정리(어드밴티지 형태):

$$\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}\big[\nabla_\theta \log \pi_\theta(a_t \mid s_t)\, A(s_t, a_t)\big]$$

PPO 클리핑 목표:

$$L^{\text{CLIP}}(\theta) = \mathbb{E}_t\Big[\min\big(\rho_t A_t,\ \operatorname{clip}(\rho_t, 1-\epsilon, 1+\epsilon) A_t\big)\Big],\qquad \rho_t = \frac{\pi_\theta(a_t \mid s_t)}{\pi_{\theta_\text{old}}(a_t \mid s_t)}$$

## 예제

앞 레슨과 같은 격자 세계를 `step()` 함수로만 경험하며 Q-learning 으로 푼다. 시작 칸은 왼쪽 아래 (3, 0) 이다.

```python
import numpy as np

# m9-mdp-decision-making 과 같은 4 × 4 격자. 이번에는 전이 확률을 모른 채 step() 으로만 경험한다.
LAYOUT = ["...G", ".#.P", "....", "...."]
MOVES = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # ↑ → ↓ ←
NAMES = "↑→↓←"
GAMMA, ALPHA, STEP_COST = 0.95, 0.1, -0.04
rng = np.random.default_rng(0)


def step(s, a):
    a = rng.choice([a, (a - 1) % 4, (a + 1) % 4], p=[0.8, 0.1, 0.1])  # 미끄러짐
    r, c = s[0] + MOVES[a][0], s[1] + MOVES[a][1]
    if not (0 <= r < 4 and 0 <= c < 4) or LAYOUT[r][c] == "#":
        r, c = s
    cell = LAYOUT[r][c]
    if cell == "G":
        return (r, c), 1.0, True
    if cell == "P":
        return (r, c), -1.0, True
    return (r, c), STEP_COST, False


Q = np.zeros((4, 4, 4))  # Q[행, 열, 행동]
for episode in range(20000):
    eps = max(0.05, 1.0 - episode / 10000)  # ε-greedy: 탐험 비율을 점점 줄인다
    s, done = (3, 0), False
    while not done:
        a = rng.integers(4) if rng.random() < eps else int(Q[s].argmax())
        s2, reward, done = step(s, a)
        target = reward if done else reward + GAMMA * Q[s2].max()  # TD 목표
        Q[s][a] += ALPHA * (target - Q[s][a])  # TD 오차만큼 이동
        s = s2

for r in range(4):
    cells = []
    for c in range(4):
        if LAYOUT[r][c] in "#GP":
            cells.append(f"  {LAYOUT[r][c] * (2 if LAYOUT[r][c] == '#' else 1):4s}")
        else:
            cells.append(f"{NAMES[Q[r, c].argmax()]}{Q[r, c].max():+.2f}")
    print(" ".join(cells))
```

출력:

```text
→+0.76 →+0.86 →+0.96   G
↑+0.66   ##   ↑+0.78   P
↑+0.56 ←+0.45 ←+0.35 ↓+0.23
↑+0.44 ←+0.39 ←+0.29 ←+0.25
```

시작 칸에서 목표까지 가는 왼쪽 열과 윗줄의 정책은 가치 반복과 같다. 그러나 (2, 2) 는 가치 반복의 답(↑, 0.52)과
달리 ←, 0.35 다. 탐험이 줄어든 뒤에는 이 칸에 거의 가지 않아 Q 값이 덜 학습된 것이다. 학습된 값이 가치 반복보다
조금 큰 칸이 있는 것은 고정 학습률과 $\max$ 연산의 **과대추정(overestimation) 편향** 때문이다.

**연습 과제(exercise):** (1) 칸별 방문 횟수를 세어 (2, 2) 가 얼마나 드물게 갱신되는지 확인하라. (2) 시작 칸을 매
에피소드 무작위로 바꾸면(exploring starts) 정책이 가치 반복과 일치하는지 보라. (3) $\alpha$ 를 방문 횟수에 따라
$1/n$ 으로 줄여 과대추정이 줄어드는지 비교하라.

## 자가 점검 질문

1. 가치 반복의 갱신식과 Q-learning 갱신식을 나란히 쓰고, 무엇이 "기댓값"에서 "표본"으로 바뀌었는지 짚어라.
2. 정책 경사에서 기준선을 빼도 경사의 기댓값이 변하지 않는 이유는 무엇이며, 그래도 빼는 이유는 무엇인가?
3. PPO 의 클리핑이 없다면 한 배치로 여러 번 갱신할 때 어떤 일이 생길 수 있는가? on-policy 라는 성질은 로봇 실기 학습에 왜 불리한가?

## 이 단계 공부법

1. **강의(먼저):** DeepMind x UCL Lecture 1–5 로 MDP·동적 계획·model-free 예측/제어를 한 줄로 잇는다.
2. **본문 + 예제:** 예제를 돌리고 연습 과제 (1)–(2) 로 탐험의 역할을 눈으로 확인한다.
3. **심층 RL:** CS 285 의 정책 경사·actor-critic 강의를 듣고 HW2 를 시도한다. PPO 는 CleanRL 의 `ppo.py` 한 파일을 처음부터 끝까지 읽는다.
4. **로봇 관점(선택):** Tedrake *Underactuated Robotics* Ch. 20 에서 model-free 정책 탐색이 최적 제어와 어떻게 이어지는지 읽는다.

## 참고 자료

- Sergey Levine, Berkeley CS 285 Deep Reinforcement Learning — <https://rail.eecs.berkeley.edu/deeprlcourse/>
- DeepMind x UCL RL Lecture Series 2021 —
  <https://discuss.ai.google.dev/t/deepminds-reinforcement-learning-lecture-series-2021/29496>
- Russ Tedrake, *Underactuated Robotics*, Ch. 20 — <https://underactuated.mit.edu/>
- Shengyi Huang 외, CleanRL — <https://github.com/vwxyzjn/cleanrl>
- John Schulman 외, "Proximal Policy Optimization Algorithms" (2017)
