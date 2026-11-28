import { screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiUnreachableError, API_UNREACHABLE_DIGEST } from '@/lib/api/errors'
import { renderWithIntl } from '@/test/render'

import ErrorScreen from './error'

afterEach(() => vi.restoreAllMocks())

describe('the error screen (#33)', () => {
  it('shows the digest as a reference the reader can quote', () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    // What a production server render hands the boundary: a generic message and a digest.
    const error = Object.assign(new Error('Minified React error #441'), { digest: '2457749570' })
    renderWithIntl(<ErrorScreen error={error} reset={() => undefined} />)
    expect(screen.getByText(/2457749570/)).toBeInTheDocument()
    expect(screen.queryByText(/#441/)).toBeNull()
  })

  it('recognises an unreachable API by its digest, which survives a production build', () => {
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    expect(new ApiUnreachableError('http://api/x', null).digest).toBe(API_UNREACHABLE_DIGEST)
    const error = Object.assign(new Error('Minified React error #441'), {
      digest: API_UNREACHABLE_DIGEST,
    })
    renderWithIntl(<ErrorScreen error={error} reset={() => undefined} />)
    expect(
      screen.getByText(/API 에 연결|API 서버|cannot reach|could not reach/i),
    ).toBeInTheDocument()
    // No reference number for a failure the message already explains.
    expect(screen.queryByText(API_UNREACHABLE_DIGEST)).toBeNull()
  })
})
