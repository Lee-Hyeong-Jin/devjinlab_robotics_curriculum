'use client'

import { useId, type InputHTMLAttributes, type ReactNode } from 'react'

import { cx } from '@/lib/cx'

export interface FieldProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label: string
  name: string
  /** Validation message for this field; also sets `aria-invalid`. */
  error?: string
  /** Help text rendered under the input and referenced by `aria-describedby`. */
  hint?: ReactNode
}

/**
 * A labelled text input. Every field has a real `<label>`; the error and hint are
 * wired through `aria-describedby` so a screen reader reads them with the input
 * (WCAG 2.1 AA, frontend.md §6).
 */
export function Field({ label, name, error, hint, className, ...rest }: FieldProps) {
  const id = useId()
  const errorId = `${id}-error`
  const hintId = `${id}-hint`
  const describedBy = [error ? errorId : null, hint ? hintId : null].filter(Boolean).join(' ')

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-primary text-sm font-medium">
        {label}
        {rest.required ? (
          <span className="text-danger ml-1" aria-hidden="true">
            *
          </span>
        ) : null}
      </label>
      <input
        id={id}
        name={name}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy || undefined}
        className={cx(
          'bg-surface text-primary placeholder:text-muted w-full rounded-lg border px-3 py-2 text-sm',
          error ? 'border-danger' : 'border-border-default',
          className,
        )}
        {...rest}
      />
      {hint ? (
        <p id={hintId} className="text-muted text-xs">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} className="text-danger text-xs">
          {error}
        </p>
      ) : null}
    </div>
  )
}
