'use client'

import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useActionState, useEffect, useRef, useTransition, type FormEvent } from 'react'

import { submitQuiz, type QuizState } from '@/lib/actions/quiz'
import type { QuizQuestionPublic } from '@/lib/api/types'
import { choiceValue, pickedChoices } from '@/lib/quiz'
import type { ReactNode } from 'react'

import { Card } from './Card'
import { Chip } from './Chip'
import { MarkdownBody } from './MarkdownBody'
import { FormMessage } from './form/FormMessage'
import { SubmitButton } from './form/SubmitButton'

/** A question with its prompt and choices already rendered (KaTeX, code, GFM). */
export interface RenderedQuestion {
  id: string
  type: QuizQuestionPublic['type']
  prompt: ReactNode
  choices: ReactNode[]
}

export interface QuizFormProps {
  moduleId: string
  lessonId: string
  questions: RenderedQuestion[]
}

const EMPTY: QuizState = {}

/**
 * The quiz runner: one form over every question, graded in a single
 * `POST /quiz/runs`, with per-question correctness and explanations shown
 * straight after (AC-WEB.5).
 */
export function QuizForm({ moduleId, lessonId, questions }: QuizFormProps) {
  const t = useTranslations('quiz')
  const [state, formAction, actionPending] = useActionState(submitQuiz, EMPTY)
  const [transitionPending, startTransition] = useTransition()
  const formRef = useRef<HTMLFormElement>(null)
  const run = state.run
  const resultFor = (id: string) => run?.answers.find((answer) => answer.question_id === id)

  // Dispatched by hand so the reader's choices stay on screen: React clears a form after its
  // action, which wiped the answers both after "answer every question" and beside the result.
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const data = new FormData(event.currentTarget)
    startTransition(() => formAction(data))
  }

  useEffect(() => {
    if (state === EMPTY) return
    const form = formRef.current
    // To the result when there is one, otherwise to the first question still unanswered.
    const target =
      form?.querySelector<HTMLElement>('[data-unanswered="true"] input') ??
      form?.querySelector<HTMLElement>('#quiz-result')
    target?.focus()
    // Not every environment implements it (jsdom does not).
    if (typeof target?.scrollIntoView === 'function') target.scrollIntoView({ block: 'center' })
  }, [state])

  /** "2" → "2. <the choice>"; a true/false answer → its label; a short answer as typed. */
  function givenAnswer(question: RenderedQuestion, given: string | null | undefined): ReactNode {
    if (!given) return '—'
    if (question.type === 'truefalse') {
      const value = given.trim().toLowerCase()
      return value === 'o' ? t('true') : value === 'x' ? t('false') : given
    }
    const picked = pickedChoices(given).filter((n) => question.choices[n - 1] !== undefined)
    if (picked.length === 0) return given
    return (
      <span className="flex flex-col gap-1">
        {picked.map((n) => (
          <span key={n} className="flex gap-2">
            <span className="text-muted shrink-0 font-mono text-xs">{n}.</span>
            <span className="markdown-body min-w-0">{question.choices[n - 1]}</span>
          </span>
        ))}
      </span>
    )
  }

  return (
    <form ref={formRef} action={formAction} onSubmit={submit} className="flex flex-col gap-6">
      <input type="hidden" name="moduleId" value={moduleId} />
      <input type="hidden" name="lessonId" value={lessonId} />
      <input
        type="hidden"
        name="questions"
        value={JSON.stringify(questions.map((q) => ({ id: q.id, type: q.type })))}
      />

      {state.error ? <FormMessage tone="error">{state.error}</FormMessage> : null}

      {run ? (
        <Card aria-labelledby="quiz-result" className="bg-accent-light border-border-accent">
          <h2 id="quiz-result" tabIndex={-1} className="text-accent font-bold">
            {t('resultHeading')}
          </h2>
          <p className="text-primary mt-1 text-2xl font-semibold tabular-nums">
            {t('percent', { percent: run.percent })}
          </p>
          <p className="text-primary text-sm">
            {t('graded', { correct: run.correct, total: run.total })}
          </p>
          <p className="text-muted mt-1 text-xs">{t('cardsCreated')}</p>
        </Card>
      ) : null}

      <ol className="flex flex-col gap-5">
        {questions.map((question, index) => {
          const result = resultFor(question.id)
          const explanation = state.explanations?.[question.id]
          const name = `q:${question.id}`
          const missing = state.fields?.[name]
          return (
            <li key={question.id} data-unanswered={missing ? 'true' : undefined}>
              <Card
                className={
                  missing
                    ? 'border-danger'
                    : result
                      ? result.correct
                        ? 'border-border-accent'
                        : 'border-danger'
                      : undefined
                }
              >
                <fieldset aria-describedby={missing ? `${name}-missing` : undefined}>
                  <legend className="mb-2 flex max-w-full flex-wrap items-center gap-2">
                    <span className="text-muted text-xs font-semibold">
                      {t('of', { n: index + 1, total: questions.length })}
                    </span>
                    {result ? (
                      <Chip tone={result.correct ? 'success' : 'warning'}>
                        {result.correct ? t('correct') : t('incorrect')}
                      </Chip>
                    ) : null}
                    <span className="text-primary block w-full overflow-x-auto font-medium">
                      {question.prompt}
                    </span>
                    {question.type === 'multiple' ? (
                      <span className="text-muted block w-full text-xs">{t('multipleHint')}</span>
                    ) : null}
                  </legend>

                  {question.type === 'short' ? (
                    <label className="flex flex-col gap-1">
                      <span className="text-muted text-xs">{t('shortAnswerLabel')}</span>
                      <input
                        type="text"
                        name={name}
                        className="bg-surface border-border-default text-primary min-h-11 w-full rounded-lg border px-3 py-2 text-base sm:text-sm"
                      />
                    </label>
                  ) : question.type === 'truefalse' ? (
                    <div className="flex flex-col gap-1">
                      {[
                        { value: 'o', label: t('true') },
                        { value: 'x', label: t('false') },
                      ].map((option) => (
                        <label
                          key={option.value}
                          className="text-primary hover:bg-subtle -mx-2 flex min-h-11 cursor-pointer items-center gap-3 rounded-lg px-2 text-sm"
                        >
                          <input
                            type="radio"
                            name={name}
                            value={option.value}
                            className="border-border-default size-5 shrink-0"
                          />
                          {option.label}
                        </label>
                      ))}
                    </div>
                  ) : (
                    <div className="flex flex-col gap-1">
                      {question.choices.map((choice, choiceIndex) => (
                        <label
                          key={choiceValue(choiceIndex)}
                          className="text-primary hover:bg-subtle -mx-2 flex min-h-11 cursor-pointer items-center gap-3 rounded-lg px-2 py-2 text-sm"
                        >
                          <input
                            type={question.type === 'multiple' ? 'checkbox' : 'radio'}
                            name={name}
                            value={choiceValue(choiceIndex)}
                            className="border-border-default size-5 shrink-0"
                          />
                          <span className="text-muted shrink-0 font-mono text-xs">
                            {choiceValue(choiceIndex)}
                          </span>
                          <span className="markdown-body min-w-0 flex-1 overflow-x-auto">
                            {choice}
                          </span>
                        </label>
                      ))}
                    </div>
                  )}

                  {missing ? (
                    <p id={`${name}-missing`} role="alert" className="text-danger mt-2 text-xs">
                      {missing}
                    </p>
                  ) : null}

                  {result ? (
                    <dl className="border-border-default mt-3 flex flex-col gap-1 border-t pt-3 text-sm">
                      <div className="flex gap-2">
                        <dt className="text-muted">{t('yourAnswer')}</dt>
                        <dd className="text-primary min-w-0">
                          {givenAnswer(question, result.given)}
                        </dd>
                      </div>
                      <div className="flex gap-2">
                        <dt className="text-muted">{t('correctAnswer')}</dt>
                        <dd className="text-primary markdown-body min-w-0">
                          {state.correctAnswers?.[question.id] ?? result.correct_answer}
                        </dd>
                      </div>
                      {explanation || result.explanation ? (
                        <div className="mt-1">
                          <dt className="text-muted">{t('explanation')}</dt>
                          <dd className="text-primary">
                            {explanation ? (
                              <MarkdownBody>{explanation}</MarkdownBody>
                            ) : (
                              result.explanation
                            )}
                          </dd>
                        </div>
                      ) : null}
                    </dl>
                  ) : null}
                </fieldset>
              </Card>
            </li>
          )
        })}
      </ol>

      <div className="flex flex-wrap items-center gap-3">
        <SubmitButton pendingLabel={t('submitting')} pending={actionPending || transitionPending}>
          {run ? t('retry') : t('submit')}
        </SubmitButton>
        <Link
          href={`/modules/${moduleId}/${lessonId}`}
          className="text-accent text-sm underline underline-offset-2"
        >
          {t('backToLesson')}
        </Link>
      </div>
    </form>
  )
}
