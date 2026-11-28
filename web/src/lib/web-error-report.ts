import { apiBaseUrl } from './api/config'

/**
 * The report of one page this server failed to render (#35, see `instrumentation.ts`).
 *
 * Only what identifies the failure is sent: the page's path without its query string, the
 * error's type and message, and its digest — the reference the error screen shows the reader
 * and the key to the stack trace in this server's log. No cookie, no address, no query.
 */
export interface WebErrorReport {
  url: string
  init: RequestInit
}

const MESSAGE_LIMIT = 1000

function text(value: unknown, limit: number): string | null {
  return typeof value === 'string' && value !== '' ? value.slice(0, limit) : null
}

export function webErrorReport(error: unknown, path: string | undefined): WebErrorReport {
  const failure = (typeof error === 'object' && error !== null ? error : {}) as {
    name?: unknown
    message?: unknown
    digest?: unknown
  }
  const pathname = (path ?? '/').split('?')[0]?.split('#')[0] || '/'
  return {
    url: `${apiBaseUrl()}/api/v1/telemetry/weberror`,
    init: {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        path: pathname.slice(0, 500),
        digest: text(failure.digest, 64),
        error_type: text(failure.name, 100),
        message: text(failure.message, MESSAGE_LIMIT),
      }),
      cache: 'no-store',
      // The page has already failed; reporting it must not hold anything else up.
      signal: AbortSignal.timeout(1500),
    },
  }
}
