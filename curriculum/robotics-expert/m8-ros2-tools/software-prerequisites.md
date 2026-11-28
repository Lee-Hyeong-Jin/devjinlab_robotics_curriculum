---
id: m8-software-prerequisites
title: ROS 2 전에 점검할 소프트웨어 기초
summary: ROS 2 실습에서 막히는 곳은 로보틱스보다 셸·Git·C++ 빌드·Python 패키징·네트워크인 경우가 많다. 다섯 영역을 어느 수준까지 알아야 하는지 자가 점검 질문으로 확인하고, 모자란 부분을 배울 무료 자료로 연결한다.
objectives:
  - "`source` 와 스크립트 실행의 차이를 설명하고, 지금 셸이 어떤 환경 변수와 워크스페이스를 보고 있는지 확인할 수 있다."
  - CMake 설정 오류와 컴파일·링크 오류의 첫 줄을 읽고 빠진 것이 패키지인지, 헤더인지, 링크 설정인지 구분할 수 있다.
  - 두 컨테이너나 두 컴퓨터의 ROS 2 노드가 서로 보이지 않을 때 확인할 네트워크 항목을 순서대로 말할 수 있다.
prerequisites: [m8-ros2-concepts-distros]
difficulty: 1
estimated_minutes: 60
tags: [ros2, linux, shell, git, cmake, python-packaging, networking, prerequisites]
activities:
  - id: m8-software-prerequisites-reading
    kind: reading
    title: 점검표 읽고 모자란 영역 고르기
    estimated_minutes: 25
  - id: m8-software-prerequisites-quiz
    kind: quiz
    title: 셸·빌드·네트워크 증상 읽기 퀴즈
    estimated_minutes: 10
  - id: m8-software-prerequisites-exercise
    kind: exercise
    title: 터미널에서 하는 5분 자가 점검
    estimated_minutes: 25
resources:
  - title: The Missing Semester of Your CS Education (MIT)
    url: https://missing.csail.mit.edu/
    kind: course
    note: 셸, 셸 스크립트, 명령줄 환경, Git 강의. 영상과 노트가 무료다. 한국어 번역 노트가 있다.
  - title: Pro Git (Scott Chacon, Ben Straub)
    url: https://git-scm.com/book/ko/v2
    kind: book
    note: 1–3장(시작하기, 기초, 브랜치)이면 충분하다. 한국어판 무료.
  - title: CMake Tutorial
    url: https://cmake.org/cmake/help/latest/guide/tutorial/index.html
    kind: article
    note: Step 1–2 로 실행 파일과 라이브러리를 만드는 CMakeLists.txt 를 읽을 수 있게 된다.
  - title: ament_cmake user documentation (ROS 2 Jazzy)
    url: https://docs.ros.org/en/jazzy/How-To-Guides/Ament-CMake-Documentation.html
    kind: article
    note: ROS 2 패키지의 CMakeLists.txt 가 일반 CMake 와 다른 부분(find_package, ament_target_dependencies, install).
  - title: Python Packaging User Guide
    url: https://packaging.python.org/en/latest/tutorials/installing-packages/
    kind: article
    note: pip, 가상 환경, 패키지 설치 위치. ROS 2 의 ament_python 패키지를 읽기 전에 본다.
  - title: About domain ID (ROS 2 Jazzy)
    url: https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Domain-ID.html
    kind: article
    note: ROS_DOMAIN_ID 와 DDS 가 쓰는 UDP 포트. 노드가 서로 보이지 않을 때의 배경 지식.
  - title: Docker networking overview
    url: https://docs.docker.com/engine/network/
    kind: article
    note: 컨테이너가 기본으로 놓이는 bridge 네트워크와 host 네트워크의 차이.
---

# ROS 2 전에 점검할 소프트웨어 기초

ROS 2 자습서를 따라 하다 포기하는 사람의 대부분은 로보틱스에서 막히지 않는다. `ros2: command not
found`, 뜻 모를 CMake 오류, 옆 컴퓨터의 노드가 보이지 않는 문제에서 막힌다. ROS 2 는 Linux 셸, 빌드
시스템, 네트워크 위에 얹혀 있고, 자습서는 독자가 그것들을 안다고 가정한다. 이 레슨은 새 내용을
가르치지 않는다. **무엇을 어느 수준까지 알아야 하는지** 정하고, 모자란 부분을 배울 곳을 가리킨다.
다섯 영역을 전부 알 필요는 없다. 자가 점검 질문에 답하지 못한 영역만 연결된 자료로 보충하고 오면 된다.

## 어디에 쓰는가

다음 레슨부터 워크스페이스를 만들고(`colcon build`), 환경을 소싱하고, 여러 터미널에서 노드를 띄운다.
실제 로봇에서는 보드 컴퓨터에 SSH 로 들어가고, 남의 패키지를 Git 으로 받아 빌드하고, 로봇과 노트북을
같은 네트워크에 올린다. 이 다섯 가지 기초가 없으면 ROS 2 의 모든 오류가 똑같이 크고 똑같이 알 수 없어
보인다. 기초가 있으면 "이건 소싱 문제", "이건 의존성 문제", "이건 네트워크 문제"로 나뉘어 보인다.

## 개념

### 1. 셸과 환경 변수

**필요한 수준:** 디렉터리 이동과 파일 조작(`cd`, `ls`, `cp`, `mv`, `rm`, `cat`, `grep`), 환경 변수
읽기(`echo $PATH`, `printenv`), `~/.bashrc` 가 언제 실행되는지, 그리고 `source` 가 하는 일.

`source setup.bash` 는 스크립트를 **지금 셸 안에서** 실행해 그 스크립트가 바꾼 환경 변수가 남는다.
`bash setup.bash` 는 새 셸을 띄워 실행하고 끝나면 그 셸과 함께 변경이 사라진다. ROS 2 의 "소싱"은
`PATH`, `AMENT_PREFIX_PATH`, `PYTHONPATH` 같은 변수에 설치 경로를 더하는 일이므로 터미널마다 해야 한다.

- 자가 점검: 새 터미널에서 `ros2` 명령이 없다고 나온다. 어제는 됐다. 무엇을 확인하겠는가?
- 배울 곳: The Missing Semester 의 "Course overview + the shell", "Shell Tools and Scripting".

### 2. Git

**필요한 수준:** `clone`, `status`, `add`, `commit`, `log`, `diff`, 브랜치 만들고 바꾸기, 태그나
브랜치를 지정해 받기(`git clone -b jazzy <url>`). ROS 2 저장소는 배포판마다 브랜치가 다른 경우가
많아, 브랜치를 틀리게 받으면 빌드가 깨진다.

- 자가 점검: 받은 패키지가 빌드되지 않는다. 내가 받은 브랜치가 내 배포판용인지 어떻게 확인하는가?
- 배울 곳: Pro Git 1–3장.

### 3. C++ 빌드와 CMake

**필요한 수준:** C++ 를 잘 짤 필요는 없다. 소스 → 컴파일 → 링크 순서를 알고, `CMakeLists.txt` 에서
`find_package`, `add_executable`, `target_link_libraries`(ROS 2 에서는 `ament_target_dependencies`),
`install` 이 각각 무엇을 하는지 읽을 수 있으면 된다. 그리고 **오류는 맨 위의 첫 오류부터** 읽는다.

| 오류가 난 단계 | 대표 문구 | 뜻 |
|---|---|---|
| 설정(CMake) | `Could not find a package configuration file provided by "foo"` | 패키지 `foo` 가 설치되지 않았거나 소싱되지 않았다 |
| 컴파일 | `fatal error: foo/bar.hpp: No such file or directory` | 헤더를 못 찾는다. `find_package` 나 의존성 선언이 빠졌다 |
| 링크 | `undefined reference to 'foo::Bar::baz()'` | 선언은 있는데 구현 라이브러리를 링크하지 않았다 |

- 자가 점검: 위 세 문구를 보고 각각 `package.xml`·`CMakeLists.txt` 의 어디를 볼지 말할 수 있는가?
- 배울 곳: CMake Tutorial Step 1–2, 이어서 ament_cmake 문서.

### 4. Python 패키징

**필요한 수준:** `pip install` 이 패키지를 어디에 넣는지, 가상 환경(`python3 -m venv`)이 왜 있는지,
`import` 가 `sys.path` 에서 모듈을 찾는다는 것. ROS 2 의 Python 패키지(`ament_python`)는
`setup.py` 의 `entry_points` 에 적은 이름이 `ros2 run <패키지> <이름>` 의 실행 이름이 된다.

Ubuntu 24.04 에서는 시스템 Python 에 `pip install` 을 하면 `externally-managed-environment` 오류가
난다. 시스템 패키지를 보호하기 위한 동작이다. ROS 2 의존성은 `rosdep` 과 `apt` 로, 그 밖의 실험용
패키지는 가상 환경으로 넣는다.

- 자가 점검: `ModuleNotFoundError` 가 났다. 모듈이 설치되지 않은 것인지, 설치는 됐는데 지금
  Python 이 못 보는 것인지 어떻게 구분하는가?
- 배울 곳: Python Packaging User Guide 의 "Installing Packages".

### 5. 네트워크

**필요한 수준:** IP 주소와 서브넷, 네트워크 인터페이스(`ip -brief addr` 로 본 `lo`, `eth0`,
`wlan0`, `docker0`), `ping`, 그리고 유니캐스트와 **멀티캐스트**의 차이. ROS 2 의 노드는 중앙 서버
없이 멀티캐스트로 "나 여기 있다"를 알려 서로를 찾는다. 그래서 두 노드가 같은 서브넷에 있고, 그
사이의 공유기·방화벽·가상 네트워크가 멀티캐스트를 막지 않아야 한다.

두 컨테이너가 서로를 못 보는 이유도 여기서 나온다. 컨테이너는 기본적으로 Docker 가 만든 가상
네트워크(bridge) 안에 있어, 다른 Compose 프로젝트의 컨테이너나 호스트, 옆 컴퓨터와는 다른 네트워크다.

- 자가 점검: 노트북과 로봇이 같은 와이파이에 있는데 `ros2 node list` 에 로봇의 노드가 없다. 확인할
  것 세 가지를 순서대로 말하라.
- 배울 곳: About domain ID 문서와 Docker networking overview. 해결 순서는 L8.5 의 "막혔을 때"에 있다.

```hint
노트북과 로봇의 노드가 서로 보이지 않는다
1. `ping <상대 IP>` 가 되는가. 안 되면 ROS 문제가 아니라 네트워크 문제다.
2. 양쪽 `ROS_DOMAIN_ID` 가 같은가(`echo $ROS_DOMAIN_ID`, 비어 있으면 0).
3. `ros2 multicast receive` 를 한쪽에서, `ros2 multicast send` 를 다른 쪽에서 실행해 멀티캐스트가
   통하는지 본다. 학교·회사 와이파이는 기기 간 통신이나 멀티캐스트를 막는 경우가 많다. 그럴 때는
   휴대용 공유기를 따로 쓰는 것이 가장 빠르다.
```

## 예제

CMake 가 패키지를 못 찾을 때의 오류다. 길지만 읽을 곳은 두 군데다.

```text
CMake Error at CMakeLists.txt:3 (find_package):
  ...
  Could not find a package configuration file provided by
  "sensor_driver_that_is_not_installed" with any of the following names:

    sensor_driver_that_is_not_installedConfig.cmake
    sensor_driver_that_is_not_installed-config.cmake

  Add the installation prefix of "sensor_driver_that_is_not_installed" to
  CMAKE_PREFIX_PATH or set "sensor_driver_that_is_not_installed_DIR" ...
```

첫 줄은 **어디서**(`CMakeLists.txt` 3행의 `find_package`), 가운데는 **무엇을**(그 이름의 패키지)
못 찾았는지 말한다. ROS 2 에서 이 오류의 원인은 대개 둘 중 하나다. 패키지가 설치되지 않았거나
(`rosdep install --from-paths src -y --ignore-src`), 설치는 됐는데 그 워크스페이스를 소싱하지 않았다.

**연습 과제(exercise):** Linux 나 macOS 터미널(또는 L8.5 의 컨테이너)에서 아래를 한 줄씩 실행하고,
실행하기 전에 출력을 예측해 적어라. (1)–(3)이 서로 다른 이유를 한 문장으로 설명하라.

```bash
bash -c 'export RC_DEMO=1'; echo "${RC_DEMO:-unset}"     # (1)
echo 'export RC_DEMO=1' > demo.sh
bash demo.sh; echo "${RC_DEMO:-unset}"                   # (2)
source demo.sh; echo "${RC_DEMO:-unset}"                 # (3)
python3 -c "import sys; print(sys.prefix == sys.base_prefix)"   # (4)
ip -brief addr                                           # (5) macOS 는 ifconfig
```

```expected
| 줄 | 출력 | 이유 |
| --- | --- | --- |
| (1) | `unset` | `bash -c` 는 자식 셸이다. 거기서 한 `export` 는 자식과 함께 사라진다 |
| (2) | `unset` | `bash demo.sh` 도 자식 셸에서 실행한다 |
| (3) | `1` | `source` 는 지금 셸에서 실행하므로 변수가 남는다 |
| (4) | `True` | 가상 환경 밖이다. 가상 환경을 켠 터미널에서는 `False` 가 나온다 |
| (5) | 인터페이스 목록 | `lo`(127.0.0.1)와 유선·무선 인터페이스 하나 이상. Docker 가 있으면 `docker0` 와 `br-…` 도 보인다 |

(1)–(3)의 차이가 "터미널마다 `source /opt/ros/jazzy/setup.bash` 를 해야 하는 이유"다. 설정
스크립트를 `bash` 로 실행하면 아무 일도 일어나지 않은 것처럼 보인다. (5)에서 `docker0` 나 `br-…`
가 보인다면 컨테이너가 호스트와 다른 네트워크에 있다는 것을 눈으로 확인한 것이다.
```

## 자가 점검 질문

1. `source install/setup.bash` 와 `bash install/setup.bash` 의 결과가 다른 이유는 무엇인가?
2. `undefined reference to` 오류는 빌드의 어느 단계에서 나며, CMakeLists.txt 의 어디를 봐야 하는가?
3. 같은 PC 의 두 컨테이너에서 띄운 노드가 서로 보이지 않을 때 가장 먼저 확인할 것은 무엇인가?

## 확인 퀴즈

`rc quiz m8-software-prerequisites` 로 풀 수 있다. 오답은 복습 카드가 된다.

```quiz
activity: m8-software-prerequisites-quiz
questions:
  - id: q1
    type: single
    prompt: '`bash /opt/ros/jazzy/setup.bash` 를 실행한 뒤에도 `ros2` 명령이 없다고 나온다. 이유는?'
    choices:
      - '스크립트가 자식 셸에서 실행되어, 바뀐 환경 변수가 지금 셸에 남지 않았다'
      - 'ROS 2 가 설치되지 않았다'
      - '`ROS_DOMAIN_ID` 가 설정되지 않았다'
      - '관리자 권한으로 실행하지 않았다'
    answer: 0
    explanation: '`bash 파일` 은 새 셸을 띄워 실행하고 끝나면 그 셸의 환경이 사라진다. 환경 변수를 지금 셸에 남기려면 `source 파일`(또는 `. 파일`)을 써야 한다. 오류 없이 끝나기 때문에 더 헷갈린다.'
    concept: { front: '`source` 와 `bash` 실행의 차이', back: '`source` 는 지금 셸에서 실행해 환경 변수가 남고, `bash 파일` 은 자식 셸에서 실행해 사라진다' }
  - id: q2
    type: single
    prompt: '`colcon build` 가 `Could not find a package configuration file provided by "nav2_msgs"` 로 멈췄다. 먼저 할 일은?'
    choices:
      - 'C++ 소스의 `#include` 줄을 고친다'
      - '`rosdep install` 로 의존 패키지를 설치하고, 필요한 워크스페이스를 소싱했는지 확인한다'
      - '`target_link_libraries` 에 라이브러리를 더한다'
      - '컴퓨터를 다시 시작한다'
    answer: 1
    explanation: '이 문구는 컴파일 전, CMake 설정 단계에서 `find_package` 가 패키지를 찾지 못했다는 뜻이다. 패키지가 설치되지 않았거나 설치된 경로가 소싱되지 않은 것이므로 소스 코드나 링크 설정을 볼 단계가 아니다.'
    concept: { front: 'CMake `Could not find a package configuration file` 의 뜻', back: '설정 단계에서 패키지를 못 찾음 — 설치(`rosdep install`)와 소싱을 확인한다' }
  - id: q3
    type: truefalse
    prompt: '같은 PC 에서 서로 다른 Compose 프로젝트로 띄운 두 컨테이너는 별도 설정 없이도 ROS 2 노드를 서로 발견한다.'
    answer: false
    explanation: '각 Compose 프로젝트는 자기만의 가상 네트워크를 만든다. DDS 의 멀티캐스트 발견은 같은 네트워크 안에서만 닿으므로 두 컨테이너는 서로를 찾지 못한다. 같은 네트워크에 넣거나(같은 Compose 파일), Linux 에서는 host 네트워크를 쓴다.'
    concept: { front: '컨테이너끼리 ROS 2 노드가 안 보이는 이유', back: '서로 다른 가상 네트워크라 멀티캐스트 발견이 닿지 않는다 — 같은 네트워크에 두거나 host 네트워크' }
```

## 이 단계 공부법

1. **점검(먼저):** 다섯 영역의 자가 점검 질문에 소리 내어 답해 본다. 막힌 영역에만 표시한다.
2. **보충:** 표시한 영역의 자료를 적힌 범위만 본다. 전부 보려 하지 않는다. 영역마다 1–2시간이면 된다.
3. **연습:** 연습 과제를 예측 → 실행 → 비교 순서로 한다.
4. **넘어가기:** 완벽해질 때까지 기다리지 않는다. 다음 레슨에서 실제로 막히면 그때 이 레슨으로
   돌아와 해당 영역을 다시 본다. 필요해진 순간에 배우는 것이 가장 잘 남는다.

## 참고 자료

- The Missing Semester of Your CS Education (MIT) — <https://missing.csail.mit.edu/>
- Pro Git 한국어판 — <https://git-scm.com/book/ko/v2>
- CMake Tutorial — <https://cmake.org/cmake/help/latest/guide/tutorial/index.html>
- ament_cmake user documentation — <https://docs.ros.org/en/jazzy/How-To-Guides/Ament-CMake-Documentation.html>
- Python Packaging User Guide — <https://packaging.python.org/en/latest/tutorials/installing-packages/>
- About domain ID — <https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Domain-ID.html>
- Docker networking overview — <https://docs.docker.com/engine/network/>
