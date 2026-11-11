'use client'

import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'

import { Button } from './Button'
import { SearchInput } from './SearchInput'

/** The `/search` query box. Submitting navigates, so results are shareable. */
export function SearchForm({ initialQuery }: { initialQuery: string }) {
  const t = useTranslations('search')
  const router = useRouter()
  const [query, setQuery] = useState(initialQuery)

  return (
    <form
      role="search"
      className="mb-6 flex flex-wrap items-end gap-3"
      onSubmit={(event) => {
        event.preventDefault()
        router.push(`/search?q=${encodeURIComponent(query.trim())}`)
      }}
    >
      <SearchInput
        label={t('label')}
        placeholder={t('placeholder')}
        value={query}
        onChange={setQuery}
      />
      <Button type="submit">{t('submit')}</Button>
    </form>
  )
}
