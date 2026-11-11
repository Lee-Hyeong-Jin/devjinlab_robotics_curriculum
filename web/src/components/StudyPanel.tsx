import { getLocale, getTranslations } from 'next-intl/server'

import { logMinutes, markDone, startTimer, stopTimer } from '@/lib/actions/progress'
import type { LessonProgress, StudySession } from '@/lib/api/types'
import { formatDateTime, formatSeconds } from '@/lib/format'

import { Card } from './Card'
import { Chip } from './Chip'
import { ActionForm } from './form/ActionForm'
import { RowAction } from './form/RowAction'

export interface StudyPanelProps {
  moduleId: string
  lessonId: string
  progress: LessonProgress | null
  /** The running timer, if any — it may belong to another lesson. */
  openSession: StudySession | null
}

/**
 * The lesson screen's write actions: the study timer, manual time entry and
 * completion (frontend.md §2 "레슨 화면의 쓰기 동작", AC-WEB.1).
 *
 * Each action is its own form so one failing does not clear the others.
 */
export async function StudyPanel({ moduleId, lessonId, progress, openSession }: StudyPanelProps) {
  const [t, locale] = await Promise.all([getTranslations('study'), getLocale()])
  const ids = { lessonId, moduleId }
  const runningHere = openSession?.lesson_id === lessonId
  const done = progress?.status === 'done'

  return (
    <Card as="section" aria-labelledby="study-panel-heading">
      <h2 id="study-panel-heading" className="text-primary mb-3 font-semibold">
        {t('title')}
      </h2>

      {done ? <Chip tone="success">{t('alreadyDone')}</Chip> : null}

      <div className="mt-3 flex flex-col gap-4">
        <div>
          <h3 className="text-muted mb-2 text-xs font-semibold tracking-wide uppercase">
            {t('timer')}
          </h3>
          {openSession ? (
            <div className="flex flex-col gap-2">
              <p className="text-muted text-xs">
                {runningHere
                  ? t('runningSince', { at: formatDateTime(openSession.started_at, locale) })
                  : `${openSession.lesson_id} — ${t('running')}`}
              </p>
              <RowAction
                action={stopTimer}
                hidden={{ ...ids }}
                label={t('stop')}
                pendingLabel={t('stopping')}
              />
            </div>
          ) : (
            <RowAction
              action={startTimer}
              hidden={{ ...ids }}
              label={t('start')}
              pendingLabel={t('starting')}
            />
          )}
        </div>

        <div className="border-border-default border-t pt-4">
          <h3 className="text-muted mb-2 text-xs font-semibold tracking-wide uppercase">
            {t('logTitle')}
          </h3>
          <ActionForm
            action={logMinutes}
            hidden={{ ...ids }}
            submitLabel={t('log')}
            pendingLabel={t('logging')}
            fields={[
              { name: 'minutes', label: t('minutes'), kind: 'number', min: 1, max: 1440 },
              { name: 'note', label: t('note'), hint: t('noteHint') },
            ]}
          />
        </div>

        <div className="border-border-default border-t pt-4">
          <h3 className="text-muted mb-2 text-xs font-semibold tracking-wide uppercase">
            {t('doneTitle')}
          </h3>
          <ActionForm
            action={markDone}
            hidden={{ ...ids }}
            submitLabel={t('markDone')}
            pendingLabel={t('markingDone')}
            fields={[
              {
                name: 'understanding',
                label: t('understanding'),
                kind: 'select',
                defaultValue: String(progress?.understanding ?? 3),
                options: ['1', '2', '3', '4', '5'].map((value) => ({ value, label: value })),
              },
              {
                name: 'note',
                label: t('note'),
                defaultValue: progress?.note ?? '',
                hint: t('noteHint'),
              },
            ]}
          />
        </div>

        {progress ? (
          <p className="text-muted border-border-default border-t pt-3 text-xs">
            {formatSeconds(progress.total_seconds, locale)}
          </p>
        ) : null}
      </div>
    </Card>
  )
}
