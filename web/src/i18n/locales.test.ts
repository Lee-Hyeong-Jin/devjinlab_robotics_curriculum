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

  it('falls back to English for an unknown or absent language (ADR 0018)', () => {
    expect(DEFAULT_LOCALE).toBe('en')
    expect(resolveLocale(undefined, 'fr-FR,fr;q=0.9')).toBe('en')
    expect(resolveLocale(undefined, undefined)).toBe('en')
    expect(resolveLocale('de', null)).toBe('en')
    // A crawler sends neither a cookie nor a language: it reads the English page.
    expect(resolveLocale(null, null, null)).toBe('en')
  })

  it('lets the address pin a language over everything else', () => {
    expect(resolveLocale('en', 'en-US', 'ko')).toBe('ko')
    expect(resolveLocale('ko', 'ko-KR', 'en')).toBe('en')
    expect(resolveLocale('ko', 'ko-KR', 'fr')).toBe('ko')
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
