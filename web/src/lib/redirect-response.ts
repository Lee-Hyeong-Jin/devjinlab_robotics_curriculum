/**
 * A redirect from a route handler to a path on this site.
 *
 * The `Location` is the path itself, not an absolute URL. Building one from `request.url`
 * uses the address the server process listens on — `http://0.0.0.0:3000` inside the container
 * — and sends the browser somewhere it cannot reach (QA B-10). A relative `Location` is
 * resolved by the browser against the address it actually used, behind any proxy.
 */
import { safeNext } from './next-path'

export function redirectToPath(path: string, status: 302 | 303 | 307 = 302): Response {
  // Parsed and re-serialised so the header is ASCII and anything off-site collapses to `/`.
  const url = new URL(safeNext(path), 'http://same-origin.invalid')
  return new Response(null, {
    status,
    headers: { Location: `${url.pathname}${url.search}${url.hash}`, 'Cache-Control': 'no-store' },
  })
}
