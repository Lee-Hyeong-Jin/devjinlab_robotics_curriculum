---
id: m4-camera-model-features
title: 카메라 모델·캘리브레이션과 이미지 특징
summary: 핀홀 카메라 모델로 3D 점을 픽셀에 투영하고, 내부 파라미터를 최소제곱으로 추정하는 캘리브레이션의 원리와 코너(Harris) 같은 이미지 특징을 익힌다.
objectives:
  - 내부 파라미터 행렬 K 와 외부 파라미터 [R|t] 로 3D 점을 픽셀 좌표로 투영할 수 있다.
  - 캘리브레이션이 추정하는 값(초점 거리, 주점, 왜곡 계수)과 그 방법을 설명할 수 있다.
  - 이미지 그래디언트로 Harris 코너 응답을 계산하고 코너·모서리·평탄 영역을 구분할 수 있다.
prerequisites: [m1-coordinate-transforms, m4-sensor-models]
difficulty: 3
estimated_minutes: 100
tags: [camera, pinhole, calibration, features, harris, computer-vision]
activities:
  - id: m4-camera-model-features-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 35
  - id: m4-camera-model-features-quiz
    kind: quiz
    title: 투영 계산 퀴즈
    estimated_minutes: 15
  - id: m4-camera-model-features-exercise
    kind: exercise
    title: 투영·미니 캘리브레이션·Harris 코너 구현
    estimated_minutes: 50
resources:
  - title: "First Principles of Computer Vision (Shree Nayar)"
    url: https://fpcv.cs.columbia.edu/
    kind: video
    note: Camera & Imaging, Features & Boundaries 시리즈. 먼저 본다.
  - title: "Cyrill Stachniss, Homogeneous Coordinates"
    url: https://www.youtube.com/watch?v=MQdm0Z_gNcw
    kind: video
    note: 투영을 행렬 곱 하나로 쓰는 동차 좌표 복습.
  - title: QUT Robot Academy (Peter Corke)
    url: https://robotacademy.net.au/
    kind: video
    note: 3D Vision·Visual Servoing 주제 레슨(선택).
  - title: "Computer Vision: Algorithms and Applications (Richard Szeliski)"
    kind: book
    note: 카메라 캘리브레이션과 특징 검출 장(심화 참고).
---

# 카메라 모델·캘리브레이션과 이미지 특징

카메라는 싸고 정보가 많은 센서지만 3D 세계를 2D 이미지로 납작하게 만든다. 이 레슨은 그 규칙
(핀홀 모델)을 행렬로 적고, 그 행렬을 재는 법(캘리브레이션)과 다시 찾기 쉬운 점(특징점)을 고르는
법을 다룬다. 다음 레슨의 점군과 마지막 레슨의 3D 위치 추정이 이 모델 위에서 동작한다.

## 개념

### 핀홀 모델

카메라 좌표계(광축이 $z$)의 점 $(X, Y, Z)$ 는 원점을 지나는 직선을 따라 이미지 평면에 맺힌다.
먼저 $Z$ 로 나눈 **정규 이미지 좌표** $(x, y) = (X/Z, Y/Z)$ 를 만들고, 초점 거리(픽셀 단위)
$f_x, f_y$ 와 주점 $(c_x, c_y)$ 로 픽셀 $(u, v)$ 를 얻는다. 월드 좌표의 점은 먼저 외부 파라미터
$[R \mid t]$ 로 카메라 좌표로 옮긴다. $Z$ 로 나누는 순간 깊이가 사라지므로, 카메라 한 대로는 점이 놓인
**광선**까지만 알 수 있다. 실제 렌즈는 직선을 휘게 하는데, 가장 큰 성분은 중심에서 멀수록
커지는 **방사 왜곡**(계수 $k_1, k_2, \dots$)이다.

### 캘리브레이션

$K$ 와 왜곡 계수를 측정하는 과정이다. 크기를 아는 체커보드를 여러 각도에서 찍고, 코너의 3D
좌표와 검출된 픽셀 좌표의 대응으로 **재투영 오차**를 최소화한다(Zhang 방법, OpenCV
`calibrateCamera`). 예제는 3D 점을 안다고 가정하고 $f_x, c_x$ 를 선형 최소제곱으로 푸는 축소판이다.

### 이미지 특징

같은 장면을 다른 위치에서 찍었을 때 다시 찾을 수 있는 점이 **특징점**이다. 평탄한 영역은 어디로
옮겨도 똑같고, 모서리는 한 방향으로만 구분된다. **코너**는 모든 방향으로 밝기가 변하므로 위치가
확정된다. Harris 검출기는 작은 창 안의 그래디언트 공분산 $M$ 의 두 고윳값이 모두 클 때 코너로
판정한다. 직선(차선, 벽 모서리)은 Hough 변환으로 찾고, SIFT·ORB 같은 기술자가 특징점을
이미지 간에 매칭한다.

## 핵심 수식

$$\begin{bmatrix} u \\ v \\ 1 \end{bmatrix} \sim
K\,[R \mid t]\begin{bmatrix} X_w \\ 1 \end{bmatrix},\qquad
K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$

방사 왜곡: $x_d = x\,(1 + k_1 r^2 + k_2 r^4)$, $r^2 = x^2 + y^2$ ($y$ 도 같음).

Harris 응답(창 $W$ 안의 합, $k \approx 0.04$–$0.06$):

$$M = \sum_W \begin{bmatrix} I_x^2 & I_x I_y \\ I_x I_y & I_y^2 \end{bmatrix},\qquad
R = \det M - k\,(\operatorname{tr} M)^2$$

$R > 0$ 이고 크면 코너, $R < 0$ 이면 모서리, $|R| \approx 0$ 이면 평탄.

## 예제

```python
import numpy as np

rng = np.random.default_rng(2)
K = np.array([[600.0, 0, 320], [0, 600.0, 240], [0, 0, 1]])


def project(K, R, t, P_w, k1=0.0):
    P_c = P_w @ R.T + t  # 월드 → 카메라 좌표
    x, y = P_c[:, 0] / P_c[:, 2], P_c[:, 1] / P_c[:, 2]  # 정규 이미지 좌표
    s = 1 + k1 * (x**2 + y**2)  # 방사 왜곡 (1차 항만)
    return np.c_[K[0, 0] * s * x + K[0, 2], K[1, 1] * s * y + K[1, 2]]


# 1) 투영: 카메라 앞 2 m 에 놓인 0.5 m 정사각형의 네 꼭짓점
R, t = np.eye(3), np.array([0.0, 0.0, 2.0])
square = np.array([[-0.25, -0.25, 0], [0.25, -0.25, 0], [0.25, 0.25, 0], [-0.25, 0.25, 0]])
print("픽셀 좌표:\n", project(K, R, t, square).round(1))

# 2) 미니 캘리브레이션: 카메라 좌표의 3D 점과 관측 픽셀로 fx, fy, cx, cy 추정
P_c = rng.uniform([-1, -1, 2], [1, 1, 5], (50, 3))
uv = project(K, np.eye(3), np.zeros(3), P_c) + rng.normal(0, 0.5, (50, 2))
x, y = P_c[:, 0] / P_c[:, 2], P_c[:, 1] / P_c[:, 2]
ones = np.ones_like(x)
fx, cx = np.linalg.lstsq(np.c_[x, ones], uv[:, 0], rcond=None)[0]
fy, cy = np.linalg.lstsq(np.c_[y, ones], uv[:, 1], rcond=None)[0]
print(f"추정 fx={fx:.1f}, fy={fy:.1f}, cx={cx:.1f}, cy={cy:.1f}")


# 3) Harris 코너: 밝은 사각형이 있는 합성 이미지
img = np.zeros((40, 40))
img[10:30, 12:28] = 1.0


def filter2(a, k):  # 2D 상관(correlation), 가장자리는 복제 패딩
    p = np.pad(a, k.shape[0] // 2, mode="edge")
    win = np.lib.stride_tricks.sliding_window_view(p, k.shape)
    return np.einsum("ijkl,kl->ij", win, k)


Ix = filter2(img, np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]) / 8)
Iy = filter2(img, np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]) / 8)
box = np.ones((5, 5))
Sxx, Syy, Sxy = filter2(Ix * Ix, box), filter2(Iy * Iy, box), filter2(Ix * Iy, box)
Rh = (Sxx * Syy - Sxy**2) - 0.05 * (Sxx + Syy) ** 2
for name, (r, c) in {"코너": (10, 12), "모서리": (20, 12), "평탄": (20, 20)}.items():
    print(f"{name:3s} ({r:2d},{c:2d}) R = {Rh[r, c]:+.4f}")
```

정사각형은 (245, 165)–(395, 315) 픽셀에 맺힌다($600 \times 0.25 / 2 = 75$). 내부 파라미터는
1 픽셀 안으로 복원되고, Harris 응답은 코너에서 양수, 모서리에서 음수, 평탄 영역에서 0 이다.

**연습 과제(exercise):** (1) 정사각형을 카메라에서 4 m 로 옮기면 픽셀 크기가 어떻게 되는지 예측한 뒤
확인하라. (2) `k1=-0.2` 로 격자 점을 투영해 그려 술통형 왜곡을 관찰하라. (3) Harris 응답 맵 전체를
이미지로 그리고, 임계값과 3×3 국소 최대값으로 코너 네 개만 남겨라.

## 자가 점검 질문

1. 카메라 한 대의 픽셀 하나로 3D 점의 위치를 정할 수 없는 이유를 투영 식으로 설명하라.
2. 캘리브레이션에서 체커보드를 여러 각도로 찍어야 하는 이유는 무엇인가?
3. Harris 행렬 $M$ 의 두 고윳값이 (큼, 큼), (큼, 작음), (작음, 작음)일 때 각각 어떤 영역인가?

## 확인 퀴즈

`rc quiz m4-camera-model-features` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m4-camera-model-features-quiz
questions:
  - id: q1
    type: single
    prompt: '카메라 한 대의 픽셀 하나만으로 3D 점의 위치를 정할 수 없는 이유는?'
    choices:
      - '렌즈 왜곡 때문에 픽셀 좌표가 부정확하기 때문'
      - '$Z$ 로 나누는 투영에서 깊이가 사라져 같은 광선 위 점들이 모두 같은 픽셀에 맺히기 때문'
      - '주점 $(c_x, c_y)$ 를 모르기 때문'
      - '이미지 센서의 해상도가 유한하기 때문'
    answer: 1
    explanation: '$(x, y) = (X/Z, Y/Z)$ 로 나누는 순간 깊이 정보가 사라진다. 한 픽셀은 카메라 원점에서 뻗는 **광선** 하나에 대응하므로, 깊이를 얻으려면 스테레오, 운동, 깊이 센서 같은 추가 정보가 필요하다.'
    concept: { front: '단일 카메라의 한계', back: '$Z$ 로 나누며 깊이가 소실 — 픽셀 하나는 광선 하나까지만 알려 준다' }
  - id: q2
    type: single
    prompt: 'Harris 검출기에서 그래디언트 공분산 행렬 $M$ 의 두 고윳값이 (큼, 작음)이면 그 영역은?'
    choices:
      - '평탄한 영역'
      - '모서리(edge)'
      - '코너'
      - '잡음'
    answer: 1
    explanation: '한 방향으로만 밝기가 크게 변하면 고윳값 하나만 크다 — 모서리다. 둘 다 크면 코너(위치가 확정됨), 둘 다 작으면 평탄한 영역이다. Harris 응답 $R = \det M - k(\operatorname{tr}M)^2$ 가 이 판정을 한 수로 요약한다.'
    concept: { front: 'Harris 행렬 고윳값과 영역', back: '(큼, 큼) = 코너, (큼, 작음) = 모서리, (작음, 작음) = 평탄' }
  - id: q3
    type: truefalse
    prompt: '캘리브레이션에서 체커보드를 한 각도에서 여러 장 찍는 것만으로도 $K$ 와 왜곡 계수를 신뢰성 있게 구할 수 있다.'
    answer: false
    explanation: '한 자세만 쓰면 초점 거리와 거리(스케일)처럼 서로 맞바꿀 수 있는 파라미터가 분리되지 않고, 왜곡 계수를 결정할 만큼 이미지 주변부가 다양하게 채워지지도 않는다. 여러 각도·거리에서 찍어 제약을 늘려야 재투영 오차 최소화가 유일한 해로 수렴한다.'
```

## 이 단계 공부법

1. **영상(먼저):** Nayar *First Principles of Computer Vision* 의 Camera & Imaging 시리즈로
   투영·렌즈를 보고, Features & Boundaries 시리즈에서 코너·에지 검출을 본다.
2. **복습:** 동차 좌표가 흐릿하면 Stachniss *Homogeneous Coordinates* 를 다시 본다.
3. **본문 + 예제:** 투영 결과를 손으로 한 점 계산해 코드와 맞춰 본다.
4. **문제:** 퀴즈 → 연습 과제 (1)~(3). (3)은 다음 레슨의 이웃 탐색과도 연결된다.
5. **보강(선택):** QUT Robot Academy 3D Vision 레슨, Szeliski 교재의 캘리브레이션 장.

## 참고 자료

- Shree Nayar, *First Principles of Computer Vision* — <https://fpcv.cs.columbia.edu/>
- Cyrill Stachniss, "Homogeneous Coordinates" — <https://www.youtube.com/watch?v=MQdm0Z_gNcw>
- QUT Robot Academy (Peter Corke) — <https://robotacademy.net.au/>
- Richard Szeliski, *Computer Vision: Algorithms and Applications* — 캘리브레이션·특징 검출 장.
