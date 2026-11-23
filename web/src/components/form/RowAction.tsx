'use client'

import { useActionState, useEffect } from 'react'

import { EMPTY_ACTION_STATE, type ActionState } from '@/lib/actions/result'

import { flash } from '../Flash'
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
  // Said in the page-level region as well: a successful action often removes this very form
  // (the row is gone, "stop" became "start"), and its own message with it.
  useEffect(() => {
    if (state.message && !state.error) flash(state.message)
  }, [state])
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
      {/* An action whose effect is not visible in the row (a mail was sent, tokens were
          revoked) has to say that it happened. */}
      {state.message && !state.error ? (
        <p role="status" className="text-success text-xs">
          {state.message}
        </p>
      ) : null}
    </form>
  )
}
