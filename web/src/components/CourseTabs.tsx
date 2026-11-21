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
      {/* One row that scrolls sideways on a phone instead of wrapping into a second row of tabs.
          The baseline is an inset shadow, not a border: a scroll container clips anything that
          overlaps its border, and the current tab has to cover the line. */}
      <ul className="flex gap-1 overflow-x-auto shadow-[inset_0_-1px_0_var(--border-default)]">
        {courses.map((course) => {
          const current = course.id === selected
          return (
            <li key={course.id} className="shrink-0">
              <Link
                href={`${basePath}?course=${encodeURIComponent(course.id)}`}
                aria-current={current ? 'page' : undefined}
                className={cx(
                  'inline-flex min-h-11 items-center gap-2 rounded-t-lg border border-b-0 px-3 py-2 text-sm font-medium whitespace-nowrap sm:px-4',
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
