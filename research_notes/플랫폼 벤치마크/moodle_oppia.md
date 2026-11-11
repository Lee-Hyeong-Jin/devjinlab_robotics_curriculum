# Moodle · Oppia 플랫폼 벤치마크 (2026-11-11 기준)

> 소규모 오픈소스 커리큘럼 플랫폼(단일 robotics 코스, module → lesson, Markdown+frontmatter, 진행 추적, 향후 auth/API/web/CI)의 설계 레퍼런스. URL은 실제 fetch했거나 fetch한 페이지에 적힌 것만 사용. "(검색 스니펫 기준)"은 본문 미확인.

## KQ1. 라이선스 · 버전 · 릴리스 주기 · CLA · 거버넌스

### Takeaway
Moodle은 GPL-3.0(COPYING.txt = GPLv3 전문), 2026-10-05 출시 5.3이 현재 안정+차기 LTS, 6개월 메이저/2개월 마이너, Moodle HQ(Moodle Pty Ltd) 주도이며 CLA 요구 근거 없음. Oppia는 Apache-2.0, 최신 v3.5.3(2026-09-23), 월간 cut 목표, CLA 필수, Oppia Foundation(501(c)(3), EIN 81-1740068) 운영.

### Cited Findings
- Moodle COPYING.txt = "GNU GENERAL PUBLIC LICENSE, Version 3, 29 June 2007" 전문(14조 "or any later version" 선택 조항 포함) — [COPYING.txt](https://raw.githubusercontent.com/moodle/moodle/main/COPYING.txt); GitHub spdx `GPL-3.0`, default branch `main`, stars 7,600, 마지막 push 2026-10-30 — [GitHub API](https://api.github.com/repos/moodle/moodle)
- 지원 표(2026-10-04 갱신): 4.5 LTS(2024-10-07, 보안지원 ~2027-10-04), 5.1(2025-10-06), 5.2(2026-04-20, 최신 5.2.3 2026-09-14), **5.3 LTS(2026-10-05, 보안지원 ~2029-10-01)**, 6.0(2027-04-19 예정), 6.1(2027-10-04 예정). "The next LTS version will be Moodle 5.3." 메이저 매 6개월(4/10월), 마이너 2개월 — [Releases](https://moodledev.io/general/releases)
- 5.3 노트: "Moodle 5.3 (LTS)", Classic 테마 core 제거, Anthropic Claude AI provider, Learning outcomes, OAuth 2 server/client/token + routed web services — [5.3 release notes](https://moodledev.io/general/releases/5.3)
- 개발 프로세스: "Every change must have an issue in the tracker." HQ component lead peer review → "the integration team (a small team of senior developers employed by Moodle HQ)" → 테스터 → 매주 목요일 머지. CLA/저작권 양도 언급 없음 — [Process](https://moodledev.io/general/development/process); 기여 가이드도 CLA 없음, 로드맵은 "Moodle LMS Community Product Advisory Group" — [Contributing](https://moodledev.io/general/community/contribute)
- "The copyrights belong to hundreds of authors and they would ALL need to agree to any change in the license."; 핵심 개발자 = Moodle Pty Ltd — [Future FAQ](https://docs.moodle.org/dev/Future); moodle.org policyid=4는 CLA가 아닌 사이트 이용약관 — [Site Policy](https://moodle.org/admin/tool/policy/view.php?policyid=4)
- Moodle Users Association: 2015년 설립, 회원 구독료로 HQ 개발 펀딩(20개 프로젝트, 100만 AUD+), "MUA membership voted in late 2024 to dissolve the MUA", 후속은 Product Advisory Group — [moodle.org/mua](https://moodle.org/mua); Moodle Pty Ltd는 상표 소유, Certified B Corp, Certified Partners 생태계 — [moodle.com/about](https://moodle.com/about/)
- Oppia LICENSE = "Apache License, Version 2.0, January 2004" 전문(저작권 라인은 템플릿) — [LICENSE](https://raw.githubusercontent.com/oppia/oppia/develop/LICENSE); README "The Oppia code is released under the Apache v2 license.", Python/Angular/GAE, stars ~7.0k, 17,043 commits — [README](https://github.com/oppia/oppia)
- 최신 릴리스 `v3.5.3` published 2026-09-23T12:40:52Z (mon4our) — [GitHub API](https://api.github.com/repos/oppia/oppia/releases/latest); 목록 v3.5.3(9/23)·3.5.2(7/20)·3.5.1(4/09)·3.5.0(3/05)·3.4.9(12/24) — [Releases](https://github.com/oppia/oppia/releases); package.json `"version": "3.5.4"` — [package.json](https://raw.githubusercontent.com/oppia/oppia/develop/package.json)
- "Oppia releases happen monthly, and are typically cut on the first Wednesday of each month." cut → QA 1주 → 배포 1주, 월별 release coordinator, 회귀는 revert 우선 — [Release schedule](https://github.com/oppia/oppia/wiki/Release-schedule-and-other-information)
- CLA: "If you do not sign the CLA, any PRs you open will be closed." GitHub 2FA 필수 — [Contributing code to Oppia](https://github.com/oppia/oppia/wiki/Contributing-code-to-Oppia)
- Oppia Foundation Inc: 501(c)(3), EIN 81-1740068, Sacramento CA, 면세 2016-03, FY2025 Form 990-EZ 수입 $124,178 — [ProPublica](https://projects.propublica.org/nonprofits/organizations/811740068)

### Inferences
- Moodle은 CLA 없이 기여자가 저작권을 보유하는 GPL 모델, Oppia는 CLA로 재라이선스 여지 확보. 소규모 플랫폼은 Apache-2.0 + DCO로 시작해도 충분.
- Oppia의 실제 공개 릴리스는 2~4개월 간격으로 위키의 월간 cadence와 어긋남.

### Gaps
- Moodle 소스 파일 헤더의 "or any later version" 문구는 raw.githubusercontent 404로 직접 확인 실패(GPL-3.0-or-later 여부).
- Oppia CLA 폼의 조항(양도 vs 라이선스), Oppia Foundation 공식 소개 페이지(404)는 미확인.

## KQ2. 인증 · 권한 모델

### Takeaway
Moodle: 인증은 플러그인(Manual/Email/External DB/LDAP/LTI/OAuth 2(OIDC discovery)/Shibboleth/MFA; SAML2는 서드파티 auth_saml2), 권한은 역할×능력×컨텍스트 트리(SYSTEM 10 → USER 30 → COURSECAT 40 → COURSE 50 → MODULE 70 → BLOCK 80)에 Inherit/Allow/Prevent/Prohibit override. Oppia: Firebase Authentication(OIDC 1.0) 위임 + 평면 역할 16종 → 액션 집합(`_ROLE_ACTIONS`) + 리소스별 owner/editor/manager ID 리스트.

### Cited Findings
- Moodle 인증 플러그인(5.3): Manual accounts, No login, Email-based self-registration, External database, LDAP, LTI, No authentication, OAuth 2, Shibboleth, Web services, Multi-factor authentication — [Managing authentication](https://docs.moodle.org/en/Managing_authentication)
- OAuth 2 사전 설정: Google, Microsoft, Facebook, Nextcloud, MoodleNet, Open Badges, LinkedIn, Clever; 커스텀 발급자가 "Open ID Connect compliant"면 `<issuer base url>/.well-known/openid-configuration` discovery로 자동 설정 — [OAuth 2 services](https://docs.moodle.org/en/OAuth_2_services)
- SAML2: `auth_saml2`(Catalyst IT), 최신 2026-04-02, Moodle 2.7–5.1 지원, 4,796 사이트, "completely embeds a SimpleSamlPHP instance", back-channel Single Logout — [auth_saml2](https://marketplace.moodle.com/plugins/auth_saml2); LDAP는 "the most widely used standard protocol for authentication" — [Standards](https://docs.moodle.org/en/Standards)
- "A role is a collection of permissions defined for the whole system"; "The combination of roles and context define a specific user's ability" — [Roles and permissions](https://docs.moodle.org/en/Roles_and_permissions)
- "A context is a space in Moodle where roles can be assigned." accesslib.php 상수 SYSTEM=10, USER=30, COURSECAT=40, COURSE=50, MODULE=70, BLOCK=80; 역할은 트리 아래로 상속, 예외는 설정 컨텍스트와 그 하위에만 적용 — [Context](https://docs.moodle.org/en/Context)
- 능력 정의: 플러그인 `db/access.php` `$capabilities`; 이름 `plugintype/pluginname:capabilityname`(예 `mod/folder:managefiles`); 필드 `riskbitmask`, `captype`(read/write; write는 guest·비로그인 차단), `contextlevel`, `archetypes`(예 `'editingteacher' => CAP_ALLOW`), `clonepermissionsfrom`; `has_capability()`(admin 기본 true)/`require_capability()`; 지침 "Does the user have capability to do something?"; "Roles can be overridden by contexts further down the tree." — [Access API](https://moodledev.io/docs/apis/subsystems/access)
- 권한 값: Inherit(기본), Allow(해당+하위 컨텍스트), Prevent("removing permission for this capability (only for this role)"; 다른 역할 Allow면 무효), Prohibit("can NOT be overridden at any lower context or by another role"). 하위 컨텍스트 우선(Prohibit 예외), 동일 컨텍스트 Allow vs Prevent는 Allow 승. Override는 "modifies an existing specific role and affects all users assigned to that role in the context"; 필요 능력 `moodle/role:override`/`moodle/role:safeoverride`; 기본 Manager는 전 역할, Teacher는 non-editing teacher/student/guest만 override — [Override permissions](https://docs.moodle.org/en/Override_permissions)
- 표준 역할: Site administrator("can 'do everything'"), Manager("a lesser administrator role"), Course creator, Teacher, Non-editing teacher("can grade… but not edit"), Student, Guest, Authenticated user, Authenticated user on the front page — [Standard roles](https://docs.moodle.org/en/Standard_roles)
- Oppia 인증: "Oppia depends on OpenID Connect 1.0 to handle user authentication." IdP 예시 "Google, Facebook, Email verification links, and Text message SMS codes"; `auth_id` = `sub` 클레임; ID 토큰(Bearer) → HttpOnly 세션 쿠키 교환(`establish_auth_session`), `verify_session_cookie(check_revoked=True)`; super admin = `ADMIN_EMAIL_ADDRESS` 일치 또는 custom claim `role == super_admin`; "Users have ZERO CONTROL over what their assigned role is." — [firebase_auth_services.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/platform/auth/firebase_auth_services.py); `FIREBASE_SESSION_COOKIE_MAX_AGE = datetime.timedelta(days=14)`, `FIREBASE_EMULATOR_PORT = 9099` — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py)
- Oppia 역할 상수: `ROLE_ID_CURRICULUM_ADMIN = 'ADMIN'`, `ROLE_ID_MODERATOR = 'MODERATOR'`, `ROLE_ID_TOPIC_MANAGER = 'TOPIC_MANAGER'`, `ROLE_ID_FULL_USER = 'EXPLORATION_EDITOR'`, `ROLE_ID_GUEST = 'GUEST'`, `ROLE_ID_MOBILE_LEARNER = 'LEARNER'`, 그 외 BLOG_ADMIN, BLOG_POST_EDITOR, COLLECTION_EDITOR, QUESTION_ADMIN, QUESTION_COORDINATOR, RELEASE_COORDINATOR, TRANSLATION_ADMIN, TRANSLATION_COORDINATOR, VOICEOVER_ADMIN, TECH_TEAM_LEAD — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py)
- `_ROLE_ACTIONS`: curriculum admin = CREATE_NEW_TOPIC/SKILL, DELETE_TOPIC, EDIT_ANY_STORY/TOPIC/SUBTOPIC_PAGE/QUESTION, CHANGE_STORY/TOPIC_STATUS, MANAGE_TOPIC_RIGHTS, ACCESS_CLASSROOM_ADMIN_PAGE, PUBLISH_ANY_ACTIVITY 등; topic manager = EDIT_OWNED_TOPIC/STORY, EDIT_SKILL, EDIT_ANY_SUBTOPIC_PAGE, EDIT_QUESTION_IN_MANAGED_TOPIC, MANAGE_QUESTION_SKILL_STATUS; moderator = ACCESS_MODERATOR_PAGE, EDIT/DELETE/UNPUBLISH_ANY_PUBLIC_ACTIVITY, PLAY_ANY_PRIVATE_ACTIVITY; full user = CREATE_EXPLORATION, EDIT/PUBLISH_OWNED_ACTIVITY, ACCESS_LEARNER_DASHBOARD, ACCESS_LEARNER_GROUPS, SUGGEST_CHANGES; guest/mobile learner = PLAY_ANY_PUBLIC_ACTIVITY. "No role hierarchy or inheritance logic appears in this module." LEARNER는 UPDATABLE_ROLES에서 제외(프로필) — [role_services.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/role_services.py)
- 핸들러 데코레이터("Decorators to provide authorization across the site"): `role_services.ACTION_* in self.user.actions` 검사 + 리소스별 `rights_manager.check_can_edit_activity` 등; `can_access_admin_page`는 super admin; 크론은 `X-AppEngine-Cron` 헤더 — [acl_decorators.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/controllers/acl_decorators.py); `TopicRights(manager_ids, topic_is_published)` — [topic_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/topic_domain.py); ExplorationSummary에 `owner_ids, editor_ids, voice_artist_ids, viewer_ids, community_owned` — [exp_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/exp_domain.py)

### Inferences
- Moodle의 가치: `component:action` 네임스페이스 능력, "역할"이 아닌 "컨텍스트 내 능력"으로 판정, Prohibit의 하향 강제. 단일 코스라면 컨텍스트를 system/course/module/lesson 4단으로 축소 가능.
- Oppia 모델은 단순하지만 상속이 없어 역할 16종·액션 중복이 발생. 액션 enum(Oppia) + 컨텍스트 트리(Moodle) 하이브리드가 적합. Oppia의 owner/manager ID 리스트는 Markdown 폴더별 CODEOWNERS와 유사.

### Gaps
- `CAP_INHERIT/PREVENT/PROHIBIT` 숫자값·risk bitmask 목록(accesslib.php) 미확인; Oppia `ExplorationRights` 클래스·`ACTIVITY_STATUS_*` 값, oppia.org 실제 활성 IdP 목록 미확인.

## KQ3. API 인증과 호출 방식

### Takeaway
Moodle 전통 웹서비스는 `login/token.php`로 받은 `wstoken`을 `webservice/rest/server.php?wsfunction=…` RPC에 붙이는 방식("not RESTful"), 5.3에서 scope 기반 REST API(개인 액세스 토큰 + OAuth 2 client, SwaggerUI) 신설. GraphQL 없음. Oppia는 공개 API 없이 내부 JSON 핸들러 + 세션 쿠키 + ACL 데코레이터.

### Cited Findings
- "Each user will have a specific and unique security key (also known as a 'token')"; 관리자 토큰은 Manage tokens에서만; IP 제한·"Valid until"; 프로토콜별 `webservice/rest:use` 등; 커스텀 서비스("Authorised users only", "Required capability") → 함수 추가 → 능력 부여; GraphQL 언급 없음 — [Using web services](https://docs.moodle.org/en/Using_web_services)
- 토큰: `https://www.yourmoodle.com/login/token.php?username=USERNAME&password=PASSWORD&service=SERVICESHORTNAME`(모바일 `moodle_mobile_app`; 3.9+ `token`,`privatetoken` JSON). 호출: `https://your.site.com/webservice/rest/server.php?wstoken=...&wsfunction=...&moodlewsrestformat=json`(배열 `&array_name[index][parameter_name]=value`). REST는 "not RESTful"; SOAP/XML-RPC(Zend), AMF(3.0 이전); 샘플 `https://github.com/moodlehq/sample-ws-clients` — [Creating a web service client](https://docs.moodle.org/dev/Creating_a_web_service_client)
- 동일 프레임워크가 웹 UI AJAX와 Moodle Mobile App에 사용 — [External services](https://moodledev.io/docs/apis/subsystems/external); 함수 정의 `db/services.php`(`classname`, `type` read/write, `ajax`, `capabilities`("advisory only"), `services`에 `MOODLE_OFFICIAL_MOBILE_SERVICE`), `\core_external\external_api` 상속 + `execute_parameters()/execute()/execute_returns()` — [Writing a service](https://moodledev.io/docs/apis/subsystems/external/writing-a-service)
- 5.3 REST API: "REST API tokens let external apps and scripts connect to Moodle's new REST API."; Personal access tokens(`moodle/api:createtoken`) + OAuth 2 clients(`moodle/site:manageoauth2clients`, Composer 의존성 필요); "Every token has one or more scopes"; SwaggerUI(Site administration > Development); 전통 토큰과 별개, "Enable web services" 무관; "only a few parts of Moodle are available through the REST API" — [REST API tokens](https://docs.moodle.org/en/REST_API_tokens); 클라이언트 confidential/public, secret 최대 2개·1년 만료(검색 스니펫 기준) — [OAuth 2 clients](https://docs.moodle.org/en/OAuth_2_clients)
- Oppia: `main.py` 라우팅 → `core/controllers/`("Thin HTTP handlers that call services and return JSON") → `*_services.py`/`*_domain.py` → `core/storage`; 프런트 `-backend-api.ts`가 HTTP 호출 — [Codebase overview](https://github.com/oppia/oppia/wiki/Overview-of-the-Oppia-codebase); 핸들러 URL 예 `/classroom_data_handler`, `/learner_dashboard_learner_groups_handler` — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py)

### Inferences
- 신규 플랫폼은 처음부터 OpenAPI + scope 토큰(PAT + OAuth2/OIDC 클라이언트)으로 가고, 내부 UI와 외부 API가 같은 엔드포인트를 쓰도록 설계(Moodle이 AJAX/모바일에 웹서비스를 재사용하듯). Oppia식 "공개 계약 없는 내부 API"는 반면교사.

### Gaps
- 5.3 REST API 엔드포인트 경로·노출 리소스 목록(Routing/scopes 개발자 문서) 미조사; Oppia CSRF 처리·Android API 미조사.

## KQ4. 콘텐츠 모델 — Moodle

### Takeaway
course → section(+subsection) → activity/resource(mod 플러그인 인스턴스) 3계층, 저작은 HTML 에디터 중심이며 Markdown은 "Plain text area" 선택 시 텍스트 포맷 옵션. `.mbz`는 기본 tgz(옵션 zip)로 루트 `moodle_backup.xml` + `files.xml`/해시 스토어 + `course/`, `sections/`, `activities/<cmid>/` XML 묶음.

### Cited Findings
- 포맷: Custom sections("divided into customisable sections that a teacher can give titles to"), Weekly sections, Single activity("one section… one activity only"); Course index로 섹션 이동 — [Course formats](https://docs.moodle.org/en/Course_formats); 5.3: 전 코스 선형 내비게이션(Previous/Next), 서브섹션 순서 로직 개선(MDL-86393), Learning outcomes backup/restore 지원 — [5.3 release notes](https://moodledev.io/general/releases/5.3)
- 플러그인 타입 56종(표 행 집계): mod, block, qtype, qformat, filter, editor, enrol, auth, tool, logstore, availability, format, report, gradereport, repository, theme, local, contenttype, h5plib, qbank 등 — [Plugin types](https://moodledev.io/docs/apis/plugintypes)
- Book: "create multi-page resources with a book-like format and table of contents"; H5P 임베드 가능(성적부 연동 없음); PDF 인쇄 — [Book](https://docs.moodle.org/en/Book_resource); Lesson: "'branching' exercises", Content page/Question page를 Jumps로 연결, 연습/채점 선택 — [Lesson](https://docs.moodle.org/en/Lesson_activity)
- Markdown: "To use Markdown, you need to choose 'Plain text area' as text editor" 후 "Markdown format" 선택; 목록 앞 빈 줄 필수 — [Markdown](https://docs.moodle.org/en/Markdown)
- 백업: 파일명 `backup-moodle2-course-coursename-date-hour.mbz`(`-nu` 사용자 제외, `-an` 익명); 사용자·역할·그룹·완료·로그·성적 이력 포함 가능; 4.4부터 비동기 백업 기본 — [Course backup](https://docs.moodle.org/en/Course_backup); ".mbz" = "Moodle backup zip"이지만 "The default format is TGZ (gzip)"(#1F8B), `$CFG->usezipbackups = true;`로 zip; `tar -xzf`로 해제, `files.xml` contenthash → `files/<앞2자>/` — [Backup and restore FAQ](https://docs.moodle.org/en/Backup_and_restore_FAQ)
- 구조(역사 문서): `moodle_backup.xml`("the 'map' that shows/describes the whole backup"), `files.xml`+`files/`, users/roles/scales/groups/outcomes stores, `course/`(course.xml, inforef.xml), `sections/<id>/section.xml`, `activities/<cmid>/`(activityname.xml, module.xml, completion, grades, logs, inforef.xml), `blocks/`; 플랜→태스크→스텝 — [Backup 2.0 architecture](https://docs.moodle.org/dev/Backup_2.0_general_architecture); 플러그인은 `backup/moodle2/backup_<mod>_activity_task.class.php` + stepslib의 `backup_nested_element`/`set_source_table()` — [Backup API](https://moodledev.io/docs/apis/subsystems/backup)
- IMS CC: "Moodle currently only supports the import of IMS CC version 1.0 and 1.1 packages."; 내보내기 1.1만, Forums/Labels/LTI/Page/URL + Quiz 부분("the ONLY activities that can be exported"); 비동기 백업 시 불가; 1.2/1.3은 MDL-60803 — [IMS CC](https://docs.moodle.org/en/IMS_Common_Cartridge_import_and_export)

### Inferences
- Moodle 콘텐츠 단위는 DB 레코드 + 파일 영역이며 Markdown은 렌더 포맷일 뿐. Markdown-first는 "폴더=섹션, 파일=레슨"으로 가되 `.mbz`의 manifest + 콘텐츠별 파일 + 해시 파일 스토어 구조를 export 포맷에 차용. Lesson의 Jump 분기는 frontmatter `next:/branches:`로 재현 가능. CC 내보내기는 Page/URL/LTI 수준이 현실적 목표.

### Gaps
- Page 리소스, Subsections 도입 버전(docs 404), Book HTML import 기능 미확인.

## KQ5. 콘텐츠 모델 — Oppia

### Takeaway
classroom('math') → topic → story(canonical/additional) → chapter(StoryNode = 발행된 exploration 1개 + prerequisite/acquired skill IDs) → exploration(카드=State 상태기계); skill은 topic 하위 subtopic으로 묶여 practice/diagnostic에 사용. Exploration은 YAML(schema 62, states_schema 57)로 직렬화되고 State = content(HTML) + interaction(id, customization_args, answer_groups[rule_specs→outcome(dest, feedback)], default_outcome, hints, solution).

### Cited Findings
- 용어: "A topic refers to a subject a learner is learning (e.g., Decimals, Fractions)." "A story is a set of lessons that teaches a topic with real-life examples." "A subtopic is a group of Skills within a Topic." "Explorations (or lessons) are learning units in Oppia." "A lesson is made up of a series of cards…" — [Key Terms](https://oppia-lesson-creator-documentation.readthedocs.io/en/latest/start/terms.html); "A topic, like Fractions, consists of one or more stories." Exploration "is the core unit of learning in Oppia." Skill = "a concrete learning outcome that describes something that a learner should be able to do."; 선행 스킬로 "generate random review questions at the start of each lesson" — [Lesson Creation Guide](https://github.com/oppia/oppia/wiki/Lesson-Creation-Guide)
- 저작 흐름: Topics and Skills Dashboard → "Create New Topic"(name, URL, web title fragment) → Canonical Stories "Add Story" → "Add Chapter"(title, Exploration ID, thumbnail) + Chapter Outline + "Add prerequisite skill"/"Add acquired skill" → "Publish story"; "You cannot publish the Story without this step"(발행된 Exploration ID) — [Create Topic/Story/Chapter](https://oppia-lesson-creator-documentation.readthedocs.io/en/latest/admins/create-topic-story-chapter.html)
- `Topic`: canonical_story_references, additional_story_references, uncategorized_skill_ids, subtopics, practice_tab_is_displayed, skill_ids_for_diagnostic_test, url_fragment, meta_tag_content; `Subtopic`: id(int), title, skill_ids, thumbnail_*, url_fragment — [topic_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/topic_domain.py)
- `StoryNode`("a node in the exploration graph of a story"): destination_node_ids, acquired_skill_ids, prerequisite_skill_ids, outline, exploration_id, status, planned_publication_date, first_publication_date; `StoryContents`: nodes, initial_node_id, next_node_id; `Story`: corresponding_topic_id, story_contents_schema_version, url_fragment; "NOTE: Currently, this function assumes only a linear arrangement of nodes." — [story_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/story_domain.py)
- `Skill`: description("Describes the observable behaviour of the skill"), misconceptions(id, name, notes, feedback, must_be_addressed), rubrics(난이도 3개, `constants.SKILL_DIFFICULTIES`), skill_contents.explanation, superseding_skill_id, prerequisite_skill_ids; v5에서 worked_examples 제거; `UserSkillMastery.degree_of_mastery`(float) — [skill_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/skill_domain.py)
- `Classroom`: name, url_fragment, course_details, teaser_text, topic_list_intro, topic_id_to_prerequisite_topic_ids, is_published, diagnostic_test_is_enabled, thumbnail/banner — [classroom_config_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/classroom_config_domain.py); `CLASSROOM_PAGES = ['math']` — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py)
- 스키마: `CURRENT_STATE_SCHEMA_VERSION = 57`, `CURRENT_STORY_CONTENTS_SCHEMA_VERSION = 7`, `CURRENT_SKILL_CONTENTS_SCHEMA_VERSION = 5`, `CURRENT_SUBTOPIC_PAGE_CONTENTS_SCHEMA_VERSION = 4` — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py); `CURRENT_EXP_SCHEMA_VERSION = 62`("The current version of the exploration YAML schema"), `EARLIEST_SUPPORTED_EXP_SCHEMA_VERSION = 46`, `to_yaml`/`from_yaml`("for YAML schema versions 10 and later"); Exploration 필드 id, title, category, objective, language_code, tags, blurb, author_notes, states_schema_version, init_state_name, states, param_specs, param_changes, version, auto_tts_enabled, next_content_id_index, edits_allowed — [exp_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/exp_domain.py)
- `State`: content, param_changes, interaction, solicit_answer_details, `card_is_checkpoint`, `linked_skill_id`, classifier_model_id, inapplicable_skill_misconception_ids; `Outcome`: dest, `dest_if_really_stuck`, feedback, labelled_as_correct, `refresher_exploration_id`("redirect the learner to if they seem to lack understanding of a prerequisite concept"), missing_prerequisite_skill_id; `InteractionInstance`: id, customization_args, answer_groups, default_outcome, confirmed_unclassified_answers, hints, solution — [state_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/state_domain.py)
- 샘플 `hola.yaml`(schema_version 47, states_schema_version 42) 최상위 키: author_notes, auto_tts_enabled, blurb, category, correctness_feedback_enabled, edits_allowed, init_state_name, language_code, objective, param_changes, param_specs, schema_version, states, states_schema_version, tags, title; state 키: content{content_id, html}, interaction{id, answer_groups[{outcome{dest, feedback, labelled_as_correct, …}, rule_specs[{inputs, rule_type}]}], customization_args, default_outcome, hints, solution}, recorded_voiceovers, written_translations; interaction `TextInput`, `MultipleChoiceInput`, `EndExploration`; rule_type `Equals`, `Contains`, `StartsWith`, `FuzzyEquals` — [hola.yaml](https://raw.githubusercontent.com/oppia/oppia/develop/data/explorations/hola.yaml); 샘플 디렉터리 — [data/explorations](https://github.com/oppia/oppia/tree/develop/data/explorations)

### Inferences
- 스킬 그래프 + 스토리 그래프(실질 선형) + 카드 상태기계 3층이 각각 schema_version과 마이그레이션 체인을 가짐 → frontmatter `schema_version` + 마이그레이션 스크립트 관행을 차용. 콘텐츠는 HTML 문자열이며 content_id 단위 번역/음성을 붙임 → Markdown i18n에는 블록 ID 필요. "chapter = lesson + 선행/획득 스킬"은 module→lesson에 직접 대응.

### Gaps
- 최신 62 스키마 YAML 샘플(card_is_checkpoint 등 포함)은 직접 보지 못함; Subtopic page·Question 도메인, YAML 내보내기 UI 미조사.

## KQ6. 상호운용 표준 · 스택 · 최소 요구사항

### Takeaway
Moodle: LTI Advantage(소비자+제공자, AGS/NRPS/Deep Linking), SCORM 1.2+AICC, H5P core, IMS CC 1.0/1.1 in·1.1 out, Open Badges 2.x, core xAPI 라이브러리(LRS 아님); PHP 8.3+, PostgreSQL 17/MySQL 8.4/MariaDB 11.4/MSSQL 2019, 512MB–1GB RAM. Oppia: 표준 지원 근거 없음; Python 3.12 + App Engine + Datastore/NDB + Redis + Firebase + Angular 11(AngularJS 잔존), GCP 종속.

### Cited Findings
- "Learning Tool Interoperability (LTI) Advantage Complete"; "can also act as an LTI 1.1 and 2.0 tool provider"(3.1+); "Moodle complies with the SCORM 1.2 specification"; AICC; "Open Badges v 2.0 compliant as Issuer by IMS"(3.11 v2.1); WCAG 2.1 AA; IMS CC import/export; IMS Enterprise는 플러그인; xAPI는 "community plugins… limited support"; SCORM 2004·xAPI 완전 지원은 상용 mod_scormcloud — [Standards](https://docs.moodle.org/en/Standards)
- Publish as LTI tool: "allows remote users on a different platform to access selected courses and activities"; LTI Advantage(1.3) = core + Assignment and Grade Services, Names and Role Provisioning, Deep Linking; "LTI 1.1 and 2.0 have been deprecated"; 성적 30분 주기 동기화 — [Publish as LTI tool](https://docs.moodle.org/en/Publish_as_LTI_tool); External tool: LTI Advantage/1.1 등록, "Accept grades from the tool", Memberships — [External tool](https://docs.moodle.org/en/External_tool)
- SCORM: "upload and manage SCORM or AICC packages" — [SCORM activity](https://docs.moodle.org/en/SCORM_activity); H5P: 콘텐츠 타입을 h5p.org에서 scheduled task로 설치, 타입별 비활성화, "An H5P activity is one activity" — [H5P](https://docs.moodle.org/en/H5P); xAPI: `core_xapi_statement_post`("process xAPI statements and generate standard Moodle events"), 4.2부터 State API, "NOT to implement a full LRS inside Moodle" — [xAPI API](https://moodledev.io/docs/apis/subsystems/xapi)
- 5.3 요구: 업그레이드는 4.4+; PHP ≥ 8.3.0(8.4 지원), sodium 필수, `max_input_vars` ≥ 5000, 64-bit만; PostgreSQL 17, MySQL 8.4, MariaDB 11.4.0, MS SQL 2019, Aurora MySQL 8.0; "Oracle … is no longer supported from Moodle LMS 5.0" — [5.3 release notes](https://moodledev.io/general/releases/5.3)
- 하드웨어: "200MB for the Moodle code… 5GB is probably a realistic minimum."; "1 GHz (min), 2 GHz dual core or more recommended."; "512MB (min), 1GB or more is recommended."; moodledata는 "should NOT be located inside a web-accessible area"; Nginx/OpenLiteSpeed 가능, 캐시 Redis/Memcached 권장 — [Installing Moodle](https://docs.moodle.org/en/Installing_Moodle)
- Oppia: "Its backend is written in Python, and its frontend is written using AngularJS and Angular."; GAE; 프로덕션 Cloud Datastore via Cloud NDB; `core/platform/models.py`가 스토리지 구현 선택; 도메인 객체 `from_dict/to_dict` + 버전 변환 — [Codebase overview](https://github.com/oppia/oppia/wiki/Overview-of-the-Oppia-codebase)
- `runtime: python312`, `instance_class: F2`, `gunicorn --timeout 60 … main:app`, Datastore 에뮬레이터 localhost:8089, Firebase 에뮬레이터 9099, VPC connector `oppia-redis-connector-1` — [app_dev.yaml](https://raw.githubusercontent.com/oppia/oppia/develop/app_dev.yaml); `@angular/core ^11.2.10`, `typescript ~4.1.6` — [package.json](https://raw.githubusercontent.com/oppia/oppia/develop/package.json)
- 개발 환경: Debian/Ubuntu `install_prerequisites.sh`; curl/git/unzip, openjdk-11-jre("needed for GCP to work"), Google Chrome(테스트), pyenv "install Python 3.12.13", direnv; `python -m scripts.start` → localhost:8181; RAM/디스크 수치 없음, 첫 실행 "about 5 - 10 minutes when we last tested it in Sep 2020" — [Installing Oppia (Linux)](https://github.com/oppia/oppia/wiki/Installing-Oppia-(Linux;-Python-3)); 인덱스는 Linux/Mac/Windows 가이드만 — [Installing Oppia](https://github.com/oppia/oppia/wiki/Installing-Oppia); Docker 경로(검색 스니펫 기준): `make build` 약 2.1GB 다운로드, `make run-devserver` +470MB, WSL2 필수, "Experimental" — [Installing Oppia using Docker](https://www.github.com/oppia/oppia/wiki/Installing-Oppia-using-Docker)
- Oppia README/위키/코드에 LTI, SCORM, xAPI, IMS CC, H5P 언급 없음 — [README](https://github.com/oppia/oppia)

### Inferences
- 기업용 소규모 플랫폼의 최소 상호운용 집합 = LTI 1.3 Tool(AGS) + SCORM 1.2 래핑 + xAPI emitter(외부 LRS). Moodle의 "LAMP 한 대" 배포 무게를 상한으로, 단일 컨테이너 + PostgreSQL/SQLite를 목표. Oppia의 controllers→services→domain→storage 레이어와 스토리지 추상화는 차용, GCP 종속은 회피.
- 과제 전제 "~1,000+ plugin types"는 부정확: 플러그인 *타입*은 56종(플러그인 *개수*는 미조사).

### Gaps
- SCORM 2004 지원 수준, H5P core 도입 버전, mod_h5pactivity의 xAPI 시도 기록, IMS QTI 여부; Oppia Node 버전·Elasticsearch·프로덕션 스케일 미확인.

## KQ7. 진행 · 분석 모델

### Takeaway
Moodle: 활동 완료 조건(view/grade/passing grade/모듈별/수동) → 코스 완료(Any/All; 활동·타 코스·날짜·등록기간·성적·수동) → 성적부 → Events/logstore → 역량 프레임워크·학습계획(evidence, 자동 완료), 5.3 Learning outcomes. Oppia: Completed/IncompleteActivities(ID 리스트), StoryProgress(completed_node_ids), checkpoint, UserSkillMastery(float), LearnerGoals, LearnerGroup(facilitator + subtopic/story syllabus), 진단 테스트.

### Cited Findings
- 활동 완료: None(기본), 수동("Mark as done"), View, Require grade("Getting any grade will mark the activity completed"), Receive a passing grade, Quiz(passing grade/attempts), Lesson(end reached/time spent), Assignment(submit), Forum(posts/discussions/replies); 조건 변경 시 "all completion information for the activity will be deleted then recalculated" — [Activity completion settings](https://docs.moodle.org/en/Activity_completion_settings); 사이트 Advanced features 활성, "Override activity completion" 능력 — [Activity completion](https://docs.moodle.org/en/Activity_completion)
- 코스 완료 "does not have a 'restrict access' function. It is best thought of as a report." — [Course completion](https://docs.moodle.org/en/Course_completion); 조건: Any/All, Activity completion(ALL/ANY), Completion of other courses, Date, Enrolment duration, Unenrolment, Course grade(rawgrade), Manual self-completion, Manual completion by others(역할 ALL/ANY) — [Course completion settings](https://docs.moodle.org/en/Course_completion_settings)
- 성적부: 평가 항목마다 컬럼, raw 점수, 카테고리 총점, 확장은 grade report/import/export 플러그인 — [Grader report](https://docs.moodle.org/en/Gradebook)
- 로깅: Standard("very detailed and should meet most requirements")·External database 로그스토어, Write buffer size, 일부 스토어 write-only(Analytics 불가), Events 서브시스템 기반, Analytics는 로그에 ML — [Logging](https://docs.moodle.org/en/Logging)
- 역량: 프레임워크 → 학습계획 템플릿(학생/코호트 배정, 템플릿 통계) → 코스·활동에 역량 연결(복수) → "Upon activity completion" evidence/검토/완료 → 학생 선행학습 evidence → Competency breakdown 보고서 — [Competencies](https://docs.moodle.org/en/Competencies); 5.3 "Learning outcomes… constructive alignment" — [5.3 release notes](https://moodledev.io/general/releases/5.3)
- Oppia 모델: `CompletedActivitiesModel`(exploration_ids, collection_ids, story_ids, learnt_topic_ids, mastered_topic_ids), `IncompleteActivitiesModel`(partially_learnt/mastered_topic_ids), `StoryProgressModel`(`[user_id].[story_id]`, completed_node_ids), `ExplorationUserDataModel`(rating 1–5, "furthest and most recently reached checkpoint"), `LearnerGoalsModel`(topic_ids_to_learn/master), `UserSkillMasteryModel`("Model for storing a user's degree of mastery of a skill", `degree_of_mastery` FloatProperty) — [user gae_models.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/storage/user/gae_models.py)
- `LearnerGroup`: facilitator_user_ids, learner_user_ids, invited_learner_user_ids, `subtopic_page_ids`("`topicId:subtopicId`"), story_ids; facilitator ≥ 1 — [learner_group_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/learner_group_domain.py); `MAX_CURRENT_GOALS_COUNT = 5`, `/create-learner-group` — [core/feconf.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/feconf.py)
- Practice session(검색 스니펫 기준, 2023 제품 스펙): subtopic 선택 → 10문항 → 세션/스킬별 점수, 첫 시도 정답 기준 숙련도 표시 — [Practice sessions spec](https://docs.google.com/document/d/1r9IEQ5z_t-eu9XAWN3eRA7iKdKuYsOQbVUjO2ZH1qKg/export?format=pdf); v3.5.3에서 Learner Dashboard Progress 탭의 Skills 섹션 제거 — [v3.5.3](https://github.com/oppia/oppia/releases/tag/v3.5.3)

### Inferences
- Moodle 교훈: 완료·성적·역량을 별개 엔티티로 두고 완료 조건을 모듈별 선언. 단일 코스는 (a) lesson 완료 조건 (b) module/course ALL/ANY 집계 (c) 선택적 역량 매핑 3단이면 충분. Oppia의 "ID 리스트" 진행 저장 + skill float + checkpoint는 구현 비용이 매우 낮음. append-only 이벤트 테이블이 감사 로그와 학습 분석을 동시에 해결.

### Gaps
- Moodle 이벤트 필드 스키마, 성적 집계 방식 목록; Oppia `degree_of_mastery` 범위/갱신 알고리즘, topic 숙련도 계산식 미확인.

## KQ8. 설계 포인트와 비교표

### Takeaway
차용: ① Moodle `component:action` 능력 + 컨텍스트 트리 + Inherit/Allow/Prevent/Prohibit, ② Oppia 스킬 그래프(lesson frontmatter `prerequisite_skills`/`acquired_skills`) + `degree_of_mastery` + checkpoint/`dest_if_really_stuck`, ③ Oppia schema_version + 마이그레이션 체인, ④ Moodle 완료 조건→집계→역량 3단 + 이벤트 로그, ⑤ `.mbz`식 manifest+파일+해시 스토어 내보내기, ⑥ 5.3식 scope 토큰 + OpenAPI. 회피: Moodle RPC `wsfunction`·HTML 중심 저작, Oppia GCP 종속·공개 API 부재·평면 역할 난립·HTML 문자열 콘텐츠.

### Cited Findings
| 항목 | Moodle LMS | Oppia |
|---|---|---|
| 라이선스 | GPL-3.0 — [COPYING.txt](https://raw.githubusercontent.com/moodle/moodle/main/COPYING.txt) | Apache-2.0 — [LICENSE](https://raw.githubusercontent.com/oppia/oppia/develop/LICENSE) |
| 현재 버전 | 5.3 LTS(2026-10-05); 6.0 2027-04 예정 — [Releases](https://moodledev.io/general/releases) | v3.5.3(2026-09-23) — [GitHub API](https://api.github.com/repos/oppia/oppia/releases/latest) |
| 주기 / CLA | 6개월 메이저, 2개월 마이너 / CLA 근거 없음 — [Process](https://moodledev.io/general/development/process) | 월간 cut(실제 2~4개월) / CLA 필수 — [Contributing](https://github.com/oppia/oppia/wiki/Contributing-code-to-Oppia) |
| 거버넌스 | Moodle Pty Ltd; MUA 2024 해산 → PAG — [MUA](https://moodle.org/mua) | Oppia Foundation 501(c)(3) — [ProPublica](https://projects.propublica.org/nonprofits/organizations/811740068) |
| 로그인 | Manual/Email/LDAP/LTI/OAuth 2(OIDC)/Shibboleth/MFA; SAML2 서드파티 — [Managing authentication](https://docs.moodle.org/en/Managing_authentication) | Firebase Auth(OIDC), 세션 쿠키 14일 — [firebase_auth_services.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/platform/auth/firebase_auth_services.py) |
| 권한 | 역할×능력×컨텍스트(10/30/40/50/70/80), 4값 override — [Override permissions](https://docs.moodle.org/en/Override_permissions) | 평면 역할 16종→액션 집합 + owner/manager ID — [role_services.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/role_services.py) |
| API | `wstoken` RPC + 5.3 scope REST(PAT/OAuth 2, SwaggerUI) — [REST API tokens](https://docs.moodle.org/en/REST_API_tokens) | 공개 API 없음, 내부 핸들러 + ACL 데코레이터 — [acl_decorators.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/controllers/acl_decorators.py) |
| 콘텐츠 계층 | course → section → activity; Book/Page/Lesson — [Course formats](https://docs.moodle.org/en/Course_formats) | classroom → topic → story → chapter → exploration(state); skill/subtopic — [story_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/story_domain.py) |
| 포맷 | HTML 중심, Markdown 옵션; `.mbz`(tgz, moodle_backup.xml) — [Backup FAQ](https://docs.moodle.org/en/Backup_and_restore_FAQ) | HTML 콘텐츠; exploration YAML schema 62 — [exp_domain.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/domain/exp_domain.py) |
| 표준 | LTI Advantage, SCORM 1.2/AICC, H5P, IMS CC 1.1, Open Badges, xAPI lib — [Standards](https://docs.moodle.org/en/Standards) | 확인된 지원 없음 — [README](https://github.com/oppia/oppia) |
| 스택 | PHP 8.3+, PG 17/MySQL 8.4/MariaDB 11.4; 512MB–1GB RAM — [5.3 notes](https://moodledev.io/general/releases/5.3) | Python 3.12 GAE + Datastore + Redis + Firebase; Angular 11 — [app_dev.yaml](https://raw.githubusercontent.com/oppia/oppia/develop/app_dev.yaml) |
| 진행 | 활동/코스 완료 → 성적부 → logstore → 역량 — [Competencies](https://docs.moodle.org/en/Competencies) | 완료 ID 리스트, StoryProgress, skill mastery float, LearnerGroup — [user gae_models.py](https://raw.githubusercontent.com/oppia/oppia/develop/core/storage/user/gae_models.py) |

### Inferences
1. 권한: `course:edit`, `lesson:view`, `progress:read_any` 식 능력 + system/course/module/lesson 4단 컨텍스트 + archetype(admin/author/reviewer/learner) + Prohibit 포함 override; 보조로 리소스 owner 리스트.
2. 콘텐츠: lesson frontmatter `id, schema_version, module, order, prerequisite_skills[], acquired_skills[], checkpoint, next[]`; `skills/*.yaml`(description, rubric, misconceptions, prerequisites); vN→vN+1 마이그레이션 체인.
3. 진행: append-only 이벤트 → lesson 완료 조건(viewed/quiz_passed/manual) → module/course ALL/ANY → skill `degree_of_mastery`.
4. API: OpenAPI + PAT/OAuth2(OIDC) scope 토큰, 내부 UI도 동일 API 사용.
5. 내보내기: manifest+파일 zip(.mbz 교훈), SCORM 1.2 래핑, LTI 1.3 Tool(AGS).
6. 배포: 단일 컨테이너 + PostgreSQL/SQLite + 파일 스토어, IdP는 선택적 어댑터.

### Gaps
- 설계 포인트는 본 조사 추론이며 사용자 커뮤니티 만족도/이슈 통계, 플러그인 총수, Oppia 규모 지표·WCAG 상태는 미수집.
