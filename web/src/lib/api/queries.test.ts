import { beforeEach, describe, expect, it, vi } from 'vitest'

import type { Course, Module, Roadmap, Status } from './types'

const apiGet = vi.fn()
const apiGetOrNull = vi.fn()

vi.mock('./client', () => ({ apiGet, apiGetOrNull }))

const { getRoadmap } = await import('./queries')

const COURSE: Course = {
  id: 'robotics-expert',
  title: '로보틱스 전문가 코스',
  stages: [
    {
      level: '기초',
      modules: [
        { id: 'm1', title: '수학·물리', level: '기초' },
        { id: 'm2', title: 'ROS 2 기초', level: '기초' },
      ],
    },
  ],
}

const MODULES: Record<string, Module> = {
  m1: {
    id: 'm1',
    title: '수학·물리',
    lessons: [
      { id: 'l1', title: '벡터와 행렬' },
      { id: 'l2', title: '좌표 변환' },
    ],
  },
  m2: {
    id: 'm2',
    title: 'ROS 2 기초',
    lessons: [{ id: 'l3', title: '노드와 토픽' }],
  },
}

const STATUS: Status = {
  lessons: [
    { lesson_id: 'l1', status: 'done', state: 'done' },
    { lesson_id: 'l2', status: 'not_started', state: 'available' },
    { lesson_id: 'l3', status: 'not_started', state: 'locked' },
  ],
}

beforeEach(() => {
  apiGet.mockReset()
  apiGetOrNull.mockReset()
})

describe('getRoadmap', () => {
  it('returns the API payload when /roadmap is implemented', async () => {
    const payload: Roadmap = { stages: [{ level: '기초', progress: 0.5, modules: [] }] }
    apiGetOrNull.mockImplementation((path: string) =>
      Promise.resolve(path === '/api/v1/roadmap' ? payload : null),
    )
    await expect(getRoadmap()).resolves.toEqual(payload)
    // No fallback fetching when the endpoint answers.
    expect(apiGet).not.toHaveBeenCalled()
  })

  it('composes the roadmap from content and progress while /roadmap is missing', async () => {
    apiGetOrNull.mockImplementation((path: string) => {
      if (path === '/api/v1/roadmap') return Promise.resolve(null)
      if (path.startsWith('/api/v1/courses/')) return Promise.resolve(COURSE)
      if (path === '/api/v1/progress/status') return Promise.resolve(STATUS)
      return Promise.resolve(null)
    })
    apiGet.mockImplementation((path: string) => {
      const id = path.split('/').pop() ?? ''
      const detail = MODULES[id]
      return detail ? Promise.resolve(detail) : Promise.reject(new Error('404'))
    })

    const roadmap = await getRoadmap('robotics-expert')
    const stage = roadmap?.stages?.[0]
    expect(stage?.level).toBe('기초')

    const [m1, m2] = stage?.modules ?? []
    // One of two lessons done → half-finished and in progress.
    expect(m1?.progress).toBe(0.5)
    expect(m1?.state).toBe('in_progress')
    expect(m1?.lessons?.map((lesson) => lesson.state)).toEqual(['done', 'available'])
    // Its only lesson is locked → the module is locked.
    expect(m2?.progress).toBe(0)
    expect(m2?.state).toBe('locked')
    // Stage progress is the mean of its modules.
    expect(stage?.progress).toBe(0.25)
  })

  it('returns null when neither /roadmap nor the course is available', async () => {
    apiGetOrNull.mockResolvedValue(null)
    await expect(getRoadmap()).resolves.toBeNull()
  })

  it('still composes a stage when one module fails to load', async () => {
    apiGetOrNull.mockImplementation((path: string) => {
      if (path.startsWith('/api/v1/courses/')) return Promise.resolve(COURSE)
      if (path === '/api/v1/progress/status') return Promise.resolve(STATUS)
      return Promise.resolve(null)
    })
    apiGet.mockRejectedValue(new Error('500'))

    const roadmap = await getRoadmap()
    expect(roadmap?.stages?.[0]?.modules?.length).toBe(2)
    expect(roadmap?.stages?.[0]?.modules?.[0]?.lessons).toEqual([])
    // No lessons known → treated as available rather than done.
    expect(roadmap?.stages?.[0]?.modules?.[0]?.state).toBe('available')
  })
})
