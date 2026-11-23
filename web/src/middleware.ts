import { NextResponse, type NextFetchEvent, type NextRequest } from 'next/server'

import { CURRENT_PATH_HEADER } from '@/lib/api/client'
import {
  adminForbidden,
  contentTarget,
  contentVerdict,
  isDocumentRequest,
} from '@/lib/content-status'
import { pageViewRequest } from '@/lib/pageview'
import { contentSecurityPolicy, HSTS, STATIC_SECURITY_HEADERS } from '@/lib/security-headers'

/** Request header carrying the per-request CSP nonce to the root layout. */
export const NONCE_HEADER = 'x-nonce'

/**
 * Publishes the current path as a request header so a 401 from the API can send
 * the reader to `/login?next=<current path>` (frontend.md §1 "인증 처리"), and
 * sets the response security headers (`lib/security-headers.ts`).
 *
 * Route protection itself stays on the API: the frontend never decides access
 * (AC-WEB.4).
 */
export async function middleware(request: NextRequest, event: NextFetchEvent) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')
  const headers = new Headers(request.headers)
  const { pathname, search } = request.nextUrl
  headers.set(CURRENT_PATH_HEADER, `${pathname}${search}`)
  headers.set(NONCE_HEADER, nonce)

  // HSTS only over HTTPS: a browser ignores it on plain HTTP, and local runs and the E2E
  // suite serve the app over HTTP on purpose.
  const https =
    request.headers.get('x-forwarded-proto') === 'https' || request.nextUrl.protocol === 'https:'
  const csp = contentSecurityPolicy({
    nonce,
    dev: process.env.NODE_ENV !== 'production',
    https,
  })
  headers.set('content-security-policy', csp)

  const response = await respond(request, headers)
  reportPageView(request, response, event)
  response.headers.set('Content-Security-Policy', csp)
  for (const { key, value } of STATIC_SECURITY_HEADERS) response.headers.set(key, value)
  if (https) response.headers.set('Strict-Transport-Security', HSTS)
  return response
}

/**
 * Tell the API that a page was viewed (`lib/pageview.ts`, ADR 0017).
 *
 * Fire and forget: the response does not wait for it, and a failure is silent, because a visit
 * that is not counted is better than a page that is not served. Redirects and not-found answers
 * are not views.
 */
function reportPageView(request: NextRequest, response: NextResponse, event: NextFetchEvent): void {
  // Full page loads only. Navigations inside the app are often served from the router's cache
  // without a request, so the browser reports those itself (`<PageViewBeacon>`).
  if (
    response.status >= 300 ||
    request.method !== 'GET' ||
    !isDocumentRequest(request.method, request.headers)
  ) {
    return
  }
  const report = pageViewRequest(
    request.nextUrl.pathname,
    request.nextUrl.search,
    request.headers,
    request.cookies,
  )
  if (!report) return
  event.waitUntil(fetch(report.url, report.init).catch(() => undefined))
}

/** Missing content answers 404 and the `/lessons/{id}` shortcut 308 (`lib/content-status.ts`). */
async function respond(request: NextRequest, headers: Headers): Promise<NextResponse> {
  const target = contentTarget(request.nextUrl.pathname)
  if (target && isDocumentRequest(request.method, request.headers)) {
    const verdict = await contentVerdict(target, request.headers.get('cookie'))
    if (verdict.status === 'moved') {
      const url = request.nextUrl.clone()
      url.pathname = verdict.location
      return NextResponse.redirect(url, 308)
    }
    if (verdict.status === 'missing') {
      // A path no route matches renders the app's not-found page with a 404 status line.
      const url = request.nextUrl.clone()
      url.pathname = '/_missing'
      return NextResponse.rewrite(url, { request: { headers }, status: 404 })
    }
  }
  if (
    isDocumentRequest(request.method, request.headers) &&
    (await adminForbidden(request.nextUrl.pathname, request.headers.get('cookie')))
  ) {
    // The same page, which renders the "no permission" screen, under the status that says so.
    return NextResponse.rewrite(request.nextUrl, { request: { headers }, status: 403 })
  }
  return NextResponse.next({ request: { headers } })
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
