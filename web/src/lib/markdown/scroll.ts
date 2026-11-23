import type { Element, Root } from 'hast'

/** Elements `globals.css` lets scroll sideways inside `.markdown-body`. */
function scrolls(node: Element): boolean {
  return node.tagName === 'pre' || node.tagName === 'table'
}

function isDisplayMath(node: Element): boolean {
  return node.tagName === 'math' && node.properties?.display === 'block'
}

/** Class of the element that scrolls a display formula (`globals.css`). */
export const MATH_SCROLL_CLASS = 'math-scroll'

/**
 * Rehype plugin: make the horizontally scrollable parts of a lesson reachable
 * by keyboard.
 *
 * Long formulas (inside a wrapper, see below), code blocks and wide tables scroll sideways rather than
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
        if (isDisplayMath(child)) {
          // A `<math>` element lays its content out as a formula and does not become a scroll
          // container: on a phone a wide matrix was simply cut off at the edge of the card.
          // The formula goes inside a plain block that scrolls and takes keyboard focus.
          const index = node.children.indexOf(child)
          node.children[index] = {
            type: 'element',
            tagName: 'div',
            properties: { className: [MATH_SCROLL_CLASS], tabIndex: 0 },
            children: [child],
          }
          continue
        }
        visit(child)
      }
    }
  }
}
