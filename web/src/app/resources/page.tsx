import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'

import { EmptyState } from '@/components/EmptyState'
import { PageHeader } from '@/components/PageHeader'
import { ResourceExplorer } from '@/components/ResourceExplorer'
import { getResources } from '@/lib/api/queries'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('resources')
  return { title: t('title') }
}

/** Resources — `GET /resources`, filtered client-side by kind and search (AC-WEB.5). */
export default async function ResourcesPage() {
  const t = await getTranslations('resources')
  const resources = await getResources()

  if (!resources) {
    return (
      <>
        <PageHeader title={t('title')} subtitle={t('subtitle')} />
        <EmptyState title={t('unavailable')} />
      </>
    )
  }

  return (
    <>
      <PageHeader title={t('title')} subtitle={t('subtitle')} />
      <ResourceExplorer resources={resources} />
    </>
  )
}
