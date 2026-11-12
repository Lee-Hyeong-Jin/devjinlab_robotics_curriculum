# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- Research-track module `c8-decision-making-learning-theory` (C8, decision making and
  learning theory), research-grade lessons in Korean and English with derivations, problem
  sets, must-read papers, reproduction tasks and open problems. Lessons so far:
  `c8-mdp-pomdp-bellman`, `c8-policy-gradient`, `c8-value-based-rl`,
  `c8-model-based-world-models`, `c8-imitation-learning`,
  `c8-offline-rl`,
  `c8-control-as-inference`,
  `c8-generalization-sim2real`.

### Changed

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
