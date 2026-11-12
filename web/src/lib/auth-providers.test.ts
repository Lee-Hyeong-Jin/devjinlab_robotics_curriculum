import { describe, expect, it } from 'vitest'

import type { AuthProvider, Identity } from './api/types'
import { providerStartHref, unlinkedProviders } from './auth-providers'

const provider = (id: string): AuthProvider => ({
  id,
  name: id,
  type: 'oidc',
  start_url: `https://api.test/api/v1/auth/oidc/${id}/start`,
})

describe('providerStartHref', () => {
  it('attaches the destination the provider should come back to', () => {
    expect(providerStartHref('https://api.test/start', '/profile')).toBe(
      'https://api.test/start?return_to=%2Fprofile',
    )
  })

  it('refuses an absolute destination, so the button cannot become an open redirect', () => {
    expect(providerStartHref('https://api.test/start', 'https://evil.example')).toBe(
      'https://api.test/start?return_to=%2F',
    )
    expect(providerStartHref('https://api.test/start', '//evil.example')).toBe(
      'https://api.test/start?return_to=%2F',
    )
  })

  it('keeps the start URL query the API already put there', () => {
    expect(providerStartHref('https://api.test/start?a=1', '/x')).toBe(
      'https://api.test/start?a=1&return_to=%2Fx',
    )
  })

  it('still produces a usable link when the start URL is relative', () => {
    expect(providerStartHref('/api/v1/auth/oidc/univ/start', '/roadmap')).toBe(
      '/api/v1/auth/oidc/univ/start?return_to=%2Froadmap',
    )
  })
})

describe('unlinkedProviders', () => {
  const identity = (p: string): Identity => ({
    id: 1,
    provider: p,
    email: null,
    linked_at: '2026-11-12T00:00:00Z',
  })

  it('drops the providers the account already uses', () => {
    const left = unlinkedProviders([provider('univ'), provider('github')], [identity('univ')])
    expect(left.map((p) => p.id)).toEqual(['github'])
  })

  it('offers everything when nothing is linked yet', () => {
    expect(unlinkedProviders([provider('univ')], [])).toHaveLength(1)
  })
})
