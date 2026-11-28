import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { Button } from '@/components/Button'
import { EmptyState } from '@/components/EmptyState'
import { JsonLd } from '@/components/JsonLd'
import { PageHeader } from '@/components/PageHeader'
import { ResourceTable } from '@/components/ResourceTable'
import { getLessonNames, getResources } from '@/lib/api/queries'
import type { ResourceKind } from '@/lib/api/types'
import { cx } from '@/lib/cx'
import {
  ALL_KINDS,
  filterResources,
  kindCounts,
  paginate,
  readResourceFilter,
  resourcesHref,
} from '@/lib/resources'
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

interface Props {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}

/**
 * Resources — `GET /resources`, filtered by kind and text and shown a page at a time
 * (AC-WEB.5). The filter lives in the URL (`?kind=paper&q=kalman&page=2`) and is applied on
 * the server, so a filtered view can be linked to and the page stays small (#57).
 */
export default async function ResourcesPage({ searchParams }: Props) {
  const [t, tApp, tKind, locale, params] = await Promise.all([
    getTranslations('resources'),
    getTranslations('app'),
    getTranslations('kind'),
    getLocale(),
    searchParams,
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

  const kinds = kindCounts(resources)
  const filter = readResourceFilter(
    params,
    kinds.map((entry) => entry.kind),
  )
  const matching = filterResources(resources, filter)
  const page = paginate(matching, filter.page)
  // Titles are looked up for the lessons on this page only.
  const names = await getLessonNames()
  const lessonTitles = Object.fromEntries(
    page.rows
      .flatMap((row) => row.lesson_ids ?? [])
      .filter((id) => names[id])
      .map((id) => [id, names[id]!.title]),
  )
  const kindLinks = [
    { kind: ALL_KINDS, label: t('filterAll'), count: resources.length },
    ...kinds.map((entry) => ({
      kind: entry.kind,
      label: tKind(entry.kind as ResourceKind),
      count: entry.count,
    })),
  ]

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

      <div className="flex flex-col gap-4">
        <form
          method="get"
          action="/resources"
          role="search"
          className="flex flex-wrap items-end gap-3"
        >
          {filter.kind !== ALL_KINDS ? (
            <input type="hidden" name="kind" value={filter.kind} />
          ) : null}
          <div className="flex min-w-0 flex-1 flex-col gap-1.5 sm:max-w-sm">
            <label htmlFor="resource-search" className="text-primary text-sm font-medium">
              {t('search')}
            </label>
            <input
              id="resource-search"
              type="search"
              name="q"
              defaultValue={filter.query}
              maxLength={100}
              placeholder={t('searchPlaceholder')}
              className="bg-surface border-border-default text-primary placeholder:text-muted min-h-11 w-full rounded-lg border px-3 py-2 text-base sm:text-sm"
            />
          </div>
          <Button type="submit" kind="secondary">
            {t('searchSubmit')}
          </Button>
        </form>

        <nav aria-label={t('filterKind')}>
          <ul className="flex flex-wrap gap-2">
            {kindLinks.map((entry) => {
              const current = entry.kind === filter.kind
              return (
                <li key={entry.kind}>
                  <Link
                    href={resourcesHref({ kind: entry.kind, query: filter.query })}
                    aria-current={current ? 'page' : undefined}
                    className={cx(
                      'inline-flex min-h-11 items-center gap-1.5 rounded-full border px-3 py-1 text-sm sm:min-h-9',
                      current
                        ? 'bg-accent-light border-border-accent text-accent font-medium'
                        : 'bg-surface border-border-default text-primary hover:bg-subtle',
                    )}
                  >
                    {entry.label}
                    <span className="text-muted text-xs tabular-nums">{entry.count}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        <p className="text-muted text-sm" role="status">
          {page.total === 0
            ? t('count', { count: 0 })
            : page.pages === 1
              ? t('count', { count: page.total })
              : t('countRange', { from: page.from, to: page.to, total: page.total })}
        </p>

        <ResourceTable resources={page.rows} lessonTitles={lessonTitles} />

        {page.pages > 1 ? (
          <nav
            aria-label={t('pages')}
            className="flex flex-wrap items-center justify-between gap-3"
          >
            {page.page > 1 ? (
              <Link
                href={resourcesHref({ ...filter, page: page.page - 1 })}
                rel="prev"
                className="text-accent text-sm underline underline-offset-2"
              >
                ← {t('previousPage')}
              </Link>
            ) : (
              <span />
            )}
            <span className="text-muted text-sm tabular-nums">
              {t('pageOf', { page: page.page, pages: page.pages })}
            </span>
            {page.page < page.pages ? (
              <Link
                href={resourcesHref({ ...filter, page: page.page + 1 })}
                rel="next"
                className="text-accent text-sm underline underline-offset-2"
              >
                {t('nextPage')} →
              </Link>
            ) : (
              <span />
            )}
          </nav>
        ) : null}
      </div>
    </>
  )
}
