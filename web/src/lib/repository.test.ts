import { afterEach, describe, expect, it } from 'vitest'

import {
  communityUrl,
  DEFAULT_REPOSITORY_URL,
  lessonEditUrl,
  lessonIssueUrl,
  repositoryUrl,
} from './repository'

const ORIGINAL = { ...process.env }

afterEach(() => {
  process.env = { ...ORIGINAL }
})

describe('repository links (#54)', () => {
  it('points at this project unless a deployment says otherwise', () => {
    delete process.env.RC_REPO_URL
    expect(repositoryUrl()).toBe(DEFAULT_REPOSITORY_URL)
    process.env.RC_REPO_URL = 'https://github.com/someone/fork/'
    expect(repositoryUrl()).toBe('https://github.com/someone/fork')
  })

  it('can be turned off, and ignores an address that is not a web address', () => {
    for (const value of ['off', 'OFF', '0', 'false', 'none']) {
      process.env.RC_REPO_URL = value
      expect(repositoryUrl(), value).toBeNull()
    }
    process.env.RC_REPO_URL = 'javascript:alert(1)'
    expect(repositoryUrl()).toBeNull()
    process.env.RC_REPO_URL = 'not a url'
    expect(repositoryUrl()).toBeNull()
  })

  it('opens the content-issue form with the lesson filled in', () => {
    const url = new URL(
      lessonIssueUrl('https://github.com/o/r', 'm1-vectors-matrices', '벡터와 행렬'),
    )
    expect(url.pathname).toBe('/o/r/issues/new')
    expect(url.searchParams.get('template')).toBe('content_issue.yml')
    expect(url.searchParams.get('lesson')).toBe('m1-vectors-matrices')
    expect(url.searchParams.get('title')).toBe('[content] 벡터와 행렬')
  })

  it('opens the editor on the lesson file, and on nothing else', () => {
    expect(
      lessonEditUrl('https://github.com/o/r', 'curriculum/robotics-expert/m1/vectors.en.md'),
    ).toBe('https://github.com/o/r/edit/main/curriculum/robotics-expert/m1/vectors.en.md')
    for (const path of [
      null,
      undefined,
      '',
      'README.md',
      'curriculum/../.github/workflows/ci.yml',
      'curriculum/a/b.md?x=1',
      'curriculum//b.md',
      'curriculum/a/b.yaml',
      '/etc/passwd',
    ]) {
      expect(lessonEditUrl('https://github.com/o/r', path), String(path)).toBeNull()
    }
  })

  it('offers a community link only when a deployment names a place that exists', () => {
    delete process.env.RC_COMMUNITY_URL
    expect(communityUrl()).toBeNull()
    process.env.RC_COMMUNITY_URL = 'https://github.com/o/r/discussions'
    expect(communityUrl()).toBe('https://github.com/o/r/discussions')
    process.env.RC_COMMUNITY_URL = 'http://insecure.example/forum'
    expect(communityUrl()).toBeNull()
    process.env.RC_COMMUNITY_URL = 'javascript:alert(1)'
    expect(communityUrl()).toBeNull()
  })
})
