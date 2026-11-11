import type { ReactNode } from 'react'

/** Figma `10-64`. One numbered step of the lesson's "이 단계 공부법" card. */
export interface StudyStepProps {
  n: number
  action: string
  children?: ReactNode
}

export function StudyStep({ n, action, children }: StudyStepProps) {
  return (
    <li className="flex gap-3">
      <span
        aria-hidden="true"
        className="bg-accent-solid text-on-accent mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full text-xs font-bold"
      >
        {n}
      </span>
      <span className="min-w-0">
        <span className="text-primary block text-sm font-semibold">{action}</span>
        {children ? <span className="text-muted block text-sm">{children}</span> : null}
      </span>
    </li>
  )
}
