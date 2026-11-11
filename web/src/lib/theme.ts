/** Theme preference: `system` follows `prefers-color-scheme` (frontend.md §3). */
export type Theme = 'system' | 'light' | 'dark'

export const THEME_STORAGE_KEY = 'rc-theme'

export function isTheme(value: unknown): value is Theme {
  return value === 'system' || value === 'light' || value === 'dark'
}

/** Read the stored preference; `system` when absent or storage is unavailable. */
export function readStoredTheme(): Theme {
  try {
    const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
    return isTheme(stored) ? stored : 'system'
  } catch {
    return 'system'
  }
}

/** Write the preference onto `<html data-theme>`; `system` removes the attribute. */
export function applyTheme(theme: Theme): void {
  const root = document.documentElement
  if (theme === 'system') root.removeAttribute('data-theme')
  else root.setAttribute('data-theme', theme)
}

/**
 * Inline script that applies the stored theme before first paint, so a dark
 * viewer never sees a light flash.
 */
export const THEME_INIT_SCRIPT = `(function(){try{var t=localStorage.getItem('${THEME_STORAGE_KEY}');if(t==='light'||t==='dark'){document.documentElement.setAttribute('data-theme',t)}}catch(e){}})()`
