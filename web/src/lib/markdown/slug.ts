import type { Element, Root } from 'hast'

/** Slugify heading text: keeps Hangul and alphanumerics, collapses the rest to `-`. */
export function slugify(text: string): string {
  return (
    text
      .trim()
      .toLowerCase()
      .replace(/[^0-9a-z가-힣ㄱ-ㅎㅏ-ㅣ\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '') || 'section'
  )
}

/** Plain text of a hast subtree. */
export function textOf(node: Element | Root): string {
  let out = ''
  for (const child of node.children) {
    if (child.type === 'text') out += child.value
    else if (child.type === 'element') out += textOf(child)
  }
  return out
}

export interface Heading {
  id: string
  depth: number
  text: string
}

const HEADINGS = new Set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

/**
 * Rehype plugin: push every heading down by `offset` levels, capped at `h6`.
 *
 * Content from the API carries its own `#` heading (a lesson body, a weekly
 * report), while the page already has an `<h1>`. Without this the page would
 * have two level-1 headings, which breaks the heading hierarchy a screen-reader
 * user navigates by (frontend.md §6).
 */
export function rehypeShiftHeadings(offset: number) {
  return () => (tree: Root) => {
    if (offset <= 0) return
    visit(tree)

    function visit(node: Root | Element): void {
      for (const child of node.children) {
        if (child.type !== 'element') continue
        if (HEADINGS.has(child.tagName)) {
          const level = Math.min(6, Number(child.tagName.slice(1)) + offset)
          child.tagName = `h${level}`
        }
        visit(child)
      }
    }
  }
}

/**
 * Rehype plugin: give every heading a unique `id` and collect the headings into
 * `collected`, so the lesson page can build its "on this page" list without a
 * second parse.
 */
export function rehypeHeadingIds(collected: Heading[]) {
  return () => (tree: Root) => {
    const seen = new Map<string, number>()
    visit(tree)

    function visit(node: Root | Element): void {
      for (const child of node.children) {
        if (child.type !== 'element') continue
        if (HEADINGS.has(child.tagName)) {
          const text = textOf(child)
          const base = slugify(text)
          const count = seen.get(base) ?? 0
          seen.set(base, count + 1)
          const id = count === 0 ? base : `${base}-${count}`
          child.properties = { ...child.properties, id }
          collected.push({ id, depth: Number(child.tagName.slice(1)), text })
        }
        visit(child)
      }
    }
  }
}
