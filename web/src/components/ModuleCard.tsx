import Link from 'next/link'

import type { LockState } from '@/lib/progress'
import { formatPercent } from '@/lib/format'

import { Card } from './Card'
import { Chip } from './Chip'
import { ProgressBar } from './ProgressBar'
import { StatusDot } from './StatusDot'

/** Figma `10-42`. One module on the roadmap. */
export interface ModuleCardProps {
  id: string
  title: string
  state: LockState
  /** 0–1. */
  progress: number | null | undefined
  lessonsTotal: number
  lessonsDone: number
  /** Stage chip, already translated (e.g. "Foundation"). */
  level?: string | null
  stateLabel: string
  lessonsLabel: string
  progressLabel: string
}

export function ModuleCard({
  id,
  title,
  state,
  progress,
  lessonsTotal,
  lessonsDone,
  level,
  stateLabel,
  lessonsLabel,
  progressLabel,
}: ModuleCardProps) {
  const body = (
    <>
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-primary font-semibold">{title}</h3>
        {level ? <Chip tone="neutral">{level}</Chip> : null}
      </div>
      <p className="text-muted font-mono text-xs">{id}</p>
      <div className="mt-3 flex items-center justify-between gap-3">
        <StatusDot state={state} label={stateLabel} />
        <span className="text-muted text-xs">{lessonsLabel}</span>
      </div>
      <ProgressBar
        className="mt-3"
        value={progress}
        label={`${title} — ${progressLabel} ${formatPercent(progress)}`}
        showValue
      />
      <span className="sr-only">{`${lessonsDone}/${lessonsTotal}`}</span>
    </>
  )

  // Always a link: no module is gated on finishing another (ADR 0015).
  return (
    <Card className="hover:border-border-accent focus-within:border-border-accent transition-colors">
      <Link href={`/modules/${id}`} className="block">
        {body}
      </Link>
    </Card>
  )
}
