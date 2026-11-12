import type { ChipTone } from '@/components/Chip'

import type { ResourceKind } from './api/types'

/**
 * Chip tone per resource kind.
 *
 * `Record<ResourceKind, …>` on purpose: the type is generated from the API contract, so a
 * kind added there fails the typecheck here until it is given a tone. Shared by the lesson
 * sidebar and the resources table, which used to keep two copies of this map.
 *
 * Reading matter is `accent`, watching is `warning`, and the research track's own kinds
 * (paper, dataset, code, notes) stay `neutral` so a lesson listing many of them does not
 * turn into a wall of colour.
 */
export const RESOURCE_KIND_TONE: Record<ResourceKind, ChipTone> = {
  book: 'accent',
  course: 'accent',
  video: 'warning',
  article: 'neutral',
  paper: 'neutral',
  dataset: 'neutral',
  code: 'neutral',
  notes: 'neutral',
  other: 'neutral',
}
