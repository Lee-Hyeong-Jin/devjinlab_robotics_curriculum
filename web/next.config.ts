import type { NextConfig } from 'next'
import createNextIntlPlugin from 'next-intl/plugin'

import { STATIC_SECURITY_HEADERS } from './src/lib/security-headers'

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts')

const nextConfig: NextConfig = {
  reactStrictMode: true,
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
