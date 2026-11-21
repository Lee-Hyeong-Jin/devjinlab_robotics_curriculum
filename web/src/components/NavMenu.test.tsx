import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { NavMenu } from './NavMenu'

function renderMenu() {
  return render(
    <div>
      <nav>
        <NavMenu
          labels={{ open: '메뉴 열기', close: '메뉴 닫기' }}
          tabs={<a href="/roadmap">로드맵</a>}
          utilities={<a href="/login">로그인</a>}
        />
      </nav>
      <button type="button">바깥</button>
    </div>,
  )
}

describe('NavMenu', () => {
  it('is a closed disclosure that names what it controls', () => {
    renderMenu()
    const toggle = screen.getByRole('button', { name: '메뉴 열기' })
    expect(toggle).toHaveAttribute('aria-expanded', 'false')
    const panel = document.getElementById(toggle.getAttribute('aria-controls') ?? '')
    expect(panel).not.toBeNull()
    expect(panel).toHaveClass('hidden')
    // One tree for every width: the links exist once, never duplicated for a second layout.
    expect(screen.getAllByText('로드맵')).toHaveLength(1)
    expect(screen.getAllByText('로그인')).toHaveLength(1)
  })

  it('opens and closes from the toggle, and the label follows the state', async () => {
    const user = userEvent.setup()
    renderMenu()
    await user.click(screen.getByRole('button', { name: '메뉴 열기' }))
    const toggle = screen.getByRole('button', { name: '메뉴 닫기' })
    expect(toggle).toHaveAttribute('aria-expanded', 'true')
    expect(document.getElementById(toggle.getAttribute('aria-controls') ?? '')).not.toHaveClass(
      'hidden',
    )
    await user.click(toggle)
    expect(screen.getByRole('button', { name: '메뉴 열기' })).toHaveAttribute(
      'aria-expanded',
      'false',
    )
  })

  it('closes on Escape and returns focus to the toggle', async () => {
    const user = userEvent.setup()
    renderMenu()
    await user.click(screen.getByRole('button', { name: '메뉴 열기' }))
    await user.tab()
    await user.keyboard('{Escape}')
    const toggle = screen.getByRole('button', { name: '메뉴 열기' })
    expect(toggle).toHaveAttribute('aria-expanded', 'false')
    expect(toggle).toHaveFocus()
  })

  it('closes when the reader presses outside it, but not inside', async () => {
    const user = userEvent.setup()
    renderMenu()
    await user.click(screen.getByRole('button', { name: '메뉴 열기' }))
    await user.pointer({ keys: '[MouseLeft>]', target: screen.getByText('로그인') })
    expect(screen.getByRole('button', { name: '메뉴 닫기' })).toBeInTheDocument()
    await user.pointer({
      keys: '[MouseLeft>]',
      target: screen.getByRole('button', { name: '바깥' }),
    })
    expect(screen.getByRole('button', { name: '메뉴 열기' })).toBeInTheDocument()
  })
})
