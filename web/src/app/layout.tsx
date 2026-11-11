import type { Metadata, Viewport } from 'next'
import { NextIntlClientProvider } from 'next-intl'
import { getLocale, getMessages, getTranslations } from 'next-intl/server'

import { SkipLink } from '@/components/SkipLink'
import { TopNav } from '@/components/TopNav'
import { THEME_INIT_SCRIPT } from '@/lib/theme'

import './globals.css'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('app')
  return {
    title: { default: t('title'), template: `%s · ${t('shortTitle')}` },
    robots: { index: false },
  }
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  colorScheme: 'light dark',
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const [locale, messages, t] = await Promise.all([
    getLocale(),
    getMessages(),
    getTranslations('app'),
  ])

  return (
    <html lang={locale} suppressHydrationWarning>
      <head>
        {/* Apply the stored theme before first paint so dark readers see no flash. */}
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
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
