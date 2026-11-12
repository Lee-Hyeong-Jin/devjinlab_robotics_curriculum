import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { EmptyState } from '@/components/EmptyState'
import { MarkdownBody } from '@/components/MarkdownBody'
import { PageHeader } from '@/components/PageHeader'
import { StatTile } from '@/components/StatTile'
import { getCourse, getWeeklyReport } from '@/lib/api/queries'
import { isWeeklySummary } from '@/lib/api/types'
import { formatDate, formatSeconds } from '@/lib/format'
import { renderMarkdown } from '@/lib/markdown/render'

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
export default async function ReportsPage() {
  const [t, locale] = await Promise.all([getTranslations('reports'), getLocale()])
  const [report, course] = await Promise.all([getWeeklyReport(), getCourse()])
  const modules = (course?.stages ?? []).flatMap((stage) => stage.modules ?? [])

  if (!report) {
    return (
      <>
        <PageHeader title={t('title')} subtitle={t('subtitle')} />
        <EmptyState title={t('unavailable')} />
      </>
    )
  }

  const body = renderMarkdown(report.markdown)
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

      {isWeeklySummary(summary) ? (
        <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
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
                  className="bg-subtle text-primary border-border-default hover:bg-surface inline-flex rounded-lg border px-3 py-1.5 text-sm"
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
