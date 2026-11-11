import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'

import { PageHeader } from '@/components/PageHeader'
import { SearchForm } from '@/components/SearchForm'
import { SearchResults } from '@/components/SearchResults'
import { search } from '@/lib/api/queries'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('search')
  return { title: t('title') }
}

interface Props {
  searchParams: Promise<{ q?: string }>
}

/** Search — `GET /search?q=` over lessons and resources (frontend.md §2). */
export default async function SearchPage({ searchParams }: Props) {
  const [t, params] = await Promise.all([getTranslations('search'), searchParams])
  const query = params.q ?? ''
  const hits = query.trim().length >= 2 ? await search(query) : []

  return (
    <>
      <PageHeader title={t('title')} subtitle={t('subtitle')} />
      <SearchForm initialQuery={query} />
      <SearchResults query={query} hits={hits} />
    </>
  )
}
