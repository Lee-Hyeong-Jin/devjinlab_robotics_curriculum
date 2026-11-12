import type { Metadata } from 'next'

import { publicContentEnabled, siteUrl } from './api/config'
import { DEFAULT_LOCALE, LOCALE_PARAM, LOCALES } from '@/i18n/locales'

/** `x-default` points at the address with no language pinned, which serves `ko`. */
const X_DEFAULT = 'x-default'

/** An absolute URL on this site for `path` (which must start with `/`). */
export function absoluteUrl(path: string): string {
  return `${siteUrl()}${path}`
}

/**
 * The same page in each language, keyed the way `alternates.languages` wants.
 *
 * The URL has no locale segment, so a language is pinned with `?lang=` — without distinct
 * addresses `hreflang` has nothing to point at. The default language keeps the bare path so
 * the canonical URL stays the short one.
 */
export function languageAlternates(path: string): Record<string, string> {
  const out: Record<string, string> = { [X_DEFAULT]: absoluteUrl(path) }
  for (const locale of LOCALES) {
    const separator = path.includes('?') ? '&' : '?'
    out[locale] =
      locale === DEFAULT_LOCALE
        ? absoluteUrl(path)
        : absoluteUrl(`${path}${separator}${LOCALE_PARAM}=${locale}`)
  }
  return out
}

export interface PageSeoOptions {
  /** Canonical path, starting with `/` and without `?lang=`. */
  path: string
  title: string
  description?: string
  /**
   * Whether this page may be indexed. Only ever true for published curriculum, and only
   * when the deployment publishes it at all (`RC_PUBLIC_CONTENT`, ADR 0016) — everything
   * else is somebody's own data.
   */
  publishable?: boolean
  /** `article` for a lesson, `website` otherwise. */
  type?: 'website' | 'article'
}

/**
 * Metadata for one page: canonical, hreflang, OpenGraph and Twitter card, and the robots
 * directive.
 *
 * `noindex` is the default and has to be asked out of: the app is mostly a reader's own
 * dashboard, progress and notes, and a page that is indexed by accident cannot be
 * un-indexed by fixing the code later.
 */
export function pageSeo({
  path,
  title,
  description,
  publishable = false,
  type = 'website',
}: PageSeoOptions): Metadata {
  const indexable = publishable && publicContentEnabled()
  const url = absoluteUrl(path)
  return {
    title,
    ...(description ? { description } : {}),
    alternates: { canonical: url, languages: languageAlternates(path) },
    robots: indexable
      ? { index: true, follow: true }
      : { index: false, follow: false, nocache: true },
    openGraph: {
      type,
      url,
      title,
      ...(description ? { description } : {}),
      siteName: 'Robotics Expert Course',
      locale: DEFAULT_LOCALE,
    },
    twitter: {
      card: 'summary',
      title,
      ...(description ? { description } : {}),
    },
  }
}

/** One sentence, trimmed to something a search result can show without cutting mid-word. */
export function metaDescription(text: string | null | undefined, limit = 160): string {
  const flat = (text ?? '').replace(/\s+/g, ' ').trim()
  if (flat.length <= limit) return flat
  const cut = flat.slice(0, limit)
  const lastSpace = cut.lastIndexOf(' ')
  return `${(lastSpace > limit * 0.6 ? cut.slice(0, lastSpace) : cut).trimEnd()}…`
}
