'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { getTranslations } from 'next-intl/server'

import { apiPost, apiPostRaw } from '../api/client'
import type { User } from '../api/types'
import { safeNext } from '../next-path'
import { toActionState } from './problem'
import type { ActionState } from './result'

/**
 * Replay the API's `Set-Cookie` onto the browser.
 *
 * The API owns the session cookie's flags (HttpOnly, Secure, SameSite, Max-Age);
 * this only forwards what it sent, so the frontend never invents a session.
 */
async function forwardCookies(setCookie: string[]): Promise<void> {
  if (setCookie.length === 0) return
  const jar = await cookies()
  for (const header of setCookie) {
    const [pair, ...attributes] = header.split(';')
    const index = pair?.indexOf('=') ?? -1
    if (!pair || index < 1) continue
    const name = pair.slice(0, index).trim()
    const value = pair.slice(index + 1).trim()
    const options: Parameters<typeof jar.set>[2] = { path: '/' }
    for (const attribute of attributes) {
      const [rawKey, rawValue = ''] = attribute.split('=')
      const key = rawKey?.trim().toLowerCase()
      const attributeValue = rawValue.trim()
      if (key === 'path') options.path = attributeValue || '/'
      else if (key === 'max-age') options.maxAge = Number(attributeValue)
      else if (key === 'expires') options.expires = new Date(attributeValue)
      else if (key === 'domain') options.domain = attributeValue
      else if (key === 'httponly') options.httpOnly = true
      else if (key === 'secure') options.secure = true
      else if (key === 'samesite') {
        const lowered = attributeValue.toLowerCase()
        if (lowered === 'lax' || lowered === 'strict' || lowered === 'none') {
          options.sameSite = lowered
        }
      }
    }
    jar.set(name, value, options)
  }
}

function text(form: FormData, field: string): string {
  const value = form.get(field)
  return typeof value === 'string' ? value.trim() : ''
}

/** `POST /auth/login`, then on to the page the reader came from. */
export async function login(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('login')
  const email = text(form, 'email')
  const password = String(form.get('password') ?? '')
  const next = safeNext(text(form, 'next'))

  const fields: Record<string, string> = {}
  if (!email) fields.email = t('emailRequired')
  if (!password) fields.password = t('passwordRequired')
  if (Object.keys(fields).length > 0) return { fields }

  try {
    const result = await apiPostRaw<unknown>(
      '/api/v1/auth/login',
      { email, password, remember: form.get('remember') === 'on' },
      { redirectOnUnauthorized: false },
    )
    await forwardCookies(result.setCookie)
  } catch (error) {
    return toActionState(error, t('failed'))
  }
  redirect(next)
}

/** `POST /auth/signup` — the API sends the verification mail. */
export async function signup(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('signup')
  const email = text(form, 'email')
  const password = String(form.get('password') ?? '')
  const confirm = String(form.get('passwordConfirm') ?? '')
  const displayName = text(form, 'displayName')

  const fields: Record<string, string> = {}
  if (!email) fields.email = t('emailRequired')
  if (password.length < 8) fields.password = t('passwordTooShort')
  if (password !== confirm) fields.passwordConfirm = t('passwordMismatch')
  if (Object.keys(fields).length > 0) return { fields }

  let created: User
  try {
    created = await apiPost<User>(
      '/api/v1/auth/signup',
      { email, password, display_name: displayName || null },
      { redirectOnUnauthorized: false },
    )
  } catch (error) {
    return toActionState(error, t('failed'))
  }
  // A server with no SMTP configuration can never deliver the link, so telling the
  // reader to check their inbox would send them nowhere (`email_verification`).
  const verify = created.email_verification === 'pending'
  redirect(`/login?registered=${verify ? 'verify' : 'ready'}`)
}

/**
 * `POST /auth/resend-verification` — mail the link again to the signed-in account.
 *
 * Only offered while `email_verification` is `pending`; the API answers 503 when the
 * server cannot send mail at all.
 */
export async function resendVerification(
  _previous: ActionState,
  _form: FormData,
): Promise<ActionState> {
  const t = await getTranslations('verifyEmail')
  try {
    await apiPost('/api/v1/auth/resend-verification', undefined, {
      redirectOnUnauthorized: false,
    })
  } catch (error) {
    return toActionState(error, t('resendFailed'))
  }
  return { message: t('resendDone') }
}

/** `POST /auth/logout` — clears the session on the server and in the browser. */
export async function logout(): Promise<void> {
  try {
    const result = await apiPostRaw<unknown>('/api/v1/auth/logout', undefined, {
      redirectOnUnauthorized: false,
    })
    await forwardCookies(result.setCookie)
  } catch {
    // Already signed out, or the API is down: drop the cookie locally anyway.
  }
  const jar = await cookies()
  jar.delete('sid')
  redirect('/login')
}

/** `POST /auth/password/forgot` — always reports success, to not leak accounts. */
export async function requestPasswordReset(
  _previous: ActionState,
  form: FormData,
): Promise<ActionState> {
  const t = await getTranslations('password')
  const email = text(form, 'email')
  if (!email) return { fields: { email: t('emailRequired') } }
  try {
    await apiPost('/api/v1/auth/password/forgot', { email }, { redirectOnUnauthorized: false })
  } catch (error) {
    return toActionState(error, t('forgotFailed'))
  }
  return { message: t('forgotSent') }
}

/** `POST /auth/password/reset` with the token from the mailed link. */
export async function resetPassword(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('password')
  const token = text(form, 'token')
  const password = String(form.get('password') ?? '')
  const confirm = String(form.get('passwordConfirm') ?? '')

  const fields: Record<string, string> = {}
  if (!token) fields.token = t('tokenRequired')
  if (password.length < 8) fields.password = t('passwordTooShort')
  if (password !== confirm) fields.passwordConfirm = t('passwordMismatch')
  if (Object.keys(fields).length > 0) return { fields }

  try {
    await apiPost(
      '/api/v1/auth/password/reset',
      { token, password },
      { redirectOnUnauthorized: false },
    )
  } catch (error) {
    return toActionState(error, t('resetFailed'))
  }
  redirect('/login?reset=1')
}

/** `POST /auth/verify-email` with the token from the mailed link. */
export async function verifyEmail(_previous: ActionState, form: FormData): Promise<ActionState> {
  const t = await getTranslations('verifyEmail')
  const token = text(form, 'token')
  if (!token) return { fields: { token: t('tokenRequired') } }
  try {
    await apiPost('/api/v1/auth/verify-email', { token }, { redirectOnUnauthorized: false })
  } catch (error) {
    return toActionState(error, t('failed'))
  }
  return { message: t('done') }
}
