# ADR 0008: Web frontend — Next.js (App Router)

- Status: Accepted
- Date: 2026-11-11
- Deciders: project lead (orchestrator), on the architect's recommendation
- Related: `docs/platform-design.md` §1.2, `docs/architecture/frontend.md`

## Context

Phase 2 adds a server mode (FastAPI + PostgreSQL + authentication) with a browser
frontend for the learning screens that the CLI and the static site cover today:
dashboard, roadmap, lesson (with the "이 단계 공부법" section and resources), resources,
login/signup, profile, and admin.

The frontend has to render lesson bodies that contain KaTeX math, code blocks and
Mermaid diagrams, support Korean and English UI, meet WCAG 2.1 AA, and keep page LCP
under 2.5 s (PRD section 7). The project is open source, so the size of the contributor
pool matters as much as raw runtime performance.

Two candidates were compared in `docs/platform-design.md` §1.2: Next.js (App Router,
React) and SvelteKit.

## Decision

Use **Next.js with the App Router** for `web/`.

- React 19 + TypeScript, App Router with React Server Components.
- Tailwind CSS with CSS custom properties bound to the Figma `Tokens` collection
  (light and dark mode).
- `next-intl` for ko/en message catalogs.
- Lesson bodies arrive as HTML from the API (`body_html`, `study_method_html`); KaTeX
  and Mermaid render on the client.
- API access through a generated client from `docs/api/openapi.yaml`; the frontend never
  imports the Python core.

`web/` implementation starts only after the P2-1 API is merged. Until then the contract
(OpenAPI) and the Figma screens are the frozen interface.

## Rationale

- **Contributor reach.** React has the largest pool of potential open-source
  contributors, which is the dominant constraint for a project that wants outside help.
- **Content rendering.** `rehype-katex`, `rehype-pretty-code` and the MDX ecosystem are
  mature; SvelteKit's `mdsvex` path has fewer maintained plugins.
- **Performance budget.** RSC plus incremental static regeneration lets lesson pages,
  which are read-mostly and identical for every learner, be served as static HTML with
  only progress-dependent islands hydrated. That is the cheapest route to the 2.5 s LCP
  target.
- **i18n and accessibility tooling.** `next-intl` and `eslint-plugin-jsx-a11y` plus
  headless component libraries (Radix) cover the WCAG 2.1 AA checklist with established
  patterns.

SvelteKit would give smaller bundles and a gentler learning curve, but neither outweighs
contributor reach for an open-source project.

## Consequences

- Larger client bundles than SvelteKit; mitigated by server components and by keeping
  interactivity to islands (timer, quiz, review, admin tables).
- The team carries React/RSC complexity, including its caching model. The frontend guide
  (`docs/architecture/frontend.md`) pins the patterns so contributors do not have to
  rediscover them.
- Node.js enters the toolchain and the deployment (a `web` container in
  `deploy/compose.yaml`). The local mode (CLI + static site) stays Python-only and is
  unaffected.
- Design tokens must be exported from Figma to CSS variables; drift between Figma and
  `web/` is a review item.
