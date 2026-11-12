import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { MarkdownBody } from '@/components/MarkdownBody'
import { PageHeader } from '@/components/PageHeader'
import { ProgressBar } from '@/components/ProgressBar'
import { StatTile } from '@/components/StatTile'
import { isNotFound } from '@/lib/api/errors'
import { getModuleReport } from '@/lib/api/queries'
import type { Report } from '@/lib/api/types'
import { isWeeklySummary } from '@/lib/api/types'
import { formatDate, formatPercent, formatSeconds } from '@/lib/format'
import { ratio } from '@/lib/progress'
import { renderMarkdown } from '@/lib/markdown/render'

interface Params {
  params: Promise<{ moduleId: string }>
}

async function loadReport(moduleId: string): Promise<Report> {
  try {
    return await getModuleReport(moduleId)
  } catch (error) {
    if (isNotFound(error)) notFound()
    throw error
  }
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { moduleId } = await params
  const t = await getTranslations('reports')
  return { title: t('moduleTitle', { module: moduleId }) }
}

/**
 * Per-module report — `GET /reports/modules/{module_id}` (frontend.md §2).
 *
 * Same shape as the weekly report: the API returns the Markdown `rc report module`
 * prints, which goes through the lesson pipeline, plus a structured summary that
 * drives the tiles above it.
 */
export default async function ModuleReportPage({ params }: Params) {
  const { moduleId } = await params
  const [t, locale, report] = await Promise.all([
    getTranslations('reports'),
    getLocale(),
    loadReport(moduleId),
  ])

  const summary = isWeeklySummary(report.summary) ? null : report.summary
  const body = renderMarkdown(report.markdown)
  const done = ratio(summary?.done_count ?? 0, summary?.lesson_count ?? 0)

  return (
    <>
      <PageHeader
        title={summary?.module_title ?? moduleId}
        subtitle={t('moduleSubtitle')}
        eyebrow={
          <Link href="/reports" className="text-accent underline underline-offset-2">
            ← {t('title')}
          </Link>
        }
        actions={
          <span className="text-muted text-sm">
            {t('generatedAt', { at: formatDate(report.generated_at, locale) })}
          </span>
        }
      />

      {summary ? (
        <>
          <div className="mb-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <StatTile
              label={t('course')}
              value={<span className="text-base">{summary.course_title}</span>}
            />
            <StatTile
              label={t('completedLessons')}
              value={t('ofLessons', { done: summary.done_count, total: summary.lesson_count })}
            />
            <StatTile label={t('studyTime')} value={formatSeconds(summary.total_seconds, locale)} />
          </div>
          <ProgressBar
            className="mb-6 max-w-md"
            value={done}
            label={`${summary.module_title} ${formatPercent(done, locale)}`}
            showValue
          />
        </>
      ) : null}

      <div className="flex flex-wrap gap-4">
        <Link
          href={`/modules/${encodeURIComponent(moduleId)}`}
          className="text-accent mb-4 text-sm underline underline-offset-2"
        >
          {t('backToModule')}
        </Link>
      </div>

      <Card as="article" aria-labelledby="module-report-body">
        <h2 id="module-report-body" className="sr-only">
          {t('body')}
        </h2>
        <MarkdownBody empty={<p className="text-muted text-sm">{t('empty')}</p>}>
          {body.content}
        </MarkdownBody>
      </Card>
    </>
  )
}
