'use client'

import { useId } from 'react'

export interface SearchInputProps {
  label: string
  placeholder?: string
  value: string
  onChange: (value: string) => void
}

/** Labelled search box (never a placeholder-only label — WCAG 2.1 AA). */
export function SearchInput({ label, placeholder, value, onChange }: SearchInputProps) {
  const id = useId()
  return (
    <div className="flex w-full flex-col gap-1 sm:w-auto">
      <label htmlFor={id} className="text-muted text-xs font-medium">
        {label}
      </label>
      <input
        id={id}
        type="search"
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        className="bg-surface border-border-default text-primary placeholder:text-muted min-h-11 w-full rounded-lg border px-3 py-2 text-base sm:w-64 sm:text-sm"
      />
    </div>
  )
}
