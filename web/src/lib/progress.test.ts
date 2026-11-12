import { describe, expect, it } from 'vitest'

import { lessonState, lessonSummary } from '@/test/factories'

import {
  average,
  courseProgress,
  doneCount,
  fromPercent,
  lessonLockState,
  lockStateFromStatus,
  moduleState,
  normalizeState,
  ratio,
  type LockState,
} from './progress'

describe('moduleState', () => {
  it('is available for a module with no lessons', () => {
    expect(moduleState([])).toBe('available')
  })

  it('is done only when every lesson is done', () => {
    expect(moduleState(['done', 'done'])).toBe('done')
    expect(moduleState(['done', 'available'])).toBe('in_progress')
  })

  it('is in_progress as soon as one lesson is started or finished', () => {
    expect(moduleState(['in_progress', 'available'])).toBe('in_progress')
    expect(moduleState(['done', 'available'])).toBe('in_progress')
  })

  it('is available while nothing has been started', () => {
    expect(moduleState(['available', 'available'])).toBe('available')
  })
})

describe('ratio', () => {
  it('divides, and returns 0 rather than NaN for an empty total', () => {
    expect(ratio(3, 4)).toBe(0.75)
    expect(ratio(0, 0)).toBe(0)
  })
})

describe('average', () => {
  it('averages, and returns 0 for an empty list', () => {
    expect(average([0.5, 1])).toBe(0.75)
    expect(average([])).toBe(0)
  })
})

describe('doneCount', () => {
  it('counts only done lessons', () => {
    const states: LockState[] = ['done', 'in_progress', 'done', 'available']
    expect(doneCount(states)).toBe(2)
  })
})

describe('lockStateFromStatus', () => {
  it('maps a progress status onto a lock state', () => {
    expect(lockStateFromStatus('done')).toBe('done')
    expect(lockStateFromStatus('in_progress')).toBe('in_progress')
    expect(lockStateFromStatus('not_started')).toBe('available')
    expect(lockStateFromStatus(undefined)).toBe('available')
  })
})

describe('lessonLockState', () => {
  it('maps the progress status, and nothing else', () => {
    expect(lessonLockState({ status: 'done' })).toBe('done')
    expect(lessonLockState({ status: 'in_progress' })).toBe('in_progress')
    expect(lessonLockState({ status: 'not_started' })).toBe('available')
    expect(lessonLockState({})).toBe('available')
  })
})

describe('normalizeState', () => {
  it('passes the real states through', () => {
    expect(normalizeState('done')).toBe('done')
    expect(normalizeState('in_progress')).toBe('in_progress')
    expect(normalizeState('available')).toBe('available')
  })

  it("reads an old server's `locked` as available, so no screen can render a lock", () => {
    expect(normalizeState('locked')).toBe('available')
    expect(normalizeState(null)).toBe('available')
    expect(normalizeState(undefined)).toBe('available')
    expect(normalizeState('nonsense')).toBe('available')
  })
})

describe('fromPercent', () => {
  it('converts whole percent to a 0-1 ratio and clamps', () => {
    expect(fromPercent(80)).toBe(0.8)
    expect(fromPercent(0)).toBe(0)
    expect(fromPercent(140)).toBe(1)
    expect(fromPercent(-5)).toBe(0)
    expect(fromPercent(null)).toBe(0)
    expect(fromPercent(undefined)).toBe(0)
  })
})

describe('courseProgress', () => {
  it('is the share of done lessons over every lesson', () => {
    const states = (['done', 'in_progress', 'not_started', 'done'] as const).map((status, index) =>
      lessonState({
        lesson: lessonSummary({ id: `l${index}` }),
        status,
        locked: status === 'not_started',
      }),
    )
    expect(courseProgress(states)).toBe(0.5)
  })

  it('is 0 for an empty course', () => {
    expect(courseProgress([])).toBe(0)
  })
})
