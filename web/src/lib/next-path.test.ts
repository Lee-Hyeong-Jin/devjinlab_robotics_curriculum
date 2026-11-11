import { describe, expect, it } from 'vitest'

import { safeNext } from './next-path'

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

  it('falls back to the dashboard for an absent value', () => {
    expect(safeNext(undefined)).toBe('/')
    expect(safeNext(null)).toBe('/')
    expect(safeNext('')).toBe('/')
  })
})
