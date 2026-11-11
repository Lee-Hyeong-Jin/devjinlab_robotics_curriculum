import type { Metadata } from 'next'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { ActionForm } from '@/components/form/ActionForm'
import { PageHeader } from '@/components/PageHeader'
import { verifyEmail } from '@/lib/actions/auth'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('verifyEmail')
  return { title: t('title') }
}

interface Props {
  searchParams: Promise<{ token?: string }>
}

/** `POST /auth/verify-email`. The token comes from the mailed link's query. */
export default async function VerifyEmailPage({ searchParams }: Props) {
  const [t, params] = await Promise.all([getTranslations('verifyEmail'), searchParams])
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
        <p className="border-border-default mt-5 border-t pt-4 text-sm">
          <Link href="/login" className="text-accent underline underline-offset-2">
            {t('toLogin')}
          </Link>
        </p>
      </Card>
    </div>
  )
}
