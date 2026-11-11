/**
 * Locale-aware formatters. Dates and times use the user's timezone when the
 * profile supplies one (frontend.md §6); until P2-2 the caller passes it in.
 */

export const DEFAULT_LOCALE = 'ko'

/** `95` → `"95%"`. Takes a 0–1 ratio and rounds to whole percent. */
export function formatPercent(ratio: number | undefined, locale = DEFAULT_LOCALE): string {
  const value = Number.isFinite(ratio) ? Math.min(Math.max(ratio as number, 0), 1) : 0
  return new Intl.NumberFormat(locale, { style: 'percent', maximumFractionDigits: 0 }).format(value)
}

/** A 0–1 ratio as a whole number 0–100, for `aria-valuenow` and bar widths. */
export function percentValue(ratio: number | undefined): number {
  if (!Number.isFinite(ratio)) return 0
  return Math.round(Math.min(Math.max(ratio as number, 0), 1) * 100)
}

/** `135` → `"2시간 15분"` (ko) / `"2h 15m"` (en). Minutes, never negative. */
export function formatMinutes(minutes: number | undefined, locale = DEFAULT_LOCALE): string {
  const total = Math.max(0, Math.round(minutes ?? 0))
  const hours = Math.floor(total / 60)
  const rest = total % 60
  const ko = locale.startsWith('ko')
  if (hours === 0) return ko ? `${rest}분` : `${rest}m`
  if (rest === 0) return ko ? `${hours}시간` : `${hours}h`
  return ko ? `${hours}시간 ${rest}분` : `${hours}h ${rest}m`
}

/** Seconds from the API rendered as study time. */
export function formatSeconds(seconds: number | undefined, locale = DEFAULT_LOCALE): string {
  return formatMinutes(Math.round((seconds ?? 0) / 60), locale)
}

/** An ISO timestamp as a short local date-time, or `""` when absent/invalid. */
export function formatDateTime(
  iso: string | undefined,
  locale = DEFAULT_LOCALE,
  timeZone?: string,
): string {
  if (!iso) return ''
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return new Intl.DateTimeFormat(locale, {
    dateStyle: 'medium',
    timeStyle: 'short',
    ...(timeZone ? { timeZone } : {}),
  }).format(date)
}

/** An ISO timestamp as a short local date, or `""` when absent/invalid. */
export function formatDate(
  iso: string | undefined,
  locale = DEFAULT_LOCALE,
  timeZone?: string,
): string {
  if (!iso) return ''
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return new Intl.DateTimeFormat(locale, {
    dateStyle: 'medium',
    ...(timeZone ? { timeZone } : {}),
  }).format(date)
}

/** A hostname for display next to an external resource link. */
export function hostnameOf(url: string | undefined): string {
  if (!url) return ''
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return ''
  }
}
