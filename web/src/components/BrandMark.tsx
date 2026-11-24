import { cx } from '@/lib/cx'

/**
 * The site's mark: a robot arm on the accent colour.
 *
 * The same drawing as `app/icon.svg`, which is what a browser tab, a phone's home screen and a
 * search result show. Using it in the header ties those to the site: somebody who arrives from
 * a search result sees the icon they clicked. Decorative here — the link's text names the site.
 */
export function BrandMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 64 64"
      aria-hidden="true"
      focusable="false"
      className={cx('size-7 shrink-0', className)}
    >
      <rect width="64" height="64" rx="14" className="fill-accent-solid" />
      <g
        fill="none"
        className="stroke-on-accent"
        strokeWidth="5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M16 48h18" />
        <path d="M25 48V34l14-12 9 8" />
      </g>
      <g className="fill-on-accent">
        <circle cx="25" cy="34" r="5" />
        <circle cx="39" cy="22" r="5" />
        <circle cx="48" cy="30" r="3.5" />
      </g>
    </svg>
  )
}
