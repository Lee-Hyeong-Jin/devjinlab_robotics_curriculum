---
id: m7-manipulator-motion-planning
title: "매니퓰레이터 동작 계획: 구성공간 장애물과 OMPL"
summary: 작업 공간의 장애물이 관절 구성공간에서 어떤 모양의 장애물이 되는지 2-link 팔로 직접 계산하고, 원환 위 격자 A* 로 충돌 없는 관절 경로를 찾는다. 이어서 고차원 팔에서 쓰는 OMPL 샘플링 플래너와 계획 → 평활화 → 시간 매개화 파이프라인을 정리한다.
objectives:
  - 작업 공간 장애물을 링크 충돌 검사로 관절 구성공간 장애물 $C_{obs}$ 로 옮기고, 관절각의 원환(torus) 위상을 설명할 수 있다.
  - 2자유도 팔의 구성공간에서 격자 A* 로 충돌 없는 경로를 찾고, 6자유도 이상에서 샘플링 기반 플래너가 필요한 이유를 설명할 수 있다.
  - OMPL 의 주요 플래너(RRTConnect·RRT*·PRM)와 MoveIt 2 의 계획 → 평활화 → 시간 매개화 흐름을 설명할 수 있다.
prerequisites: [m7-trajectory-generation, m6-sampling-based-planning]
difficulty: 4
estimated_minutes: 120
tags: [manipulator, motion-planning, configuration-space, collision-checking, ompl]
activities:
  - id: m7-manipulator-motion-planning-reading
    kind: reading
    title: 본문과 Modern Robotics Ch. 10 영상
    estimated_minutes: 40
  - id: m7-manipulator-motion-planning-quiz
    kind: quiz
    title: 구성공간 장애물·OMPL 플래너 퀴즈
    estimated_minutes: 15
  - id: m7-manipulator-motion-planning-exercise
    kind: exercise
    title: 2-link 팔 C_obs 계산과 관절 공간 경로 계획
    estimated_minutes: 65
resources:
  - title: "Modern Robotics: Mechanics, Planning, and Control (Lynch, Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: Ch. 10 Motion Planning(10.2 구성공간 장애물, 10.5 샘플링 기반 계획).
  - title: "Modern Robotics Ch. 10 Motion Planning 영상"
    url: https://www.youtube.com/playlist?list=PLggLP4f-rq01Q3clJrnWFPRtpUwSlr4mG
    kind: video
    note: Ch. 10 재생목록, 49:36.
  - title: "Planning Algorithms (LaValle)"
    url: https://lavalle.pl/planning/
    kind: book
    note: Ch. 4 구성공간(원환·위상), Ch. 5 샘플링 기반 계획.
  - title: "Robotic Manipulation (Tedrake)"
    url: https://manipulation.mit.edu/
    kind: book
    note: Motion Planning 장(충돌 회피 IK·샘플링 플래너·궤적 최적화).
  - title: "Michigan AutoRob"
    url: https://autorob.org/
    kind: course
    note: URDF 팔에서 RRT-Connect·충돌 검사 프로젝트(선택).
---

# 매니퓰레이터 동작 계획: 구성공간 장애물과 OMPL

M6 에서 이동 로봇의 구성공간은 장애물을 부풀린 평면이었다. 매니퓰레이터의 구성은 관절각 벡터이고,
작업 공간의 공 하나가 관절 공간에서는 휘어진 띠가 된다. 이 레슨은 그 모양을 직접 계산하고, 6관절
팔에서 OMPL 을 쓰는 이유로 연결한다.

## 개념

### 관절 구성공간과 $C_{obs}$

회전 관절 $n$ 개의 구성공간은 원환 $T^n$ 이다. $-\pi$ 와 $\pi$ 가 같은 점이라 격자도 양 끝이 이어진다.
어느 링크든 장애물과 겹치면 $\theta \in C_{obs}$ 다. 정기구학이 비선형이라 $C_{obs}$ 는 볼록하지 않고,
링크끼리의 **자기 충돌**도 포함된다.

### 차원과 충돌 검사

6자유도에서 관절당 100칸이면 $10^{12}$ 칸이므로 실제 팔은 M6 의 샘플링 기반 계획을 쓰고, 병목은
**충돌 검사**가 된다. MoveIt 2 는 FCL 로 링크 충돌 형상과 플래닝 씬 물체의 충돌을 검사하고, SRDF 의
"충돌 안 함" 링크 쌍으로 불필요한 자기 충돌 검사를 건너뛴다.

### OMPL 과 계획 파이프라인

**OMPL(Open Motion Planning Library)** 은 RRTConnect, RRT*, PRM, KPIECE 같은 샘플링 플래너 모음이고,
충돌 검사는 MoveIt 2 가 제공한다. MoveIt 2 기본은 양방향 나무의 RRTConnect 이며, 직선·원호 동작에는
Pilz, 매끄러움이 중요하면 CHOMP·STOMP 를 고른다. 전체 흐름은 다음과 같다.

1. **계획:** 충돌 없는 경로점 열(자세 목표는 IK 로 변환).
2. **단순화:** 지름길 잇기(M6).
3. **시간 매개화:** 한계로 시간 부여(레슨 3).
4. **실행:** ros2_control 궤적 컨트롤러(다음 레슨).

## 핵심 수식

구성공간 장애물($A(\theta)$ 는 구성 $\theta$ 에서 로봇이 차지하는 영역, $\mathcal{O}$ 는 장애물):

$$C_{obs} = \{\theta \in T^n \mid A(\theta) \cap \mathcal{O} \neq \varnothing\},\qquad C_{free} = T^n \setminus C_{obs}$$

원환 위 관절 거리(격자 휴리스틱): $d_i = \min(|\theta_i - \theta_i'|,\, 2\pi - |\theta_i - \theta_i'|)$.

## 예제

```python
import heapq

import numpy as np

L1, L2 = 1.0, 0.8
OBST = np.array([[1.0, 0.9, 0.3], [-0.2, -1.2, 0.3]])  # 작업 공간 원형 장애물 (cx, cy, r)
N = 180  # 관절당 격자 수 (2° 간격)
th = np.linspace(-np.pi, np.pi, N, endpoint=False)


def link_points(q1, q2, n=15):
    """두 링크 위 표본점들의 (x, y)."""
    s = np.linspace(0, 1, n)
    q1, q2 = np.asarray(q1)[..., None], np.asarray(q2)[..., None]
    ex, ey = L1 * np.cos(q1), L1 * np.sin(q1)
    p1 = np.stack([s * ex, s * ey], -1)
    p2 = np.stack([ex + s * L2 * np.cos(q1 + q2), ey + s * L2 * np.sin(q1 + q2)], -1)
    return np.concatenate([p1, p2], axis=-2)


def in_collision(q1, q2):
    pts = link_points(q1, q2)
    d = np.linalg.norm(pts[..., None, :] - OBST[:, :2], axis=-1)
    return (d < OBST[:, 2]).any(axis=(-1, -2))


# 1) 구성공간 장애물 C_obs 를 격자로 계산
Q1, Q2 = np.meshgrid(th, th, indexing="ij")
C_obs = in_collision(Q1, Q2)
ws = (OBST[:, 2] ** 2).sum() / ((L1 + L2) ** 2 - (L1 - L2) ** 2)
print(f"장애물이 가린 작업 공간 {ws * 100:.1f}% → 충돌하는 관절 구성 {C_obs.mean() * 100:.1f}%")


def idx(q):
    return tuple(np.round((np.asarray(q) + np.pi) / (2 * np.pi) * N).astype(int) % N)


# 2) 관절 공간 직선 보간이 막히는지 확인
qa, qb = np.array([-0.3, 0.2]), np.array([1.6, -0.4])
line = np.linspace(qa, qb, 200)
print("시작/목표 충돌:", bool(in_collision(*qa)), bool(in_collision(*qb)))
print("관절 공간 직선 경로 충돌:", bool(in_collision(line[:, 0], line[:, 1]).any()))


# 3) 원환 격자 위 A* (-π 와 π 가 이웃)
def astar(start, goal):
    def h(a):
        d = np.abs(np.subtract(a, goal))
        return float(np.hypot(*np.minimum(d, N - d)))

    openq, came, cost = [(h(start), start)], {start: None}, {start: 0.0}
    nbrs = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]
    while openq:
        _, cur = heapq.heappop(openq)
        if cur == goal:
            path = []
            while cur is not None:
                path.append(cur)
                cur = came[cur]
            return path[::-1]
        for di, dj in nbrs:
            nxt = ((cur[0] + di) % N, (cur[1] + dj) % N)
            if C_obs[nxt]:
                continue
            c = cost[cur] + np.hypot(di, dj)
            if c < cost.get(nxt, np.inf):
                cost[nxt], came[nxt] = c, cur
                heapq.heappush(openq, (c + h(nxt), nxt))
    return None


path = astar(idx(qa), idx(qb))
q_path = np.unwrap(th[np.array(path)], axis=0)
length = np.linalg.norm(np.diff(q_path, axis=0), axis=1).sum()
print(f"A* 경로: {len(path)} 점, 관절 공간 길이 {length:.2f} rad")
print(f"직선 거리(하한) {np.linalg.norm(qb - qa):.2f} rad")
fine = np.concatenate([np.linspace(a, b, 5) for a, b in zip(q_path[:-1], q_path[1:])])
print("세밀 재검사 충돌:", bool(in_collision(fine[:, 0], fine[:, 1]).any()))
```

두 원은 작업 공간의 약 5.6% 지만 관절 구성은 약 15.6% 를 막는다. 링크 전체가 피해야 하기 때문이다.
관절 공간 직선(1.99 rad)은 막혀 있고 A* 는 약 4.68 rad 의 우회 경로를 찾으며, 촘촘히 재검사해도
충돌이 없다. 계단식 경로라 실제로는 단순화와 시간 매개화를 거친다.

**연습 과제(exercise):** (1) `C_obs` 를 이미지로 그려 띠 모양을 확인하라. (2) M6 의 RRT 를 이 관절
공간으로 옮겨 A* 와 비교하라. (3) 반지름을 0.4 m 로 키워 시작·목표가 끊기는지 확인하라.

## 자가 점검 질문

1. 작은 작업 공간 장애물이 넓은 관절 영역을 막는 이유는?
2. 관절각 격자에서 $-\pi$ 와 $\pi$ 를 이어 주지 않으면 어떤 경로를 놓치는가?
3. MoveIt 2 가 계획 결과에 단순화와 시간 매개화를 거치는 이유는?

## 확인 퀴즈

`rc quiz m7-manipulator-motion-planning` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m7-manipulator-motion-planning-quiz
questions:
  - id: q1
    type: single
    prompt: '작업 공간의 작은 장애물 하나가 관절 구성공간에서는 넓은 영역을 막을 수 있는 이유는?'
    choices:
      - '충돌 검사가 보수적으로 근사하기 때문'
      - '여러 링크 중 어느 하나라도 그 장애물과 겹치면 충돌이고, 정기구학이 비선형이라 그런 구성들이 $C_{obs}$ 에 넓게 흩어지기 때문'
      - '관절 한계 때문'
      - '격자 해상도가 낮기 때문'
    answer: 1
    explanation: '$C_{obs} = \{\theta \mid A(\theta) \cap \mathcal{O} \neq \varnothing\}$ 에서 $A(\theta)$ 는 팔 전체가 차지하는 영역이다. 서로 멀리 떨어진 관절 조합들이 같은 장애물에 닿을 수 있고, 매핑이 비선형이라 $C_{obs}$ 는 볼록하지도 연결되어 있지도 않다. 자기 충돌까지 더해진다.'
    concept: { front: '작업 공간 장애물 → $C_{obs}$', back: '링크 중 하나라도 겹치면 충돌 + 비선형 FK → 관절 공간에 넓고 비볼록한 금지 영역' }
  - id: q2
    type: single
    prompt: '회전 관절의 격자에서 $-\pi$ 와 $\pi$ 를 잇지 않으면 무엇을 놓치는가?'
    choices:
      - '관절 한계를 넘는 경로'
      - '$\pi$ 를 지나 한 바퀴 돌아가는 더 짧은 경로'
      - '자기 충돌이 있는 경로'
      - '아무것도 놓치지 않는다'
    answer: 1
    explanation: '회전 관절의 구성공간은 원환($T^n$)이라 $-\pi$ 와 $\pi$ 는 같은 자세다. 양 끝을 끊어 두면 $\theta = 3.1$ 에서 $-3.1$ 로 가는 짧은 이동을 "거의 한 바퀴 되돌아가는" 경로로만 표현하게 되어 최적해를 놓친다(각도 감기와 같은 이야기).'
    concept: { front: '관절 구성공간은 원환', back: '$-\pi$ 와 $\pi$ 는 같은 점 — 양 끝을 이어야 짧은 경로를 찾는다' }
  - id: q3
    type: single
    prompt: 'MoveIt 2 가 플래너 출력에 단순화와 시간 매개화를 덧붙이는 이유는?'
    choices:
      - '샘플링 플래너의 경로는 구불구불하고 시간 정보가 없어, 그대로는 컨트롤러가 실행할 수 없기 때문'
      - '충돌 검사를 건너뛰기 위해'
      - 'IK 를 다시 풀기 위해'
      - 'URDF 를 갱신하기 위해'
    answer: 0
    explanation: 'RRTConnect 같은 플래너는 충돌 없는 경로점 열만 준다. 지름길 잇기로 불필요한 꺾임을 없애고, 속도·가속도 한계로 각 점에 `time_from_start` 를 붙여야 `joint_trajectory_controller` 가 보간해 실행할 수 있다(경로 → 궤적).'
```

## 이 단계 공부법

1. **영상(먼저):** Modern Robotics Ch. 10 영상의 구성공간 장애물 부분을 본다.
2. **본문 + 예제:** 연습 (1) 의 그림을 꼭 그린다. 매니퓰레이터 계획의 직관이 이 그림에 있다.
3. **교재:** LaValle Ch. 4 의 원환 위상과 Ch. 5 의 충돌 검사 해상도를 읽는다.
4. **심화(선택):** Tedrake 의 Motion Planning 장, AutoRob 의 RRT-Connect 프로젝트.

## 참고 자료

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 10 — <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics Ch. 10 Motion Planning 영상 — <https://www.youtube.com/playlist?list=PLggLP4f-rq01Q3clJrnWFPRtpUwSlr4mG>
- Steven M. LaValle, *Planning Algorithms* — <https://lavalle.pl/planning/>
- Russ Tedrake, *Robotic Manipulation* — <https://manipulation.mit.edu/>
- University of Michigan, AutoRob — <https://autorob.org/>
- Ioan A. Şucan, Mark Moll, Lydia E. Kavraki, "The Open Motion Planning Library", IEEE Robotics & Automation Magazine 2012 (OMPL 논문, 링크 없음)
