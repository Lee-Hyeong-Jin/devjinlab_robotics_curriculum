import { describe, expect, it, afterEach } from 'vitest'

import { absoluteUrl, languageAlternates, metaDescription, pageSeo } from './seo'

const ORIGINAL = { ...process.env }

afterEach(() => {
  process.env = { ...ORIGINAL }
})

describe('absoluteUrl', () => {
  it('uses RC_PUBLIC_URL and drops its trailing slash', () => {
    process.env.RC_PUBLIC_URL = 'https://learnrobotics.example.com/'
    expect(absoluteUrl('/lessons/a')).toBe('https://learnrobotics.example.com/lessons/a')
  })
})

describe('languageAlternates', () => {
  it('gives the default language the bare path and pins the other with ?lang=', () => {
    process.env.RC_PUBLIC_URL = 'https://x.test'
    const alternates = languageAlternates('/modules/m1')
    expect(alternates.ko).toBe('https://x.test/modules/m1')
    expect(alternates.en).toBe('https://x.test/modules/m1?lang=en')
    expect(alternates['x-default']).toBe('https://x.test/modules/m1')
  })

  it('appends to a path that already carries a query', () => {
    process.env.RC_PUBLIC_URL = 'https://x.test'
    expect(languageAlternates('/roadmap?course=research').en).toBe(
      'https://x.test/roadmap?course=research&lang=en',
    )
  })
})

describe('pageSeo', () => {
  it('refuses to index by default, even for a page that asks', () => {
    // RC_PUBLIC_CONTENT unset: the deployment publishes nothing yet (ADR 0016).
    delete process.env.RC_PUBLIC_CONTENT
    const meta = pageSeo({ path: '/lessons/a', title: 'A', publishable: true })
    expect(meta.robots).toMatchObject({ index: false, follow: false })
  })

  it('indexes a publishable page once the deployment publishes content', () => {
    process.env.RC_PUBLIC_CONTENT = '1'
    const meta = pageSeo({ path: '/lessons/a', title: 'A', publishable: true })
    expect(meta.robots).toMatchObject({ index: true, follow: true })
  })

  it('never indexes a page that is not publishable', () => {
    process.env.RC_PUBLIC_CONTENT = '1'
    const meta = pageSeo({ path: '/profile', title: '프로필' })
    expect(meta.robots).toMatchObject({ index: false, follow: false })
  })

  it('carries the canonical URL, the alternates and the cards', () => {
    process.env.RC_PUBLIC_URL = 'https://x.test'
    const meta = pageSeo({
      path: '/lessons/a',
      title: '좌표 변환',
      description: '설명',
      publishable: true,
      type: 'article',
    })
    expect(meta.alternates?.canonical).toBe('https://x.test/lessons/a')
    expect(meta.alternates?.languages).toMatchObject({ en: 'https://x.test/lessons/a?lang=en' })
    expect(meta.openGraph).toMatchObject({ type: 'article', url: 'https://x.test/lessons/a' })
    expect(meta.twitter).toMatchObject({ card: 'summary', title: '좌표 변환' })
  })
})

describe('metaDescription', () => {
  it('collapses whitespace and leaves a short summary alone', () => {
    expect(metaDescription('  두 줄\n  요약  ')).toBe('두 줄 요약')
  })

  it('trims a long summary at a word boundary', () => {
    const text = `${'word '.repeat(60)}end`
    const out = metaDescription(text)
    expect(out.length).toBeLessThanOrEqual(161)
    expect(out.endsWith('…')).toBe(true)
    expect(out).not.toContain('wor…')
  })

  it('handles a missing summary', () => {
    expect(metaDescription(null)).toBe('')
    expect(metaDescription(undefined)).toBe('')
  })
})
