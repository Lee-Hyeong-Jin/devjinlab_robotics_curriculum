'use server'

import { revalidatePath } from 'next/cache'
import { getTranslations } from 'next-intl/server'

import { apiPost } from '../api/client'
import type { DoneResult } from '../api/types'
import { toActionState } from './problem'
import type { ActionState } from './result'

function text(form: FormData, field: string): string {
  const value = form.get(field)
  return typeof value === 'string' ? value.trim() : ''
}

/** Refresh the lesson screen and everything that counts its progress. */
function revalidateLesson(moduleId: string, lessonId: string): void {
  revalidatePath(`/modules/${moduleId}/${lessonId}`)
  revalidatePath(`/modules/${moduleId}`)
  revalidatePath('/roadmap')
  revalidatePath('/')
}

/**
 * `POST /progress/start` — begin the study timer.
 *
 * A 409 means another lesson's timer is still running; the API's detail says
 * which, so it is shown as-is (frontend.md §2 "레슨 화면의 쓰기 동작").
 */
export async function startTimer(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('study')
  const lessonId = text(form, 'lessonId')
  const moduleId = text(form, 'moduleId')
  try {
    await apiPost('/api/v1/progress/start', { lesson_id: lessonId })
  } catch (error) {
    return toActionState(error, t('startFailed'))
  }
  revalidateLesson(moduleId, lessonId)
  return { message: t('started') }
}

/** `POST /progress/stop` — end the running timer and keep the time. */
export async function stopTimer(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('study')
  const lessonId = text(form, 'lessonId')
  const moduleId = text(form, 'moduleId')
  try {
    await apiPost('/api/v1/progress/stop', { note: text(form, 'note') || null, discard: false })
  } catch (error) {
    return toActionState(error, t('stopFailed'))
  }
  revalidateLesson(moduleId, lessonId)
  return { message: t('stopped') }
}

/** `POST /progress/log` — record minutes without having run the timer. */
export async function logMinutes(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('study')
  const lessonId = text(form, 'lessonId')
  const moduleId = text(form, 'moduleId')
  const minutes = Number(text(form, 'minutes'))

  if (!Number.isInteger(minutes) || minutes < 1 || minutes > 1440) {
    return { fields: { minutes: t('minutesInvalid') } }
  }

  try {
    await apiPost('/api/v1/progress/log', {
      lesson_id: lessonId,
      minutes,
      note: text(form, 'note') || null,
    })
  } catch (error) {
    return toActionState(error, t('logFailed'))
  }
  revalidateLesson(moduleId, lessonId)
  return { message: t('logged', { minutes }) }
}

/**
 * `POST /progress/done` — mark the lesson complete with a self-rated
 * understanding and an optional note. The reply says which lessons that
 * unlocked, which is reported back to the reader.
 */
export async function markDone(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('study')
  const lessonId = text(form, 'lessonId')
  const moduleId = text(form, 'moduleId')
  const understanding = Number(text(form, 'understanding'))

  if (!Number.isInteger(understanding) || understanding < 1 || understanding > 5) {
    return { fields: { understanding: t('understandingInvalid') } }
  }

  let result: DoneResult
  try {
    result = await apiPost<DoneResult>('/api/v1/progress/done', {
      lesson_id: lessonId,
      understanding,
      note: text(form, 'note') || null,
    })
  } catch (error) {
    return toActionState(error, t('doneFailed'))
  }
  revalidateLesson(moduleId, lessonId)

  const unlocked = result.unlocked_lesson_ids
  return {
    message:
      unlocked.length > 0
        ? t('doneWithUnlocked', { count: unlocked.length, ids: unlocked.join(', ') })
        : t('done'),
  }
}
