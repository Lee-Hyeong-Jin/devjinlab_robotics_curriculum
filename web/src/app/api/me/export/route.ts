import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

import { apiBaseUrl, apiTimeoutMs } from '@/lib/api/config'

/**
 * Streams `GET /api/v1/me/export` back to the browser as a download.
 *
 * The export needs the caller's session, which lives in an HttpOnly cookie this
 * origin holds — the browser cannot call the API directly across origins. This
 * route forwards the cookie and nothing else, and never caches the result.
 */
export async function GET(request: Request): Promise<Response> {
  const jar = await cookies()
  const all = jar.getAll()
  const headers = new Headers({ Accept: 'application/json' })
  if (all.length > 0) {
    headers.set('Cookie', all.map((cookie) => `${cookie.name}=${cookie.value}`).join('; '))
  }

  let upstream: Response
  try {
    upstream = await fetch(`${apiBaseUrl()}/api/v1/me/export`, {
      headers,
      cache: 'no-store',
      signal: AbortSignal.timeout(apiTimeoutMs()),
    })
  } catch {
    return NextResponse.json(
      { title: 'Bad Gateway', status: 502, detail: 'The API could not be reached.' },
      { status: 502, headers: { 'content-type': 'application/problem+json' } },
    )
  }

  if (upstream.status === 401) {
    return NextResponse.redirect(new URL('/login?next=/profile', request.url), 302)
  }
  if (!upstream.ok) {
    return new NextResponse(upstream.body, {
      status: upstream.status,
      headers: {
        'content-type': upstream.headers.get('content-type') ?? 'application/problem+json',
      },
    })
  }

  const stamp = new Date().toISOString().slice(0, 10)
  return new NextResponse(upstream.body, {
    status: 200,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'content-disposition': `attachment; filename="robotics-curriculum-export-${stamp}.json"`,
      'cache-control': 'no-store',
    },
  })
}
