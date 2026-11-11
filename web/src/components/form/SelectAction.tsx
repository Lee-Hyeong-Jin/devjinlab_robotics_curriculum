'use client'

import { useActionState, useId } from 'react'

import { EMPTY_ACTION_STATE, type ActionState } from '@/lib/actions/result'

import { SubmitButton } from './SubmitButton'

export interface SelectField {
  name: string
  label: string
  value: string
  options: Array<{ value: string; label: string }>
}

export interface SelectActionProps {
  action: (previous: ActionState, form: FormData) => Promise<ActionState>
  hidden: Record<string, string>
  selects: SelectField[]
  label: string
  pendingLabel: string
}

/** A row form with one or more selects and an apply button (admin tables). */
export function SelectAction({ action, hidden, selects, label, pendingLabel }: SelectActionProps) {
  const [state, formAction] = useActionState(action, EMPTY_ACTION_STATE)
  const prefix = useId()

  return (
    <form action={formAction} className="flex flex-wrap items-end gap-2">
      {Object.entries(hidden).map(([name, value]) => (
        <input key={name} type="hidden" name={name} value={value} />
      ))}
      {selects.map((select) => (
        <div key={select.name} className="flex flex-col gap-1">
          <label htmlFor={`${prefix}-${select.name}`} className="text-muted text-xs font-medium">
            {select.label}
          </label>
          <select
            id={`${prefix}-${select.name}`}
            name={select.name}
            defaultValue={select.value}
            className="bg-surface border-border-default text-primary rounded-lg border px-2 py-1.5 text-sm"
          >
            {select.options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      ))}
      <SubmitButton kind="secondary" pendingLabel={pendingLabel}>
        {label}
      </SubmitButton>
      {state.error ? (
        <p role="alert" className="text-danger basis-full text-xs">
          {state.error}
        </p>
      ) : null}
      {state.message ? (
        <p role="status" className="text-success basis-full text-xs">
          {state.message}
        </p>
      ) : null}
    </form>
  )
}
