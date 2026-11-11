import { notFound, redirect } from 'next/navigation'

import { isNotFound } from '@/lib/api/errors'
import { getLesson } from '@/lib/api/queries'

interface Params {
  params: Promise<{ lessonId: string }>
}

/**
 * Canonical lesson link.
 *
 * Search hits and prerequisite ids name a lesson without its module, so this
 * resolves the module from the API and redirects to the real lesson URL.
 */
export default async function LessonRedirect({ params }: Params) {
  const { lessonId } = await params
  try {
    const lesson = await getLesson(lessonId)
    redirect(`/modules/${lesson.module_id}/${lesson.id}`)
  } catch (error) {
    if (isNotFound(error)) notFound()
    throw error
  }
}
