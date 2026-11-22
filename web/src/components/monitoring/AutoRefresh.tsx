'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState, useTransition } from 'react'

const INTERVAL_MS = 30_000

/**
 * "Refresh" and an opt-in "every 30 seconds".
 *
 * Off by default: a page that reloads itself moves content under a reader and re-announces it
 * to a screen reader, so the operator turns it on when they want a wall display.
 */
export function AutoRefresh({
  refreshLabel,
  autoLabel,
}: {
  refreshLabel: string
  autoLabel: string
}) {
  const router = useRouter()
  const [auto, setAuto] = useState(false)
  const [pending, startTransition] = useTransition()

  useEffect(() => {
    if (!auto) return
    const timer = window.setInterval(() => {
      // Not while the tab is in the background: nobody is looking, and each refresh is audited.
      if (document.visibilityState === 'visible') startTransition(() => router.refresh())
    }, INTERVAL_MS)
    return () => window.clearInterval(timer)
  }, [auto, router])

  return (
    <div className="flex flex-wrap items-center gap-3">
      <button
        type="button"
        onClick={() => startTransition(() => router.refresh())}
        disabled={pending}
        aria-busy={pending || undefined}
        className="bg-surface text-primary border-border-default hover:bg-subtle inline-flex min-h-11 items-center rounded-lg border px-4 py-2 text-sm font-medium disabled:opacity-50"
      >
        {refreshLabel}
      </button>
      <label className="text-primary flex min-h-11 cursor-pointer items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={auto}
          onChange={(event) => setAuto(event.target.checked)}
          className="border-border-default size-5 shrink-0 rounded"
        />
        {autoLabel}
      </label>
    </div>
  )
}
