'use client'

import { useTranslations } from 'next-intl'
import { useEffect } from 'react'

import { Button } from '@/components/Button'
import { EmptyState } from '@/components/EmptyState'
import { API_UNREACHABLE_DIGEST } from '@/lib/api/errors'

type RenderError = Error & { digest?: string }

/**
 * Route-level error boundary. The API base URL and request ids stay out of the
 * message; the detail goes to the server log.
 *
 * In production the error that arrives here from a server render carries no message of its
 * own: React substitutes a generic one ("Minified React error #441", which only says that a
 * server component failed) and a `digest`. Printing that object to the console looked like a
 * second bug (#33) and told nobody anything. What is useful is the digest: it is the key to
 * the real error in the web server's log, so it is shown to the reader as a reference to quote
 * and logged in one line.
 */
export default function Error({ error, reset }: { error: RenderError; reset: () => void }) {
  const t = useTranslations('error')
  const digest = error.digest
  const unreachable = digest === API_UNREACHABLE_DIGEST || error.message.includes('API unreachable')

  useEffect(() => {
    if (process.env.NODE_ENV === 'production') {
      console.error(`Page render failed (reference ${digest ?? 'none'}); see the server log.`)
    } else {
      console.error(error)
    }
  }, [error, digest])

  return (
    <EmptyState
      title={t('title')}
      body={
        <>
          {unreachable ? t('apiUnreachable') : t('generic')}
          {digest && !unreachable ? (
            <span className="text-muted mt-2 block font-mono text-xs">
              {t('reference', { id: digest })}
            </span>
          ) : null}
        </>
      }
      action={<Button onClick={reset}>{t('retry')}</Button>}
    />
  )
}
