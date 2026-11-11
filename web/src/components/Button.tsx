import Link from 'next/link'
import type { ButtonHTMLAttributes, ReactNode } from 'react'

import { cx } from '@/lib/cx'

/** Figma `10-20` primary · `10-22` secondary · `10-24` mono (CLI command). */
export type ButtonKind = 'primary' | 'secondary' | 'mono'

const KIND_CLASS: Record<ButtonKind, string> = {
  primary: 'bg-accent-solid text-on-accent border-transparent hover:opacity-90',
  secondary: 'bg-surface text-primary border-border-default hover:bg-subtle',
  mono: 'bg-subtle text-primary border-border-default font-mono text-sm hover:bg-surface',
}

const BASE =
  'inline-flex items-center justify-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-opacity disabled:cursor-not-allowed disabled:opacity-50'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  kind?: ButtonKind
  children: ReactNode
}

export function Button({ kind = 'primary', className, children, ...rest }: ButtonProps) {
  return (
    <button type="button" className={cx(BASE, KIND_CLASS[kind], className)} {...rest}>
      {children}
    </button>
  )
}

export interface ButtonLinkProps {
  href: string
  kind?: ButtonKind
  children: ReactNode
  className?: string
  /** External links open in a new tab with the usual rel guard. */
  external?: boolean
  'aria-label'?: string
}

export function ButtonLink({
  href,
  kind = 'primary',
  children,
  className,
  external = false,
  ...rest
}: ButtonLinkProps) {
  const classes = cx(BASE, KIND_CLASS[kind], className)
  if (external) {
    return (
      <a href={href} target="_blank" rel="noopener noreferrer" className={classes} {...rest}>
        {children}
      </a>
    )
  }
  return (
    <Link href={href} className={classes} {...rest}>
      {children}
    </Link>
  )
}
