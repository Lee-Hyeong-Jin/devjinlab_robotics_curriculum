import { describe, expect, it } from 'vitest'

import {
  formatDate,
  formatDateTime,
  formatMinutes,
  formatPercent,
  formatSeconds,
  hostnameOf,
  percentValue,
} from './format'

describe('formatMinutes', () => {
  it('writes hours and minutes in Korean', () => {
    expect(formatMinutes(135, 'ko')).toBe('2시간 15분')
    expect(formatMinutes(120, 'ko')).toBe('2시간')
    expect(formatMinutes(45, 'ko')).toBe('45분')
  })

  it('writes hours and minutes in English', () => {
    expect(formatMinutes(135, 'en')).toBe('2h 15m')
    expect(formatMinutes(45, 'en')).toBe('45m')
  })

  it('treats missing and negative values as zero', () => {
    expect(formatMinutes(undefined, 'ko')).toBe('0분')
    expect(formatMinutes(-10, 'ko')).toBe('0분')
  })
})

describe('formatSeconds', () => {
  it('rounds seconds to minutes', () => {
    expect(formatSeconds(3660, 'en')).toBe('1h 1m')
    expect(formatSeconds(undefined, 'en')).toBe('0m')
  })
})

describe('formatPercent / percentValue', () => {
  it('renders a 0-1 ratio as whole percent', () => {
    expect(formatPercent(0.756, 'en')).toBe('76%')
    expect(percentValue(0.756)).toBe(76)
  })

  it('clamps out-of-range and non-numeric input', () => {
    expect(percentValue(1.4)).toBe(100)
    expect(percentValue(-1)).toBe(0)
    expect(percentValue(undefined)).toBe(0)
    expect(percentValue(Number.NaN)).toBe(0)
  })
})

describe('formatDateTime / formatDate', () => {
  it('formats in the given timezone', () => {
    const out = formatDateTime('2026-11-11T00:30:00Z', 'ko', 'Asia/Seoul')
    expect(out).toContain('2026')
    expect(out).not.toBe('')
  })

  it('returns an empty string for missing or invalid input', () => {
    expect(formatDateTime(undefined, 'ko')).toBe('')
    expect(formatDateTime('not-a-date', 'ko')).toBe('')
    expect(formatDate(undefined, 'ko')).toBe('')
  })
})

describe('hostnameOf', () => {
  it('strips the scheme and www', () => {
    expect(hostnameOf('https://www.example.com/a/b')).toBe('example.com')
  })

  it('returns an empty string for a non-URL', () => {
    expect(hostnameOf('book, chapter 3')).toBe('')
    expect(hostnameOf(undefined)).toBe('')
  })
})
