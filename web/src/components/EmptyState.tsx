import type { ReactNode } from 'react'

import { Card } from './Card'

export interface EmptyStateProps {
  title: string
  body?: string
  action?: ReactNode
}

export function EmptyState({ title, body, action }: EmptyStateProps) {
  return (
    <Card className="flex flex-col items-center gap-2 py-10 text-center">
      <p className="text-primary font-medium">{title}</p>
      {body ? <p className="text-muted max-w-md text-sm">{body}</p> : null}
      {action ? <div className="mt-2">{action}</div> : null}
    </Card>
  )
}
