import { useTranslations } from 'next-intl'

import type { AuthProvider } from '@/lib/api/types'
import { providerStartHref } from '@/lib/auth-providers'
import { cx } from '@/lib/cx'

export interface ProviderButtonsProps {
  /** `GET /auth/providers`; an empty list renders nothing at all. */
  providers: readonly AuthProvider[]
  /** App path the provider should send the reader back to. */
  returnTo?: string
  /**
   * `login` offers to sign in with the provider, `connect` to link it to the
   * account that is already signed in.
   */
  variant?: 'login' | 'connect'
  /** Show the "or continue with" separator above the buttons. */
  withHeading?: boolean
  className?: string
}

/**
 * One button per configured external login (ADR 0010).
 *
 * Plain `<a>` elements on purpose: the flow is a full-page navigation to the API,
 * which redirects on to the provider. Nothing renders when no provider is
 * configured, so a password-only deployment shows no empty section.
 */
export function ProviderButtons({
  providers,
  returnTo = '/',
  variant = 'login',
  withHeading = false,
  className,
}: ProviderButtonsProps) {
  const t = useTranslations('auth')
  if (providers.length === 0) return null

  return (
    <div className={cx('flex flex-col gap-2', className)}>
      {withHeading ? (
        <p className="text-muted flex items-center gap-3 text-xs">
          <span className="bg-border-default h-px flex-1" aria-hidden="true" />
          {t('providersHeading')}
          <span className="bg-border-default h-px flex-1" aria-hidden="true" />
        </p>
      ) : null}
      <ul className="flex flex-col gap-2">
        {providers.map((provider) => (
          <li key={provider.id}>
            <a
              href={providerStartHref(provider.start_url, returnTo)}
              className="bg-surface text-primary border-border-default hover:bg-subtle inline-flex w-full items-center justify-center rounded-lg border px-4 py-2 text-sm font-medium"
            >
              {variant === 'login'
                ? t('continueWith', { name: provider.name })
                : t('connectWith', { name: provider.name })}
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}
