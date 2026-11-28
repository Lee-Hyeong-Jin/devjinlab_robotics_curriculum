import { describe, expect, it } from 'vitest'

import type { ResourceRef } from './api/types'
import {
  filterResources,
  kindCounts,
  paginate,
  readResourceFilter,
  resourcesHref,
} from './resources'

function resource(over: Partial<ResourceRef>): ResourceRef {
  return { title: 't', url: null, kind: 'book', note: null, lesson_ids: [], ...over } as ResourceRef
}

const RESOURCES = [
  resource({ title: 'Modern Robotics', url: 'https://example.com/mr', kind: 'book', note: '3장' }),
  resource({ title: 'ROS 2 Tutorials', url: 'https://example.com/ros', kind: 'course' }),
  resource({ title: 'SLAM 강의', url: 'https://example.com/slam', kind: 'video' }),
  resource({ title: 'Probabilistic Robotics', kind: 'book', note: 'Kalman filter chapters' }),
]

describe('the resource library (#57)', () => {
  it('counts kinds, most common first', () => {
    expect(kindCounts(RESOURCES)).toEqual([
      { kind: 'book', count: 2 },
      { kind: 'course', count: 1 },
      { kind: 'video', count: 1 },
    ])
  })

  it('filters by kind and by text in the title, the note or the address (AC-WEB.5)', () => {
    expect(filterResources(RESOURCES, { kind: 'video', query: '' }).map((r) => r.title)).toEqual([
      'SLAM 강의',
    ])
    expect(filterResources(RESOURCES, { kind: 'all', query: 'ROS' })).toHaveLength(1)
    expect(filterResources(RESOURCES, { kind: 'all', query: 'kalman' })[0]?.title).toBe(
      'Probabilistic Robotics',
    )
    expect(filterResources(RESOURCES, { kind: 'all', query: 'example.com/mr' })).toHaveLength(1)
    expect(filterResources(RESOURCES, { kind: 'book', query: 'ros' })).toEqual([])
    expect(filterResources(RESOURCES, { kind: 'all', query: '  ' })).toHaveLength(4)
  })

  it('reads the filter from the address and ignores what it cannot use', () => {
    const kinds = ['book', 'course', 'video']
    expect(readResourceFilter({ kind: 'video', q: ' slam ', page: '2' }, kinds)).toEqual({
      kind: 'video',
      query: 'slam',
      page: 2,
    })
    expect(readResourceFilter({ kind: 'nonsense', page: '-3' }, kinds)).toEqual({
      kind: 'all',
      query: '',
      page: 1,
    })
    expect(readResourceFilter({ kind: ['book', 'video'], page: 'abc' }, kinds).kind).toBe('book')
    expect(readResourceFilter({ q: 'x'.repeat(500) }, kinds).query).toHaveLength(100)
  })

  it('cuts the list into pages and stays inside them', () => {
    const rows = Array.from({ length: 95 }, (_unused, index) => index)
    expect(paginate(rows, 1, 40)).toMatchObject({ page: 1, pages: 3, total: 95, from: 1, to: 40 })
    expect(paginate(rows, 3, 40)).toMatchObject({ page: 3, from: 81, to: 95 })
    expect(paginate(rows, 3, 40).rows).toHaveLength(15)
    // A page past the end is the last page, not an empty one.
    expect(paginate(rows, 99, 40).page).toBe(3)
    expect(paginate([], 1, 40)).toMatchObject({ page: 1, pages: 1, total: 0, from: 0, to: 0 })
  })

  it('keeps the filter in the address and the plain address plain', () => {
    expect(resourcesHref({})).toBe('/resources')
    expect(resourcesHref({ kind: 'all', query: '', page: 1 })).toBe('/resources')
    expect(resourcesHref({ kind: 'paper', query: 'kalman filter', page: 2 })).toBe(
      '/resources?kind=paper&q=kalman+filter&page=2',
    )
  })
})
