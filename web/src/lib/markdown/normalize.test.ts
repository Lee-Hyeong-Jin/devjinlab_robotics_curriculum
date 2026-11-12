import { describe, expect, it } from 'vitest'

import { normalizeDisplayMath } from './normalize'

describe('normalizeDisplayMath', () => {
  it('puts a one-line display formula on its own lines', () => {
    expect(normalizeDisplayMath('$$x = y$$')).toBe('$$\nx = y\n$$')
  })

  it('splits a multi-line formula whose markers share a line with content', () => {
    // remark-math would otherwise read `T_{ac} = …` as fence meta, never close the
    // block, and render the rest of the lesson as raw TeX.
    expect(normalizeDisplayMath('$$T_{ac} = T_{ab}, \\qquad\nT^{-1} = T_{ba}$$')).toBe(
      '$$\nT_{ac} = T_{ab}, \\qquad\nT^{-1} = T_{ba}\n$$',
    )
  })

  it('keeps the prose that precedes and follows a formula on the same line', () => {
    expect(normalizeDisplayMath('앞 $$x$$ 뒤')).toBe('앞\n$$\nx\n$$\n뒤')
  })

  it('leaves markers that are already alone untouched', () => {
    const text = '$$\nx = y\n$$'
    expect(normalizeDisplayMath(text)).toBe(text)
  })

  it('leaves inline math alone', () => {
    const text = '좌표 $(2, 1)$ 에서 $90^\\circ$ 방향.'
    expect(normalizeDisplayMath(text)).toBe(text)
  })

  it('never touches a fenced code block', () => {
    const text = '```python\nprice = "$$"\n```'
    expect(normalizeDisplayMath(text)).toBe(text)
  })

  it('never touches an inline-code span', () => {
    const text = '구분자는 `$$` 다.'
    expect(normalizeDisplayMath(text)).toBe(text)
  })
})
