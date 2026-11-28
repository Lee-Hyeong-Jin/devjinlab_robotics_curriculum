import { afterEach, describe, expect, it } from 'vitest'

import { webErrorReport } from './web-error-report'

const ORIGINAL = { ...process.env }

afterEach(() => {
  process.env = { ...ORIGINAL }
})

describe('webErrorReport (#35)', () => {
  it('sends the path, the error and its digest to the API', () => {
    process.env.RC_API_BASE_URL = 'http://api:8000/'
    const error = Object.assign(new TypeError('cannot read x'), { digest: '2457749570' })
    const report = webErrorReport(error, '/modules/m1/l1')
    expect(report.url).toBe('http://api:8000/api/v1/telemetry/weberror')
    expect(report.init.method).toBe('POST')
    expect(JSON.parse(String(report.init.body))).toEqual({
      path: '/modules/m1/l1',
      digest: '2457749570',
      error_type: 'TypeError',
      message: 'cannot read x',
    })
  })

  it('keeps the query string, and anything personal in it, out of the report', () => {
    const report = webErrorReport(new Error('x'), '/search?q=my+private+words#top')
    expect(JSON.parse(String(report.init.body)).path).toBe('/search')
    expect(String(report.init.body)).not.toContain('private')
    // No cookie or other header travels with it.
    expect(report.init.headers).toEqual({ 'Content-Type': 'application/json' })
  })

  it('copes with a thrown value that is not an error, and bounds what it sends', () => {
    expect(JSON.parse(String(webErrorReport('boom', undefined).init.body))).toEqual({
      path: '/',
      digest: null,
      error_type: null,
      message: null,
    })
    const long = webErrorReport(new Error('m'.repeat(5000)), `/${'p'.repeat(900)}`)
    const body = JSON.parse(String(long.init.body))
    expect(body.message.length).toBe(1000)
    expect(body.path.length).toBe(500)
  })
})
