import { beforeEach, describe, expect, it, vi } from 'vitest'

import { THEME_INIT_SCRIPT, THEME_STORAGE_KEY, applyTheme, isTheme, readStoredTheme } from './theme'

describe('applyTheme', () => {
  beforeEach(() => {
    document.documentElement.removeAttribute('data-theme')
  })

  it('pins light and dark on the html element', () => {
    applyTheme('dark')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
    applyTheme('light')
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')
  })

  it('removes the attribute for the system default', () => {
    applyTheme('dark')
    applyTheme('system')
    expect(document.documentElement.hasAttribute('data-theme')).toBe(false)
  })
})

function installStorage(): Storage {
  const store = new Map<string, string>()
  const storage: Storage = {
    get length() {
      return store.size
    },
    clear: () => store.clear(),
    getItem: (key) => store.get(key) ?? null,
    key: (index) => [...store.keys()][index] ?? null,
    removeItem: (key) => void store.delete(key),
    setItem: (key, value) => void store.set(key, value),
  }
  vi.stubGlobal('localStorage', storage)
  Object.defineProperty(window, 'localStorage', { value: storage, configurable: true })
  return storage
}

describe('readStoredTheme', () => {
  let storage: Storage

  beforeEach(() => {
    storage = installStorage()
  })

  it('reads a stored preference', () => {
    storage.setItem(THEME_STORAGE_KEY, 'dark')
    expect(readStoredTheme()).toBe('dark')
  })

  it('defaults to system when absent or invalid', () => {
    expect(readStoredTheme()).toBe('system')
    storage.setItem(THEME_STORAGE_KEY, 'neon')
    expect(readStoredTheme()).toBe('system')
  })

  it('defaults to system when storage throws (private mode)', () => {
    vi.spyOn(storage, 'getItem').mockImplementation(() => {
      throw new Error('blocked')
    })
    expect(readStoredTheme()).toBe('system')
  })
})

describe('isTheme', () => {
  it('accepts only the three options', () => {
    expect(['system', 'light', 'dark'].every(isTheme)).toBe(true)
    expect(isTheme('sepia')).toBe(false)
  })
})

describe('THEME_INIT_SCRIPT', () => {
  it('reads the same storage key and tolerates a throwing accessor', () => {
    expect(THEME_INIT_SCRIPT).toContain(THEME_STORAGE_KEY)
    expect(THEME_INIT_SCRIPT).toContain('catch')
  })
})
