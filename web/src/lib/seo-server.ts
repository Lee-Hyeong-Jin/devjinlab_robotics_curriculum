import type { Metadata } from 'next'
import { getLocale, getTranslations } from 'next-intl/server'

import { isLocale, DEFAULT_LOCALE } from '@/i18n/locales'

import { pageSeo, type PageSeoOptions } from './seo'

/**
 * `pageSeo` with the request's language filled in: `og:locale` and `og:site_name` follow the
 * language the page is actually rendered in (`?lang=en` serves English under the same path).
 *
 * Kept apart from `seo.ts` so that file stays free of request state and unit-testable.
 */
export async function localizedPageSeo(
  options: Omit<PageSeoOptions, 'locale' | 'siteName'>,
): Promise<Metadata> {
  const [locale, t] = await Promise.all([getLocale(), getTranslations('app')])
  return pageSeo({
    ...options,
    locale: isLocale(locale) ? locale : DEFAULT_LOCALE,
    siteName: t('title'),
  })
}
