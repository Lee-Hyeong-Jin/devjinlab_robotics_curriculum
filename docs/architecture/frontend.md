# 프론트엔드 구현 가이드 (web/)

| 항목 | 내용 |
|---|---|
| 버전 | 0.1 (2026-11-11) |
| 대상 | Phase 2 `web/` 구현 세션 |
| 결정 | `docs/adr/0008-web-nextjs.md` (Next.js App Router), `docs/adr/0009-session-model.md` (세션 쿠키 + PAT) |
| 계약 | `docs/api/openapi.yaml` (경로·스키마 정본), `docs/platform-design.md` §2 (IA·와이어프레임), §2.5 (i18n·접근성) |
| 디자인 | Figma 파일 `BVk1OeYnq1gFHz4etJi1oN` — 아래 §4 노드 매핑 |
| 착수 조건 | P2-1 API 머지 후. 그 전에는 계약과 Figma가 고정 인터페이스다 |

## 1. 스택과 규칙

- Next.js 15 App Router + React 19 + TypeScript strict. 패키지 매니저 `pnpm`.
- Tailwind CSS. **색은 임의 hex 금지** — §3의 CSS 변수만 쓴다.
- 상태: 서버 데이터는 서버 컴포넌트에서 fetch, 변경은 Server Action 또는 라우트 핸들러. 클라이언트 전역 상태 라이브러리는 쓰지 않는다.
- API 클라이언트는 `openapi.yaml`에서 생성(`openapi-typescript` + 얇은 fetch 래퍼). **손으로 타입을 다시 정의하지 않는다.**
- 코어(Python)를 import하지 않는다. 모든 데이터는 API에서 온다.
- 테스트: Playwright E2E(주요 흐름 + axe-core 접근성 0 위반), Vitest 단위(포맷터·훅).

### 인증 처리

- 브라우저는 `sid` 쿠키(HttpOnly)를 쓴다. 프론트엔드 JS는 토큰을 보관하지 않는다.
- 변경 요청(POST/PATCH/DELETE)에는 `X-CSRF-Token` 헤더를 더블 서밋으로 보낸다.
- 401 → `/login?next=<현재경로>`로 리다이렉트. 403 → "권한 없음" 화면(역할 부족).
- 서버 컴포넌트에서 fetch할 때 요청 쿠키를 그대로 전달한다(`cookies()` → `Cookie` 헤더).

## 2. 라우트와 API 매핑

| 라우트 | 화면 | 주 API | 비고 |
|---|---|---|---|
| `/` | 대시보드 | `GET /progress/status` | 로그인 필수. 현재 단계·모듈·다음 레슨, 단계별 진행률, 주간 시간, 연속일, 복습 수, 최근 활동 |
| `/roadmap` | 로드맵 | `GET /roadmap` | 단계별 모듈 카드 + 선수지식 체인 |
| `/modules/[moduleId]` | 모듈 개요 | `GET /modules/{module_id}`, `GET /progress/lessons` | 레슨 목록·상태, 모듈 자료 |
| `/modules/[moduleId]/[lessonId]` | 레슨 | `GET /lessons/{lesson_id}`, `GET /progress/lessons/{lesson_id}` | 본문·공부법·자료·활동. 타이머·완료는 아래 동작 참조 |
| `/modules/[moduleId]/[lessonId]/quiz` | 퀴즈 | `POST /quiz/runs` → `POST /quiz/runs/{id}/answers` → `POST /quiz/runs/{id}/finish` | 문항 하나씩, 즉시 채점·해설 |
| `/review` | 복습 | `GET /review/due`, `POST /review/{card_id}` | 앞면 → 뒤집기 → again/hard/good/easy |
| `/resources` | 자료실 | `GET /resources` | 유형·단계·주제 필터(클라이언트), 검색 |
| `/search` | 검색 | `GET /search?q=` | 레슨·자료 통합 |
| `/reports` | 리포트 | `GET /reports/weekly`, `GET /reports/modules/{module_id}` | Markdown 렌더 |
| `/login` | 로그인 | `POST /auth/login`, `GET /auth/oidc/{provider}/start` | 비로그인 전용 |
| `/signup` | 회원가입 | `POST /auth/signup` | 비로그인 전용 |
| `/verify-email`, `/password/forgot`, `/password/reset` | 계정 | `POST /auth/verify-email`, `/auth/password/forgot`, `/auth/password/reset` | 토큰은 쿼리에서 |
| `/profile` | 프로필 | `GET/PATCH /me`, `/me/password`, `/me/identities`, `/me/sessions`, `/me/tokens`, `/me/export`, `DELETE /me` | 좌측 하위 탭 |
| `/admin/users` | 사용자 관리 | `GET /admin/users`, `PATCH /admin/users/{id}`, `DELETE /admin/users/{id}/sessions`, `POST /admin/invitations` | admin 전용 |
| `/admin/content` | 콘텐츠 | `GET /admin/content`, `POST /admin/content/reload` | reload는 author 이상 |
| `/admin/audit` | 감사 로그 | `GET /admin/audit` | 커서 페이지네이션 |
| `/admin/system` | 시스템 | `GET /readyz`, `GET /version` | 설정은 마스킹 값 |

### 레슨 화면의 쓰기 동작

| UI | API | 결과 |
|---|---|---|
| [학습 시작] 타이머 | `POST /progress/start` → `POST /progress/stop` | 열린 세션이 있으면 409 → 기존 세션을 보여 주고 종료를 제안 |
| [시간 직접 입력] | `POST /progress/log` | 분 단위 |
| [완료] (이해도 1–5, 메모) | `POST /progress/done` | 응답의 `unlocked_lesson_ids`로 "해금됨" 토스트 |
| 활동 체크박스 | `POST /progress/done` + `activity_id` | 활동 단위 완료 |

## 3. 디자인 토큰

Figma 컬렉션 `Tokens`(22개, Light/Dark 모드)를 CSS 변수로 1:1 내보낸다. 이름은 Figma 경로의 `/`를 `-`로 바꾼다.

```css
:root {
  --bg-page: #F7F8FA;        --bg-surface: #FFFFFF;      --bg-subtle: #F3F4F6;
  --bg-accent-light: #E6F6F3; --bg-warning-light: #FEF3C7; --bg-success-light: #DCFCE7;
  --border-default: #E5E7EB;  --border-accent: #0F9D8A;
  --text-primary: #1A1D21;    --text-muted: #6B7280;      --text-accent: #0F9D8A;
  --text-on-accent: #FFFFFF;  --text-warning: #B45309;    --text-success: #15803D;
  --accent-primary: #0F9D8A;
  --status-done: #0F9D8A;     --status-in-progress: #F59E0B;
  --status-available: #9CA3AF; --status-locked: #D1D5DB;
  --status-success: #16A34A;  --status-danger: #DC2626;   --track-progress: #E5E7EB;
}
:root:not([data-theme="light"]) { @media (prefers-color-scheme: dark) { /* Dark 값 */ } }
:root[data-theme="dark"] { --bg-page: #0F1115; --bg-surface: #171A1F; --bg-subtle: #22262D;
  --bg-accent-light: #113B36; --bg-warning-light: #3B2A0A; --bg-success-light: #0F2E1A;
  --border-default: #2A2F37; --border-accent: #2BB5A0; --text-primary: #E6E8EB;
  --text-muted: #9AA3AE; --text-accent: #2BB5A0; --text-warning: #FBBF24;
  --text-success: #4ADE80; --accent-primary: #2BB5A0; --status-done: #2BB5A0;
  --status-available: #6B7280; --status-locked: #3F454E; --status-success: #22C55E;
  --status-danger: #EF4444; --track-progress: #2A2F37; }
```

- 글꼴: 본문 Noto Sans KR(또는 Pretendard), 레슨 ID·CLI 명령은 JetBrains Mono.
- 간격 8px 그리드, 카드 반경 12px, 내비 높이 64px, 데스크톱 폭 1440 기준.
- 테마 전환은 `<html data-theme>` 속성 + `localStorage`(기본값은 시스템 설정).

## 4. 컴포넌트 ↔ Figma 노드 매핑

파일: `https://www.figma.com/design/BVk1OeYnq1gFHz4etJi1oN/?node-id=<id>`

### 화면 프레임

| 화면 | Figma 노드 | 라우트 |
|---|---|---|
| Cover (제품 정의·목록) | `12-107` | — |
| Tokens (Light/Dark 표) | `20-139` | — |
| Components (섹션) | `20-138` | — |
| Dashboard | `11-2` (다크 변형은 같은 페이지) | `/` |
| Roadmap | `11-119` | `/roadmap` |
| Lesson | `11-307` | `/modules/[moduleId]/[lessonId]` |
| Resources | `11-492` | `/resources` |
| Login | `23-3` | `/login` |
| Signup | `23-55` | `/signup` |
| Profile | `23-111` | `/profile` |
| Admin (사용자 관리) | `23-221` | `/admin/users` |

### 컴포넌트

| React 컴포넌트 | Figma 노드 | 변형 | 쓰이는 곳 |
|---|---|---|---|
| `<StatusDot state>` | `10-2` done · `10-3` in-progress · `10-4` available · `10-5` locked | 4 | 로드맵, 레슨 사이드바, 모듈 카드 |
| `<Chip tone>` | `10-8` neutral · `10-10` accent · `10-12` warning · `10-14` success · `10-16` locked | 5 | 단계·역할·상태·필터 |
| `<Button kind>` | `10-20` primary · `10-22` secondary · `10-24` mono(명령 표시) | 3 | 전역 |
| `<NavTab active>` | `10-28` default · `10-30` active | 2 | 상단 내비 |
| `<ProgressBar value>` | `10-34` | — | 대시보드, 모듈 카드 |
| `<StatTile>` | `10-37` | — | 대시보드, 관리자 통계 |
| `<ModuleCard>` | `10-42` | — | 로드맵 |
| `<LessonRow>` | `10-58` | — | 모듈 개요, 레슨 사이드바 |
| `<StudyStep n action text>` | `10-64` | — | 레슨 "이 단계 공부법" |
| `<ResourceRow>` | `10-70` | — | 레슨 자료, 자료실 |

추가로 만들 것(Figma에 단독 노드 없음, 화면 안에서 확인): `<TopNav>`, `<SideNav>`, `<PageHeader>`, `<Card>`, `<DataTable>`(자료실·사용자·감사 공용), `<FilterBar>`, `<SearchInput>`, `<Toast>`, `<Modal>`, `<EmptyState>`, `<Pagination>`(커서), `<MarkdownBody>`(KaTeX·Mermaid 포함), `<QuizQuestion>`, `<ReviewCard>`.

> 진행률 바는 Figma에서 인스턴스가 아니라 분리된 프레임이다(플러그인 API 제약). 구현에서는 `<ProgressBar>` 하나로 만든다.

## 5. 콘텐츠 렌더링

API는 **Markdown 원문**을 준다(`GET /api/v1/lessons/{id}` → `body`, `study_method`, `content_format: "markdown"`). HTML 변환은 프론트엔드 책임이다.

- 파이프라인은 서버 컴포넌트에서 `unified` + `remark-parse` → `remark-math` → `remark-gfm` → `rehype-katex` → `rehype-pretty-code` → `rehype-sanitize` → `rehype-react`. 결과를 RSC로 직렬화하므로 `dangerouslySetInnerHTML`을 쓰지 않는다.
- `rehype-sanitize`는 KaTeX·코드 하이라이트가 쓰는 클래스와 속성을 허용 목록에 넣는다.
- Mermaid 코드 블록은 클라이언트 전용 컴포넌트로 동적 import(`next/dynamic`, `ssr: false`).
- `study_method`는 같은 파이프라인으로 렌더해 레슨 상단 강조 카드에 넣는다(Figma `11-307`의 "이 단계 공부법").
- 변환 결과는 레슨 ID + 콘텐츠 SHA로 캐시한다(콘텐츠는 재배포 때만 바뀐다).

## 6. i18n과 접근성

- `next-intl`. 메시지 `messages/ko.json`, `messages/en.json`. 기본 `ko`.
- 언어 결정: `users.locale` → `Accept-Language` → `ko`. 프로필에서 변경하면 `PATCH /me`.
- 레슨 콘텐츠는 번역 대상이 아니다(한국어 본문 + 영어 용어 병기).
- 날짜·시간은 `users.timezone` 기준으로 서식화.
- 접근성(WCAG 2.1 AA): 랜드마크(`header/nav/main/aside`), 헤딩 계층, 포커스 링 2px accent, 모달 포커스 트랩, 건너뛰기 링크, 표에 `th scope`, 진행률 바 `role="progressbar" aria-valuenow`, 아이콘 버튼 `aria-label`, `prefers-reduced-motion` 존중, 200% 확대에서 가로 스크롤 없음.
- 상태는 색만으로 전달하지 않는다(점 + 글자, 🔒 아이콘 병기).

## 7. 성능 목표 (PRD 7절)

| 항목 | 목표 | 방법 |
|---|---|---|
| 페이지 LCP | 2.5초 이내 | 레슨·로드맵은 서버 컴포넌트 + 정적 생성, 진도 의존 부분만 클라이언트 섬 |
| 읽기 API p95 | 300 ms | 서버 컴포넌트에서 병렬 fetch, 중복 호출 제거 |
| 번들 | 초기 JS 200 KB 이하(gzip) | Mermaid·KaTeX 동적 import, 관리자 화면 라우트 분할 |

## 8. 구현 순서 제안

1. 뼈대: 레이아웃(`<TopNav>`), 토큰 CSS, API 클라이언트 생성, 인증 미들웨어(401 리다이렉트).
2. 읽기 화면: 대시보드 → 로드맵 → 모듈 → 레슨(본문·공부법·자료).
3. 인증: 로그인·회원가입·이메일 인증·비밀번호 재설정·프로필.
4. 쓰기: 타이머·완료·퀴즈·복습.
5. 자료실·검색·리포트.
6. 관리자: 사용자·콘텐츠·감사·시스템.
7. 다크 모드·i18n 마감, axe·Lighthouse·부하 테스트.
