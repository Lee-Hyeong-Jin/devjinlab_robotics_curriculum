'use client'

import { useLocale, useTranslations } from 'next-intl'
import { useRouter } from 'next/navigation'
import { useId, useTransition } from 'react'

import { LOCALES, LOCALE_COOKIE, LOCALE_PARAM, type Locale } from '@/i18n/locales'

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
    // An address that pins its language (`?lang=ko`, the form a search result links to) wins
    // over the stored choice, so on such a page the switcher did nothing. The pin is dropped
    // and the choice just made decides. A full load, not a client navigation: the root layout
    // (`<html lang>`, the message catalogue) is not rendered again when only the query changes.
    const url = new URL(window.location.href)
    if (url.searchParams.has(LOCALE_PARAM)) {
      url.searchParams.delete(LOCALE_PARAM)
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination -- see above
      window.location.assign(`${url.pathname}${url.search}${url.hash}`)
      return
    }
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
        className="bg-subtle text-primary border-border-default min-h-11 rounded-lg border px-2 py-1 text-sm xl:min-h-0 xl:text-xs"
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
