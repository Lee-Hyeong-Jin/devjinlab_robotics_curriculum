export interface Bar {
  key: string
  /** Height of the bar. */
  value: number
  /** A part of `value` drawn darker at the bottom (errors among requests, visitors among views). */
  part?: number
  /** Read by assistive tech and shown as the tooltip: the same numbers the bar draws. */
  description: string
}

export interface BarChartProps {
  label: string
  bars: readonly Bar[]
  /** Text under the first and the last bar. */
  from: string
  to: string
  /** Colour of the darker part: `danger` for something bad, `accent` for a subset. */
  partTone?: 'danger' | 'accent'
}

/**
 * A row of bars, one per interval.
 *
 * The chart is a list: each bar is an item whose text is the interval and its numbers, so a
 * screen reader gets the same data the picture shows and no separate table is needed
 * (AC-A11Y.3). Heights are relative to the tallest bar.
 */
export function BarChart({ label, bars, from, to, partTone = 'danger' }: BarChartProps) {
  const peak = Math.max(1, ...bars.map((bar) => bar.value))
  return (
    <div>
      <ol aria-label={label} className="flex h-32 items-end gap-px sm:gap-0.5">
        {bars.map((bar) => {
          const height = bar.value > 0 ? Math.max(3, Math.round((bar.value / peak) * 100)) : 2
          const part =
            bar.part && bar.value > 0 ? Math.min(100, Math.round((bar.part / bar.value) * 100)) : 0
          return (
            <li key={bar.key} className="flex h-full min-w-0 flex-1 flex-col justify-end">
              <span className="sr-only">{bar.description}</span>
              <span
                aria-hidden="true"
                title={bar.description}
                className={
                  bar.value > 0
                    ? 'bg-border-accent flex flex-col justify-end overflow-hidden rounded-t opacity-70'
                    : 'bg-track rounded-t'
                }
                style={{ height: `${height}%` }}
              >
                {part > 0 ? (
                  <span
                    className={partTone === 'danger' ? 'bg-danger' : 'bg-accent-solid'}
                    style={{ height: `${Math.max(part, 8)}%` }}
                  />
                ) : null}
              </span>
            </li>
          )
        })}
      </ol>
      <p className="text-muted mt-2 flex justify-between text-xs" aria-hidden="true">
        <span>{from}</span>
        <span>{to}</span>
      </p>
    </div>
  )
}
