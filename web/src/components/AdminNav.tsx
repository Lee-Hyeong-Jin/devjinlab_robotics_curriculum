'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

import { cx } from '@/lib/cx'

export interface AdminNavItem {
  href: string
  label: string
  /** Match the path exactly; otherwise nested routes keep the item current. */
  exact?: boolean
}

/** Section navigation of the admin console, with the current section marked. */
export function AdminNav({ label, items }: { label: string; items: AdminNavItem[] }) {
  const pathname = usePathname()
  return (
    <nav aria-label={label} className="lg:sticky lg:top-20 lg:self-start">
      <ul className="flex gap-1 overflow-x-auto lg:flex-col">
        {items.map((item) => {
          const current = item.exact
            ? pathname === item.href
            : pathname === item.href || pathname.startsWith(`${item.href}/`)
          return (
            <li key={item.href} className="shrink-0">
              <Link
                href={item.href}
                aria-current={current ? 'page' : undefined}
                className={cx(
                  'flex min-h-11 items-center rounded-lg px-3 py-2 text-sm font-medium whitespace-nowrap',
                  current
                    ? 'bg-accent-light text-accent'
                    : 'text-muted hover:bg-subtle hover:text-primary',
                )}
              >
                {item.label}
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
