import type { Metadata } from 'next'
import Link from 'next/link'
import { getLocale, getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { JsonLd } from '@/components/JsonLd'
import { PageHeader } from '@/components/PageHeader'
import { repositoryUrl } from '@/lib/repository'
import { localizedPageSeo } from '@/lib/seo-server'
import { articleSchema, breadcrumbs } from '@/lib/structured-data'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('about')
  return localizedPageSeo({
    path: '/about',
    title: t('title'),
    description: t('description'),
    publishable: true,
    type: 'article',
  })
}

/**
 * "How this course is written" (issue #61).
 *
 * Readers asked how much of the text an AI wrote. The answer was known only from commit
 * trailers and a forum thread. This page says it plainly: how a lesson is produced, what is
 * checked by a machine on every change, what no expert has checked, and how to report a
 * mistake. Being open about it costs little; a reader finding out on their own costs trust.
 */
export default async function AboutPage() {
  const [t, tApp, locale] = await Promise.all([
    getTranslations('about'),
    getTranslations('app'),
    getLocale(),
  ])
  const repository = repositoryUrl()
  const sections: Array<[id: string, title: string, paragraphs: string[]]> = [
    ['sources', t('sourcesTitle'), [t('sourcesBody')]],
    ['writing', t('writingTitle'), [t('writingBody1'), t('writingBody2')]],
    ['review', t('reviewTitle'), [t('reviewBody1'), t('reviewBody2')]],
  ]
  const checked = [t('checked1'), t('checked2'), t('checked3'), t('checked4'), t('checked5')]
  const unchecked = [t('unchecked1'), t('unchecked2'), t('unchecked3')]

  return (
    <>
      <JsonLd
        data={[
          articleSchema(t('title'), t('description'), '/about', locale),
          breadcrumbs([
            [tApp('title'), '/'],
            [t('title'), '/about'],
          ]),
        ]}
      />
      <PageHeader title={t('title')} />
      <p className="text-muted -mt-3 mb-8 max-w-3xl text-base">{t('lead')}</p>

      <div className="flex max-w-3xl flex-col gap-6">
        {sections.slice(0, 2).map(([id, title, paragraphs]) => (
          <section key={id} aria-labelledby={`about-${id}`}>
            <h2 id={`about-${id}`} className="text-primary text-lg font-bold">
              {title}
            </h2>
            {paragraphs.map((paragraph) => (
              <p key={paragraph} className="text-muted mt-2 text-sm">
                {paragraph}
              </p>
            ))}
          </section>
        ))}

        <Card as="section" aria-labelledby="about-checked">
          <h2 id="about-checked" className="text-primary font-semibold">
            {t('checkedTitle')}
          </h2>
          <p className="text-muted mt-1 text-sm">{t('checkedLead')}</p>
          <ul className="text-muted mt-3 flex list-disc flex-col gap-1.5 pl-5 text-sm">
            {checked.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Card>

        <Card as="section" aria-labelledby="about-unchecked">
          <h2 id="about-unchecked" className="text-primary font-semibold">
            {t('uncheckedTitle')}
          </h2>
          <ul className="text-muted mt-3 flex list-disc flex-col gap-1.5 pl-5 text-sm">
            {unchecked.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </Card>

        {sections.slice(2).map(([id, title, paragraphs]) => (
          <section key={id} aria-labelledby={`about-${id}`}>
            <h2 id={`about-${id}`} className="text-primary text-lg font-bold">
              {title}
            </h2>
            {paragraphs.map((paragraph) => (
              <p key={paragraph} className="text-muted mt-2 text-sm">
                {paragraph}
              </p>
            ))}
          </section>
        ))}

        <section aria-labelledby="about-report">
          <h2 id="about-report" className="text-primary text-lg font-bold">
            {t('reportTitle')}
          </h2>
          <p className="text-muted mt-2 text-sm">{t('reportBody')}</p>
          <p className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-sm">
            {repository ? (
              <>
                <a
                  href={`${repository}/issues/new?template=content_issue.yml`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent underline underline-offset-2"
                >
                  {t('reportLink')}
                </a>
                <a
                  href={`${repository}/blob/main/CONTRIBUTING.md`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent underline underline-offset-2"
                >
                  {t('contributeLink')}
                </a>
              </>
            ) : null}
            <Link href="/roadmap" className="text-accent underline underline-offset-2">
              {t('roadmapLink')}
            </Link>
          </p>
        </section>
      </div>
    </>
  )
}
