import type { ResourceRef } from './api/types'

/**
 * The resource library, one page at a time (#57).
 *
 * The page used to send all 320-odd resources to the browser twice — once as HTML and once as
 * the data for a client-side filter — which made it an 830 KB document. Filtering and paging
 * now happen on the server and the state lives in the URL (`?kind=paper&q=kalman&page=2`), so
 * a filtered view can be linked to and the page carries only the rows it shows.
 */
export const RESOURCE_PAGE_SIZE = 25

export const ALL_KINDS = 'all'

export interface ResourceFilter {
  /** A resource kind, or `all`. */
  kind: string
  /** Free text matched against title, scope note and address. */
  query: string
  /** 1-based. */
  page: number
}

export interface KindCount {
  kind: string
  count: number
}

function kindOf(resource: ResourceRef): string {
  return resource.kind ?? 'other'
}

/** How many resources there are of each kind, most common first. */
export function kindCounts(resources: readonly ResourceRef[]): KindCount[] {
  const counts = new Map<string, number>()
  for (const resource of resources)
    counts.set(kindOf(resource), (counts.get(kindOf(resource)) ?? 0) + 1)
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([kind, count]) => ({ kind, count }))
}

/** Read the filter out of the page's search parameters, tolerating anything a URL can hold. */
export function readResourceFilter(
  params: Record<string, string | string[] | undefined>,
  kinds: readonly string[],
): ResourceFilter {
  const first = (value: string | string[] | undefined) => (Array.isArray(value) ? value[0] : value)
  const kind = first(params.kind) ?? ALL_KINDS
  const page = Number(first(params.page) ?? '1')
  return {
    kind: kinds.includes(kind) ? kind : ALL_KINDS,
    query: (first(params.q) ?? '').trim().slice(0, 100),
    page: Number.isInteger(page) && page >= 1 ? page : 1,
  }
}

/** The resources that match the kind and the text, in their original (teaching) order. */
export function filterResources(
  resources: readonly ResourceRef[],
  filter: Pick<ResourceFilter, 'kind' | 'query'>,
): ResourceRef[] {
  const needle = filter.query.trim().toLowerCase()
  return resources.filter((resource) => {
    if (filter.kind !== ALL_KINDS && kindOf(resource) !== filter.kind) return false
    if (needle === '') return true
    const haystack = `${resource.title} ${resource.note ?? ''} ${resource.url ?? ''}`
    return haystack.toLowerCase().includes(needle)
  })
}

export interface Page<Row> {
  rows: Row[]
  /** The page actually shown: a page past the end falls back to the last one. */
  page: number
  pages: number
  total: number
  /** 1-based position of the first and last row shown; both 0 when there is none. */
  from: number
  to: number
}

export function paginate<Row>(
  rows: readonly Row[],
  page: number,
  size = RESOURCE_PAGE_SIZE,
): Page<Row> {
  const pages = Math.max(1, Math.ceil(rows.length / size))
  const shown = Math.min(Math.max(1, page), pages)
  const start = (shown - 1) * size
  const slice = rows.slice(start, start + size)
  return {
    rows: slice,
    page: shown,
    pages,
    total: rows.length,
    from: slice.length === 0 ? 0 : start + 1,
    to: start + slice.length,
  }
}

/** `/resources` with the filter in the query; defaults are left out so the plain address stays. */
export function resourcesHref(filter: Partial<ResourceFilter>): string {
  const params = new URLSearchParams()
  if (filter.kind && filter.kind !== ALL_KINDS) params.set('kind', filter.kind)
  if (filter.query) params.set('q', filter.query)
  if (filter.page && filter.page > 1) params.set('page', String(filter.page))
  const query = params.toString()
  return query ? `/resources?${query}` : '/resources'
}
