'use client'

import { useTranslations } from 'next-intl'
import { useMemo, useState } from 'react'

import type { ResourceKind, ResourceRef } from '@/lib/api/types'
import { hostnameOf } from '@/lib/format'

import { Chip, type ChipTone } from './Chip'
import { DataTable, type Column } from './DataTable'
import { EmptyState } from './EmptyState'
import { FilterBar, type FilterOption } from './FilterBar'
import { SearchInput } from './SearchInput'

const KIND_TONE: Record<ResourceKind, ChipTone> = {
  book: 'accent',
  course: 'accent',
  video: 'warning',
  article: 'neutral',
  other: 'neutral',
}

const ALL = 'all'

/**
 * Resource table with a client-side kind filter and search (frontend.md §2,
 * AC-WEB.5). The list is fetched on the server; only the filtering is interactive.
 */
export function ResourceExplorer({ resources }: { resources: ResourceRef[] }) {
  const t = useTranslations('resources')
  const tKind = useTranslations('kind')
  const [kind, setKind] = useState<string>(ALL)
  const [query, setQuery] = useState('')

  const kindOptions = useMemo<FilterOption[]>(() => {
    const counts = new Map<string, number>()
    for (const resource of resources) {
      const key = resource.kind ?? 'other'
      counts.set(key, (counts.get(key) ?? 0) + 1)
    }
    return [
      { value: ALL, label: t('filterAll'), count: resources.length },
      ...[...counts.entries()]
        .sort((a, b) => b[1] - a[1])
        .map(([value, count]) => ({ value, label: tKind(value as ResourceKind), count })),
    ]
  }, [resources, t, tKind])

  const rows = useMemo(() => {
    const needle = query.trim().toLowerCase()
    return resources.filter((resource) => {
      if (kind !== ALL && (resource.kind ?? 'other') !== kind) return false
      if (needle === '') return true
      const haystack = `${resource.title} ${resource.note ?? ''} ${resource.url ?? ''}`
      return haystack.toLowerCase().includes(needle)
    })
  }, [resources, kind, query])

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
      cell: (row) => (row.kind ? <Chip tone={KIND_TONE[row.kind]}>{tKind(row.kind)}</Chip> : null),
    },
    {
      key: 'note',
      header: t('colNote'),
      cell: (row) => <span className="text-muted">{row.note ?? '—'}</span>,
      hideOnMobile: true,
    },
    {
      key: 'lessons',
      header: t('colLessons'),
      cell: (row) => (
        <span className="text-muted font-mono text-xs">{(row.lesson_ids ?? []).join(', ')}</span>
      ),
      hideOnMobile: true,
    },
  ]

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-end gap-6">
        <SearchInput
          label={t('search')}
          placeholder={t('searchPlaceholder')}
          value={query}
          onChange={setQuery}
        />
        <FilterBar label={t('filterKind')} options={kindOptions} value={kind} onChange={setKind} />
      </div>
      <p className="text-muted text-sm" role="status">
        {t('count', { count: rows.length })}
      </p>
      <DataTable
        caption={t('title')}
        columns={columns}
        rows={rows}
        rowKey={(row, index) => `${row.title}-${index}`}
        empty={<EmptyState title={t('empty')} />}
      />
    </div>
  )
}
