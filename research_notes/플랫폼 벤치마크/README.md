# 유사 오픈소스 학습 플랫폼 벤치마크 (2026-11-11)

목적: "로보틱스 전문가 코스" 단일 코스(모듈 → 레슨, Markdown + 프런트매터, 진도 추적, 인증·API·웹·CI 예정, FSRS 복습 검토)를 오픈소스·엔터프라이즈 급으로 설계할 때 참고할 기존 플랫폼의 인증·권한, 콘텐츠 포맷, 라이선스, 설계 포인트 정리. 상세·출처는 각 노트 참조.

| 노트 | 범위 |
|---|---|
| open_edx_canvas.md | Open edX, Canvas LMS |
| moodle_oppia.md | Moodle, Oppia |
| anki_developer_platforms_standards.md | Anki·FSRS 생태계, freeCodeCamp·Exercism·The Odin Project·Jupyter Book/MyST, xAPI·cmi5·LTI 1.3·Open Badges 3.0 |

## 결론 5줄

1. 라이선스: 대형 LMS는 전부 카피레프트(Open edX·Canvas·Exercism AGPL-3.0, Moodle GPL-3.0, Anki AGPL-3.0-or-later)이고 Oppia·FSRS 라이브러리만 허용적(Apache-2.0, fsrs-rs BSD-3, py-fsrs/ts-fsrs MIT). 우리 코드 Apache-2.0 + 콘텐츠 CC BY 4.0 방침은 이들 코드를 복사하지 않고 "설계만 차용"할 때만 성립하며, FSRS 라이브러리는 그대로 의존성으로 써도 된다.
2. 콘텐츠 포맷: 성공한 개발자용 플랫폼(freeCodeCamp·Exercism·The Odin Project)은 모두 "Git 저장소의 Markdown + JSON/프런트매터 + 순서 파일"이며, LMS(OLX XML, .mbz, Common Cartridge)는 무겁다. 우리 방향(레슨 .md 프런트매터 + module.yaml)은 전자와 일치하고, 외부 호환은 LTI 1.3 출력과 xAPI 문장 내보내기 정도만 두면 충분하다.
3. 권한 모델: Moodle의 컨텍스트 트리(System→Category→Course→Module) + 능력 문자열(`plugin:capability`) + Inherit/Allow/Prevent/Prohibit 오버라이드, Canvas의 계정 트리 + 권한 사전(`enabled/locked/applies_to_descendants`)이 참고할 패턴이다. 단일 코스 플랫폼은 역할 4~5종(learner/author/reviewer/admin + 선택 mentor)을 리소스 범위(course/module/lesson)와 결합한 소형 RBAC로 충분하며, Open edX처럼 "LMS가 유일한 IdP, OAuth2 + JWT, 세션 인증 병행"을 따르면 된다.
4. 진도 모델: Open edX BlockCompletion(user, course, block, completion 0.0–1.0 유일 행), Canvas 모듈 완료 조건(must_view/must_submit/min_score/must_mark_done + 순차 잠금), The Odin Project lesson_completions(user, lesson, 레슨 uuid)가 수렴하는 형태는 "레슨당 1행 + 프런트매터에 완료 조건 enum"이다. Oppia의 skill mastery(float)와 story 선수 노드는 FSRS 복습을 레슨/개념 단위로 붙일 때의 모델이 된다.
5. 피할 것: XML 저작(OLX), 이중 저장소·다수 MFE 컨테이너(Open edX), Rails+RCE+잡 서버의 배포 무게(Canvas, 8 GB RAM+), 내장 SCORM 런타임, 공개 API 없는 폐쇄 내부 핸들러(Oppia), 만료·역할 없는 단일 hkey 인증(Anki sync). 표준은 xAPI 2.0(IEEE 9274.1.1-2023, lrsql Apache-2.0)과 Open Badges 3.0(VC 2.0, 2026-06 v1.4.5)만 선택적으로 채택한다.

## 플랫폼 요약표

| 플랫폼 | 코드 라이선스 | 인증 | 권한 모델 | 콘텐츠 포맷 | 진도 모델 | 배포 무게 |
|---|---|---|---|---|---|---|
| Open edX (Verawood 2026-07) | AGPL-3.0 + CLA(Axim) | LMS=IdP, OAuth2(DOT)+JWT, SAML/social 연동 | Staff/Admin/Data Researcher…, Verawood부터 openedx-authz RBAC 옵트인 | OLX XML tar.gz(course/chapter/sequential/vertical/XBlock), Markdown은 서드파티 XBlock | BlockCompletion 0.0–1.0, tracking log, Aspects(ClickHouse) | Tutor 최소 4 GB/2 CPU, 권장 8 GB/4 CPU |
| Canvas LMS (월간 릴리스) | AGPL-3.0 + CLA, "dual-licensed" | 12종 auth_type(SAML/CAS/LDAP/OIDC…), OAuth2 1h 토큰+refresh | 기본 역할 + 권한 사전(enabled/locked/applies_to_descendants), 계정 트리 | Pages HTML, Modules 완료 조건, Common Cartridge/QTI 입출력, LTI 1.3 Advantage | 모듈 완료 상태, Live Events(Caliper), Canvas Data 2 | Ruby 3.4+/Node 20/PG 14+/Redis, 8 GB RAM+ |
| Moodle 5.3 LTS (2026-10) | GPL-3.0, CLA 없음 | manual/OAuth2/OIDC/SAML2/LDAP/LTI | 컨텍스트 레벨(10/30/40/50/70/80) + 능력 + 오버라이드 | 코스/섹션/활동 모듈, .mbz(tgz+moodle_backup.xml), CC 1.1, SCORM 1.2, H5P, LTI Advantage | 활동·코스 완료 조건, logstore, 역량 프레임워크 | PHP ≥8.3, PG 17/MySQL 8.4, 1 GB RAM/5 GB |
| Oppia v3.5.x (2026-09) | Apache-2.0 + CLA 필수 | Firebase 세션 쿠키, 공개 API 없음 | 역할 상수 16종 + _ROLE_ACTIONS, 상속 없음 | classroom→topic→story→chapter→exploration(State 상태기계), YAML 내보내기 | StoryProgress, UserSkillMastery(float), checkpoint, LearnerGroup | python312 GAE + Datastore + Redis + Firebase |
| Anki 26.09 / FSRS | AGPL-3.0-or-later; fsrs-rs BSD-3, py-fsrs·ts-fsrs MIT | sync: user:pass → hkey, 만료·역할 없음 | 없음(단일 사용자) | SQLite notes/cards/revlog, .apkg(zstd) | revlog + cards.data FSRS 상태(s,d,…) | 단일 바이너리; FSRS-6 21파라미터, FSRS-7 ts-fsrs 기본 |
| freeCodeCamp | BSD-3(코드) | 이메일 코드 + Google/GitHub | 단순(user/admin) | challenges/<block>/<id>.md + structure JSON, 테스트 내장 | completedChallenges[{id, date, solution}] | Node + MongoDB |
| Exercism | AGPL-3.0 | 웹 세션/OAuth | 멘토·메인테이너 역할 | track config.json v3 + .docs/*.md + .meta/config.json, Docker 테스트 러너 | 연습문제 상태, 멘토링 | Rails + MySQL/Mongo/Redis |
| The Odin Project | MIT(앱), CC BY-NC-SA 4.0(커리큘럼) | Devise + GitHub/Google OmniAuth | 단순 | paths/courses/sections/lessons ← GitHub Markdown(kramdown), 필수 섹션 린트 | lesson_completions(user, lesson uuid), project_submissions | Rails 8.1 + PostgreSQL |
| Jupyter Book 2 / MyST | BSD-3 / MIT | 없음 | 없음 | MyST Markdown + 프런트매터(page/project 상속 규칙) | 없음 | 정적 사이트 |

## 차용할 설계 포인트

- 콘텐츠: 파일 트리 = 코스 트리(OLX 개념만), 레슨 Markdown 소스 + 정화된 HTML 출력, 순서는 module.yaml(freeCodeCamp structure JSON 역할), 레슨 필수 섹션 린트(The Odin Project TOP001–TOP013 방식), 자료는 프런트매터 인라인(현 PRD v0.5).
- 진도: (user, lesson) 유일 행 + completion 0.0–1.0, 프런트매터 `completion: must_view|must_submit|min_score|must_mark_done`, 모듈 순차 잠금 옵션(Canvas), 이벤트 공통 필드(event_type, source, context{course, user}, time) 후 xAPI 변환은 별도 계층(Open edX).
- 복습: FSRS 라이브러리(py-fsrs/ts-fsrs) 그대로 의존, 레슨·개념 단위 카드 모델은 Oppia skill mastery + Anki revlog 필드(rating, interval, state)를 축소 채택.
- 권한: Moodle식 컨텍스트 범위(course/module/lesson) + 소수 역할, 권한 사전은 Canvas처럼 `enabled/locked` 플래그로 상속 제어.
- 인증·API: 자체 IdP(세션 + OAuth2/JWT), 외부 IdP는 OIDC/SAML 연동만, Moodle 5.3처럼 scope 기반 REST + PAT, GraphQL 불필요.
- 표준(선택): LTI 1.3 Tool(엔터프라이즈 LMS 임베드), xAPI 2.0 내보내기(lrsql), Open Badges 3.0 수료증(Certo AGPL은 참고만).

## 미확인·공백(노트의 Gaps 참조)

Open edX Sumac/Teak/Ulmo 정확 일자·OAuth scope 문서, Canvas 공식 릴리스 일정 본문·SCORM LTI 상세, Moodle 소스 헤더 "or later" 문구·5.3 REST 엔드포인트 목록, Oppia degree_of_mastery 알고리즘, freeCodeCamp 커리큘럼 CC-BY-SA 명시 파일, Anki 최신 스키마(v18) 테이블, FSRS-7 수식, ADL(adlnet.gov) 연결 거부로 SCORM/xAPI 공식 문구 미확인. 과제 전제 "Moodle 플러그인 타입 1,000+"는 부정확(공식 56종).
