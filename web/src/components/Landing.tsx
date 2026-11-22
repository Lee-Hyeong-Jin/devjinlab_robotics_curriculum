import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { getCourse, getCourses } from '@/lib/api/queries'
import { defaultCourseId } from '@/lib/api/config'
import { formatMinutes } from '@/lib/format'
import { courseTotals, roundHours } from '@/lib/landing'
import { metaDescription, plainText } from '@/lib/seo'
import {
  courseListSchema,
  courseSchema,
  faqSchema,
  organizationSchema,
  webSiteSchema,
} from '@/lib/structured-data'

import { ButtonLink } from './Button'
import { Card } from './Card'
import { Chip } from './Chip'
import { Faq } from './Faq'
import { JsonLd } from './JsonLd'

/** Where a course's roadmap lives; the default course owns the bare `/roadmap` (ADR 0016). */
function roadmapPath(courseId: string): string {
  return courseId === defaultCourseId()
    ? '/roadmap'
    : `/roadmap?course=${encodeURIComponent(courseId)}`
}

/**
 * The home page for a visitor without a session on a deployment that publishes its curriculum
 * (frontend.md §5.2).
 *
 * `/` used to be the dashboard for everybody, which for a first-time visitor and for a crawler
 * is a row of zeroes marked `noindex` — the site's own front door said nothing about the site.
 * This page says what the curriculum is and links every course and module, so the root URL is
 * worth indexing and every published page is reachable from it in two steps.
 */
export async function Landing() {
  const [t, tCourse, locale, summaries] = await Promise.all([
    getTranslations('landing'),
    getTranslations('course'),
    getLocale(),
    getCourses(),
  ])
  const tApp = await getTranslations('app')
  const courses = (await Promise.all(summaries.map((summary) => getCourse(summary.id)))).filter(
    (course) => course !== null,
  )
  const moduleCount = courses.reduce((sum, course) => sum + (course.module_count ?? 0), 0)
  const lessonCount = courses.reduce((sum, course) => sum + (course.lesson_count ?? 0), 0)
  // The course a newcomer starts with, and the one that follows it.
  const main = courses.find((course) => course.id === defaultCourseId()) ?? courses[0]
  const advanced = courses.find((course) => course.id !== main?.id)
  const mainTotals = courseTotals(main)
  const faq: Array<[string, string]> = [
    [t('faq1Q'), t('faq1A')],
    [t('faq2Q'), t('faq2A')],
    [t('faq3Q'), t('faq3A')],
    [
      t('faq4Q'),
      t('faq4A', {
        expertLessons: mainTotals.lessons,
        expertHours: roundHours(mainTotals.minutes),
        researchLessons: courseTotals(advanced).lessons,
      }),
    ],
    [t('faq5Q'), t('faq5A')],
    [t('faq6Q'), t('faq6A')],
  ]
  const how: Array<[string, string]> = [
    [t('how1Title'), t('how1Body')],
    [t('how2Title'), t('how2Body')],
    [t('how3Title'), t('how3Body')],
    [t('how4Title'), t('how4Body')],
  ]

  return (
    <>
      <JsonLd
        data={[
          webSiteSchema(tApp('title'), tApp('description'), locale),
          organizationSchema(tApp('title')),
          courseListSchema(courses.map((course) => [course.title, roadmapPath(course.id)])),
          ...courses.map((course) => courseSchema(course, roadmapPath(course.id))),
          faqSchema(faq),
        ]}
      />

      <section aria-labelledby="landing-title" className="mb-10 sm:mb-14">
        <h1
          id="landing-title"
          className="text-primary max-w-3xl text-3xl font-bold tracking-tight sm:text-4xl"
        >
          {t('h1')}
        </h1>
        <p className="text-muted mt-3 max-w-2xl text-base sm:text-lg">{t('lead')}</p>
        <p className="text-muted mt-2 max-w-2xl text-sm">{t('free')}</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <ButtonLink href="/roadmap">{t('viewRoadmap')}</ButtonLink>
          <ButtonLink href="/signup" kind="secondary">
            {t('signUp')}
          </ButtonLink>
          <ButtonLink href="/guide" kind="secondary">
            {t('readGuide')}
          </ButtonLink>
        </div>
        <dl className="mt-8 grid max-w-xl grid-cols-3 gap-4">
          {[
            [t('statCourses'), courses.length],
            [t('statModules'), moduleCount],
            [t('statLessons'), lessonCount],
          ].map(([label, value]) => (
            <div key={String(label)}>
              <dt className="text-muted text-xs font-medium">{label}</dt>
              <dd className="text-primary text-2xl font-bold tabular-nums">{value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <div className="flex flex-col gap-8">
        {main ? (
          <section aria-labelledby="landing-what">
            <h2 id="landing-what" className="text-primary text-xl font-bold">
              {t('whatTitle')}
            </h2>
            <p className="text-muted mt-2 max-w-3xl text-sm">{t('whatBody')}</p>
            <ol className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
              {(main.stages ?? [])
                .flatMap((stage) => stage.modules ?? [])
                .map((module) => (
                  <li key={module.id}>
                    <Link
                      href={`/modules/${encodeURIComponent(module.id)}`}
                      className="bg-surface border-border-default hover:border-border-accent flex h-full flex-col gap-1 rounded-[var(--radius-card)] border p-4"
                    >
                      <span className="text-primary font-semibold">{module.title}</span>
                      <span className="text-muted text-sm">
                        {metaDescription(module.summary, 140)}
                      </span>
                    </Link>
                  </li>
                ))}
            </ol>
          </section>
        ) : null}

        <section aria-labelledby="landing-how">
          <h2 id="landing-how" className="text-primary text-xl font-bold">
            {t('howTitle')}
          </h2>
          <ul className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {how.map(([title, body]) => (
              <li
                key={title}
                className="bg-surface border-border-default rounded-[var(--radius-card)] border p-4"
              >
                <h3 className="text-primary font-semibold">{title}</h3>
                <p className="text-muted mt-1 text-sm">{body}</p>
              </li>
            ))}
          </ul>
        </section>

        {courses.map((course) => (
          <Card as="section" key={course.id} aria-labelledby={`course-${course.id}`}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <h2 id={`course-${course.id}`} className="text-primary text-xl font-bold">
                <Link href={roadmapPath(course.id)} className="hover:text-accent">
                  {course.title}
                </Link>
              </h2>
              <span className="text-muted text-sm">
                {tCourse('lessonCount', { count: course.lesson_count ?? 0 })}
              </span>
            </div>
            <p className="text-muted mt-2 max-w-3xl text-sm">{plainText(course.summary)}</p>

            {(course.stages ?? []).map((stage) => (
              <div key={stage.level} className="mt-5">
                <h3 className="text-primary mb-2 flex items-center gap-2 text-sm font-semibold">
                  <Chip tone="neutral">{stage.level_label ?? stage.level}</Chip>
                  <span className="text-muted font-normal">
                    {t('moduleCount', { count: (stage.modules ?? []).length })}
                  </span>
                </h3>
                <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-3">
                  {(stage.modules ?? []).map((module) => (
                    <li key={module.id}>
                      <Link
                        href={`/modules/${encodeURIComponent(module.id)}`}
                        className="border-border-default hover:border-border-accent flex min-h-11 flex-col justify-center rounded-lg border px-3 py-2"
                      >
                        <span className="text-primary text-sm font-medium">{module.title}</span>
                        <span className="text-muted text-xs">
                          {tCourse('lessonCount', { count: module.lesson_count ?? 0 })}
                          {module.estimated_minutes
                            ? ` · ${formatMinutes(module.estimated_minutes, locale)}`
                            : ''}
                        </span>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}

            <p className="mt-5">
              <Link
                href={roadmapPath(course.id)}
                className="text-accent text-sm font-medium underline underline-offset-2"
              >
                {t('openRoadmap', { course: course.title })}
              </Link>
            </p>
          </Card>
        ))}

        <Faq id="landing-faq" title={t('faqTitle')} items={faq} />

        <Card as="section" aria-labelledby="landing-resources">
          <h2 id="landing-resources" className="text-primary text-lg font-bold">
            {t('resourcesTitle')}
          </h2>
          <p className="text-muted mt-1 max-w-3xl text-sm">{t('resourcesBody')}</p>
          <p className="mt-3">
            <Link
              href="/resources"
              className="text-accent text-sm font-medium underline underline-offset-2"
            >
              {t('openResources')}
            </Link>
          </p>
        </Card>
      </div>
    </>
  )
}
