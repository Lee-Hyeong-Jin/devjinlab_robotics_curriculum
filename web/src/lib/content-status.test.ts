import { afterEach, describe, expect, it, vi } from 'vitest'

import { contentTarget, contentVerdict, isDocumentRequest } from './content-status'

afterEach(() => {
  vi.unstubAllGlobals()
})

function api(routes: Record<string, { status: number; body?: unknown }>) {
  const calls: string[] = []
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: string | URL) => {
      const path = new URL(String(input)).pathname
      calls.push(path)
      const route = routes[path]
      if (!route) throw new Error(`unexpected request ${path}`)
      return new Response(route.body === undefined ? null : JSON.stringify(route.body), {
        status: route.status,
      })
    }),
  )
  return calls
}

describe('contentTarget', () => {
  it('recognises module, lesson, quiz and shortcut paths and nothing else', () => {
    expect(contentTarget('/modules/m1')).toEqual({ kind: 'module', moduleId: 'm1' })
    expect(contentTarget('/modules/m1/')).toEqual({ kind: 'module', moduleId: 'm1' })
    expect(contentTarget('/modules/m1/l1')).toEqual({
      kind: 'lesson',
      moduleId: 'm1',
      lessonId: 'l1',
    })
    expect(contentTarget('/modules/m1/l1/quiz')).toEqual({
      kind: 'lesson',
      moduleId: 'm1',
      lessonId: 'l1',
    })
    expect(contentTarget('/lessons/l1')).toEqual({ kind: 'shortcut', lessonId: 'l1' })
    for (const path of ['/', '/roadmap', '/modules', '/modules/m1/l1/quiz/extra', '/lessons']) {
      expect(contentTarget(path), path).toBeNull()
    }
  })
})

describe('isDocumentRequest', () => {
  it('is true for a page load and false for client navigation, prefetch and writes', () => {
    expect(
      isDocumentRequest('GET', new Headers({ accept: 'text/html,application/xhtml+xml' })),
    ).toBe(true)
    expect(isDocumentRequest('GET', new Headers())).toBe(true) // curl, some crawlers
    expect(isDocumentRequest('HEAD', new Headers({ accept: '*/*' }))).toBe(true)
    expect(isDocumentRequest('GET', new Headers({ rsc: '1', accept: '*/*' }))).toBe(false)
    expect(isDocumentRequest('GET', new Headers({ 'next-router-prefetch': '1' }))).toBe(false)
    expect(isDocumentRequest('GET', new Headers({ 'next-router-segment-prefetch': '/x' }))).toBe(
      false,
    )
    expect(isDocumentRequest('POST', new Headers({ accept: 'text/html' }))).toBe(false)
    // What the middleware actually sees for the router's requests: Next has removed the
    // `rsc` headers, and only the browser's fetch metadata tells them from a page load.
    expect(
      isDocumentRequest('GET', new Headers({ accept: '*/*', 'sec-fetch-dest': 'empty' })),
    ).toBe(false)
    expect(
      isDocumentRequest('GET', new Headers({ accept: 'text/html', 'sec-fetch-dest': 'document' })),
    ).toBe(true)
    expect(isDocumentRequest('GET', new Headers({ accept: 'application/json' }))).toBe(false)
  })
})

describe('contentVerdict', () => {
  const moduleBody = { id: 'm1', lessons: [{ id: 'l1' }, { id: 'l2' }] }

  it('finds a module and its lessons from one module request', async () => {
    const calls = api({ '/api/v1/modules/m1': { status: 200, body: moduleBody } })
    expect(await contentVerdict({ kind: 'module', moduleId: 'm1' }, null)).toEqual({ status: 'ok' })
    expect(await contentVerdict({ kind: 'lesson', moduleId: 'm1', lessonId: 'l2' }, null)).toEqual({
      status: 'ok',
    })
    expect(calls).toEqual(['/api/v1/modules/m1', '/api/v1/modules/m1'])
  })

  it('reports an unknown module and a lesson that is not in its module as missing', async () => {
    api({
      '/api/v1/modules/nope': { status: 404 },
      '/api/v1/modules/m1': { status: 200, body: moduleBody },
    })
    expect(await contentVerdict({ kind: 'module', moduleId: 'nope' }, null)).toEqual({
      status: 'missing',
    })
    expect(await contentVerdict({ kind: 'lesson', moduleId: 'm1', lessonId: 'l9' }, null)).toEqual({
      status: 'missing',
    })
  })

  it('redirects the shortcut to the canonical lesson address', async () => {
    api({
      '/api/v1/lessons/l1': { status: 200, body: { id: 'l1', module_id: 'm1' } },
      '/api/v1/lessons/l9': { status: 404 },
    })
    expect(await contentVerdict({ kind: 'shortcut', lessonId: 'l1' }, null)).toEqual({
      status: 'moved',
      location: '/modules/m1/l1',
    })
    expect(await contentVerdict({ kind: 'shortcut', lessonId: 'l9' }, null)).toEqual({
      status: 'missing',
    })
  })

  it('never guesses: an outage, a 401 or a strange body lets the page through', async () => {
    api({
      '/api/v1/modules/closed': { status: 401 },
      '/api/v1/modules/broken': { status: 500 },
      '/api/v1/modules/odd': { status: 200, body: { unexpected: true } },
      '/api/v1/lessons/closed': { status: 401 },
    })
    for (const moduleId of ['closed', 'broken', 'odd']) {
      expect(
        await contentVerdict({ kind: 'lesson', moduleId, lessonId: 'l1' }, null),
        moduleId,
      ).toEqual({ status: 'ok' })
    }
    expect(await contentVerdict({ kind: 'shortcut', lessonId: 'closed' }, null)).toEqual({
      status: 'ok',
    })
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        throw new Error('connection refused')
      }),
    )
    expect(await contentVerdict({ kind: 'module', moduleId: 'm1' }, null)).toEqual({ status: 'ok' })
  })

  it('passes the session cookie on, so a closed deployment answers for its own readers', async () => {
    const seen: Array<string | null> = []
    vi.stubGlobal(
      'fetch',
      vi.fn(async (_input: string | URL, init?: RequestInit) => {
        seen.push(new Headers(init?.headers).get('cookie'))
        return new Response(JSON.stringify(moduleBody), { status: 200 })
      }),
    )
    await contentVerdict({ kind: 'module', moduleId: 'm1' }, 'sid=abc')
    await contentVerdict({ kind: 'module', moduleId: 'm1' }, null)
    expect(seen).toEqual(['sid=abc', null])
  })
})
