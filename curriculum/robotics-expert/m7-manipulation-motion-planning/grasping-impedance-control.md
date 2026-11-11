---
id: m7-grasping-impedance-control
title: "파지·접촉 기초: 그리퍼, 힘 제어와 임피던스"
summary: 그리퍼 종류와 마찰 원뿔·힘 닫힘으로 두 손가락 파지가 성립하는 조건을 판정하고, 위치 제어로는 다루기 어려운 접촉을 힘 제어와 임피던스 제어로 다루는 원리를 1자유도 벽 접촉 시뮬레이션으로 확인한다. 픽앤플레이스 파이프라인의 단계도 정리한다.
objectives:
  - 쿨롱 마찰 원뿔과 힘 닫힘 개념으로 두 손가락(antipodal) 파지의 성립 여부를 판정하고 필요한 파지력을 계산할 수 있다.
  - 위치 제어·힘 제어·임피던스 제어의 차이를 설명하고, 임피던스 강성이 접촉력과 충격에 주는 영향을 시뮬레이션으로 보일 수 있다.
  - 인식 → 파지 자세 선택 → 접근 → 파지 → 이송 → 놓기로 이어지는 픽앤플레이스 파이프라인의 각 단계와 실패 지점을 설명할 수 있다.
prerequisites: [m7-manipulator-dynamics-torque-control, m4-point-clouds-icp-ransac]
difficulty: 3
estimated_minutes: 120
tags: [manipulation, grasping, friction-cone, force-control, impedance-control, pick-and-place]
activities:
  - id: m7-grasping-impedance-control-reading
    kind: reading
    title: 본문과 Robotic Manipulation Ch. 3 읽기
    estimated_minutes: 45
  - id: m7-grasping-impedance-control-quiz
    kind: quiz
    title: 마찰 원뿔·힘 닫힘·임피던스 퀴즈
    estimated_minutes: 15
  - id: m7-grasping-impedance-control-exercise
    kind: exercise
    title: 파지 판정과 1자유도 임피던스 제어 실험
    estimated_minutes: 60
resources:
  - title: "Robotic Manipulation (Tedrake)"
    url: https://manipulation.mit.edu/
    kind: book
    note: Ch. 3 Basic Pick and Place, Ch. 5 Bin Picking(파지 후보 선택), Ch. 8 Manipulator Control(힘·임피던스).
  - title: "Modern Robotics: Mechanics, Planning, and Control (Lynch, Park)"
    url: http://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: Ch. 11.5–11.6 힘 제어·임피던스 제어, Ch. 12 Grasping and Manipulation(마찰 원뿔·힘 닫힘).
  - title: "Modern Robotics Ch. 11 Robot Control 영상"
    url: https://www.youtube.com/playlist?list=PLggLP4f-rq02N54sD6xwdDWlDScvb32Pp
    kind: video
    note: 힘 제어·하이브리드 제어·임피던스 제어 편.
  - title: "MIT OCW 6.4210 Robotic Manipulation"
    url: https://ocw.mit.edu/courses/6-4210-robotic-manipulation-fall-2022/
    kind: course
    note: Fall 2022 강의 영상 + 과제(픽앤플레이스·파지).
---

# 파지·접촉 기초: 그리퍼, 힘 제어와 임피던스

이동 로봇의 목표는 "부딪히지 않기"였지만, 매니퓰레이터는 "제대로 부딪히기", 즉 잡고 밀고 끼워 넣어야
한다. 접촉 중에는 1 mm 의 위치 오차가 수십 N 의 힘이 된다. 이 레슨은 "언제 잡혔는가"(파지)와 "접촉
중 힘을 어떻게 다루는가"(힘·임피던스 제어)를 다룬다.

## 개념

### 그리퍼와 파지 모델

그리퍼는 **평행 두 손가락**(SO-101 같은 저가 팔 포함), 평평한 면에 강한 **흡착**(물류 bin picking),
손 안 조작이 가능하지만 제어가 어려운 **다지 손**으로 나뉜다.

접점에서 손가락이 낼 수 있는 힘은 쿨롱 마찰 때문에 **마찰 원뿔** 안에 있어야 한다. 법선 성분이
$f_n$ 이면 접선 성분은 $|f_t| \le \mu f_n$ 이고, 원뿔 반각은 $\arctan\mu$ 다. 외력과 상관없이 접촉력만으로
물체를 붙잡을 수 있는 상태를 **힘 닫힘(force closure)** 이라 한다. 평면 두 손가락 파지에서는
"두 접점을 잇는 선이 양쪽 마찰 원뿔 안에 있을 것"과 같다(antipodal 조건).

### 위치·힘·임피던스 제어

- **위치 제어:** 접촉 시 힘이 환경 강성에 따라 폭주한다.
- **힘 제어:** $F_d$ 를 직접 낸다($\tau = J^\top F_d + g$). 접촉이 없으면 가속해 날아간다.
- **하이브리드 위치/힘 제어:** 방향별로 나눈다(예: 표면 법선은 힘, 접선은 위치).
- **임피던스 제어:** 말단을 가상의 스프링·댐퍼로 만든다. 자유 공간에서는 위치 제어처럼, 접촉 중에는
  $K \cdot$(침투량) 정도의 힘만 낸다. 레슨 1의 $\tau = J^\top F$ 로 관절 토크가 된다.

### 픽앤플레이스 파이프라인

인식(M4 의 점군·RANSAC 으로 물체 자세 추정) → 파지 후보 생성·선택(antipodal 판정, 충돌 검사) →
접근 자세(pre-grasp)까지 이동 → 작업 공간 직선 접근 → 그리퍼 닫기와 파지 확인(손가락 폭·전류) →
이송 → 놓기. 실패는 대부분 인식 오차와 미끄러짐에서 생기며, 낮은 임피던스가 인식 오차를 흡수한다.

## 핵심 수식

마찰 원뿔과 두 손가락 수평 파지의 최소 파지력:

$$|f_t| \le \mu f_n,\qquad 2\mu N \ge mg \;\Rightarrow\; N \ge \frac{mg}{2\mu}$$

임피던스 법칙과 강성 $k_e$ 인 벽에 대한 정상 접촉력:

$$F = K(x_d - x) - D\dot{x},\qquad F_{ss} = \frac{K k_e}{K + k_e}(x_d - x_w)$$

## 예제

```python
import numpy as np

# 1) 두 손가락 평면 파지: 힘 닫힘(force closure) 판정
MU = 0.5


def antipodal_ok(p1, n1, p2, n2, mu=MU):
    """두 접점을 잇는 선이 양쪽 마찰 원뿔(안쪽 법선 기준) 안에 있으면 힘 닫힘."""
    d = (p2 - p1) / np.linalg.norm(p2 - p1)
    a1 = np.arccos(np.clip(d @ n1, -1, 1))  # 접점1 안쪽 법선과 연결선 사이 각
    a2 = np.arccos(np.clip(-d @ n2, -1, 1))
    return a1 <= np.arctan(mu) and a2 <= np.arctan(mu), np.degrees([a1, a2])


def unit(deg):
    return np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg))])


print(f"마찰 계수 {MU} → 원뿔 반각 {np.degrees(np.arctan(MU)):.1f}°")
cases = {
    "정면": (np.array([-0.05, 0]), unit(0), np.array([0.05, 0]), unit(180)),
    "약간 어긋남": (np.array([-0.05, -0.01]), unit(0), np.array([0.05, 0.02]), unit(180)),
    "크게 어긋남": (np.array([-0.05, -0.03]), unit(0), np.array([0.05, 0.04]), unit(180)),
    "쐐기 면(법선 40°)": (np.array([-0.05, 0]), unit(40), np.array([0.05, 0]), unit(140)),
}
for name, (p1, n1, p2, n2) in cases.items():
    ok, ang = antipodal_ok(p1, n1, p2, n2)
    print(f"{name:12s} 각도 {ang.round(1)} → {'힘 닫힘' if ok else '미끄러짐'}")

m, g = 0.4, 9.81  # 0.4 kg 물체를 두 손가락으로 옆에서 집어 든다
print(f"최소 파지력 N ≥ mg/(2μ) = {m * g / (2 * MU):.2f} N (안전율 2 → {m * g / MU:.2f} N)")

# 2) 1자유도 임피던스 제어: 벽(x=0.10 m, 강성 k_e) 너머 x_d=0.12 m 를 명령
M_EE, K_ENV, X_WALL, X_D = 1.0, 2.0e4, 0.10, 0.12
dt, steps = 1e-5, 100_000  # 1 s


def simulate(K, zeta=1.0):
    D = 2 * zeta * np.sqrt(K * M_EE)
    x, v, forces = 0.0, 0.0, []
    for _ in range(steps):
        f_env = -K_ENV * (x - X_WALL) if x > X_WALL else 0.0
        f_ctrl = K * (X_D - x) - D * v  # 임피던스 법칙(중력은 보상되었다고 가정)
        v += dt * (f_ctrl + f_env) / M_EE
        x += dt * v
        forces.append(-f_env)
    return max(forces), forces[-1], x


print("임피던스 K[N/m]  최대 접촉력[N]  정상 접촉력[N]  침투[mm]")
for K in [300.0, 3000.0, 30000.0]:
    fmax, fss, x = simulate(K)
    theory = K * K_ENV / (K + K_ENV) * (X_D - X_WALL)
    print(f"{K:14.0f}  {fmax:13.1f}  {fss:8.2f}({theory:.2f})  {(x - X_WALL) * 1e3:8.3f}")
```

원뿔 반각 26.6° 안인 16.7° 어긋남은 버티지만 35° 어긋남과 40° 쐐기 면은 미끄러진다. 정상 접촉력은
이론값과 일치하며 $K$ 와 함께 약 6 N → 240 N 으로 커진다. 눈여겨볼 것은 **최대** 접촉력이다. 낮은
강성에서도 달려와 부딪히는 순간 정상값의 6배(약 36 N)가 생기므로, 실제 파지는 접촉 직전에 감속한다.

**연습 과제(exercise):** (1) 마찰 계수 0.3, 0.8 에서 판정을 다시 하라. (2) 벽 0.5 cm 앞까지 천천히 접근한
뒤 임피던스로 바꿔 최대 접촉력을 재라. (3) 순수 힘 제어($F = F_d$)로 바꾸고 벽이 없을 때를 설명하라.

## 자가 점검 질문

1. 마찰 계수가 작아지면 antipodal 파지가 성립하는 접점 배치가 어떻게 바뀌는가?
2. 임피던스 제어가 위치 제어와 힘 제어의 "중간"이라고 하는 이유를 자유 공간과 접촉 상황으로 나눠 설명하라.
3. 픽앤플레이스에서 인식 오차가 2 cm 일 때 실패를 줄이기 위해 접근 단계에서 할 수 있는 일 두 가지를 써라.

## 이 단계 공부법

1. **교재(먼저):** Tedrake *Robotic Manipulation* Ch. 3 에서 픽앤플레이스 전체 흐름을 읽어 큰 그림을 잡는다.
2. **본문 + 예제:** 파지 판정과 임피던스 실험을 돌리고, 연습 (2) 로 "접근 속도"가 핵심임을 확인한다.
3. **이론:** Modern Robotics Ch. 12(마찰 원뿔·힘 닫힘)와 Ch. 11 의 힘·임피던스 제어 절과 영상을 본다.
4. **심화(선택):** MIT OCW 6.4210 의 픽앤플레이스·파지 과제를 따라 Ch. 5 의 파지 후보 선택까지 넓힌다.

## 참고 자료

- Russ Tedrake, *Robotic Manipulation: Perception, Planning, and Control*, Ch. 3, 5, 8 — <https://manipulation.mit.edu/>
- Kevin M. Lynch, Frank C. Park, *Modern Robotics*, Ch. 11–12 — <http://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Modern Robotics Ch. 11 Robot Control 영상 — <https://www.youtube.com/playlist?list=PLggLP4f-rq02N54sD6xwdDWlDScvb32Pp>
- MIT OCW 6.4210 Robotic Manipulation (Fall 2022) — <https://ocw.mit.edu/courses/6-4210-robotic-manipulation-fall-2022/>
- Neville Hogan, "Impedance Control: An Approach to Manipulation", ASME J. Dyn. Sys. Meas. Control 1985 (임피던스 제어 원논문, 링크 없음)
