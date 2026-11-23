import { describe, expect, it } from 'vitest'

import { loginUrl, safeNext, sessionExpiredUrl } from './next-path'

describe('safeNext', () => {
  it('keeps a same-origin path', () => {
    expect(safeNext('/modules/m1/l1')).toBe('/modules/m1/l1')
    expect(safeNext('/roadmap?x=1')).toBe('/roadmap?x=1')
  })

  it('refuses anything that could leave the origin', () => {
    expect(safeNext('https://evil.example')).toBe('/')
    expect(safeNext('//evil.example')).toBe('/')
    expect(safeNext('javascript:alert(1)')).toBe('/')
    expect(safeNext('modules/m1')).toBe('/')
  })

  it('refuses the spellings a browser turns into another host (QA B-04)', () => {
    // A browser treats a backslash as a slash and drops tabs and newlines before parsing.
    expect(safeNext('/\\evil.example')).toBe('/')
    expect(safeNext('/\\/evil.example')).toBe('/')
    expect(safeNext('/\t/evil.example')).toBe('/')
    expect(safeNext('/\n/evil.example')).toBe('/')
    expect(safeNext('/\r/evil.example')).toBe('/')
    expect(safeNext('/ok\\..\\evil')).toBe('/')
    expect(safeNext('/\u0000/evil.example')).toBe('/')
    expect(safeNext('/' + 'a'.repeat(3000))).toBe('/')
    // Ordinary paths with queries, fragments and non-ASCII text still pass.
    expect(safeNext('/search?q=칼만 필터')).toBe('/search?q=칼만 필터')
    expect(safeNext('/modules/m1/l1#quiz')).toBe('/modules/m1/l1#quiz')
    expect(safeNext('/login?next=/x')).toBe('/login?next=/x')
  })

  it('builds the login and session-expired addresses', () => {
    expect(loginUrl('/reports')).toBe('/login?next=%2Freports')
    expect(loginUrl('/')).toBe('/login')
    expect(loginUrl('/reports', true)).toBe('/login?next=%2Freports&expired=1')
    expect(loginUrl('//evil.example', true)).toBe('/login?expired=1')
    expect(sessionExpiredUrl('/profile')).toBe('/session/expired?next=%2Fprofile')
    expect(sessionExpiredUrl('/\\evil.example')).toBe('/session/expired?next=%2F')
  })

  it('falls back to the dashboard for an absent value', () => {
    expect(safeNext(undefined)).toBe('/')
    expect(safeNext(null)).toBe('/')
    expect(safeNext('')).toBe('/')
  })
})
