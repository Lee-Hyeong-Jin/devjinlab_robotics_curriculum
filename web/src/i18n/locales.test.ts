import { describe, expect, it } from 'vitest'

import { DEFAULT_LOCALE, isLocale, resolveLocale } from './locales'

describe('resolveLocale', () => {
  it('prefers the stored choice (AC-I18N.2)', () => {
    expect(resolveLocale('en', 'ko-KR,ko;q=0.9')).toBe('en')
  })

  it('falls back to Accept-Language', () => {
    expect(resolveLocale(undefined, 'en-GB,en;q=0.9')).toBe('en')
    expect(resolveLocale(null, 'ko-KR,ko;q=0.9,en;q=0.8')).toBe('ko')
  })

  it('falls back to ko for an unknown or absent language', () => {
    expect(resolveLocale(undefined, 'fr-FR,fr;q=0.9')).toBe('ko')
    expect(resolveLocale(undefined, undefined)).toBe(DEFAULT_LOCALE)
    expect(resolveLocale('de', null)).toBe('ko')
  })
})

describe('isLocale', () => {
  it('accepts only the declared locales', () => {
    expect(isLocale('ko')).toBe(true)
    expect(isLocale('en')).toBe(true)
    expect(isLocale('ja')).toBe(false)
    expect(isLocale(undefined)).toBe(false)
  })
})
