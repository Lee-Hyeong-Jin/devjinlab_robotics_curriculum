import type { Metadata } from 'next'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { AuthForm } from '@/components/form/AuthForm'
import { Field } from '@/components/form/Field'
import { SubmitButton } from '@/components/form/SubmitButton'
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
        <AuthForm action={resetPassword}>
          {(state) => (
            <>
              <Field
                label={t('token')}
                name="token"
                defaultValue={params.token ?? ''}
                required
                hint={t('tokenHint')}
                error={state.fields?.token}
              />
              <Field
                label={t('newPassword')}
                name="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                error={state.fields?.password}
              />
              <Field
                label={t('passwordConfirm')}
                name="passwordConfirm"
                type="password"
                autoComplete="new-password"
                required
                error={state.fields?.passwordConfirm}
              />
              <SubmitButton pendingLabel={t('resetSubmitting')}>{t('resetSubmit')}</SubmitButton>
            </>
          )}
        </AuthForm>
        <p className="border-border-default mt-5 border-t pt-4 text-sm">
          <Link href="/login" className="text-accent underline underline-offset-2">
            {t('backToLogin')}
          </Link>
        </p>
      </Card>
    </div>
  )
}
