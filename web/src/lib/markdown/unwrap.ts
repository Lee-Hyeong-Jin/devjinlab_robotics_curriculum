import type { Root } from 'hast'

/**
 * Rehype plugin: drop the wrapping `<p>` when the document is a single paragraph.
 *
 * Short fields (a lesson summary, an objective, a flashcard side) are rendered
 * into an element that is already a `<p>` or an `<li>`, and a nested `<p>` is
 * invalid HTML the browser silently splits apart.
 */
export function rehypeUnwrapParagraph() {
  return (tree: Root) => {
    const children = tree.children.filter(
      (node) => node.type !== 'text' || node.value.trim() !== '',
    )
    const only = children[0]
    if (children.length === 1 && only?.type === 'element' && only.tagName === 'p') {
      tree.children = only.children
    }
  }
}
