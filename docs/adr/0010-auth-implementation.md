# 0010. 인증 구현 세부: 모드, 세션 수명, CSRF 바인딩, 시도 제한, PAT 범위

- 상태: accepted
- 날짜: 2026-11-11
- 관련: ADR 0009(세션 모델), docs/architecture/auth.md, docs/PRD.md 부록 C.3(AC-AUTH.1~9),
  docs/ops/asvs-l2-checklist.md, docs/api/role-matrix.md, harness/roadmap.yaml P2-2

## 맥락

ADR 0009가 "브라우저 = 서버 측 세션 쿠키, 프로그램 = PAT"를 정했다. 구현에서 남은 결정:
로컬 모드와 공존하는 방식, 세션 수명 상한, CSRF 토큰 검증 방식, 시도 제한 수치, PAT 범위의 의미,
문서 간 수치 차이(재설정 토큰 1시간 vs 30분).

## 선택지

| 결정 | 택한 것 | 버린 것과 이유 |
|---|---|---|
| 모드 | `RC_AUTH_MODE=local`(기본, 계정 없음·user 1) / `server` | 로컬에도 로그인 강제 → 1인 오프라인 사용성 저하 |
| 세션 수명 | 유휴 14일 슬라이딩 + 절대 30일 | 슬라이딩만 → 탈취 세션이 무기한 유지(ASVS 3.3) |
| CSRF | 로그인 시 랜덤 토큰을 쿠키(`csrf_token`, HttpOnly 아님)와 응답 본문으로 주고, 세션 행에 SHA-256만 저장. 쿠키 인증의 비안전 메서드는 `X-CSRF-Token`이 그 해시와 일치해야 함 | 순수 더블 서밋(쿠키=헤더 비교) → 하위 도메인이 쿠키를 심을 수 있으면 우회 |
| 시도 제한 | 계정별 15분 창 실패 5회, IP별 20회 → 429 + `Retry-After`(창이 지나면 해제). 실패 기록은 DB(`login_attempts`) | 메모리 카운터 → 무상태·다중 레플리카와 충돌. IP 5회 → NAT 뒤 기관 사용자 일괄 차단 |
| 계정 열거 | 잘못된 비밀번호와 없는 계정이 같은 401 문구·같은 Argon2 비용, 재설정 요청은 항상 202 | — |
| PAT | `rcp_` 접두사 + 256비트, 해시만 저장, 범위 `read:progress`(GET), `write:progress`(쓰기), `admin`(관리 API, admin 역할 필요). PAT로 계정 관리(`/me` 수정·토큰·세션·삭제)는 불가 | 범위 없는 토큰 → 유출 시 피해 범위가 계정 전체 |
| 재설정 토큰 | 30분 1회용(PRD AC-AUTH.1이 auth.md의 1시간보다 우선), 사용 시 모든 세션 무효 | — |
| 감사 로그 | append-only(갱신·삭제 API 없음), 보존 기간(`RC_AUTH_AUDIT_RETENTION_DAYS`, 기본 90일) 뒤 행위자 id·IP만 익명화 | DB 트리거로 불변 강제 → 익명화 UPDATE도 막힘 |
| 저장소 | `auth/` 패키지의 `AuthStore` Protocol + SQLAlchemy Core 구현(SQLite·PostgreSQL 공용). 스키마 원본은 `auth/schema.py`, PostgreSQL은 Alembic 0003(P2-3), SQLite는 `create_all` | ORM → 진도 저장소(ADR 0003·0007)와 스타일 불일치 |

## 결정

위 표의 "택한 것". OIDC(AC-AUTH.3)는 `identities` 테이블과 `/auth/oidc/{provider}/start|callback`
자리(501)만 두고 2차 증분에서 authlib로 구현한다.

## 결과

- 얻는 것: 로컬 모드 사용자는 바뀌는 것이 없고, 서버 모드는 모든 `/api/v1` 호출이 인증되며
  학습 데이터 조회는 인증 컨텍스트의 `user_id`로만 묶인다(라우터·코어 서비스 두 겹).
- 감수하는 것: 인증 요청마다 세션 조회 1회(+분당 1회 갱신), 로그인 실패마다 행 1개 기록
  (`login_attempts` 정리 작업은 P2-5 운영 작업으로).
- 후속: OIDC(2차), 메일 인증 전 기능 제한(공개 기능이 생길 때), MFA(Phase 3), HIBP 유출 비밀번호
  검사(선택), `login_attempts`·만료 세션 정리 잡, 초대(`invite` 토큰 종류만 선반영).
