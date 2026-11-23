'use client'

import { useEffect, useState } from 'react'

const EVENT = 'rc:flash'
const VISIBLE_MS = 6000

/** Announce that an action succeeded, from anywhere on the page. */
export function flash(message: string): void {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent<string>(EVENT, { detail: message }))
}

/**
 * One place, outside the page content, that says an action worked.
 *
 * A button's own confirmation lives next to the button, and the button is often gone the moment
 * the action succeeds: ending the timer replaces "stop" with "start", signing a device out
 * removes its row. The reader was left with no sign that anything had happened (QA B-24). This
 * region survives those re-renders; it is a live region, so a screen reader announces it too.
 */
export function Flash() {
  const [message, setMessage] = useState('')

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined
    const show = (event: Event) => {
      setMessage((event as CustomEvent<string>).detail ?? '')
      clearTimeout(timer)
      timer = setTimeout(() => setMessage(''), VISIBLE_MS)
    }
    window.addEventListener(EVENT, show)
    return () => {
      window.removeEventListener(EVENT, show)
      clearTimeout(timer)
    }
  }, [])

  return (
    <div
      role="status"
      aria-live="polite"
      data-flash=""
      className="pointer-events-none fixed inset-x-0 bottom-4 z-50 flex justify-center px-4"
    >
      {message ? (
        <p className="border-border-accent bg-success-light text-success pointer-events-auto max-w-md rounded-lg border px-4 py-2 text-sm shadow-lg">
          <span aria-hidden="true">✓ </span>
          {message}
        </p>
      ) : null}
    </div>
  )
}
