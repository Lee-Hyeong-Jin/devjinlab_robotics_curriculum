import { useTranslations } from 'next-intl'
import type { ReactNode } from 'react'

import type { LessonProblem } from '@/lib/api/types'

import { Chip } from './Chip'
import { MarkdownBody } from './MarkdownBody'

/** A problem with its prompt and solution already rendered (they carry KaTeX). */
export interface RenderedProblem extends Omit<LessonProblem, 'prompt' | 'solution'> {
  prompt: ReactNode
  solution: ReactNode
}

export interface ProblemSetProps {
  problems: readonly RenderedProblem[]
}

/** 1 star of 3 shown as a filled/hollow rating, so difficulty is not just a number. */
function stars(count: number): string {
  return '★'.repeat(count) + '☆'.repeat(Math.max(0, 3 - count))
}

/**
 * The lesson's problem set (lesson-standard.md §11-3).
 *
 * Not a quiz: nothing is submitted, graded or scheduled for review — a derivation or a proof
 * cannot be marked automatically. The solution sits behind a `<details>` so a reader can work
 * first, and its summary says what is behind it (a sketch, a full solution, a rubric).
 */
export function ProblemSet({ problems }: ProblemSetProps) {
  const t = useTranslations('problem')
  if (problems.length === 0) return null

  return (
    <ol className="flex flex-col gap-5">
      {problems.map((problem, index) => (
        <li
          key={problem.id}
          className="border-border-default border-t pt-4 first:border-t-0 first:pt-0"
        >
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span className="text-muted text-xs font-semibold">{index + 1}</span>
            <Chip>{t(`type.${problem.type}`)}</Chip>
            <span className="text-muted text-xs" aria-label={t('stars', { count: problem.stars })}>
              {stars(problem.stars)}
            </span>
            {problem.refers_to.length > 0 ? (
              <span className="text-muted text-xs">
                {t('refersTo')}: {problem.refers_to.join(' · ')}
              </span>
            ) : null}
          </div>
          <MarkdownBody>{problem.prompt}</MarkdownBody>
          {problem.solution ? (
            <details className="border-border-default mt-3 rounded-lg border px-3 py-2">
              <summary className="text-accent cursor-pointer text-sm font-medium">
                {t(`policy.${problem.solution_policy}`)}
              </summary>
              <div className="mt-2">
                <MarkdownBody>{problem.solution}</MarkdownBody>
                {problem.tolerance !== null ? (
                  <p className="text-muted mt-2 text-xs">
                    {t('tolerance')}: <code className="font-mono">{problem.tolerance}</code>
                  </p>
                ) : null}
              </div>
            </details>
          ) : null}
        </li>
      ))}
    </ol>
  )
}
