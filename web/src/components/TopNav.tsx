import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

import { LocaleSwitcher } from './LocaleSwitcher'
import { NavTab } from './NavTab'
import { ThemeToggle } from './ThemeToggle'

/** Top navigation (frontend.md §4 — no standalone Figma node; see screen frames). */
export async function TopNav() {
  const t = await getTranslations()
  return (
    <header className="bg-surface border-border-default sticky top-0 z-40 border-b">
      <nav
        aria-label={t('app.mainNavigation')}
        className="mx-auto flex h-16 max-w-[var(--content-max)] items-center gap-4 px-4 sm:px-6"
      >
        <Link href="/" className="text-primary flex items-center gap-2 font-bold">
          <span aria-hidden="true" className="bg-accent-solid size-2.5 rounded-full" />
          <span className="hidden sm:inline">{t('app.title')}</span>
          <span className="sm:hidden">{t('app.shortTitle')}</span>
        </Link>
        <div className="flex items-center gap-1">
          <NavTab href="/">{t('nav.dashboard')}</NavTab>
          <NavTab href="/roadmap" matchPrefixes={['/modules']}>
            {t('nav.roadmap')}
          </NavTab>
          <NavTab href="/resources">{t('nav.resources')}</NavTab>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <LocaleSwitcher />
          <ThemeToggle
            groupLabel={t('nav.theme')}
            labels={{
              system: t('nav.themeSystem'),
              light: t('nav.themeLight'),
              dark: t('nav.themeDark'),
            }}
          />
        </div>
      </nav>
    </header>
  )
}
