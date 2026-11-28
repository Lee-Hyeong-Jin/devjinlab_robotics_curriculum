---
id: m11-motors-gearing
title: 모터의 종류와 고르기
summary: 브러시드 DC·서보·스테퍼·BLDC 모터의 차이를 정리하고, DC 모터의 토크-속도 직선과 기어비로 "이 로봇을 이 모터로 움직일 수 있는가"를 계산한다.
objectives:
  - 브러시드 DC, RC 서보, 스테퍼, BLDC 모터의 구동 방식과 로봇에서의 쓰임을 구분할 수 있다.
  - 데이터시트의 무부하 속도와 정지 토크에서 토크-속도 직선, 정지 전류, 최대 출력점을 계산할 수 있다.
  - 로봇의 질량·바퀴 반지름·가속도·경사 요구에서 필요한 바퀴 토크와 속도를 구하고 기어비를 고를 수 있다.
prerequisites: [m3-differential-drive]
difficulty: 2
estimated_minutes: 80
tags: [actuators, dc-motor, bldc, servo, stepper, gearing, sizing]
activities:
  - id: m11-motors-gearing-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 30
  - id: m11-motors-gearing-quiz
    kind: quiz
    title: 토크-속도 곡선과 기어비 퀴즈
    estimated_minutes: 10
  - id: m11-motors-gearing-exercise
    kind: exercise
    title: 요구 조건에서 모터와 기어비 고르기
    estimated_minutes: 40
resources:
  - title: "Modern Robotics, 8.9절 Actuation, Gearing, and Friction (Lynch & Park)"
    url: https://hades.mech.northwestern.edu/index.php/Modern_Robotics
    kind: book
    note: DC 모터 모델, 토크-속도 곡선, 기어의 겉보기 관성. 책 PDF 와 강의 영상이 무료다.
  - title: "Elements of Robotics (Ben-Ari & Mondada)"
    url: https://link.springer.com/book/10.1007/978-3-319-62533-1
    kind: book
    note: 오픈 액세스. 1–5장에서 센서·모터·바퀴 로봇의 움직임을 쉬운 말로 다룬다.
  - title: "DC Motor Speed: System Modeling (Control Tutorials for MATLAB and Simulink)"
    url: https://ctms.engin.umich.edu/CTMS/index.php?example=MotorSpeed&section=SystemModeling
    kind: article
    note: 이 레슨의 모터 방정식을 전달 함수로 유도한다. 미시간 대학 무료 자료.
---

# 모터의 종류와 고르기

M3 에서는 "바퀴 속도 $\omega_R$, $\omega_L$ 을 명령하면 그대로 돈다"고 가정했다. 실제로는 그 속도를
만들어 내는 모터가 있고, 모터는 낼 수 있는 토크와 속도에 한계가 있다. 로봇이 경사를 못 오르거나, 출발할
때 덜컥거리거나, 배터리가 금방 닳는 문제의 상당수는 코드가 아니라 모터와 기어를 잘못 고른 데서 온다.
이 레슨은 데이터시트의 숫자 두세 개로 그 판단을 하는 법을 다룬다.

## 어디에 쓰는가

로봇 청소기의 바퀴, 로봇 팔의 관절, 드론의 프로펠러, 3D 프린터의 축은 모두 모터지만 종류가 다르다.
바퀴 로봇을 처음 만들 때는 "기어 달린 DC 모터 중 무엇을 살 것인가"가 첫 결정이고, 로봇 팔이나 다리
로봇을 설계할 때는 관절마다 토크·속도 요구를 계산해 모터와 감속기를 고른다. M10 의 캡스톤에서 요구
사양으로부터 부품을 정하는 절차가 이 레슨의 계산을 그대로 쓴다.

## 개념

### 네 가지 모터

| 종류 | 구동 방식 | 장점 | 약점 | 로봇에서의 쓰임 |
|---|---|---|---|---|
| 브러시드 DC | 전압을 걸면 돈다. 전압으로 속도, 전류로 토크가 정해진다 | 싸고 단순하다 | 브러시 마모, 효율 | 소형 바퀴 로봇, 저가 그리퍼 |
| RC 서보 | DC 모터 + 기어 + 위치 제어기가 한 몸. 목표 각도를 신호로 준다 | 배선 3가닥, 각도 제어가 내장 | 각도 범위·정밀도 제한, 상태를 알기 어렵다 | 소형 팔, 팬틸트 |
| 스테퍼 | 펄스 하나에 정해진 각도만큼 돈다 | 엔코더 없이 위치 제어 | 과부하 시 탈조(스텝을 잃음), 고속 토크 약함 | 3D 프린터, 직교 로봇 |
| BLDC | 권선 전류를 전자 회로가 순서대로 바꾼다(전자 정류) | 효율·출력 밀도·수명 | 전용 드라이버와 회전자 각도 정보가 필요 | 드론, 다리 로봇, 협동 로봇 관절 |

시리얼 버스 서보("스마트 서보")는 RC 서보에 통신을 더한 것으로, 위치·속도·전류·온도를 읽을 수 있어
교육용 로봇 팔에 많이 쓰인다.

### DC 모터의 두 식

브러시드 DC 모터는 식 두 개로 충분히 설명된다. 전류가 토크를 만들고, 회전이 전압(역기전력)을 만든다.

$$\tau = k_t\, i, \qquad V = R\, i + k_e\, \omega$$

SI 단위에서는 $k_t = k_e$ 다. 두 식에서 $i$ 를 지우면 **토크-속도 직선**이 나온다. 속도가 오를수록
역기전력이 전류를 줄여 낼 수 있는 토크가 줄어든다. 양 끝점이 데이터시트의 두 숫자다.

- **정지 토크** $\tau_s = k_t V / R$: 축이 멈춰 있을 때의 최대 토크. 이때 전류($V/R$, 정지 전류)가 가장 크다.
- **무부하 속도** $\omega_0 = V / k_e$: 부하가 없을 때의 최대 속도. 이때 토크는 0 이다.

기계적 출력 $P = \tau\omega$ 는 직선의 한가운데($\omega_0/2$)에서 최대이고 그 값은 $\tau_s\omega_0/4$ 다.
정지 토크 근처에서 오래 쓰면 큰 전류가 열로 바뀌어 모터가 탄다. 연속으로 쓰는 토크는 정지 토크의
20–30% 이하로 잡는 것이 흔한 기준이다.

### 기어

소형 DC 모터는 빠르고 힘이 약하다(분당 수천~만 회전, 수 mN·m). 바퀴에 필요한 것은 그 반대다. 기어비
$N$ 의 감속기는 속도를 $1/N$ 로 줄이고 토크를 $N\eta$ 배로 키운다($\eta$ 는 효율, 소형 기어박스에서
0.6–0.8).

$$\omega_{out} = \frac{\omega_m}{N}, \qquad \tau_{out} = N\,\eta\,\tau_m$$

기어비가 너무 작으면 토크가 모자라고, 너무 크면 최고 속도가 모자란다. 기어비가 클수록 백래시(유격)와
마찰이 늘고, 바깥에서 축을 돌리기 어려워진다(역구동성 저하). 사람과 접촉하는 로봇 팔이나 다리 로봇이
큰 모터와 작은 기어비를 쓰는 이유다.

### 필요한 토크와 속도

바퀴 로봇에서 필요한 구동력은 가속, 경사, 구름 저항의 합이다.

$$F = m a + m g \sin\theta + c_{rr}\, m g \cos\theta$$

구동 바퀴가 $n$ 개면 바퀴 하나의 토크는 $\tau_w = F r / n$, 바퀴 속도는 $\omega_w = v_{max}/r$ 다. 모터는
이 **두 조건을 동시에** 만족해야 한다. 토크-속도 직선 위에서 필요한 점이 직선 아래에 있어야 한다.

## 핵심 수식

- 모터: $\tau = k_t i$, $V = R i + k_e\omega$ → $\tau(\omega) = k_t (V - k_e\omega)/R$
- 끝점: $\tau_s = k_t V/R$, $\omega_0 = V/k_e$, 최대 출력 $\tau_s\omega_0/4$ ($\omega_0/2$ 에서)
- 기어: $\omega_{out} = \omega_m/N$, $\tau_{out} = N\eta\tau_m$
- 요구: $F = ma + mg\sin\theta + c_{rr} mg\cos\theta$, $\tau_w = Fr/n$, $\omega_w = v_{max}/r$

## 예제

데이터시트 값 세 개(정격 전압, 무부하 속도, 정지 토크)로 모터 상수를 구하고, 2 kg 로봇의 요구 조건을
만족하는 기어비를 찾는다.

```python
import numpy as np

# 소형 브러시드 DC 모터 (데이터시트 값): 정격 6 V, 무부하 12000 rpm, 정지 토크 20 mN·m
V, w0, tau_s = 6.0, 12000 * 2 * np.pi / 60, 0.020
k = V / w0  # 역기전력 상수 k_e = 토크 상수 k_t [V·s/rad = N·m/A]
R = k * V / tau_s  # 권선 저항 [ohm]
print(f"k = {k * 1000:.2f} mN·m/A, R = {R:.2f} ohm, 정지 전류 = {V / R:.2f} A")  # 4.77, 1.43, 4.19


def motor_torque(w, v=V):
    return k * (v - k * w) / R  # 토크-속도 직선


# 요구 조건: 2 kg 로봇, 바퀴 반지름 3 cm, 구동 바퀴 2개
m, r, g = 2.0, 0.03, 9.81
a, slope, c_rr, v_max = 0.5, np.deg2rad(10), 0.03, 0.5
force = m * a + m * g * np.sin(slope) + c_rr * m * g * np.cos(slope)
tau_wheel, w_wheel = force * r / 2, v_max / r
print(
    f"필요 구동력 {force:.2f} N -> 바퀴당 {tau_wheel * 1000:.1f} mN·m, {w_wheel:.1f} rad/s"
)  # 4.99, 74.8, 16.7

eta = 0.7  # 기어박스 효율
for N in (10, 30, 50, 100):
    tau_m, w_m = tau_wheel / (N * eta), w_wheel * N
    ok = tau_m <= 0.3 * tau_s and motor_torque(w_m) >= tau_m
    print(
        f"N={N:3d}: 모터 토크 {tau_m / tau_s * 100:5.1f}% of stall, "
        f"모터 속도 {w_m / w0 * 100:5.1f}% of no-load -> {'OK' if ok else 'X'}"
    )
# N= 10: 53.4%, 13.3% -> X (토크 과다)   N= 30: 17.8%, 39.8% -> OK
# N= 50: 10.7%, 66.3% -> OK              N=100:  5.3%, 132.6% -> X (속도 부족)
```

기어비 10 은 토크가 정지 토크의 절반을 넘어 모터가 과열되고, 100 은 필요한 속도가 무부하 속도를 넘어
아예 낼 수 없다. 30–50 사이가 답이다.

**연습 과제(exercise):** (1) 이 모터의 최대 기계 출력과 그때의 회전 속도, 효율을 구하라. (2) 로봇
질량이 5 kg 으로 늘면 네 기어비 중 어느 것이 남는가? (3) 기어비 30, 질량 2 kg 일 때 10° 경사를 일정한
속도로 오르는 속도와 평지를 달리는 속도를 구하라(가속 항은 0). 요구 속도 0.5 m/s 와 비교해 무엇을 알 수 있는가?

```expected
1. 최대 출력은 $\tau_s\omega_0/4 = 0.020 \times 1256.6 / 4 = 6.28$ W, 무부하 속도의 절반인 6000 rpm 에서
   나온다. 이때 전류는 정지 전류의 절반(2.09 A)이라 전기 입력은 $6 \times 2.09 = 12.6$ W, 효율은 50% 다.
   최대 출력점은 효율이 좋은 점이 아니다. 효율은 무부하 속도에 가까운 쪽(작은 토크)에서 높다.
2. 필요 구동력이 12.47 N, 바퀴당 187 mN·m 로 늘어난다.

   | $N$ | 모터 토크(정지 토크 대비) | 모터 속도(무부하 대비) | 판정 |
   | --- | --- | --- | --- |
   | 10 | 133.6% | 13.3% | 불가(정지 토크보다 큼) |
   | 30 | 44.5% | 39.8% | 불가(30% 기준 초과, 과열) |
   | 50 | 26.7% | 66.3% | 가능 |
   | 100 | 13.4% | 132.6% | 불가(속도 부족) |

   기어비 50 하나만 남고 그것도 여유가 거의 없다. 더 큰 모터가 필요하다는 신호다.
3. 경사에서는 구동력 3.99 N, 모터 토크가 정지 토크의 14.2%(전류 0.60 A)이고 속도는 약 1.08 m/s 다.
   평지에서는 구름 저항만 이기면 되므로 전류 0.09 A, 속도 약 1.23 m/s 다. 둘 다 요구 속도 0.5 m/s 의
   두 배가 넘는다. 요구 속도는 "낼 수 있어야 하는" 속도이고, 실제 속도는 제어기가 전압(PWM)을 줄여
   맞춘다. 속도 여유가 크므로 기어비를 50 으로 올려 토크 여유를 더 얻는 선택도 가능하다.
```

## 자가 점검 질문

1. 모터 축을 손으로 잡아 멈추면 전류가 왜 커지는가? 역기전력으로 설명하라.
2. 기어비를 두 배로 하면 바퀴의 최대 토크와 최고 속도는 각각 어떻게 되는가?
3. 드론 프로펠러에 브러시드 DC 대신 BLDC 를 쓰는 이유 두 가지는 무엇인가?

## 확인 퀴즈

`rc quiz m11-motors-gearing` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m11-motors-gearing-quiz
questions:
  - id: q1
    type: single
    prompt: '브러시드 DC 모터에 일정한 전압을 건 채 축을 잡아 멈추면 어떻게 되는가?'
    choices:
      - '역기전력이 0 이 되어 전류가 최대(V/R)가 되고 모터가 뜨거워진다'
      - '전류가 0 이 되어 안전하다'
      - '속도가 0 이므로 토크도 0 이다'
      - '전압이 자동으로 내려간다'
    answer: 0
    explanation: '$V = Ri + k_e\omega$ 에서 $\omega = 0$ 이면 역기전력이 사라져 전류가 $V/R$ 로 최대가 된다. 토크도 최대(정지 토크)지만 전기 에너지가 전부 열이 되므로 오래 두면 권선이 탄다. 드라이버도 이 전류를 견뎌야 한다.'
    concept: { front: 'DC 모터의 정지(stall) 상태', back: '역기전력 0 → 전류 V/R 로 최대, 토크 최대, 전부 열로 — 드라이버·모터 과열 주의' }
  - id: q2
    type: single
    prompt: '기어비를 30 에서 60 으로 바꾸면(효율 같다고 가정) 바퀴에서 일어나는 변화는?'
    choices:
      - '최대 토크 2배, 최고 속도 절반'
      - '최대 토크 2배, 최고 속도 2배'
      - '최대 토크 절반, 최고 속도 2배'
      - '둘 다 변하지 않는다'
    answer: 0
    explanation: '감속기는 출력($\tau\omega$)을 키우지 않고 토크와 속도를 맞바꾼다. $\tau_{out} = N\eta\tau_m$, $\omega_{out} = \omega_m/N$ 이므로 기어비가 2배면 토크는 2배, 속도는 절반이다.'
    concept: { front: '기어비 N 의 효과', back: '토크 N·η 배, 속도 1/N — 출력은 늘지 않고 맞바꾼다' }
  - id: q3
    type: truefalse
    prompt: 'DC 모터는 정지 토크의 절반을 내는 점에서 효율이 가장 높다.'
    answer: false
    explanation: '정지 토크의 절반(속도는 무부하의 절반)은 기계 출력이 최대인 점이고, 그때 효율은 50% 다. 효율은 토크가 작고 속도가 무부하에 가까운 쪽에서 높다. 그래서 연속 운전점은 정지 토크의 20–30% 이하로 잡는다.'
    concept: { front: 'DC 모터의 최대 출력점과 효율', back: '최대 출력은 ω0/2 에서 τs·ω0/4, 효율 50%. 고효율은 저토크·고속 쪽' }
```

## 이 단계 공부법

1. **본문(먼저):** 두 식에서 토크-속도 직선을 손으로 유도하고, 직선을 그려 정지 토크·무부하 속도·
   최대 출력점을 표시한다.
2. **예제:** 코드를 실행하고 기어비마다 "필요한 점"을 직선 그림 위에 찍어 본다.
3. **연습:** 질량·경사·바퀴 반지름을 자신이 만들고 싶은 로봇 값으로 바꿔 다시 계산한다.
4. **확인:** 실제 기어 모터 데이터시트 하나를 찾아 무부하 속도와 정지 토크가 이 계산에 넣을 수 있는
   형태로 적혀 있는지(기어 포함인지 모터만인지) 확인한다.

## 참고 자료

- Lynch & Park, *Modern Robotics*, 8.9절 — <https://hades.mech.northwestern.edu/index.php/Modern_Robotics>
- Ben-Ari & Mondada, *Elements of Robotics* (오픈 액세스) — <https://link.springer.com/book/10.1007/978-3-319-62533-1>
- Control Tutorials for MATLAB and Simulink, DC Motor Speed — <https://ctms.engin.umich.edu/CTMS/index.php?example=MotorSpeed&section=SystemModeling>
