import { cookies } from 'next/headers'

import { pageViewRequest } from '@/lib/pageview'

/**
 * Receives the browser's report of a navigation inside the app and passes it to the API
 * (`<PageViewBeacon>`, ADR 0017).
 *
 * A full page load is counted by the middleware. A click on a link, though, is often served
 * from the router's cache with no request at all, so the browser says where it went. Only
 * same-origin reports are accepted, the path goes through the same filter as everywhere else,
 * and the answer is empty either way: this endpoint tells a caller nothing.
 */
export async function POST(request: Request): Promise<Response> {
  const done = new Response(null, { status: 204, headers: { 'cache-control': 'no-store' } })
  // A browser says where a request comes from; anything that is not this site is ignored.
  const site = request.headers.get('sec-fetch-site')
  if (site !== null && site !== 'same-origin') return done

  let path: unknown
  try {
    path = ((await request.json()) as { path?: unknown }).path
  } catch {
    return done
  }
  if (typeof path !== 'string' || !path.startsWith('/') || path.length > 500) return done

  const [pathname, search = ''] = path.split('?', 2)
  const report = pageViewRequest(
    pathname ?? '/',
    search ? `?${search}` : '',
    // The referrer of a navigation inside the app is the app itself, which is not a source.
    new Headers([...request.headers].filter(([name]) => name !== 'referer')),
    await cookies(),
  )
  if (report) await fetch(report.url, report.init).catch(() => undefined)
  return done
}
