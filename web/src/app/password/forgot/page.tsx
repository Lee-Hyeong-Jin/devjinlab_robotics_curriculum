import type { Metadata } from 'next'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { ActionForm } from '@/components/form/ActionForm'
import { PageHeader } from '@/components/PageHeader'
import { requestPasswordReset } from '@/lib/actions/auth'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('password')
  return { title: t('forgotTitle') }
}

/** `POST /auth/password/forgot`. The reply never says whether the account exists. */
export default async function ForgotPasswordPage() {
  const t = await getTranslations('password')
  return (
    <div className="mx-auto max-w-md">
      <PageHeader title={t('forgotTitle')} subtitle={t('forgotSubtitle')} />
      <Card>
        <ActionForm
          action={requestPasswordReset}
          submitLabel={t('forgotSubmit')}
          pendingLabel={t('forgotSubmitting')}
          fields={[
            {
              name: 'email',
              label: t('email'),
              kind: 'email',
              autoComplete: 'email',
              required: true,
            },
          ]}
        />
        <p className="border-border-default mt-5 border-t pt-4 text-sm">
          <Link href="/login" className="text-accent underline underline-offset-2">
            {t('backToLogin')}
          </Link>
        </p>
      </Card>
    </div>
  )
}
