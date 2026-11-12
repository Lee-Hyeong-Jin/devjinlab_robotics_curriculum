import type { MetadataRoute } from 'next'

import { publicContentEnabled } from '@/lib/api/config'
import { getCourse, getCourses } from '@/lib/api/queries'
import { absoluteUrl, languageAlternates } from '@/lib/seo'

/** Static pages worth listing, most important first. */
const ROOTS = ['/roadmap', '/resources'] as const

/**
 * Built per request, not at build time: `RC_PUBLIC_CONTENT` and `RC_PUBLIC_URL` are runtime
 * settings, and the content comes from the API. Prerendered, this file would freeze whatever
 * the build environment happened to have — which is how it first shipped as `Disallow: /`
 * against a deployment that does publish.
 */
export const dynamic = 'force-dynamic'

/**
 * `sitemap.xml`: the roadmap, the resource library, and every course, module and lesson, each
 * with its `hreflang` alternates (ko, en, x-default).
 *
 * Empty while nothing is published (ADR 0016) — advertising URLs that answer with a login
 * screen would only earn crawl errors. Lesson URLs are the canonical
 * `/modules/{module}/{lesson}` form, not the `/lessons/{id}` shortcut, so a crawler is not
 * handed two addresses for one page.
 */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  if (!publicContentEnabled()) return []

  const courses = await getCourses()
  const entries: MetadataRoute.Sitemap = ROOTS.map((path) => ({
    url: absoluteUrl(path),
    changeFrequency: 'weekly' as const,
    priority: 0.8,
    alternates: { languages: languageAlternates(path) },
  }))

  for (const summary of courses) {
    const path = `/roadmap?course=${encodeURIComponent(summary.id)}`
    entries.push({
      url: absoluteUrl(path),
      changeFrequency: 'weekly',
      priority: 0.9,
      alternates: { languages: languageAlternates(path) },
    })

    const course = await getCourse(summary.id)
    for (const stage of course?.stages ?? []) {
      for (const mod of stage.modules ?? []) {
        const modulePath = `/modules/${encodeURIComponent(mod.id)}`
        entries.push({
          url: absoluteUrl(modulePath),
          changeFrequency: 'monthly',
          priority: 0.7,
          alternates: { languages: languageAlternates(modulePath) },
        })
        const full = await getModuleLessons(mod.id)
        for (const lessonId of full) {
          const lessonPath = `/modules/${encodeURIComponent(mod.id)}/${encodeURIComponent(lessonId)}`
          entries.push({
            url: absoluteUrl(lessonPath),
            changeFrequency: 'monthly',
            priority: 0.6,
            alternates: { languages: languageAlternates(lessonPath) },
          })
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
