import { webErrorReport } from '@/lib/web-error-report'

/**
 * Report pages this server failed to render to the API, so an operator sees them (#35).
 *
 * The monitoring screen lists failed requests from the API's point of view. A page that fails
 * here, in the web server, never reaches the API as a failure: during one incident every page
 * answered 500 while that list stayed empty. Next.js calls `onRequestError` for each such
 * failure, and it is posted to the API, which stores it beside its own failures.
 *
 * A failure to report is swallowed — the page has already failed once, and the error is in
 * this server's log either way.
 */
export async function onRequestError(error: unknown, request: { path?: string }): Promise<void> {
  try {
    const report = webErrorReport(error, request.path)
    await fetch(report.url, report.init)
  } catch {
    // Not reported.
  }
}
