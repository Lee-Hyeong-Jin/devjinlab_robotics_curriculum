# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Monitoring for operators at `/admin/monitoring` (P3-2, ADR 0017, RUNBOOK §8.4):
  - **API traffic**: requests, success rate, latency p50/p95/p99, Apdex, an error budget against
    a 99.9% availability target, and the busiest, slowest and failing routes, over 24 hours,
    7 days or 30 days. Counts are stored per hour and survive a restart.
  - **Failed requests**: every 5xx with its time, route, exception and request id, to look up
    in the server log. Query strings and bodies are never recorded.
  - **System resources**: CPU load and usage, memory, swap, disk, temperature sensors, open
    files, uptime, and the database's response time, size and connections.
  - **Visits**: page views and unique visitors per day, crawler views, the most viewed pages,
    referring sites and languages — counted by the server, with no browser script, no cookie
    and no stored IP address or user agent.
  - **Product KPIs**: DAU / WAU / MAU and stickiness, sign-ups, visit-to-sign-up, activation
    rate, week-1 retention, learning volume and mean quiz score.
  - Readings past a threshold are listed at the top and on the admin overview.
- `RC_OPS_METRICS` (default on) turns the recording off.
- Web SEO, third pass — content and technical (frontend.md §5.2):
  - Titles and headings carry the words people search with: the home page is "로보틱스 강의 —
    …" / "Learn Robotics — Free Robotics Tutorials and Courses", and a lesson is
    "<topic> — 로보틱스 강의 | Learn Robotics" / "<topic> — Robotics Tutorial | Learn Robotics"
    (shortened when the topic is long).
  - The landing page has real content: an introduction, what the course teaches (module
    summaries), how it works, and a FAQ with `FAQPage` structured data.
  - `/guide`, "로보틱스 공부 방법" / "How to learn robotics": prerequisites, the learning path with
    hours computed from the curriculum, how to work through a lesson, and a FAQ.
  - A footer on every published page linking the roadmap, the guide and the resource library.
  - `Course` structured data states that the course is free and its workload.
- Admin console for operators (P3-1, RUNBOOK §8.3):
  - `/admin` overview: what needs attention, account, session and sign-in totals, learning
    activity for the last seven days, a 14-day sign-up trend and the system settings
    (`GET /admin/overview`).
  - User search by email or name with role, status and verification filters and a total count;
    a page per account with its sessions, API tokens, external sign-ins, learning summary and
    recent audit trail (`GET /admin/users/{id}/overview`).
  - Admin actions on an account: revoke every API token (`DELETE /admin/users/{id}/tokens`) and
    send a password-reset email the admin never sees (`POST /admin/users/{id}/password-reset`).
  - Audit log filters (action prefix, actor, target, period), the actor's email on each entry,
    and a CSV export that is safe to open in a spreadsheet (`GET /admin/audit/export`).
- `RC_API_TRUSTED_PROXIES`: the proxies allowed to tell the API the browser's address.
- Web SEO, second pass (frontend.md §5.2, RUNBOOK §8.2):
  - On a deployment that publishes its curriculum, `/` is a public landing page for a visitor
    without a session — the courses, stages and modules, all linked — and is indexable. It used
    to be the dashboard for everybody, so the site's root URL was a `noindex` page of zeroes.
    A signed-in reader still gets their dashboard there.
  - Site verification for Google Search Console and Naver Search Advisor through
    `RC_GOOGLE_SITE_VERIFICATION` and `RC_NAVER_SITE_VERIFICATION`.
  - A favicon, an app icon, a web app manifest and a 1200x630 share image on every page
    (`summary_large_image`).
  - Structured data: `WebSite`, `Organization` and a course `ItemList` on the home page,
    `CollectionPage` on the resource library.
- Web: a responsive layout for phones and tablets (frontend.md §4.2). The top navigation no
  longer overflows below 1280px: on a phone it collapses into a menu, on a tablet the page links
  stay in the bar and the account, language and theme controls move into the menu. No page
  scrolls sideways from 320px up; a long formula, a table or a code block scrolls inside its own
  block. Data tables (resources, admin, profile) stack each row as a card on a phone, buttons,
  inputs, tabs and quiz options have a 44px touch height, and Korean text breaks between words.
  Checked by `e2e/smoke-responsive.spec.ts` at 320, 390, 768 and 1024px.
- Research track complete: all 105 lessons of the design (17 modules) are now in Korean and
  English. This closes S1 (`s1-dense-neural-slam`, `s1-semantic-scene-graphs`,
  `s1-certifiable-slam`, `s1-slam-benchmarking`), S3 (`s3-locomotion-rl`,
  `s3-dynamic-maneuvers`), S4 (`s4-evaluation-science`, `s4-safety-ood`), S5
  (`s5-active-information-gathering`, `s5-comms-constrained-estimation`, `s5-field-deployment`),
  C4 (`c4-robust-stochastic-oc`) and adds the R2 capstone module (`r2-capstone-survey`,
  `r2-capstone-reproduction`, `r2-capstone-contribution`). The numbers in each reproduction task
  come from running its code; comparisons against public tools and datasets that were not run are
  marked as such in the lesson.
- `curriculum/README.md` lists the research-track modules and the current translation status.
- 연구원 트랙에 S2 조작·접촉 모듈을 열었다 — `s2-grasp-mechanics`(접촉 역학과 파지 안정성),
  `s2-contact-modes-dexterity`(접촉 모드와 외재적 손재주),
  `s2-tactile-contact-estimation`(촉각과 접촉 상태 추정),
  `s2-learned-grasping`(학습 기반 파지), `s2-generative-policies`(생성형 정책),
  `s2-planning-through-contact`(접촉을 통한 계획·제어). 모듈 6 레슨 완성.
  각 레슨은 한국어·영어.
- Research-track lesson `c4-contact-implicit-hybrid`: a proof that the complementarity set is
  non-convex and breaks LICQ at every feasible point, the time-stepping through-contact
  transcription, the saltation matrix derived from the variation in transition time and
  verified against finite differences, and a measured relaxation study showing that the
  relaxation is always tight and falsifies the contact schedule. Korean source plus the
  English translation.
- Research-track lesson `c4-mpc`: recursive feasibility from control invariance of the
  terminal set and Lyapunov stability from a terminal cost that is a control Lyapunov
  function, both proved by the shift-and-append construction; a grid study counting the 178
  states that are feasible now and infeasible later without a terminal condition; explicit
  MPC as a piecewise affine map; and real-time iteration. Korean source plus the English
  translation.
- Research-track lesson `c4-direct-collocation-sqp`: the exact nonzero count of the
  transcribed constraint Jacobian and its identity with the Riccati recursion, Hermite-Simpson
  derived from cubic Hermite interpolation with midpoint collocation (global order four), SQP
  proved to be Newton's method on the KKT system, and a measurement showing a
  machine-precision defect alongside an $O(10^2)$ interpolant residual. Korean source plus the
  English translation.
- Research-track lesson `c4-ilqr-ddp`: the second-order DDP backward pass derived in full,
  why DDP is Newton on the control sequence (quadratic) and iLQR Gauss-Newton (linear), the
  two regularizations and the merit-ratio line search, exact handling of control box
  constraints against the impossibility for state constraints, and the locality of the
  method. Korean source plus the English translation.
- Research-track lesson `c4-dp-lqr-lqg`: the Bellman equation and the HJB, the verification
  theorem as the sufficient condition the PMP lacks, the costate as the gradient of the value
  function, LQR derived three ways (DP, PMP, completion of squares), monotone convergence of
  the Riccati recursion with a worked detectability counterexample, and the LQG separation
  theorem together with Doyle's margin critique. Korean source plus the English translation.
- Research-track module C4 (optimal control and trajectory optimization) with its first
  lesson, `c4-pontryagin-indirect`: Pontryagin's minimum principle proved from needle
  variations and a separating hyperplane, the adjoint equation derived as the transpose of
  the variational equation, bang-bang structure and singular arcs, the exponential
  conditioning of single shooting, and the brachistochrone solved in closed form. Korean
  source plus the English translation.
- 연구 트랙 S5 모듈 세 번째 레슨 `s5-multi-agent-planning`(다중 로봇 경로 계획): CBS 의 완전성·최적성 증명, 우선순위 계획이 모든 순서에서 실패하는 반례, 고정 예산 아래 성공률 역전의 실측. 한국어·영어 동시 제공.
- 연구원 트랙 S5 에 `s5-distributed-optimization`(분산 최적화와 분산 SLAM, ko/en)을 추가했다.
  2블록 ADMM 의 수렴을 증명하고 2차 문제에서 ADMM 이 아핀 반복임을 보여 수렴률을 명시적
  스펙트럼 반경으로 쓰고, 블록 Gauss-Seidel 의 수렴률이 정확히 1 − λ_min(Λ₂₂⁻¹S)(S 는 Schur
  보완)임을 증명해 Λ ≻ 0 이면 항상 수렴함을 보였다. 2대 로봇 포즈 그래프에서 중앙집중 해와
  186 라운드에 1e-4 이내로 일치하고, 로봇 간 공유를 늘리면 정확도는 올라가지만 수렴률이
  나빠지는 교환을 수치로 측정했다.
- 연구원 트랙에 S5 다중 로봇·필드 로보틱스 모듈을 시작했다 — `s5-graph-consensus`(그래프
  이론과 합의, ko/en). 연속시간 합의의 수렴률이 정확히 대수적 연결성 λ₂ 임을 증명하고, 이산시간
  합의의 최적 보폭 2/(λ₂+λₙ)과 그 수렴률 (κ−1)/(κ+1)을 닫힌 형태로 유도하고, 방향 그래프의
  합의값이 좌 영벡터 가중 평균임을 보이고, 시변 그래프에서는 결합 연결성만이 문제임을
  (각각 λ₂ = 0 인 두 그래프를 번갈아 써도 합의에 도달함을) 수치로 확인했다.
- 연구원 트랙에 C6 동작 계획 이론 모듈을 추가했다 — `c6-cspace-complexity`(구성공간과 복잡도),
  `c6-combinatorial-gcs`(조합적 계획과 볼록 분해), `c6-sampling-completeness`(샘플링 기반과
  확률적 완전성), `c6-asymptotic-optimality`(점근 최적성),
  `c6-search-based-planning`(탐색 기반 계획),
  `c6-kinodynamic-planning`(미분 제약·격자 계획),
  `c6-tamp`(TAMP). 7레슨 전부 한국어·영어.
- Translations for the content that had nowhere to hold them: `course.<lang>.yaml` and
  `module.<lang>.yaml` carry a course's and a module's title and summary, and
  `<lesson>.<lang>.yaml` carries activity titles, resource titles and notes, and the quiz
  (matched by question id, so `type` and `answer` are never translated and grading is
  identical in every language). This release ships the English course and module metadata,
  the activity titles and resources of all 50 lessons, and the 42 quiz questions of M1-M4.
- `level_label` on every API response that carries a module level, and `label` on the
  dashboard's stage statistics: `level` stays the stable id written in `module.yaml`
  (`기초`/`중급`/`고급`) and the label is what a reader is shown.
- `?lang=` on any API request, which wins over `Accept-Language`. A client that caches by
  URL — the web front-end does — needs the language in the URL so two readers in two
  languages cannot share one cached body.
- `answers` on a translated quiz question (`<lesson>.<lang>.yaml`, `short` questions only):
  accepted answers written in that language. They are *added* to the ones in the lesson
  body and never substituted for them, so what counts as correct is the union over every
  language and grading does not depend on the language a learner reads in; only the
  answer that is *shown* follows the request. `rc validate` rejects `answers` on a
  question that is not `short`, and rejects `display_answers` in a quiz block, since it
  is derived and never graded.
- `docs/curriculum/GLOSSARY.md`: the ko ↔ en term list every translation follows.
- `scripts/i18n/audit.py` and `docs/reviews/i18n-gap-audit.md`: the English build is driven
  end to end (API, static site, CLI) and every Korean string that is left is reported.
- Research-track specialization module `s4-robot-learning-foundation-models` (S4, robot
  learning and foundation models) at `level: 연구`. Every reproduction task is judged on a CPU
  without a GPU; large-scale fine-tuning is an optional extension. Lessons so far:
  `s4-robot-data-scaling`, `s4-vla-architectures`,
  `s4-pretrained-representations`, `s4-language-and-planning`.
- Research-track module `c8-decision-making-learning-theory` (C8, decision making and
  learning theory) at `level: 연구`, complete with all eight lessons in Korean and English:
  `c8-mdp-pomdp-bellman`, `c8-policy-gradient`, `c8-value-based-rl`,
  `c8-model-based-world-models`, `c8-imitation-learning`, `c8-offline-rl`,
  `c8-control-as-inference` and `c8-generalization-sim2real`. Each derives its central
  results to the depth the blueprint asks for, names a failure mode per D2/D3 result, and
  carries a problem set, two to four must-read papers (resolved through the course registry),
  a reproduction task whose acceptance criteria were checked by running the code, and open
  problems.

### Security
- Tightened validation of the page a reader returns to after signing in.
- Sessions, audit entries and the per-address sign-in limit now use the browser's address and
  user agent instead of the web server's. The web forwards them and the API accepts
  `X-Forwarded-For` only from a trusted proxy (RUNBOOK §8, "클라이언트 주소").
- The Security workflow's `npm audit (web)` job now applies an allowlist
  (`web/audit-allowlist.txt`, checked by `scripts/ops/npm_audit_gate.py`). One exception is
  recorded: GHSA-fc5q-39xc-vjpf (picomatch ReDoS, reached through next-intl's file watcher), for
  which no patched release exists yet. Every other high or critical advisory still fails the job,
  and the entry fails the job once it no longer applies.
- Removed that exception again: GHSA-fc5q-39xc-vjpf was withdrawn upstream on 2026-11-18, so
  `npm audit` reports nothing for the web lockfile and the allowlist is empty.

### Fixed
- A browser whose session had been ended elsewhere (another device, an operator, a disabled
  account) got HTTP 500 on every page, the login screen included, until its cookies were
  cleared by hand. It is now treated as signed out and sent to sign in again.
- The link in the password-reset mail opened a page that does not exist. It now opens the reset
  screen; links from mails already sent are redirected.
- A profile time zone that is not a real zone was saved and then broke the profile screen for
  that account. The API accepts IANA zone names only and the screen no longer fails on a stored
  bad value.
- Changing the password with a wrong current password showed no message.
- A personal access token asked to expire in 0 or a negative number of days was issued with no
  expiry.
- "Send password reset email" in the admin console reported a failure after sending the mail.
- The web container's health check was counted as about 8,600 page views a day. It now uses
  `/healthz`, which is not counted.
- Export links opened without a session redirected to the container's internal address.
- A refused form lost everything that had been typed and did not mark the field at fault.
- Matrices in lessons rendered with their columns run together and brackets one line tall.
- An audit log filter time written with an offset other than UTC (`since=…+09:00`) matched the
  wrong rows on SQLite, which compares stored times as text. Filter times are converted to UTC
  before the query.
- `rc api serve` no longer lets uvicorn rewrite the caller's address from `X-Forwarded-For`; the
  app applies `RC_API_TRUSTED_PROXIES` itself. With both active, a web tier on the same host
  looked like the browser it was speaking for.
- Web SEO: the English version of a page (`?lang=en`) is now its own canonical URL. It pointed at
  the Korean address, which tells a search engine the English text is a duplicate, so English
  queries could not find the site.
- Web SEO: an unknown module or lesson answers HTTP 404 and `/lessons/{id}` answers 308. Both used
  to answer 200 (a not-found screen, a client-side redirect).
- Web SEO: descriptions no longer show TeX source. A summary such as `$\Phi(-r/2)$` reached the
  meta description, the share preview and JSON-LD with its dollar signs and backslashes; it is
  now plain text (`Φ(-r/2)`).
- Web SEO: crawlers always get `<title>`, the description, the canonical link and the robots tag
  inside `<head>`. For Googlebot and the KakaoTalk scraper a cold request for a lesson had none
  of them there, because Next streamed the metadata into the body.
- Web SEO: `og:locale` follows the language the page is rendered in (`ko_KR` / `en_US`); the
  English alternate used to say `ko`. The sitemap lists `/` and no longer lists the default
  course's roadmap twice.

- `docker-compose.yml` passed `RC_PUBLIC_CONTENT` to neither service and gave the web no
  `RC_PUBLIC_URL`, so setting them in `.env` did nothing to the deployment that actually runs
  — publishing stayed off and canonical links and the sitemap pointed at `localhost`. Both
  values now reach both services, with a test over the compose file so it cannot silently
  regress.

### Changed
- Error messages from the API follow the reader's language. Refusals such as a wrong password,
  an address that is already registered or an expired link used to appear in English on a
  Korean screen; each now carries a stable `code` in the problem body and a localized `detail`.
- "Keep me signed in" now does something: without it the session cookies end when the browser
  is closed. The server-side session expires by the same rules either way.
- A quiz is graded only when every question is answered. Answering one question out of three
  used to be scored as 100%. The result shows the chosen answers in words and renders formulas
  in the correct answer.
- The weekly report can show earlier weeks (`/reports?week=2026-W47`, with previous/next links).
- Lesson titles replace internal ids in the review deck, the running timer, the resource list
  and the "recommended next" message; CLI commands in lesson text and reports link to the
  matching screen.
- Progress and study-time figures agree between screens (stage progress, overall progress,
  minutes on the dashboard and in reports).
- Review, reports and quizzes send an anonymous reader to the login screen instead of saying
  the page could not be loaded. The admin console answers 403 and a report for an unknown
  module answers 404.
- The audit CSV starts with a byte-order mark so that Excel opens Korean text correctly.
- The service runs in Korea Standard Time (`RC_TIMEZONE`, default `Asia/Seoul`; RUNBOOK §8
  "시간대"). Every container sets `TZ`, PostgreSQL logs and displays in that zone, API log lines
  carry `+09:00`, and every date and time on screen is shown in it. A day now begins at local
  midnight for visit counts, the sign-up trend, weekly reports, study streaks, review due dates
  and the daily traffic chart; it used to begin at 09:00 KST (UTC midnight). Stored times are
  absolute instants and are unchanged, as are the times in API responses.
- Backup files are named with local time and its offset (`rc-20261122T020000+0900.dump`) and the
  deploy and restore-drill logs use the same form. Existing `…Z.dump` files restore as before.
- The audit CSV export writes `at` in the service's time zone, and the audit date filter in the
  admin console selects whole local days.
- C4 lessons `c4-pontryagin-indirect`, `c4-dp-lqr-lqg` and `c4-ilqr-ddp` cite their papers through
  the course registry (`papers[]`) instead of article resources, use the `paper` and
  `reproduction` activity kinds, and the C4 module level is `연구`.

- SEO. With `RC_PUBLIC_CONTENT=1` (ADR 0016) the curriculum is readable without a session and
  the pages that hold it become indexable: per-page title and description, canonical URL,
  `hreflang` for ko/en plus `x-default`, OpenGraph and Twitter cards, `sitemap.xml` covering
  every course, module and lesson in both languages, a `robots.txt` that keeps crawlers out
  of personal and operator pages, and JSON-LD (`Course`, `LearningResource`,
  `BreadcrumbList`). `noindex` stays the default for the whole app, so a page has to ask to
  be indexed and only gets it where content is actually published.
- The UI language can be pinned with `?lang=en`. The URL carries no locale segment, so the
  English version of a page had no address of its own — which `hreflang` and a sitemap both
  need. `?lang=` overrides the cookie for that request; the canonical URL stays the bare path.
- Web: an anonymous reader on a published page is no longer redirected to the login screen
  when the page asks for their progress — having none is an answer, not an error. A signed-in
  reader whose session expired is still redirected.

- `rc validate` gains rule 12: a link in a lesson body (or in a translation of it) must be an
  http(s) URL, an anchor, or a relative path to an asset — never another lesson's `.md` file,
  which the generated site lays out elsewhere and so turns into a dead link. Write the lesson
  id in backticks instead.
- `rc site build --strict` fails on any mkdocs warning, and the verification gate and CI now
  use it. Without it a link to a page that does not exist only warned and the build still
  exited 0, so broken lesson links reached a green CI run. `scripts/harness/check.sh` also
  runs `rc validate` and the strict build now, which it never did.
- Nothing in a course is locked any more (ADR 0015). Prerequisites are advice about order:
  every lesson can be opened, started and completed at any time, which the core always
  allowed — only the display pretended otherwise. `rc next` now ranks instead of filtering,
  the `[-]` / `▨` / 🔒 markers are gone, and the lesson screen lists unfinished prerequisites
  as links. `LessonState.locked` stays in the API, always false and deprecated; read the new
  `missing_prerequisites` instead.

### Fixed

- The English build showed Korean in places that had no translation at all: course and
  module titles, activity titles, resource notes, quiz questions, both report renderers,
  quiz type labels, stage names, duration strings and account e-mails. All of them now
  follow the requested language and fall back to Korean only where no translation exists.
- Web: the UI language never reached the API, so picking English left every title, summary,
  report and stage chip in Korean. The API client now sends the reader's locale, and the
  stage chips and roadmap headings show the translated label instead of the stored level id.
- `GET /api/v1/progress/status`, `/progress/next`, `/resources`, `/search` and both report
  endpoints ignored `Accept-Language` and always answered in Korean. `/search` now also
  searches the text of the requested language, so an English reader can find a lesson by
  its English title.


- `GET /api/v1/auth/providers`: the external logins configured through `RC_OIDC_PROVIDERS`
  (id, display name, type and the URL that starts the flow), so the sign-in screen can offer
  a button per provider. Unauthenticated, and it never returns client secrets or role maps.
- Web: external-login buttons on the login and sign-up screens, and a "connect" button per
  unlinked provider in the profile's external-logins section. Nothing is shown when the
  deployment has no provider configured.
- Web: a module report screen (`/reports/modules/{module_id}`), linked from the weekly report
  and from the module overview.
- Web: quiz explanations are rendered with the lesson Markdown pipeline (KaTeX, code, GFM and
  the same sanitiser) instead of being printed as their Markdown source.
- `email_verification` (`unavailable` | `pending` | `verified`) on the sign-up response,
  `GET /api/v1/me` and the admin user list. A server with no SMTP configuration can never
  deliver the link, so clients stop telling the reader to check an inbox: the web shows no
  verification banner and no resend button, and sign-up says the account is ready.
- `POST /api/v1/auth/resend-verification`: mail the verification link again to the signed-in
  account (session only, so there is nothing to enumerate; 503 without SMTP). The previous
  link stops working. The web offers it on the profile and verify-email screens while the
  state is `pending`.
- `RC_AUTH_REQUIRE_VERIFIED_EMAIL` (default `0`): with `1`, an account whose address is not
  confirmed can sign in and read but gets 403 on learning-data writes and PAT creation.
  Setting it without SMTP configured refuses to start, since nobody could get past it.
- `rc api send-test-email <address>`: send one message through the configured SMTP server to
  check the settings. Writes nothing to the database.
- Web: security headers on every page response — a nonce-based `Content-Security-Policy`
  (`strict-dynamic`, `frame-ancestors 'none'`, no `unsafe-eval`), `X-Content-Type-Options`,
  `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `Cross-Origin-Opener-Policy`,
  and `Strict-Transport-Security` only when the request arrived over HTTPS.
- `docs/adr/0013-signup-policy.md` (proposed, not implemented): `RC_AUTH_SIGNUP`
  (`open` | `closed` | `invite`) and how invitations would work.
- `scripts/perf/api_load.py` reports the machine's CPU count and load average, and warns when
  the control endpoint (`healthz`, which does no work) is itself slow — that is the signal
  that a run measured a busy machine rather than the API, which is otherwise easy to read as
  a performance regression. `docs/operations/perf-baseline.md` and `lighthouse.md` gain a
  second dated measurement, taken with two courses and 53 lessons.
- Web: a course switcher. With more than one course the roadmap shows a tab per course and
  the dashboard a progress row per course, each linking to that course's roadmap. The
  selection travels in `?course=`, so it works without JavaScript and can be bookmarked.
  Until now `RC_DEFAULT_COURSE_ID` was the only way to pick a course, which left a second
  one (the research track) with no way in at all. A single-course deployment is unchanged.
- ` ```problemset ` blocks: a lesson can carry derivations, proofs, numerical and
  implementation problems that are **not** graded and never become flashcards, unlike quiz
  questions (lesson-standard.md §11-3). `rc validate` gains rule 13 for their structure —
  including that a `numerical` problem must publish both its expected value and a tolerance —
  and warns when a set is outside 4-8 problems or uses fewer than three types. The static
  site and the web lesson screen show the problems with each solution behind a disclosure
  that says whether it is a sketch, a full solution or a rubric; `GET /lessons/{id}` carries
  them as `problems[]`.
- `<lesson>.<lang>.yaml` can translate a paper reference's `note` (`papers: {<id>: "..."}`).
  Only the note: a paper's title, authors and venue are its published bibliography.
- Assigned papers are shown: `GET /lessons/{id}` carries `papers[]` (required reading first,
  with a one-line citation), the static site gets a "필독 논문" section, and the web lesson
  screen lists them in the sidebar. A paper whose link nobody has checked says so.
- A course may carry a `papers.yaml` bibliography that its lessons reference by id
  (ADR 0014): the registry says what a paper is, the lesson decides which papers it assigns,
  whether each is required, and what to read of it. `rc papers <lesson_id>` lists them,
  required reading first, flagging a link that has not been checked. `rc validate` gains
  rule 11 (referential integrity, unique ids, http(s) urls, at least one required reading per
  lesson that assigns papers). A course with no `papers.yaml` is unaffected.
- `rc validate` can now report a **warning**: it prints them, keeps exit code 0, and the API
  and progress service ignore them. Used for a bibliography entry no lesson references yet,
  and for a stale reverse index — both normal while lessons are still being written.
- Content vocabulary for the research track (`lesson-standard.md` §11-2, §11-4, §11-5), all
  additive so the existing lessons validate unchanged: `ActivityKind` gains `paper`,
  `reproduction` and `project`; `ResourceKind` gains `paper`, `dataset`, `code` and `notes`;
  `Level` gains `연구` (`research`). Labels added in ko and en for the CLI, the static site
  and the web.
- `scripts/perf/api_load.py`: measures the read endpoints' latency percentiles with asyncio
  and the `httpx` already in the package (no new dependency). Baseline recorded in
  `docs/operations/perf-baseline.md`: every read endpoint's p95 is under the PRD's 300 ms
  target in both local and server mode, with the slowest at 158 ms.
- `docs/operations/lighthouse.md`: why Lighthouse was not run (not installed; adding it is a
  dependency decision), plus LCP/FCP/CLS measured with the Chromium already present — the
  slowest page's LCP is 420 ms against the PRD's 2.5 s target, CLS 0.
- `scripts/ops/deploy_pull.sh`: pull-based continuous deployment for a single host (deploys only commits with a green CI run, backs up first, rolls back on failure).
- Robotics researcher track: a new course under `curriculum/robotics-research/` with the first
  reference lesson (SO(3)/SE(3) and exponential coordinates) in Korean and English, plus the
  authoring guide `docs/curriculum/AUTHORING_RESEARCH_TRACK.md`. The track design (benchmark of
  graduate courses, 97-lesson blueprint, lesson standard, 134-paper reading list) is under
  `research_notes/연구 트랙 설계/`.
- Research track module C7 (perception and 3D representations), starting with
  `c7-two-view-geometry`: the epipolar constraint and the essential matrix derived from
  coplanarity, the singular-value characterisation of essential matrices proved in both
  directions, the eight-point and five-point algorithms, and the optimality and bias of
  triangulation — with an eight-item problem set, a measured reproduction task (eight- against
  five-point, plus the planar degeneracy) and four open problems, in Korean and English.
- `c7-bundle-adjustment`: the sparse normal equations of the reprojection error, the Schur
  complement proved exact through the block LDL factorisation and Sylvester's law of inertia,
  the seven gauge generators, and the solvability of self-calibration with its critical motion
  sequences. The reproduction task converges a Schur-complement LM bundle adjuster on the public
  BAL `problem-49-7776` and matches measured reference costs.
- `c7-robust-fitting-ransac`: the RANSAC iteration count derived from the hypergeometric
  distribution (and why the $w^m$ form is optimistic), the gap between what that formula
  guarantees and what RANSAC delivers, the inlier threshold as a $\chi^2$ quantile, and branch
  and bound for globally optimal maximum consensus checked against exhaustive enumeration.
- `c7-learned-correspondence-slam`: the gradient of a differentiable bundle adjustment layer by
  implicit differentiation (and the measured bias of the Gauss-Newton Hessian shortcut), the
  SuperGlue matching layer derived as entropic optimal transport, the scale ambiguity of joint
  depth-and-pose learning as a one-dimensional null space, and an experiment separating noise from
  structural ambiguity as the cause of correspondence failure.
- `c7-neural-fields-3dgs`: the volume rendering integral from the absorption-emission model, a
  proof that NeRF's alpha-compositing discretisation is exact for piecewise-constant density (with
  the measured second-order error for smooth density), the spectral bias of positional encoding
  quantified through Gram eigenvalues, and the measured valid regime of the affine (EWA) projection
  used by 3D Gaussian splatting.
- `c7-event-tactile-sensing`, completing module C7: the event generation model as a threshold
  crossing of log intensity (and why its rate form overpredicts for short windows), contrast
  maximisation with a measured angular-velocity estimate on the public ECD dataset, the
  non-convexity of that objective, and GelSight photometric stereo with the measured failure
  condition of volume-based force estimation.
- Research track module S1 (SLAM and spatial AI) under
  `curriculum/robotics-research/s1-slam-spatial-ai/`, starting with `s1-vio-systems`: the filter
  and optimisation architectures of VIO, a proof that MSCKF's null-space projection is exact
  marginalisation, the four unobservable directions of monocular VIO with the measured weak
  observability of roll, pitch and scale, and a Monte Carlo showing that a filter pays in the tail
  of the consistency statistic rather than in RMSE.
- `s1-loop-closure-lifelong`: the precision-recall law of place recognition (with the measured
  threshold growing linearly in the log of the database size), the factor-of-22 damage a single
  false loop does to a least-squares pose graph, the contamination rates at which Huber and GNC
  give out, and why map sparsification is naturally overconfident, measured in KLD.
- `curriculum/robotics-research/papers.yaml`: the course paper registry (ADR 0014) with the
  eleven papers the C7 lessons assign; both C7 lessons reference them through front-matter
  `papers:` and `rc papers <lesson_id>` lists them.
- Research track module C5 (state estimation): the `c5-factor-graphs-map` lesson in Korean and
  English — MAP on a factor graph proved equivalent to nonlinear least squares, Gaussian variable
  elimination derived as the Schur complement, the Kalman filter re-derived from the normal
  equations, and a two-lap SE(2) pose graph reproduction task with machine-checkable acceptance
  criteria.
- Research track module C5: the `c5-sparsity-isam` lesson in Korean and English — the fill-path
  theorem proved in both directions, the locality of iSAM2's incremental re-elimination derived
  from the Bayes tree's conditional factorization, incremental QR by Givens rotations with its
  cost shown to be distance in the variable order, and KL-optimal sparsification derived as
  moment matching. Adds five verified papers to the C5 block of the reading-list registry.
- Research track module C5: the `c5-manifold-estimation` lesson in Korean and English — the
  retraction invariance of on-manifold Gauss-Newton proved, the Ad transformation between left and
  right uncertainty derived, the group-affine cancellation that makes the invariant error dynamics
  autonomous derived line by line, and a 3000-run Monte Carlo NEES comparison of a standard EKF
  against an invariant EKF on SE(3).
- Research track module C5: the `c5-imu-preintegration` lesson in Korean and English — the
  preintegration identity proved exactly for the stated discretization (including the gravity
  bookkeeping that makes it work), the bias-relinearization Jacobian recursions and the
  nine-dimensional noise covariance derived, and the two-fold scale/gravity ambiguity of monocular
  visual-inertial fusion under constant acceleration derived in closed form and confirmed
  numerically.
- Research track module C5: the `c5-observability-consistency` lesson in Korean and English — the
  Hermann-Krener rank condition, the four-dimensional unobservable subspace of monocular
  visual-inertial estimation derived from its invariance group, the mechanism by which an EKF's
  linearization points break the null space, and FEJ shown to turn on choosing between two
  algebraically identical Jacobian expressions. The reproduction task measures all of it by
  numerical rank, and reports honestly that null-space preservation did not improve NEES in either
  simulated setting.
- Research track module C5: the `c5-robust-global-estimation` lesson in Korean and English — the
  M-estimator / IRLS equivalence proved and verified numerically, influence functions used to
  separate bounded from redescending kernels, and a four-line proof of the global optimality
  certificate for SO(2) rotation synchronization (SE-Sync in miniature) together with the measured
  fact that its tightness survives noise but not outliers.
- Research track module C5 is complete (six lessons) and converted to the landed schema
  (AUTHORING §8-1): must-read papers moved from `resources[]` into front-matter `papers[]`
  referencing the course registry, 23 entries added to the registry's C5 block (all with URLs
  verified against the Crossref or arXiv API), activity kinds `paper` and `reproduction`, and
  `level: 연구` on the module.
- Research-track module C3 (nonlinear and robust control) under
  `curriculum/robotics-research/c3-nonlinear-robust-control/`: lesson 1, Lyapunov stability and
  ISS, in Korean and English — the Lyapunov theorem, its converse for exponential stability and
  LaSalle's invariance principle as proof sketches, the ISS estimate derived from an
  ISS-Lyapunov function, and a sum-of-squares certificate for a region of attraction with a
  numerically checkable reproduction task.
- Research-track lesson 2 of module C3, feedback linearisation and controllability, in Korean and
  English: the full feedback-linearisation condition reduced to the Frobenius theorem, zero
  dynamics and the forward-point output of a differential-drive robot, the second-order Lie
  bracket motion derived from a composition of flows, the chained form with steering by sinusoids
  ($\Delta z_3 = \pi ab/\omega^2$), and Brockett's obstruction shown concretely.
- Research-track lesson 3 of module C3, contraction theory and incremental stability, in Korean
  and English: the contraction condition derived from virtual displacements up to finite
  Riemannian distance, constant metrics found by LMI where the Euclidean metric certifies nothing,
  the disturbance tube $\sup\lVert\Theta d\rVert/\lambda$, why a control contraction metric is
  convex in the dual metric, and a reproduction task that measures how conservative the
  certificate is (certified 0.49 against a measured rate of 1.00).
- Research-track lesson 4 of module C3, passivity, energy shaping and impedance control, in
  Korean and English: manipulator passivity from the skew symmetry of $\tfrac12\dot M - C$,
  the passivity theorem for feedback interconnections, energy shaping with damping injection, and
  a closed-form per-cycle energy of a sampled virtual wall that reproduces the Colgate-Schenkel
  passivity condition in the limit and quantifies where it is conservative.
- Research-track lesson 5 of module C3, adaptive control and persistent excitation, in Korean and
  English: the regressor of a two-link arm built column by column, the Slotine-Li Lyapunov
  derivation of $\dot V = -s^\top K_D s$, persistent excitation as the necessary and sufficient
  boundary of parameter convergence, and a reproduction task where tracking reaches $5\cdot10^{-14}$
  at a set-point while the inertial parameters stay 34% wrong.
- Research-track lesson 6 of module C3, CBF and CLF safety filters, in Korean and English,
  completing the module: forward invariance proved with the comparison lemma, the closed form of
  the minimum-intervention QP from the KKT conditions, the exponential CBF chain for a
  relative-degree-two constraint, and a reproduction task that measures how input limits break the
  guarantee (95 of 189 runs saturate at $u_{\max}=2$, worst $h = -0.138$).
- Research-track module S3 (legged and underactuated robots) under
  `curriculum/robotics-research/s3-legged-underactuated/`: lesson 1, hybrid dynamics and limit
  cycles, in Korean and English — the Poincare map and orbital stability of a periodic orbit with
  impacts, the saltation matrix derived from the event-time perturbation, the compass-gait
  equations of motion and impact map derived from scratch, and a reproduction task whose numbers
  (limit cycle, eigenvalues, energy balance, second-order saltation check) cross-validate each
  other. It is the first lesson to use the structured ```problemset block.
- Research-track lesson 2 of module S3, hybrid zero dynamics and gait generation, in Korean and
  English: virtual constraints and the zero dynamics surface, impact invariance as the boundary
  conditions of a Bezier virtual constraint, the one-dimensional affine return map that follows
  from the hip torque having no moment about the stance foot, and a reproduction task in which the
  reduced model's predicted rate matches the four-state model's dominant Poincare eigenvalue to
  eight digits.
- Research-track lesson 3 of module S3, centroidal dynamics and MPC walking, in Korean and
  English: the centroidal dynamics derived from whole-body Newton-Euler (and verified on a
  point-footed walker while the hip torque is swung), the CoP/ZMP equation, the LIPM and the DCM in
  closed form, and a reproduction task that measures the recovery limit $\omega p_{\max}$ and shows
  an MPC without a terminal constraint reporting "optimal" with a 39 m terminal DCM.
- Research-track lesson 4 of module S3, whole-body control and hierarchical QPs, in Korean and
  English: the null-space projection hierarchy and its priority-preservation proof, the equivalence
  with a lexicographic QP for equality tasks, measurements showing that clipping a projection
  solution destroys the priority while a weighted sum leaks in proportion to its weight, and what a
  lexicographic QP guarantees when the top level is infeasible.
- Module C3 moved onto the schema the paper registry added (AUTHORING §8-1): its 22 papers are
  registered in `curriculum/robotics-research/papers.yaml` (all with verified URLs), each lesson
  references them from front-matter `papers[]` with `required`/`role` and a language-neutral
  locator, the activity kinds `paper` and `reproduction` replace the interim `reading`/`exercise`,
  tool resources use `kind: code`, and the module level is `연구`.
- Research track module C2 (multibody dynamics) under
  `curriculum/robotics-research/c2-multibody-dynamics/`: six research-grade lessons in Korean and
  English on spatial vector algebra, RNEA, CRBA/ABA, constrained dynamics, contact dynamics and
  the derivatives of dynamics with inertial parameter identification. Each lesson derives its key
  results at depth D2-D3, sets 4-8 problems, assigns 2-4 verified must-read papers and a
  reproduction task with machine-checkable acceptance criteria.

### Fixed

- Web: lesson formulas reached the reader as raw TeX. A `$$` display block written with
  content on the marker line — how every "핵심 수식" section is written — was parsed as a math
  fence with meta, so the block never closed and swallowed the rest of the lesson. The
  Markdown normaliser now puts every `$$` marker on its own line; 12 of the 40 lessons were
  affected. The static site (`rc site build`, pymdownx.arithmatex) was never affected.
- Web: lesson `summary`, `objectives` and flashcard sides printed their inline TeX as text;
  they now go through the same Markdown pipeline. Resource notes deliberately do not — their
  `$` are prices.
- Web: the lesson body repeated the study-method section (the card above already shows it) and
  printed the quiz block's YAML source as a code block. Both sections are now dropped from the
  body, as `rc site build` already did in its own way.
- Web: long formulas, code blocks and wide tables scroll sideways but could not be reached
  without a mouse (axe `scrollable-region-focusable`); they now carry `tabindex="0"`.
- CI: restore-drill teardown now passes the required compose secrets; e2e jobs pin `ubuntu-24.04` for the Playwright browser install; generated web API types are back in step with the OpenAPI schema.

## [0.2.0] - 2026-11-12

### Added

#### Core (Phase 1)

- `rc` CLI (Typer): `version`, `validate`, `show`, `resources`, `status`, `start`, `stop`,
  `log`, `done`, `next`, `roadmap`, `progress export|import`, `report weekly|module`,
  `site build`.
- Content model: Course > Module > Lesson > Activity as Markdown with YAML front matter, with a
  loader and validator (required fields, unknown prerequisites, prerequisite cycles, resource
  URL format).
- Robotics expert course content under `curriculum/robotics-expert/` (modules M1–M6, M8, M10 so
  far), with "이 단계 공부법" sections and resource lists for each lesson.
- Local progress tracking in SQLite (`.rc/progress.db`) behind a store interface, with JSON
  export and import.
- Weekly and per-module Markdown reports.
- Lesson translations as sibling files (`<lesson>.<lang>.md`, ADR 0012): text only, so the
  prerequisite graph stays single-sourced. The loader, `rc validate`, the API
  (`Accept-Language`, with `lang` and `available_languages` in the response) and
  `rc site build --lang` use a translation when there is one and fall back to the language the
  lesson was written in.
- Accessibility checks for the generated site (document language, heading levels, table
  headers, skip link, image alt text, contrast of the project's own colours); the
  in-progress status colour was darkened to meet WCAG AA on white.
- Message catalogues for Korean and English (`src/robotics_curriculum/i18n/locales/*.yaml`,
  ADR 0011): the CLI picks a language with `--lang` or `RC_LANG`, `rc site build --lang`
  translates the site chrome, and the API localizes problem titles from `Accept-Language`.
  Lesson content stays in the language it was written in. A few CLI lines that were English
  regardless of locale (the unlock list, the prerequisite warning) are now Korean by default.
- Quizzes and spaced repetition (P1-2): ` ```quiz ` blocks in lesson bodies (single, multiple,
  true/false, short answer) validated by `rc validate`; `rc quiz <lesson>` grades in the
  terminal and turns wrong answers and `concept` questions into flashcards; `rc review`
  schedules them with SM-2 (ADR 0005); progress schema v2 (cards, card_state, reviews,
  quiz_attempts, quiz_runs, activity_progress) included in JSON export/import; quiz accuracy
  and review counts in the weekly report and `rc status`; quiz questions on lesson pages with
  answers folded into `<details>`.
- Prerequisite roadmap with done / in-progress / locked states and next-lesson recommendation.
- Offline static study site (MkDocs Material): dashboard, roadmap, module and lesson pages,
  resource library.
- Engineering scaffolding: Apache-2.0 license for code, CC BY 4.0 for curriculum content,
  contribution guide, Code of Conduct, security policy, issue and PR templates, Dependabot,
  GitHub Actions CI and release workflows, strict mypy, coverage gate, pre-commit hooks,
  Dockerfile and Compose file.
- Development harness: graph spec (`harness/graph.md`), roadmap state (`harness/roadmap.yaml`),
  verification gate (`scripts/harness/check.sh`), Claude Code hooks, agents, and workflows
  (see `docs/HARNESS.md`).
- Architecture decision records 0001–0004 (Phase 1 stack, harness, SQLite progress store,
  MkDocs static site).
- `rc --verbose/-v` turns on debug logging to stderr; library modules log through the
  standard `logging` module (never personal data such as study notes).
- `rc progress import --allow-unknown` and `rc site build --force`: escape hatches for the
  new input and output-path checks listed under Security.

#### Server and web (Phase 2)

- HTTP API (`rc api serve`, optional extra `api`): FastAPI app under `/api/v1` for courses,
  modules, lessons, resources, progress (status, next, start, stop, log, done), weekly and
  module reports, and progress export; `/healthz`, `/readyz`, `/version`; RFC 9457
  problem+json errors, `X-Request-ID`, JSON logs, and an OpenAPI snapshot test.
- PostgreSQL progress store for server mode (optional extra `postgres`: SQLAlchemy 2 Core +
  psycopg 3) with Alembic migrations, backend selection via `RC_DATABASE_URL` (unset keeps the
  local SQLite file), `rc progress transfer` to move local SQLite or JSON-export data into
  PostgreSQL (merge without duplicates, `--user-id` to assign a server account), and a `db`
  service (PostgreSQL 16) in the Compose file.
- Server-mode accounts (`RC_AUTH_MODE=server`): email + Argon2id passwords, login throttling,
  server-side session cookies with CSRF protection, personal access tokens with scopes, roles
  learner/author/admin, per-user progress, password reset and email verification by mail,
  account export and deletion, admin user management and an audit log; security headers.
- OIDC login (Authorization Code + PKCE) for providers listed in `RC_OIDC_PROVIDERS`, with
  account linking and `/api/v1/me/identities`; GitHub login (`"type": "github"`) and IdP group
  to role mapping (`role_claim`, `role_map`; raises roles only).
- `GET /api/v1/roadmap` (level → module → lesson states and progress) and `GET /api/v1/search`
  (lessons and resources).
- Prometheus metrics at `/metrics` (request counts, latency histogram, in-flight requests,
  database pool usage); `RC_API_METRICS=0` turns it off.
- `docs/api/openapi.yaml` is generated from the served API (plus `x-planned` routes) and a test
  keeps them identical.
- Web frontend (`web/`, Next.js App Router): sign-in, dashboard, roadmap, lesson reader with
  maths and highlighted code, resource library, quiz and review screens, reports and account
  export, in Korean and English. It calls the API only and ships as its own container image.

### Changed

- Engineering rules (`.claude/rules/engineering.md`): coverage gate is core-library line+branch
  80%; every commit carries a DCO `Signed-off-by`; large design changes go through `docs/rfcs/`
  then an ADR; only Apache-2.0-compatible dependencies; CHANGELOG is mandatory; server-mode
  observability and OWASP ASVS L2 checks; multi-session agent operating rules.
- Roadmap acceptance criteria for P1-2 and P2-1 … P2-5 now cite PRD appendix C IDs; P1-2 uses
  SM-2 and depends on P1-5, P2-1 depends on P1-2.
- `docs/HARNESS.md` documents how hooks behave in worktree sessions.
- Container and compose stack cover server mode end to end: a `web` target builds the Next.js
  standalone bundle (unprivileged user, read-only root, node-fetch health check) and the `web`
  service waits for a healthy api. `scripts/smoke.sh` brings up db -> migrate -> api -> web and
  checks that the screens render.
- `scripts/harness/check.sh`: `--quick` (the Stop hook) skips the node stack, and a full run
  installs `web/node_modules` when it is missing instead of failing with exit 127.
- CI runs the frontend checks for real on Node 22 and 26, fails on API client types that drift
  from `docs/api/openapi.yaml`, and runs two Playwright + axe end-to-end legs: smoke against a
  local-mode API and the full sign-up-to-report journey against a server-mode one, each keeping
  its own report as an artifact.

### Fixed

- The package version had two sources (`pyproject.toml` and `__version__`), so `rc version`
  and `/version` could disagree with the release. `__version__` now comes from the installed
  distribution and a test holds it to `pyproject.toml`.

### Security

- Second server review round: a mail server failure no longer turns sign-up or a reset request
  into a 500 (the undeliverable token is discarded and the failure audited); the local-mode bind
  guard moved into the app factory, so running the app with uvicorn directly cannot bypass it;
  `id_token`s with several audiences need an `azp` naming this client; OIDC now requires
  `RC_AUTH_SECRET` instead of falling back to a per-process key; `/metrics` can require a bearer
  token via `RC_API_METRICS_TOKEN`; `rc api promote-admin` refuses an unverified address unless
  `--force` is given.
- Server review fixes (`docs/reviews/2026-11-11-server-review.md`): the compose stack and the api
  image run in server mode with required secrets and no default database password; local mode
  refuses non-loopback binds; the bootstrap admin is promoted only after email verification
  (or with `rc api promote-admin`); password-reset requests are rate limited and only the newest
  reset link works; error bodies no longer show server paths; denied requests and admin reads
  are audited; account deletion anonymizes the user's audit entries; api containers run with a
  read-only root, no capabilities and `no-new-privileges`.
- Vendored KaTeX updated from 0.16.11 to 0.19.1, out of the range of GHSA-238p-pmpm-9mq7
  (>=0.11.0 <0.18.2). Every shipped file is now pinned by sha256 in
  `src/robotics_curriculum/site/assets/katex/MANIFEST.sha256` and checked by a test;
  `scripts/ops/vendor_katex.sh` re-vendors and refreshes both.
- `npm audit --omit=dev --audit-level=high` runs over the frontend lockfile in
  `.github/workflows/security.yml`, with the dev toolchain audited without blocking.
- `.github/workflows/security.yml`: CodeQL (Python, security-and-quality) and pip-audit of the
  locked runtime dependencies on every PR, on pushes to `main`, and weekly. Any known
  vulnerability in a runtime dependency fails the job.
- The static site no longer passes curriculum text through to HTML unchanged: titles,
  summaries, objectives, tags, activity and resource names are HTML-escaped (including the
  nav titles and `site_name` in `mkdocs.yml`, which the theme writes out verbatim), rendered
  pages are cleaned with an `nh3` allowlist, and each page carries a Content-Security-Policy
  meta tag. A resource `url` that is not `http(s)` is shown as plain text instead of a link.
- `rc site build` refuses an `--out` or `--src` directory that holds files it did not write
  (no `.rc-site` marker), and refuses the working directory, the repository root and `$HOME`
  outright; `--force` allows the first case. mkdocs empties both directories, so a mistyped
  path used to delete unrelated files.
- Content loading rejects files that leave the content root once symlinks are resolved,
  reports unreadable or non-UTF-8 files instead of raising, checks prerequisite cycles
  iteratively (a long chain used to exhaust the stack) and requires ids to be unique across
  courses. Every command validates the curriculum, not only `rc validate`.
- `rc progress import` validates the export against the database invariants and refuses
  lesson ids that are not in the curriculum unless `--allow-unknown` is passed; study
  durations are capped at one day. The progress database is opened in WAL mode with a busy
  timeout, its files are created owner-only, and storage failures (such as a locked
  database) are reported as `error: ...` instead of a traceback.
