/**
 * Fixture builders for the generated API types.
 *
 * The contract is generated from the FastAPI implementation, so most fields are
 * required. These helpers fill them in so a test can state only what it is about.
 */
import type {
  Course,
  LessonState,
  LessonSummary,
  ModuleSummary,
  ResourceRef,
} from '@/lib/api/types'

export function lessonSummary(over: Partial<LessonSummary> & { id: string }): LessonSummary {
  return {
    title: over.id,
    summary: '',
    course_id: 'robotics-expert',
    module_id: 'm1',
    difficulty: 3,
    estimated_minutes: 40,
    prerequisites: [],
    tags: [],
    lang: 'ko',
    ...over,
  }
}

export function moduleSummary(over: Partial<ModuleSummary> & { id: string }): ModuleSummary {
  return {
    title: over.id,
    summary: '',
    level: '기초',
    level_label: 'Foundation',
    course_id: 'robotics-expert',
    lesson_count: 0,
    estimated_minutes: 0,
    lang: 'ko',
    ...over,
  }
}

export function lessonState(over: Partial<LessonState> & { lesson: LessonSummary }): LessonState {
  return {
    status: 'not_started',
    // The API still sends this, always false (ADR 0015). Screens read
    // `missing_prerequisites` instead.
    locked: false,
    total_seconds: 0,
    started_at: null,
    completed_at: null,
    understanding: null,
    note: null,
    ...over,
  }
}

export function course(over: Partial<Course> = {}): Course {
  return {
    id: 'robotics-expert',
    title: '로보틱스 전문가 코스',
    summary: '',
    tags: [],
    lang: 'ko',
    module_count: 0,
    lesson_count: 0,
    stages: [],
    ...over,
  }
}

export function resource(over: Partial<ResourceRef> & { title: string }): ResourceRef {
  return { lesson_ids: [], ...over }
}
