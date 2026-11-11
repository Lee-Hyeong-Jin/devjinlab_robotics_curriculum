import type { NextConfig } from 'next'
import createNextIntlPlugin from 'next-intl/plugin'

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts')

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // `NEXT_OUTPUT=standalone npm run build` produces the self-contained bundle
  // the `web` container runs (`node .next/standalone/server.js` plus copies of
  // `.next/static` and `public/`). It is opt-in because `next start` refuses to
  // serve a standalone build, which local runs and the E2E suite rely on.
  ...(process.env.NEXT_OUTPUT === 'standalone' ? { output: 'standalone' as const } : {}),
  typescript: {
    // `npm run typecheck` is the gate; `next build` must not pass on type errors either.
    ignoreBuildErrors: false,
  },
}

export default withNextIntl(nextConfig)
