import { describe, expect, it } from 'vitest'

import { goalProgress, lessonsOnPath, roadmapHref, selectGoal, type GoalPath } from './goal-path'

const GOAL: GoalPath = {
  id: 'mobile-robot',
  title: 'Make a robot move',
  summary: 's',
  target_ids: ['m3-c'],
  lesson_ids: ['m1-a', 'm1-b', 'm3-c'],
  lessons: [
    { id: 'm1-a', title: 'A', module_id: 'm1', estimated_minutes: 60 },
    { id: 'm1-b', title: 'B', module_id: 'm1', estimated_minutes: 90 },
    { id: 'm3-c', title: 'C', module_id: 'm3', estimated_minutes: 100 },
  ],
  estimated_minutes: 250,
}

describe('goal paths on the roadmap (#52)', () => {
  it('selects a goal the course has, and nothing else', () => {
    expect(selectGoal([GOAL], 'mobile-robot')).toBe(GOAL)
    expect(selectGoal([GOAL], 'nope')).toBeNull()
    expect(selectGoal([GOAL], undefined)).toBeNull()
    expect(selectGoal([], 'mobile-robot')).toBeNull()
  })

  it('lays the progress of the reader over the path', () => {
    expect(goalProgress(GOAL, {})).toEqual({
      done: 0,
      total: 3,
      remainingMinutes: 250,
      next: GOAL.lessons[0],
    })
    // A lesson in progress is not done yet; the next step is the first one not finished.
    const partly = goalProgress(GOAL, { 'm1-a': 'done', 'm1-b': 'in_progress' })
    expect(partly).toMatchObject({ done: 1, remainingMinutes: 190 })
    expect(partly.next?.id).toBe('m1-b')
    const finished = goalProgress(GOAL, { 'm1-a': 'done', 'm1-b': 'done', 'm3-c': 'done' })
    expect(finished).toEqual({ done: 3, total: 3, remainingMinutes: 0, next: null })
  })

  it('knows which modules a goal does not touch', () => {
    expect(lessonsOnPath(GOAL, 'm1')).toBe(2)
    expect(lessonsOnPath(GOAL, 'm3')).toBe(1)
    expect(lessonsOnPath(GOAL, 'm7')).toBe(0)
  })

  it('keeps the goal in the address', () => {
    expect(roadmapHref('expert', 'expert')).toBe('/roadmap')
    expect(roadmapHref('expert', 'expert', 'navigation')).toBe('/roadmap?goal=navigation')
    expect(roadmapHref('research', 'expert', 'x')).toBe('/roadmap?course=research&goal=x')
    expect(roadmapHref('research', 'expert', null)).toBe('/roadmap?course=research')
  })
})
