import 'server-only'

import { getTranslations } from 'next-intl/server'

import { ApiError, ApiUnreachableError } from '../api/errors'
import { camelCase, fieldMessageKey } from './field-errors'
import type { ActionState } from './result'

/** One entry of a 422 problem's `errors` list. */
interface FieldProblem {
  loc?: Array<string | number>
  msg?: string
  type?: string
}

/**
 * Turn a thrown API error into form state.
 *
 * `fallback` is used when the API sent no problem detail. A 422 carries the list of refused
 * values; each is attached to its field, so the reader sees which input is wrong instead of
 * only "1 field is invalid" above the form (QA B-11). A `NEXT_REDIRECT` error is Next's own
 * control flow and must be re-thrown.
 *
 * @param fieldNames API field name -> form input name, for the ones that are not simply the
 *   camelCase of each other (`expires_in_days` -> `expiresInDays` needs no entry).
 */
export async function toActionState(
  error: unknown,
  fallback: string,
  fieldNames: Record<string, string> = {},
): Promise<ActionState> {
  if (isRedirect(error)) throw error
  if (error instanceof ApiUnreachableError) return { error: fallback }
  if (error instanceof ApiError) {
    const fields = await fieldMessages(error, fieldNames)
    const detail = error.problem?.detail ?? error.problem?.title
    const message = detail && detail.length > 0 ? detail : fallback
    return Object.keys(fields).length > 0 ? { error: message, fields } : { error: message }
  }
  return { error: fallback }
}

/** The stable `code` of a problem (`wrong_current_password`, …), when the API sent one. */
export function problemCode(error: unknown): string | undefined {
  if (!(error instanceof ApiError)) return undefined
  const code = (error.problem as { code?: unknown } | undefined)?.code
  return typeof code === 'string' ? code : undefined
}

async function fieldMessages(
  error: ApiError,
  fieldNames: Record<string, string>,
): Promise<Record<string, string>> {
  const errors = (error.problem as { errors?: FieldProblem[] } | undefined)?.errors
  if (error.status !== 422 || !Array.isArray(errors) || errors.length === 0) return {}
  const t = await getTranslations('form')
  const out: Record<string, string> = {}
  for (const entry of errors) {
    // `['body', 'display_name']`: the last string is the field.
    const name = [...(entry.loc ?? [])].reverse().find((part) => typeof part === 'string')
    if (typeof name !== 'string' || name === 'body' || name === 'query') continue
    const field = fieldNames[name] ?? camelCase(name)
    if (!(field in out)) out[field] = t(fieldMessageKey(entry.type))
  }
  return out
}

/** Next signals `redirect()` by throwing; never swallow it. */
export function isRedirect(error: unknown): boolean {
  return (
    typeof error === 'object' &&
    error !== null &&
    'digest' in error &&
    typeof (error as { digest?: unknown }).digest === 'string' &&
    (error as { digest: string }).digest.startsWith('NEXT_REDIRECT')
  )
}
