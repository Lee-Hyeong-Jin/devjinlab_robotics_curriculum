/**
 * Per-screen data loaders. Pages call these, not `apiGet`, so the route ↔ API
 * mapping of frontend.md §2 lives in one place.
 */
import 'server-only'

import { composeRoadmap, type RoadmapStageView } from '../roadmap'
import { apiGet, apiGetOrNull } from './client'
import { defaultCourseId } from './config'
import type {
  Course,
  Lesson,
  LessonProgress,
  Module,
  NextLesson,
  ResourceRef,
  Status,
} from './types'

/** `GET /api/v1/progress/status` — the dashboard payload. */
export function getStatus(): Promise<Status | null> {
  return apiGetOrNull('/api/v1/progress/status')
}

/** `GET /api/v1/progress/next` — the next-lesson recommendations (FR-3.4). */
export function getNextLessons(): Promise<NextLesson[] | null> {
  return apiGetOrNull('/api/v1/progress/next')
}

/** `GET /api/v1/courses/{course_id}` — stages and module summaries. */
export function getCourse(courseId: string = defaultCourseId()): Promise<Course | null> {
  return apiGetOrNull(
    `/api/v1/courses/${encodeURIComponent(courseId)}` as '/api/v1/courses/{course_id}',
    { cache: 'content', tags: ['content', `course:${courseId}`] },
  )
}

/** `GET /api/v1/modules/{module_id}` — a module with its lesson list. */
export function getModule(moduleId: string): Promise<Module> {
  return apiGet(
    `/api/v1/modules/${encodeURIComponent(moduleId)}` as '/api/v1/modules/{module_id}',
    { cache: 'content', tags: ['content', `module:${moduleId}`] },
  )
}

/** `GET /api/v1/lessons/{lesson_id}` — lesson body, study method, resources, activities. */
export function getLesson(lessonId: string): Promise<Lesson> {
  return apiGet(
    `/api/v1/lessons/${encodeURIComponent(lessonId)}` as '/api/v1/lessons/{lesson_id}',
    { cache: 'content', tags: ['content', `lesson:${lessonId}`] },
  )
}

/** `GET /api/v1/progress/lessons` — every lesson's progress row for the caller. */
export function getLessonProgressList(): Promise<LessonProgress[] | null> {
  return apiGetOrNull('/api/v1/progress/lessons')
}

/** `GET /api/v1/progress/lessons/{lesson_id}` — one lesson's progress row. */
export function getLessonProgress(lessonId: string): Promise<LessonProgress | null> {
  return apiGetOrNull(
    `/api/v1/progress/lessons/${encodeURIComponent(lessonId)}` as '/api/v1/progress/lessons/{lesson_id}',
  )
}

/** `GET /api/v1/resources` — the resource catalogue, optionally scoped. */
export function getResources(scope?: {
  moduleId?: string
  lessonId?: string
}): Promise<ResourceRef[] | null> {
  return apiGetOrNull('/api/v1/resources', {
    cache: 'content',
    tags: ['content', 'resources'],
    query: { module_id: scope?.moduleId, lesson_id: scope?.lessonId },
  })
}

/**
 * The roadmap, composed from the course structure and the caller's lesson states.
 *
 * Replace this with a single `GET /api/v1/roadmap` call once that endpoint is in
 * the contract — see `src/lib/roadmap.ts`.
 */
export async function getRoadmap(
  courseId: string = defaultCourseId(),
): Promise<RoadmapStageView[]> {
  const [course, status] = await Promise.all([getCourse(courseId), getStatus()])
  return composeRoadmap(course, status?.lessons ?? [], status?.stages ?? [])
}
