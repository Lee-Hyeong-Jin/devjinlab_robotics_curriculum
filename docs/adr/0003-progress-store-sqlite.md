# 0003. 학습 진도 저장소: 표준 라이브러리 sqlite3 + 인터페이스/구현 분리

- 상태: accepted
- 날짜: 2026-11-11
- 관련: docs/PRD.md FR-3, FR-10, §8, §12(user_id 선반영); harness/roadmap.yaml P1-1

## 맥락

진도 추적(레슨 상태, 이해도·메모, 타이머/수동 학습 시간)과 JSON 내보내기/가져오기가 필요하다.
제약: 단일 로컬 사용자, 로그인 없음, 오프라인 동작, CLI 응답 1초 이내, Python 단일 스택.
Phase 2에서 웹/API 서버로 옮겨 갈 수 있고, 멀티유저(FR-10.3)를 대비해 `user_id`를 미리 둔다.

## 선택지

| 선택지 | 장점 | 단점 |
|---|---|---|
| A. JSON/YAML 파일 | 사람이 읽기 쉬움, git diff 가능 | 동시 쓰기·부분 갱신·질의(주간 합계 등)가 불편, 손상 위험 |
| B. SQLite + 표준 라이브러리 `sqlite3` | 런타임 의존성 0, 트랜잭션·제약조건, 단일 파일, 빠름 | SQL 직접 작성, 마이그레이션 직접 관리 |
| C. SQLite + ORM(SQLAlchemy/SQLModel) | 마이그레이션 도구(Alembic), 모델 매핑 | 새 런타임 의존성, 테이블 2~3개에는 과함 |

## 결정

B를 택한다.

- `progress/store.py`에 `ProgressStore` Protocol(인터페이스)과 `SqliteProgressStore`(구현)를
  분리한다. 서비스 계층(`progress/service.py`)은 Protocol에만 의존하므로 Phase 2에서
  다른 백엔드로 교체할 수 있다.
- 스키마 v1: `lesson_progress(user_id, lesson_id, status, started_at, completed_at,
  total_seconds, understanding, note)`, `sessions(id, user_id, lesson_id, started_at, ended_at,
  note, source)`, `meta(key, value)`. 사용자당 열린 세션 1개는 부분 유니크 인덱스로 보장한다.
- `meta.schema_version`과 `MIGRATIONS` 딕셔너리로 버전을 관리하고, 열 때마다 빠진 단계만
  하나의 트랜잭션에서 적용한다(멱등).
- 시각은 UTC ISO 8601 문자열. `user_id`는 정수, Phase 1에서는 항상 1.
- 데이터 위치: `$RC_DATA_DIR`(또는 `rc --data-dir`)가 있으면 그 디렉터리, 없으면
  `<repo>/.rc/progress.db`. `<repo>`는 cwd에서 위로 올라가며 `.git` 또는 `pyproject.toml`이
  있는 첫 디렉터리. `.rc/`는 git에서 무시한다.
- 백업·이전은 `rc progress export/import`(JSON, `ProgressExport` 모델).

## 결과

- 얻는 것: 의존성 추가 없음, 원자적 갱신, 테스트에서 `tmp_path`만으로 격리.
- 잃는 것 / 감수하는 리스크: SQL과 마이그레이션을 손으로 관리한다. 진도는 레슨 단위이며
  Activity 단위 상태(FR-3.1의 `rc done <activity>`)는 아직 없다.
- 후속 작업: Activity 단위 진도는 스키마 v2 마이그레이션으로 추가. 주간 학습 시간·streak
  (FR-3.4)은 `sessions`에서 계산한다.
