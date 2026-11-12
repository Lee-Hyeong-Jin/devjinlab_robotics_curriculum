import Link from 'next/link'
import { useTranslations } from 'next-intl'

import type { CourseSummary } from '@/lib/api/types'
import { cx } from '@/lib/cx'

export interface CourseTabsProps {
  courses: readonly CourseSummary[]
  /** The course currently shown. */
  selected: string
  /** Path the tabs link to; `?course=` is appended. */
  basePath: string
}

/**
 * One tab per course, for switching between tracks.
 *
 * Renders nothing for a single course: the default deployment has one, and a tab bar with a
 * single tab is noise. The selection travels in `?course=`, so a tab is a plain link — it
 * works without JavaScript and a reader can bookmark or share the track they are on.
 */
export function CourseTabs({ courses, selected, basePath }: CourseTabsProps) {
  const t = useTranslations('course')
  if (courses.length < 2) return null

  return (
    <nav aria-label={t('switcher')} className="mb-6">
      <ul className="border-border-default flex flex-wrap gap-1 border-b">
        {courses.map((course) => {
          const current = course.id === selected
          return (
            <li key={course.id}>
              <Link
                href={`${basePath}?course=${encodeURIComponent(course.id)}`}
                aria-current={current ? 'page' : undefined}
                className={cx(
                  '-mb-px inline-flex items-center gap-2 rounded-t-lg border border-b-0 px-4 py-2 text-sm font-medium',
                  current
                    ? 'bg-surface border-border-default text-primary'
                    : 'text-muted hover:bg-subtle hover:text-primary border-transparent',
                )}
              >
                {course.title}
                <span className="text-muted text-xs tabular-nums">
                  {t('lessonCount', { count: course.lesson_count })}
                </span>
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
