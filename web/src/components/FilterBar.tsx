'use client'

import { useId } from 'react'

import { cx } from '@/lib/cx'

export interface FilterOption {
  value: string
  label: string
  count?: number
}

export interface FilterBarProps {
  label: string
  options: readonly FilterOption[]
  value: string
  onChange: (value: string) => void
}

/** Radio-group filter: keyboard reachable, state announced via `aria-checked`. */
export function FilterBar({ label, options, value, onChange }: FilterBarProps) {
  const name = useId()
  return (
    <fieldset className="flex flex-col gap-1">
      <legend className="text-muted text-xs font-medium">{label}</legend>
      <div className="flex flex-wrap gap-1.5">
        {options.map((option) => {
          const selected = option.value === value
          return (
            <label
              key={option.value}
              className={cx(
                'cursor-pointer rounded-full border px-3 py-1 text-xs font-medium transition-colors',
                selected
                  ? 'bg-accent-light text-accent border-border-accent'
                  : 'bg-surface text-muted border-border-default hover:bg-subtle',
              )}
            >
              <input
                type="radio"
                name={name}
                value={option.value}
                checked={selected}
                onChange={() => onChange(option.value)}
                className="sr-only"
              />
              {option.label}
              {option.count === undefined ? null : (
                <span className="ml-1 tabular-nums opacity-70">{option.count}</span>
              )}
            </label>
          )
        })}
      </div>
    </fieldset>
  )
}
