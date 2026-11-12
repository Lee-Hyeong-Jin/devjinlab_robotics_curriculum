'use client'

import { useLocale, useTranslations } from 'next-intl'
import { useRouter } from 'next/navigation'
import { useId, useTransition } from 'react'

import { LOCALES, LOCALE_COOKIE, type Locale } from '@/i18n/locales'

const LABEL: Record<Locale, string> = { ko: '한국어', en: 'English' }

/**
 * UI language switch. Writes the `NEXT_LOCALE` cookie and re-renders; once the
 * P2-2 profile API lands this also sends `PATCH /me { locale }` so the choice
 * survives a new device (AC-I18N.2).
 */
export function LocaleSwitcher() {
  const current = useLocale()
  const t = useTranslations('nav')
  const router = useRouter()
  const id = useId()
  const [pending, startTransition] = useTransition()

  function choose(next: string) {
    // One year, site-wide; no personal data, so no consent gate.
    document.cookie = `${LOCALE_COOKIE}=${next}; path=/; max-age=31536000; samesite=lax`
    startTransition(() => router.refresh())
  }

  return (
    <div className="flex items-center gap-2" data-locale-switcher="">
      <label htmlFor={id} className="sr-only">
        {t('language')}
      </label>
      <select
        id={id}
        value={current}
        disabled={pending}
        onChange={(event) => choose(event.target.value)}
        className="bg-subtle text-primary border-border-default rounded-lg border px-2 py-1 text-xs"
      >
        {LOCALES.map((locale) => (
          <option key={locale} value={locale}>
            {LABEL[locale]}
          </option>
        ))}
      </select>
    </div>
  )
}
