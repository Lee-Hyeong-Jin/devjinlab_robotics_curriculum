---
id: m4-point-clouds-icp-ransac
title: "점군 처리와 3D 기하: RANSAC·ICP"
summary: LiDAR·깊이 카메라가 만드는 점군을 다루는 두 핵심 알고리즘, 이상치에 강한 모델 추정(RANSAC)과 두 점군을 정합하는 ICP 를 numpy 로 구현한다.
objectives:
  - 깊이 영상을 카메라 모델로 역투영해 점군을 만드는 과정을 설명할 수 있다.
  - RANSAC 으로 이상치가 섞인 점군에서 평면을 찾고, 필요한 반복 횟수를 계산할 수 있다.
  - SVD 기반 강체 정합과 최근접 이웃 대응을 반복하는 point-to-point ICP 를 구현할 수 있다.
prerequisites: [m4-camera-model-features, m1-rotation-representations]
difficulty: 3
estimated_minutes: 110
tags: [point-cloud, ransac, icp, registration, lidar, 3d-geometry]
activities:
  - id: m4-point-clouds-icp-ransac-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 35
  - id: m4-point-clouds-icp-ransac-quiz
    kind: quiz
    title: RANSAC 반복 횟수와 ICP 수렴 퀴즈
    estimated_minutes: 15
  - id: m4-point-clouds-icp-ransac-exercise
    kind: exercise
    title: 바닥 평면 제거와 점군 정합 구현
    estimated_minutes: 60
resources:
  - title: "Cyrill Stachniss, ICP"
    url: https://www.youtube.com/watch?v=djnd502836w
    kind: video
    note: Robotics 블록. SVD 기반 정합 유도까지. 먼저 본다.
  - title: "Cyrill Stachniss, RANSAC"
    url: https://www.youtube.com/watch?v=Cu1f6vpEilg
    kind: video
    note: Robotics 블록. 반복 횟수 공식 포함.
  - title: "Cyrill Stachniss, Least Squares – An Informal Introduction"
    url: https://www.youtube.com/watch?v=r2cyMQ5NB1o
    kind: video
    note: Basics 블록. 정합을 최소제곱 문제로 보는 관점 복습.
  - title: Open3D Getting Started
    url: https://www.open3d.org/docs/release/getting_started.html
    kind: other
    note: v0.19. Geometry(point cloud·KDTree)·Pipelines(ICP registration) 튜토리얼로 실제 데이터 실습.
---

# 점군 처리와 3D 기하: RANSAC·ICP

LiDAR 와 깊이 카메라는 이미지 대신 **점군**(point cloud), 즉 3D 점 수만 개의 목록을 준다.
점군으로 로봇이 하는 일은 대부분 두 질문으로 줄어든다. "이 점들 중 어떤 것이 바닥·벽 같은
모델에 속하는가?"(RANSAC) 그리고 "방금 본 점군과 이전 점군은 얼마나 움직였는가?"(ICP).
두 알고리즘은 중급 M5 의 스캔 매칭 SLAM 과 고급 단계의 파지 위치 추정에 그대로 쓰인다.

## 개념

### 점군 만들기

깊이 카메라는 픽셀 $(u, v)$ 마다 깊이 $Z$ 를 준다. 앞 레슨의 투영을 거꾸로 하면 3D 점이 된다.
2D LiDAR 는 각도 $\phi_i$ 와 거리 $r_i$ 로 $(r_i\cos\phi_i, r_i\sin\phi_i)$ 를 만든다. 이렇게 만든 점은
센서 좌표계에 있으므로, M1 의 동차 변환으로 로봇·월드 좌표계로 옮긴다. 점이 너무 많으면
**복셀 다운샘플링**(격자마다 한 점)으로 줄이고, 이웃 탐색은 KD-트리로 빠르게 한다.

### RANSAC

최소제곱은 이상치 하나에도 크게 끌려간다. RANSAC 은 반대로 접근한다.

1. 모델을 정하는 데 필요한 최소 점(평면이면 3개)을 무작위로 뽑는다.
2. 그 점으로 모델을 만들고, 거리 임계값 안에 드는 **인라이어** 수를 센다.
3. 여러 번 반복해 인라이어가 가장 많은 모델을 고르고, 그 인라이어로 최소제곱 재추정한다.

로봇에서는 바닥 평면을 찾아 지우고 남은 점에서 장애물·물체를 찾는 전처리로 자주 쓴다.

### ICP

두 점군 $P$(소스)와 $Q$(타깃)이 같은 장면을 다른 위치에서 본 것일 때, $P$ 를 $Q$ 에 겹치는
회전 $R$ 과 이동 $t$ 를 찾는다. 대응점을 알면 SVD 로 한 번에 풀린다(Kabsch). 대응을 모르므로
**최근접 이웃을 대응으로 가정 → 정합 → 다시 대응 찾기**를 반복한다. 초기 추정이 실제와 너무
다르면 엉뚱한 국소 최솟값에 빠지므로, 보통 오도메트리로 초기값을 준다.

## 핵심 수식

점 $p$ 와 평면(단위 법선 $n$, 평면 위의 점 $a$) 사이 거리: $d = |(p - a)\cdot n|$.

RANSAC 반복 횟수(인라이어 비율 $w$, 최소 표본 수 $s$, 성공 확률 $p$):

$$N = \frac{\log(1 - p)}{\log(1 - w^s)}$$

예: $w = 0.6$, $s = 3$, $p = 0.99$ 이면 $N \approx 19$.

강체 정합(대응 $p_i \leftrightarrow q_i$ 가 주어졌을 때):

$$\min_{R,t}\sum_i \lVert R\,p_i + t - q_i\rVert^2,\quad
H = \sum_i (p_i - \bar p)(q_i - \bar q)^\top = U\Sigma V^\top$$

$$R = V\,\mathrm{diag}(1, 1, \det(VU^\top))\,U^\top,\qquad t = \bar q - R\,\bar p$$

## 예제

```python
import numpy as np

rng = np.random.default_rng(3)

# 1) RANSAC 평면 검출: 바닥(z=0) 300점 + 상자·잡음 이상치 150점
floor = np.c_[rng.uniform(-2, 2, (300, 2)), rng.normal(0, 0.01, 300)]
clutter = rng.uniform([-2, -2, 0.05], [2, 2, 1.0], (150, 3))
cloud = np.vstack([floor, clutter])


def ransac_plane(P, iters=200, thresh=0.03):
    best = np.zeros(len(P), dtype=bool)
    for _ in range(iters):
        a, b, c = P[rng.choice(len(P), 3, replace=False)]
        n = np.cross(b - a, c - a)
        if np.linalg.norm(n) < 1e-9:
            continue  # 세 점이 한 직선 위
        n /= np.linalg.norm(n)
        inliers = np.abs((P - a) @ n) < thresh
        if inliers.sum() > best.sum():
            best = inliers
    return best


inl = ransac_plane(cloud)
print(f"평면 인라이어 {inl.sum()}개 (바닥 점 300개)")


# 2) ICP: 같은 점군을 회전·이동한 뒤 원래 위치로 정합
def best_fit(A, B):  # A를 B에 맞추는 R, t (SVD, Kabsch)
    ca, cb = A.mean(0), B.mean(0)
    U, _, Vt = np.linalg.svd((A - ca).T @ (B - cb))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])  # 반사 방지
    R = Vt.T @ D @ U.T
    return R, cb - R @ ca


def icp(src, dst, iters=30):
    R_tot, t_tot, cur = np.eye(3), np.zeros(3), src.copy()
    for _ in range(iters):
        d2 = ((cur[:, None, :] - dst[None, :, :]) ** 2).sum(-1)
        nn = dst[d2.argmin(1)]  # 최근접 이웃 대응
        R, t = best_fit(cur, nn)
        cur = cur @ R.T + t
        R_tot, t_tot = R @ R_tot, R @ t_tot + t
    return R_tot, t_tot, np.sqrt(d2.min(1).mean())


yaw = np.deg2rad(10)
R_true = np.array([[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]])
dst = clutter
src = (dst - [0.1, -0.05, 0.0]) @ R_true  # dst = R_true @ src + t_true
R_est, t_est, err = icp(src, dst)
print(f"추정 yaw {np.rad2deg(np.arctan2(R_est[1, 0], R_est[0, 0])):.2f} deg, t {t_est.round(3)}")
print(f"정합 후 RMS 거리 {err:.4f}")
```

RANSAC 은 이상치가 3분의 1 이나 섞여도 바닥 점 거의 전부(298/300)를 찾는다. ICP 는
$10^\circ$ 회전과 $(0.1, -0.05, 0)$ 이동을 정확히 되찾는다. 최근접 이웃을 전부 비교하는
$O(nm)$ 방식은 수백 점까지만 쓸 만하고, 실제로는 KD-트리(Open3D)를 쓴다.

**연습 과제(exercise):** (1) 이상치 비율을 바꿔 가며 RANSAC 이 실패하기 시작하는 반복 횟수를
찾고 공식과 비교하라. (2) RANSAC 인라이어로 평면을 최소제곱 재추정하라(SVD 의 최소 특이벡터가
법선). (3) ICP 초기 회전을 10°, 30°, 60° 로 늘리며 수렴 여부를 기록하라.

## 자가 점검 질문

1. 이상치가 섞인 데이터에 최소제곱 대신 RANSAC 을 쓰는 이유는 무엇인가?
2. ICP 가 좋은 초기값을 필요로 하는 이유를 최근접 이웃 대응 관점에서 설명하라.
3. Kabsch 정합에서 $\det(VU^\top) = -1$ 인 경우를 보정하지 않으면 어떤 결과가 나오는가?

## 확인 퀴즈

`rc quiz m4-point-clouds-icp-ransac` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m4-point-clouds-icp-ransac-quiz
questions:
  - id: q1
    type: single
    prompt: '이상치가 섞인 점군에서 바닥 평면을 찾을 때 최소제곱보다 RANSAC 이 유리한 이유는?'
    choices:
      - '계산량이 항상 더 적기 때문'
      - '모든 점의 오차를 더하지 않고, 임계값 안에 드는 인라이어 수가 가장 많은 모델을 고르기 때문'
      - '이상치가 없는 데이터에서도 더 정확하기 때문'
      - '반복이 필요 없기 때문'
    answer: 1
    explanation: '최소제곱은 모든 점의 제곱 오차를 더하므로 멀리 떨어진 이상치 하나가 해를 크게 끌고 간다. RANSAC 은 인라이어 개수로 모델을 평가하므로 이상치가 해에 거의 영향을 주지 않는다. 이상치가 없다면 최소제곱이 더 정확하고 빠르다.'
    concept: { front: 'RANSAC 이 이상치에 강한 이유', back: '제곱 오차 합이 아니라 임계값 안 인라이어 **개수**로 모델을 고른다' }
  - id: q2
    type: truefalse
    prompt: 'ICP 는 초기 추정이 실제 변환과 많이 달라도 전역 최적해로 수렴한다.'
    answer: false
    explanation: 'ICP 는 최근접 이웃을 대응으로 **가정**하고 반복한다. 초기값이 나쁘면 처음부터 틀린 대응이 만들어지고 그 대응에 맞는 국소 최솟값으로 수렴한다. 그래서 보통 오도메트리나 거친 정합으로 초기값을 준다.'
    concept: { front: 'ICP 가 초기값에 민감한 이유', back: '최근접 이웃 대응 가정 — 초기값이 나쁘면 틀린 대응의 국소 최솟값에 빠진다' }
  - id: q3
    type: single
    prompt: 'Kabsch 정합에서 $R = V\,\mathrm{diag}(1, 1, \det(VU^\top))\,U^\top$ 의 보정 항을 빼면 어떤 일이 생길 수 있는가?'
    choices:
      - '회전이 항상 항등 행렬이 된다'
      - '$\det R = -1$ 인 반사(거울상)가 나와 점군이 뒤집힌다'
      - '이동 벡터 $t$ 를 구할 수 없다'
      - '아무 차이가 없다'
    answer: 1
    explanation: 'SVD 가 주는 $VU^\top$ 는 직교 행렬이지만 행렬식이 $-1$ 일 수 있다. 그러면 회전이 아니라 반사가 되어 점군이 거울처럼 뒤집힌다. 마지막 특이값에 대응하는 성분의 부호를 $\det(VU^\top)$ 로 바로잡아 $\det R = +1$ 인 $SO(3)$ 원소를 보장한다.'
```

## 이 단계 공부법

1. **영상(먼저):** Stachniss *RANSAC* → *ICP* 순으로 본다. ICP 유도가 어렵다면
   *Least Squares – An Informal Introduction* 을 먼저 본다.
2. **본문 + 예제:** `best_fit` 을 대응이 알려진 점 세 쌍으로 손계산과 비교해 본다.
3. **문제:** 퀴즈에서 반복 횟수 공식을 직접 계산하고, 연습 과제 (1)~(3)을 푼다.
4. **실데이터(선택):** Open3D Getting Started 의 point cloud·ICP registration 튜토리얼로
   KD-트리, 다운샘플링, point-to-plane ICP 를 써 본다.

## 참고 자료

- Cyrill Stachniss, "ICP" — <https://www.youtube.com/watch?v=djnd502836w>
- Cyrill Stachniss, "RANSAC" — <https://www.youtube.com/watch?v=Cu1f6vpEilg>
- Cyrill Stachniss, "Least Squares – An Informal Introduction" — <https://www.youtube.com/watch?v=r2cyMQ5NB1o>
- Open3D Getting Started (v0.19) — <https://www.open3d.org/docs/release/getting_started.html>
