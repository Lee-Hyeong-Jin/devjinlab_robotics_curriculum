/** UI locales. `ko` is the default; `en` is the placeholder catalogue (AC-I18N.1). */
export const LOCALES = ['ko', 'en'] as const

export type Locale = (typeof LOCALES)[number]

export const DEFAULT_LOCALE: Locale = 'ko'

/** Cookie the locale switcher writes; `PATCH /me` persists it once P2-2 lands. */
export const LOCALE_COOKIE = 'NEXT_LOCALE'

/**
 * Query parameter that pins a page's language: `?lang=en`.
 *
 * The URL carries no locale segment, so without this there is no distinct address for the
 * English version of a page — and `hreflang` needs one URL per language, as does a sitemap.
 * It overrides the cookie for that one request, which also makes the alternate links a
 * crawler follows render in the language they promise.
 */
export const LOCALE_PARAM = 'lang'

export function isLocale(value: string | undefined | null): value is Locale {
  return !!value && (LOCALES as readonly string[]).includes(value)
}

/**
 * Resolve the UI locale: `?lang=`, then the user's stored choice, then `Accept-Language`,
 * then `ko` (frontend.md §6).
 */
export function resolveLocale(
  cookieValue?: string | null,
  acceptLanguage?: string | null,
  queryValue?: string | null,
): Locale {
  if (isLocale(queryValue)) return queryValue
  if (isLocale(cookieValue)) return cookieValue
  for (const part of (acceptLanguage ?? '').split(',')) {
    const tag = part.split(';')[0]?.trim().toLowerCase() ?? ''
    const base = tag.split('-')[0]
    if (isLocale(base)) return base
  }
  return DEFAULT_LOCALE
}
