---
id: m5-graph-slam-slam-toolbox
title: "그래프 SLAM 개요와 SLAM Toolbox 읽기"
summary: SLAM 을 자세 노드와 상대 측정 간선으로 이루어진 포즈 그래프의 최소제곱 문제로 보고, 루프 클로저가 누적 오차를 되돌리는 과정을 numpy 로 확인한다. 이어서 ROS 2 의 SLAM Toolbox 가 스캔 매칭(프런트엔드)과 그래프 최적화(백엔드)를 어떻게 나누고 map → odom 을 발행하는지 설정과 함께 읽는다.
objectives:
  - 온라인·전체 SLAM 의 차이와 그래프 SLAM 의 프런트엔드·백엔드 역할을 설명할 수 있다.
  - 상대 측정 간선과 루프 클로저로 이루어진 포즈 그래프를 정보 행렬 가중 최소제곱으로 풀 수 있다.
  - SLAM Toolbox 의 주요 파라미터와 mapping·localization 모드, 발행하는 tf·토픽을 읽고 설명할 수 있다.
prerequisites: [m5-occupancy-grid-scan-matching, m5-odometry-sensor-fusion, m8-tf2-urdf-visualization]
difficulty: 4
estimated_minutes: 140
tags: [slam, graph-slam, pose-graph, loop-closure, slam-toolbox, ros2]
activities:
  - id: m5-graph-slam-slam-toolbox-reading
    kind: reading
    title: 본문과 SLAM 강의·SLAM Toolbox 자습서 읽기
    estimated_minutes: 55
  - id: m5-graph-slam-slam-toolbox-quiz
    kind: quiz
    title: 포즈 그래프와 SLAM Toolbox 설정 퀴즈
    estimated_minutes: 20
  - id: m5-graph-slam-slam-toolbox-exercise
    kind: exercise
    title: 포즈 그래프 최적화와 설정 파일 해석
    estimated_minutes: 65
resources:
  - title: "Introduction to SLAM (Stachniss)"
    url: https://www.youtube.com/watch?v=0I30M6yTklo
    kind: video
    note: Online Training – Mobile Robotics, Robotics 블록. SLAM 문제 정의와 분류.
  - title: "Graph-based SLAM (Stachniss)"
    url: https://www.youtube.com/watch?v=uHbRKvD8TWg
    kind: video
    note: 포즈 그래프 최소제곱과 정보 행렬. 심화로 Graph SLAM with Landmarks, Robust LS 강의.
  - title: "FH Aachen ROS 2 summer school: SLAM Toolbox tutorial (Day 6)"
    url: https://ros2.fh-aachen.de/summer_school/Day6/Tutorials/slam_toolbox.html
    kind: article
    note: 독립적인 SLAM Toolbox 실습 안내. 이 레슨에서는 설정·토픽 구조만 읽는다.
  - title: "ROS2로 배우는 자율주행 로봇 센서 융합과 SLAM (최종명, 위키독스)"
    url: https://wikidocs.net/book/18464
    kind: book
    note: EKF → SLAM Toolbox 흐름(한국어, 2025-10).
  - title: "Michigan ROB 530 Mobile Robotics"
    url: https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public
    kind: course
    note: SLAM HW 와 Lie 군 기반 자세 표현(심화, 선택).
---

# 그래프 SLAM 개요와 SLAM Toolbox 읽기

앞 레슨에서 자세를 알면 지도를 만들 수 있고, 지도가 있으면 자세를 고칠 수 있음을 봤다. 둘 다
모를 때 동시에 푸는 것이 SLAM 이다. 스캔 매칭만 이어 붙이면 작은 오차가 쌓여 지도가 휘고, 같은
장소로 돌아왔을 때 벽이 이중으로 그려진다. 그래프 SLAM 은 "여기는 아까 왔던 곳"이라는 **루프
클로저**를 제약으로 추가하고 전체 궤적을 다시 최적화해 이 누적 오차를 되돌린다.

## 개념

### 온라인 SLAM 과 전체 SLAM

- **온라인 SLAM:** 현재 자세와 지도만 추정 $p(x_t, m \mid z_{1:t}, u_{1:t})$. EKF-SLAM, 파티클
  기반 FastSLAM·GMapping 이 여기에 속한다.
- **전체(full) SLAM:** 궤적 전체 $x_{1:t}$ 를 추정. 과거 자세를 고칠 수 있어 루프 클로저에 유리하다.
  그래프 SLAM 이 대표적이다.

### 포즈 그래프

- **노드:** 로봇 자세 $x_i$(보통 일정 거리·각도 이동마다 하나).
- **간선:** 두 자세 사이 상대 측정 $z_{ij}$ 와 그 확신도(정보 행렬 $\Omega_{ij}$). 연속 노드
  사이는 오도메트리·스캔 매칭, 멀리 떨어진 노드 사이는 루프 클로저.
- **프런트엔드:** 간선을 만든다(스캔 매칭, 루프 후보 탐색). 틀린 루프 클로저 하나가 지도 전체를
  망가뜨리므로 검증이 중요하다.
- **백엔드:** 모든 간선 오차를 동시에 최소화한다(가우스–뉴턴, Levenberg–Marquardt). 행렬이
  희소해서 수천 노드도 빠르게 푼다.

### SLAM Toolbox

Steve Macenski 의 SLAM Toolbox 는 ROS 2·Nav2 의 기본 2D LiDAR SLAM 이다. Karto 계열의 상관 스캔
매칭으로 간선을 만들고, 포즈 그래프를 Ceres 로 최적화한다. 결과로 `/map`(OccupancyGrid)과
`map → odom` 변환을 발행한다. 앞 레슨의 EKF 가 `odom → base_link` 를 맡으므로 tf 트리가
`map → odom → base_link → laser` 로 완성된다.

## 핵심 수식

간선 오차와 전체 비용:

$$e_{ij}(x) = z_{ij} - \hat z_{ij}(x_i, x_j),\qquad x^{\star} = \arg\min_x \sum_{(i,j)} e_{ij}^\top\,\Omega_{ij}\,e_{ij}$$

선형화하면 정규 방정식 $H\,\Delta x = -b$ 를 푼다. 여기서
$H = \sum J_{ij}^\top \Omega_{ij} J_{ij}$, $b = \sum J_{ij}^\top \Omega_{ij} e_{ij}$ 이다.
측정이 모두 상대값이므로 첫 자세를 고정해야(게이지 자유도) $H$ 가 가역이 된다.

## 예제

회전을 뺀 2D 위치 포즈 그래프다. 정사각형을 돌아 원점으로 돌아오며, 오도메트리에는 매 스텝 같은
방향의 치우침이 있다. 위치만 다루면 문제가 선형이라 한 번의 풀이로 끝난다.

```python
import numpy as np

rng = np.random.default_rng(2)
# 참 궤적: 4 m × 4 m 정사각형을 1 m 씩 돌아 원점으로 복귀(노드 17개)
dirs = [(1, 0)] * 4 + [(0, 1)] * 4 + [(-1, 0)] * 4 + [(0, -1)] * 4
moves = [np.array(d, float) for d in dirs]
truth = np.cumsum([np.zeros(2)] + moves, axis=0)
n = len(truth)

# 간선: (i, j, 측정된 x_j - x_i, 정보 가중치)
edges = []
for i, d in enumerate(moves):  # 오도메트리: 일정한 치우침 + 잡음
    edges.append((i, i + 1, d + [0.03, 0.02] + rng.normal(0, 0.03, 2), 1 / 0.03**2))
loop_z = truth[0] - truth[n - 1] + rng.normal(0, 0.02, 2)
edges.append((n - 1, 0, loop_z, 1 / 0.02**2))  # 루프 클로저: "원점에 돌아왔다"

odom_only = np.cumsum([np.zeros(2)] + [e[2] for e in edges[:-1]], axis=0)

H = np.zeros((2 * n, 2 * n))
b = np.zeros(2 * n)
for i, j, z, w in edges:
    A = np.zeros((2, 2 * n))  # 오차 e = (x_j - x_i) - z 의 야코비안
    A[:, 2 * i : 2 * i + 2], A[:, 2 * j : 2 * j + 2] = -np.eye(2), np.eye(2)
    H += w * A.T @ A
    b += w * A.T @ z
H[:2, :2] += 1e6 * np.eye(2)  # 첫 자세를 원점에 고정
x = np.linalg.solve(H, b).reshape(n, 2)


def rmse(est):
    return np.sqrt(np.mean(np.sum((est - truth) ** 2, axis=1)))


print(f"오도메트리만: RMSE {rmse(odom_only):.3f} m, 끝점 {np.linalg.norm(odom_only[-1]):.3f} m")
print(f"포즈 그래프 : RMSE {rmse(x):.3f} m, 끝점 {np.linalg.norm(x[-1]):.3f} m")
```

오도메트리만 쓰면 끝점이 원점에서 약 0.6 m 벗어나지만, 루프 클로저 간선 하나가 오차를 궤적 전체에
고르게 나눠 RMSE 가 0.38 m 에서 약 0.03 m 로 줄어든다. 실제 SLAM 은 회전 때문에 비선형이라 이 풀이를
가우스–뉴턴으로 반복한다.

### SLAM Toolbox 설정 읽기

`mapper_params_online_async.yaml` 에서 먼저 볼 항목(발췌):

```yaml
slam_toolbox:
  ros__parameters:
    mode: mapping               # localization 이면 저장된 그래프로 위치 추정만
    odom_frame: odom
    map_frame: map
    base_frame: base_footprint
    scan_topic: /scan
    resolution: 0.05            # 점유 격자 칸 크기 [m]
    minimum_travel_distance: 0.5   # 새 노드를 만드는 이동 거리
    do_loop_closing: true
```

**연습 과제(exercise):** (1) 루프 클로저 간선을 빼고 풀면 결과가 오도메트리와 같아짐을 확인하고
이유를 설명하라. (2) 루프 클로저 측정을 일부러 1 m 틀리게 넣어 지도가 어떻게 망가지는지 보라.
(3) FH Aachen 자습서를 읽고 SLAM Toolbox 가 구독·발행하는 토픽과 tf 를 그림으로 정리하라.

## 자가 점검 질문

1. 그래프 SLAM 에서 프런트엔드와 백엔드는 각각 무엇을 하며, 틀린 루프 클로저는 어느 쪽 책임인가?
2. 첫 자세를 고정하지 않으면 정규 방정식이 풀리지 않는 이유는?
3. SLAM Toolbox 와 robot_localization 이 각각 어떤 tf 를 발행해 트리를 완성하는가?

## 이 단계 공부법

1. **영상(먼저):** Stachniss "Introduction to SLAM" → "Graph-based SLAM" 순서로 본다.
2. **본문 + 예제:** 예제를 실행하고 궤적을 그려 루프 클로저 전후를 비교한 뒤 연습 과제를 한다.
3. **도구 읽기:** FH Aachen SLAM Toolbox 자습서와 최종명 위키독스 SLAM 장을 읽고 설정 파일을 본문과 대응시킨다.
4. **심화(선택):** ROB 530 SLAM 과제와 Stachniss 의 Graph SLAM with Landmarks·Robust LS 강의로 넓힌다.

## 참고 자료

- Cyrill Stachniss, "Introduction to SLAM" — <https://www.youtube.com/watch?v=0I30M6yTklo>
- Cyrill Stachniss, "Graph-based SLAM" — <https://www.youtube.com/watch?v=uHbRKvD8TWg>
- FH Aachen, ROS 2 summer school SLAM Toolbox tutorial —
  <https://ros2.fh-aachen.de/summer_school/Day6/Tutorials/slam_toolbox.html>
- 최종명, 『ROS2로 배우는 자율주행 로봇 센서 융합과 SLAM』(위키독스) — <https://wikidocs.net/book/18464>
- University of Michigan, ROB 530 Mobile Robotics — <https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public>
- Steve Macenski, Ivona Jambrecic, "SLAM Toolbox: SLAM for the dynamic world" (JOSS, 2021)
