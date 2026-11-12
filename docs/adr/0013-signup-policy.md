# 0013. 가입 정책: `RC_AUTH_SIGNUP` (open | closed | invite)

- 상태: proposed
- 날짜: 2026-11-12
- 관련: ADR 0009(세션 모델), ADR 0010(인증 구현), docs/architecture/auth.md,
  docs/api/role-matrix.md, docs/ops/asvs-l2-checklist.md, docs/operations/RUNBOOK.md §8

> **초안이다.** 사용자가 정책을 고른 뒤에 구현한다. 지금 들어 있는 것은 설계와 그 근거뿐이며,
> 코드·API·마이그레이션은 아직 없다.

## 맥락

플랫폼이 <https://learnrobotics.devjinlab.com> 으로 공개 배포됐다. 지금은 `RC_AUTH_ALLOW_SIGNUP`
불리언 하나로 "누구나 가입" 또는 "가입 완전 차단"만 고를 수 있다. 공개된 주소에서 이 둘 다
불편하다.

- 누구나 가입: 스팸 계정·봇 가입을 막을 수단이 없다. 계정마다 진행도 행이 생기고 감사 로그가
  늘어난다. 이메일 인증은 SMTP 가 설정된 서버에서만 장벽이 되고(ADR [1'] 참조:
  `email_verification`), 그마저도 일회용 주소로 넘어간다.
- 완전 차단: 소유자가 매번 서버에서 계정을 만들어야 한다. `rc` 에 계정 생성 명령이 없어
  실질적으로 DB 를 직접 만지게 된다.

가운데 단계가 필요하다. 토큰 종류 `invite` 는 ADR 0010 때 `TokenKind.INVITE` 로 자리만 잡아 뒀고
(메일 경로 `accept-invite` 포함) 발급·사용 경로는 없다.

## 선택지

| 선택지 | 장점 | 단점 |
|---|---|---|
| A. 현행 유지(`RC_AUTH_ALLOW_SIGNUP` 불리언) | 코드 변경 0 | 공개 주소에서 쓸 수 있는 중간 단계가 없다 |
| B. `RC_AUTH_SIGNUP=open \| closed \| invite` | 한 변수로 세 운영 형태를 덮고, 기본값을 바꾸지 않아 기존 배포가 그대로 동작 | 초대 토큰·관리자 화면·메일 경로가 새로 필요 |
| C. 도메인 허용 목록(`RC_AUTH_SIGNUP_DOMAINS`) | 기관 배포(대학 메일)에 편하다 | 인증된 이메일이 전제인데 SMTP 없는 배포에서는 검증 불가. 개인 배포에는 쓸모가 없다 |
| D. CAPTCHA·레이트 리밋만 강화 | 외부 의존 없이 봇을 줄인다 | 사람이 직접 만드는 스팸 계정은 막지 못하고, 소유자가 누가 들어오는지 통제하지 못한다 |

B 를 택하고, C 는 `invite` 와 **직교하는** 뒤 작업으로 남긴다(둘 다 켜면 AND). D 는 이미 있는
가입 레이트 리밋으로 부분 충족하며, 외부 CAPTCHA 서비스는 "키 없이도 동작" 원칙과 충돌한다.

## 결정 (제안)

`RC_AUTH_SIGNUP` 을 도입하고 `RC_AUTH_ALLOW_SIGNUP` 을 한 릴리스 동안 별칭으로 유지한다.

| 값 | `POST /api/v1/auth/signup` | 웹 |
|---|---|---|
| `open` (기본) | 지금과 같다 | 가입 링크·화면 그대로 |
| `closed` | 403 problem+json | 가입 링크를 숨기고, `/signup` 은 "이 서버는 가입을 받지 않습니다" |
| `invite` | 유효한 `invite` 토큰이 본문에 있을 때만 201, 없거나 틀리면 403 | `/signup?invite=<토큰>` 으로만 양식을 보여 준다 |

- **별칭 규칙:** `RC_AUTH_SIGNUP` 이 설정돼 있으면 그 값이 이긴다. 없고
  `RC_AUTH_ALLOW_SIGNUP=0` 이면 `closed`, 그 외에는 `open`. 둘이 모순되면(예: `open` + `0`)
  기동 시 경고 1줄을 남기고 `RC_AUTH_SIGNUP` 을 따른다. 다음 메이저에서 별칭을 제거한다.
- **초대 발급:** `POST /api/v1/admin/invitations` (admin 역할, 설계 문서의 `x-planned` 에 이미
  경로가 있다). 본문은 `{ "email": "...", "role": "learner", "expires_in_days": 7 }`.
  이메일은 **선택**이다. 주소를 주면 메일을 보내고(SMTP 가 있을 때), 없으면 응답 본문으로 링크를
  한 번만 돌려준다 — SMTP 없는 배포에서도 초대가 동작해야 한다(ADR [1'] 과 같은 원칙).
- **토큰:** `TokenKind.INVITE`, 기존 일회용 토큰 저장소를 그대로 쓴다(해시만 저장, 1회용,
  기본 7일). 가입이 성공하면 소비된다. `GET /api/v1/admin/invitations` 로 미사용 초대를
  나열하고 `DELETE .../{id}` 로 취소한다. 평문 토큰은 발급 응답에서 한 번만 나간다(PAT 와 같은 규칙).
- **역할:** 초대에 담긴 역할로 계정을 만든다. 단 `admin` 은 초대로 줄 수 없다 — 관리자 승격은
  `rc api promote-admin` 또는 관리자 화면의 명시적 조작으로만(마지막 관리자 보호와 같은 이유).
- **이메일 일치:** 초대에 주소가 있으면 가입 주소가 그 주소와 **같아야** 한다(소문자 정규화 후
  비교, 다르면 403). 주소 없는 초대는 아무 주소로나 쓸 수 있는 "링크 초대"다.
- **열거 방지:** 틀린·만료된·이미 쓴 토큰은 모두 같은 403 문구를 받는다. 토큰 검증 실패도
  가입 레이트 리밋(IP 기준)에 센다.
- **OIDC:** `invite` 와 `closed` 에서 **알려지지 않은** 제공자 신원은 새 계정을 만들지 못하고
  403 이 된다(ADR 0010 의 "그 외에는 비밀번호 없는 새 계정" 규칙이 정책을 우회하지 않도록).
  이미 연결된 신원의 로그인과, 로그인 상태에서 시작하는 연결은 영향이 없다.
- **감사:** `invitation.created`, `invitation.revoked`, `invitation.used`(가입한 user id 포함),
  `auth.signup.refused`(reason `policy` | `invite_invalid` | `invite_email_mismatch`).
- **API 노출:** 가입이 가능한지는 비인증 클라이언트가 알아야 하므로
  `GET /api/v1/auth/providers` 와 같은 자리에 `signup` 상태를 둔다 —
  `GET /api/v1/auth/signup-policy` 를 새로 만들지 않고, 기존 응답을 묶는
  `GET /api/v1/auth/config` 쪽으로 합치는 안을 구현 시 함께 검토한다(엔드포인트 수를 늘리지 않는 편이
  좋다). 어느 쪽이든 비밀은 나가지 않는다.

## 결과

- 얻는 것: 공개 배포에서 소유자가 누가 들어오는지 통제할 수 있고, 기본값이 바뀌지 않으므로 기존
  배포와 테스트는 그대로다. SMTP 없는 배포에서도 초대가 쓸 수 있다.
- 감수하는 것: 일회용 토큰 종류가 하나 더 실제로 쓰이고(만료 정리 잡의 대상이 늘어난다),
  관리자 화면에 초대 목록이 추가된다. 가입 경로의 분기가 셋으로 늘어 테스트 매트릭스가 커진다.
- 후속 작업(이 ADR 이 accepted 된 뒤):
  1. `AuthConfig.signup_policy` + 별칭 처리, `signup()` 의 정책 분기, 403 문구.
  2. `invitations` 발급·목록·취소 API 와 감사 액션, `x-planned` 경로를 실제 경로로 옮기기.
  3. 웹: `/signup?invite=`, 가입 링크 숨김, 관리자 초대 화면, i18n 문구.
  4. 계약 테스트·스냅샷·`docs/api/openapi.yaml` 재생성, role-matrix 행 추가.
  5. RUNBOOK 에 "가입 잠그기 / 초대로 운영하기" 절.
  6. (별도) `RC_AUTH_SIGNUP_DOMAINS` 허용 목록 — `invite` 와 AND 로 결합.
