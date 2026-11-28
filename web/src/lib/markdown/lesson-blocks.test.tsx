import { render } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { figureBase, figureUrl } from './lesson-blocks'
import { renderMarkdown } from './render'

function renderBody(markdown: string, options = {}) {
  return render(<div>{renderMarkdown(markdown, options).content}</div>)
}

describe('expected-result blocks (#48)', () => {
  const BODY =
    '**Exercise:** tune the gain.\n\n```expected\nThe error settles at **4.3°**; with $K_i$ it reaches 0.\n\n- overshoot below 10%\n```\n\nNext paragraph.\n'

  it('folds the block away under a labelled summary', () => {
    const { container } = renderBody(BODY, { expectedLabel: '기대 결과' })
    const details = container.querySelector('details')
    expect(details).not.toBeNull()
    expect(details?.hasAttribute('open')).toBe(false)
    expect(details?.querySelector('summary')?.textContent).toBe('기대 결과')
    // It is not printed as a code block.
    expect(container.querySelector('pre')).toBeNull()
  })

  it('renders what is inside as Markdown, formulas included', () => {
    const { container } = renderBody(BODY)
    const details = container.querySelector('details')
    expect(details?.querySelector('strong')?.textContent).toBe('4.3°')
    expect(details?.querySelector('math')).not.toBeNull()
    expect(details?.querySelectorAll('li')).toHaveLength(1)
    // The text after the block is outside it.
    expect(details?.textContent).not.toContain('Next paragraph')
    expect(container.textContent).toContain('Next paragraph')
  })

  it('leaves an ordinary code block alone', () => {
    const { container } = renderBody('```python\nprint(1)\n```\n')
    expect(container.querySelector('details')).toBeNull()
    expect(container.querySelector('pre')).not.toBeNull()
  })
})

describe('lesson figures (#60)', () => {
  it('builds the address the app serves a figure from', () => {
    expect(figureBase('m1-vectors-matrices')).toBe('/lesson-assets/m1-vectors-matrices')
    expect(figureUrl('figures/frames.svg', '/lesson-assets/l1')).toBe(
      '/lesson-assets/l1/frames.svg',
    )
    for (const source of [
      'figures/../secret.svg',
      'figures/Frames.SVG',
      'figures/a/b.svg',
      'other/frames.svg',
      'figures/frames.html',
      undefined,
    ]) {
      expect(figureUrl(source, '/lesson-assets/l1'), String(source)).toBeNull()
    }
  })

  it('points a figure at the app route, keeps its alt text and loads it lazily', () => {
    const { container } = renderBody('![Two frames related by a rotation](figures/frames.svg)\n', {
      figureBase: '/lesson-assets/m1-x',
    })
    const image = container.querySelector('img')
    expect(image?.getAttribute('src')).toBe('/lesson-assets/m1-x/frames.svg')
    expect(image?.getAttribute('alt')).toBe('Two frames related by a rotation')
    expect(image?.getAttribute('loading')).toBe('lazy')
    expect(image?.className).toBe('lesson-figure')
  })

  it('drops an image that could not load, and keeps a web image', () => {
    const local = renderBody('![x](figures/frames.svg) and ![y](../../etc/passwd)\n')
    expect(local.container.querySelector('img')).toBeNull()
    const web = renderBody('![logo](https://example.com/logo.png)\n')
    expect(web.container.querySelector('img')?.getAttribute('src')).toBe(
      'https://example.com/logo.png',
    )
  })
})

describe('hint blocks (#64)', () => {
  const BODY =
    'Run the talker.\n\n```hint\n`ros2: command not found`\nSource the installation **in this terminal**.\n```\n'

  it('folds the advice away under "If this failed: <symptom>"', () => {
    const { container } = renderBody(BODY, { hintLabel: '막혔을 때' })
    const details = container.querySelector('details')
    expect(details?.hasAttribute('open')).toBe(false)
    expect(details?.querySelector('summary')?.textContent).toBe(
      '막혔을 때: `ros2: command not found`',
    )
    expect(details?.querySelector('strong')?.textContent).toBe('in this terminal')
    expect(container.querySelector('pre')).toBeNull()
  })
})
