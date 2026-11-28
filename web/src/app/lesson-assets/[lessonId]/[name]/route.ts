import { cookies } from 'next/headers'

import { apiBaseUrl, apiTimeoutMs } from '@/lib/api/config'

const NAME = /^[a-z0-9][a-z0-9-]*\.(svg|png)$/
const LESSON = /^[a-z0-9][a-z0-9-]*$/
const TYPES: Record<string, string> = { svg: 'image/svg+xml', png: 'image/png' }

interface Params {
  params: Promise<{ lessonId: string; name: string }>
}

/**
 * A lesson's figure, fetched from the API and passed on (`lib/markdown/lesson-blocks.ts`).
 *
 * The figure file lives next to the lesson's source and only the API can read it; the
 * browser can only reach this app. The session cookie is forwarded so a deployment that does
 * not publish its curriculum keeps its figures private too. The answer is always an image
 * type from the short list above, with a policy that forbids an SVG opened on its own to run
 * or load anything.
 */
export async function GET(_request: Request, { params }: Params): Promise<Response> {
  const { lessonId, name } = await params
  const extension = NAME.exec(name)?.[1]
  if (!extension || !LESSON.test(lessonId)) return new Response(null, { status: 404 })

  const jar = await cookies()
  const cookie = jar
    .getAll()
    .map((entry) => `${entry.name}=${entry.value}`)
    .join('; ')
  let upstream: Response
  try {
    upstream = await fetch(`${apiBaseUrl()}/api/v1/lessons/${lessonId}/figures/${name}`, {
      headers: cookie ? { Cookie: cookie } : {},
      cache: 'no-store',
      signal: AbortSignal.timeout(apiTimeoutMs()),
    })
  } catch {
    return new Response(null, { status: 502 })
  }
  if (!upstream.ok) return new Response(null, { status: upstream.status === 401 ? 401 : 404 })

  return new Response(upstream.body, {
    status: 200,
    headers: {
      'content-type': TYPES[extension] ?? 'application/octet-stream',
      'content-security-policy': "default-src 'none'; style-src 'unsafe-inline'; sandbox",
      'x-content-type-options': 'nosniff',
      'cache-control': 'private, max-age=3600',
    },
  })
}
