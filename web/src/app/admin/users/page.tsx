import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { ButtonLink, Button } from '@/components/Button'
import { Card } from '@/components/Card'
import { Chip } from '@/components/Chip'
import { DataTable, type Column } from '@/components/DataTable'
import { FilterInput, FilterSelect } from '@/components/form/FilterControls'
import { PageHeader } from '@/components/PageHeader'
import { oneOf, param, withQuery } from '@/lib/admin-query'
import { apiGetOrNull } from '@/lib/api/client'
import type { AdminUser, Role, UserStatus } from '@/lib/api/types'
import { formatDate } from '@/lib/format'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('admin')
  return { title: t('usersTitle') }
}

const ROLES: readonly Role[] = ['learner', 'author', 'admin']
const STATUSES: readonly UserStatus[] = ['active', 'disabled', 'pending_deletion', 'deleted']
const VERIFIED = ['true', 'false'] as const

interface Props {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}

/**
 * Admin users (Figma `23-221`) — `GET /admin/users` with search, filters and cursor paging.
 *
 * The table finds an account; changing it happens on the account's own page, where the
 * operator can see what they are about to change.
 */
export default async function AdminUsersPage({ searchParams }: Props) {
  const [t, tRole, tStatus, locale, params] = await Promise.all([
    getTranslations('admin'),
    getTranslations('role'),
    getTranslations('userStatus'),
    getLocale(),
    searchParams,
  ])
  const q = param(params.q)
  const role = oneOf(param(params.role), ROLES)
  const status = oneOf(param(params.status), STATUSES)
  const verified = oneOf(param(params.verified), VERIFIED)
  const filters = { q, role, status, verified }
  const filtered = Object.values(filters).some((value) => value !== undefined)

  const page = await apiGetOrNull('/api/v1/admin/users', {
    query: {
      ...filters,
      verified: verified === undefined ? undefined : verified === 'true',
      cursor: param(params.cursor),
      limit: 50,
    },
  })

  const any = { value: '', label: t('any') }
  const columns: ReadonlyArray<Column<AdminUser>> = [
    {
      key: 'user',
      header: t('colUser'),
      cell: (row) => (
        <Link href={`/admin/users/${row.id}`} className="flex flex-col">
          <span className="text-accent font-medium underline underline-offset-2">
            {row.display_name || row.email}
          </span>
          {row.display_name ? <span className="text-muted text-xs">{row.email}</span> : null}
        </Link>
      ),
    },
    {
      key: 'role',
      header: t('colRole'),
      cell: (row) => (
        <Chip tone={row.role === 'learner' ? 'neutral' : 'accent'}>{tRole(row.role)}</Chip>
      ),
    },
    {
      key: 'status',
      header: t('colStatus'),
      cell: (row) => (
        <Chip tone={row.status === 'active' ? 'success' : 'warning'}>{tStatus(row.status)}</Chip>
      ),
    },
    {
      key: 'verified',
      header: t('colVerified'),
      cell: (row) =>
        row.email_verified ? (
          <span className="text-muted">{t('verified')}</span>
        ) : (
          <Chip tone="warning">{t('unverified')}</Chip>
        ),
    },
    {
      key: 'created',
      header: t('colCreated'),
      cell: (row) => formatDate(row.created_at, locale),
      hideOnMobile: true,
    },
  ]

  return (
    <>
      <PageHeader title={t('usersTitle')} subtitle={t('usersSubtitle')} />

      <form
        method="get"
        role="search"
        aria-label={t('userFiltersLabel')}
        className="mb-4 grid grid-cols-1 items-end gap-3 sm:grid-cols-2 lg:grid-cols-[minmax(0,2fr)_repeat(3,minmax(0,1fr))_auto]"
      >
        <FilterInput
          label={t('searchLabel')}
          name="q"
          type="search"
          defaultValue={q ?? ''}
          placeholder={t('searchPlaceholder')}
          maxLength={200}
          autoComplete="off"
        />
        <FilterSelect
          label={t('filterRole')}
          name="role"
          value={role ?? ''}
          options={[any, ...ROLES.map((value) => ({ value, label: tRole(value) }))]}
        />
        <FilterSelect
          label={t('filterStatus')}
          name="status"
          value={status ?? ''}
          options={[any, ...STATUSES.map((value) => ({ value, label: tStatus(value) }))]}
        />
        <FilterSelect
          label={t('filterVerified')}
          name="verified"
          value={verified ?? ''}
          options={[
            any,
            { value: 'true', label: t('verifiedYes') },
            { value: 'false', label: t('verifiedNo') },
          ]}
        />
        <div className="flex gap-2">
          <Button type="submit">{t('apply')}</Button>
          {filtered ? (
            <ButtonLink href="/admin/users" kind="secondary">
              {t('reset')}
            </ButtonLink>
          ) : null}
        </div>
      </form>

      <p className="text-muted mb-3 text-sm" role="status">
        {t('resultCount', { count: page?.total ?? 0 })}
      </p>

      <Card className="p-0 sm:p-0">
        <DataTable
          caption={t('usersTableCaption')}
          columns={columns}
          rows={page?.items ?? []}
          rowKey={(row) => String(row.id)}
          empty={<p className="text-muted p-5 text-sm">{t('noUsers')}</p>}
        />
      </Card>

      {page?.next_cursor ? (
        <p className="mt-4">
          <Link
            href={withQuery('/admin/users', { ...filters, cursor: page.next_cursor })}
            className="text-accent text-sm underline underline-offset-2"
          >
            {t('more')}
          </Link>
        </p>
      ) : null}
    </>
  )
}
