/**
 * The roadmap view model.
 *
 * `GET /api/v1/roadmap` returns the stage → module → lesson tree with the same
 * state vocabulary and 0–1 progress the screens use, so this only adds the
 * per-stage lesson counts the API does not carry and narrows the nullable
 * `level` to a string.
 *
 * `level` is the stable id the API groups by, the same in every language; the
 * reader is shown `levelLabel`, which the API translates (FR-9).
 */
import type { Course, Roadmap } from './api/types'
import { doneCount, normalizeState, type LockState } from './progress'

export interface RoadmapLessonView {
  id: string
  title: string
  state: LockState
}

export interface RoadmapModuleView {
  id: string
  title: string
  /** 0–1. */
  progress: number
  state: LockState
  lessons: RoadmapLessonView[]
  /**
   * How many lessons the module has. Usually `lessons.length`, but an anonymous reader is
   * served the course structure instead of the roadmap (ADR 0016) and that carries the count
   * without the per-lesson list.
   */
  lessonsTotal: number
}

export interface RoadmapStageView {
  /** Stable level id, the same in every language. Use it as a key, not as a label. */
  level: string
  /** `level` as it should be shown, in the reader's language. */
  levelLabel: string
  /** 0–1. */
  progress: number
  lessonsDone: number
  lessonsTotal: number
  modules: RoadmapModuleView[]
}

/** Adapt `GET /roadmap` into the shape the roadmap and dashboard screens render. */
export function toStageViews(roadmap: Roadmap | null): RoadmapStageView[] {
  if (!roadmap) return []
  return roadmap.stages.map((stage) => {
    const modules: RoadmapModuleView[] = stage.modules.map((module) => ({
      id: module.id,
      title: module.title,
      progress: module.progress,
      state: normalizeState(module.state),
      lessons: module.lessons.map((lesson) => ({
        id: lesson.id,
        title: lesson.title,
        state: normalizeState(lesson.state),
      })),
      lessonsTotal: module.lessons.length,
    }))
    const lessons = modules.flatMap((module) => module.lessons)
    return {
      level: stage.level ?? '',
      levelLabel: stage.level_label ?? stage.level ?? '',
      progress: stage.progress,
      lessonsDone: doneCount(lessons.map((lesson) => lesson.state)),
      lessonsTotal: lessons.length,
      modules,
    }
  })
}

/**
 * The same view model built from `GET /courses/{id}` instead of `GET /roadmap`.
 *
 * An anonymous reader may read the curriculum but not the roadmap, which carries the
 * caller's own progress (ADR 0016). The course gives the stage → module structure — which is
 * what a first-time visitor and a crawler need — so the page shows that rather than nothing.
 * Every state is `available` and every progress 0, because there is no reader to have any.
 */
export function toStageViewsFromCourse(course: Course | null): RoadmapStageView[] {
  if (!course) return []
  return (course.stages ?? []).map((stage) => {
    const modules: RoadmapModuleView[] = (stage.modules ?? []).map((module) => ({
      id: module.id,
      title: module.title,
      progress: 0,
      state: 'available' as const,
      lessons: [],
      lessonsTotal: module.lesson_count,
    }))
    return {
      level: stage.level ?? '',
      levelLabel: stage.level_label ?? stage.level ?? '',
      progress: 0,
      lessonsDone: 0,
      lessonsTotal: modules.reduce((sum, module) => sum + module.lessonsTotal, 0),
      modules,
    }
  })
}
