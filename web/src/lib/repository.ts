/**
 * Links from the site back to the repository the curriculum is written in (#54).
 *
 * A reader who finds a mistake had no way to say so from the page they were reading, and
 * nowhere on the site said the course is open source. The address comes from configuration:
 * a self-hosted copy points `RC_REPO_URL` at its own fork, or sets it to `off` when its
 * content is not on GitHub, and every such link disappears.
 */
export const DEFAULT_REPOSITORY_URL =
  'https://github.com/Lee-Hyeong-Jin/devjinlab_robotics_curriculum'

/** The branch "suggest an edit" opens the file on. */
const EDIT_BRANCH = 'main'

/** The content-issue form (`.github/ISSUE_TEMPLATE/content_issue.yml`) and its lesson field. */
const CONTENT_ISSUE_TEMPLATE = 'content_issue.yml'

/** The repository's address without a trailing slash, or `null` when links are turned off. */
export function repositoryUrl(): string | null {
  const raw = process.env.RC_REPO_URL?.trim()
  if (raw === undefined || raw === '') return DEFAULT_REPOSITORY_URL
  if (['off', '0', 'false', 'none'].includes(raw.toLowerCase())) return null
  try {
    const url = new URL(raw)
    if (url.protocol !== 'https:' && url.protocol !== 'http:') return null
    return `${url.origin}${url.pathname}`.replace(/\/+$/, '')
  } catch {
    return null
  }
}

/** The new-issue form for a problem in one lesson, with the lesson filled in. */
export function lessonIssueUrl(repository: string, lessonId: string, title: string): string {
  const params = new URLSearchParams({
    template: CONTENT_ISSUE_TEMPLATE,
    title: `[content] ${title}`,
    lesson: lessonId,
  })
  return `${repository}/issues/new?${params.toString()}`
}

/**
 * GitHub's editor on the lesson's source file, or `null` when the path is not one of ours.
 *
 * The path comes from the API; only a plain path under `curriculum/` is accepted, so nothing
 * else can be smuggled into the link.
 */
export function lessonEditUrl(
  repository: string,
  sourcePath: string | null | undefined,
): string | null {
  if (!sourcePath || !/^curriculum\/[A-Za-z0-9._\-/]+\.md$/.test(sourcePath)) return null
  if (sourcePath.split('/').some((part) => part === '..' || part === '')) return null
  return `${repository}/edit/${EDIT_BRANCH}/${sourcePath}`
}

/**
 * Where readers ask questions and find study partners (`RC_COMMUNITY_URL`), or `null`.
 *
 * There is no default: the link must lead somewhere that exists. This project's place is
 * GitHub Discussions, which a repository owner has to switch on first; until a deployment
 * names its place, the site offers no such link rather than one that answers 404.
 */
export function communityUrl(): string | null {
  const raw = process.env.RC_COMMUNITY_URL?.trim()
  if (!raw) return null
  try {
    const url = new URL(raw)
    return url.protocol === 'https:' ? url.toString() : null
  } catch {
    return null
  }
}
