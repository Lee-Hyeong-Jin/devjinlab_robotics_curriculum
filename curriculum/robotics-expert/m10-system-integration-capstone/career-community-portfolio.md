---
id: m10-career-community-portfolio
title: "포트폴리오·커뮤니티·대회와 커리어"
summary: 캡스톤을 남이 읽고 재현할 수 있는 포트폴리오로 정리하고, 오픈소스 기여·국내외 커뮤니티·학회·대회·채용 연계 과정으로 연결하는 방법을 2026년 국내 생태계 조사를 바탕으로 정리한다.
objectives:
  - 캡스톤 저장소를 README·데모 영상·결과 지표·재현 절차를 갖춘 포트폴리오로 정리할 수 있다.
  - 오픈소스 로보틱스 프로젝트에 이슈·문서·작은 PR 로 기여하는 단계를 설명할 수 있다.
  - 국내외 커뮤니티·대회·채용 연계 교육 중 자기 목표에 맞는 다음 단계를 근거를 들어 고를 수 있다.
prerequisites: [m10-capstone-project-guide]
difficulty: 3
estimated_minutes: 90
tags: [portfolio, career, community, open-source, competition, korea]
activities:
  - id: m10-career-community-portfolio-reading
    kind: reading
    title: 본문과 커뮤니티·대회 페이지 둘러보기
    estimated_minutes: 30
  - id: m10-career-community-portfolio-quiz
    kind: quiz
    title: 포트폴리오 구성 요소 퀴즈
    estimated_minutes: 10
  - id: m10-career-community-portfolio-exercise
    kind: exercise
    title: 캡스톤 저장소 포트폴리오화와 다음 6개월 계획
    estimated_minutes: 50
resources:
  - title: ROS Discourse — Korea Users Group
    url: https://discourse.openrobotics.org/c/local/korea/33
    kind: other
    note: 2025-04 이후 활동이 거의 없다. 과거 세미나 자료(표윤석) 열람용, 질문은 본 포럼 영문 카테고리가 낫다.
  - title: "ROSCon Korea 2026 (Korea Times 보도)"
    url: https://www.koreatimes.co.kr/amp/southkorea/20260129/kwangwoon-university-hosts-robot-developer-conference
    kind: article
    note: 2026-01-21~22 판교, 광운대 주최·PinkLAB·XYZ 공동 주최. 국내 첫 ROSCon.
  - title: RoboCup South Korea Open 2026
    url: https://www.robocup.org/events/78
    kind: other
    note: 2026-02-06~08 평창. RoboCup 2026 인천(06-30~07-06)은 https://robocup.org/events/80
  - title: 2026 로보틱스 작품공모전 (과기정통부)
    url: https://eopla.net/magazines/48000
    kind: other
    note: 접수 2026-10-08~11-02, 프로젝트 제출형. 캡스톤을 그대로 낼 수 있는 형식.
  - title: F1TENTH 공개 강의 저장소 (mlab-upenn)
    url: https://www.github.com/mlab-upenn/f1tenthpublic
    kind: other
    note: 자율주행 레이싱 랩·슬라이드(차량 약 $2,100~3,000). 대학 연구실 연계 시 다음 단계.
---

# 포트폴리오·커뮤니티·대회와 커리어

로보틱스 채용 담당자와 연구실은 "무엇을 공부했는가"보다 **"무엇을 만들었고, 어떻게 검증했는가"**를 본다.
캡스톤을 끝냈다면 이미 그 증거를 가지고 있다. 이 레슨은 그 증거를 읽히는 형태로 바꾸고, 혼자 공부하던
흐름을 커뮤니티·대회·직무로 잇는 마지막 단계다.

## 개념

### 포트폴리오: 30초, 5분, 30분

읽는 사람은 세 층으로 본다. **30초**: README 맨 위의 한 줄 요약과 데모 GIF/영상. **5분**: 아키텍처 그림,
요구사항 대비 결과 지표 표, 설계 결정과 그 이유. **30분**: Docker 로 재현하고 코드·테스트를 읽는다.
L10.1–L10.5 의 산출물(추적표, BOM, FMEA, CI, 루브릭 결과)이 그대로 이 세 층을 채운다. 실패 사례와
한계를 적는 것은 감점이 아니라 엔지니어링 판단력의 증거다.

### 오픈소스 기여

캡스톤에서 쓴 패키지(Nav2, ros2_control, LeRobot, 드라이버)에서 막혔던 지점이 첫 기여 후보다.
(1) 재현 절차가 있는 이슈 보고 → (2) 문서·예제 수정 PR → (3) 작은 버그 수정 순으로 간다. Jazzy 와 Lyrical
사이 API 변경(예: ros2_control 의 제거된 API)처럼 마이그레이션 노트는 수요가 많은 기여다.

### 국내외 커뮤니티 (2026년 기준)

- 국내 ROS 커뮤니티는 분산되어 있다. ROS Discourse Korea 그룹은 2025-04 이후 사실상 휴면이고, 오로카의
  옛 도메인(oroca.org)은 다른 용도로 넘어갔다. 활동은 네이버 카페, 판교 오프라인 모임(2026-01 오로카 판교
  오픈랩 세미나), 모두의연구소·PyTorch KR 공지 채널로 흩어져 있다.
- 구심점은 **ROSCon Korea 2026**(판교, 광운대·PinkLAB·XYZ)으로 옮겨 가는 중이다.
- 영문 채널: ROS Discourse 본 포럼, LeRobot Discord, Pupper(Hands-On Robotics) Discord, HomeBrew Robotics Club 메일링 리스트.
- 학회: 국제적으로 ICRA·IROS·RSS·CoRL, 국내에서는 제어로봇시스템학회(ICROS)·한국로봇학회 학술대회가
  있다(일정·URL 은 조사 노트에서 확인하지 못했으니 각 학회 공지를 직접 확인한다). 학생·개인도 워크숍 포스터로
  참여할 수 있다.

### 대회

성인 소프트웨어 개발자가 접근하기 쉬운 것은 **RoboCup Korea Open**(2월), **로보틱스 작품공모전**(10–11월,
프로젝트 제출형), 대학 연구실과 연계한 **F1TENTH** 류 자율주행 레이싱이다. RoboCup 2026 은 인천에서 처음
열렸다. VEX·FIRST·WRO 는 주로 초·중·고 팀 대상이다.

### 채용과 연계 교육

2026년 국내 로봇 SW 채용 연계 경로의 큰 축은 고용노동부 KDT 국비 과정이다. 로보티즈·클로봇 Physical AI
로봇 SW 채용연계과정(980시간), 한화로보틱스 AI 로봇 테크 스쿨, 두산로보틱스 로키부트캠프 등이 ROS 2 →
SLAM/Nav2 → 모방학습 → 실로봇 캡스톤 순서로 수렴한다. 이 코스를 마쳤다면 그 커리큘럼의 대부분을 이미
다뤘으므로, 지원서에서 **캡스톤 결과 지표와 저장소 링크**로 차별화한다. 직무는 대략 내비게이션·인식·제어·
로봇 러닝·임베디드/시스템 통합으로 나뉘며, 캡스톤 브리프 A·B·C 가 각각 내비게이션/통합, 로봇 러닝,
상태 추정/인식 쪽 증거가 된다.

## 핵심 체크리스트

- [ ] README 첫 화면에 한 줄 요약, 데모 영상, 핵심 지표 표가 있다.
- [ ] 아키텍처 그림과 설계 결정 3개 이상(대안과 선택 이유)이 있다.
- [ ] `docker run` 한 줄 또는 5단계 이하로 재현할 수 있다.
- [ ] 라이선스, 사용한 오픈소스와 데이터 출처가 명시되어 있다.
- [ ] 한계와 다음 단계 절이 있다.

## 예제

캡스톤 저장소가 포트폴리오 최소 요건을 갖췄는지 검사한다.

```python
from pathlib import Path

REQUIRED = {
    "README.md": "30초 요약·데모·지표",
    "LICENSE": "라이선스",
    "Dockerfile": "재현 환경",
    "docs/architecture.png": "아키텍처 그림",
    "docs/results.md": "요구사항 대비 결과",
    ".github/workflows": "CI",
}
README_KEYWORDS = ["데모", "결과", "재현", "한계"]


def check_portfolio(repo: Path) -> list[str]:
    missing = [f"{p} ({why})" for p, why in REQUIRED.items() if not (repo / p).exists()]
    readme = repo / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        missing += [f"README 에 '{k}' 절 없음" for k in README_KEYWORDS if k not in text]
    return missing


problems = check_portfolio(Path("."))
print("포트폴리오 준비 완료" if not problems else "\n".join(f"- {p}" for p in problems))
```

**연습 과제(exercise):** (1) 검사기를 내 캡스톤 저장소에서 돌려 빈 항목을 채워라. (2) 사용한 오픈소스
하나에 재현 절차가 있는 이슈 또는 문서 PR 하나를 올려라. (3) 커뮤니티·대회·채용 중 하나를 골라
다음 6개월 계획(마감일 포함)을 쓴다.

## 자가 점검 질문

1. 데모 영상만 있고 지표 표가 없는 포트폴리오는 읽는 사람에게 어떤 의문을 남기는가?
2. 첫 오픈소스 기여로 큰 기능 PR 보다 재현 가능한 이슈 보고나 문서 수정이 나은 이유는?
3. 국내 ROS 커뮤니티가 분산된 상황에서 질문·교류 채널을 어떻게 조합하는 것이 효율적인가?

## 이 단계 공부법

1. **정리(먼저):** 캡스톤 저장소를 예제 검사기로 점검하고 README 첫 화면부터 고친다.
2. **둘러보기:** ROSCon Korea 보도, RoboCup·작품공모전 페이지를 읽고 다음 마감일을 달력에 적는다.
3. **기여:** 캡스톤 중 막혔던 문서 한 곳을 골라 이슈나 PR 로 남긴다.
4. **확장(선택):** F1TENTH 공개 저장소의 랩을 훑어 다음 프로젝트 후보로 삼는다.

## 참고 자료

- ROS Discourse, Korea Users Group — <https://discourse.openrobotics.org/c/local/korea/33>
- Korea Times, ROSCon Korea 2026 보도(2026-01-29) — <https://www.koreatimes.co.kr/amp/southkorea/20260129/kwangwoon-university-hosts-robot-developer-conference>
- RoboCup South Korea Open 2026 — <https://www.robocup.org/events/78>
- 과학기술정보통신부, 2026 로보틱스 작품공모전 — <https://eopla.net/magazines/48000>
- mlab-upenn, F1TENTH 공개 강의 저장소 — <https://www.github.com/mlab-upenn/f1tenthpublic>
