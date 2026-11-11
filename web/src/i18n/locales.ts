/** UI locales. `ko` is the default; `en` is the placeholder catalogue (AC-I18N.1). */
export const LOCALES = ['ko', 'en'] as const

export type Locale = (typeof LOCALES)[number]

export const DEFAULT_LOCALE: Locale = 'ko'

/** Cookie the locale switcher writes; `PATCH /me` persists it once P2-2 lands. */
export const LOCALE_COOKIE = 'NEXT_LOCALE'

export function isLocale(value: string | undefined | null): value is Locale {
  return !!value && (LOCALES as readonly string[]).includes(value)
}

/**
 * Resolve the UI locale: the user's stored choice, then `Accept-Language`,
 * then `ko` (frontend.md §6).
 */
export function resolveLocale(cookieValue?: string | null, acceptLanguage?: string | null): Locale {
  if (isLocale(cookieValue)) return cookieValue
  for (const part of (acceptLanguage ?? '').split(',')) {
    const tag = part.split(';')[0]?.trim().toLowerCase() ?? ''
    const base = tag.split('-')[0]
    if (isLocale(base)) return base
  }
  return DEFAULT_LOCALE
}
