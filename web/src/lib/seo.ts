import type { Metadata } from 'next'

import { publicContentEnabled, siteUrl } from './api/config'
import { DEFAULT_LOCALE, LOCALE_PARAM, LOCALES, type Locale } from '@/i18n/locales'

/** `x-default` points at the address with no language pinned, which serves the default (`en`). */
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
  /** Language the page is rendered in; decides `og:locale`. Defaults to the default locale. */
  locale?: Locale
  /** Site name in that language, for `og:site_name`. */
  siteName?: string
  /** Use `title` as the whole `<title>`, without the site-name suffix (the home page). */
  absoluteTitle?: boolean
  /**
   * The language the URL itself pins with `?lang=`, if any.
   *
   * `/x?lang=en` is the English page and has to be its own canonical: pointing it at `/x`
   * tells a search engine that the English text is a copy of the Korean page, so only the
   * Korean one is indexed and an English query never finds the site. Each language version
   * names itself as canonical and the others through `hreflang`.
   */
  pinnedLocale?: Locale
}

/** OpenGraph wants a territory as well as a language (`ko_KR`), unlike `hreflang`. */
const OG_LOCALE: Record<Locale, string> = { ko: 'ko_KR', en: 'en_US' }
const DEFAULT_SITE_NAME = 'Robotics Expert Course'

/**
 * The card image shown when a page is shared (`public/og-image.png`, 1200x630).
 *
 * Named in every page's metadata rather than left to the `opengraph-image` file convention: a
 * page that sets its own `openGraph` replaces the inherited object, which silently dropped the
 * image from every route below the root.
 */
export const OG_IMAGE = { path: '/og-image.png', width: 1200, height: 630 } as const

/** Tokens a search engine's verification page asks to find in the markup, when configured. */
export function siteVerification(): Metadata['verification'] {
  const google = process.env.RC_GOOGLE_SITE_VERIFICATION?.trim()
  const naver = process.env.RC_NAVER_SITE_VERIFICATION?.trim()
  if (!google && !naver) return undefined
  return {
    ...(google ? { google } : {}),
    ...(naver ? { other: { 'naver-site-verification': naver } } : {}),
  }
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
  locale = DEFAULT_LOCALE,
  siteName = DEFAULT_SITE_NAME,
  absoluteTitle = false,
  pinnedLocale,
}: PageSeoOptions): Metadata {
  const indexable = publishable && publicContentEnabled()
  const alternates = languageAlternates(path)
  const url = (pinnedLocale && alternates[pinnedLocale]) || absoluteUrl(path)
  const image = absoluteUrl(OG_IMAGE.path)
  return {
    title: absoluteTitle ? { absolute: title } : title,
    ...(description ? { description } : {}),
    alternates: { canonical: url, languages: alternates },
    robots: indexable
      ? { index: true, follow: true }
      : { index: false, follow: false, nocache: true },
    openGraph: {
      type,
      url,
      title,
      ...(description ? { description } : {}),
      siteName,
      images: [{ url: image, width: OG_IMAGE.width, height: OG_IMAGE.height, alt: siteName }],
      locale: OG_LOCALE[locale],
      alternateLocale: LOCALES.filter((other) => other !== locale).map((other) => OG_LOCALE[other]),
    },
    twitter: {
      card: 'summary_large_image',
      images: [image],
      title,
      ...(description ? { description } : {}),
    },
  }
}

/** About where a search result cuts a title off. */
export const TITLE_LIMIT = 65

/**
 * `<subject> — <label> | <brand>`, shortened to fit a search result.
 *
 * The subject is the page's own name and is never cut. The label ("Robotics Tutorial") says what
 * kind of page it is and the brand names the site; when the three do not fit, the brand goes
 * first and then the label, because a title that ends in "…" has lost its last words anyway and
 * the subject is the part a searcher is matching.
 */
export function composeTitle(
  subject: string,
  label: string,
  brand: string,
  limit = TITLE_LIMIT,
): string {
  const full = `${subject} — ${label} | ${brand}`
  if (full.length <= limit) return full
  const labelled = `${subject} — ${label}`
  return labelled.length <= limit ? labelled : subject
}

/** TeX commands that have a plain character a search result can show. */
const TEX_SYMBOLS: Record<string, string> = {
  alpha: 'α',
  beta: 'β',
  gamma: 'γ',
  delta: 'δ',
  epsilon: 'ε',
  varepsilon: 'ε',
  zeta: 'ζ',
  eta: 'η',
  theta: 'θ',
  kappa: 'κ',
  lambda: 'λ',
  mu: 'μ',
  nu: 'ν',
  xi: 'ξ',
  pi: 'π',
  rho: 'ρ',
  sigma: 'σ',
  tau: 'τ',
  phi: 'φ',
  varphi: 'φ',
  chi: 'χ',
  psi: 'ψ',
  omega: 'ω',
  Gamma: 'Γ',
  Delta: 'Δ',
  Theta: 'Θ',
  Lambda: 'Λ',
  Xi: 'Ξ',
  Pi: 'Π',
  Sigma: 'Σ',
  Phi: 'Φ',
  Psi: 'Ψ',
  Omega: 'Ω',
  to: '→',
  rightarrow: '→',
  Rightarrow: '⇒',
  leftarrow: '←',
  mapsto: '↦',
  le: '≤',
  leq: '≤',
  ge: '≥',
  geq: '≥',
  ne: '≠',
  neq: '≠',
  approx: '≈',
  sim: '~',
  equiv: '≡',
  times: '×',
  cdot: '·',
  pm: '±',
  infty: '∞',
  partial: '∂',
  nabla: '∇',
  in: '∈',
  notin: '∉',
  subset: '⊂',
  subseteq: '⊆',
  cup: '∪',
  cap: '∩',
  sum: 'Σ',
  prod: 'Π',
  int: '∫',
  propto: '∝',
  succeq: '⪰',
  preceq: '⪯',
  succ: '≻',
  prec: '≺',
  top: 'ᵀ',
  dots: '…',
  ldots: '…',
  cdots: '…',
  quad: ' ',
  qquad: ' ',
  ell: 'ℓ',
  forall: '∀',
  exists: '∃',
  neg: '¬',
  circ: '∘',
  star: '*',
  sqrt: '√',
  log: 'log ',
  ln: 'ln ',
  exp: 'exp ',
  min: 'min ',
  max: 'max ',
  sin: 'sin ',
  cos: 'cos ',
  tan: 'tan ',
  det: 'det ',
}

const SUPERSCRIPT: Record<string, string> = {
  '0': '⁰',
  '1': '¹',
  '2': '²',
  '3': '³',
  '4': '⁴',
  '5': '⁵',
  '6': '⁶',
  '7': '⁷',
  '8': '⁸',
  '9': '⁹',
  '-': '⁻',
  '+': '⁺',
}

/** `a` stays `a`; `1-q` becomes `(1-q)`, so a fraction or an exponent keeps its grouping. */
function group(text: string): string {
  const trimmed = text.trim()
  return /^[\p{L}\p{N}.]+$/u.test(trimmed) ? trimmed : `(${trimmed})`
}

/** `^{-1}` → `⁻¹` when every character has a superscript form, `^(…)` otherwise. */
function script(mark: string, body: string): string {
  const trimmed = body.trim()
  if (mark === '^' && trimmed === 'ᵀ') return 'ᵀ'
  if (mark === '^' && [...trimmed].every((char) => char in SUPERSCRIPT)) {
    return [...trimmed].map((char) => SUPERSCRIPT[char]).join('')
  }
  return `${mark}${group(trimmed)}`
}

/** One TeX formula as the closest plain text: `\Phi(-r/2)` → `Φ(-r/2)`, `\frac{a}{b}` → `a/b`. */
function texToText(tex: string): string {
  let out = tex
    .replace(/\\(?:left|right|big|Big|bigg|Bigg|displaystyle|textstyle|,|;|:|!)/g, '')
    .replace(/\\[dt]?frac\s*(\d)\s*(\d)/g, '$1/$2')
  // Innermost groups first, so nested fractions, exponents and styled arguments all resolve.
  for (let pass = 0; pass < 6; pass += 1) {
    out = out
      .replace(
        /\\[dt]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}/g,
        (_match, top: string, bottom: string) => `${group(top)}/${group(bottom)}`,
      )
      .replace(/([\^_])\s*\{([^{}]*)\}/g, (_match, mark: string, body: string) =>
        script(mark, texSymbols(body)),
      )
      // A command that only styles its argument (`\mathcal{C}`, `\text{…}`) keeps the argument.
      .replace(/\\([A-Za-z]+)\*?\s*\{([^{}]*)\}/g, (_match, name: string, inner: string) =>
        name in TEX_SYMBOLS ? `${TEX_SYMBOLS[name]}${inner}` : inner,
      )
  }
  return texSymbols(out)
    .replace(/\^\s*(ᵀ|[0-9])/g, (_match, body: string) => script('^', body))
    .replace(/\\ /g, ' ')
    .replace(/\\(.)/g, '$1')
    .replace(/[{}]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

function texSymbols(tex: string): string {
  return tex.replace(/\\([A-Za-z]+)/g, (match, name: string) => TEX_SYMBOLS[name] ?? match)
}

/**
 * Lesson and module summaries are Markdown with inline TeX. A search result, a link preview and
 * JSON-LD show the string as it is, so `$\Phi(-r/2)$` would appear with its dollar signs and
 * backslashes. This is the reading text: formulas become plain characters and Markdown marks go.
 */
export function plainText(text: string | null | undefined): string {
  return (text ?? '')
    .replace(/\$\$([\s\S]+?)\$\$/g, (_match, tex: string) => texToText(tex))
    .replace(/\$([^$\n]+?)\$/g, (_match, tex: string) => texToText(tex))
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/`([^`]*)`/g, '$1')
    .replace(/(\*\*|__)(.+?)\1/g, '$2')
    .replace(/(^|[\s(])[*_]([^*_\n]+)[*_](?=$|[\s).,;:!?])/g, '$1$2')
    .replace(/\s+/g, ' ')
    .trim()
}

/** One sentence, trimmed to something a search result can show without cutting mid-word. */
export function metaDescription(text: string | null | undefined, limit = 160): string {
  const flat = plainText(text)
  if (flat.length <= limit) return flat
  const cut = flat.slice(0, limit)
  const lastSpace = cut.lastIndexOf(' ')
  return `${(lastSpace > limit * 0.6 ? cut.slice(0, lastSpace) : cut).trimEnd()}…`
}
