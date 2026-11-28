import type { Problem } from './types'

/**
 * A non-2xx API response. `problem` carries the RFC 9457 body when the server
 * sent `application/problem+json`.
 */
export class ApiError extends Error {
  readonly status: number
  readonly problem: Problem | undefined
  readonly requestId: string | undefined

  constructor(status: number, message: string, problem?: Problem, requestId?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.problem = problem
    this.requestId = requestId
  }

  /** The user-facing detail, falling back to the title and then the message. */
  get detail(): string {
    return this.problem?.detail ?? this.problem?.title ?? this.message
  }
}

/** What the error boundary sees of an `ApiUnreachableError` thrown during a server render. */
export const API_UNREACHABLE_DIGEST = 'API_UNREACHABLE'

/** The API could not be reached at all (connection refused, DNS, timeout). */
export class ApiUnreachableError extends Error {
  /**
   * In a production build React replaces the message of an error thrown while rendering on the
   * server with a generic one, so the browser never learns what failed. A `digest` set by the
   * thrown error is the one thing passed through, and it is how the error screen can tell
   * "the API is down" from everything else.
   */
  readonly digest = API_UNREACHABLE_DIGEST

  constructor(url: string, cause: unknown) {
    super(`API unreachable: ${url}`, { cause })
    this.name = 'ApiUnreachableError'
  }
}

/** True when the API answered 404 — used to fall back to an empty state. */
export function isNotFound(error: unknown): boolean {
  return error instanceof ApiError && error.status === 404
}

/** True when the API refused for lack of a session or a valid token. */
export function isUnauthorized(error: unknown): boolean {
  return error instanceof ApiError && error.status === 401
}

/** True when the endpoint is not implemented yet (404/405/501 on a contract path). */
export function isUnimplemented(error: unknown): boolean {
  return error instanceof ApiError && [404, 405, 501].includes(error.status)
}

/** True when the API refused for lack of permission. */
export function isForbidden(error: unknown): boolean {
  return error instanceof ApiError && error.status === 403
}
