'use client'

import { useTranslations } from 'next-intl'
import { useEffect } from 'react'

import { Button } from '@/components/Button'
import { EmptyState } from '@/components/EmptyState'

/**
 * Route-level error boundary. The API base URL and request ids stay out of the
 * message; the detail goes to the server log.
 */
export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  const t = useTranslations('error')

  useEffect(() => {
    console.error(error)
  }, [error])

  const unreachable = error.message.includes('API unreachable')

  return (
    <EmptyState
      title={t('title')}
      body={unreachable ? t('apiUnreachable') : t('generic')}
      action={<Button onClick={reset}>{t('retry')}</Button>}
    />
  )
}
