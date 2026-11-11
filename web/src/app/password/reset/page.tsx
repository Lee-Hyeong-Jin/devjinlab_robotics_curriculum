import type { Metadata } from 'next'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { ActionForm } from '@/components/form/ActionForm'
import { PageHeader } from '@/components/PageHeader'
import { resetPassword } from '@/lib/actions/auth'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('password')
  return { title: t('resetTitle') }
}

interface Props {
  searchParams: Promise<{ token?: string }>
}

/** `POST /auth/password/reset`. The token comes from the mailed link's query. */
export default async function ResetPasswordPage({ searchParams }: Props) {
  const [t, params] = await Promise.all([getTranslations('password'), searchParams])
  return (
    <div className="mx-auto max-w-md">
      <PageHeader title={t('resetTitle')} subtitle={t('resetSubtitle')} />
      <Card>
        <ActionForm
          action={resetPassword}
          submitLabel={t('resetSubmit')}
          pendingLabel={t('resetSubmitting')}
          fields={[
            {
              name: 'token',
              label: t('token'),
              defaultValue: params.token ?? '',
              required: true,
              hint: t('tokenHint'),
            },
            {
              name: 'password',
              label: t('newPassword'),
              kind: 'password',
              autoComplete: 'new-password',
              required: true,
              minLength: 8,
            },
            {
              name: 'passwordConfirm',
              label: t('passwordConfirm'),
              kind: 'password',
              autoComplete: 'new-password',
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
