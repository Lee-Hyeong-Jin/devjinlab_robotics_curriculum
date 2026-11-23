import { cookies } from 'next/headers'

import { apiBaseUrl, apiTimeoutMs } from '@/lib/api/config'
import { browserIdentity } from '@/lib/api/forward'
import { loginUrl, safeNext } from '@/lib/next-path'
import { redirectToPath } from '@/lib/redirect-response'

const SESSION_COOKIE = 'sid'

/**
 * Where a reader whose session has ended lands on the way to the login screen (QA B-01).
 *
 * A session can end without the browser knowing: signed out from another device, signed out by
 * an operator, the account disabled, a password reset. The cookie is still sent, the API
 * refuses it, and a page render cannot delete a cookie — only a route handler can. So the
 * pages redirect here, the stale cookie is dropped, and the reader arrives at the login screen
 * with a notice instead of meeting the same refusal on every page.
 *
 * The cookie is dropped only when the API really refuses it. A link to this address must not
 * be a way to sign somebody out of a working session.
 */
export async function GET(request: Request): Promise<Response> {
  const next = safeNext(new URL(request.url).searchParams.get('next'))
  const jar = await cookies()
  const session = jar.get(SESSION_COOKIE)
  if (!session) return redirectToPath(loginUrl(next))

  let status = 0
  try {
    const response = await fetch(`${apiBaseUrl()}/api/v1/me`, {
      headers: {
        Accept: 'application/json',
        Cookie: `${SESSION_COOKIE}=${session.value}`,
        ...(await browserIdentity()),
      },
      cache: 'no-store',
      signal: AbortSignal.timeout(apiTimeoutMs()),
    })
    status = response.status
  } catch {
    // The API is unreachable: nothing is known about the session, so nothing is dropped.
    return redirectToPath(loginUrl(next))
  }

  if (status === 401) {
    jar.delete(SESSION_COOKIE)
    return redirectToPath(loginUrl(next, true))
  }
  // The session works after all (a stale link, a second tab that signed in again).
  return redirectToPath(status === 200 ? next : loginUrl(next))
}
