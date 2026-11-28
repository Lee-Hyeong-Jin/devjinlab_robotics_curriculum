---
id: m11-microcontrollers-buses
title: 마이크로컨트롤러와 보드 컴퓨터, 통신 버스
summary: 마이크로컨트롤러와 보드 컴퓨터가 각각 무엇을 잘하는지, 어떤 코드를 어디에서 돌려야 하는지를 실시간성으로 가르고, UART·I2C·SPI·CAN 을 비교한다. 둘 사이의 시리얼 프로토콜을 프레임·체크섬·타임아웃으로 짜 보고, micro-ROS 가 하는 일을 한 쪽으로 정리한다.
objectives:
  - 마이크로컨트롤러와 보드 컴퓨터의 차이를 실시간성 관점에서 설명하고, 로봇의 기능을 둘 중 어디에 둘지 정할 수 있다.
  - UART·I2C·SPI·CAN 의 배선·속도·거리·다중 연결 특성을 비교해 용도에 맞는 버스를 고를 수 있다.
  - 헤더·길이·체크섬이 있는 시리얼 프레임을 만들고 해석하며, 통신이 끊겼을 때 로봇을 멈추는 워치독의 필요성을 설명할 수 있다.
prerequisites: [m11-encoders-speed-loop, m11-power-budget]
difficulty: 2
estimated_minutes: 80
tags: [embedded, microcontroller, single-board-computer, real-time, uart, i2c, spi, can, micro-ros]
activities:
  - id: m11-microcontrollers-buses-reading
    kind: reading
    title: 본문 읽기
    estimated_minutes: 30
  - id: m11-microcontrollers-buses-quiz
    kind: quiz
    title: 역할 분담·버스 선택 퀴즈
    estimated_minutes: 10
  - id: m11-microcontrollers-buses-exercise
    kind: exercise
    title: 시리얼 프레임의 전송량·오류 검출·워치독 계산
    estimated_minutes: 40
resources:
  - title: micro-ROS
    url: https://micro.ros.org/
    kind: article
    note: 마이크로컨트롤러를 ROS 2 그래프에 넣는 프로젝트의 공식 문서. Overview 와 First micro-ROS Application 을 본다.
  - title: ros2_control documentation
    url: https://control.ros.org/
    kind: article
    note: 하드웨어 인터페이스(보드 컴퓨터 쪽에서 마이크로컨트롤러와 통신하는 자리)의 구조.
  - title: Arduino documentation — Learn
    url: https://docs.arduino.cc/learn/
    kind: article
    note: UART, I2C, SPI 의 배선과 기본 사용법을 그림으로 설명하는 입문 글.
---

# 마이크로컨트롤러와 보드 컴퓨터, 통신 버스

지금까지의 레슨에서 "모터 속도 루프를 1 kHz 로 돌린다", "엔코더 카운트를 놓치지 않는다", "통신이 끊기면
멈춘다"는 요구가 나왔다. 한편 M4 이후의 인식·SLAM·계획은 카메라와 큰 메모리, Linux 와 ROS 2 를
요구한다. 한 컴퓨터가 둘 다 잘하기는 어렵다. 그래서 거의 모든 로봇은 **마이크로컨트롤러(MCU)와 보드
컴퓨터(SBC)를 함께** 쓰고 둘을 통신으로 잇는다. 이 레슨은 그 경계를 어디에 긋고 무엇으로 이을지를 다룬다.

## 어디에 쓰는가

TurtleBot 급 로봇을 열어 보면 모터와 센서에 붙은 마이크로컨트롤러 보드와, ROS 2 를 돌리는 보드
컴퓨터가 USB(시리얼)로 연결되어 있다. 로봇 팔과 다리 로봇은 관절마다 드라이버가 있고 CAN 이나
EtherCAT 으로 묶인다. 센서를 하나 더 달 때 "이 센서는 I2C 인가 SPI 인가, 주소가 겹치지 않는가"를
확인하고, 로봇이 가끔 명령을 놓칠 때 통신 프레임과 타임아웃을 들여다보게 된다. M8 의 micro-ROS 와
`ros2_control` 하드웨어 인터페이스가 바로 이 경계에 놓인 소프트웨어다.

## 개념

### 두 종류의 컴퓨터

| | 마이크로컨트롤러(MCU) | 보드 컴퓨터(SBC) |
|---|---|---|
| 연산·메모리 | 수십~수백 MHz, RAM 수십 KB~수 MB | GHz 급 멀티코어, RAM 수 GB |
| 소프트웨어 | OS 없음 또는 RTOS. 켜면 수 ms 안에 시작 | Linux. 부팅에 수십 초 |
| 타이밍 | 타이머 인터럽트로 µs 단위까지 일정 | 다른 프로세스에 밀려 수 ms~수십 ms 흔들릴 수 있다 |
| 입출력 | 핀을 직접 다룬다: PWM, ADC, 타이머, 엔코더 카운터 | USB, 이더넷, 카메라, 와이파이 |
| 맡는 일 | 모터 속도 루프, 엔코더 계수, 센서 읽기, 안전 정지 | 인식, SLAM, 경로 계획, ROS 2, 기록, 통신 |

### 무엇을 어디에서 돌리는가

경계를 긋는 질문은 하나다. **"이 일이 매번, 정해진 시간 안에 일어나지 않으면 어떻게 되는가?"**

- 엔코더 펄스 하나를 놓치면 오도메트리가 영원히 틀린다. 1 kHz 속도 루프가 한 번에 20 ms 늦으면
  모터가 덜컥거린다. 통신이 끊겼는데 모터가 마지막 명령대로 계속 돌면 로봇이 벽을 들이받는다.
  이런 일은 **MCU** 에서 한다. 시간 제약을 어기면 실패인 일을 경성(hard) 실시간이라고 한다.
- 지도 갱신이 50 ms 늦어도 로봇은 조금 덜 정확할 뿐이다. 이런 연성(soft) 실시간 일과 연산이
  무거운 일은 **SBC** 에서 한다.

일반 Linux 는 프로세스를 언제 실행할지 보장하지 않는다. SBC 의 Python 루프에서 `sleep(0.001)` 로
1 kHz 제어를 하면 평균은 맞아도 가끔 수십 ms 씩 밀린다. 실시간 커널로 줄일 수는 있지만, 핀을 직접
다루는 일은 MCU 에 두는 것이 단순하고 안전하다. MCU 안에서 여러 일을 우선순위로 나눠 돌릴 때는
RTOS(FreeRTOS, Zephyr 등)를 쓴다.

### 통신 버스

| 버스 | 전선 | 연결 | 속도(대략) | 거리 | 로봇에서의 쓰임 |
|---|---|---|---|---|---|
| UART | TX, RX (+GND) | 1:1 | 9.6 k~1 M bps | 수 m | MCU ↔ SBC, GPS, 시리얼 서보 |
| I2C | SDA, SCL (+풀업 저항) | 여러 장치, 주소로 구분 | 100 k / 400 k bps | 보드 안(수십 cm) | IMU, 거리 센서, 소형 디스플레이 |
| SPI | SCK, MOSI, MISO, 장치마다 CS | 여러 장치, CS 선으로 구분 | 수 M bps | 보드 안 | 고속 IMU, 자기식 엔코더, 플래시 |
| CAN | CAN-H, CAN-L (차동, 양 끝 120 Ω) | 여러 노드, 메시지 ID 로 우선순위 | 최대 1 M bps | 수십 m | 관절 드라이버, 배터리 관리, 차량 |

고르는 기준은 이렇다. 보드 안의 센서 몇 개는 I2C(선이 적다), 빠르게 읽어야 하면 SPI. 서로 다른 보드
둘을 잇는 것은 UART(USB 시리얼 포함). 모터 전류가 흐르는 환경에서 여러 장치를 긴 선으로 묶을 때는
잡음에 강한 CAN. 보드 컴퓨터와 카메라·LiDAR 는 USB 나 이더넷이다.

조심할 것 둘. UART 는 양쪽이 같은 속도(baud)를 미리 정해야 하고, 한 바이트에 시작·정지 비트가 붙어
10비트가 든다. 그리고 3.3 V 장치와 5 V 장치를 그대로 이으면 3.3 V 쪽이 망가질 수 있다(레벨 변환기를 쓴다).

### 시리얼 프로토콜

UART 는 바이트를 보낼 뿐 "어디서부터 어디까지가 한 메시지인가"는 알려 주지 않는다. 바이트가 빠지거나
잡음으로 바뀔 수도 있다. 그래서 메시지를 **프레임**으로 싼다.

- **헤더:** 프레임의 시작을 알리는 정해진 바이트. 중간부터 읽기 시작해도 다시 맞출 수 있다.
- **길이와 본문:** 본문이 몇 바이트인지, 그리고 본문.
- **체크섬(또는 CRC):** 본문이 깨졌는지 확인한다. 깨진 프레임은 쓰지 않고 버린다.

받는 쪽에는 **워치독**(타임아웃)을 둔다. 일정 시간 올바른 명령이 오지 않으면 모터를 멈춘다. 케이블이
빠지거나 보드 컴퓨터의 프로그램이 죽었을 때 로봇이 마지막 명령으로 계속 달리는 것을 막는 유일한 장치다.

### micro-ROS 한 쪽 정리

micro-ROS 는 MCU 를 ROS 2 그래프의 노드로 만든다. MCU 에서는 작은 클라이언트 라이브러리(`rclc`)가 돌고,
보드 컴퓨터에서는 **micro-ROS Agent** 가 시리얼이나 UDP 로 MCU 와 이야기하며 그것을 DDS 쪽에 대신
내보낸다. 그 결과 MCU 가 발행한 `/wheel_ticks` 를 `ros2 topic echo` 로 볼 수 있다.

- 얻는 것: 프레임·직렬화·메시지 정의를 직접 만들지 않아도 된다. ROS 2 도구를 그대로 쓴다.
- 대가: RTOS 를 돌릴 만한 MCU(RAM 수십 KB 이상)가 필요하고, 빌드 환경이 무거우며, Agent 가 죽으면
  통신이 끊긴다. 워치독은 여전히 직접 넣어야 한다.
- 대안: 이 레슨의 프레임 같은 단순한 시리얼 프로토콜을 직접 정하고, 보드 컴퓨터 쪽에서
  `ros2_control` 하드웨어 인터페이스나 작은 브리지 노드가 그것을 토픽으로 바꾼다. 작은 로봇에서는
  이쪽이 디버깅하기 쉽다.

## 핵심 수식

- UART 전송량: 초당 바이트 = baud / 10 (8N1), 초당 프레임 = baud / (10 × 프레임 바이트)
- 워치독 정지 거리: $d = v \times t_{timeout}$
- 체크섬: 본문 바이트 합의 보수 — 한 비트 오류는 모두 잡지만, 합이 같아지는 두 군데 오류는 놓친다

## 예제

바퀴 속도 명령을 프레임으로 싸고, 쓰레기 바이트와 깨진 프레임이 섞인 스트림에서 온전한 것만 골라낸다.

```python
import struct

HEADER = b"\xaa\x55"


def checksum(data: bytes) -> int:
    return (~sum(data)) & 0xFF


def pack(left: float, right: float, seq: int) -> bytes:
    """바퀴 속도 명령 한 개를 프레임으로: 헤더 2 + 길이 1 + 본문 9 + 체크섬 1 = 13 바이트."""
    body = struct.pack("<Bff", seq & 0xFF, left, right)
    return HEADER + bytes([len(body)]) + body + bytes([checksum(body)])


def parse(stream: bytes):
    """바이트 스트림에서 온전한 프레임만 골라낸다. 깨진 프레임은 버리고 다음 헤더를 찾는다."""
    out, i = [], 0
    while i + 3 <= len(stream):
        if stream[i : i + 2] != HEADER:
            i += 1
            continue
        n = stream[i + 2]
        frame_end = i + 3 + n + 1
        if frame_end > len(stream):
            break  # 아직 다 오지 않았다
        body = stream[i + 3 : i + 3 + n]
        if n == 9 and checksum(body) == stream[frame_end - 1]:
            out.append(struct.unpack("<Bff", body))
            i = frame_end
        else:
            i += 1  # 헤더처럼 보였지만 아니었다
    return out


frames = [pack(1.0 + k, -1.0 - k, k) for k in range(4)]
stream = bytearray(b"\x00\x13" + b"".join(frames))  # 앞에 쓰레기 2바이트
stream[2 + 13 + 7] ^= 0x40  # 두 번째 프레임의 한 비트가 뒤집혔다
print([f[0] for f in parse(bytes(stream))])  # [0, 2, 3]: 깨진 1번만 빠진다

baud, frame_bytes = 115200, len(frames[0])
print(
    f"프레임 {frame_bytes} 바이트, {baud} bps 에서 초당 최대 {baud / 10 / frame_bytes:.0f} 개"
)  # 13, 886
```

스트림 맨 앞의 쓰레기 2바이트는 헤더가 아니라서 건너뛰고, 한 비트가 뒤집힌 1번 프레임은 체크섬이 맞지
않아 버려진다. 뒤따르는 2번, 3번은 다시 헤더를 찾아 정상적으로 읽힌다.

**연습 과제(exercise):** (1) 이 13바이트 프레임을 9600, 115200, 1 000 000 bps 에서 초당 최대 몇 개
보낼 수 있는가? 100 Hz 로 명령을 보내고 같은 크기의 상태를 돌려받으려면 어느 속도가 필요한가?
(2) 체크섬이 잡지 못하는 오류를 만들어 보라(힌트: 본문의 한 바이트에 0x40 을 더하고 다른 바이트에서
0x40 을 뺀다). 무엇으로 바꿔야 하는가? (3) 워치독 타임아웃이 0.2 초이고 로봇이 0.5 m/s 로 달린다.
케이블이 빠진 뒤 로봇은 멈추기 전까지 얼마나 더 가는가? 타임아웃을 0.02 초로 줄이면 생기는 문제는?

```expected
1. 한 바이트에 10비트가 들므로 초당 프레임 수는 baud / 130 이다.

   | 속도 | 초당 최대 프레임 |
   | --- | --- |
   | 9600 bps | 약 74 |
   | 115200 bps | 약 886 |
   | 1 000 000 bps | 약 7692 |

   100 Hz 왕복은 방향마다 $100 \times 13 \times 10 = 13\,000$ bps 가 필요하다. 9600 bps 로는 불가능하고
   115200 bps 면 용량의 약 11% 만 쓴다.
2. 본문의 한 바이트에 0x40 을 더하고 다른 바이트에서 0x40 을 빼면 바이트 합이 그대로라 체크섬이 같다.
   `parse` 는 이 프레임을 정상으로 받아들이고, 바퀴 속도는 엉뚱한 값이 된다. 단순 합 체크섬은 한 비트
   오류는 모두 잡지만 이렇게 서로 상쇄되는 오류, 바이트 순서가 바뀐 오류는 놓친다. CRC(CRC-8,
   CRC-16)로 바꾸면 이런 경우를 거의 다 잡는다. 받은 값이 물리적으로 가능한 범위인지 한 번 더
   확인하는 것도 값싼 방어다.
3. $0.5 \times 0.2 = 0.1$ m 를 더 간다(감속 거리는 별도). 타임아웃을 0.02 초로 줄이면 정지 거리는
   1 cm 로 줄지만, 100 Hz(10 ms 주기)로 오는 명령이 한두 개만 늦거나 깨져도 로봇이 멈칫거린다. 보드
   컴퓨터의 Linux 는 가끔 수십 ms 씩 밀리므로 타임아웃은 명령 주기의 몇 배(여기서는 50–200 ms)로 잡는다.
```

## 자가 점검 질문

1. 모터 속도 루프를 보드 컴퓨터의 Python 프로그램이 아니라 마이크로컨트롤러에서 돌리는 이유는 무엇인가?
2. IMU 하나와 거리 센서 둘을 MCU 에 붙이려 한다. I2C 를 고를 때 확인해야 할 것은 무엇인가?
3. micro-ROS 를 쓰더라도 MCU 에 워치독이 필요한 이유는 무엇인가?

## 확인 퀴즈

`rc quiz m11-microcontrollers-buses` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m11-microcontrollers-buses-quiz
questions:
  - id: q1
    type: single
    prompt: '다음 중 마이크로컨트롤러에 두어야 하는 일은?'
    choices:
      - '엔코더 카운트와 1 kHz 모터 속도 루프'
      - '카메라 영상에서 물체 검출'
      - 'SLAM 지도 작성'
      - '전역 경로 계획'
    answer: 0
    explanation: '엔코더 카운트를 놓치거나 속도 루프가 가끔 수십 ms 밀리면 바로 문제가 된다. 매번 정해진 시간 안에 일어나야 하는 일은 타이머 인터럽트로 일정하게 도는 MCU 에 둔다. 나머지 셋은 연산이 무겁고 조금 늦어도 되는 일이라 보드 컴퓨터가 맞다.'
    concept: { front: 'MCU 와 SBC 의 역할 분담 기준', back: '매번 정해진 시간 안에 일어나야 하는 일(엔코더, 속도 루프, 안전 정지)은 MCU, 무겁고 조금 늦어도 되는 일은 SBC' }
  - id: q2
    type: single
    prompt: '모터 전류가 흐르는 로봇 팔에서 관절 드라이버 여섯 개를 긴 케이블로 묶으려 한다. 가장 알맞은 버스는?'
    choices:
      - 'I2C'
      - 'SPI'
      - 'CAN'
      - '장치마다 따로 UART'
    answer: 2
    explanation: 'CAN 은 차동 신호라 잡음에 강하고, 두 가닥 선에 여러 노드를 달 수 있으며, 수십 m 거리에서도 동작한다. I2C 와 SPI 는 보드 안의 짧은 거리용이고, UART 는 1:1 이라 장치마다 선이 따로 필요하다.'
    concept: { front: 'CAN 을 쓰는 경우', back: '잡음 많은 환경에서 여러 장치를 긴 선으로 묶을 때 — 차동 신호, 다중 노드, 메시지 ID 우선순위' }
  - id: q3
    type: truefalse
    prompt: '통신 프레임에 체크섬이 있으면 수신 쪽 워치독(타임아웃)은 없어도 된다.'
    answer: false
    explanation: '체크섬은 깨진 프레임을 버리게 해 줄 뿐, 프레임이 아예 오지 않는 상황(케이블 빠짐, 프로그램 정지)은 알려 주지 않는다. 일정 시간 올바른 명령이 없으면 모터를 멈추는 워치독이 따로 있어야 한다.'
    concept: { front: '체크섬과 워치독의 역할', back: '체크섬 = 깨진 데이터를 버림, 워치독 = 데이터가 안 올 때 멈춤. 둘 다 필요' }
```

## 이 단계 공부법

1. **본문(먼저):** 지금까지 배운 기능(엔코더 계수, 속도 루프, 경로 추종, 센서 필터, 물체 검출)을
   적고 각각 MCU 와 SBC 중 어디에 둘지, 그 사이를 오가는 데이터가 무엇인지 그린다.
2. **예제:** 코드를 실행하고, 스트림의 다른 위치(헤더, 길이 바이트)를 깨뜨려 `parse` 가 어떻게
   다시 맞추는지 본다.
3. **연습:** 세 문항을 계산한다. (2)는 실제로 바이트를 바꿔 `parse` 가 받아들이는 것을 확인한다.
4. **확인:** micro-ROS 문서의 Overview 를 읽고, 이 레슨의 직접 만든 프로토콜과 비교해 무엇을 대신
   해 주는지 세 가지를 적는다.

## 참고 자료

- micro-ROS — <https://micro.ros.org/>
- ros2_control documentation — <https://control.ros.org/>
- Arduino documentation, Learn — <https://docs.arduino.cc/learn/>
