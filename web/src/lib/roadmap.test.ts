import { describe, expect, it } from 'vitest'

import type { Roadmap } from './api/types'

import { toStageViews } from './roadmap'

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
    expect(basic?.modules[1]?.state).toBe('locked')
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
