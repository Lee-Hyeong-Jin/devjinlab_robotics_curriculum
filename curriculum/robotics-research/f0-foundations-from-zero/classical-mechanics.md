---
id: f0-classical-mechanics
title: 고전 역학
summary: >-
  Newton 법칙으로 운동을 세우고, 에너지·운동량 보존과 회전 운동(관성 모멘트, 토크, 각운동량)을
  다루는 수준까지 올린다. MIT 8.01SC 로 안내하는 가이드형 레슨이다.
objectives:
  - 자유물체도를 그리고 Newton 운동 방정식을 세울 수 있다.
  - 일-에너지 정리와 에너지 보존으로 운동 문제를 풀 수 있다.
  - 운동량·충격량과 충돌(탄성·비탄성)을 다룰 수 있다.
  - 관성 모멘트·토크·각운동량으로 회전 운동을 기술할 수 있다.
  - 강체의 평면 운동(병진 + 회전)을 분해해 풀 수 있다.
prerequisites: [f0-differential-equations]
difficulty: 1
estimated_minutes: 4200
tags: [foundations, mechanics, physics, guide]
activities:
  - id: f0-classical-mechanics-diagnostic
    kind: quiz
    title: 시작 전 자가 진단 (통과하면 이 레슨을 건너뛴다)
    estimated_minutes: 40
  - id: f0-classical-mechanics-lectures
    kind: reading
    title: MIT 8.01SC 강의 영상·온라인 교재 수강
    estimated_minutes: 2400
  - id: f0-classical-mechanics-problems
    kind: exercise
    title: 문제집 1-12 풀이
    estimated_minutes: 1760
resources:
  - title: "MIT 8.01SC Classical Mechanics (Fall 2016)"
    url: https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/
    kind: course
    note: 1순위. 강의 영상, 문제집 1-12, 온라인 교재, 읽기 자료 공개.
  - title: "Lynch & Park, Modern Robotics"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: ch.8 (Dynamics of Open Chains) 의 도입부만 미리 훑어 두면 이 레슨의 목적이 보인다.
---

# 고전 역학

## 도달 목표

이 레슨은 **가이드형**이다. 통과하면 건너뛴다.

**로봇은 강체 집합이고 그 운동은 역학이다.** C2(다물체 동역학)가 이 레슨의 직접적 상위 과정이고,
C3·C4(제어)는 그 운동 방정식을 조작한다. 특히 **관성 모멘트와 각운동량**, 그리고 **라그랑지안
역학으로 가는 입구인 에너지 관점**이 핵심이다. 로보틱스 문헌은 뉴턴-오일러와 라그랑주를 둘 다
쓰므로, 여기서 두 관점을 모두 보는 것이 좋다.

통과 기준은 §시작 전 자가 진단의 6문항 중 5문항 이상이다.

## 시작 전 자가 진단

`rc quiz f0-classical-mechanics` 로 푼다. 5/6 이상이면 건너뛰고 `f0-proofs-math-maturity` 로 간다.

```quiz
activity: f0-classical-mechanics-diagnostic
questions:
  - id: q1
    type: short
    prompt: "길이 $L$, 질량 $m$ 인 균일 막대를 한쪽 끝을 축으로 회전시킬 때 관성 모멘트는 $mL^2/k$ 다. $k$ 는?"
    answer: ["3", "three"]
    explanation: "$I = \\int_0^L (m/L)x^2 dx = mL^2/3$. 중심축이면 $mL^2/12$ 이고, 둘의 관계가 평행축 정리다. C2 의 관성행렬이 이 계산의 3차원 확장이다."
    concept: { front: "균일 막대의 관성 모멘트", back: "끝 축 $mL^2/3$, 중심축 $mL^2/12$. 평행축 정리로 연결된다" }
  - id: q2
    type: single
    prompt: "평행축 정리는?"
    choices:
      - "$I = I_{cm} + mL^2/12$"
      - "$I = I_{cm} + md^2$ ($d$ 는 질량중심에서 축까지 거리)"
      - "$I = I_{cm} - md^2$"
      - "$I = mI_{cm}d^2$"
    answer: 1
    explanation: "$I = I_{cm} + md^2$. C2 에서 공간 관성을 다른 프레임으로 옮길 때 쓰는 변환이 이 정리의 6차원 판이다."
    concept: { front: "평행축 정리", back: "$I = I_{cm} + md^2$ — 축을 질량중심에서 $d$ 만큼 옮기면 $md^2$ 가 더해진다" }
  - id: q3
    type: single
    prompt: "마찰 없는 경사면(각도 $\\theta$)을 미끄러지는 물체의 가속도는?"
    choices: ["$g$", "$g\\sin\\theta$", "$g\\cos\\theta$", "$g\\tan\\theta$"]
    answer: 1
    explanation: "경사 방향 성분이 $mg\\sin\\theta$ 이므로 $a = g\\sin\\theta$. 자유물체도를 그리고 축을 경사 방향으로 잡는 것이 요령이다."
    concept: { front: "경사면 위 가속도", back: "$a = g\\sin\\theta$ (마찰 없음). 축을 경사 방향으로 잡는다" }
  - id: q4
    type: single
    prompt: "외부 토크가 0 인 계에서 보존되는 양은?"
    choices: ["운동 에너지", "선운동량만", "각운동량", "관성 모멘트"]
    answer: 2
    explanation: "$\\tau_{ext}=0$ 이면 각운동량 $L = I\\omega$ 가 보존된다. 관성 모멘트가 바뀌면 $\\omega$ 가 바뀐다(피겨 스케이터). 운동 에너지는 보존되지 않을 수 있다."
    concept: { front: "각운동량 보존", back: "외부 토크 0 이면 $L=I\\omega$ 보존. $I$ 가 줄면 $\\omega$ 가 늘어난다" }
  - id: q5
    type: truefalse
    prompt: "완전 비탄성 충돌에서 운동량과 운동 에너지가 모두 보존된다."
    answer: false
    explanation: "운동량은 보존되지만 운동 에너지는 보존되지 않는다(열·변형으로 소실). 이 구분이 S3(보행)의 충격 모델에서 중요하다 — 접촉 충격이 에너지를 잃는다."
    concept: { front: "비탄성 충돌", back: "운동량 보존, 운동 에너지 비보존. 탄성 충돌은 둘 다 보존" }
  - id: q6
    type: short
    prompt: "질량 $m$, 길이 $l$ 인 단진자의 작은 진동 주기는 $T = 2\\pi\\sqrt{l/k}$ 다. $k$ 는?"
    answer: ["g", "9.8", "9.81", "중력가속도"]
    explanation: "$\\ddot\\theta + (g/l)\\sin\\theta = 0$ 을 선형화하면 각진동수 $\\sqrt{g/l}$ 이므로 $T=2\\pi\\sqrt{l/g}$ 다. 질량에 무관하다. 이 진자가 C1·C4 의 모든 예제에 쓰인다."
    concept: { front: "단진자의 소진폭 주기", back: "$T = 2\\pi\\sqrt{l/g}$ — 질량과 무관. 선형화한 결과다" }
```

## 학습 경로

**1순위 자료**: [MIT 8.01SC Classical Mechanics (Fall 2016)](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/).
강의 영상, 문제집 1–12, 온라인 교재가 공개된다.

| 단계 | 8.01 범위 | 무엇을 할 수 있게 되는가 | 예상 |
|---|---|---|---|
| 1 | 운동학과 Newton 법칙 | 자유물체도, 운동 방정식, 마찰, 원운동 | 20시간 |
| 2 | 일과 에너지 | 일-에너지 정리, 보존력과 위치 에너지, 에너지 보존 | 15시간 |
| 3 | 운동량과 충돌 | 충격량, 질량중심, 탄성·비탄성 충돌 | 12시간 |
| 4 | 회전 운동 | 관성 모멘트, 토크, 각운동량, 평행축 정리, 강체 평면 운동 | 23시간 |

합계 약 70시간. **4단계가 로보틱스와 직결된다** — 시간이 부족하면 1·4 단계를 우선한다.

## 이 단계 공부법

1. **진단을 먼저 (40분)** — 5/6 이상이면 끝이다.
2. **자유물체도를 반드시 그린다** — 역학 문제의 90%는 그림을 제대로 그리면 풀린다. 생략하고
   식부터 쓰는 습관이 뒤에서 부호 오류로 돌아온다.
3. **같은 문제를 두 관점으로 푼다 (매 단계)** — Newton(힘과 가속도)과 에너지(보존) 양쪽으로
   푼다. C2 에서 Newton–Euler 와 Lagrange 를 둘 다 쓰므로 이 습관이 그대로 쓰인다.
4. **4단계는 로봇을 생각하며 본다 (23시간)** — 관성 모멘트는 C2 의 관성행렬, 평행축 정리는
   공간 관성의 프레임 변환, 각운동량은 중심 동역학(S3)으로 이어진다.
5. **진자를 수치로 적분한다 (2시간)** — 단진자를 선형화한 해와 비선형 수치해를 비교해 진폭이
   커질 때 주기가 달라지는 것을 본다. `f0-differential-equations` 와 이어지는 지점이다.
6. **문제집으로 판정한다** — 8.01SC 문제집 1–12 를 풀고 80% 이상.

**통과 기준**: 진단 5/6 이상, 8.01SC 문제집 80% 이상, 그리고 임의의 강체 평면 운동 문제에서
자유물체도 → 운동 방정식 → 수치 적분까지 혼자 할 수 있다.
