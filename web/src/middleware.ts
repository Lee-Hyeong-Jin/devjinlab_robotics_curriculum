import { NextResponse, type NextRequest } from 'next/server'

import { CURRENT_PATH_HEADER } from '@/lib/api/client'
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
export function middleware(request: NextRequest) {
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

  const response = NextResponse.next({ request: { headers } })
  response.headers.set('Content-Security-Policy', csp)
  for (const { key, value } of STATIC_SECURITY_HEADERS) response.headers.set(key, value)
  if (https) response.headers.set('Strict-Transport-Security', HSTS)
  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
