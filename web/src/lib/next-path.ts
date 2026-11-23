/**
 * Only a same-origin path is accepted as a post-login destination, so a crafted
 * `?next=https://evil.example` cannot turn the login screen into an open redirect.
 *
 * "Starts with one slash" is not enough. A browser reads `/\\host` as `//host`, and drops
 * tabs and newlines before parsing, so `/<tab>/host` is `//host` as well: both leave the site.
 * The rule is therefore strict: a slash, then something that is neither a slash nor a
 * backslash, no backslash or control character anywhere, and the URL parser must agree that
 * the result stays on this origin.
 */
const ORIGIN = 'http://same-origin.invalid'

export function safeNext(next: string | null | undefined): string {
  if (!next || next.length > 2048) return '/'
  if (!next.startsWith('/') || next.startsWith('//')) return '/'
  if (next.includes('\\')) return '/'
  for (const char of next) {
    const code = char.codePointAt(0) ?? 0
    if (code < 0x20 || code === 0x7f) return '/'
  }
  try {
    const url = new URL(next, ORIGIN)
    if (url.origin !== ORIGIN) return '/'
  } catch {
    return '/'
  }
  return next
}

/** Where a reader whose session has ended is sent: the cookie is dropped there, then login. */
export const SESSION_EXPIRED_PATH = '/session/expired'

/** `/session/expired?next=<path>` for a path the reader was on. */
export function sessionExpiredUrl(next: string): string {
  return `${SESSION_EXPIRED_PATH}?next=${encodeURIComponent(safeNext(next))}`
}

/** `/login?next=<path>`; `expired` adds the "your session has ended" notice. */
export function loginUrl(next: string, expired = false): string {
  const safe = safeNext(next)
  const params = new URLSearchParams()
  if (safe !== '/') params.set('next', safe)
  if (expired) params.set('expired', '1')
  const query = params.toString()
  return query ? `/login?${query}` : '/login'
}
