import { NextResponse, type NextRequest } from 'next/server'

import { CURRENT_PATH_HEADER } from '@/lib/api/client'

/**
 * Publishes the current path as a request header so a 401 from the API can send
 * the reader to `/login?next=<current path>` (frontend.md §1 "인증 처리").
 *
 * Route protection itself stays on the API: the frontend never decides access
 * (AC-WEB.4). Once the P2-2 session API lands, this is also where an absent `sid`
 * cookie short-circuits to `/login`.
 */
export function middleware(request: NextRequest) {
  const headers = new Headers(request.headers)
  const { pathname, search } = request.nextUrl
  headers.set(CURRENT_PATH_HEADER, `${pathname}${search}`)
  return NextResponse.next({ request: { headers } })
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
