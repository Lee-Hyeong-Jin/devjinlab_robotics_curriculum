import { render, type RenderOptions, type RenderResult } from '@testing-library/react'
import { NextIntlClientProvider } from 'next-intl'
import type { ReactElement, ReactNode } from 'react'

import ko from '../../messages/ko.json'

/** Render with the ko message catalogue, as the app does by default. */
export function renderWithIntl(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
): RenderResult {
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <NextIntlClientProvider locale="ko" messages={ko} timeZone="Asia/Seoul">
        {children}
      </NextIntlClientProvider>
    )
  }
  return render(ui, { wrapper: Wrapper, ...options })
}

export { ko as koMessages }
