import type { ReactNode } from 'react'

import type { MonitoringLevel } from '@/lib/api/types'
import { cx } from '@/lib/cx'
import { percentValue } from '@/lib/format'

import { Card } from '../Card'
import { Chip } from '../Chip'

const BAR: Record<MonitoringLevel, string> = {
  ok: 'bg-accent-solid',
  warning: 'bg-state-in-progress',
  critical: 'bg-danger',
}
const TONE = { ok: 'success', warning: 'warning', critical: 'warning' } as const

export interface MeterProps {
  label: string
  /** The reading as text ("72%", "44 °C"). */
  value: ReactNode
  /** 0–1 to draw as a bar; omit for a reading that has no "full". */
  ratio?: number | null
  level: MonitoringLevel
  /** The level in words: a reading's state is never shown by colour alone. */
  levelLabel: string
  hint?: ReactNode
}

/** One reading with its state: a figure, an optional bar and a second line of detail. */
export function Meter({ label, value, ratio, level, levelLabel, hint }: MeterProps) {
  const percent = ratio === null || ratio === undefined ? null : percentValue(ratio)
  return (
    <Card className="flex flex-col gap-2">
      <div className="flex items-start justify-between gap-2">
        <span className="text-muted text-xs font-medium tracking-wide uppercase">{label}</span>
        <Chip tone={TONE[level]}>{levelLabel}</Chip>
      </div>
      <span
        className={cx(
          'text-2xl font-semibold tabular-nums',
          level === 'critical' ? 'text-danger' : 'text-primary',
        )}
      >
        {value}
      </span>
      {percent !== null ? (
        <div
          role="progressbar"
          aria-label={label}
          aria-valuenow={percent}
          aria-valuemin={0}
          aria-valuemax={100}
          className="bg-track h-2 w-full overflow-hidden rounded-full"
        >
          <div className={cx('h-full rounded-full', BAR[level])} style={{ width: `${percent}%` }} />
        </div>
      ) : null}
      {hint ? <span className="text-muted text-xs wrap-anywhere">{hint}</span> : null}
    </Card>
  )
}
