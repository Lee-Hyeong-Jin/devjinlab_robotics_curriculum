import 'server-only'

import { ApiError, ApiUnreachableError } from '../api/errors'
import type { ActionState } from './result'

/**
 * Turn a thrown API error into form state.
 *
 * `fallback` is used when the API sent no problem detail. A `NEXT_REDIRECT`
 * error is Next's own control flow and must be re-thrown.
 */
export function toActionState(error: unknown, fallback: string): ActionState {
  if (isRedirect(error)) throw error
  if (error instanceof ApiUnreachableError) return { error: fallback }
  if (error instanceof ApiError) {
    const detail = error.problem?.detail ?? error.problem?.title
    return { error: detail && detail.length > 0 ? detail : fallback }
  }
  return { error: fallback }
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
