import { describe, expect, it } from 'vitest'

import { contentSecurityPolicy, HSTS, STATIC_SECURITY_HEADERS } from './security-headers'

function directives(policy: string): Map<string, string> {
  return new Map(
    policy.split('; ').map((part) => {
      const space = part.indexOf(' ')
      return space === -1 ? [part, ''] : [part.slice(0, space), part.slice(space + 1)]
    }),
  )
}

describe('contentSecurityPolicy', () => {
  const policy = contentSecurityPolicy({ nonce: 'abc123' })
  const d = directives(policy)

  it('carries the request nonce and strict-dynamic instead of a hash list', () => {
    expect(d.get('script-src')).toContain("'nonce-abc123'")
    expect(d.get('script-src')).toContain("'strict-dynamic'")
    expect(d.get('script-src')).not.toContain("'unsafe-inline'")
  })

  it('refuses framing, plugins and a rewritten base URI', () => {
    expect(d.get('frame-ancestors')).toBe("'none'")
    expect(d.get('object-src')).toBe("'none'")
    expect(d.get('base-uri')).toBe("'self'")
    expect(d.get('form-action')).toBe("'self'")
  })

  it('keeps the default locked to this origin', () => {
    expect(d.get('default-src')).toBe("'self'")
    expect(d.get('connect-src')).toBe("'self'")
  })

  it('never allows eval in production', () => {
    expect(policy).not.toContain("'unsafe-eval'")
    expect(contentSecurityPolicy({ nonce: 'n', dev: true })).toContain("'unsafe-eval'")
  })

  it('upgrades insecure requests only when the request arrived over HTTPS', () => {
    expect(policy).not.toContain('upgrade-insecure-requests')
    expect(contentSecurityPolicy({ nonce: 'n', https: true })).toContain(
      'upgrade-insecure-requests',
    )
  })
})

describe('STATIC_SECURITY_HEADERS', () => {
  const byKey = new Map(STATIC_SECURITY_HEADERS.map(({ key, value }) => [key, value]))

  it('covers the headers a reverse proxy should not have to add', () => {
    expect(byKey.get('X-Content-Type-Options')).toBe('nosniff')
    expect(byKey.get('X-Frame-Options')).toBe('DENY')
    expect(byKey.get('Referrer-Policy')).toBe('strict-origin-when-cross-origin')
    expect(byKey.get('Permissions-Policy')).toContain('camera=()')
    expect(byKey.get('Cross-Origin-Opener-Policy')).toBe('same-origin')
  })

  it('leaves HSTS out, because it is only sent over HTTPS', () => {
    expect(byKey.has('Strict-Transport-Security')).toBe(false)
    expect(HSTS).toContain('max-age=31536000')
  })
})
