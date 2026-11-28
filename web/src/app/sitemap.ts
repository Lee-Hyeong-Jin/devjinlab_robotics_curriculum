import type { MetadataRoute } from 'next'

import { defaultCourseId, publicContentEnabled } from '@/lib/api/config'
import { getCourse, getCourses } from '@/lib/api/queries'
import { LOCALES } from '@/i18n/locales'
import { languageAlternates } from '@/lib/seo'

/** Static pages worth listing, most important first. */
const ROOTS = ['/', '/roadmap', '/guide', '/about', '/resources'] as const

/**
 * Built per request, not at build time: `RC_PUBLIC_CONTENT` and `RC_PUBLIC_URL` are runtime
 * settings, and the content comes from the API. Prerendered, this file would freeze whatever
 * the build environment happened to have — which is how it first shipped as `Disallow: /`
 * against a deployment that does publish.
 */
export const dynamic = 'force-dynamic'

/**
 * `sitemap.xml`: the home page, the roadmap, the resource library, and every course, module and lesson, each
 * in every language version, each with its `hreflang` alternates (ko, en, x-default).
 *
 * Empty while nothing is published (ADR 0016) — advertising URLs that answer with a login
 * screen would only earn crawl errors. Lesson URLs are the canonical
 * `/modules/{module}/{lesson}` form, not the `/lessons/{id}` shortcut, so a crawler is not
 * handed two addresses for one page.
 */
type Entry = MetadataRoute.Sitemap[number]

/**
 * One `<url>` per language version of a page, each carrying the full set of alternates.
 *
 * Listing only the Korean address and naming English as an alternate leaves the English page
 * to be discovered second-hand. Search engines ask for every language version to be listed
 * in its own right, with the same `hreflang` set on each.
 */
function versions(
  path: string,
  changeFrequency: Entry['changeFrequency'],
  priority: number,
): MetadataRoute.Sitemap {
  const languages = languageAlternates(path)
  const urls = [...new Set(LOCALES.map((locale) => languages[locale]))].filter(
    (url): url is string => typeof url === 'string',
  )
  return urls.map((url) => ({ url, changeFrequency, priority, alternates: { languages } }))
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  if (!publicContentEnabled()) return []

  const courses = await getCourses()
  const entries: MetadataRoute.Sitemap = ROOTS.flatMap((path) =>
    versions(path, 'weekly', path === '/' ? 1 : 0.9),
  )

  for (const summary of courses) {
    // The default course is the bare `/roadmap`, already listed above. `/roadmap?course=<it>`
    // names that page as its canonical, so listing it would hand the crawler a duplicate.
    if (summary.id !== defaultCourseId()) {
      entries.push(...versions(`/roadmap?course=${encodeURIComponent(summary.id)}`, 'weekly', 0.9))
    }

    const course = await getCourse(summary.id)
    for (const stage of course?.stages ?? []) {
      for (const mod of stage.modules ?? []) {
        const modulePath = `/modules/${encodeURIComponent(mod.id)}`
        entries.push(...versions(modulePath, 'monthly', 0.7))
        for (const lessonId of await getModuleLessons(mod.id)) {
          entries.push(...versions(`${modulePath}/${encodeURIComponent(lessonId)}`, 'monthly', 0.6))
        }
      }
    }
  }
  return entries
}

/** Lesson ids of a module, or `[]` when it cannot be read. */
async function getModuleLessons(moduleId: string): Promise<string[]> {
  const { getModuleOrNull } = await import('@/lib/api/queries')
  const found = await getModuleOrNull(moduleId)
  return (found?.lessons ?? []).map((lesson) => lesson.id).filter((id): id is string => !!id)
}
