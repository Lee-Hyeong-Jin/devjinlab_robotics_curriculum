---
id: m2-inverse-kinematics
title: 역기구학 (Inverse Kinematics)
summary: 원하는 말단 위치에 도달하는 관절 값을 해석적 방법과 자코비안 기반 수치 방법으로 구하고, 해의 개수와 특이점을 이해한다.
objectives:
  - 2-link 평면 팔의 역기구학을 해석적으로 풀고 elbow-up / elbow-down 두 해를 구할 수 있다.
  - 도달 불가능한 목표와 특이점(singularity)을 판별할 수 있다.
  - 자코비안을 이용한 뉴턴–랩슨 방식의 수치 역기구학을 구현할 수 있다.
prerequisites: [m2-forward-kinematics]
difficulty: 4
estimated_minutes: 100
tags: [kinematics, manipulator, inverse-kinematics, jacobian]
activities:
  - id: m2-inverse-kinematics-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 35
  - id: m2-inverse-kinematics-quiz
    kind: quiz
    title: 역기구학 해의 개수·특이점 퀴즈
    estimated_minutes: 15
  - id: m2-inverse-kinematics-exercise
    kind: exercise
    title: 해석적 IK 와 수치 IK 구현 후 FK 로 검증
    estimated_minutes: 50
resources:
  - title: "Modern Robotics, 5–6장 Velocity Kinematics / Inverse Kinematics (Lynch & Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: 자코비안(5.1절)과 해석적·수치 IK(6장).
  - title: "Modern Robotics 강의 영상 (5–6장)"
    url: https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos
    kind: video
    note: 자코비안과 역기구학 영상.
  - title: "Introduction to Robotics: Mechanics and Control, 4th ed. (John J. Craig)"
    kind: book
    note: 4장 Inverse Manipulator Kinematics — 해석적 IK 예제.
  - title: "Robotics: Modelling, Planning and Control (Siciliano, Sciavicco, Villani, Oriolo)"
    kind: book
    note: 3장 자코비안, 특이점, 역기구학 알고리즘(심화).
  - title: "ModernRobotics 공식 코드 라이브러리"
    url: https://github.com/NxRLab/ModernRobotics
    kind: other
    note: IKinSpace 로 결과 비교(선택).
---

# 역기구학

역기구학(inverse kinematics, IK)은 "손끝을 저 점에 놓으려면 관절을 얼마나 돌려야 하는가?"
에 답한다. 정기구학 $\mathbf{x} = f(\boldsymbol{\theta})$ 의 역문제 $\boldsymbol{\theta} = f^{-1}(\mathbf{x})$ 이며,
로봇 팔에 목표 자세를 지시하는 거의 모든 작업의 출발점이다. FK 와 달리 해가 **없을 수도,
여러 개일 수도, 무한히 많을 수도** 있다는 점이 핵심이다.

## 개념

### 해의 존재와 개수

- **해가 없음:** 목표가 작업 영역 밖에 있다(2-link 팔이면 $r > L_1 + L_2$ 또는 $r < |L_1 - L_2|$).
- **해가 여러 개:** 2-link 팔은 대부분의 점에 팔꿈치를 위로 굽힌(elbow-up) 해와 아래로
  굽힌(elbow-down) 해 두 개로 도달한다. 6자유도 산업용 팔은 최대 8개(이상)의 해를 가질 수 있다.
- **해가 무한히 많음:** 작업 차원보다 관절이 많은 **여유 자유도(redundant)** 팔.

### 해석적 방법

기하학(삼각형, 코사인 법칙)이나 대수적 조작으로 닫힌 식을 얻는다. 빠르고 모든 해를
한 번에 얻지만, 특정 구조(예: 손목 세 축이 한 점에서 만나는 6축 팔)에서만 가능하다.

### 수치적 방법과 자코비안

자코비안 $J(\boldsymbol{\theta}) = \partial f / \partial \boldsymbol{\theta}$ 는 관절 속도를 말단 속도로 바꾸는
행렬이다. 현재 오차를 자코비안으로 관절 공간에 되돌려 보내는 일을 반복하면(뉴턴–랩슨)
일반적인 팔에도 적용할 수 있다. 다만 **초기값 근처의 해 하나**만 찾고, 수렴이 보장되지 않는다.

### 특이점

$\det J = 0$ 이 되는 자세에서는 어떤 방향으로 말단을 움직일 수 없고, 그 근처에서 IK 가
매우 큰 관절 속도를 요구한다. 2-link 팔은 $\theta_2 = 0$ (완전히 폄) 또는 $\pi$ (완전히 접음)
에서 특이하다. 수치 IK 에서는 감쇠 최소 제곱(damped least squares)으로 이를 완화한다.

## 핵심 수식

2-link 해석적 IK (코사인 법칙):

$$\cos\theta_2 = \frac{x^2 + y^2 - L_1^2 - L_2^2}{2L_1L_2}, \qquad
\theta_2 = \operatorname{atan2}\!\left(\pm\sqrt{1-\cos^2\theta_2},\ \cos\theta_2\right)$$

$$\theta_1 = \operatorname{atan2}(y, x) - \operatorname{atan2}\!\left(L_2\sin\theta_2,\ L_1 + L_2\cos\theta_2\right)$$

$|\cos\theta_2| > 1$ 이면 도달 불가다. 2-link 자코비안과 행렬식:

$$J = \begin{bmatrix} -L_1 s_1 - L_2 s_{12} & -L_2 s_{12} \\ L_1 c_1 + L_2 c_{12} & L_2 c_{12} \end{bmatrix}, \qquad \det J = L_1 L_2 \sin\theta_2$$

뉴턴–랩슨 반복($J^{\dagger}$ 는 의사역행렬):

$$\boldsymbol{\theta}_{k+1} = \boldsymbol{\theta}_k + J^{\dagger}(\boldsymbol{\theta}_k)\,\big(\mathbf{x}_d - f(\boldsymbol{\theta}_k)\big)$$

## 예제

$L_1 = L_2 = 1$, 목표 $(1, 1)$ 을 손으로 풀어 보자.

- $\cos\theta_2 = (1 + 1 - 1 - 1)/2 = 0$ 이므로 $\theta_2 = \pm 90^\circ$.
- $\theta_2 = +90^\circ$: $\theta_1 = 45^\circ - \operatorname{atan2}(1, 1) = 0^\circ$.
  FK 확인: $x = \cos 0 + \cos 90^\circ = 1$, $y = \sin 0 + \sin 90^\circ = 1$.
- $\theta_2 = -90^\circ$: $\theta_1 = 45^\circ - \operatorname{atan2}(-1, 1) = 90^\circ$.
  FK 확인: $x = \cos 90^\circ + \cos 0 = 1$, $y = \sin 90^\circ + \sin 0 = 1$.

```python
import numpy as np

L1, L2 = 1.0, 1.0


def fk(th):
    return np.array(
        [
            L1 * np.cos(th[0]) + L2 * np.cos(th[0] + th[1]),
            L1 * np.sin(th[0]) + L2 * np.sin(th[0] + th[1]),
        ]
    )


def jac(th):
    s1, c1 = np.sin(th[0]), np.cos(th[0])
    s12, c12 = np.sin(th[0] + th[1]), np.cos(th[0] + th[1])
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12], [L1 * c1 + L2 * c12, L2 * c12]])


def ik_analytic(x, y, elbow=+1):
    c2 = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)
    if abs(c2) > 1:
        return None  # 작업 영역 밖
    t2 = np.arctan2(elbow * np.sqrt(1 - c2**2), c2)
    t1 = np.arctan2(y, x) - np.arctan2(L2 * np.sin(t2), L1 + L2 * np.cos(t2))
    return np.array([t1, t2])


def ik_newton(xd, th0, iters=50, tol=1e-9):
    th = np.array(th0, dtype=float)
    for _ in range(iters):
        err = xd - fk(th)
        if np.linalg.norm(err) < tol:
            break
        th += np.linalg.pinv(jac(th)) @ err
    return th


print(np.rad2deg(ik_analytic(1, 1, +1)))  # [ 0. 90.]
print(np.rad2deg(ik_analytic(1, 1, -1)))  # [90. -90.]
th = ik_newton(np.array([1.0, 1.0]), [0.3, 0.5])
print(np.rad2deg(th).round(3), fk(th).round(6))
```

**연습 과제(exercise):** (1) 작업 영역 안의 무작위 목표 200개에 대해 두 해석해를 구하고
FK 로 오차가 $10^{-9}$ 이하인지 검증하라. (2) 수치 IK 의 초기값을 바꾸면 어느 해로
수렴하는지 기록하라. (3) 초기값을 $\theta_2 = 0$ 으로 두면 무슨 일이 생기는지 관찰하고,
`pinv` 대신 감쇠 최소 제곱 $J^T(JJ^T + \lambda^2 I)^{-1}$ 을 써서 비교하라.

## 자가 점검 질문

1. 2-link 팔에서 elbow-up 과 elbow-down 해가 하나로 합쳐지는 목표 위치는 어디인가?
2. $\det J = 0$ 인 자세에서 말단은 어느 방향으로 움직일 수 없는가? 직관적으로 설명하라.
3. 수치 IK 가 해석적 IK 보다 유리한 경우와 불리한 경우를 각각 하나씩 들어라.

## 이 단계 공부법

1. **영상:** Modern Robotics 강의 영상 5장 중 자코비안 소개 부분과 6장 "Inverse Kinematics"
   (해석적 IK, 수치 IK) 를 본다.
2. **교재:** Modern Robotics 6장(6.1 해석적, 6.2 수치적)을 읽는다. 자코비안이 처음이라면
   5.1절만 먼저 읽어도 충분하다. 해석적 IK 예제를 더 보고 싶다면 Craig 4장을 참고한다.
3. **본문 + 예제:** $(1, 1)$ 손계산 → 코드 실행 → FK 로 검증 순서로 진행한다.
4. **문제:** 확인 퀴즈 → 연습 과제 (1)~(3) 순으로 푼다. (3) 은 특이점 직관을 만드는
   핵심 과제이니 건너뛰지 말자.
5. **도구(선택):** `modern_robotics` 패키지의 `IKinSpace` 로 같은 문제를 풀어 결과를 비교한다.

## 참고 자료

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, 5장 "Velocity Kinematics and Statics",
  6장 "Inverse Kinematics" — <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics 강의 영상 목록 — <https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos>
- Modern Robotics 공식 코드 라이브러리 — <https://github.com/NxRLab/ModernRobotics>
- John J. Craig, *Introduction to Robotics: Mechanics and Control*, 4th ed., Pearson —
  4장 "Inverse Manipulator Kinematics".
- Bruno Siciliano, Lorenzo Sciavicco, Luigi Villani, Giuseppe Oriolo, *Robotics: Modelling,
  Planning and Control*, Springer, 2009 — 3장 (자코비안, 특이점, 역기구학 알고리즘).
