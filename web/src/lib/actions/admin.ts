'use server'

import { revalidatePath } from 'next/cache'
import { getTranslations } from 'next-intl/server'

import { apiDelete, apiPatch, apiPost } from '../api/client'
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
  revalidatePath(userPath(id))
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
  revalidatePath(userPath(id))
  return { message: t('revoked') }
}

/** Path of one user's admin page; revalidated after an action so its lists are fresh. */
function userPath(id: string): string {
  return `${USERS_PATH}/${encodeURIComponent(id)}`
}

/** `DELETE /admin/users/{id}/tokens` — revoke every personal access token of a user. */
export async function revokeUserTokens(
  _previous: ActionState,
  form: FormData,
): Promise<ActionState> {
  const t = await getTranslations('admin')
  const id = text(form, 'userId')
  let revoked = 0
  try {
    const result = await apiDelete<{ revoked: number }>(
      `/api/v1/admin/users/${encodeURIComponent(id)}/tokens`,
    )
    revoked = result?.revoked ?? 0
  } catch (error) {
    return toActionState(error, t('revokeTokensFailed'))
  }
  revalidatePath(userPath(id))
  return { message: t('tokensRevoked', { count: revoked }) }
}

/**
 * `POST /admin/users/{id}/password-reset` — mail the user a reset link.
 *
 * The link goes to the user's inbox only. The API answers 503 when the server has no mail
 * configuration and 409 for an account that is not active; both arrive here as the form error.
 */
export async function sendPasswordReset(
  _previous: ActionState,
  form: FormData,
): Promise<ActionState> {
  const t = await getTranslations('admin')
  const id = text(form, 'userId')
  try {
    await apiPost(`/api/v1/admin/users/${encodeURIComponent(id)}/password-reset`)
  } catch (error) {
    return toActionState(error, t('sendResetFailed'))
  }
  revalidatePath(userPath(id))
  return { message: t('resetSent') }
}
