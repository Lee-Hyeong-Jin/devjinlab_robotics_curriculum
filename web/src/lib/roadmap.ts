/**
 * The roadmap view model.
 *
 * `GET /api/v1/roadmap` returns the stage → module → lesson tree with the same
 * state vocabulary and 0–1 progress the screens use, so this only adds the
 * per-stage lesson counts the API does not carry and narrows the nullable
 * `level` to a string.
 */
import type { Roadmap } from './api/types'
import { doneCount, type LockState } from './progress'

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
}

export interface RoadmapStageView {
  level: string
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
      state: module.state,
      lessons: module.lessons.map((lesson) => ({
        id: lesson.id,
        title: lesson.title,
        state: lesson.state,
      })),
    }))
    const lessons = modules.flatMap((module) => module.lessons)
    return {
      level: stage.level ?? '',
      progress: stage.progress,
      lessonsDone: doneCount(lessons.map((lesson) => lesson.state)),
      lessonsTotal: lessons.length,
      modules,
    }
  })
}
