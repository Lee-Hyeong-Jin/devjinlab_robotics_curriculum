import type { Metadata } from 'next'
import Link from 'next/link'
import { redirect } from 'next/navigation'
import { getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { AuthForm } from '@/components/form/AuthForm'
import { Field } from '@/components/form/Field'
import { SubmitButton } from '@/components/form/SubmitButton'
import { PageHeader } from '@/components/PageHeader'
import { signup } from '@/lib/actions/auth'
import { getMe } from '@/lib/auth'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('signup')
  return { title: t('title') }
}

/** Signup — `POST /auth/signup` (Figma `23-55`). Signed-in only route out. */
export default async function SignupPage() {
  const t = await getTranslations('signup')
  if (await getMe()) redirect('/')

  return (
    <div className="mx-auto max-w-md">
      <PageHeader title={t('title')} subtitle={t('subtitle')} />
      <Card>
        <AuthForm action={signup}>
          {(state) => (
            <>
              <Field
                label={t('email')}
                name="email"
                type="email"
                autoComplete="email"
                required
                error={state.fields?.email}
              />
              <Field
                label={t('displayName')}
                name="displayName"
                autoComplete="name"
                hint={t('displayNameHint')}
                error={state.fields?.displayName}
              />
              <Field
                label={t('password')}
                name="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                hint={t('passwordHint')}
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
              <SubmitButton pendingLabel={t('submitting')}>{t('submit')}</SubmitButton>
            </>
          )}
        </AuthForm>
        <p className="border-border-default text-muted mt-5 border-t pt-4 text-sm">
          {t('haveAccount')}{' '}
          <Link href="/login" className="text-accent underline underline-offset-2">
            {t('loginLink')}
          </Link>
        </p>
      </Card>
    </div>
  )
}
