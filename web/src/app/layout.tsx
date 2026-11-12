import type { Metadata, Viewport } from 'next'
import { headers } from 'next/headers'
import { NextIntlClientProvider } from 'next-intl'
import { getLocale, getMessages, getTranslations } from 'next-intl/server'

import { SkipLink } from '@/components/SkipLink'
import { TopNav } from '@/components/TopNav'
import { siteUrl } from '@/lib/api/config'
import { THEME_INIT_SCRIPT } from '@/lib/theme'
import { NONCE_HEADER } from '@/middleware'

import './globals.css'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('app')
  return {
    // Canonical and OpenGraph URLs resolve against this; without it Next emits relative
    // ones, which a crawler cannot use.
    metadataBase: new URL(siteUrl()),
    title: { default: t('title'), template: `%s · ${t('shortTitle')}` },
    description: t('description'),
    // noindex is the default for the whole app; a published page asks out of it through
    // `pageSeo` (ADR 0016). A page indexed by accident cannot be un-indexed by a later fix.
    robots: { index: false, follow: false },
  }
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  colorScheme: 'light dark',
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const [locale, messages, t, requestHeaders] = await Promise.all([
    getLocale(),
    getMessages(),
    getTranslations('app'),
    headers(),
  ])
  // Minted per request by `middleware.ts` and named in the CSP; without it this script is
  // blocked and dark readers get a flash of light.
  const nonce = requestHeaders.get(NONCE_HEADER) ?? undefined

  return (
    <html lang={locale} suppressHydrationWarning>
      <head>
        {/* Apply the stored theme before first paint so dark readers see no flash. */}
        <script nonce={nonce} dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body className="min-h-dvh">
        <NextIntlClientProvider locale={locale} messages={messages}>
          <SkipLink label={t('skipToContent')} />
          <TopNav />
          <main id="main" className="mx-auto max-w-[var(--content-max)] px-4 py-8 sm:px-6">
            {children}
          </main>
        </NextIntlClientProvider>
      </body>
    </html>
  )
}
