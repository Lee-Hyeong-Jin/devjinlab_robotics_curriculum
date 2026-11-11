/**
 * Per-screen data loaders. Pages call these, not `apiGet`, so the route ↔ API
 * mapping of frontend.md §2 lives in one place.
 */
import 'server-only'

import { average, doneCount, moduleState, ratio } from '../progress'
import { apiGet, apiGetOrNull } from './client'
import { defaultCourseId } from './config'
import type {
  Course,
  Lesson,
  LessonProgress,
  LessonState,
  LockState,
  Module,
  ResourceRef,
  Roadmap,
  RoadmapModule,
  Status,
} from './types'

/** `GET /api/v1/progress/status` — the dashboard payload. */
export function getStatus(): Promise<Status | null> {
  return apiGetOrNull('/api/v1/progress/status')
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
    {
      cache: 'content',
      tags: ['content', `module:${moduleId}`],
    },
  )
}

/** `GET /api/v1/lessons/{lesson_id}` — lesson body, study method, resources, activities. */
export function getLesson(lessonId: string): Promise<Lesson> {
  return apiGet(
    `/api/v1/lessons/${encodeURIComponent(lessonId)}` as '/api/v1/lessons/{lesson_id}',
    {
      cache: 'content',
      tags: ['content', `lesson:${lessonId}`],
    },
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

/* ------------------------------------------------------------------------- *
 * Roadmap
 * ------------------------------------------------------------------------- */

/**
 * `GET /api/v1/roadmap`, with a fallback.
 *
 * The contract path is the real source, but P2-1 ships only the content and
 * progress routers, so until `api-developer` lands `/roadmap` we compose the
 * same shape from `/courses/{id}`, each module's lesson list, and the lesson
 * states in `/progress/status`. Remove the fallback once `/roadmap` answers.
 */
export async function getRoadmap(courseId: string = defaultCourseId()): Promise<Roadmap | null> {
  const direct = await apiGetOrNull('/api/v1/roadmap', {
    cache: 'content',
    tags: ['content', 'roadmap'],
  })
  if (direct?.stages && direct.stages.length > 0) return direct
  return composeRoadmap(courseId)
}

async function composeRoadmap(courseId: string): Promise<Roadmap | null> {
  const [course, status] = await Promise.all([getCourse(courseId), getStatus()])
  if (!course?.stages) return null

  const stateByLesson = lessonStateIndex(status?.lessons ?? [])
  const moduleIds = course.stages.flatMap((stage) =>
    (stage.modules ?? []).map((module) => module.id).filter((id): id is string => !!id),
  )
  const modules = await Promise.all(
    moduleIds.map((id) => getModule(id).catch((): Module | null => null)),
  )
  const moduleById = new Map<string, Module>()
  for (const detail of modules) {
    if (detail?.id) moduleById.set(detail.id, detail)
  }

  const stages = course.stages.map((stage) => {
    const roadmapModules: RoadmapModule[] = (stage.modules ?? []).map((summary) => {
      const detail = summary.id ? moduleById.get(summary.id) : undefined
      const lessons = (detail?.lessons ?? []).map((lesson) => ({
        id: lesson.id,
        title: lesson.title,
        state: lesson.id ? (stateByLesson.get(lesson.id) ?? 'available') : 'available',
      }))
      const states = lessons.map((lesson) => lesson.state as LockState)
      return {
        id: summary.id,
        title: summary.title,
        progress: ratio(doneCount(states), states.length),
        state: moduleState(states),
        lessons,
      }
    })
    return {
      level: stage.level,
      progress: average(roadmapModules.map((module) => module.progress ?? 0)),
      modules: roadmapModules,
    }
  })

  return { stages }
}

function lessonStateIndex(states: LessonState[]): Map<string, LockState> {
  const index = new Map<string, LockState>()
  for (const entry of states) {
    if (entry.lesson_id && entry.state) index.set(entry.lesson_id, entry.state)
  }
  return index
}
