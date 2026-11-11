# curriculum/

This directory holds the course content: lessons as Markdown with YAML front matter,
organized as Course (Track) > Module > Lesson > Activity.

- Layout, front matter fields and validation rules: `docs/curriculum/CONTENT_MODEL.md`
- Copy-pasteable lesson skeleton: `docs/curriculum/LESSON_TEMPLATE.md`
- Validate everything here: `uv run rc validate` (or `rc validate curriculum/<course>`)

Courses:

- `robotics-expert/` — 로보틱스 전문가 코스 (기초→중급→고급). 기초 단계 M1~M3 written; later stages to follow.

Content in this directory is licensed under [CC BY 4.0](LICENSE) (Creative Commons Attribution 4.0 International); code elsewhere in the repository is Apache-2.0.
