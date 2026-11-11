'use client'

import { useEffect, useState } from 'react'

import { cx } from '@/lib/cx'
import { THEME_STORAGE_KEY, applyTheme, readStoredTheme, type Theme } from '@/lib/theme'

const ORDER: Theme[] = ['system', 'light', 'dark']

export interface ThemeToggleProps {
  labels: Record<Theme, string>
  groupLabel: string
}

/**
 * Theme switch: writes `<html data-theme>` and `localStorage`, defaulting to the
 * system setting (frontend.md §3).
 */
export function ThemeToggle({ labels, groupLabel }: ThemeToggleProps) {
  const [theme, setTheme] = useState<Theme>('system')
  const [ready, setReady] = useState(false)

  useEffect(() => {
    setTheme(readStoredTheme())
    setReady(true)
  }, [])

  function choose(next: Theme) {
    setTheme(next)
    applyTheme(next)
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, next)
    } catch {
      // Private mode or blocked storage: the choice still applies for this page.
    }
  }

  return (
    <div
      role="group"
      aria-label={groupLabel}
      className="bg-subtle flex items-center gap-0.5 rounded-lg p-0.5"
    >
      {ORDER.map((option) => (
        <button
          key={option}
          type="button"
          aria-pressed={ready ? theme === option : undefined}
          onClick={() => choose(option)}
          className={cx(
            'rounded-md px-2 py-1 text-xs font-medium transition-colors',
            ready && theme === option ? 'bg-surface text-primary' : 'text-muted hover:text-primary',
          )}
        >
          {labels[option]}
        </button>
      ))}
    </div>
  )
}
