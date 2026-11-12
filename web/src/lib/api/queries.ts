/**
 * Per-screen data loaders. Pages call these, not `apiGet`, so the route ↔ API
 * mapping of frontend.md §2 lives in one place.
 */
import 'server-only'

import { toStageViews, type RoadmapStageView } from '../roadmap'
import { apiGet, apiGetOrNull } from './client'
import { defaultCourseId } from './config'
import type {
  AuthProvider,
  Course,
  Lesson,
  LessonProgress,
  Module,
  NextLesson,
  QuizPublic,
  Report,
  ResourceRef,
  ReviewCard,
  SearchHit,
  Status,
} from './types'

/**
 * `GET /api/v1/auth/providers` — the configured external logins.
 *
 * Unauthenticated, and `null`/`[]` when the deployment has none, which the
 * sign-in screens read as "show no provider buttons".
 */
export async function getAuthProviders(): Promise<AuthProvider[]> {
  return (await apiGetOrNull('/api/v1/auth/providers', { redirectOnUnauthorized: false })) ?? []
}

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

/** `GET /api/v1/roadmap` — stage → module → lesson witheach lesson's state. */
export async function getRoadmap(
  courseId: string = defaultCourseId(),
): Promise<RoadmapStageView[]> {
  return toStageViews(await apiGetOrNull('/api/v1/roadmap', { query: { course: courseId } }))
}

/** `GET /api/v1/search` — lessons and resources matching `q` (min. 2 characters). */
export function search(query: string, limit = 50): Promise<SearchHit[] | null> {
  if (query.trim().length < 2) return Promise.resolve([])
  return apiGetOrNull('/api/v1/search', { query: { q: query.trim(), limit } })
}

/** `GET /api/v1/lessons/{id}/quiz` — the lesson's questions, without answers. */
export function getQuiz(lessonId: string): Promise<QuizPublic | null> {
  return apiGetOrNull(
    `/api/v1/lessons/${encodeURIComponent(lessonId)}/quiz` as '/api/v1/lessons/{lesson_id}/quiz',
  )
}

/** `GET /api/v1/review/due` — the flashcards due today. */
export function getDueCards(): Promise<ReviewCard[] | null> {
  return apiGetOrNull('/api/v1/review/due')
}

/** `GET /api/v1/reports/weekly` — the weekly report, as Markdown plus a summary. */
export function getWeeklyReport(): Promise<Report | null> {
  return apiGetOrNull('/api/v1/reports/weekly')
}

/** `GET /api/v1/reports/modules/{module_id}` — one module's report (`rc report module`). */
export function getModuleReport(moduleId: string): Promise<Report> {
  return apiGet(
    `/api/v1/reports/modules/${encodeURIComponent(moduleId)}` as '/api/v1/reports/modules/{module_id}',
  )
}
