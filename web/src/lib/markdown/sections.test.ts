import { describe, expect, it } from 'vitest'

import { stripLessonSections } from './sections'

const STUDY = '1. 영상을 본다.\n2. 본문을 읽는다.'

const BODY = [
  '## 개념',
  '',
  '벡터는 방향과 크기다.',
  '',
  '## 확인 퀴즈',
  '',
  '```quiz',
  '- id: q1',
  '  type: single',
  '  prompt: 내적이 0이면?',
  '```',
  '',
  '## 이 단계 공부법',
  '',
  STUDY,
  '',
  '## 참고 자료',
  '',
  '- [Modern Robotics](https://example.org)',
].join('\n')

describe('stripLessonSections', () => {
  it('removes the quiz section instead of printing its YAML source', () => {
    const out = stripLessonSections(BODY, { studyMethod: STUDY })
    expect(out).not.toContain('type: single')
    expect(out).not.toContain('확인 퀴즈')
  })

  it('removes the study-method section, which the card above already shows', () => {
    const out = stripLessonSections(BODY, { studyMethod: STUDY })
    expect(out).not.toContain('이 단계 공부법')
    expect(out).not.toContain('영상을 본다')
  })

  it('keeps every other section, in order', () => {
    const out = stripLessonSections(BODY, { studyMethod: STUDY })
    expect(out.split('\n').filter((line) => line.startsWith('## '))).toEqual([
      '## 개념',
      '## 참고 자료',
    ])
    expect(out).toContain('벡터는 방향과 크기다.')
  })

  it('keeps the study-method section when the API did not surface it separately', () => {
    expect(stripLessonSections(BODY)).toContain('이 단계 공부법')
  })

  it('matches a translated study-method heading by its text, not its name', () => {
    const body = '## How to study this stage\n\n1. Watch the video.\n\n## Concepts\n\nText.'
    const out = stripLessonSections(body, { studyMethod: '1. Watch the video.' })
    expect(out).toBe('## Concepts\n\nText.')
  })

  it('keeps a section that holds a quiz fence next to real prose', () => {
    const body = '## 예제\n\n코드 설명.\n\n```quiz\n- id: q1\n```\n\n끝.'
    const out = stripLessonSections(body, {})
    expect(out).toContain('## 예제')
    expect(out).toContain('코드 설명.')
    expect(out).toContain('끝.')
    expect(out).not.toContain('id: q1')
  })

  it('never treats a heading inside a fenced block as a section heading', () => {
    const body = '## 개념\n\n```md\n## 이 단계 공부법\n```\n'
    expect(stripLessonSections(body, { studyMethod: 'x' })).toContain('## 이 단계 공부법')
  })

  it('returns an empty string for missing input', () => {
    expect(stripLessonSections(undefined)).toBe('')
    expect(stripLessonSections(null)).toBe('')
  })
})

describe('stripLessonSections with a problem set', () => {
  const BODY = [
    '## 개념',
    '',
    '본문.',
    '',
    '## 문제',
    '',
    '```problemset',
    'problems:',
    '  - id: p1',
    '    type: proof',
    '```',
  ].join('\n')

  it('removes the problem-set block, which the screen lays out itself', () => {
    const out = stripLessonSections(BODY)
    expect(out).not.toContain('type: proof')
    expect(out).not.toContain('problems:')
  })

  it('removes a section that held nothing but the block', () => {
    expect(stripLessonSections(BODY)).not.toContain('## 문제')
  })

  it('keeps prose that shares the section with the block', () => {
    const body = '## 문제\n\n먼저 읽어라.\n\n```problemset\nproblems:\n  - id: p1\n```\n'
    const out = stripLessonSections(body)
    expect(out).toContain('## 문제')
    expect(out).toContain('먼저 읽어라.')
    expect(out).not.toContain('id: p1')
  })
})
