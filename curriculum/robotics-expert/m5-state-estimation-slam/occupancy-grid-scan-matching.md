---
id: m5-occupancy-grid-scan-matching
title: "점유 격자 지도와 스캔 매칭"
summary: 자세를 알 때 LiDAR 스캔으로 지도를 만드는 점유 격자 매핑(로그 오즈 갱신)을 구현하고, 반대로 지도가 있을 때 새 스캔을 맞춰 자세를 보정하는 스캔 매칭(상관 탐색·ICP)을 다룬다. 둘을 번갈아 하면 SLAM 의 프런트엔드가 된다.
objectives:
  - 점유 격자의 각 칸을 이진 베이즈 필터로 보고 로그 오즈 갱신식과 역센서 모델을 설명할 수 있다.
  - LiDAR 스캔과 알려진 자세로부터 점유 격자 지도를 numpy 로 만들 수 있다.
  - 상관(correlative) 스캔 매칭과 ICP 가 오도메트리 오차를 줄이는 원리와 실패 조건을 설명할 수 있다.
prerequisites: [m5-particle-filter-mcl, m4-point-clouds-icp-ransac]
difficulty: 3
estimated_minutes: 130
tags: [occupancy-grid, mapping, log-odds, scan-matching, icp, lidar]
activities:
  - id: m5-occupancy-grid-scan-matching-reading
    kind: reading
    title: 본문과 Occupancy Grid Maps 강의
    estimated_minutes: 45
  - id: m5-occupancy-grid-scan-matching-quiz
    kind: quiz
    title: 로그 오즈와 스캔 매칭 퀴즈
    estimated_minutes: 20
  - id: m5-occupancy-grid-scan-matching-exercise
    kind: exercise
    title: 가상 LiDAR 매핑·스캔 매칭 실험
    estimated_minutes: 65
resources:
  - title: "Occupancy Grid Maps (Stachniss)"
    url: https://www.youtube.com/watch?v=v-Rm9TUG9LA
    kind: video
    note: Online Training – Mobile Robotics, Robotics 블록.
  - title: "ICP (Stachniss)"
    url: https://www.youtube.com/watch?v=djnd502836w
    kind: video
    note: 스캔 정합의 기본. M4 ICP 레슨의 복습 겸 심화.
  - title: "Probabilistic Robotics (Thrun, Burgard, Fox)"
    url: https://robots.stanford.edu/probabilistic-robotics/
    kind: book
    note: Ch. 9 Occupancy Grid Mapping, Ch. 6 빔·우도장 센서 모델.
  - title: "Michigan ROB 530 Mobile Robotics"
    url: https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public
    kind: course
    note: 매핑 HW 로 연습량 보강(선택).
---

# 점유 격자 지도와 스캔 매칭

MCL 은 지도가 **있다고** 가정했다. 이 레슨은 그 지도를 만드는 법(자세를 알 때의 매핑)과, 지도에
스캔을 맞춰 자세를 고치는 법(스캔 매칭)을 다룬다. 둘을 함께 푸는 것이 다음 레슨의
SLAM 이고, Nav2·SLAM Toolbox 의 지도가 바로 점유 격자다.

## 개념

### 점유 격자

공간을 일정한 칸(예: 5 cm)으로 나누고 각 칸이 점유되었을 확률 $p(m_i)$ 를 저장한다. 칸들이 서로
독립이라고 가정하면, 각 칸은 "점유/비점유" 두 상태만 있는 **이진 베이즈 필터**다.

- LiDAR 빔이 지나간 칸 → 비어 있을 가능성 증가
- 빔이 끝난 칸 → 점유 가능성 증가
- 빔이 닿지 않은 칸 → 변화 없음(미지)

이 규칙이 **역센서 모델** $p(m_i \mid z, x)$ 이다. 확률을 그대로 곱하면 0·1 근처에서 수치가
불안정하므로 **로그 오즈**로 저장해 덧셈으로 갱신한다. 값을 일정 범위로 자르면(clamp) 문이 열리는
등 환경이 바뀌어도 다시 갱신될 수 있다.

### 스캔 매칭

오도메트리로 얻은 자세 추정 근처에서, 새 스캔의 끝점들이 지도의 점유 칸과 가장 잘 겹치는 자세를
찾는다.

- **상관 스캔 매칭:** 작은 탐색 창 $(\Delta x, \Delta y, \Delta\theta)$ 을 격자로 훑으며 점수를
  계산한다. 단순하고 지역 최소에 강하다. SLAM Toolbox(Karto 기반)가 이 방식이다.
- **ICP:** M4 에서 본 대로 점-점 대응을 반복 최적화한다. 빠르지만 초기값이 나쁘면 틀린 해에 빠진다.

긴 복도처럼 특징이 한 방향으로만 있는 환경에서는 복도 방향 이동이 구별되지 않아 매칭이 실패한다.

## 핵심 수식

로그 오즈와 칸 갱신($l_0$ 는 사전값, 보통 0):

$$l(m_i) = \log\frac{p(m_i)}{1 - p(m_i)},\qquad l_t(m_i) = l_{t-1}(m_i) + \log\frac{p(m_i \mid z_t, x_t)}{1 - p(m_i \mid z_t, x_t)} - l_0$$

확률 복원: $p(m_i) = 1 - 1/(1 + e^{l(m_i)})$

스캔 매칭(지도 $m$, 스캔 끝점 $\mathbf{p}_k$, 자세 변환 $T_x$):

$$x^{\star} = \arg\max_{x \in \text{창}} \sum_k \text{score}\big(m,\ T_x\,\mathbf{p}_k\big)$$

## 예제

6 m × 6 m 정사각형 방에서 세 자세의 360° 스캔으로 지도를 만들고, 오도메트리 오차가 있는 새 자세를
상관 탐색으로 보정한다.

```python
import numpy as np

rng = np.random.default_rng(0)
res, size = 0.1, 60  # 10 cm 격자, 6 m × 6 m
L_OCC, L_FREE = 0.85, -0.4  # 역센서 모델의 로그 오즈 증분
logodds = np.zeros((size, size))


def raycast(pose, angles, max_r=5.0):
    """정사각형 방(벽: x,y = 0.5, 5.5)에 대한 가상 LiDAR 거리."""
    x, y, th = pose
    r = []
    for a in angles:
        c, s = np.cos(th + a), np.sin(th + a)
        tx = [(w - x) / c for w in (0.5, 5.5) if abs(c) > 1e-9 and (w - x) / c > 0]
        ty = [(w - y) / s for w in (0.5, 5.5) if abs(s) > 1e-9 and (w - y) / s > 0]
        r.append(min(tx + ty + [max_r]))
    return np.array(r) + rng.normal(0, 0.02, len(angles))


def integrate_scan(pose, angles, ranges):
    x, y, th = pose
    for a, r in zip(angles, ranges, strict=True):
        d = np.arange(0, r, res / 2)  # 빔을 따라 반 칸 간격으로 샘플
        free = np.c_[x + d * np.cos(th + a), y + d * np.sin(th + a)]
        cells = np.unique((free / res).astype(int), axis=0)
        logodds[cells[:, 1], cells[:, 0]] += L_FREE
        hit = (np.array([x + r * np.cos(th + a), y + r * np.sin(th + a)]) / res).astype(int)
        logodds[hit[1], hit[0]] += L_OCC - L_FREE  # 끝점은 점유로 뒤집는다
    np.clip(logodds, -5, 5, out=logodds)


angles = np.linspace(-np.pi, np.pi, 180, endpoint=False)
for pose in [(2.0, 2.0, 0.0), (3.0, 2.5, 0.5), (4.0, 3.5, 1.0)]:
    integrate_scan(pose, angles, raycast(pose, angles))

prob = 1 - 1 / (1 + np.exp(logodds))
print("가운데 줄:", "".join("#" if p > 0.7 else "." if p < 0.3 else "?" for p in prob[30]))


def match_score(pose, angles, ranges):
    x, y, th = pose
    pts = np.c_[x + ranges * np.cos(th + angles), y + ranges * np.sin(th + angles)]
    idx = np.clip((pts / res).astype(int), 0, size - 1)
    return logodds[idx[:, 1], idx[:, 0]].sum()  # 끝점이 벽 칸에 떨어질수록 높다


true_pose = np.array([3.3, 2.8, 0.65])
scan = raycast(true_pose, angles)
guess = true_pose + [0.2, -0.15, 0.08]  # 오도메트리 추정(오차 포함)
steps = np.arange(-0.3, 0.31, 0.05)
candidates = [
    guess + [dx, dy, dth] for dx in steps for dy in steps for dth in np.arange(-0.15, 0.151, 0.01)
]
best = max(candidates, key=lambda p: match_score(p, angles, scan))
print("오도메트리 오차", np.round(guess - true_pose, 3))
print("스캔 매칭 오차", np.round(best - true_pose, 3))
```

가운데 줄은 `?????#....#?????` 꼴로 벽(`#`) 안쪽이 자유 공간(`.`), 바깥이 미지(`?`)다. 스캔 매칭은
(0.2, −0.15) m, 0.08 rad 오차를 탐색 해상도(5 cm) 이내로 줄인다.

**연습 과제(exercise):** (1) `prob` 를 이미지로 그리고 `L_OCC`, `L_FREE` 를 바꿔 벽 두께와 잡음 칸이
어떻게 변하는지 보라. (2) 방을 긴 복도(벽 x = 0.5, 1.5)로 바꾸고 복도 방향 오차가 스캔 매칭으로
보정되지 않는 것을 확인하라. (3) 탐색 창 대신 M4 의 ICP 로 같은 보정을 해 보고 초기 오차를 키워 가며 비교하라.

## 자가 점검 질문

1. 점유 격자에서 확률 대신 로그 오즈를 저장하는 이유 두 가지를 써라.
2. 빔이 끝난 칸과 빔이 지나간 칸에 서로 다른 갱신을 하는 이유를 역센서 모델로 설명하라.
3. 긴 복도에서 스캔 매칭이 실패하는 이유와, 이때 오도메트리·IMU 융합이 하는 역할은?

## 이 단계 공부법

1. **영상(먼저):** Stachniss "Occupancy Grid Maps" 로 로그 오즈 유도를 따라간다.
2. **본문 + 예제:** 예제를 돌리고 지도를 이미지로 그린 뒤 연습 과제 (1)–(3)을 한다.
3. **복습:** M4 ICP 레슨과 Stachniss "ICP" 강의로 스캔 정합을 다시 정리한다.
4. **심화(선택):** *Probabilistic Robotics* Ch. 9 와 ROB 530 매핑 과제로 연습량을 늘린다.

## 참고 자료

- Cyrill Stachniss, "Occupancy Grid Maps" — <https://www.youtube.com/watch?v=v-Rm9TUG9LA>
- Cyrill Stachniss, "ICP" — <https://www.youtube.com/watch?v=djnd502836w>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, MIT Press —
  <https://robots.stanford.edu/probabilistic-robotics/>
- University of Michigan, ROB 530 Mobile Robotics — <https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public>
