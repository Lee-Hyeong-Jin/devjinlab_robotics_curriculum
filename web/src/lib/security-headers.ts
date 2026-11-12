/**
 * Response security headers for the web app.
 *
 * The API sets its own (`api/middleware.py`); these are the browser-facing ones for the
 * pages, which the API's headers never reach because nginx serves `web` directly.
 *
 * The CSP is nonce-based: `middleware.ts` mints a nonce per request, puts it in the policy
 * and forwards it as a request header, and Next adds it to its own scripts while the root
 * layout puts it on the one inline script we write ourselves (the pre-paint theme switch).
 * `'strict-dynamic'` then covers the chunks those scripts load, so no hash list has to be
 * maintained; `'self'` stays for browsers that do not implement it.
 */
export const STATIC_SECURITY_HEADERS: ReadonlyArray<{ key: string; value: string }> = [
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  // `frame-ancestors 'none'` in the CSP is what modern browsers obey; this covers the rest.
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=(), payment=(), usb=()',
  },
  { key: 'Cross-Origin-Opener-Policy', value: 'same-origin' },
  { key: 'X-DNS-Prefetch-Control', value: 'off' },
]

/** One year, with subdomains. Only ever sent over HTTPS — a browser ignores it otherwise. */
export const HSTS = 'max-age=31536000; includeSubDomains'

export interface CspOptions {
  nonce: string
  /** Development needs `eval` for React refresh and inline styles for the dev overlay. */
  dev?: boolean
  /** Add `upgrade-insecure-requests` when the request already arrived over HTTPS. */
  https?: boolean
}

export function contentSecurityPolicy({ nonce, dev = false, https = false }: CspOptions): string {
  const script = [
    "'self'",
    `'nonce-${nonce}'`,
    "'strict-dynamic'",
    ...(dev ? ["'unsafe-eval'"] : []),
  ]
  const directives: Array<[string, string]> = [
    ['default-src', "'self'"],
    ['base-uri', "'self'"],
    ['object-src', "'none'"],
    ['frame-ancestors', "'none'"],
    ['form-action', "'self'"],
    ['script-src', script.join(' ')],
    // One inline `style` attribute carries the progress-bar width, and Next injects its own
    // style tags. Style injection cannot execute code, so this stays rather than growing a
    // hash list that breaks on every Next upgrade.
    ['style-src', "'self' 'unsafe-inline'"],
    // Lesson content may link an illustration on another host; the sanitizer already limits
    // `src` to http(s) (`markdown/sanitize.ts`).
    ['img-src', "'self' data: blob: https:"],
    ['font-src', "'self' data:"],
    // The browser never calls the API directly: pages are rendered server-side and talk to
    // it from there (frontend.md §1).
    ['connect-src', "'self'"],
    ['manifest-src', "'self'"],
    ['media-src', "'self'"],
    ['worker-src', "'self' blob:"],
  ]
  const policy = directives.map(([name, value]) => `${name} ${value}`)
  if (https) policy.push('upgrade-insecure-requests')
  return policy.join('; ')
}
