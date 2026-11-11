/**
 * Typed fetch wrapper over the platform API.
 *
 * Server-only: it forwards the incoming request cookies so the API sees the
 * caller's session (`sid`), and it never stores a token in client JavaScript
 * (frontend.md §1 "인증 처리"). Response bodies are typed from the generated
 * OpenAPI schema, so no API shape is written by hand.
 */
import 'server-only'

import { cookies, headers } from 'next/headers'
import { redirect } from 'next/navigation'

import { apiBaseUrl, apiTimeoutMs } from './config'
import { ApiError, ApiUnreachableError } from './errors'
import type { GetPath, GetResponse, Problem } from './types'

/** Header set by `src/middleware.ts` so a 401 can redirect back to the current page. */
export const CURRENT_PATH_HEADER = 'x-current-path'
/** Cookie holding the double-submit CSRF token (frontend.md §1). */
export const CSRF_COOKIE = 'csrf'
/** Header carrying the double-submit CSRF token on mutations. */
export const CSRF_HEADER = 'X-CSRF-Token'

export type CachePolicy = 'content' | 'progress'

export interface RequestOptions {
  /**
   * `content` revalidates on an interval — curriculum content only changes on a
   * redeploy. `progress` is per-user and never cached.
   */
  cache?: CachePolicy
  /** Query parameters; `undefined` and `null` values are dropped. */
  query?: Record<string, string | number | boolean | undefined | null>
  /** Redirect to `/login` on 401 instead of throwing. Defaults to true. */
  redirectOnUnauthorized?: boolean
  /** Extra cache tags for `revalidateTag`. */
  tags?: string[]
}

/** Seconds between content revalidations. */
const CONTENT_REVALIDATE_SECONDS = 300

function buildUrl(path: string, query: RequestOptions['query']): string {
  const url = new URL(`${apiBaseUrl()}${path}`)
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined && value !== null) url.searchParams.set(key, String(value))
  }
  return url.toString()
}

async function forwardedHeaders(method: string): Promise<Headers> {
  const out = new Headers({ Accept: 'application/json' })
  const jar = await cookies()
  const all = jar.getAll()
  if (all.length > 0) {
    out.set('Cookie', all.map((c) => `${c.name}=${c.value}`).join('; '))
  }
  if (method !== 'GET' && method !== 'HEAD') {
    const csrf = jar.get(CSRF_COOKIE)?.value
    if (csrf) out.set(CSRF_HEADER, csrf)
    out.set('Content-Type', 'application/json')
  }
  return out
}

async function currentPath(): Promise<string> {
  try {
    const store = await headers()
    return store.get(CURRENT_PATH_HEADER) ?? '/'
  } catch {
    return '/'
  }
}

async function parseProblem(response: Response): Promise<Problem | undefined> {
  const type = response.headers.get('content-type') ?? ''
  if (!type.includes('json')) return undefined
  try {
    return (await response.json()) as Problem
  } catch {
    return undefined
  }
}

interface RawRequest extends RequestOptions {
  method: string
  path: string
  body?: unknown
}

async function request<T>({
  method,
  path,
  body,
  cache = 'progress',
  query,
  redirectOnUnauthorized = true,
  tags,
}: RawRequest): Promise<T> {
  const url = buildUrl(path, query)
  const init: RequestInit & { next?: { revalidate?: number; tags?: string[] } } = {
    method,
    headers: await forwardedHeaders(method),
    signal: AbortSignal.timeout(apiTimeoutMs()),
  }
  if (body !== undefined) init.body = JSON.stringify(body)
  if (method === 'GET' && cache === 'content') {
    init.next = { revalidate: CONTENT_REVALIDATE_SECONDS, ...(tags ? { tags } : {}) }
  } else {
    init.cache = 'no-store'
  }

  let response: Response
  try {
    response = await fetch(url, init)
  } catch (cause) {
    throw new ApiUnreachableError(url, cause)
  }

  const requestId = response.headers.get('x-request-id') ?? undefined

  if (response.status === 401 && redirectOnUnauthorized) {
    redirect(`/login?next=${encodeURIComponent(await currentPath())}`)
  }

  if (!response.ok) {
    const problem = await parseProblem(response)
    throw new ApiError(
      response.status,
      `${method} ${path} → ${response.status}`,
      problem,
      requestId,
    )
  }

  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

/** GET a contract path; the result type comes from the OpenAPI schema. */
export function apiGet<P extends GetPath>(
  path: P,
  options: RequestOptions = {},
): Promise<GetResponse<P>> {
  return request<GetResponse<P>>({ method: 'GET', path, ...options })
}

/**
 * GET a contract path and return `null` instead of throwing when the API answers
 * 404 or the endpoint is not implemented yet. Lets a page render a skeleton for
 * fields the backend has not shipped (frontend.md §2 "필드 가용 시점").
 */
export async function apiGetOrNull<P extends GetPath>(
  path: P,
  options: RequestOptions = {},
): Promise<GetResponse<P> | null> {
  const { isUnimplemented } = await import('./errors')
  try {
    return await apiGet(path, options)
  } catch (error) {
    if (isUnimplemented(error) || error instanceof ApiUnreachableError) return null
    throw error
  }
}

/** POST to a contract path. Sends the double-submit CSRF header automatically. */
export function apiPost<T>(path: string, body?: unknown, options: RequestOptions = {}): Promise<T> {
  return request<T>({ method: 'POST', path, body, ...options })
}

/** PATCH a contract path. */
export function apiPatch<T>(
  path: string,
  body?: unknown,
  options: RequestOptions = {},
): Promise<T> {
  return request<T>({ method: 'PATCH', path, body, ...options })
}

/** DELETE a contract path. */
export function apiDelete<T>(path: string, options: RequestOptions = {}): Promise<T> {
  return request<T>({ method: 'DELETE', path, ...options })
}
