import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import type { ResourceKind, ResourceRef } from '@/lib/api/types'
import { hostnameOf } from '@/lib/format'
import { RESOURCE_KIND_TONE } from '@/lib/resource-kind'

import { Chip } from './Chip'
import { DataTable, type Column } from './DataTable'
import { EmptyState } from './EmptyState'

export interface ResourceTableProps {
  /** The rows of the page being shown, already filtered. */
  resources: readonly ResourceRef[]
  /** Lesson id -> title, for the "lessons" column; an id without one is shown as is. */
  lessonTitles?: Record<string, string>
}

/**
 * One page of the resource library (frontend.md §2, AC-WEB.5). Rendered on the server: the
 * filter and the page are in the URL, so the browser receives the rows it shows and no copy of
 * the whole catalogue (#57).
 */
export async function ResourceTable({ resources, lessonTitles = {} }: ResourceTableProps) {
  const [t, tKind] = await Promise.all([getTranslations('resources'), getTranslations('kind')])

  const columns: ReadonlyArray<Column<ResourceRef>> = [
    {
      key: 'title',
      header: t('colTitle'),
      cell: (row) =>
        row.url ? (
          <a
            href={row.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-accent font-medium underline underline-offset-2"
          >
            {row.title}
            <span className="sr-only"> ({t('externalLink')})</span>
            {hostnameOf(row.url) ? (
              <span className="text-muted ml-2 text-xs font-normal">{hostnameOf(row.url)}</span>
            ) : null}
          </a>
        ) : (
          <span className="font-medium">{row.title}</span>
        ),
    },
    {
      key: 'kind',
      header: t('colKind'),
      cell: (row) =>
        row.kind ? (
          <Chip tone={RESOURCE_KIND_TONE[row.kind]}>{tKind(row.kind as ResourceKind)}</Chip>
        ) : null,
    },
    {
      key: 'note',
      header: t('colNote'),
      cell: (row) => <span className="text-muted">{row.note ?? '—'}</span>,
    },
    {
      key: 'lessons',
      header: t('colLessons'),
      cell: (row) => (
        <span className="text-muted flex flex-col gap-0.5 text-xs">
          {(row.lesson_ids ?? []).map((id) => (
            <Link
              key={id}
              href={`/lessons/${encodeURIComponent(id)}`}
              className={`hover:text-accent underline underline-offset-2 ${lessonTitles[id] ? '' : 'font-mono'}`}
            >
              {lessonTitles[id] ?? id}
            </Link>
          ))}
        </span>
      ),
      hideOnMobile: true,
    },
  ]

  return (
    <DataTable
      caption={t('title')}
      columns={columns}
      rows={resources}
      rowKey={(row, index) => `${row.title}-${index}`}
      empty={<EmptyState title={t('empty')} />}
    />
  )
}
