---
id: m6-costmap-global-planning
title: "비용 지도와 전역 계획(Nav2 플래너 읽기)"
summary: 점유 격자를 그대로 쓰지 않고 정적·장애물·팽창 층을 겹친 비용 지도(costmap)로 바꿔, 장애물에서 떨어진 안전한 전역 경로를 A* 로 찾는다. Nav2 비용 지도의 비용 값 체계와 NavFn·Smac 플래너가 이 구조 위에서 어떻게 동작하는지 읽는다.
objectives:
  - 비용 지도의 층(정적·장애물·팽창)과 비용 값(자유·내접·치명·미지)의 의미를 설명할 수 있다.
  - 팽창 층의 지수 감쇠 비용을 계산하고, 비용을 반영한 A* 로 여유 있는 경로를 numpy 로 구할 수 있다.
  - Nav2 의 전역 플래너 플러그인(NavFn, Smac 계열, Theta*)을 로봇 형태와 요구에 맞게 고르는 기준을 말할 수 있다.
prerequisites: [m6-configuration-space-graph-search, m5-occupancy-grid-scan-matching]
difficulty: 3
estimated_minutes: 120
tags: [costmap, inflation, global-planner, nav2, a-star, navfn, smac]
activities:
  - id: m6-costmap-global-planning-reading
    kind: reading
    title: 본문과 Nav2 Navigation Concepts 읽기
    estimated_minutes: 45
  - id: m6-costmap-global-planning-quiz
    kind: quiz
    title: 비용 지도 층과 비용 값 퀴즈
    estimated_minutes: 15
  - id: m6-costmap-global-planning-exercise
    kind: exercise
    title: 팽창 파라미터와 비용 가중 A* 실험
    estimated_minutes: 60
resources:
  - title: "Nav2 Documentation"
    url: https://docs.nav2.org/rolling/index.html
    kind: article
    note: Navigation Concepts(Costmap 2D·플래너 서버), Configuration Guide 의 Costmap 2D·Inflation Layer·플래너 플러그인 항목.
  - title: "A* Planning (Stachniss)"
    url: https://www.youtube.com/watch?v=HR1TNa8Lp7w
    kind: video
    note: 레슨 1 복습. 비용 지도 위의 탐색으로 다시 본다.
  - title: "PythonRobotics (Sakai)"
    url: https://atsushisakai.github.io/PythonRobotics/
    kind: other
    note: Path Planning 모듈(그리드 기반·Hybrid A* 등) 코드 읽기.
  - title: "Planning Algorithms (LaValle)"
    url: https://lavalle.pl/planning/
    kind: book
    note: Ch. 4 구성공간(장애물 팽창의 근거), Ch. 2 탐색(선택).
---

# 비용 지도와 전역 계획(Nav2 플래너 읽기)

레슨 1의 A* 는 벽 모서리를 스치는 경로를 냈다. 점유/비점유 두 값만 보는 탐색은 "충돌하지
않는다"만 보장할 뿐, 실제 로봇이 위치 오차와 제어 오차를 안고도 안전하게 지나갈 경로는 주지 않는다.
Nav2 는 이 문제를 **비용 지도**로 푼다. 점유 격자 위에 "장애물에 얼마나 가까운가"를 비용으로 칠해
두고, 플래너가 짧으면서도 비용이 낮은 경로를 찾게 한다.

## 개념

### 비용 지도의 층

Nav2 의 Costmap 2D 는 여러 **층(layer)** 을 순서대로 합친다.

- **정적 층(static):** SLAM 으로 만든 지도(M5)를 그대로 옮긴다.
- **장애물 층(obstacle / voxel):** LiDAR·깊이 카메라의 현재 관측으로 지도에 없던 장애물을 표시하고,
  빔이 지나간 칸은 비운다(M5 역센서 모델과 같은 원리).
- **팽창 층(inflation):** 치명 칸 주변으로 비용을 퍼뜨린다.

전역 비용 지도는 `map` 프레임의 넓은 지도로 전역 계획에, 지역 비용 지도는 `odom` 프레임에서 로봇을
따라다니는 작은 창으로 다음 레슨의 지역 계획에 쓴다.

### 비용 값

칸 비용은 0–255 정수다. 254 는 **치명(lethal)**, 즉 장애물 자체다. 253 은 **내접(inscribed)** 으로,
로봇 중심이 여기 오면 몸체가 장애물에 닿는다(레슨 1의 원형 로봇 C-space 팽창). 255 는 **미지**,
0 은 자유다. 내접 반경 밖에서 팽창 반경까지는 거리에 따라 지수적으로 줄어드는 비용을 준다.
`cost_scaling_factor` 가 클수록 비용이 빨리 줄어 벽에 더 붙는 경로가 나온다.

### 전역 플래너 플러그인

Nav2 의 플래너 서버는 플러그인을 바꿔 끼운다.

- **NavFn:** 격자 위 Dijkstra/A*. 원형 로봇·차동 구동에 단순하고 견고하다.
- **Smac Planner:** 2D A*, 방향과 최소 회전 반경을 고려하는 Hybrid-A*, 상태 격자(State Lattice)
  변형이 있다. 자동차형·직사각형 로봇에 쓴다.
- **Theta\*:** 격자 칸을 건너뛰는 시야 기반 직선 연결로 꺾임이 적은 경로를 낸다.

## 핵심 수식

팽창 비용($d$ 는 가장 가까운 치명 칸까지의 거리, $r_{in}$ 은 내접 반경, $\alpha$ 는 감쇠율):

$$c(d) = \begin{cases} 254 & d = 0 \\ 253 & 0 < d \le r_{in} \\ 252\, e^{-\alpha (d - r_{in})} & r_{in} < d \le r_{inf} \\ 0 & d > r_{inf} \end{cases}$$

비용 가중 간선($w$ 는 비용 벌점 가중치):

$$c(n, n') = \lVert n' - n \rVert \left(1 + w\,\frac{c(n')}{252}\right)$$

## 예제

3 m × 4 m 공간의 벽 두 개와 상자에 팽창 층을 만들고, 벌점 가중치 0 과 3 으로 A* 를 돌린다.

```python
import heapq

import numpy as np

res = 0.05  # 5 cm 격자
occ = np.zeros((60, 80), dtype=bool)  # 3 m × 4 m, True = 점유 (정적 지도 층)
occ[0:40, 25] = True
occ[20:60, 55] = True
occ[28:32, 38:44] = True  # 가운데 상자

# 장애물 층 + 팽창 층: 각 칸에서 가장 가까운 점유 칸까지의 거리 (브루트포스 거리 변환)
rows, cols = np.indices(occ.shape)
cells = np.c_[rows.ravel(), cols.ravel()]
obs = np.argwhere(occ)
dist = np.sqrt(((cells[:, None, :] - obs[None, :, :]) ** 2).sum(-1)).min(1).reshape(occ.shape) * res

INSCRIBED, INFLATION, SCALE = 0.15, 0.6, 5.0  # 로봇 내접 반경, 팽창 반경 [m], 감쇠율
cost = np.zeros(occ.shape)
band = (dist > INSCRIBED) & (dist <= INFLATION)
cost[band] = 252 * np.exp(-SCALE * (dist[band] - INSCRIBED))  # Nav2 팽창 층과 같은 꼴
cost[dist <= INSCRIBED] = 253  # 로봇 중심이 들어가면 반드시 충돌
cost[occ] = 254  # LETHAL
MOVES = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]


def astar(cost, start, goal, weight):
    def h(n):
        return np.hypot(n[0] - goal[0], n[1] - goal[1])

    g, parent, open_list, closed = {start: 0.0}, {start: None}, [(h(start), start)], set()
    while open_list:
        _, node = heapq.heappop(open_list)
        if node in closed:
            continue
        closed.add(node)
        if node == goal:
            break
        for dr, dc in MOVES:
            nb = (node[0] + dr, node[1] + dc)
            if not (0 <= nb[0] < cost.shape[0] and 0 <= nb[1] < cost.shape[1]) or cost[nb] >= 253:
                continue
            step = np.hypot(dr, dc) * (1 + weight * cost[nb] / 252)  # 거리 × (1 + 비용 벌점)
            if g[node] + step < g.get(nb, np.inf):
                g[nb], parent[nb] = g[node] + step, node
                heapq.heappush(open_list, (g[nb] + h(nb), nb))
    path, n = [], goal
    while n is not None:
        path.append(n)
        n = parent[n]
    return np.array(path[::-1])


start, goal = (50, 5), (10, 75)
for weight in [0.0, 3.0]:
    path = astar(cost, start, goal, weight)
    length = np.linalg.norm(np.diff(path, axis=0), axis=1).sum() * res
    clearance = dist[path[:, 0], path[:, 1]]
    print(
        f"벌점 가중치 {weight}: 길이 {length:.2f} m, 최소 여유 {clearance.min():.2f} m, "
        f"평균 여유 {clearance.mean():.2f} m"
    )
```

벌점이 없으면 경로가 4.56 m 로 짧지만 내접 경계(0.15 m)에 붙어 지난다. 벌점 3 을 주면 5.30 m 로
조금 길어지는 대신 최소 여유가 0.30 m, 평균 여유가 0.63 m 로 늘어 통로 가운데를 지난다.

**연습 과제(exercise):** (1) `SCALE` 을 1, 5, 20 으로 바꿔 경로 길이와 여유의 변화를 표로 정리하라.
(2) `INFLATION` 을 내접 반경과 같게 하면 어떤 경로가 나오는가? (3) 레슨 1의 `closed` 집합 크기를
여기서도 세어 비용 가중이 탐색량에 주는 영향을 보라.

## 자가 점검 질문

1. 내접(253)과 치명(254)을 구분하는 이유는 무엇인가? 원형이 아닌 로봇에서는 어떤 차이가 생기는가?
2. 전역 비용 지도와 지역 비용 지도가 서로 다른 프레임(`map`, `odom`)을 쓰는 이유를 M5·M8 내용으로 설명하라.
3. 자동차형 로봇에 NavFn 대신 Smac Hybrid-A* 를 써야 하는 이유는?

## 확인 퀴즈

`rc quiz m6-costmap-global-planning` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m6-costmap-global-planning-quiz
questions:
  - id: q1
    type: single
    prompt: 'Costmap 2D 에서 치명(254)과 내접(253) 비용을 구분하는 이유는?'
    choices:
      - '254 는 장애물 자체, 253 은 로봇 **중심**이 그곳에 오면 몸체가 장애물에 닿는 영역이기 때문'
      - '253 은 미지 영역이기 때문'
      - '두 값은 같은 의미이고 호환성 때문에 나뉘어 있다'
      - '253 은 지역 비용 지도에만 쓰이기 때문'
    answer: 0
    explanation: '254 는 관측된 장애물 칸이고, 253 은 내접 반경 팽창 결과다. 계획은 로봇 중심의 경로를 다루므로, 중심이 253 에 들어가면 충돌이다. 원형이 아닌 로봇은 방향에 따라 실제 충돌 여부가 달라져 내접 반경 근사가 보수적이거나 위험할 수 있고, 그때는 풋프린트 기반 충돌 검사가 필요하다.'
    concept: { front: 'costmap 의 253 vs 254', back: '254 = 장애물 칸, 253 = 중심이 들어가면 몸체가 닿는 내접 팽창 영역' }
  - id: q2
    type: single
    prompt: '전역 비용 지도는 `map`, 지역 비용 지도는 `odom` 프레임을 쓰는 이유는?'
    choices:
      - '전역 계획은 절대 좌표가 필요하고, 지역 계획은 점프 없는 연속 좌표가 필요하기 때문'
      - '`odom` 프레임이 더 정확하기 때문'
      - '`map` 프레임은 회전하지 않기 때문'
      - '두 프레임의 차이는 관례일 뿐 기능 차이는 없다'
    answer: 0
    explanation: '전역 경로는 지도 위 목표까지 가야 하므로 `map` 기준이어야 한다. 반면 지역 계획·제어는 위치 추정이 보정될 때 `map → odom` 이 점프하면 명령이 튀므로, 연속적인 `odom` 기준의 작은 창을 쓴다. M5·M8 의 프레임 역할 분담과 같은 이유다.'
    concept: { front: '전역/지역 비용 지도의 프레임', back: '전역 = `map`(절대 목표), 지역 = `odom`(점프 없는 연속 좌표)' }
  - id: q3
    type: single
    prompt: '자동차형(ackermann) 로봇에 NavFn 대신 Smac Hybrid-A* 를 쓰는 이유는?'
    choices:
      - 'Hybrid-A* 가 항상 더 빠르기 때문'
      - '방향과 최소 회전 반경을 고려해 실제로 주행 가능한 경로를 내기 때문'
      - 'NavFn 은 Nav2 에서 제거되었기 때문'
      - 'Hybrid-A* 만 비용 지도를 읽을 수 있기 때문'
    answer: 1
    explanation: 'NavFn 은 $(x, y)$ 격자에서 어느 방향으로든 갈 수 있다고 보므로 제자리 회전이 가능한 차동 구동에 맞다. 자동차형 로봇은 제자리에서 돌 수 없어서 $(x, y, \theta)$ 와 최소 회전 반경을 반영하는 Hybrid-A* 나 State Lattice 가 필요하다. 그렇지 않으면 추종할 수 없는 경로가 나온다.'
```

## 이 단계 공부법

1. **문서(먼저):** Nav2 Navigation Concepts 의 Costmap·플래너 부분을 읽고 층 구조를 그림으로 그려 본다.
2. **본문 + 예제:** 예제의 `cost` 배열을 이미지로 그려 팽창 띠를 확인하고 연습 과제를 한다.
3. **설정 읽기:** Nav2 Configuration Guide 의 Inflation Layer 파라미터(`inflation_radius`,
   `cost_scaling_factor`)와 예제 변수를 1:1 로 대응시킨다.
4. **심화(선택):** PythonRobotics 의 Hybrid A* 코드를 읽고 방향을 상태에 넣으면 무엇이 바뀌는지 정리한다.

## 참고 자료

- Nav2 Documentation — <https://docs.nav2.org/rolling/index.html>
- Cyrill Stachniss, "A* Planning" — <https://www.youtube.com/watch?v=HR1TNa8Lp7w>
- Atsushi Sakai, PythonRobotics — <https://atsushisakai.github.io/PythonRobotics/>
- Steven M. LaValle, *Planning Algorithms*, Cambridge University Press — <https://lavalle.pl/planning/>
