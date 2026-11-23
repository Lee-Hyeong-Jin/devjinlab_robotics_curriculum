/**
 * ISO 8601 weeks (`2026-W47`), the unit of the weekly report.
 *
 * Week 1 is the week with the year's first Thursday; weeks run Monday to Sunday. The API takes
 * and returns weeks in this spelling; these helpers move between weeks for the "previous week"
 * and "next week" links (QA B-29).
 */

const WEEK = /^(\d{4})-W(\d{2})$/
const DAY_MS = 86_400_000

/** True for a well-formed week that exists (`2026-W53` exists, `2025-W53` does not). */
export function isIsoWeek(value: string | null | undefined): value is string {
  if (!value) return false
  const monday = mondayOf(value)
  return monday !== null && isoWeekOf(monday) === value
}

/** The Monday a week starts on, as a UTC date, or `null` when the spelling is wrong. */
function mondayOf(week: string): Date | null {
  const match = WEEK.exec(week)
  if (!match) return null
  const year = Number(match[1])
  const number = Number(match[2])
  if (number < 1 || number > 53) return null
  // 4 January is always in week 1.
  const fourth = new Date(Date.UTC(year, 0, 4))
  const weekday = fourth.getUTCDay() || 7
  return new Date(fourth.getTime() + ((number - 1) * 7 - (weekday - 1)) * DAY_MS)
}

/** The ISO week a UTC calendar date falls in. */
export function isoWeekOf(date: Date): string {
  const day = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()))
  // Thursday of this week decides the year.
  day.setUTCDate(day.getUTCDate() + 4 - (day.getUTCDay() || 7))
  const yearStart = Date.UTC(day.getUTCFullYear(), 0, 1)
  const number = Math.ceil(((day.getTime() - yearStart) / DAY_MS + 1) / 7)
  return `${day.getUTCFullYear()}-W${String(number).padStart(2, '0')}`
}

/** The week `delta` weeks after (or before) a week, or `null` when the week is not valid. */
export function shiftIsoWeek(week: string, delta: number): string | null {
  const monday = mondayOf(week)
  if (!monday) return null
  return isoWeekOf(new Date(monday.getTime() + delta * 7 * DAY_MS))
}

/** The current ISO week in a time zone (weeks turn over at that zone's Monday midnight). */
export function currentIsoWeek(timeZone: string, now: Date = new Date()): string {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(now)
  const get = (type: string) => Number(parts.find((part) => part.type === type)?.value ?? 0)
  return isoWeekOf(new Date(Date.UTC(get('year'), get('month') - 1, get('day'))))
}
