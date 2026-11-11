import Link from 'next/link'

import type { LockState } from '@/lib/progress'
import { cx } from '@/lib/cx'

import { StatusDot } from './StatusDot'

/** Figma `10-58`. A lesson in a module overview or the lesson sidebar. */
export interface LessonRowProps {
  moduleId: string
  lessonId: string
  title: string
  state: LockState
  stateLabel: string
  /** e.g. "예상 40분". */
  meta?: string | null
  /** Mark the row the reader is currently on (lesson sidebar). */
  current?: boolean
}

export function LessonRow({
  moduleId,
  lessonId,
  title,
  state,
  stateLabel,
  meta,
  current = false,
}: LessonRowProps) {
  const locked = state === 'locked'
  const inner = (
    <>
      <StatusDot state={state} label={stateLabel} labelHidden />
      <span className="min-w-0 flex-1">
        <span className="text-primary block truncate text-sm font-medium">{title}</span>
        <span className="text-muted block font-mono text-xs">{lessonId}</span>
      </span>
      <span className="text-muted shrink-0 text-xs">{stateLabel}</span>
      {meta ? <span className="text-muted hidden shrink-0 text-xs sm:inline">{meta}</span> : null}
    </>
  )
  const base = 'flex items-center gap-3 rounded-lg px-3 py-2.5 text-left'
  if (locked) {
    return (
      <li className={cx(base, 'bg-subtle')} data-locked="true">
        {inner}
      </li>
    )
  }
  return (
    <li>
      <Link
        href={`/modules/${moduleId}/${lessonId}`}
        aria-current={current ? 'page' : undefined}
        className={cx(
          base,
          'hover:bg-subtle w-full transition-colors',
          current && 'bg-accent-light',
        )}
      >
        {inner}
      </Link>
    </li>
  )
}
