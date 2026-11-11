import { getTranslations } from 'next-intl/server'

import { ButtonLink } from '@/components/Button'
import { EmptyState } from '@/components/EmptyState'

export default async function NotFound() {
  const t = await getTranslations('error')
  return (
    <EmptyState
      title={t('notFoundTitle')}
      body={t('notFoundBody')}
      action={
        <ButtonLink href="/" kind="secondary">
          {t('home')}
        </ButtonLink>
      }
    />
  )
}
