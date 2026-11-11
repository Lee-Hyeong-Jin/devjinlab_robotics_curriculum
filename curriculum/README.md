# curriculum/

This directory holds the course content: lessons as Markdown with YAML front matter,
organized as Course (Track) > Module > Lesson > Activity.

- Layout, front matter fields and validation rules: `docs/curriculum/CONTENT_MODEL.md`
- Copy-pasteable lesson skeleton: `docs/curriculum/LESSON_TEMPLATE.md`
- Validate everything here: `uv run rc validate` (or `rc validate curriculum/<course>`)

Courses:

- `robotics-basics/` — 로보틱스 기초 (PRD 부록 A). Modules M1~M2 are stubbed; M3~M5 to follow.
