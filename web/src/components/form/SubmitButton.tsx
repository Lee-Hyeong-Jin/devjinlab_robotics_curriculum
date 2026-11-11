'use client'

import { useFormStatus } from 'react-dom'

import { Button, type ButtonKind } from '../Button'

export interface SubmitButtonProps {
  children: string
  /** Label while the action is running; also announced via `aria-busy`. */
  pendingLabel: string
  kind?: ButtonKind
  className?: string
}

/** Submit button that disables itself while its form's action is in flight. */
export function SubmitButton({
  children,
  pendingLabel,
  kind = 'primary',
  className,
}: SubmitButtonProps) {
  const { pending } = useFormStatus()
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
