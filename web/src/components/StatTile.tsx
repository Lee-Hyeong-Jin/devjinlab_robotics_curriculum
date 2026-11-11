import type { ReactNode } from 'react'

import { Card } from './Card'

/** Figma `10-37`. One number with its label; `hint` carries the secondary line. */
export interface StatTileProps {
  label: string
  value: ReactNode
  hint?: ReactNode
  /** Rendered when the backend does not expose the value yet (frontend.md §2). */
  pending?: boolean
  pendingLabel?: string
}

export function StatTile({ label, value, hint, pending = false, pendingLabel }: StatTileProps) {
  return (
    <Card className="flex flex-col gap-1">
      <span className="text-muted text-xs font-medium tracking-wide uppercase">{label}</span>
      {pending ? (
        <>
          <span
            className="bg-subtle mt-1 h-7 w-20 animate-pulse rounded"
            aria-hidden="true"
            data-testid="stat-skeleton"
          />
          <span className="text-muted mt-1 text-xs">{pendingLabel}</span>
        </>
      ) : (
        <>
          <span className="text-primary text-2xl font-semibold tabular-nums">{value}</span>
          {hint ? <span className="text-muted text-xs">{hint}</span> : null}
        </>
      )}
    </Card>
  )
}
