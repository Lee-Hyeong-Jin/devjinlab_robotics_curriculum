import type { Course } from './api/types'

/** Lessons, modules and estimated minutes of a course, summed from its stages. */
export function courseTotals(course: Course | null | undefined): {
  modules: number
  lessons: number
  minutes: number
} {
  const modules = (course?.stages ?? []).flatMap((stage) => stage.modules ?? [])
  return {
    modules: modules.length,
    lessons: modules.reduce((sum, module) => sum + (module.lesson_count ?? 0), 0),
    minutes: modules.reduce((sum, module) => sum + (module.estimated_minutes ?? 0), 0),
  }
}

/** Whole hours for a count of minutes, never below 1 once there is any time at all. */
export function roundHours(minutes: number): number {
  return minutes <= 0 ? 0 : Math.max(1, Math.round(minutes / 60))
}
