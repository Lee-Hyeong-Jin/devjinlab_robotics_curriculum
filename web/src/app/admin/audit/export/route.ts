import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'

import { apiBaseUrl, apiTimeoutMs } from '@/lib/api/config'
import { browserIdentity } from '@/lib/api/forward'

/** The filters `GET /api/v1/admin/audit/export` accepts; anything else is dropped. */
const FILTERS = ['action', 'actor_user_id', 'target_type', 'target_id', 'since', 'until'] as const

/**
 * Streams `GET /api/v1/admin/audit/export` back to the browser as a CSV download.
 *
 * Same shape as `/api/me/export`: the session lives in an HttpOnly cookie this origin holds,
 * so the browser cannot ask the API itself. The API checks the admin role; this route only
 * forwards the cookie and the known filters, and never caches the result.
 */
export async function GET(request: Request): Promise<Response> {
  const jar = await cookies()
  const all = jar.getAll()
  const headers = new Headers({ Accept: 'text/csv', ...(await browserIdentity()) })
  if (all.length > 0) {
    headers.set('Cookie', all.map((cookie) => `${cookie.name}=${cookie.value}`).join('; '))
  }

  const incoming = new URL(request.url).searchParams
  const query = new URLSearchParams()
  for (const name of FILTERS) {
    const value = incoming.get(name)
    if (value) query.set(name, value)
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : ''

  let upstream: Response
  try {
    upstream = await fetch(`${apiBaseUrl()}/api/v1/admin/audit/export${suffix}`, {
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
    return NextResponse.redirect(new URL('/login?next=/admin/audit', request.url), 302)
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
      'content-type': 'text/csv; charset=utf-8',
      'content-disposition': `attachment; filename="audit-log-${stamp}.csv"`,
      'cache-control': 'no-store',
      'x-truncated': upstream.headers.get('x-truncated') ?? 'false',
    },
  })
}
