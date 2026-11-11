---
id: m9-vla-foundation-models
title: "로봇 파운데이션 모델과 VLA(RT-2, OpenVLA, π0, SmolVLA)"
summary: 사전학습된 비전-언어 모델(VLM)에 행동 출력을 붙인 VLA(Vision-Language-Action) 모델의 구조를 행동 토큰화 방식과 연속 행동 헤드(flow matching) 방식으로 나눠 이해하고, RT-2·OpenVLA·π0 계열·SmolVLA·GR00T 의 공개 여부와 계산 요구를 정리한다. numpy 로 행동 토큰화의 양자화 오차와 토큰 수 문제를 확인한다.
objectives:
  - VLA 의 입력(이미지·언어·고유수용 상태)과 출력(행동 또는 행동 청크), 그리고 VLM 백본을 재사용하는 이유를 설명할 수 있다.
  - 이산 행동 토큰화(RT-2·OpenVLA)와 연속 행동 헤드(π0 의 flow matching)의 장단점을 양자화 오차와 추론 속도 관점에서 비교할 수 있다.
  - 공개 가중치·라이선스·VRAM 요구를 근거로 주어진 GPU 환경에서 추론·파인튜닝할 모델을 고를 수 있다.
prerequisites: [m9-imitation-learning-bc-dagger]
difficulty: 4
estimated_minutes: 120
tags: [vla, foundation-models, rt-2, openvla, pi0, smolvla, action-tokenization]
activities:
  - id: m9-vla-foundation-models-reading
    kind: reading
    title: 본문과 SmolVLA 블로그·VLA 서베이 읽기
    estimated_minutes: 60
  - id: m9-vla-foundation-models-quiz
    kind: quiz
    title: VLA 구조와 모델 선택 퀴즈
    estimated_minutes: 20
  - id: m9-vla-foundation-models-exercise
    kind: exercise
    title: 행동 토큰화 양자화 오차 실험
    estimated_minutes: 40
resources:
  - title: "SmolVLA 블로그 (Hugging Face)"
    url: https://huggingface.co/blog/smolvla
    kind: article
    note: 450M, Apache-2.0. LeRobot 커뮤니티 데이터로 학습. 파인튜닝 10–16 GB VRAM.
  - title: "openpi (Physical Intelligence)"
    url: https://github.com/Physical-Intelligence/openpi
    kind: other
    note: π0·π0-FAST·π0.5. 추론 >8 GB, LoRA 파인튜닝 >22.5 GB, 전체 파인튜닝 >70 GB.
  - title: "A Survey on Vision-Language-Action Models for Embodied AI"
    url: https://arxiv.org/html/2405.14093v7
    kind: article
    note: v7(2026-02) 아키텍처 분류 절. 읽기 순서는 https://relatedrepos.com/gh/MilkClouds/awesome-vla-study
  - title: "Isaac-GR00T (NVIDIA)"
    url: https://github.com/NVIDIA/Isaac-GR00T
    kind: other
    note: GR00T N1.7. 코드 Apache-2.0, 가중치 NVIDIA Open Model License. 추론 16 GB+, 파인튜닝 40 GB+ 권장.
---

# 로봇 파운데이션 모델과 VLA(RT-2, OpenVLA, π0, SmolVLA)

앞 레슨의 ACT 는 과제가 바뀌면 시연을 처음부터 다시 모은다. 언어 모델이 사전학습 후 적은 데이터로 적응하듯, 로봇도 **여러 로봇·과제의 대규모 데이터로 사전학습한 정책**을
파인튜닝해 쓰자는 것이 로봇 파운데이션 모델이다. 그 주류 형태가 VLA(Vision-Language-Action) 모델이다.

## 개념

### VLA 의 구조

VLA 는 카메라 이미지, 언어 지시("컵을 접시에 놔"), 로봇의 관절 상태를 받아 행동을 낸다. 몸통은 사전학습된
**비전-언어 모델(VLM)** 이다. VLM 이 이미 아는 물체·공간 관계·언어 이해를 재사용하므로, 로봇 데이터만으로는 배우기
어려운 "처음 보는 물체" 일반화가 가능해진다. 차이는 행동을 어떻게 출력하느냐다.

- **행동 토큰화(RT-2, OpenVLA):** 연속 행동의 각 차원을 256 개 구간으로 나눠 정수 토큰으로 만들고, VLM 이 텍스트를
  생성하듯 행동 토큰을 생성한다. 구조 변경이 거의 없지만 양자화 오차가 있고, 토큰을 하나씩 생성하므로 느리다.
  RT-2 는 가중치가 공개되지 않았고, OpenVLA(약 7B, MIT)는 공개 모델이다.
- **연속 행동 헤드(π0, π0.5, SmolVLA, GR00T):** VLM 위에 별도의 "행동 전문가" 네트워크를 두고 flow matching(확산
  계열)으로 **행동 청크**를 한 번에 연속값으로 생성한다. ACT 의 청크와 Diffusion Policy 의 분포 표현을 VLM 위로 옮긴
  셈이다. π0-FAST 는 반대로 압축 토크나이저(FAST)로 토큰 수를 줄여 자기회귀 방식을 살렸다.

### 무엇을 실제로 돌릴 수 있나 (조사 시점 2026-11)

| 모델 | 공개 | 대략의 요구 |
|---|---|---|
| SmolVLA | 450M, Apache-2.0 | 파인튜닝 10–16 GB |
| π0 / π0.5 (openpi, LeRobot) | 코드 Apache-2.0 | 추론 >8 GB, LoRA >22.5 GB, 전체 >70 GB |
| GR00T N1.7 | 코드 Apache-2.0, 가중치 NVIDIA 라이선스 | 추론 16 GB+, 파인튜닝 40 GB+ |
| OpenVLA / OpenVLA-OFT | MIT | 7B 급 |
| RT-2 | 가중치 비공개 | — |

24 GB 소비자 GPU 한 장이면 SmolVLA 파인튜닝과 π0.5·GR00T 추론까지가 현실적이다. 전체 파인튜닝은 40–80 GB GPU 를 빌린다.

### 파인튜닝이 기본 사용법

사전학습된 VLA 도 내 로봇·카메라 배치에서는 보통 시연 수십–수백 개로 파인튜닝한다. 앞 레슨의 데이터 수집
요령이 그대로 중요하다. 행동 공간(관절 vs 말단, 절대 vs 상대)과 정규화를
사전학습 데이터와 맞추는 일이 흔한 실패 지점이다.

## 핵심 수식

행동 토큰화($[\ell_j, h_j]$ 는 $j$ 번째 차원의 범위, $B$ 는 구간 수)와 최대 양자화 오차:

$$k_j = \Big\lfloor B \cdot \frac{a_j - \ell_j}{h_j - \ell_j} \Big\rfloor,\qquad |a_j - \hat a_j| \le \frac{h_j - \ell_j}{2B}$$

flow matching 행동 헤드: 노이즈 $\epsilon$ 과 정답 청크 $A$ 사이를 잇는 속도장 $v_\theta$ 를 학습하고, 추론 때 적분한다.

$$A^\tau = \tau A + (1 - \tau)\epsilon,\qquad \mathcal{L} = \mathbb{E}\,\big\lVert v_\theta(A^\tau, o, \tau) - (A - \epsilon) \big\rVert^2$$

## 예제

7차원 행동을 구간 수별로 토큰화했다가 복원해 오차를 재고, 행동 청크가 만드는 토큰 수를 센다.

```python
import numpy as np

# 가짜 텔레오퍼레이션 데이터: 7차원 행동(Δx, Δy, Δz, Δroll, Δpitch, Δyaw, 그리퍼) 2000 스텝
rng = np.random.default_rng(0)
t = np.arange(2000) * 0.02
arm = [0.05 * np.sin(t + k) + 0.005 * rng.standard_normal(t.size) for k in range(6)]
actions = np.column_stack(arm + [(np.sin(0.5 * t) > 0).astype(float)])


class BinTokenizer:
    """차원마다 1~99 백분위 범위를 n_bins 구간으로 나눠 정수 토큰으로 바꾼다."""

    def __init__(self, data, n_bins=256):
        self.lo, self.hi = np.percentile(data, 1, axis=0), np.percentile(data, 99, axis=0)
        self.n = n_bins

    def encode(self, a):
        z = (np.clip(a, self.lo, self.hi) - self.lo) / (self.hi - self.lo)
        return np.minimum((z * self.n).astype(int), self.n - 1)

    def decode(self, tok):
        return self.lo + (tok + 0.5) / self.n * (self.hi - self.lo)  # 구간 중앙값


for n_bins in (16, 64, 256):
    tk = BinTokenizer(actions, n_bins)
    err = np.abs(tk.decode(tk.encode(actions)) - actions)[:, :3]
    print(
        f"{n_bins:3d} 구간: Δ위치 평균 오차 {1000 * err.mean():.3f} mm, 최대 {1000 * err.max():.2f} mm"
    )

H = 50  # 행동 청크 길이(예: 50 Hz 로 1초)
print(
    f"청크 {H} 스텝 × {actions.shape[1]} 차원 = 토큰 {H * actions.shape[1]}개를 하나씩 생성해야 한다"
)
```

출력:

```text
 16 구간: Δ위치 평균 오차 1.805 mm, 최대 13.07 mm
 64 구간: Δ위치 평균 오차 0.480 mm, 최대 10.44 mm
256 구간: Δ위치 평균 오차 0.147 mm, 최대 9.79 mm
청크 50 스텝 × 7 차원 = 토큰 350개를 하나씩 생성해야 한다
```

평균 오차는 구간 수에 반비례해 줄지만, 최대 오차는 10 mm 근처에 머문다. 1–99 백분위 밖의 큰 행동이 잘려
나가기 때문이다. 이상치에 강한 범위 설정과 정밀도 사이의 맞교환이다. 청크 전체를 토큰으로 내면 수백 토큰을
순차 생성해야 하므로, 고속 제어에는 연속 헤드나 압축 토크나이저가 유리하다.

**연습 과제(exercise):** (1) 범위를 최소·최대값으로 바꿔 평균·최대 오차가 어떻게 바뀌는지 보라. (2) 그리퍼(이진)
차원의 오차를 따로 재 보고, 이 차원에 256 구간이 필요한지 판단하라.

## 자가 점검 질문

1. VLA 가 VLM 백본을 재사용해서 얻는 것과, 그 대가로 치르는 것(크기·지연)을 하나씩 들어라.
2. 행동 토큰화와 flow matching 헤드 중 50 Hz 이상의 제어 루프에 더 맞는 쪽은 무엇이며 왜인가?
3. 24 GB GPU 한 장으로 SO-101 팔에 언어 지시 집기 과제를 붙이려 한다. 어떤 모델로 어떻게(추론만/LoRA/전체) 시작하겠는가?

## 확인 퀴즈

`rc quiz m9-vla-foundation-models` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m9-vla-foundation-models-quiz
questions:
  - id: q1
    type: single
    prompt: 'VLA 가 사전학습된 VLM 백본을 재사용해서 얻는 것과 치르는 대가는?'
    choices:
      - '얻음: 처음 보는 물체·언어 지시에 대한 일반화 / 대가: 모델 크기와 추론 지연'
      - '얻음: 더 빠른 추론 / 대가: 일반화 능력 손실'
      - '얻음: 보상 함수 불필요 / 대가: 시연 데이터 증가'
      - '얻음: 실시간성 / 대가: GPU 메모리 절약 불가'
    answer: 0
    explanation: 'VLM 은 웹 규모 데이터에서 물체·공간 관계·언어를 이미 배웠으므로, 로봇 데이터만으로는 어려운 일반화를 가져온다. 대신 수억~수십억 파라미터를 들고 다녀야 해서 GPU 메모리와 추론 지연이 커지고, 그래서 제어 루프 구조를 따로 설계해야 한다.'
    concept: { front: 'VLM 백본 재사용의 거래', back: '얻음 = 새 물체·언어 일반화, 대가 = 크기·추론 지연' }
  - id: q2
    type: single
    prompt: '50 Hz 이상의 제어 루프에 더 적합한 행동 출력 방식과 그 이유는?'
    choices:
      - 'flow matching 행동 헤드 — 행동 청크를 한 번에 연속값으로 생성해 추론 1회로 여러 스텝을 덮는다'
      - '행동 토큰화 — 토큰을 하나씩 자기회귀로 생성해 지연이 작다'
      - '둘의 지연은 같다'
      - '어느 쪽도 50 Hz 에서는 불가능하다'
    answer: 0
    explanation: '행동 토큰화는 차원·스텝마다 토큰을 순차 생성하므로 한 행동을 내는 데 많은 디코딩 스텝이 든다. flow matching 헤드는 $k$ 스텝 청크를 한 번에 내므로 추론 1회로 여러 제어 주기를 채울 수 있다. π0-FAST 가 토큰 수를 줄이려 압축 토크나이저를 쓴 것도 같은 문제를 겨냥한 것이다.'
    concept: { front: '행동 토큰화 vs flow matching 헤드', back: '토큰화 = 순차 디코딩(느림), flow matching = 청크 한 번에(고주기 제어에 유리)' }
  - id: q3
    type: single
    prompt: '24 GB GPU 한 장으로 SO-101 팔에 언어 지시 집기 과제를 붙이려 할 때 현실적인 출발점은?'
    choices:
      - 'SmolVLA(450M)를 자기 데이터로 파인튜닝한다 — 10–16 GB 로 가능하다'
      - 'π0 전체 파인튜닝부터 시작한다'
      - 'OpenVLA 7B 전체 파인튜닝부터 시작한다'
      - 'GR00T 를 처음부터 학습한다'
    answer: 0
    explanation: '24 GB 한 장이면 SmolVLA 파인튜닝이 들어간다. π0 는 추론만 8 GB 이상, LoRA 가 22.5 GB 이상, 전체 파인튜닝은 70 GB 이상이라 단일 24 GB 로는 LoRA 가 간신히 경계에 있고 전체는 불가능하다. 작은 모델로 파이프라인(데이터 수집 → 학습 → 평가)을 먼저 완성하는 것이 순서다.'
```

## 이 단계 공부법

1. **서베이(먼저):** VLA 서베이의 아키텍처 분류 절만 읽고 토큰화 계열과 연속 헤드 계열을 표로 정리한다.
2. **본문 + 예제:** 예제로 양자화 오차와 토큰 수를 체감한다.
3. **모델 하나 깊게:** SmolVLA 블로그를 읽고, openpi README 에서 π0·π0-FAST·π0.5 의 차이와 메모리 요구를 확인한다.
4. **선택:** Isaac-GR00T 의 SO-100 예제 구성을 훑어 내 로봇에 붙일 때 바꿀 곳(행동 공간·카메라)을 적는다.

## 참고 자료

- Hugging Face, "SmolVLA: Efficient Vision-Language-Action Model trained on LeRobot Community Data" —
  <https://huggingface.co/blog/smolvla>
- Physical Intelligence, openpi — <https://github.com/Physical-Intelligence/openpi>
- "A Survey on Vision-Language-Action Models for Embodied AI" (v7) — <https://arxiv.org/html/2405.14093v7>
- NVIDIA, Isaac-GR00T — <https://github.com/NVIDIA/Isaac-GR00T>
- Anthony Brohan 외, "RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control" (2023)
- Moo Jin Kim 외, "OpenVLA: An Open-Source Vision-Language-Action Model" (2024)
- Kevin Black 외, "π0: A Vision-Language-Action Flow Model for General Robot Control" (2024)
