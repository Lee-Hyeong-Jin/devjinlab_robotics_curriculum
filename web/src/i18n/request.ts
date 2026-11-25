import { cookies, headers } from 'next/headers'
import { getRequestConfig } from 'next-intl/server'

import { CURRENT_PATH_HEADER } from '@/lib/api/client'
import { serviceTimeZone } from '@/lib/timezone'

import { LOCALE_COOKIE, LOCALE_PARAM, resolveLocale } from './locales'

/**
 * Locale skeleton: no locale segment in the URL (every route is served in the
 * viewer's locale), but `?lang=` pins one so each language has an address of its own.
 * English is the default (`DEFAULT_LOCALE`); Korean is the other catalogue (AC-I18N.1).
 */
function localeFromPath(pathWithQuery: string | null): string | null {
  const query = pathWithQuery?.split('?')[1]
  return query ? new URLSearchParams(query).get(LOCALE_PARAM) : null
}

export default getRequestConfig(async () => {
  const [jar, headerList] = await Promise.all([cookies(), headers()])
  // `?lang=` is read from the path header the middleware publishes: this config has no access
  // to searchParams, and the language has to be pinnable by URL for hreflang to mean anything.
  const locale = resolveLocale(
    jar.get(LOCALE_COOKIE)?.value,
    localeFromPath(headerList.get(CURRENT_PATH_HEADER)),
  )
  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
    // The same zone as every date the app formats itself (`lib/timezone.ts`).
    timeZone: serviceTimeZone(),
  }
})
