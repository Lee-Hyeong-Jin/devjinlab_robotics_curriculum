import { describe, expect, it } from 'vitest'

import type { CourseSummary } from './api/types'
import { selectedCourseId } from './courses'

const course = (id: string): CourseSummary => ({
  id,
  title: id,
  summary: '',
  tags: [],
  module_count: 1,
  lesson_count: 1,
  lang: 'ko',
})

const COURSES = [course('robotics-expert'), course('robotics-research')]

describe('selectedCourseId', () => {
  it('honours the requested course', () => {
    expect(selectedCourseId(COURSES, 'robotics-research', 'robotics-expert')).toBe(
      'robotics-research',
    )
  })

  it('falls back to the configured default when none is requested', () => {
    expect(selectedCourseId(COURSES, undefined, 'robotics-expert')).toBe('robotics-expert')
  })

  it('ignores a course that does not exist, rather than showing nothing', () => {
    expect(selectedCourseId(COURSES, 'made-up', 'robotics-expert')).toBe('robotics-expert')
  })

  it('falls back to the first course when the configured default is not there either', () => {
    // A deployment whose RC_DEFAULT_COURSE_ID is stale would otherwise show an empty roadmap.
    expect(selectedCourseId(COURSES, undefined, 'gone')).toBe('robotics-expert')
  })

  it('returns the fallback unchanged when there are no courses at all', () => {
    expect(selectedCourseId([], undefined, 'robotics-expert')).toBe('robotics-expert')
  })
})
