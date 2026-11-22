import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { Chip } from '@/components/Chip'
import { DataTable, type Column } from '@/components/DataTable'
import { EmptyState } from '@/components/EmptyState'
import { AutoRefresh } from '@/components/monitoring/AutoRefresh'
import { BarChart } from '@/components/monitoring/BarChart'
import { Meter } from '@/components/monitoring/Meter'
import { PageHeader } from '@/components/PageHeader'
import { StatTile } from '@/components/StatTile'
import { oneOf, param, withQuery } from '@/lib/admin-query'
import { apiGetOrNull } from '@/lib/api/client'
import type {
  FailedRequest,
  MonitoringAlert,
  MonitoringLevel,
  RouteStats,
  SystemStatus,
} from '@/lib/api/types'
import { cx } from '@/lib/cx'
import {
  formatBytes,
  formatDateTime,
  formatDuration,
  formatMinutes,
  formatMs,
  formatRatio,
} from '@/lib/format'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('monitoring')
  return { title: t('title') }
}

const TRAFFIC_RANGES = ['24h', '7d', '30d'] as const
const VISIT_RANGES = ['7d', '30d', '90d'] as const

interface Props {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}

type T = Awaited<ReturnType<typeof getTranslations<'monitoring'>>>

/** One alert as a sentence, with the reading and its threshold in the units a person reads. */
function alertText(alert: MonitoringAlert, t: T, locale: string): string {
  const detail = alert.detail ?? ''
  const percent = (value: number) => formatRatio(value, locale)
  switch (alert.key) {
    case 'disk':
      return t('alert_disk', {
        value: percent(alert.value),
        threshold: percent(alert.threshold),
        detail,
      })
    case 'memory':
      return t('alert_memory', { value: percent(alert.value), threshold: percent(alert.threshold) })
    case 'swap':
      return t('alert_swap', { value: percent(alert.value), threshold: percent(alert.threshold) })
    case 'load':
      return t('alert_load', {
        value: alert.value.toFixed(2),
        threshold: alert.threshold.toFixed(1),
      })
    case 'temperature':
      return t('alert_temperature', {
        value: `${alert.value.toFixed(0)} °C`,
        threshold: `${alert.threshold.toFixed(0)} °C`,
        detail,
      })
    case 'open_files':
      return t('alert_open_files', {
        value: percent(alert.value),
        threshold: percent(alert.threshold),
      })
    case 'db_connections':
      return t('alert_db_connections', {
        value: percent(alert.value),
        threshold: percent(alert.threshold),
      })
    case 'database':
      return t('alert_database')
    case 'errors':
      return t('alert_errors', {
        value: formatRatio(alert.value, locale, 2),
        threshold: formatRatio(alert.threshold, locale, 0),
      })
    case 'latency':
      return t('alert_latency', {
        value: formatMs(alert.value, locale),
        threshold: formatMs(alert.threshold, locale),
      })
    case 'error_budget':
      return t('alert_error_budget', {
        value: formatRatio(alert.value, locale, 0),
        threshold: formatRatio(alert.threshold, locale, 0),
      })
    default:
      return alert.key
  }
}

function RangeLinks({
  label,
  name,
  current,
  options,
  query,
  anchor,
}: {
  label: string
  name: string
  current: string
  options: ReadonlyArray<{ value: string; label: string }>
  query: Record<string, string | undefined>
  anchor: string
}) {
  return (
    <nav aria-label={label}>
      <ul className="bg-subtle inline-flex gap-0.5 rounded-lg p-0.5">
        {options.map((option) => (
          <li key={option.value}>
            <Link
              href={`${withQuery('/admin/monitoring', { ...query, [name]: option.value })}#${anchor}`}
              aria-current={option.value === current ? 'true' : undefined}
              className={cx(
                'inline-flex min-h-10 items-center rounded-md px-3 text-sm font-medium whitespace-nowrap',
                option.value === current
                  ? 'bg-surface text-primary'
                  : 'text-muted hover:text-primary',
              )}
            >
              {option.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  )
}

function hottest(system: SystemStatus) {
  return system.temperatures[0]
}

/**
 * Monitoring — `GET /admin/monitoring/{kpi,system,traffic,errors,visits}` (P3-2, ADR 0017).
 *
 * One screen, top to bottom in the order an operator asks: is anything wrong, how is the
 * business doing, is the machine healthy, is the API healthy, what failed, who is visiting.
 * The periods are in the URL, so a view can be bookmarked or shared.
 */
export default async function MonitoringPage({ searchParams }: Props) {
  const [t, locale, params] = await Promise.all([
    getTranslations('monitoring'),
    getLocale(),
    searchParams,
  ])
  const trafficRange = oneOf(param(params.t), TRAFFIC_RANGES) ?? '24h'
  const visitRange = oneOf(param(params.v), VISIT_RANGES) ?? '30d'
  const errorCursor = param(params.cursor)
  const query = { t: trafficRange, v: visitRange }

  const [system, traffic, errors, visits, kpi] = await Promise.all([
    apiGetOrNull('/api/v1/admin/monitoring/system'),
    apiGetOrNull('/api/v1/admin/monitoring/traffic', { query: { range: trafficRange } }),
    apiGetOrNull('/api/v1/admin/monitoring/errors', { query: { limit: 20, cursor: errorCursor } }),
    apiGetOrNull('/api/v1/admin/monitoring/visits', { query: { range: visitRange } }),
    apiGetOrNull('/api/v1/admin/monitoring/kpi'),
  ])

  if (!system || !traffic || !errors || !visits || !kpi) {
    return (
      <>
        <PageHeader title={t('title')} />
        <EmptyState title={t('unavailable')} />
      </>
    )
  }

  const levelLabel = (level: MonitoringLevel) =>
    ({ ok: t('levelOk'), warning: t('levelWarning'), critical: t('levelCritical') })[level]
  const count = (value: number) => value.toLocaleString(locale)
  const alerts = [...system.alerts, ...traffic.alerts]
  const none = t('noData')
  const rangeLabels = {
    '24h': t('range24h'),
    '7d': t('range7d'),
    '30d': t('range30d'),
    '90d': t('range90d'),
  }

  const hot = hottest(system)
  const disk = system.disks[0]
  const memory = system.memory
  const cpu = system.cpu
  const db = system.database
  const totals = traffic.totals
  const budget = traffic.error_budget

  const bucketLabel = (iso: string) =>
    new Intl.DateTimeFormat(locale, {
      month: 'short',
      day: 'numeric',
      ...(traffic.bucket_seconds < 86400 ? { hour: 'numeric' } : {}),
    }).format(new Date(iso))

  const routeColumns = (kind: 'busiest' | 'slowest' | 'failing'): Column<RouteStats>[] => [
    {
      key: 'route',
      header: t('colRoute'),
      cell: (row) => (
        <code className="font-mono text-xs">
          {row.method} {row.route}
        </code>
      ),
    },
    { key: 'requests', header: t('colRequests'), cell: (row) => count(row.requests) },
    ...(kind === 'slowest'
      ? []
      : [
          {
            key: 'errors',
            header: t('colErrors'),
            cell: (row: RouteStats) => (
              <span className={row.server_errors > 0 ? 'text-danger font-semibold' : undefined}>
                {count(row.server_errors)}
              </span>
            ),
          },
          {
            key: 'client',
            header: t('colClientErrors'),
            cell: (row: RouteStats) => count(row.client_errors),
            hideOnMobile: true,
          },
        ]),
    { key: 'p95', header: t('colP95'), cell: (row) => formatMs(row.p95_ms, locale) },
    {
      key: 'mean',
      header: t('colMean'),
      cell: (row) => formatMs(row.mean_ms, locale),
      hideOnMobile: true,
    },
    {
      key: 'max',
      header: t('colMax'),
      cell: (row) => formatMs(row.max_ms, locale),
      hideOnMobile: true,
    },
  ]

  const errorColumns: ReadonlyArray<Column<FailedRequest>> = [
    {
      key: 'at',
      header: t('colAt'),
      cell: (row) => <span className="whitespace-nowrap">{formatDateTime(row.at, locale)}</span>,
    },
    {
      key: 'status',
      header: t('colStatus'),
      cell: (row) => <Chip tone="warning">{String(row.status)}</Chip>,
    },
    {
      key: 'path',
      header: t('colPath'),
      cell: (row) => (
        <code className="font-mono text-xs">
          {row.method} {row.path}
        </code>
      ),
    },
    {
      key: 'error',
      header: t('colError'),
      cell: (row) =>
        row.error_type ? (
          <span className="text-sm">
            <span className="font-semibold">{row.error_type}</span>
            {row.error_message ? <span className="text-muted">: {row.error_message}</span> : null}
          </span>
        ) : (
          '—'
        ),
    },
    {
      key: 'duration',
      header: t('colDuration'),
      cell: (row) => formatMs(row.duration_ms, locale),
      hideOnMobile: true,
    },
    {
      key: 'request',
      header: t('colRequestId'),
      cell: (row) => <code className="text-muted font-mono text-xs">{row.request_id ?? '—'}</code>,
    },
    {
      key: 'user',
      header: t('colUser'),
      cell: (row) =>
        row.user_id === null ? (
          '—'
        ) : (
          <Link
            href={`/admin/users/${row.user_id}`}
            className="text-accent underline underline-offset-2"
          >
            #{row.user_id}
          </Link>
        ),
      hideOnMobile: true,
    },
  ]

  const sections: Array<[string, string]> = [
    ['kpi', t('kpiTitle')],
    ['system', t('systemTitle')],
    ['traffic', t('trafficTitle')],
    ['errors', t('errorsTitle')],
    ['visits', t('visitsTitle')],
  ]

  return (
    <>
      <PageHeader
        title={t('title')}
        subtitle={t('subtitle', { time: formatDateTime(system.generated_at, locale) })}
        actions={<AutoRefresh refreshLabel={t('refresh')} autoLabel={t('autoRefresh')} />}
      />

      <nav aria-label={t('sections')} className="mb-6">
        <ul className="flex flex-wrap gap-x-4 gap-y-1 text-sm">
          {sections.map(([id, label]) => (
            <li key={id}>
              <a
                href={`#${id}`}
                className="text-accent inline-flex min-h-11 items-center underline underline-offset-2"
              >
                {label}
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <Card as="section" aria-labelledby="alerts-heading" className="mb-8">
        <h2 id="alerts-heading" className="text-primary mb-2 font-semibold">
          {t('alertsTitle')}
        </h2>
        {alerts.length === 0 ? (
          <p className="text-muted text-sm">{t('alertsNone')}</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {alerts.map((alert, index) => (
              <li
                key={`${alert.key}-${index}`}
                className="flex flex-wrap items-center gap-2 text-sm"
              >
                <Chip tone="warning">{levelLabel(alert.level)}</Chip>
                <span className={alert.level === 'critical' ? 'text-danger font-semibold' : ''}>
                  {alertText(alert, t, locale)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      {/* -- KPIs ------------------------------------------------------------------------- */}
      <section aria-labelledby="kpi" className="mb-10 scroll-mt-24">
        <h2 id="kpi" className="text-primary mb-3 text-lg font-bold">
          {t('kpiTitle')}
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatTile
            label={t('kpiDau')}
            value={count(kpi.active_users.daily)}
            hint={t('kpiActiveHint')}
          />
          <StatTile label={t('kpiWau')} value={count(kpi.active_users.weekly)} />
          <StatTile label={t('kpiMau')} value={count(kpi.active_users.monthly)} />
          <StatTile
            label={t('kpiStickiness')}
            value={
              kpi.active_users.stickiness === null
                ? none
                : formatRatio(kpi.active_users.stickiness, locale, 0)
            }
            hint={t('kpiStickinessHint')}
          />
          <StatTile
            label={t('kpiSignups')}
            value={count(kpi.growth.signups_7d)}
            hint={t('kpiSignupsHint', {
              month: kpi.growth.signups_30d,
              total: kpi.growth.users_total,
            })}
          />
          <StatTile
            label={t('kpiConversion')}
            value={
              kpi.growth.visit_to_signup === null
                ? none
                : formatRatio(kpi.growth.visit_to_signup, locale)
            }
            hint={t('kpiConversionHint', { days: kpi.growth.visitor_days_30d })}
          />
          <StatTile
            label={t('kpiActivation')}
            value={
              kpi.cohorts.activation_rate === null
                ? none
                : formatRatio(kpi.cohorts.activation_rate, locale, 0)
            }
            hint={t('kpiActivationHint', {
              cohort: kpi.cohorts.activation_cohort,
              count: kpi.cohorts.activated,
            })}
          />
          <StatTile
            label={t('kpiRetention')}
            value={
              kpi.cohorts.week1_retention === null
                ? none
                : formatRatio(kpi.cohorts.week1_retention, locale, 0)
            }
            hint={t('kpiRetentionHint', {
              cohort: kpi.cohorts.retention_cohort,
              count: kpi.cohorts.retained,
            })}
          />
          <StatTile
            label={t('kpiLearners')}
            value={count(kpi.learning_7d.active_learners)}
            hint={t('kpiLearnersHint', { month: kpi.learning_30d.active_learners })}
          />
          <StatTile
            label={t('kpiLessons')}
            value={count(kpi.learning_7d.lessons_completed)}
            hint={t('kpiLessonsHint', { month: kpi.learning_30d.lessons_completed })}
          />
          <StatTile
            label={t('kpiStudy')}
            value={formatMinutes(kpi.learning_7d.study_minutes, locale)}
            hint={t('kpiStudyHint', {
              month: formatMinutes(kpi.learning_30d.study_minutes, locale),
            })}
          />
          <StatTile
            label={t('kpiQuiz')}
            value={
              kpi.learning_30d.quiz_mean_score === null
                ? none
                : formatRatio(kpi.learning_30d.quiz_mean_score, locale, 0)
            }
            hint={t('kpiQuizHint', {
              runs: kpi.learning_30d.quiz_runs,
              reviews: kpi.learning_30d.reviews,
            })}
          />
        </div>
      </section>

      {/* -- system ----------------------------------------------------------------------- */}
      <section aria-labelledby="system" className="mb-10 scroll-mt-24">
        <h2 id="system" className="text-primary mb-1 text-lg font-bold">
          {t('systemTitle')}
        </h2>
        <p className="text-muted mb-3 max-w-3xl text-sm">{t('systemHint')}</p>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {cpu ? (
            <Meter
              label={t('cpu')}
              value={
                cpu.usage_ratio === null
                  ? (cpu.load_1m?.toFixed(2) ?? none)
                  : formatRatio(cpu.usage_ratio, locale, 0)
              }
              ratio={cpu.usage_ratio ?? cpu.load_per_cpu}
              level={cpu.level}
              levelLabel={levelLabel(cpu.level)}
              hint={
                <>
                  {t('cpuLoad', {
                    one: cpu.load_1m?.toFixed(2) ?? '—',
                    five: cpu.load_5m?.toFixed(2) ?? '—',
                    fifteen: cpu.load_15m?.toFixed(2) ?? '—',
                    count: cpu.count,
                  })}
                  {cpu.usage_ratio === null ? ` · ${t('cpuUsageFirst')}` : ''}
                </>
              }
            />
          ) : null}
          {memory ? (
            <Meter
              label={t('memory')}
              value={formatRatio(memory.used_ratio, locale, 0)}
              ratio={memory.used_ratio}
              level={memory.level}
              levelLabel={levelLabel(memory.level)}
              hint={t('memoryDetail', {
                used: formatBytes(memory.total_bytes - memory.available_bytes, locale),
                total: formatBytes(memory.total_bytes, locale),
                rss: formatBytes(memory.process_rss_bytes, locale),
              })}
            />
          ) : null}
          {disk ? (
            <Meter
              label={t('disk')}
              value={formatRatio(disk.used_ratio, locale, 0)}
              ratio={disk.used_ratio}
              level={disk.level}
              levelLabel={levelLabel(disk.level)}
              hint={t('diskDetail', {
                used: formatBytes(disk.used_bytes, locale),
                total: formatBytes(disk.total_bytes, locale),
                free: formatBytes(disk.free_bytes, locale),
                path: disk.path,
              })}
            />
          ) : null}
          {hot ? (
            <Meter
              label={t('temperature')}
              value={`${hot.celsius.toFixed(0)} °C`}
              ratio={hot.celsius / 100}
              level={hot.level}
              levelLabel={levelLabel(hot.level)}
              hint={t('temperatureHottest', { sensor: hot.sensor })}
            />
          ) : (
            <Card className="flex flex-col gap-2">
              <span className="text-muted text-xs font-medium tracking-wide uppercase">
                {t('temperature')}
              </span>
              <span className="text-muted text-sm">{t('temperatureNone')}</span>
            </Card>
          )}
          {memory ? (
            <Meter
              label={t('swap')}
              value={
                memory.swap_used_ratio === null
                  ? t('swapNone')
                  : formatRatio(memory.swap_used_ratio, locale, 0)
              }
              ratio={memory.swap_used_ratio}
              level={memory.swap_level}
              levelLabel={levelLabel(memory.swap_level)}
              hint={
                memory.swap_total_bytes > 0
                  ? t('swapDetail', { total: formatBytes(memory.swap_total_bytes, locale) })
                  : undefined
              }
            />
          ) : null}
          <Meter
            label={t('openFiles')}
            value={
              system.process.open_files === null
                ? none
                : t('openFilesValue', {
                    open: count(system.process.open_files),
                    limit:
                      system.process.open_files_limit === null
                        ? '—'
                        : count(system.process.open_files_limit),
                  })
            }
            ratio={system.process.open_files_ratio}
            level={system.process.open_files_level}
            levelLabel={levelLabel(system.process.open_files_level)}
            hint={
              system.process.requests_in_progress === null
                ? undefined
                : `${t('inProgress')}: ${count(system.process.requests_in_progress)}`
            }
          />
          <StatTile
            label={t('uptime')}
            value={formatDuration(system.process_uptime_seconds, locale)}
            hint={`${t('uptimeProcess', {
              process: formatDuration(system.process_uptime_seconds, locale),
            })} · ${t('uptimeHost', {
              host: formatDuration(system.host_uptime_seconds, locale),
            })} · ${t('version')} ${system.version}`}
          />
          <Meter
            label={t('database')}
            value={db.reachable ? formatMs(db.ping_ms, locale) : t('dbUnreachable')}
            ratio={
              db.connections !== null && db.connections_max
                ? db.connections / db.connections_max
                : null
            }
            level={db.reachable ? db.connections_level : 'critical'}
            levelLabel={levelLabel(db.reachable ? db.connections_level : 'critical')}
            hint={[
              `${t('dbBackend')}: ${db.backend}`,
              `${t('dbSize')}: ${formatBytes(db.size_bytes, locale)}`,
              db.connections !== null && db.connections_max !== null
                ? `${t('dbConnections')}: ${t('dbConnectionsValue', {
                    used: db.connections,
                    max: db.connections_max,
                  })}`
                : null,
              ...Object.entries(db.pool).map(
                ([, pool]) => `${t('dbPool')}: ${pool.checked_out ?? 0} / ${pool.size ?? 0}`,
              ),
            ]
              .filter(Boolean)
              .join(' · ')}
          />
        </div>

        {system.temperatures.length > 1 ? (
          <details className="mt-4">
            <summary className="text-accent inline-flex min-h-11 cursor-pointer items-center text-sm font-medium underline underline-offset-2">
              {t('sensorsAll', { count: system.temperatures.length })}
            </summary>
            <div className="mt-2">
              <DataTable
                caption={t('sensorsCaption')}
                captionVisible
                columns={[
                  { key: 'sensor', header: t('colSensor'), cell: (row) => row.sensor },
                  {
                    key: 'celsius',
                    header: t('colCelsius'),
                    cell: (row) => `${row.celsius.toFixed(1)} °C`,
                  },
                  {
                    key: 'level',
                    header: t('colLevel'),
                    cell: (row) => (
                      <Chip tone={row.level === 'ok' ? 'success' : 'warning'}>
                        {levelLabel(row.level)}
                      </Chip>
                    ),
                  },
                ]}
                rows={system.temperatures}
                rowKey={(row) => row.sensor}
              />
            </div>
          </details>
        ) : null}
      </section>

      {/* -- traffic ---------------------------------------------------------------------- */}
      <section aria-labelledby="traffic" className="mb-10 scroll-mt-24">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <h2 id="traffic" className="text-primary text-lg font-bold">
            {t('trafficTitle')}
          </h2>
          <RangeLinks
            label={`${t('trafficTitle')} — ${t('rangeLabel')}`}
            name="t"
            current={trafficRange}
            options={TRAFFIC_RANGES.map((value) => ({ value, label: rangeLabels[value] }))}
            query={query}
            anchor="traffic"
          />
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StatTile
            label={t('requests')}
            value={count(totals.requests)}
            hint={t('requestsHint', {
              rpm: totals.requests_per_minute.toLocaleString(locale, { maximumFractionDigits: 1 }),
              peak: count(totals.peak_bucket_requests),
            })}
          />
          <StatTile
            label={t('successRate')}
            value={
              totals.success_rate === null ? none : formatRatio(totals.success_rate, locale, 2)
            }
            hint={t('successRateHint', {
              errors: count(totals.server_errors),
              client: count(totals.client_errors),
            })}
          />
          <Meter
            label={t('errorBudget', { target: formatRatio(budget.target, locale, 2) })}
            value={
              budget.consumed_ratio === null ? none : formatRatio(budget.consumed_ratio, locale, 0)
            }
            ratio={budget.consumed_ratio}
            level={budget.level}
            levelLabel={levelLabel(budget.level)}
            hint={
              budget.availability === null
                ? t('errorBudgetNone')
                : t('errorBudgetHint', {
                    allowed: budget.allowed_failures.toLocaleString(locale, {
                      maximumFractionDigits: 1,
                    }),
                    failures: count(budget.failures),
                    availability: formatRatio(budget.availability, locale, 3),
                  })
            }
          />
          <StatTile label={t('latencyP50')} value={formatMs(totals.p50_ms, locale)} />
          <StatTile
            label={t('latencyP95')}
            value={formatMs(totals.p95_ms, locale)}
            hint={t('latencyP95Hint', {
              p99: formatMs(totals.p99_ms, locale),
              max: formatMs(totals.max_ms, locale),
              mean: formatMs(totals.mean_ms, locale),
            })}
          />
          <StatTile
            label={t('apdex')}
            value={totals.apdex === null ? none : totals.apdex.toFixed(2)}
            hint={t('apdexHint')}
          />
        </div>

        <Card className="mt-4">
          <h3 className="text-primary mb-3 text-sm font-semibold">{t('chartRequests')}</h3>
          <BarChart
            label={t('chartRequests')}
            bars={traffic.series.map((bucket) => ({
              key: bucket.start,
              value: bucket.requests,
              part: bucket.server_errors,
              description: t('chartRequestsItem', {
                start: bucketLabel(bucket.start),
                requests: bucket.requests,
                errors: bucket.server_errors,
                p95: formatMs(bucket.p95_ms, locale),
              }),
            }))}
            from={bucketLabel(traffic.series[0]?.start ?? traffic.since)}
            to={bucketLabel(traffic.series[traffic.series.length - 1]?.start ?? traffic.since)}
          />
        </Card>

        <div className="mt-4 grid grid-cols-1 gap-6 xl:grid-cols-2">
          {(
            [
              ['busiest', t('routesBusiest'), traffic.busiest],
              ['slowest', t('routesSlowest'), traffic.slowest],
            ] as const
          ).map(([kind, title, rows]) => (
            <div key={kind}>
              <DataTable
                caption={title}
                captionVisible
                columns={routeColumns(kind)}
                rows={rows}
                rowKey={(row) => `${row.method} ${row.route}`}
                empty={
                  <Card>
                    <h3 className="text-primary text-sm font-semibold">{title}</h3>
                    <p className="text-muted mt-1 text-sm">{t('routesNone')}</p>
                  </Card>
                }
              />
            </div>
          ))}
        </div>
        {traffic.failing.length > 0 ? (
          <div className="mt-4">
            <DataTable
              caption={t('routesFailing')}
              captionVisible
              columns={routeColumns('failing')}
              rows={traffic.failing}
              rowKey={(row) => `${row.method} ${row.route}`}
            />
          </div>
        ) : null}
      </section>

      {/* -- failed requests -------------------------------------------------------------- */}
      <section aria-labelledby="errors" className="mb-10 scroll-mt-24">
        <h2 id="errors" className="text-primary mb-1 text-lg font-bold">
          {t('errorsTitle')}
        </h2>
        <p className="text-muted mb-1 max-w-3xl text-sm">{t('errorsHint')}</p>
        <p className="text-primary mb-3 text-sm font-medium" role="status">
          {t('errorsCount24h', { count: errors.total_24h })}
        </p>
        <DataTable
          caption={t('errorsCaption')}
          columns={errorColumns}
          rows={errors.items}
          rowKey={(row) => String(row.id)}
          empty={
            <Card>
              <p className="text-muted text-sm">{t('errorsNone')}</p>
            </Card>
          }
        />
        {errors.next_cursor ? (
          <p className="mt-4">
            <Link
              href={`${withQuery('/admin/monitoring', { ...query, cursor: errors.next_cursor })}#errors`}
              className="text-accent text-sm underline underline-offset-2"
            >
              {t('more')}
            </Link>
          </p>
        ) : null}
      </section>

      {/* -- visits ----------------------------------------------------------------------- */}
      <section aria-labelledby="visits" className="scroll-mt-24">
        <div className="mb-1 flex flex-wrap items-center justify-between gap-3">
          <h2 id="visits" className="text-primary text-lg font-bold">
            {t('visitsTitle')}
          </h2>
          <RangeLinks
            label={`${t('visitsTitle')} — ${t('rangeLabel')}`}
            name="v"
            current={visitRange}
            options={VISIT_RANGES.map((value) => ({ value, label: rangeLabels[value] }))}
            query={query}
            anchor="visits"
          />
        </div>
        <p className="text-muted mb-3 max-w-3xl text-sm">{t('visitsHint')}</p>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatTile
            label={t('views')}
            value={count(visits.totals.views)}
            hint={t('viewsHint', { today: count(visits.totals.views_today) })}
          />
          <StatTile
            label={t('visitorDays')}
            value={count(visits.totals.visitor_days)}
            hint={t('visitorDaysHint', { today: count(visits.totals.visitors_today) })}
          />
          <StatTile
            label={t('botViews')}
            value={count(visits.totals.bot_views)}
            hint={t('botViewsHint')}
          />
          <StatTile
            label={t('signedInShare')}
            value={
              visits.totals.signed_in_share === null
                ? none
                : formatRatio(visits.totals.signed_in_share, locale, 0)
            }
            hint={`${t('activeUsers')}: ${t('activeUsersValue', {
              week: visits.active_users_7d,
              month: visits.active_users_30d,
            })}`}
          />
        </div>

        <Card className="mt-4">
          <h3 className="text-primary mb-3 text-sm font-semibold">{t('chartVisits')}</h3>
          <BarChart
            label={t('chartVisits')}
            partTone="accent"
            bars={visits.series.map((day) => ({
              key: day.day,
              value: day.views,
              part: day.visitors,
              description: t('chartVisitsItem', {
                day: day.day,
                views: day.views,
                visitors: day.visitors,
                bots: day.bot_views,
              }),
            }))}
            from={visits.series[0]?.day ?? ''}
            to={visits.series[visits.series.length - 1]?.day ?? ''}
          />
        </Card>

        <div className="mt-4 grid grid-cols-1 gap-6 xl:grid-cols-2">
          <DataTable
            caption={t('topPages')}
            captionVisible
            columns={[
              {
                key: 'path',
                header: t('colPage'),
                cell: (row) =>
                  row.path.startsWith('/') ? (
                    <Link
                      href={row.path}
                      className="text-accent font-mono text-xs underline underline-offset-2"
                    >
                      {row.path}
                    </Link>
                  ) : (
                    <span className="text-muted text-sm">{t('otherPages')}</span>
                  ),
              },
              { key: 'views', header: t('colViews'), cell: (row) => count(row.views) },
            ]}
            rows={visits.top_pages}
            rowKey={(row) => row.path}
            empty={
              <Card>
                <h3 className="text-primary text-sm font-semibold">{t('topPages')}</h3>
                <p className="text-muted mt-1 text-sm">{t('topPagesNone')}</p>
              </Card>
            }
          />
          <div className="flex flex-col gap-6">
            <DataTable
              caption={t('referrers')}
              captionVisible
              columns={[
                { key: 'host', header: t('colReferrer'), cell: (row) => row.host },
                { key: 'visits', header: t('colVisits'), cell: (row) => count(row.visits) },
              ]}
              rows={visits.referrers}
              rowKey={(row) => row.host}
              empty={
                <Card>
                  <h3 className="text-primary text-sm font-semibold">{t('referrers')}</h3>
                  <p className="text-muted mt-1 text-sm">{t('referrersNone')}</p>
                </Card>
              }
            />
            {Object.keys(visits.by_locale).length > 0 ? (
              <Card>
                <h3 className="text-primary mb-2 text-sm font-semibold">{t('byLocale')}</h3>
                <dl className="flex flex-wrap gap-x-6 gap-y-1 text-sm">
                  {Object.entries(visits.by_locale)
                    .sort(([, a], [, b]) => b - a)
                    .map(([name, views]) => (
                      <div key={name} className="flex gap-2">
                        <dt className="text-muted">{name}</dt>
                        <dd className="text-primary font-semibold tabular-nums">{count(views)}</dd>
                      </div>
                    ))}
                </dl>
              </Card>
            ) : null}
          </div>
        </div>
      </section>
    </>
  )
}
