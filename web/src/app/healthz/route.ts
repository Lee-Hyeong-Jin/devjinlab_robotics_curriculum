/**
 * Liveness of the web server itself, for the container health check and a load balancer.
 *
 * The health check used to request `/`, every ten seconds. That renders a whole page, calls
 * the API, and was counted as a page view: about 8,600 "visits" a day from the container
 * alone, which drowned the real numbers (QA B-09). This answers without touching the API or
 * the page-view counter. Whether the API is reachable is the API's own `/readyz`.
 */
export const dynamic = 'force-dynamic'

export function GET(): Response {
  return new Response('ok\n', {
    status: 200,
    headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' },
  })
}
