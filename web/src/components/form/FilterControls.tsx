import { useId, type InputHTMLAttributes } from 'react'

import { cx } from '@/lib/cx'

const CONTROL =
  'bg-surface border-border-default text-primary placeholder:text-muted min-h-11 w-full rounded-lg border px-3 py-2 text-base sm:text-sm'

/**
 * Controls for a filter form that submits with GET.
 *
 * The filters live in the URL, so a filtered list can be bookmarked, shared with a colleague
 * and paged with plain links — and the form works before any script has loaded.
 */
export function FilterInput({
  label,
  className,
  ...rest
}: { label: string } & Omit<InputHTMLAttributes<HTMLInputElement>, 'id'>) {
  const id = useId()
  return (
    <div className={cx('flex min-w-0 flex-col gap-1', className)}>
      <label htmlFor={id} className="text-muted text-xs font-medium">
        {label}
      </label>
      <input id={id} className={CONTROL} {...rest} />
    </div>
  )
}

export interface FilterSelectProps {
  label: string
  name: string
  value: string
  options: ReadonlyArray<{ value: string; label: string }>
  className?: string
}

export function FilterSelect({ label, name, value, options, className }: FilterSelectProps) {
  const id = useId()
  return (
    <div className={cx('flex min-w-0 flex-col gap-1', className)}>
      <label htmlFor={id} className="text-muted text-xs font-medium">
        {label}
      </label>
      <select id={id} name={name} defaultValue={value} className={CONTROL}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  )
}
