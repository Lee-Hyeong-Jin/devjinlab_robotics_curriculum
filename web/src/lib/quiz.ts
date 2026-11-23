/**
 * Quiz and review helpers that are not Server Actions.
 *
 * Every export of a `'use server'` module must be an async function, so the
 * pure pieces live here and are unit tested directly.
 */
import type { QuizQuestionPublic, Rating } from './api/types'

/** The ratings the review screen offers, in SM-2 order. */
export const RATINGS: Rating[] = ['again', 'hard', 'good', 'easy']

export type AnswerableQuestion = Pick<QuizQuestionPublic, 'id' | 'type'>

/**
 * Collect one answer per question in the CLI's notation, which is what
 * `QuizSubmission.answers` takes: `2` for single choice, `1,3` for multiple,
 * `o`/`x` for true-false, free text for short answers.
 *
 * Unanswered questions are left out of the result; the caller refuses a submission that
 * leaves any out (`unanswered`), because grading only what was answered turned one right
 * answer out of three questions into "100%" (QA B-06).
 */
export function readAnswers(
  form: Pick<FormData, 'get' | 'getAll'>,
  questions: readonly AnswerableQuestion[],
): Record<string, string> {
  const answers: Record<string, string> = {}
  for (const question of questions) {
    if (question.type === 'multiple') {
      const picked = form
        .getAll(`q:${question.id}`)
        .filter((value): value is string => typeof value === 'string')
        .map((value) => value.trim())
        .filter((value) => value !== '')
      if (picked.length > 0) answers[question.id] = picked.join(',')
      continue
    }
    const value = form.get(`q:${question.id}`)
    if (typeof value === 'string' && value.trim() !== '') answers[question.id] = value.trim()
  }
  return answers
}

/** Choice labels are 1-based in the CLI notation. */
export function choiceValue(index: number): string {
  return String(index + 1)
}

/** The questions a submission leaves unanswered, in order. */
export function unanswered(
  questions: readonly AnswerableQuestion[],
  answers: Record<string, string>,
): string[] {
  return questions.filter((question) => !(question.id in answers)).map((question) => question.id)
}

/**
 * The 1-based choice numbers in an answer written in the CLI notation (`2`, `1,3`), or an empty
 * list when it is not a list of numbers (a short answer, `o`/`x`).
 */
export function pickedChoices(given: string | null | undefined): number[] {
  if (!given) return []
  const parts = given.split(',').map((part) => part.trim())
  if (parts.some((part) => !/^\d+$/.test(part))) return []
  return parts.map(Number)
}
