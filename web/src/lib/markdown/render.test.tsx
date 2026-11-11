import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { MarkdownBody } from '@/components/MarkdownBody'

import { renderMarkdown } from './render'
import { slugify } from './slug'

function renderBody(markdown: string) {
  const { content, headings } = renderMarkdown(markdown)
  const result = render(<MarkdownBody>{content}</MarkdownBody>)
  return { ...result, headings }
}

describe('renderMarkdown', () => {
  it('returns nothing for empty input', () => {
    expect(renderMarkdown(undefined).content).toBeNull()
    expect(renderMarkdown('   ').content).toBeNull()
    expect(renderMarkdown('').headings).toEqual([])
  })

  it('renders inline and display KaTeX math as MathML (AC-WEB.2)', () => {
    const { container } = renderBody(
      '회전 행렬 $R \\in SO(3)$ 는 다음을 만족한다.\n\n$$\nR^T R = I\n$$\n',
    )
    const math = container.querySelectorAll('math')
    expect(math.length).toBe(2)
    // Display math is marked as a block so it can scroll independently.
    expect(container.querySelector('math[display="block"]')).not.toBeNull()
    // The TeX source survives in the MathML annotation, so the formula is
    // selectable and reaches assistive tech.
    expect(container.textContent).toContain('SO')
  })

  it('leaves invalid TeX in place instead of throwing', () => {
    expect(() => renderMarkdown('$\\frac{1}{$')).not.toThrow()
  })

  it('highlights fenced code with language classes (AC-WEB.2)', () => {
    const { container } = renderBody('```python\nimport numpy as np\nR = np.eye(3)\n```\n')
    const code = container.querySelector('pre code')
    expect(code?.className).toContain('language-python')
    expect(code?.className).toContain('hljs')
    // highlight.js token spans survive the sanitizer.
    expect(container.querySelectorAll('span.hljs-keyword').length).toBeGreaterThan(0)
  })

  it('renders GFM tables with a header row', () => {
    const { container } = renderBody('| a | b |\n|---|---|\n| 1 | 2 |\n')
    expect(container.querySelectorAll('table thead th').length).toBe(2)
    expect(container.querySelectorAll('tbody td').length).toBe(2)
  })

  it('opens external links in a new tab and keeps internal links in place', () => {
    const { container } = renderBody('[외부](https://example.com) 와 [앵커](#section)\n')
    const external = container.querySelector('a[href="https://example.com"]')
    expect(external?.getAttribute('target')).toBe('_blank')
    expect(external?.getAttribute('rel')).toContain('noopener')
    const internal = container.querySelector('a[href="#section"]')
    expect(internal).not.toBeNull()
    expect(internal?.getAttribute('target')).toBeNull()
  })

  it('strips raw HTML, scripts and javascript: URLs', () => {
    const { container } = renderBody(
      '<script>window.x=1</script>\n\n<img src=x onerror="alert(1)">\n\n[나쁜 링크](javascript:alert(1))\n',
    )
    expect(container.querySelector('script')).toBeNull()
    expect(container.querySelector('img[onerror]')).toBeNull()
    expect(container.innerHTML).not.toContain('javascript:')
  })

  it('never emits an inline style attribute', () => {
    const { container } = renderBody('$$\\begin{bmatrix} 1 & 0 \\\\ 0 & 1 \\end{bmatrix}$$\n')
    expect(container.querySelectorAll('[style]').length).toBe(0)
  })

  it('gives headings ids and collects them in document order', () => {
    const { container, headings } = renderBody('## 이 단계 공부법\n\n본문\n\n### 세부\n\n## 정리\n')
    expect(headings.map((heading) => heading.text)).toEqual(['이 단계 공부법', '세부', '정리'])
    expect(headings.map((heading) => heading.depth)).toEqual([2, 3, 2])
    expect(container.querySelector('h2')?.id).toBe('이-단계-공부법')
  })

  it('de-duplicates repeated heading slugs', () => {
    const { headings } = renderBody('## 정리\n\n## 정리\n')
    expect(headings.map((heading) => heading.id)).toEqual(['정리', '정리-1'])
  })
})

describe('slugify', () => {
  it('keeps Hangul and collapses punctuation', () => {
    expect(slugify('이 단계 공부법')).toBe('이-단계-공부법')
    expect(slugify('Forward Kinematics (FK)!')).toBe('forward-kinematics-fk')
  })

  it('falls back to "section" when nothing is left', () => {
    expect(slugify('!!!')).toBe('section')
  })
})

describe('single-line display math', () => {
  it('renders `$$x$$` on its own line as display math, like the static site', () => {
    const { container } = renderBody('앞 문장\n\n$$T_{0n} = T_{01} T_{12}$$\n\n뒤 문장\n')
    expect(container.querySelector('math[display="block"]')).not.toBeNull()
  })

  it('leaves inline math inside a sentence inline', () => {
    const { container } = renderBody('회전은 $R \\in SO(3)$ 이다.\n')
    expect(container.querySelector('math[display="block"]')).toBeNull()
    expect(container.querySelector('math')).not.toBeNull()
  })

  it('does not touch `$$` inside a fenced code block', () => {
    const { container } = renderBody('```bash\n$$x$$\n```\n')
    expect(container.querySelector('math')).toBeNull()
    expect(container.querySelector('pre code')?.textContent).toContain('$$x$$')
  })
})
