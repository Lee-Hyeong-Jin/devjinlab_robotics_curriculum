import type { LockState } from '@/lib/api/types'
import { cx } from '@/lib/cx'

/** Figma `10-2`/`10-3`/`10-4`/`10-5`. */
const DOT_CLASS: Record<LockState, string> = {
  done: 'bg-state-done',
  in_progress: 'bg-state-in-progress',
  available: 'bg-state-available',
  locked: 'bg-state-locked',
}

export interface StatusDotProps {
  state: LockState
  /** Visible label next to the dot. State is never conveyed by colour alone (§6). */
  label: string
  /** Hide the label visually but keep it for assistive tech. */
  labelHidden?: boolean
  className?: string
}

export function StatusDot({ state, label, labelHidden = false, className }: StatusDotProps) {
  return (
    <span className={cx('inline-flex items-center gap-2', className)}>
      <span
        aria-hidden="true"
        data-state={state}
        className={cx('inline-block size-2.5 shrink-0 rounded-full', DOT_CLASS[state])}
      />
      <span className={cx('text-sm', labelHidden && 'sr-only')}>
        {state === 'locked' && !labelHidden ? `🔒 ${label}` : label}
      </span>
    </span>
  )
}
