/** Skip link: first focusable element on the page (WCAG 2.1 AA, frontend.md §6). */
export function SkipLink({ label }: { label: string }) {
  return (
    <a
      href="#main"
      className="bg-surface text-accent border-border-accent focus:ring-accent-solid sr-only rounded-lg border px-4 py-2 text-sm font-medium focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-50"
    >
      {label}
    </a>
  )
}
