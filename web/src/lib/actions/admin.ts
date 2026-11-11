'use server'

import { revalidatePath } from 'next/cache'
import { getTranslations } from 'next-intl/server'

import { apiDelete, apiPatch } from '../api/client'
import type { Role, UserStatus } from '../api/types'
import { toActionState } from './problem'
import type { ActionState } from './result'

const USERS_PATH = '/admin/users'

const ROLES: Role[] = ['learner', 'author', 'admin']
const STATUSES: UserStatus[] = ['active', 'disabled']

function text(form: FormData, field: string): string {
  const value = form.get(field)
  return typeof value === 'string' ? value.trim() : ''
}

/**
 * `PATCH /admin/users/{id}` — change a user's role or status.
 *
 * The API enforces that only an admin may do this; a learner reaching this
 * action gets the API's 403 back as the form error (AC-WEB.4).
 */
export async function updateUser(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('admin')
  const id = text(form, 'userId')
  const role = text(form, 'role')
  const status = text(form, 'status')

  const body: { role?: Role; status?: UserStatus } = {}
  if (ROLES.includes(role as Role)) body.role = role as Role
  if (STATUSES.includes(status as UserStatus)) body.status = status as UserStatus
  if (Object.keys(body).length === 0) return { error: t('nothingToChange') }

  try {
    await apiPatch(`/api/v1/admin/users/${encodeURIComponent(id)}`, body)
  } catch (error) {
    return toActionState(error, t('updateFailed'))
  }
  revalidatePath(USERS_PATH)
  return { message: t('updated') }
}

/** `DELETE /admin/users/{id}/sessions` — sign a user out of every device. */
export async function revokeUserSessions(
  _previous: ActionState,
  form: FormData,
): Promise<ActionState> {
  const t = await getTranslations('admin')
  const id = text(form, 'userId')
  try {
    await apiDelete(`/api/v1/admin/users/${encodeURIComponent(id)}/sessions`)
  } catch (error) {
    return toActionState(error, t('revokeFailed'))
  }
  revalidatePath(USERS_PATH)
  return { message: t('revoked') }
}
