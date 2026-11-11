/**
 * Pure derivations over progress data. No API, no React — unit tested directly.
 */
import type { LessonStatus, LockState } from './api/types'

/** Roll lesson lock states up to the module: done > in-progress > available > locked. */
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

/** The lock state implied by a lesson's progress status, when the API omits it. */
export function lockStateFromStatus(status: LessonStatus | undefined): LockState {
  switch (status) {
    case 'done':
      return 'done'
    case 'in_progress':
      return 'in_progress'
    default:
      return 'available'
  }
}

/** How many of these lessons are done. */
export function doneCount(states: readonly LockState[]): number {
  return states.filter((state) => state === 'done').length
}
