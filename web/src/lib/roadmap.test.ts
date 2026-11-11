import { describe, expect, it } from 'vitest'

import { course, lessonState, lessonSummary, moduleSummary } from '@/test/factories'

import { composeRoadmap } from './roadmap'

const COURSE = course({
  stages: [
    {
      level: '기초',
      modules: [
        moduleSummary({ id: 'm1', title: '수학·물리' }),
        moduleSummary({ id: 'm2', title: 'ROS 2' }),
      ],
    },
    {
      level: '중급',
      modules: [moduleSummary({ id: 'm5', title: 'SLAM', level: '중급' })],
    },
  ],
})

const LESSONS = [
  lessonState({
    lesson: lessonSummary({ id: 'l1', title: '벡터와 행렬', module_id: 'm1' }),
    status: 'done',
  }),
  lessonState({
    lesson: lessonSummary({ id: 'l2', title: '좌표 변환', module_id: 'm1' }),
    status: 'not_started',
  }),
  lessonState({
    lesson: lessonSummary({ id: 'l3', title: '노드와 토픽', module_id: 'm2' }),
    status: 'not_started',
    locked: true,
  }),
  lessonState({
    lesson: lessonSummary({ id: 'l4', title: '칼만 필터', module_id: 'm5' }),
    status: 'in_progress',
  }),
]

describe('composeRoadmap', () => {
  it('returns nothing without a course', () => {
    expect(composeRoadmap(null, LESSONS)).toEqual([])
    expect(composeRoadmap(course({ stages: [] }), LESSONS)).toEqual([])
  })

  it('groups the course modules by stage', () => {
    const stages = composeRoadmap(COURSE, LESSONS)
    expect(stages.map((stage) => stage.level)).toEqual(['기초', '중급'])
    expect(stages[0]?.modules.map((module) => module.id)).toEqual(['m1', 'm2'])
    expect(stages[1]?.modules.map((module) => module.id)).toEqual(['m5'])
  })

  it('derives each lesson state from status and the lock flag', () => {
    const [basic] = composeRoadmap(COURSE, LESSONS)
    expect(basic?.modules[0]?.lessons.map((lesson) => lesson.state)).toEqual(['done', 'available'])
    expect(basic?.modules[1]?.lessons.map((lesson) => lesson.state)).toEqual(['locked'])
  })

  it('rolls lesson states up to the module', () => {
    const [basic, intermediate] = composeRoadmap(COURSE, LESSONS)
    // One of two done.
    expect(basic?.modules[0]?.state).toBe('in_progress')
    expect(basic?.modules[0]?.progress).toBe(0.5)
    // Its only lesson is locked.
    expect(basic?.modules[1]?.state).toBe('locked')
    expect(basic?.modules[1]?.progress).toBe(0)
    expect(intermediate?.modules[0]?.state).toBe('in_progress')
  })

  it('counts stage lessons and derives stage progress when the API reports none', () => {
    const [basic] = composeRoadmap(COURSE, LESSONS)
    expect(basic?.lessonsTotal).toBe(3)
    expect(basic?.lessonsDone).toBe(1)
    expect(basic?.progress).toBeCloseTo(1 / 3)
  })

  it('prefers the stage progress the API reports, converting whole percent', () => {
    const [basic] = composeRoadmap(COURSE, LESSONS, [{ level: '기초', progress: 80 }])
    expect(basic?.progress).toBe(0.8)
    // A stage the API did not report still falls back to the local count.
    const [, intermediate] = composeRoadmap(COURSE, LESSONS, [{ level: '기초', progress: 80 }])
    expect(intermediate?.progress).toBe(0)
  })

  it('leaves a module with no lesson states empty rather than complete', () => {
    const stages = composeRoadmap(COURSE, [])
    expect(stages[0]?.modules[0]?.lessons).toEqual([])
    expect(stages[0]?.modules[0]?.state).toBe('available')
    expect(stages[0]?.modules[0]?.progress).toBe(0)
  })

  it('ignores lesson states for modules outside the course view', () => {
    const stages = composeRoadmap(COURSE, [
      ...LESSONS,
      lessonState({
        lesson: lessonSummary({ id: 'lx', module_id: 'm99' }),
        status: 'done',
      }),
    ])
    expect(stages.flatMap((stage) => stage.modules).map((module) => module.id)).toEqual([
      'm1',
      'm2',
      'm5',
    ])
  })
})
