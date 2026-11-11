'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

import { cx } from '@/lib/cx'

/** Figma `10-28` default · `10-30` active. */
export interface NavTabProps {
  href: string
  children: string
  /** Also mark active for nested routes (e.g. `/modules/...` under Roadmap). */
  matchPrefixes?: string[]
}

export function NavTab({ href, children, matchPrefixes = [] }: NavTabProps) {
  const pathname = usePathname()
  const active =
    pathname === href ||
    matchPrefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`))
  return (
    <Link
      href={href}
      aria-current={active ? 'page' : undefined}
      className={cx(
        'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
        active ? 'bg-accent-light text-accent' : 'text-muted hover:bg-subtle hover:text-primary',
      )}
    >
      {children}
    </Link>
  )
}
