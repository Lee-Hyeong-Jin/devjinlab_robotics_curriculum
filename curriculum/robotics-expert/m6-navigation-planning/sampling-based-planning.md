---
id: m6-sampling-based-planning
title: "샘플링 기반 계획(RRT, RRT*, PRM)"
summary: 구성공간을 격자로 나누기 어려운 고차원·복잡한 문제를 위해, 무작위 샘플과 충돌 검사만으로 경로를 찾는 PRM·RRT 와 점근적 최적성을 더한 RRT* 를 다룬다. 작은 2D RRT/RRT* 를 numpy 로 구현해 경로 길이를 비교한다.
objectives:
  - 격자 탐색이 고차원 구성공간에서 실패하는 이유와, 샘플링 기반 계획이 충돌 검사만으로 이를 피하는 방법을 설명할 수 있다.
  - PRM(다중 질의)과 RRT(단일 질의)의 구조 차이와 쓰임새를 구분할 수 있다.
  - RRT 의 sample-nearest-steer-check 루프와 RRT* 의 부모 선택·rewire 를 numpy 로 구현할 수 있다.
prerequisites: [m6-configuration-space-graph-search]
difficulty: 3
estimated_minutes: 130
tags: [motion-planning, sampling, rrt, rrt-star, prm, collision-checking]
activities:
  - id: m6-sampling-based-planning-reading
    kind: reading
    title: 본문과 Modern Robotics Ch. 10 영상
    estimated_minutes: 45
  - id: m6-sampling-based-planning-quiz
    kind: quiz
    title: PRM·RRT·RRT* 비교 퀴즈
    estimated_minutes: 20
  - id: m6-sampling-based-planning-exercise
    kind: exercise
    title: RRT/RRT* 구현과 파라미터 실험
    estimated_minutes: 65
resources:
  - title: "Planning Algorithms (LaValle)"
    url: https://lavalle.pl/planning/
    kind: book
    note: Part II Ch. 5 샘플링 기반 계획(RRT·PRM), Ch. 4 구성공간.
  - title: "Modern Robotics Ch. 10 Motion Planning 영상"
    url: https://www.youtube.com/playlist?list=PLggLP4f-rq01Q3clJrnWFPRtpUwSlr4mG
    kind: video
    note: Ch. 10 재생목록, 49:36.
  - title: "Modern Robotics: Mechanics, Planning, and Control (Lynch, Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: Ch. 10.5 샘플링 기반 계획. 무료 preprint PDF.
  - title: "Michigan AutoRob"
    url: https://autorob.org/
    kind: course
    note: A*·RRT-Connect·충돌 검사 프로젝트(선택).
---

# 샘플링 기반 계획(RRT, RRT*, PRM)

앞 레슨의 격자 탐색은 2D 이동 로봇에는 잘 맞지만, 차원이 늘면 무너진다. 칸을 축마다 100 개로만
나눠도 6관절 팔의 구성공간은 $100^6 = 10^{12}$ 칸이다. 게다가 $C_{obs}$ 를 명시적으로 그릴 수도 없다.
샘플링 기반 계획은 "이 구성이 충돌하는가?"라는 질문(충돌 검사)만 반복해서 $C_{free}$ 를 탐색한다.
M7 의 MoveIt 2 가 쓰는 OMPL 플래너들이 이 계열이다.

## 개념

### PRM(Probabilistic Roadmap)

1. $C_{free}$ 에서 무작위 구성을 $N$ 개 뽑는다.
2. 각 점을 가까운 $k$ 개 이웃과 잇되, 잇는 선분이 충돌하지 않을 때만 간선으로 둔다.
3. 시작·목표를 로드맵에 붙이고 A* 로 탐색한다.

로드맵을 한 번 만들어 두면 같은 환경에서 여러 질의에 재사용할 수 있다(**다중 질의**). 좁은 통로처럼
부피가 작은 영역에는 샘플이 거의 떨어지지 않는 것이 약점이다.

### RRT(Rapidly-exploring Random Tree)

시작점에서 나무를 키운다. 매 반복마다 무작위 점 $q_{rand}$ 를 뽑고, 나무에서 가장 가까운 노드
$q_{near}$ 에서 그쪽으로 한 걸음 $\eta$ 만 뻗어 $q_{new}$ 를 만든 뒤, 선분이 충돌하지 않으면 추가한다.
큰 빈 공간 쪽 점이 더 자주 뽑히므로 나무는 미탐색 영역으로 빠르게 퍼진다(Voronoi 편향). 몇 %
확률로 목표점 자체를 샘플로 쓰면(목표 편향) 수렴이 빨라진다. 한 번의 질의에 특화되어 있고(**단일
질의**), 해가 있으면 언젠가 찾지만(확률적 완전성) 경로는 구불구불하고 최적이 아니다.

### RRT*

RRT 에 두 단계를 더한다. (1) $q_{new}$ 의 부모를 가장 가까운 노드가 아니라 반경 $r$ 안에서 누적
비용이 가장 작은 노드로 고른다. (2) **rewire:** 반경 안 이웃이 $q_{new}$ 를 거치면 더 싸질 때 부모를
바꾼다. 샘플이 늘수록 경로 비용이 최적값으로 수렴한다(점근적 최적성). 대가는 반복당 계산량이다.

## 핵심 수식

RRT 의 steer(한 걸음 $\eta$):

$$q_{new} = q_{near} + \min\!\left(1, \frac{\eta}{\lVert q_{rand} - q_{near}\rVert}\right)(q_{rand} - q_{near})$$

RRT* 의 부모 선택($\mathcal{N}$ 은 반경 $r$ 안의 이웃, $c$ 는 누적 비용):

$$\text{parent}(q_{new}) = \arg\min_{q \in \mathcal{N}} \big[c(q) + \lVert q_{new} - q\rVert\big]$$

## 예제

10 m × 10 m 공간의 원형 장애물 세 개를 피해 (0.5, 0.5) 에서 (9.5, 9.5) 로 간다.

```python
import numpy as np

rng = np.random.default_rng(1)
obstacles = np.array([[3.0, 3.0, 1.2], [6.0, 6.5, 1.5], [7.5, 2.5, 1.0]])  # (cx, cy, r)
start, goal = np.array([0.5, 0.5]), np.array([9.5, 9.5])
STEP, GOAL_TOL, N_ITER = 0.5, 0.5, 3000


def collision_free(a, b, n=10):
    """선분 a→b 위 n+1 점이 모든 원 밖이면 True (간단한 이산 충돌 검사)."""
    pts = a + np.linspace(0, 1, n + 1)[:, None] * (b - a)
    d = np.linalg.norm(pts[:, None, :] - obstacles[None, :, :2], axis=2)
    return bool(np.all(d > obstacles[:, 2]))


def rrt(star=False, radius=1.5):
    nodes, parent, cost = [start], [-1], [0.0]
    best = None
    for _ in range(N_ITER):
        sample = goal if rng.random() < 0.05 else rng.uniform(0, 10, 2)  # 5% 목표 편향
        pts = np.array(nodes)
        i_near = int(np.argmin(np.linalg.norm(pts - sample, axis=1)))
        d = sample - pts[i_near]
        new = pts[i_near] + d * min(1.0, STEP / (np.linalg.norm(d) + 1e-12))  # steer
        if not collision_free(pts[i_near], new):
            continue
        p_best, c_best = i_near, cost[i_near] + np.linalg.norm(new - pts[i_near])
        if star:  # 반경 안 이웃 중 비용이 가장 작은 부모를 고른다
            near = np.flatnonzero(np.linalg.norm(pts - new, axis=1) < radius)
            for j in near:
                c = cost[j] + np.linalg.norm(new - pts[j])
                if c < c_best and collision_free(pts[j], new):
                    p_best, c_best = int(j), c
        nodes.append(new)
        parent.append(p_best)
        cost.append(c_best)
        k = len(nodes) - 1
        if star:  # rewire: 새 노드를 거치면 더 싼 이웃의 부모를 바꾼다
            for j in near:
                c = c_best + np.linalg.norm(pts[j] - new)
                if c < cost[j] and collision_free(new, pts[j]):
                    parent[j], cost[j] = k, c  # (자손 비용 전파는 생략한 단순판)
        if np.linalg.norm(new - goal) < GOAL_TOL and (best is None or cost[k] < cost[best]):
            best = k
            if not star:
                break  # RRT 는 처음 찾은 경로로 끝낸다
    path, k = [goal], best  # 마지막 노드에서 목표점까지 직선으로 잇는다
    while k != -1:
        path.append(nodes[k])
        k = parent[k]
    return np.array(path[::-1]), len(nodes)


for name, star in [("RRT", False), ("RRT*", True)]:
    path, n_nodes = rrt(star)
    length = np.linalg.norm(np.diff(path, axis=0), axis=1).sum()
    print(f"{name:5s} 노드 {n_nodes:4d}  경로 점 {len(path):3d}  길이 {length:5.2f}")
print("직선 거리(장애물 무시 하한)", round(float(np.linalg.norm(goal - start)), 2))
```

RRT 는 노드 150 개 남짓으로 금방 경로를 찾지만 길이가 약 15.5 m 로 구불구불하다. RRT* 는 노드를
2500 개 넘게 쓰는 대신 약 13.2 m 로 장애물 사이를 거의 곧게 지난다. 충돌 검사는 선분 위 점 몇 개만
보는 단순판이라 아주 얇은 장애물은 뚫을 수 있다.

**연습 과제(exercise):** (1) 시드를 바꿔 10 번 돌리고 두 방법의 경로 길이 평균·분산을 비교하라.
(2) RRT* 의 `N_ITER` 를 500, 1000, 3000 으로 바꿔 길이가 줄어드는 곡선을 그려라. (3) 같은 장애물
위에 PRM(샘플 300 개, $k = 10$)을 만들고 레슨 1의 A* 로 탐색해 보라.

## 자가 점검 질문

1. 6관절 팔의 경로 계획에 격자 A* 대신 샘플링 기반 계획을 쓰는 이유 두 가지를 써라.
2. PRM 이 유리한 상황과 RRT 가 유리한 상황을 각각 예로 들어라.
3. RRT 에 목표 편향을 너무 크게(예: 50%) 주면 어떤 문제가 생기는가?

## 이 단계 공부법

1. **영상(먼저):** Modern Robotics Ch. 10 영상에서 구성공간·PRM·RRT 부분을 본다.
2. **본문 + 예제:** 예제를 돌리고 나무(`nodes`, `parent`)를 그림으로 그려 RRT 와 RRT* 의 차이를 눈으로 확인한다.
3. **교재:** LaValle Ch. 5 에서 충돌 검사·최근접 이웃 탐색이 실제 병목이라는 부분을 읽는다.
4. **심화(선택):** AutoRob 의 RRT-Connect 과제로 양방향 나무를 구현해 본다.

## 참고 자료

- Steven M. LaValle, *Planning Algorithms*, Cambridge University Press — <https://lavalle.pl/planning/>
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 10 — <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics Ch. 10 Motion Planning 영상 — <https://www.youtube.com/playlist?list=PLggLP4f-rq01Q3clJrnWFPRtpUwSlr4mG>
- University of Michigan, AutoRob — <https://autorob.org/>
- Sertac Karaman, Emilio Frazzoli, "Sampling-based Algorithms for Optimal Motion Planning", IJRR 2011 (RRT* 원논문, 링크 없음)
