/**
 * External-login helpers that are not Server Components, so they can be unit tested.
 *
 * The browser starts an OIDC/GitHub login by navigating to the API, not by a fetch:
 * the flow ends with the provider redirecting back to the API's callback, which sets
 * the session cookie. `GET /auth/providers` hands us the absolute start URL for each
 * configured provider (built from `RC_API_BASE_URL`, see ADR 0010).
 */
import type { AuthProvider, Identity } from './api/types'
import { safeNext } from './next-path'

/**
 * The provider's start URL with `return_to` attached.
 *
 * `return_to` goes through {@link safeNext} first: the API only accepts a relative
 * path, and a rejected one would silently land the reader on `/` instead.
 */
export function providerStartHref(startUrl: string, returnTo: string): string {
  const target = safeNext(returnTo)
  try {
    const url = new URL(startUrl)
    url.searchParams.set('return_to', target)
    return url.toString()
  } catch {
    // Not an absolute URL — a misconfigured RC_API_BASE_URL. Keep it usable anyway.
    const separator = startUrl.includes('?') ? '&' : '?'
    return `${startUrl}${separator}return_to=${encodeURIComponent(target)}`
  }
}

/** Providers the account has not linked yet — the only ones worth offering to connect. */
export function unlinkedProviders(
  providers: readonly AuthProvider[],
  identities: readonly Identity[],
): AuthProvider[] {
  const linked = new Set(identities.map((identity) => identity.provider))
  return providers.filter((provider) => !linked.has(provider.id))
}
