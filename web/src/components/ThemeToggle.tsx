'use client'

import { useSyncExternalStore } from 'react'

import { cx } from '@/lib/cx'
import {
  THEME_EVENT,
  THEME_STORAGE_KEY,
  applyTheme,
  readStoredTheme,
  subscribeToTheme,
  type Theme,
} from '@/lib/theme'

const ORDER: Theme[] = ['system', 'light', 'dark']

export interface ThemeToggleProps {
  labels: Record<Theme, string>
  groupLabel: string
}

/**
 * Theme switch: writes `<html data-theme>` and `localStorage`, defaulting to the
 * system setting (frontend.md §3).
 *
 * `localStorage` is an external store, so it is read with
 * `useSyncExternalStore` — that keeps the server render (`system`) and the
 * client in step without a state-setting effect, and picks up a change made in
 * another tab.
 */
export function ThemeToggle({ labels, groupLabel }: ThemeToggleProps) {
  const theme = useSyncExternalStore(
    subscribeToTheme,
    readStoredTheme,
    // The server has no storage; it always renders the system default.
    () => 'system' as Theme,
  )

  function choose(next: Theme) {
    applyTheme(next)
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, next)
    } catch {
      // Private mode or blocked storage: the choice still applies for this page.
    }
    window.dispatchEvent(new Event(THEME_EVENT))
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
          aria-pressed={theme === option}
          onClick={() => choose(option)}
          className={cx(
            'rounded-md px-2 py-1 text-xs font-medium transition-colors',
            theme === option ? 'bg-surface text-primary' : 'text-muted hover:text-primary',
          )}
        >
          {labels[option]}
        </button>
      ))}
    </div>
  )
}
