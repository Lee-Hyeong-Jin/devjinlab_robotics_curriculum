import type { Element, Root as HastRoot } from 'hast'
import type { Code, Paragraph, Parent, Root as MdastRoot, RootContent } from 'mdast'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import remarkParse from 'remark-parse'
import { unified } from 'unified'

import { normalizeDisplayMath } from './normalize'

/**
 * Two lesson conventions the plain Markdown pipeline does not know (see
 * `docs/curriculum/CONTENT_MODEL.md`):
 *
 * - ```` ```expected ```` after an exercise: what a correct attempt gives. It is Markdown, and
 *   it is shown folded so a reader tries first.
 * - `![alt](figures/name.svg)`: a figure kept next to the lesson's source file. The browser
 *   cannot reach that file, so the address is rewritten to this app's own route, which
 *   fetches it from the API.
 */

const EXPECTED = 'expected'
const FIGURE = /^figures\/([a-z0-9][a-z0-9-]*\.(?:svg|png))$/

/** Where the app serves a lesson's figures from (`app/lesson-assets/…/route.ts`). */
export function figureBase(lessonId: string): string {
  return `/lesson-assets/${encodeURIComponent(lessonId)}`
}

/** `figures/frames.svg` → `/lesson-assets/<lesson>/frames.svg`; anything else → `null`. */
export function figureUrl(source: string | undefined, base: string): string | null {
  const name = FIGURE.exec(source ?? '')?.[1]
  return name ? `${base}/${name}` : null
}

function parseMarkdown(markdown: string): RootContent[] {
  const tree = unified()
    .use(remarkParse)
    .use(remarkMath)
    .use(remarkGfm)
    .parse(normalizeDisplayMath(markdown)) as MdastRoot
  return tree.children
}

/**
 * Remark plugin: turn each ```` ```expected ```` block into `<details>` holding the block's own
 * Markdown, under a `<summary>` with the given label.
 */
export function remarkExpectedResults(label: string) {
  return () => (tree: MdastRoot) => {
    const visit = (parent: Parent): void => {
      parent.children.forEach((child, index) => {
        if (child.type === 'code' && (child as Code).lang === EXPECTED) {
          const summary: Paragraph = {
            type: 'paragraph',
            data: { hName: 'summary' },
            children: [{ type: 'text', value: label }],
          }
          parent.children[index] = {
            type: 'blockquote', // any container type: `hName` decides what it becomes
            data: { hName: 'details' },
            children: [summary, ...parseMarkdown((child as Code).value)],
          } as RootContent
        } else if ('children' in child) {
          visit(child as Parent)
        }
      })
    }
    visit(tree)
  }
}

/**
 * Rehype plugin: point figure images at the app's route and let them load lazily. An image
 * whose address is neither a figure nor a web address is dropped — it could not load.
 */
export function rehypeFigures(base: string | undefined) {
  return () => (tree: HastRoot) => {
    const visit = (node: HastRoot | Element): void => {
      node.children = node.children.filter((child) => {
        if (child.type !== 'element') return true
        if (child.tagName === 'img') {
          const source = typeof child.properties?.src === 'string' ? child.properties.src : ''
          const figure = base ? figureUrl(source, base) : null
          if (figure) {
            child.properties = {
              ...child.properties,
              src: figure,
              loading: 'lazy',
              decoding: 'async',
              className: ['lesson-figure'],
            }
            return true
          }
          return /^https?:\/\//.test(source)
        }
        visit(child)
        return true
      })
    }
    visit(tree)
  }
}
