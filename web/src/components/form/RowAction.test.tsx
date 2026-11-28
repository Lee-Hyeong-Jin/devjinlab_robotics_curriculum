import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ActionState } from '@/lib/actions/result'
import { renderWithIntl } from '@/test/render'

import { RowAction } from './RowAction'

afterEach(() => vi.restoreAllMocks())

function setup(confirm?: string) {
  const action = vi.fn(async (): Promise<ActionState> => ({ message: 'done' }))
  renderWithIntl(
    <RowAction
      action={action}
      hidden={{ tokenId: '7' }}
      label="Revoke"
      pendingLabel="Revoking"
      confirm={confirm}
    />,
  )
  return action
}

describe('RowAction', () => {
  it('does not run an irreversible action the reader declines (#34)', async () => {
    const ask = vi.spyOn(window, 'confirm').mockReturnValue(false)
    const action = setup('Revoke the token "ci"?')
    await userEvent.click(screen.getByRole('button', { name: 'Revoke' }))
    expect(ask).toHaveBeenCalledWith('Revoke the token "ci"?')
    expect(action).not.toHaveBeenCalled()
  })

  it('runs it once the reader confirms, and announces the result', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true)
    const heard: string[] = []
    const listen = (event: Event) => heard.push((event as CustomEvent<string>).detail)
    window.addEventListener('rc:flash', listen)
    const action = setup('Sure?')
    await userEvent.click(screen.getByRole('button', { name: 'Revoke' }))
    await waitFor(() => expect(action).toHaveBeenCalledTimes(1))
    await waitFor(() => expect(heard).toEqual(['done']))
    window.removeEventListener('rc:flash', listen)
  })

  it('asks nothing when no confirmation is set', async () => {
    const ask = vi.spyOn(window, 'confirm')
    const action = setup()
    await userEvent.click(screen.getByRole('button', { name: 'Revoke' }))
    await waitFor(() => expect(action).toHaveBeenCalledTimes(1))
    expect(ask).not.toHaveBeenCalled()
  })
})
