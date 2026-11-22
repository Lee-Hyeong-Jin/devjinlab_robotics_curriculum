import { headers } from 'next/headers'

/**
 * Who the browser is, to pass on to the API.
 *
 * The browser never calls the API; this server does, on its behalf. Left alone, the API sees
 * every request as coming from this server with the user agent `node`, so the audit log and
 * the "signed-in devices" list name the web tier instead of the person, and the API's
 * per-address sign-in throttle counts all visitors as one.
 *
 * `X-Forwarded-For` is passed through as received. The API believes it only when the
 * connection comes from a proxy it trusts (`RC_API_TRUSTED_PROXIES`), and reads it right to
 * left, so a value a client invented cannot displace the address the edge proxy wrote. That
 * holds as long as this app is deployed behind a reverse proxy that sets the header, which
 * RUNBOOK §8 requires for a public deployment.
 */
export async function browserIdentity(): Promise<Record<string, string>> {
  const out: Record<string, string> = {}
  try {
    const incoming = await headers()
    const forwardedFor = incoming.get('x-forwarded-for')
    if (forwardedFor) out['X-Forwarded-For'] = forwardedFor
    const userAgent = incoming.get('user-agent')
    if (userAgent) out['User-Agent'] = userAgent
  } catch {
    // Outside a request (a build step, a test): there is no browser to describe.
  }
  return out
}
