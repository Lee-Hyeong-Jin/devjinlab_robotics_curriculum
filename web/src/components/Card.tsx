import type { ElementType, ReactNode } from 'react'

import { cx } from '@/lib/cx'

export interface CardProps {
  children: ReactNode
  className?: string
  as?: ElementType
}

/** Surface container: 12px radius, 1px border, token background (frontend.md §3). */
export function Card({ children, className, as: Tag = 'div' }: CardProps) {
  return (
    <Tag
      className={cx(
        'bg-surface border-border-default rounded-[var(--radius-card)] border p-5',
        className,
      )}
    >
      {children}
    </Tag>
  )
}
