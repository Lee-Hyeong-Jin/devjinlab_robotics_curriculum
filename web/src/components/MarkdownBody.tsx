import type { ReactNode } from 'react'

import { cx } from '@/lib/cx'

export interface MarkdownBodyProps {
  children: ReactNode
  className?: string
  /** Rendered when the Markdown was empty. */
  empty?: ReactNode
}

/**
 * Wrapper for a rendered Markdown tree (`renderMarkdown`). Typography, KaTeX and
 * code-highlight styling live in `globals.css` under `.markdown-body`.
 */
export function MarkdownBody({ children, className, empty }: MarkdownBodyProps) {
  if (children === null || children === undefined) return <>{empty ?? null}</>
  return <div className={cx('markdown-body text-primary', className)}>{children}</div>
}
