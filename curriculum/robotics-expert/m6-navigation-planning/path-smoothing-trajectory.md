---
id: m6-path-smoothing-trajectory
title: "경로 평활화와 궤적 생성"
summary: 격자·샘플링 플래너가 낸 꺾인 경로를 매끄럽게 다듬고(경사 하강 평활화), 곡률과 가속 한계를 지키는 속도 프로파일을 붙여 시간이 있는 궤적으로 바꾼다. 경로(path)와 궤적(trajectory)의 차이, Nav2 스무더 서버의 위치를 함께 본다.
objectives:
  - 경로와 궤적을 구분하고, 플래너 출력에 평활화와 시간 매개화가 필요한 이유를 설명할 수 있다.
  - 데이터 항과 평활 항을 가진 경사 하강 평활화를 구현하고 두 가중치의 역할을 설명할 수 있다.
  - 곡률에 따른 속도 제한과 전·후진 가속 패스로 사다리꼴형 속도 프로파일을 만들 수 있다.
prerequisites: [m6-sampling-based-planning, m6-costmap-global-planning]
difficulty: 3
estimated_minutes: 110
tags: [path-smoothing, trajectory-generation, curvature, velocity-profile, time-parameterization]
activities:
  - id: m6-path-smoothing-trajectory-reading
    kind: reading
    title: 본문과 Modern Robotics Ch. 9 읽기
    estimated_minutes: 40
  - id: m6-path-smoothing-trajectory-quiz
    kind: quiz
    title: 경로·궤적·곡률 퀴즈
    estimated_minutes: 15
  - id: m6-path-smoothing-trajectory-exercise
    kind: exercise
    title: 평활화 가중치와 속도 프로파일 실험
    estimated_minutes: 55
resources:
  - title: "Modern Robotics: Mechanics, Planning, and Control (Lynch, Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: Ch. 9 Trajectory Generation(시간 스케일링·사다리꼴 프로파일), Ch. 10.8 평활화.
  - title: "Modern Robotics Videos"
    url: https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos
    kind: video
    note: Ch. 9 영상.
  - title: "Planning Algorithms (LaValle)"
    url: https://lavalle.pl/planning/
    kind: book
    note: Part IV 미분 제약 하의 계획(선택, 심화).
  - title: "Nav2 Documentation"
    url: https://docs.nav2.org/rolling/index.html
    kind: article
    note: Configuration Guide 의 스무더 서버·Velocity Smoother 항목.
---

# 경로 평활화와 궤적 생성

레슨 1의 A* 는 45° 단위로 꺾이는 계단 경로를, 레슨 2의 RRT 는 지그재그 경로를 냈다. 이런 경로는
꺾이는 점에서 곡률이 무한대에 가까워 로봇이 거의 멈춰서 돌아야 한다. 또 플래너 출력은 **경로(path)**,
즉 시간 정보가 없는 점들의 열일 뿐이다. 로봇이 따라가려면 각 점을 언제, 얼마의 속도로 지날지 정한
**궤적(trajectory)** 이 필요하다.

## 개념

### 평활화

가장 단순한 방법은 **지름길 잇기(shortcutting)** 다. 경로 위 두 점을 골라 그 사이 직선이 충돌하지
않으면 중간 점을 지운다. RRT 경로에 특히 효과적이다.

**경사 하강 평활화**는 각 점 $y_i$ 를 두 힘으로 움직인다. 데이터 항은 원래 점 $x_i$ 로 당겨 경로가
너무 멀리 벗어나지 않게 하고, 평활 항은 이웃의 중점 쪽으로 당겨 꺾임을 편다. 평활 가중치가 클수록
곧아지지만 원 경로(그리고 플래너가 확인한 안전 영역)에서 멀어진다. 그래서 실제 스무더는 비용 지도를
보며 충돌을 다시 검사한다. Nav2 는 플래너와 별도의 **스무더 서버**에 Simple Smoother, Constrained
Smoother 같은 플러그인을 둔다.

### 시간 매개화(속도 프로파일)

경로를 호 길이 $s$ 로 다시 샘플링한 뒤 각 점의 속도 상한을 정한다.

- **최대 속도** $v_{max}$
- **곡률 제한:** 곡률 $\kappa$ 인 곳에서 횡가속도 $v^2\kappa$ 가 한계를 넘지 않게 한다.
- **가속·감속 한계:** 앞에서부터 가속 한계로, 뒤에서부터 감속 한계로 속도를 깎는다(전·후진 패스).

결과는 직선에서는 가속-등속-감속의 사다리꼴, 코너에서는 그 사이가 움푹 파인 모양이다. Modern
Robotics Ch. 9 의 시간 스케일링과 같은 생각이다.

## 핵심 수식

경사 하강 평활화(끝점 고정):

$$y_i \leftarrow y_i + \alpha\,(x_i - y_i) + \beta\,(y_{i-1} + y_{i+1} - 2y_i)$$

평면 곡선의 곡률과 곡률 속도 제한:

$$\kappa = \frac{|x'y'' - y'x''|}{(x'^2 + y'^2)^{3/2}},\qquad v(s) \le \sqrt{a_{lat}/\kappa(s)}$$

가속 한계(전진 패스, 후진 패스는 방향만 반대):

$$v_i^2 \le v_{i-1}^2 + 2\,a_{max}\,\Delta s$$

## 예제

격자 플래너가 낼 법한 계단 경로를 평활화하고, 원 경로와 평활 경로에 같은 속도 프로파일을 붙인다.

```python
import numpy as np

# 격자 A* 가 낼 법한 계단식 경로 (0.5 m 간격, 45° 꺾임)
raw = np.array([[0, 0], [1, 0], [2, 0], [3, 1], [4, 2], [4, 3], [4, 4], [5, 5], [6, 5], [7, 5]])
path = raw * 0.5


def smooth(path, w_data=0.1, w_smooth=0.4, iters=500):
    """원래 점 근처에 머물면서(데이터 항) 이웃의 평균 쪽으로 당긴다(평활 항). 양 끝점 고정."""
    y = path.copy()
    for _ in range(iters):
        y[1:-1] += w_data * (path[1:-1] - y[1:-1]) + w_smooth * (y[:-2] + y[2:] - 2 * y[1:-1])
    return y


def resample(path, ds=0.05):
    seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
    s = np.r_[0, np.cumsum(seg)]
    s_new = np.arange(0, s[-1], ds)
    return np.c_[np.interp(s_new, s, path[:, 0]), np.interp(s_new, s, path[:, 1])], s_new


def curvature(p):
    d1, d2 = np.gradient(p, axis=0), np.gradient(np.gradient(p, axis=0), axis=0)
    return np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / np.linalg.norm(d1, axis=1) ** 3


def velocity_profile(s, kappa, v_max=0.5, a_max=0.3, a_lat=0.2):
    v = np.minimum(v_max, np.sqrt(a_lat / np.maximum(kappa, 1e-6)))  # 곡률 제한 v ≤ √(a_lat/κ)
    v[0] = v[-1] = 0.0  # 출발·정지
    ds = np.diff(s)
    for i in range(1, len(v)):  # 앞으로: 가속 한계 v_i² ≤ v_{i-1}² + 2 a Δs
        v[i] = min(v[i], np.sqrt(v[i - 1] ** 2 + 2 * a_max * ds[i - 1]))
    for i in range(len(v) - 2, -1, -1):  # 뒤로: 감속 한계
        v[i] = min(v[i], np.sqrt(v[i + 1] ** 2 + 2 * a_max * ds[i]))
    t = np.r_[0, np.cumsum(2 * ds / np.maximum(v[1:] + v[:-1], 1e-6))]  # 구간 평균 속도로 시간
    return v, t


for name, p in [("원 경로", path), ("평활화", smooth(path))]:
    dense, s = resample(p)
    kappa = curvature(dense)
    v, t = velocity_profile(s, kappa)
    print(
        f"{name}: 길이 {s[-1]:.2f} m, 최대 곡률 {kappa.max():6.2f} 1/m, "
        f"코너 제한 속도 {min(0.5, np.sqrt(0.2 / kappa.max())):.2f} m/s, 주행 시간 {t[-1]:.1f} s"
    )
```

평활화로 경로가 5.10 m 에서 4.35 m 로 짧아지고, 최대 곡률이 약 9 에서 2.0 1/m 로 줄어 코너 제한
속도가 0.15 에서 0.32 m/s 로 오른다. 주행 시간은 15.3 s 에서 11.0 s 가 된다. 원 경로의 곡률 값은
재샘플 간격에 따라 달라지는 근사라는 점에 주의하라.

**연습 과제(exercise):** (1) `w_smooth` 를 0.1, 0.25, 0.45 로 바꿔 경로가 원래 점에서 얼마나 벗어나는지
최대 편차를 재라. (2) 레슨 3의 비용 지도 위에서 평활 경로의 각 점 비용을 확인하고, 치명 칸에 닿으면
그 점의 평활 갱신을 멈추는 규칙을 넣어라. (3) `velocity_profile` 의 `v` 를 $s$ 에 대해 그려 사다리꼴과
코너의 움푹 파인 곳을 확인하라.

## 자가 점검 질문

1. 경로와 궤적의 차이는 무엇이며, 지역 컨트롤러는 그중 무엇을 입력으로 받는가?
2. 평활 가중치를 크게 할 때 얻는 것과 잃는 것은 각각 무엇인가?
3. 속도 프로파일에서 후진(감속) 패스를 생략하면 어떤 일이 생기는가?

## 이 단계 공부법

1. **교재(먼저):** Modern Robotics Ch. 9 의 시간 스케일링과 사다리꼴 프로파일을 영상과 함께 본다.
2. **본문 + 예제:** 예제를 돌리고 두 경로와 속도 곡선을 그려 연습 과제를 한다.
3. **연결:** 레슨 2의 RRT 경로에 지름길 잇기와 평활화를 차례로 적용해 길이·곡률 변화를 기록한다.
4. **심화(선택):** Nav2 스무더 서버 문서와 LaValle Part IV 로 미분 제약을 직접 다루는 계획을 훑어본다.

## 참고 자료

- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 9–10 — <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics Videos — <https://hades.mech.northwestern.edu/index.php/Modern_Robotics_Videos>
- Steven M. LaValle, *Planning Algorithms*, Cambridge University Press — <https://lavalle.pl/planning/>
- Nav2 Documentation — <https://docs.nav2.org/rolling/index.html>
