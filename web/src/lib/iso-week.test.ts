import { describe, expect, it } from 'vitest'

import { currentIsoWeek, isIsoWeek, isoWeekOf, shiftIsoWeek } from './iso-week'

describe('ISO weeks', () => {
  it('names the week of a date', () => {
    expect(isoWeekOf(new Date(Date.UTC(2026, 10, 23)))).toBe('2026-W48') // a Monday
    expect(isoWeekOf(new Date(Date.UTC(2026, 10, 22)))).toBe('2026-W47') // the Sunday before
    // Around New Year the week's year is not always the date's year.
    expect(isoWeekOf(new Date(Date.UTC(2027, 0, 1)))).toBe('2026-W53')
    expect(isoWeekOf(new Date(Date.UTC(2024, 11, 30)))).toBe('2025-W01')
  })

  it('moves between weeks, across a year end', () => {
    expect(shiftIsoWeek('2026-W48', -1)).toBe('2026-W47')
    expect(shiftIsoWeek('2026-W48', 1)).toBe('2026-W49')
    expect(shiftIsoWeek('2026-W53', 1)).toBe('2027-W01')
    expect(shiftIsoWeek('2027-W01', -1)).toBe('2026-W53')
    expect(shiftIsoWeek('2025-W01', -1)).toBe('2024-W52')
    expect(shiftIsoWeek('nonsense', 1)).toBeNull()
  })

  it('accepts only weeks that exist', () => {
    expect(isIsoWeek('2026-W47')).toBe(true)
    expect(isIsoWeek('2026-W53')).toBe(true)
    expect(isIsoWeek('2025-W53')).toBe(false)
    expect(isIsoWeek('2026-W00')).toBe(false)
    expect(isIsoWeek('2026-W7')).toBe(false)
    expect(isIsoWeek("2026-W47' OR 1=1")).toBe(false)
    expect(isIsoWeek(undefined)).toBe(false)
  })

  it('reads the current week in a time zone', () => {
    // Sunday 20:00 UTC is already Monday in Korea.
    const instant = new Date('2026-11-22T20:00:00Z')
    expect(currentIsoWeek('Asia/Seoul', instant)).toBe('2026-W48')
    expect(currentIsoWeek('UTC', instant)).toBe('2026-W47')
  })
})
