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

import { lessonSanitizeSchema } from './sanitize'
import { rehypeHeadingIds, type Heading } from './slug'

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
 * remark-rehype → rehype-katex → rehype-highlight → rehype-sanitize → rehype-react.
 *
 * Two deliberate choices, both to keep the sanitizer strict:
 * - KaTeX runs with `output: 'mathml'`, so no inline `style` attribute has to be
 *   allowed through `rehype-sanitize` and no KaTeX stylesheet ships to the client.
 * - Highlighting uses `rehype-highlight` (class names) rather than
 *   `rehype-pretty-code` (inline styles), and the classes are themed from the
 *   design tokens in `globals.css`.
 */
export function renderMarkdown(markdown: string | undefined): RenderedMarkdown {
  if (!markdown || markdown.trim() === '') return { content: null, headings: [] }

  const headings: Heading[] = []
  const file = unified()
    .use(remarkParse)
    .use(remarkMath)
    .use(remarkGfm)
    .use(remarkRehype)
    .use(rehypeKatex, { output: 'mathml', throwOnError: false, strict: false })
    .use(rehypeHighlight, { detect: false, ignoreMissing: true })
    .use(rehypeHeadingIds(headings))
    .use(rehypeSanitize, lessonSanitizeSchema)
    .use(rehypeReact, { Fragment, jsx, jsxs, components })
    .processSync(markdown)

  return { content: file.result as ReactElement, headings }
}
