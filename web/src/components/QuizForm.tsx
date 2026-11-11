'use client'

import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useActionState } from 'react'

import { submitQuiz, type QuizState } from '@/lib/actions/quiz'
import type { QuizQuestionPublic } from '@/lib/api/types'
import { choiceValue } from '@/lib/quiz'
import type { ReactNode } from 'react'

import { Card } from './Card'
import { Chip } from './Chip'
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
  const [state, formAction] = useActionState(submitQuiz, EMPTY)
  const run = state.run
  const resultFor = (id: string) => run?.answers.find((answer) => answer.question_id === id)

  return (
    <form action={formAction} className="flex flex-col gap-6">
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
          <h2 id="quiz-result" className="text-accent font-bold">
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
          const name = `q:${question.id}`
          return (
            <li key={question.id}>
              <Card
                className={
                  result ? (result.correct ? 'border-border-accent' : 'border-danger') : undefined
                }
              >
                <fieldset>
                  <legend className="mb-2 flex flex-wrap items-center gap-2">
                    <span className="text-muted text-xs font-semibold">
                      {t('of', { n: index + 1, total: questions.length })}
                    </span>
                    {result ? (
                      <Chip tone={result.correct ? 'success' : 'warning'}>
                        {result.correct ? t('correct') : t('incorrect')}
                      </Chip>
                    ) : null}
                    <span className="text-primary block w-full font-medium">{question.prompt}</span>
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
                        className="bg-surface border-border-default text-primary w-full rounded-lg border px-3 py-2 text-sm"
                      />
                    </label>
                  ) : question.type === 'truefalse' ? (
                    <div className="flex flex-col gap-2">
                      {[
                        { value: 'o', label: t('true') },
                        { value: 'x', label: t('false') },
                      ].map((option) => (
                        <label
                          key={option.value}
                          className="text-primary flex items-center gap-2 text-sm"
                        >
                          <input
                            type="radio"
                            name={name}
                            value={option.value}
                            className="border-border-default size-4"
                          />
                          {option.label}
                        </label>
                      ))}
                    </div>
                  ) : (
                    <div className="flex flex-col gap-2">
                      {question.choices.map((choice, choiceIndex) => (
                        <label
                          key={choiceValue(choiceIndex)}
                          className="text-primary flex items-start gap-2 text-sm"
                        >
                          <input
                            type={question.type === 'multiple' ? 'checkbox' : 'radio'}
                            name={name}
                            value={choiceValue(choiceIndex)}
                            className="border-border-default mt-0.5 size-4"
                          />
                          <span className="markdown-body">
                            <span className="text-muted mr-1 font-mono text-xs">
                              {choiceValue(choiceIndex)}
                            </span>
                            {choice}
                          </span>
                        </label>
                      ))}
                    </div>
                  )}

                  {result ? (
                    <dl className="border-border-default mt-3 flex flex-col gap-1 border-t pt-3 text-sm">
                      <div className="flex gap-2">
                        <dt className="text-muted">{t('yourAnswer')}</dt>
                        <dd className="text-primary font-mono">{result.given || '—'}</dd>
                      </div>
                      <div className="flex gap-2">
                        <dt className="text-muted">{t('correctAnswer')}</dt>
                        <dd className="text-primary font-mono">{result.correct_answer}</dd>
                      </div>
                      {result.explanation ? (
                        <div className="mt-1">
                          <dt className="text-muted">{t('explanation')}</dt>
                          <dd className="text-primary">{result.explanation}</dd>
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
        <SubmitButton pendingLabel={t('submitting')}>{run ? t('retry') : t('submit')}</SubmitButton>
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
