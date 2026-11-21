import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import { getMe } from '@/lib/auth'

import { AccountMenu } from './AccountMenu'
import { LocaleSwitcher } from './LocaleSwitcher'
import { NavMenu } from './NavMenu'
import { NavTab } from './NavTab'
import { ThemeToggle } from './ThemeToggle'

/** Top navigation (frontend.md §4 — no standalone Figma node; see screen frames). */
export async function TopNav() {
  const [t, user] = await Promise.all([getTranslations(), getMe()])
  return (
    <header className="bg-surface border-border-default sticky top-0 z-40 border-b">
      <nav
        aria-label={t('app.mainNavigation')}
        className="mx-auto flex h-[var(--nav-height)] max-w-[var(--content-max)] items-center gap-2 px-4 sm:px-6 md:gap-3 xl:gap-4"
      >
        <Link
          href="/"
          className="text-primary flex min-h-11 shrink-0 items-center gap-2 font-bold whitespace-nowrap"
        >
          <span aria-hidden="true" className="bg-accent-solid size-2.5 rounded-full" />
          <span className="hidden xl:inline">{t('app.title')}</span>
          <span className="xl:hidden">{t('app.shortTitle')}</span>
        </Link>
        <NavMenu
          labels={{ open: t('nav.openMenu'), close: t('nav.closeMenu') }}
          tabs={
            <>
              <NavTab href="/">{t('nav.dashboard')}</NavTab>
              <NavTab href="/roadmap" matchPrefixes={['/modules']}>
                {t('nav.roadmap')}
              </NavTab>
              <NavTab href="/resources">{t('nav.resources')}</NavTab>
              <NavTab href="/review">{t('nav.review')}</NavTab>
              <NavTab href="/reports">{t('nav.reports')}</NavTab>
              <NavTab href="/search">{t('nav.search')}</NavTab>
            </>
          }
          utilities={
            <>
              <AccountMenu user={user} />
              <LocaleSwitcher />
              <ThemeToggle
                groupLabel={t('nav.theme')}
                labels={{
                  system: t('nav.themeSystem'),
                  light: t('nav.themeLight'),
                  dark: t('nav.themeDark'),
                }}
              />
            </>
          }
        />
      </nav>
    </header>
  )
}
