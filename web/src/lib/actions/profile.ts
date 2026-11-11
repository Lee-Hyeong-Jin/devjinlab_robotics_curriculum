'use server'

import { revalidatePath } from 'next/cache'
import { getTranslations } from 'next-intl/server'

import { apiDelete, apiPatch, apiPost, apiPut } from '../api/client'
import type { ApiTokenCreated, Scope } from '../api/types'
import { LOCALE_COOKIE, isLocale } from '@/i18n/locales'
import { toActionState } from './problem'
import type { ActionState } from './result'

const PROFILE_PATH = '/profile'

function text(form: FormData, field: string): string {
  const value = form.get(field)
  return typeof value === 'string' ? value.trim() : ''
}

/** `PATCH /me` — display name, UI locale and timezone. */
export async function updateProfile(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('profile')
  const locale = text(form, 'locale')
  const timezone = text(form, 'timezone')

  if (locale && !isLocale(locale)) return { fields: { locale: t('localeInvalid') } }

  try {
    await apiPatch('/api/v1/me', {
      display_name: text(form, 'displayName') || null,
      locale: locale || null,
      timezone: timezone || null,
    })
  } catch (error) {
    return toActionState(error, t('saveFailed'))
  }

  // Keep the cookie the UI reads in step with the stored preference (AC-I18N.2).
  if (isLocale(locale)) {
    const { cookies } = await import('next/headers')
    const jar = await cookies()
    jar.set(LOCALE_COOKIE, locale, { path: '/', maxAge: 31_536_000, sameSite: 'lax' })
  }
  revalidatePath(PROFILE_PATH)
  return { message: t('saved') }
}

/** `PUT /me/password` — needs the current password. */
export async function changePassword(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('profile')
  const current = String(form.get('currentPassword') ?? '')
  const next = String(form.get('newPassword') ?? '')
  const confirm = String(form.get('newPasswordConfirm') ?? '')

  const fields: Record<string, string> = {}
  if (!current) fields.currentPassword = t('currentPasswordRequired')
  if (next.length < 8) fields.newPassword = t('passwordTooShort')
  if (next !== confirm) fields.newPasswordConfirm = t('passwordMismatch')
  if (Object.keys(fields).length > 0) return { fields }

  try {
    await apiPut('/api/v1/me/password', { current_password: current, new_password: next })
  } catch (error) {
    return toActionState(error, t('passwordFailed'))
  }
  return { message: t('passwordChanged') }
}

/** `DELETE /me/sessions/{id}` — sign a single device out. */
export async function revokeSession(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('profile')
  const id = text(form, 'sessionId')
  try {
    await apiDelete(`/api/v1/me/sessions/${encodeURIComponent(id)}`)
  } catch (error) {
    return toActionState(error, t('sessionRevokeFailed'))
  }
  revalidatePath(PROFILE_PATH)
  return { message: t('sessionRevoked') }
}

/** `DELETE /me/identities/{id}` — unlink an external login. */
export async function unlinkIdentity(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('profile')
  const id = text(form, 'identityId')
  try {
    await apiDelete(`/api/v1/me/identities/${encodeURIComponent(id)}`)
  } catch (error) {
    return toActionState(error, t('identityUnlinkFailed'))
  }
  revalidatePath(PROFILE_PATH)
  return { message: t('identityUnlinked') }
}

const SCOPES: Scope[] = ['read:progress', 'write:progress', 'admin']

/**
 * `POST /me/tokens` — issue a personal access token.
 *
 * The plaintext token is returned once and never again, so it is handed back in
 * the action state for the reader to copy.
 */
export async function createToken(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('profile')
  const name = text(form, 'name')
  const scopes = SCOPES.filter((scope) => form.get(`scope:${scope}`) === 'on')
  const days = Number(text(form, 'expiresInDays'))

  const fields: Record<string, string> = {}
  if (!name) fields.name = t('tokenNameRequired')
  if (scopes.length === 0) fields.scope = t('tokenScopeRequired')
  if (Object.keys(fields).length > 0) return { fields }

  try {
    const created = await apiPost<ApiTokenCreated & { token?: string }>('/api/v1/me/tokens', {
      name,
      scopes,
      expires_in_days: Number.isFinite(days) && days > 0 ? days : null,
    })
    revalidatePath(PROFILE_PATH)
    return {
      message: created.token
        ? t('tokenCreatedWithValue', { token: created.token })
        : t('tokenCreated'),
    }
  } catch (error) {
    return toActionState(error, t('tokenFailed'))
  }
}

/** `DELETE /me/tokens/{id}` — revoke a personal access token. */
export async function revokeToken(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('profile')
  const id = text(form, 'tokenId')
  try {
    await apiDelete(`/api/v1/me/tokens/${encodeURIComponent(id)}`)
  } catch (error) {
    return toActionState(error, t('tokenRevokeFailed'))
  }
  revalidatePath(PROFILE_PATH)
  return { message: t('tokenRevoked') }
}
