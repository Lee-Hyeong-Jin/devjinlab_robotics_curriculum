import type { Element, Root } from 'hast'

/** Elements `globals.css` lets scroll sideways inside `.markdown-body`. */
function scrolls(node: Element): boolean {
  if (node.tagName === 'pre' || node.tagName === 'table') return true
  return node.tagName === 'math' && node.properties?.display === 'block'
}

/**
 * Rehype plugin: make the horizontally scrollable parts of a lesson reachable
 * by keyboard.
 *
 * Long formulas, code blocks and wide tables scroll sideways rather than
 * widening the page (globals.css, frontend.md §6 — no horizontal page scroll at
 * 200% zoom). A scrollable region that cannot be focused is unreachable without
 * a mouse, which axe reports as `scrollable-region-focusable` (serious,
 * AC-A11Y.1).
 *
 * Runs after the sanitizer, so `tabindex` needs no entry in the schema.
 */
export function rehypeFocusableScrollers() {
  return (tree: Root) => {
    visit(tree)

    function visit(node: Root | Element): void {
      for (const child of node.children) {
        if (child.type !== 'element') continue
        if (scrolls(child)) {
          child.properties = { ...child.properties, tabIndex: 0 }
          continue
        }
        visit(child)
      }
    }
  }
}
