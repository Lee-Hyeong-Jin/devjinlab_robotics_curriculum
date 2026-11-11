import { describe, expect, it } from 'vitest'

import type { LockState } from './api/types'
import { average, doneCount, lockStateFromStatus, moduleState, ratio } from './progress'

describe('moduleState', () => {
  it('is available for a module with no lessons', () => {
    expect(moduleState([])).toBe('available')
  })

  it('is done only when every lesson is done', () => {
    expect(moduleState(['done', 'done'])).toBe('done')
    expect(moduleState(['done', 'available'])).toBe('in_progress')
  })

  it('is in_progress as soon as one lesson is started or finished', () => {
    expect(moduleState(['in_progress', 'locked'])).toBe('in_progress')
    expect(moduleState(['done', 'locked'])).toBe('in_progress')
  })

  it('is locked only when every lesson is locked', () => {
    expect(moduleState(['locked', 'locked'])).toBe('locked')
    expect(moduleState(['locked', 'available'])).toBe('available')
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
    const states: LockState[] = ['done', 'in_progress', 'done', 'locked']
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
