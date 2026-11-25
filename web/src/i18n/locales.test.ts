import { describe, expect, it } from 'vitest'

import { DEFAULT_LOCALE, isLocale, resolveLocale } from './locales'

describe('resolveLocale', () => {
  it('opens in English when the reader has chosen nothing (ADR 0018)', () => {
    expect(DEFAULT_LOCALE).toBe('en')
    expect(resolveLocale(undefined, undefined)).toBe('en')
    expect(resolveLocale(null, null)).toBe('en')
    // Not a language the site speaks: ignored, wherever it comes from.
    expect(resolveLocale('de', null)).toBe('en')
    expect(resolveLocale(null, 'fr')).toBe('en')
  })

  it('does not look at the browser language at all', () => {
    // The function takes a stored choice and an address, nothing else: a browser set to
    // Korean and a crawler that sends no language get the same English page.
    expect(resolveLocale.length).toBe(2)
  })

  it('keeps a stored choice (AC-I18N.2)', () => {
    expect(resolveLocale('ko')).toBe('ko')
    expect(resolveLocale('en')).toBe('en')
  })

  it('lets the address pin a language over the stored choice', () => {
    expect(resolveLocale('en', 'ko')).toBe('ko')
    expect(resolveLocale('ko', 'en')).toBe('en')
    expect(resolveLocale('ko', 'fr')).toBe('ko')
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
