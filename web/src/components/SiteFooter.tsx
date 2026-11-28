import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import { publicContentEnabled } from '@/lib/api/config'
import { communityUrl, repositoryUrl } from '@/lib/repository'

/**
 * Site footer: the same three links on every page.
 *
 * It gives every published page a link to the roadmap, the study guide and the resource
 * library, so none of them depends on the navigation bar's wording to be found. Rendered only
 * on a deployment that publishes its curriculum; a closed one has nothing to point visitors at.
 */
export async function SiteFooter() {
  if (!publicContentEnabled()) return null
  const t = await getTranslations('footer')
  const repository = repositoryUrl()
  const community = communityUrl()
  return (
    <footer className="border-border-default mt-12 border-t">
      <div className="mx-auto flex max-w-[var(--content-max)] flex-col gap-3 px-4 py-6 text-sm sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <p className="text-muted">{t('tagline')}</p>
        <nav aria-label={t('label')}>
          <ul className="flex flex-wrap gap-x-5 gap-y-2">
            {(
              [
                ['/roadmap', t('roadmap')],
                ['/guide', t('guide')],
                ['/resources', t('resources')],
              ] as const
            ).map(([href, label]) => (
              <li key={href}>
                <Link
                  href={href}
                  className="text-accent inline-flex min-h-11 items-center underline underline-offset-2"
                >
                  {label}
                </Link>
              </li>
            ))}
            {[
              [repository, t('source')],
              [community, t('community')],
            ]
              .filter((entry): entry is [string, string] => typeof entry[0] === 'string')
              .map(([href, label]) => (
                <li key={href}>
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-accent inline-flex min-h-11 items-center underline underline-offset-2"
                  >
                    {label}
                  </a>
                </li>
              ))}
          </ul>
        </nav>
        <p className="text-muted text-xs">{t('license')}</p>
      </div>
    </footer>
  )
}
