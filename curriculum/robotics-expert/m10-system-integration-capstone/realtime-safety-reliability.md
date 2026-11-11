---
id: m10-realtime-safety-reliability
title: "실시간성·안전·신뢰성(워치독, 페일세이프, 기능 안전 개요)"
summary: 로봇 소프트웨어에서 "실시간"이 무엇을 뜻하는지(마감 시간과 지터), 명령 끊김·센서 고장·과전류에 대비한 워치독과 페일세이프 설계, 하드웨어 비상정지의 위치, 그리고 기능 안전 표준이 요구하는 사고방식(위험 분석→안전 기능→검증)을 개요 수준으로 익힌다.
objectives:
  - 연성·경성 실시간을 구분하고, 제어 루프의 주기·지연·지터를 측정해 요구사항과 비교할 수 있다.
  - 명령 타임아웃 워치독과 안전 상태(정지·감속)로 가는 상태 기계를 설계하고 코드로 구현할 수 있다.
  - 고장 모드를 나열하고 각각의 감지 방법과 안전 반응을 표(간이 FMEA)로 정리할 수 있다.
prerequisites: [m10-hardware-selection-integration, m3-pid-control]
difficulty: 4
estimated_minutes: 120
tags: [real-time, safety, watchdog, failsafe, reliability, fmea, e-stop]
activities:
  - id: m10-realtime-safety-reliability-reading
    kind: reading
    title: 본문과 전원·비상정지 구조 강의
    estimated_minutes: 40
  - id: m10-realtime-safety-reliability-quiz
    kind: quiz
    title: 워치독·페일세이프 시나리오 퀴즈
    estimated_minutes: 20
  - id: m10-realtime-safety-reliability-exercise
    kind: exercise
    title: 워치독 상태 기계 구현과 간이 FMEA 표 작성
    estimated_minutes: 60
resources:
  - title: "현직자가 알려주는 로보틱스 시스템 완전 해부: 부품부터 통신까지 (인프런, jelly)"
    url: https://www.inflearn.com/course/a-complete-breakdown
    kind: course
    note: 전원/비상정지, 상·하위 제어기 분담 절. 29,700원(한국어).
  - title: ros2_control Getting Started
    url: https://control.ros.org/rolling/doc/getting_started/getting_started.html
    kind: article
    note: Controller Manager·하드웨어 컴포넌트의 실시간 루프 구조. Jazzy/Kilted/Lyrical 문서 선택 가능.
  - title: Getting started with micro-ROS on Raspberry Pi Pico (Canonical)
    url: https://ubuntu.com/blog/getting-started-with-micro-ros-on-raspberry-pi-pico
    kind: article
    note: MCU 에 워치독·모터 차단을 두는 하위 제어기 실습의 출발점.
  - title: 기능 안전 표준 개요 — IEC 61508, ISO 10218, ISO 13482
    kind: other
    note: 원문은 유료이며 조사 노트에서 URL 을 확보하지 못했다. 표준 이름과 적용 범위만 알아 두는 수준.
---

# 실시간성·안전·신뢰성

데모 영상 속 로봇은 늘 잘 움직인다. 실제 로봇의 품질은 **무언가 잘못되었을 때** 드러난다. 와이파이가
끊기면, LiDAR 케이블이 빠지면, 노드가 예외로 죽으면 로봇은 어떻게 하는가? 이 레슨은 그 질문에 설계로
답하는 법을 다룬다. 캡스톤 평가표(L10.5)에서도 안전 항목은 별도 배점이 있다.

## 개념

### 실시간은 "빠르다"가 아니라 "제때"다

실시간 시스템은 **마감 시간(deadline)을 지키는** 시스템이다. 50 Hz 제어 루프는 20 ms 마다 실행되어야 하고,
실제 주기의 흔들림을 **지터**라고 한다.

- **경성(hard) 실시간:** 마감을 한 번이라도 놓치면 고장(모터 전류 제어, 에어백). MCU·RTOS 영역.
- **연성(soft) 실시간:** 가끔 늦어도 성능만 떨어짐(Nav2 지역 플래너, SLAM). 일반 Linux + ROS 2 영역.

그래서 L10.2 의 분담이 나온다. 마감이 1 ms 이하이고 놓치면 위험한 일(PWM, 전류 제한, 최종 워치독)은
MCU 에, 수십 ms 단위의 판단은 SBC 에 둔다. ros2_control 은 SBC 위에서 읽기→갱신→쓰기 루프를 정해진
주기로 돌리는 구조이며, PREEMPT_RT 커널로 지터를 줄일 수 있지만 그래도 MCU 를 대체하지는 않는다.

### 워치독과 페일세이프

**워치독**은 "살아 있다"는 신호(heartbeat)가 일정 시간 안에 오지 않으면 안전 동작을 강제하는 감시자다.

- 소프트웨어 워치독: 베이스 컨트롤러가 `/cmd_vel` 을 0.5 s 이상 못 받으면 속도 0.
- 하드웨어 워치독: MCU 가 SBC 의 시리얼 패킷을 못 받으면 모터 드라이버 Enable 핀을 내림.
- MCU 자체 워치독 타이머: 펌웨어가 멈추면 MCU 를 리셋.

**페일세이프**는 고장 시 시스템이 미리 정한 **안전 상태**로 가는 성질이다. 이동 로봇의 안전 상태는 대개
"정지 + 브레이크", 매니퓰레이터는 "현재 자세 유지" 또는 "토크 해제 후 낙하 방지"처럼 플랫폼마다 다르다.
고장을 감지하지 못하면 안전 상태로 갈 수도 없으므로, **감지 → 반응**을 한 쌍으로 설계한다.

### 비상정지(E-stop)는 소프트웨어가 아니다

물리 E-stop 은 소프트웨어가 전부 멈춰도 동작해야 하므로 **모터 전원 회로를 직접 끊는다**. 소프트웨어
정지 버튼(토픽)은 편의 기능일 뿐 E-stop 을 대신하지 않는다.

### 기능 안전의 사고방식(개요)

IEC 61508(전기·전자 안전 관련 시스템 일반), ISO 10218(산업용 로봇), ISO 13482(개인 케어 로봇) 같은
표준은 공통적으로 **위험 분석 → 안전 기능 정의 → 요구 무결성 수준 결정 → 검증·문서화**를 요구한다.
캡스톤에서 인증을 받을 일은 없지만, 이 흐름을 간이 FMEA(고장 모드·영향 분석) 표로 흉내 내는 것만으로도
설계 품질이 눈에 띄게 올라간다.

## 핵심 체크리스트

- [ ] 각 제어 루프의 목표 주기와 실측 최대 지터를 기록했다.
- [ ] 명령 타임아웃 워치독이 SBC 와 MCU 양쪽에 있다.
- [ ] 물리 E-stop 이 모터 전원을 직접 끊는다.
- [ ] 고장 모드 표에 감지 방법·안전 반응·복구 조건이 있다.
- [ ] 안전 상태에서 자동으로 다시 움직이지 않는다(사람이 명시적으로 재개).

## 예제

명령 타임아웃 워치독을 상태 기계로 구현하고, 가짜 시간으로 시나리오를 돌린다.

```python
from enum import Enum


class State(Enum):
    RUN = "RUN"
    SAFE_STOP = "SAFE_STOP"


class CmdWatchdog:
    def __init__(self, timeout_s=0.5, max_speed=0.3):
        self.timeout_s, self.max_speed = timeout_s, max_speed
        self.state, self.last_cmd_t, self.cmd = State.SAFE_STOP, None, 0.0

    def on_cmd(self, t, v):
        self.last_cmd_t, self.cmd = t, max(-self.max_speed, min(self.max_speed, v))

    def reset(self, t):  # 사람이 명시적으로 재개해야만 RUN
        if self.last_cmd_t is not None and t - self.last_cmd_t < self.timeout_s:
            self.state = State.RUN

    def output(self, t):
        if self.state is State.RUN and (
            self.last_cmd_t is None or t - self.last_cmd_t > self.timeout_s
        ):
            self.state = State.SAFE_STOP  # 감지 → 안전 상태
        return self.cmd if self.state is State.RUN else 0.0


wd = CmdWatchdog()
events = {0.00: ("cmd", 0.5), 0.10: ("reset", None), 0.40: ("cmd", 0.2), 1.50: ("cmd", 0.2)}
for k in range(0, 200, 10):  # 0~2 s, 100 ms 간격(50 Hz 루프를 성기게 샘플)
    t = k / 100
    kind, v = events.get(t, (None, None))
    if kind == "cmd":
        wd.on_cmd(t, v)
    elif kind == "reset":
        wd.reset(t)
    out = wd.output(t)
    print(f"t={t:4.2f}s  상태={wd.state.value:9s}  출력={out:4.2f} m/s")
```

0.5 m/s 명령은 0.3 m/s 로 잘리고, 0.4 s 의 마지막 명령에서 0.5 s 가 넘게 지난 1.0 s 에 SAFE_STOP 으로 떨어진다.
1.5 s 에 명령이 다시 와도 `reset` 없이는 움직이지 않는다. 이것이 "자동 재개 금지" 규칙이다.

**연습 과제(exercise):** (1) 위 클래스를 rclpy 노드로 감싸 `/cmd_vel` 을 구독하고 50 Hz 타이머로 출력하라.
(2) 캡스톤 로봇의 고장 모드 6개 이상(통신 끊김, LiDAR 무응답, 배터리 저전압, 노드 예외 종료, 인코더
오류, 위치 추정 발산)에 대해 감지·반응·복구 열을 가진 FMEA 표를 작성하라.

## 자가 점검 질문

1. Nav2 지역 플래너가 가끔 30 ms 늦게 끝나는 것과 모터 전류 루프가 가끔 1 ms 늦는 것의 위험도는 왜 다른가?
2. 소프트웨어 정지 토픽만 있고 물리 E-stop 이 없을 때, 어떤 고장에서 로봇을 멈출 수 없는가?
3. 워치독이 안전 상태로 간 뒤 명령이 다시 들어오면 자동으로 움직이게 하는 설계의 위험은 무엇인가?

## 이 단계 공부법

1. **강의(먼저):** 인프런 "로보틱스 시스템 완전 해부"의 전원·비상정지 절을 다시 보며 E-stop 배선 위치를 그린다.
2. **본문 + 예제:** 워치독 예제의 이벤트 시각을 바꿔 가며 상태 전이를 손으로 예측한 뒤 실행해 맞춰 본다.
3. **문서:** ros2_control Getting Started 에서 제어 루프와 하드웨어 컴포넌트의 경계를 읽고, 워치독이 어디에 들어갈지 표시한다.
4. **하위 제어기(선택):** micro-ROS Pico 튜토리얼로 MCU 쪽 heartbeat 감시를 직접 구현해 본다.

## 참고 자료

- jelly, "현직자가 알려주는 로보틱스 시스템 완전 해부: 부품부터 통신까지", 인프런 — <https://www.inflearn.com/course/a-complete-breakdown>
- ros2_control, Getting Started — <https://control.ros.org/rolling/doc/getting_started/getting_started.html>
- Canonical, "Getting started with micro-ROS on Raspberry Pi Pico" — <https://ubuntu.com/blog/getting-started-with-micro-ros-on-raspberry-pi-pico>
- IEC 61508 / ISO 10218 / ISO 13482 (표준 원문, 유료; URL 미확보)
