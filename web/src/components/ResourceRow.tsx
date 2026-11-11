import type { ResourceKind } from '@/lib/api/types'
import { hostnameOf } from '@/lib/format'

import { Chip, type ChipTone } from './Chip'

const KIND_TONE: Record<ResourceKind, ChipTone> = {
  book: 'accent',
  course: 'accent',
  video: 'warning',
  article: 'neutral',
  other: 'neutral',
}

/** Figma `10-70`. A resource in the lesson sidebar or the resources table. */
export interface ResourceRowProps {
  title: string
  url?: string
  kind?: ResourceKind
  kindLabel?: string
  /** The "범위 메모" — which part of the book or course applies. */
  note?: string
  externalLabel: string
}

export function ResourceRow({
  title,
  url,
  kind,
  kindLabel,
  note,
  externalLabel,
}: ResourceRowProps) {
  const host = hostnameOf(url)
  return (
    <li className="border-border-default flex flex-col gap-1 border-b py-3 last:border-b-0">
      <div className="flex flex-wrap items-center gap-2">
        {kind && kindLabel ? <Chip tone={KIND_TONE[kind]}>{kindLabel}</Chip> : null}
        {url ? (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-accent text-sm font-medium underline underline-offset-2"
          >
            {title}
            <span className="sr-only"> ({externalLabel})</span>
          </a>
        ) : (
          <span className="text-primary text-sm font-medium">{title}</span>
        )}
        {host ? <span className="text-muted text-xs">{host}</span> : null}
      </div>
      {note ? <p className="text-muted text-sm">{note}</p> : null}
    </li>
  )
}
