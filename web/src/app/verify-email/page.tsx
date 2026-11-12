import type { Metadata } from 'next'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { ActionForm } from '@/components/form/ActionForm'
import { PageHeader } from '@/components/PageHeader'
import { RowAction } from '@/components/form/RowAction'
import { resendVerification, verifyEmail } from '@/lib/actions/auth'
import { getMe } from '@/lib/auth'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('verifyEmail')
  return { title: t('title') }
}

interface Props {
  searchParams: Promise<{ token?: string }>
}

/** `POST /auth/verify-email`. The token comes from the mailed link's query. */
export default async function VerifyEmailPage({ searchParams }: Props) {
  const [t, params, me] = await Promise.all([getTranslations('verifyEmail'), searchParams, getMe()])
  // Resending needs a session, and a server with no SMTP can never deliver the link.
  const canResend = me?.email_verification === 'pending'
  return (
    <div className="mx-auto max-w-md">
      <PageHeader title={t('title')} subtitle={t('subtitle')} />
      <Card>
        <ActionForm
          action={verifyEmail}
          submitLabel={t('submit')}
          pendingLabel={t('submitting')}
          fields={[
            {
              name: 'token',
              label: t('token'),
              defaultValue: params.token ?? '',
              required: true,
            },
          ]}
        />
        {canResend ? (
          <div className="border-border-default mt-5 border-t pt-4">
            <p className="text-muted mb-2 text-sm">{t('resendHint')}</p>
            <RowAction
              action={resendVerification}
              hidden={{}}
              label={t('resend')}
              pendingLabel={t('resending')}
            />
          </div>
        ) : null}
        <p className="border-border-default mt-5 border-t pt-4 text-sm">
          <Link href="/login" className="text-accent underline underline-offset-2">
            {t('toLogin')}
          </Link>
        </p>
      </Card>
    </div>
  )
}
