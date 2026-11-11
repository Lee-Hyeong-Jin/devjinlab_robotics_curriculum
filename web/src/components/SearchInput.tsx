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
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-muted text-xs font-medium">
        {label}
      </label>
      <input
        id={id}
        type="search"
        value={value}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        className="bg-surface border-border-default text-primary placeholder:text-muted w-full rounded-lg border px-3 py-2 text-sm sm:w-64"
      />
    </div>
  )
}
