/**
 * The roadmap view model.
 *
 * `GET /api/v1/roadmap` is planned but not in the contract yet (the API session
 * is building it; see `docs/architecture/frontend.md` §2). Until it answers, the
 * same shape is composed here from the course structure and the lesson states in
 * `GET /api/v1/progress/status` — both of which the P2-1 API ships. These are
 * frontend aggregates, not restatements of an API schema; when `/roadmap` lands,
 * swap `composeRoadmap` for the generated response type.
 */
import type { Course, LessonState } from './api/types'
import {
  doneCount,
  fromPercent,
  lessonLockState,
  moduleState,
  ratio,
  type LockState,
} from './progress'

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

/**
 * Group the course's modules by stage and attach each lesson's display state.
 *
 * Stage progress comes from `Status.stages` when the API reports it (it is
 * authoritative and counts every lesson, including ones this course view omits);
 * otherwise it is the share of done lessons in the stage's modules.
 */
export function composeRoadmap(
  course: Course | null,
  lessons: readonly LessonState[],
  stageStats: ReadonlyArray<{ level: string; progress: number }> = [],
): RoadmapStageView[] {
  if (!course || course.stages.length === 0) return []

  const stateByLesson = new Map<string, LockState>()
  const lessonsByModule = new Map<string, LessonState[]>()
  for (const entry of lessons) {
    const lesson = entry.lesson
    if (!lesson?.id) continue
    stateByLesson.set(lesson.id, lessonLockState(entry))
    const bucket = lessonsByModule.get(lesson.module_id) ?? []
    bucket.push(entry)
    lessonsByModule.set(lesson.module_id, bucket)
  }

  const statByLevel = new Map(stageStats.map((stat) => [stat.level, stat.progress]))

  return course.stages.map((stage) => {
    const modules: RoadmapModuleView[] = stage.modules.map((summary) => {
      const moduleLessons = lessonsByModule.get(summary.id) ?? []
      const views: RoadmapLessonView[] = moduleLessons.map((entry) => ({
        id: entry.lesson.id,
        title: entry.lesson.title,
        state: stateByLesson.get(entry.lesson.id) ?? 'available',
      }))
      const states = views.map((view) => view.state)
      return {
        id: summary.id,
        title: summary.title,
        progress: ratio(doneCount(states), states.length),
        state: moduleState(states),
        lessons: views,
      }
    })

    const stageLessons = modules.flatMap((module) => module.lessons)
    const lessonsDone = doneCount(stageLessons.map((lesson) => lesson.state))
    const reported = stage.level === null ? undefined : statByLevel.get(stage.level)

    return {
      level: stage.level ?? '',
      progress:
        reported === undefined ? ratio(lessonsDone, stageLessons.length) : fromPercent(reported),
      lessonsDone,
      lessonsTotal: stageLessons.length,
      modules,
    }
  })
}
