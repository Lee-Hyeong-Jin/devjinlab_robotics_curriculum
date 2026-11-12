import type { Metadata } from 'next'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { DataTable, type Column } from '@/components/DataTable'
import { EmptyState } from '@/components/EmptyState'
import { ModuleCard } from '@/components/ModuleCard'
import { PageHeader } from '@/components/PageHeader'
import { ProgressBar } from '@/components/ProgressBar'
import { StatusDot } from '@/components/StatusDot'
import { getRoadmap } from '@/lib/api/queries'
import { formatPercent } from '@/lib/format'
import type { LockState } from '@/lib/progress'
import { doneCount } from '@/lib/progress'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('roadmap')
  return { title: t('title') }
}

interface TableRow {
  moduleId: string
  title: string
  level: string
  state: LockState
  progress: number
}

/** Roadmap — stage → module cards plus a text alternative table (AC-WEB.3, AC-A11Y.3). */
export default async function RoadmapPage() {
  const [t, tState, locale] = await Promise.all([
    getTranslations('roadmap'),
    getTranslations('state'),
    getLocale(),
  ])
  const stages = await getRoadmap()

  if (stages.length === 0) {
    return (
      <>
        <PageHeader title={t('title')} subtitle={t('subtitle')} />
        <EmptyState title={t('empty')} />
      </>
    )
  }

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
      <PageHeader title={t('title')} subtitle={t('subtitle')} />

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
            <ul className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {stage.modules.map((module) => (
                <li key={module.id}>
                  <ModuleCard
                    id={module.id}
                    title={module.title}
                    state={module.state}
                    progress={module.progress}
                    lessonsTotal={module.lessons.length}
                    lessonsDone={doneCount(module.lessons.map((lesson) => lesson.state))}
                    level={stage.levelLabel}
                    stateLabel={tState(module.state)}
                    lessonsLabel={t('lessonCount', { count: module.lessons.length })}
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
