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

import { apiGetOrNull } from './api/client'
import type { Role, User } from './api/types'

/** The session cookie the API sets on login (ADR 0009). */
export const SESSION_COOKIE = 'sid'

/** The signed-in user, or null when there is no usable session. */
export async function getMe(): Promise<User | null> {
  const jar = await cookies()
  if (!jar.get(SESSION_COOKIE)) return null
  return apiGetOrNull('/api/v1/me', { redirectOnUnauthorized: false })
}

/** The signed-in user, or a redirect to `/login?next=…`. */
export async function requireUser(nextPath: string): Promise<User> {
  const user = await getMe()
  if (!user) redirect(`/login?next=${encodeURIComponent(nextPath)}`)
  return user
}

/** Role ranking: an admin may do anything an author may, and so on. */
const RANK: Record<Role, number> = { learner: 0, author: 1, admin: 2 }

/** True when the user's role is at least `needed`. */
export function hasRole(user: Pick<User, 'role'> | null, needed: Role): boolean {
  return !!user && RANK[user.role] >= RANK[needed]
}
