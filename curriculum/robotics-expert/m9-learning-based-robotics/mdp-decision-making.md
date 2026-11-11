---
id: m9-mdp-decision-making
title: "의사결정과 MDP(가치 반복, 정책 반복)"
summary: 행동 결과가 확률적인 로봇의 의사결정을 마르코프 결정 과정(MDP)으로 정식화하고, 벨만 방정식을 푸는 가치 반복과 정책 반복을 미끄러지는 격자 세계에서 numpy 로 구현한다. M6 의 결정론적 그래프 탐색과 M9 의 강화학습을 잇는 다리다.
objectives:
  - 상태·행동·전이 확률·보상·할인율로 MDP 를 정의하고, 격자 경로 계획 문제를 MDP 로 바꿔 쓸 수 있다.
  - 벨만 최적 방정식을 쓰고 가치 반복과 정책 반복을 구현해 같은 최적 정책에 수렴함을 확인할 수 있다.
  - 미끄러짐 확률·단계 비용·할인율이 최적 정책(위험 회피 경로)에 주는 영향을 설명할 수 있다.
prerequisites: [m6-configuration-space-graph-search, m5-bayes-filter]
difficulty: 3
estimated_minutes: 120
tags: [mdp, bellman-equation, value-iteration, policy-iteration, decision-making, gridworld]
activities:
  - id: m9-mdp-decision-making-reading
    kind: reading
    title: 본문과 Stachniss MDP 강의
    estimated_minutes: 40
  - id: m9-mdp-decision-making-quiz
    kind: quiz
    title: 벨만 방정식과 반복 해법 퀴즈
    estimated_minutes: 20
  - id: m9-mdp-decision-making-exercise
    kind: exercise
    title: 미끄러지는 격자 세계에서 가치·정책 반복 실험
    estimated_minutes: 60
resources:
  - title: "MDPs (Stachniss)"
    url: https://www.youtube.com/watch?v=72QwRnSNY88
    kind: video
    note: Online Training – Mobile Robotics, Robotics 블록. 가치 반복을 로봇 내비게이션 맥락에서 설명.
  - title: "Planning Algorithms (LaValle)"
    url: https://lavalle.pl/planning/
    kind: book
    note: Part III Decision-Theoretic Planning(MDP·가치/정책 반복·POMDP). 무료 HTML/PDF.
  - title: "Probabilistic Robotics (Thrun, Burgard, Fox)"
    url: https://robots.stanford.edu/probabilistic-robotics/
    kind: book
    note: Markov Decision Processes 장(가치 반복과 로봇 제어). M5 와 같은 교재.
  - title: "MIT OCW 16.410 Principles of Autonomy and Decision Making"
    url: https://ocw.mit.edu/courses/16-410-principles-of-autonomy-and-decision-making-fall-2010
    kind: course
    note: 탐색·플래닝·의사결정 강의(2010). 이론 보강용(선택).
---

# 의사결정과 MDP(가치 반복, 정책 반복)

M6 의 A* 는 명령한 칸으로 반드시 간다고 가정했지만 실제 로봇은 미끄러진다. M5 가 **상태의 불확실성**을
다뤘다면 이 레슨은 **행동 결과의 불확실성**을 다룬다. 그 표준 틀이 마르코프 결정 과정(Markov Decision
Process, MDP)이고, 이어지는 강화학습은 "모델을 모르는 MDP 풀기"다.

## 개념

### MDP 의 다섯 요소

MDP 는 $(S, A, P, r, \gamma)$ 로 정의한다.

- **상태 $S$, 행동 $A$:** 격자 칸, 상·하·좌·우.
- **전이 확률 $P(s' \mid s, a)$:** 의도한 방향 0.8, 좌우로 미끄러짐 각 0.1. 다음 상태가 현재 상태와
  행동에만 달려 있다는 **마르코프 성질**이 핵심 가정이다.
- **보상 $r$:** 목표 +1, 구덩이 −1, 그 밖의 칸은 −0.04(시간 비용).
- **할인율 $\gamma \in [0, 1)$:** 먼 미래 보상을 덜 쳐 주어 무한 합을 유한하게 만든다.

해는 경로가 아니라 **정책(policy)** $\pi(s)$, 즉 "어느 칸에서든 무엇을 할지"의 표다. 미끄러져 계획에
없던 칸에 가도 정책이 답을 준다.

### 가치 함수와 벨만 방정식

상태 가치 $V^\pi(s)$ 는 $s$ 에서 $\pi$ 를 따를 때의 기대 할인 보상 합이다. 최적 가치 $V^*$ 는 "한 걸음 해 보고
나머지는 최적으로"라는 **벨만 최적 방정식**을 만족하며, 대표 해법이 둘이다.

- **가치 반복(value iteration):** 벨만 식을 대입 갱신으로 반복한다. 매 스윕마다 오차가 최소 $\gamma$ 배로
  줄어드는 축약(contraction)이라 수렴이 보장된다.
- **정책 반복(policy iteration):** (1) 현재 정책의 가치를 선형 방정식으로 정확히 구하고(정책 평가),
  (2) 그 가치에 대해 탐욕적으로 정책을 바꾼다(정책 개선). 반복 횟수는 적지만 매번 $|S| \times |S|$
  연립방정식을 푼다.

$P$ 를 모르면 강화학습으로, 상태조차 확실히 모르면 belief 위의 MDP(POMDP)로 확장된다.

## 핵심 수식

가치 반복 갱신(벨만 최적 방정식):

$$V_{k+1}(s) = \max_a \sum_{s'} P(s' \mid s, a)\,\big[r(s') + \gamma V_k(s')\big]$$

정책 평가(벨만 기대 방정식의 행렬 형태)와 정책 개선:

$$V^\pi = (I - \gamma P_\pi)^{-1} P_\pi r,\qquad \pi'(s) = \arg\max_a \sum_{s'} P(s' \mid s, a)\big[r(s') + \gamma V^\pi(s')\big]$$

## 예제

4 × 4 격자를 두 방법으로 풀어 비교한다.

```python
import numpy as np

# 4 × 4 격자. G = 목표(+1), P = 구덩이(-1), # = 벽. 나머지 칸으로의 이동은 -0.04
LAYOUT = ["...G", ".#.P", "....", "...."]
MOVES = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # ↑ → ↓ ←
NAMES = "↑→↓←"
GAMMA, STEP_COST = 0.95, -0.04
states = [(r, c) for r in range(4) for c in range(4) if LAYOUT[r][c] != "#"]
idx = {s: i for i, s in enumerate(states)}
N = len(states)
R = np.array([{"G": 1.0, "P": -1.0}.get(LAYOUT[r][c], STEP_COST) for r, c in states])


def move(s, a):
    r, c = s[0] + MOVES[a][0], s[1] + MOVES[a][1]
    ok = 0 <= r < 4 and 0 <= c < 4 and LAYOUT[r][c] != "#"
    return (r, c) if ok else s  # 벽·경계에 막히면 제자리


# 전이 확률 P[a, s, s']: 의도한 방향 0.8, 좌우로 미끄러짐 각 0.1. R[s'] 는 도착 칸의 보상
P = np.zeros((4, N, N))
for a in range(4):
    for s in states:
        if LAYOUT[s[0]][s[1]] in "GP":
            continue  # 종료 상태: 나가는 전이가 없으므로 V = 0 으로 남는다
        for a2, p in [(a, 0.8), ((a - 1) % 4, 0.1), ((a + 1) % 4, 0.1)]:
            P[a, idx[s], idx[move(s, a2)]] += p


def value_iteration(tol=1e-8):
    V, sweeps = np.zeros(N), 0
    while True:
        Q = P @ (R + GAMMA * V)  # Q[a, s] = Σ_s' P(s'|s,a) [r(s') + γ V(s')]
        sweeps += 1
        if np.abs(Q.max(axis=0) - V).max() < tol:
            return Q.max(axis=0), Q.argmax(axis=0), sweeps
        V = Q.max(axis=0)


def policy_iteration():
    pi, rounds = np.zeros(N, dtype=int), 0
    while True:
        P_pi = P[pi, np.arange(N)]  # 정책이 고른 행동의 전이 행렬 (N × N)
        V = np.linalg.solve(np.eye(N) - GAMMA * P_pi, P_pi @ R)  # 정책 평가
        pi_new = (P @ (R + GAMMA * V)).argmax(axis=0)  # 정책 개선(탐욕)
        rounds += 1
        if np.array_equal(pi_new, pi):
            return V, pi, rounds
        pi = pi_new


V_vi, pi_vi, sweeps = value_iteration()
V_pi, pi_pi, rounds = policy_iteration()
print(f"가치 반복 {sweeps}회, 정책 반복 {rounds}회, 가치 차 {np.abs(V_vi - V_pi).max():.0e}")
for r in range(4):
    cells = [LAYOUT[r][c] * 5 for c in range(4)]
    for c in range(4):
        if LAYOUT[r][c] == ".":
            i = idx[(r, c)]
            cells[c] = f"{NAMES[pi_vi[i]]}{V_vi[i]:+.2f}"
    print(" ".join(cells))
```

출력:

```text
가치 반복 42회, 정책 반복 5회, 가치 차 1e-08
→+0.72 →+0.83 →+0.94 GGGGG
↑+0.63 ##### ↑+0.64 PPPPP
↑+0.53 ←+0.44 ↑+0.52 ↓+0.30
↑+0.44 ↑+0.38 ↑+0.42 ←+0.34
```

두 방법은 같은 정책에 도달한다. 구덩이 바로 아래 칸 (2, 3) 의 최적 행동이 위가 아니라 **아래**다. 위로 가면
0.8 확률로 구덩이에 빠지므로 물러나서 돌아가는 길을 고른다. 결정론적 A* 는 이런 위험 회피를 표현하지 못한다.

**연습 과제(exercise):** (1) `STEP_COST` 를 −0.4 로 바꿔 정책이 구덩이 옆 지름길로 바뀌는지 보라. (2) 미끄러짐을
0 으로 하면 M6 의 최단 경로와 같아지는가? (3) $\gamma$ 를 0.5·0.99 로 바꿔 스윕 수를 기록하라.

## 자가 점검 질문

1. A* 의 "경로"와 MDP 의 "정책"은 무엇이 다르며, 미끄러짐이 있으면 왜 정책이 필요한가?
2. 가치 반복이 수렴하는 이유를 축약(contraction)과 $\gamma < 1$ 로 설명하라. $\gamma$ 가 1 에 가까우면 무엇이 느려지는가?
3. 정책 반복은 반복 횟수가 훨씬 적은데도 큰 상태 공간에서 항상 더 빠르지는 않다. 왜인가?

## 이 단계 공부법

1. **영상(먼저):** Stachniss "MDPs" 로 전체 흐름을 잡는다.
2. **본문 + 예제:** 스윕마다 `V` 를 출력해 가치가 목표에서 퍼지는 모습을 M6 Dijkstra 와 비교한다.
3. **손 계산:** 칸 (0, 2) 의 벨만 갱신 한 번을 손으로 계산해 코드와 맞춘다.
4. **심화(선택):** LaValle Part III 와 *Probabilistic Robotics* 의 MDP·POMDP 장을 읽는다.

## 참고 자료

- Cyrill Stachniss, "MDPs" — <https://www.youtube.com/watch?v=72QwRnSNY88>
- Steven M. LaValle, *Planning Algorithms*, Part III — <https://lavalle.pl/planning/>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, MIT Press —
  <https://robots.stanford.edu/probabilistic-robotics/>
- MIT OCW 16.410 Principles of Autonomy and Decision Making —
  <https://ocw.mit.edu/courses/16-410-principles-of-autonomy-and-decision-making-fall-2010>
