import type { Metadata } from 'next'
import { getLocale, getTranslations } from 'next-intl/server'

import { EmptyState } from '@/components/EmptyState'
import { JsonLd } from '@/components/JsonLd'
import { PageHeader } from '@/components/PageHeader'
import { ResourceExplorer } from '@/components/ResourceExplorer'
import { getLessonNames, getResources } from '@/lib/api/queries'
import { localizedPageSeo } from '@/lib/seo-server'
import { breadcrumbs, collectionPageSchema } from '@/lib/structured-data'

export async function generateMetadata(): Promise<Metadata> {
  const [t, resources] = await Promise.all([getTranslations('seo'), getResources()])
  return localizedPageSeo({
    path: '/resources',
    title: t('resourcesTitle'),
    absoluteTitle: true,
    description: t('resourcesDescription', { count: resources?.length ?? 0 }),
    publishable: true,
  })
}

/** Resources — `GET /resources`, filtered client-side by kind and search (AC-WEB.5). */
export default async function ResourcesPage() {
  const [t, tApp, locale] = await Promise.all([
    getTranslations('resources'),
    getTranslations('app'),
    getLocale(),
  ])
  const resources = await getResources()

  if (!resources) {
    return (
      <>
        <PageHeader title={t('title')} subtitle={t('subtitle')} />
        <EmptyState title={t('unavailable')} />
      </>
    )
  }

  const names = await getLessonNames()
  const lessonTitles = Object.fromEntries(
    Object.entries(names).map(([id, name]) => [id, name.title]),
  )

  return (
    <>
      <JsonLd
        data={[
          collectionPageSchema(t('title'), t('subtitle'), '/resources', locale),
          breadcrumbs([
            [tApp('title'), '/'],
            [t('title'), '/resources'],
          ]),
        ]}
      />
      <PageHeader title={t('title')} subtitle={t('subtitle')} />
      <ResourceExplorer resources={resources} lessonTitles={lessonTitles} />
    </>
  )
}
