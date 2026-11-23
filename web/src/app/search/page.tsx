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

/** `GET /search` accepts at most this many characters. */
const MAX_QUERY_LENGTH = 200

interface Props {
  searchParams: Promise<{ q?: string }>
}

/** Search — `GET /search?q=` over lessons and resources (frontend.md §2). */
export default async function SearchPage({ searchParams }: Props) {
  const [t, params] = await Promise.all([getTranslations('search'), searchParams])
  const query = params.q ?? ''
  // The API refuses a longer query (422); the reader gets a sentence about it, not an error
  // screen (QA B-30).
  const length = query.trim().length
  const hits = length >= 2 && length <= MAX_QUERY_LENGTH ? await search(query) : []

  return (
    <>
      <PageHeader title={t('title')} subtitle={t('subtitle')} />
      <SearchForm initialQuery={query} />
      <SearchResults query={query} hits={hits} maxLength={MAX_QUERY_LENGTH} />
    </>
  )
}
