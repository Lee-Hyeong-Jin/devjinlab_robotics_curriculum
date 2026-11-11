---
id: m9-robot-learning-overview
title: "로봇 러닝 개관: 모델 기반에서 데이터 중심으로"
summary: 지금까지의 모델 기반 파이프라인(인식→추정→계획→제어)과 학습 기반 정책을 비교하고, 강화학습·모방학습·파운데이션 모델이 각각 어떤 데이터와 가정 위에 서 있는지 지도를 그린다. M9 의 나머지 레슨과 계산 자원 요구를 미리 정리한다.
objectives:
  - 모델 기반 로봇 스택과 엔드투엔드 학습 정책의 차이를 입력·출력·실패 방식 관점에서 설명할 수 있다.
  - 강화학습·모방학습·VLA(파운데이션 모델)를 데이터 출처(보상, 시연, 대규모 다중 로봇 데이터)로 구분할 수 있다.
  - 주어진 과제(보행, 집기, 언어 지시 조작)에 어떤 학습 방식과 계산 자원 등급이 맞는지 근거를 들어 고를 수 있다.
prerequisites: [m9-mdp-decision-making, m4-object-detection-intro]
difficulty: 3
estimated_minutes: 90
tags: [robot-learning, reinforcement-learning, imitation-learning, foundation-models, overview, lerobot]
activities:
  - id: m9-robot-learning-overview-reading
    kind: reading
    title: 본문과 Hugging Face Robotics Course Unit 0–2
    estimated_minutes: 50
  - id: m9-robot-learning-overview-quiz
    kind: quiz
    title: 학습 방식 구분 퀴즈
    estimated_minutes: 15
  - id: m9-robot-learning-overview-exercise
    kind: exercise
    title: 내 과제에 맞는 학습 방식·자원 표 작성
    estimated_minutes: 25
resources:
  - title: "Hugging Face Robotics Course"
    url: https://huggingface.co/learn/robotics-course
    kind: course
    note: Unit 0–2(소개·LeRobot 생태계·고전 로보틱스의 한계). 무료, 자기 진도. Unit 5–7 은 조사 시점 미공개.
  - title: "Robot Learning: A Tutorial (Capuano 외, LeRobot 팀)"
    url: https://arxiv.org/abs/2510.12403
    kind: article
    note: RL·행동 복제·generalist 정책 장과 LeRobot 예제. 인터랙티브판 https://huggingface.co/spaces/lerobot/robot-learning-tutorial
  - title: "A realistic path to robotic foundation models (Interconnects)"
    url: https://www.interconnects.ai/p/robotic-foundation-models
    kind: article
    note: 왜 로보틱스가 데이터 중심으로 가는지에 대한 해설.
---

# 로봇 러닝 개관: 모델 기반에서 데이터 중심으로

M1–M8 에서 만든 로봇은 사람이 쓴 모델의 사슬이다. 카메라 모델(M4)로 특징을 뽑고, 칼만 필터(M5)로 위치를
추정하고, A*·DWA(M6)로 경로와 속도를 정한다. 각 부품은 해석할 수 있고 검증할 수 있다. 그러나 수건 개기,
케이블 꽂기, 처음 보는 물체 집기처럼 **모델을 쓰기 어려운 과제**에서는 사슬이 쉽게 끊긴다. 로봇 러닝은
이 빈틈을 데이터로 메우는 방법들의 묶음이다.

## 개념

### 정책이라는 공통 언어

앞 레슨의 MDP 정책 $\pi(s)$ 를 일반화하면 학습 기반 로봇의 출력은 **정책** $\pi_\theta(a \mid o)$ 하나다.
관측 $o$(이미지, 관절 각, 언어 지시)를 받아 행동 $a$(관절 목표, 말단 속도)를 낸다. 파라미터 $\theta$ 를
무엇으로 맞추느냐에 따라 세 갈래로 나뉜다.

| 방식 | 학습 신호 | 강점 | 약점 |
|---|---|---|---|
| 강화학습(RL) | 보상 함수 | 시연 없이 사람보다 나은 행동도 가능 | 시행착오가 많아 대부분 시뮬레이션에서 학습 |
| 모방학습(IL) | 사람 시연(텔레오퍼레이션) | 실제 로봇에서 수십 개 시연으로 시작 | 시연 밖 상태에서 오차 누적 |
| VLA·파운데이션 모델 | 대규모 다중 로봇 데이터 + 언어 | 언어 지시, 여러 로봇·과제로 일반화 | 큰 GPU, 평가가 어렵다 |

현장에서는 셋을 섞는다. 보행 정책은 시뮬레이션 RL 이 주류이고, 매니퓰레이션은 텔레오퍼레이션 시연으로
행동 복제(ACT, Diffusion Policy)를 하거나 VLA 를 파인튜닝한다. 고전 스택이 사라지는 것도 아니다.
학습 정책 아래에는 여전히 M3 의 저수준 제어와 안전 한계가, 옆에는 M5·M6 의 위치 추정과 내비게이션이 있다.

### 왜 "데이터 중심"인가

모델 기반 방법의 병목이 "더 좋은 모델"이라면, 학습 기반 방법의 병목은 **데이터의 양·다양성·품질**이다.
그래서 이 모듈의 뒷부분은 알고리즘만큼 데이터 수집(텔레오퍼레이션), 데이터셋 형식(LeRobotDataset,
RLDS), 평가 프로토콜을 다룬다. Interconnects 글이 말하는 "현실적인 경로"도 결국 데이터 수집 비용을 낮추는
이야기다.

### 계산 자원 등급

조사 노트(`research_notes/.../ai_robot_learning.md`)가 정리한 대략의 기준은 다음과 같다.

- **GPU 없음:** 이 모듈의 numpy 예제, Colab·HF Jobs 같은 원격 자원. LeRobot 은 CPU 학습을 권하지 않는다.
- **12–16 GB:** ACT 같은 가벼운 행동 복제, 작은 배치의 Diffusion Policy.
- **24 GB:** SmolVLA 파인튜닝, π0.5·GR00T 추론까지. 전체 VLA 파인튜닝은 40–80 GB 를 빌려야 한다.

## 핵심 수식

궤적 $\tau = (o_0, a_0, o_1, a_1, \dots)$ 의 확률과 RL 목표:

$$p_\theta(\tau) = p(s_0) \prod_t \pi_\theta(a_t \mid o_t)\, P(s_{t+1} \mid s_t, a_t),\qquad J(\theta) = \mathbb{E}_{\tau \sim p_\theta}\Big[\sum_t \gamma^t r_t\Big]$$

모방학습(행동 복제) 목표 — 시연 데이터 $\mathcal{D}$ 에 대한 최대 우도:

$$\theta^* = \arg\max_\theta \sum_{(o, a) \in \mathcal{D}} \log \pi_\theta(a \mid o)$$

두 식의 차이가 핵심이다. RL 은 **자기 정책이 만든** 분포 $p_\theta$ 위에서 기대 보상을 올리고, 행동 복제는
**전문가가 만든** 고정 분포 위에서 지도학습을 한다. 이 차이가 이후 레슨의 분포 이동(distribution shift)
문제로 이어진다.

## 예제

코드 대신 판단 연습을 한다. 다음 세 과제에 대해 학습 신호, 데이터 출처, 필요한 GPU 등급을 표로 정리하라.

1. 4족 보행 로봇의 평지 속도 추종 → 보상 설계가 쉽고 시뮬레이터가 좋다: **시뮬레이션 RL**, 학습엔 NVIDIA GPU.
2. 저가 6축 팔(SO-101)로 블록 집어 상자에 넣기 → 시연 50개 내외: **행동 복제(ACT)**, 12 GB 급.
3. "빨간 컵을 접시 옆에 놔" 같은 언어 지시 → **VLA 파인튜닝**(SmolVLA), 24 GB 급 또는 원격 GPU.

**연습 과제(exercise):** 본인이 관심 있는 과제 하나를 골라 같은 표를 만들고, 고전 스택(M3–M6)으로 풀 때와
비교해 무엇을 얻고 무엇을 잃는지 세 줄로 적어라.

## 자가 점검 질문

1. 고전 파이프라인에서 위치 추정이 실패하면 어디서 알 수 있는가? 엔드투엔드 정책이 실패하면 원인을 찾기가 왜 더 어려운가?
2. RL 목표와 행동 복제 목표에서 기대값을 취하는 분포는 각각 무엇이며, 그 차이가 왜 중요한가?
3. 보상 함수를 쓰기 어려운 과제와 시연을 모으기 어려운 과제의 예를 하나씩 들고 각각 어떤 방식을 고르겠는가?

## 이 단계 공부법

1. **강의(먼저):** Hugging Face Robotics Course Unit 0–2 를 읽고 LeRobot 이 무엇을 묶어 주는지 파악한다.
2. **튜토리얼:** *Robot Learning: A Tutorial* 의 서론과 RL·행동 복제 장의 개요만 훑는다(세부는 다음 레슨에서).
3. **해설:** Interconnects 글로 "왜 지금 데이터 중심인가"를 정리하고, 본문 표에 근거를 한 줄씩 보탠다.
4. **확인:** 자가 점검 질문에 답을 쓰고, 표를 M9 를 마칠 때 다시 고친다.

## 참고 자료

- Hugging Face, Robotics Course — <https://huggingface.co/learn/robotics-course>
- Francesco Capuano 외, "Robot Learning: A Tutorial" (arXiv:2510.12403) — <https://arxiv.org/abs/2510.12403>
  (인터랙티브판 <https://huggingface.co/spaces/lerobot/robot-learning-tutorial>)
- Nathan Lambert, "A realistic path to robotic foundation models", Interconnects —
  <https://www.interconnects.ai/p/robotic-foundation-models>
- LeRobot Hardware Guide(계산 자원 등급) — <https://huggingface.co/docs/lerobot/main/hardware_guide>
