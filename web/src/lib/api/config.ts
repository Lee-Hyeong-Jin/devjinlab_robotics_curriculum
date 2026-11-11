/** Server-side API configuration. Read from the environment, never shipped to the browser. */

export const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000'
export const DEFAULT_COURSE_ID = 'robotics-expert'
export const DEFAULT_TIMEOUT_MS = 10_000

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

/** Per-request timeout in milliseconds. */
export function apiTimeoutMs(): number {
  const parsed = Number(process.env.RC_API_TIMEOUT_MS)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : DEFAULT_TIMEOUT_MS
}
