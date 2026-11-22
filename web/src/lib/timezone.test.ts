import { afterEach, describe, expect, it } from 'vitest'

import { dayToInstant } from './admin-query'
import { formatDate, formatDateTime } from './format'
import {
  DEFAULT_TIME_ZONE,
  offsetMinutes,
  serviceTimeZone,
  timeZoneLabel,
  zonedDayStart,
} from './timezone'

const ORIGINAL = { ...process.env }

afterEach(() => {
  process.env = { ...ORIGINAL }
})

// 16:00 UTC on the 11th is 01:00 on the 12th in Korea: the two zones disagree about the day.
const LATE = '2026-11-11T16:00:00+00:00'

describe('serviceTimeZone', () => {
  it('is Korea Standard Time unless RC_TIMEZONE names another real zone', () => {
    delete process.env.RC_TIMEZONE
    expect(DEFAULT_TIME_ZONE).toBe('Asia/Seoul')
    expect(serviceTimeZone()).toBe('Asia/Seoul')
    process.env.RC_TIMEZONE = ' UTC '
    expect(serviceTimeZone()).toBe('UTC')
    process.env.RC_TIMEZONE = 'America/New_York'
    expect(serviceTimeZone()).toBe('America/New_York')
    process.env.RC_TIMEZONE = 'Not/AZone'
    expect(serviceTimeZone()).toBe('Asia/Seoul')
  })
})

describe('formatting', () => {
  it('shows times in KST whatever zone the process runs in', () => {
    delete process.env.RC_TIMEZONE
    // The same instant, read in Korea: the 12th, one in the morning.
    expect(formatDateTime(LATE, 'en')).toBe('Nov 12, 2026, 1:00 AM')
    expect(formatDate(LATE, 'en')).toBe('Nov 12, 2026')
    expect(formatDateTime(LATE, 'ko')).toContain('2026. 11. 12.')
    expect(formatDateTime(LATE, 'ko')).toContain('오전 1:00')
    // An instant written with a Korean offset is the same instant.
    expect(formatDateTime('2026-11-12T01:00:00+09:00', 'en')).toBe('Nov 12, 2026, 1:00 AM')
  })

  it('follows RC_TIMEZONE, and an explicit zone wins over it', () => {
    process.env.RC_TIMEZONE = 'UTC'
    expect(formatDateTime(LATE, 'en')).toBe('Nov 11, 2026, 4:00 PM')
    expect(formatDate(LATE, 'en')).toBe('Nov 11, 2026')
    expect(formatDate(LATE, 'en', 'Asia/Seoul')).toBe('Nov 12, 2026')
  })
})

describe('day boundaries', () => {
  it('knows the offset of a zone at an instant', () => {
    expect(offsetMinutes(new Date(LATE), 'Asia/Seoul')).toBe(540)
    expect(offsetMinutes(new Date(LATE), 'UTC')).toBe(0)
    // A zone with daylight saving: winter and summer differ.
    expect(offsetMinutes(new Date('2026-01-15T12:00:00Z'), 'America/New_York')).toBe(-300)
    expect(offsetMinutes(new Date('2026-07-15T12:00:00Z'), 'America/New_York')).toBe(-240)
  })

  it('starts a day at local midnight', () => {
    expect(zonedDayStart('2026-11-22', 'Asia/Seoul')?.toISOString()).toBe(
      '2026-11-21T15:00:00.000Z',
    )
    expect(zonedDayStart('2026-11-22', 'UTC')?.toISOString()).toBe('2026-11-22T00:00:00.000Z')
    // The day the clocks go forward in New York still starts at its own midnight.
    expect(zonedDayStart('2026-03-08', 'America/New_York')?.toISOString()).toBe(
      '2026-03-08T05:00:00.000Z',
    )
    expect(zonedDayStart('2026-03-09', 'America/New_York')?.toISOString()).toBe(
      '2026-03-09T04:00:00.000Z',
    )
    expect(zonedDayStart('22 Nov', 'Asia/Seoul')).toBeUndefined()
  })

  it('turns an audit date filter into the Korean day, end inclusive', () => {
    delete process.env.RC_TIMEZONE
    expect(dayToInstant('2026-11-22')).toBe('2026-11-21T15:00:00.000Z')
    // "To the 22nd" runs until the 23rd begins in Korea.
    expect(dayToInstant('2026-11-22', true)).toBe('2026-11-22T15:00:00.000Z')
    expect(dayToInstant('2026-12-31', true)).toBe('2026-12-31T15:00:00.000Z')
    expect(dayToInstant('nonsense')).toBeUndefined()
    expect(dayToInstant(undefined)).toBeUndefined()
    process.env.RC_TIMEZONE = 'UTC'
    expect(dayToInstant('2026-11-22')).toBe('2026-11-22T00:00:00.000Z')
  })
})

describe('timeZoneLabel', () => {
  it('names the zone beside a time', () => {
    expect(timeZoneLabel('Asia/Seoul')).toBe('KST')
    expect(timeZoneLabel('UTC')).toBe('UTC')
  })
})
