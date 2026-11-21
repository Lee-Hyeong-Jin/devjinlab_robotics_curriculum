import type { NextConfig } from 'next'
import createNextIntlPlugin from 'next-intl/plugin'

import { STATIC_SECURITY_HEADERS } from './src/lib/security-headers'

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts')

/**
 * Clients that must find `<title>` and the meta tags inside `<head>`.
 *
 * Next streams a dynamic page's metadata into the body unless the user agent matches this
 * pattern, and for a match it holds the response until the metadata is in `<head>`. Its built-in
 * list leaves out Googlebot (which runs scripts and would pick the tags up from the body) and
 * the link-preview clients Korean readers use. Measured on this app, a cold request for a lesson
 * as Googlebot got no title, description, canonical or robots tag in `<head>` at all.
 *
 * So the pattern is generic instead of a list to keep up to date: anything that calls itself a
 * bot, crawler, spider, scraper or preview, plus the well-known agents whose names say none of
 * those. A false positive costs that client a slightly later first byte and nothing else.
 */
const HTML_LIMITED_BOTS =
  /bot|crawl|spider|scrap|preview|slurp|yeti|daum\/|daumoa|facebookexternalhit|facebookcatalog|whatsapp|embedly|quora|tumblr|vkshare|ia_archiver|lighthouse|google-|-google|googleweblight|mediapartners|bingpreview|skypeuri/i

const nextConfig: NextConfig = {
  reactStrictMode: true,
  htmlLimitedBots: HTML_LIMITED_BOTS,
  poweredByHeader: false,
  // `NEXT_OUTPUT=standalone npm run build` produces the self-contained bundle
  // the `web` container runs (`node .next/standalone/server.js` plus copies of
  // `.next/static` and `public/`). It is opt-in because `next start` refuses to
  // serve a standalone build, which local runs and the E2E suite rely on.
  ...(process.env.NEXT_OUTPUT === 'standalone' ? { output: 'standalone' as const } : {}),
  // The CSP and HSTS are per-request and live in `src/middleware.ts`; these are constant and
  // set here so they also cover `_next/static`, which the middleware matcher skips.
  async headers() {
    return [{ source: '/:path*', headers: [...STATIC_SECURITY_HEADERS] }]
  },
  typescript: {
    // `npm run typecheck` is the gate; `next build` must not pass on type errors either.
    ignoreBuildErrors: false,
  },
}

export default withNextIntl(nextConfig)
