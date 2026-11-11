import { cx } from '@/lib/cx'

export interface FormMessageProps {
  tone: 'error' | 'success'
  children: string
}

/**
 * Form-level feedback. `role="alert"` so it is announced when it appears, and
 * the tone is carried by an icon and wording, not only by colour (§6).
 */
export function FormMessage({ tone, children }: FormMessageProps) {
  const error = tone === 'error'
  return (
    <p
      role="alert"
      className={cx(
        'flex items-start gap-2 rounded-lg border px-3 py-2 text-sm',
        error
          ? 'border-danger bg-warning-light text-warning'
          : 'border-border-accent bg-success-light text-success',
      )}
    >
      <span aria-hidden="true">{error ? '⚠' : '✓'}</span>
      <span>{children}</span>
    </p>
  )
}
