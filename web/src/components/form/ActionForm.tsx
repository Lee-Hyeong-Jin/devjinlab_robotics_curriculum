'use client'

import { useActionState, useId } from 'react'

import { EMPTY_ACTION_STATE, type ActionState } from '@/lib/actions/result'
import { cx } from '@/lib/cx'

import { Field } from './Field'
import { FormMessage } from './FormMessage'
import { SubmitButton } from './SubmitButton'
import type { FieldSpec } from './spec'

export interface ActionFormProps {
  action: (previous: ActionState, form: FormData) => Promise<ActionState>
  fields: FieldSpec[]
  submitLabel: string
  pendingLabel: string
  /** Hidden values submitted with the form (ids, the post-login path, …). */
  hidden?: Record<string, string>
  /** Shown before the first submit, e.g. "가입이 완료됐습니다". */
  notice?: string
  className?: string
}

/**
 * A form bound to a Server Action. Renders the fields from their specs and the
 * action's form-level and per-field messages.
 */
export function ActionForm({
  action,
  fields,
  submitLabel,
  pendingLabel,
  hidden,
  notice,
  className,
}: ActionFormProps) {
  const [state, formAction] = useActionState(action, EMPTY_ACTION_STATE)
  const prefix = useId()

  return (
    <form action={formAction} className={cx('flex flex-col gap-4', className)} noValidate>
      {Object.entries(hidden ?? {}).map(([name, value]) => (
        <input key={name} type="hidden" name={name} value={value} />
      ))}
      {notice && !state.error && !state.message ? (
        <FormMessage tone="success">{notice}</FormMessage>
      ) : null}
      {state.error ? <FormMessage tone="error">{state.error}</FormMessage> : null}
      {state.message ? <FormMessage tone="success">{state.message}</FormMessage> : null}

      {fields.map((field) => {
        const error = state.fields?.[field.name]
        const id = `${prefix}-${field.name}`

        if (field.kind === 'checkbox') {
          return (
            <label key={field.name} className="text-primary flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                name={field.name}
                defaultChecked={field.defaultValue === 'on'}
                className="border-border-default size-4 rounded"
              />
              {field.label}
            </label>
          )
        }

        if (field.kind === 'select') {
          return (
            <div key={field.name} className="flex flex-col gap-1.5">
              <label htmlFor={id} className="text-primary text-sm font-medium">
                {field.label}
              </label>
              <select
                id={id}
                name={field.name}
                defaultValue={field.defaultValue}
                aria-invalid={error ? true : undefined}
                aria-describedby={error ? `${id}-error` : undefined}
                className="bg-surface border-border-default text-primary w-full rounded-lg border px-3 py-2 text-sm"
              >
                {(field.options ?? []).map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              {field.hint ? <p className="text-muted text-xs">{field.hint}</p> : null}
              {error ? (
                <p id={`${id}-error`} className="text-danger text-xs">
                  {error}
                </p>
              ) : null}
            </div>
          )
        }

        if (field.kind === 'checkboxGroup') {
          return (
            <fieldset key={field.name} className="flex flex-col gap-1.5">
              <legend className="text-primary text-sm font-medium">{field.label}</legend>
              {(field.options ?? []).map((option) => (
                <label key={option.value} className="text-primary flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    name={`${field.name}:${option.value}`}
                    className="border-border-default size-4 rounded"
                  />
                  {option.mono ? (
                    <code className="font-mono text-xs">{option.label}</code>
                  ) : (
                    option.label
                  )}
                </label>
              ))}
              {field.hint ? <p className="text-muted text-xs">{field.hint}</p> : null}
              {error ? (
                <p role="alert" className="text-danger text-xs">
                  {error}
                </p>
              ) : null}
            </fieldset>
          )
        }

        return (
          <Field
            key={field.name}
            label={field.label}
            name={field.name}
            type={field.kind ?? 'text'}
            defaultValue={field.defaultValue}
            required={field.required}
            autoComplete={field.autoComplete}
            minLength={field.minLength}
            min={field.min}
            max={field.max}
            placeholder={field.placeholder}
            hint={field.hint}
            error={error}
          />
        )
      })}

      <SubmitButton pendingLabel={pendingLabel}>{submitLabel}</SubmitButton>
    </form>
  )
}
