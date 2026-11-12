import type { MetadataRoute } from 'next'

import { publicContentEnabled, siteUrl } from '@/lib/api/config'

/**
 * Built per request, not at build time: `RC_PUBLIC_CONTENT` and `RC_PUBLIC_URL` are runtime
 * settings, and the content comes from the API. Prerendered, this file would freeze whatever
 * the build environment happened to have — which is how it first shipped as `Disallow: /`
 * against a deployment that does publish.
 */
export const dynamic = 'force-dynamic'

/**
 * `robots.txt`.
 *
 * With nothing published (`RC_PUBLIC_CONTENT` off, ADR 0016) the whole site is disallowed:
 * a crawler would only reach the login screen anyway, and a half-open site is worse than a
 * closed one. With content published, the curriculum is allowed and everything that belongs
 * to a person or an operator is named explicitly — `Disallow` is not a security control
 * (those paths need a session), it keeps crawlers out of pages that would be useless to them.
 */
export default function robots(): MetadataRoute.Robots {
  const base = siteUrl()
  if (!publicContentEnabled()) {
    return { rules: [{ userAgent: '*', disallow: '/' }] }
  }
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: [
          '/login',
          '/signup',
          '/profile',
          '/admin/',
          '/review',
          '/reports',
          '/search',
          '/password/',
          '/verify-email',
          '/api/',
          // The quiz hands out answers and explanations; it is per-reader, not a page.
          '/modules/*/quiz',
        ],
      },
    ],
    sitemap: `${base}/sitemap.xml`,
    host: base,
  }
}
