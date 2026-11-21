import { describe, expect, it, afterEach } from 'vitest'

import {
  absoluteUrl,
  languageAlternates,
  metaDescription,
  pageSeo,
  plainText,
  siteVerification,
} from './seo'

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
    expect(meta.twitter).toMatchObject({ card: 'summary_large_image', title: '좌표 변환' })
    // The card image is named on every page; a nested route does not inherit it.
    expect(meta.openGraph?.images).toEqual([
      {
        url: 'https://x.test/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Robotics Expert Course',
      },
    ])
  })

  it('names the language the page is rendered in, not always the default', () => {
    const ko = pageSeo({ path: '/roadmap', title: '로드맵' })
    expect(ko.openGraph).toMatchObject({ locale: 'ko_KR', alternateLocale: ['en_US'] })
    const en = pageSeo({ path: '/roadmap', title: 'Roadmap', locale: 'en', siteName: 'Site' })
    expect(en.openGraph).toMatchObject({
      locale: 'en_US',
      alternateLocale: ['ko_KR'],
      siteName: 'Site',
    })
  })

  it('can use the title as the whole <title>, for the home page', () => {
    expect(pageSeo({ path: '/', title: '사이트', absoluteTitle: true }).title).toEqual({
      absolute: '사이트',
    })
    expect(pageSeo({ path: '/roadmap', title: '로드맵' }).title).toBe('로드맵')
  })
})

describe('siteVerification', () => {
  it('is absent until a token is configured', () => {
    delete process.env.RC_GOOGLE_SITE_VERIFICATION
    delete process.env.RC_NAVER_SITE_VERIFICATION
    expect(siteVerification()).toBeUndefined()
  })

  it('carries the Google and Naver tokens', () => {
    process.env.RC_GOOGLE_SITE_VERIFICATION = ' g-token '
    process.env.RC_NAVER_SITE_VERIFICATION = 'n-token'
    expect(siteVerification()).toEqual({
      google: 'g-token',
      other: { 'naver-site-verification': 'n-token' },
    })
  })
})

describe('plainText', () => {
  it('turns inline TeX into characters a search result can show', () => {
    expect(plainText('오류 확률 $\\Phi(-r/2)$ 가 $1-q$ 로 수렴')).toBe(
      '오류 확률 Φ(-r/2) 가 1-q 로 수렴',
    )
    expect(plainText('$r \\to 0$, $\\mathcal{C} = 0.172$, $\\succeq 0$')).toBe(
      'r → 0, C = 0.172, ⪰ 0',
    )
  })

  it('keeps the grouping of fractions, exponents and subscripts', () => {
    expect(plainText('$\\frac{q}{1-q}$')).toBe('q/(1-q)')
    expect(plainText('$\\mathbb{R}^2$, $S^{-1}$, $K^\\top$, $O(n^3)$')).toBe('R², S⁻¹, Kᵀ, O(n³)')
    expect(plainText('$P_{k+1}$ 와 $e^{-n\\,\\mathcal{C}}$')).toBe('P_(k+1) 와 e^(-nC)')
    expect(plainText('$\\sqrt{N}$, $\\tfrac12$')).toBe('√N, 1/2')
  })

  it('drops Markdown marks but keeps their text', () => {
    expect(plainText('**굵게** 와 `code` 와 [링크](https://x.test)')).toBe('굵게 와 code 와 링크')
  })

  it('leaves no dollar sign or backslash from a formula behind', () => {
    const out = plainText(
      '$\\tfrac12\\nu^\\top S^{-1}\\nu$ 와 $\\log\\frac{q}{(1-q)/(C-1)}$ 와 $\\|x\\|_2$',
    )
    expect(out).not.toMatch(/[$\\\\{}]/)
  })

  it('handles a missing value', () => {
    expect(plainText(null)).toBe('')
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

  it('describes a summary with formulas in plain text (the snippet shows the string as is)', () => {
    expect(metaDescription('기하만 쓰면 $\\Phi(-r/2)$ 다.')).toBe('기하만 쓰면 Φ(-r/2) 다.')
  })

  it('handles a missing summary', () => {
    expect(metaDescription(null)).toBe('')
    expect(metaDescription(undefined)).toBe('')
  })
})
