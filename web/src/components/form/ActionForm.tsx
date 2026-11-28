'use client'

import { useActionState, useEffect, useId, useRef, useTransition, type FormEvent } from 'react'

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
  const [state, formAction, actionPending] = useActionState(action, EMPTY_ACTION_STATE)
  const [transitionPending, startTransition] = useTransition()
  const pending = actionPending || transitionPending
  const prefix = useId()
  const formRef = useRef<HTMLFormElement>(null)

  // React clears an uncontrolled form once its action has run, whatever the outcome. After a
  // refusal that throws away everything the reader typed (QA B-11), so the action is
  // dispatched by hand, which leaves the fields alone, and the form is cleared here only when
  // the action succeeded. Without JavaScript the form still posts through `action`.
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const submitter = (event.nativeEvent as SubmitEvent).submitter
    const data = new FormData(event.currentTarget, submitter)
    startTransition(() => formAction(data))
  }

  useEffect(() => {
    const form = formRef.current
    if (!form || state === EMPTY_ACTION_STATE) return
    const failed = Boolean(state.error) || Object.keys(state.fields ?? {}).length > 0
    if (!failed) {
      form.reset()
      return
    }
    // A password is typed again after a refusal; everything else stays.
    for (const input of form.querySelectorAll<HTMLInputElement>('input[type="password"]')) {
      input.value = ''
    }
    // Move to the first field that was refused, so a keyboard or screen-reader user lands on it.
    form.querySelector<HTMLElement>('[aria-invalid="true"]')?.focus()
  }, [state])

  return (
    <form
      ref={formRef}
      action={formAction}
      onSubmit={submit}
      className={cx('flex flex-col gap-4', className)}
      noValidate
    >
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
            <div key={field.name} className="flex flex-col gap-1">
              <label className="text-primary flex min-h-11 cursor-pointer items-center gap-3 text-sm">
                <input
                  type="checkbox"
                  name={field.name}
                  defaultChecked={field.defaultValue === 'on'}
                  aria-invalid={error ? true : undefined}
                  aria-describedby={error ? `${id}-error` : undefined}
                  className="border-border-default size-5 shrink-0 rounded"
                />
                {field.label}
              </label>
              {error ? (
                <p id={`${id}-error`} role="alert" className="text-danger text-xs">
                  {error}
                </p>
              ) : null}
            </div>
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
                className="bg-surface border-border-default text-primary min-h-11 w-full rounded-lg border px-3 py-2 text-base sm:text-sm"
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
                <label
                  key={option.value}
                  className="text-primary flex min-h-11 cursor-pointer items-center gap-3 text-sm"
                >
                  <input
                    type="checkbox"
                    name={`${field.name}:${option.value}`}
                    aria-invalid={error ? true : undefined}
                    className="border-border-default size-5 shrink-0 rounded"
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

      <SubmitButton pendingLabel={pendingLabel} pending={pending}>
        {submitLabel}
      </SubmitButton>
    </form>
  )
}
