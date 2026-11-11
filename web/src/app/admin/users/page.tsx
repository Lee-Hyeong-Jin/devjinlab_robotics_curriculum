import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { Chip } from '@/components/Chip'
import { DataTable, type Column } from '@/components/DataTable'
import { RowAction } from '@/components/form/RowAction'
import { SelectAction } from '@/components/form/SelectAction'
import { PageHeader } from '@/components/PageHeader'
import { revokeUserSessions, updateUser } from '@/lib/actions/admin'
import { apiGetOrNull } from '@/lib/api/client'
import type { AdminUser, Role, UserStatus } from '@/lib/api/types'
import { formatDate } from '@/lib/format'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('admin')
  return { title: t('usersTitle') }
}

const ROLES: Role[] = ['learner', 'author', 'admin']
const ASSIGNABLE_STATUS: UserStatus[] = ['active', 'disabled']

interface Props {
  searchParams: Promise<{ cursor?: string }>
}

/** Admin users (Figma `23-221`) — `GET/PATCH /admin/users` with cursor paging. */
export default async function AdminUsersPage({ searchParams }: Props) {
  const [t, tRole, tStatus, locale, params] = await Promise.all([
    getTranslations('admin'),
    getTranslations('role'),
    getTranslations('userStatus'),
    getLocale(),
    searchParams,
  ])
  const page = await apiGetOrNull('/api/v1/admin/users', {
    query: { cursor: params.cursor, limit: 50 },
  })

  const columns: ReadonlyArray<Column<AdminUser>> = [
    {
      key: 'user',
      header: t('colUser'),
      cell: (row) => (
        <span className="flex flex-col">
          <span className="text-primary font-medium">{row.display_name || row.email}</span>
          <span className="text-muted text-xs">{row.email}</span>
          {row.email_verified ? null : <Chip tone="warning">{t('unverified')}</Chip>}
        </span>
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
      key: 'created',
      header: t('colCreated'),
      cell: (row) => formatDate(row.created_at, locale),
      hideOnMobile: true,
    },
    {
      key: 'change',
      header: t('colRole'),
      cell: (row) => (
        <SelectAction
          action={updateUser}
          hidden={{ userId: String(row.id) }}
          label={t('save')}
          pendingLabel={t('saving')}
          selects={[
            {
              name: 'role',
              label: t('colRole'),
              value: row.role,
              options: ROLES.map((role) => ({ value: role, label: tRole(role) })),
            },
            {
              name: 'status',
              label: t('colStatus'),
              value: ASSIGNABLE_STATUS.includes(row.status) ? row.status : 'active',
              options: ASSIGNABLE_STATUS.map((status) => ({
                value: status,
                label: tStatus(status),
              })),
            },
          ]}
        />
      ),
    },
    {
      key: 'sessions',
      header: t('colActions'),
      cell: (row) => (
        <RowAction
          action={revokeUserSessions}
          hidden={{ userId: String(row.id) }}
          label={t('revokeSessions')}
          pendingLabel={t('revoking')}
          confirm={t('revokeConfirm')}
        />
      ),
    },
  ]

  return (
    <>
      <PageHeader title={t('usersTitle')} subtitle={t('usersSubtitle')} />
      <Card className="p-0">
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
            href={`/admin/users?cursor=${encodeURIComponent(page.next_cursor)}`}
            className="text-accent text-sm underline underline-offset-2"
          >
            {t('more')}
          </Link>
        </p>
      ) : null}
    </>
  )
}
