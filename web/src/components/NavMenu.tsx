'use client'

import { usePathname } from 'next/navigation'
import { useEffect, useId, useRef, useState, type ReactNode } from 'react'

import { cx } from '@/lib/cx'

export interface NavMenuProps {
  /** The page links. In the bar from `md` up, in the menu below that. */
  tabs: ReactNode
  /** Account, language and theme. In the bar from `xl` up, in the menu below that. */
  utilities: ReactNode
  labels: { open: string; close: string }
}

/**
 * Responsive part of the top navigation (frontend.md §4.2).
 *
 * One DOM tree serves every width, so nothing is rendered twice and no id is duplicated:
 *
 * - below `md` (phones) the links and the utilities sit in one panel under the bar,
 * - from `md` (tablets) the links move into the bar and the panel holds the utilities only,
 * - from `xl` everything is in the bar and the menu button is gone.
 *
 * The panel is a disclosure (`aria-expanded` + `aria-controls`), not a modal dialog: the page
 * stays reachable, Escape and a press outside close it, and so does navigating.
 */
export function NavMenu({ tabs, utilities, labels }: NavMenuProps) {
  const pathname = usePathname()
  // Remember the path the menu was opened on. Following a link changes the path, which closes
  // the menu without an effect that sets state.
  const [openedAt, setOpenedAt] = useState<string | null>(null)
  const open = openedAt === pathname
  const panelId = useId()
  const rootRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    if (!open) return
    function onKeyDown(event: KeyboardEvent) {
      if (event.key !== 'Escape') return
      setOpenedAt(null)
      buttonRef.current?.focus()
    }
    function onPointerDown(event: PointerEvent) {
      if (event.target instanceof Node && !rootRef.current?.contains(event.target)) {
        setOpenedAt(null)
      }
    }
    document.addEventListener('keydown', onKeyDown)
    document.addEventListener('pointerdown', onPointerDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.removeEventListener('pointerdown', onPointerDown)
    }
  }, [open])

  return (
    <div ref={rootRef} className="contents">
      {/* First in the DOM so the keyboard reaches the toggle before what it reveals; `order-last`
          puts it at the end of the bar. */}
      <button
        ref={buttonRef}
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        aria-label={open ? labels.close : labels.open}
        onClick={() => setOpenedAt(open ? null : pathname)}
        className="text-primary hover:bg-subtle order-last ml-auto inline-flex size-11 shrink-0 items-center justify-center rounded-lg xl:hidden"
      >
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          className="size-6"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
        >
          {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
        </svg>
      </button>
      <div
        id={panelId}
        className={cx(
          open ? 'flex' : 'hidden',
          'bg-surface border-border-default absolute inset-x-0 top-full max-h-[calc(100dvh-var(--nav-height))] flex-col gap-3 overflow-y-auto border-b p-4 shadow-lg',
          'md:contents',
        )}
      >
        <div className="flex flex-col gap-1 md:min-w-0 md:flex-row md:items-center">{tabs}</div>
        <div
          className={cx(
            open ? 'md:flex' : 'md:hidden',
            'border-border-default flex flex-col items-start gap-3 border-t pt-3',
            'md:bg-surface md:absolute md:top-full md:right-4 md:w-80 md:rounded-b-xl md:border md:border-t-0 md:p-4 md:shadow-lg',
            'xl:static xl:ml-auto xl:flex xl:w-auto xl:flex-row xl:items-center xl:gap-2 xl:rounded-none xl:border-0 xl:bg-transparent xl:p-0 xl:shadow-none',
          )}
        >
          {utilities}
        </div>
      </div>
    </div>
  )
}
