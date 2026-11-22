import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { Chip } from '@/components/Chip'
import { DataTable, type Column } from '@/components/DataTable'
import { EmptyState } from '@/components/EmptyState'
import { RowAction } from '@/components/form/RowAction'
import { SelectAction } from '@/components/form/SelectAction'
import { PageHeader } from '@/components/PageHeader'
import {
  revokeUserSessions,
  revokeUserTokens,
  sendPasswordReset,
  updateUser,
} from '@/lib/actions/admin'
import { positiveInt } from '@/lib/admin-query'
import { apiGetOrNull } from '@/lib/api/client'
import type { AdminUserOverview, AuditEntry, Role, UserStatus } from '@/lib/api/types'
import { getMe } from '@/lib/auth'
import { formatDate, formatDateTime, formatMinutes } from '@/lib/format'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('admin')
  return { title: t('userTitle') }
}

const ROLES: Role[] = ['learner', 'author', 'admin']
const ASSIGNABLE_STATUS: UserStatus[] = ['active', 'disabled']

type Session = AdminUserOverview['sessions'][number]
type Token = AdminUserOverview['tokens'][number]
type Identity = AdminUserOverview['identities'][number]

interface Params {
  params: Promise<{ userId: string }>
}

/**
 * One account for an operator — `GET /admin/users/{id}/overview` (P3-1).
 *
 * Everything needed to answer "what is going on with this account" is on one page, next to
 * the actions that fix it. Each action is checked by the API, is audited, and asks first.
 */
export default async function AdminUserPage({ params }: Params) {
  const [t, tRole, tStatus, locale, { userId }, me] = await Promise.all([
    getTranslations('admin'),
    getTranslations('role'),
    getTranslations('userStatus'),
    getLocale(),
    params,
    getMe(),
  ])
  const id = positiveInt(userId)
  const data = id
    ? await apiGetOrNull(
        `/api/v1/admin/users/${id}/overview` as '/api/v1/admin/users/{user_id}/overview',
      )
    : null
  const back = (
    <Link href="/admin/users" className="text-accent underline underline-offset-2">
      {t('backToUsers')}
    </Link>
  )

  if (!data) {
    return (
      <>
        <PageHeader title={t('userTitle')} eyebrow={back} />
        <EmptyState title={t('userNotFound')} />
      </>
    )
  }

  const { user, learning } = data
  const hidden = { userId: String(user.id) }
  const isSelf = me?.id === user.id
  // Spelled out rather than built from the value, so the catalogue check can see each key.
  const verification = {
    verified: t('verification_verified'),
    pending: t('verification_pending'),
    unavailable: t('verification_unavailable'),
  }[user.email_verification]

  const profile: Array<[string, React.ReactNode]> = [
    [t('fieldEmail'), user.email],
    [t('fieldName'), user.display_name || '—'],
    [t('fieldId'), `#${user.id}`],
    [t('fieldVerification'), verification],
    [t('fieldPassword'), user.has_password ? t('hasPassword') : t('noPassword')],
    [t('fieldCreated'), formatDate(user.created_at, locale)],
    [t('fieldUpdated'), formatDateTime(user.updated_at, locale)],
    [t('fieldFailedLogins'), t('failedLoginsValue', { count: data.failed_logins_24h })],
  ]

  const sessionColumns: ReadonlyArray<Column<Session>> = [
    {
      key: 'device',
      header: t('colDevice'),
      cell: (row) => <span className="text-sm">{row.user_agent ?? '—'}</span>,
    },
    { key: 'ip', header: t('colIp'), cell: (row) => row.ip ?? '—' },
    {
      key: 'seen',
      header: t('colLastSeen'),
      cell: (row) => formatDateTime(row.last_seen_at, locale),
    },
    {
      key: 'expires',
      header: t('colExpires'),
      cell: (row) => formatDate(row.expires_at, locale),
      hideOnMobile: true,
    },
  ]
  const tokenColumns: ReadonlyArray<Column<Token>> = [
    {
      key: 'name',
      header: t('colTokenName'),
      cell: (row) => (
        <span className="flex flex-col">
          <span className="font-medium">{row.name}</span>
          <code className="text-muted font-mono text-xs">{row.prefix}…</code>
        </span>
      ),
    },
    {
      key: 'scopes',
      header: t('colScopes'),
      cell: (row) => <code className="font-mono text-xs">{row.scopes.join(', ')}</code>,
    },
    {
      key: 'used',
      header: t('colLastUsed'),
      cell: (row) => (row.last_used_at ? formatDateTime(row.last_used_at, locale) : t('never')),
    },
    {
      key: 'expires',
      header: t('colExpires'),
      cell: (row) => (row.expires_at ? formatDate(row.expires_at, locale) : t('noExpiry')),
      hideOnMobile: true,
    },
  ]
  const identityColumns: ReadonlyArray<Column<Identity>> = [
    { key: 'provider', header: t('colProvider'), cell: (row) => row.provider },
    { key: 'email', header: t('fieldEmail'), cell: (row) => row.email ?? '—' },
    {
      key: 'linked',
      header: t('colLinked'),
      cell: (row) => formatDate(row.linked_at, locale),
    },
  ]
  const auditColumns: ReadonlyArray<Column<AuditEntry>> = [
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
      cell: (row) => row.actor_email ?? t('system'),
    },
    { key: 'ip', header: t('colIp'), cell: (row) => row.actor_ip ?? '—', hideOnMobile: true },
  ]

  return (
    <>
      <PageHeader
        title={user.display_name || user.email}
        eyebrow={back}
        actions={
          <>
            <Chip tone={user.role === 'learner' ? 'neutral' : 'accent'}>{tRole(user.role)}</Chip>
            <Chip tone={user.status === 'active' ? 'success' : 'warning'}>
              {tStatus(user.status)}
            </Chip>
          </>
        }
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card as="section" aria-labelledby="profile-heading">
          <h2 id="profile-heading" className="text-primary mb-2 font-semibold">
            {t('secProfile')}
          </h2>
          <dl className="flex flex-col">
            {profile.map(([label, value]) => (
              <div
                key={label}
                className="border-border-default flex justify-between gap-4 border-b py-2 text-sm last:border-b-0"
              >
                <dt className="text-muted shrink-0">{label}</dt>
                <dd className="text-primary text-right font-medium wrap-anywhere">{value}</dd>
              </div>
            ))}
          </dl>
        </Card>

        <div className="flex min-w-0 flex-col gap-6">
          <Card as="section" aria-labelledby="access-heading">
            <h2 id="access-heading" className="text-primary mb-3 font-semibold">
              {t('secAccess')}
            </h2>
            <SelectAction
              action={updateUser}
              hidden={hidden}
              label={t('save')}
              pendingLabel={t('saving')}
              selects={[
                {
                  name: 'role',
                  label: t('colRole'),
                  value: user.role,
                  options: ROLES.map((role) => ({ value: role, label: tRole(role) })),
                },
                {
                  name: 'status',
                  label: t('colStatus'),
                  value: ASSIGNABLE_STATUS.includes(user.status) ? user.status : 'active',
                  options: ASSIGNABLE_STATUS.map((status) => ({
                    value: status,
                    label: tStatus(status),
                  })),
                },
              ]}
            />
            {isSelf ? <p className="text-muted mt-2 text-xs">{t('actionsSelfNote')}</p> : null}
          </Card>

          <Card as="section" aria-labelledby="actions-heading">
            <h2 id="actions-heading" className="text-primary mb-3 font-semibold">
              {t('secActions')}
            </h2>
            <div className="flex flex-wrap items-start gap-3">
              <RowAction
                action={revokeUserSessions}
                hidden={hidden}
                label={t('revokeSessions')}
                pendingLabel={t('revoking')}
                confirm={t('revokeConfirm')}
              />
              <RowAction
                action={revokeUserTokens}
                hidden={hidden}
                label={t('revokeTokens')}
                pendingLabel={t('revokingTokens')}
                confirm={t('revokeTokensConfirm')}
              />
              <RowAction
                action={sendPasswordReset}
                hidden={hidden}
                label={t('sendReset')}
                pendingLabel={t('sendingReset')}
                confirm={t('sendResetConfirm')}
              />
            </div>
            <p className="text-muted mt-3 text-xs">{t('sendResetHint')}</p>
          </Card>

          <Card as="section" aria-labelledby="user-learning-heading">
            <h2 id="user-learning-heading" className="text-primary mb-2 font-semibold">
              {t('secUserLearning')}
            </h2>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              {(
                [
                  [t('learnDone'), learning.lessons_done.toLocaleString(locale)],
                  [t('learnInProgress'), learning.lessons_in_progress.toLocaleString(locale)],
                  [t('learnTime'), formatMinutes(learning.study_minutes, locale)],
                  [
                    t('learnLast'),
                    learning.last_activity_at
                      ? formatDateTime(learning.last_activity_at, locale)
                      : t('never'),
                  ],
                ] as Array<[string, string]>
              ).map(([label, value]) => (
                <div key={label}>
                  <dt className="text-muted text-xs">{label}</dt>
                  <dd className="text-primary font-semibold">{value}</dd>
                </div>
              ))}
            </dl>
          </Card>
        </div>
      </div>

      <section aria-labelledby="sessions-heading" className="mt-6">
        <h2 id="sessions-heading" className="text-primary mb-3 font-semibold">
          {t('secSessions')}
        </h2>
        <DataTable
          caption={t('secSessions')}
          columns={sessionColumns}
          rows={data.sessions}
          rowKey={(row) => String(row.id)}
          empty={<p className="text-muted text-sm">{t('noSessions')}</p>}
        />
      </section>

      <section aria-labelledby="tokens-heading" className="mt-6">
        <h2 id="tokens-heading" className="text-primary mb-3 font-semibold">
          {t('secTokens')}
        </h2>
        <DataTable
          caption={t('secTokens')}
          columns={tokenColumns}
          rows={data.tokens}
          rowKey={(row) => String(row.id)}
          empty={<p className="text-muted text-sm">{t('noTokens')}</p>}
        />
      </section>

      <section aria-labelledby="identities-heading" className="mt-6">
        <h2 id="identities-heading" className="text-primary mb-3 font-semibold">
          {t('secIdentities')}
        </h2>
        <DataTable
          caption={t('secIdentities')}
          columns={identityColumns}
          rows={data.identities}
          rowKey={(row) => String(row.id)}
          empty={<p className="text-muted text-sm">{t('noIdentities')}</p>}
        />
      </section>

      <section aria-labelledby="user-audit-heading" className="mt-6">
        <h2 id="user-audit-heading" className="text-primary mb-3 font-semibold">
          {t('secUserAudit')}
        </h2>
        <DataTable
          caption={t('secUserAudit')}
          columns={auditColumns}
          rows={data.recent_audit}
          rowKey={(row) => String(row.id)}
          empty={<p className="text-muted text-sm">{t('noUserAudit')}</p>}
        />
        <p className="mt-3">
          <Link
            href={`/admin/audit?target_type=user&target_id=${user.id}`}
            className="text-accent text-sm underline underline-offset-2"
          >
            {t('viewAllAudit')}
          </Link>
        </p>
      </section>
    </>
  )
}
