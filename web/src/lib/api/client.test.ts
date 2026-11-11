import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const redirect = vi.fn((url: string) => {
  throw new Error(`NEXT_REDIRECT:${url}`)
})
const cookieJar: Array<{ name: string; value: string }> = []
const requestHeaders = new Map<string, string>()

vi.mock('next/navigation', () => ({ redirect }))
vi.mock('next/headers', () => ({
  cookies: async () => ({
    getAll: () => cookieJar,
    get: (name: string) => cookieJar.find((cookie) => cookie.name === name),
  }),
  headers: async () => ({ get: (name: string) => requestHeaders.get(name) ?? null }),
}))

import type { ApiError as ApiErrorClass } from './errors'

const { CSRF_HEADER, CURRENT_PATH_HEADER, apiGet, apiGetOrNull, apiPost } = await import('./client')
const { ApiError, ApiUnreachableError } = await import('./errors')

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'content-type': 'application/json', 'x-request-id': 'req-1' },
    ...init,
  })
}

let fetchMock: ReturnType<typeof vi.fn>

beforeEach(() => {
  cookieJar.length = 0
  requestHeaders.clear()
  redirect.mockClear()
  process.env.RC_API_BASE_URL = 'http://api.test'
  fetchMock = vi.fn()
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  vi.unstubAllGlobals()
  delete process.env.RC_API_BASE_URL
})

describe('apiGet', () => {
  it('calls the configured base URL and returns the parsed body', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ lessons: [] }))
    await expect(apiGet('/api/v1/progress/status')).resolves.toEqual({ lessons: [] })
    expect(fetchMock.mock.calls[0]?.[0]).toBe('http://api.test/api/v1/progress/status')
  })

  it('forwards the request cookies so the API sees the session', async () => {
    cookieJar.push({ name: 'sid', value: 'abc' }, { name: 'csrf', value: 'tok' })
    fetchMock.mockResolvedValue(jsonResponse({}))
    await apiGet('/api/v1/progress/status')
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit
    expect((init.headers as Headers).get('Cookie')).toBe('sid=abc; csrf=tok')
  })

  it('appends query parameters and drops empty ones', async () => {
    fetchMock.mockResolvedValue(jsonResponse([]))
    await apiGet('/api/v1/resources', { query: { module_id: 'm1', lesson_id: undefined } })
    expect(fetchMock.mock.calls[0]?.[0]).toBe('http://api.test/api/v1/resources?module_id=m1')
  })

  it('does not cache progress data and revalidates content', async () => {
    fetchMock.mockResolvedValue(jsonResponse({}))
    await apiGet('/api/v1/progress/status')
    expect((fetchMock.mock.calls[0]?.[1] as RequestInit).cache).toBe('no-store')

    fetchMock.mockResolvedValue(jsonResponse([]))
    await apiGet('/api/v1/resources', { cache: 'content', tags: ['content'] })
    const init = fetchMock.mock.calls[1]?.[1] as RequestInit & { next?: { revalidate?: number } }
    expect(init.next?.revalidate).toBeGreaterThan(0)
    expect(init.cache).toBeUndefined()
  })

  it('throws an ApiError carrying the RFC 9457 problem body', async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ title: 'Not Found', detail: '레슨이 없습니다', status: 404 }), {
        status: 404,
        headers: { 'content-type': 'application/problem+json', 'x-request-id': 'req-9' },
      }),
    )
    const error = await apiGet('/api/v1/progress/status').catch((caught: unknown) => caught)
    expect(error).toBeInstanceOf(ApiError)
    expect((error as ApiErrorClass).status).toBe(404)
    expect((error as ApiErrorClass).detail).toBe('레슨이 없습니다')
    expect((error as ApiErrorClass).requestId).toBe('req-9')
  })

  it('redirects to /login with the current path on 401', async () => {
    requestHeaders.set(CURRENT_PATH_HEADER, '/modules/m1/lesson-1')
    fetchMock.mockResolvedValue(new Response(null, { status: 401 }))
    await expect(apiGet('/api/v1/progress/status')).rejects.toThrow('NEXT_REDIRECT')
    expect(redirect).toHaveBeenCalledWith('/login?next=%2Fmodules%2Fm1%2Flesson-1')
  })

  it('can opt out of the 401 redirect', async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 401 }))
    await expect(
      apiGet('/api/v1/progress/status', { redirectOnUnauthorized: false }),
    ).rejects.toBeInstanceOf(ApiError)
    expect(redirect).not.toHaveBeenCalled()
  })

  it('wraps a connection failure as ApiUnreachableError', async () => {
    fetchMock.mockRejectedValue(new Error('ECONNREFUSED'))
    await expect(apiGet('/api/v1/progress/status')).rejects.toBeInstanceOf(ApiUnreachableError)
  })
})

describe('apiGetOrNull', () => {
  it('returns null for an endpoint that is not implemented yet', async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 404 }))
    await expect(apiGetOrNull('/api/v1/progress/next')).resolves.toBeNull()

    fetchMock.mockResolvedValue(new Response(null, { status: 501 }))
    await expect(apiGetOrNull('/api/v1/progress/next')).resolves.toBeNull()
  })

  it('returns null when the API cannot be reached', async () => {
    fetchMock.mockRejectedValue(new Error('ECONNREFUSED'))
    await expect(apiGetOrNull('/api/v1/progress/status')).resolves.toBeNull()
  })

  it('still throws for a server error', async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 500 }))
    await expect(apiGetOrNull('/api/v1/progress/status')).rejects.toBeInstanceOf(ApiError)
  })
})

describe('apiPost', () => {
  it('double-submits the CSRF cookie and sends JSON', async () => {
    cookieJar.push({ name: 'csrf', value: 'tok-123' })
    fetchMock.mockResolvedValue(jsonResponse({ ok: true }))
    await apiPost('/api/v1/progress/start', { lesson_id: 'l1' })
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit
    const headers = init.headers as Headers
    expect(init.method).toBe('POST')
    expect(headers.get(CSRF_HEADER)).toBe('tok-123')
    expect(headers.get('Content-Type')).toBe('application/json')
    expect(init.body).toBe('{"lesson_id":"l1"}')
  })

  it('omits the CSRF header when there is no cookie yet', async () => {
    fetchMock.mockResolvedValue(jsonResponse({}))
    await apiPost('/api/v1/progress/start', {})
    expect((fetchMock.mock.calls[0]?.[1] as RequestInit).headers).toBeDefined()
    expect(
      ((fetchMock.mock.calls[0]?.[1] as RequestInit).headers as Headers).get(CSRF_HEADER),
    ).toBeNull()
  })

  it('returns undefined for a 204', async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }))
    await expect(apiPost('/api/v1/auth/logout')).resolves.toBeUndefined()
  })
})
