import type { Metadata } from 'next'
import Link from 'next/link'
import { redirect } from 'next/navigation'
import { getTranslations } from 'next-intl/server'

import { Card } from '@/components/Card'
import { AuthForm } from '@/components/form/AuthForm'
import { Field } from '@/components/form/Field'
import { SubmitButton } from '@/components/form/SubmitButton'
import { PageHeader } from '@/components/PageHeader'
import { login } from '@/lib/actions/auth'
import { getMe } from '@/lib/auth'
import { safeNext } from '@/lib/next-path'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('login')
  return { title: t('title') }
}

interface Props {
  searchParams: Promise<{ next?: string; registered?: string; reset?: string }>
}

/** Login — `POST /auth/login` (Figma `23-3`). Signed-in readers go straight on. */
export default async function LoginPage({ searchParams }: Props) {
  const [t, params] = await Promise.all([getTranslations('login'), searchParams])
  const next = safeNext(params.next)

  if (await getMe()) redirect(next)

  const notice = params.registered ? t('registered') : params.reset ? t('resetDone') : undefined

  return (
    <div className="mx-auto max-w-md">
      <PageHeader title={t('title')} subtitle={t('subtitle')} />
      <Card>
        <AuthForm action={login} notice={notice}>
          {(state) => (
            <>
              <input type="hidden" name="next" value={next} />
              <Field
                label={t('email')}
                name="email"
                type="email"
                autoComplete="email"
                required
                error={state.fields?.email}
              />
              <Field
                label={t('password')}
                name="password"
                type="password"
                autoComplete="current-password"
                required
                error={state.fields?.password}
              />
              <label className="text-primary flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  name="remember"
                  className="border-border-default size-4 rounded"
                />
                {t('remember')}
              </label>
              <SubmitButton pendingLabel={t('submitting')}>{t('submit')}</SubmitButton>
            </>
          )}
        </AuthForm>
        <div className="border-border-default mt-5 flex flex-col gap-2 border-t pt-4 text-sm">
          <Link href="/password/forgot" className="text-accent underline underline-offset-2">
            {t('forgot')}
          </Link>
          <p className="text-muted">
            {t('noAccount')}{' '}
            <Link href="/signup" className="text-accent underline underline-offset-2">
              {t('signupLink')}
            </Link>
          </p>
        </div>
      </Card>
    </div>
  )
}
