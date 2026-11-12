import type { Metadata } from 'next'
import Link from 'next/link'
import { redirect } from 'next/navigation'
import { getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { ActionForm } from '@/components/form/ActionForm'
import { PageHeader } from '@/components/PageHeader'
import { ProviderButtons } from '@/components/ProviderButtons'
import { signup } from '@/lib/actions/auth'
import { getAuthProviders } from '@/lib/api/queries'
import { getMe } from '@/lib/auth'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('signup')
  return { title: t('title') }
}

/** Signup — `POST /auth/signup` (Figma `23-55`). */
export default async function SignupPage() {
  const t = await getTranslations('signup')
  if (await getMe()) redirect('/')

  const providers = await getAuthProviders()

  return (
    <div className="mx-auto max-w-md">
      <PageHeader title={t('title')} subtitle={t('subtitle')} />
      <Card>
        <ActionForm
          action={signup}
          submitLabel={t('submit')}
          pendingLabel={t('submitting')}
          fields={[
            {
              name: 'email',
              label: t('email'),
              kind: 'email',
              autoComplete: 'email',
              required: true,
            },
            {
              name: 'displayName',
              label: t('displayName'),
              autoComplete: 'name',
              hint: t('displayNameHint'),
            },
            {
              name: 'password',
              label: t('password'),
              kind: 'password',
              autoComplete: 'new-password',
              required: true,
              minLength: 8,
              hint: t('passwordHint'),
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
        <ProviderButtons providers={providers} withHeading className="mt-5" />
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
