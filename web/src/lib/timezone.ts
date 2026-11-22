/**
 * The service's time zone (frontend.md §6, RUNBOOK §8 "시간대").
 *
 * Every date and time the app shows is in this zone, whatever zone the server process or the
 * container happens to run in: a time on screen should not change because a deployment forgot
 * to set `TZ`. It is Korea Standard Time unless `RC_TIMEZONE` says otherwise, the same variable
 * the API reads, so the two cut days at the same midnight.
 */

export const DEFAULT_TIME_ZONE = 'Asia/Seoul'

/** The configured IANA zone name, or the default when it is unset or not a real zone. */
export function serviceTimeZone(): string {
  const raw = process.env.RC_TIMEZONE?.trim()
  if (!raw) return DEFAULT_TIME_ZONE
  try {
    new Intl.DateTimeFormat('en-US', { timeZone: raw })
    return raw
  } catch {
    return DEFAULT_TIME_ZONE
  }
}

/** Minutes the zone is ahead of UTC at `instant` (540 for Korea). */
export function offsetMinutes(instant: Date, timeZone: string): number {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone,
    hourCycle: 'h23',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).formatToParts(instant)
  const get = (type: string) => Number(parts.find((part) => part.type === type)?.value ?? 0)
  const asUtc = Date.UTC(
    get('year'),
    get('month') - 1,
    get('day'),
    get('hour'),
    get('minute'),
    get('second'),
  )
  return Math.round((asUtc - instant.getTime()) / 60_000)
}

/**
 * The instant a calendar day begins in a zone: `('2026-11-22', 'Asia/Seoul')` is
 * `2026-11-21T15:00:00.000Z`.
 *
 * The offset is looked up at the day itself rather than assumed, so a zone with daylight
 * saving gets the right midnight on either side of a change.
 */
export function zonedDayStart(day: string, timeZone: string): Date | undefined {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) return undefined
  const guess = new Date(`${day}T00:00:00Z`)
  if (Number.isNaN(guess.getTime())) return undefined
  const first = new Date(guess.getTime() - offsetMinutes(guess, timeZone) * 60_000)
  // Around a daylight-saving change the offset at the guess and at the answer can differ.
  return new Date(guess.getTime() - offsetMinutes(first, timeZone) * 60_000)
}

/** A short name for the zone to show beside a time ("KST", "UTC", "GMT-5"). */
export function timeZoneLabel(timeZone: string, locale = 'en'): string {
  if (timeZone === 'Asia/Seoul') return 'KST'
  const part = new Intl.DateTimeFormat(locale, { timeZone, timeZoneName: 'short' })
    .formatToParts(new Date())
    .find((item) => item.type === 'timeZoneName')
  return part?.value ?? timeZone
}
