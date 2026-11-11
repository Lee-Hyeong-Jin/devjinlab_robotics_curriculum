---
id: m2-dh-parameters
title: DH 파라미터
summary: Denavit–Hartenberg 규약으로 링크와 관절 사이의 관계를 네 개의 파라미터로 기술하고 동차 변환 행렬로 바꾼다.
objectives:
  - 링크 길이, 링크 비틀림, 링크 오프셋, 관절 각의 의미를 설명할 수 있다.
  - 표준(classic) DH 와 수정(modified, Craig) DH 규약의 차이를 구분할 수 있다.
  - 2-link 평면 매니퓰레이터의 DH 테이블을 작성하고 링크별 변환 행렬을 구성할 수 있다.
prerequisites: [m1-coordinate-transforms]
difficulty: 3
estimated_minutes: 75
tags: [kinematics, manipulator, dh]
activities:
  - id: m2-dh-parameters-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 40
  - id: m2-dh-parameters-quiz
    kind: quiz
    title: DH 파라미터 의미 퀴즈
    estimated_minutes: 15
  - id: m2-dh-parameters-exercise
    kind: exercise
    title: 2-link 매니퓰레이터 DH 테이블 작성
    estimated_minutes: 20
resources:
  - title: "Robot Modeling and Control, 2nd ed. (Spong, Hutchinson, Vidyasagar)"
    kind: book
    note: 3장 표준 DH 좌표계 배치 절차. 이 레슨의 기준 규약.
  - title: "Introduction to Robotics: Mechanics and Control, 4th ed. (John J. Craig)"
    kind: book
    note: 3장 수정(modified) DH. 규약 차이에 주의.
  - title: "Stanford CS223A Introduction to Robotics (Oussama Khatib)"
    url: https://see.stanford.edu/Course/CS223A
    kind: course
    note: 운동학 강의 중 DH 프레임 배치.
  - title: "Modern Robotics, 부록 C Denavit-Hartenberg Parameters (Lynch & Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: DH 와 PoE 비교(선택).
---

# DH 파라미터

로봇 팔은 링크(강체)와 관절이 사슬처럼 이어진 구조다. 말단의 자세를 구하려면 인접한
링크 좌표계 사이의 변환을 차례로 곱하면 되는데(M1 좌표 변환), 일반적인 변환은 6개 숫자가
필요하다. **Denavit–Hartenberg(DH) 규약**은 좌표계를 놓는 규칙을 정해 이것을 **4개**로
줄인다. 1955년에 제안된 이래 교재, 로봇 제조사 데이터시트, 시뮬레이터에서 가장 널리
쓰이는 매니퓰레이터 기술 방식이다.

## 개념

### 좌표계 배치 규칙 (표준 DH)

관절 $i$ 마다 좌표계 $\{i\}$ 를 다음처럼 붙인다.

1. $z_{i-1}$ 축은 관절 $i$ 의 회전축(회전 관절) 또는 이동 방향(직동 관절)에 놓는다.
2. $x_i$ 축은 $z_{i-1}$ 과 $z_i$ 의 **공통 수선** 방향으로, $z_{i-1}$ 에서 $z_i$ 를 향하게 놓는다.
3. $y_i$ 는 오른손 좌표계가 되도록 정한다.

### 네 파라미터

| 기호 | 이름 | 의미 |
|---|---|---|
| $\theta_i$ | 관절 각 (joint angle) | $z_{i-1}$ 축 둘레로 $x_{i-1}$ 에서 $x_i$ 까지의 각도 |
| $d_i$ | 링크 오프셋 (link offset) | $z_{i-1}$ 축을 따라 잰 거리 |
| $a_i$ | 링크 길이 (link length) | $x_i$ 축(공통 수선)을 따라 잰 두 $z$ 축 사이 거리 |
| $\alpha_i$ | 링크 비틀림 (link twist) | $x_i$ 축 둘레로 $z_{i-1}$ 에서 $z_i$ 까지의 각도 |

회전 관절이면 $\theta_i$ 가 변수이고 나머지 셋은 상수, 직동 관절이면 $d_i$ 가 변수다.

### 표준 DH vs 수정 DH

Craig 교재는 좌표계 $\{i\}$ 를 관절 $i$ 축에 붙이는 **수정(modified) DH** 를 쓰며,
파라미터 이름도 $a_{i-1}, \alpha_{i-1}, d_i, \theta_i$ 이고 곱하는 순서가 다르다. 두 규약을
섞으면 틀린 결과가 나오므로, 데이터시트나 코드를 볼 때 어느 규약인지 먼저 확인하자.
Modern Robotics 는 DH 대신 지수 곱(PoE) 공식을 주로 쓰고 DH 는 부록 C 에서 다룬다.

## 핵심 수식

표준 DH 에서 링크 변환은 $z$ 축 회전·이동 후 $x$ 축 이동·회전이다.

$$T_{i-1,i} = \mathrm{Rot}_z(\theta_i)\,\mathrm{Trans}_z(d_i)\,\mathrm{Trans}_x(a_i)\,\mathrm{Rot}_x(\alpha_i)$$

$$T_{i-1,i} = \begin{bmatrix}
\cos\theta_i & -\sin\theta_i\cos\alpha_i & \sin\theta_i\sin\alpha_i & a_i\cos\theta_i \\
\sin\theta_i & \cos\theta_i\cos\alpha_i & -\cos\theta_i\sin\alpha_i & a_i\sin\theta_i \\
0 & \sin\alpha_i & \cos\alpha_i & d_i \\
0 & 0 & 0 & 1
\end{bmatrix}$$

## 예제

링크 길이 $L_1, L_2$ 인 평면 2-link 팔(두 회전 관절, 축은 모두 지면에 수직)의 DH 테이블:

| $i$ | $\theta_i$ | $d_i$ | $a_i$ | $\alpha_i$ |
|---|---|---|---|---|
| 1 | $\theta_1$ (변수) | 0 | $L_1$ | 0 |
| 2 | $\theta_2$ (변수) | 0 | $L_2$ | 0 |

모든 $z$ 축이 평행하므로 $\alpha_i = 0$, 같은 평면에 있으므로 $d_i = 0$ 이다. 위 행렬에
$\alpha = 0$, $d = 0$ 을 넣으면 각 링크 변환은 "평면 회전 $\theta_i$ 후 $x$ 방향 $L_i$ 이동"
이 된다.

```python
import numpy as np


def dh(theta, d, a, alpha):
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array(
        [
            [ct, -st * ca, st * sa, a * ct],
            [st, ct * ca, -ct * sa, a * st],
            [0.0, sa, ca, d],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )


L1, L2 = 0.5, 0.3
T01 = dh(np.deg2rad(30), 0, L1, 0)
T12 = dh(np.deg2rad(45), 0, L2, 0)
print((T01 @ T12)[:3, 3].round(4))  # 말단 위치 → 다음 레슨(정기구학)
```

**연습 과제(exercise):** 같은 팔에 세 번째 회전 관절(길이 $L_3$)을 추가한 3-link 평면 팔과,
바닥 회전 관절 위에 2-link 팔을 세운 구조(첫 관절 $\alpha_1 = 90^\circ$)의 DH 테이블을
작성하고, `dh()` 함수로 몇 가지 관절 각에서 말단 위치를 계산해 손계산과 비교하라.

## 자가 점검 질문

1. 회전 관절과 직동 관절에서 각각 어느 DH 파라미터가 변수가 되는가?
2. 두 관절 축이 평행할 때와 서로 수직으로 교차할 때 $a_i$, $\alpha_i$ 는 어떤 값이 되는가?
3. Craig 교재의 DH 테이블을 표준 DH 공식에 그대로 넣으면 왜 틀린 결과가 나오는가?

## 확인 퀴즈

`rc quiz m2-dh-parameters` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m2-dh-parameters-quiz
questions:
  - id: q1
    type: single
    prompt: '표준 DH 에서 **회전 관절(revolute joint)** 의 변수가 되는 파라미터는?'
    choices:
      - '$\theta_i$ (관절 각)'
      - '$d_i$ (링크 오프셋)'
      - '$a_i$ (링크 길이)'
      - '$\alpha_i$ (링크 비틀림)'
    answer: 0
    explanation: '회전 관절은 $z_{i-1}$ 축 둘레로 돌므로 $\theta_i$ 가 변수이고 나머지 셋은 링크 구조가 정하는 상수다. 직동 관절(prismatic)이면 $d_i$ 가 변수가 된다.'
    concept: { front: 'DH 파라미터 중 관절 변수', back: '회전 관절은 $\theta_i$, 직동 관절은 $d_i$ — 나머지 셋은 구조 상수' }
  - id: q2
    type: single
    prompt: '두 관절 축 $z_{i-1}$ 과 $z_i$ 가 서로 평행할 때 링크 비틀림 $\alpha_i$ 는?'
    choices:
      - '$0$ (또는 $180^\circ$)'
      - '$90^\circ$ 로 고정'
      - '관절 각과 같다'
      - '정의할 수 없다'
    answer: 0
    explanation: '$\alpha_i$ 는 공통 수선 둘레로 $z_{i-1}$ 에서 $z_i$ 까지 재는 각도다. 두 축이 평행하면 비틀림이 없으므로 $0$(같은 방향) 또는 $180^\circ$(반대 방향)다. 두 축이 수직으로 교차하면 $a_i = 0$, $\alpha_i = \pm 90^\circ$ 가 된다.'
  - id: q3
    type: truefalse
    prompt: 'Craig 교재의 DH 테이블을 표준 DH 공식에 그대로 넣어도 같은 결과가 나온다.'
    answer: false
    explanation: 'Craig 는 좌표계를 관절 $i$ 축에 붙이는 수정(modified) DH 규약을 쓴다. 파라미터 첨자($a_{i-1}, \alpha_{i-1}$)와 변환을 곱하는 순서가 달라서, 두 규약을 섞으면 틀린 변환이 나온다. 데이터시트나 코드를 볼 때 어느 규약인지 먼저 확인해야 한다.'
    concept: { front: '표준 DH vs 수정(Craig) DH', back: '좌표계를 붙이는 위치·파라미터 첨자·곱 순서가 다르다 — 섞어 쓰면 틀린다' }
```

## 이 단계 공부법

1. **교재(주):** Spong 등 *Robot Modeling and Control* 3장 또는 Craig 3장 중 하나를 골라 DH 좌표계 배치 절차를 읽는다. 두 책의 규약이 다르므로 **한 권만** 기준으로 삼는다(이 레슨은 표준 DH = Spong 방식).
2. **영상:** Stanford CS223A(Khatib) 강의 중 DH 좌표계 배치를 다루는 운동학 강의를 본다.
3. **본문 + 예제:** 2-link DH 테이블을 직접 채운 뒤 `dh()` 코드를 실행해 본다.
4. **문제:** 확인 퀴즈 → 연습 과제(3-link 평면 팔, 바닥 회전 + 2-link 팔 DH 테이블) 순으로 푼다.
5. **비교(선택):** Modern Robotics 부록 C 를 읽고 DH 와 PoE 표현의 차이를 한 문단으로 정리해 둔다. 다음 레슨(정기구학)에서 이 테이블을 그대로 쓴다.

## 참고 자료

- John J. Craig, *Introduction to Robotics: Mechanics and Control*, 4th ed., Pearson —
  3장 "Manipulator Kinematics" (수정 DH).
- Mark W. Spong, Seth Hutchinson, M. Vidyasagar, *Robot Modeling and Control*, 2nd ed.,
  Wiley, 2020 — 3장 (표준 DH).
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, 부록 C "Denavit–Hartenberg Parameters" —
  <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Oussama Khatib, Stanford CS223A *Introduction to Robotics* (강의 영상) —
  <https://see.stanford.edu/Course/CS223A>
