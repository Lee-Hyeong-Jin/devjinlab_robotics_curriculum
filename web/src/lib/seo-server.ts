import type { Metadata } from 'next'
import { headers } from 'next/headers'
import { getLocale, getTranslations } from 'next-intl/server'

import { DEFAULT_LOCALE, isLocale, LOCALE_PARAM, type Locale } from '@/i18n/locales'

import { CURRENT_PATH_HEADER } from './api/client'
import { pageSeo, type PageSeoOptions } from './seo'

/** The language `?lang=` pins on this request's URL, if it is a real one. */
async function pinnedLocale(): Promise<Locale | undefined> {
  try {
    const path = (await headers()).get(CURRENT_PATH_HEADER)
    const query = path?.split('?')[1]
    const value = query ? new URLSearchParams(query).get(LOCALE_PARAM) : null
    return isLocale(value) ? value : undefined
  } catch {
    return undefined
  }
}

/**
 * `pageSeo` with the request's language filled in.
 *
 * `og:locale` and `og:site_name` follow the language the page is rendered in, and a URL that
 * pins its language (`?lang=en`) is its own canonical, so each language version can be indexed
 * (see `PageSeoOptions.pinnedLocale`).
 *
 * Kept apart from `seo.ts` so that file stays free of request state and unit-testable.
 */
export async function localizedPageSeo(
  options: Omit<PageSeoOptions, 'locale' | 'siteName' | 'pinnedLocale'>,
): Promise<Metadata> {
  const [locale, t, pinned] = await Promise.all([
    getLocale(),
    getTranslations('app'),
    pinnedLocale(),
  ])
  return pageSeo({
    ...options,
    locale: isLocale(locale) ? locale : DEFAULT_LOCALE,
    siteName: t('title'),
    pinnedLocale: pinned,
  })
}
