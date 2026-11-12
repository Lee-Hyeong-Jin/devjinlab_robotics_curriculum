/** Server-side API configuration. Read from the environment, never shipped to the browser. */

export const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000'
export const DEFAULT_COURSE_ID = 'robotics-expert'
export const DEFAULT_TIMEOUT_MS = 10_000
export const DEFAULT_SITE_URL = 'http://localhost:3000'

/** Base URL of the `rc api serve` backend, without a trailing slash. */
export function apiBaseUrl(): string {
  const raw = process.env.RC_API_BASE_URL?.trim()
  return (raw && raw.length > 0 ? raw : DEFAULT_API_BASE_URL).replace(/\/+$/, '')
}

/** Course shown on the dashboard and the roadmap until course selection lands. */
export function defaultCourseId(): string {
  const raw = process.env.RC_DEFAULT_COURSE_ID?.trim()
  return raw && raw.length > 0 ? raw : DEFAULT_COURSE_ID
}

/**
 * Whether the curriculum is readable without a session (`RC_PUBLIC_CONTENT`, ADR 0016).
 *
 * The web needs to know as well as the API: it decides whether a content page renders for an
 * anonymous reader and whether that page may be indexed. Mirrors the API's default (off).
 */
export function publicContentEnabled(): boolean {
  return process.env.RC_PUBLIC_CONTENT === '1'
}

/**
 * Public base URL of this site, without a trailing slash — for canonical links, hreflang,
 * the sitemap and OpenGraph.
 *
 * `RC_PUBLIC_URL` is the same variable the API uses for the links it mails, so a deployment
 * sets one address rather than two.
 */
export function siteUrl(): string {
  const raw = process.env.RC_PUBLIC_URL?.trim()
  return (raw && raw.length > 0 ? raw : DEFAULT_SITE_URL).replace(/\/+$/, '')
}

/** Per-request timeout in milliseconds. */
export function apiTimeoutMs(): number {
  const parsed = Number(process.env.RC_API_TIMEOUT_MS)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : DEFAULT_TIMEOUT_MS
}
