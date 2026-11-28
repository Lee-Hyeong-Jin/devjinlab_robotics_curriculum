import type { GoalPath } from './api/types'
import type { LockState } from './progress'

export type { GoalPath }

/**
 * A goal-based learning path on the roadmap (#52).
 *
 * The course is one long line; a goal ("a robot that navigates") needs only part of it. The
 * API computes which lessons that is. Here the reader's own progress is laid over it: how much
 * of the path is done, how much time is left, and which modules the goal does not touch.
 */
export interface GoalProgress {
  done: number
  total: number
  remainingMinutes: number
  /** The first lesson on the path that is not done, if any. */
  next: GoalPath['lessons'][number] | null
}

/** Which goal `?goal=` selects, or `null` for none or for one the course does not have. */
export function selectGoal(
  goals: readonly GoalPath[],
  requested: string | undefined,
): GoalPath | null {
  if (!requested) return null
  return goals.find((goal) => goal.id === requested) ?? null
}

/** The reader's progress along a path, given each lesson's state. */
export function goalProgress(
  goal: GoalPath,
  states: Readonly<Record<string, LockState | undefined>>,
): GoalProgress {
  const pending = goal.lessons.filter((lesson) => states[lesson.id] !== 'done')
  return {
    done: goal.lessons.length - pending.length,
    total: goal.lessons.length,
    remainingMinutes: pending.reduce((sum, lesson) => sum + lesson.estimated_minutes, 0),
    next: pending[0] ?? null,
  }
}

/** How many of a module's lessons are on the path (0 means the goal does not need the module). */
export function lessonsOnPath(goal: GoalPath, moduleId: string): number {
  return goal.lessons.filter((lesson) => lesson.module_id === moduleId).length
}

/** `/roadmap` for a course and a goal; defaults are left out of the address. */
export function roadmapHref(
  courseId: string,
  defaultCourse: string,
  goalId?: string | null,
): string {
  const params = new URLSearchParams()
  if (courseId !== defaultCourse) params.set('course', courseId)
  if (goalId) params.set('goal', goalId)
  const query = params.toString()
  return query ? `/roadmap?${query}` : '/roadmap'
}
