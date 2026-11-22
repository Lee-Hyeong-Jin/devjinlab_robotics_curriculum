import { LOCALE_COOKIE, LOCALE_PARAM, resolveLocale } from '@/i18n/locales'

import { SESSION_COOKIE_NAME } from './api/client'
import { apiBaseUrl } from './api/config'

/**
 * Page-view reporting (ADR 0017).
 *
 * The web server tells the API about each page it serves: no script runs in the browser and no
 * cookie is set. What is sent is the path, the language, the referring page and whether the
 * reader has a session; the browser's address and user agent travel as headers so the API can
 * derive its daily visitor pseudonym, and are not stored.
 */

const NOT_PAGES = /^\/(?:api|admin|_next)(?:\/|$)|\.[a-z0-9]{2,12}$/i

/** Whether a path is a page worth counting (not an asset, an API route or the admin console). */
export function countsAsPage(pathname: string): boolean {
  return !NOT_PAGES.test(pathname)
}

/**
 * The referring page, unless it is this site: moving between our own pages is not a source of
 * visits. The site's host is whatever the browser called it (`Host`, or the proxy's
 * `X-Forwarded-Host`), which is right behind any proxy without configuration.
 */
function externalReferrer(headers: Headers): string | null {
  const referrer = headers.get('referer')
  if (!referrer) return null
  const own = (headers.get('x-forwarded-host') ?? headers.get('host') ?? '').split(',')[0]?.trim()
  try {
    return new URL(referrer).host === own ? null : referrer
  } catch {
    // Not a URL at all: nothing worth passing on.
    return null
  }
}

export interface PageViewRequest {
  url: string
  init: RequestInit
}

/** The request that reports one page view, or `null` when this request is not one to count. */
export function pageViewRequest(
  pathname: string,
  search: string,
  headers: Headers,
  cookies: { get(name: string): { value: string } | undefined },
): PageViewRequest | null {
  if (!countsAsPage(pathname)) return null
  const locale = resolveLocale(
    cookies.get(LOCALE_COOKIE)?.value,
    headers.get('accept-language'),
    new URLSearchParams(search).get(LOCALE_PARAM),
  )
  const forwarded: Record<string, string> = { 'Content-Type': 'application/json' }
  const forwardedFor = headers.get('x-forwarded-for')
  if (forwardedFor) forwarded['X-Forwarded-For'] = forwardedFor
  const userAgent = headers.get('user-agent')
  if (userAgent) forwarded['User-Agent'] = userAgent
  return {
    url: `${apiBaseUrl()}/api/v1/telemetry/pageview`,
    init: {
      method: 'POST',
      headers: forwarded,
      body: JSON.stringify({
        path: pathname,
        locale,
        referrer: externalReferrer(headers),
        signed_in: cookies.get(SESSION_COOKIE_NAME) !== undefined,
      }),
      cache: 'no-store',
      // A slow API must not hold a page back or pile requests up.
      signal: AbortSignal.timeout(1500),
    },
  }
}
