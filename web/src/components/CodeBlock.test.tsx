import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { renderMarkdown } from '@/lib/markdown/render'

import { CodeToolLabelsProvider } from './CodeBlock'

afterEach(() => vi.restoreAllMocks())

const PYTHON = '```python\nimport numpy as np\nprint(np.eye(2))\n```\n'

describe('code blocks (#49)', () => {
  it('copies exactly the code that is shown', async () => {
    const user = userEvent.setup()
    const written: string[] = []
    vi.spyOn(navigator.clipboard, 'writeText').mockImplementation(async (text: string) => {
      written.push(text)
    })
    render(<div>{renderMarkdown(PYTHON).content}</div>)
    await user.click(screen.getByRole('button', { name: 'Copy' }))
    await waitFor(() => expect(written).toEqual(['import numpy as np\nprint(np.eye(2))\n']))
    expect(screen.getByRole('button', { name: 'Copied' })).toBeInTheDocument()
  })

  it('offers a .py download for Python only', () => {
    const { rerender } = render(<div>{renderMarkdown(PYTHON).content}</div>)
    expect(screen.getByRole('button', { name: 'Download .py' })).toBeInTheDocument()
    rerender(<div>{renderMarkdown('```bash\nrc example m1\n```\n').content}</div>)
    expect(screen.getByRole('button', { name: 'Copy' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Download .py' })).toBeNull()
  })

  it('takes its labels from the page, in the language of the reader', () => {
    render(
      <CodeToolLabelsProvider labels={{ copy: '복사', copied: '복사됨', download: '.py 내려받기' }}>
        {renderMarkdown(PYTHON).content}
      </CodeToolLabelsProvider>,
    )
    expect(screen.getByRole('button', { name: '복사' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '.py 내려받기' })).toBeInTheDocument()
  })

  it('keeps the block a keyboard-reachable scroller', () => {
    const { container } = render(<div>{renderMarkdown(PYTHON).content}</div>)
    expect(container.querySelector('.code-block pre')?.getAttribute('tabindex')).toBe('0')
  })
})
