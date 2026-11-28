/**
 * The questions the landing page and the study guide answer, as `[question, answer]` pairs.
 *
 * Both pages print the pairs and repeat them in their `FAQPage` JSON-LD, so the list is built
 * in one place. Questions 7–13 are the ones readers asked when the site was first shared:
 * who it is for, what it leads to, whether there are videos, who writes the lessons, how the
 * course differs from others, whether it is maths-first, and what it does not cover.
 */

export type FaqKey =
  | 'faq1Q'
  | 'faq1A'
  | 'faq2Q'
  | 'faq2A'
  | 'faq3Q'
  | 'faq3A'
  | 'faq4Q'
  | 'faq4A'
  | 'faq5Q'
  | 'faq5A'
  | 'faq6Q'
  | 'faq6A'
  | 'faq7Q'
  | 'faq7A'
  | 'faq8Q'
  | 'faq8A'
  | 'faq9Q'
  | 'faq9A'
  | 'faq10Q'
  | 'faq10A'
  | 'faq11Q'
  | 'faq11A'
  | 'faq12Q'
  | 'faq12A'
  | 'faq13Q'
  | 'faq13A'

/** The `landing` message namespace, narrowed to what the FAQ needs. */
export type FaqTranslate = (key: FaqKey, values?: Record<string, string | number>) => string

/** Numbers computed from the curriculum that the "how long" answer quotes. */
export interface FaqTotals {
  expertLessons: number
  expertHours: number
  researchLessons: number
}

export type FaqItem = [question: string, answer: string]

type QuestionNumber = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13

/** Which questions each page shows, in reading order. */
const LANDING_ORDER: readonly QuestionNumber[] = [1, 7, 8, 11, 12, 13, 2, 3, 4, 5, 9, 10, 6]
const GUIDE_ORDER: readonly QuestionNumber[] = [1, 12, 3, 4, 5, 13, 9, 10, 2]

/**
 * Every pair, by question number.
 *
 * The keys are written out one by one because the catalogue test finds used messages by their
 * literal `t('key')` calls; a key assembled at run time would look unused.
 */
function pairs(t: FaqTranslate, totals: FaqTotals): Record<QuestionNumber, FaqItem> {
  return {
    1: [t('faq1Q'), t('faq1A')],
    2: [t('faq2Q'), t('faq2A')],
    3: [t('faq3Q'), t('faq3A')],
    4: [t('faq4Q'), t('faq4A', { ...totals })],
    5: [t('faq5Q'), t('faq5A')],
    6: [t('faq6Q'), t('faq6A')],
    7: [t('faq7Q'), t('faq7A')],
    8: [t('faq8Q'), t('faq8A')],
    9: [t('faq9Q'), t('faq9A')],
    10: [t('faq10Q'), t('faq10A')],
    11: [t('faq11Q'), t('faq11A')],
    12: [t('faq12Q'), t('faq12A')],
    13: [t('faq13Q'), t('faq13A')],
  }
}

/** The landing page's FAQ: orientation first, practicalities after. */
export function landingFaq(t: FaqTranslate, totals: FaqTotals): FaqItem[] {
  const all = pairs(t, totals)
  return LANDING_ORDER.map((n) => all[n])
}

/** The study guide's FAQ: the same answers, without the ones the guide's own text gives. */
export function guideFaq(t: FaqTranslate, totals: FaqTotals): FaqItem[] {
  const all = pairs(t, totals)
  return GUIDE_ORDER.map((n) => all[n])
}
