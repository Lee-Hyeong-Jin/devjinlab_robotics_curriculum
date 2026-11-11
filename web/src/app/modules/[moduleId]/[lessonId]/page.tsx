import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { Chip } from '@/components/Chip'
import { LessonRow } from '@/components/LessonRow'
import { MarkdownBody } from '@/components/MarkdownBody'
import { PageHeader } from '@/components/PageHeader'
import { ResourceRow } from '@/components/ResourceRow'
import { StudyPanel } from '@/components/StudyPanel'
import { isNotFound } from '@/lib/api/errors'
import { getLesson, getLessonProgress, getModule, getStatus } from '@/lib/api/queries'
import type { Lesson, Module } from '@/lib/api/types'
import { formatMinutes } from '@/lib/format'
import { renderMarkdown } from '@/lib/markdown/render'
import { lockStateFromStatus } from '@/lib/progress'

interface Params {
  params: Promise<{ moduleId: string; lessonId: string }>
}

async function loadLesson(lessonId: string): Promise<Lesson> {
  try {
    return await getLesson(lessonId)
  } catch (error) {
    if (isNotFound(error)) notFound()
    throw error
  }
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { lessonId } = await params
  try {
    const lesson = await getLesson(lessonId)
    return { title: lesson.title ?? lessonId }
  } catch {
    return { title: lessonId }
  }
}

/**
 * Lesson — `GET /lessons/{lesson_id}` + `GET /progress/lessons/{lesson_id}`.
 *
 * The API returns Markdown (`content_format: "markdown"`); rendering KaTeX, code
 * highlighting and the "이 단계 공부법" card is the frontend's job (frontend.md §5,
 * AC-WEB.2). Write actions (timer, completion) arrive in the next step; until then
 * the page points at the CLI.
 */
export default async function LessonPage({ params }: Params) {
  const { moduleId, lessonId } = await params
  const [t, tState, tKind, tActivity, locale] = await Promise.all([
    getTranslations('lesson'),
    getTranslations('state'),
    getTranslations('kind'),
    getTranslations('activityKind'),
    getLocale(),
  ])
  const [lesson, progress, mod, status] = await Promise.all([
    loadLesson(lessonId),
    getLessonProgress(lessonId),
    getModule(moduleId).catch((): Module | null => null),
    getStatus(),
  ])

  const body = renderMarkdown(lesson.body)
  const studyMethod = renderMarkdown(lesson.study_method ?? undefined)
  const siblings = mod?.lessons ?? []
  const sectionHeadings = body.headings.filter((heading) => heading.depth === 2)

  return (
    <>
      <PageHeader
        title={lesson.title ?? lessonId}
        subtitle={lesson.summary}
        eyebrow={
          <Link href={`/modules/${moduleId}`} className="text-accent underline underline-offset-2">
            ← {mod?.title ?? t('toModule')}
          </Link>
        }
        actions={
          <>
            {lesson.difficulty ? (
              <Chip>{t('difficulty', { level: lesson.difficulty })}</Chip>
            ) : null}
            {lesson.estimated_minutes ? (
              <Chip tone="accent">
                {t('estimated', { minutes: formatMinutes(lesson.estimated_minutes, locale) })}
              </Chip>
            ) : null}
            {progress?.status ? (
              <Chip tone={progress.status === 'done' ? 'success' : 'warning'}>
                {tState(lockStateFromStatus(progress.status))}
              </Chip>
            ) : null}
          </>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
        <div className="flex min-w-0 flex-col gap-6">
          {studyMethod.content ? (
            <Card
              as="section"
              className="bg-accent-light border-border-accent"
              aria-labelledby="study-method-heading"
            >
              <h2 id="study-method-heading" className="text-accent mb-2 font-bold">
                {t('studyMethod')}
              </h2>
              <MarkdownBody>{studyMethod.content}</MarkdownBody>
            </Card>
          ) : null}

          {lesson.objectives && lesson.objectives.length > 0 ? (
            <Card as="section" aria-labelledby="objectives-heading">
              <h2 id="objectives-heading" className="text-primary mb-2 font-semibold">
                {t('objectives')}
              </h2>
              <ul className="text-primary list-disc pl-5 text-sm">
                {lesson.objectives.map((objective, index) => (
                  <li key={index}>{objective}</li>
                ))}
              </ul>
            </Card>
          ) : null}

          <Card as="article" aria-labelledby="lesson-body-heading">
            <h2 id="lesson-body-heading" className="sr-only">
              {t('body')}
            </h2>
            <MarkdownBody empty={<p className="text-muted text-sm">{t('empty')}</p>}>
              {body.content}
            </MarkdownBody>
          </Card>

          <nav
            aria-label={`${t('prev')} / ${t('next')}`}
            className="flex flex-wrap items-center justify-between gap-3"
          >
            {lesson.prev_lesson_id ? (
              <Link
                href={`/modules/${moduleId}/${lesson.prev_lesson_id}`}
                className="text-accent text-sm underline underline-offset-2"
              >
                ← {t('prev')}
              </Link>
            ) : (
              <span />
            )}
            {lesson.next_lesson_id ? (
              <Link
                href={`/modules/${moduleId}/${lesson.next_lesson_id}`}
                className="text-accent text-sm underline underline-offset-2"
              >
                {t('next')} →
              </Link>
            ) : null}
          </nav>
        </div>

        <aside className="flex flex-col gap-6" aria-label={t('onThisPage')}>
          <StudyPanel
            moduleId={moduleId}
            lessonId={lessonId}
            progress={progress}
            openSession={status?.open_session ?? null}
          />

          {sectionHeadings.length > 0 ? (
            <Card as="nav" aria-labelledby="toc-heading">
              <h2 id="toc-heading" className="text-primary mb-2 text-sm font-semibold">
                {t('onThisPage')}
              </h2>
              <ul className="flex flex-col gap-1">
                {sectionHeadings.map((heading) => (
                  <li key={heading.id}>
                    <a
                      href={`#${heading.id}`}
                      className="text-muted hover:text-accent block truncate text-sm"
                    >
                      {heading.text}
                    </a>
                  </li>
                ))}
              </ul>
            </Card>
          ) : null}

          {lesson.prerequisites.length > 0 ? (
            <Card as="section" aria-labelledby="prerequisites-heading">
              <h2 id="prerequisites-heading" className="text-primary mb-2 text-sm font-semibold">
                {t('prerequisites')}
              </h2>
              <ul className="flex flex-col gap-1">
                {lesson.prerequisites.map((id) => (
                  <li key={id}>
                    <Link
                      href={`/lessons/${encodeURIComponent(id)}`}
                      className="text-accent font-mono text-xs underline underline-offset-2"
                    >
                      {id}
                    </Link>
                  </li>
                ))}
              </ul>
            </Card>
          ) : null}

          {lesson.activities && lesson.activities.length > 0 ? (
            <Card as="section" aria-labelledby="activities-heading">
              <h2 id="activities-heading" className="text-primary mb-2 text-sm font-semibold">
                {t('activities')}
              </h2>
              <ul className="flex flex-col gap-2">
                {lesson.activities.map((activity, index) => (
                  <li key={activity.id ?? index} className="flex flex-wrap items-center gap-2">
                    {activity.kind ? <Chip>{tActivity(activity.kind)}</Chip> : null}
                    <span className="text-primary min-w-0 flex-1 text-sm">{activity.title}</span>
                    {activity.estimated_minutes ? (
                      <span className="text-muted text-xs">
                        {formatMinutes(activity.estimated_minutes, locale)}
                      </span>
                    ) : null}
                  </li>
                ))}
              </ul>
            </Card>
          ) : null}

          {lesson.resources && lesson.resources.length > 0 ? (
            <Card as="section" aria-labelledby="lesson-resources-heading">
              <h2 id="lesson-resources-heading" className="text-primary mb-1 text-sm font-semibold">
                {t('resources')}
              </h2>
              <ul>
                {lesson.resources.map((resource, index) => (
                  <ResourceRow
                    key={`${resource.title}-${index}`}
                    title={resource.title}
                    url={resource.url}
                    kind={resource.kind}
                    kindLabel={resource.kind ? tKind(resource.kind) : undefined}
                    note={resource.note}
                    externalLabel={t('resources')}
                  />
                ))}
              </ul>
            </Card>
          ) : null}

          {siblings.length > 0 ? (
            <Card as="nav" className="p-2" aria-labelledby="siblings-heading">
              <h2 id="siblings-heading" className="text-primary px-3 py-2 text-sm font-semibold">
                {mod?.title ?? t('toModule')}
              </h2>
              <ul className="flex flex-col">
                {siblings.map((sibling, index) => (
                  <LessonRow
                    key={sibling.id ?? index}
                    moduleId={moduleId}
                    lessonId={sibling.id ?? ''}
                    title={sibling.title ?? sibling.id ?? ''}
                    state={sibling.id === lessonId ? 'in_progress' : 'available'}
                    stateLabel={tState(sibling.id === lessonId ? 'in_progress' : 'available')}
                    current={sibling.id === lessonId}
                  />
                ))}
              </ul>
            </Card>
          ) : null}
        </aside>
      </div>
    </>
  )
}
