---
id: m6-configuration-space-graph-search
title: "구성공간과 그래프 탐색(Dijkstra, A*)"
summary: 로봇의 자세 전체를 한 점으로 보는 구성공간(C-space)으로 경로 계획 문제를 정의하고, 점유 격자를 그래프로 보아 Dijkstra 와 A* 로 최단 경로를 찾는다. 휴리스틱이 탐색량을 줄이면서도 최적성을 지키는 조건을 numpy 예제로 확인한다.
objectives:
  - 작업 공간의 장애물이 구성공간의 금지 영역(C_obs)으로 바뀌는 과정을 설명하고, 원형 로봇에서 장애물 팽창이 그 근사임을 말할 수 있다.
  - 점유 격자를 8-연결 그래프로 만들고 Dijkstra 와 A* 를 우선순위 큐로 구현할 수 있다.
  - 허용(admissible)·일관(consistent) 휴리스틱의 뜻과, 휴리스틱이 확장 노드 수와 최적성에 주는 영향을 설명할 수 있다.
prerequisites: [m2-forward-kinematics, m5-occupancy-grid-scan-matching]
difficulty: 3
estimated_minutes: 120
tags: [configuration-space, graph-search, dijkstra, a-star, heuristic, grid]
activities:
  - id: m6-configuration-space-graph-search-reading
    kind: reading
    title: 본문과 A* 강의
    estimated_minutes: 40
  - id: m6-configuration-space-graph-search-quiz
    kind: quiz
    title: 구성공간과 휴리스틱 퀴즈
    estimated_minutes: 20
  - id: m6-configuration-space-graph-search-exercise
    kind: exercise
    title: 격자 A* 구현과 휴리스틱 실험
    estimated_minutes: 60
resources:
  - title: "Planning Algorithms (LaValle)"
    url: https://lavalle.pl/planning/
    kind: book
    note: Part I Ch. 2 Discrete Planning(Dijkstra·A*), Ch. 4 구성공간. 무료 HTML/PDF.
  - title: "A* Planning (Stachniss)"
    url: https://www.youtube.com/watch?v=HR1TNa8Lp7w
    kind: video
    note: Online Training – Mobile Robotics, Robotics 블록.
  - title: "PythonRobotics (Sakai)"
    url: https://atsushisakai.github.io/PythonRobotics/
    kind: other
    note: Path Planning 모듈의 Dijkstra·A* 샘플 코드와 애니메이션.
  - title: "MIT OCW 16.410 Principles of Autonomy and Decision Making"
    url: https://ocw.mit.edu/courses/16-410-principles-of-autonomy-and-decision-making-fall-2010
    kind: course
    note: 휴리스틱 탐색 강의(2010). 이론 보강용(선택).
---

# 구성공간과 그래프 탐색(Dijkstra, A*)

M5 에서 로봇은 지도(점유 격자)와 그 안의 자기 위치를 얻었다. 이제 "어디로 어떻게 갈지"를 정할
차례다. 이 레슨은 경로 계획 문제를 **구성공간**에서 정의하고, 가장 기본적인 해법인 격자 위의
그래프 탐색을 구현한다. Nav2 의 전역 플래너(NavFn, Smac)도 결국 이 알고리즘의 변형이다.

## 개념

### 구성공간(C-space)

로봇의 **구성(configuration)** $q$ 는 로봇의 모든 점의 위치를 정하는 최소한의 변수다. 평면 이동
로봇은 $q = (x, y, \theta)$, 2관절 팔은 $q = (\theta_1, \theta_2)$ 다(M2 의 정기구학이 $q$ 에서
몸체 위치를 계산한다). 로봇이 장애물과 겹치는 모든 $q$ 의 집합이 $C_{obs}$, 나머지가 자유 공간
$C_{free}$ 다. 경로 계획은 $C_{free}$ 안에서 $q_{start}$ 와 $q_{goal}$ 을 잇는 연속 곡선을 찾는 문제가
된다.

반경 $r$ 인 원형 로봇이면 방향 $\theta$ 가 충돌에 영향을 주지 않으므로, 장애물을 $r$ 만큼 부풀리고
로봇을 점으로 보면 된다. 다음 레슨의 비용 지도 팽창이 바로 이 아이디어다. 직사각형 로봇은
$\theta$ 마다 $C_{obs}$ 모양이 달라져 계산이 어려워지고, 이것이 샘플링 기반 계획이 필요한 이유다.

### 격자를 그래프로

점유 격자의 각 빈 칸을 노드, 이웃 칸으로의 이동을 간선(가로·세로 비용 1, 대각선 $\sqrt{2}$)으로
보면 경로 계획이 그래프 최단 경로 문제가 된다.

- **Dijkstra:** 시작점에서 누적 비용 $g(n)$ 이 가장 작은 노드부터 확장한다. 모든 방향으로 고르게
  퍼지며 최단 경로를 보장한다.
- **A\*:** $f(n) = g(n) + h(n)$ 이 가장 작은 노드부터 확장한다. $h(n)$ 은 목표까지의 남은 비용 추정이다.
  목표 쪽 노드를 먼저 보므로 확장 수가 크게 준다.

휴리스틱이 실제 남은 비용을 절대 넘지 않으면(**허용**) A* 는 최적 경로를 찾는다. 8-연결 격자에서는
옥타일 거리가 허용 휴리스틱이다. $h$ 에 1보다 큰 가중치를 곱하면(Weighted A*) 더 빨라지지만 최적성을
잃는다.

## 핵심 수식

A* 의 평가 함수와 간선 완화(relaxation):

$$f(n) = g(n) + h(n),\qquad g(n') \leftarrow \min\big(g(n'),\ g(n) + c(n, n')\big)$$

허용성과 일관성($h^*$ 는 실제 최소 남은 비용):

$$h(n) \le h^*(n),\qquad h(n) \le c(n, n') + h(n')$$

8-연결 격자의 옥타일 거리($\Delta r, \Delta c$ 는 행·열 차이):

$$h = \max(\Delta r, \Delta c) + (\sqrt{2} - 1)\min(\Delta r, \Delta c)$$

## 예제

두 벽이 엇갈린 20 × 30 격자에서 Dijkstra 와 A* 를 비교한다. 같은 코드에서 휴리스틱만 0 으로 바꾸면
Dijkstra 가 된다.

```python
import heapq

import numpy as np

grid = np.zeros((20, 30), dtype=bool)  # True = 장애물
grid[0:16, 10] = True  # 세로 벽, 아래쪽에 틈
grid[4:20, 20] = True  # 세로 벽, 위쪽에 틈
start, goal = (10, 2), (10, 27)  # (행, 열)
MOVES = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]


def plan(grid, start, goal, use_heuristic=True):
    def h(n):
        if not use_heuristic:
            return 0.0  # h = 0 이면 Dijkstra
        dr, dc = abs(n[0] - goal[0]), abs(n[1] - goal[1])
        return max(dr, dc) + (np.sqrt(2) - 1) * min(dr, dc)  # 8-연결 옥타일 거리

    g, parent = {start: 0.0}, {start: None}
    open_list, closed = [(h(start), start)], set()
    while open_list:
        _, node = heapq.heappop(open_list)
        if node in closed:
            continue  # 더 큰 비용으로 먼저 들어간 중복 항목
        closed.add(node)
        if node == goal:
            break
        for dr, dc in MOVES:
            nb = (node[0] + dr, node[1] + dc)
            if not (0 <= nb[0] < grid.shape[0] and 0 <= nb[1] < grid.shape[1]) or grid[nb]:
                continue
            new_g = g[node] + np.hypot(dr, dc)
            if new_g < g.get(nb, np.inf):
                g[nb], parent[nb] = new_g, node
                heapq.heappush(open_list, (new_g + h(nb), nb))
    path, n = [], goal
    while n is not None:
        path.append(n)
        n = parent[n]
    return path[::-1], g[goal], len(closed)


for name, use_h in [("Dijkstra", False), ("A*", True)]:
    path, cost, expanded = plan(grid, start, goal, use_h)
    print(f"{name:8s} 비용 {cost:6.2f}  경로 칸 {len(path):3d}  확장 노드 {expanded:4d}")

canvas = np.where(grid, "#", ".").astype("<U1")
for r, c in path:
    canvas[r, c] = "*"
print("\n".join("".join(row) for row in canvas))
```

두 알고리즘 모두 비용 37.53 의 같은 최단 경로를 찾지만 확장 노드는 Dijkstra 484 개, A* 325 개다.
그림의 `*` 가 벽 끝을 대각선으로 스치는 것에 주의하라. 실제 로봇이라면 벽 모서리를 긁는다.

**연습 과제(exercise):** (1) 휴리스틱에 가중치 1.5, 3 을 곱해 확장 노드 수와 경로 비용을 비교하라.
(2) 대각 이동 시 양옆 두 칸 중 하나라도 장애물이면 금지하도록 고쳐 모서리 긁기를 없애라.
(3) 4-연결로 바꾸고 맨해튼 거리를 휴리스틱으로 써 보라. 옥타일 거리를 그대로 쓰면 허용인가?

## 자가 점검 질문

1. 원형 로봇에서는 장애물을 부풀려 점 로봇으로 계획할 수 있는데, 직사각형 로봇에서는 왜 그렇게 간단하지 않은가?
2. 휴리스틱이 허용 조건을 어기면 A* 의 결과에 어떤 일이 생길 수 있는가? 반대로 $h = 0$ 이면?
3. 격자 해상도를 절반으로 줄이면(칸 수 4배) 탐색 비용과 경로 품질은 각각 어떻게 변하는가?

## 이 단계 공부법

1. **영상(먼저):** Stachniss "A* Planning" 으로 Dijkstra 에서 A* 로 가는 흐름을 잡는다.
2. **본문 + 예제:** 예제를 직접 돌리고 확장된 칸(`closed`)을 그림에 표시해 두 알고리즘의 퍼짐 모양을 비교한다.
3. **코드 읽기:** PythonRobotics 의 A* 코드와 내 구현을 나란히 놓고 차이를 찾는다.
4. **심화(선택):** LaValle *Planning Algorithms* Ch. 2 의 일반 탐색 틀과 Ch. 4 의 구성공간 정의를 읽는다.

## 참고 자료

- Steven M. LaValle, *Planning Algorithms*, Cambridge University Press — <https://lavalle.pl/planning/>
- Cyrill Stachniss, "A* Planning" — <https://www.youtube.com/watch?v=HR1TNa8Lp7w>
- Atsushi Sakai, PythonRobotics — <https://atsushisakai.github.io/PythonRobotics/>
- MIT OCW 16.410 Principles of Autonomy and Decision Making —
  <https://ocw.mit.edu/courses/16-410-principles-of-autonomy-and-decision-making-fall-2010>
