import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { ButtonLink } from '@/components/Button'
import { Card } from '@/components/Card'
import { Chip } from '@/components/Chip'
import { EmptyState } from '@/components/EmptyState'
import { PageHeader } from '@/components/PageHeader'
import { ProgressBar } from '@/components/ProgressBar'
import { StageProgress } from '@/components/StageProgress'
import { StatTile } from '@/components/StatTile'
import { getCourses, getNextLessons, getRoadmap, getStatus } from '@/lib/api/queries'
import { formatDateTime, formatMinutes, formatPercent } from '@/lib/format'
import { courseProgress, lessonLockState, type LockState } from '@/lib/progress'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('dashboard')
  return { title: t('title') }
}

/**
 * Dashboard — `GET /progress/status` plus `GET /progress/next` (frontend.md §2).
 *
 * Covers AC-WEB.3: course, stage and module progress, weekly study time, the
 * study streak, cards due today and the next-lesson recommendation.
 */
export default async function DashboardPage() {
  const [t, tState, tCourse, locale] = await Promise.all([
    getTranslations('dashboard'),
    getTranslations('state'),
    getTranslations('course'),
    getLocale(),
  ])
  const [status, stages, next, courses] = await Promise.all([
    getStatus(),
    getRoadmap(),
    getNextLessons(),
    getCourses(),
  ])

  if (!status && stages.length === 0) {
    return (
      <>
        <PageHeader title={t('title')} subtitle={t('subtitle')} />
        <EmptyState title={t('title')} body={t('unavailable')} />
      </>
    )
  }

  const lessons = status?.lessons ?? []
  const progress = courseProgress(lessons)
  // With more than one course the single course-progress tile would mix the tracks, so each
  // course gets its own row. `GET /progress/status` covers every course at once.
  const perCourse =
    courses.length > 1
      ? courses.map((course) => {
          const own = lessons.filter((row) => row.lesson.course_id === course.id)
          return { course, progress: courseProgress(own), lessonsTotal: own.length }
        })
      : []
  const week = status?.week
  const openSession = status?.open_session
  const recommended = next?.[0]
  const currentStage = stages.find((stage) =>
    stage.modules.some((module) => module.state === 'in_progress'),
  )
  const currentModule = currentStage?.modules.find((module) => module.state === 'in_progress')
  const stateLabel = (state: LockState) => tState(state)
  const lessonsLabel = (done: number, total: number) => t('moduleLessons', { done, total })

  return (
    <>
      <PageHeader title={t('title')} subtitle={t('subtitle')} />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile
          label={t('courseProgress')}
          value={formatPercent(progress, locale)}
          hint={
            <ProgressBar
              className="mt-2"
              value={progress}
              label={`${t('courseProgress')} ${formatPercent(progress, locale)}`}
            />
          }
        />
        <StatTile
          label={t('weeklyMinutes')}
          value={formatMinutes(week?.minutes, locale)}
          hint={week ? t('weeklySessions', { count: week.sessions }) : undefined}
          pending={!week}
          pendingLabel={t('pending')}
        />
        <StatTile label={t('streak')} value={t('streakDays', { days: status?.streak_days ?? 0 })} />
        <StatTile
          label={t('dueCards')}
          value={t('dueCardsValue', { count: status?.due_cards ?? 0 })}
          hint={t('dueCardsCli')}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="flex flex-col gap-6">
          <Card as="section" aria-labelledby="current-heading">
            <h2 id="current-heading" className="text-primary mb-3 font-semibold">
              {t('current')}
            </h2>
            {currentModule ? (
              <div className="flex flex-col gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  {currentStage ? <Chip tone="accent">{currentStage.levelLabel}</Chip> : null}
                  <span className="text-primary font-medium">{currentModule.title}</span>
                </div>
                <ProgressBar
                  className="max-w-sm"
                  value={currentModule.progress}
                  label={`${currentModule.title} ${t('courseProgress')}`}
                  showValue
                />
              </div>
            ) : (
              <p className="text-muted text-sm">{t('noCurrent')}</p>
            )}

            {recommended ? (
              <div className="border-border-default mt-4 flex flex-wrap items-center gap-3 border-t pt-4">
                <div className="min-w-0 flex-1">
                  <p className="text-muted text-xs">{t('nextLesson')}</p>
                  <p className="text-primary text-sm font-medium">{recommended.lesson.title}</p>
                  <p className="text-muted text-xs">{recommended.reason}</p>
                </div>
                <ButtonLink
                  href={`/modules/${recommended.lesson.module_id}/${recommended.lesson.id}`}
                >
                  {t('openLesson')}
                </ButtonLink>
              </div>
            ) : null}
          </Card>

          {perCourse.length > 0 ? (
            <Card as="section" aria-labelledby="courses-heading">
              <h2 id="courses-heading" className="text-primary mb-3 font-semibold">
                {tCourse('progressHeading')}
              </h2>
              <ul className="flex flex-col gap-4">
                {perCourse.map((row) => (
                  <li key={row.course.id} className="flex flex-col gap-1">
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <Link
                        href={`/roadmap?course=${encodeURIComponent(row.course.id)}`}
                        className="text-accent text-sm font-medium underline underline-offset-2"
                      >
                        {row.course.title}
                      </Link>
                      <span className="text-muted text-xs tabular-nums">
                        {tCourse('lessonCount', { count: row.lessonsTotal })}
                      </span>
                    </div>
                    <ProgressBar
                      value={row.progress}
                      label={`${row.course.title} ${t('courseProgress')}`}
                      showValue
                    />
                  </li>
                ))}
              </ul>
            </Card>
          ) : null}

          {stages.length > 0 ? (
            <StageProgress
              title={t('stageProgress')}
              stages={stages}
              stateLabel={stateLabel}
              progressLabel={t('courseProgress')}
              lessonsLabel={lessonsLabel}
            />
          ) : null}
        </div>

        <div className="flex flex-col gap-6">
          {openSession ? (
            <Card as="section" aria-labelledby="open-session-heading">
              <h2 id="open-session-heading" className="text-primary mb-2 font-semibold">
                {t('openSession')}
              </h2>
              <p className="text-primary font-mono text-sm">{openSession.lesson_id}</p>
              <p className="text-muted mt-1 text-xs">
                {t('openSessionSince', { at: formatDateTime(openSession.started_at, locale) })}
              </p>
            </Card>
          ) : null}

          <Card as="section" aria-labelledby="recent-heading">
            <h2 id="recent-heading" className="text-primary mb-3 font-semibold">
              {t('recent')}
            </h2>
            {(() => {
              const recent = lessons
                .filter((lesson) => lesson.completed_at || lesson.started_at)
                .sort((a, b) =>
                  (b.completed_at ?? b.started_at ?? '').localeCompare(
                    a.completed_at ?? a.started_at ?? '',
                  ),
                )
                .slice(0, 5)
              if (recent.length === 0) {
                return <p className="text-muted text-sm">{t('noRecent')}</p>
              }
              return (
                <ul className="flex flex-col gap-3">
                  {recent.map((entry) => (
                    <li key={entry.lesson.id} className="flex flex-col">
                      <span className="text-primary text-sm">{entry.lesson.title}</span>
                      <span className="text-muted text-xs">
                        {tState(lessonLockState(entry))} ·{' '}
                        {formatDateTime(entry.completed_at ?? entry.started_at, locale)}
                      </span>
                    </li>
                  ))}
                </ul>
              )
            })()}
          </Card>
        </div>
      </div>
    </>
  )
}
