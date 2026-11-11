'use client'

import { useActionState } from 'react'

import { EMPTY_ACTION_STATE, type ActionState } from '@/lib/actions/result'

import { SubmitButton } from './SubmitButton'

export interface RowActionProps {
  action: (previous: ActionState, form: FormData) => Promise<ActionState>
  hidden: Record<string, string>
  label: string
  pendingLabel: string
  /** Confirmation text; the action does not run unless the reader confirms. */
  confirm?: string
}

/**
 * A one-button form for a table row (revoke a session, unlink an identity…).
 * The error is rendered next to the row rather than at the top of the page.
 */
export function RowAction({ action, hidden, label, pendingLabel, confirm }: RowActionProps) {
  const [state, formAction] = useActionState(action, EMPTY_ACTION_STATE)
  return (
    <form
      action={formAction}
      onSubmit={(event) => {
        if (confirm && !window.confirm(confirm)) event.preventDefault()
      }}
      className="flex flex-col items-start gap-1"
    >
      {Object.entries(hidden).map(([name, value]) => (
        <input key={name} type="hidden" name={name} value={value} />
      ))}
      <SubmitButton kind="secondary" pendingLabel={pendingLabel}>
        {label}
      </SubmitButton>
      {state.error ? (
        <p role="alert" className="text-danger text-xs">
          {state.error}
        </p>
      ) : null}
    </form>
  )
}
