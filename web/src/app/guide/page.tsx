import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { ButtonLink } from '@/components/Button'
import { Card } from '@/components/Card'
import { Chip } from '@/components/Chip'
import { Faq } from '@/components/Faq'
import { JsonLd } from '@/components/JsonLd'
import { PageHeader } from '@/components/PageHeader'
import { defaultCourseId } from '@/lib/api/config'
import { getCourse, getCourses } from '@/lib/api/queries'
import { courseTotals, roundHours } from '@/lib/landing'
import { localizedPageSeo } from '@/lib/seo-server'
import { guideFaq } from '@/lib/faq'
import { articleSchema, breadcrumbs, faqSchema } from '@/lib/structured-data'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('seo')
  return localizedPageSeo({
    path: '/guide',
    title: t('guideTitle'),
    description: t('guideDescription'),
    publishable: true,
    absoluteTitle: true,
    type: 'article',
  })
}

/**
 * "How to learn robotics" — the study guide (frontend.md §5.2).
 *
 * The one page written for somebody who has not chosen this site yet: what to know before
 * starting, the order to learn things in with the time each stage takes, and how a lesson is
 * meant to be used. The stages, counts and hours come from the curriculum itself, so the guide
 * cannot drift from the course it describes.
 */
export default async function GuidePage() {
  const [t, tLanding, tApp, tSeo, locale, summaries] = await Promise.all([
    getTranslations('guide'),
    getTranslations('landing'),
    getTranslations('app'),
    getTranslations('seo'),
    getLocale(),
    getCourses(),
  ])
  const courses = (await Promise.all(summaries.map((summary) => getCourse(summary.id)))).filter(
    (course) => course !== null,
  )
  const main = courses.find((course) => course.id === defaultCourseId()) ?? courses[0]
  const advanced = courses.find((course) => course.id !== main?.id)
  const mainTotals = courseTotals(main)

  const faq = guideFaq(tLanding, {
    expertLessons: mainTotals.lessons,
    expertHours: roundHours(mainTotals.minutes),
    researchLessons: courseTotals(advanced).lessons,
  })
  const steps: Array<[string, string]> = [
    [t('step1Title'), t('step1Body')],
    [t('step2Title'), t('step2Body')],
    [t('step3Title'), t('step3Body')],
    [t('step4Title'), t('step4Body')],
    [t('step5Title'), t('step5Body')],
  ]

  return (
    <>
      <JsonLd
        data={[
          articleSchema(t('title'), tSeo('guideDescription'), '/guide', locale),
          breadcrumbs([
            [tApp('title'), '/'],
            [t('breadcrumb'), '/guide'],
          ]),
          faqSchema(faq),
        ]}
      />
      <PageHeader title={t('title')} />
      <p className="text-muted -mt-3 mb-8 max-w-3xl text-base">{t('lead')}</p>

      <div className="flex flex-col gap-8">
        <section aria-labelledby="guide-before">
          <h2 id="guide-before" className="text-primary text-xl font-bold">
            {t('beforeTitle')}
          </h2>
          <p className="text-muted mt-2 max-w-3xl text-sm">{t('beforeBody')}</p>
        </section>

        {main ? (
          <section aria-labelledby="guide-path">
            <h2 id="guide-path" className="text-primary text-xl font-bold">
              {t('pathTitle')}
            </h2>
            <p className="text-muted mt-2 max-w-3xl text-sm">
              {t('pathBody', { course: main.title })}
            </p>
            <ol className="mt-4 flex flex-col gap-4">
              {(main.stages ?? []).map((stage, index) => {
                const modules = stage.modules ?? []
                const lessons = modules.reduce((sum, m) => sum + (m.lesson_count ?? 0), 0)
                const minutes = modules.reduce((sum, m) => sum + (m.estimated_minutes ?? 0), 0)
                return (
                  <li key={stage.level}>
                    <Card>
                      <h3 className="text-primary flex flex-wrap items-center gap-2 font-semibold">
                        <span className="text-muted tabular-nums">{index + 1}.</span>
                        <Chip tone="accent">{stage.level_label ?? stage.level}</Chip>
                        <span className="text-muted text-sm font-normal">
                          {t('stageSummary', {
                            modules: modules.length,
                            lessons,
                            hours: roundHours(minutes),
                          })}
                        </span>
                      </h3>
                      <ul className="mt-3 flex flex-col gap-2">
                        {modules.map((module) => (
                          <li key={module.id} className="text-sm">
                            <Link
                              href={`/modules/${encodeURIComponent(module.id)}`}
                              className="text-accent font-medium underline underline-offset-2"
                            >
                              {module.title}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </Card>
                  </li>
                )
              })}
            </ol>
          </section>
        ) : null}

        <section aria-labelledby="guide-lesson">
          <h2 id="guide-lesson" className="text-primary text-xl font-bold">
            {t('lessonTitle')}
          </h2>
          <p className="text-muted mt-2 max-w-3xl text-sm">{t('lessonBody')}</p>
          <ol className="mt-4 flex flex-col gap-3">
            {steps.map(([title, body], index) => (
              <li key={title} className="flex gap-3">
                <span
                  aria-hidden="true"
                  className="bg-accent-solid text-on-accent flex size-7 shrink-0 items-center justify-center rounded-full text-sm font-semibold"
                >
                  {index + 1}
                </span>
                <div>
                  <h3 className="text-primary font-semibold">{title}</h3>
                  <p className="text-muted max-w-3xl text-sm">{body}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        {advanced ? (
          <section aria-labelledby="guide-research">
            <h2 id="guide-research" className="text-primary text-xl font-bold">
              {t('researchTitle')}
            </h2>
            <p className="text-muted mt-2 max-w-3xl text-sm">
              {t('researchBody', { course: advanced.title })}
            </p>
            <p className="mt-2">
              <Link
                href={`/roadmap?course=${encodeURIComponent(advanced.id)}`}
                className="text-accent text-sm font-medium underline underline-offset-2"
              >
                {t('researchLink', { course: advanced.title })}
              </Link>
            </p>
          </section>
        ) : null}

        <section aria-labelledby="guide-tips">
          <h2 id="guide-tips" className="text-primary text-xl font-bold">
            {t('tipsTitle')}
          </h2>
          <ul className="text-muted mt-2 flex max-w-3xl list-disc flex-col gap-1 pl-5 text-sm">
            <li>{t('tip1')}</li>
            <li>{t('tip2')}</li>
            <li>{t('tip3')}</li>
            <li>{t('tipExamples')}</li>
            <li>{t('tipRos')}</li>
          </ul>
        </section>

        <Faq id="guide-faq" title={tLanding('faqTitle')} items={faq} />

        <Card as="section" aria-labelledby="guide-start">
          <h2 id="guide-start" className="text-primary text-lg font-bold">
            {t('startTitle')}
          </h2>
          <p className="text-muted mt-1 text-sm">{t('startBody')}</p>
          <div className="mt-3">
            <ButtonLink href="/roadmap">{t('startLink')}</ButtonLink>
          </div>
        </Card>
      </div>
    </>
  )
}
