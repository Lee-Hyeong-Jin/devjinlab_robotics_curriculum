---
id: m9-imitation-learning-bc-dagger
title: "모방학습: 행동 복제, DAgger, ACT·Diffusion Policy"
summary: 사람 시연으로 정책을 지도학습하는 행동 복제(BC)와, 시연 밖 상태에서 오차가 쌓이는 분포 이동 문제, 이를 데이터 수집으로 고치는 DAgger 를 다룬다. 작은 numpy 예제로 BC 의 실패와 DAgger 의 회복을 재현하고, 실전 정책 계열인 ACT 와 Diffusion Policy 의 아이디어와 텔레오퍼레이션 데이터 수집 요령을 읽는다.
objectives:
  - 행동 복제를 지도학습 문제로 정식화하고 시연 데이터로 정책을 회귀할 수 있다.
  - 분포 이동(covariate shift)으로 오차가 누적되는 이유를 설명하고 DAgger 의 데이터 집계 절차를 구현할 수 있다.
  - ACT 의 행동 청크와 Diffusion Policy 의 다봉(multimodal) 행동 표현이 각각 어떤 BC 의 약점을 다루는지 설명할 수 있다.
prerequisites: [m9-reinforcement-learning-basics, m7-grasping-impedance-control]
difficulty: 4
estimated_minutes: 140
tags: [imitation-learning, behavior-cloning, dagger, act, diffusion-policy, teleoperation]
activities:
  - id: m9-imitation-learning-bc-dagger-reading
    kind: reading
    title: 본문과 Underactuated Ch. 21 Imitation Learning
    estimated_minutes: 50
  - id: m9-imitation-learning-bc-dagger-quiz
    kind: quiz
    title: 분포 이동과 DAgger 퀴즈
    estimated_minutes: 20
  - id: m9-imitation-learning-bc-dagger-exercise
    kind: exercise
    title: 차선 유지 BC·DAgger 실험
    estimated_minutes: 70
resources:
  - title: "Underactuated Robotics (Tedrake)"
    url: https://underactuated.mit.edu/
    kind: book
    note: Ch. 21 Imitation Learning.
  - title: "LeRobot"
    url: https://github.com/huggingface/lerobot
    kind: other
    note: 조사 시점 v0.7.0. ACT·Diffusion·VQ-BeT 정책 구현과 LIBERO/MetaWorld 벤치마크, LeRobotDataset.
  - title: "How I trained ACT on SO-101 (Hugging Face 블로그 미러)"
    url: https://www.plushcap.com/content/huggingface/blog/huggingface-how-i-trained-action-chunking-transformer-act-on-so-101-my-journey-gotchas-and-lessons
    kind: article
    note: 첫 ACT 학습의 시행착오 기록(Sherry Chen). 데이터 수집 요령 읽기용.
  - title: "Berkeley CS 285 Deep Reinforcement Learning"
    url: https://rail.eecs.berkeley.edu/deeprlcourse/
    kind: course
    note: Imitation Learning 강의와 HW1(BC·DAgger).
---

# 모방학습: 행동 복제, DAgger, ACT·Diffusion Policy

실제 로봇 팔로 수백만 번 시행착오를 할 수는 없다. 그래서 매니퓰레이션에서는 사람이 리더 팔이나 VR 로 로봇을
조종(텔레오퍼레이션)해 **시연**을 모으고 그것을 흉내 내는 **모방학습(imitation learning)** 이 출발점이다.

## 개념

### 행동 복제(Behavior Cloning, BC)

시연 $\mathcal{D} = \{(o_i, a_i)\}$ 를 입력–정답 쌍으로 보고 회귀나 분류를 한다. 보상이 필요 없고 시연
수십 개로도 동작한다. 문제는 **학습할 때와 실행할 때 상태 분포가
다르다**는 점이다. 학습 데이터는 전문가가 방문한 상태뿐인데, 실행하면 정책의 작은 실수가 전문가가 가 본 적 없는
상태로 로봇을 데려가고, 거기서 실수가 커진다. 이를 **분포 이동(covariate shift)** 또는 오차 누적(compounding
error)이라 한다.

### DAgger: 데이터로 분포 이동을 고친다

DAgger(Dataset Aggregation)는 (1) 현재 학습자 정책으로 로봇을 굴려 상태를 모으고, (2) 그 상태들에 전문가가 정답
행동을 붙이고, (3) 기존 데이터에 합쳐 다시 학습한다. 몇 번 반복하면 학습 분포가 학습자 자신의 방문 분포를 덮는다.
대가는 전문가가 학습자가 모는 동안 정답을 알려 줘야 한다는 것이라, 실전에서는 사람이 위험할 때만 개입하는
형태(HIL)로 변형해 쓴다.

### 실전 정책 계열

- **ACT(Action Chunking with Transformers):** 한 번에 행동 하나가 아니라 $k$ 스텝짜리 **행동 청크**를 예측한다.
  결정 횟수가 $1/k$ 로 줄어 오차 누적이 준다. LeRobot 기준 2–6 GB VRAM 의 가벼운 정책이다.
- **Diffusion Policy:** 같은 상황에서 사람이 왼쪽으로도 오른쪽으로도 돌아가면, 평균 제곱 오차 회귀는 두 시연의
  **평균**(장애물로 직진)을 낸다. 확산 모델로 행동 분포 자체를 표현해 다봉성(multimodality)을 다룬다(8–14 GB).

### 데이터 수집 요령

전략은 일관되게, 물체 위치·조명은 다양하게, 실패 직전 복구 동작도 일부러 넣는다(손으로 얻는 DAgger 효과).
카메라 위치와 보정(M4)은 학습과 배포 때 같아야 한다.

## 핵심 수식

행동 복제(가우시안 정책이면 평균 제곱 오차와 같다):

$$\hat\theta = \arg\min_\theta \sum_{(o, a) \in \mathcal{D}} \lVert \pi_\theta(o) - a \rVert^2$$

오차 누적: 매 스텝 실수 확률이 $\epsilon$ 일 때, 길이 $T$ 에피소드에서 BC 의 비용 증가는 최악의 경우 $O(\epsilon T^2)$,
DAgger 는 $O(\epsilon T)$ 다(Ross 외, 2011).

DAgger 반복($d_{\pi_i}$ 는 학습자 정책 $\pi_i$ 의 상태 방문 분포):

$$\mathcal{D} \leftarrow \mathcal{D} \cup \{(s, \pi^*(s)) : s \sim d_{\pi_i}\},\qquad \pi_{i+1} = \text{BC}(\mathcal{D})$$

## 예제

1차원 차선 유지. 시연은 중앙 근처에서만 모였고 시험은 벗어난 곳에서 출발한다. 정책은 RBF 특징 위의 릿지 회귀다.

```python
import numpy as np

# 1차원 차선 유지: x = 차선 중심에서의 횡 오차[m]. 옆바람 DRIFT 가 계속 +x 쪽으로 민다.
DT, DRIFT, T = 0.1, 0.5, 100
CENTERS = np.linspace(-3, 3, 25)  # RBF 특징의 중심
rng = np.random.default_rng(0)


def expert(x):
    return -2.0 * x - DRIFT  # 바람을 상쇄하고 중심으로 되돌리는 전문가(사람 운전자 역할)


def features(x):
    return np.exp(-((np.atleast_1d(x)[:, None] - CENTERS) ** 2) / (2 * 0.25**2))


def fit(X, U, lam=1e-3):  # 행동 복제 = 지도학습(릿지 회귀)
    F = features(X)
    return np.linalg.solve(F.T @ F + lam * np.eye(len(CENTERS)), F.T @ U)


def learner(w):
    return lambda x: (features(x) @ w)[0]


def rollout(policy, x0):
    xs, x = [], x0
    for _ in range(T):
        xs.append(x)
        x = float(np.clip(x + DT * (policy(x) + DRIFT) + rng.normal(0, 0.05), -3, 3))
    return np.array(xs)


starts = [-1.5, 1.0, 1.5]  # 시험: 중앙에서 벗어난 곳에서 출발


def report(name, policy):
    err = np.mean([np.abs(rollout(policy, x0)).mean() for x0 in starts for _ in range(5)])
    print(f"{name:9s} 평균 |x| = {err:.2f} m")


# 1) 전문가 시연 10개: 모두 차선 중앙 근처에서 출발
X = np.concatenate([rollout(expert, rng.normal(0, 0.05)) for _ in range(10)])
U = expert(X)
w = fit(X, U)
print(f"시연 데이터 범위 x ∈ [{X.min():+.2f}, {X.max():+.2f}]")
report("전문가", expert)
report("BC", learner(w))

# 2) DAgger: 학습자가 직접 몰아 본 상태에 전문가가 정답 행동을 붙이고 데이터에 합친다
for it in range(1, 4):
    Xn = np.concatenate([rollout(learner(w), x0) for x0 in starts])
    X, U = np.concatenate([X, Xn]), np.concatenate([U, expert(Xn)])
    w = fit(X, U)
    report(f"DAgger {it}", learner(w))
```

출력:

```text
시연 데이터 범위 x ∈ [-0.29, +0.27]
전문가       평균 |x| = 0.12 m
BC        평균 |x| = 1.54 m
DAgger 1  평균 |x| = 0.12 m
DAgger 2  평균 |x| = 0.12 m
DAgger 3  평균 |x| = 0.13 m
```

BC 정책은 시연 범위 $|x| < 0.3$ 밖에서 거의 0 을 출력해 바람에 밀려 나간다. DAgger 는 학습자가 실제로 방문한
상태에 정답을 붙여 한 번의 집계로 전문가 수준을 회복한다.

**연습 과제(exercise):** (1) 시연을 다양한 출발점(±2 m)에서 모으면 DAgger 없이도 BC 가 성공하는지 확인하라.
(2) 전문가 행동에 표준편차 0.3 의 노이즈를 넣어 사람 시연의 흔들림을 흉내 내고 BC·DAgger 를 비교하라.

## 자가 점검 질문

1. 행동 복제가 지도학습인데도 지도학습의 일반화 보장이 그대로 적용되지 않는 이유는 무엇인가?
2. DAgger 의 전문가 질의 비용이 실제 로봇에서 왜 문제가 되며, 사람 개입 기반 변형은 이를 어떻게 줄이는가?
3. 장애물을 왼쪽·오른쪽으로 피하는 시연이 섞여 있을 때 평균 제곱 오차 BC 는 무엇을 출력하는가? Diffusion Policy 는 이를 어떻게 다르게 다루는가?

## 확인 퀴즈

`rc quiz m9-imitation-learning-bc-dagger` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m9-imitation-learning-bc-dagger-quiz
questions:
  - id: q1
    type: single
    prompt: '행동 복제(BC)가 지도학습인데도 지도학습의 일반화 보장이 그대로 적용되지 않는 이유는?'
    choices:
      - '지도학습은 테스트 분포가 학습 분포와 같다고 가정하지만, 정책이 행동하면 자기 실수로 전문가가 가 본 적 없는 상태에 도달하기 때문'
      - '시연 데이터의 라벨이 부정확하기 때문'
      - 'BC 는 손실 함수를 쓰지 않기 때문'
      - '로봇 데이터는 항상 부족하기 때문'
    answer: 0
    explanation: 'i.i.d. 가정이 깨지는 것이 핵심이다. 학습 분포는 전문가 방문 상태이고, 실행 분포는 **학습된 정책**의 방문 상태다. 작은 예측 오차가 상태를 학습 분포 밖으로 밀어내고 거기서 오차가 더 커진다(분포 이동·오차 누적).'
    concept: { front: 'BC 의 분포 이동', back: '학습 = 전문가 방문 분포, 실행 = 정책 방문 분포 → i.i.d. 가정 붕괴, 오차 누적' }
  - id: q2
    type: single
    prompt: 'DAgger 의 전문가 질의 비용이 실제 로봇에서 문제가 되는 이유와 사람 개입 기반 변형의 해법은?'
    choices:
      - '학습자가 모는 모든 상태에 전문가가 정답 행동을 붙여야 하므로 비용이 크다 — 사람이 위험·실패 순간에만 개입해 교정 데이터를 준다'
      - '전문가가 로봇을 조작할 수 없기 때문 — 시뮬레이션만 쓴다'
      - 'DAgger 는 보상 함수가 필요하기 때문 — 보상을 학습한다'
      - '전문가 데이터가 너무 정확하기 때문 — 노이즈를 더한다'
    answer: 0
    explanation: 'DAgger 는 학습자가 방문한 상태 전체에 라벨을 요구하므로 사람이 계속 붙어 있어야 한다. HG-DAgger·HIL-SERL 류는 정책이 주행하다 위험해질 때만 사람이 끼어들어 교정하게 해, 가장 정보량이 큰 상태에만 라벨 비용을 쓴다.'
    concept: { front: 'DAgger 와 사람 개입 변형', back: '모든 방문 상태 라벨 → 비용 큼. 위험·실패 순간만 개입(HIL)해 정보량 높은 상태에 집중' }
  - id: q3
    type: single
    prompt: '장애물을 왼쪽·오른쪽으로 피하는 시연이 섞여 있을 때 평균 제곱 오차 BC 의 출력과 Diffusion Policy 의 차이는?'
    choices:
      - 'MSE 는 두 모드의 평균(장애물로 직진)을 출력하고, Diffusion Policy 는 행동 분포를 학습해 한쪽 모드를 표본으로 낸다'
      - '둘 다 한쪽 모드를 고른다'
      - 'MSE 가 더 안전한 경로를 고른다'
      - 'Diffusion Policy 도 평균을 출력한다'
    answer: 0
    explanation: 'MSE 회귀의 최적해는 조건부 평균이므로, 왼쪽·오른쪽 시연이 섞이면 그 평균인 "직진"을 내놓아 장애물로 들어간다(모드 평균화). 확산·flow 계열은 행동의 조건부 분포를 모델링해 다봉 분포에서 하나를 뽑으므로 한쪽으로 깔끔히 피한다.'
    concept: { front: '다봉 행동 분포와 MSE BC', back: 'MSE 는 조건부 평균(모드 평균화) → 위험. Diffusion/flow 는 분포에서 표본' }
```

## 이 단계 공부법

1. **교재(먼저):** Tedrake *Underactuated Robotics* Ch. 21 로 BC·분포 이동·DAgger 의 이론을 잡는다.
2. **본문 + 예제:** 예제를 돌리고 연습 과제 (1) 로 "데이터 다양성"과 "DAgger" 가 같은 문제를 푸는 두 방법임을 확인한다.
3. **강의·과제:** CS 285 의 imitation learning 강의를 듣고 HW1 을 시도한다.
4. **실전 읽기:** LeRobot 의 ACT 정책 코드와 "How I trained ACT on SO-101" 을 읽고, 시연 수·카메라·학습 시간에 대한 실전 감각을 메모한다.

## 참고 자료

- Russ Tedrake, *Underactuated Robotics*, Ch. 21 — <https://underactuated.mit.edu/>
- Hugging Face, LeRobot — <https://github.com/huggingface/lerobot>
- Sherry Chen, "How I trained Action Chunking Transformer (ACT) on SO-101" (HF 블로그 미러) —
  <https://www.plushcap.com/content/huggingface/blog/huggingface-how-i-trained-action-chunking-transformer-act-on-so-101-my-journey-gotchas-and-lessons>
- Stéphane Ross, Geoffrey Gordon, J. Andrew Bagnell, "A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning" (AISTATS 2011, DAgger)
- Tony Z. Zhao 외, "Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware" (2023, ACT)
- Cheng Chi 외, "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion" (2023)
