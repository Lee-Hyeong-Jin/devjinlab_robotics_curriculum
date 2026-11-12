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
| `/` | 대시보드 | `GET /progress/status`, `GET /progress/next` | 구현됨. `Status` 는 `open_session`·`lessons`·`stages`·`week`·`streak_days`·`due_cards` 를 준다. `current`·`recent` 는 계약에 없어서 현재 모듈은 로드맵에서, 다음 레슨 추천은 `/progress/next` 에서, 최근 활동은 `lessons[]` 의 타임스탬프에서 만든다 |
| `/roadmap` | 로드맵 | `GET /roadmap` | 구현됨. 단계별 모듈 카드 + 그래프의 텍스트 대안 표(AC-A11Y.3) |
| `/modules/[moduleId]` | 모듈 개요 | `GET /modules/{module_id}`, `GET /progress/lessons` | 레슨 목록·상태, 모듈 자료 |
| `/modules/[moduleId]/[lessonId]` | 레슨 | `GET /lessons/{lesson_id}`, `GET /progress/lessons/{lesson_id}` | 본문·공부법·자료·활동. 타이머·완료는 아래 동작 참조 |
| `/modules/[moduleId]/[lessonId]/quiz` | 퀴즈 | `POST /quiz/runs` → `POST /quiz/runs/{id}/answers` → `POST /quiz/runs/{id}/finish` | 문항 하나씩, 즉시 채점·해설 |
| `/review` | 복습 | `GET /review/due`, `POST /review/{card_id}` | 앞면 → 뒤집기 → again/hard/good/easy |
| `/resources` | 자료실 | `GET /resources` | 유형·단계·주제 필터(클라이언트), 검색 |
| `/search` | 검색 | `GET /search?q=` | 구현됨. 2글자 이상, 질의는 URL 에 둔다 |
| `/lessons/[lessonId]` | — | `GET /lessons/{lesson_id}` | 모듈을 모르는 링크(검색 결과, 선수지식 id, 복습 카드)를 정규 URL 로 리다이렉트한다 |
| `/reports` | 리포트 | `GET /reports/weekly`, `GET /reports/modules/{module_id}` | Markdown 렌더 |
| `/login` | 로그인 | `POST /auth/login`, `GET /auth/oidc/{provider}/start` | 비로그인 전용 |
| `/signup` | 회원가입 | `POST /auth/signup` | 비로그인 전용 |
| `/verify-email`, `/password/forgot`, `/password/reset` | 계정 | `POST /auth/verify-email`, `/auth/password/forgot`, `/auth/password/reset` | 토큰은 쿼리에서 |
| `/profile` | 프로필 | `GET/PATCH /me`, `/me/password`, `/me/identities`, `/me/sessions`, `/me/tokens`, `/me/export` | 구현됨. 좌측 섹션 내비 + 앵커. `/me/export` 는 세션 쿠키가 이 오리진에 있어 브라우저가 API 를 직접 못 부르므로 라우트 핸들러 `/api/me/export` 가 중계한다 |
| `/admin/users` | 사용자 관리 | `GET /admin/users`, `PATCH /admin/users/{id}`, `DELETE /admin/users/{id}/sessions`, `POST /admin/invitations` | admin 전용 |
| `/admin/audit` | 감사 로그 | `GET /admin/audit` | 구현됨. 커서 페이지네이션 |
| `/admin/content` | 콘텐츠 | `GET /admin/content`, `POST /admin/content/reload` | 계약에 아직 없음 |
| `/admin/system` | 시스템 | `GET /readyz`, `GET /version` | 미구현. 설정은 마스킹 값 |

### 레슨 화면의 쓰기 동작

| UI | API | 결과 |
|---|---|---|
| [학습 시작] 타이머 | `POST /progress/start` → `POST /progress/stop` | 열린 세션이 있으면 409 → 기존 세션을 보여 주고 종료를 제안 |
| [시간 직접 입력] | `POST /progress/log` | 분 단위 |
| [완료] (이해도 1–5, 메모) | `POST /progress/done` | 응답의 `unlocked_lesson_ids`로 "해금됨" 토스트 |
| 활동 체크박스 | `POST /progress/done` + `activity_id` | 활동 단위 완료 |

## 3. 디자인 토큰

Figma 컬렉션 `Tokens`(22개, Light/Dark 모드)를 CSS 변수로 내보낸다. 이름은 Figma 경로의 `/`를 `-`로 바꾼다.
구현은 `web/src/app/globals.css` 이고, Tailwind 유틸(`bg-surface`, `text-muted` …)은 `@theme inline` 로 이 변수에 묶여 있다.

> **대비 수정(2026-11-12).** 아래 값 중 4개는 Figma 원본과 다르다. Figma 값이 WCAG 2.1 AA 의 소형 텍스트 대비 4.5:1 을
> 넘지 못해 axe-core 가 전 화면에서 실패했기 때문이다(AC-A11Y.1·AC-A11Y.2). 오케스트레이터가 이 값을 정본으로 승인했고,
> **Figma `Tokens` 컬렉션을 이 값으로 고치는 것이 남은 작업**이다(ADR 0008 의 "Figma ↔ 코드 drift 는 리뷰 항목").
>
> | 토큰 | 모드 | Figma | 정본 | 대비 |
> |---|---|---|---|---|
> | `--text-muted` | Light | `#6B7280` | `#4B5563` | 4.39:1 → 6.9:1 (on `--bg-subtle`) |
> | `--text-accent` | Light | `#0F9D8A` | `#0B7A6B` | 3.38:1 → 5.3:1 (on `--bg-surface`), 3.03:1 → 4.8:1 (on `--bg-accent-light`) |
> | `--accent-primary` | Light | `#0F9D8A` | `#0B7A6B` | 흰 글자를 올린 채움: 3.38:1 → 5.3:1 |
> | `--text-on-accent` | Dark | `#FFFFFF` | `#0F1115` | 밝은 다크 accent 위: 2.6:1 → 7.4:1 |
>
> 상태 점(`--status-*`)과 테두리(`--border-accent`)는 Figma 값 `#0F9D8A` 를 그대로 둔다 — 비텍스트 요소라 3:1 이면 충분하다.
> 잠긴 카드·행은 `opacity` 로 흐리게 하지 않는다. 투명도를 곱하면 본문 대비가 3.4:1 까지 떨어진다. 대신 `--bg-subtle` 배경과 🔒 라벨로 표시한다.

```css
:root {
  --bg-page: #F7F8FA;        --bg-surface: #FFFFFF;      --bg-subtle: #F3F4F6;
  --bg-accent-light: #E6F6F3; --bg-warning-light: #FEF3C7; --bg-success-light: #DCFCE7;
  --border-default: #E5E7EB;  --border-accent: #0F9D8A;
  --text-primary: #1A1D21;    --text-muted: #4B5563;      --text-accent: #0B7A6B;
  --text-on-accent: #FFFFFF;  --text-warning: #B45309;    --text-success: #15803D;
  --accent-primary: #0B7A6B;
  --status-done: #0F9D8A;     --status-in-progress: #F59E0B;
  --status-available: #9CA3AF; --status-locked: #D1D5DB;
  --status-success: #16A34A;  --status-danger: #DC2626;   --track-progress: #E5E7EB;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { /* 아래 Dark 값과 동일 */ } }
:root[data-theme="dark"] { --bg-page: #0F1115; --bg-surface: #171A1F; --bg-subtle: #22262D;
  --bg-accent-light: #113B36; --bg-warning-light: #3B2A0A; --bg-success-light: #0F2E1A;
  --border-default: #2A2F37; --border-accent: #2BB5A0; --text-primary: #E6E8EB;
  --text-muted: #9AA3AE; --text-accent: #2BB5A0; --text-warning: #FBBF24;
  --text-success: #4ADE80; --text-on-accent: #0F1115; --accent-primary: #2BB5A0;
  --status-done: #2BB5A0; --status-available: #6B7280; --status-locked: #3F454E;
  --status-success: #22C55E; --status-danger: #EF4444; --track-progress: #2A2F37; }
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

- 파이프라인은 서버 컴포넌트에서 `unified` + `remark-parse` → `remark-math` → `remark-gfm` → `remark-rehype` → `rehype-katex` → `rehype-highlight` → 헤딩 레벨 이동 → `rehype-sanitize` → 헤딩 id 부여 → `rehype-react`. 결과를 RSC로 직렬화하므로 `dangerouslySetInnerHTML`을 쓰지 않는다. 구현은 `web/src/lib/markdown/`.
- **KaTeX 는 MathML 모드**(`output: 'mathml'`)로 돌린다. 그래야 sanitize 스키마에 `style` 속성을 열어 줄 필요가 없고(인라인 스타일 0개), KaTeX CSS 도 클라이언트로 나가지 않는다.
- **하이라이트는 `rehype-pretty-code`(인라인 style) 대신 `rehype-highlight`**(클래스)를 쓰고, `hljs-*` 클래스를 디자인 토큰으로 칠한다. 같은 이유로 sanitize 를 느슨하게 할 필요가 없다.
- `rehype-sanitize`는 MathML 태그·속성과 `hljs-*`·`language-*` 클래스를 허용 목록에 넣는다. `style` 은 어디에도 허용하지 않는다.
- **콘텐츠 헤딩은 한 단계 내린다**(본문 `#` → `<h2>`). 레슨 본문과 주간 리포트가 자체 `#` 제목을 갖고 있어서, 그대로 두면 페이지에 `<h1>` 이 둘이 되어 헤딩 계층(§6)이 깨진다.
- 커리큘럼은 표시 수식의 `$$` 마커를 내용과 같은 줄에 쓴다 — 한 줄(`$$x = y$$`)이거나 여러 줄(`$$A = B,` … `C = D$$`). 정적 사이트의 KaTeX auto-render 는 둘 다 display 로 보지만, `remark-math` 는 math 를 코드 펜스처럼 파싱해서 여는 `$$` 뒤의 글자를 **메타로 버리고** 끝에 `$$` 가 붙은 줄은 닫는 펜스로 보지 않는다. 그러면 블록이 닫히지 않아 레슨 나머지가 통째로 raw TeX 로 나간다. 그래서 파싱 전에 모든 `$$` 마커를 자기 줄로 분리한다(`markdown/normalize.ts`, AC-WEB.2).
- 짧은 필드(레슨 `summary`·`objectives`, 플래시카드 앞/뒤면, 퀴즈 해설)도 인라인 수식을 담으므로 같은 파이프라인의 `renderInlineMarkdown` 으로 렌더한다(단일 문단이면 바깥 `<p>` 를 벗긴다). **자료 `note` 는 제외**한다 — `팔로워 $121.94 / 리더 $229.88` 처럼 `$` 가 가격이라서 수식으로 읽으면 깨진다.
- 가로로 스크롤되는 부분(`pre`, `table`, `math[display=block]`)에는 sanitize 뒤에 `tabindex="0"` 을 붙인다. 마우스 없이 닿을 수 없는 스크롤 영역은 axe 의 `scrollable-region-focusable`(serious, AC-A11Y.1)이다.
- 레슨 화면은 자기 UI 로 이미 보여 주는 절을 본문에서 뺀다(`markdown/sections.ts`): 공부법 절(상단 강조 카드)과 ```` ```quiz ```` 펜스(퀴즈 화면). 빼지 않으면 공부법이 두 번 나오고 퀴즈 YAML 원문이 코드 블록으로 찍힌다. `rc site build` 는 한 페이지에 다 보여 주므로 대신 퀴즈 펜스를 읽을 수 있는 문항 목록으로 바꾼다.
- Mermaid 코드 블록은 클라이언트 전용 컴포넌트로 동적 import(`next/dynamic`, `ssr: false`).
- `study_method`는 같은 파이프라인으로 렌더해 레슨 상단 강조 카드에 넣는다(Figma `11-307`의 "이 단계 공부법").
- 변환 결과는 레슨 ID + 콘텐츠 SHA로 캐시한다(콘텐츠는 재배포 때만 바뀐다).

## 5.1 보안 헤더

API 가 자기 응답에 붙이는 헤더(`api/middleware.py`)는 브라우저가 받는 페이지에는 닿지 않는다
(nginx 가 `web` 을 직접 서빙한다). 그래서 web 이 자기 몫을 붙인다 — `lib/security-headers.ts` 에
정의, `middleware.ts` 가 응답에 설정.

- **CSP 는 nonce 기반**이다. `middleware.ts` 가 요청마다 nonce 를 만들어 정책에 넣고 요청 헤더
  `x-nonce` 로 넘기면, Next 가 자기 스크립트에 붙이고 루트 레이아웃이 직접 쓰는 인라인 스크립트
  (첫 페인트 전 테마 적용)에 붙인다. `'strict-dynamic'` 이 그 스크립트들이 불러오는 청크를 덮으므로
  해시 목록을 관리하지 않는다. `'unsafe-eval'` 은 개발 모드에만 들어간다.
- `style-src` 는 `'unsafe-inline'` 을 유지한다. 진행바 너비가 인라인 `style` 속성이고 Next 가 자기
  style 태그를 주입한다. 스타일 주입은 코드를 실행하지 못하므로, Next 업그레이드마다 깨지는 해시
  목록보다 이쪽이 낫다.
- `img-src` 는 `https:` 를 허용한다. 레슨이 다른 호스트의 그림을 링크할 수 있고, `src` 프로토콜은
  sanitize 스키마가 이미 http(s) 로 제한한다.
- **HSTS 는 HTTPS 요청에만** 보낸다(`x-forwarded-proto`). 평문 HTTP 에서는 브라우저가 무시하고,
  로컬 실행과 E2E 는 일부러 HTTP 다.
- 상수 헤더(`X-Content-Type-Options` 등)는 `next.config.ts` 의 `headers()` 에도 두어
  미들웨어 matcher 가 건너뛰는 `_next/static` 까지 덮는다.
- 회귀 방지: `lib/security-headers.test.ts`(정책 조립)와 smoke e2e(실제 응답 헤더 + nonce CSP 아래
  하이드레이션이 동작하고 콘솔 에러 0).

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

## 8. 구현 순서와 현재 상태

1. ~~뼈대: 레이아웃(`<TopNav>`), 토큰 CSS, API 클라이언트 생성, 인증 미들웨어(401 리다이렉트).~~ 완료
2. ~~읽기 화면: 대시보드 → 로드맵 → 모듈 → 레슨(본문·공부법·자료).~~ 완료
3. ~~인증: 로그인·회원가입·이메일 인증·비밀번호 재설정·프로필.~~ 완료
4. ~~쓰기: 타이머·완료·퀴즈·복습.~~ 완료
5. ~~자료실·검색·리포트(모듈 리포트 화면 포함).~~ 완료
6. 관리자: ~~사용자·감사~~ 완료 / 콘텐츠·시스템 미구현
7. 다크 모드·i18n ~~기본~~ 완료 / ~~부하 테스트~~ 완료(docs/operations/perf-baseline.md) /
   Lighthouse 는 도구 미설치로 생략, LCP·CLS 는 Chromium 으로 직접 측정
   (docs/operations/lighthouse.md)

남은 것: `/admin/content`·`/admin/system`, Lighthouse 도구 도입(의존성 추가 결정 필요).

완료된 것 중 설계가 바뀐 것: OIDC 로그인 버튼은 `GET /api/v1/auth/providers`(설정된 제공자
목록)를 계약에 넣어 해결했고, 퀴즈 해설 Markdown 은 Server Action 이 렌더한 React 트리를
상태로 돌려주는 방식으로 해결했다(RSC 가 직렬화한다).

테스트: Vitest 단위·컴포넌트와 Playwright 두 스펙. `e2e/smoke.spec.ts` 는 **local**
모드 API 로(비로그인 화면 + axe), `e2e/journey.spec.ts` 는 **server** 모드 API 로
(AC-WEB.1 전체 흐름) 돌려야 한다. 자세한 것은 `web/README.md`.
