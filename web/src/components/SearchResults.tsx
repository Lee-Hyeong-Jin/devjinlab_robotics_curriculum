import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import type { SearchHit } from '@/lib/api/types'

import { Card } from './Card'
import { Chip } from './Chip'
import { EmptyState } from './EmptyState'

export interface SearchResultsProps {
  query: string
  hits: SearchHit[] | null
}

/** Result list for `/search` — lessons and resources, each linking to its lesson. */
export async function SearchResults({ query, hits }: SearchResultsProps) {
  const t = await getTranslations('search')

  if (query.trim().length < 2) return <EmptyState title={t('tooShort')} />
  if (!hits) return <EmptyState title={t('unavailable')} />
  if (hits.length === 0) return <EmptyState title={t('noResults', { query })} />

  return (
    <>
      <p className="text-muted mb-3 text-sm" role="status">
        {t('count', { count: hits.length })}
      </p>
      <ul className="flex flex-col gap-3">
        {hits.map((hit) => (
          <li key={`${hit.kind}-${hit.id}`}>
            <Card className="hover:border-border-accent transition-colors">
              <Link href={`/lessons/${encodeURIComponent(hit.lesson_id)}`} className="block">
                <span className="mb-1 flex flex-wrap items-center gap-2">
                  <Chip tone={hit.kind === 'lesson' ? 'accent' : 'neutral'}>{t(hit.kind)}</Chip>
                  <span className="text-primary font-medium">{hit.title}</span>
                </span>
                <span className="text-muted block text-sm">{hit.snippet}</span>
                <span className="text-muted mt-1 block font-mono text-xs">{hit.lesson_id}</span>
              </Link>
            </Card>
          </li>
        ))}
      </ul>
    </>
  )
}
