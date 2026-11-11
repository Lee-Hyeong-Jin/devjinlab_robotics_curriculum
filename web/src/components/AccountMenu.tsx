import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import { logout } from '@/lib/actions/auth'
import type { User } from '@/lib/api/types'
import { hasRole } from '@/lib/auth'

import { SubmitButton } from './form/SubmitButton'

/**
 * Account area of the top navigation. The admin link is only rendered for an
 * admin, but the admin routes are protected by the API, not by hiding the link
 * (AC-WEB.4).
 */
export async function AccountMenu({ user }: { user: User | null }) {
  const t = await getTranslations('account')

  if (!user) {
    return (
      <Link
        href="/login"
        className="text-muted hover:text-primary rounded-lg px-3 py-2 text-sm font-medium"
      >
        {t('signIn')}
      </Link>
    )
  }

  return (
    <div className="flex items-center gap-1" aria-label={t('menu')}>
      {hasRole(user, 'admin') ? (
        <Link
          href="/admin/users"
          className="text-muted hover:text-primary rounded-lg px-3 py-2 text-sm font-medium"
        >
          {t('admin')}
        </Link>
      ) : null}
      <Link
        href="/profile"
        aria-label={t('profile')}
        className="text-primary max-w-[12rem] truncate rounded-lg px-3 py-2 text-sm font-medium"
      >
        {user.display_name || user.email}
      </Link>
      <form action={logout}>
        <SubmitButton kind="secondary" pendingLabel={t('signingOut')}>
          {t('signOut')}
        </SubmitButton>
      </form>
    </div>
  )
}
