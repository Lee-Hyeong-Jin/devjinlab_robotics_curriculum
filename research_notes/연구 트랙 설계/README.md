# 연구 트랙 설계 (Robotics Researcher Track — design notes)

로보틱스 **연구원(researcher)** 을 목표로 하는 specialization 급 전문 과정의 설계 자료다.
기존 `curriculum/robotics-expert`(10모듈 50레슨)은 로보틱스 **엔지니어** 입문~중급 과정이고,
이 설계는 그 위에 세우는 별도 코스(`curriculum/robotics-research`)의 청사진이다.

## 읽는 순서

| 파일 | 내용 | 먼저 읽을 사람 |
|---|---|---|
| [benchmark.md](benchmark.md) | 세계 최상위 대학원 과목의 **확인된** 강의계획·과제·교재, 박사 자격요건, 교재 정전 | 설계 근거를 확인하려는 사람 |
| [blueprint.md](blueprint.md) | 트랙·모듈·레슨 목록(97레슨), 레슨별 유도할 결과·필독 논문·재현 과제·열린 문제, 선수 DAG, 일정, 기존 50레슨 처분표 | **먼저 읽는다** |
| [lesson-standard.md](lesson-standard.md) | 레슨 1개를 어떻게 쓰는가: 고정 섹션 9개, 유도 깊이 등급, 문제 세트, 논문 읽기 질문, 재현 티어, 스키마 확장 제안 | 레슨을 쓰는 저자 세션 |
| [papers.yaml](papers.yaml) | 필독 논문 131편 레지스트리(레슨 참조용) | 레슨을 쓰는 저자 세션 |

## 설계의 핵심 주장 다섯 개

1. **연구원 수준은 "영역별 과목 + 연구 수행 능력"으로 정의된다.** CMU RI 의 Core Course
   Qualifier 4영역(Perception / Cognition / Action / Math Foundations)과 MIT EECS TQE
   Group 3·4 가 그 증거다. 공개된 "리딩리스트 시험"은 조사에서 확인되지 않았다
   (benchmark.md §7).
2. **수학 기초가 독립 모듈이어야 한다.** CMU 는 Math Foundations 영역에 과목을 하나만 두었고
   (16-811), 전제 배경으로 수치해석·미분기하를 요구한다. 기존 M1 은 이 수준이 아니다.
3. **과제는 구현 + 학회 포맷 보고서다.** 16-745(ICRA/IROS 6페이지), CS287(6페이지),
   MEAM 620(conference-quality report), Georgia Tech 구술(2페이지 제안 + 발표)이 일관된 근거다.
4. **원 논문이 1차 자료다.** 조사한 대학원 과목의 다수가 필수 교재를 두지 않는다(16-745,
   16-782, 16-822, 6.4212, CS326). 레슨은 논문 읽기와 재현을 필수 요소로 갖는다.
5. **파운데이션 모델·생성형 정책은 선택 주제가 아니라 코어다.** AA274A 의 advanced topics,
   CS285 HW4(LLM RL), AA203 W10(world models), CS326 §9 가 이미 정규 과목에 넣고 있다.

## 확인 규칙 (이 폴더 전체에 적용)

- `확인` = 2026-11-12 조사에서 해당 URL 을 실제로 fetch 해 그 자료임을 확인했다.
- `(미확인)` = 검색 스니펫만 있거나 fetch 가 실패했다. 문서에 노출할 때 그대로 표기한다.
- papers.yaml 은 항목마다 `verified` 필드로 같은 구분을 유지한다.
- 한국어 자료는 이 설계의 기준이 아니다(사용자 지시 2026-11-12: 글로벌 연구원 기준).
  기존 조사 노트의 `korean_resources_ecosystem.md` 는 참고하지 않았다.

## 사용자 확인이 필요한 결정

blueprint.md §10 에 모아 두었다: specialization 트랙 수(현재 5개), R0 수학 브리지의 위치,
기존 50레슨에 "연구 트랙으로 이어짐" 링크를 넣을지, 97레슨의 작성 순서(코어 51레슨 우선 권장).
