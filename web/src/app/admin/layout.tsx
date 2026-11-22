import { getTranslations } from 'next-intl/server'
import type { ReactNode } from 'react'

import { AdminNav } from '@/components/AdminNav'
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
  const [t, tMonitoring] = await Promise.all([
    getTranslations('admin'),
    getTranslations('monitoring'),
  ])
  await requireUser('/admin')
  const user = await getMe()

  if (!hasRole(user, 'admin')) return <Forbidden />

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-[12rem_minmax(0,1fr)]">
      <AdminNav
        label={t('nav')}
        items={[
          { href: '/admin', label: t('overview'), exact: true },
          { href: '/admin/monitoring', label: tMonitoring('nav') },
          { href: '/admin/users', label: t('users') },
          { href: '/admin/audit', label: t('audit') },
        ]}
      />
      <div className="min-w-0">{children}</div>
    </div>
  )
}
