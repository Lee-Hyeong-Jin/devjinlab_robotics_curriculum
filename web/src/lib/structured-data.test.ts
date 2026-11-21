import { afterEach, describe, expect, it } from 'vitest'

import {
  breadcrumbs,
  courseListSchema,
  isoDuration,
  organizationSchema,
  webSiteSchema,
} from './structured-data'

const ORIGINAL = { ...process.env }

afterEach(() => {
  process.env = { ...ORIGINAL }
})

describe('home page structured data', () => {
  it('describes the site and its organisation with absolute URLs', () => {
    process.env.RC_PUBLIC_URL = 'https://x.test'
    expect(webSiteSchema('사이트', '설명', 'ko')).toMatchObject({
      '@type': 'WebSite',
      name: '사이트',
      url: 'https://x.test/',
      inLanguage: 'ko',
    })
    expect(organizationSchema('사이트')).toMatchObject({
      '@type': 'Organization',
      url: 'https://x.test/',
      logo: 'https://x.test/icon-512.png',
    })
  })

  it('lists the courses in order', () => {
    process.env.RC_PUBLIC_URL = 'https://x.test'
    const list = courseListSchema([
      ['전문가 코스', '/roadmap'],
      ['연구원 트랙', '/roadmap?course=research'],
    ])
    expect(list.itemListElement).toEqual([
      { '@type': 'ListItem', position: 1, name: '전문가 코스', url: 'https://x.test/roadmap' },
      {
        '@type': 'ListItem',
        position: 2,
        name: '연구원 트랙',
        url: 'https://x.test/roadmap?course=research',
      },
    ])
  })
})

describe('breadcrumbs', () => {
  it('numbers the trail from one', () => {
    process.env.RC_PUBLIC_URL = 'https://x.test'
    const trail = breadcrumbs([
      ['로드맵', '/roadmap'],
      ['M1', '/modules/m1'],
    ])
    expect(trail.itemListElement).toMatchObject([
      { position: 1, name: '로드맵', item: 'https://x.test/roadmap' },
      { position: 2, name: 'M1', item: 'https://x.test/modules/m1' },
    ])
  })
})

describe('isoDuration', () => {
  it('writes minutes as an ISO 8601 duration', () => {
    expect(isoDuration(90)).toBe('PT1H30M')
    expect(isoDuration(120)).toBe('PT2H')
    expect(isoDuration(45)).toBe('PT45M')
    expect(isoDuration(0)).toBeUndefined()
    expect(isoDuration(null)).toBeUndefined()
  })
})
