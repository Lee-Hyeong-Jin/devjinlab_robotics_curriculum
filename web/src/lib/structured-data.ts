import type { Course, Lesson, Module } from './api/types'
import { absoluteUrl, metaDescription } from './seo'

/** The organisation/author every item is attributed to. */
const PROVIDER = { '@type': 'Organization', name: 'Robotics Expert Course' } as const

/** schema.org `BreadcrumbList` from `[name, path]` pairs, in order. */
export function breadcrumbs(trail: ReadonlyArray<[string, string]>): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: trail.map(([name, path], index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name,
      item: absoluteUrl(path),
    })),
  }
}

/**
 * schema.org `Course` for a track.
 *
 * `hasCourseInstance` is deliberately absent: the course is self-paced with no scheduled
 * run, and inventing a date would be a false claim about the content.
 */
export function courseSchema(course: Course, path: string): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'Course',
    name: course.title,
    description: metaDescription(course.summary),
    url: absoluteUrl(path),
    inLanguage: course.lang,
    provider: PROVIDER,
    numberOfCredits: undefined,
    courseMode: 'online',
    isAccessibleForFree: true,
    teaches: (course.stages ?? []).flatMap((stage) =>
      (stage.modules ?? []).map((module) => module.title),
    ),
  }
}

/** schema.org `LearningResource` for a module: a syllabus section of its course. */
export function moduleSchema(module: Module, path: string): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'LearningResource',
    name: module.title,
    description: metaDescription(module.summary),
    url: absoluteUrl(path),
    inLanguage: module.lang,
    learningResourceType: 'Syllabus section',
    educationalLevel: module.level_label ?? module.level ?? undefined,
    timeRequired: isoDuration(module.estimated_minutes),
    provider: PROVIDER,
    isAccessibleForFree: true,
    isPartOf: { '@type': 'Course', name: module.course_id },
  }
}

/** schema.org `LearningResource` for one lesson. */
export function lessonSchema(
  lesson: Lesson,
  path: string,
  moduleTitle: string | null,
): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'LearningResource',
    name: lesson.title,
    description: metaDescription(lesson.summary),
    url: absoluteUrl(path),
    inLanguage: lesson.lang,
    learningResourceType: 'Lesson',
    timeRequired: isoDuration(lesson.estimated_minutes),
    teaches: lesson.objectives,
    keywords: lesson.tags.length > 0 ? lesson.tags.join(', ') : undefined,
    provider: PROVIDER,
    isAccessibleForFree: true,
    ...(moduleTitle ? { isPartOf: { '@type': 'LearningResource', name: moduleTitle } } : {}),
  }
}

/** Minutes as an ISO 8601 duration (`90` → `PT1H30M`), or undefined when there is none. */
export function isoDuration(minutes: number | null | undefined): string | undefined {
  if (!minutes || minutes <= 0) return undefined
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  return `PT${hours > 0 ? `${hours}H` : ''}${rest > 0 || hours === 0 ? `${rest}M` : ''}`
}
