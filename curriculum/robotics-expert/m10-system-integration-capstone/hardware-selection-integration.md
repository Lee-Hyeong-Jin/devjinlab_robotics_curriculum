---
id: m10-hardware-selection-integration
title: "하드웨어 선정과 통합(센서·액추에이터·컴퓨팅, 전원, 통신)"
summary: 요구사항의 수치에서 출발해 센서·액추에이터·컴퓨팅 보드를 고르고, 전원 예산과 통신 버스(UART·USB·I2C·CAN·Ethernet)를 설계한다. 2026년 가격 변동을 반영한 예산 사다리와 전력·비용 계산 스크립트로 부품표(BOM)를 검증한다.
objectives:
  - NFR(속도·정확도·주기·예산)에서 센서 사양(범위·분해능·주기)과 모터 사양(토크·속도·인코더)을 역산할 수 있다.
  - 상위 제어기(SBC)와 하위 제어기(MCU)의 역할 분담과, 그 사이 통신 방식을 근거를 들어 선택할 수 있다.
  - 부품별 전류를 합산해 배터리 용량·런타임·전압 레일을 설계하고, BOM 총액을 예산과 대조할 수 있다.
prerequisites: [m10-system-architecture-requirements, m4-sensor-models, m3-differential-drive]
difficulty: 4
estimated_minutes: 120
tags: [hardware, bom, sensors, actuators, power, communication, budget]
activities:
  - id: m10-hardware-selection-integration-reading
    kind: reading
    title: 본문과 시스템 해부 강의
    estimated_minutes: 45
  - id: m10-hardware-selection-integration-quiz
    kind: quiz
    title: 통신 버스·전원 설계 퀴즈
    estimated_minutes: 15
  - id: m10-hardware-selection-integration-exercise
    kind: exercise
    title: 내 캡스톤 BOM 과 전력 예산표 작성
    estimated_minutes: 60
resources:
  - title: "현직자가 알려주는 로보틱스 시스템 완전 해부: 부품부터 통신까지 (인프런, jelly)"
    url: https://www.inflearn.com/course/a-complete-breakdown
    kind: course
    note: 58분 17강(상/하위 제어기·모터 드라이버·센서·전원/비상정지; Serial·CAN·Ethernet·EtherCAT·SPI/I2C·패킷 설계), 29,700원(한국어).
  - title: SO-ARM100 (TheRobotStudio)
    url: https://github.com/TheRobotStudio/SO-ARM100
    kind: other
    note: SO-101 BOM(팔로워 $121.94 / 리더+팔로워 $229.88)·3D 프린팅·판매처(한국 RoboSEasy 포함).
  - title: TurtleBot3 Burger (Generation Robots)
    url: https://www.generationrobots.com/en/402707-turtlebot3-burger-mobile-robot.html
    kind: other
    note: €894.92(2026-11, RPi4-4GB·LDS-02). 국내 가격 미확인.
  - title: Raspberry Pi 5 가격 인상 (OMG! Ubuntu)
    url: https://omgubuntu.co.uk/2026/11/raspberry-pi-5-price-goes-up-and-up
    kind: article
    note: 2026 DRAM 부족으로 Pi 5 16GB $385. 컴퓨팅 예산을 넉넉히 잡아야 하는 근거.
  - title: micro_ros_setup (micro-ROS)
    url: https://github.com/micro-ROS/micro_ros_setup
    kind: other
    note: ESP32·Pico·STM32 등 MCU 를 ROS 2 그래프에 직접 붙이는 하위 제어기 경로.
---

# 하드웨어 선정과 통합

L10.1 에서 요구사항과 인터페이스를 정했다. 이제 그 인터페이스 뒤에 실제 부품을 꽂을 차례다. 하드웨어
선정은 "좋은 부품 고르기"가 아니라 **요구사항 수치를 만족하는 가장 싸고 단순한 조합 찾기**다. 그리고
2026년은 그 계산이 특히 까다로운 해다. DRAM 부족으로 Raspberry Pi 5 16GB 가 $385, Jetson Orin Nano
Super 가 $249 에서 $399 로 올랐고, Jetson Nano 는 단종(EOL) 수순이다.

## 개념

### 요구사항에서 사양으로 역산

- **센서:** "0.3 m/s 로 달리며 장애물 앞 0.5 m 에서 정지" → 반응 시간 = 센서 주기 + 처리 지연 + 제동.
  LiDAR 가 10 Hz 면 최악 0.1 s 동안 3 cm 를 이동한다. 범위·분해능·주기는 M4 의 센서 모델 관점에서 본다.
  저가 2D LiDAR 로는 LD19 계열(약 $69, 후속 D500 권장)과 RPLIDAR A1(약 $99)이 ROS 2 드라이버를 갖췄다.
  깊이 카메라 OAK-D Lite 는 2026-07 에 $169 → $269 로 올랐다.
- **액추에이터:** 차동 구동(M3)이면 바퀴 반지름 $r$ 과 최대 속도 $v$ 에서 모터 회전수 $\omega = v / r$,
  가속·경사에서 필요한 토크를 구한다. 인코더 분해능은 오도메트리 정확도(M5)를 좌우한다. 매니퓰레이터라면
  SO-101 처럼 위치 제어 서보(STS3215)를 직렬 버스로 묶는 구성이 가장 저렴하다.
- **컴퓨팅:** SLAM·Nav2 까지는 CPU 기반 SBC(Pi 4/5)로 충분하고, 신경망 추론을 로봇 위에서 돌릴 때만 GPU
  보드가 필요하다. 학습은 노트북·클라우드에서 하고 로봇에는 추론만 올리는 분리가 예산을 크게 줄인다.

### 상위·하위 제어기 분담

| 계층 | 예 | 하는 일 | 시간 특성 |
|---|---|---|---|
| 상위(SBC) | Raspberry Pi, Jetson | ROS 2, SLAM, 계획, 로깅 | 수십 ms, 비실시간 OS |
| 하위(MCU) | ESP32, Pico, STM32 | 모터 PWM, 인코더 카운트, 워치독 | 1 ms 이하, 결정적 |

둘 사이는 USB 시리얼(UART) + 직접 설계한 패킷이 가장 흔하고, micro-ROS 를 쓰면 MCU 가 ROS 2 노드로
보인다. 여러 모터 드라이버를 잇는 산업용 구성은 CAN·EtherCAT 를, 센서 근거리 연결은 I2C·SPI 를 쓴다.

### 전원과 배선

- 모터 레일과 로직 레일을 분리하고(모터 기동 전류의 전압 강하가 SBC 를 재부팅시킨다), 접지는 한 점에서 묶는다.
- 런타임 ≈ 배터리 용량(Wh) × 0.8 / 평균 소비 전력(W). 0.8 은 방전 깊이·변환 손실 여유다.
- 퓨즈와 **물리 비상정지(E-stop) 스위치는 모터 전원을 직접 끊는 위치**에 둔다(L10.3).

## 핵심 체크리스트

- [ ] 모든 부품 사양이 L10.1 의 NFR 수치 하나 이상에서 역산되었다.
- [ ] 각 부품에 ROS 2(Jazzy) 드라이버 또는 MCU 펌웨어 경로가 확인되어 있다.
- [ ] 상위·하위 제어기 통신 방식, 보드레이트, 패킷 형식(체크섬 포함)이 정해져 있다.
- [ ] 전력 예산표에 최대 전류와 평균 전류가 따로 있다.
- [ ] BOM 에 단가·수량·판매처·예비품이 있고, 총액이 예산의 80% 이하(나머지는 고장·환율 여유)다.

## 예제

전력 예산과 BOM 총액을 한 번에 검사한다. 수치는 예시이며 실제 부품 데이터시트로 바꿔 넣는다.

```python
parts = [
    # 이름, 레일, 평균 A, 최대 A, 단가(USD), 수량
    ("Raspberry Pi 5 4GB", "5V", 1.2, 2.5, 120.0, 1),
    ("LD19 LiDAR", "5V", 0.18, 0.3, 69.0, 1),
    ("ESP32 보드", "5V", 0.1, 0.25, 10.0, 1),
    ("DC 기어드 모터(인코더)", "12V", 0.4, 2.0, 20.0, 2),
    ("모터 드라이버", "12V", 0.02, 0.05, 12.0, 1),
]
battery_wh, budget_usd, regulator_5v_max_a = 3 * 3.7 * 2.6, 450.0, 3.0  # 3S 2600mAh

power_w = 0.0
for rail in ("5V", "12V"):
    volts = float(rail.rstrip("V"))
    avg = sum(a * n for _, r, a, _, _, n in parts if r == rail)
    peak = sum(p * n for _, r, _, p, _, n in parts if r == rail)
    power_w += avg * volts
    print(f"{rail:>4} 평균 {avg:4.2f} A, 최대 {peak:4.2f} A")
    if rail == "5V" and peak > regulator_5v_max_a:
        print(f"     경고: 5V 레귤레이터 {regulator_5v_max_a} A < 최대 {peak:.2f} A")

runtime_h = battery_wh * 0.8 / power_w
total = sum(price * n for *_, price, n in parts)
print(f"평균 소비 {power_w:.1f} W, 예상 런타임 {runtime_h:.1f} h")
print(f"BOM {total:.0f} USD / 예산 {budget_usd:.0f} USD ({total / budget_usd:.0%})")
```

출력에서 5V 최대 전류(3.05 A)가 레귤레이터 한계(3 A)를 넘는다는 경고가 나온다. Pi 5 는 부팅·USB
부하 때 전류가 튀므로 5 A 급 레귤레이터로 바꾸는 것이 맞다. 예산 비율이 80% 를 넘는지도 함께 본다.

**연습 과제(exercise):** 자신의 캡스톤 BOM 을 위 표 형식으로 만들고, (1) 레일별 최대 전류, (2) 런타임,
(3) 예산 비율을 계산하라. 가격은 확인한 날짜와 판매처를 함께 적는다.

## 자가 점검 질문

1. 모터와 SBC 를 같은 5 V 레귤레이터에 물리면 어떤 증상이 생기고, 왜 그런가?
2. 모터 PWM 과 인코더 카운트를 Raspberry Pi 의 Python 노드에서 직접 처리하지 않고 MCU 에 맡기는 이유는?
3. 신경망 추론이 필요 없는 Nav2 로봇에 GPU 보드를 고르면 예산·전력 면에서 무엇을 잃는가?

## 이 단계 공부법

1. **강의(먼저):** 인프런 "로보틱스 시스템 완전 해부"(58분)로 상·하위 제어기, 통신 버스, 전원·비상정지 구조를 한 번에 본다.
2. **BOM 읽기:** SO-ARM100 README 의 BOM 과 TurtleBot3 Burger 구성품을 비교해 "완제품 vs 직접 조립"의 가격·시간 차이를 적는다.
3. **가격 확인:** 컴퓨팅 보드는 2026년 가격 변동이 크므로 구입 직전에 다시 확인한다(OMG! Ubuntu 기사 참고).
4. **하위 제어기(선택):** micro_ros_setup README 로 ESP32·Pico 를 ROS 2 노드로 붙이는 경로를 훑는다.

## 참고 자료

- jelly, "현직자가 알려주는 로보틱스 시스템 완전 해부: 부품부터 통신까지", 인프런 — <https://www.inflearn.com/course/a-complete-breakdown>
- TheRobotStudio, SO-ARM100 — <https://github.com/TheRobotStudio/SO-ARM100>
- Generation Robots, TurtleBot3 Burger — <https://www.generationrobots.com/en/402707-turtlebot3-burger-mobile-robot.html>
- OMG! Ubuntu, Raspberry Pi 5 가격 인상(2026-11) — <https://omgubuntu.co.uk/2026/11/raspberry-pi-5-price-goes-up-and-up>
- micro-ROS, micro_ros_setup — <https://github.com/micro-ROS/micro_ros_setup>
