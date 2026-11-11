import { cookies, headers } from 'next/headers'
import { getRequestConfig } from 'next-intl/server'

import { LOCALE_COOKIE, resolveLocale } from './locales'

/**
 * Locale skeleton: no locale segment in the URL (every route is served in the
 * viewer's locale). `ko` is the default; `en` exists so the catalogue test has
 * two sides to compare (AC-I18N.1).
 */
export default getRequestConfig(async () => {
  const [jar, headerList] = await Promise.all([cookies(), headers()])
  const locale = resolveLocale(jar.get(LOCALE_COOKIE)?.value, headerList.get('accept-language'))
  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
    timeZone: 'Asia/Seoul',
  }
})
