import { percentValue } from '@/lib/format'
import { cx } from '@/lib/cx'

/**
 * Figma `10-34`. Takes a 0–1 ratio.
 *
 * In Figma the bar is a detached frame per state (plugin API limitation); in code
 * it is this single component (frontend.md §4).
 */
export interface ProgressBarProps {
  /** 0–1. */
  value: number | undefined
  /** Accessible name — required, since the bar carries meaning. */
  label: string
  /** Show the percentage as text beside the bar. */
  showValue?: boolean
  className?: string
}

export function ProgressBar({ value, label, showValue = false, className }: ProgressBarProps) {
  const percent = percentValue(value)
  return (
    <div className={cx('flex items-center gap-3', className)}>
      <div
        role="progressbar"
        aria-label={label}
        aria-valuenow={percent}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuetext={`${percent}%`}
        className="bg-track h-2 w-full overflow-hidden rounded-full"
      >
        <div
          className="bg-accent-solid h-full rounded-full"
          style={{ width: `${percent}%` }}
          aria-hidden="true"
        />
      </div>
      {showValue ? (
        <span className="text-muted w-10 shrink-0 text-right text-xs tabular-nums">{percent}%</span>
      ) : null}
    </div>
  )
}
