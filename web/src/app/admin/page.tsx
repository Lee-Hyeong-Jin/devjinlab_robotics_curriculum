import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { DataTable, type Column } from '@/components/DataTable'
import { EmptyState } from '@/components/EmptyState'
import { PageHeader } from '@/components/PageHeader'
import { StatTile } from '@/components/StatTile'
import { apiGetOrNull } from '@/lib/api/client'
import type { AdminOverview, AuditEntry } from '@/lib/api/types'
import { formatDateTime, formatMinutes, formatPercent } from '@/lib/format'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('admin')
  return { title: t('overviewTitle') }
}

interface Attention {
  key: string
  text: string
  href?: string
}

/** What an operator should look at first, derived from the overview numbers. */
function attentionItems(
  data: AdminOverview,
  t: Awaited<ReturnType<typeof getTranslations<'admin'>>>,
  monitoringAlerts: number,
): Attention[] {
  const items: Attention[] = []
  if (monitoringAlerts > 0) {
    items.push({
      key: 'monitoring',
      text: t('attentionMonitoring', { count: monitoringAlerts }),
      href: '/admin/monitoring',
    })
  }
  if (data.system.lesson_count === null) {
    items.push({ key: 'content', text: t('attentionContent') })
  }
  if (!data.system.mail_enabled) items.push({ key: 'mail', text: t('attentionNoMail') })
  if (data.security.logins_24h.failed > 0) {
    items.push({
      key: 'failed',
      text: t('attentionFailedLogins', { count: data.security.logins_24h.failed }),
      href: '/admin/audit?action=auth.login.failed',
    })
  }
  // Without mail nobody can verify an address, so an unverified account is not a finding.
  if (data.system.mail_enabled && data.users.unverified > 0) {
    items.push({
      key: 'unverified',
      text: t('attentionUnverified', {
        count: data.users.unverified,
        stale: data.users.stale_unverified,
      }),
      href: '/admin/users?verified=false&status=active',
    })
  }
  const disabled = data.users.by_status.disabled ?? 0
  if (disabled > 0) {
    items.push({
      key: 'disabled',
      text: t('attentionDisabled', { count: disabled }),
      href: '/admin/users?status=disabled',
    })
  }
  const pending = data.users.by_status.pending_deletion ?? 0
  if (pending > 0) {
    items.push({
      key: 'pending',
      text: t('attentionPendingDeletion', { count: pending }),
      href: '/admin/users?status=pending_deletion',
    })
  }
  return items
}

/** Admin overview — `GET /admin/overview` plus the latest admin actions (P3-1). */
export default async function AdminOverviewPage() {
  const [t, locale] = await Promise.all([getTranslations('admin'), getLocale()])
  const [data, recent, machine, traffic] = await Promise.all([
    apiGetOrNull('/api/v1/admin/overview'),
    // What operators did lately: changes to users, not every page view.
    apiGetOrNull('/api/v1/admin/audit', { query: { action: 'user.', limit: 8 } }),
    // Only their alerts are used here; the readings themselves are on the monitoring page.
    apiGetOrNull('/api/v1/admin/monitoring/system'),
    apiGetOrNull('/api/v1/admin/monitoring/traffic', { query: { range: '24h' } }),
  ])

  if (!data) {
    return (
      <>
        <PageHeader title={t('overviewTitle')} subtitle={t('overviewSubtitle')} />
        <EmptyState title={t('unavailable')} />
      </>
    )
  }

  const { users, security, learning, system } = data
  const attempts = security.logins_24h.succeeded + security.logins_24h.failed
  const failRate = attempts > 0 ? security.logins_24h.failed / attempts : 0
  const attention = attentionItems(
    data,
    t,
    (machine?.alerts.length ?? 0) + (traffic?.alerts.length ?? 0),
  )
  const peak = Math.max(1, ...users.signups_daily.map((day) => day.count))
  const signupTotal = users.signups_daily.reduce((sum, day) => sum + day.count, 0)

  const systemRows: Array<[string, string]> = [
    [t('sysVersion'), system.version],
    [
      t('sysContent'),
      system.lesson_count === null
        ? t('sysContentFailed')
        : t('sysContentValue', {
            courses: system.course_count ?? 0,
            lessons: system.lesson_count,
          }),
    ],
    [t('sysMail'), system.mail_enabled ? t('on') : t('off')],
    [t('sysPublic'), system.public_content ? t('on') : t('off')],
    [t('sysSignup'), system.signup_open ? t('open') : t('closed')],
    [
      t('sysProviders'),
      system.auth_providers.length > 0 ? system.auth_providers.join(', ') : t('none'),
    ],
    [t('sysRetention'), t('sysRetentionValue', { days: system.audit_retention_days })],
  ]

  const recentColumns: ReadonlyArray<Column<AuditEntry>> = [
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
  ]

  return (
    <>
      <PageHeader
        title={t('overviewTitle')}
        subtitle={`${t('overviewSubtitle')} ${t('generatedAt', {
          time: formatDateTime(data.generated_at, locale),
        })}`}
      />

      <Card as="section" aria-labelledby="attention-heading" className="mb-6">
        <h2 id="attention-heading" className="text-primary mb-2 font-semibold">
          {t('secAttention')}
        </h2>
        {attention.length === 0 ? (
          <p className="text-muted text-sm">{t('attentionNone')}</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {attention.map((item) => (
              <li key={item.key} className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
                <span className="bg-state-in-progress size-2 shrink-0 rounded-full" aria-hidden />
                <span className="text-primary">{item.text}</span>
                {item.href ? (
                  <Link href={item.href} className="text-accent underline underline-offset-2">
                    {t('view')}
                  </Link>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </Card>

      <section aria-labelledby="accounts-heading" className="mb-6">
        <h2 id="accounts-heading" className="text-primary mb-3 font-semibold">
          {t('secAccounts')}
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatTile
            label={t('statUsers')}
            value={users.total.toLocaleString(locale)}
            hint={t('statUsersHint', { week: users.new_7d, month: users.new_30d })}
          />
          <StatTile
            label={t('statAdmins')}
            value={(users.by_role.admin ?? 0).toLocaleString(locale)}
            hint={t('statAuthors', { count: users.by_role.author ?? 0 })}
          />
          <StatTile
            label={t('statSessions')}
            value={security.active_sessions.toLocaleString(locale)}
          />
          <StatTile
            label={t('statLogins24h')}
            value={security.logins_24h.succeeded.toLocaleString(locale)}
            hint={`${t('statFailRate', { rate: formatPercent(failRate, locale) })} · ${t(
              'statLoginsHint',
              {
                failed: security.logins_24h.failed,
                weekOk: security.logins_7d.succeeded,
                weekFailed: security.logins_7d.failed,
              },
            )}`}
          />
        </div>
      </section>

      <section aria-labelledby="learning-heading" className="mb-6">
        <h2 id="learning-heading" className="text-primary mb-3 font-semibold">
          {t('secLearning', { days: learning.window_days })}
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatTile
            label={t('statActiveLearners')}
            value={learning.active_learners.toLocaleString(locale)}
            hint={t('statActiveLearnersHint', { total: learning.learners_total })}
          />
          <StatTile
            label={t('statLessonsCompleted')}
            value={learning.lessons_completed.toLocaleString(locale)}
            hint={t('statLessonsCompletedHint', { total: learning.lessons_completed_total })}
          />
          <StatTile
            label={t('statStudyTime')}
            value={formatMinutes(learning.study_minutes, locale)}
          />
        </div>
      </section>

      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card as="section" aria-labelledby="signups-heading">
          <h2 id="signups-heading" className="text-primary mb-1 font-semibold">
            {t('secSignups')}
          </h2>
          <p className="text-muted mb-3 text-sm">{t('signupsTotal', { count: signupTotal })}</p>
          {/* A bar per day. The list is the accessible form of the same data: each item reads
              "date: count", so the chart needs no separate table. */}
          <ol aria-label={t('signupsChartLabel')} className="flex h-28 items-end gap-1">
            {users.signups_daily.map((day) => (
              <li key={day.day} className="flex h-full flex-1 flex-col justify-end">
                <span className="sr-only">
                  {t('signupsDay', { day: day.day, count: day.count })}
                </span>
                <span
                  aria-hidden="true"
                  title={t('signupsDay', { day: day.day, count: day.count })}
                  className={day.count > 0 ? 'bg-accent-solid rounded-t' : 'bg-track rounded-t'}
                  style={{ height: `${Math.max(4, Math.round((day.count / peak) * 100))}%` }}
                />
              </li>
            ))}
          </ol>
          <p className="text-muted mt-2 flex justify-between text-xs" aria-hidden="true">
            <span>{users.signups_daily[0]?.day}</span>
            <span>{users.signups_daily[users.signups_daily.length - 1]?.day}</span>
          </p>
        </Card>

        <Card as="section" aria-labelledby="system-heading">
          <h2 id="system-heading" className="text-primary mb-2 font-semibold">
            {t('secSystem')}
          </h2>
          <dl className="flex flex-col">
            {systemRows.map(([label, value]) => (
              <div
                key={label}
                className="border-border-default flex justify-between gap-4 border-b py-2 text-sm last:border-b-0"
              >
                <dt className="text-muted">{label}</dt>
                <dd className="text-primary text-right font-medium wrap-anywhere">{value}</dd>
              </div>
            ))}
          </dl>
        </Card>
      </div>

      <section aria-labelledby="recent-heading">
        <h2 id="recent-heading" className="text-primary mb-3 font-semibold">
          {t('secRecent')}
        </h2>
        <DataTable
          caption={t('secRecent')}
          columns={recentColumns}
          rows={recent?.items ?? []}
          rowKey={(row) => String(row.id)}
          empty={<p className="text-muted text-sm">{t('noAudit')}</p>}
        />
      </section>
    </>
  )
}
