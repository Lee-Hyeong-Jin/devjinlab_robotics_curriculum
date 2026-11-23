'use client'

import { useActionState, useCallback } from 'react'

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
  // Said in the page-level region as well, and from the action's own result rather than from
  // an effect: a successful action often removes this very form in the same render (the row is
  // gone, "stop" became "start"), so nothing mounted here ever sees the new state.
  const announced = useCallback(
    async (previous: ActionState, form: FormData) => {
      const result = await action(previous, form)
      if (result.message && !result.error) flash(result.message)
      return result
    },
    [action],
  )
  const [state, formAction] = useActionState(announced, EMPTY_ACTION_STATE)
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
      {/* Success is said once, in the page-level region (`<Flash>`): this form may not
          survive the action that it ran. */}
    </form>
  )
}
