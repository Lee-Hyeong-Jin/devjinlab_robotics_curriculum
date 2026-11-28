---
id: m11-encoders-speed-loop
title: 엔코더와 모터 속도 루프
summary: 쿼드러처 엔코더로 바퀴의 각도와 속도를 재는 법, 카운트법의 속도 분해능과 지연의 절충을 다루고, M3 의 방향 제어 루프 아래에 놓이는 모터 속도 루프(캐스케이드)를 포화·양자화·전압 강하가 있는 모터 시뮬레이션으로 닫아 본다.
objectives:
  - 엔코더의 PPR·4체배·기어비에서 바퀴 한 바퀴당 카운트 수와 각도·속도 분해능을 계산할 수 있다.
  - 카운트법으로 잰 속도의 분해능과 측정 창 길이의 관계를 설명하고, 저속에서 생기는 문제와 대책을 말할 수 있다.
  - 바깥 루프(위치·방향)와 안쪽 루프(모터 속도)로 이루어진 캐스케이드 제어의 구조와 각 루프의 주기를 정하는 기준을 설명할 수 있다.
prerequisites: [m11-drivers-pwm, m3-pid-control]
difficulty: 3
estimated_minutes: 100
tags: [actuators, encoder, velocity-estimation, cascade-control, pid, saturation]
activities:
  - id: m11-encoders-speed-loop-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 35
  - id: m11-encoders-speed-loop-quiz
    kind: quiz
    title: 엔코더 분해능·캐스케이드 퀴즈
    estimated_minutes: 15
  - id: m11-encoders-speed-loop-exercise
    kind: exercise
    title: 양자화·포화·전압 강하가 있는 속도 루프 실험
    estimated_minutes: 50
resources:
  - title: "Feedback Systems: An Introduction for Scientists and Engineers, 2nd ed. (Åström & Murray)"
    url: https://fbswiki.org/wiki/index.php/Main_Page
    kind: book
    note: 무료 PDF. 11장 PID 제어(적분 와인드업, 캐스케이드)와 1장의 피드백 개념.
  - title: "DC Motor Speed: PID Controller Design (Control Tutorials for MATLAB and Simulink)"
    url: https://ctms.engin.umich.edu/CTMS/index.php?example=MotorSpeed&section=ControlPID
    kind: article
    note: DC 모터 속도 루프의 P, PI, PID 응답을 단계별로 비교한다.
  - title: "Elements of Robotics (Ben-Ari & Mondada)"
    url: https://link.springer.com/book/10.1007/978-3-319-62533-1
    kind: book
    note: 오픈 액세스. 5장 로봇의 움직임과 오도메트리(바퀴 엔코더).
---

# 엔코더와 모터 속도 루프

M3 의 PID 예제에서 제어기가 낸 각속도 명령은 그대로 로봇의 각속도가 됐다. 실제 모터는 같은 듀티를
줘도 배터리 전압, 바닥 마찰, 경사에 따라 다른 속도로 돈다. 그래서 실제 로봇은 **모터마다 속도를 재서
명령 속도에 맞추는 작은 제어 루프**를 하나 더 둔다. 커뮤니티에서 "가장 많이 배우는 단계"로 꼽는 것이
이것, 엔코더를 단 DC 모터에 PID 속도 루프를 닫는 일이다. 이 레슨은 그 루프를 하드웨어 없이, 실제
모터에서 생기는 세 가지 문제(엔코더 양자화, 출력 포화, 전압 강하)를 넣은 시뮬레이션으로 해 본다.

## 어디에 쓰는가

Nav2 가 내는 `cmd_vel` 은 "선속도 0.3 m/s, 각속도 0.5 rad/s" 다. 이것을 좌우 바퀴 속도로 나눈 뒤
(M3) 실제로 그 속도가 나오게 하는 것이 모터 속도 루프이고, ROS 2 에서는 `ros2_control` 의
`diff_drive_controller` 아래, 마이크로컨트롤러 펌웨어 안에서 돈다. 엔코더 카운트는 동시에 오도메트리
(M3, M5)의 원재료다. 로봇이 직진 명령에 한쪽으로 휘거나, 저속에서 덜덜 떨거나, 언덕에서 느려지는
문제는 대부분 이 루프에서 고친다.

## 개념

### 쿼드러처 엔코더

증분형(incremental) 엔코더는 축이 돌 때 펄스를 낸다. 90° 어긋난 두 채널(A, B)을 써서 어느 채널이
먼저 바뀌는지로 회전 방향을 알고, 두 채널의 오르내림을 모두 세면 한 주기에 네 번 셀 수 있다(4체배).

$$\text{바퀴 한 바퀴당 카운트} = 4 \times \text{PPR} \times N_{gear}$$

엔코더가 모터 축에 달려 있으면 기어비만큼 분해능이 좋아진다. PPR 12 인 자석식 엔코더와 기어비 30 이면
$4 \times 12 \times 30 = 1440$ 카운트, 각도 분해능은 $360^\circ/1440 = 0.25^\circ$ 다.

엔코더는 **상대** 각도만 안다. 전원을 켠 순간이 0 이고, 카운트를 놓치면(인터럽트가 늦거나 잡음이
끼면) 그만큼 영원히 틀린다. 마이크로컨트롤러의 하드웨어 카운터(타이머의 엔코더 모드)를 쓰는 이유다.

### 속도 추정

속도는 직접 재지 못하고 카운트에서 계산한다. 가장 단순한 **카운트법**은 일정 시간 $T_w$ 동안의 카운트
변화를 센다.

$$\hat\omega = \frac{2\pi}{\text{CPR}} \cdot \frac{\Delta \text{count}}{T_w}, \qquad
\text{분해능} = \frac{2\pi}{\text{CPR} \cdot T_w}$$

카운트는 정수라 속도도 이 분해능의 배수로만 나온다. 1440 CPR 을 1 ms 마다 재면 분해능이 4.36 rad/s 다.
목표가 10 rad/s 면 측정값은 8.7 과 13.1 사이를 오간다. 창을 10 ms 로 늘리면 분해능은 0.44 rad/s 로
좋아지지만 측정이 평균 5 ms 늦어진다. M4 의 필터 레슨에서 본 "노이즈 대 지연" 절충과 같다.

저속에서는 창 안에 카운트가 0개 아니면 1개라 카운트법이 쓸모없어진다. 그때는 **주기법**(한 카운트에서
다음 카운트까지의 시간을 잰다)을 쓰거나 둘을 섞는다. 더 높은 분해능의 엔코더를 쓰는 것이 가장 쉽다.

### 속도 루프

모터 속도 루프는 보통 PI 다. P 만으로는 역기전력과 마찰을 이기는 데 필요한 전압을 내려면 오차가
남아야 하므로 정상 상태 오차가 생기고, 부하가 걸리면 더 커진다(M3 에서 본 그대로다). I 항이 그 전압을
채운다. D 항은 양자화된 속도 측정의 계단을 증폭하므로 속도 루프에서는 잘 쓰지 않는다.

출력은 PWM 듀티라 $[-1, 1]$ 을 넘지 못한다. 포화 중에 적분이 쌓이지 않게 하는 anti-windup 이 필수다.
그리고 듀티 1 에서 낼 수 있는 속도는 배터리 전압이 정한다. 전류가 클수록 배터리 내부 저항 때문에
단자 전압이 내려가므로(전압 강하), 부하가 걸렸을 때 낼 수 있는 최고 속도는 무부하 때보다 낮다.

### 캐스케이드 제어

M3 의 방향 루프와 이 속도 루프를 겹치면 **캐스케이드**(다단) 제어가 된다.

| 루프 | 측정 | 출력 | 주기(예) |
|---|---|---|---|
| 바깥: 위치·방향(M3 경로 추종) | 오도메트리, IMU | 바퀴 속도 명령 $\omega_R^*$, $\omega_L^*$ | 20–50 Hz |
| 안쪽: 모터 속도(이 레슨) | 엔코더 | PWM 듀티 | 500–1000 Hz |
| (가장 안쪽: 전류·토크, FOC 드라이버) | 전류 센서 | 스위치 | 10–20 kHz |

규칙은 **안쪽 루프가 바깥 루프보다 5–10배 빨라야 한다**는 것이다. 그러면 바깥 루프는 안쪽 루프를
"명령하면 바로 따라오는 것"으로 볼 수 있다. M3 의 가정이 성립하는 조건이 이것이다. 튜닝도 안쪽부터 한다.

## 핵심 수식

- 카운트: $\text{CPR} = 4 \times \text{PPR} \times N_{gear}$, 각도 분해능 $2\pi/\text{CPR}$
- 카운트법: $\hat\omega = 2\pi\,\Delta\text{count}/(\text{CPR}\,T_w)$, 분해능 $2\pi/(\text{CPR}\,T_w)$, 평균 지연 $T_w/2$
- 모터: $J\dot\omega = k i - b\omega - \tau_{load}$, $i = (D\,V_{supply} - k\omega)/R$
- 전압 강하: $V_{supply} = V_{batt} - R_{int}\, i_{batt}$

## 예제

```python
import numpy as np

# 모터 + 기어 + 바퀴 (바퀴 축 기준): J dw/dt = k i - b w - tau_load,  i = (v - k w) / R
k, R, J, b = 0.05, 2.0, 2e-4, 1e-4
V_BATT, R_INT = 7.4, 0.25  # 배터리 개방 전압과 내부 저항
COUNTS = 4 * 12 * 30  # 4체배 x 12 PPR x 기어비 30 = 바퀴 한 바퀴당 1440 카운트


def run(kp, ki, w_ref=10.0, dt=0.001, T=2.0, tau_load=0.0, sag=False, window=1):
    """PI 속도 루프. 속도는 최근 window 주기 동안의 카운트 차이로 잰다. 1초에 부하가 걸린다."""
    w = theta = integ = 0.0
    counts, log = [0] * (window + 1), []
    for n in range(int(T / dt)):
        counts = counts[1:] + [int(np.floor(theta / (2 * np.pi) * COUNTS))]  # 엔코더는 정수만 센다
        w_meas = (counts[-1] - counts[0]) * 2 * np.pi / COUNTS / (dt * window)
        err = w_ref - w_meas
        u = kp * err + ki * integ
        duty = float(np.clip(u, -1.0, 1.0))  # PWM 듀티는 -1..1 을 넘을 수 없다
        if u == duty:  # anti-windup: 포화 중에는 적분 중지
            integ += err * dt
        v_supply = V_BATT
        if sag:  # 전류가 흐르면 배터리 단자 전압이 내려간다
            i_est = (duty * V_BATT - k * w) / (R + R_INT * abs(duty))
            v_supply = V_BATT - R_INT * abs(duty) * i_est
        i = (duty * v_supply - k * w) / R
        load = tau_load if n * dt >= 1.0 else 0.0
        w += (k * i - b * w - load) / J * dt
        theta += w * dt
        log.append((w, w_meas, duty))
    return np.array(log)


print(f"속도 분해능(1 ms 카운트법): {2 * np.pi / COUNTS / 0.001:.2f} rad/s")  # 4.36
for name, (kp, ki) in {"P ": (0.05, 0.0), "PI": (0.05, 1.0)}.items():
    log = run(kp, ki, tau_load=0.02)
    before, after = log[900:1000, 0].mean(), log[1900:, 0].mean()
    print(f"{name}: 부하 전 {before:5.2f}, 부하 후 {after:5.2f} rad/s (목표 10)")
# P : 부하 전  8.72, 부하 후  6.84 rad/s    PI: 부하 전 10.00, 부하 후 10.00 rad/s
log = run(0.05, 1.0)
print(
    f"측정 속도 떨림 {log[1500:, 1].std():.2f} rad/s, 실제 속도 떨림 {log[1500:, 0].std():.3f} rad/s"
)  # 1.98, 0.058
```

P 만 쓰면 목표 10 rad/s 에 8.72 rad/s 로 못 미치고, 1초에 부하(0.02 N·m)가 걸리면 6.84 rad/s 로 더
떨어진다. PI 는 두 경우 모두 10.00 으로 되돌린다. 측정 속도는 양자화 때문에 표준편차 2 rad/s 로
떨리는데, 실제 속도의 떨림은 0.06 rad/s 뿐이다. 모터의 관성이 떨리는 듀티를 걸러 주기 때문이다.

**연습 과제(exercise):** (1) `window=10` 으로 바꿔 분해능, 측정 속도의 떨림, 실제 속도의 떨림이 어떻게
달라지는지 보라(`run(0.05, 1.0, window=10)`). (2) 목표를 1 rad/s 로 낮추면(`w_ref=1.0`) `window=1` 과
`window=10` 에서 측정값이 어떤 값들만 나오는가? (3) 목표 100 rad/s, 1초에 부하 0.1 N·m 를 걸고
(`w_ref=100, tau_load=0.1, T=3.0`) `sag=False` 와 `sag=True` 의 마지막 속도와 듀티를 비교하라. 목표에
못 미치는 이유를 식으로 설명하라.

```expected
1. 창을 10 ms 로 늘리면 측정이 고와지고 그 결과 듀티와 실제 속도도 덜 떨린다.

   | `window` | 분해능 | 측정 속도 표준편차 | 실제 속도 표준편차 |
   | --- | --- | --- | --- |
   | 1 (1 ms) | 4.36 rad/s | 1.98 rad/s | 0.058 rad/s |
   | 10 (10 ms) | 0.44 rad/s | 0.12 rad/s | 0.008 rad/s |

   대가는 평균 5 ms 의 측정 지연이다. 이득을 더 올리면 긴 창 쪽이 먼저 진동하기 시작한다.
2. 1 rad/s 에서는 카운트가 약 4.4 ms 에 하나씩 온다. `window=1` 이면 측정값은 0 아니면 4.36 rad/s
   두 가지뿐이라, 제어기는 "멈췄다"와 "네 배 넘게 빠르다" 사이를 오가는 신호를 받는다. 실제 속도의
   평균은 1.0 으로 맞지만(적분항이 평균을 맞춘다) 듀티가 계속 튄다. `window=10` 이면 측정값이 0.87 과
   1.31 rad/s 로 좁혀지고 실제 속도의 떨림이 0.058 에서 0.010 rad/s 로 준다. 이보다 더 느린 속도에서는
   주기법이나 더 촘촘한 엔코더가 필요하다.
3. 부하가 걸린 뒤 두 경우 모두 듀티가 1.0 에 포화되고 목표에 못 미친다.

   | | 부하 전 | 부하 후 속도 | 듀티 | 전류 |
   | --- | --- | --- | --- | --- |
   | `sag=False` | 100.0 rad/s | 63.0 rad/s | 1.0 | 2.1 A |
   | `sag=True` | 100.0 rad/s | 53.2 rad/s | 1.0 | 2.1 A |

   100 rad/s 에서 0.1 N·m 를 내려면 전류가 $(b\omega + \tau_{load})/k \approx 2.2$ A, 전압이
   $Ri + k\omega \approx 2 \times 2.2 + 0.05 \times 100 = 9.4$ V 필요한데 배터리는 7.4 V 다. 제어기가 아무리
   잘해도 낼 수 없는 속도다. 전압 강하를 넣으면 단자 전압이 $7.4 - 0.25 \times 2.1 \approx 6.9$ V 로 더
   내려가 속도가 10 rad/s 가량 더 떨어진다. 이럴 때 고칠 것은 이득이 아니라 모터·기어비·배터리다.
   anti-windup 이 없다면 이 구간에서 적분이 끝없이 쌓여, 부하가 사라진 뒤 한참 동안 과속한다.
```

## 자가 점검 질문

1. PPR 이 같은 엔코더를 모터 축에 달 때와 바퀴 축에 달 때 바퀴 각도의 분해능은 어떻게 다른가?
2. 속도 측정 창을 길게 하면 좋아지는 것과 나빠지는 것은 각각 무엇인가?
3. 캐스케이드 제어에서 안쪽 루프가 바깥 루프보다 빨라야 하는 이유는 무엇인가?

## 확인 퀴즈

`rc quiz m11-encoders-speed-loop` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m11-encoders-speed-loop-quiz
questions:
  - id: q1
    type: single
    prompt: 'PPR 11 인 쿼드러처 엔코더가 모터 축에 달려 있고 기어비가 50 이다. 4체배로 세면 바퀴 한 바퀴당 카운트는?'
    choices:
      - '2200'
      - '550'
      - '44'
      - '1100'
    answer: 0
    explanation: '$4 \times 11 \times 50 = 2200$. 4체배는 A·B 두 채널의 오름·내림을 모두 세는 것이고, 엔코더가 모터 축에 있으므로 기어비만큼 더 곱해진다.'
    concept: { front: '바퀴 한 바퀴당 엔코더 카운트', back: '4 × PPR × 기어비 (엔코더가 모터 축에 있을 때)' }
  - id: q2
    type: single
    prompt: '카운트법 속도 측정의 창을 1 ms 에서 10 ms 로 늘리면?'
    choices:
      - '분해능이 10배 좋아지고 측정 지연이 늘어난다'
      - '분해능이 10배 나빠지고 측정 지연이 줄어든다'
      - '분해능과 지연 모두 변하지 않는다'
      - '분해능과 지연 모두 좋아진다'
    answer: 0
    explanation: '분해능은 $2\pi/(\text{CPR}\,T_w)$ 라 창이 10배면 10배 곱다. 대신 창 안의 평균 속도를 재는 것이므로 평균 $T_w/2$ 만큼 늦다. 노이즈와 지연의 절충이다.'
    concept: { front: '카운트법 속도 측정의 창 길이', back: '창↑ → 분해능 좋아짐, 지연(창의 절반) 늘어남' }
  - id: q3
    type: truefalse
    prompt: '속도 루프의 출력이 듀티 1.0 에 포화된 채 목표 속도에 못 미친다면 적분 이득을 올려 해결할 수 있다.'
    answer: false
    explanation: '포화는 전원 전압이 모자라다는 뜻이다. 제어기는 이미 낼 수 있는 최대를 내고 있어 이득으로는 바뀌지 않는다. 모터·기어비·배터리 전압을 바꾸거나 목표를 낮춰야 한다. 적분 이득을 올리면 와인드업만 심해진다.'
    concept: { front: '속도 루프가 포화된 채 목표에 못 미칠 때', back: '이득 문제가 아니라 전압·토크 부족 — 모터·기어비·배터리를 본다' }
```

## 이 단계 공부법

1. **본문(먼저):** 캐스케이드 표를 M3 의 경로 추종 그림과 연결해 "명령이 위에서 아래로, 측정이 아래에서
   위로" 흐르는 블록 그림을 그린다.
2. **예제:** 코드를 실행하고 `log` 의 세 열(실제 속도, 측정 속도, 듀티)을 시간에 대해 그린다.
3. **연습:** 세 문항을 실행하기 전에 결과를 예측해 적는다. 특히 (3)은 필요한 전압을 손으로 먼저 계산한다.
4. **확인:** `kp` 를 0.05 에서 0.5 로 올려 측정 양자화가 듀티를 얼마나 흔드는지 보고, 창 길이로
   완화되는지 확인한다.

## 참고 자료

- Åström & Murray, *Feedback Systems*, 2nd ed. (무료 PDF) — <https://fbswiki.org/wiki/index.php/Main_Page>
- Control Tutorials for MATLAB and Simulink, DC Motor Speed: PID Controller Design — <https://ctms.engin.umich.edu/CTMS/index.php?example=MotorSpeed&section=ControlPID>
- Ben-Ari & Mondada, *Elements of Robotics* (오픈 액세스) — <https://link.springer.com/book/10.1007/978-3-319-62533-1>
