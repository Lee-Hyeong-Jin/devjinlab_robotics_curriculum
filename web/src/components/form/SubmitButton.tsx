'use client'

import { useFormStatus } from 'react-dom'

import { Button, type ButtonKind } from '../Button'

export interface SubmitButtonProps {
  children: string
  /** Label while the action is running; also announced via `aria-busy`. */
  pendingLabel: string
  kind?: ButtonKind
  className?: string
  /** Set by a form that dispatches its action itself, where `useFormStatus` sees nothing. */
  pending?: boolean
}

/** Submit button that disables itself while its form's action is in flight. */
export function SubmitButton({
  children,
  pendingLabel,
  kind = 'primary',
  className,
  pending: pendingProp,
}: SubmitButtonProps) {
  const status = useFormStatus()
  const pending = pendingProp ?? status.pending
  return (
    <Button
      type="submit"
      kind={kind}
      disabled={pending}
      aria-busy={pending || undefined}
      className={className}
    >
      {pending ? pendingLabel : children}
    </Button>
  )
}
