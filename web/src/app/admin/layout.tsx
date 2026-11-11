import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import type { ReactNode } from 'react'

import { Forbidden } from '@/components/Forbidden'
import { getMe, hasRole } from '@/lib/auth'
import { requireUser } from '@/lib/auth'

/**
 * Admin shell.
 *
 * The nav and the 403 screen are a courtesy: every admin route calls an admin
 * API that checks the role itself, so hiding the UI is never the protection
 * (AC-WEB.4). A learner who guesses the URL sees this screen, and the API
 * refuses the request behind it either way.
 */
export default async function AdminLayout({ children }: { children: ReactNode }) {
  const t = await getTranslations('admin')
  await requireUser('/admin/users')
  const user = await getMe()

  if (!hasRole(user, 'admin')) return <Forbidden />

  return (
    <div className="grid gap-6 lg:grid-cols-[12rem_minmax(0,1fr)]">
      <nav aria-label={t('nav')} className="lg:sticky lg:top-20 lg:self-start">
        <ul className="flex flex-wrap gap-1 lg:flex-col">
          <li>
            <Link
              href="/admin/users"
              className="text-muted hover:bg-subtle hover:text-primary block rounded-lg px-3 py-2 text-sm"
            >
              {t('users')}
            </Link>
          </li>
          <li>
            <Link
              href="/admin/audit"
              className="text-muted hover:bg-subtle hover:text-primary block rounded-lg px-3 py-2 text-sm"
            >
              {t('audit')}
            </Link>
          </li>
        </ul>
      </nav>
      <div className="min-w-0">{children}</div>
    </div>
  )
}
