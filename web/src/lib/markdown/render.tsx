import 'server-only'

import type { ReactElement, ReactNode } from 'react'
import { Fragment, jsx, jsxs } from 'react/jsx-runtime'
import rehypeHighlight from 'rehype-highlight'
import rehypeKatex from 'rehype-katex'
import rehypeReact from 'rehype-react'
import rehypeSanitize from 'rehype-sanitize'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import remarkParse from 'remark-parse'
import remarkRehype from 'remark-rehype'
import { unified } from 'unified'

import { normalizeDisplayMath } from './normalize'
import { lessonSanitizeSchema } from './sanitize'
import { rehypeFocusableScrollers } from './scroll'
import { rehypeHeadingIds, rehypeShiftHeadings, type Heading } from './slug'
import { rehypeUnwrapParagraph } from './unwrap'

export type { Heading } from './slug'

export interface RenderedMarkdown {
  /** The rendered React tree — serialized by RSC, never `dangerouslySetInnerHTML`. */
  content: ReactNode
  /** Headings in document order, for the "on this page" list. */
  headings: Heading[]
}

/** Components substituted into the rendered tree. */
const components = {
  a: ({ href, children, ...rest }: { href?: string; children?: ReactNode }) => {
    const external = !!href && /^https?:\/\//.test(href)
    return (
      <a
        href={href}
        {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
        {...rest}
      >
        {children}
      </a>
    )
  },
}

/**
 * Render lesson Markdown to a React tree.
 *
 * Pipeline (frontend.md §5): remark-parse → remark-math → remark-gfm →
 * remark-rehype → rehype-katex → rehype-highlight → rehype-sanitize → heading
 * ids → rehype-react.
 *
 * Two deliberate choices, both to keep the sanitizer strict:
 * - KaTeX runs with `output: 'mathml'`, so no inline `style` attribute has to be
 *   allowed through `rehype-sanitize` and no KaTeX stylesheet ships to the client.
 * - Highlighting uses `rehype-highlight` (class names) rather than
 *   `rehype-pretty-code` (inline styles), and the classes are themed from the
 *   design tokens in `globals.css`.
 */
export interface RenderOptions {
  /**
   * Push content headings down this many levels so they nest under the page's
   * own `<h1>`. 1 by default: a body `#` becomes `<h2>`.
   */
  headingOffset?: number
}

export function renderMarkdown(
  markdown: string | undefined,
  { headingOffset = 1 }: RenderOptions = {},
): RenderedMarkdown {
  if (!markdown || markdown.trim() === '') return { content: null, headings: [] }

  const headings: Heading[] = []
  const file = unified()
    .use(remarkParse)
    .use(remarkMath)
    .use(remarkGfm)
    .use(remarkRehype)
    .use(rehypeKatex, { output: 'mathml', throwOnError: false, strict: false })
    .use(rehypeHighlight, { detect: false, ignoreMissing: true })
    .use(rehypeShiftHeadings(headingOffset))
    .use(rehypeSanitize, lessonSanitizeSchema)
    // After the sanitizer: the ids are generated here from heading text, so they
    // must not pick up its `user-content-` clobber prefix (the "on this page"
    // links target them directly).
    .use(rehypeHeadingIds(headings))
    .use(rehypeFocusableScrollers)
    .use(rehypeReact, { Fragment, jsx, jsxs, components })
    .processSync(normalizeDisplayMath(markdown))

  return { content: file.result as ReactElement, headings }
}

/**
 * Render a short, single-paragraph string — a lesson summary or objective, a
 * flashcard side — with the same pipeline, minus the wrapping `<p>`.
 *
 * These fields carry inline KaTeX (`관성 모멘트 $I = mr^2$`), so printing them
 * as text showed the TeX source. The paragraph is unwrapped because the result
 * goes inside an element that is already a `<p>` or an `<li>`.
 *
 * Not for free text that merely contains `$`: a resource note like
 * `팔로워 $121.94 / 리더 $229.88` is prices, not math, and must stay text.
 */
export function renderInlineMarkdown(markdown: string | null | undefined): ReactNode {
  if (!markdown || markdown.trim() === '') return null
  const file = unified()
    .use(remarkParse)
    .use(remarkMath)
    .use(remarkGfm)
    .use(remarkRehype)
    .use(rehypeKatex, { output: 'mathml', throwOnError: false, strict: false })
    .use(rehypeSanitize, lessonSanitizeSchema)
    .use(rehypeUnwrapParagraph)
    .use(rehypeFocusableScrollers)
    .use(rehypeReact, { Fragment, jsx, jsxs, components })
    .processSync(normalizeDisplayMath(markdown))
  return file.result as ReactElement
}
