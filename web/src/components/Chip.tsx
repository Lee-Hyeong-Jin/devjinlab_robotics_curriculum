import type { ReactNode } from 'react'

import { cx } from '@/lib/cx'

/** Figma `10-8`…`10-16`. */
export type ChipTone = 'neutral' | 'accent' | 'warning' | 'success' | 'locked'

const TONE_CLASS: Record<ChipTone, string> = {
  neutral: 'bg-subtle text-muted border-border-default',
  accent: 'bg-accent-light text-accent border-border-accent',
  warning: 'bg-warning-light text-warning border-warning-light',
  success: 'bg-success-light text-success border-success-light',
  locked: 'bg-subtle text-muted border-state-locked',
}

export interface ChipProps {
  tone?: ChipTone
  children: ReactNode
  className?: string
}

export function Chip({ tone = 'neutral', children, className }: ChipProps) {
  return (
    <span
      className={cx(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium whitespace-nowrap',
        TONE_CLASS[tone],
        className,
      )}
    >
      {children}
    </span>
  )
}
