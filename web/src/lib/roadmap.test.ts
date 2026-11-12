import { describe, expect, it } from 'vitest'

import type { Roadmap } from './api/types'

import { toStageViews, toStageViewsFromCourse } from './roadmap'

const ROADMAP: Roadmap = {
  stages: [
    {
      course_id: 'robotics-expert',
      level: '기초',
      progress: 0.25,
      modules: [
        {
          id: 'm1',
          title: '수학·물리',
          progress: 0.5,
          state: 'in_progress',
          lessons: [
            { id: 'l1', title: '벡터와 행렬', state: 'done' },
            { id: 'l2', title: '좌표 변환', state: 'available' },
          ],
        },
        {
          id: 'm2',
          title: 'ROS 2',
          progress: 0,
          state: 'locked',
          lessons: [{ id: 'l3', title: '노드와 토픽', state: 'locked' }],
        },
      ],
    },
    {
      course_id: 'robotics-expert',
      level: null,
      progress: 0,
      modules: [],
    },
  ],
}

describe('toStageViews', () => {
  it('returns nothing without a roadmap', () => {
    expect(toStageViews(null)).toEqual([])
    expect(toStageViews({ stages: [] })).toEqual([])
  })

  it('keeps the API stage, module and lesson tree', () => {
    const [basic] = toStageViews(ROADMAP)
    expect(basic?.level).toBe('기초')
    expect(basic?.modules.map((module) => module.id)).toEqual(['m1', 'm2'])
    expect(basic?.modules[0]?.lessons.map((lesson) => lesson.state)).toEqual(['done', 'available'])
  })

  it('passes module and stage progress through unchanged (already 0-1)', () => {
    const [basic] = toStageViews(ROADMAP)
    expect(basic?.progress).toBe(0.25)
    expect(basic?.modules[0]?.progress).toBe(0.5)
  })

  it("reads an old server's `locked` as available, so no screen renders a lock (ADR 0015)", () => {
    const [basic] = toStageViews(ROADMAP)
    expect(basic?.modules[1]?.state).toBe('available')
    expect(basic?.modules[1]?.lessons[0]?.state).toBe('available')
  })

  it('adds the per-stage lesson counts the API does not carry', () => {
    const [basic] = toStageViews(ROADMAP)
    expect(basic?.lessonsTotal).toBe(3)
    expect(basic?.lessonsDone).toBe(1)
  })

  it('renders a stage with no level as an empty label rather than "null"', () => {
    const [, unlabelled] = toStageViews(ROADMAP)
    expect(unlabelled?.level).toBe('')
    expect(unlabelled?.lessonsTotal).toBe(0)
  })
})

describe('toStageViewsFromCourse', () => {
  const COURSE = {
    id: 'robotics-expert',
    title: '로보틱스',
    summary: '',
    tags: [],
    module_count: 2,
    lesson_count: 7,
    lang: 'ko',
    stages: [
      {
        level: '기초' as const,
        level_label: 'Foundation',
        modules: [
          {
            id: 'm1',
            title: '수학',
            summary: '',
            level: '기초' as const,
            level_label: 'Foundation',
            course_id: 'robotics-expert',
            lesson_count: 3,
            estimated_minutes: 90,
            lang: 'ko',
          },
          {
            id: 'm2',
            title: '운동학',
            summary: '',
            level: '기초' as const,
            level_label: 'Foundation',
            course_id: 'robotics-expert',
            lesson_count: 4,
            estimated_minutes: 120,
            lang: 'ko',
          },
        ],
      },
    ],
  }

  it('builds the stage structure an anonymous reader may see (ADR 0016)', () => {
    const [stage] = toStageViewsFromCourse(COURSE)
    expect(stage?.levelLabel).toBe('Foundation')
    expect(stage?.modules.map((module) => module.id)).toEqual(['m1', 'm2'])
    // The lesson count survives even though the per-lesson list does not.
    expect(stage?.modules.map((module) => module.lessonsTotal)).toEqual([3, 4])
    expect(stage?.lessonsTotal).toBe(7)
  })

  it('reports no progress, because there is no reader to have any', () => {
    const [stage] = toStageViewsFromCourse(COURSE)
    expect(stage?.progress).toBe(0)
    expect(stage?.lessonsDone).toBe(0)
    expect(stage?.modules.every((module) => module.state === 'available')).toBe(true)
  })

  it('returns nothing for a missing course', () => {
    expect(toStageViewsFromCourse(null)).toEqual([])
  })
})
