import type { ReactNode } from 'react'

export interface PageHeaderProps {
  title: string
  subtitle?: string
  /** Breadcrumb or back link, rendered above the title. */
  eyebrow?: ReactNode
  /** Actions aligned to the right of the title row. */
  actions?: ReactNode
}

export function PageHeader({ title, subtitle, eyebrow, actions }: PageHeaderProps) {
  return (
    <div className="mb-6 flex flex-col gap-2">
      {eyebrow ? <div className="text-muted text-sm">{eyebrow}</div> : null}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <h1 className="text-primary text-2xl font-bold tracking-tight">{title}</h1>
        {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
      </div>
      {subtitle ? <p className="text-muted max-w-2xl text-sm">{subtitle}</p> : null}
    </div>
  )
}
