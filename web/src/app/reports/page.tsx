import type { Metadata } from 'next'
import Link from 'next/link'
import { signInIfRequired } from '@/lib/auth'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { EmptyState } from '@/components/EmptyState'
import { MarkdownBody } from '@/components/MarkdownBody'
import { PageHeader } from '@/components/PageHeader'
import { StatTile } from '@/components/StatTile'
import { getCourse, getWeeklyReport } from '@/lib/api/queries'
import { isWeeklySummary } from '@/lib/api/types'
import { formatDate, formatSeconds } from '@/lib/format'
import { currentIsoWeek, isIsoWeek, shiftIsoWeek } from '@/lib/iso-week'
import { serviceTimeZone } from '@/lib/timezone'
import { webCliHints } from '@/lib/markdown/cli-hints-server'
import { renderMarkdown } from '@/lib/markdown/render'

interface Props {
  searchParams: Promise<{ week?: string }>
}

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('reports')
  return { title: t('title') }
}

/**
 * Weekly report — `GET /reports/weekly` (frontend.md §2).
 *
 * The API returns the same Markdown as `rc report weekly`, so the body goes
 * through the lesson pipeline and the summary drives the stat tiles above it.
 */
export default async function ReportsPage({ searchParams }: Props) {
  const [t, locale, params] = await Promise.all([
    getTranslations('reports'),
    getLocale(),
    searchParams,
  ])
  // `?week=2026-W47` shows an earlier week. Anything that is not a real week, or a week that
  // has not begun, falls back to the current one.
  const thisWeek = currentIsoWeek(serviceTimeZone())
  const asked = isIsoWeek(params.week) && params.week < thisWeek ? params.week : undefined
  const week = asked ?? thisWeek
  const previous = shiftIsoWeek(week, -1)
  const next = asked ? shiftIsoWeek(week, 1) : null
  const [report, course] = await Promise.all([getWeeklyReport(asked), getCourse()])
  const modules = (course?.stages ?? []).flatMap((stage) => stage.modules ?? [])

  if (!report) {
    await signInIfRequired('/reports')
    return (
      <>
        <PageHeader title={t('title')} subtitle={t('subtitle')} />
        <EmptyState title={t('unavailable')} />
      </>
    )
  }

  // The report is the CLI's own text; its `rc start …` hints become links here.
  const body = renderMarkdown(await webCliHints(report.markdown))
  const summary = report.summary

  return (
    <>
      <PageHeader
        title={t('title')}
        subtitle={t('subtitle')}
        actions={
          <span className="text-muted text-sm">
            {t('generatedAt', { at: formatDate(report.generated_at, locale) })}
          </span>
        }
      />

      <nav aria-label={t('weekNav')} className="mb-4 flex flex-wrap items-center gap-3 text-sm">
        {previous ? (
          <Link
            href={`/reports?week=${previous}`}
            className="text-accent underline underline-offset-2"
          >
            ← {t('previousWeek')}
          </Link>
        ) : null}
        <span className="text-primary font-medium tabular-nums">{week}</span>
        {next ? (
          <Link
            href={next >= thisWeek ? '/reports' : `/reports?week=${next}`}
            className="text-accent underline underline-offset-2"
          >
            {t('nextWeek')} →
          </Link>
        ) : (
          <span className="text-muted">{t('thisWeek')}</span>
        )}
      </nav>

      {isWeeklySummary(summary) ? (
        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatTile
            label={t('period')}
            value={
              <span className="text-base">
                {formatDate(summary.start, locale)} – {formatDate(summary.end, locale)}
              </span>
            }
          />
          <StatTile label={t('studyTime')} value={formatSeconds(summary.total_seconds, locale)} />
          <StatTile
            label={t('sessions')}
            value={t('sessionCount', { count: summary.session_count })}
          />
          <StatTile label={t('activeDays')} value={t('dayCount', { count: summary.active_days })} />
        </div>
      ) : null}

      <Card as="article" aria-labelledby="report-body">
        <h2 id="report-body" className="sr-only">
          {t('body')}
        </h2>
        <MarkdownBody empty={<p className="text-muted text-sm">{t('empty')}</p>}>
          {body.content}
        </MarkdownBody>
      </Card>

      <Card as="section" className="mt-6" aria-labelledby="module-reports">
        <h2 id="module-reports" className="text-primary font-semibold">
          {t('moduleReports')}
        </h2>
        <p className="text-muted mt-1 mb-3 text-sm">{t('moduleReportsHint')}</p>
        {modules.length === 0 ? (
          <p className="text-muted text-sm">{t('noModules')}</p>
        ) : (
          <ul className="flex flex-wrap gap-2">
            {modules.map((mod) => (
              <li key={mod.id}>
                <Link
                  href={`/reports/modules/${encodeURIComponent(mod.id)}`}
                  className="bg-subtle text-primary border-border-default hover:bg-surface inline-flex min-h-11 items-center rounded-lg border px-3 py-1.5 text-sm"
                >
                  {mod.title ?? mod.id}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </>
  )
}
