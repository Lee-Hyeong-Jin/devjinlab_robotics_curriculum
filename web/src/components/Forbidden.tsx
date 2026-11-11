import { getTranslations } from 'next-intl/server'

import { ButtonLink } from './Button'
import { EmptyState } from './EmptyState'

/**
 * The 403 screen. Shown when the API refuses for lack of permission — the
 * frontend reflects that decision, it never makes it (AC-WEB.4).
 */
export async function Forbidden() {
  const t = await getTranslations('error')
  return (
    <EmptyState
      title={t('forbidden')}
      body={t('forbiddenBody')}
      action={
        <ButtonLink href="/" kind="secondary">
          {t('home')}
        </ButtonLink>
      }
    />
  )
}
