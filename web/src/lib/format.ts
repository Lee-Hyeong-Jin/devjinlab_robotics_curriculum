/**
 * Locale-aware formatters. Dates and times are shown in the service's time zone
 * (`lib/timezone.ts`: KST by default) unless the caller passes another.
 */

import { serviceTimeZone } from './timezone'

export const DEFAULT_LOCALE = 'ko'

/** `95` → `"95%"`. Takes a 0–1 ratio and rounds to whole percent. */
export function formatPercent(ratio: number | null | undefined, locale = DEFAULT_LOCALE): string {
  const value = Number.isFinite(ratio) ? Math.min(Math.max(ratio as number, 0), 1) : 0
  return new Intl.NumberFormat(locale, { style: 'percent', maximumFractionDigits: 0 }).format(value)
}

/** A 0–1 ratio as a whole number 0–100, for `aria-valuenow` and bar widths. */
export function percentValue(ratio: number | null | undefined): number {
  if (!Number.isFinite(ratio)) return 0
  return Math.round(Math.min(Math.max(ratio as number, 0), 1) * 100)
}

/** `135` → `"2시간 15분"` (ko) / `"2h 15m"` (en). Minutes, never negative. */
export function formatMinutes(minutes: number | null | undefined, locale = DEFAULT_LOCALE): string {
  const total = Math.max(0, Math.round(minutes ?? 0))
  const hours = Math.floor(total / 60)
  const rest = total % 60
  const ko = locale.startsWith('ko')
  if (hours === 0) return ko ? `${rest}분` : `${rest}m`
  if (rest === 0) return ko ? `${hours}시간` : `${hours}h`
  return ko ? `${hours}시간 ${rest}분` : `${hours}h ${rest}m`
}

/** Seconds from the API rendered as study time. */
export function formatSeconds(seconds: number | null | undefined, locale = DEFAULT_LOCALE): string {
  return formatMinutes(Math.round((seconds ?? 0) / 60), locale)
}

/**
 * An ISO timestamp as a short date-time in the service's time zone (KST unless `RC_TIMEZONE`
 * says otherwise), or `""` when absent/invalid. Never the process's own zone: a container
 * left on UTC must not move every time on screen by nine hours.
 */
export function formatDateTime(
  iso: string | null | undefined,
  locale = DEFAULT_LOCALE,
  timeZone: string = serviceTimeZone(),
): string {
  if (!iso) return ''
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return new Intl.DateTimeFormat(locale, {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone,
  }).format(date)
}

/** An ISO timestamp as a short date in the service's time zone, or `""` when absent/invalid. */
export function formatDate(
  iso: string | null | undefined,
  locale = DEFAULT_LOCALE,
  timeZone: string = serviceTimeZone(),
): string {
  if (!iso) return ''
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return new Intl.DateTimeFormat(locale, { dateStyle: 'medium', timeZone }).format(date)
}

/** A hostname for display next to an external resource link. */
export function hostnameOf(url: string | null | undefined): string {
  if (!url) return ''
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return ''
  }
}

/** A byte count in binary units: `1536` → `"1.5 KB"`, `16428158976` → `"15.3 GB"`. */
export function formatBytes(bytes: number | null | undefined, locale = DEFAULT_LOCALE): string {
  if (bytes === null || bytes === undefined || !Number.isFinite(bytes) || bytes < 0) return '—'
  const units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
  let value = bytes
  let unit = 0
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024
    unit += 1
  }
  const digits = unit === 0 || value >= 100 ? 0 : 1
  return `${new Intl.NumberFormat(locale, { maximumFractionDigits: digits }).format(value)} ${units[unit]}`
}

/** Milliseconds as a latency: `0.42` → `"<1 ms"`, `37.5` → `"38 ms"`, `2400` → `"2.4 s"`. */
export function formatMs(ms: number | null | undefined, locale = DEFAULT_LOCALE): string {
  if (ms === null || ms === undefined || !Number.isFinite(ms)) return '—'
  if (ms < 1) return '<1 ms'
  if (ms < 1000)
    return `${new Intl.NumberFormat(locale, { maximumFractionDigits: 0 }).format(ms)} ms`
  return `${new Intl.NumberFormat(locale, { maximumFractionDigits: 1 }).format(ms / 1000)} s`
}

/** Seconds as an uptime: `93784` → `"1일 2시간"` (ko) / `"1d 2h"` (en); under an hour in minutes. */
export function formatDuration(
  seconds: number | null | undefined,
  locale = DEFAULT_LOCALE,
): string {
  if (seconds === null || seconds === undefined || !Number.isFinite(seconds)) return '—'
  const total = Math.max(0, Math.floor(seconds))
  const days = Math.floor(total / 86400)
  const hours = Math.floor((total % 86400) / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const ko = locale.startsWith('ko')
  if (days > 0) return ko ? `${days}일 ${hours}시간` : `${days}d ${hours}h`
  if (hours > 0) return ko ? `${hours}시간 ${minutes}분` : `${hours}h ${minutes}m`
  return ko ? `${minutes}분` : `${minutes}m`
}

/** A 0–1 ratio with one decimal where it matters: `0.9991` → `"99.9%"`, `0.42` → `"42%"`. */
export function formatRatio(
  ratio: number | null | undefined,
  locale = DEFAULT_LOCALE,
  fractionDigits = 1,
): string {
  if (ratio === null || ratio === undefined || !Number.isFinite(ratio)) return '—'
  return new Intl.NumberFormat(locale, {
    style: 'percent',
    maximumFractionDigits: fractionDigits,
  }).format(ratio)
}
