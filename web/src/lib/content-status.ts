import { apiBaseUrl } from './api/config'

/**
 * Real HTTP statuses for content URLs (frontend.md §5.2).
 *
 * The page for a module or a lesson streams: the response starts before the page has asked the
 * API whether the id exists, so an unknown id used to answer `200` with a not-found screen (a
 * "soft 404"), and the `/lessons/{id}` shortcut answered `200` with a client-side redirect.
 * A crawler wants the status line to say it. The middleware asks the API first, for document
 * requests only, and answers 404 or 308 itself.
 */

export type ContentTarget =
  | { kind: 'module'; moduleId: string }
  | { kind: 'lesson'; moduleId: string; lessonId: string }
  | { kind: 'shortcut'; lessonId: string }

const MODULE_PATH = /^\/modules\/([^/]+)(?:\/([^/]+))?(?:\/quiz)?\/?$/
// A module's report exists exactly when the module does.
const REPORT_PATH = /^\/reports\/modules\/([^/]+)\/?$/
const SHORTCUT_PATH = /^\/lessons\/([^/]+)\/?$/

/** Which content a path names, or `null` for every other page. */
export function contentTarget(pathname: string): ContentTarget | null {
  const shortcut = SHORTCUT_PATH.exec(pathname)
  if (shortcut?.[1]) return { kind: 'shortcut', lessonId: decodeURIComponent(shortcut[1]) }
  const report = REPORT_PATH.exec(pathname)
  if (report?.[1]) return { kind: 'module', moduleId: decodeURIComponent(report[1]) }
  const match = MODULE_PATH.exec(pathname)
  if (!match?.[1]) return null
  const moduleId = decodeURIComponent(match[1])
  return match[2]
    ? { kind: 'lesson', moduleId, lessonId: decodeURIComponent(match[2]) }
    : { kind: 'module', moduleId }
}

/**
 * Whether a request is a full page load, the only kind whose status line anybody reads and the
 * only kind the server counts as a visit.
 *
 * The router's own requests (navigations, prefetches) must not match. Their marker headers
 * (`rsc`, `next-router-prefetch`) are checked, but Next removes them before the middleware
 * runs, so the deciding signal is the browser's `Sec-Fetch-Dest`: `document` for a page load,
 * `empty` for anything fetched by script. Clients that do not send it (crawlers, curl) are
 * judged by `Accept`.
 */
export function isDocumentRequest(method: string, headers: Headers): boolean {
  if (method !== 'GET' && method !== 'HEAD') return false
  if (
    headers.has('rsc') ||
    headers.has('next-router-prefetch') ||
    headers.has('next-router-segment-prefetch')
  ) {
    return false
  }
  const destination = headers.get('sec-fetch-dest')
  if (destination !== null) return destination === 'document'
  const accept = headers.get('accept') ?? ''
  return accept === '' || accept.includes('text/html') || accept.includes('*/*')
}

export type ContentVerdict =
  { status: 'ok' } | { status: 'missing' } | { status: 'moved'; location: string }

const TIMEOUT_MS = 2000

async function getJson(path: string, cookie: string | null): Promise<Response | null> {
  try {
    return await fetch(`${apiBaseUrl()}${path}`, {
      headers: { Accept: 'application/json', ...(cookie ? { Cookie: cookie } : {}) },
      cache: 'no-store',
      signal: AbortSignal.timeout(TIMEOUT_MS),
    })
  } catch {
    return null
  }
}

/**
 * Ask the API whether the content exists.
 *
 * Only a definite `404` says "missing". Anything else — the API being slow or down, a `401` on a
 * deployment that publishes nothing — is `ok`: the page itself deals with those, and a check
 * that guesses would turn an outage into a site full of 404s.
 */
export async function contentVerdict(
  target: ContentTarget,
  cookie: string | null,
): Promise<ContentVerdict> {
  if (target.kind === 'shortcut') {
    const response = await getJson(`/api/v1/lessons/${encodeURIComponent(target.lessonId)}`, cookie)
    if (response?.status === 404) return { status: 'missing' }
    if (!response?.ok) return { status: 'ok' }
    const lesson = (await response.json().catch(() => null)) as {
      id?: string
      module_id?: string
    } | null
    if (!lesson?.id || !lesson.module_id) return { status: 'ok' }
    return {
      status: 'moved',
      location: `/modules/${encodeURIComponent(lesson.module_id)}/${encodeURIComponent(lesson.id)}`,
    }
  }

  // The module answer is small and lists its lesson ids, so it settles both kinds of page.
  const response = await getJson(`/api/v1/modules/${encodeURIComponent(target.moduleId)}`, cookie)
  if (response?.status === 404) return { status: 'missing' }
  if (!response?.ok || target.kind === 'module') return { status: 'ok' }
  const found = (await response.json().catch(() => null)) as {
    lessons?: Array<{ id?: string }>
  } | null
  if (!found?.lessons) return { status: 'ok' }
  return found.lessons.some((lesson) => lesson.id === target.lessonId)
    ? { status: 'ok' }
    : { status: 'missing' }
}

/**
 * Whether the admin console must answer `403` for this request.
 *
 * The console's layout shows a "no permission" screen to a signed-in reader who is not an
 * admin, but a streamed page has already said `200` by then (QA B-28). The API is the one that
 * decides; this only asks it who is calling so the status line can say the same thing. `true`
 * only on a definite answer — a signed-in account whose role is not admin. No session, an
 * unreachable API or anything unexpected is left to the page (which redirects to the login
 * screen or shows its own error).
 */
export async function adminForbidden(pathname: string, cookie: string | null): Promise<boolean> {
  if (!/^\/admin(?:\/|$)/.test(pathname) || !cookie) return false
  const response = await getJson('/api/v1/me', cookie)
  if (!response?.ok) return false
  const me = (await response.json().catch(() => null)) as { role?: string } | null
  return typeof me?.role === 'string' && me.role !== 'admin'
}
