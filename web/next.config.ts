import type { NextConfig } from 'next'
import createNextIntlPlugin from 'next-intl/plugin'

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts')

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  typescript: {
    // `npm run typecheck` is the gate; `next build` must not pass on type errors either.
    ignoreBuildErrors: false,
  },
  eslint: {
    // `npm run lint` is the gate; no need for `next build` to lint a second time.
    ignoreDuringBuilds: true,
  },
}

export default withNextIntl(nextConfig)
