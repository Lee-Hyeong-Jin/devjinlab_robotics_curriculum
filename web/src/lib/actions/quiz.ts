'use server'

import { revalidatePath } from 'next/cache'
import { getTranslations } from 'next-intl/server'
import type { ReactNode } from 'react'

import { apiPost } from '../api/client'
import type { QuizRun, Rating, ReviewResult } from '../api/types'
import { renderMarkdown } from '../markdown/render'
import { RATINGS, readAnswers, unanswered, type AnswerableQuestion } from '../quiz'
import { toActionState } from './problem'
import type { ActionState } from './result'

/** A quiz run's outcome, carried back to the screen alongside the form state. */
export interface QuizState extends ActionState {
  run?: QuizRun
  /**
   * Each answered question's explanation, rendered here on the server with the
   * lesson Markdown pipeline (KaTeX, code, GFM, the same sanitiser) and shipped
   * as an RSC-serialised React tree — never as HTML the client would have to
   * trust. Keyed by question id; a question without an explanation is absent.
   */
  explanations?: Record<string, ReactNode>
  /** Each question's correct answer, rendered the same way (it can contain LaTeX). */
  correctAnswers?: Record<string, ReactNode>
}

/**
 * `POST /quiz/runs` — grade the whole quiz at once.
 *
 * The API returns per-question correctness and explanations, which the screen
 * shows immediately (AC-WEB.5). A card is created for each wrong answer, so the
 * dashboard's due count changes too.
 */
export async function submitQuiz(_previous: QuizState, form: FormData): Promise<QuizState> {
  const t = await getTranslations('quiz')
  const lessonId = String(form.get('lessonId') ?? '')
  const moduleId = String(form.get('moduleId') ?? '')

  let questions: AnswerableQuestion[]
  try {
    questions = JSON.parse(String(form.get('questions') ?? '[]')) as typeof questions
  } catch {
    return { error: t('submitFailed') }
  }

  const answers = readAnswers(form, questions)
  if (Object.keys(answers).length === 0) return { error: t('noAnswers') }
  // Every question has to be answered. Grading only the answered ones scored one right
  // answer out of three questions as 100%.
  const missing = unanswered(questions, answers)
  if (missing.length > 0) {
    return {
      error: t('unanswered', { count: missing.length }),
      fields: Object.fromEntries(missing.map((id) => [`q:${id}`, t('unansweredOne')])),
    }
  }

  try {
    const run = await apiPost<QuizRun>('/api/v1/quiz/runs', {
      lesson_id: lessonId,
      answers,
    })
    revalidatePath(`/modules/${moduleId}/${lessonId}`)
    revalidatePath('/')
    const explanations: Record<string, ReactNode> = {}
    const correctAnswers: Record<string, ReactNode> = {}
    for (const answer of run.answers) {
      const content = renderMarkdown(answer.explanation ?? undefined).content
      if (content !== null) explanations[answer.question_id] = content
      // The correct answer carries the same Markdown and LaTeX as the choices it names.
      const correct = renderMarkdown(answer.correct_answer ?? undefined).content
      if (correct !== null) correctAnswers[answer.question_id] = correct
    }
    return {
      run,
      explanations,
      correctAnswers,
      message: t('graded', { correct: run.correct, total: run.total }),
    }
  } catch (error) {
    return toActionState(error, t('submitFailed'))
  }
}

/** A rated card's new schedule, carried back to the review screen. */
export interface ReviewState extends ActionState {
  result?: ReviewResult
}

/** `POST /review/{card_id}` — rate a card and get its next due date. */
export async function rateCard(_previous: ReviewState, form: FormData): Promise<ReviewState> {
  const t = await getTranslations('review')
  const cardId = String(form.get('cardId') ?? '')
  const rating = String(form.get('rating') ?? '')

  if (!RATINGS.includes(rating as Rating)) return { error: t('ratingInvalid') }

  try {
    const result = await apiPost<ReviewResult>(`/api/v1/review/${encodeURIComponent(cardId)}`, {
      rating,
    })
    revalidatePath('/review')
    revalidatePath('/')
    return { result, message: t('rated', { days: result.interval_days }) }
  } catch (error) {
    return toActionState(error, t('rateFailed'))
  }
}
