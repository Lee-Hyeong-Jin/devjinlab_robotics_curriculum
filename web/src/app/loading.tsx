import { getTranslations } from 'next-intl/server'

/**
 * Route-level loading state. Pages are server-rendered on demand, so this is
 * what a reader sees while the API answers. `role="status"` announces it once
 * rather than on every skeleton block.
 */
export default async function Loading() {
  const t = await getTranslations('app')
  return (
    <div role="status" aria-live="polite" className="flex flex-col gap-4">
      <span className="sr-only">{t('loading')}</span>
      <span className="bg-subtle h-8 w-64 animate-pulse rounded" aria-hidden="true" />
      <span className="bg-subtle h-4 w-96 max-w-full animate-pulse rounded" aria-hidden="true" />
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4" aria-hidden="true">
        {[0, 1, 2, 3].map((index) => (
          <span
            key={index}
            className="bg-surface border-border-default h-28 animate-pulse rounded-[var(--radius-card)] border"
          />
        ))}
      </div>
    </div>
  )
}
