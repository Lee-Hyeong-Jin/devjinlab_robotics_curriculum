/**
 * Who is signed in, server-side.
 *
 * The browser holds an HttpOnly `sid` cookie; the frontend never reads a token
 * (frontend.md §1). Authorisation is the API's job — these helpers only decide
 * what to render, never what is allowed (AC-WEB.4).
 */
import 'server-only'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'

import { apiGet, apiGetOrNull } from './api/client'
import { isUnauthorized } from './api/errors'
import { loginUrl, sessionExpiredUrl } from './next-path'
import type { Role, User } from './api/types'

/** The session cookie the API sets on login (ADR 0009). */
export const SESSION_COOKIE = 'sid'

/** The signed-in user, or null when there is no usable session. */
export async function getMe(): Promise<User | null> {
  const jar = await cookies()
  if (!jar.get(SESSION_COOKIE)) return null
  try {
    return await apiGetOrNull('/api/v1/me', { redirectOnUnauthorized: false })
  } catch (error) {
    // A cookie the API no longer honours: the session was ended from another device or by an
    // operator, the account was disabled, or the cookie is simply stale. That is "nobody is
    // signed in", not a failure — every page, the login screen included, asks this question
    // from the layout, so throwing here took the whole site down for that browser (QA B-01).
    if (isUnauthorized(error)) return null
    throw error
  }
}

/** True when the browser still holds a session cookie the API has stopped honouring. */
export async function hasStaleSession(): Promise<boolean> {
  const jar = await cookies()
  return jar.has(SESSION_COOKIE) && (await getMe()) === null
}

/**
 * The signed-in user, or a redirect to the login screen and back.
 *
 * A stale cookie is dropped on the way (`/session/expired`), so the reader is told the session
 * ended instead of meeting the same refusal on every page.
 */
export async function requireUser(nextPath: string): Promise<User> {
  const user = await getMe()
  if (!user) {
    const jar = await cookies()
    redirect(jar.has(SESSION_COOKIE) ? sessionExpiredUrl(nextPath) : loginUrl(nextPath))
  }
  return user
}

/** Role ranking: an admin may do anything an author may, and so on. */
const RANK: Record<Role, number> = { learner: 0, author: 1, admin: 2 }

/** True when the user's role is at least `needed`. */
export function hasRole(user: Pick<User, 'role'> | null, needed: Role): boolean {
  return !!user && RANK[user.role] >= RANK[needed]
}

/**
 * Send an anonymous reader to the login screen when this server has accounts.
 *
 * For the screens that are a reader's own (review, reports, a quiz run): without a session
 * there is nothing to load, and "could not be loaded" told nobody that signing in is the way
 * forward (QA B-25). In local mode there are no accounts and the API serves a fixed reader
 * without a cookie, so nothing happens there.
 */
export async function signInIfRequired(nextPath: string): Promise<void> {
  const jar = await cookies()
  if (jar.has(SESSION_COOKIE)) return // an ended session is dealt with by the API client
  try {
    await apiGet('/api/v1/me', { redirectOnUnauthorized: false })
  } catch (error) {
    if (isUnauthorized(error)) redirect(loginUrl(nextPath))
    // Anything else (local mode's 404, the API being down) is not a reason to ask for a login.
  }
}
