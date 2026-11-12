import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { Chip } from '@/components/Chip'
import { LessonRow } from '@/components/LessonRow'
import { PageHeader } from '@/components/PageHeader'
import { ProgressBar } from '@/components/ProgressBar'
import { ResourceRow } from '@/components/ResourceRow'
import { getLessonProgressList, getModule, getResources } from '@/lib/api/queries'
import { isNotFound } from '@/lib/api/errors'
import type { LessonProgress, Module } from '@/lib/api/types'
import { formatMinutes, formatPercent } from '@/lib/format'
import { doneCount, lockStateFromStatus, ratio, type LockState } from '@/lib/progress'

interface Params {
  params: Promise<{ moduleId: string }>
}

async function loadModule(moduleId: string): Promise<Module> {
  try {
    return await getModule(moduleId)
  } catch (error) {
    if (isNotFound(error)) notFound()
    throw error
  }
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { moduleId } = await params
  try {
    const mod = await getModule(moduleId)
    return { title: mod.title ?? moduleId }
  } catch {
    return { title: moduleId }
  }
}

/** Module overview — `GET /modules/{module_id}` + `GET /progress/lessons` (frontend.md §2). */
export default async function ModulePage({ params }: Params) {
  const { moduleId } = await params
  const [t, tState, tKind, locale] = await Promise.all([
    getTranslations('module'),
    getTranslations('state'),
    getTranslations('kind'),
    getLocale(),
  ])
  const [mod, progressList, resources] = await Promise.all([
    loadModule(moduleId),
    getLessonProgressList(),
    getResources({ moduleId }),
  ])

  const progressByLesson = new Map<string, LessonProgress>()
  for (const row of progressList ?? []) {
    if (row.lesson_id) progressByLesson.set(row.lesson_id, row)
  }

  const lessons = mod.lessons ?? []
  const states: LockState[] = lessons.map((lesson) =>
    lockStateFromStatus(lesson.id ? progressByLesson.get(lesson.id)?.status : undefined),
  )
  const progress = ratio(doneCount(states), states.length)

  return (
    <>
      <PageHeader
        title={mod.title ?? moduleId}
        subtitle={mod.summary}
        eyebrow={
          <Link href="/roadmap" className="text-accent underline underline-offset-2">
            ← {t('backToRoadmap')}
          </Link>
        }
        actions={
          <>
            {(mod.level_label ?? mod.level) ? (
              <Chip tone="accent">{mod.level_label ?? mod.level}</Chip>
            ) : null}
            {mod.estimated_minutes ? (
              <Chip>
                {t('estimated', { minutes: formatMinutes(mod.estimated_minutes, locale) })}
              </Chip>
            ) : null}
            <Link
              href={`/reports/modules/${encodeURIComponent(moduleId)}`}
              className="text-accent text-sm underline underline-offset-2"
            >
              {t('report')}
            </Link>
          </>
        }
      />

      <ProgressBar
        className="mb-6 max-w-md"
        value={progress}
        label={`${mod.title ?? moduleId} ${formatPercent(progress, locale)}`}
        showValue
      />

      <div className="grid gap-6 lg:grid-cols-[2fr_1fr]">
        <Card as="section" className="p-2" aria-labelledby="lessons-heading">
          <h2 id="lessons-heading" className="text-primary px-3 py-2 font-semibold">
            {t('lessons')}
          </h2>
          {lessons.length === 0 ? (
            <p className="text-muted px-3 py-4 text-sm">{t('empty')}</p>
          ) : (
            <ul className="flex flex-col">
              {lessons.map((lesson, index) => (
                <LessonRow
                  key={lesson.id ?? index}
                  moduleId={moduleId}
                  lessonId={lesson.id ?? ''}
                  title={lesson.title ?? lesson.id ?? ''}
                  state={states[index] ?? 'available'}
                  stateLabel={tState(states[index] ?? 'available')}
                  meta={
                    lesson.estimated_minutes
                      ? t('estimated', { minutes: formatMinutes(lesson.estimated_minutes, locale) })
                      : undefined
                  }
                />
              ))}
            </ul>
          )}
        </Card>

        <Card as="section" aria-labelledby="module-resources-heading">
          <h2 id="module-resources-heading" className="text-primary mb-2 font-semibold">
            {t('resources')}
          </h2>
          {resources && resources.length > 0 ? (
            <ul>
              {resources.map((resource, index) => (
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
          ) : (
            <p className="text-muted text-sm">—</p>
          )}
        </Card>
      </div>
    </>
  )
}
