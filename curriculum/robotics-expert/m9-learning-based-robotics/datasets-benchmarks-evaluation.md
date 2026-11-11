---
id: m9-datasets-benchmarks-evaluation
title: "LeRobot 생태계·데이터셋·벤치마크와 안전한 평가"
summary: LeRobot 을 중심으로 로봇 학습 데이터가 어떻게 기록·공유되는지(LeRobotDataset, RLDS, Open X-Embodiment, DROID), 정책을 어떤 벤치마크로 비교하는지(LIBERO, MetaWorld), 그리고 적은 시행 수로 성공률을 정직하게 보고하고 실기 평가를 안전하게 하는 방법을 다룬다. numpy 로 성공률 신뢰구간과 순열 검정을 계산한다.
objectives:
  - LeRobot 의 구성(데이터셋·정책·로봇 드라이버·평가)과 LeRobotDataset·RLDS 형식, 대표 데이터셋의 규모와 라이선스 주의점을 설명할 수 있다.
  - 시뮬레이션 벤치마크와 실기 평가의 역할 차이를 설명하고, 평가 프로토콜(초기 조건, 시행 수, 성공 판정)을 설계할 수 있다.
  - 성공률의 Wilson 신뢰구간과 순열 검정을 계산해 두 정책의 차이가 의미 있는지 판단하고, 실기 평가의 안전 장치를 나열할 수 있다.
prerequisites: [m9-vla-foundation-models, m9-sim-to-real-domain-randomization]
difficulty: 4
estimated_minutes: 120
tags: [lerobot, datasets, benchmarks, evaluation, open-x-embodiment, safety]
activities:
  - id: m9-datasets-benchmarks-evaluation-reading
    kind: reading
    title: 본문과 LeRobot·Open X-Embodiment 문서 읽기
    estimated_minutes: 50
  - id: m9-datasets-benchmarks-evaluation-quiz
    kind: quiz
    title: 데이터셋·평가 프로토콜 퀴즈
    estimated_minutes: 20
  - id: m9-datasets-benchmarks-evaluation-exercise
    kind: exercise
    title: 성공률 신뢰구간과 평가 계획서 작성
    estimated_minutes: 50
resources:
  - title: "LeRobot"
    url: https://github.com/huggingface/lerobot
    kind: other
    note: 조사 시점 v0.7.0 고정 권장. 데이터셋 기록·시각화, ACT·Diffusion·VLA 정책, LIBERO/MetaWorld 평가.
  - title: "Open X-Embodiment"
    url: https://robotics-transformer-x.github.io/
    kind: article
    note: 1M+ 실제 궤적, 22 개 임바디먼트, RLDS 형식. 데이터셋별 라이선스가 다르다. LeRobot 미러 서브셋 존재.
  - title: "Vision-Language-Action in Robotics: A Survey of Datasets, Benchmarks, and Data Engines"
    url: https://arxiv.org/html/2604.23001
    kind: article
    note: 2026-04. 평가 프로토콜과 데이터 엔진. 파인튜닝 전에 읽기 권장.
  - title: "Sim-to-Real with SO-101 (NVIDIA Physical AI Learning)"
    url: https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/index.html
    kind: course
    note: 데이터 수집→학습→시뮬레이션·실기 평가의 전 과정 예시.
---

# LeRobot 생태계·데이터셋·벤치마크와 안전한 평가

학습 기반 로봇의 실력은 데이터에서 오고, 그 실력이 진짜인지는 평가가 말해 준다. 이 레슨은 M9 를 마무리하며
**데이터를 어떻게 남기고, 정책을 어떻게 비교하고, 결과를 어떻게 정직하게 보고하는지**를 다룬다. M10 캡스톤의
모방학습 트랙이 이 절차를 그대로 쓴다.

## 개념

### LeRobot 생태계

Hugging Face LeRobot 은 `pip install lerobot` 하나로 (1) 텔레오퍼레이션 기록과 데이터셋 형식, (2) ACT·Diffusion·
SmolVLA·π0 계열 등 정책 구현, (3) SO-101 같은 저가 팔의 모터 설정·보정 CLI, (4) LIBERO·MetaWorld 시뮬레이션
평가를 묶는다. 릴리스마다 설치·학습 인터페이스가 바뀌는 일이 잦으므로 커리큘럼에서는 버전을 고정한다(조사 시점 v0.7.0).

### 데이터셋 형식과 대표 데이터

- **LeRobotDataset:** 에피소드별 관절 상태·행동은 표 형식으로, 카메라는 동영상으로 저장하고 Hugging Face Hub 에서
  공유·스트리밍한다. 기록한 데이터를 웹에서 바로 시각화해 불량 에피소드를 거른다.
- **RLDS:** TensorFlow Datasets 기반 형식. Open X-Embodiment(1M+ 궤적, 22 개 로봇)와 DROID 가 이 형식으로 시작했다.
  LeRobot 형식 미러 서브셋도 있다.
- **라이선스:** OXE 는 하위 데이터셋마다 라이선스가 다르다(상업 이용 가능한 CC-BY 부터 비상업 전용까지).
  제품에 쓰려면 하위 데이터셋 단위로 확인해야 한다.

### 벤치마크와 실기 평가

시뮬레이션 벤치마크(LIBERO, MetaWorld)는 같은 초기 조건을 수백 번 재현할 수 있어 **알고리즘 비교**에 좋다.
그러나 실기 성능을 대신하지는 못한다. 실기 평가는 시행이 비싸 보통 수십 회에 그치므로 **프로토콜**이 중요하다.
초기 물체 배치를 미리 정해 두 정책에 똑같이 쓰고, 성공 판정 기준과 시간 제한을 사전에 적고, 실패 유형(못 집음,
떨어뜨림, 충돌)을 기록한다. 시행 수와 신뢰구간 없이 "성공률 80%"만 쓰는 보고는 비교 근거가 되지 못한다.

### 안전

학습 정책은 학습 분포 밖에서 예측하기 어려운 행동을 한다. 실기 평가 전에 (1) 관절·속도·토크 한계를 정책
바깥의 저수준 제어기에서 강제하고, (2) 비상 정지를 손 닿는 곳에 두고, (3) 작업 공간에 가상 경계를 두고,
(4) 처음에는 낮은 속도 배율로 돌리고, (5) 사람은 작업 공간 밖에서 관찰한다. 정책이 아니라 정책을 감싼 시스템이
안전을 책임진다.

## 핵심 수식

성공 $k$ 회 / 시행 $n$ 회, $\hat p = k/n$, $z = 1.96$ 일 때 95% Wilson 신뢰구간:

$$\frac{\hat p + \frac{z^2}{2n}}{1 + \frac{z^2}{n}} \pm \frac{z}{1 + \frac{z^2}{n}} \sqrt{\frac{\hat p (1 - \hat p)}{n} + \frac{z^2}{4n^2}}$$

신뢰구간 폭은 대략 $1/\sqrt{n}$ 로 줄어든다. 폭을 절반으로 줄이려면 시행이 4 배 필요하다.

## 예제

정책 A 와 B 를 20 회씩, 그리고 200 회씩 평가했다고 하자.

```python
import numpy as np


def wilson(successes, n, z=1.96):
    """성공률의 95% Wilson 신뢰구간. 시행 수가 적거나 0%·100% 근처에서도 안정적이다."""
    p = successes / n
    center = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return center - half, center + half


for name, k, n in [
    ("정책 A", 16, 20),
    ("정책 B", 13, 20),
    ("정책 A", 160, 200),
    ("정책 B", 130, 200),
]:
    lo, hi = wilson(k, n)
    print(f"{name} {k:3d}/{n:3d} = {k / n:.0%}  95% CI [{lo:.0%}, {hi:.0%}]")

# 순열 검정: 두 정책의 진짜 성공률이 같다면 20 회씩에서 3 회 이상 차이가 얼마나 자주 나는가?
rng = np.random.default_rng(0)
pooled = np.array([1] * (16 + 13) + [0] * (40 - 29))
diffs = []
for _ in range(20000):
    rng.shuffle(pooled)
    diffs.append(pooled[:20].sum() - pooled[20:].sum())
print(f"20 회씩 비교의 p-값 ≈ {np.mean(np.abs(diffs) >= 3):.2f}")
```

출력:

```text
정책 A  16/ 20 = 80%  95% CI [58%, 92%]
정책 B  13/ 20 = 65%  95% CI [43%, 82%]
정책 A 160/200 = 80%  95% CI [74%, 85%]
정책 B 130/200 = 65%  95% CI [58%, 71%]
20 회씩 비교의 p-값 ≈ 0.48
```

20 회씩이면 80% 와 65% 의 신뢰구간이 크게 겹치고, 순열 검정 p-값도 0.48 이다. "A 가 낫다"고 말할 근거가 없다.
같은 성공률이라도 200 회씩이면 구간이 갈라진다. 실기 시행은 비싸므로, 시뮬레이션 벤치마크로 후보를 좁히고 실기는
마지막 비교에 쓰는 이유다.

**연습 과제(exercise):** (1) 진짜 성공률이 80% 와 65% 일 때, 순열 검정으로 차이를 5% 수준에서 검출하려면 대략 몇 회씩
필요한지 시뮬레이션으로 찾아라. (2) 본인의 M10 과제를 가정해 초기 조건 10 가지, 성공 판정, 시간 제한, 안전 장치를
적은 한 쪽짜리 평가 계획서를 써라.

## 자가 점검 질문

1. 시뮬레이션 벤치마크 점수가 높은 정책이 실기에서 낮을 수 있는 이유를 앞 레슨의 현실 격차와 연결해 설명하라.
2. 20 회 시행에서 20/20 성공했다면 "성공률 100%"라고 보고해도 되는가? Wilson 구간의 하한은 대략 얼마인가?
3. 학습 정책의 안전을 정책 자체가 아니라 바깥 시스템에서 보장해야 하는 이유는 무엇인가?

## 이 단계 공부법

1. **문서(먼저):** LeRobot README 와 데이터셋 시각화 도구로 Hub 의 공개 데이터셋 하나를 열어 에피소드 구조를 확인한다.
2. **본문 + 예제:** 예제를 돌리고 연습 과제 (1) 로 "몇 번 시험해야 하는가"에 대한 감을 잡는다.
3. **데이터 읽기:** Open X-Embodiment 사이트에서 임바디먼트·과제 구성과 라이선스 안내를 확인한다.
4. **서베이:** 데이터셋·벤치마크 서베이(2604.23001)의 평가 프로토콜 절을 읽고 내 평가 계획서를 고친다.

## 참고 자료

- Hugging Face, LeRobot — <https://github.com/huggingface/lerobot>
- Open X-Embodiment Collaboration, Open X-Embodiment — <https://robotics-transformer-x.github.io/>
- "Vision-Language-Action in Robotics: A Survey of Datasets, Benchmarks, and Data Engines" — <https://arxiv.org/html/2604.23001>
- NVIDIA Physical AI Learning, "Sim-to-Real with SO-101" —
  <https://docs.nvidia.com/learning/physical-ai/sim-to-real-so-101/latest/index.html>
- DROID collaboration, DROID (Distributed Robot Interaction Dataset) — <https://droid-dataset.github.io>
