import type { Metadata } from 'next'
import Link from 'next/link'
import { goalProgress, lessonsOnPath, roadmapHref, selectGoal } from '@/lib/goal-path'
import { cx } from '@/lib/cx'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { DataTable, type Column } from '@/components/DataTable'
import { EmptyState } from '@/components/EmptyState'
import { ModuleCard } from '@/components/ModuleCard'
import { PageHeader } from '@/components/PageHeader'
import { ProgressBar } from '@/components/ProgressBar'
import { StatusDot } from '@/components/StatusDot'
import { CourseTabs } from '@/components/CourseTabs'
import { JsonLd } from '@/components/JsonLd'
import { getCourse, getCourses, getRoadmap } from '@/lib/api/queries'
import { defaultCourseId } from '@/lib/api/config'
import { selectedCourseId } from '@/lib/courses'
import { composeTitle, metaDescription } from '@/lib/seo'
import { localizedPageSeo } from '@/lib/seo-server'
import { breadcrumbs, courseSchema } from '@/lib/structured-data'
import { formatMinutes, formatPercent } from '@/lib/format'
import type { LockState } from '@/lib/progress'
import { doneCount } from '@/lib/progress'

export async function generateMetadata({ searchParams }: Props): Promise<Metadata> {
  const [t, tSeo, params, courses] = await Promise.all([
    getTranslations('roadmap'),
    getTranslations('seo'),
    searchParams,
    getCourses(),
  ])
  const courseId = selectedCourseId(courses, params.course, defaultCourseId())
  const course = courses.find((candidate) => candidate.id === courseId)
  const isDefault = courseId === defaultCourseId()
  return localizedPageSeo({
    // The default course lives at the bare `/roadmap`, so the two addresses do not compete
    // for the same content.
    path: isDefault ? '/roadmap' : `/roadmap?course=${encodeURIComponent(courseId)}`,
    // Names the course *and* what the page is: the course title alone would not say that
    // this is its roadmap, and the bare word "roadmap" says nothing about which course.
    title: composeTitle(
      tSeo('roadmapName', { course: course?.title ?? t('title') }),
      tSeo('roadmapLabel'),
      tSeo('brand'),
    ),
    absoluteTitle: true,
    description: metaDescription(course?.summary) || t('subtitle'),
    publishable: true,
  })
}

interface TableRow {
  moduleId: string
  title: string
  level: string
  state: LockState
  progress: number
}

interface Props {
  searchParams: Promise<{ course?: string; goal?: string }>
}

/** Roadmap — stage → module cards plus a text alternative table (AC-WEB.3, AC-A11Y.3). */
export default async function RoadmapPage({ searchParams }: Props) {
  const [t, tState, locale, params, courses] = await Promise.all([
    getTranslations('roadmap'),
    getTranslations('state'),
    getLocale(),
    searchParams,
    getCourses(),
  ])
  const courseId = selectedCourseId(courses, params.course, defaultCourseId())
  const stages = await getRoadmap(courseId)
  const course = await getCourse(courseId)
  const coursePath =
    courseId === defaultCourseId() ? '/roadmap' : `/roadmap?course=${encodeURIComponent(courseId)}`

  if (stages.length === 0) {
    return (
      <>
        <PageHeader title={t('title')} subtitle={t('subtitle')} />
        <CourseTabs courses={courses} selected={courseId} basePath="/roadmap" />
        <EmptyState title={t('empty')} />
      </>
    )
  }

  // A goal narrows the roadmap to the lessons it needs (`?goal=navigation`, #52).
  const goals = course?.goals ?? []
  const goal = selectGoal(goals, params.goal)
  const states = Object.fromEntries(
    stages.flatMap((stage) =>
      stage.modules.flatMap((module) => module.lessons.map((lesson) => [lesson.id, lesson.state])),
    ),
  )
  const onGoal = goal ? goalProgress(goal, states) : null

  const rows: TableRow[] = stages.flatMap((stage) =>
    stage.modules.map((module) => ({
      moduleId: module.id,
      title: module.title,
      level: stage.levelLabel,
      state: module.state,
      progress: module.progress,
    })),
  )

  const columns: ReadonlyArray<Column<TableRow>> = [
    { key: 'module', header: t('colModule'), cell: (row) => row.title },
    { key: 'stage', header: t('colStage'), cell: (row) => row.level, hideOnMobile: true },
    {
      key: 'state',
      header: t('colState'),
      cell: (row) => <StatusDot state={row.state} label={tState(row.state)} />,
    },
    {
      key: 'progress',
      header: t('colProgress'),
      cell: (row) => <span className="tabular-nums">{formatPercent(row.progress, locale)}</span>,
    },
  ]

  return (
    <>
      {course ? (
        <JsonLd
          data={[courseSchema(course, coursePath), breadcrumbs([[course.title, coursePath]])]}
        />
      ) : null}
      <PageHeader
        title={course ? t('courseTitle', { course: course.title }) : t('title')}
        subtitle={t('subtitle')}
      />
      <CourseTabs courses={courses} selected={courseId} basePath="/roadmap" />

      {goals.length > 0 ? (
        <Card as="section" className="mb-8" aria-labelledby="goal-heading">
          <h2 id="goal-heading" className="text-primary font-semibold">
            {t('goalHeading')}
          </h2>
          <p className="text-muted mt-1 mb-3 max-w-3xl text-sm">{t('goalHint')}</p>
          <nav aria-label={t('goalHeading')}>
            <ul className="flex flex-wrap gap-2">
              {[{ id: null, title: t('goalAll') }, ...goals].map((entry) => {
                const current = (entry.id ?? null) === (goal?.id ?? null)
                return (
                  <li key={entry.id ?? 'all'}>
                    <Link
                      href={roadmapHref(courseId, defaultCourseId(), entry.id)}
                      aria-current={current ? 'page' : undefined}
                      className={cx(
                        'inline-flex min-h-11 items-center rounded-full border px-3 py-1 text-sm sm:min-h-9',
                        current
                          ? 'bg-accent-light border-border-accent text-accent font-medium'
                          : 'bg-surface border-border-default text-primary hover:bg-subtle',
                      )}
                    >
                      {entry.title}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>

          {goal && onGoal ? (
            <div className="border-border-default mt-4 border-t pt-4">
              <p className="text-primary text-sm font-medium">{goal.title}</p>
              <p className="text-muted mt-1 max-w-3xl text-sm">{goal.summary}</p>
              <p className="text-primary mt-2 text-sm" role="status">
                {t('goalProgress', {
                  done: onGoal.done,
                  total: onGoal.total,
                  remaining: formatMinutes(onGoal.remainingMinutes, locale),
                  time: formatMinutes(goal.estimated_minutes, locale),
                })}
              </p>
              <ol className="mt-3 flex flex-col gap-1">
                {goal.lessons.map((lesson, index) => {
                  const state = states[lesson.id] ?? 'available'
                  return (
                    <li key={lesson.id} className="flex flex-wrap items-baseline gap-x-3 text-sm">
                      <span className="text-muted w-6 shrink-0 text-right tabular-nums">
                        {index + 1}.
                      </span>
                      <Link
                        href={`/modules/${encodeURIComponent(lesson.module_id)}/${encodeURIComponent(lesson.id)}`}
                        className="text-accent underline underline-offset-2"
                      >
                        {lesson.title}
                      </Link>
                      <StatusDot state={state} label={tState(state)} />
                      <span className="text-muted text-xs">
                        {formatMinutes(lesson.estimated_minutes, locale)}
                      </span>
                    </li>
                  )
                })}
              </ol>
            </div>
          ) : null}
        </Card>
      ) : null}

      <div className="flex flex-col gap-8">
        {stages.map((stage, index) => (
          <section key={stage.level || index} aria-labelledby={`stage-${index}`}>
            <div className="mb-3 flex flex-wrap items-center gap-4">
              <h2 id={`stage-${index}`} className="text-primary text-lg font-bold">
                {t('stage', { level: stage.levelLabel })}
              </h2>
              <span className="text-muted text-sm">
                {t('stageLessons', { done: stage.lessonsDone, total: stage.lessonsTotal })}
              </span>
              <ProgressBar
                className="max-w-xs flex-1"
                value={stage.progress}
                label={`${stage.levelLabel} ${t('colProgress')}`}
                showValue
              />
            </div>
            <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {stage.modules.map((module) => (
                <li
                  key={module.id}
                  // The modules a chosen goal needs are outlined. The others are not dimmed:
                  // fading them took their text below the contrast minimum, and they stay
                  // perfectly usable — the line above each card says which is which.
                  className={
                    goal && lessonsOnPath(goal, module.id) > 0
                      ? 'ring-border-accent rounded-[var(--radius-card)] ring-2 ring-offset-2 ring-offset-transparent'
                      : undefined
                  }
                >
                  {goal ? (
                    <p className="text-muted mb-1 text-xs">
                      {lessonsOnPath(goal, module.id) === 0
                        ? t('goalModuleOff')
                        : t('goalModuleOn', {
                            count: lessonsOnPath(goal, module.id),
                            total: module.lessonsTotal,
                          })}
                    </p>
                  ) : null}
                  <ModuleCard
                    id={module.id}
                    title={module.title}
                    state={module.state}
                    progress={module.progress}
                    lessonsTotal={module.lessonsTotal}
                    lessonsDone={doneCount(module.lessons.map((lesson) => lesson.state))}
                    level={stage.levelLabel}
                    stateLabel={tState(module.state)}
                    lessonsLabel={t('lessonCount', { count: module.lessonsTotal })}
                    progressLabel={t('colProgress')}
                  />
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>

      <Card as="section" className="mt-8 p-0" aria-labelledby="roadmap-table-heading">
        <h2 id="roadmap-table-heading" className="sr-only">
          {t('tableCaption')}
        </h2>
        <DataTable
          caption={t('tableCaption')}
          captionVisible
          columns={columns}
          rows={rows}
          rowKey={(row, index) => row.moduleId || String(index)}
        />
      </Card>
    </>
  )
}
