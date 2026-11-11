import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'

import { ButtonLink } from '@/components/Button'
import { EmptyState } from '@/components/EmptyState'
import { PageHeader } from '@/components/PageHeader'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('login')
  return { title: t('title') }
}

/**
 * Placeholder. The real sign-in screen (Figma `23-3`) lands with the P2-2
 * authentication API; until then this is the 401 redirect target so the flow in
 * `apiFetch` has somewhere to go.
 */
export default async function LoginPage() {
  const t = await getTranslations('login')
  return (
    <>
      <PageHeader title={t('title')} />
      <EmptyState
        title={t('title')}
        body={t('pending')}
        action={
          <ButtonLink href="/" kind="secondary">
            {t('back')}
          </ButtonLink>
        }
      />
    </>
  )
}
