import type { CourseSummary } from './api/types'

/**
 * Which course a screen is showing.
 *
 * `?course=<id>` wins, then the configured default (`RC_DEFAULT_COURSE_ID`), then the first
 * course the API lists. The fallbacks matter: the default is a single fixed id, so a
 * deployment that adds a second course (the research track) would otherwise have no way to
 * reach it, and a deployment whose default id does not exist would show nothing at all.
 */
export function selectedCourseId(
  courses: readonly CourseSummary[],
  requested: string | undefined,
  fallback: string,
): string {
  const ids = courses.map((course) => course.id)
  if (requested && ids.includes(requested)) return requested
  if (ids.includes(fallback)) return fallback
  return ids[0] ?? fallback
}
