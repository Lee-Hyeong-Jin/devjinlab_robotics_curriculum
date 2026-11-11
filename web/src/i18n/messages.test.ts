import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

import en from '../../messages/en.json'
import ko from '../../messages/ko.json'
import { LOCALES } from './locales'

type Catalogue = Record<string, unknown>

/** Every leaf key as a dotted path. */
function flatten(value: Catalogue, prefix = ''): string[] {
  return Object.entries(value).flatMap(([key, child]) =>
    child !== null && typeof child === 'object'
      ? flatten(child as Catalogue, `${prefix}${key}.`)
      : [`${prefix}${key}`],
  )
}

/** Every ICU placeholder in a catalogue, keyed by message path. */
function placeholders(value: Catalogue, prefix = ''): Map<string, string[]> {
  const out = new Map<string, string[]>()
  for (const [key, child] of Object.entries(value)) {
    const path = `${prefix}${key}`
    if (child !== null && typeof child === 'object') {
      for (const [nested, names] of placeholders(child as Catalogue, `${path}.`)) {
        out.set(nested, names)
      }
    } else if (typeof child === 'string') {
      out.set(path, [...child.matchAll(/\{(\w+)[^}]*\}/g)].map((match) => match[1] ?? '').sort())
    }
  }
  return out
}

const SOURCE_ROOT = join(process.cwd(), 'src')

function sourceFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name)
    if (entry.isDirectory()) return sourceFiles(path)
    if (!/\.tsx?$/.test(entry.name)) return []
    if (/\.test\.tsx?$/.test(entry.name)) return []
    return [path]
  })
}

const sources = sourceFiles(SOURCE_ROOT).map((path) => readFileSync(path, 'utf8'))
const allSource = sources.join('\n')

/** Namespaces passed to `getTranslations('x')` / `useTranslations('x')`. */
const namespaces = new Set(
  [...allSource.matchAll(/(?:get|use)Translations\(\s*'([\w.]+)'\s*\)/g)].map(
    (match) => match[1] ?? '',
  ),
)
/** First arguments of every `t('…')`-style call. */
const messageKeys = new Set(
  [...allSource.matchAll(/\bt[A-Za-z]*\(\s*'([\w.]+)'/g)].map((match) => match[1] ?? ''),
)
/** Keys called with an argument object: `t('key', { … })`. */
const keysCalledWithArgs = new Set(
  [...allSource.matchAll(/\bt[A-Za-z]*\(\s*'([\w.]+)'\s*,/g)].map((match) => match[1] ?? ''),
)
/** Keys called with no second argument anywhere: `t('key')`. */
const keysCalledBare = new Set(
  [...allSource.matchAll(/\bt[A-Za-z]*\(\s*'([\w.]+)'\s*\)/g)].map((match) => match[1] ?? ''),
)

describe('message catalogues', () => {
  it('ships one catalogue per declared locale', () => {
    expect(LOCALES).toEqual(['ko', 'en'])
  })

  it('has no key missing from any locale (AC-I18N.1)', () => {
    const koKeys = flatten(ko).sort()
    const enKeys = flatten(en).sort()
    expect(enKeys.filter((key) => !koKeys.includes(key))).toEqual([])
    expect(koKeys.filter((key) => !enKeys.includes(key))).toEqual([])
  })

  it('uses the same ICU placeholders in every locale', () => {
    const koPlaceholders = placeholders(ko)
    const mismatches: string[] = []
    for (const [path, names] of placeholders(en)) {
      const other = koPlaceholders.get(path)
      if (other && JSON.stringify(other) !== JSON.stringify(names)) mismatches.push(path)
    }
    expect(mismatches).toEqual([])
  })

  it('has no unused key (AC-I18N.1)', () => {
    const unused = flatten(ko).filter((key) => {
      if (messageKeys.has(key)) return false
      const dot = key.lastIndexOf('.')
      const namespace = key.slice(0, dot)
      const leaf = key.slice(dot + 1)
      // `t('leaf')` inside `getTranslations('namespace')`.
      if (namespaces.has(namespace) && messageKeys.has(leaf)) return false
      // Namespaces indexed dynamically, e.g. `tState(state)` over `state.*`.
      if (namespaces.has(namespace) && new RegExp(`\\(\\s*'${namespace}'\\s*\\)`).test(allSource)) {
        return !new RegExp(`t[A-Za-z]*\\(`).test(allSource)
      }
      return true
    })
    expect(unused).toEqual([])
  })

  it('passes an argument for every message that takes a placeholder', () => {
    // next-intl raises FORMATTING_ERROR at render time when a placeholder has no
    // value, and the page still renders, so neither tsc nor an E2E run catches it.
    const missingArgs: string[] = []
    const needlessPlaceholder: string[] = []
    for (const [path, names] of placeholders(ko)) {
      const leaf = path.slice(path.lastIndexOf('.') + 1)
      const called = messageKeys.has(path) || messageKeys.has(leaf)
      if (!called) continue
      const withArgs = keysCalledWithArgs.has(path) || keysCalledWithArgs.has(leaf)
      const bare = keysCalledBare.has(path) || keysCalledBare.has(leaf)
      if (names.length > 0 && bare && !withArgs) missingArgs.push(`${path} needs {${names}}`)
      if (names.length === 0 && withArgs && !bare) needlessPlaceholder.push(path)
    }
    expect(missingArgs).toEqual([])
    expect(needlessPlaceholder).toEqual([])
  })

  it('never leaves a message empty', () => {
    for (const catalogue of [ko, en]) {
      const empty = flatten(catalogue).filter((key) => {
        const value = key
          .split('.')
          .reduce<unknown>((node, part) => (node as Catalogue)?.[part], catalogue)
        return typeof value !== 'string' || value.trim() === ''
      })
      expect(empty).toEqual([])
    }
  })
})
