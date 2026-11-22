/** Query-string helpers for the admin lists, whose filters live in the URL. */

/** The first value of a search parameter, trimmed; `undefined` when absent or empty. */
export function param(value: string | string[] | undefined): string | undefined {
  const first = Array.isArray(value) ? value[0] : value
  const trimmed = first?.trim()
  return trimmed ? trimmed : undefined
}

/** `value` if it is one of `allowed`, otherwise `undefined` (an unknown filter is no filter). */
export function oneOf<T extends string>(
  value: string | undefined,
  allowed: readonly T[],
): T | undefined {
  return allowed.includes(value as T) ? (value as T) : undefined
}

/** A positive integer id from the URL, or `undefined`. */
export function positiveInt(value: string | undefined): number | undefined {
  if (!value || !/^[0-9]{1,9}$/.test(value)) return undefined
  const parsed = Number(value)
  return parsed > 0 ? parsed : undefined
}

const DAY = /^\d{4}-\d{2}-\d{2}$/

/**
 * A `YYYY-MM-DD` day from a date input as the UTC instant the API filters on.
 *
 * `endOfDay` returns the start of the *next* day, because the API's `until` is exclusive and a
 * reader who picks "to 22 Nov" expects that day to be included.
 */
export function dayToInstant(value: string | undefined, endOfDay = false): string | undefined {
  if (!value || !DAY.test(value)) return undefined
  const date = new Date(`${value}T00:00:00Z`)
  if (Number.isNaN(date.getTime())) return undefined
  if (endOfDay) date.setUTCDate(date.getUTCDate() + 1)
  return date.toISOString()
}

/** `path?a=1&b=2` from the defined entries of `query`, in the order given. */
export function withQuery(path: string, query: Record<string, string | undefined>): string {
  const search = new URLSearchParams()
  for (const [name, value] of Object.entries(query)) {
    if (value !== undefined && value !== '') search.set(name, value)
  }
  const text = search.toString()
  return text ? `${path}?${text}` : path
}
