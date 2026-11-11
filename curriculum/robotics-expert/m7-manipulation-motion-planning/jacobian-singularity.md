---
id: m7-jacobian-singularity
title: 자코비안·속도 기구학과 특이점
summary: 관절 속도를 말단 속도로, 말단 힘을 관절 토크로 바꾸는 자코비안을 유도하고, 특이점·조작성 타원체·감쇠 최소 제곱 역해로 특이점 근처의 거동을 numpy 로 확인한다.
objectives:
  - 2-link 평면 팔의 자코비안을 정기구학의 편미분으로 유도하고 $\dot{x} = J\dot{\theta}$, $\tau = J^\top F$ 의 의미를 설명할 수 있다.
  - 행렬식·특이값·조작성 지표로 특이점을 판별하고, 특이점 근처에서 관절 속도가 폭주하는 이유를 설명할 수 있다.
  - 감쇠 최소 제곱(DLS) 역해를 구현해 특이점 근처의 속도 명령을 안정화할 수 있다.
prerequisites: [m2-inverse-kinematics]
difficulty: 3
estimated_minutes: 100
tags: [manipulator, jacobian, velocity-kinematics, singularity, statics]
activities:
  - id: m7-jacobian-singularity-reading
    kind: reading
    title: 본문과 Modern Robotics Ch. 5 영상
    estimated_minutes: 35
  - id: m7-jacobian-singularity-quiz
    kind: quiz
    title: 자코비안·특이점·정역학 퀴즈
    estimated_minutes: 15
  - id: m7-jacobian-singularity-exercise
    kind: exercise
    title: 2-link 자코비안과 DLS 역해 구현
    estimated_minutes: 50
resources:
  - title: "Modern Robotics: Mechanics, Planning, and Control (Lynch, Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: Ch. 5 Velocity Kinematics and Statics(자코비안, 특이점, 조작성 타원체). 무료 preprint PDF.
  - title: "Modern Robotics 강의 영상"
    url: https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos
    kind: video
    note: Ch. 5 재생목록.
  - title: "Robotics Toolbox for Python (Corke)"
    url: https://github.com/petercorke/robotics-toolbox-python
    kind: other
    note: "`jacob0`·조작성 계산으로 손 계산 결과를 검증(선택)."
  - title: "Robotics: Modelling, Planning and Control (Siciliano, Sciavicco, Villani, Oriolo)"
    kind: book
    note: Ch. 3 미분 기구학과 정역학, 특이점·여유 자유도(심화).
---

# 자코비안·속도 기구학과 특이점

M2 에서는 "어디로 가는가"(위치)만 다뤘다. 매니퓰레이터를 실제로 움직이려면 "얼마나 빨리, 얼마의
힘으로"를 알아야 한다. 이 둘을 잇는 행렬이 **자코비안(Jacobian)** 이다. M2 의 수치 IK 에서 잠깐
등장했지만, 이 모듈의 동역학·임피던스 제어·작업 공간 궤적이 모두 이 행렬 위에 서 있으므로 여기서
제대로 정리한다.

## 개념

### 속도 기구학

정기구학 $x = f(\theta)$ 를 시간으로 미분하면 $\dot{x} = J(\theta)\dot{\theta}$ 다. $J$ 의 $i$ 번째 열은
"관절 $i$ 만 단위 속도로 돌렸을 때 말단이 움직이는 속도"다. 6자유도 팔에서는 선속도 3개와 각속도
3개를 쌓은 6×n 행렬이 되며, Modern Robotics 는 이를 트위스트로 표현한 **공간 자코비안**과
**물체 자코비안**으로 나눈다. 원리는 2-link 평면 팔과 같다.

### 정역학(statics)

말단이 환경에 힘 $F$ 를 낼 때 필요한 관절 토크는 가상일의 원리 $F^\top \dot{x} = \tau^\top \dot{\theta}$
에서 $\tau = J^\top F$ 다. 같은 행렬이 속도는 관절→말단으로, 힘은 말단→관절로 옮긴다. 이 관계는
레슨 4의 임피던스 제어에서 그대로 쓰인다.

### 특이점

$J$ 의 랭크가 떨어지는 자세가 **특이점**이다. 그 자세에서는 어떤 관절 속도로도 만들 수 없는 말단
속도 방향이 생긴다. 2-link 팔은 $\det J = l_1 l_2 \sin\theta_2$ 이므로 팔을 쭉 펴거나($\theta_2 = 0$)
완전히 접을 때($\theta_2 = \pi$) 특이하다. 특이점 근처에서 $\dot{\theta} = J^{-1}\dot{x}$ 를 쓰면 작은
말단 속도 명령에도 관절 속도가 폭주한다.

### 조작성과 감쇠 최소 제곱

$JJ^\top$ 의 고유벡터·고윳값은 단위 관절 속도로 만들 수 있는 말단 속도의 타원체(**조작성 타원체**)를
준다. 특이값 $\sigma_i$ 의 곱 $w = \sqrt{\det(JJ^\top)}$ 은 Yoshikawa 조작성 지표이고, $\sigma_{min}/\sigma_{max}$ 가
0 에 가까울수록 특이점에 가깝다. 실제 제어기는 역행렬 대신 **감쇠 최소 제곱(DLS)** 역해를 써서
정확도를 조금 버리고 관절 속도를 유한하게 묶는다.

## 핵심 수식

2-link 평면 팔($c_{12} = \cos(\theta_1 + \theta_2)$ 등):

$$J(\theta) = \begin{bmatrix} -l_1 s_1 - l_2 s_{12} & -l_2 s_{12} \\ l_1 c_1 + l_2 c_{12} & l_2 c_{12} \end{bmatrix},\qquad \det J = l_1 l_2 \sin\theta_2$$

정역학과 DLS 역해($\lambda$ 는 감쇠 계수):

$$\tau = J^\top F,\qquad \dot{\theta} = J^\top (JJ^\top + \lambda^2 I)^{-1}\dot{x}$$

## 예제

팔을 점점 펴면서 같은 말단 속도 $\dot{x} = (0.1, 0)$ m/s(팔 방향)를 요구한다.

```python
import numpy as np

L1, L2 = 1.0, 0.8


def fk(th):
    t1, t12 = th[0], th[0] + th[1]
    return np.array([L1 * np.cos(t1) + L2 * np.cos(t12), L1 * np.sin(t1) + L2 * np.sin(t12)])


def jacobian(th):
    s1, c1 = np.sin(th[0]), np.cos(th[0])
    s12, c12 = np.sin(th[0] + th[1]), np.cos(th[0] + th[1])
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]])


# 1) 수치 미분으로 해석적 자코비안 검증
th = np.array([0.4, 0.9])
eps = 1e-6
J_num = np.column_stack([(fk(th + eps * e) - fk(th - eps * e)) / (2 * eps) for e in np.eye(2)])
print("해석/수치 자코비안 최대 차이:", np.abs(jacobian(th) - J_num).max().round(9))

# 2) 특이점에 다가갈 때: 조건수와 필요한 관절 속도
xdot = np.array([0.1, 0.0])
lam = 0.05
for th2 in [1.0, 0.3, 0.1, 0.01]:
    J = jacobian(np.array([0.0, th2]))
    sv = np.linalg.svd(J, compute_uv=False)
    qd_inv = np.linalg.solve(J, xdot)
    qd_dls = J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(2), xdot)
    err = np.linalg.norm(J @ qd_dls - xdot)
    print(
        f"th2={th2:5.2f}  det={np.linalg.det(J):7.4f}  조작성={sv.prod():6.4f}  "
        f"|qd_inv|={np.linalg.norm(qd_inv):8.2f}  |qd_dls|={np.linalg.norm(qd_dls):5.2f}  "
        f"DLS 오차={err:.3f}"
    )

# 3) 정역학: 말단으로 바닥을 10 N 누르려면 관절 토크는?
th = np.array([0.5, -1.0])
F = np.array([0.0, -10.0])
print("tau = J^T F =", (jacobian(th).T @ F).round(3), "N·m")
```

$\theta_2$ 가 1.0 → 0.01 로 줄면 행렬식이 약 0.67 → 0.008 로 떨어지고, 역행렬 해의 관절 속도는
0.22 rad/s 에서 약 24.6 rad/s 로 100 배 넘게 폭주한다. DLS 해는 관절 속도를 1 rad/s 아래로 묶는
대신 오차를 받아들여, $\theta_2 = 0.01$ 에서는 팔 방향 속도를 거의 포기한다(오차 ≈ 0.1 m/s). 그
방향이 바로 펴진 팔이 낼 수 없는 방향이다. 실제 MoveIt Servo 같은 실시간 제어기도 조건수를 감시해
특이점 근처에서 속도를 줄이거나 멈춘다.

**연습 과제(exercise):** (1) $\lambda$ 를 0.01, 0.05, 0.2 로 바꿔 관절 속도 크기와 말단 속도 오차의
균형을 표로 정리하라. (2) $\theta_2 \in (0, \pi)$ 에 대해 조작성 $w$ 를 그리고 최대가 되는 $\theta_2$ 를
해석적으로 구해 확인하라($w = l_1 l_2 |\sin\theta_2|$). (3) 특이 자세 $\theta_2 = 0$ 에서 $J^\top$ 의
영공간을 구하고, 그 방향의 말단 힘이 관절 토크 없이 버텨지는 이유를 설명하라.

## 자가 점검 질문

1. 자코비안이 속도는 관절→말단으로, 힘은 말단→관절로 옮기는 이유를 가상일의 원리로 설명하라.
2. 2-link 팔의 두 특이 자세에서 만들 수 없는 말단 속도 방향은 각각 무엇인가?
3. DLS 의 $\lambda$ 를 키우면 무엇을 얻고 무엇을 잃는가?

## 확인 퀴즈

`rc quiz m7-jacobian-singularity` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m7-jacobian-singularity-quiz
questions:
  - id: q1
    type: single
    prompt: '같은 자코비안 $J$ 가 속도는 $\dot x = J\dot\theta$, 힘은 $\tau = J^\top F$ 로 쓰이는 근거는?'
    choices:
      - '우연히 같은 행렬이 나온 것이다'
      - '가상일의 원리 — 두 표현에서 일률이 같아야 하므로 $F^\top\dot x = \tau^\top\dot\theta$ 에서 전치가 나온다'
      - '$J$ 가 항상 직교 행렬이기 때문'
      - '힘과 속도가 같은 단위이기 때문'
    answer: 1
    explanation: '말단에서 계산한 일률 $F^\top \dot x$ 와 관절에서 계산한 일률 $\tau^\top\dot\theta$ 는 같아야 한다. $\dot x = J\dot\theta$ 를 넣으면 $F^\top J\dot\theta = \tau^\top\dot\theta$ 가 모든 $\dot\theta$ 에 대해 성립해야 하므로 $\tau = J^\top F$ 다. 속도는 관절→말단, 힘은 말단→관절로 간다.'
    concept: { front: '$\dot x = J\dot\theta$ 와 $\tau = J^\top F$', back: '가상일(일률 보존)에서 나온다 — 속도는 관절→말단, 힘은 말단→관절' }
  - id: q2
    type: single
    prompt: '2-link 평면 팔을 완전히 펴면($\theta_2 = 0$) 말단이 움직일 수 없는 방향은?'
    choices:
      - '팔 축에 수직인 방향(접선 방향)'
      - '팔 축 방향(반지름 방향, 더 멀어지거나 가까워지는 방향)'
      - '모든 방향'
      - '수직 방향만'
    answer: 1
    explanation: '완전히 펴면 말단은 도달 가능한 최대 반지름에 있으므로 반지름 방향으로 더 나갈 수 없다. 두 관절이 만드는 말단 속도가 모두 접선 방향이어서 $J$ 의 두 열이 평행해지고 랭크가 1로 떨어진다. 완전히 접은 자세($\theta_2 = \pi$)도 마찬가지로 반지름 방향을 잃는다.'
    concept: { front: '2-link 팔의 특이 자세', back: '$\theta_2 = 0, \pi$ — 반지름 방향 운동 불가, $J$ 의 열이 평행해져 랭크 하락' }
  - id: q3
    type: single
    prompt: '감쇠 최소 제곱(DLS)의 감쇠 계수 $\lambda$ 를 키우면?'
    choices:
      - '특이점 근처 관절 속도가 작아져 안전하지만, 말단 속도 추종 정확도가 떨어진다'
      - '정확도와 안전성이 모두 좋아진다'
      - '관절 속도가 더 커진다'
      - '특이점이 사라진다'
    answer: 0
    explanation: 'DLS 는 $J^\top(JJ^\top + \lambda^2 I)^{-1}$ 로 작은 특이값의 역수가 폭발하는 것을 막는다. $\lambda$ 가 크면 관절 속도가 확실히 유한해지지만 명령한 말단 속도를 정확히 내지 못한다. 정확도와 수치 안정성을 맞바꾸는 손잡이다.'
    concept: { front: 'DLS 의 $\lambda$ 트레이드오프', back: '크면 관절 속도 유한·안전, 말단 속도 추종 정확도 손실' }
```

## 이 단계 공부법

1. **영상(먼저):** Modern Robotics 영상 Ch. 5 에서 자코비안·특이점·조작성 타원체 부분을 본다.
2. **본문 + 예제:** 예제의 수치 미분 검증을 먼저 돌려 해석식을 믿을 수 있게 만든 뒤 특이점 표를 해석한다.
3. **교재:** Modern Robotics 5.1–5.4 절을 읽고 공간·물체 자코비안의 차이를 2-link 예로 손으로 정리한다.
4. **검증(선택):** Robotics Toolbox for Python 으로 같은 팔을 만들어 자코비안 값을 비교한다.

## 참고 자료

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 5 — <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics 강의 영상 — <https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos>
- Peter Corke, Robotics Toolbox for Python — <https://github.com/petercorke/robotics-toolbox-python>
- Bruno Siciliano 외, *Robotics: Modelling, Planning and Control*, Springer, 2009 — Ch. 3 (링크 없음)
- Tsuneo Yoshikawa, "Manipulability of Robotic Mechanisms", IJRR 1985 (조작성 지표 원논문, 링크 없음)
