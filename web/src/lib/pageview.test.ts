import { describe, expect, it } from 'vitest'

import { countsAsPage, pageViewRequest } from './pageview'

function jar(values: Record<string, string>) {
  return { get: (name: string) => (name in values ? { value: values[name] ?? '' } : undefined) }
}

describe('countsAsPage', () => {
  it('leaves out assets, API routes and the admin console', () => {
    for (const path of ['/', '/roadmap', '/modules/m1/l1', '/guide', '/login']) {
      expect(countsAsPage(path), path).toBe(true)
    }
    for (const path of [
      '/api/me/export',
      '/admin',
      '/admin/users/3',
      '/_next/data/x',
      '/icon.svg',
      '/robots.txt',
      '/sitemap.xml',
      '/manifest.webmanifest',
      '/og-image.png',
    ]) {
      expect(countsAsPage(path), path).toBe(false)
    }
  })
})

describe('pageViewRequest', () => {
  it('reports the path, language, referrer and whether there is a session', () => {
    const report = pageViewRequest(
      '/modules/m1/l1',
      '?lang=en',
      new Headers({
        'x-forwarded-for': '198.51.100.7',
        'user-agent': 'Mozilla/5.0 (test)',
        referer: 'https://www.google.com/search?q=robotics',
        'accept-language': 'ko',
      }),
      jar({ sid: 'abc' }),
    )
    expect(report?.url).toMatch(/\/api\/v1\/telemetry\/pageview$/)
    expect(JSON.parse(String(report?.init.body))).toEqual({
      path: '/modules/m1/l1',
      locale: 'en',
      referrer: 'https://www.google.com/search?q=robotics',
      signed_in: true,
    })
    const headers = new Headers(report?.init.headers)
    // The browser's identity travels as headers for the API to hash; it is not in the body.
    expect(headers.get('x-forwarded-for')).toBe('198.51.100.7')
    expect(headers.get('user-agent')).toBe('Mozilla/5.0 (test)')
    expect(String(report?.init.body)).not.toContain('198.51.100.7')
    // The session cookie itself is never forwarded.
    expect(headers.get('cookie')).toBeNull()
  })

  it('falls back to the cookie and the browser language, and to no referrer', () => {
    const cookie = pageViewRequest('/', '', new Headers(), jar({ NEXT_LOCALE: 'en' }))
    expect(JSON.parse(String(cookie?.init.body))).toMatchObject({
      locale: 'en',
      referrer: null,
      signed_in: false,
    })
    const browser = pageViewRequest('/', '', new Headers({ 'accept-language': 'en-US' }), jar({}))
    expect(JSON.parse(String(browser?.init.body)).locale).toBe('en')
  })

  it('does not report this site as the place a visit came from', () => {
    const own = pageViewRequest(
      '/roadmap',
      '',
      new Headers({ host: 'learn.example.org', referer: 'https://learn.example.org/' }),
      jar({}),
    )
    expect(JSON.parse(String(own?.init.body)).referrer).toBeNull()
    const proxied = pageViewRequest(
      '/roadmap',
      '',
      new Headers({
        host: 'web:3000',
        'x-forwarded-host': 'learn.example.org',
        referer: 'https://learn.example.org/guide',
      }),
      jar({}),
    )
    expect(JSON.parse(String(proxied?.init.body)).referrer).toBeNull()
    const garbage = pageViewRequest('/', '', new Headers({ referer: 'not a url' }), jar({}))
    expect(JSON.parse(String(garbage?.init.body)).referrer).toBeNull()
  })

  it('returns nothing for a path that is not a page', () => {
    expect(pageViewRequest('/admin/users', '', new Headers(), jar({}))).toBeNull()
    expect(pageViewRequest('/icon.svg', '', new Headers(), jar({}))).toBeNull()
  })
})
