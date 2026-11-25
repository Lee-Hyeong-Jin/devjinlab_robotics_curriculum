/** UI locales (AC-I18N.1). */
export const LOCALES = ['ko', 'en'] as const

export type Locale = (typeof LOCALES)[number]

/**
 * The language of a request that states none: English (ADR 0018).
 *
 * This is what every first-time visitor and every crawler gets, whatever language their
 * browser asks for, and so the language of every canonical URL. The curriculum is written in
 * Korean and Korean stays one choice away — the switcher, the profile, or `?lang=ko`.
 */
export const DEFAULT_LOCALE: Locale = 'en'

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
 * Resolve the UI locale: `?lang=`, then the reader's stored choice, then English
 * (frontend.md §6, ADR 0018).
 *
 * The browser's `Accept-Language` is deliberately not consulted. The site opens in English
 * for everybody; Korean is something a reader chooses (the switcher, their profile, or an
 * address that pins it), and once chosen it is remembered. One address therefore always shows
 * one language to anybody without a stored choice — a visitor and a crawler see the same page.
 */
export function resolveLocale(cookieValue?: string | null, queryValue?: string | null): Locale {
  if (isLocale(queryValue)) return queryValue
  if (isLocale(cookieValue)) return cookieValue
  return DEFAULT_LOCALE
}
