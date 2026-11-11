import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { DataTable, type Column } from '@/components/DataTable'
import { PageHeader } from '@/components/PageHeader'
import { apiGetOrNull } from '@/lib/api/client'
import type { AuditEntry } from '@/lib/api/types'
import { formatDateTime } from '@/lib/format'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('admin')
  return { title: t('auditTitle') }
}

interface Props {
  searchParams: Promise<{ cursor?: string }>
}

/** Admin audit log — `GET /admin/audit`, cursor paginated. */
export default async function AdminAuditPage({ searchParams }: Props) {
  const [t, locale, params] = await Promise.all([
    getTranslations('admin'),
    getLocale(),
    searchParams,
  ])
  const page = await apiGetOrNull('/api/v1/admin/audit', {
    query: { cursor: params.cursor, limit: 100 },
  })

  const columns: ReadonlyArray<Column<AuditEntry>> = [
    {
      key: 'at',
      header: t('colAt'),
      cell: (row) => <span className="whitespace-nowrap">{formatDateTime(row.at, locale)}</span>,
    },
    {
      key: 'action',
      header: t('colAction'),
      cell: (row) => <code className="font-mono text-xs">{row.action}</code>,
    },
    {
      key: 'actor',
      header: t('colActor'),
      cell: (row) => (row.actor_user_id === null ? '—' : `#${row.actor_user_id}`),
      hideOnMobile: true,
    },
    {
      key: 'target',
      header: t('colTarget'),
      cell: (row) =>
        row.target_type ? (
          <span className="text-muted font-mono text-xs">
            {row.target_type}
            {row.target_id ? `:${row.target_id}` : ''}
          </span>
        ) : (
          '—'
        ),
      hideOnMobile: true,
    },
    {
      key: 'ip',
      header: t('colIp'),
      cell: (row) => row.actor_ip ?? '—',
      hideOnMobile: true,
    },
  ]

  return (
    <>
      <PageHeader title={t('auditTitle')} subtitle={t('auditSubtitle')} />
      <Card className="p-0">
        <DataTable
          caption={t('auditTableCaption')}
          columns={columns}
          rows={page?.items ?? []}
          rowKey={(row) => String(row.id)}
          empty={<p className="text-muted p-5 text-sm">{t('noAudit')}</p>}
        />
      </Card>
      {page?.next_cursor ? (
        <p className="mt-4">
          <Link
            href={`/admin/audit?cursor=${encodeURIComponent(page.next_cursor)}`}
            className="text-accent text-sm underline underline-offset-2"
          >
            {t('more')}
          </Link>
        </p>
      ) : null}
    </>
  )
}
