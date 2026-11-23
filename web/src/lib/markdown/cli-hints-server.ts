import 'server-only'

import { getTranslations } from 'next-intl/server'

import { linkCliHints } from './cli-hints'

/**
 * `linkCliHints` with this app's routes and the reader's language.
 *
 * @param quizzes lesson id -> the address of its quiz, for the lessons whose module is known.
 *   A quiz address needs the module; a lesson address does not (`/lessons/{id}` redirects).
 */
export async function webCliHints(
  markdown: string | null | undefined,
  quizzes: Record<string, string> = {},
): Promise<string | undefined> {
  if (!markdown) return undefined
  const t = await getTranslations('cliHint')
  return linkCliHints(markdown, {
    labels: { quiz: t('quiz'), start: t('start'), review: t('review'), cli: t('cli') },
    quizHref: (lessonId) => quizzes[lessonId] ?? null,
    lessonHref: (lessonId) => `/lessons/${encodeURIComponent(lessonId)}`,
  })
}
