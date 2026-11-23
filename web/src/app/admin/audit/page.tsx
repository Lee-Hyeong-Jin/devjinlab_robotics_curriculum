import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { Button, ButtonLink } from '@/components/Button'
import { Card } from '@/components/Card'
import { DataTable, type Column } from '@/components/DataTable'
import { FilterInput } from '@/components/form/FilterControls'
import { PageHeader } from '@/components/PageHeader'
import { dayToInstant, param, positiveInt, withQuery } from '@/lib/admin-query'
import { apiGetOrNull } from '@/lib/api/client'
import type { AuditEntry } from '@/lib/api/types'
import { formatDateTime } from '@/lib/format'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('admin')
  return { title: t('auditTitle') }
}

interface Props {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}

/** `key=value; key=value` for the detail column; long values wrap, nothing is hidden. */
function detailText(detail: AuditEntry['detail']): string {
  return Object.entries(detail)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => `${key}=${typeof value === 'object' ? JSON.stringify(value) : value}`)
    .join('; ')
}

/**
 * Admin audit log — `GET /admin/audit` with filters, cursor paging and a CSV export (P3-1).
 *
 * The date inputs are whole days in the service's time zone (KST by default); `to` includes
 * the day picked.
 */
export default async function AdminAuditPage({ searchParams }: Props) {
  const [t, locale, params] = await Promise.all([
    getTranslations('admin'),
    getLocale(),
    searchParams,
  ])
  const action = param(params.action)
  const actor = positiveInt(param(params.actor_user_id))
  const targetType = param(params.target_type)
  const targetId = param(params.target_id)
  const from = param(params.from)
  const to = param(params.to)
  const since = dayToInstant(from)
  const until = dayToInstant(to, true)

  // What the page shows in the URL (days) and what the API is asked (instants).
  const shown = {
    action,
    actor_user_id: actor === undefined ? undefined : String(actor),
    target_type: targetType,
    target_id: targetId,
    from: since ? from : undefined,
    to: until ? to : undefined,
  }
  const apiFilters = {
    action,
    actor_user_id: shown.actor_user_id,
    target_type: targetType,
    target_id: targetId,
    since,
    until,
  }
  const filtered = Object.values(shown).some((value) => value !== undefined)
  // A value that cannot be a filter is dropped, and the reader is told: silently showing the
  // whole log for "actor = abc" looks like a result for that filter (QA B-33).
  const ignored = [
    param(params.actor_user_id) && actor === undefined ? t('filterActor') : null,
    from && !since ? t('filterSince') : null,
    to && !until ? t('filterUntil') : null,
  ].filter((label): label is string => label !== null)

  const page = await apiGetOrNull('/api/v1/admin/audit', {
    query: { ...apiFilters, actor_user_id: actor, cursor: param(params.cursor), limit: 100 },
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
      cell: (row) =>
        row.actor_user_id === null ? (
          <span className="text-muted">{t('system')}</span>
        ) : (
          <Link
            href={`/admin/users/${row.actor_user_id}`}
            className="text-accent underline underline-offset-2"
          >
            {row.actor_email ?? `#${row.actor_user_id}`}
          </Link>
        ),
    },
    {
      key: 'target',
      header: t('colTarget'),
      cell: (row) =>
        row.target_type === 'user' && row.target_id ? (
          <Link
            href={`/admin/users/${encodeURIComponent(row.target_id)}`}
            className="text-accent font-mono text-xs underline underline-offset-2"
          >
            user:{row.target_id}
          </Link>
        ) : row.target_type ? (
          <span className="text-muted font-mono text-xs">
            {row.target_type}
            {row.target_id ? `:${row.target_id}` : ''}
          </span>
        ) : (
          '—'
        ),
    },
    {
      key: 'detail',
      header: t('colDetail'),
      cell: (row) => (
        <span className="text-muted font-mono text-xs">{detailText(row.detail) || '—'}</span>
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
      {ignored.length > 0 ? (
        <p role="alert" className="text-warning mb-3 text-sm">
          {t('filterIgnored', { fields: ignored.join(', ') })}
        </p>
      ) : null}

      <form
        method="get"
        role="search"
        aria-label={t('filtersLabel')}
        className="mb-4 grid grid-cols-1 items-end gap-3 sm:grid-cols-2 lg:grid-cols-[minmax(0,2fr)_repeat(3,minmax(0,1fr))_auto]"
      >
        <FilterInput
          label={t('filterAction')}
          name="action"
          defaultValue={action ?? ''}
          placeholder={t('filterActionPlaceholder')}
          maxLength={100}
          autoComplete="off"
        />
        <FilterInput
          label={t('filterActor')}
          name="actor_user_id"
          inputMode="numeric"
          pattern="[0-9]*"
          defaultValue={shown.actor_user_id ?? ''}
        />
        <FilterInput
          label={t('filterSince')}
          name="from"
          type="date"
          defaultValue={shown.from ?? ''}
        />
        <FilterInput label={t('filterUntil')} name="to" type="date" defaultValue={shown.to ?? ''} />
        {/* A target filter arrives by link from a user's page; keep it across a new search. */}
        {targetType ? <input type="hidden" name="target_type" value={targetType} /> : null}
        {targetId ? <input type="hidden" name="target_id" value={targetId} /> : null}
        <div className="flex gap-2">
          <Button type="submit">{t('apply')}</Button>
          {filtered ? (
            <ButtonLink href="/admin/audit" kind="secondary">
              {t('reset')}
            </ButtonLink>
          ) : null}
        </div>
      </form>

      <p className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
        {/* A plain anchor, not a client-side link: the response is a file download. */}
        <a
          href={withQuery('/admin/audit/export', apiFilters)}
          className="text-accent font-medium underline underline-offset-2"
        >
          {t('exportCsv')}
        </a>
        <span className="text-muted">{t('exportHint')}</span>
      </p>

      <Card className="p-0 sm:p-0">
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
            href={withQuery('/admin/audit', { ...shown, cursor: page.next_cursor })}
            className="text-accent text-sm underline underline-offset-2"
          >
            {t('more')}
          </Link>
        </p>
      ) : null}
    </>
  )
}
