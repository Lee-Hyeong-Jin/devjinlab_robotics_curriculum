'use client'

import { usePathname, useSearchParams } from 'next/navigation'
import { useEffect, useRef } from 'react'

/**
 * Reports navigations inside the app as page views (ADR 0017).
 *
 * The first page of a visit is counted on the server, where it also works without script.
 * After that the router moves between pages largely from its cache, so the server sees
 * nothing; this component tells it. It sends the path and nothing else: no identifier is
 * created or stored in the browser.
 */
export function PageViewBeacon() {
  const pathname = usePathname()
  const search = useSearchParams().toString()
  const first = useRef(true)

  useEffect(() => {
    if (first.current) {
      // The server already counted the page this visit started on.
      first.current = false
      return
    }
    const path = search ? `${pathname}?${search}` : pathname
    void fetch('/api/pv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path }),
      keepalive: true,
    }).catch(() => undefined)
    // The language switch and filters change the query, not the page: only a new path counts.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname])

  return null
}
