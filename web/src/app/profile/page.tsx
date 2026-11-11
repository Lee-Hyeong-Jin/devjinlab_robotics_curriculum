import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { Chip } from '@/components/Chip'
import { DataTable, type Column } from '@/components/DataTable'
import { ActionForm } from '@/components/form/ActionForm'
import { RowAction } from '@/components/form/RowAction'
import { PageHeader } from '@/components/PageHeader'
import { apiGetOrNull } from '@/lib/api/client'
import type { ApiToken, AuthSession, Identity, Scope } from '@/lib/api/types'
import { requireUser } from '@/lib/auth'
import {
  changePassword,
  createToken,
  revokeSession,
  revokeToken,
  unlinkIdentity,
  updateProfile,
} from '@/lib/actions/profile'
import { formatDate, formatDateTime } from '@/lib/format'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('profile')
  return { title: t('title') }
}

const SCOPES: Scope[] = ['read:progress', 'write:progress', 'admin']

const SECTIONS = ['account', 'passwordSection', 'sessions', 'identities', 'tokens', 'data'] as const

/**
 * Profile (Figma `23-111`) — `GET/PATCH /me`, `/me/password`, `/me/sessions`,
 * `/me/identities`, `/me/tokens`, `/me/export` (frontend.md §2).
 */
export default async function ProfilePage() {
  const [t, tRole, locale] = await Promise.all([
    getTranslations('profile'),
    getTranslations('role'),
    getLocale(),
  ])
  const user = await requireUser('/profile')
  const [sessions, identities, tokens] = await Promise.all([
    apiGetOrNull('/api/v1/me/sessions'),
    apiGetOrNull('/api/v1/me/identities'),
    apiGetOrNull('/api/v1/me/tokens'),
  ])

  const sessionColumns: ReadonlyArray<Column<AuthSession>> = [
    {
      key: 'device',
      header: t('colDevice'),
      cell: (row) => (
        <span className="flex flex-col gap-1">
          <span className="truncate">{row.user_agent ?? '—'}</span>
          {row.current ? <Chip tone="accent">{t('sessionCurrent')}</Chip> : null}
        </span>
      ),
    },
    { key: 'ip', header: t('colIp'), cell: (row) => row.ip ?? '—', hideOnMobile: true },
    {
      key: 'lastSeen',
      header: t('colLastSeen'),
      cell: (row) => formatDateTime(row.last_seen_at, locale, user.timezone ?? undefined),
      hideOnMobile: true,
    },
    {
      key: 'expires',
      header: t('colExpires'),
      cell: (row) => formatDate(row.expires_at, locale, user.timezone ?? undefined),
      hideOnMobile: true,
    },
    {
      key: 'action',
      header: t('revoke'),
      cell: (row) =>
        row.current ? null : (
          <RowAction
            action={revokeSession}
            hidden={{ sessionId: String(row.id) }}
            label={t('revoke')}
            pendingLabel={t('revoking')}
          />
        ),
    },
  ]

  const tokenColumns: ReadonlyArray<Column<ApiToken>> = [
    { key: 'name', header: t('colTokenName'), cell: (row) => row.name },
    {
      key: 'prefix',
      header: t('colPrefix'),
      cell: (row) => <code className="font-mono text-xs">{row.prefix}</code>,
    },
    {
      key: 'scopes',
      header: t('colScopes'),
      cell: (row) => (
        <span className="flex flex-wrap gap-1">
          {row.scopes.map((scope) => (
            <Chip key={scope}>{scope}</Chip>
          ))}
        </span>
      ),
      hideOnMobile: true,
    },
    {
      key: 'expires',
      header: t('colExpiresAt'),
      cell: (row) =>
        row.expires_at ? formatDate(row.expires_at, locale, user.timezone ?? undefined) : '—',
      hideOnMobile: true,
    },
    {
      key: 'lastUsed',
      header: t('colLastUsed'),
      cell: (row) =>
        row.last_used_at
          ? formatDateTime(row.last_used_at, locale, user.timezone ?? undefined)
          : t('never'),
      hideOnMobile: true,
    },
    {
      key: 'action',
      header: t('revokeToken'),
      cell: (row) => (
        <RowAction
          action={revokeToken}
          hidden={{ tokenId: String(row.id) }}
          label={t('revokeToken')}
          pendingLabel={t('revokingToken')}
        />
      ),
    },
  ]

  const identityColumns: ReadonlyArray<Column<Identity>> = [
    { key: 'provider', header: t('colProvider'), cell: (row) => row.provider },
    { key: 'email', header: t('email'), cell: (row) => row.email ?? '—', hideOnMobile: true },
    {
      key: 'linkedAt',
      header: t('colLinkedAt'),
      cell: (row) => formatDate(row.linked_at, locale, user.timezone ?? undefined),
      hideOnMobile: true,
    },
    {
      key: 'action',
      header: t('unlink'),
      cell: (row) => (
        <RowAction
          action={unlinkIdentity}
          hidden={{ identityId: String(row.id) }}
          label={t('unlink')}
          pendingLabel={t('unlinking')}
        />
      ),
    },
  ]

  return (
    <>
      <PageHeader title={t('title')} subtitle={t('subtitle')} />

      <div className="grid gap-6 lg:grid-cols-[14rem_minmax(0,1fr)]">
        <nav aria-label={t('onThisPage')} className="lg:sticky lg:top-20 lg:self-start">
          <ul className="flex flex-wrap gap-1 lg:flex-col">
            {SECTIONS.map((section) => (
              <li key={section}>
                <a
                  href={`#${section}`}
                  className="text-muted hover:bg-subtle hover:text-primary block rounded-lg px-3 py-2 text-sm"
                >
                  {t(section)}
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <div className="flex min-w-0 flex-col gap-6">
          <Card as="section" aria-labelledby="account">
            <h2 id="account" className="text-primary mb-4 font-semibold">
              {t('account')}
            </h2>
            <dl className="mb-5 grid gap-3 sm:grid-cols-2">
              <div>
                <dt className="text-muted text-xs">{t('email')}</dt>
                <dd className="text-primary flex flex-wrap items-center gap-2 text-sm">
                  {user.email}
                  {user.email_verified ? (
                    <Chip tone="success">{t('emailVerified')}</Chip>
                  ) : (
                    <>
                      <Chip tone="warning">{t('emailUnverified')}</Chip>
                      <Link
                        href="/verify-email"
                        className="text-accent text-xs underline underline-offset-2"
                      >
                        {t('verifyEmailLink')}
                      </Link>
                    </>
                  )}
                </dd>
              </div>
              <div>
                <dt className="text-muted text-xs">{t('role')}</dt>
                <dd className="text-primary text-sm">{tRole(user.role)}</dd>
              </div>
              <div>
                <dt className="text-muted text-xs">{t('createdAt')}</dt>
                <dd className="text-primary text-sm">
                  {formatDate(user.created_at, locale, user.timezone ?? undefined)}
                </dd>
              </div>
            </dl>

            <ActionForm
              action={updateProfile}
              submitLabel={t('save')}
              pendingLabel={t('saving')}
              fields={[
                {
                  name: 'displayName',
                  label: t('displayName'),
                  defaultValue: user.display_name ?? '',
                  autoComplete: 'name',
                },
                {
                  name: 'locale',
                  label: t('locale'),
                  kind: 'select',
                  defaultValue: user.locale ?? 'ko',
                  options: [
                    { value: 'ko', label: '한국어' },
                    { value: 'en', label: 'English' },
                  ],
                },
                {
                  name: 'timezone',
                  label: t('timezone'),
                  defaultValue: user.timezone ?? '',
                  hint: t('timezoneHint'),
                },
              ]}
            />
          </Card>

          <Card as="section" aria-labelledby="passwordSection">
            <h2 id="passwordSection" className="text-primary mb-4 font-semibold">
              {t('passwordSection')}
            </h2>
            <ActionForm
              action={changePassword}
              submitLabel={t('changePassword')}
              pendingLabel={t('changingPassword')}
              fields={[
                {
                  name: 'currentPassword',
                  label: t('currentPassword'),
                  kind: 'password',
                  autoComplete: 'current-password',
                  required: true,
                },
                {
                  name: 'newPassword',
                  label: t('newPassword'),
                  kind: 'password',
                  autoComplete: 'new-password',
                  required: true,
                  minLength: 8,
                },
                {
                  name: 'newPasswordConfirm',
                  label: t('newPasswordConfirm'),
                  kind: 'password',
                  autoComplete: 'new-password',
                  required: true,
                },
              ]}
            />
          </Card>

          <Card as="section" className="p-0" aria-labelledby="sessions">
            <div className="p-5 pb-3">
              <h2 id="sessions" className="text-primary font-semibold">
                {t('sessions')}
              </h2>
              <p className="text-muted mt-1 text-sm">{t('sessionsHint')}</p>
            </div>
            <DataTable
              caption={t('sessionsTableCaption')}
              columns={sessionColumns}
              rows={sessions ?? []}
              rowKey={(row) => String(row.id)}
              empty={<p className="text-muted px-5 pb-5 text-sm">{t('noSessions')}</p>}
            />
          </Card>

          <Card as="section" className="p-0" aria-labelledby="identities">
            <div className="p-5 pb-3">
              <h2 id="identities" className="text-primary font-semibold">
                {t('identities')}
              </h2>
            </div>
            <DataTable
              caption={t('identitiesTableCaption')}
              columns={identityColumns}
              rows={identities ?? []}
              rowKey={(row) => String(row.id)}
              empty={<p className="text-muted px-5 pb-5 text-sm">{t('noIdentities')}</p>}
            />
          </Card>

          <Card as="section" aria-labelledby="tokens">
            <h2 id="tokens" className="text-primary font-semibold">
              {t('tokens')}
            </h2>
            <p className="text-muted mt-1 mb-4 text-sm">{t('tokensHint')}</p>
            <DataTable
              caption={t('tokensTableCaption')}
              columns={tokenColumns}
              rows={tokens ?? []}
              rowKey={(row) => String(row.id)}
              empty={<p className="text-muted pb-4 text-sm">{t('noTokens')}</p>}
            />
            <div className="border-border-default mt-5 border-t pt-5">
              <ActionForm
                action={createToken}
                submitLabel={t('createToken')}
                pendingLabel={t('creatingToken')}
                fields={[
                  { name: 'name', label: t('tokenName'), required: true },
                  {
                    name: 'scope',
                    label: t('tokenScopes'),
                    kind: 'checkboxGroup',
                    options: SCOPES.map((scope) => ({
                      value: scope,
                      label: scope,
                      mono: true,
                    })),
                  },
                  {
                    name: 'expiresInDays',
                    label: t('tokenExpiresInDays'),
                    kind: 'number',
                    min: 1,
                    max: 365,
                    defaultValue: '90',
                    hint: t('tokenExpiresHint'),
                  },
                ]}
              />
            </div>
          </Card>

          <Card as="section" aria-labelledby="data">
            <h2 id="data" className="text-primary font-semibold">
              {t('data')}
            </h2>
            <p className="text-muted mt-1 mb-4 text-sm">{t('exportHint')}</p>
            <a
              href="/api/me/export"
              className="bg-surface text-primary border-border-default hover:bg-subtle inline-flex items-center rounded-lg border px-4 py-2 text-sm font-medium"
            >
              {t('export')}
            </a>
          </Card>
        </div>
      </div>
    </>
  )
}
