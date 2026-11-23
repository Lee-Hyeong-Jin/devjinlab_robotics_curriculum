import { describe, expect, it } from 'vitest'

import { redirectToPath } from './redirect-response'

describe('redirectToPath', () => {
  it('answers with a relative Location, never the address the server listens on (QA B-10)', () => {
    const response = redirectToPath('/login?next=%2Fprofile')
    expect(response.status).toBe(302)
    expect(response.headers.get('location')).toBe('/login?next=%2Fprofile')
    expect(response.headers.get('cache-control')).toBe('no-store')
  })

  it('keeps the header ASCII and refuses to leave the site', () => {
    expect(redirectToPath('/search?q=칼만').headers.get('location')).toBe(
      '/search?q=%EC%B9%BC%EB%A7%8C',
    )
    expect(redirectToPath('//evil.example/x').headers.get('location')).toBe('/')
    expect(redirectToPath('/\\evil.example').headers.get('location')).toBe('/')
    expect(redirectToPath('https://evil.example').headers.get('location')).toBe('/')
  })
})
