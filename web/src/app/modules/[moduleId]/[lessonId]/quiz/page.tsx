import type { Metadata } from 'next'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import { EmptyState } from '@/components/EmptyState'
import { PageHeader } from '@/components/PageHeader'
import { QuizForm, type RenderedQuestion } from '@/components/QuizForm'
import { getQuiz } from '@/lib/api/queries'
import { renderMarkdown } from '@/lib/markdown/render'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('quiz')
  return { title: t('title') }
}

interface Params {
  params: Promise<{ moduleId: string; lessonId: string }>
}

/** Quiz — `GET /lessons/{id}/quiz` then `POST /quiz/runs` (frontend.md §2). */
export default async function QuizPage({ params }: Params) {
  const { moduleId, lessonId } = await params
  const t = await getTranslations('quiz')
  const quiz = await getQuiz(lessonId)

  const back = (
    <Link
      href={`/modules/${moduleId}/${lessonId}`}
      className="text-accent underline underline-offset-2"
    >
      ← {t('backToLesson')}
    </Link>
  )

  if (!quiz) {
    return (
      <>
        <PageHeader title={t('title')} eyebrow={back} />
        <EmptyState title={t('unavailable')} />
      </>
    )
  }
  if (quiz.questions.length === 0) {
    return (
      <>
        <PageHeader title={t('title')} eyebrow={back} />
        <EmptyState title={t('empty')} />
      </>
    )
  }

  // Prompts and choices carry KaTeX, so they go through the lesson Markdown
  // pipeline here, on the server, and reach the client as React trees
  // (AC-WEB.2 — the same formula renders the same way as in the lesson body).
  const questions: RenderedQuestion[] = quiz.questions.map((question) => ({
    id: question.id,
    type: question.type,
    prompt: renderMarkdown(question.prompt).content,
    choices: (question.choices ?? []).map((choice) => renderMarkdown(choice).content),
  }))

  return (
    <>
      <PageHeader title={t('title')} subtitle={t('subtitle')} eyebrow={back} />
      <QuizForm moduleId={moduleId} lessonId={lessonId} questions={questions} />
    </>
  )
}
