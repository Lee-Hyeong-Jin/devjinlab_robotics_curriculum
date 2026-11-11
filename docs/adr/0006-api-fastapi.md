# 0006. HTTP API: FastAPI, `/api/v1` 버전 정책, problem+json 오류

- 상태: accepted
- 날짜: 2026-11-11
- 관련: docs/PRD.md 부록 C.2 (AC-API.1~8, "P2-1 1차 범위 합의"), docs/api/openapi.yaml,
  docs/platform-design.md §1.1, docs/architecture/auth.md, harness/roadmap.yaml P2-1,
  ADR 0003(진도 저장소)

## 맥락

Phase 2 웹 화면과 외부 클라이언트가 코스·진도·리포트를 HTTP로 다뤄야 한다(US-API.1~4).
제약: Python 단일 스택(ADR 0001), 코어 라이브러리(content, progress, report)를 그대로 재사용,
CLI와 API가 같은 입력에 같은 결과, OpenAPI 스키마 공개와 비호환 변경 감지, mypy strict.
인증(P2-2)과 PostgreSQL(P2-3)은 뒤따르므로 지금은 그 자리만 만든다.

## 선택지

| 선택지 | 장점 | 단점 |
|---|---|---|
| A. FastAPI + uvicorn | pydantic v2 모델을 그대로 스키마로 사용, OpenAPI 3.1 자동 생성, 의존성 주입(인증 자리), 타입 힌트 친화, TestClient | Starlette/FastAPI 버전 추종 필요 |
| B. Litestar | 성능, DI·DTO 풍부 | 생태계·자료 적음, 팀 익숙도 낮음 |
| C. Flask + 확장(flask-smorest 등) | 성숙 | 동기 전용, pydantic 연동·OpenAPI 생성이 덧붙이기, 타입 지원 약함 |
| D. Django REST Framework | 관리 화면·ORM | 우리 저장소 추상화(ADR 0003)와 겹치고 무거움 |

## 결정

A를 택한다.

- 패키지 `src/robotics_curriculum/api/`: `create_app(settings, clock=...)` 팩토리, 라우터
  `health`(`/healthz`, `/readyz`, `/version`), `content`, `progress`, `reports`.
  fastapi·uvicorn은 optional extra `api`로 두어 CLI만 쓰는 사용자는 설치하지 않는다
  (`rc api serve`는 extra가 없으면 설치 안내를 출력하고 종료 코드 1).
- **버전 정책**: 모든 리소스는 `/api/v1` 아래. 필드 추가·새 엔드포인트처럼 하위 호환인 변경만
  v1에 넣는다. 필드 제거·이름/타입 변경·의미 변경은 `/api/v2`를 v1과 나란히 띄우고, v1은
  공지 후 최소 한 마이너 릴리스 동안 유지한다. 헬스체크(`/healthz`, `/readyz`, `/version`)는
  버전 없음.
- **계약 감시**: `tests/snapshots/openapi.json` 스냅샷 테스트(`info.version` 제외)가 모든 스키마
  변경을 잡는다. 의도한 변경이면 `RC_UPDATE_SNAPSHOTS=1 uv run pytest tests/test_api.py`로
  갱신하고 `docs/api/openapi.yaml`(아키텍트 소유 설계 초안)을 같이 고친다.
- **오류**: RFC 9457 `application/problem+json`. `type`은 `about:blank`, `title`은 HTTP 상태
  문구, `detail`, `instance`(요청 경로), `request_id`, 422에는 `errors[]{loc,msg,type}`.
  404 = 없는 id, 409 = 코어 `ProgressError`(타이머 중복 시작·실행 중 타이머 없음 등),
  422 = 요청 검증, 503 = 콘텐츠 미로드, 500 = 처리되지 않은 예외(내용은 숨기고 로그에만).
- **코어 래핑(AC-API.3)**: 라우터는 `ProgressService`, `build_*_report`/`render_*`,
  `extract_section` 같은 코어 함수만 호출한다. 콘텐츠는 앱 생성 시 코어 로더로 한 번 읽어
  id 색인(`ContentIndex`)을 만들고, 진도는 요청마다 저장소를 열고 닫는다(서버 무상태,
  SQLite 연결이 스레드를 넘지 않음). CLI/API 동치는 테스트로 확인한다(모듈 리포트 Markdown,
  진도 내보내기 JSON).
- **인증 자리**: `current_user_id()` 의존성이 지금은 로컬 사용자 `1`을 돌려준다. P2-2에서
  이 의존성만 세션 쿠키/PAT 검증(docs/architecture/auth.md)으로 바꾸면 라우터는 그대로다.
  경로·본문에는 `user_id`를 받지 않는다.
- **운영 최소 구현**: 요청 ID 미들웨어(`X-Request-ID` 수용 또는 생성, 응답 헤더·로그에 기록),
  JSON 한 줄 로그(`rc api serve`가 루트·uvicorn 로거를 JSON으로 설정), `/readyz`는 콘텐츠
  색인과 진도 저장소 열기를 확인한다. 설정은 `RC_CURRICULUM_DIR`, `RC_DATA_DIR`,
  `RC_API_HOST`, `RC_API_PORT`, `RC_API_LOG_LEVEL`(CLI 옵션이 우선).

## 결과

- 얻는 것: 코어 모델 재사용으로 스키마 중복이 적고, OpenAPI가 자동으로 맞는다. 인증·DB 교체가
  의존성 하나와 저장소 구현 하나로 국한된다.
- 잃는 것 / 감수하는 리스크: FastAPI·Starlette 업그레이드 때 스냅샷이 바뀔 수 있다(검토 후
  갱신). 요청마다 SQLite를 여는 비용(로컬 모드에서는 무시할 수준, 서버 모드는 P2-3 풀로 대체).
  리포트의 "이번 주"는 서버 로컬 시간대 기준이다(CLI와 같음).
- 후속 작업: 퀴즈·복습 엔드포인트와 레슨 퀴즈 필드(P1-2 머지 후), 활동 단위 상태 갱신,
  `/progress/sessions` 커서 페이지네이션, `/roadmap`, `/search`, 콘텐츠 재색인(AC-API.6,
  platform-design §1.1), Prometheus 메트릭·부하 테스트(P2-5), 인증(P2-2), PostgreSQL(P2-3).
