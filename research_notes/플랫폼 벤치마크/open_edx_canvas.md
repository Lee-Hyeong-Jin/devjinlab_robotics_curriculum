# Open edX · Canvas LMS 벤치마크 프로필 (2026-11-11 기준)

> 소규모 Markdown-first 커리큘럼 플랫폼(모듈→레슨, frontmatter, 진도 추적, 인증/API/CI)의 설계 벤치마크. URL은 실제 fetch했거나 fetch 페이지에 등장한 것만 사용. 본문 대신 검색 스니펫만 확인한 항목은 "(스니펫)"으로 표기.

## KQ1. 인증·권한 모델 (로그인, 역할/권한, API 인증, 멀티테넌시)

### Takeaway
Open edX는 "LMS가 유일한 IdP·OAuth2 서버"(OEP-42) 원칙 아래 OAuth2 + 비대칭 JWT를 표준으로 하며, 코스 역할은 Staff/Limited Staff/Admin/Data Researcher에서 Verawood부터 openedx-authz 기반 RBAC(waffle flag)로 이행 중. Canvas는 계정→하위계정 트리 위에 base role type을 상속한 커스텀 역할과 `enabled/locked/applies_to_descendants` 속성의 권한 사전을 두고, 로그인 공급자 12종, API는 RFC-6749 OAuth2(1시간 토큰+refresh)와 LTI 1.3 client-credentials.

### Cited Findings
- Open edX: "The LMS will act as the sole identity provider and OAuth authorization server for all other surrounding IDAs"; 권장 인증은 OAuth 2.0 + JWT(Django OAuth Toolkit); "All JWTs will be signed using 'asymmetric' cryptographic keys"(일부 미완); "All usage of Bearer tokens in Open edX has been deprecated"; DRF에서 `JwtAuthentication`(edx-drf-extensions)과 `SessionAuthentication` 지원; 서버 간 `OAuthAPIClient`, MFE는 `@edx/frontend-platform/auth` + 공유 JWT 쿠키; TLS 필수; 소셜/SAML 로그인은 외부 ID를 Open edX 계정에 연결하는 방식 — [OEP-42](https://open-edx-proposals.readthedocs.io/en/latest/best-practices/oep-0042-bp-authentication.html)
- (스니펫) JWT 요청은 `/oauth2/access_token/`에 `token_type=JWT`, 기본 1시간 만료(`JWT_ACCESS_TOKEN_EXPIRE_SECONDS`), 헤더 `Authorization: JWT <token>`, IdP 구현은 `oauth_dispatch` — [Confluence](https://openedx.atlassian.net/wiki/x/WYDFxw)
- Open edX 레거시 코스 역할: **Staff**(Studio+인스트럭터 대시보드, 개별 성적 수정, 등록/해지, 인증서), **Limited Staff**("has no access to Studio"), **Admin**(Staff 전체 + 전원 성적 수정 + Staff/Admin/베타테스터/Discussion 역할 관리), **Course Data Researcher**(Data Download). 기타 Beta Tester, Discussion Admin/Moderator, Community TA, Group Community TA. 신규 opt-in 시스템의 **Course Admin**(+Roles and Permissions 콘솔), **Course Staff**(Studio 전 수명주기) — [Course Team Roles](https://docs.openedx.org/en/latest/educators/references/course_development/course_team_roles.html)
- Verawood: openedx-authz 기반 RBAC가 레거시 `CourseAccessRole` 대체; waffle flag `authz.enable_course_authoring`(기본 off, 코스/조직/전역 3단계); 마이그레이션 `authz_migrate_course_authoring`(`--course-id-list`/`--org-id`/`--delete`); `ENABLE_AUTOMATIC_AUTHZ_COURSE_AUTHORING_MIGRATION` 기본 False; Willow에서 기본 on, Xylon(2027-06)에서 레거시 제거 예정 — [Verawood Dev&Op Notes](https://docs.openedx.org/en/latest/community/release_notes/verawood/dev_op_release_notes.html)
- Open edX 멀티사이트: "By default, an Open edX installation has one site... You can configure multiple sites"; 도메인은 Django admin에서 설정, 사이트별 독립 설정·테마·노출 코스 — [Configuring Sites (Ulmo)](https://docs.openedx.org/en/ulmo/site_ops/install_configure_run_guide/configuration/sites/index.html); edx-organizations: "Organizations represent the entities responsible for creating and publishing Courses" — [README](https://github.com/openedx/edx-organizations/blob/master/README.rst); (스니펫) eox-tenant 플러그인, Tutor+MFE 다중 도메인은 공식 문서 부족 포럼 보고 — [discuss](https://discuss.openedx.org/t/configure-multi-tenant-connect-multiple-site-domain-to-the-same-backend/17444)
- Canvas `auth_type`: `apple, canvas, cas, clever, facebook, github, google, ldap, linkedin, microsoft, openid_connect, saml`; JIT provisioning "Valid for all providers except Canvas"; `federated_attributes`(`attribute, provisioning_only, autoconfirm`); SSO 설정 `auth_discovery_url`, `unknown_user_url`, `saml_entity_id`(기본 `<host>/saml2`) — [Authentication Providers API](https://canvas.instructure.com/doc/api/authentication_providers.html)
- Canvas 역할: base role type `AccountMembership, StudentEnrollment, TeacherEnrollment, TaEnrollment, ObserverEnrollment, DesignerEnrollment, CohortLeader`; 커스텀 역할 `POST /api/v1/accounts/:id/roles`(`label`만 필수), 삭제=비활성화("Existing users assigned to the role will continue to function with the same permissions"); `permissions` 사전 항목 `enabled, locked, applies_to_self, applies_to_descendants, readonly, explicit, prior_default`(self·descendants 동시 false 불가); 예 `read_course_content, read_reports, manage_groups, send_messages, manage_lti_add, view_user_logins` — [Roles API](https://canvas.instructure.com/doc/api/roles.html)
- Canvas API: "Canvas uses OAuth2 (specifically RFC-6749)", code 1회용, 2015-10 이후 키의 토큰은 1시간 후 만료 → "must use refresh tokens"; 로그아웃 `DELETE login/oauth2/token`; 수동 토큰은 테스트용, "Applications in use by multiple users MUST use OAuth"; 스코프는 `/auth/userinfo`만 명시; LTI AGS/NRPS는 client credentials grant + public JWK("The JWK must include an alg and use"), RS256 서명 — [OAuth2](https://canvas.instructure.com/doc/api/file.oauth.html)
- Canvas 계정 트리: 루트는 `parent_account_id` null; `GET .../sub_accounts?recursive=true`; 재부모화는 "must be in the same root account"; 설정 `value`+`locked`("Lock this setting for sub-accounts and courses") — [Accounts API](https://canvas.instructure.com/doc/api/accounts.html)

### Inferences
- 양쪽 다 "역할=권한 묶음"이나 Canvas가 권한 단위·계층 상속/잠금까지 세분화돼 있고 Open edX는 이제 RBAC로 이행 중. 소규모 플랫폼은 처음부터 `role → {permission: {enabled, locked}}` + 조직/과정 스코프를 두는 Canvas형이 안전.
- 단일 모놀리스라면 세션 인증 + 외부 OIDC IdP 연동으로 충분; Open edX식 JWT 발급 서버는 서비스 분리 전제라 과함.

### Gaps
- Open edX OAuth 스코프/필터 공식 문서 미확인(OEP-42 본문에 없음; [2018 Confluence](https://openedx.atlassian.net/wiki/spaces/OEPM/blog/2018/08/10/807305448/Architecture+OAuth+Scopes) 본문 미확인). edx-platform `docs/concepts/authentication.rst`는 404.
- Verawood RBAC의 전체 역할명, Canvas 권한 전수 목록 미확인.

## KQ2. 콘텐츠 포맷·모델 (OLX, CC/QTI, LTI 1.3, xAPI/SCORM, Markdown)

### Takeaway
Open edX 정준 포맷은 OLX(XML, `.tar.gz`), 계층 course→chapter→sequential→vertical→XBlock; Markdown은 서드파티 `markdown-xblock`뿐. Canvas는 Page body=HTML, Modules가 항목+완료요건을 묶으며 `common_cartridge(.imscc)/qti/zip` 내보내기, CC/QTI/Moodle 가져오기. LTI 1.3/Advantage는 양쪽 지원(Verawood "LTI Advantage Complete" 인증). SCORM: Open edX Tutor 번들 XBlock(1.2/2004), Canvas는 기관이 켜는 SCORM LTI. xAPI: Open edX event-routing-backends, Canvas는 Caliper 1.1 Live Events만.

### Cited Findings
- OLX는 "XML-based format for building courses"; Studio `.tar.gz` 내보내기/가져오기; CC→OLX 변환기 `cc2olx`; "assumes authors understand XML" — [What is OLX](https://docs.openedx.org/en/latest/educators/olx/what-is-olx.html)
- 디렉터리: `course/` 아래 `course.xml`, `chapter/`(섹션), `sequential/`(서브섹션), `vertical/`(유닛), `html/`, `problem/`, `video/`, `policies/`(`assets.json`, 코스런 폴더의 `grading_policy.json`·`policy.json`), `static/`, `about/`(`overview.html`, `short_description.html`), `info/`(`handouts.html`, `updates.html`); LTI·커스텀 블록은 부모에 인라인 — [OLX Directory Structure](https://docs.openedx.org/en/latest/educators/olx/directory-structure.html); (스니펫) 인라인 정의 구조는 Studio 가져오기 미보장 — [Courseware Structure (Ulmo)](https://docs.openedx.org/en/ulmo/educators/olx/organizing-course/course-xml-file.html)
- markdown-xblock: "[b]ased on the HTML XBlock by OpenCraft", markdown2(extras: code-friendly, fenced-code-blocks, footnotes, tables, use-file-vars; `XBLOCK_SETTINGS["markdown"]`), safe mode 기본 `replace`(인라인 HTML→`[HTML_REMOVED]`); Tutor `OPENEDX_EXTRA_PIP_REQUIREMENTS`에 `markdown-xblock==2.4.1`; advanced module list에 `"markdown"`; Python 3.8+ — [README](https://github.com/citynetwork/markdown-xblock/blob/main/README.md); (스니펫) PyPI 2.4.0, Quince 미동작 보고 — [PyPI](https://pypi.org/project/markdown-xblock/), [discuss](https://discuss.openedx.org/t/markdown-xblock-broken-in-quince/11925)
- xblock-lti-consumer: LTI 1.3 + Deep Linking/AGS/NRPS, LTI 1.1/1.2 Basic Outcomes 1.0, LTI 2.0 Result Service 2.0 — [README](https://github.com/openedx/xblock-lti-consumer/blob/master/README.rst); Verawood 노트 "Verawood Release is LTI Advantage Complete Certified", LTI Block은 `xblocks-core`로 추출 — [Product Notes](https://docs.openedx.org/en/latest/community/release_notes/verawood/feature_release_notes.html), [Dev&Op Notes](https://docs.openedx.org/en/latest/community/release_notes/verawood/dev_op_release_notes.html)
- openedx-scorm-xblock: "Currently supports SCORM 1.2 and SCORM 2004 standard", "comes bundled by default in the official Tutor releases"; 완료는 패키지가 결정(`cmi.core.lesson_status`/`cmi.completion_status`/`cmi.progress_measure`) — [README](https://github.com/overhangio/openedx-scorm-xblock/blob/master/README.rst)
- event-routing-backends: 이벤트를 외부 서비스로 재전송; "Currently work to support xAPI and Caliper event formats is in progress"(OEP-26) — [README](https://github.com/openedx/event-routing-backends/blob/master/README.rst)
- Canvas Page `body`: "the page content, in HTML"; `editing_roles`=`teachers,students,members,public`; `published`(구 `hide_from_students` 폐기), `publish_at`; 리비전 API(`revision_id, updated_at, latest, edited_by, url, title, body`, 되돌리기); `url` 슬러그는 제목 변경 시 바뀜, `page_id:<id>`로 ID 강제 — [Pages API](https://canvas.instructure.com/doc/api/pages.html)
- Canvas Module 항목 `File, Page, Discussion, Assignment, Quiz, SubHeader, ExternalUrl, ExternalTool`; 완료요건 `must_view`(전부), `must_contribute`(Assignment/Discussion/Page), `must_submit`(Assignment/Quiz), `min_score`(Assignment/Quiz), `must_mark_done`(Assignment/Page/AiExperience), `min_percentage`(객체에만); 선수 모듈은 낮은 position 필수("they will be ignored"); `require_sequential_progress`; `requirement_type` `all|one`; 상태 `locked/unlocked/started/completed`+`completed_at`; `PUT .../relock` — [Modules API](https://canvas.instructure.com/doc/api/modules.html)
- Canvas Exports `export_type`: `common_cartridge`(".imscc"), `qti`("Export quizzes... in the QTI format"), `zip`; 상태 `created→exporting→exported|failed`, `progress_url` — [Content Exports](https://canvas.instructure.com/doc/api/content_exports.html); Migrations `migration_type`: `canvas_cartridge_importer, common_cartridge_importer, course_copy_importer, zip_file_importer, qti_converter, moodle_converter`; `selective_import`→`waiting_for_select` — [Content Migrations](https://canvas.instructure.com/doc/api/content_migrations.html); "QTIMigrationTool is required for copying or importing quiz content" — [Production Start](https://github.com/instructure/canvas-lms/wiki/Production-Start)
- Canvas LTI 1.3: "Canvas moved to using Developer Keys to store tool configuration information"; JSON 설정 `title, oidc_initiation_url, target_link_uri, scopes, extensions, public_jwk|public_jwk_url`; JWKS 검증("public keys are environment-specific, but not domain-specific"); AGS 스코프 `lineitem, lineitem.readonly, result.readonly, score`, NRPS `contextmembership.readonly`, Deep Linking `LtiDeepLinkingRequest`; placements `course_navigation, editor_button`; `privacy_level`, `custom_fields`($Canvas.user.id) — [LTI Dev Key Config](https://canvas.instructure.com/doc/api/file.lti_dev_key_config.html)
- Canvas Live Events 형식: "Canvas"(객체별) 및 "Caliper IMS 1.1"(카테고리별) — [Live Events Intro](https://canvas.instructure.com/doc/api/file.data_service_introduction.html); (스니펫) SCORM은 "If your institution has enabled the SCORM LTI" 업로드 가능 — [guide](https://community.instructure.com/t5/Instructor-Guide/How-do-I-import-SCORM-files-as-an-assignment/ta-p/673); (스니펫) "Canvas has very limited support for the xAPI standard... Canvas does not include [an LRS]" — [Developers Group](https://community.canvaslms.com/t5/Developers-Group/Using-xAPI-to-integrate-Articulate-Rise-content/td-p/648872)

### Inferences
- 양쪽 다 "컨테이너 계층 + 리프 아이템, 리프 본문=HTML". Markdown을 소스로 두고 sanitize된 HTML을 빌드 산출물로 분리하면 OLX/CC 변환과 LTI 임베드가 모두 쉬움.
- 상호운용 우선순위: LTI 1.3 Tool(외부 LMS에 임베드) > Common Cartridge 내보내기(Canvas importer·cc2olx 양쪽 경로) > xAPI 방출(LRS 외부화) > SCORM 런타임(가장 무겁고 양쪽에서도 애드온).

### Gaps
- Open edX Caliper 완성도, Canvas SCORM LTI 버전/채점, Canvas QTI 버전(2.1/3.0) 미확인. 1EdTech 스펙 페이지는 호출 예산상 미fetch.

## KQ3. 라이선스·CLA·거버넌스·릴리스

### Takeaway
edx-platform·canvas-lms 모두 LICENSE는 "GNU AFFERO GENERAL PUBLIC LICENSE Version 3, 19 November 2007"(AGPL-3.0); edx-platform엔 edX Inc.의 웹서비스 비파생 해석 문구 추가. 둘 다 CLA 필수(Open edX: Axim, 개인 폼/legal@axim.org; Canvas: PR CLA 체크, "dual-licensed"). Open edX는 6개월 명명 릴리스, 현재 Verawood(2026-07-30, Tutor v22); Canvas는 월간 프로덕션 릴리스(날짜 명명).

### Cited Findings
- edx-platform LICENSE: AGPL v3 전문 + 말미 EdX Inc. 해석("any public, independently available web service offered over the network and communicating with edX's copyrighted works"는 파생물 아님) — [LICENSE](https://raw.githubusercontent.com/openedx/edx-platform/master/LICENSE)
- canvas-lms LICENSE: AGPL v3 표준 전문, 고유 예외 없음 — [LICENSE](https://raw.githubusercontent.com/instructure/canvas-lms/master/LICENSE); README "It is released under the AGPLv3 license.", "developed and maintained by Instructure Inc." — [README](https://github.com/instructure/canvas-lms/blob/master/README.md)
- Canvas CLA: dual-licensed이므로 "we need you to sign a contributor license agreement (CLA) before we can accept a pull request"; PR CLA 상태 체크 → Details 웹폼 — [Contributing to Canvas](https://github.com/instructure/canvas-lms/wiki/Contributing-to-Canvas)
- Open edX CLA: "Before we can merge your contribution you will need to sign a Contributor License Agreement (CLA)"; 개인은 openedx.org/cla, 기관은 `legal@axim.org` — [Quickstart (Ulmo)](https://docs.openedx.org/en/ulmo/developers/quickstarts/so_you_want_to_contribute.html); `openedx.org/cla/`는 `https://tcril.tfaforms.net/f/individual-cla`로 303 리다이렉트 — [openedx.org/cla](https://openedx.org/cla/)
- 거버넌스: 비영리 edX Inc.는 2021-11-16 edX.org 사업을 2U에 매각 완료, Axim Collaborative로 개명 후 "the stewardship of the Open edX platform" 유지, Harvard·MIT 임명 이사회; 푸터는 edX/Open edX를 "registered trademarks of edX LLC"로 표기; 새 CLA는 license grant 방식 — [Axim blog](https://openedx.org/blog/the-open-edx-project-at-the-center-for-reimagining-learning); (스니펫) Core Contributor는 CLA+Program Agreement — [OEP-54](https://open-edx-proposals.readthedocs.io/en/latest/processes/oep-0054-core-contributors.html)
- Open edX 주기: "Every six months, we take a snapshot of our code, test it, and package it as an official Open edX release"; Redwood 2024-06; Willow는 2027-01 코드컷, "Willow goes out March 2027" — [Releases Homepage](https://openedx.atlassian.net/wiki/spaces/OEPM/pages/4191191044); 공식 색인은 Verawood(현재), Willow "December 2026", Xylon "June 2027", "the latest release is the only supported release" — [Release Notes index](https://docs.openedx.org/en/latest/community/release_notes/index.html) (Willow 시점 상충)
- Verawood "was released on July 30, 2026."; 하이라이트: granular team management, AI Extensions Framework, Libraries, Studio 사이드바, 새 Instructor Dashboard, tagging/taxonomy, LTI Advantage Complete, plugin slots — [Verawood](https://docs.openedx.org/en/latest/community/release_notes/verawood.html); (스니펫) 구 문서는 "June 2026", 계획 대비 5주 지연 — [Ulmo docs](https://docs.openedx.org/en/ulmo/community/release_notes/verawood.html), [discuss](https://discuss.openedx.org/t/new-release-open-edx-verawood-1-is-out/19183)
- Tutor v22.0.0(2026-08-07): `OPENEDX_COMMON_VERSION`=`release/verawood.1`, "Tutor now requires Python 3.10+", Meilisearch 1.36.0 재색인, Caddy 2.11.4/MongoDB 7.0.39/MySQL 8.4.11/Redis 7.4.10, 이미지 Python 3.12.13·Node 24.16.0 — [discuss](https://discuss.openedx.org/t/announcing-tutor-v22-0-0-open-edx-verawood-support/19207)
- Teak/Ulmo 명칭은 문서 경로로 확인 — [release-teak](https://docs.openedx.org/en/release-teak/educators/olx/organizing-course/course-xml-file.html), [ulmo](https://docs.openedx.org/en/ulmo/community/release_notes/verawood/dev_op_release_notes.html)
- Canvas: (스니펫) 프로덕션 릴리스 매월 셋째 토요일(2026-01-17 일치), 베타 약 1개월 선행, 테스트는 릴리스 후 첫 월요일; 베타 3주 주기 전환 공지 후 번복 — [Updated Schedule](https://community.canvaslms.com/t5/The-Product-Blog/Updated-Canvas-Deploy-and-Release-Schedule/ba-p/659097), [Release Notes 2026-01-17](https://community.instructure.com/en/discussion/664358/canvas-release-notes-2026-01-17), [Deploy Notes 2026-01-14](https://community.instructure.com/en/discussion/664383/canvas-deploy-notes-2026-01-14); 날짜 명명 예 — [2025-11-15](https://community.canvaslms.com/t5/Canvas-Releases/Canvas-Release-Notes-2025-11-15/ta-p/660781); "Canvas now recommends min Ruby 3.4.1, as of the 2025-07-02 release" — [Production Start](https://github.com/instructure/canvas-lms/wiki/Production-Start)

### Inferences
- 둘 다 AGPL-3.0이므로 코드 복사는 전염 대상; 스키마·API 형태만 참고. "최신만 지원"(Open edX)·월간 SaaS 릴리스(Canvas)는 셀프호스팅 업그레이드 부담 → 릴리스마다 dev/op 마이그레이션 노트를 동봉하는 관행만 차용. 소규모엔 CLA보다 DCO가 저비용(추론).

### Gaps
- Sumac/Teak/Ulmo 출시일 미확인(eduNEXT 버전 표 403). Canvas 공식 일정 문서(DOC-1384, 블로그)는 404/제목만 반환 → "셋째 토요일"은 1차 본문 미확인. Canvas 상업 라이선스 조건 미기재.

## KQ4. 아키텍처·스택·배포 무게

### Takeaway
Open edX: Django/Python 모놀리스(LMS+Studio, Mako) + React MFE(Verawood부터 frontend-base 단일 셸), Tutor(Docker)로 배포; 최소 4 GB/2 CPU/8 GB, 권장 8 GB/4 CPU/25 GB. Canvas: Rails(Ruby 3.4.1+), Node 20, PostgreSQL 14+, Redis 6+, Apache/Passenger, 별도 RCE API·QTIMigrationTool, "at least 8GB RAM". 둘 다 1인 과정용 대비 매우 무겁다.

### Cited Findings
- openedx-platform은 "the legacy monolith application"(LMS 모드/Studio 모드), Django(Mako 템플릿), React MFE(frontend-platform: 인증·로깅·모니터링·번역), Django 렌더링→MFE 이행 중; 확장점 plugin slots/XBlocks/Hooks Extension Framework/design tokens — [Platform Overview](https://docs.openedx.org/en/latest/developers/concepts/platform_overview.html)
- Verawood: frontend-base 첫 지원(`frontend-app-authn`, `-learner-dashboard` 기본 off; `-instructor-dashboard`, `-notifications` 기본 on); Catalog MFE 기본, 레거시는 Willow 제거; 레거시 Libraries→Content Libraries 필수 마이그레이션; `USE_L10N` 제거(Django 5.0), Django 5.2+ `STORAGES` 권고; Typesense 2.0.0("only compatible with Typesense Server >= v30.0") — [Dev&Op Notes](https://docs.openedx.org/en/latest/community/release_notes/verawood/dev_op_release_notes.html)
- Tutor 요구사항: 최소 "4 GB RAM, 2 CPUs, 8 GB disk space", 권장 "8 GB RAM, 4 CPUs, 25 GB disk space"; 64-bit UNIX(WSL 2 보고), AMD64/ARM64; Docker Engine v24.0.5+(BuildKit 0.11+), Compose v2.0.0+; Mac 기본 2 GB 부족 — [Tutor Requirements](https://docs.tutor.edly.io/gettingstarted/requirements.html); 스택 이미지(MySQL/MongoDB/Redis/Meilisearch/Caddy)는 Tutor v22 공지 — [discuss](https://discuss.openedx.org/t/announcing-tutor-v22-0-0-open-edx-verawood-support/19207)
- Canvas Production Start(Ubuntu 22.04 테스트): Ruby 3.4.1+, Node 20, "the required yarn version is 1.19.1", "at least PostgreSQL version 14", "redis 6.x or above", Apache+Passenger+mod_rewrite, "we recommend a server with at least 8GB RAM", "Canvas likes RAM", 전용 job 서버 "advisable"("so many jobs to run"), prod 브랜치 편집에 Rich Content Editor API 서비스 필요, CPU 미기재 — [Production Start](https://github.com/instructure/canvas-lms/wiki/Production-Start)

### Inferences
- 실제 운용선은 양쪽 모두 8 GB급. 소규모 플랫폼을 "컨테이너 1개 + DB 1개(1 vCPU/1 GB)"로 잡으면 1/8 이하 무게이며 그 자체가 차별점. 공통 교훈: 저작/학습 런타임 분리, 플러그인 슬롯 확장, 검색·분석을 코어 밖으로.

### Gaps
- Open edX 데이터스토어 구성(MySQL/MongoDB modulestore/Meilisearch)은 아키텍처 페이지에 없고 Tutor 이미지 목록으로만 간접 확인. Canvas 공식 컨테이너 배포 가이드·실측 메모리 미조사.

## KQ5. 진도·분석 데이터 모델

### Takeaway
Open edX: `BlockCompletion(user, context_key, block_key, block_type, completion∈[0,1])`, unique(context_key, block_key, user), waffle switch로 활성화; JSON 트래킹 로그(공통 필드) → event-routing-backends(xAPI) → Vector/Ralph → ClickHouse → dbt/Superset(Aspects). Canvas: Modules 완료요건/상태 + Live Events(`grade_change` 등, `metadata`+`body`, SQS/Webhook, Canvas·Caliper 1.1) + DAP/Canvas Data 2(snapshot 1회+incremental, CLI→PostgreSQL/MySQL/MSSQL).

### Cited Findings
- BlockCompletion: `user=ForeignKey(User, CASCADE)`, `context_key=LearningContextKeyField(255, db_column="course_key")`, `block_key=UsageKeyField(255)`, `block_type=CharField(64)`(집계용 분리), `completion=FloatField(validators=[validate_percent])`("must be between 0.0 and 1.0"), `unique_together=('context_key','block_key','user')`, 실무는 1.0/0.0 이진 — [models.py](https://github.com/openedx/completion/blob/master/completion/models.py); 배치 제출 DRF API, 기본 off, switch `completion.enable_completion_tracking` — [README](https://github.com/openedx/completion/blob/master/README.rst)
- 트래킹 로그: server/browser/mobile 방출, JSON 문서 — [index](https://docs.openedx.org/en/latest/developers/references/internal_data_formats/tracking_logs/index.html); 공통 필드 `accept_language, agent, context{course_id, org_id, path, user_id}, event, event_source(browser|mobile|server|task), event_type, host, ip, name("supersedes the event_type field"), page, referer, session(32자), time(UTC), username` — [Common Fields](https://docs.openedx.org/en/latest/developers/references/internal_data_formats/tracking_logs/common_fields.html)
- Aspects: "primarily a Tutor plugin that combines data from the Open edX learning management system and Studio"; 등록 추세·문제 정답률·비디오 시청 구간; 기본 학습자 비식별; 대시보드 Course/Individual Learner/At-Risk/Operator/Course Comparison/In-Context — [Aspects docs](https://docs.openedx.org/projects/openedx-aspects/en/latest/index.html); 구성 ClickHouse, Superset, Ralph("validates and stores xAPI statements in ClickHouse", v4부터 선택), Vector(기본), Event-Routing-Backends, dbt(aspects-dbt); 설치 `pip install tutor-contrib-aspects` → `tutor plugins enable aspects` → `tutor images build aspects aspects-superset` → `tutor local do init` — [README](https://github.com/openedx/tutor-contrib-aspects/blob/master/README.rst); Aspects v4.0.0은 Python 3.12 — [Dev&Op Notes](https://docs.openedx.org/en/latest/community/release_notes/verawood/dev_op_release_notes.html)
- Canvas Live Events: "Customers can subscribe to specific events and receive them using either an AWS SQS queue or an HTTPS Webhook"; 분석용, 최신 상태는 일반 API — [Intro](https://canvas.instructure.com/doc/api/file.data_service_introduction.html); `grade_change`("emitted anytime when a submission is graded"; body `score, old_score, grade, old_grade, student_id, assignment_id, submission_id, grader_id, points_possible, muted, grading_complete`), `course_grade_change`(`current_score, old_current_score, final_score, ...`), `grade_override`; 공통 `metadata`(`event_name, event_time, context_id, root_account_id, user_id`) — [Grade events](https://canvas.instructure.com/doc/api/file.data_service_canvas_grade.html)
- DAP: "Instructure's centralized data repository for analytics across products"; Query API, CLI, Python 클라이언트 — [overview](https://developerdocs.instructure.com/services/dap); snapshot(전체, `canvas_logs`는 30일) vs incremental, "taking a snapshot exactly once (as an initialization step)"; 네임스페이스 `canvas`(`assignments, content_tags, submissions`), `canvas_logs`(`web_logs`), `catalog`, `new_quizzes` — [Key Concepts](https://developerdocs.instructure.com/services/dap/key-concepts); CLI: "An API key is restricted to a set of tables it may read", DB 타깃 "PostgreSQL 16.3+, MySQL 8.2+, Microsoft SQL Server 2019+", "Python 3.11+" — [CLI README](https://developerdocs.instructure.com/services/dap/dap-cli-readme)

### Inferences
- 양쪽 모두 "완료 테이블"과 "이벤트 스트림"을 분리. `lesson_progress(user_id, course_id, lesson_id, completion, completed_at)` + JSONL append-only 이벤트(공통 필드 `event_type, event_source, context, time, session`)면 충분하며 xAPI 변환·ClickHouse는 후속 플러그인. Canvas의 `old_*`/현재값 쌍은 성적 감사 로그에 차용.

### Gaps
- Open edX grades 모델(PersistentCourseGrade 등)·completion-aggregator 미조사. DAP 출력 포맷·신선도 미기재. Canvas Caliper 소개 페이지 404.

## KQ6. 차용/회피 설계 포인트

### Takeaway
차용: OLX식 파일 트리=코스 트리, Canvas 완료요건 enum, BlockCompletion 스키마, Canvas 권한 사전, 트래킹 공통 필드+xAPI 분리, 릴리스별 마이그레이션 노트. 회피: XML 수작업 저작, 다중 저장소, HTML-only 본문, 다수 MFE 배포, SCORM 런타임 내장.

### Cited Findings
- 근거는 KQ1~5의 출처: [OLX Directory Structure](https://docs.openedx.org/en/latest/educators/olx/directory-structure.html), [markdown-xblock](https://github.com/citynetwork/markdown-xblock/blob/main/README.md), [Pages API](https://canvas.instructure.com/doc/api/pages.html), [Modules API](https://canvas.instructure.com/doc/api/modules.html), [completion/models.py](https://github.com/openedx/completion/blob/master/completion/models.py), [Roles API](https://canvas.instructure.com/doc/api/roles.html), [Verawood Dev&Op Notes](https://docs.openedx.org/en/latest/community/release_notes/verawood/dev_op_release_notes.html), [Common Fields](https://docs.openedx.org/en/latest/developers/references/internal_data_formats/tracking_logs/common_fields.html), [Tutor Requirements](https://docs.tutor.edly.io/gettingstarted/requirements.html), [Production Start](https://github.com/instructure/canvas-lms/wiki/Production-Start), [OEP-42](https://open-edx-proposals.readthedocs.io/en/latest/best-practices/oep-0042-bp-authentication.html)

### Inferences
1. **레포 트리=코스 트리**: `course/modules/<m>/lessons/<l>.md`, frontmatter에 안정 slug(OLX `url_name` 역할)와 `grading_policy.json` 상당 메타; tar.gz/zip 단일 내보내기(후속 OLX/CC 변환 용이).
2. **Markdown 소스 + sanitize HTML 산출물**: 양쪽 정준이 HTML이므로 빌드 시 HTML 생성; markdown-xblock의 safe mode 기본 on 정책 채택.
3. **완료요건 frontmatter enum**: `must_view|must_submit|min_score|must_mark_done`, `require_sequential_progress`, 선수조건; 진도는 `(user, course, lesson)` 유니크 + `completion float` + `completed_at`.
4. **권한 사전 + 계층 잠금**: `{permission: {enabled, locked}}`, 조직→과정 `applies_to_descendants`; 권한 모델 변경 시 flag 단계 롤아웃 + 마이그레이션 명령(Open edX authz 패턴).
5. **이벤트 공통 필드 + 변환 분리**: JSONL append-only를 1차 저장소로, xAPI/Caliper 변환은 별도 프로세스.
6. **회피**: MySQL+MongoDB 이중 저장소, 다수 MFE, Rails+Passenger+RCE+job 서버, SCORM 런타임; LTI 1.3 Tool로 외부 LMS에 임베드되는 쪽 선택. OLX의 XML 전제·Canvas HTML 리비전 대신 Git 기반 Markdown 리비전.

### Gaps
- Content Libraries v2, Canvas Blueprint/Commons 등 재사용 메커니즘, 접근성(WCAG) 문서는 미조사.

## 비교표

| 항목 | Open edX | Canvas LMS |
|---|---|---|
| 라이선스/CLA | AGPL-3.0(+edX 해석 문구); CLA 필수(Axim) | AGPL-3.0 표준; "dual-licensed", PR CLA 체크 |
| 거버넌스 | Axim Collaborative(비영리, Harvard·MIT 이사회) | Instructure Inc. |
| 릴리스 | 6개월 명명 릴리스, Verawood 2026-07-30, 최신만 지원; Willow 2026-12/2027-03(상충), Xylon 2027-06 | 월간 프로덕션(날짜 명명, 2026-01-17 등) + Deploy Notes(스니펫) |
| 스택/배포 | Django 모놀리스 + React MFE/frontend-base; Tutor(Docker); 최소 4 GB/2 CPU, 권장 8 GB/4 CPU | Rails(Ruby 3.4.1+)/Node 20/PostgreSQL 14+/Redis 6+/Apache; RCE API, job 서버; "at least 8GB RAM" |
| 로그인 | LMS 단일 IdP; 소셜/SAML 연동 | 12종 `auth_type`(saml, cas, ldap, openid_connect...) |
| API 인증 | OAuth2(DOT)+비대칭 JWT, Bearer 폐기 | OAuth2 RFC-6749, 1h 토큰+refresh, LTI client-credentials |
| 역할/권한 | Staff/Limited Staff/Admin/Data Researcher → openedx-authz RBAC | base role type + 커스텀 역할 + 권한 사전(`enabled/locked/applies_to_descendants`) |
| 멀티테넌시 | Django Site + Site Configuration, Organizations | Root→sub-account 트리, 설정 `locked` 상속 |
| 콘텐츠 포맷 | OLX(XML, tar.gz): course→chapter→sequential→vertical→XBlock | Pages(HTML)+Modules; CC(.imscc)/QTI/zip 내보내기, CC/QTI/Moodle 가져오기 |
| Markdown | 서드파티 markdown-xblock | 네이티브 없음 |
| LTI / SCORM / xAPI | 1.1/1.3+Advantage(Verawood 인증) / Tutor 번들 1.2·2004 / event-routing-backends→xAPI | 1.3+Advantage / 기관 SCORM LTI(스니펫) / Caliper 1.1 Live Events, xAPI 없음 |
| 진도/분석 | BlockCompletion(0~1) / Aspects(ClickHouse·Superset·Vector·dbt) | Module 상태 locked→completed / Live Events(SQS/Webhook) + DAP(snapshot+incremental) |
