/**
 * Pure derivations over progress data. No API, no React — unit tested directly.
 */
import type { LessonState, LessonStatus } from './api/types'

/**
 * The four states a lesson or module is shown in. This is the UI's vocabulary —
 * it matches the `<StatusDot>` variants in Figma (`10-2` … `10-5`) — and is
 * derived from the API's `status` + `locked`, which is how the contract models it.
 */
export type LockState = 'done' | 'in_progress' | 'available' | 'locked'

/** The display state of one lesson: `locked` only matters while it is unfinished. */
export function lessonLockState(state: {
  status?: LessonStatus
  locked?: boolean | null
}): LockState {
  if (state.status === 'done') return 'done'
  if (state.status === 'in_progress') return 'in_progress'
  return state.locked ? 'locked' : 'available'
}

/** The display state of a lesson known only by its progress status. */
export function lockStateFromStatus(status: LessonStatus | undefined): LockState {
  return lessonLockState({ status, locked: false })
}

/** Roll lesson states up to the module: done > in-progress > available > locked. */
export function moduleState(states: readonly LockState[]): LockState {
  if (states.length === 0) return 'available'
  if (states.every((state) => state === 'done')) return 'done'
  if (states.some((state) => state === 'in_progress' || state === 'done')) return 'in_progress'
  if (states.every((state) => state === 'locked')) return 'locked'
  return 'available'
}

/** `part / total`, or 0 when there is nothing to divide by. */
export function ratio(part: number, total: number): number {
  return total > 0 ? part / total : 0
}

/** Arithmetic mean, or 0 for an empty list. */
export function average(values: readonly number[]): number {
  return values.length > 0 ? values.reduce((sum, value) => sum + value, 0) / values.length : 0
}

/** How many of these states are done. */
export function doneCount(states: readonly LockState[]): number {
  return states.filter((state) => state === 'done').length
}

/** The API reports stage progress as whole percent; the UI works in 0–1. */
export function fromPercent(percent: number | null | undefined): number {
  return Number.isFinite(percent) ? Math.min(Math.max((percent as number) / 100, 0), 1) : 0
}

/** Course-wide completion from every lesson's state, as a 0–1 ratio. */
export function courseProgress(lessons: readonly LessonState[]): number {
  const states = lessons.map((lesson) => lessonLockState(lesson))
  return ratio(doneCount(states), states.length)
}
