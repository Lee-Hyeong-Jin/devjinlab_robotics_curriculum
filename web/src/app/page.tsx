import type { Metadata } from 'next'
import { getLocale, getTranslations } from 'next-intl/server'

import { ButtonLink } from '@/components/Button'
import { Card } from '@/components/Card'
import { Chip } from '@/components/Chip'
import { EmptyState } from '@/components/EmptyState'
import { PageHeader } from '@/components/PageHeader'
import { ProgressBar } from '@/components/ProgressBar'
import { StageProgress } from '@/components/StageProgress'
import { StatTile } from '@/components/StatTile'
import { getRoadmap, getStatus } from '@/lib/api/queries'
import type { LockState } from '@/lib/api/types'
import { average, doneCount } from '@/lib/progress'
import { formatDateTime, formatMinutes, formatPercent } from '@/lib/format'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('dashboard')
  return { title: t('title') }
}

/**
 * Dashboard — `GET /progress/status` (frontend.md §2).
 *
 * `Status` is filled in additively by the backend: P2-1 ships `open_session` and
 * `lessons`; `current`, `stages`, `week`, `streak_days` and `recent` arrive with
 * P2-2; `due_cards` after P1-2. Fields that are not there yet render as a
 * skeleton rather than blocking the screen.
 */
export default async function DashboardPage() {
  const [t, tState, locale] = await Promise.all([
    getTranslations('dashboard'),
    getTranslations('state'),
    getLocale(),
  ])
  const [status, roadmap] = await Promise.all([getStatus(), getRoadmap()])

  if (!status && !roadmap) {
    return (
      <>
        <PageHeader title={t('title')} subtitle={t('subtitle')} />
        <EmptyState title={t('title')} body={t('pending')} />
      </>
    )
  }

  const stateLabel = (state: LockState) => tState(state)
  // `stages` comes from the status payload once P2-2 lands; until then the
  // roadmap (which this app can compose from content + progress) stands in.
  const stages = status?.stages ?? roadmap?.stages ?? []
  const lessons = status?.lessons ?? []
  const courseProgress =
    lessons.length > 0
      ? doneCount(lessons.map((lesson) => lesson.state ?? 'available')) / lessons.length
      : average(stages.map((stage) => stage.progress ?? 0))
  const current = status?.current
  const week = status?.week
  const openSession = status?.open_session

  return (
    <>
      <PageHeader title={t('title')} subtitle={t('subtitle')} />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile
          label={t('courseProgress')}
          value={formatPercent(courseProgress, locale)}
          hint={
            <ProgressBar
              className="mt-2"
              value={courseProgress}
              label={`${t('courseProgress')} ${formatPercent(courseProgress, locale)}`}
            />
          }
        />
        <StatTile
          label={t('weeklyMinutes')}
          value={formatMinutes(week?.minutes, locale)}
          hint={
            week?.goal_minutes
              ? t('weeklyGoal', { goal: formatMinutes(week.goal_minutes, locale) })
              : undefined
          }
          pending={week === undefined}
          pendingLabel={t('pending')}
        />
        <StatTile
          label={t('streak')}
          value={t('streakDays', { days: status?.streak_days ?? 0 })}
          pending={status?.streak_days === undefined}
          pendingLabel={t('pending')}
        />
        <StatTile
          label={t('dueCards')}
          value={t('dueCardsValue', { count: status?.due_cards ?? 0 })}
          hint={t('dueCardsCli')}
          pending={status?.due_cards === undefined}
          pendingLabel={t('pending')}
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[2fr_1fr]">
        <div className="flex flex-col gap-6">
          <Card as="section" aria-labelledby="current-heading">
            <h2 id="current-heading" className="text-primary mb-3 font-semibold">
              {t('current')}
            </h2>
            {current ? (
              <div className="flex flex-col gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  {current.level ? <Chip tone="accent">{current.level}</Chip> : null}
                  <span className="text-primary font-medium">
                    {current.module_title ?? current.module_id}
                  </span>
                </div>
                <p className="text-muted text-sm">
                  {t('moduleLessons', {
                    done: current.lessons_done ?? 0,
                    total: current.lessons_total ?? 0,
                  })}
                </p>
                {current.next_lesson_id ? (
                  <div className="border-border-default mt-1 flex flex-wrap items-center gap-3 border-t pt-3">
                    <span className="text-muted text-xs">{t('nextLesson')}</span>
                    <span className="text-primary text-sm font-medium">
                      {current.next_lesson_title ?? current.next_lesson_id}
                    </span>
                    <ButtonLink
                      className="ml-auto"
                      href={`/modules/${current.module_id ?? ''}/${current.next_lesson_id}`}
                    >
                      {t('openLesson')}
                    </ButtonLink>
                  </div>
                ) : null}
              </div>
            ) : (
              <p className="text-muted text-sm">{t('noCurrent')}</p>
            )}
          </Card>

          {stages.length > 0 ? (
            <StageProgress
              title={t('stageProgress')}
              stages={stages}
              stateLabel={stateLabel}
              progressLabel={t('courseProgress')}
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
            {status?.recent && status.recent.length > 0 ? (
              <ul className="flex flex-col gap-3">
                {status.recent.map((entry, index) => (
                  <li key={`${entry.at ?? index}`} className="flex flex-col">
                    <span className="text-primary text-sm">{entry.text}</span>
                    <span className="text-muted text-xs">
                      {formatDateTime(entry.at, locale)}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-muted text-sm">{t('noRecent')}</p>
            )}
          </Card>
        </div>
      </div>
    </>
  )
}
