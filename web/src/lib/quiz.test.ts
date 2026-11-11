import { describe, expect, it } from 'vitest'

import { RATINGS, choiceValue, readAnswers } from './quiz'

function formOf(entries: Array<[string, string]>): FormData {
  const form = new FormData()
  for (const [name, value] of entries) form.append(name, value)
  return form
}

describe('readAnswers', () => {
  it('reads a single choice as its 1-based index', () => {
    const form = formOf([['q:q1', '2']])
    expect(readAnswers(form, [{ id: 'q1', type: 'single' }])).toEqual({ q1: '2' })
  })

  it('joins a multiple choice with commas, in the order picked', () => {
    const form = formOf([
      ['q:q1', '1'],
      ['q:q1', '3'],
    ])
    expect(readAnswers(form, [{ id: 'q1', type: 'multiple' }])).toEqual({ q1: '1,3' })
  })

  it('reads true-false as o or x and trims short answers', () => {
    const form = formOf([
      ['q:q1', 'o'],
      ['q:q2', '  자유 응답  '],
    ])
    expect(
      readAnswers(form, [
        { id: 'q1', type: 'truefalse' },
        { id: 'q2', type: 'short' },
      ]),
    ).toEqual({ q1: 'o', q2: '자유 응답' })
  })

  it('leaves unanswered questions out entirely', () => {
    const form = formOf([
      ['q:q1', '1'],
      ['q:q3', '   '],
    ])
    const answers = readAnswers(form, [
      { id: 'q1', type: 'single' },
      { id: 'q2', type: 'single' },
      { id: 'q3', type: 'short' },
    ])
    expect(answers).toEqual({ q1: '1' })
    expect('q2' in answers).toBe(false)
    expect('q3' in answers).toBe(false)
  })

  it('ignores a multiple choice with nothing picked', () => {
    expect(readAnswers(new FormData(), [{ id: 'q1', type: 'multiple' }])).toEqual({})
  })
})

describe('choiceValue', () => {
  it('is 1-based', () => {
    expect(choiceValue(0)).toBe('1')
    expect(choiceValue(3)).toBe('4')
  })
})

describe('RATINGS', () => {
  it('offers the four SM-2 ratings in order', () => {
    expect(RATINGS).toEqual(['again', 'hard', 'good', 'easy'])
  })
})
