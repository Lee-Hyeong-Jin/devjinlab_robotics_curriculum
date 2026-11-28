import { describe, expect, it } from 'vitest'

import en from '../../messages/en.json'
import ko from '../../messages/ko.json'

import { guideFaq, landingFaq, type FaqKey, type FaqTranslate } from './faq'

const totals = { expertLessons: 50, expertHours: 93, researchLessons: 105 }

/** A translator over a real message file, substituting `{name}` like next-intl does. */
function translator(messages: Record<string, string>): FaqTranslate {
  return (key: FaqKey, values = {}) => {
    const template = messages[key]
    if (template === undefined) throw new Error(`missing message landing.${key}`)
    return template.replace(/\{(\w+)\}/g, (_, name: string) => String(values[name] ?? `{${name}}`))
  }
}

describe.each([
  ['en', en.landing as Record<string, string>],
  ['ko', ko.landing as Record<string, string>],
])('FAQ in %s', (_lang, messages) => {
  const t = translator(messages)

  it('answers the ten landing questions, each with text and no unfilled placeholder', () => {
    const faq = landingFaq(t, totals)
    expect(faq).toHaveLength(10)
    expect(new Set(faq.map(([question]) => question)).size).toBe(10)
    for (const [question, answer] of faq) {
      expect(question.trim()).not.toBe('')
      expect(answer.trim()).not.toBe('')
      expect(answer).not.toMatch(/\{\w+\}/)
    }
  })

  it('puts who it is for and what it leads to right after where to start', () => {
    const questions = landingFaq(t, totals).map(([question]) => question)
    expect(questions.slice(0, 3)).toEqual([messages.faq1Q, messages.faq7Q, messages.faq8Q])
  })

  it('says on both pages that there are no original videos and how lessons are written', () => {
    for (const faq of [landingFaq(t, totals), guideFaq(t, totals)]) {
      const questions = faq.map(([question]) => question)
      expect(questions).toContain(messages.faq9Q)
      expect(questions).toContain(messages.faq10Q)
    }
  })

  it('quotes the curriculum totals in the "how long" answer', () => {
    const answer = new Map(landingFaq(t, totals)).get(messages.faq4Q as string)
    expect(answer).toContain('50')
    expect(answer).toContain('93')
    expect(answer).toContain('105')
  })
})

it('keeps the guide list a subset of the landing list', () => {
  const t = translator(en.landing as Record<string, string>)
  const landing = new Set(landingFaq(t, totals).map(([question]) => question))
  for (const [question] of guideFaq(t, totals)) expect(landing.has(question)).toBe(true)
})
