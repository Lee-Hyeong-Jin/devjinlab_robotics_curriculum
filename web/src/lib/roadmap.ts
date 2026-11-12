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
import type { Roadmap } from './api/types'
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
